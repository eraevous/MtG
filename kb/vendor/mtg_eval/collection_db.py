"""Read-only reader for a bring-your-own collection database (collection/schema.sql).

Returns the same shape as _adapter.read_xlsx_selected: {tab name: [row dicts with Sheet
column headers and '_row']}, so everything downstream of the adapter reads a collection
database exactly as it reads an export of the canonical Sheet. Copies in Decks and Copies
Free are computed from deck allocations here, never stored. Nothing is ever written.
"""
import json
import sqlite3
from pathlib import Path

MAGIC = b'SQLite format 3\x00'
SCHEMA_VERSIONS = {'1'}
TABS = ('Collection', 'Deck Allocations', 'Mechanics · Units', 'Mechanics · Operations')
PHYSICAL = ('Current deck', 'Companion')


def is_collection_db(path):
    """True when `path` is a SQLite file (by its header, whatever the extension)."""
    try:
        with open(path, 'rb') as f:
            return f.read(16) == MAGIC
    except OSError:
        return False


def _open(path):
    con = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    names = {r[0] for r in con.execute("select name from sqlite_master where type in ('table','view')")}
    if not {'meta', 'collection_rows', 'allocation_rows'} <= names:
        con.close()
        raise ValueError(f'{path} is a SQLite file but not a collection database '
                         '(create one with collection/mtgcollection.py; see docs/BRING_YOUR_OWN_COLLECTION.md)')
    version = dict(con.execute('select key,value from meta')).get('schema_version')
    if version not in SCHEMA_VERSIONS:
        con.close()
        raise ValueError(f'{path}: collection schema version {version!r} is not supported (expected {sorted(SCHEMA_VERSIONS)})')
    return con


def _cell(v):
    if v is None:
        return ''
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def meta(path):
    con = _open(path)
    try:
        return dict(con.execute('select key,value from meta'))
    finally:
        con.close()


def read(path, wanted=None):
    """Collection database -> {tab: rows}, the read_xlsx_selected shape. Missing annotation tabs read as empty."""
    wanted = set(wanted or TABS)
    con = _open(path)
    try:
        out = {}
        holders = {}
        for r in con.execute('select deck, card_name from deck_cards where status in (?,?) and quantity>0 '
                             'group by deck, card_name order by min(id)', PHYSICAL):
            holders.setdefault(r['card_name'], []).append(r['deck'])
        if 'Collection' in wanted:
            rows = []
            for i, r in enumerate(con.execute('select * from collection_rows order by "Card Name"'), start=2):
                rec = {k: v for k, v in json.loads(r['extra_json'] or '{}').items()}
                rec.update({k: _cell(r[k]) for k in r.keys() if k != 'extra_json'})
                owned, assigned = r['Known Qty (min)'], r['Copies in Decks']
                rec['Availability'] = ('Unowned' if owned == 0 else 'Free' if assigned == 0
                                       else 'Allocated' if owned <= assigned else 'Allocated + free')
                rec['Current Deck(s)'] = '; '.join(holders.get(r['Card Name'], []))
                rec['_row'] = i
                rows.append(rec)
            out['Collection'] = rows
        if 'Deck Allocations' in wanted:
            rows = []
            for r in con.execute('select * from allocation_rows order by id'):
                rec = dict(json.loads(r['extra_json'] or '{}'))
                rec.update({k: _cell(r[k]) for k in ('Card Name', 'Deck', 'Status', 'Quantity', 'Section')})
                rec['_row'] = r['id']
                rows.append(rec)
            out['Deck Allocations'] = rows
        for tab in wanted - {'Collection', 'Deck Allocations'}:
            out[tab] = [dict(json.loads(r['row_json']), _row=r['row_number'])
                        for r in con.execute('select row_number,row_json from sheet_rows where tab=? order by row_number', (tab,))]
        return out
    finally:
        con.close()


def identity(path):
    """Provenance for reports: which collection this is, and the Sheet it was imported from, if any."""
    m = meta(path)
    label = m.get('collection_name') or Path(path).stem
    return {'kind': 'collection_db', 'label': label, 'owner': m.get('owner', ''),
            'source_sheet_id': m.get('source_sheet_id', ''), 'schema_version': m.get('schema_version')}
