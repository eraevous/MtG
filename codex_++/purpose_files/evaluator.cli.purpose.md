# Module: evaluator.cli
> Contextual deck and card evaluation: card, deck, module, compare, upgrades, build, inventory, transfer, portfolio, regress.

@ai-path: evaluator.cli
@ai-source-file: kb/vendor/mtg_eval/cli.py
@ai-role: evaluator
@ai-intent: "Contextual deck and card evaluation: card, deck, module, compare, upgrades, build, inventory, transfer, portfolio, regress."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: api, regression, report
@ai-contracts: P-04, P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | Inventory export (.xlsx) or a collection database (collection/schema.sql, read by collection_db.py), KB through sqlite_bridge |
| Out | Deck reports (Markdown or JSON) |

### Risks, invariants and known gaps
- Typed coverage is 4 to 31 of 60 to 65 nonland cards per deck, so the outputs are descriptive profiles, not rankings.
- Does not reproduce the observed 'Vraska can't close' result. That remains open evidence against its predictive adequacy.
- Prefer this vendored copy. kb/mtg_eval_release names an older Sheet id.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
