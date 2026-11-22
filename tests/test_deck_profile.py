"""Synthetic physical lists only: regressions for composition, uncertainty and adapters."""
import json
from fractions import Fraction
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'kb' / 'vendor')]
from kb.deck_profile import profile, compare_profiles, exact_k, distribution, demand
from kb.profile_reports import install_profiles
from mtg_eval.access import DeckState


def card(typ='Creature', cost='{2}{G}', mv=3):
    return {'Type Line': typ, 'Mana Cost': cost, 'Mana Value': mv, 'Color Identity': 'WUBRG'}


def supported(*roles):
    return {r: {'status': 'supported', 'evidence': {'basis': 'synthetic_fixture', 'verification_state': 'candidate'}} for r in roles}


class Inventory:
    def __init__(self):
        self.cards = {'Leader': card(cost='{C}{G}'), 'Basic': card('Basic Land', '', 0),
                      'Dual': card('Land', '', 0), 'Tired Dual': card('Land', '', 0),
                      'Outlet Tutor': card('Artifact Creature'), 'Outlet': card('Artifact Creature'),
                      'Spell': card('Enchantment', '{2}{C}{G}{G/W}{G/P}{X}', 6),
                      'Flexible': card('Sorcery // Land', '{2}{G} // ', 3)}
        self.decks = {'Synthetic': [('Leader', 1, 'Commander'), ('Basic', 36, 'Land'),
                                   ('Outlet Tutor', 1, 'Nonland'), ('Spell', 62, 'Nonland'), ('Outlet', 1, 'Companion')]}
        self.records = {'Outlet Tutor': supported('sac_outlet', 'Sacrifice outlet', 'Tutor'),
                        'Outlet': supported('sac_outlet'), 'Leader': supported('draw')}
    def record(self, name): return self.records.get(name, {})


class ExactCounts(unittest.TestCase):
    def test_hand_checkable(self):
        self.assertEqual([exact_k(5, 2, 2, k) for k in range(3)], [Fraction(3, 10), Fraction(6, 10), Fraction(1, 10)])
        self.assertEqual(distribution(5, 2, 2)['0_to_1'], .9)
        self.assertEqual(distribution(5, 2, 2)['at_least_1'], .7)
        self.assertEqual(exact_k(5, 2, 2, 3), 0)
        self.assertEqual(exact_k(0, 0, 0, 0), 1)
        with self.assertRaises(ValueError): exact_k(5, 6, 2, 0)
    def test_all_land_ranges_and_windows(self):
        p = profile(Inventory(), ['Basic'] * 10)
        self.assertEqual(p['odds']['opening_seven']['land_cards']['at_least_3'], 1)
        self.assertEqual(p['odds']['opening_seven']['land_cards']['2_to_4'], 0)
        self.assertEqual(p['odds']['turn3_on_play_skip_first_draw']['cards_seen'], 9)
        self.assertEqual(p['odds']['turn3_on_draw_or_multiplayer']['cards_seen'], 10)
    def test_no_clamping_tiny_lists(self):
        self.assertIsNone(profile(Inventory(), ['Basic'])['odds']['opening_seven']['land_cards'])


class Composition(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.st = DeckState(self.inv, 'Synthetic')
    def get(self, st=None):
        st = st or self.st
        return profile(self.inv, st.library, st.commanders, st.companion,
                       {'sac_outlet': ['Sacrifice outlet'], 'tutor': ['Tutor']})
    def test_multiplicity_commanders_companion_and_overlapping_types(self):
        p = self.get()
        self.assertEqual((p['library_count'], p['commander_count'], p['companion_count']), (99, 1, 1))
        self.assertEqual(p['lands']['basic'], 36)
        self.assertEqual(p['types']['creature']['count'], 1)
        self.assertEqual(p['types']['artifact']['count'], 1)
        self.assertAlmostEqual(p['types']['land']['percent_library'], 3600 / 99)
        self.assertNotIn('draw', p['roles'])  # commander draw is never opening library access
        self.assertEqual(p['size_status'], 'size_complete')
        self.assertEqual(p['demand']['commanders']['true_colorless'], 1)
    def test_role_union_uses_positions_not_number_of_aliases(self):
        p = profile(self.inv, ['Outlet Tutor'] * 2 + ['Basic'] * 8,
                    role_groups={'sac_outlet': ['Sacrifice outlet']})
        self.assertEqual(p['roles']['sac_outlet']['supported_slots'], 2)
        self.assertAlmostEqual(p['odds']['opening_seven']['roles']['sac_outlet'], float(1 - exact_k(10, 2, 7, 0)))
    def test_role_preserved_but_tutor_lost(self):
        before = self.get()
        after = self.get(DeckState(self.inv, 'Synthetic', [('Outlet Tutor', 'Outlet')]))
        delta = {r['metric']: r['delta'] for r in compare_profiles(before, after)['deltas']}
        self.assertEqual(delta['roles.sac_outlet.supported_slots'], 0)
        self.assertEqual(delta['roles.tutor.supported_slots'], -1)
        self.assertGreater(after['roles']['tutor']['unknown_slots'], 0)
    def test_unchanged_and_one_cut(self):
        before = self.get()
        self.assertTrue(all(r['delta'] in (0, None) for r in compare_profiles(before, self.get())['deltas']))
        after = self.get(DeckState(self.inv, 'Synthetic', [('Basic', None)]))
        self.assertEqual(after['size_status'], 'incomplete')
        self.assertEqual(after['odds_scope'], 'incomplete_supplied_list_only')
        delta = {r['metric']: r['delta'] for r in compare_profiles(before, after)['deltas']}
        self.assertEqual(delta['library_count'], -1)
        self.assertEqual(delta['lands.basic'], -1)
        self.assertNotEqual(delta['odds.opening_seven.land_cards.0_to_1'], 0)
    def test_unknown_does_not_become_zero_or_full_deck_odds(self):
        p = profile(self.inv, ['Missing'] + ['Basic'] * 98, ['Leader'])
        self.assertEqual(p['coverage']['missing_cards'], 1)
        self.assertEqual(p['types']['land']['count'], 98)
        self.assertIsNone(p['odds']['opening_seven']['land_cards'])
        self.assertEqual(p['supply']['potential_colors']['C'], 0)
        self.assertEqual(p['supply']['unknown_cards'], 99)
    def test_unknown_distribution_to_known_does_not_imply_zero_before(self):
        a = profile(self.inv, ['Missing'] + ['Basic'] * 9)
        b = profile(self.inv, ['Basic'] * 10)
        rows = {r['metric']: r for r in compare_profiles(a, b)['deltas']}
        self.assertIsNone(rows['odds.opening_seven.land_cards']['delta'])
        self.assertIsNone(rows['odds.opening_seven.land_cards']['before'])

    def test_alternative_land_face_is_not_an_extra_card_or_guaranteed_land(self):
        p = profile(self.inv, ['Flexible'] + ['Basic'] * 9)
        self.assertEqual(p['library_count'], 10)
        self.assertEqual(p['types']['land']['count'], 9)
        self.assertEqual(p['coverage']['unknown_type_slots'], 1)
        self.assertIsNone(p['odds']['opening_seven']['land_cards'])
        self.assertFalse(p['optional_faces']['Flexible']['counted_as_extra_cards'])
        self.assertEqual(p['demand']['library_spells']['unknown_cards'], 1)
    def test_land_seen_is_not_mill_or_land_drop(self):
        p = self.get()
        self.assertNotIn('self_mill', p['roles'])
        self.assertIn('Seen is not castable, a land drop, or mill.', ' '.join(p['limitations']))
    def test_strict_demand_reuses_typed_parser(self):
        d = demand([self.inv.cards['Spell']])
        self.assertEqual((d['generic'], d['true_colorless'], d['colored']['G']), (2, 1, 1))
        self.assertEqual(d['conditional_symbols'], {'{G/W}': 1, '{G/P}': 1, '{X}': 1})
        self.assertEqual(demand([card(cost='{2/W}{S}{0}')])['snow'], 1)
        self.assertEqual(demand([card(cost='bad {G}')])['unknown_cards'], 1)
        self.assertEqual(demand([card(cost='{}')])['unknown_cards'], 1)
        json.dumps(self.get(), allow_nan=False)
    def test_inventory_production_fields_are_labelled_and_never_color_identity(self):
        self.inv.cards['Dual']['Produces'] = 'WG'
        self.inv.cards['Dual']['ETB Tapped'] = 'Conditional'
        p = profile(self.inv, ['Dual'] * 10)
        self.assertEqual(p['supply']['potential_colors'], dict(W=10, U=0, B=0, R=0, G=10, C=0))
        self.assertEqual(p['supply']['land_entry_hints']['conditional'], 10)
        self.assertEqual(p['card_evidence']['Dual']['mana']['basis'], 'inventory_field_fallback')

    def test_fallback_has_evidence_and_uncertain_tags_not_support(self):
        self.inv.records['Spell'] = {'draw': {'status': 'tag_only', 'evidence': {'tag': True}}}
        p = self.get()
        self.assertEqual(p['roles']['draw']['supported_slots'], 0)
        self.assertEqual(p['card_evidence']['Spell']['roles']['draw']['evidence']['basis'], 'text_pattern_fallback')


class Production(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        db = self.inv.db = sqlite3.connect(':memory:')
        db.execute('create table current_contracts (contract_id text, contract_version int, card_name text, contract_json text)')
        db.execute('create table validation_queue (contract_id text, contract_version int, queue_state text)')
        self.addCleanup(db.close)
    def add(self, name, mode='alternatives', state='ready_for_review', **fields):
        cid = name + str(self.inv.db.execute('select count(*) from current_contracts').fetchone()[0])
        contract = {'result': {'produces': [{'id': 'mana.add', 'mana': dict(mode=mode, alternatives=[['W'], ['G']], **fields)}]}}
        self.inv.db.execute('insert into current_contracts values (?,1,?,?)', (cid, name, json.dumps(contract)))
        self.inv.db.execute('insert into validation_queue values (?,1,?)', (cid, state))
    def test_land_swap_preserves_potential_colors_without_inventing_untapped_parity(self):
        self.inv.cards['Dual']['ETB Tapped'] = 'No'
        self.inv.cards['Tired Dual']['ETB Tapped'] = 'Yes'
        self.add('Dual')
        self.add('Tired Dual')  # only production is encoded; ETB tapped distinction is not available here
        a, b = [profile(self.inv, [n] * 10) for n in ('Dual', 'Tired Dual')]
        self.assertEqual(a['supply']['potential_colors'], b['supply']['potential_colors'])
        self.assertEqual(a['supply']['potential_colors']['W'], 10)
        self.assertIsNone(b['supply']['availability']['always'])
        self.assertIsNone(b['supply']['availability']['tapped'])
        delta = {r['metric']: r['delta'] for r in compare_profiles(a, b)['deltas']}
        self.assertEqual(delta['supply.land_entry_hints.untapped'], -10)
        self.assertEqual(delta['supply.land_entry_hints.tapped'], 10)
    def test_casting_commander_or_tapping_is_not_opening_supply(self):
        self.add('Leader')
        self.add('Outlet')
        p = profile(self.inv, ['Outlet'] * 10, ['Leader'])
        self.assertEqual(p['supply']['candidate_sources']['dork'], 10)
        self.assertEqual(p['supply']['potential_colors']['G'], 10)  # never includes commander
        self.assertIsNone(p['supply']['availability']['opening_usable_sources'])
    def test_reference_mana_unknown_not_color_identity_and_rejected_excluded(self):
        self.add('Dual', mode='commander_identity')
        self.add('Tired Dual', state='rejected')
        p = profile(self.inv, ['Dual', 'Tired Dual'])
        self.assertEqual(sum(p['supply']['potential_colors'].values()), 0)
        self.assertEqual(p['supply']['unknown_color_slots'], 2)
        self.assertEqual(p['card_evidence']['Dual']['mana']['verification_state'], 'candidate')
    def test_true_colorless_and_multiple_contracts_count_one_physical_source(self):
        self.add('Dual', mode='colorless', symbols=['C'])
        self.add('Dual', mode='colorless', symbols=['C'])
        p = profile(self.inv, ['Dual'] * 2)
        self.assertEqual(p['supply']['potential_colors']['C'], 2)
        self.assertEqual(p['supply']['candidate_sources']['land'], 2)


class ReportEvaluator:
    """The vendor DeckState, with tiny report bodies to isolate the adapter contract."""
    def __init__(self): self.inv = Inventory()
    def _state(self, deck, swaps=()): return DeckState(self.inv, deck, swaps)
    def _resolve_deck(self, name): return 'Synthetic' if name == 'alias' else name
    def _card(self, name): return 'Outlet' if name == 'outlet alias' else name
    def result(self): return {'data': {}, 'sections': [], 'limitations': [], 'uncertainty': []}
    def deck(self, name, games=None): return self.result()
    def compare(self, deck, swaps, games=None):
        for out, inn in swaps: pass
        return self.result()
    def upgrades(self, deck, top=5):
        r = self.result()
        r['data']['upgrades'] = [{'cut': 'Outlet Tutor (human_review_required)', 'add': 'Outlet'}]
        r['sections'] = [('Cut order used (lowest measured loss first)', [{'card': 'Outlet Tutor'}])]
        return r
    def build(self, commander, n_lands=36):
        self.inv.decks['__build__'] = [(commander, 1, 'Commander'), ('Basic', n_lands, 'Land')]
        try: self._state('__build__')
        finally: self.inv.decks.pop('__build__')
        return self.result()


class Reports(unittest.TestCase):
    def setUp(self): self.ev = install_profiles(ReportEvaluator())
    def test_deck_keyword_alias_and_idempotence(self):
        install_profiles(self.ev)
        r = self.ev.deck(name='alias')
        self.assertEqual(r['data']['composition_profile']['library_count'], 99)
        self.assertEqual(len(r['sections']), 1)
    def test_compare_generator_and_resolved_names(self):
        p = self.ev.compare(deck='alias', swaps=iter([('Outlet Tutor', 'outlet alias')]))['data']['composition_profile']
        self.assertEqual(p['after']['roles']['sac_outlet']['supported_slots'], 1)
        self.assertEqual(p['individual_changes'][0]['add'], 'Outlet')
    def test_upgrades_include_each_cut_and_swap(self):
        p = self.ev.upgrades('Synthetic')['data']['composition_profile']
        self.assertEqual(p['proposals'][0]['after']['size_status'], 'size_complete')
        self.assertEqual(p['cuts_only'][0]['after']['size_status'], 'incomplete')
    def test_build_captures_real_multiplicity_and_restores_state(self):
        original = self.ev._state
        p = self.ev.build('Leader', n_lands=42)['data']['composition_profile']
        self.assertEqual(p['library_count'], 42)
        self.assertNotIn('__build__', self.ev.inv.decks)
        self.assertEqual(self.ev._state, original)
    def test_mtgtools_compare_uses_profile_adapter(self):
        from mtgtools.verbs import compare
        with patch('mtg_eval.api.Evaluator', return_value=ReportEvaluator()):
            data, claims = compare('alias', ['Outlet Tutor=Outlet'], 'synthetic.xlsx')
        self.assertIn('composition_profile', data['evaluator']['data'])
        self.assertTrue(claims)


class ExistingEvaluatorIntegration(unittest.TestCase):
    def test_real_collection_adapter_and_all_four_vendor_reports(self):
        from mtg_eval.api import Evaluator
        from mtg_eval.report import to_json, markdown
        fixture = Inventory()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.sqlite'
            con = sqlite3.connect(path)
            con.executescript((ROOT / 'collection' / 'schema.sql').read_text())
            con.execute("insert into meta values ('schema_version','1')")
            for name, row in fixture.cards.items():
                con.execute('insert into cards (card_name,type_line,mana_cost,mana_value,color_identity,oracle_text,commander_legal,can_be_commander) values (?,?,?,?,?,?,?,?)',
                            (name, row['Type Line'], row['Mana Cost'], row['Mana Value'], 'WUBRG', '', 'Legal', 'Yes'))
                con.execute("insert into holdings (card_name,quantity,source) values (?,100,'synthetic')", (name,))
            for name, qty, section in fixture.decks['Synthetic']:
                con.execute("insert into deck_cards (deck,card_name,quantity,section) values ('Synthetic',?,?,?)", (name, qty, section))
            con.commit()
            con.close()
            ev = install_profiles(Evaluator(path, games=2, engine_games=0))
            reports = [ev.deck('Synthetic'), ev.compare('Synthetic', [('Outlet Tutor', 'Outlet')]),
                       ev.upgrades('Synthetic'), ev.build('Leader', n_lands=0)]
            for report in reports:
                self.assertIn('composition_profile', json.loads(to_json(report))['data'])
                self.assertIn('Physical composition', markdown(report))
            self.assertEqual(reports[0]['data']['composition_profile']['library_count'], 99)
            self.assertEqual(reports[1]['data']['composition_profile']['after']['size_status'], 'size_complete')


if __name__ == '__main__': unittest.main()
