# Semantic readiness audit: Dina (v0.2)

Nonland cards: **63**. Candidate operations: **105**. Contracts ready for review: **50**; blocked: **55**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 51, machine_parsed 12. Unread clauses across the deck: **80**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 26 |
| eligible after review | 25 |
| reviewable, no executable action | 12 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 1 | 1 | 0 | 1 | 0 | 0.3.0 action missing text or disagrees (1) |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 8 | 8 | 3 | 5 | 0 | 0.3.0 action missing text or disagrees (3); unbound branch/condition/scaling/modes (2); multi-face clause not located on one face (1) |
| land_search | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (2) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 13 | 13 | 6 | 7 | 0 | 0.3.0 action missing text or disagrees (7); no effect recorded (2); mana production not typed (1) |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### landfall

- **Bloodghast** (blocked): Landfall — Whenever a land you control enters, you may return this card from your graveyard to the battlefield.

### repeatable_recursion

- **Along the Crooked Way** (ready_for_review): When this enchantment enters, return target creature card from your graveyard to your hand.
- **Bloodghast** (blocked): Landfall — Whenever a land you control enters, you may return this card from your graveyard to the battlefield.
- **Cauldron of Essence** (ready_for_review): {1}{B}{G}, {T}, Sacrifice a creature: Return target creature card from your graveyard to the battlefield. Activate only as a sorcery.
- **Defiled Crypt // Cadaver Lab** (blocked): When you unlock this door, return target creature card from your graveyard to your hand.
- **Nether Traitor** (blocked): Whenever another creature is put into your graveyard from the battlefield, you may pay {B}. If you do, return this card from your graveyard to the battlefield.
- **Ninja Teen** (ready_for_review): You may cast creature spells from your graveyard using their sneak abilities.
- **Veinwitch Coven** (blocked): Whenever you gain life, you may pay {B}. If you do, return target creature card from your graveyard to your hand.
- **Witch of the Moors** (blocked): At the beginning of your end step, if you gained life this turn, each opponent sacrifices a creature of their choice and you return up to one target creature card from yo

### land_search

- **Sakura-Tribe Elder** (blocked): Sacrifice this creature: Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.
- **Wight of the Reliquary** (blocked): {T}, Sacrifice another creature: Search your library for a land card, put it onto the battlefield tapped, then shuffle.

### sacrifice_conversion

- **Cauldron of Essence** (ready_for_review): {1}{B}{G}, {T}, Sacrifice a creature: Return target creature card from your graveyard to the battlefield. Activate only as a sorcery.
- **Dimir House Guard** (blocked): Sacrifice a creature: Regenerate this creature.
- **Dina, Essence Brewer** (blocked): {2}, {T}, Sacrifice another creature: You gain X life and put X +1/+1 counters on target creature you control, where X is the sacrificed creature's power.
- **Dina, Soul Steeper** (blocked): {1}, Sacrifice another creature: Dina gets +X/+0 until end of turn, where X is the sacrificed creature's power.
- **Haywire Mite** (ready_for_review): {G}, Sacrifice this creature: Exile target noncreature artifact or noncreature enchantment.
- **Lord Dregg, Insect Invader** (ready_for_review): {3}{G}, Sacrifice a token: Draw a card.
- **Pizza Face, Gastromancer** (ready_for_review): {10}, {T}, Sacrifice Pizza Face: You gain 15 life.
- **Priest of Forgotten Gods** (blocked): {T}, Sacrifice two other creatures: Any number of target players each lose 2 life and sacrifice a creature of their choice. You add {B}{B} and draw a card. (Activate only
- **Sakura-Tribe Elder** (blocked): Sacrifice this creature: Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.
- **Twitching Doll** (blocked): {T}, Sacrifice this creature: Create a 2/2 green Spider creature token with reach for each counter on this creature. Activate only as a sorcery.
- **Warren Soultrader** (ready_for_review): Pay 1 life, Sacrifice another creature: Create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")
- **Wight of the Reliquary** (blocked): {T}, Sacrifice another creature: Search your library for a land card, put it onto the battlefield tapped, then shuffle.
- **Woe Strider** (ready_for_review): Sacrifice another creature: Scry 1.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Defiled Crypt // Cadaver Lab | 2 | 0 | 2 | 0 | partial | 4 | 0 | blocked | repeatable_recursion |
| Dimir House Guard | 1 | 0 | 1 | 1 | partial | 3 | 0 | blocked | sacrifice_conversion |
| Buzzard-Wasp Colony | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Loading Zone | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Nether Traitor | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked | repeatable_recursion |
| Sothera, the Supervoid | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| The Hunger Tide Rises | 2 | 0 | 2 | 0 | partial | 2 | 0 | blocked |  |
| Twitching Doll | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked | sacrifice_conversion |
| Unbury | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Wight of the Reliquary | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | land_search, sacrifice_conversion |
| Witherbloom Charm | 4 | 0 | 4 | 3 | partial | 2 | 0 | blocked |  |
| Withering Curse | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Awakening Zone | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Bitterbloom Bearer | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Immoral Bargain | 1 | 0 | 1 | 2 | partial | 1 | 0 | blocked |  |
| Jadar, Ghoulcaller of Nephalia | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked |  |
| Pest Infestation | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Priest of Forgotten Gods | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | sacrifice_conversion |
| Rise of the Witch-king | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Sakura-Tribe Elder | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search, sacrifice_conversion |
| Toxic Deluge | 1 | 0 | 1 | 2 | partial | 1 | 0 | blocked |  |
| Veinwitch Coven | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Victimize | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Witch of the Moors | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Great Fierce Bee | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Mirkwood Bats | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Along the Crooked Way | 3 | 1 | 2 | 2 | partial | 2 | 0 | eligible after review | repeatable_recursion |
| Smothering Abomination | 2 | 1 | 1 | 2 | partial | 2 | 0 | eligible after review |  |
| Woe Strider | 2 | 2 | 0 | 2 | partial | 2 | 0 | eligible after review | sacrifice_conversion |
| Blight Mound | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Defiling Daemogoth | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Dina, Essence Brewer | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Dina, Soul Steeper | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Essenceknit Scholar | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Gorma, the Gullet | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Lord Dregg, Insect Invader | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Pizza Face, Gastromancer | 3 | 2 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Plumb the Forbidden | 3 | 1 | 2 | 2 | partial | 1 | 0 | eligible after review |  |
| South Wind Avatar | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Springleaf Parade | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Starscape Cleric | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Cauldron of Essence | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion, sacrifice_conversion |
| Chomping Changeling | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Deadly Dispute | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Elvish Mystic | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Haywire Mite | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Moldervine Reclamation | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Pestbrood Sloth | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Vicious Rivalry | 1 | 1 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Ninja Teen | 6 | 4 | 2 | 0 | partial | 6 | 0 | reviewable, no executable action | repeatable_recursion |
| Bloodghast | 3 | 2 | 1 | 1 | partial | 3 | 0 | reviewable, no executable action | landfall, repeatable_recursion |
| Tendershoot Dryad | 2 | 2 | 0 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Beledros Witherbloom | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Pest Rescuer | 2 | 1 | 1 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Al Bhed Salvagers | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Blood Artist | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Mazirek, Kraul Death Priest | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Nadier's Nightblade | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Pawn of Ulamog | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Warren Soultrader | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action | sacrifice_conversion |
| Zulaport Cutthroat | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
