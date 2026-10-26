"""Acceptance tests for the grammar layer (Kate's 2026-10-21 pilot list plus the distinctions Zach asked for).

    python3 -I tests.py      (from this folder)

Each test parses Oracle text with no database, so it pins the grammar and the rules, not a particular build.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar as g  # noqa: E402
import concepts as cx  # noqa: E402


def read(text, type_line='Creature', name='Test Card'):
    """Return [(ability kind, [(role, frame, concepts, completeness, bindings)])]."""
    out = []
    for ab in g.segment_face(g.prep(text, g.self_names(name, name)), type_line, []):
        parts = []
        for p in ab.get('parts', []):
            if p['role'] == 'keyword':
                fr, b = 'keyword ' + ab['keyword'], []
            else:
                fr, b = g.frame(p['text'])
            edges, comp = cx.match_frame(p['role'], fr)
            parts.append((p['role'], fr, {e[0] for e in edges}, comp, b))
        out.append((ab['kind'], parts))
    return out


def concepts(text, **kw):
    return set().union(*[p[2] for _, ps in read(text, **kw) for p in ps])


def frames(text, **kw):
    return [p[1] for _, ps in read(text, **kw) for p in ps]


def bindings(text, slot, **kw):
    return [e[1] for _, ps in read(text, **kw) for p in ps for e in p[4] if e[0] == slot]


class Mana(unittest.TestCase):
    def test_related_but_distinct_outputs(self):
        for t in ('{T}: Add {C}.', '{T}: Add {W}.', '{T}: Add {W} or {B}.', '{T}: Add {W}{B}.'):
            self.assertEqual(concepts(t), {'cost.tap_self', 'op.mana.add'}, t)
        # the choice is in the template, the colours are in the bindings
        self.assertIn('add <mana> or <mana>', frames('{T}: Add {W} or {B}.'))
        self.assertIn('add <mana>', frames('{T}: Add {W}{B}.'))
        self.assertEqual(bindings('{T}: Add {W}{B}.', 'mana'), ['{W}{B}'])
        self.assertEqual(bindings('{T}: Add {W} or {B}.', 'mana'), ['{W}', '{B}'])
        self.assertEqual(bindings('{T}: Add {C}.', 'mana'), ['{C}'])


class TapCostVsEffect(unittest.TestCase):
    def test_three_taps(self):
        self.assertIn('cost.tap_self', concepts('{T}: Add {G}.'))
        self.assertIn('cost.tap_other', concepts('Tap an untapped creature you control: Draw a card.'))
        c = concepts('Tap target creature.', type_line='Instant')
        self.assertIn('op.permanent.tap', c)
        self.assertFalse({'cost.tap_self', 'cost.tap_other'} & c)

    def test_tapped_for_mana_is_not_becomes_tapped(self):
        self.assertIn('ev.permanent.tapped_for_mana', concepts('Whenever you tap a creature for mana, add an additional {G}.'))
        c = concepts('Whenever a creature you control becomes tapped, you gain 1 life.')
        self.assertIn('ev.permanent.tap', c)
        self.assertNotIn('ev.permanent.tapped_for_mana', c)


class Sacrifice(unittest.TestCase):
    def test_actor_cause_and_cardinality_differ(self):
        a = read('Whenever you sacrifice a creature, each opponent loses 1 life.')
        b = read('Whenever a creature dies, each opponent loses 1 life.')
        c = read('Whenever one or more creatures die, each opponent loses 1 life.')
        self.assertIn('ev.permanent.sacrifice', a[0][1][0][2])
        self.assertIn(['player.you', 'you'], a[0][1][0][4])           # actor is kept
        self.assertIn('ev.permanent.dies', b[0][1][0][2])
        self.assertNotIn('ev.permanent.sacrifice', b[0][1][0][2])
        self.assertNotEqual(b[0][1][0][1], c[0][1][0][1])             # "one or more" is a different template
        self.assertIn('<obj.oneormore>', c[0][1][0][1])

    def test_sacrifice_as_cost_vs_effect(self):
        self.assertIn('cost.sacrifice_other', concepts('Sacrifice a creature: Draw a card.'))
        self.assertIn('op.permanent.sacrifice', concepts('Each opponent sacrifices a creature.', type_line='Sorcery'))


class EnterCastCreate(unittest.TestCase):
    def test_not_equivalent(self):
        self.assertIn('ev.battlefield.enter', concepts('Whenever an artifact you control enters, draw a card.'))
        self.assertIn('ev.spell.cast', concepts('Whenever you cast an artifact spell, draw a card.'))
        c = concepts('Create a Treasure token.', type_line='Sorcery')
        self.assertIn('op.token.create', c)
        self.assertFalse({'ev.spell.cast', 'ev.battlefield.enter'} & c)


class Amplifier(unittest.TestCase):
    def test_for_each_is_amplifier_not_requirement(self):
        a = read('When this creature enters, create a 0/1 green Plant creature token for each land you control.')
        b = read('When this creature enters, create a 0/1 green Plant creature token.')
        fa = [p for p in a[0][1] if p[0] == 'effect'][0][1]
        fb = [p for p in b[0][1] if p[0] == 'effect'][0][1]
        self.assertEqual(fa, fb)                                       # same output primitive
        self.assertIn('amp.count', {c for p in a[0][1] for c in p[2]})
        self.assertNotIn('amp.count', {c for p in b[0][1] for c in p[2]})


class Branching(unittest.TestCase):
    def test_if_you_do_and_instead_survive(self):
        r = read('Target creature gets +3/+3 until end of turn. If this spell was kicked, instead that creature gets +4/+4.',
                 type_line='Instant')
        roles = [p[0] for _, ps in r for p in ps]
        self.assertIn('condition', roles)
        c = concepts('At the beginning of combat on your turn, you may pay {E}. If you do, target creature gets +1/+0 until end of turn.')
        self.assertIn('proc.if_you_do', c)
        self.assertIn('op.pay', c)


class EventIntentVsConfirmed(unittest.TestCase):
    def test_destroy_is_an_intent_not_a_death(self):
        c = concepts('Destroy target creature.', type_line='Instant')
        self.assertIn('op.permanent.destroy', c)
        self.assertNotIn('ev.permanent.dies', c)
        self.assertEqual(cx.C['op.permanent.destroy'][0], 'operation')
        self.assertEqual(cx.C['ev.permanent.dies'][0], 'event')

    def test_state_event_operation_are_distinct(self):
        self.assertEqual(cx.C['st.object_status'][0], 'state_predicate')       # a creature is tapped
        self.assertEqual(cx.C['ev.permanent.tap'][0], 'event')                 # a creature became tapped
        self.assertEqual(cx.C['op.permanent.tap'][0], 'operation')             # tap a creature
        self.assertIn('st.object_status', concepts('As long as this creature is tapped, it gets +1/+1.'))


class SpanAccounting(unittest.TestCase):
    def test_unaccounted_words_are_not_complete(self):
        _, comp = cx.match_frame('effect', 'draw <obj.q> unless the moon is full')
        self.assertEqual(comp, 'partial')
        _, comp = cx.match_frame('effect', 'draw <obj.q>')
        self.assertEqual(comp, 'complete')


if __name__ == '__main__':
    unittest.main()
