# MTG Card Knowledgebase v0.2.1, refresh r20261030

This is a classifier-only rebuild after role audit v0.2 (`evaluations/role_detector_audit_v0.2/`). In that audit, two of the three confirmed misses on untagged cards were roles that live only in reminder text, which the detector strips. Zach approved the mapping work on 2026-10-29 and the release on 2026-10-30.

What is unchanged:
- The inventory input: the same export as r20261024d (`d7a2d191…4bab4`).
- The schema, drafter, compiler, overrides and review overlay.

No contract was approved, and nothing was promoted to verified.

## What changed

- `vendor/mtg_eval` is now 0.3.0+kb4, and `derivation_version` is `kbfacts-0.2.1/mtg_eval_0.3.0+kb4`.
- **kb patch 4** (`semantics.py`, `PREDEFINED_TOKENS`, `TOKEN_KEYWORDS`) maps by name, and reminder text stays stripped. It covers two things:
  - **Predefined tokens the card itself creates.** "Its controller creates" or "target player creates" does not count.

    | Token | Roles |
    |---|---|
    | Treasure, Gold | ramp, fixing |
    | Lander | ramp, fixing, land_drop |
    | Powerstone | ramp |
    | Clue | draw |
    | Food | lifegain_source |

  - **Token-making keywords:**
    - These map to token_maker: incubate, afterlife, living weapon, for Mirrodin!, mobilize, offspring, fabricate, squad, embalm, eternalize, myriad.
    - Extort maps to closer.
- **Deliberately not mapped:**
  - Junk, because impulse is not draw (D-0011).
  - Blood, because loot is not draw (D-0010).
  - Map.
  - Populate and other copies (D-0008, D-0011).
- **Effect on the whole collection** (the full list is in `evaluations/token_role_mapping_v0.1/claim_diff.csv`):
  - 38 new semantic claims.
  - 63 tag-only claims now backed by Oracle text.
  - One new contradiction (Tokka & Rahzar, where a hand label says not fixing).
  - No claims lost.
- `capability_claims` goes from 26,494 to 26,634, and the pin in `test_v02.py` is updated.

## Inventory source

The export is the same as r20261024d, so the build meta still names Sheet `1N1xBUkL…`. The live Sheet is `1f83bN…`, and its card data is unchanged.

## Rebuild

```
python build_mtg_db.py MTG_Master_Inventory_Canonical_export_20261024d.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T23:57:02.816Z --built-utc 2026-10-30T14:30:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
