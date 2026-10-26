# MTG Portable Card Knowledgebase — v0.1 (2026-10-20)

**This is the persisted card/collection/semantic index that should have preceded `mtg_eval`.** It is built from the *working* canonical inventory, not from an archive, and is meant to become the simulator's default, read-only card-data source. SQLite is the primary deliverable; JSONL exports are included for cross-language use. No card purchases, physical swaps, or workbook edits occurred.

## Contents

- **`mtg_cards.sqlite`** — complete portable SQLite database with 3,372 Collection records, 3,364 confirmed-owned card names, 5,426 known copies, full custody/deck allocations, stored Oracle text and inventory roles, **4,631 legacy operation candidates**, 3,562 cached 0.3.0 simulator ability projections, **25,363 capability claims** across multiple evidence sources, and queued review priorities. Every card's typed statics and unread clauses are retained.
- **`schema.sql`** — normalized tables and indexes with ownership integrity constraints, SQLite full-text card search, inventory queries, and audit trail.
- **`jsonl/`** — newline-delimited JSON exports for cards, abilities, candidate operations, claims, typed profiles and allocations. The equivalent JSON is also available directly via the database.
- **`source_sheet_rows`** in SQLite — all **38 source workbook tabs** as cell-value snapshots (17,707 populated rows) for reference/reconciliation. **This is NOT a formula/style-preserving XLSX backup**; keep your frozen archived workbooks.
- **`reference_documents`** — DIO v3.1.1, its addendum, DBEP v1.2 addendum, vocabulary registry, and Kairos–GATE text with hashes. `ontology_domains` contains 78 typed domain definitions.
- **`build_mtg_db.py`**, **`inventory_adapter.py`**, **`vendor/mtg_eval/`** — reproducible stdlib builder; vendor is Claude's 0.3.0 parsing implementation, version-stamped.
- **`mtgdb.py`** — fast portable read-only CLI (does NOT require the source XLSX).
- **`sqlite_bridge.py`** — compatibility layer for `mtg_eval` 0.3.0: reads card/deck facts and cached roles/abilities from SQLite, avoiding the 0.3.0 ability reparse for the turn engine; **does not auto-execute unverified Mechanics candidates**.
- **`overrides/verified_reviews.jsonl`** — empty by default, deliberately. Manual reviews must include evidence and card-text hash; rebuilding the DB never confers verification just because a pattern matched.

## Fast queries

```bash
python mtgdb.py stats
python mtgdb.py card 'The Necrobloom'
python mtgdb.py abilities 'Avenger of Zendikar'
python mtgdb.py operations 'The Necrobloom'
python mtgdb.py deck Necrobloom
python mtgdb.py search 'dredge'
python mtgdb.py role 'token_maker' --free --limit 20
python mtgdb.py review --deck Necrobloom --limit 20
python mtgdb.py ontology 'hook.kind'
python mtgdb.py sql 'SELECT card_name, free FROM cards WHERE free > 0 AND color_identity = "BG" LIMIT 10'
```

**To load in Python:**

```python
import sqlite3
c = sqlite3.connect('file:mtg_cards.sqlite?mode=ro', uri=True)
print(c.execute('SELECT card_name, oracle_text FROM cards WHERE card_name=?', ('The Necrobloom',)).fetchone())
```

**Bridge to the 0.3.0 evaluator** (uses the code in `vendor/mtg_eval`):

```python
from sqlite_bridge import SQLiteEvaluator
from mtg_eval.report import render  # or work directly with Result
engine = SQLiteEvaluator('mtg_cards.sqlite', games=50, engine_games=5)
result = engine.deck('Necrobloom')
print(result['title'], len(result['sections']))
```

`SQLiteEvaluator` is an integration proof for the current 0.3.0 API, not a replacement for a verified DIO operation compiler. Some API routines outside the engine still perform lexical checks or scenario inference; those should subsequently be redirected to database records instead of repeated work.

## Refresh procedure, preserving archives

1. Keep the working canonical: https://docs.google.com/spreadsheets/d/1wv-uSSSlTIRAJp5qInwq0oppGUOX49_D2ni3vAnESxU/edit
2. For **major structural changes**, first create and verify a frozen timestamped workbook in the Archive folder. Archives must never be used as the live build input.
3. Export the **working** Google Sheet to a local `.xlsx` file. The included DB is based on a mounted snapshot of that canonical workbook; the live sheet metadata was verified as last modified on 2026-10-15 at 19:03:42 UTC.
4. Regenerate atomically to a fresh output path (do not alter the source XLSX):

```bash
PYTHONHASHSEED=0 python build_mtg_db.py /path/to/current_live_export.xlsx --db mtg_cards_NEW.sqlite --jsonl jsonl_NEW
python -m unittest -v test_mtg_db.py
```

5. Verify owned quantities, all active 100-card decks, zero overallocations, source SHA-256, operation counts and projection-version changes. Promote the regenerated DB only after checks pass. Update the version manifest and retain the previous DB alongside the frozen source reference for reproducibility. For a **parser change**, rebuild the derived records but preserve reviewed overrides separately and invalidate reviews when their source Oracle text hash changes.

## Evidence hierarchy (CRITICAL)

1. **Collection / Deck Allocations** — authority for recorded ownership and physical custody.
2. **Stored Oracle text** — recorded source text, not freshly verified against Scryfall today.
3. **Human-reviewed contract** — requires explicit review, evidence, card text hash and review status; none automatically asserted here.
4. **`candidate_operations`** — 4,631 unverified candidates, preserving source clauses/gates/outputs as found in the existing workbook.
5. **`projected_abilities`** — 0.3.0 parser outputs, **cached** as structured JSON with unparsed fragments and a pinned parser version. They are **not verified DIO contracts**.
6. **`capability_claims`** — source-specific inventory hints, machine pattern matches, and labels, with status. A `machine_supported` role is evidence of a text match, **not proof the role will work in a real scenario**.

The parser's designation `machine_parsed` means it had no **unread fragments within its own vocabulary**. That is not a guarantee that it recognized every operative rule. At build time, 503 cards are `machine_parsed`, 2,834 `partial`, and 35 have no projection; the 4,631 candidate operations still have 0 formal verification records. The DB makes these **gaps observable and addressable rather than rediscovered**.

## Decisions that remain for development

- Establish a reviewed **DIO operation compiler** with actionable hooks, typed event predicates, costs, targets, source/destination zones, replacement effects, magnitude and cadence. Prefer reusable operation templates. Reject uncertain operations rather than invent semantics.
- Bulk-prioritize review by active commander/deck presence and impact on engines. `review_backlog` is a **triage heuristic**. Prioritize correcting high-impact interpretations and false positives, not merely maximizing the number of fully-parsed cards.
- Define stable card identifiers (prefer official Oracle IDs when available) and full face/printing metadata for any collision or multi-face legality questions; current primary key is the inventory's canonical card name. Edition/printing tracking is retained as raw sheet rows pending normalized curation.
- Make inventory/deck/role queries default to SQLite. Move additional static reports from runtime regex to persisted records; preserve the original workbook as master and SQLite as a derived, regenerable artifact.
- Verify operational conclusions by explicit scenario simulation and held-out physical games; do not equate parsed clauses with accurate gameplay.

## Tests

`python -m unittest -v test_mtg_db.py` validates integrity, all 12 decks, ownership, all-source-tab capture, no fake verification, full-text search, cached parser parity on representative cards, and a real `SQLiteEvaluator.deck('Necrobloom')` call.
