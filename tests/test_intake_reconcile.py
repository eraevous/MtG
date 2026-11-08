"""Regression and negative controls for read-only intake reconciliation."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'collection' / 'intake_reconcile.py'
spec = importlib.util.spec_from_file_location('intake_reconcile', MODULE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.collection = self.root / 'collection.csv'
        self.collection.write_text('MTG Master Collection\nHeader prose\n\n'
            'Card Name,Known Qty (min),Copies in Decks,Copies Free,Current Deck(s)\n'
            'Hallowed Fountain,1,1,0,TMNT\n'
            'Kindred Judgment,1,0,1,\n'
            'Theorist\'s Proxy,1,0,1,\n'
            'Ornithopter of Paradise,1,0,1,\n', encoding='utf-8')
        self.inventory, self.header_row = r.read_collection(self.collection)

    def test_header_not_position(self):
        self.assertEqual(self.header_row, 4)
        self.assertEqual(len(self.inventory), 4)
        self.assertEqual(self.inventory['Hallowed Fountain']['row_number'], 5)

    def test_hallowed_fountain_copy_preserves_protected(self):
        data = [{'card_name':'Hallowed Fountain','quantity':1,'identity_status':'accepted',
                 'set_code':'rtr','collector_number':'241','finish':'nonfoil'}]
        p, d, report = r.reconcile(self.inventory, data)
        self.assertEqual(report['proposal_copies'], 1)
        self.assertEqual((p[0]['known_qty_before'],p[0]['proposed_known_qty_min']), (1, 2))
        self.assertEqual((p[0]['copies_in_decks'], p[0]['proposed_free_min'], p[0]['current_decks']), (1, 1, 'TMNT'))

    def test_distinguish_ornithopter_from_paradise(self):
        p, _, _ = r.reconcile(self.inventory, [{'card_name':'Ornithopter','quantity':1,'identity_status':'accepted'}])
        self.assertEqual(p[0]['match_status'], 'new_exact_name')
        self.assertEqual(p[0]['known_qty_before'], 0)

    def test_duplicate_printings_aggregate_without_losing_variants(self):
        items=[{'card_name':'Mogg War Marshal','quantity':1,'identity_status':'accepted',
                'set_code':'dmr','collector_number':'131','finish':'nonfoil'},
               {'card_name':'Mogg War Marshal','quantity':1,'identity_status':'accepted',
                'set_code':'dmr','collector_number':'326','finish':'foil'}]
        p,d,report=r.reconcile(self.inventory,items)
        self.assertEqual((len(p),report['proposal_copies']), (1,2))
        self.assertIn('dmr #131',p[0]['printings'])
        self.assertIn('dmr #326',p[0]['printings'])
        self.assertEqual(len(d),2)

    def test_unaccepted_not_counted(self):
        items=[{'card_name':'Hallowed Fountain','quantity':1,'identity_status':'accepted'},
               {'card_name':'Mogg War Marshal','quantity':2,'identity_status':'review'},
               {'card_name':'','quantity':1,'identity_status':'unresolved'}]
        p,d,s=r.reconcile(self.inventory,items)
        self.assertEqual(s['intake_physical_copies_read'],4)
        self.assertEqual(s['proposal_copies'],1)
        self.assertEqual(s['skipped_copies'],3)
        self.assertEqual(s['review_rows'],2)

    def test_similar_alias_quarantined(self):
        p,_,s=r.reconcile(self.inventory,[{'card_name':'theorists proxy','quantity':1,'identity_status':'accepted'}])
        self.assertEqual(p,[])
        self.assertEqual(s['review_rows'],1)
        self.assertEqual(s['review'][0]['reason'],'possible_alias_requires_review')

    def test_foil_unknown_not_assumed_nonfoil(self):
        row=[{'card_name':'Hallowed Fountain','quantity':1,'identity_status':'accepted'}]
        p,_,s=r.reconcile(self.inventory,row)
        self.assertIn('finish unknown',p[0]['printings'])
        self.assertIn('some_printing_finishes_unspecified',p[0]['review_reason'])
        self.assertEqual(s['flagged_proposals'], 1)
        self.assertTrue(s['requires_review'])
        p,_,s=r.reconcile(self.inventory,row,require_finish=True)
        self.assertEqual(p,[])
        self.assertEqual(s['review'][0]['reason'],'finish_unspecified')

    def test_derived_free_discrepancy_flagged(self):
        raw=self.inventory['Kindred Judgment']; raw['free']=0
        p,_,_=r.reconcile(self.inventory,[{'card_name':'Kindred Judgment','quantity':1,'identity_status':'accepted'}])
        self.assertIn('current_free_does_not_equal_qty_minus_deck_copies',p[0]['review_reason'])

    def test_reject_duplicate_collection(self):
        with self.collection.open('a',encoding='utf8') as f: f.write('Hallowed Fountain,1,1,0,TMNT\n')
        with self.assertRaisesRegex(ValueError,'duplicate'): r.read_collection(self.collection)

    def test_reject_formula_or_partial_collection(self):
        self.collection.write_text('Card Name,Known Qty (min),Copies in Decks,Copies Free,Current Deck(s)\n'
                                   'Hallowed Fountain,=A2,1,0,TMNT\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Known Qty'): r.read_collection(self.collection)

    def test_json_review_preserves_raw_speech(self):
        f=self.root/'voice.json'
        f.write_text(json.dumps({'cards':[{'line':7,'spoken':'one Hallowed Fountain set RTR number 241',
                          'name':'Hallowed Fountain','quantity':1,'set_code':'rtr',
                          'collector_number':'241','status':'accepted','method':'batch-exact'}]}))
        rows=r.read_intake(f)
        self.assertEqual(rows[0]['source_text'],'one Hallowed Fountain set RTR number 241')
        self.assertEqual(rows[0]['finish'],'')

    def test_end_to_end_does_not_mutate_inputs(self):
        inp=self.root/'verified.csv'
        inp.write_text('Card Name,Quantity,Set Code,Collector Number,Finish,Notes\nHallowed Fountain,1,rtr,241,nonfoil,voice intake\n', encoding='utf8')
        before=(r.digest(self.collection),r.digest(inp))
        out=self.root/'staging'
        argv=['--collection',str(self.collection),'--intake',str(inp),'--output',str(out),
              '--source-title',r.CANONICAL_TITLE]
        self.assertEqual(r.main(argv),0)
        self.assertEqual(before,(r.digest(self.collection),r.digest(inp)))
        with (out/'proposal.csv').open() as f:
            self.assertEqual(len(list(csv.DictReader(f))),1)
        self.assertEqual(json.loads((out/'review.json').read_text())['status'],'PROPOSAL_ONLY_NOT_APPLIED')

    def test_archive_title_rejected(self):
        inp=self.root/'voice.csv';inp.write_text('Card Name,Quantity\nSol Ring,1\n')
        with self.assertRaises(SystemExit) as e:
            r.main(['--collection',str(self.collection),'--intake',str(inp),'--output',str(self.root/'out'),
                    '--source-title',r.CANONICAL_TITLE+'_ARCHIVE'])
        self.assertEqual(e.exception.code,2)


if __name__=='__main__': unittest.main()
