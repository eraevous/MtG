# Collection update, 2026-10-24

After the first photo intake (IMG_3874), 31 new cards were added to the Sheet and to the KB (`sqlite-kb`, release v0.2.1-r20261024). All 31 were already in this corpus, so nothing was re-parsed. The update does three things:

- `card.in_collection` = 1, `scope` = collection and `kb_card_name` are set for the 31 oracle_ids. There are now 3,399 collection oracle_ids, up from 3,368.
- `frame.n_cards`, `n_collection_parts` and `n_collection_cards` are recomputed with the same SQL as `build.py`.
- A `collection_update_20261024` row is added to `source_manifest`.

The corpus file, templates, concepts and ability contracts did not change. `tests.py` passes (11 tests).

The pre-update database is `archive/grammar_layer_v0.2_20261024T1915Z_ARCHIVE.sqlite`.

The new metrics are in `metrics_r20261024.json`. `metrics.json` and REPORT.md still show the 10-22 numbers.

| Metric | Before | After |
|---|---:|---:|
| Collection abilities | 6,858 | 6,932 |
| Parts complete | 90.1% | 90.0% |
| Cards with every ability complete | 2,254 | 2,272 |
| Distinct frames used | 2,269 | 2,286 |

The review CSVs and `discovery/collection_loops.csv` were not regenerated, because `review/template_review_sample.csv` is with Zach for review. Regenerate them with `review.py export` and `discovery.py` when that review is done.

## Second update, 2026-10-24 (batch 2)

After the second photo intake (IMG_3875–3878), 57 more new cards were added to the Sheet and to the KB (release v0.2.1-r20261024b). All 57 were already in this corpus. The same three steps were applied, with a `collection_update_20261024b` manifest row, and `kb_external_oracle_run` now points at snapshot `4699ccaa01b83aca`. There are now 3,456 collection oracle_ids. `tests.py` passes (11 tests).

The pre-update database is `archive/grammar_layer_v0.2_20261024T2032Z_ARCHIVE.sqlite`. The new metrics are in `metrics_r20261024b.json`.

| Metric | After batch 1 | After batch 2 |
|---|---:|---:|
| Collection abilities | 6,932 | 7,042 |
| Abilities parsed complete | 5,681 | 5,772 |
| Cards with every ability complete | 2,272 | 2,312 |
| Distinct frames used | 2,286 | 2,307 |
| Collection abilities with no matching contract | 629 | 705 |

The review CSVs are still not regenerated, for the same reason as above.

## Third update, 2026-10-24 (Token Triumph precon)

The Token Triumph precon (Starter Commander Decks, set SCD, commander Emmara, Soul of the Accord) added 60 new cards to the Sheet and to the KB (release v0.2.1-r20261024c). All 60 were already in this corpus. The same three steps were applied, with a `collection_update_20261024c` manifest row, and `kb_external_oracle_run` now points at snapshot `bbdd0ad27a59e47d`. There are now 3,516 collection oracle_ids. `tests.py` passes (11 tests).

The pre-update database is `archive/grammar_layer_v0.2_20261024T2253Z_ARCHIVE.sqlite`. The new metrics are in `metrics_r20261024c.json`.

| Metric | After batch 2 | After Token Triumph |
|---|---:|---:|
| Collection abilities | 7,042 | 7,145 |
| Abilities parsed complete | 5,772 (82.0%) | 5,864 (82.1%) |
| Cards with every ability complete | 2,312 | 2,362 |
| Distinct frames used | 2,307 | 2,318 |
| Collection abilities with no matching contract | 705 | 789 |

The review CSVs are still not regenerated, for the same reason as above.
