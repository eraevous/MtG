# Module: project (MtG Deck Behavioral Model)
> Project-level purpose contract. It states the system's objectives and invariants. Module contracts state local responsibilities. A module can satisfy its own contract and still violate this one, and that is the drift AEC exists to catch.

@ai-path: project
@ai-source-file: (project-level; no single source file)
@ai-role: purpose-authority
@ai-intent: Help Zach conceive, explore and compile Commander decks from his owned collection, with verified mechanics, traceable decisions and revisable criteria.
@ai-version: 0.1.0
@schema-version: 0.3
@ai-risk-pii: low (personal collection data only)
@ai-risk-performance: medium (KB rebuild, grammar compile, evaluator engine games)
@ai-dependencies: inventory Sheet (live id resolved at run time), Scryfall Oracle + rulings, DIO v3.1.1 + addenda A1–A7, grammar layer v0.2, mtg-kb v0.2.1, mtg_eval 0.3.0+kb2
@ai-used-by: Zach; Kate (coordination); Claude agents (build/execution)
@ai-downstream: deck charters, interaction maps, decision ledger, frozen predictions

## 🎯 Intent & Responsibility
See VISION.md. The core (Decision Model) explains why a contribution matters to a given deck under versioned criteria. It orchestrates the existing inventory, grammar, KB and evaluator and does not reimplement them.

## Project contracts
| ID | Contract | Authority | Verification | Change procedure |
|---|---|---|---|---|
| P-01 | One authoritative card semantics | Oracle → grammar → DIO | boundary check (planned) | ontology-change proposal; the compiler never invents semantics |
| P-02 | Rules distinctions survive | DIO + addenda | lossy-compile gate (exists), distinction fixtures (planned) | addendum reviewed by Zach + Kate |
| P-03 | Claims carry evidence + verification state | KB verification states | review overlay + tests (exists) | Zach review citing scenarios |
| P-04 | Discovery separate from judgment | VISION | claim tagging (planned) | decision event |
| P-05 | Respect the actual collection | inventory Sheet | owned-only test (planned) | archive-then-clone Sheet edit |
| P-06 | Decision provenance, append-only | decision ledger | append-only test (planned) | none: events are never edited, only superseded |
| P-07 | Separate validation modes | frozen predictions | sha256 freeze (exists) | new frozen file |
| P-08 | Versioned, revisable criteria | Zach (design authority) | criteria registry (planned) | new criteria version with rationale |

## 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|---|---|---|---|
| in | inventory export | xlsx / Sheet API | owned copies, deck allocations |
| in | KB release | SQLite + manifest | candidate/verified contracts with states |
| in | criteria version | registry entry | what "better" means for this question |
| out | deck charter | markdown/JSON | the intended machine (Conceive) |
| out | interaction map | graph + claims tagged exploratory/decision_grade | Explore |
| out | decision event | append-only record | who, what, why, evidence, criteria version |
| out | frozen prediction | JSON + sha256 | a prospective claim scored only against later games |

## 🔗 Dependencies
See the layer table in VISION.md. Authority order: see CHARTER.md.

## 🤝 Integration & Coordination
- Kate (ChatGPT) coordinates and reviews adversarially; Zach holds design authority; Claude agents build and run.
- Spec Kit (if adopted) runs spec/plan/tasks through a thin adapter. A spec never silently overrides this file.
- Unresolved challenges are append-only records referencing a contract, decision or artifact, and are closed only with a disposition and rationale.

## ⚠️ Risks & Edge Cases
- 0 of 4,961 contracts are reviewed, and the evaluator types only 4–31 of 60–65 nonland cards per deck, so outputs are descriptive.
- The evaluator does not reproduce the observed Vraska closing failure.
- Offspring token/card identity and SCD basic collector numbers are unresolved.
- The inherited AEC template charter (S3/FAISS/Typer) is itself a drift case and is replaced here.

## 🗣️ Dialogic / Philosophy Notes
Zach develops objectives while using models to interrogate designs. The system must let the criteria change visibly, not just the decks.

## 📌 Pipeline Integration
@ai-pipeline-order: inventory + Oracle → grammar → DIO contracts → KB → interactions → contextual evaluation → (optional) simulation; the Decision Model consumes all of them, and deck construction/portfolio consume its outputs. This is a conceptual dependency flow, not one executable pipeline.

## 🧪 Test Guarantees
Each P-contract gets at least one violating fixture that fails (as each check is built), plus clean decoys and one approved purpose revision that must *not* be flagged.

## 🌱 Future Enhancements
Scored 10-20 predictions; Factory/Dina/Vraska demo; one new frozen counterfactual; the 330-op class review as a separate KB quality track (off the critical path).
