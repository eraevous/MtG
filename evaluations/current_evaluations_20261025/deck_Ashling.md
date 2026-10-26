# Deck: Ashling

- Ashling, the Limitless (WUBRG), 100 cards, companion Jegantha, the Wellspring
- Lands 37, nonland 62 (creatures 30), average nonland mana value 3.37
- Mana (goldfish, on the draw): 4 by T4 82.1%, all colors by T5 40.2%, commander out by T4 63.0% / T6 91.8%
- Weakest areas (seen by T7 vs target): protection:anti_wipe 14.1% (1 cards), protection 46.2% (4 cards), spot_removal 66.8% (7 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 2; unopposed goldfish lethal by T10 81.7% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 8 three turns later
- Without the commander: damage by T10 -0.3 (paired); typed coverage 14 of 63 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 1 | 0 to 10 | 6 of 13 |
| tap claimants per creature card | 0.03 | 0.0 to 0.62 | 7 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 0 | 0 to 5 | 8 of 13 |
| creature cards | 31 | 16 to 44 | 8 of 13 |
| creatures with power 4+ | 7 | 2 to 12 | 9 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 1 | 0 to 4 | 5 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Kithkeeper | tap creatures | 3 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Ashling, the Limitless | no | - | - | 0 | Duty Beyond Death, Flock Impostor, Personify |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 3 |
| 2 | 22 |
| 3 | 14 |
| 4 | 8 |
| 5 | 8 |
| 6 | 4 |
| 7+ | 3 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 18 | 10 | Excessive |
| fixing | 36 | 24 | Strong |
| draw | 12 | 10 | Strong |
| spot_removal | 7 | 8 | Adequate |
| wipe | 2 | 2 | Strong |
| counterspell | 1 | None | not scored |
| protection | 4 | 5 | Adequate |
| recursion | 4 | 3 | Strong |
| closer | 6 | 4 | Strong |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 17 | 86.3% | 91.0% | 94.2% | 97.1% | 94.2% |
| draw | 12 | 74.3% | 80.8% | 85.8% | 91.0% | 90.0% |
| spot_removal | 7 | 53.7% | 60.8% | 66.8% | 74.5% | 71.9% |
| wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 46.2% |
| recursion | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 85.8% |
| closer | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 66.8% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| protection:all_creatures | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| counterspell | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| fixing | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 100.0% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection:anti_wipe | 1 | 2 | 14.1% | 26.4% | 12.3 |
| protection | 4 | 5 | 46.2% | 54.1% | 7.9 |
| spot_removal | 7 | 8 | 66.8% | 71.9% | 5.1 |
| wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| draw | 12 | 10 | 85.8% | 79.9% | -5.9 |
| recursion | 4 | 3 | 46.2% | 37.0% | -9.2 |
| ramp | 17 | 10 | 94.2% | 79.9% | -14.3 |
| closer | 6 | 4 | 61.0% | 46.2% | -14.8 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Ashling's Command | damage | ordinary |
| Blasphemous Act | damage | ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Duty Beyond Death | indestructible | all_creatures | damage, destroy |
| Flock Impostor | blink/bounce own | single_target | damage, destroy, exile, minus, sacrifice |
| Personify | blink/bounce own | single_target | damage, destroy, exile, minus, sacrifice |
| Tam, Mindful First-Year | hexproof | other_creatures | - |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Graveshifter | hand | any creature | one-shot |
| Muldrotha, the Gravetide | cast | other | one-shot |
| Ninja Teen | cast | any creature | repeatable |
| Unbury | hand | any creature | one-shot |
| Unbury | hand | any creature | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 26.4% | package | 8/2/2 | yes |
| counters | 0.0% | fragment | 2/0 |  |
| artifact_tokens | 0.0% | fragment | 0/2 |  |
| lifegain | 0.0% | fragment | 6/0 |  |
| blink | 13.5% | package | 1/19 | yes |
| landfall | 3.5% | package | 2/1 | yes |
| spellslinger | 0.0% | fragment | 12/0 |  |
| graveyard | 11.7% | package | 2/4 | yes |
| go_wide | 61.0% | redundant | 8/6 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Arcane Denial | repeatable trigger (cadence not priced) |  |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Ashling's Command | copy effect; unparsed text |  |
| Ashling, Rekindled // Ashling, Rimebound | repeatable trigger (cadence not priced); unparsed text |  |
| Ashling, the Limitless | copy effect; keyworded mechanic: evoke; repeatable trigger (cadence not priced); unparsed text |  |
| Belonging | unparsed text |  |
| Blasphemous Act | cost reduction or free cast |  |
| Celestial Reunion | X-scaled magnitude; replacement or prevention effect; unparsed text |  |
| Chomping Changeling | unparsed text |  |
| Chromatic Lantern | activated ability (repeatable, not priced) |  |
| Continue? | unparsed text | recursion |
| Cream of the Crop | X-scaled magnitude; repeatable trigger (cadence not priced); unparsed text |  |
| Determined Iteration | repeatable trigger (cadence not priced); unparsed text | copy, token_maker |
| Dimir Signet | activated ability (repeatable, not priced) | fixing |
| Distant Melody | unparsed text |  |
| Duty Beyond Death |  | spot_removal, wipe |
| Erode | unparsed text |  |
| Faeburrow Elder | activated ability (repeatable, not priced); unparsed text | fixing |
| Fellwar Stone | activated ability (repeatable, not priced) |  |
| Fertile Ground | additional or multiplied effect; repeatable trigger (cadence not priced); unparsed text |  |
| Firdoch Core | activated ability (repeatable, not priced); animation; unparsed text |  |
| Flamebraider | activated ability (repeatable, not priced); unparsed text |  |
| Flock Impostor | unparsed text |  |
| Foundation Breaker | keyworded mechanic: evoke | recursion |
| Frostcliff Siege | repeatable trigger (cadence not priced); unparsed text |  |
| Garruk's Uprising | repeatable trigger (cadence not priced) |  |
| Graveshifter | unparsed text |  |
| Gruul Signet | activated ability (repeatable, not priced) | fixing |
| Hoofprints of the Stag | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text | draw |
| Horde of Notions | activated ability (repeatable, not priced); cost reduction or free cast | recursion |
| Incandescent Soulstoke | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Ingot Chewer | keyworded mechanic: evoke | recursion |
| Izzet Signet | activated ability (repeatable, not priced) | fixing |
| Kithkeeper | X-scaled magnitude; unparsed text |  |
| Lamentation | unparsed text | token_maker |
| Maelstrom Wanderer | unparsed text |  |
| Mass of Mysteries | repeatable trigger (cadence not priced) | copy, token_maker |
| Mulldrifter | keyworded mechanic: evoke | recursion |
| Ninja Teen | activated ability (repeatable, not priced); keyworded mechanic: sneak; repeatable trigger (cadence not priced) |  |
| Omnath, Locus of the Roil | repeatable trigger (cadence not priced) | closer |
| Prismatic Undercurrents | X-scaled magnitude; additional or multiplied effect; unparsed text |  |
| Realmwalker | unparsed text | recursion |
| Relic of Legends | activated ability (repeatable, not priced) |  |
| Rimekin Recluse |  | spot_removal |
| Risen Reef | repeatable trigger (cadence not priced); unparsed text |  |
| Selesnya Signet | activated ability (repeatable, not priced) | fixing |
| Shimmercreep | X-scaled magnitude |  |
| Shriekmaw | keyworded mechanic: evoke; unparsed text | recursion |
| Simic Signet | activated ability (repeatable, not priced) | fixing |
| Smokebraider | activated ability (repeatable, not priced); unparsed text |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Splinter's Technique | keyworded mechanic: sneak | recursion |
| Tam, Mindful First-Year | activated ability (repeatable, not priced) |  |
| Tanufel Rimespeaker | repeatable trigger (cadence not priced) |  |
| Twinflame Travelers | additional or multiplied effect |  |
| Unbury | unparsed text |  |
| Urza's Incubator | cost reduction or free cast; unparsed text |  |
| Vernal Sovereign | repeatable trigger (cadence not priced) |  |
| Witherbloom Charm | unparsed text |  |
| Yarok, the Desecrated | additional or multiplied effect |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: creature token enters; independent sources: 3; cards: Belonging, Hoofprints of the Stag, Vernal Sovereign |
| linear payoff | Chomping Changeling: enter -> interaction (fed by 1 cards) |
| linear payoff | Flock Impostor: enter -> interaction (fed by 1 cards) |
| linear payoff | Foundation Breaker: enter -> interaction (fed by 1 cards) |
| linear payoff | Graveshifter: enter -> recursion (fed by 1 cards) |
| linear payoff | Ingot Chewer: enter -> interaction (fed by 1 cards) |
| linear payoff | Lamentation: enter -> interaction, life (fed by 1 cards) |
| linear payoff | Rimekin Recluse: enter -> interaction (fed by 1 cards) |
| linear payoff | Shriekmaw: enter -> interaction (fed by 1 cards) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.12 | 0.64 | 1.4 | 2.3 | 3.16 | 3.92 |
| can attack | 0.12 | 0.64 | 1.4 | 2.3 | 3.16 | 3.92 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.05 | 0.49 | 1.08 | 1.98 | 2.5 | 3.33 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0.09 | 0.05 |
| untapped at end | 0.56 | 0.84 | 1.18 | 1.31 | 1.68 | 1.6 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.77 | 3.53 | 3.11 | 2.48 | 1.86 | 1.37 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 87% | 0% | 7% | 51% | spells waiting for mana |
| T4 | 0% | 88% | 0% | 15% | 70% | spells waiting for mana |
| T5 | 0% | 82% | 0% | 33% | 76% | spells waiting for mana |
| T6 | 0% | 69% | 0% | 30% | 81% | spells waiting for mana |
| T7 | 0% | 55% | 0% | 53% | 89% | spells waiting for mana |
| T8 | 0% | 45% | 0% | 43% | 82% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 2 | 0.0 | 12.6 | +0.0 (SE 0.0) |
| station_first | 2 | 0.0 | 12.6 | +0.0 (SE 0.0) |
| mana_first | 2 | 0.0 | 12.6 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 16.0% / 81.7% |
| light blockers: lethal by T10 | 0.7% |
| light blockers: median damage by T8 / T10 | 1 / 2 |
| tokens per turn T4-T8 (mean) | 0.15 |
| cards drawn by T8 (mean, incl. normal draws) | 9.5 |
| board at end of T8 (median bodies / power) | 4 / 11 |
| power per body at end of T8 (median) | 2.50 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 8 | -2.8 (SE 0.3) |
| exile wipe after T6 | 7 -> 8 | -2.8 (SE 0.3) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.76 | -2.5 (SE 0.3) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 3; commander casts T7-T10 2.73 | -3.1 (SE 0.3) |
| no commander (ablation) | tokens per turn T4-T8: 0.15 -> 0.17 | -0.3 (SE 0.3) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Arcane Denial | its controller may draw up to two cards at the beginning of the next turn's upkeep; you at the beginning of the next turn's upkeep |
| Ashling's Command | choose two —; • create a token that's a copy of target elemental you control.; • target player draws two cards.; • ~ deals 2 damage to each creature target play |
| Ashling, Rekindled // Ashling, Rimebound | ~ {1}{r}; or transforms into ~ you may discard a card if you do; pay {u} if you do transform ~; ~, rimebound; whenever this creature transforms into ~, rimeboun |
| Ashling, the Limitless | elemental permanent spells you cast from your hand gain evoke {4} as you cast them.; create a token that's a copy of it the token gains haste until end of turn  |
| Belonging | encore {6}{w}{w} |
| Blasphemous Act | this spell costs {1} less to cast for each creature on the battlefield. |
| Celestial Reunion | search your library for a creature card with mana value x or less reveal it put it into your hand then shuffle if this spell's additional cost was paid and the  |
| Chromatic Lantern | lands you control have "{t}: add one mana of any color." |
| Continue? | choose up to four target creature cards in your graveyard that were put there from the battlefield this turn return them to the battlefield |
| Cream of the Crop | look at the top x cards of your library where x is that creature's power if you do put one of those cards on top of your library and the rest on the bottom of y |
| Determined Iteration | populate the token created this way gains haste sacrifice it at the beginning of the next end step |
| Distant Melody | choose a creature type for each permanent you control of that type |
| Duty Beyond Death | creatures you control gain indestructible until end of turn |
| Erode | its controller may search their library for a basic land card put it onto the battlefield tapped then shuffle |
| Faeburrow Elder | this creature gets +1/+1 for each color among permanents you control.; for each color among permanents you control add one mana of that color |
| Fellwar Stone | that a land an opponent controls could produce |
| Fertile Ground | enchant land; whenever enchanted land is tapped for mana, its controller adds an additional one mana of any color. |
| Firdoch Core | becomes a 4/4 artifact creature until end of turn |
| Flamebraider | add two mana in any combination of colors spend this mana only to cast elemental spells or activate abilities of elemental sources |
| Foundation Breaker | evoke {1}{g} |
| Frostcliff Siege | as this enchantment enters, choose jeskai or temur.; • jeskai — whenever one or more creatures you control deal combat damage to a player, draw a card.; • temur |
| Garruk's Uprising | if you control a creature with power 4 or greater; creatures you control have trample. |
| Hoofprints of the Stag | put a hoofprint counter on this enchantment; activate only during your turn |
| Horde of Notions | play target elemental card from your graveyard without paying its mana cost |
| Incandescent Soulstoke | other elemental creatures you control get +1/+1.; put an elemental creature card from your hand onto the battlefield that creature gains haste until end of turn |
| Ingot Chewer | evoke {r} |
| Kithkeeper | vivid — when this creature enters, create x 1/1 green and white kithkin creature tokens, where x is the number of colors among permanents you control.; this |
| Lamentation | encore {6}{b}{b} |
| Maelstrom Wanderer | creatures you control have haste.; cascade, cascade |
| Mass of Mysteries | another target elemental you control gains myriad until end of turn |
| Muldrotha, the Gravetide | during each of your turns, you may play a land and cast a permanent spell of each permanent type from your graveyard. |
| Mulldrifter | evoke {2}{u} |
| Ninja Teen | whenever a creature you control leaves the battlefield, each opponent loses 1 life.; {1}{b}: level 2; creatures you control get +1/+0 and have menace.; {b}: lev |
| Omnath, Locus of the Roil | it deals damage to any target equal to the number of elementals you control; if you control eight or more lands |
| Prismatic Undercurrents | vivid — when this enchantment enters, search your library for up to x basic land cards, where x is the number of colors among permanents you control. reveal tho |
| Realmwalker | as this creature enters, choose a creature type.; you may look at the top card of your library any time.; you may cast creature spells of the chosen type from t |
| Risen Reef | look at the top card of your library if it's a land card you may put it onto the battlefield tapped if you don't put the card onto the battlefield put it into y |
| Shimmercreep | vivid — when this creature enters, each opponent loses x life and you gain x life, where x is the number of colors among permanents you control. |
| Shriekmaw | fear; evoke {1}{b} |
| Smokebraider | add two mana in any combination of colors spend this mana only to cast elemental spells or activate abilities of elementals |

## Uncertainty

- 60 of 63 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 14 of 63 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
