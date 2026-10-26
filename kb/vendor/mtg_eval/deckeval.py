"""Deck, trade and portfolio queries over the shared card record (pre-kernel deckbuilding layer).

Coverage bands, module contracts on the kernel's three-valued gates, one-slot placement,
transactions with backfill, inventory census and new-deck construction. Numbers marked
ASSUMPTION are heuristics, not calibrated power. Nothing here writes inventory.
"""
import re
from ._kernel import YES, NO, UNKNOWN, gate_and, gate_or
from .semantics import COVERAGE
from .inventory import BASICS, NON_DECK, COLORS, ci_set, notna


# Module contracts: AND over groups, OR within a group (Ontology §1.6 route templates).
MODULES = {
    'aristocrats':     [['token_maker'], ['sac_outlet'], ['death_payoff']],
    'counters':        [['counter_source'], ['counter_payoff', 'counter_multiplier']],
    'artifact_tokens': [['artifact_token'], ['artifact_payoff', 'sac_outlet']],
    'lifegain':        [['lifegain_source'], ['lifegain_payoff']],
    'blink':           [['blink'], ['etb_value']],
    'landfall':        [['land_drop'], ['landfall_payoff']],
    'spellslinger':    [['instant_sorcery'], ['spell_payoff']],
    'graveyard':       [['self_mill'], ['recursion', 'reanimation']],
    'go_wide':         [['token_maker'], ['token_payoff', 'closer']],
}
# ASSUMPTION: casual-Commander coverage targets per 99 (Protocol §2.5 bands by ratio).
TARGETS = {'ramp': 10, 'draw': 10, 'spot_removal': 8, 'wipe': 2, 'protection': 5, 'recursion': 3, 'closer': 4}
BAND_NAMES = ['Absent', 'Fragile', 'Adequate', 'Strong', 'Excessive']
TUTOR = re.compile(r"search your library for (?:a|an|up to \w+) (?!basic)(?![^.]*\bland\b)[^.]*card", re.I)


def band(n, target):
    if not target: return None
    r = n / target
    return 0 if n == 0 else 1 if r < .5 else 2 if r < 1 else 3 if r <= 1.5 else 4


# ---------------------------------------------------------------- card scale
def evaluate_card(inv, name):
    rec = inv.record(name)
    mods = {m: [i for i, g in enumerate(gs) if set(g) & inv.supported(name)] for m, gs in MODULES.items()}
    return {'card': name, 'functions': {f: v['status'] for f, v in rec.items()},
            'supported': sorted(inv.supported(name)),
            'module_groups': {m: v for m, v in mods.items() if v}, 'evidence': rec}


# ---------------------------------------------------------------- deck scale
def deck_assessment(inv, deck=None, cards=None, ci=None, commanders=None):
    """cards: list of names (overlay for hypotheticals); defaults to the recorded deck."""
    names = cards if cards is not None else [n for n, _, _ in inv.decks[deck]]
    ci = ci if ci is not None else inv.deck_ci(deck)
    nonbasic = [n for n in names if n not in BASICS]
    cov = {}
    for f in COVERAGE:
        if f == 'fixing':
            n = sum('fixing' in inv.supported(c) or inv.multicolor_land(c) for c in nonbasic)
            t = 0 if len(ci) < 2 else 6 * (len(ci) - 1)  # ASSUMPTION
        else:
            n = sum(f in inv.supported(c) for c in nonbasic); t = TARGETS.get(f)
        b = band(n, t)
        cov[f] = {'count': n, 'target': t, 'band': b, 'band_name': BAND_NAMES[b] if b is not None else 'not scored'}
    modules = {}
    for m, groups in MODULES.items():
        gstat, gcount, gcards = [], [], []
        for g in groups:
            sup = [c for c in nonbasic if set(g) & inv.supported(c)]
            tag = [c for c in nonbasic if c not in sup and any(inv.record(c).get(f, {}).get('status') == 'tag_only' for f in g)]
            gstat.append(gate_or([YES] * bool(sup) + [UNKNOWN] * bool(tag) + [NO]))
            gcount.append(len(sup)); gcards.append(sup)
        lo = min(gcount)
        maturity = 'absent' if max(gcount) == 0 else 'fragment' if lo == 0 else 'package' if lo < 3 else 'redundant'
        modules[m] = {'status': gate_and(gstat), 'maturity': maturity, 'group_counts': gcount,
                      'bottleneck_group': groups[gcount.index(lo)], 'group_cards': gcards}
    qa = [{'card': c, 'function': f, 'finding': 'tag without Oracle support' if v['status'] == 'tag_only' else 'tag/rule contradicted by hand label'}
          for c in nonbasic for f, v in inv.record(c).items() if v['status'] in ('tag_only', 'contradicted') and f in COVERAGE]
    cmd = commanders if commanders is not None else inv.commanders(deck)
    cf = set().union(*[inv.supported(c) for c in cmd]) if cmd else set()
    # plan modules: the commander fills a group, or the deck already runs it as a package
    plan = sorted(m for m, v in modules.items() if any(set(g) & cf for g in MODULES[m]) or v['maturity'] in ('package', 'redundant'))
    return {'deck': deck, 'size': len(names), 'coverage': cov, 'modules': modules, 'plan_modules': plan, 'qa': qa}


def floor_breaches(before, after):
    """ASSUMED floor: an already-thin function (band <= 2) must not lose a band;
    no function may drop to Absent/Fragile; a package-or-better module must stay a package."""
    out = []
    for f, b in before['coverage'].items():
        a = after['coverage'][f]
        if b['band'] is None: continue
        if a['band'] < b['band'] and (b['band'] <= 2 or a['band'] <= 1):
            out.append(f"{f} {b['band_name']}->{a['band_name']} ({b['count']}->{a['count']})")
    rank = ['absent', 'fragment', 'package', 'redundant']
    for m, b in before['modules'].items():
        a = after['modules'][m]
        if rank.index(b['maturity']) >= 2 and rank.index(a['maturity']) < 2:
            out.append(f"module {m} {b['maturity']}->{a['maturity']}")
    return out


def diff(before, after):
    gains, losses = [], []
    for f, b in before['coverage'].items():
        a = after['coverage'][f]
        if b['band'] is None or a['band'] == b['band']: continue
        if min(a['band'], b['band']) >= 3: continue  # Strong<->Excessive is over-supply, not value
        (gains if a['band'] > b['band'] else losses).append(f"{f} {b['band_name']}->{a['band_name']}")
    rank = ['absent', 'fragment', 'package', 'redundant']
    for m, b in before['modules'].items():
        a = after['modules'][m]
        if m not in before['plan_modules']: continue  # incidental, not the deck's plan
        if a['maturity'] != b['maturity']:
            (gains if rank.index(a['maturity']) > rank.index(b['maturity']) else losses).append(f"module {m} {b['maturity']}->{a['maturity']}")
        elif a['group_counts'] != b['group_counts'] and b['maturity'] in ('fragment', 'package'):
            if min(a['group_counts']) > min(b['group_counts']): gains.append(f"module {m} bottleneck {b['bottleneck_group']} {min(b['group_counts'])}->{min(a['group_counts'])}")
            elif min(a['group_counts']) < min(b['group_counts']): losses.append(f"module {m} bottleneck {min(b['group_counts'])}->{min(a['group_counts'])}")
    return gains, losses


def displaced_slot(inv, deck, assess, protect=()):
    """Cheapest cut by the record: no floor breach, fewest band/module losses, then the
    lowest scarcity cost (sum of 1/deck-count over its supported functions), then higher MV.
    Cards the record cannot read (no supported function) are never auto-cut: they are
    unpriced, not worthless, and are listed by unpriced_cards() for a human."""
    names = [n for n, _, _ in inv.decks[deck]]
    cnt = {}
    for n in names:
        for f in inv.supported(n): cnt[f] = cnt.get(f, 0) + 1
    best = None
    for n, _, sec in inv.decks[deck]:
        if sec != 'Nonland' or n in protect: continue
        if not inv.supported(n) - {'creature', 'instant_sorcery', 'land'}: continue  # unpriced: the record can't read it
        after = deck_assessment(inv, deck, [x for x in names if x != n])
        g, l = diff(assess, after)
        cost = round(sum(1 / cnt[f] for f in inv.supported(n) if f not in ('creature', 'instant_sorcery', 'land')), 3)
        key = (len(floor_breaches(assess, after)), len(l), cost, -float(inv.cards[n]['Mana Value'] or 0))
        if best is None or key < best[0]: best = (key, n, l)
    return best[1], best[2]


def unpriced_cards(inv, deck):
    return [n for n, _, s in inv.decks[deck] if s == 'Nonland' and not inv.supported(n) - {'creature', 'instant_sorcery', 'land'}]


def place(inv, name, deck, cut=None):
    """One-slot hypothetical: name in, cut out. Returns gains/losses/floor."""
    names = [n for n, _, _ in inv.decks[deck]]
    before = deck_assessment(inv, deck)
    if cut is None:  # the cheapest slot depends only on the deck, so it is computed once per deck
        cache = inv.__dict__.setdefault('_cut', {})
        if deck not in cache: cache[deck] = displaced_slot(inv, deck, before)[0]
        cut = cache[deck]
    after = deck_assessment(inv, deck, [n for n in names if n != cut] + [name])
    g, l = diff(before, after)
    return {'deck': deck, 'cut': cut, 'gains': g, 'losses': l, 'floor_breaches': floor_breaches(before, after)}


def card_destinations(inv, name):
    rows = []
    for d in sorted(inv.decks):
        ok, why = inv.legal_in(name, inv.deck_ci(d))
        if name in [n for n, _, _ in inv.decks[d]]: ok, why = False, 'already in this deck'
        elif ok and TUTOR.search(str(inv.cards[name]['Oracle Text'])): ok, why = False, 'nonland tutor (portfolio preference: little to no tutoring)'
        if not ok:
            rows.append({'deck': d, 'verdict': 'not suitable', 'reason': why}); continue
        p = place(inv, name, d)
        n_g = len(p['gains'])
        verdict = 'not suitable' if p['floor_breaches'] else 'strong' if n_g >= 2 and not p['losses'] else 'moderate' if n_g > len(p['losses']) else 'marginal'
        reason = ('breaks floor: ' + '; '.join(p['floor_breaches'])) if p['floor_breaches'] else \
                 ('adds nothing the deck lacks at its current bands' if not n_g else '')
        rows.append({'deck': d, 'verdict': verdict, 'reason': reason, **p})
    order = {'strong': 0, 'moderate': 1, 'marginal': 2, 'not suitable': 3}
    rows.sort(key=lambda r: (order[r['verdict']], -len(r.get('gains', [])), len(r.get('losses', []))))
    custody = 'free copy' if inv.free(name) > 0 else f"no free copy (in {inv.cards[name]['Current Deck(s)']})"
    return {'card': name, 'functions': sorted(inv.supported(name)), 'custody': custody, 'destinations': rows}


# ---------------------------------------------------------------- transactions
def best_backfill(inv, deck, lost_functions, deck_cards, exclude=(), allow_borrow=False):
    """REPLACE: find a card for deck that restores the lost functions. Free pool first."""
    ci = inv.deck_ci(deck); want = set(lost_functions)
    cands = []
    for n, r in inv.cards.items():
        if n in deck_cards or n in exclude or n in BASICS or inv.is_land(n): continue
        if not inv.legal_in(n, ci)[0] or TUTOR.search(str(r['Oracle Text'])): continue
        hit = inv.supported(n) & want
        if not hit: continue
        free = inv.free(n) > 0
        if not free and not allow_borrow: continue
        holders = [d for d in inv.decks if n in [x for x, _, _ in inv.decks[d]]]
        cands.append((-len(hit), not free, float(r['Mana Value'] or 0), n, holders))
    cands.sort()
    return [{'card': c[3], 'restores': sorted(inv.supported(c[3]) & want), 'custody': 'free' if not c[1] else 'held by ' + ', '.join(c[4])}
            for c in cands[:5]]


def evaluate_transaction(inv, moves, backfills=None):
    """moves: [(card, from_deck_or_'free', to_deck, cut_in_to_deck)]. backfills: {deck: card}.
    Returns per-deck before/after, replacement-adjusted loss, floor verdict."""
    state = {d: [n for n, _, _ in inv.decks[d]] for d in inv.decks}
    touched = set()
    for card, src, dst, cut in moves:
        if src != 'free': state[src].remove(card); touched.add(src)
        state[dst] = [n for n in state[dst] if n != cut] + [card]; touched.add(dst)
    for d, c in (backfills or {}).items():
        state[d].append(c); touched.add(d)
    out = {}
    for d in sorted(touched):
        b = deck_assessment(inv, d); a = deck_assessment(inv, d, state[d])
        g, l = diff(b, a)
        out[d] = {'size_before': b['size'], 'size_after': a['size'], 'gains': g, 'losses': l, 'floor_breaches': floor_breaches(b, a)}
    verdict = 'reject' if any(v['floor_breaches'] or v['size_after'] != v['size_before'] for v in out.values()) else 'acceptable proposal'
    return {'moves': moves, 'backfills': backfills or {}, 'decks': out, 'verdict': verdict}


# ---------------------------------------------------------------- portfolio scale
def inventory_assessment(inv):
    allocated = {n for d in inv.decks for n, _, _ in inv.decks[d]}
    supply = {}
    funcs = list(TARGETS) + ['fixing', 'counterspell'] + sorted({f for gs in MODULES.values() for g in gs for f in g})
    for f in dict.fromkeys(funcs):
        hold = [n for n in inv.cards if f in inv.supported(n)]
        supply[f] = {'cards': len(hold), 'free_cards': sum(inv.free(n) > 0 for n in hold), 'in_decks': sum(n in allocated for n in hold)}
    census = {d: {m: v['maturity'] for m, v in deck_assessment(inv, d)['modules'].items() if v['maturity'] != 'absent'} for d in sorted(inv.decks)}
    tag_only = {}
    for n in inv.cards:
        for f, v in inv.record(n).items():
            if v['status'] == 'tag_only': tag_only[f] = tag_only.get(f, 0) + 1
    tagged = {}
    for n in inv.cards:
        for f, v in inv.record(n).items():
            if v['evidence'].get('tag'): tagged[f] = tagged.get(f, 0) + 1
    qa = {f: {'tagged': tagged.get(f, 0), 'tag_without_oracle_support': tag_only.get(f, 0)} for f in sorted(tagged)}
    return {'free_names': sum(inv.free(n) > 0 for n in inv.cards if n not in BASICS), 'role_supply': supply,
            'module_census': census, 'metadata_qa': qa}


def propose_configuration(inv, commanders, n_lands=36, max_nonbasic=None):
    """Build from free, Commander-legal singletons in CI. Complete only when every
    quota and the commander's own module groups are met by Oracle-supported cards."""
    commanders = [commanders] if isinstance(commanders, str) else commanders
    ci = set().union(*[ci_set(inv.cards[c]['Color Identity']) for c in commanders])
    pool = [n for n, r in inv.cards.items() if n not in commanders and n not in BASICS and inv.free(n) > 0
            and inv.legal_in(n, ci)[0] and not TUTOR.search(str(r['Oracle Text']))]
    lands = sorted([n for n in pool if inv.is_land(n) and (ci_set(inv.cards[n]['Produces']) & ci or 'C' in str(inv.cards[n]['Produces']))],
                   key=lambda n: (-len(ci_set(inv.cards[n]['Produces']) & ci), str(inv.cards[n]['ETB Tapped']) == 'Yes', n))
    nb = lands[:max_nonbasic if max_nonbasic is not None else (0 if len(ci) < 2 else 4 + 4 * len(ci))]
    basics = [b for b, c in zip(['Plains', 'Island', 'Swamp', 'Mountain', 'Forest'], COLORS) if c in ci] or ['Wastes']
    spells = [n for n in pool if not inv.is_land(n)]
    cmd_funcs = set().union(*[inv.supported(c) for c in commanders])
    cmd_mods = [m for m, gs in MODULES.items() if any(set(g) & cmd_funcs for g in gs)]
    chosen, why = [], {}
    plan_f = {f for m in cmd_mods for g in MODULES[m] for f in g}
    def take(cands, reason, k, plan_first=False):
        key = lambda n: ((-len(inv.supported(n) & plan_f),) if plan_first else ()) + (-len(inv.supported(n) & set(COVERAGE)), float(inv.cards[n]['Mana Value'] or 0), n)
        for n in sorted(cands, key=key):
            if k <= 0 or len(chosen) >= 99 - n_lands: break
            if n not in chosen: chosen.append(n); why[n] = reason; k -= 1
    for f, t in TARGETS.items():
        have = sum(f in inv.supported(n) for n in chosen)
        take([n for n in spells if f in inv.supported(n)], f, t - have)
    for m in cmd_mods:
        for g in MODULES[m]:
            have = sum(bool(set(g) & inv.supported(n)) for n in chosen)
            take([n for n in spells if set(g) & inv.supported(n)], f'{m}:{"/".join(g)}', 6 - have)
    take([n for n in spells if inv.supported(n) & (set(COVERAGE) | plan_f)], 'filler: commander plan first', 99 - n_lands, plan_first=True)
    nonland_short = 99 - n_lands - len(chosen)
    n_basic = n_lands - len(nb)
    deck = chosen + nb + [basics[i % len(basics)] for i in range(n_basic)]
    a = deck_assessment(inv, None, deck + commanders, ci, commanders)
    needs = [f"{f}: {v['count']}/{v['target']}" for f, v in a['coverage'].items() if v['band'] is not None and v['band'] < 2]
    needs += [f"module {m} is {a['modules'][m]['maturity']}" for m in cmd_mods if a['modules'][m]['maturity'] in ('absent', 'fragment')]
    if nonland_short > 0: needs.append(f'{nonland_short} nonland slots unfilled')
    return {'commanders': commanders, 'ci': ''.join(c for c in COLORS if c in ci), 'pool_size': len(spells),
            'commander_modules': cmd_mods, 'list': deck, 'why': why, 'nonbasic_lands': nb,
            'assessment': a, 'missing_obligations': needs, 'complete': not needs and len(deck) == 99}
