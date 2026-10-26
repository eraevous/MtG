# Deck: Blight Curse

- Auntie Ool, Cursewretch (BRG), 100 cards
- Lands 39, nonland 60 (creatures 27), average nonland mana value 3.67
- Mana (goldfish, on the draw): 4 by T4 73.5%, all colors by T5 87.8%, commander out by T4 56.8% / T6 90.7%
- Weakest areas (seen by T7 vs target): protection 0.0% (0 cards), protection:anti_wipe 0.0% (0 cards), closer 26.4% (2 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 0; unopposed goldfish lethal by T10 80.3% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 9 three turns later
- Without the commander: damage by T10 +0.5 (paired); typed coverage 6 of 61 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 0 | 0 to 10 | 12 of 13 |
| tap claimants per creature card | 0.0 | 0.0 to 0.62 | 12 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 0 | 0 to 5 | 8 of 13 |
| creature cards | 28 | 16 to 44 | 6 of 13 |
| creatures with power 4+ | 12 | 2 to 12 | 13 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

- No shared-resource claims read.

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Auntie Ool, Cursewretch | no | - | - | 0 | none |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 2 |
| 2 | 15 |
| 3 | 15 |
| 4 | 10 |
| 5 | 8 |
| 6 | 7 |
| 7+ | 3 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 10 | 10 | Strong |
| fixing | 21 | 12 | Excessive |
| draw | 15 | 10 | Strong |
| spot_removal | 10 | 8 | Strong |
| wipe | 7 | 2 | Excessive |
| counterspell | 0 | None | not scored |
| protection | 0 | 5 | Absent |
| recursion | 5 | 3 | Excessive |
| closer | 2 | 4 | Adequate |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 85.8% |
| draw | 14 | 79.9% | 85.8% | 90.0% | 94.2% | 95.2% |
| spot_removal | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 95.2% |
| wipe | 7 | 53.7% | 60.8% | 66.8% | 74.5% | 71.9% |
| protection | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| recursion | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 83.1% |
| closer | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 46.2% |
| fixing | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 98.8% |
| counter_preservation | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 0 | 5 | 0.0% | 54.1% | 54.1 |
| protection:anti_wipe | 0 | 2 | 0.0% | 26.4% | 26.4 |
| closer | 2 | 4 | 26.4% | 46.2% | 19.8 |
| ramp | 10 | 10 | 79.9% | 79.9% | 0.0 |
| spot_removal | 10 | 8 | 79.9% | 71.9% | -8.0 |
| draw | 14 | 10 | 90.0% | 79.9% | -10.1 |
| recursion | 5 | 3 | 54.1% | 37.0% | -17.1 |
| wipe | 7 | 2 | 66.8% | 26.4% | -40.4 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Archfiend of Ifnir | asymmetric, minus | indestructible, ordinary |
| Black Sun's Zenith | minus | indestructible, ordinary |
| Carnifex Demon | minus | indestructible, ordinary |
| Chain Reaction | damage | ordinary |
| Midnight Banshee | minus | indestructible, ordinary |
| Soul Snuffers | minus | indestructible, ordinary |
| Village Pillagers | asymmetric, damage | ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Puppeteer Clique | persist/undying | unclear | damage, destroy, sacrifice |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Aberrant Return | battlefield | any creature | one-shot |
| Dread Tiller | battlefield | any card of a type | repeatable |
| Grave Venerations | hand | any creature | repeatable |
| Liliana, Death Wielder | battlefield | any creature | one-shot |
| Persist | battlefield | any creature | one-shot |
| Puca's Covenant | hand | any creature | repeatable |
| Puppeteer Clique | battlefield | any creature | one-shot |
| Puppeteer Clique | battlefield | self only | repeatable |
| The Scorpion God | hand | any creature | repeatable |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 6/0/9 |  |
| counters | 13.1% | redundant | 3/3 | yes |
| artifact_tokens | 0.0% | fragment | 2/0 |  |
| lifegain | 0.0% | fragment | 2/0 |  |
| blink | 0.0% | fragment | 0/15 |  |
| landfall | 5.0% | package | 3/1 | yes |
| spellslinger | 0.0% | fragment | 18/0 |  |
| graveyard | 7.3% | package | 1/5 | yes |
| go_wide | 15.5% | package | 6/2 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Aberrant Return | additional or multiplied effect; unparsed text | recursion |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Archfiend of Ifnir | keyworded mechanic: cycling; repeatable trigger (cadence not priced) | spot_removal |
| Assassin's Trophy | unparsed text |  |
| Auntie Ool, Cursewretch | repeatable trigger (cadence not priced); unparsed text | closer |
| Binding the Old Gods | unparsed text | fixing |
| Black Sun's Zenith | X-scaled magnitude; unparsed text | recursion |
| Blowfly Infestation | repeatable trigger (cadence not priced) | spot_removal |
| Burning Curiosity | replacement or prevention effect; unparsed text |  |
| Carnifex Demon | activated ability (repeatable, not priced); unparsed text |  |
| Cathartic Pyre | unparsed text |  |
| Chain Reaction | X-scaled magnitude |  |
| Channeler Initiate | activated ability (repeatable, not priced) |  |
| Chimil, the Inner Sun | repeatable trigger (cadence not priced); uncounterable |  |
| Commander's Sphere | activated ability (repeatable, not priced) |  |
| Contagion Clasp | activated ability (repeatable, not priced) |  |
| Devoted Druid | activated ability (repeatable, not priced); unparsed text |  |
| Dread Tiller | repeatable trigger (cadence not priced) |  |
| Dusk Urchins | repeatable trigger (cadence not priced) | death_payoff |
| Eventide's Shadow | unparsed text | draw |
| Everlasting Torment | unparsed text |  |
| Evolution Sage | repeatable trigger (cadence not priced) |  |
| Ferrafor, Young Yew | activated ability (repeatable, not priced) | counter_multiplier |
| Fire Covenant | X-scaled magnitude | wipe |
| Flourishing Defenses | repeatable trigger (cadence not priced) |  |
| Glissa Sunslayer | repeatable trigger (cadence not priced); unparsed text |  |
| Grave Titan | repeatable trigger (cadence not priced) |  |
| Grave Venerations | repeatable trigger (cadence not priced) |  |
| Grim Poppet | unparsed text | spot_removal |
| Hapatra, Vizier of Poisons | repeatable trigger (cadence not priced) |  |
| Hoarder's Greed | unparsed text |  |
| Ignoble Hierarch | activated ability (repeatable, not priced); unparsed text | fixing |
| Incremental Blight | unparsed text | spot_removal |
| Infernal Grasp | unparsed text |  |
| Kulrath Knight | unparsed text |  |
| Lasting Tarfire | repeatable trigger (cadence not priced) |  |
| Liliana, Death Wielder | unparsed text |  |
| Massacre Girl, Known Killer | repeatable trigger (cadence not priced); unparsed text |  |
| Midnight Banshee | repeatable trigger (cadence not priced); unparsed text |  |
| Necroskitter | repeatable trigger (cadence not priced); unparsed text | recursion |
| Oft-Nabbed Goat | activated ability (repeatable, not priced); unparsed text | closer, death_payoff |
| Painful Truths | X-scaled magnitude |  |
| Puca's Covenant | repeatable trigger (cadence not priced); unparsed text |  |
| Puppeteer Clique | repeatable trigger (cadence not priced); unparsed text |  |
| Putrefy | unparsed text |  |
| Sinister Gnarlbark | repeatable trigger (cadence not priced) |  |
| Skinrender |  | spot_removal |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Terminate | unparsed text |  |
| The Reaper, King No More | repeatable trigger (cadence not priced); unparsed text | spot_removal |
| The Scorpion God | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) | recursion |
| Tree of Perdition | activated ability (repeatable, not priced) | closer |
| Village Pillagers | repeatable trigger (cadence not priced); unparsed text | ramp |
| Vraska, Betrayal's Sting | activated ability (repeatable, not priced); unparsed text | spot_removal |
| Wickerbough Elder | activated ability (repeatable, not priced); unparsed text |  |
| Wickersmith's Tools | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced) | sac_outlet |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 2; cards: Village Pillagers, Wickersmith's Tools |
| parallel producers | event: creature token enters; independent sources: 2; cards: Grave Titan, Wickersmith's Tools |
| linear payoff | Dusk Urchins: dies -> cards (fed by 0 cards) |
| linear payoff | Evolution Sage: landfall -> counters (fed by land drops) |
| linear payoff | Grave Venerations: end_step -> recursion (fed by each turn) |
| linear payoff | Grave Venerations: dies -> damage to each opponent (fed by 0 cards) |
| linear payoff | Lasting Tarfire: end_step -> damage to each opponent (fed by each turn) |
| linear payoff | Massacre Girl, Known Killer: dies -> cards (fed by 0 cards) |
| linear payoff | Sinister Gnarlbark: end_step -> cards (fed by each turn) |
| linear payoff | Village Pillagers: enter -> removal (fed by 1 cards) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.24 | 0.6 | 1.21 | 1.85 | 2.49 | 3.13 |
| can attack | 0.24 | 0.6 | 1.21 | 1.85 | 2.49 | 3.13 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.09 | 0.43 | 0.97 | 1.64 | 2.21 | 2.8 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.42 | 0.69 | 0.77 | 0.77 | 0.93 | 1.07 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.86 | 3.86 | 3.68 | 3.26 | 2.74 | 2.2 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 89% | 0% | 14% | 40% | spells waiting for mana |
| T4 | 0% | 94% | 0% | 16% | 63% | spells waiting for mana |
| T5 | 0% | 91% | 0% | 22% | 61% | spells waiting for mana |
| T6 | 0% | 88% | 0% | 19% | 62% | spells waiting for mana |
| T7 | 0% | 80% | 0% | 27% | 72% | spells waiting for mana |
| T8 | 0% | 72% | 0% | 30% | 74% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 0 | 0.0 | 13.3 | +0.0 (SE 0.0) |
| station_first | 0 | 0.0 | 13.3 | +0.0 (SE 0.0) |
| mana_first | 0 | 0.0 | 13.3 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 21.0% / 80.3% |
| light blockers: lethal by T10 | 0.0% |
| light blockers: median damage by T8 / T10 | 0 / 0 |
| tokens per turn T4-T8 (mean) | 0.04 |
| cards drawn by T8 (mean, incl. normal draws) | 10.5 |
| board at end of T8 (median bodies / power) | 4 / 12 |
| power per body at end of T8 (median) | 3.20 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 9 | -1.4 (SE 0.2) |
| exile wipe after T6 | 7 -> 9 | -1.6 (SE 0.2) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.52 | -1.3 (SE 0.2) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 4; commander casts T7-T10 1.92 | -1.4 (SE 0.2) |
| no commander (ablation) | tokens per turn T4-T8: 0.04 -> 0.05 | +0.5 (SE 0.2) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Aberrant Return | put one two or three target creature cards from graveyards onto the battlefield under your control each of them enters with an additional 1/ 1 counter on it |
| Archfiend of Ifnir | whenever you cycle or discard another card, put a -1/-1 counter on each creature your opponents control.; cycling {2} |
| Assassin's Trophy | its controller may search their library for a basic land card put it onto the battlefield then shuffle |
| Auntie Ool, Cursewretch | ward—blight 2.; whenever one or more -1/-1 counters are put on a creature, draw a card if you control that creature. if you don't control it, its controller los |
| Binding the Old Gods | i — destroy target nonland permanent an opponent controls.; ii — search your library for a forest card, put it onto the battlefield tapped, then shuffle.; iii — |
| Black Sun's Zenith | put x 1/ 1 counters on each creature shuffle ~ into its owner's library |
| Blowfly Infestation | if it had a 1/ 1 counter on it put a 1/ 1 counter on target creature |
| Burning Curiosity | exile the top two cards of your library if this spell's additional cost was paid exile the top three cards instead until the end of your next turn you may play  |
| Carnifex Demon | this creature enters with two -1/-1 counters on it.; put a 1/ 1 counter on each other creature |
| Cathartic Pyre | choose one —; • discard up to two cards then draw that many cards |
| Chain Reaction | ~ deals x damage to each creature where x is the number of creatures on the battlefield |
| Channeler Initiate | put three 1/ 1 counters on target creature you control |
| Chimil, the Inner Sun | spells you control can't be countered.; discover 5 |
| Contagion Clasp | put a 1/ 1 counter on target creature |
| Devoted Druid | put a -1/-1 counter on this creature: untap this creature. |
| Dread Tiller | put a 1/ 1 counter on target creature; whenever a creature with a -1/-1 counter on it dies, you may put a land card from your hand or graveyard onto the battlef |
| Dusk Urchins | or blocks put a 1/ 1 counter on it; for each 1/ 1 counter on it |
| Eventide's Shadow | remove any number of counters from among permanents on the battlefield you draw cards and lose life equal to the number of counters removed this way |
| Everlasting Torment | players can't gain life.; damage can't be prevented.; all damage is dealt as though its source had wither. |
| Ferrafor, Young Yew | create a number of 1/1 green saproling creature tokens equal to the number of counters among creatures target player controls; double the number of each kind of |
| Fire Covenant | ~ deals x damage divided as you choose among any number of target creatures |
| Flourishing Defenses | whenever a -1/-1 counter is put on a creature, you may create a 1/1 green elf warrior creature token. |
| Glissa Sunslayer | choose one; • you draw a card and lose 1 life.; • destroy target enchantment.; • remove up to three counters from target permanent. |
| Grave Titan | or attacks |
| Grave Venerations | you become the monarch; if you're the monarch |
| Grim Poppet | this creature enters with three -1/-1 counters on it.; remove a -1/-1 counter from this creature: put a -1/-1 counter on another target creature. |
| Hapatra, Vizier of Poisons | put a 1/ 1 counter on target creature; whenever you put one or more -1/-1 counters on a creature, create a 1/1 green snake creature token with deathtouch. |
| Hoarder's Greed | you lose 2 life and then clash with an opponent if you win repeat this process |
| Ignoble Hierarch | exalted; {r} or {g} |
| Incremental Blight | put a 1/ 1 counter on target creature two 1/ 1 counters on another target creature and three 1/ 1 counters on a third target creature |
| Infernal Grasp | you lose 2 life |
| Kulrath Knight | creatures your opponents control with counters on them can't attack or block. |
| Lasting Tarfire | if you put a counter on a creature this turn this enchantment |
| Liliana, Death Wielder | [+2]: put a -1/-1 counter on up to one target creature.; [−3]: destroy target creature with a -1/-1 counter on it.; [−10]: return all creature cards from your g |
| Massacre Girl, Known Killer | creatures you control have wither.; if its toughness was less than 1 |
| Midnight Banshee | put a 1/ 1 counter on each nonblack creature |
| Necroskitter | whenever a creature an opponent controls with a -1/-1 counter on it dies, you may return that card to the battlefield under your control. |
| Night's Whisper | you and lose 2 life |
| Oft-Nabbed Goat | gain control of and put a 1/ 1 counter on it only your opponents may activate this ability and only as a sorcery; if it had one or more 1/ 1 counters on it its  |
| Painful Truths | converge you and lose x life where x is the number of colors of mana spent to cast this spell |

## Uncertainty

- 56 of 61 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 6 of 61 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
