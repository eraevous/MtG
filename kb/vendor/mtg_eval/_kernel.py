#!/usr/bin/env python3
"""MTG semantic kernel spike v0.1.

Compatibility target: MTG-DIO 3.1.1 + 2026-10-09 addendum.
Deliberately NOT a rules engine, a parser, or a deck evaluator.

Reads scenario JSON containing DIO-like operations and qualified event/context
facts, applies AND-of-OR gates with three-valued logic, computes optional
amplifiers, and reports which evidence satisfied each gate.

Run: python mtg_semantic_kernel_v0_1.py MTG_Semantic_Kernel_Cases_v0.1.json
"""
from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

YES, NO, UNKNOWN = 'satisfied', 'failed', 'unknown'

# Canonical event vocabulary. A facet is the SAME event plus a required property.
# An implication represents an entailed consequence, not a synonymous hook.
FACETS = {
    'creature.enters_battlefield': ('battlefield.enter', {'types': ['creature']}),
    'artifact.enters_battlefield': ('battlefield.enter', {'types': ['artifact']}),
    'land.enters_battlefield': ('battlefield.enter', {'types': ['land']}),
    'token.enters_battlefield': ('battlefield.enter', {'token': True}),
    'card.milled': ('card.mill', {}),
    'permanent.dies': ('permanent.dies', {}),
}
# Step aliases are scoped to a STEP BEGIN event, not to arbitrary combat timing.
STEP_ALIASES = {'combat': 'begin_combat', 'beginning_of_combat': 'begin_combat',
                'begin_combat': 'begin_combat', 'end': 'end_step'}
# Per-edge conditions matter: dying requires a graveyard destination; leaving does not.
# These are rules-level entailments of *actual completed* events, not hypothetical
# actions that may fail or get replaced.
EVENT_IMPLICATIONS = {
    'permanent.dies': (('battlefield.leave', 'always'), ('graveyard.enter', 'always')),
    'token.create': (('battlefield.enter', 'positive_quantity'),),
    'card.return_to_battlefield': (('battlefield.enter', 'always'),),
    'permanent.sacrifice': (('battlefield.leave', 'always'), ('permanent.dies', 'to_graveyard')),
    'permanent.destroy': (('battlefield.leave', 'destroy_completed'), ('permanent.dies', 'to_graveyard')),
    'battlefield.leave': (('permanent.dies', 'to_graveyard'),),
    'graveyard.enter': (('permanent.dies', 'from_battlefield'), ('battlefield.leave', 'from_battlefield')),
    'card.discard': (('graveyard.enter', 'to_graveyard'),),
    'card.mill': (('graveyard.enter', 'to_graveyard'),),
}
COLLECTION_QUALIFIERS = {'types', 'subtypes', 'supertypes', 'colors', 'keywords'}
STRING_QUALIFIERS = {'controller', 'owner', 'caster', 'player', 'to_zone', 'from_zone',
                     'zone', 'step', 'active_player', 'source_card', 'name'}
# Values below use case-insensitive rules vocabulary; opaque identities never do.
CASE_SENSITIVE_FIELDS = {'object_id', 'previous_object_id', 'event_id', 'turn_id',
                         'source_object_id', 'derived_from'}
COLOR_CODES = {'white':'w','blue':'u','black':'b','red':'r','green':'g'}


def normalize_hook(hook: str) -> tuple[str, dict[str, Any]]:
    return FACETS.get(hook, (hook, {}))


def gate_and(results: list[str]) -> str:
    if NO in results:
        return NO
    if UNKNOWN in results:
        return UNKNOWN
    return YES


def gate_or(results: list[str]) -> str:
    if YES in results:
        return YES
    if UNKNOWN in results:
        return UNKNOWN
    return NO


def merge_predicates(a: dict, b: dict) -> dict | None:
    """Merge constraints from a narrow facet and a listener, if compatible."""
    result = dict(a)
    for key, value in b.items():
        if key == 'types':
            base_types = _tokens(result.get(key, []))
            extra_types = _tokens(value)
            if base_types is None or extra_types is None:
                return None
            result[key] = sorted(base_types | extra_types)
        elif key in result and result[key] != value:
            return None
        else:
            result[key] = value
    return result


def _type_options(value):
    """Possible sets of card *types* for each unresolved face.

    An explicit observed face should instead supply its active `types`.
    Never interpret words beyond a subtype dash as card types.
    """
    if isinstance(value, (list,tuple,set)):
        if not all(isinstance(x,str) for x in value): return None
        # Structured lists also accept accidentally combined type-line elements.
        items = list(value)
    elif isinstance(value,str):
        items = [value]
    else:
        return None
    alternatives = [set()]
    for raw in items:
        segments = raw.split('//')
        face_options = []
        for part in segments:
            main = re.split(r"\s+[—–-]\s+", part.strip(), maxsplit=1)[0]
            face_options.append(set(t.casefold() for t in re.findall(r"[\w-]+",main)))
        if any(not opt for opt in face_options): return None
        alternatives = [a|b for a in alternatives for b in face_options]
    return alternatives


def _tokens(value):
    """Exact normalized membership tokens, or None for ambiguous multi-face types."""
    options = _type_options(value)
    if options is None or len(options)!=1: return None
    return options[0]


def _other_tokens(value, key):
    """Typed set membership. No whitespace splitting for multi-word keywords/subtypes."""
    if isinstance(value, str): values=[value]
    elif isinstance(value, (list,tuple,set)) and all(isinstance(x,str) for x in value):
        values=list(value)
    else: return None
    result=set()
    for v in values:
        for token in v.split(','):
            token=token.strip().casefold()
            if not token: continue
            if key=='colors': token=COLOR_CODES.get(token,token)
            result.add(token)
    return result


def _membership(observed, required, key):
    if key=='types':
        possible=_type_options(observed)
        expected=_tokens(required)
        if possible is None or expected is None: return UNKNOWN
        matches=[expected.issubset(x) for x in possible]
        return YES if all(matches) else NO if not any(matches) else UNKNOWN
    actual=_other_tokens(observed,key); expected=_other_tokens(required,key)
    return UNKNOWN if actual is None or expected is None else YES if expected.issubset(actual) else NO


def _step(value):
    if not isinstance(value,str): return value
    return STEP_ALIASES.get(value.casefold(), value.casefold())


def _counter_kind(value):
    """Canonicalize a verified notation alias, preserving all other values."""
    if not isinstance(value,str): return value
    alias={'1_1':'+1/+1', '+1/+1':'+1/+1'}
    return alias.get(value.strip().casefold(),value.strip().casefold())


def match_properties(known: dict, required: dict, source_object_id=None) -> str:
    checks: list[str] = []
    for key, expected in required.items():
        if key=='self':
            # Both self and another compare GAME-OBJECT IDs, not card names.
            # Unknown identity can never prove an 'other' predicate.
            observed_id=known.get('object_id')
            if type(expected) is not bool or observed_id is None or source_object_id is None:
                checks.append(UNKNOWN)
            elif expected:
                checks.append(YES if observed_id==source_object_id else NO)
            else:
                checks.append(YES if observed_id!=source_object_id else NO)
        elif key not in known or known[key] is None or expected is None:
            checks.append(UNKNOWN)
        elif key in COLLECTION_QUALIFIERS:
            checks.append(_membership(known[key],expected,key))
        elif key=='counter_kind':
            checks.append(YES if _counter_kind(known[key])==_counter_kind(expected) else NO)
        elif key in STRING_QUALIFIERS and isinstance(known[key],str) and isinstance(expected,str):
            checks.append(YES if known[key].casefold()==expected.casefold() else NO)
        elif (type(known[key]) is bool) != (type(expected) is bool):
            checks.append(UNKNOWN)
        else:
            checks.append(YES if known[key]==expected else NO)
    result=gate_and(checks)
    if result==NO and 'keywords' in required and known.get('keywords_complete') is False:
        # Partial keyword extraction can prove presence but cannot prove absence.
        without={k:v for k,v in required.items() if k!='keywords'}
        other=match_properties(known,without,source_object_id) if without else YES
        if other!=NO:return UNKNOWN
    return result


def _edge_gate(condition, known):
    """Three-valued entailment; a failed edge need not invalidate a different path."""
    if condition=='always': return YES
    if condition=='positive_quantity':
        amount=known.get('quantity',None)
        if amount is None: return UNKNOWN  # quantity unrecorded; not proof of creation
        interval=_quantity_interval(amount)
        if interval is None:return UNKNOWN
        low,high=interval
        return YES if low>0 else NO if high==0 else UNKNOWN
    if condition=='from_battlefield':
        origin=known.get('from_zone')
        return UNKNOWN if origin is None or not isinstance(origin,str) else YES if origin.casefold()=='battlefield' else NO
    if condition in ('to_graveyard','destroy_completed'):
        destination=known.get('to_zone')
        if destination is None:
            return UNKNOWN
        if not isinstance(destination,str): return UNKNOWN
        if condition=='destroy_completed':
            zone=destination.casefold()
            return YES if zone in {'graveyard','exile','hand','library','command','stack'} else NO if zone=='battlefield' else UNKNOWN
        return YES if destination.casefold()=='graveyard' else NO
    return UNKNOWN


def _implied_match(observed_name, requested_name, known):
    """Transitive qualified implication, with three-valued per-edge evidence.

    Return YES if any established route exists, UNKNOWN if a route could hold,
    else NO. Visited states bound cycles (leave <-> dies).
    """
    if observed_name==requested_name: return YES
    # Track possible path certainty; a known YES dominates an unresolved path.
    pending=[(observed_name,YES)]
    visited=set()
    possible=False
    while pending:
        current,status=pending.pop()
        if (current,status) in visited: continue
        visited.add((current,status))
        for target,condition in EVENT_IMPLICATIONS.get(current,()):
            edge=_edge_gate(condition,known)
            if edge==NO: continue
            new=gate_and([status,edge])
            if target==requested_name:
                if new==YES: return YES
                possible=True
            else: pending.append((target,new))
    return UNKNOWN if possible else NO


# Event names entail structural facts even when the observation omitted them.
# These are facts of completed events, not of attempted actions.
EVENT_INTRINSICS = {
    'permanent.dies': {'from_zone':'battlefield', 'to_zone':'graveyard'},
    'battlefield.leave': {'from_zone':'battlefield'},
    'battlefield.enter': {'to_zone':'battlefield'},
    'graveyard.enter': {'to_zone':'graveyard'},
    'permanent.sacrifice': {'from_zone':'battlefield'},
    'card.return_to_battlefield': {'to_zone':'battlefield'},
}

def _enrich_facts(known, additions):
    result=dict(known)
    for key,value in additions.items():
        if key in result and match_properties({key:result[key]},{key:value})!=YES:
            return None
        result[key]=value
    return result


def _quantity_interval(amount):
    """Known nonnegative integral event multiplicity; None high = unbounded."""
    if type(amount) is int and amount>=0: return amount,amount
    if (hasattr(amount,'low') and hasattr(amount,'high') and
        type(amount.low) in (int,float) and amount.low>=0 and
        int(amount.low)==amount.low and
        (amount.high is None or
         (type(amount.high) in (int,float) and amount.high>=amount.low and int(amount.high)==amount.high))):
        return int(amount.low), (int(amount.high) if amount.high is not None else None)
    return None


def one_event_match(fact: dict, alternative: dict, context: dict | None=None) -> str:
    """Match actual event hooks and qualified, conditional implications.

    `where` on an *observation* is a fact; `where` on a listener is a filter.
    Derived hooks do not manufacture a second event ID.
    """
    if not isinstance(fact,dict) or not isinstance(fact.get('hook'),str):
        return UNKNOWN
    observed_name, observed_facet=normalize_hook(fact['hook'])
    if not isinstance(alternative,dict) or not isinstance(alternative.get('hook'),str):
        return UNKNOWN
    requested_name, requested_facet=normalize_hook(alternative['hook'])
    requested=merge_predicates(requested_facet, alternative.get('where',{}))
    if requested is None: return NO
    if (requested_name=='timing.step_begin' and isinstance(requested.get('active_player'),str)
        and requested['active_player'].casefold()=='each'):
        # 'at the beginning of EACH end step' has no controller restriction.
        # 'each' was produced as a spurious active_player by the converter.
        requested.pop('active_player')
    snap=alternative.get('snapshot','event')
    evidence=fact.get('snapshots') or {}
    if not isinstance(evidence,dict): return UNKNOWN
    snapshot=evidence.get(snap,{})
    if not isinstance(snapshot,dict): return UNKNOWN
    supplied_where=fact.get('where',{})
    if not isinstance(supplied_where,dict): return UNKNOWN
    # Contradiction across observation fields is unresolved evidence, not failure.
    known=dict(observed_facet)
    for group in (supplied_where,snapshot):
        for key,val in group.items():
            if key in known and match_properties({key:val},{key:known[key]})!=YES:
                return UNKNOWN
            known[key]=val
    known=_enrich_facts(known, EVENT_INTRINSICS.get(observed_name,{}))
    if known is None: return UNKNOWN
    if observed_name=='timing.step_begin' and isinstance(known.get('step'),str):
        known['step']=_step(known['step'])
    if requested_name=='timing.step_begin' and isinstance(requested.get('step'),str):
        requested['step']=_step(requested['step'])
    implication=(UNKNOWN if observed_name=='projection.unknown' and fact.get('status')=='unknown'
                 else _implied_match(observed_name,requested_name,known))
    if implication==NO: return NO
    if implication==YES:
        known=_enrich_facts(known, EVENT_INTRINSICS.get(requested_name,{}))
        if known is None: return UNKNOWN
    # An observed token-creation record must denote a nonzero creation; a
    # missing or zero quantity cannot certify a Rosie's-style per-token trigger.
    if observed_name=='token.create' and requested_name=='token.create':
        gate=_edge_gate('positive_quantity',known)
        if gate!=YES:
            return NO if gate==NO and known.get('quantity') not in (0, None) else UNKNOWN
    # Derived battlefield entries inherit token / card characteristics.
    if observed_name=='token.create' and requested_name=='battlefield.enter':
        if 'token' in known and known['token'] is not True: return UNKNOWN
        known['token']=True
    if observed_name=='card.return_to_battlefield' and requested_name=='battlefield.enter':
        pass
    # Derived dies implies the entity left the battlefield as a creature.
    # Explicit event object types supply last-known characteristics.
    source_id=(context or {}).get('source_object_id') if isinstance(context,dict) else None
    qualifiers=match_properties(known,requested,source_object_id=source_id)
    if qualifiers==NO: return NO
    if fact.get('status')=='unknown': return UNKNOWN
    return gate_and([implication,qualifiers])


def _event_quantity(event, target_hook):
    """Known multiplicity, or None if the count cannot be proven."""
    observed,_=normalize_hook(event.get('hook',''))
    target,_=normalize_hook(target_hook)
    if observed=='token.create' and target in ('battlefield.enter','token.create'):
        snap=event.get('snapshots',{}).get('event',{})
        quantity=snap.get('quantity') if isinstance(snap,dict) else None
        interval=_quantity_interval(quantity)
        return interval[0] if interval and interval[0]==interval[1] else None
    return 1


def matched_occurrences(events, alternatives):
    """Count causal occurrences, not records, using scoped uncertainty.

    A complete, compatible per-token expansion replaces a batch. Incomplete,
    contradictory or cardinality-unknown expansion *cannot* establish an exact
    count. A conflicting batch only affects listeners that it might match.
    """
    alternatives=[a for a in alternatives if isinstance(a,dict) and a.get('kind')=='event']
    entry_requested=any(normalize_hook(a.get('hook',''))[0]=='battlefield.enter' for a in alternatives)
    creation_requested=any(normalize_hook(a.get('hook',''))[0]=='token.create' for a in alternatives)
    batch_listener=(creation_requested and all(a.get('occurrence_mode')=='per_batch' for a in alternatives))
    batches={}
    for i,e in enumerate(events):
        if isinstance(e,dict) and normalize_hook(e.get('hook',''))[0]=='token.create' and e.get('event_id') is not None:
            batches[e['event_id']]=e
    children={}
    for item in events:
        if (not isinstance(item,dict) or
            normalize_hook(item.get('hook',''))[0]!='battlefield.enter' or
            not isinstance(item.get('derived_from'),str)): continue
        snap=item.get('snapshots',{}).get('event',{})
        if (isinstance(snap,dict) and snap.get('token') is True and
            item.get('derived_from') in batches):
            children.setdefault(item['derived_from'],[]).append(item)

    replaced=set()
    uncertain_roots=set()
    if entry_requested:
        for identifier, descendants in children.items():
            batch=batches[identifier]
            quantity=_event_quantity(batch,'battlefield.enter')
            child_ids={d.get('event_id') for d in descendants}
            base=(batch.get('snapshots') or {}).get('event',{})
            compatible=isinstance(base,dict) and len(child_ids)==len(descendants)
            if compatible:
                for descendant in descendants:
                    detail=(descendant.get('snapshots') or {}).get('event',{})
                    if not isinstance(detail,dict): compatible=False; break
                    expected={k:v for k,v in base.items() if k in
                              ('types','subtypes','supertypes','colors','controller','token') and v is not None}
                    if match_properties(detail,expected)!=YES:
                        compatible=False; break
            # A complete, compatible child expansion supersedes its parent.
            # In an inconsistent batch the children remain genuine observations:
            # never erase a matching entry because its parent is contradictory.
            replaced.add(identifier)
            if not (quantity is not None and quantity==len(descendants) and compatible):
                uncertain_roots.add(identifier)

    per_id={}; conflicts=set(); seen={}
    for index,event in enumerate(events):
        if not isinstance(event,dict):continue
        original,_=normalize_hook(event.get('hook',''))
        root_id=event.get('event_id',f'item_{index}')
        if batch_listener and original=='token.create':
            root_id=('batch',event.get('batch_id',root_id))
        if entry_requested and original=='token.create' and root_id in replaced:
            continue  # children are individual, already-observed entries
        states=[one_event_match(event,alt) for alt in alternatives]
        state=gate_or(states) if states else NO
        weight=1
        if original=='token.create' and (entry_requested or creation_requested):
            weight=(1 if batch_listener else _event_quantity(event,'battlefield.enter' if entry_requested else 'token.create'))
            if weight==0:state=UNKNOWN  # an observed zero-token creation is contradictory evidence
        # Different snapshots with the same ID can never be treated as one
        # fully known occurrence. Facet aliases are compatible when shared
        # qualified facts agree; genuinely contradictory facts are not.
        if root_id in seen and not batch_listener:
            prior=seen[root_id]
            if isinstance(prior,dict):
                a=(prior.get('snapshots') or {}).get('event',{})
                b=(event.get('snapshots') or {}).get('event',{})
                if isinstance(a,dict) and isinstance(b,dict):
                    for field in a.keys() & b.keys():
                        if match_properties({field:a[field]},{field:b[field]})!=YES:
                            conflicts.add(root_id);break
                else: conflicts.add(root_id)
        else: seen[root_id]=event
        per_id.setdefault(root_id,[]).append((state,weight))

    # An incomplete or contradictory parent batch can still imply additional
    # entries. Retain all observed children; add uncertainty only where the
    # parent's qualified type could match, or contradictory children already
    # establish that the batch record is inconsistent for this listener.
    for identifier in uncertain_roots:
        batch=batches[identifier]
        parents=gate_or([one_event_match(batch,a) for a in alternatives])
        child_has_match=any(gate_or([one_event_match(child,a) for a in alternatives])==YES
                            for child in children.get(identifier,[]))
        if parents!=NO or child_has_match:
            per_id.setdefault(identifier,[]).append((UNKNOWN,None))
    count=0; uncertain_count=False
    for identifier,rows in per_id.items():
        statuses=[s for s,_ in rows]
        if any(s==YES for s in statuses):
            weight=max((w for s,w in rows if s==YES and w is not None),default=None)
            if (weight is None or identifier in conflicts or
                (identifier in uncertain_roots and entry_requested)):
                uncertain_count=True
            else: count+=weight
        elif any(s==UNKNOWN for s in statuses):
            uncertain_count=True
        elif identifier in conflicts and any(s!=NO for s in statuses):
            uncertain_count=True
    return (None if uncertain_count else count),per_id


def read_path(obj: dict, path: str) -> tuple[bool, Any]:
    value: Any = obj
    for piece in path.split('.'):
        if not isinstance(value, dict) or piece not in value:
            return False, None
        value = value[piece]
    return True, value


def compare(actual: Any, op: str, expected: Any, key: str | None=None) -> str:
    """Tri-valued comparison. None means not known, not a negative answer."""
    if actual is None or expected is None:
        return UNKNOWN
    try:
        if (type(actual) is bool) != (type(expected) is bool): return UNKNOWN
        if op == 'eq':
            if isinstance(actual,str) and isinstance(expected,str): return YES if ((actual.casefold()==expected.casefold()) if key in STRING_QUALIFIERS or key in ('enum','color') else actual==expected) else NO
            return YES if actual == expected else NO
        if op == 'ne':
            if isinstance(actual,str) and isinstance(expected,str): return YES if ((actual.casefold()!=expected.casefold()) if key in STRING_QUALIFIERS or key in ('enum','color') else actual!=expected) else NO
            return YES if actual != expected else NO
        if op == 'gt': return YES if actual > expected else NO
        if op == 'gte': return YES if actual >= expected else NO
        if op == 'lt': return YES if actual < expected else NO
        if op == 'lte': return YES if actual <= expected else NO
        if op == 'contains':
            if not isinstance(expected,str): return UNKNOWN
            if key is None:
                # Preserve older keyless comparisons; recognize only *unambiguous* color tokens.
                known_colors=set(COLOR_CODES)|set(COLOR_CODES.values())
                key = ('colors' if expected.casefold() in known_colors or
                       (isinstance(actual,(list,tuple,set)) and actual and
                        all(isinstance(x,str) and x.casefold() in known_colors for x in actual))
                       else 'types')
            return _membership(actual,[expected],key)
    except (TypeError, ValueError):
        return UNKNOWN
    return UNKNOWN


def canonical_event(hook: str, where: dict | None=None) -> dict:
    """Canonicalize a verified event facet without inventing another event.
    Qualifiers are retained in `where`. Conflicting qualifiers are errors.
    """
    name, facet=normalize_hook(hook)
    user={} if where is None else where
    merged=merge_predicates(facet,user)
    if merged is None:
        raise ValueError(f'Contradictory qualifier for {hook}: {where}')
    if name=='timing.step_begin' and isinstance(merged.get('step'),str):
        merged['step']=_step(merged['step'])
    return {'hook':name,'where':merged}

def eval_alternative(alt: dict, events: list[dict], context: dict, events_complete: bool) -> tuple[str, str]:
    kind = alt.get('kind')
    if kind == 'event':
        count, per_id=matched_occurrences(events,[alt])
        states=[gate_or([s for s,_ in rows]) for rows in per_id.values()]
        result=gate_or(states)
        if result==NO and not events_complete: result=UNKNOWN
        matched=[eid for eid,rows in per_id.items() if any(s==YES for s,_ in rows)]
        return result, f'event {alt["hook"]}: matching_event_ids={matched}, matched_count={count}'
    if kind == 'context':
        present, actual = read_path(context, alt['path'])
        if not present:
            return UNKNOWN, f'context {alt["path"]}: not supplied'
        result = compare(actual, alt.get('op', 'eq'), alt.get('value'),key=alt['path'].split('.')[-1])
        return result, f'context {alt["path"]}: {actual!r} {alt.get("op", "eq")} {alt.get("value")!r}'
    return UNKNOWN, f'unsupported alternative kind={kind!r}'


def count_amplifier(amp: dict, context: dict) -> tuple[Any | None, str]:
    if amp.get('kind') != 'count':
        return None, 'not evaluated: unsupported amplifier kind'
    present, collection = read_path(context, amp['path'])
    if not present:
        return None, 'not evaluated: context value missing'
    if isinstance(collection, int) and not isinstance(collection, bool):
        if collection < 0:
            return None, 'not evaluated: negative count'
        return collection, 'known numeric count'
    if not isinstance(collection, list):
        return None, 'not evaluated: expected list or nonnegative integer'
    predicate = amp.get('where', {})
    if not predicate:
        return len(collection), 'count of supplied set'
    matched = 0
    for item in collection:
        if not isinstance(item, dict):
            return None, 'not evaluated: member has no typed fields'
        results = []
        for field, check in predicate.items():
            if field not in item:
                return None, f'not evaluated: member missing {field}'
            results.append(compare(item[field], check['op'], check['value'],key=field))
        state = gate_and(results)
        if state == UNKNOWN:
            return None, 'not evaluated: member comparison unresolved'
        if state == YES:
            matched += 1
    return matched, 'count of members satisfying predicate'


def evaluate(scenario: dict) -> dict:
    op = scenario['operation']
    events = scenario.get('events', [])  # only observed FINAL events, not proposed/replaced events
    context = scenario.get('context', {})
    events_complete = scenario.get('events_complete', False)
    groups = op.get('initiation', {}).get('requirement_groups', [])
    audit: list[dict] = []
    states: list[str] = []
    for group in groups:
        checks = [eval_alternative(a, events, context, events_complete) for a in group.get('alternatives', [])]
        status = gate_or([r for r, _ in checks]) if checks else UNKNOWN
        states.append(status)
        matched_count,_=matched_occurrences(events,group.get('alternatives',[]))
        occurrence_data=None
        # The reviewed ontology contract is an opt-in EXPLICIT source grammar.
        # Legacy scenario behavior is unchanged until the converter supplies
        # per-alt count modes, object IDs and simultaneity evidence.
        if group.get('occurrence_contract') is True:
            from trigger_occurrences import legal_trigger_occurrences, as_json_bound
            alts=group.get('alternatives', [])
            if alts and all(a.get('kind')=='event' for a in alts):
                listener={
                    'alternatives': alts,
                    'max_per_turn': group.get('max_per_turn'),
                    'intervening_if': group.get('intervening_if', False),
                    'opaque_restrictions': group.get('opaque_restrictions', []),
                    'do_this_only_once_each_turn': group.get('do_this_only_once_each_turn', False),
                }
                bounds=legal_trigger_occurrences(listener,events,context)
                occurrence_data=as_json_bound(bounds)
                lo,hi=bounds
                matched_count=lo if lo==hi else None
                status=YES if lo>0 else NO if hi==0 and events_complete else UNKNOWN
                states[-1]=status
        item={'group': group['id'], 'matched_event_count': matched_count, 'class': group.get('class'),
                      'checkpoint': group.get('checkpoint'), 'status': status,
                      'alternatives': [{'status': r, 'explanation': why} for r, why in checks]}
        if occurrence_data is not None:
            item['legal_trigger_occurrence_bounds']=occurrence_data
            # A resolution-time intervening-if condition gates the THEN, not
            # whether the trigger was already put on the stack.
            lo=occurrence_data['lower']; hi=occurrence_data['upper']
            if group.get('intervening_if'):
                resolution=context.get('intervening_if_at_resolution')
                item['resolution_effect_occurrence_bounds']=(
                    {'lower': 0, 'upper': 0} if resolution is False else
                    {'lower': lo, 'upper': hi} if resolution is True else
                    {'lower': 0, 'upper': hi})
        audit.append(item)
    gate = gate_and(states) if groups else YES
    amplifiers = {}
    for amp in op.get('initiation', {}).get('amplifiers', []):
        number, explanation = count_amplifier(amp, context)
        amplifiers[amp['id']] = {'value': number, 'explanation': explanation}
    derived = {}
    for output in op.get('result', {}).get('produces', []):
        formula = output.get('quantity')
        if formula is None:
            continue
        amp_id = formula.get('amplifier')
        count = amplifiers.get(amp_id, {}).get('value')
        derived[output['hook']] = None if count is None else count * formula.get('per_unit', 1) + formula.get('base', 0)
    return {
        'id': scenario['id'], 'gate_status': gate, 'groups': audit,
        'amplifiers': amplifiers, 'derived_output_quantities': derived,
        'interpretation': ('All represented requirements satisfied; NOT a full Magic legality or strategic-value verdict.'
                           if gate == YES else 'At least one represented requirement fails.' if gate == NO
                           else 'Evidence is insufficient to decide all represented requirements.')
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python mtg_semantic_kernel_v0_1.py cases.json')
    cases = json.loads(Path(sys.argv[1]).read_text())['cases']
    failures = []
    for scenario in cases:
        actual = evaluate(scenario)
        expected = scenario['expect']
        passed = actual['gate_status'] == expected['gate_status']
        for key, expected_value in expected.get('amplifiers', {}).items():
            passed &= actual['amplifiers'].get(key, {}).get('value') == expected_value
        for key, expected_value in expected.get('derived_output_quantities', {}).items():
            passed &= actual['derived_output_quantities'].get(key) == expected_value
        for key, expected_value in expected.get('matched_event_counts', {}).items():
            passed &= next((g['matched_event_count'] for g in actual['groups'] if g['group'] == key), None) == expected_value
        print(('PASS' if passed else 'FAIL'), scenario['id'], actual['gate_status'],
              'expected', expected['gate_status'])
        if not passed:
            failures.append({'id': scenario['id'], 'expected': expected, 'actual': actual})
    print(f'\n{len(cases) - len(failures)}/{len(cases)} cases passed.')
    if failures:
        print(json.dumps(failures, indent=2))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
