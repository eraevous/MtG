# Deck: Shanid

- Shanid, Sleepers' Scourge (WBR), 100 cards
- Lands 36, nonland 63 (creatures 38), average nonland mana value 3.05
- Mana (goldfish, on the draw): 4 by T4 68.3%, all colors by T5 78.6%, commander out by T4 44.8% / T6 81.2%
- Weakest areas (seen by T7 vs target): recursion 14.1% (1 cards), protection 37.0% (3 cards), protection:anti_wipe 14.1% (1 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 8; unopposed goldfish lethal by T10 84.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 8 three turns later
- Without the commander: damage by T10 -4.8 (paired); typed coverage 8 of 64 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 1 | 0 to 10 | 6 of 13 |
| tap claimants per creature card | 0.03 | 0.0 to 0.62 | 7 of 13 |
| station power needed | 7 | 0 to 30 | 3 of 13 |
| artifact-sacrifice claimants | 0 | 0 to 5 | 8 of 13 |
| creature cards | 39 | 16 to 44 | 10 of 13 |
| creatures with power 4+ | 10 | 2 to 12 | 12 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| The Seriema | station | 7 | one-time |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Shanid, Sleepers' Scourge | no | - | - | 0 | Cloud, Planet's Champion, The Seriema, Yahenni, Undying Partisan, Éowyn, Fearless Knight |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 6 |
| 2 | 16 |
| 3 | 20 |
| 4 | 13 |
| 5 | 6 |
| 6 | 2 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 9 | 10 | Adequate |
| fixing | 13 | 12 | Strong |
| draw | 9 | 10 | Adequate |
| spot_removal | 10 | 8 | Strong |
| wipe | 4 | 2 | Excessive |
| counterspell | 0 | None | not scored |
| protection | 3 | 5 | Adequate |
| recursion | 1 | 3 | Fragile |
| closer | 12 | 4 | Excessive |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 9 | 63.3% | 70.4% | 76.2% | 83.1% | 76.2% |
| draw | 8 | 58.8% | 65.9% | 71.9% | 79.2% | 71.9% |
| spot_removal | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 88.1% |
| wipe | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 46.2% |
| protection | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 54.1% |
| recursion | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 46.2% |
| closer | 11 | 71.0% | 77.8% | 83.1% | 88.9% | 95.2% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| protection:all_creatures | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| fixing | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 90.0% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| recursion | 1 | 3 | 14.1% | 37.0% | 22.9 |
| protection | 3 | 5 | 37.0% | 54.1% | 17.1 |
| protection:anti_wipe | 1 | 2 | 14.1% | 26.4% | 12.3 |
| draw | 8 | 10 | 71.9% | 79.9% | 8.0 |
| ramp | 9 | 10 | 76.2% | 79.9% | 3.7 |
| spot_removal | 10 | 8 | 79.9% | 71.9% | -8.0 |
| wipe | 4 | 2 | 46.2% | 26.4% | -19.8 |
| closer | 11 | 4 | 83.1% | 46.2% | -36.9 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Ajani Unrelenting | damage | ordinary |
| Glóin the Mighty | asymmetric, damage | ordinary |
| Oros, the Avenger | damage | ordinary |
| Starfall Invocation | destroy | big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Cloud, Planet's Champion | indestructible | self | damage, destroy |
| My Precious // Allure of Power | hexproof | unclear | - |
| The Seriema | indestructible | all_creatures | damage, destroy |
| Yahenni, Undying Partisan | indestructible | self | damage, destroy |
| Éowyn, Fearless Knight | protection from | all_creatures | - |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Starfall Invocation | battlefield | any creature | one-shot |
| Vincent Valentine // Galian Beast | battlefield | any creature | one-shot |
| Zoraline, Cosmos Caller | battlefield | any card of a type | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 13.6% | package | 9/2/4 | yes |
| counters | 10.4% | package | 9/1 | yes |
| artifact_tokens | 9.3% | package | 3/2 | yes |
| lifegain | 37.0% | redundant | 14/3 | yes |
| blink | 0.0% | fragment | 0/16 |  |
| landfall | 1.9% | package | 1/1 | yes |
| spellslinger | 0.0% | fragment | 8/0 |  |
| graveyard | 1.9% | package | 1/1 | yes |
| go_wide | 76.2% | redundant | 9/13 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Adelbert Steiner | unparsed text |  |
| Agent Bishop, Man in Black | repeatable trigger (cadence not priced) |  |
| Airbender's Reversal | unparsed text |  |
| Ajani Resolute | repeatable trigger (cadence not priced) |  |
| Ajani Unrelenting | repeatable trigger (cadence not priced) |  |
| Ambrosia Whiteheart | repeatable trigger (cadence not priced) |  |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Baird, Argivian Recruiter | repeatable trigger (cadence not priced) |  |
| Blitzball | activated ability (repeatable, not priced); unparsed text |  |
| Bre of Clan Stoutarm | activated ability (repeatable, not priced); cost reduction or free cast; repeatable trigger (cadence not priced) |  |
| Chaos Warp | unparsed text |  |
| Cloud, Planet's Champion | cost reduction or free cast; unparsed text | closer, protection |
| Dori, Bearer of Friends |  | fixing, sac_outlet |
| Elas il-Kor, Sadistic Pilgrim | repeatable trigger (cadence not priced) |  |
| Garna, Bloodfist of Keld | repeatable trigger (cadence not priced) | spot_removal |
| Gideon Jura | animation; replacement or prevention effect; unparsed text |  |
| Glóin the Mighty | repeatable trigger (cadence not priced) |  |
| Gogo, Mysterious Mime | animation; copy effect; repeatable trigger (cadence not priced); unparsed text |  |
| Hero's Heirloom | unparsed text |  |
| Leonardo, Cutting Edge | keyworded mechanic: sneak; repeatable trigger (cadence not priced) |  |
| Leonardo, Leader in Blue | activated ability (repeatable, not priced); keyworded mechanic: sneak |  |
| Lightning, Security Sergeant | repeatable trigger (cadence not priced); unparsed text | closer |
| Liliana of the Veil | unparsed text |  |
| Loxodon Warhammer | unparsed text |  |
| Mabel, Valley Hero | repeatable trigger (cadence not priced) |  |
| Mardu Devotee | activated ability (repeatable, not priced); unparsed text | fixing |
| Mirror of Galadriel | activated ability (repeatable, not priced); cost reduction or free cast |  |
| My Precious // Allure of Power | unparsed text | protection |
| Northern Air Temple | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Oroku Saki, Shredder Rising | keyworded mechanic: sneak; repeatable trigger (cadence not priced) | closer, spot_removal |
| Oros, the Avenger | repeatable trigger (cadence not priced) | closer |
| Rakdos Charm | unparsed text | closer |
| Rakdos Signet | activated ability (repeatable, not priced) | fixing |
| Raph & Leo, Sibling Rivals | additional or multiplied effect; repeatable trigger (cadence not priced) |  |
| Raphael, the Muscle | replacement or prevention effect; unparsed text |  |
| Raphael, the Nightwatcher | keyworded mechanic: sneak |  |
| Relic of Legends | activated ability (repeatable, not priced) |  |
| Ring of the Lucii | activated ability (repeatable, not priced) |  |
| Rising of the Day | unparsed text |  |
| Rosie Cotton of South Lane | repeatable trigger (cadence not priced) |  |
| Samwise the Stouthearted | unparsed text | recursion |
| Sauron, the Necromancer | copy effect; repeatable trigger (cadence not priced) | closer |
| Shagrat, Loot Bearer | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Shanid, Sleepers' Scourge | repeatable trigger (cadence not priced) |  |
| Shredder's Technique | keyworded mechanic: sneak; unparsed text |  |
| Shredder, Shadow Master | copy effect; repeatable trigger (cadence not priced); unparsed text |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Southern Air Temple | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Splinter, Hamato Yoshi | keyworded mechanic: sneak; unparsed text |  |
| Starfall Invocation | unparsed text | recursion, spot_removal |
| Sting, the Glinting Dagger | repeatable trigger (cadence not priced); unparsed text |  |
| Swords to Plowshares | unparsed text |  |
| Thalia, the Survivor | unparsed text |  |
| The Infamous Cruelclaw | repeatable trigger (cadence not priced); unparsed text | closer |
| The Seriema | keyworded mechanic: station; unparsed text |  |
| Tori D'Avenant, Fury Rider | repeatable trigger (cadence not priced); unparsed text |  |
| Vincent Valentine // Galian Beast | repeatable trigger (cadence not priced); unparsed text | recursion |
| Wingnut, Bat on the Belfry | keyworded mechanic: alliance; repeatable trigger (cadence not priced) |  |
| Winter, Tormented Loner | unparsed text | sac_outlet |
| Yahenni, Undying Partisan | repeatable trigger (cadence not priced) |  |
| Zoraline, Cosmos Caller | repeatable trigger (cadence not priced) | spot_removal |
| Éomer, Marshal of Rohan | additional or multiplied effect; repeatable trigger (cadence not priced); unparsed text |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 2; cards: Dori, Bearer of Friends, Raphael, the Muscle |
| parallel producers | event: creature token enters; independent sources: 1; cards: Baird, Argivian Recruiter |
| linear payoff | Agent Bishop, Man in Black: begin_combat -> power (fed by each turn) |
| linear payoff | Elas il-Kor, Sadistic Pilgrim: dies -> damage to each opponent (fed by 0 cards) |
| linear payoff | Garna, Bloodfist of Keld: dies -> cards, damage to each opponent (fed by 0 cards) |
| linear payoff | Glóin the Mighty: main_phase -> mana (fed by each turn) |
| linear payoff | Leonardo, Cutting Edge: lifegain -> power (fed by 1 cards) |
| linear payoff | Leonardo, Leader in Blue: enter -> power (fed by 1 cards) |
| linear payoff | Mabel, Valley Hero: enter -> power (fed by 39 cards) |
| linear payoff | Northern Air Temple: enter -> damage to each opponent (fed by 1 cards) |
| linear payoff | Oroku Saki, Shredder Rising: combat_damage -> cards (fed by combat) |
| linear payoff | Rosie Cotton of South Lane: create -> power (fed by 3 cards) |
| linear payoff | Sauron, the Necromancer: attack -> interaction (fed by combat) |
| linear payoff | Southern Air Temple: enter -> power (fed by 1 cards) |
| linear payoff | Tori D'Avenant, Fury Rider: attack -> power (fed by combat) |
| linear payoff | Wingnut, Bat on the Belfry: attack -> power (fed by combat) |
| feed-forward chain | Baird, Argivian Recruiter: end_step -> Elas il-Kor, Sadistic Pilgrim: enter -> Ajani Resolute: lifegain |
| feed-forward chain | Baird, Argivian Recruiter: end_step -> Elas il-Kor, Sadistic Pilgrim: enter -> Leonardo, Cutting Edge: lifegain |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.42 | 0.95 | 1.52 | 2.31 | 2.8 | 3.69 |
| can attack | 0.42 | 0.95 | 1.52 | 2.31 | 2.8 | 3.69 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.01 | 0.03 | 0.13 |
| attacked | 0.2 | 0.66 | 1.02 | 2.1 | 2.3 | 3.24 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0.0 | 0.01 | 0.03 | 0.08 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.81 | 1.03 | 1.41 | 1.2 | 1.46 | 1.44 |
| station charge still needed | 0.02 | 0.02 | 0.01 | 0.08 | 0.24 | 0.35 |
| spells waiting in hand | 3.76 | 3.73 | 3.43 | 2.94 | 2.36 | 1.75 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 86% | 0% | 22% | 66% | spells waiting for mana |
| T4 | 0% | 83% | 0% | 29% | 77% | spells waiting for mana |
| T5 | 0% | 79% | 0% | 46% | 86% | spells waiting for mana |
| T6 | 1% | 71% | 0% | 23% | 83% | spells waiting for mana |
| T7 | 4% | 57% | 0% | 43% | 83% | spells waiting for mana |
| T8 | 7% | 44% | 0% | 40% | 80% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 8 | 0.7 | 10.5 | +0.0 (SE 0.0) |
| station_first | 8 | 0.9 | 10.5 | +0.3 (SE 0.1) |
| mana_first | 8 | 0.7 | 10.5 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 38.3% / 84.0% |
| light blockers: lethal by T10 | 0.3% |
| light blockers: median damage by T8 / T10 | 5 / 8 |
| tokens per turn T4-T8 (mean) | 0.06 |
| cards drawn by T8 (mean, incl. normal draws) | 8.3 |
| board at end of T8 (median bodies / power) | 4 / 12 |
| power per body at end of T8 (median) | 2.67 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 8 | -4.6 (SE 0.3) |
| exile wipe after T6 | 7 -> 8 | -4.8 (SE 0.3) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.24 | -4.9 (SE 0.2) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 5; commander casts T7-T10 1.67 | -5.5 (SE 0.3) |
| no commander (ablation) | tokens per turn T4-T8: 0.06 -> 0.06 | -4.8 (SE 0.2) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Adelbert Steiner | ~ gets +1/+1 for each equipment you control. |
| Airbender's Reversal | choose one —; • airbend target creature you control |
| Ajani Resolute | put a loyalty counter on ajani; 0: you gain 1 life.; −4: create a 2/2 white cat soldier creature token named ajani's pridemate with "whenever you gain life, put |
| Ajani Unrelenting | whenever you activate a loyalty ability, create a 2/2 colorless wizard soldier creature token named cadet.; +1: creatures you control get +1/+0 and gain haste u |
| Ambrosia Whiteheart | return another permanent you control to its owner's hand; ~ gets +1/+0 until end of turn |
| Baird, Argivian Recruiter | if you control a creature with power greater than its base power |
| Blitzball | activate only if an opponent was dealt combat damage by a legendary creature this turn |
| Bre of Clan Stoutarm | another target creature you control gains flying and lifelink until end of turn; if you gained life this turn exile cards from the top of your library until you |
| Chaos Warp | the owner of target permanent shuffles it into their library then reveals the top card of their library if it's a permanent card they put it onto the battlefiel |
| Cloud, Planet's Champion | during your turn, as long as ~ is equipped, it has double strike and indestructible.; equip abilities you activate that target ~ cost {2} less to activate. |
| Garna, Bloodfist of Keld | if it was attacking otherwise ~ |
| Gideon Jura | +2: during target opponent's next turn, creatures that player controls attack ~ if able.; −2: destroy target tapped creature.; 0: until end of turn, ~ becomes a |
| Glóin the Mighty | easy pickings : easy pickings deals 1 damage to each creature your opponents control. |
| Gogo, Mysterious Mime | have ~ become a copy of another target creature you control until end of turn except its name is ~ if you do ~ and that creature each get +2/+0 and gain haste u |
| Hero's Heirloom | equipped creature gets +2/+1.; as long as equipped creature is legendary, it has trample and haste. |
| Leonardo, Cutting Edge | sneak {w} |
| Leonardo, Leader in Blue | sneak {3}{w}{w}; if his sneak cost was paid; ~ gains first strike until end of turn |
| Lightning, Security Sergeant | exile the top card of your library you may play that card for as long as you control ~ |
| Liliana of the Veil | +1: each player discards a card.; −2: target player sacrifices a creature.; −6: separate all permanents target player controls into two piles. that player sacri |
| Loxodon Warhammer | equipped creature gets +3/+0 and has trample and lifelink. |
| Mabel, Bitter Recluse | remove up to three counters from another target creature or planeswalker |
| Mardu Devotee | {w} or {b} activate only once each turn |
| Mirror of Galadriel | this ability costs {1} less to activate for each legendary creature you control |
| My Precious // Allure of Power | ~ {3}; equipped creature has hexproof and can't be blocked.; equip—{2}, pay 2 life.; allure of power {1}{b}; draw two cards. |
| Northern Air Temple | each opponent loses x life and you gain x life where x is the number of shrines you control |
| Oroku Saki, Shredder Rising | sneak {1}{b}; you and lose 1 life |
| Oros, the Avenger | pay {2}{w} if you do ~ deals 3 damage to each nonwhite creature |
| Rakdos Charm | choose one —; • each creature deals 1 damage to its controller |
| Raph & Leo, Sibling Rivals | whenever ~ attack, if it's the first combat phase of the turn, untap one or two target attacking creatures. after this phase, there is an additional combat phas |
| Raphael, the Muscle | double all damage that creatures you control with counters on them would deal.; partner—character select |
| Raphael, the Nightwatcher | sneak {1}{r}{r}; attacking creatures you control have double strike. |
| Ring of the Lucii | tap target nonland permanent |
| Rising of the Day | creatures you control have haste.; legendary creatures you control get +1/+0. |
| Rosie Cotton of South Lane | when rosie cotton enters, create a food token. |
| Samwise the Stouthearted | choose up to one target permanent card in your graveyard that was put there from the battlefield this turn return it to your hand then the ring tempts you |
| Sauron, the Necromancer | create a tapped and attacking token that's a copy of that card except it's a 3/3 black wraith with menace at the beginning of the next end step exile that token |
| Shagrat, Loot Bearer | attach up to one target equipment to it then amass orcs x where x is the number of equipment attached to ~ |
| Shanid, Sleepers' Scourge | other legendary creatures you control have menace.; whenever you play a legendary land or cast a legendary spell, you draw a card and you lose 1 life. |
| Shredder's Technique | sneak {b}; if an enchantment was destroyed this way you lose 2 life |
| Shredder, Shadow Master | a player for each other opponent create a token that's a copy of ~ tapped and attacking that player except it isn't legendary sacrifice those tokens at end of c |

## Uncertainty

- 62 of 64 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 8 of 64 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

## Not modelled

- No opponents: no removal of your pieces, no counterspells, no combat; wipes appear only in named scenarios.
- The goldfish deploys creatures, token makers, ramp and draw; most noncreature engines are not cast.
- Repeatable effects count as one source; their cadence and magnitude are not priced.
- Mana is measured as if all of it can go to the role in question (no competition between spells). Competition for untapped bodies and artifacts is counted in the resource ledger, not simulated.
- Coverage targets are casual-Commander heuristics (ASSUMPTION), not calibrated power.
- Unopposed goldfish: no blockers and no opponent removal except in a named scenario.
- Interaction spells (removal, counters, bounce) are cast with leftover mana as if a target exists; that matters because casting them still triggers "whenever you cast".
- Combat damage all goes to one opponent at 40 life; drain hits each opponent. Reach (damage to any target) is reported, not counted toward lethal.
- Equipment, Class levels, planeswalker loyalty abilities, copy effects and modal choices beyond the first useful mode are not modelled.
- Light blockers (ASSUMPTION): the defending opponent has (turn-1)/2 ground 2/3 blockers and one flier from T7, each blocking one attacker; it is a stress test, not an opponent model.
