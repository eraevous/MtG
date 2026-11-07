# Module: kb.interpret
> Writer for the append-only, hash-chained interpretation log (`kb/overrides/interpretations.jsonl`): what two or more readers said a card or mechanic does, with CR citations and the model that spoke, and whether they agreed. Every row is a candidate; the module refuses any other state.

@ai-path: kb.interpret
@ai-source-file: kb/interpret.py
@ai-role: ledger_writer
@ai-intent: "Record dialogic readings of Oracle text as evidence for a later review or decision, never as a review."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: chain
@ai-contracts: P-01, P-03, P-06

### Inputs and outputs
| Direction | What |
|---|---|
| In | A question about a card or mechanic; readings `[{party, model, reading, cr_citations}]`; an outcome (`agreed`, `contested`, `needs-zach`); the KB release database, read-only, to bind a card row to its oracle_id and current Oracle text SHA |
| Out | One appended line in `kb/overrides/interpretations.jsonl`, chained to the previous line (`prev`, `interpretation_id`) |

### Risks, invariants and known gaps
- `verification_state` is always `candidate`. Promotion is Zach's and happens in `review.py` (a semantic review with scenarios) or `decisions/`, never here (AGENTS.md hard rules; overrides/INTERPRETATIONS_POLICY.md, an addendum to REVIEW_POLICY.md).
- A reading must cite its evidence (a CR rule number, `oracle`, or `ruling:YYYY-MM-DD`). `agreed` and `contested` need at least two distinct parties; one party may only record `needs-zach`.
- The log is the one home of these readings (DIO §2). Nothing replays it into the SQLite build, so adding a table was not needed; if a tool later wants to show readings beside a `card` answer, it reads this file.
- Opens the KB `mode=ro`; never writes the Sheet, the DB or any other override.
- Read-time trust: the readings are model and human judgments labelled by `party` and `model`. A row from a cheaper model carries that model's name so a reader can weigh it (DEC-152 allows cheaper models for the dialogue).

### Notes
- Added 2026-11-07 for DEC-152 (HO-MTG-20261107-92QA), on branch `mtg/interpretations-log`. The alternative, an `mtgtools interpret add` verb, was rejected because `mtgtools.cli` is read-only by contract and writing an override would change its responsibility (AGENTS.md Drift trigger). A read-only `mtgtools interpret show` may follow.
