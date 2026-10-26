# Semantic readiness audit: Brigid (v0.2)

Nonland cards: **65**. Candidate operations: **98**. Contracts ready for review: **33**; blocked: **65**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 57, machine_parsed 8. Unread clauses across the deck: **109**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 35 |
| eligible after review | 17 |
| reviewable, no executable action | 13 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 0 | 0 | 0 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 7 | 7 | 1 | 6 | 0 | 0.3.0 action missing text or disagrees (4); cost missing or unparsed (1); unbound branch/condition/scaling/modes (1) |
| land_search | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (1); multi-face clause not located on one face (1) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 5 | 5 | 4 | 1 | 0 | no effect recorded (1); 0.3.0 action missing text or disagrees (1) |
| self_mill | 1 | 1 | 0 | 1 | 0 | multi-face clause not located on one face (1) |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### repeatable_recursion

- **Astelli Reclaimer** (blocked): When this creature enters, return target noncreature, nonland permanent card with mana value X or less from your graveyard to the battlefield, where X is the amount of ma
- **Case of the Uneaten Feast** (blocked): Solved — Sacrifice this Case: Creature cards in your graveyard gain "You may cast this card from your graveyard" until end of turn.
- **Dundoolin Weaver** (blocked): When this creature enters, if you control three or more creatures, return target permanent card from your graveyard to your hand.
- **Golden Argosy** (blocked): Whenever Golden Argosy attacks, exile each creature that crewed it this turn. Return them to the battlefield tapped under their owner's control at the beginning of the ne
- **Salvation Swan** (blocked): Whenever this creature or another Bird you control enters, exile up to one target creature you control without flying. Return it to the battlefield under its owner's cont
- **Serra Paragon** (blocked): Once during each of your turns, you may play a land from your graveyard or cast a permanent spell with mana value 3 or less from your graveyard. If you do, it gains "When
- **Teleportation Circle** (ready_for_review): At the beginning of your end step, exile up to one target artifact or creature you control, then return that card to the battlefield under its owner's control.

### land_search

- **Guardian Sunmare** (blocked): Whenever this creature attacks while saddled, search your library for a nonland permanent card with mana value 3 or less, put it onto the battlefield, then shuffle.
- **Studious First-Year // Rampant Growth** (blocked): Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.

### sacrifice_conversion

- **Boromir, Warden of the Tower** (blocked): Sacrifice Boromir: Creatures you control gain indestructible until end of turn. The Ring tempts you.
- **Carrot Cake** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Guac & Marshmallow Pizza** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Qasali Pridemage** (ready_for_review): {1}, Sacrifice this creature: Destroy target artifact or enchantment.
- **Undergrowth Leopard** (ready_for_review): {1}, Sacrifice this creature: Destroy target artifact or enchantment.

### self_mill

- **Vastlands Scavenger // Bind to Life** (blocked): Mill seven cards. Then put a creature card from among them onto the battlefield.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Brigid, Clachan's Heart // Brigid, Doun's Mind | 4 | 0 | 4 | 4 | partial | 6 | 0 | blocked |  |
| Elite Interceptor // Rejoinder | 2 | 0 | 2 | 0 | partial | 5 | 0 | blocked |  |
| Lita, Little Orphan Amphibian | 4 | 0 | 4 | 1 | partial | 4 | 0 | blocked |  |
| Requisition Raid | 3 | 0 | 3 | 4 | partial | 4 | 0 | blocked |  |
| Spiritcall Enthusiast // Scrollboost | 1 | 0 | 1 | 1 | partial | 4 | 0 | blocked |  |
| Studious First-Year // Rampant Growth | 1 | 0 | 1 | 0 | partial | 4 | 0 | blocked | land_search |
| Vastlands Scavenger // Bind to Life | 1 | 0 | 1 | 0 | partial | 4 | 0 | blocked | self_mill |
| Vigorbloom Charm | 4 | 0 | 4 | 3 | partial | 4 | 0 | blocked |  |
| Guardian Sunmare | 1 | 0 | 1 | 1 | partial | 3 | 0 | blocked | land_search |
| Aang's Iceberg | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Astelli Reclaimer | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | repeatable_recursion |
| Bounding Felidar | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Bramblewood Paragon | 2 | 0 | 2 | 0 | partial | 2 | 0 | blocked |  |
| Peerless Recycling | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Queen Allenal of Ruadach | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Starfield Shepherd | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Strength of the Coalition | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Biosynthic Burst | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Blossoming Bogbeast | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Coeurl | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Dundoolin Weaver | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Focus Fire | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Golden Argosy | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Heirloom Epic | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Helping Hand | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Little Bear | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Owlin Historian | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked |  |
| Rosa, Resolute White Mage | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Salvation Swan | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Serra Paragon | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked | repeatable_recursion |
| Sunpearl Kirin | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Traveling Botanist | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Trudge Garden | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Whitemane Lion | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Stampeding Scurryfoot | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Case of the Uneaten Feast | 2 | 1 | 1 | 1 | partial | 2 | 0 | eligible after review | repeatable_recursion |
| Drix Fatemaker | 2 | 1 | 1 | 1 | partial | 2 | 0 | eligible after review |  |
| Haliya, Guided by Light | 2 | 1 | 1 | 2 | partial | 2 | 0 | eligible after review |  |
| Rayblade Trooper | 2 | 2 | 0 | 1 | partial | 2 | 0 | eligible after review |  |
| Cloudbound Moogle | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Guac & Marshmallow Pizza | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Ohran Frostfang | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Qasali Pridemage | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| To Arms! | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Veteran Beastrider | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Carrot Cake | 2 | 1 | 1 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Dawnstrike Vanguard | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Elvish Visionary | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Mighty Mutanimals | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Sundering Growth | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Teleportation Circle | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion |
| Undergrowth Leopard | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Hunter's Talent | 5 | 1 | 4 | 2 | partial | 5 | 0 | reviewable, no executable action |  |
| Nyxborn Hydra | 1 | 1 | 0 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Boromir, Warden of the Tower | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action | sacrifice_conversion |
| Emil, Vastlands Roamer | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Prehistoric Pet | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Quintessential Katana | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| The Wandering Rescuer | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Adept Watershaper | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Lightning Greaves | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Pawpatch Recruit | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Stirring Hopesinger | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Suki, Courageous Rescuer | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Umbral Mantle | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
