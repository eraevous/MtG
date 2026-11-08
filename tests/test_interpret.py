"""kb/interpret.py: the append-only, hash-chained interpretation log (DEC-152, HO-MTG-20261107-92QA).

What a reviewer should check here: (1) the log can never hold a state other than `candidate`, whatever the caller
passes; (2) a reading without evidence, or an agreement with one voice, is refused; (3) the chain breaks on any edit;
(4) a card in the KB binds to its current Oracle text hash so later text changes are visible. The tests run against a
tiny SQLite stand-in for the KB, so they need no release database."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kb'))
import interpret as I  # noqa: E402

TEXT_SHA = 'a' * 64


def reading(party='claude:mtg', model='claude-fable-5-1', text='The Zombie replaces the Plant.', cites=('oracle', '614.1a')):
    return {'party': party, 'model': model, 'reading': text, 'cr_citations': list(cites)}


def body(**kw):
    b = {'utc': '2026-11-07T04:00:00+00:00', 'subject_kind': 'card', 'card_or_mechanic': 'The Necrobloom',
         'oracle_id': 'b981af39-4ee6-4fbc-9a89-618dcad9dfbf', 'oracle_text_sha256': TEXT_SHA, 'contract_id': None, 'in_kb': True,
         'kb_release': 'test', 'question': 'Does the seven-names branch replace the Plant?',
         'readings': [reading(), reading(party='kate', model='gpt-5-mini')], 'outcome': 'agreed',
         'verification_state': I.CANDIDATE, 'source': 'unit-test', 'recorded_by': 'unit-test', 'notes': None, 'supersedes': None}
    b.update(kw)
    return b


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = Path(self.tmp.name)
        self.log = d / 'interpretations.jsonl'
        self.db = d / 'kb.sqlite'
        con = sqlite3.connect(self.db)
        con.executescript("""
            create table cards(card_name text primary key, oracle_text_sha256 text);
            create table card_identity(card_name text primary key, oracle_id text);
            create table current_contracts(contract_id text primary key, card_name text);
        """)
        con.execute("insert into cards values('The Necrobloom', ?)", (TEXT_SHA,))
        con.execute("insert into card_identity values('The Necrobloom', 'b981af39-4ee6-4fbc-9a89-618dcad9dfbf')")
        con.execute("insert into current_contracts values('card.The%20Necrobloom.op001', 'The Necrobloom')")
        con.execute("insert into current_contracts values('card.Other.op001', 'Other Card')")
        con.commit(); con.close()
        (d / 'SOURCE_MANIFEST.json').write_text(json.dumps({'release': 'mtg-kb-test'}), encoding='utf-8')

    def tearDown(self): self.tmp.cleanup()


class Refusals(Sandbox):
    def test_only_candidate_is_ever_written(self):
        for state in ('verified', 'semantic_reviewed', 'accepted', None, ''):
            with self.assertRaises(ValueError, msg=state): I.add(self.log, body(verification_state=state))
        self.assertFalse(self.log.exists())

    def test_a_reading_needs_evidence(self):
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[reading(cites=()), reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[reading(cites=('I think so',)), reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[reading(text='  '), reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[]))

    def test_citation_forms(self):
        for ok in ('oracle', '702', '702.52', '704.5q', '106.12a', 'ruling:2024-06-07'):
            self.assertTrue(I.citation_ok(ok), ok)
        for bad in ('CR 702.52', '70', 'ruling:yesterday', '', 7, 'oracle text'):
            self.assertFalse(I.citation_ok(bad), bad)

    def test_agreement_takes_two_parties(self):
        one = [reading(), reading(model='gpt-5-mini')]            # same party, two models: still one voice
        with self.assertRaises(ValueError): I.add(self.log, body(readings=one, outcome='agreed'))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=one, outcome='contested'))
        I.add(self.log, body(readings=one, outcome='needs-zach'))  # one voice may ask Zach

    def test_outcome_and_kind_vocabulary(self):
        with self.assertRaises(ValueError): I.add(self.log, body(outcome='verified'))
        with self.assertRaises(ValueError): I.add(self.log, body(subject_kind='deck'))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[dict(reading(), extra=1), reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(in_kb=True, oracle_id=None))


class KateAmendments(Sandbox):
    """Kate's round-17 amendments (kairos/kate-round-17.md) are PROPOSALS: the fields are optional, so a row
    without them is still valid, and vocabulary-checked when present, so adopting them later needs no schema change."""

    def test_absent_is_valid_and_hashes_as_none(self):
        rec = I.add(self.log, body())
        self.assertEqual((rec.get('layer'), rec.get('disagreement_type'), rec.get('scenarios')), (None, None, None))
        self.assertEqual(I.read(self.log)[0]['interpretation_id'], rec['interpretation_id'])

    def test_layer_vocabulary(self):
        for ok in I.LAYERS: I.add(self.log, body(layer=ok))
        with self.assertRaises(ValueError): I.add(self.log, body(layer='strategy'))

    def test_independent_reading_fields(self):
        r = dict(reading(), independent=True, uncertainty='low: "instead" is replacement wording', scenario='7 named lands, Plant trigger')
        I.add(self.log, body(readings=[r, reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[dict(reading(), independent='yes'), reading(party='kate')]))
        with self.assertRaises(ValueError): I.add(self.log, body(readings=[dict(reading(), uncertainty=''), reading(party='kate')]))

    def test_disagreement_type_only_on_disagreement(self):
        I.add(self.log, body(outcome='contested', disagreement_type='ontology_representation'))
        I.add(self.log, body(outcome='needs-zach', disagreement_type='contextual_role'))
        with self.assertRaises(ValueError): I.add(self.log, body(outcome='agreed', disagreement_type='oracle_rules'))
        with self.assertRaises(ValueError): I.add(self.log, body(outcome='contested', disagreement_type='vibes'))

    def test_scenarios_come_as_a_pair(self):
        sc = {'positive': 'Seven differently named lands, Plant enters: a Zombie instead.', 'near_miss': 'Seven lands, two share a name: a Plant.', 'kb_output_changed': None}
        I.add(self.log, body(scenarios=sc))
        I.add(self.log, body(scenarios=dict(sc, kb_output_changed=True)))
        with self.assertRaises(ValueError): I.add(self.log, body(scenarios={'positive': 'only the happy path'}))
        with self.assertRaises(ValueError): I.add(self.log, body(scenarios=dict(sc, near_miss='')))
        with self.assertRaises(ValueError): I.add(self.log, body(scenarios=dict(sc, kb_output_changed='maybe')))
        with self.assertRaises(ValueError): I.add(self.log, body(scenarios=dict(sc, extra=1)))


class Chain(Sandbox):
    def test_append_chains_and_edit_breaks(self):
        r1 = I.add(self.log, body()); r2 = I.add(self.log, body(question='Is dredge 2 a replacement of the draw?'))
        self.assertEqual(r1['prev'], ''); self.assertEqual(r2['prev'], r1['interpretation_id'])
        self.assertEqual(len(I.read(self.log)), 2)
        text = self.log.read_text(encoding='utf-8').replace('"agreed"', '"contested"', 1)
        self.log.write_text(text, encoding='utf-8')
        with self.assertRaises(ValueError): I.read(self.log)

    def test_supersedes_is_an_id(self):
        r1 = I.add(self.log, body())
        with self.assertRaises(ValueError): I.add(self.log, body(supersedes='the first one'))
        I.add(self.log, body(supersedes=r1['interpretation_id'], outcome='contested'))


class Binding(Sandbox):
    def test_card_in_kb_binds_text_hash_and_identity(self):
        kb = I.bind_to_kb(self.db, 'The Necrobloom', 'card.The%20Necrobloom.op001')
        self.assertEqual(kb, {'in_kb': True, 'oracle_id': 'b981af39-4ee6-4fbc-9a89-618dcad9dfbf', 'oracle_text_sha256': TEXT_SHA, 'kb_release': 'mtg-kb-test'})
        self.assertEqual(I.bind_to_kb(self.db, 'Not Owned', None)['in_kb'], False)
        with self.assertRaises(ValueError): I.bind_to_kb(self.db, 'The Necrobloom', 'card.Other.op001')
        with self.assertRaises(ValueError): I.bind_to_kb(self.db, 'The Necrobloom', 'card.Nope.op009')

    def test_stale_reports_changed_text(self):
        I.add(self.log, body())
        self.assertEqual(I.stale(self.log, self.db), [])
        con = sqlite3.connect(self.db); con.execute("update cards set oracle_text_sha256=?", ('b' * 64,)); con.commit(); con.close()
        self.assertEqual(len(I.stale(self.log, self.db)), 1)
        self.assertIsNone(I.stale(self.log, self.db.with_name('missing.sqlite')))


class Cli(Sandbox):
    def run_cli(self, *args, stdin=None):
        env = dict(os.environ, RELAYKIT_ACTOR='claude:mtg#test')
        return subprocess.run([sys.executable, str(ROOT / 'kb' / 'interpret.py'), '--file', str(self.log), '--db', str(self.db), *args],
                              capture_output=True, text=True, input=stdin, env=env)

    def test_add_show_verify(self):
        rd = json.dumps([reading(), reading(party='kate', model='gpt-5-mini', text='Agreed: "instead" marks a replacement of the token creation.', cites=('614.1a',))])
        r = self.run_cli('add', '--kind', 'card', '--name', 'The Necrobloom', '--question', 'Replace or add?', '--readings', '-',
                         '--outcome', 'agreed', '--source', 'unit-test', '--contract', 'card.The%20Necrobloom.op001', stdin=rd)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec['verification_state'], 'candidate'); self.assertEqual(rec['recorded_by'], 'claude:mtg#test')
        self.assertEqual(rec['kb_release'], 'mtg-kb-test'); self.assertTrue(rec['in_kb'])
        v = json.loads(self.run_cli('verify').stdout)
        self.assertEqual((v['lines'], v['chain'], v['promoted'], v['stale_text']), (1, 'ok', 0, []))
        shown = json.loads(self.run_cli('show', '--name', 'The Necrobloom').stdout)
        self.assertEqual(len(shown), 1)
        m = self.run_cli('add', '--kind', 'mechanic', '--name', 'proliferate', '--question', 'Does proliferate add new counter kinds?',
                         '--readings', '-', '--outcome', 'needs-zach', '--source', 'unit-test', stdin=json.dumps([reading(cites=('701.27a',))]))
        self.assertEqual(m.returncode, 0, m.stderr)
        self.assertFalse(json.loads(m.stdout)['in_kb'])

    def test_optional_flags_round_trip(self):
        d = Path(self.tmp.name)
        (d / 'readings.json').write_text(json.dumps([dict(reading(), independent=True), dict(reading(party='kate', model='gpt-5-mini'), independent=True)]), encoding='utf-8')
        (d / 'scen.json').write_text(json.dumps({'positive': 'p', 'near_miss': 'n', 'kb_output_changed': False}), encoding='utf-8')
        r = self.run_cli('add', '--kind', 'card', '--name', 'The Necrobloom', '--question', 'Replace or add?', '--readings', str(d / 'readings.json'),
                         '--outcome', 'contested', '--source', 'unit-test', '--layer', 'dio_representation',
                         '--disagreement-type', 'ontology_representation', '--scenarios', str(d / 'scen.json'))
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual((rec['layer'], rec['disagreement_type'], rec['scenarios']['kb_output_changed']), ('dio_representation', 'ontology_representation', False))
        self.assertTrue(all(x['independent'] for x in rec['readings']))
        v = json.loads(self.run_cli('verify').stdout)
        self.assertEqual((v['chain'], v['with_scenarios'], v['kb_output_changed'], v['promoted']), ('ok', 1, 0, 0))
        bad = self.run_cli('add', '--kind', 'card', '--name', 'The Necrobloom', '--question', 'q', '--readings', str(d / 'readings.json'),
                           '--outcome', 'agreed', '--source', 'unit-test', '--disagreement-type', 'oracle_rules')
        self.assertNotEqual(bad.returncode, 0)


if __name__ == '__main__':
    unittest.main()
