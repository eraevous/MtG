# Changelog

## 0.3.0 (2026-10-20): resource ledger, event routing and prospective test (Kate's handoff)

**Why.** Kate accepted 0.1.0 as the baseline and asked for shared infrastructure, not a Vraska script: a ledger of real resource use, engine classes that do not equate "good" with "compounding", closing and recovery scenarios, and predictions frozen before outcomes.

**New modules:**
- `abilities.py`: typed ability records (hook, cost, gates, outputs, cadence, confidence, unread text). These are text projections, because the canonical sheet has no verified DIO Operations yet; event names follow the DIO hooks.
- `engine.py`: a turn engine with object identities and a resource ledger. It keeps apart a creature's own {T} (needs no summoning sickness) from tapping it to pay station or crew (does not), and station from crew. It also handles vigilance, once-per-turn caps and commander tax.
- `routing.py`: event routing and engine classes. Cast and enter are separate hooks.
- `scenarios.py`: three policies; light blockers; destroy and exile wipes; commander removal; attrition; and no-commander ablation, all on the same shuffles.

**Reports:**
- `deck` gains engine routes, the ledger, bottlenecks, policies, closing, resilience and engine coverage.
- `module` gains routes among its cards and per-card throughput.
- `compare` gains paired engine measures.
- `upgrades` gains paired engine damage and post-wipe power for each pick.

**CLI:**
- Options can go after the subcommand.
- `--engine-games` sets the number of engine games per scenario.
- `regress` lists every snapshot difference.

**Corrections:**
- The 0.2.0 "token engine does not compound" flag is retired. Its same-card test was not a compounding test (Kate).
- The exploratory claim that Sharuum has no artifact payoffs is withdrawn. Mechan Assembler is bounded feedback, and Pactdoll Terror is a linear payoff (test R4).
- The remaining 0.2.0 flags are labelled post-hoc.

**Numbers.**
- Access, coverage and module numbers are unchanged.
- The snapshot changes only by the retired flag and a new `engine` block per deck.

**Honest result.** The engine does not reproduce "Vraska can't close". Unopposed, and against light blockers, Vraska is the fastest of the 12 decks, because its 1/1 fliers get past ground blockers.
- What the engine does reproduce (frozen run, 500 games): the largest commander dependence of any deck (median −17 damage by T10 without Vraska), the highest body contention (0.176 of turns T5–T8), and the second-lowest power per body (1.89; Necrobloom 1.67).
- Attrition is weak but not the weakest: Vraska keeps 0.4 of its board power after a wipe plus three commander removals, rank 11 of 12 (TMNT 0.273 is lower).
- Closing failure in that game therefore looks driven by interaction (wipe, repeated commander removal, bigger blockers), not by goldfish speed. This is a post-hoc reading.

**Predictions.** `predictions/PREDICTIONS_2026-10-20.json` (sha256 `18657701bdba2bdc5beb60b4bd66632396b0e55c99fd8bed9bed80fa9bce589c`) freezes pre-game predictions for all 12 decks before any outcome is reported. An earlier file from the same day was replaced before anyone saw it or any outcome existed, when the tie rule (4 or more tied decks make no prediction) was added; it was never scored.


## 0.2.0 (2026-10-19): structural checks after the Vraska game

**Why.** Zach named five causes for Vraska's loss. Before the game, 0.1.0 predicted one and a half of them. It rated the artifact engine "redundant" and the closers "Strong", and it did not model resource competition (see `../vraska-postmortem/VRASKA.md`).

**New `structure.py`, shown in every deck report:**
- **Resource ledger:** claims on untapped creatures and artifacts and on artifact sacrifices (station thresholds, crew N, tap N untapped creatures or artifacts, convoke, improvise).
- **Token feedback:** compounding, reinforcing, multiplied, linear or no payoffs. A trigger and its token must be in the same ability to count as a loop.
- **Closing profile:** creature cards, power 4+, lasting anthems, and engines that need combat damage.
- **Commander dependence:** whether the commander is the engine, the spells that feed it, and the protection that can cover it.
- **Four flags** with ASSUMPTION thresholds set from the 12 current decks. Each measure is ranked against every deck.

**Results on export `828a8970…`:** Vraska raises all four flags; no other deck raises any. These thresholds were set after the game, so this shows separation, not prediction.

**Numbers.** All 0.1.0 numbers are unchanged. The snapshot only adds `structure_flags`.


## 0.1.0 (2026-10-19): first consolidated release

**Consolidation.** Consolidates `capabilities.py`, `evalcore.py`, `access.py` and `validation.py`, plus the three `run_*.py` drivers, into one package with one entry point. Kate's stdlib adapter reader replaces pandas.

**Parity.** Checked against the old modules on export `828a8970…`:
- Same 3,366 card names, the same 12 deck lists, and the same coverage counts, except as listed below.
- Identical TMNT goldfish rates.

**Intended changes in numbers:**
- **Protection reading.** It now recognises "those creatures gain indestructible" (Inspiring Call) and treats shield counters on up to N targets as multi-creature protection.
  - Counter Blitz protection goes from 2 to 3 cards, and its team / survives-a-destroy-wipe protection from 0 to 2 cards.
  - Brigid, Limit Break, Necrobloom and Shanid gain typed protection sources.
- **New role `protection:all_creatures`** for effects that cover every creature.
- **New function `counter_preservation`** (moving or keeping counters when permanents leave). It is flagged by the clause audit and not priced.
- **Clause audit.** It now also flags station, offspring, metalcraft, storied, flurry and crew.
- **Recursion typing.** It ignores "if this spell was cast from a graveyard" bonuses, so a flashback cantrip is not read as recursion.

**Withdrawn recommendation.** VALIDATION.md's Counter Blitz swap (Resourceful Defense → Duty Beyond Death) is withdrawn. The baseline protection was under-read, and Resourceful Defense's counter salvage is not priced.
