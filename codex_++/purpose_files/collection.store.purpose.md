# Module: collection.store
> Bring-your-own collection database: import a collection (CSV, Sheet .xlsx, decklists) into one SQLite file, fill card data from Scryfall, and let the evaluator and KB build read it in place of the canonical Sheet export.

@ai-path: collection.store
@ai-source-file: collection/mtgcollection.py
@ai-role: adapter
@ai-intent: "Hold one person's ownership and deck allocation in a SQLite collection database that downstream tools read exactly like the canonical Sheet export."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: low (a person's card collection and an optional owner label; databases are gitignored)
@ai-dependencies: ext:kb/vendor/mtg_eval
@ai-used-by: evaluator.cli, kb build_mtg_db (through kb/vendor/mtg_eval/collection_db.py)
@ai-contracts: P-01, P-05
@ai-semantic-role: candidate-source

### Inputs and outputs
| Direction | What |
|---|---|
| In | Collection CSV (Moxfield, Archidekt, ManaBox, Deckbox or hand-made), Sheet .xlsx export (canonical layout or one tab), text decklists, Scryfall Oracle data (bulk file or API) |
| Out | `collection/schema.sql` database; read back by `kb/vendor/mtg_eval/collection_db.py` as Collection / Deck Allocations rows with the Sheet's headers |

### Risks, invariants and known gaps
- Owned, in-deck and free counts are views over holdings and allocations, never stored, so they cannot drift from each other.
- Only `Current deck` and `Companion` allocations move copies. Every other status is a plan (P-05: plans are not moves).
- Card data is a cache of Oracle data or of the user's own Sheet columns, not an authority. `ETB Tapped` and `Can Be Commander` are pattern-derived index hints (declared `candidate-source`, P-01), matching the canonical Sheet's own hint columns.
- Enrichment renames cards to their exact Oracle name and keeps the imported spelling as `Recorded / Printed Alias`. Back-face names never match (Rampant Growth is also the back of Studious First-Year).
- For the canonical Sheet, the Sheet stays the inventory authority. A database imported from its export is a snapshot. The KB release pipeline still builds from the `.xlsx`.
- KB mechanics contracts come from the canonical Sheet's Mechanics tabs, so other people's collections get none yet.

### Notes
- Setup guide: `docs/BRING_YOUR_OWN_COLLECTION.md`. Tests: `tests/test_collection.py`. Decision: D-0003 (proposed).
