"""kb/contract_roles.py: the evaluator's roles are read from KB contracts, not only cited (C-012).

The fixture tests need no release DB. The last test runs against the pinned KB if it is installed.
"""
import json, sqlite3, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'kb'), str(ROOT / 'kb' / 'vendor')]
import contract_roles as R

DB = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'


def fixture(contracts, states=None, old_versions=None):
    """A throwaway KB: {card: {contract_id: [feeds]}} as current contracts (version 2), each with a
    validation_queue state (default ready_for_review). old_versions: {contract_id: [feeds]} at version 1."""
    con = sqlite3.connect(':memory:')
    con.execute('create table operation_contracts (contract_id text, contract_version int, card_name text, contract_json text)')
    con.execute('create table validation_queue (contract_id text, contract_version int, queue_state text)')
    con.execute('create view current_contracts as select c.* from operation_contracts c where contract_version='
                '(select max(contract_version) from operation_contracts x where x.contract_id=c.contract_id)')
    for card, cs in contracts.items():
        for cid, feeds in cs.items():
            con.execute('insert into operation_contracts values (?,2,?,?)', (cid, card, json.dumps({'query_index': {'feeds': feeds}})))
            con.execute('insert into validation_queue values (?,2,?)', (cid, (states or {}).get(cid, 'ready_for_review')))
            if cid in (old_versions or {}):
                con.execute('insert into operation_contracts values (?,1,?,?)', (cid, card, json.dumps({'query_index': {'feeds': old_versions[cid]}})))
    return con


class FakeInventory:
    def __init__(self, con, pattern):
        self.db, self._pattern, self._rec = con, pattern, {}
    def record(self, name):
        return self._pattern.get(name, {})
    def supported(self, name):
        return {f for f, v in self.record(name).items() if v['status'] == 'supported'}


PATTERN = {'Test Card': {'draw': {'status': 'supported', 'evidence': {'oracle': 'draw a card'}},
                         'creature': {'status': 'supported', 'evidence': {'oracle': 'type line'}}}}


class ConsumptionNotCitation(unittest.TestCase):
    def test_changing_the_contract_changes_the_role(self):
        inv = R.install(FakeInventory(fixture({'Test Card': {'c.op1': ['card.draw']}}), PATTERN))
        self.assertIn('draw', inv.supported('Test Card'))
        self.assertNotIn('ramp', inv.supported('Test Card'))
        # same card, same pattern reading; only the contract changes
        inv = R.install(FakeInventory(fixture({'Test Card': {'c.op1': ['mana.add']}}), PATTERN))
        self.assertNotIn('draw', inv.supported('Test Card'))
        self.assertIn('ramp', inv.supported('Test Card'))
        self.assertEqual(inv.record('Test Card')['draw']['status'], 'not_in_contract')
        self.assertEqual(inv.record('Test Card')['ramp']['evidence']['contracts'], ['c.op1'])

    def test_changing_the_role_map_changes_the_role(self):
        con = fixture({'Test Card': {'c.op1': ['card.draw']}})
        g = R.grounded_record(PATTERN['Test Card'], R.contract_feeds(con, 'Test Card'), role_map={'draw': ['card.search']})
        self.assertEqual(g['draw']['status'], 'not_in_contract')

    def test_no_contract_gives_a_labelled_fallback(self):
        inv = R.install(FakeInventory(fixture({}), PATTERN))
        rec = inv.record('Test Card')
        self.assertIn('draw', inv.supported('Test Card'))     # pattern kept...
        for v in rec.values():                                 # ...but never silently
            self.assertEqual(v['evidence']['basis'], 'text_pattern_fallback')
            self.assertEqual(v['evidence']['fallback_reason'], 'no KB contract for this card')

    def test_unmapped_role_is_labelled_fallback(self):
        g = R.grounded_record(PATTERN['Test Card'], {'c.op1': ['card.draw']})
        self.assertEqual(g['creature']['evidence']['basis'], 'text_pattern_fallback')
        self.assertIn('ROLE_MAP', g['creature']['evidence']['fallback_reason'])

    def test_every_role_has_a_basis_and_nothing_is_verified(self):
        g = R.grounded_record(PATTERN['Test Card'], {'c.op1': ['card.draw', 'token.create']})
        for role, v in g.items():
            self.assertIn(v['evidence']['basis'], ('dio_contract', 'text_pattern_fallback', 'human_label'), role)
            self.assertNotEqual(v['evidence'].get('verification_state'), 'verified')

    def test_human_label_outranks_the_contract(self):
        pat = {'token_maker': {'status': 'contradicted', 'evidence': {'label': False, 'oracle': 'create'}}}
        g = R.grounded_record(pat, {'c.op1': ['token.create']})
        self.assertEqual(g['token_maker']['status'], 'contradicted')
        self.assertEqual(g['token_maker']['evidence']['basis'], 'human_label')
        self.assertEqual(g['token_maker']['evidence']['contract_says'], 'supported')

    def test_role_map_events_are_in_the_kb_event_vocabulary(self):
        known = {'card.draw', 'mana.add', 'land_to_battlefield', 'spell.countered', 'token.create', 'counter.put', 'life.gain'}
        self.assertTrue({e.split(':')[0] for es in R.ROLE_MAP.values() for e in es} <= known)


class LandsAreNotRamp(unittest.TestCase):
    """Codex review on #42: a land's own mana is mana base, not ramp (mtg_eval semantics)."""
    def test_land_mana_is_not_ramp(self):
        g = R.grounded_record({'land': {'status': 'supported', 'evidence': {'oracle': 'type line'}}},
                              {'c.op1': ['mana.add']}, type_line='Land')
        self.assertNotIn('ramp', g)

    def test_land_that_puts_lands_onto_the_battlefield_is_ramp(self):
        g = R.grounded_record({}, {'c.op1': ['mana.add', 'land_to_battlefield']}, type_line='Land')
        self.assertEqual(g['ramp']['status'], 'supported')

    def test_nonland_mana_is_ramp(self):
        g = R.grounded_record({}, {'c.op1': ['mana.add']}, type_line='Artifact')
        self.assertEqual(g['ramp']['status'], 'supported')


class EffectiveContractState(unittest.TestCase):
    """Codex review on #42: respect current versions and review/quarantine decisions."""
    def test_rejected_contract_is_not_read(self):
        con = fixture({'Test Card': {'c.op1': ['card.draw'], 'c.op2': ['mana.add']}}, states={'c.op2': 'rejected'})
        inv = R.install(FakeInventory(con, PATTERN))
        self.assertNotIn('ramp', inv.supported('Test Card'))
        self.assertEqual(inv.record('Test Card')['draw']['evidence']['excluded_contracts'], ['c.op2'])

    def test_all_quarantined_falls_back_with_reason(self):
        con = fixture({'Test Card': {'c.op1': ['mana.add']}}, states={'c.op1': 'quarantined'})
        rec = R.install(FakeInventory(con, PATTERN)).record('Test Card')
        self.assertEqual(rec['draw']['status'], 'supported')
        self.assertEqual(rec['draw']['evidence']['basis'], 'text_pattern_fallback')
        self.assertEqual(rec['draw']['evidence']['fallback_reason'], 'all KB contracts rejected or quarantined')
        self.assertNotIn('ramp', rec)

    def test_only_the_current_version_is_read(self):
        con = fixture({'Test Card': {'c.op1': ['card.draw']}}, old_versions={'c.op1': ['mana.add']})
        self.assertEqual(R.contract_feeds(con, 'Test Card'), {'c.op1': ['card.draw']})

    def test_verification_state_is_carried_not_assumed(self):
        con = fixture({'Test Card': {'c.op1': ['card.draw']}}, states={'c.op1': 'semantic_reviewed'})
        ev = R.install(FakeInventory(con, PATTERN)).record('Test Card')['draw']['evidence']
        self.assertEqual(ev['verification_state'], 'candidate')   # ROLE_MAP is unreviewed: a reviewed contract doesn't promote the role
        self.assertEqual(ev['contract_states'], {'c.op1': 'semantic_reviewed'})
        con = fixture({'Test Card': {'c.op1': ['card.draw']}}, states={'c.op1': 'blocked'})
        ev = R.install(FakeInventory(con, PATTERN)).record('Test Card')['draw']['evidence']
        self.assertEqual(ev['verification_state'], 'candidate')
        self.assertEqual(ev['contract_states'], {'c.op1': 'blocked'})


class CopilotReviewFindings(unittest.TestCase):
    """Copilot review on #42."""
    def test_false_label_without_pattern_hit_blocks_the_contract_role(self):
        g = R.grounded_record({}, {'c.op1': ['token.create']}, labels={'token_maker': False})
        self.assertEqual(g['token_maker']['status'], 'contradicted')
        self.assertEqual(g['token_maker']['evidence']['basis'], 'human_label')
        self.assertEqual(g['token_maker']['evidence']['contract_says'], 'supported')

    def test_tag_only_without_contract_hit_stays_uncertain(self):
        g = R.grounded_record({'draw': {'status': 'tag_only', 'evidence': {'tag': True}}}, {'c.op1': ['mana.add']})
        self.assertEqual(g['draw']['status'], 'tag_only')
        self.assertEqual(g['draw']['evidence']['contract_says'], 'not_in_contract')

    def test_label_basis_survives_the_no_contract_path(self):
        g = R.grounded_record({'wipe': {'status': 'supported', 'evidence': {'label': True, 'oracle': 'destroy all'}}}, {})
        self.assertEqual(g['wipe']['evidence']['basis'], 'human_label')
        self.assertNotIn('fallback_reason', g['wipe']['evidence'])

    def test_role_dependent_reports_carry_role_source(self):
        class FakeEv:
            def __init__(self):
                self.inv = R.install(FakeInventory(fixture({}), PATTERN), labels_for=lambda n: {})
            def deck(self, name, games=None):
                return {'title': f'Deck: {name}', 'limitations': [], 'data': {}, 'sections': []}
        res = R.wrap_reports(FakeEv()).deck('Test')
        self.assertTrue(any('candidate' in x for x in res['limitations']))
        self.assertEqual(res['data']['role_source']['map_version'], R.MAP_VERSION)


class CopilotSecondReview(unittest.TestCase):
    """Copilot review on #42 (second pass)."""
    def test_false_label_without_any_evidence_records_nothing(self):
        self.assertNotIn('token_maker', R.grounded_record({}, {'c.op1': ['card.draw']}, labels={'token_maker': False}))
        self.assertNotIn('wipe', R.grounded_record({}, {}, labels={'wipe': False}))

    def test_contract_evidence_keeps_the_tag(self):
        g = R.grounded_record({'draw': {'status': 'tag_only', 'evidence': {'tag': True}}}, {'c.op1': ['mana.add']})
        self.assertTrue(g['draw']['evidence']['tag'])
        self.assertEqual(g['draw']['evidence']['basis'], 'dio_contract')
        g = R.grounded_record({'draw': {'status': 'supported', 'evidence': {'tag': True, 'oracle': 'draw a card'}}}, {'c.op1': ['card.draw']})
        self.assertEqual(g['draw']['evidence']['oracle'], 'draw a card')


class CounterKinds(unittest.TestCase):
    """Codex review on #42: counter_source means +1/+1 counters or proliferate, not any counter."""
    def put(self, **kw):
        return {'result': {'produces': [dict({'id': 'counter.put'}, **kw)]}}

    def test_charge_counters_are_not_a_counter_source(self):
        q = R.counter_qualifiers(self.put(counter_kinds=['charge']), ['counter.put'])
        self.assertEqual(q, [])
        self.assertNotIn('counter_source', R.grounded_record({}, {'c.op1': ['counter.put'] + q}))

    def test_plus_one_counters_and_proliferate_are(self):
        self.assertEqual(R.counter_qualifiers(self.put(counter_kinds=['+1/+1']), ['counter.put']), ['counter.put:+1/+1'])
        q = R.counter_qualifiers(self.put(counter_kinds=['present_kinds'], mode='proliferate'), ['counter.put'])
        self.assertEqual(q, ['counter.put:proliferate'])
        self.assertEqual(R.grounded_record({}, {'c.op1': ['counter.put'] + q})['counter_source']['status'], 'supported')

    def test_no_qualifier_when_feeds_dropped_counter_put(self):
        # kb/contracts.py feeds() drops counter.put when it is only a condition (C-015)
        self.assertEqual(R.counter_qualifiers(self.put(counter_kinds=['+1/+1']), []), [])


class CardResultShowsBasis(unittest.TestCase):
    """Codex review on #42: Evaluator.card() must show the basis, not drop it."""
    def test_capability_table_gains_basis_columns(self):
        class FakeEv:
            def __init__(self):
                self.inv = R.install(FakeInventory(fixture({'Test Card': {'c.op1': ['mana.add']}}), PATTERN))
            def card(self, name, deck=None):
                return {'title': f'Card: {name}', 'limitations': [], 'sections': [(R.CAPABILITY_SECTION,
                        [{'function': f, 'status': v['status']} for f, v in sorted(self.inv.record(name).items())])]}
        ev = R.wrap_card(FakeEv())
        rows = {r['function']: r for r in ev.card('Test Card')['sections'][0][1]}
        self.assertEqual(rows['ramp']['basis'], 'dio_contract')
        self.assertEqual(rows['ramp']['verification'], 'candidate')
        self.assertEqual(rows['ramp']['contracts'], 'c.op1')
        self.assertEqual(rows['creature']['basis'], 'text_pattern_fallback')
        self.assertEqual(rows['draw']['pattern status'], 'supported')


@unittest.skipUnless(DB.exists(), 'KB database not installed (python3 tools/kb_bootstrap.py install)')
class AgainstPinnedKB(unittest.TestCase):
    def test_cultivate_search_is_not_a_draw(self):
        # pattern reader counts Cultivate as draw; its contract feeds card.search + land_to_battlefield (candidate)
        rep = R.role_report(str(DB), ['Cultivate'])['Cultivate']
        self.assertEqual(rep['draw'], {'status': 'not_in_contract', 'basis': 'dio_contract', 'pattern_status': 'supported'})
        self.assertEqual(rep['ramp']['basis'], 'dio_contract')

    def test_grounded_card_result_shows_basis(self):
        ev = R.open_grounded_evaluator(str(DB), games=20, engine_games=2)
        res = ev.card('Cultivate')
        rows = dict(res['sections'])[R.CAPABILITY_SECTION]
        self.assertTrue(rows and all('basis' in r for r in rows))
        self.assertTrue(any('Roles:' in x for x in res['limitations']))


if __name__ == '__main__':
    unittest.main()
