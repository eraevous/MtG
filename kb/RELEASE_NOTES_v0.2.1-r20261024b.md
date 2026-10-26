# MTG Card Knowledgebase v0.2.1, data refresh r20261024b

A data-only rebuild of v0.2.1 after the second physical-card photo intake of 2026-10-24 (IMG_3875–3878). The schema, the drafter, the compiler and the overrides are unchanged.

- No contract was approved. The review overlay is still empty.
- No physical card was moved, and no deck allocation changed.

## Inventory source

- The Sheet was edited before this build, under the archive-then-clone rule. The post-batch-1 workbook is frozen in Drive `archive/` as "MTG Master Inventory — Canonical_20261024-2010Z_ARCHIVE" (id `1vAweCvOb371YNQOoDVjKRn1P83U_thk63WzvW1fRpVc`).
- The working Sheet is now id `1Jzdb0YOUbjLfzFrrCLFVdzBeY8eqRqe04LPotWFBXZc` (Drive modified 2026-10-24T20:21:33.975Z). `inventory_adapter.py` and `vendor/mtg_eval/_adapter.py` carry the new id.
- The export is `canonical_20261024b.xlsx`, sha256 `0f4e4b64…2895`.

| | r20261024 | r20261024b |
|---|---:|---:|
| Collection rows (`cards`) | 3,403 | 3,460 |
| Known copies (`sum(owned_min)`) | 5,480 | 5,702 |
| Source tabs in `source_sheet_rows` | 39 | 40 (adds "Photo Intake · Oct 24 B") |
| Projected abilities | 3,596 | 3,653 |
| Capability claims | 25,616 | 26,071 |
| Oracle ids | 3,402 | 3,459 |
| `rules_text` from the Oracle refresh | 3,400 | 3,457 |
| Candidate operations / contracts | 4,631 | 4,631 |

The intake added 222 copies of 193 names (199 printings): 57 new rows (58 copies) and 136 incremented rows (164 copies, including 12 basic lands). Every validation check result is identical to r20261024.

## Oracle refresh

- New snapshot `refresh/oracle_refresh_2026-10-24_4699ccaa01b83aca.jsonl`, from the same Scryfall bulk as r20261024 (`oracle-cards-20261024090157`, converted to a JSON array). All 199 photographed printings have their oracle_id in that bulk.
- 3,459 matched and 1 unmatched, 208 discrepancies (the same cards as before).
- All three snapshots are replayed, and each one opens its own QA items, so `qa_queue` now has 636 rows (3 × 212). This is replay duplication, not new problems.

## What the new cards don't have yet

The 57 new cards have no candidate operations, so they also have no contracts. Together with the 31 from r20261024 that makes 88 owned cards waiting for a Mechanics extraction pass ("Mechanics · Operations" was extracted on 2026-10-11). They do have Oracle identity, rules text, roles, projections and capability claims.

## Tests

The pinned counts in `test_v02.py`, `test_mtg_db.py` and `test_acceptance.py` (T1, T7) were updated to the numbers above. Run the suites from the release folder.

## Rebuild

```
python build_mtg_db.py canonical_20261024b.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T20:21:33.975Z --built-utc 2026-10-24T20:30:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
