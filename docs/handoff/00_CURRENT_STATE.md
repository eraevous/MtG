# MTG project: current state (2026-10-25)

This is a self-contained snapshot of Zach's Magic: The Gathering inventory and mechanics project. It covers what exists, what changed most recently, what is still unverified, and what is waiting on decisions. All counts are as of 2026-10-25.

## 1. Architecture

The pipeline runs in this order:

1. **Inventory**: the Google Sheet "MTG Master Inventory — Canonical" (live id `1f83bN2ULQmXJQkkRL_JxPvzq9gWMYwLFobhATCjkCpU` as of 2026-10-25).
2. **Oracle KB**: a SQLite database rebuilt from the Sheet plus a Scryfall Oracle refresh.
3. **Verified DIO contracts**: one per card ability.
4. **Roles and interaction graphs.**
5. **Optional simulation**, with StateFrames as a downstream consumer.

Rules that govern all work:
- **The Sheet is the inventory authority.** Before any edit, the Sheet is copied, the original is renamed with a timestamp and "_ARCHIVE" and moved to an archive folder, and only the clone is edited. The clone gets a new Drive id each time.
- **Oracle text from Scryfall is the rules authority.**
- **The KB is derived.** It is rebuilt from the Sheet and never hand-edited.
- **Review rules:**
  - Nothing is auto-promoted to verified, and contracts are never mass-approved. They are validated by mechanical class.
  - Semantic review and runtime readiness are separate verification states.
  - A human `verified` review must cite passing test scenarios.

## 2. Inventory (as of 2026-10-24)

- **Size:** 3,520 Collection rows, 5,802 physical copies and 3,512 owned card names.
- **Decks:** 13 current decks, all 100 cards. The newest is the Token Triumph precon (set SCD, commander Emmara, Soul of the Accord, GW Selesnya), recorded as an intact, allocated deck.
- **Added on 2026-10-24** from photos: batch 1 (54 copies, 31 new names) and batch 2 (222 copies, 57 new names), plus the precon (100 cards, 60 new names).
- **Open identification items:**
  - The collector numbers of the precon's SCD basic lands are unresolved.
  - Two collector numbers were inferred, not read: Strix Lookout FDN 52 and Mountain TMT 194.
- **Plans are not moves.** Deck plans and backfill proposals never change physical allocations.

## 3. Mechanics extraction pass (2026-10-24, newest work)

- **Scope.** The pass targeted the 412 owned cards that had no rows in Mechanics · Operations. Their operations came from the Oracle grammar layer (described below), mapped onto the Sheet's 18 Operations columns and its 43-hook vocabulary.
- **Result.** It produced 330 candidate operations on 266 cards. The other 146 cards have nothing to extract, because they are keyword-only, vanilla or basic lands.
  - 233 rows are `extracted_candidate` and 97 are `requires_manual_annotation`.
  - Confidence is medium for 161 rows and low for 169.
- **Sheet changes.** 151 new Units rows were added and 115 existing ones updated. 169 Review Queue rows (rows 713–881) hold all the low-confidence operations.
- **Review packet.** The packet for Zach groups the 330 operations into 88 mechanical classes (signature `kind | hook -> produces`), 52 of them single-card.
  - Largest classes: continuous with no hook (93), spell-resolve effects (32), enters-the-battlefield replacements (23), mana abilities (19), token-making activated abilities (10) and ETB triggers (9).
  - Review order: Token Triumph cards (79 operations), then other allocated cards (32), then free cards (219).
- **Status.** Not reviewed yet. Zach is giving class-level verdicts.

## 4. SQLite knowledgebase

- **Current release:** v0.2.1, data refresh r20261024d (built 2026-10-25). It holds 4,961 candidate operations/contracts, up from 4,631. Of those, 446 compile losslessly and 7 are quarantined. All 61 tests pass.
- **Verification states:** ready_for_review, blocked, quarantined, semantic_reviewed, rejected and review_stale. Runtime certificates are issued only for lossless compiles. Only mechanically supported actions reach the evaluator.
- **Review status:** no contract has been human-reviewed yet. The review overlay is empty.
- **Oracle reconciliation:** 12 append-only records. They cover sheet errors with quarantined contracts, 3 excluded placeholder names and 3 accepted aliases.
- **DIO addendum A1–A7** is recorded:
  - A1: tapped_for_mana facet.
  - A2: actor kept. Kate overruled collapsing actor into controller, so both relations stay.
  - A3: cardinality.
  - A4: typed mana.
  - A5: act_time.
  - A6: turn.step/phase.begin.
  - A7: keyword macros.

## 5. Oracle grammar layer (v0.2, 2026-10-22)

- **What it is:** a language layer between Oracle text and DIO. It is an inspectable phrase↔concept template registry learned across all of Scryfall, and every ability compiles to a DIO contract (6,858 owned abilities). The headline metric is the % of collection abilities expressible through reviewed templates.
- **Parsing:** 82.0% of collection abilities parse fully. 0% are reviewed. Reviewing the top 300 templates would cover 64.5%.
- **Blind sample (seed 4471):** 68% of contracts were fully correct and 92% structurally correct. The next sample needs a new seed.
- **Validation:**
  - Train sets: TLA, TLE, EOE, EOC, TMT and TMC. Held out: Star Trek (TRK/TRC).
  - Rulings checks: 41 claims, 733 tests, 0 contradictions.
  - 2,493 rulings are not yet converted, and unconverted rulings never count as confirmation.
  - The station tests transferred to the held-out cards (63 of 63 pass).
- **Discovery:** 2,125 two-card loop candidates in the collection, of which only 11 are "guaranteed".
- **Known drafter bugs** (0.4.0):
  - An ability granted to a token in quoted text inherits the parent card's trigger hook.
  - 36 "As this land enters, you may reveal/pay" clauses are drafted as ETB triggers instead of as-enters replacements.

## 6. Evaluator (mtg_eval 0.3.0)

- **What it does:** card, deck, module, compare, upgrades, build, inventory, transfer and portfolio queries, with a turn engine, a resource ledger and scenarios. 54 tests pass.
- **What it shows:** it reproduces commander dependence and card contention, but not the observed "Vraska can't close" result. Ability-typing breadth is the main limitation.
- **Frozen predictions:** a set of deck predictions from 2026-10-20 is frozen, to be scored as supported / contradicted / untested when game results come in.

## 7. Open decisions and next steps

1. **Mechanics packet review** (Zach). Class verdicts, then row exceptions, applied one contract at a time.
2. **Offspring identity.** The Sheet rows for Finch Formation, Rust-Shield Rampager and Thornplate Intimidator point at token printings, and their contracts are quarantined. Are the owned copies the cards or the tokens?
3. **Station modelling.** Station threshold lines (Galvanizing Sawship, Lumen-Class Frigate) were extracted as continuous operations with the threshold as a requirement. Is that acceptable?
4. **Additional costs.** These are recorded as `payment` on the cast operation, not as separate operations (for example Soaring Stoneglider).
5. **Grammar template review.** A 74-row sample is waiting for whole-frame semantic review.
6. **Drafter fixes.** The next drafter version should fix the two bugs above.
7. **Blocked access.** magic.wizards.com and media.wizards.com are blocked from the build environment, so release notes and the Comprehensive Rules text can't be fetched.
8. **End goal.** Judge what a chain of interactions produces and whether that matters in a deck, with no or few tutors.
