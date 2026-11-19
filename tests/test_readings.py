"""mtgtools reading (D-0033): a derived, read-only page over kb/overrides/interpretations.jsonl.

What a reviewer should check here: (1) the verb prints `candidate` and grades every claim exploratory, even for a row
that claims another state; (2) superseded rows leave the current set; (3) a broken chain hides every row and says so;
(4) Oracle-text drift is flagged when the KB is present; (5) the verb needs no KB and writes no file; (6) the renderer
writes only into a gitignored directory and never calls a reading anything but candidate. No release database needed.
"""
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'kb')); sys.path.insert(0, str(ROOT / 'tools'))
import chain  # noqa: E402
import interpret as I  # noqa: E402
from mtgtools import cli, readings as R  # noqa: E402
import render_readings as RR  # noqa: E402

SHA = 'a' * 64


def row(**kw):
    b = {'utc': '2026-11-18T00:00:00+00:00', 'subject_kind': 'card', 'card_or_mechanic': 'Evolution Sage', 'oracle_id': 'test-oracle-id',
         'oracle_text_sha256': SHA, 'contract_id': 'card.Evolution%20Sage.op001', 'in_kb': True, 'kb_release': 'test',
         'question': 'Is proliferate a put-counter event?',
         'readings': [{'party': 'claude:mtg', 'model': 'm1', 'reading': 'Yes.', 'cr_citations': ['701.27a']},
                      {'party': 'kate', 'model': 'm2', 'reading': 'Yes.', 'cr_citations': ['122.6']}],
         'outcome': 'agreed', 'verification_state': I.CANDIDATE, 'source': 'unit-test', 'recorded_by': 'unit-test',
         'notes': 'KB gap: feeds is empty.', 'supersedes': None}
    b.update(kw)
    return b


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        self.log = self.d / 'interpretations.jsonl'

    def tearDown(self): self.tmp.cleanup()


class Page(Sandbox):
    def test_candidate_only_whatever_the_row_says(self):
        chain.append(self.log, I.FIELDS, I.ID_KEY, row(verification_state='verified'))   # bypasses interpret.check on purpose
        data, claims = R.reading('evolution sage', log=self.log)
        self.assertEqual(data['subject'], 'Evolution Sage')
        self.assertEqual(data['banner']['verification_state'], 'candidate')
        self.assertEqual(data['current'][0]['verification_state'], 'candidate')
        self.assertEqual(data['current'][0]['logged_state'], 'verified')
        self.assertEqual({c['grade'] for c in claims}, {'exploratory'})
        self.assertNotIn('verified', json.dumps(claims))

    def test_superseded_rows_leave_the_current_set(self):
        first = I.add(self.log, row(outcome='needs-zach', readings=row()['readings'][:1]))
        I.add(self.log, row(supersedes=first[I.ID_KEY]))
        data, claims = R.reading('Evolution Sage', log=self.log)
        self.assertEqual([v['outcome'] for v in data['current']], ['agreed'])
        self.assertEqual(data['superseded'][0]['interpretation_id'], first[I.ID_KEY])
        self.assertEqual(len(claims), 1)
        self.assertEqual(data['by_outcome'], {'agreed': [data['current'][0]['interpretation_id']]})

    def test_broken_chain_shows_nothing_and_says_so(self):
        I.add(self.log, row())
        self.log.write_text(self.log.read_text(encoding='utf-8').replace('Yes.', 'No.'), encoding='utf-8')
        data, claims = R.reading('Evolution Sage', log=self.log)
        self.assertEqual(data['current'], [])
        self.assertTrue(data['banner']['chain'].startswith('broken'))
        self.assertIn('hash-chain', claims[-1]['text'])

    def test_unknown_subject_is_an_empty_page_not_an_error(self):
        I.add(self.log, row())
        data, claims = R.reading('proliferate', log=self.log)
        self.assertEqual((data['current'], claims), ([], []))
        self.assertTrue(any('nobody has asked' in x for x in data['limits']))

    def test_oracle_drift_is_flagged_with_a_kb(self):
        I.add(self.log, row())
        con = sqlite3.connect(':memory:')
        con.execute('create table cards(card_name text, oracle_text_sha256 text)')
        con.execute("insert into cards values('Evolution Sage', ?)", ('b' * 64,))
        with patch.object(R.kb, 'card', return_value={'contracts': [
                {'contract_id': 'card.Evolution%20Sage.op001', 'queue_state': 'ready_for_review', 'failed_checks': []}]}):
            data, claims = R.reading('Evolution Sage', con, log=self.log)
        self.assertTrue(data['current'][0]['oracle_text_changed_since'])
        self.assertIn('oracle_text_changed_since_reading', claims[0]['evidence'])
        self.assertEqual(data['kb_contracts'][0]['queue_state'], 'ready_for_review')

    def test_cli_needs_no_kb_and_writes_nothing(self):
        I.add(self.log, row())
        before = sorted(p.name for p in self.d.iterdir())
        out = io.StringIO()
        with patch.object(R.interpret, 'DEFAULT', self.log), patch.object(R.reading, '__defaults__', (None, self.log)), \
                redirect_stdout(out):
            code = cli.main(['--db', str(self.d / 'missing.sqlite'), 'reading', 'Evolution Sage'])
        env = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(env['grounding']['level'], 'log_only')
        self.assertEqual(env['data']['banner']['log_rows'], 1)
        self.assertEqual(sorted(p.name for p in self.d.iterdir()), before)


class Renderer(Sandbox):
    def env(self):
        I.add(self.log, row())
        data, claims = R.reading('Evolution Sage', log=self.log)
        return {'data': data, 'claims': claims, 'grounding': {'level': 'log_only'}, 'collection': {'release': 'x'}}

    def test_page_says_candidate_and_quotes_readings(self):
        page = RR.render(self.env())
        self.assertIn('(candidate)', page.splitlines()[0])
        self.assertIn('Generated, not a home', page)
        self.assertIn('none (log only)', page)
        self.assertIn('> Yes.', page)
        self.assertNotRegex(page.lower(), r'\bverified\b')

    def test_reader_uncertainty_and_scenarios_survive(self):
        rs = row()['readings']
        rs[1] = dict(rs[1], uncertainty='medium: no ruling in hand', scenario='Proliferate two creatures.')
        I.add(self.log, row(readings=rs, scenarios={'positive': 'P case', 'near_miss': 'N case', 'kb_output_changed': None}))
        data, claims = R.reading('Evolution Sage', log=self.log)
        v = data['current'][0]
        self.assertEqual(v['readings'][1]['uncertainty'], 'medium: no ruling in hand')
        self.assertEqual(v['scenarios']['near_miss'], 'N case')
        page = RR.render({'data': data, 'claims': claims, 'grounding': {'level': 'log_only'}, 'collection': {}})
        for text in ('medium: no ruling in hand', 'Proliferate two creatures.', 'P case', 'N case'):
            self.assertIn(text, page)

    def test_line_breaks_in_logged_fields_cannot_forge_a_heading(self):
        # interpret.check accepts any non-empty string for party, model and source, line breaks included.
        rs = row()['readings']
        rs[0] = dict(rs[0], party='claude:mtg\n\n## agreed · verified · `0000`', model='claude-test')
        rs[1] = dict(rs[1], model='gpt-test')
        I.add(self.log, row(readings=rs, source='unit\n# Verified ruling', card_or_mechanic='Evolution Sage\n# verified'))
        data, claims = R.reading('Evolution Sage\n# verified', log=self.log)
        page = RR.render({'data': data, 'claims': claims, 'grounding': {'level': 'log_only'}, 'collection': {}})
        headings = [ln for ln in page.splitlines() if ln.startswith('#')]
        self.assertEqual(len(headings), 3, headings)   # the title, one row, Limits
        self.assertTrue(all('verified' not in h.lower() or h.startswith('# Readings:') for h in headings), headings)
        self.assertIn('Reading by claude:mtg ## agreed · verified · `0000` (claude-test)', page)
        self.assertIn('Source: unit # Verified ruling', page)

    def test_a_crashed_verb_is_a_clean_error_not_a_traceback(self):
        done = type('P', (), {'stdout': '', 'stderr': 'Traceback ...\nsqlite3.DatabaseError: file is not a database', 'returncode': 1})()
        with patch.object(RR.subprocess, 'run', return_value=done):
            with self.assertRaises(SystemExit) as e:
                RR.fetch('Evolution Sage')
        self.assertIn('printed no JSON (exit 1): sqlite3.DatabaseError', str(e.exception))

    # Kate's records for #56 (kate-replies:replies/HO-MTG-20261119-EFWD--b77c61d4598b.md): RENDER-INLINE-01, FETCH-NO-JSON-01.
    def test_inline_folding_covers_cr_and_crlf_too(self):   # RENDER-INLINE-01
        for brk in ('\n', '\r\n', '\r'):
            with self.subTest(brk=repr(brk)):
                self.assertEqual(RR._inline(f'claude:mtg{brk}{brk}## verified'), 'claude:mtg ## verified')
        self.assertEqual(RR._inline('Evolution Sage'), 'Evolution Sage')
        self.assertEqual(RR._inline('a \t  b'), 'a b')

    def test_multiline_fields_stay_quoted_across_blank_lines(self):   # RENDER-INLINE-01
        quoted = RR._quote('first\n\n## verified\r\nlast')
        self.assertTrue(all(ln.startswith('>') for ln in quoted.splitlines()), quoted)

    def test_no_json_error_edge_cases(self):   # FETCH-NO-JSON-01
        for stderr, code, want in (('', 1, '(exit 1): no output'), ('', 0, '(exit 0): no output'),
                                   ('one\ntwo\nlast line\n', 2, '(exit 2): last line')):
            with self.subTest(stderr=stderr, code=code):
                done = type('P', (), {'stdout': '', 'stderr': stderr, 'returncode': code})()
                with patch.object(RR.subprocess, 'run', return_value=done):
                    with self.assertRaises(SystemExit) as e:
                        RR.fetch('Evolution Sage')
                self.assertIn(want, str(e.exception))
                self.assertEqual(len(str(e.exception).splitlines()), 1)
        ok = type('P', (), {'stdout': '{"data": {}}', 'stderr': '', 'returncode': 0})()
        with patch.object(RR.subprocess, 'run', return_value=ok):
            self.assertEqual(RR.fetch('Evolution Sage'), {'data': {}})

    def test_refuses_an_output_directory_git_tracks(self):
        with self.assertRaises(SystemExit):
            RR.main(['--out', str(ROOT / 'docs' / 'readings'), 'Evolution Sage'])
        self.assertFalse((ROOT / 'docs' / 'readings').exists())

    def test_default_output_is_gitignored(self):
        self.assertTrue(RR.ignored(RR.OUT / 'probe.md'))


if __name__ == '__main__':
    unittest.main()
