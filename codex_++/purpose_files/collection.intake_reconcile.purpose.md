# Module: collection.intake_reconcile

> Stage receipt quantities against a canonical inventory export without changing custody.

@ai-path: collection.intake_reconcile
@ai-source-file: collection/intake_reconcile.py
@ai-role: adapter
@ai-intent: "Produce read-only review proposals while preserving unknown printing details and existing allocations."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: low (private collection details; inputs and outputs remain local)
@ai-dependencies: none
@ai-contracts: P-02, P-05

## Contract
- Read explicit Collection CSV and accepted intake CSV or full review JSON. Reject noncanonical declared source titles; title declarations do not independently verify freshness.
- Propose additions by exact accepted card name only. Ambiguous normalized names, unresolved identities and invalid quantities remain excluded from proposals.
- Preserve input printing details, observed language and source evidence. Missing set/collector identifiers and unknown finishes are explicit review flags, never invented values.
- Never alter canonical ownership, existing deck allocations, KB data or input files. Current canonical Sheet validation, approval and physical confirmation precede any separate application.
- Tests: `tests/test_intake_reconcile.py` and `tests/test_inventory_first_intake.py`.
