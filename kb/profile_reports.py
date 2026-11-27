"""Add physical composition profiles to supported evaluator reports without vendor edits."""
from functools import wraps
from inspect import signature

from kb.deck_profile import profile, compare_profiles, LIMITS


def _display_metrics(p):
    """Project existing JSON into labelled numeric rows; never infer missing facts."""
    groups = {}
    def add(group, label, value, unit='cards'):
        groups.setdefault(group, {})[label] = (value, unit)
    for key, label in [('library_count', 'Physical library'), ('commander_count', 'Commanders (outside library)'),
                       ('companion_count', 'Companions (outside deck)')]:
        add('Composition', label, p[key])
    for typ, measure in p['types'].items():
        add('Composition', f'{typ}: known count (types overlap)', measure['count'])
        add('Composition', f'{typ}: percent of library', measure['percent_library'], '%')
    for key, value in p['lands'].items(): add('Composition', f'Lands: {key}', value)
    for key in ('missing_cards', 'unknown_type_slots', 'unknown_nonland_mv_slots'):
        add('Composition', f'Coverage: {key}', p['coverage'][key])
    add('Mana value / curve', 'Known nonland cards', p['mana_value']['known_nonland_count'])
    add('Mana value / curve', 'Mean known nonland mana value', p['mana_value']['mean_known_nonland'], 'MV')
    for mv, count in p['mana_value']['curve'].items(): add('Mana value / curve', f'Nonland MV {mv}', count)
    for scope, demand in p['demand'].items():
        label = 'Library spell demand' if scope == 'library_spells' else 'Commander demand (separate)'
        for color, value in demand['colored'].items(): add(label, f'{color} colored pips', value, 'pips')
        for key, name in [('generic', 'Generic mana'), ('true_colorless', 'True C mana'), ('snow', 'Snow mana')]:
            add(label, name, demand[key], 'mana')
        for symbol, count in demand['conditional_symbols'].items():
            add(label, f'{symbol} conditional, not paid', count, 'symbols')
        add(label, 'Known printed costs', demand['known_cards'])
        add(label, 'Unknown printed costs', demand['unknown_cards'])
    supply = p['supply']
    for kind, count in supply['candidate_sources'].items(): add('Mana supply (candidate evidence)', f'{kind} potential sources', count)
    for color, count in supply['potential_colors'].items():
        add('Mana supply (candidate evidence)', f'{color} potential sources (colors overlap)', count)
    for key in ('unknown_cards', 'unknown_color_slots'): add('Mana supply (candidate evidence)', key, supply[key])
    for hint, count in supply['land_entry_hints'].items(): add('Mana supply (candidate evidence)', f'Land entry hint: {hint}', count)
    for key, value in supply['availability'].items(): add('Mana supply (candidate evidence)', f'Usable availability: {key}', value)
    for role, values in p['roles'].items():
        for key in ('supported_slots', 'unknown_slots'):
            add('Roles (detected, not exhaustive)', f'{role}: {key}', values[key])
        add('Roles (detected, not exhaustive)', f'{role}: percent of library', values['percent_library'], '%')
    windows = {'opening_seven': 'Opening seven (7 seen)',
               'turn3_on_play_skip_first_draw': 'Turn 3 on play, skip first draw (9 seen)',
               'turn3_on_draw_or_multiplayer': 'Turn 3 on draw / multiplayer (10 seen)'}
    for window, values in p['odds'].items():
        group = windows[window] + ' — no mulligan'
        lands = values['land_cards']
        for key, label in [('0_to_1', 'P(0–1 land cards)'), ('2_to_4', 'P(2–4 land cards)'),
                           ('at_least_3', 'P(at least 3 land cards)'), ('at_least_1', 'P(at least 1 land card)')]:
            add(group, label, lands[key] * 100 if lands is not None else None, '%')
        for k in range(values['cards_seen'] + 1):
            add(group, f'P(exactly {k} land cards)', lands['exact_k'][str(k)] * 100 if lands is not None else None, '%')
        for role, prob in values['roles'].items():
            add(group, f'P(at least 1 detected {role} slot)', prob * 100 if prob is not None else None, '%')
    return groups


def _number(value, unit, change=False):
    if value is None: return 'unknown'
    suffix = 'percentage points' if change and unit == '%' else unit
    number = f'{value:+.3f}' if change else f'{value:.3f}'
    if unit in ('cards', 'pips', 'mana', 'symbols'):
        number = f'{value:+g}' if change else f'{value:g}'
    return f'{number} {suffix}'


def composition_sections(value, single_label="Current list"):
    """Human-readable panels over the unchanged composition_profile payload."""
    panels = []
    if 'library_count' in value:
        panels.append((single_label, value, None))
    elif 'before' in value:
        panels.append(('Current vs full proposal', value['before'], value['after']))
        for i, change in enumerate(value.get('individual_changes', []), 1):
            kind = "Individual swap" if change.get("add") else "Standalone cut"
            name = f"{kind} {i}: {change.get('out') or '(no cut)'} -> {change.get('add') or '(no addition)'}"
            panels.append((name, change['before'], change['after']))
    else:
        panels.append(('Current list', value['current'], None))
        for label, key in [('Individual swap', 'proposals'), ('Standalone cut', 'cuts_only')]:
            for i, change in enumerate(value[key], 1):
                name = f"{label} {i}: {change['out']} -> {change.get('add') or '(no addition)'}"
                panels.append((name, change['before'], change['after']))
    sections = []
    for label, before, after in panels:
        sides = [('current' if after is not None else 'list', before)] + ([('proposed', after)] if after is not None else [])
        status = '; '.join(f"{name}: {p['size_status']} ({p['library_count']} library cards)" for name, p in sides)
        notes = [status,
                 'Size complete is not legality or playability. Incomplete-list odds describe only supplied slots.',
                 'No mulligan, selection, extra draws or mill. Seen is not castable, a land drop or mill.',
                 'Types and potential colors overlap. Entry hints are candidate evidence, not opening mana availability.',
                 'Role odds cover detected supported slots only; unknown and undetected capabilities remain unknown.',
                 'Changes in percentages and probabilities are percentage points; unknown changes stay unknown.']
        for name, p in sides:
            if p['optional_faces']:
                notes.append(f"{name}: unresolved optional faces: {', '.join(p['optional_faces'])}; one physical slot per card; affected aggregates unknown.")
        sections.append((f'Physical composition — {label}', notes))
        left, right = _display_metrics(before), _display_metrics(after) if after is not None else {}
        for group in dict.fromkeys([*left, *right]):
            rows = []
            a, b = left.get(group, {}), right.get(group, {})
            for metric in dict.fromkeys([*a, *b]):
                unit = (a.get(metric) or b[metric])[1]
                # Absent sparse count categories (curve bins/symbols/roles) have zero count.
                av, bv = a.get(metric, (0, unit))[0], b.get(metric, (0, unit))[0]
                row = {'measure': metric, 'current' if after is not None else 'list': _number(av, unit)}
                if after is not None:
                    row['proposed'] = _number(bv, unit)
                    row['change'] = _number(None if av is None or bv is None else bv - av, unit, change=True)
                rows.append(row)
            if rows: sections.append((f'{label} — {group}', rows))
    return sections


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

    def attach(res, value, single_label="Current list"):
        res.setdefault('data', {})['composition_profile'] = value
        res['limitations'] = list(res.get('limitations', [])) + LIMITS
        res.setdefault('sections', []).extend(composition_sections(value, single_label))
        sides = [value] if 'library_count' in value else (
            [value['before'], value['after']] if 'before' in value else [value['current']])
        if any(p['size_status'] == 'incomplete' for p in sides):
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
                return attach(res, snapshot(captured[-1]), "Proposed build list")
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
