# Deck: Dina

- Dina, Essence Brewer (BG), 100 cards
- Lands 37, nonland 62 (creatures 38), average nonland mana value 3.05
- Mana (goldfish, on the draw): 4 by T4 72.6%, all colors by T5 95.9%, commander out by T4 87.7% / T6 96.3%
- Weakest areas (seen by T7 vs target): protection 0.0% (0 cards), protection:anti_wipe 0.0% (0 cards), spot_removal 54.1% (5 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 5; unopposed goldfish lethal by T10 85.7% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 6 three turns later
- Without the commander: damage by T10 -0.1 (paired); typed coverage 12 of 63 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 0 | 0 to 10 | 12 of 13 |
| tap claimants per creature card | 0.0 | 0.0 to 0.62 | 12 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 2 | 0 to 5 | 4 of 13 |
| creature cards | 39 | 16 to 44 | 10 of 13 |
| creatures with power 4+ | 5 | 2 to 12 | 6 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 1 | 0 to 4 | 5 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Buzzard-Wasp Colony | sacrifice artifacts | 1 | per use |
| Deadly Dispute | sacrifice artifacts | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Dina, Essence Brewer | no | - | - | 0 | none |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 4 |
| 2 | 18 |
| 3 | 21 |
| 4 | 11 |
| 5 | 7 |
| 7+ | 1 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 12 | 10 | Strong |
| fixing | 16 | 6 | Excessive |
| draw | 10 | 10 | Strong |
| spot_removal | 5 | 8 | Adequate |
| wipe | 3 | 2 | Strong |
| counterspell | 0 | None | not scored |
| protection | 0 | 5 | Absent |
| recursion | 11 | 3 | Excessive |
| closer | 10 | 4 | Excessive |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 12 | 74.3% | 80.8% | 85.8% | 91.0% | 85.8% |
| draw | 9 | 63.3% | 70.4% | 76.2% | 83.1% | 79.9% |
| spot_removal | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 83.1% |
| wipe | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 66.8% |
| protection | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| recursion | 11 | 71.0% | 77.8% | 83.1% | 88.9% | 88.1% |
| closer | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 83.1% |
| fixing | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 96.0% |
| counter_preservation | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 0 | 5 | 0.0% | 54.1% | 54.1 |
| protection:anti_wipe | 0 | 2 | 0.0% | 26.4% | 26.4 |
| spot_removal | 5 | 8 | 54.1% | 71.9% | 17.8 |
| draw | 9 | 10 | 76.2% | 79.9% | 3.7 |
| ramp | 12 | 10 | 85.8% | 79.9% | -5.9 |
| wipe | 3 | 2 | 37.0% | 26.4% | -10.6 |
| closer | 10 | 4 | 79.9% | 46.2% | -33.7 |
| recursion | 11 | 3 | 83.1% | 37.0% | -46.0 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Toxic Deluge | minus | indestructible, ordinary |
| Vicious Rivalry | destroy | big_toughness, ordinary |
| Withering Curse | destroy, minus | indestructible, big_toughness, ordinary |

## Typed protection

- No protection read.

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Along the Crooked Way | hand | any creature | one-shot |
| Bloodghast | battlefield | self only | repeatable |
| Cauldron of Essence | battlefield | any creature | repeatable |
| Defiled Crypt // Cadaver Lab | hand | any creature | one-shot |
| Mudflat Village | hand | narrow creature types | one-shot |
| Nether Traitor | battlefield | self only | repeatable |
| Ninja Teen | cast | any creature | repeatable |
| Rise of the Witch-king | battlefield | any card of a type | one-shot |
| The Hunger Tide Rises | battlefield | any creature | one-shot |
| Unbury | hand | any creature | one-shot |
| Unbury | hand | any creature | one-shot |
| Veinwitch Coven | hand | any creature | one-shot |
| Witch of the Moors | hand | any creature | repeatable |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 97.8% | redundant | 22/11/16 | yes |
| counters | 0.0% | fragment | 4/0 | yes |
| artifact_tokens | 37.0% | redundant | 3/11 | yes |
| lifegain | 61.0% | redundant | 20/6 | yes |
| blink | 0.0% | fragment | 0/10 |  |
| landfall | 5.0% | package | 3/1 | yes |
| spellslinger | 0.0% | fragment | 11/0 |  |
| graveyard | 0.0% | fragment | 0/11 |  |
| go_wide | 78.0% | redundant | 22/10 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Al Bhed Salvagers | repeatable trigger (cadence not priced) |  |
| Along the Crooked Way | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Awakening Zone | repeatable trigger (cadence not priced) |  |
| Beledros Witherbloom | repeatable trigger (cadence not priced); unparsed text | death_payoff |
| Bitterbloom Bearer | repeatable trigger (cadence not priced) |  |
| Blight Mound | repeatable trigger (cadence not priced); unparsed text |  |
| Blood Artist | repeatable trigger (cadence not priced) |  |
| Bloodghast | repeatable trigger (cadence not priced); unparsed text |  |
| Buzzard-Wasp Colony | repeatable trigger (cadence not priced) | closer, sac_outlet |
| Cauldron of Essence | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text | spot_removal |
| Chomping Changeling | unparsed text |  |
| Deadly Dispute |  | fixing |
| Defiled Crypt // Cadaver Lab | repeatable trigger (cadence not priced); unparsed text |  |
| Defiling Daemogoth | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Dimir House Guard | unparsed text |  |
| Dina, Essence Brewer | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text | spot_removal |
| Dina, Soul Steeper | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced) | lifegain_source |
| Elvish Mystic | activated ability (repeatable, not priced) |  |
| Essenceknit Scholar | repeatable trigger (cadence not priced) |  |
| Gorma, the Gullet | additional or multiplied effect; repeatable trigger (cadence not priced) | wipe |
| Great Fierce Bee | repeatable trigger (cadence not priced) |  |
| Haywire Mite | activated ability (repeatable, not priced) | death_payoff |
| Immoral Bargain | X-scaled magnitude | spot_removal |
| Jadar, Ghoulcaller of Nephalia | repeatable trigger (cadence not priced) |  |
| Loading Zone | replacement or prevention effect; unparsed text | counter_multiplier |
| Lord Dregg, Insect Invader | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Mazirek, Kraul Death Priest | repeatable trigger (cadence not priced) | wipe |
| Mirkwood Bats | repeatable trigger (cadence not priced) |  |
| Moldervine Reclamation | repeatable trigger (cadence not priced) |  |
| Nadier's Nightblade | repeatable trigger (cadence not priced) |  |
| Nether Traitor | repeatable trigger (cadence not priced); unparsed text |  |
| Ninja Teen | activated ability (repeatable, not priced); keyworded mechanic: sneak; repeatable trigger (cadence not priced) |  |
| Pawn of Ulamog | repeatable trigger (cadence not priced) |  |
| Pest Infestation | X-scaled magnitude | death_payoff, token_maker |
| Pest Rescuer | repeatable trigger (cadence not priced); replacement or prevention effect | death_payoff |
| Pestbrood Sloth | repeatable trigger (cadence not priced) | death_payoff |
| Pizza Face, Gastromancer | activated ability (repeatable, not priced); animation; repeatable trigger (cadence not priced) |  |
| Plumb the Forbidden | copy effect; unparsed text | wipe |
| Priest of Forgotten Gods | activated ability (repeatable, not priced) | spot_removal |
| Smothering Abomination | repeatable trigger (cadence not priced); unparsed text | spot_removal |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Sothera, the Supervoid | additional or multiplied effect; repeatable trigger (cadence not priced) |  |
| South Wind Avatar | repeatable trigger (cadence not priced) | lifegain_source |
| Springleaf Parade | X-scaled magnitude; activated ability (repeatable, not priced) |  |
| Starscape Cleric | keyworded mechanic: offspring; repeatable trigger (cadence not priced); unparsed text | lifegain_source, token_maker |
| Tendershoot Dryad | repeatable trigger (cadence not priced); unparsed text |  |
| The Hunger Tide Rises | unparsed text |  |
| Toxic Deluge | X-scaled magnitude |  |
| Twitching Doll | activated ability (repeatable, not priced); unparsed text |  |
| Unbury | unparsed text |  |
| Veinwitch Coven | repeatable trigger (cadence not priced) | lifegain_source |
| Vicious Rivalry | X-scaled magnitude |  |
| Victimize | unparsed text | recursion |
| Warren Soultrader |  | fixing |
| Wight of the Reliquary | activated ability (repeatable, not priced); unparsed text | wipe |
| Witch of the Moors | repeatable trigger (cadence not priced) | lifegain_source |
| Witherbloom Charm | unparsed text |  |
| Withering Curse | replacement or prevention effect | lifegain_source |
| Woe Strider | keyworded mechanic: escape; unparsed text | recursion |
| Zulaport Cutthroat | repeatable trigger (cadence not priced) |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 1; cards: Pizza Face, Gastromancer |
| parallel producers | event: creature token enters; independent sources: 9; cards: Awakening Zone, Bitterbloom Bearer, Blight Mound, Essenceknit Scholar, Jadar, Ghoulcaller of Nephalia, Pestbrood Sloth, Springleaf Parade, Twitching Doll, Woe Strider |
| linear payoff | Along the Crooked Way: enter -> recursion (fed by 1 cards) |
| linear payoff | Buzzard-Wasp Colony: enter -> cards (fed by 1 cards) |
| linear payoff | Cauldron of Essence: dies -> damage to each opponent (fed by 0 cards) |
| linear payoff | Chomping Changeling: enter -> interaction (fed by 1 cards) |
| linear payoff | Dina, Essence Brewer: sacrifice -> cards (fed by 0 cards) once per turn |
| linear payoff | Dina, Soul Steeper: lifegain -> damage to each opponent (fed by 6 cards) |
| linear payoff | Essenceknit Scholar: end_step -> cards (fed by each turn) |
| linear payoff | Gorma, the Gullet: dies -> power (fed by 0 cards) |
| linear payoff | Mirkwood Bats: create -> damage to each opponent (fed by 11 cards) |
| linear payoff | Smothering Abomination: sacrifice -> cards (fed by 0 cards) |
| linear payoff | South Wind Avatar: lifegain -> damage to each opponent (fed by 6 cards) |
| linear payoff | Starscape Cleric: lifegain -> damage to each opponent (fed by 6 cards) |
| linear payoff | Veinwitch Coven: lifegain -> recursion (fed by 6 cards) |
| linear payoff | Witch of the Moors: end_step -> recursion (fed by each turn) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.6 | 1.53 | 2.35 | 3.14 | 3.98 | 4.64 |
| can attack | 0.57 | 1.49 | 2.28 | 3.03 | 3.83 | 4.44 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.26 | 1.32 | 1.93 | 2.84 | 3.21 | 3.87 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 1.24 | 1.0 | 1.26 | 1.31 | 1.92 | 1.94 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 4.31 | 4.02 | 3.52 | 2.78 | 2.1 | 1.54 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 91% | 0% | 31% | 88% | spells waiting for mana |
| T4 | 0% | 92% | 0% | 17% | 74% | spells waiting for mana |
| T5 | 0% | 88% | 0% | 31% | 81% | spells waiting for mana |
| T6 | 0% | 80% | 0% | 18% | 82% | spells waiting for mana |
| T7 | 0% | 62% | 0% | 45% | 91% | spells waiting for mana |
| T8 | 0% | 47% | 0% | 42% | 91% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 5 | 0.0 | 12.1 | +0.0 (SE 0.0) |
| station_first | 5 | 0.0 | 12.1 | +0.0 (SE 0.0) |
| mana_first | 5 | 0.0 | 12.1 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 24.0% / 85.7% |
| light blockers: lethal by T10 | 2.0% |
| light blockers: median damage by T8 / T10 | 4 / 5 |
| tokens per turn T4-T8 (mean) | 0.33 |
| cards drawn by T8 (mean, incl. normal draws) | 9.4 |
| board at end of T8 (median bodies / power) | 5 / 9 |
| power per body at end of T8 (median) | 1.90 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 6 | -4.8 (SE 0.4) |
| exile wipe after T6 | 7 -> 6 | -5.4 (SE 0.4) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.72 | -3.0 (SE 0.3) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 4; commander casts T7-T10 2.12 | -4.7 (SE 0.4) |
| no commander (ablation) | tokens per turn T4-T8: 0.33 -> 0.36 | -0.1 (SE 0.4) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Al Bhed Salvagers | whenever this creature or another creature or artifact you control dies, target opponent loses 1 life and you gain 1 life. |
| Along the Crooked Way | whenever a creature card leaves your graveyard, amass goblins 1.; goblins and orcs you control gain menace until end of turn |
| Awakening Zone | it has "sacrifice this token: " |
| Beledros Witherbloom | at the beginning of each upkeep, create a 1/1 black and green pest creature token with "when this token dies, you gain 1 life."; pay 10 life: untap all lands yo |
| Bitterbloom Bearer | you lose 1 life and |
| Blight Mound | attacking pests you control get +1/+0 and have menace. |
| Blood Artist | whenever this creature or another creature dies, target player loses 1 life and you gain 1 life. |
| Bloodghast | this creature can't block.; this creature has haste as long as an opponent has 10 or less life.; return this card from your graveyard to the battlefield |
| Buzzard-Wasp Colony | sacrifice an artifact or creature if you do; if it had counters on it put its counters on |
| Defiled Crypt // Cadaver Lab | ~ {3}{b}; whenever one or more cards leave your graveyard, create a 2/2 black horror enchantment creature token. this ability triggers only once each turn.; cad |
| Defiling Daemogoth | each opponent loses x life where x is the amount of life you gained this turn |
| Dimir House Guard | fear; regenerate; transmute {1}{b}{b} |
| Dina, Essence Brewer | you gain x life and put x +1/+1 counters on target creature you control where x is the sacrificed creature's power |
| Dina, Soul Steeper | ~ gets +x/+0 until end of turn where x is the sacrificed creature's power |
| Essenceknit Scholar | if a creature died under your control this turn |
| Gorma, the Gullet | nontoken creatures you control enter with an additional +1/+1 counter on them for each creature that died under your control this turn. |
| Immoral Bargain | destroy x target nonland permanents |
| Jadar, Ghoulcaller of Nephalia | if you control no creatures with decayed |
| Loading Zone | if one or more counters would be put on a creature, spacecraft, or planet you control, twice that many of each of those kinds of counters are put on it instead. |
| Lord Dregg, Insect Invader | disappear — at the beginning of your end step, if a permanent left the battlefield under your control this turn, create a 1/1 black insect warrior creature toke |
| Mazirek, Kraul Death Priest | whenever a player sacrifices another permanent, put a +1/+1 counter on each creature you control. |
| Nadier's Nightblade | whenever a token you control leaves the battlefield, each opponent loses 1 life and you gain 1 life. |
| Nether Traitor | shadow; whenever another creature is put into your graveyard from the battlefield, you may pay {b}. if you do, return this card from your graveyard to the battl |
| Ninja Teen | whenever a creature you control leaves the battlefield, each opponent loses 1 life.; {1}{b}: level 2; creatures you control get +1/+0 and have menace.; {b}: lev |
| Pawn of Ulamog | whenever this creature or another nontoken creature you control dies, you may create a 0/1 colorless eldrazi spawn creature token. it has "sacrifice this token: |
| Pest Infestation | destroy up to x target artifacts and/or enchantments create twice x 1/1 black and green pest creature tokens with "when this token dies " |
| Pest Rescuer | at the beginning of each upkeep, if you don't control a pest creature token, create a 1/1 black and green pest creature token with "when this token dies, you ga |
| Pizza Face, Gastromancer | disappear — at the beginning of your end step, if a permanent left the battlefield under your control this turn, put three +1/+1 counters on up to one other tar |
| Plumb the Forbidden | you and lose 1 life |
| Priest of Forgotten Gods | any number of target players each lose 2 life and sacrifice a creature of their choice you and |
| Rise of the Witch-king | each player sacrifices a creature of their choice if you sacrificed a creature this way you may return another permanent card from your graveyard to the battlef |
| Sakura-Tribe Elder | search your library for a basic land card put that card onto the battlefield tapped then shuffle |
| Smothering Abomination | devoid; sacrifice a creature |
| Sothera, the Supervoid | each opponent chooses a creature they control and exiles it; if a player controls no creatures sacrifice ~ then put a creature card exiled with it onto the batt |
| South Wind Avatar | you gain life equal to its toughness |
| Springleaf Parade | creature tokens you control have "{t}: add one mana of any color." |
| Starscape Cleric | this creature can't block. |
| Tendershoot Dryad | ascend; at the beginning of each upkeep, create a 1/1 green saproling creature token.; saprolings you control get +2/+2 as long as you have the city's blessing. |
| The Hunger Tide Rises | i, ii, iii — create a 1/1 black and green insect creature token.; iv — sacrifice any number of creatures. search your library and/or graveyard for a creature ca |
| Toxic Deluge | all creatures get x/ x until end of turn |

## Uncertainty

- 61 of 63 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 12 of 63 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
