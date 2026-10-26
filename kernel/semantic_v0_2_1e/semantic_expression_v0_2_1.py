#!/usr/bin/env python3
"""Small generic expression interpreter for MTG DIO v3.1.1 conformance.

This is an explicitly bounded AST interpreter, not an Oracle parser or Magic rules engine.
Absence of a field is unknown rather than false. This module contains no card names.
"""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from math import inf
from mtg_semantic_kernel_v0_2_1 import YES, NO, UNKNOWN, gate_and, gate_or, one_event_match, compare

MISSING = object()


@dataclass(frozen=True)
class Members:
    certain: tuple
    possible: tuple


@dataclass(frozen=True)
class Bounds:
    # None as high represents an unbounded upper bound, not an unknown value.
    low: float
    high: float | None


def _interval(value):
    if isinstance(value, Bounds):
        return (value.low, inf if value.high is None else value.high)
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        return (value,value)
    return None


def bounded_compare(lhs, operator, rhs):
    a,b=_interval(lhs),_interval(rhs)
    if a is None or b is None:
        return UNKNOWN
    al,ah=a; bl,bh=b
    if operator=='gte':
        return YES if al>=bh else NO if ah<bl else UNKNOWN
    if operator=='gt':
        return YES if al>bh else NO if ah<=bl else UNKNOWN
    if operator=='lte':
        return YES if ah<=bl else NO if al>bh else UNKNOWN
    if operator=='lt':
        return YES if ah<bl else NO if al>=bh else UNKNOWN
    if operator=='eq':
        return YES if al==ah==bl==bh else NO if ah<bl or bh<al else UNKNOWN
    if operator=='ne':
        v=bounded_compare(lhs,'eq',rhs)
        return {YES:NO, NO:YES, UNKNOWN:UNKNOWN}[v]
    return UNKNOWN


def cast_event_identity(member):
    """All supplied cast-provenance facets must agree; contradicting facts are unknown."""
    if member is MISSING or member is None or not isinstance(member,dict): return UNKNOWN
    markers=[]
    event=member.get('event_hook')
    if event is not None:
        if event=='spell.cast': markers.append(YES)
        elif event=='spell.copied': markers.append(NO)
        else: markers.append(UNKNOWN)
    if 'was_cast' in member:
        value=member['was_cast']
        markers.append(YES if value is True else NO if value is False else UNKNOWN)
    origin=member.get('origin')
    if origin is not None:
        if origin in ('cast','cast_copy','cast_from_exile','cast_from_graveyard'): markers.append(YES)
        elif origin in ('stack_copy','copied_on_stack','spell_copy'): markers.append(NO)
        else: markers.append(UNKNOWN)
    # is_copy=True is ambiguous alone: can be copied *card* which was cast, or stack spell copy.
    if member.get('is_copy') is True and not markers: return UNKNOWN
    if member.get('is_copy') is False and not markers: return UNKNOWN
    if not markers: return UNKNOWN
    if YES in markers and NO in markers: return UNKNOWN
    if UNKNOWN in markers: return UNKNOWN
    return markers[0]



def path_value(root: Any, path: str):
    current = root
    for part in path.split('.'):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return MISSING
    return current


def expression(expr: Any, state: dict, item: Any = MISSING):
    if not isinstance(expr, dict) or 'op' not in expr:
        return expr
    op = expr['op']
    if op == 'path':
        return path_value({'state': state, 'item': item}, expr['value'])
    if op == 'get':
        obj = expression(expr['source'], state, item)
        return obj.get(expr['field'], MISSING) if isinstance(obj, dict) else MISSING
    if op == 'filter':
        seq = expression(expr['source'], state, item)
        if not isinstance(seq, (list, Members)): return MISSING
        confirmed = []
        possible = []
        sure = seq if isinstance(seq,list) else seq.certain
        maybe = () if isinstance(seq,list) else seq.possible
        for member in sure:
            result=predicate(expr['where'],state,member)
            if result==YES: confirmed.append(member)
            elif result==UNKNOWN: possible.append(member)
        for member in maybe:
            result=predicate(expr['where'],state,member)
            if result!=NO: possible.append(member)
        return Members(tuple(confirmed),tuple(possible)) if possible else confirmed
    if op == 'count':
        seq = expression(expr['source'], state, item)
        if isinstance(seq, list): return len(seq)
        if isinstance(seq, Members): return Bounds(len(seq.certain),len(seq.certain)+len(seq.possible))
        return MISSING
    if op == 'distinct_count':
        seq = expression(expr['source'], state, item)
        if not isinstance(seq,(list,Members)): return MISSING
        known = seq if isinstance(seq,list) else seq.certain
        uncertain = () if isinstance(seq,list) else seq.possible
        values = [expression(expr['field'],state,member) for member in known]
        definite = {str(v).strip().casefold() for v in values if v is not MISSING and v is not None and str(v).strip()}
        possible_extra = len(uncertain)+sum(v is MISSING or v is None or (isinstance(v,str) and not v.strip()) for v in values)
        return Bounds(len(definite),len(definite)+possible_extra) if possible_extra else len(definite)
    if op == 'max':
        seq = expression(expr['source'],state,item)
        if not isinstance(seq,(list,Members)): return MISSING
        known=seq if isinstance(seq,list) else seq.certain
        possible=() if isinstance(seq,list) else seq.possible
        vals=[expression(expr['field'],state,member) for member in known]
        plausible=[expression(expr['field'],state,member) for member in possible]
        if not known and not possible:return MISSING
        good=lambda v: type(v) in (float,int)
        nums=[v for v in vals if good(v)]
        if any(not good(v) for v in vals): return Bounds(max(nums) if nums else 0,None)
        if not possible: return max(nums) if nums else MISSING
        lo=max(nums) if nums else 0
        if any(not good(v) for v in plausible):return Bounds(lo,None)
        return Bounds(lo,max([lo]+plausible))
    if op == 'select':
        status = predicate(expr['condition'], state, item)
        if status == UNKNOWN: return MISSING
        return expression(expr['then'] if status == YES else expr['else'], state, item)
    if op == 'add':
        vals = [expression(e, state, item) for e in expr['args']]
        return sum(vals) if all(type(v) in (int,float) for v in vals) else MISSING
    return MISSING


def predicate(pred: dict, state: dict, item: Any=MISSING) -> str:
    op = pred.get('op')
    if op == 'all': return gate_and([predicate(p,state,item) for p in pred['args']])
    if op == 'any': return gate_or([predicate(p,state,item) for p in pred['args']])
    if op == 'not':
        v = predicate(pred['arg'],state,item)
        return {YES:NO, NO:YES, UNKNOWN:UNKNOWN}[v]
    if op == 'cmp':
        lhs, rhs = expression(pred['left'],state,item), expression(pred['right'],state,item)
        if lhs is MISSING or rhs is MISSING or lhs is None or rhs is None: return UNKNOWN
        if isinstance(lhs,Bounds) or isinstance(rhs,Bounds):
            return bounded_compare(lhs,pred['compare'],rhs)
        left=pred.get('left')
        key=(left.get('field') if isinstance(left,dict) and left.get('op')=='get' else
             left.get('value','').split('.')[-1] if isinstance(left,dict) and left.get('op')=='path' else None)
        return compare(lhs,pred['compare'],rhs,key=key)
    if op == 'cast_event':
        return cast_event_identity(item)
    return UNKNOWN


def render(template: Any, state: dict):
    if isinstance(template, dict):
        if 'op' in template:
            v = expression(template,state)
            if v is MISSING: return None
            if isinstance(v,Bounds):
                return v.low if v.high==v.low else None
            return v
        return {k:render(v,state) for k,v in template.items()}
    if isinstance(template,list): return [render(v,state) for v in template]
    return template


def _has_null(val):
    if val is None: return True
    if isinstance(val, dict):return any(_has_null(v) for v in val.values())
    if isinstance(val, list):return any(_has_null(v) for v in val)
    return False


def validate_history_snapshots(state: dict) -> bool:
    """When both checkpoints expose same-turn cast ledgers, earlier records persist."""
    trigger=state.get('trigger',{})
    resolution=state.get('resolution',{})
    if not isinstance(trigger,dict) or not isinstance(resolution,dict): return False
    a,b=trigger.get('spells_cast'),resolution.get('spells_cast')
    if a is None or b is None:return True
    if not isinstance(a,list) or not isinstance(b,list):return False
    if len(a)>len(b):return False
    return all(x==y for x,y in zip(a,b))


def evaluate_operation(spec: dict, case: dict) -> dict:
    """Evaluate author-supplied snapshots against rules-annotated operation stages.
    This does NOT infer game legality, priority, object identity or a complete event ledger.
    """
    state = case['state']
    observed = case.get('observed_event')
    if not validate_history_snapshots(state):
        return {'status':'unknown','stage':'snapshot_validation','reason':'inconsistent or malformed cast-history checkpoints'}
    if spec['kind'] == 'trigger':
        if observed is None: return {'status':'unknown','stage':'trigger','reason':'missing observed event'}
        match = one_event_match(observed, spec['event'],state)
        if match != YES: return {'status':'not_triggered' if match==NO else 'unknown','stage':'trigger','reason':'event mismatch or unknown qualifier'}
        check = gate_and([predicate(p,state) for p in spec.get('trigger_requirements',[])])
        if check != YES: return {'status':'not_triggered' if check==NO else 'unknown','stage':'trigger','reason':'trigger requirement '+check}
        if 'target' in spec:
            target_ok = predicate(spec['target']['at_selection'],state)
            if target_ok != YES:
                return {'status':'not_on_stack' if target_ok==NO else 'unknown','stage':'target_selection','reason':'target selection '+target_ok, 'triggered':True}
        resolution_ok = gate_and([predicate(p,state) for p in spec.get('resolution_requirements',[])])
        if resolution_ok != YES: return {'status':'no_effect' if resolution_ok==NO else 'unknown','stage':'resolution','reason':'resolution gate '+resolution_ok, 'triggered':True}
        if 'target' in spec:
            target_ok = predicate(spec['target']['at_resolution'],state)
            if target_ok != YES:
                return {'status':'no_effect' if target_ok==NO else 'unknown','stage':'resolution','reason':'target revalidation '+target_ok, 'triggered':True}
        if 'optional' in spec:
            value=expression(spec['optional'],state)
            if value is MISSING:return {'status':'unknown','stage':'resolution','reason':'choice not supplied', 'triggered':True}
            if value is False: return {'status':'resolved_no_action','stage':'resolution','reason':'optional action declined','effects':[],'triggered':True}
            if value is not True:return {'status':'unknown','stage':'resolution','reason':'invalid choice','triggered':True}
        effects = render(spec.get('effects',[]),state)
        if _has_null(effects): return {'status':'unknown','stage':'output','reason':'output expression missing context', 'triggered':True}
        return {'status':'resolved','stage':'resolution','effects':effects,'triggered':True}
    if spec['kind'] == 'replacement':
        if observed is None: return {'status':'unknown','stage':'proposed_event','reason':'missing proposed event'}
        match=one_event_match(observed,spec['event'],state)
        if match != YES:return {'status':'not_applicable' if match==NO else 'unknown','stage':'proposed_event','reason':'event mismatch or unknown qualifier'}
        ok=gate_and([predicate(p,state) for p in spec.get('requirements',[])])
        if ok != YES:return {'status':'not_applicable' if ok==NO else 'unknown','stage':'replacement','reason':'replacement requirement '+ok}
        if 'optional' in spec:
            v=expression(spec['optional'],state)
            if v is MISSING or not isinstance(v,bool):return {'status':'unknown','stage':'replacement','reason':'choice missing'}
            if not v:return {'status':'not_chosen','stage':'replacement','reason':'optional replacement declined'}
        effects=render(spec.get('effects',[]),state)
        if _has_null(effects): return {'status':'unknown','stage':'output','reason':'replacement output missing context'}
        return {'status':'applied','stage':'replacement','suppresses_proposed_event':True,'effects':effects}
    return {'status':'unknown','reason':'operation kind outside v0.2 adapter'}
