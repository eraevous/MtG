# Module: tools.drift_check
> Mechanical drift checks: frozen files, purpose-file sync, undeclared semantic authority, append-only ledgers, governed DIO sources, the decision mirror.

@ai-path: tools.drift_check
@ai-source-file: tools/drift_check.py
@ai-role: governance
@ai-intent: "Mechanical drift checks: frozen files, purpose-file sync, undeclared semantic authority, append-only ledgers, governed DIO sources, the decision mirror."
@ai-version: 0.2.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-01, P-03, P-06, P-09

### Inputs and outputs
| Direction | What |
|---|---|
| In | Repo tree, tools/drift_rules.json, .aec/records.jsonl and decisions/decision_events.jsonl when present, optional git base ref |
| Out | Findings (text or JSON). Exit 1 on errors; exit 2 in hook mode |

### Risks, invariants and known gaps
- Structural only. A clean run is not evidence that P-00 to P-09 survived.
- `governed` reads the latest version of each `source` record whose subject is in `governed_subjects` and fails when an anchored repo file's bytes differ. It re-implements only AEC's raw-byte digest, not locators or roots, so it runs without an AEC checkout. AEC (`aec check`) stays the full anchor check. (0.2.0, D-0020 proposed)
- `mirror` compares status only. It does not check that a decision's text or dependencies match the log.
- The semantic-authority check is a heuristic (it flags oracle_text plus regex outside the owners), so it gives warnings only.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
