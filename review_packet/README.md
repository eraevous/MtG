# Mechanics review packet, 2026-10-24 extraction pass

This packet holds the 330 candidate operations that the 2026-10-24 extraction pass added to the Sheet (Mechanics · Operations) for 266 owned cards that had none. They feed KB release `mtg-kb-v0.2.1-r20261024d`.

**Nothing has been verified or approved.** Each row has status `extracted_candidate` (233) or `requires_manual_annotation` (97). Confidence is medium for 161 rows and low for 169.

## Files

- `class_summary.csv` has one row per mechanical class, 88 classes in all (52 of them singletons). A class is the signature `kind | hook -> produces`. Start here.
- `operations_by_class.csv` has every operation, grouped by class and sorted by priority. It carries the Oracle clause, the 18 Sheet columns, the Review Queue flag, the kernel readiness columns, and blank verdict columns for you to fill in.
- `scripts/` holds the extraction, Review Queue and packet scripts plus `extraction.json`, so the packet can be rebuilt.

## How to review

1. Give a verdict per class in `class_summary.csv` (`class_verdict`: ok / needs_review / rejected, plus a `reviewer_note`). Validate by mechanical class. Do not mass-approve.
2. In `operations_by_class.csv`, fill in `row_verdict` and `correction` only for exceptions to the class verdict.
3. Work in priority order:
   - `1 Token Triumph`: 79 operations on 62 cards in the Emmara precon.
   - `2 allocated`: 32 more operations on other allocated cards.
   - `3 free`: the other 219 operations.

Largest classes:

| Class | Signature | Operations |
|---|---|---:|
| C01 | continuous \| - -> - | 93 |
| C02 | spell_effect \| spell.resolve -> - | 32 |
| C03 | replacement \| battlefield.enter -> - | 23 |
| C04 | activate \| - -> mana.add | 19 |
| C05 | activate \| - -> token.create | 10 |
| C06 | trigger \| battlefield.enter -> - | 9 |

## How verdicts are applied

I apply your verdicts to the review overlay with `review.py add`, one contract at a time. The contract id is the operation id.

- `needs_review`, `rejected` and `contradicted` can be recorded straight from your notes.
- `verified` needs scenario ids from `scenarios/*.json`. Without them a row stays a candidate.
- Reviews are semantic only. Runtime readiness is tracked separately, in the kernel columns.

Corrections are made in the Sheet under the archive-then-clone rule, and then the KB is rebuilt. The KB is never hand-edited.

## Flags worth a look

- **Offspring identity.** The Sheet rows for Finch Formation, Rust-Shield Rampager and Thornplate Intimidator point at token printings. Their 3 contracts are quarantined by the existing `sheet_error` reconciliation. Please confirm which printings you own.
- **Station thresholds.** For Galvanizing Sawship and Lumen-Class Frigate, the station threshold lines (`N+ |`) became continuous operations with the threshold as a requirement. Check that this matches how you want station modelled.
- **Additional costs.** Rows such as Soaring Stoneglider record the additional cost as `payment` on the cast operation and not as a separate operation.
- **Low confidence.** All 169 low-confidence rows are also in the Sheet Review Queue (rows 713–881), with kernel columns K:N filled. `in_review_queue` = yes marks them in this packet.
- **No operations.** 146 owned cards produced nothing because they are keyword-only, vanilla or basic lands. There are also 3 placeholder names ("______", "Counters", "Elemental"). They are not in this packet.

## Release

The KB is `mtg-kb-v0.2.1-r20261024d` in `mechanics-kernel/sqlite-kb/`. It has 4,961 contracts, 446 lossless compiles and 7 quarantined, and all tests pass in the release folder. The Sheet id at build time was `1N1xBUkL_aYKpPcR8WJJVpeicgE8A06dqeUBM-hUa3Xo`.
