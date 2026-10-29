"""v0.2 bridge: the 0.3.0 evaluator reads every per-card textual fact from SQLite.

v0.1's bridge cached Inventory rows, role claims and ability projections. The evaluator still ran
regex readers at query time for clauses, the clause audit, wipe kinds, protection scope, recursion
types, the resource ledger, token feedback, closing profile, commander dependence, the tutor filter
and the goldfish CardModel. Here each of those is answered from `derived_facts` (written offline
by kbfacts.derive, keyed by the exact input the runtime passes).

A lookup miss means the DB is stale relative to the input: by default it falls back to the 0.3.0
reader and is counted in `stats['misses']`; `strict=True` raises instead.

Only actions that pass all six verification states (contract_verification.mechanically_supported:
Oracle identity, current rules text, human semantic review, lossless compile, passing runtime
scenario) are attached to the runtime record as `verified_actions`; nothing else is promoted.

Inventory policy (kb_policy): rows the reconciliation marks non-game are excluded, and cards whose
Sheet text is materially wrong are read from the Oracle rules text, never edited in the Sheet.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kbfacts as F

DERIVATION_VERSION = 'kbfacts-0.2.1/mtg_eval_0.3.0+kb4'


class FactStore:
    def __init__(self, con, strict=False):
        self.raw = {(k, key): v for k, key, v in con.execute('select fact_kind,input_key,value_json from derived_facts')}
        self.cache, self.strict = {}, strict
        self.stats = {'hits': {}, 'misses': {}}

    def get(self, kind, key, fallback):
        k = (kind, key)
        if k in self.cache:
            self.stats['hits'][kind] = self.stats['hits'].get(kind, 0) + 1
            return self.cache[k]
        if k in self.raw:
            self.stats['hits'][kind] = self.stats['hits'].get(kind, 0) + 1
            v = self.cache[k] = F.loads(self.raw[k])
            return v
        self.stats['misses'][kind] = self.stats['misses'].get(kind, 0) + 1
        if self.strict: raise KeyError(f'derived fact missing: {kind}')
        return fallback()


def _rebind(original, replacement):
    """Point every mtg_eval module-level name bound to `original` at `replacement`."""
    for m in [m for n, m in list(sys.modules.items()) if n == 'mtg_eval' or n.startswith('mtg_eval.')]:
        for a, v in list(vars(m).items()):
            if v is original: setattr(m, a, replacement)


def install(facts):
    """Route the evaluator's text readers through the fact store. Returns the originals."""
    import copy
    from mtg_eval import semantics as M, structure as S, deckeval as D, access as A
    orig = {'clean': M.clean, 'clauses': M.clauses, 'clause_audit': M.clause_audit, 'recursion_types': M.recursion_types,
            'wipe_kind': M.wipe_kind, 'protection_profile': M.protection_profile, 'resource_claims': S.resource_claims,
            'feedback': S.feedback, 'closing_profile': S.closing_profile, 'commander_dependence': S.commander_dependence,
            'TUTOR': D.TUTOR, 'CardModel': A.CardModel}
    # mutable results are deep-copied so a caller that edits a result cannot corrupt the store
    def clean(oracle, name): return facts.get('clean', F.sha(name, str(oracle)), lambda: orig['clean'](oracle, name))
    def clauses(oracle, name): return list(facts.get('clauses', F.sha(name, str(oracle)), lambda: orig['clauses'](oracle, name)))
    def clause_audit(oracle, name): return copy.deepcopy(facts.get('clause_audit', F.sha(name, str(oracle)), lambda: orig['clause_audit'](oracle, name)))
    def recursion_types(cl): return copy.deepcopy(facts.get('recursion_types', F.sha(json.dumps(cl)), lambda: orig['recursion_types'](cl)))
    def wipe_kind(t): return set(facts.get('wipe_kind', F.sha(t), lambda: orig['wipe_kind'](t)))
    def protection_profile(t): return copy.deepcopy(facts.get('protection_profile', F.sha(t), lambda: orig['protection_profile'](t)))
    def resource_claims(text): return copy.deepcopy(facts.get('resource_claims', F.sha(text), lambda: orig['resource_claims'](text)))

    def ff(text): return facts.get('feedback_features', F.sha(text), lambda: F.feedback_features(text))

    def feedback(texts, family):
        fe = {c: ff(t) for c, t in texts.items()}
        makers = sorted(c for c in texts if fe[c][family]['maker'])
        enter = sorted(c for c in texts if fe[c][family]['enter'])
        cast = sorted(c for c in texts if fe[c][family]['cast'])
        loops = sorted(c for c in enter if fe[c][family]['loop'])
        mult = sorted(c for c in texts if fe[c]['multiplier'])
        reinforce = sorted(c for c in enter if fe[c][family]['reinforce'])
        cls = ('compounding' if loops else 'reinforcing' if reinforce else 'multiplied' if mult
               else 'linear' if (enter or cast) else 'no payoffs')
        capped = sorted(c for c in loops if fe[c]['capped'])
        return {'family': family, 'class': cls, 'capped loops': capped, 'reinforcers': reinforce, 'makers': makers, 'enter_payoffs': enter, 'cast_payoffs': cast,
                'loops': loops, 'multipliers': mult}

    def closing_profile(inv, cards):
        fe = {c: facts.get('closing_features', F.closing_key(inv.cards[c], c), lambda c=c: F.closing_features(inv, c)) for c in cards}
        creatures = [c for c in cards if fe[c]['creature']]
        anthems = [c for c in cards if fe[c]['anthem']]
        lasting = [c for c in anthems if fe[c]['lasting']]
        return {'creature cards': len(creatures), 'power 4+': [c for c in creatures if fe[c]['power4']],
                'evasive creatures': [c for c in creatures if fe[c]['evasive']],
                'lasting anthems': lasting, 'one-turn anthems': sorted(set(anthems) - set(lasting)),
                'combat-damage engines': [c for c in cards if fe[c]['combat_engine'] and (c not in creatures or fe[c]['combat_engine_team'])],
                'repeatable drain or ping': [c for c in cards if fe[c]['ping_repeat']]}

    def commander_dependence(inv, commanders, cards, families):
        out = []
        for cmd in commanders:
            f = ff(str(inv.cards[cmd]['Oracle Text']))
            makes = [x for x in ('artifact', 'creature') if f[x]['maker']]
            feed, kind = None, f['cast_feed_kind']
            if kind:
                def fed(c):
                    tl = str(inv.cards[c]['Type Line'])
                    if inv.is_land(c): return False
                    return {'noncreature': 'Creature' not in tl, 'artifact': 'Artifact' in tl, 'creature': 'Creature' in tl,
                            'instant or sorcery': 'Instant' in tl or 'Sorcery' in tl}[kind]
                feed = sum(fed(c) for c in cards)
            guards = sorted({c for c in cards for p in protection_profile(A.text(inv, c)) if p['scope'] in S.COVERS_COMMANDER})
            makers = families.get(makes[0], {}).get('makers', []) if makes else []
            out.append({'commander': cmd, 'engine': bool(makes and feed), 'makes': makes, 'spells that feed it': feed,
                        'other makers of that family': len([c for c in makers if c != cmd]), 'protection that can cover it': guards})
        return out

    class Tutor:
        pattern = orig['TUTOR'].pattern
        def search(self, text):
            return facts.get('tutor', F.sha(str(text)), lambda: bool(orig['TUTOR'].search(str(text)))) or None

    Base = orig['CardModel']

    class CardModel(Base):
        """Restores the CardModel state persisted for this card and colour identity."""
        def __init__(self, inv, n, ci):
            if n == A.BLANK or n not in inv.cards:
                return Base.__init__(self, inv, n, ci)
            groups = facts.get('card_model', F.card_model_key(inv.cards[n], n), lambda: None)
            want = F.ci_key(ci)
            hit = next((st for cis, st in (groups or []) if want in cis), None)
            if hit is None:
                return Base.__init__(self, inv, n, ci)
            self.__dict__.update(F.dec(copy.deepcopy(hit)))

    repl = {'clean': clean, 'clauses': clauses, 'clause_audit': clause_audit, 'recursion_types': recursion_types,
            'wipe_kind': wipe_kind, 'protection_profile': protection_profile, 'resource_claims': resource_claims,
            'feedback': feedback, 'closing_profile': closing_profile, 'commander_dependence': commander_dependence,
            'TUTOR': Tutor(), 'CardModel': CardModel}
    for k, v in repl.items(): _rebind(orig[k], v)
    return orig


def uninstall(orig, current):
    for k, v in orig.items(): _rebind(current[k], v)


def open_evaluator(database, games=5000, seed=20261018, engine_games=300, strict=False, use_facts=True, policy=True):
    """SQLite-backed 0.3.0 Evaluator. use_facts=False reproduces the v0.1 bridge (runtime regex);
    policy=False keeps mtg_eval 0.3.0's hard-coded NON_DECK list and the Sheet text for every card."""
    for p in (str(HERE), str(HERE / 'vendor')):
        if p not in sys.path: sys.path.insert(0, p)
    from sqlite_bridge import SQLiteEvaluator
    ev = SQLiteEvaluator(database, games=games, seed=seed, engine_games=engine_games)
    ev.facts = None
    src = ev.inv.source()
    src.setdefault('export', Path(database).name)  # v0.1 bridge omitted the key api.inventory() reads
    ev.inv.source = lambda: dict(src)
    if use_facts:
        ev.facts = FactStore(ev.inv.db, strict=strict)
        install(ev.facts)
        if policy:
            import kb_policy
            from mtg_eval import abilities
            ev.inv.oracle_read = kb_policy.apply(ev.inv, ev.inv.db)
            for n in ev.inv.oracle_read:  # runtime records derived offline from the Oracle rules text
                abilities._CACHE[(ev.inv.sha256, n)] = ev.facts.get('runtime_record', F.sha(n, str(ev.inv.cards[n]['Oracle Text'])),
                                                                     lambda: (abilities._CACHE.pop((ev.inv.sha256, n), None), abilities.card_record(ev.inv, n))[1])
        attach_verified_actions(ev.inv)
    return ev


def attach_verified_actions(inv):
    """Add compiled actions that passed all six verification states to the runtime records (read-only)."""
    from mtg_eval import abilities
    try:
        rows = inv.db.execute('select card_name,contract_id,action_json from runtime_verified_actions').fetchall()
    except Exception:
        return 0
    for name, cid, aj in rows:
        rec = abilities._CACHE.get((inv.sha256, name))
        if rec is not None: rec.setdefault('verified_actions', []).append({'contract_id': cid, 'action': json.loads(aj)})
    return len(rows)
