# Vision

The authoritative purpose statement is `codex_++/project.purpose.md` (P-00). This file gives the longer view.

## What Zach wants

A better tool to build decks, and ultimately one that makes the Bullshit Factory "not suck". The old workflow helped in three ways, at different phases:

- **Conceive**: articulating the intended machine when starting or overhauling a deck.
- **Explore**: surfacing interactions, especially unconventional, distributed ones (the mesh thesis: consistency from many possible solutions, not fewer).
- **Compile**: judging individual card slots against the deck's purpose and the cards he actually owns.

He builds from boosters, precons and his existing collection, and does not buy singles. He dislikes infinite loops as a deck's purpose, though incidental loops are welcome.

## Why the ontology came first

Discovery comes before judgment. The Deck Interaction Ontology makes relationships across mechanics expressible (bounce, blink, sacrifice, counters, object identity, recursion), so that unconventional interactions can be found before anyone knows whether they are good. Building the ontology was itself a form of discovery.

## What went wrong before, and what this repo guards against

In October 2026 a run of locally reasonable steps turned a semantic-representation project into a simulator. The simulator became the authority on what cards meant, while the ontology sat disconnected. No test failed. The AEC layer here (`codex_++/`, `decisions/`, `challenges/`, `tools/drift_check.py`) exists to make that kind of drift visible early.

It must not repeat the mistake one level up: **the repository is infrastructure for the Magic project, not the other way round.** Governance features have to justify their cost.

## Near-term milestones

1. **Viable repo** (this import): someone can clone it, run the tests, find the authority for any deck decision, and extend the project without breaking its purpose.
2. **First decision capability**: one real deck decision moves through Conceive → Explore → Compile using existing capabilities (KB queries, discovery, evaluator), with inspectable provenance.
3. **First evidence**: score the 2026-10-20 frozen predictions against games played since, if any. Reproduce the Dina, Vraska and Factory distinctions without passing off explanations as predictions. Then freeze one new counterfactual.

## Open scope question

Charter v0.1 keeps automated Oracle parsing and a comprehensive KB *out of* the foundational core, yet `grammar/` and `kb/` already exist here. Are they extensions the core consumes, or part of the core? This is challenge C-002, and Zach decides it.
