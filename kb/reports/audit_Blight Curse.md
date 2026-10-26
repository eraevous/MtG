# Semantic readiness audit: Blight Curse (v0.2)

Nonland cards: **61**. Candidate operations: **95**. Contracts ready for review: **25**; blocked: **70**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 55, machine_parsed 6. Unread clauses across the deck: **87**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 40 |
| eligible after review | 13 |
| reviewable, no executable action | 8 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 1 | 1 | 1 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 3 | 3 | 1 | 2 | 0 | 0.3.0 action missing text or disagrees (2) |
| land_search | 0 | 0 | 0 | 0 | 0 |  |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 2 | 2 | 1 | 1 | 0 | 0.3.0 action missing text or disagrees (1) |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### landfall

- **Evolution Sage** (ready_for_review): Landfall — Whenever a land you control enters, proliferate.

### repeatable_recursion

- **Grave Venerations** (blocked): At the beginning of your end step, if you're the monarch, return up to one target creature card from your graveyard to your hand.
- **Necroskitter** (ready_for_review): Whenever a creature an opponent controls with a -1/-1 counter on it dies, you may return that card to the battlefield under your control.
- **Puca's Covenant** (blocked): Whenever a creature you control with a counter on it dies, you may return another target permanent card with mana value less than or equal to the number of counters on th

### sacrifice_conversion

- **Commander's Sphere** (ready_for_review): Sacrifice this artifact: Draw a card.
- **Wickersmith's Tools** (blocked): {5}, {T}, Sacrifice this artifact: Create X tapped 2/2 colorless Scarecrow artifact creature tokens, where X is the number of charge counters on this artifact.

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Glissa Sunslayer | 4 | 0 | 4 | 1 | partial | 4 | 0 | blocked |  |
| Binding the Old Gods | 2 | 0 | 2 | 0 | partial | 3 | 0 | blocked |  |
| Liliana, Death Wielder | 3 | 0 | 3 | 0 | partial | 3 | 0 | blocked |  |
| Auntie Ool, Cursewretch | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Carnifex Demon | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Cathartic Pyre | 3 | 0 | 3 | 2 | partial | 2 | 0 | blocked |  |
| Dread Tiller | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Dusk Urchins | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Ferrafor, Young Yew | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Grim Poppet | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Hapatra, Vizier of Poisons | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Ignoble Hierarch | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Oft-Nabbed Goat | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Puppeteer Clique | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| The Reaper, King No More | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Village Pillagers | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Aberrant Return | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Assassin's Trophy | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Black Sun's Zenith | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Blowfly Infestation | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Chain Reaction | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Eventide's Shadow | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Fire Covenant | 1 | 0 | 1 | 2 | partial | 1 | 0 | blocked |  |
| Flourishing Defenses | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Grave Titan | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Hoarder's Greed | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Incremental Blight | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Infernal Grasp | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Lasting Tarfire | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Midnight Banshee | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Night's Whisper | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Painful Truths | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Persist | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Puca's Covenant | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | repeatable_recursion |
| Putrefy | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Sinister Gnarlbark | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Skinrender | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Soul Snuffers | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Terminate | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Tree of Perdition | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Grave Venerations | 3 | 1 | 2 | 3 | partial | 2 | 0 | eligible after review | repeatable_recursion |
| Wickersmith's Tools | 3 | 1 | 2 | 2 | partial | 2 | 0 | eligible after review | sacrifice_conversion |
| Burning Curiosity | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Channeler Initiate | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Contagion Clasp | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Devoted Druid | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Wickerbough Elder | 1 | 1 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Cathartic Reunion | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review |  |
| Commander's Sphere | 2 | 2 | 0 | 2 | machine_parsed | 0 | 0 | eligible after review | sacrifice_conversion |
| Evolution Sage | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review | landfall |
| Harmonize | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Vraska, Betrayal's Sting | 3 | 1 | 2 | 0 | partial | 4 | 0 | reviewable, no executable action |  |
| Everlasting Torment | 3 | 2 | 1 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| The Scorpion God | 3 | 1 | 2 | 2 | partial | 3 | 0 | reviewable, no executable action |  |
| Archfiend of Ifnir | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Chimil, the Inner Sun | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Massacre Girl, Known Killer | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Kulrath Knight | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Necroskitter | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action | repeatable_recursion |
