"""Shared semantic record: one capability record per card, plus typed readings and clause audit.

Part 1 (from capabilities.py): one capability record per card, from Oracle text, inventory tags and hand labels.

Evidence is merged, never added: a Roles tag, an Oracle rule hit and a hand label
for the same function are three pieces of evidence for ONE capability.

Oracle rules are regexes over Oracle text with reminder text removed and the
card's own name replaced by '~'. They are derived hypotheses (strategic role
detectors), not DIO operations; their precision is measured in README.
"""
import re, csv
from pathlib import Path

HERE = Path(__file__).resolve().parent / 'data'
NUM = r"(?:a|an|one|two|three|four|five|six|x|that many|\d+)"

RULES = {
    # functional coverage (Protocol §2.5)
    'ramp': [r"\badd \{", r"\badd (?:one|two|three|x|that much) mana", r"mana of any (?:one )?color", r"any combination of colors",
             r"search your library for (?:a|up to \w+) basic land cards?[^.]*onto the battlefield",
             r"put (?:a|up to \w+) land cards? [^.]*onto the battlefield", r"create (?:a|\w+) treasure",
             r"you may play an additional land", r"until you reveal a land card\. put that card onto the battlefield",
             r"search your library for (?:a|an|up to \w+) (?:basic )?(?:forest|island|swamp|mountain|plains|land)[^.]*cards?[^.]*onto the battlefield"],
    'draw': [r"\bdraws? " + NUM + r" cards?", r"\bdraw (?:a|one|two|three|x) cards?", r"draw cards equal", r"\binvestigate", r"\bconnives?\b",
             r"\bdraw a card\b", r"put (?:one|two|it|that card|one of them|any number of them|those cards)[^.]* into your hand"],
    'spot_removal': [r"(?:destroy|exile) (?:up to one )?(?:other )?target (?:[^.]*?)(?:creature|permanent|artifact|enchantment|planeswalker|battle(?!field))(?!s? you control)",
                     r"deals? (?:\w+|x) damage to (?:any target|target creature|target planeswalker|up to one target)",
                     r"deals? damage equal to [^.]*to (?:any target|target creature)",
                     r"damage [^.]*divided as you choose among any number of target",
                     r"return target (?:nonland )?(?:creature|permanent|spell|nonland permanent)[^.]*to its owner's hand",
                     r"target (?:creature|permanent) [^.]*gets -\d+/-[1-9]\d*|target creature gets -x/-x",
                     r"\bfights? (?:target|up to one target|another target)", r"deals damage equal to its power to target creature",
                     r"target (?:opponent|player) sacrifices", r"each (?:player|opponent) sacrifices (?:a|an) ", r"owner of target (?:nonland )?permanent shuffles"],
    'wipe': [r"(?:destroy|exile) all (?:creatures|nonland permanents|artifacts|enchantments|other creatures|permanents)",
             r"(?:destroy|exile) each (?:creature|nonland permanent|other creature)", r"all (?:other )?creatures get -",
             r"return (?:all|each) (?:creature|nonland permanent|other creature)s?[^.]*to (?:its|their) owner'?s?'? hands?",
             r"deals? (?:\w+|x) damage to each (?:creature|other creature)", r"each player sacrifices (?:all|half)", r"sacrifices the rest",
             r"(?:destroy|exile) all (?:\w+ )?(?:creatures|artifacts|enchantments|permanents)", r"destroy each artifact",
             r"-1/-1 counters? on each (?:other )?(?:\w+ )?creature", r"damage to each (?:other )?(?:[\w-]+ )?creature",
             r"return all attacking creatures", r"\boverload \{"],
    'counterspell': [r"counter target (?:\w+ )?(?:spell|ability|activated|triggered)"],
    'protection': [r"(?:creatures|permanents|other creatures|other permanents) you control (?:gain|have|get)[^.]*(?:hexproof|indestructible|protection from|shroud)",
                   r"target (?:creature|permanent) you control (?:gains|has)[^.]*(?:hexproof|indestructible|protection from)",
                   r"(?:creature|permanent) gains indestructible", r"target creature you control [^.]*(?:hexproof|indestructible)", r"gains [^.]*indestructible", r"creatures? you control (?:has|have) hexproof", r"has persist", r"shield counter", r"phases? out",
                   r"exile target creature you control, then return", r"return [^.]*other target creature you control to its owner's hand",
                   r"\bthose creatures gain[^.]*indestructible", r"\bgain indestructible"],
    'counter_preservation': [r"if it had counters on it, put those counters", r"\bmove (?:any number of|all|a|one or more) [^.]*counters?",
                             r"put (?:its|those) counters on"],
    'recursion': [r"return [^.]*(?:card|cards) from your graveyard to (?:the battlefield|your hand)",
                  r"return [^.]*from your graveyard to (?:the battlefield|your hand)", r"cast [^.]*from your graveyard",
                  r"\bpersist\b", r"\bundying\b"],
    'closer': [r"each opponent loses \d+ life", r"each opponent loses (?:x|that much) life", r"deals? \w+ damage to each opponent",
               r"creatures you control (?:gain|get|have)[^.]*(?:flying|trample|menace|double strike|can't be blocked|\+\w+/\+\w+)",
               r"additional combat phase", r"target opponent loses", r"deals that much damage to target opponent"],
    # module roles (Ontology §1.6 route templates)
    'token_maker': [r"\bcreate " + NUM + r"[^.]*tokens?", r"\binvestigate\b", r"\bamass\b"],
    'sac_outlet': [r"\bsacrifice (?:a|an|another|one|x|two|three) (?:[^.:]*?)(?:creature|artifact|permanent|token|food|clue|treasure)s?[^.]*:",
                   r"as an additional cost to cast this spell, sacrifice (?:a|an|another) (?:creature|artifact)"],
    'death_payoff': [r"whenever [^.]*\bdies\b", r"whenever you sacrifice", r"whenever [^.]*leaves the battlefield",
                     r"whenever [^.]*is put into (?:a|your) graveyard from the battlefield"],
    'counter_source': [r"put " + NUM + r" \+1/\+1 counters? on", r"enters with " + NUM + r" (?:additional )?\+1/\+1 counters?",
                       r"\+1/\+1 counter on (?:each|target|it|that)", r"\badapt \d", r"\bbolster\b", r"\bproliferate\b", r"\bevolve\b",
                       r"mutagen token", r"\bincrement\b"],
    'counter_multiplier': [r"twice that many \+1/\+1", r"that many plus one \+1/\+1", r"put an additional \+1/\+1 counter",
                           r"double the number of \+1/\+1 counters"],
    'counter_payoff': [r"whenever (?:one or more )?\+1/\+1 counters? (?:is|are) put", r"whenever you put one or more [^.]*counters",
                       r"(?:creature|creatures) you control with (?:a|one or more) (?:\+1/\+1 )?counters? on", r"for each \+1/\+1 counter",
                       r"with a counter on it", r"number of (?:\+1/\+1 )?counters on"],
    'etb_value': [r"when ~ enters", r"when this (?:creature|artifact|enchantment|permanent|land|vehicle) enters",
                  r"whenever ~ enters", r"whenever this creature enters"],
    'blink': [r"exile (?:target|another target|up to one target|one or more other target)[^.]*you control[^.]*,? then return",
              r"exile [^.]*you control[^.]*return (?:it|that card|them|those cards) to the battlefield"],
    'lifegain_source': [r"\byou gain (?:\d+|x|that much) life", r"\blifelink\b", r"create [^.]*food", r"gains? \d+ life"],
    'lifegain_payoff': [r"whenever you gain life", r"if you(?:'ve)? gained (?:\d+ or more )?life", r"whenever you gain"],
    'artifact_payoff': [r"whenever (?:an|another|one or more) (?:other )?(?:artifacts?|food|treasures?|clues?)(?: tokens?)? (?:you control )?(?:enters|are put|is put|leaves)",
                        r"whenever you sacrifice (?:an|a|another) (?:artifact|food|treasure|clue)", r"for each artifact you control",
                        r"whenever [^.]*or (?:another )?artifact you control enters", r"artifacts you control (?:are|have)"],
    'artifact_token': [r"create [^.]*(?:food|treasure|clue|mutagen|blood|map|powerstone|gold|incubator|junk|lander|artifact)[^.]*tokens?", r"\binvestigate\b"],
    'token_payoff': [r"whenever (?:a|one or more) (?:creature )?tokens? (?:you control )?enters?", r"whenever you create (?:a|one or more)[^.]*tokens?",
                     r"if one or more tokens would be created"],
    'landfall_payoff': [r"whenever a land (?:you control )?enters", r"\blandfall\b", r"whenever one or more lands (?:you control )?enter"],
    'land_drop': [r"play an additional land", r"until you reveal a land card\. put that card onto the battlefield", r"put (?:a|up to \w+|that) land cards? [^.]*onto the battlefield",
                  r"search your library for [^.]*land cards?[^.]*onto the battlefield", r"return [^.]*(?<!non)\bland cards?[^.]*to the battlefield"],
    'self_mill': [r"\bmill\b", r"\bsurveil\b", r"put the top [^.]*into your graveyard", r"\bdredge\b", r"discard (?:a|two|x) cards?"],
    'reanimation': [r"return [^.]*creature cards? from (?:your|a) graveyard to the battlefield", r"put [^.]*creature card from (?:a|your) graveyard onto the battlefield"],
    'spell_payoff': [r"whenever you cast (?:an|a|your first) (?:instant|sorcery|noncreature)", r"\bmagecraft\b", r"\bprowess\b",
                     r"whenever you cast or copy"],
    'copy': [r"\bcopy of\b", r"\bcopy target\b", r"\bcopy it\b"],
}
# kb patch 4 (2026-10-29): roles that live only in reminder text, which clean() strips. Predefined tokens carry their
# abilities in reminder text, and some keywords create tokens. Mapped here by name, never by un-stripping reminder text.
# Role audit v0.2 found Gold Pan (Treasure: fixing) and Galactic Wayfarer (Lander: ramp) this way. Impulse tokens (Junk)
# are not draw (D-0011); Blood loots (not draw, D-0010); Map explores. Those carry no role here.
PREDEFINED_TOKENS = {
    'treasure': ('ramp', 'fixing'), 'gold': ('ramp', 'fixing'), 'lander': ('ramp', 'fixing', 'land_drop'),
    'powerstone': ('ramp',), 'clue': ('draw',), 'food': ('lifegain_source',),
}
TOKEN_CREATE = re.compile(r"\bcreate\b(?:(?!\bsacrifice\b)[^.])*?\b(" + '|'.join(PREDEFINED_TOKENS) + r")s?\b(?: artifact)? tokens?")
TOKEN_KEYWORDS = {  # keyword (as it reads once reminder text is gone) -> roles
    r"\bincubate (?:\d+|x)": ('token_maker', 'artifact_token'), r"\bafterlife \d": ('token_maker',),
    r"\bliving weapon\b": ('token_maker',), r"\bfor mirrodin!": ('token_maker',), r"\bmobilize (?:\d+|x)": ('token_maker',),
    r"\boffspring \{": ('token_maker',), r"\bfabricate \d": ('token_maker',), r"\bsquad \{": ('token_maker',),
    r"\b(?:embalm|eternalize) \{": ('token_maker',), r"\bmyriad\b": ('token_maker',), r"\bextort\b": ('closer',),
}

TYPE_ROLES = {'instant_sorcery': r"\b(?:Instant|Sorcery)\b", 'creature': r"\bCreature\b", 'land': r"\bLand\b"}
COVERAGE = ['ramp', 'fixing', 'draw', 'spot_removal', 'wipe', 'counterspell', 'protection', 'recursion', 'closer']
FIXING = [r"mana of any (?:one )?color", r"any combination of colors", r"search your library for [^.]*basic land", r"any color", r"mana of the chosen color", r"\{t\}: add \{[wubrg]\} or \{[wubrg]\}"]

# Roles tag -> function (exact tag tokens). Used as retrieval evidence only.
TAGMAP = {'Removal': 'spot_removal', 'Board wipe': 'wipe', 'Card draw': 'draw', 'Ramp': 'ramp', 'Mana fixing': 'fixing',
          'Protection': 'protection', 'Recursion': 'recursion', 'Token maker': 'token_maker', 'Sacrifice outlet': 'sac_outlet',
          'Death trigger': 'death_payoff', 'Counter multiplier': 'counter_multiplier', 'Blink / flicker': 'blink',
          'Landfall': 'landfall_payoff', 'Counterspell': 'counterspell', 'Drain / burn': 'closer', 'Copy': 'copy',
          'Evasion': 'closer', 'Lifegain': 'lifegain_source', 'Mana rock': 'ramp', 'Mana dork': 'ramp'}
LABEL_COLS = {'ramp': 'ramp', 'fixing': 'fixing', 'draw': 'draw', 'spot_removal': 'spot_removal', 'wipe': 'wipe',
              'counterspell': 'counterspell', 'protection': 'protection', 'recursion': 'recursion', 'closer': 'closer',
              'token_maker': 'token_standalone', 'counter_source': 'counter_source'}

def clean(oracle, name):
    t = re.sub(r"\([^)]*\)", "", str(oracle) if str(oracle) != 'nan' else '')
    # kb patch 1 (2026-10-22): longest name first, so the result no longer depends on PYTHONHASHSEED
    for n in sorted({name, name.split(' // ')[0], name.split(',')[0]}, key=lambda x: (-len(x), x)):
        if n: t = t.replace(n, '~')
    return t.lower().replace('~', '~')

# kb patch 3 (2026-10-28): a mass-removal phrase is not a wipe when its scope is the source's own helpers or
# blockers, the controller's own side, or the objects come straight back (flicker). Golden Argosy was the case.
WIPE_NARROW = re.compile(r"\s*(?:you control\b|that crewed|blocking (?:it|~)|blocked by (?:it|~)|that blocked|that attacked)")
WIPE_RETURN = re.compile(r"return (?:it|them|that card|those cards|the exiled cards?)[^.]*to the battlefield")


def wipe_scope_ok(t, m):
    after = '.'.join(t[m.end():].split('.', 2)[:2])  # rest of this sentence and the next
    return not WIPE_NARROW.match(t, m.end()) and not WIPE_RETURN.search(after)


def oracle_functions(name, oracle, type_line):
    t = clean(oracle, name); spans = {}
    t = re.sub(r"whenever (?:you|a player|an opponent) draws? (?:a|your \w+) cards?", "", t)
    t = re.sub(r"search your library for [^.]*?put (?:it|that card|them) into your hand", "search your library (tutor)", t)  # a tutor is not draw
    for f, pats in RULES.items():
        for p in pats:
            m = next((m for m in re.finditer(p, t) if f != 'wipe' or wipe_scope_ok(t, m)), None)
            if m: spans[f] = m.group(0)[:80]; break
    if 'wipe' in spans and spans['wipe'].startswith('overload') and 'spot_removal' not in spans:
        del spans['wipe']  # overload only turns removal into a wipe, not a pump
    if 'land' not in str(type_line).lower():
        for p in FIXING:
            m = re.search(p, t)
            if m: spans['fixing'] = m.group(0)[:80]; break
    else:
        spans.pop('ramp', None)  # a land's own mana is mana base, not ramp
    for m in TOKEN_CREATE.finditer(t):
        for f in PREDEFINED_TOKENS[m.group(1)]:
            spans.setdefault(f, m.group(0)[:80])
    for p, roles in TOKEN_KEYWORDS.items():
        m = re.search(p, t)
        for f in roles if m else ():
            spans.setdefault(f, m.group(0))
    for f, p in TYPE_ROLES.items():
        if re.search(p, str(type_line)): spans[f] = 'type line'
    # a mana creature/rock 'add {' without restriction counts as ramp; restricted fixers stay fixing
    return spans

def load_labels():
    p = HERE / 'tmnt_function_labels.csv'
    if not p.exists(): return {}
    with open(p, encoding='utf-8') as f:
        return {r['card']: r for r in csv.DictReader(f)}

def capability_record(row, labels=None):
    """Return {function: {'status', 'evidence': {...}}} for one Collection row."""
    name = row['Card Name']; tags = [r.strip() for r in str(row['Roles']).split(';') if r.strip() and str(row['Roles']) != 'nan']
    spans = oracle_functions(name, row['Oracle Text'], row['Type Line'])
    tagged = {TAGMAP[t] for t in tags if t in TAGMAP}
    lab = (labels or {}).get(name)
    rec = {}
    for f in set(spans) | tagged | ({k for k in LABEL_COLS if lab[LABEL_COLS[k]] == '1'} if lab else set()):
        ev = {}
        if f in spans: ev['oracle'] = spans[f]
        if f in tagged: ev['tag'] = True
        if lab and f in LABEL_COLS: ev['label'] = lab[LABEL_COLS[f]] == '1'
        # status: judgment overrides; otherwise Oracle rule decides; tag alone is a candidate only
        if 'label' in ev: status = 'supported' if ev['label'] else ('contradicted' if ev.get('tag') or ev.get('oracle') else None)
        elif 'oracle' in ev: status = 'supported'
        else: status = 'tag_only'
        if status: rec[f] = {'status': status, 'evidence': ev}
    return rec

def counts(rec):
    """Functions that count toward coverage: supported only (never tag_only)."""
    return {f for f, v in rec.items() if v['status'] == 'supported'}


# ====================================================================== Part 2: typed readings
# These refine a role by what it actually does. They read Oracle text only.
WIPE_KINDS = ['destroy', 'damage', 'exile', 'bounce', 'minus', 'sacrifice']
THREATS = {  # which wipe kinds answer a threat class
    'indestructible': {'bounce', 'exile', 'minus', 'sacrifice'},
    'big_toughness': {'bounce', 'exile', 'destroy', 'sacrifice'},
    'ordinary': {'bounce', 'exile', 'destroy', 'damage', 'minus', 'sacrifice'},
}


def text_of(row, name):
    return clean(row['Oracle Text'], name) if row is not None else ''


def wipe_kind(t):
    """Effect classes of a mass-removal card (t = cleaned Oracle text)."""
    kinds = set()
    if re.search(r"return (?:all|each)[^.]*owner'?s?'? hands?", t): kinds.add('bounce')
    if re.search(r"(?:destroy) (?:all|each)", t): kinds.add('destroy')
    if re.search(r"exile (?:all|each)", t): kinds.add('exile')
    if re.search(r"damage to each", t): kinds.add('damage')
    if re.search(r"-\d+/-\d+ counters? on each|get -\w+/-\w+|-x/-x", t): kinds.add('minus')
    if re.search(r"sacrifices? (?:all|half|the rest)", t): kinds.add('sacrifice')
    if re.search(r"without a \+1/\+1 counter|you don't control|opponents control", t): kinds.add('asymmetric')
    return kinds


SURVIVES = {  # what a protective effect lets a creature survive (rules reading)
    'indestructible': {'destroy', 'damage'}, 'shield counter': {'destroy', 'damage'},
    'phase out': {'destroy', 'damage', 'exile', 'bounce', 'minus', 'sacrifice'},
    'persist/undying': {'destroy', 'damage', 'sacrifice'}, 'hexproof': set(), 'protection from': set(),
    'blink/bounce own': {'destroy', 'damage', 'exile', 'minus', 'sacrifice'},
}


def protection_profile(t):
    """Typed protection: list of {scope, effect, survives}. Scope says how many creatures it covers:
    all_creatures | creatures_with_counters | up_to_N_targets | single_target | self | other_creatures."""
    out = []
    for c in re.split(r"(?<=\.)\s+|\n", t):
        effs = [e for e, p in [('indestructible', r"indestructible"), ('shield counter', r"shield counter"), ('phase out', r"phases? out"),
                               ('persist/undying', r"\bpersist\b|\bundying\b"), ('hexproof', r"hexproof|\bshroud\b"),
                               ('protection from', r"protection from")] if re.search(p, c)]
        if not effs and re.search(r"exile target creature you control, then return|return [^.]*other target creature you control to its owner's hand", c):
            effs = ['blink/bounce own']
        if not effs: continue
        if re.search(r"creatures? (?:you control )?with (?:a|one or more) \+1/\+1 counters?|those creatures gain", t) and re.search(r"those creatures|with (?:a|one or more) \+1/\+1 counter[^.]*gain", c):
            scope = 'creatures_with_counters'
        elif re.search(r"(?:creatures|permanents) you control (?:gain|have|get)|each creature you control|other creatures you control|creatures you control (?:has|have)", c):
            scope = 'all_creatures'
        elif re.search(r"each other (?:nontoken )?creature you control", c): scope = 'other_creatures'
        elif m := re.search(r"up to (one|two|three|four|five|x) target creatures", c): scope = f'up_to_{m.group(1)}_targets'
        elif re.search(r"target (?:creature|permanent)", c): scope = 'single_target'
        elif re.search(r"~|this creature", c): scope = 'self'
        else: scope = 'unclear'
        for e in effs:
            out.append({'scope': scope, 'effect': e, 'survives': sorted(SURVIVES.get(e, set())), 'clause': c[:120]})
    return out


def recursion_types(clauses_):
    """Each graveyard-return clause typed by destination, referent and cadence. Empty = not recursion."""
    out = []
    for c in clauses_:
        if not re.search(r"graveyard|dies, return|persist|undying", c): continue
        if re.search(r"if this spell was cast from (?:a|your) graveyard", c): continue
        if re.search(r"(?:put|puts|shuffle|exile)[^.]*(?:cards? )?from (?:their|a|your|each) graveyard[^.]*(?:bottom|library|exile)|cards from their graveyard on the bottom", c): continue
        if re.search(r"\bmill\b|into your graveyard|is put into (?:a|your) graveyard from", c) and 'return' not in c: continue
        dest = 'battlefield' if re.search(r"(?:to|onto) the battlefield|persist|undying", c) else 'hand' if 'hand' in c else 'cast' if re.search(r"\bcast\b", c) else None
        if not dest: continue
        if re.search(r"this card|return ~|cast ~|~ from your graveyard|persist|undying", c): ref = 'self only'
        elif re.search(r"target (?:\w+, )+(?:\w+ )?or \w+ card", c): ref = 'narrow creature types'
        elif re.search(r"cast creature spells from your graveyard", c): ref = 'any creature'
        elif re.search(r"creature card|creature you control|it to the battlefield|return it|that card", c): ref = 'any creature' if 'without flying' not in c else 'creature without flying'
        elif re.search(r"permanent card|land card|card from your graveyard|cards? from your graveyard", c): ref = 'any card of a type' if re.search(r"(?:artifact|enchantment|land|permanent) card", c) else 'any card'
        else: ref = 'other'
        cad = 'one-shot' if re.search(r"sacrifice this (?:land|artifact|enchantment|creature)|unlock this door", c) else 'repeatable' if re.search(r"\{[^}]+\}[^:.]*:|\bwhenever\b|at the beginning|persist|undying|from your graveyard using", c) or (ref == 'self only' and dest == 'battlefield') else 'one-shot'
        out.append({'destination': dest, 'referent': ref, 'cadence': cad, 'clause': c[:140]})
    return out


# ====================================================================== Part 3: clause audit
PRICED = set(COVERAGE) | {'token_maker', 'sac_outlet', 'death_payoff', 'counter_source', 'counter_payoff', 'counter_multiplier',
                          'artifact_token', 'artifact_payoff', 'lifegain_source', 'lifegain_payoff', 'blink', 'etb_value', 'land_drop',
                          'landfall_payoff', 'instant_sorcery', 'spell_payoff', 'self_mill', 'reanimation', 'token_payoff'}
KEYWORD_LINE = re.compile(r"^(?:(?:flash|flying|vigilance|reach|trample|haste|lifelink|deathtouch|menace|defender|first strike|"
                          r"double strike|indestructible|hexproof|ward \{[^}]+\}|ward—[^,]+)(?:, |$))+$")
FEATURES = [  # consequential features the evaluator does not price; each blocks a conclusive verdict
    (r"\bcopy\b", 'copy effect'),
    (r"can't be countered", 'uncounterable'),
    (r"\binstead\b|\bwould\b|\bprevent\b", 'replacement or prevention effect'),
    (r"\bx\b", 'X-scaled magnitude'),
    (r"(?<!as an )\badditional\b(?! cost)", 'additional or multiplied effect'),
    (r"earthbend|becomes? (?:a|an) [^.]*creature", 'animation'),
    (r"costs? \{\d+\} less|without paying", 'cost reduction or free cast'),
    (r"\b(sneak|evoke|ninjutsu|flashback|escape|kicker|hideaway|cheer|alliance|unlock ability|ronso rage|increment|overload|cycling|disturb|foretell|channel|mutate|bestow|station|offspring|metalcraft|storied|flurry|crew)\b", 'keyworded mechanic'),
    (r"\bwhenever\b|at the beginning of", 'repeatable trigger (cadence not priced)'),
    (r"\{[^}]+\}[^:.]*:", 'activated ability (repeatable, not priced)'),
    (r"\bcounters? (?:on|from) [^.]*(?:move|put those)|\bmove [^.]*counters?", 'counter movement or preservation'),
]


def clauses(oracle, name):
    t = clean(oracle, name)
    out = []
    for line in re.split(r"\n|//", t):
        for c in re.split(r"(?<=\.)\s+", line.strip()):
            c = c.strip(' .•')
            if c: out.append(c)
    return out


def clause_audit(oracle, name):
    """Each clause: priced (the evaluator measures it), keyword (noted), or a reason it is not understood."""
    rows = []
    for c in clauses(oracle, name):
        if KEYWORD_LINE.match(c):
            rows.append({'clause': c, 'status': 'keyword (body quality, noted, not blocking)'}); continue
        hit = {f for f, ps in RULES.items() if any(re.search(p, c) for p in ps)} | ({'fixing'} if any(re.search(p, c) for p in FIXING) else set())
        feats = sorted({lab + (f": {m.group(1)}" if m.groups() else '') for p, lab in FEATURES for m in [re.search(p, c)] if m})
        priced = sorted(hit & PRICED)
        if not hit and not feats: status = 'unparsed'
        elif feats: status = 'unpriced feature'
        elif not priced: status = 'parsed, unpriced function'
        else: status = 'priced'
        rows.append({'clause': c, 'functions': sorted(hit), 'priced': priced, 'features': feats, 'status': status})
    return rows


def understood(audit_rows):
    """'complete' when every clause is priced or a keyword; otherwise 'partial' with the gaps."""
    gaps = [r for r in audit_rows if r['status'] in ('unparsed', 'unpriced feature', 'parsed, unpriced function')]
    return ('complete' if not gaps else 'partial'), gaps
