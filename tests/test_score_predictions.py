"""Tests for tools/score_predictions.py (P-07). All game data here is SYNTHETIC.

  python3 -m unittest discover -s tests
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import score_predictions as S  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "game_log" / "games_synthetic.csv"


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = S.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class EmptyLog(unittest.TestCase):
    def test_header_only_log_scores_nothing(self):
        code, out, _ = run("--games", str(ROOT / "docs" / "game-log" / "games.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "0 games recorded; nothing scored")

    def test_shipped_header_matches_schema(self):
        header = (ROOT / "docs" / "game-log" / "games.csv").read_text(encoding="utf-8").strip()
        self.assertEqual(header, ",".join(S.COLUMNS))


class SyntheticGames(unittest.TestCase):
    def setUp(self):
        pred = S.load_predictions(S.PREDICTIONS)
        self.result = S.score(pred, S.load_games(FIXTURE))
        self.lines = {(r["deck"], r["measure"], r["direction"]): r for r in self.result["lines"]}

    def test_supported(self):
        for m in ("close", "recover"):
            r = self.lines[("Sharuum", m, "strength")]
            self.assertEqual((r["supported"], r["contradicted"]), (1, 0), m)
        r = self.lines[("Sharuum", "contention", "weakness")]
        self.assertEqual((r["supported"], r["contradicted"]), (1, 0))

    def test_contradicted(self):
        r = self.lines[("Sharuum", "mana", "weakness")]
        self.assertEqual((r["supported"], r["contradicted"]), (0, 1))

    def test_not_observable_when_condition_did_not_arise(self):
        # SYNTH-02: TMNT game with no blockers noted, no wipe, ended before the midgame
        for key in [("TMNT", "close", "strength"), ("TMNT", "recover", "weakness"), ("TMNT", "mana", "strength")]:
            r = self.lines[key]
            self.assertEqual(r["status"], "not observable yet", key)
            self.assertTrue(all(g["verdict"] == S.NOT_OBSERVABLE for g in r["games"]))

    def test_rule_not_fixed_measures_are_never_scored(self):
        for (deck, measure, _), r in self.lines.items():
            if measure in S.NOT_FIXED_RULES and deck != "Vraska":
                self.assertEqual(r["status"], S.NOT_FIXED)
                self.assertEqual(r["games"], [])
        # Sharuum's commander weakness: 2 removals recorded, still not scored
        self.assertEqual(self.lines[("Sharuum", "commander", "weakness")]["status"], S.NOT_FIXED)

    def test_no_retrospective_or_excluded_scoring(self):
        skipped = {s["game_id"]: s["why"] for s in self.result["skipped"]}
        self.assertIn("before the freeze", skipped["SYNTH-03"])
        self.assertIn("same day", skipped["SYNTH-06"])
        self.assertIn("excluded", skipped["SYNTH-04"])
        self.assertIn("no frozen prediction", skipped["SYNTH-05"])
        for (deck, _, _), r in self.lines.items():
            if deck in ("Dina", "Ashling"):
                self.assertFalse(r["games"], deck)
            if deck == "Vraska":
                self.assertEqual(r["status"], "excluded")

    def test_deck_version_and_coverage_travel_with_each_comparison(self):
        r = self.lines[("Sharuum", "close", "strength")]
        self.assertEqual(r["coverage"], "20/63")
        self.assertEqual(r["games"][0]["deck_version"], "synthetic-v1")

    def test_synthetic_banner(self):
        code, out, _ = run("--games", str(FIXTURE))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("SYNTHETIC DATA"))


class FrozenHash(unittest.TestCase):
    def test_decoy_real_file_is_accepted_and_untouched(self):
        before = S.sha256(S.PREDICTIONS)
        self.assertEqual(before, S.pinned_digest())
        run("--games", str(FIXTURE))
        run("--games", str(FIXTURE), "--json")
        self.assertEqual(S.sha256(S.PREDICTIONS), before)
        self.assertEqual(S.sha256(S.PREDICTIONS), "18657701bdba2bdc5beb60b4bd66632396b0e55c99fd8bed9bed80fa9bce589c")

    def test_violation_tampered_copy_is_refused(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        p = tmp / "PREDICTIONS_2026-10-20.json"
        data = json.loads(S.PREDICTIONS.read_text(encoding="utf-8"))
        data["decks"]["Sharuum"]["predictions"][0]["direction"] = "weakness"
        p.write_text(json.dumps(data), encoding="utf-8")
        code, out, err = run("--games", str(FIXTURE), "--predictions", str(p))
        self.assertEqual(code, 2)
        self.assertIn("Refusing to score unfrozen predictions", err)
        self.assertEqual(out, "")


class BadInput(unittest.TestCase):
    def write(self, text):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        p = tmp / "games.csv"
        p.write_text(text, encoding="utf-8")
        return p

    def test_wrong_header_refused(self):
        code, _, err = run("--games", str(self.write("game,deck\nx,y\n")))
        self.assertEqual(code, 2)
        self.assertIn("header", err)

    def test_bad_flag_refused(self):
        row = "SYNTH-9,2026-11-01,4,p,Sharuum,v,9,w,close,maybe,,,,0,n,n,SYNTHETIC"
        code, _, err = run("--games", str(self.write(",".join(S.COLUMNS) + "\n" + row + "\n")))
        self.assertEqual(code, 2)
        self.assertIn("stalled_vs_blockers", err)


if __name__ == "__main__":
    unittest.main()
