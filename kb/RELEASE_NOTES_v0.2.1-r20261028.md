# MTG Card Knowledgebase v0.2.1, refresh r20261028

A classifier-only rebuild after the 2026-10-28 paired evaluation, where both arms called Golden Argosy Brigid's only board wipe. Kate's provenance audit (2026-10-28) traced it to the wipe role detector. The inventory input is unchanged: the same export as r20261024d (`d7a2d191…4bab4`). The schema, drafter, compiler, overrides and review overlay are unchanged too.

- No contract was approved. Nothing was promoted to verified.

## What changed

- `vendor/mtg_eval` is now 0.3.0+kb3. **kb patch 3** is in `semantics.py`, in `oracle_functions` and `wipe_scope_ok`. A mass-removal phrase no longer counts as `wipe` in three cases:
  - Its object is narrowed to the source's helpers or blockers ("that crewed it", "blocking it"), or to the controller's own side ("you control").
  - The same or the next sentence returns the objects to the battlefield (flicker).
  - It is `overload` on a spell with no spot removal.
- The effect on the whole collection is that exactly 3 cards lose their `wipe` Oracle claim, and no other capability changes:

| Card | Old match | Why it was wrong |
|---|---|---|
| Golden Argosy | exile each creature | exiles only its crew, and they come back at end step |
| Battle-Scarred Goblin | damage to each creature | only creatures blocking it |
| Weapon Surge | overload { | overload of a pump spell |

- Golden Argosy keeps its Sheet `Board wipe` tag as `unverified_tag_only`. That tag is wrong in the Sheet, but the Sheet is not edited without Zach.
- `capability_claims` goes from 26,499 to 26,494. The pin in `test_v02.py` is updated.
- `kbq.overlap()` now reports `sole_detected_candidates` ({role: {card, evidence}}) and `reviewed_role_counts`, replacing `single_source_roles`. Its evidence note now says the roles are detected candidates. mtgtools `context --deck` passes them on, with a caveat claim.

## Inventory source

Same export as r20261024d, so the build meta still names Sheet `1N1xBUkL…`. The live Sheet has since been archived and cloned (now `1f83bN…`, 2026-10-25). Its card data is unchanged.

## Rebuild

```
python build_mtg_db.py MTG_Master_Inventory_Canonical_export_20261024d.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T23:57:02.816Z --built-utc 2026-10-28T22:00:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
