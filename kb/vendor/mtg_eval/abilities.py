"""Typed ability records: hook (what event starts it), cost (what it spends), gates (timing and
caps), outputs (what it produces) and cadence. One record per ability line of Oracle text.

These are lightweight projections from Oracle text, not verified DIO operations: the canonical
sheet has no verified Operations yet, so every record carries confidence 'typed' (every clause
of the line was read) or 'partial' (some text was not read; the unread text is kept). Event names
follow the DIO's hooks: cast, enter, create, leave, sacrifice, attack, combat_damage, upkeep,
end_step, scry_surveil. Cast and enter are separate hooks: a token entering never "casts".

Generic patterns only; there are no per-card exceptions."""
import re
from .inventory import COLORS

I = re.I
WORD_N = {'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'x': 0, 'that many': 0}
TOKEN_KINDS = {  # non-creature artifact tokens and the abilities every copy has (CR 111.10)
    'treasure': {'types': {'artifact'}, 'ability': 'mana'},
    'food': {'types': {'artifact'}, 'ability': 'food'},
    'clue': {'types': {'artifact'}, 'ability': 'clue'},
    'lander': {'types': {'artifact'}, 'ability': 'lander'},
    'mutagen': {'types': {'artifact'}, 'ability': None},
    'map': {'types': {'artifact'}, 'ability': None},
}
SELF = r'(?:~|this (?:creature|artifact|enchantment|vehicle|spacecraft|equipment|permanent|land|token|planeswalker))'


def _n(s):
    s = (s or 'a').lower().strip()
    return int(s) if s.isdigit() else WORD_N.get(s, 1)


def _types_filter(phrase):
    """'noncreature', 'artifact', 'artifact or lesson', 'instant or sorcery', 'creature', 'any'."""
    p = phrase.lower()
    out = set()
    for w in ('noncreature', 'nonartifact', 'artifact', 'creature', 'instant', 'sorcery', 'enchantment', 'lesson', 'token', 'nontoken'):
        if re.search(r'\b' + w + r'\b', p): out.add(w)
    if 'creature' in out and 'noncreature' in out and not re.search(r'\bcreature\b(?! spell)', p.replace('noncreature', '')): out.discard('creature')
    stop = {'noncreature', 'nonartifact', 'artifact', 'artifacts', 'creature', 'creatures', 'instant', 'sorcery', 'enchantment', 'lesson', 'token', 'tokens',
            'nontoken', 'other', 'or', 'and', 'spell', 'spells', 'a', 'an', 'one', 'more', 'permanent', 'permanents', 'you', 'control', 'nonland', 'card', 'cards'}
    for w in re.findall(r'[a-z]+', p):
        if w not in stop: out.add('sub:' + (w[:-1] if w.endswith('s') and len(w) > 4 else w))
    return out or {'any'}


# ---------------------------------------------------------------- outputs
TOKEN_RE = re.compile(r"create (a|an|one|two|three|four|five|x|that many) (tapped )?(?:(\d+)/(\d+) )?([\w ,'-]*?)(artifact )?(creature )?tokens?(?: with ((?:\"[^\"]*\")|[\w ,]+?))?(?=[.,;]| and | for | then |$)", I)


def parse_tokens(eff):
    out = []
    for m in TOKEN_RE.finditer(eff):
        n, tapped, p, t, desc, art, cre, kw = m.groups()
        desc = desc.strip()
        kind = next((k for k in TOKEN_KINDS if re.search(r'\b' + k + r'\b', desc)), None)
        types = set()
        if art or (kind and not cre): types.add('artifact')
        if cre or p is not None: types.add('creature')
        sub = [w for w in re.findall(r'[a-z]+', desc) if w not in ('colorless', 'white', 'blue', 'black', 'red', 'green', 'and', 'legendary')]
        spec = {'n': _n(n), 'tapped': bool(tapped), 'power': int(p) if p else 0, 'toughness': int(m.group(4)) if p else 0,
                'types': types, 'subtypes': set(sub), 'keywords': set(), 'mana_sac': False, 'kind': kind}
        kwtxt = (kw or '').lower()
        for k in ('flying', 'haste', 'vigilance', 'menace', 'trample', 'prowess', 'lifelink'):
            if k in kwtxt: spec['keywords'].add(k)
        if kind == 'treasure' or 'sacrifice this token: add' in kwtxt: spec['mana_sac'] = True
        out.append(spec)
    if not out:
        m = re.search(r'\b(investigate)\b', eff)
        if m: out.append({'n': 1, 'tapped': False, 'power': 0, 'toughness': 0, 'types': {'artifact'}, 'subtypes': {'clue'},
                          'keywords': set(), 'mana_sac': False, 'kind': 'clue'})
    return out


def parse_outputs(eff):
    """Outputs of one effect text. Returns (outputs, unread_fragments)."""
    outs, rest = [], eff
    def took(pat, fn):
        nonlocal rest
        for m in re.finditer(pat, rest, I):
            outs.append(fn(m))
        rest = re.sub(pat, ' ', rest, flags=I)
    toks = parse_tokens(rest)
    for t in toks: outs.append(('token', t))
    rest = TOKEN_RE.sub(' ', rest)
    rest = re.sub(r'\binvestigate\b', ' ', rest) if any(t.get('kind') == 'clue' for t in toks) else rest
    took(r'(?:deals|loses) (\d+) (?:damage to each opponent|life)(?: and you gain \d+ life)?|each opponent loses (\d+) life(?: and you gain \d+ life)?',
         lambda m: ('drain', int(m.group(1) or m.group(2))))
    took(r'deals (\d+) damage to (?:any target|each of one or two targets|target (?:player|opponent))', lambda m: ('reach', int(m.group(1))))
    took(r'deals? (\d+) damage to (?:target|each) (?:creature|attacking|blocking)[^.]*', lambda m: ('removal', int(m.group(1))))
    took(r'draws? (a|one|two|three|x) cards?(?:, then discard (?:a|one|two) cards?)?', lambda m: ('draw', _n(m.group(1))))
    took(r'(surveil|scry) (\d+)(?:, then draw a card)?', lambda m: ('scry_surveil', int(m.group(2))))
    took(r'\bproliferate\b', lambda m: ('proliferate', 1))
    took(r'creatures you control (?:gain [\w ]+ and )?get \+x/\+0 until end of turn,? where x is the number of (\w+) you control', lambda m: ('pump_team_x', m.group(1)))
    took(r'add (one mana of any color(?: in your commander\'s color identity)?|\{[wubrgc]\} or \{[wubrgc]\}|\{[wubrgc]\}(?:\{[wubrgc]\})*)', lambda m: ('mana', 1 if 'one mana' in m.group(1) or ' or ' in m.group(1) else len(re.findall(r'\{', m.group(1)))))
    took(r'put (a|one|two|three|\d+) \+1/ ?\+?1 counters? on ([^.]+)', lambda m: ('counters', _n(m.group(1)), m.group(2)))
    took(r'creatures you control get \+(\d+)/\+(\d+)(?: and gain [\w ]+)? until end of turn', lambda m: ('pump_team', int(m.group(1))))
    took(r'(?:target )?creatures? (?:you control )?(?:get|gets) \+(\d+)/\+\d+[^.]*until end of turn', lambda m: ('pump_one', int(m.group(1))))
    took(r"can't be blocked this turn", lambda m: ('evasion', 1))
    took(r'put (\w+) charge counters? on target (?:spacecraft|planet)[^.]*', lambda m: ('charge', _n(m.group(1))))
    took(r'you gain (\d+) life', lambda m: ('life', int(m.group(1))))
    took(r'(?:destroy|exile) all (?:other )?(?:nonland permanents|creatures|artifacts|nonland, nontoken permanents)[^.]*', lambda m: ('wipe', 1))
    took(r"(?:destroy|exile) (?:up to one )?target [^.]*|counter target [^.]*|return (?:up to one )?(?:other )?target (?:nonland permanent|creature|artifact|permanent)[^.]* to its owner's hand|tap or untap target [^.]*|put a stun counter on [^.]*",
         lambda m: ('interaction', 1))
    took(r'return (?:up to one )?target ([\w ]+?) card from your graveyard to (?:the battlefield|your hand)', lambda m: ('recursion', 1))
    left = re.sub(r'[\s.,;—-]+', ' ', rest).strip()
    left = re.sub(r'\b(?:this ability triggers only once each turn|this (?:creature|artifact|permanent)|~)\b', ' ', left)
    left = re.sub(r'^(?:you may|then|and|if you do)\b ?', '', re.sub(r'\s+', ' ', left).strip()).strip()
    left = '' if re.fullmatch(r'[~\s•—-]*', left) else left
    return outs, left


# ---------------------------------------------------------------- hooks and costs
HOOKS = [
    ('cast', re.compile(r'^whenever you cast (?:an? |your )?(second spell each turn|[\w ,/-]*?)\s*spells?\b(?: or [\w ]+ spell)?,?', I)),
    ('enter_self_or_other', re.compile(r'^whenever ' + SELF + r' or another ([\w ]+?) (?:you control )?enters,?', I)),
    ('enter_self', re.compile(r'^when(?:ever)? ' + SELF + r' (?:enters|is turned face up)(?: or leaves the battlefield)?(?: and when you sacrifice it)?,?', I)),
    ('enter', re.compile(r'^(?:alliance — )?whenever (a|an|another|one or more) (?:other )?([\w ]+?) (?:you control )?enters?,?', I)),
    ('create', re.compile(r'^whenever you create (?:or sacrifice )?(?:a|one or more) ([\w ]*?)tokens?,?', I)),
    ('attack', re.compile(r'^whenever (?:you attack|' + SELF + r' attacks)(?: with [\w ]+)?,?', I)),
    ('combat_damage', re.compile(r'^whenever (?:a|an|one or more|another) ([\w ]+?) (?:you control )?deals? combat damage to (?:a player|an opponent|one or more players),?', I)),
    ('combat_damage_self', re.compile(r'^whenever ' + SELF + r' deals combat damage to a player,?', I)),
    ('upkeep', re.compile(r'^at the beginning of your upkeep,?(?: if you control an? (\w+),)?', I)),
    ('end_step', re.compile(r'^at the beginning of (?:your|each) end step,?(?: if you control (two|three|\w+) or more tapped creatures,)?', I)),
    ('scry_surveil', re.compile(r'^whenever you (?:scry or surveil|surveil|scry),?', I)),
    ('landfall', re.compile(r'^(?:landfall — )?whenever a land you control enters,?', I)),
    ('begin_combat', re.compile(r'^at the beginning of combat on your turn,?', I)),
    ('main_phase', re.compile(r'^at the beginning of your (?:first |precombat )?main phase,?', I)),
    ('dies_self', re.compile(r'^when ' + SELF + r' dies,?', I)),
    ('dies', re.compile(r'^whenever (?:a|an|another|one or more) ([\w ]+?) (?:you control )?dies?,?', I)),
    ('sacrifice', re.compile(r'^whenever you sacrifice (?:a|an|another|one or more) ([\w ]+?),', I)),
    ('lifegain', re.compile(r'^whenever you gain life,?', I)),
    ('counters', re.compile(r'^whenever (?:you put )?one or more \+1/\+1 counters (?:are put )?on (?:a |an )?([\w ]+?)(?: you control)?,', I)),
    ('draw', re.compile(r'^whenever you draw (?:a|your second) card,?', I)),
    ('cast', re.compile(r'^magecraft — whenever you cast or copy an? (instant or sorcery) spell,?', I)),
    ('leave_self', re.compile(r'^when ' + SELF + r' leaves the battlefield,?', I)),
]

COST_TAP_OTHER = re.compile(r'tap (a|an|another|one|two|three|any number of) (?:other )?untapped (creatures?|artifacts?) you control', I)
COST_SAC = re.compile(r'sacrifice (this \w+|~|a|an|another|one|two|three)\b ?(?:other )?([a-z ]{0,30}?)(?=[,:]|$)', I)


def parse_cost(cost):
    c = {'mana': (0, []), 'tap_self': False, 'tap_other': None, 'sac': None, 'sac_self': False}
    generic, req = 0, []
    for s in re.findall(r'\{([^}]+)\}', cost):
        s = s.lower()
        if s == 't': c['tap_self'] = True
        elif s.isdigit(): generic += int(s)
        elif s.upper() in COLORS: req.append({s.upper()})
    c['mana'] = (generic, req)
    m = COST_TAP_OTHER.search(cost)
    if m: c['tap_other'] = {'n': 99 if m.group(1) == 'any number of' else _n(m.group(1)), 'kind': 'creature' if 'creature' in m.group(2) else 'artifact'}
    m = COST_SAC.search(cost)
    if m:
        who = m.group(1).lower()
        if who.startswith('this') or who == '~': c['sac_self'] = True
        else: c['sac'] = {'n': _n(who), 'filter': (m.group(2) or 'permanent').strip().rstrip('s')}
    return c


# ---------------------------------------------------------------- one card
def _raw_station(raw):
    m = re.search(r"artifact creature at (\d+)\+", raw, I)
    return int(m.group(1)) if m else None


def card_abilities(name, cleaned, raw, type_line, keywords=''):
    """Returns {'abilities': [...], 'statics': {...}, 'unread': [...]} for one card."""
    abil, unread = [], []
    st = {'vigilance_for': None, 'anthem': [], 'cost_reduction': [], 'replacement_create': [], 'station': None,
          'station_levels': [], 'crew': None, 'keywords': set(), 'haste': False, 'offspring': None, 'flurry': None}
    tl = str(type_line).lower()
    kws = {k.strip().lower() for k in str(keywords).split(';') if k.strip() and str(keywords) != 'nan'}
    st['keywords'] = {k for k in kws if k in ('flying', 'haste', 'vigilance', 'menace', 'trample', 'lifelink', 'deathtouch', 'first strike', 'double strike', 'reach', 'flash')}
    lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
    if 'station' in kws or any(l.startswith('station') for l in lines):
        lv = [int(x) for x in re.findall(r'^(\d+)\+ \|', cleaned, re.M)]
        st['station'] = _raw_station(raw) or (max(lv) if lv else 1)
    for l in lines:
        # keyword-only lines
        if re.fullmatch(r'[a-z ,]+', l) and all(w.strip() in ('flying', 'haste', 'vigilance', 'menace', 'trample', 'lifelink', 'deathtouch', 'first strike', 'reach', 'flash', 'defender', 'prowess', 'ward', 'station', 'storied', 'changeling', 'wither', 'convoke', 'improvise', 'indestructible', 'hexproof', 'infect', 'choose one —') for w in l.split(',')):
            if 'convoke' in l: st['convoke'] = True
            if 'improvise' in l: st['improvise'] = True
            if 'haste' in l: st['haste'] = True
            continue
        m = re.match(r'^equip \{(\d+)\}', l)
        if m: st['equip'] = int(m.group(1)); continue
        m = re.match(r'^crew (\d+)', l)
        if m: st['crew'] = int(m.group(1)); continue
        m = re.match(r'^(\d+)\+ \| (.*)$', l)
        if m:  # station level: a static (or keyword grant) that turns on at N charge counters
            body = m.group(2); lvl = int(m.group(1))
            a = re.search(r'other creatures you control get \+(\d+)/\+(\d+)', body)
            st['station_levels'].append({'at': lvl, 'anthem': int(a.group(1)) if a else 0,
                                         'keywords': {k for k in ('flying', 'lifelink', 'trample', 'vigilance') if k in body}})
            continue
        m = re.match(r'^offspring \{(\d+)\}', l)
        if m: st['offspring'] = int(m.group(1)); continue
        # statics
        m = re.match(r'^(artifact creatures|creatures|other creatures|tokens) you control have ([\w ,]+)\.', l)
        if m and 'vigilance' in m.group(2): st['vigilance_for'] = m.group(1); continue
        m = re.match(r'^(other creatures|creatures|thopters|artifact creatures|tokens) you control get \+(\d+)/\+(\d+)\.', l)
        if m: st['anthem'].append({'scope': m.group(1), 'p': int(m.group(2))});
        if m and l.count('.') <= 1: continue
        m = re.match(r'^([\w ]+?) spells you cast cost \{(\d+)\} less to cast\.', l)
        if m: st['cost_reduction'].append({'filter': _types_filter(m.group(1)), 'n': int(m.group(2))}); continue
        m = re.match(r'^if one or more ([\w ]*?)tokens would be created under your control, (?:those tokens plus an additional ([^.]*?) token|twice that many)', l)
        if m:
            extra = parse_tokens('create a ' + m.group(2) + ' token') if m.group(2) else []
            st['replacement_create'].append({'filter': _types_filter(m.group(1) or 'token'), 'extra': extra, 'double': m.group(2) is None})
            rest = l[m.end():]
            if re.search(r'are created instead\.?\s*$', rest) or not rest.strip(' .'): continue
        if l.startswith('flurry —'):
            outs, left = parse_outputs(l)
            abil.append({'kind': 'triggered', 'hook': ('cast', {'second spell'}), 'cost': None, 'gates': {}, 'outputs': outs, 'line': l,
                         'confidence': 'typed' if not left or left.startswith('flurry') else 'partial'}); continue
        # triggered
        hit = None
        for hk, pat in HOOKS:
            m = pat.match(l)
            if m: hit = (hk, m); break
        if hit:
            hk, m = hit
            eff = l[m.end():]
            gates = {'once_per_turn': bool(re.search(r'only once each turn', l)), 'condition': None,
                     'batch': bool(re.match(r'^whenever (?:one or more|you attack)', l)), 'optional': ' you may ' in (' ' + l[m.end():m.end() + 12])}
            if hk == 'cast': hook = ('cast', _types_filter(m.group(1)) if m.group(1) != 'second spell each turn' else {'second spell'})
            elif hk == 'enter_self_or_other': hook = ('enter', {'self_or_other': True, 'types': _types_filter(m.group(1))})
            elif hk == 'enter_self':
                hook = ('enter', {'self': True})
                if 'leaves the battlefield' in m.group(0): abil.append({'kind': 'triggered', 'hook': ('leave', {'self': True}), 'cost': None, 'gates': gates,
                                                                         'outputs': parse_outputs(eff)[0], 'line': l, 'confidence': 'typed'})
                if 'when you sacrifice it' in m.group(0): abil.append({'kind': 'triggered', 'hook': ('sacrifice', {'self': True}), 'cost': None, 'gates': gates,
                                                                        'outputs': parse_outputs(eff)[0], 'line': l, 'confidence': 'typed'})
            elif hk == 'enter': hook = ('enter', {'other': m.group(1) == 'another', 'types': _types_filter(m.group(2))})
            elif hk == 'create': hook = ('create', {'types': _types_filter(m.group(1) or 'token')})
            elif hk == 'attack': hook = ('attack', {'self': SELF[3:] in m.group(0) or ' attacks' in m.group(0)})
            elif hk == 'combat_damage': hook = ('combat_damage', {'types': _types_filter(m.group(1))})
            elif hk == 'combat_damage_self': hook = ('combat_damage', {'self': True})
            elif hk == 'upkeep': hook = ('upkeep', {}); gates['condition'] = ('control', m.group(1)) if m.group(1) else None
            elif hk == 'end_step': hook = ('end_step', {}); gates['condition'] = ('tapped_creatures', _n(m.group(1))) if m.group(1) else None
            elif hk == 'scry_surveil': hook = ('scry_surveil', {})
            elif hk == 'dies': hook = ('dies', {'types': _types_filter(m.group(1))})
            elif hk == 'leave_self': hook = ('leave', {'self': True})
            elif hk == 'dies_self': hook = ('dies', {'self': True})
            elif hk == 'sacrifice': hook = ('sacrifice', {'types': _types_filter(m.group(1))})
            elif hk == 'counters': hook = ('counters', {'types': _types_filter(m.group(1))})
            elif hk in ('lifegain', 'draw'): hook = (hk, {})
            elif hk in ('landfall', 'begin_combat', 'main_phase'): hook = (hk, {})
            opt_cost = re.match(r'\s*you may tap (two|three|a|an) untapped creatures you control\. if you do, ', eff)
            cost = None
            if opt_cost:
                cost = {'mana': (0, []), 'tap_self': False, 'tap_other': {'n': _n(opt_cost.group(1)), 'kind': 'creature'}, 'sac': None, 'sac_self': False}
                eff = eff[opt_cost.end():]
            outs, left = parse_outputs(eff)
            abil.append({'kind': 'triggered', 'hook': hook, 'cost': cost, 'gates': gates, 'outputs': outs, 'line': l,
                         'confidence': 'typed' if not left else 'partial', 'unread': left})
            if left: unread.append(left)
            continue
        # activated: "cost: effect" (levels of a Class are activated too)
        m = re.match(r'^([^:"]{1,90}):\s*(.*)$', l)
        if m and ('{' in m.group(1) or m.group(1).startswith(('tap', 'sacrifice'))) and not m.group(1).startswith(('when', 'at the')):
            cost = parse_cost(m.group(1)); eff = m.group(2)
            if 'level ' in eff[:12]:
                unread.append(l); continue  # class levels: their abilities are not modelled
            gates = {'sorcery': 'activate only as a sorcery' in eff, 'once_per_turn': 'only once each turn' in eff}
            eff = re.sub(r'activate only as a sorcery\.?', '', eff)
            outs, left = parse_outputs(eff)
            if 'untap this artifact' in eff or 'untap ~' in eff: outs.append(('untap_self', 1)); left = left.replace('untap this artifact', '').strip()
            abil.append({'kind': 'activated', 'hook': None, 'cost': cost, 'gates': gates, 'outputs': outs, 'line': l,
                         'confidence': 'typed' if not left else 'partial', 'unread': left})
            if left: unread.append(left)
            continue
        # the card itself (spells and ETB-less permanents): effects on resolution
        if re.match(r'^(choose one|as an additional cost|this spell costs|flash|ward|equip|equipped creature|enchant|you have no maximum)', l):
            if l.startswith('as an additional cost'):
                abil.append({'kind': 'additional_cost', 'hook': None, 'cost': parse_cost(l), 'gates': {}, 'outputs': [], 'line': l, 'confidence': 'typed'})
            elif not l.startswith(('flash', 'you have no maximum')):
                unread.append(l)
            continue
        if tl.startswith(('instant', 'sorcery')):
            outs, left = parse_outputs(l)
            abil.append({'kind': 'spell', 'hook': None, 'cost': None, 'gates': {}, 'outputs': outs, 'line': l,
                         'confidence': 'typed' if not left else 'partial', 'unread': left})
            if left: unread.append(left)
            continue
        unread.append(l)
    return {'abilities': abil, 'statics': st, 'unread': [u for u in unread if u]}


_CACHE = {}


def card_record(inv, name):
    """Cached per inventory export and card. A card's short name ('Sharuum' for 'Sharuum the Hegemon')
    is read as itself, like the full name."""
    from .access import text
    key = (getattr(inv, 'sha256', id(inv)), name)
    if key not in _CACHE:
        r = inv.cards[name]; t = text(inv, name)
        short = re.split(r'[ ,]', name.split(' // ')[0])[0].lower()
        if len(short) > 3:
            t = re.sub(r'\b' + re.escape(short) + r'\b(?= (?:enters|attacks|deals|dies|leaves|gets|has|is))', '~', t)
        _CACHE[key] = card_abilities(name, t, str(r['Oracle Text']), r['Type Line'], r['Keywords'])
    return _CACHE[key]
