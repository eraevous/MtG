"""Executable event semantics for hook objects (DIO addendum A1-A3). Offline and deterministic.

An event is a dict:
  {'id': 'permanent.tap' | 'permanent.sacrifice' | 'permanent.dies' | ..., 'actor': 'you' | 'opponent',
   'object': {'types': [...], 'subtypes': [...], 'token': bool, 'controller': 'you' | 'opponent', 'is_observer': bool},
   'reason': 'mana_ability' | 'crew' | 'station' | 'cost' | 'effect' (taps only),
   'mana_ability_cost_has_tap': bool, 'produced': ['G', ...] (taps for mana only), 'batch': int, 'checkpoint': 'payment' | 'resolution'}

derive_facets adds the facet events A1 defines; fires/trigger_count decide whether and how often a hook
(from a contract's trigger group) triggers, with actor, controller and cardinality (A2, A3)."""
import re


def derive_facets(events):
    """A1: permanent.tapped_for_mana is true only when a mana ability of that permanent whose cost includes {T}
    resolves and produces mana (CR 106.12, 106.12a-b, 605). Crew, station, other costs and effects never make it true."""
    out = []
    for e in events:
        out.append(e)
        if e['id'] == 'permanent.tap' and e.get('reason') == 'mana_ability' and e.get('mana_ability_cost_has_tap') and e.get('produced'):
            out.append(dict(e, id='permanent.tapped_for_mana', derived_from='permanent.tap + mana.add'))
    return out


def _filter_ok(filt, obj):
    if not filt: return True
    f = filt.lower()
    words = set(re.findall(r'[a-z]+', f))
    types = {t.lower() for t in obj.get('types', [])} | {t.lower() for t in obj.get('subtypes', [])}
    if 'nontoken' in words and obj.get('token'): return False
    if 'token' in words and 'nontoken' not in words and not obj.get('token'): return False
    nouns = {w.rstrip('s') for w in words} - {'nontoken', 'token', 'other', 'another', 'a', 'an', 'nonland', 'noncreature'}
    if 'nonland' in words and 'land' in types: return False
    if 'noncreature' in words and 'creature' in types: return False
    nouns -= {'permanent'}
    return not nouns or bool(nouns & types)


def fires(hook, e):
    """Does one event satisfy one hook object (observer = the hook's controller, 'you')?"""
    if hook['id'] != e['id']: return False
    q = hook.get('qualifiers', {})
    obj = e.get('object', {})
    if hook.get('subject') == 'this' and not obj.get('is_observer'): return False
    if q.get('actor') == 'you' and e.get('actor') != 'you': return False
    if q.get('actor') == 'opponent' and e.get('actor') != 'opponent': return False
    if q.get('controller') == 'you' and obj.get('controller') != 'you': return False
    if q.get('controller') == 'opponent' and obj.get('controller') != 'opponent': return False
    if q.get('permanent_controller_at_event') == 'same_as_actor' and obj.get('controller') not in (None, e.get('actor')): return False
    if q.get('other') and obj.get('is_observer'): return False
    if q.get('token') is True and not obj.get('token'): return False
    if q.get('token') is False and obj.get('token'): return False
    filt = q.get('object_filter') or (q.get('source_filter') if q.get('source_event') else None)
    if filt and not filt.startswith('enchanted'): return _filter_ok(filt, obj)
    return True


def trigger_count(hook, events):
    """A3: each_object triggers once per matching object; one_or_more once per simultaneous batch."""
    hits = [e for e in derive_facets(events) if fires(hook, e)]
    if hook.get('qualifiers', {}).get('cardinality') == 'one_or_more':
        return len({e.get('batch', i) for i, e in enumerate(hits)})
    return len(hits)


def payment_events(contract, observer_types=('creature',)):
    """Events a contract's cost produces at the payment checkpoint (before the ability resolves; DIO §5.3)."""
    out = []
    for g in contract['initiation']['requirement_groups']:
        if g['class'] != 'cost': continue
        c = g['alternatives'][0]
        if c.get('family') == 'sacrifice':
            obj = {'types': list(observer_types), 'controller': 'you', 'is_observer': c.get('subject') == 'this', 'token': False}
            if c.get('subject') == 'other':
                obj = {'types': [w.rstrip('s') for w in re.findall(r'[a-z]+', c.get('object_filter') or '') if w not in ('another', 'other')],
                       'controller': 'you', 'is_observer': False, 'token': False}
            out.append({'id': 'permanent.sacrifice', 'actor': 'you', 'object': obj, 'checkpoint': 'payment', 'act_time': c.get('act_time')})
            if 'creature' in obj['types']:
                out.append({'id': 'permanent.dies', 'actor': 'you', 'object': obj, 'checkpoint': 'payment', 'act_time': c.get('act_time')})
        elif c.get('family') == 'tap':
            out.append({'id': 'permanent.tap', 'actor': 'you', 'reason': 'cost', 'checkpoint': 'payment', 'act_time': c.get('act_time'),
                        'object': {'types': list(observer_types), 'controller': 'you', 'is_observer': c.get('subject') == 'this'}})
    return out
