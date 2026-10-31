"""Tests for the mtg tool surface. Grading rules run everywhere; verb tests need the KB database (data/README.md)
and are skipped when it is absent, as in CI until the release databases are published (C-006)."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mtgtools.claims import claim, grade  # noqa: E402

DB = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'


class Grading(unittest.TestCase):
    def test_grade_is_per_kind(self):
        self.assertEqual(grade('mechanics', 'semantic_reviewed'), 'decision_grade')
        for s in ('ready_for_review', 'blocked', 'quarantined', 'candidate'):
            self.assertEqual(grade('mechanics', s), 'exploratory')
        self.assertEqual(grade('rules_text', 'oracle'), 'decision_grade')
        self.assertEqual(grade('rules_text', 'sheet_text'), 'exploratory')
        self.assertEqual(grade('inventory', 'collection_snapshot'), 'decision_grade')

    def test_performance_and_preference_are_never_decision_grade(self):
        for s in ('evaluator_model', 'semantic_reviewed', 'oracle', 'collection_snapshot'):
            self.assertEqual(grade('performance', s), 'exploratory')
            self.assertEqual(grade('preference', s), 'not_system_gradable')

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            claim('x', 'vibes', 'oracle')


class Qualifiers(unittest.TestCase):
    """Qualifier matching on hand-built contracts, so it runs in CI without the KB database."""
    VOCAB = {'legendary', 'creature', 'enchantment', 'saga', 'artifact', 'artificer', 'human', 'wizard', 'land', 'aura'}

    def k(self, card, faces, feeds=(), hooks=(), subject='others', filt=None, self_phrase=False, targets=()):
        return {'contract_id': card + '.op', 'card': card, 'faces': list(faces), 'feeds': list(feeds), 'hooks': list(hooks),
                'hook_subject': subject, 'targets': list(targets), 'state': 'blocked',
                'triggers': {h: {'filter': filt, 'self': self_phrase, 'parsed': True} for h in hooks}}

    def setUp(self):
        from mtgtools import verbs
        self.v = verbs
        self.terra_return = self.k('Terra', ['legendary creature — human wizard', 'legendary enchantment creature — saga wizard'],
                                   feeds=['card.return_to_battlefield'])
        self.terra_copy = self.k('Terra', self.terra_return['faces'], feeds=['token.create'],
                                 targets=['target nonlegendary enchantment you control'])

    def q(self, p, eff, o, hook='battlefield.enter'):
        return self.v._qualify(p, eff, o, hook, self.VOCAB)

    def test_object_type_filter(self):
        era = self.k('Era', ['enchantment'], hooks=['battlefield.enter'], filt='artifact or artificer')
        module = self.k('Module', ['artifact'], hooks=['battlefield.enter'], filt='creature')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', era)[0], 'incompatible')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', module)[0], 'compatible')

    def test_counter_type_is_never_assumed(self):
        chapter = self.k('Terra', [], hooks=['counter.put'], subject=None)
        energy = self.k('Nissa', ['legendary creature'], feeds=['counter.put'])
        self.assertEqual(self.q(energy, 'counter.put', chapter, 'counter.put')[0], 'unresolved')

    def test_self_enter_needs_a_copy_or_return_of_that_card(self):
        light = self.k('Light', ['enchantment'], hooks=['battlefield.enter'], subject='self')
        talent = self.k('Talent', ['enchantment — class'], hooks=['battlefield.enter'], self_phrase=True)
        golem = self.k('Golem', ['artifact creature'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(self.terra_copy, 'token.create', light)[1], 'reentry_of_target')
        self.assertEqual(self.q(self.terra_copy, 'token.create', talent)[1], 'reentry_of_target')
        self.assertEqual(self.q(self.terra_copy, 'token.create', golem)[0], 'incompatible')   # not an enchantment
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', light)[0], 'incompatible')

    def test_a_target_disjunction_is_not_read_as_a_conjunction(self):
        copier = self.k('Copier', ['enchantment'], feeds=['token.create'], targets=['target artifact or enchantment you control'])
        artifact = self.k('Relic', ['artifact'], hooks=['battlefield.enter'], subject='self')
        land = self.k('Field', ['land'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(copier, 'token.create', artifact)[0], 'unresolved')     # was rejected as "artifact enchantment"
        self.assertEqual(self.q(copier, 'token.create', land)[0], 'unresolved')         # a miss on a disjunction is not a rejection

    def test_a_card_can_feed_its_own_watcher_of_other_objects(self):
        maker = self.k('Maker', ['creature'], feeds=['token.create'])
        watcher = dict(self.k('Maker', ['creature'], hooks=['battlefield.enter'], filt='creature'), contract_id='Maker.op2')
        links = self.v._links([maker, watcher])
        self.assertTrue(any(l['same_card'] and l['observer_contract'] == 'Maker.op2' for l in links))

    def test_same_card_reentry_on_a_two_faced_card_stays_unresolved(self):
        etb = self.k('Terra', self.terra_return['faces'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', etb)[:2], ('unresolved', 'same_card'))


class Ontology(unittest.TestCase):
    """The DIO lookup and the grounding label run everywhere: an agent without the KB can still consult the ontology."""
    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(list(args))
        return code, json.loads(buf.getvalue())

    def test_dio_needs_no_database(self):
        code, out = self.run_cli('--db', str(ROOT / 'no_such.sqlite'), 'dio', 'persistence')
        self.assertEqual(code, 0)
        self.assertEqual(out['grounding']['level'], 'doctrine')
        self.assertEqual(out['claims'], [])
        heads = [s['heading'] for s in out['data']['sections']]
        self.assertTrue(any('6.4 The persistence table' in h for h in heads), heads)

    def test_dio_section_number_finds_that_section_first(self):
        _, out = self.run_cli('dio', '7', '--limit', '1')
        self.assertIn('7. CONNECTIONS', out['data']['sections'][0]['heading'])

    def test_dio_reads_the_addendum_numbered_headings(self):
        _, out = self.run_cli('dio', 'feedstock')
        self.assertTrue(any(s['source'].startswith('DIO v3.1.1 addendum') for s in out['data']['sections']))

    def test_missing_kb_is_labelled_and_points_to_the_bootstrap(self):
        code, out = self.run_cli('--db', str(ROOT / 'no_such.sqlite'), 'card', 'Sol Ring')
        self.assertEqual(code, 2)
        self.assertEqual(out['grounding']['level'], 'doctrine_only')
        self.assertIn('tools/kb_bootstrap.py install', out['error'])


@unittest.skipUnless(DB.exists(), 'KB database not present (data/README.md)')
class Verbs(unittest.TestCase):
    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(['--db', str(DB), *args])
        return code, json.loads(buf.getvalue())

    def test_envelope_names_its_collection(self):
        code, out = self.run_cli('context')
        self.assertEqual(code, 0)
        pinned = json.loads((ROOT / 'tools' / 'kb_release.json').read_text(encoding='utf-8'))['release']
        self.assertEqual(out['collection']['release'], pinned)
        self.assertEqual(out['grounding']['level'], 'kb_grounded')
        self.assertEqual(out['collection']['release'], 'mtg-kb-v0.2.1-r20261030')
        self.assertTrue(all({'kind', 'support', 'grade'} <= set(c) for c in out['claims']))

    def test_card_separates_oracle_text_from_contract_readings(self):
        code, out = self.run_cli('card', 'Terra, Magical Adept')
        self.assertEqual(code, 0)
        kinds = {c['kind']: c for c in out['claims']}
        self.assertEqual(kinds['rules_text']['grade'], 'decision_grade')
        mech = [c for c in out['claims'] if c['kind'] == 'mechanics']
        self.assertTrue(mech and all(c['grade'] == 'exploratory' for c in mech))   # nothing is reviewed in r20261030

    def test_explore_works_without_a_seed_and_marks_discovery(self):
        code, out = self.run_cli('explore', '--ci', 'RG', '--limit', '5')
        self.assertEqual(code, 0)
        self.assertEqual(out['data']['mode'], 'divergent')
        self.assertTrue(out['claims'])
        self.assertTrue(all(c['discovery'] == 'unrequested' for c in out['claims']))

    def test_divergent_chains_start_at_the_seed(self):
        code, out = self.run_cli('explore', 'Terra, Magical Adept', '--mode', 'divergent', '--limit', '10')
        self.assertEqual(code, 0)
        for ch in out['data']['chains']:
            self.assertTrue(ch['first']['producer'].startswith('Terra, Magical Adept'))
            self.assertEqual(ch['first']['observer'], ch['second']['producer'])
            self.assertNotEqual((ch['first']['produces'], ch['first']['hook']), (ch['second']['produces'], ch['second']['hook']))

    def test_explore_without_pool_is_an_error_not_a_guess(self):
        code, out = self.run_cli('explore')
        self.assertEqual(code, 2)
        self.assertIn('error', out)

    def test_hypothesis_reports_unverified_links(self):
        code, out = self.run_cli('hypothesis', 'Cauldron of Essence', 'Knightfisher')
        self.assertEqual(code, 0)
        self.assertTrue(out['data']['links'] or out['data']['loops'])
        self.assertTrue(out['data']['unverified_contracts'])
        self.assertTrue(out['data']['would_settle_it'])

    def run_check(self, items):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(items, f)
        code, out = self.run_cli('check', f.name)
        self.assertEqual(code, 0)
        return out['claims']

    def test_check_grades_each_claim_by_kind(self):
        claims = self.run_check([{'text': 'owned', 'kind': 'inventory', 'cards': ['Cauldron of Essence']},
                                 {'text': 'faster', 'kind': 'performance'},
                                 {'text': 'likes it', 'kind': 'preference', 'deck': 'NoSuchDeck'}])
        self.assertEqual([c['evidence_grade'] for c in claims], ['decision_grade', 'exploratory', 'not_system_gradable'])
        # no assertion given: the source is good, but the claim itself is not checked, so it is not decision grade
        self.assertEqual([c['verdict'] for c in claims], ['NOT_CHECKED'] * 3)
        self.assertEqual(claims[0]['grade'], 'exploratory')

    # --- regressions from the Terra runs (Kate, 2026-10-27): the questions are no longer held out ---

    def test_check_never_turns_a_good_source_into_a_true_claim(self):
        claims = self.run_check([
            {'text': 'Leaves from the Vine is available for Steph', 'kind': 'inventory', 'cards': ['Leaves from the Vine']},
            {'text': 'a free copy exists', 'kind': 'inventory', 'cards': ['Leaves from the Vine'], 'assert': {'free_min': 1}},
            {'text': 'nonlegendary only', 'kind': 'rules_text', 'cards': ['Terra, Magical Adept'],
             'assert': {'text_contains': 'nonlegendary enchantment'}}])
        self.assertEqual(claims[0]['evidence_grade'], 'decision_grade')
        self.assertEqual((claims[0]['verdict'], claims[0]['grade']), ('NOT_CHECKED', 'exploratory'))
        self.assertEqual(claims[1]['verdict'], 'CONTRADICTED')          # owned 1, free 0
        self.assertEqual(claims[2]['verdict'], 'SUPPORTED')

    def test_a_true_assertion_does_not_verify_a_false_sentence(self):
        c = self.run_check([{'text': 'Leaves from the Vine has a free copy for Steph', 'kind': 'inventory',
                             'cards': ['Leaves from the Vine'], 'assert': {'owned_min': 1}}])[0]
        self.assertEqual((c['verdict'], c['verdict_on'], c['text_judged']), ('SUPPORTED', 'assertion', False))

    def hyp(self, a, b):
        code, out = self.run_cli('hypothesis', a, b)
        self.assertEqual(code, 0)
        return out['data']

    def test_copy_of_a_self_enter_enchantment_is_a_lead_not_a_blank(self):
        d = self.hyp('Terra, Magical Adept', 'Banishing Light')
        reentry = [l for l in d['links'] if l['observer'] == 'Banishing Light' and l['basis'] == 'reentry_of_target']
        self.assertTrue(reentry)
        self.assertEqual(reentry[0]['qualifiers'], 'unresolved')       # the contracts don't record that the token is a copy
        self.assertTrue(any(x['actor'].startswith('Terra') and x['acts_on'] == 'Banishing Light' for x in d['acts_on']))

    def test_terra_cycle_is_a_same_card_link(self):
        d = self.hyp('Terra, Magical Adept', 'Banishing Light')
        same = [l for l in d['same_card_links'] if l['produces'] == 'card.return_to_battlefield']
        self.assertTrue(same and all(l['observer'].startswith('Terra') for l in same))

    def test_type_qualifier_rejects_era_of_innovation(self):
        d = self.hyp('Terra, Magical Adept', 'Era of Innovation')
        self.assertFalse([l for l in d['links'] if l['produces'] == 'card.return_to_battlefield'])
        self.assertTrue(any('artifact or artificer' in l['qualifier_note'] for l in d['rejected_links']))

    def test_energy_loops_are_contested_and_do_not_hide_the_card(self):
        d = self.hyp('Terra, Magical Adept', 'Decoction Module')
        self.assertFalse(d['loops'])                                   # no contract records Decoction Module putting counters
        self.assertEqual({l['kb_check'] for l in d['loops_contested']}, {'unsupported_by_contracts'})
        self.assertTrue(d['loops_contested'])
        bounce = [x for x in d['acts_on'] if x['actor'] == 'Decoction Module']
        self.assertTrue(bounce and 'card.return_to_hand' in bounce[0]['produces'])

    def test_unsupported_theme_names_the_supported_ones(self):
        code, out = self.run_cli('explore', 'saga')
        self.assertEqual(code, 2)
        self.assertIn('self_mill', out['error'])

    def test_card_reports_availability_under_the_policy(self):
        code, out = self.run_cli('card', 'Leaves from the Vine')
        self.assertEqual(code, 0)
        av = out['data']['availability']
        self.assertEqual(av['usable_without_asking'], 0)
        self.assertIn('Necrobloom', av['in_other_built_decks'])

    def test_role_summary_reports_detected_candidates_not_verified_roles(self):
        # Golden Argosy was the sole "wipe" in both arms of the 2026-10-28 paired run (Kate's audit)
        code, out = self.run_cli('context', '--deck', 'Brigid')
        self.assertEqual(code, 0)
        roles = out['data']['roles']
        self.assertNotIn('single_source_roles', roles)
        self.assertNotIn('Golden Argosy', [v['card'] for v in roles['sole_detected_candidates'].values()])
        caveat = [c for c in out['claims'] if 'sole detected candidate' in c['text']]
        self.assertEqual(len(caveat), 1)
        self.assertEqual(caveat[0]['grade'], 'exploratory')

    # Zach's blind ChatGPT Merfolk test, 2026-10-31: a search for the word missed the type's generic support
    def test_typal_census_finds_members_support_and_protected_copies(self):
        code, out = self.run_cli('typal', 'Merfolk')
        self.assertEqual(code, 0)
        d = out['data']
        self.assertEqual(d['counts']['members'], 35)
        self.assertEqual(d['members_by_color_identity'], {'U': 21, 'W': 7, 'WU': 4, 'UB': 2, 'UG': 1})
        self.assertEqual(sum(m['free'] for m in d['members']), 75)
        self.assertIn('kindred', {m['kind'] for m in d['members'] if m['card'] == 'Wanderwine Farewell'})
        found = {x['card'] for g in ('every_type', 'type_support', 'names_the_type') for x in d[g]}
        for name in ('Harmonized Crescendo', 'Gathering Stone', 'Kindred Judgment', 'Kindred Summons', 'Distant Melody',
                     "Urza's Incubator", 'Omni-Changeling', 'Seahunter'):
            self.assertIn(name, found)
        for name in ('Distant Melody', "Urza's Incubator", 'Secluded Courtyard', 'Unclaimed Territory'):
            self.assertIn(name, d['held_in_protected_decks'])
        self.assertEqual({s['commander'] for s in d['commander_candidates']},
                         {'Emperor Mihail II', 'Orysa, Tide Choreographer', 'Tatyova, Steward of Tides', 'Vohar, Vodalian Desecrator'})
        self.assertEqual(d['identities_without_type_commander'], ['W', 'WU'])
        self.assertIn('Gathering Stone', d['tag_gaps'])           # the Sheet Roles tags miss it: a data-layer gap
        for k, v in d['counts'].items():                         # the counts agree with the lists they summarise
            self.assertEqual(v, len(d[k]))
        lexical = [c for c in out['claims'] if c['support'] == 'lexical_match']
        self.assertTrue(lexical and all(c['grade'] == 'exploratory' for c in lexical))

    def test_typal_rejects_a_word_no_type_line_has(self):
        code, out = self.run_cli('typal', 'Merfolkk')
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
