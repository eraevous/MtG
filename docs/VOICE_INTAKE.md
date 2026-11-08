# Voice intake: dictated cards → Scryfall batch → reviewable collection rows

**Purpose:** Identify around sixty dictated cards without sixty sequential requests. This tool handles **transcribed text**, not microphone/audio transcription. Use phone dictation to create text, then pass it through the CLI. Python 3.10+, standard library only.

## One command

```sh
python3 collection/voice_intake.py data/dictated_cards.txt --review data/intake_review.json --csv data/intake_verified.csv
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

## Output and authority

- `--review`: full JSON with every original line, quantity, submitted identity, Scryfall identity, lookup method, and `accepted` / `review` / `unresolved` status.
- `--csv`: **exact accepted rows only**, headers compatible with `collection/mtgcollection.py import-csv`. Ambiguous and fuzzy rows are absent until independently confirmed.
- Exit 0: all exact; 1: review/unresolved; 2: transport/API error.

**Check the JSON and the CSV before importing.** This CLI NEVER modifies an existing SQLite collection, deck allocation, KB, or the canonical Google Sheet. Do not treat Scryfall identification as proof of physical ownership. For importing the resulting CSV into a separately managed collection, see `docs/BRING_YOUR_OWN_COLLECTION.md`: distinct source labels add together; importing the same source label replaces that source's holdings.

## Efficiency and Scryfall policy

`POST /cards/collection` accepts at most **75 identifiers** per batch. The script deduplicates lookup identities: sixty correct set/number rows need **one** batch call, not sixty. It paces sequential calls at least 550 ms apart, uses identifying User-Agent / JSON Accept headers, caps fuzzy lookups, and stops on HTTP 429 rather than retrying aggressively. For repeated whole-database work, use the existing bulk-data path in `collection/mtgcollection.py`.

Source: https://scryfall.com/docs/faqs/i-m-having-trouble-accessing-the-scryfall-api-or-i-m-blocked-17

**Evidence boundary:** Unit tests prove request counts against a mocked transport; no real-network speed claim or phone speech-recognition accuracy has been measured yet. Benchmark sixty real dictated rows before claiming a specific latency.

## Future adapter, not part of this PR

A phone capture adapter, local microphone STT, curated set-symbol mapping, and immediate review interface could eventually remove the manual transcript-file step. This PR intentionally delivers the smallest useful tool first.
