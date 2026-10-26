# Deck: Brigid

- Brigid, Clachan's Heart // Brigid, Doun's Mind (WG), 100 cards
- Lands 35, nonland 64 (creatures 43), average nonland mana value 2.70
- Mana (goldfish, on the draw): 4 by T4 52.6%, all colors by T5 94.5%, commander out by T4 88.8% / T6 96.0%
- Weakest areas (seen by T7 vs target): ramp 14.1% (1 cards), wipe 14.1% (1 cards), closer 37.0% (3 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 6; unopposed goldfish lethal by T10 95.3% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 9 before, 7 three turns later
- Without the commander: damage by T10 -0.3 (paired); typed coverage 8 of 65 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 3 | 0 to 10 | 4 of 13 |
| tap claimants per creature card | 0.07 | 0.0 to 0.62 | 5 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 0 | 0 to 5 | 8 of 13 |
| creature cards | 44 | 16 to 44 | 13 of 13 |
| creatures with power 4+ | 5 | 2 to 12 | 6 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 1 | 0 to 4 | 5 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Golden Argosy | crew | 1 | per use |
| Heirloom Epic | tap creatures | 1 | per use |
| The Wandering Rescuer | tap creatures | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Brigid, Clachan's Heart // Brigid, Doun's Mind | no | creature | - | 9 | Adept Watershaper, Boromir, Warden of the Tower, Prehistoric Pet, The Wandering Rescuer, Vigorbloom Charm |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 14 |
| 2 | 18 |
| 3 | 16 |
| 4 | 7 |
| 5 | 7 |
| 6 | 2 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 1 | 10 | Fragile |
| fixing | 7 | 6 | Strong |
| draw | 10 | 10 | Strong |
| spot_removal | 8 | 8 | Strong |
| wipe | 1 | 2 | Adequate |
| counterspell | 0 | None | not scored |
| protection | 6 | 5 | Strong |
| recursion | 6 | 3 | Excessive |
| closer | 3 | 4 | Adequate |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 26.4% |
| draw | 10 | 67.4% | 74.3% | 79.9% | 86.3% | 83.1% |
| spot_removal | 8 | 58.8% | 65.9% | 71.9% | 79.2% | 85.8% |
| wipe | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 61.0% |
| protection | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 71.9% |
| recursion | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 66.8% |
| closer | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 61.0% |
| protection:team | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 37.0% |
| protection:anti_wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:all_creatures | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| fixing | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 71.9% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| ramp | 1 | 10 | 14.1% | 79.9% | 65.8 |
| wipe | 1 | 2 | 14.1% | 26.4% | 12.3 |
| closer | 3 | 4 | 37.0% | 46.2% | 9.2 |
| protection:anti_wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| spot_removal | 8 | 8 | 71.9% | 71.9% | 0.0 |
| draw | 10 | 10 | 79.9% | 79.9% | 0.0 |
| protection | 6 | 5 | 61.0% | 54.1% | -6.8 |
| recursion | 6 | 3 | 61.0% | 37.0% | -23.9 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Golden Argosy | exile | indestructible, big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Adept Watershaper | indestructible | all_creatures | damage, destroy |
| Biosynthic Burst | indestructible | unclear | damage, destroy |
| Boromir, Warden of the Tower | indestructible | all_creatures | damage, destroy |
| Lightning Greaves | hexproof | unclear | - |
| Prehistoric Pet | blink/bounce own | single_target | damage, destroy, exile, minus, sacrifice |
| The Wandering Rescuer | hexproof | all_creatures | - |
| Vigorbloom Charm | indestructible | single_target | damage, destroy |
| Vigorbloom Charm | hexproof | single_target | - |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Astelli Reclaimer | battlefield | any card of a type | one-shot |
| Case of the Uneaten Feast | cast | self only | one-shot |
| Dundoolin Weaver | hand | any card of a type | one-shot |
| Helping Hand | battlefield | any creature | one-shot |
| Peerless Recycling | hand | any card of a type | one-shot |
| Peerless Recycling | hand | any card of a type | one-shot |
| Serra Paragon | cast | other | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 8/0/2 | yes |
| counters | 53.6% | redundant | 20/5 | yes |
| artifact_tokens | 1.9% | package | 1/1 | yes |
| lifegain | 25.0% | package | 15/2 | yes |
| blink | 14.1% | package | 1/17 | yes |
| landfall | 0.0% | fragment | 5/0 |  |
| spellslinger | 12.2% | package | 13/1 | yes |
| graveyard | 15.5% | package | 2/6 | yes |
| go_wide | 46.2% | redundant | 8/4 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Aang's Iceberg | activated ability (repeatable, not priced); unparsed text |  |
| Astelli Reclaimer | X-scaled magnitude; unparsed text |  |
| Biosynthic Burst | unparsed text |  |
| Blossoming Bogbeast | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Boromir, Warden of the Tower | repeatable trigger (cadence not priced); unparsed text | counterspell |
| Bounding Felidar | repeatable trigger (cadence not priced); unparsed text |  |
| Bramblewood Paragon | additional or multiplied effect | wipe |
| Brigid, Clachan's Heart // Brigid, Doun's Mind | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Carrot Cake | activated ability (repeatable, not priced) | sac_outlet |
| Case of the Uneaten Feast | repeatable trigger (cadence not priced); unparsed text |  |
| Cloudbound Moogle | unparsed text |  |
| Coeurl | activated ability (repeatable, not priced) | spot_removal |
| Dawnstrike Vanguard | repeatable trigger (cadence not priced) |  |
| Drix Fatemaker | unparsed text | recursion, wipe |
| Elite Interceptor // Rejoinder | unparsed text | copy |
| Emil, Vastlands Roamer | X-scaled magnitude; activated ability (repeatable, not priced); unparsed text |  |
| Focus Fire | X-scaled magnitude | closer, spot_removal |
| Golden Argosy | keyworded mechanic: crew; repeatable trigger (cadence not priced) | blink |
| Guac & Marshmallow Pizza | activated ability (repeatable, not priced); unparsed text |  |
| Guardian Sunmare | repeatable trigger (cadence not priced); unparsed text | protection |
| Haliya, Guided by Light | repeatable trigger (cadence not priced); unparsed text | recursion |
| Heirloom Epic | activated ability (repeatable, not priced); unparsed text |  |
| Helping Hand |  | spot_removal |
| Hunter's Talent | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Lightning Greaves | unparsed text |  |
| Lita, Little Orphan Amphibian | keyworded mechanic: alliance; repeatable trigger (cadence not priced); unparsed text | token_maker |
| Mighty Mutanimals | keyworded mechanic: alliance; repeatable trigger (cadence not priced) |  |
| Nyxborn Hydra | X-scaled magnitude; keyworded mechanic: bestow |  |
| Ohran Frostfang | repeatable trigger (cadence not priced); unparsed text |  |
| Owlin Historian | repeatable trigger (cadence not priced) |  |
| Pawpatch Recruit | keyworded mechanic: offspring; repeatable trigger (cadence not priced) | protection, token_maker |
| Peerless Recycling | replacement or prevention effect; unparsed text | draw, spot_removal |
| Prehistoric Pet | activated ability (repeatable, not priced); unparsed text | closer |
| Qasali Pridemage | activated ability (repeatable, not priced); unparsed text | sac_outlet |
| Queen Allenal of Ruadach | replacement or prevention effect; unparsed text | token_maker |
| Quintessential Katana | repeatable trigger (cadence not priced); unparsed text |  |
| Rayblade Trooper | repeatable trigger (cadence not priced); unparsed text |  |
| Requisition Raid | unparsed text |  |
| Rosa, Resolute White Mage | repeatable trigger (cadence not priced) |  |
| Salvation Swan | repeatable trigger (cadence not priced) | blink, closer |
| Spiritcall Enthusiast // Scrollboost | repeatable trigger (cadence not priced); unparsed text |  |
| Stampeding Scurryfoot | activated ability (repeatable, not priced) |  |
| Starfield Shepherd | unparsed text |  |
| Stirring Hopesinger | repeatable trigger (cadence not priced) | wipe |
| Strength of the Coalition | keyworded mechanic: kicker; unparsed text | wipe |
| Studious First-Year // Rampant Growth | unparsed text |  |
| Suki, Courageous Rescuer | repeatable trigger (cadence not priced); unparsed text |  |
| Sundering Growth |  | copy, token_maker |
| Teleportation Circle | repeatable trigger (cadence not priced) |  |
| The Wandering Rescuer | unparsed text | wipe |
| To Arms! | unparsed text |  |
| Traveling Botanist | repeatable trigger (cadence not priced); unparsed text |  |
| Trudge Garden | repeatable trigger (cadence not priced) | lifegain_source |
| Umbral Mantle | activated ability (repeatable, not priced); unparsed text |  |
| Undergrowth Leopard | activated ability (repeatable, not priced) | sac_outlet |
| Vastlands Scavenger // Bind to Life | unparsed text | copy |
| Veteran Beastrider | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Vigorbloom Charm | unparsed text |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: creature token enters; independent sources: 6; cards: Brigid, Clachan's Heart // Brigid, Doun's Mind, Carrot Cake, Emil, Vastlands Roamer, Mighty Mutanimals, Stampeding Scurryfoot, Trudge Garden |
| unbounded feedback | cycle: Haliya, Guided by Light: enter -> Trudge Garden: lifegain -> Case of the Uneaten Feast: enter; limit: none read |
| linear payoff | Cloudbound Moogle: enter -> power (fed by 1 cards) |
| linear payoff | Dawnstrike Vanguard: end_step -> power (fed by each turn) |
| linear payoff | Drix Fatemaker: enter -> power (fed by 1 cards) |
| linear payoff | Dundoolin Weaver: enter -> recursion (fed by 1 cards) |
| linear payoff | Elvish Visionary: enter -> cards (fed by 1 cards) |
| linear payoff | Guac & Marshmallow Pizza: enter -> power (fed by 1 cards) |
| linear payoff | Haliya, Guided by Light: end_step -> cards (fed by each turn) |
| linear payoff | Hunter's Talent: attack -> power (fed by combat) |
| linear payoff | Hunter's Talent: end_step -> cards (fed by each turn) |
| linear payoff | Little Bear: enter -> power (fed by 1 cards) |
| linear payoff | Mighty Mutanimals: enter -> power (fed by 46 cards) |
| linear payoff | Ohran Frostfang: combat_damage -> cards (fed by combat) |
| linear payoff | Rayblade Trooper: enter -> power (fed by 1 cards) |
| linear payoff | Rosa, Resolute White Mage: begin_combat -> power (fed by each turn) |
| feed-forward chain | Blossoming Bogbeast: attack -> Trudge Garden: lifegain -> Case of the Uneaten Feast: enter |
| feed-forward chain | Blossoming Bogbeast: attack -> Trudge Garden: lifegain -> Haliya, Guided by Light: enter |
| feed-forward chain | Blossoming Bogbeast: attack -> Trudge Garden: lifegain -> Lita, Little Orphan Amphibian: enter |
| feed-forward chain | Blossoming Bogbeast: attack -> Trudge Garden: lifegain -> Mighty Mutanimals: enter |
| feed-forward chain | Blossoming Bogbeast: attack -> Trudge Garden: lifegain -> Spiritcall Enthusiast // Scrollboost: enter |
| feed-forward chain | Bounding Felidar: attack -> Trudge Garden: lifegain -> Case of the Uneaten Feast: enter |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.79 | 2.17 | 2.83 | 3.52 | 4.16 | 5.0 |
| can attack | 0.79 | 2.17 | 2.83 | 3.52 | 4.16 | 5.0 |
| with 2+ uses | 0.0 | 0.0 | 0.12 | 0.23 | 0.45 | 0.57 |
| attacked | 0.34 | 1.44 | 1.6 | 2.98 | 3.18 | 4.26 |
| could attack but spent before combat | 0 | 0.06 | 0.04 | 0.06 | 0.04 | 0.07 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0.06 | 0.09 | 0.14 | 0.15 | 0.17 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 1.94 | 1.47 | 1.83 | 1.42 | 2.13 | 2.34 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 4.22 | 3.94 | 3.32 | 2.65 | 2.0 | 1.55 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 94% | 0% | 45% | 91% | spells waiting for mana |
| T4 | 0% | 93% | 4% | 55% | 87% | spells waiting for mana |
| T5 | 0% | 85% | 2% | 66% | 90% | spells waiting for mana |
| T6 | 0% | 76% | 3% | 43% | 84% | spells waiting for mana |
| T7 | 0% | 55% | 2% | 60% | 87% | spells waiting for mana |
| T8 | 0% | 46% | 4% | 45% | 83% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 6 | 0.0 | 13.0 | +0.0 (SE 0.0) |
| station_first | 6 | 0.0 | 13.0 | -0.0 (SE 0.0) |
| mana_first | 6 | 0.0 | 13.0 | -0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 60.0% / 95.3% |
| light blockers: lethal by T10 | 4.0% |
| light blockers: median damage by T8 / T10 | 4 / 6 |
| tokens per turn T4-T8 (mean) | 0.32 |
| cards drawn by T8 (mean, incl. normal draws) | 9.5 |
| board at end of T8 (median bodies / power) | 5 / 13 |
| power per body at end of T8 (median) | 2.43 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 9 -> 7 | -15.1 (SE 5.2) |
| exile wipe after T6 | 9 -> 7 | -15.1 (SE 5.2) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.50 | -9.9 (SE 5.0) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 9 -> 6; commander casts T7-T10 1.64 | -15.6 (SE 5.2) |
| no commander (ablation) | tokens per turn T4-T8: 0.32 -> 0.28 | -0.3 (SE 3.5) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Aang's Iceberg | exile up to one other target nonland permanent until this enchantment leaves the battlefield; sacrifice this enchantment if you do |
| Adept Watershaper | other tapped creatures you control have indestructible. |
| Astelli Reclaimer | return target noncreature nonland permanent card with mana value x or less from your graveyard to the battlefield where x is the amount of mana spent to cast; w |
| Biosynthic Burst | it gains reach trample and indestructible until end of turn untap it |
| Blossoming Bogbeast | creatures you control gain trample and get +x/+x until end of turn where x is the amount of life you gained this turn |
| Boromir, Warden of the Tower | whenever an opponent casts a spell, if no mana was spent to cast it, counter that spell.; creatures you control gain indestructible until end of turn the ring t |
| Bounding Felidar | while saddled for each of those creatures; saddle 2 |
| Bramblewood Paragon | each other warrior creature you control enters with an additional +1/+1 counter on it.; each creature you control with a +1/+1 counter on it has trample. |
| Brigid, Clachan's Heart // Brigid, Doun's Mind | ~ {2}{w}; or transforms into ~; pay {g} if you do transform ~; ~, doun's mind; add x {g} or x {w} where x is the number of other creatures you control; pay {w}  |
| Case of the Uneaten Feast | to solve — you've gained 5 or more life this turn.; solved — sacrifice this case: creature cards in your graveyard gain "you may cast this card from your gravey |
| Cloudbound Moogle | plainscycling {2} |
| Coeurl | tap target nonenchantment creature |
| Drix Fatemaker | each creature you control with a +1/+1 counter on it has trample.; warp {1}{g} |
| Dundoolin Weaver | if you control three or more creatures |
| Elite Interceptor // Rejoinder | ~ {w}; this creature enters prepared.; rejoinder {1}{w}; you may tap or untap target creature.; draw a card. |
| Emil, Vastlands Roamer | creatures you control with +1/+1 counters on them have trample.; put x +1/+1 counters on it where x is the number of differently named lands you control |
| Focus Fire | ~ deals x damage to target attacking or blocking creature where x is 2 plus the number of creatures and/or spacecraft you control |
| Golden Argosy | exile each creature that crewed it this turn return them to the battlefield tapped under their owner's control at the beginning of the next end step |
| Guac & Marshmallow Pizza | untap it |
| Guardian Sunmare | ward {2}; while saddled search your library for a nonland permanent card with mana value 3 or less put it onto the battlefield then shuffle; saddle 4 |
| Haliya, Guided by Light | if you've gained 3 or more life this turn; warp {w} |
| Heirloom Epic | for each mana in this ability's activation cost you may tap an untapped creature you control rather than pay that mana |
| Helping Hand | return target creature card with mana value 3 or less from your graveyard to the battlefield tapped |
| Hunter's Talent | when this class enters, target creature you control deals damage equal to its power to target creature you don't control.; {1}{g}: level 2; target attacking; {3 |
| Lightning Greaves | equipped creature has haste and shroud. |
| Lita, Little Orphan Amphibian | choose one that hasn't been chosen this turn; • put a +1/+1 counter on ~.; • create a food token.; • scry 1. |
| Little Bear | untap another target creature you control if that creature is a bear |
| Nyxborn Hydra | bestow {x}{g}{g}; this permanent enters with x +1/+1 counters on it.; enchanted creature gets +1/+1 for each +1/+1 counter on this aura and has reach and trampl |
| Ohran Frostfang | attacking creatures you control have deathtouch. |
| Owlin Historian | whenever one or more cards leave your graveyard, this creature gets +1/+1 until end of turn. |
| Pawpatch Recruit | whenever a creature you control becomes the target of a spell or ability an opponent controls, put a +1/+1 counter on target creature you control other than tha |
| Peerless Recycling | gift a card; if the gift was promised instead return two target permanent cards from your graveyard to your hand |
| Prehistoric Pet | this creature can't be blocked by creatures with greater power.; return another target creature you control to its owner's hand activate only during your turn |
| Qasali Pridemage | exalted |
| Queen Allenal of Ruadach | ~'s power and toughness are each equal to the number of creatures you control.; if one or more creature tokens would be created under your control, those tokens |
| Quintessential Katana | equipped creature gets +1/+1 and has "whenever this creature deals combat damage, untap it and you gain 2 life."; attach this equipment to it |
| Rayblade Trooper | whenever a nontoken creature you control with a +1/+1 counter on it dies, create a 1/1 white human soldier creature token.; warp {1}{w} |
| Requisition Raid | spree; + {1}; + {1}; + {1} |
| Rosa, Resolute White Mage | it gains lifelink until end of turn |
| Salvation Swan | return it to the battlefield under its owner's control with a flying counter on it at the beginning of the next end step |

## Uncertainty

- 58 of 65 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 8 of 65 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
