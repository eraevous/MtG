# Deck: Counter Blitz

- Tidus, Yuna's Guardian (WUG), 100 cards
- Lands 37, nonland 62 (creatures 34), average nonland mana value 3.03
- Mana (goldfish, on the draw): 4 by T4 70.4%, all colors by T5 85.4%, commander out by T4 65.3% / T6 89.4%
- Weakest areas (seen by T7 vs target): closer 0.0% (0 cards), recursion 14.1% (1 cards), protection 37.0% (3 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 3; unopposed goldfish lethal by T10 84.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 8 before, 7 three turns later
- Without the commander: damage by T10 -0.2 (paired); typed coverage 8 of 63 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 1 | 0 to 10 | 6 of 13 |
| tap claimants per creature card | 0.03 | 0.0 to 0.62 | 7 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 1 | 0 to 5 | 5 of 13 |
| creature cards | 35 | 16 to 44 | 9 of 13 |
| creatures with power 4+ | 6 | 2 to 12 | 8 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 3 | 0 to 4 | 2 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Collective Effort | tap creatures | 1 | per use |
| Tireless Tracker | sacrifice artifacts | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Tidus, Yuna's Guardian | no | - | - | 0 | Inspiring Call, Summon: Magus Sisters |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 0 | 2 |
| 1 | 5 |
| 2 | 17 |
| 3 | 16 |
| 4 | 13 |
| 5 | 6 |
| 6 | 2 |
| 7+ | 1 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 10 | 10 | Strong |
| fixing | 26 | 12 | Excessive |
| draw | 13 | 10 | Strong |
| spot_removal | 10 | 8 | Strong |
| wipe | 4 | 2 | Excessive |
| counterspell | 1 | None | not scored |
| protection | 3 | 5 | Adequate |
| recursion | 1 | 3 | Fragile |
| closer | 0 | 4 | Absent |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 83.1% |
| draw | 12 | 74.3% | 80.8% | 85.8% | 91.0% | 88.1% |
| spot_removal | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 83.1% |
| wipe | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 46.2% |
| protection | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 46.2% |
| recursion | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 26.4% |
| closer | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| counterspell | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 14.1% |
| fixing | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 99.7% |
| counter_preservation | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 54.1% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| closer | 0 | 4 | 0.0% | 46.2% | 46.2 |
| recursion | 1 | 3 | 14.1% | 37.0% | 22.9 |
| protection | 3 | 5 | 37.0% | 54.1% | 17.1 |
| protection:anti_wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| ramp | 10 | 10 | 79.9% | 79.9% | 0.0 |
| draw | 12 | 10 | 85.8% | 79.9% | -5.9 |
| spot_removal | 10 | 8 | 79.9% | 71.9% | -8.0 |
| wipe | 4 | 2 | 46.2% | 26.4% | -19.8 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Bane of Progress | destroy | big_toughness, ordinary |
| Damning Verdict | destroy | big_toughness, ordinary |
| Farewell | exile | indestructible, big_toughness, ordinary |
| Promise of Loyalty | sacrifice | indestructible, big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Inspiring Call | indestructible | creatures_with_counters | damage, destroy |
| Protection Magic | shield counter | up_to_three_targets | damage, destroy |
| Summon: Magus Sisters | shield counter | single_target | damage, destroy |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Luminous Broodmoth | battlefield | creature without flying | repeatable |
| Yuna's Decision | hand | any card of a type | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 5/0/4 |  |
| counters | 79.9% | redundant | 35/10 | yes |
| artifact_tokens | 14.1% | package | 3/1 | yes |
| lifegain | 0.0% | fragment | 4/0 |  |
| blink | 0.0% | fragment | 0/9 |  |
| landfall | 3.5% | package | 2/1 | yes |
| spellslinger | 0.0% | fragment | 15/0 |  |
| graveyard | 1.9% | package | 1/1 | yes |
| go_wide | 0.0% | fragment | 5/0 |  |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Altered Ego | X-scaled magnitude; additional or multiplied effect; copy effect; uncounterable | protection |
| An Offer You Can't Refuse | unparsed text | fixing, ramp, token_maker |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Auron, Venerated Guardian | repeatable trigger (cadence not priced) |  |
| Blitzball Stadium | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced) | closer |
| Bred for the Hunt | repeatable trigger (cadence not priced) |  |
| Chasm Skulker | X-scaled magnitude; repeatable trigger (cadence not priced) | death_payoff, draw |
| Chocobo Knights | repeatable trigger (cadence not priced) |  |
| Collective Effort | unparsed text |  |
| Destroy Evil | unparsed text |  |
| Endless Detour | unparsed text |  |
| Everflowing Chalice | activated ability (repeatable, not priced); unparsed text |  |
| Farewell | unparsed text |  |
| Farseek |  | fixing |
| Fathom Mage | repeatable trigger (cadence not priced) |  |
| Fight Rigging | cost reduction or free cast; keyworded mechanic: hideaway; repeatable trigger (cadence not priced) |  |
| Forgotten Ancient | counter movement or preservation; repeatable trigger (cadence not priced) |  |
| Gatta and Luzzu | replacement or prevention effect |  |
| Generous Patron | repeatable trigger (cadence not priced) |  |
| Grateful Apparition | repeatable trigger (cadence not priced) | closer |
| Gyre Sage | activated ability (repeatable, not priced) |  |
| Hardened Scales | replacement or prevention effect |  |
| Incubation Druid | activated ability (repeatable, not priced); replacement or prevention effect | fixing |
| Inexorable Tide | repeatable trigger (cadence not priced) |  |
| Kimahri, Valiant Guardian | animation; copy effect; keyworded mechanic: ronso rage; repeatable trigger (cadence not priced) |  |
| Lord Jyscal Guado | repeatable trigger (cadence not priced) | closer |
| Lulu, Stern Guardian | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Luminous Broodmoth | repeatable trigger (cadence not priced) | closer, recursion |
| Maester Seymour | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| O'aka, Traveling Merchant | activated ability (repeatable, not priced) |  |
| Path of Discovery | repeatable trigger (cadence not priced) |  |
| Path to Exile | unparsed text |  |
| Promise of Loyalty | unparsed text |  |
| Pull from Tomorrow | X-scaled magnitude |  |
| Rampant Rejuvenator | X-scaled magnitude | death_payoff |
| Resourceful Defense | activated ability (repeatable, not priced); counter movement or preservation; repeatable trigger (cadence not priced) |  |
| Rikku, Resourceful Guardian | activated ability (repeatable, not priced); counter movement or preservation; repeatable trigger (cadence not priced); unparsed text | closer |
| Scholar of New Horizons | activated ability (repeatable, not priced); unparsed text |  |
| Shelinda, Yevon Acolyte | repeatable trigger (cadence not priced) |  |
| Sin, Unending Cataclysm | X-scaled magnitude; counter movement or preservation; unparsed text | closer, death_payoff |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Sphere Grid | keyworded mechanic: unlock ability; repeatable trigger (cadence not priced) |  |
| Summon: Magus Sisters | unparsed text |  |
| Summon: Valefor | unparsed text | closer, spot_removal |
| Summon: Yojimbo | X-scaled magnitude; unparsed text | fixing |
| Summoner's Sending | repeatable trigger (cadence not priced) |  |
| Sunscorch Regent | repeatable trigger (cadence not priced) | closer |
| Tidus, Yuna's Guardian | counter movement or preservation; keyworded mechanic: cheer; repeatable trigger (cadence not priced); unparsed text |  |
| Tireless Tracker | repeatable trigger (cadence not priced) |  |
| Together Forever | activated ability (repeatable, not priced); unparsed text | death_payoff |
| Tromell, Seymour's Butler | X-scaled magnitude; activated ability (repeatable, not priced); additional or multiplied effect | counter_multiplier |
| Wakka, Devoted Guardian | repeatable trigger (cadence not priced) |  |
| Walking Ballista | X-scaled magnitude; activated ability (repeatable, not priced) | closer |
| Yuna's Decision | unparsed text | sac_outlet |
| Yuna's Whistle | X-scaled magnitude; unparsed text |  |
| Yuna, Grand Summoner | activated ability (repeatable, not priced); additional or multiplied effect; repeatable trigger (cadence not priced) |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 2; cards: Lord Jyscal Guado, Tireless Tracker |
| parallel producers | event: creature token enters; independent sources: 2; cards: Chasm Skulker, Summoner's Sending |
| linear payoff | Bane of Progress: enter -> power, wipe (fed by 1 cards) |
| linear payoff | Chasm Skulker: draw -> power (fed by 5 cards) |
| linear payoff | Duskshell Crawler: enter -> power (fed by 1 cards) |
| linear payoff | Fight Rigging: begin_combat -> power (fed by each turn) |
| linear payoff | Grateful Apparition: combat_damage -> counters (fed by combat) |
| linear payoff | Inexorable Tide: cast -> counters (fed by 60 cards) |
| linear payoff | Shelinda, Yevon Acolyte: enter -> power (fed by 32 cards) |
| linear payoff | Sphere Grid: combat_damage -> power (fed by combat) |
| linear payoff | Tireless Tracker: sacrifice -> power (fed by 0 cards) |
| linear payoff | Wakka, Devoted Guardian: combat_damage -> interaction, power (fed by combat) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.53 | 1.26 | 2.07 | 2.88 | 3.75 | 4.37 |
| can attack | 0.53 | 1.26 | 2.07 | 2.88 | 3.75 | 4.37 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.26 | 1.06 | 1.75 | 2.64 | 3.19 | 3.86 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.9 | 0.97 | 1.18 | 1.24 | 1.62 | 1.72 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.52 | 3.33 | 2.93 | 2.35 | 1.78 | 1.23 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 87% | 0% | 27% | 76% | spells waiting for mana |
| T4 | 0% | 86% | 0% | 20% | 81% | spells waiting for mana |
| T5 | 0% | 80% | 0% | 33% | 83% | spells waiting for mana |
| T6 | 0% | 65% | 0% | 23% | 82% | spells waiting for mana |
| T7 | 0% | 54% | 0% | 48% | 89% | spells waiting for mana |
| T8 | 0% | 43% | 0% | 41% | 91% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 3 | 0.0 | 11.1 | +0.0 (SE 0.0) |
| station_first | 3 | 0.0 | 11.1 | +0.0 (SE 0.0) |
| mana_first | 3 | 0.0 | 11.1 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 34.0% / 84.0% |
| light blockers: lethal by T10 | 0.7% |
| light blockers: median damage by T8 / T10 | 2 / 3 |
| tokens per turn T4-T8 (mean) | 0.21 |
| cards drawn by T8 (mean, incl. normal draws) | 8.6 |
| board at end of T8 (median bodies / power) | 5 / 12 |
| power per body at end of T8 (median) | 2.33 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 8 -> 7 | -3.4 (SE 0.3) |
| exile wipe after T6 | 8 -> 7 | -3.4 (SE 0.3) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.64 | -1.9 (SE 0.2) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 8 -> 4; commander casts T7-T10 2.13 | -3.6 (SE 0.3) |
| no commander (ablation) | tokens per turn T4-T8: 0.21 -> 0.25 | -0.2 (SE 0.2) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Altered Ego | this spell can't be countered.; you may have this creature enter as a copy of any creature on the battlefield, except it enters with x additional +1/+1 counters |
| An Offer You Can't Refuse | its controller creates two treasure tokens |
| Auron, Venerated Guardian | shooting star — whenever ~ attacks, put a +1/+1 counter on it. when you do, exile target creature defending player controls with power less than ~'s power until |
| Blitzball Stadium | support x; until end of turn target creature gains "whenever deals combat damage to a player for each kind of counter on it" and it |
| Bred for the Hunt | whenever a creature you control with a +1/+1 counter on it deals combat damage to a player, you may draw a card. |
| Chasm Skulker | where x is the number of +1/+1 counters on |
| Chocobo Knights | creatures you control with counters on them gain double strike until end of turn |
| Collective Effort | escalate tap an untapped creature you control; choose one or more — |
| Destroy Evil | choose one — |
| Duskshell Crawler | each creature you control with a +1/+1 counter on it has trample. |
| Endless Detour | the owner of target spell nonland permanent or card in a graveyard puts it on their choice of the top or bottom of their library |
| Everflowing Chalice | multikicker {2}; this artifact enters with a charge counter on it for each time it was kicked.; for each charge counter on |
| Farewell | choose one or more —; • exile all enchantments; • exile all graveyards |
| Farseek | search your library for a plains island swamp or mountain card put it onto the battlefield tapped then shuffle |
| Fathom Mage | evolve; whenever a +1/+1 counter is put on this creature, you may draw a card. |
| Fight Rigging | hideaway 5; if you control a creature with power 7 or greater you may play the exiled card without paying its mana cost |
| Forgotten Ancient | whenever a player casts a spell, you may put a +1/+1 counter on this creature.; move any number of +1/+1 counters from onto other creatures |
| Gatta and Luzzu | choose target creature you control if damage would be dealt to that creature this turn prevent that damage and put that many +1/+1 counters on it |
| Generous Patron | support 2; whenever you put one or more counters on a creature you don't control, draw a card. |
| Grateful Apparition | or planeswalker |
| Gyre Sage | evolve; for each +1/+1 counter on |
| Hardened Scales | if one or more +1/+1 counters would be put on a creature you control, that many plus one +1/+1 counters are put on it instead. |
| Incubation Druid | add one mana of any type that a land you control could produce if has a +1/+1 counter on it add three mana of that type instead; adapt 3 |
| Inspiring Call | for each creature you control with a +1/+1 counter on it those creatures gain indestructible until end of turn |
| Kimahri, Valiant Guardian | ronso rage — at the beginning of combat on your turn, put a +1/+1 counter on ~ and tap target creature an opponent controls. then you may have ~ become a copy o |
| Lord Jyscal Guado | if you put a counter on a creature this turn |
| Lulu, Stern Guardian | whenever an opponent attacks you, choose target creature attacking you. put a stun counter on that creature. |
| Luminous Broodmoth | return it to the battlefield under its owner's control with a flying counter on it |
| Maester Seymour | put a number of +1/+1 counters equal to ~'s power on another target creature you control; monstrosity x where x is the number of counters among creatures you co |
| Path of Discovery | it explores |
| Path to Exile | its controller may search their library for a basic land card put that card onto the battlefield tapped then shuffle |
| Promise of Loyalty | each player puts a vow counter on a creature they control and sacrifices the rest each of those creatures can't attack you or planeswalkers you control for as l |
| Protection Magic | put a shield counter on each of up to three target creatures |
| Rampant Rejuvenator | this creature enters with two +1/+1 counters on it.; search your library for up to x basic land cards where x is 's power put them onto the battlefield then shu |
| Resourceful Defense | whenever a permanent you control leaves the battlefield, if it had counters on it, put those counters on target permanent you control.; move any number of count |
| Rikku, Resourceful Guardian | whenever you put one or more counters on a creature, until end of turn, that creature can't be blocked by creatures your opponents control.; move a counter from |
| Scholar of New Horizons | this creature enters with a +1/+1 counter on it.; search your library for a plains card and reveal it if an opponent controls more lands than you you may put th |
| Shelinda, Yevon Acolyte | otherwise |
| Sin, Unending Cataclysm | as ~ enters, remove all counters from any number of artifacts, creatures, and enchantments. ~ enters with x +1/+1 counters on it, where x is twice the number of |
| Sphere Grid | unlock ability — creatures you control with +1/+1 counters on them have reach and trample. |

## Uncertainty

- 56 of 63 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 8 of 63 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
