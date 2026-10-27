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
LINK_LIMITS = ['Links match an effect to a trigger hook, then test the qualifiers the contracts record (object type filters, '
               '"this enters" subjects, target types). A link that contradicts a recorded qualifier is rejected; one whose qualifier '
               'is not recorded (counter type, controller, token characteristics, which face) stays unresolved, never matched.',
               'Contracts cover parsed abilities only; keyword-only and unparsed abilities produce no links, so absence proves nothing.']
LOOPS_CSV = ROOT / 'grammar' / 'discovery' / 'collection_loops.csv'
CHARTERS = ROOT / 'decks' / 'charters'
POLICY = ROOT / 'decks' / 'collection_policy.json'
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
    for r in c.execute('select k.contract_id,k.card_name,k.exact_text,k.operation_kind,k.contract_json,q.queue_state,cd.type_line '
                       'from current_contracts k join validation_queue q using(contract_id,contract_version) '
                       'left join cards cd using(card_name)'):
        if names is not None and r['card_name'] not in names:
            continue
        j = json.loads(r['contract_json'])
        qi = j.get('query_index') or {}
        triggers, targets = {}, []
        for g in (j.get('initiation') or {}).get('requirement_groups') or []:
            for alt in g.get('alternatives') or []:
                if g.get('class') == 'trigger' and alt.get('id'):
                    phrase = (alt.get('text') or '').lower()
                    triggers[alt['id']] = {'filter': (alt.get('qualifiers') or {}).get('object_filter'),
                                           'self': alt.get('subject') == 'this' or phrase.startswith(('this ', '~ ')),
                                           'parsed': bool(alt.get('qualifiers'))}
                elif g.get('class') == 'eligibility' and 'target' in (alt.get('text') or ''):
                    targets.append(alt['text'])
        out.append({'contract_id': r['contract_id'], 'card': r['card_name'], 'text': r['exact_text'], 'kind': r['operation_kind'],
                    'state': r['queue_state'], 'feeds': qi.get('feeds') or [], 'hooks': qi.get('hook_ids') or [],
                    'hook_subject': qi.get('hook_subject'), 'triggers': triggers, 'targets': targets,
                    'faces': [f.strip().lower() for f in (r['type_line'] or '').split('//')]})
    return out


def _link_state(p, o):
    return 'semantic_reviewed' if p['state'] in REVIEWED_STATES and o['state'] in REVIEWED_STATES else 'candidate'


# hooks that name the entering object's type themselves
HOOK_TYPE = {'land.enters_battlefield': 'land', 'creature.enters_battlefield': 'creature', 'artifact.enters_battlefield': 'artifact'}
ENTER_EFFECTS = {'token.create', 'card.return_to_battlefield', 'land_to_battlefield'}
QUAL_RANK = {'compatible': 0, 'unresolved': 1, 'incompatible': 2}
REENTRY_EFFECTS = {'token.create', 'card.return_to_battlefield'}   # can put a copy of, or return, a targeted object
# pathways that carry each theme; a theme seed lists links on these first
THEME_PATHS = {'self_mill': {'card.mill', 'graveyard.enter'}, 'dredge': {'card.mill', 'graveyard.enter', 'card.draw'},
               'landfall': {'land_to_battlefield', 'land.enters_battlefield'},
               'land_search': {'land_to_battlefield', 'land.enters_battlefield'},
               'extra_land_drops': {'land_to_battlefield', 'land.enters_battlefield'},
               'repeatable_recursion': {'card.return_to_battlefield', 'battlefield.enter'},
               'sacrifice_conversion': {'permanent.sacrifice', 'permanent.dies', 'creature.card_enters_graveyard'}}
_FILLER = {'a', 'an', 'one', 'or', 'more', 'another', 'other', 'you', 'control', 'controls', 'your', 'target', 'up', 'to', 'of',
           'each', 'that', 'this', 'it'}
_VOCAB = set()


def _vocab(c):
    """Type-line words in this collection (card types, supertypes, subtypes): the words a type filter can be decided on."""
    if not _VOCAB:
        for (t,) in c.execute('select type_line from cards where type_line is not null'):
            _VOCAB.update(w for w in t.lower().replace('—', ' ').replace('//', ' ').split())
    return _VOCAB


def _face_matches(filt, face, vocab, is_token=False):
    """True / False / None (undecidable) for a recorded object filter ("artifact or artificer") against one face's type line."""
    words_on_face = set(face.replace('—', ' ').split())
    results = []
    for alt in filt.lower().replace(',', ' or ').split(' or '):
        ok = True
        for w in alt.split():
            if w in _FILLER or w == 'permanent':
                continue
            if w in ('token', 'nontoken'):
                ok &= (w == 'token') == is_token
                continue
            neg = w.startswith('non') and (w[3:] in vocab or w[3:].rstrip('s') in vocab)
            base = w[3:] if neg else w
            if base not in vocab and base.rstrip('s') in vocab:
                base = base.rstrip('s')
            if base not in vocab:
                ok = None
                break
            ok &= (base in words_on_face) != neg
        results.append(ok)
    if any(r is True for r in results):
        return True
    return False if all(r is False for r in results) else None


def _target_types(texts, vocab):
    """Type words a contract's target eligibility names, e.g. "target nonlegendary enchantment you control" -> nonlegendary enchantment."""
    out = []
    for t in texts:
        alts = []
        for alt in t.lower().replace(',', ' or ').split(' or '):
            words = [w for w in alt.split() if w not in _FILLER and (w in vocab or (w.startswith('non') and w[3:] in vocab))]
            if words:
                alts.append(' '.join(words))
        out.append(' or '.join(alts))
    return out


def _fits_target(p, o, vocab):
    """Could o's card be the object p's targeted ability acts on? True / False / None. Both cards are in one collection, so a
    target an opponent controls (or you don't control) can't be the other card."""
    best = False
    for raw, tt in zip(p['targets'], _target_types(p['targets'], vocab)):
        if any(x in raw.lower() for x in ('opponent controls', "don't control", 'opponent owns')):
            continue
        if not tt:
            return None
        r = [_face_matches(tt, f, vocab) for f in o['faces']]
        if any(x is True for x in r):
            return True
        if any(x is None for x in r) or ' or ' in tt:
            best = None          # disjunctions are not represented in the contracts yet, so a miss stays unresolved (Kate)
    return best


def _self_obs(o, hook):
    """The observer triggers only on its own card ("When this enchantment enters"): from the hook subject or the trigger's event phrase."""
    return o['hook_subject'] == 'self' or (o['triggers'].get(hook) or {}).get('self', False)


def _qualify(p, eff, o, hook, vocab):
    """(status, basis, reason): status is 'compatible' | 'unresolved' | 'incompatible' for producer effect -> observer hook, from recorded qualifiers only."""
    trig = o['triggers'].get(hook) or {}
    self_obs = _self_obs(o, hook)
    if hook == 'counter.put':
        return 'unresolved', 'counter_type_unknown', 'counter type and recipient are not recorded in the contracts (a Saga chapter needs lore counters on that Saga)'
    own = eff in ENTER_EFFECTS and eff != 'token.create' and not p['targets']     # the producer puts its own card onto the battlefield
    if self_obs:
        if p['card'] == o['card'] and own:
            return (('compatible', 'same_card', 'the card re-enters and sees itself enter') if len(o['faces']) == 1 else
                    ('unresolved', 'same_card', 'same card re-enters; which face it enters on is not recorded'))
        if eff in REENTRY_EFFECTS and p['targets']:
            fit = _fits_target(p, o, vocab)
            if fit is False:
                return 'incompatible', 'target_type', f"{o['card']} is not a legal target for: {'; '.join(p['targets'])}"
            return 'unresolved', 'reentry_of_target', f"only if the producer {'copies' if eff == 'token.create' else 'returns'} {o['card']} itself (the observer sees only itself enter)"
        return 'incompatible', 'self_trigger', 'the observer triggers only when it enters itself'
    filt = trig.get('filter')
    implied = HOOK_TYPE.get(hook)
    if own:
        checks = [(_face_matches(filt, f, vocab) if filt else True) and (_face_matches(implied, f, vocab) if implied else True)
                  for f in p['faces']]
        if all(x is False for x in checks):
            return 'incompatible', 'object_type', f"{p['card']} is not {filt or implied}"
        if all(x is True for x in checks):
            return 'compatible', 'object_type', f"{p['card']} matches {filt or implied or 'the trigger'}"
        if any(x is True for x in checks):
            return 'unresolved', 'face', f"only one face of {p['card']} matches {filt or implied}"
        return 'unresolved', 'filter_undecidable', f'filter "{filt}" not decidable from type lines'
    if eff == 'token.create':
        return 'unresolved', 'token_unknown', "the token's characteristics are not recorded" + (f" (it acts on: {'; '.join(p['targets'])})" if p['targets'] else '')
    return ('unresolved', 'object_unknown', 'the produced object is not recorded') if (filt or implied) else \
        ('unresolved', 'no_filter', 'no object filter recorded')


def _links(contracts, only=None, c=None):
    """Producer -> observer candidate links through a shared hook (the KB's FEEDS table), each with a qualifier status.
    `only` keeps links touching those cards. Incompatible links are returned too, so callers can report what was rejected."""
    vocab = _vocab(c) if c is not None else set()
    observers = {}
    for k in contracts:
        for h in k['hooks']:
            observers.setdefault(h, []).append(k)
    seen, out = {}, []
    for p in contracts:
        for eff in p['feeds']:
            for hook in kb.FEEDS.get(eff, []):
                for o in observers.get(hook, []):
                    self_obs = _self_obs(o, hook)
                    if o['contract_id'] == p['contract_id']:
                        continue
                    if self_obs and not ((eff in REENTRY_EFFECTS and p['targets']) or (eff in ENTER_EFFECTS and o['card'] == p['card'])):
                        continue                        # a self trigger sees only its own card entering; not a candidate at all
                    if only is not None and p['card'] not in only and o['card'] not in only:
                        continue
                    status, basis, why = _qualify(p, eff, o, hook, vocab)
                    link = {'producer': p['card'], 'produces': eff, 'observer': o['card'], 'hook': hook,
                            'producer_contract': p['contract_id'], 'observer_contract': o['contract_id'],
                            'producer_state': p['state'], 'observer_state': o['state'], 'link_state': _link_state(p, o),
                            'qualifiers': status, 'basis': basis, 'qualifier_note': why, 'same_card': p['card'] == o['card'], 'also_via': []}
                    # one link per card pair and pathway; other contract pairs on it are kept as also_via, best status wins
                    key = (p['card'], eff, o['card'], hook) if not link['same_card'] else (p['contract_id'], eff, o['contract_id'], hook)
                    have = seen.get(key)
                    if have is None:
                        seen[key] = link
                        out.append(link)
                    elif QUAL_RANK[status] < QUAL_RANK[have['qualifiers']]:
                        extra = have['also_via'] + [[have['producer_contract'], have['observer_contract']]]
                        have.update(link, also_via=extra)
                    else:
                        have['also_via'].append([p['contract_id'], o['contract_id']])
    return out


def _split(links):
    kept = [l for l in links if l['qualifiers'] != 'incompatible']
    rejected = [l for l in links if l['qualifiers'] == 'incompatible']
    return kept, rejected


def _rejected_summary(rejected, n=5):
    by = {}
    for l in rejected:
        by[l['qualifier_note']] = by.get(l['qualifier_note'], 0) + 1
    return {'total': len(rejected), 'by_reason': dict(sorted(by.items(), key=lambda x: -x[1])[:10]),
            'examples': [{k: l[k] for k in ('producer', 'produces', 'observer', 'hook', 'qualifier_note')} for l in rejected[:n]]}


def _acts_on(ks, a, b, vocab):
    """Targeted abilities of a that b's card could be the target of (e.g. a bounce or copy effect), whatever they produce."""
    bk = next((k for k in ks if k['card'] == b), {'faces': []})
    out = []
    for k in ks:
        if k['card'] != a or not k['targets']:
            continue
        fit = _fits_target(k, bk, vocab)
        if fit is False:
            continue
        out.append({'actor': a, 'contract': k['contract_id'], 'text': k['text'], 'produces': k['feeds'], 'acts_on': b,
                    'targets': k['targets'], 'state': k['state'],
                    'qualifiers': 'compatible' if fit else 'unresolved',
                    'qualifier_note': f"{b} fits the target type" if fit else 'target filter not decidable from type lines'})
    return out


def _loops(pool, only=None, ks=None):
    """Loop candidates from the grammar layer's collection discovery, restricted to a card pool. With contracts `ks`, each
    loop is checked against the KB: a step whose effect no KB contract of that card produces is marked unsupported_by_contracts (absence in incomplete contracts is not proof the step can't happen)."""
    if not LOOPS_CSV.exists():
        return []
    feeds = {}
    for k in ks or []:
        for f in k['feeds']:
            feeds.setdefault(k['card'], set()).update([f] + kb.FEEDS.get(f, []))
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
            lp = {'cards': [a, b], 'certainty': r['certainty'], 'a_produces': r['A_produces'], 'b_output': r['B_output'],
                  'enables_a_via': r['enables_A_via'], 'both_fully_parsed': r['both_fully_parsed'] == '1',
                  'capacity_limited': r['capacity_limited'] == '1', 'kb_check': 'not_checked'}
            if ks is not None:
                bad = [f"{n}: no recorded KB contract produces {e}" for n, e in ((a, r['A_produces']), (b, r['B_output'])) if e not in feeds.get(n, set())]
                lp['kb_check'] = 'unsupported_by_contracts' if bad else 'kb_consistent'
                lp['kb_note'] = '; '.join(bad)
            out.append(lp)
    out.sort(key=lambda x: (x['kb_check'] == 'unsupported_by_contracts', CERTAINTY_ORDER.get(x['certainty'], 9), not x['both_fully_parsed'], x['cards']))
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


def _policy():
    """Who may use this collection and which decks are protected (decks/collection_policy.json), or None if not recorded."""
    return json.loads(POLICY.read_text(encoding='utf-8')) if POLICY.exists() else None


def _availability(c, name, policy):
    """Copies by tier: free, in protected decks, in other physically built decks (negotiable), and planned-only rows."""
    protected = set((policy or {}).get('protected_decks') or [])
    row = c.execute('select free from cards where card_name=?', (name,)).fetchone()
    out = {'free': row['free'] if row else 0, 'in_protected_decks': {}, 'in_other_built_decks': {}, 'planned_only': {}}
    for r in c.execute('select deck,sum(quantity) q,physically_assigned,group_concat(distinct status_raw) st from deck_allocations '
                       'where card_name=? group by deck,physically_assigned', (name,)):
        if r['physically_assigned']:
            out['in_protected_decks' if r['deck'] in protected else 'in_other_built_decks'][r['deck']] = r['q']
        else:
            out['planned_only'][r['deck']] = r['st']
    out['usable_without_asking'] = out['free']
    out['usable_by_agreement'] = out['free'] + sum(out['in_other_built_decks'].values())
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
        pol = _policy()
        if pol:
            prot = pol.get('protected_decks') or []
            for d in decks:
                d['protected'] = d['deck'] in prot
            claims.append(claim(f"Collection policy (recorded {pol.get('recorded')} by {pol.get('decided_by')}): {pol.get('owner')}'s "
                                f"collection is shared with {', '.join(pol.get('shared_with') or [])}; protected decks: {', '.join(prot)}. "
                                'Other built decks are negotiable; planned allocations are not physical moves.',
                                'preference', 'collection_policy', evidence=['decks/collection_policy.json']))
        else:
            claims.append(claim('No collection policy is recorded, so who may use these cards, and which decks are protected, is unknown.',
                                'preference', 'none'))
        return {'collection': {'owned_names': tot[0], 'copies': tot[1], 'names_with_free_copy': tot[2]}, 'policy': pol,
                'decks': decks}, claims
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
    pol = _policy()
    av = _availability(c, name, pol)
    if pol:
        claims.append(claim(f"Under the collection policy: {av['usable_without_asking']} usable without asking; "
                            f"{av['usable_by_agreement']} with agreement from other built decks; protected decks hold "
                            f"{sum(av['in_protected_decks'].values())}" + (f" ({', '.join(av['in_protected_decks'])})" if av['in_protected_decks'] else '') + '.',
                            'inventory', 'collection_snapshot', evidence=['decks/collection_policy.json']))
    for k in d['contracts']:
        claims.append(claim(f"Contract reading of: {k['exact_text']}", 'mechanics', k['queue_state'],
                            evidence=[k['contract_id']] + k['failed_checks']))
    data = {'card': d['card'], 'custody': d['custody'], 'held_by': dest['held_by'], 'availability': av,
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
            try:
                seed_card = _card_row(c, seed)['card_name']
            except LookupError as e:
                raise LookupError(f'{e.args[0]}. A seed is a card in the collection or one of the supported themes: '
                                  f'{sorted(kb.THEMES)}') from None
    if ci is None and seed_card and not deck:
        ci = ''.join(x for x in kb.COLORS if x in (_card_row(c, seed_card)['color_identity'] or ''))
    if ci is None and not deck:
        raise ValueError('explore needs a seed card, --ci or --deck to define the card pool')
    pool = _pool(c, ci, deck, free)
    if seed_card:
        pool.add(seed_card)
    ks = _contracts(c, pool)
    theme_contracts = None
    if seed_theme:
        rows = [r for r in kb.theme(c, seed_theme) if r['card_name'] in pool]
        focus = {r['card_name'] for r in rows}
        theme_contracts = {r['contract_id'] for r in rows}
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

    def themed(links):
        # a theme seed keeps links whose themed ability takes part, not every link of a card that has one
        if theme_contracts is None:
            return links
        out = [l for l in links if l['producer_contract'] in theme_contracts or l['observer_contract'] in theme_contracts]
        paths = THEME_PATHS.get(seed_theme, set())
        for l in out:
            l['theme_pathway'] = l['produces'] in paths or l['hook'] in paths
        return out

    if mode == 'focused':
        links, rejected = _split(themed(_links(ks, only=focus, c=c)))
        loops = _loops(pool, only=focus, ks=ks)
        disc = 'requested'
    elif focus:
        # second order: chains seed -> X -> Y where the second step uses a pathway the seed itself does not,
        # scored so that narrow pathways (few cards in the pool share them) come first
        first, rejected = _split(themed(_links(ks, only=focus, c=c)))
        seed_paths = _count_paths(first)
        out_of = {}
        for l in first:
            if l['producer'] in focus and l['observer'] not in focus:   # a chain runs forward from the seed
                out_of.setdefault(l['observer'], []).append(l)
        second = [l for l in _split(_links(ks, only=set(out_of), c=c))[0] if l['producer'] in out_of and l['observer'] not in focus
                  and _pathway(l) not in seed_paths]
        pool_paths = _count_paths(second)
        chains = []
        for l2 in second:
            for l1 in out_of[l2['producer']]:
                score = 1.0 / (seed_paths[_pathway(l1)] * pool_paths[_pathway(l2)])
                quals = 'compatible' if l1['qualifiers'] == l2['qualifiers'] == 'compatible' else 'unresolved'
                chains.append({'score': round(score, 6), 'qualifiers': quals, 'first': l1, 'second': l2,
                               'link_state': 'semantic_reviewed' if l1['link_state'] == l2['link_state'] == 'semantic_reviewed' else 'candidate'})
        chains.sort(key=lambda ch: (ch['qualifiers'] != 'compatible', -ch['score'], ch['first']['producer'], ch['second']['observer']))
        seen, top = set(), []
        for ch in chains:
            k = (ch['first']['hook'], _pathway(ch['second']))
            if k in seen:
                continue                     # one example per pathway pair keeps the answer varied
            seen.add(k)
            top.append(ch)
        data['first_order_links'] = len(first)
        data['rejected_links'] = _rejected_summary(rejected)
        data['chains_total'] = len(chains)
        data['chains_by_qualifiers'] = _count(chains, 'qualifiers')
        data['chains'] = top[:limit]
        loops = [l for l in _loops(pool, only=set(out_of), ks=ks) if not set(l['cards']) & focus]
        _put_loops(data, loops, limit)
        for ch in data['chains']:
            a, b = ch['first'], ch['second']
            claims.append(claim(f"{a['producer']} ({a['produces']}) -> {a['observer']} via {a['hook']}, then "
                                f"{b['producer']} ({b['produces']}) -> {b['observer']} via {b['hook']} (qualifiers {ch['qualifiers']}).",
                                'mechanics', ch['link_state'],
                                evidence=[a['producer_contract'], a['observer_contract'], b['producer_contract'], b['observer_contract']],
                                discovery='unrequested', qualifiers=ch['qualifiers']))
        _loop_claims(claims, data['loops'], "next to the seed's neighbours", 'unrequested')
        return data, claims
    else:
        (links, rejected), loops, disc = _split(_links(ks, c=c)), _loops(pool, ks=ks), 'unrequested'
    data['links_total'] = len(links)
    data['links_by_qualifiers'] = _count(links, 'qualifiers')
    data['links_by_basis'] = _count(links, 'basis')
    if seed_theme:
        data['theme_pathways'] = {'pathways': sorted(THEME_PATHS.get(seed_theme, [])),
                                  'links_on_them': sum(1 for l in links if l.get('theme_pathway'))}
        if not data['theme_pathways']['links_on_them']:
            data['theme_pathways']['note'] = ('no contract in this pool observes the theme\'s own pathways, so the links below come '
                                              'from other abilities of the themed cards and say little about the theme itself')
    data['links_by_pathway'] = {f'{k[0]} -> {k[1]}': n for k, n in sorted(_count_paths(links).items(), key=lambda x: -x[1])[:20]}
    data['rejected_links'] = _rejected_summary(rejected)
    data['links'] = _spread(links, limit)
    _put_loops(data, loops, limit)
    data['hooks_by_link_count'] = dict(sorted(_count(links, 'hook').items(), key=lambda x: -x[1])[:15])
    for l in data['links']:
        claims.append(_link_claim(l, disc))
    _loop_claims(claims, data['loops'], '', disc)
    return data, claims


def _op(cid):
    return cid.rsplit('.', 1)[-1]


def _link_claim(l, disc=None):
    note = 'same card: ' if l['same_card'] else ''
    return claim(f"{l['producer']} [{_op(l['producer_contract'])}] ({l['produces']}) can feed {l['observer']} "
                 f"[{_op(l['observer_contract'])}] via {l['hook']} "
                 f"({note}qualifiers {l['qualifiers']}: {l['qualifier_note']}).", 'mechanics', l['link_state'],
                 evidence=[l['producer_contract'], l['observer_contract']], discovery=disc, qualifiers=l['qualifiers'])


def _put_loops(data, loops, limit):
    """Loops the KB contradicts are listed apart, so a contested loop never hides as a lead (and never hides the cards)."""
    ok = [l for l in loops if l['kb_check'] != 'unsupported_by_contracts']
    bad = [l for l in loops if l['kb_check'] == 'unsupported_by_contracts']
    data['loops_total'] = len(ok)
    data['loops'] = ok[:limit]
    data['loops_contested'] = {'total': len(bad), 'note': 'the grammar layer proposed these, but no KB contract on one side '
                               'records the step. That is lack of support in incomplete contracts, not proof the loop is invalid, '
                               'and the cards may still interact in other ways (see hypothesis)',
                               'examples': [{'cards': l['cards'], 'certainty': l['certainty'], 'kb_note': l['kb_note']} for l in bad[:limit]]}


def _loop_claims(claims, loops, where, disc):
    for l in loops:
        claims.append(claim(f"{l['cards'][0]} and {l['cards'][1]} may form a loop ({l['certainty']})" + (f', {where}' if where else '') + '.',
                            'mechanics', 'candidate', evidence=['grammar/discovery/collection_loops.csv'], discovery=disc,
                            kb_check=l['kb_check']))


def _pathway(l):
    return (l['produces'], l['hook'])


def _count_paths(links):
    out = {}
    for l in links:
        out[_pathway(l)] = out.get(_pathway(l), 0) + 1
    return out


def _spread(links, limit):
    """Pick links round-robin across pathways (effect -> hook), rarest pathway first, so one crowded pathway can't fill the
    answer. A group is a pathway plus its qualifier status and basis (same card, re-entry of a target, object type, ...).
    Tiers fill in order: reviewed first, then links on the theme's own pathways."""
    tiers = {}
    for l in links:
        t = (l['link_state'] != 'semantic_reviewed', not l.get('theme_pathway', True))
        tiers.setdefault(t, []).append(l)
    out = []
    for t in sorted(tiers):
        groups = {}
        for l in sorted(tiers[t], key=lambda l: (l['producer'], l['observer'])):
            groups.setdefault(_pathway(l) + (l['qualifiers'], l.get('basis')), []).append(l)
        # rarer groups first (they are the less obvious ones), compatible before unresolved at equal size
        order = sorted(groups, key=lambda k: (len(groups[k]), k[2] != 'compatible'))
        i = 0
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
    vocab = _vocab(c)
    every = _links(ks, only={a, b}, c=c)
    pair = [l for l in every if {l['producer'], l['observer']} == {a, b}]
    same_card = [l for l in every if l['same_card'] and l['qualifiers'] != 'incompatible']
    if effect:
        pair = [l for l in pair if effect in (l['produces'], l['hook'])]
    links, rejected = _split(pair)
    acts_on = _acts_on(ks, a, b, vocab) + _acts_on(ks, b, a, vocab)
    if effect:
        acts_on = [x for x in acts_on if effect in x['produces']]
    all_loops = [l for l in _loops({a, b}, ks=ks) if set(l['cards']) == {a, b}]
    loops = [l for l in all_loops if l['kb_check'] != 'unsupported_by_contracts']
    contested = [l for l in all_loops if l['kb_check'] == 'unsupported_by_contracts']
    disconfirming = [f"rejected link {l['producer']} ({l['produces']}) -> {l['observer']} via {l['hook']}: {l['qualifier_note']}"
                     for l in rejected]
    disconfirming += [f"contested loop ({l['certainty']}): {l['kb_note']}" for l in contested]
    used = {x for l in links + same_card for x in (l['producer_contract'], l['observer_contract'])} | {x['contract'] for x in acts_on}
    for cid in sorted(used):
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
    claims = [_link_claim(l) for l in links]
    for x in acts_on:
        claims.append(claim(f"{x['actor']}'s ability can act on {x['acts_on']} ({'; '.join(x['targets'])}; produces "
                            f"{', '.join(x['produces']) or 'nothing recorded'}): {x['text']}", 'mechanics',
                            'semantic_reviewed' if x['state'] in REVIEWED_STATES else 'candidate', evidence=[x['contract']],
                            qualifiers=x['qualifiers']))
    for l in same_card:
        claims.append(_link_claim(l))
    for l in loops:
        claims.append(claim(f"{a} and {b} may form a loop ({l['certainty']}).", 'mechanics', 'candidate',
                            evidence=['grammar/discovery/collection_loops.csv'], kb_check=l['kb_check']))
    if not links and not loops and not acts_on:
        claims.append(claim(f'No contract link, targeted ability or loop candidate connects {a} and {b}' +
                            (f' through {effect}' if effect else '') + '.', 'mechanics', 'candidate',
                            evidence=['absence in the KB is not proof of absence: contracts cover parsed abilities only']))
    states = {k['contract_id']: k['state'] for k in ks}
    unverified = sorted(x for x in used if states.get(x) not in REVIEWED_STATES)
    data = {'cards': [a, b], 'effect': effect, 'links': links, 'acts_on': acts_on, 'same_card_links': same_card,
            'loops': loops, 'loops_contested': contested, 'rejected_links': rejected,
            'conditions': [{'contract_id': k['contract_id'], 'card': k['card'], 'text': k['text'], 'state': k['state']}
                           for k in ks if k['contract_id'] in used],
            'unverified_contracts': unverified, 'disconfirming_evidence': disconfirming, 'limitations': LINK_LIMITS,
            'reading_note': 'A rejected link or contested loop rules out that one route only. Check acts_on and the other '
                            'links before deciding the cards do not interact.',
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


ASSERTS = {'inventory': ('owned_min', 'free_min', 'usable_without_asking_min', 'usable_by_agreement_min', 'in_deck'),
           'rules_text': ('text_contains',)}
VERDICTS = ('SUPPORTED', 'CONTRADICTED', 'UNKNOWN', 'NOT_CHECKED')


def _verdict(c, kind, rows, missing, asserts):
    """SUPPORTED / CONTRADICTED / UNKNOWN / NOT_CHECKED for a structured assertion, with the reasons. Free text is never judged."""
    if not asserts:
        return 'NOT_CHECKED', ['no structured assertion given ("assert"); the text itself is not judged']
    allowed = ASSERTS.get(kind)
    if not allowed:
        return 'NOT_CHECKED', [f'{kind} claims have no mechanical check in v0']
    bad = sorted(set(asserts) - set(allowed))
    if bad:
        raise ValueError(f'unknown assert key(s) {bad} for {kind}; allowed: {list(allowed)}')
    if missing or not rows:
        return 'UNKNOWN', ['not every named card is in this collection'] + missing
    pol = _policy()
    why, ok = [], True
    for r in rows:
        n = r['card_name']
        if kind == 'inventory':
            av = _availability(c, n, pol)
            for key, val in asserts.items():
                if key in ('usable_without_asking_min', 'usable_by_agreement_min') and not pol:
                    return 'UNKNOWN', ['no collection policy is recorded, so who may use which copies is unknown']
                have = {'owned_min': r['owned_min'], 'free_min': r['free'],
                        'usable_without_asking_min': av['usable_without_asking'],
                        'usable_by_agreement_min': av['usable_by_agreement']}.get(key)
                if key == 'in_deck':
                    held = set(av['in_protected_decks']) | set(av['in_other_built_decks'])
                    good = val in held
                    why.append(f'{n}: physically in {sorted(held) or "no deck"}')
                else:
                    good = (have or 0) >= val
                    why.append(f'{n}: {key[:-4]} {have} (needs >= {val})')
                ok &= good
        else:
            text = (r['oracle_text'] or '').lower()
            good = asserts['text_contains'].lower() in text
            why.append(f"{n}: rules text {'contains' if good else 'does not contain'} {asserts['text_contains']!r}")
            ok &= good
    return ('SUPPORTED' if ok else 'CONTRADICTED'), why


def check(c, items):
    """Per-claim support: what each claim in a draft answer rests on, what is still missing, and, for a structured
    assertion, whether the evidence supports or contradicts it. Evidence authority is never claim truth: `evidence_grade`
    says how good the source is, `verdict` whether the assertion holds, and `grade` is decision_grade only when a
    decision-grade source settles the assertion. The verdict's object is the assertion (`verdict_on`), never the sentence:
    a true assertion next to a false sentence is SUPPORTED, and `text_judged` stays false. A CONTRADICTED verdict with
    decision_grade means the contradiction is established, not the sentence."""
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
            unrev = [k['contract_id'] for k in ks if k['state'] not in REVIEWED_STATES]
            support = 'semantic_reviewed' if ks and not unrev and not missing else ('candidate' if ks else 'none')
            evidence = [f"{k['contract_id']}: {k['state']}" for k in ks]
            if unrev:
                missing.append(f'{len(unrev)} contract(s) not semantically reviewed')
            if not ks:
                missing.append('no contracts for these cards')
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
        verdict, why = _verdict(c, kind, rows, missing, it.get('assert'))
        cl = claim(it.get('text', ''), kind, support, evidence=evidence, missing=missing, verdict=verdict, verdict_basis=why,
                   verdict_on='assertion', assertion=it.get('assert'), text_judged=False)
        cl['evidence_grade'] = cl['grade']
        if verdict not in ('SUPPORTED', 'CONTRADICTED') and cl['grade'] == 'decision_grade':
            cl['grade'] = 'exploratory'          # a good source alone does not settle an unchecked claim
        out.append(cl)
    return {'checked': len(out), 'by_verdict': _count(out, 'verdict'),
            'assert_keys': {k: list(v) for k, v in ASSERTS.items()}}, out
