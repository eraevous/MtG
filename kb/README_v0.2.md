# MTG Card Knowledgebase v0.2 (2026-10-20; schema 0.2.1 on 2026-10-22)

> **Read `RELEASE_NOTES_v0.2.1.md` first.** On 2026-10-22, schema 0.2.1 changed the following:
> - It separates six verification states, so human semantic review is no longer runtime certification.
> - A lossy compile blocks runtime certification.
> - A review must cite scenario ids that pass on the contract.
> - Oracle is now the rules-text authority, with an append-only reconciliation and quarantine.
> - It records the DIO A1–A7 addendum, keeps `actor`, and restores the Offspring rows.
> - Builds are deterministic without `PYTHONHASHSEED`.
>
> The queue state `trusted` is now `semantic_reviewed`, and `compile_trusted()` is now `compile_and_certify()`. The sections below describe v0.2 as of 2026-10-20/21, except where they say otherwise.

Additive layer on Zach's v0.1 package. Nothing in v0.1 was changed: `mtg_cards.sqlite`, `sqlite_bridge.py`,
`mtgdb.py`, `vendor/` and the JSONL exports are as shipped. v0.2 is built from the v0.1 DB by one
deterministic script and adds persisted facts, operation contracts, a validation queue, an append-only
review overlay, an Oracle-refresh path and a compiler stage.

```
working Sheet ──export──> build_mtg_db.py (v0.1 import) ──> migrate_v02.py ──> mtg_cards_v0.2.sqlite
                                                              ▲   ▲                 │
                                 overrides/review_overlay.jsonl   refresh/*.jsonl   ├─> kbq.py, deck_audit.py (discovery, no simulator)
                                 (human reviews, append-only)     (Oracle snapshots) └─> bridge_v02.open_evaluator (mtg_eval 0.3.0)
```

The Sheet is the only source. The DB is derived and can be rebuilt from three inputs: the Sheet export, the
review overlay file and the refresh snapshots. Reviews and refreshes live in files, not only in the DB, so a
rebuild or a parser update can't erase them.

## 1. Verification of v0.1

| Item | Stated in README/handoff | In `mtg_cards.sqlite` | Note |
|---|---:|---:|---|
| Collection rows | 3,372 | 3,372 | 3,364 owned names, 5,426 copies |
| Candidate operations | 4,631 | 4,631 | all `unverified_candidate` |
| Cached typed ability projections | 3,562 | **3,563** | AUDIT.json also says 3,563; the README figure is off by one |
| Capability claims | 25,363 | **25,370** | AUDIT.json also says 25,370; the README figure is off by seven |
| Current 100-card decks | 12 | 12 | all exactly 100; no card is over-allocated |
| Integrity / foreign keys | | ok / ok | v0.1 tests: 11 pass, 1 skipped (needs the xlsx) |

- **Full-corpus parity (the skipped v0.1 test, run another way):** a fresh 0.3.0 parse of every stored row
  matches the cached projections and claim statuses on all 3,366 evaluator cards: 0 mismatches.
- The Sheet's Drive `modifiedTime` is still 2026-10-15T19:03:42.774Z, so the DB is current.
- `vendor/mtg_eval` is byte-identical to the 0.3.0 release in `mechanics-kernel/mtg_eval_release`.
- **Bug fixed:** under the v0.1 bridge, `Evaluator.inventory()` raises `KeyError('export')`.
  `bridge_v02` supplies the missing key.
- **Watch:** six Collection names are excluded by the evaluator's `NON_DECK` list. Three of them are real
  owned cards (Finch Formation ×2, Rust-Shield Rampager ×2, Thornplate Intimidator ×1). They are still in
  SQLite and in discovery queries, but the evaluator can't see them.

## 2. Priority 1: no Oracle regex in the query/evaluation path

`kbfacts.derive` runs every 0.3.0 text reader that the evaluator called at query time **once, offline**, and stores
each result in `derived_facts` (37,026 rows), keyed by the exact input of the runtime call. The readers covered are
`clean`, `clauses`, `clause_audit`, `recursion_types`, `wipe_kind`, `protection_profile`, `resource_claims`, the tutor
filter, token-feedback features, closing-profile features, commander feed and the goldfish `CardModel` for all 32
colour identities. `bridge_v02.open_evaluator()` sends each of those calls to the store.

| Measured over 29 API calls (12 `deck`, 11 `card`, build, compare, upgrades, transfer, portfolio, inventory) | v0.1 bridge | v0.2 |
|---|---:|---:|
| Regex calls during queries | 2,087,946 | 37,014, **all inside `json.decoder`**, none on Oracle text |
| Fact-store misses (strict mode) | n/a | 0 |
| Output | baseline | **identical on all 29 calls** |

A miss means the DB is older than its input. By default the bridge falls back to the reader and counts the miss;
`strict=True` raises instead. Wall time is about the same because the Monte Carlo dominates. The gain is that the
evaluator now uses one persisted reading, not one re-derived on each query.

## 3. Priority 2: candidates → contracts → validation queue → compiler

Each of the 4,631 Mechanics · Operations candidates becomes a versioned contract (`operation_contracts`). The
contract keeps:

- the exact clause and the Oracle SHA it was drafted against;
- the face it sits on;
- the DIO operation kind and hook identifier, checked against the Grammar Registry's hook vocabulary, plus the
  hook's subject (self, others or both);
- requirement groups (AND across groups, OR within a group; triggers, intervening-if, costs and timing
  restrictions as separate groups, each with its exact text);
- parsed cost atoms (registry `cost.family`), effects, zone transitions with continuity, timing speed and turn scope;
- modality (may/must), granted quoted abilities and qualifiers;
- an explicit `unbound` list;
- full source evidence (row, status, confidence, URL, review note and the untouched legacy fields).

Where a 0.3.0 projected ability matches the clause, it is attached as `proposed_action`. That is the executable shape.

**Update 2026-10-21 (drafter 0.3.0):** contracts now have the DIO §5 `operation` shape, mana is typed and hooks carry
qualifiers. See [ONTOLOGY_ALIGNMENT.md](ONTOLOGY_ALIGNMENT.md). The figures below are from the 0.3.0 rebuild.

There are 15 deterministic checks, C01–C15. Any `fail` blocks the contract:

| Queue state | Contracts |
|---|---:|
| ready_for_review | 1,617 (1,051 of them carry an executable action) |
| blocked | 3,014 |
| trusted | **0** (nothing is trusted without a review) |

The main reasons a contract is blocked:

- **1,024 have unbound semantics:** an inner "if", "instead", "unless", per-mode outputs, or a cost substitution. "For each" and X are now bound as amplifiers.
- **2,031 have a 0.3.0 action that drops text or disagrees with the contract.**
- 812 have no recorded effect.
- 253 source rows still need manual annotation.
- 178 multi-face clauses aren't located on a face.
- 162 have an unclassified kind.
- **47 legacy "operations" are reminder text** (for example the earthbend reminder "When it dies or is exiled,
  return it…"). These belong in the keyword's definition, not in a separate operation.

`compile_trusted()` compiles only contracts whose **latest** review is `verified` and still applies. The compiled action
goes to `runtime_verified_actions`, and the bridge attaches it to the runtime record as `verified_actions`. Today
the compiled action is the same 0.3.0 ability the engine already runs, so it adds a trust marker and doesn't change
behaviour. Engine code that prefers verified actions is the next step.

## 4. Priority 3: discovery from SQLite (`kbq.py`)

These queries work with no simulator coverage. Every answer names its evidence level (reviewed, machine_supported,
machine_inferred, tag_only, contradicted) and its contract state.

```
kbq.py card NAME                    custody, identity, claims by evidence, contracts + failing checks, reviews
kbq.py destinations NAME            every current deck: legal? already there / free copy / transfer from
kbq.py available ROLE --ci BG --free
kbq.py overlap DECK                 role counts, single-source roles, multi-role cards (tags excluded)
kbq.py unverified --deck DECK       tag-only and contradicted claims, contracts with no review
kbq.py theme landfall --deck DECK   themes: landfall, dredge, repeatable_recursion, land_search,
                                    land_tokens_scaling, sacrifice_conversion, self_mill, extra_land_drops
kbq.py packages --ci WBG --deck Necrobloom --theme landfall
                                    producer→observer links via shared hooks; status 'candidate' unless both sides are trusted
kbq.py queue --deck DECK --state ready_for_review
```

Example: the Necrobloom landfall package has 11 land producers (Cultivate, Kodama's Reach, Springbloom Druid, Evolving
Wilds and others) feeding 4 landfall payoffs (The Necrobloom, Avenger of Zendikar, Ride the Shoopuf, Weather Maker).
All the links are `candidate`.

## 5. Priority 4: Oracle refresh as an explicit, versioned operation

`oracle_refresh.py snapshot` compares the stored text with a Scryfall bulk *Oracle Cards* file. It writes one
immutable `refresh/oracle_refresh_<date>_<run>.jsonl` snapshot. On every build, `migrate_v02.py --refresh-dir` replays
all snapshots:

- `external_oracle` gets the external text, `oracle_id`, faces and Commander legality for each card;
- `card_identity` and `card_faces` get `oracle_id` and the real faces;
- each difference opens a `qa_queue` item. The severity is `high` if the card has a verified review.

It never edits `cards` or reviews. `card_identity` also holds the printing (set and collector number) from the
inventory's Scryfall URL.

**First real refresh (2026-10-21, `oracle_refresh-0.2.1`, run `7e517de93bb47238`):** Scryfall `oracle_cards` bulk
updated 2026-10-21T09:01:59Z. Scryfall now publishes this bulk file only as `.jsonl.gz`, so convert it to a JSON array
before `snapshot` (one `json.loads` per line). 3,371 of 3,372 cards have an `oracle_id`; `Elemental` (a token name)
has none. QA opened 208 `oracle_text_discrepancy`, 3 `oracle_name_spelling` and 1 `oracle_card_not_found` items.
See `reports/oracle_refresh_2026-10-21.md`.

0.2.1 matching: when several Oracle objects share a name, prefer playable, Commander-legal, non-`funny` ones
(0.2.0 picked a `funny` *Pick Your Poison* and Jumpstart front cards for *Savage Lands* and *Earth Rumble*). It also
falls back to a diacritic- and punctuation-blind name, which opens an `oracle_name_spelling` QA item.

## 6. Priority 6: append-only review overlay

`review.py add` appends one line to `overrides/review_overlay.jsonl`. Each line records the reviewer, source,
timestamp, Oracle SHA, contract SHA, tests and an optional `supersedes`, and lines are hash-chained.

- It refuses a `verified` decision with no test or no source.
- It refuses a review against an Oracle SHA or contract SHA that isn't current, or against a contract with failing checks.
- In the DB, triggers forbid UPDATE and DELETE on `review_overlay`.
- `effective_reviews` takes the latest line per subject and marks it `stale_text_changed` or `stale_contract_changed`.
  A stale review drops the contract to `review_stale` and removes its compiled action. A parser update can't reverify
  changed text, and it can't overwrite a human review either.

## 7. Priority 5: Necrobloom audit

The audit is in `reports/audit_Necrobloom.md`, with `.csv` and `.json`. The review packet is
`reports/review_packet_Necrobloom.md`.

- **60** nonland cards and 112 candidate operations; 21 contracts are ready for review and 91 are blocked.
- There are 98 unread clauses. 56 cards have a partial 0.3.0 projection and 4 are fully parsed.
- Verified reviews: **0**. Compiled actions: **0**.
- Runtime eligibility: 12 cards are eligible after review, 5 are reviewable but have no executable action,
  40 are blocked, and 3 have no candidate operations (Mirkwood Pathmaker, Mulch, Rootborn Defenses).

Necrobloom has the most blocked contracts of the 12 decks (91; the next highest is Counter Blitz with 78).

By theme:

- **Landfall:** 4 payoffs. Avenger's counters and Ride the Shoopuf are reviewable. The commander's token trigger is
  blocked because the seven-names "instead" branch is unbound, and 0.3.0 drops it.
- **Dredge:** completely unmodelled. "Land cards in your graveyard have dredge 2" is a draw-replacement static,
  and no reader or engine path exists for it.
- **Repeatable recursion:** 11 hits, 0 ready. 7 are earthbend reminder text, which should become one `earthbend`
  keyword macro. Pothole Mole and Primary Research are blocked on dropped text.
- **Land search:** 6 cards. 5 are blocked because the 0.3.0 action loses the "one to battlefield, one to hand"
  split. The Earth King is reviewable.
- **Land tokens and scaling:** Avenger's "for each land you control" ETB is read as one token, and Necrobloom's
  seven-names threshold is unbound.
- **Sacrifice conversions:** Aron and Rat King are reviewable. All-Fates Scroll's X-scaled draw is blocked.

Across the 12 decks, 10–40 cards per deck are eligible after review: Vraska 40, Sharuum 32, Ashling 25, Dina 22,
Necrobloom 12.

## 8. Priority 7: archive policy

- `migrate_v02.py` and `freeze_check.py guard-input` refuse any build input whose name or path marks it as an archive.
- `freeze_check.py status --live-modified <Drive modifiedTime>` says whether the DB was built from the Sheet's
  current revision. Today it is current.
- `freeze_check.py verify-freeze` checks a frozen `_ARCHIVE` copy against the live export (the Collection and Deck
  Allocations values) and appends the result to a manifest. Run it before any structural change.
- Every DB connection in kbq, deck_audit, review and the bridge is read-only. Nothing writes to the Sheet.

## Rebuild and test

```
python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl \
    --refresh-dir refresh --source-modified 2026-10-15T19:03:42.774Z --built-utc 2026-10-22T12:00:00+00:00
python -m unittest test_v02.py test_mtg_db.py test_acceptance.py   # 61 tests; no hash-seed pinning needed since 0.2.1
python parity_v01.py .                                              # cached vs fresh 0.3.0, all cards
python parity_eval.py regex|facts|policy mtg_cards_v0.2.sqlite out.json
python deck_audit.py Necrobloom --out reports
python release.py --out <dir>                                       # self-contained release + SOURCE_MANIFEST + MANIFEST.sha256
```

## What is still open

1. **Reviews.** Nothing is verified. The fastest real gain is to work through `review_packet_<deck>.md`. Necrobloom
   has 34 contracts in its packet (lands included), and each needs a named test.
2. **Drafter binding for blocked semantics:** modes, "instead" branches, intervening/inner "if", "for each"/X scaling
   and keyword macros (earthbend, dredge). These cover most blocked contracts. They need a new drafter version, and
   the new version leaves existing reviews stale instead of inheriting them.
3. **Engine use of `verified_actions`,** and readers for dredge (draw replacement), land-count scaling and split
   search destinations.
4. **`oracle_id`:** done 2026-10-21 (3,371/3,372). Next is the Sheet review of the QA items in
   `reports/oracle_refresh_2026-10-21.md`.
5. **Candidate coverage gaps:** at least 3 Necrobloom nonland cards have no Mechanics · Operations row (Mulch among
   them), so themes can't find them through contracts.
