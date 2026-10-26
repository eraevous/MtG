"""Regression snapshot: per deck, size, commanders, role source counts and exact access by T7,
and formal module access. Used by tests/test_regression.py and tools/make_expected.py."""
from . import access as A
from . import structure as S


def _engine(st, games=60):
    from . import scenarios as SC
    sm = SC.summary(SC.profile(st, games=games))
    r = lambda x: round(x, 2)
    return {'light blockers damage by T10 (median)': sm['closing']['light blockers damage by T10 (median)'],
            'unopposed lethal by T10': r(sm['closing']['unopposed lethal by T10']),
            'tokens per turn T4-T8': r(sm['throughput']['tokens per turn T4-T8']),
            'cards drawn by T8': r(sm['throughput']['cards drawn by T8']),
            'power 3 turns after destroy wipe (median)': sm['resilience']['wipe_destroy']['power 3 turns after (median)'],
            'damage change without commander': r(sm['commander']['damage by T10 change without commander (paired)'][0])}


def snapshot(ev):
    from .api import VITAL, TYPED
    out = {'sha256': ev.inv.sha256, 'decks': {}}
    for d in sorted(ev.inv.decks):
        st = ev._state(d); acc = ev._access(st, (7,))
        out['decks'][d] = {'size': st.size, 'commanders': st.commanders, 'companion': st.companion,
                           'roles': {r: [acc[r]['k'], acc[r]['T7']] for r in VITAL + TYPED},
                           'modules_T7': A.module_access(st, 7),
                           'structure_flags': [f for f, _ in S.flags(S.measure(ev.inv, st))],
                           'engine': _engine(st)}
    return out


def diff(want, got, path=''):
    """Every difference between two snapshots, one line each. A new export is never accepted automatically."""
    out = []
    if path == '' and want.get('sha256') != got.get('sha256'):
        out.append(f"export differs: expected sha256 {str(want.get('sha256'))[:12]}..., this export {str(got.get('sha256'))[:12]}...")
    if isinstance(want, dict) and isinstance(got, dict):
        for k in sorted(set(want) | set(got), key=str):
            if k == 'sha256' and path == '': continue
            if k not in got: out.append(f'{path}/{k}: missing in this export')
            elif k not in want: out.append(f'{path}/{k}: new in this export')
            else: out += diff(want[k], got[k], f'{path}/{k}')
    elif want != got:
        out.append(f'{path}: {want} -> {got}')
    return out
