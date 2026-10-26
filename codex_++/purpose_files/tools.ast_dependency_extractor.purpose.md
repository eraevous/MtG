# Module: tools.ast_dependency_extractor
> Extract function-call dependencies from Python files via AST (carried over from AEC).

@ai-path: tools.ast_dependency_extractor
@ai-source-file: tools/ast_dependency_extractor.py
@ai-role: analysis
@ai-intent: "Extract function-call dependencies from Python files via AST (carried over from AEC)."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: structural

### Inputs and outputs
| Direction | What |
|---|---|
| In | Python source tree |
| Out | CSV of call dependencies |

### Risks, invariants and known gaps
- Not wired into CI yet. drift_check has its own import scan.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
