# PROPOSED: how to decide the Token Triumph review class

**Status: PROPOSED** (D-0027). Nothing has been applied. The review packet, the KB, the review overlay and the decks are unchanged. Only Zach decides.
**Author:** claude:mtg, 2026-11-04. **Grounding:** doctrine only. This checkout has no KB database (`kb_bootstrap.py status`: collections none), so the readings of Oracle text below are my own and come from the packet's `oracle_clause` column. DIO sections used: §2, §4.3, §10, §11, §12.1, §12.6. No card was annotated in the KB.

## The class

`review_packet/` puts priority `1 Token Triumph` first: **79 operations on 62 cards** in the Emmara, Soul of the Accord precon. It is a priority tier and not a mechanical class. Its rows fall into **42 of the 88 mechanical classes** (`kind | hook -> produces`), and in most of those classes some rows belong to other decks. Today it has 68 `extracted_candidate` and 11 `requires_manual_annotation` rows, 54 medium and 25 low confidence, and no verdicts. The review overlay is empty.

## The decision: split it into three groups

**Recommendation: split. Do not accept or reject the tier as a whole.**

| group | rows | rule | what Zach does |
|---|---:|---|---|
| **A: ready** | 36 rows, 31 cards, 20 classes | `extracted_candidate`, medium confidence, kernel readiness `structured`, no `why_flagged` | Give **row verdicts** (`row_verdict`: ok / needs_review / rejected) by checking each typed gate against Oracle text. Leave `class_verdict` blank where the class has rows outside group A. |
| **B: low confidence** | 25 rows (11 `requires_manual_annotation`) | confidence low | `needs_review` row by row. They are already in the Sheet Review Queue. |
| **C: not ready** | 18 rows | medium confidence, but readiness is `inherits_parent` (10), `out_of_scope` (7) or `partial` (1) | No verdict yet. Review with the parent spell, after the granted ability is split out, or once the residue is typed (each row's `kernel_next`). |

Group A by class: C04 mana abilities (9: Avacyn's Pilgrim, Elfhame Palace, Graypelt Refuge, Holdout Settlement ×2, Jaspera Sentinel, Talisman of Unity, Tranquil Expanse, Vitu-Ghazi); C05 activated token makers (6: Dawn of Hope, Idol of Oblivion, Jade Mage, Selesnya Evangel, Selesnya Guildmage, Vitu-Ghazi); C07 (Dauntless Escort, Selesnya Guildmage op002); C14 (Champion of Lambholt op002, Rishkar op001); C33 landfall tokens (Maja op002, Sporemound); and one row each in C06 Valor in Akros, C09 Hornet Queen, C10 Ajani +1, C13 Karametra's Favor, C20 Graypelt Refuge, C22 Nullmage Shepherd, C29 Eternal Witness, C30 Conclave Tribunal, C32 Felidar Retreat (mode header), C42 Talisman of Unity op002, C66 Farhaven Elf, C70 Reclamation Sage, C72 Great Oak Guardian, C82 Emmara, C88 Verdant Force.

An `ok` row verdict still leaves the row a candidate. `verified` needs scenario ids (`review_packet/README.md`, CHARTER 3).

## Evidence for splitting rather than accepting

- **Accepting the tier would be the banned bulk promotion.** CHARTER's anti-patterns include "Promoting contracts by class, in bulk". AGENTS.md says "never mass-approve". The packet says "Validate by mechanical class. Do not mass-approve." A tier spans 42 classes, so one verdict on it would not even be a class verdict.
- **Class verdicts would spill outside the tier.** The 20 group-A classes hold 84 operations, and 48 of them sit outside group A. For example, C04 has 19 rows, of which 10 are in Token Triumph. A class verdict given while looking at the Emmara deck would decide rows nobody looked at. Row verdicts keep the scope to what was checked.
- **Some medium-confidence rows lose information** (my reading, not KB-grounded):
  - *Rootborn Defenses* (C02): "Populate" creates a token copy, but `result_produces` is empty. DIO §4.3 and §10 keep token copy and token creation as distinct events ("Copy family, never merged"). An `ok` on C02 would accept a row that drops a token creation in a token deck.
  - *Presence of Gond* (C01): a granted "{T}: Create a token" ability is stored as a continuous effect. The packet's own `kernel_next` says to split it out first, and the 2026-10-25 state names granted-ability inheritance as a known drafter bug.
  - *Great Oak Guardian* (C72, group A): only `permanent.untap` is produced, and the +2/+2 is not. Row-level review exists to catch exactly this.
- **Group B is already flagged.** 12 rows carry "Qualified timing and resource gates" and 11 carry "Grammar parse incomplete".

## Evidence against (or for doing something else)

- **Rejecting the tier has no support.** Nothing in the repo shows the group-A rows are wrong. The 2026-10-22 blind sample found 68% fully correct and 92% structurally correct contracts. Rejecting the tier would throw away the cheapest reviewable rows.
- **The packet may be stale.** It was built against `mtg-kb-v0.2.1-r20261024d`. The current release is `r20261104` (drafter 0.6.0, D-0025), and operation ids or shapes may have moved. I could not check this here (no KB). Before verdicts are applied, `review.py add` should confirm that each id still exists with the same shape.
- **Row verdicts on 36 rows cost more of Zach's time** than 20 class verdicts would. An alternative is class verdicts only on the 7 group-A classes that lie wholly inside Token Triumph (C33, C42, C66, C70, C72, C82, C88). That covers 8 rows. It is cheaper but narrower.

## What it would change in decks

**No card list changes.** Verdicts change the representation, not the 100 cards (DIO §2: the ontology does not decide what is worth a slot). What changes is what can be said about Token Triumph with evidence behind it:

- The deck profile reports only 23 of 61 nonland cards fully typed. Group A covers its mana base (9 rows), its repeatable token makers (C05, C33, C82, C88) and its commander trigger.
- **Emmara's engine becomes checkable.** Emmara triggers on "becomes tapped" (C82, gate `permanent.tap{self}`). Group A also holds the cards whose cost is "tap an untapped creature you control" (Holdout Settlement, Jaspera Sentinel, Selesnya Evangel). DIO §4.3 keeps "entered tapped" separate from "became tapped", and §12.1 keeps "tap capacity spent" separate from "permanent consumed". With these rows reviewed, the question "do these costs tap Emmara for a token?" moves from my reading to a reviewed link. The deck profile ranks Token Triumph 2nd of 13 for tap claimants (8), which is the contention a swap decision would weigh.
- Groups B and C stay candidates. They include the deck's convoke and X-token spells (March of the Multitudes, Scatter the Seeds, White Sun's Zenith) and its wipe Hour of Reckoning ("nontoken"). Any swap reasoning about those cards stays labelled "candidate".
