# DIO and AEC: a comparative review

Status: **review** (2026-10-31, claude-aec). Zach accepted both proposals, D-0020 and D-0021, on 2026-11-01. The rest is the agent's analysis, not decisions. The proposals it leads to are D-0020 and D-0021 in `decisions/decision_events.jsonl`, and the open questions are C-020 to C-022 in `challenges/ledger.jsonl`. Zach decides.

Asked by Zach on 2026-10-31: "a comparative review between DIO and the development engine system ... DIO should be incorporated as part of the intentions and purposes and other pieces of AEC ... update this project's development kit with new AEC branches and reconcile."

**What was compared**

| | Version read | Where |
|---|---|---|
| DIO | v3.1.1 (2026-10-06), its 2026-10-09 addendum, compatibility addendum A1–A7 (`DIO-3.1.1-kb-addendum-0.1`) | `kb/reference_sources/`, `kb/addendum/` |
| AEC upstream | `eraevous/AEC` main at `4decef6` (2026-10-31): v0.3 CLI, WP0 self-reconciliation, WP-S source anchors, approved architecture, failure-mode catalogue, WP1A spec | `README.md`, `CHARTER.md`, `.specify/memory/constitution.md`, `docs/architecture.md`, `docs/reasoning-vocabulary.md`, `docs/failure-modes.md`, `src/aec/` |
| AEC in MtG | the layer forked on 2026-10-26 from AEC `bdf3f34` (2025-10-22) and grown here since | `CHARTER.md`, `VISION.md`, `codex_++/`, `decisions/`, `challenges/`, `tools/drift_check.py` |

**Which AEC branches.** Zach said "new AEC branches". AEC's own branches (`case_study`, seven `codex/*` visualisation branches) are 2025 Data-Guide work and are already copied into MtG; none is newer than the fork. The newer work is the 36 commits merged into AEC `main` from the `speckit/002` to `speckit/005`, `aec/change-impact-v0` and `docs/*` branches between 2026-10-27 and 2026-10-31. Those are what this review reconciles. If Zach meant something else, the reconciliation in §5 is the part to redo.

---

## 1. Two ontologies at two levels

The DIO is an ontology of **what cards can do together**. AEC's reasoning vocabulary is an ontology of **what conclusions about the work rest on**. They were built separately, a month apart, by the same owner, and they make the same moves:

| Concern | DIO (cards) | AEC (development) | Fit |
|---|---|---|---|
| Unit of meaning | Operation: requirement groups, amplifiers, result (§5) | Record: claim, requirement, evidence, decision with typed relations | parallel |
| What must hold | **Gate rule**: every requirement group, any one alternative; an amplifier is never a requirement (§1, §12.1) | `depends_on` is necessary; `supports` counts toward a claim but never establishes it | **AEC is weaker here** (§2.1) |
| Identity through change | **Persistence rule**: does the same object continue? If so its state persists by default (§1, §6.4) | `id@version` pinning; `supersedes`; `rebaseline` vs `stale`; `observed_on` evidence needs an applicability review, never invalidation | parallel |
| Status of a link | connection `status`: verified / conditional / candidate / incompatible / unknown; `strength`; `polarity` (§7) | evidence `tier`: candidate / reviewed / observed / prospective; impact dispositions | parallel, but AEC has no polarity |
| Keep the failures | "Keep negative, mixed, broken and unknown connections; they prevent the same false inference twice" (§7, §14) | append-only records; `challenges/`; rejected alternatives (failure mode S8) | parallel |
| Description vs judgment | The ontology "does not decide that a card is good"; evaluation, portfolio and Kairos–GATE keep their own objectives (§2) | Core establishes structural facts; reviewer agents interpret; only Zach accepts. "A passing check is not purpose" | parallel (P-04 is the shared root) |
| One home per fact | "Record each fact once. Derive the rest" (§2, §9) | One authority per subject; generated edges are not authority; "collapsing different relationships into one meaning is not allowed" (architecture) | parallel |
| Parsimony | "Open precision only when it changes the answer"; §12.6 anti-overengineering: a new field is rejected unless it improves a recommendation, compression or connection | "Earn additions" (CHARTER 6, constitution V); failure mode P7, governance outgrows the work | parallel |
| Claim labels | RC / OC / NC / IC / RU / DR on every rules claim (§12) | candidate / reviewed / observed / prospective; MtG's six KB verification states | parallel |
| Tests | Acceptance tests are normative; "a conforming implementation distinguishes ..." (§12) | Every check has a violating fixture and a clean decoy (constitution III) | parallel |
| Versioning | Minor adds vocabulary; major when the gate or persistence rule changes meaning; add a primitive only when nothing existing can describe it (§13) | MAJOR/MINOR/PATCH on the constitution; committed records change only by authorized revision | parallel, but **not linked** (§2.2) |
| Who may change it | Not stated in the DIO | `authority` records by subject; `authorized_by` is a claim, not consent | **DIO relies on the project** (§2.2) |
| Maturity | "A loop is verified only when costs, capacities, timing, state restoration and termination all close, not when the graph returns to its start" (§8) | "evidence supporting a claim does not establish it; a passing test does not satisfy a requirement; a satisfied requirement does not show the purpose was achieved" | same lesson |

The resemblance is not decoration. Both encode the October 2026 failure Zach observed twice: plausible intermediate results presented as justified conclusions. In decks that was synergy mistaken for advantage and apparent routes that could not execute ("between a quarter and nearly half", DIO §7). In development it was the simulator growing its own card parsing while every test passed (VISION, "Observed").

## 2. Where they differ, and what each can lend the other

### 2.1 The gate rule would sharpen AEC's `weakened` (DIO → AEC)

AEC classifies a conclusion as `weakened` when it "lost one support but keeps others", and as `unjustified` when "no remaining support of that kind holds it up". It counts supports. The DIO would ask a sharper question: **which requirement group did the lost support belong to?** A claim like "Vraska recovers from wipes" has at least two groups: a recursion route exists (alternatives: Duty Beyond Death, a reanimation spell, ...) and the board can pay its cost. Losing one alternative of a group with others left is `weakened`. Losing the last alternative of any group is `unjustified`, even when supports in other groups remain. Today AEC can't tell these apart, and the reasoning vocabulary already says so ("counting supports cannot tell").

The DIO also separates a requirement from an **amplifier**: evidence that only makes a claim stronger (a larger sample, a second game) is not a requirement, and losing it should never make a conclusion `unjustified`.

This is an upstream AEC proposal, not something MtG can change. It is recorded as C-022 so it reaches the AEC hub.

### 2.2 The DIO has no change procedure inside the AEC layer (AEC → DIO)

The DIO says how it versions (§13) but not who may revise it, and the MtG AEC layer names it as an authority (P-01, "Authority by subject") without pinning it. Concretely, before this PR:

- The DIO files in `kb/reference_sources/` could be edited in any PR and no check noticed. `drift_check` pins the 2026-10-20 predictions, not the ontology every contract is drafted against.
- `decisions/README.md` had no decision kind for an ontology revision. The v3.1.2 candidate (Kate, 2026-10-17) and the addendum A1–A7 (accepted 2026-10-22) were decided in threads, not in the decision log.
- No record linked P-01, P-02, P-04 or any accepted decision (D-0008, D-0011, D-0014 role definitions) to the DIO version they assume. So when DIO v3.1.2 is accepted, nothing says what must be re-examined.

That third point is exactly the question AEC v0 was built for: *something changed; which conclusions are no longer justified, and which changes were legitimate revisions?* The DIO is the most consequential thing in this project that can change, and it was the one thing AEC did not watch.

### 2.3 Polarity has no counterpart in AEC

The DIO keeps validity and polarity apart: blink plus +1/+1 counters is a valid connection with negative polarity. AEC has `contradicts`, which is evidence against a claim, but nothing for "this dependency holds and hurts". In development terms, that is a dependency that is real and harmful (a module that relies on another's bug). Worth knowing, not worth building yet. Left as an observation.

### 2.4 Derived, never stored, applies to governance too

DIO §9 says anything computable is derived, because storing it "creates a second copy of a fact that can drift". The AEC layer here has a few such copies:

- Decision status lives in `decisions/decision_events.jsonl`. Upstream AEC keeps decisions as `decision` records in `.aec/records.jsonl`. Adopting upstream naively would create a second home for every decision.
- The DIO version is written by hand in `CHARTER.md`, `codex_++/project.purpose.md`, `docs/DOCUMENT_PRECEDENCE.md`, `docs/AGENT_GUIDE.md` and `mtgtools/dio.py`.
- AEC's `examples/mtg-pilot/records.jsonl` restates MtG's P-01 (`@1`, `@2`) from 2026-10-26. It is already behind MtG's current wording.

The proposal in §4 keeps one home per fact: decisions stay in `decisions/`, and `.aec/records.jsonl` mirrors only the decisions that depend on the DIO, with `drift_check` failing when a mirror disagrees with the log.

## 3. Where the DIO sits in AEC's architecture

AEC's approved architecture keeps five representations apart (a: code topology, b: co-change, c: reasoning records, d: semantic contracts, e: coordination). For this project the DIO is a sixth thing that architecture does not have: a **domain ontology** that governs the meaning of the data the code handles. It is neither a module purpose file (d) nor a reasoning record (c). The fitting AEC concepts are:

- the DIO files are `source` records under an `authority` for the subject `formal-representation`;
- P-01, P-02 and P-04 are requirements that `depends_on` those sources;
- a DIO revision is a `revise` change event, authorized only by Zach (and Kate jointly, as with A1–A7, if Zach says so);
- `aec impact` then answers which contracts, decisions and purposes need review.

The upstream architecture lists "implementation drift: (a) vs (d)". MtG adds **semantic drift: code vs the domain ontology**. That is the drift VISION.md describes, and drift_check's `semantic` heuristic (code reading `oracle_text` outside `grammar/` and `kb/`) is its only detector so far. This is worth carrying to the AEC hub as a general point: a project with a domain ontology needs AEC to treat it as a governed source, not just as data (C-022).

## 4. What this PR does (all proposed)

| Change | Why | Where |
|---|---|---|
| `.aec/records.jsonl`: authorities by subject; the DIO, its addendum, A1–A7 and the Grammar Registry as `source` records with raw-byte SHA-256 anchors; P-00 to P-08 (and the proposed P-09) as provisional purpose/requirements, with the DIO-dependent ones `depends_on` the DIO; the accepted decisions that rest on the DIO, mirrored | Puts the DIO into AEC's records, so `aec check` verifies the files and `aec impact` can answer what a DIO revision touches | `.aec/` |
| `.aec/scenarios/dio_v312_adopted.jsonl` | A worked change event: adopting the v3.1.2 candidate, authorized and unauthorized | `.aec/scenarios/` |
| `drift_check` gains `governed` (pinned DIO sources) and `mirror` (decision status in `.aec` matches the log) checks, each with a violating fixture and a decoy | A DIO edit becomes a visible decision, not a silent diff; the mirror can't drift | `tools/drift_check.py`, `tests/test_drift_check.py` |
| Proposed **P-09**: the DIO is a governed source, revised only by decision, and its parsimony rules bind this repo's governance too | Zach's ask that the DIO be part of AEC's purposes | `codex_++/project.purpose.md` |
| `dio_revision` decision kind | So the next DIO change lands in the log | `decisions/README.md` |
| AEC upstream pinned at `4decef6`; CI runs `aec check` on MtG's records from that commit; `AGENTS.md`, `CHARTER.md`, `VISION.md` updated | Brings the kit up to AEC v0.3 without vendoring AEC's code into this repo | `tools/aec_upstream.json`, `.github/workflows/ci.yml` |

## 5. Reconciling with upstream AEC: adopt, adapt, decline

| Upstream piece | Verdict | Reason |
|---|---|---|
| Reasoning records + `aec check` / `aec impact` (v0.1–v0.3) | **adopt** for the DIO slice | It answers the DIO-revision question directly (§2.2) |
| Source anchors (WP-S) | **adopt** | Raw-byte SHA-256 + locator is the right shape for pinning the DIO and quoting sections |
| `aec init` / `import-purpose` | **adapt** | Run once here (0 errors, 28 module purpose files imported in a scratch copy); not committed, because the 28 provisional records would duplicate `codex_++/purpose_files/` and need re-import on every purpose edit. Revisit if `aec context` (WP2A) lands |
| `aec edges` snapshot | **adapt** | 9,357 edges for this repo. Generated in CI, never committed (upstream says never hand-edit; committing it would churn every PR) |
| Constitution / Spec Kit | **decline for now** | MtG does not use Spec Kit. Its CHARTER already plays the constitution's role. Adopting Spec Kit is a scope decision for Zach, and P-00 says governance must earn its cost |
| "Every check has a violating fixture and a clean decoy" (constitution III) | **adopt** in CHARTER | MtG already said "not called enforced until a violating fixture fails"; the decoy half was missing |
| "`authorized_by` is a claim, not verified consent" | **adopt** in CHARTER | Failure mode P5 (misread authority); MtG relays Kate's messages, so this matters here |
| Failure-mode catalogue (S1–S10, P1–P8) | **reference** | MtG's F-P01 to F-P05 fixtures map onto S4/S5/P4/P5; no new machinery |
| Vendoring `src/aec/` into MtG | **decline** | It would be a second copy of AEC that drifts (DIO §9 again). Pin a commit and clone it in CI instead |

## 6. Dissent review (AGENTS.md, Drift)

This PR changes the AEC layer's responsibility (it now watches the DIO) and adds a records file, so it is a Drift trigger.

1. **Which purpose might it violate?** P-00: "The repository is infrastructure for the Magic project. The Magic project is not an excuse to build infrastructure." And CHARTER 9 / DIO §12.6: additions must improve a decision capability.
2. **Evidence for the concern.** No deck decision changes because of this PR. It adds a records file, two checks, a pinned upstream and a CI step. Zach's last two hours of work were about a Merfolk deck and counter identity, not governance.
3. **Counter-evidence.** Zach asked for it. The DIO is about to change (v3.1.2 candidate pending; the counter-identity release in "Fix problems from Merfolk deck test" leans on the DIO's polarity rule), and today nothing would say which accepted role definitions, P-contracts or KB contracts that change touches. The added records are 30-odd hand-written lines, and the checks are about 60 lines of standard library code.
4. **If the concern is right.** The records will go stale like the AEC pilot example did, and the CI step becomes noise. The signal to watch: nobody runs `aec impact` when the DIO next changes. If so, drop `.aec/` and keep only the `governed` pin in `drift_rules.json`.
5. **What to decide.** Zach: accept or reject D-0020 (P-09 and the governed DIO) and D-0021 (adopt the AEC v0.3 records slice, pinned upstream). Test: the next DIO revision, run through `.aec/scenarios/`, should name the affected decisions before anyone has to remember them.

_This review was written by the same session that made the changes. A fresh-context reviewer would reduce anchoring; it has not been run._
