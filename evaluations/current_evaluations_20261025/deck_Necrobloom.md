# Deck: Necrobloom

- The Necrobloom (WBG), 100 cards
- Lands 41, nonland 58 (creatures 28), average nonland mana value 3.17
- Mana (goldfish, on the draw): 4 by T4 63.1%, all colors by T5 91.2%, commander out by T4 37.3% / T6 91.6%
- Weakest areas (seen by T7 vs target): closer 26.4% (2 cards), protection 46.2% (4 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 0; unopposed goldfish lethal by T10 56.7% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 5 before, 7 three turns later
- Without the commander: damage by T10 +0.0 (paired); typed coverage 4 of 60 nonland cards fully read

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
| creature cards | 30 | 16 to 44 | 7 of 13 |
| creatures with power 4+ | 4 | 2 to 12 | 2 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 0 | 0 to 4 | 8 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| The Seriema | station | 7 | one-time |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| The Necrobloom | no | creature | - | 6 | Blacksmith's Skill, Rootborn Defenses, The Seriema |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 3 |
| 2 | 17 |
| 3 | 19 |
| 4 | 10 |
| 5 | 6 |
| 6 | 1 |
| 7+ | 2 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 11 | 10 | Strong |
| fixing | 24 | 12 | Excessive |
| draw | 14 | 10 | Strong |
| spot_removal | 12 | 8 | Strong |
| wipe | 2 | 2 | Strong |
| counterspell | 0 | None | not scored |
| protection | 4 | 5 | Adequate |
| recursion | 6 | 3 | Excessive |
| closer | 2 | 4 | Adequate |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 11 | 71.0% | 77.8% | 83.1% | 88.9% | 88.1% |
| draw | 14 | 79.9% | 85.8% | 90.0% | 94.2% | 90.0% |
| spot_removal | 12 | 74.3% | 80.8% | 85.8% | 91.0% | 90.0% |
| wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 46.2% |
| protection | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 46.2% |
| recursion | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 96.0% |
| closer | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 37.0% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:all_creatures | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| fixing | 9 | 63.3% | 70.4% | 76.2% | 83.1% | 98.8% |
| counter_preservation | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| closer | 2 | 4 | 26.4% | 46.2% | 19.8 |
| protection | 4 | 5 | 46.2% | 54.1% | 7.9 |
| wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| protection:anti_wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| ramp | 11 | 10 | 83.1% | 79.9% | -3.2 |
| draw | 14 | 10 | 90.0% | 79.9% | -10.1 |
| spot_removal | 12 | 8 | 85.8% | 71.9% | -13.9 |
| recursion | 6 | 3 | 61.0% | 37.0% | -23.9 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Final Act | destroy, exile | indestructible, big_toughness, ordinary |
| Game Over | destroy | big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Blacksmith's Skill | indestructible | single_target | damage, destroy |
| Blacksmith's Skill | hexproof | single_target | - |
| Origin of Metalbending | indestructible | unclear | damage, destroy |
| Rootborn Defenses | indestructible | all_creatures | damage, destroy |
| The Seriema | indestructible | all_creatures | damage, destroy |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Coiling Rebirth | battlefield | any creature | one-shot |
| Deadly Brew | hand | any card of a type | one-shot |
| Pothole Mole | hand | any card of a type | one-shot |
| Primary Research | battlefield | any card of a type | one-shot |
| The Cruelty of Gix | battlefield | any creature | one-shot |
| Twilight Diviner | cast | other | repeatable |
| Witherbloom Command | hand | any card of a type | one-shot |
| You Happen on a Glade | hand | any card of a type | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 15.8% | package | 10/2/2 | yes |
| counters | 32.0% | redundant | 11/3 | yes |
| artifact_tokens | 6.6% | package | 2/2 | yes |
| lifegain | 0.0% | fragment | 5/0 |  |
| blink | 0.0% | fragment | 0/21 |  |
| landfall | 85.8% | redundant | 12/4 | yes |
| spellslinger | 0.0% | fragment | 24/0 |  |
| graveyard | 66.8% | redundant | 5/7 | yes |
| go_wide | 37.0% | redundant | 10/3 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| All-Fates Scroll | X-scaled magnitude; activated ability (repeatable, not priced) |  |
| Aron, Benalia's Ruin | activated ability (repeatable, not priced) | wipe |
| Assassin's Trophy | unparsed text |  |
| Avenger of Zendikar | repeatable trigger (cadence not priced) |  |
| Badgermole Cub | additional or multiplied effect; animation; repeatable trigger (cadence not priced) | death_payoff, ramp, recursion |
| Beifong's Bounty Hunters | X-scaled magnitude; animation; repeatable trigger (cadence not priced) | recursion |
| Beorn, Reluctant Host // Till and Tend | additional or multiplied effect; unparsed text | spot_removal |
| Blacksmith's Skill | unparsed text |  |
| Chocobo Kick | keyworded mechanic: kicker; replacement or prevention effect |  |
| Clifftop Lookout | unparsed text |  |
| Coiling Rebirth | copy effect; unparsed text |  |
| Cremate | unparsed text | spot_removal |
| Cursed Wombat | activated ability (repeatable, not priced); additional or multiplied effect; repeatable trigger (cadence not priced); unparsed text |  |
| Cycle of Renewal | unparsed text |  |
| Dai Li Agents | X-scaled magnitude; animation; repeatable trigger (cadence not priced) | death_payoff, recursion |
| Deadly Brew |  | wipe |
| Dockworker Drone |  | death_payoff |
| Earth Kingdom General | animation; repeatable trigger (cadence not priced); unparsed text | death_payoff, lifegain_source, recursion |
| Eclipsed Elf | unparsed text |  |
| Eclipsed Kithkin | unparsed text |  |
| Emil, Vastlands Roamer | X-scaled magnitude; activated ability (repeatable, not priced); unparsed text |  |
| Final Act | unparsed text | closer |
| Game Over | cost reduction or free cast |  |
| Gift of the Viper | unparsed text |  |
| Great Forest Druid | activated ability (repeatable, not priced) |  |
| Greenhouse // Rickety Gazebo | activated ability (repeatable, not priced); unparsed text | recursion |
| Hei Bai, Spirit of Balance | repeatable trigger (cadence not priced) | sac_outlet |
| Heritage Reclamation | unparsed text |  |
| High Perfect Morcant | repeatable trigger (cadence not priced); unparsed text |  |
| Lluwen, Exchange Student // Pest Friend | repeatable trigger (cadence not priced); unparsed text | recursion |
| Lys Alana Dignitary | activated ability (repeatable, not priced); unparsed text | recursion |
| Mirkwood Pathmaker | unparsed text |  |
| Mulch | unparsed text |  |
| Old Man Willow | repeatable trigger (cadence not priced); unparsed text | sac_outlet |
| Origin of Metalbending | unparsed text |  |
| Primary Research | repeatable trigger (cadence not priced) |  |
| Rat King, Pale Piper | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Ride the Shoopuf | activated ability (repeatable, not priced); animation; repeatable trigger (cadence not priced) |  |
| Rockalanche | X-scaled magnitude; animation; keyworded mechanic: flashback | death_payoff, recursion |
| Rootborn Defenses | unparsed text | copy, token_maker |
| Rosie Cotton of South Lane | repeatable trigger (cadence not priced) |  |
| Sandbender's Storm | animation; unparsed text | death_payoff, recursion |
| The Cruelty of Gix | unparsed text | recursion |
| The Earth King | repeatable trigger (cadence not priced) | ramp |
| The Necrobloom | repeatable trigger (cadence not priced); replacement or prevention effect | recursion |
| The Seriema | keyworded mechanic: station; unparsed text |  |
| Toph, the Blind Bandit | animation | death_payoff, recursion |
| Twilight Diviner | copy effect; repeatable trigger (cadence not priced); unparsed text |  |
| Weather Maker | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Witherbloom Command | unparsed text |  |
| You Happen on a Glade | unparsed text | fixing |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: creature token enters; independent sources: 4; cards: Avenger of Zendikar, Emil, Vastlands Roamer, The Earth King, The Necrobloom |
| linear payoff | Primary Research: end_step -> cards (fed by each turn) |
| linear payoff | Witch Enchanter // Witch-Blessed Meadow: enter -> interaction (fed by 1 cards) |
| feed-forward chain | Emil, Vastlands Roamer: activated -> Rosie Cotton of South Lane: create -> Earth Kingdom General: counters |
| feed-forward chain | The Necrobloom: landfall -> Rosie Cotton of South Lane: create -> Earth Kingdom General: counters |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.23 | 0.57 | 1.31 | 2.62 | 3.82 | 5.13 |
| can attack | 0.23 | 0.55 | 1.08 | 2.11 | 3.27 | 4.55 |
| with 2+ uses | 0.0 | 0.0 | 0.01 | 0.03 | 0.14 | 0.15 |
| attacked | 0.05 | 0.26 | 0.57 | 1.71 | 2.23 | 3.8 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0.01 | 0.01 | 0.03 | 0.04 | 0.06 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.45 | 0.79 | 1.46 | 1.65 | 2.47 | 2.03 |
| station charge still needed | 0.05 | 0.08 | 0.1 | 0.15 | 0.15 | 0.3 |
| spells waiting in hand | 3.41 | 3.23 | 3.12 | 2.52 | 1.88 | 1.3 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 88% | 0% | 19% | 41% | spells waiting for mana |
| T4 | 1% | 91% | 0% | 29% | 63% | spells waiting for mana |
| T5 | 1% | 92% | 0% | 44% | 89% | spells waiting for mana |
| T6 | 1% | 82% | 0% | 35% | 92% | spells waiting for mana |
| T7 | 1% | 63% | 0% | 66% | 95% | spells waiting for mana |
| T8 | 3% | 45% | 0% | 42% | 90% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 0 | 0.6 | 11.3 | +0.0 (SE 0.0) |
| station_first | 0 | 1.0 | 11.3 | +0.1 (SE 0.0) |
| mana_first | 0 | 0.6 | 11.3 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 3.7% / 56.7% |
| light blockers: lethal by T10 | 0.0% |
| light blockers: median damage by T8 / T10 | 0 / 0 |
| tokens per turn T4-T8 (mean) | 0.41 |
| cards drawn by T8 (mean, incl. normal draws) | 8.9 |
| board at end of T8 (median bodies / power) | 5 / 9 |
| power per body at end of T8 (median) | 1.67 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 5 -> 7 | -0.5 (SE 0.1) |
| exile wipe after T6 | 5 -> 7 | -0.5 (SE 0.1) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.31 | -0.6 (SE 0.1) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 5 -> 4; commander casts T7-T10 1.80 | -0.5 (SE 0.1) |
| no commander (ablation) | tokens per turn T4-T8: 0.41 -> 0.04 | +0.0 (SE 0.1) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Accursed Marauder | each player sacrifices a nontoken creature of their choice |
| All-Fates Scroll | where x is the number of differently named lands you control |
| Assassin's Trophy | its controller may search their library for a basic land card put it onto the battlefield then shuffle |
| Avenger of Zendikar | for each land you control |
| Badgermole Cub | earthbend 1; whenever you tap a creature for mana, add an additional {g}. |
| Beifong's Bounty Hunters | earthbend x where x is that creature's power |
| Beorn, Reluctant Host // Till and Tend | ~ {4}{g}; till and tend {1}{g}; you may play an additional land this turn. |
| Blacksmith's Skill | target permanent gains hexproof and indestructible until end of turn if it's an artifact creature it gets +2/+2 until end of turn |
| Chocobo Kick | kicker return a land you control to its owner's hand; target creature you control deals damage equal to its power to target creature an opponent controls if thi |
| Clifftop Lookout | reveal cards from the top of your library until you reveal a land card put that card onto the battlefield tapped and the rest on the bottom of your library in a |
| Coiling Rebirth | gift a card; if the gift was promised and that creature isn't legendary create a token that's a copy of that creature except it's 1/1 |
| Cultivate | search your library for up to two basic land cards reveal those cards put one onto the battlefield tapped and the other into your hand then shuffle |
| Cursed Wombat | adapt 2; permanents you control have "whenever one or more +1/+1 counters are put on this permanent, put an additional +1/+1 counter on it. this ability trigger |
| Cycle of Renewal | sacrifice a land search your library for up to two basic land cards put them onto the battlefield tapped then shuffle |
| Dai Li Agents | earthbend 1 then earthbend 1; each opponent loses x life and you gain x life where x is the number of creatures you control with +1/+1 counters on them |
| Deadly Brew | each player sacrifices a creature or planeswalker of their choice if you sacrificed a permanent this way you may return another permanent card from your graveya |
| Dockworker Drone | this creature enters with a +1/+1 counter on it.; put its counters on target creature you control |
| Earth Kingdom General | earthbend 2; gain that much life do this only once each turn |
| Eclipsed Elf | look at the top four cards of your library you may reveal an elf swamp or forest card from among them and put it into your hand put the rest on the bottom of yo |
| Eclipsed Kithkin | look at the top four cards of your library you may reveal a kithkin forest or plains card from among them and put it into your hand put the rest on the bottom o |
| Emil, Vastlands Roamer | creatures you control with +1/+1 counters on them have trample.; put x +1/+1 counters on it where x is the number of differently named lands you control |
| Final Act | choose one or more —; • destroy all planeswalkers; • destroy all battles; • exile all graveyards; • each opponent loses all counters |
| Game Over | this spell costs {2} less to cast if a player's life total is less than or equal to half their starting life total. |
| Gift of the Viper | put a +1/+1 counter a reach counter and a deathtouch counter on target creature untap it |
| Greenhouse // Rickety Gazebo | ~ {2}{g}; lands you control have "{t}: add one mana of any color."; rickety gazebo {3}{g}; when you unlock this door, mill four cards, then return up to two per |
| Hei Bai, Spirit of Balance | or attacks you may sacrifice another creature or artifact if you do; put its counters on target creature you control |
| Heritage Reclamation | choose one — |
| High Perfect Morcant | each opponent blights 1 |
| Kodama's Reach | search your library for up to two basic land cards reveal those cards put one onto the battlefield tapped and the other into your hand then shuffle |
| Leaves from the Vine | i — mill three cards, then create a food token.; ii — put a +1/+1 counter on each of up to two target creatures you control.; iii — draw a card if there's a cre |
| Lluwen, Exchange Student // Pest Friend | ~ {2}{b}{g}; ~ enters prepared.; exile a creature card from your graveyard: ~ becomes prepared. activate only as a sorcery.; pest friend {b/g}; create a 1/1 bla |
| Lys Alana Dignitary | activate only if there is an elf card in your graveyard |
| Mirkwood Pathmaker | ~'s power and toughness are each equal to the number of lands you control. |
| Mulch | reveal the top four cards of your library put all land cards revealed this way into your hand and the rest into your graveyard |
| Night's Whisper | you and lose 2 life |
| Old Man Willow | ~'s power and toughness are each equal to the number of lands you control.; sacrifice another creature or a token when you do target creature an opponent contro |
| Origin of Metalbending | choose one —; • it gains indestructible until end of turn |
| Pothole Mole | mill three cards then you may return a land card from your graveyard to your hand |
| Primary Research | return target nonland permanent card with mana value 3 or less from your graveyard to the battlefield; if a card left your graveyard this turn |
| Rat King, Pale Piper | whenever ~ or another nontoken creature you control leaves the battlefield, create a 1/1 black rat creature token. |

## Uncertainty

- 51 of 59 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 4 of 60 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
