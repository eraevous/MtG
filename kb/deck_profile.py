"""Deterministic physical-slot profiles; consumes inventory facts and role records.

No Oracle-text interpretation, simulation, ranking or writes. Typed costs belong to
kb.mana; optional mana production facts belong to current KB contracts. Candidate
production is not a claim of opening availability, castability or land drops.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from math import comb, isfinite
import json

from kb.mana import parse_cost

COLORS = 'WUBRGC'
TYPES = ('land', 'creature', 'enchantment', 'artifact', 'instant', 'sorcery', 'planeswalker', 'battle')
LIMITS = [
    'Physical library slots only; commanders and companions are excluded from draws.',
    'No mulligan, selection, extra draws or mill. Seen is not castable, a land drop, or mill.',
    'Types and potential mana colors overlap; totals need not sum to 100%. Colors are not simultaneously available.',
    'Multi-face rows are not resolved without zone/layout semantics: separate face information is retained; affected aggregates are unknown.',
    'Mana production is candidate KB or labelled inventory-field evidence, not usable mana. ETB hints describe entry only; always-usable, fetch and opening availability remain unknown.',
    'Size complete means 100 physical cards including commanders, not Commander legality or playability.',
]


def exact_k(population, successes, draws, k):
    """Exact hypergeometric probability (Fraction); impossible k has probability zero."""
    if not 0 <= successes <= population or not 0 <= draws <= population:
        raise ValueError('require 0 <= successes, draws <= population')
    if not 0 <= k <= min(successes, draws) or draws - k > population - successes:
        return Fraction(0)
    return Fraction(comb(successes, k) * comb(population - successes, draws - k), comb(population, draws))


def distribution(n, k, draws):
    if draws > n:
        return None  # never silently clamp an opening hand to a tiny/incomplete library
    ps = [exact_k(n, k, draws, i) for i in range(draws + 1)]
    return {'exact_k': {str(i): float(p) for i, p in enumerate(ps)},
            '0_to_1': float(sum(ps[:2])), '2_to_4': float(sum(ps[2:5])),
            'at_least_3': float(sum(ps[3:])), 'at_least_1': float(1 - ps[0])}


def _text(value):
    return '' if value is None or str(value).strip().lower() in ('', 'nan', 'none') else str(value).strip()


def _measure(count, n):
    return {'count': count, 'percent_library': 100 * count / n if n else None}


def _types(row):
    text = _text(row.get('Type Line'))
    if not text or '//' in text:
        return None
    return set(text.split('—', 1)[0].lower().split())


def demand(rows):
    """Strict printed cost demand, not the goldfish's normalized payment heuristic."""
    out = {'colored': dict.fromkeys('WUBRG', 0), 'generic': 0, 'true_colorless': 0,
           'snow': 0, 'conditional_symbols': {}, 'unknown_cards': 0, 'known_cards': 0}
    conditional = Counter()
    for row in rows:
        cost = _text(row.get('Mana Cost')) if row else ''
        # Multi-face rows may keep the joined type line with only the front cost: unresolved.
        if not cost or '//' in cost or '//' in _text(row.get('Type Line')):
            out['unknown_cards'] += 1
            continue
        parsed = parse_cost(cost)
        # Reject arbitrary surrounding text rather than silently parsing a partial cost.
        if not parsed or ''.join(p['symbol'] for p in parsed['pips']) != cost.replace(' ', '') or parsed['unknown'] or any(p['type'] == 'colored' and p['color'] not in tuple('WUBRG') for p in parsed['pips']):
            out['unknown_cards'] += 1
            continue
        out['known_cards'] += 1
        for pip in parsed['pips']:
            kind = pip['type']
            if kind == 'colored': out['colored'][pip['color']] += 1
            elif kind == 'generic': out['generic'] += pip['amount']
            elif kind == 'colorless': out['true_colorless'] += pip['amount']
            elif kind == 'snow': out['snow'] += pip['amount']
            else: conditional[pip['symbol']] += 1
    out['conditional_symbols'] = dict(sorted(conditional.items()))
    out['complete'] = out['unknown_cards'] == 0
    return out


def mana_evidence(inv, name):
    """Read existing typed production; do not re-parse text or use color identity.

    Missing contracts do not prove absence of production. All contract-derived
    availability stays unknown, even when the production colors are explicit.
    """
    row = inv.cards.get(name) or {}
    raw = _text(row.get('Produces'))
    compact = raw.translate(str.maketrans('', '', '{}, /'))
    valid = bool(compact) and set(compact) <= set(COLORS)
    fallback = {'status': 'candidate' if valid else 'unknown', 'basis': 'inventory_field_fallback',
                'verification_state': 'candidate', 'colors': sorted(set(compact)) if valid else [],
                'colors_incomplete': not valid, 'contracts': [], 'produces_field': raw}
    if not hasattr(inv, 'db'):
        return fallback
    rows = inv.db.execute(
        'select k.contract_id, k.contract_json, q.queue_state from current_contracts k '
        'join validation_queue q on q.contract_id=k.contract_id and q.contract_version=k.contract_version '
        'where k.card_name=?', (name,))
    colors, evidence, untyped, excluded = set(), [], False, []
    for cid, raw, state in rows:
        if state in ('quarantined', 'rejected'):
            excluded.append(cid)
            continue
        contract = json.loads(raw)
        for result in (contract.get('result') or {}).get('produces') or []:
            if result.get('id') != 'mana.add' or result.get('granted_to_other_object'): continue
            mana = result.get('mana') or {}
            mode = mana.get('mode')
            if mode in ('fixed', 'colorless'): cs = set(mana.get('symbols') or [])
            elif mode == 'alternatives': cs = {c for alt in mana.get('alternatives', []) for c in alt}
            elif mode == 'combination_of': cs = set(mana.get('colors') or [])
            elif mode in ('any_color', 'any_one_color', 'any_combination'): cs = set('WUBRG')
            else: cs = set()  # chosen/commander/reference-dependent is explicitly unknown
            if not cs or not cs <= set(COLORS): untyped = True
            colors |= cs & set(COLORS)
            evidence.append({'contract': cid, 'source_state': state, 'production': mana})
    if not evidence and not excluded: return fallback
    return {'status': 'candidate' if evidence else 'unknown', 'basis': 'dio_contract',
            'excluded_contracts': excluded,
            'verification_state': 'candidate', 'colors': sorted(colors),
            'colors_incomplete': untyped or not evidence, 'contracts': evidence}


def _role_measure(evidence, n, aliases):
    """Count each side's physical slots; absent role evidence is unknown coverage."""
    supported = uncertain = None
    if evidence is not None and all('quantity' in v and 'roles' in v for v in evidence.values()) and sum(v['quantity'] for v in evidence.values()) == n:
        supported = uncertain = 0
        for entry in evidence.values():
            rec, quantity = entry['roles'], entry['quantity']
            if any(rec.get(r, {}).get('status') == 'supported' for r in aliases):
                supported += quantity
            elif not any(r in rec for r in aliases) or any(rec.get(r, {}).get('status') in ('tag_only', 'contradicted', 'not_in_contract') for r in aliases):
                uncertain += quantity
    return {'supported_slots': supported, 'unknown_slots': uncertain, 'aliases': sorted(aliases),
            'percent_library': 100 * supported / n if n and supported is not None else None}


def _align_roles(before, after):
    """Use a stable compared vocabulary without mutating either caller's snapshot.

    Only omitted roles are computed from that side's own evidence. Explicit null
    metrics/probabilities remain not computed; no other side's coverage is copied.
    """
    before, after = deepcopy(before), deepcopy(after)
    vocabulary = before['roles'].keys() | after['roles'].keys()
    for side, other in ((before, after), (after, before)):
        for role in sorted(vocabulary - side['roles'].keys()):
            aliases = set(other['roles'][role].get('aliases', ())) | {role}
            measure = _role_measure(side.get('card_evidence'), side['library_count'], aliases)
            side['roles'][role] = measure
            for window in side['odds'].values():
                k = measure['supported_slots']
                probability = (distribution(side['library_count'], k, window['cards_seen']) or {}).get('at_least_1') if k is not None else None
                window['roles'].setdefault(role, probability)
    return before, after


def profile(inv, library, commanders=(), companion=(), role_groups=None):
    """One reusable profile for an explicit list of physical slots (multiplicity retained).

    role_groups maps a displayed role to aliases, merged as a union of positions.
    Reports size and data completeness separately; odds for incomplete lists are
    conditional on the supplied list and never labelled full-deck odds.
    """
    library, commanders, companion = list(library), list(commanders), list(companion)
    n = len(library)
    count = Counter(library)
    records, facts, roles, types, mv, curve = {}, {}, {}, Counter(), [], Counter()
    missing, unknown_types, unknown_mv, basic, nonbasic, faces = 0, 0, 0, 0, 0, {}
    spell_rows = []
    supplies, entry_hints = Counter(), Counter()
    color_slots = {c: set() for c in COLORS}
    mana_cache = {}
    for name, quantity in sorted(count.items()):
        row = inv.cards.get(name)
        typ = _types(row) if row is not None else None
        if row is None: missing += quantity
        if typ is None: unknown_types += quantity
        else:
            for t in TYPES:
                if t in typ: types[t] += quantity
            if not typ.intersection(('land', 'creature', 'enchantment', 'artifact')): types['other'] += quantity
            if 'land' in typ:
                if 'basic' in typ: basic += quantity
                else: nonbasic += quantity
                hint = {'No': 'untapped', 'Yes': 'tapped', 'Conditional': 'conditional'}.get(_text(row.get('ETB Tapped')), 'unknown')
                entry_hints[hint] += quantity
        if row and ('//' in _text(row.get('Type Line')) or '//' in _text(row.get('Mana Cost'))):
            faces[name] = {'quantity': quantity, 'type_line': _text(row.get('Type Line')),
                           'mana_cost': _text(row.get('Mana Cost')), 'counted_as_extra_cards': False}
        if typ is None or 'land' not in typ:
            spell_rows.extend([row] * quantity)
            try:
                value = float(row.get('Mana Value')) if row is not None and typ is not None and name not in faces else float('nan')
                if not isfinite(value) or value < 0: raise ValueError()
                mv.extend([value] * quantity)
                curve[str(int(value)) if value.is_integer() else str(value)] += quantity
            except (ValueError, TypeError): unknown_mv += quantity
        rec = inv.record(name) if row is not None else {}
        records[name] = {}
        for role, entry in rec.items():
            ev = dict(entry.get('evidence') or {})
            ev.setdefault('basis', 'human_label' if 'label' in ev else 'text_pattern_fallback')
            ev.setdefault('verification_state', 'candidate')
            records[name][role] = dict(entry, evidence=ev)
        facts[name] = {'quantity': quantity, 'roles': records[name]}
        mana_cache[name] = mana_evidence(inv, name)
        facts[name]['mana'] = dict(mana_cache[name], etb_tapped_field=_text(row.get('ETB Tapped')) if row else '')
        if mana_cache[name]['status'] == 'candidate':
            category = ('land' if typ and 'land' in typ else 'dork' if typ and 'creature' in typ
                        else 'rock' if typ and 'artifact' in typ else 'other')
            supplies[category] += quantity
        else: supplies['unknown_cards'] += quantity
    all_roles = set(role_groups or {}) | {r for rec in records.values() for r in rec}
    for role in sorted(all_roles):
        aliases = set((role_groups or {}).get(role, [])) | {role}
        roles[role] = _role_measure(facts, n, aliases)
    for i, name in enumerate(library):
        for c in mana_cache[name]['colors']: color_slots[c].add(i)
    complete = n + len(commanders) == 100 and len(commanders) in (1, 2)
    odds = {}
    for window, draws in [('opening_seven', 7), ('turn3_on_play_skip_first_draw', 9), ('turn3_on_draw_or_multiplayer', 10)]:
        odds[window] = {'cards_seen': draws,
            'land_cards': distribution(n, types['land'], draws) if not unknown_types else None,
            'roles': {r: (distribution(n, v['supported_slots'], draws) or {}).get('at_least_1') for r, v in roles.items()}}
    return {'schema': 'deck-profile-0.1', 'grade': 'exploratory',
            'input_basis': 'existing inventory row fields and inv.record; no refresh',
            'role_source': dict(getattr(inv, 'role_source', {'basis': 'labelled text_pattern_fallback'})),
            'library_count': n, 'commander_count': len(commanders), 'companion_count': len(companion),
            'size_status': 'size_complete' if complete else 'incomplete',
            'odds_scope': 'supplied_library' if complete else 'incomplete_supplied_list_only',
            'coverage': {'missing_cards': missing, 'unknown_type_slots': unknown_types,
                         'unknown_nonland_mv_slots': unknown_mv, 'role_absence_is_not_verified': True},
            'types': {t: _measure(types[t], n) for t in (*TYPES, 'other')},
            'lands': {'basic': basic, 'nonbasic': nonbasic, 'unknown_type_slots': unknown_types},
            'mana_value': {'known_nonland_count': len(mv), 'mean_known_nonland': sum(mv) / len(mv) if mv else None,
                           'curve': dict(sorted(curve.items()))},
            'optional_faces': faces,
            'demand': {'library_spells': demand(spell_rows), 'commanders': demand([inv.cards.get(c) for c in commanders])},
            'supply': {'candidate_sources': {k: supplies[k] for k in ('land', 'rock', 'dork', 'other')},
                       'unknown_cards': supplies['unknown_cards'],
                       'potential_colors': {c: len(pos) for c, pos in color_slots.items()},
                       'unknown_color_slots': sum(mana_cache[x].get('colors_incomplete', True) for x in library),
                       'land_entry_hints': {k: entry_hints[k] for k in ('untapped', 'tapped', 'conditional', 'unknown')},
                       'land_entry_basis': 'inventory ETB Tapped field; candidate hint, not mana availability',
                       'availability': dict.fromkeys(('always', 'tapped', 'conditional', 'fetch', 'opening_usable_sources'))},
            'roles': roles, 'odds': odds, 'card_evidence': facts, 'limitations': list(LIMITS)}


def compare_profiles(before, after):
    """Numeric leaf deltas with units implied by their path; unknown stays null.

    Missing sparse count categories mean zero (e.g. a curve bin lost).
    Roles first align to a shared vocabulary using independent per-side evidence.
    Coverage, state and evidence stay on both full profiles, never subtracted.
    """
    before, after = _align_roles(before, after)
    roots = ('library_count', 'commander_count', 'companion_count', 'types', 'lands',
             'mana_value', 'demand', 'supply', 'roles', 'odds')
    changes = []
    def walk(a, b, path):
        if a is None or b is None:
            changes.append({'metric': '.'.join(path), 'before': a, 'after': b, 'delta': None})
        elif isinstance(a, dict) or isinstance(b, dict):
            aa, bb = a if isinstance(a, dict) else {}, b if isinstance(b, dict) else {}
            for k in sorted(aa.keys() | bb.keys()): walk(aa.get(k, 0), bb.get(k, 0), path + [k])
        elif type(a) in (int, float) and type(b) in (int, float):
            changes.append({'metric': '.'.join(path), 'before': a, 'after': b, 'delta': b - a})
    for root in roots: walk(before[root], after[root], [root])
    return {'before': before, 'after': after, 'deltas': changes}
