-- Collection database: a bring-your-own inventory for the MtG tools.
-- Ownership and deck allocation live here; card data (Oracle text, types, legality) is a
-- cached copy of Scryfall/Oracle data or of the user's own Sheet columns, never an authority.
-- kb/inventory_adapter.py reads this file through the `collection_rows` and `allocation_rows`
-- views, which present the same columns as the Sheet's Collection and Deck Allocations tabs.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta(
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- One row per card name. The name is the join key for every other table.
CREATE TABLE IF NOT EXISTS cards(
  card_name        TEXT PRIMARY KEY,
  oracle_text      TEXT,
  type_line        TEXT,
  mana_cost        TEXT,
  mana_value       REAL,
  color_identity   TEXT,             -- WUBRG order, 'C' for colorless
  keywords         TEXT,             -- '; ' separated
  produces         TEXT,             -- mana symbols the card can produce, WUBRGC order
  power            TEXT,
  toughness        TEXT,
  rarity           TEXT,
  commander_legal  TEXT,             -- 'Legal' | 'Not legal'
  can_be_commander TEXT,             -- 'Yes' | 'No' (index hint)
  etb_tapped       TEXT,             -- lands: 'Yes' | 'No' | 'Conditional'; others 'N/A' (index hint)
  scryfall_url     TEXT,
  oracle_id        TEXT,
  roles            TEXT,             -- your own '; ' separated tags; unverified hints
  card_data_source TEXT,             -- 'scryfall-bulk:<sha12>', 'scryfall-api:<date>', 'import:<source>', or NULL
  extra_json       TEXT NOT NULL DEFAULT '{}'   -- any other Sheet columns, kept verbatim
);

-- What you physically own. Several rows per card are fine (printings, binders, imports).
-- Owned quantity = SUM(quantity). Re-importing a source replaces that source's rows only.
CREATE TABLE IF NOT EXISTS holdings(
  id               INTEGER PRIMARY KEY,
  card_name        TEXT NOT NULL REFERENCES cards(card_name) ON UPDATE CASCADE,
  quantity         INTEGER NOT NULL CHECK (quantity >= 0),
  source           TEXT NOT NULL,    -- import label, e.g. 'moxfield', 'binder-2', 'sheet'
  set_code         TEXT,
  collector_number TEXT,
  finish           TEXT,
  language         TEXT,
  condition        TEXT,
  notes            TEXT
);
CREATE INDEX IF NOT EXISTS holdings_card ON holdings(card_name);

-- Deck allocation. Status 'Current deck' means the copies are physically sleeved in that deck;
-- 'Companion' is held by the deck outside its 100. Any other status is a plan, not a move.
CREATE TABLE IF NOT EXISTS deck_cards(
  id         INTEGER PRIMARY KEY,
  deck       TEXT NOT NULL,
  card_name  TEXT NOT NULL REFERENCES cards(card_name) ON UPDATE CASCADE,
  quantity   INTEGER NOT NULL CHECK (quantity >= 0),
  section    TEXT NOT NULL DEFAULT '',     -- 'Commander', 'Companion', 'Nonland', 'Land' or ''
  status     TEXT NOT NULL DEFAULT 'Current deck',
  extra_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS deck_cards_deck ON deck_cards(deck);

-- Other Sheet tabs carried through verbatim (e.g. the canonical Sheet's Mechanics tabs).
-- They stay candidate annotations, exactly as in the Sheet.
CREATE TABLE IF NOT EXISTS sheet_rows(
  tab        TEXT NOT NULL,
  row_number INTEGER NOT NULL,
  row_json   TEXT NOT NULL,
  PRIMARY KEY (tab, row_number)
);

-- Provenance of every import and enrichment run.
CREATE TABLE IF NOT EXISTS imports(
  id          INTEGER PRIMARY KEY,
  utc         TEXT NOT NULL,
  kind        TEXT NOT NULL,          -- csv | xlsx | decklist | enrich
  source      TEXT NOT NULL,
  file_name   TEXT,
  sha256      TEXT,
  rows        INTEGER,
  notes       TEXT
);

DROP VIEW IF EXISTS owned;
CREATE VIEW owned AS
  SELECT c.card_name, COALESCE(SUM(h.quantity), 0) AS owned
  FROM cards c LEFT JOIN holdings h ON h.card_name = c.card_name
  GROUP BY c.card_name;

DROP VIEW IF EXISTS physically_assigned;
CREATE VIEW physically_assigned AS
  SELECT card_name, SUM(quantity) AS assigned
  FROM deck_cards WHERE status IN ('Current deck', 'Companion')
  GROUP BY card_name;

-- Same columns as the Sheet's Collection tab (header names are the adapter's contract).
DROP VIEW IF EXISTS collection_rows;
CREATE VIEW collection_rows AS
  SELECT c.card_name                         AS "Card Name",
         o.owned                             AS "Known Qty (min)",
         COALESCE(a.assigned, 0)             AS "Copies in Decks",
         o.owned - COALESCE(a.assigned, 0)   AS "Copies Free",
         c.mana_cost                         AS "Mana Cost",
         c.mana_value                        AS "Mana Value",
         c.color_identity                    AS "Color Identity",
         c.type_line                         AS "Type Line",
         c.rarity                            AS "Rarity",
         c.roles                             AS "Roles",
         c.oracle_text                       AS "Oracle Text",
         c.power                             AS "Power",
         c.toughness                         AS "Toughness",
         c.keywords                          AS "Keywords",
         c.produces                          AS "Produces",
         c.etb_tapped                        AS "ETB Tapped",
         c.commander_legal                   AS "Commander Legal",
         c.can_be_commander                  AS "Can Be Commander",
         c.scryfall_url                      AS "Scryfall URL",
         CASE WHEN o.owned > 0 THEN 'Yes' ELSE 'No' END AS "Ownership",
         c.extra_json                        AS extra_json
  FROM cards c JOIN owned o ON o.card_name = c.card_name
  LEFT JOIN physically_assigned a ON a.card_name = c.card_name;

DROP VIEW IF EXISTS allocation_rows;
CREATE VIEW allocation_rows AS
  SELECT id, card_name AS "Card Name", deck AS "Deck", status AS "Status",
         quantity AS "Quantity", section AS "Section", extra_json
  FROM deck_cards;
