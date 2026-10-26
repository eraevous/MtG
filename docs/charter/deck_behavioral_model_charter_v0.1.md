# Deck Behavioral Model: Foundational Charter (proposed v0.1)

**Status: proposed, pending Zach's review.** Drafted by Kate with build-project Claude in the coordination thread (2026-10-26). The text below is verbatim. Amendments follow it; they have not been merged into the text.

---

Build a small, inspectable, AI-assisted system for understanding, constructing, and improving Magic: The Gathering decks through three phases: **Conceive** (articulate the intended machine), **Explore** (discover plausible interactions and architectures), and **Compile** (verify, compare, and recommend changes). The foundational core will use versioned deck fixtures, explicitly verified interactions, lightweight module and dependency graphs, evidence-supported whole-deck characteristics, and an auditable decision ledger to explain how a deck operates, identify its limiting constraints, and predict the direction of proposed changes. Dimensions must earn their place through demonstrated usefulness rather than theoretical elegance. The core explicitly excludes automated Oracle parsing, a comprehensive knowledge base, general-purpose network science, full-game simulation, universal power rankings, and autonomous deck optimization; these remain possible extensions subject to independent validation. **The first proof** will reproduce known distinctions among Dina, Vraska, and the Bullshit Factory without retrospectively treating explanations as predictions, then freeze and evaluate at least one genuinely new counterfactual against subsequent evidence. The repository will demonstrate reproducible analysis, transparent uncertainty, human-controlled decisions, and disciplined AI-assisted development rather than attempting to automate the entire game.

---

## Proposed amendments (not yet merged)

1. **Preserve discovery.** Exploratory interaction hypotheses may come before verification. Only decision-grade claims need the verification gate. Hypotheses between cards, modules or whole decks may exist without first becoming KB contracts. *(Kate, refined by build-project Claude)*
2. **Preserve decision provenance.** Record who proposed, challenged, corrected, accepted or rejected each change, with the reason and evidence. This is a small decision-event record (`decisions/`), separate from KB contract reviews. *(Kate)*
3. **Separate validation modes.** Retrospective reconstruction (the Factory history), observed games (Dina, Vraska, Shanid) and prospective frozen predictions (`predictions/`) are scored separately. A successful retrospective explanation is not a successful prediction. *(Kate)*
4. **Preserve criteria revisions.** "The system shall preserve not only decisions and their evidence, but revisions to the questions, objectives, and criteria governing those decisions, without rewriting earlier judgments." Criteria are versioned (`decisions/criteria/`). *(Kate)*

Converged guidance from the same thread:
- The core orchestrates existing capabilities around a defensible decision. It does not duplicate their implementations.
- The 330-operation mechanics review is off the critical path. Verification happens on demand when a deck decision needs a card, and it covers potentially disqualifying interactions too.
- First demonstration: score the 2026-10-20 frozen predictions if qualifying games exist, alongside the Factory, Dina and Vraska cases. Then freeze a new counterfactual.

Open tensions: challenges C-002 and C-003 in `challenges/ledger.jsonl`.
