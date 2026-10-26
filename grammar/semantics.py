"""From templates to DIO-shaped contracts: composed frame semantics, typed slot -> qualifier binding, and per-ability
operation assembly.

Three steps, each stored so a reviewer can see where a reading came from:

  frame_semantics   one row per template. The template's edges composed into units with slot-indexed arguments:
                    one trigger requirement group with alternatives, one replacement operation that rewrites a
                    proposed event into a resulting one, results with their relation and hook, cost components,
                    conditions, amplifiers. This is what a template review approves: the whole construction,
                    not loose edges.
  qualifiers        the value bound to each slot occurrence, parsed into DIO v3.1.1 §4.1 qualifier axes using the
                    v0.2.1 addendum names (actor, relation_to_observer, cardinality, simultaneity_group, act_time,
                    mana.production.mode ...).
  ability_contract  one DIO §5 operation per ability: kind, source_unit (with the host when the ability is
                    granted to a token or another object), requirement groups, amplifiers, timing, cost, result,
                    process and evidence (part and frame ids, versions, completeness, review state).

Nothing here is a rules engine. An operation's hook is its event intent; whether "destroy" ends in a death is a
rules question and is recorded only as a conditional implication (IMPLIES), never as a produced event.
"""
import hashlib
import json
import re

import concepts as cx
from lexicon import CARD_TYPES, SUBTYPES, SUPERTYPES, NUMBER_WORDS, KEYWORD_ABILITIES

SEMANTICS_VERSION = 'semantics-0.1.1'

SLOT_TOK = re.compile(r'<([a-z_.]+)>')
PREPS = ('to', 'on', 'from', 'into', 'onto', 'under', 'for', 'of', 'with', 'at', 'in', 'by', 'among', 'than',
         'equal', 'attached', 'except')
NON_VERBS = {'when', 'whenever', 'at', 'if', 'a', 'an', 'the', 'may', 'each', 'up', 'to', 'one', 'or', 'and', 'more',
             'then', 'that', 'this', 'you', 'all', 'any', 'another', 'other', 'target', 'not', "don't", "doesn't",
             'beginning', 'of', 'instead', 'also', ':', ',', '.', '—', 'have', 'has'}

# hook ids for concepts whose dio_ref does not start with one
COST_HOOK = {
    'cost.tap_self': ('tap', 'permanent.tap'), 'cost.tap_other': ('tap', 'permanent.tap'),
    'cost.untap_self': ('untap', 'permanent.untap'), 'cost.sacrifice_self': ('sacrifice', 'permanent.sacrifice'),
    'cost.sacrifice_other': ('sacrifice', 'permanent.sacrifice'), 'cost.discard': ('discard', 'card.discard'),
    'cost.exile': ('exile', 'exile.enter'), 'cost.life': ('pay_life', 'life.pay'), 'cost.mana': ('mana', 'mana.spend'),
    'cost.return_to_hand': ('return_to_hand', 'card.return_to_hand'),
    'cost.counter_remove': ('remove_counters', 'counter.remove'), 'cost.mill': ('mill', 'card.mill'),
    'cost.reveal': ('reveal', 'card.reveal'), 'cost.energy': ('pay_energy', 'energy.pay'),
    'cost.loyalty': ('loyalty', 'counter.remove|counter.put [loyalty]'), 'cost.keyword': ('keyword', None),
    'cost.additional': ('additional', None),
}

# One-way implications used by discovery (DIO §4.3). certainty: guaranteed | conditional.
IMPLIES = {
    'token.create': [('battlefield.enter', 'guaranteed', 'the token enters (token.enters_battlefield)')],
    'permanent.sacrifice': [('permanent.dies', 'conditional', 'a sacrificed creature dies unless replaced'),
                            ('battlefield.leave', 'guaranteed', '')],
    'permanent.destroy': [('permanent.dies', 'conditional', 'only if it is a creature and the destruction is not replaced or prevented'),
                          ('battlefield.leave', 'conditional', '')],
    'permanent.dies': [('battlefield.leave', 'guaranteed', ''), ('zone.change', 'guaranteed', 'graveyard entry')],
    'card.return_to_battlefield': [('battlefield.enter', 'guaranteed', '')],
    'permanent.tapped_for_mana': [('permanent.tap', 'guaranteed', ''), ('mana.add', 'guaranteed', '')],
    'exile.enter': [('zone.change', 'guaranteed', '')],
    'card.mill': [('zone.change', 'guaranteed', 'graveyard entry from library')],
    'card.discard': [('zone.change', 'guaranteed', 'graveyard entry from hand')],
    'combat.damage': [('damage.deal', 'guaranteed', '')],
    'life.pay': [('life.lose', 'guaranteed', '')],
}


HOOK_RE = re.compile(r'\b([a-z_]+\.[a-z_]+(?:\.[a-z_]+)*)\b')
EXTRA_HOOK = {'ev.keyword_action': 'keyword_action.performed'}


def concept_hook(cid):
    """The DIO hook identifier a concept reads (events) or attempts to produce (operations). None for modifiers,
    state predicates and processes that have no hook of their own."""
    if cid in COST_HOOK:
        return COST_HOOK[cid][1]
    if cid in EXTRA_HOOK:
        return EXTRA_HOOK[cid]
    c = cx.C.get(cid)
    if not c:
        return None
    st, dio, status, label, intent = c
    if intent and re.fullmatch(r'[a-z_]+\.[a-z_.]+', intent):
        return intent
    if st not in ('event', 'operation'):
        return None
    body = dio.split(':', 1)[1] if dio.startswith(('result.', 'requirement_group')) else dio
    m = HOOK_RE.search(body)
    return m.group(1) if m else None


# ------------------------------------------------------------------ qualifiers (§4.1 + addendum v0.2.1 names)

NUMW = {w: i for i, w in enumerate(['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
                                    'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
                                    'seventeen', 'eighteen', 'nineteen', 'twenty'])}
COLORS = ('white', 'blue', 'black', 'red', 'green')
_CT = sorted({t.lower() for t in CARD_TYPES}, key=len, reverse=True)
_SUP = {t.lower() for t in SUPERTYPES} - {'token'}
_SUB = {t.lower() for t in SUBTYPES}
_KW = sorted({k.lower() for k in KEYWORD_ABILITIES} | {'first strike', 'double strike'}, key=len, reverse=True)


def number(word):
    if word is None:
        return None
    w = word.lower()
    if w in ('a', 'an', 'another'):
        return 1
    if w.isdigit():
        return int(w)
    if w in NUMW:
        return NUMW[w]
    if w == 'x':
        return 'X'
    return None


def singular(w):
    if w.endswith('ies'):
        return w[:-3] + 'y'
    if w.endswith(('sses', 'ches', 'shes', 'xes')):
        return w[:-2]
    if w.endswith('ves') and w[:-3] + 'f' in _SUB:
        return w[:-3] + 'f'
    if w.endswith('s') and not w.endswith('ss') and w[:-1] in (_SUB | set(_CT) | {'card', 'spell', 'permanent', 'token', 'creature', 'land', 'player', 'opponent'}):
        return w[:-1]
    return w


def object_qualifiers(slot, value):
    """Parse an object noun phrase into §4.1 axes. Unknown words are kept in 'unparsed' so nothing is silently lost."""
    sel = slot.split('.', 1)[1] if '.' in slot else slot
    v = ' ' + value.lower().replace(',', ' ,') + ' '
    q = {}
    if sel == 'target' or ' target ' in v:
        q['selection'] = 'target'
    if sel in ('each', 'all') or re.search(r' (?:each|all) ', v):
        q['cardinality'] = 'each_object'
    if sel == 'oneormore' or ' one or more ' in v:
        q['cardinality'] = 'one_or_more'
        q['simultaneity_group'] = 'per_event_batch'
    if sel == 'anynum' or ' any number of ' in v:
        q['quantity'] = 'any_number'
    if sel == 'ref':
        q['reference'] = 'antecedent'
    if sel == 'attached' or re.match(r' (?:enchanted|equipped) ', v):
        q['attached_to'] = 'this'
    m = re.search(r' up to (\w+) ', v)
    if m:
        q['quantity_max'] = number(m.group(1))
    else:
        m = re.match(r' (a|an|another|\d+|x|' + '|'.join(NUMW) + r') ', v)
        if m and 'quantity' not in q:
            q['quantity'] = number(m.group(1))
    if re.search(r' (?:another|other) ', v):
        q['exclude_self'] = True
    if ' nontoken ' in v:
        q['token'] = False
    elif re.search(r' tokens? ', v):
        q['token'] = True
    types, not_types, subs, sups, colors, not_colors = [], [], [], [], [], []
    for w in re.findall(r"[a-z][a-z'-]*", v):
        neg = w.startswith('non') and len(w) > 4
        base = singular(w[3:].lstrip('-') if neg else w)
        if base in _CT:
            (not_types if neg else types).append(base)
        elif base in _SUP:
            sups.append(('non' if neg else '') + base)
        elif base in COLORS:
            (not_colors if neg else colors).append(base)
        elif base in _SUB and base not in ('token',):
            subs.append(base)
    if (len(set(types)) + len(set(subs)) > 1) and re.search(r'\b(?:or|and/or)\b', v) and not re.search(r'\bnon', v):
        # "creature or Vehicle", "artifact or enchantment": any one of these, not all of them
        q['type_logic'] = 'any_of'
    if types:
        q['card_type'] = sorted(set(types))
    if not_types:
        q['card_type_not'] = sorted(set(not_types))
    if subs:
        q['subtype'] = sorted(set(subs))
    if sups:
        q['supertype'] = sorted(set(sups))
    if colors:
        q['color'] = sorted(set(colors))
    if not_colors:
        q['color_not'] = sorted(set(not_colors))
    if ' colorless ' in v:
        q['color'] = ['colorless']
    if ' multicolored ' in v:
        q['color_count'] = '>=2'
    # what kind of object, and so which zone it is in unless stated
    if re.search(r' cards? ', v):
        q['object'] = 'card'
    elif re.search(r' spells? ', v):
        q['object'] = 'spell'
        q['zone'] = 'stack'
    elif re.search(r' abilit(?:y|ies) ', v):
        q['object'] = 'ability'
        q['zone'] = 'stack'
    else:
        q['object'] = 'permanent'
    # controller / owner (addendum A2: kept apart from the actor)
    if re.search(r" you don't control ", v):
        q['controller'] = 'not_you'
    elif re.search(r' you control ', v) or v.startswith(' your '):
        q['controller'] = 'you'
    elif re.search(r" (?:an opponent|your opponents|opponents|each opponent) controls? ", v):
        q['controller'] = 'opponent'
    elif re.search(r' (?:that player|they|defending player|target player|its controller) controls? ', v):
        q['controller'] = 'referenced_player'
    if re.search(r" you don't own ", v):
        q['owner'] = 'not_you'
    elif re.search(r' you own ', v):
        q['owner'] = 'you'
    m = re.search(r' (?:in|from) (your|a|each|their|an opponent\'s|target player\'s|that player\'s) (graveyard|hand|library|exile)', v)
    if m:
        q['zone'] = m.group(2)
        q['zone_owner'] = {'your': 'you', 'a': 'any', 'each': 'each', 'their': 'referenced_player'}.get(m.group(1), m.group(1))
    if q.get('object') == 'permanent' and 'zone' not in q:
        q['zone'] = 'battlefield'
    status = [s for s in ('tapped', 'untapped', 'attacking', 'blocking', 'blocked', 'unblocked', 'face-down', 'face-up')
              if re.search(r"(?: that's| )" + s + ' ', v)]
    if ' attacking or blocking ' in v:
        status = ['attacking|blocking']
    if status:
        q['status'] = status
    filt = []
    for m in re.finditer(r' with (?:total )?(power|toughness|mana value|base power) (\w+)(?: or (greater|less|more|fewer))?', v):
        filt.append({'axis': m.group(1).replace(' ', '_'), 'op': {'greater': '>=', 'more': '>=', 'less': '<=', 'fewer': '<='}.get(m.group(3), '=='),
                     'value': number(m.group(2)) if number(m.group(2)) is not None else m.group(2)})
    for m in re.finditer(r' with (?:power|toughness|mana value) (less than|greater than|equal to) ([^,]+?)(?= ,| and | or |$)', v):
        filt.append({'axis': 'stat', 'op': {'less than': '<', 'greater than': '>', 'equal to': '=='}[m.group(1)],
                     'value': m.group(2).strip()})
    if filt:
        q['filters'] = filt
    kws = [k for k in _KW if re.search(r' with(?:out)? (?:[a-z ]+, )?(?:[a-z ]+ (?:or|and) )?' + re.escape(k) + r'\b', v)]
    if kws:
        q['has_ability' if ' without ' not in v else 'lacks_ability'] = kws
    m = re.search(r' with (?:a|an|one or more|\w+) (\S+) counters? on ', v)
    if m:
        q['has_counter'] = m.group(1)
    m = re.search(r'([+-]?(?:\d+|x)/[+-]?(?:\d+|x))', v)
    if m and q.get('token'):
        q['base_pt'] = m.group(1)
    if q.get('token'):
        m = re.search(r" ([a-z][a-z'-]+) tokens? ", v)
        if m and m.group(1) not in _CT and m.group(1) not in _SUB and m.group(1) not in COLORS and m.group(1) not in (
                'creature', 'artifact', 'a', 'an', 'the', 'that', 'colorless', 'legendary', 'tapped', 'untapped'):
            q['token_name'] = m.group(1)
    m = re.search(r" named ([a-z][a-z' ,-]+?)(?= with| ,|$| )", v)
    if m and m.group(1) != '~':
        q['name'] = m.group(1)
    if ' of the chosen type ' in v or ' chosen type ' in v:
        q['chosen_type'] = True
    if ' named ~' in v:
        q['name'] = 'this'
    if re.search(r' (?:this way|exiled with ~|the exiled card)', v):
        q['linked'] = True
    if q.get('token') and ' create' not in v:
        pass
    return q


def player_qualifiers(slot, value):
    v = (value or '').lower()
    sel = slot.split('.', 1)[1].replace('_poss', '') if '.' in slot else slot
    q = {}
    if v in ('you', 'your'):
        q['player'] = 'you'
        q['relation_to_observer'] = 'observer_controller'
    elif 'opponent' in v:
        q['player'] = 'opponent'
        q['relation_to_observer'] = 'opponent_of_observer'
    elif re.search(r'\b(?:each|a|any|target|another) player\b|^players$', v):
        q['player'] = 'any_player'
        q['relation_to_observer'] = 'any'
    elif 'defending' in v:
        q['player'] = 'defending_player'
    elif re.search(r'controller|owner', v):
        q['player'] = 'controller_of_referenced_object' if 'controller' in v else 'owner_of_referenced_object'
    else:
        q['player'] = 'referenced_player'
    if sel == 'target' or 'target' in v:
        q['selection'] = 'target'
    if sel == 'each' or v.startswith('each') or v in ('players', 'opponents', 'your opponents'):
        q['cardinality'] = 'per_player'
    if 'other' in v or 'another' in v:
        q['exclude_self'] = True
    m = re.match(r'(each (?:opponent|player)) who (.+)', v)
    if m:
        q['condition'] = m.group(2)
    return q


def mana_qualifiers(frame_text, values):
    """Kate's ProduceMana(quantity, type, alternatives, restrictions, source), with addendum A4 names."""
    syms = [re.findall(r'\{([^}]+)\}', v) for v in values]
    q = {}
    ft = frame_text
    if 'color identity' in ft and 'commander' in ft:
        q['mode'] = 'commander_identity'
    elif ' of any color' in ft or 'any color' in ft:
        q['mode'] = 'any_color'
    elif 'any type' in ft:
        q['mode'] = 'any_type'
    elif 'chosen color' in ft:
        q['mode'] = 'chosen_color'
    elif 'any combination' in ft:
        q['mode'] = 'any_combination'
    elif len(values) > 1 and ' or ' in ft:
        q['mode'] = 'alternatives'
    elif values:
        q['mode'] = 'colorless' if all(s == 'C' for s in syms[0]) else 'fixed'
    else:
        q['mode'] = 'unread'
    if values:
        if q['mode'] == 'alternatives':
            q['alternatives'] = [[s for s in ss] for ss in syms]
            q['quantity'] = len(syms[0])
        else:
            q['units'] = [s for ss in syms for s in ss]
            q['quantity'] = len(q['units'])
    return q


def qualify(slot, value, frame_text=''):
    if value is None:
        if slot == 'self':
            return {'self': True}
        if slot in ('tap_symbol', 'untap_symbol'):
            return {'self': True}
        if slot == 'player.you_poss':
            return {'player': 'you', 'relation_to_observer': 'observer_controller'}
        return {}
    if slot.startswith('obj.'):
        return object_qualifiers(slot, value)
    if slot.startswith('player.'):
        return player_qualifiers(slot, value)
    if slot == 'self':
        q = {'self': True}
        if 'token' in value:
            q['token'] = True
        return q
    if slot == 'ref':
        return {'reference': 'antecedent', 'surface': value}
    if slot == 'n':
        n = number(value.split()[0]) if value else None
        return {'quantity': n if n is not None else value}
    if slot == 'zone':
        z = re.sub(r"^(?:your|their|its owner's|its owners'|that player's|an opponent's|target player's|the|a|each)\s+", '', value)
        own = 'you' if value.startswith('your') else ('referenced_player' if value.startswith(('their', "its owner", "that player")) else None)
        q = {'zone': z.rstrip('s') if z.endswith('graveyards') else z}
        if own:
            q['zone_owner'] = own
        return q
    if slot == 'counter':
        return {'counter_kind': value.replace(' counters', '').replace(' counter', '')}
    if slot == 'mana':
        return {'symbols': re.findall(r'\{([^}]+)\}', value)}
    if slot == 'pt':
        return {'pt_change': value}
    if slot == 'kw':
        return {'ability': value}
    if slot == 'color':
        return {'color': value}
    if slot == 'granted_ability':
        return {'granted_text': value}
    if slot == 'energy':
        return {'energy': value.count('{e}')}
    return {'value': value}


# ------------------------------------------------------------------ frame semantics (template level)

def tokens_with_pos(ft):
    return [(m.start(), m.group(0)) for m in re.finditer(r'<[a-z_.]+>|[^\s<>]+', ft)]


def arg_roles(ft, span, slots):
    """Name each slot inside a matched span by its grammatical position: actor/subject before the verb, the
    preposition that governs it, or object after the verb."""
    pos = [m.start() for m in SLOT_TOK.finditer(ft)]
    names = [m.group(1) for m in SLOT_TOK.finditer(ft)]
    s0, e0 = span if span else (0, len(ft))
    toks = [(p, t) for p, t in tokens_with_pos(ft) if s0 <= p < e0]
    verb_pos = None
    for p, t in toks:
        if not t.startswith('<') and t not in NON_VERBS and re.match(r"[a-z]", t):
            verb_pos = p
            break
    out = {}
    for i in slots:
        if i >= len(pos):
            continue
        p, name = pos[i], names[i]
        prev = None
        for q, t in toks:
            if q < p:
                prev = t
        if name.endswith('_poss'):
            role = 'possessor'
        elif name == 'n' and prev not in ('on', 'to', 'from'):
            role = 'amount'
        elif name in SLOT_ROLE and prev not in ('from', 'to', 'into', 'onto', 'in', 'on'):
            role = SLOT_ROLE[name]
        elif prev in PREPS:
            role = prev
        elif verb_pos is not None and p < verb_pos:
            role = 'actor' if name.startswith('player.') else 'subject'
        else:
            role = 'object' if not name.startswith('player.') else 'player'
        k, j = role, 2
        while k in out:
            k = f'{role}_{j}'
            j += 1
        out[k] = i
    return out


SLOT_ROLE = {'zone': 'zone', 'counter': 'counter', 'pt': 'pt_change', 'mana': 'mana', 'kw': 'ability',
             'color': 'color', 'tap_symbol': 'self', 'untap_symbol': 'self', 'granted_ability': 'granted_ability',
             'energy': 'energy'}

UNIT_OF = {'event': 'trigger', 'operation': 'result', 'cost': 'cost', 'state_predicate': 'condition',
           'modifier': 'modifier', 'process': 'process', 'keyword_macro': 'keyword', 'structure': 'structure'}


def modifier_unit(cid):
    p = cid.split('.')[0]
    return {'amp': 'amplifier', 'time': 'timing', 'cap': 'capacity', 'gate': 'timing', 'rest': 'restriction',
            'choice': 'choice'}.get(p, 'modifier')


def compose(role, ft, edges):
    """Compose a template's edges into units. edges: [(concept_id, relation, rule_id, meta)]."""
    units = []
    trig = [e for e in edges if (e[3] or {}).get('group') == 'trigger']
    if trig:
        alts = []
        for cid, rel, rid, meta in sorted(trig, key=lambda e: e[3].get('alt', 0)):
            alt_ft = meta.get('alt_text') or ft
            span = meta.get('span')
            if meta.get('alt_text'):
                # map the alternative's own slot order back to the template's slot indices
                local = arg_roles(alt_ft, None, list(range(len(meta['slots']))))
                args = {k: meta['slots'][v] for k, v in local.items()}
            else:
                args = arg_roles(ft, span, meta.get('slots', []))
            # "this creature or another creature you control": coordinated subjects are alternatives of the
            # same group (DIO §5.1), one per subject, sharing the other arguments
            subj = [k for k in args if k == 'subject' or k.startswith('subject_')]
            rest = {k: v for k, v in args.items() if k not in subj}
            for k in subj or [None]:
                a = dict(rest)
                if k:
                    a['subject'] = args[k]
                if re.search(r'\b(?:is|are) dealt\b', alt_ft) and 'subject' in a:
                    a['to'] = a.pop('subject')        # "is dealt damage": the subject receives it
                alts.append({'concept': cid, 'hook': concept_hook(cid), 'args': a, 'rule': rid, 'text': alt_ft})
        units.append({'unit': 'requirement_group', 'class': 'trigger', 'alternatives': alts})
    comp = {}
    for cid, rel, rid, meta in edges:
        meta = meta or {}
        if meta.get('group') == 'trigger':
            continue
        if meta.get('composite'):
            c = meta['composite']
            u = comp.get(c['rule'])
            if not u:
                proposed = c['proposed']
                # what the replacement watches for is read from the construction itself
                if c['rule'] == 'rep.die_exile':
                    if 'would leave the battlefield' in ft:
                        proposed = 'ev.battlefield.leave'
                    elif re.search(r'would be put into <zone>', ft):
                        proposed = 'ev.zone.change'
                args = arg_roles(ft, meta.get('span'), meta.get('slots', []))
                u = {'unit': 'operation', 'kind': 'replacement', 'mode': c['mode'], 'rule': rid,
                     'rewrites': {'proposed': {'concept': proposed, 'hook': concept_hook(proposed)},
                                  'resulting': ({'concept': c['resulting'], 'hook': concept_hook(c['resulting'])}
                                                if c['resulting'] else {'concept': None, 'hook': None,
                                                                         'note': 'replacement event not decomposed'})},
                     'args': args}
                comp[c['rule']] = u
                units.append(u)
            continue
        st = cx.concept_type(cid)
        unit = UNIT_OF.get(st, 'other')
        if unit == 'modifier':
            unit = modifier_unit(cid)
        u = {'unit': unit, 'concept': cid, 'relation': rel, 'hook': concept_hook(cid), 'rule': rid,
             'args': arg_roles(ft, meta.get('span'), meta.get('slots', []))}
        if unit in ('keyword', 'choice') and not u['args']:
            u.pop('args')
        if unit == 'cost':
            u['family'] = COST_HOOK.get(cid, (None,))[0]
            u['act_time'] = 'paid_as_cost'
        if unit == 'result':
            u['act_time'] = 'on_resolution'
            if cid == 'op.mana.add':
                u['mana_template'] = True
        units.append(u)
    order = {'requirement_group': 0, 'operation': 1, 'cost': 2, 'condition': 3, 'result': 4}
    units.sort(key=lambda u: order.get(u['unit'], 5))
    return units


def sem_sha(units):
    return hashlib.sha256(json.dumps(units, sort_keys=True).encode()).hexdigest()


def describe(units):
    """One line a reviewer can read: the whole construction, not loose edges."""
    out = []
    for u in units:
        if u['unit'] == 'requirement_group':
            out.append('TRIGGER any of [' + ' | '.join(
                f"{a['hook']}({', '.join(f'{k}=#{v}' for k, v in a['args'].items())})" for a in u['alternatives']) + ']')
        elif u['unit'] == 'operation':
            r = u['rewrites']
            out.append(f"REPLACEMENT[{u['mode']}] {r['proposed']['hook']} -> {r['resulting']['hook'] or '?'}"
                       f"({', '.join(f'{k}=#{v}' for k, v in u['args'].items())})")
        else:
            out.append(f"{u['unit'].upper()} {u.get('relation', '')} {u['concept']}"
                       + (f"[{u['hook']}]" if u.get('hook') else '')
                       + (f"({', '.join(f'{k}=#{v}' for k, v in u['args'].items())})" if u.get('args') else ''))
    return ' ; '.join(out)


def install_frame_semantics(db):
    db.executescript('''
    DROP TABLE IF EXISTS frame_semantics;
    CREATE TABLE frame_semantics(frame_id INTEGER PRIMARY KEY REFERENCES frame(frame_id), units_json TEXT NOT NULL,
      description TEXT NOT NULL, semantics_sha TEXT NOT NULL, semantics_version TEXT NOT NULL);''')
    edges = {}
    for fid, cid, rel, rid, sm in db.execute('SELECT frame_id, concept_id, relation, rule_id, slot_map FROM frame_concept_edge'):
        edges.setdefault(fid, []).append((cid, rel, rid, json.loads(sm) if sm else {}))
    rows = []
    for fid, role, ft in db.execute('SELECT frame_id, role, frame_text FROM frame'):
        units = compose(role, ft, edges.get(fid, []))
        rows.append((fid, json.dumps(units, sort_keys=True), describe(units), sem_sha(units), SEMANTICS_VERSION))
    db.executemany('INSERT INTO frame_semantics VALUES(?,?,?,?,?)', rows)


# ------------------------------------------------------------------ binding and ability contracts

def bind_args(args, bindings, ft):
    out = {}
    for k, i in args.items():
        if i >= len(bindings):
            out[k] = {'slot': None, 'unbound': True}
            continue
        b = bindings[i]
        slot, val = b[0], b[1]
        q = qualify(slot, val, ft)
        e = {'slot': slot, 'value': val, 'q': q}
        if len(b) > 2 and isinstance(b[2], dict) and b[2].get('alts'):
            e['alternatives'] = [{'value': a, 'q': qualify(slot, a, ft)} for a in b[2]['alts']]
        out[k] = e
    return out


def bound_hook(u, bindings, ft):
    d = {'concept': u.get('concept'), 'hook': u.get('hook'), 'args': bind_args(u.get('args', {}), bindings, ft)}
    cid = u.get('concept')
    dest = [a['q'].get('zone') for k, a in d['args'].items() if k.split('_')[0] in ('to', 'onto', 'into') and a.get('q')]
    if cid in ('op.zone.return', 'op.zone.put') and 'battlefield' in dest:
        d['hook'] = 'card.return_to_battlefield' if cid == 'op.zone.return' else 'zone.enter'
        if re.search(r'\btransformed\b', ft):
            d['enters_transformed'] = True
    elif cid == 'op.zone.return' and 'hand' in dest:
        d['hook'] = 'card.return_to_hand'
    if dest and d['hook'] in ('zone.enter', 'card.return_to_battlefield', 'card.return_to_hand'):
        d['destination'] = dest[0]
    if cid in ('op.entry.tapped', 'ev.battlefield.enter', 'op.token.create', 'op.zone.put', 'op.zone.return'):
        st = [w for w in ('tapped', 'attacking', 'blocking') if re.search(r'\b' + w + r'\b', ft)]
        if st:
            d['entry_status'] = st          # "enters tapped and attacking": a status of the entry, not a declaration
    m = re.search(r'\b(first|second|third) <obj\.[a-z_]+> each turn', ft)
    if m and cid and cid.startswith('ev.'):
        d['ordinal_condition'] = m.group(1) + '_each_turn'   # §5.2: holds for one event per turn, an implicit capacity
    if cid == 'op.pay':
        d['hook'] = ('mana.spend' if any(b[0] == 'mana' for b in bindings) else
                     'life.pay' if ' life' in ft else 'energy.pay' if any(b[0] == 'energy' for b in bindings) else 'cost.pay')
    if cid == 'st.control':
        m = re.search(r"control (no|<n> or more|<n> or fewer|exactly <n>|at least <n>)", ft)
        if m:
            d['comparison'] = {'no': '== 0', '<n> or more': '>= n', '<n> or fewer': '<= n', 'exactly <n>': '== n',
                               'at least <n>': '>= n'}[m.group(1)]
    if cid == 'op.choice.value':
        for a in d['args'].values():
            if a.get('slot', '') and a['slot'].startswith('obj.'):
                a['q'] = {'choice_of': a['value'] + (' type' if ' type' in ft else '')}
    if u.get('concept') == 'op.mana.add':
        vals = [b[1] for b in bindings if b[0] == 'mana']
        d['mana'] = mana_qualifiers(ft + ' ' + ' '.join(str(b[1]) for b in bindings if b[1]), vals)
    return d


TRIGGER_STEP = re.compile(r'at the beginning of (?:the |each |your |each of your |that turn\'s |the next |'
                          r'<player\.[a-z_]+> |each <player\.[a-z_]+> )?(.+)$')


def step_qualifiers(alt_text, bindings):
    m = TRIGGER_STEP.search(alt_text)
    if not m:
        return {}
    which = m.group(1).replace('<player.you_poss> ', '')
    whose = 'each'
    if '<player.you_poss>' in alt_text or 'your ' in alt_text:
        whose = 'you'
    if any(b[0].startswith('player') and b[1] and 'opponent' in b[1] for b in bindings):
        whose = 'opponent'
    return {'which': re.sub(r' on .*| of each turn', '', which).strip(), 'whose_turn': whose}


def ability_contract(ab, parts, sem, card, host=None):
    """ab: ability row dict; parts: [(part_id, role, frame_id, frame_text, bindings, completeness, reviewed)]."""
    kind = {'triggered': 'trigger', 'activated': 'activate', 'loyalty': 'activate', 'spell': 'cast',
            'static': 'continuous', 'replacement': 'replacement', 'keyword': 'keyword_macro', 'mode': 'mode',
            'chapter': 'trigger', 'additional_cost': 'cast'}.get(ab['kind'], ab['kind'])
    op = {'id': f"{card['name']}#{ab['ability_id']}", 'kind': kind,
          'source_unit': {'card': card['name'], 'oracle_id': card['oracle_id']},
          'initiation': {'requirement_groups': [], 'amplifiers': [], 'timing': {}, 'cost': {'components': []},
                         'choice': []},
          'process': [], 'result': {'produces': [], 'consumes': [], 'transforms': [], 'modifies': [], 'permits': [],
                                    'prevents': [], 'rewrites': []},
          'conditions': [], 'restrictions': [], 'keywords': []}
    if host:
        op['source_unit']['granted'] = host
    if ab['kind'] == 'activated':
        op['initiation']['timing']['speed'] = 'instant'
    elif ab['kind'] == 'loyalty':
        op['initiation']['timing']['speed'] = 'sorcery'
    gi = 0
    seq = 0
    last_subject = None
    modality_may = False
    branch = None
    for pid, role, fid, ft, bindings, comp, reviewed in parts:
        units = sem.get(fid, [])
        if not units or comp != 'complete':
            # a part the grammar cannot read is kept visibly, never dropped: a contract with an unread
            # condition is not the same contract without it
            op.setdefault('unread', []).append({'role': role, 'template': ft, 'completeness': comp, 'part': pid})
        slotless = {b[0]: b[1] for b in bindings if len(b) > 2 and isinstance(b[2], dict) and b[2].get('slotless')}
        positional = [b for b in bindings if not (len(b) > 2 and isinstance(b[2], dict) and b[2].get('slotless'))]
        may = slotless.get('modality') == 'may'
        if not may and comp != 'complete' and re.search(r'<player[^>]*> may |\byou may ', ft):
            # the modality sits in the unread prefix of a partial frame ("as <self> enters, you may pay ...")
            may = True
        for u in units:
            ev = {'part': pid, 'frame': fid}
            if u['unit'] == 'requirement_group':
                gi += 1
                alts = []
                for a in u['alternatives']:
                    h = bound_hook(a, positional, ft)
                    h['text'] = a.get('text')
                    if h['hook'] in ('turn.step.begin', 'turn.phase.begin'):
                        h['step'] = step_qualifiers(a['text'], positional)
                    # the subject of "this creature" is the host when the ability is granted
                    for arg in h['args'].values():
                        if arg.get('slot') == 'self' and host:
                            arg['q']['host'] = host['host']
                    alts.append(h)
                op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': 'trigger',
                                                               'alternatives': alts, 'checkpoint': 'trigger', **ev})
            elif u['unit'] == 'operation':
                args = bind_args(u['args'], positional, ft)
                op['result']['rewrites'].append({'mode': u['mode'], 'proposed': u['rewrites']['proposed'],
                                                 'resulting': u['rewrites']['resulting'], 'args': args, **ev})
                op['kind'] = 'replacement'
            elif u['unit'] == 'cost':
                gi += 1
                h = bound_hook(u, positional, ft)
                if u['concept'] == 'cost.sacrifice_other' or any(a.get('q', {}).get('exclude_self') for a in h['args'].values()):
                    h['must_come_from_other_unit'] = True
                if may:
                    h['optional'] = True
                op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': 'cost', 'family': u.get('family'),
                                                               'act_time': 'paid_as_cost', **h, **ev})
                op['initiation']['cost']['components'].append(f'g{gi}')
            elif u['unit'] == 'condition':
                gi += 1
                h = bound_hook(u, positional, ft)
                cls = 'history' if u['concept'] in ('st.history', 'st.did_action') else 'state'
                op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': cls,
                                                               'checkpoint': 'trigger' if role == 'condition' and kind == 'trigger' else 'resolution',
                                                               'text': ft, **h, **ev})
            elif u['unit'] == 'result':
                h = bound_hook(u, positional, ft)
                h['act_time'] = 'continuous' if kind == 'continuous' else 'on_resolution'
                if not any(k in h['args'] for k in ('actor', 'player')) and u['concept'] not in ('op.pt.modify', 'op.pt.set', 'op.ability.grant', 'op.ability.remove', 'op.type.change', 'op.evasion', 'op.restrict', 'op.untap.prevent'):
                    h['args']['actor'] = {'slot': None, 'implicit': True, 'q': {'player': 'you', 'relation_to_observer': 'observer_controller'}}
                h['certainty'] = 'optional' if may else ('conditional' if branch else 'guaranteed')
                if branch:
                    h['branch'] = branch
                for arg in h['args'].values():
                    if arg.get('q', {}).get('selection') == 'target':
                        gi += 1
                        op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': 'eligibility',
                                                                       'target': arg['value'], 'q': arg['q'],
                                                                       'checkpoint': 'initiation', **ev})
                # "gets +1/+1 and gains trample": a coordinated predicate shares the subject of the clause before it
                if not any(k in h['args'] for k in ('subject', 'object')) and last_subject and u['concept'] in (
                        'op.pt.modify', 'op.pt.set', 'op.ability.grant', 'op.ability.remove', 'op.type.change'):
                    h['args']['subject'] = {**last_subject, 'inherited': True}
                subj = h['args'].get('subject') or h['args'].get('object')
                if subj and subj.get('slot') and not subj.get('inherited'):
                    last_subject = subj
                seq += 1
                h['step'] = seq
                rel = (u.get('relation') or 'PRODUCES').lower()
                rel = rel if rel in op['result'] else 'produces'
                op['result'][rel].append({**h, **ev})
            elif u['unit'] == 'amplifier':
                op['initiation']['amplifiers'].append({'concept': u['concept'], 'relation': 'MODIFIES',
                                                       'text': ft, 'args': bind_args(u['args'], positional, ft), **ev})
            elif u['unit'] in ('timing', 'capacity'):
                term = {'concept': u['concept'], 'text': ft, **ev}
                if re.search(r"during <player\.you_poss> turn|during your turn", ft):
                    term['turn_scope'] = 'your_turn'
                elif re.search(r"during (?:each )?<player\.[a-z_]+> turn|during an opponent's turn|not <player\.you_poss> turn", ft):
                    term['turn_scope'] = 'opponent_turn'
                op['initiation']['timing'].setdefault('terms', []).append(term)
                if u['concept'] == 'time.sorcery_speed':
                    op['initiation']['timing']['speed'] = 'sorcery'
            elif u['unit'] == 'process':
                op['process'].append({'concept': u['concept'], **ev})
                if u['concept'] in ('proc.if_you_do', 'proc.reflexive'):
                    branch = u['concept']
                elif u['concept'] == 'proc.if_not':
                    branch = 'proc.if_not'
            elif u['unit'] == 'choice':
                ch = {'concept': u['concept'], 'text': ft, 'args': bind_args(u.get('args', {}), positional, ft), **ev}
                op['initiation']['choice'].append(ch)
                if u['concept'] == 'choice.target':
                    for arg in ch['args'].values():
                        gi += 1
                        op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': 'eligibility',
                                                                       'target': arg.get('value'), 'q': arg.get('q', {}),
                                                                       'checkpoint': 'initiation', **ev})
            elif u['unit'] == 'keyword':
                kwd = {'macro': u['concept'], 'text': ft, 'args': bind_args(u.get('args', {}), positional, ft), **ev}
                op['keywords'].append(kwd)
                for arg in kwd['args'].values():
                    if arg.get('q', {}).get('selection') == 'target':
                        gi += 1
                        op['initiation']['requirement_groups'].append({'id': f'g{gi}', 'class': 'eligibility',
                                                                       'target': arg['value'], 'q': arg['q'],
                                                                       'checkpoint': 'initiation', 'via_macro': u['concept'], **ev})
            elif u['unit'] == 'restriction':
                op['restrictions'].append({'concept': u['concept'], 'text': ft, **ev})
            else:
                op['conditions'].append({'concept': u.get('concept'), 'unit': u['unit'], 'text': ft, **ev})
        if may:
            modality_may = True
    # A1: tapping this for mana is a facet the grammar can read directly from {T} + add mana
    costs = [g for g in op['initiation']['requirement_groups'] if g['class'] == 'cost']
    if any(g.get('concept') == 'cost.tap_self' for g in costs) and any(r.get('concept') == 'op.mana.add' for r in op['result']['produces']):
        op['result']['produces'].append({'concept': None, 'hook': 'permanent.tapped_for_mana', 'derived': 'A1',
                                         'args': {'subject': {'slot': 'self', 'q': {'self': True}}}})
    for g in costs:
        if g.get('concept') in ('cost.sacrifice_self', 'cost.sacrifice_other', 'cost.tap_self', 'cost.tap_other',
                                'cost.discard', 'cost.exile', 'cost.life', 'cost.return_to_hand', 'cost.counter_remove',
                                'cost.mill'):
            op['initiation']['cost'].setdefault('on_payment', []).append({'hook': g.get('hook'), 'group': g['id']})
    for k in ('amplifiers', 'choice'):
        if not op['initiation'][k]:
            del op['initiation'][k]
    for k in list(op['result']):
        if not op['result'][k]:
            del op['result'][k]
    for k in ('process', 'conditions', 'restrictions', 'keywords', 'unread'):
        if k in op and not op[k]:
            del op[k]
    if not op['initiation']['cost']['components']:
        del op['initiation']['cost']
    if not op['initiation']['timing']:
        del op['initiation']['timing']
    if modality_may:
        op['optional'] = True
    return op


def flag_mana_ability(op):
    """CR 605.1: an activated ability that adds mana, has no target and is not a loyalty ability; or a triggered
    ability that triggers from a mana ability (tapped for mana / mana added) and adds mana (605.1b)."""
    adds = any(r.get('concept') == 'op.mana.add' for r in op.get('result', {}).get('produces', []))
    if not adds:
        return
    groups = op['initiation'].get('requirement_groups', [])
    targets = any(g['class'] == 'eligibility' for g in groups)
    if op['kind'] == 'activate' and not targets and not any(g.get('concept') == 'cost.loyalty' for g in groups):
        op['mana_ability'] = 'activated (CR 605.1a)'
    elif op['kind'] == 'trigger' and not targets and any(
            a.get('hook') in ('permanent.tapped_for_mana', 'mana.add') for g in groups if g['class'] == 'trigger'
            for a in g['alternatives']):
        op['mana_ability'] = 'triggered (CR 605.1b)'


def host_of(db_parts_by_ability, parent_id, sem):
    """When an ability is granted (a quoted ability), find what it is granted to: a token the parent creates, or
    the objects the parent grants it to. Returns {'host': 'token'|'object'|'unknown', 'qualifiers': ..., ...}."""
    for pid, role, fid, ft, bindings, comp, reviewed in db_parts_by_ability.get(parent_id, []):
        if '<granted_ability>' not in ft:
            continue
        units = sem.get(fid, [])
        positional = [b for b in bindings if not (len(b) > 2 and isinstance(b[2], dict) and b[2].get('slotless'))]
        for u in units:
            if u.get('concept') == 'op.token.create':
                objs = [b for b in positional if b[0].startswith('obj.')]
                return {'host': 'token', 'created_by_ability': parent_id, 'part': pid,
                        'token': objs[0][1] if objs else None,
                        'q': object_qualifiers(objs[0][0], objs[0][1]) if objs else {}}
            if u.get('concept') == 'op.ability.grant':
                args = bind_args(u.get('args', {}), positional, ft)
                tgt = next((a for k, a in args.items() if k in ('subject', 'object') and a.get('slot', '').startswith(('obj.', 'self'))), None)
                return {'host': 'self' if tgt and tgt.get('slot') == 'self' else 'object', 'granted_by_ability': parent_id,
                        'part': pid, 'object': tgt.get('value') if tgt else None, 'q': tgt.get('q') if tgt else {}}
        return {'host': 'unknown', 'granted_by_ability': parent_id, 'part': pid}
    return {'host': 'unknown', 'granted_by_ability': parent_id}


def install_contracts(db, where='c.in_collection = 1'):
    from collections import defaultdict
    sem = {fid: json.loads(u) for fid, u in db.execute('SELECT frame_id, units_json FROM frame_semantics')}
    rev = {}
    try:
        rev = dict(db.execute('SELECT frame_id, frame_ok FROM effective_frame_review'))
    except Exception:
        pass
    db.executescript('''
    DROP TABLE IF EXISTS ability_contract;
    CREATE TABLE ability_contract(ability_id INTEGER PRIMARY KEY, oracle_id TEXT, contract_json TEXT NOT NULL,
      completeness TEXT, reviewed INT, n_unbound INT, semantics_version TEXT);''')
    abil = db.execute(f'''SELECT a.ability_id, a.oracle_id, a.kind, a.parent_ability, a.granted_by, a.text, c.name
                          FROM ability a JOIN card c USING(oracle_id) WHERE {where}''').fetchall()
    ids = {r[0] for r in abil}
    parts = defaultdict(list)
    for pid, aid, role, fid, ft, b, comp in db.execute(
            f'''SELECT p.part_id, p.ability_id, p.role, p.frame_id, f.frame_text, p.bindings_json, f.completeness
                FROM part p JOIN frame f USING(frame_id) JOIN ability a USING(ability_id) JOIN card c USING(oracle_id)
                WHERE {where} ORDER BY p.ability_id, p.ordinal'''):
        parts[aid].append((pid, role, fid, ft, json.loads(b or '[]'), comp, rev.get(fid, 0)))
    rows = []
    for aid, oid, kind, parent, granted_by, text, name in abil:
        if kind in ('reminder_only', 'structure'):
            continue
        host = host_of(parts, granted_by, sem) if granted_by else None
        ps = parts.get(aid, [])
        con = ability_contract({'ability_id': aid, 'kind': kind}, ps, sem, {'name': name, 'oracle_id': oid}, host)
        comps = [p[5] for p in ps]
        completeness = ('complete' if comps and all(c == 'complete' for c in comps) else
                        'none' if not comps or all(c == 'none' for c in comps) else 'partial')
        reviewed = int(bool(ps) and all(p[6] == 1 for p in ps))
        con['evidence'] = {'ability_id': aid, 'oracle_text': text, 'parts': [p[0] for p in ps],
                           'frames': [p[2] for p in ps], 'completeness': completeness, 'template_reviewed': bool(reviewed)}
        flag_mana_ability(con)
        n_unbound = json.dumps(con).count('"unbound": true')
        rows.append((aid, oid, json.dumps(con, sort_keys=True), completeness, reviewed, n_unbound, SEMANTICS_VERSION))
    db.executemany('INSERT INTO ability_contract VALUES(?,?,?,?,?,?,?)', rows)
    return len(rows)


def contracts_from_text(text, name='Test Card', type_line='Creature', keywords=()):
    """Run the whole pipeline in memory (no database): grammar -> frames -> edges -> composed semantics -> bound
    contracts. Used for macro expansions read from printed reminder text, and by the tests."""
    import grammar as g
    if keywords == 'sentences':
        # a macro expansion is a sequence of instructions: one line per sentence, except that a restriction
        # ("Station only as a sorcery") stays with the ability it restricts
        text, keywords = re.sub(r'\.\s+(?=[A-Z])(?!(?:Activate|Station|Crew|Saddle) only\b)', '.\n', text), ()
    abilities = g.segment_face(g.prep(text, g.self_names(name, name)), type_line, list(keywords))
    sem, parts_by, out = {}, {}, []
    fid = 0
    for ab in abilities:
        ps = []
        for k, p in enumerate(ab.get('parts', [])):
            if p['role'] == 'keyword':
                ft, b = 'keyword ' + ab['keyword'], []
            elif p['role'] == 'structure':
                ft, b = '<structure>', [['structure', p['text']]]
            else:
                ft, b = g.frame(p['text'])
            edges, comp = cx.match_frame(p['role'], ft)
            fid += 1
            sem[fid] = compose(p['role'], ft, edges)
            ps.append((f"{ab['id']}.{k}", p['role'], fid, ft, [list(x) for x in b], comp, 0))
        parts_by[ab['id']] = ps
    for ab in abilities:
        if ab['kind'] in ('reminder_only', 'structure'):
            continue
        host = host_of(parts_by, ab['granted_by'], sem) if ab.get('granted_by') is not None else None
        con = ability_contract({'ability_id': str(ab['id']), 'kind': ab['kind']}, parts_by[ab['id']], sem,
                               {'name': name, 'oracle_id': None}, host)
        comps = [p[5] for p in parts_by[ab['id']]]
        flag_mana_ability(con)
        con['evidence'] = {'oracle_text': ab['text'], 'completeness': 'complete' if comps and all(c == 'complete' for c in comps)
                           else 'partial', 'reminders': ab.get('reminders')}
        out.append(con)
    return out
