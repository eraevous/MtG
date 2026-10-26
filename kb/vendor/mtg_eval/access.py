"""Draw-dependent access and module reliability (Kate's 2026-10-18 addendum).

Evaluation layer only: it reads the shared card record (capabilities.py via
evalcore.Inventory) and adds probabilities. Nothing here is a DIO primitive.

Two tiers, both from one deck state:
  A. exact   finite-deck hypergeometric access, with inclusion-exclusion for
             multi-role modules (overlapping cards, shared library, no independence);
  B. goldfish seeded Monte Carlo with land drops, colored mana, ramp, real one-shot
             draw, typed narrow tutors and a free first mulligan. No opponents.

Every probability is "access" or "castable", never "the effect was good enough";
threat-specific usability is a separate typed filter (wipe kind vs threat class).
"""
import re, random
from math import comb
from functools import lru_cache
from . import deckeval as E
from .inventory import BASICS, ci_set
from .semantics import clean, wipe_kind as _wipe_kind, protection_profile, THREATS

COLORS = 'WUBRG'
BLANK = '(blank slot)'  # analytic ablation only: a card with no functions, never a physical proposal

# ---------------------------------------------------------------- tier A: exact
def seen(t, on_play=False):
    """Cards seen by your turn t: 7-card hand + one draw per turn (none on turn 1 on the play)."""
    return 7 + t - (1 if on_play else 0)


@lru_cache(maxsize=None)
def p_none(N, n, u):
    """P(none of u specific cards among n seen from a shuffled N-card library)."""
    if u <= 0: return 1.0
    if n >= N: return 0.0
    return comb(N - u, n) / comb(N, n)


def p_any(N, n, k):
    return 1 - p_none(N, n, k)


def p_all(N, n, groups):
    """P(at least one card from EVERY group is seen). Groups are sets of physical card ids and
    may overlap; exact by inclusion-exclusion over the union of groups that are missed.
    An empty group (role absent) gives 0; a group equal to None means commander-supplied (always met)."""
    gs = [frozenset(g) for g in groups if g is not None]
    if any(not g for g in gs): return 0.0
    total = 0.0
    for mask in range(1 << len(gs)):
        u = set()
        for i, g in enumerate(gs):
            if mask >> i & 1: u |= g
        total += (-1) ** bin(mask).count('1') * p_none(N, n, len(u))
    return total


# ---------------------------------------------------------------- typed roles from the record
def text(inv, n):
    if n == BLANK: return ''
    return clean(inv.cards[n]['Oracle Text'], n) if n in inv.cards else ''


def wipe_kind(inv, n):
    return _wipe_kind(text(inv, n))


def protection_scope(inv, n):
    """team: covers more than one creature at once; anti_destroy_wipe: lets several creatures survive a
    destroy wipe (indestructible, shield counters, phasing, persist); all_creatures: every creature."""
    prof = protection_profile(text(inv, n))
    many = [p for p in prof if p['scope'] in ('all_creatures', 'creatures_with_counters', 'other_creatures') or
            (p['scope'].startswith('up_to_') and not p['scope'].startswith('up_to_one'))]
    return {'team': bool(many), 'anti_destroy_wipe': any('destroy' in p['survives'] for p in many),
            'all_creatures': any(p['scope'] == 'all_creatures' and 'destroy' in p['survives'] for p in prof), 'profile': prof}


def roles(inv, library):
    """role -> set of library positions. Uses supported functions only (tag_only never counts)."""
    out = {}
    for i, n in enumerate(library):
        for f in (inv.supported(n) if n != BLANK else ()):
            out.setdefault(f, set()).add(i)
        if n == BLANK: continue
        if 'wipe' in inv.supported(n):
            for k in wipe_kind(inv, n): out.setdefault('wipe:' + k, set()).add(i)
        if 'protection' in inv.supported(n):
            s = protection_scope(inv, n)
            if s['team']: out.setdefault('protection:team', set()).add(i)
            if s['anti_destroy_wipe']: out.setdefault('protection:anti_wipe', set()).add(i)
            if s['all_creatures']: out.setdefault('protection:all_creatures', set()).add(i)
    return out


# ---------------------------------------------------------------- deck state (complete, physical)
class DeckState:
    """Complete physical deck: commanders + library with basic multiplicities. Overlays are
    applied as 1-for-1 replacements at the same library position (common random numbers)."""
    def __init__(self, inv, deck, swaps=()):
        self.inv, self.deck = inv, deck
        self.commanders = [n for n, _, s in inv.decks[deck] if s == 'Commander']
        self.companion = [n for n, _, s in inv.decks[deck] if s == 'Companion']
        self.library = []
        for n, q, s in sorted(inv.decks[deck], key=lambda r: r[0]):
            if s in ('Commander', 'Companion'): continue
            self.library += [n] * q
        for out, inn in swaps:
            i = self.library.index(out) if out else None
            if out and inn: self.library[i] = inn
            elif out: self.library.pop(i)
            elif inn: self.library.append(inn)
        self.swaps = list(swaps)

    @property
    def size(self):
        return len(self.library) + len(self.commanders)

    @property
    def ci(self):
        return set().union(*[ci_set(self.inv.cards[c]['Color Identity']) for c in self.commanders])


def role_access(state, windows=(3, 5, 7, 10), on_play=False):
    N = len(state.library); r = roles(state.inv, state.library)
    cmd = set().union(*[state.inv.supported(c) for c in state.commanders])
    rep = {}
    unk = {}  # tag-only claims: unknown, not absent; they widen the bound, never the estimate
    for i, nm in enumerate(state.library):
        if nm == BLANK: continue
        for f, v in state.inv.record(nm).items():
            if v['status'] == 'tag_only': unk.setdefault(f, set()).add(i)
    for role, pos in sorted(r.items()):
        upper = len(pos | unk.get(role, set()))
        rep[role] = {'k': len(pos), 'k_if_unknowns_true': upper, 'P_seen_T7_upper': round(p_any(N, seen(7, on_play), upper), 4),
                     'unknown_sources': sorted({state.library[i] for i in unk.get(role, set()) - pos}),
                     'commander_supplies': role in cmd,
                     'sources': sorted({state.library[i] for i in pos}),
                     **{f'P_seen_T{t}': round(p_any(N, seen(t, on_play), len(pos)), 4) for t in windows}}
    return rep


# ---------------------------------------------------------------- tier B: goldfish
def mana_cost(inv, n):
    c = str(inv.cards[n]['Mana Cost']).split(' // ')[0]
    if c == 'nan': return 0, []
    sym = re.findall(r"\{([^}]+)\}", c)
    generic, req = 0, []
    for s in sym:
        if s.isdigit(): generic += int(s)
        elif s in ('X', 'C'): generic += 0 if s == 'X' else 1
        elif '/' in s:
            opts = {x for x in s.split('/') if x in COLORS}
            if 'P' in s.split('/'): continue  # phyrexian: pay life
            if s.split('/')[0].isdigit(): generic += int(s.split('/')[0]); continue
            req.append(opts)
        elif s in COLORS: req.append({s})
    return generic, req


def can_pay(units, generic, req):
    """units: list of color sets (one per available mana). Bipartite match colored pips, then generic."""
    if len(units) < generic + len(req): return None
    match = [-1] * len(units)
    def aug(j, seenu):
        for i, u in enumerate(units):
            if i in seenu or not (u & req[j]): continue
            seenu.add(i)
            if match[i] == -1 or aug(match[i], seenu):
                match[i] = j; return True
        return False
    for j in range(len(req)):
        if not aug(j, set()): return None
    used = {i for i, m in enumerate(match) if m != -1}
    rest = [i for i in range(len(units)) if i not in used]
    return sorted(used) + rest[:generic]


class CardModel:
    """Per-card goldfish behaviour, typed from Oracle text. Every class is printed in the report."""
    def __init__(self, inv, n, ci):
        if n == BLANK:
            self.name, self.mv_generic, self.req, self.is_land, self.creature, self.types = n, 99, [], False, False, ''
            self.mana = 0; self.mana_colors = set(); self.mana_delay = 0; self.mana_once = False; self.fetch = False; self.land_aura = None
            self.draw_once = 0; self.draw_engine = False; self.token = None; self.counter_once = False; self.mutagen = False
            self.counter_on_entry = False; self.held = True; self.tutor_target = None
            return
        r = inv.cards[n]; t = text(inv, n); tl = str(r['Type Line'])
        self.name, self.mv_generic, self.req = n, *mana_cost(inv, n)
        self.is_land = inv.is_land(n) and not tl.startswith(('Instant', 'Sorcery'))
        if ' // ' in n and 'Land' in tl.split(' // ')[-1]: self.is_land = True  # MDFC with land back
        self.creature = 'Creature' in tl.split(' // ')[0]
        self.types = tl
        prod = ci_set(r['Produces']) if str(r['Produces']) != 'nan' else set()
        self.land_colors, self.land_tapped = set(), False
        if self.is_land:
            m = re.search(r"search your library for a basic ([\w ,]+?) card", t)
            if 'commander' in t and 'any color' in t: prod = set(ci)
            if m:
                prod = {c for c, b in zip(COLORS, ['plains', 'island', 'swamp', 'mountain', 'forest']) if b in m.group(1)} or set(ci)
                if 'basic land card, put it onto the battlefield' in t: prod = set(ci)
                self.land_tapped = True
            if 'spend this mana only' in t: prod = set()  # restricted colors (Turtle Lair) count as colorless
            self.land_colors = (prod & set(ci)) or {'C'}
            et = str(r['ETB Tapped'])
            self.land_tapped = self.land_tapped or et == 'Yes'
            self.land_conditional = et == 'Conditional'
        # mana sources (nonland)
        self.mana = 0; self.mana_colors = set(); self.mana_delay = 0; self.mana_once = False; self.fetch = False; self.land_aura = None
        if not self.is_land:
            any_c = re.search(r"any color|any combination of colors|any one color", t)
            cols = (set(ci) if any_c else prod & set(ci)) or {'C'}
            if re.search(r"\{t\}: add \{c\}\{c\}", t): self.mana, self.mana_colors = 2, {'C'}
            elif re.search(r"(?:\{t\}|\{g\}, \{t\}): add", t) and 'enchanted land has' not in t: self.mana, self.mana_colors = 1, cols
            if self.mana and self.creature: self.mana_delay = 1
            if 'enchanted land' in t and 'additional one mana' in t: self.mana, self.mana_colors, self.land_aura = 1, set(ci), 'extra'
            if 'enchanted land has' in t and 'any color' in t: self.land_aura = 'fix'
            if re.search(r"create a treasure", t) and re.search(r"when (?:~|this creature) enters", t): self.mana, self.mana_colors, self.mana_once = 1, set(ci), True
            if re.search(r"when (?:~|this creature) enters, create a food", t) and 'sacrifice a food: add' in t: self.mana, self.mana_colors, self.mana_once = 1, set(ci), True
            if re.search(r"at the beginning of your [\w ]*main phase, create a food", t) and 'add one mana' in t: self.mana, self.mana_colors, self.mana_delay = 1, set(ci), 1
            if re.search(r"search your library for (?:a|up to \w+) basic land[^.]*onto the battlefield", t): self.fetch = True
        # draw
        self.draw_once = 0; self.draw_engine = False
        for sent in re.split(r"(?<=[.])\s|\n", t):
            m = re.search(r"\bdraws? (a|one|two|three) cards?", sent)
            if not m and 'investigate' not in sent: continue
            k = {'a': 1, 'one': 1, 'two': 2, 'three': 3}.get(m.group(1), 1) if m else 0
            if re.search(r"\bwhenever\b|at the beginning|\bif\b|sacrifice|\{", sent): self.draw_engine = True
            elif re.search(r"when (?:~|this \w+) enters", sent) or tl.startswith(('Instant', 'Sorcery')): self.draw_once += k
        # tokens (for module cadence)
        self.token = None
        for sent in re.split(r"(?<=[.])\s|\n", t):
            if not re.search(r"\bcreate\b|\binvestigate\b", sent): continue
            if re.search(r"^when [^,]*?enters", sent) or tl.startswith(('Instant', 'Sorcery')):
                self.token = self.token or 'one_shot'
            elif re.search(r"at the beginning of", sent):
                self.token = 'each_turn_if_creature' if 'nontoken creatures' in sent else 'each_turn'
            elif re.search(r"whenever (?:~ or another |another |a |one or more )?([\w, ]*?)(?:creatures? )?(?:you control )?enters", sent):
                self.token = 'on_creature_entry'
                tm = re.search(r"whenever (?:~ or another |a )([\w, ]+?) you control enters", sent)
                self.token_types = [w.strip(' ,') for w in re.split(r",|\bor\b|and/or", tm.group(1))] if tm else []
            elif re.search(r"\{[^}]+\}[^:]*: create", sent):
                self.token = 'activated'; self.token_cost = sum(int(x) if x.isdigit() else 1 for x in re.findall(r"\{([^}t]+)\}", sent.split(':')[0]))
            else:
                self.token = self.token or 'conditional_unmodelled'
        self.counter_once = bool(re.search(r"(?:when (?:~|this \w+) enters, put|enters with) (?:a|one|two|\w+) \+1/\+1 counters?|^put (?:a|two) \+1/\+1 counter", t)) or \
            (tl.startswith(('Instant', 'Sorcery')) and '+1/+1 counter' in t)
        self.mutagen = 'mutagen token' in t
        self.counter_on_entry = bool(re.search(r"whenever another (?:nontoken )?creature you control enters, put a \+1/\+1 counter", t))
        self.held = tl.startswith(('Instant', 'Sorcery')) and bool(inv.supported(n) & {'spot_removal', 'wipe', 'counterspell', 'protection'})
        # typed narrow tutor (partner-with): exact target, to hand, on ETB
        raw = str(r['Oracle Text']).lower()  # reminder text carries the partner-with search, so read it raw
        m = re.search(r"partner with ([^(]+?) \(when this creature enters, target player may put", raw)
        self.tutor_target = m.group(1).strip() if m else None


def _models(state):
    ms = {}
    for n in set(state.library) | set(state.commanders):
        ms[n] = CardModel(state.inv, n, state.ci)
    for n in ms:  # restore exact names for partner targets (text is lower-cased)
        if ms[n].tutor_target:
            ms[n].tutor_target = next((x for x in ms if x.lower() == ms[n].tutor_target), None)
    return ms


def goldfish(state, games=20000, turns=10, seed=20261018, on_play=False, draw_mode='one_shot',
             tutors=True, role_sets=None, mulligan=True, trace=(), observer=None, cast_commander=False):
    """observer(g, t, info): optional per-turn hook for scenario layers (validation.py); it reads state and
    changes nothing. cast_commander: also cast non-Leonardo commanders when affordable (off by default so
    the frozen ACCESS.md numbers reproduce exactly).
    Returns per-turn rates. draw_mode: 'none' | 'one_shot' | 'engines' (one-shot + 1 card/turn per
    engine on the battlefield, an optimistic upper bound). Mulligan: free 7-card redraw if 0-1 or 6-7 lands."""
    inv = state.inv; ms = _models(state); lib0 = state.library; N = len(lib0)
    role_sets = role_sets or {}
    acc = {k: [0] * (turns + 1) for k in ['mana4', 'mana5', 'all_colors', 'W', 'leo', 'modA', 'modB', 'modA_by', 'modB_by', 'counter_event']}
    for k in role_sets: acc['seen:' + k] = [0] * (turns + 1); acc['cast:' + k] = [0] * (turns + 1)
    totals = {'modA_turns_by_T8': 0, 'modB_turns_by_T8': 0, 'lands_T5': 0}
    per_game = {f'{k}@T{t}': [] for k, t in trace}
    leo = next((c for c in state.commanders if c.startswith('Leonardo')), None)
    payoffs_B = {n for n in lib0 if n.startswith(('Casey Jones', 'Terrasymbiosis'))}
    for g in range(games):
        rng = random.Random(seed * 1000003 + g)
        perm = list(range(N)); rng.shuffle(perm)
        lib = [lib0[i] for i in perm]
        hand = lib[:7]; pos = 7
        nl = sum(ms[c].is_land for c in hand)
        if mulligan and (nl <= 1 or nl >= 6):  # free first mulligan (multiplayer Commander), keep the next seven
            rng.shuffle(lib); hand = lib[:7]; pos = 7
        lands, sources, bf = [], [], set()
        seen_set = set(hand); leo_on = False; extra_cards = 0
        mutagens = 0; firstA = firstB = False
        for t in range(1, turns + 1):
            before_turn = {k: acc[k][t] for k, _ in trace}
            if not (t == 1 and on_play):
                if pos < N: hand.append(lib[pos]); seen_set.add(lib[pos]); pos += 1
            # land drop: prefer untapped land adding a missing color
            have = set().union(*[l[0] for l in lands]) if lands else set()
            cands = [c for c in hand if ms[c].is_land]
            if cands:
                def lkey(c):
                    m = ms[c]; tapped = m.land_tapped or (m.land_conditional and len(lands) < 2)
                    return (tapped, -len(m.land_colors - have), c)
                c = min(cands, key=lkey); hand.remove(c); m = ms[c]
                tapped = m.land_tapped or (m.land_conditional and len(lands) < 2)
                lands.append([set(m.land_colors), t + (1 if tapped else 0)])
            units = [l[0] for l in lands if l[1] <= t] + [s[0] for s in sources if s[1] <= t for _ in range(s[2])]
            units_start = list(units)
            # measure availability at the start of the main phase (before this turn's spending)
            if len(units) >= 4: acc['mana4'][t] += 1
            if len(units) >= 5: acc['mana5'][t] += 1
            col = set().union(*units) if units else set()
            if set(state.ci) <= col and can_pay(units, 0, [{c} for c in state.ci]) is not None: acc['all_colors'][t] += 1
            if 'W' in col: acc['W'][t] += 1
            for k, names in role_sets.items():
                if seen_set & names: acc['seen:' + k][t] += 1
                # available = on the battlefield already, or in hand and castable with this turn's mana
                if (bf & names) or any(c in names and can_pay(units, ms[c].mv_generic, ms[c].req) is not None for c in hand): acc['cast:' + k][t] += 1
            # spend: ramp first, then commander, then draw, then token makers (greedy goldfish)
            token_event = False; counter_event = False; cast_creature_types = []; deployed_now = set()
            def cast(c):
                nonlocal units
                pay = can_pay(units, ms[c].mv_generic, ms[c].req)
                if pay is None: return False
                units = [u for i, u in enumerate(units) if i not in set(pay)]
                return True
            for c in sorted([c for c in hand if (ms[c].mana or ms[c].fetch or ms[c].land_aura) and not ms[c].is_land], key=lambda c: ms[c].mv_generic + len(ms[c].req)):
                if c in hand and cast(c):
                    hand.remove(c); m = ms[c]; bf.add(c)
                    if draw_mode != 'none' and m.draw_once:  # e.g. Abundant Growth: fixing aura that also draws
                        for _ in range(m.draw_once):
                            if pos < N: hand.append(lib[pos]); seen_set.add(lib[pos]); pos += 1
                    if m.fetch: lands.append([set(state.ci), t + 1])
                    if m.land_aura == 'fix' and lands: min(lands, key=lambda l: len(l[0]))[0] = set(state.ci)
                    if m.land_aura == 'extra':  # one chosen color: the color the deck lacks most
                        have_now = set().union(*[l[0] for l in lands]) if lands else set()
                        pick = next((x for x in COLORS if x in state.ci and x not in have_now), 'G')
                        sources.append([{pick}, t, 1]); units.append({pick})
                    elif m.mana and m.mana_once: units.append(set(m.mana_colors))
                    elif m.mana: sources.append([set(m.mana_colors), t + m.mana_delay, m.mana])
                    if m.creature: cast_creature_types.append(m.types)
                    if m.token == 'one_shot': token_event = True
            if leo and not leo_on and cast(leo): leo_on = True; cast_creature_types.append(ms[leo].types)
            if leo_on: acc['leo'][t] += 1
            if cast_commander:
                for cm in state.commanders:
                    if cm != leo and cm not in bf and cast(cm): bf.add(cm); cast_creature_types.append(ms[cm].types)
            if draw_mode != 'none':
                for c in [c for c in hand if ms[c].draw_once and not ms[c].is_land]:
                    if cast(c):
                        hand.remove(c); bf.add(c)
                        for _ in range(ms[c].draw_once):
                            if pos < N: hand.append(lib[pos]); seen_set.add(lib[pos]); pos += 1
                        if ms[c].creature: cast_creature_types.append(ms[c].types)
                        if ms[c].token == 'one_shot': token_event = True
            # deploy: token makers first, then other creatures/permanents; instants and sorceries stay in hand
            deploy = [c for c in hand if not ms[c].is_land and not ms[c].held and (ms[c].token or ms[c].creature or ms[c].counter_on_entry) and c not in payoffs_B]
            for c in sorted(deploy, key=lambda c: (not ms[c].token, ms[c].mv_generic + len(ms[c].req), c)):
                if c in hand and cast(c):
                    hand.remove(c); bf.add(c); deployed_now.add(c)
                    if ms[c].creature: cast_creature_types.append(ms[c].types)
                    if ms[c].token == 'one_shot': token_event = True
                    if ms[c].mutagen and ms[c].token == 'one_shot': mutagens += 1
                    if ms[c].counter_once: counter_event = True
                    if draw_mode != 'none':
                        for _ in range(ms[c].draw_once):
                            if pos < N: hand.append(lib[pos]); seen_set.add(lib[pos]); pos += 1
                    tg = ms[c].tutor_target
                    if tutors and tg and tg in lib[pos:]:  # typed narrow tutor: that one card, to hand, on ETB
                        lib.remove(tg); lib.insert(pos, tg); hand.append(tg); seen_set.add(tg); pos += 1
            for c in bf:
                m = ms[c]
                if m.counter_on_entry and len(cast_creature_types) > (1 if c in deployed_now else 0): counter_event = True
                if m.token == 'each_turn': token_event = True
                elif m.token == 'each_turn_if_creature' and cast_creature_types: token_event = True
                elif m.token == 'on_creature_entry' and any(not m.token_types or any(ty.lower() in tl.lower() for ty in m.token_types) for tl in cast_creature_types):
                    token_event = True
                    if m.mutagen: mutagens += 1
                elif m.token == 'activated' and len(units) >= getattr(m, 'token_cost', 2):
                    units = units[getattr(m, 'token_cost', 2):]; token_event = True
            if draw_mode == 'engines':
                for c in bf:
                    if ms[c].draw_engine and pos < N: hand.append(lib[pos]); seen_set.add(lib[pos]); pos += 1
            modA = leo_on and token_event
            if modA: counter_event = True
            if mutagens and units: mutagens -= 1; units = units[1:]; counter_event = True
            if counter_event: acc['counter_event'][t] += 1
            modB = bool(payoffs_B & bf) and counter_event
            for c in [c for c in hand if c in payoffs_B]:
                if cast(c): hand.remove(c); bf.add(c)
            if modA: acc['modA'][t] += 1; totals['modA_turns_by_T8'] += t <= 8; firstA = True
            if modB: acc['modB'][t] += 1; totals['modB_turns_by_T8'] += t <= 8; firstB = True
            acc['modA_by'][t] += firstA; acc['modB_by'][t] += firstB
            if t == 5: totals['lands_T5'] += len(lands)
            if observer:
                observer(g, t, {'hand': hand, 'bf': bf | ({leo} if leo_on else set()), 'seen': seen_set, 'units_start': units_start,
                                'units_end': units, 'models': ms, 'token_event': token_event, 'counter_event': counter_event,
                                'modA': modA, 'leo_on': leo_on, 'lands': len(lands)})
            for k, tt in trace:
                if tt == t: per_game[f'{k}@T{t}'].append(acc[k][t] - before_turn[k])
    out = {k: [round(v / games, 4) for v in arr[1:]] for k, arr in acc.items()}
    out.update({k: round(v / games, 3) for k, v in totals.items()})
    out['games'] = games; out['draw_mode'] = draw_mode; out['on_play'] = on_play
    if trace: out['_per_game'] = per_game
    return out


def paired_delta(base, var, key):
    """Common-random-number difference var-base for one traced flag, with its standard error."""
    a, b = base['_per_game'][key], var['_per_game'][key]
    d = [y - x for x, y in zip(a, b)]; n = len(d); m = sum(d) / n
    se = (sum((x - m) ** 2 for x in d) / (n - 1) / n) ** 0.5
    return round(m, 4), round(se, 4)


def model_report(state):
    ms = _models(state); rows = []
    for n in sorted(ms):
        m = ms[n]
        if m.is_land:
            rows.append({'card': n, 'land_colors': ''.join(sorted(m.land_colors)), 'tapped': m.land_tapped, 'conditional': m.land_conditional})
        else:
            d = {'card': n, 'cost': f"{m.mv_generic}+{''.join('/'.join(sorted(r)) for r in m.req)}"}
            if m.mana: d['mana'] = f"+{m.mana} {''.join(sorted(m.mana_colors))}{' once' if m.mana_once else ''}{' (sick 1 turn)' if m.mana_delay else ''}"
            if m.fetch: d['ramp'] = 'fetches basic tapped'
            if m.draw_once: d['draw_once'] = m.draw_once
            if m.draw_engine: d['draw_engine'] = 'conditional/repeatable (only in engines mode)'
            if m.token: d['token'] = m.token
            if m.tutor_target: d['tutor'] = f'partner-with: {m.tutor_target} to hand on ETB'
            if len(d) > 2: rows.append(d)
    return rows


# ---------------------------------------------------------------- ablation and cut certification
KEY_ROLES = ['ramp', 'draw', 'spot_removal', 'wipe', 'protection', 'recursion', 'closer', 'counterspell']


def module_access(state, window=7, on_play=False):
    """Exact raw draw access for each candidate module: P(every group has a seen card), with groups
    the commander fills treated as anchored (no draw needed; deployment is separate)."""
    N = len(state.library); n = seen(window, on_play); r = roles(state.inv, state.library)
    cmd = set().union(*[state.inv.supported(c) for c in state.commanders])
    out = {}
    for m, groups in E.MODULES.items():
        gs = [None if set(g) & cmd else set().union(*[r.get(f, set()) for f in g]) for g in groups]
        out[m] = round(p_all(N, n, gs), 4)
    return out


def ablation(state, card, window=7):
    """Replace one copy of `card` with a blank and report the exact access change per key role
    and per module (negative = loss). Analytic only; the blank is never a physical proposal."""
    base_r = role_access(state, (window,)); base_m = module_access(state, window)
    ab = DeckState(state.inv, state.deck, state.swaps + [(card, BLANK)])
    r = role_access(ab, (window,)); m = module_access(ab, window)
    key = f'P_seen_T{window}'
    dr = {f: round(r.get(f, {}).get(key, 0) - base_r[f][key], 4) for f in KEY_ROLES if f in base_r}
    dm = {k: round(m[k] - base_m[k], 4) for k in m if m[k] != base_m[k]}
    sole = [f for f in KEY_ROLES if f in base_r and base_r[f]['k'] == 1 and dr.get(f)]
    return {'card': card, 'role_delta': {k: v for k, v in dr.items() if v}, 'module_delta': dm, 'sole_source_of': sole}


def certify_cut(state, card, models=None):
    """A cut is certified only when no flag fires. Flags block automatic cuts; they never forbid a
    human from choosing the card. Vetoes (a user never-cut list) can be passed as extra blocks."""
    inv = state.inv; ms = models or _models(state); m = ms[card]; r = inv.cards[card]
    flags = []
    if not inv.supported(card) - {'creature', 'instant_sorcery', 'land'}: flags.append('unpriced: the record reads no function')
    if m.token in ('each_turn', 'each_turn_if_creature', 'on_creature_entry', 'activated') or m.draw_engine or (m.mana and not m.mana_once) or m.counter_on_entry:
        flags.append('repeatable engine (token, draw, mana or counter cadence)')
    tl = str(r['Type Line'])
    try: power = int(r['Power'])
    except (TypeError, ValueError): power = 0
    if 'Creature' in tl and (float(r['Mana Value'] or 0) >= 5 or power >= 5): flags.append('large threat body (MV>=5 or power>=5): rate not priced')
    if str(r['Rarity']).lower() == 'mythic': flags.append('mythic: impact not priced')
    cmd = set().union(*[inv.supported(c) for c in state.commanders])
    plan_f = {f for gs in E.MODULES.values() if any(set(g) & cmd for g in gs) for g in gs for f in g}
    cnt = {}
    for n in state.library:
        for f in (inv.supported(n) if n != BLANK else ()): cnt[f] = cnt.get(f, 0) + 1
    # a role of the commander's plan that few library cards supply: losing one is a plan risk
    partner = sorted(f for f in inv.supported(card) & plan_f if cnt.get(f, 0) <= 4)
    if partner: flags.append('thin commander-plan role: ' + ', '.join(f'{f} ({cnt[f]} in library)' for f in partner))
    a = ablation(state, card)
    if a['sole_source_of']: flags.append('sole source of ' + ', '.join(a['sole_source_of']))
    big = {k: v for k, v in {**a['role_delta'], **a['module_delta']}.items() if v <= -0.03}
    if big: flags.append('access loss >= 3 points: ' + ', '.join(f'{k} {v:+.3f}' for k, v in big.items()))
    loss = round(-sum(v for v in list(a['role_delta'].values()) + list(a['module_delta'].values()) if v < 0), 4)
    return {'card': card, 'certified': not flags, 'flags': flags, 'total_access_loss_T7': loss, **a}


def certified_cuts(state, protect=()):
    ms = _models(state)
    rows = [certify_cut(state, n, ms) for n in sorted(set(state.library)) if n not in BASICS and n != BLANK
            and not ms[n].is_land and n not in protect]
    ok = sorted([r for r in rows if r['certified']], key=lambda r: (r['total_access_loss_T7'], r['card']))
    return ok, [r for r in rows if not r['certified']]
