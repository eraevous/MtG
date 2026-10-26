# Module: inventory.adapter
> Read the canonical inventory export (Collection, Deck Allocations) as the source of ownership and allocation facts. Mechanics sheets are candidate annotations, never verified rules.

@ai-path: inventory.adapter
@ai-source-file: kb/inventory_adapter.py
@ai-role: adapter
@ai-intent: "Read the canonical inventory export (Collection, Deck Allocations) as the source of ownership and allocation facts. Mechanics sheets are candidate annotations, never verified rules."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | Canonical Sheet export (.xlsx, read only) |
| Out | Card copy facts, deck lists, candidate mechanics rows (JSONL) |

### Risks, invariants and known gaps
- Sheet authority: archive-then-clone, so the Sheet id changes with each edit. Resolve the current id; never embed it permanently.
- Never writes to the workbook. Plans are not moves.
- Refuses archive copies as build inputs (see kb/freeze_check.py).

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
