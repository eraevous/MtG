# Data artifacts (not in Git)

These are needed to run the KB tests, the evaluator and the grammar rebuild. They are large, derived or personal, so they are gitignored.

| File | Put it at | Source |
|---|---|---|
| `mtg_cards.sqlite` (35 MB, v0.1 import) | `kb/` | `mtg_kb_v0.2.1-r20261030.zip` (project files, mechanics-kernel/sqlite-kb/); r20261024d is in `MTG_handoff_2026-10-25.zip` |
| `mtg_cards_v0.2.sqlite` (102 MB, current KB) | `kb/` | same zip, or rebuild: `python3 kb/migrate_v02.py --v01 kb/mtg_cards.sqlite ...` (see C-001) |
| `MTG_Master_Inventory_Canonical_export_20261024d.xlsx` | `data/` | `01_inventory/` in the handoff zip, or a fresh export of the live Sheet |
| `grammar_layer.sqlite` (135 MB) | `grammar/` | `MTG_grammar_layer_db_2026-10-24.zip`. Optional: only needed to query or rebuild the grammar layer |

Not Zach? You don't need any of these to run the evaluator. Build a collection database from your own cards instead (`docs/BRING_YOUR_OWN_COLLECTION.md`) and keep it here as `data/<name>.sqlite`.

The live inventory is the Google Sheet "MTG Master Inventory — Canonical". Its id changes with every edit (archive-then-clone). Exports are snapshots, never the authority.

Next step (C-006): publish the two KB databases as a GitHub release asset, so CI can run the 61 KB tests.
