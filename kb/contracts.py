"""Mechanics · Operations candidates -> DIO operation contracts -> validation checks -> compiler.

Drafting is deterministic and conservative: every contract keeps the exact Oracle clause, the
Oracle text SHA it was drafted against, the source evidence (row, status, confidence, URL and the
untouched legacy fields), requirement groups (AND across groups, OR within a group), hook timing,
costs, effects and zone transitions. Anything the drafter cannot bind is recorded as unbound and
blocks the contract; it is never guessed.

Since 0.3.0 the contract has the shape of a DIO v3.1.1 `operation` (§5): initiation.requirement_groups
(each cost component, target class, condition and trigger its own group; alternatives inside a group),
amplifiers, timing, cost {method, components, on_payment, remembered}, choice, result {produces,
consumes, transforms, modifies, permits, prevents, transitions}, capacity and evidence. Hooks are §4
objects {id, kind, subject, qualifiers}. Mana is typed (mana.py). `query_index` is a derived index for
kbq.py, not part of the operation.

No contract is reviewed by drafting or by passing checks. Semantic review comes only from a current
`verified` entry in the append-only review overlay. Only reviewed contracts whose compile loses nothing are
compiled, and only those with a passing runtime scenario reach the evaluator.
"""
import json, re, unicodedata
import kbfacts as F
import mana as MANA

DRAFTER_VERSION = 'contract-drafter-0.4.0'
COMPILER_VERSION = 'contract-compiler-0.3.0'
ADDENDUM_VERSION = 'DIO-3.1.1-kb-addendum-0.1'

KIND = {'trigger': 'trigger', 'activate': 'activate', 'continuous': 'continuous', 'replacement': 'replacement',
        'special_action': 'special_action', 'spell_effect': 'cast', 'choice_mode': 'composite', 'unclassified': None}

# 0.3.0 projection hook -> DIO hook identifier (for agreement checks only)
PROJ_HOOK = {'enter': 'battlefield.enter', 'landfall': 'land.enters_battlefield', 'dies': 'permanent.dies',
             'attack': 'attacker.declared', 'cast': 'spell.cast', 'combat_damage': 'combat.damage',
             'end_step': 'turn.step.begin', 'upkeep': 'turn.step.begin', 'begin_combat': 'turn.step.begin',
             'main_phase': 'turn.phase.begin', 'lifegain': 'life.gain', 'leave': 'battlefield.leave',
             'sacrifice': 'permanent.sacrifice', 'draw': 'card.draw', 'counters': 'counter.put', 'create': 'token.create',
             'scry_surveil': 'card.look'}
# legacy hook spellings that name a registry concept under another identifier
HOOK_ALIASES = {'timing.step_begin': 'turn.step.begin'}  # addendum A6: legacy spelling -> registry identifier
ENGINE_KINDS = {'triggered', 'activated', 'spell', 'additional_cost'}
ENGINE_OUTPUTS = {'mana', 'draw', 'interaction', 'token', 'counters', 'pump_one', 'life', 'scry_surveil', 'removal', 'drain',
                  'reach', 'recursion', 'pump_team', 'evasion', 'wipe', 'proliferate', 'pump_team_x', 'charge', 'untap_self'}

ZONES = {  # effect identifier -> zone transition (from, to, continuity); 'text' = read the destination from the clause
    'token.create': ('none', 'battlefield', 'new_object'), 'card.draw': ('library', 'hand', 'same_object'),
    'card.discard': ('hand', 'graveyard', 'new_object'), 'card.mill': ('library', 'graveyard', 'new_object'),
    'permanent.destroy': ('battlefield', 'graveyard', 'new_object'), 'permanent.sacrifice': ('battlefield', 'graveyard', 'new_object'),
    'card.return_to_battlefield': ('graveyard', 'battlefield', 'new_object'), 'exile.enter': ('text', 'exile', 'new_object'),
    'card.return_to_hand': ('text', 'hand', 'new_object'), 'card.search': ('library', 'text', 'new_object'),
    'graveyard.leave': ('graveyard', 'text', 'new_object'), 'library.enter': ('text', 'library', 'new_object'),
}


def norm(s):
    s = unicodedata.normalize('NFKC', str(s)).replace('−', '-').replace('—', '-').replace('–', '-')
    return re.sub(r'\s+', ' ', s).strip().lower()


def clause_key(text, name):
    t = re.sub(r'\([^)]*\)', '', norm(text))
    for n in sorted({name, name.split(' // ')[0], name.split(',')[0], re.split(r'[ ,]', name.split(' // ')[0])[0]}, key=lambda x: (-len(x), x)):
        if len(n) > 3: t = t.replace(n.lower(), '~')  # longest first, so the result does not depend on PYTHONHASHSEED
    t = re.sub(r'\bthis (?:creature|artifact|enchantment|land|card|spell|permanent)\b', '~', t)
    return re.sub(r'[^a-z0-9~{}/+\- ]', '', t).replace('  ', ' ').strip(' .')


def faces(card):
    """Faces as recorded in the inventory row (name ' // ' split; text split on '//' lines)."""
    names = card['card_name'].split(' // ')
    if len(names) == 1: return [{'face_index': 0, 'face_name': names[0], 'oracle_text': card['oracle_text'] or '',
                                 'type_line': card['type_line'], 'mana_cost': card['mana_cost']}]
    texts = re.split(r'\n?\s*//\s*\n?', card['oracle_text'] or '')
    types = (card['type_line'] or '').split(' // ')
    costs = (card['mana_cost'] or '').split(' // ')
    return [{'face_index': i, 'face_name': nm, 'oracle_text': texts[i] if i < len(texts) and len(texts) == len(names) else None,
             'type_line': types[i] if i < len(types) and len(types) == len(names) else None,
             'mana_cost': costs[i] if i < len(costs) and len(costs) == len(names) else None} for i, nm in enumerate(names)]


# ---------------------------------------------------------------- costs (DIO §5.3)
NUMW = {'a': 1, 'an': 1, 'one': 1, 'another': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'x': 'X', 'any number of': 'any'}
SELF_REF = r'(?:this (?:creature|artifact|enchantment|land|permanent|vehicle|aura|equipment|token|card|planeswalker|saga)|~|it)'


def _qty(phrase):
    m = re.match(r'(an|a|one|another|two|three|four|five|six|x|any number of)\b\s*', phrase)
    return (NUMW[m.group(1)], phrase[m.end():]) if m else (1, phrase)


def cost_component(atom, name):
    """One printed cost component -> a typed DIO cost component, or None if it is not understood."""
    a = norm(atom).replace(name.lower(), '~')
    if a == '{t}':
        return {'family': 'tap', 'subject': 'this', 'symbol': '{T}', 'on_payment': ['permanent.tap [this]']}
    if a == '{q}':
        return {'family': 'untap', 'subject': 'this', 'symbol': '{Q}', 'on_payment': ['permanent.untap [this]']}
    if '{e}' in a:
        w = re.match(r'pay (\w+) \{e\}$', a)
        return {'family': 'pay_energy', 'amount': NUMW.get(w.group(1), w.group(1)) if w else a.count('{e}'), 'on_payment': []}
    if re.fullmatch(r'(?:\{[0-9wubrgcxsp/]+\})+', a):
        return MANA.parse_cost(atom)
    m = re.fullmatch(r'tap (.+?) untapped (.+?)(?: you control)?', a) or re.fullmatch(r'tap (an?|one|two|three|x|another) (.+)', a)
    if m:
        q, _ = _qty(m.group(1) + ' ')
        filt = m.group(2)
        return {'family': 'tap', 'subject': 'other', 'object_filter': filt, 'quantity': q, 'untapped': 'untapped' in a,
                'must_come_from_other_unit': bool(re.search(r'\b(?:other|another)\b', a)), 'on_payment': [f'permanent.tap [{filt}]']}
    m = re.fullmatch(r'sacrifice (.+)', a)
    if m:
        obj = m.group(1)
        if re.fullmatch(SELF_REF, obj):
            return {'family': 'sacrifice', 'subject': 'this', 'on_payment': ['permanent.sacrifice [this]', 'battlefield.leave [this]']}
        q, filt = _qty(obj)
        return {'family': 'sacrifice', 'subject': 'other', 'object_filter': filt, 'quantity': q,
                'must_come_from_other_unit': bool(re.search(r'\b(?:other|another)\b', a)),
                'on_payment': [f'permanent.sacrifice [{filt}]'] + (['permanent.dies'] if 'creature' in filt else [])}
    for pat, fam in [(r'discard (.+)', 'discard'), (r'pay (\w+) life', 'pay_life'), (r'exile (.+)', 'exile'), (r'reveal (.+)', 'reveal'),
                     (r'return (.+) to (?:its|their) owner.s hand', 'return_to_hand'), (r'remove (.+?) counters? from (.+)', 'remove_counters'),
                     (r'blight (\w+)', 'blight'), (r'collect evidence (\w+)', 'collect_evidence')]:
        m = re.fullmatch(pat, a)
        if m:
            on = {'discard': ['card.discard'], 'pay_life': ['life.pay'], 'exile': ['exile.enter'], 'remove_counters': ['counter.remove'],
                  'return_to_hand': ['card.return_to_hand']}.get(fam, [])
            return {'family': fam, 'object': m.group(1), 'on_payment': on}
    if re.fullmatch(r'[+-]?\d+|[+-]x', a):
        return {'family': 'loyalty', 'amount': a, 'on_payment': ['counter.put [loyalty]' if a.startswith('+') else 'counter.remove [loyalty]']}
    return None


def parse_costs(payment, name):
    comps, unread = [], []
    for atom in [x.strip() for x in re.split(r',\s*(?![^{]*\})', payment or '') if x.strip()]:
        c = cost_component(atom, name)
        if c is None or (c.get('family') == 'mana' and c.get('unknown')): unread.append(atom)
        else: comps.append(dict(c, text=atom))
    return comps, unread


# ---------------------------------------------------------------- hooks (DIO §4)
FILTER_WORDS = r'(?:nontoken |noncreature |nonland |other |another )*(?:legendary )?(?:[a-z]+ )?(?:creatures?|lands?|artifacts?|enchantments?|tokens?|permanents?|spells?|planeswalkers?|foods?|clues?|treasures?|blood tokens?|cards?)'


def hook_object(event_text, legacy_id, name):
    """An event description -> {id, kind, subject, qualifiers}. Qualifiers follow DIO §4.1 axes."""
    e = norm(event_text).replace(name.lower(), '~')
    q = {}
    hid = (legacy_id or '').split(';')[0].strip() or None
    if re.search(r'\bis tapped for mana\b|\btaps? (?:a|an|one or more)? ?[\w ]*? for mana\b', e):
        hid = 'permanent.tapped_for_mana'  # addendum A1: a {T}-cost mana ability of that permanent resolved and produced mana
        q['source_event'] = 'tapped_for_mana'
        m = re.search(r'(enchanted land|(?:a|an) [\w ]+?) (?:is tapped|for mana)', e) or re.search(r'tap (?:a|an) ([\w ]+?) for mana', e)
        q['source_filter'] = re.sub(r'^an? ', '', m.group(1)) if m else None
        q['implies'] = ['permanent.tap [that permanent]', 'mana.add [source: that permanent]']
    elif m := re.search(r'\bexpend (\d+)', e):
        hid = 'mana.spend'; q['threshold'] = {'measurement': 'total mana spent this turn', 'operator': 'crosses', 'reference': int(m.group(1))}
    elif 'sacrific' in e:
        hid = 'permanent.sacrifice'
    else:
        verb = next((v for p, v in VERB_HOOK if re.search(p, e)), None)
        # the legacy row carries one hook for the whole trigger; each alternative gets the hook its own verb names
        if verb and not (hid and hid.split('.')[-1] == verb.split('.')[-1]) and not (verb == 'battlefield.enter' and (hid or '').endswith('enters_battlefield')):
            hid = verb
    # addendum A2: who acts, who controls the permanent when the event happens, who controls the
    # event's source, who owns the object, and how each relates to the observing ability's controller.
    if re.match(r'you\b', e): q['actor'] = 'you'
    elif re.match(r'an opponent\b|one of your opponents', e): q['actor'] = 'opponent'
    elif re.match(r'(?:a|each) player\b', e): q['actor'] = 'any_player'
    if re.search(r'\byou control\b', e): q['controller'] = 'you'
    elif re.search(r"(?:an opponent|your opponents) controls?\b", e): q['controller'] = 'opponent'
    rel = {'you': 'observer_controller', 'opponent': 'opponent_of_observer', 'any_player': 'any'}
    if 'actor' in q: q['relation_to_observer'] = rel[q['actor']]
    if hid in ('permanent.sacrifice', 'permanent.tapped_for_mana') and 'actor' in q:
        q['permanent_controller_at_event'] = 'same_as_actor'  # CR 701.21a, 106.12/605: only the controller does it
    elif 'controller' in q:
        q['permanent_controller_at_event'] = rel[q['controller']]
    if m := re.search(r'\ba source (you|an opponent) controls?\b', e): q['source_controller'] = rel['you' if m.group(1) == 'you' else 'opponent']
    if m := re.search(r"\b(you own|you don.t own|an opponent owns)\b", e):
        q['owner'] = {'you own': 'observer_controller', 'an opponent owns': 'opponent_of_observer'}.get(m.group(1), 'not_observer_controller')
    if re.search(r'\b(?:another|other)\b', e): q['other'] = True
    # addendum A3: each_object fires once per object; one_or_more once per simultaneous event batch
    if 'one or more' in e: q['cardinality'] = 'one_or_more'; q['simultaneity_group'] = 'per_event_batch'
    else: q['cardinality'] = 'each_object'
    if re.search(SELF_REF, e) and not re.search(r'\b(?:a|an|another|one or more)\b', e): subject = 'this'
    else: subject = None
    f = object_filter(re.sub(r'^(?:you|a player|an opponent|each player|one of your opponents)\s+\w+\s+', '', e))
    if f and subject != 'this': q['object_filter'] = f
    if re.search(r'\bnontoken\b', e): q['token'] = False
    elif re.search(r'\btokens?\b', e): q['token'] = True
    if q.get('source_event'): q['source_filter'] = q.get('object_filter') or q.get('source_filter')
    return {'id': hid, 'kind': 'event', 'subject': subject, 'qualifiers': q, 'text': event_text.strip()}


def object_filter(e):
    """The noun phrase an event is about: 'you sacrifice a nontoken elemental' -> 'nontoken elemental'."""
    m = re.search(r'\b(?:a|an|another|one or more|each|two or more|other)\s+((?:other\s+)?(?:[\w/-]+\s+){0,3}?[\w/-]+?)'
                  r'(?=\s+(?:you control|you don.t control|an opponent controls|your opponents control|enters?|dies|die|is|are|attacks?|leaves?|'
                  r'becomes?|deals?|for mana|from|card|spells?\b)|,|$)', e)
    if m: return m.group(1)
    m = re.search(r'\b(enchanted \w+|equipped creature)', e)
    return m.group(1) if m else None


VERB_HOOK = [(r'\bdies\b|\bdie\b', 'permanent.dies'), (r'\bdeals? combat damage\b', 'combat.damage'), (r'\battacks?\b', 'attacker.declared'),
             (r'\bblocks?\b', 'blocker.declared'), (r'\bleaves? the battlefield\b', 'battlefield.leave'), (r'\benters?\b', 'battlefield.enter'),
             (r'\bbecomes? tapped\b', 'permanent.tap'), (r'\bcasts? \b', 'spell.cast'), (r'\bbecomes? the target\b', 'object.becomes_target')]

STEPS = {'upkeep': 'upkeep', 'draw step': 'draw', 'end step': 'end_step', 'end of combat': 'end_of_combat', 'combat': 'beginning_of_combat',
         'cleanup': 'cleanup'}
PHASES = {'precombat main phase': 'precombat_main', 'first main phase': 'precombat_main', 'postcombat main phase': 'postcombat_main',
          'second main phase': 'postcombat_main', 'main phase': 'either_main', 'combat phase': 'combat', 'ending phase': 'ending'}


def turn_hook(event):
    """'at the beginning of your upkeep' -> turn.step.begin {step: upkeep, whose_turn: you} (addendum A6)."""
    e = norm(event)
    m = re.match(r'the beginning of (?:the )?(?:(your|each|each opponent.s|each player.s|the next|that player.s|your next) )?(.+)$', e)
    whose = {'your': 'you', 'each': 'each', "each opponent's": 'opponent', "each player's": 'each', 'your next': 'you',
             "that player's": 'that_player', 'the next': 'next'}.get(m.group(1) if m else None)
    rest = (m.group(2) if m else e).strip()
    for k, v in PHASES.items():
        if rest.startswith(k):
            return {'id': 'turn.phase.begin', 'kind': 'event', 'subject': None, 'text': event.strip(),
                    'qualifiers': {'phase': v, 'whose_turn': whose, 'legacy_alias': 'timing.step_begin'}}
    for k, v in STEPS.items():
        if rest.startswith(k):
            return {'id': 'turn.step.begin', 'kind': 'event', 'subject': None, 'text': event.strip(),
                    'qualifiers': {'step': v, 'whose_turn': whose, 'legacy_alias': 'timing.step_begin'}}
    return {'id': 'turn.step.begin', 'kind': 'event', 'subject': None, 'text': event.strip(),
            'qualifiers': {'step': 'unread', 'whose_turn': whose, 'legacy_alias': 'timing.step_begin'}}


TRIG = re.compile(r'^(?:[\w\' ]+ — )?(when|whenever|at)\b(.*?),\s*(.*)$', re.I | re.S)


def trigger_alternatives(event):
    ors = re.split(r'\s+or\s+(?=(?:attacks|dies|enters|leaves|is put|becomes|deals|blocks|you cast|another))', event)
    if len(ors) == 1: return [event.strip()]
    verb = re.search(r'\b(enters(?: the battlefield)?|attacks|dies|leaves the battlefield|becomes tapped|deals combat damage[^,]*)$', ors[-1].strip())
    return [o.strip() if (not verb or re.search(r'\b(enters|attacks|dies|leaves|becomes|deals|cast|is put)\b', o)) else f'{o.strip()} {verb.group(1)}' for o in ors]


# ---------------------------------------------------------------- result side
def result_of(effects, clause, name, legacy_transition, modifies):
    low = norm(clause)
    body = low.split(':', 1)[1] if re.match(r'^[^"]*?:', low) and not TRIG.match(low) else low
    granted = norm(' '.join(re.findall(r'"([^"]+)"', clause)))
    produces = []
    for e in effects:
        item = {'id': e}
        if e == 'mana.add':
            if granted and ' add ' not in body.replace(granted, ''):
                item['granted_to_other_object'] = True
            item['mana'] = MANA.parse_production(body.replace(granted, '') if granted and ' add ' in body.replace(granted, '') else body)
        if e == 'permanent.sacrifice':
            m = re.search(r'\b(each opponent|each player|target player|target opponent|you)\s+sacrifices?', body)
            item['actor'] = m.group(1) if m else ('granted ability' if 'sacrifice' in granted else 'unread')
        produces.append(item)
    if 'mana.add' not in effects and re.search(r'\badds? (?:an additional |that much |\w+ additional )?(?:\{[wubrgc]\}|\w+ mana|mana)', body.replace(granted, '')):
        produces.append({'id': 'mana.add', 'added_by': 'drafter (legacy row had no mana.add)', 'mana': MANA.parse_production(body.replace(granted, ''))})
    m = re.search(r'(?:^|[.;] |, (?:then )?|\band )(?:you may )?tap ((?:up to \w+ )?(?:target|all|each|another)[^.,]*|' + SELF_REF + r'\b)', body)
    if m and 'permanent.tap' not in effects:
        produces.append({'id': 'permanent.tap', 'as': 'effect', 'object': m.group(1)})
    transitions = zone_transitions(effects, clause, legacy_transition)
    return {'produces': produces, 'consumes': [], 'transforms': [], 'modifies': [{'text': clause, 'bound': False}] if modifies else [],
            'permits': [], 'prevents': [], 'transitions': transitions}


def amplifiers_of(body):
    out = []
    for m in re.finditer(r'\bfor each ([^.,]+)|\bequal to ([^.,]+)|\bx is ([^.,]+)|where x is ([^.,]+)', body):
        measure = next(g for g in m.groups() if g)
        out.append({'text': m.group(0), 'measures': measure.strip(), 'aggregation': 'count' if m.group(1) or 'number of' in measure else 'value',
                    'relation': 'MODIFIES'})
    return out


def choice_of(clause):
    low = norm(clause)
    m = re.search(r'\bchoose (one|two|three|one or both|one or more|any number|up to \w+)\b', low)
    modes = [x.strip(' .') for x in re.split(r'\s*•\s*', clause)[1:]] if '•' in clause else []
    if not m and not modes: return None
    return {'chooser': 'controller', 'choice_time': 'initiation', 'cardinality': m.group(1) if m else 'unread', 'legal_set': modes,
            'scope': 'shared', 'branch_outputs': None}


TARGET = re.compile(r'\b(?:up to (\w+) )?targets? ((?:[\w\-]+ ){0,5}?(?:creature|player|opponent|permanent|artifact|enchantment|land|spell|card|planeswalker|any target)s?(?: an opponent controls| you control| you don\'t control)?)')


def requirement_groups(clause, op, kind, costs, name):
    groups, unbound = [], []
    low_clause = norm(clause)
    body = clause
    m = TRIG.match(clause.strip())
    if m and kind == 'trigger':
        word, event, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        alts = [turn_hook(event) for _ in [0]] if word == 'at' else [hook_object(t, op['observes_hook'], name) for t in trigger_alternatives(event)]
        groups.append({'id': 'g_trigger', 'class': 'trigger', 'checkpoint': 'trigger', 'trigger_word': word, 'alternatives': alts})
        im = re.match(r'if ([^,]+),\s*(.*)$', body, re.I | re.S)
        if im:
            groups.append({'id': 'g_intervening_if', 'class': 'state', 'checkpoint': 'trigger', 'recheck_at': 'resolution',
                           'alternatives': [{'text': 'if ' + im.group(1)}]})
            body = im.group(2)
    for i, c in enumerate(costs, 1):
        groups.append({'id': f'g_cost{i}', 'class': 'cost', 'checkpoint': 'payment', 'alternatives': [c],
                       'must_come_from_other_unit': c.get('must_come_from_other_unit', False), 'quantity': c.get('quantity')})
    for i, t in enumerate(TARGET.finditer(norm(body)), 1):
        groups.append({'id': f'g_target{i}', 'class': 'eligibility', 'checkpoint': 'initiation' if kind != 'trigger' else 'trigger',
                       'alternatives': [{'text': t.group(0)}], 'quantity': {'up_to': t.group(1)} if t.group(1) else 1})
    for pat, cls in [(r'activate (?:this ability )?only as a sorcery', 'timing'), (r'only during your turn', 'timing'),
                     (r'activate only if ([^.]+)', 'state')]:
        mm = re.search(pat, low_clause)
        if mm: groups.append({'id': f'g_{cls}', 'class': cls, 'checkpoint': 'initiation', 'alternatives': [{'text': mm.group(0)}]})
    low = norm(body)
    if re.search(r'\binstead\b', low): unbound.append('replacement branch ("instead") not bound to process branches')
    if re.search(r'\botherwise\b', low): unbound.append('else branch ("otherwise") not bound')
    if re.search(r'\bunless\b', low): unbound.append('"unless" condition not bound')
    if re.search(r'rather than pay|instead of paying|without paying', low): unbound.append('cost substitution / alternative cost method not bound (DIO §5.3 cost.method/modifiers)')
    if re.search(r'(?<!activate only )(?<!activate this ability only )\bif\b', low): unbound.append('conditional "if" inside the effect not bound')
    if (re.search(r'\bchoose (?:one|two|any|up to)\b|•', low) or op['operation_kind'] == 'choice_mode'):
        unbound.append('modes recorded as a choice, but outputs are not separated per branch')
    return groups, unbound, body


def zone_transitions(effects, clause, legacy):
    out, low = [], norm(clause)
    for e in effects:
        if e not in ZONES: continue
        frm, to, cont = ZONES[e]
        if frm == 'text':
            frm = next((z for z in ('graveyard', 'battlefield', 'hand', 'library', 'exile') if f'from your {z}' in low or f'from a {z}' in low or f'from their {z}' in low), 'battlefield' if e != 'library.enter' else 'unbound')
        if to == 'text':
            split = re.search(r'put (one|\w+ of them) onto the battlefield( tapped)? and the other into your hand', low)
            if split:  # e.g. Cultivate: one card to each destination
                out.append({'effect': e, 'from': frm, 'to': 'battlefield', 'quantity': 1, 'tapped': bool(split.group(2)), 'continuity': cont, 'split_group': e})
                out.append({'effect': e, 'from': frm, 'to': 'hand', 'quantity': 1, 'continuity': cont, 'split_group': e})
                continue
            to = 'battlefield' if 'onto the battlefield' in low else 'hand' if 'into your hand' in low or 'to your hand' in low else 'unbound'
        out.append({'effect': e, 'from': frm, 'to': to, 'continuity': cont})
    if legacy: out.append({'legacy_note': legacy})
    return out


def timing_of(op, clause, kind, effects, type_line):
    low = norm(clause)
    speed = None
    if kind == 'activate':
        speed = 'sorcery' if 'only as a sorcery' in low else ('mana_ability' if effects == ['mana.add'] and 'target' not in low else 'instant')
    elif kind == 'cast':
        speed = 'instant' if 'Instant' in (type_line or '') or 'flash' in low else 'sorcery'
    elif kind in ('continuous', 'replacement'):
        speed = 'none'
    scope = 'your_turn' if re.search(r'\byour (?:upkeep|end step|turn|first main|second main|combat)', low) else None
    w = re.search(r'at the beginning of (?:(your|each|the next|each opponent.s) )?([\w ]+?)(?:,|$)', low)
    window = {'relative_to': w.group(2).strip(), 'whose': w.group(1)} if w else None
    ordinal = 'first_each_turn' if 'for the first time each turn' in low else 'second_each_turn' if 'second' in low and 'each turn' in low else None
    return {'turn_scope': scope, 'window': window, 'speed': speed, 'ordinal_condition': ordinal, 'legacy': op['timing'] or None}


def capacity_of(clause):
    low = norm(clause)
    if re.search(r'only once each turn|triggers only once each turn', low):
        return [{'kind': 'capacity', 'uses': 1, 'renews': 'each_turn', 'text': re.search(r'[^.]*only once each turn[^.]*', low).group(0).strip()}]
    return []


# ---------------------------------------------------------------- keyword macros (addendum A7)
MACROS = {  # keyword -> versioned macro id. A reminder-text clause belongs to the macro, not to a separate operation.
    'earthbend': 'macro.earthbend@1', 'offspring': 'macro.offspring@1', 'dredge': 'macro.dredge@1',
    'crew': 'macro.crew@1', 'station': 'macro.station@1'}


def keyword_macro(clause, card):
    """The versioned keyword macro a clause instantiates or expands, if any."""
    low, text = norm(clause), norm(card['oracle_text'] or '')
    pos = text.find(low.rstrip(').'))
    head = text[:pos] if pos >= 0 else ''
    inside = pos >= 0 and head.count('(') > head.count(')')
    for kw, mid in MACROS.items():
        if inside:
            if re.search(rf'\b{kw}\b[^.()]*$', head[:head.rfind('(')]): return {'macro': mid, 'role': 'reminder_text_of_macro'}
        elif m := re.search(rf'\b{kw}\b\s*(\{{[^}}]+\}}|\d+|x)?', low):
            return {'macro': mid, 'role': 'instance', 'parameter': m.group(1)}
    return None


# ---------------------------------------------------------------- drafting
def draft(op, card, vocab, projections):
    """Return (operation_contract, proposed_action or None, checks[list of (id,result,detail)])."""
    name, clause = op['card_name'], op['oracle_clause'] or ''
    kind = KIND.get(op['operation_kind'])
    fs = faces(card)
    if len(fs) > 1:
        hits = [f for f in fs if f['oracle_text'] and norm(clause) in norm(f['oracle_text'])]
        face = hits[0] if len(hits) == 1 else None
    else:
        face = fs[0]
    costs, cost_unread = parse_costs(op['payment_consumes'], name)
    method = 'base'
    if kind == 'cast' and face and face.get('mana_cost'):
        mc = MANA.parse_cost(face['mana_cost'])
        if mc: costs = [dict(mc, text=face['mana_cost'], source='mana cost of the spell')] + costs
    groups, unbound, body = requirement_groups(clause, op, kind, costs, name)
    effects = [e.strip() for e in (op['result_produces'] or '').split(';') if e.strip()]
    result = result_of(effects, clause, name, op['object_transition'], op['modifies'])
    amps = amplifiers_of(norm(body))
    unbound += [f"amplifier measure not read: {a['text']}" for a in amps if not a['measures']]
    unbound += [f'cost component not understood: {a}' for a in cost_unread]
    ck = clause_key(clause, name)
    proj = next((p for p in projections if clause_key(p['clause'] or '', name) == ck), None) or \
        next((p for p in projections if ck and p['clause'] and (clause_key(p['clause'], name) in ck or ck in clause_key(p['clause'], name))), None)
    trig = next((g for g in groups if g['class'] == 'trigger'), None)
    contract = {
        'schema': 'DIO-3.1.1/operation', 'id': op['operation_id'], 'kind': kind, 'legacy_kind': op['operation_kind'],
        'source_unit': {'card': name, 'face': face['face_name'] if face else None, 'oracle_text_sha256': card['oracle_text_sha256']},
        'exact_text': clause,
        'initiation': {
            'requirement_groups': groups, 'amplifiers': amps,
            'timing': timing_of(op, clause, kind, effects, (face or {}).get('type_line') or card['type_line']),
            'cost': {'method': method, 'components': [g['id'] for g in groups if g['class'] == 'cost'],
                     'on_payment': [e for c in costs for e in c.get('on_payment', [])],
                     'remembered': ['X'] if any(c.get('has_x') for c in costs) else [],
                     'mana_restrictions': None},
            'choice': choice_of(clause)},
        'result': result,
        'modality': 'may' if re.search(r'\byou may\b', norm(clause)) else 'must',
        'capacity': capacity_of(clause),
        'granted_abilities': re.findall(r'"([^"]+)"', clause),
        'qualifiers_legacy': [q.strip() for q in (op['qualifiers'] or '').split(';') if q.strip()],
        'unbound': unbound,
        'evidence': {'source_operation_id': op['operation_id'], 'source_row': op['source_row'], 'source_status': op['source_status'],
                     'source_confidence': op['source_confidence'], 'source_url': op['source_url'], 'review_note': op['review_note'],
                     'legacy_fields': json.loads(op['raw_json'])},
        'projection_link': {'ability_index': proj['ability_index'], 'projection_version': proj['projection_version'],
                            'unread': proj['unread'] or ''} if proj else None,
    }
    # addendum A5: a cost component is paid as a cost (before the ability is on the stack / resolves);
    # a result item is done on resolution. The same act (sacrifice, tap, discard) can be either.
    for g in groups:
        if g['class'] == 'cost':
            for a in g['alternatives']: a['act_time'] = 'paid_as_cost'
    if kind not in ('continuous', 'replacement'):
        for it in result['produces']: it.setdefault('act_time', 'on_resolution')
    contract['keyword_macro'] = keyword_macro(clause, card)
    hook_ids = sorted({a['id'] for a in trig['alternatives'] if a.get('id')}) if trig else [h.strip() for h in (op['observes_hook'] or '').split(';') if h.strip()]
    contract['query_index'] = {  # derived for discovery queries (DIO §9: derived, never authoritative)
        'hook_ids': hook_ids,
        'hook_ids_in_vocabulary': all(h in vocab for h in hook_ids) if hook_ids else None,
        'hook_subject': hook_subject(trig['alternatives'][0]['text'] if trig else None, name),
        'feeds': feeds(contract, effects)}
    action = json.loads(proj['raw_ability_json']) if proj else None
    checks = validate(contract, card, action, proj, effects, vocab)
    return contract, action, checks


def validate(c, card, action, proj, effects, vocab):
    ch = []
    add = lambda i, r, d='': ch.append((i, r, d))
    text = norm(card['oracle_text'] or '')
    add('C01_exact_text_in_oracle', 'pass' if norm(c['exact_text']) and norm(c['exact_text']) in text else 'fail', 'clause must occur in the stored Oracle text')
    pos = text.find(norm(c['exact_text']).rstrip(').'))
    inside = pos >= 0 and text[:pos].count('(') > text[:pos].count(')')
    add('C13_not_reminder_text', 'fail' if inside else 'pass', 'clause is reminder text (inside parentheses); it belongs to the keyword definition, not a separate operation' if inside else '')
    add('C02_oracle_sha', 'pass' if card['oracle_text_sha256'] else 'fail')
    add('C03_operation_kind', 'pass' if c['kind'] else 'fail', c['legacy_kind'])
    idx = c['query_index']
    if c['kind'] == 'trigger' and not idx['hook_ids']: add('C04_hook', 'fail', 'trigger without an observed hook')
    elif idx['hook_ids'] and not idx['hook_ids_in_vocabulary']:
        add('C04_hook', 'warn', ', '.join(h for h in idx['hook_ids'] if h not in vocab) + ' not in the registry hook vocabulary')
    else: add('C04_hook', 'pass')
    add('C05_face', 'pass' if c['source_unit']['face'] else 'fail', 'multi-face card: clause not located on exactly one face' if not c['source_unit']['face'] else c['source_unit']['face'])
    src = c['evidence']['source_status']
    add('C06_source_annotation', 'fail' if src == 'requires_manual_annotation' else 'pass', src)
    comps = [g for g in c['initiation']['requirement_groups'] if g['class'] == 'cost']
    cu = [u for u in c['unbound'] if u.startswith('cost component')]
    if c['kind'] == 'activate' and not comps: add('C07_costs', 'fail', 'activated ability without a parsed cost')
    elif cu: add('C07_costs', 'fail', '; '.join(cu))
    else: add('C07_costs', 'pass')
    bad = [e for e in effects if e not in vocab]
    if c['kind'] in ('trigger', 'activate', 'cast') and not effects and not (action and action.get('outputs')):
        add('C08_effects', 'fail', 'no effect recorded')
    else: add('C08_effects', 'warn' if bad else 'pass', ', '.join(bad))
    sem = [u for u in c['unbound'] if not u.startswith('cost component')]
    add('C09_bound_semantics', 'fail' if sem else 'pass', '; '.join(sem))
    zt = [z for z in c['result']['transitions'] if 'unbound' in (z.get('from'), z.get('to'))]
    add('C10_zone_transitions', 'fail' if zt else 'pass', ', '.join(z['effect'] for z in zt))
    if c['granted_abilities']:
        add('C12_granted_ability', 'warn', 'quoted ability granted to another object; check that its outputs are not counted as this operation\'s')
    mana_out = [p for p in c['result']['produces'] if p['id'] == 'mana.add' and not p.get('granted_to_other_object')]
    untyped = [p for p in mana_out if not p.get('mana') or p['mana'].get('mode') == 'unread']
    add('C14_mana_typed', 'fail' if untyped else 'pass', 'mana production not typed (colour/amount unread)' if untyped else
        '; '.join(f"{p['mana']['mode']} x{p['mana']['amount']}" for p in mana_out))
    if not action:
        add('C11_executable_shape', 'warn', 'no 0.3.0 projected ability matches this clause; not compilable until an action is attached')
    else:
        problems = []
        if action.get('kind') not in ENGINE_KINDS: problems.append(f"kind {action.get('kind')}")
        bad_out = [o[0] for o in action.get('outputs', []) if isinstance(o, list) and o and o[0] not in ENGINE_OUTPUTS]
        if bad_out: problems.append('outputs ' + ','.join(bad_out))
        ph = action['hook'][0] if isinstance(action.get('hook'), list) else None
        hooks = idx['hook_ids']
        if ph and hooks and PROJ_HOOK.get(ph) and PROJ_HOOK[ph] not in hooks and not (ph == 'enter' and any(x.endswith('enters_battlefield') for x in hooks)):
            problems.append(f'projection hook {ph} disagrees with contract hook {", ".join(hooks)}')
        if action.get('gates', {}).get('optional') is False and c['modality'] == 'may' and c['kind'] == 'trigger':
            problems.append('clause says "may" but the projected action is mandatory')
        if proj and proj['unread']: problems.append('projected ability drops text: ' + proj['unread'][:120])
        add('C11_executable_shape', 'fail' if problems else 'pass', '; '.join(problems))
        if mana_out and any(o[0] == 'mana' for o in action.get('outputs', []) if isinstance(o, list)):
            add('C15_engine_mana_colour', 'warn', '0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel')
    return ch


LAND_TO_BF = re.compile(r"(?:search your library|from your hand|from your graveyard|top card of your library)[^.]*\bland cards?\b[^.]*onto the battlefield"
                        r"|put (?:a|an|up to \w+|any number of) (?:basic )?land cards? [^.]*onto the battlefield"
                        r"|return [^.]*\bland cards?\b[^.]*(?:to|onto) the battlefield|create [^.]*\bland\b[^.]*token|you may play (?:an additional land|lands from)")


def hook_subject(event, name):
    """'self' when the trigger watches only this object, 'others' when it watches other objects, 'both'."""
    if not event: return None
    e = norm(event)
    short = [x.lower() for x in {name, name.split(' // ')[0], name.split(',')[0]} if len(x) > 3]
    selfish = bool(re.search(r'\bthis (?:creature|artifact|enchantment|land|permanent|vehicle|card)\b|~', e)) or any(x in e for x in short)
    other = bool(re.search(r'\b(?:another|a|an|one or more|each|any|other)\b', re.sub(r'\bthis \w+', '', e)))
    return 'both' if selfish and other else 'self' if selfish else 'others'


def feeds(contract, effects):
    """Effects this operation makes happen for its controller (persisted for the discovery queries)."""
    eff = set(effects)
    low = norm(contract['exact_text'])
    if re.search(r"\b(?:its controller|that player|target opponent|each opponent) (?:may )?search", low): eff.discard('card.search')
    elif LAND_TO_BF.search(low): eff.add('land_to_battlefield')
    for p in contract['result']['produces']:
        if p.get('granted_to_other_object'): eff.discard(p['id'])
        if p['id'] == 'permanent.sacrifice' and p.get('actor') == 'granted ability': eff.discard(p['id'])
        if p['id'] == 'permanent.tap': eff.add('permanent.tap')
    return sorted(eff)


def contract_sha(contract, action):
    return F.sha(F.dumps(contract), F.dumps(action))


# ---------------------------------------------------------------- compiler
# What the 0.3.0 engine actually does with an action (engine.Game.resolve / pay). Anything else in a
# contract is information the engine would silently drop, so the compile is lossy.
ENGINE_EXECUTES = {'token', 'drain', 'reach', 'draw', 'scry_surveil', 'counters', 'life', 'charge', 'pump_team', 'pump_team_x'}
OUTPUT_TRANSITIONS = {'draw': {('library', 'hand')}, 'token': {('none', 'battlefield')}}
ENGINE_COST_FAMILIES = {'tap', 'sacrifice', 'mana'}


def runtime_losses(contract, action):
    """Every way running `action` in the 0.3.0 engine would lose what the contract says. [] = lossless."""
    L = []
    add = lambda code, detail='': L.append((code, detail))
    if not action: add('no_action', 'no 0.3.0 action matches this clause'); return L
    if action.get('kind') not in ENGINE_KINDS: add('action_kind', str(action.get('kind')))
    if action.get('confidence') not in (None, 'typed'): add('partial_projection', str(action.get('confidence')))
    if action.get('unread'): add('unread_text', action['unread'][:160])
    outs = [o for o in action.get('outputs') or [] if isinstance(o, (list, tuple)) and o]
    for p in contract['result']['produces']:
        if p['id'] == 'mana.add' and not p.get('granted_to_other_object'):
            m = p.get('mana') or {}
            add('mana_type_lost', f"contract: {m.get('mode')} {''.join(m.get('symbols') or []) or ''} x{m.get('amount')}; action: amount only")
    for o in outs:
        if o[0] not in ENGINE_EXECUTES and o[0] != 'mana': add('output_not_executed', o[0])
        # engine.resolve puts counters on the source or on ONE creature, never on each of a group
        if o[0] == 'counters' and len(o) > 2 and re.match(r'(?:each|all|up to|any number)', str(o[2])): add('distribution_lost', str(o[2]))
    covered = set().union(*[OUTPUT_TRANSITIONS.get(o[0], set()) for o in outs]) if outs else set()
    for t in contract['result']['transitions']:
        if 'from' in t and (t['from'], t['to']) not in covered: add('zone_transition_lost', f"{t['effect']}: {t['from']} -> {t['to']}")
    groups = contract['initiation']['requirement_groups']
    for g in groups:
        if g['class'] == 'eligibility': add('target_lost', g['alternatives'][0].get('text', ''))
        if g['class'] == 'trigger':
            for h in g['alternatives']:
                q = h.get('qualifiers', {})
                if q.get('cardinality') == 'one_or_more' and not (action.get('gates') or {}).get('batch'): add('batching_lost', h.get('text', ''))
                if q.get('actor') in ('opponent', 'any_player') or q.get('controller') == 'opponent': add('observer_relation_lost', h.get('text', ''))
        if g['class'] == 'cost':
            c = g['alternatives'][0]
            if c.get('family') not in ENGINE_COST_FAMILIES: add('cost_lost', f"{c.get('family')}: {c.get('text', '')}")
            elif c.get('family') == 'mana':
                odd = [x['symbol'] for x in c['pips'] if x['type'] not in ('generic', 'colored')]
                if odd: add('cost_mana_type_lost', ' '.join(odd))
    for a in contract['initiation']['amplifiers']: add('amplifier_lost', a['text'])
    gates = action.get('gates') or {}
    if contract['modality'] == 'may' and contract['kind'] == 'trigger' and gates.get('optional') is not True: add('optional_lost', 'may')
    if contract['capacity'] and not gates.get('once_per_turn'): add('capacity_lost', contract['capacity'][0]['text'])
    for u in contract['unbound']: add('branch_unbound', u)
    if contract['initiation']['choice']: add('modes_lost', str(contract['initiation']['choice'].get('cardinality')))
    if contract['granted_abilities']: add('granted_ability', contract['granted_abilities'][0][:80])
    if (contract.get('keyword_macro') or {}).get('role') == 'reminder_text_of_macro': add('reminder_text', contract['keyword_macro']['macro'])
    return L


def compile_action(contract, action, review_id):
    """Semantically reviewed contract -> engine action. Refuses any compile that would lose meaning."""
    losses = runtime_losses(contract, action)
    if losses: raise ValueError('lossy compile: ' + '; '.join(f'{c} ({d})' for c, d in losses[:6]))
    return dict(action, provenance={'contract_text': contract['exact_text'], 'review_id': review_id, 'compiler': COMPILER_VERSION})
