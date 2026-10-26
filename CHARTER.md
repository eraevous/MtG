# 🛠️ MtG Charter: Principles to Build (and Review) By

@ai-version: 0.1.1-draft · supersedes the inherited Cognitive-Scaffolding charter (S3, FAISS, Typer, LLM-client rules) · status: proposed, pending Zach's review

_Authored by build-project Claude (PR #2), which owns the MTG invariants. Reconciled into the repo shell by the AEC session (C-008): P-01 amended and authority scoped by subject, per Kate's review; `exists` items point at checks that are actually in this repo; rules 11–13 carried over from the shell charter. Build-project Claude is to review._

Each principle is Rule → Why → Enforce. **Enforce** says what will make a violation fail, with its status: `exists` (a check runs today), `planned` (to build), or `review` (a human or the dissent review checks it). A rule is not called enforced until a violating fixture has been shown to fail.

## Authority by subject (not a single ranking)
Each kind of authority has its own subject; see the table in `codex_++/project.purpose.md`. Inventory Sheet → ownership and allocation. Scryfall Oracle, Comprehensive Rules and rulings → card mechanics. DIO v3.1.1 and accepted addenda A1–A7 → formal representation. Grammar layer and KB → reusable interpretation, by verification state. Evaluation protocols and deck goals → contextual usefulness. Observed games and frozen predictions → empirical evidence. Simulation → provisional only. Inventory never outranks Oracle on mechanics, and Oracle never outranks the Sheet on ownership.
Design authority (purpose, criteria) is Zach's. It is recorded in `codex_++/project.purpose.md`, VISION.md and `decisions/`, and it can be challenged through evidence (`challenges/`). Operational authority (who runs and checks a task) belongs to tools, hooks and CI.

1) No Silent Competing Card Semantics (P-01, as amended)
- Rule: Oracle text and the rules govern mechanical truth; the DIO governs its representation. Verified contracts are reusable interpretations. Unverified grammar and KB output remains a candidate. No module may silently introduce its own interpretation as authoritative or hard-code card behaviour on the side. Reading Oracle text to *verify* a candidate is allowed, and so is *disagreeing* with an unverified candidate, provided the disagreement is recorded for review.
- Why: Parallel interpretations drift and contradict each other silently.
- Enforce: exists (warning, heuristic): `tools/drift_check.py` semantic check (oracle_text + regex outside grammar/ and kb/ without `@ai-semantic-role:`). review: dissent review on any new card-specific logic.

2) Rules Distinctions Survive (P-02)
- Rule: Representations keep distinctions the rules make: blink ≠ bounce, sacrifice ≠ destroy, actor ≠ controller (A2), tapped-for-mana (A1), typed mana (A4), copy vs. token, and so on. Information loss must never yield certainty.
- Why: Most past analysis errors were invented or merged rules interactions.
- Enforce: exists: KB lossy-compile gate (only lossless compiles get runtime certificates; `kb/test_v02.py`, `kb/test_acceptance.py`). `invariants_v021d.py` is named by the build project but is not in the imported release, so it is to be imported. planned: a fixture pair per distinction that must produce different outputs.

3) Claims Carry Evidence and a Verification State (P-03)
- Rule: Every mechanics or deck claim names its evidence and its state: candidate, ready_for_review, semantic_reviewed, runtime-ready, quarantined, rejected or review_stale. Semantic review and runtime readiness are separate. A contract never gains authority because the evaluator consumes it successfully. Nothing is auto-promoted or mass-approved. A human `verified` review must cite passing scenarios.
- Why: Generated contracts look authoritative. Zero of 4,961 are human-reviewed today.
- Enforce: exists: KB verification states, append-only review overlay (`kb/test_v02.py` rejects update and delete; `tools/drift_check.py` append-only check on `kb/overrides/*.jsonl` in CI), scenario-backed reviews (61 KB tests; 60 pass here, see C-001). planned: a behavioural test that the evaluator refuses or flags unverified input in decision-grade output.

4) Discovery Stays Separate from Judgment (P-04, amendment 1)
- Rule: Exploratory interaction hypotheses (between cards, modules or whole decks) may precede verification and need not become KB contracts. Only decision-grade claims pass the verification gate. Interaction graphs describe what might connect. They never rank card quality on their own.
- Why: Judging too early kills unconventional discoveries. Treating discoveries as verdicts produced "synergy mistaken for advantage".
- Enforce: planned: output schemas that tag every claim `exploratory` or `decision_grade`; a behavioural check that no ranking is computed from graph metrics alone. review.

5) Respect the Actual Collection (P-05)
- Rule: Recommendations use only owned cards, resolved against the current canonical Sheet. Consumers resolve the live Sheet id and never embed it. Plans are not moves: proposals never change physical allocations. Sheet edits follow archive-then-clone.
- Why: Inventory and version errors were a recurring failure, for example the Shanid lookup that missed 41 legends.
- Enforce: exists: KB manifest names its source Sheet id. planned: a test that recommendation output only names owned, available copies; a check for hard-coded Sheet ids.

6) Decision Provenance (amendment 2)
- Rule: Decisions (card swaps, accepted or rejected theses, criteria changes) are append-only decision events: who proposed, challenged, corrected, accepted or rejected the change, with the reason, the evidence and links to the affected contracts. These are separate from KB contract reviews.
- Why: Zach acted as the validator, and his reasons were the most valuable and most often lost data (the Factory's September 28 rationale).
- Enforce: exists: `decisions/decision_events.jsonl` (schema in `decisions/README.md`); `tools/drift_check.py --base` fails CI when a past line changes. planned: schema validation of each event.
- Status: this is an obligation, not a finished system. The store and the append-only check exist; nothing yet requires every decision to be logged.

7) Separate Validation Modes (amendment 3)
- Rule: Retrospective reconstruction (Factory), observed games (Dina, Vraska, Shanid) and frozen prospective predictions are recorded and scored separately. A successful explanation is not a successful prediction. Vraska cannot become an independent validation case retroactively. A game scores a prediction only if it exercised the predicted condition, and deck version + model coverage accompany every comparison.
- Why: Post-hoc fit is easy and was mistaken for validation.
- Enforce: exists: `predictions/PREDICTIONS_2026-10-20.*` pinned by sha256 in `tools/drift_rules.json` (CI fails on any edit), with the scoring rule fixed in advance. planned: a scoring tool that refuses unfrozen predictions.

8) Versioned, Revisable Criteria (amendment 4)
- Rule: The system preserves revisions to the questions, objectives and criteria governing decisions, without rewriting earlier judgments. Each criterion is versioned with why it changed, the observation that motivated it and which judgments it supersedes. A prediction is scored only against the criteria version frozen with it. A legitimate, approved purpose revision is recorded as a supersession, not flagged as drift.
- Why: Zach repeatedly changed the question when a model answered a less useful one. The "quality" measure was added after the Vraska game.
- Enforce: planned: criteria registry (`decisions/criteria/`, a README only so far) with version ids referenced by every prediction and decision event.
- Status: an obligation; not yet implemented.

9) Extensions Earn Their Place
- Rule: Dimensions, metrics and subsystems enter the core only after improving a demonstrated decision capability. Governance features must justify their cost too.
- Why: The tools got ahead of how they connect to decisions; governance can become overhead.
- Enforce: review: dissent review at subsystem introductions, responsibility changes and spec revisions (not at every module switch).
- Open: C-003. Kate proposes two stages: *experimental admission* (advances a declared capability, coherent and testable) and *promotion to the core* (evidence of improvement). Zach decides.

10) Budgeted, Bounded Work
- Rule: Model calls, review frequency and repeated semantic extraction have limits. A task can finish without an unbounded audit cycle.
- Why: Cost control and finishing working software.
- Enforce: planned: budget tracker on model calls; hooks give fast feedback, and CI (independent of Claude Code) is the backstop.

11) The KB Is Derived; Oracle Refresh Is Explicit
- Rule: Rebuild the KB from the Sheet export, the overrides and the Oracle refresh snapshots. Never hand-edit SQLite. Oracle refreshes are explicit, versioned operations that write append-only snapshots to `kb/refresh/`, never run inside a query, and never erase manual corrections.
- Why: One rebuildable source of derived truth.
- Enforce: exists: KB rebuild and refresh-replay tests (`kb/test_acceptance.py`, `kb/test_v02.py`). Byte-identical rebuild fails in this environment (C-001).

12) Standard Library Only
- Rule: Project code uses only the Python standard library. Optional heavy dependencies must be guarded.
- Why: The tools must run wherever Zach and the agents work.
- Enforce: review. One known exception: `review_packet/scripts/extract.py` imports openpyxl (C-004).

13) Contracts Stay in Sync with Code
- Rule: Every `codex_++/purpose_files/*.purpose.md` names a real source file, and its `@ai-dependencies` matches that file's local imports.
- Why: A stale contract is worse than none.
- Enforce: exists: `tools/drift_check.py` purpose check (error for a missing source, warning for a dependency mismatch).

## ❌ Anti-Patterns to Ban
- Hand-editing the KB, or any derived artifact, instead of rebuilding it from sources.
- Promoting contracts by class, in bulk, or because a downstream tool accepted them.
- Rankings or "best card" claims computed from graph density or simulation alone.
- Hard-coded Sheet ids, card counts or "free card" claims without a dated inventory reference.
- Rewriting past predictions, decisions or criteria in place.
- Calling a rule enforced because a hook config exists, without a failing fixture.

## ✅ Definition of Done (per PR)
- `python3 tools/drift_check.py --base origin/main`: no errors; new warnings fixed or logged in `challenges/`. `python3 -m unittest discover -s tests` and the grammar tests pass; KB suite locally if `kb/` changed.
- Claims in outputs carry evidence + verification state; exploratory vs. decision_grade is tagged.
- No new card-text interpretation outside grammar/KB.
- Inventory resolved live; no plans written as moves.
- Decision events / criteria versions appended, not edited, where a decision changed.
- Purpose file updated or intent file added (G-13); tests pass; any new Enforce check has a violating fixture that fails.
