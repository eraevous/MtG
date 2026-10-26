# Deck: TMNT

- Leonardo, the Balance + Splinter, the Mentor (WUBRG), 100 cards
- Lands 39, nonland 59 (creatures 40), average nonland mana value 2.92
- Mana (goldfish, on the draw): 4 by T4 82.8%, all colors by T5 42.5%, commander out by T4 37.6% / T6 85.2%
- Weakest areas (seen by T7 vs target): wipe 14.3% (1 cards), protection:anti_wipe 14.3% (1 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 13; unopposed goldfish lethal by T10 96.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 10 before, 7 three turns later
- Without the commander: damage by T10 -8.6 (paired); typed coverage 12 of 61 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 1 | 0 to 10 | 6 of 13 |
| tap claimants per creature card | 0.02 | 0.0 to 0.62 | 11 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 5 | 0 to 5 | 1 of 13 |
| creature cards | 42 | 16 to 44 | 12 of 13 |
| creatures with power 4+ | 4 | 2 to 12 | 2 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | tap creatures | 1 | per use |
| Gilded Goose | sacrifice artifacts | 1 | per use |
| Gyome, Master Chef | sacrifice artifacts | 1 | per use |
| Improvised Club | sacrifice artifacts | 1 | per use |
| Ragost, Deft Gastronaut | sacrifice artifacts | 1 | per use |
| Tempestra, Dame of Games | sacrifice artifacts | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Leonardo, the Balance | no | - | - | 0 | Flock Impostor, Gyome, Master Chef, Personify |
| Splinter, the Mentor | no | artifact | - | 16 | Flock Impostor, Gyome, Master Chef, Personify |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 4 |
| 2 | 16 |
| 3 | 23 |
| 4 | 13 |
| 5 | 3 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 12 | 10 | Strong |
| fixing | 31 | 24 | Strong |
| draw | 11 | 10 | Strong |
| spot_removal | 8 | 8 | Strong |
| wipe | 1 | 2 | Adequate |
| counterspell | 1 | None | not scored |
| protection | 6 | 5 | Strong |
| recursion | 4 | 3 | Strong |
| closer | 9 | 4 | Excessive |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 12 | 74.7% | 81.2% | 86.1% | 91.3% | 86.1% |
| draw | 11 | 71.4% | 78.2% | 83.4% | 89.2% | 88.3% |
| spot_removal | 8 | 59.2% | 66.3% | 72.3% | 79.6% | 72.3% |
| wipe | 1 | 10.2% | 12.2% | 14.3% | 17.3% | 14.3% |
| protection | 6 | 48.5% | 55.3% | 61.4% | 69.2% | 61.4% |
| recursion | 4 | 35.4% | 41.2% | 46.6% | 53.9% | 46.6% |
| closer | 8 | 59.2% | 66.3% | 72.3% | 79.6% | 72.3% |
| protection:team | 2 | 19.5% | 23.1% | 26.7% | 31.8% | 26.7% |
| protection:anti_wipe | 1 | 10.2% | 12.2% | 14.3% | 17.3% | 14.3% |
| counterspell | 1 | 10.2% | 12.2% | 14.3% | 17.3% | 14.3% |
| fixing | 10 | 67.8% | 74.7% | 80.3% | 86.6% | 99.8% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| wipe | 1 | 2 | 14.3% | 26.7% | 12.4 |
| protection:anti_wipe | 1 | 2 | 14.3% | 26.7% | 12.4 |
| spot_removal | 8 | 8 | 72.3% | 72.3% | -0.0 |
| draw | 11 | 10 | 83.4% | 80.3% | -3.1 |
| ramp | 12 | 10 | 86.1% | 80.3% | -5.8 |
| protection | 6 | 5 | 61.4% | 54.5% | -6.8 |
| recursion | 4 | 3 | 46.6% | 37.4% | -9.2 |
| closer | 8 | 4 | 72.3% | 46.6% | -25.7 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Wave Goodbye | asymmetric, bounce | indestructible, big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Biosynthic Burst | indestructible | unclear | damage, destroy |
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | persist/undying | other_creatures | damage, destroy, sacrifice |
| Flock Impostor | blink/bounce own | single_target | damage, destroy, exile, minus, sacrifice |
| Gyome, Master Chef | indestructible | single_target | damage, destroy |
| Murderous Redcap | persist/undying | unclear | damage, destroy, sacrifice |
| Personify | blink/bounce own | single_target | damage, destroy, exile, minus, sacrifice |
| Tam, Mindful First-Year | hexproof | other_creatures | - |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | battlefield | self only | repeatable |
| Murderous Redcap | battlefield | self only | repeatable |
| Reaping Willow | battlefield | any creature | repeatable |
| Scout for Survivors | battlefield | any creature | one-shot |
| Zoraline, Cosmos Caller | battlefield | any card of a type | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 61.4% | package | 17/6/2 | yes |
| counters | 80.3% | redundant | 22/10 | yes |
| artifact_tokens | 67.3% | redundant | 15/7 | yes |
| lifegain | 26.7% | package | 14/2 | yes |
| blink | 12.4% | package | 1/13 | yes |
| landfall | 0.0% | fragment | 2/0 |  |
| spellslinger | 0.0% | fragment | 12/0 |  |
| graveyard | 6.3% | package | 1/4 | yes |
| go_wide | 100.0% | redundant | 17/12 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Abundant Growth | activated ability (repeatable, not priced); unparsed text | ramp |
| Ambitious Augmenter | keyworded mechanic: increment | death_payoff, token_maker |
| April O'Neil, Live on the Scene | repeatable trigger (cadence not priced); unparsed text | token_maker |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Assassin's Trophy | unparsed text |  |
| Baxter, Fly in the Ointment | repeatable trigger (cadence not priced) | draw, wipe |
| Bebop, Skull & Crossbones | X-scaled magnitude; repeatable trigger (cadence not priced); unparsed text |  |
| Berta, Wise Extrapolator | X-scaled magnitude; activated ability (repeatable, not priced); keyworded mechanic: increment; repeatable trigger (cadence not priced) |  |
| Big Mother Mouser | repeatable trigger (cadence not priced) | death_payoff |
| Biosynthic Burst | unparsed text |  |
| Casey Jones, Back Alley Brute | repeatable trigger (cadence not priced) |  |
| Corpsejack Menace | replacement or prevention effect |  |
| Devoted Druid | activated ability (repeatable, not priced); unparsed text |  |
| Dimension X Pizzasaur | activated ability (repeatable, not priced) |  |
| Donatello, the Brains | replacement or prevention effect; unparsed text | counter_source, token_maker |
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | repeatable trigger (cadence not priced); unparsed text | death_payoff |
| Endurance | keyworded mechanic: evoke |  |
| Flock Impostor | unparsed text |  |
| Genghis Frog | repeatable trigger (cadence not priced) |  |
| Gilded Goose | activated ability (repeatable, not priced) |  |
| Glen Elendra Guardian | activated ability (repeatable, not priced); unparsed text | draw |
| Gyome, Master Chef | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Haliya, Guided by Light | repeatable trigger (cadence not priced); unparsed text | recursion |
| Heaped Harvest | activated ability (repeatable, not priced) |  |
| Heroes in a Half Shell | repeatable trigger (cadence not priced) |  |
| High Score | repeatable trigger (cadence not priced); replacement or prevention effect |  |
| Improvised Club |  | closer |
| Irma, Part-Time Mutant | animation; copy effect; repeatable trigger (cadence not priced) |  |
| Leonardo, the Balance | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text | wipe |
| Lita, Little Orphan Amphibian | keyworded mechanic: alliance; repeatable trigger (cadence not priced); unparsed text | token_maker |
| Michelangelo, Weirdness to 11 | replacement or prevention effect |  |
| Mighty Mutanimals | keyworded mechanic: alliance; repeatable trigger (cadence not priced) |  |
| Mirkwood Bats | repeatable trigger (cadence not priced) |  |
| Mona Lisa, Science Geek | X-scaled magnitude; activated ability (repeatable, not priced) |  |
| Murderous Redcap |  | death_payoff, recursion |
| Mutant Chain Reaction |  | counter_source, sac_outlet |
| Ninja Pizza | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Noggle Robber |  | death_payoff |
| Peregrin Took | additional or multiplied effect; replacement or prevention effect | lifegain_source |
| Ragost, Deft Gastronaut | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Ray Fillet, Wave Warrior | repeatable trigger (cadence not priced) |  |
| Reaping Willow | activated ability (repeatable, not priced); unparsed text |  |
| Return of the Wildspeaker | unparsed text |  |
| Rocksteady, Mutant Marauder | repeatable trigger (cadence not priced); unparsed text |  |
| Rosie Cotton of South Lane | repeatable trigger (cadence not priced) |  |
| Selvala, Heart of the Wilds | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Shimmerwilds Growth | additional or multiplied effect; repeatable trigger (cadence not priced); unparsed text |  |
| Shredder's Technique | keyworded mechanic: sneak; unparsed text |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Splinter, the Mentor | repeatable trigger (cadence not priced); unparsed text | counter_source |
| Tam, Mindful First-Year | activated ability (repeatable, not priced) |  |
| Tempestra, Dame of Games | activated ability (repeatable, not priced); copy effect; repeatable trigger (cadence not priced); unparsed text |  |
| Terrasymbiosis | repeatable trigger (cadence not priced); unparsed text |  |
| The Last Ronin's Technique | keyworded mechanic: sneak |  |
| Tokka & Rahzar, Unsupervised | repeatable trigger (cadence not priced); unparsed text | token_maker |
| Wave Goodbye |  | counter_source |
| Zoraline, Cosmos Caller | repeatable trigger (cadence not priced) | spot_removal |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 5; cards: Crustacean Commando, Genghis Frog, Gilded Goose, Michelangelo, Weirdness to 11, Noggle Robber |
| parallel producers | event: creature token enters; independent sources: 3; cards: Ambitious Augmenter, Berta, Wise Extrapolator, Mighty Mutanimals |
| replacement amplification | amplifier: Peregrin Took; adds per event: 1 extra token; events it sees (sources): 9 |
| linear payoff | Flock Impostor: enter -> interaction (fed by 1 cards) |
| linear payoff | Haliya, Guided by Light: enter -> life (fed by 49 cards) |
| linear payoff | Mirkwood Bats: create -> damage to each opponent (fed by 13 cards) |
| feed-forward chain | Ambitious Augmenter: dies -> Leonardo, the Balance: enter -> Casey Jones, Back Alley Brute: counters |
| feed-forward chain | Ambitious Augmenter: dies -> Leonardo, the Balance: enter -> Terrasymbiosis: counters |
| feed-forward chain | Ambitious Augmenter: dies -> Mighty Mutanimals: enter -> Casey Jones, Back Alley Brute: counters |
| feed-forward chain | Ambitious Augmenter: dies -> Mighty Mutanimals: enter -> Terrasymbiosis: counters |
| feed-forward chain | Ambitious Augmenter: dies -> Peregrin Took: replacement -> Haliya, Guided by Light: enter |
| feed-forward chain | Ambitious Augmenter: dies -> Peregrin Took: replacement -> Leonardo, the Balance: enter -> Casey Jones, Back Alley Brute: counters |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.83 | 1.67 | 2.57 | 3.65 | 4.6 | 5.03 |
| can attack | 0.83 | 1.67 | 2.57 | 3.65 | 4.6 | 5.03 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.67 | 1.55 | 2.38 | 3.5 | 4.31 | 4.64 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.97 | 1.12 | 1.35 | 1.28 | 1.68 | 1.77 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.62 | 3.5 | 3.12 | 2.55 | 1.97 | 1.89 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 86% | 0% | 16% | 80% | spells waiting for mana |
| T4 | 0% | 88% | 0% | 12% | 89% | spells waiting for mana |
| T5 | 0% | 79% | 0% | 18% | 91% | spells waiting for mana |
| T6 | 0% | 62% | 0% | 16% | 82% | spells waiting for mana |
| T7 | 0% | 53% | 0% | 26% | 92% | spells waiting for mana |
| T8 | 0% | 48% | 0% | 30% | 92% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 13 | 0.0 | 12.7 | +0.0 (SE 0.0) |
| station_first | 13 | 0.0 | 12.7 | +0.0 (SE 0.0) |
| mana_first | 13 | 0.0 | 12.7 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 71.0% / 96.0% |
| light blockers: lethal by T10 | 4.7% |
| light blockers: median damage by T8 / T10 | 10 / 13 |
| tokens per turn T4-T8 (mean) | 0.28 |
| cards drawn by T8 (mean, incl. normal draws) | 9.5 |
| board at end of T8 (median bodies / power) | 6 / 14 |
| power per body at end of T8 (median) | 2.50 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 10 -> 7 | -7.9 (SE 0.6) |
| exile wipe after T6 | 10 -> 7 | -7.9 (SE 0.6) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 5.23 | -9.4 (SE 0.6) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 10 -> 3; commander casts T7-T10 3.40 | -8.6 (SE 0.6) |
| no commander (ablation) | tokens per turn T4-T8: 0.28 -> 0.31 | -8.6 (SE 0.5) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Abundant Growth | enchant land; when this aura enters, draw a card.; enchanted land has "{t}: add one mana of any color." |
| Ambitious Augmenter | increment; if it had one or more counters on it then put 's counters on that token |
| April O'Neil, Live on the Scene | whenever a mutant, ninja, or turtle you control enters, investigate.; partner—character select |
| Assassin's Trophy | its controller may search their library for a basic land card put it onto the battlefield then shuffle |
| Baxter, Fly in the Ointment | or attacks each creature you control with a counter on it gains flying until end of turn |
| Bebop, Skull & Crossbones | partner with rocksteady, mutant marauder; where x is the number of counters on ~ if you do you lose x life |
| Berta, Wise Extrapolator | increment; whenever one or more +1/+1 counters are put on ~, add one mana of any color.; put x +1/+1 counters on it |
| Big Mother Mouser | this creature enters with two +1/+1 counters on it.; double the number of +1/+1 counters on it; create a number of 1/1 colorless robot artifact creature tokens  |
| Biosynthic Burst | it gains reach trample and indestructible until end of turn untap it |
| Casey Jones, Back Alley Brute | ~ deals that much damage to target opponent |
| Corpsejack Menace | if one or more +1/+1 counters would be put on a creature you control, twice that many +1/+1 counters are put on it instead. |
| Devoted Druid | put a -1/-1 counter on this creature: untap this creature. |
| Dimension X Pizzasaur | when you do |
| Donatello, the Brains | if one or more tokens would be created under your control, those tokens plus a mutagen token are created instead.; partner—character select |
| Eirdu, Carrier of Dawn // Isilu, Carrier of Twilight | ~ {3}{w}{w}; creature spells you cast have convoke.; pay {b} if you do transform ~; isilu, carrier of twilight; each other nontoken creature you control has per |
| Endurance | up to one target player puts all the cards from their graveyard on the bottom of their library in a random order; evoke—exile a green card from your hand. |
| Glen Elendra Guardian | this creature enters with a -1/-1 counter on it.; its controller |
| Gyome, Master Chef | create a number of food tokens equal to the number of nontoken creatures you had enter the battlefield under your control this turn; target creature gains indes |
| Haliya, Guided by Light | if you've gained 3 or more life this turn; warp {w} |
| Heaped Harvest | search your library for a basic land card put it onto the battlefield tapped then shuffle |
| Heroes in a Half Shell | whenever one or more mutants, ninjas, and/or turtles you control deal combat damage to a player, put a +1/+1 counter on each of those creatures and draw a card. |
| High Score | if one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead.; if you control a creature with t |
| Irma, Part-Time Mutant | ~ becomes a copy of up to one other target creature you control except her name is ~ and she has this ability then |
| Leonardo, the Balance | do this only once each turn; creatures you control gain menace trample and lifelink until end of turn; partner—character select |
| Lita, Little Orphan Amphibian | choose one that hasn't been chosen this turn; • put a +1/+1 counter on ~.; • create a food token.; • scry 1. |
| Michelangelo, Weirdness to 11 | if one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead. |
| Mona Lisa, Science Geek | add x mana of any one color where x is ~'s power |
| Murderous Redcap | it deals damage equal to its power to any target; persist |
| Ninja Pizza | foods you control have "{t}, sacrifice this artifact: add one mana of any color."; at the beginning of your second main phase, create a food token. |
| Noggle Robber | or dies |
| Ragost, Deft Gastronaut | artifacts you control are foods in addition to their other types and have "{2}, {t}, sacrifice this artifact: you gain 3 life."; if you gained life this turn un |
| Ray Fillet, Wave Warrior | evolve |
| Reaping Willow | this creature enters with two -1/-1 counters on it.; return target creature card with mana value 3 or less from your graveyard to the battlefield |
| Return of the Wildspeaker | choose one —; • draw cards equal to the greatest power among non human creatures you control; • non human |
| Rocksteady, Mutant Marauder | partner with bebop, skull & crossbones |
| Rosie Cotton of South Lane | when rosie cotton enters, create a food token. |
| Scout for Survivors | return up to three target creature cards with total mana value 3 or less from your graveyard to the battlefield |
| Selvala, Heart of the Wilds | its controller may if its power is greater than each other creature's power; add x mana in any combination of colors where x is the greatest power among creatur |
| Shimmerwilds Growth | enchant land; as this aura enters, choose a color.; enchanted land is the chosen color.; whenever enchanted land is tapped for mana, its controller adds an addi |
| Shredder's Technique | sneak {b}; if an enchantment was destroyed this way you lose 2 life |

## Uncertainty

- 57 of 61 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 12 of 61 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
