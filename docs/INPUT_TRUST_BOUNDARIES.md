# MTG input trust boundaries (Aegis)

## Observed routes

- `collection/mtgcollection.py`: `import_csv` / `import_rows` preserve collection
  fields; `import_xlsx` reads Sheet exports and keeps Mechanics rows as candidate
  annotations. `fields_from_scryfall` retains Oracle text (face text is joined by
  the existing formatter). These are data-import operations, not model prompts.
- `kb/inventory_adapter.py` reads workbook values and cached formula values, not
  executable formulas. KB builders derive candidate records from these inputs.
- `mtgtools/verbs.py` retrieves Oracle text, candidate contracts, deck charters and
  collection policy. `card` repeats rules text in claims; `check` echoes submitted
  claim text but explicitly does not judge that text. `context` returns charters.
- `mtgtools/dio.py` quotes local governed sources with file, line and heading.
  Its representation authority does not include agent/tool operation.
- `mtgtools/kb.py::release` reads adjacent SOURCE_MANIFEST metadata. These labels
  and hashes are not cryptographic verification of the retrieved content.
- `mtgtools/cli.py::envelope` is the shared JSON delivery boundary. Source strings
  can contain forged role markers, approvals or instructions in any of these
  paths; a conversational consumer may encounter them. No embedded model or
  natural-language-driven executor was identified in this retrieval path.

## Bounded defense

Version 0.4.3 adds a code-owned, versioned `trust_boundary` descriptor to every
success and handled-error CLI envelope. It declares reference-data status,
source-derived fields, scoped domain authority and no operational permission.
Data remains structurally nested and JSON-escaped; nested metadata cannot replace
that descriptor. Manifest dates are no longer interpolated into a guidance
sentence. Existing text, evidence grades and field locations are preserved.

This is defense in depth at a consumer boundary, not an exploit-proof sandbox or a
new content classifier. Tests assert structure, lossless text and error-path
coverage, not model immunity. A forged entire tool response still needs trusted
transport/producer verification by the consumer. Direct library use or raw data
reads bypass the descriptor. There is no new action executor, URL follower,
keyword blocker or automatic sanitization. Authorization and side-effect gates
remain the responsibility of the calling agent/runtime. Source text must never
supply those grants, even when domain evidence is decision-grade.
