# Deck: Vraska

- Vraska, Soul of Stone (WUR), 100 cards
- Lands 36, nonland 63 (creatures 15), average nonland mana value 2.57
- Mana (goldfish, on the draw): 4 by T4 74.1%, all colors by T5 83.2%, commander out by T4 71.6% / T6 88.1%
- Weakest areas (seen by T7 vs target): protection 14.1% (1 cards), recursion 0.0% (0 cards), protection:anti_wipe 0.0% (0 cards)
- Count screen (post-hoc): resource contention; thin board to close with; engine runs through an exposed commander
- Engine (light blockers): median damage by T10 28; unopposed goldfish lethal by T10 93.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 10 before, 9 three turns later
- Without the commander: damage by T10 -60.9 (paired); typed coverage 31 of 64 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

| flag | evidence |
|---|---|
| resource contention | 10 cards spend untapped creatures or artifacts (0.62 per creature card); stations alone need 30 power of taps |
| thin board to close with | 16 creature cards incl. commander, 2 with power 4+; lasting anthems 1; 4 engines need combat damage (Bident of Thassa, Curiosity Crafter, Gossip's Talent, Thopter Spy Network) |
| engine runs through an exposed commander | Vraska, Soul of Stone makes artifact tokens off 48 spells; 1 card can protect it |

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 10 | 0 to 10 | 1 of 13 |
| tap claimants per creature card | 0.62 | 0.0 to 0.62 | 1 of 13 |
| station power needed | 30 | 0 to 30 | 1 of 13 |
| artifact-sacrifice claimants | 3 | 0 to 5 | 2 of 13 |
| creature cards | 16 | 16 to 44 | 1 of 13 |
| creatures with power 4+ | 2 | 2 to 12 | 1 of 13 |
| lasting anthems | 1 | 0 to 1 | 13 of 13 |
| engines needing combat damage | 4 | 0 to 4 | 1 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Boosted Sloop | crew | 1 | per use |
| Flame Fusillade | tap permanents | 1 | per use |
| Improvised Club | sacrifice artifacts | 1 | per use |
| Lumen-Class Frigate | station | 12 | one-time |
| Raff, Weatherlight Stalwart | tap creatures | 2 | per use |
| Retrofitter Foundry | sacrifice artifacts | 1 | per use |
| Sai, Master Thopterist | sacrifice artifacts | 2 | per use |
| Springleaf Drum | tap creatures | 1 | per use |
| Strixhaven Skycoach | crew | 2 | per use |
| Uthros Scanship | station | 8 | one-time |
| Warmaker Gunship | station | 6 | one-time |
| Whirler Rogue | tap artifacts | 2 | per use |
| Wurmwall Sweeper | station | 4 | one-time |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Vraska, Soul of Stone | yes | artifact, creature | 48 | 15 | Shore Up |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 7 |
| 2 | 33 |
| 3 | 12 |
| 4 | 8 |
| 5 | 1 |
| 7+ | 2 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 8 | 10 | Adequate |
| fixing | 17 | 12 | Strong |
| draw | 21 | 10 | Excessive |
| spot_removal | 15 | 8 | Excessive |
| wipe | 1 | 2 | Adequate |
| counterspell | 2 | None | not scored |
| protection | 1 | 5 | Fragile |
| recursion | 0 | 3 | Absent |
| closer | 6 | 4 | Strong |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 7 | 53.7% | 60.8% | 66.8% | 74.5% | 79.9% |
| draw | 21 | 91.9% | 95.3% | 97.3% | 98.9% | 97.3% |
| spot_removal | 15 | 82.3% | 87.8% | 91.6% | 95.4% | 93.0% |
| wipe | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| protection | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 26.4% |
| recursion | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| closer | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 88.1% |
| counterspell | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| fixing | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 93.0% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 1 | 5 | 14.1% | 54.1% | 40.0 |
| recursion | 0 | 3 | 0.0% | 37.0% | 37.0 |
| protection:anti_wipe | 0 | 2 | 0.0% | 26.4% | 26.4 |
| ramp | 7 | 10 | 66.8% | 79.9% | 13.1 |
| wipe | 1 | 2 | 14.1% | 26.4% | 12.3 |
| closer | 6 | 4 | 61.0% | 46.2% | -14.8 |
| draw | 21 | 10 | 97.3% | 79.9% | -17.4 |
| spot_removal | 15 | 8 | 91.6% | 71.9% | -19.8 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Blasphemous Act | damage | ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Shore Up | hexproof | single_target | - |

## Typed recursion

- No recursion read.

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 17/2/0 | yes |
| counters | 0.0% | fragment | 2/0 |  |
| artifact_tokens | 37.0% | redundant | 14/3 | yes |
| lifegain | 0.0% | fragment | 5/0 |  |
| blink | 0.0% | fragment | 0/16 |  |
| landfall | 0.0% | fragment | 1/0 |  |
| spellslinger | 96.7% | redundant | 20/6 | yes |
| graveyard | 0.0% | fragment | 10/0 |  |
| go_wide | 61.0% | redundant | 17/6 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Bespoke Bō | unparsed text |  |
| Bident of Thassa | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Blasphemous Act | cost reduction or free cast |  |
| Boosted Sloop | keyworded mechanic: crew; repeatable trigger (cadence not priced) |  |
| Boros Signet | activated ability (repeatable, not priced) | fixing |
| Carrot Cake | activated ability (repeatable, not priced) | sac_outlet |
| Cori-Steel Cutter | keyworded mechanic: flurry; repeatable trigger (cadence not priced); unparsed text |  |
| Coruscation Mage | keyworded mechanic: offspring; repeatable trigger (cadence not priced) | copy, token_maker |
| Craterclaw Colossus | X-scaled magnitude | token_maker |
| Cryogen Relic | activated ability (repeatable, not priced) |  |
| Curiosity Crafter | repeatable trigger (cadence not priced); unparsed text |  |
| Dreams of Laguna | keyworded mechanic: flashback | recursion |
| Drill Too Deep | unparsed text |  |
| Elsewhere Flask | unparsed text |  |
| Emergency Eject | unparsed text | ramp, token_maker |
| Etherium Sculptor | cost reduction or free cast |  |
| Flame Fusillade | activated ability (repeatable, not priced) | closer |
| Fountainport Bell | activated ability (repeatable, not priced) | ramp |
| Galvanic Blast | keyworded mechanic: metalcraft; replacement or prevention effect | closer |
| Geist of Saint Thalia | cost reduction or free cast | closer |
| Generous Gift | unparsed text | token_maker |
| Gossip's Talent | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) | blink, closer |
| Guidelight Matrix | activated ability (repeatable, not priced); animation; unparsed text |  |
| Improvised Club |  | closer |
| Instant Ramen | activated ability (repeatable, not priced) |  |
| Lumen-Class Frigate | keyworded mechanic: station |  |
| Melded Moxite | activated ability (repeatable, not priced) |  |
| Mouser Attack! | unparsed text |  |
| Mouser Foundry | activated ability (repeatable, not priced) | closer |
| Omni-Cheese Pizza | activated ability (repeatable, not priced) |  |
| Pinnacle Emissary | repeatable trigger (cadence not priced); unparsed text |  |
| Plunder the Trollshaws | keyworded mechanic: flashback; replacement or prevention effect | spot_removal |
| Prismari Charm | unparsed text |  |
| Raff, Weatherlight Stalwart | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Reality Shift | unparsed text |  |
| Reckless Fireweaver | repeatable trigger (cadence not priced) |  |
| Resculpt | unparsed text |  |
| Retrofitter Foundry | activated ability (repeatable, not priced) | sac_outlet |
| Saheeli, Consul of Oversight | repeatable trigger (cadence not priced); unparsed text |  |
| Saheeli, Sublime Artificer | animation; copy effect; repeatable trigger (cadence not priced) |  |
| Sai, Master Thopterist | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Sami, Ship's Engineer | repeatable trigger (cadence not priced) |  |
| Sewer-veillance Cam | activated ability (repeatable, not priced) |  |
| Shore Up | unparsed text |  |
| Sokka, Bold Boomeranger | repeatable trigger (cadence not priced) |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Spicy Oatmeal Pizza | activated ability (repeatable, not priced) | closer |
| Springleaf Drum | activated ability (repeatable, not priced) |  |
| Stridehangar Automaton | additional or multiplied effect; replacement or prevention effect; unparsed text | token_maker |
| Strixhaven Skycoach | keyworded mechanic: crew | ramp |
| Talisman of Progress | activated ability (repeatable, not priced); unparsed text |  |
| Thopter Spy Network | repeatable trigger (cadence not priced) |  |
| Thorin Oakenshield | keyworded mechanic: storied; unparsed text | protection |
| Uthros Scanship | keyworded mechanic: station; unparsed text |  |
| Vraska, Soul of Stone | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Warmaker Gunship | keyworded mechanic: station; unparsed text |  |
| Whirler Rogue | unparsed text | closer |
| White Auracite | activated ability (repeatable, not priced) |  |
| Wurmwall Sweeper | keyworded mechanic: station; unparsed text |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 11; cards: Melded Moxite, Mouser Foundry, Pinnacle Emissary, Retrofitter Foundry, Saheeli, Consul of Oversight, Saheeli, Sublime Artificer, Sai, Master Thopterist, Sami, Ship's Engineer, Thopter Spy Network, Vraska, Soul of Stone, Whirler Rogue |
| parallel producers | event: creature token enters; independent sources: 13; cards: Carrot Cake, Cori-Steel Cutter, Melded Moxite, Mouser Foundry, Pinnacle Emissary, Retrofitter Foundry, Saheeli, Consul of Oversight, Saheeli, Sublime Artificer, Sai, Master Thopterist, Sami, Ship's Engineer, Thopter Spy Network, Vraska, Soul of Stone, Whirler Rogue |
| replacement amplification | amplifier: Stridehangar Automaton; adds per event: 1 extra token; events it sees (sources): 12 |
| scaling | card: Craterclaw Colossus; output: team +X power, X = your artifacts |
| bounded feedback | cycle: Stridehangar Automaton: replacement -> Saheeli, Consul of Oversight: scry_surveil -> Gossip's Talent: enter; limit: once per turn: Saheeli, Consul of Oversight: scry_surveil |
| resource-quality feedback | card: Lumen-Class Frigate; route: creature power -> station charge -> at 2+ other creatures +1/+1 -> more power to station and attack; barrier: needs 2 charge from tapped creatures (sorcery speed) |
| linear payoff | Bespoke Bō: enter -> interaction (fed by 1 cards) |
| linear payoff | Bident of Thassa: combat_damage -> cards (fed by combat) |
| linear payoff | Boosted Sloop: attack -> cards (fed by combat) |
| linear payoff | Coruscation Mage: cast -> damage to each opponent (fed by 48 cards) |
| linear payoff | Craterclaw Colossus: enter -> power (fed by 1 cards) |
| linear payoff | Cryogen Relic: leave -> cards (fed by 0 cards) |
| linear payoff | Cryogen Relic: enter -> cards (fed by 1 cards) |
| linear payoff | Curiosity Crafter: combat_damage -> cards (fed by combat) |
| linear payoff | Elsewhere Flask: enter -> cards (fed by 1 cards) |
| linear payoff | Guidelight Matrix: enter -> cards (fed by 1 cards) |
| linear payoff | Instant Ramen: enter -> cards (fed by 1 cards) |
| linear payoff | Melded Moxite: enter -> cards (fed by 1 cards) |
| linear payoff | Omni-Cheese Pizza: enter -> cards (fed by 1 cards) |
| linear payoff | Raff, Weatherlight Stalwart: cast -> cards (fed by 18 cards) |
| feed-forward chain | Carrot Cake: sacrifice -> Gossip's Talent: enter -> Saheeli, Consul of Oversight: scry_surveil -> Reckless Fireweaver: enter |
| feed-forward chain | Carrot Cake: sacrifice -> Gossip's Talent: enter -> Saheeli, Consul of Oversight: scry_surveil -> Stridehangar Automaton: replacement -> Reckless Fireweaver: enter |
| feed-forward chain | Carrot Cake: sacrifice -> Saheeli, Consul of Oversight: scry_surveil -> Gossip's Talent: enter |
| feed-forward chain | Carrot Cake: sacrifice -> Saheeli, Consul of Oversight: scry_surveil -> Reckless Fireweaver: enter |
| feed-forward chain | Carrot Cake: sacrifice -> Saheeli, Consul of Oversight: scry_surveil -> Stridehangar Automaton: replacement -> Gossip's Talent: enter |
| feed-forward chain | Carrot Cake: sacrifice -> Saheeli, Consul of Oversight: scry_surveil -> Stridehangar Automaton: replacement -> Reckless Fireweaver: enter |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.24 | 0.98 | 2.33 | 4.06 | 5.88 | 7.6 |
| can attack | 0.24 | 0.98 | 2.31 | 4.01 | 5.79 | 7.46 |
| with 2+ uses | 0.0 | 0.09 | 1.01 | 2.06 | 2.82 | 3.53 |
| attacked | 0.08 | 0.9 | 2.08 | 4.1 | 5.67 | 7.4 |
| could attack but spent before combat | 0.01 | 0.01 | 0.03 | 0.07 | 0.09 | 0.13 |
| tapped to station | 0.03 | 0.24 | 0.7 | 0.72 | 0.67 | 0.72 |
| tapped to crew | 0.0 | 0.06 | 0.13 | 0.28 | 0.36 | 0.33 |
| spent for mana | 0.02 | 0.04 | 0.32 | 0.49 | 0.48 | 0.71 |
| tapped for other costs | 0 | 0 | 0.01 | 0.04 | 0.08 | 0.17 |
| untapped at end | 0.85 | 1.24 | 1.88 | 2.84 | 4.11 | 6.07 |
| station charge still needed | 0.63 | 1.11 | 1.24 | 0.77 | 0.53 | 0.39 |
| spells waiting in hand | 2.99 | 2.57 | 1.89 | 1.4 | 1.07 | 1.02 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 6% | 85% | 1% | 16% | 71% | spells waiting for mana |
| T4 | 15% | 80% | 1% | 12% | 74% | spells waiting for mana |
| T5 | 22% | 64% | 2% | 28% | 73% | spells waiting for mana |
| T6 | 15% | 46% | 6% | 5% | 81% | spells waiting for mana |
| T7 | 10% | 33% | 8% | 17% | 87% | spells waiting for mana |
| T8 | 8% | 27% | 9% | 14% | 91% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 28 | 10.8 | 24.2 | +0.0 (SE 0.0) |
| station_first | 30 | 10.6 | 24.1 | +2.4 (SE 4.2) |
| mana_first | 30 | 12.2 | 23.8 | +33.2 (SE 45.9) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 72.7% / 93.0% |
| light blockers: lethal by T10 | 41.0% |
| light blockers: median damage by T8 / T10 | 12 / 28 |
| tokens per turn T4-T8 (mean) | 2.17 |
| cards drawn by T8 (mean, incl. normal draws) | 14.1 |
| board at end of T8 (median bodies / power) | 8 / 16 |
| power per body at end of T8 (median) | 1.91 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 10 -> 9 | -70.3 (SE 17.3) |
| exile wipe after T6 | 10 -> 9 | -70.3 (SE 17.3) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.63 | -59.8 (SE 16.9) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 10 -> 4; commander casts T7-T10 2.45 | -74.2 (SE 17.3) |
| no commander (ablation) | tokens per turn T4-T8: 2.17 -> 0.84 | -60.9 (SE 16.7) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Bespoke Bō | equipped creature gets +2/+1 and has vigilance. |
| Bident of Thassa | creatures your opponents control attack this turn if able |
| Blasphemous Act | this spell costs {1} less to cast for each creature on the battlefield. |
| Cori-Steel Cutter | equipped creature gets +1/+1 and has trample and haste. |
| Desculpting Blast | if it was attacking and "this token can block only creatures with flying " |
| Drill Too Deep | choose one — |
| Elsewhere Flask | choose a basic land type each land you control becomes that type until end of turn |
| Emergency Eject | its controller creates a lander token |
| Flame Fusillade | until end of turn permanents you control gain "{t}: " |
| Fountainport Bell | search your library for a basic land card reveal it then shuffle and put that card on top |
| Galvanic Blast | metalcraft ~ deals 4 damage instead if you control three or more artifacts |
| Geistwave | if you controlled that permanent |
| Generous Gift | its controller creates a 3/3 green elephant creature token |
| Gossip's Talent | {1}{u}: level 2 — whenever you attack, target attacking creature with power 3 or less can't be blocked this turn.; {3}{u}: level 3 — whenever a creature you con |
| Guidelight Matrix | target mount you control becomes saddled until end of turn; target vehicle you control becomes an artifact creature until end of turn |
| Melded Moxite | discard a card if you do |
| Mouser Attack! | choose one — |
| Mouser Foundry | it |
| Pinnacle Emissary | "this token can block only creatures with flying "; warp {u/r} |
| Plunder the Trollshaws | if this spell was cast from a graveyard instead |
| Prismari Charm | choose one —; • then |
| Reality Shift | its controller manifests the top card of their library |
| Resculpt | its controller creates a 4/4 blue and red elemental creature token |
| Retrofitter Foundry | untap |
| Saheeli, Sublime Artificer | [−2]: target artifact you control becomes a copy of another target artifact or creature you control until end of turn, except it's an artifact in addition to it |
| Shore Up | untap it |
| Sokka, Bold Boomeranger | discard up to two cards then draw that many cards |
| Spicy Oatmeal Pizza | it and 3 damage to you |
| Strixhaven Skycoach | search your library for a basic land card reveal it put it into your hand then shuffle |
| Talisman of Progress | deals 1 damage to you |
| Thorin Oakenshield | as long as you have an enduring story, artifacts and creatures you control have ward {1}. |
| Warmaker Gunship | it deals damage equal to the number of artifacts you control to target creature an opponent controls |
| Whirler Rogue | target creature |

## Uncertainty

- 60 of 64 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 31 of 64 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
