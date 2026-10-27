#!/usr/bin/env python3
"""Build and maintain a bring-your-own collection database for the MtG tools.

The database (schema.sql) holds what you own and which cards sit in which deck. The evaluator
and the KB build read it wherever they accept a Sheet export: pass the .sqlite path instead of
the .xlsx. Standard library only.

  python3 collection/mtgcollection.py init my_collection.sqlite --name "Sam's cards" --owner Sam
  python3 collection/mtgcollection.py import-csv my_collection.sqlite moxfield_export.csv
  python3 collection/mtgcollection.py import-deck my_collection.sqlite atraxa.txt --deck Atraxa
  python3 collection/mtgcollection.py import-xlsx my_collection.sqlite my_sheet.xlsx --tab Cards
  python3 collection/mtgcollection.py enrich my_collection.sqlite --online       # or --scryfall oracle-cards.json
  python3 collection/mtgcollection.py check my_collection.sqlite

Card data (Oracle text, type line, legality, color identity) is a cached copy of Scryfall's
Oracle data or of your own Sheet's columns. Oracle text stays the rules authority. The derived
index columns `ETB Tapped` and `Can Be Commander` are hints computed here with patterns over
Oracle text, the same kind of hint the canonical Sheet carries; nothing downstream treats them
as verified mechanics.

@ai-semantic-role: candidate-source
"""
import argparse
import csv
import datetime
import gzip
import hashlib
import io
import json
import re
import sqlite3
import sys
import time
import unicodedata
import urllib.request
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'kb' / 'vendor'))
from mtg_eval import _adapter, collection_db  # noqa: E402

SCHEMA_VERSION = '1'
SCRYFALL_COLLECTION = 'https://api.scryfall.com/cards/collection'
SCRYFALL_BULK = 'https://api.scryfall.com/bulk-data/oracle-cards'
USER_AGENT = 'eraevous-MtG-collection/1 (+https://github.com/eraevous/MtG)'
NOT_A_CARD = ('art_series', 'token', 'double_faced_token', 'emblem')
NON_GAME = ('planar', 'scheme', 'vanguard')

# Sheet column -> cards column. These are the Collection headers the adapter reads.
CARD_COLUMNS = {
    'Oracle Text': 'oracle_text', 'Type Line': 'type_line', 'Mana Cost': 'mana_cost', 'Mana Value': 'mana_value',
    'Color Identity': 'color_identity', 'Keywords': 'keywords', 'Produces': 'produces', 'Power': 'power',
    'Toughness': 'toughness', 'Rarity': 'rarity', 'Commander Legal': 'commander_legal',
    'Can Be Commander': 'can_be_commander', 'ETB Tapped': 'etb_tapped', 'Scryfall URL': 'scryfall_url', 'Roles': 'roles',
}
# Computed by the reader from holdings and allocations, so never stored from an import.
DERIVED = {'Known Qty (min)', 'Copies in Decks', 'Copies Free', 'Availability', 'Current Deck(s)', 'Ownership', '_row'}

# Header aliases used by common collection exports (Moxfield, Archidekt, ManaBox, Deckbox, Deckstats,
# TCGplayer) and by hand-made sheets. Matching ignores case, spaces, underscores and punctuation.
ALIASES = {
    'name': ['Card Name', 'Name', 'Card', 'Card Title'],
    'quantity': ['Quantity', 'Count', 'Qty', 'Amount', 'Copies', 'Owned', 'Have', 'Known Qty (min)'],
    'set_code': ['Set Code', 'Set', 'Edition Code', 'Edition', 'Expansion Code'],
    'collector_number': ['Collector Number', 'Card Number', 'Number', 'CN', 'Collector #'],
    'finish': ['Finish', 'Foil', 'Printing'],
    'language': ['Language', 'Lang'],
    'condition': ['Condition'],
    'notes': ['Notes', 'Note', 'Comment'],
}
HOLDING_HEADERS = {h for v in ALIASES.values() for h in v}


def key(s):
    return re.sub(r'[^a-z0-9#]', '', str(s).casefold())


def fold(s):
    """Diacritic- and punctuation-blind name key (matches kb/oracle_refresh.py)."""
    return re.sub(r'[^a-z0-9/]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().casefold())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------- database
def connect(db, create=False):
    db = Path(db)
    if not create and not db.exists():
        raise SystemExit(f'{db} does not exist. Create it with: mtgcollection.py init {db}')
    if db.exists() and not collection_db.is_collection_db(db) and db.stat().st_size:
        raise SystemExit(f'{db} exists and is not a SQLite file')
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    con.executescript((HERE / 'schema.sql').read_text(encoding='utf-8'))
    version = con.execute("select value from meta where key='schema_version'").fetchone()
    if version is None:
        con.executemany('insert into meta values(?,?)', [('schema_version', SCHEMA_VERSION), ('created_utc', now())])
    elif version[0] != SCHEMA_VERSION:
        raise SystemExit(f'{db}: schema version {version[0]} is not {SCHEMA_VERSION}')
    con.commit()
    return con


def set_meta(con, **kv):
    con.executemany('insert or replace into meta values(?,?)', [(k, str(v)) for k, v in kv.items() if v is not None])


def log_import(con, kind, source, file_name=None, digest=None, rows=None, notes=None):
    con.execute('insert into imports(utc,kind,source,file_name,sha256,rows,notes) values(?,?,?,?,?,?,?)',
                (now(), kind, source, file_name, digest, rows, notes))
    set_meta(con, updated_utc=now())


def ensure_card(con, name):
    con.execute('insert or ignore into cards(card_name) values(?)', (name,))


def parse_qty(raw, default=1):
    s = str(raw if raw is not None else '').strip()
    if s == '':
        return default
    v = float(s)
    if v < 0 or not v.is_integer():
        raise ValueError(f'quantity must be a whole number >= 0, got {raw!r}')
    return int(v)


def finish_of(raw):
    s = str(raw or '').strip().lower()
    if s in ('', 'no', 'false', '0', 'normal', 'nonfoil', 'non-foil', 'regular'):
        return None
    if s in ('yes', 'true', '1', 'foil'):
        return 'foil'
    return s


def card_fields(row):
    """Sheet-style card columns present in an import row -> {cards column: value}."""
    out = {}
    for header, col in CARD_COLUMNS.items():
        v = row.get(header)
        if v is not None and str(v).strip() != '':
            out[col] = str(v)
    if 'mana_value' in out:
        try:
            out['mana_value'] = float(out['mana_value'])
        except ValueError:
            del out['mana_value']
    return out


def update_card(con, name, fields, extra=None, source=None):
    ensure_card(con, name)
    if fields:
        cols = ', '.join(f'{c}=?' for c in fields)
        con.execute(f'update cards set {cols} where card_name=?', (*fields.values(), name))
        if 'oracle_text' in fields and source:
            con.execute('update cards set card_data_source=? where card_name=?', (source, name))
    if extra:
        cur = json.loads(con.execute('select extra_json from cards where card_name=?', (name,)).fetchone()[0])
        cur.update(extra)
        con.execute('update cards set extra_json=? where card_name=?', (json.dumps(cur, ensure_ascii=False, sort_keys=True), name))


# ------------------------------------------------------------------------------- imports
def resolve_headers(headers):
    by_key = {key(h): h for h in headers}
    found = {}
    for field, names in ALIASES.items():
        for n in names:
            if key(n) in by_key:
                found[field] = by_key[key(n)]
                break
    return found


def import_rows(con, rows, source, kind, file_name=None, digest=None):
    """Collection rows (dicts keyed by header) -> holdings for `source`, replacing that source's earlier rows."""
    rows = list(rows)
    if not rows:
        raise SystemExit('no rows to import')
    cols = resolve_headers(rows[0].keys())
    if 'name' not in cols:
        raise SystemExit(f'no card name column found; expected one of {ALIASES["name"]}. Headers: {list(rows[0])}')
    con.execute('delete from holdings where source=?', (source,))
    n = copies = 0
    for i, r in enumerate(rows, start=2):
        name = str(r.get(cols['name']) or '').strip()
        if not name:
            continue
        get = lambda f: str(r.get(cols[f]) or '').strip() or None if f in cols else None
        try:
            # a blank quantity cell means none owned; a list with no quantity column means one of each
            q = parse_qty(r.get(cols['quantity']), 0) if 'quantity' in cols else 1
        except ValueError as e:
            raise SystemExit(f'{file_name or source} row {i} ({name}): {e}')
        extra = {k: v for k, v in r.items()
                 if k and k not in CARD_COLUMNS and k not in DERIVED and k not in cols.values()
                 and k not in HOLDING_HEADERS and str(v).strip() != ''}
        update_card(con, name, card_fields(r), extra, f'import:{source}')
        con.execute('insert into holdings(card_name,quantity,source,set_code,collector_number,finish,language,condition,notes) '
                    'values(?,?,?,?,?,?,?,?,?)',
                    (name, q, source, get('set_code'), get('collector_number'), finish_of(get('finish')),
                     get('language'), get('condition'), get('notes')))
        n += 1
        copies += q
    log_import(con, kind, source, file_name, digest, n)
    con.commit()
    return {'source': source, 'rows': n, 'copies': copies}


def import_csv(con, path, source=None):
    path = Path(path)
    text = path.read_text(encoding='utf-8-sig')
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    return import_rows(con, rows, source or path.stem, 'csv', path.name, sha256(path))


@contextmanager
def header_rows(extra):
    """Let the adapter's OOXML reader read tabs it does not know, at the given header row."""
    saved = dict(_adapter.HEADER_ROWS)
    _adapter.HEADER_ROWS.update(extra)
    try:
        yield
    finally:
        _adapter.HEADER_ROWS.clear()
        _adapter.HEADER_ROWS.update(saved)


def sheet_tabs(path):
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET
    with ZipFile(path) as z:
        wb = ET.fromstring(z.read('xl/workbook.xml'))
    return [s.get('name') for s in wb.findall(f'.//{{{_adapter.NS}}}sheet')]


def import_xlsx(con, path, source=None, tab=None, header_row=None, sheet_id=None):
    """Import an .xlsx export (e.g. Google Sheets: File > Download > Microsoft Excel).

    With no --tab and a workbook in the canonical layout (Collection + Deck Allocations tabs,
    header on row 4), the whole inventory is imported: holdings, every deck allocation, and the
    Mechanics tabs as pass-through candidate annotations. Otherwise one tab is read as a plain
    collection list, like a CSV."""
    path = Path(path)
    digest = sha256(path)
    tabs = sheet_tabs(path)
    if tab is None and {'Collection', 'Deck Allocations'} <= set(tabs):
        wanted = {t for t in _adapter.HEADER_ROWS if t in tabs}
        raw = _adapter.read_xlsx_selected(str(path), wanted)
        data = _adapter.normalize({t: raw.get(t, []) for t in _adapter.HEADER_ROWS})
        source = source or 'sheet'
        result = import_rows(con, [{k: v for k, v in r.items() if k != '_row'} for r in raw['Collection']],
                             source, 'xlsx', path.name, digest)
        result['decks'] = replace_allocations(con, raw['Deck Allocations'])
        con.execute("delete from sheet_rows where tab like 'Mechanics%'")
        for t in wanted - {'Collection', 'Deck Allocations'}:
            con.executemany('insert into sheet_rows values(?,?,?)',
                            [(t, r['_row'], json.dumps({k: v for k, v in r.items() if k != '_row'}, ensure_ascii=False)) for r in raw[t]])
        set_meta(con, source_sheet_id=sheet_id, source_sheet_export=path.name)
        con.commit()
        result['sheet_issues'] = {k: v for k, v in data['health']['known_problems'].items()}
        return result
    tab = tab or tabs[0]
    if tab not in tabs:
        raise SystemExit(f'no tab {tab!r} in {path.name}; tabs: {tabs}')
    with header_rows({tab: header_row or 1}):
        raw = _adapter.read_xlsx_selected(str(path), {tab})
    rows = [{k: v for k, v in r.items() if k != '_row'} for r in raw[tab]]
    result = import_rows(con, rows, source or f'{path.stem}:{tab}', 'xlsx', path.name, digest)
    set_meta(con, source_sheet_id=sheet_id)
    con.commit()
    return result


def replace_allocations(con, rows):
    con.execute('delete from deck_cards')
    decks = set()
    for r in rows:
        name, deck = str(r.get('Card Name', '')).strip(), str(r.get('Deck', '')).strip()
        if not name or not deck:
            continue
        ensure_card(con, name)
        extra = {k: v for k, v in r.items() if k not in ('Card Name', 'Deck', 'Status', 'Quantity', 'Section', '_row') and str(v).strip()}
        con.execute('insert into deck_cards(deck,card_name,quantity,section,status,extra_json) values(?,?,?,?,?,?)',
                    (deck, name, parse_qty(r.get('Quantity'), 0), str(r.get('Section', '')).strip(),
                     str(r.get('Status', '')).strip(), json.dumps(extra, ensure_ascii=False, sort_keys=True)))
        decks.add(deck)
    return len(decks)


SECTION_HEADERS = {
    'commander': 'Commander', 'commanders': 'Commander', 'companion': 'Companion',
    'deck': '', 'main': '', 'mainboard': '', 'main deck': '', 'maindeck': '',
    'sideboard': None, 'maybeboard': None, 'considering': None, 'tokens': None,
}
DECK_LINE = re.compile(r'^(?P<qty>\d+)\s*x?\s+(?P<name>.+?)'
                       r'(?:\s+\((?P<set>[A-Za-z0-9]{2,6})\)(?:\s+(?P<cn>[^\s*\[]+))?)?'
                       r'(?P<tail>(?:\s+\*[A-Za-z]+\*)*(?:\s+\[[^\]]*\])?(?:\s+\^[^^]*\^)?)\s*$')


def parse_decklist(text, commanders=()):
    """Plain-text decklist (Moxfield, Archidekt, MTGA, MTGO style) -> [(name, qty, section)].

    Section headers 'Commander', 'Companion', 'Deck'/'Mainboard' are understood; 'Sideboard',
    'Maybeboard' and 'Tokens' blocks are skipped. Inline '*CMDR*' or '[Commander]' marks a commander."""
    out, skipped, section = [], [], ''
    cmd = {c.casefold() for c in commanders}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        head = re.sub(r'^(?://|#)\s*', '', line).rstrip(':').strip().casefold()
        head = re.sub(r'\s*\(\d+\)$', '', head)
        if head in SECTION_HEADERS:
            section = SECTION_HEADERS[head]
            continue
        m = DECK_LINE.match(line)
        if not m:
            raise ValueError(f'cannot read decklist line: {raw!r}')
        if section is None:
            skipped.append(m.group('name'))
            continue
        name, tail = m.group('name').strip(), m.group('tail') or ''
        sec = section
        if name.casefold() in cmd or '*CMDR*' in tail.upper() or re.search(r'\[[^\]]*commander', tail, re.I):
            sec = 'Commander'
        out.append((name, int(m.group('qty')), sec))
    return out, skipped


def import_deck(con, path, deck, status='Current deck', commanders=(), own_missing=False):
    path = Path(path)
    cards, skipped = parse_decklist(path.read_text(encoding='utf-8-sig'), commanders)
    if not cards:
        raise SystemExit(f'no cards read from {path}')
    con.execute('delete from deck_cards where deck=?', (deck,))
    con.execute('delete from holdings where source=?', (f'deck:{deck}',))
    total = {}
    for name, q, sec in cards:
        ensure_card(con, name)
        st = 'Companion' if sec == 'Companion' and status == 'Current deck' else status
        con.execute('insert into deck_cards(deck,card_name,quantity,section,status) values(?,?,?,?,?)', (deck, name, q, sec, st))
        total[name] = total.get(name, 0) + q
    added = {}
    if own_missing and status in collection_db.PHYSICAL:
        for name in total:
            owned = con.execute('select owned from owned where card_name=?', (name,)).fetchone()[0]
            assigned = con.execute('select coalesce(sum(quantity),0) from deck_cards where card_name=? and status in (?,?)',
                                   (name, *collection_db.PHYSICAL)).fetchone()[0]
            if assigned > owned:
                added[name] = assigned - owned
                con.execute('insert into holdings(card_name,quantity,source,notes) values(?,?,?,?)',
                            (name, assigned - owned, f'deck:{deck}', 'added by import-deck --own-missing'))
    log_import(con, 'decklist', f'deck:{deck}', path.name, sha256(path), len(cards),
               json.dumps({'status': status, 'skipped': skipped, 'own_missing_added': added}, ensure_ascii=False))
    con.commit()
    in100 = sum(q for _, q, s in cards if s != 'Companion')
    return {'deck': deck, 'cards': in100, 'commanders': [n for n, _, s in cards if s == 'Commander'],
            'skipped_sideboard_lines': len(skipped), 'holdings_added': sum(added.values())}


# ------------------------------------------------------------------------------- enrichment
def oracle_text_of(card):
    """Oracle text in the Sheet's layout: one block per face, 'Face name {cost}' then its text."""
    faces = card.get('card_faces')
    if faces and any('oracle_text' in f for f in faces) and card.get('oracle_text') is None:
        return '\n\n'.join('\n'.join(x for x in (f"{f.get('name', '')} {f.get('mana_cost', '')}".strip(), f.get('oracle_text', '')) if x)
                           for f in faces)
    return card.get('oracle_text') or ''


def face_join(card, field):
    if card.get(field) is not None:
        return str(card[field])
    vals = [f.get(field) for f in card.get('card_faces') or [] if f.get(field) is not None]
    return ' // '.join(vals) if vals else ''


def etb_tapped(front_type, text):
    if 'Land' not in front_type:
        return 'N/A'
    t = text.casefold()
    if re.search(r"enters(?: the battlefield)? tapped unless|if you don't, (?:it|this land) enters(?: the battlefield)? tapped", t):
        return 'Conditional'
    if re.search(r'(?:this land|it|~) enters(?: the battlefield)? tapped', t) or re.search(r'enters(?: the battlefield)? tapped\.', t):
        return 'Yes'
    return 'No'


def fields_from_scryfall(card):
    """One Scryfall card object -> cards columns, in the canonical Sheet's value conventions."""
    text = oracle_text_of(card)
    type_line = card.get('type_line') or face_join(card, 'type_line')
    front = type_line.split(' // ')[0]
    mana_cost = card.get('mana_cost')
    if mana_cost is None:
        faces = card.get('card_faces') or [{}]
        mana_cost = faces[0].get('mana_cost', '')
    ci = ''.join(c for c in 'WUBRG' if c in (card.get('color_identity') or [])) or 'C'
    produced = card.get('produced_mana') or []
    commander_text = 'can be your commander' in text.casefold()
    rarity = {'mythic': 'Mythic Rare'}.get(card.get('rarity'), str(card.get('rarity') or '').title())
    return {
        'oracle_text': text, 'type_line': type_line, 'mana_cost': mana_cost, 'mana_value': card.get('cmc'),
        'color_identity': ci, 'keywords': '; '.join(card.get('keywords') or []),
        'produces': ''.join(c for c in 'WUBRGC' if c in produced),
        'power': face_join(card, 'power'), 'toughness': face_join(card, 'toughness'), 'rarity': rarity,
        'commander_legal': 'Legal' if (card.get('legalities') or {}).get('commander') == 'legal' else 'Not legal',
        # legendary creatures, legendary Vehicles/Spacecraft with power and toughness, and 'can be your commander' text
        'can_be_commander': 'Yes' if 'Legendary' in front and ('Creature' in front or (
            re.search(r'\b(?:Vehicle|Spacecraft)\b', front) and face_join(card, 'power'))) or commander_text else 'No',
        'etb_tapped': etb_tapped(front, text),
        'scryfall_url': (card.get('scryfall_uri') or '').split('?')[0], 'oracle_id': card.get('oracle_id') or '',
    }


def load_bulk(path):
    """A Scryfall bulk file: a JSON array, or JSON Lines (one card per line); gzip or not."""
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    text = raw.decode('utf-8').lstrip()
    if text.startswith('['):
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


class BulkIndex:
    """Name lookup over a Scryfall bulk 'Oracle Cards' (or 'Default Cards') JSON file."""
    def __init__(self, path):
        data = load_bulk(path)
        rank = lambda c: (c.get('layout') in NON_GAME, (c.get('legalities') or {}).get('commander') == 'not_legal',
                          c.get('set_type') in ('funny', 'memorabilia'))
        self.match = name_matcher(sorted((c for c in data if c.get('layout') not in NOT_A_CARD), key=rank))

    def lookup(self, names):
        return {n: c for n in names if (c := self.match(n))}


def name_matcher(cards):
    """name -> card. Exact full names win, then diacritic-blind full names, then front-face names.
    Back faces are never matched: 'Rampant Growth' is also the back of Studious First-Year."""
    exact, folded, front = {}, {}, {}
    for c in cards:
        exact.setdefault(c['name'].casefold(), c)
        folded.setdefault(fold(c['name']), c)
        faces = [f.get('name') for f in c.get('card_faces') or []] or c['name'].split(' // ')
        if faces and faces[0]:
            front.setdefault(faces[0].casefold(), c)
            front.setdefault(fold(faces[0]), c)

    def match(name):
        head = name.split(' // ')[0]
        return (exact.get(name.casefold()) or folded.get(fold(name))
                or front.get(head.casefold()) or front.get(fold(head)))
    return match


def scryfall_lookup_online(names, pause=0.1):
    """Look names up through Scryfall's /cards/collection endpoint, 75 per request."""
    found = {}
    names = list(names)
    for i in range(0, len(names), 75):
        batch = names[i:i + 75]
        body = json.dumps({'identifiers': [{'name': n.split(' // ')[0]} for n in batch]}).encode()
        req = urllib.request.Request(SCRYFALL_COLLECTION, data=body, method='POST',
                                     headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
        match = name_matcher(data.get('data', []))
        for n in batch:
            if (c := match(n)):
                found[n] = c
        time.sleep(pause)
    return found


def download_bulk(dest_dir):
    req = urllib.request.Request(SCRYFALL_BULK, headers={'Accept': 'application/json', 'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        info = json.load(resp)
    uri = info.get('download_uri') or info['jsonl_download_uri']   # Scryfall now serves gzipped JSON Lines
    dest = Path(dest_dir) / Path(uri).name
    if not dest.exists():
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(uri, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=600) as resp, open(dest, 'wb') as f:
            while chunk := resp.read(1 << 20):
                f.write(chunk)
    return dest


def rename_card(con, old, new):
    """Move a card to its canonical Oracle name, merging into an existing row if there is one."""
    if con.execute('select 1 from cards where card_name=?', (new,)).fetchone():
        con.execute('update holdings set card_name=? where card_name=?', (new, old))
        con.execute('update deck_cards set card_name=? where card_name=?', (new, old))
        con.execute('delete from cards where card_name=?', (old,))
    else:
        con.execute('update cards set card_name=? where card_name=?', (new, old))
    update_card(con, new, {}, {'Recorded / Printed Alias': old})


def enrich(con, scryfall=None, online=False, refresh=False):
    """Fill card data from Scryfall for cards that have no Oracle text yet (all cards with refresh=True)."""
    where = '' if refresh else "where type_line is null or type_line=''"
    names = [r[0] for r in con.execute(f'select card_name from cards {where} order by card_name')]
    if not names:
        return {'looked_up': 0, 'filled': 0, 'renamed': [], 'not_found': []}
    if scryfall:
        found = BulkIndex(scryfall).lookup(names)
        label = f'scryfall-bulk:{sha256(scryfall)[:12]}'
    elif online:
        found = scryfall_lookup_online(names)
        label = f'scryfall-api:{datetime.date.today().isoformat()}'
    else:
        raise SystemExit('give --scryfall FILE or --online')
    renamed = []
    for name, card in found.items():
        target = card['name']
        if target != name:
            rename_card(con, name, target)
            renamed.append([name, target])
        update_card(con, target, fields_from_scryfall(card), source=label)
    missing = sorted(set(names) - set(found))
    log_import(con, 'enrich', label, Path(scryfall).name if scryfall else None, sha256(scryfall) if scryfall else None,
               len(found), json.dumps({'not_found': missing, 'renamed': renamed}, ensure_ascii=False))
    con.commit()
    return {'looked_up': len(names), 'filled': len(found), 'renamed': renamed, 'not_found': missing}


# ------------------------------------------------------------------------------- checks
def check(db):
    raw = collection_db.read(db)
    data = _adapter.normalize(raw)
    con = sqlite3.connect(db)
    missing = [r[0] for r in con.execute("select card_name from cards where type_line is null or type_line='' order by card_name")]
    con.close()
    h = data['health']
    return {'collection': collection_db.identity(db)['label'],
            'card_names': h['cards_in_collection'], 'owned_names': h['card_names_with_known_copies'],
            'copies': h['known_physical_copy_minimum'], 'decks': h['deck_counts'],
            'cards_without_card_data': len(missing), 'cards_without_card_data_sample': missing[:20],
            'problems': [i for i in data['issues'] if i['severity'] in ('critical', 'high')],
            'ready_for_evaluator': not missing and not any(i['severity'] == 'critical' for i in data['issues']),
            'ready_for_kb_build': not missing and not (h['critical_problems'] or h['high_problems'])}


# ------------------------------------------------------------------------------- CLI
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='Setup guide: docs/BRING_YOUR_OWN_COLLECTION.md')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init', help='create an empty collection database')
    s.add_argument('db'); s.add_argument('--name', help='collection label shown in reports'); s.add_argument('--owner')
    s = sub.add_parser('import-csv', help='import a collection CSV (Moxfield, Archidekt, ManaBox, Deckbox, or your own)')
    s.add_argument('db'); s.add_argument('csv'); s.add_argument('--source', help='label for this import; re-importing it replaces its rows (default: file name)')
    s = sub.add_parser('import-xlsx', help='import an .xlsx Sheet export: the canonical layout, or one tab as a card list')
    s.add_argument('db'); s.add_argument('xlsx'); s.add_argument('--source')
    s.add_argument('--tab', help='tab holding a plain card list (default: canonical layout if present, else the first tab)')
    s.add_argument('--header-row', type=int, help='row number of the header in --tab (default 1)')
    s.add_argument('--sheet-id', help='Google Sheet id the export came from, recorded as provenance')
    s = sub.add_parser('import-deck', help='import a plain-text decklist as a deck')
    s.add_argument('db'); s.add_argument('decklist'); s.add_argument('--deck', required=True)
    s.add_argument('--commander', action='append', default=[], help='mark this card as a commander (repeatable)')
    s.add_argument('--status', default='Current deck', help="'Current deck' (physically built, default) or a plan label such as 'Candidate'")
    s.add_argument('--own-missing', action='store_true', help='add holdings for deck cards your collection import does not cover')
    s = sub.add_parser('enrich', help='fill Oracle text, types and legality from Scryfall')
    s.add_argument('db'); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument('--scryfall', help="Scryfall bulk 'Oracle Cards' file (.json, .jsonl or .jsonl.gz)")
    g.add_argument('--online', action='store_true', help='look cards up through the Scryfall API (75 per request)')
    g.add_argument('--download', metavar='DIR', help="download Scryfall's Oracle Cards bulk file into DIR, then use it")
    s.add_argument('--refresh', action='store_true', help='re-fetch card data for every card, not only cards without it')
    s = sub.add_parser('check', help='report counts, missing card data and inventory problems')
    s.add_argument('db')
    a = p.parse_args(argv)

    if a.cmd == 'init':
        con = connect(a.db, create=True)
        set_meta(con, collection_name=a.name or Path(a.db).stem, owner=a.owner)
        con.commit()
        result = {'created': str(a.db), 'schema_version': SCHEMA_VERSION}
    elif a.cmd == 'check':
        result = check(a.db)
    else:
        con = connect(a.db)
        if a.cmd == 'import-csv':
            result = import_csv(con, a.csv, a.source)
        elif a.cmd == 'import-xlsx':
            result = import_xlsx(con, a.xlsx, a.source, a.tab, a.header_row, a.sheet_id)
        elif a.cmd == 'import-deck':
            result = import_deck(con, a.decklist, a.deck, a.status, a.commander, a.own_missing)
        elif a.cmd == 'enrich':
            scry = download_bulk(a.download) if a.download else a.scryfall
            result = enrich(con, scry, a.online, a.refresh)
        con.close()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
