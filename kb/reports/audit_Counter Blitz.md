# Semantic readiness audit: Counter Blitz (v0.2)

Nonland cards: **63**. Candidate operations: **99**. Contracts ready for review: **25**; blocked: **74**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 55, machine_parsed 8. Unread clauses across the deck: **88**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 40 |
| eligible after review | 12 |
| reviewable, no executable action | 10 |
| no candidate operations | 1 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 1 | 1 | 1 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| land_search | 3 | 3 | 0 | 3 | 0 | 0.3.0 action missing text or disagrees (3); unbound branch/condition/scaling/modes (1) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 0 | 0 | 0 | 0 | 0 |  |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### landfall

- **Tireless Tracker** (ready_for_review): Landfall — Whenever a land you control enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.")

### repeatable_recursion

- **Luminous Broodmoth** (blocked): Whenever a creature you control without flying dies, return it to the battlefield under its owner's control with a flying counter on it.
- **Summoner's Sending** (blocked): At the beginning of your end step, you may exile target creature card from a graveyard. If you do, create a 1/1 white Spirit creature token with flying. Put a +1/+1 count

### land_search

- **Farseek** (blocked): Search your library for a Plains, Island, Swamp, or Mountain card, put it onto the battlefield tapped, then shuffle.
- **Rampant Rejuvenator** (blocked): When this creature dies, search your library for up to X basic land cards, where X is this creature's power, put them onto the battlefield, then shuffle.
- **Scholar of New Horizons** (blocked): {T}, Remove a counter from a permanent you control: Search your library for a Plains card and reveal it. If an opponent controls more lands than you, you may put that car

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Summon: Magus Sisters | 3 | 0 | 3 | 0 | partial | 4 | 0 | blocked |  |
| Everflowing Chalice | 1 | 0 | 1 | 1 | partial | 3 | 0 | blocked |  |
| Farewell | 5 | 0 | 5 | 4 | partial | 3 | 0 | blocked |  |
| Summon: Yojimbo | 2 | 0 | 2 | 0 | partial | 3 | 0 | blocked |  |
| Yuna's Decision | 3 | 0 | 3 | 2 | partial | 3 | 0 | blocked |  |
| Blitzball Stadium | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Collective Effort | 4 | 0 | 4 | 4 | partial | 2 | 0 | blocked |  |
| Fathom Mage | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Fight Rigging | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Generous Patron | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Gyre Sage | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Incubation Druid | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Maester Seymour | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Rampant Rejuvenator | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | land_search |
| Resourceful Defense | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Rikku, Resourceful Guardian | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Scholar of New Horizons | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | land_search |
| Summon: Valefor | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Together Forever | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Tromell, Seymour's Butler | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Yuna, Grand Summoner | 3 | 0 | 3 | 1 | partial | 2 | 0 | blocked |  |
| An Offer You Can't Refuse | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Chocobo Knights | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Destroy Evil | 3 | 0 | 3 | 2 | partial | 1 | 0 | blocked |  |
| Farseek | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Gatta and Luzzu | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Grateful Apparition | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Hardened Scales | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Inspiring Call | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Lord Jyscal Guado | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Luminous Broodmoth | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Path of Discovery | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Path to Exile | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Promise of Loyalty | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Protection Magic | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Shelinda, Yevon Acolyte | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Summoner's Sending | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Three Visits | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Yuna's Whistle | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Inexorable Tide | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Walking Ballista | 2 | 1 | 1 | 1 | partial | 2 | 0 | eligible after review |  |
| Chasm Skulker | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Duskshell Crawler | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Sphere Grid | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Wakka, Devoted Guardian | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Bane of Progress | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Damning Verdict | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| O'aka, Traveling Merchant | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Pull from Tomorrow | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Tireless Tracker | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | landfall |
| Endless Detour | 0 | 0 | 0 | 1 | partial | 1 | 0 | no candidate operations |  |
| Altered Ego | 2 | 1 | 1 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Forgotten Ancient | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Sin, Unending Cataclysm | 2 | 2 | 0 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Summon: Ixion | 2 | 1 | 1 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Tidus, Yuna's Guardian | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Auron, Venerated Guardian | 2 | 1 | 1 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Bred for the Hunt | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Kimahri, Valiant Guardian | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Lulu, Stern Guardian | 2 | 1 | 1 | 1 | partial | 1 | 0 | reviewable, no executable action |  |
| Sunscorch Regent | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
