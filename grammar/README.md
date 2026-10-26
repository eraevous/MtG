# Grammar layer: Oracle text → templates → DIO concepts

This folder holds the language layer between Oracle text and DIO v3.1.1. It is built from the whole Scryfall
Oracle corpus and applied to Zach's collection. Kate's 2026-10-21 pilot came first. This is the full version of
that pilot's data model.

The findings are in [REPORT.md](REPORT.md). This file says how the parts fit and how to rebuild them.

## What is here

| File | What it is |
|---|---|
| `grammar_layer.sqlite` | Everything: cards, abilities, parts, templates, concepts, edges, frame semantics, ability contracts, discovery, sets, rulings, claims, tests, the review table |
| `DATA_DICTIONARY.md` | **Definitions:** every review column and code, how concept and hook names work, and a glossary of every concept. Regenerate it with `python3 -I dictionary.py grammar_layer.sqlite > DATA_DICTIONARY.md` |
| `review/template_review_sample.csv` | **Start here.** 74 representative templates, about 4 per mechanical class, one row per template with its whole semantics |
| `review/template_review_top300.csv`, `template_review_collection.csv` | The same format for the 300 most-used templates and for all of the collection's templates |
| `review/template_inventory_corpus.csv` | Every template in the corpus, with counts (browse only) |
| `discovery/collection_loops.csv` | Two-card loop candidates in the collection, with certainty |
| `validation/` | Blind sample, held-out freeze and grading, per-set summary, claims and tests, disagreement report |
| `metrics.json` | The grammar numbers in REPORT.md, written by `metrics.py` |
| `grammar.py`, `lexicon.py` | Ability boundaries, kinds, parts, frames with typed slots; closed word classes |
| `concepts.py` | Concepts (DIO-facing), the rules that propose edges, coordination and replacement composites |
| `semantics.py` | Frame semantics, slot→qualifier binding, ability contracts (DIO §5 operations) |
| `discovery.py` | produces / observes / needs per ability, flow edges and loops |
| `fetch_sets.py`, `validation.py`, `set_summary.py` | Set fetch, rulings ingestion, claims, tests, statuses, families |
| `build.py`, `metrics.py`, `review.py`, `tests.py` | Build, measure, review round trip, acceptance tests |
| `data/sources/SOURCE_MANIFEST.json`, `data/sets/`, `data/rulings/` | Input files with their shas |
| `archive/` | The v0.1 database and review files |

## The four levels

```
card → ability → part → frame (template) ⇄ concept (DIO)
```

- **Ability.** One rules ability. Its kind is one of: keyword, triggered, activated, spell, static, replacement,
  mode, loyalty, chapter, additional_cost. Quoted abilities that a card grants become nested abilities with
  `granted_by` set. Reminder text is stripped but kept on the ability (`reminders_json`).
- **Part.** One grammatical role inside an ability. The roles are: cost, trigger_event, condition, effect,
  static, amplifier, duration, restriction, link (if you do, then, when you do), mode_header, replacement,
  delayed_trigger, timing and keyword.
- **Frame.** The part's text with typed slots in place of the details. The slots are `<obj.q|target|each|all|another|upto|ref|bare|attached>`,
  `<player.you|each|target|ref|q>`, `<self>`, `<ref>`, `<zone>`, `<mana>`, `<n>`, `<pt>`, `<counter>`, `<kw>`,
  `<color>`, `<energy>`, `<tap_symbol>` and `<granted_ability>`. The value of each slot in each occurrence is
  stored in `part.bindings_json`. For example, `{W}{B}` and `{W}`,`{B}` stay distinct.
- **Concept.** A DIO-facing node. Its semantic type is one of: operation, event, state_predicate, cost,
  modifier, process or keyword_macro. Each concept carries its DIO reference and its `dio_status`:
  `ontology_defined`, `addendum_pending` (it depends on A1–A7) or `language_layer` (a grouping label, not a new
  primitive).

Events, operations and state predicates are separate concepts, even when they share a hook id. For example:

- `ev.permanent.tap` is "became tapped"
- `op.permanent.tap` is "tap it"
- `st.object_status` is "is tapped"

Operations carry an `event_intent`. For example, `op.permanent.destroy` intends `permanent.destroy`. They never
claim the confirmed event (`permanent.dies`), because that is a rules question.

**Completeness** is measured with span accounting:

- `complete`: the rules account for every word of the frame.
- `partial`: some concept was found, but words are left over, or only a whole-part catch rule matched.
- `none`: no rule matched.

## Rebuild

```bash
# 1. the corpus (allowed hosts: api.scryfall.com, data.scryfall.io)
curl -sS https://api.scryfall.com/bulk-data/oracle-cards     # read jsonl_download_uri
curl -sS -o oracle-cards.jsonl.gz <jsonl_download_uri>
# 2. build (about 55 s), export the review files, measure, discover
python3 -I build.py --oracle oracle-cards.jsonl.gz --kb ../sqlite-kb/mtg_cards_v0.2.sqlite --out grammar_layer.sqlite
python3 -I review.py export grammar_layer.sqlite review/
python3 -I metrics.py grammar_layer.sqlite --kb ../sqlite-kb/mtg_cards_v0.2.sqlite > metrics.json
python3 -I discovery.py grammar_layer.sqlite --out discovery/
python3 -I tests.py
# 3. validation: sets are cached in data/sets/ (fetch_sets.py), rulings are one bulk file
python3 -I fetch_sets.py tla tle eoe eoc tmt tmc trk trc     # skips sets already cached
python3 -I validation.py grammar_layer.sqlite --rulings data/rulings/rulings-20261021210033.jsonl.gz \
    --sets tla tle eoe eoc tmt tmc --heldout trk trc --frozen validation/heldout_trk_trc_predictions.json --out validation/
python3 -I set_summary.py grammar_layer.sqlite > validation/per_set_summary.json
```

For a new held-out set, leave out `--frozen`. validation.py then freezes that set's contracts before it reads any
ruling. Once rulings have been read, always pass `--frozen` with the original file, because a freeze made after
reading rulings is not a held-out test.

Both inputs are read-only. The collection is the set of oracle_ids in the KB's `external_oracle` table (refresh run
`7e517de93bb47238`). The corpus leaves out art series, tokens, emblems, planes, schemes, Vanguard, Jumpstart front
cards, memorabilia, Un-sets, Alchemy and non-paper cards. Collection cards are always kept.

## Reviewing

Open `review/template_review_sample.csv`. Each row is one template with its complete semantics (the `semantics`
column), for example `TRIGGER any of [battlefield.enter | attacker.declared]` or
`REPLACEMENT[substitute] permanent.dies -> exile.enter`. Fill in `verdict`:

- `approve`: the template means exactly this.
- `reject`: it doesn't.
- `fix`: put the right concept ids in `corrected_concepts`, separated by spaces. The semantics are recomposed from them.

Then run:

```bash
python3 -I review.py apply grammar_layer.sqlite reviewed.csv --reviewer Zach
python3 -I metrics.py grammar_layer.sqlite > metrics.json      # reviewed_complete goes up
```

Each verdict is stored with the SHA-256 of the template text and of its semantics. If a later version changes
either one, the verdict goes stale instead of carrying over. Frame ids can change between builds, but the shas do not.

Approving a template approves the construction, not every card that uses it. An inner "if", an "instead" or an
odd target restriction is its own part with its own template, so an exception lands in its own row.

## Useful queries

```sql
-- every owned card that uses a template, with the exact text
SELECT c.name, p.surface FROM part p JOIN ability a USING(ability_id) JOIN card c USING(oracle_id)
 WHERE p.frame_id = 26 AND c.in_collection = 1;
-- what an owned card's abilities decompose into
SELECT a.kind, p.role, f.frame_text, group_concat(e.concept_id) FROM card c JOIN ability a USING(oracle_id)
  JOIN part p USING(ability_id) JOIN frame f USING(frame_id) LEFT JOIN frame_concept_edge e USING(frame_id)
 WHERE c.name = 'Zulaport Cutthroat' GROUP BY p.part_id ORDER BY a.ordinal, p.ordinal;
-- templates mapped to a concept, by collection impact
SELECT f.frame_text, f.role, f.n_collection_cards FROM frame_concept_edge e JOIN frame f USING(frame_id)
 WHERE e.concept_id = 'ev.permanent.sacrifice' ORDER BY f.n_collection_cards DESC;
```
