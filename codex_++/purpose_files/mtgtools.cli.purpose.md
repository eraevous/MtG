# Module: mtgtools.cli
> The `mtg` command: six read-only verbs (context, card, explore, hypothesis, compare, check) that a conversational AI calls to think with the collection. Output is JSON with per-claim kind, support and grade.

@ai-path: mtgtools.cli
@ai-source-file: mtgtools/cli.py
@ai-role: interface
@ai-intent: "Give LLMs a small, testable tool surface over the KB, the loop discovery and the evaluator, without embedding an LLM in the engine."
@ai-version: 0.2.1
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: kb, verbs
@ai-contracts: P-01, P-03, P-04, P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | `--db` collection SQLite (default kb/mtg_cards_v0.2.sqlite), verb arguments, for `check` a JSON list of claims, for `compare` an inventory export |
| Out | One JSON envelope: tool/version/verb/query, the collection's release and inventory snapshot, claims, data, or error |

### Risks, invariants and known gaps
- Read-only. Opens the database with `mode=ro` and never writes the Sheet, the KB or the overrides.
- Every claim carries `kind` (inventory, rules_text, mechanics, performance, preference) and a grade computed per kind (mtgtools/claims.py). performance is never decision_grade in v0, and preference is never system-gradable.
- Design: Kate's review, coordination thread 2026-10-27 [44]; held-out test is her eight frozen Terra questions (prompt sha256 eab81c1cb306…).
