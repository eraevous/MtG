"""Turn engine with a resource ledger (0.3.0). An unopposed goldfish with object identities:
every creature, artifact and token is one object that is either untapped or tapped, sick or not,
and can be spent once per window. Abilities come from abilities.card_record (typed projections),
mana from access.CardModel (the land and rock model the access layer already tests).

Per turn: untap, upkeep, draw, main 1, combat, main 2, end step, then the opponents' turns
(held instants are cast there with leftover mana). Rules the ledger keeps apart:
- {T} abilities of a creature need it to be free of summoning sickness; tapping it to pay another
  permanent's cost (crew, station, Springleaf Drum, Raff) does not (CR 302.6);
- station is sorcery speed, one creature per activation, charge = that creature's power;
  crew is any number of creatures with total power N;
- vigilance attackers stay untapped, so they can station or pay costs in main 2;
- a token sacrificed for mana is gone; a tapped object cannot pay another tap cost;
- cast, enter, create, leave, sacrifice, attack and combat-damage are separate hooks: tokens
  entering never trigger "whenever you cast";
- once-per-turn caps are enforced per ability per turn;
- commander tax: +2 generic per earlier cast from the command zone.

Policies decide who gets a contested body: attack_first, station_first, mana_first.
Assumptions (always printed): no blockers, no opponent removal unless a named scenario says so,
interaction spells always find a target, one opponent at 40 life takes all combat damage."""
import random
from collections import defaultdict
from .abilities import card_record
from . import access as A

POLICIES = ('attack_first', 'station_first', 'mana_first')
ASSUMPTIONS = [
    'Unopposed goldfish: no blockers and no opponent removal except in a named scenario.',
    'Interaction spells (removal, counters, bounce) are cast with leftover mana as if a target exists; that matters because casting them still triggers "whenever you cast".',
    'Combat damage all goes to one opponent at 40 life; drain hits each opponent. Reach (damage to any target) is reported, not counted toward lethal.',
    'Equipment, Class levels, planeswalker loyalty abilities, copy effects and modal choices beyond the first useful mode are not modelled.',
]


class Obj:
    __slots__ = ('id', 'name', 'token', 'types', 'subtypes', 'power', 'tough', 'kw', 'sick', 'tapped', 'counters', 'charge',
                 'abil', 'st', 'cmd', 'mana_sac', 'crewed', 'model', 'fired')

    def __init__(self, oid, name, types, power=0, tough=0, kw=(), token=False, abil=(), st=None, cmd=False, mana_sac=False, model=None, subtypes=()):
        self.id, self.name, self.token, self.types = oid, name, token, set(types)
        self.subtypes = set(subtypes); self.power, self.tough, self.kw = power, tough, set(kw)
        self.sick, self.tapped, self.counters, self.charge = True, False, 0, 0
        self.abil, self.st, self.cmd, self.mana_sac, self.crewed, self.model = list(abil), st or {}, cmd, mana_sac, False, model
        self.fired = defaultdict(int)


def _num(v):
    try: return int(float(str(v)))
    except ValueError: return 0


def matches(f, obj=None, spell_types=None, is_token=False):
    """Type filter from abilities._types_filter against an object (or a spell's types)."""
    types = obj.types if obj is not None else spell_types
    tok = obj.token if obj is not None else is_token
    if 'any' in f: return True
    if 'token' in f and not tok: return False
    if 'nontoken' in f and tok: return False
    if 'noncreature' in f: return 'creature' not in types
    if 'nonartifact' in f and 'artifact' in types: return False
    subs = {x[4:] for x in f if x.startswith('sub:')}
    want = {x for x in f if not x.startswith('sub:')} - {'token', 'nontoken', 'nonartifact'}
    if subs:
        have = obj.subtypes if obj is not None else {x[4:] for x in types if isinstance(x, str) and x.startswith('sub:')}
        if not subs & {h.lower() for h in have}: return False
        return not want or bool(want & types)
    if not want: return True
    return bool(want & types)


class Game:
    def __init__(self, ev, state, rng, policy='attack_first', scenario=None, log=None):
        self.inv, self.state, self.rng, self.policy = state.inv, state, rng, policy
        self.sc = scenario or {}
        self.ms = ev['models']; self.rec = ev['records']
        self.lib = list(state.library); rng.shuffle(self.lib)
        self.hand = self.lib[:7]; self.pos = 7
        nl = sum(self.ms[c].is_land for c in self.hand)
        if nl <= 1 or nl >= 6: rng.shuffle(self.lib); self.hand = self.lib[:7]
        self.bf, self.lands = [], []
        self.nid = 0; self.t = 0
        self.cmd_zone = [] if self.sc.get('no_commander') else list(state.commanders)
        self.cmd_casts = defaultdict(int)
        self.dmg = 0; self.drain = 0; self.reach = 0; self.drawn = 0; self.spells_turn = 0
        self.m = defaultdict(float)  # per-game metrics, keyed 'name@T'
        self.log = log
        self.station_done = {}

    # ------------------------------------------------------------ helpers
    def new(self, name, **kw):
        self.nid += 1
        o = Obj(self.nid, name, **kw); self.bf.append(o); return o

    def draw(self, n=1):
        for _ in range(n):
            if self.pos < len(self.lib): self.hand.append(self.lib[self.pos]); self.pos += 1; self.drawn += 1
            if getattr(self, '_in_draw', False): continue
            self._in_draw = True; self.fire('draw'); self._in_draw = False

    def note(self, k, v=1):
        self.m[f'{k}@{self.t}'] += v

    def creatures(self):
        return [o for o in self.bf if self.is_creature(o)]

    def is_creature(self, o):
        if 'creature' in o.types: return True
        if o.crewed: return True
        st = o.st.get('station')
        return bool(st and o.charge >= st)

    def anthem(self, o):
        p = 0
        for s in self.bf:
            for a in s.st.get('anthem', []):
                sc = a['scope']
                if sc == 'other creatures' and s is o: continue
                if sc == 'thopters' and 'thopter' not in o.subtypes: continue
                if sc == 'artifact creatures' and 'artifact' not in o.types: continue
                if sc == 'tokens' and not o.token: continue
                p += a['p']
            for lv in s.st.get('station_levels', []):
                if lv['anthem'] and s.charge >= lv['at'] and s is not o: p += lv['anthem']
        return p

    def pw(self, o):
        base = o.power if self.is_creature(o) or o.crewed else 0
        if o.st.get('station') and o.charge >= o.st['station']: base = o.power
        return max(0, base + o.counters + self.anthem(o) + getattr(self, 'pump', 0))

    def vigilant(self, o):
        if 'vigilance' in o.kw: return True
        for s in self.bf:
            v = s.st.get('vigilance_for')
            if v == 'artifact creatures' and 'artifact' in o.types: return True
            if v in ('creatures', 'tokens') and (v == 'creatures' or o.token): return True
        return False

    def can_attack(self, o):
        return bool(self.is_creature(o) and not o.tapped and (not o.sick or 'haste' in o.kw or o.st.get('haste')))

    # ------------------------------------------------------------ mana
    def mana_units(self, allow_bodies):
        """(colors, source, kind). kind: land | rock | dork | sac_body | drum. Bodies only when allowed."""
        units = []
        for i, l in enumerate(self.lands):
            if not l['tapped'] and l['ready'] <= self.t: units.append((l['colors'], ('land', i), 'land'))
        ci = set(self.state.ci) or {'C'}
        for o in self.bf:
            if o.tapped: continue
            md = o.model
            if md is not None and md.mana and not md.mana_once and not md.is_land:
                if self.is_creature(o) and o.sick: continue
                for _ in range(md.mana): units.append((set(md.mana_colors), o, 'dork' if self.is_creature(o) else 'rock'))
            elif o.mana_sac and not o.sick or (o.mana_sac and not self.is_creature(o)):
                if self.is_creature(o) and not allow_bodies: continue
                units.append((ci, o, 'sac_body' if self.is_creature(o) else 'treasure'))
        if allow_bodies:
            for o in self.bf:  # Springleaf Drum shape: {T}, tap an untapped creature: add one mana
                if o.tapped: continue
                for a in o.abil:
                    c = a.get('cost') or {}
                    if a['kind'] == 'activated' and c.get('tap_self') and (c.get('tap_other') or {}).get('kind') == 'creature' and any(x[0] == 'mana' for x in a['outputs']):
                        body = next((b for b in self.creatures() if not b.tapped and b is not o and not b.mana_sac), None)
                        if body: units.append((ci, (o, body), 'drum'))
        return units

    def pay(self, generic, req, allow_bodies, why):
        units = self.mana_units(allow_bodies)
        order = {'land': 0, 'rock': 1, 'treasure': 2, 'dork': 3, 'drum': 4, 'sac_body': 5}
        units.sort(key=lambda u: order[u[2]])
        pick = A.can_pay([u[0] for u in units], generic, req)
        if pick is None: return False
        used_src = set()
        for i in pick:
            colors, src, kind = units[i]
            if kind == 'land': self.lands[src[1]]['tapped'] = True
            elif kind in ('rock', 'dork'):
                if id(src) in used_src: continue
                src.tapped = True; used_src.add(id(src))
            elif kind == 'treasure': self.leave(src, sacrificed=True)
            elif kind == 'sac_body':
                self.spend(src); src.tapped = True; self.leave(src, sacrificed=True); self.note('body:mana')
            elif kind == 'drum':
                self.spend(src[1]); src[0].tapped = True; src[1].tapped = True; self.note('body:mana')
        return True

    def cost_of(self, c):
        md = self.ms[c]; g, req = md.mv_generic, md.req
        tl = str(self.inv.cards[c]['Type Line']).lower()
        for o in self.bf:
            for r in o.st.get('cost_reduction', []):
                f = r['filter']
                if ('artifact' in f and 'artifact' in tl) or ('noncreature' in f and 'creature' not in tl.split('//')[0]): g = max(0, g - r['n'])
        if c in self.state.commanders: g += 2 * self.cmd_casts[c]
        return g, req

    # ------------------------------------------------------------ events
    def fire(self, ev, subj=None, spell_types=None, depth=0):
        if depth > 40: return
        for o in list(self.bf):
            for k, a in enumerate(o.abil):
                if a['kind'] != 'triggered' or a['hook'] is None or a['hook'][0] != ev: continue
                h = a['hook'][1]
                if not self._hook_ok(ev, h, o, subj, spell_types): continue
                g = a.get('gates') or {}
                key = (k, self.t)
                if g.get('once_per_turn') and o.fired[key]: continue
                if g.get('batch') and o.fired[('batch', ev, k, self.t, getattr(self, 'combat_no', 0))]: continue
                cond = g.get('condition')
                if cond and cond[0] == 'control' and not any(cond[1] in x.types for x in self.bf): continue
                if cond and cond[0] == 'tapped_creatures' and sum(1 for x in self.creatures() if x.tapped) < cond[1]: continue
                if a.get('cost') and a['cost'].get('tap_other'):
                    if not self.pay_tap_other(a['cost']['tap_other'], optional=True): continue
                o.fired[key] += 1
                if g.get('batch'): o.fired[('batch', ev, k, self.t, getattr(self, 'combat_no', 0))] += 1
                self.note(f'trigger:{o.name}')
                self.resolve(a['outputs'], o, depth + 1)

    def _hook_ok(self, ev, h, o, subj, spell_types):
        if ev == 'cast':
            if 'second spell' in h: return self.spells_turn == 2
            return matches(h, spell_types=spell_types)
        if ev in ('enter', 'leave', 'sacrifice', 'dies', 'create', 'counters'):
            if h.get('self'): return subj is o
            if subj is o and h.get('other'): return False
            if h.get('self_or_other'): return subj is o or matches(h['types'], subj)
            return matches(h.get('types', {'any'}), subj)
        if ev == 'combat_damage':
            if h.get('self'): return subj is o
            return matches(h.get('types', {'creature'}), subj)
        if ev == 'attack':
            return not h.get('self') or subj is o
        return True

    def resolve(self, outs, src, depth=0):
        for out in outs:
            k = out[0]
            if k == 'token':
                self.create(out[1], src, depth)
            elif k == 'drain': self.drain += out[1]; self.note('drain', out[1]); self.note(f'drain:{src.name if src else "spell"}', out[1])
            elif k == 'reach': self.reach += out[1]
            elif k == 'draw': self.draw(out[1]); self.note('draw:engine' if src else 'draw:spell', out[1])
            elif k == 'scry_surveil': self.fire('scry_surveil', depth=depth)
            elif k == 'counters' and src is not None:
                tgt = src if out[2].startswith(('~', 'this', 'it')) else max(self.creatures(), key=self.pw, default=None)
                if tgt: tgt.counters += out[1]; self.fire('counters', tgt, depth=depth)
            elif k == 'life': self.fire('lifegain', depth=depth)
            elif k == 'charge':
                sp = next((o for o in self.bf if o.st.get('station') and o.charge < o.st['station']), None)
                if sp: sp.charge += out[1]
            elif k == 'pump_team': self.pump = getattr(self, 'pump', 0) + out[1]
            elif k == 'pump_team_x':
                self.pump = getattr(self, 'pump', 0) + sum(1 for o in self.bf if out[1].rstrip('s') in o.types)

    def create(self, spec, src, depth=0):
        specs = [spec]
        if 'artifact' in spec['types'] or 'creature' in spec['types']:
            for o in self.bf:
                for r in o.st.get('replacement_create', []):
                    if matches(r['filter'], spell_types=spec['types'], is_token=True):
                        specs += [dict(x) for x in r['extra']]
                        if r['double']: specs.append(dict(spec))
        made = []
        if len(self.bf) > 150:  # board explosion: count it, stop simulating more objects
            self.m['capped'] = 1; return
        for sp in specs:
            for _ in range(max(1, sp['n'])):
                abil = []
                kind = sp.get('kind')
                if kind == 'clue': abil = [{'kind': 'activated', 'hook': None, 'cost': {'mana': (2, []), 'tap_self': False, 'tap_other': None, 'sac': None, 'sac_self': True}, 'gates': {}, 'outputs': [('draw', 1)], 'line': 'clue'}]
                o = self.new(('token:' + '/'.join(sorted(sp['subtypes'])))[:40], types=sp['types'], power=sp['power'], tough=sp['toughness'],
                             kw=sp['keywords'], token=True, abil=abil, mana_sac=sp['mana_sac'], subtypes=sp['subtypes'])
                o.tapped = sp['tapped']
                made.append(o)
                self.note('tokens'); self.note(f'tokens:{src.name if src else "spell"}')
        for o in made:
            self.fire('create', o, depth=depth); self.fire('enter', o, depth=depth)

    def leave(self, o, sacrificed=False, dies=False):
        if o not in self.bf: return
        self.fire('leave', o)
        if sacrificed: self.fire('sacrifice', o)
        if dies and self.is_creature(o): self.fire('dies', o)
        if o in self.bf: self.bf.remove(o)
        if o.cmd: self.cmd_zone.append(o.name)

    def spend(self, b):
        """Ledger: a body that could have attacked this turn is spent before combat."""
        if self.combat_no == 0 and self.can_attack(b): self.note('body:diverted')

    def pay_tap_other(self, need, optional=False):
        """Tap N other untapped creatures/artifacts from the spare pool (bodies the policy has not reserved)."""
        pool = [b for b in self.bf if not b.tapped and (self.is_creature(b) if need['kind'] == 'creature' else 'artifact' in b.types)]
        pool = [b for b in pool if b.id not in self.reserved]
        if len(pool) < need['n']: return False
        for b in sorted(pool, key=self.pw)[:need['n']]: self.spend(b); b.tapped = True
        self.note('body:tap_cost', need['n'])
        return True

    # ------------------------------------------------------------ casting
    def cast(self, c, allow_bodies):
        if c in self.cmd_zone:
            g, req = self.cost_of(c)
        else:
            g, req = self.cost_of(c)
        if not self.pay(g, req, allow_bodies, c): return False
        if c in self.cmd_zone: self.cmd_zone.remove(c); self.cmd_casts[c] += 1; self.note('commander_cast')
        else: self.hand.remove(c)
        self.spells_turn += 1; self.note('spells')
        rec = self.rec[c]; md = self.ms[c]
        tl = str(self.inv.cards[c]['Type Line']).split(' // ')[0].lower()
        types = {w for w in ('artifact', 'creature', 'enchantment', 'instant', 'sorcery', 'planeswalker', 'land', 'battle') if w in tl}
        if 'lesson' in tl: types.add('lesson')
        self.fire('cast', spell_types=types)
        if types & {'instant', 'sorcery'}:
            done = False
            for a in rec['abilities']:
                if a['kind'] == 'spell' and a['outputs'] and not done:
                    self.resolve(a['outputs'], None); done = True
            if md.draw_once and not any(o[0] == 'draw' for a in rec['abilities'] for o in a['outputs']): self.draw(md.draw_once)
            return True
        r = self.inv.cards[c]
        subs = set(str(r['Type Line']).split(' // ')[0].lower().split('—')[-1].split()) if '—' in str(r['Type Line']) else set()
        o = self.new(c, types=types, power=_num(r['Power']), tough=_num(r['Toughness']), kw=rec['statics']['keywords'],
                     abil=rec['abilities'], st=rec['statics'], cmd=c in self.state.commanders, model=md, subtypes=subs)
        if rec['statics'].get('haste'): o.kw.add('haste')
        if md.fetch: self.lands.append({'colors': set(self.state.ci) or {'C'}, 'ready': self.t + 1, 'tapped': False})
        if md.mana_once and md.mana: self.new('token:treasure', types={'artifact'}, token=True, mana_sac=True)
        self.fire('enter', o)
        return True

    # ------------------------------------------------------------ the turn
    def turn(self, t):
        self.t = t; self.spells_turn = 0; self.pump = 0; self.combat_no = 0; self.reserved = set()
        for o in self.bf: o.tapped = False; o.sick = False; o.crewed = False
        for l in self.lands: l['tapped'] = False
        self.fire('upkeep')
        self.draw(1)
        # land drop
        cands = [c for c in self.hand if self.ms[c].is_land]
        if cands:
            have = set().union(*[l['colors'] for l in self.lands]) if self.lands else set()
            c = min(cands, key=lambda c: (self.ms[c].land_tapped, -len(self.ms[c].land_colors - have), c))
            self.hand.remove(c); md = self.ms[c]
            self.lands.append({'colors': set(md.land_colors), 'ready': t + (1 if md.land_tapped else 0), 'tapped': False})
            self.fire('landfall')
        self.fire('main_phase')
        self.mana_start = len(self.mana_units(True))
        self.ledger_start()
        body_mana = self.policy == 'mana_first'
        if self.policy == 'station_first': self.do_station()
        self.main(body_mana)
        self.crew()
        self.combat()
        if self.policy == 'mana_first':
            self.main(True); self.do_station()
        else:
            self.do_station(); self.main(True); self.do_station()
        self.activations()
        self.fire('end_step')
        self.cleanup()
        self.ledger_end()
        self.opponents_turns()

    def cleanup(self):
        """Discard to seven unless something says you have no maximum hand size; extra lands go first."""
        if any('no maximum hand size' in a.get('line', '') or 'no maximum hand size' in str(self.inv.cards[o.name]['Oracle Text']).lower()
               for o in self.bf if not o.token for a in o.abil[:1] or [{}]):
            return
        while len(self.hand) > 7:
            c = max(self.hand, key=lambda c: (self.ms[c].is_land and len(self.lands) >= 6, self.ms[c].mv_generic + len(self.ms[c].req)))
            self.hand.remove(c); self.note('discarded')

    def main(self, allow_bodies):
        ms = self.ms
        def order(c):
            md = ms[c]
            ramp = bool(md.mana or md.fetch) and not md.is_land
            held = self.held(c)
            return (not ramp, c not in self.cmd_zone, held, not md.draw_once, -(md.mv_generic + len(md.req)), c)
        progress = True
        while progress:
            progress = False
            for c in sorted([c for c in self.hand if not ms[c].is_land and not self.held(c)] + list(self.cmd_zone), key=order):
                if (c in self.hand or c in self.cmd_zone) and self.cast(c, allow_bodies): progress = True; break

    def held(self, c):
        md = self.ms[c]
        return md.held

    def crew(self):
        for v in [o for o in self.bf if o.st.get('crew') and not o.crewed]:
            need = v.st['crew']
            pool = sorted([b for b in self.creatures() if not b.tapped and b is not v], key=lambda b: (not b.sick, self.pw(b)))
            # attack_first crews only with bodies that cannot attack, unless the vehicle hits harder than they do
            got, use = 0, []
            for b in pool:
                if got >= need: break
                if self.policy == 'attack_first' and self.can_attack(b) and not b.sick and v.power <= self.pw(b): continue
                use.append(b); got += self.pw(b)
            if got >= need:
                for b in use: self.spend(b); b.tapped = True
                v.crewed = True; v.sick = False
                self.note('body:crew', len(use))

    def blockers(self):
        """Named 'blockers' scenario (ASSUMPTION): the defending opponent has (t-1)//2 ground 2/3 blockers
        (1 on T3, 2 on T5, 4 on T9) and one flying blocker from T7; each blocks one attacker, biggest first.
        Set for spread across all 12 decks (the earlier t-2 version left 10 of 12 decks at 0 damage), not from any outcome."""
        if not self.sc.get('blockers'): return 0, 0
        g = max(0, (self.t - 1) // 2); return g, (1 if self.t >= 7 else 0)

    def combat(self):
        att = [o for o in self.creatures() if self.can_attack(o)]
        if not att: return
        gb, fb = self.blockers()
        evasive = lambda o: bool({'flying', 'menace'} & o.kw) or any(lv['keywords'] & {'flying'} and o.charge >= lv['at'] for lv in o.st.get('station_levels', []))
        if gb and len(att) <= gb + fb:  # not enough attackers to get through: keep back those a 2/3 blocker would kill
            att = [o for o in att if evasive(o) or o.tough + o.counters > 2]
            if not att: return
        self.combat_no += 1
        self.fire('attack')
        for o in att:
            if not self.vigilant(o): o.tapped = True
            self.fire('attack', o)
        blocked = set()
        if gb or fb:
            ground = sorted([o for o in att if not evasive(o)], key=lambda o: -self.pw(o))
            air = sorted([o for o in att if evasive(o)], key=lambda o: -self.pw(o))
            for o in ground[:gb]: blocked.add(o.id)
            for o in (air + ground[gb:])[:fb]: blocked.add(o.id)
        dealt = 0
        for o in att:
            if o.id in blocked:
                if o.tough + o.counters <= 2 and 'indestructible' not in o.kw: self.leave(o, dies=True); self.note('blocked_died')
                continue
            p = self.pw(o)
            if p > 0:
                dealt += p
                self.fire('combat_damage', o)
        self.dmg += dealt; self.note('combat', dealt); self.note('body:attack', len(att))

    def do_station(self):
        for sp in sorted([o for o in self.bf if o.st.get('station') and o.charge < o.st['station']], key=lambda o: o.st['station'] - o.charge):
            while sp.charge < sp.st['station']:
                pool = [b for b in self.creatures() if not b.tapped and b is not sp and self.pw(b) > 0 and b.id not in self.reserved]
                if self.policy == 'attack_first' and self._precombat():
                    pool = [b for b in pool if not self.can_attack(b)]
                if not pool: break
                b = max(pool, key=self.pw); self.spend(b); b.tapped = True; sp.charge += self.pw(b)
                self.note('body:station'); self.note('charge', self.pw(b))
            if sp.charge >= sp.st['station'] and sp.name not in self.station_done: self.station_done[sp.name] = self.t

    def _precombat(self):
        return self.combat_no == 0

    def activations(self):
        """Main-2 activated abilities with leftover resources: token makers, card draw (non-body costs first)."""
        for o in list(self.bf):
            for a in o.abil:
                if a['kind'] != 'activated' or o not in self.bf: continue
                outs = a['outputs']
                if not outs or any(x[0] in ('mana', 'life', 'untap_self', 'evasion', 'interaction', 'removal') for x in outs): continue
                c = a['cost'] or {}
                if c.get('tap_self') and (o.tapped or (self.is_creature(o) and o.sick)): continue
                if a['gates'].get('sorcery') is False and False: continue
                fodder = []
                if c.get('sac'):
                    f = c['sac']['filter']
                    pool = [b for b in self.bf if b is not o and (f in b.types or f in b.subtypes or f == 'permanent') and (b.tapped or not self.is_creature(b))]
                    if len(pool) < c['sac']['n']: continue
                    fodder = pool[:c['sac']['n']]
                if c.get('tap_other') and not self.pay_tap_other(c['tap_other'], optional=True): continue
                g, req = c.get('mana', (0, []))
                if (g or req) and not self.pay(g, req, True, o.name): continue
                if c.get('tap_self'): o.tapped = True
                for b in fodder: self.leave(b, sacrificed=True)
                if c.get('sac_self'): self.leave(o, sacrificed=True)
                self.note(f'activate:{o.name}')
                self.resolve(outs, o)

    def opponents_turns(self):
        """Leftover mana on opponents' turns: held instants (counters, removal, protection) as if a target exists."""
        for c in sorted([c for c in self.hand if self.held(c) and 'Instant' in str(self.inv.cards[c]['Type Line'])], key=lambda c: self.ms[c].mv_generic):
            if c in self.hand: self.cast(c, True)
        sc = self.sc
        if sc.get('wipe') and sc['wipe'][0] == self.t: self.wipe(sc['wipe'][1])
        if self.t in sc.get('remove_commander', ()):
            for o in [o for o in self.bf if o.cmd]: self.leave(o, dies=True); self.note('commander_removed')
        # sorcery-speed interaction is cast in main 2 by main(True) only if not held; held sorceries use leftover here as an approximation
        for c in sorted([c for c in self.hand if self.held(c) and 'Sorcery' in str(self.inv.cards[c]['Type Line'])], key=lambda c: self.ms[c].mv_generic):
            if c in self.hand and self.t >= 3: self.cast(c, True)

    def wipe(self, kind):
        for o in list(self.bf):
            if kind in ('destroy', 'exile') and self.is_creature(o):
                if kind == 'destroy' and 'indestructible' in o.kw: continue
                self.leave(o, dies=(kind == 'destroy'))
            elif kind == 'bounce' and not ('land' in o.types):
                self.leave(o)
                if not o.token and not o.cmd: self.hand.append(o.name)
        self.note('wiped')

    # ------------------------------------------------------------ ledger
    def ledger_start(self):
        bodies = self.creatures()
        self.note('supply:bodies', len(bodies))
        self.note('supply:attack_ready', sum(self.can_attack(b) for b in bodies))
        self.note('supply:power', sum(self.pw(b) for b in bodies))
        self.note('supply:artifacts', sum('artifact' in o.types for o in self.bf))
        need_station = sum(max(0, o.st['station'] - o.charge) for o in self.bf if o.st.get('station'))
        uncrewed = sum(1 for o in self.bf if o.st.get('crew'))
        castable_blocked = 0
        contested = 0
        for b in bodies:
            uses = 0
            if self.can_attack(b): uses += 1
            if need_station: uses += 1
            if uncrewed: uses += 1
            if b.mana_sac and not b.sick: uses += 1
            contested += uses >= 2
        self.note('supply:contested', contested)
        self.note('claim:station', need_station)

    def ledger_end(self):
        bodies = self.creatures()
        self.note('end:idle', sum(1 for b in bodies if not b.tapped))
        self.note('end:station_unmet', sum(max(0, o.st['station'] - o.charge) for o in self.bf if o.st.get('station')))
        # mana-limited: non-interaction spells wait in hand and the mana left (bodies included) cannot pay the cheapest
        waiting = [self.cost_of(c) for c in self.hand if not self.ms[c].is_land and not self.held(c)]
        left = len(self.mana_units(True))
        self.note('end:hand_spells', len(waiting))
        self.note('end:mana_short', 1 if waiting and left < min(g + len(r) for g, r in waiting) else 0)
        self.note('board:power', sum(self.pw(b) for b in bodies))
        self.note('board:bodies', len(bodies))
        self.note('cum:combat', self.dmg); self.note('cum:drain', self.drain); self.note('cum:reach', self.reach)
        self.note('cum:drawn', self.drawn)
        if self.dmg + self.drain >= 40 and not self.m.get('lethal'): self.m['lethal'] = self.t


def prepare(state):
    ms = A._models(state)
    recs = {c: card_record(state.inv, c) for c in ms if c != A.BLANK}
    return {'models': ms, 'records': recs}


def run(state, games=1000, turns=10, seed=20261018, policy='attack_first', scenario=None, prepared=None):
    """Returns {'mean': {'key@T': mean}, 'per_game': [metrics dicts], 'lethal': [...]}. Common random
    numbers: game g uses the same shuffle under every policy and scenario."""
    ev = prepared or prepare(state)
    per = []
    for g in range(games):
        rng = random.Random(seed * 1000003 + g)
        G = Game(ev, state, rng, policy, scenario)
        for t in range(1, turns + 1): G.turn(t)
        G.m['station_done'] = dict(G.station_done)
        per.append(G.m)
    keys = {k for m in per for k in m if '@' in k}
    mean = {k: sum(m.get(k, 0) for m in per) / games for k in keys}
    return {'mean': mean, 'per_game': per, 'games': games, 'turns': turns, 'policy': policy, 'scenario': scenario or {}}


def series(res, key, turns=None):
    T = turns or res['turns']
    return [round(res['mean'].get(f'{key}@{t}', 0.0), 2) for t in range(1, T + 1)]


def lethal_by(res, t):
    return sum(1 for m in res['per_game'] if m.get('lethal') and m['lethal'] <= t) / res['games']


def paired(a, b, key, t):
    """Mean paired difference b - a of a per-game value at turn t (same shuffles), with its standard error."""
    d = [y.get(f'{key}@{t}', 0) - x.get(f'{key}@{t}', 0) for x, y in zip(a['per_game'], b['per_game'])]
    n = len(d); m = sum(d) / n
    se = (sum((v - m) ** 2 for v in d) / max(1, n - 1) / n) ** 0.5
    return m, se
