# DIO v3.1.1 compatibility addendum v0.1 (`DIO-3.1.1-kb-addendum-0.1`)

- **Status:** accepted.
- **Decided by:** Kate and Zach, 2026-10-22. They decided on the open questions A1–A7 in `ONTOLOGY_ALIGNMENT.md` (2026-10-21), as part of the independent review of KB v0.2.
- **Scope:** the smallest set of additions that lets operation contracts be expressed in the ontology without private fields.
- **Machine-readable form:** `addendum/registry_delta_v0.1.json`.
  - `migrate_v02.py` loads it into the `ontology_addendum` table.
  - Validation check C04 counts its hook identifiers as registry vocabulary.

The ontology remains the governing schema. This addendum extends it and does not replace any part of it. Any later change gets a new version number, and contracts record which addendum they were drafted against (`meta.addendum_version`).

| # | Decision | Registry delta | Drafter 0.4.0 behaviour |
|---|---|---|---|
| A1 | `permanent.tapped_for_mana` is a **derived facet**. It is true only when a mana ability of that permanent, whose cost includes {T}, resolves and produces mana (CR 106.12, 106.12a–b, 605). It is not true for crew, station, other costs, or tapping by an effect. | hook identifier `permanent.tapped_for_mana`, implies `permanent.tap [that permanent]` + `mana.add [source: that permanent]` | "Whenever you tap a creature for mana", "enchanted land is tapped for mana" and "a player taps a land for mana" draft to this id with `source_filter`. `events.derive_facets` implements the rule (T3). |
| A2 | **Keep `actor`.** Also record `permanent_controller_at_event`, `source_controller`, `owner` and the `relation_to_observer`. (This reverses the 2026-10-21 proposal to fold actor into controller.) | domains `hook.qualifier.actor`, `hook.qualifier.player_relation` | Hook qualifiers carry `actor` (you / opponent / any_player) and `relation_to_observer`. For sacrifice and tapped-for-mana, `permanent_controller_at_event: same_as_actor` (CR 701.21a, 605). Elsewhere the `controller` relation is used. `source_controller` and `owner` are filled when the text names them. |
| A3 | Cardinality: `each_object`, `one_or_more` (once per simultaneous event), `per_player`, `per_batch`, plus a simultaneity group. | domains `hook.qualifier.cardinality`, `hook.qualifier.simultaneity_group` | "one or more" drafts to `one_or_more` + `simultaneity_group: per_event_batch`. Everything else drafts to `each_object`. `events.trigger_count` counts firings accordingly (T4). |
| A4 | Typed mana with provenance. Snow is a property of the source, not a colour. "Any colour" excludes colourless. "Any type" may include colourless. {C} can't be paid with coloured mana. | domains `mana.unit.type`, `mana.symbol.type`, `mana.production.mode`, `mana.provenance` | `mana.parse_cost` and `mana.parse_production` (as before). New `mana.can_pay(cost, units, life, x)` and `mana.production_pools(record)` (T2). |
| A5 | A narrow set of cost primitives plus macros. Keep "paid as a cost" separate from "done on resolution". | `rules.cost.family` adds `remove_counters` and `pay_energy`. Macros: `loyalty`, `blight`, `collect_evidence`. Domain `act.time`. | Every cost component has `act_time: paid_as_cost`, and its events are in `cost.on_payment` (observable at payment). Every result item has `act_time: on_resolution`. |
| A6 | `turn.phase.begin` and `turn.step.begin`, qualified by phase/step and whose turn. The legacy `timing.step_begin` becomes an alias. | two hook identifiers, alias `timing.step_begin → turn.step.begin / turn.phase.begin` | "At the beginning of …" triggers draft to these ids, using the steps and phases from `rules.turn.step` / `rules.turn.phase`. C04 vocabulary warnings dropped from 197 to 6. |
| A7 | Versioned keyword macros. | `macro.earthbend@1`, `macro.offspring@1`, `macro.dredge@1`, `macro.crew@1`, `macro.station@1` | `contract.keyword_macro = {macro, role: instance \| reminder_text_of_macro, parameter}`. Reminder-text clauses stay blocked (C13), and the runtime gate records them as `reminder_text`. Macro expansion into process steps is not done yet. |

## Not decided here

- The phrase-to-concept grammar layer. That is a separate thread, which will use these contracts as comparison material.
- Process branches (`instead`, `otherwise`, `if`, `unless`), `choice.branch_outputs`, and `cost.method: alternative`. These still block contracts, as recorded in `ONTOLOGY_ALIGNMENT.md` §B.
