# Semantic readiness audit: TMNT (v0.2)

Nonland cards: **62**. Candidate operations: **100**. Contracts ready for review: **35**; blocked: **65**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 50, machine_parsed 12. Unread clauses across the deck: **93**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 33 |
| eligible after review | 21 |
| reviewable, no executable action | 8 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 0 | 0 | 0 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (2); cost missing or unparsed (1) |
| land_search | 1 | 1 | 1 | 0 | 0 |  |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 7 | 7 | 5 | 2 | 0 | 0.3.0 action missing text or disagrees (2); no effect recorded (1) |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### repeatable_recursion

- **Reaping Willow** (blocked): {1}{W/B}, Remove two counters from this creature: Return target creature card with mana value 3 or less from your graveyard to the battlefield. Activate only as a sorcery
- **Zoraline, Cosmos Caller** (blocked): Whenever Zoraline enters or attacks, you may pay {W}{B} and 2 life. When you do, return target nonland permanent card with mana value 3 or less from your graveyard to the

### land_search

- **Heaped Harvest** (ready_for_review): When this artifact enters and when you sacrifice it, you may search your library for a basic land card, put it onto the battlefield tapped, then shuffle.

### sacrifice_conversion

- **Dimension X Pizzasaur** (ready_for_review): {2}, {T}, Sacrifice this creature: You gain 3 life and each opponent loses 3 life.
- **Gilded Goose** (ready_for_review): {T}, Sacrifice a Food: Add one mana of any color.
- **Gyome, Master Chef** (blocked): {1}, Sacrifice a Food: Target creature gains indestructible until end of turn. Tap it.
- **Heaped Harvest** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Peregrin Took** (ready_for_review): Sacrifice three Foods: Draw a card.
- **Ragost, Deft Gastronaut** (ready_for_review): {1}, {T}, Sacrifice a Food: Ragost deals 3 damage to each opponent.
- **Tempestra, Dame of Games** (blocked): {2}{R}, {T}, Sacrifice an artifact: Create a token that's a copy of another target creature you control, except it isn't legendary. It gains haste. Sacrifice it at the be

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | 4 | 0 | 4 | 2 | partial | 6 | 0 | blocked |  |
| Lita, Little Orphan Amphibian | 4 | 0 | 4 | 1 | partial | 4 | 0 | blocked |  |
| Sink into Stupor // Soporific Springs | 3 | 0 | 3 | 5 | partial | 4 | 0 | blocked |  |
| Berta, Wise Extrapolator | 2 | 0 | 2 | 1 | partial | 3 | 0 | blocked |  |
| Big Mother Mouser | 2 | 0 | 2 | 2 | partial | 3 | 0 | blocked |  |
| Leonardo, the Balance | 2 | 0 | 2 | 2 | partial | 3 | 0 | blocked |  |
| Return of the Wildspeaker | 3 | 0 | 3 | 2 | partial | 3 | 0 | blocked |  |
| Ambitious Augmenter | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| April O'Neil, Live on the Scene | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Bebop, Skull & Crossbones | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Donatello, the Brains | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Endurance | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Glen Elendra Guardian | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Gyome, Master Chef | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked | sacrifice_conversion |
| High Score | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Murderous Redcap | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Reaping Willow | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | repeatable_recursion |
| Selvala, Heart of the Wilds | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Shredder's Technique | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Tam, Mindful First-Year | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| The Last Ronin's Technique | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Assassin's Trophy | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Biosynthic Burst | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Corpsejack Menace | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Heroes in a Half Shell | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Mona Lisa, Science Geek | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Noggle Robber | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Scout for Survivors | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Tainted Treats | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Tempestra, Dame of Games | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | sacrifice_conversion |
| Terrasymbiosis | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Wave Goodbye | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Mirkwood Bats | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Haliya, Guided by Light | 2 | 1 | 1 | 2 | partial | 2 | 0 | eligible after review |  |
| Ragost, Deft Gastronaut | 3 | 1 | 2 | 2 | partial | 2 | 0 | eligible after review | sacrifice_conversion |
| Baxter, Fly in the Ointment | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Casey Jones, Back Alley Brute | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Devoted Druid | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Dimension X Pizzasaur | 3 | 1 | 2 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Heaped Harvest | 2 | 2 | 0 | 3 | partial | 1 | 0 | eligible after review | land_search, sacrifice_conversion |
| Michelangelo, Weirdness to 11 | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Ray Fillet, Wave Warrior | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Rocksteady, Mutant Marauder | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Crustacean Commando | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Flock Impostor | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Genghis Frog | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Gilded Goose | 3 | 3 | 0 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Improvised Club | 2 | 1 | 1 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Mighty Mutanimals | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Mutant Chain Reaction | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Peregrin Took | 2 | 1 | 1 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Personify | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Shimmerwilds Growth | 2 | 1 | 1 | 0 | partial | 4 | 0 | reviewable, no executable action |  |
| Abundant Growth | 2 | 2 | 0 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Ninja Pizza | 2 | 1 | 1 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Splinter, the Mentor | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Zoraline, Cosmos Caller | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action | repeatable_recursion |
| Irma, Part-Time Mutant | 1 | 1 | 0 | 1 | partial | 1 | 0 | reviewable, no executable action |  |
| Rosie Cotton of South Lane | 2 | 1 | 1 | 1 | partial | 1 | 0 | reviewable, no executable action |  |
| Tokka & Rahzar, Unsupervised | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
