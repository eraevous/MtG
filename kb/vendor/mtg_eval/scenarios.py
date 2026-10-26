"""Named scenarios over the turn engine (0.3.0): one call per deck gives the closing, throughput,
contention, policy and resilience measurements that the deck, module, compare and upgrade
reports print. Every run uses the same shuffles (common random numbers), so differences between
scenarios are paired.

Baseline for comparisons is the 'light blockers' scenario (engine.Game.blockers), because an
unopposed goldfish rewards any wide board; unopposed lethal is reported only as an upper bound."""
import statistics
from . import engine as E

WIPE_TURN = 6
REMOVE_AT = (5, 7)
ATTRITION = (7, 8, 9)  # after the T6 wipe, the commander is removed again after each of the next three turns


def _med(res, key, t):
    return statistics.median(m.get(f'{key}@{t}', 0) for m in res['per_game'])


def _avg(res, key, ts):
    return sum(res['mean'].get(f'{key}@{t}', 0) for t in ts) / len(ts)


def profile(state, games=300, seed=20261018, turns=10):
    prep = E.prepare(state)
    run = lambda **kw: E.run(state, games=games, turns=turns, seed=seed, prepared=prep, **kw)
    base = {'blockers': True}
    R = {'unopposed': run(policy='attack_first')}
    for p in E.POLICIES: R[p] = run(policy=p, scenario=dict(base))
    R['wipe_destroy'] = run(policy='attack_first', scenario={**base, 'wipe': (WIPE_TURN, 'destroy')})
    R['wipe_exile'] = run(policy='attack_first', scenario={**base, 'wipe': (WIPE_TURN, 'exile')})
    R['commander_removed'] = run(policy='attack_first', scenario={**base, 'remove_commander': REMOVE_AT})
    R['no_commander'] = run(policy='attack_first', scenario={**base, 'no_commander': True})
    R['attrition'] = run(policy='attack_first', scenario={**base, 'wipe': (WIPE_TURN, 'destroy'), 'remove_commander': ATTRITION})
    return {'runs': R, 'prepared': prep, 'games': games, 'turns': turns}


def coverage(state, prep):
    cards = sorted({c for c in set(state.library) | set(state.commanders) if not state.inv.is_land(c)})
    full = [c for c in cards if not prep['records'][c]['unread'] and all(a['confidence'] == 'typed' for a in prep['records'][c]['abilities'])]
    part = {c: prep['records'][c]['unread'] for c in cards if c not in full}
    return {'cards': len(cards), 'fully typed': len(full), 'partly typed': part}


def dmg_delta(a, b, t):
    """Paired change in combat + drain damage by turn t, with its standard error."""
    d = [(y.get(f'cum:combat@{t}', 0) + y.get(f'cum:drain@{t}', 0)) - (x.get(f'cum:combat@{t}', 0) + x.get(f'cum:drain@{t}', 0))
         for x, y in zip(a['per_game'], b['per_game'])]
    n = len(d); m = sum(d) / n
    return m, (sum((v - m) ** 2 for v in d) / max(1, n - 1) / n) ** 0.5


def summary(P):
    R = P['runs']; b = R['attack_first']; T = P['turns']
    out = {}
    out['closing'] = {
        'unopposed lethal by T8': E.lethal_by(R['unopposed'], 8), 'unopposed lethal by T10': E.lethal_by(R['unopposed'], 10),
        'light blockers lethal by T10': E.lethal_by(b, 10),
        'light blockers damage by T8 (median)': _med(b, 'cum:combat', 8) + _med(b, 'cum:drain', 8),
        'light blockers damage by T10 (median)': _med(b, 'cum:combat', 10) + _med(b, 'cum:drain', 10)}
    out['throughput'] = {'tokens per turn T4-T8': _avg(b, 'tokens', range(4, 9)), 'cards drawn by T8': b['mean'].get('cum:drawn@8', 0),
                         'spells per turn T4-T8': _avg(b, 'spells', range(4, 9)), 'drain per turn T4-T8': _avg(b, 'drain', range(4, 9)),
                         'board power end T8 (median)': _med(b, 'board:power', 8), 'bodies end T8 (median)': _med(b, 'board:bodies', 8)}
    w = WIPE_TURN
    pre = _med(R['wipe_destroy'], 'board:power', w) or 0
    out['resilience'] = {}
    for k in ('wipe_destroy', 'wipe_exile'):
        r = R[k]
        out['resilience'][k] = {'power before (median)': pre, 'power 3 turns after (median)': _med(r, 'board:power', w + 3),
                                'bodies 3 turns after (median)': _med(r, 'board:bodies', w + 3),
                                'damage by T10 change (paired)': dmg_delta(b, r, T)}
    cr = R['commander_removed']; nc = R['no_commander']
    out['commander'] = {
        'casts by T10 when removed on T5 and T7': sum(cr['mean'].get(f'commander_cast@{t}', 0) for t in range(1, T + 1)),
        'damage by T10 change when removed (paired)': dmg_delta(b, cr, T),
        'damage by T10 change without commander (paired)': dmg_delta(b, nc, T),
        'tokens per turn T4-T8 without commander': _avg(nc, 'tokens', range(4, 9)), 'tokens per turn T4-T8 with': _avg(b, 'tokens', range(4, 9))}
    at = R['attrition']
    out['resilience']['attrition'] = {'power before (median)': pre, 'power 3 turns after (median)': _med(at, 'board:power', w + 3),
                                      'bodies 3 turns after (median)': _med(at, 'board:bodies', w + 3), 'damage by T10 change (paired)': dmg_delta(b, at, T),
                                      'commander casts T7-T10': sum(at['mean'].get(f'commander_cast@{t}', 0) for t in range(7, T + 1))}
    out['throughput']['power per body end T8 (median)'] = statistics.median(m.get('board:power@8', 0) / max(1, m.get('board:bodies@8', 0)) for m in b['per_game'])
    out['policies'] = {p: {'damage by T10 (median)': _med(R[p], 'cum:combat', T) + _med(R[p], 'cum:drain', T),
                           'station charge by T10': sum(R[p]['mean'].get(f'charge@{t}', 0) for t in range(1, T + 1)),
                           'cards by T10': R[p]['mean'].get(f'cum:drawn@{T}', 0),
                           'vs attack_first damage (paired)': dmg_delta(b, R[p], T)} for p in E.POLICIES}
    return out


LEDGER_KEYS = [('bodies at start', 'supply:bodies'), ('can attack', 'supply:attack_ready'), ('with 2+ uses', 'supply:contested'),
               ('attacked', 'body:attack'), ('could attack but spent before combat', 'body:diverted'), ('tapped to station', 'body:station'), ('tapped to crew', 'body:crew'),
               ('spent for mana', 'body:mana'), ('tapped for other costs', 'body:tap_cost'), ('untapped at end', 'end:idle'),
               ('station charge still needed', 'end:station_unmet'), ('spells waiting in hand', 'end:hand_spells')]


def ledger_rows(res, turns=range(3, 9)):
    rows = []
    for label, k in LEDGER_KEYS:
        rows.append({'per turn (mean)': label, **{f'T{t}': round(res['mean'].get(f'{k}@{t}', 0), 2) for t in turns}})
    return rows


def bottlenecks(res, turns=range(3, 9)):
    """Per turn, the claim most often left unmet: station charge still needed while no body was free,
    affordable spells left in hand, or bodies that could attack but were spent elsewhere."""
    out = []
    for t in turns:
        g = res['per_game']; n = len(g)
        station = sum(1 for m in g if m.get(f'end:station_unmet@{t}', 0) > 0 and m.get(f'end:idle@{t}', 0) == 0) / n
        spells = sum(1 for m in g if m.get(f'end:mana_short@{t}', 0) > 0) / n
        diverted = sum(1 for m in g if m.get(f'body:diverted@{t}', 0) > 0) / n
        held = sum(1 for m in g if m.get(f'supply:attack_ready@{t}', 0) > m.get(f'body:attack@{t}', 0) + m.get(f'body:diverted@{t}', 0)) / n
        idle = sum(1 for m in g if m.get(f'end:idle@{t}', 0) > 0) / n
        cand = {'station waiting for bodies': station, 'spells waiting for mana': spells, 'attackers spent before combat': diverted}
        top = max(cand, key=cand.get)
        out.append({'turn': f'T{t}', **{k: f'{100 * v:.0f}%' for k, v in cand.items()}, 'attackers kept home (blockers)': f'{100 * held:.0f}%', 'bodies left idle': f'{100 * idle:.0f}%',
                    'most frequent': top if cand[top] > 0.05 else 'none'})
    return out


def paired_rows(st0, st1, games=300, seed=20261018, turns=10):
    """Engine-level before/after for a substitution (same shuffles; the swapped card sits at the same
    library position). Light blockers baseline and a destroy wipe on T6."""
    p0, p1 = E.prepare(st0), E.prepare(st1)
    b0 = E.run(st0, games=games, turns=turns, seed=seed, prepared=p0, scenario={'blockers': True})
    b1 = E.run(st1, games=games, turns=turns, seed=seed, prepared=p1, scenario={'blockers': True})
    w0 = E.run(st0, games=games, turns=turns, seed=seed, prepared=p0, scenario={'blockers': True, 'wipe': (WIPE_TURN, 'destroy')})
    w1 = E.run(st1, games=games, turns=turns, seed=seed, prepared=p1, scenario={'blockers': True, 'wipe': (WIPE_TURN, 'destroy')})
    rows = []
    def add(label, a, b, key, t, fmt='{:.2f}'):
        m, se = E.paired(a, b, key, t)
        rows.append({'measure': label, 'before (mean)': fmt.format(a['mean'].get(f'{key}@{t}', 0)), 'after (mean)': fmt.format(b['mean'].get(f'{key}@{t}', 0)),
                     'paired change': f'{m:+.2f} (SE {se:.2f})'})
    m, se = dmg_delta(b0, b1, turns)
    rows.append({'measure': f'damage by T{turns} (light blockers)', 'before (mean)': f"{b0['mean'].get(f'cum:combat@{turns}', 0) + b0['mean'].get(f'cum:drain@{turns}', 0):.2f}",
                 'after (mean)': f"{b1['mean'].get(f'cum:combat@{turns}', 0) + b1['mean'].get(f'cum:drain@{turns}', 0):.2f}", 'paired change': f'{m:+.2f} (SE {se:.2f})'})
    add('cards drawn by T8', b0, b1, 'cum:drawn', 8)
    add('board power at end of T8', b0, b1, 'board:power', 8)
    add('tokens made on T6', b0, b1, 'tokens', 6)
    add('bodies spent before combat on T6', b0, b1, 'body:diverted', 6)
    add('station charge still needed at end of T8', b0, b1, 'end:station_unmet', 8)
    add(f'board power 3 turns after a T{WIPE_TURN} destroy wipe', w0, w1, 'board:power', WIPE_TURN + 3)
    return rows, {'base': b0, 'variant': b1}


def engine_delta(st0, st1, games=300, seed=20261018, turns=10, base=None):
    """Short form for upgrade lists: paired damage change by T10 and board power 3 turns after a T6 wipe."""
    if base is None:
        p0 = E.prepare(st0)
        base = (E.run(st0, games=games, turns=turns, seed=seed, prepared=p0, scenario={'blockers': True}),
                E.run(st0, games=games, turns=turns, seed=seed, prepared=p0, scenario={'blockers': True, 'wipe': (WIPE_TURN, 'destroy')}))
    p1 = E.prepare(st1)
    b1 = E.run(st1, games=games, turns=turns, seed=seed, prepared=p1, scenario={'blockers': True})
    w1 = E.run(st1, games=games, turns=turns, seed=seed, prepared=p1, scenario={'blockers': True, 'wipe': (WIPE_TURN, 'destroy')})
    return {'damage': dmg_delta(base[0], b1, turns), 'recovery': E.paired(base[1], w1, 'board:power', WIPE_TURN + 3)}, base
