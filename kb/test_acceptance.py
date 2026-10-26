"""Acceptance tests T1-T8 (Kate's review of KB v0.2, 2026-10-21; scope relayed 2026-10-22).

  python -m unittest -v test_acceptance.py          (needs mtg_cards_v0.2.sqlite; no hash-seed pinning)
  KB_SKIP_REBUILD=1 python -m unittest ...          (skips the ~20 s deterministic-rebuild check in T7)

T1 Oracle identity       T2 mana payability        T3 tap and tapped-for-mana events
T4 sacrifice hooks       T5 consequences            T6 review gate
T7 reproducibility       T8 discovery
"""
import hashlib, json, os, shutil, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'vendor'))
DB = HERE / 'mtg_cards_v0.2.sqlite'
import kbfacts as F, contracts as K, mana as MANA, events as EV, scenarios as SC, review as R, oracle_refresh as O, kbq, deck_audit
import test_v02 as T   # Scratch, LOSSLESS, LOSSY

OFFSPRING = ['Finch Formation', 'Rust-Shield Rampager', 'Thornplate Intimidator']


def ro():
    c = sqlite3.connect(DB.resolve().as_uri() + '?mode=ro', uri=True); c.row_factory = sqlite3.Row; return c


def contract(c, cid):
    return F.loads(c.execute('select contract_json from current_contracts where contract_id=?', (cid,)).fetchone()[0])


def hook(c, cid):
    return contract(c, cid)['initiation']['requirement_groups'][0]['alternatives'][0]


def obj(types, controller='you', token=False, observer=False, subtypes=()):
    return {'types': list(types), 'subtypes': list(subtypes), 'controller': controller, 'token': token, 'is_observer': observer}


class T1_OracleIdentity(unittest.TestCase):
    def test_tokens_jumpstart_and_joke_cards_never_override_a_real_printing(self):
        with T.Scratch() as s:
            text = s.con.execute("select oracle_text from cards where card_name='Cultivate'").fetchone()[0]
            same = {'name': 'Cultivate', 'oracle_text': 'not the card'}
            fixture = [dict(same, oracle_id='token', layout='token', legalities={}),
                       dict(same, oracle_id='art', layout='art_series', legalities={}),
                       dict(same, oracle_id='jumpstart', layout='front_card', legalities={'commander': 'not_legal'}),
                       dict(same, oracle_id='joke', layout='normal', set_type='funny', legalities={'commander': 'not_legal'}),
                       {'name': 'Cultivate', 'oracle_id': 'real', 'layout': 'normal', 'oracle_text': text, 'legalities': {'commander': 'legal'}}]
            fx = s.dir / 'bulk.json'; fx.write_text(json.dumps(fixture))
            p, _ = O.snapshot(s.db, fx, s.dir / 'refresh')
            row = next(json.loads(l) for l in p.read_text().splitlines()[1:] if json.loads(l)['card_name'] == 'Cultivate')
            self.assertEqual((row['oracle_id'], row['match_status']), ('real', 'identical'))

    def test_identity_layer(self):
        c = ro()
        self.assertEqual(c.execute('select count(*) from card_identity where oracle_id is not null').fetchone()[0], 3519)
        rt = {r['card_name']: r for r in c.execute('select * from rules_text')}
        self.assertEqual(rt['Elemental']['authority'], 'excluded (token_not_card)'); self.assertFalse(rt['Elemental']['identity_confirmed'])
        self.assertEqual(rt['Counters']['evaluator_reads'], 'excluded'); self.assertFalse(rt['Counters']['identity_confirmed'])  # matched the {B} front card
        self.assertEqual(rt['______']['evaluator_reads'], 'excluded')
        for n in ['Dunedain Blade', 'Gideon the Oathsworn', "Sandbender's Storm"]:
            self.assertTrue(rt[n]['identity_confirmed'], n); self.assertEqual(rt[n]['evaluator_reads'], 'sheet')
        for n in OFFSPRING: self.assertFalse(rt[n]['identity_confirmed'], n)  # Sheet row points at the token printing (tblb)

    def test_sheet_is_never_edited(self):
        v1 = sqlite3.connect((HERE / 'mtg_cards.sqlite').resolve().as_uri() + '?mode=ro', uri=True)
        a = v1.execute('select card_name,oracle_text,type_line,raw_json from cards order by card_name').fetchall()
        b = ro().execute('select card_name,oracle_text,type_line,raw_json from cards order by card_name').fetchall()
        self.assertEqual(a, [tuple(x) for x in b])


class T2_ManaPayability(unittest.TestCase):
    def test_pips(self):
        P = MANA.pool
        self.assertFalse(MANA.can_pay('{1}{C}', P('WW')))
        self.assertTrue(MANA.can_pay('{1}{C}', P('WC')))
        self.assertTrue(MANA.can_pay('{2}', P('WW'))); self.assertTrue(MANA.can_pay('{2}', P('WC'))); self.assertTrue(MANA.can_pay('{2}', P('CC')))
        self.assertFalse(MANA.can_pay('{C}', P('G')))
        self.assertTrue(MANA.can_pay('{G/W}{G}', P('WG'))); self.assertFalse(MANA.can_pay('{G/W}{G}', P('WW')))
        self.assertTrue(MANA.can_pay('{2/B}', P('CC'))); self.assertTrue(MANA.can_pay('{2/B}', P('B')))
        self.assertTrue(MANA.can_pay('{W/P}', [], life=2)); self.assertFalse(MANA.can_pay('{W/P}', [], life=1))
        self.assertFalse(MANA.can_pay('{S}', P('G'))); self.assertTrue(MANA.can_pay('{S}', P('G', snow=True)))
        self.assertTrue(MANA.can_pay('{X}{R}', P('RRR'), x=2)); self.assertFalse(MANA.can_pay('{X}{R}', P('RR'), x=2))

    def test_production_from_contracts(self):
        c = ro()
        pools = lambda cid: [sorted(u['type'] for u in p) for m in [x['mana'] for x in contract(c, cid)['result']['produces'] if x['id'] == 'mana.add']
                             for p in MANA.production_pools(m)]
        self.assertEqual(pools('card.Orzhov%20Basilica.op003'), [['B', 'W']])            # exactly {W}{B}, never "2 mana"
        self.assertEqual(pools('card.Crystal%20Grotto.op002'), [['C']])
        druid = pools('card.Great%20Forest%20Druid.op001')
        self.assertEqual(sorted(druid), [['B'], ['G'], ['R'], ['U'], ['W']])
        self.assertFalse(any(MANA.can_pay('{C}', MANA.pool(p)) for p in druid))       # any colour can't pay {C}
        self.assertTrue(MANA.can_pay('{C}', MANA.pool(pools('card.Crystal%20Grotto.op002')[0])))
        self.assertIn('C', {u['type'] for p in MANA.production_pools({'mode': 'any_type', 'amount': 1}) for u in p})  # any type may be colourless


class T3_TapEvents(unittest.TestCase):
    def tap(self, reason, produced=(), has_tap=True, types=('creature',)):
        return {'id': 'permanent.tap', 'actor': 'you', 'object': obj(types), 'reason': reason, 'produced': list(produced),
                'mana_ability_cost_has_tap': has_tap}

    def test_tapped_for_mana_facet(self):
        facet = lambda e: [x['id'] for x in EV.derive_facets([e])].count('permanent.tapped_for_mana')
        self.assertEqual(facet(self.tap('mana_ability', ['G'])), 1)
        for r in ('crew', 'station', 'cost', 'effect'): self.assertEqual(facet(self.tap(r)), 0, r)
        self.assertEqual(facet(self.tap('mana_ability', [], True)), 0)              # produced no mana
        self.assertEqual(facet(self.tap('mana_ability', ['G'], False)), 0)          # mana ability without {T} in its cost

    def test_hooks_on_real_contracts(self):
        c = ro()
        cub = hook(c, 'card.Badgermole%20Cub.op003')                                    # "Whenever you tap a creature for mana"
        self.assertEqual(cub['id'], 'permanent.tapped_for_mana')
        self.assertEqual(EV.trigger_count(cub, [self.tap('mana_ability', ['G'])]), 1)
        self.assertEqual(EV.trigger_count(cub, [self.tap('crew'), self.tap('station')]), 0)
        self.assertEqual(EV.trigger_count(cub, [self.tap('mana_ability', ['G'], types=('land',))]), 0)
        barbs = hook(c, 'card.Manabarbs.op001')                                          # "a player taps a land for mana"
        opp = dict(self.tap('mana_ability', ['R'], types=('land',)), actor='opponent'); opp['object'] = obj(['land'], 'opponent')
        self.assertEqual(EV.trigger_count(barbs, [opp]), 1)

    def test_effect_taps_are_not_costs(self):
        c = ro()
        seal = contract(c, 'card.Tiger-Seal.op002')
        self.assertFalse([g for g in seal['initiation']['requirement_groups'] if g['class'] == 'cost'])
        self.assertIn('effect', [p.get('as') for p in seal['result']['produces'] if p['id'] == 'permanent.tap'])
        bas = contract(c, 'card.Orzhov%20Basilica.op003')
        cost = [g['alternatives'][0] for g in bas['initiation']['requirement_groups'] if g['class'] == 'cost']
        self.assertEqual([(x['family'], x['subject'], x['act_time']) for x in cost], [('tap', 'this', 'paid_as_cost')])


class T4_Sacrifice(unittest.TestCase):
    def sac(self, types, actor='you', batch=0, controller=None, token=False, observer=False):
        return {'id': 'permanent.sacrifice', 'actor': actor, 'batch': batch, 'object': obj(types, controller or actor, token, observer)}

    def test_each_object_vs_one_or_more(self):
        c = ro()
        dina = hook(c, 'card.Dina%2C%20Essence%20Brewer.op001')                       # "Whenever you sacrifice a creature"
        three = [self.sac(['creature']) for _ in range(3)]
        self.assertEqual(dina['qualifiers']['cardinality'], 'each_object')
        self.assertEqual(EV.trigger_count(dina, three), 3)
        batch = K.hook_object('you sacrifice one or more creatures', 'permanent.sacrifice', 'Test Card')
        self.assertEqual((batch['qualifiers']['cardinality'], batch['qualifiers']['simultaneity_group']), ('one_or_more', 'per_event_batch'))
        self.assertEqual(EV.trigger_count(batch, three), 1)
        self.assertEqual(EV.trigger_count(batch, three + [self.sac(['creature'], batch=1)]), 2)

    def test_actor_and_controller_relations(self):
        c = ro()
        dina = hook(c, 'card.Dina%2C%20Essence%20Brewer.op001')
        q = dina['qualifiers']
        self.assertEqual((q['actor'], q['relation_to_observer'], q['permanent_controller_at_event']), ('you', 'observer_controller', 'same_as_actor'))
        self.assertEqual(EV.trigger_count(dina, [self.sac(['creature'], actor='opponent')]), 0)
        self.assertEqual(EV.trigger_count(dina, [self.sac(['artifact'])]), 0)
        maz = hook(c, 'card.Mazirek%2C%20Kraul%20Death%20Priest.op002')               # "a player sacrifices another permanent"
        self.assertEqual(maz['qualifiers']['actor'], 'any_player')
        self.assertEqual(EV.trigger_count(maz, [self.sac(['artifact'], actor='opponent')]), 1)
        self.assertEqual(EV.trigger_count(maz, [self.sac(['creature'], observer=True)]), 0)  # "another"
        ash = hook(c, 'card.Ashling%2C%20the%20Limitless.op002')                         # "a nontoken Elemental"
        elemental = lambda token: {'id': 'permanent.sacrifice', 'actor': 'you', 'object': obj(['creature'], subtypes=['elemental'], token=token)}
        self.assertEqual(EV.trigger_count(ash, [elemental(True)]), 0)
        self.assertEqual(EV.trigger_count(ash, [elemental(False)]), 1)

    def test_paid_sacrifice_is_observable_before_resolution(self):
        c = ro()
        cost = contract(c, 'card.Dina%2C%20Essence%20Brewer.op002')                   # "{2}, {T}, Sacrifice another creature: ..."
        pay = EV.payment_events(cost)
        sac = [e for e in pay if e['id'] == 'permanent.sacrifice']
        self.assertEqual([(e['checkpoint'], e['act_time']) for e in sac], [('payment', 'paid_as_cost')])
        self.assertIn('permanent.dies', [e['id'] for e in pay])
        self.assertEqual(EV.trigger_count(hook(c, 'card.Dina%2C%20Essence%20Brewer.op001'), pay), 1)


class T5_Consequences(unittest.TestCase):
    def test_contracts_record_the_consequences(self):
        c = ro()
        cult = contract(c, 'card.Cultivate.op001')
        self.assertEqual(sorted((t['from'], t['to']) for t in cult['result']['transitions'] if 'from' in t), [('library', 'battlefield'), ('library', 'hand')])
        self.assertTrue(next(t for t in cult['result']['transitions'] if t.get('to') == 'battlefield')['tapped'])
        av = contract(c, 'card.Avenger%20of%20Zendikar.op001')
        self.assertEqual([a['measures'] for a in av['initiation']['amplifiers']], ['land you control'])
        self.assertEqual(json.loads(c.execute("select proposed_action_json from operation_contracts where contract_id='card.Avenger%20of%20Zendikar.op001'").fetchone()[0])
                         ['outputs'][0][1]['subtypes'], ['plant'])
        self.assertIn('counter.put', [p['id'] for p in contract(c, 'card.Avenger%20of%20Zendikar.op002')['result']['produces']])
        cre = contract(c, 'card.Cremate.op001')
        self.assertEqual([(t['from'], t['to']) for t in cre['result']['transitions']], [('graveyard', 'exile')])
        self.assertTrue([g for g in cre['initiation']['requirement_groups'] if g['class'] == 'eligibility'])

    def test_none_is_runtime_certifiable(self):
        c = ro()
        want = {'card.Cultivate.op001': 'zone_transition_lost', 'card.Avenger%20of%20Zendikar.op001': 'amplifier_lost',
                'card.Avenger%20of%20Zendikar.op002': 'distribution_lost', 'card.Cremate.op001': 'target_lost',
                'card.The%20Necrobloom.op001': 'branch_unbound', 'card.Orzhov%20Basilica.op003': 'mana_type_lost'}
        for cid, loss in want.items():
            v = c.execute('select runtime_compilation_complete,mechanically_supported from contract_verification where contract_id=?', (cid,)).fetchone()
            self.assertEqual(tuple(v), (0, 0), cid)
            self.assertIn(loss, [r[0] for r in c.execute('select loss_code from compile_losses where contract_id=?', (cid,))], cid)
        self.assertEqual(c.execute("select count(*) from compile_losses where contract_id='card.Cremate.op001' and detail like 'exile.enter%'").fetchone()[0], 1)

    @unittest.expectedFailure
    def test_necrobloom_seven_names_branch_is_bound(self):
        """Known gap: the 'instead' replacement branch is not bound to DIO process branches yet."""
        self.assertEqual(contract(ro(), 'card.The%20Necrobloom.op001')['unbound'], [])

    @unittest.expectedFailure
    def test_necrobloom_dredge_grant_is_bound(self):
        """Known gap: 'Land cards in your graveyard have dredge 2' is a granted replacement; macro.dredge@1 is not expanded yet."""
        c = ro()
        self.assertEqual(c.execute("select count(*) from compile_losses where contract_id='card.The%20Necrobloom.op002'").fetchone()[0], 0)


class T6_ReviewGate(unittest.TestCase):
    def test_placeholders_and_unknown_tests_are_refused(self):
        with T.Scratch() as s:
            for bad in (['scenario:<name>'], ['<name>'], ['scenario:test'], ['no.such.scenario'], ['orzhov_basilica.tap_adds_wb']):
                with self.assertRaises(ValueError, msg=bad): s.review(T.LOSSLESS, tests=bad)

    def test_failing_scenario_is_refused(self):
        with T.Scratch() as s:
            reg = SC.load(); bad = dict(reg['cremate.draw'], id='cremate.draw_wrong', semantic=[{'op': 'transitions', 'expect': [['library', 'graveyard']]}])
            reg['cremate.draw_wrong'] = bad
            with self.assertRaises(ValueError): s.review(T.LOSSLESS, tests=['cremate.draw_wrong'], registry=reg)

    def test_quarantined_and_runtime_scope_refused(self):
        with T.Scratch() as s:
            kite = s.con.execute("select contract_id from validation_queue where card_name=\"Medic's Kitesail\"").fetchone()[0]
            self.assertEqual(s.con.execute('select queue_state from validation_queue where contract_id=?', (kite,)).fetchone()[0], 'quarantined')
            reg = dict(SC.load(), **{'kite.any': {'id': 'kite.any', 'contract_id': kite, 'scenario_sha256': 'x', 'semantic': [{'op': 'no_hook', 'id': 'x'}]}})
            with self.assertRaises(ValueError): s.review(kite, tests=['kite.any'], registry=reg)
            with self.assertRaises(ValueError): s.review(T.LOSSLESS, scope='runtime')
            with self.assertRaises(ValueError): s.review(T.LOSSLESS, rules_text_sha256='0' * 64)

    def test_real_scenario_passes_and_is_recorded(self):
        with T.Scratch() as s:
            rec = s.review(T.LOSSLESS)
            self.assertEqual([t['scenario'] for t in rec['test_results']], ['cremate.draw'])
            self.assertEqual(R.read_overlay(s.overlay)[0]['scope'], 'semantic')

    def test_review_packets_have_no_placeholders(self):
        c = ro()
        for deck in ('Necrobloom', 'Dina'):
            self.assertNotIn('<name>', deck_audit.packet(c, deck)); self.assertNotIn('scenario:', deck_audit.packet(c, deck))

    def test_runtime_certificates_are_separate_from_review(self):
        c = ro()
        v = c.execute('select * from contract_verification where contract_id=?', (T.LOSSLESS,)).fetchone()
        self.assertEqual((v['runtime_compilation_complete'], v['runtime_scenario_tested'], v['semantic_contract_reviewed'], v['mechanically_supported']), (1, 1, 0, 0))
        self.assertEqual(c.execute('select issued_by from runtime_certifications where contract_id=?', (T.LOSSLESS,)).fetchone()[0], SC.SCENARIO_VERSION)
        self.assertEqual(c.execute('select count(*) from review_overlay').fetchone()[0], 0)


class T7_Reproducibility(unittest.TestCase):
    def test_manifest(self):
        m = HERE / 'MANIFEST.sha256'
        if not m.exists(): self.skipTest('MANIFEST.sha256 is written by release.py into the release folder')
        for line in m.read_text().splitlines():
            digest, name = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((HERE / name).read_bytes()).hexdigest(), digest, name)
        src = json.loads((HERE / 'SOURCE_MANIFEST.json').read_text())
        meta = dict(ro().execute('select key,value from meta'))
        self.assertEqual(src['oracle_refresh']['run_id'], meta['oracle_run_id'])
        self.assertEqual(src['database']['sha256'], hashlib.sha256(DB.read_bytes()).hexdigest())
        self.assertEqual(src['inventory_source']['input_sha256'], meta['input_sha256'])

    def test_oracle_coverage_and_counts(self):
        c = ro()
        self.assertEqual(c.execute("select count(*) from rules_text where authority='oracle_refresh'").fetchone()[0], 3517)
        self.assertEqual(c.execute('select count(*) from operation_contracts').fetchone()[0], 4961)
        self.assertEqual(c.execute('select count(*) from contract_verification').fetchone()[0], 4961)

    @unittest.skipIf(os.environ.get('KB_SKIP_REBUILD'), 'KB_SKIP_REBUILD set')
    def test_rebuild_is_byte_identical_under_another_hash_seed(self):
        meta = dict(ro().execute('select key,value from meta'))
        built = meta['v02_built_utc']
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'rebuilt.sqlite'
            env = dict(os.environ, PYTHONHASHSEED='12345')
            subprocess.run([sys.executable, str(HERE / 'migrate_v02.py'), '--v01', str(HERE / 'mtg_cards.sqlite'), '--out', str(out),
                            '--overlay', str(HERE / 'overrides' / 'review_overlay.jsonl'), '--refresh-dir', str(HERE / 'refresh'),
                            '--source-modified', ro().execute("select source_modified_utc from import_runs").fetchone()[0], '--built-utc', built],
                           check=True, env=env, capture_output=True, cwd=d)
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), hashlib.sha256(DB.read_bytes()).hexdigest())


class T8_Discovery(unittest.TestCase):
    def test_necrobloom(self):
        c = kbq.connect(DB)
        r = kbq.card(c, 'The Necrobloom')
        self.assertEqual(len(r['contracts']), len(r['verification']))
        self.assertEqual(r['rules_text']['authority'], 'oracle_refresh')
        self.assertTrue(kbq.theme(c, 'landfall', deck='Necrobloom'))
        self.assertTrue(kbq.theme(c, 'repeatable_recursion', deck='Necrobloom'))

    def test_owned_legal_offspring(self):
        c = kbq.connect(DB)
        hits = {r['card']: r for r in kbq.keyword(c, 'Offspring', ci='WUBRG')}
        for n in OFFSPRING:
            self.assertIn(n, hits); self.assertTrue(hits[n]['commander_legal']); self.assertEqual(hits[n]['evaluator_reads'], 'oracle')
        self.assertNotIn('Elemental', {r['card'] for r in kbq.keyword(c, 'Whenever', ci='WUBRG')})

    def test_mana_choices(self):
        c = kbq.connect(DB)
        colorless = kbq.mana_sources(c, pays='{C}', limit=5000)
        self.assertTrue(colorless)
        self.assertTrue(all('C' in r['can_add'] for r in colorless))
        self.assertNotIn('Great Forest Druid', {r['card'] for r in colorless})
        self.assertIn('Orzhov Basilica', {r['card'] for r in kbq.mana_sources(c, pays='{W}{B}', limit=5000)})

    def test_evaluator_sees_restored_cards_and_not_excluded_rows(self):
        from bridge_v02 import open_evaluator
        ev = open_evaluator(DB, games=5, engine_games=1, strict=True)
        for n in OFFSPRING: self.assertIn(n, ev.inv.cards); self.assertIn('Offspring', ev.inv.cards[n]['Oracle Text'])
        for n in ('Elemental', 'Counters', '______'): self.assertNotIn(n, ev.inv.cards)
        self.assertIn('Equip {2}', ev.inv.cards["Medic's Kitesail"]['Oracle Text'])
        self.assertEqual(ev.facts.stats['misses'], {})


if __name__ == '__main__':
    unittest.main()
