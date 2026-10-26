# Contracts vs the Interaction Ontology: alignment and open decisions (2026-10-21)

> **Update, 2026-10-22.** Kate and Zach decided A1–A7. The decisions are recorded as a versioned compatibility addendum:
> `addendum/DIO_v3.1.1_compat_addendum_v0.1.md` and `registry_delta_v0.1.json`. Drafter 0.4.0 follows it.
> - **A2 is reversed.** `actor` stays a field of its own, next to `permanent_controller_at_event`, `source_controller`, `owner` and
>   `relation_to_observer`. My proposal below to fold actor into controller is withdrawn.
> - The table in §A is kept as the record of what was proposed.

This note answers Zach's 2026-10-21 notes:

- tap as a cost vs tap as an effect;
- mana colour in costs and outputs;
- mana and sacrifice hooks;
- why the contract schema didn't match the ontology.

It covers drafter 0.3.0 (`contracts.py`, `mana.py`) and the rebuilt `mtg_cards_v0.2.sqlite`.

## Short answer

The 2026-10-20 contracts were my own drafting format, not the ontology's. Nothing in the ontology prevented a
clean match; I hadn't mapped to it. As of 0.3.0, each contract is a DIO v3.1.1 §5 `operation` with §4 hook
objects. The remaining mismatches fall into three groups:

- **A. Gaps in the ontology or registry.** These need your decision; proposals are listed below.
- **B. Ontology structure the drafter can't fill yet.** The contract records these as `unbound` and blocks.
- **C. The 0.3.0 simulator's action format,** which is older than the ontology and can't express colour, among
  other things.

You were right about mana: before this change, no record in the corpus said what colour of mana an ability
produces. Projections stored `["mana", 1]`, candidate rows stored `mana.add`, and cost atoms stored only the text.
The only place colour existed was inside the goldfish `CardModel`, and there "any colour" meant the deck's colour
identity.

## Field mapping (contract 0.3.0 → DIO v3.1.1)

| DIO §5 / §4 | Contract field | Status |
|---|---|---|
| `operation.id`, `kind` | `id`, `kind` (`spell_effect`→`cast`, `choice_mode`→`composite`) | matches; 162 legacy rows are `unclassified` and blocked |
| `source_unit` | `source_unit {card, face, oracle_text_sha256}` | matches; 178 multi-face clauses have no face and are blocked |
| `initiation.requirement_groups[] {id, class, alternatives, quantity, must_come_from_other_unit, checkpoint}` | same keys | matches. Each trigger, cost component, target class and condition is its own group, and alternatives sit inside a group (§5.1) |
| trigger alternatives as hooks `{id, kind, subject, qualifiers}` | same | matches. Qualifiers include controller, other, object_filter, cardinality, token, actor and source_event (see A2/A3) |
| `amplifiers` | `initiation.amplifiers [{text, measures, aggregation, relation: MODIFIES}]` | partial: "for each", "equal to" and X are bound as amplifiers, but the §5.6 comparison is only the measured phrase |
| `timing {turn_scope, window, speed, ordinal_condition}` | same, plus `legacy` | matches; `stack_condition`, `delay` and `expiry` aren't drafted |
| `cost {method, components, additional, modifiers, mana_restrictions, on_payment, remembered}` | `method`, `components` (group ids), `on_payment`, `remembered` | partial: alternative and additional cost methods and substitutions are flagged unbound (B) |
| `choice {chooser, choice_time, legal_set, cardinality, scope, branch_outputs}` | same | partial: modes are listed, but `branch_outputs` is null, so modal cards stay blocked |
| `process` (ordered steps, branches) | not drafted | B: "instead", "otherwise", inner "if" and "unless" block the contract |
| `result {produces, consumes, transforms, modifies, permits, prevents, transitions}` | same keys | partial: `produces` holds ids plus typed mana, tap, sacrifice actor and zone transitions. Quantities and recipients (for example "draw **a** card") aren't on every item yet |
| `capacity` | `capacity [{uses, renews}]` | matches for "only once each turn" |
| `evidence` | `evidence` (row, status, confidence, URL, untouched legacy fields) | matches |
| §9 "derived, never stored" | `query_index` | an index for `kbq.py`, labelled as derived and never used as a source |

## Your notes, one by one

**1. Tap as a cost vs tap as an effect.** These are now separate everywhere:

- `{T}` is a cost component `{family: tap, subject: this}` in its own cost group (662 contracts).
- "Tap an untapped creature you control" is a cost component `{family: tap, subject: other, object_filter,
  quantity, must_come_from_other_unit}` (12 contracts).
- Both write `permanent.tap` into `cost.on_payment`, because paying is an act that produces events (§5.3).
- Tapping as part of the effect is `result.produces {id: permanent.tap, as: effect, object}` (9 contracts).

The 0.3.0 engine's `tap_self` / `tap_other` fields only model the cost side.

**2. Mana colour and type** (`mana.py`).

*Costs.* Each pip is typed:

| Pip | Type | Can be paid with |
|---|---|---|
| `{N}` | generic (the grey number) | any mana |
| `{W}` | colored | only that colour |
| `{C}` | colorless | only colourless mana |
| `{W/U}` | hybrid | either colour |
| `{2/W}` | mono-hybrid | two generic **or** W |
| `{W/P}` | phyrexian | W **or** 2 life |
| `{X}` | X | value is remembered, and it acts as an amplifier |
| `{S}` | snow | mana from a snow source |

Hybrid, mono-hybrid and phyrexian pips are the "split costs that aren't equivalent". Each one is an OR inside a
single cost group, which is what DIO §5.1 alternatives are for, so they don't need a special case.

Whole alternative costs ("rather than pay this spell's mana cost") are `cost.method: alternative` in DIO. The drafter
flags them as unbound for now.

Spell contracts now carry the card's own mana cost as their first cost group.

*Production.* Every `mana.add` records a mode, amount, scaling and restriction. The modes are:

| Mode | Contracts |
|---|---:|
| alternatives | 117 |
| fixed | 108 |
| colorless | 90 |
| any_color | 81 |
| chosen_color | 15 |
| any_combination | 6 |
| any_one_color | 5 |
| combination_of | 4 |
| any_type | 1 |
| unread | 2 (blocked by check C14) |

Each record also says whether the mana is coloured, colourless or both, so "only coloured" sources (which can't pay
`{C}`) are distinguishable from colourless ones.

New check C15 warns wherever the 0.3.0 action would run the ability with amount-only mana. Also found: the goldfish
model in `access.mana_cost` counts `{C}` as generic. That bug only matters for the handful of `{C}` costs (5 cards).

**3. Mana hooks.**

- "Whenever you tap a creature for mana", "enchanted land is tapped for mana" and "a player / an opponent taps a land
  for mana" are now `mana.add` listeners with `{source_event: tapped_for_mana, source_filter, actor}`.
- "Whenever you expend 4" is `mana.spend` with a threshold comparison.
- DIO has `mana.add` and `mana.spend`, but no way to say *which permanent was tapped* to produce mana. This is
  decision A1.

**4. Sacrifice hooks** (the Dina question). Sacrifice listeners now carry:

- **actor:** you, any player or opponent;
- **object_filter:** creature, nontoken Elemental, Food, Clue, Blood token, permanent, and so on;
- **other/another;**
- **token / nontoken;**
- **cardinality:** each vs one_or_more.

Today the corpus holds 18 sacrifice listeners: 13 "you sacrifice …" (3 of them "another"), 3 "a player sacrifices
…" and 2 "…enters and when you sacrifice it". In those last 2 the actor isn't read yet. `permanent.sacrifice` stays separate from `permanent.dies`, as §4.3 requires. A sacrifice
paid as a cost also writes `permanent.sacrifice` (and `permanent.dies` if it's a creature) into `cost.on_payment`, so
an engine can see it fire before resolution (§5.3).

## A. Ontology and registry gaps (your decision)

| # | Gap | What I do now | Proposal |
|---|---|---|---|
| A1 | No hook for "tapped for mana": §4.2 has `mana.add` and `permanent.tap`, but nothing ties the mana to its source | `mana.add` with qualifiers `source_event: tapped_for_mana`, `source_filter`, `proposed_identifier: permanent.tapped_for_mana` | Add facet `permanent.tapped_for_mana`, implying `permanent.tap` and `mana.add [source: that permanent]` (CR 106.12) |
| A2 | No "actor" axis in §4.1. "You sacrifice" names who acts, not who controls | `actor` qualifier | ~~Collapse `actor` into `controller` for sacrifice and tapped-for-mana~~ **Overruled 2026-10-22:** keep `actor`, add `permanent_controller_at_event` (`same_as_actor` where CR 701.21a/605 force it), `source_controller`, `owner`, `relation_to_observer` |
| A3 | Batching ("one or more") is in the grammar registry (`one_or_more`) but has no hook qualifier slot | `cardinality: each \| one_or_more` | Add `cardinality` to §4 qualifiers; ties to Kate's simultaneity_group work |
| A4 | No mana vocabulary: no domain for pip types or production modes, and `mana_restrictions` has no values | `mana.py` types (above) | Add registry domains `mana.symbol.type`, `mana.production.mode` and `mana.restriction` |
| A5 | `rules.cost.family` lacks energy, loyalty, remove counters, blight and collect evidence | families `pay_energy`, `loyalty`, `remove_counters`, `blight`, `collect_evidence` | Add them, or say which should be macros |
| A6 | "At the beginning of …" has no hook id. Legacy rows use `timing.step_begin`, which isn't in the registry (197 warnings) | kept as a warning | Add `step.begin [step, whose turn]`, or bind it to §5.2 `window` |
| A7 | Keyword reminder text (earthbend etc.) appears as operations (47 legacy rows) | blocked by C13 | Keyword macros with their own event, as in the v3.1.2 review |

## B. Ontology structure the drafter can't fill yet (blocks contracts)

- `process` branches for "instead", "otherwise", inner "if" and "unless". This is most of the 1,024 C09 failures.
  The Necrobloom seven-names branch is one of them.
- `choice.branch_outputs`: modal spells list their modes, but the outputs aren't split per mode.
- `cost.method: alternative` and substitutions ("rather than pay", "without paying").
- Quantities and recipients on most `result` items, and the §5.6 comparison behind amplifiers.
- `rewrites` for replacements, and `implies` on produced hooks.

## C. The simulator boundary

The 0.3.0 action (`proposed_action`) is the engine's format: `kind`, `hook`, `cost` and `outputs` like
`["mana", 1]`. It has no colour, no actor and no batching, and it is not the ontology. In this design the contract
is the executable data and the action is only a compile target. Right now the compiler borrows the matching 0.3.0
projection. The next step is for the compiler to emit the engine action **from the contract** (colour, pip
alternatives, tap and sacrifice on payment), and for the engine to accept typed mana. Until then, C15 marks every
place where colour would be lost.

## Effect on the queue

The rebuild produced 1,617 contracts ready for review (1,051 with an action) and 3,014 blocked; it was 1,563 and
3,068. Binding "for each" and X as amplifiers unblocked some contracts. New blocks came from cost substitutions and
two unread mana productions. Reviews: still 0. Because each contract's SHA changed, any review made against
yesterday's drafts would now read `stale_contract_changed`. None existed.
