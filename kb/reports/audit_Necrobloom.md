# Semantic readiness audit: Necrobloom (v0.2)

Nonland cards: **60**. Candidate operations: **112**. Contracts ready for review: **21**; blocked: **91**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 56, machine_parsed 4. Unread clauses across the deck: **98**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 40 |
| eligible after review | 12 |
| reviewable, no executable action | 5 |
| no candidate operations | 3 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 4 | 4 | 2 | 2 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| dredge | 1 | 1 | 0 | 1 | 0 | unbound branch/condition/scaling/modes (1) |
| repeatable_recursion | 11 | 11 | 0 | 11 | 0 | clause is reminder text (7); 0.3.0 action missing text or disagrees (2); multi-face clause not located on one face (1) |
| land_search | 6 | 6 | 1 | 5 | 0 | 0.3.0 action missing text or disagrees (5); unbound branch/condition/scaling/modes (2); operation kind unclassified (1) |
| land_tokens_scaling | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| sacrifice_conversion | 3 | 3 | 2 | 1 | 0 | 0.3.0 action missing text or disagrees (1) |
| self_mill | 5 | 5 | 0 | 5 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (2); multi-face clause not located on one face (1) |
| extra_land_drops | 1 | 1 | 0 | 1 | 0 | multi-face clause not located on one face (1) |

### landfall

- **Avenger of Zendikar** (ready_for_review): Landfall — Whenever a land you control enters, you may put a +1/+1 counter on each Plant creature you control.
- **Ride the Shoopuf** (ready_for_review): Landfall — Whenever a land you control enters, put a +1/+1 counter on target creature you control.
- **The Necrobloom** (blocked): Landfall — Whenever a land you control enters, create a 0/1 green Plant creature token. If you control seven or more lands with different names, create a 2/2 black Zombie
- **Weather Maker** (blocked): Landfall — Whenever a land you control enters, put a charge counter on this artifact.

### dredge

- **The Necrobloom** (blocked): Land cards in your graveyard have dredge 2. (You may return a land card from your graveyard to your hand and mill two cards instead of drawing a card.)

### repeatable_recursion

- **Badgermole Cub** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **Beifong's Bounty Hunters** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **Dai Li Agents** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **Earth Kingdom General** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **Lluwen, Exchange Student // Pest Friend** (blocked): Exile a creature card from your graveyard: Lluwen becomes prepared. Activate only as a sorcery.
- **Pothole Mole** (blocked): When this creature enters, mill three cards, then you may return a land card from your graveyard to your hand. (To mill three cards, put the top three cards of your libra
- **Primary Research** (blocked): When this enchantment enters, return target nonland permanent card with mana value 3 or less from your graveyard to the battlefield.
- **Rockalanche** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **Sandbender's Storm** (blocked): When it dies or is exiled, return it to the battlefield tapped.)
- **The Necrobloom** (blocked): Land cards in your graveyard have dredge 2. (You may return a land card from your graveyard to your hand and mill two cards instead of drawing a card.)
- **Toph, the Blind Bandit** (blocked): When it dies or is exiled, return it to the battlefield tapped.)

### land_search

- **Cultivate** (blocked): Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle.
- **Cycle of Renewal** (blocked): Sacrifice a land. Search your library for up to two basic land cards, put them onto the battlefield tapped, then shuffle.
- **Kodama's Reach** (blocked): Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle.
- **Springbloom Druid** (blocked): When this creature enters, you may sacrifice a land. If you do, search your library for up to two basic land cards, put them onto the battlefield tapped, then shuffle.
- **The Earth King** (ready_for_review): Whenever one or more creatures you control with power 4 or greater attack, search your library for up to that many basic land cards, put them onto the battlefield tapped,
- **You Happen on a Glade** (blocked): • Journey On — Search your library for up to two basic land cards, reveal them, put them into your hand, then shuffle.

### land_tokens_scaling

- **Avenger of Zendikar** (blocked): When this creature enters, create a 0/1 green Plant creature token for each land you control.
- **The Necrobloom** (blocked): Landfall — Whenever a land you control enters, create a 0/1 green Plant creature token. If you control seven or more lands with different names, create a 2/2 black Zombie

### sacrifice_conversion

- **All-Fates Scroll** (blocked): {7}, {T}, Sacrifice this artifact: Draw X cards, where X is the number of differently named lands you control.
- **Aron, Benalia's Ruin** (ready_for_review): {W}{B}, {T}, Sacrifice another creature: Put a +1/+1 counter on each creature you control.
- **Rat King, Pale Piper** (ready_for_review): {2}, Sacrifice a token: Draw a card.

### self_mill

- **Greenhouse // Rickety Gazebo** (blocked): When you unlock this door, mill four cards, then return up to two permanent cards from among them to your hand.
- **Leaves from the Vine** (blocked): I — Mill three cards, then create a Food token. (It's an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.")
- **Pothole Mole** (blocked): When this creature enters, mill three cards, then you may return a land card from your graveyard to your hand. (To mill three cards, put the top three cards of your libra
- **The Necrobloom** (blocked): Land cards in your graveyard have dredge 2. (You may return a land card from your graveyard to your hand and mill two cards instead of drawing a card.)
- **Witherbloom Command** (blocked): • Target player mills three cards, then you return a land card from your graveyard to your hand.

### extra_land_drops

- **Beorn, Reluctant Host // Till and Tend** (blocked): You may play an additional land this turn. (Then exile this card. You may cast the creature later from exile.)

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Final Act | 6 | 0 | 6 | 5 | partial | 5 | 0 | blocked |  |
| Lluwen, Exchange Student // Pest Friend | 2 | 0 | 2 | 0 | partial | 5 | 0 | blocked | repeatable_recursion |
| Greenhouse // Rickety Gazebo | 2 | 0 | 2 | 0 | partial | 4 | 0 | blocked | self_mill |
| The Cruelty of Gix | 2 | 0 | 2 | 0 | partial | 4 | 0 | blocked |  |
| Witherbloom Command | 4 | 0 | 4 | 5 | partial | 4 | 0 | blocked | self_mill |
| Beorn, Reluctant Host // Till and Tend | 1 | 0 | 1 | 0 | partial | 3 | 0 | blocked | extra_land_drops |
| Witch Enchanter // Witch-Blessed Meadow | 3 | 0 | 3 | 2 | partial | 3 | 0 | blocked |  |
| You Happen on a Glade | 3 | 0 | 3 | 2 | partial | 3 | 0 | blocked | land_search |
| Badgermole Cub | 3 | 0 | 3 | 1 | partial | 2 | 0 | blocked | repeatable_recursion |
| Chocobo Kick | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Coiling Rebirth | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Dai Li Agents | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked | repeatable_recursion |
| Dockworker Drone | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Earth Kingdom General | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked | repeatable_recursion |
| Hei Bai, Spirit of Balance | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Old Man Willow | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Origin of Metalbending | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Primary Research | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked | repeatable_recursion |
| Sandbender's Storm | 4 | 0 | 4 | 2 | partial | 2 | 0 | blocked | repeatable_recursion |
| The Necrobloom | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked | landfall, dredge, repeatable_recursion, land_tokens_scaling, self_mill |
| Toph, the Blind Bandit | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked | repeatable_recursion |
| Accursed Marauder | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Assassin's Trophy | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Beifong's Bounty Hunters | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Blacksmith's Skill | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Clifftop Lookout | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Cultivate | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Cycle of Renewal | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Deadly Brew | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Eclipsed Elf | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Eclipsed Kithkin | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Gift of the Viper | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Heritage Reclamation | 4 | 0 | 4 | 3 | partial | 1 | 0 | blocked |  |
| High Perfect Morcant | 2 | 0 | 2 | 2 | partial | 1 | 0 | blocked |  |
| Kodama's Reach | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Lys Alana Dignitary | 1 | 0 | 1 | 2 | partial | 1 | 0 | blocked |  |
| Night's Whisper | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Pothole Mole | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion, self_mill |
| Rockalanche | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Springbloom Druid | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Weather Maker | 4 | 2 | 2 | 4 | partial | 2 | 0 | eligible after review | landfall |
| All-Fates Scroll | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Avenger of Zendikar | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | landfall, land_tokens_scaling |
| Game Over | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Rat King, Pale Piper | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Ride the Shoopuf | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | landfall |
| The Earth King | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review | land_search |
| Twilight Diviner | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Aron, Benalia's Ruin | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Cremate | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Great Forest Druid | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Harmonize | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Mirkwood Pathmaker | 0 | 0 | 0 | 0 | partial | 1 | 0 | no candidate operations |  |
| Mulch | 0 | 0 | 0 | 1 | partial | 1 | 0 | no candidate operations |  |
| Rootborn Defenses | 0 | 0 | 0 | 1 | partial | 1 | 0 | no candidate operations |  |
| Leaves from the Vine | 3 | 1 | 2 | 0 | partial | 3 | 0 | reviewable, no executable action | self_mill |
| Cursed Wombat | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Emil, Vastlands Roamer | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| The Seriema | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Rosie Cotton of South Lane | 2 | 1 | 1 | 1 | partial | 1 | 0 | reviewable, no executable action |  |
