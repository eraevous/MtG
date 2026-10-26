"""Event routing between cards (0.3.0): which ability's output starts which other ability, and what
kind of engine that makes. Built from abilities.card_record, so cast and enter stay separate
hooks: a token entering never reaches a "whenever you cast" ability.

Engine classes are kept apart (Kate, 2026-10-19); none of them means "good" by itself:
- parallel producers: independent sources of the same event (source redundancy);
- linear payoff: an event turned into an end output (damage, cards, mana) that feeds nothing back;
- feed-forward chain: A's output starts B, whose output starts C, with no way back to A;
- replacement amplification: a replacement adds output to every matching event (Stridehangar shape);
- scaling: an output whose size grows with a count (pump +X where X is your artifacts);
- bounded feedback: a cycle that a once-per-turn cap or a cost limits;
- unbounded feedback: a cycle with neither (reported, never assumed to win);
- resource-quality feedback: output raises the power that a station or crew cost spends."""
from collections import defaultdict
from .abilities import card_record
from .engine import matches

TERMINAL = {'drain': 'damage to each opponent', 'reach': 'damage to any target', 'draw': 'cards', 'mana': 'mana',
            'life': 'life', 'counters': 'power', 'pump_team': 'power', 'pump_one': 'power', 'pump_team_x': 'power',
            'charge': 'station charge', 'interaction': 'interaction', 'removal': 'removal', 'evasion': 'evasion',
            'recursion': 'recursion', 'proliferate': 'counters', 'wipe': 'wipe'}


def _card_types(inv, c):
    tl = str(inv.cards[c]['Type Line']).split(' // ')[0].lower()
    out = {w for w in ('artifact', 'creature', 'enchantment', 'instant', 'sorcery', 'planeswalker', 'lesson') if w in tl}
    if '—' in tl: out |= {'sub:' + w for w in tl.split('—')[-1].split()}
    return out


def build(inv, cards):
    """Nodes: ('cast', card) for casting each nonland card, and (card, i) for each ability.
    Returns {'nodes', 'edges', 'emits', 'labels'}."""
    nodes, emits, labels, info = [], {}, {}, {}
    recs = {c: card_record(inv, c) for c in cards}
    for c in cards:
        types = _card_types(inv, c)
        n = ('cast', c); nodes.append(n); labels[n] = f'cast {c}'
        ev = [('cast', frozenset(types), False, c)]
        if not types & {'instant', 'sorcery'}: ev.append(('enter', frozenset(types), False, c))
        else:
            for a in recs[c]['abilities']:
                if a['kind'] == 'spell': ev += _out_events(a['outputs'], c)
        emits[n] = ev
        for i, a in enumerate(recs[c]['abilities']):
            if a['kind'] not in ('triggered', 'activated'): continue
            k = (c, i); nodes.append(k); info[k] = a
            labels[k] = f"{c}: {a['hook'][0] if a['hook'] else 'activated'}"
            emits[k] = _out_events(a['outputs'], c)
        for j, r in enumerate(recs[c]['statics'].get('replacement_create', [])):
            k = (c, 'replace', j); nodes.append(k); info[k] = {'kind': 'replacement', 'filter': r['filter'], 'gates': {}}
            labels[k] = f'{c}: replacement'
            emits[k] = []
            for x in r['extra']:
                ty = frozenset(set(x['types']) | {'sub:' + y for y in x['subtypes']})
                emits[k] += [('create', ty, True, c), ('enter', ty, True, c)]
        st = recs[c]['statics']
        if st.get('station'):
            k = (c, 'station'); nodes.append(k); info[k] = {'kind': 'station', 'gates': {}}
            labels[k] = f'{c}: station'
            emits[k] = [('terminal', 'station charge', c)]
            for lv in st.get('station_levels', []):
                if lv['anthem']: emits[k].append(('terminal', 'power', c))
    edges = defaultdict(set)
    for a in nodes:
        for e in emits[a]:
            if e[0] == 'terminal': continue
            for b in nodes:
                if b[0] == 'cast' or (b == a and not e[2]): continue  # a token it makes can re-trigger it
                ab = info.get(b)
                if ab is None: continue
                if ab['kind'] == 'replacement':
                    if e[0] == 'create' and e[2] and matches(ab['filter'], spell_types=set(e[1]), is_token=True) and a[0] != b[0]: edges[a].add(b)
                    continue
                if ab['kind'] != 'triggered' or not ab['hook']: continue
                hk, h = ab['hook']
                if hk != e[0]: continue
                if not _hook_ok(hk, h, e, b[0]): continue
                edges[a].add(b)
            if e[0] in ('enter', 'create') and 'creature' in e[1]:
                for b in nodes:
                    if info.get(b, {}).get('kind') == 'station': edges[a].add(b)  # new bodies can pay station
    # kb patch 2 (2026-10-22): successors in node order, so cycles and chains do not depend on PYTHONHASHSEED
    order = {n: i for i, n in enumerate(nodes)}
    edges = {a: sorted(bs, key=order.__getitem__) for a, bs in edges.items()}
    return {'nodes': nodes, 'edges': edges, 'emits': emits, 'labels': labels, 'info': info}


def _out_events(outs, c):
    ev = []
    for o in outs:
        if o[0] == 'token':
            ty = frozenset(set(o[1]['types']) | {'sub:' + x for x in o[1]['subtypes']})
            ev += [('create', ty, True, c), ('enter', ty, True, c)]
        elif o[0] == 'scry_surveil': ev.append(('scry_surveil', frozenset(), False, c))
        if o[0] == 'counters': ev.append(('counters', frozenset({'creature'}), False, c))
        if o[0] == 'life': ev.append(('lifegain', frozenset(), False, c))
        if o[0] == 'draw': ev.append(('draw', frozenset(), False, c))
        if o[0] in TERMINAL: ev.append(('terminal', TERMINAL[o[0]], c))
    return ev


def _hook_ok(hk, h, e, owner):
    if hk == 'cast':
        if 'second spell' in h: return True
        return matches(h, spell_types=set(e[1]))
    if hk == 'counters': return matches(h.get('types', {'any'}), spell_types=set(e[1]))
    if hk in ('lifegain', 'draw'): return True
    if hk in ('enter', 'create'):
        if h.get('self'): return e[3] == owner and not e[2]
        if h.get('self_or_other'): return (e[3] == owner and not e[2]) or matches(h['types'], spell_types=set(e[1]), is_token=e[2])
        if h.get('other') and e[3] == owner and not e[2]: return False
        return matches(h.get('types', {'any'}), spell_types=set(e[1]), is_token=e[2])
    return hk == 'scry_surveil'



def _sccs(nodes, edges):
    idx, low, stack, on, out, n = {}, {}, [], set(), [], [0]
    import sys
    sys.setrecursionlimit(10000)
    def visit(v):
        idx[v] = low[v] = n[0]; n[0] += 1; stack.append(v); on.add(v)
        for w in edges.get(v, ()):
            if w not in idx: visit(w); low[v] = min(low[v], low[w])
            elif w in on: low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stack.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in nodes:
        if v not in idx: visit(v)
    return out


def classify(inv, cards):
    g = build(inv, cards)
    nodes, edges, emits, labels, info = g['nodes'], g['edges'], g['emits'], g['labels'], g['info']
    out = {'parallel producers': [], 'linear payoffs': [], 'feed-forward chains': [], 'replacement amplification': [],
           'scaling': [], 'bounded feedback': [], 'unbounded feedback': [], 'resource-quality feedback': []}
    # producers of token entries, by family
    fam = defaultdict(set)
    for k in nodes:
        if k[0] == 'cast' or info.get(k, {}).get('kind') == 'replacement': continue
        for e in emits[k]:
            if e[0] == 'enter' and e[2]:
                fam['artifact token' if 'artifact' in e[1] else 'creature token'].add(k[0])
                if 'artifact' in e[1] and 'creature' in e[1]: fam['creature token'].add(k[0])
    for f, srcs in sorted(fam.items()):
        out['parallel producers'].append({'event': f + ' enters', 'independent sources': len(srcs), 'cards': sorted(srcs)})
    # linear payoffs: a triggered ability whose outputs are all terminal and that feeds nothing
    for k in nodes:
        a = info.get(k)
        if not a or a.get('kind') != 'triggered': continue
        term = [e[1] for e in emits[k] if e[0] == 'terminal']
        if term and not edges.get(k):
            feeders = sorted({labels[s].split(':')[0].replace('cast ', '') for s in nodes if k in edges.get(s, ())})
            hk = a['hook'][0]
            fed = {'combat_damage': 'combat', 'attack': 'combat', 'upkeep': 'each turn', 'end_step': 'each turn', 'begin_combat': 'each turn',
                   'main_phase': 'each turn', 'landfall': 'land drops'}.get(hk, f'{len(feeders)} cards')
            out['linear payoffs'].append({'payoff': labels[k], 'hook': hk, 'output': ', '.join(sorted(set(term))),
                                          'fed by': fed, 'cap': 'once per turn' if a['gates'].get('once_per_turn') else ''})
    # replacement amplification and scaling
    for k in nodes:
        a = info.get(k)
        if a and a.get('kind') == 'replacement':
            fed = sorted({s[0] for s in nodes if k in edges.get(s, ())})
            out['replacement amplification'].append({'amplifier': k[0], 'adds per event': '1 extra token', 'events it sees (sources)': len(fed)})
    for c in cards:
        for a in card_record(inv, c)['abilities']:
            for o in a['outputs']:
                if o[0] == 'pump_team_x': out['scaling'].append({'card': c, 'output': f'team +X power, X = your {o[1]}'})
        for lv in card_record(inv, c)['statics'].get('station_levels', []):
            if lv['anthem']:
                out['resource-quality feedback'].append({'card': c, 'route': f'creature power -> station charge -> at {lv["at"]}+ other creatures +{lv["anthem"]}/+{lv["anthem"]} -> more power to station and attack',
                                                         'barrier': f'needs {lv["at"]} charge from tapped creatures (sorcery speed)'})
    # cycles
    for comp in _sccs(nodes, edges):
        if len(comp) == 1 and comp[0] not in edges.get(comp[0], ()): continue
        if all(n[0] == 'cast' for n in comp): continue
        if all(info.get(n, {}).get('kind') == 'station' for n in comp): continue
        caps = [labels[n] for n in comp if info.get(n, {}).get('gates', {}).get('once_per_turn')]
        costs = [labels[n] for n in comp if info.get(n, {}).get('kind') == 'activated']
        row = {'cycle': ' -> '.join(labels[n] for n in comp) + (' -> (itself)' if len(comp) == 1 else ''),
               'limit': ('once per turn: ' + '; '.join(caps)) if caps else ('costs: ' + '; '.join(costs)) if costs else 'none read'}
        out['bounded feedback' if caps or costs else 'unbounded feedback'].append(row)
    # feed-forward chains: paths of 3+ abilities that are not inside a cycle
    in_cycle = {n for comp in _sccs(nodes, edges) if len(comp) > 1 or comp[0] in edges.get(comp[0], ()) for n in comp}
    seen = set()
    def walk(path):
        last = path[-1]
        nxt = [b for b in edges.get(last, ()) if b not in path and b[0] != 'cast' and info.get(b, {}).get('kind') != 'station']
        if not nxt and len(path) >= 3:
            key = tuple(path)
            if key not in seen: seen.add(key); out['feed-forward chains'].append({'chain': ' -> '.join(labels[p] for p in path)})
        for b in nxt[:6]:
            if len(path) < 5: walk(path + [b])
    for k in nodes:
        if k[0] == 'cast' or k in in_cycle: continue
        if info.get(k, {}).get('kind') == 'triggered' and any(k in edges.get(s, ()) for s in nodes): continue
        if any(e[0] != 'terminal' for e in emits[k]): walk([k])
    out['feed-forward chains'] = out['feed-forward chains'][:12]
    return out
