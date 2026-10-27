"""The six read-only verbs. Each returns a dict that the CLI wraps in the common envelope.

Card meaning comes only from the KB (contracts, Oracle rules text) and the grammar layer's loop discovery (P-01).
Nothing here parses card text. Interaction links are candidates unless both contracts are semantically reviewed (P-03),
and exploration output is never a ranking of card quality (P-04).
"""
import csv
import json
from pathlib import Path

from . import kb
from .claims import claim, REVIEWED_STATES

ROOT = Path(__file__).resolve().parent.parent
LINK_LIMITS = ['Links match an effect to a trigger hook only. Qualifiers such as whose permanent, which type or how many are not '
               'checked, so a link is a lead to read, not a working interaction.',
               'Contracts cover parsed abilities only; keyword-only and unparsed abilities produce no links, so absence proves nothing.']
LOOPS_CSV = ROOT / 'grammar' / 'discovery' / 'collection_loops.csv'
CHARTERS = ROOT / 'decks' / 'charters'
CERTAINTY_ORDER = {'guaranteed': 0, 'optional': 1, 'conditional': 2, 'possible': 3}


# ---------- shared lookups ----------

def _card_row(c, name):
    row = c.execute('select * from cards where card_name=?', (name,)).fetchone()
    if row:
        return row
    hits = [r[0] for r in c.execute('select card_name from cards where lower(card_name) like ? order by card_name limit 8',
                                    (name.lower() + '%',))]
    if len(hits) == 1:
        return c.execute('select * from cards where card_name=?', (hits[0],)).fetchone()
    raise LookupError(f'card not found: {name!r}' + (f'; did you mean one of {hits}' if hits else ''))


def _contracts(c, names=None):
    """Current contracts with their review state and query index, optionally for a set of card names."""
    out = []
    for r in c.execute('select k.contract_id,k.card_name,k.exact_text,k.operation_kind,k.contract_json,q.queue_state '
                       'from current_contracts k join validation_queue q using(contract_id,contract_version)'):
        if names is not None and r['card_name'] not in names:
            continue
        qi = json.loads(r['contract_json']).get('query_index') or {}
        out.append({'contract_id': r['contract_id'], 'card': r['card_name'], 'text': r['exact_text'], 'kind': r['operation_kind'],
                    'state': r['queue_state'], 'feeds': qi.get('feeds') or [], 'hooks': qi.get('hook_ids') or [],
                    'hook_subject': qi.get('hook_subject')})
    return out


def _link_state(p, o):
    return 'semantic_reviewed' if p['state'] in REVIEWED_STATES and o['state'] in REVIEWED_STATES else 'candidate'


def _links(contracts, only=None):
    """Producer -> observer candidate links through a shared hook (the KB's FEEDS table). `only` keeps links touching those cards."""
    observers = {}
    for k in contracts:
        if k['hook_subject'] == 'self':
            continue
        for h in k['hooks']:
            observers.setdefault(h, []).append(k)
    seen, out = set(), []
    for p in contracts:
        for eff in p['feeds']:
            for hook in kb.FEEDS.get(eff, []):
                for o in observers.get(hook, []):
                    if o['card'] == p['card']:
                        continue
                    if only is not None and p['card'] not in only and o['card'] not in only:
                        continue
                    key = (p['card'], eff, o['card'], hook)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({'producer': p['card'], 'produces': eff, 'observer': o['card'], 'hook': hook,
                                'producer_contract': p['contract_id'], 'observer_contract': o['contract_id'],
                                'producer_state': p['state'], 'observer_state': o['state'], 'link_state': _link_state(p, o)})
    return out


def _loops(pool, only=None):
    """Loop candidates from the grammar layer's collection discovery, restricted to a card pool."""
    if not LOOPS_CSV.exists():
        return []
    out, seen = [], set()
    with open(LOOPS_CSV, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            a, b = r['card_A'], r['card_B']
            if a not in pool or b not in pool:
                continue
            if only is not None and a not in only and b not in only:
                continue
            key = (frozenset((a, b)), r['certainty'])   # a loop is listed once from each side
            if key in seen:
                continue
            seen.add(key)
            out.append({'cards': [a, b], 'certainty': r['certainty'], 'a_produces': r['A_produces'], 'b_output': r['B_output'],
                        'enables_a_via': r['enables_A_via'], 'both_fully_parsed': r['both_fully_parsed'] == '1',
                        'capacity_limited': r['capacity_limited'] == '1'})
    out.sort(key=lambda x: (CERTAINTY_ORDER.get(x['certainty'], 9), not x['both_fully_parsed'], x['cards']))
    return out


def _pool(c, ci=None, deck=None, free=False):
    if deck:
        names = set(kb.deck_cards(c, deck))
        if not names:
            raise LookupError(f'deck not found: {deck!r}; decks: {kb.decks(c)}')
        return names
    out = set()
    for r in c.execute('select * from cards where owned_min>0'):
        if free and r['free'] <= 0:
            continue
        if ci is not None and not kb.legal_rules(c, r, ci)[0]:
            continue
        out.add(r['card_name'])
    return out


def _charter(deck):
    p = CHARTERS / f'{deck}.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


# ---------- verbs ----------

def context(c, deck=None):
    if not deck:
        decks = []
        for d in kb.decks(c):
            cmd = [r[0] for r in c.execute("select card_name from deck_allocations where deck=? and section='Commander' and counts_in_deck_100=1", (d,))]
            decks.append({'deck': d, 'commanders': cmd, 'color_identity': kb.deck_ci(c, d), 'distinct_names': len(kb.deck_cards(c, d)),
                          'charter': (CHARTERS / f'{d}.json').exists()})
        tot = c.execute('select count(*),sum(owned_min),sum(free>0) from cards where owned_min>0').fetchone()
        claims = [claim(f'The collection snapshot holds {tot[1]} copies of {tot[0]} owned card names; {tot[2]} names have a free copy.',
                        'inventory', 'collection_snapshot')]
        return {'collection': {'owned_names': tot[0], 'copies': tot[1], 'names_with_free_copy': tot[2]}, 'decks': decks}, claims
    cards = kb.deck_cards(c, deck)
    if not cards:
        raise LookupError(f'deck not found: {deck!r}; decks: {kb.decks(c)}')
    ov = kb.overlap(c, deck)
    ch = _charter(deck)
    size = c.execute('select sum(quantity) from deck_allocations where deck=? and counts_in_deck_100=1', (deck,)).fetchone()[0]
    claims = [claim(f'{deck} counts {size} cards toward its 100 ({len(cards)} distinct names) in the snapshot.', 'inventory', 'collection_snapshot')]
    claims.append(claim(f'{deck} has a deck charter recording preferences and constraints.' if ch else
                        f'{deck} has no deck charter yet, so preferences and constraints are unknown to the tools.',
                        'preference', 'deck_charter' if ch else 'none'))
    return {'deck': deck, 'color_identity': kb.deck_ci(c, deck), 'cards': cards, 'charter': ch,
            'roles': {'evidence': ov['evidence'], 'role_counts': ov['role_counts'], 'single_source_roles': ov['single_source_roles']}}, claims


def card(c, name):
    row = _card_row(c, name)
    name = row['card_name']
    d = kb.card(c, name)
    dest = kb.destinations(c, name)
    rt = d.get('rules_text') or {}
    oracle = rt.get('authority') == 'oracle_refresh' and bool(rt.get('identity_confirmed'))
    claims = [claim('Rules text: ' + (d['card']['oracle_text'] or ''), 'rules_text', 'oracle' if oracle else 'sheet_text',
                    evidence=[f"rules_text.authority={rt.get('authority')}", f"oracle_run_id={rt.get('oracle_run_id')}"]),
              claim(f"Owned {d['custody']['owned']}, free {d['custody']['free']}, assigned {d['custody']['assigned']}.",
                    'inventory', 'collection_snapshot')]
    for k in d['contracts']:
        claims.append(claim(f"Contract reading of: {k['exact_text']}", 'mechanics', k['queue_state'],
                            evidence=[k['contract_id']] + k['failed_checks']))
    data = {'card': d['card'], 'custody': d['custody'], 'held_by': dest['held_by'],
            'legal_in_decks': [x['deck'] for x in dest['destinations'] if x['legal']],
            'contracts': [{k: x[k] for k in ('contract_id', 'operation_kind', 'queue_state', 'exact_text', 'failed_checks')} for x in d['contracts']],
            'reconciliation': d['reconciliation']}
    return data, claims


def explore(c, seed=None, ci=None, deck=None, free=False, mode='focused', limit=25):
    """Candidate interactions in a pool. Focused: links and loops touching the seed. Divergent: what the seed's own hooks
    and effects don't already cover, so the tools surface relationships nobody asked about."""
    seed_card, seed_theme = None, None
    if seed:
        if seed in kb.THEMES:
            seed_theme = seed
        else:
            seed_card = _card_row(c, seed)['card_name']
    if ci is None and seed_card and not deck:
        ci = ''.join(x for x in kb.COLORS if x in (_card_row(c, seed_card)['color_identity'] or ''))
    if ci is None and not deck:
        raise ValueError('explore needs a seed card, --ci or --deck to define the card pool')
    pool = _pool(c, ci, deck, free)
    if seed_card:
        pool.add(seed_card)
    ks = _contracts(c, pool)
    if seed_theme:
        focus = {r['card_name'] for r in kb.theme(c, seed_theme) if r['card_name'] in pool}
    elif seed_card:
        focus = {seed_card}
    else:
        focus = None
    if mode == 'focused' and focus is None:
        mode = 'divergent'
    claims, data = [], {'pool': {'source': f'deck {deck}' if deck else ('free copies' if free else 'owned cards'),
                                 'color_identity': ci, 'cards': len(pool), 'contracts': len(ks)},
                        'seed': seed_card or seed_theme, 'mode': mode,
                        'pool_contract_states': _count(ks, 'state'), 'limitations': LINK_LIMITS}
    if mode == 'focused':
        links = _links(ks, only=focus)
        loops = _loops(pool, only=focus)
        disc = 'requested'
    elif focus:
        # second order: chains seed -> X -> Y where the second step uses a pathway the seed itself does not,
        # scored so that narrow pathways (few cards in the pool share them) come first
        first = _links(ks, only=focus)
        seed_paths = _count_paths(first)
        out_of = {}
        for l in first:
            if l['producer'] in focus and l['observer'] not in focus:   # a chain runs forward from the seed
                out_of.setdefault(l['observer'], []).append(l)
        second = [l for l in _links(ks, only=set(out_of)) if l['producer'] in out_of and l['observer'] not in focus
                  and _pathway(l) not in seed_paths]
        pool_paths = _count_paths(second)
        chains = []
        for l2 in second:
            for l1 in out_of[l2['producer']]:
                score = 1.0 / (seed_paths[_pathway(l1)] * pool_paths[_pathway(l2)])
                chains.append({'score': round(score, 6), 'first': l1, 'second': l2,
                               'link_state': 'semantic_reviewed' if l1['link_state'] == l2['link_state'] == 'semantic_reviewed' else 'candidate'})
        chains.sort(key=lambda ch: (-ch['score'], ch['first']['producer'], ch['second']['observer']))
        seen, top = set(), []
        for ch in chains:
            k = (ch['first']['hook'], _pathway(ch['second']))
            if k in seen:
                continue                     # one example per pathway pair keeps the answer varied
            seen.add(k)
            top.append(ch)
        data['first_order_links'] = len(first)
        data['chains_total'] = len(chains)
        data['chains'] = top[:limit]
        loops = [l for l in _loops(pool, only=set(out_of)) if not set(l['cards']) & focus]
        data['loops_total'] = len(loops)
        data['loops'] = loops[:limit]
        for ch in data['chains']:
            a, b = ch['first'], ch['second']
            claims.append(claim(f"{a['producer']} ({a['produces']}) -> {a['observer']} via {a['hook']}, then "
                                f"{b['producer']} ({b['produces']}) -> {b['observer']} via {b['hook']}.", 'mechanics', ch['link_state'],
                                evidence=[a['producer_contract'], a['observer_contract'], b['producer_contract'], b['observer_contract']],
                                discovery='unrequested'))
        for l in data['loops']:
            claims.append(claim(f"{l['cards'][0]} and {l['cards'][1]} may form a loop ({l['certainty']}), next to the seed's neighbours.",
                                'mechanics', 'candidate', evidence=['grammar/discovery/collection_loops.csv'], discovery='unrequested'))
        return data, claims
    else:
        links, loops, disc = _links(ks), _loops(pool), 'unrequested'
    data['links_total'] = len(links)
    data['links_by_pathway'] = {f'{k[0]} -> {k[1]}': n for k, n in sorted(_count_paths(links).items(), key=lambda x: -x[1])[:20]}
    data['links'] = _spread(links, limit)
    data['loops_total'] = len(loops)
    data['loops'] = loops[:limit]
    data['hooks_by_link_count'] = dict(sorted(_count(links, 'hook').items(), key=lambda x: -x[1])[:15])
    for l in data['links']:
        claims.append(claim(f"{l['producer']} ({l['produces']}) can feed {l['observer']} via {l['hook']}.", 'mechanics',
                            l['link_state'], evidence=[l['producer_contract'], l['observer_contract']], discovery=disc))
    for l in data['loops']:
        claims.append(claim(f"{l['cards'][0]} and {l['cards'][1]} may form a loop ({l['certainty']}).", 'mechanics', 'candidate',
                            evidence=['grammar/discovery/collection_loops.csv'], discovery=disc))
    return data, claims


def _pathway(l):
    return (l['produces'], l['hook'])


def _count_paths(links):
    out = {}
    for l in links:
        out[_pathway(l)] = out.get(_pathway(l), 0) + 1
    return out


def _spread(links, limit):
    """Pick links round-robin across pathways (effect -> hook), reviewed first, so one crowded pathway can't fill the answer."""
    groups = {}
    for l in sorted(links, key=lambda l: (l['link_state'] != 'semantic_reviewed', l['producer'], l['observer'])):
        groups.setdefault(_pathway(l), []).append(l)
    order = sorted(groups, key=lambda k: len(groups[k]))      # rarer pathways first: they are the less obvious ones
    out, i = [], 0
    while len(out) < limit and any(i < len(groups[k]) for k in order):
        for k in order:
            if i < len(groups[k]) and len(out) < limit:
                out.append(groups[k][i])
        i += 1
    return out


def _count(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def hypothesis(c, a, b, effect=None, ci=None):
    """What would have to hold for A and B to interact, which links are unverified, and what could disconfirm it."""
    a, b = _card_row(c, a)['card_name'], _card_row(c, b)['card_name']
    ks = _contracts(c, {a, b})
    links = _links(ks, only={a, b})
    links = [l for l in links if {l['producer'], l['observer']} == {a, b}]
    if effect:
        links = [l for l in links if effect in (l['produces'], l['hook'])]
    loops = [l for l in _loops({a, b}) if set(l['cards']) == {a, b}]
    disconfirming = []
    by_id = {k['contract_id']: k for k in ks}
    for cid in {x for l in links for x in (l['producer_contract'], l['observer_contract'])}:
        for r in c.execute("select check_id,detail from validation_checks where contract_id=? and result='fail'", (cid,)):
            disconfirming.append(f"{cid}: failed check {r['check_id']}: {r['detail']}")
    for n in (a, b):
        row = _card_row(c, n)
        if (row['owned_min'] or 0) <= 0:
            disconfirming.append(f'{n} is not owned in this collection snapshot.')
        if ci is not None:
            ok, why = kb.legal_rules(c, row, ci)
            if not ok:
                disconfirming.append(f'{n}: {why}.')
        rec = c.execute('select category,decision,quarantine_contracts from effective_reconciliation where card_name=?', (n,)).fetchone()
        if rec:
            disconfirming.append(f"{n}: Oracle reconciliation {rec['category']} / {rec['decision']}.")
    claims = []
    for l in links:
        claims.append(claim(f"{l['producer']} ({l['produces']}) can feed {l['observer']} via {l['hook']}.", 'mechanics', l['link_state'],
                            evidence=[l['producer_contract'], l['observer_contract']]))
    for l in loops:
        claims.append(claim(f"{a} and {b} may form a loop ({l['certainty']}).", 'mechanics', 'candidate',
                            evidence=['grammar/discovery/collection_loops.csv']))
    if not links and not loops:
        claims.append(claim(f'No contract link or loop candidate connects {a} and {b}' + (f' through {effect}' if effect else '') + '.',
                            'mechanics', 'candidate',
                            evidence=['absence in the KB is not proof of absence: contracts cover parsed abilities only']))
    unverified = sorted({x for l in links for x, s in ((l['producer_contract'], l['producer_state']), (l['observer_contract'], l['observer_state']))
                         if s not in REVIEWED_STATES})
    data = {'cards': [a, b], 'effect': effect, 'links': links, 'loops': loops,
            'conditions': [{'contract_id': k['contract_id'], 'card': k['card'], 'text': k['text'], 'state': k['state']}
                           for k in ks if k['contract_id'] in {x for l in links for x in (l['producer_contract'], l['observer_contract'])}],
            'unverified_contracts': unverified, 'disconfirming_evidence': disconfirming, 'limitations': LINK_LIMITS,
            'would_settle_it': ['semantic review of each unverified contract (kb/review.py, citing passing scenarios)',
                                'a rules check of the trigger and replacement wording against the Comprehensive Rules']
            if unverified else []}
    return data, claims


def compare(deck, swaps, workbook, engine_games=0):
    """Descriptive deltas from the evaluator. Always exploratory: the evaluator types few cards per deck and is unvalidated."""
    import sys
    sys.path.insert(0, str(ROOT / 'kb' / 'vendor'))
    from mtg_eval.api import Evaluator
    from mtg_eval import report
    ev = Evaluator(str(workbook), engine_games=engine_games)
    res = json.loads(report.to_json(ev.compare(deck, [tuple((x.split('=', 1) + [''])[:2]) for x in swaps])))
    claims = [claim(f'Evaluator profile change for {deck} with swaps {swaps}; descriptive only.', 'performance', 'evaluator_model',
                    evidence=['kb/vendor/mtg_eval compare', f'workbook {Path(workbook).name}'])]
    return {'deck': deck, 'swaps': swaps, 'evaluator': res,
            'limitations': ['The evaluator fully types a median of about 10 of 60-65 nonland cards per deck.',
                            'It does not reproduce the observed Vraska closing failure.',
                            'Count thresholds were set after the fact; read deltas as direction, not size.']}, claims


def check(c, items):
    """Per-claim support: what each claim in a draft answer rests on, and what is still missing."""
    out = []
    for it in items:
        kind, names = it.get('kind'), it.get('cards') or []
        missing, evidence, support = [], [], 'none'
        rows = []
        for n in names:
            try:
                rows.append(_card_row(c, n))
            except LookupError as e:
                missing.append(str(e))
        if kind == 'inventory':
            support = 'collection_snapshot' if rows and not missing else 'none'
            evidence = [f"{r['card_name']}: owned {r['owned_min']}, free {r['free']}" for r in rows]
        elif kind == 'rules_text':
            ok = True
            for r in rows:
                rt = c.execute('select authority,identity_confirmed from rules_text where card_name=?', (r['card_name'],)).fetchone()
                good = bool(rt) and rt['authority'] == 'oracle_refresh' and bool(rt['identity_confirmed'])
                ok &= good
                evidence.append(f"{r['card_name']}: rules text authority {rt['authority'] if rt else 'none'}")
            support = 'oracle' if rows and ok and not missing else 'sheet_text'
        elif kind == 'mechanics':
            ks = _contracts(c, {r['card_name'] for r in rows})
            states = {k['state'] for k in ks}
            unrev = [k['contract_id'] for k in ks if k['state'] not in REVIEWED_STATES]
            support = 'semantic_reviewed' if ks and not unrev and not missing else ('candidate' if ks else 'none')
            evidence = [f"{k['contract_id']}: {k['state']}" for k in ks]
            if unrev:
                missing.append(f'{len(unrev)} contract(s) not semantically reviewed')
            if not ks:
                missing.append('no contracts for these cards')
            states = sorted(states)
        elif kind == 'performance':
            support = 'evaluator_model'
            missing.append('observed games or a frozen prediction scored against later games')
        elif kind == 'preference':
            ch = _charter(it['deck']) if it.get('deck') else None
            support = 'deck_charter' if ch else 'none'
            if not ch:
                missing.append('a deck charter recording the person\'s preferences')
        else:
            raise ValueError(f'claim kind must be one of inventory, rules_text, mechanics, performance, preference; got {kind!r}')
        out.append(claim(it.get('text', ''), kind, support, evidence=evidence, missing=missing))
    return {'checked': len(out)}, out
