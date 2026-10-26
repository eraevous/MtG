# MtG: deck interaction, building and evaluation tools

Zach's Magic: The Gathering (Commander) project. It holds the tools that help him **conceive, explore and compile** decks from the cards he actually owns, plus the governance layer (AEC/Codex++) that keeps AI-assisted development of those tools aimed at that purpose.

> **Status (2026-10-26):** the 2026-10-25 handoff has been imported as-is. Nothing in the mechanics data is human-verified. Every operation and contract is a *candidate*. The evaluator's numbers are descriptive profiles, not rankings. See `docs/handoff/00_CURRENT_STATE.md`.

## Start here

1. `codex_++/project.purpose.md`: what this project is for (P-00) and the five contracts (P-01 to P-05) that changes must not break.
2. `docs/handoff/START_HERE.md` and `docs/handoff/00_CURRENT_STATE.md`: what exists, with its numbers and open decisions.
3. `docs/charter/`: the proposed Deck Behavioral Model charter v0.1, pending Zach's review.
4. `AGENTS.md`: how AI agents (Claude Code, Codex) work in this repo.

## Layout

| Path | What | Authority over |
|---|---|---|
| `kb/` | SQLite knowledgebase v0.2.1 (r20261024d) as released: build, migrate, query (`kbq.py`), audit, review overlay, Oracle refresh snapshots, doctrine (`reference_sources/`), DIO addendum, vendored evaluator `kb/vendor/mtg_eval` (0.3.0+kb2) | derived candidate contracts, never hand-edited |
| `grammar/` | Oracle grammar layer v0.2: Oracle phrases → templates → DIO concepts → candidate contracts; loop discovery; validation | candidate interpretations |
| `review_packet/` | 330 candidate operations in 88 mechanical classes, waiting for Zach's class-level verdicts | none (a review queue) |
| `evaluations/` | Deck reports from 2026-10-25 for all 13 decks | descriptive only |
| `predictions/` | The **frozen** 2026-10-20 predictions. Never edit them; score them only against reported games | prospective evidence |
| `decisions/` | Append-only design decisions and versioned criteria | provenance of design intent |
| `challenges/` | Append-only unresolved objections and known defects | n/a |
| `codex_++/` | Project purpose, module purpose files, drift fixtures | design intent |
| `tools/` | `drift_check.py` (AEC checks), `ast_dependency_extractor.py` | n/a |
| `docs/` | Handoff docs and the charter | n/a |
| `data/` | Where the gitignored databases and inventory export go (see `data/README.md`) | n/a |

The inventory authority is the Google Sheet "MTG Master Inventory — Canonical", not anything in this repo (see `kb/inventory_adapter.py`).

## Run

Python 3.10+, standard library only (one exception is logged as challenge C-004).

```bash
# governance checks and their tests (no data needed)
python3 tools/drift_check.py
python3 -m unittest discover -s tests

# grammar layer unit tests (no data needed)
cd grammar && python3 -m unittest tests.py && cd ..

# KB tests and queries: first put the databases in kb/ (see data/README.md)
cd kb && python3 -m unittest test_v02.py test_mtg_db.py test_acceptance.py
python3 kbq.py card "Emmara, Soul of the Accord"
PYTHONPATH=vendor python3 -m mtg_eval --workbook ../data/<export>.xlsx deck "Token Triumph"
```

Known baseline: 60 of 61 KB tests pass. The reproducibility test fails, and it also fails on the untouched release (challenge C-001).

## Development model

Spec-driven workflows (for example GitHub Spec Kit) may own feature specs, plans and tasks. **AEC owns purpose**: the project contract, decision history and open challenges. A new spec never quietly overrides `codex_++/project.purpose.md`. Conflicts go to Zach with the evidence. See `AGENTS.md` and `CHARTER.md`.
