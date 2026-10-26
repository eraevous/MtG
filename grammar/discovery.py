"""Collection discovery over the ability contracts, without the simulator.

Each ability contract is read into a functional summary:

  produces   events its result or its paid cost makes happen (hook + the object's qualifiers + certainty),
             widened one step through DIO §4.3 implications (token.create -> battlefield.enter, ...)
  observes   the alternatives of its trigger requirement group
  needs      what would let the operation happen again: its trigger events, plus whatever replenishes a cost
             component ({T} needs an untap, "sacrifice a creature" needs a creature to arrive, a counter cost
             needs counters put on it ...)

A flow edge A -> B means something A produces satisfies something B observes, with every material qualifier
compatible (§4.1: similar nouns do not establish compatibility). A loop is A -> B where B's output also satisfies
one of A's needs: Kate's query "which cards produce an event another card observes, where the second card's output
enables the first card's operation to happen again".

    python3 -I discovery.py grammar_layer.sqlite --out discovery/        # writes flow_edge + loops tables and CSVs

Everything is a candidate read from proposed (unreviewed) templates unless the contract says template_reviewed.
"""
import argparse
import csv
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantics as sm  # noqa: E402

COST_NEEDS = {
    'cost.tap_self': ('permanent.untap', {'self': True}),
    'cost.untap_self': ('permanent.tap', {'self': True}),
    'cost.counter_remove': ('counter.put', {'self': True}),
    'cost.sacrifice_other': ('battlefield.enter', None),
    'cost.tap_other': ('battlefield.enter', None),
    'cost.discard': ('card.draw', None),
    # mana is a generic resource: every mana producer would "enable" every mana cost, so it is not a loop
    'cost.energy': ('energy.gain', None),
}


def obj_of(h, order=('object', 'subject', 'on', 'to')):
    args = h.get('args', {})
    for k in order:
        a = args.get(k)
        if a and a.get('slot') and (a['slot'].startswith('obj.') or a['slot'] in ('self', 'ref')):
            return a
    return None


def full_q(h, order=('object', 'subject', 'on', 'to')):
    """Object qualifiers plus the event qualifiers that decide compatibility: counter kind, destination and
    source zone."""
    o = obj_of(h, order)
    q = dict((o or {}).get('q', {}))
    args = h.get('args', {})
    for k, a in args.items():
        if not a or not a.get('slot'):
            continue
        if a['slot'] == 'counter':
            q['counter_kind'] = a['q'].get('counter_kind')
        elif a['slot'] == 'zone' and k.split('_')[0] in ('into', 'onto', 'to'):
            q['destination'] = a['q'].get('zone')
        elif a['slot'] == 'zone' and k.split('_')[0] == 'from':
            q['source_zone'] = a['q'].get('zone')
    if h.get('concept') == 'ev.saga.chapter':
        q.update({'self': True, 'counter_kind': 'lore'})
    return o, q


def actor_of(h):
    a = h.get('args', {}).get('actor') or h.get('args', {}).get('player')
    return (a or {}).get('q', {})


def self_qualifiers(type_line, con):
    """What "this" is: the card's own types, or the host's when the ability is granted to a token or object."""
    host = con.get('source_unit', {}).get('granted')
    if host and host.get('q'):
        return {k: v for k, v in host['q'].items() if k in ('card_type', 'subtype', 'token', 'color')}
    front = (type_line or '').split(' // ')[0].lower()
    q = sm.object_qualifiers('obj.q', 'a ' + front.replace('—', ' '))
    return {k: v for k, v in q.items() if k in ('card_type', 'subtype')}


def fill_self(q, sq):
    if q.get('self'):
        for k, v in sq.items():
            q.setdefault(k, v)
    return q


def summarize(con, sq=None):
    sq = sq or {}
    prod, obs, needs = [], [], []
    res = con.get('result', {})
    for rel in ('produces', 'transforms'):
        for h in res.get(rel, []):
            if not h.get('hook'):
                continue
            o, q = full_q(h)
            if h.get('concept') == 'op.token.create':
                q.setdefault('controller', 'you')
                q['token'] = True
            cert = h.get('certainty', 'guaranteed')
            prod.append({'hook': h['hook'], 'q': q, 'certainty': cert, 'act_time': h.get('act_time'),
                         'concept': h.get('concept'), 'actor': actor_of(h), 'value': (o or {}).get('value')})
    for g in con.get('initiation', {}).get('requirement_groups', []):
        if g['class'] == 'trigger':
            for a in g['alternatives']:
                s, q = full_q(a, ('subject', 'on', 'object', 'to'))
                obs.append({'hook': a.get('hook'), 'q': q, 'actor': actor_of(a), 'value': (s or {}).get('value'),
                            'concept': a.get('concept')})
                needs.append({'hook': a.get('hook'), 'q': q, 'why': 'trigger', 'actor': actor_of(a)})
        elif g['class'] == 'cost':
            if g.get('hook') and g.get('concept') not in ('cost.mana',):
                o, q = full_q(g)
                if g.get('concept') in ('cost.tap_self', 'cost.sacrifice_self'):
                    q = {'self': True}
                prod.append({'hook': g['hook'], 'q': q, 'certainty': 'optional', 'act_time': 'paid_as_cost',
                             'concept': g.get('concept'), 'actor': {'player': 'you'}, 'value': (o or {}).get('value')})
            o_ = obj_of(g)
            if o_ and o_.get('slot') == 'self' and g.get('concept') in ('cost.discard', 'cost.exile', 'cost.return_to_hand'):
                # "discard this card", "exile this card from your graveyard": only this card coming back helps
                needs.append({'hook': 'card.return_to_hand' if g['concept'] == 'cost.discard' else 'zone.enter',
                              'q': {'self': True}, 'why': 'cost:' + g['concept'] + ':self'})
            elif g.get('concept') in COST_NEEDS:
                hook, q = COST_NEEDS[g['concept']]
                if q is None:
                    o = obj_of(g)
                    q = {k: v for k, v in ((o or {}).get('q', {})).items() if k in ('card_type', 'subtype', 'token', 'controller')}
                needs.append({'hook': hook, 'q': q, 'why': 'cost:' + g['concept']})
    # "when this artifact enters and when you sacrifice it": 'it' is this object
    for g in con.get('initiation', {}).get('requirement_groups', []):
        if g['class'] == 'trigger' and any((a.get('args', {}).get('subject') or {}).get('slot') == 'self' for a in g['alternatives']):
            for x in obs + needs:
                if x['q'].get('reference') == 'antecedent':
                    x['q']['self'] = True
            for a in g['alternatives']:
                if re.search(r'\b(?:first|second|third|next)\b', a.get('text', '') or ''):
                    pass
    ordinal = any(re.search(r'\b(?:first|second|third)\b .*\beach turn', t.get('text', '') or '')
                  for g in con.get('initiation', {}).get('requirement_groups', []) if g['class'] == 'trigger'
                  for t in g['alternatives'])
    for x in obs:
        if ordinal:
            x['ordinal'] = True
    for x in prod + obs + needs:
        fill_self(x['q'], sq)
    gated = [g for g in con.get('initiation', {}).get('requirement_groups', []) if g['class'] in ('state', 'history')]
    if gated:
        for p in prod:
            if p['certainty'] == 'guaranteed':
                p['certainty'] = 'conditional'
                p['condition'] = 'intervening or resolution condition: ' + gated[0].get('text', '')
    # one implication step (DIO §4.3); a conditional implication keeps its condition
    for p in list(prod):
        for hook, cert, cond in sm.IMPLIES.get(p['hook'], []):
            if p['hook'] == 'permanent.sacrifice' and hook == 'permanent.dies' and 'creature' not in p['q'].get('card_type', ['creature']):
                continue
            prod.append({**p, 'hook': hook, 'certainty': 'conditional' if cert == 'conditional' else p['certainty'],
                         'via': p['hook'], 'condition': cond})
    return prod, obs, needs


def compatible(p, o, same_card):
    """(ok, certainty, reason). p: produced, o: observed or needed."""
    if not o.get('hook') or p['hook'] != o['hook']:
        return False, None, 'hook'
    pq, oq = p['q'], o['q']
    if oq.get('self') and not same_card:
        # "when this creature dies" is satisfied by another card's act only if that act can pick this creature
        if pq.get('self') or pq.get('reference') or pq.get('token'):
            return False, None, 'self-subject'
        cert = 'possible'
    else:
        cert = 'guaranteed'
    if oq.get('self') and same_card:
        return False, None, 'same card'
    if pq.get('self') and not same_card and oq.get('exclude_self') is None:
        pass
    pt, ot = set(pq.get('card_type', [])), set(oq.get('card_type', []))
    if oq.get('type_logic') == 'any_of' or pq.get('type_logic') == 'any_of':
        # "creature or Vehicle": compare the union of card types and subtypes
        pu, ou = pt | set(pq.get('subtype', [])), ot | set(oq.get('subtype', []))
        if pu and ou and not (pu & ou):
            return False, None, 'card_type'
        ot = pt = set()
    if ot and pt and not (ot & pt):
        return False, None, 'card_type'
    if ot and not pt and not pq.get('self'):
        cert = 'possible'
    if set(oq.get('card_type_not', [])) & pt:
        return False, None, 'card_type_not'
    if oq.get('type_logic') != 'any_of' and oq.get('subtype') and pq.get('subtype') and not set(oq['subtype']) & set(pq['subtype']):
        return False, None, 'subtype'
    if oq.get('token') is not None and pq.get('token') is not None and oq['token'] != pq['token']:
        return False, None, 'token'
    for k in ('counter_kind', 'destination'):
        if oq.get(k) and pq.get(k) and oq[k] != pq[k]:
            return False, None, k
    if oq.get('counter_kind') and not pq.get('counter_kind') and p['hook'] == 'counter.put':
        cert = 'possible'
    oc, pc = oq.get('controller'), pq.get('controller')
    if oc and pc and oc != pc and not (oc == 'not_you' and pc == 'opponent') and pc != 'referenced_player':
        return False, None, 'controller'
    if oc == 'opponent' and p['act_time'] == 'paid_as_cost':
        return False, None, 'controller'
    oa, pa = (o.get('actor') or {}).get('player'), (p.get('actor') or {}).get('player')
    if oa and pa and oa != pa and oa != 'any_player' and pa != 'any_player':
        return False, None, 'actor'
    order = ('guaranteed', 'optional', 'conditional', 'possible')
    if order.index(p['certainty']) > order.index(cert):
        cert = p['certainty']         # a produced event is never surer than its producer ("possible" when partly read)
    if o.get('unread_parts'):
        cert = 'possible'
    if o.get('ordinal') and cert in ('guaranteed', 'optional'):
        cert = 'conditional'          # "your second card each turn" holds only for one of the events
    return True, cert, ''


def run(dbpath, outdir):
    db = sqlite3.connect(dbpath)
    rows = db.execute('''SELECT ac.ability_id, c.name, ac.contract_json, ac.completeness, c.type_line FROM ability_contract ac
                         JOIN card c USING(oracle_id) WHERE c.in_collection = 1''').fetchall()
    S = {}
    cap = {}
    oneshot = {}
    for aid, name, cj, comp, tl in rows:
        con = json.loads(cj)
        p, o, n = summarize(con, self_qualifiers(tl, con))
        if comp != 'complete':
            for x in p:
                x['certainty'] = 'possible'
            for x in o:
                x['unread_parts'] = True
        S[aid] = (name, p, o, n, comp, con['evidence']['oracle_text'])
        oneshot[aid] = con.get('kind') == 'cast'
        cap[aid] = any(t['concept'].startswith('cap.') for t in con.get('initiation', {}).get('timing', {}).get('terms', []))
    by_hook_obs = defaultdict(list)
    for aid, (name, p, o, n, comp, txt) in S.items():
        for x in o:
            by_hook_obs[x['hook']].append((aid, x))
    edges = []
    for a, (na, pa, _, _, ca, _) in S.items():
        for p in pa:
            for b, o in by_hook_obs.get(p['hook'], []):
                nb = S[b][0]
                if a == b:
                    continue
                ok, cert, _ = compatible(p, o, na == nb)
                if ok and na != nb:
                    edges.append((a, b, p['hook'], cert, p.get('via'), p.get('value'), o.get('value')))
    db.executescript('''DROP TABLE IF EXISTS flow_edge; CREATE TABLE flow_edge(src_ability INT, dst_ability INT, hook TEXT,
                        certainty TEXT, via TEXT, produced TEXT, observed TEXT);
                        DROP TABLE IF EXISTS loop2; CREATE TABLE loop2(a_ability INT, b_ability INT, a_card TEXT, b_card TEXT,
                        forward_hook TEXT, back_hook TEXT, back_need TEXT, certainty TEXT, both_complete INT, capacity_limited INT);''')
    db.executemany('INSERT INTO flow_edge VALUES(?,?,?,?,?,?,?)', edges)
    fwd = defaultdict(list)
    for a, b, hook, cert, via, pv, ov in edges:
        fwd[(a, b)].append((hook, cert))
    rank = {'guaranteed': 0, 'optional': 1, 'conditional': 2, 'possible': 3}
    loops = []
    for (a, b), hs in fwd.items():
        if oneshot[a]:
            continue                  # a spell resolves once; its card leaves the stack, so it cannot close a loop
        na, pa, oa, need_a, ca, ta = S[a]
        nb, pb, ob, nbn, cb, tb = S[b]
        best = None
        for p in pb:
            for nd in need_a:
                ok, cert, _ = compatible(p, nd, False)
                if ok:
                    c2 = max([min(hs, key=lambda h: rank[h[1]])[1], cert], key=lambda c: rank[c])
                    cand = (rank[c2], p['hook'], nd['why'], c2)
                    if not best or cand < best:
                        best = cand
        if best:
            h = min(hs, key=lambda h: rank[h[1]])
            loops.append((a, b, na, nb, h[0], best[1], best[2], best[3], int(ca == 'complete' and cb == 'complete'), int(cap[a] or cap[b])))
    db.executemany('INSERT INTO loop2 VALUES(?,?,?,?,?,?,?,?,?,?)', loops)
    db.commit()
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'collection_loops.csv')
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['certainty', 'card_A', 'A_ability', 'A_produces', 'card_B', 'B_ability', 'B_output', 'enables_A_via',
                    'both_fully_parsed', 'capacity_limited'])
        for a, b, na, nb, fh_, bh, need, cert, both, capl in sorted(loops, key=lambda r: (rank[r[7]], -r[8], r[2], r[3])):
            w.writerow([cert, na, S[a][5], fh_, nb, S[b][5], bh, need, both, capl])
    summary = {
        'abilities': len(S), 'flow_edges': len(edges),
        'flow_edges_by_certainty': {k: sum(1 for e in edges if e[3] == k) for k in rank},
        'loops': len(loops), 'loops_by_certainty': {k: sum(1 for l in loops if l[7] == k) for k in rank},
        'loop_card_pairs': len({tuple(sorted((l[2], l[3]))) for l in loops}),
        'loops_both_fully_parsed': sum(l[8] for l in loops),
    }
    with open(os.path.join(outdir, 'discovery_summary.json'), 'w') as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1))
    return summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('db')
    ap.add_argument('--out', default='discovery')
    a = ap.parse_args()
    run(a.db, a.out)
