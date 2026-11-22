"""Add physical composition profiles to supported evaluator reports without vendor edits."""
from functools import wraps
from inspect import signature

from kb.deck_profile import profile, compare_profiles, LIMITS


def install_profiles(ev):
    """Opt-in, idempotent adapter for deck/compare/upgrades/build.

    Build temporarily creates a deck in the existing evaluator. Capture its actual
    physical state before that evaluator removes it, preserving basic multiplicity.
    Like the evaluator's build method, this adapter is not thread safe.
    """
    if getattr(ev, '_composition_profiles_installed', False): return ev
    ev._composition_profiles_installed = True
    from mtgtools.verbs import ROLE_ALIASES

    def snapshot(st):
        return profile(ev.inv, st.library, st.commanders, st.companion, ROLE_ALIASES)

    def attach(res, value):
        res.setdefault('data', {})['composition_profile'] = value
        res['limitations'] = list(res.get('limitations', [])) + LIMITS
        sides = [('current', value)] if 'library_count' in value else (
            [('before', value['before']), ('after', value['after'])] if 'before' in value else [('current', value['current'])])
        rows = []
        for label, p in sides:
            rows.append({'list': label, 'library': p['library_count'], 'status': p['size_status'],
                         'lands (known)': p['types']['land']['count'], 'basic': p['lands']['basic'],
                         'nonbasic': p['lands']['nonbasic'], 'unknown types': p['coverage']['unknown_type_slots'],
                         'creatures (overlap)': p['types']['creature']['count'],
                         'enchantments (overlap)': p['types']['enchantment']['count'],
                         'artifacts (overlap)': p['types']['artifact']['count'],
                         'mean known nonland MV': p['mana_value']['mean_known_nonland']})
        res.setdefault('sections', []).append(('Physical composition (full numeric profile in data.composition_profile)', rows))
        if 'deltas' in value:
            meaningful = [r for r in value['deltas'] if r['delta'] not in (None, 0)]
            res['sections'].append(('Composition deltas (percentages change in percentage points)', meaningful or ['No numeric composition changes.']))
        if any(p['size_status'] == 'incomplete' for _, p in sides):
            res.setdefault('uncertainty', []).append('Composition: incomplete physical list. Odds apply only to supplied slots, not a complete Commander deck.')
        return res

    def wrap(method):
        plain = getattr(ev, method)
        sig = signature(plain)
        @wraps(plain)
        def wrapped(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            values = bound.arguments
            if method == 'build':
                captured = []
                original_state = ev._state
                def capture(deck, swaps=()):
                    state = original_state(deck, swaps)
                    if deck == '__build__': captured.append(state)
                    return state
                ev._state = capture
                try: res = plain(*args, **kwargs)
                finally: ev._state = original_state
                if not captured: raise RuntimeError('build did not expose its physical state')
                return attach(res, snapshot(captured[-1]))
            deck = ev._resolve_deck(values['name'] if method == 'deck' else values['deck'])
            # Materialize iterators once so the original and the profile see identical swaps.
            if method == 'compare':
                values['swaps'] = list(values['swaps'])
            res = plain(*bound.args, **bound.kwargs)
            current = snapshot(ev._state(deck))
            if method == 'deck': return attach(res, current)
            if method == 'compare':
                swaps = [(ev._card(out) if out else None, ev._card(inn) if inn else None) for out, inn in values['swaps']]
                comparison = compare_profiles(current, snapshot(ev._state(deck, swaps)))
                # Each suggested exchange in isolation as well as the complete proposal.
                comparison['individual_changes'] = [dict(out=out, add=inn,
                    **compare_profiles(current, snapshot(ev._state(deck, [(out, inn)])))) for out, inn in swaps]
                return attach(res, comparison)
            proposals, cuts = [], []
            for row in res.get('data', {}).get('upgrades', []):
                cut = row['cut'].rsplit(' (', 1)[0]
                proposals.append(dict(out=cut, add=row['add'],
                    **compare_profiles(current, snapshot(ev._state(deck, [(cut, row['add'])])))))
            for heading, rows in res.get('sections', []):
                if heading == 'Cut order used (lowest measured loss first)':
                    cuts = [dict(out=row['card'], **compare_profiles(current,
                        snapshot(ev._state(deck, [(row['card'], None)])))) for row in rows]
            return attach(res, {'current': current, 'proposals': proposals, 'cuts_only': cuts})
        setattr(ev, method, wrapped)
    for method in ('deck', 'compare', 'upgrades', 'build'):
        if callable(getattr(ev, method, None)): wrap(method)
    return ev
