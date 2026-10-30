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
@ai-dependencies: bridge_v02, contracts, freeze_check, kb_policy, kbfacts, oracle_refresh, reconcile, review, scenarios, sqlite_bridge
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

### Notes
- Drafted by the AEC session from the 2026-10-25 handoff docs, as an import-time description. Build-project Claude should review it, and this note goes away once it has.
