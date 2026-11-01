# Project purpose: MtG

> The project-level contract. Module `.purpose.md` files describe what each part does. This file says what the whole project is for. A module can meet its own contract and still break this one. That kind of drift is what AEC exists to catch.

@ai-path: project
@ai-role: project_contract
@ai-version: 0.1.2
@schema-version: 0.3
@status: proposed. Pending Zach's review. Wording was reviewed by Kate in the coordination thread, 2026-10-26. 0.1.2 adds P-09 (DIO as a governed source), proposed in D-0020 at Zach's request of 2026-10-31.
@change-procedure: Edit only with Zach's explicit approval. Record the change as a decision event in `decisions/decision_events.jsonl`. Earlier wording is kept in Git history and is never rewritten in place.

---

## P-00: Why this project exists

Help Zach **conceive, discover, construct, understand, evaluate and improve** Commander decks, especially through unconventional interactions and distributed mechanical relationships. The system improves his decisions. It does not replace his judgment.

- The **ontology** (DIO) exists to make possibilities discoverable.
- The **evaluator** exists to make their consequences intelligible.
- The **tools** exist to make those capabilities usable.

**The repository is infrastructure for the Magic project. The Magic project is not an excuse to build infrastructure.** That holds for AEC governance in this repo too.

Extensions are judged by whether they advance a declared project capability. A single extension does not have to produce an immediately better card swap. Ontology work can legitimately widen what is discoverable before anyone knows which discovery will matter. (See challenge C-003 on how this relates to charter v0.1.)

## P-01: One semantic authority per question, and candidates stay candidates

Current Oracle text and the applicable rules govern mechanical truth. The DIO governs how that truth is formally represented. **Verified** semantic contracts are reusable interpretations. Unverified grammar and KB outputs remain **candidates**, whatever their parse rate. Downstream components must not silently introduce competing interpretations.

- **Allowed:** an evaluator, reviewer or test reading Oracle text to check a candidate independently.
- **Not allowed:** a component that derives its own card semantics and uses them as truth without declaring that it does so.
- **Drift test (fixture F-P01):** a downstream module re-parses Oracle text and silently treats its own reading as authoritative, with no reconciliation against the KB contract and no provenance. This must be flagged even though the module's own tests pass. Disagreeing with an unverified KB candidate is **not** drift: it may be a needed correction. Unacknowledged competing authority is drift.

## P-02: Rules-relevant distinctions survive every representation

Object identity, event identity, timing, costs, permissions and state transitions must survive each translation step: Oracle → grammar → DIO contract → KB → evaluator. Separate events are never collapsed because they look alike on the surface.

- **Drift test (fixture F-P02):** a component treats blink (exile and return) as equivalent to bounce and recast.

## P-03: Every claim carries its evidence and its verification state

A mechanics or interaction claim names its source text, its interpretation and its verification state (candidate, ready_for_review or semantic_reviewed), plus any open uncertainty. A claim does not gain authority because something downstream used it successfully. Retrospective explanation, observed games and frozen predictions are three separate validation modes, scored separately.

- **Drift test (fixture F-P03):** a plausible but unsupported synergy passes a loose keyword match. The system must name the unsupported condition, then correct the claim or withhold it.

## P-04: Discovery is not evaluation

The interaction layer describes capabilities and relationships. Evaluators judge usefulness against a deck's stated purpose and constraints. Neither layer silently takes over the other's job. In particular, discovery must not drop mechanically valid interactions because they look weak or uncompetitive.

"Do not equate connectivity with card quality." (DIO)

- **Drift test (fixture F-P04, the hard case):** an interaction-discovery change quietly adds a power or competitiveness filter. Ordinary functional tests still pass. The check must notice that the kind of problem being solved has changed.

## P-05: Recommendations that can be acted on respect the real collection

Actual ownership and deck allocation, read from the canonical inventory Sheet, are authoritative inputs for any recommendation Zach can act on. Hypothetical (unowned) cards and proposed transfers must be labeled as such. Conceptual exploration may go beyond the collection, provided it is labeled.

- **Drift test (fixture F-P05, the positive control):** a recommendation presents an unowned card as available, or mistakes a card's current deck allocation for an ownership restriction.

## P-06: Decision provenance is append-only

Design decisions (card swaps, accepted or rejected theses, criteria changes, scope changes, purpose-contract changes) are recorded as append-only events: who proposed, challenged, corrected, accepted or rejected each one, with the reason and evidence. They are kept separate from KB contract reviews. Events are superseded, never edited.

- **Status: an obligation, partly built.** The store (`decisions/decision_events.jsonl`) and the CI append-only check exist. Nothing yet requires every decision to be logged.

## P-07: Validation modes stay separate

Retrospective reconstruction, observed games and frozen prospective predictions are recorded and scored separately. A good explanation is not a successful prediction. A game scores a prediction only if it exercised the predicted condition, and the deck version and model coverage accompany every comparison.

- **Status: partly built.** The 2026-10-20 predictions are pinned by hash. No scoring tool exists yet.

## P-08: Criteria are versioned and revisable

The system keeps revisions to the questions, objectives and criteria behind decisions, without rewriting earlier judgments. Each criteria version says why it changed and what observation motivated it. A prediction is scored only against the criteria version frozen with it. An approved purpose revision is recorded as a supersession, not flagged as drift.

- **Status: an obligation, not yet built.** `decisions/criteria/` holds only a README so far.

## P-09: The DIO is a governed source, and its discipline binds this repo's governance (proposed, D-0020)

The Deck Interaction Ontology is the project's domain ontology. It is part of what AEC protects here, not just data the code reads.

- **Pinned.** The governing DIO files (v3.1.1, its 2026-10-09 addendum, the A1–A7 compatibility addendum and its registry delta) are `source` records with raw-byte SHA-256 anchors in `.aec/records.jsonl`. A change to those bytes without a new source-record version is drift.
- **Revised only by decision.** A DIO revision (a new version, an addendum, or an accepted candidate such as v3.1.2) is a decision event of kind `dio_revision`, accepted by Zach. The DIO's own rule decides minor vs major (DIO §13).
- **Revisions are impact-checked.** P-01, P-02, P-04 and the accepted decisions that rest on the DIO record that dependency (`depends_on`), so a revision names what must be re-examined. An authorized revision is a rebaseline, not drift (P-08).
- **Its discipline applies one level up.** The DIO's parsimony rules govern AEC artifacts in this repo too: one home per fact, derive the rest (DIO §2, §9); keep negative and unknown results (§7, §14); a new field, check or record type is rejected unless it improves a decision, a compression or a connection (§12.6). This is P-00's "governance features must justify their cost", stated in the ontology's own terms.
- **Drift test (fixture F-P09):** a PR edits a DIO file in `kb/reference_sources/` (for example, renumbers a section or changes the persistence table) without a `dio_revision` decision. `tools/drift_check.py` must fail, even though every other test passes.

_P-06 to P-08 come from Kate's charter amendments 2 to 4, as formalized by build-project Claude in PR #2, and were reconciled here (C-008). P-09 was proposed by the AEC session on 2026-10-31 at Zach's request ("DIO should be incorporated as part of the intentions and purposes and other pieces of AEC"); see `docs/aec/DIO_AEC_REVIEW.md`._

---

## Authority by subject

There is no single ranking. Each kind of authority has its own subject.

| Subject | Authority | Notes |
|---|---|---|
| Ownership and allocation | Canonical inventory Google Sheet | Archive-then-clone: the Sheet id changes with every edit, so consumers resolve the current id and never embed it permanently. Inventory proposals are not physical transfers. |
| Card mechanics | Scryfall Oracle text, the Comprehensive Rules and rulings | Refreshed as an explicit, versioned operation, never inside a query. |
| Formal representation | DIO v3.1.1, its addendum and the compatibility addendum A1–A7 | A valid mechanic the DIO can't express becomes an ontology change proposal, not undocumented compiler semantics. The DIO answers representation questions; revising the DIO is Zach's decision (`dio_revision`, P-09, proposed). |
| Reusable interpretation | Grammar layer and KB contracts, by verification state | Candidates stay candidates (P-01, P-03). |
| Contextual usefulness | Evaluation Protocol v1.0–v1.2 and deck goals | Descriptive while typed coverage is low. |
| Empirical evidence | Observed games and frozen predictions | Scored only against the criteria version frozen with them. |
| Design intent | Zach, recorded in this file, `docs/charter/` and `decisions/` | His decisions remain open to challenge through evidence and the `challenges/` ledger. Challenging a decision never means overriding it silently. |

Operational authority (which tool or agent runs or checks a task) belongs to `AGENTS.md`, `CHARTER.md`, hooks and CI. Operational authority never decides design intent or domain truth.

## Drift fixtures

| Fixture | Contract | How it is checked | State |
|---|---|---|---|
| frozen-predictions hash | P-03, P-07 | `tools/drift_check.py` (mechanical) | automated |
| undeclared semantic authority | P-01 | `tools/drift_check.py` (heuristic: non-owner code reading `oracle_text` without a declared role) | automated (warning) |
| purpose-file source and dependency sync | structural | `tools/drift_check.py` | automated |
| append-only ledgers | P-03, P-06 | `tools/drift_check.py --base <ref>` | automated in CI |
| governed DIO sources (proposed) | P-09 | `tools/drift_check.py` `governed`: anchored bytes in `.aec/records.jsonl` must match | automated |
| decision mirror (proposed) | P-06 | `tools/drift_check.py` `mirror`: a `decision` record in `.aec/records.jsonl` must match the latest status in `decisions/` | automated |
| DIO revision impact (proposed) | P-08, P-09 | `aec impact .aec/records.jsonl .aec/scenarios/<change>.jsonl` (AEC pinned in `tools/aec_upstream.json`) | on demand |
| F-P01 to F-P05 behavioral fixtures | P-01 to P-05 | dissent review plus seeded diffs (see `codex_++/fixtures/README.md`) | specified, not yet automated |

**A passing structural check is not evidence that the purpose survived.** P-04 in particular needs judgment-level review.
