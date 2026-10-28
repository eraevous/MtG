"""Bring-your-own collection database: import, enrich, read-back and downstream use. No network, no personal data."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'collection'))
sys.path.insert(0, str(ROOT / 'kb' / 'vendor'))
sys.path.insert(0, str(ROOT / 'kb'))
import mtgcollection as mc  # noqa: E402
from mtg_eval import _adapter, collection_db  # noqa: E402
from mtg_eval.inventory import Inventory  # noqa: E402

SCRYFALL = ROOT / 'tests' / 'fixtures' / 'scryfall_sample.json'

MOXFIELD = '''"Count","Tradelist Count","Name","Edition","Condition","Language","Foil","Collector Number"
"1","0","Sol Ring","c21","Near Mint","English","","263"
"2","0","Evolving Wilds","c21","Near Mint","English","foil","286"
"1","0","Brigid, Clachan's Heart","ecl","Near Mint","English","","7"
"1","0","Lim-Dul's Vault","all","Near Mint","English","",""
"1","0","Craw Wurm","m19","Near Mint","English","",""
'''

DECK = '''Commander
1 Emmara, Soul of the Accord (GRN) 168

Deck
1x Sol Ring
1 Temple Garden (GRN) 258 *F*
1 Brigid, Clachan's Heart
3 Forest
2 Plains

Sideboard
1 Craw Wurm
'''


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.db = d / 'sam.sqlite'
        (d / 'moxfield.csv').write_text(MOXFIELD, encoding='utf-8')
        (d / 'deck.txt').write_text(DECK, encoding='utf-8')
        self.csv, self.deck = d / 'moxfield.csv', d / 'deck.txt'
        self.con = mc.connect(self.db, create=True)
        mc.set_meta(self.con, collection_name='Sam example', owner='Sam')
        self.con.commit()

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def build(self, own_missing=True, status='Current deck'):
        mc.import_csv(self.con, self.csv, 'moxfield')
        result = mc.import_deck(self.con, self.deck, 'Emmara', status=status, own_missing=own_missing)
        mc.enrich(self.con, scryfall=SCRYFALL)
        return result

    def test_decklist_formats(self):
        cards, skipped = mc.parse_decklist(DECK)
        self.assertEqual(cards[0], ('Emmara, Soul of the Accord', 1, 'Commander'))
        self.assertIn(('Temple Garden', 1, ''), cards)
        self.assertIn(('Sol Ring', 1, ''), cards)
        self.assertEqual(skipped, ['Craw Wurm'])
        cards, _ = mc.parse_decklist('1 Atraxa, Praetors\' Voice *CMDR*\n1 Sol Ring [Ramp]\n')
        self.assertEqual(cards[0][2], 'Commander')
        cards, _ = mc.parse_decklist('1 Sol Ring\n', commanders=['sol ring'])
        self.assertEqual(cards[0][2], 'Commander')
        with self.assertRaises(ValueError):
            mc.parse_decklist('Sol Ring without a count\n')

    def test_archidekt_board_tags_are_skipped(self):
        cards, skipped = mc.parse_decklist('1x Kenrith, the Returned King (eld) 303 [Commander{top}]\n'
                                           '1x Sol Ring (c21) 263 [Ramp]\n1x Craw Wurm (m19) 1 [Maybeboard{noDeck}{noPrice}]\n')
        self.assertEqual([c[0] for c in cards], ['Kenrith, the Returned King', 'Sol Ring'])
        self.assertEqual(cards[0][2], 'Commander')
        self.assertEqual(skipped, ['Craw Wurm'])

    def test_own_missing_uses_the_collection_spelling(self):
        # regression: a front-face deck line must not add a second copy of a card the CSV already holds
        p = Path(self.tmp.name) / 'split.csv'
        p.write_text('Name,Count\n"Brigid, Clachan\'s Heart // Brigid, Doun\'s Mind",1\nSol Ring,1\n', encoding='utf-8')
        mc.import_csv(self.con, p, 'csv')
        d = Path(self.tmp.name) / 'd.txt'
        d.write_text("1 Brigid, Clachan's Heart\n1 Sol Ring\n", encoding='utf-8')
        r = mc.import_deck(self.con, d, 'D', own_missing=True)
        self.assertEqual(r['holdings_added'], 0)
        mc.enrich(self.con, scryfall=SCRYFALL)
        owned = dict(self.con.execute('select card_name, owned from owned'))
        self.assertEqual(owned["Brigid, Clachan's Heart // Brigid, Doun's Mind"], 1)

    def test_overlapping_sources_warn(self):
        mc.import_csv(self.con, self.csv, 'export')
        p = Path(self.tmp.name) / 'export_nov.csv'
        p.write_text(MOXFIELD, encoding='utf-8')
        r = mc.import_csv(self.con, p)
        self.assertIn('export', r['warning'])

    def test_sheet_import_keeps_decks_from_import_deck(self):
        mc.import_csv(self.con, self.csv, 'moxfield')
        mc.import_deck(self.con, self.deck, 'Mine', own_missing=True)
        sheet = [{'Card Name': 'Sol Ring', 'Deck': 'Sheet deck', 'Status': 'Current deck', 'Quantity': '1', 'Section': ''}]
        mc.replace_allocations(self.con, sheet)
        mc.replace_allocations(self.con, sheet)   # a second Sheet import replaces only the Sheet's decks
        decks = dict(self.con.execute('select deck, count(*) from deck_cards group by deck'))
        self.assertEqual(decks, {'Mine': 6, 'Sheet deck': 1})

    def test_csv_aliases_and_reimport_replaces_source(self):
        r = mc.import_csv(self.con, self.csv, 'moxfield')
        self.assertEqual((r['rows'], r['copies']), (5, 6))
        h = self.con.execute("select finish,set_code,collector_number,condition from holdings where card_name='Evolving Wilds'").fetchone()
        self.assertEqual(tuple(h), ('foil', 'c21', '286', 'Near Mint'))
        mc.import_csv(self.con, self.csv, 'moxfield')
        mc.import_csv(self.con, self.csv, 'binder')
        owned = dict(self.con.execute('select card_name, owned from owned'))
        self.assertEqual(owned['Evolving Wilds'], 4)   # two sources, each counted once

    def test_names_only_list_counts_one_each(self):
        p = Path(self.tmp.name) / 'names.csv'
        p.write_text('Name\nSol Ring\nCraw Wurm\n', encoding='utf-8')
        mc.import_csv(self.con, p)
        self.assertEqual(dict(self.con.execute('select card_name, owned from owned')), {'Sol Ring': 1, 'Craw Wurm': 1})

    def test_enrich_canonicalizes_names_and_fills_sheet_columns(self):
        self.build()
        names = {r[0] for r in self.con.execute('select card_name from cards')}
        self.assertIn("Brigid, Clachan's Heart // Brigid, Doun's Mind", names)
        self.assertIn("Lim-Dûl's Vault", names)
        self.assertNotIn("Lim-Dul's Vault", names)
        rows = {r['Card Name']: r for r in collection_db.read(self.db, {'Collection'})['Collection']}
        brigid = rows["Brigid, Clachan's Heart // Brigid, Doun's Mind"]
        self.assertTrue(brigid['Oracle Text'].startswith("Brigid, Clachan's Heart {2}{W}\n"))
        self.assertIn("\n\nBrigid, Doun's Mind\n", brigid['Oracle Text'])
        self.assertEqual((brigid['Mana Cost'], brigid['Color Identity'], brigid['Can Be Commander']), ('{2}{W}', 'WG', 'Yes'))
        self.assertEqual(brigid['Recorded / Printed Alias'], "Brigid, Clachan's Heart")
        self.assertEqual(rows['Temple Garden']['ETB Tapped'], 'Conditional')
        self.assertEqual(rows['Evolving Wilds']['ETB Tapped'], 'No')   # the land itself enters untapped, as the canonical Sheet records it
        self.assertEqual(rows['Sol Ring']['ETB Tapped'], 'N/A')
        self.assertEqual(rows['Sol Ring']['Produces'], 'C')
        self.assertEqual(rows['Sol Ring']['Color Identity'], 'C')
        self.assertEqual(rows['Emmara, Soul of the Accord']['Commander Legal'], 'Legal')
        self.assertEqual(rows['Craw Wurm']['Oracle Text'], '')        # vanilla, but has card data
        self.assertEqual(mc.check(self.db)['cards_without_card_data'], 0)

    def test_back_face_names_never_shadow_real_cards(self):
        mdfc = {'name': 'Studious First-Year // Rampant Growth',
                'card_faces': [{'name': 'Studious First-Year'}, {'name': 'Rampant Growth'}]}
        real = {'name': 'Rampant Growth'}
        for order in ([mdfc, real], [real, mdfc]):
            match = mc.name_matcher(order)
            self.assertIs(match('Rampant Growth'), real)
            self.assertIs(match('Studious First-Year'), mdfc)
        self.assertIsNone(mc.name_matcher([mdfc])('Rampant Growth'))

    def test_custody_is_computed_not_stored(self):
        r = self.build()
        self.assertEqual(r['cards'], 9)
        rows = {r['Card Name']: r for r in collection_db.read(self.db, {'Collection'})['Collection']}
        # Sol Ring: 1 owned from Moxfield, 1 in the deck
        self.assertEqual((rows['Sol Ring']['Known Qty (min)'], rows['Sol Ring']['Copies in Decks'], rows['Sol Ring']['Copies Free']), ('1', '1', '0'))
        # Evolving Wilds: 2 owned, none in decks
        self.assertEqual((rows['Evolving Wilds']['Copies Free'], rows['Evolving Wilds']['Availability']), ('2', 'Free'))
        # Forest: not in the CSV; --own-missing added the 3 the deck holds
        self.assertEqual(rows['Forest']['Known Qty (min)'], '3')
        self.assertEqual(rows['Forest']['Current Deck(s)'], 'Emmara')

    def test_shortfall_without_own_missing_is_reported(self):
        self.build(own_missing=False)
        kinds = {i['kind'] for i in mc.check(self.db)['problems']}
        self.assertIn('overallocated', kinds)

    def test_plan_status_is_not_a_physical_move(self):
        self.build(own_missing=False, status='Candidate list')
        inv = Inventory(self.db)
        self.assertEqual(inv.decks, {})
        self.assertEqual(inv.free('Sol Ring'), 1)

    def test_evaluator_inventory_reads_the_database(self):
        self.build()
        inv = Inventory(self.db)
        self.assertEqual(inv.commanders('Emmara'), ['Emmara, Soul of the Accord'])
        self.assertEqual(inv.deck_ci('Emmara'), {'W', 'G'})
        self.assertEqual(inv.owned('Evolving Wilds'), 2)
        self.assertEqual(inv.free('Sol Ring'), 0)
        self.assertEqual(inv.holders('Sol Ring'), ['Emmara'])
        self.assertTrue(inv.legal_in('Sol Ring', {'W', 'G'})[0])
        self.assertIn("'Sam example'", inv.source()['sheet_id'])
        health = _adapter.normalize(collection_db.read(self.db))['health']
        self.assertEqual(health['deck_counts'], {'Emmara': 9})
        self.assertEqual(health['critical_problems'], 0)

    def test_kb_build_accepts_the_database(self):
        import build_mtg_db
        self.build(own_missing=False, status='Candidate list')   # no 100-card deck needed for a plan
        out = Path(self.tmp.name) / 'kb' / 'mtg_cards.sqlite'
        audit = build_mtg_db.build(self.db, out)
        self.assertEqual(audit['cards'], 9)
        meta = dict(sqlite3.connect(out).execute('select key,value from meta'))
        self.assertEqual(meta['canonical_sheet_id'], 'collection:Sam example')
        self.assertNotIn('collection_imported_from_sheet', meta)
        self.assertEqual(meta['source_type'], 'read-only collection database')

    def test_reader_refuses_other_sqlite_files(self):
        other = Path(self.tmp.name) / 'other.sqlite'
        sqlite3.connect(other).execute('create table t(x)').connection.close()
        self.assertTrue(collection_db.is_collection_db(other))
        with self.assertRaises(ValueError):
            collection_db.read(other)
        self.assertFalse(collection_db.is_collection_db(SCRYFALL))

    def test_generic_xlsx_tab_round_trip(self):
        # A minimal one-tab workbook, as Google Sheets exports it, read through the adapter's OOXML reader.
        import zipfile
        p = Path(self.tmp.name) / 'mine.xlsx'
        ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        cells = [('A1', 'Name'), ('B1', 'Qty'), ('A2', 'Sol Ring'), ('B2', '3'), ('A3', 'Craw Wurm'), ('B3', '1')]
        rows = {}
        for ref, v in cells:
            rows.setdefault(ref[1:], []).append(f'<c r="{ref}" t="inlineStr"><is><t>{v}</t></is></c>')
        sheet = f'<worksheet xmlns="{ns}"><sheetData>' + ''.join(f'<row r="{r}">{"".join(c)}</row>' for r, c in rows.items()) + '</sheetData></worksheet>'
        with zipfile.ZipFile(p, 'w') as z:
            z.writestr('xl/workbook.xml', f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                                          '<sheets><sheet name="My cards" sheetId="1" r:id="rId1"/></sheets></workbook>')
            z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                                     '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
            z.writestr('xl/worksheets/sheet1.xml', sheet)
        r = mc.import_xlsx(self.con, p)
        self.assertEqual((r['rows'], r['copies']), (2, 4))
        self.assertNotIn('My cards', _adapter.HEADER_ROWS)   # the reader's tab table is restored


if __name__ == '__main__':
    unittest.main()
