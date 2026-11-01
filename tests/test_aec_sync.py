"""Tests for tools/aec_sync.py without network: a fake `aec` package stands in for upstream AEC.

A violating fixture (the fake check fails) must keep the pin; a clean decoy (it passes) must move it.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import aec_sync as S  # noqa: E402

FAKE_MAIN = """import sys
ok = {ok!r}
print("aec " + sys.argv[1] + (": 0 error(s)" if ok else ": 1 error(s)"))
sys.exit(0 if ok else 1)
"""

PIN = {"repo": "https://example.invalid/AEC", "commit": "a" * 40, "date": "2026-10-31", "aec_version": "0.3"}


class TestAecSync(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        (self.root / ".aec/scenarios").mkdir(parents=True)
        (self.root / ".aec/records.jsonl").write_text("{}\n")
        (self.root / ".aec/scenarios/s1.jsonl").write_text("{}\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def fake_aec(self, ok: bool) -> Path:
        src = self.tmp / f"src_{ok}"
        (src / "aec").mkdir(parents=True)
        (src / "aec/__init__.py").write_text("")
        (src / "aec/__main__.py").write_text(FAKE_MAIN.format(ok=ok))
        return src

    def test_checks_pass_with_a_clean_upstream(self):
        results = S.run_checks(self.fake_aec(True), self.root)
        self.assertEqual([r["name"] for r in results], ["check", "impact s1.jsonl"])
        self.assertTrue(all(r["ok"] for r in results))

    def test_failing_upstream_is_reported(self):
        results = S.run_checks(self.fake_aec(False), self.root)
        self.assertFalse(any(r["ok"] for r in results))
        report = S.render_report(PIN, "b" * 40, ["bbbbbbb 2026-11-01 change"], results)
        self.assertIn("was **not** moved", report)
        self.assertIn("FAIL", report)

    def test_moved_pin_keeps_history(self):
        new = S.moved_pin(PIN, "b" * 40, "2026-11-01")
        self.assertEqual(new["commit"], "b" * 40)
        self.assertEqual(new["history"], [{"commit": "a" * 40, "date": "2026-10-31"}])
        self.assertNotIn("aec_version", new)
        self.assertEqual(PIN["commit"], "a" * 40)  # the old pin object is not mutated

    def test_passing_report_says_the_pin_moves(self):
        results = S.run_checks(self.fake_aec(True), self.root)
        self.assertIn("this PR moves the pin", S.render_report(PIN, "b" * 40, [], results))

    def test_real_pin_file_is_well_formed(self):
        pin = json.loads((ROOT / S.PIN).read_text(encoding="utf-8"))
        self.assertRegex(pin["commit"], r"^[0-9a-f]{40}$")
        self.assertTrue(pin["repo"].startswith("https://github.com/"))


if __name__ == "__main__":
    unittest.main()
