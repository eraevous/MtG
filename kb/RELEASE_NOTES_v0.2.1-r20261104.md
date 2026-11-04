# MTG Card Knowledgebase v0.2.1, refresh r20261104: Sagas, faces and token copies

Zach asked for this release on 2026-11-04 ("let's fix the data layer"). It came after a ChatGPT build of Steph's Terra deck (C-024). The deck's central question is whether Terra's token copy of a Summon Saga gets its chapters again. The KB could not answer it, for three reasons:
- the clauses on Terra's faces were not located on a face;
- chapter abilities had no trigger shape;
- a token copy did not record what it copies.

What is unchanged:
- The inventory input is the same export as r20261024d and r20261031 (`d7a2d191…4bab4`).
- The Oracle refresh, overrides, review overlay, scenarios and compiler are unchanged.
- Contract and capability-claim counts are unchanged (4,961 and 26,634).

No contract was approved, and nothing was promoted to verified. Every new reading is drafted, not reviewed (`candidate`).

## What changed (drafter contract-drafter-0.6.0, new `sagas.py` saga-copy-0.1.0)

- **Faces from Oracle.** When an inventory row's text is not split by face (no `//` lines), the drafter now finds the clause in the Oracle refresh faces (`card_faces`, `face_source = 'scryfall'`, the rules authority). `source_unit.face_source` says which was used.
  - C05_face fails: 180 → 5 contracts.
- **Printed costs.** When an activated ability's row records no payment, the cost is read from the clause before the colon ("Trance — {4}{R}{G}, {T}: ..."). `initiation.cost.payment_source` says `row` or `clause`.
  - C07_costs fails: 63 → 18. 53 contracts take their cost from the clause.
- **Saga chapters.** A clause on a Saga face that starts with chapter numerals is a triggered ability (CR 714.2b). This holds even where the row called it `continuous` (9 rows did).
  - The contract gets a trigger group: `counter.put`, counter kind `lore`, subject `this`, the chapter numbers, and the condition "for each chapter N listed, the lore count goes from below N to N or more" (CR 714.2c).
  - It also gets a `saga` block: chapter numbers, chapter name ("Crescent Fang"), every chapter on the face, the final chapter, read ahead, and the lifecycle (enters with one lore counter, one more after the draw step, sacrificed after the final chapter: CR 714.3a, 714.3b, 714.4).
  - The counter facets add `listen_put lore`, and `hook_subject` is `self`.
  - 41 chapter contracts on 21 Saga cards.
- **Token copies.** `token.create` items carry `copy_of`. Its source is `target`, `self`, `referent` ("a copy of it") or `chosen` (populate, "a creature token you control"). It also records the object filter, any `except` clause, and the rule (CR 707.2: the token has the copied object's abilities).
  - Counters put "on it" right after the copy are a separate `counter.put` with `recipient: created_token`, amount, up-to and condition. Terra: lore, up to 3, "if it's a Saga".
  - That condition is bound, so it no longer counts as an unbound "if" (C09).
  - 36 contracts record a copy.
- **C06_source_annotation gate (proposed, D-0025).** A row the Sheet marks `requires_manual_annotation` still fails C06, except when it is a chapter ability whose trigger the saga drafter supplied. That case is a `warn` that names the drafter and says the contract is not reviewed. This moves those contracts from `blocked` to `ready_for_review`, which means a person can review them. It does not mean anyone has reviewed them.
  - C06 fails: 350 → 320.
- Overall:
  - Contracts with a failing check: 3,220 → 3,113.
  - Queue: blocked 3,216 → 3,109; ready_for_review 1,738 → 1,845; quarantined 7.
  - All 22 owned Sagas: contracts failing a check went from 42 to 17.

## mtgtools (reads the new fields)

- A copy producer links to the copied card's own abilities:
  - `copy_enters`: the copy's own enter trigger fires (Terra copies Sidequest: Raise a Chocobo, so a Bird).
  - `copy_chapters`: chapters reached on the copy, worked out from the lore counters. Terra copying Summon: Choco/Mog gives "chapters 1, 2, 3, 4 of 4". Fenrir gives 1, 2, 3 of 3.
  - `copy_type`: a copy of an enchantment is an enchantment entering (Elvish Archivist). This is compatible only when the observer's filter names a type.
- Counters that go on the created token are no longer read as going on the producer (Terra's chapter IV is not fed by its own I–III).

## Known limits

- 13 of the 17 remaining Saga failures are conditions or modes no drafter binds yet: "if you control the creature with the greatest power", "unless", modal chapters.
- 4 are effects the hook registry has no identifier for:
  - team pumps such as Choco/Mog's "+1/+0" (49 contracts in the collection have the same blank);
  - "can't block / can't attack";
  - "look at the top seven, put one into your hand".
  Adding effect identifiers is a registry/DIO change (P-09), not a drafter change.
- C11_executable_shape (2,198 fails) comes from the vendored mtg_eval 0.3.0 projection, which is pinned (T7). Terra's mill-five and Trance abilities still fail it. That is a separate piece of work.
- `transform` and `return transformed` are not yet a face-aware event. Links still say "which face it enters on is not recorded".
- A copy made by populate never links to a card in the collection (it copies a token).

## Rebuild

```
python build_mtg_db.py MTG_Master_Inventory_Canonical_export_20261024d.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T23:57:02.816Z --built-utc 2026-11-04T04:00:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
