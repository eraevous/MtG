# Module: grammar.build
> Map Oracle phrases to reusable, inspectable templates and DIO concepts, and compile each ability into a candidate DIO contract.

@ai-path: grammar.build
@ai-source-file: grammar/build.py
@ai-role: compiler
@ai-intent: "Map Oracle phrases to reusable, inspectable templates and DIO concepts, and compile each ability into a candidate DIO contract."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: concepts, grammar, semantics
@ai-contracts: P-01, P-02

### Inputs and outputs
| Direction | What |
|---|---|
| In | Scryfall corpus, rulings, set data (grammar/data) |
| Out | grammar_layer.sqlite (not in Git), review CSVs, metrics |

### Risks, invariants and known gaps
- 82% of collection abilities parse; 0% of templates are reviewed. Parse success is not semantic validity (P-01).
- A mechanic the DIO can't express becomes an ontology change proposal, not new compiler semantics.
- Known drafter bugs in 0.4.0: quoted granted abilities inherit the parent's hook; 36 'as this land enters' clauses are drafted as ETB triggers.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
