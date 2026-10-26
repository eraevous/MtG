"""Command line: one program, one subcommand per question.

  mtgeval --workbook export.xlsx card "Altered Ego" [--deck "Counter Blitz"]
  mtgeval --workbook export.xlsx deck Vraska
  mtgeval --workbook export.xlsx module TMNT go_wide
  mtgeval --workbook export.xlsx compare TMNT "Crustacean Commando=Knockout Maneuver"
  mtgeval --workbook export.xlsx upgrades Sharuum --protect Dina [--transfers] [--top 5]
  mtgeval --workbook export.xlsx build "Balmor, Battlemage Captain"
  mtgeval --workbook export.xlsx inventory
  mtgeval --workbook export.xlsx transfer "Cauldron of Essence" Dina Necrobloom [--backfill "Boggart Mischief"]
  mtgeval --workbook export.xlsx portfolio "Duty Beyond Death" [--objective protection:anti_wipe]

The workbook can also come from the MTG_WORKBOOK environment variable.
"""
import argparse
import os
import sys

from .api import Evaluator
from . import report


def main(argv=None):
    # global options work before or after the subcommand
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--workbook', default=argparse.SUPPRESS, help='read-only .xlsx export of the canonical sheet')
    common.add_argument('--games', type=int, default=argparse.SUPPRESS, help='goldfish games per deck version (default 5000)')
    common.add_argument('--engine-games', type=int, default=argparse.SUPPRESS, help='turn-engine games per scenario (default 300; 0 turns the engine off)')
    common.add_argument('--json', action='store_true', default=argparse.SUPPRESS, help='print JSON instead of Markdown')
    common.add_argument('--out', default=argparse.SUPPRESS, help='write the report to this file')
    p = argparse.ArgumentParser(prog='mtgeval', parents=[common], description='Evaluate cards, decks, modules, swaps, builds, transfers and the portfolio.')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('card', parents=[common]); s.add_argument('name'); s.add_argument('--deck')
    s = sub.add_parser('deck', parents=[common]); s.add_argument('name')
    s = sub.add_parser('module', parents=[common]); s.add_argument('deck'); s.add_argument('module')
    s = sub.add_parser('compare', parents=[common]); s.add_argument('deck'); s.add_argument('swaps', nargs='+', help='OUT=IN pairs; leave a side empty to only add or only cut')
    s = sub.add_parser('upgrades', parents=[common]); s.add_argument('deck'); s.add_argument('--top', type=int, default=5); s.add_argument('--weakest', type=int, default=3)
    s.add_argument('--protect', nargs='*', default=[], help='decks never used as donors'); s.add_argument('--transfers', action='store_true', help='also consider cards held by other decks')
    s = sub.add_parser('build', parents=[common]); s.add_argument('commander'); s.add_argument('--lands', type=int, default=36)
    sub.add_parser('inventory', parents=[common])
    s = sub.add_parser('transfer', parents=[common]); s.add_argument('card'); s.add_argument('src'); s.add_argument('dst'); s.add_argument('--backfill'); s.add_argument('--cut')
    s = sub.add_parser('portfolio', parents=[common]); s.add_argument('card'); s.add_argument('--decks', nargs='*'); s.add_argument('--objective', default='protection:anti_wipe')
    s = sub.add_parser('regress', parents=[common], help='compare this export with a frozen snapshot and list every difference (never accepts it)')
    s.add_argument('expected', help='tests/expected_<sha12>.json or another frozen snapshot')
    a = p.parse_args(argv)
    a.workbook = getattr(a, 'workbook', None) or os.environ.get('MTG_WORKBOOK')
    a.games = getattr(a, 'games', 5000); a.engine_games = getattr(a, 'engine_games', 300)
    a.json = getattr(a, 'json', False); a.out = getattr(a, 'out', None)
    if not a.workbook: p.error('give --workbook or set MTG_WORKBOOK')
    ev = Evaluator(a.workbook, games=a.games, engine_games=a.engine_games)
    if a.cmd == 'regress':
        from .regression import snapshot, diff
        import json
        with open(a.expected) as f: want = json.load(f)
        lines = diff(want, json.loads(json.dumps(snapshot(ev))))
        text = '\n'.join(lines) if lines else 'No differences.'
        print(text) if not a.out else open(a.out, 'w').write(text)
        return 1 if lines else 0
    try:
        if a.cmd == 'card': res = ev.card(a.name, a.deck)
        elif a.cmd == 'deck': res = ev.deck(a.name)
        elif a.cmd == 'module': res = ev.module(a.deck, a.module)
        elif a.cmd == 'compare': res = ev.compare(a.deck, [tuple((x.split('=', 1) + [''])[:2]) for x in a.swaps])
        elif a.cmd == 'upgrades': res = ev.upgrades(a.deck, a.top, a.weakest, a.protect, a.transfers)
        elif a.cmd == 'build': res = ev.build(a.commander, a.lands)
        elif a.cmd == 'inventory': res = ev.inventory()
        elif a.cmd == 'transfer': res = ev.transfer(a.card, a.src, a.dst, a.backfill, a.cut)
        elif a.cmd == 'portfolio': res = ev.portfolio(a.card, a.decks, a.objective)
    except KeyError as e:
        print(f'error: {e.args[0]}', file=sys.stderr); return 2
    text = report.to_json(res) if a.json else report.markdown(res)
    if a.out:
        with open(a.out, 'w') as f: f.write(text)
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
