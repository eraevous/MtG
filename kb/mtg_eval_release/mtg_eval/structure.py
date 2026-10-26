"""Structural checks that read how a deck's parts depend on one another, not how many of each
it has. Added in 0.2.0 after the Vraska game, where three of the five causes Zach named were
invisible to card counts:

- resource ledger: cards that spend the same untapped creatures, untapped artifacts or
  artifact sacrifices (station, crew, "tap an untapped creature", improvise, ...);
- feedback: whether a token engine's output triggers its own payoffs (compounding), is only
  multiplied, or is linear;
- closing profile: the board a deck's closers and combat-damage engines need;
- commander dependence: how much of the engine runs through the commander, and what can
  protect it.

Readings are text patterns over Oracle text (ASSUMPTION thresholds are marked). Every deck is
measured, so a flag is reported with the deck's rank among the decks in the inventory."""
import re

I = re.I

# ---------------------------------------------------------------- resource ledger
NUM = {'a': 1, 'an': 1, 'one': 1, 'another': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
STATION_AT = re.compile(r"(?:it's an artifact creature at|^)\s*(\d+)\+", I | re.M)
CLAIMS = [  # (kind, pattern, what the number means)
    ('station', re.compile(r'\bstation\b(?! only)', I), 'one-time'),
    ('crew', re.compile(r'\bcrew (\d+)', I), 'per use'),
    ('tap creatures', re.compile(r'tap (a|an|another|one|two|three|any number of) (?:other )?untapped creatures?', I), 'per use'),
    ('tap creatures', re.compile(r'\{t\}, tap an untapped creature you control', I), 'per use'),
    ('tap artifacts', re.compile(r'tap (a|an|another|one|two|three|any number of) (?:other )?untapped artifacts?', I), 'per use'),
    ('tap permanents', re.compile(r'permanents you control gain "\{t\}', I), 'per use'),
    ('tap creatures', re.compile(r'\bconvoke\b', I), 'per use'),
    ('tap artifacts', re.compile(r'\bimprovise\b', I), 'per use'),
    ('sacrifice artifacts', re.compile(r'sacrifice (a|an|another|one|two|three) (?:other )?(?:artifacts?|servo|thopter|treasure|clue|food)\b', I), 'per use'),
    ('sacrifice artifacts', re.compile(r'sacrifice an artifact or creature', I), 'per use'),
]


def resource_claims(text):
    """Claims one card's text makes on the shared pool of untapped bodies and artifacts."""
    out = []
    for kind, pat, unit in CLAIMS:
        m = pat.search(text)
        if not m: continue
        if kind == 'station':
            n = max((int(x) for x in STATION_AT.findall(text)), default=1)
        elif kind == 'crew':
            n = int(m.group(1))
        elif m.groups() and m.group(1):
            n = NUM.get(m.group(1).lower(), 1)
        else:
            n = 1
        if not any(o['kind'] == kind for o in out):
            out.append({'kind': kind, 'amount': n, 'unit': unit})
    return out


# ---------------------------------------------------------------- feedback
MAKES = {
    'artifact': re.compile(r'create[^.]*\b(artifact[^.]*token|treasure|clue|food|thopter|servo|robot|drone|construct|lander|mutagen)', I),
    'creature': re.compile(r'create[^.]*creature token|create[^.]*\b(thopter|servo|robot|drone|construct)\b', I),
}
ON_ENTER = {
    'artifact': re.compile(r'whenever (?:an|one or more|another) (?:other )?(?:nontoken )?artifacts? (?:you control )?(?:enters|enter)|whenever you create (?:one or more |a |an )?(?:artifact )?tokens?|whenever (?:one or more )?(?:artifact )?tokens? (?:you control )?enters?', I),
    'creature': re.compile(r'whenever (?:a|an|one or more|another) (?:other )?(?:nontoken )?creatures? (?:you control )?(?:enters|enter)|whenever you create (?:one or more |a |an )?(?:creature )?tokens?|whenever (?:one or more )?(?:creature )?tokens? (?:you control )?enters?', I),
}
ON_CAST = {
    'artifact': re.compile(r'whenever you cast an artifact spell|whenever you cast an artifact or', I),
    'creature': re.compile(r'whenever you cast a creature spell', I),
}
# a payoff that makes the whole board stronger per token, not just itself
REINFORCE = re.compile(r'(\+1/\+1 counters? on (?:target|each|another|up to \w+ target) (?:other )?creatures?|creatures you control get \+\d)', I)
MULTIPLY = re.compile(r'(twice that many|those tokens plus|that many plus|create that many[^.]*instead|an additional[^.]*token)', I)


def feedback(texts, family):
    """texts: {card: oracle text}. family: 'artifact' or 'creature'.
    compounding: a card triggered by the family's tokens entering also makes one, so output feeds input;
    reinforcing: each token entering makes the board stronger (+1/+1 counters on other creatures, anthem);
    multiplied: a replacement adds tokens per event but nothing re-triggers;
    linear: payoffs exist but none makes the family's tokens on that trigger."""
    makers = sorted(c for c, t in texts.items() if MAKES[family].search(t))
    enter = sorted(c for c, t in texts.items() if ON_ENTER[family].search(t))
    cast = sorted(c for c, t in texts.items() if ON_CAST[family].search(t))
    # the trigger and the token must be in the same ability (line), or it is an ETB maker plus a payoff
    lines = lambda c: [l for l in texts[c].split('\n') if l.strip()]
    loops = sorted(c for c in enter if any(ON_ENTER[family].search(l) and MAKES[family].search(l) for l in lines(c)))
    mult = sorted(c for c in texts if any(MULTIPLY.search(l) and re.search(r'\btokens?\b', l, I) for l in lines(c)))
    reinforce = sorted(c for c in enter if any(ON_ENTER[family].search(l) and REINFORCE.search(l) for l in lines(c)))
    cls = ('compounding' if loops else 'reinforcing' if reinforce else 'multiplied' if mult
           else 'linear' if (enter or cast) else 'no payoffs')
    capped = sorted(c for c in loops if re.search(r'only once each turn', texts[c], I))
    return {'family': family, 'class': cls, 'capped loops': capped, 'reinforcers': reinforce, 'makers': makers, 'enter_payoffs': enter, 'cast_payoffs': cast,
            'loops': loops, 'multipliers': mult}


# ---------------------------------------------------------------- closing profile
EVASION = re.compile(r'\b(flying|menace|trample|shadow|can\'t be blocked|unblockable|skulk|horsemanship)\b', I)
ANTHEM = re.compile(r'(?:other )?creatures you control get \+\d+/\+\d+|(?:thopters|artifact creatures|tokens) you control get \+\d', I)
COMBAT_ENGINE = re.compile(r'deals? combat damage to (?:a player|an opponent|one or more players)', I)
PING = re.compile(r'deals? \d+ damage to each opponent|each opponent loses \d+ life', I)


def _power(v):
    try: return float(str(v))
    except ValueError: return None


def closing_profile(inv, cards):
    creatures = [c for c in cards if 'Creature' in str(inv.cards[c]['Type Line'])]
    big = [c for c in creatures if (_power(inv.cards[c]['Power']) or 0) >= 4]
    txt = {c: str(inv.cards[c]['Oracle Text']) for c in cards}
    anthems = [c for c in cards if ANTHEM.search(txt[c])]
    lasting = [c for c in anthems if not re.search(ANTHEM.pattern + r'[^.]*until end of turn', txt[c], I)]
    return {'creature cards': len(creatures), 'power 4+': big,
            'evasive creatures': [c for c in creatures if EVASION.search(txt[c] + ' ' + str(inv.cards[c]['Keywords']))],
            'lasting anthems': lasting, 'one-turn anthems': sorted(set(anthems) - set(lasting)),
            'combat-damage engines': [c for c in cards if COMBAT_ENGINE.search(txt[c]) and (c not in creatures or re.search(r'whenever (?:a|one or more|another)[^.]*creatures?(?: tokens?)? you control deals? combat damage', txt[c], I))],
            'repeatable drain or ping': [c for c in cards if PING.search(txt[c]) and re.search(r'\bwhenever\b', txt[c], I)]}


# ---------------------------------------------------------------- commander dependence
COVERS_COMMANDER = {'single_target', 'self', 'all_creatures', 'up_to_N_targets', 'creatures_with_counters'}


def commander_dependence(inv, commanders, cards, families):
    """engine_share: of the cards that make the deck's main token family, the commander's share is
    reported together with whether the commander makes them on a cast trigger fed by the deck."""
    from .semantics import protection_profile
    from .access import text
    out = []
    for cmd in commanders:
        t = str(inv.cards[cmd]['Oracle Text'])
        makes = [f for f in ('artifact', 'creature') if MAKES[f].search(t)]
        feed = None
        m = re.search(r'whenever you cast an? (noncreature|artifact|creature|instant or sorcery)[^.]*spell', t, I)
        if m:
            kind = m.group(1).lower()
            def fed(c):
                tl = str(inv.cards[c]['Type Line'])
                if inv.is_land(c): return False
                return {'noncreature': 'Creature' not in tl, 'artifact': 'Artifact' in tl, 'creature': 'Creature' in tl,
                        'instant or sorcery': 'Instant' in tl or 'Sorcery' in tl}[kind]
            feed = sum(fed(c) for c in cards)
        guards = sorted({c for c in cards for p in protection_profile(text(inv, c)) if p['scope'] in COVERS_COMMANDER})
        makers = families.get(makes[0], {}).get('makers', []) if makes else []
        out.append({'commander': cmd, 'engine': bool(makes and feed), 'makes': makes, 'spells that feed it': feed,
                    'other makers of that family': len([c for c in makers if c != cmd]), 'protection that can cover it': guards})
    return out


# ---------------------------------------------------------------- one deck, and flags against the portfolio
def measure(inv, state):
    cards = sorted(set(state.library) | set(state.commanders))
    nonland = [c for c in cards if not inv.is_land(c)]
    txt = {c: str(inv.cards[c]['Oracle Text']) for c in nonland}
    ledger = []
    for c in nonland:
        for cl in resource_claims(txt[c]): ledger.append({'card': c, **cl})
    fam = {f: feedback(txt, f) for f in ('artifact', 'creature')}
    close = closing_profile(inv, nonland)
    station = sum(r['amount'] for r in ledger if r['kind'] == 'station')
    claimants = sorted({r['card'] for r in ledger if r['kind'] != 'sacrifice artifacts'})
    return {'ledger': ledger, 'tap claimants': claimants, 'station power': station,
            'sacrifice claimants': sorted({r['card'] for r in ledger if r['kind'] == 'sacrifice artifacts'}),
            'claims per creature card': len(claimants) / max(1, close['creature cards']),
            'feedback': fam, 'closing': close,
            'commander': commander_dependence(inv, state.commanders, nonland, fam)}


# ASSUMPTION thresholds; set from the 12 current decks so that each flag is rare, not tuned to one game.
CONTENTION_RATIO = 0.35     # tap claimants per creature card
CONTENTION_MIN = 5          # and at least this many tap claimants
LINEAR_MIN_MAKERS = 8       # a token engine this large with payoffs but no feedback is flagged
THIN_CREATURES = 20         # fewer creature cards than this ...
THIN_BIG = 3                # ... and at most this many with power 4+
UNGUARDED = 1               # commander engine with at most this many cards that can protect it


def flags(m):
    out = []
    n, r = len(m['tap claimants']), m['claims per creature card']
    if n >= CONTENTION_MIN and r >= CONTENTION_RATIO:
        out.append(('resource contention', f"{n} cards spend untapped creatures or artifacts ({r:.2f} per creature card); stations alone need {m['station power']} power of taps"))
    # 0.3.0: the 'token engine does not compound' flag is retired; routing.classify reports engine classes instead
    c = m['closing']
    if c['creature cards'] < THIN_CREATURES and len(c['power 4+']) <= THIN_BIG:
        need = c['combat-damage engines']
        out.append(('thin board to close with', f"{c['creature cards']} creature cards incl. commander, {len(c['power 4+'])} with power 4+; lasting anthems {len(c['lasting anthems'])}"
                    + (f"; {len(need)} engines need combat damage ({', '.join(need)})" if need else '')))
    for d in m['commander']:
        if d['engine'] and len(d['protection that can cover it']) <= UNGUARDED:
            out.append(('engine runs through an exposed commander', f"{d['commander']} makes {d['makes'][0]} tokens off {d['spells that feed it']} spells; {len(d['protection that can cover it'])} {'card' if len(d['protection that can cover it']) == 1 else 'cards'} can protect it"))
    return out
