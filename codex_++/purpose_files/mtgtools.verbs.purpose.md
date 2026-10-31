# Module: mtgtools.verbs
> Implementations of the six verbs over the KB's read-only query layer (kb/kbq.py) and the grammar layer's collection loop discovery.

@ai-path: mtgtools.verbs
@ai-source-file: mtgtools/verbs.py
@ai-role: query
@ai-intent: "Answer an LLM's questions with evidence and say how far each answer is established; surface relationships it did not ask about."
@ai-version: 0.2.1
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: claims, kb
@ai-contracts: P-01, P-03, P-04, P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | sqlite3 connection (KB v0.2.1 schema), grammar/discovery/collection_loops.csv, decks/charters/*.json, decks/collection_policy.json, evaluator (compare only) |
| Out | (data, claims) per verb |

### Risks, invariants and known gaps
- No `oracle_text` interpretation here (P-01): links come from contract query indexes and the KB's FEEDS table, and loops from the grammar layer. Exception under review (C-010): to qualify links, the module reads the contracts' structured `object_filter`, a leading "this" in the trigger's event phrase, and type-line words in target-eligibility phrases.
- Each link carries a qualifier status (`compatible` / `unresolved` / `incompatible`) and a basis. Incompatible links are rejected and summarised, never silently dropped. Unknown qualifiers (counter type, token characteristics, controller, face) stay `unresolved`, never matched.
- Loops from the grammar layer whose step no recorded KB contract produces are `loops_contested` (`unsupported_by_contracts`, not proof of invalidity). A rejected route never removes a card's other interactions (`hypothesis` → `acts_on`).
- `check`: `evidence_grade` is the source, `verdict` is the structured assertion, and `grade` is decision_grade only when both hold. Invariant: decision-grade evidence never automatically makes a decision-grade conclusion.
- `context --deck` role counts are detected candidates from the KB's role patterns, not verified roles. `sole_detected_candidates` means the only detected candidate, not a verified sole provider. A caveat claim (mechanics, exploratory until every card-role assignment in the summary is reviewed) says so, after the 2026-10-28 Golden Argosy error.
- Collection policy (`decks/collection_policy.json`) is operational configuration. It records Zach's decision, and the tools never move cards.
- `explore --mode divergent` with a seed returns two-step chains forward from the seed through pathways the seed does not use itself, scored so that narrow pathways come first. It is a heuristic for surfacing unrequested relationships, not a measure of value.
- Coverage: in r20261030, 0 of 4,961 contracts are semantically reviewed, so mechanics claims are exploratory today.
