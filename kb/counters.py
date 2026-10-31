"""Counter identity for DIO operation contracts (C-015, C-016; Zach 2026-10-31).

Every mention of counters in a contract's exact text becomes a facet {role, kind, holder, ...}:

  role    put | remove | move | listen_put | listen_remove | measure | require | enters_with | modify_put | proliferate | mention
  kind    '+1/+1', '-1/-1', a named kind ('nest', 'stun', 'poison', 'lore', ...), 'any' (generic wording:
          "a counter", "each counter", "counters"), or 'present_kinds' (proliferate: only kinds already there)
  holder  permanent | player | unread

DIO v3.1.1 says a counter's sign must not be assumed (state table: "May be a buff, a gate, a clock, a capacity or a
liability"). These facets keep the kind through Oracle -> contract (P-02). They are drafted, not reviewed.

Matching (`match`): a named producer and a named listener must name the same kind; an 'any' listener accepts every
kind; a named listener against an 'any' producer is only 'possible'; proliferate adds only kinds already present.

Order of operations the facets do not decide on their own (kept as rules notes, scenario-tested elsewhere):
- "Enters with" counters are part of the entering event (CR 614.1c). A replacement that changes how many counters are
  put (Loading Zone, "twice that many") applies to them as the object enters, so no other ability can add a +1/+1
  counter "first".
- State-based actions are checked simultaneously (CR 704.3). A creature with toughness 0 or less is put into the
  graveyard (704.5f) in the same check that removes +1/+1 and -1/-1 counter pairs (704.5q), so cancellation never
  rescues a creature that is already at 0 toughness.
"""
import re

DRAFTER = 'counters-0.1.0'
CARD_DRAFTER = 'card-counters-0.1.0'
PLAYER_KINDS = {'poison', 'energy', 'experience', 'rad', 'ticket'}
GENERIC = {'a', 'an', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'x', 'that', 'many', 'those', 'more', 'each', 'the',
           'of', 'all', 'its', 'their', 'no', 'any', 'additional', 'another', 'twice', 'his', 'her', 'number', 'kind', 'with',
           'put', 'remove', 'move', 'get', 'gets', 'and', 'or', 'this', 'than', 'least', 'amount', 'same', 'these', 'such', 'times',
           'thrice', 'double', 'had', 'has', 'have', 'half', 'kinds', 'single', 'triple', 'exactly', 'distributed', 'total'}
VERB_COUNTER = re.compile(r"\bcounter(?=\s+(?:target|that|it\b|up to|all|the next|the chosen|each spell|any|a spell|an? (?:activated|triggered)))")
NOUN = re.compile(r"((?:[+-]\d+/[+-]\d+)|[a-z'\-]+)\s+counters?\b")
PLAYER_HOLDER = re.compile(r"\bon (?:target player|target opponent|each opponent|each player|that player|you|your opponents?|"
                           r"each of your opponents|its controller|that creature's controller)\b")
PLAYER_GETS = re.compile(r"\b(?:you|each opponent|each player|target player|target opponent|that player|its controller|"
                         r"each of your opponents|your opponents) gets?\b[^.]*?\bcounters?\b")


def _norm(s):
    return re.sub(r'\s+', ' ', str(s).replace('−', '-').replace('—', '-').replace('–', '-')).strip().lower()


def _kind(word):
    return 'any' if word in GENERIC else word


def _holder(kind, after, before):
    if kind in PLAYER_KINDS:
        return 'player'
    if PLAYER_HOLDER.match(after) or PLAYER_GETS.search(before[-80:] + ' counter') or \
            re.search(r'\b(?:you|each opponent|each player|target player|that player) (?:loses?|has|have|had)\b[^.]*$', before[-60:]):
        return 'player'
    if re.match(r'\bon (?:him|her|it|them|this|that|target|each|another|a|an|up to|one|any|other|~|enchanted|equipped)\b', after) or \
            re.search(r'\b(?:creature|permanent|artifact|land|planeswalker|saga|spacecraft|planet)s?\b', after[:60] + ' ' + before[-60:]):
        return 'permanent'
    return 'unread'


ROLE_WORDS = [  # (pattern, role); the keyword nearest before the counter noun, in the same clause segment, decides
    (r'\b(?:onto|to) the battlefield\b[^.:;]*\bwith\b', 'enters_with'), (r'\benters?(?: the battlefield)?(?: tapped)? with\b', 'enters_with'),
    (r'\bmove\b', 'move'), (r'\bremove[sd]?\b|\blos(?:e|es|t)\b', 'remove'),
    (r'\bdouble the number of\b', 'double'),
    (r'\bfor each\b|\bnumber of\b|\bequal to\b|\bas many\b|\bfor every\b', 'measure'),
    (r'\bputs?\b|\bplaced?\b|\bgets?\b|\bdistribute\b|\badditional\b', 'put'),
    (r'\bwith\b|\bhas\b|\bhave\b|\bhad\b|\bwithout\b|\bno\b', 'require')]


def _role(before, after, in_trigger):
    after = after.strip()
    if re.match(r'(?:\S+ ){0,2}(?:would be put|would be placed|would be removed)', after):
        return 'modify_remove' if 'removed' in after[:40] else 'modify_put'
    if in_trigger and re.match(r'(?:\S+ ){0,6}?(?:is|are) (?:put|placed)\b', after):
        return 'listen_put'
    if in_trigger and re.match(r'(?:\S+ ){0,6}?(?:is|are) removed\b', after):
        return 'listen_remove'
    seg = re.split(r'[.:;•]|, then\b', before)[-1]
    best, role = -1, 'mention'
    for pat, r in ROLE_WORDS:
        for m in re.finditer(pat, seg):
            if m.end() > best or (m.end() == best and r == 'enters_with'):
                best, role = m.end(), r
    if re.search(r'\b(?:gets?|puts?|distribute) (?:a|the) number of\s*$', seg):
        role = 'put'
    if in_trigger and role in ('put', 'remove'):
        return 'listen_' + role
    if role == 'put' and re.search(r'\bif\b[^,]*$', seg) and re.search(r'^[^.]*\bthis turn\b', after):
        return 'condition_put'          # "if you put a counter on a creature this turn": history, not an output
    return role


def _self_names(t, name):
    for n in sorted({name, name.split(' // ')[0], name.split(',')[0], name.split(' ')[0]} if name else (), key=len, reverse=True):
        if len(n) > 3:
            t = re.sub(r'\b' + re.escape(_norm(n)) + r'\b', 'this permanent', t)
    return t


def facets(text, trigger_event=None, name=None):
    """Counter facets of one ability's exact text. `trigger_event` is the trigger's event phrase, if it is a trigger;
    `name` is the card's name, so "put a counter on Ajani" reads as this permanent."""
    t = _self_names(_norm(re.sub(r'\([^)]*\)', '', text)), name)    # reminder text belongs to its keyword
    t = VERB_COUNTER.sub('COUNTERSPELL', t)
    trig = _self_names(_norm(trigger_event), name) if trigger_event else ''
    out = []
    if trig:
        for m in NOUN.finditer(trig):
            kind = _kind(m.group(1))
            out.append({'role': _role(trig[:m.end(1)] if m.group(1) in GENERIC else trig[:m.start()], trig[m.end():], True), 'kind': kind, 'holder': _holder(kind, trig[m.end():].strip(), trig[:m.start()]),
                        'text': trig[max(0, m.start() - 30):m.end() + 20].strip()})
        t = t.replace(trig, ' ', 1)
    for m in NOUN.finditer(t):
        kind = _kind(m.group(1))
        before = t[:m.end(1)] if m.group(1) in GENERIC else t[:m.start()]
        after = t[m.end():].strip()
        role = _role(before, t[m.end():], False)
        if role == 'double':
            role, kind = 'put', 'present_kinds'
        f = {'role': role, 'kind': kind, 'holder': _holder(kind, after, before),
             'text': t[max(0, m.start() - 30):m.end() + 20].strip()}
        if 'would be put' in t and f['role'] in ('mention', 'put') and re.search(r'\binstead\b', t):
            f['role'] = 'modify_put'        # the replacement's own result ("twice that many ... are put on it instead")
        if f['role'] == 'modify_put' and re.search(r'\btwice that many\b|\bthat many plus\b|\binstead\b', t):
            f['modifier'] = 'doubles' if 'twice that many' in t else 'adds' if 'plus' in t else 'replaces'
        out.append(f)
    if '{e}' in t and not any(f['kind'] == 'energy' for f in out):
        role = 'remove' if re.search(r'\bpay [^.]*\{e\}', t) else 'put'
        out.append({'role': role, 'kind': 'energy', 'holder': 'player', 'text': '{E}'})
    if re.search(r'\bproliferate\b', t):
        out.append({'role': 'proliferate', 'kind': 'present_kinds', 'holder': 'permanent_or_player', 'text': 'proliferate'})
    return out


def produced_kinds(fs):
    """Kinds of counters an ability puts (proliferate puts 'present_kinds')."""
    return [f['kind'] for f in fs if f['role'] in ('put', 'enters_with', 'proliferate')]


def match(produced, listened):
    """'compatible' | 'possible' | 'incompatible' for a producer's counter kind against a listener's."""
    if listened == 'any':
        return 'compatible'
    if produced in ('any', 'present_kinds'):
        return 'possible'
    return 'compatible' if produced == listened else 'incompatible'


def polarity_note(kinds_a, kinds_b):
    """A rules note when one side puts -1/-1 counters and the other puts or reads +1/+1 counters (CR 704.5q)."""
    a, b = set(kinds_a), set(kinds_b)
    if ('-1/-1' in a and '+1/+1' in b) or ('+1/+1' in a and '-1/-1' in b):
        return ('+1/+1 and -1/-1 counters on one permanent are removed in pairs as a state-based action (CR 704.5q), in the '
                'same check that puts a creature with 0 or less toughness into the graveyard (704.5f, 704.3)')
    return None


# Keyword macros whose counters live in reminder text (stripped above) or in the rules, not in printed words.
# (keyword, [(role, kind, holder)]). Drafted from the Comprehensive Rules' keyword definitions; not reviewed.
KEYWORDS = {
    'persist': [('require', '-1/-1', 'permanent'), ('enters_with', '-1/-1', 'permanent')],      # CR 702.79
    'undying': [('require', '+1/+1', 'permanent'), ('enters_with', '+1/+1', 'permanent')],      # CR 702.93
    'wither': [('put', '-1/-1', 'permanent')],                                                  # CR 702.80
    'infect': [('put', '-1/-1', 'permanent'), ('put', 'poison', 'player')],                     # CR 702.90
    'toxic': [('put', 'poison', 'player')], 'poisonous': [('put', 'poison', 'player')],
    'modular': [('enters_with', '+1/+1', 'permanent'), ('move', '+1/+1', 'permanent')],         # CR 702.43
    'graft': [('enters_with', '+1/+1', 'permanent'), ('move', '+1/+1', 'permanent')],
    'riot': [('enters_with', '+1/+1', 'permanent')], 'unleash': [('enters_with', '+1/+1', 'permanent')],
    'bloodthirst': [('enters_with', '+1/+1', 'permanent')], 'devour': [('enters_with', '+1/+1', 'permanent')],
    'sunburst': [('enters_with', 'any', 'permanent')], 'amplify': [('enters_with', '+1/+1', 'permanent')],
    'evolve': [('put', '+1/+1', 'permanent')], 'outlast': [('put', '+1/+1', 'permanent')],
    'bolster': [('put', '+1/+1', 'permanent')], 'adapt': [('put', '+1/+1', 'permanent')],
    'monstrosity': [('put', '+1/+1', 'permanent')], 'support': [('put', '+1/+1', 'permanent')],
    'training': [('put', '+1/+1', 'permanent')], 'backup': [('put', '+1/+1', 'permanent')],
    'mentor': [('put', '+1/+1', 'permanent')], 'fabricate': [('put', '+1/+1', 'permanent')],
    'renown': [('put', '+1/+1', 'permanent')], 'dethrone': [('put', '+1/+1', 'permanent')],
    'scavenge': [('put', '+1/+1', 'permanent')], 'reinforce': [('put', '+1/+1', 'permanent')],
    'exploit': [], 'vanishing': [('enters_with', 'time', 'permanent'), ('remove', 'time', 'permanent')],
    'fading': [('enters_with', 'fade', 'permanent'), ('remove', 'fade', 'permanent')],
    'cumulative upkeep': [('put', 'age', 'permanent')], 'suspend': [('put', 'time', 'permanent'), ('remove', 'time', 'permanent')],
    'level up': [('put', 'level', 'permanent')], 'saga': [('enters_with', 'lore', 'permanent'), ('put', 'lore', 'permanent')],
}
KEYWORD_LINE = re.compile(r"^(" + '|'.join(sorted((re.escape(k) for k in KEYWORDS), key=len, reverse=True)) + r")\b")


def card_facets(rules_text, name=None, type_line=''):
    """Card-level counter facets from a card's whole rules text, including what operation contracts miss: keyword macros
    (persist, infect, modular, ...) and static "enters with" lines, and keywords it grants ("as though its source had wither"). Each facet carries `source`:
    the line it came from, 'keyword:<name>' or 'grants:<name>'."""
    out = []
    if 'saga' in (type_line or '').lower():
        out += [{'role': r, 'kind': k, 'holder': h, 'text': 'saga', 'source': 'keyword:saga'} for r, k, h in KEYWORDS['saga']]
    for line in str(rules_text or '').split('\n'):
        low = _self_names(_norm(re.sub(r'\([^)]*\)', '', line)), name)
        for part in re.split(r',\s*', low) if re.fullmatch(r"[a-z ,\d{}/+-]+", low or '-') else [low]:
            m = KEYWORD_LINE.match(part.strip())
            if m:
                out += [{'role': r, 'kind': k, 'holder': h, 'text': part.strip(), 'source': 'keyword:' + m.group(1)} for r, k, h in KEYWORDS[m.group(1)]]
        for g in re.finditer(r'\b(?:has|have|had|gains?|gets|with) (?:[a-z]+(?: \d+)?,? (?:and )?){0,3}?(wither|infect|persist|undying|toxic|modular|riot)\b', low):
            out += [{'role': r, 'kind': k, 'holder': h, 'text': g.group(0), 'source': 'grants:' + g.group(1)} for r, k, h in KEYWORDS[g.group(1)]]
        trig = re.match(r'^((?:when|whenever|at)\b[^,]*),', low)
        for f in facets(line, trig.group(1) if trig else None, name):
            f['source'] = line.strip()[:160]
            out.append(f)
    return out


def counter_order_note(fs):
    """Order-of-operations note for a card that enters with -1/-1 counters (Reaping Willow, persist returns)."""
    if any(f['role'] == 'enters_with' and f['kind'] == '-1/-1' for f in fs):
        return ('Enters with -1/-1 counters. A replacement that changes how many counters it gets (Loading Zone doubles them) '
                'applies as it enters (CR 614.1c). If its toughness is then 0 or less it dies at the next state-based '
                'check (704.5f) before any player can act, so +1/+1 counters put on it later cannot cancel the -1/-1 counters '
                '(704.5q) in time. Counters it has at the same moment do cancel, and toughness counts both (704.3: the checks are simultaneous).')
    return None
