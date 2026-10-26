"""Domain grammar for Oracle text: ability boundaries, ability kind, parts, and clause frames.

Three levels, each kept separately so a reviewer can see where a reading came from:

  ability  one rules ability (a keyword, a triggered/activated/static ability, a spell effect, a mode)
  part     one grammatical role inside the ability: cost, trigger_event, condition, effect, static,
           amplifier, duration, restriction, link, keyword, mode_header, ...
  frame    the part's text with its noun phrases, players, zones, numbers and mana replaced by typed
           slots. Frames are the templates the registry maps to DIO concepts. Slot values are kept
           per occurrence as bindings.

No meaning is assigned here. concepts.py does that from (role, frame).
"""
import re
from lexicon import (KEYWORD_ABILITIES, ABILITY_WORDS, TYPE_WORDS, HEAD_WORDS, PREMODS, NUMBER_WORDS,
                     LEMMA, ACTION_VERB_START, ZONE_PHRASES, COLORS, plural)

GRAMMAR_VERSION = 'grammar-0.2.0'

# ---------------------------------------------------------------- text preparation

REMINDER = re.compile(r'\s*\((?:[^()]|\([^()]*\))*\)')
SELF_NOUNS = ('creature|artifact|enchantment|land|permanent|spell|card|aura|equipment|vehicle|saga|'
              'planeswalker|battle|class|case|room|token|siege|fortification|contraption|attraction|'
              'background|plan|shrine|spacecraft|planet|cave|desert|gate|sorcery|instant|'
              'artifact creature|enchantment creature|land creature|kindred [a-z]+|object|source|face|ability')


def self_names(card_name, face_name):
    names = {card_name, face_name}
    for n in list(names):
        if n and ', ' in n:
            names.add(n.split(', ')[0])
        if n and ' of the ' in n:
            names.add(n.split(' of the ')[0])
        if n and ' // ' in n:
            names.update(n.split(' // '))
    return sorted({n for n in names if n and len(n) > 2}, key=len, reverse=True)


def prep(text, names):
    t = text.replace('−', '-').replace('—', '—').replace('’', "'")
    for n in names:
        t = re.sub(r'(?<![A-Za-z])' + re.escape(n) + r'(?![A-Za-z])', '~', t)
    return t


def strip_reminder(line):
    reminders = [m.group(0).strip() for m in REMINDER.finditer(line)]
    return REMINDER.sub('', line).strip(), reminders


def top_level(s, i):
    """True when position i of s is outside quotation marks."""
    return s[:i].count('"') % 2 == 0 and s[:i].count('“') == s[:i].count('”')


def split_top(s, sep_re):
    out, last = [], 0
    for m in re.finditer(sep_re, s):
        if top_level(s, m.start()):
            out.append(s[last:m.start()])
            last = m.end()
    out.append(s[last:])
    return [x for x in out if x.strip()]


# ---------------------------------------------------------------- keyword lines

KW_RE = re.compile(r'^(?:' + '|'.join(re.escape(k) for k in KEYWORD_ABILITIES) +
                   r'|[a-z]+walk|[a-z]+cycling|protection from .+|hexproof from .+)\b', re.I)


def keyword_items(line, card_keywords):
    """Return the keyword items if every comma/semicolon item of the line is a keyword ability, else None."""
    if not line or line.endswith(':'):
        return None
    items = [x.strip() for x in re.split(r'[,;] (?![^{]*\})', line.rstrip('.'))]
    if not items:
        return None
    kws = []
    for it in items:
        m = KW_RE.match(it)
        if not m:
            return None
        head = m.group(0).lower()
        rest = it[m.end():].strip()
        # A keyword followed by a sentence ("Flying. Draw a card") is not a keyword line.
        if rest and not re.match(r'^(\{[^}]+\}|\d+|X|—|-|[a-z]|from|with|for|\()', rest) and not rest.startswith('{'):
            if not (card_keywords and any(head.startswith(k.lower()) for k in card_keywords)):
                return None
        kws.append((head, rest))
    return kws


# ---------------------------------------------------------------- abilities

ROMAN = r'(?:I|II|III|IV|V|VI|VII)'
CHAPTER_RE = re.compile(r'^(' + ROMAN + r'(?:, ' + ROMAN + r')*) — (.*)$')
LOYALTY_RE = re.compile(r'^([+-]?(?:\d+|X)): (.*)$')
MODAL_RE = re.compile(r'(?:^|\b)(choose (?:one|two|three|four|five|one or both|one or more|any number|up to (?:one|two|three|four|five)|X|one or two|two or three|one —)(?: (?:that hasn\'t been chosen|of them|instead|—))?[^—•]*?) ?—\s*$', re.I)
ABILITY_WORD_RE = re.compile(r'^([A-Z][A-Za-z\'’ -]{2,40}?) — (.+)$')
LEVEL_RE = re.compile(r'^(LEVEL \d+(?:-\d+|\+)|\d+/\d+|Level \d+(?:-\d+|\+)?)$')
TRIGGER_START = re.compile(r'^(When|Whenever|At)\b')
COST_VERB = re.compile(r'^(?:\{|Sacrifice|Tap|Untap|Discard|Exile|Pay|Remove|Return|Put|Reveal|Collect|Mill|'
                       r'Forage|Blight|Waterbend|Earthbend|Airbend|Firebend|Exert|Behold|Lose|Gain|\d|X|'
                       r'Mana|Energy|Loyalty|Q)', re.I)


class Ability(dict):
    """kind, text, parts, keyword, ability_word, line_index, granted_by (for quoted abilities)."""


def segment_face(text, type_line, card_keywords):
    """Yield Ability dicts for one face's Oracle text (already self-name substituted)."""
    lines = [l.strip() for l in text.split('\n')]
    is_spell = bool(re.search(r'\b(Instant|Sorcery)\b', type_line or ''))
    abilities = []
    pending_modal = None
    for li, raw in enumerate(lines):
        if not raw:
            continue
        line, reminders = strip_reminder(raw)
        if not line:
            abilities.append(Ability(kind='reminder_only', text=raw, line_index=li, parts=[], reminders=reminders,
                                     id=len(abilities)))
            continue
        if line.startswith('•') and pending_modal is not None:
            mode_text = line.lstrip('• ').strip()
            mode = Ability(kind='mode', text=mode_text, line_index=li, reminders=reminders,
                           parent=pending_modal['id'], id=len(abilities))
            mode_word = re.match(r'^([A-Z][A-Za-z\' -]{2,30}) — (.+)$', mode_text)
            if mode_word:  # Spree/escalate modes with their own costs: "+ {1} — ..." handled below
                mode['mode_label'], mode_text = mode_word.group(1), mode_word.group(2)
            spree = re.match(r'^\+ ((?:\{[^}]+\})+) — (.+)$', mode_text)
            if spree:
                mode['mode_cost'], mode_text = spree.group(1), spree.group(2)
            mode['text'] = mode_text
            mode['parts'] = decompose_body(mode_text, 'effect')
            if spree:
                mode['parts'].insert(0, part('cost', spree.group(1)))
            abilities.append(mode)
            continue
        pending_modal = None
        ab = Ability(text=line, line_index=li, reminders=reminders, id=len(abilities))
        m = ABILITY_WORD_RE.match(line)
        if m and (m.group(1).lower() in ABILITY_WORDS or not KW_RE.match(m.group(1))) and not CHAPTER_RE.match(line):
            ab['ability_word'] = m.group(1)
            line = m.group(2)
            ab['text'] = line
        striation = re.match(r'^(\d+)\+ \| (.+)$', line)
        if striation:
            # station: "N+ | abilities" means "as long as this has N or more charge counters on it, it has
            # [abilities]" (CR 702.184, release notes). Each inner ability keeps its own kind and gets the
            # threshold as a state condition.
            n = striation.group(1)
            for inner in segment_face(striation.group(2), type_line, card_keywords):
                inner['id'] = len(abilities)
                inner['line_index'] = li
                inner['station_threshold'] = int(n)
                cond = part('condition', f'as long as ~ has {n} or more charge counters on it', station=int(n))
                inner['parts'] = [cond] + inner.get('parts', [])
                if inner['kind'] == 'keyword':
                    inner['kind'] = 'static'
                    inner['parts'] = [cond, part('static', 'has ' + inner['text'].lower())]
                abilities.append(inner)
            continue
        if LEVEL_RE.match(line):
            ab.update(kind='structure', parts=[part('structure', line)])
        elif CHAPTER_RE.match(line):
            ch = CHAPTER_RE.match(line)
            ab.update(kind='chapter', chapters=ch.group(1))
            ab['parts'] = [part('trigger_event', 'chapter ' + ch.group(1))] + decompose_body(ch.group(2), 'effect')
        elif keyword_items(line, card_keywords) is not None:
            kws = keyword_items(line, card_keywords)
            for k, rest in kws:
                kab = Ability(kind='keyword', text=(k + (' ' + rest if rest else '')), line_index=li,
                              reminders=reminders, keyword=k, keyword_param=rest, id=len(abilities))
                kab['parts'] = [part('keyword', kab['text'])]
                abilities.append(kab)
            continue
        elif LOYALTY_RE.match(line):
            lm = LOYALTY_RE.match(line)
            ab['kind'] = 'loyalty'
            ab['parts'] = [part('cost', 'loyalty ' + lm.group(1))] + decompose_body(lm.group(2), 'effect')
        elif TRIGGER_START.match(line):
            ab['kind'] = 'triggered'
            ab['parts'] = decompose_trigger(line)
        elif activated_split(line):
            cost, body = activated_split(line)
            ab['kind'] = 'activated'
            ab['parts'] = [part('cost', c.strip()) for c in split_cost(cost)] + decompose_body(body, 'effect')
        elif is_spell and not re.match(r'^(This spell|~ (?:can\'t|costs|has|is)|As an additional cost|You may cast|'
                                       r'Spells|If ~ would|Cast ~ only|Buyback|Delve|Convoke)', line):
            ab['kind'] = 'spell'
            ab['parts'] = decompose_body(line, 'effect')
        elif re.match(r'^As an additional cost to cast (?:this spell|~|[a-z ]+spells?)(?: you cast)?, (.+)$', line):
            am = re.match(r'^As an additional cost to cast (?:this spell|~|[a-z ]+spells?)(?: you cast)?, (.+)$', line)
            ab['kind'] = 'additional_cost'
            ab['parts'] = [part('cost_header', 'as an additional cost to cast this spell')] + \
                          [part('cost', c) for c in split_top(am.group(1).rstrip('.'), r', or |, | or ')]
        else:
            ab['kind'] = 'static'
            if re.search(r'\binstead\b|\benters with\b|^As ~ enters|\benters tapped\b|\bwould\b|\bskip\b|'
                         r'\benters as\b|\benter tapped\b|\benter with\b', line):
                ab['kind'] = 'replacement'
            ab['parts'] = decompose_body(line, 'static')
        if MODAL_RE.search(ab['text']):
            pending_modal = ab
        abilities.append(ab)
    # quoted (granted) abilities become nested abilities
    out = []
    for ab in abilities:
        out.append(ab)
        for p in ab.get('parts', []):
            for q in re.findall(r'"([^"]+)"', p['text']):
                nested = segment_face(q, '', card_keywords)
                for n in nested:
                    n['granted_by'] = ab['id']
                    n['id'] = ('g', ab['id'], n['id'])
                    if n.get('parent') is not None:
                        n['parent'] = ('g', ab['id'], n['parent'])
                    n['line_index'] = ab['line_index']
                    out.append(n)
    return out


def activated_split(line):
    idx = None
    for m in re.finditer(r': ', line):
        if top_level(line, m.start()):
            idx = m.start()
            break
    if idx is None:
        return None
    cost = line[:idx]
    if '. ' in cost or len(cost) > 160 or TRIGGER_START.match(cost):
        return None
    if not COST_VERB.match(cost) and not re.match(r'^[A-Z][a-z]+(?: [a-z]+)? \{', cost):
        return None
    return cost, line[idx + 2:]


def split_cost(cost):
    return split_top(cost, r', (?![^{]*\})')


def part(role, text, **kw):
    d = {'role': role, 'text': text.strip().rstrip('.').strip()}
    d.update(kw)
    return d


TRIGGER_LIST_CONT = re.compile(r'^(?:or |and |and/or )|^(?:' + '|'.join(sorted(
    {'artifact', 'creature', 'enchantment', 'land', 'planeswalker', 'instant', 'sorcery', 'battle', 'kindred',
     'white', 'blue', 'black', 'red', 'green', 'noncreature', 'nonland', 'aura', 'equipment', 'vehicle'})) +
                               r')\b')


def decompose_trigger(line):
    m = TRIGGER_START.match(line)
    word = m.group(1)
    rest = line[m.end():].strip()
    cut = None
    for cm in re.finditer(r', ', rest):
        if not top_level(rest, cm.start()):
            continue
        after = rest[cm.end():]
        if TRIGGER_LIST_CONT.match(after):
            continue
        cut = cm
        break
    if cut is None:
        return [part('trigger_event', word.lower() + ' ' + rest, trigger_word=word.lower()),
                part('residue', '', note='no effect after trigger')]
    event = rest[:cut.start()]
    body = rest[cut.end():]
    parts = [part('trigger_event', word.lower() + ' ' + event, trigger_word=word.lower())]
    im = re.match(r'^if (.+?), (.+)$', body)
    if im and top_level(body, im.end(1)):
        parts.append(part('condition', 'if ' + im.group(1), intervening=True))
        body = im.group(2)
    return parts + decompose_body(body, 'effect')


SENTENCE_SPLIT = r'(?<=[.])\s+(?=[A-Z~"])'
LEAD_LINKS = [
    (r'^If you do, ', 'link', 'if you do'), (r"^If you don't, ", 'link', "if you don't"),
    (r'^If you can\'t, ', 'link', "if you can't"),
    (r'^If they do, ', 'link', 'if they do'), (r"^If they don't, ", 'link', "if they don't"),
    (r'^If that player does, ', 'link', 'if that player does'),
    (r"^If that player doesn't, ", 'link', "if that player doesn't"),
    (r'^If no one does, ', 'link', 'if no one does'),
    (r'^When you do, ', 'link', 'when you do'), (r'^Whenever you do, ', 'link', 'whenever you do'),
    (r'^Otherwise, ', 'link', 'otherwise'), (r'^Then ', 'link', 'then'), (r'^Then, ', 'link', 'then'),
    (r'^Also, ', 'link', 'also'),
    (r'^Until end of turn, ', 'duration', 'until end of turn'),
    (r'^Until your next turn, ', 'duration', 'until your next turn'),
    (r'^Until the end of your next turn, ', 'duration', 'until the end of your next turn'),
    (r'^This turn, ', 'duration', 'this turn'),
    (r'^For as long as ([^,]+), ', 'duration', None),
    (r'^As long as ([^,]+), ', 'condition', None),
    (r'^Unless ([^,]+), ', 'condition', None),
    (r'^For each ([^,]+), ', 'amplifier', None),
    (r'^During ([^,]+), ', 'timing', None),
    (r'^At the beginning of ([^,]+), ', 'delayed_trigger', None),
    (r'^At end of combat, ', 'delayed_trigger', 'at end of combat'),
    (r'^Each (?:turn|combat), ', 'timing', None),
    (r'^Once each turn, ', 'restriction', 'once each turn'),
    (r'^After this (?:main )?phase, ', 'timing', None),
]
RESTRICTION_RE = re.compile(r'^((?:Activate|Station|Crew|Saddle) (?:only|this ability only|no more than)|This ability triggers only|'
                            r'Spend this mana only|~ can\'t be countered|This spell can\'t be countered|'
                            r'It\'s still a land|Any player may activate|You may activate|'
                            r'(?:Cast|Play) (?:~|this spell) only|This ability can\'t be|Activate each|'
                            r'Do this only|Only your opponents|Exile it instead|This effect doesn\'t|'
                            r'It can\'t be|They can\'t be|That (?:creature|token)? ?can\'t be)', re.I)
TAIL_MODS = [
    (r',? where X is (.+)$', 'amplifier'),
    (r' equal to (?!the number of)(.+)$', 'amplifier'), (r' equal to the number of (.+)$', 'amplifier'),
    (r' for each (.+)$', 'amplifier'),
    (r',? unless (.+)$', 'condition'),
    (r' until end of turn$', 'duration'), (r' until your next turn$', 'duration'),
    (r' until the end of your next turn$', 'duration'),
    (r' for as long as (.+)$', 'duration'), (r' until (~ leaves the battlefield|.+ leaves the battlefield)$', 'duration'),
    (r' this turn$', 'duration'),
    (r',? if (.+)$', 'condition'),
    (r' only (?:during your turn|as a sorcery|any time you could cast a sorcery)$', 'restriction'),
    (r' instead$', 'replacement_marker'),
    (r' at the beginning of (?:the next|your next|the next turn\'s) [a-z ]+$', 'delayed_trigger'),
]


def decompose_body(body, role):
    parts = []
    body = body.strip()
    if not body:
        return parts
    modal = MODAL_RE.search(body)
    if modal:
        head = body[:modal.start()].strip()
        parts += decompose_body(head, role) if head else []
        parts.append(part('mode_header', modal.group(1)))
        return parts
    for sent in split_top(body, SENTENCE_SPLIT):
        sent = sent.strip()
        if not sent:
            continue
        if RESTRICTION_RE.match(sent):
            parts.append(part('restriction', sent))
            continue
        changed = True
        while changed:
            changed = False
            for pat, prole, label in LEAD_LINKS:
                m = re.match(pat, sent)
                if m:
                    txt = label if label else m.group(0).rstrip(', ').strip()
                    parts.append(part(prole, txt))
                    sent = sent[m.end():]
                    sent = sent[:1].upper() + sent[1:] if sent else sent
                    changed = True
                    break
        lead_if = re.match(r'^If (.+?), (?=[a-z~])', sent)
        if lead_if and top_level(sent, lead_if.end()) and ' would ' not in lead_if.group(1):
            parts.append(part('condition', 'if ' + lead_if.group(1)))
            sent = sent[lead_if.end():]
        if re.match(r'^If .+ would ', sent):
            parts.append(part('replacement', sent))
            continue
        for clause in split_clauses(sent):
            parts.extend(peel_tail(clause, role))
    return parts


CLAUSE_VERB = r'(?:' + '|'.join(re.escape(v) for v in ACTION_VERB_START) + r')\b'
SUBJECT = r'(?:(?:you|each (?:player|opponent)|target (?:player|opponent)|that player|its controller|its owner|they)\s+)?'


def split_clauses(sent):
    sent = sent.rstrip('.').strip()
    pieces = split_top(sent, r', then |\. Then |, and then | and then |, (?=' + SUBJECT + CLAUSE_VERB + r')')
    out = []
    for p in pieces:
        sub = split_top(p, r'(?:,)? and (?=' + SUBJECT + CLAUSE_VERB + r')')
        if len(sub) > 1:
            first = sub[0]
            # "Exile target creature and its controller gains..." keep; "X and Y" object lists are not split
            # because the right side must begin with a verb.
            out.append(first)
            out.extend(sub[1:])
        else:
            out.append(p)
    return [o.strip() for o in out if o.strip()]


def peel_tail(clause, role):
    """Pull trailing modifiers off a clause so the core frame is reusable."""
    tails = []
    c = clause.strip().rstrip('.')
    # "put charge counters equal to its power on this Spacecraft": the destination belongs to the core frame
    c = re.sub(r'^(.*\bput (?:a number of )?[^,]*?counters?) (equal to [^,]+?) (on [^,]+)$', r'\1 \3 \2', c, flags=re.I)
    changed = True
    while changed:
        changed = False
        for pat, trole in TAIL_MODS:
            m = re.search(pat, c)
            if m and top_level(c, m.start()) and m.start() > 6:
                core = c[:m.start()].rstrip(', ')
                if trole == 'condition' and ' if ' in m.group(0) and core.lower().startswith(('if ', 'when')):
                    continue
                txt = m.group(0).strip(', ')
                tails.insert(0, part(trole, txt))
                c = core
                changed = True
                break
    return [part(role, c)] + tails


# ---------------------------------------------------------------- frames (templates with typed slots)

NUM = r'(?:\d+|' + '|'.join(NUMBER_WORDS) + r')'
TYPE_ALT = sorted({re.escape(w) for w in TYPE_WORDS} | {re.escape(plural(w)) for w in TYPE_WORDS}, key=len, reverse=True)
HEAD_ALT = sorted({re.escape(w) for w in HEAD_WORDS}, key=len, reverse=True)
PREMOD_ALT = sorted({re.escape(w) for w in PREMODS} | {re.escape(w) for w in TYPE_WORDS}, key=len, reverse=True)
NON_X = r'non-?[a-z]+'
PREMOD = r'(?:' + NON_X + r'|' + '|'.join(PREMOD_ALT) + r'|[+-]?(?:\d+|x)/[+-]?(?:\d+|x)|' + NUM + r'-mana)'
PREMODS_SEQ = r'(?:' + PREMOD + r'(?:,? (?:and/or |or |and )?|-| ))*'
HEAD = r'(?:' + '|'.join(HEAD_ALT) + r')\b'
HEADS = HEAD + r'(?:,? (?:and/or |or |and )(?:' + PREMODS_SEQ + r')?' + HEAD + r')*'
DET = (r'(?:(?:up to ' + NUM + r'|any number of|one or more|' + NUM + r'|a|an|another|each|all|any|other|the|that|those|'
       r'these|this|target|' + NUM + r' target|' + NUM + r' other target|another target|each other|all other|' +
       NUM + r' other|up to ' + NUM + r' target|up to ' + NUM + r' other target|your|its|their|his or her|'
       r'each of your|each of|your opponents\'|an opponent\'s|target opponent\'s|that player\'s|enchanted|equipped|'
       r'exactly ' + NUM + r'|at least ' + NUM + r'|half the) )')
COUNTER_STOP = {'then', 'and', 'may', 'to', "can't", 'or', 'you', 'must', 'cannot', 'player', 'opponent', 'they',
                'spell', 'ability', 'abilities', 'spells', 'it', 'and/or', 'instead', 'that', 'would', 'cards',
                'not', 'also', 'first', 'can', 'could'}
_KW_ALT = '|'.join(re.escape(k) for k in KEYWORD_ABILITIES if len(k) > 3 and k not in
                   ('enchant', 'equip', 'protection', 'flash', 'cast', 'crew', 'partner', 'station', 'champion',
                    'companion', 'craft', 'level up', 'squad', 'saddle', 'storm', 'vanishing', 'fading'))
KW_PHRASE = (r'\b(?:' + _KW_ALT + r'|first strike|double strike|protection from [a-z]+(?: and from [a-z]+)*|'
             r'hexproof from [a-z]+)\b')

POSTMODS = [
    r"you control", r"you don't control", r"you own", r"you don't own", r"your opponents control",
    r"an opponent controls", r"target opponent controls", r"target player controls", r"that player controls",
    r"defending player controls", r"each opponent controls", r"each player controls", r"its controller controls",
    r"they control", r"you both own and control", r"you control but don't own", r"you own but don't control",
    r"(?:with|without) (?:power|toughness|mana value|total power|base power(?: and toughness)?) " + NUM + r"(?: or (?:greater|less|more|fewer))?",
    r"(?:with|without) (?:power|toughness|mana value) less than [^,.]+?(?=[,.]|$| and | or )",
    r"(?:with|without) (?:power|toughness|mana value) (?:greater than|equal to) [^,.]+?(?=[,.]|$| and | or )",
    r"(?:with|without) (?:a|an|one or more|" + NUM + r") <counter[\ue000-\uf8ff]?>s?(?: on (?:it|them))?",
    r"(?:with|without) (?:" + _KW_ALT + r"|first strike|double strike)(?:(?:,| or| and|, and) (?:" + _KW_ALT + r"|first strike|double strike))*",
    r"(?:with|without) (?:a|an) (?:activated|triggered|mana) abilit(?:y|ies)",
    r"with the (?:greatest|least|highest|lowest) [a-z ]+",
    r"of the chosen (?:type|color|name)", r"of that type", r"of the chosen creature type", r"of each color",
    r"of your choice", r"named ~", r"with the same name(?: as [^,.]+)?", r"that shares? [^,.]+?(?=[,.]|$| and | or )",
    r"that's (?:attacking|blocking|tapped|untapped|a [a-z]+|not [a-z]+|an? [a-z]+|attacking or blocking|all colors)",
    r"that (?:attacked|blocked|dealt damage|entered|was dealt damage)(?: [^,.]+?)?(?= this turn|[,.]|$)",
    r"attacking (?:you|that player)", r"blocking (?:it|~|<self>)", r"blocked by (?:it|~|<self>)",
    r"in (?:your|a|each|their) (?:party|graveyard|hand)", r"tapped this way", r"sacrificed this way",
    r"destroyed this way", r"exiled this way", r"revealed this way", r"discarded this way",
    r"put (?:into [^,.]+ )?this way", r"chosen this way", r"returned this way", r"milled this way",
    r"other than ~", r"other than (?:it|<self>|that creature|the chosen [a-z]+)", r"you cast", r"your opponents cast",
    r"an opponent casts", r"cast this way", r"from (?:anywhere )?other than your hand",
]
POSTMOD_RE = re.compile(r'^ (?:' + '|'.join('(?:' + p + ')' for p in POSTMODS) + r')')
NP_RE = re.compile(r'\b(' + DET + r')?(' + PREMODS_SEQ + r')(' + HEADS + r')')

PLAYER_RE = re.compile(r"\b(each opponent|each player|each other player|target opponent|target player|an opponent|"
                       r"a player|that player|the chosen player|chosen player|defending player|its controller|"
                       r"its owner|their controller|their owners?|that creature's controller|that permanent's controller|"
                       r"that spell's controller|the active player|your opponents|opponents|players|each of your opponents|"
                       r"that opponent|the player|any player|another player|another target player|"
                       r"each opponent who [^,.]+|each player who [^,.]+|up to one target player|you)\b")
QUANT = [
    ('upto', r'^up to '), ('target', r'^(?:' + NUM + r' )?(?:other )?target\b|^another target\b'),
    ('anynum', r'^any number of'), ('oneormore', r'^one or more'), ('each', r'^each\b|^each of'),
    ('all', r'^all\b'), ('another', r'^another\b|^other\b'), ('ref', r'^(?:the|that|those|these|this|its|their)\b'),
    ('q', r'^(?:a|an|' + NUM + r'|exactly|at least|half)\b'), ('poss', r"^(?:your|an opponent's|target opponent's|that player's|your opponents')"),
    ('attached', r'^(?:enchanted|equipped)\b'),
]

REF_RE = re.compile(r"\b(it|them|they|that creature|that card|that permanent|that spell|that token|those creatures|"
                    r"those cards|those tokens|those permanents|the exiled card|the exiled cards|the chosen creature|"
                    r"the creature|the card|the token|that land|that artifact|the copy|the sacrificed creature|"
                    r"the revealed card|this way|its|their)\b")


def player_class(p):
    if p == 'you':
        return 'player.you'
    for name, qre in QUANT:
        if re.match(qre, p):
            return 'player.' + name
    if p.startswith(('its ', 'their ', 'defending', 'the chosen', 'chosen', 'that ')):
        return 'player.ref'
    return 'player.bare'


def player_rep(m):
    cls = player_class(m.group(0))
    _B[-1].append((cls, m.group(0)))
    return ' <' + cls + '> '


_B = []



MK = '[\ue000-\uf8ff]?'          # private-use marker carrying a binding's index while the frame is built
_MKRE = re.compile('[\ue000-\uf8ff]')


def _mk(i):
    return chr(0xE000 + i)


def _clean(v):
    return re.sub(r'\s+', ' ', _MKRE.sub('', v)).strip()


def frame(text):
    """Return (frame, bindings).

    Bindings are positional: the k-th entry is the value of the k-th slot occurrence in the frame, read left to
    right, as [slot, value] (or [slot, value, {"alts": [...]}] where "<obj> or <obj>" collapsed to one slot).
    Bindings that fill no slot (modality, subject) follow the positional ones as [name, value, {"slotless": true}].
    Each binding carries a private-use marker while the passes run, so the order survives every substitution.
    """
    b = []
    _B.append(b)
    t = ' ' + text.lower().strip().rstrip('.') + ' '

    def slot_tok(slot, val):
        b.append((slot, val))
        return ' <' + slot + _mk(len(b) - 1) + '> '

    t = re.sub(r'"[^"]*"', lambda m: slot_tok('granted_ability', m.group(0).strip('"')), t)

    def sub(pattern, slot, s, flags=0):
        return re.sub(pattern, lambda m: slot_tok(slot, m.group(0).strip()), s, flags=flags)

    t = re.sub(r'\{t\}', ' <tap_symbol> ', t)
    t = re.sub(r'\{q\}', ' <untap_symbol> ', t)
    t = sub(r'(?:\{e\})+', 'energy', t)
    t = re.sub(r'(?:\{[^}]+\})+', lambda m: slot_tok('mana', m.group(0).upper()), t)
    selves = []

    def self_rep(m):
        selves.append(m.group(0).strip())
        return ' <self> '
    t = re.sub(r'\b(?:this|that) ' + r'(?:' + SELF_NOUNS + r')\b(?!\'s controller)',
               lambda m: self_rep(m) if m.group(0).startswith('this') else m.group(0), t)
    if '~' in t:
        selves.append('~')
    t = t.replace('~', ' <self> ')
    t = re.sub(r'\s+', ' ', t)
    t = sub(r'(?<![a-z])(?:[+-]?(?:\d+|x)/[+-]?(?:\d+|x)|[a-z]+(?:-[a-z]+)?) counters?\b', 'counter', t)
    for i, sv in enumerate(b):
        if sv and sv[0] == 'counter' and sv[1].split()[0] in COUNTER_STOP:
            t = t.replace(' <counter' + _mk(i) + '> ', ' ' + sv[1] + ' ')
            b[i] = None
    # zones before objects so "from your graveyard" never becomes part of a noun phrase
    for zp in ZONE_PHRASES:
        t = sub(r'\b' + zp + r'\b', 'zone', t)
    t = re.sub(r'\b(in|from|into|to|onto) (exile|the battlefield|the stack|the command zone|graveyards?)\b',
               lambda m: ' ' + m.group(1) + slot_tok('zone', m.group(2)), t)
    t = re.sub(r'\bany (?:other )?target\b', lambda m: slot_tok('obj.target', m.group(0)), t)
    t = re.sub(r'\s+', ' ', t)
    # object noun phrases
    def np_rep(m):
        det = (m.group(1) or '').strip()
        full = m.group(0)
        rest = t2[m.end():]
        post = ''
        while True:
            pm = POSTMOD_RE.match(rest)
            if not pm:
                break
            post += pm.group(0)
            rest = rest[pm.end():]
        q = 'bare'
        for name, qre in QUANT:
            if re.match(qre, det):
                q = name
                break
        head = m.group(3)
        kind = 'player' if re.search(r'\b(player|opponent)s?\b', head) else 'obj'
        state['skip'] = len(post)
        return slot_tok(kind + '.' + q, _clean(full + post))
    out, pos = '', 0
    t2 = t
    state = {'skip': 0}
    for m in NP_RE.finditer(t2):
        if m.start() < pos:
            continue
        if not m.group(0).strip():
            continue
        out += t2[pos:m.start()] + np_rep(m)
        pos = m.end() + state['skip']
        state['skip'] = 0
    t = out + t2[pos:]
    t = sub(r'(?<![a-z<])[+-]?(?:\d+|x)/[+-]?(?:\d+|x)', 'pt', t)
    for c in COLORS:
        t = re.sub(r'\b' + c + r'\b(?! mana)', lambda m: slot_tok('color', m.group(0)), t)
    t = re.sub(KW_PHRASE, lambda m: slot_tok('kw', m.group(0)), t)
    t = re.sub(r'\s+', ' ', t)
    # players (after objects, so "you control" postmodifiers are already consumed)
    t = PLAYER_RE.sub(lambda m: slot_tok(player_class(m.group(0)), m.group(0)), t)
    t = re.sub(r"\byour\b", ' <player.you_poss> ', t)

    def poss(m):
        i = ord(m.group(2)) - 0xE000
        b[i] = (b[i][0] + '_poss', b[i][1])
        return '<' + b[i][0] + m.group(2) + '>'
    t = re.sub(r"<(player\.[a-z]+)([\ue000-\uf8ff])> ?'s\b", poss, t)
    t = REF_RE.sub(lambda m: slot_tok('ref', m.group(0)), t)
    t = re.sub(r'\b(?:a|an) (?=<counter' + MK + '>)', lambda m: slot_tok('n', '1').strip() + ' ', t)
    t = sub(r'\b' + NUM + r'\b', 'n', t)
    # lemmatize verbs
    t = ' '.join(LEMMA.get(w, w) for w in t.split())
    t = re.sub(r'\s+', ' ', t).strip().strip(',').strip()
    alts = {}

    def collapse(m):
        toks = re.findall(r'<[^<>]+>', m.group(0))
        first = ord(toks[0][-2]) - 0xE000 if _MKRE.search(toks[0]) else None
        if first is not None:
            alts[first] = [b[ord(x[-2]) - 0xE000][1] for x in toks[1:] if _MKRE.search(x)]
            for x in toks[1:]:
                if _MKRE.search(x):
                    b[ord(x[-2]) - 0xE000] = None
        return toks[0]
    t = re.sub(r'<(obj|player)\.[a-z]+' + MK + r'>(?: or <\1\.[a-z]+' + MK + r'>)+', collapse, t)
    extra = []
    # subject and modality are bindings, not part of the construction
    m = re.match(r'^(?:<player\.you' + MK + r'> )?(may|must|can) (?=[a-z])', t)
    if m:
        if m.group(0).startswith('<'):
            extra.append(['subject', 'you', {'slotless': True}])
        extra.append(['modality', m.group(1), {'slotless': True}])
        t = t[m.end():]
    m = re.match(r'^<player\.you' + MK + r'> (?=[a-z])', t)
    if m:
        extra.append(['subject', 'you', {'slotless': True}])
        t = t[m.end():]
    m = re.match(r'^(<player\.[a-z]+' + MK + r'>) (may) ', t)
    if m:
        extra.append(['modality', 'may', {'slotless': True}])
        t = m.group(1) + ' ' + t[m.end():]
    out = []
    si = 0
    for tok in re.findall(r'<([a-z_.]+)([\ue000-\uf8ff]?)>', t):
        name, marker = tok
        if marker:
            i = ord(marker) - 0xE000
            slot, val = b[i]
            e = [slot, _clean(val) if slot != 'mana' else val]
            if alts.get(i):
                e.append({'alts': [_clean(a) for a in alts[i]]})
            out.append(e)
        elif name == 'self':
            out.append(['self', selves[min(si, len(selves) - 1)] if selves else '~'])
            si += 1
        else:
            out.append([name, None])
    t = _MKRE.sub('', t)
    _B.pop()
    return t, out + extra
