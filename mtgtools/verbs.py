"""The read-only verbs over the KB (dio lives in dio.py). Each returns a dict that the CLI wraps in the common envelope.

Card meaning comes only from the KB (contracts, Oracle rules text) and the grammar layer's loop discovery (P-01).
Apart from the declared lookup in `typal` (below), nothing here parses card text. Interaction links are candidates unless both contracts are semantically reviewed (P-03),
and exploration output is never a ranking of card quality (P-04).

@ai-semantic-role: candidate-source
Only `typal` reads rules text, as a declared lexical lookup for retrieval (labelled lexical_match, C-014); every other verb
reads contracts.
"""
import csv
import json
import re
from pathlib import Path

from . import kb
import counters as COUNTERS   # kb/counters.py, on the path via mtgtools.kb
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
    if hits:
        raise LookupError(f'card not found: {name!r}; did you mean one of {hits}')
    raise LookupError(f'card not found: {name!r}. The KB holds only the cards in the inventory snapshot it was built from, so '
                      'either the card is not owned, or it was acquired after that snapshot, or the name is spelled differently; '
                      'the KB cannot tell which. If it is owned, it has no contract until the next KB release: annotate it by hand '
                      '(python3 -m mtgtools dio 11), label that reading as agent-drafted, and explore the owned side with '
                      'explore THEME or explore OWNED_CARD.')


# events a cost records under on_payment that other cards can observe (Viscera Seer's "Sacrifice a creature:" feeds Blood
# Artist). The KB's query_index.feeds lists only resolution effects, so these are read from the cost itself.
COST_FEEDS = ('permanent.sacrifice', 'card.discard')


def _paid_events(j):
    """{effect: object filter of what is paid} for the observable events in a contract's cost ('this' = the card itself)."""
    out = {}
    for g in (j.get('initiation') or {}).get('requirement_groups') or []:
        if g.get('class') != 'cost':
            continue
        for alt in g.get('alternatives') or []:
            for ev in alt.get('on_payment') or []:
                base, _, obj = ev.partition(' [')
                if base in COST_FEEDS:
                    out.setdefault(base, (alt.get('object_filter') or obj.rstrip(']') or None))
    return out


def _own_names(card, type_line=None):
    """How a card's text names itself: its full name, the short name before a comma ("Jet enters"), and for a legendary
    card without a comma its first word ("Sharuum enters" on Sharuum the Hegemon)."""
    out = set()
    legendary = 'legendary' in (type_line or '').lower()
    for face in card.lower().split(' // '):
        out.update({face + ' ', face.split(',')[0] + ' '})
        if legendary and ',' not in face and ' ' in face:
            out.add(face.split()[0] + ' ')
    return tuple(out)


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
                    q = alt.get('qualifiers') or {}
                    t = {'filter': q.get('object_filter'),
                         'self': alt.get('subject') == 'this' or phrase.startswith(('this ', '~ ') + _own_names(r['card_name'], r['type_line'])),
                         'others': bool(q.get('other')) or phrase.startswith(('another ', 'a ', 'an ', 'each ', 'one or more ')),
                         'parsed': bool(q)}
                    have = triggers.get(alt['id'])
                    if have:   # "this creature or another creature dies": one event id, two alternatives
                        keep = t if t['others'] or not have['others'] else have
                        t = dict(keep, self=have['self'] and t['self'], others=have['others'] or t['others'])
                    triggers[alt['id']] = t
                elif g.get('class') == 'eligibility' and 'target' in (alt.get('text') or ''):
                    targets.append(alt['text'])
        feeds = list(qi.get('feeds') or [])
        paid = _paid_events(j)
        paid = {e: f for e, f in paid.items() if e not in feeds}
        out.append({'contract_id': r['contract_id'], 'card': r['card_name'], 'text': r['exact_text'], 'kind': r['operation_kind'],
                    'state': r['queue_state'], 'feeds': feeds + sorted(paid), 'paid': paid, 'hooks': qi.get('hook_ids') or [],
                    'hook_subject': qi.get('hook_subject'), 'triggers': triggers, 'targets': targets,
                    'counters': qi.get('counters') or [],
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
        if not tt and re.search(r'\btarget (player|opponent)s?\b', raw.lower()) and 'any target' not in raw.lower():
            continue      # a player is not a card in the collection
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
    t = o['triggers'].get(hook) or {}
    if t.get('others'):        # "this creature or another creature dies" also watches other objects, whatever hook_subject says
        return False
    return o['hook_subject'] == 'self' or t.get('self', False)


def _qualify(p, eff, o, hook, vocab):
    """(status, basis, reason): status is 'compatible' | 'unresolved' | 'incompatible' for producer effect -> observer hook, from recorded qualifiers only."""
    trig = o['triggers'].get(hook) or {}
    self_obs = _self_obs(o, hook)
    if hook == 'counter.put':
        made = [f['kind'] for f in p.get('counters') or [] if f['role'] in ('put', 'enters_with', 'proliferate')]
        heard = [f['kind'] for f in o.get('counters') or [] if f['role'] == 'listen_put']
        if not made or not heard:
            return 'unresolved', 'counter_type_unknown', 'counter kind is not recorded on both contracts (a Saga chapter needs lore counters on that Saga)'
        verdicts = {COUNTERS.match(m, h) for m in made for h in heard}
        pair = f"{'/'.join(sorted(set(made)))} -> {'/'.join(sorted(set(heard)))}"
        if 'compatible' in verdicts:
            return 'unresolved' if self_obs else 'compatible', 'counter_kind', f'counter kind matches ({pair}); recipient not checked' + \
                ('; the observer watches only itself' if self_obs else '')
        if 'possible' in verdicts:
            return 'unresolved', 'counter_kind_possible', f'kind depends on what is already there ({pair}): proliferate or generic counters'
        return 'incompatible', 'counter_kind', f'different counter kinds ({pair})'
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
    if eff in p.get('paid', {}):
        obj = p['paid'][eff]
        where = f"paid as a cost ({p['text'].split(':')[0].strip()})"
        if not (filt or implied):
            return 'unresolved', 'paid_no_filter', f'{where}; no object filter recorded'
        if not obj:
            return 'unresolved', 'paid_object_unknown', f'{where}; the paid object is not recorded'
        need = ' '.join(x for x in (filt, implied) if x)
        if 'token' in need.split() or 'nontoken' in need.split():
            return 'unresolved', 'paid_object', f'{where}; token or nontoken not decidable'
        faces = p['faces'] if obj == 'this' else [obj.lower()]
        checks = [(_face_matches(filt, f, vocab) if filt else True) and (_face_matches(implied, f, vocab) if implied else True)
                  for f in faces]
        if all(x is True for x in checks):
            return 'compatible', 'paid_object', f"{where}: the paid {'card' if obj == 'this' else obj} matches {need}"
        return 'unresolved', 'paid_object', f"{where}: the paid {obj} may not be {need} (an artifact can also be a creature)"
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


NOT_A_LOOP = ('unsupported_by_contracts', 'once_only')   # listed under loops_contested, never as loops


def _loops(pool, only=None, ks=None):
    """Loop candidates from the grammar layer's collection discovery, restricted to a card pool. With contracts `ks`, each
    loop is checked against the KB: a step whose effect no KB contract of that card produces is marked unsupported_by_contracts (absence in incomplete contracts is not proof the step can't happen)."""
    if not LOOPS_CSV.exists():
        return []
    feeds, final, spells = {}, set(), set()
    for k in ks or []:
        for f in k['feeds']:
            feeds.setdefault(k['card'], set()).update([f] + kb.FEEDS.get(f, []))
        if any(x['kind'] == 'finality' and x['role'] in ('enters_with', 'put') for x in k['counters']):
            final.add(k['card'])
        if k['faces'] and all(('instant' in f or 'sorcery' in f) and 'adventure' not in f for f in k['faces']):
            spells.add(k['card'])
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
                once = [f'{n} gets a finality counter, so the next time it would die it is exiled: the cycle runs at most once'
                        for n in sorted(final & {a, b})]
                once += [f'{n} is an instant or sorcery: it resolves once, so it cannot repeat the cycle' for n in sorted(spells & {a, b})]
                lp['kb_check'] = 'unsupported_by_contracts' if bad else 'once_only' if once else 'kb_consistent'
                lp['kb_note'] = '; '.join(bad or once)
            out.append(lp)
    out.sort(key=lambda x: (x['kb_check'] in NOT_A_LOOP, CERTAINTY_ORDER.get(x['certainty'], 9), not x['both_fully_parsed'], x['cards']))
    return out


def _resolve_deck(c, deck):
    """A deck by its inventory name, or by its commander's name ("Auntie Ool" is recorded as the deck Blight Curse)."""
    decks = kb.decks(c)
    for d in decks:
        if d.lower() == deck.strip().lower():
            return d
    hits = sorted({r[0] for r in c.execute("select deck from deck_allocations where section='Commander' and counts_in_deck_100=1 "
                                           'and lower(card_name) like ?', (deck.strip().lower() + '%',))})
    if len(hits) == 1:
        return hits[0]
    raise LookupError(f'deck not found: {deck!r}' + (f'; commander matches several decks: {hits}' if hits else '') +
                      f'; decks: {decks}')


def _pool(c, ci=None, deck=None, free=False):
    if deck:
        names = set(kb.deck_cards(c, _resolve_deck(c, deck)))
        return names
    out = set()
    for r in c.execute('select * from cards where owned_min>0'):
        if free and r['free'] <= 0:
            continue
        if ci is not None and not kb.legal_rules(c, r, ci)[0]:
            continue
        out.add(r['card_name'])
    return out


def _policy(c=None):
    """Who may use this collection and which decks are protected, or None if not recorded. A collection_policy.json beside
    the database wins over decks/collection_policy.json (an as-of database built by tools/asof_kb.py carries its dated
    policy there, or {"not_recorded": true} so that today's policy is never applied to a past collection)."""
    if c is not None:
        main = next((r[2] for r in c.execute('pragma database_list') if r[1] == 'main'), None)
        local = Path(main).parent / 'collection_policy.json' if main else None
        if local and local.exists():
            j = json.loads(local.read_text(encoding='utf-8'))
            return None if j.get('not_recorded') else j
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
        pol = _policy(c)
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
    deck = _resolve_deck(c, deck)
    cards = kb.deck_cards(c, deck)
    ov = kb.overlap(c, deck)
    ch = _charter(deck)
    size = c.execute('select sum(quantity) from deck_allocations where deck=? and counts_in_deck_100=1', (deck,)).fetchone()[0]
    claims = [claim(f'{deck} counts {size} cards toward its 100 ({len(cards)} distinct names) in the snapshot.', 'inventory', 'collection_snapshot')]
    claims.append(claim(f'{deck} has a deck charter recording preferences and constraints.' if ch else
                        f'{deck} has no deck charter yet, so preferences and constraints are unknown to the tools.',
                        'preference', 'deck_charter' if ch else 'none'))
    sole = ov['sole_detected_candidates']
    named = '; '.join(k + ': ' + v['card'] for k, v in sorted(sole.items())) or 'none here'
    claims.append(claim(f"{deck}'s role counts are detected candidates: {sum(ov['reviewed_role_counts'].values())} of "
                        f"{sum(ov['role_counts'].values())} card-role assignments are reviewed. A sole detected candidate "
                        f'({named}) is not a verified sole provider; read the card before protecting it or cutting around it.',
                        'mechanics', 'semantic_reviewed' if ov['role_counts'] and ov['reviewed_role_counts'] == ov['role_counts'] else 'candidate'))
    return {'deck': deck, 'color_identity': kb.deck_ci(c, deck), 'cards': cards, 'charter': ch,
            'roles': {k: ov[k] for k in ('evidence', 'role_counts', 'reviewed_role_counts', 'sole_detected_candidates')}}, claims


def _counter_facets(c, name):
    """Card-level counter facets (drafted, not reviewed) from the KB's derived_facts, or None if the KB predates them."""
    try:
        r = c.execute("select value_json from derived_facts where fact_kind='counter_facets' and card_name=?", (name,)).fetchone()
    except Exception:
        return None
    return json.loads(r[0]) if r else {'facets': [], 'order_note': None}


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
    pol = _policy(c)
    av = _availability(c, name, pol)
    if pol:
        claims.append(claim(f"Under the collection policy: {av['usable_without_asking']} usable without asking; "
                            f"{av['usable_by_agreement']} with agreement from other built decks; protected decks hold "
                            f"{sum(av['in_protected_decks'].values())}" + (f" ({', '.join(av['in_protected_decks'])})" if av['in_protected_decks'] else '') + '.',
                            'inventory', 'collection_snapshot', evidence=['decks/collection_policy.json']))
    for k in d['contracts']:
        claims.append(claim(f"Contract reading of: {k['exact_text']}", 'mechanics', k['queue_state'],
                            evidence=[k['contract_id']] + k['failed_checks']))
    cf = _counter_facets(c, name)
    if cf and cf['facets']:
        kinds = sorted({f"{f['role']} {f['kind']} ({f['holder']})" for f in cf['facets']})
        claims.append(claim('Counter facets: ' + '; '.join(kinds) + '. Drafted from rules text; kinds are kept, sign is not '
                            'assumed (DIO v3.1.1 state table).', 'mechanics', 'candidate', evidence=['derived_facts.counter_facets']))
        if cf.get('order_note'):
            claims.append(claim(cf['order_note'], 'rules_text', 'oracle', evidence=['CR 614.1c', 'CR 704.3', 'CR 704.5f', 'CR 704.5q']))
    data = {'card': d['card'], 'custody': d['custody'], 'held_by': dest['held_by'], 'availability': av,
            'counters': cf['facets'] if cf else None,
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
    ok = [l for l in loops if l['kb_check'] not in NOT_A_LOOP]
    bad = [l for l in loops if l['kb_check'] in NOT_A_LOOP]
    data['loops_total'] = len(ok)
    data['loops'] = ok[:limit]
    data['loops_contested'] = {'total': len(bad), 'note': 'the grammar layer proposed these, but no KB contract on one side '
                               'records the step (unsupported_by_contracts), or a recorded counter ends it after one pass (once_only). Unsupported is '
                               'lack of support in incomplete contracts, not proof the loop is invalid, and the cards may still interact '
                               'in other ways (see hypothesis)',
                               'examples': [{'cards': l['cards'], 'certainty': l['certainty'], 'kb_check': l['kb_check'],
                                             'kb_note': l['kb_note']} for l in bad[:limit]]}


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
    loops = [l for l in all_loops if l['kb_check'] not in NOT_A_LOOP]
    contested = [l for l in all_loops if l['kb_check'] in NOT_A_LOOP]
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
    pol = _policy(c)
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


# ---------- typal census ----------

# KB capability tags (from the Sheet's Roles column) that mark a card as working with a creature type in general
TYPAL_TAGS = {'Changeling', 'Choose a creature type', 'Creature-type synergy', 'Typal payoff'}
GENERIC_TAGS = {'Changeling', 'Choose a creature type'}   # the other two also mark cards about one fixed type (Goblins, Orcs)
# declared lexical lookups over the KB's rules text; they find candidates for retrieval and never decide mechanics (P-01)
EVERY_TYPE_PHRASES = ('is every creature type', "it's every creature type", "they're every creature type", 'all creature types')
CHOSEN_TYPE_PHRASES = ('choose a creature type', 'chosen type', 'creature type of your choice', 'shares a creature type',
                       'share a creature type')
TYPAL_READING = ['Membership is the type line in the snapshot. Whether a payoff counts a card is a qualifier question the DIO '
                 'decides, not this census: cast versus enters (a card put onto the battlefield was not cast), Changeling in '
                 'every zone, and Kindred spells that have a creature type without being creatures (dio 4.1, dio changeling).',
                 'Lexical hits are declared text lookups over the KB rules text. They widen retrieval; they are not contract '
                 'readings and they are not verified.']


def _rules_text(c, row):
    r = c.execute("select rules_text from rules_text where card_name=? and authority='oracle_refresh'", (row['card_name'],)).fetchone()
    return (r[0] if r and r[0] else row['oracle_text']) or ''


def _subtypes(type_line):
    """Subtype words per face: what follows the dash on each face of the type line."""
    out = set()
    for face in (type_line or '').split('//'):
        if '—' in face:
            out.update(w.lower() for w in face.split('—', 1)[1].split())
    return out


def typal(c, ctype, ci=None, free=False):
    """Inventory-first census for a creature type: members, every-type cards, generic type support and cards that name the
    type, each with availability under the collection policy. A retrieval aid for a typal request, not a ranking (P-04)."""
    import re
    t = ctype.strip().lower()
    if t.endswith('s') and t not in _vocab(c) and t[:-1] in _vocab(c):
        t = t[:-1]
    if t not in _vocab(c):
        raise LookupError(f'{ctype!r} is not a type-line word in this collection, so no owned card has it as a type')
    word = re.compile(r'\b' + re.escape(t) + r'(s|es)?\b', re.I)
    pol = _policy(c)
    tags = {}
    for r in c.execute('select card_name,capability from capability_claims where capability in (%s)' % ','.join('?' * len(TYPAL_TAGS)),
                       tuple(TYPAL_TAGS)):
        tags.setdefault(r['card_name'], set()).add(r['capability'])
    groups = {'members': [], 'every_type': [], 'names_the_type': [], 'type_support': [], 'tagged_only': []}
    gaps = []
    for row in c.execute('select * from cards where owned_min>0 order by card_name'):
        name = row['card_name']
        if ci is not None and not kb.legal_rules(c, row, ci)[0]:
            continue
        if free and row['free'] <= 0:
            continue
        text = _rules_text(c, row).lower()
        own = sorted(tags.get(name, ()))
        basis, group = [], None
        if t in _subtypes(row['type_line']):
            group = 'members'
            basis.append('type_line')
        elif 'changeling' in (row['keywords_stored'] or '').lower() or 'Changeling' in own:
            group = 'every_type'
            basis.append('keyword:Changeling' if 'changeling' in (row['keywords_stored'] or '').lower() else 'tag:Changeling')
        elif any(p in text for p in EVERY_TYPE_PHRASES):
            group = 'every_type'
            basis.append('lexical:every creature type')
        elif word.search(text):
            group = 'names_the_type'
            basis.append(f'lexical:names {t}')
        elif set(own) & GENERIC_TAGS or any(p in text for p in CHOSEN_TYPE_PHRASES):
            group = 'type_support'
            basis += ['tag:' + x for x in own if x in GENERIC_TAGS]
            if any(p in text for p in CHOSEN_TYPE_PHRASES):
                basis.append('lexical:chosen type')
        elif own:
            group = 'tagged_only'
            basis += ['tag:' + x for x in own]
        if not group:
            continue
        if group in ('every_type', 'type_support') and not set(own) & GENERIC_TAGS:
            gaps.append(name)
        av = _availability(c, name, pol)
        groups[group].append({'card': name, 'type_line': row['type_line'], 'color_identity': row['color_identity'] or 'C',
                              'owned': row['owned_min'], 'free': row['free'], 'basis': basis, 'kb_tags': own,
                              'can_be_commander': row['can_be_commander_stored'] == 'Yes',
                              'kind': ('kindred' if 'kindred' in (row['type_line'] or '').lower() else
                                       'creature' if 'creature' in (row['type_line'] or '').lower() else 'other'),
                              'in_protected_decks': av['in_protected_decks'], 'in_other_built_decks': av['in_other_built_decks'],
                              'usable_without_asking': av['usable_without_asking'], 'usable_by_agreement': av['usable_by_agreement']})
    members = groups['members']
    by_ci = _count(members, 'color_identity')
    shells = []
    for cmd in [m for m in members if m['can_be_commander']]:
        cci = ''.join(x for x in cmd['color_identity'] if x in kb.COLORS)
        legal = lambda g: [x for x in groups[g] if set(x['color_identity']) - {'C'} <= set(cci)]
        shells.append({'commander': cmd['card'], 'color_identity': cmd['color_identity'],
                       'commander_usable_without_asking': cmd['usable_without_asking'],
                       'members_in_identity': len(legal('members')), 'every_type_in_identity': len(legal('every_type')),
                       'names_the_type_in_identity': len(legal('names_the_type')),
                       'type_support_in_identity': len(legal('type_support'))})
    covered = {s['color_identity'] for s in shells}
    uncovered = sorted(k for k in by_ci if not any(set(k) - {'C'} <= set(x) for x in covered))
    counts = {g: len(v) for g, v in groups.items()}
    held = sorted({x['card'] for g, v in groups.items() if g != 'tagged_only' for x in v
                   if x['in_protected_decks'] and x['usable_without_asking'] <= 0})
    claims = [claim(f"The snapshot holds {counts['members']} owned card names with {t} on the type line "
                    f"({sum(m['owned'] for m in members)} copies, {sum(m['free'] for m in members)} free); by color identity: "
                    + ', '.join(f'{k} {v}' for k, v in sorted(by_ci.items(), key=lambda kv: -kv[1])) + '.',
                    'inventory', 'collection_snapshot'),
              claim(f"Beyond members: {counts['every_type']} every-type cards (Changeling and type-granting effects), "
                    f"{counts['type_support']} cards that work with a chosen or shared creature type, and {counts['names_the_type']} "
                    f"cards whose text names {t}. {counts['tagged_only']} more carry a typal tag without chosen-type wording, "
                    'probably about one other type (tagged_only). Read each before counting it.',
                    'rules_text', 'lexical_match', discovery='requested')]
    if uncovered:
        claims.append(claim(f"No owned {t} commander covers color identit{'y' if len(uncovered) == 1 else 'ies'} "
                            f"{', '.join(uncovered)}, which hold {sum(by_ci[k] for k in uncovered)} member names; a shell there "
                            f'needs a commander from outside the type.', 'inventory', 'collection_snapshot'))
    if held:
        claims.append(claim(f"{len(held)} of these have every copy in a protected deck and are not available without agreement: "
                            + ', '.join(held) + '.', 'inventory', 'collection_snapshot', evidence=['decks/collection_policy.json']))
    if gaps:
        claims.append(claim(f'{len(gaps)} cards were found only by text lookup; the KB capability tags miss them: '
                            + ', '.join(gaps) + '. This is a data-layer gap (Sheet Roles), not a tool result.',
                            'rules_text', 'lexical_match', evidence=['capability_claims']))
    if not shells:
        claims.append(claim(f'No owned {t} can be your commander, so a {t} deck needs a commander from outside the type.',
                            'inventory', 'collection_snapshot'))
    return {'creature_type': t, 'counts': counts, 'members_by_color_identity': by_ci, 'commander_candidates': shells,
            'identities_without_type_commander': uncovered, 'held_in_protected_decks': held, 'tag_gaps': gaps, 'reading': TYPAL_READING, **groups}, claims


# ---------- deck decommission: release audit ----------

MINUS_COUNTER = ('-1/-1 counter',)
BASICS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'}


def release(c, donor, receiver):
    """Release audit for retiring DONOR and absorbing into RECEIVER: which donor cards the receiver already runs, which can't
    go there, which already have a free copy elsewhere (no disassembly needed), and which only the decommission unlocks.
    A retiring donor's deck floor is not a constraint; physical custody still is. Nothing moves (P-05)."""
    donor, receiver = _resolve_deck(c, donor), _resolve_deck(c, receiver)
    if donor == receiver:
        raise ValueError('donor and receiver are the same deck')
    pol = _policy(c)
    protected = set((pol or {}).get('protected_decks') or [])
    rci = kb.deck_ci(c, receiver)
    rcards = set(kb.deck_cards(c, receiver))
    groups = {'already_in_receiver': [], 'outside_receiver_identity': [], 'free_copy_elsewhere': [], 'unlocked_by_decommission': []}
    basics = 0
    for name in kb.deck_cards(c, donor):
        row = c.execute('select * from cards where card_name=?', (name,)).fetchone()
        if name in BASICS:
            basics += c.execute('select sum(quantity) from active_deck_cards where deck=? and card_name=?', (donor, name)).fetchone()[0]
            continue
        text = _rules_text(c, row).lower()
        av = _availability(c, name, pol)
        item = {'card': name, 'type_line': row['type_line'], 'color_identity': row['color_identity'] or 'C', 'free': row['free'],
                'in_other_built_decks': {k: v for k, v in av['in_other_built_decks'].items() if k != donor},
                'in_protected_decks': av['in_protected_decks']}
        cf = _counter_facets(c, name)
        if cf is not None:
            minus_roles = sorted({f['role'] for f in cf['facets'] if f['kind'] == '-1/-1'})
            if minus_roles:
                item['counters'] = {'-1/-1': minus_roles}
                item['check'] = ('-1/-1 counters (' + ', '.join(minus_roles) + '): they cancel +1/+1 counters (CR 704.5q)'
                                 + ('; ' + cf['order_note'] if cf.get('order_note') else ''))
        elif any(p in text for p in MINUS_COUNTER):
            item['check'] = 'mentions -1/-1 counters (lexical): they cancel +1/+1 counters (CR 704.5q); check which side gets them'
        if name in rcards:
            groups['already_in_receiver'].append(item)
        elif not kb.legal_rules(c, row, rci)[0]:
            groups['outside_receiver_identity'].append(item)
        elif row['free'] > 0:
            groups['free_copy_elsewhere'].append(item)
        else:
            groups['unlocked_by_decommission'].append(item)
    counts = {g: len(v) for g, v in groups.items()}
    minus = [x['card'] for x in groups['unlocked_by_decommission'] + groups['free_copy_elsewhere'] if 'check' in x]
    claims = [claim(f"{donor} holds {sum(counts.values())} nonbasic names (+{basics} basic lands). For {receiver} ({rci}): "
                    f"{counts['already_in_receiver']} are already in it, {counts['outside_receiver_identity']} are outside its "
                    f"identity, {counts['free_copy_elsewhere']} have a free copy elsewhere (no disassembly needed), and "
                    f"{counts['unlocked_by_decommission']} become available only if {donor} is taken apart.",
                    'inventory', 'collection_snapshot'),
              claim('A copy of a card the receiver already runs adds no slot: singleton. Released copies return to the free pool.',
                    'rules_text', 'oracle')]
    if donor in protected:
        claims.append(claim(f'{donor} is a protected deck: decommissioning it needs agreement from Zach and Steph.',
                            'preference', 'collection_policy', evidence=['decks/collection_policy.json']))
    if receiver in protected:
        claims.append(claim(f'{receiver} is protected: adding to it needs no release from anyone else, but every cut from it does.',
                            'preference', 'collection_policy', evidence=['decks/collection_policy.json']))
    if minus:
        facet_kb = _counter_facets(c, minus[0]) is not None
        claims.append(claim(f'{len(minus)} candidates put, require or remove -1/-1 counters ({", ".join(minus)}). '
                            + ('Each carries its counter roles (drafted counter facets, not reviewed); whether they help or hurt '
                               'depends on which permanent gets them, so read the roles against the receiver.' if facet_kb else
                               'This KB predates counter facets, so the match is lexical; read each card.'),
                            'mechanics', 'candidate', evidence=['derived_facts.counter_facets' if facet_kb else 'C-015']))
    claims.append(claim('This is a release audit, not an absorption verdict: which receiver cards to cut, and how much of each '
                        "card's function survives leaving the donor's engine, still need hypothesis/compare and the deck charter.",
                        'performance', 'none'))
    return {'mode': 'decommission', 'donor': donor, 'receiver': receiver, 'receiver_color_identity': rci,
            'donor_basic_lands': basics, 'counts': counts, **groups}, claims


# ---------- find: functional retrieval (Kate, 2026-11-01) ----------

# A role is a KB capability (mtg_eval role or Collection.Roles tag). A family pairs the cards that perform a function with
# the cards that support (pay off) it, so an outlet and a payoff are never counted as the same match. Retrieval only: the
# capabilities come from the KB's capability_claims; this table names them, it reads no Oracle text (P-01).
ROLE_FAMILIES = {
    'sacrifice': {'performs': ['sac_outlet', 'Sacrifice outlet'], 'supports': ['death_payoff', 'Death trigger']},
    'tokens': {'performs': ['token_maker', 'artifact_token', 'Token maker'], 'supports': ['token_payoff', 'Token multiplier']},
    'lifegain': {'performs': ['lifegain_source', 'Lifegain'], 'supports': ['lifegain_payoff']},
    'counters': {'performs': ['counter_source', 'Counters', 'Proliferate'],
                 'supports': ['counter_payoff', 'counter_multiplier', 'Counter payoff', 'Counter multiplier']},
    'artifacts': {'performs': ['artifact_token'], 'supports': ['artifact_payoff', 'Artifact synergy']},
    'landfall': {'performs': ['land_drop', 'Land search'], 'supports': ['landfall_payoff', 'Landfall', 'Lands matter']},
    'spells': {'performs': ['instant_sorcery'], 'supports': ['spell_payoff', 'Spellslinger payoff']},
    'graveyard': {'performs': ['self_mill', 'Mill', 'Surveil'], 'supports': ['recursion', 'reanimation', 'Recursion', 'Graveyard']},
    'blink': {'performs': ['blink', 'Blink / flicker'], 'supports': ['etb_value', 'ETB value', 'ETB payoff']},
}
ROLE_ALIASES = {
    'removal': ['spot_removal', 'Removal'], 'spot_removal': ['spot_removal', 'Removal'], 'wipe': ['wipe', 'Board wipe'],
    'protection': ['protection', 'Protection', 'Indestructible'], 'draw': ['draw', 'Card draw'],
    'ramp': ['ramp', 'Ramp', 'Mana dork', 'Mana rock'], 'fixing': ['fixing', 'Mana fixing'],
    'recursion': ['recursion', 'reanimation', 'Recursion'], 'counterspell': ['counterspell', 'Counterspell'],
    'copy': ['copy', 'Copy'], 'tutor': ['Tutor'], 'closer': ['closer'], 'sac_outlet': ['sac_outlet', 'Sacrifice outlet'],
    'death_payoff': ['death_payoff', 'Death trigger'], 'token_maker': ['token_maker', 'Token maker'],
    'token_multiplier': ['Token multiplier'], 'bounce': ['Bounce', 'Creature bounce'],
}
EVIDENCE_CLASS = {'unverified_inventory_tag': 'inventory_tag_only', 'unverified_tag_only': 'inventory_tag_only',
                  'machine_supported': 'detected_candidate', 'machine_inferred': 'detected_candidate'}
CLASS_RANK = {'reviewed_capability': 0, 'detected_candidate': 1, 'inventory_tag_only': 2}
SHAPE = {'activate': 'activated (repeatable while you can pay)', 'trigger': 'triggered', 'cast': 'one-shot spell',
         'continuous': 'static', 'replacement': 'replacement', 'composite': 'composite'}


def _find_roles(c, role):
    r = role.strip()
    if r.lower() in ROLE_FAMILIES:
        return r.lower(), ROLE_FAMILIES[r.lower()]
    if r.lower() in ROLE_ALIASES:
        return r.lower(), {'performs': ROLE_ALIASES[r.lower()], 'supports': []}
    known = {x[0] for x in c.execute('select distinct capability from capability_claims')}
    hit = next((k for k in known if k.lower() == r.lower()), None)
    if hit:
        return hit, {'performs': [hit], 'supports': []}
    raise LookupError(f'role not known: {role!r}. Families (performs + supports): {sorted(ROLE_FAMILIES)}; roles: '
                      f'{sorted(ROLE_ALIASES)}; or any capability recorded in the KB, e.g. {sorted(known)[:12]} ...')


def _shape(c, name, phrase, type_line=''):
    """How the matched ability works, from the KB contract whose text holds the matched phrase: activated, triggered,
    one-shot, and whether the contract records an unbound condition (Amalia's wipe needs power exactly 20)."""
    if not phrase:
        return None
    for r in c.execute('select contract_id,operation_kind,exact_text,contract_json from current_contracts where card_name=?', (name,)):
        if phrase.lower() in (r['exact_text'] or '').lower():
            unbound = [u for u in json.loads(r['contract_json']).get('unbound') or [] if 'conditional' in u or 'unless' in u]
            spell = any(w in (type_line or '').lower() for w in ('instant', 'sorcery'))
            return {'contract': r['contract_id'], 'kind': 'one-shot spell' if spell else SHAPE.get(r['operation_kind'], r['operation_kind']),
                    'repeatable': r['operation_kind'] == 'activate' and not spell,
                    'conditional': bool(unbound), 'condition_note': '; '.join(unbound) or None, 'text': r['exact_text']}
    return None


def find(c, role, ci=None, free=False, limit=40):
    """Owned cards the KB records as performing (or supporting) a function, with the evidence behind each match. Retrieval,
    not ranking and not a claim of completeness: no match means none detected, not none exist."""
    name, fam = _find_roles(c, role)
    pol = _policy(c)
    reviewed = {(r['card_name'], r['subject_id']) for r in c.execute(
        "select card_name,subject_id from review_overlay where subject_kind='capability_claim' and decision='verified'")}
    sides, excluded = {}, []
    for side in ('performs', 'supports'):
        caps = fam[side]
        if not caps:
            continue
        cards = {}
        for r in c.execute('select cc.*, cd.free, cd.owned_min from capability_claims cc join cards cd using(card_name) '
                           'where cd.owned_min>0 and cc.capability in (%s)' % ','.join('?' * len(caps)), tuple(caps)):
            if r['claim_status'] == 'machine_contradicted':
                excluded.append({'card': r['card_name'], 'capability': r['capability'], 'reason': 'the KB marks this role claim contradicted by Oracle text'})
                continue
            cls = 'reviewed_capability' if any(r['card_name'] == n and r['capability'] in s for n, s in reviewed) \
                else EVIDENCE_CLASS.get(r['claim_status'], 'inventory_tag_only')
            ev = r['evidence_text']
            if ev and ev.startswith('{'):
                ev = json.loads(ev).get('oracle')
            cards.setdefault(r['card_name'], []).append({'capability': r['capability'], 'source': r['source'],
                                                         'claim_status': r['claim_status'], 'class': cls, 'matched_text': ev})
        rows = []
        for n, evs in cards.items():
            row = c.execute('select * from cards where card_name=?', (n,)).fetchone()
            if free and row['free'] <= 0:
                continue
            if ci is not None and not kb.legal_rules(c, row, ci)[0]:
                continue
            best = min(evs, key=lambda e: CLASS_RANK[e['class']])['class']
            phrase = next((e['matched_text'] for e in evs if e['source'] == 'oracle_rule_match' and e['matched_text']), None)
            av = _availability(c, n, pol)
            rows.append({'card': n, 'class': best, 'color_identity': row['color_identity'] or 'C', 'type_line': row['type_line'],
                         'mana_value': row['mana_value'], 'shape': _shape(c, n, phrase, row['type_line']),
                         'evidence': sorted(evs, key=lambda e: (CLASS_RANK[e['class']], e['source'], e['capability'])),
                         'availability': {k: av[k] for k in ('free', 'usable_without_asking', 'usable_by_agreement', 'in_protected_decks')}})
        rows.sort(key=lambda x: (CLASS_RANK[x['class']], bool(x['shape'] and x['shape']['conditional']), x['card']))
        sides[side] = rows
    counts = {s: {'total': len(v), **_count(v, 'class')} for s, v in sides.items()}
    where = ', '.join(x for x in ((f'legal in {ci} color identity' if ci is not None else ''), ('with a free copy' if free else 'owned')) if x)
    claims = []
    for s, v in sides.items():
        verb = 'perform' if s == 'performs' else 'support (pay off)'
        if v:
            claims.append(claim(f"{len(v)} {where} cards are recorded to {verb} {name}: "
                                f"{counts[s].get('detected_candidate', 0)} detected candidates, {counts[s].get('inventory_tag_only', 0)} "
                                f"inventory tags only, {counts[s].get('reviewed_capability', 0)} reviewed.", 'mechanics', 'candidate',
                                evidence=['capability_claims']))
        else:
            claims.append(claim(f'No matching candidates detected that {verb} {name} ({where}). Role detection is incomplete, so this '
                                'does not show that no suitable card exists.', 'mechanics', 'candidate'))
    cond = [x['card'] for v in sides.values() for x in v if x['shape'] and x['shape']['conditional']]
    if cond:
        claims.append(claim(f"{len(cond)} matches rest on an ability whose contract records an unbound condition; read before "
                            f"counting them: {', '.join(cond[:10])}" + (' ...' if len(cond) > 10 else '') + '.', 'mechanics', 'candidate'))
    rel = kb.release(c.execute('pragma database_list').fetchone()[2])
    data = {'role': name, 'families': fam, 'ci': ci, 'free': free, 'counts': counts,
            'performs': sides.get('performs', [])[:limit], 'supports': sides.get('supports', [])[:limit],
            'excluded_contradicted': excluded[:limit],
            'freshness': {'kb_release': rel.get('release'), 'kb_built_utc': rel.get('built_utc'),
                          'inventory_snapshot_modified_utc': rel.get('inventory_snapshot_modified_utc'),
                          **({'inventory_as_of': rel['as_of']} if rel.get('as_of') else {}),
                          'note': 'Card meaning comes from the KB release; ownership and availability come from the inventory '
                                  'snapshot it was built from. Neither date says anything about the other, and neither is the live Sheet.'},
            'evidence_classes': {'reviewed_capability': 'a semantically reviewed capability claim (review overlay)',
                                 'detected_candidate': "an unreviewed role detected from Oracle text by the KB's rule match or the evaluator's patterns (C-012)",
                                 'inventory_tag_only': 'a Collection.Roles tag in the inventory, with no detected text support'},
            'limitations': ['Nonexhaustive: a card the detectors miss does not appear. No match means none detected.',
                            "Roles come from capability_claims (Collection.Roles tags and the evaluator's text patterns), not from DIO contracts (C-012).",
                            'shape comes from the contract whose text holds the matched phrase; it is missing when no contract holds it.']}
    return data, claims
