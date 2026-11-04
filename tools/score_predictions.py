#!/usr/bin/env python3
"""Score the frozen 2026-10-20 predictions against observed games (P-07). Standard library only.

  python3 tools/score_predictions.py                       # docs/game-log/games.csv
  python3 tools/score_predictions.py --games PATH [--predictions PATH] [--json]

Reads the frozen predictions JSON (read-only) and a games CSV (header: docs/game-log/games.csv,
one row per game per deck of Zach's; template: docs/game-log/TEMPLATE.md). For every prediction
line it reports, per game, supported / contradicted / not observable, and a tally.

What this tool does NOT do
- It never edits the predictions file. It refuses to run if the file's SHA-256 differs from the
  pin in tools/drift_rules.json (CHARTER 7: "a scoring tool that refuses unfrozen predictions").
- It scores only observed games dated after the freeze (the JSON's label "observed outcome":
  "supplied by Zach after this file was frozen"). Earlier and same-day games are listed as
  not scored. Vraska is excluded (excluded_from_scoring in the JSON).
- It invents no scoring rule. Rules below come from the "How to score" section of
  predictions/PREDICTIONS_2026-10-20.md plus the wording of each prediction line. Where that
  section does not fix a rule, the measure is reported as "rule not fixed". A rule fixed after
  2026-10-20 would be a new criteria version (P-08) and could not score these predictions.

"How to score" (PREDICTIONS_2026-10-20.md, quoted):
  For each game, note: deck, pod size, result, turn it ended, and which of these happened: a board
  wipe (turn, kind), commander removed (how many times), stalled against blockers, ran out of
  mana, bodies spent on costs instead of attacks. A prediction is supported if its condition
  arose and the deck showed the predicted behaviour, contradicted if the condition arose and it
  did not, and untested if the condition never arose.

Per-measure rules (derived; Zach has not yet accepted them, see D-0026):
  close       column stalled_vs_blockers (y / n / blank). The section names "stalled against
              blockers". Answered y or n = the condition (opponents had blockers that mattered)
              arose; blank = it did not, or was not noticed. y = weakness shown ("games go long
              or stall"), n = strength shown ("pressures life totals through blockers").
  recover     condition: wipe_turn is filled (the section names "a board wipe (turn, kind)").
              behaviour: rebuilt_within_3 (y / n), the prediction lines' own wording ("rebuild
              a threatening board within about three turns"). y = strength, n = weakness.
              Wipe with rebuilt_within_3 blank = not observable.
  contention  column bodies_on_costs (y / n / blank), the section's "bodies spent on costs
              instead of attacks". Answered = the deck reached the midgame with bodies to spend;
              y = weakness shown, n = not shown. Only weaknesses were predicted.
  mana        column ran_out_of_mana (y / n / blank), the section's "ran out of mana". Answered =
              the game reached the midgame; y = weakness ("spells stay in hand"),
              n = strength ("rarely short of mana").
  commander   RULE NOT FIXED. The section records how many times the commander was removed but
              not how many removals make the condition ("repeated commander removal") nor what
              shows "hurts badly". commander_removals is logged, not scored.
  attrition   RULE NOT FIXED. The measure is a wipe followed by three more commander removals;
              the section records the removal count but not whether removals came after the
              wipe, nor what "keeps a board" means. Logged, not scored.
  quality     RULE NOT FIXED. The section names no observation for it (the measure was added
              after the Vraska game). Not scored.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREDICTIONS = ROOT / "predictions" / "PREDICTIONS_2026-10-20.json"
PREDICTIONS_REL = "predictions/PREDICTIONS_2026-10-20.json"
GAMES = ROOT / "docs" / "game-log" / "games.csv"
DRIFT_RULES = ROOT / "tools" / "drift_rules.json"

COLUMNS = ["game_id", "date", "pod_size", "pod", "deck", "deck_version", "turns", "winner", "how",
           "stalled_vs_blockers", "wipe_turn", "wipe_kind", "rebuilt_within_3", "commander_removals",
           "ran_out_of_mana", "bodies_on_costs", "note"]
HOW = {"", "close", "stall", "wipe-recover", "commander removal", "attrition", "mana-screw"}
YN = {"", "y", "n"}

SUPPORTED, CONTRADICTED, NOT_OBSERVABLE, NOT_FIXED = (
    "supported", "contradicted", "not observable", "rule not fixed")

# behaviour flag -> True when the WEAKNESS behaviour was shown
FIXED_RULES = {
    "close": "stalled_vs_blockers=y shows the weakness, n the strength; blank = condition did not arise",
    "recover": "wipe_turn filled is the condition; rebuilt_within_3=y shows the strength, n the weakness",
    "contention": "bodies_on_costs=y shows the weakness, n does not; blank = condition did not arise",
    "mana": "ran_out_of_mana=y shows the weakness, n the strength; blank = condition did not arise",
}
NOT_FIXED_RULES = {
    "commander": "'How to score' fixes no removal count for 'repeated' and no observation for 'hurts badly'",
    "attrition": "'How to score' does not record whether removals followed the wipe, or what 'keeps a board' is",
    "quality": "'How to score' names no observation for this measure",
}


class Refused(Exception):
    pass


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pinned_digest(rules_path: Path = DRIFT_RULES) -> str:
    """The pin lives in tools/drift_rules.json (one home per fact)."""
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    return rules["frozen"][PREDICTIONS_REL]


def load_predictions(path: Path, rules_path: Path = DRIFT_RULES) -> dict:
    digest, pin = sha256(path), pinned_digest(rules_path)
    if digest != pin:
        raise Refused(f"{path} does not match the frozen pin {pin[:12]}... (got {digest[:12]}...). "
                      "Refusing to score unfrozen predictions.")
    return json.loads(path.read_bytes().decode("utf-8"))


def load_games(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            raise Refused(f"{path}: header must be exactly: {','.join(COLUMNS)}")
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in reader]
    rows = [r for r in rows if any(r.values())]
    for i, r in enumerate(rows, start=2):
        where = f"{path}:{i}"
        if not r["game_id"] or not r["deck"]:
            raise Refused(f"{where}: game_id and deck are required")
        try:
            date.fromisoformat(r["date"])
        except ValueError:
            raise Refused(f"{where}: date must be YYYY-MM-DD, got {r['date']!r}")
        for col in ("stalled_vs_blockers", "rebuilt_within_3", "ran_out_of_mana", "bodies_on_costs"):
            r[col] = r[col].lower()
            if r[col] not in YN:
                raise Refused(f"{where}: {col} must be y, n or blank, got {r[col]!r}")
        for col in ("pod_size", "turns", "wipe_turn", "commander_removals"):
            if r[col] and not r[col].isdigit():
                raise Refused(f"{where}: {col} must be a whole number or blank, got {r[col]!r}")
        r["how"] = r["how"].lower()
        if r["how"] not in HOW:
            raise Refused(f"{where}: how must be one of {sorted(HOW - {''})} or blank")
    return rows


def judge(measure: str, direction: str, g: dict) -> str:
    """One prediction line against one game row. Returns a verdict."""
    if measure in NOT_FIXED_RULES or measure not in FIXED_RULES:
        return NOT_FIXED
    if measure == "recover":
        if not g["wipe_turn"] or not g["rebuilt_within_3"]:
            return NOT_OBSERVABLE
        weakness_shown = g["rebuilt_within_3"] == "n"
    else:
        col = {"close": "stalled_vs_blockers", "contention": "bodies_on_costs",
               "mana": "ran_out_of_mana"}[measure]
        if not g[col]:
            return NOT_OBSERVABLE
        weakness_shown = g[col] == "y"
    if direction == "weakness":
        return SUPPORTED if weakness_shown else CONTRADICTED
    return CONTRADICTED if weakness_shown else SUPPORTED


def score(pred: dict, games: list[dict]) -> dict:
    freeze_day = date.fromisoformat(pred["frozen_utc"][:10])
    excluded = pred.get("excluded_from_scoring", {})
    eligible, skipped = [], []
    for g in games:
        d = date.fromisoformat(g["date"])
        if d < freeze_day:
            skipped.append((g, "dated before the freeze: retrospective, never scored"))
        elif d == freeze_day:
            skipped.append((g, "same day as the freeze; cannot show the game came after 16:09Z"))
        elif g["deck"] in excluded:
            skipped.append((g, f"excluded from scoring: {excluded[g['deck']]}"))
        elif g["deck"] not in pred["decks"]:
            skipped.append((g, "no frozen prediction for this deck"))
        else:
            eligible.append(g)
    lines = []
    for deck, info in pred["decks"].items():
        cov = info.get("measurements", {}).get("coverage", "?")
        for p in info["predictions"]:
            row = {"deck": deck, "measure": p["measure"], "direction": p["direction"],
                   "rank": p["rank"], "prediction": p["prediction"], "coverage": cov,
                   "confidence": info.get("confidence (engine coverage)"), "games": []}
            if deck in excluded:
                row["status"] = "excluded"
            elif p["measure"] not in FIXED_RULES:
                row["status"] = NOT_FIXED
            else:
                for g in eligible:
                    if g["deck"] == deck:
                        row["games"].append({"game_id": g["game_id"], "date": g["date"],
                                             "deck_version": g["deck_version"] or "(not recorded)",
                                             "verdict": judge(p["measure"], p["direction"], g)})
                s = sum(x["verdict"] == SUPPORTED for x in row["games"])
                c = sum(x["verdict"] == CONTRADICTED for x in row["games"])
                row["supported"], row["contradicted"] = s, c
                row["status"] = "not observable yet" if s + c == 0 else "scored"
            lines.append(row)
    return {"games": len({g["game_id"] for g in games}),
            "synthetic": any(g["game_id"].upper().startswith("SYNTH") for g in games),
            "skipped": [{"game_id": g["game_id"], "deck": g["deck"], "why": why} for g, why in skipped],
            "lines": lines}


def render(result: dict) -> str:
    out = []
    if result["synthetic"]:
        out.append("SYNTHETIC DATA in the games file: these verdicts are a test, not evidence.")
    out.append(f"{result['games']} games recorded. Frozen predictions 2026-10-20 (hash verified).")
    for s in result["skipped"]:
        out.append(f"  not scored: {s['game_id']} {s['deck']}: {s['why']}")
    for r in result["lines"]:
        head = f"{r['deck']:<13} {r['direction']:<8} {r['measure']:<10} (rank {r['rank']}, coverage {r['coverage']})"
        if r["status"] == "scored":
            detail = "; ".join(f"{g['game_id']} [{g['deck_version']}] {g['verdict']}" for g in r["games"]
                               if g["verdict"] != NOT_OBSERVABLE)
            out.append(f"{head}: supported {r['supported']}, contradicted {r['contradicted']}  ({detail})")
        else:
            out.append(f"{head}: {r['status']}")
    out.append("Rules: fixed for " + ", ".join(FIXED_RULES) + "; not fixed for " + ", ".join(NOT_FIXED_RULES)
               + " (see the docstring of tools/score_predictions.py).")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", type=Path, default=GAMES)
    ap.add_argument("--predictions", type=Path, default=PREDICTIONS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        pred = load_predictions(a.predictions)
        games = load_games(a.games)
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    if not games:
        print("0 games recorded; nothing scored")
        return 0
    result = score(pred, games)
    print(json.dumps(result, indent=1) if a.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
