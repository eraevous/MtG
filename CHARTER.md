# Charter: engineering rules

Rules for any change, whether made by a human or an AI. Each rule is written as Rule → Why → Enforced by. "Enforced by" names the actual mechanism. **(review)** means no automated check exists yet, so the rule is checked by human or dissent review.

This replaces the charter inherited from the AEC template, whose rules about S3, FAISS and LLM clients came from an unrelated project. The rules below come from the MTG project's own documented policies (`docs/handoff/00_CURRENT_STATE.md`, `kb/overrides/REVIEW_POLICY.md`, `kb/freeze_check.py`). They are pending build-project Claude's review and Zach's approval.

1. **The inventory Sheet is the authority on ownership and allocation.**
   Why: plans are not moves, and recommendations must reflect real cards (P-05).
   Rules:
   - Never edit the Sheet while querying.
   - Before a structural edit: copy the Sheet, rename the original with a timestamp and `_ARCHIVE`, and edit only the clone.
   - Resolve the current Sheet id; never embed it permanently.
   - Never use an archive as a build input.

   Enforced by: `kb/freeze_check.py guard-input` (refuses archives as inputs), plus **(review)** for the rest.

2. **The KB is derived.**
   Why: one rebuildable source of derived truth, no hand-made forks.
   Rule: rebuild the KB from the Sheet export, the overrides and the Oracle refresh snapshots. Never hand-edit SQLite.
   Enforced by: the KB rebuild tests (`kb/test_acceptance.py`); see C-001.

3. **Candidates stay candidates.**
   Why: parse success is not semantic validity (P-01, P-03).
   Rules:
   - Nothing is auto-promoted to verified, and nothing is mass-approved. Contracts are reviewed by mechanical class and recorded one contract at a time.
   - Semantic review and runtime readiness are separate states.
   - A human `verified` must cite passing test scenarios.

   Enforced by: KB verification states and the append-only review overlay (`kb/test_v02.py` checks that the overlay can't be updated or deleted), plus `drift_check` append-only checks on `kb/overrides/*.jsonl`.

4. **One semantic authority per question.**
   Why: the October 2026 drift happened when the simulator became the authority on card meaning (P-01).
   Rule: code outside `grammar/` and `kb/` may read Oracle text to *verify* a claim, but must not derive and use its own card semantics without declaring `@ai-semantic-role:`.
   Enforced by: `tools/drift_check.py` semantic check (a heuristic that only warns).

5. **Oracle refresh is an explicit, versioned operation.**
   Why: reproducibility; manual corrections must survive refreshes.
   Rule: refreshes write append-only snapshots to `kb/refresh/` and never run inside a user query.
   Enforced by: **(review)**; the refresh replay tests in `kb/test_v02.py`.

6. **Frozen means frozen.**
   Why: predictions only count if they were made before the outcome (P-03).
   Rules:
   - Never edit `predictions/PREDICTIONS_2026-10-20.*`. New predictions go in new, dated files.
   - Score a prediction only against the criteria version frozen with it.

   Enforced by: `tools/drift_check.py` frozen-hash check (an error that fails CI).

7. **Discovery doesn't judge.**
   Why: P-04.
   Rule: discovery code must not filter interactions by power, efficiency or competitiveness. Any such filter belongs to evaluation and must be labeled there.
   Enforced by: **(review)**, using fixture F-P04 (`codex_++/fixtures/`).

8. **Hypotheticals are labeled.**
   Why: P-05.
   Rule: anything recommending a card Zach doesn't own, or a transfer between decks, says so.
   Enforced by: **(review)**, using fixture F-P05.

9. **Standard library only** for project code. Optional heavy dependencies must be guarded.
   Why: the tools have to run anywhere Zach and the agents work.
   Enforced by: **(review)**; there is one known exception (C-004).

10. **Decisions and challenges are append-only.**
    Why: provenance; earlier judgments are superseded, never rewritten (charter amendments 2 and 4).
    Enforced by: `tools/drift_check.py --base origin/main` in CI.

11. **Purpose files stay in sync with their code.**
    Why: a stale contract is worse than none.
    Rule: every purpose file names a real source file, and its `@ai-dependencies` matches that file's local imports.
    Enforced by: `tools/drift_check.py` purpose check (errors for a missing source, warnings for a dependency mismatch).

## Definition of done (per PR)

- `python3 tools/drift_check.py --base origin/main` reports no errors. New warnings are fixed or logged in `challenges/`.
- `python3 -m unittest discover -s tests` and the grammar tests pass. If the PR touches `kb/`, the KB suite passes locally against the data artifacts.
- Behavior changes: the module's purpose file is updated.
- Design changes: a `decisions/` event is appended.
- Mechanics claims carry their verification state.
- The PR description says whether the change touches P-01 to P-05. If it does, which contract, and how the change preserves it.
