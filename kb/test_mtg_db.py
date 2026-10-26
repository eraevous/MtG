"""Portable knowledgebase integration tests. Run python -m unittest -v test_mtg_db.py"""
import hashlib,json,sqlite3,unittest
from pathlib import Path
from sqlite_bridge import SQLiteInventory,SQLiteEvaluator
from mtgdb import dbconnect
HERE=Path(__file__).resolve().parent
class MTGDBTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.c=dbconnect(HERE/'mtg_cards.sqlite')
 @classmethod
 def tearDownClass(cls): cls.c.close()
 def scalar(self,s):return self.c.execute(s).fetchone()[0]
 def test_integrity(self):
  self.assertEqual(self.scalar('pragma integrity_check'),'ok')
  self.assertEqual(len(self.c.execute('pragma foreign_key_check').fetchall()),0)
 def test_totals(self):
  self.assertEqual(self.scalar('select count(*) from cards'),3520)
  self.assertEqual(self.scalar('select sum(owned_min) from cards'),5802)
  self.assertEqual(self.scalar('select count(*) from candidate_operations'),4961)
 def test_all_decks(self):
  self.assertEqual(self.scalar('select count(*) from deck_card_counts'),13)
  self.assertEqual(self.scalar('select count(*) from deck_card_counts where total_cards<>100'),0)
 def test_custody(self):
  self.assertEqual(self.scalar('select count(*) from cards where free<>owned_min-assigned'),0)
  self.assertEqual(self.scalar("select count(*) from qa_issues where severity in ('high','critical')"),0)
 def test_no_fake_verification(self):
  self.assertEqual(self.scalar("select count(*) from candidate_operations where verification_status='verified'"),0)
  self.assertEqual(self.scalar('select count(*) from manual_reviews'),0)
 def test_database_contains_every_source_tab(self):
  self.assertEqual(self.scalar('select count(distinct sheet_name) from source_sheet_rows'),41)
  self.assertEqual(self.scalar('select count(*) from ontology_domains'),78)
  self.assertEqual(self.scalar('select count(*) from reference_documents'),5)
 def test_card_oracle_and_ability(self):
  x=self.c.execute("select oracle_text,owned_min from cards where card_name='The Necrobloom'").fetchone()
  self.assertIn('landfall',x['oracle_text'].lower())
  self.assertEqual(x['owned_min'],1)
  self.assertGreaterEqual(self.scalar("select count(*) from projected_abilities where card_name='The Necrobloom'"),1)
 def test_fts(self):
  self.assertGreater(self.scalar("select count(*) from card_fts where card_fts match 'dredge'"),0)
 def test_adapter_decks(self):
  inv=SQLiteInventory(HERE/'mtg_cards.sqlite')
  self.assertEqual(len(inv.decks),13)
  self.assertEqual(sum(q for n,q,s in inv.decks['Necrobloom'] if s!='Companion'),100)
 def test_cache_parity_sample(self):
  from mtg_eval.inventory import Inventory
  from mtg_eval.abilities import card_record
  from build_mtg_db import jsonable
  # This test requires the snapshot to be present; portable DB-only tests don't.
  p=Path('/mnt/data/MTG Master Inventory — Canonical')
  if not p.exists(): self.skipTest('Source workbook not mounted')
  original=Inventory(p);cached=SQLiteInventory(HERE/'mtg_cards.sqlite')
  for n in ['The Necrobloom','Avenger of Zendikar','Cultivate','Resourceful Defense','Duty Beyond Death','Mechan Assembler','Sol Ring','Shore Up','Tendershoot Dryad','Vraska, Soul of Stone','Pactdoll Terror','Inspiring Call','Altered Ego']:
   self.assertEqual(jsonable(card_record(original,n)),jsonable(cached.cached_runtime_record(n)),n)
   self.assertEqual(original.supported(n),cached.supported(n),n)
 def test_db_evaluator(self):
  e=SQLiteEvaluator(HERE/'mtg_cards.sqlite',games=10,engine_games=2)
  r=e.deck('Necrobloom')
  self.assertEqual(r['title'],'Deck: Necrobloom')
  self.assertGreater(len(r['sections']),10)
 def test_source_digest(self):
  sha=self.c.execute("select value from meta where key='input_sha256'").fetchone()[0]
  self.assertEqual(sha,self.scalar('select sha256 from source_snapshots'))
if __name__=='__main__':unittest.main()
