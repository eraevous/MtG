# Deck: Rootha

- Rootha, Mastering the Moment (UR), 100 cards
- Lands 36, nonland 63 (creatures 23), average nonland mana value 3.48
- Mana (goldfish, on the draw): 4 by T4 82.5%, all colors by T5 96.7%, commander out by T4 65.2% / T6 93.3%
- Weakest areas (seen by T7 vs target): protection 0.0% (0 cards), closer 14.1% (1 cards), protection:anti_wipe 0.0% (0 cards)
- Count screen (post-hoc): none (of the checks run on all 13 decks)
- Engine (light blockers): median damage by T10 2; unopposed goldfish lethal by T10 72.0% (upper bound)
- Most frequent bottleneck T6-T8: spells waiting for mana
- After a T6 destroy wipe: median board power 7 before, 6 three turns later
- Without the commander: damage by T10 +0.6 (paired); typed coverage 10 of 64 nonland cards fully read

**Conclusive:** no. a deck profile is descriptive; it does not rank this deck against others

## Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)

- None raised.

## Structure compared with the other 12 decks

| measure | this deck | range across decks | rank (1 = most exposed) |
|---|---|---|---|
| tap claimants | 1 | 0 to 10 | 6 of 13 |
| tap claimants per creature card | 0.04 | 0.0 to 0.62 | 6 of 13 |
| station power needed | 0 | 0 to 30 | 5 of 13 |
| artifact-sacrifice claimants | 1 | 0 to 5 | 5 of 13 |
| creature cards | 24 | 16 to 44 | 2 of 13 |
| creatures with power 4+ | 4 | 2 to 12 | 2 of 13 |
| lasting anthems | 0 | 0 to 1 | 1 of 13 |
| engines needing combat damage | 2 | 0 to 4 | 4 of 13 |

## Shared-resource claims by card (count; the turn-engine ledger below measures what happens)

| card | claim | amount | unit |
|---|---|---|---|
| Mica, Reader of Ruins | sacrifice artifacts | 1 | per use |
| Unexpected Assistance | tap creatures | 1 | per use |

## Commander dependence

| commander | engine | makes | spells that feed it | other makers of that family | protection that can cover it |
|---|---|---|---|---|---|
| Rootha, Mastering the Moment | no | creature | - | 5 | none |

## Curve (nonland mana value)

| MV | cards |
|---|---|
| 1 | 7 |
| 2 | 18 |
| 3 | 13 |
| 4 | 10 |
| 5 | 7 |
| 6 | 2 |
| 7+ | 6 |

## Coverage bands (pre-kernel, counts vs ASSUMED targets)

| function | cards | target | band |
|---|---|---|---|
| ramp | 17 | 10 | Excessive |
| fixing | 17 | 6 | Excessive |
| draw | 22 | 10 | Excessive |
| spot_removal | 7 | 8 | Adequate |
| wipe | 2 | 2 | Strong |
| counterspell | 1 | None | not scored |
| protection | 0 | 5 | Absent |
| recursion | 1 | 3 | Fragile |
| closer | 1 | 4 | Fragile |

## Draw access (exact, on the draw)

| role | cards | T3 | T5 | T7 | T10 | T7 if unconfirmed tags were true |
|---|---|---|---|---|---|---|
| ramp | 17 | 86.3% | 91.0% | 94.2% | 97.1% | 95.2% |
| draw | 22 | 93.0% | 96.0% | 97.8% | 99.1% | 98.2% |
| spot_removal | 7 | 53.7% | 60.8% | 66.8% | 74.5% | 71.9% |
| wipe | 2 | 19.3% | 22.9% | 26.4% | 31.5% | 46.2% |
| protection | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| recursion | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 54.1% |
| closer | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 46.2% |
| counterspell | 1 | 10.1% | 12.1% | 14.1% | 17.2% | 26.4% |
| fixing | 7 | 53.7% | 60.8% | 66.8% | 74.5% | 97.3% |

## Gap to target (seen by T7)

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 0 | 5 | 0.0% | 54.1% | 54.1 |
| closer | 1 | 4 | 14.1% | 46.2% | 32.1 |
| protection:anti_wipe | 0 | 2 | 0.0% | 26.4% | 26.4 |
| recursion | 1 | 3 | 14.1% | 37.0% | 22.9 |
| spot_removal | 7 | 8 | 66.8% | 71.9% | 5.1 |
| wipe | 2 | 2 | 26.4% | 26.4% | -0.0 |
| ramp | 17 | 10 | 94.2% | 79.9% | -14.3 |
| draw | 22 | 10 | 97.8% | 79.9% | -17.9 |

## Typed answers

| card | kind | answers |
|---|---|---|
| Ashling's Command | damage | ordinary |
| Blasphemous Act | damage | ordinary |

## Typed protection

- No protection read.

## Typed recursion

| card | to | referent | cadence |
|---|---|---|---|
| Divergent Equation | hand | any card | one-shot |
| Furygale Flocking | cast | other | one-shot |
| Impulsivity | cast | other | one-shot |
| Quistis Trepe | cast | other | one-shot |

## Modules (formal draw access by T7; maturity by source counts)

| module | access T7 | maturity | source counts per group | plan |
|---|---|---|---|---|
| aristocrats | 0.0% | fragment | 19/0/0 | yes |
| counters | 0.0% | fragment | 2/0 |  |
| artifact_tokens | 26.4% | package | 7/2 | yes |
| blink | 0.0% | fragment | 0/7 |  |
| landfall | 0.0% | fragment | 2/0 |  |
| spellslinger | 83.0% | redundant | 36/11 | yes |
| graveyard | 9.8% | package | 8/1 | yes |
| go_wide | 14.1% | package | 19/1 | yes |

## Cards the evaluator only partly understands

| card | not priced | unconfirmed tags |
|---|---|---|
| Arcane Signet | activated ability (repeatable, not priced) |  |
| Archmage Emeritus | copy effect; repeatable trigger (cadence not priced) |  |
| Artist's Talent | activated ability (repeatable, not priced); cost reduction or free cast; repeatable trigger (cadence not priced); replacement or prevention effect | closer |
| Ashling's Command | copy effect; unparsed text |  |
| Big Score |  | fixing |
| Blasphemous Act | cost reduction or free cast |  |
| Blazing Firesinger // Seething Song | unparsed text | fixing |
| Consult the Star Charts | X-scaled magnitude; keyworded mechanic: kicker; replacement or prevention effect; unparsed text |  |
| Cursed Mirror | activated ability (repeatable, not priced); animation; copy effect |  |
| Deep Analysis | keyworded mechanic: flashback | recursion |
| Dig Through Time | unparsed text |  |
| Dirgur Focusmage // Braingeyser | X-scaled magnitude; cost reduction or free cast; repeatable trigger (cadence not priced); unparsed text |  |
| Divergent Equation | X-scaled magnitude; unparsed text |  |
| Echocasting Symposium | copy effect; unparsed text | token_maker |
| Ember Island Production | copy effect; unparsed text |  |
| Enduring Curiosity | repeatable trigger (cadence not priced); unparsed text | closer, death_payoff, spot_removal |
| Expressive Iteration | unparsed text |  |
| Fellwar Stone | activated ability (repeatable, not priced) |  |
| Fury | keyworded mechanic: evoke |  |
| Furygale Flocking | cost reduction or free cast; unparsed text |  |
| Galazeth Prismari | activated ability (repeatable, not priced); unparsed text |  |
| Gandalf's Sanction | X-scaled magnitude; replacement or prevention effect |  |
| Glen Elendra's Answer | uncounterable; unparsed text | counterspell |
| Goldspan Dragon | activated ability (repeatable, not priced); repeatable trigger (cadence not priced) |  |
| Harmonic Prodigy | additional or multiplied effect |  |
| Haughty Djinn | cost reduction or free cast; unparsed text |  |
| Here Comes a New Hero! | X-scaled magnitude; copy effect |  |
| High Tide | additional or multiplied effect; repeatable trigger (cadence not priced) | ramp |
| Impulse | unparsed text |  |
| Impulsivity | cost reduction or free cast; replacement or prevention effect; unparsed text | recursion, token_maker |
| Inspired Skypainter // Maestro's Gift | copy effect; repeatable trigger (cadence not priced); unparsed text | recursion |
| Into the Flood Maw | replacement or prevention effect; unparsed text | token_maker |
| Magma Opus | activated ability (repeatable, not priced); unparsed text |  |
| Mica, Reader of Ruins | copy effect; repeatable trigger (cadence not priced) | copy, protection |
| Muddle, the Ever-Changing | animation; copy effect; repeatable trigger (cadence not priced) | token_maker |
| Pelargir Survivor | activated ability (repeatable, not priced); unparsed text |  |
| Prismari Charm | unparsed text |  |
| Prismari Command | unparsed text |  |
| Prismari Pianist | repeatable trigger (cadence not priced); replacement or prevention effect |  |
| Quistis Trepe | replacement or prevention effect | recursion |
| Redoubled Stormsinger | copy effect; repeatable trigger (cadence not priced) | wipe |
| Return the Favor | copy effect; unparsed text | protection |
| Rionya, Fire Dancer | X-scaled magnitude; repeatable trigger (cadence not priced); unparsed text |  |
| Rite of Replication | copy effect; keyworded mechanic: kicker; replacement or prevention effect |  |
| Rootha, Mastering the Moment | X-scaled magnitude; repeatable trigger (cadence not priced) |  |
| Seize the Spoils |  | fixing, sac_outlet |
| Shellshock | X-scaled magnitude; unparsed text | wipe |
| Sleight of Hand | unparsed text |  |
| Sol Ring | activated ability (repeatable, not priced) |  |
| Storm-Kiln Artist | copy effect; repeatable trigger (cadence not priced) | fixing |
| Stormcatch Mentor | cost reduction or free cast |  |
| Tablet of Discovery | activated ability (repeatable, not priced); unparsed text |  |
| Talisman of Creativity | activated ability (repeatable, not priced); unparsed text |  |
| The Emperor of Palamecia // The Lord Master of Hell | X-scaled magnitude; activated ability (repeatable, not priced); repeatable trigger (cadence not priced); unparsed text | copy |
| Thunderclap Drake | activated ability (repeatable, not priced); copy effect; cost reduction or free cast; unparsed text |  |
| Traumatic Critique | X-scaled magnitude | closer |
| Treasure Cruise | unparsed text |  |
| Twinflame | copy effect; repeatable trigger (cadence not priced); unparsed text |  |
| Unexpected Assistance | unparsed text |  |
| Veyran, Voice of Duality | additional or multiplied effect; copy effect; repeatable trigger (cadence not priced) |  |

## Engine routes (typed events; cast, enter and create are separate hooks)

| class | detail |
|---|---|
| parallel producers | event: artifact token enters; independent sources: 4; cards: Galazeth Prismari, Goldspan Dragon, Magma Opus, Storm-Kiln Artist |
| parallel producers | event: creature token enters; independent sources: 2; cards: Prismari Pianist, Redoubled Stormsinger |
| linear payoff | Archmage Emeritus: cast -> cards (fed by 33 cards) |
| linear payoff | Artist's Talent: cast -> cards (fed by 40 cards) |
| linear payoff | Enduring Curiosity: combat_damage -> cards (fed by combat) |
| linear payoff | The Emperor of Palamecia // The Lord Master of Hell: cast -> power (fed by 40 cards) |

## Resource ledger (light blockers, attack first; mean per game, 300 games)

| per turn (mean) | T3 | T4 | T5 | T6 | T7 | T8 |
|---|---|---|---|---|---|---|
| bodies at start | 0.26 | 0.77 | 1.51 | 2.08 | 2.74 | 3.37 |
| can attack | 0.26 | 0.77 | 1.51 | 2.08 | 2.74 | 3.37 |
| with 2+ uses | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| attacked | 0.13 | 0.61 | 1.35 | 1.92 | 2.39 | 2.94 |
| could attack but spent before combat | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to station | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped to crew | 0 | 0 | 0 | 0 | 0 | 0 |
| spent for mana | 0 | 0 | 0 | 0 | 0 | 0 |
| tapped for other costs | 0 | 0 | 0 | 0 | 0 | 0 |
| untapped at end | 0.56 | 0.82 | 0.69 | 0.74 | 1.01 | 1.06 |
| station charge still needed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| spells waiting in hand | 3.42 | 3.45 | 3.29 | 2.89 | 2.25 | 1.76 |

## Bottlenecks by turn (share of games)

| turn | station waiting for bodies | spells waiting for mana | attackers spent before combat | attackers kept home (blockers) | bodies left idle | most frequent |
|---|---|---|---|---|---|---|
| T3 | 0% | 87% | 0% | 13% | 52% | spells waiting for mana |
| T4 | 0% | 87% | 0% | 16% | 74% | spells waiting for mana |
| T5 | 0% | 86% | 0% | 17% | 57% | spells waiting for mana |
| T6 | 0% | 79% | 0% | 20% | 60% | spells waiting for mana |
| T7 | 0% | 71% | 0% | 32% | 70% | spells waiting for mana |
| T8 | 0% | 60% | 0% | 37% | 64% | spells waiting for mana |

## Who gets a contested body: three policies (light blockers, same shuffles)

| policy | damage by T10 (median) | station charge by T10 (mean) | cards by T10 (mean) | damage vs attack first (paired mean) |
|---|---|---|---|---|
| attack_first | 2 | 0.0 | 15.8 | +0.0 (SE 0.0) |
| station_first | 2 | 0.0 | 15.8 | +0.0 (SE 0.0) |
| mana_first | 2 | 0.0 | 15.8 | +0.0 (SE 0.0) |

## Closing (conditional; see assumptions)

| measure | value |
|---|---|
| unopposed goldfish conditional lethal by T8 / T10 | 15.3% / 72.0% |
| light blockers: lethal by T10 | 0.0% |
| light blockers: median damage by T8 / T10 | 1 / 2 |
| tokens per turn T4-T8 (mean) | 0.38 |
| cards drawn by T8 (mean, incl. normal draws) | 11.7 |
| board at end of T8 (median bodies / power) | 4 / 10 |
| power per body at end of T8 (median) | 2.67 |

## Resilience scenarios (light blockers; paired with the same shuffles)

| scenario | board power before -> 3 turns after (median) | damage by T10 change |
|---|---|---|
| destroy wipe after T6 | 7 -> 6 | -2.0 (SE 0.2) |
| exile wipe after T6 | 7 -> 6 | -2.0 (SE 0.2) |
| commander removed after T5 and T7 (recast with tax) | commander casts by T10: 2.59 | -1.5 (SE 0.2) |
| attrition: destroy wipe after T6, then commander removed after T7, T8 and T9 | 7 -> 3; commander casts T7-T10 2.13 | -2.2 (SE 0.2) |
| no commander (ablation) | tokens per turn T4-T8: 0.38 -> 0.44 | +0.6 (SE 0.2) |

## Engine coverage (what the turn engine reads)

| card | not read |
|---|---|
| Artist's Talent | discard a card if you do; {2}{r}: level 2; {2}{r}: level 3; if a source you control would deal noncombat damage to an opponent or a permanent an opponent contro |
| Ashling's Command | choose two —; • create a token that's a copy of target elemental you control.; • target player draws two cards.; • ~ deals 2 damage to each creature target play |
| Blasphemous Act | this spell costs {1} less to cast for each creature on the battlefield. |
| Blazing Firesinger // Seething Song | ~ {2}{r}; this creature enters prepared.; seething song {2}{r}; add {r}{r}{r}{r}{r}. |
| Consult the Star Charts | kicker {1}{u}; look at the top x cards of your library where x is the number of lands you control put one of those cards into your hand if this spell was kicked |
| Cursed Mirror | as this artifact enters, you may have it become a copy of any creature on the battlefield until end of turn, except it has haste. |
| Deep Analysis | target player |
| Dig Through Time | delve; look at the top seven cards of your library put two of them into your hand and the rest on the bottom of your library in any order |
| Dirgur Focusmage // Braingeyser | ~ {2}{u}; with mana value 5 or greater from your hand becomes prepared; braingeyser {x}{u}{u}; target player draws x cards. |
| Divergent Equation | return up to x target instant and/or sorcery cards from your graveyard to your hand; exile ~ |
| Echocasting Symposium | target player creates a token that's a copy of target creature you control; paradigm |
| Ember Island Production | choose one —; • create a token that's a copy of target creature you control except it's not legendary and it's a 4/4 hero in addition to its other types; • crea |
| Enduring Curiosity | if it was a creature return it to the battlefield under its owner's control it's an enchantment |
| Expressive Iteration | look at the top three cards of your library put one of them into your hand put one of them on the bottom of your library and exile one of them you may play the  |
| Fellwar Stone | that a land an opponent controls could produce |
| Fury | double strike; it deals 4 damage divided as you choose among any number of target creatures and/or planeswalkers; evoke—exile a red card from your hand. |
| Furygale Flocking | this spell costs {1} less to cast for each instant and sorcery card in your graveyard.; for each opponent they gain haste until end of turn |
| Galazeth Prismari | artifacts you control have "{t}: add one mana of any color. spend this mana only to cast an instant or sorcery spell." |
| Gandalf's Sanction | ~ deals x damage to target creature where x is the number of instant and sorcery cards in your graveyard excess damage is dealt to that creature's controller in |
| Glen Elendra's Answer | this spell can't be countered; counter all spells your opponents control and all abilities your opponents control for each spell and ability countered this way |
| Goldspan Dragon | or becomes the target of a spell; treasures you control have "{t}, sacrifice this artifact: add two mana of any one color." |
| Harmonic Prodigy | if a triggered ability of a shaman or another wizard you control triggers, that ability triggers an additional time. |
| Haughty Djinn | ~'s power is equal to the number of instant and sorcery cards in your graveyard. |
| Here Comes a New Hero! | target player create a token that's a copy of up to one target creature with mana value x or less |
| High Tide | until end of turn whenever a player taps an island for mana that player adds an additional {u} |
| Impulse | look at the top four cards of your library put one of them into your hand and the rest on the bottom of your library in any order |
| Impulsivity | cast target instant or sorcery card from a graveyard without paying its mana cost if that spell would be put into a graveyard exile it instead; encore {7}{r}{r} |
| Inspired Skypainter // Maestro's Gift | ~ {u}{r}; whenever one or more creature tokens you control deal combat damage to a player becomes prepared; maestro's gift {3}{u}{r}; create a token that's a co |
| Into the Flood Maw | gift a tapped fish; if the gift was promised instead |
| Magma Opus | ~ deals 4 damage divided as you choose among any number of targets tap two target permanents |
| Mana Geyser | for each tapped land your opponents control |
| Mica, Reader of Ruins | ward—pay 3 life.; sacrifice an artifact if you do copy that spell and you may choose new targets for the copy |
| Muddle, the Ever-Changing | ~ becomes a copy of up to one target nonlegendary creature you control until end of turn except it has myriad |
| Pelargir Survivor | spend this mana only to cast an instant or sorcery spell; target player mills three cards |
| Prismari Charm | choose one —; • then |
| Prismari Command | choose two; • target player then discards two cards; • target player creates a treasure token |
| Prismari Pianist | if that spell's mana value is 5 or greater create three of those tokens instead |
| Quistis Trepe | blue magic — when ~ enters, you may cast target instant or sorcery card from a graveyard, and mana of any type can be spent to cast that spell. if that spell wo |
| Redoubled Stormsinger | for each creature token you control that entered this turn at the beginning of the next end step sacrifice those tokens |
| Return the Favor | spree; + {1} copy target instant spell sorcery spell activated ability or triggered ability you may choose new targets for the copy; + {1} change the target of  |

## Uncertainty

- 60 of 64 distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.
- Goldfish rates use 5000 games; sampling error is about ±1.4 points (95%).
- Turn engine: 10 of 64 nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.

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
