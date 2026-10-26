# Deck: Limit Break

- Cloud, Ex-SOLDIER (WRG), 100 cards
- Lands 37, nonland 62 (creatures 24), average nonland mana value 3.05
- Mana (goldfish, on the draw): 4 by T4 78.3%, all colors by T5 89.5%, commander out by T4 28.0% / T6 80.7%
- Weakest areas (seen by T7 vs target): spot_removal 46.2% (4 cards), closer 37.0% (3 cards), protection 46.2% (4 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 4; unopposed goldfish lethal by T10 87.3% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 10 before, 10 three turns later
- Without the commander: damage by T10 -4.7 (paired); typed coverage 4 of 63 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 2 | 0 to 10 | 5 of 13 |
| tap claimants per creature card | 0.08 | 0.0 to 0.62 | 4 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 1 | 0 to 5 | 5 of 13 |
| creature cards | 25 | 16 to 44 | 3 of 13 |
| creatures with power 4+ | 7 | 2 to 12 | 9 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 3 | 0 to 4 | 2 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Clever Concealment | tap creatures | 1 | per use |
| Inspiring Statuary | tap artifacts | 1 | per use |
| Professional Face-Breaker | sacrifice artifacts | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Cloud, Ex-SOLDIER | no | artifact | - | 1 | Bastion Protector, Ultimate Magic: Holy, Zack Fair |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 7 |
| 2 | 18 |
| 3 | 19 |
| 4 | 9 |
| 5 | 3 |
| 6 | 5 |
| 7+ | 1 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 10 | 10 | Strong |
| fixing | 28 | 12 | Excessive |
| draw | 12 | 10 | Strong |
| spot_removal | 4 | 8 | Adequate |
| wipe | 5 | 2 | Excessive |
| counterspell | 0 | None | not scored |
| protection | 4 | 5 | Adequate |
| recursion | 6 | 3 | Excessive |
| closer | 3 | 4 | Adequate |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 9 | 63.3% | 70.4% | 76.2% | 83.1% | 79.9% |
| draw | 11 | 71.0% | 77.8% | 83.1% | 88.9% | 83.1% |
| spot_removal | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 71.9% |
| wipe | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 54.1% |
| protection | 4 | 35.1% | 40.9% | 46.2% | 53.5% | 66.8% |
| recursion | 6 | 48.1% | 54.9% | 61.0% | 68.8% | 61.0% |
| closer | 3 | 27.6% | 32.4% | 37.0% | 43.5% | 83.1% |
| protection:team | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:anti_wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| protection:all_creatures | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 26.4% |
| fixing | 5 | 42.0% | 48.3% | 54.1% | 61.9% | 99.6% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| spot_removal | 4 | 8 | 46.2% | 71.9% | 25.7 |
| closer | 3 | 4 | 37.0% | 46.2% | 9.2 |
| protection | 4 | 5 | 46.2% | 54.1% | 7.9 |
| ramp | 9 | 10 | 76.2% | 79.9% | 3.7 |
| protection:anti_wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| draw | 11 | 10 | 83.1% | 79.9% | -3.2 |
| recursion | 6 | 3 | 61.0% | 37.0% | -23.9 |
| wipe | 5 | 2 | 54.1% | 26.4% | -27.7 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Austere Command | destroy | big_toughness, ordinary |
| Cloud's Limit Break | destroy | big_toughness, ordinary |
| Ultimate Magic: Meteor | damage | ordinary |
| Vandalblast | asymmetric |  |
| Vanquish the Horde | destroy | big_toughness, ordinary |

## Typed protection

| card | effect | scope | survives |
|---|---|---|---|
| Bastion Protector | indestructible | all_creatures | damage, destroy |
| Champion's Helm | hexproof | unclear | - |
| Clever Concealment | phase out | unclear | bounce, damage, destroy, exile, minus, sacrifice |
| Darksteel Plate | indestructible | unclear | damage, destroy |
| Darksteel Plate | indestructible | unclear | damage, destroy |
| Lightning Greaves | hexproof | unclear | - |
| Ultimate Magic: Holy | indestructible | all_creatures | damage, destroy |
| Zack Fair | indestructible | single_target | damage, destroy |

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Aerith, Last Ancient | hand | any creature | repeatable |
| Cid, Freeflier Pilot | hand | any card | repeatable |
| Elena, Turk Recruit | hand | any card | one-shot |
| Red XIII, Proud Warrior | hand | any card | one-shot |
| Sephiroth, Fallen Hero | battlefield | self only | repeatable |
| Unfinished Business | battlefield | any creature | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 3.5% | package | 5/2/1 | yes |
| counters | 6.2% | package | 4/1 | yes |
| artifact_tokens | 37.0% | package | 2/3 | yes |
| lifegain | 14.1% | package | 2/1 | yes |
| blink | 0.0% | fragment | 0/5 | yes |
| landfall | 0.0% | fragment | 4/0 |  |
| spellslinger | 0.0% | fragment | 17/0 |  |
| graveyard | 15.5% | package | 2/6 | yes |
| go_wide | 37.0% | redundant | 5/3 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Aerith, Last Ancient | repeatable trigger (cadence not priced); replacement or prevention effect |  |
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Armory Automaton | repeatable trigger (cadence not priced) |  |
| Austere Command | unparsed text | spot_removal |
| Avalanche of Sector 7 | repeatable trigger (cadence not priced); unparsed text | closer |
| Barret Wallace | repeatable trigger (cadence not priced) | closer |
| Barret, Avalanche Leader | repeatable trigger (cadence not priced) |  |
| Behemoth Sledge | unparsed text |  |
| Bronze Guardian | unparsed text | protection |
| Bugenhagen, Wise Elder | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Cait Sith, Fortune Teller | X-scaled magnitude; repeatable trigger (cadence not priced); unparsed text |  |
| Champion's Helm | unparsed text | protection |
| Chaos Warp | unparsed text |  |
| Cid, Freeflier Pilot | activated ability (repeatable, not priced); cost reduction or free cast; unparsed text | closer |
| Clever Concealment | unparsed text |  |
| Cloud's Limit Break | unparsed text |  |
| Cloud, Ex-SOLDIER | repeatable trigger (cadence not priced) |  |
| Colossus Hammer | unparsed text |  |
| Conformer Shuriken | repeatable trigger (cadence not priced); unparsed text |  |
| Conqueror's Flail | unparsed text |  |
| Darksteel Plate | unparsed text | protection |
| Dispatch | keyworded mechanic: metalcraft; unparsed text | spot_removal |
| Elena, Turk Recruit | repeatable trigger (cadence not priced) |  |
| Explorer's Scope | repeatable trigger (cadence not priced); unparsed text |  |
| Furious Rise | repeatable trigger (cadence not priced); unparsed text |  |
| Heidegger, Shinra Executive | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Helitrooper | cost reduction or free cast; repeatable trigger (cadence not priced) | closer |
| Hellkite Tyrant | repeatable trigger (cadence not priced) | closer |
| Hero's Blade | repeatable trigger (cadence not priced); unparsed text |  |
| Hero's Heirloom | unparsed text |  |
| Inspiring Statuary | unparsed text | ramp |
| Lifestream's Blessing | X-scaled magnitude; keyworded mechanic: foretell | lifegain_source |
| Lightning Greaves | unparsed text |  |
| Mask of Memory | repeatable trigger (cadence not priced); unparsed text |  |
| Nature's Lore |  | fixing |
| Professional Face-Breaker | repeatable trigger (cadence not priced); unparsed text |  |
| Professor Hojo | cost reduction or free cast; repeatable trigger (cadence not priced); unparsed text |  |
| Puresteel Paladin | keyworded mechanic: metalcraft; repeatable trigger (cadence not priced) |  |
| SOLDIER Military Program | repeatable trigger (cadence not priced); replacement or prevention effect |  |
| Sephiroth, Fallen Hero | activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text |  |
| Skullclamp | repeatable trigger (cadence not priced); unparsed text |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Summon: Kujata | unparsed text | closer, spot_removal |
| Summoning Materia | activated ability (repeatable, not priced); unparsed text |  |
| Sword of the Animist | repeatable trigger (cadence not priced); unparsed text |  |
| Tifa, Martial Artist | additional or multiplied effect; repeatable trigger (cadence not priced); unparsed text |  |
| Trailblazer's Boots | unparsed text |  |
| Ultimate Magic: Holy | keyworded mechanic: foretell; replacement or prevention effect |  |
| Ultimate Magic: Meteor | keyworded mechanic: foretell; unparsed text | spot_removal |
| Vandalblast | keyworded mechanic: overload |  |
| Vanquish the Horde | cost reduction or free cast |  |
| Vincent, Vengeful Atoner | repeatable trigger (cadence not priced) | closer |
| Wrecking Ball Arm | unparsed text | closer |
| Yuffie, Materia Hunter | keyworded mechanic: ninjutsu; unparsed text |  |
| Zack Fair | activated ability (repeatable, not priced); unparsed text | sac_outlet |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 2; cards: Cloud, Ex-SOLDIER, Professional Face-Breaker |
| linear payoff | Bugenhagen, Wise Elder: upkeep -> cards (fed by each turn) |
| linear payoff | Cloud, Ex-SOLDIER: attack -> cards (fed by combat) |
| linear payoff | Elena, Turk Recruit: cast -> power (fed by 0 cards) |
| linear payoff | Puresteel Paladin: enter -> cards (fed by 16 cards) |
| linear payoff | Vincent, Vengeful Atoner: combat_damage -> power (fed by combat) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.25 | 0.65 | 1.37 | 2.28 | 3.24 | 4.08 |
| can attack | 0.25 | 0.65 | 1.37 | 2.28 | 3.24 | 4.08 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.14 | 0.68 | 1.53 | 2.28 | 2.94 | 3.87 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.47 | 0.65 | 0.78 | 1.02 | 1.31 | 1.23 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.09 | 2.93 | 2.62 | 2.03 | 1.37 | 0.91 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 89% | 0% | 15% | 44% | spells waiting for mana |
| T4 | 0% | 89% | 0% | 15% | 55% | spells waiting for mana |
| T5 | 0% | 85% | 0% | 17% | 58% | spells waiting for mana |
| T6 | 0% | 71% | 0% | 18% | 69% | spells waiting for mana |
| T7 | 0% | 51% | 0% | 32% | 78% | spells waiting for mana |
| T8 | 0% | 34% | 0% | 23% | 74% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 4 | 0.0 | 18.5 | +0.0 (SE 0.0) |
| station_first | 4 | 0.0 | 18.5 | +0.0 (SE 0.0) |
| mana_first | 4 | 0.0 | 18.5 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 48.0% / 87.3% |
| light blockers: lethal by T10 | 1.0% |
| light blockers: median damage by T8 / T10 | 2 / 4 |
| tokens per turn T4-T8 (mean) | 1.45 |
| cards drawn by T8 (mean, incl. normal draws) | 13.7 |
| board at end of T8 (median bodies / power) | 5 / 15 |
| power per body at end of T8 (median) | 3.00 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 10 -> 10 | -4.1 (SE 0.4) |
| exile wipe after T6 | 10 -> 10 | -4.1 (SE 0.4) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.27 | -2.7 (SE 0.3) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 10 -> 6; commander casts T7-T10 2.05 | -4.3 (SE 0.4) |
| no commander (ablation) | tokens per turn T4-T8: 1.45 -> 0.03 | -4.7 (SE 0.4) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Aerith, Last Ancient | raise — at the beginning of your end step, if you gained life this turn, return target creature card from your graveyard to your hand. if you gained 7 or more l |
| Armory Automaton | or attacks you may attach any number of target equipment to it |
| Austere Command | choose two; • destroy all enchantments |
| Avalanche of Sector 7 | ~'s power is equal to the number of artifacts your opponents control.; whenever an opponent activates an ability of an artifact they control, ~ deals 1 damage t |
| Barret Wallace | it deals damage equal to the number of equipped creatures you control to defending player |
| Barret, Avalanche Leader | avalanche! — whenever an equipment you control enters, create a 2/2 red rebel creature token.; attach up to one target equipment you control to target rebel you |
| Bastion Protector | commander creatures you control get +2/+2 and have indestructible. |
| Behemoth Sledge | equipped creature gets +2/+2 and has trample and lifelink. |
| Bronze Guardian | double strike; ward {2}; other artifacts you control have ward {2}.; ~'s power is equal to the number of artifacts you control. |
| Bugenhagen, Wise Elder | if you control a creature with power 7 or greater |
| Cait Sith, Fortune Teller | lucky slots — at the beginning of combat on your turn, scry 1, then exile the top card of your library. you may play that card this turn. when you exile a card  |
| Champion's Helm | equipped creature gets +2/+2.; as long as equipped creature is legendary, it has hexproof. |
| Chaos Warp | the owner of target permanent shuffles it into their library then reveals the top card of their library if it's a permanent card they put it onto the battlefiel |
| Cid, Freeflier Pilot | jump — during your turn, ~ has flying. |
| Clever Concealment | any number of target nonland permanents you control phase out |
| Cloud's Limit Break | tiered; • cross slash {0}; • blade beam {1} destroy any number of target tapped creatures with different controllers; • omnislash {3}{w} destroy all tapped crea |
| Cloud, Ex-SOLDIER | attach up to one target equipment you control to it; for each equipped attacking creature you control then if ~ has power 7 or greater |
| Colossus Hammer | equipped creature gets +10/+10 and loses flying. |
| Conformer Shuriken | equipped creature has "whenever this creature attacks, tap target creature defending player controls. if that creature has greater power than this creature, put |
| Conqueror's Flail | equipped creature gets +1/+1 for each color among permanents you control.; as long as this equipment is attached to a creature, your opponents can't cast spells |
| Cultivate | search your library for up to two basic land cards reveal those cards put one onto the battlefield tapped and the other into your hand then shuffle |
| Darksteel Plate | equipped creature has indestructible. |
| Dispatch | tap target creature; metalcraft if you control three or more artifacts exile that creature |
| Elena, Turk Recruit | return target non assassin historic card from your graveyard to your hand |
| Explorer's Scope | whenever equipped creature attacks, look at the top card of your library. if it's a land card, you may put it onto the battlefield tapped. |
| Furious Rise | if you control a creature with power 4 or greater exile the top card of your library you may play that card until you exile another card with this enchantment |
| Heidegger, Shinra Executive | target creature you control gets +x/+0 until end of turn where x is the number of soldiers you control; create a number of 1/1 white soldier creature tokens equ |
| Helitrooper | another target attacking creature gains flying until end of turn; equip abilities you activate that target this creature cost {2} less to activate. |
| Hellkite Tyrant | gain control of all artifacts that player controls; if you control twenty or more artifacts you win the game |
| Hero's Blade | equipped creature gets +3/+2.; attach this equipment to it |
| Hero's Heirloom | equipped creature gets +2/+1.; as long as equipped creature is legendary, it has trample and haste. |
| Inspiring Statuary | nonartifact spells you cast have improvise. |
| Lifestream's Blessing | where x is the greatest power among creatures you controlled as you cast this spell if this spell was cast from exile you gain twice x life; foretell {4}{g} |
| Lightning Greaves | equipped creature has haste and shroud. |
| Mask of Memory | whenever equipped creature deals combat damage to a player, you may draw two cards. if you do, discard a card. |
| Nature's Lore | search your library for a forest card put that card onto the battlefield then shuffle |
| Professional Face-Breaker | exile the top card of your library you may play that card this turn |
| Professor Hojo | the first activated ability you activate during your turn that targets a creature you control costs {2} less to activate.; whenever one or more creatures you co |
| Puresteel Paladin | metalcraft — equipment you control have equip {0} as long as you control three or more artifacts. |
| Rampant Growth | search your library for a basic land card put that card onto the battlefield tapped then shuffle |

## Uncertainty

- 55 of 63 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 4 of 63 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
