# Module: kb.contract_roles
> Makes the 0.3.0 evaluator read its coverage roles (draw, ramp, counterspell, token_maker, counter_source, lifegain_source) from the KB's DIO-shaped operation contracts (`query_index.feeds`), instead of only from its own Oracle-text patterns (C-012). Roles the contract vocabulary can't carry yet stay on the pattern reader, labelled as fallback.

@ai-path: kb.contract_roles
@ai-source-file: kb/contract_roles.py
@ai-role: evaluator_adapter
@ai-intent: "Downstream consumes upstream: the evaluator's role claims come from the contracts the KB owns, with every role carrying its basis."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: bridge_v02, sqlite_bridge
@ai-contracts: P-01, P-03, P-06

### Inputs and outputs
| Direction | What |
|---|---|
| In | The KB release database (read-only): `operation_contracts.contract_json.query_index.feeds`; the evaluator's own pattern record per card |
| Out | A replacement `inv.record()` on a SQLiteInventory: `{role: {status, evidence{basis, ...}}}`, basis one of `dio_contract`, `text_pattern_fallback`, `human_label`; `inv.role_source` summary |

### Risks, invariants and known gaps
- Opt-in: `open_grounded_evaluator()`; `bridge_v02.open_evaluator()` and the vendored mtg_eval are unchanged (both pinned in kb/MANIFEST.sha256), so released outputs and the frozen predictions don't move.
- `ROLE_MAP` (role -> DIO event ids) is a candidate lane reading, not a DIO statement and not part of the pinned DIO (P-09). Contracts are candidates too (0 semantically reviewed). Nothing here is verified.
- Human judgment labels outrank both readers. A pattern role the contracts don't support becomes `not_in_contract` and isn't counted.
- Not covered: removal/wipe scope, recursion, protection, closers, and the derived_facts readers (clauses, wipe_kind, resource ledger) still come from the 0.3.0 patterns. Contract feeds are said to be "for its controller" but Swords to Plowshares feeds life.gain (the exiled creature's controller gains): a KB gap, raised for a dialogue round.
