# Module: discovery.loops
> Derive produces/observes/needs per ability, plus flow edges and loop candidates, without judging their value.

@ai-path: discovery.loops
@ai-source-file: grammar/discovery.py
@ai-role: discovery
@ai-intent: "Derive produces/observes/needs per ability, plus flow edges and loop candidates, without judging their value."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: semantics
@ai-contracts: P-04

### Inputs and outputs
| Direction | What |
|---|---|
| In | Compiled ability contracts |
| Out | discovery/collection_loops.csv with a certainty level |

### Risks, invariants and known gaps
- 2,125 two-card loop candidates, of which 11 are 'guaranteed'. Candidates inherit the verification limits of the contracts underneath.
- Must not filter by power or competitiveness. That is the evaluator's job (P-04).

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
