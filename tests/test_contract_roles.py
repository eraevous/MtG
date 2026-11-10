"""kb/contract_roles.py: the evaluator's roles are read from KB contracts, not only cited (C-012).

The fixture tests need no release DB. The last test runs against the pinned KB if it is installed.
"""
import json, sqlite3, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'kb'), str(ROOT / 'kb' / 'vendor')]
import contract_roles as R

DB = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'


def fixture(contracts):
    """A throwaway KB with only operation_contracts: {card: {contract_id: [feeds]}}."""
    con = sqlite3.connect(':memory:')
    con.execute('create table operation_contracts (contract_id text, card_name text, contract_json text)')
    for card, cs in contracts.items():
        for cid, feeds in cs.items():
            con.execute('insert into operation_contracts values (?,?,?)', (cid, card, json.dumps({'query_index': {'feeds': feeds}})))
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
        self.assertTrue({e for es in R.ROLE_MAP.values() for e in es} <= known)


@unittest.skipUnless(DB.exists(), 'KB release DB not installed (python3 tools/kb_bootstrap.py install)')
class AgainstPinnedKB(unittest.TestCase):
    def test_cultivate_search_is_not_a_draw(self):
        # pattern reader counts Cultivate as draw; its contract feeds card.search + land_to_battlefield (candidate)
        rep = R.role_report(str(DB), ['Cultivate'])['Cultivate']
        self.assertEqual(rep['draw'], {'status': 'not_in_contract', 'basis': 'dio_contract', 'pattern_status': 'supported'})
        self.assertEqual(rep['ramp']['basis'], 'dio_contract')


if __name__ == '__main__':
    unittest.main()
