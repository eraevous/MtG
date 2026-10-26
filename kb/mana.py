"""Typed mana: cost pips and mana production, as data (offline drafting only).

Payment rules the types encode (CR 107.4, 106.1b, 107.4e-f, 107.4h):
  generic {N}       payable by mana of any type, coloured or colourless
  colored {W}       payable only by mana of that colour
  colorless {C}     payable only by colourless mana; coloured mana can't pay it
  hybrid {W/U}      one pip, either colour (an OR inside one cost component)
  mono_hybrid {2/W} one pip: two generic OR one W
  phyrexian {W/P}   one pip: W OR 2 life (hybrid phyrexian {G/W/P}: G OR W OR 2 life)
  snow {S}          one mana from a snow source
  X                 chosen at casting/activation; remembered value, an amplifier, 0 outside the stack
Production keeps what can be spent where: a fixed colour, alternatives ("{R} or {G}"), any one
colour, any combination of colours, the chosen colour, any type (may be colourless), colourless,
amounts that scale ("for each ..."), and spending restrictions ("Spend this mana only ...").
"""
import re

COLORS = 'WUBRG'
WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'x': 'X', 'that much': 'amount_referenced'}


def pip(sym):
    s = sym.strip('{}').upper()
    parts = s.split('/')
    if s.isdigit(): return {'symbol': sym, 'type': 'generic', 'amount': int(s)}
    if s == 'X': return {'symbol': sym, 'type': 'X', 'remembered': 'X'}
    if s == 'C': return {'symbol': sym, 'type': 'colorless', 'amount': 1}
    if s == 'S': return {'symbol': sym, 'type': 'snow', 'amount': 1}
    if s in COLORS: return {'symbol': sym, 'type': 'colored', 'color': s}
    if 'P' in parts:
        cols = [p for p in parts if p in COLORS]
        return {'symbol': sym, 'type': 'phyrexian', 'alternatives': [{'color': c} for c in cols] + [{'pay_life': 2}]}
    if parts[0].isdigit():
        return {'symbol': sym, 'type': 'mono_hybrid', 'alternatives': [{'generic': int(parts[0])}] + [{'color': c} for c in parts[1:] if c in COLORS]}
    if all(p in COLORS + 'C' for p in parts):
        return {'symbol': sym, 'type': 'hybrid', 'alternatives': [{'color': c} if c != 'C' else {'colorless': 1} for c in parts]}
    return {'symbol': sym, 'type': 'unknown'}


def parse_cost(text):
    """'{2}{G/W}{G/P}' -> pips + summary. Returns None if the text holds no mana symbols."""
    syms = re.findall(r'\{[^}]+\}', text or '')
    syms = [s for s in syms if s.upper() not in ('{T}', '{Q}', '{E}')]
    if not syms: return None
    pips = [pip(s) for s in syms]
    mv = sum(p.get('amount', 0) if p['type'] in ('generic', 'colorless', 'snow') else
             (max(a.get('generic', 1) for a in p['alternatives']) if p['type'] == 'mono_hybrid' else 0 if p['type'] == 'X' else 1) for p in pips)
    return {'family': 'mana', 'pips': pips, 'mana_value': mv,
            'requires_colorless': any(p['type'] == 'colorless' for p in pips),
            'colors_required': sorted({p['color'] for p in pips if p['type'] == 'colored'}, key=COLORS.index),
            'has_alternatives': any('alternatives' in p for p in pips), 'has_x': any(p['type'] == 'X' for p in pips),
            'unknown': [p['symbol'] for p in pips if p['type'] == 'unknown']}


def _amount(s):
    m = re.match(r'(\w+|that much)\s+mana', s)
    if m and m.group(1) == 'x': return 'X'
    if m: return WORD.get(m.group(1), m.group(1))
    return None


def parse_production(clause):
    """Typed reading of the first 'add ...' in a clause, or None. Unknown shapes come back with mode 'unread'."""
    low = clause.lower()
    m = re.search(r'\badds? (.+?)(?:\.|$)', low)
    if not m: return None
    s = m.group(1).strip()
    out = {'amount': 1, 'restriction': None, 'scaling': None, 'source_text': s}
    r = re.search(r'spend this mana only ([^.]+)', low)
    if r: out['restriction'] = 'only ' + r.group(1).strip()
    f = re.search(r'\bfor each ([^.,]+)|equal to ([^.,]+)', s)
    if f: out['scaling'] = (f.group(1) or f.group(2)).strip(); s = s[:f.start()].strip()
    s = re.sub(r'^(?:an additional|additional)\s+', '', s)
    if re.fullmatch(r'(\{[wubrgc]\})+', s):
        syms = re.findall(r'\{([wubrgc])\}', s)
        cols = [x.upper() for x in syms]
        out.update(mode='colorless' if set(cols) == {'C'} else 'fixed', symbols=cols, amount=len(cols),
                   colored=any(c != 'C' for c in cols), colorless=('C' in cols))
    elif re.fullmatch(r'(\{[wubrgc]\})+(?:,\s*(\{[wubrgc]\})+)*,?\s*or\s+(\{[wubrgc]\})+', s):
        alts = [[x.upper() for x in re.findall(r'\{([wubrgc])\}', a)] for a in re.split(r',\s*or\s+|\s+or\s+|,\s*', s) if a.strip()]
        out.update(mode='alternatives', alternatives=alts, amount=len(alts[0]), colored=any(c != 'C' for a in alts for c in a),
                   colorless=any('C' in a for a in alts))
    elif re.fullmatch(r'(\{[wubrgc]\})+(?:,\s*(\{[wubrgc]\})+)*,?\s*and\s+(\{[wubrgc]\})+', s):
        cols = [x.upper() for x in re.findall(r'\{([wubrgc])\}', s)]
        out.update(mode='fixed', symbols=cols, amount=len(cols), colored=any(c != 'C' for c in cols), colorless='C' in cols)
    elif re.search(r'any combination of (\{[wubrg]\})', s):
        out.update(mode='combination_of', colors=[x.upper() for x in re.findall(r'\{([wubrg])\}', s)], amount=_amount(s) or 'X', colored=True, colorless=False)
    elif 'any combination of colors' in s:
        out.update(mode='any_combination', amount=_amount(s) or 'X', colored=True, colorless=False)
    elif re.search(r'of any (?:one )?colou?r', s):
        out.update(mode='any_one_color' if 'any one color' in s or (_amount(s) or 1) != 1 else 'any_color', amount=_amount(s) or 1, colored=True, colorless=False)
    elif 'of the chosen color' in s or 'of that color' in s:
        out.update(mode='chosen_color', amount=_amount(s) or 1, colored=True, colorless=False)
    elif 'of any type' in s:
        out.update(mode='any_type', amount=_amount(s) or 1, colored=None, colorless=None, note='may be colourless; depends on what the referenced lands could produce')
    elif "commander's color identity" in s or 'color identity' in s:
        out.update(mode='commander_identity', amount=_amount(s) or 1, colored=True, colorless=False)
    else:
        out.update(mode='unread')
    return out


# --- payability (DIO compatibility addendum A4) --------------------------------------------------
# A mana unit is {'type': one of WUBRG or 'C', 'snow': bool, 'source': optional provenance}.
# Snow is a property of the source, never a colour. Generic accepts any unit; {C} accepts only a C
# unit; a coloured pip accepts only that colour.

def unit(t, snow=False, source=None):
    t = t.upper()
    if t not in COLORS + 'C': raise ValueError(f'not a mana type: {t}')
    return {'type': t, 'snow': snow, 'source': source}


def pool(spec, snow=False, source=None):
    """'WB' or '{W}{B}' or ['W', 'C'] -> list of units."""
    if isinstance(spec, str): spec = re.findall(r'[WUBRGC]', spec.upper())
    return [unit(t, snow, source) for t in spec]


def _pip_options(p):
    """Ways to pay one pip: each is (accepts(unit) or None, units_needed, life)."""
    t = p['type']
    if t == 'generic': return [('any', p['amount'], 0)]
    if t == 'colored': return [(p['color'], 1, 0)]
    if t == 'colorless': return [('C', 1, 0)]
    if t == 'snow': return [('snow', 1, 0)]
    if t == 'X': return [('any', 0, 0)]
    if t in ('hybrid', 'mono_hybrid', 'phyrexian'):
        out = []
        for a in p['alternatives']:
            if 'color' in a: out.append((a['color'], 1, 0))
            elif 'colorless' in a: out.append(('C', 1, 0))
            elif 'generic' in a: out.append(('any', a['generic'], 0))
            elif 'pay_life' in a: out.append((None, 0, a['pay_life']))
        return out
    raise ValueError(f"unknown pip {p['symbol']}")


def _accepts(kind, u):
    return kind == 'any' or (kind == 'snow' and u['snow']) or u['type'] == kind


def can_pay(cost, units, life=0, x=0):
    """True when the units (and up to `life` life) can pay the mana cost text, with X = x.

    >>> can_pay('{1}{C}', pool('WW'))
    False
    >>> can_pay('{1}{C}', pool('WC'))
    True
    """
    pc = parse_cost(cost) if isinstance(cost, str) else cost
    if pc is None: return True
    if pc['unknown']: raise ValueError('unknown symbols ' + ','.join(pc['unknown']))
    needs = []
    for p in pc['pips']:
        if p['type'] == 'X': needs.append([('any', x, 0)])
        else: needs.append(_pip_options(p))
    # most constrained pips first: single specific option, then alternatives, then generic
    needs.sort(key=lambda o: (len(o) > 1, any(k == 'any' for k, _, _ in o)))
    return _search(needs, list(units), life)


def _search(needs, units, life):
    if not needs: return True
    first, rest = needs[0], needs[1:]
    for kind, n, l in first:
        if l:
            if l <= life and _search(rest, units, life - l): return True
            continue
        idx = [i for i, u in enumerate(units) if _accepts(kind, u)]
        if len(idx) < n: continue
        if kind == 'any':  # spend the least useful units first: C, then snow-less colours in reverse order
            idx.sort(key=lambda i: (units[i]['type'] != 'C', -COLORS.find(units[i]['type'])))
        take = set(idx[:n])
        if _search(rest, [u for i, u in enumerate(units) if i not in take], life): return True
    return False


def production_pools(m, chosen=None, x=1):
    """Every pool one resolution of a typed production record can add (amount X read as x).

    fixed {W}{B} -> [[W, B]]; any_color -> five single-colour pools (never C); any_type -> six,
    C included; alternatives {R} or {G} -> [[R], [G]]; chosen_color needs `chosen`."""
    amt = m.get('amount', 1)
    amt = x if amt == 'X' or not isinstance(amt, int) else amt
    mode = m['mode']
    if mode in ('fixed', 'colorless'): return [pool(m['symbols'])]
    if mode == 'alternatives': return [pool(a) for a in m['alternatives']]
    if mode in ('any_color', 'any_one_color'): return [pool(c * amt) for c in COLORS]
    if mode == 'any_type': return [pool(c * amt) for c in COLORS + 'C']
    if mode == 'chosen_color':
        if not chosen: raise ValueError('chosen_color needs the chosen colour')
        return [pool(chosen * amt)]
    if mode in ('any_combination', 'combination_of'):
        import itertools
        cols = m.get('colors') or list(COLORS)
        return [pool(''.join(c)) for c in itertools.combinations_with_replacement(cols, amt)]
    raise ValueError(f'production mode {mode} has no pool reading')
