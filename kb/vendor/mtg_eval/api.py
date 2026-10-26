"""One entry point for every evaluation question.

    ev = Evaluator('export.xlsx')
    ev.card('Altered Ego')                      ev.deck('Vraska')
    ev.module('TMNT', 'go_wide')                ev.compare('TMNT', [('Crustacean Commando', 'Knockout Maneuver')])
    ev.upgrades('Sharuum', protect_decks=['Dina'])
    ev.build('Balmor, Battlemage Captain')      ev.inventory()
    ev.transfer('Cauldron of Essence', 'Dina', 'Necrobloom')
    ev.portfolio('Duty Beyond Death')

Every query reads the same Inventory and the same card record. Each returns a Result:
a summary, sections, what is uncertain, what is not modelled, and whether the answer is
conclusive. A partial understanding never blocks an answer; it blocks a claim of certainty.
"""
import statistics
from . import access as A
from . import deckeval as D
from . import structure as S
from . import scenarios as SC
from . import routing as RT
from . import engine as EN
from .cuts import audit_cut, audit_deck
from .inventory import Inventory, BASICS, COLORS, ci_set
from .semantics import clause_audit, understood, recursion_types, clauses, wipe_kind, THREATS

VITAL = ['ramp', 'draw', 'spot_removal', 'wipe', 'protection', 'recursion', 'closer']
TYPED = ['protection:team', 'protection:anti_wipe', 'protection:all_creatures', 'counterspell', 'fixing', 'counter_preservation']
EXTRA_TARGETS = {'protection:anti_wipe': 2, 'counterspell': None}  # ASSUMPTION, like TARGETS
LIMITS = [
    'No opponents: no removal of your pieces, no counterspells, no combat; wipes appear only in named scenarios.',
    'The goldfish deploys creatures, token makers, ramp and draw; most noncreature engines are not cast.',
    'Repeatable effects count as one source; their cadence and magnitude are not priced.',
    'Mana is measured as if all of it can go to the role in question (no competition between spells). Competition for untapped bodies and artifacts is counted in the resource ledger, not simulated.',
    'Coverage targets are casual-Commander heuristics (ASSUMPTION), not calibrated power.',
]


class Result(dict):
    """title, summary[list], sections[list of (heading, str | list[str] | list[dict])],
    uncertainty[list], limitations[list], conclusive (bool, reason), data{}"""
    def __init__(self, title, **kw):
        super().__init__(title=title, summary=[], sections=[], uncertainty=[], limitations=[], conclusive=(False, ''), data={})
        self.update(kw)

    def add(self, heading, content):
        self['sections'].append((heading, content)); return self


def pct(p):
    return f'{100 * p:.1f}%'


def pts(d):
    return f'{100 * d:+.1f}'


class Evaluator:
    def __init__(self, workbook, games=5000, seed=20261018, engine_games=300):
        self.inv = Inventory(workbook)
        self.games, self.seed, self.engine_games = games, seed, engine_games
        self._profiles = {}

    # ================================================================ turn engine (0.3.0)
    def _profile(self, st):
        key = (st.deck, tuple(st.swaps), self.engine_games)
        if key not in self._profiles:
            self._profiles[key] = SC.profile(st, games=self.engine_games, seed=self.seed)
        return self._profiles[key]

    def _engine_sections(self, res, st):
        P = self._profile(st); sm = SC.summary(P); R = P['runs']; T = P['turns']
        cov = SC.coverage(st, P['prepared'])
        cards = sorted({c for c in set(st.library) | set(st.commanders) if not self.inv.is_land(c)})
        routes = RT.classify(self.inv, cards)
        cl, th, rs, cm = sm['closing'], sm['throughput'], sm['resilience'], sm['commander']
        bn = SC.bottlenecks(R['attack_first'])
        late = [b['most frequent'] for b in bn[-3:]]
        res['summary'] += [
            f"Engine (light blockers): median damage by T10 {cl['light blockers damage by T10 (median)']:.0f}; unopposed goldfish lethal by T10 {pct(cl['unopposed lethal by T10'])} (upper bound)",
            f"Most frequent bottleneck T6-T8: {max(set(late), key=late.count)}",
            f"After a T{SC.WIPE_TURN} destroy wipe: median board power {rs['wipe_destroy']['power before (median)']:.0f} before, {rs['wipe_destroy']['power 3 turns after (median)']:.0f} three turns later",
            f"Without the commander: damage by T10 {cm['damage by T10 change without commander (paired)'][0]:+.1f} (paired); typed coverage {cov['fully typed']} of {cov['cards']} nonland cards fully read"]
        rrows = []
        for k in ('parallel producers', 'replacement amplification', 'scaling', 'bounded feedback', 'unbounded feedback', 'resource-quality feedback'):
            for r in routes[k]: rrows.append({'class': k, 'detail': '; '.join(f'{a}: {b}' if not isinstance(b, list) else f'{a}: {", ".join(b)}' for a, b in r.items())})
        rrows += [{'class': 'linear payoff', 'detail': f"{r['payoff']} -> {r['output']} (fed by {r['fed by']}){' once per turn' if r['cap'] else ''}"} for r in routes['linear payoffs'][:14]]
        rrows += [{'class': 'feed-forward chain', 'detail': r['chain']} for r in routes['feed-forward chains'][:6]]
        res.add('Engine routes (typed events; cast, enter and create are separate hooks)', rrows or ['No routes read.'])
        res.add(f'Resource ledger (light blockers, attack first; mean per game, {P["games"]} games)', SC.ledger_rows(R['attack_first']))
        res.add('Bottlenecks by turn (share of games)', bn)
        res.add('Who gets a contested body: three policies (light blockers, same shuffles)', [{'policy': p, 'damage by T10 (median)': f"{v['damage by T10 (median)']:.0f}",
                'station charge by T10 (mean)': f"{v['station charge by T10']:.1f}", 'cards by T10 (mean)': f"{v['cards by T10']:.1f}",
                'damage vs attack first (paired mean)': f"{v['vs attack_first damage (paired)'][0]:+.1f} (SE {v['vs attack_first damage (paired)'][1]:.1f})"} for p, v in sm['policies'].items()])
        res.add('Closing (conditional; see assumptions)', [{'measure': 'unopposed goldfish conditional lethal by T8 / T10', 'value': f"{pct(cl['unopposed lethal by T8'])} / {pct(cl['unopposed lethal by T10'])}"},
                {'measure': 'light blockers: lethal by T10', 'value': pct(cl['light blockers lethal by T10'])},
                {'measure': 'light blockers: median damage by T8 / T10', 'value': f"{cl['light blockers damage by T8 (median)']:.0f} / {cl['light blockers damage by T10 (median)']:.0f}"},
                {'measure': 'tokens per turn T4-T8 (mean)', 'value': f"{th['tokens per turn T4-T8']:.2f}"},
                {'measure': 'cards drawn by T8 (mean, incl. normal draws)', 'value': f"{th['cards drawn by T8']:.1f}"},
                {'measure': 'board at end of T8 (median bodies / power)', 'value': f"{th['bodies end T8 (median)']:.0f} / {th['board power end T8 (median)']:.0f}"},
                {'measure': 'power per body at end of T8 (median)', 'value': f"{th['power per body end T8 (median)']:.2f}"}])
        res.add('Resilience scenarios (light blockers; paired with the same shuffles)', [
                {'scenario': f'destroy wipe after T{SC.WIPE_TURN}', 'board power before -> 3 turns after (median)': f"{rs['wipe_destroy']['power before (median)']:.0f} -> {rs['wipe_destroy']['power 3 turns after (median)']:.0f}",
                 'damage by T10 change': f"{rs['wipe_destroy']['damage by T10 change (paired)'][0]:+.1f} (SE {rs['wipe_destroy']['damage by T10 change (paired)'][1]:.1f})"},
                {'scenario': f'exile wipe after T{SC.WIPE_TURN}', 'board power before -> 3 turns after (median)': f"{rs['wipe_exile']['power before (median)']:.0f} -> {rs['wipe_exile']['power 3 turns after (median)']:.0f}",
                 'damage by T10 change': f"{rs['wipe_exile']['damage by T10 change (paired)'][0]:+.1f} (SE {rs['wipe_exile']['damage by T10 change (paired)'][1]:.1f})"},
                {'scenario': f'commander removed after T{SC.REMOVE_AT[0]} and T{SC.REMOVE_AT[1]} (recast with tax)', 'board power before -> 3 turns after (median)': f"commander casts by T10: {cm['casts by T10 when removed on T5 and T7']:.2f}",
                 'damage by T10 change': f"{cm['damage by T10 change when removed (paired)'][0]:+.1f} (SE {cm['damage by T10 change when removed (paired)'][1]:.1f})"},
                {'scenario': f'attrition: destroy wipe after T{SC.WIPE_TURN}, then commander removed after T7, T8 and T9', 'board power before -> 3 turns after (median)': f"{rs['attrition']['power before (median)']:.0f} -> {rs['attrition']['power 3 turns after (median)']:.0f}; commander casts T7-T10 {rs['attrition']['commander casts T7-T10']:.2f}",
                 'damage by T10 change': f"{rs['attrition']['damage by T10 change (paired)'][0]:+.1f} (SE {rs['attrition']['damage by T10 change (paired)'][1]:.1f})"},
                {'scenario': 'no commander (ablation)', 'board power before -> 3 turns after (median)': f"tokens per turn T4-T8: {cm['tokens per turn T4-T8 with']:.2f} -> {cm['tokens per turn T4-T8 without commander']:.2f}",
                 'damage by T10 change': f"{cm['damage by T10 change without commander (paired)'][0]:+.1f} (SE {cm['damage by T10 change without commander (paired)'][1]:.1f})"}])
        res.add('Engine coverage (what the turn engine reads)', [{'card': c, 'not read': '; '.join(u)[:160]} for c, u in sorted(cov['partly typed'].items()) if u][:40]
                or ['Every nonland card is fully typed.'])
        res['uncertainty'].append(f"Turn engine: {cov['fully typed']} of {cov['cards']} nonland cards are fully typed; the rest act only through the parts that were read (see Engine coverage). Sampling error is separate from this coverage error.")
        res['limitations'] = list(res['limitations']) + EN.ASSUMPTIONS + ['Light blockers (ASSUMPTION): the defending opponent has (turn-1)/2 ground 2/3 blockers and one flier from T7, each blocking one attacker; it is a stress test, not an opponent model.']
        res['data']['engine'] = {'summary': sm, 'coverage': {'fully typed': cov['fully typed'], 'cards': cov['cards']}}
        return sm

    # ================================================================ shared pieces
    def _state(self, deck, swaps=()):
        return A.DeckState(self.inv, deck, list(swaps))

    def _resolve_deck(self, deck):
        d = self.inv.find(deck)
        if d not in self.inv.decks: raise KeyError(f'{deck!r} is not a current deck. Decks: ' + ', '.join(sorted(self.inv.decks)))
        return d

    def _card(self, name):
        n = self.inv.find(name)
        if n not in self.inv.cards: raise KeyError(f'{name!r} is not in the Collection')
        return n

    def _access(self, st, windows=(5, 7)):
        ra = A.role_access(st, windows)
        out = {}
        for r in VITAL + TYPED:
            v = ra.get(r, {})
            out[r] = {'k': v.get('k', 0), **{f'T{t}': v.get(f'P_seen_T{t}', 0.0) for t in windows},
                      'upper_T7': v.get('P_seen_T7_upper', v.get('P_seen_T7', 0.0)), 'unknown_sources': v.get('unknown_sources', []),
                      'sources': v.get('sources', [])}
        return out

    def _targets(self, st):
        t = dict(D.TARGETS); t.update({k: v for k, v in EXTRA_TARGETS.items() if v})
        t['fixing'] = 0 if len(st.ci) < 2 else 6 * (len(st.ci) - 1)
        return t

    def _weakest(self, st, acc, n=3):
        """Gap = access a deck at its target count would have, minus the access it has (seen by T7)."""
        N = len(st.library); seen = A.seen(7); rows = []
        for r, t in self._targets(st).items():
            if not t or r not in acc or r == 'fixing': continue  # fixing is judged by the goldfish color rates, since lands count
            want = A.p_any(N, seen, t); have = acc[r]['T7']
            rows.append({'area': r, 'sources': acc[r]['k'], 'target (ASSUMPTION)': t, 'seen by T7': pct(have),
                         'at target': pct(want), 'gap (points)': round(100 * (want - have), 1), 'gap': round(want - have, 4)})
        rows.sort(key=lambda x: (-x['gap'], x['sources']))
        return [x for x in rows if x['gap'] > 0][:n], rows

    def _goldfish_rows(self, st, games, role_sets=None):
        """Per game, per turn: mana, colors, commander, and 'available' (on the battlefield or castable) per role set."""
        rows = {}; cmds = st.commanders; ci = sorted(st.ci); role_sets = role_sets or {}
        def obs(g, t, info):
            us = info['units_start']; ms = info['models']
            r = {'mana3': len(us) >= 3, 'mana4': len(us) >= 4, 'mana5': len(us) >= 5,
                 'colors': A.can_pay(us, 0, [{c} for c in ci]) is not None,
                 'commander': all(c in info['bf'] for c in cmds)}
            for k, names in role_sets.items():
                r['avail:' + k] = bool(info['bf'] & names) or any(c in names and A.can_pay(us, ms[c].mv_generic, ms[c].req) is not None for c in info['hand'])
            rows.setdefault(g, {})[t] = r
        A.goldfish(st, games, seed=self.seed, observer=obs, cast_commander=True)
        return rows

    @staticmethod
    def _by(rows, key, t):
        return sum(1 for g in rows.values() if any(g[u][key] for u in range(1, t + 1))) / len(rows)

    @staticmethod
    def _at(rows, key, t):
        return sum(1 for g in rows.values() if g[t][key]) / len(rows)

    @staticmethod
    def _paired(r0, r1, key, t, by=False):
        f = (lambda g: any(g[u][key] for u in range(1, t + 1))) if by else (lambda g: g[t][key])
        d = [int(f(r1[g])) - int(f(r0[g])) for g in r0]
        n = len(d); m = sum(d) / n
        se = (sum((x - m) ** 2 for x in d) / (n - 1) / n) ** 0.5 if n > 1 else 0
        return m, se

    def _custody(self, uses, returns):
        rows = []
        for c in sorted(set(uses) | set(returns)):
            fr = self.inv.free(c); own = self.inv.owned(c); after = fr - uses.get(c, 0) + returns.get(c, 0)
            rows.append({'card': c, 'owned': own if c not in BASICS else 'basic', 'free before': fr if c not in BASICS else '-',
                         'free after': after if c not in BASICS else '-', 'now in': ', '.join(self.inv.holders(c)) or '-',
                         'conserved': 'yes' if c in BASICS or 0 <= after <= own else 'NO'})
        return rows

    def _understanding(self, name):
        rows = clause_audit(self.inv.cards[name]['Oracle Text'], name)
        level, gaps = understood(rows)
        unknown = sorted(f for f, v in self.inv.record(name).items() if v['status'] in ('tag_only', 'contradicted'))
        if unknown and level == 'complete': level = 'partial'
        return level, gaps, unknown

    def _role_sets(self, st, roles):
        r = A.roles(self.inv, st.library)
        return {k: {st.library[i] for i in r.get(k, set())} for k in roles}

    # ================================================================ 1. card
    def card(self, name, deck=None):
        inv = self.inv; n = self._card(name); r = inv.cards[n]
        level, gaps, unknown = self._understanding(n)
        res = Result(f'Card: {n}')
        res['summary'] = [f"{r['Mana Cost'] if str(r['Mana Cost']) != 'nan' else ''} {r['Type Line']}".strip(),
                          f"Functions the evaluator counts: {', '.join(sorted(inv.supported(n) - {'creature', 'instant_sorcery', 'land'})) or 'none'}",
                          f"Understanding: {level}" + (f" ({len(gaps)} clause(s) not priced)" if gaps else ''),
                          f"Custody: {inv.owned(n)} owned, {inv.free(n)} free, in {', '.join(inv.holders(n)) or 'no deck'}"]
        res.add('Oracle text (stored in inventory)', str(r['Oracle Text']))
        res.add('Capability record (evidence per function)', [{'function': f, 'status': v['status'],
                'oracle rule': v['evidence'].get('oracle', ''), 'inventory tag': 'yes' if v['evidence'].get('tag') else '',
                'hand label': {True: 'yes', False: 'no'}.get(v['evidence'].get('label'), '')} for f, v in sorted(inv.record(n).items())])
        res.add('Clause audit', [{'clause': a['clause'][:100], 'status': a['status'], 'functions': ', '.join(a.get('functions', [])),
                                  'not priced': '; '.join(a.get('features', []))} for a in clause_audit(r['Oracle Text'], n)])
        t = A.text(inv, n)
        typed = []
        for p in A.protection_profile(t): typed.append({'reading': 'protection', 'detail': f"{p['effect']} for {p['scope']}; survives {', '.join(p['survives']) or 'no wipe'}"})
        for p in recursion_types(clauses(r['Oracle Text'], n)): typed.append({'reading': 'recursion', 'detail': f"to {p['destination']}, {p['referent']}, {p['cadence']}"})
        wk = wipe_kind(t) if 'wipe' in inv.supported(n) else set()
        if wk: typed.append({'reading': 'wipe', 'detail': ', '.join(sorted(wk)) + '; answers ' + ', '.join(th for th, ks in THREATS.items() if wk & ks)})
        if typed: res.add('Typed readings', typed)
        if deck:
            d = self._resolve_deck(deck); st = self._state(d)
            if n in st.library:
                a = audit_cut(st, n)
                res.add(f'As a cut from {d}', [f"Label: {a['label']}", *(f'Flag: {x}' for x in a['coarse_flags']), *(f'Blocker: {x}' for x in a['audit_blockers']),
                                               'Access change if removed (seen by T7): ' + (', '.join(f'{k} {pts(v)}' for k, v in {**a['role_delta'], **a['module_delta']}.items()) or 'none')])
            else:
                res.add(f'Fit in {d}', self._fit_rows(n, [d]))
        else:
            res.add('Band-level fit in each current deck (pre-kernel check)', [{'deck': x['deck'], 'verdict': x['verdict'], 'gains': '; '.join(x.get('gains', [])),
                    'losses': '; '.join(x.get('losses', [])), 'note': x.get('reason', '')} for x in D.card_destinations(inv, n)['destinations']])
        if gaps: res['uncertainty'] += [f"Not priced: \"{g['clause'][:90]}\"" + (f" ({'; '.join(g['features'])})" if g.get('features') else '') for g in gaps]
        if unknown: res['uncertainty'].append('Inventory tag or hand label not confirmed by the rules: ' + ', '.join(unknown))
        res['limitations'] = ['Card text is the inventory\'s stored Oracle text, not freshly verified.'] + LIMITS[2:3]
        res['conclusive'] = (level == 'complete', 'every clause is priced' if level == 'complete' else 'some abilities are not priced, so any comparison involving this card is indicative')
        return res

    def _fit_rows(self, n, decks):
        rows = []
        for d in decks:
            ok, why = self.inv.legal_in(n, self.inv.deck_ci(d))
            if not ok: rows.append({'deck': d, 'fit': 'not legal', 'detail': why}); continue
            st = self._state(d); by = audit_deck(st)
            cut = (by.get('mechanically_audited_cut') or by.get('human_review_required') or [None])[0]
            if not cut: rows.append({'deck': d, 'fit': 'no screened cut', 'detail': ''}); continue
            a0 = self._access(st, (7,)); a1 = self._access(self._state(d, [(cut['card'], n)]), (7,))
            ch = {k: a1[k]['T7'] - a0[k]['T7'] for k in a0 if a1[k]['T7'] != a0[k]['T7']}
            rows.append({'deck': d, 'fit': 'legal', 'cut': f"{cut['card']} ({cut['label']})", 'access change by T7': ', '.join(f'{k} {pts(v)}' for k, v in ch.items()) or 'none'})
        return rows

    # ================================================================ 2. deck
    def deck(self, name, games=None):
        inv = self.inv; d = self._resolve_deck(name); st = self._state(d); games = games or self.games
        ms = A._models(st); nonland = [c for c in st.library if not ms[c].is_land]
        mv = [float(inv.cards[c]['Mana Value'] or 0) for c in nonland]
        curve = {}
        for m in mv: k = '7+' if m >= 7 else str(int(m)); curve[k] = curve.get(k, 0) + 1
        acc = self._access(st, (3, 5, 7, 10)); assess = D.deck_assessment(inv, d)
        weak, allgaps = self._weakest(st, acc)
        rows = self._goldfish_rows(st, games)
        sm = self._structure(); mine = sm[d]; fl = S.flags(mine)
        res = Result(f'Deck: {d}')
        res['summary'] = [f"{' + '.join(st.commanders)} ({''.join(c for c in COLORS if c in st.ci)}), {st.size} cards" + (f", companion {', '.join(st.companion)}" if st.companion else ''),
                          f"Lands {len(st.library) - len(nonland)}, nonland {len(nonland)} (creatures {sum(ms[c].creature for c in nonland)}), average nonland mana value {statistics.mean(mv):.2f}",
                          f"Mana (goldfish, on the draw): 4 by T4 {pct(self._at(rows, 'mana4', 4))}, all colors by T5 {pct(self._at(rows, 'colors', 5))}, commander out by T4 {pct(self._by(rows, 'commander', 4))} / T6 {pct(self._by(rows, 'commander', 6))}",
                          'Weakest areas (seen by T7 vs target): ' + ', '.join(f"{w['area']} {w['seen by T7']} ({w['sources']} cards)" for w in weak),
                          'Count screen (post-hoc): ' + ('; '.join(f[0] for f in fl) if fl else f'none (of the checks run on all {len(sm)} decks)')]
        res.add('Count screen (0.2.0; thresholds set after the Vraska game, so not evidence of prediction)', [{'flag': f, 'evidence': e} for f, e in fl] or ['None raised.'])
        res.add(f'Structure compared with the other {len(sm) - 1} decks', self._structure_rows(d, sm))
        res.add('Shared-resource claims by card (count; the turn-engine ledger below measures what happens)', [{'card': r['card'], 'claim': r['kind'], 'amount': r['amount'], 'unit': r['unit']} for r in mine['ledger']] or ['No shared-resource claims read.'])
        res.add('Commander dependence', [{'commander': x['commander'], 'engine': 'yes' if x['engine'] else 'no', 'makes': ', '.join(x['makes']) or '-',
                                          'spells that feed it': x['spells that feed it'] if x['spells that feed it'] is not None else '-',
                                          'other makers of that family': x['other makers of that family'], 'protection that can cover it': ', '.join(x['protection that can cover it']) or 'none'} for x in mine['commander']])
        res.add('Curve (nonland mana value)', [{'MV': k, 'cards': curve[k]} for k in sorted(curve, key=lambda x: (len(x), x))])
        res.add('Coverage bands (pre-kernel, counts vs ASSUMED targets)', [{'function': f, 'cards': v['count'], 'target': v['target'], 'band': v['band_name']} for f, v in assess['coverage'].items()])
        res.add('Draw access (exact, on the draw)', [{'role': r, 'cards': v['k'], 'T3': pct(v['T3']), 'T5': pct(v['T5']), 'T7': pct(v['T7']), 'T10': pct(v['T10']),
                                                      'T7 if unconfirmed tags were true': pct(v['upper_T7'])} for r, v in acc.items() if v['k'] or r in VITAL])
        res.add('Gap to target (seen by T7)', [{k: v for k, v in g.items() if k != 'gap'} for g in allgaps])
        wipes = [c for c in set(st.library) if 'wipe' in inv.supported(c)]
        res.add('Typed answers', [{'card': c, 'kind': ', '.join(sorted(A.wipe_kind(inv, c))), 'answers': ', '.join(th for th, ks in THREATS.items() if A.wipe_kind(inv, c) & ks)} for c in sorted(wipes)] or ['No mass removal.'])
        prot = []
        for c in sorted(set(st.library) | set(st.commanders)):
            for p in A.protection_profile(A.text(inv, c)): prot.append({'card': c, 'effect': p['effect'], 'scope': p['scope'], 'survives': ', '.join(p['survives']) or '-'})
        res.add('Typed protection', prot or ['No protection read.'])
        rec = []
        for c in sorted(set(st.library)):
            for p in recursion_types(clauses(inv.cards[c]['Oracle Text'], c)): rec.append({'card': c, 'to': p['destination'], 'referent': p['referent'], 'cadence': p['cadence']})
        res.add('Typed recursion', rec or ['No recursion read.'])
        mods = A.module_access(st, 7)
        res.add('Modules (formal draw access by T7; maturity by source counts)', [{'module': m, 'access T7': pct(mods[m]), 'maturity': v['maturity'],
                'source counts per group': '/'.join(map(str, v['group_counts'])), 'plan': 'yes' if m in assess['plan_modules'] else ''}
                for m, v in assess['modules'].items() if v['maturity'] != 'absent'])
        partial = []
        for c in sorted(set(nonland) | set(st.commanders)):
            lv, gaps, unk = self._understanding(c)
            if lv != 'complete': partial.append((c, gaps, unk))
        res.add('Cards the evaluator only partly understands', [{'card': c, 'not priced': '; '.join(sorted({f for g in gaps for f in g.get('features', [])} | ({'unparsed text'} if any(g['status'] == 'unparsed' for g in gaps) else set()))),
                                                                'unconfirmed tags': ', '.join(u)} for c, gaps, u in partial])
        res['uncertainty'] = [f'{len(partial)} of {len(set(nonland) | set(st.commanders))} distinct nonland cards (incl. commander) have abilities the evaluator does not price; their contribution is under-counted.',
                              f'Goldfish rates use {games} games; sampling error is about ±{100 * 0.5 / games ** 0.5 * 2:.1f} points (95%).']
        res['limitations'] = LIMITS
        res['conclusive'] = (False, 'a deck profile is descriptive; it does not rank this deck against others')
        res['data'] = {'access': acc, 'weakest': weak, 'modules': mods, 'structure_flags': [f for f, _ in fl]}
        if self.engine_games: self._engine_sections(res, st)
        return res

    def _structure(self):
        if not hasattr(self, '_sm'):
            self._sm = {d: S.measure(self.inv, self._state(d)) for d in sorted(self.inv.decks)}
        return self._sm

    def _structure_rows(self, d, sm):
        keys = [('tap claimants', lambda m: len(m['tap claimants']), 'high'),
                ('tap claimants per creature card', lambda m: round(m['claims per creature card'], 2), 'high'),
                ('station power needed', lambda m: m['station power'], 'high'),
                ('artifact-sacrifice claimants', lambda m: len(m['sacrifice claimants']), 'high'),
                ('creature cards', lambda m: m['closing']['creature cards'], 'low'),
                ('creatures with power 4+', lambda m: len(m['closing']['power 4+']), 'low'),
                ('lasting anthems', lambda m: len(m['closing']['lasting anthems']), 'low'),
                ('engines needing combat damage', lambda m: len(m['closing']['combat-damage engines']), 'high')]
        rows = []
        for label, f, bad in keys:
            vals = {k: f(m) for k, m in sm.items()}; v = vals[d]
            worse = sum((x > v) if bad == 'high' else (x < v) for x in vals.values())
            rows.append({'measure': label, 'this deck': v, 'range across decks': f'{min(vals.values())} to {max(vals.values())}',
                         'rank (1 = most exposed)': f'{worse + 1} of {len(vals)}'})
        return rows

    # ================================================================ 3. module
    def module(self, deck, module):
        inv = self.inv; d = self._resolve_deck(deck); st = self._state(d)
        if module not in D.MODULES: raise KeyError(f'module {module!r}; known: ' + ', '.join(D.MODULES))
        groups = D.MODULES[module]; r = A.roles(inv, st.library)
        cmd = set().union(*[inv.supported(c) for c in st.commanders])
        res = Result(f'Module: {module} in {d}')
        rows, gs = [], []
        for g in groups:
            anchored = bool(set(g) & cmd)
            pos = set().union(*[r.get(f, set()) for f in g])
            gs.append(None if anchored else pos)
            rows.append({'group (any of)': ' / '.join(g), 'commander supplies': 'yes' if anchored else '', 'library cards': len(pos),
                         'cards': ', '.join(sorted({st.library[i] for i in pos}))[:300]})
        N = len(st.library)
        acc = {t: A.p_all(N, A.seen(t), gs) for t in (5, 7, 10)}
        res['summary'] = [f"Every group has a card in hand or play (exact, commander groups count as met): T5 {pct(acc[5])}, T7 {pct(acc[7])}, T10 {pct(acc[10])}",
                          'This is formal access. It does not mean the pieces were cast, connected or survived.']
        res.add('Groups', rows)
        if any(c.startswith('Leonardo') for c in st.commanders) and module in ('go_wide', 'counters'):
            rec = {}
            def obs(g, t, info): rec.setdefault(g, {})[t] = {'leo': info['leo_on'], 'modA': info['modA']}
            A.goldfish(st, self.games, seed=self.seed, observer=obs)
            res.add('Operational layer (goldfish): Leonardo + a token entering the same turn', [{'by turn': f'T{t}', 'Leonardo cast': pct(self._by(rec, 'leo', t)),
                    'module online at least once': pct(self._by(rec, 'modA', t))} for t in (4, 5, 6, 7)])
        else:
            res['uncertainty'].append('No module-specific cast-and-connect model; the turn engine below reports what these cards actually did.')
        mcards = sorted({st.library[i] for g in groups for f in g for i in r.get(f, set())} | set(st.commanders))
        if self.engine_games:
            routes = RT.classify(inv, sorted({c for c in mcards if not inv.is_land(c)}))
            res.add('Engine routes among this module\'s cards', [{'class': k, 'detail': '; '.join(f'{a}: {b}' if not isinstance(b, list) else f'{a}: {len(b)}' for a, b in x.items())}
                                                                  for k, v in routes.items() for x in v[:8]] or ['No routes read among these cards.'])
            P = self._profile(st); b = P['runs']['attack_first']
            fired = []
            for c in mcards:
                row = {'card': c, **{f'T{t}': round(b['mean'].get(f'trigger:{c}@{t}', 0) + b['mean'].get(f'activate:{c}@{t}', 0), 2) for t in range(3, 9)}}
                if any(v for k, v in row.items() if k != 'card'): fired.append(row)
            res.add('Throughput: triggers and activations per turn by card (turn engine, light blockers, mean)', fired or ['None of these cards fired in the engine (their abilities may be outside what it reads).'])
            res['summary'].append('Throughput comes from the turn engine; operation is conditional on its assumptions (see Not modelled).')
        res['limitations'] = LIMITS[:3] + (EN.ASSUMPTIONS if self.engine_games else [])
        res['conclusive'] = (False, 'formal access is an upper bound on operation')
        return res

    # ================================================================ 4. compare substitutions
    def compare(self, deck, swaps, games=None):
        inv = self.inv; d = self._resolve_deck(deck); games = games or self.games
        swaps = [(self._card(o) if o else None, self._card(i) if i else None) for o, i in swaps]
        st0 = self._state(d); st1 = self._state(d, swaps)
        for o, i in swaps:
            if o and o not in st0.library: raise KeyError(f'{o} is not in {d}')
            if i and not inv.legal_in(i, st0.ci)[0]: raise KeyError(f'{i}: ' + inv.legal_in(i, st0.ci)[1])
        a0, a1 = self._access(st0), self._access(st1)
        m0, m1 = A.module_access(st0, 7), A.module_access(st1, 7)
        changed = [r for r in a0 if (a0[r]['k'], a0[r]['T7']) != (a1[r]['k'], a1[r]['T7'])]
        rs = {k: self._role_sets(st0, [k])[k] | self._role_sets(st1, [k])[k] for k in changed}
        r0 = self._goldfish_rows(st0, games, rs); r1 = self._goldfish_rows(st1, games, rs)
        res = Result(f"Compare in {d}: " + '; '.join(f'{o} -> {i}' for o, i in swaps))
        res.add('Draw access (exact)', [{'role': r, 'before': f"{a0[r]['k']} cards, T5 {pct(a0[r]['T5'])}, T7 {pct(a0[r]['T7'])}",
                                         'after': f"{a1[r]['k']} cards, T5 {pct(a1[r]['T5'])}, T7 {pct(a1[r]['T7'])}", 'change T7': pts(a1[r]['T7'] - a0[r]['T7'])} for r in changed] or ['No role access changes.'])
        res.add('Modules (formal access by T7)', [{'module': m, 'before': pct(m0[m]), 'after': pct(m1[m]), 'change': pts(m1[m] - m0[m])} for m in m0 if m0[m] != m1[m]] or ['No module access changes.'])
        gold = []
        for key, t, by, label in [('mana4', 4, False, '4 mana on T4'), ('mana5', 5, False, '5 mana on T5'), ('colors', 5, False, 'all colors on T5'),
                                  ('colors', 7, False, 'all colors on T7'), ('commander', 4, True, 'commander out by T4'), ('commander', 6, True, 'commander out by T6')] + \
                                 [(f'avail:{k}', t, False, f'{k} available (in play or castable) on T{t}') for k in changed for t in (5, 7)]:
            b = self._by(r0, key, t) if by else self._at(r0, key, t); a = self._by(r1, key, t) if by else self._at(r1, key, t)
            m, se = self._paired(r0, r1, key, t, by)
            gold.append({'measure': label, 'before': pct(b), 'after': pct(a), 'paired change': f'{pts(m)} (SE {100 * se:.1f})'})
        res.add(f'Goldfish ({games} games, same shuffles both sides)', gold)
        cut_rows, cards_ok = [], True
        for o, i in swaps:
            if o:
                a = audit_cut(st0, o); cards_ok &= a['label'] == 'mechanically_audited_cut'
                cut_rows.append({'card': o, 'role': 'out', 'label': a['label'], 'why': '; '.join(a['coarse_flags'] + a['audit_blockers'])[:400] or 'all clauses priced'})
            if i:
                lv, gaps, unk = self._understanding(i); cards_ok &= lv == 'complete'
                cut_rows.append({'card': i, 'role': 'in', 'label': f'understanding: {lv}', 'why': '; '.join(sorted({f for g in gaps for f in g.get('features', [])} | set(unk)))[:400] or 'all clauses priced'})
        if self.engine_games:
            erows, _ = SC.paired_rows(st0, st1, games=self.engine_games, seed=self.seed)
            res.add(f'Turn engine ({self.engine_games} games, same shuffles; light blockers)', erows)
        res.add('What the evaluator cannot see in these cards', cut_rows)
        res.add('Custody (hypothetical)', self._custody({i: 1 for _, i in swaps if i}, {o: 1 for o, _ in swaps if o}))
        res['summary'] = [f"Deck stays at {st1.size} cards.",
                          'Access changes by T7: ' + (', '.join(f"{r} {pts(a1[r]['T7'] - a0[r]['T7'])}" for r in changed) or 'none'),
                          'Each change is shown on its own; per-role changes are never added together.']
        res['uncertainty'] = [f"{x['card']} ({x['role']}): {x['why']}" for x in cut_rows if x['why'] != 'all clauses priced']
        res['limitations'] = LIMITS + (EN.ASSUMPTIONS if self.engine_games else [])
        res['conclusive'] = (cards_ok, 'every card involved is fully priced and every cut is mechanically audited' if cards_ok else
                             'at least one card has unpriced abilities or a cut needs human review: treat as a playtest candidate, not a verdict')
        res['data'] = {'access_before': a0, 'access_after': a1}
        return res

    # ================================================================ 5. upgrades
    def upgrades(self, deck, top=5, weakest=3, protect_decks=(), allow_transfers=False, games=None):
        inv = self.inv; d = self._resolve_deck(deck); st = self._state(d); games = games or max(1000, self.games // 2)
        protect = {self._resolve_deck(x) for x in protect_decks}
        acc = self._access(st, (7,)); _, allgaps = self._weakest(st, acc, 99)
        weak = []
        for g in allgaps:  # protection:anti_wipe is a sub-kind of protection: one family, one slot in the top list
            if g['area'] == 'protection:anti_wipe' and any(w['area'] == 'protection' for w in weak): continue
            if g['area'] == 'protection' and any(w['area'] == 'protection:anti_wipe' for w in weak):
                weak = [w for w in weak if w['area'] != 'protection:anti_wipe']
            weak.append(g)
            if len(weak) == weakest: break
        areas = [w['area'] for w in weak]
        rank_keys = [k for a in areas for k in ([a, 'protection:anti_wipe'] if a == 'protection' else [a])]
        by = audit_deck(st)
        cuts = (by.get('mechanically_audited_cut', []) + by.get('human_review_required', []))
        library = set(st.library)
        pool = []
        for n, r in inv.cards.items():
            if n in library or n in st.commanders or n in BASICS or inv.is_land(n) or not inv.legal_in(n, st.ci)[0]: continue
            if D.TUTOR.search(str(r['Oracle Text'])): continue
            if inv.free(n) > 0: src = 'free'
            elif allow_transfers:
                h = [x for x in inv.holders(n) if x not in protect and x != d]
                if not h: continue
                src = h[0]
            else: continue
            pool.append((n, src))
        base_r = A.roles(inv, st.library)
        def eligible_cut(hit, used):
            return next((c for c in cuts if c['card'] not in used and not any(st.library.index(c['card']) in base_r.get(a, set()) for a in hit)), None)
        def score(n, cut):
            a1 = self._access(self._state(d, [(cut['card'], n)]), (7,))
            gains = {a: a1[a]['T7'] - acc[a]['T7'] for a in rank_keys}
            losses = {k: a1[k]['T7'] - acc[k]['T7'] for k in a1 if k not in rank_keys and a1[k]['T7'] < acc[k]['T7']}
            return gains, losses
        cands = []
        for n, src in pool:
            fake = A.roles(inv, [n]); hit = [a for a in rank_keys if a in fake]
            if not hit: continue
            cut = eligible_cut(hit, ())
            if cut is None: continue
            gains, losses = score(n, cut)
            cands.append({'card': n, 'src': src, 'hit': hit, 'gains': gains})
        key = lambda c: tuple(-c['gains'][a] for a in rank_keys) + (c['src'] != 'free', float(inv.cards[c['card']]['Mana Value'] or 0), c['card'])
        cands.sort(key=key)
        # one card per slot; cover each weak area before stacking the first; distinct cuts assigned in order
        order = []
        for a in areas:
            for c in cands:
                if c['gains'][a] > 0 and c not in order: order.append(c); break
        order += [c for c in cands if c not in order]
        picked, used = [], set()
        for c in order:
            if len(picked) >= top: break
            cut = eligible_cut(c['hit'], used)
            if cut is None: continue
            used.add(cut['card']); gains, losses = score(c['card'], cut)
            picked.append((c['card'], c['src'], cut['card'], cut['label'], gains, losses))
        rows = []
        r0 = self._goldfish_rows(st, games); ebase = None
        for n, src, cut, label, gains, losses in picked:
            lv, gaps, unk = self._understanding(n)
            st1 = self._state(d, [(cut, n)])
            def _e(x):
                nonlocal ebase
                e, ebase = SC.engine_delta(st, x, games=self.engine_games, seed=self.seed, base=ebase)
                return e
            r1 = self._goldfish_rows(st1, games)
            mm, _ = self._paired(r0, r1, 'mana4', 4); cm, _ = self._paired(r0, r1, 'colors', 5)
            donor = 'none'
            if src != 'free':
                x0 = self._access(self._state(src), (7,)); x1 = self._access(self._state(src, [(n, A.BLANK)]), (7,))
                donor = ', '.join(f'{k} {pts(x1[k]["T7"] - x0[k]["T7"])}' for k in x0 if x1[k]['T7'] != x0[k]['T7']) or 'no access change'
            rows.append({'add': n, 'source': 'free' if src == 'free' else f'transfer from {src}', 'improves (seen by T7)': ', '.join(f'{a} {pts(v)}' for a, v in gains.items() if v > 0),
                         'costs elsewhere': ', '.join(f'{k} {pts(v)}' for k, v in losses.items()) or 'none',
                         'donor loss (no backfill)': donor, 'mana/colors (goldfish)': f'4 mana T4 {pts(mm)}, colors T5 {pts(cm)}',
                         'cut': f'{cut} ({label})', 'add understood': lv,
                         **({} if not self.engine_games else (lambda e: {'engine: damage by T10 (paired)': f"{e['damage'][0]:+.1f} (SE {e['damage'][1]:.1f})",
                              'engine: power 3 turns after T6 wipe': f"{e['recovery'][0]:+.1f} (SE {e['recovery'][1]:.1f})"})(_e(st1))),
                         'conclusive': 'yes' if lv == 'complete' and label == 'mechanically_audited_cut' and src == 'free' else 'no'})
        res = Result(f'Upgrades for {d}')
        res['summary'] = ['Weakest areas: ' + ', '.join(f"{w['area']} ({w['sources']} cards, seen by T7 {w['seen by T7']} vs {w['at target']} at target" + ('' if w['gap'] > 0 else ', already at target') + ')' for w in weak),
                          f"Candidates: {'free pool' + (' + transfers, never from ' + ', '.join(sorted(protect)) if allow_transfers else ' only')}, legal in {''.join(c for c in COLORS if c in st.ci)}, no tutors",
                          f'{len(rows)} upgrades shown; each pairs one add with one cut, and every cut is a different card.']
        res.add('Weakest functional areas', [{k: v for k, v in g.items() if k != 'gap'} for g in weak])
        res.add('Upgrades', rows or ['No candidate in the allowed pool adds to these areas.'])
        res.add('Cut order used (lowest measured loss first)', [{'card': c['card'], 'label': c['label'], 'loss by T7': pts(-c['access_loss_T7'])} for c in cuts[:12]])
        res['uncertainty'] = ['A cut labelled human_review_required has abilities the evaluator cannot price; check it before moving a card.',
                              'Gains are draw access only; a card that is drawn may still lack mana, targets or a board to use it.']
        res['limitations'] = LIMITS + (EN.ASSUMPTIONS if self.engine_games else [])
        res['conclusive'] = (all(r['conclusive'] == 'yes' for r in rows) and bool(rows), 'see the conclusive column per upgrade')
        res['data'] = {'weakest': weak, 'upgrades': rows}
        return res

    # ================================================================ 6. build
    def build(self, commander, n_lands=36):
        inv = self.inv; c = self._card(commander)
        prop = D.propose_configuration(inv, [c], n_lands=n_lands)
        key = '__build__'
        inv.decks[key] = [(c, 1, 'Commander')] + [(n, 1, 'Nonland' if not inv.is_land(n) else 'Land') for n in prop['list'] if n not in BASICS] + \
                         [(b, prop['list'].count(b), 'Land') for b in sorted(set(prop['list']) & BASICS)]
        try:
            st = self._state(key); acc = self._access(st, (5, 7)); weak, _ = self._weakest(st, acc)
            rows = self._goldfish_rows(st, self.games)
            partial = [n for n in set(st.library) if n not in BASICS and self._understanding(n)[0] != 'complete']
            peers = []
            for d in sorted(inv.decks):
                if d == key: continue
                shared = st.ci & inv.deck_ci(d)
                if len(shared) >= max(1, len(st.ci) - 1):
                    peers.append({'existing deck': d, 'colors': ''.join(x for x in COLORS if x in inv.deck_ci(d)),
                                  'shared plan modules': ', '.join(sorted(set(D.deck_assessment(inv, d)['plan_modules']) & set(prop['commander_modules']))) or '-'})
        finally:
            inv.decks.pop(key, None)
        res = Result(f'Build from free cards: {c}')
        res['summary'] = [f"{'Complete' if prop['complete'] else 'Incomplete'}: {len(prop['list']) + 1} cards from {prop['pool_size']} free legal spells; colors {prop['ci']}",
                          'Missing obligations: ' + ('; '.join(prop['missing_obligations']) or 'none'),
                          f"Mana: 4 by T4 {pct(self._at(rows, 'mana4', 4))}, all colors by T5 {pct(self._at(rows, 'colors', 5))}, commander out by T4 {pct(self._by(rows, 'commander', 4))}",
                          'Weakest areas: ' + ', '.join(f"{w['area']} {w['seen by T7']}" for w in weak)]
        res.add('List', [{'card': n, 'why': prop['why'].get(n, 'land')} for n in sorted(set(prop['list']), key=lambda x: (x in BASICS, x))])
        res.add('Draw access (exact)', [{'role': r, 'cards': v['k'], 'T5': pct(v['T5']), 'T7': pct(v['T7'])} for r, v in acc.items() if v['k'] or r in VITAL])
        res.add('Existing decks in overlapping colors (compare play pattern before building)', peers)
        res['uncertainty'] = [f'{len(partial)} chosen cards have abilities the evaluator does not price.',
                              'The list is chosen by function counts and the commander\'s module groups, not by play pattern or power.']
        res['limitations'] = LIMITS + ['Uses only free copies; no card is taken from a current deck.']
        res['conclusive'] = (False, 'a construction proposal for review, not a tested deck')
        return res

    # ================================================================ 7. inventory
    def inventory(self):
        inv = self.inv; ia = D.inventory_assessment(inv)
        sizes = {d: self._state(d).size for d in sorted(inv.decks)}
        res = Result('Inventory')
        res['summary'] = [f"{len(inv.cards)} card names; {len(inv.decks)} current decks, all at 100: {'yes' if all(v == 100 for v in sizes.values()) else 'NO'}",
                          f"{ia['free_names']} names have at least one free copy",
                          f"Source: sheet {inv.source()['sheet_id']}, export {inv.source()['export']} (sha256 {inv.sha256[:12]}…)"]
        res.add('Decks', [{'deck': d, 'cards': n, 'commanders': ', '.join(self.inv.commanders(d)), 'colors': ''.join(c for c in COLORS if c in inv.deck_ci(d))} for d, n in sizes.items()])
        res.add('Role supply across the collection', [{'role': f, **v} for f, v in ia['role_supply'].items()])
        res.add('Inventory tags the rules do not confirm', [{'role': f, **v} for f, v in ia['metadata_qa'].items() if v['tag_without_oracle_support']])
        res['limitations'] = ['Ownership and custody come from Collection and Deck Allocations only; plans and benches are not physical moves.']
        res['conclusive'] = (True, 'custody counts are read directly from the canonical sheet export')
        return res

    # ================================================================ 8. transfer
    def transfer(self, card, src, dst, backfill=None, cut=None):
        inv = self.inv; c = self._card(card); s = self._resolve_deck(src); t = self._resolve_deck(dst)
        if c not in self._state(s).library: raise KeyError(f'{c} is not in {s}')
        if not inv.legal_in(c, inv.deck_ci(t))[0]: raise KeyError(f'{c} is not legal in {t}')
        st_t = self._state(t)
        if cut is None:
            by = audit_deck(st_t); best = (by.get('mechanically_audited_cut') or by.get('human_review_required') or [None])[0]
            cut = best['card'] if best else None
        else: cut = self._card(cut)
        bf = self._card(backfill) if backfill else None
        s0, s1 = self._state(s), self._state(s, [(c, bf or A.BLANK)])
        t1 = self._state(t, [(cut, c)])
        def delta(a, b):
            x, y = self._access(a, (7,)), self._access(b, (7,))
            return [{'role': r, 'before': pct(x[r]['T7']), 'after': pct(y[r]['T7']), 'change': pts(y[r]['T7'] - x[r]['T7'])} for r in x if x[r]['T7'] != y[r]['T7']]
        def rclasses(st):
            out = {}
            for i, n in enumerate(st.library):
                if n == A.BLANK: continue
                for p in recursion_types(clauses(inv.cards[n]['Oracle Text'], n)): out.setdefault(f"to {p['destination']}, {p['referent']}, {p['cadence']}", set()).add(n)
            return out
        rc0, rc1 = rclasses(s0), rclasses(s1)
        lost = [{'recursion type': k, 'before': ', '.join(sorted(v)), 'after': ', '.join(sorted(rc1.get(k, set()))) or 'NONE'} for k, v in rc0.items() if v != rc1.get(k, set())]
        res = Result(f'Transfer {c}: {s} -> {t}')
        res.add(f'Donor {s} (' + (f'backfill {bf}' if bf else 'no backfill') + ')', delta(s0, s1) or ['No role access change.'])
        if lost: res.add(f'Donor {s}: typed recursion that changes', lost)
        res.add(f'Recipient {t} (cut {cut})', delta(st_t, t1) or ['No role access change.'])
        res.add('Custody (hypothetical)', self._custody({**({bf: 1} if bf else {}), c: 0}, {cut: 1} if cut else {}) +
                [{'card': c, 'owned': inv.owned(c), 'free before': inv.free(c), 'free after': inv.free(c), 'now in': s, 'conserved': f'moves {s} -> {t}'}])
        flags = []
        a_out = audit_cut(s0, c); flags.append(f"{c} as a cut from {s}: {a_out['label']}")
        if cut: a_cut = audit_cut(st_t, cut); flags.append(f"{cut} as a cut from {t}: {a_cut['label']}")
        res['summary'] = [f'Both decks stay at 100.' if s1.size == 100 and t1.size == 100 else f'Sizes after: {s} {s1.size}, {t} {t1.size}'] + flags + \
                         (['A recursion type the donor relies on disappears: see the typed recursion table.'] if any(x['after'] == 'NONE' for x in lost) else [])
        ok = a_out['label'] == 'mechanically_audited_cut' and (not cut or a_cut['label'] == 'mechanically_audited_cut')
        res['uncertainty'] = flags[1:] if not ok else []
        res['limitations'] = LIMITS
        res['conclusive'] = (ok, 'both removals are mechanically audited' if ok else 'a removal has unpriced abilities or protected status: the owner decides')
        return res

    # ================================================================ 9. portfolio
    def portfolio(self, card, decks=None, objective='protection:anti_wipe'):
        """Where should one free copy go? Per-deck objective vectors, the Pareto set, and a
        maximin suggestion on one stated objective. Nothing is summed across roles."""
        inv = self.inv; c = self._card(card)
        decks = [self._resolve_deck(x) for x in decks] if decks else sorted(inv.decks)
        rows, vecs = [], {}
        for d in decks:
            st = self._state(d)
            if c in st.library or not inv.legal_in(c, st.ci)[0]: continue
            by = audit_deck(st); cut = (by.get('mechanically_audited_cut') or by.get('human_review_required') or [None])[0]
            if not cut: continue
            a0 = self._access(st, (7,)); a1 = self._access(self._state(d, [(cut['card'], c)]), (7,))
            ch = {r: round(a1[r]['T7'] - a0[r]['T7'], 4) for r in a0 if a1[r]['T7'] != a0[r]['T7']}
            vecs[d] = (a0[objective]['T7'] if objective in a0 else 0.0, ch)
            rows.append({'deck': d, f'{objective} before (T7)': pct(vecs[d][0]), 'changes by T7': ', '.join(f'{k} {pts(v)}' for k, v in ch.items()),
                         'cut': f"{cut['card']} ({cut['label']})"})
        best = min(vecs, key=lambda d: (vecs[d][0], -vecs[d][1].get(objective, 0))) if vecs else None
        res = Result(f'Portfolio: where should {c} go?')
        res['summary'] = [f"Custody: {inv.free(c)} free of {inv.owned(c)} owned.",
                          'Each option improves only its own deck, so no option dominates another; choosing needs a stated priority.',
                          (f'Maximin on {objective} (help the deck that has least of it first): ' + ', '.join(sorted(x for x in vecs if vecs[x][0] == vecs[best][0] and vecs[x][1].get(objective, 0) == vecs[best][1].get(objective, 0)))
                           + (' (tied; compare their other changes and cuts)' if sum(1 for x in vecs if vecs[x][0] == vecs[best][0] and vecs[x][1].get(objective, 0) == vecs[best][1].get(objective, 0)) > 1 else '')) if best else 'No legal destination.']
        res.add('Options', rows)
        res['uncertainty'] = ['The maximin rule is a preference, not a measurement; weighting a deck\'s main plan higher can change the answer.']
        res['limitations'] = LIMITS
        res['conclusive'] = (False, 'allocation depends on owner priorities')
        return res
