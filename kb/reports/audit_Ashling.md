# Semantic readiness audit: Ashling (v0.2)

Nonland cards: **63**. Candidate operations: **96**. Contracts ready for review: **40**; blocked: **56**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 49, machine_parsed 14. Unread clauses across the deck: **84**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 29 |
| eligible after review | 25 |
| reviewable, no executable action | 7 |
| no candidate operations | 2 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 1 | 1 | 0 | 1 | 0 | unbound branch/condition/scaling/modes (1); 0.3.0 action missing text or disagrees (1) |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 4 | 4 | 2 | 2 | 0 | unbound branch/condition/scaling/modes (2); no effect recorded (1); 0.3.0 action missing text or disagrees (1) |
| land_search | 1 | 1 | 1 | 0 | 0 |  |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 1 | 1 | 1 | 0 | 0 |  |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 1 | 1 | 1 | 0 | 0 |  |

### landfall

- **Omnath, Locus of the Roil** (blocked): Landfall — Whenever a land you control enters, put a +1/+1 counter on target Elemental you control. If you control eight or more lands, draw a card.

### repeatable_recursion

- **Graveshifter** (ready_for_review): When this creature enters, you may return target creature card from your graveyard to your hand.
- **Horde of Notions** (blocked): {W}{U}{B}{R}{G}: You may play target Elemental card from your graveyard without paying its mana cost.
- **Muldrotha, the Gravetide** (blocked): During each of your turns, you may play a land and cast a permanent spell of each permanent type from your graveyard. (If a card has multiple permanent types, choose one 
- **Ninja Teen** (ready_for_review): You may cast creature spells from your graveyard using their sneak abilities.

### land_search

- **Prismatic Undercurrents** (ready_for_review): Vivid — When this enchantment enters, search your library for up to X basic land cards, where X is the number of colors among permanents you control. Reveal those cards, 

### sacrifice_conversion

- **Umbral Collar Zealot** (ready_for_review): Sacrifice another creature or artifact: Surveil 1. (Look at the top card of your library. You may put it into your graveyard.)

### extra_land_drops

- **Prismatic Undercurrents** (ready_for_review): You may play an additional land on each of your turns.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Ashling, Rekindled // Ashling, Rimebound | 4 | 0 | 4 | 3 | partial | 6 | 0 | blocked |  |
| Ashling's Command | 4 | 0 | 4 | 0 | partial | 5 | 0 | blocked |  |
| Arcane Denial | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Ashling, the Limitless | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Faeburrow Elder | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Fertile Ground | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Hoofprints of the Stag | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Incandescent Soulstoke | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Kithkeeper | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Omnath, Locus of the Roil | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked | landfall |
| Splinter's Technique | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Tam, Mindful First-Year | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Unbury | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Witherbloom Charm | 4 | 0 | 4 | 3 | partial | 2 | 0 | blocked |  |
| Blasphemous Act | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked |  |
| Continue? | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Cream of the Crop | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Determined Iteration | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Distant Melody | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Erode | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Fellwar Stone | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Flamebraider | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Horde of Notions | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Mass of Mysteries | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Muldrotha, the Gravetide | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked | repeatable_recursion |
| Risen Reef | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Smokebraider | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Tanufel Rimespeaker | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Vernal Sovereign | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Garruk's Uprising | 3 | 2 | 1 | 2 | partial | 2 | 0 | eligible after review |  |
| Shriekmaw | 1 | 1 | 0 | 1 | partial | 2 | 0 | eligible after review |  |
| Belonging | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Celestial Reunion | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Chromatic Lantern | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Duty Beyond Death | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Firdoch Core | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Foundation Breaker | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Ingot Chewer | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Lamentation | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Mulldrifter | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Chomping Changeling | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Dimir Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Flock Impostor | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Graveshifter | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion |
| Gruul Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Izzet Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Personify | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Relic of Legends | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Rimekin Recluse | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Selesnya Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Simic Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Umbral Collar Zealot | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Twinflame Travelers | 0 | 0 | 0 | 0 | partial | 1 | 0 | no candidate operations |  |
| Yarok, the Desecrated | 0 | 0 | 0 | 0 | partial | 1 | 0 | no candidate operations |  |
| Ninja Teen | 6 | 4 | 2 | 0 | partial | 6 | 0 | reviewable, no executable action | repeatable_recursion |
| Frostcliff Siege | 3 | 1 | 2 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Realmwalker | 3 | 3 | 0 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Maelstrom Wanderer | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Prismatic Undercurrents | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action | land_search, extra_land_drops |
| Urza's Incubator | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Shimmercreep | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
