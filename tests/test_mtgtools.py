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
        self.assertEqual(out['collection']['release'], 'mtg-kb-v0.2.1-r20261024d')
        self.assertTrue(all({'kind', 'support', 'grade'} <= set(c) for c in out['claims']))

    def test_card_separates_oracle_text_from_contract_readings(self):
        code, out = self.run_cli('card', 'Terra, Magical Adept')
        self.assertEqual(code, 0)
        kinds = {c['kind']: c for c in out['claims']}
        self.assertEqual(kinds['rules_text']['grade'], 'decision_grade')
        mech = [c for c in out['claims'] if c['kind'] == 'mechanics']
        self.assertTrue(mech and all(c['grade'] == 'exploratory' for c in mech))   # nothing is reviewed in r20261024d

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

    def test_check_grades_each_claim_by_kind(self):
        import tempfile
        items = [{'text': 'owned', 'kind': 'inventory', 'cards': ['Cauldron of Essence']},
                 {'text': 'faster', 'kind': 'performance'},
                 {'text': 'likes it', 'kind': 'preference', 'deck': 'NoSuchDeck'}]
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(items, f)
        code, out = self.run_cli('check', f.name)
        self.assertEqual(code, 0)
        self.assertEqual([c['grade'] for c in out['claims']], ['decision_grade', 'exploratory', 'not_system_gradable'])


if __name__ == '__main__':
    unittest.main()
