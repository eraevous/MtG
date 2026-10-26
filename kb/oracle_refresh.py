#!/usr/bin/env python3
"""Explicit, versioned Oracle refresh: compare stored inventory text with an external Oracle source.

Runs on demand, never inside a user query. It does not change `cards` (the working Sheet is the
source of recorded text) and does not touch reviews. It writes one immutable snapshot file per run;
every DB build replays all snapshots, so identity (oracle_id, faces) and discrepancies survive
rebuilds. Discrepancies open QA items; a reviewer decides whether the Sheet needs a correction.

  # Scryfall bulk "Oracle Cards" file (https://scryfall.com/docs/api/bulk-data), downloaded separately:
  python oracle_refresh.py snapshot --db mtg_cards_v0.2.sqlite --scryfall oracle-cards-20261020.json --out refresh/
  python migrate_v02.py ... --refresh-dir refresh/      # replays every snapshot into the DB
"""
import argparse, datetime, hashlib, json, sqlite3, unicodedata, re
from pathlib import Path

TOOL = 'oracle_refresh-0.2.1'
NOT_A_CARD = ('art_series', 'token', 'double_faced_token', 'emblem')
NON_GAME = ('front_card', 'planar', 'scheme', 'vanguard')   # matched only when nothing playable has the name


def fold(s):
    """Diacritic/punctuation-blind key, for Sheet spellings like 'Dunedain Blade' or 'Gideon the Oathsworn'."""
    return re.sub(r'[^a-z0-9/]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().casefold())


def rank(c):
    """Lower is preferred when several Oracle objects share a name (e.g. a 'funny' playtest card, a Jumpstart front card)."""
    return (c.get('layout') in NON_GAME, (c.get('legalities') or {}).get('commander') == 'not_legal',
            c.get('set_type') in ('funny', 'memorabilia'))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').replace('−', '-').replace('—', '-').replace('–', '-').replace('’', "'")
    return re.sub(r'\s+', ' ', s).strip()


def external_text(card):
    if card.get('oracle_text') is not None and not card.get('card_faces'): return card['oracle_text']
    faces = card.get('card_faces') or []
    if card.get('oracle_text') is not None and card.get('layout') not in ('transform', 'modal_dfc', 'split', 'adventure', 'flip', 'reversible_card'):
        return card['oracle_text']
    return '\n//\n'.join(f.get('oracle_text', '') for f in faces)


def snapshot(db, source, outdir, source_updated_at=None):
    raw = Path(source).read_bytes()
    data = json.loads(raw)
    by_name, by_fold = {}, {}
    for c in sorted((c for c in data if c.get('layout') not in NOT_A_CARD), key=rank):   # stable: file order within a rank
        for key in [c['name']] + ([c['name'].split(' // ')[0]] if ' // ' in c['name'] else []):
            by_name.setdefault(key.casefold(), c); by_fold.setdefault(fold(key), c)
    con = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    src_sha = hashlib.sha256(raw).hexdigest()
    run_id = hashlib.sha256(f'{TOOL}|{src_sha}|{started}'.encode()).hexdigest()[:16]
    rows = []
    for name, stored, osha, legal in con.execute('select card_name,oracle_text,oracle_text_sha256,commander_legal_stored from cards order by card_name'):
        c = by_name.get(name.casefold()) or by_name.get(name.split(' // ')[0].casefold())
        method = 'exact_name'
        if not c:
            c = by_fold.get(fold(name)) or by_fold.get(fold(name.split(' // ')[0])); method = 'folded_name'
        if not c:
            rows.append({'card_name': name, 'match_status': 'not_found'}); continue
        ext = external_text(c)
        st = 'identical' if ext == (stored or '') else 'normalized_equal' if norm(ext) == norm(stored) else 'differs'
        rows.append({'card_name': name, 'match_status': st, 'match_method': method, 'external_name': c['name'],
                     'oracle_id': c.get('oracle_id'), 'layout': c.get('layout'),
                     'external_text': ext, 'external_text_sha256': hashlib.sha256(ext.encode()).hexdigest(),
                     'stored_text_sha256': osha, 'legal_commander': (c.get('legalities') or {}).get('commander'),
                     'faces': [{'face_index': i, 'name': f.get('name'), 'mana_cost': f.get('mana_cost'), 'type_line': f.get('type_line'),
                                'oracle_text': f.get('oracle_text')} for i, f in enumerate(c.get('card_faces') or [])] or
                              [{'face_index': 0, 'name': c.get('name'), 'mana_cost': c.get('mana_cost'), 'type_line': c.get('type_line'), 'oracle_text': ext}]})
    head = {'run_id': run_id, 'source_kind': 'scryfall_bulk', 'source_name': Path(source).name, 'source_sha256': src_sha,
            'source_updated_at': source_updated_at, 'started_utc': started, 'tool_version': TOOL,
            'cards_matched': sum(r['match_status'] != 'not_found' for r in rows), 'cards_unmatched': sum(r['match_status'] == 'not_found' for r in rows),
            'discrepancies': sum(r['match_status'] == 'differs' for r in rows),
            'folded_name_matches': sum(r.get('match_method') == 'folded_name' for r in rows)}
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    p = out / f'oracle_refresh_{started[:10]}_{run_id}.jsonl'
    with open(p, 'x', encoding='utf-8') as f:  # 'x': a snapshot is never overwritten
        f.write(json.dumps({'run': head}, ensure_ascii=False) + '\n')
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    return p, head


def replay(con, refresh_dir):
    """Load every snapshot (oldest first). Opens QA items; never edits cards or reviews."""
    n = 0
    for p in sorted(Path(refresh_dir).glob('oracle_refresh_*.jsonl')) if refresh_dir and Path(refresh_dir).exists() else []:
        lines = p.read_text(encoding='utf-8').splitlines()
        head = json.loads(lines[0])['run']
        con.execute('insert into oracle_refresh_runs values(?,?,?,?,?,?,?,?,?,?,?)', (head['run_id'], head['source_kind'], head['source_name'],
                    head['source_sha256'], head.get('source_updated_at'), head['started_utc'], head['tool_version'], head['cards_matched'],
                    head['cards_unmatched'], head['discrepancies'], p.name))
        cur = {a: b for a, b in con.execute('select card_name,oracle_text_sha256 from cards')}
        for line in lines[1:]:
            r = json.loads(line)
            if r['card_name'] not in cur: continue
            con.execute('insert into external_oracle values(?,?,?,?,?,?,?,?,?)', (head['run_id'], r['card_name'], r.get('oracle_id'), r.get('layout'),
                        r.get('external_text'), r.get('external_text_sha256'), json.dumps(r.get('faces')) if r.get('faces') else None,
                        r.get('legal_commander'), r['match_status']))
            for f in r.get('faces') or []:
                con.execute('insert or replace into card_faces values(?,?,?,?,?,?,?,?)', (r['card_name'], f['face_index'], f['name'] or '', f.get('mana_cost'),
                            f.get('type_line'), f.get('oracle_text'), 'scryfall', head['run_id']))
            if r.get('oracle_id'):
                con.execute("update card_identity set oracle_id=?, layout=?, identity_source='scryfall refresh', refresh_run_id=? where card_name=?",
                            (r['oracle_id'], r.get('layout'), head['run_id'], r['card_name']))
            issues = []
            if r['match_status'] == 'differs': issues.append('oracle_text_discrepancy')
            elif r['match_status'] == 'not_found': issues.append('oracle_card_not_found')
            if r.get('match_method') == 'folded_name': issues.append('oracle_name_spelling')
            for issue in issues:
                reviewed = con.execute("select count(*) from review_overlay where card_name=? and decision='verified'", (r['card_name'],)).fetchone()[0]
                if r.get('stored_text_sha256') not in (None, cur[r['card_name']]): issue += '_stale_snapshot'
                con.execute('insert or ignore into qa_queue values(?,?,?,?,?,?,?,?)',
                            (hashlib.sha256(f"{head['run_id']}|{issue}|{r['card_name']}".encode()).hexdigest()[:16], issue, r['card_name'],
                             'high' if reviewed else 'medium', TOOL, head['started_utc'],
                             json.dumps({'run_id': head['run_id'], 'stored_sha256': cur[r['card_name']], 'external_sha256': r.get('external_text_sha256'),
                                         'external_text': r.get('external_text'), 'external_name': r.get('external_name'),
                                         'has_verified_review': bool(reviewed)}), 'open'))
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest='cmd', required=True)
    x = s.add_parser('snapshot'); x.add_argument('--db', required=True); x.add_argument('--scryfall', required=True)
    x.add_argument('--out', default='refresh'); x.add_argument('--source-updated-at')
    a = ap.parse_args()
    p, head = snapshot(a.db, a.scryfall, a.out, a.source_updated_at)
    print(json.dumps(dict(head, file=str(p)), indent=2))


if __name__ == '__main__':
    main()
