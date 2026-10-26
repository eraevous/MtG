# MTG Project — source map and operating standard
**Revision:** 2026-10-25 • **Status:** active navigation supplement, not a replacement of the ontology or protocols.

## Governing authorities

1. **Ownership, physical copies, allocations:** live Google Sheet **MTG Master Inventory — Canonical**. At handoff, [live Sheet](https://docs.google.com/spreadsheets/d/1f83bN2ULQmXJQkkRL_JxPvzq9gWMYwLFobhATCjkCpU/edit). ID changes after every approved archive-then-clone operation; confirm the latest clone before editing. The handoff export is a dated snapshot, not the perpetual source.
2. **Rules text:** current Scryfall Oracle wording, checked against relevant rules and rulings for contested mechanics; generated semantic translations do not override Oracle.
3. **Mechanics:** DIO v3.1.1, its existing addendum, and the accepted `DIO_v3.1.1_A1-A7_COMPATIBILITY_ACCEPTED.md` plus its registry delta. Preserve v2.x and earlier documents as historical references.
4. **Deck evaluation and portfolio:** Evaluation Protocol v1.0, v1.1 and v1.2 addenda and the actual DeckRequirementsProfile, protected cards and user game observations. Mechanics representation is descriptive; usefulness and feel are context-dependent.
5. **Execution:** derived Oracle grammar, KB and evaluator. Their outputs carry source versions, separate semantic/runtime readiness, unsupported mechanics and simulation assumptions. Never hand-edit derived KB content.

## Frozen October 24–25 snapshot

- Inventory: 3,520 Collection rows; 5,802 copies; 3,512 card names; 13 complete allocated Commander decks, including intact Token Triumph (Emmara, Soul of the Accord). Plans are **not** physical transfers. The handoff workbook has **41 tabs** (the `START_HERE` guide's 38 is obsolete).
- KB release `mtg-kb-v0.2.1-r20261024d`: 4,961 **candidate** contracts; 446 lossless compiles; seven quarantined. No contract was human-semantic-verified. 61 software tests pass; runtime support is a separate gate.
- Grammar `grammar-0.2.0`: current collection reporting from `metrics_r20261024c.json` is **5,864 / 7,145 fully parsed abilities (82.1%)**, 0% reviewed. Earlier report states 5,621/6,858 (82.0%) for an older collection scope. Keep snapshot dates explicit.
- Evaluator `mtg_eval 0.3.0+kb2`: 13 descriptive October 25 reports, but only 4–31 of ~60–65 nonland cards fully typed per deck (median 10). Do **not** equate goldfish lethal bounds with multiplayer wins or treat reports as deck rankings.
- Frozen October 20 predictions must not be modified in hindsight; score against later reported games as supported, contradicted or untested.

## Access map

- [MtG Google Drive folder](https://drive.google.com/drive/folders/1ybacqfJehp06beZ7lBgKbfMtWJ2JxayL): living documents and current canonical Sheet.
- [Claude handoff folder](https://drive.google.com/drive/folders/1k2AK8IZ4tpxG1dpPrnmlZXTw8KjRzGFd): current-state note, START_HERE, accepted A1–A7, KB release notes and all-deck report headlines.
- Full local handoff ZIP from October 25: KB release, 13 detailed deck reports, frozen predictions, grammar code and review material. The separate grammar database ZIP is optional for querying/rebuilding.
- [Google Doc — canonical entry/integration map](https://docs.google.com/document/d/1EYmUrBVBoY6Zko7b2q5FAfub4y_gvQqugliGDdpcLm8/edit).
- [Google Doc — grammar/contract standard](https://docs.google.com/document/d/1XPUSdBnCAwXABn6njeCPq2PHmEIYNTM8nmTW4DUXTNk/edit).
- [Google Doc — evaluator validation register](https://docs.google.com/document/d/1OSB9RUI73hDpVxJeTq1wrPEzOJJ0JcHrpFJoODbTe-g/edit).

## Workflow: ask what decision is at stake

- **Card text or interaction:** verify exact rules text, qualified hooks, controller/actor, timing, object identity, and event-vs-state effects. Grammar edges are candidate discovery until reviewed.
- **Deckbuilding:** establish dated current 100-card list and commander; honor owner-only construction unless changed; separate confirmed allocations from proposed swaps. Analyze effective density, overlapping functional redundancy, ordinary deck needs, antagonisms, mana and low-tutor reliability.
- **Portfolio movements:** inspect free copy counts, donor decks, protected slots, and replacement cascades. No inferred transfers from a plan or simulator suggestion.
- **Simulation:** show model/Sheet version, typed mechanic coverage, assumptions, optimistic bounds and comparison to real games. Reject unsupported certainty.
- **Governance:** version new compatibility decisions, record precise exceptions and rationale, update the live Sheet only under archive-then-clone; do not silently rewrite historical ontology text.

## Read next

`01_GRAMMAR_CONTRACT_VERIFICATION.md` for Oracle→DIO review and runtime gates; `02_EVALUATOR_VALIDATION_REGISTER.md` for empirical tests; `DIO_v3.1.1_A1-A7_COMPATIBILITY_ACCEPTED.md` for accepted vocabulary. For the dated full state see Claude's October 25 current-state note in the handoff folder.
