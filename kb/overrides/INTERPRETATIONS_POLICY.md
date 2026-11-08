# Interpretation log policy (2026-11-07, DEC-152)

This is an addendum to `REVIEW_POLICY.md`. It lives in its own file because `REVIEW_POLICY.md` is pinned by the release manifest (`kb/MANIFEST.sha256`, C-011); fold it in at the next `release.py` run.

- `interpretations.jsonl` holds **dialogic readings**: a question about one card or mechanic, each party's reading with its CR citations and the model that spoke, and an outcome of `agreed`, `contested` or `needs-zach`.
- Write lines only with `python3 kb/interpret.py add`. The file is append-only and hash-chained (`chain.py`), and `tools/drift_rules.json` lists it as append-only. Never edit a line; append a new one with `--supersedes <interpretation_id>`.
- Every row is `verification_state: candidate`, and the writer refuses any other state. An agreed reading is **evidence** for a later semantic review (`review.py`, with scenarios) or a decision event; it is never a review itself and changes no contract's state. Only Zach promotes.
- Every reading cites its basis: a CR rule number (`702.52`, `704.5q`), `oracle` (the Oracle text alone decides it) or `ruling:YYYY-MM-DD`. Uncited readings are refused.
- `agreed` and `contested` need at least two distinct parties (`party`, not `model`: two models under one actor are one voice). One party can only record `needs-zach`.
- A card row binds to the KB's current `oracle_text_sha256`, `oracle_id` and release. `interpret.py verify` reports rows whose card text has since changed. A `--contract` id is optional context, checked for existence and ownership, not bound by SHA: the question is about the text, which outlives a drafter version.
- The log is the only home of these readings (DIO §2). Nothing replays it into the SQLite build. A tool that wants to show readings beside a `card` answer reads this file.

## Optional fields: Kate's round-17 protocol amendments (2026-11-07; **proposals, not adopted**)

Kate agreed to the dialogue protocol with four amendments (relay-kit-private `kairos/kate-round-17.md`, provenance Kate → Abigail → coordinator, verification against the source thread pending). Zach has not decided them. They are carried as **optional** fields so he can adopt or drop them without a schema change; a row without them is valid, a row with them is vocabulary-checked.

| Amendment | Field | Vocabulary / shape |
|---|---|---|
| 1. Separate "what does the card do", "how does the DIO represent it", "what role in this deck" | `layer` | `mechanics` \| `dio_representation` \| `deck_role` |
| 2. Independent first readings (Oracle text, CR citations, interpretation, uncertainty, concrete scenario, before seeing the other's) | per reading: `independent`, `uncertainty`, `scenario` | bool; non-empty strings |
| 3. Record the disagreement type; don't resolve substantive disagreement by model consensus | `disagreement_type` | `oracle_rules` \| `ontology_representation` \| `contextual_role` \| `insufficient_evidence`; refused on an `agreed` row |
| 4. Test executable consequences: a positive scenario and a near-miss counterexample; capture whether KB/evaluator output changes | `scenarios` | `{positive, near_miss, kb_output_changed: true\|false\|null}`; the pair is required together, `null` = not run yet |

`interpret.py verify` reports `with_scenarios` and `kb_output_changed` counts beside the outcome counts, because Kate's proposed measure of the dialogue is whether it reduces recurring mechanical errors and improves deck decisions, not how many readings are agreed. Nothing here changes who promotes (Zach) or the `candidate` invariant.
