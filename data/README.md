# Data artifacts (not in Git)

**Quick path:** `python3 tools/kb_bootstrap.py install` puts the two KB databases into `kb/` and checks them against `kb/MANIFEST.sha256`. It finds the release zip pinned in `tools/kb_release.json` in `data/` or in the Claude project files, or downloads it from the GitHub release asset. `python3 tools/kb_bootstrap.py status` says what is present.

These are needed to run the KB tests, the evaluator and the grammar rebuild. They are large, derived or personal, so they are gitignored.

| File | Put it at | Source |
|---|---|---|
| `mtg_cards.sqlite` (35 MB, v0.1 import) | `kb/` | `mtg_kb_v0.2.1-r20261030.zip` (GitHub release `kb-r20261030`, or project files mechanics-kernel/sqlite-kb/); r20261024d is in `MTG_handoff_2026-10-25.zip` |
| `mtg_cards_v0.2.sqlite` (102 MB, current KB) | `kb/` | same zip, or rebuild: `python3 kb/migrate_v02.py --v01 kb/mtg_cards.sqlite ...` (see C-001) |
| `MTG_Master_Inventory_Canonical_export_20261024d.xlsx` | `data/` | `01_inventory/` in the handoff zip, or a fresh export of the live Sheet |
| `grammar_layer.sqlite` (135 MB) | `grammar/` | `MTG_grammar_layer_db_2026-10-24.zip`. Optional: only needed to query or rebuild the grammar layer |

Not Zach? You don't need any of these to run the evaluator. Build a collection database from your own cards instead (`docs/BRING_YOUR_OWN_COLLECTION.md`) and keep it here as `data/<name>.sqlite`.

The live inventory is the Google Sheet "MTG Master Inventory — Canonical". Its id changes with every edit (archive-then-clone). Exports are snapshots, never the authority.

C-006: once the release zip is a GitHub release asset (tag `kb-r20261030`, file `mtg_kb_v0.2.1-r20261030.zip`), `kb_bootstrap.py install` works from any clone, and CI can install it and run the 61 KB tests.
