"""Builder regressions for independently reported factory and role-coverage defects.

Synthetic inputs only. These tests are remediation, not independent review.
"""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'kb'), str(ROOT / 'kb' / 'vendor')]
from test_deck_profile import Inventory, ReportEvaluator
from kb.contract_roles import open_grounded_evaluator
from kb.deck_profile import profile, compare_profiles
from kb.profile_reports import install_profiles
from mtg_eval.report import markdown


def synthetic_kb(path):
    """Build the minimal synthetic KB input consumed by the real SQLite factory."""
    fixture = Inventory()
    con = sqlite3.connect(path)
    con.executescript('''
        create table meta (key text, value text);
        create table cards (card_name text, raw_json text);
        create table deck_allocations (deck text, card_name text, quantity integer, section text, physically_assigned integer, row_id integer);
        create table capability_claims (card_name text, capability text, claim_status text, evidence_text text, source text);
        create table projected_card_statics (card_name text, statics_json text, unread_json text);
        create table projected_abilities (card_name text, ability_index integer, raw_ability_json text);
        create table current_contracts (contract_id text, contract_version integer, card_name text, contract_json text);
        create table validation_queue (contract_id text, contract_version integer, queue_state text);
        create table derived_facts (fact_kind text, input_key text, value_json text);
    ''')
    con.executemany('insert into meta values (?,?)', [('input_sha256','synthetic-factory'), ('canonical_sheet_id','synthetic')])
    for name, data in fixture.cards.items():
        row = dict(data, **{'Card Name': name, 'Oracle Text': '', 'Roles': '', 'Known Qty (min)':100,
                           'Copies Free':99, 'Copies in Decks':1, 'Can Be Commander':'Yes', 'Commander Legal':'Legal'})
        con.execute('insert into cards values (?,?)', (name, json.dumps(row)))
        con.execute('insert into projected_card_statics values (?, ?, ?)', (name, '{}', '[]'))
    for i, (name, qty, section) in enumerate(fixture.decks['Synthetic']):
        con.execute('insert into deck_allocations values (?,?,?,?,1,?)', ('Synthetic', name, qty, section, i))
    con.execute('insert into current_contracts values (?,1,?,?)',
                ('synthetic.life', 'Outlet Tutor', json.dumps({'query_index': {'feeds': ['life.gain']}})))
    con.execute("insert into validation_queue values ('synthetic.life',1,'ready_for_review')")
    con.commit()
    con.close()


class GroundedFactoryRegression(unittest.TestCase):
    def test_documented_factory_real_reports_positional_and_keyword(self):
        from mtg_eval import semantics as M, structure as S, deckeval as D, access as A, abilities
        import bridge_v02
        bindings = [(M, name) for name in ('clean','clauses','clause_audit','recursion_types','wipe_kind','protection_profile')]
        bindings += [(S, name) for name in ('resource_claims','feedback','closing_profile','commander_dependence')]
        bindings += [(D, 'TUTOR'), (A, 'CardModel')]
        originals = {name: getattr(module, name) for module, name in bindings}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(abilities._CACHE, clear=True):
            path = Path(tmp) / 'synthetic.sqlite'
            synthetic_kb(path)
            ev = open_grounded_evaluator(path, games=2, engine_games=0)
            try:
                for method, args, kwargs in [
                    ('deck', ('Synthetic',), {}), ('deck', (), {'name':'Synthetic'}),
                    ('compare', ('Synthetic', [('Outlet Tutor','Outlet')]), {}),
                    ('compare', (), {'deck':'Synthetic', 'swaps':[('Outlet Tutor','Outlet')]}),
                    ('upgrades', ('Synthetic',), {}), ('upgrades', (), {'deck':'Synthetic'}),
                    ('build', ('Leader', 0), {}), ('build', (), {'commander':'Leader','n_lands':0}),
                ]:
                    with self.subTest(method=method, keyword=bool(kwargs)):
                        result = getattr(ev, method)(*args, **kwargs)
                        self.assertIn('composition_profile', result['data'])
                        self.assertEqual(result['data']['role_source']['verification_state'], 'candidate')
                        self.assertTrue(any(s.startswith('Roles:') for s in result['limitations']))
                        self.assertIn('Physical composition', markdown(result))
                p = ev.deck('Synthetic')['data']['composition_profile']
                self.assertEqual(p['roles']['lifegain_source']['supported_slots'], 1)
                self.assertEqual(p['card_evidence']['Outlet Tutor']['roles']['lifegain_source']['evidence']['basis'], 'dio_contract')
            finally:
                ev.inv.db.close()
                bridge_v02.uninstall(originals, {name: getattr(module, name) for module, name in bindings})


class StableRoleCoverageRegression(unittest.TestCase):
    def setUp(self):
        self.ev = install_profiles(ReportEvaluator())
        self.ev.inv.records = {'Outlet Tutor': {'lifegain_source': {'status':'supported', 'evidence':{'basis':'synthetic_fixture'}}}}

    def render(self, result):
        return markdown(dict(title='Synthetic coverage', summary=[], conclusive=(False,'synthetic'), **result))

    def assert_comparison(self, p, before_unknown, after_unknown, before_supported, after_supported):
        role = 'lifegain_source'
        self.assertEqual(p['before']['roles'][role]['unknown_slots'], before_unknown)
        self.assertEqual(p['after']['roles'][role]['unknown_slots'], after_unknown)
        deltas = {r['metric']:r for r in p['deltas']}
        self.assertEqual(deltas[f'roles.{role}.unknown_slots']['delta'], after_unknown-before_unknown)
        for side, supported in [('before',before_supported), ('after',after_supported)]:
            self.assertEqual(p[side]['roles'][role]['supported_slots'], supported)
            self.assertAlmostEqual(p[side]['odds']['opening_seven']['roles'][role], supported * 7 / p[side]['library_count'])

    def test_both_swap_directions_full_and_individual_structured_and_rendered(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                if reverse:
                    self.ev.inv.decks['Synthetic'][2] = ('Outlet',1,'Nonland')
                swaps = [('Outlet','Outlet Tutor')] if reverse else [('Outlet Tutor','Outlet')]
                result = self.ev.compare('Synthetic', swaps)
                p = result['data']['composition_profile']
                values = (99,98,0,1) if reverse else (98,99,1,0)
                for comparison in (p, p['individual_changes'][0]): self.assert_comparison(comparison, *values)
                text = self.render(result)
                row = '| lifegain_source: unknown_slots | 99 cards | 98 cards | -1 cards |' if reverse else '| lifegain_source: unknown_slots | 98 cards | 99 cards | +1 cards |'
                self.assertEqual(text.count(row), 2)
                self.assertIn('7.071 %', text)
                self.assertIn('0.000 %', text)

    def test_cut_is_incomplete_and_has_its_own_coverage_denominator(self):
        result = self.ev.compare('Synthetic', [('Outlet Tutor',None)])
        p = result['data']['composition_profile']
        for comparison in (p, p['individual_changes'][0]):
            self.assert_comparison(comparison,98,98,1,0)
            self.assertEqual(comparison['after']['size_status'],'incomplete')
            self.assertEqual(comparison['after']['odds_scope'],'incomplete_supplied_list_only')
        text = self.render(result)
        self.assertIn('proposed: incomplete (98 library cards)', text)
        self.assertIn('| lifegain_source: unknown_slots | 98 cards | 98 cards | +0 cards |',text)

    def test_direct_helper_alignment_does_not_mutate_or_invent_uncomputed_values(self):
        inv = self.ev.inv
        before = profile(inv, ['Outlet Tutor'] + ['Spell']*98)
        after = profile(inv, ['Outlet'] + ['Spell']*98)
        saved = copy.deepcopy((before,after))
        self.assert_comparison(compare_profiles(before,after),98,99,1,0)
        self.assertEqual((before,after),saved)
        # Without per-slot evidence there is no computed coverage to report.
        after.pop('card_evidence')
        p = compare_profiles(before,after)
        self.assertIsNone(p['after']['roles']['lifegain_source']['unknown_slots'])
        self.assertIsNone(p['after']['odds']['opening_seven']['roles']['lifegain_source'])
        deltas = {r['metric']:r['delta'] for r in p['deltas']}
        self.assertIsNone(deltas['roles.lifegain_source.unknown_slots'])
        # An explicitly uncomputed existing value must not be overwritten either.
        p['after']['roles']['lifegain_source']['supported_slots'] = None
        q = compare_profiles(p['before'],p['after'])
        self.assertIsNone(q['after']['roles']['lifegain_source']['supported_slots'])


if __name__ == '__main__': unittest.main()
