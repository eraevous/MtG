# Collection operations: intake, checkout, and reconciliation

Status: proposed operational design, 2026-11-07. Intake's **staging/reconciliation** slice is implemented; checkout and writeback are **not** implemented or authorized by this document. Zach's live Google Sheet titled exactly **MTG Master Inventory — Canonical** is the ownership authority. Never reuse an archived ID, never infer a physical move from a recommendation, and never write to that Sheet from these tools without separately authorized archive-then-clone operations.

## System boundary

These are distinct facts:

1. **Card identity/printing:** Scryfall set + collector number, face, finish, language; independently checked, never a custody assertion.
2. **Physical ownership/custody:** confirmed quantity and location, established by Zach or Steph, not by Scryfall or KB.
3. **Allocation:** whether a physically owned copy is in a built deck, free, checked out for evaluation, or reserved in a *proposal*.
4. **Mechanical interpretation:** Oracle/Comprehensive Rules and candidate DIO/KB annotations. Intake and checkout do not classify abilities.

The canonical Sheet stores ownership and existing deck assignments. A separate append-only operational journal is proposed for receipts and movements, reconciled into the Sheet only after approval. The KB is derived from snapshots and must not be used as the source of live quantities.

## Workflow map

| Workflow | Input | Output | Side effects | State |
|---|---|---|---|---|
| **Intake capture** | Voice transcript, photo or product/card list | Original words, identity candidates, printings | None | PR #36, pending review |
| **Intake reconciliation** | Verified entries + latest canonical Collection values export | Per-copy details, proposed quantity delta, before/after, exceptions | None; read-only report | Implemented by `collection/intake_reconcile.py` |
| **Intake approval/writeback** | Reviewed receipt, current Sheet revision, Zach/Steph confirmation | Archive, clone, applied values, readback and new snapshot | Controlled inventory modification | Proposed, NOT implemented |
| **Card Checkout** | Exact copy, source location, intended deck/purpose, requester | Checkout receipt, due/return status, owner agreement | No deck movement until physical confirmation | Proposed |
| **Card Return** | Checkout receipt and observed return | Custody restored, exception if missing/damaged | Controlled movement record | Proposed |
| **Swap / Transfer** | Named cuts and adds in two active decks | Atomic, reversible allocation plan with donor impact | Requires explicit approval and physical confirmation | Proposed |
| **Decommission** | Retiring deck, destination decks | Release audit and custody ledger; protected agreement | Donor deck retired only when physically confirmed | `mtgtools release` supports analysis, transaction not implemented |
| **Audit / Sync** | Current Sheet, physical spot-check and journal | Deltas, conflicts, stale KB/release flags | None without approval | Proposed |
| **Checkout Suggestions** | Newly free cards and deck gaps | Suggestions only, with custody class | Never an allocation | Proposed |

### Intake state machine

`CAPTURED → IDENTIFIED → REVIEW_REQUIRED / READY_FOR_REVIEW → APPROVED → APPLIED → VERIFIED`

* Every original voice line remains attached to the resulting row. A card's set, number and finish are separate fields. Repeated cards/printings are **not** deduplicated as physical copies.
* `review`/`unresolved` identities are never included in the quantity proposal. Similar names/aliases are quarantined, not silently merged. A blank foil field means **unknown**, not nonfoil.
* Quantity deltas are additive **exactly once per approved receipt**; source checksum/batch ID must be checked against a persistent journal before actual writeback. This stage is proposal-only, so rerunning it cannot double-count the canonical Sheet.
* Existing physical allocations and protected-deck copies do not change during intake. Newly confirmed copies normally increase `Copies Free` by the number added, subject to reconciliation of anomalous existing rows.
* The writeback implementation must re-resolve the Sheet by **exact title** immediately before application, verify latest revision and unchanged before-values, archive/clone, apply only reviewed rows, and read back. If any conflict, stop without partial application.
* Preserve both a per-printing receipt and per-card consolidated totals. Inventory-level quantities lose foil/collector detail; don't erase the printing ledger.
* Propagate into a new dated snapshot and KB release only after the canonical Sheet has been verified. KB freshness and inventory freshness are independent.

### Staging CLI (implemented)

First, identify dictated names and printings through PR #36 (when available):

```bash
python3 collection/voice_intake.py dictated.txt \
  --review voice_review.json --csv intake_verified.csv
```

Export the **current, exact-title** canonical Sheet's `Collection` tab to CSV (values, header on row 4). Check its source title; do not use a `_ARCHIVE` file or a stale saved Sheet ID. Then:

```bash
python3 collection/intake_reconcile.py \
  --collection canonical_Collection_export.csv \
  --intake voice_review.json \
  --source-title 'MTG Master Inventory — Canonical' \
  --output data/intake_20261107_review
```

For already-reviewed rows, use `--intake intake_verified.csv`. The JSON version keeps ambiguous/unresolved lines in the review packet; the accepted CSV contains only positively identified rows. Use `--require-finish` if unknown finishes must be held until physical inspection.

Outputs:
* `intake_detail.csv`: individual cards with set/number/finish, original dictation when provided.
* `proposal.csv`: before/after **proposed minimum quantities**, estimated new free copies, deck allocation unchanged, explicit review flags.
* `review.json`: exception list and source hashes; state is always `PROPOSAL_ONLY_NOT_APPLIED`.

**Important:** PR #36's verified CSV does not currently preserve a foil/finish field from dictation. Add finish to the capture/accepted CSV contract before treating it as a lossless ingestion path for the November 7 seven-foil batch. Without that, review the `Voice intake` staging workbook and add a `Finish` column to the CSV before running reconciliation. A `Finish` value must be explicitly observed, never guessed.

The command validates named headers, rejects source-title mismatches, preserved existing deck copies, checks quantities and reports absent/ambiguous names as candidates rather than claiming they are unowned. It never modifies the Sheet, the KB, or a deck.

## Card Checkout — proposed transaction model

A checkout is **physical custody**, not a recommendation or virtual reserve. Suggested record (append-only):

`event_id`, `copy_identifier (printing + local copy_id when available)`, `card_name`, `source_location`, `destination`, `requester`, `authorized_by`, `protected_deck_agreement`, `observed_at`, `status`, `batch_id`, `reason`, `sheet_revision_before/after`.

Suggested states: `REQUESTED → APPROVED → CHECKED_OUT → RETURNED`, or `CANCELLED`/`MISSING` with explicit exception reasons. A user can reserve a card conceptually without checking it out. Checkout cannot silently cross the protected TMNT, Ashling, Rootha or Dina boundary. Cards in other built decks require agreement, and a checkout must name the intended return location.

Two-phase transaction: (1) propose/validate available copy and permission, (2) physical move confirmed and journaled; synchronize the canonical Sheet with archive/clone/readback. On failure, leave physical state as reported and flag reconciliation, never invent a successful return. Avoid introducing a second authority for deck membership: the journal is evidence of movement, the Sheet remains the canonical reflection.

## Validation gates to build next

1. Provenanced receipt ID and persistent deduplication/journal, including authorization signatures and re-run protection.
2. Archive/clone/write/readback adapter to Google Sheets with optimistic row-version checks.
3. Checkout/return atomic allocation checks, protected donor approvals and stale-copy conflict cases.
4. Ability to compare a newly received card to decks **as a recommendation only** using KB/Oracle evidence, with availability labels.
5. Repeat 60-card voice benchmark and 85-card DMR/FRA fixture validation, including six repeated names, seven foils and the unresolved DMR Plains.

This workflow deliberately keeps identity, custody, interpretation, and deck-building decisions separate. It is not an ontology extension and makes no claims about card mechanics.
