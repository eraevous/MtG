# Module: kb.build
> Rebuild the derived SQLite KB (v0.2) from the v0.1 import, the append-only review overlay and Oracle refresh snapshots. The KB is derived: rebuilt, never hand-edited.

@ai-path: kb.build
@ai-source-file: kb/migrate_v02.py
@ai-role: store_builder
@ai-intent: "Rebuild the derived SQLite KB (v0.2) from the v0.1 import, the append-only review overlay and Oracle refresh snapshots. The KB is derived: rebuilt, never hand-edited."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: bridge_v02, contracts, counters, freeze_check, kb_policy, kbfacts, oracle_refresh, reconcile, review, scenarios, sqlite_bridge
@ai-contracts: P-01, P-03

### Inputs and outputs
| Direction | What |
|---|---|
| In | mtg_cards.sqlite (v0.1), overrides/*.jsonl, refresh/*.jsonl |
| Out | mtg_cards_v0.2.sqlite (not in Git) |

### Risks, invariants and known gaps
- Verification states: ready_for_review, blocked, quarantined, semantic_reviewed, rejected, review_stale. Nothing is auto-promoted, and nothing is mass-approved.
- Semantic review and runtime readiness are separate states. A human 'verified' must cite passing scenarios.
- Test test_rebuild_is_byte_identical_under_another_hash_seed fails here (challenge C-001).
- Capability (role) claims come from Oracle-text regexes in vendor/mtg_eval/semantics.py. `machine_supported` means only that a pattern matched; nobody reviewed it. The role summary (kbq.overlap) reports them as detected candidates (`sole_detected_candidates`, `reviewed_role_counts`). kb patch 3 (r20261028) excludes flicker, own-side and helper/blocker-only scopes from `wipe`. kb patch 4 (r20261030) reads roles that live only in reminder text by name: predefined tokens (Treasure, Gold, Lander, Powerstone, Clue, Food) and token-making keywords (afterlife, living weapon, incubate, ...). Reminder text stays stripped.
- Counter identity (r20261031, counters.py): every contract carries `counters.facets` ({role, kind, holder}; kind is +1/+1, -1/-1, a named kind, `any` for generic wording, or `present_kinds` for proliferate), and `derived_facts` holds card-level `counter_facets` that add keyword macros (persist, infect, wither, modular, sagas, ...), "enters with" lines and granted keywords, with an order-of-operations note for cards that enter with -1/-1 counters (CR 614.1c, 704.3, 704.5f, 704.5q). Facets are drafted, never reviewed. counters.py is a second reader of counter text beside the grammar layer's counter_kind (C-017): converge them, don't grow both.
- Sagas, faces and copies (r20261104, sagas.py saga-copy-0.1.0, drafter 0.6.0; C-024): clauses on multi-face cards are located on a face from the Oracle refresh faces when the inventory row is not split; an activated ability with no recorded payment reads its printed cost from the clause; a chapter ability on a Saga face is a trigger on `counter.put` (lore, subject this, chapter numbers; CR 714.2b-c) with a `saga` block (all chapters, final chapter, read ahead, lifecycle CR 714.3-714.4); `token.create` carries `copy_of` (target, self, referent, chosen) and counters put on the token are a `counter.put` with `recipient: created_token`. C06 is a warn, not a fail, for a `requires_manual_annotation` chapter row whose trigger the saga drafter supplied (D-0025, accepted by Zach 2026-11-04). All drafted, never reviewed.

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
