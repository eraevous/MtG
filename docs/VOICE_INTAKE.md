# Intake: transcript or CSV → inventory first → Scryfall batch → reviewable rows

**Purpose:** Identify around sixty dictated cards without sixty sequential requests. This tool handles **transcribed text** or structured CSV from any capture source, not microphone/audio transcription or photo recognition. Use phone dictation to create text, then pass it through the CLI. Python 3.10+, standard library only.

## One command

```sh
python3 collection/voice_intake.py data/dictated_cards.txt --inventory data/current_collection.csv --review data/intake_review.json --csv data/intake_verified.csv
```

On Windows, replace `python3` with `py`. Or pipe transcribed text into `python3 collection/voice_intake.py -`.

Say *next card* between entries (or use separate lines or semicolons). **Don't split at bare commas**, because many card names contain commas.

Example input:

```text
three copies of Sol Ring set symbol C M M number 396
next card
one Arcane Signet
next card
2 Lightning Bolt (M11) 146
next card
CMM 396
```

Best input is **set code + collector number**: `CMM 396`, or `set code CMM number 396`, optionally with a name and quantity. The set/number combination identifies the exact printing; an incorrect spoken name is marked **review** rather than accepted. Otherwise an exact card name works. If no exact name exists, the tool tries up to five fuzzy suggestions (configurable with `--fuzzy-budget`), **always marked review**.

A name plus set code without a collector number (for example, `Sol Ring set CMM`) preserves that set restriction. A response from another set is marked **review** and excluded from the CSV.

Bare number words can be part of a card name: `Seven Dwarves` is checked alongside the quantity interpretation in the same batch. An exact full-name match keeps quantity one; if both interpretations match, the JSON records both quantities and requires review. If neither matches exactly, fuzzy lookup uses the unstripped name with quantity one and keeps the alternate interpretation visible. Say `seven copies of ...` or use a numeric quantity to make the quantity explicit. Extra name interpretations count toward the 75-identifier batch limit.

Name matching uses the existing collection matcher: full names before front faces, never a back-face-only exact match. Back-face-only fuzzy suggestions still require review.

Use the two-to-six-character **set code**, not the full set name or a visual symbol description. Speak digits for collector numbers; free-form spoken number words are not confidently reassembled.

## Inventory first, for every capture source

Pass a recent local inventory CSV with `--inventory`. The canonical Collection export (header in the first 12 rows) and simple `Card Name` / `Name` lists work. Each entry first checks unique, exact full names (case/diacritic/punctuation normalization allowed), or explicitly recorded `Set Code` + `Collector Number`. This is intentionally conservative: ambiguous names, disagreeing print metadata, incomplete two-face names, front-face aliases and bare quantity-word ambiguity go to the existing external resolver. No local fuzzy guess is auto-accepted.

An exact inventory name does **not** establish the new copy's printing. Name-only hits leave collector number unknown and do not copy finish, language, IDs or URLs from existing holdings. A card-level Scryfall URL is a reference, not proof of an owned printing. The review report labels local `identity_scope` / `printing_status` and lists matching source rows. `accepted` means an exact recorded identity match suitable for review, not approval to update inventory.

Inventory snapshots are only identity hints, even if old or zero-quantity. They never establish current ownership, free copies or an absent card being unowned. Reports include a SHA-256 of the decoded UTF-8 inventory text, `freshness: not_verified`, and the provenance boundary. Verify the latest canonical Sheet separately before reconciliation or application. No title, quantity, allocation, notes, source path or raw transcript is sent to Scryfall: only unmatched lookup identifiers and bounded fuzzy names. Omitting `--inventory` preserves the older API-only flow; the caller must supply the correct snapshot for inventory-first behavior.

For a photo-derived list, product list, manually entered rows or another capture adapter, use the same resolver:

```sh
python3 collection/voice_intake.py captured.csv --input-format csv --inventory data/current_collection.csv --review data/intake_review.json --csv data/intake_verified.csv
```

Input columns: `Card Name` (or `Name`), optional `Quantity` (positive whole number; defaults to 1 if the column is absent), `Set Code`, `Collector Number`, `Finish`, `Language`, and `Source Text` / `Original Dictation`. Finish and language are carried from explicit capture only, not independently verified. Structured names are not reparsed as spoken quantities, so `Seven Dwarves,1` keeps its complete name. A malformed inventory fails before network calls rather than silently skipping the requested check.

Output CSV adds `Finish`, `Language` and `Method`; reconciliation retains observed language in its per-copy detail and printing summaries. Input/output aliases (including symlinks and hardlinks) are rejected before lookup. Callers that enforce a closed header set must accommodate them. No inventory content is committed by this workflow.

## Output and authority

- `--review`: full JSON with every original line, quantity, submitted identity, resolved identity, lookup method, inventory provenance when supplied, and `accepted` / `review` / `unresolved` status.
- `--csv`: **exact accepted rows only**, headers compatible with `collection/mtgcollection.py import-csv`. Ambiguous and fuzzy rows are absent until independently confirmed.
- Exit 0: all exact; 1: review/unresolved; 2: transport/API error.

**Check the JSON and the CSV before importing.** This CLI NEVER modifies an existing SQLite collection, deck allocation, KB, or the canonical Google Sheet. Do not treat Scryfall identification as proof of physical ownership. For importing the resulting CSV into a separately managed collection, see `docs/BRING_YOUR_OWN_COLLECTION.md`: distinct source labels add together; importing the same source label replaces that source's holdings.

## Efficiency and Scryfall policy

`POST /cards/collection` accepts at most **75 identifiers** per batch. After local matching, the script deduplicates remaining lookup identities: sixty correct set/number rows need **one** batch call, not sixty. It paces sequential calls at least 550 ms apart, uses identifying User-Agent / JSON Accept headers, caps and deduplicates repeated fuzzy lookups, and stops on HTTP 429 rather than retrying aggressively. For repeated whole-database work, use the existing bulk-data path in `collection/mtgcollection.py`.

Source: https://scryfall.com/docs/faqs/i-m-having-trouble-accessing-the-scryfall-api-or-i-m-blocked-17

**Evidence boundary:** Synthetic tests prove sixty exact local names → zero API requests, mixed batches send only misses, and 80 unique misses → two requests. Unit tests prove request counts against a mocked transport; no real-network speed claim or phone speech-recognition accuracy has been measured yet. Benchmark sixty real dictated rows before claiming a specific latency.

## Future adapter, not part of this PR

A phone capture adapter, local microphone STT, curated set-symbol mapping, and immediate review interface could eventually remove the manual transcript-file step. This PR intentionally delivers the smallest useful tool first.
