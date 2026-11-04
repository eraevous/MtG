"""Saga chapters, Oracle faces, printed costs and token copies (kb/sagas.py, kb/contracts.py drafter 0.6.0; C-024).
Text tests run in CI without the KB databases; the link tests need the KB release (python3 tools/kb_bootstrap.py install)."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'kb'))
sys.path.insert(0, str(ROOT))
import sagas as S  # noqa: E402
import contracts as K  # noqa: E402

ESPER = ("(As this Saga enters and after your draw step, add a lore counter.)\n"
         "I, II, III — Create a token that's a copy of target nonlegendary enchantment you control. It gains haste. If it's a Saga, "
         "put up to three lore counters on it. Sacrifice it at the beginning of your next end step.\n"
         "IV — Add {W}{W}, {U}{U}, {B}{B}, {R}{R}, and {G}{G}. Exile Esper Terra, then return it to the battlefield (front face up).\nFlying")
FENRIR = ("I — Crescent Fang — Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.\n"
          "II — Heavenward Howl — When you next cast a creature spell this turn, that creature enters with an additional +1/+1 counter on it.\n"
          "III — Ecliptic Growl — Draw a card if you control the creature with the greatest power or tied for the greatest power.")


class Chapters(unittest.TestCase):
    def test_chapter_is_a_lore_trigger_with_its_numbers_and_final_chapter(self):
        ch = S.chapter(ESPER.split('\n')[1], 'Legendary Enchantment Creature — Saga Wizard', ESPER)
        self.assertEqual(ch['chapters'], [1, 2, 3])
        self.assertEqual(ch['final_chapter'], 4)
        self.assertEqual(ch['all_chapters'], [1, 2, 3, 4])
        self.assertEqual((ch['trigger']['id'], ch['trigger']['counter_kind'], ch['trigger']['subject']), ('counter.put', 'lore', 'this'))

    def test_named_chapter_keeps_its_name_out_of_the_body(self):
        ch = S.chapter(FENRIR.split('\n')[0], 'Enchantment Creature — Saga Wolf', FENRIR)
        self.assertEqual(ch['chapter_name'], 'Crescent Fang')
        self.assertTrue(ch['body'].startswith('Search your library'))

    def test_not_a_saga_face_is_not_a_chapter(self):
        # a roman numeral on a non-Saga face (class levels, a planeswalker) is not a chapter ability
        self.assertIsNone(S.chapter('I — Draw a card.', 'Legendary Creature — Human', 'I — Draw a card.'))

    def test_chapters_reached_by_a_copy(self):
        # a copy enters with one lore counter (CR 714.3a) and Terra adds up to three: all of chapters I-IV
        self.assertEqual(S.chapters_reached(1, 3, [1, 2, 3, 4]), [1, 2, 3, 4])
        self.assertEqual(S.chapters_reached(1, 3, [1, 2, 3, 4, 5]), [1, 2, 3, 4])


class Copies(unittest.TestCase):
    def test_terra_copies_its_target_and_puts_lore_counters_on_the_token(self):
        cp = S.copies(ESPER.split('\n')[1], 'Terra, Magical Adept // Esper Terra')
        self.assertEqual(len(cp), 1)
        self.assertEqual((cp[0]['source'], cp[0]['filter']), ('target', 'nonlegendary enchantment you control'))
        tc = cp[0]['then_counters']
        self.assertEqual((tc['kind'], tc['amount'], tc['up_to'], tc['recipient']), ('lore', 3, True, 'created_token'))

    def test_self_referent_and_populate(self):
        self.assertEqual(S.copies("Whenever Shredder attacks a player, create a token that's a copy of Shredder tapped and attacking.",
                                  'Shredder, Shadow Master')[0]['source'], 'self')
        self.assertEqual(S.copies("Whenever you sacrifice a nontoken Elemental, create a token that's a copy of it.")[0]['source'], 'referent')
        self.assertEqual(S.copies('Create a 3/3 green Centaur creature token, then populate.')[-1]['filter'], 'creature token you control')

    def test_except_clause_is_kept(self):
        cp = S.copies("Create a token that's a copy of target creature you control, except it's not legendary.")
        self.assertEqual(cp[0]['except'], "it's not legendary")


class DrafterHelpers(unittest.TestCase):
    def test_printed_cost_from_the_clause(self):
        self.assertEqual(K.clause_payment("Trance — {4}{R}{G}, {T}: Exile Terra, then return it transformed."), '{4}{R}{G}, {T}')
        self.assertEqual(K.clause_payment('{T}: Add {R}.'), '{T}')
        self.assertEqual(K.clause_payment('Flying'), '')

    def test_face_from_oracle_when_the_row_is_not_split(self):
        row = [{'face_name': 'A', 'oracle_text': None}, {'face_name': 'B', 'oracle_text': None}]
        oracle = [{'face_name': 'A', 'oracle_text': 'When A enters, draw a card.'}, {'face_name': 'B', 'oracle_text': 'Flying'}]
        face, src = K.locate_face('When A enters, draw a card.', row, oracle)
        self.assertEqual((face['face_name'], src), ('A', 'oracle'))


DB = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'


@unittest.skipUnless(DB.exists(), 'KB database not installed (python3 tools/kb_bootstrap.py install)')
class TerraLinks(unittest.TestCase):
    def hyp(self, a, b):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(['--db', str(DB), 'hypothesis', a, b])
        return json.loads(buf.getvalue())['data']

    def setUp(self):
        import sqlite3
        c = sqlite3.connect(DB)
        drafter = dict(c.execute('select key,value from meta')).get('drafter_version', '')
        c.close()
        if drafter < 'contract-drafter-0.6.0':
            self.skipTest('KB release predates drafter 0.6.0 (C-024)')

    def test_terra_copy_of_choco_mog_reaches_all_four_chapters(self):
        d = self.hyp('Terra, Magical Adept', 'Summon: Choco/Mog')
        ln = [l for l in d['links'] if l['observer'] == 'Summon: Choco/Mog' and l['basis'] == 'copy_chapters']
        self.assertTrue(ln)
        self.assertEqual(ln[0]['qualifiers'], 'compatible')
        self.assertIn('chapters 1, 2, 3, 4 of 4', ln[0]['qualifier_note'])

    def test_terra_does_not_put_its_lore_counters_on_itself(self):
        d = self.hyp('Terra, Magical Adept', 'Summon: Fenrir')
        own = [l for l in d['same_card_links'] if l['produces'] == 'counter.put']
        self.assertFalse([l for l in own if l['qualifiers'] == 'compatible'])

    def test_terra_copy_is_an_enchantment_entering(self):
        d = self.hyp('Terra, Magical Adept', 'Elvish Archivist')
        ln = [l for l in d['links'] if l['observer'] == 'Elvish Archivist' and l['basis'] == 'copy_type']
        self.assertTrue(ln and ln[0]['qualifiers'] == 'compatible')


if __name__ == '__main__':
    unittest.main()
