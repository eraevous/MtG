# Semantic readiness audit: Vraska (v0.2)

Nonland cards: **65**. Candidate operations: **104**. Contracts ready for review: **57**; blocked: **47**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 34, machine_parsed 31. Unread clauses across the deck: **41**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| eligible after review | 41 |
| blocked | 20 |
| no candidate operations | 3 |
| reviewable, no executable action | 1 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 0 | 0 | 0 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 1 | 1 | 1 | 0 | 0 |  |
| land_search | 3 | 3 | 0 | 3 | 0 | 0.3.0 action missing text or disagrees (3); zone transition unbound (1) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 12 | 14 | 11 | 3 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1); no effect recorded (1) |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### repeatable_recursion

- **Gossip's Talent** (ready_for_review): {3}{U}: Level 3 — Whenever a creature you control deals combat damage to a player, you may exile it, then return it to the battlefield under its owner's control.

### land_search

- **Emergency Eject** (blocked): Destroy target nonland permanent. Its controller creates a Lander token. (It's an artifact with "{2}, {T}, Sacrifice this token: Search your library for a basic land card
- **Fountainport Bell** (blocked): When this artifact enters, you may search your library for a basic land card, reveal it, then shuffle and put that card on top.
- **Strixhaven Skycoach** (blocked): When this Vehicle enters, you may search your library for a basic land card, reveal it, put it into your hand, then shuffle.

### sacrifice_conversion

- **Carrot Cake** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Cryogen Relic** (blocked): {1}{U}, Sacrifice this artifact: Put a stun counter on up to one target tapped creature. (If a permanent with a stun counter would become untapped, remove one from it ins
- **Elsewhere Flask** (blocked): Sacrifice this artifact: Choose a basic land type. Each land you control becomes that type until end of turn.
- **Fountainport Bell** (ready_for_review): {1}, Sacrifice this artifact: Draw a card.
- **Instant Ramen** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Melded Moxite** (ready_for_review): {3}, Sacrifice this artifact: Create a tapped 2/2 colorless Robot artifact creature token.
- **Mouser Foundry** (blocked): {4}{R}, Sacrifice this artifact: It deals 3 damage to target creature.
- **Omni-Cheese Pizza** (ready_for_review): {1}, {T}, Sacrifice this artifact: Add one mana of any color.
- **Omni-Cheese Pizza** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Retrofitter Foundry** (ready_for_review): {1}, {T}, Sacrifice a Servo: Create a 1/1 colorless Thopter artifact creature token with flying.
- **Retrofitter Foundry** (ready_for_review): {T}, Sacrifice a Thopter: Create a 4/4 colorless Construct artifact creature token.
- **Sai, Master Thopterist** (ready_for_review): {1}{U}, Sacrifice two artifacts: Draw a card.
- **Sewer-veillance Cam** (ready_for_review): {3}{U}, Sacrifice this artifact: Draw two cards.
- **Spicy Oatmeal Pizza** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Rush of Inspiration // Crackling Falls | 2 | 0 | 2 | 5 | partial | 4 | 0 | blocked |  |
| Pinnacle Emissary | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Prismari Charm | 4 | 0 | 4 | 3 | partial | 2 | 0 | blocked |  |
| Blasphemous Act | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked |  |
| Desculpting Blast | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Drill Too Deep | 3 | 0 | 3 | 2 | partial | 1 | 0 | blocked |  |
| Emergency Eject | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Flame Fusillade | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Galvanic Blast | 2 | 0 | 2 | 2 | partial | 1 | 0 | blocked |  |
| Geistwave | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Generous Gift | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Mouser Attack! | 3 | 0 | 3 | 2 | partial | 1 | 0 | blocked |  |
| Plunder the Trollshaws | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Reality Shift | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Resculpt | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Shore Up | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Strixhaven Skycoach | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Warmaker Gunship | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Saheeli, Consul of Oversight | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Stridehangar Automaton | 1 | 0 | 1 | 0 | machine_parsed | 0 | 0 | blocked |  |
| Gossip's Talent | 3 | 2 | 1 | 1 | partial | 2 | 0 | eligible after review | repeatable_recursion |
| Guidelight Matrix | 3 | 1 | 2 | 3 | partial | 2 | 0 | eligible after review |  |
| Bespoke Bō | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Bident of Thassa | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Cori-Steel Cutter | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Elsewhere Flask | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Fountainport Bell | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | land_search, sacrifice_conversion |
| Melded Moxite | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Mouser Foundry | 2 | 1 | 1 | 3 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Retrofitter Foundry | 4 | 3 | 1 | 4 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Saheeli, Sublime Artificer | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Sokka, Bold Boomeranger | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Spicy Oatmeal Pizza | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Talisman of Progress | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Whirler Rogue | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Boosted Sloop | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Boros Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Carrot Cake | 2 | 1 | 1 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Coruscation Mage | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Counterspell | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Craterclaw Colossus | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Cryogen Relic | 2 | 1 | 1 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Curiosity Crafter | 2 | 2 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Dreams of Laguna | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Improvised Club | 2 | 1 | 1 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Instant Ramen | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Omni-Cheese Pizza | 3 | 3 | 0 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Ooze Spill | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Raff, Weatherlight Stalwart | 2 | 1 | 1 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Reckless Fireweaver | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sai, Master Thopterist | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Sami, Ship's Engineer | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sewer-veillance Cam | 2 | 2 | 0 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Springleaf Drum | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Thopter Spy Network | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Uthros Scanship | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Vraska, Soul of Stone | 2 | 2 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| White Auracite | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Wurmwall Sweeper | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Etherium Sculptor | 0 | 0 | 0 | 0 | machine_parsed | 0 | 0 | no candidate operations |  |
| Geist of Saint Thalia | 0 | 0 | 0 | 0 | machine_parsed | 0 | 0 | no candidate operations |  |
| Lumen-Class Frigate | 0 | 0 | 0 | 0 | machine_parsed | 0 | 0 | no candidate operations |  |
| Thorin Oakenshield | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
