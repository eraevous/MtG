"""Runs the v0.2.1d property/metamorphic invariants against the semantic kernel v0.2.1e.

The suite prints one '### <family>: N violations' line per invariant family it breaks.
Only the families listed in KNOWN may appear; anything new fails the test.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "kernel" / "invariants_v021d.py"
BUNDLE = ROOT / "kernel" / "semantic_v0_2_1e"

# Known open violation, recorded in challenges/ledger.jsonl (C-009).
KNOWN = {"M6b re-projecting one resolution double-counts (default ids)"}


class KernelInvariants(unittest.TestCase):
    def test_no_new_invariant_violations(self):
        out = subprocess.run(
            [sys.executable, str(SCRIPT), str(BUNDLE), "3000"],
            capture_output=True, text=True, timeout=300, check=True,
        ).stdout
        found = set(re.findall(r"^### (.+?): \d+ violations", out, flags=re.M))
        self.assertEqual(found - KNOWN, set(), out)


if __name__ == "__main__":
    unittest.main()
