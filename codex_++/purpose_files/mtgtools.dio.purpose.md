# Module: mtgtools.dio
> Finds and quotes sections of the Deck Interaction Ontology (DIO v3.1.1, its 2026-10-09 addendum, compatibility addendum A1-A7) for `mtg dio TERM`. Needs no database, so an agent can consult the ontology when the KB is absent.

@ai-path: mtgtools.dio
@ai-source-file: mtgtools/dio.py
@ai-role: interface
@ai-intent: "Put the ontology on the agent's path: quote DIO sections with file and line, interpret nothing."
@ai-version: 0.3.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-01, P-03

### Inputs and outputs
| Direction | What |
|---|---|
| In | A term or section number; the DIO markdown files in kb/reference_sources/ and kb/addendum/ |
| Out | Matching sections (source, file, line, heading trail, text), a fixed reading map, no claims |

### Risks, invariants and known gaps
- Retrieval only: word counts over headings and text. It never decides what a card does, and it returns no claims, so it cannot be cited as evidence about a card.
- The reading map is a hand-written pointer list. If the DIO is renumbered, the map and the tests must change with it.
- The Grammar & Rules Vocabulary Registry (JSON) is not searched.
