"""Build the grammar layer: Scryfall Oracle corpus -> abilities -> parts -> frames -> concept edges.

    python3 -I build.py --oracle <oracle-cards-*.jsonl.gz> --kb <mtg_cards_v0.2.sqlite> --out grammar_layer.sqlite

Read-only on both inputs. The collection is identified by oracle_id from the KB's external_oracle table
(the 2026-10-21 refresh). Rebuilding is deterministic for a given Oracle file and code version.
"""
import argparse
import collections
import gzip
import hashlib
import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar as g  # noqa: E402
import concepts as cx  # noqa: E402
import semantics as sm  # noqa: E402

EXCLUDED_LAYOUTS = {'art_series', 'token', 'double_faced_token', 'emblem', 'planar', 'vanguard', 'scheme',
                    'front_card'}
EXCLUDED_SET_TYPES = {'memorabilia', 'token', 'minigame', 'funny', 'alchemy'}

SCHEMA = '''
CREATE TABLE source_manifest(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE card(oracle_id TEXT PRIMARY KEY, name TEXT NOT NULL, layout TEXT, set_code TEXT, set_type TEXT,
  type_line TEXT, in_collection INT NOT NULL, kb_card_name TEXT, scope TEXT NOT NULL, oracle_sha256 TEXT NOT NULL);
CREATE TABLE face(oracle_id TEXT, face_index INT, face_name TEXT, type_line TEXT, oracle_text TEXT,
  PRIMARY KEY(oracle_id, face_index));
CREATE TABLE ability(ability_id INTEGER PRIMARY KEY, oracle_id TEXT, face_index INT, line_index INT,
  ordinal INT, kind TEXT, ability_word TEXT, keyword TEXT, parent_ability INT, granted_by INT, text TEXT,
  reminders_json TEXT);
CREATE TABLE frame(frame_id INTEGER PRIMARY KEY, role TEXT NOT NULL, frame_text TEXT NOT NULL,
  n_parts INT DEFAULT 0, n_cards INT DEFAULT 0, n_collection_parts INT DEFAULT 0, n_collection_cards INT DEFAULT 0,
  UNIQUE(role, frame_text));
CREATE TABLE part(part_id INTEGER PRIMARY KEY, ability_id INT REFERENCES ability(ability_id), ordinal INT,
  role TEXT, surface TEXT, frame_id INT REFERENCES frame(frame_id), bindings_json TEXT, attrs_json TEXT);
CREATE TABLE concept(concept_id TEXT PRIMARY KEY, semantic_type TEXT NOT NULL, dio_ref TEXT NOT NULL,
  dio_status TEXT NOT NULL, label TEXT NOT NULL, event_intent TEXT, note TEXT);
CREATE TABLE frame_concept_edge(frame_id INT REFERENCES frame(frame_id), concept_id TEXT REFERENCES concept(concept_id),
  relation TEXT NOT NULL, slot_map TEXT, rule_id TEXT NOT NULL, status TEXT NOT NULL,
  PRIMARY KEY(frame_id, concept_id, relation));
CREATE TABLE review(frame_id INT, concept_id TEXT, relation TEXT, verdict TEXT, corrected_concept TEXT,
  corrected_relation TEXT, reviewer TEXT, reviewed_utc TEXT, note TEXT, frame_text_sha TEXT, semantics_sha TEXT);
CREATE INDEX ix_part_frame ON part(frame_id);
CREATE INDEX ix_part_ability ON part(ability_id);
CREATE INDEX ix_ability_card ON ability(oracle_id);
'''


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def load_collection(kb):
    con = sqlite3.connect(f'file:{kb}?mode=ro', uri=True)
    rows = con.execute('SELECT card_name, oracle_id FROM external_oracle WHERE oracle_id IS NOT NULL').fetchall()
    return {oid: name for name, oid in rows}


def card_scope(c, in_coll):
    if in_coll:
        return 'collection'
    if c.get('layout') in EXCLUDED_LAYOUTS:
        return 'excluded:layout:' + c['layout']
    if c.get('set_type') in EXCLUDED_SET_TYPES:
        return 'excluded:set_type:' + c['set_type']
    if 'paper' not in (c.get('games') or []):
        return 'excluded:not_paper'
    return 'corpus'


def faces_of(c):
    if c.get('card_faces') and any('oracle_text' in f for f in c['card_faces']):
        return [(i, f.get('name', c['name']), f.get('type_line', c.get('type_line', '')), f.get('oracle_text', ''))
                for i, f in enumerate(c['card_faces'])]
    return [(0, c['name'], c.get('type_line', ''), c.get('oracle_text', ''))]


def keyword_frame(k, rest):
    if not rest:
        return 'keyword ' + k, []
    fr, b = g.frame(rest)
    return 'keyword ' + k + ' ' + fr, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--oracle', required=True)
    ap.add_argument('--kb', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    coll = load_collection(a.kb)
    if os.path.exists(a.out):
        os.remove(a.out)
    db = sqlite3.connect(a.out)
    db.executescript(SCHEMA)
    frames = {}
    frame_parts = collections.Counter()
    n_cards = 0
    ab_id = 0
    part_rows = []
    for line in gzip.open(a.oracle, 'rt', encoding='utf-8'):
        c = json.loads(line)
        oid = c.get('oracle_id') or (c.get('card_faces') or [{}])[0].get('oracle_id')
        if not oid:
            continue
        in_coll = oid in coll
        scope = card_scope(c, in_coll)
        fs = faces_of(c)
        full = '\n//\n'.join(f[3] for f in fs)
        db.execute('INSERT OR REPLACE INTO card VALUES(?,?,?,?,?,?,?,?,?,?)',
                   (oid, c['name'], c.get('layout'), c.get('set'), c.get('set_type'), c.get('type_line'),
                    int(in_coll), coll.get(oid), scope, sha(full)))
        if scope.startswith('excluded'):
            continue
        n_cards += 1
        if a.limit and n_cards > a.limit:
            break
        for fi, fname, tline, text in fs:
            db.execute('INSERT OR REPLACE INTO face VALUES(?,?,?,?,?)', (oid, fi, fname, tline, text))
            if not text:
                continue
            prepped = g.prep(text, g.self_names(c['name'], fname))
            abilities = g.segment_face(prepped, tline, c.get('keywords'))
            local = {}
            for ordn, ab in enumerate(abilities):
                ab_id += 1
                local[ab['id']] = ab_id
                db.execute('INSERT INTO ability VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                           (ab_id, oid, fi, ab.get('line_index'), ordn, ab.get('kind'), ab.get('ability_word'),
                            ab.get('keyword'), local.get(ab.get('parent')), local.get(ab.get('granted_by')),
                            ab.get('text'), json.dumps(ab.get('reminders') or [])))
                for pi, p in enumerate(ab.get('parts', [])):
                    if p['role'] == 'keyword':
                        ft, binds = keyword_frame(ab['keyword'], ab.get('keyword_param') or '')
                    elif p['role'] in ('structure',):
                        ft, binds = '<structure>', [['structure', p['text']]]
                    else:
                        ft, binds = g.frame(p['text'])
                    if p['role'] == 'trigger_event' and p['text'].startswith('chapter'):
                        ft = 'chapter <n>'
                        binds = [['n', p['text'][len('chapter'):].strip()]]
                    key = (p['role'], ft)
                    if key not in frames:
                        frames[key] = len(frames) + 1
                    attrs = {k: v for k, v in p.items() if k not in ('role', 'text')}
                    part_rows.append((None, ab_id, pi, p['role'], p['text'], frames[key],
                                      json.dumps(binds), json.dumps(attrs) if attrs else None))
    db.executemany('INSERT INTO frame(frame_id, role, frame_text) VALUES(?,?,?)',
                   [(fid, r, f) for (r, f), fid in frames.items()])
    db.executemany('INSERT INTO part VALUES(?,?,?,?,?,?,?,?)', part_rows)
    db.executescript('''
      UPDATE frame SET n_parts=(SELECT count(*) FROM part p WHERE p.frame_id=frame.frame_id);
      CREATE TEMP TABLE fc AS SELECT p.frame_id, a.oracle_id, c.in_collection FROM part p
        JOIN ability a USING(ability_id) JOIN card c USING(oracle_id);
      CREATE TEMP TABLE agg AS SELECT frame_id, count(DISTINCT oracle_id) nc,
        sum(in_collection) ncp, count(DISTINCT CASE WHEN in_collection=1 THEN oracle_id END) ncc FROM fc GROUP BY frame_id;
      UPDATE frame SET n_cards=(SELECT nc FROM agg WHERE agg.frame_id=frame.frame_id),
        n_collection_parts=(SELECT ncp FROM agg WHERE agg.frame_id=frame.frame_id),
        n_collection_cards=(SELECT ncc FROM agg WHERE agg.frame_id=frame.frame_id);
    ''')
    cx.install(db)
    sm.install_frame_semantics(db)
    n_contracts = sm.install_contracts(db)
    manifest = {
        'grammar_version': g.GRAMMAR_VERSION, 'concepts_version': cx.CONCEPTS_VERSION, 'semantics_version': sm.SEMANTICS_VERSION,
        'n_ability_contracts': str(n_contracts),
        'oracle_file': os.path.basename(a.oracle), 'oracle_file_sha256': hashlib.sha256(open(a.oracle, 'rb').read()).hexdigest(),
        'kb_file': os.path.basename(a.kb), 'collection_oracle_ids': str(len(coll)),
        'cards_parsed': str(n_cards), 'built_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'build_seconds': f'{time.time() - t0:.1f}',
    }
    db.executemany('INSERT INTO source_manifest VALUES(?,?)', manifest.items())
    db.commit()
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
