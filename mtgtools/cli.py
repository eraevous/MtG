"""Command line: one program, six read-only verbs, JSON out.

  python3 -m mtgtools context [--deck Vraska]
  python3 -m mtgtools card "Terra, Magical Adept"
  python3 -m mtgtools explore ["Terra, Magical Adept" | landfall] [--ci RG] [--deck D] [--free] [--mode focused|divergent]
  python3 -m mtgtools hypothesis "Card A" "Card B" [--effect token.create] [--ci RG]
  python3 -m mtgtools compare TMNT "Crustacean Commando=Knockout Maneuver" [--workbook export.xlsx]
  python3 -m mtgtools check claims.json        (a JSON list of {text, kind, cards[], deck?, assert?})

--db picks the collection: any SQLite built by kb/migrate_v02.py (default kb/mtg_cards_v0.2.sqlite).
"""
import argparse
import json
from contextlib import closing
import os
import sys
from pathlib import Path

from . import __version__, kb, verbs

ROOT = Path(__file__).resolve().parent.parent


def envelope(verb, query, db, data=None, claims=None, error=None):
    claims = claims or []
    grades = {}
    for c in claims:
        grades[c['grade']] = grades.get(c['grade'], 0) + 1
    out = {'tool': 'mtg', 'version': __version__, 'verb': verb, 'query': query,
           'collection': {'db': str(db), **kb.release(db)},
           'summary': {'claims': len(claims), 'by_grade': grades},
           'read_me_first': 'Each claim carries its own kind and grade. decision_grade on one kind (inventory, rules_text, '
                            'mechanics) says nothing about the others. performance is never decision_grade in v0, and '
                            'preference belongs to the person (deck charter), not to these tools. A good source is not a true '
                            'claim: check reports evidence_grade (the source) apart from verdict (whether a structured '
                            'assertion holds). Links carry qualifiers: compatible, or unresolved when the contracts do not '
                            'record what would decide it; rejected links and contested loops rule out one route, not the card.'}
    if error:
        out['error'] = error
    else:
        out['claims'] = claims
        out['data'] = data
    return out


def _workbook(a):
    wb = a.workbook or os.environ.get('MTG_WORKBOOK')
    if wb:
        return wb
    found = sorted((ROOT / 'data').glob('*.xlsx'))
    if not found:
        raise LookupError('compare needs --workbook, MTG_WORKBOOK or an export in data/ (see data/README.md)')
    return str(found[-1])


def _read_claims(path):
    if path == '-':
        return json.load(sys.stdin)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main(argv=None):
    p = argparse.ArgumentParser(prog='mtg', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--db', default=str(kb.DEFAULT_DB), help='collection database (default: kb/mtg_cards_v0.2.sqlite)')
    sub = p.add_subparsers(dest='verb', required=True)
    s = sub.add_parser('context'); s.add_argument('--deck')
    s = sub.add_parser('card'); s.add_argument('name')
    s = sub.add_parser('explore'); s.add_argument('seed', nargs='?', help='a card, a commander or a theme; optional')
    s.add_argument('--ci'); s.add_argument('--deck'); s.add_argument('--free', action='store_true')
    s.add_argument('--mode', choices=['focused', 'divergent'], default='focused'); s.add_argument('--limit', type=int, default=25)
    s = sub.add_parser('hypothesis'); s.add_argument('a'); s.add_argument('b'); s.add_argument('--effect'); s.add_argument('--ci')
    s = sub.add_parser('compare'); s.add_argument('deck'); s.add_argument('swaps', nargs='+', help='OUT=IN pairs')
    s.add_argument('--workbook'); s.add_argument('--engine-games', type=int, default=0)
    s = sub.add_parser('check'); s.add_argument('claims', help='JSON file with a list of claims, or - for stdin')
    a = p.parse_args(argv)
    query = {k: v for k, v in vars(a).items() if k not in ('verb', 'db') and v not in (None, False)}
    if not Path(a.db).exists():
        print(json.dumps(envelope(a.verb, query, a.db, error=f'collection database not found: {a.db} (see data/README.md)'), indent=2))
        return 2
    try:
        if a.verb == 'compare':
            data, claims = verbs.compare(a.deck, a.swaps, _workbook(a), a.engine_games)
        else:
            with closing(kb.connect(a.db)) as c:
                if a.verb == 'context':
                    data, claims = verbs.context(c, a.deck)
                elif a.verb == 'card':
                    data, claims = verbs.card(c, a.name)
                elif a.verb == 'explore':
                    data, claims = verbs.explore(c, a.seed, a.ci, a.deck, a.free, a.mode, a.limit)
                elif a.verb == 'hypothesis':
                    data, claims = verbs.hypothesis(c, a.a, a.b, a.effect, a.ci)
                else:
                    items = _read_claims(a.claims)
                    data, claims = verbs.check(c, items)
    except (LookupError, ValueError, KeyError) as e:
        print(json.dumps(envelope(a.verb, query, a.db, error=str(e.args[0] if e.args else e)), indent=2, ensure_ascii=False))
        return 2
    print(json.dumps(envelope(a.verb, query, a.db, data, claims), indent=2, ensure_ascii=False, default=str))
    return 0
