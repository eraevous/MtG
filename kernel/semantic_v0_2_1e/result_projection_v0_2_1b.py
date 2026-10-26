"""Conservative projection of resolved, typed effects into observable facts.

A projection is not a Magic rules engine. It presumes the provided *outcome*
really occurred after replacements, and never invents unknown characteristics.
Every invocation gets a distinct causal action identity unless explicitly supplied.
"""
from __future__ import annotations
import re
from uuid import uuid4
from semantic_expression_v0_2_1 import Bounds

KEYWORD_ABILITIES = {"flying", "haste", "first strike", "double strike", "vigilance",
                     "deathtouch", "lifelink", "trample", "reach", "menace", "defender",
                     "hexproof", "indestructible", "flash", "ward", "prowess", "protection"}
SNAPSHOT_FIELDS = ('types','subtypes','supertypes','colors','controller','owner','token',
                   'tapped','attacking','name','keywords','keyword_details',
                   'power','toughness','object_id','subject','previous_object_id',
                   'is_cast','from_zone','to_zone')
VALID_ZONES = {'battlefield','graveyard','exile','hand','library','command','stack'}


def _unknown(root, reason, hook='projection.unknown', attrs=None):
    return {'event_id':f'{root}:unknown', 'hook':hook, 'status':'unknown',
            'reason':reason, 'derived_from':root, 'snapshots':{'event':attrs or {}}}


def _new_object_id(root, suffix='obj'):
    return f'{root}:{suffix}'


def _event(hook, eid, attrs, provenance):
    return {'event_id':eid, 'hook':hook, 'snapshots':{'event':attrs}, 'derived_from':provenance}


def _zone(value):
    return value.casefold().strip() if isinstance(value,str) and value.strip() else None


def _keywords(abilities):
    """Extract only confidently parsed keyword names; keep parameters separately.

    Non-keyword rules text doesn't prove the absence of other keyword abilities.
    """
    if not isinstance(abilities,list) or not all(isinstance(a,str) for a in abilities):
        return None, None, False
    names=[]; params={}; complete=True
    for raw in abilities:
        phrase=' '.join(raw.casefold().strip().split())
        # For parameterized keywords keep the parameter payload verbatim.
        m=re.fullmatch(r'(ward)\s+(.+)',phrase)
        p=re.fullmatch(r'(protection)\s+(from\s+.+)',phrase)
        if m or p:
            match=m or p
            k=match.group(1)
            names.append(k)
            params.setdefault(k,[]).append(raw[len(k):].strip())
        elif phrase in KEYWORD_ABILITIES:
            names.append(phrase)
        else:
            complete=False
    return sorted(set(names)),params,complete


def _attrs(effect):
    return {k:v for k,v in effect.items() if k in SNAPSHOT_FIELDS}


def project_resolved_effects(effects:list[dict], action_id:str|None=None, *,
                             used_action_ids:set[str]|None=None,
                             require_action_id:bool=False,
                             _internal:bool=False) -> list[dict]:
    """Emit outcome observations, with causal/identity provenance.

    Caller-supplied action_id must be globally unique per *resolution*. When absent,
    a UUID is minted, so two separate calls never share an object/event identity
    in ordinary operation. Explicit IDs enable reproducible tests and replay.
    """
    if action_id is None:
        if require_action_id:
            raise ValueError('a stable action_id is required for persisted/imported event ledgers')
        action_id = 'resolution:'+uuid4().hex
    elif not isinstance(action_id,str) or not action_id or (':' in action_id and not _internal):
        raise ValueError('explicit action_id must be nonempty and cannot contain colon')
    if used_action_ids is not None:
        if action_id in used_action_ids:
            raise ValueError('duplicate resolution action_id in ledger')
        used_action_ids.add(action_id)
    if not isinstance(effects,list):
        raise TypeError('effects must be a list')
    result=[]
    for i,effect in enumerate(effects):
        root=f'{action_id}:{i}'
        if not isinstance(effect,dict):
            result.append(_unknown(root,'malformed effect record'))
            continue
        kind=effect.get('kind')
        if effect.get('optional') is True:
            choice=effect.get('chosen')
            if choice is False:
                continue
            if choice is not True:
                # Project the ACTUAL chosen branch and then strip its certainty.
                # A guessed hook would report incorrect definite nonmatches.
                branch={k:v for k,v in effect.items() if k not in ('optional','chosen')}
                # Reserve ':' for internal derivation, forbidden in caller IDs;
                # this cannot collide with an independent external resolution.
                branch_id=f'{action_id}:optional:{i}'
                maybe=project_resolved_effects([branch],branch_id,_internal=True)
                for observation in maybe:
                    observation['status']='unknown'
                    observation['reason']='optional effect choice not known'
                    observation['derived_from']=root
                    result.append(observation)
                continue
        if kind=='token_create':
            quantity=effect.get('quantity')
            token=effect.get('token')
            attrs=_attrs(token) if isinstance(token,dict) else {}
            attrs['token']=True
            if 'controller' not in attrs and effect.get('controller') is not None:
                attrs['controller']=effect['controller']
            if isinstance(token,dict) and 'abilities' in token:
                names,params,complete=_keywords(token['abilities'])
                if names is not None:
                    existing=attrs.get('keywords',[])
                    if isinstance(existing,(tuple,list)) and all(isinstance(x,str) for x in existing):
                        attrs['keywords']=sorted(set(existing) | set(names))
                    elif 'keywords' not in attrs:
                        attrs['keywords']=names
                    if params: attrs['keyword_details']=params
                    if not complete: attrs['keywords_complete']=False
                else:
                    attrs['keywords_complete']=False
            if isinstance(quantity,Bounds):
                interval=(quantity.low,quantity.high)
                integral=(type(quantity.low) in (int,float) and quantity.low>=0 and
                          int(quantity.low)==quantity.low and
                          (quantity.high is None or
                           (type(quantity.high) in (int,float) and quantity.high>=quantity.low and
                            int(quantity.high)==quantity.high)))
                if not integral or not isinstance(token,dict):
                    result.append(_unknown(root,'invalid bounded token quantity/characteristics','battlefield.enter',attrs))
                    continue
                certain=int(quantity.low)
                if quantity.high is None or quantity.high>quantity.low:
                    possible=dict(attrs)
                    possible['to_zone']='battlefield'
                    result.append(_unknown(root+':remainder','bounded quantity may create additional tokens',
                                           'battlefield.enter',possible))
                quantity=certain
            if type(quantity) is not int or quantity<0 or not isinstance(token,dict):
                result.append(_unknown(root,'missing or invalid token quantity/characteristics',
                                       'battlefield.enter',attrs))
                continue
            for j in range(quantity):
                obj=dict(attrs)
                obj['object_id']=_new_object_id(root,f'token:{j}:obj')
                obj['to_zone']='battlefield'
                result.append(_event('battlefield.enter',f'{root}:token:{j}',obj,root))
        elif kind=='zone_move':
            origin=_zone(effect.get('from',effect.get('from_zone')))
            destination=_zone(effect.get('to',effect.get('to_zone')))
            attrs=_attrs(effect)
            attrs['from_zone']=origin
            attrs['to_zone']=destination
            if (origin is not None and origin not in VALID_ZONES) or destination not in VALID_ZONES:
                target=('battlefield.enter' if destination=='battlefield' else
                        'battlefield.leave' if origin=='battlefield' else 'projection.unknown')
                result.append(_unknown(root,'zone move has unknown or invalid zone',target,attrs))
                continue
            if origin==destination:
                result.append(_unknown(root,'zone move with unchanged zone', 'projection.unknown',attrs))
                continue
            if destination=='battlefield':
                attrs['object_id']=_new_object_id(root)
                if effect.get('object_id') is not None and attrs.get('previous_object_id') is None:
                    attrs['previous_object_id']=effect['object_id']
                result.append(_event('battlefield.enter',f'{root}:entry',attrs,root))
            elif origin=='battlefield':
                # Identity and last-known characteristics belong to the OLD object.
                result.append(_event('battlefield.leave',f'{root}:leave',attrs,root))
            else:
                # Information sufficient to prove the zone entered; graveyard listeners
                # need this even though no battlefield departure happened.
                result.append(_event(f'{destination}.enter',f'{root}:entry',attrs,root))
        elif kind in ('sacrifice','destroy'):
            hook='permanent.sacrifice' if kind=='sacrifice' else 'permanent.destroy'
            attrs=_attrs(effect)
            if 'to_zone' in effect: attrs['to_zone']=_zone(effect.get('to_zone'))
            if attrs.get('to_zone') not in VALID_ZONES and attrs.get('to_zone') is not None:
                result.append(_unknown(root,'invalid resolved removal destination',hook,attrs))
            else:
                result.append(_event(hook,f'{root}:remove',attrs,root))
        else:
            result.append(_unknown(root,f'unrecognized resolved effect kind {kind!r}'))
    return result
