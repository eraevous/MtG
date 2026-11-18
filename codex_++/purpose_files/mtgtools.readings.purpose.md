# Module: mtgtools.readings
> `mtg reading NAME`: the interpretation-log rows about one card or mechanic, as JSON, with the KB's current Oracle hash and contracts when the database is present (D-0033 (a)). Derived, never stored; needs no database.

@ai-path: mtgtools.readings
@ai-source-file: mtgtools/readings.py
@ai-role: interface
@ai-intent: "Put agreed, contested and needs-zach readings where a deck question is asked, without letting a page read as review."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: kb, claims
@ai-contracts: P-01, P-03, P-04, P-09

### Inputs and outputs
| Direction | What |
|---|---|
| In | A card or mechanic name (case-insensitive); kb/overrides/interpretations.jsonl, read and chain-checked through kb/interpret.py; optionally a read-only KB connection |
| Out | `data`: subject, banner (candidate, promoted 0, chain state, log head), current rows, superseded rows, rows by outcome, KB contracts, notes, limits. One `mechanics` claim per current row, support `candidate` |

### Risks, invariants and known gaps
- `candidate` is the only state it can print. A row that says otherwise is shown as `logged_state` beside `verification_state: candidate`, and its claim is still exploratory (P-03).
- Parses no card text (P-01) and judges no usefulness (P-04). Writes nothing: the rendered markdown page is tools/render_readings.py's job, into gitignored build/readings/ (D-0033 (b)).
- A broken hash chain hides every row and is reported in the banner and a claim.
- Known gap: a card page lists only rows named for that card, not the mechanic rows it inherits, and there is no `--deck` mode. Both need a hook-to-mechanic join (92QA 3.2) that is not built.
