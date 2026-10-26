#!/usr/bin/env python3
"""Targeted Oracle reconciliation: append-only decisions about specific Sheet-vs-Oracle differences.

Authorities: the working Google Sheet is the inventory authority (what is owned, where it is). The
matched Scryfall Oracle record from a versioned refresh run is the rules-text authority. Neither
overwrites the other: this file never edits the Sheet or `cards`; it records, per card, what the
difference is, whether it is material, what the evaluator should read, whether the card's contracts
are quarantined, and the Sheet correction a human may choose to make.

  python reconcile.py --db mtg_cards_v0.2.sqlite add --card "Medic's Kitesail" --category sheet_error ...
  python reconcile.py show | verify
  python reconcile.py corrections --db mtg_cards_v0.2.sqlite --out reports/proposed_sheet_corrections.csv
"""
import argparse, csv, datetime, json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chain

FIELDS = ['card_name', 'oracle_run_id', 'oracle_id', 'category', 'material', 'fields', 'sheet_value', 'oracle_value', 'decision',
          'evaluator_reads', 'quarantine_contracts', 'identity_confirmed', 'proposed_sheet_correction', 'reviewer', 'source',
          'recorded_by', 'recorded_utc', 'notes', 'supersedes']
CATEGORIES = {'sheet_error', 'name_alias', 'non_game', 'token_not_card', 'identity_mismatch'}
DEFAULT = HERE / 'overrides' / 'oracle_reconciliation.jsonl'


def read(path=DEFAULT): return chain.read(path, FIELDS, 'reconciliation_id')


def effective(path=DEFAULT):
    """Latest record per card (a later record supersedes an earlier one)."""
    out = {}
    for r in read(path): out[r['card_name']] = r
    return out


def check(body):
    if body['category'] not in CATEGORIES: raise ValueError(f"category must be one of {sorted(CATEGORIES)}")
    if body['evaluator_reads'] not in ('oracle', 'sheet', 'excluded'): raise ValueError('evaluator_reads: oracle | sheet | excluded')
    for k in ('card_name', 'oracle_run_id', 'decision', 'reviewer', 'source'):
        if not body.get(k): raise ValueError(f'{k} is required')


def add(path, body):
    check(body)
    return chain.append(path, FIELDS, 'reconciliation_id', body)


def replay(con, path=DEFAULT):
    n = 0
    for seq, r in enumerate(read(path), 1):
        con.execute('insert into oracle_reconciliation values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (seq, r['reconciliation_id'], r['card_name'], r['oracle_run_id'], r.get('oracle_id'), r['category'], int(bool(r['material'])),
                     json.dumps(r.get('fields') or []), r.get('sheet_value'), r.get('oracle_value'), r['decision'], r['evaluator_reads'],
                     int(bool(r.get('quarantine_contracts'))), None if r.get('identity_confirmed') is None else int(bool(r['identity_confirmed'])),
                     r.get('proposed_sheet_correction'), r['reviewer'], r['source'], r['recorded_utc']))
        n += 1
    return n


def corrections(con, out):
    rows = con.execute("select card_name,category,fields_json,sheet_value,oracle_value,proposed_sheet_correction,reconciliation_id "
                       "from effective_reconciliation where proposed_sheet_correction is not null order by card_name").fetchall()
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['card_name', 'category', 'fields', 'sheet_value', 'oracle_value', 'proposed_sheet_correction', 'reconciliation_id', 'applied'])
        for r in rows: w.writerow(list(r) + ['no (proposal only; the Sheet is edited by a human)'])
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--file', default=str(DEFAULT)); ap.add_argument('--db', default=str(HERE / 'mtg_cards_v0.2.sqlite'))
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add')
    for k in ('card', 'category', 'decision', 'evaluator-reads', 'reviewer', 'source', 'oracle-run-id'): a.add_argument('--' + k, required=True)
    for k in ('sheet-value', 'oracle-value', 'correction', 'notes', 'supersedes', 'oracle-id'): a.add_argument('--' + k)
    a.add_argument('--field', action='append', default=[]); a.add_argument('--material', action='store_true')
    a.add_argument('--quarantine', action='store_true'); a.add_argument('--identity-confirmed', choices=['yes', 'no'])
    sub.add_parser('show'); sub.add_parser('verify')
    c = sub.add_parser('corrections'); c.add_argument('--out', default='reports/proposed_sheet_corrections.csv')
    x = ap.parse_args()
    if x.cmd == 'add':
        body = {'card_name': x.card, 'oracle_run_id': x.oracle_run_id, 'oracle_id': x.oracle_id, 'category': x.category, 'material': x.material,
                'fields': x.field, 'sheet_value': x.sheet_value, 'oracle_value': x.oracle_value, 'decision': x.decision,
                'evaluator_reads': x.evaluator_reads, 'quarantine_contracts': x.quarantine,
                'identity_confirmed': None if x.identity_confirmed is None else x.identity_confirmed == 'yes',
                'proposed_sheet_correction': x.correction, 'reviewer': x.reviewer, 'source': x.source, 'recorded_by': 'reconcile.py',
                'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'notes': x.notes, 'supersedes': x.supersedes}
        print(json.dumps(add(x.file, body), indent=1, ensure_ascii=False))
    elif x.cmd == 'show':
        print(json.dumps(read(x.file), indent=1, ensure_ascii=False))
    elif x.cmd == 'verify':
        print(json.dumps({'lines': len(read(x.file)), 'chain': 'ok'}))
    else:
        con = sqlite3.connect(Path(x.db).resolve().as_uri() + '?mode=ro', uri=True)
        print(corrections(con, x.out), 'proposed corrections written to', x.out)


if __name__ == '__main__':
    main()
