# MTG Card Knowledgebase v0.2.1, post-refresh release (2026-10-22)

This release responds to Kate's independent review of v0.2 (2026-10-21) and to the scope Zach and Kate set on 2026-10-22: the four P0 fixes, the actor field kept, A1–A7 recorded as a compatibility addendum, acceptance tests T1–T8, a targeted Oracle reconciliation, and the Offspring rows restored.

- No contract was approved. The review overlay is still empty.
- The Sheet was not read, written or exported.
- No physical card was moved.

```
Sheet (inventory authority) ─export─> v0.1 import ─> migrate_v02.py ─> mtg_cards_v0.2.sqlite ─> kbq / deck_audit / evaluator
                                                       ▲      ▲       ▲          ▲        ▲
         refresh/*.jsonl (Oracle = rules authority) ───┘      │       │          │        └ addendum/registry_delta_v0.1.json
         overrides/oracle_reconciliation.jsonl (append-only) ─┘       │          └ scenarios/*.json (tests)
         overrides/review_overlay.jsonl (semantic reviews, append-only)
```

## Verification state, as built

| State (per contract) | Contracts | How it is set |
|---|---:|---|
| `oracle_identity_confirmed` | 4,631 / 4,631 | A matched refresh record, with no reconciliation saying the identity is wrong |
| `rules_text_current` | 4,623 | The clause matches the Oracle rules text after representational normalisation. The 8 that don't are 4 quarantined and 4 real wording differences (listed in `reports/verification_summary_2026-10-22.json`). |
| `semantic_contract_reviewed` | 0 | A current human `verified` review that cites passing scenarios |
| `runtime_compilation_complete` | 418 | The 0.3.0 engine action loses nothing the contract says (`compile_losses` is empty) |
| `runtime_scenario_tested` | 1 | A build-issued runtime certificate. Cremate "Draw a card." shows it is independent of review. |
| `mechanically_supported` | 0 | All five states above, and not quarantined. Only these reach the evaluator as `verified_actions`. |

Queue states:

- 1,607 `ready_for_review`. 1,059 of these carry an action, and 394 compile losslessly.
- 3,020 `blocked`.
- 4 `quarantined`.
- 0 `semantic_reviewed`. This state was called `trusted` in v0.2.

Compared with v0.2, 11 contracts moved from ready to blocked. The projection matcher (`clause_key`) used to depend on the hash seed. It now always attaches the right 0.3.0 projection, and for these 11 that projection drops text (C11).

## P0 fixes

1. **Verification states are separate.** The six states above are materialised in `contract_verification`.
   - A human review is semantic only (`scope: semantic`). The overlay refuses any other scope.
   - Runtime certificates (`runtime_certifications`) are issued by the build from scenario runs, with:
     - the scenario sha;
     - the contract sha;
     - the compiler version;
     - the Oracle run id;
     - the action sha;
     - expected vs observed values.
   - The harness (`scenarios.run_action`) resolves the action in a bare 0.3.0 engine `Game`.
2. **A lossy compile blocks runtime certification.** `contracts.runtime_losses` lists every way the 0.3.0 action would lose what the contract says. The compiler refuses any compile with a loss, and a reviewed contract with a lossy compile opens a QA item. Loss codes, by number of contracts:

   | Loss code | Contracts | Notes |
   |---|---:|---|
   | `unread_text`, `partial_projection` | 2,058 | |
   | `no_action` | 1,279 | |
   | `target_lost` | 1,095 | includes Cremate |
   | `zone_transition_lost` | 817 | includes Cremate's graveyard → exile and Cultivate's split |
   | `branch_unbound` | 700 | |
   | `output_not_executed` | 652 | the engine ignores `interaction`, `removal`, `recursion`, … |
   | **`mana_type_lost`** | **414** | every `mana.add`. Orzhov Basilica {W}{B}, Crystal Grotto {C} and Great Forest Druid's any colour all record "N mana" in 0.3.0. This was check C15. |
   | `amplifier_lost` | 260 | |
   | `modes_lost` | 260 | |
   | `granted_ability` | 134 | |
   | `optional_lost` | 117 | |
   | `cost_lost` | 96 | |
   | `cost_mana_type_lost` | 51 | |
   | `distribution_lost` | 39 | the engine puts "+1/+1 on each Plant" on one creature. This includes Avenger of Zendikar. |
   | `observer_relation_lost` | 10 | |
   | `batching_lost` | 4 | |
   | `capacity_lost` | 4 | |
3. **Approval needs a real test.**
   - `review.py` resolves every `--test` to a scenario in `scenarios/*.json`.
   - The scenario must name the contract and its semantic assertions must pass on the current contract version.
   - Placeholders (`scenario:<name>`), labels and unknown ids are refused. Results are recorded in the review line.
   - The review packets no longer print a placeholder. They list the scenarios that cover the contract, or say that one must be written first.
   - The 13 scenarios in `scenarios/kb_scenarios.json` are acceptance evidence, not approvals.
4. **Authorities.**
   - The Sheet is the inventory authority (`cards.*`, never edited).
   - The matched Oracle refresh record (run `7e517de93bb47238`) is the rules-text authority. It lives in the `rules_text` and `rules_text_lines` tables.
   - Material Sheet/Oracle differences quarantine the card's contracts: Medic's Kitesail ×1, Polliwallop ×2 and Whiplash Wordsmith ×1. The three Offspring rows have no candidate operations.
   - A review also pins `rules_text_sha256`, so a later Oracle change makes it `stale_rules_text_changed`.

## Targeted reconciliation (`overrides/oracle_reconciliation.jsonl`, 12 append-only records)

| Card | Category | Evaluator reads | Quarantine | Identity |
|---|---|---|---|---|
| Medic's Kitesail | sheet_error (Equip {3} vs {2}) | Oracle | yes | confirmed |
| Finch Formation, Rust-Shield Rampager, Thornplate Intimidator | sheet_error (Offspring token text and type line) | Oracle text, type line, legality | yes (no contracts) | **not confirmed**: the rows point at the token printing (tblb) |
| Polliwallop | sheet_error (Affinity for Frogs keyword missing) | Oracle | yes | confirmed |
| Whiplash Wordsmith | sheet_error (prepare face missing) | Oracle | yes | confirmed |
| Counters | non_game (Jumpstart front card) | excluded | no | **not confirmed**: matched the {B} card, the Sheet says {G} |
| ______ | non_game (Un-card, not Commander legal) | excluded | no | confirmed |
| Elemental | token_not_card | excluded | no | no oracle_id |
| Dunedain Blade, Gideon the Oathsworn, Sandbender's Storm | name_alias | Sheet | no | confirmed |

The other 200 refresh differences are representational: face headers, reminder text, self-reference, quotes. They change no contract.

`reports/proposed_sheet_corrections.csv` lists 11 Sheet corrections a person may choose to make. None has been applied.

**Offspring rows.** They are restored to the evaluator as asked:

- `kb_policy` replaces mtg_eval's hard-coded `NON_DECK` list with the reconciliation.
- For these rows the evaluator reads the Oracle text, type line and Commander legality, and they appear in `kbq keyword Offspring`.
- But each Sheet row records the token printing, the token text and 1/1 stats, like the Elemental token row. So their identity stays unconfirmed until Zach checks the physical cards.
- Their P/T stay 1/1, because the refresh snapshot carries no P/T.

## Actor (A2) and the addendum (A1–A7)

`actor` is kept, and hooks also carry `relation_to_observer`, `permanent_controller_at_event`, `source_controller` and `owner`. The decisions are in `addendum/DIO_v3.1.1_compat_addendum_v0.1.md`, with `registry_delta_v0.1.json` loaded into the `ontology_addendum` table and the C04 vocabulary. Drafter 0.4.0:

- drafts `permanent.tapped_for_mana`;
- drafts `turn.step.begin` / `turn.phase.begin` (C04 warnings dropped from 197 to 6);
- uses the cardinalities `each_object` and `one_or_more` + `per_event_batch`;
- marks `act_time` (`paid_as_cost` / `on_resolution`);
- records versioned keyword macros;
- splits Cultivate's battlefield/hand destinations.

`events.py` makes A1–A3 executable for tests:

- the tapped-for-mana facet;
- hook matching by actor and controller;
- each vs one-or-more counting;
- payment-time events.

## Determinism (the Grub failure)

The failing parity test came from two set-iteration bugs in mtg_eval 0.3.0. Both are fixed in the vendored copy as `0.3.0+kb2`, and both fixes are marked "kb patch" in the source:

- `semantics.clean` substituted card names in hash-seed order (Grub, Storied Matriarch).
- `routing.build` stored successor sets, so the order of cycles and chains varied.

`contracts.clause_key` had the same name-order bug. Results:

- The build is byte-identical under different `PYTHONHASHSEED` values (T7 rebuilds and compares).
- The suites pass with no seed pinning.
- Evaluator parity, the 0.3.0 regex readers vs persisted facts, holds on 29/29 API calls, run under different hash seeds (`reports/parity_eval_summary.json`).
- With the 0.2.1 inventory policy, only `inventory` and `build: The Necrobloom` change, because their pool now includes the restored rows.

## Discovery additions (`kbq.py`)

- `kbq mana --pays '{C}' --ci BG` lists typed mana sources that can pay a cost.
  - A chosen colour is one of WUBRG, never colourless.
- `kbq keyword Offspring` lists owned cards with a keyword line in the rules text, using Oracle legality.
  - This is an SQL `LIKE` over persisted lines, with no regex at query time.
- `kbq card` now shows the rules-text authority, the reconciliation and the six states for each contract.

## Tests

| Suite | Result |
|---|---|
| `test_v02.py` | 21 tests. The `trusted` assertions are renamed and the reviews use real scenarios. New: a reviewed lossy contract never reaches runtime. |
| `test_mtg_db.py` | 12 tests, 1 skipped (needs the xlsx, as in v0.1) |
| `test_acceptance.py` | T1–T8, 28 tests. 2 expected failures record the known Necrobloom gaps: the seven-names `instead` branch and the dredge grant. |

All suites were run from the extracted release zip without seed pinning. The counts are in `SOURCE_MANIFEST.json`.

## Rebuild

```
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-15T19:03:42.774Z --built-utc 2026-10-22T12:00:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py
```

## Still open

- **Engine.** The 0.3.0 engine can't take typed mana, targets, zone destinations, amplifiers or distribution. Until the compiler emits engine actions from the contract, no mana ability can be runtime-certified.
- **Necrobloom.** Process branches and macro expansion (dredge, earthbend, offspring).
- **Rules-text mismatches.** Four genuine wording differences need a look: Argivian Cavalier, Prudent Fateseer, Tangle Tumbler and Yuriko.
- **Offspring identity.** Zach to confirm cards vs tokens.
