# Bring your own collection

The tools in this repo were built around one person's collection, kept in a private Google Sheet. You can point them at **your** cards instead. Your collection goes into a single SQLite file (a *collection database*). The deck evaluator and the knowledgebase build read that file anywhere they would read the Sheet export.

You need Python 3.10 or newer and a copy of this repo. Nothing else gets installed: everything uses the Python standard library.

## Quick start

```bash
git clone https://github.com/eraevous/MtG.git && cd MtG
M="python3 collection/mtgcollection.py"

$M init data/my_collection.sqlite --name "Sam's cards" --owner Sam
$M import-csv  data/my_collection.sqlite ~/Downloads/moxfield_haves.csv
$M import-deck data/my_collection.sqlite ~/Downloads/atraxa.txt --deck Atraxa
$M enrich      data/my_collection.sqlite --online
$M check       data/my_collection.sqlite

cd kb && PYTHONPATH=vendor python3 -m mtg_eval --workbook ../data/my_collection.sqlite deck Atraxa
```

Put the database under `data/`. Git ignores `*.sqlite` and everything in `data/`, so your collection is never committed.

On Windows, use `py` in place of `python3`. To set `PYTHONPATH` in PowerShell, run `$env:PYTHONPATH="vendor"` first.

A worked example with a public precon list is in `collection/examples/`:

```bash
$M init data/example.sqlite --name "Example"
$M import-csv  data/example.sqlite collection/examples/moxfield_collection.csv
$M import-deck data/example.sqlite collection/examples/token_triumph.txt --deck "Token Triumph" --own-missing
$M enrich      data/example.sqlite --online
```

## 1. Create the database

```bash
python3 collection/mtgcollection.py init data/my_collection.sqlite --name "Sam's cards" --owner Sam
```

`--name` is the label reports print as the source of the inventory.

## 2. Import what you own

You can run several imports. Each one is a **source**, which by default is the file name; set your own with `--source`. If you import the same source again, it replaces that source's earlier rows, and other sources are left alone. So you can keep, say, a Moxfield export and a "binder 2" spreadsheet side by side, and refresh either one on its own. Your owned count for a card is the sum across all sources.

> **Refreshing an export? Reuse its source label.** `export.csv` and a newer `export_nov.csv` are two different sources by default, so their counts would add up. Use the same `--source` for every version of the same export (for example `--source moxfield`). If most of the cards in a new import also appear in another source, the importer prints a warning.

Import your collection **before** your decks. A deck line like `1 Fire` then attaches to the `Fire // Ice` your collection already holds, instead of becoming a second card.

### From a collection app (CSV)

```bash
python3 collection/mtgcollection.py import-csv data/my_collection.sqlite export.csv --source moxfield
```

The importer recognises the column names that Moxfield, Archidekt, ManaBox, Deckbox, Deckstats and TCGplayer exports use. It only needs a **name** column. A **quantity** column is optional: if there isn't one, each row counts as one copy. Where they exist, set code, collector number, foil/finish, language and condition are stored per row.

| Field | Accepted headers (case and spacing ignored) |
|---|---|
| name (required) | Card Name, Name, Card, Card Title |
| quantity | Quantity, Count, Qty, Amount, Copies, Owned, Have |
| set | Set Code, Set, Edition Code, Edition |
| collector number | Collector Number, Card Number, Number, CN |
| finish | Finish, Foil, Printing |
| language, condition, notes | Language, Condition, Notes |

Comma, semicolon and tab separators all work.

### From your own Google Sheet or Excel file

The easiest route is **File → Download → Comma-separated values** on the tab that lists your cards, then `import-csv`. To import the whole workbook instead, use **File → Download → Microsoft Excel (.xlsx)**:

```bash
python3 collection/mtgcollection.py import-xlsx data/my_collection.sqlite my_sheet.xlsx --tab "Cards" --header-row 1
```

Your sheet can also carry its own card data, using the same column names as the canonical Sheet: `Oracle Text`, `Type Line`, `Mana Cost`, `Mana Value`, `Color Identity`, `Keywords`, `Produces`, `Power`, `Toughness`, `Rarity`, `Commander Legal`, `Can Be Commander`, `ETB Tapped`, `Scryfall URL` and `Roles`. Whatever is filled in is kept. `Roles` holds your own tags (for example `Ramp; Card draw`), separated by `; `. The evaluator uses them as unverified hints. Any other columns are stored as they are.

### A plain list of names

A one-column CSV with a `Name` header counts one copy of each card.

## 3. Add your decks

Export each deck as text from Moxfield, Archidekt, MTG Arena or MTGO, then:

```bash
python3 collection/mtgcollection.py import-deck data/my_collection.sqlite atraxa.txt --deck Atraxa
```

- The usual formats work: `1 Sol Ring`, `1x Sol Ring`, `1 Sol Ring (C21) 263 *F*`.
- A `Commander` header marks the commander, and so does an inline `*CMDR*` or `[Commander]`. If your export does neither, add `--commander "Atraxa, Praetors' Voice"`.
- Lines under `Sideboard`, `Maybeboard` and `Tokens` are skipped, and so are lines tagged `[Maybeboard]`, `[Sideboard]` or `[Considering]` (Archidekt categories). A `Companion` section is kept outside the 100.
- Names are matched to the spelling your collection already uses: front faces and missing accents both count.
- Importing the same `--deck` again replaces that deck.

**Status.** By default a deck is a `Current deck`, meaning its cards are physically in that deck. Those copies stop counting as free for other decks. For a list you are only considering, use `--status "Candidate"` (or any label you like). A candidate list never moves cards; it is a plan.

**Cards your collection import missed.** Often a collection export leaves out cards that sit in built decks. `check` reports these as `overallocated`. If you know you own them, add `--own-missing`. Holdings are then added for the shortfall, under the source `deck:<name>`.

## 4. Fill in card data from Scryfall

The tools need each card's Oracle text, type line, mana cost, color identity and Commander legality. `enrich` fills these in from Scryfall for every card that doesn't have them yet.

```bash
python3 collection/mtgcollection.py enrich data/my_collection.sqlite --online             # Scryfall API, 75 cards per request
python3 collection/mtgcollection.py enrich data/my_collection.sqlite --download data/     # fetch the bulk "Oracle Cards" file (~160 MB) once
python3 collection/mtgcollection.py enrich data/my_collection.sqlite --scryfall data/oracle-cards-2026….json
```

- Card names are moved to their exact Oracle names. For example, `Brigid, Clachan's Heart` becomes `Brigid, Clachan's Heart // Brigid, Doun's Mind`, and `Lim-Dul's Vault` becomes `Lim-Dûl's Vault`. The name you imported is kept as `Recorded / Printed Alias`.
- Names Scryfall can't find are listed under `not_found`. Fix the spelling in your source and import it again.
- `--refresh` fetches card data again for every card, for example after an Oracle update.

The card data in the database is a **cached copy** of Scryfall's Oracle data. Oracle text stays the rules authority. Two columns are hints computed from Oracle text with simple patterns: `ETB Tapped` (lands: Yes, No or Conditional) and `Can Be Commander`. Treat them as hints, as the canonical Sheet does.

## 5. Check it

```bash
python3 collection/mtgcollection.py check data/my_collection.sqlite
```

`check` prints counts, the size of each deck, any cards still missing card data, and the problems the inventory adapter finds: cards in more decks than you own copies of, unknown cards, and decks that aren't 100 cards. `ready_for_evaluator` and `ready_for_kb_build` tell you whether the next steps will run. The KB build is stricter: it refuses decks that aren't 100 cards.

## 6. Use it

Pass the `.sqlite` path wherever a command asks for `--workbook`:

```bash
cd kb
export PYTHONPATH=vendor
python3 -m mtg_eval --workbook ../data/my_collection.sqlite inventory
python3 -m mtg_eval --workbook ../data/my_collection.sqlite deck Atraxa
python3 -m mtg_eval --workbook ../data/my_collection.sqlite card "Smothering Tithe" --deck Atraxa
python3 -m mtg_eval --workbook ../data/my_collection.sqlite upgrades Atraxa --top 5
python3 -m mtg_eval --workbook ../data/my_collection.sqlite build "Selvala, Heart of the Wilds"
```

`MTG_WORKBOOK=../data/my_collection.sqlite` works in place of `--workbook`. Reports still print the word "sheet" in a couple of places (for example "Source: sheet collection 'Sam's cards'"), but the source they name is your database.

### Optional: build the knowledgebase for queries

```bash
cd kb
python3 build_mtg_db.py ../data/my_collection.sqlite --db ../data/kb/mtg_cards.sqlite
python3 migrate_v02.py --v01 ../data/kb/mtg_cards.sqlite --out ../data/kb/mtg_cards_v0.2.sqlite \
    --overlay ../collection/no_overrides.jsonl --reconciliation ../collection/no_overrides.jsonl
python3 kbq.py --db ../data/kb/mtg_cards_v0.2.sqlite card "Smothering Tithe"
python3 kbq.py --db ../data/kb/mtg_cards_v0.2.sqlite available --help
```

The two `no_overrides.jsonl` arguments stop the build from replaying the original owner's review overlay and Oracle reconciliation records, which name cards you may not own.

## What works for you, and what doesn't yet

| Part | With your collection |
|---|---|
| Inventory, custody, free copies, deck lists | Works. Copies in decks and free copies are computed from your deck imports. |
| Deck evaluator (`mtg_eval`: deck, card, compare, upgrades, build, transfer, portfolio) | Works. Its coverage limits apply to everyone: its numbers are descriptive profiles, not rankings (see `evaluations/EVALUATOR_README.md`). |
| KB v0.1 build, `kbq.py` queries | Works, with the overrides shown above. |
| KB **mechanics contracts** (DIO candidate operations, review queue) | **Empty for your cards.** Contracts are drafted from the "Mechanics" tabs of the original owner's Sheet. Drafting them for any collection from the grammar layer is future work. |
| Grammar layer (`grammar/`) | Collection-independent, but its `in_collection` flags describe the original owner's cards. |
| Doctrine and labels (`kb/reference_sources/`, the TMNT function labels) | Written for the original owner's decks. They load, but they say nothing about yours. |

None of the mechanics output is human-verified, for anyone. Read every interaction claim as a candidate (see `codex_++/project.purpose.md`, P-01 and P-03).

## For the canonical Sheet's owner

The canonical Sheet ("MTG Master Inventory — Canonical") imports as a whole:

```bash
python3 collection/mtgcollection.py import-xlsx data/zach.sqlite data/MTG_Master_Inventory_Canonical_export_<date>.xlsx --sheet-id <current sheet id>
```

When the workbook has `Collection` and `Deck Allocations` tabs (header on row 4) and no `--tab` is given, three things are imported (an import replaces the decks the previous Sheet import brought in, and keeps decks added with `import-deck`): the holdings, every deck allocation row (whatever its status), and the two `Mechanics` tabs, passed through as candidate annotations. The evaluator then gives the same results from the database as from the export. Other tabs (Overview, intake logs and so on) are not carried over. The KB release pipeline still builds from the `.xlsx` export, so its manifests keep naming the Sheet id. A KB built from the database names the collection as its source (`collection:<name>`) and records the Sheet id only as `collection_imported_from_sheet`, because the database may have been edited since the import. The Sheet stays the inventory authority, and a database made from it is a snapshot, like the export.

## Reference

- Schema: `collection/schema.sql`. Tables: `cards` (card data), `holdings` (what you own: one or more rows per card), `deck_cards` (allocations), `sheet_rows` (pass-through tabs), `imports` (provenance of every import and enrichment), `meta`. Owned, in-deck and free counts are views, never stored.
- Reader: `kb/vendor/mtg_eval/collection_db.py`. It returns the same rows as the Sheet export reader, so downstream code doesn't need to know which one it got.
- A file counts as a collection database when it starts with the SQLite header and has the collection views. Any other SQLite file is refused with an error.
- Tests: `python3 -m unittest tests.test_collection`.
