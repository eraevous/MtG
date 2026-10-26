-- Portable MTG Collection and Card-Semantics Knowledgebase v0.1.
-- Source facts, machine hypotheses, and verified rulings MUST remain distinguishable.
PRAGMA foreign_keys=ON;
CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE source_snapshots(source_id INTEGER PRIMARY KEY,source_name TEXT NOT NULL,source_url TEXT,sha256 TEXT NOT NULL,source_kind TEXT NOT NULL,imported_utc TEXT NOT NULL,notes TEXT);
CREATE TABLE cards(
 card_name TEXT PRIMARY KEY,owned_min INTEGER NOT NULL CHECK(owned_min>=0), assigned INTEGER NOT NULL CHECK(assigned>=0), free INTEGER NOT NULL,
 availability_stored TEXT, color_identity TEXT,mana_cost TEXT,mana_value REAL,type_line TEXT,rarity TEXT,roles_stored TEXT,
 oracle_text TEXT,oracle_text_sha256 TEXT,keywords_stored TEXT,produces_stored TEXT,etb_tapped_stored TEXT,
 power_stored TEXT,toughness_stored TEXT,commander_legal_stored TEXT,can_be_commander_stored TEXT,
 scryfall_url TEXT,ownership_stored TEXT,alias_stored TEXT,collection_row INTEGER,raw_json TEXT NOT NULL,
 CHECK(free=owned_min-assigned));
CREATE TABLE deck_allocations(
 row_id INTEGER PRIMARY KEY, card_name TEXT NOT NULL REFERENCES cards(card_name), deck TEXT NOT NULL,
 status_raw TEXT NOT NULL, status_group TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>=0),section TEXT,
 physically_assigned INTEGER NOT NULL,counts_in_deck_100 INTEGER NOT NULL,raw_json TEXT NOT NULL);
CREATE INDEX idx_alloc_deck ON deck_allocations(deck,status_group);
CREATE INDEX idx_alloc_card ON deck_allocations(card_name,status_group);
CREATE TABLE candidate_operations(
 operation_id TEXT PRIMARY KEY,card_name TEXT NOT NULL REFERENCES cards(card_name),source_row INTEGER,
 face_scope TEXT,operation_kind TEXT,oracle_clause TEXT,observes_hook TEXT,requirement_groups TEXT,alternatives TEXT,
 result_produces TEXT,payment_consumes TEXT,modifies TEXT,timing TEXT,qualifiers TEXT,object_transition TEXT,
 source_status TEXT NOT NULL,source_confidence TEXT,source_url TEXT,review_note TEXT,
 verification_status TEXT NOT NULL DEFAULT 'unverified_candidate',raw_json TEXT NOT NULL);
CREATE INDEX idx_candidate_card ON candidate_operations(card_name);
CREATE INDEX idx_candidate_hook ON candidate_operations(observes_hook);
CREATE TABLE capability_claims(
 card_name TEXT NOT NULL REFERENCES cards(card_name),capability TEXT NOT NULL,source TEXT NOT NULL,
 claim_status TEXT NOT NULL,evidence_text TEXT,projection_version TEXT NOT NULL,
 PRIMARY KEY(card_name,capability,source));
CREATE INDEX idx_claim_role ON capability_claims(capability,claim_status);
CREATE TABLE projected_abilities(
 card_name TEXT NOT NULL REFERENCES cards(card_name),ability_index INTEGER NOT NULL,kind TEXT NOT NULL,
 hook TEXT, hook_details_json TEXT,cost_json TEXT,gates_json TEXT,outputs_json TEXT,
 clause TEXT,unread TEXT,projection_status TEXT NOT NULL,projection_version TEXT NOT NULL,raw_ability_json TEXT NOT NULL,
 runtime_verification TEXT NOT NULL DEFAULT 'unverified_machine_projection',
 PRIMARY KEY(card_name,ability_index));
CREATE INDEX idx_projection_hook ON projected_abilities(hook);
CREATE TABLE projected_card_statics(card_name TEXT PRIMARY KEY REFERENCES cards(card_name),statics_json TEXT NOT NULL,unread_json TEXT NOT NULL,
 projected_ability_count INTEGER NOT NULL,unread_fragment_count INTEGER NOT NULL,projection_status TEXT NOT NULL,projection_version TEXT NOT NULL);
CREATE TABLE typed_profiles(card_name TEXT PRIMARY KEY REFERENCES cards(card_name),profile_json TEXT NOT NULL,projection_version TEXT NOT NULL,
 verification_status TEXT NOT NULL DEFAULT 'unverified_machine_projection');
CREATE TABLE manual_reviews(card_name TEXT NOT NULL REFERENCES cards(card_name),operation_id TEXT, review_scope TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('verified','contradicted','rejected','needs_review')), reviewer TEXT NOT NULL,
 reviewed_utc TEXT NOT NULL, source TEXT NOT NULL, notes TEXT,
 PRIMARY KEY(card_name,review_scope,source));
CREATE TABLE source_sheet_rows(sheet_name TEXT NOT NULL,row_number INTEGER NOT NULL,values_json TEXT NOT NULL,
 PRIMARY KEY(sheet_name,row_number));
CREATE TABLE qa_issues(issue_type TEXT NOT NULL, card_name TEXT, severity TEXT NOT NULL, details_json TEXT NOT NULL);
CREATE INDEX idx_qa_issue ON qa_issues(issue_type,severity);
CREATE VIEW active_deck_cards AS SELECT deck,card_name,quantity,section FROM deck_allocations WHERE counts_in_deck_100=1;
CREATE VIEW physical_card_locations AS SELECT card_name,deck,SUM(quantity) AS quantity FROM deck_allocations WHERE physically_assigned=1 GROUP BY card_name,deck;
CREATE VIEW deck_card_counts AS SELECT deck,SUM(quantity) AS total_cards FROM active_deck_cards GROUP BY deck;
-- A claim labeled machine_supported is a text pattern prediction, NOT an official rules verification.
CREATE VIEW candidate_capability_index AS SELECT c.card_name,c.capability,c.source,c.claim_status,cd.free,cd.assigned,cd.color_identity
 FROM capability_claims c JOIN cards cd USING(card_name);
CREATE VIRTUAL TABLE card_fts USING fts5(card_name,oracle_text,roles_stored,type_line,content='cards',content_rowid='rowid');
CREATE TABLE reference_documents(doc_id TEXT PRIMARY KEY,title TEXT NOT NULL,doc_kind TEXT NOT NULL,sha256 TEXT NOT NULL,content_text TEXT NOT NULL);
CREATE TABLE ontology_domains(domain TEXT PRIMARY KEY,purpose TEXT,status TEXT,source TEXT,source_location TEXT,definition_json TEXT NOT NULL);
CREATE TABLE review_backlog(card_name TEXT PRIMARY KEY REFERENCES cards(card_name),priority_score INTEGER NOT NULL,reason TEXT NOT NULL,
 operation_candidate_count INTEGER NOT NULL,unread_fragment_count INTEGER NOT NULL,projection_status TEXT NOT NULL);
CREATE INDEX idx_review_priority ON review_backlog(priority_score DESC,card_name);
