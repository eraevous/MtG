"""Offline derivation of every per-card textual fact the 0.3.0 evaluator reads at query time.

This module is the ONLY place the 0.3.0 regex readers run in the v0.2 architecture
(workbook -> versioned offline import -> SQLite -> compiler -> evaluator). The results are
persisted in `derived_facts`, keyed by the exact input each runtime call receives, so the
query/evaluation path becomes a lookup. They are machine readings with the 0.3.0 parser's
limits, stamped with `derivation_version`; they are not reviewed semantics.
"""
import hashlib, itertools, json, re

COLORS = 'WUBRG'


# ---------------------------------------------------------------- typed JSON (sets/tuples survive)
def enc(o):
    if isinstance(o, (set, frozenset)):
        items = [enc(x) for x in o]
        return {'$set': sorted(items, key=lambda x: json.dumps(x, sort_keys=True))}
    if isinstance(o, tuple): return {'$tuple': [enc(x) for x in o]}
    if isinstance(o, list): return [enc(x) for x in o]
    if isinstance(o, dict): return {str(k): enc(v) for k, v in o.items()}
    return o


def dec(o):
    if isinstance(o, dict):
        if set(o) == {'$set'}: return set(dec(x) for x in o['$set'])
        if set(o) == {'$tuple'}: return tuple(dec(x) for x in o['$tuple'])
        return {k: dec(v) for k, v in o.items()}
    if isinstance(o, list): return [dec(x) for x in o]
    return o


def dumps(o): return json.dumps(enc(o), ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def loads(s): return dec(json.loads(s))


def sha(*parts):
    return hashlib.sha256('\x00'.join(str(p) for p in parts).encode('utf-8')).hexdigest()


def ci_key(ci): return ''.join(c for c in COLORS if c in ci)


ALL_CI = [set(x) for k in range(6) for x in itertools.combinations(COLORS, k)]


# ---------------------------------------------------------------- per-card readings
def feedback_features(text):
    """Per-text pieces of structure.feedback; the deck-level combination is pure set logic."""
    from mtg_eval import structure as S
    lines = [l for l in text.split('\n') if l.strip()]
    out = {}
    for fam in ('artifact', 'creature'):
        out[fam] = {
            'maker': bool(S.MAKES[fam].search(text)),
            'enter': bool(S.ON_ENTER[fam].search(text)),
            'cast': bool(S.ON_CAST[fam].search(text)),
            'loop': any(S.ON_ENTER[fam].search(l) and S.MAKES[fam].search(l) for l in lines),
            'reinforce': any(S.ON_ENTER[fam].search(l) and S.REINFORCE.search(l) for l in lines),
        }
    out['multiplier'] = any(S.MULTIPLY.search(l) and re.search(r'\btokens?\b', l, re.I) for l in lines)
    out['capped'] = bool(re.search(r'only once each turn', text, re.I))
    m = re.search(r'whenever you cast an? (noncreature|artifact|creature|instant or sorcery)[^.]*spell', text, re.I)
    out['cast_feed_kind'] = m.group(1).lower() if m else None
    return out


def closing_features(inv, c):
    from mtg_eval import structure as S
    r = inv.cards[c]; txt = str(r['Oracle Text'])
    creature = 'Creature' in str(r['Type Line'])
    anthem = bool(S.ANTHEM.search(txt))
    return {'creature': creature, 'power4': (S._power(r['Power']) or 0) >= 4,
            'evasive': bool(S.EVASION.search(txt + ' ' + str(r['Keywords']))),
            'anthem': anthem, 'lasting': anthem and not re.search(S.ANTHEM.pattern + r'[^.]*until end of turn', txt, re.I),
            'combat_engine': bool(S.COMBAT_ENGINE.search(txt)),
            'combat_engine_team': bool(re.search(r'whenever (?:a|one or more|another)[^.]*creatures?(?: tokens?)? you control deals? combat damage', txt, re.I)),
            'ping_repeat': bool(S.PING.search(txt) and re.search(r'\bwhenever\b', txt, re.I))}


def card_model_groups(inv, n):
    """CardModel for every colour identity, grouped: [[ci_keys], state]. Exact by construction."""
    from mtg_eval import access as A
    groups = {}
    for ci in ALL_CI:
        state = dumps(vars(A.CardModel(inv, n, ci)))
        groups.setdefault(state, []).append(ci_key(ci))
    return [[cis, json.loads(state)] for state, cis in groups.items()]


def derive(inv):
    """Yield (fact_kind, key, card_name, value) for every card in a (SQLite) Inventory."""
    from mtg_eval import semantics as M, structure as S, deckeval as D, access as A
    for n in sorted(inv.cards):
        r = inv.cards[n]; oracle = r['Oracle Text']; so = str(oracle)
        kn = sha(n, so)
        t = M.clean(oracle, n)
        cl = M.clauses(oracle, n)
        yield 'clean', kn, n, t
        yield 'clauses', kn, n, cl
        yield 'clause_audit', kn, n, M.clause_audit(oracle, n)
        yield 'recursion_types', sha(json.dumps(cl)), n, M.recursion_types(cl)
        yield 'wipe_kind', sha(t), n, M.wipe_kind(t)
        yield 'protection_profile', sha(t), n, M.protection_profile(t)
        yield 'resource_claims', sha(so), n, S.resource_claims(so)
        yield 'tutor', sha(so), n, bool(D.TUTOR.search(so))
        yield 'feedback_features', sha(so), n, feedback_features(so)
        yield 'closing_features', closing_key(r, n), n, closing_features(inv, n)
        yield 'card_model', card_model_key(r, n), n, card_model_groups(inv, n)
    from mtg_eval import abilities
    for n in sorted(getattr(inv, 'oracle_read', [])):  # cards read from Oracle rules text need their own runtime record
        abilities._CACHE.pop((inv.sha256, n), None)
        yield 'runtime_record', sha(n, str(inv.cards[n]['Oracle Text'])), n, abilities.card_record(inv, n)
        abilities._CACHE.pop((inv.sha256, n), None)


def card_model_key(r, n):
    return sha(n, str(r['Oracle Text']), r['Type Line'], r['Mana Cost'], r['Produces'], r['ETB Tapped'], r['Roles'])


def closing_key(r, n):
    return sha(n, str(r['Oracle Text']), r['Type Line'], r['Power'], r['Keywords'])
