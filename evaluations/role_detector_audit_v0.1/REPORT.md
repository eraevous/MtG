# Role-detector audit v0.1 (2026-10-28)

A bounded, risk-ordered audit of the KB role detectors (`kb/vendor/mtg_eval/semantics.py`, release r20261028), following Kate's plan after the Golden Argosy error. `wipe` was audited separately in PR #10: 3 false positives out of 74 detections.

**Verification state.** Every judgment is Claude's model reading of Oracle text. None has been reviewed by Zach or Kate. These are not DIO contract reviews. The per-pair records are in `tier1_records.jsonl` and `tier23_records.jsonl`, with card, role, Oracle text, detector span, assessment, reason, and whether the card is a sole detected candidate in a deck.

## Method

- For each role, the sample was:
  - every sole detected candidate across the 13 decks;
  - a seeded random sample of in-deck detections, plus a few detections outside any deck;
  - a seeded sample of **tag-only** cards. The inventory Sheet tags these with the role, but the detector missed them, so they are false-negative candidates.
- `sample.py` reproduces the selection. Run it from the repo root with KB r20261028; it needs PR #10's `sole_detected_candidates`. The seed is `audit-2026-10-28-<role>`.
- Assessments:
  - `true_positive` / `false_positive` / `ambiguous` for detections;
  - `false_negative` / `tag_error` / `ambiguous` for tag-only cards.
  - `ambiguous` mostly means the role's definition is unclear, not that the card is unclear.

## Results

| Tier | Role | Detections sampled | TP | FP | Ambiguous | Tag-only sampled | Real misses (FN) | Wrong Sheet tags | Ambiguous |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | spot_removal | 35 | 31 | 0 | 4 | 20 | 10 | 8 | 2 |
| 1 | protection | 36 | 32 | 0 | 4 | 20 | 8 | 4 | 8 |
| 1 | recursion | 39 | 38 | 0 | 1 | 20 | 4 | 13 | 3 |
| 2 | ramp | 29 | 25 | 0 | 4 | 15 | 5 | 7 | 3 |
| 2 | fixing | 29 | 26 | 0 | 3 | 15 | 0 | 1 | 14 |
| 2 | draw | 28 | 25 | 0 | 3 | 14 | 2 | 4 | 8 |
| 3 | closer | 29 | 24 | 0 | 5 | 15 | 4 | 5 | 6 |
| 3 | sac_outlet | 28 | 27 | 0 | 1 | 15 | 5 | 8 | 2 |
| 3 | token_maker | 28 | 18 | 0 | 10 | 15 | 7 | 3 | 5 |
| | **total** | **281** | **246** | **0** | **35** | **149** | **45** | **53** | **51** |

## Corrections after Kate's spot-check (2026-10-28)

Kate checked all 45 misses, all 85 ambiguous records, the reported false positive and a sample of true positives. Her review led to these changes:

- **Vraska, Betrayal's Sting is not a false positive.** Its −2 can target a creature you control, and you keep the Treasure. It is now `ambiguous` (conditional, inefficient fixing), so the audit has **0 established false positives** among the 281 detections.
- **Overall conclusion revised.** The audited detections contain few established false positives, while detector omissions are common among Sheet-tagged negatives. Population precision and recall are **not** established: the samples are not uniform, and every judgment is a model's. Unresolved role definitions change both measures.
- **Several "misses" depend on the role definition:**
  - Queen Allenal and Stridehangar Automaton are token multipliers or replacements, not independent token sources.
  - Buzzard-Wasp Colony allows a one-shot sacrifice.
  - Rockalanche's flashback is self-reuse, not recovery of other cards.
- **Provenance.** Each record now carries `claim_provenance` (`oracle_pattern` / `hand_label` / `inventory_tag`). Two closer "detections" (Eirdu, Heroes in a Half Shell) are `hand_label` and should not count toward detector precision.
- **Reproducibility.** `sample.py` now uses the tier-1 sizes (25 + 10 detections, 15 + 5 tag-only). It reproduces all nine recorded samples exactly, checked against KB r20261028.
- The "about a third wrong Sheet tags" figure applies only to the sampled tag-only records, not to all Sheet tags.

The original findings below are kept as written, apart from the Vraska counts.

## Findings

1. **(Superseded; see Corrections.) Precision is high. A Golden Argosy-type error looks rare.**
   - Only 1 clear false positive turned up in 281 sampled detections: Vraska, Betrayal's Sting's −2 counted as fixing, but the Treasure stays with the opponent.
   - With roughly 30 detections per role, a role with 0 false positives could still have up to about 10% (95% upper bound). So "rare" is an estimate, not a guarantee.

2. **Recall is the bigger weakness.** About 30% of the tag-only cards (45 of 149) are real misses. That means a "sole detected candidate" more often *understates* a deck's redundancy than invents it. The misses have three recurring causes:
   - **Reminder text is stripped before matching**, so keyword mechanics never match: offspring, encore and populate (token_maker), flashback (recursion), cycling (draw).
   - **Narrow vocabularies**:
     - number words stop at "six" (Raphael's Technique: "draw seven cards");
     - sacrifice subtypes such as Servo and Eldrazi are missing;
     - "create a *tapped* Treasure" and "up to that many basic land cards" don't match.
   - **Phrasing variants**:
     - −1/−1 counters on a target creature (Skinrender, Grim Poppet, Incremental Blight);
     - "each of up to two target creatures";
     - "X target nonland permanents";
     - "target attacking or blocking creature";
     - "equipped creature has hexproof/indestructible";
     - "… have ward";
     - "can't be the targets of spells or abilities your opponents control".
   - Untagged misses were **not** measured, because the miss pool came only from Sheet-tagged cards. True recall is likely lower.

3. **The Sheet's Roles tags are noisy.** About a third of the sampled tag-only claims (53 of 149) are wrong tags. Examples:
   - cards that sacrifice only themselves are tagged as sacrifice outlets;
   - effects that give an opponent tokens or Treasures are tagged as token makers or ramp;
   - earthbend and bounce lands are tagged as recursion;
   - Golden Argosy is tagged "Board wipe".
   Keeping tags out of role counts is right. Fixing the tags means editing the Sheet, which is Zach's call.

4. **Unclear role definitions cause most of the ambiguous calls.**
   - `token_maker` counts Treasure, Food and Mutagen (10 of 28 sampled).
   - `fixing` leaves out lands by design, so a deck's fixing count omits its dual lands (14 of 15 tag-only fixing cards were lands).
   - `draw` counts loots.
   - `closer` mixes drains, anthems and evasion.
   - Deciding these is design intent for Zach.

5. **Some role claims aren't from the detector at all.** Claims from hand labels (`tmnt_function_labels.csv`) are stored as `machine_supported`, for example Eirdu and Heroes in a Half Shell as `closer`. The role summary cannot tell them apart.

6. **The detector doesn't track who gets the token or mana.** Vraska's −2, An Offer You Can't Refuse and Emergency Eject give the token or mana to an opponent. The detector got the first one wrong, and the Sheet mis-tagged the other two.

## What follows (proposals, not done)

- **Narrow false-positive fix:** don't count a mana or token effect that ends up under an opponent's control. This would follow the kb patch 3 pattern, plus a regression test.
- **Recall fixes.** These change many claims, so they need Zach's go-ahead:
  - read keyword mechanics before reminder text is stripped (keyword → role);
  - extend the number words;
  - add the phrasing variants above, each with a test.
- **Definitions (Zach):** decide whether `token_maker` means creature tokens, and whether `fixing` should count lands, or the summary should say it excludes them. Possibly split `draw` from `loot`.
- **Provenance:** store hand-label claims with their own status, separate from the detector.
- **Before relying on these results:** have Kate or Zach spot-check a share of the records. Then audit untagged misses with a random sample of cards that have no claim and no tag.
