# Module: simulation.engine
> Turn engine and resource ledger for scenario play. A consumer of mechanics, never their authority.

@ai-path: simulation.engine
@ai-source-file: kb/vendor/mtg_eval/engine.py
@ai-role: simulation
@ai-intent: "Turn engine and resource ledger for scenario play. A consumer of mechanics, never their authority."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: abilities, access
@ai-contracts: P-01, P-03

### Inputs and outputs
| Direction | What |
|---|---|
| In | Typed ability projections |
| Out | Scenario outcomes (provisional) |

### Risks, invariants and known gaps
- A goldfish lethal bound is not a multiplayer win probability.
- Simulation must not become the authority on card meaning, which was the October 2026 drift. Frozen predictions in predictions/ are scored only against the criteria version frozen with them.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
