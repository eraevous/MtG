# MTG DECK INTERACTION ONTOLOGY

**Version 3.1.1 · 2026-10-06 · Namespace: mtg-dio**

A portable analytical ontology for what Magic: The Gathering abilities, cards, packages, subsystems and decks can do: what they require, what they produce, consume, transform, modify, permit, prevent or observe, what constrains those operations, and where apparent connections fail.

Version 3.1 is the same model as 3.0.1 with fewer parts. It keeps the InteractionUnit holarchy, the seven primitive relations, the hook vocabulary, AND-of-OR operations, amplifiers, connection polarity, module contracts and the separation of description from evaluation. It merges 41 record schemas into 13, replaces per-record survival flags with one table, and moves everything computable out of storage. Section 13 maps every 3.0.1 record onto this edition; no meaning changed. Release 3.1.1 is a wording and verification pass on 3.1.0, listed at the end of section 13.

The purpose is not to simulate Magic. It is to stop losing deck-building information at the places where the rules are irreducibly stateful.

---

## 1. THE MODEL ON ONE PAGE

Five nouns:

| Noun | What it is |
|---|---|
| **Unit** | An ability, card, package, subsystem or deck. Units nest and overlap. |
| **Hook** | A typed, qualified thing a unit can receive or expose: an event, a state, a resource, an object, a permission. |
| **Operation** | The smallest executable contract. It has requirement groups, optional amplifiers and a result. |
| **Object** | What an operation acts on, in three strata: the object itself, its characteristics, its state. |
| **Connection** | One operation's output satisfying another operation's requirement. Verified connections compose into modules. |

Two rules:

1. **The gate rule.** An operation can happen only when every one of its requirement groups is satisfied, and a group is satisfied by any one of its alternatives. An input that only makes the result bigger is an amplifier and is never a requirement.
2. **The persistence rule.** When something changes, ask whether the same object continues. If it does, no entry or departure occurs and its object-bound state persists by default; that state ends early only when the operation itself changes it or the state's own continuing condition fails. If a new object is created, object-bound state is gone and entry happens afresh. Section 6.4 is the full table.

Seven questions apply the model to any line:

```
What is the object?            What must be paid, and when?
What can currently touch it?   What persists through the change?
What operation is legal?       What event really occurred?
                               What can use the result?
```

---

## 2. BOUNDARIES AND PARSIMONY

The ontology describes capability, execution conditions, state transitions and connectivity. It does not decide that a card is good, efficient, fun or worth a slot. Three neighbouring layers keep their own objectives: **Deck Building and Evaluation** (quality, coverage, probability, resilience), **Portfolio Allocation** (which physical copy lives in which deck) and **Kairos–GATE** (live play). It also keeps no runtime object IDs, no turn ledger, no priority or layer engine, and no exhaustive state-based-action processing. When exact rules machinery decides whether a connection works, do the short rules check and store the deck-relevant consequence.

A concept belongs in the model when it changes a recommendation, prevents a false connection or exposes a hidden one, recurs across many cards, can be read from Oracle text or a short rules check, saves repeated reasoning, composes from ability up to deck, and does not turn the ontology into a simulator. Three working rules follow:

- **Normalize before naming.** Decompose a new mechanic into existing hooks, relations, operations and transitions. "Irma liability laundering" is a derived route, not a primitive.
- **One home per fact.** What an operation needs and does lives on the Operation. What an object remembers lives in State. Anything computable from those is derived (section 9) and not stored.
- **Open precision only when it changes the answer.** A vanilla creature, plain removal, an ordinary mana rock, a basic ETB creature, a normal land and an ordinary Aura need a Unit and perhaps one Operation. If they need more, the implementation is too heavy.

---

## 3. UNITS

```yaml
unit:
  id:
  name:
  level: effect_bundle | ability | card | package | subsystem | deck
  purpose:
  evidence: {oracle_text, source, verification_date, status, confidence, unresolved_questions}
  member_units:
  operations:        # references
  object:            # section 6, only when continuity, copying or state matters
  viability: {requires, disrupted_by, competes_for, dead_without, recovers_via, vulnerable_domains}
  contract:          # packages and subsystems, section 8
  alternatives:
  notes:
```

A unit can be read as a black box through its contract, opened into smaller units, belong to several larger units at once, and be replaced by another implementation with a compatible boundary. The structure is a directed typed hypergraph, not a tree.

`viability.requires` holds only external preconditions that no single operation owns (a commander being available, an assumed board). `vulnerable_domains` names the systemic conditions that switch the unit off: graveyard, creature battlefield, artifact battlefield, activated abilities, stack, combat, tokens, counters, lands, commander access.

A unit with no Operation records may list `accepts:` and `exposes:` hooks directly. Otherwise those are roll-ups of its operations.

---

## 4. HOOKS

```yaml
hook:
  id:                # dotted identifier, section 4.2
  kind: event | state | resource | object | permission | capability | historical_condition | information
  subject:
  qualifiers: {controller, owner, zone, object_filter, quantity, cardinality, timing, condition, evaluation_time}
  certainty: guaranteed | optional | conditional | opportunity
  implies:           # broader hooks this one also satisfies: a bare id, or {hook, projection, condition}
```

### 4.1 The qualifier discipline

A producer satisfies a receiver only when the identifier and every material qualifier match. Similar nouns do not establish compatibility.

Qualifier axes: card type, subtype, supertype · creature type and chosen type · shares a type, color, name, controller or owner · color and color identity · mana cost, mana value, mana actually spent · power, toughness, base values · token, nontoken, card, noncard · controller and owner · source and destination zone · self, other, another, target, chosen, linked · attacking, blocking, blocked, unblocked, tapped, untapped · cast form, alternative cost, additional cost · this turn, each turn, your turn, opponent's turn, this combat · first, second, next, once, one or more · current, trigger-time, resolution-time or captured value.

Creature-type relations are predicates, not events. Changeling widens type membership in every zone and creates no event. "This or another" is not a qualifier; it defines alternatives inside one requirement group (section 5.1).

### 4.2 Core vocabulary

Extensible. Prefer a broad identifier plus qualifiers over synonyms.

| Family | Identifiers |
|---|---|
| Zone and access | `zone.enter/leave` · `battlefield.enter/leave` · `graveyard.enter/leave` · `hand.enter/leave` · `exile.enter/leave` · `library.enter/leave` · `command.enter/leave` · `card.return_to_hand` · `card.return_to_battlefield` · `card.cast_from_zone` · `card.play_from_zone` |
| Stack and ability | `spell.cast/resolve/countered/copied` · `ability.activated/triggered/copied/resolved` · `object.becomes_target` · `permission.cast/play/activate` |
| Object and resource | `card.draw/discard/mill/reveal/look/search` · `library.shuffle` · `permanent.sacrifice/destroy` · `token.create` · `counter.put/remove/move` · `mana.add/spend` · `life.gain/lose/pay` · `damage.deal` · `land.play` |
| State and characteristic | `permanent.tap/untap` · `permanent.transform` · `permanent.turn_face_up/down` · `permanent.phase_in/out` · `permanent.attach/detach` · `control.change` · `characteristics.change` · `object.becomes_copy` · `designation.gain/lose` · `threshold.crossed` (event) · `threshold.reached` (state) · `comparison.satisfied` |
| Combat | `attacker.declared` · `blocker.declared` · `creature.attacking/blocked/unblocked` · `combat.damage` · `noncombat.damage` · `creature.removed_from_combat` · `combat.begin/end` |
| Narrower facets | `permanent.dies` · `creature.card_enters_graveyard` · `token.enters_battlefield` · `creature/artifact/land.enters_battlefield` |

### 4.3 Events, facets and states

- **An event is one occurrence.** It satisfies its own hook and every hook that hook implies, judged against the right snapshot: an entry is judged on the object as it enters, a departure on the object as it last existed on the battlefield. An Artifact Enchantment Creature Land entering is one entry that satisfies five listeners. It is never five entries.
- **Implication runs one way.** `creature.enters_battlefield` implies `battlefield.enter`. `permanent.dies` implies a battlefield departure and a graveyard entry. `spell.copied` does **not** imply `spell.cast`. `token.enters_battlefield` does **not** imply `token.create`.
- **Most implications are a bare identifier.** When the broader hook has a different subject or holds only sometimes, write `{hook, projection, condition}`. `permanent.dies` implies `{hook: creature.card_enters_graveyard, projection: the card that was the permanent, condition: nontoken creature and destination not replaced}`.
- **A state holds; an event happens.** "Has three lore counters" is a state. "Went from two to three" is an event. A listener for the crossing is not satisfied by the state.
- **A replaced event did not occur.** Only the resulting event exposes hooks (section 5.4).

Distinctions that must survive: cast vs enter · leave vs die vs graveyard entry · sacrifice vs destroy · mill vs death · draw vs card entering hand · token created vs token entered · spell copied vs spell cast · trigger copied vs event repeated · one doubled event vs two events · entered tapped vs became tapped · entered attacking vs declared as attacker · cost paid vs effect resolved · current vs last-known value · damage vs life loss vs life payment vs net life change.

---

## 5. OPERATIONS

```yaml
operation:
  id:
  kind: cast | activate | trigger | continuous | replacement | special_action | state_based | composite
  source_unit:
  initiation:
    requirement_groups:          # ALL required
      - id:
        class: trigger | cost | timing | access | eligibility | assembly | state | history | information
        alternatives:            # ANY one suffices
        must_come_from_other_unit:
        quantity:
        checkpoint: trigger | initiation | payment | resolution | entry | state_check
    amplifiers:                  # scale the result, never required
    timing:                      # section 5.2
    cost:                        # section 5.3
    choice:                      # section 5.5
  process:                       # ordered steps or branches, only when order matters
  result:
    produces:
    consumes:
    transforms:
    modifies:
    permits:
    prevents:
    transitions:                 # section 6.4
    state_created:               # section 6.3
    rewrites:                    # replacement only: proposed event -> resulting event
  capacity:                      # references to state of kind capacity
  evidence:
```

Not every printed sentence needs an Operation. Split only where cost, timing, branching, replacement or event identity changes a connection.

**The seven primitive relations** are unchanged: **PRODUCES** (creates an event, object, resource, state or permission) · **OBSERVES** (responds to or measures without consuming; written as a requirement group or amplifier that reads a hook) · **CONSUMES** (spends finite stock or capacity) · **TRANSFORMS** (turns one defined input into another output) · **MODIFIES** (changes quantity, magnitude, cadence, eligibility, cost or capacity) · **PERMITS** (allows an action, zone use, timing exception or cost method) · **PREVENTS** (stops, replaces, restricts, taxes, counters or redirects).

### 5.1 Requirement groups and amplifiers

- The alternative events of one trigger form one group. "Whenever this creature or another artifact you control enters" is a single group with two alternatives.
- Each cost component, each target class and each stated condition is its own group.
- A hook narrower than a listed alternative satisfies it through `implies` and need not be listed.
- `must_come_from_other_unit` marks a group the card cannot supply itself ("sacrifice another creature").
- `checkpoint` says when the group is tested. A condition true at one checkpoint is not assumed true at a later one. Note any value captured there (power as the trigger was created, the amount paid).
- `class` exists for diagnosis. "I don't have the card" (access), "I can't pay" (cost), "the window is closed" (timing), "it is no longer a creature" (eligibility) and "the other piece is missing" (assembly) are different failures.

```yaml
operation:
  id: pactdoll_terror.drain
  kind: trigger
  initiation:
    requirement_groups:
      - id: g1
        class: trigger
        alternatives:
          - "battlefield.enter [subject: this permanent]"
          - "artifact.enters_battlefield [controller: you, other]"
  result:
    produces:
      - "life.lose [each opponent, 1]"
      - "life.gain [you, 1]"
```

Read as AND, the card looks almost unfireable. The first MeshLab hypergraph made exactly that error.

**Amplifiers.** Mana paid into X, extra bodies counted by a "for each" payoff and extra counters read by a scaling ability change the size of a result without gating it. A supplier of an amplifier is not a dependency and not a route; record it as a latent or conditional connection with MODIFIES. If the operation does nothing at zero, the first unit is a requirement (a group with quantity 1) and the rest is amplifier.

Multiplier classes name what a MODIFIES relation scales: quantity_multiplier, magnitude_modifier, event_repeater, trigger_multiplier, ability_copy, spell_copy, generator_population, capacity_multiplier, cost_efficiency_modifier, scaling_input_modifier. Say which stage is scaled. Doubling a trigger is not doubling the event that caused it, and reducing a cost is not making mana.

### 5.2 Timing

A timing-class group says when the operation may be initiated. Add detail only when the window changes connectivity.

```yaml
timing:
  turn_scope: your_turn | opponent_turn | any_turn
  window: {phase, step, relative_to, before_or_after}
  speed: sorcery | instant | mana_ability | special_action | none (continuous, replacement, state_based)
  stack_condition:
  ordinal_condition: first_each_turn | second_each_turn | next
  delay:           # trigger created now, resolves or acts later
  expiry:
```

Timing never holds a use count. How many times, and when that renews, is state of kind `capacity` (section 6.3). "Once each turn" is a capacity that renews every turn. "Only during your turn" is a window with no count.

### 5.3 Cost

Cost components are cost-class groups. Paying one is itself an act that can produce events and consume capacity before anything resolves.

```yaml
cost:
  method: base | alternative | without_paying_mana_cost
  components:      # cost-class group ids
  additional:      # still owed under any method
  modifiers: {increases, reductions, substitutions}
  mana_restrictions:
  on_payment:      # events and state created by paying: sacrifice, departure, bounce, tap
  remembered:      # values later text reads: X, mana spent, what was sacrificed
```

- A sacrifice paid as a cost exposes sacrifice, departure and death hooks before resolution.
- Returning an attacker to hand as an additional cost is a real bounce and a real loss.
- Tapping permanents to pay consumes their tap capacity even though they survive.
- One alternative cost cannot be combined with another. Additional costs still apply under an alternative.
- A reduction is not mana. Restricted mana is not fungible outside its permitted uses.
- "Without paying its mana cost" is a method, not a claim that nothing else is required. X is normally zero.

### 5.4 Replacement and state-based operations

A replacement is an operation of kind `replacement` whose result `rewrites` a proposed event into a resulting one. The hooks lost and gained are the difference between the two events and need no separate record. A draw replaced by dredge is not a draw. A token creation replaced by a different creation is one creation event.

A state-based consequence that matters to a line is an operation of kind `state_based`: one state-class group, tested at `state_check`, and its result. Store the condition and consequence, not the engine.

### 5.5 Choice

```yaml
choice:
  chooser:
  choice_time: initiation | payment | resolution | entry | replacement | trigger
  legal_set:
  cardinality:
  scope: shared | per_object | per_trigger | per_event
  opponent_agency:
  branch_outputs:
```

Modes, targets, chosen types and copied forms are all choices. `scope` matters most: ten independent triggers may choose ten different objects, while one shared choice forces a common result.

### 5.6 Comparisons

A comparison is the expression behind a condition or an amplifier.

```yaml
comparison: {subject_set, measurement, aggregation, operator, reference, scope, evaluation_time, tie_behavior, empty_set_behavior}
```

Do not collapse: the maximum value and the objects that have it · life lost and net life change · current and last-known power · each opponent and opponents pooled · event count and event magnitude · tied greatest and uniquely greatest.

---

## 6. OBJECTS

Open this section only when a line depends on continuity, copying, type change or stored state.

```yaml
object:
  substrate: physical_card | token | card_copy | spell_copy | ability_copy | emblem_like
  forms:                       # faces, halves, alternate spell forms; which are physically present
  characteristic_effects:      # section 6.2, only non-printed or contested ones
  state:                       # references, section 6.3
```

A `card_copy` is a nonphysical copy of a card made in a zone off the stack, which may then be cast. It is the substrate of "copy a card and cast the copy" and of a prepared permanent's linked spell, and it is not a spell until it is cast. Its lifetime is set by the effect that creates it; when it is meant to persist, record that as state with a `condition`.

### 6.1 Three strata

| Stratum | Contents | Question |
|---|---|---|
| **Object** | The physical card or token, and whether this is still the same game object | Same object, or a new one? |
| **Characteristics** | Name, colors, types, abilities, power and toughness, each with its source. A subset is copiable. | What is it right now, and what would a copy see? |
| **State** | Everything remembered about it that is not a characteristic: counters, tapped status, damage, attachments, designations, links, tracked effects, capacities, permissions, chosen values, history | What does it carry, and what reads that? |

The seven strata of 3.0.1 are these three: physical identity and continuity are the object; current and copiable characteristics are one stratum with a flag; stored state, history, linkage and tracked effects are all state.

### 6.2 Characteristics

```yaml
characteristic_effect:
  axis: name | color | type | subtype | supertype | ability | power_toughness
  operation: set | add | remove | retain | copy
  value:
  source:
  duration:
  condition:
  copiable: true | false
```

- **Current characteristics** are the printed values plus every effect that applies.
- **Copiable characteristics** are the printed values of the face that is up, plus effects marked `copiable`. Only copy effects (including their "except" clauses) and a few entry-time configuration abilities are copiable. Counters, attachments, ordinary buffs, type-changing animation and all other state are not.
- **Provenance.** When two effects support the same predicate, one expiring does not end it. A permanent animated by two effects stays a creature until the later one ends.
- **Forms.** A copied back face does not make the copier a physical double-faced card. A characteristic borrowed by a copy effect disappears when the copy effect ends on a zone change.

A characteristic change opens and closes selectors: an animated land can be targeted by creature-copy effects, a Vehicle that becomes a creature can be sacrificed as one, a creature that becomes a noncreature land leaves a creature sweeper's reach. These consequences are derived from the effect and the hook qualifiers. They are not stored.

### 6.3 State

```yaml
state:
  id:
  kind: counter | status | attachment | designation | link | tracked_effect | capacity | permission | chosen_value | history
  bearer:
  scope: object_instance | physical_card | player | turn | combat | game | linked_object
  quantity_or_value:
  created_by:          # operation; mark on_entry when only the entry event creates it
  interpreter:         # operations whose groups or amplifiers read it
  condition:           # what must stay true for it to continue: attachment legality, still prepared
  schedule:            # tracked effects: window and consequence
  uses:                # capacities and permissions
  renews_on:
  expiry:
  grants:              # permissions: action, eligible object, origin zone, cost method
  persistence:         # ONLY exceptions to section 6.4
  absence_consequence: # what happens when it is expected but missing
```

| Kind | Examples | Notes |
|---|---|---|
| counter | +1/+1, lore, time, finality, charge | May be a buff, a gate, a clock, a capacity or a liability. Do not assume its sign. |
| status | tapped, damaged, face-down, phased | |
| attachment | Equipment, Aura | `condition` is its continuing legality. Failure detaches Equipment and sends an Aura to the graveyard. An effect its trigger already created lasts its own duration. |
| designation | prepared, monarch, initiative, city's blessing, max speed | Text that could create a designation does not confer it. |
| link | "the exiled card", a linked prepared spell | A later ability that needs the link does nothing if this object never established it. |
| tracked_effect | delayed sacrifice or exile, "until end of turn" | Bound to one object or player. Never inherited through copying. |
| capacity | tap capacity, land plays, once-each-turn uses, extra combats | The only home for use limits. Untapping replenishes; it is not generic "untap synergy". |
| permission | cast from exile or graveyard, extra land play, alternate payment | May be finite and may expire. Satisfies an access, timing or cost group that would otherwise fail. |
| chosen_value, history | a chosen color; "cast this turn"; a remembered X | History is state scoped to a turn, a game or an object. |

Three properties do most of the work:

- **State has an interpreter, and the interpreter can change.** Lore counters on a continuing object mean one thing under one Saga's text and another under a different one. +1/+1 counters sit inert on a noncreature and matter again when it is a creature. This is *state reinterpretation*, and it is derived: the state persists, the operations reading it change.
- **On-entry state exists only if the entry happened.** "Enters with" counters, "as this enters" choices and entry-created links are created by the entry event and by nothing else.
- **Absence has a sign.** Missing on-entry state removes a liability driven by the state's presence (vanishing with no time counters never sacrifices) and triggers one driven by its absence (fading with no fade counters is sacrificed at the next upkeep). Record the second kind in `absence_consequence`.

Population is state and resource at once: a board of tokens is stock for sacrifice, measured state for a go-wide payoff, and tap capacity. Consuming it can be positive for one module and negative for another while both connections are valid.

### 6.4 The persistence table

```yaml
transition:
  operation:
  continuity: same_object | new_object | additional_object_created | old_object_ends
  source_zone:
  destination_zone:
  cast_occurs:
  entry_origin: stack | nonstack | none
  characteristic_effects:      # what the transition changes, including a copy
  exceptions:                  # state that departs from the table below
  replay_obligation:
```

| Transition | Object | Entry or departure | Cast | Characteristics | Object-bound state |
|---|---|---|---|---|---|
| Characteristic change (animate, add or remove a type) | same | none | no | effect added | kept; may fall inert or become readable |
| Becomes a copy | same | none | no | copiable set replaced, exceptions kept | kept; on-entry state of the copied text **not** created |
| Transform, turn face up | same | none | no | face or profile changes | kept |
| Phase out and in | same | none | no | kept | kept |
| Control change | same | none | no | kept | kept |
| Blink (leave the battlefield and return) | new | battlefield departure, then entry | no | the card's own | gone; on-entry state created |
| Reanimate, put onto the battlefield from another zone | new | entry; the card leaves its source zone | no | the card's own | none carried; on-entry state created |
| Bounce then recast | new | battlefield departure, later entry | yes | the card's own | gone; on-entry state created; cast choices made |
| Token copy, enters as a copy | additional or new | entry | no | source's copiable set plus exceptions | fresh; on-entry state of the copied text created |
| Spell copy on the stack | new | none | no | the spell and its choices | none |
| Card copy made, then cast | new | none until it resolves | yes | the copied card's copiable set | none |
| Leaves and does not return | ends | battlefield departure | no | copy effects and battlefield-only modifications end; the card has its own characteristics in the new zone | gone; a token ceases to exist |

Reading the table:

- "Kept" means kept by default. The operation can still remove state, and state with a `condition` ends when the condition fails: Equipment falls off a permanent that stops being a creature even though the object continues.
- "The card's own" characteristics are those of the card in its new zone, before any effect that applies there. An object entering as a copy takes the copied set instead.
- State scoped to a card, player, turn or game is untouched by object transitions.
- Counters on an object that changes zones cease to exist. That is not a `counter.remove` event.
- A new object is not tracked by effects that tracked the old one. Verify the wording before relying on this.
- A copy effect's exceptions become copiable, so later copies inherit them (*heritable phenotype*).
- Fill `exceptions` only where evidence shows a departure from the table.

**Worked example.** Irma, Part-Time Mutant: "At the beginning of combat on your turn, Irma becomes a copy of up to one other target creature you control, except her name is Irma, Part-Time Mutant and she has this ability. Then put a +1/+1 counter on her." Row two applies: same object, no entry, copiable set replaced, state kept. So she keeps every counter, gains none of the target's "enters with" state, and performs none of its entry abilities. Copying an animated land gives her the land's own copiable characteristics, because animation is not copiable. Her two exceptions are copiable, so a token copy of her (row eight) is a new object named Irma with her ability that does enter.

---

## 7. CONNECTIONS

```yaml
connection:
  from_unit:
  from_operation:
  output_hook:
  to_unit:
  to_operation:
  input_group:
  status: verified | conditional | candidate | incompatible | unknown
  strength: direct | conditional | package_dependent | latent | broken
  conditions:
  mismatches:
  polarity: positive | negative | mixed | context_dependent
  benefits:
  costs_or_losses:
  affected_state:
  break_even:
  evidence:
```

Three checks before `verified`:

1. **Same operation.** The output reaches the operation that holds the payoff. A card whose landfall trigger adds counters and whose damage sits on its entry trigger is not connected to a land source on the damage side.
2. **Requirement, not amplifier.**
3. **Qualified, not similar.** A listener that needs a token to enter is not fed by a nontoken creature.

In pairwise deck graphs built without these checks, between a quarter and nearly half of the apparent routes in the looser decks could not execute.

Validity and polarity are separate questions. Blink plus an ETB creature is valid and positive. Blink plus a creature carrying +1/+1 counters is valid and negative. Blink plus harmful counters is valid and positive for a different reason. Keep negative, mixed, broken and unknown connections; they prevent the same false inference from being made twice.

---

## 8. MODULES

A package or subsystem carries a contract:

```yaml
contract:
  purpose:
  accepts:
  guarantees:
  may_produce:
  exposes:
  required_operations:
  startup:
  cadence:
  limiting_resource:
  footprint: {total_slots, unique_required_roles, narrow_cards, independently_useful_cards, commander_supplied_roles, interchangeable_slots}
  membership: [{unit, contribution, required, replaceable, shared_with, contention_notes}]
  maturity:
  emergent_outputs:
  failure_points:
  vulnerable_domains:
  alternative_implementations:
```

> Given these qualified inputs, permissions, costs, timing conditions and state assumptions, this module can produce these outputs at this cadence, with these limits.

Reason through the contract. Reopen the internals only when timing, cost, object state, a qualifier or contention matters.

**Composition:** serial, parallel, convergent, divergent, feedback, redundant, competitive, inhibitory, conditional. Redundancy asks two questions: do several implementations reach the same output, and do they fail to the same condition?

**Maturity:** fragment → conditional_package → complete_package → repeatable_engine → self_feeding_engine → closed_loop_candidate → verified_loop → payoff_complete_engine → resilient_engine. A loop is verified only when costs, capacities, timing, state restoration and termination all close, not when the graph returns to its start.

**Width.** A module is as wide as its groups have alternatives. A sacrifice mesh is wide: its cost group accepts any expendable body, and it exposes `permanent.sacrifice`, `battlefield.leave`, and `permanent.dies` and `graveyard.enter` when qualified. Same-name recast through Twinning Glass ("{1}, {T}: You may cast a spell from your hand without paying its mana cost if it has the same name as a spell that was cast this turn") is narrow, because every group has one alternative:

```yaml
operation:
  id: twinning_glass.cast
  kind: activate
  initiation:
    requirement_groups:
      - {id: g_history, class: history, alternatives: ["spell.cast named X this turn, by any player"]}
      - {id: g_card, class: access, alternatives: ["castable card named X in your hand"]}
      - {id: g_mana, class: cost, alternatives: ["mana {1}"]}
      - {id: g_tap, class: cost, alternatives: ["Twinning Glass untapped"]}
    cost: {method: without_paying_mana_cost, additional: "still owed"}
  result:
    produces: ["spell.cast named X from hand"]
  capacity: ["Twinning Glass tap capacity, renews on untap"]
```

A copied spell does not satisfy `g_history`. A bounced token cannot satisfy `g_card`. Entering as a copy establishes no cast history. Another alternative cost cannot be combined with this method.

---

## 9. DERIVED, NEVER STORED

Compute these from units, operations, state and connections. Storing them creates a second copy of a fact that can drift.

| Derived view | Computed from |
|---|---|
| A unit's interface and relations | its operations' groups and results |
| Roles: generator, listener, sink, converter, enabler, multiplier, repeater, resetter, bridge, payoff, protector, cycle closer, interaction | graph position in the current deck; a card may hold several and they change by deck |
| Event facets | the base event, `implies`, and the snapshot |
| Interfaces opened or closed by a type change | characteristic effects and hook qualifiers |
| State reinterpretation | persisting state and the changing set of interpreters |
| Resource lifecycle | an object's non-destructive uses ordered before its destructive ones |
| Module-to-module relations: feeds, amplifies, reloads, protects, reenables, completes, bridges, competes, depletes, resets beneficially or harmfully, cancels a liability, imposes tempo, grants an opponent reuse | primitive relations plus polarity |
| Hook economy: producers, receivers, scarcity, surplus, stranded outputs, overloaded sinks | hook counts across a pool |
| Failure-domain diversity | `vulnerable_domains` across redundant modules |
| Completion distance | the smallest unsatisfied group in a fragment |
| State economy | state created, consumed, destroyed, reloaded, reinterpreted or bypassed by modules |

Because mechanics are stored as qualified structure and not as flat role tags, a collection can be searched for structure:

- leave-listeners that require neither death, a graveyard destination, nor a prior link;
- effects that grant a predicate another owned operation selects on;
- state that survives a characteristic change and has more than one interpreter;
- copy effects whose exceptions a later owned copy effect can inherit;
- objects with a non-destructive use available before a destructive one;
- redundant modules that share one failure domain, and an implementation on another axis;
- hooks with many producers and few receivers, and converters that would make them useful.

---

## 10. ROUTE PATTERNS

Routes are patterns over operations and the persistence table. They compress reasoning and are not primitives.

**New-object routes.** Each buys fresh entry and sheds object-bound state. Charge what is lost.

| Route | Cast | Notes |
|---|---|---|
| Blink, reinstantiation | no | Fresh entry hooks. Cast-dependent choices are not made (a Room returns with both doors locked). Ordinary tokens do not return. |
| Bounce then recast | yes | Hand access only, then a real cost and a real cast. |
| Reanimation, direct return | no | Unless the route explicitly casts. |
| Recursion | varies | Graveyard to hand, battlefield, exile or stack. Not all recursion is reanimation or casting. |
| Temporary-deployment laundering | n/a | Warp, evoke, unearth-like: make a new object before the tracked liability collects. Verify the tracking. |
| Face-down conversion | no | Returns face up. No turn-face-up event occurred. |
| Land reset and replay | no | Repeats entry, configuration and entry counters. Costs a land drop and tempo. |
| Offensive reset | either | Same accounting on an opponent's permanent. Can reload their entries. |

**Same-object routes.** Each changes characteristics while state stays.

| Route | What it does |
|---|---|
| Eligibility bridge | A temporary predicate exists only to let another operation select the object. |
| Reclassification defense, refuge form | The object leaves a hostile selector before it checks. |
| Same-object copy, liability decoupling | Text acquired without entry. Check the sign of absent on-entry state. |
| Heritable phenotype | Copy exceptions accumulate through later copies. |
| State reinterpretation | Old state, new interpreter. |
| State-gate recharge | Remove the state that blocks a permission (persist's −1/−1 counter). |

**Consumption routes.**

| Route | Shape |
|---|---|
| Sacrifice | eligible permanent → sacrifice (cost or effect) → departure → destination → possible death and graveyard facets → listeners |
| Token-sacrifice | generator → token entry → expendable supply → outlet → hooks → payoff → possible replenishment |
| Harvest → transition → redeploy | take a non-destructive use (tap, attack), then sacrifice, bounce or reset the object |
| Departure → residue | a leave-listener turns the departure into new stock for another module |

**Named mechanics as decompositions.** Evoke: alternative-cost cast → entry → sacrifice trigger → response window. Prepared: designation gained → linked spell copy and permission → copy cast → designation consumed; becoming a copy of a prepare card does not confer it. Sneak: unblocked attacker returned as an additional cost → real cast → enters tapped and attacking, not declared. Warp: discounted cast → entry → delayed exile → later cast permission. Copy family, never merged: spell copy on the stack · copy a card and cast it · ability copy · token copy · enters as a copy · existing permanent becomes a copy · permanent spell copy resolving as a token.

---

## 11. ANNOTATION PROCEDURE

1. Obtain exact Oracle text and record evidence and its status.
2. Split the card into abilities only where that improves connection precision.
3. For each ability that matters, write an Operation: requirement groups (one per trigger with its alternatives inside, one per cost component, one per target class, one per condition), amplifiers, result.
4. Add timing, cost or choice detail only where it changes a connection.
5. Add an Object, characteristic effects, State or a Transition only where continuity, copying, type change or stored state changes the answer.
6. Connect outputs to requirement groups after the three checks. Mark conditional, latent, incompatible and unknown connections as such.
7. Collapse verified recurring routes into modules with contracts.
8. Derive roles and the views in section 9. Hand the graph to evaluation.

Do not record speculative combo routes as verified modules, every conceivable use of an object, implied facets, or anything that encodes "good", "bad", "staple" or power level.

---

## 12. ACCEPTANCE TESTS

Status tags on rules claims:

- **RC** — rule text re-read on 2026-10-06; rule number given.
- **OC** — depends on a named card's Oracle text, checked against Scryfall data of 2026-10-02.
- **NC** — checked against the Secrets of Strixhaven release notes, 2026-10-05.
- **IC** — instance check required: true only for particular card pairings or timing.
- **RU** — standard rules behaviour not yet re-read. None remain in this suite.
- **DR** — design requirement on the ontology, not a rules claim.

RC, OC and NC theses are normative. An IC thesis is normative about representation only: the ontology must be able to express the line, and the rules claim holds per instance. DR theses constrain the ontology and assert nothing about the rules.

**Editions read.** Rule text came from online copies of the Comprehensive Rules of different dates: November 2025 for 702.63a, 704.5, 707 and 714; June 2024 for 400.7 and 603; October 2022 for 122, 607, 611 and 614; the copy of 702.32a showed no date. The edition in force at this writing is dated 25 September 2026 and could not be read past rule 121. These rules are long-standing, but confirm number and wording against the current edition before treating a citation as final.

### 12.1 The gate rule

A conforming implementation distinguishes:

- alternatives inside one trigger from separate requirements (Pactdoll Terror fires on its own entry alone);
- a required input from an amplifier (a mana source is not a dependency of an X spell);
- two abilities on one card (an input to its counter trigger is not connected to a payoff on its entry trigger);
- a qualified listener from a similar one;
- a use limit from a timing window ("once each turn" from "only during your turn");
- a group the card satisfies itself from one that needs another unit;
- sacrifice as a cost from sacrifice on resolution, and a returned attacker paid as a cost from the later permanent entering attacking;
- an alternative base cost from additional costs that still apply; restricted from unrestricted mana; cost reduction from mana generation; tap capacity spent from a permanent consumed;
- trigger creation from trigger resolution; end step from end of combat; precombat main from beginning of combat; a permission that expires before the next opportunity.

### 12.2 Events and facets

It distinguishes every pair listed at the end of section 4.3, and also: same name, same type, shared type and chosen type · one departure satisfying several facets from several departures · a threshold crossed from a threshold held.

### 12.3 The persistence table

It distinguishes: blink of a creature with +1/+1 counters (loss) from blink of one with harmful counters (cleansing) · finality-counter cleansing from counter removal · blink from bounce and recast · phasing from a reset · laundering a warp or evoke liability from letting it collect · face-down reinstantiation from turning face up · bouncing a Vivid land as reload plus a land drop · sacrificing tokens as event generation and population loss · a token copy from an existing permanent becoming a copy · current from copiable characteristics · copied characteristics from counters, status, attachments, buffs, tracked effects and history · inherited copy exceptions from ordinary modifications.

### 12.4 State-reinterpretation suite

Derivable without hard-coding Halcyon Glaze or Irma. Numbers match 3.0.1.

| # | Thesis | Status |
|---|---|---|
| 1 | Object, characteristics, state and history are separable. | DR |
| 2 | Halcyon Glaze oscillates between creature and noncreature without changing zones. | OC |
| 3 | Its counters stay while inert and matter again when it is a creature. | RC 122.1a, 122.2 |
| 4 | Losing the creature predicate detaches Equipment and makes creature-only Auras illegal. | RC 704.5m, 704.5n |
| 5 | An effect an Equipment trigger already created outlasts the attachment when its duration says so. | RC 611.2a, 611.2c · IC |
| 6 | Independent sources keep a predicate true after one expires. | RC 611.2a |
| 7 | Additive type effects create multi-interface objects. | OC · IC |
| 8 | Becoming a land can defend against nonland- or creature-restricted effects when timing permits. | IC |
| 9 | One entry satisfies several type-qualified listeners; later type changes create no entry. | RC 603.6a |
| 10 | One departure satisfies several facets by pre-departure characteristics. | RC 603.10a |
| 11 | An animated Halcyon Glaze that is bounced satisfies creature-leave listeners. | OC · RC 603.10a |
| 12 | Irma copying a creature acquires its text without its entry. | OC · RC 614.1c, 603.6d |
| 13 | On-entry counters are therefore absent. | RC 614.1c · IC (see 37) |
| 14 | Copying a back face does not make Irma double-faced; her name exception changes legend-rule outcomes. | OC · RC 707.8 |
| 15 | Animation makes a land eligible for Irma, who then becomes the plain land. | OC · RC 707.2 |
| 16 | A creature Saga is copied as characteristics while Irma's counters stay. | RC 707.2 |
| 17 | Lore counters persist across copy identities and matter again under another Saga. | RC 122.2 |
| 18 | Existing counters create no crossing; preloading to N−1 and adding one does. | RC 714.2b |
| 19 | Final-chapter recycling is representable where a verified window permits it. | IC |
| 20 | Precombat-main lore progression can make a beginning-of-combat escape too late. | OC · RC 714.3b |
| 21 | Same-object change preserves state; a new object resets it. | RC 400.7, 122.2 |
| 22 | Copy exceptions become part of the copiable set. | RC 707.9b |
| 23 | Copycrook and Irma copies accumulate copy-added abilities. | OC · RC 707.9b |
| 24 | A token-creation replacement copying an Irma phenotype creates objects that enter and initialize. | IC |
| 25 | A nonlegendary copy modification can seed a nonlegendary population. | OC · RC 707.9b |
| 26 | Population rewriting inherits the seed's copiable set, not a tracked effect bound to the seed. | IC |
| 27 | Independent triggers choose different copy targets when scope is per trigger. | RC 603.3d |
| 28 | Independent leave-text can be borrowed and cashed out by bouncing the copier. | RC 603.10a · IC |
| 29 | Death-only, graveyard-only and link-dependent leave-text must be filtered out. | RC 607.2a |
| 30 | Prepared is a designation with a link, distinct from copied characteristics. | NC |
| 31 | A borrowed Adventure characteristic gives no later casting route once the copy effect ends. | RC 400.7 |
| 32 | Copying a modified object separates copiable from noncopiable. | RC 707.2 |
| 33–35 | State reinterpretation and heritable phenotype are discoverable as general architectures, and construction can search for them structurally. | DR |
| 36 | An object holding lore counters at or above the final chapter number that becomes a copy of a Saga is sacrificed at the next state check. | RC 714.4, 704.5s |
| 37 | Absent on-entry state removes a presence-driven liability (vanishing: a permanent without time counters that becomes a copy of one with vanishing stays indefinitely) and triggers an absence-driven one (fading). | RC 702.32a, 702.63a |

### 12.5 Deck-derived tests

- **Ashling / Jegantha:** evoke cast, entry, evoke sacrifice, token-copy entry, recursion and recast are distinct. A created copy inherits no cast history. Companion legality is a deck constraint, not a card interaction. A sacrifice outlet and a go-wide payoff can both be valid and antagonistic.
- **Dina:** one death feeds several listeners without becoming several deaths. Persist's counter is a rechargeable gate. Tapping a body before sacrificing it adds lifetime value without paying a destructive cost twice.
- **TMNT:** Irma keeps counters across copies. Sneak's bounce precedes the real cast. Twinning Glass needs genuine same-name cast history and a castable card in hand.
- **Sharuum:** blink and bounce-recast expose different hooks. Tokens may fail return routes. Animation opens creature-only reset, sacrifice and copy interfaces.
- **Brigid:** warp plus blink cancels the liability only when the new object breaks tracking. A creature population is tap capacity as well as combat population. Untap effects replenish capacity.
- **Rootha:** spell copy and spell cast stay distinct. A prepared copy is really cast. Mana throughput and spell throughput are different resources until something converts one into the other.
- **Necrobloom:** an earthbent land is land and creature with counters and competing capacities. Its return after death is a new land without them. A dredged draw is not a draw. Land replay charges land deployment.

### 12.6 Anti-overengineering

The cards named in section 2 must stay simple. A proposed new field is rejected, derived or moved to an extension unless it improves a recommendation, a compression or a connection.

---

## 13. COMPATIBILITY WITH 3.0.1

Every 3.0.1 record is a 3.1.0 record, a kind of one, or a derived view. Field names are kept wherever a field survives. Existing records need no rewrite; migrate one only when the compact form changes a query or a recommendation.

| 3.0.1 | 3.1.0 |
|---|---|
| interaction_unit | unit; `interface` and `relations` become roll-ups, still writable for units without operations |
| hook, hook_implication | hook, with `implies` (a bare id, or `{hook, projection, condition}`) |
| operation | operation |
| requirement, requirement_group, condition_check | requirement group, with `class` and `checkpoint` |
| amplifier | amplifier |
| timing_profile | timing detail |
| cost_protocol, cost_component | cost detail; components are cost-class groups |
| permission_profile | state, kind `permission` |
| choice_protocol | choice |
| object_semantics | object |
| characteristic_effect, copiable_profile | characteristic_effect with `copiable` |
| copy_operation | transition with a copy characteristic effect |
| interface_transition | derived (section 9) |
| state_record | state |
| persistence_profile | the table in 6.4 plus `persistence` exceptions |
| state_interpreter | `interpreter` field; reinterpretation is derived |
| threshold_event | `threshold.crossed` (event) and `threshold.reached` (state) |
| state_based_consequence | operation, kind `state_based` |
| designation, linkage, tracked_effect, capacity_window | state, kinds `designation`, `link`, `tracked_effect`, `capacity` |
| attachment_profile, effect_instance_profile | state, kinds `attachment` and `tracked_effect` |
| initialization_profile | `state.created_by` marked `on_entry` |
| object_transition | transition |
| event_pattern | section 4.3: one event, implied facets, snapshot |
| form_profile | `object.forms` |
| event_rewrite | operation, kind `replacement`, `result.rewrites` |
| resource_lifecycle | derived |
| comparison, viability, connection | unchanged |
| module_contract, membership, footprint | contract |

**Changes in 3.1.1.** No record or field was removed.

- The persistence rule now says object-bound state persists *by default*, ending early when the operation changes it or its own condition fails (section 1, section 6.4).
- `card_copy` added to `object.substrate`, with a table row for a card copy that is made and then cast.
- Table wording tightened: blink separated from reanimation, "face or profile changes" for transform and turning face up, and "the card's own characteristics in the new zone" in place of "printed".
- `hook.implies` may carry `{hook, projection, condition}` where a bare identifier is not enough.
- Every rules claim in 12.4 was re-read and cited; none is left as unchecked standard behaviour. The editions read are listed there.

What was not compressed, because it is irreducible: the seven relations, the hook vocabulary and qualifier axes, the gate rule, the cost distinctions, the copiable-characteristics rule, the rows of the persistence table, connection status, strength and polarity, the module contract, and the tests.

**Versioning.** Identifiers are lower-case dotted names; custom additions use `custom.namespace.identifier`. Minor releases may add vocabulary, route patterns, optional fields and tests. A major release is required when an established meaning or the gate or persistence rule changes incompatibly. Add a primitive only when existing structures cannot describe a deck-relevant connection without distortion.

---

## 14. GOVERNING PRINCIPLES

- Model deck relationships, not the game.
- Keep enough rules precision to tell real connections from false ones, and no more.
- Connect operations, not cards. Require every group, accept any alternative, keep amplifiers out of both.
- Treat timing and cost as mechanics. A cost can create events before anything resolves.
- Separate the object, its characteristics and its state. Ask first whether the same object continues.
- Let state persist without assuming its meaning persists, and ask what its absence does.
- One event with many facets is one event. A replaced event did not occur.
- Record each fact once. Derive the rest.
- Keep negative, mixed, broken and unknown connections.
- Collapse proven routes into modules with contracts, and keep modules openable.
- Keep card quality, physical allocation and live strategy out of the ontology.
- Judge the ontology by whether it produces better deck analysis and finds interactions worth caring about.

The ontology should make strange machines discoverable without making ordinary cards complicated.

**END**
