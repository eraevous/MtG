# MTG Card Knowledgebase v0.2.1, data refresh r20261024

A data-only rebuild of v0.2.1 after the first physical-card photo intake of 2026-10-24 (IMG_3874). The schema, the drafter (0.4.0), the compiler (0.3.0) and the overrides are unchanged.

- No contract was approved. The review overlay is still empty.
- No physical card was moved, and no deck allocation changed.

## Inventory source

- The Sheet was edited before this build, under the archive-then-clone rule. The pre-intake workbook is frozen in Drive `archive/` as "MTG Master Inventory — Canonical_20261024-1857Z_ARCHIVE" (id `1wv-uSSSlTIRAJp5qInwq0oppGUOX49_D2ni3vAnESxU`).
- The working Sheet is now id `1vAweCvOb371YNQOoDVjKRn1P83U_thk63WzvW1fRpVc` (Drive modified 2026-10-24T19:05:17.624Z). `inventory_adapter.py` and `vendor/mtg_eval/_adapter.py` carry the new id.
- The export is `canonical_20261024.xlsx`, sha256 `964f615f…20fe`.

| | v0.2.1 (2026-10-22) | r20261024 |
|---|---:|---:|
| Collection rows (`cards`) | 3,372 | 3,403 |
| Known copies (`sum(owned_min)`) | 5,426 | 5,480 |
| Source tabs in `source_sheet_rows` | 38 | 39 (adds "Photo Intake · Oct 24") |
| Projected abilities | 3,563 | 3,596 |
| Capability claims | 25,370 | 25,616 |
| Oracle ids | 3,371 | 3,402 |
| `rules_text` from the Oracle refresh | 3,369 | 3,400 |
| Candidate operations / contracts | 4,631 | 4,631 |

The intake added 54 copies of 50 names: 31 new rows and 19 incremented rows. Apart from `collection_row` positions, the rebuilt v0.1 `cards` table differs from the old one only on those 19 rows (owned, free and availability). The photographed card "Lifelong Friendship" (TLE #48) is stored under its Oracle name, Eladamri's Call.

## Oracle refresh

- New snapshot `refresh/oracle_refresh_2026-10-24_3ff6602d641a0899.jsonl`, from Scryfall bulk `oracle-cards-20261024090157.jsonl.gz` (updated 2026-10-24T09:01:57Z), converted to a JSON array.
- 3,402 matched and 1 unmatched. There are 208 discrepancies, the same cards as the 10-21 run. All 31 new cards are `identical`.
- Both snapshots are replayed. Each one opens its own QA items, so `qa_queue` has 424 rows (212 + 212).

## What the new cards don't have yet

The 31 new cards have no candidate operations, so they also have no contracts. The contracts come from the Sheet's "Mechanics · Operations" tab, which was extracted on 2026-10-11 and doesn't list them. They do have Oracle identity, rules text, roles, projections and capability claims. Contracts for them need a Mechanics extraction pass. Run it as its own step.

## Side effect of rebuilding v0.1 with the vendored parser

The 2026-10-20 v0.1 projections came from parser `mtg_eval_0.3.0:a178fc7d1893e43c`. A rebuild uses the vendored `0.3.0+kb2` (`0d2cb97fc3acb9ea`), which substitutes the full card name for `~`. Four contracts change their check results:

- Irma, Part-Time Mutant op001 moves from `ready_for_review` to `blocked`. Its C11 now finds a projection and reports dropped text.
- Brigid op002, Gogo op001 and Trystan op003 stay `blocked`, with warnings turned into failures.

The queue is now 1,606 `ready_for_review`, 3,021 `blocked` and 4 `quarantined`. The verification counts are unchanged: 4,631 identity, 4,623 rules text current, 418 lossless and 0 mechanically supported.

## Tests

The pinned counts in `test_v02.py`, `test_mtg_db.py` and `test_acceptance.py` (T1, T7) were updated to the numbers above. Results are in SOURCE_MANIFEST.json. Run the suites from the release folder.

## Rebuild

```
python build_mtg_db.py canonical_20261024.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T19:05:17.624Z --built-utc 2026-10-24T19:10:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
