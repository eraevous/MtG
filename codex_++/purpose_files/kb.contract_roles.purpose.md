# Module: kb.contract_roles
> Makes the 0.3.0 evaluator read its coverage roles (draw, ramp, counterspell, token_maker, counter_source, lifegain_source) from the KB's DIO-shaped operation contracts (`query_index.feeds`), instead of only from its own Oracle-text patterns (C-012). Roles the contract vocabulary can't carry yet stay on the pattern reader, labelled as fallback.

@ai-path: kb.contract_roles
@ai-source-file: kb/contract_roles.py
@ai-role: evaluator_adapter
@ai-intent: "Downstream consumes upstream: the evaluator's role claims come from the contracts the KB owns, with every role carrying its basis."
@ai-version: 0.1.5
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
- 0.1.1 (Codex review on #42): reads `current_contracts` joined to `validation_queue`; `rejected` and `quarantined` contracts are left out (listed as `excluded_contracts`); `verification_state` is `semantic_reviewed` only when every contract a role rests on is, else `candidate`, with `contract_states` beside it. `open_grounded_evaluator().card()` adds basis, contracts, verification, pattern status and fallback reason to the capability table, plus a roles line under limitations.
- 0.1.2 (Codex review on #42): a land's own `mana.add` is not ramp (mtg_eval's rule); `land_to_battlefield` still is.
- 0.1.3 (Copilot review on #42): contract roles are always `candidate` (ROLE_MAP is unreviewed; source review states stay in `contract_states`); hand labels are read independently, so a false label with no pattern hit still blocks a contract role; `tag_only`/`contradicted` stay uncertain when the contract is silent; labelled roles keep basis `human_label` on every path; deck/module/compare/upgrades/build/inventory/transfer/portfolio reports carry a roles line and `data.role_source`.
- 0.1.4 (Codex review on #42): counter_source needs a kind-qualified event (`counter.put:+1/+1` or `counter.put:proliferate`, derived from `result.produces`); charge, loyalty, -1/-1 and other counters no longer count.
- 0.1.5 (Copilot review on #42, second pass): a false hand label records `contradicted` only when a contract would otherwise support the role (otherwise nothing, so no false uncertainty); contract evidence keeps the prior oracle/tag evidence.
