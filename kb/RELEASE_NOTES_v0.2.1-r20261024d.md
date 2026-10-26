# MTG Card Knowledgebase v0.2.1, data refresh r20261024d

A data-only rebuild of v0.2.1 after the 2026-10-24 Mechanics extraction pass. The inventory is unchanged (same cards, copies and decks as r20261024c). What changed is the Sheet's Mechanics tabs: 330 new candidate operations for owned cards that had none. The schema, the drafter, the compiler and the overrides are unchanged.

- No contract was approved. The review overlay is still empty.
- Nothing was promoted to verified. Every new operation is a candidate.

## Inventory source

- The Sheet was edited before this build, under the archive-then-clone rule. The post-precon workbook is frozen in Drive `archive/` as "MTG Master Inventory — Canonical_20261024-2315Z_ARCHIVE" (formerly id `17ZkkmKS_ILM0twXlrmJRPuXAm6-WtfHkps-RuyUU0zk`).
- The working Sheet is now id `1N1xBUkL_aYKpPcR8WJJVpeicgE8A06dqeUBM-hUa3Xo` (Drive modified 2026-10-24T23:57:02.816Z). `inventory_adapter.py` and `vendor/mtg_eval/_adapter.py` carry the new id.
- The export is `canonical_20261024d.xlsx`, sha256 `d7a2d191…4bab4`.

## What the extraction pass did

- Scope: the 412 owned legal cards with zero rows in Mechanics · Operations (the 148 flagged in r20261024c plus older gaps).
- Source: the Oracle grammar layer (grammar 0.2.0 / semantics 0.1.1). Each ability's DIO contract was mapped onto the Sheet's 18 Operations columns; only hooks in the Sheet's 43-hook vocabulary were kept.
- Result: 330 operations on 266 cards. 146 cards produced nothing (keyword-only, vanilla, or basic lands). Existing operations were not touched.
- Status: 233 `extracted_candidate`, 97 `requires_manual_annotation`. Confidence: 161 medium, 169 low.
- Units: 151 new card rows; 115 existing rows had their operation counts updated.
- Review Queue: 169 new rows (all low-confidence ops), with kernel columns K:N filled.

| | r20261024c | r20261024d |
|---|---:|---:|
| Candidate operations / contracts | 4,631 | 4,961 |
| Lossless compiles | 418 | 446 |
| Quarantined contracts | 4 | 7 |
| Owned names with no operations | 412 (+3 placeholders) | 146 (+3 placeholders) |
| `qa_queue` rows | 848 | 1,060 |

The 3 newly quarantined contracts belong to the Offspring rows (Finch Formation, Rust-Shield Rampager, Thornplate Intimidator). Their Sheet rows point at token printings, the existing `sheet_error` reconciliation records quarantine them, and the evaluator reads Oracle text for them. Identity is still unconfirmed.

## Oracle refresh

- New snapshot `refresh/oracle_refresh_2026-10-24_ed02ffb54a5b1a9d.jsonl`, same Scryfall bulk as before. 3,519 matched, 1 unmatched, 208 discrepancies (unchanged).
- All five snapshots are replayed, so `qa_queue` grows by 212 again. This is replay duplication, not new problems.

## Tests

The pinned counts for candidate operations, contracts and verification rows were updated from 4,631 to 4,961. Run the suites from the release folder.

## Rebuild

```
python build_mtg_db.py canonical_20261024d.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T23:57:02.816Z --built-utc 2026-10-25T00:05:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
