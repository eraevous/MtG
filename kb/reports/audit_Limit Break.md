# Semantic readiness audit: Limit Break (v0.2)

Nonland cards: **63**. Candidate operations: **93**. Contracts ready for review: **43**; blocked: **50**. Verified reviews: **0**. Compiled runtime actions: **0**.

0.3.0 projection status: partial 59, machine_parsed 4. Unread clauses across the deck: **95**.

## Runtime compiler eligibility

| Eligibility | Cards |
|---|---:|
| blocked | 28 |
| reviewable, no executable action | 21 |
| eligible after review | 11 |
| no candidate operations | 3 |

## Focus themes

| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |
|---|---:|---:|---:|---:|---:|---|
| landfall | 0 | 0 | 0 | 0 | 0 |  |
| dredge | 0 | 0 | 0 | 0 | 0 |  |
| repeatable_recursion | 5 | 5 | 2 | 3 | 0 | source row needs manual annotation (2); 0.3.0 action missing text or disagrees (2); unbound branch/condition/scaling/modes (1) |
| land_search | 3 | 3 | 1 | 2 | 0 | 0.3.0 action missing text or disagrees (2) |
| land_tokens_scaling | 0 | 0 | 0 | 0 | 0 |  |
| sacrifice_conversion | 3 | 3 | 0 | 3 | 0 | 0.3.0 action missing text or disagrees (3); source row needs manual annotation (1); cost missing or unparsed (1) |
| self_mill | 0 | 0 | 0 | 0 | 0 |  |
| extra_land_drops | 0 | 0 | 0 | 0 | 0 |  |

### repeatable_recursion

- **Aerith, Last Ancient** (blocked): Raise — At the beginning of your end step, if you gained life this turn, return target creature card from your graveyard to your hand. If you gained 7 or more life this t
- **Cid, Freeflier Pilot** (ready_for_review): {2}, {T}: Return target Equipment or Vehicle card from your graveyard to your hand.
- **Elena, Turk Recruit** (blocked): When Elena enters, return target non-Assassin historic card from your graveyard to your hand. (Artifacts, legendaries, and Sagas are historic.)
- **Red XIII, Proud Warrior** (ready_for_review): Cosmo Memory — When Red XIII enters, return target Aura or Equipment card from your graveyard to your hand.
- **Sephiroth, Fallen Hero** (blocked): The Reunion — {3}, Sacrifice a modified creature: Return this card from your graveyard to the battlefield tapped.

### land_search

- **Cultivate** (blocked): Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle.
- **Rampant Growth** (blocked): Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.
- **Sword of the Animist** (ready_for_review): Whenever equipped creature attacks, you may search your library for a basic land card, put it onto the battlefield tapped, then shuffle.

### sacrifice_conversion

- **Professional Face-Breaker** (blocked): Sacrifice a Treasure: Exile the top card of your library. You may play that card this turn.
- **Sephiroth, Fallen Hero** (blocked): The Reunion — {3}, Sacrifice a modified creature: Return this card from your graveyard to the battlefield tapped.
- **Zack Fair** (blocked): {1}, Sacrifice Zack Fair: Target creature you control gains indestructible until end of turn. Put Zack Fair's counters on that creature and attach an Equipment that was a

## Every nonland card

| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |
|---|---:|---:|---:|---:|---|---:|---:|---|---|
| Cloud's Limit Break | 3 | 0 | 3 | 4 | partial | 4 | 0 | blocked |  |
| SOLDIER Military Program | 3 | 0 | 3 | 1 | partial | 3 | 0 | blocked |  |
| Austere Command | 4 | 0 | 4 | 5 | partial | 2 | 0 | blocked |  |
| Avalanche of Sector 7 | 1 | 0 | 1 | 0 | partial | 2 | 0 | blocked |  |
| Barret, Avalanche Leader | 2 | 0 | 2 | 1 | partial | 2 | 0 | blocked |  |
| Cloud, Ex-SOLDIER | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Dispatch | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Heidegger, Shinra Executive | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Helitrooper | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Hellkite Tyrant | 2 | 0 | 2 | 2 | partial | 2 | 0 | blocked |  |
| Lifestream's Blessing | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Tifa, Martial Artist | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Ultimate Magic: Meteor | 1 | 0 | 1 | 2 | partial | 2 | 0 | blocked |  |
| Yuffie, Materia Hunter | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked |  |
| Zack Fair | 1 | 0 | 1 | 1 | partial | 2 | 0 | blocked | sacrifice_conversion |
| Aerith, Last Ancient | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked | repeatable_recursion |
| Armory Automaton | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Barret Wallace | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Conformer Shuriken | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Cultivate | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Explorer's Scope | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Furious Rise | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Mask of Memory | 1 | 0 | 1 | 0 | partial | 1 | 0 | blocked |  |
| Nature's Lore | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Rampant Growth | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked | land_search |
| Secret Rendezvous | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Unfinished Business | 1 | 0 | 1 | 1 | partial | 1 | 0 | blocked |  |
| Decimate | 1 | 0 | 1 | 1 | machine_parsed | 0 | 0 | blocked |  |
| Bugenhagen, Wise Elder | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review |  |
| Cid, Freeflier Pilot | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review | repeatable_recursion |
| Elena, Turk Recruit | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | repeatable_recursion |
| Professional Face-Breaker | 2 | 1 | 1 | 2 | partial | 1 | 0 | eligible after review | sacrifice_conversion |
| Puresteel Paladin | 2 | 2 | 0 | 1 | partial | 1 | 0 | eligible after review |  |
| Vandalblast | 1 | 1 | 0 | 2 | partial | 1 | 0 | eligible after review |  |
| Vanquish the Horde | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Vincent, Vengeful Atoner | 2 | 1 | 1 | 1 | partial | 1 | 0 | eligible after review |  |
| Arcane Signet | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Harmonize | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Sol Ring | 1 | 1 | 0 | 1 | machine_parsed | 0 | 0 | eligible after review |  |
| Ultimate Magic: Holy | 0 | 0 | 0 | 2 | partial | 2 | 0 | no candidate operations |  |
| Chaos Warp | 0 | 0 | 0 | 1 | partial | 1 | 0 | no candidate operations |  |
| Clever Concealment | 0 | 0 | 0 | 1 | partial | 1 | 0 | no candidate operations |  |
| Bronze Guardian | 1 | 1 | 0 | 0 | partial | 4 | 0 | reviewable, no executable action |  |
| Summon: Kujata | 4 | 2 | 2 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Summoning Materia | 3 | 3 | 0 | 0 | partial | 3 | 0 | reviewable, no executable action |  |
| Champion's Helm | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Conqueror's Flail | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Hero's Blade | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action |  |
| Hero's Heirloom | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Professor Hojo | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Red XIII, Proud Warrior | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action | repeatable_recursion |
| Sephiroth, Fallen Hero | 2 | 1 | 1 | 1 | partial | 2 | 0 | reviewable, no executable action | repeatable_recursion, sacrifice_conversion |
| Skullclamp | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Sword of the Animist | 2 | 2 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action | land_search |
| Wrecking Ball Arm | 1 | 1 | 0 | 0 | partial | 2 | 0 | reviewable, no executable action |  |
| Bastion Protector | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Behemoth Sledge | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Cait Sith, Fortune Teller | 2 | 1 | 1 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Colossus Hammer | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Darksteel Plate | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Inspiring Statuary | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Lightning Greaves | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
| Trailblazer's Boots | 1 | 1 | 0 | 0 | partial | 1 | 0 | reviewable, no executable action |  |
