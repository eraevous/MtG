# Module: tools.drift_check
> Mechanical drift checks: frozen files, purpose-file sync, undeclared semantic authority, append-only ledgers.

@ai-path: tools.drift_check
@ai-source-file: tools/drift_check.py
@ai-role: governance
@ai-intent: "Mechanical drift checks: frozen files, purpose-file sync, undeclared semantic authority, append-only ledgers."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-01, P-03

### Inputs and outputs
| Direction | What |
|---|---|
| In | Repo tree, tools/drift_rules.json, optional git base ref |
| Out | Findings (text or JSON). Exit 1 on errors; exit 2 in hook mode |

### Risks, invariants and known gaps
- Structural only. A clean run is not evidence that P-00 to P-05 survived.
- The semantic-authority check is a heuristic (it flags oracle_text plus regex outside the owners), so it gives warnings only.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
