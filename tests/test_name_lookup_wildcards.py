"""Name lookups treat the typed name as literal text, not as a SQL LIKE pattern.

`_card_row` and `_resolve_deck` fall back to a prefix match when the exact name misses. Before this test, `%` and `_`
in the typed name were LIKE wildcards, so a name containing them could resolve, silently and uniquely, to a different
card or deck. Fixture card names are synthetic.
"""
import sqlite3
import unittest

from mtgtools import verbs


def _db():
    c = sqlite3.connect(':memory:')
    c.row_factory = sqlite3.Row
    c.execute('create table cards(card_name text)')
    c.executemany('insert into cards values (?)', [('Alpha Spring',), ('Beta Gate',), ('Under_score Imp',)])
    c.execute('create table active_deck_cards(deck text)')
    c.execute('insert into active_deck_cards values (?)', ('Blight Curse',))
    c.execute('create table deck_allocations(deck text, section text, counts_in_deck_100 int, card_name text)')
    c.execute("insert into deck_allocations values ('Blight Curse', 'Commander', 1, 'Auntie Ool')")
    return c


class CardNameIsLiteral(unittest.TestCase):
    def test_exact_and_plain_prefix_still_resolve(self):
        c = _db()
        self.assertEqual(verbs._card_row(c, 'Beta Gate')['card_name'], 'Beta Gate')
        self.assertEqual(verbs._card_row(c, 'alpha')['card_name'], 'Alpha Spring')

    def test_percent_is_not_a_wildcard(self):
        with self.assertRaises(LookupError):
            verbs._card_row(_db(), '%spring')

    def test_underscore_is_not_a_wildcard(self):
        with self.assertRaises(LookupError):
            verbs._card_row(_db(), 'b_ta')

    def test_literal_underscore_prefix_still_resolves(self):
        self.assertEqual(verbs._card_row(_db(), 'under_')['card_name'], 'Under_score Imp')


class DeckNameIsLiteral(unittest.TestCase):
    def test_commander_prefix_still_resolves(self):
        self.assertEqual(verbs._resolve_deck(_db(), 'auntie'), 'Blight Curse')

    def test_wildcards_do_not_match_a_commander(self):
        for typed in ('%', '%ool', 'a_ntie'):
            with self.subTest(typed=typed), self.assertRaises(LookupError):
                verbs._resolve_deck(_db(), typed)


if __name__ == '__main__':
    unittest.main()
