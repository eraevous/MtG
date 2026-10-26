# Semantic readiness audit: Sharuum (v0.2)

Nonland cards: **63**. Candidate operations: **92**. Contracts ready for review: **48**; blocked: **44**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 43, machine_parsed 20. Unread clauses across the deck: **64**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| eligible after review | 32 |
| blocked | 22 |
| reviewable, no executable action | 8 |
| no candidate operations | 1 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 0 | 0 | 0 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 9 | 9 | 3 | 6 | 0 | 0.3.0 action missing text or disagrees (5); trigger has no hook / hook outside registry (1); cost missing or unparsed (1) |
| land_search | 2 | 2 | 0 | 2 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 12 | 13 | 10 | 3 | 0 | 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| self_mill | 1 | 1 | 1 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### repeatable_recursion

- **Astelli Reclaimer** (blocked): When this creature enters, return target noncreature, nonland permanent card with mana value X or less from your graveyard to the battlefield, where X is the amount of ma
- **Conjurer's Bauble** (blocked): {T}, Sacrifice this artifact: Put up to one target card from your graveyard on the bottom of your library. Draw a card.
- **Does Machines** (blocked): When this Class becomes level 2, return up to two target artifact cards from your graveyard to your hand.
- **Don & Leo, Problem Solvers** (blocked): At the beginning of your end step, exile up to one target artifact you control and up to one target creature you control. Then return them to the battlefield under their 
- **Junk Diver** (blocked): When this creature dies, return another target artifact card from your graveyard to your hand.
- **Rescue Skiff** (ready_for_review): When this Spacecraft enters, return target creature or enchantment card from your graveyard to the battlefield.
- **Sanctum Gargoyle** (ready_for_review): When this creature enters, you may return target artifact card from your graveyard to your hand.
- **Sharuum the Hegemon** (ready_for_review): When Sharuum enters, you may return target artifact card from your graveyard to the battlefield.
- **Zoraline, Cosmos Caller** (blocked): Whenever Zoraline enters or attacks, you may pay {W}{B} and 2 life. When you do, return target nonland permanent card with mana value 3 or less from your graveyard to the

### land_search

- **Divert Disaster** (blocked): Counter target spell unless its controller pays {2}. If they do, you create a Lander token. (It's an artifact with "{2}, {T}, Sacrifice this token: Search your library fo
- **Solemn Simulacrum** (blocked): When this creature enters, you may search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.

### sacrifice_conversion

- **Anchovy & Banana Pizza** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Chromatic Star** (ready_for_review): {1}, {T}, Sacrifice this artifact: Add one mana of any color.
- **Conjurer's Bauble** (blocked): {T}, Sacrifice this artifact: Put up to one target card from your graveyard on the bottom of your library. Draw a card.
- **Cryogen Relic** (blocked): {1}{U}, Sacrifice this artifact: Put a stun counter on up to one target tapped creature. (If a permanent with a stun counter would become untapped, remove one from it ins
- **Etherium Astrolabe** (ready_for_review): {B}, {T}, Sacrifice an artifact: Draw a card.
- **Executioner's Capsule** (ready_for_review): {1}{B}, {T}, Sacrifice this artifact: Destroy target nonblack creature.
- **Grim Bauble** (ready_for_review): {2}{B}, {T}, Sacrifice this artifact: Surveil 2. (Look at the top two cards of your library, then put any number of them into your graveyard and the rest on top of your l
- **Nutrient Block** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Omni-Cheese Pizza** (ready_for_review): {1}, {T}, Sacrifice this artifact: Add one mana of any color.
- **Omni-Cheese Pizza** (ready_for_review): {2}, {T}, Sacrifice this artifact: You gain 3 life.
- **Repurposing Bay** (blocked): {2}, {T}, Sacrifice another artifact: Search your library for an artifact card with mana value equal to 1 plus the sacrificed artifact's mana value, put that card onto th
- **Sewer-veillance Cam** (ready_for_review): {3}{U}, Sacrifice this artifact: Draw two cards.
- **Thopter Foundry** (ready_for_review): {1}, Sacrifice a nontoken artifact: Create a 1/1 blue Thopter artifact creature token with flying. You gain 1 life.

### self_mill

- **Does Machines** (ready_for_review): When this Class enters, mill two cards, draw two cards, then discard two cards.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Skycoach Conductor // All Aboard | 1 | 0 | 1 | 0 | partial | 4 | 0 | blocked |  |
| Krang, Master Mind | 1 | 0 | 1 | 1 | partial | 3 | 0 | blocked |  |
| Astelli Reclaimer | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | repeatable_recursion |
| Hymn of the Faller | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Refurbished Familiar | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Scour for Scrap | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Conjurer's Bauble | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion, sacrifice_conversion |
| Divert Disaster | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Don & Leo, Problem Solvers | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Esperzoa | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Fix What's Broken | 1 | 0 | 1 | 2 | partial | 1 | 0 | blocked |  |
| Guidelight Pathmaker | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Junk Diver | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Magister Sphinx | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Path to Exile | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Repurposing Bay | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | sacrifice_conversion |
| Selfcraft Mechan | 2 | 0 | 2 | 1 | partial | 1 | 0 | blocked |  |
| Shatter the Sky | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Susurian Dirgecraft | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Twinning Glass | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Unbender Tine | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Mirkwood Bats | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Nesting Bot | 1 | 1 | 0 | 1 | partial | 2 | 0 | eligible after review |  |
| Bender's Waterskin | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Bespoke Bō | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Blitzball | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Chromatic Lantern | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Chromatic Star | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Coin of Mastery | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Firdoch Core | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Gold Pan | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Grim Bauble | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Nutrient Block | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Puppet Conjurer | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Solemn Simulacrum | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | land_search |
| Vanquish the Horde | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Anchovy & Banana Pizza | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Azorius Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Buzz Bots | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Cryogen Relic | 2 | 1 | 1 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Disruptor of Currents | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Etherium Astrolabe | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Executioner's Capsule | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Hulldrifter | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Mechan Assembler | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Omni-Cheese Pizza | 3 | 3 | 0 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Orzhov Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Pactdoll Terror | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Prismatic Lens | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Rescue Skiff | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion |
| Sanctum Gargoyle | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion |
| Sewer-veillance Cam | 2 | 2 | 0 | 3 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Sharuum the Hegemon | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | repeatable_recursion |
| Thopter Foundry | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Etherium Sculptor | 0 | 0 | 0 | 0 | machine_parsed | 0 | 0 | no candidate operations |  |
| Does Machines | 5 | 1 | 4 | 1 | partial | 5 | 0 | reviewable, no executable action | repeatable_recursion, self_mill |
| Coldsteel Heart | 2 | 1 | 1 | 1 | partial | 3 | 0 | reviewable, no executable action |  |
| Cavern Harpy | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Gandalf the White | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Illvoi Light Jammer | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Susurian Voidborn | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Zoraline, Cosmos Caller | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action | repeatable_recursion |
| Al Bhed Salvagers | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
