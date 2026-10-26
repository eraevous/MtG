# Deck: Sharuum

- Sharuum the Hegemon (WUB), 100 cards
- Lands 37, nonland 62 (creatures 24), average nonland mana value 3.24
- Mana (goldfish, on the draw): 4 by T4 67.7%, all colors by T5 90.0%, commander out by T4 2.8% / T6 56.0%
- Weakest areas (seen by T7 vs target): protection 0.0% (0 cards), protection:anti_wipe 0.0% (0 cards), spot_removal 54.1% (5 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 12; unopposed goldfish lethal by T10 73.3% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 9 three turns later
- Without the commander: damage by T10 -7.9 (paired); typed coverage 20 of 63 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 5 | 0 to 10 | 3 of 13 |
| tap claimants per creature card | 0.2 | 0.0 to 0.62 | 3 of 13 |
| station power needed | 17 | 0 to 30 | 2 of 13 |
| artifact-sacrifice claimants | 3 | 0 to 5 | 2 of 13 |
| creature cards | 25 | 16 to 44 | 3 of 13 |
| creatures with power 4+ | 7 | 2 to 12 | 9 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Disruptor of Currents | tap creatures | 1 | per use |
| Etherium Astrolabe | sacrifice artifacts | 1 | per use |
| Guidelight Pathmaker | crew | 2 | per use |
| Hulldrifter | crew | 3 | per use |
| Repurposing Bay | sacrifice artifacts | 1 | per use |
| Rescue Skiff | station | 10 | one-time |
| Selfcraft Mechan | sacrifice artifacts | 1 | per use |
| Susurian Dirgecraft | station | 7 | one-time |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Sharuum the Hegemon | no | - | - | 0 | none |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 8 |
| 2 | 16 |
| 3 | 13 |
| 4 | 13 |
| 5 | 7 |
| 6 | 2 |
| 7+ | 3 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 13 | 10 | Strong |
| fixing | 23 | 12 | Excessive |
| draw | 18 | 10 | Excessive |
| spot_removal | 5 | 8 | Adequate |
| wipe | 2 | 2 | Strong |
| counterspell | 1 | None | not scored |
| protection | 0 | 5 | Absent |
| recursion | 9 | 3 | Excessive |
| closer | 4 | 4 | Strong |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 13 | 77.3% | 83.5% | 88.1% | 92.8% | 90.0% |
| draw | 18 | 87.9% | 92.3% | 95.2% | 97.7% | 95.2% |
| spot_removal | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 61.0% |
| wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 37.0% |
| protection | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| recursion | 8 | 58.8% | 65.9% | 71.9% | 79.2% | 76.2% |
| closer | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 66.8% |
| counterspell | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| fixing | 9 | 63.3% | 70.4% | 76.2% | 83.1% | 99.0% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 0 | 5 | 0.0% | 54.1% | 54.1 |
| protection:anti_wipe | 0 | 2 | 0.0% | 26.4% | 26.4 |
| spot_removal | 5 | 8 | 54.1% | 71.9% | 17.8 |
| wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| closer | 4 | 4 | 46.2% | 46.2% | 0.0 |
| ramp | 13 | 10 | 88.1% | 79.9% | -8.1 |
| draw | 18 | 10 | 95.2% | 79.9% | -15.3 |
| recursion | 8 | 3 | 71.9% | 37.0% | -34.9 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Shatter the Sky | destroy | big_toughness, ordinary |
| Vanquish the Horde | destroy | big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Illvoi Light Jammer | hexproof | unclear | - |
| Nutrient Block | indestructible | unclear | damage, destroy |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Astelli Reclaimer | battlefield | any card of a type | one-shot |
| Does Machines | hand | any card of a type | one-shot |
| Fix What's Broken | battlefield | any creature | one-shot |
| Junk Diver | hand | any card of a type | one-shot |
| Rescue Skiff | battlefield | any card of a type | one-shot |
| Sanctum Gargoyle | hand | any card of a type | one-shot |
| Scour for Scrap | hand | any card of a type | one-shot |
| Zoraline, Cosmos Caller | battlefield | any card of a type | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 6.8% | package | 7/3/2 | yes |
| counters | 0.0% | fragment | 3/0 |  |
| artifact_tokens | 41.1% | redundant | 7/5 | yes |
| lifegain | 0.0% | fragment | 11/0 |  |
| blink | 13.8% | package | 1/23 | yes |
| landfall | 0.0% | fragment | 3/0 |  |
| spellslinger | 0.0% | fragment | 8/0 |  |
| graveyard | 37.0% | redundant | 3/9 | yes |
| go_wide | 30.0% | redundant | 7/4 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Al Bhed Salvagers | repeatable trigger (cadence not priced) |  |
| Anchovy & Banana Pizza | activated ability (repeatable, not priced) |  |
| Astelli Reclaimer | X-scaled magnitude; unparsed text |  |
| Azorius Signet | activated ability (repeatable, not priced) | fixing |
| Bender's Waterskin | activated ability (repeatable, not priced); unparsed text |  |
| Bespoke Bō | unparsed text |  |
| Blitzball | activated ability (repeatable, not priced); unparsed text |  |
| Buzz Bots |  | death_payoff |
| Cavern Harpy | unparsed text |  |
| Chromatic Lantern | activated ability (repeatable, not priced) |  |
| Chromatic Star | activated ability (repeatable, not priced) |  |
| Coin of Mastery | activated ability (repeatable, not priced); additional or multiplied effect | fixing, wipe |
| Coldsteel Heart | activated ability (repeatable, not priced); unparsed text |  |
| Conjurer's Bauble | activated ability (repeatable, not priced) |  |
| Cryogen Relic | activated ability (repeatable, not priced) |  |
| Disruptor of Currents | unparsed text |  |
| Divert Disaster |  | ramp |
| Does Machines | activated ability (repeatable, not priced); animation; repeatable trigger (cadence not priced) |  |
| Don & Leo, Problem Solvers | repeatable trigger (cadence not priced); unparsed text | blink |
| Esperzoa | repeatable trigger (cadence not priced) | closer |
| Etherium Astrolabe | activated ability (repeatable, not priced) |  |
| Etherium Sculptor | cost reduction or free cast |  |
| Executioner's Capsule | activated ability (repeatable, not priced) |  |
| Firdoch Core | activated ability (repeatable, not priced); animation; unparsed text |  |
| Fix What's Broken | X-scaled magnitude |  |
| Gandalf the White | additional or multiplied effect; unparsed text |  |
| Gold Pan | unparsed text |  |
| Grim Bauble | activated ability (repeatable, not priced) |  |
| Guidelight Pathmaker | keyworded mechanic: crew; unparsed text |  |
| Hulldrifter | keyworded mechanic: crew |  |
| Hymn of the Faller | unparsed text |  |
| Illvoi Light Jammer | unparsed text | protection |
| Junk Diver |  | closer, death_payoff |
| Krang, Master Mind | unparsed text |  |
| Magister Sphinx |  | closer |
| Mechan Assembler | repeatable trigger (cadence not priced); unparsed text |  |
| Mirkwood Bats | repeatable trigger (cadence not priced) |  |
| Nesting Bot | unparsed text | death_payoff |
| Nutrient Block | activated ability (repeatable, not priced) | protection |
| Omni-Cheese Pizza | activated ability (repeatable, not priced) |  |
| Orzhov Signet | activated ability (repeatable, not priced) | fixing |
| Pactdoll Terror | repeatable trigger (cadence not priced) |  |
| Path to Exile | unparsed text |  |
| Prismatic Lens | activated ability (repeatable, not priced) |  |
| Puppet Conjurer | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Refurbished Familiar | unparsed text |  |
| Repurposing Bay | activated ability (repeatable, not priced); unparsed text |  |
| Rescue Skiff | keyworded mechanic: station; unparsed text |  |
| Scour for Scrap | unparsed text |  |
| Sewer-veillance Cam | activated ability (repeatable, not priced) |  |
| Skycoach Conductor // All Aboard | unparsed text | copy, spot_removal |
| Solemn Simulacrum |  | death_payoff |
| Susurian Dirgecraft | keyworded mechanic: station; unparsed text |  |
| Susurian Voidborn | repeatable trigger (cadence not priced); unparsed text | recursion |
| Thopter Foundry | activated ability (repeatable, not priced) |  |
| Twinning Glass | activated ability (repeatable, not priced); cost reduction or free cast |  |
| Unbender Tine | activated ability (repeatable, not priced) |  |
| Vanquish the Horde | cost reduction or free cast |  |
| Zoraline, Cosmos Caller | repeatable trigger (cadence not priced) | spot_removal |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 6; cards: Coin of Mastery, Gold Pan, Mechan Assembler, Nesting Bot, Puppet Conjurer, Thopter Foundry |
| parallel producers | event: creature token enters; independent sources: 4; cards: Mechan Assembler, Nesting Bot, Puppet Conjurer, Thopter Foundry |
| bounded feedback | cycle: Mechan Assembler: enter -> (itself); limit: once per turn: Mechan Assembler: enter |
| linear payoff | Anchovy & Banana Pizza: enter -> interaction (fed by 1 cards) |
| linear payoff | Bespoke Bō: enter -> interaction (fed by 1 cards) |
| linear payoff | Buzz Bots: dies -> cards (fed by 0 cards) |
| linear payoff | Cryogen Relic: leave -> cards (fed by 0 cards) |
| linear payoff | Cryogen Relic: enter -> cards (fed by 1 cards) |
| linear payoff | Disruptor of Currents: enter -> interaction (fed by 1 cards) |
| linear payoff | Does Machines: begin_combat -> power (fed by each turn) |
| linear payoff | Don & Leo, Problem Solvers: end_step -> interaction (fed by each turn) |
| linear payoff | Hulldrifter: enter -> cards (fed by 1 cards) |
| linear payoff | Mirkwood Bats: create -> damage to each opponent (fed by 7 cards) |
| linear payoff | Omni-Cheese Pizza: enter -> cards (fed by 1 cards) |
| linear payoff | Pactdoll Terror: enter -> damage to each opponent (fed by 46 cards) |
| linear payoff | Refurbished Familiar: enter -> cards (fed by 1 cards) |
| linear payoff | Rescue Skiff: enter -> recursion (fed by 1 cards) |
| feed-forward chain | Coin of Mastery: activated -> Mechan Assembler: enter -> Mirkwood Bats: create |
| feed-forward chain | Coin of Mastery: activated -> Mechan Assembler: enter -> Pactdoll Terror: enter |
| feed-forward chain | Nesting Bot: dies -> Mechan Assembler: enter -> Mirkwood Bats: create |
| feed-forward chain | Nesting Bot: dies -> Mechan Assembler: enter -> Pactdoll Terror: enter |
| feed-forward chain | Puppet Conjurer: activated -> Mechan Assembler: enter -> Mirkwood Bats: create |
| feed-forward chain | Puppet Conjurer: activated -> Mechan Assembler: enter -> Pactdoll Terror: enter |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.13 | 0.33 | 0.78 | 1.43 | 2.09 | 2.89 |
| can attack | 0.13 | 0.33 | 0.78 | 1.43 | 2.09 | 2.89 |
| with 2+ uses | 0.0 | 0.0 | 0.01 | 0.06 | 0.29 | 0.63 |
| attacked | 0.04 | 0.24 | 0.54 | 1.21 | 1.77 | 2.58 |
| could attack but spent before combat | 0 | 0 | 0.01 | 0.06 | 0.09 | 0.13 |
| tapped to station | 0 | 0 | 0.01 | 0.04 | 0.14 | 0.22 |
| tapped to crew | 0 | 0 | 0.01 | 0.1 | 0.18 | 0.27 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.31 | 0.66 | 1.03 | 1.11 | 1.28 | 1.28 |
| station charge still needed | 0.0 | 0.09 | 0.21 | 0.4 | 0.96 | 1.07 |
| spells waiting in hand | 4.06 | 3.63 | 3.43 | 3.12 | 2.66 | 2.03 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 91% | 0% | 9% | 28% | spells waiting for mana |
| T4 | 1% | 91% | 0% | 9% | 57% | spells waiting for mana |
| T5 | 3% | 90% | 0% | 23% | 75% | spells waiting for mana |
| T6 | 6% | 87% | 5% | 21% | 76% | spells waiting for mana |
| T7 | 14% | 80% | 7% | 29% | 73% | spells waiting for mana |
| T8 | 17% | 63% | 9% | 29% | 72% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 12 | 3.0 | 12.4 | +0.0 (SE 0.0) |
| station_first | 12 | 3.9 | 12.4 | +0.4 (SE 0.2) |
| mana_first | 12 | 3.0 | 12.4 | -0.1 (SE 0.1) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 12.3% / 73.3% |
| light blockers: lethal by T10 | 4.3% |
| light blockers: median damage by T8 / T10 | 5 / 12 |
| tokens per turn T4-T8 (mean) | 0.18 |
| cards drawn by T8 (mean, incl. normal draws) | 9.6 |
| board at end of T8 (median bodies / power) | 4 / 13 |
| power per body at end of T8 (median) | 3.25 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 9 | -8.2 (SE 0.5) |
| exile wipe after T6 | 7 -> 9 | -8.4 (SE 0.5) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 1.77 | -6.8 (SE 0.4) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 6; commander casts T7-T10 1.48 | -10.6 (SE 0.6) |
| no commander (ablation) | tokens per turn T4-T8: 0.18 -> 0.20 | -7.9 (SE 0.4) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Al Bhed Salvagers | whenever this creature or another creature or artifact you control dies, target opponent loses 1 life and you gain 1 life. |
| Astelli Reclaimer | return target noncreature nonland permanent card with mana value x or less from your graveyard to the battlefield where x is the amount of mana spent to cast; w |
| Bender's Waterskin | untap this artifact during each other player's untap step. |
| Bespoke Bō | equipped creature gets +2/+1 and has vigilance. |
| Blitzball | activate only if an opponent was dealt combat damage by a legendary creature this turn |
| Cavern Harpy | return a blue or black creature you control to its owner's hand; pay 1 life: return this creature to its owner's hand. |
| Chromatic Lantern | lands you control have "{t}: add one mana of any color." |
| Chromatic Star | when this artifact is put into a graveyard from the battlefield, draw a card. |
| Coin of Mastery | each creature you control enters with an additional +1/+1 counter on it for each mana from an artifact source spent to cast it. |
| Coldsteel Heart | this artifact enters tapped.; as this artifact enters, choose a color.; add one mana of the chosen color |
| Conjurer's Bauble | put up to one target card from your graveyard on the bottom of your library |
| Divert Disaster | if they do you |
| Does Machines | when this class enters, mill two cards, draw two cards, then discard two cards.; {1}{u}: level 2; when this class becomes level 2, return up to two target artif |
| Don & Leo, Problem Solvers | return them to the battlefield under their owners' control |
| Esperzoa | return an artifact you control to its owner's hand |
| Firdoch Core | becomes a 4/4 artifact creature until end of turn |
| Fix What's Broken | return each artifact and creature card with mana value x from your graveyard to the battlefield |
| Gandalf the White | you may cast legendary spells and artifact spells as though they had flash.; if a legendary permanent or an artifact entering or leaving the battlefield causes  |
| Gold Pan | equipped creature gets +1/+1. |
| Grim Bauble | target creature an opponent controls gets 2/ 2 until end of turn |
| Guidelight Pathmaker | search your library for an artifact card and reveal it put it onto the battlefield if its mana value is 2 or less otherwise put it into your hand if you search  |
| Hymn of the Faller | you and lose 1 life; void if a nonland permanent left the battlefield this turn or a spell was warped this turn draw another card |
| Illvoi Light Jammer | attach it to target creature you control that creature gains hexproof until end of turn; equipped creature gets +1/+2. |
| Junk Diver | return another target artifact card from your graveyard to your hand |
| Krang, Master Mind | affinity for artifacts; if you have fewer than four cards in hand draw cards equal to the difference; ~ gets +1/+0 for each other artifact you control. |
| Magister Sphinx | target player's life total becomes 10 |
| Nesting Bot | start your engines!; max speed — this creature gets +1/+0. |
| Nutrient Block | when this artifact is put into a graveyard from the battlefield, draw a card. |
| Path to Exile | its controller may search their library for a basic land card put that card onto the battlefield tapped then shuffle |
| Puppet Conjurer | sacrifice a homunculus |
| Refurbished Familiar | affinity for artifacts; each opponent discards a card for each opponent who can't you |
| Repurposing Bay | search your library for an artifact card with mana value equal to 1 plus the sacrificed artifact's mana value put that card onto the battlefield then shuffle |
| Scour for Scrap | choose one or both —; • search your library for an artifact card reveal it put it into your hand then shuffle |
| Selfcraft Mechan | sacrifice an artifact when you do |
| Shatter the Sky | each player who controls a creature with power 4 or greater then |
| Skycoach Conductor // All Aboard | ~ {2}{u}; this creature enters prepared.; all aboard {u}; exile target non-pilot creature you control, then return that card to the battlefield under its owner' |
| Solemn Simulacrum | search your library for a basic land card put that card onto the battlefield tapped then shuffle |
| Susurian Dirgecraft | each opponent sacrifices a nontoken creature of their choice |
| Susurian Voidborn | whenever this creature or another creature or artifact you control dies, target opponent loses 1 life and you gain 1 life.; warp {b} |
| Twinning Glass | cast a spell from your hand without paying its mana cost if it has the same name as a spell that was cast this turn |

## Uncertainty

- 59 of 63 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 20 of 63 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
