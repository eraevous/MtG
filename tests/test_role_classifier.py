"""Regressions for the KB's wipe role detector (kb/vendor/mtg_eval/semantics.py, kb patch 2). Runs without the KB database."""
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


if __name__ == '__main__':
    unittest.main()
