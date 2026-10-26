# Module: oracle.refresh
> Fetch and snapshot Scryfall Oracle text as an explicit, versioned refresh. Discrepancies go to the QA queue and never erase manual corrections.

@ai-path: oracle.refresh
@ai-source-file: kb/oracle_refresh.py
@ai-role: ingest
@ai-intent: "Fetch and snapshot Scryfall Oracle text as an explicit, versioned refresh. Discrepancies go to the QA queue and never erase manual corrections."
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
| In | Card identities from the KB |
| Out | Append-only refresh snapshots in kb/refresh/*.jsonl |

### Risks, invariants and known gaps
- Runs as a separate operation, never inside a user query.
- Each replay adds about 212 qa_queue rows, so qa_queue counts are not a count of new problems.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
