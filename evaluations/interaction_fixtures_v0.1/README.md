# Interaction fixtures v0.1

These are expected-answer fixtures for real interactions the 2026-10-28 paired run found. Kate wrote them on 2026-10-28. There are eight core fixtures, two optional ones, two three-card sequences, and a list of claims the system must not make. All are in `fixtures.json`.

**Verification state.** Kate specified these from card text and rulings. They have not yet been checked against the KB's Oracle snapshot. None of them is a reviewed DIO contract.

**How to use them.** Grade two things separately, as Kate asks:

1. **Mechanical truth.** Is the expected answer right under the rules? This does not depend on what the ontology can represent.
2. **Tool behavior.** Does the tool find the relationship as a candidate? Does it label missing information `unresolved` instead of inventing or rejecting it?

Today's KB does not have to produce a `compatible` link for every fixture. When a link is missing, that is a retrieval or representation gap. When a link is wrong, that is a precision failure. An `unresolved` link that names the missing information can be a calibrated success.

No runner is wired up yet. These are specifications for a later run of mtgtools and for future evaluations.
