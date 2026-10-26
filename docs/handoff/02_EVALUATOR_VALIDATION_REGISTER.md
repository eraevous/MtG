# MTG Evaluator — Validation & Evidence Register
**Revision:** 2026-10-25 • **Status:** working evidence standard, not a deck ranking.

## Frozen baselines — NEVER RETROFIT

- **2026-10-20T16:09:35Z:** pre-game predictions for 12 decks, 500 engine games per scenario, seed `20261018`; predictions JSON SHA-256 `18657701bdba2bdc5beb60b4bd66632396b0e55c99fd8bed9bed80fa9bce589c`. Vraska deliberately excluded from scoring because its reported outcome informed the measures. Preserve predeclared ranks and tie rules; score only later independent game reports.
- **2026-10-25:** evaluator `mtg_eval 0.3.0+kb2` produced fresh descriptive reports for 13 decks including Token Triumph, using inventory export `20261024d`. Do not blend these outputs into the old frozen forecasts.
- **KB:** `mtg-kb-v0.2.1-r20261024d`, 4,961 candidate operations, 446 lossless compiles, 7 quarantined, 61 reported passing KB tests, no human-reviewed semantics. Evaluator reports 54 software tests.

## Coverage and interpretation constraints

- Only **4–31 of approximately 60–65 nonland cards per deck** are fully read by the evaluator (median 10). Coverage differs by deck and ability family, so raw simulated ranking is not comparable on equal terms.
- “Unopposed goldfish lethal by turn 10” is an optimistic modeled upper bound, not Commander multiplayer win probability. Limited blockers, disruption, politics and missing noncombat lines can all materially affect applicability.
- Post-hoc screen thresholds and counts of role tags are descriptive. Do not turn an untested count into a power grade or blanket cut recommendation.
- The model reproduces some commander dependence/contention but **does not reproduce the observed ‘Vraska can't close’ case**. Preserve that real-world observation and use it as a known model validation failure.
- Never treat unreviewed mechanics contracts as fully supported evaluator actions. State source, assumptions, coverage and contradictions with each quantitative comparison.

## Per-game evidence record (fill only from actual reports)

```yaml
record_id:
game_date:
deck_and_exact_version:
commander_companion:
players_and_table_context:
observed_game_turns_result:
observed_successes:
observed_stalls_or_failing_functions:
disruption_and_opponent_actions:
pre_game_prediction_and_frozen_file:
pre_declared_scoring_criterion:
verdict: supported | contradicted | untested
observation_source:
post_hoc_hypothesis: # explicitly separate from observations
model_release_coverage_scenario_seed:
next_discriminating_test:
```

## Validation procedure

1. Freeze list, intended decision, scenario, version, seed and prediction *before* the game.
2. Obtain actual game reports when available; a game that never exercises a forecast's condition is **untested**, not supportive.
3. Score only original predeclared forecasts against unseen play. Separate user observation from explanations written afterward.
4. Compare mismatches to missing typed operations, flawed assumptions, sequencing/mana constraints, alternative win routes, disruption model, and engine/closing architecture.
5. Use ablation, targeted scenario reproduction, holdouts and a new frozen forecast before revising rules or making universal strength claims.
6. For a portfolio transfer, measure donor deck consequences and replacement availability, not only target upside.

## Active backlog

- Reproduce actual Vraska closing failure or bound it as unsupported by current simulator.
- Expand grammar typing for Necrobloom, Limit Break and other sparsely represented decks before interpreting strengths.
- Model commander removal, wipes, interaction through blockers, noncombat outcomes and reliable closing power.
- Audit tapping/sacrifice/population contention, reset state losses and restricted mana.
- Score 2026-10-20 predictions only when independent dated game observations exist.

## Minimum claim disclosure

Include (a) exact source deck version, (b) inventory and model release, (c) typed coverage, (d) assumptions and seed/trials where applicable, (e) measured result and known omitted mechanics, (f) user observations that disagree, and (g) which decision is being informed.

**Sources:** Drive Mtg/handoff evaluator headlines and current state; handoff ZIP `03_evaluator/current_evaluations_20261025/`, `03_evaluator/predictions/PREDICTIONS_2026-10-20.{md,json}`. Maintain frozen predictions intact.
