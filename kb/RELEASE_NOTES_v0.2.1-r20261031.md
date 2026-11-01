# MTG Card Knowledgebase v0.2.1, refresh r20261031: counter identity

Zach asked for this release on 2026-10-31, after the Blight Curse → TMNT decommission test (C-015, C-016). Contracts had recorded "counters" without saying which counters, so a +1/+1 producer looked like it fed a -1/-1 listener, and keyword cards such as persist creatures had no counter reading at all.

What is unchanged:
- The inventory input: the same export as r20261024d (`d7a2d191…4bab4`), rebuilt into a fresh v0.1 database.
- The schema, compiler, Oracle refresh, overrides and review overlay. Contract and capability-claim counts are unchanged (4,961 and 26,634).

No contract was approved, and nothing was promoted to verified. Every counter facet is **drafted, not reviewed** (`candidate`).

## What changed

- **New `counters.py`** (counters-0.1.0, card-counters-0.1.0) reads each counter mention as a facet `{role, kind, holder}`:
  - kind: `+1/+1`, `-1/-1`, a named kind (`nest`, `stun`, `poison`, `lore`, ...), `any` for generic wording ("a counter", "each counter"), or `present_kinds` for proliferate and "double the number of each kind".
  - role: put, remove, move, enters_with, listen_put, listen_remove, measure, require, modify_put (replacements such as Loading Zone and Hardened Scales), proliferate, condition_put (history such as Lasting Tarfire's "if you put a counter ... this turn"), mention.
  - holder: permanent, player (poison, energy, experience) or unread.
  - DIO v3.1.1's state table says a counter's sign must not be assumed. The facets keep the kind and leave the sign to the reader.
- **Contracts** (drafter contract-drafter-0.5.0): each contract carries `counters.facets`. `counter.put` produces name their kinds, proliferate becomes a `counter.put` of `present_kinds`, removal becomes `counter.remove`, triggers carry `counter_kind` and `counter_holder` qualifiers, and the query index carries the facets. A conditional that only reads history no longer feeds anything.
  - Queue: blocked 3,226 → 3,216, ready_for_review 1,728 → 1,738. Ten counter-listener contracts (Fathom Mage, Hapatra, Aeon Chronicler, ...) now pass the hook check.
  - 705 contracts have counter facets.
- **Card-level counter facets** in `derived_facts` (`fact_kind = 'counter_facets'`, 632 cards). They come from the whole Oracle text and cover what no operation contract holds:
  - static "enters with" lines (Reaping Willow);
  - keyword macros (persist, undying, wither, infect, toxic, modular, graft, riot, unleash, bloodthirst, evolve, scavenge, suspend, vanishing, fading, sagas, ...), drafted from the Comprehensive Rules' definitions;
  - granted keywords ("as though its source had wither").
  - `derived_facts` goes from 38,726 to 39,358.
- **Order-of-operations note** on the 24 cards that enter with -1/-1 counters. A replacement that changes the number of counters (Loading Zone doubles them) applies as the object enters (CR 614.1c). If toughness is then 0 or less, the creature dies at the next state-based check (704.5f) before anyone can act, so +1/+1 counters added later cannot cancel the -1/-1 counters (704.5q) in time. Counters it has at the same moment do cancel, because the checks are simultaneous (704.3).
- **mtgtools** reads the new fields: counter links are compatible, incompatible or unresolved by kind; `card` shows the counter facets and the order note; `release` lists each candidate's -1/-1 roles instead of a lexical flag.

## Known limits

- 19 contract facets have no readable holder, mostly time counters.
- "Remove a counter" from a cost and "remove a -1/-1 counter" are told apart, but which permanent pays a generic cost is decided at play, not here.
- Keyword facets come from a list in `counters.py`. A keyword missing from the list gets no facet.

## Rebuild

```
python build_mtg_db.py MTG_Master_Inventory_Canonical_export_20261024d.xlsx --db mtg_cards.sqlite
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-24T23:57:02.816Z --built-utc 2026-10-31T21:00:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```
