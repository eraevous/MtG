# Role audit v0.2: blind review of undetected roles

- **Selections (frozen, accepted by Kate on 2026-10-28):**
  - `blind_packet.jsonl` has 360 card-role pairs with no claim of that role from any source: 9 roles × in-deck/outside × 20, seeded. Population sizes are in `population.json`.
  - `challenge_packet.jsonl` has 54 hard-mechanism items. These are for mechanism checks only and are never used for population estimates.
- **Reviewer inputs:** `reviewer/batch_01..09.jsonl` holds all 414 items shuffled together under opaque ids R001–R414, with only item, role, card, type line and Oracle text. Give reviewers these batches and `REVIEWER_GUIDE.md`, and nothing else.
- **Private:** `private_key.jsonl` maps R ids to U/C ids, stratum and mechanism. It is for analysis only.
- **Protocol (Kate):**
  - Reviewer A is a fresh-context Claude and reviewer B a fresh-context ChatGPT, ideally with no project memory.
  - Each completed batch is frozen; nobody edits it after seeing other results.
  - Disagreements are reconciled in a separate record that keeps both original answers. Inter-reviewer agreement is reported per role.
  - The KB stays frozen at r20261028 until results exist.
- **Definitions:** D-0008 (accepted by Zach). D-0009 (proposed) includes Kate's operational clarifications for ramp, fixing and draw.
- **Not measured here:** overall recall. The v0.1 detected-positive audit, the v0.1 tag-only audit and this untagged audit stay separate measures until they are combined with sampling weights.
- **Results (2026-10-29):** both reviewers are frozen in `reviews/`. `compare.py` writes `agreement.json` and `reconciliation.jsonl`, which keeps both answers and the proposed adjudication from `adjudication_claude.jsonl`. The write-up is in `REPORT.md`.
