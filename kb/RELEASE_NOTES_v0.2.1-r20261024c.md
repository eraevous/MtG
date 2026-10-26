# MTG Card Knowledgebase v0.2.1, data refresh r20261024c

A data-only rebuild of v0.2.1 after adding the Token Triumph precon on 2026-10-24. Token Triumph is a Starter Commander Deck (set SCD), GW Selesnya, with Emmara, Soul of the Accord as commander. The schema, the drafter, the compiler and the overrides are unchanged.

- No contract was approved. The review overlay is still empty.
- One deck was added: "Token Triumph" is an intact, allocated current deck, following the Blight Curse precedent. No other allocation changed.

## Inventory source

- The Sheet was edited before this build, under the archive-then-clone rule. The post-batch-2 workbook is frozen in Drive `archive/` as "MTG Master Inventory — Canonical_20261024-2233Z_ARCHIVE" (id `1Jzdb0YOUbjLfzFrrCLFVdzBeY8eqRqe04LPotWFBXZc`).
- The working Sheet is now id `17ZkkmKS_ILM0twXlrmJRPuXAm6-WtfHkps-RuyUU0zk` (Drive modified 2026-10-24T22:42:35.194Z). `inventory_adapter.py` and `vendor/mtg_eval/_adapter.py` carry the new id.
- The export is `canonical_20261024c.xlsx`, sha256 `f890ce2a…bbbd`.
- The card list is the official Wizards decklist: https://magic.wizards.com/en/news/announcements/starter-commander-decks-decklists-2022-10-20

| | r20261024b | r20261024c |
|---|---:|---:|
| Collection rows (`cards`) | 3,460 | 3,520 |
| Known copies (`sum(owned_min)`) | 5,702 | 5,802 |
| Current 100-card decks | 12 | 13 (adds Token Triumph) |
| Source tabs in `source_sheet_rows` | 40 | 41 (adds "New · Token Triumph") |
| Projected abilities | 3,653 | 3,709 |
| Capability claims | 26,071 | 26,499 |
| Oracle ids | 3,459 | 3,519 |
| `rules_text` from the Oracle refresh | 3,457 | 3,517 |
| Candidate operations / contracts | 4,631 | 4,631 |

The precon added 100 copies:

- 60 new rows.
- 11 existing names incremented by 1 each.
- Forest +15 and Plains +14.

All 100 copies are allocated to Token Triumph. Every non-basic card has exactly one SCD printing on Scryfall. The SCD basics have four arts each (Forest #349–352, Plains #333–336), and which arts are in the box is not established.

## Oracle refresh

- New snapshot `refresh/oracle_refresh_2026-10-24_bbdd0ad27a59e47d.jsonl`. It uses the same Scryfall bulk as r20261024b (`oracle-cards-20261024090157`).
- The snapshot has 3,519 matched cards, 1 unmatched card and 208 discrepancies. These are the same cards as before, so none of the new cards has a discrepancy.
- All four snapshots are replayed, and each one opens its own QA items. `qa_queue` now has 848 rows (4 × 212). This is replay duplication, not new problems.

## What the new cards don't have yet

The 60 new cards have no candidate operations, so they also have no contracts. Adding them to the 88 from r20261024 and r20261024b gives 148 owned cards waiting for a Mechanics extraction pass. The new cards do have Oracle identity, rules text, roles, projections and capability claims.

## Tests

The pinned counts in `test_v02.py`, `test_mtg_db.py` and `test_acceptance.py` were updated to the numbers above, including 13 decks and 41 tabs. Run the suites from the release folder.

## Rebuild

```
python build_mtg_db.py canonical_20261024c.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T22:42:35.194Z --built-utc 2026-10-24T22:50:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
