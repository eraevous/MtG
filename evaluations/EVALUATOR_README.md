# mtg-eval 0.3.0: Commander evaluation over the canonical inventory

`mtg-eval` is one program for card, deck, module, swap, build, inventory, transfer and portfolio questions. Every question reads the same inventory and the same card record.

The program never writes to the inventory. Swaps and transfers are hypothetical: they are reported, never applied.

It uses only the Python standard library. It needs Python 3.9 or later; it was tested on 3.13.

## Install and run

```sh
# from this folder; no network access and no dependencies needed
python3 -m mtg_eval --workbook /path/to/export.xlsx deck Vraska
# or install the `mtgeval` command
pip install .            # use `pip install --no-build-isolation .` when offline
mtgeval --workbook /path/to/export.xlsx deck Vraska
```

- **Workbook:** export the live canonical sheet as `.xlsx`: the one titled exactly "MTG Master Inventory — Canonical", with no `_ARCHIVE` suffix (id `1f83bN2ULQmXJQkkRL_JxPvzq9gWMYwLFobhATCjkCpU` as of 2026-10-25; the id changes with every archive-then-clone). Do not use an archived workbook.
- **Environment variable:** instead of passing `--workbook` every time, you can set `MTG_WORKBOOK=/path/to/export.xlsx`.
- **Options:** `--games N` sets the number of goldfish games per deck version (default 5000). `--json` gives machine-readable output, and `--out file.md` saves the report.
- **Turn engine:** `--engine-games N` sets games per engine scenario (default 300; `0` turns the engine off for a quick report). A deck report runs nine scenarios and takes about 10 to 40 seconds.
- **Option order:** global options can go before or after the subcommand (`deck Vraska --games 100` works).
- **Reproducibility:** set `PYTHONHASHSEED=0` to get identical numbers from run to run.
- **New export:** `mtgeval --workbook new.xlsx regress tests/expected_<sha12>.json` lists every number that moved. Nothing is accepted automatically; regenerate the snapshot with `tools/make_expected.py` only after reading the list, and say why in CHANGELOG.md.

## The questions it answers

| Question | Command | Example |
|---|---|---|
| What does this card do, and what does the evaluator miss? | `card NAME [--deck D]` | [card_altered_ego](examples/card_altered_ego.md), [card_inspiring_call](examples/card_inspiring_call.md) |
| How does this deck work, and where is it thin? | `deck NAME` | [Vraska](examples/deck_Vraska.md), [Sharuum](examples/deck_Sharuum.md), [Shanid](examples/deck_Shanid.md), [Brigid](examples/deck_Brigid.md), [Rootha](examples/deck_Rootha.md), [TMNT](examples/deck_TMNT.md) |
| How often can this multi-card module assemble? | `module DECK MODULE` | [TMNT go_wide](examples/module_tmnt_go_wide.md), [Dina aristocrats](examples/module_dina_aristocrats.md) |
| Is this substitution better? | `compare DECK "OUT=IN" ...` | [TMNT Knockout](examples/compare_tmnt_knockout.md), [Counter Blitz Duty](examples/compare_counter_blitz_duty.md) |
| What are the best upgrades? | `upgrades DECK [--protect D ...] [--transfers] [--top 5]` | [Sharuum, never from Dina](examples/upgrades_sharuum_no_dina.md), [Vraska](examples/upgrades_vraska.md) |
| Build a deck around this commander from free cards | `build COMMANDER` | [Balmor](examples/build_balmor.md) |
| State of the collection | `inventory` | [inventory](examples/inventory.md) |
| What happens if this card moves? | `transfer CARD FROM TO [--backfill C] [--cut C]` | [Cauldron Dina → Necrobloom](examples/transfer_cauldron.md) |
| Where should one free copy go? | `portfolio CARD [--objective ROLE]` | [Duty Beyond Death](examples/portfolio_duty.md) |

Kate's example ("Evaluate Sharuum against my entire free pool, identify the three weakest functional areas, and show me the best five potential upgrades without raiding Dina") is this one command:

```sh
mtgeval upgrades Sharuum --protect Dina --transfers --top 5
```

## How to read a report

Every report has the same parts.

| Part | What it tells you |
|---|---|
| Summary | The answer, in a few lines. |
| **Conclusive** | `yes` only when every card involved is fully understood and every cut is mechanically audited. Otherwise the result is a playtest candidate, and the line says why. |
| Sections | Tables with the evidence. |
| Engine routes (deck, module) | Which card's output starts which other card's ability, classed as parallel producers, linear payoffs, feed-forward chains, replacement amplification, scaling, bounded or unbounded feedback, and resource-quality feedback. None of these means "good" by itself. |
| Resource ledger and bottlenecks (deck) | From the turn engine: bodies available, what each was spent on (attack, station, crew, mana, other costs), what stayed idle, and which claim most often went unmet each turn. Three policies show who should get a contested body. |
| Closing and resilience (deck) | Unopposed goldfish conditional lethal (an upper bound), damage against light blockers, a destroy wipe, an exile wipe, commander removal with tax, attrition (wipe plus three more commander removals) and a no-commander ablation, all on the same shuffles. |
| Engine coverage | Which cards the engine reads fully and the text it does not read. Cards act in the engine only through the parts that were read. |
| Count screen (deck) | The 0.2.0 counts and flags. Their thresholds were set after the Vraska game, so they are labelled post-hoc. |
| Uncertainty | What the evaluator could not price in these cards: copy effects, X costs, repeatable triggers, counter movement, unconfirmed inventory tags. |
| Not modelled | The model's standing limits: no opponents, no resource competition, and coverage targets that are heuristic. |

**Fallback.** When a card is only partly understood, the report still gives the parts it can establish and names what is missing. It never claims certainty it does not have.

**Probabilities.**
- "Seen by T7" is exact finite-deck math on the draw: 7 cards plus 7 draws from the 99.
- Multi-card modules use inclusion–exclusion over the shared library, never products of independent chances.
- Goldfish rates come from a seeded simulation. A swap compares the same shuffles before and after, so the paired change has a small standard error. That error measures sampling only, not model error.

**Cut labels:**
- `protected`: a coarse flag fires.
- `human_review_required`: the card has abilities the evaluator does not price.
- `mechanically_audited_cut`: every clause is priced.

None of these labels means "safe to cut"; the owner decides.

## Architecture (frozen for this release)

| Module | Responsibility | Replaces |
|---|---|---|
| `inventory.py` + `_adapter.py` | Read-only Collection and current-deck custody, through Kate's stdlib adapter reader. Each deck is 100 cards; a companion sits outside the 100. | `evalcore.Inventory`, `deck_view.py` |
| `semantics.py` | The shared card record (Oracle rules, inventory tags, hand labels, evidence status), typed readings (wipe kind, protection scope, recursion destination, referent and cadence) and the clause audit. | `capabilities.py`, `validation.py` (typing and audit) |
| `access.py` | Exact draw access, module access, deck states, goldfish simulation, ablation. | `access.py` |
| `deckeval.py` | Coverage bands, module contracts on the kernel's three-valued gates, one-slot fit, transactions, inventory census, construction. These are the pre-kernel deckbuilding checks. | `evalcore.py` |
| `cuts.py` | Coarse screen, then clause audit, then a cut label. | `validation.py` (gates) |
| `structure.py` | The 0.2.0 count screen (claims by card, closing profile, commander dependence). Its compounding flag is retired. | none (new in 0.2.0) |
| `abilities.py` | Typed ability records: hook, cost, gates (sorcery speed, once per turn), outputs, confidence and unread text. | none (new in 0.3.0) |
| `engine.py` | Turn engine with object identities and the resource ledger; policies; named scenarios. | none (new in 0.3.0) |
| `routing.py` | Event routing between cards and engine classes. | the 0.2.0 compounding check |
| `scenarios.py` | The scenario set, summaries, ledger rows, bottlenecks, and paired before/after for swaps and upgrades. | none (new in 0.3.0) |
| `api.py` | The single `Evaluator` with the nine queries. | `run_demos.py`, `run_access.py`, `run_validation.py` |
| `report.py`, `cli.py` | Markdown and JSON output, and the command line. | none (new) |
| `_kernel.py` | The vendored reviewed kernel (gate_and and gate_or). | `kernel_v0_3_1_reviewed/` |

The ontology is not changed. Probabilities and simulations live only in the evaluation layer.

The older scripts in `../parsimony-swap/` stay as the frozen record of earlier rounds (README, CROSS_SCALE, ACCESS, VALIDATION). They are not deleted.

## Tests

```sh
python3 -m unittest discover -s tests -t .                                        # 38 tests without a workbook (units + Kate's R1-R6)
MTG_WORKBOOK=/path/to/export.xlsx PYTHONHASHSEED=0 python3 -m unittest discover -s tests -t .   # + 17 tests on the real inventory
```

Kate's acceptance tests (2026-10-19 handoff):

| Test | Where | What it checks |
|---|---|---|
| R1 tap contention | `tests/test_engine.py` | One Sculpture attacks and, with vigilance, stations after combat; station-first spends it before combat; a second Sculpture adds an action; a body is spent once. |
| R2 new-token timing | `tests/test_engine.py` | A summoning-sick Sculpture cannot tap for its own mana but can pay station and crew; crew sums power, station uses one creature's power; no station on the opponents' turns. |
| R3 event routing | both | Vraska + Stridehangar + Fireweaver: two artifact entries, two drains; Sai never triggers from tokens, only from casting an artifact spell. |
| R4 bounded Sharuum feedback | both | Mechan Assembler makes one Robot per turn; Pactdoll Terror sees every entry; the report never says Sharuum has no payoffs. |
| R5 four classes | `tests/test_engine.py` | Parallel producers, linear payoff, replacement amplification and bounded feedback are separate; an amplifier is not a producer. |
| R6 commander and wipes | both | Tax grows by 2; no commander means no commander tokens; destroy and exile differ in death triggers; artifacts survive a creature wipe. |
| R7 cross-deck and holdout | `tests/test_regression.py` | The engine runs on all 12 decks with coverage; predictions are frozen in `predictions/` with labels. |
| R8 every query | `tests/test_regression.py` | All nine queries run, and deck, module, compare and upgrades carry engine output. |
| R9 honesty labels | `tests/test_regression.py` | Reports label unopposed lethal as conditional, the count screen as post-hoc, and show engine coverage. |

**Snapshots.** Snapshots are keyed by the export's sha256, so a different export skips the snapshot test (it is not a pass). Use `regress` to see what moved.

**Example reports.** `sh tools/make_examples.sh export.xlsx` regenerates `examples/`.

**Predictions.** `tools/predict.py export.xlsx` freezes pre-game predictions for every deck in `predictions/` and prints the file's sha256.

## Semantic-coverage backlog (prioritised)

Each item is a class of mechanics, not a single card. Until an item is done, cards in that class are reported as only partly understood, and comparisons involving them are not conclusive.

1. **Conditional and partial protection: started.**
   - Done: scope typing (all creatures, creatures with counters, up to N targets, single target), and what each effect survives.
   - Next: count the protected creatures on a modelled board, against wipes at named turns.
2. **Counter preservation across zone changes: flagged, not priced.**
   - Covers Resourceful Defense, Yuna, Grand Summoner and Nesting Grounds.
   - Next: model where the counters go and what receives them.
3. **Recursion destination: typed** by destination, referent and cadence.
   - Next: price sustained loops (sacrifice, return, sacrifice again).
4. **Clone and copy effects: flagged.**
   - Next: list the copy targets in the deck and on a modelled board.
5. **Repeatable operations: flagged.**
   - Next: per-turn cadence, so a repeatable source is worth more than a one-shot.
6. **Resource competition: simulated (0.3.0).**
   - Done: object-level ledger in the turn engine, with vigilance, summoning sickness, station/crew rules and three policies.
   - Next: smarter policies (choose per turn by expected damage), and equipment.
9. **Post-wipe recovery: scenarios (0.3.0).** Destroy, exile, commander removal, attrition, ablation.
10. **Closing: conditional (0.3.0).** Unopposed lethal and light blockers. Next: blockers with real sizes and fliers drawn from typical pods.
11. **Ability typing breadth (P2).** Most cards outside Vraska and Sharuum are only partly read (see Engine coverage in each deck report). Next: modal spells, equipment, counters-matter payoffs, death triggers with sacrifice outlets, driven by the cards with the most unread text in the decks that get scored.
7. **Operational modules beyond Leonardo.**
   - Next: cast-and-connect layers for counters (Tidus), aristocrats and artifacts.
8. **Opponent scenarios.**
   - Next: a handful of named threats (wipe on turn N, removal on the commander) instead of a full opponent simulator.
