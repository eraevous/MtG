"""Regressions for the KB's role detector (kb/vendor/mtg_eval/semantics.py): wipe scope (kb patch 3) and roles that live in reminder text (kb patch 4). Runs without the KB database."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'kb' / 'vendor'))

from mtg_eval.semantics import oracle_functions  # noqa: E402

WIPES = {
    'Wrath of God': "Destroy all creatures. They can't be regenerated.",
    'Pyroclasm': 'Pyroclasm deals 2 damage to each creature.',
    'Farewell': 'Choose one or more —\n• Exile all artifacts.\n• Exile all creatures.\n• Exile all enchantments.\n• Exile all graveyards.',
    'Swift Demise': "Destroy target creature. Then destroy each creature you don't control that was dealt damage this turn.",
    'Vandalblast': "Destroy target artifact you don't control.\nOverload {4}{R}",
    'Ajani Unrelenting': '−3: Ajani deals 4 damage to each creature except for tokens you control.',
}
NOT_WIPES = {
    'Golden Argosy': 'Whenever Golden Argosy attacks, exile each creature that crewed it this turn. Return them to the battlefield '
                     "tapped under their owner's control at the beginning of the next end step.\nCrew 1",
    'Battle-Scarred Goblin': 'Whenever this creature becomes blocked, it deals 1 damage to each creature blocking it.',
    'Weapon Surge': 'Target creature you control gets +1/+0 and gains first strike until end of turn.\nOverload {1}{R}',
    'Mass flicker': "Exile all creatures. At the beginning of the next end step, return those cards to the battlefield under their owners' control.",
    'Own-side exile': "Exile each creature you control, then return them to the battlefield under their owner's control.",
}


class WipeDetector(unittest.TestCase):
    def test_real_wipes_are_still_detected(self):
        for name, text in WIPES.items():
            self.assertIn('wipe', oracle_functions(name, text, 'Sorcery'), name)

    def test_flicker_and_narrow_scopes_are_not_wipes(self):
        for name, text in NOT_WIPES.items():
            self.assertNotIn('wipe', oracle_functions(name, text, 'Artifact'), name)


# kb patch 4: predefined tokens and token-making keywords, read by name because reminder text is stripped.
TOKEN_ROLES = [
    ('Gold Pan', 'When this Equipment enters, create a Treasure token. (It\'s an artifact with "{T}, Sacrifice this token: '
                 'Add one mana of any color.")', 'Artifact — Equipment', {'ramp', 'fixing'}),
    ('Galactic Wayfarer', 'When this creature enters, create a Lander token. (It\'s an artifact with "{2}, {T}, Sacrifice this '
                          'token: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.")',
     'Creature — Human Scout', {'ramp', 'fixing', 'land_drop'}),
    ("Jet's Brainwashing", 'If this spell was kicked, create a Clue token.', 'Sorcery', {'draw'}),
    ('Mines of Moria', '{T}: Add {R}.\n{3}{R}, {T}, Exile three cards from your graveyard: Create two Treasure tokens.', 'Land', {'ramp', 'fixing'}),
    ('Indebted Spirit', 'Afterlife 1 (When this permanent is put into a graveyard from the battlefield, create a 1/1 white and '
                        'black Spirit creature token with flying.)', 'Enchantment Creature — Spirit', {'token_maker'}),
    ('Kaldra Compleat', 'Living weapon\nIndestructible', 'Legendary Artifact — Equipment', {'token_maker'}),
]
NO_TOKEN_ROLES = [  # sacrificing or caring about a token is not creating one; Junk is impulse, which is not draw (D-0011)
    ('Treasure payoff', 'Whenever you sacrifice a Treasure, create a 1/1 colorless Thopter artifact creature token with flying.',
     'Creature', {'ramp', 'fixing'}),
    ('Junk maker', 'When this creature enters, create a Junk token.', 'Creature', {'draw'}),
    ('Afterlife lord', 'Creatures you control with afterlife get +1/+1.', 'Creature', {'token_maker'}),
]


class ReminderTextRoles(unittest.TestCase):
    def test_token_and_keyword_roles_are_detected(self):
        for name, text, type_line, roles in TOKEN_ROLES:
            self.assertLessEqual(roles, set(oracle_functions(name, text, type_line)), name)

    def test_no_role_without_creating_the_token(self):
        for name, text, type_line, roles in NO_TOKEN_ROLES:
            self.assertFalse(roles & set(oracle_functions(name, text, type_line)), name)


if __name__ == '__main__':
    unittest.main()
