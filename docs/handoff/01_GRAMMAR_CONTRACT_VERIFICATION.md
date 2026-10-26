# MTG Grammar & Contract Verification — integration supplement
**Revision:** 2026-10-25 • **Authority:** procedural supplement; does not approve mechanics.

## Purpose and layers

Oracle language is parsed into phrase↔concept templates, which draft a DIO operation contract. The **DIO is the authoritative schema** and the grammar is an inspectable translation/discovery layer. Preserve the distinction between source clause, parsed meaning, rules-valid event, executable runtime action and *deck-value judgment*. Template concept IDs are not DIO primitive hook IDs.

## Required provenance / status per operation

- Card identification (`oracle_id`, printing when disputed), exact Oracle clause, snapshot or retrieval date.
- Dated inventory export/live Sheet identity and allocation evidence.
- Parser versions (grammar/concepts/semantics/drafter), `frame_sha`, `semantics_sha` when derived from grammar, and operation ID if reviewing a Sheet/KB contract.
- Kind, input hooks, result hooks, costs/payment timing, applicable zones, object and player qualifiers, cardinality, replacement mapping, remaining `unread` material, uncertainty and source reconciliations.
- **Independent states:** (a) machine candidate / requires review / rejected / contradicted / semantically verified with scenario IDs; (b) compiler losslessness and runtime support; (c) empirically corroborated or unsupported deck-level effects. A passing test suite cannot automatically promote either other state.

## Review order and method

1. Work in a frozen version with visible Oracle clauses. Start with the 330-operations packet: 79 Token Triumph, 32 other allocated, 219 free; 88 coarse mechanical classes (52 singletons).
2. Set class-level `ok / needs_review / rejected` only for **triage**. Class signatures like `continuous | - -> -` cover semantically different abilities. Use per-row `row_verdict` / `correction` for exceptions; do not mass-approve.
3. Validate whole frames, not just edges or hook match: result(s), origin, target/controller/actor/owner, cost, trigger, alternative branches, replacement rewrites, simultaneity and qualifier scope. Record `unread` not erased information.
4. Semantic `verified` requires explicit passing scenario IDs; assign to the review overlay one contract at a time. Correct the Sheet only under archive-then-clone; rebuild the KB, never alter derived SQLite by hand.
5. Grammar review uses `approve / reject / fix` with whole-frame semantics; bind review to `frame_sha + semantics_sha`. Frame numeric IDs are unstable. A changed meaning stales prior review rather than inheriting approval.
6. Check evaluator support separately. A **lossless compile** is not proof of implemented action support. Require acceptance scenarios before turning operations into active simulated mechanics.
7. For blind accuracy tests, freeze a fresh seed and score original untouched predictions; post-fix regrades are diagnostic only.

## Accepted DIO A1–A7 (refer to original addendum for exact definitions)

- A1 derived `permanent.tapped_for_mana` requires an appropriate {T} mana ability to resolve and produce mana; crew or station tapping does not qualify.
- A2 actor remains separate from object controller, source controller, owner and relation to observer.
- A3 distinguish each-object / one-or-more simultaneous / per-player / per-batch cardinality.
- A4 typed mana and provenance: snow is property of source, any-color vs any-type differs, and colored mana cannot pay {C}.
- A5 `paid_as_cost` vs `on_resolution`, with narrow cost-family primitives/macros.
- A6 `turn.phase.begin` and `turn.step.begin`, legacy `timing.step_begin` alias.
- A7 versioned macro vocabulary (`earthbend`, `offspring`, `dredge`, `crew`, `station`) does **not** imply executable expansion is complete.

## Critical adversarial distinctions

Replacement vs trigger (as-enters clauses are NOT ETB triggers); casting vs entering without casting (Rooms); current object vs underlying card lineage (blink) and state preserving displacement (phasing); token/card distinctions; actor/controller; cost payment vs resolution; stored counters and delayed liabilities; output event vs observed state; and valid-but-harmful interactions when modules compete for tokens, taps or state.

## Unverified work queue (October 25)

- 330 new operations: 233 `extracted_candidate`, 97 `requires_manual_annotation`; confidence 161 medium and 169 low. Review Queue records 169 low-confidence rows in dated workbook.
- 74-row whole-frame grammar review sample; zero reviewed templates. Grammar latest post-precon 5,864/7,145 fully parsed (82.1%); **parsing is not verification**.
- 50-case untouched blind sample seed 4471: 34 wholly correct, 46 structurally correct. Need a *new-seed* sample; fixes to this one are contaminated.
- 41 rulings claims, 733 tests; 2,493 not converted to claims and therefore not confirmations.
- Quarantined printing/token ambiguity: Finch Formation; Rust-Shield Rampager; Thornplate Intimidator.
- Inspect Station threshold lines: Galvanizing Sawship; Lumen-Class Frigate. Inspect additional cost payment representation: e.g. Soaring Stoneglider.
- Drafter 0.4.0 defects: token-granted quoted ability inherits parent trigger; 36 “as land enters reveal/pay” replacements drafted as ETB triggers.

## Minimal criteria before calling an operation verified

Exact source and identity; fully reviewed event/results/roles/qualifiers/costs/alternatives; no material unaccounted `unread`; scenario IDs and passing mechanical tests; reviewer identity/version/hash; support and exclusions explicitly bounded. If not met, classify as candidate, blocked, or needs_review, and state what would change that judgment.

**Sources:** DIO v3.1.1; accepted compatibility addendum; handoff README; KB release notes; handoff ZIP `04_mechanics_review_packet/` and `05_grammar_layer/{REPORT.md,DATA_DICTIONARY.md,review/,validation/}`.
