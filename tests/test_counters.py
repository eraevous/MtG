"""Counter identity (kb/counters.py): kind, role and holder survive Oracle -> contract (P-02; C-015, C-016).
Pure text tests: they run in CI without the KB databases."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kb'))
import counters as C  # noqa: E402


def roles(fs):
    return {(f['role'], f['kind'], f['holder']) for f in fs}


class CounterFacets(unittest.TestCase):
    def test_named_kind_and_generic_reader_are_different_facets(self):
        # Twitching Doll: the tap ability puts a nest counter; the sacrifice ability counts every counter, of any kind
        a = C.facets('{T}: Add one mana of any color. Put a nest counter on this creature.', name='Twitching Doll')
        b = C.facets('{T}, Sacrifice this creature: Create a 2/2 green Spider creature token with reach for each counter on '
                     'this creature. Activate only as a sorcery.', name='Twitching Doll')
        self.assertIn(('put', 'nest', 'permanent'), roles(a))
        self.assertIn(('measure', 'any', 'permanent'), roles(b))

    def test_polarity_is_kept(self):
        self.assertIn(('put', '+1/+1', 'permanent'), roles(C.facets('Put a +1/+1 counter on target creature.')))
        self.assertIn(('put', '-1/-1', 'permanent'), roles(C.facets('Put a -1/-1 counter on target creature.')))
        self.assertIn(('remove', 'any', 'permanent'), roles(C.facets('{1}{W/B}, Remove two counters from this creature: Draw a card.')))

    def test_poison_is_held_by_a_player(self):
        fs = C.facets('Target player gets two poison counters.')
        self.assertIn(('put', 'poison', 'player'), roles(fs))

    def test_replacement_modifies_rather_than_produces(self):
        fs = C.facets('If one or more counters would be put on a creature, Spacecraft, or Planet you control, twice that many '
                      'of each of those kinds of counters are put on it instead.')
        self.assertTrue(fs and all(f['role'] == 'modify_put' for f in fs))
        self.assertIn('doubles', {f.get('modifier') for f in fs})

    def test_history_condition_is_not_an_output(self):
        fs = C.facets('At the beginning of each end step, if you put a counter on a creature this turn, draw a card.')
        self.assertEqual({f['role'] for f in fs}, {'condition_put'})
        self.assertEqual(C.produced_kinds(fs), [])

    def test_trigger_listens_for_its_kind(self):
        fs = C.facets('Whenever one or more -1/-1 counters are put on a creature your opponents control, create a 1/1 Snake.',
                      trigger_event='whenever one or more -1/-1 counters are put on a creature your opponents control')
        self.assertIn(('listen_put', '-1/-1', 'permanent'), roles(fs))

    def test_proliferate_adds_only_present_kinds(self):
        fs = C.facets('Proliferate.')
        self.assertEqual(C.produced_kinds(fs), ['present_kinds'])
        self.assertEqual(C.match('present_kinds', '-1/-1'), 'possible')

    def test_the_verb_counter_is_not_a_counter(self):
        self.assertEqual(C.facets('Counter target spell.'), [])

    def test_matching(self):
        self.assertEqual(C.match('+1/+1', '-1/-1'), 'incompatible')
        self.assertEqual(C.match('-1/-1', '-1/-1'), 'compatible')
        self.assertEqual(C.match('nest', 'any'), 'compatible')
        self.assertEqual(C.match('any', 'nest'), 'possible')
        self.assertIsNotNone(C.polarity_note(['-1/-1'], ['+1/+1']))
        self.assertIsNone(C.polarity_note(['nest'], ['+1/+1']))


class CardFacets(unittest.TestCase):
    def test_enters_with_static_has_identity_and_order_note(self):
        fs = C.card_facets('Lifelink\nThis creature enters with two -1/-1 counters on it.\n{1}{W/B}, Remove two counters from '
                           'this creature: Return target creature card with mana value 3 or less from your graveyard to the '
                           'battlefield. Activate only as a sorcery.', 'Reaping Willow', 'Creature - Treefolk Cleric')
        self.assertIn(('enters_with', '-1/-1', 'permanent'), roles(fs))
        self.assertIn(('remove', 'any', 'permanent'), roles(fs))
        note = C.counter_order_note(fs)
        self.assertIn('614.1c', note)
        self.assertIn('704.3', note)

    def test_keyword_macros(self):
        finks = C.card_facets("Persist (When this creature dies, if it had no -1/-1 counters on it, return it to the battlefield "
                              "under its owner's control with a -1/-1 counter on it.)\nWhen this creature enters, you gain 2 life.",
                              'Kitchen Finks')
        self.assertEqual(roles(finks), {('require', '-1/-1', 'permanent'), ('enters_with', '-1/-1', 'permanent')})
        self.assertIn(('put', 'poison', 'player'), roles(C.card_facets('Infect', 'Glistener Elf')))
        self.assertIn(('enters_with', 'lore', 'permanent'), roles(C.card_facets('I - Draw a card.', 'X', 'Enchantment - Saga')))

    def test_granted_keyword_carries_its_counters(self):
        fs = C.card_facets("Players can't gain life.\nAll damage is dealt as though its source had wither.", 'Everlasting Torment')
        self.assertEqual(roles(fs), {('put', '-1/-1', 'permanent')})

    def test_card_name_is_not_a_keyword(self):
        self.assertEqual(C.card_facets('Unleash the Inferno deals 7 damage to target creature.', 'Unleash the Inferno'), [])


if __name__ == '__main__':
    unittest.main()
