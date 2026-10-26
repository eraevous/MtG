-- MTG Portable Card Knowledgebase v0.2 (schema 0.2.1, 2026-10-22): additive migration over v0.1. No v0.1 table is altered.
-- Authorities: the working Sheet for inventory (cards.*); the matched Oracle refresh record for rules text (rules_text).
-- Layering: Sheet (source) -> versioned import (v0.1 tables) -> derived facts -> operation contracts
--           -> validation queue -> append-only human review overlay -> compiled actions -> evaluator.
CREATE TABLE schema_migrations(version TEXT PRIMARY KEY, applied_utc TEXT NOT NULL, tool TEXT NOT NULL, notes TEXT);

-- 1. Persisted machine readings (0.3.0 readers run once, offline). Keyed by the exact runtime input.
CREATE TABLE derived_facts(
 fact_kind TEXT NOT NULL, input_key TEXT NOT NULL, card_name TEXT NOT NULL REFERENCES cards(card_name),
 value_json TEXT NOT NULL, derivation_version TEXT NOT NULL,
 PRIMARY KEY(fact_kind, input_key, card_name));
CREATE INDEX idx_facts_card ON derived_facts(card_name);

-- 2. Card identity. oracle_id stays NULL until an explicit Oracle refresh run supplies it.
CREATE TABLE card_identity(
 card_name TEXT PRIMARY KEY REFERENCES cards(card_name), oracle_id TEXT, layout TEXT,
 printing_set TEXT, printing_number TEXT, scryfall_url TEXT,
 identity_source TEXT NOT NULL, refresh_run_id TEXT);
CREATE TABLE card_faces(
 card_name TEXT NOT NULL REFERENCES cards(card_name), face_index INTEGER NOT NULL, face_name TEXT NOT NULL,
 mana_cost TEXT, type_line TEXT, oracle_text TEXT, face_source TEXT NOT NULL, refresh_run_id TEXT,
 PRIMARY KEY(card_name, face_index, face_source));

-- 3. Oracle refresh: explicit, versioned, never inside a user query, never overwrites cards.*.
CREATE TABLE oracle_refresh_runs(
 run_id TEXT PRIMARY KEY, source_kind TEXT NOT NULL, source_name TEXT NOT NULL, source_sha256 TEXT NOT NULL,
 source_updated_at TEXT, started_utc TEXT NOT NULL, tool_version TEXT NOT NULL,
 cards_matched INTEGER, cards_unmatched INTEGER, discrepancies INTEGER, notes TEXT);
CREATE TABLE external_oracle(
 run_id TEXT NOT NULL REFERENCES oracle_refresh_runs(run_id), card_name TEXT NOT NULL REFERENCES cards(card_name),
 oracle_id TEXT, layout TEXT, external_text TEXT, external_text_sha256 TEXT, faces_json TEXT, legal_commander TEXT,
 match_status TEXT NOT NULL CHECK(match_status IN ('identical','normalized_equal','differs','not_found')),
 PRIMARY KEY(run_id, card_name));
CREATE TABLE qa_queue(
 qa_id TEXT PRIMARY KEY, issue_type TEXT NOT NULL, card_name TEXT, severity TEXT NOT NULL,
 opened_by TEXT NOT NULL, opened_utc TEXT NOT NULL, details_json TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'open' CHECK(state IN ('open','acknowledged','resolved_by_review','wont_fix')));

-- 3b. Targeted reconciliation (append-only; source of truth overrides/oracle_reconciliation.jsonl) and the rules-text layer.
CREATE TABLE oracle_reconciliation(
 seq INTEGER PRIMARY KEY, reconciliation_id TEXT NOT NULL UNIQUE, card_name TEXT NOT NULL REFERENCES cards(card_name),
 oracle_run_id TEXT NOT NULL, oracle_id TEXT, category TEXT NOT NULL, material INTEGER NOT NULL, fields_json TEXT NOT NULL,
 sheet_value TEXT, oracle_value TEXT, decision TEXT NOT NULL,
 evaluator_reads TEXT NOT NULL CHECK(evaluator_reads IN ('oracle','sheet','excluded')),
 quarantine_contracts INTEGER NOT NULL, identity_confirmed INTEGER, proposed_sheet_correction TEXT,
 reviewer TEXT NOT NULL, source TEXT NOT NULL, recorded_utc TEXT NOT NULL);
CREATE TRIGGER oracle_reconciliation_append_only_u BEFORE UPDATE ON oracle_reconciliation BEGIN SELECT RAISE(ABORT,'oracle_reconciliation is append-only'); END;
CREATE TRIGGER oracle_reconciliation_append_only_d BEFORE DELETE ON oracle_reconciliation BEGIN SELECT RAISE(ABORT,'oracle_reconciliation is append-only'); END;
CREATE VIEW effective_reconciliation AS SELECT r.* FROM oracle_reconciliation r
 WHERE r.seq=(SELECT MAX(seq) FROM oracle_reconciliation x WHERE x.card_name=r.card_name);
-- one row per card: which text is the rules authority, and whether the card's identity is confirmed
CREATE TABLE rules_text(
 card_name TEXT PRIMARY KEY REFERENCES cards(card_name), authority TEXT NOT NULL, oracle_run_id TEXT, oracle_id TEXT,
 rules_text TEXT, rules_text_sha256 TEXT, inventory_text_sha256 TEXT NOT NULL, match_status TEXT,
 identity_confirmed INTEGER NOT NULL, material_discrepancy INTEGER NOT NULL, evaluator_reads TEXT NOT NULL, reconciliation_id TEXT);
CREATE TABLE rules_text_lines(card_name TEXT NOT NULL REFERENCES cards(card_name), line_no INTEGER NOT NULL, line TEXT NOT NULL,
 PRIMARY KEY(card_name, line_no));
-- DIO compatibility addendum (versioned registry delta, addendum/registry_delta_*.json)
CREATE TABLE ontology_addendum(addendum TEXT NOT NULL, kind TEXT NOT NULL, value TEXT NOT NULL, decision TEXT, definition_json TEXT NOT NULL,
 PRIMARY KEY(addendum, kind, value));

-- 4. Operation contracts: drafted from Mechanics · Operations candidates. Versioned; never edited in place.
CREATE TABLE operation_contracts(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, contract_sha256 TEXT NOT NULL,
 card_name TEXT NOT NULL REFERENCES cards(card_name), source_operation_id TEXT REFERENCES candidate_operations(operation_id),
 face TEXT, exact_text TEXT NOT NULL, oracle_text_sha256 TEXT NOT NULL, operation_kind TEXT NOT NULL,
 contract_json TEXT NOT NULL, proposed_action_json TEXT, drafter_version TEXT NOT NULL, drafted_utc TEXT NOT NULL,
 PRIMARY KEY(contract_id, contract_version));
CREATE INDEX idx_contract_card ON operation_contracts(card_name);
CREATE VIEW current_contracts AS SELECT c.* FROM operation_contracts c
 WHERE contract_version=(SELECT MAX(contract_version) FROM operation_contracts x WHERE x.contract_id=c.contract_id);
CREATE TABLE validation_checks(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, check_id TEXT NOT NULL,
 result TEXT NOT NULL CHECK(result IN ('pass','warn','fail')), detail TEXT,
 PRIMARY KEY(contract_id, contract_version, check_id));

-- 5. Human review overlay: append-only. Source of truth is overrides/review_overlay.jsonl, replayed on every build.
CREATE TABLE review_overlay(
 seq INTEGER PRIMARY KEY, review_id TEXT NOT NULL UNIQUE,
 subject_kind TEXT NOT NULL CHECK(subject_kind IN ('operation_contract','capability_claim','card_projection','card_identity')),
 subject_id TEXT NOT NULL, card_name TEXT NOT NULL REFERENCES cards(card_name),
 decision TEXT NOT NULL CHECK(decision IN ('verified','contradicted','rejected','needs_review','revoked')),
 reviewer TEXT NOT NULL, reviewed_utc TEXT NOT NULL, source TEXT NOT NULL,
 oracle_text_sha256 TEXT NOT NULL, contract_sha256 TEXT, tests_json TEXT NOT NULL, notes TEXT, supersedes TEXT,
 rules_text_sha256 TEXT, scope TEXT NOT NULL DEFAULT 'semantic', test_results_json TEXT,
 CHECK(decision<>'verified' OR (json_array_length(tests_json)>0 AND length(source)>0)));
CREATE TRIGGER review_overlay_append_only_u BEFORE UPDATE ON review_overlay BEGIN SELECT RAISE(ABORT,'review_overlay is append-only'); END;
CREATE TRIGGER review_overlay_append_only_d BEFORE DELETE ON review_overlay BEGIN SELECT RAISE(ABORT,'review_overlay is append-only'); END;
-- latest decision per subject, and whether it still applies to today's text and contract
CREATE VIEW effective_reviews AS
 SELECT r.*, CASE
   WHEN r.oracle_text_sha256 <> cd.oracle_text_sha256 THEN 'stale_text_changed'
   WHEN r.rules_text_sha256 IS NOT NULL AND r.rules_text_sha256 <> (SELECT rules_text_sha256 FROM rules_text t WHERE t.card_name=r.card_name) THEN 'stale_rules_text_changed'
   WHEN r.subject_kind='operation_contract' AND r.contract_sha256 IS NOT NULL
        AND r.contract_sha256 <> (SELECT contract_sha256 FROM current_contracts k WHERE k.contract_id=r.subject_id) THEN 'stale_contract_changed'
   ELSE 'current' END AS applicability
 FROM review_overlay r JOIN cards cd USING(card_name)
 WHERE r.seq=(SELECT MAX(seq) FROM review_overlay x WHERE x.subject_kind=r.subject_kind AND x.subject_id=r.subject_id);

CREATE VIEW validation_queue AS
 SELECT k.contract_id, k.contract_version, k.card_name, k.operation_kind, k.exact_text,
  (SELECT COUNT(*) FROM validation_checks v WHERE v.contract_id=k.contract_id AND v.contract_version=k.contract_version AND v.result='fail') AS fails,
  (SELECT COUNT(*) FROM validation_checks v WHERE v.contract_id=k.contract_id AND v.contract_version=k.contract_version AND v.result='warn') AS warns,
  e.decision AS review_decision, e.applicability AS review_applicability,
  CASE
   WHEN EXISTS (SELECT 1 FROM effective_reconciliation z WHERE z.card_name=k.card_name AND z.quarantine_contracts=1) THEN 'quarantined'
   WHEN e.decision='verified' AND e.applicability='current' THEN 'semantic_reviewed'
   WHEN e.decision IN ('rejected','contradicted') AND e.applicability='current' THEN 'rejected'
   WHEN e.decision IS NOT NULL AND e.applicability<>'current' THEN 'review_stale'
   WHEN (SELECT COUNT(*) FROM validation_checks v WHERE v.contract_id=k.contract_id AND v.contract_version=k.contract_version AND v.result='fail')>0 THEN 'blocked'
   ELSE 'ready_for_review' END AS queue_state
 FROM current_contracts k
 LEFT JOIN effective_reviews e ON e.subject_kind='operation_contract' AND e.subject_id=k.contract_id;

-- 6. Compiler output: only semantically reviewed contracts whose compile is lossless. Rebuilt every build.
CREATE TABLE compiled_actions(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, card_name TEXT NOT NULL,
 compiler_version TEXT NOT NULL, action_json TEXT NOT NULL, review_id TEXT NOT NULL,
 PRIMARY KEY(contract_id, contract_version, compiler_version));

-- 7. Build provenance and archive guard.
CREATE TABLE import_runs(
 run_id TEXT PRIMARY KEY, kind TEXT NOT NULL, input_name TEXT NOT NULL, input_sha256 TEXT NOT NULL,
 source_drive_id TEXT, source_modified_utc TEXT, archive_guard TEXT NOT NULL, built_utc TEXT NOT NULL, tool TEXT NOT NULL);

-- 8. Verification states (schema 0.2.1). Semantic review (human) and runtime certification (build) are separate.
-- What the 0.3.0 engine would lose if it ran the contract's action. No losses = runtime_compilation_complete.
CREATE TABLE compile_losses(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, compiler_version TEXT NOT NULL, loss_code TEXT NOT NULL, detail TEXT NOT NULL,
 PRIMARY KEY(contract_id, contract_version, compiler_version, loss_code, detail));
-- Issued by the build (scenarios.py runtime harness), never by a reviewer.
CREATE TABLE runtime_certifications(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, contract_sha256 TEXT NOT NULL, scenario_id TEXT NOT NULL,
 scenario_sha256 TEXT NOT NULL, compiler_version TEXT NOT NULL, oracle_run_id TEXT, action_sha256 TEXT NOT NULL,
 expected_json TEXT NOT NULL, observed_json TEXT NOT NULL, passed INTEGER NOT NULL, issued_by TEXT NOT NULL, issued_utc TEXT NOT NULL,
 PRIMARY KEY(contract_id, contract_version, scenario_id, compiler_version));
CREATE TABLE contract_verification(
 contract_id TEXT NOT NULL, contract_version INTEGER NOT NULL, card_name TEXT NOT NULL,
 oracle_identity_confirmed INTEGER NOT NULL, rules_text_current INTEGER NOT NULL, semantic_contract_reviewed INTEGER NOT NULL,
 runtime_compilation_complete INTEGER NOT NULL, runtime_scenario_tested INTEGER NOT NULL, mechanically_supported INTEGER NOT NULL,
 quarantined INTEGER NOT NULL, detail_json TEXT NOT NULL, PRIMARY KEY(contract_id, contract_version));
CREATE INDEX idx_cv_card ON contract_verification(card_name);
-- the evaluator only ever receives actions that passed all six states
CREATE VIEW runtime_verified_actions AS
 SELECT a.card_name, a.contract_id, a.action_json FROM compiled_actions a
 JOIN contract_verification v ON v.contract_id=a.contract_id AND v.contract_version=a.contract_version
 JOIN validation_queue q ON q.contract_id=a.contract_id AND q.contract_version=a.contract_version
 WHERE v.mechanically_supported=1 AND q.queue_state='semantic_reviewed';
