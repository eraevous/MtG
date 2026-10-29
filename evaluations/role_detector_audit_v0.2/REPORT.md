# Role audit v0.2: results

KB r20261028, frozen. Reviewer A was a fresh Claude agent and reviewer B a fresh ChatGPT Temporary Chat. Both saw only `REVIEWER_GUIDE.md` and the reviewer batches. Reproduce with `python3 compare.py`.

Verification state: the reviewer answers are model judgments, and the adjudications are Claude proposals. Nothing here is Zach-reviewed, and no contract or claim changes.

## Agreement

| part | n | raw agreement | Cohen's kappa |
|---|---|---|---|
| untagged sample (360) | 360 | 0.94 | 0.20 |
| challenge set (54) | 54 | 0.96 | 0.93 |

Kappa is low on the untagged sample only because nearly every answer is NO (the prevalence paradox). Raw agreement is the more useful number there. The per-role figures are in `agreement.json`.

The reviewers disagree on 24 items (22 untagged, 2 challenge), and the pattern is systematic:

- **B reads the definitions more broadly.** 11 of B's DEPENDS answers are copy, redirect, reanimate or trigger-doubling cards that fill a role only if the thing copied does (Rite of Replication copying a mana dork, for example). A answered NO on all of them.
- **B called four single-creature or one-shot threats closers,** which the accepted closer rule excludes.
- **B made one carry-over error.** R131 (Stormcatch Mentor, token_maker) got ramp qualifiers from the item before it.
- **A counted impulse draw as draw.** That was Chaos Channeler, R266, which B answered NO.

## Adjudication (proposed)

`adjudication_claude.jsonl` covers all 24 disagreements:

- 19 resolve to NO under the existing rules or by analogy to them.
- 3 resolve to DEPENDS: Braingeyser as a decking win, and two tribal-only grants.
- 1 resolves to YES, R266, which needs a policy decision (see below).

Zach decided both policy questions on 2026-10-29 (D-0011, accepted), and the rows are appended to the adjudication file:
1. **Generic copy effects** answer NO with the qualifier `copy_effect`. Copy needs an ontological answer, not a role-table one. A copy ability that is itself specific ("copy a creature token you control") is classified by what it can copy. Trigger doublers and reanimation stay NO on the earlier reasoning.
2. **Impulse draw is not draw** (NO, `impulse`). Exile-and-play does not trigger draw listeners. Zach is open to counterarguments for other purposes.

So all 24 disagreements resolve to 21 NO and 3 DEPENDS, with no YES.

## Misses in the untagged population

Each stratum has only 20 cards, so the bounds are wide. The 95% upper bound is Bonferroni-adjusted: a one-sided 97.5% Clopper-Pearson bound per stratum, weighted and summed. It holds per role, not jointly across all nine. The first version summed per-stratum 95% bounds, which does not guarantee 95% coverage. Those numbers are kept in `agreement.json` as `*_upper95_sum_v1`.

| role | untagged owned cards | agreed or adjudicated YES in sample | point estimate | 95% upper |
|---|---|---|---|---|
| ramp | 3,213 | 1 (Galactic Wayfarer, Lander token) | ~121 | 736 |
| spot_removal | 2,924 | 1 (Shellshock) | ~39 | 555 |
| fixing | 3,113 | 1 (Gold Pan, Treasure token) | ~34 | 580 |
| closer, draw, protection, recursion, sac_outlet, token_maker | 2,888–3,376 | 0 | 0 | 486–569 |

## What this says

- **The point estimates are small,** under 4% of untagged cards per role. The sample cannot rule out misses as high as roughly 17–23% per role. Halving that bound would take about four times as many reviewed cards, with two reviewers each.
- **Two of the three confirmed misses are the same data-layer gap.** The token's ability lives in reminder text, which the detector strips: Treasure gives fixing and ramp, and a Lander gives ramp. The third, Shellshock ("deals X damage to each of those creatures" after "choose up to one target creature"), is a phrasing variant.
- **The v0.1 tag-only audit found its misses where the Sheet tags disagree with the detector.** Together with this audit, misses look concentrated in identifiable mechanisms rather than spread thin.
- **The next step is a targeted fix, not more sampling.** A keyword- and token-aware mapping (Treasure, Lander, Food, Clue and similar predefined tokens mapped to their roles), checked against the full collection, gains more than more sampling would. This is a data-layer fix, not a tool feature.
- **An open ontology item follows from D-0011.** Copy effects need a DIO-level treatment: a copy takes on the copied object's behavior, so role and interaction analysis should derive it at deck level. This is a design question for the grammar/DIO layer, not a role-table patch.

## Corrections after Kate's review (2026-10-29)

- **Upper bounds are now Bonferroni-adjusted,** as above. Her figures match `compare.py` exactly. The point estimates are unchanged.
- **Positive agreement is now reported alongside kappa.** On the untagged sample it is 0.21 counting YES or DEPENDS as positive, and 0.46 counting YES only. On the challenge set it is 1.00 and 0.96. The 94% raw agreement is mostly agreement on NO: the two reviewers rarely agree on which of the rare positives is real. That is why every positive here went through adjudication.
- **Temporary tap or stun is tempo control, not spot removal.** This is written down as D-0013 (proposed) so that the next reviewer reads Homesickness the same way.
- **Provenance:** the label on each adjudicated answer says whether it rests on Zach's accepted policy (`accepted_policy`) or only on Claude's proposal (`proposed`). Neither is human-verified mechanical truth. Reviewer B's provenance is in `reviews/reviewer_B/README.md`.
- **copy_effect stays an audit qualifier, not a new DIO primitive.** DIO v3.1.1 already models copying (`object.becomes_copy`, `token.create` as a copy, spell and ability copies, `trigger_multiplier`). The work left is deriving roles from those operations in context: Rite of Replication is intrinsically a token maker, and ramp only in context.
