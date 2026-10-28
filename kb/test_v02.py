"""v0.2 tests: python -m unittest -v test_v02.py  (needs mtg_cards_v0.2.sqlite built by migrate_v02.py; no hash-seed pinning)"""
import json, random, shutil, sqlite3, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'vendor'))
DB = HERE / 'mtg_cards_v0.2.sqlite'
import kbfacts as F, review as R, migrate_v02 as M, oracle_refresh as O, freeze_check as Z, kbq, mana as MANA, contracts as K, scenarios as SC


def ro(p=DB):
    c = sqlite3.connect(Path(p).resolve().as_uri() + '?mode=ro', uri=True); c.row_factory = sqlite3.Row; return c


class Scratch:
    """A writable copy of the built DB plus an empty overlay file, for overlay/compile/refresh tests."""
    def __enter__(self):
        self.dir = Path(tempfile.mkdtemp()); self.db = self.dir / 'kb.sqlite'; shutil.copy(DB, self.db)
        self.overlay = self.dir / 'overlay.jsonl'; self.overlay.write_text('')
        self.con = sqlite3.connect(self.db); self.con.row_factory = sqlite3.Row
        return self

    def __exit__(self, *a):
        self.con.close(); shutil.rmtree(self.dir)

    def review(self, cid, decision='verified', tests=None, source='test fixture', registry=None, **kw):
        k = self.con.execute('select card_name,contract_sha256 from current_contracts where contract_id=?', (cid,)).fetchone()
        osha = self.con.execute('select oracle_text_sha256 from cards where card_name=?', (k['card_name'],)).fetchone()[0]
        rsha = self.con.execute('select rules_text_sha256 from rules_text where card_name=?', (k['card_name'],)).fetchone()[0]
        if tests is None: tests = [s['id'] for s in SC.load().values() if s['contract_id'] == cid]
        body = dict({'subject_kind': 'operation_contract', 'subject_id': cid, 'card_name': k['card_name'], 'decision': decision, 'reviewer': 'unit-test',
                     'reviewed_utc': '2026-10-20T21:00:00+00:00', 'source': source, 'oracle_text_sha256': osha, 'contract_sha256': k['contract_sha256'],
                     'tests': list(tests), 'notes': None, 'supersedes': None, 'rules_text_sha256': rsha, 'scope': 'semantic'}, **kw)
        return R.append(self.con, self.overlay, body, registry)

    def apply(self):
        """Replay the overlay, then compile, certify and recompute the verification states, as a rebuild would.
        Returns the number of compiled (semantically reviewed + lossless) actions."""
        self.con.execute('drop trigger review_overlay_append_only_d'); self.con.execute('delete from review_overlay')
        self.con.execute("create trigger review_overlay_append_only_d before delete on review_overlay begin select raise(abort,'review_overlay is append-only'); end")
        R.replay(self.con, self.overlay)
        st = M.compile_and_certify(self.con, 'test', SC.load(), 'test-run')
        self.con.execute('delete from contract_verification'); M.verification_states(self.con); self.con.commit()
        return st['compiled']


LOSSLESS = 'card.Cremate.op002'            # "Draw a card.": scenario cremate.draw has semantic and runtime parts
LOSSY = 'card.Orzhov%20Basilica.op003'     # "{T}: Add {W}{B}.": the 0.3.0 action records only "2 mana"


def ready_with_action(c):
    """A reviewable contract with an action and a passing scenario (the review gate needs a real test)."""
    return LOSSLESS


class V01Preserved(unittest.TestCase):
    def test_counts(self):
        c = ro()
        for t, n in [('cards', 3520), ('candidate_operations', 4961), ('projected_abilities', 3709), ('capability_claims', 26494)]:
            self.assertEqual(c.execute(f'select count(*) from {t}').fetchone()[0], n, t)
        self.assertEqual(c.execute('select count(*) from deck_card_counts where total_cards=100').fetchone()[0], 13)
        self.assertEqual(c.execute('pragma integrity_check').fetchone()[0], 'ok')

    def test_nothing_reviewed_without_review(self):
        c = ro()
        self.assertEqual(c.execute("select count(*) from validation_queue where queue_state='semantic_reviewed'").fetchone()[0], 0)
        self.assertEqual(c.execute('select count(*) from contract_verification where mechanically_supported=1').fetchone()[0], 0)
        self.assertEqual(c.execute('select count(*) from compiled_actions').fetchone()[0], 0)
        self.assertEqual(c.execute("select count(*) from candidate_operations where verification_status<>'unverified_candidate'").fetchone()[0], 0)

    def test_contracts_keep_exact_text_and_evidence(self):
        c = ro()
        for r in c.execute('select k.exact_text,k.contract_json,o.oracle_clause,o.raw_json from operation_contracts k join candidate_operations o on o.operation_id=k.source_operation_id'):
            self.assertEqual(r['exact_text'], r['oracle_clause'])
            self.assertEqual(json.loads(r['contract_json'])['evidence']['legacy_fields'], json.loads(r['raw_json']))


class Facts(unittest.TestCase):
    def test_sample_parity_with_runtime_readers(self):
        from sqlite_bridge import SQLiteInventory
        from mtg_eval import semantics as S, structure as T
        import kb_policy
        inv = SQLiteInventory(DB); c = ro(); kb_policy.apply(inv, c)
        names = sorted(inv.cards); random.Random(7).shuffle(names)
        for n in names[:150]:
            r = inv.cards[n]; t = S.clean(r['Oracle Text'], n)
            get = lambda kind, key: F.loads(c.execute('select value_json from derived_facts where fact_kind=? and input_key=?', (kind, key)).fetchone()[0])
            self.assertEqual(get('clause_audit', F.sha(n, str(r['Oracle Text']))), S.clause_audit(r['Oracle Text'], n), n)
            self.assertEqual(get('protection_profile', F.sha(t)), S.protection_profile(t), n)
            self.assertEqual(get('wipe_kind', F.sha(t)), S.wipe_kind(t), n)
            self.assertEqual(get('resource_claims', F.sha(str(r['Oracle Text']))), T.resource_claims(str(r['Oracle Text'])), n)

    def test_strict_evaluator_has_no_misses(self):
        from bridge_v02 import open_evaluator
        ev = open_evaluator(DB, games=20, engine_games=1, strict=True)
        r = ev.deck('Necrobloom')
        self.assertEqual(r['title'], 'Deck: Necrobloom')
        self.assertEqual(ev.facts.stats['misses'], {})


class Overlay(unittest.TestCase):
    def test_append_only(self):
        with Scratch() as s:
            s.review(ready_with_action(s.con), decision='needs_review', tests=())
            s.apply()
            with self.assertRaises(sqlite3.IntegrityError): s.con.execute("update review_overlay set decision='verified'")
            with self.assertRaises(sqlite3.IntegrityError): s.con.execute('delete from review_overlay')

    def test_verified_needs_tests_source_and_current_sha(self):
        with Scratch() as s:
            cid = ready_with_action(s.con)
            with self.assertRaises(ValueError): s.review(cid, tests=())
            with self.assertRaises(ValueError): s.review(cid, source='')
            with self.assertRaises(ValueError): s.review(cid, oracle_text_sha256='0' * 64)
            with self.assertRaises(ValueError): s.review(cid, contract_sha256='0' * 64)
            blocked = s.con.execute("select contract_id from validation_queue where queue_state='blocked' limit 1").fetchone()[0]
            with self.assertRaises(ValueError): s.review(blocked)

    def test_chain_detects_tampering(self):
        with Scratch() as s:
            s.review(ready_with_action(s.con), decision='needs_review', tests=())
            line = s.overlay.read_text().replace('needs_review', 'verified'); s.overlay.write_text(line)
            with self.assertRaises(ValueError): R.read_overlay(s.overlay)

    def test_verified_contract_compiles_and_reaches_runtime(self):
        with Scratch() as s:
            cid = ready_with_action(s.con); s.review(cid)
            self.assertEqual(s.apply(), 1)
            self.assertEqual(s.con.execute('select queue_state from validation_queue where contract_id=?', (cid,)).fetchone()[0], 'semantic_reviewed')
            self.assertEqual(s.con.execute('select count(*) from runtime_verified_actions').fetchone()[0], 1)

    def test_reviewed_lossy_contract_never_reaches_runtime(self):
        with Scratch() as s:
            s.review(LOSSY); self.assertEqual(s.apply(), 0)
            v = s.con.execute('select * from contract_verification where contract_id=?', (LOSSY,)).fetchone()
            self.assertEqual((v['semantic_contract_reviewed'], v['runtime_compilation_complete'], v['mechanically_supported']), (1, 0, 0))
            self.assertEqual(s.con.execute('select count(*) from runtime_verified_actions').fetchone()[0], 0)
            self.assertEqual(s.con.execute("select count(*) from qa_queue where issue_type='reviewed_contract_lossy_compile'").fetchone()[0], 1)

    def test_text_change_makes_review_stale(self):
        with Scratch() as s:
            cid = ready_with_action(s.con); s.review(cid); s.apply()
            name = s.con.execute('select card_name from current_contracts where contract_id=?', (cid,)).fetchone()[0]
            s.con.execute("update cards set oracle_text_sha256='changed' where card_name=?", (name,))  # new Sheet text after a rebuild
            self.assertEqual(s.con.execute('select applicability from effective_reviews where subject_id=?', (cid,)).fetchone()[0], 'stale_text_changed')
            self.assertEqual(s.con.execute('select queue_state from validation_queue where contract_id=?', (cid,)).fetchone()[0], 'review_stale')
            self.assertEqual(s.con.execute('select count(*) from runtime_verified_actions').fetchone()[0], 0)

    def test_parser_update_does_not_inherit_review(self):
        with Scratch() as s:
            cid = ready_with_action(s.con); s.review(cid); s.apply()
            k = dict(s.con.execute('select * from operation_contracts where contract_id=?', (cid,)).fetchone())
            k.update(contract_version=2, contract_sha256='new-drafter-output', drafter_version='next')
            s.con.execute(f"insert into operation_contracts({','.join(k)}) values({','.join('?' * len(k))})", list(k.values()))
            self.assertEqual(s.con.execute('select applicability from effective_reviews where subject_id=?', (cid,)).fetchone()[0], 'stale_contract_changed')
            self.assertEqual(s.con.execute('select count(*) from runtime_verified_actions').fetchone()[0], 0)

    def test_later_line_supersedes(self):
        with Scratch() as s:
            cid = ready_with_action(s.con); first = s.review(cid); s.review(cid, decision='revoked', tests=(), supersedes=first['review_id'])
            s.apply()
            self.assertEqual(s.con.execute('select queue_state from validation_queue where contract_id=?', (cid,)).fetchone()[0], 'ready_for_review')
            self.assertEqual(s.con.execute('select count(*) from review_overlay').fetchone()[0], 2)


class Typing(unittest.TestCase):
    def test_mana_cost_pips(self):
        p = MANA.parse_cost('{2}{G/W}{G/P}{2/B}{C}{X}')['pips']
        self.assertEqual([x['type'] for x in p], ['generic', 'hybrid', 'phyrexian', 'mono_hybrid', 'colorless', 'X'])
        self.assertEqual(p[2]['alternatives'], [{'color': 'G'}, {'pay_life': 2}])
        self.assertEqual(p[3]['alternatives'], [{'generic': 2}, {'color': 'B'}])
        self.assertTrue(MANA.parse_cost('{C}{C}')['requires_colorless'])

    def test_mana_production(self):
        cases = {'{T}: Add {C}.': ('colorless', 1), '{T}: Add {R} or {G}.': ('alternatives', 1), '{T}: Add {G}{G}.': ('fixed', 2),
                 '{T}: Add one mana of any color.': ('any_color', 1), 'Add two mana in any combination of colors.': ('any_combination', 2),
                 '{T}: Add one mana of the chosen color.': ('chosen_color', 1)}
        for t, (mode, n) in cases.items():
            r = MANA.parse_production(t); self.assertEqual((r['mode'], r['amount']), (mode, n), t)
        self.assertFalse(MANA.parse_production('{T}: Add {C}.')['colored'])
        self.assertEqual(MANA.parse_production('{T}: Add one mana of any color. Spend this mana only to cast creature spells.')['restriction'], 'only to cast creature spells')

    def test_tap_cost_vs_tap_effect(self):
        self.assertEqual(K.cost_component('{T}', 'X')['subject'], 'this')
        t = K.cost_component('Tap an untapped creature you control', 'X')
        self.assertEqual((t['family'], t['subject'], t['object_filter']), ('tap', 'other', 'creature'))
        s = K.cost_component('Sacrifice another creature', 'X')
        self.assertTrue(s['must_come_from_other_unit']); self.assertIn('permanent.dies', s['on_payment'])
        r = K.result_of([], 'When this creature enters, tap target creature an opponent controls.', 'X', '', '')
        self.assertEqual([p['id'] for p in r['produces']], ['permanent.tap'])

    def test_hook_qualifiers(self):
        h = K.hook_object('you sacrifice a creature', 'permanent.sacrifice', 'Dina, Essence Brewer')
        self.assertEqual((h['id'], h['qualifiers']['actor'], h['qualifiers']['object_filter']), ('permanent.sacrifice', 'you', 'creature'))
        h = K.hook_object('a player taps a land for mana', '', 'Manabarbs')
        self.assertEqual((h['id'], h['qualifiers']['source_event'], h['qualifiers']['source_filter'], h['qualifiers']['actor']),
                         ('permanent.tapped_for_mana', 'tapped_for_mana', 'land', 'any_player'))
        self.assertEqual(K.hook_object('one or more creatures you control die', 'permanent.dies', 'X')['qualifiers']['cardinality'], 'one_or_more')
        self.assertEqual(K.hook_object('this creature enters', 'permanent.dies', 'X')['id'], 'battlefield.enter')

    def test_every_mana_output_typed(self):
        c = ro()
        self.assertLessEqual(c.execute("select count(*) from validation_checks where check_id='C14_mana_typed' and result='fail'").fetchone()[0], 2)


class Refresh(unittest.TestCase):
    def test_snapshot_replay_opens_qa_and_keeps_cards(self):
        with Scratch() as s:
            names = ['The Necrobloom', 'Avenger of Zendikar', 'Cultivate']
            texts = {n: s.con.execute('select oracle_text from cards where card_name=?', (n,)).fetchone()[0] for n in names}
            fixture = [{'name': names[0], 'oracle_id': 'fixture-0', 'layout': 'normal', 'oracle_text': texts[names[0]], 'legalities': {'commander': 'legal'}},
                       {'name': names[1], 'oracle_id': 'fixture-1', 'layout': 'normal', 'oracle_text': texts[names[1]] + ' (changed)', 'legalities': {'commander': 'legal'}}]
            fx = s.dir / 'fixture.json'; fx.write_text(json.dumps(fixture))
            p, head = O.snapshot(s.db, fx, s.dir / 'refresh')
            self.assertEqual(head['discrepancies'], 1)
            O.replay(s.con, s.dir / 'refresh')
            # scope to this run: the built DB already carries QA items from real refresh snapshots
            self.assertEqual(s.con.execute("select count(*) from qa_queue where issue_type='oracle_text_discrepancy' and json_extract(details_json,'$.run_id')=?",
                                           (head['run_id'],)).fetchone()[0], 1)
            self.assertEqual(s.con.execute('select oracle_text from cards where card_name=?', (names[1],)).fetchone()[0], texts[names[1]])
            self.assertEqual(s.con.execute('select oracle_id from card_identity where card_name=?', (names[0],)).fetchone()[0], 'fixture-0')
            with self.assertRaises(FileExistsError):  # snapshots are immutable
                open(p, 'x')


class Policy(unittest.TestCase):
    def test_archive_inputs_refused(self):
        for p in ['MTG Master Inventory — Canonical_20261015-1842Z_ARCHIVE.xlsx', 'drive/archive/export.xlsx']:
            with self.assertRaises(SystemExit): Z.guard_input(p)
            with self.assertRaises(SystemExit): M.archive_guard(p)
        self.assertEqual(Z.guard_input('MTG Master Inventory — Canonical.xlsx')['archive_guard'], 'ok')

    def test_queries_are_read_only(self):
        c = kbq.connect(DB)
        with self.assertRaises(sqlite3.OperationalError): c.execute("update cards set free=0")
        self.assertTrue(kbq.card(c, 'The Necrobloom')['contracts'])
        self.assertEqual(len(kbq.destinations(c, 'Avenger of Zendikar')['destinations']), 13)


if __name__ == '__main__':
    unittest.main()
