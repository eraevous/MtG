"""Read-only inventory: Collection + current-deck allocations from one export of the canonical sheet.

Reads the workbook through the vendored inventory adapter (_adapter.read_xlsx_selected,
Kate's stdlib OOXML reader). Nothing is ever written back. Rows behave like the earlier
pandas rows: an empty cell reads as NaN, numeric columns read as numbers.
"""
import hashlib
import math
from pathlib import Path

from . import _adapter

CANONICAL_ID = _adapter.CANONICAL_ID
BASICS = {'Forest', 'Island', 'Swamp', 'Mountain', 'Plains', 'Wastes'}
NON_DECK = {'______', 'Counters', 'Elemental', 'Finch Formation', 'Rust-Shield Rampager', 'Thornplate Intimidator'}
COLORS = 'WUBRG'
NUMERIC = {'Mana Value', 'Known Qty (min)', 'Copies in Decks', 'Copies Free', 'Quantity'}
NAN = float('nan')


def notna(v):
    return not (isinstance(v, float) and math.isnan(v))


def ci_set(s):
    return {c for c in str(s) if c in COLORS}


class Row(dict):
    """A Collection row. Missing or empty cells read as NaN (like the earlier pandas reader)."""
    def __getitem__(self, k):
        v = dict.get(self, k, '')
        if v == '' or v is None: return NAN
        if k in NUMERIC:
            try:
                f = float(v); return int(f) if f.is_integer() else f
            except (TypeError, ValueError):
                return v
        return v


class Inventory:
    """Collection and the current physical decks. Sizes: every current deck is 100 cards;
    a companion is held in custody but sits outside the 100."""
    def __init__(self, xlsx, labels=None):
        self.path = Path(xlsx)
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        raw = _adapter.read_xlsx_selected(str(self.path), {'Collection', 'Deck Allocations'})
        self.cards = {}
        for r in raw['Collection']:
            n = str(r.get('Card Name', '')).strip()
            if n and n not in NON_DECK: self.cards[n] = Row(r)
        self.decks = {}
        for r in raw['Deck Allocations']:
            if str(r.get('Status', '')).strip() not in ('Current deck', 'Companion'): continue
            n = str(r.get('Card Name', '')).strip()
            if not n or n in NON_DECK: continue
            q = float(r.get('Quantity') or 0)
            self.decks.setdefault(str(r['Deck']).strip(), []).append((n, int(q), str(r.get('Section', '')).strip()))
        from .semantics import load_labels  # late import: semantics needs nothing from here at import time
        self.labels = load_labels() if labels is None else labels
        self._rec = {}

    # ------------------------------------------------------------ provenance
    def source(self):
        return {'sheet_id': CANONICAL_ID, 'export': self.path.name, 'sha256': self.sha256,
                'note': 'read-only export of the live canonical sheet; regenerate after sheet edits'}

    # ------------------------------------------------------------ card record
    def record(self, name):
        from .semantics import capability_record
        if name not in self._rec:
            self._rec[name] = capability_record(self.cards[name], self.labels) if name in self.cards else {}
        return self._rec[name]

    def supported(self, name):
        return {f for f, v in self.record(name).items() if v['status'] == 'supported'}

    # ------------------------------------------------------------ decks and custody
    def commanders(self, deck):
        return [n for n, _, s in self.decks[deck] if s == 'Commander']

    def deck_cards(self, deck):
        return [n for n, _, _ in self.decks[deck]]

    def deck_ci(self, deck):
        return set().union(*[ci_set(self.cards[n]['Color Identity']) for n in self.commanders(deck)])

    def free(self, name):
        r = self.cards.get(name)
        if name in BASICS: return 10 ** 6
        return int(r['Copies Free']) if r is not None and notna(r['Copies Free']) else 0

    def owned(self, name):
        r = self.cards.get(name)
        return int(r['Known Qty (min)']) if r is not None and notna(r['Known Qty (min)']) else 0

    def holders(self, name):
        return sorted(d for d in self.decks if name in self.deck_cards(d))

    def legal_in(self, name, ci):
        r = self.cards.get(name)
        if r is None: return False, 'not in Collection'
        if r['Commander Legal'] != 'Legal': return False, 'not Commander legal'
        if not ci_set(r['Color Identity']) <= ci: return False, f"color identity {r['Color Identity']} outside {''.join(c for c in COLORS if c in ci)}"
        return True, ''

    def is_land(self, name):
        return name in BASICS or 'Land' in str(self.cards[name]['Type Line']) and 'Creature' not in str(self.cards[name]['Type Line'])

    def multicolor_land(self, name):
        return self.is_land(name) and name not in BASICS and len(ci_set(self.cards[name]['Produces'])) >= 2

    def find(self, name):
        """Exact name, else a unique case-insensitive prefix or front-face match."""
        if name in self.cards or name in self.decks: return name
        low = name.lower()
        hits = [n for n in list(self.cards) + list(self.decks) if n.lower() == low or n.lower().split(' // ')[0] == low]
        hits = hits or [n for n in list(self.decks) + list(self.cards) if n.lower().startswith(low)]
        if len(set(hits)) == 1: return hits[0]
        raise KeyError(f'{name!r}: ' + ('no match' if not hits else 'ambiguous: ' + ', '.join(sorted(set(hits))[:8])))
