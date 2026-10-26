# Deck: Token Triumph

- Emmara, Soul of the Accord (WG), 100 cards
- Lands 39, nonland 60 (creatures 26), average nonland mana value 3.58
- Mana (goldfish, on the draw): 4 by T4 86.5%, all colors by T5 96.9%, commander out by T4 89.5% / T6 97.5%
- Weakest areas (seen by T7 vs target): protection 26.4% (2 cards), recursion 14.1% (1 cards), spot_removal 61.0% (6 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 4; unopposed goldfish lethal by T10 90.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 6 before, 8 three turns later
- Without the commander: damage by T10 -0.8 (paired); typed coverage 23 of 61 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 8 | 0 to 10 | 2 of 13 |
| tap claimants per creature card | 0.3 | 0.0 to 0.62 | 2 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 0 | 0 to 5 | 8 of 13 |
| creature cards | 27 | 16 to 44 | 5 of 13 |
| creatures with power 4+ | 4 | 2 to 12 | 2 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Conclave Tribunal | tap creatures | 1 | per use |
| Devouring Light | tap creatures | 1 | per use |
| Hour of Reckoning | tap creatures | 1 | per use |
| Jaspera Sentinel | tap creatures | 1 | per use |
| March of the Multitudes | tap creatures | 1 | per use |
| Nissa's Expedition | tap creatures | 1 | per use |
| Scatter the Seeds | tap creatures | 1 | per use |
| Selesnya Evangel | tap creatures | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Emmara, Soul of the Accord | no | creature | - | 19 | Dauntless Escort, Rootborn Defenses |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 4 |
| 2 | 12 |
| 3 | 18 |
| 4 | 9 |
| 5 | 9 |
| 6 | 5 |
| 7+ | 3 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 13 | 10 | Strong |
| fixing | 17 | 6 | Excessive |
| draw | 11 | 10 | Strong |
| spot_removal | 6 | 8 | Adequate |
| wipe | 2 | 2 | Strong |
| counterspell | 0 | None | not scored |
| protection | 2 | 5 | Fragile |
| recursion | 1 | 3 | Fragile |
| closer | 10 | 4 | Excessive |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 13 | 77.3% | 83.5% | 88.1% | 92.8% | 88.1% |
| draw | 11 | 71.0% | 77.8% | 83.1% | 88.9% | 83.1% |
| spot_removal | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 71.9% |
| wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 46.2% |
| recursion | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| closer | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 88.1% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:all_creatures | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| fixing | 8 | 58.8% | 65.9% | 71.9% | 79.2% | 94.2% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 2 | 5 | 26.4% | 54.1% | 27.7 |
| recursion | 1 | 3 | 14.1% | 37.0% | 22.9 |
| spot_removal | 6 | 8 | 61.0% | 71.9% | 10.9 |
| wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| protection:anti_wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| draw | 11 | 10 | 83.1% | 79.9% | -3.2 |
| ramp | 13 | 10 | 88.1% | 79.9% | -8.1 |
| closer | 10 | 4 | 79.9% | 46.2% | -33.7 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Citywide Bust | destroy | big_toughness, ordinary |
| Hour of Reckoning | destroy | big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Dauntless Escort | indestructible | all_creatures | damage, destroy |
| Rootborn Defenses | indestructible | all_creatures | damage, destroy |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Eternal Witness | hand | any card | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 20/0/0 | yes |
| counters | 14.1% | package | 6/1 | yes |
| lifegain | 14.1% | package | 8/1 | yes |
| blink | 0.0% | fragment | 0/11 |  |
| landfall | 13.1% | redundant | 3/3 | yes |
| spellslinger | 0.0% | fragment | 16/0 |  |
| graveyard | 0.0% | fragment | 0/1 |  |
| go_wide | 79.9% | redundant | 20/10 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Ajani, Caller of the Pride | X-scaled magnitude; unparsed text | closer |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Aura Mutation | X-scaled magnitude |  |
| Avacyn's Pilgrim | activated ability (repeatable, not priced) |  |
| Camaraderie | X-scaled magnitude |  |
| Champion of Lambholt | repeatable trigger (cadence not priced); unparsed text | closer |
| Citanul Hierophants | activated ability (repeatable, not priced) |  |
| Citywide Bust |  | spot_removal |
| Commander's Sphere | activated ability (repeatable, not priced) |  |
| Conclave Tribunal | unparsed text |  |
| Curse of Bounty | repeatable trigger (cadence not priced); unparsed text |  |
| Dauntless Escort |  | sac_outlet |
| Dawn of Hope | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Devouring Light | unparsed text |  |
| Dictate of Heliod |  | protection |
| Emmara, Soul of the Accord | repeatable trigger (cadence not priced) |  |
| Felidar Retreat | repeatable trigger (cadence not priced); unparsed text |  |
| Great Oak Guardian | unparsed text |  |
| Harvest Season | X-scaled magnitude |  |
| Hornet Nest | repeatable trigger (cadence not priced) | protection |
| Hornet Queen |  | closer |
| Hour of Reckoning | unparsed text |  |
| Idol of Oblivion | activated ability (repeatable, not priced); unparsed text |  |
| Jade Mage | activated ability (repeatable, not priced) |  |
| Jaspera Sentinel | activated ability (repeatable, not priced) |  |
| Karametra's Favor | activated ability (repeatable, not priced); unparsed text |  |
| Leafkin Druid | activated ability (repeatable, not priced); replacement or prevention effect |  |
| Loyal Guardian | repeatable trigger (cadence not priced) |  |
| Maja, Bretagard Protector | repeatable trigger (cadence not priced) |  |
| March of the Multitudes | X-scaled magnitude; unparsed text |  |
| Mentor of the Meek | repeatable trigger (cadence not priced) |  |
| Nissa's Expedition | unparsed text |  |
| Overwhelming Instinct | repeatable trigger (cadence not priced) |  |
| Path to Exile | unparsed text |  |
| Presence of Gond | activated ability (repeatable, not priced); unparsed text |  |
| Rishkar, Peema Renegade | activated ability (repeatable, not priced) |  |
| Rootborn Defenses | unparsed text | copy, token_maker |
| Scatter the Seeds | unparsed text |  |
| Scavenging Ooze | activated ability (repeatable, not priced) |  |
| Selesnya Evangel | activated ability (repeatable, not priced) |  |
| Selesnya Guildmage | activated ability (repeatable, not priced) |  |
| Slate of Ancestry | activated ability (repeatable, not priced) |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Sporemound | repeatable trigger (cadence not priced) |  |
| Sylvan Reclamation | unparsed text | spot_removal |
| Talisman of Unity | activated ability (repeatable, not priced); unparsed text |  |
| Trostani Discordant | repeatable trigger (cadence not priced) |  |
| Valor in Akros | repeatable trigger (cadence not priced) |  |
| Verdant Force | repeatable trigger (cadence not priced) |  |
| White Sun's Zenith | X-scaled magnitude; unparsed text |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: creature token enters; independent sources: 9; cards: Dawn of Hope, Hornet Queen, Idol of Oblivion, Jade Mage, Maja, Bretagard Protector, Selesnya Evangel, Selesnya Guildmage, Sporemound, Trostani Discordant |
| linear payoff | Champion of Lambholt: enter -> power (fed by 32 cards) |
| linear payoff | Conclave Tribunal: enter -> interaction (fed by 1 cards) |
| linear payoff | Dawn of Hope: lifegain -> cards (fed by 0 cards) |
| linear payoff | Mentor of the Meek: enter -> cards (fed by 0 cards) |
| linear payoff | Overwhelming Instinct: attack -> cards (fed by combat) |
| linear payoff | Reclamation Sage: enter -> interaction (fed by 1 cards) |
| linear payoff | Rishkar, Peema Renegade: enter -> power (fed by 1 cards) |
| linear payoff | Valor in Akros: enter -> power (fed by 33 cards) |
| linear payoff | Voice of Many: enter -> cards (fed by 1 cards) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.76 | 1.43 | 1.87 | 2.68 | 3.07 | 3.98 |
| can attack | 0.76 | 1.43 | 1.85 | 2.63 | 2.98 | 3.86 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.18 | 0.79 | 0.61 | 1.66 | 1.45 | 2.37 |
| could attack but spent before combat | 0 | 0 | 0.02 | 0.01 | 0.02 | 0.02 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0.01 | 0.0 | 0.01 | 0.01 | 0.01 | 0.01 |
| tapped for other costs | 0 | 0 | 0.01 | 0.01 | 0.04 | 0.04 |
| untapped at end | 1.17 | 1.16 | 1.94 | 1.65 | 2.52 | 2.56 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.78 | 3.47 | 3.14 | 2.7 | 2.3 | 1.85 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 94% | 0% | 55% | 88% | spells waiting for mana |
| T4 | 0% | 91% | 0% | 57% | 78% | spells waiting for mana |
| T5 | 0% | 86% | 2% | 86% | 93% | spells waiting for mana |
| T6 | 0% | 82% | 1% | 60% | 83% | spells waiting for mana |
| T7 | 0% | 70% | 2% | 84% | 96% | spells waiting for mana |
| T8 | 0% | 62% | 2% | 71% | 94% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 4 | 0.0 | 12.7 | +0.0 (SE 0.0) |
| station_first | 4 | 0.0 | 12.7 | +0.0 (SE 0.0) |
| mana_first | 4 | 0.0 | 12.7 | +0.5 (SE 0.3) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 42.7% / 90.0% |
| light blockers: lethal by T10 | 1.7% |
| light blockers: median damage by T8 / T10 | 2 / 4 |
| tokens per turn T4-T8 (mean) | 0.34 |
| cards drawn by T8 (mean, incl. normal draws) | 9.7 |
| board at end of T8 (median bodies / power) | 4 / 11 |
| power per body at end of T8 (median) | 2.50 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 6 -> 8 | -3.2 (SE 0.4) |
| exile wipe after T6 | 6 -> 8 | -3.2 (SE 0.4) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 3.24 | -2.8 (SE 0.3) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 6 -> 4; commander casts T7-T10 2.57 | -4.3 (SE 0.4) |
| no commander (ablation) | tokens per turn T4-T8: 0.34 -> 0.41 | -0.8 (SE 0.3) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Ajani, Caller of the Pride | +1: put a +1/+1 counter on up to one target creature.; −3: target creature gains flying and double strike until end of turn.; −8: create x 2/2 white cat creatur |
| Aura Mutation | where x is that enchantment's mana value |
| Camaraderie | you gain x life and where x is the number of creatures you control |
| Champion of Lambholt | creatures with power less than this creature's power can't block creatures you control. |
| Citanul Hierophants | creatures you control have "{t}: add {g}." |
| Collective Unconscious | for each creature you control |
| Commander's Insignia | creatures you control get +1/+1 for each time you've cast your commander from the command zone this game. |
| Curse of Bounty | enchant player; whenever enchanted player is attacked, untap all nonland permanents you control. each opponent attacking that player untaps all nonland permanen |
| Dauntless Escort | creatures you control gain indestructible until end of turn |
| Dawn of Hope | pay {2} if you do |
| Emmara, Soul of the Accord | whenever ~ becomes tapped, create a 1/1 white soldier creature token with lifelink. |
| Eternal Witness | return target card from your graveyard to your hand |
| Farhaven Elf | search your library for a basic land card put it onto the battlefield tapped then shuffle |
| Felidar Retreat | choose one; • create a 2/2 white cat beast creature token.; • put a +1/+1 counter on each creature you control. those creatures gain vigilance until end of turn |
| Great Oak Guardian | creatures target player controls get +2/+2 until end of turn untap them |
| Harvest Season | search your library for up to x basic land cards where x is the number of tapped creatures you control put those cards onto the battlefield tapped then shuffle |
| Hornet Nest | whenever this creature is dealt damage, create that many 1/1 green insect creature tokens with flying and deathtouch. |
| Hornet Queen | deathtouch |
| Hour of Reckoning | destroy all nontoken creatures |
| Idol of Oblivion | activate only if you created a token this turn |
| Karametra's Favor | enchant creature; when this aura enters, draw a card.; enchanted creature has "{t}: add one mana of any color." |
| Leafkin Druid | if you control four or more creatures instead |
| Loyal Guardian | lieutenant — at the beginning of combat on your turn, if you control your commander, put a +1/+1 counter on each creature you control. |
| Mentor of the Meek | pay {1} if you do |
| Nissa's Expedition | search your library for up to two basic land cards put them onto the battlefield tapped then shuffle |
| Path to Exile | its controller may search their library for a basic land card put that card onto the battlefield tapped then shuffle |
| Presence of Gond | enchant creature; enchanted creature has "{t}: create a 1/1 green elf warrior creature token." |
| Rishkar, Peema Renegade | each creature you control with a counter on it has "{t}: add {g}." |
| Rootborn Defenses | populate creatures you control gain indestructible until end of turn |
| Scavenging Ooze | if it was a creature card |
| Slate of Ancestry | for each creature you control |
| Sylvan Reclamation | exile up to two target artifacts and/or enchantments; basic landcycling {2} |
| Talisman of Unity | deals 1 damage to you |
| Thunderfoot Baloth | lieutenant — as long as you control your commander, this creature gets +2/+2 and other creatures you control get +2/+2 and have trample. |
| Trostani Discordant | each player gains control of all creatures they own |
| Verdant Force | at the beginning of each upkeep, create a 1/1 green saproling creature token. |
| Voice of Many | for each opponent who controls fewer creatures than you |
| White Sun's Zenith | shuffle ~ into its owner's library |

## Uncertainty

- 50 of 61 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 23 of 61 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
