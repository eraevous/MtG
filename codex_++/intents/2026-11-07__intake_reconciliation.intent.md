# Intake reconciliation intent — 2026-11-07

**User goal:** Reconcile recent acquired cards and establish repeatable Intake and Card Checkout workflows. Existing PR #36 performs Scryfall batch identity resolution but does not reconcile ownership or preserve finish in its accepted CSV.

**Implemented scope:** one stdlib read-only CLI, `collection/intake_reconcile.py`, compatible with PR #36 JSON/CSV, plus negative-control unit tests and `docs/COLLECTION_WORKFLOWS.md`. The current canonical Sheet is read by exact title and exported outside this CLI. It is **never** modified.

**Authority:** Sheet for custody, Scryfall for printing identity, rules for mechanics, Zach for design/physical decisions. No DIO edits, new mechanics parser, KB modification, or deck allocation changes. P-01, P-03, P-05, P-06 apply.

**Drift / dissent review:** (1) Potential violation: a second collection ledger becomes competing custody authority. (2) Evidence: existing `collection/mtgcollection.py` has holdings and import sources, and PR #36 already stages another input. (3) Counterargument: this module deliberately stores only a proposed delta with source SHA and no live mutation. (4) If it becomes an independent mutable inventory, it would create conflicting quantities and stale deck assignments. (5) Require an approved archive/clone/readback writeback design before building any `apply` command; tests ensure only proposal files are written.

**Evidence:** tests cover canonical row-four headers, correct Hallowed Fountain/TMNT allocation and new free copy, Ornithopter ≠ Ornithopter of Paradise, duplicate printings, ambiguity quarantine, unaccepted Scryfall matches, unknown foils, mismatched derivations, archived-title rejection and unchanged inputs. No live-network performance or 85-card staging reconciliation is claimed.

**Remaining dependency:** the actual `MTG_Voice_Intake_2026-11-07_DMR_FRA_STAGING.xlsx` from the other chat is required to reconcile all 85 observed physical cards. No individual unretrieved rows were fabricated.
