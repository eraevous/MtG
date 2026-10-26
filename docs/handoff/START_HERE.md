# MTG project handoff bundle (2026-10-25)

Read `00_CURRENT_STATE.md` first. It explains the architecture, the rules all work follows, and what is open. This file says what each folder holds and how to run the tools.

Everything here is a read-only snapshot. The live inventory is a Google Sheet, now id `1f83bN2ULQmXJQkkRL_JxPvzq9gWMYwLFobhATCjkCpU` (since 2026-10-25 18:10Z). Edits to it follow an archive-then-clone rule, so the id changes with every edit. The export, KB and evaluations here were built from the previous clone `1N1xBUkL_aYKpPcR8WJJVpeicgE8A06dqeUBM-hUa3Xo`, which is now archived as "…_20261025-1810Z_ARCHIVE". Its card data, counts and allocations are identical to the live Sheet. The only later changes were to the README, the Overview deck table and the filter ranges. **No operation or contract in any of these files is human-verified.** Treat every mechanics claim as a candidate.

## What is in the bundle

| Folder | Contents |
|---|---|
| `00_CURRENT_STATE.md` | Project status brief: architecture, inventory, extraction pass, KB, grammar layer, evaluator, open decisions. |
| `01_inventory/` | xlsx export of the canonical Sheet, taken 2026-10-24 after the mechanics extraction pass (sha256 `d7a2d191…4bab4`). It has 38 tabs. Collection and Deck Allocations have their header on row 4. |
| `02_knowledgebase/` | `mtg_kb_v0.2.1-r20261024d.zip` is the full KB release: both SQLite databases, the query and audit tools, the tests, the scenarios, the vendored evaluator and the doctrine documents. Its release notes and README are also unzipped next to it. |
| `03_evaluator/` | `current_evaluations_20261025/` holds fresh reports, run today: one inventory report and one deck report for each of the 13 decks. `01_deck_headlines.md` gathers the summary block of every deck report. Also here: the evaluator README and CHANGELOG, and the frozen 2026-10-20 predictions (never edit these; score them only against reported games). |
| `04_mechanics_review_packet/` | The 330 new candidate operations grouped into 88 mechanical classes, ready for Zach's class-level review. Includes the README and the scripts that produced them. |
| `05_grammar_layer/` | Oracle-text grammar layer v0.2: code, REPORT, DATA_DICTIONARY, metrics (including the per-intake r20261024* files), review CSVs, validation results and loop discovery. The 135 MB database is in the separate `MTG_grammar_layer_db_2026-10-24.zip`. It is optional and only needed to query or rebuild the grammar layer. |

The doctrine is in the KB zip under `reference_sources/`: Interaction Ontology v3.1.1 and its addendum, Evaluation Protocol v1.2 addendum, Kairos–GATE, and Grammar & Rules Vocabulary Registry v0.1. The DIO compatibility addendum (A1–A7) is in `addendum/`. Evaluation Protocol v1.0 and v1.1 are PDFs that live only in Zach's Drive.

## How to run (Python 3.10+, standard library only)

Unzip the KB release, then work from inside the unzipped folder:

```
unzip mtg_kb_v0.2.1-r20261024d.zip && cd mtg_kb_v0.2.1-r20261024d

# tests: 61, all pass
python3 -m unittest test_v02.py test_mtg_db.py test_acceptance.py

# knowledgebase queries; each answer names its evidence level
python3 kbq.py card "Emmara, Soul of the Accord"
python3 kbq.py overlap "Token Triumph"
python3 kbq.py packages --ci WG --deck "Token Triumph" --theme landfall
python3 kbq.py queue --deck "Token Triumph" --state ready_for_review
python3 deck_audit.py Necrobloom --out reports

# evaluator: use the vendored copy (0.3.0+kb2), which carries the current Sheet id
PYTHONPATH=vendor python3 -m mtg_eval --workbook ../01_inventory/MTG_Master_Inventory_Canonical_export_20261024d.xlsx deck "Token Triumph"
PYTHONPATH=vendor python3 -m mtg_eval --workbook <xlsx> <card|deck|module|compare|upgrades|build|inventory|transfer|portfolio|regress> ...
```

A deck report takes 10 to 40 seconds. `--engine-games 0` makes it quick, and `--json` gives machine-readable output.

## Known caveats

- **Nothing is verified.** Of 4,961 contracts, none is semantically reviewed. 446 compile losslessly and 7 are quarantined.
- **Typed coverage is low.** The evaluator fully reads only 4–31 of the 60–65 nonland cards per deck (median 10). Its numbers are descriptive profiles, not rankings, and its count screen thresholds were set after the fact.
- **`VERSION.json` in the KB zip is stale.** It is a leftover v0.1 file. The current release identity is in `SOURCE_MANIFEST.json`.
- **`mtg_eval_release/` inside the KB zip still names an older Sheet id.** The labels are wrong but the data is current. Prefer `vendor/mtg_eval`.
- **`qa_queue` counts include replayed Oracle snapshots.** Each replay adds about 212 rows, so the count is not the number of new problems.
- **Unresolved identity.** The three Offspring cards are flagged in the review packet README, and the SCD basic lands have unresolved collector numbers.
