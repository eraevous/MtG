#!/usr/bin/env python3
"""Scenario tests for operation contracts: the only evidence a review or a runtime certificate may cite.

A scenario lives in scenarios/*.json and names one contract. It has two independent parts:

  semantic  assertions about what the contract says (typed mana pools and payability, hooks and their
            qualifiers, cost components, targets, zone transitions, amplifiers, payment events).
            A human `verified` review must cite at least one scenario whose semantic part passes on
            the current contract. A placeholder or unknown id is refused.
  runtime   what the compiled action must do when the 0.3.0 engine resolves it (draws, tokens,
            counters, drain ...). Runtime certificates are issued by the build, never by a reviewer,
            and only for a contract whose compile is lossless and whose runtime part passes.

  python scenarios.py --db mtg_cards_v0.2.sqlite list [--contract ID]
  python scenarios.py --db mtg_cards_v0.2.sqlite run ID
"""
import argparse, glob, json, re, sqlite3, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kbfacts as F, mana as MANA

SCENARIO_VERSION = 'scenarios-0.1.0'
ID_RE = re.compile(r'^[a-z0-9][a-z0-9_.\-]*$')


def load(dirpath=HERE / 'scenarios'):
    out = {}
    for p in sorted(glob.glob(str(Path(dirpath) / '*.json'))):
        for s in json.loads(Path(p).read_text(encoding='utf-8'))['scenarios']:
            if not ID_RE.match(s['id']): raise ValueError(f"bad scenario id {s['id']!r} in {p}")
            if s['id'] in out: raise ValueError(f"duplicate scenario id {s['id']}")
            out[s['id']] = dict(s, file=Path(p).name, scenario_sha256=F.sha(F.dumps(s)))
    return out


def registry_sha(dirpath=HERE / 'scenarios'):
    return F.sha(*[Path(p).read_text(encoding='utf-8') for p in sorted(glob.glob(str(Path(dirpath) / '*.json')))])


# ---------------------------------------------------------------- semantic assertions
def _mana_items(c):
    return [p['mana'] for p in c['result']['produces'] if p['id'] == 'mana.add' and p.get('mana') and not p.get('granted_to_other_object')]


def _hooks(c):
    return [h for g in c['initiation']['requirement_groups'] if g['class'] == 'trigger' for h in g['alternatives']]


def _costs(c):
    return [g['alternatives'][0] for g in c['initiation']['requirement_groups'] if g['class'] == 'cost']


def _canon(pools):
    return sorted(sorted(u['type'] for u in p) for p in pools)


def check_semantic(a, c):
    """One assertion against a contract -> (passed, observed)."""
    op = a['op']
    if op == 'produces_pools':
        got = [_canon(MANA.production_pools(m, chosen=a.get('chosen'))) for m in _mana_items(c)]
        want = sorted(sorted(p) for p in a['pools'])
        return (len(got) == 1 and got[0] == want), got
    if op == 'production_pays':  # can some pool this ability adds pay the cost?
        ms = _mana_items(c)
        ok = any(MANA.can_pay(a['cost'], p) for m in ms for p in MANA.production_pools(m, chosen=a.get('chosen')))
        return ok == a['expect'], ok
    if op == 'hook':
        hs = _hooks(c)
        hit = [h for h in hs if h['id'] == a['id'] and all(h['qualifiers'].get(k) == v for k, v in a.get('qualifiers', {}).items())]
        return bool(hit), [{'id': h['id'], 'qualifiers': h['qualifiers']} for h in hs]
    if op == 'no_hook':
        return all(h['id'] != a['id'] for h in _hooks(c)), [h['id'] for h in _hooks(c)]
    if op == 'cost':
        cs = _costs(c)
        hit = [x for x in cs if all(x.get(k) == v for k, v in a['match'].items())]
        return bool(hit), [{k: x.get(k) for k in ('family', 'subject', 'object_filter', 'text', 'act_time')} for x in cs]
    if op == 'no_cost_family':
        return all(x.get('family') != a['family'] for x in _costs(c)), [x.get('family') for x in _costs(c)]
    if op == 'on_payment_includes':
        got = c['initiation']['cost']['on_payment']
        return any(e.startswith(a['event']) for e in got), got
    if op == 'effect':
        got = [{k: p.get(k) for k in ('id', 'as', 'act_time', 'object') if p.get(k) is not None} for p in c['result']['produces']]
        return any(all(p.get(k) == v for k, v in a['match'].items()) for p in c['result']['produces']), got
    if op == 'transitions':
        got = sorted((t['from'], t['to']) for t in c['result']['transitions'] if 'from' in t)
        return got == sorted(tuple(x) for x in a['expect']), got
    if op == 'target':
        got = [g['alternatives'][0].get('text') for g in c['initiation']['requirement_groups'] if g['class'] == 'eligibility']
        return any(a['text_contains'] in (t or '') for t in got), got
    if op == 'amplifier':
        got = [x['measures'] for x in c['initiation']['amplifiers']]
        return any(a['measures_contains'] in m for m in got), got
    if op == 'unbound_includes':
        return any(a['text_contains'] in u for u in c['unbound']), c['unbound']
    raise ValueError(f'unknown semantic op {op}')


# ---------------------------------------------------------------- runtime harness (0.3.0 engine)
def run_action(action, card_name, types=('creature',)):
    """Resolve a compiled action's outputs in a bare 0.3.0 engine Game and report what happened."""
    for p in (str(HERE), str(HERE / 'vendor')):
        if p not in sys.path: sys.path.insert(0, p)
    from mtg_eval.engine import Game
    g = Game.__new__(Game)
    g.bf, g.lands, g.nid, g.t, g.lib, g.hand, g.pos = [], [], 0, 1, ['library card'] * 20, [], 0
    g.drawn = g.drain = g.reach = g.spells_turn = g.dmg = 0
    g.m, g.log, g.combat_no, g.reserved, g.station_done = defaultdict(float), None, 0, set(), {}
    src = None if action['kind'] == 'spell' else g.new(card_name, types=set(types))
    if src is not None: src.sick = False
    g.resolve([tuple(o) for o in action.get('outputs') or []], src)
    tokens = sorted([{'types': sorted(o.types), 'subtypes': sorted(o.subtypes), 'power': o.power, 'toughness': o.tough}
                     for o in g.bf if o.token], key=json.dumps)
    return {'drawn': g.drawn, 'tokens': tokens, 'token_count': len(tokens), 'drain': g.drain, 'reach': g.reach,
            'counters_on_source': src.counters if src is not None else 0,
            'metrics': {k.split('@')[0]: v for k, v in sorted(g.m.items())}}


def check_runtime(expect, observed):
    bad = {k: (v, observed.get(k)) for k, v in expect.items() if observed.get(k) != v}
    return not bad, bad


# ---------------------------------------------------------------- evaluation against a DB
def contract_row(con, cid):
    return con.execute('select k.contract_id,k.contract_sha256,k.card_name,k.contract_json,k.proposed_action_json '
                       'from current_contracts k where contract_id=?', (cid,)).fetchone()


def run_semantic(con, sc):
    r = contract_row(con, sc['contract_id'])
    if r is None: return {'scenario': sc['id'], 'passed': False, 'error': 'contract not found'}
    c = F.loads(r[3])
    results = []
    for a in sc.get('semantic', []):
        try: ok, obs = check_semantic(a, c)
        except Exception as e: ok, obs = False, f'error: {e}'
        results.append({'assert': a, 'passed': ok, 'observed': obs})
    return {'scenario': sc['id'], 'contract_id': sc['contract_id'], 'contract_sha256': r[1], 'scenario_sha256': sc['scenario_sha256'],
            'passed': bool(results) and all(x['passed'] for x in results), 'results': results}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db', default=str(HERE / 'mtg_cards_v0.2.sqlite'))
    sub = ap.add_subparsers(dest='cmd', required=True)
    l = sub.add_parser('list'); l.add_argument('--contract')
    r = sub.add_parser('run'); r.add_argument('id')
    a = ap.parse_args()
    reg = load()
    con = sqlite3.connect(Path(a.db).resolve().as_uri() + '?mode=ro', uri=True)
    if a.cmd == 'list':
        for s in reg.values():
            if not a.contract or s['contract_id'] == a.contract: print(s['id'], '\t', s['contract_id'], '\t', s.get('description', ''))
    else:
        print(json.dumps(run_semantic(con, reg[a.id]), indent=1, default=str, ensure_ascii=False))


if __name__ == '__main__':
    main()
