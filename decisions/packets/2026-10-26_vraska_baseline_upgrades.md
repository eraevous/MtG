# Upgrades for Vraska

- Weakest areas: protection (1 cards, seen by T7 14.1% vs 54.1% at target), recursion (0 cards, seen by T7 0.0% vs 37.0% at target), ramp (7 cards, seen by T7 66.8% vs 79.9% at target)
- Candidates: free pool only, legal in WUR, no tutors
- 10 upgrades shown; each pairs one add with one cut, and every cut is a different card.

**Conclusive:** no. see the conclusive column per upgrade

## Weakest functional areas

| area | sources | target (ASSUMPTION) | seen by T7 | at target | gap (points) |
|---|---|---|---|---|---|
| protection | 1 | 5 | 14.1% | 54.1% | 40.0 |
| recursion | 0 | 3 | 0.0% | 37.0% | 37.0 |
| ramp | 7 | 10 | 66.8% | 79.9% | 13.1 |

## Upgrades

| add | source | improves (seen by T7) | costs elsewhere | donor loss (no backfill) | mana/colors (goldfish) | cut | add understood | engine: damage by T10 (paired) | engine: power 3 turns after T6 wipe | conclusive |
|---|---|---|---|---|---|---|---|---|---|---|
| Duty Beyond Death | free | protection +12.3, protection:anti_wipe +14.1 | spot_removal -1.6 | none | 4 mana T4 +0.0, colors T5 +0.0 | Desculpting Blast (mechanically_audited_cut) | partial | -1.8 (SE 1.1) | -0.0 (SE 0.0) | no |
| Fateshaper Aspirant | free | protection +12.3, recursion +14.1 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Carrot Cake (human_review_required) | complete | -1.5 (SE 2.8) | +0.1 (SE 0.1) | no |
| Barrels of Blasting Jelly | free | ramp +5.0 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Cori-Steel Cutter (human_review_required) | partial | +0.7 (SE 0.8) | -0.2 (SE 0.1) | no |
| Adept Watershaper | free | protection +12.3, protection:anti_wipe +14.1 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Gossip's Talent (human_review_required) | complete | +7.0 (SE 5.0) | +0.3 (SE 0.2) | no |
| The Walls of Ba Sing Se | free | protection +12.3, protection:anti_wipe +14.1 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Pinnacle Emissary (human_review_required) | complete | -6.7 (SE 2.8) | +0.2 (SE 0.4) | no |
| Krang, Utrom Warlord | free | protection +12.3, protection:anti_wipe +14.1 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Saheeli, Sublime Artificer (human_review_required) | complete | -3.6 (SE 1.7) | +0.2 (SE 0.2) | no |
| Rattleblaze Scarecrow | free | protection +12.3, recursion +14.1 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Strixhaven Skycoach (human_review_required) | partial | +8.9 (SE 11.7) | +0.1 (SE 0.2) | no |
| Chase Inspiration | free | protection +12.3 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Whirler Rogue (human_review_required) | complete | +5.9 (SE 5.8) | -0.1 (SE 0.1) | no |
| Crumb and Get It | free | protection +12.3 | none | none | 4 mana T4 +0.0, colors T5 +0.0 | Wurmwall Sweeper (human_review_required) | partial | -1.7 (SE 0.5) | -0.0 (SE 0.2) | no |
| Earth Kingdom Protectors | free | protection +12.3 | draw -0.6 | none | 4 mana T4 -0.6, colors T5 +0.0 | Cryogen Relic (human_review_required) | complete | -1.2 (SE 0.7) | -0.2 (SE 0.2) | no |

## Cut order used (lowest measured loss first)

| card | label | loss by T7 |
|---|---|---|
| Desculpting Blast | mechanically_audited_cut | -2.4 |
| Carrot Cake | human_review_required | +0.0 |
| Cori-Steel Cutter | human_review_required | +0.0 |
| Gossip's Talent | human_review_required | +0.0 |
| Pinnacle Emissary | human_review_required | +0.0 |
| Saheeli, Sublime Artificer | human_review_required | +0.0 |
| Strixhaven Skycoach | human_review_required | +0.0 |
| Whirler Rogue | human_review_required | +0.0 |
| Wurmwall Sweeper | human_review_required | +0.0 |
| Cryogen Relic | human_review_required | -0.6 |
| Elsewhere Flask | human_review_required | -0.6 |
| Guidelight Matrix | human_review_required | -0.6 |

## Uncertainty

- A cut labelled human_review_required has abilities the evaluator cannot price; check it before moving a card.
- Gains are draw access only; a card that is drawn may still lack mana, targets or a board to use it.

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
