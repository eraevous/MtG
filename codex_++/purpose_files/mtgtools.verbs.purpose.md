# Module: mtgtools.verbs
> Implementations of the six verbs over the KB's read-only query layer (kb/kbq.py) and the grammar layer's collection loop discovery.

@ai-path: mtgtools.verbs
@ai-source-file: mtgtools/verbs.py
@ai-role: query
@ai-intent: "Answer an LLM's questions with evidence and say how far each answer is established; surface relationships it did not ask about."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: claims, kb
@ai-contracts: P-01, P-03, P-04, P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | sqlite3 connection (KB v0.2.1 schema), grammar/discovery/collection_loops.csv, decks/charters/*.json, evaluator (compare only) |
| Out | (data, claims) per verb |

### Risks, invariants and known gaps
- No card-text parsing here (P-01): links come from contract query indexes and the KB's FEEDS table, and loops from the grammar layer.
- Links match on hook only. Qualifiers (whose permanent, which type) are not checked, so every link is a lead and says so in `limitations`.
- `explore --mode divergent` with a seed returns two-step chains forward from the seed through pathways the seed does not use itself, scored so that narrow pathways come first. It is a heuristic for surfacing unrequested relationships, not a measure of value.
- Coverage: in r20261024d, 0 of 4,961 contracts are semantically reviewed, so mechanics claims are exploratory today.
