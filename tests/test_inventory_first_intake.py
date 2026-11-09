"""Inventory-first intake: synthetic fixtures, no network or personal inventory."""
import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from collection import voice_intake as v
from collection import intake_reconcile as reconcile
from test_voice_intake import FakeTransport, card, client


class InventoryFirstTests(unittest.TestCase):
    def test_sixty_local_identities_no_requests_or_printing_inference(self):
        inventory = v.InventoryIndex('Card Name,Known Qty (min),Scryfall URL,Finish\n' + ''.join(
            f'Example Card {i},0,https://scryfall.com/card/cmm/{i}/example,foil\n' for i in range(60)))
        fake = FakeTransport()
        report = v.resolve(v.parse('\n'.join(f'Example Card {i}' for i in range(60))), client(fake), inventory=inventory)
        self.assertEqual((report['accepted'], report['inventory_matches'], report['requests']), (60, 60, 0))
        self.assertEqual(fake.requests, [])
        for row in report['cards']:
            self.assertEqual(row['identity_scope'], 'card_name')
            self.assertEqual(row['printing_status'], 'not_identified')
            for field in ('set_code', 'collector_number', 'scryfall_id', 'scryfall_uri', 'finish', 'language'):
                self.assertIsNone(row[field])
        self.assertEqual(report['inventory']['freshness'], 'not_verified')
        self.assertIn('not_current_ownership', report['inventory']['role'])

    def test_only_misses_leave_local_machine_batched_and_deduped(self):
        inventory = v.InventoryIndex('Card Name,Set Code,Collector Number,Notes\nPrivate Known,cmm,1,secret note\n')
        entries = v.parse('Private Known set CMM number 1; ' + '; '.join(f'CMM {i}' for i in range(2, 82)) + '; 3 CMM 2')
        fake = FakeTransport()
        report = v.resolve(entries, client(fake), inventory=inventory)
        self.assertEqual((report['accepted'], report['inventory_matches'], report['requests']), (82, 1, 2))
        identifiers = [json.loads(req.data)['identifiers'] for req in fake.requests]
        self.assertEqual(list(map(len, identifiers)), [75, 5])
        self.assertNotIn('Private Known', str(identifiers))
        self.assertNotIn('secret note', str(identifiers))
        self.assertEqual(sum(row['quantity'] for row in report['cards']), 84)
        self.assertEqual(report['cards'][0]['printing_status'], 'recorded_set_and_number_match')

    def test_name_only_never_borrows_the_only_known_printing(self):
        inventory = v.InventoryIndex('Card Name,Set Code,Collector Number,Finish,Language\nSol Ring,cmm,396,foil,Japanese\n')
        report = v.resolve(v.parse('Sol Ring; Sol Ring set CMM'), client(FakeTransport()), inventory=inventory)
        self.assertEqual(report['requests'], 0)
        self.assertEqual([r['set_code'] for r in report['cards']], [None, 'cmm'])
        self.assertEqual([r['collector_number'] for r in report['cards']], [None, None])
        self.assertTrue(all(r['finish'] is None and r['language'] is None for r in report['cards']))
        self.assertEqual([r['Set Code'] for r in csv.DictReader(io.StringIO(v.csv_content(report)))], ['', 'cmm'])

    def test_reference_url_is_not_owned_printing(self):
        inventory = v.InventoryIndex('Card Name,Scryfall URL\nSol Ring,https://scryfall.com/card/cmm/396/sol-ring\n')
        fake = FakeTransport([card()])
        report = v.resolve(v.parse('Sol Ring set CMM number 396'), client(fake), inventory=inventory)
        self.assertEqual((report['inventory_matches'], report['requests']), (0, 1))

    def test_conflicting_printings_and_names_fall_through(self):
        cases = [
            ('Sol Ring,c21,263\n', 'Sol Ring set CMM number 396'),
            ('Sol Ring,cmm,396\nDifferent Card,cmm,396\n', 'CMM 396'),
            ('Sol Ring,cmm,396\n', 'Wrong Name set CMM number 396'),
            ('Sol-Ring,cmm,396\nSol Ring,c21,263\n', 'solring'),
        ]
        for rows, text in cases:
            with self.subTest(text=text, rows=rows):
                report = v.resolve(v.parse(text), client(FakeTransport([])), 0,
                                   inventory=v.InventoryIndex('Card Name,Set Code,Collector Number\n' + rows))
                self.assertEqual(report['inventory_matches'], 0)
                self.assertEqual(report['requests'], 1)
                self.assertEqual(report['accepted'], 0)

    def test_duplicate_holdings_dont_inflate_intake_or_make_name_ambiguous(self):
        inventory = v.InventoryIndex('Card Name,Set Code,Collector Number\nSol Ring,cmm,396\nSol Ring,c21,263\n')
        report = v.resolve(v.parse('2 Sol Ring; Sol Ring'), client(FakeTransport()), inventory=inventory)
        self.assertEqual(report['requests'], 0)
        self.assertEqual([r['quantity'] for r in report['cards']], [2, 1])
        self.assertEqual(report['cards'][0]['inventory_rows'], [2, 3])

    def test_complete_two_face_identity_and_no_back_face_shortcut(self):
        inventory = v.InventoryIndex('Card Name,Set Code,Collector Number\nFront // Correct Back,cmm,1\n')
        for text in ('Front // Wrong Back', 'Correct Back', 'Front', 'Front // Wrong Back set CMM number 1'):
            report = v.resolve(v.parse(text), client(FakeTransport([])), 0, inventory=inventory)
            self.assertEqual(report['inventory_matches'], 0, text)
        report = v.resolve(v.parse('Front // Correct Back'), client(FakeTransport()), inventory=inventory)
        self.assertEqual(report['requests'], 0)

    def test_bare_quantity_word_keeps_both_interpretations_for_external_resolution(self):
        inventory = v.InventoryIndex('Card Name\nSeven Dwarves\n')
        fake = FakeTransport([card('Seven Dwarves'), card('Dwarves', n='2')])
        report = v.resolve(v.parse('Seven Dwarves'), client(fake), inventory=inventory)
        self.assertEqual((report['inventory_matches'], report['review']), (0, 1))
        self.assertEqual(json.loads(fake.requests[0].data)['identifiers'],
                         [{'name': 'Dwarves'}, {'name': 'Seven Dwarves'}])
        report = v.resolve(v.parse_csv('Card Name,Quantity\nSeven Dwarves,1\n'), client(FakeTransport()), inventory=inventory)
        self.assertEqual((report['inventory_matches'], report['requests']), (1, 0))

    def test_fuzzy_duplicate_queries_are_cached_but_each_copy_stays_for_review(self):
        fake = FakeTransport([], {'Sole Rung': card()})
        report = v.resolve(v.parse('Sole Rung; 2 Sole Rung; Sole Rung'), client(fake))
        self.assertEqual((report['requests'], report['review']), (2, 3))
        self.assertEqual([r['quantity'] for r in report['cards']], [1, 2, 1])
        self.assertEqual(v.csv_content(report).count('\n'), 1)

    def test_structured_capture_preserves_finish_language_and_original_text(self):
        text = 'Card Name,Quantity,Set Code,Collector Number,Finish,Language,Source Text\nSol Ring,2,cmm,396,foil,Japanese,photo 1\n'
        inventory = v.InventoryIndex('Card Name,Set Code,Collector Number\nSol Ring,cmm,396\n')
        report = v.resolve(v.parse_csv(text), client(FakeTransport()), inventory=inventory)
        row = report['cards'][0]
        self.assertEqual((row['finish'], row['language'], row['spoken']), ('foil', 'Japanese', 'photo 1'))
        exported = next(csv.DictReader(io.StringIO(v.csv_content(report))))
        self.assertEqual((exported['Finish'], exported['Language'], exported['Method']), ('foil', 'Japanese', 'inventory-exact'))

    def test_invalid_quantities_never_lookup_or_accept(self):
        inventory = v.InventoryIndex('Card Name\nSol Ring\n')
        for raw in ('0', '-1', '1.5', '', '=1+1'):
            report = v.resolve(v.parse_csv(f'Card Name,Quantity\nSol Ring,{raw}\n'), client(FakeTransport()), inventory=inventory)
            self.assertEqual((report['unresolved'], report['requests']), (1, 0), raw)
        report = v.resolve(v.parse('0 Sol Ring'), client(FakeTransport()), inventory=inventory)
        self.assertEqual((report['unresolved'], report['requests']), (1, 0))

    def test_preamble_and_invalid_headers(self):
        inventory = v.InventoryIndex('Title\nSome description\n\nCard Name,Known Qty (min)\nSol Ring,99\n')
        self.assertEqual(inventory.match(v.parse('Sol Ring')[0])['inventory_rows'], [5])
        for text in ('Name,Card Name\nA,B\n', 'Name,Name\nA,B\n', 'Not a CSV', 'Name\nA,B\n'):
            with self.assertRaises(ValueError):
                v.InventoryIndex(text)

    def test_cli_all_local_is_read_only_and_json_csv_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inv = root / 'inventory.csv'
            inv.write_text('Card Name,Known Qty (min),Copies in Decks,Copies Free,Current Deck(s)\nSol Ring,1,1,0,Protected\n')
            inp = root / 'input.csv'
            inp.write_text('Card Name,Quantity,Finish,Language\nSol Ring,2,foil,Japanese\n')
            before = (inv.read_bytes(), inp.read_bytes())
            review, accepted = root / 'review.json', root / 'accepted.csv'
            fake = FakeTransport()
            with patch.object(v, 'ScryfallClient', return_value=client(fake)), redirect_stdout(io.StringIO()):
                result = v.main([str(inp), '--input-format', 'csv', '--inventory', str(inv),
                                 '--review', str(review), '--csv', str(accepted)])
            self.assertEqual(result, 0)
            self.assertEqual(before, (inv.read_bytes(), inp.read_bytes()))
            self.assertEqual(fake.requests, [])
            collection, _ = reconcile.read_collection(inv)
            for path in (review, accepted):
                proposals, details, report = reconcile.reconcile(collection, reconcile.read_intake(path))
                self.assertEqual(details[0]['language'], 'Japanese')
                self.assertIn('Japanese', proposals[0]['printings'])
                self.assertEqual((proposals[0]['proposed_known_qty_min'], proposals[0]['copies_in_decks']), (3, 1))
                self.assertEqual(proposals[0]['current_decks'], 'Protected')
                self.assertIn('some_printing_identifiers_unspecified', proposals[0]['review_reason'])
                self.assertTrue(report['requires_review'])

    def test_output_aliases_rejected_before_network_or_writes(self):
        import os
        for source in ('inventory', 'capture', 'output'):
            for alias in ('same', 'symlink', 'hardlink'):
                with self.subTest(source=source, alias=alias), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    inv, inp, review, accepted = (root / name for name in ('inv.csv', 'input.txt', 'out.json', 'out.csv'))
                    inv.write_text('Card Name\nSol Ring\n')
                    inp.write_text('Unknown Card')
                    review.write_text('old review')
                    target = {'inventory': inv, 'capture': inp, 'output': review}[source]
                    if alias == 'same':
                        accepted = target
                    elif alias == 'symlink':
                        accepted.symlink_to(target)
                    else:
                        os.link(target, accepted)
                    before = (inv.read_bytes(), inp.read_bytes(), review.read_bytes(), target.read_bytes())
                    fake = FakeTransport()
                    with patch.object(v, 'ScryfallClient', return_value=client(fake)), redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as exc:
                            v.main([str(inp), '--inventory', str(inv), '--csv', str(accepted), '--review', str(review)])
                    self.assertEqual(exc.exception.code, 2)
                    self.assertEqual(before, (inv.read_bytes(), inp.read_bytes(), review.read_bytes(), target.read_bytes()))
                    self.assertEqual(fake.requests, [])
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp) / 'inv.csv'
            inv.write_text('Card Name\nSol Ring\n')
            with patch('sys.stdin', io.StringIO('Sol Ring')), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    v.main(['-', '--inventory', str(inv), '--review', str(inv)])
            self.assertEqual(inv.read_text(), 'Card Name\nSol Ring\n')

    def test_invalid_inventory_fails_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp) / 'bad.csv'
            inv.write_text('invalid')
            fake = FakeTransport()
            with patch.object(v, 'ScryfallClient', return_value=client(fake)), \
                 patch('sys.stdin', io.StringIO('Sol Ring')), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    v.main(['-', '--inventory', str(inv)])
            self.assertEqual(exc.exception.code, 2)
            self.assertEqual(fake.requests, [])


if __name__ == '__main__':
    unittest.main()
