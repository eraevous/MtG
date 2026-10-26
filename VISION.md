# VISION — MtG Deck Behavioral Model

@ai-version: 0.1.0-draft · @ai-generated: true · status: proposed, pending Zach's review
Sources: Deck Behavioral Model Charter v0.1 (Kate) + amendments 1–4; AEC hub round 2 (Kate); build-side state 2026-10-25.

## Purpose
Build a small, inspectable, AI-assisted system for understanding, constructing and improving Zach's Magic: The Gathering (Commander) decks through three phases:

- **Conceive:** articulate the machine a deck is meant to be (a deck charter).
- **Explore:** discover plausible interactions and architectures (an interaction map).
- **Compile:** verify, compare and recommend changes (a decision ledger).

The core explains how a deck operates, identifies its limiting constraints, and predicts the *direction* of proposed changes. It does this with versioned deck fixtures, explicitly verified interactions, lightweight module/dependency graphs, evidence-supported whole-deck characteristics and an auditable decision ledger.

## Scope principle
**The core orchestrates existing capabilities around a defensible decision. It does not duplicate them.**

| Layer | Answers | Status |
|---|---|---|
| Inventory (canonical Sheet) | What does Zach own, and where is it? | exists |
| Oracle + grammar layer | What does the card text say, as templates? | exists (v0.2, 0% reviewed) |
| DIO contracts + KB | What do interactions *mean*? | exists (4,961 candidates, 0 verified) |
| Evaluator (mtg_eval) | What do they *contribute*? | exists (0.3.0+kb2, descriptive only) |
| **Decision Model (new core)** | **Why does a contribution matter to this deck, under criteria Zach can deliberately change?** | to build |
| Simulation | Provisional predictions under stated coverage | optional, downstream |

## Non-goals (for the core)
Automated Oracle parsing, a comprehensive knowledgebase, general-purpose network science, full-game simulation, universal power rankings and autonomous deck optimization. These may exist as upstream tools or extensions, but they are not core scope. **An extension is promoted into the core only if it improves a demonstrated decision capability, not merely coverage or sophistication.**

## What the system preserves
- Decisions, with who proposed, challenged, corrected, accepted or rejected them, and why.
- **Revisions to the questions, objectives and criteria governing decisions, without rewriting earlier judgments.** Zach develops the objectives while using the models to interrogate a design (the Factory record shows connectivity → assembly → closing → mesh philosophy).
- Unresolved challenges, until they get an explicit disposition.

## First proof
1. If games have been played since 2026-10-20, score the frozen predictions (`PREDICTIONS_2026-10-20.json`, sha256 18657701…). That validates aspects of the evaluator, not the Decision Model.
2. Reproduce known distinctions among three contrasting cases, without treating explanations as predictions:
   - **Factory:** reconstruct architectural decisions and the changing design criteria.
   - **Dina:** explain a productive engine and an observed resource constraint.
   - **Vraska:** explain an observed failure without pretending it was predicted.
3. Freeze at least one genuinely new counterfactual, and evaluate it only against later evidence.

The first milestone is **one working end-to-end capability with inspectable provenance**, not a general framework. If AEC governance obstructs that, AEC is failing its own purpose test.

## What the repository demonstrates
Reproducible analysis, transparent uncertainty, human-controlled decisions and disciplined AI-assisted development, rather than an attempt to automate the whole game.
