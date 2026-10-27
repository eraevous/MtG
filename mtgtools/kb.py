"""Access to the derived KB through kb/kbq.py, the KB's own read-only query layer. The KB is the only source of
card meaning these tools use (P-01); the database is opened read-only."""
import sys
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / 'kb'
sys.path.insert(0, str(KB_DIR))

import kbq  # noqa: E402

DEFAULT_DB = KB_DIR / 'mtg_cards_v0.2.sqlite'
COLORS, FEEDS, THEMES = kbq.COLORS, kbq.FEEDS, kbq.THEMES
connect, card, destinations, theme, overlap = kbq.connect, kbq.card, kbq.destinations, kbq.theme, kbq.overlap
deck_ci, deck_cards, legal_rules = kbq.deck_ci, kbq.deck_cards, kbq.legal_rules


def decks(c):
    return [r[0] for r in c.execute('select distinct deck from active_deck_cards order by deck')]


def release(db):
    """The KB release and inventory snapshot a database was built from, read from SOURCE_MANIFEST.json beside it."""
    import json
    m = Path(db).resolve().parent / 'SOURCE_MANIFEST.json'
    if not m.exists():
        return {'release': None, 'note': 'no SOURCE_MANIFEST.json beside this database'}
    j = json.loads(m.read_text(encoding='utf-8'))
    inv = j.get('inventory_source', {})
    return {'release': j.get('release'), 'built_utc': j.get('built_utc'),
            'inventory_snapshot_sha256': inv.get('input_sha256'), 'inventory_snapshot_modified_utc': inv.get('drive_modified_utc')}
