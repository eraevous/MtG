#!/usr/bin/env python3
"""Build an as-of collection database: a copy of a KB release whose ownership is replaced by a dated inventory fixture.

Why: a replay of a historical question must see the collection as it was on that date, not today's. The card meaning
(Oracle text, contracts, reviews) stays the KB release's; only who owns what changes. The release KB is never touched:
this writes a new, derived database (rebuildable from the fixture and the release, so it is not a hand edit).

What changes in the copy:
  * cards owned on the date keep their KB row, with owned_min/assigned/free recomputed from the fixture;
  * cards not owned on the date are removed from every card-keyed table (so no verb, search or SQL lookup can see them);
  * deck_allocations is replaced by the fixture's deck lists (or by the inventory's deck column when no deck files are given);
  * inventory-derived tags (cards.roles_stored, capability_claims from Collection.Roles) are dropped, because they were
    written into a later inventory; text-derived claims stay;
  * tables with no card_name column that hold later state are emptied: source_sheet_rows (every sheet of the release's
    source workbook) and reference_documents (doctrine copies dated later than most as-of dates); meta's pointers to the
    live canonical sheet are redacted;
  * SOURCE_MANIFEST.json beside it names the fixture, its sha256 and the as-of date, and lists fixture names the KB lacks;
  * collection_policy.json beside it is the dated policy if one is given, and otherwise records that none is known
    (mtgtools then reports the policy as unknown instead of reading today's decks/collection_policy.json).

Usage:
  python3 tools/asof_kb.py --as-of 2026-10-06 --inventory inv.csv [--deck decks/a.csv ...] [--policy p.json] --out DIR

Inventory CSV: one row per name (or per name and deck); columns name|card_name|card, qty|quantity|count, optional
deck|allocation, optional status. Deck CSV: name|card_name|card, qty|quantity|count, optional deck (else the file stem),
section, status. A status containing planned, proposed, wishlist or hypothetical makes the row planned_only.
"""
import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'
NAME_COLS = ('name', 'card_name', 'card', 'card name')
QTY_COLS = ('qty', 'quantity', 'count', 'copies')
DECK_COLS = ('deck', 'allocation', 'deck_name')
PLANNED = ('planned', 'proposed', 'wishlist', 'hypothetical', 'not_built', 'not built')
BASICS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'}
LATER_STATE_TABLES = ('source_sheet_rows', 'reference_documents')
LIVE_META_KEYS = ('canonical_sheet_id', 'canonical_url')


def _col(header, options):
    low = {h.strip().lower(): h for h in header}
    for o in options:
        if o in low:
            return low[o]
    return None


def _rows(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        name, qty = _col(r.fieldnames or [], NAME_COLS), _col(r.fieldnames or [], QTY_COLS)
        if not name:
            raise SystemExit(f'{path}: no name column (one of {NAME_COLS})')
        deck, section, status = _col(r.fieldnames, DECK_COLS), _col(r.fieldnames, ('section',)), _col(r.fieldnames, ('status',))
        for row in r:
            n = (row.get(name) or '').strip()
            if not n:
                continue
            try:
                q = int(float(row.get(qty) or 1)) if qty else 1
            except ValueError:
                q = 1
            yield {'name': n, 'qty': q, 'deck': (row.get(deck) or '').strip() if deck else '',
                   'section': (row.get(section) or '').strip() if section else '',
                   'status': (row.get(status) or '').strip() if status else ''}


def _resolver(c):
    """Map a fixture name to a KB card_name: exact, case-insensitive, or the front face of a 'A // B' card."""
    exact, low = {}, {}
    for (n,) in c.execute('select card_name from cards'):
        exact[n] = n
        low.setdefault(n.lower(), n)
        if ' // ' in n:
            low.setdefault(n.split(' // ')[0].lower(), n)
    return lambda n: exact.get(n) or low.get(n.lower()) or low.get(n.split(' // ')[0].lower())


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(as_of, inventory, decks=(), policy=None, out=None, base=DEFAULT_BASE):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    db = out / Path(base).name
    shutil.copyfile(base, db)
    c = sqlite3.connect(db)
    resolve = _resolver(c)

    owned, missing, inv_alloc = defaultdict(int), defaultdict(int), []
    for r in _rows(inventory):
        k = resolve(r['name'])
        if k is None:
            missing[r['name']] += r['qty']
            continue
        owned[k] += r['qty']
        if r['deck']:
            inv_alloc.append(dict(r, name=k))
    alloc, deck_missing = [], defaultdict(int)
    for d in decks:
        for r in _rows(d):
            k = resolve(r['name'])
            if k is None:
                deck_missing[r['name']] += r['qty']
                continue
            alloc.append(dict(r, name=k, deck=r['deck'] or Path(d).stem))
    if not decks:
        alloc = inv_alloc
    for a in alloc:   # a basic land in a deck list is owned even when the inventory does not count basics
        if a['name'] in BASICS and owned[a['name']] < a['qty']:
            owned[a['name']] = max(owned[a['name']], a['qty'])

    keep = set(owned)
    # the copy is a derived fixture, so the release's append-only guards (triggers) do not apply to it; the release is untouched
    triggers = [n for (n,) in c.execute("select name from sqlite_master where type='trigger'")]
    for t in triggers:
        c.execute(f'drop trigger "{t}"')
    c.execute('create temp table keep(card_name text primary key)')
    c.executemany('insert into keep values (?)', [(k,) for k in keep])
    tables = [n for (n,) in c.execute("select name from sqlite_master where type='table' and name not like 'card_fts%' "
                                       "and name not like 'sqlite_%'")]
    pruned = {}
    for t in tables:
        if 'card_name' in [r[1] for r in c.execute(f'pragma table_info("{t}")')]:
            pruned[t] = c.execute(f'delete from "{t}" where card_name not in (select card_name from keep)').rowcount

    # contract-keyed tables (compile_losses, validation_checks, ...) have no card_name: keep only rows of surviving contracts
    if 'operation_contracts' in tables:
        for t in tables:
            cols = [r[1] for r in c.execute(f'pragma table_info("{t}")')]
            if 'contract_id' in cols and 'card_name' not in cols:
                pruned[t] = c.execute(f'delete from "{t}" where contract_id not in '
                                      '(select contract_id from operation_contracts)').rowcount

    c.execute('delete from deck_allocations')
    assigned = defaultdict(int)
    for i, a in enumerate(alloc, 1):
        planned = any(p in a['status'].lower() for p in PLANNED)
        if not planned:
            assigned[a['name']] += a['qty']
        c.execute('insert into deck_allocations(row_id,card_name,deck,status_raw,status_group,quantity,section,physically_assigned,'
                  'counts_in_deck_100,raw_json) values (?,?,?,?,?,?,?,?,?,?)',
                  (i, a['name'], a['deck'], a['status'] or 'Allocated', 'planned' if planned else 'allocated', a['qty'],
                   a['section'] or None, 0 if planned else 1, 0 if a['section'].lower() in ('maybe', 'sideboard', 'considering') else 1,
                   json.dumps({'source': 'asof_fixture', **a})))
    over = {}
    for k in keep:
        o, s = owned[k], assigned[k]
        if s > o:
            over[k] = {'owned': o, 'assigned': s}
        c.execute('update cards set owned_min=?, assigned=?, free=?, roles_stored=NULL, availability_stored=NULL where card_name=?',
                  (o, s, o - s, k))
    dropped_tags = c.execute("delete from capability_claims where source='Collection.Roles'").rowcount
    # tables without a card_name column escape the prune above but still carry the later collection: the raw rows of every
    # sheet of the release's source workbook (Collection, Deck Allocations, Plans, Photo Intake ...) and the doctrine copies
    # stored in the DB (dated later than most as-of dates). meta also points at the live canonical sheet. Clear them all.
    later_state = {}
    for t in LATER_STATE_TABLES:
        if t in tables:
            later_state[t] = c.execute(f'delete from "{t}"').rowcount
    if 'meta' in tables:
        later_state['meta_redacted'] = c.execute(
            f"update meta set value='redacted:asof-{as_of}' where key in ({','.join('?' * len(LIVE_META_KEYS))})",
            LIVE_META_KEYS).rowcount
    c.execute("insert into card_fts(card_fts) values('rebuild')")
    c.commit()
    c.execute('vacuum')
    c.close()

    base_man = json.loads((Path(base).parent / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    man = {'release': f"{base_man.get('release')}+asof-{as_of}", 'schema_version': base_man.get('schema_version'),
           'built_utc': base_man.get('built_utc'),
           'as_of': {'date': as_of, 'base_release': base_man.get('release'), 'base_sha256': _sha(base),
                     'note': 'Card meaning is the base release; ownership, deck lists and policy are the dated fixture. '
                             'Cards not owned on the date are absent. Inventory role tags were dropped (they came from a later '
                             'inventory).'},
           'inventory_source': {'input_name': Path(inventory).name, 'input_sha256': _sha(inventory),
                                'deck_files': {Path(d).name: _sha(d) for d in decks},
                                'drive_modified_utc': None, 'note': f'as-of fixture for {as_of}'},
           'counts': {'owned_names': len(keep), 'copies': sum(owned.values()), 'deck_rows': len(alloc),
                      'decks': sorted({a['deck'] for a in alloc}), 'rows_pruned': pruned, 'inventory_tags_dropped': dropped_tags,
                      'later_state_cleared': later_state,
                      'append_only_triggers_dropped_in_copy': len(triggers)},
           'gaps': {'fixture_names_not_in_kb': dict(sorted(missing.items())), 'deck_names_not_in_kb': dict(sorted(deck_missing.items())),
                    'assigned_exceeds_owned': over}}
    (out / 'SOURCE_MANIFEST.json').write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding='utf-8')
    pol = json.loads(Path(policy).read_text(encoding='utf-8')) if policy else {'not_recorded': True, 'as_of': as_of}
    (out / 'collection_policy.json').write_text(json.dumps(pol, indent=1), encoding='utf-8')
    return man


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--as-of', required=True)
    p.add_argument('--inventory', required=True)
    p.add_argument('--deck', action='append', default=[])
    p.add_argument('--policy')
    p.add_argument('--base', default=str(DEFAULT_BASE))
    p.add_argument('--out', required=True)
    a = p.parse_args(argv)
    m = build(a.as_of, a.inventory, a.deck, a.policy, a.out, a.base)
    g = m['gaps']
    print(json.dumps({'release': m['release'], 'counts': {k: v for k, v in m['counts'].items() if k != 'rows_pruned'},
                      'fixture_names_not_in_kb': len(g['fixture_names_not_in_kb']),
                      'deck_names_not_in_kb': len(g['deck_names_not_in_kb']),
                      'assigned_exceeds_owned': len(g['assigned_exceeds_owned'])}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
