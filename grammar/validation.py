"""Set-level and rulings-based validation of the grammar -> DIO mappings.

    python3 -I validation.py grammar_layer.sqlite --rulings rulings-YYYYMMDDhhmmss.jsonl.gz \
        --sets tla tle eoe eoc tmt tmc --heldout trk trc --out validation/

What it does, in order:

  1. Loads complete sets (data/sets/<code>.json, from fetch_sets.py) and builds ability contracts for every card in
     them, not only owned cards.
  2. HELD-OUT FIRST: freezes the contracts of the held-out sets (sha256 + time) before any of their rulings are read.
  3. Ingests Scryfall rulings once from the bulk file, keyed by oracle_id. Each ruling keeps its source (wotc or
     scryfall), its publication date, the bulk file name and sha256, and the time it was ingested. A ruling is
     identified by the sha256 of (oracle_id, source, date, text), so a re-run inserts only new rulings.
  4. Reads macro expansions from printed reminder text (earthbend, station, sneak ...) and stores them as proposed
     expansions with their provenance.
  5. Turns rulings into claims. Mechanic-level claims are hand-extracted (CURATED, each tied to the exact ruling
     text) and attached to a construction or a keyword macro, so one ruling tests every card that uses it. Generic
     claims come from fixed patterns (PATTERNS). A ruling no claim was extracted from stays 'unconverted'; it is
     never counted as agreement.
  6. Evaluates every claim against the contracts. Outcomes per ruling: confirmed, contradiction,
     insufficient_representation, ambiguous, unconverted, plus the potentially_outdated flag. Abilities with no
     ruling at all are counted as no_applicable_ruling, which is not confirmation.

Nothing here promotes a contract or a template to reviewed, and nothing touches the inventory.
"""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantics as sm  # noqa: E402

VALIDATION_VERSION = 'validation-0.1.0'
HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = '''
DROP TABLE IF EXISTS set_info; DROP TABLE IF EXISTS set_member; DROP TABLE IF EXISTS macro_expansion;
DROP TABLE IF EXISTS claim; DROP TABLE IF EXISTS test_result; DROP TABLE IF EXISTS ruling_status;
DROP TABLE IF EXISTS ruling_scope; DROP TABLE IF EXISTS mechanic_family;
CREATE TABLE set_info(code TEXT PRIMARY KEY, name TEXT, set_type TEXT, released_at TEXT, card_count INT,
  parent_set_code TEXT, retrieved_utc TEXT, role TEXT);
CREATE TABLE set_member(code TEXT, oracle_id TEXT, name TEXT, collector_number TEXT, rarity TEXT);
CREATE TABLE IF NOT EXISTS ruling(ruling_sha TEXT PRIMARY KEY, oracle_id TEXT, source TEXT, published_at TEXT,
  comment TEXT, bulk_file TEXT, bulk_sha256 TEXT, ingested_utc TEXT);
CREATE INDEX IF NOT EXISTS ix_ruling_oracle ON ruling(oracle_id);
CREATE TABLE ruling_scope(ruling_sha TEXT, scope TEXT, mechanic TEXT, n_cards INT);
CREATE TABLE macro_expansion(macro TEXT PRIMARY KEY, reminder_template TEXT, n_cards INT, example_card TEXT,
  contracts_json TEXT, provenance TEXT, status TEXT);
CREATE TABLE claim(claim_id TEXT PRIMARY KEY, ruling_sha TEXT, ruling_text TEXT, mechanic TEXT, scope_kind TEXT,
  scope_ref TEXT, polarity TEXT, predicate TEXT, args_json TEXT, extracted_by TEXT, note TEXT, status TEXT);
CREATE TABLE test_result(claim_id TEXT, oracle_id TEXT, ability_id TEXT, outcome TEXT, detail TEXT);
CREATE TABLE ruling_status(ruling_sha TEXT, oracle_id TEXT, status TEXT, outdated INT, detail TEXT);
CREATE TABLE mechanic_family(code TEXT, mechanic TEXT, kind TEXT, n_cards INT, n_abilities INT, n_templates INT,
  n_complete_templates INT, first_seen TEXT, status_in_set TEXT, templates_json TEXT);
CREATE TABLE IF NOT EXISTS frozen_prediction(set_code TEXT, sha256 TEXT, frozen_utc TEXT, path TEXT, n_contracts INT);
'''

MECHANICS = {'earthbend': 'kwa.earthbend', 'station': 'kw.station', 'sneak': 'kw.sneak'}

# ------------------------------------------------------------------ curated claims
# Each claim is tied to the exact ruling text it was read from (the 'ruling' substring must occur in exactly one
# distinct ruling comment). 'scope' says what it tests: a keyword macro (every ability using it, plus the macro's
# expansion), or templates matching a pattern (every card using the construction).
CURATED = [
    # earthbend (Avatar: The Last Airbender, 2025-11-21)
    dict(id='earthbend.def.target', mechanic='earthbend', ruling='"Earthbend N" means "Target land you control becomes',
         scope=('macro', 'kwa.earthbend'), polarity='positive', predicate='has_target',
         args={'q': {'card_type': ['land'], 'controller': 'you'}},
         note='Earthbend targets a land you control; every ability that earthbends must have that eligibility group.'),
    dict(id='earthbend.def.counters', mechanic='earthbend', ruling='"Earthbend N" means "Target land you control becomes',
         scope=('macro', 'kwa.earthbend'), polarity='positive', predicate='macro_result_includes',
         args={'hook': 'counter.put', 'q': {'counter_kind': '+1/+1'}}, note='Put N +1/+1 counters on it.'),
    dict(id='earthbend.def.animate', mechanic='earthbend', ruling='"Earthbend N" means "Target land you control becomes',
         scope=('macro', 'kwa.earthbend'), polarity='positive', predicate='macro_result_includes',
         args={'concept': 'op.type.change'}, note='The land becomes a 0/0 creature with haste in addition to its types.'),
    dict(id='earthbend.def.return', mechanic='earthbend', ruling='"Earthbend N" means "Target land you control becomes',
         scope=('macro', 'kwa.earthbend'), polarity='positive', predicate='macro_trigger_alternatives_exact',
         args={'hooks': ['permanent.dies', 'exile.enter'], 'then': 'card.return_to_battlefield'},
         note='When it dies or is exiled, return it to the battlefield tapped.'),
    dict(id='earthbend.other_zones', mechanic='earthbend', ruling='would go to any zone other than the graveyard or exile',
         scope=('macro', 'kwa.earthbend'), polarity='negative', predicate='macro_trigger_alternatives_exclude',
         args={'hooks': ['battlefield.leave', 'card.return_to_hand', 'zone.enter']},
         note='Bounce or tuck does not return it: the delayed trigger must not observe a generic departure.'),
    dict(id='earthbend.illegal_target', mechanic='earthbend', ruling='If the targeted land becomes an illegal target',
         scope=('macro', 'kwa.earthbend'), polarity='positive', predicate='has_target', args={},
         note='Earthbend has a target, so it can fizzle.'),
    dict(id='earthbend.no_color', mechanic='earthbend', ruling="Earthbend doesn't give the land you control a color",
         scope=('macro', 'kwa.earthbend'), polarity='negative', predicate='macro_result_excludes',
         args={'concept': 'op.type.change', 'q_key': 'color'},
         note='The type change adds creature and haste, never a color.'),
    dict(id='earthbend.already_creature', mechanic='earthbend', ruling='You may target a land that is already a creature',
         scope=('macro', 'kwa.earthbend'), polarity='negative', predicate='target_excludes',
         args={'q_key': 'card_type_not', 'value': 'creature'}, note='The target must not exclude creatures.'),
    dict(id='earthbend.trigger_is_action', mechanic='earthbend', ruling='An ability that triggers "whenever you earthbend"',
         scope=('frame', r'^whenever <player\.[a-z_]+> earthbend'), polarity='positive', predicate='frame_maps_to',
         args={'concept': 'ev.keyword_action', 'role': 'trigger_event'},
         note='"Whenever you earthbend" observes the keyword action itself, even if some of its actions were impossible.'),
    # station (Edge of Eternities, 2025-08-01)
    dict(id='station.def.cost', mechanic='station', ruling='The station keyword means "Tap another untapped creature you control',
         scope=('macro', 'kw.station'), polarity='positive', predicate='macro_cost_includes',
         args={'concept': 'cost.tap_other', 'q': {'exclude_self': True, 'controller': 'you', 'card_type': ['creature']}},
         note='Station is paid by tapping another untapped creature you control.'),
    dict(id='station.def.counters', mechanic='station', ruling='The station keyword means "Tap another untapped creature you control',
         scope=('macro', 'kw.station'), polarity='positive', predicate='macro_result_includes',
         args={'hook': 'counter.put', 'q': {'counter_kind': 'charge'}}, note='Put charge counters on this permanent.'),
    dict(id='station.def.amount', mechanic='station', ruling='The station keyword means "Tap another untapped creature you control',
         scope=('macro', 'kw.station'), polarity='positive', predicate='macro_amplifier', args={'concept': 'amp.stat'},
         note="The number of counters equals the tapped creature's power: an amplifier, not a requirement."),
    dict(id='station.def.sorcery', mechanic='station', ruling='The station keyword means "Tap another untapped creature you control',
         scope=('macro', 'kw.station'), polarity='positive', predicate='macro_timing_speed', args={'speed': 'sorcery'},
         note='Activate only as a sorcery.'),
    dict(id='station.not_mana', mechanic='station', ruling='The station keyword means "Tap another untapped creature you control',
         scope=('macro', 'kw.station'), polarity='negative', predicate='macro_result_excludes',
         args={'hook': 'permanent.tapped_for_mana'},
         note='Addendum A1: tapping a creature for station does not make permanent.tapped_for_mana true.'),
    dict(id='station.striation', mechanic='station', ruling='A station symbol means "As long as this permanent has N or more charge counters on it',
         scope=('striations', 'kw.station'), polarity='positive', predicate='striation_condition',
         args={'counter_kind': 'charge'},
         note='Each striation is a static condition on N or more charge counters; every "N+ |" line must yield one.'),
    dict(id='station.state_not_event', mechanic='station', ruling='The abilities of a permanent with station are based on the number of charge counters',
         scope=('striations', 'kw.station'), polarity='positive', predicate='striation_is_state', args={},
         note='Counters from any source (proliferate) change the abilities: the condition is a state, not a trigger.'),
    dict(id='station.lki_power', mechanic='station', ruling="Use the tapped creature's power as the station ability resolves",
         scope=('macro', 'kw.station'), polarity='positive', predicate='not_representable',
         args={'reason': 'amplifiers carry no evaluation_time (resolution / last known information) yet'},
         note="Power is read on resolution, using last known information."),
    dict(id='station.negative_power', mechanic='station', ruling='If the tapped creature has negative power',
         scope=('macro', 'kw.station'), polarity='positive', predicate='not_representable',
         args={'reason': 'no rule for negative amounts'}, note='Negative power puts no counters and removes none.'),
    # sneak (Teenage Mutant Ninja Turtles, 2026-03-06)
    dict(id='sneak.timing', mechanic='sneak', ruling='Spells can only be cast for their sneak costs',
         scope=('macro', 'kw.sneak'), polarity='positive', predicate='macro_text_window',
         args={'pattern': 'declare blockers step'},
         note='Castable for the sneak cost only in your declare blockers step, at instant speed.'),
    dict(id='sneak.cost', mechanic='sneak', ruling='Spells can only be cast for their sneak costs',
         scope=('macro', 'kw.sneak'), polarity='positive', predicate='macro_cost_includes',
         args={'concept': 'cost.return_to_hand', 'q': {'controller': 'you'}},
         note='Returning an unblocked attacker you control to hand is part of the sneak cost.'),
    dict(id='sneak.enters_attacking', mechanic='sneak', ruling="If a creature spell's sneak cost was paid, the creature it becomes enters tapped and attacking",
         scope=('macro', 'kw.sneak'), polarity='positive', predicate='macro_result_includes',
         args={'hook': 'battlefield.enter', 'status': ['tapped', 'attacking']},
         note='It enters tapped and attacking: an entry with status, not a declaration.'),
    dict(id='sneak.not_declared', mechanic='sneak', ruling='those tokens were never declared as attacking creatures',
         scope=('frame', r'\benter (?:tapped and )?attacking\b|\btapped and attacking\b'), polarity='negative',
         predicate='frame_maps_to', args={'concept': 'ev.attacker.declared'},
         note='Entering attacking never satisfies "whenever a creature attacks" (DIO: entered attacking != declared as attacker).'),
]

# ------------------------------------------------------------------ generic patterns
OUTDATED = re.compile(r'enters the battlefield|comes into play|\bin play\b|removed from the game|mana burn|'
                      r'damage on the stack|leaves play', re.I)
ACTS = {'sacrificing': 'sacrifice', 'paying': 'pay', 'tapping': 'tap', 'discarding': 'discard', 'exiling': 'exile',
        'returning': 'return_to_hand', 'removing': 'remove_counters', 'revealing': 'reveal'}
PATTERNS = [
    ('pattern.once_each_turn', re.compile(r'\b(?:triggers?|resolves?|activated?) only once each turn\b|\bonly once each turn\b', re.I),
     'capacity', {}),
    ('pattern.mana_ability', re.compile(r"\bis a mana ability\b", re.I), 'is_mana_ability', {'value': True}),
    ('pattern.not_mana_ability', re.compile(r"\b(?:isn't|is not) a mana ability\b", re.I), 'is_mana_ability', {'value': False}),
    ('pattern.not_target', re.compile(r"\b(?:doesn't|does not|don't|do not) target\b", re.I), 'card_has_target', {'value': False}),
    ('pattern.act_not_cost', re.compile(r"\b(" + '|'.join(ACTS) + r")\b[^.]{0,80}?\b(?:isn't|is not|aren't|are not) (?:a |an |part of (?:the |its )?)?(?:additional )?cost", re.I),
     'act_in', {'where': 'result'}),
    ('pattern.act_is_cost', re.compile(r"\b(" + '|'.join(ACTS) + r")\b[^.]{0,80}?\b(?:is|are) (?:a |an |part of (?:the |its )?)(?:additional )?cost", re.I),
     'act_in', {'where': 'cost'}),
]


def rsha(oid, source, date, text):
    return hashlib.sha256('\t'.join([oid or '', source or '', date or '', text]).encode()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ------------------------------------------------------------------ steps

def load_sets(db, codes, heldout, setdir):
    for code in codes + heldout:
        d = json.load(open(os.path.join(setdir, code + '.json')))
        s = d['set']
        db.execute('INSERT INTO set_info VALUES(?,?,?,?,?,?,?,?)', (s['code'], s['name'], s['set_type'], s['released_at'],
                                                                  s['card_count'], s.get('parent_set_code'), d['retrieved_utc'],
                                                                  'held_out' if code in heldout else 'training'))
        seen = set()
        for m in d['members']:
            if m['oracle_id'] in seen:
                continue
            seen.add(m['oracle_id'])
            db.execute('INSERT INTO set_member VALUES(?,?,?,?,?)', (code, m['oracle_id'], m['name'], m['collector_number'], m['rarity']))


def contracts_by_card(db, where):
    out = collections.defaultdict(list)
    for oid, aid, cj in db.execute(f'SELECT ac.oracle_id, ac.ability_id, ac.contract_json FROM ability_contract ac WHERE {where}'):
        out[oid].append((aid, json.loads(cj)))
    return out


def freeze(db, codes, outdir):
    rows = db.execute(f'''SELECT sm.code, c.name, ac.ability_id, ac.contract_json FROM ability_contract ac JOIN card c USING(oracle_id)
                          JOIN set_member sm ON sm.oracle_id=ac.oracle_id WHERE sm.code IN ({','.join('?' * len(codes))})
                          ORDER BY sm.code, c.name, ac.ability_id''', codes).fetchall()
    payload = {'frozen_utc': now(), 'sets': codes, 'versions': {'semantics': sm.SEMANTICS_VERSION},
               'note': 'Frozen before any ruling for these sets was read by validation.py.',
               'contracts': [{'set': s, 'card': n, 'ability_id': a, 'contract': json.loads(c)} for s, n, a, c in rows]}
    path = os.path.join(outdir, f"heldout_{'_'.join(codes)}_predictions.json")
    blob = json.dumps(payload, sort_keys=True, indent=0)
    open(path, 'w').write(blob)
    h = hashlib.sha256(blob.encode()).hexdigest()
    db.execute('INSERT INTO frozen_prediction VALUES(?,?,?,?,?)', (','.join(codes), h, payload['frozen_utc'],
                                                                   os.path.relpath(path, HERE), len(rows)))
    return h, len(rows), path


def ingest_rulings(db, path):
    fsha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    t = now()
    n_new = 0
    have = {r[0] for r in db.execute('SELECT ruling_sha FROM ruling')}
    rows = []
    for line in gzip.open(path, 'rt', encoding='utf-8'):
        r = json.loads(line)
        h = rsha(r['oracle_id'], r['source'], r['published_at'], r['comment'])
        if h in have:
            continue
        have.add(h)
        rows.append((h, r['oracle_id'], r['source'], r['published_at'], r['comment'], os.path.basename(path), fsha, t))
        n_new += 1
    db.executemany('INSERT INTO ruling VALUES(?,?,?,?,?,?,?,?)', rows)
    return n_new, fsha


def build_macros(db):
    """Read each mechanic's expansion from its printed reminder text (numbers generalised to N). The most common
    wording becomes the proposed expansion; every wording is kept in provenance."""
    out = {}
    for mech, macro in MECHANICS.items():
        texts = collections.Counter()
        example = {}
        for name, rj in db.execute('''SELECT c.name, a.reminders_json FROM ability a JOIN card c USING(oracle_id)
                                      WHERE (a.keyword = ? OR a.text LIKE ?) AND a.reminders_json != '[]' ''',
                                   (mech, f'%{mech}%')):
            for r in json.loads(rj or '[]'):
                r = r.strip('() ')
                if not r:
                    continue
                norm = re.sub(r'\{[0-9WUBRGC/]+\}(?:\{[0-9WUBRGC/]+\})*', '{COST}', r)
                norm = re.sub(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b(?= \+1/\+1)', 'N', norm)
                norm = re.sub(r'\b(?:He|She|It|They)\b', 'It', norm)
                norm = re.sub(r'at \d+\+', 'at N+', norm)
                texts[norm] += 1
                example.setdefault(norm, name)
        if not texts:
            continue
        tmpl, n = texts.most_common(1)[0]
        parse = tmpl.replace('{COST}', '{2}{B}').replace('N +1/+1', 'two +1/+1').replace('at N+', 'at 7+')
        cons = sm.contracts_from_text(parse, example[tmpl], 'Artifact Creature — Spacecraft', 'sentences')
        prov = {'wordings': texts.most_common(), 'parsed_as': parse, 'source': 'printed reminder text'}
        db.execute('INSERT INTO macro_expansion VALUES(?,?,?,?,?,?,?)', (macro, tmpl, sum(texts.values()), example[tmpl],
                                                                         json.dumps(cons, sort_keys=True), json.dumps(prov),
                                                                         'proposed'))
        out[macro] = cons
    return out


def scope_rulings(db, set_oids):
    by_text = collections.defaultdict(set)
    rows = db.execute(f'''SELECT ruling_sha, oracle_id, comment FROM ruling WHERE oracle_id IN ({','.join('?' * len(set_oids))})''',
                      list(set_oids)).fetchall()
    for h, oid, txt in rows:
        by_text[txt].add(oid)
    for h, oid, txt in rows:
        mech = [m for m in MECHANICS if re.search(r'\b' + m, txt, re.I)]
        n = len(by_text[txt])
        scope = 'mechanic' if mech and n >= 2 else 'card'
        db.execute('INSERT INTO ruling_scope VALUES(?,?,?,?)', (h, scope, ','.join(mech) or None, n))
    return rows


# ------------------------------------------------------------------ predicates

def all_results(c):
    return [h for rel, hs in c.get('result', {}).items() if rel != 'rewrites' for h in hs]


def groups(c, cls=None):
    return [g for g in c.get('initiation', {}).get('requirement_groups', []) if cls is None or g['class'] == cls]


def q_sub(want, have):
    for k, v in (want or {}).items():
        hv = have.get(k)
        if isinstance(v, list):
            if not hv or not set(v) <= set(hv if isinstance(hv, list) else [hv]):
                return False
        elif hv != v:
            return False
    return True


def arg_qs(h):
    out = []
    for a in h.get('args', {}).values():
        if isinstance(a, dict):
            out.append(a.get('q', {}))
    return out


def uses_macro(c, macro):
    return any(k['macro'] == macro for k in c.get('keywords', []))


def eval_macro_pred(pred, args, exp):
    """exp: the macro's expansion contracts. Returns (outcome, detail)."""
    if not exp:
        return 'not_representable', 'no expansion read for this macro'
    res = [h for c in exp for h in all_results(c)]
    if pred == 'macro_result_includes':
        for h in res:
            if args.get('hook') and h.get('hook') != args['hook']:
                continue
            if args.get('concept') and h.get('concept') != args['concept']:
                continue
            if args.get('q') and not any(q_sub(args['q'], q) for q in arg_qs(h)):
                continue
            if args.get('status'):
                if not all(s in json.dumps(h) for s in args['status']):
                    return 'not_representable', f"{h.get('concept')} found but entry status {args['status']} is not carried"
            return 'pass', f"{h.get('concept')} [{h.get('hook')}]"
        return 'fail', f"no result {args} in expansion; results: {[h.get('concept') for h in res]}"
    if pred == 'macro_result_excludes':
        for h in res:
            if args.get('hook') and h.get('hook') == args['hook']:
                return 'fail', f"expansion produces {args['hook']}"
            if args.get('concept') and h.get('concept') == args['concept'] and args.get('q_key'):
                if any(args['q_key'] in q for q in arg_qs(h)):
                    return 'fail', f"{args['concept']} carries {args['q_key']}"
        return 'pass', 'not produced'
    if pred == 'macro_trigger_alternatives_exact':
        for c in exp:
            for g in groups(c, 'trigger'):
                hooks = sorted(a.get('hook') for a in g['alternatives'])
                if hooks == sorted(args['hooks']):
                    if args.get('then') and not any(h.get('hook') == args['then'] for h in all_results(c)):
                        return 'fail', f"trigger right, but result is {[h.get('hook') for h in all_results(c)]}"
                    return 'pass', f'alternatives {hooks}'
                return 'fail', f'alternatives {hooks}, expected {sorted(args["hooks"])}'
        return 'fail', 'no delayed trigger in expansion'
    if pred == 'macro_trigger_alternatives_exclude':
        for c in exp:
            for g in groups(c, 'trigger'):
                bad = [a.get('hook') for a in g['alternatives'] if a.get('hook') in args['hooks']]
                if bad:
                    return 'fail', f'observes {bad}'
        return 'pass', 'no generic departure observed'
    if pred == 'macro_cost_includes':
        for c in exp:
            for g in groups(c, 'cost'):
                if g.get('concept') == args['concept'] and (not args.get('q') or any(q_sub(args['q'], q) for q in arg_qs(g))):
                    return 'pass', g['concept']
        return 'fail', f"costs in expansion: {[g.get('concept') for c in exp for g in groups(c, 'cost')]}"
    if pred == 'macro_amplifier':
        if any(a['concept'] == args['concept'] for c in exp for a in c.get('initiation', {}).get('amplifiers', [])):
            return 'pass', args['concept']
        return 'fail', 'no such amplifier'
    if pred == 'macro_timing_speed':
        sp = [c.get('initiation', {}).get('timing', {}).get('speed') for c in exp]
        if args['speed'] in sp:
            return 'pass', 'sorcery'
        # the restriction can be read as its own sentence of the expansion
        if any(t.get('concept') == 'time.sorcery_speed' for c in exp for t in c.get('initiation', {}).get('timing', {}).get('terms', [])):
            return 'pass', 'sorcery (separate sentence)'
        return 'fail', f'speeds {sp}'
    if pred == 'macro_text_window':
        txt = json.dumps(exp)
        if args['pattern'] in txt and any(t.get('concept') for c in exp for t in c.get('initiation', {}).get('timing', {}).get('terms', [])):
            return 'pass', 'window term present'
        if args['pattern'] in txt:
            return 'not_representable', 'the window is only inside unread text'
        return 'fail', 'no window'
    if pred == 'has_target':
        for c in exp:
            for g in groups(c, 'eligibility'):
                if q_sub(args.get('q'), g.get('q', {})):
                    return 'pass', g.get('target')
        return 'fail', 'expansion has no matching target'
    if pred == 'target_excludes':
        for c in exp:
            for g in groups(c, 'eligibility'):
                v = g.get('q', {}).get(args['q_key'], [])
                if args['value'] in (v if isinstance(v, list) else [v]):
                    return 'fail', f"target excludes {args['value']}"
        return 'pass', 'not excluded'
    return None, None


def evaluate(db, exps, set_oids, outdir):
    rows = []
    claims = []
    rulings = {txt: (h, oid) for h, oid, txt in db.execute(
        f"SELECT ruling_sha, oracle_id, comment FROM ruling WHERE oracle_id IN ({','.join('?' * len(set_oids))})", list(set_oids))}
    allc = contracts_by_card(db, '1=1')
    names = dict(db.execute('SELECT oracle_id, name FROM card'))
    fsem = {fid: json.loads(u) for fid, u in db.execute('SELECT frame_id, units_json FROM frame_semantics')}
    owned = {r[0] for r in db.execute('SELECT oracle_id FROM card WHERE in_collection=1')}
    frames_by = collections.defaultdict(list)
    for fid, role, ft in db.execute('SELECT frame_id, role, frame_text FROM frame'):
        frames_by[role].append((fid, ft))
    edges = collections.defaultdict(set)
    for fid, cid in db.execute('SELECT frame_id, concept_id FROM frame_concept_edge'):
        edges[fid].add(cid)
    # --- curated
    for cl in CURATED:
        hits = [t for t in rulings if cl['ruling'] in t]
        rs = rulings[hits[0]][0] if hits else None
        claims.append((cl['id'], rs, hits[0] if hits else None, cl['mechanic'], cl['scope'][0], cl['scope'][1], cl['polarity'],
                       cl['predicate'], json.dumps(cl['args']), 'claude-curated', cl['note'], 'proposed'))
        kind, ref = cl['scope']
        if cl['predicate'] == 'not_representable':
            rows.append((cl['id'], None, None, 'not_representable', cl['args']['reason']))
            continue
        if kind == 'macro':
            exp = exps.get(ref)
            if cl['predicate'] == 'has_target':
                # every ability that uses the macro: target either printed or supplied by the expansion
                mo, md = eval_macro_pred('has_target', cl['args'], exp)
                for oid, abs_ in allc.items():
                    for aid, c in abs_:
                        if uses_macro(c, ref):
                            own = [g for g in groups(c, 'eligibility') if g.get('via_macro') == ref or q_sub(cl['args'].get('q'), g.get('q', {}))]
                            out = 'pass' if own or mo == 'pass' else 'fail'
                            rows.append((cl['id'], oid, aid, out, 'printed target' if own else md))
                continue
            o, d = eval_macro_pred(cl['predicate'], cl['args'], exp)
            if cl['polarity'] == 'negative' and cl['predicate'] in ('macro_result_includes',):
                o = {'pass': 'fail', 'fail': 'pass'}.get(o, o)
            # a macro claim applies to every ability using the macro
            n = 0
            for oid, abs_ in allc.items():
                for aid, c in abs_:
                    if uses_macro(c, ref):
                        rows.append((cl['id'], oid, aid, o, d))
                        n += 1
            if not n:
                rows.append((cl['id'], None, None, o, d))
        elif kind == 'frame':
            rx = re.compile(ref)
            role = cl['args'].get('role')
            matched = [(fid, ft) for r_, fl in frames_by.items() if not role or r_ == role for fid, ft in fl if rx.search(ft)]
            for fid, ft in matched:
                has = cl['args']['concept'] in edges[fid]
                # in a coordinated trigger, judge only the alternative the pattern is about
                alts = [a for u in fsem.get(fid, []) if u['unit'] == 'requirement_group' for a in u['alternatives']]
                if len(alts) > 1:
                    hit = [a for a in alts if rx.search(a.get('text') or '')]
                    if hit:
                        has = any(a['concept'] == cl['args']['concept'] for a in hit)
                ok = has if cl['polarity'] == 'positive' else not has
                for oid, aid in db.execute('''SELECT a.oracle_id, a.ability_id FROM part p JOIN ability a USING(ability_id)
                                              WHERE p.frame_id=? ''', (fid,)):
                    rows.append((cl['id'], oid, aid, 'pass' if ok else 'fail', f'template {fid}: {ft} -> {sorted(edges[fid])}'))
        elif kind == 'striations':
            for oid, abs_ in allc.items():
                txt = ' '.join(c['evidence']['oracle_text'] for _, c in abs_)
                if not any(uses_macro(c, ref) for _, c in abs_):
                    continue
                face = db.execute('SELECT group_concat(oracle_text, char(10)) FROM face WHERE oracle_id=?', (oid,)).fetchone()[0] or ''
                lines = re.findall(r'^(\d+)\+ \|', face, re.M)
                conds = []
                for aid, c in abs_:
                    for g in groups(c):
                        if g.get('concept') == 'st.counter_threshold':
                            conds.append((aid, g))
                if cl['predicate'] == 'striation_condition':
                    found = {next((a['value'] for a in g['args'].values() if a.get('slot') == 'n'), None) for _, g in conds}
                    kinds = {next((a['q'].get('counter_kind') for a in g['args'].values() if a.get('slot') == 'counter'), None) for _, g in conds}
                    ok = set(lines) <= found and kinds <= {'charge'} and lines
                    rows.append((cl['id'], oid, None, 'pass' if ok else 'fail',
                                 f'striations {lines}, conditions {sorted(x for x in found if x)}, counter kinds {sorted(k for k in kinds if k)}'))
                else:
                    bad = [g for _, g in conds if g['class'] != 'state']
                    rows.append((cl['id'], oid, None, 'pass' if conds and not bad else ('fail' if conds else 'fail'),
                                 f'{len(conds)} threshold conditions, classes {sorted({g["class"] for _, g in conds})}'))
    # --- patterns, on every set ruling (card scope)
    for txt, (h, oid) in rulings.items():
        for pid, rx, pred, args in PATTERNS:
            m = rx.search(txt)
            if not m:
                continue
            cid = f'{pid}:{h[:12]}'
            a = dict(args)
            if pred == 'act_in':
                a['act'] = ACTS[m.group(1).lower()]
            claims.append((cid, h, txt, None, 'card', oid, 'positive', pred, json.dumps(a), pid, '', 'proposed'))
            abs_ = [(aid, c) for aid, c in allc.get(oid, []) if c['kind'] != 'keyword_macro']
            if not abs_:
                rows.append((cid, oid, None, 'not_representable', 'no contract for this card'))
                continue
            if pred == 'capacity':
                ok = any(t['concept'].startswith('cap.') for _, c in abs_ for t in c.get('initiation', {}).get('timing', {}).get('terms', []))
                ordn = any(a.get('ordinal_condition') for _, c in abs_ for g in groups(c, 'trigger') for a in g['alternatives'])
                rows.append((cid, oid, None, 'pass' if ok or ordn else 'fail',
                             'capacity term' if ok else 'ordinal condition (once per turn)' if ordn else 'no capacity term on any ability'))
            elif pred == 'is_mana_ability':
                mana = [(aid, c) for aid, c in abs_ if any(r.get('concept') == 'op.mana.add' for r in all_results(c))]
                if not mana:
                    rows.append((cid, oid, None, 'ambiguous', 'no ability adds mana'))
                    continue
                def is_ma(c):
                    return bool(c.get('mana_ability'))
                vals = {is_ma(c) for _, c in mana}
                if len(vals) > 1:
                    rows.append((cid, oid, None, 'ambiguous', 'several mana abilities disagree'))
                else:
                    rows.append((cid, oid, None, 'pass' if vals == {a['value']} else 'fail', f'mana ability: {vals.pop()}'))
            elif pred == 'card_has_target':
                subj = txt[:m.start()].strip()
                nm = (names.get(oid) or '').split(',')[0].split(' //')[0]
                if not re.search(r"\b(?:this|that|its|the) (?:\w+ )?(?:spell|ability)\b|\bability\b|^" + re.escape(nm), subj, re.I):
                    rows.append((cid, oid, None, 'ambiguous', f'subject "{subj[-60:]}" is not this card or one of its abilities'))
                elif len(abs_) > 1:
                    rows.append((cid, oid, None, 'ambiguous', f'{len(abs_)} abilities; the ruling does not say which'))
                else:
                    has = bool(groups(abs_[0][1], 'eligibility'))
                    rows.append((cid, oid, abs_[0][0], 'pass' if has == a['value'] else 'fail', f'has target: {has}'))
            elif pred == 'act_in':
                fam = a['act']
                inc = [(aid, c) for aid, c in abs_ if any(g.get('family') == fam for g in groups(c, 'cost'))]
                inr = [(aid, c) for aid, c in abs_ if any(fam.split('_')[0] in (r.get('concept') or '') for r in all_results(c))]
                if a['where'] == 'cost':
                    o = 'pass' if inc else ('fail' if inr else 'not_representable')
                else:
                    o = 'pass' if inr and not inc else ('fail' if inc and not inr else ('ambiguous' if inc and inr else 'not_representable'))
                rows.append((cid, oid, None, o, f'{fam}: in cost {len(inc)}, in result {len(inr)}'))
    db.executemany('INSERT INTO claim VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', claims)
    db.executemany('INSERT INTO test_result VALUES(?,?,?,?,?)', rows)
    return claims, rows, names, owned


def ruling_statuses(db, set_oids):
    res = collections.defaultdict(list)
    for cid, rs, outcome in db.execute('SELECT c.claim_id, c.ruling_sha, t.outcome FROM claim c JOIN test_result t USING(claim_id)'):
        res[rs].append(outcome)
    out = collections.Counter()
    for h, oid, txt, date in db.execute(f"SELECT ruling_sha, oracle_id, comment, published_at FROM ruling WHERE oracle_id IN ({','.join('?' * len(set_oids))})",
                                        list(set_oids)):
        oc = res.get(h, [])
        if not oc:
            st = 'unconverted'
        elif 'fail' in oc:
            st = 'contradiction'
        elif all(o == 'pass' for o in oc):
            st = 'confirmed'
        elif 'pass' in oc and all(o in ('pass', 'ambiguous') for o in oc):
            st = 'confirmed'
        elif all(o == 'ambiguous' for o in oc):
            st = 'ambiguous'
        else:
            st = 'insufficient_representation'
        outdated = int(bool(OUTDATED.search(txt)) and (date or '') < '2024-11-08')
        db.execute('INSERT INTO ruling_status VALUES(?,?,?,?,?)', (h, oid, st, outdated, ','.join(sorted(set(oc)))))
        out[st] += 1
    return out


def families(db, codes, first_seen):
    for code in codes:
        oids = [r[0] for r in db.execute('SELECT oracle_id FROM set_member WHERE code=?', (code,))]
        q = ','.join('?' * len(oids))
        fam = collections.defaultdict(lambda: {'cards': set(), 'abilities': set(), 'frames': collections.Counter(), 'kind': None})
        for oid, aid, kw, aw in db.execute(f'SELECT oracle_id, ability_id, keyword, ability_word FROM ability WHERE oracle_id IN ({q})', oids):
            if kw:
                f = fam[kw.lower()]
                f['kind'] = 'keyword_ability'
                f['cards'].add(oid)
                f['abilities'].add(aid)
            if aw:
                f = fam[aw.lower()]
                f['kind'] = 'ability_word'
                f['cards'].add(oid)
                f['abilities'].add(aid)
        for oid, aid, fid, ft, comp, cid in db.execute(f'''SELECT a.oracle_id, a.ability_id, p.frame_id, f.frame_text, f.completeness, e.concept_id
                                                           FROM part p JOIN ability a USING(ability_id) JOIN frame f USING(frame_id)
                                                           JOIN frame_concept_edge e ON e.frame_id=p.frame_id
                                                           WHERE a.oracle_id IN ({q}) AND (e.concept_id LIKE 'kwa.%' OR e.concept_id LIKE 'kw.%')''', oids):
            m = cid.split('.', 1)[1].replace('_', ' ')
            f = fam[m]
            f['kind'] = f['kind'] or ('keyword_action' if cid.startswith('kwa.') else 'keyword_ability')
            f['cards'].add(oid)
            f['abilities'].add(aid)
            f['frames'][(ft, comp)] += 1
        rel = db.execute('SELECT released_at FROM set_info WHERE code=?', (code,)).fetchone()[0]
        for m, f in fam.items():
            fs = first_seen.get(m)
            status = None
            if fs:
                status = 'introduced' if fs[:7] >= (rel or '')[:7] else 'returning'
            db.execute('INSERT INTO mechanic_family VALUES(?,?,?,?,?,?,?,?,?,?)', (
                code, m, f['kind'], len(f['cards']), len(f['abilities']), len(f['frames']),
                sum(1 for (ft, c) in f['frames'] if c == 'complete'), fs, status,
                json.dumps([{'template': ft, 'completeness': c, 'n': n} for (ft, c), n in f['frames'].most_common(12)])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('db')
    ap.add_argument('--rulings', required=True)
    ap.add_argument('--sets', nargs='+', required=True)
    ap.add_argument('--heldout', nargs='*', default=[])
    ap.add_argument('--setdir', default=os.path.join(HERE, 'data', 'sets'))
    ap.add_argument('--out', default=os.path.join(HERE, 'validation'))
    ap.add_argument('--frozen', help='an earlier freeze of the held-out sets; recorded as is, never rewritten, '
                                     'because a freeze made after the rulings were read is not a held-out test')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    db = sqlite3.connect(a.db)
    db.executescript(SCHEMA)
    load_sets(db, a.sets, a.heldout, a.setdir)
    n = sm.install_contracts(db, where='c.in_collection = 1 OR c.oracle_id IN (SELECT oracle_id FROM set_member)')
    report = {'version': VALIDATION_VERSION, 'run_utc': now(), 'contracts': n}
    if a.heldout and a.frozen:
        blob = open(a.frozen).read()
        p = json.loads(blob)
        h, k, path = hashlib.sha256(blob.encode()).hexdigest(), len(p['contracts']), a.frozen
        db.execute('INSERT INTO frozen_prediction VALUES(?,?,?,?,?)', (','.join(a.heldout), h, p['frozen_utc'],
                                                                       os.path.relpath(path, HERE), k))
        report['heldout_frozen'] = {'sets': a.heldout, 'sha256': h, 'contracts': k, 'path': os.path.relpath(path, HERE),
                                    'reused': True}
    elif a.heldout:
        h, k, path = freeze(db, a.heldout, a.out)
        report['heldout_frozen'] = {'sets': a.heldout, 'sha256': h, 'contracts': k, 'path': os.path.relpath(path, HERE)}
    db.commit()
    new, fsha = ingest_rulings(db, a.rulings)
    report['rulings_ingested_new'] = new
    report['rulings_bulk'] = {'file': os.path.basename(a.rulings), 'sha256': fsha}
    exps = build_macros(db)
    report['macros'] = {m: len(c) for m, c in exps.items()}
    set_oids = {r[0] for r in db.execute('SELECT oracle_id FROM set_member')}
    scope_rulings(db, set_oids)
    claims, rows, names, owned = evaluate(db, exps, set_oids, a.out)
    report['ruling_status'] = dict(ruling_statuses(db, set_oids))
    fs_path = os.path.join(a.setdir, 'keyword_first_seen.json')
    first_seen = json.load(open(fs_path)) if os.path.exists(fs_path) else {}
    families(db, a.sets + a.heldout, first_seen)
    db.commit()
    print(json.dumps(report, indent=1))
    json.dump(report, open(os.path.join(a.out, 'validation_run.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
