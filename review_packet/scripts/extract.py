"""Mechanics extraction pass 2026-10-24: Oracle text -> Mechanics · Operations candidate rows, for owned cards with no
operations. Segmentation and hooks come from the grammar layer (grammar 0.2.0 / semantics 0.1.1); the row format
follows the 2026-10-11 extraction. Every row is a candidate, never verified."""
import sqlite3, json, re, urllib.parse, collections, csv, openpyxl
KB = sqlite3.connect('file:/mnt/project-files/mechanics-kernel/sqlite-kb/mtg_cards_v0.2.sqlite?mode=ro', uri=True)
GL = sqlite3.connect('gl_scratch.sqlite')
wb = openpyxl.load_workbook('../kb/canonical_20261024c.xlsx', read_only=True, data_only=True)
coll = {r[0]: r for r in ([list(x) + [None] * 25 for x in wb['Collection'].values][4:]) if r[0]}
units = {r[1] for r in ([list(x) for x in wb['Mechanics · Units'].values][1:]) if r[1]}
targets = json.load(open('targets.json'))
VOCAB = {r[0] for r in list(wb['Mechanics · Hook Economy'].values)[1:] if r[0]}
NOTE = 'Grammar-layer extraction 2026-10-24 (grammar 0.2.0 / semantics 0.1.1); candidate only, not rules-verified'
KIND = {'triggered': 'trigger', 'chapter': 'trigger', 'activated': 'activate', 'loyalty': 'activate', 'spell': 'spell_effect',
        'additional_cost': 'spell_effect', 'static': 'continuous', 'replacement': 'replacement', 'mode': 'choice_mode'}
TRIG_MAP = {'turn.step.begin': 'timing.step_begin', 'turn.phase.begin': 'timing.step_begin'}


def zone_dest(r):
    s = json.dumps(r.get('args', {})).lower()
    if '"battlefield"' in s: return 'card.return_to_battlefield'
    if '"hand"' in s: return 'card.return_to_hand'
    if '"exile"' in s: return 'exile.enter'
    return None


clause_ctx = ['']


def produced(con):
    out = []
    res = con.get('result', {})
    for rel in ('produces', 'transforms', 'permits'):
        for r in res.get(rel, []):
            h = r.get('hook')
            if h == 'zone.enter': h = zone_dest(r)
            if h in ('card.return_to_battlefield', 'card.return_to_hand') and 'return' not in json.dumps(r).lower() and 'return' not in clause_ctx[0].lower(): continue
            if h == 'permanent.tapped_for_mana': continue
            if h in VOCAB and h not in out: out.append(h)
    return out


def trig_hooks(con, clause):
    hs = []
    for g in con['initiation'].get('requirement_groups', []):
        if g['class'] != 'trigger': continue
        for a in g['alternatives']:
            h = TRIG_MAP.get(a.get('hook'), a.get('hook'))
            if h == 'battlefield.enter' and re.search(r'\bland(s)? (you control )?enters?\b|\blandfall\b', (a.get('text') or '') + ' ' + clause, re.I) and not re.search(r'^when(ever)? (this|~)', clause, re.I):
                h = 'land.enters_battlefield'
            if h == 'zone.enter' and 'battlefield' in json.dumps(a): h = 'battlefield.enter'
            if h in VOCAB and h not in hs: hs.append(h)
    return hs


def qualifiers(cl):
    low = re.sub(r'\([^)]*\)', '', cl).lower(); q = []
    if re.search(r'\btarget\b|\bmay\b|\bif\b|\bchoose\b|\bunless\b|\bwhere\b|•', low): q.append('conditional/choice/target')
    if re.search(r'you control', low): q.append('controller: you')
    if re.search(r'until end of turn|this turn', low): q.append('turn scoped')
    if re.search(r'\bnontoken\b', low): q.append('nontoken')
    elif re.search(r'\btokens?\b', low): q.append('token')
    if re.search(r'\bhand\b', low): q.append('hand')
    if re.search(r'\b(other|another)\b', low): q.append('other/another')
    if re.search(r'opponent', low): q.append('opponent')
    if re.search(r'\b(destroy|sacrifice|dies|die)\b', low): q.append('death/destination facets conditional')
    if re.search(r'graveyard', low): q.append('graveyard')
    if re.search(r'\bexile', low): q.append('exile')
    return '; '.join(q)


def transition(prods, cl):
    low = cl.lower()
    if 'permanent.transform' in prods or re.search(r'\btransform\b', low): return 'same object transforms'
    if re.search(r'becomes? a copy', low): return 'same object becomes copy'
    if 'card.return_to_battlefield' in prods: return 'new object; no cast inferred'
    if 'card.return_to_hand' in prods and re.search(r'return .*to (its|their) owner', low): return 'departure to hand; recast separate'
    return ''


FALLBACK = [(r'\bcounters? on\b', 'counter.put'), (r'\bdraws? (a|two|three|\w+) cards?\b', 'card.draw'), (r'\bcreate\b', 'token.create'),
            (r'\bdeals? [\w ]*damage\b', 'damage.deal'), (r'\bgains? (\d+|x|that much) life\b', 'life.gain'), (r'\bdestroy\b', 'permanent.destroy'),
            (r'\bexile\b', 'exile.enter'), (r'\badd \{', 'mana.add'), (r'search (your|their) library', 'card.search'),
            (r'\bsacrifices?\b', 'permanent.sacrifice'), (r"return [^.]* to (its owner's|your|their owner's|their) hand", 'card.return_to_hand'),
            (r'return [^.]* to the battlefield', 'card.return_to_battlefield'), (r'\bmills?\b', 'card.mill'), (r'\bdiscards?\b', 'card.discard'),
            (r'\buntap\b', 'permanent.untap'), (r'\btap (target|up to)', 'permanent.tap'), (r'\bloses? (\d+|x) life\b', 'life.lose'),
            (r'\bshuffle', 'library.shuffle'), (r'counter target [^.]*spell', 'spell.countered'), (r'\bscry\b', 'library.scry')]


def fallback_produced(cl):
    low = re.sub(r'\([^)]*\)|"[^"]*"', '', cl).lower()
    low = low.split(':', 1)[1] if re.match(r'[^:"]+:', low) else low
    return [h for p, h in FALLBACK if re.search(p, low)]


def raw_lines(oid):
    faces = GL.execute('select face_index, oracle_text from face where oracle_id=? order by face_index', (oid,)).fetchall()
    return {f: (t or '').split('\n') for f, t in faces}, len(faces)


rows, units_new, units_upd, skipped = [], [], [], collections.Counter()
for name, oid in sorted(targets.items(), key=lambda kv: kv[0].lower()):
    lines, nfaces = raw_lines(oid)
    abil = GL.execute('''select a.ability_id, a.face_index, a.line_index, a.ordinal, a.kind, a.text, a.parent_ability, a.granted_by,
                         a.completeness, ac.contract_json from ability a left join ability_contract ac using(ability_id)
                         where a.oracle_id=? order by a.face_index, a.line_index, a.ordinal''', (oid,)).fetchall()
    # the op number counts Oracle lines across faces, as in the 2026-10-11 extraction (1-based)
    offset, base = {}, 0
    for f in sorted(lines):
        offset[f] = base; base += len(lines[f])
    used = collections.Counter(); card_rows = []
    for aid, fi, li, ordi, kind, text, parent, granted, comp, cj in abil:
        if kind == 'keyword' and re.match(r'exhaust — [^:]+:', text or '', re.I): kind = 'activated'  # as in the 10-11 extraction
        if kind in ('keyword', 'reminder_only', 'structure'): skipped[kind] += 1; continue
        if granted is not None: skipped['granted (quoted) ability'] += 1; continue
        if kind == 'replacement' and re.fullmatch(r'(This|~) [\w ]*enters tapped\.', text or ''): skipped['unconditional enters tapped'] += 1; continue
        if kind not in KIND: skipped['kind ' + kind] += 1; continue
        con = json.loads(cj) if cj else {'initiation': {}, 'result': {}}
        clause = lines[fi][li] if li < len(lines[fi]) else text
        if used[(fi, li)]:
            if re.match(r'\d+\+ \|', clause): skipped['station line continuation'] += 1; continue
            clause = text  # several abilities on one Oracle line
        used[(fi, li)] += 1
        n = offset[fi] + li + 1
        opid = f"card.{urllib.parse.quote(name)}.op{n:03d}" + ('' if used[(fi, li)] == 1 else chr(96 + used[(fi, li)]))
        k = KIND[kind]
        clause_ctx[0] = clause
        prods = produced(con)
        fb = False
        if not prods and not con.get('result') and k in ('trigger', 'activate', 'spell_effect', 'choice_mode'):
            prods = fallback_produced(clause); fb = bool(prods)
        hook, req, timing, pay = '', '', '', ''
        if k == 'trigger':
            m = re.match(r'(?:[A-Z][\w\' -]+ — )?(When|Whenever|At)\b(.*?),', clause)
            hs = trig_hooks(con, clause)
            if m and m.group(1) == 'At':
                req = timing = 'timing: ' + (m.group(1) + m.group(2)).strip()
                hs = ['timing.step_begin']
            else:
                req = 'event: ' + (m.group(2).strip() if m else '(unread)')
                timing = 'on observed event'
            hook = '; '.join(hs)
        elif k == 'activate':
            m = re.match(r'(?:[A-Z][\w\' -]+ — )?([^:"]+):', clause)
            pay = m.group(1).strip() if m else ''
            req = ' AND '.join('cost: ' + c.strip() for c in re.split(r',\s*(?![^{]*\})', pay) if c.strip()) if pay else ''
            timing = 'loyalty activation; sorcery speed, once per turn' if kind == 'loyalty' else 'activation window; verify'
        elif kind == 'additional_cost':
            req, pay = 'additional cost paid as the spell is cast', clause; prods = []; fb = False
        elif k == 'spell_effect':
            hook, req = 'spell.resolve', 'spell or granted-effect resolution'
        elif k == 'choice_mode':
            req = 'selected mode in enclosing operation'
        elif k == 'replacement':
            req = 'entry checkpoint' if re.search(r'\benters?\b', clause, re.I) else 'proposed event: ' + clause[:140]
            if re.search(r'\benters?\b', clause, re.I): hook = 'battlefield.enter'
        mods = 'modifies; inspect clause' if con.get('result', {}).get('modifies') or con.get('result', {}).get('rewrites') else ''
        unread = con.get('unread', [])
        status = 'extracted_candidate' if comp == 'complete' else 'requires_manual_annotation'
        station = bool(re.match(r'\d+\+ \|', clause))
        if station or kind == 'additional_cost': status = 'requires_manual_annotation'
        low = station or kind == 'additional_cost' or (k == 'trigger' and not hook) or comp != 'complete' or nfaces > 1 or k in ('replacement', 'choice_mode') or bool(unread) or \
            bool(re.search(r'\b(if|unless|instead|as long as|for each|where x)\b', clause, re.I))
        note = NOTE + ('' if comp == 'complete' else f' | grammar parse {comp}: {len(unread)} unread part(s)')
        if fb: note += ' | Result Produces read from text patterns (grammar contract has no result)'
        if station: note += ' | station threshold line: the abilities apply once the permanent has that many charge counters'
        if name in ('Finch Formation', 'Rust-Shield Rampager', 'Thornplate Intimidator'):
            note += ' | Sheet row points at the token printing; extracted from Oracle card text (identity unconfirmed)'
        row = [opid, name, 'multi-face; inspect face' if nfaces > 1 else 'single/shared', k, clause, hook, req, '',
               '; '.join(prods), pay, mods, timing, qualifiers(clause), transition(prods, clause), status,
               'low' if low else 'medium', coll[name][22] or '', note]
        row = [r for r in row]
        card_rows.append((row, comp, con, aid, kind))
    rows += card_rows
    c = coll[name]
    nlow = sum(1 for r, *_ in card_rows if r[15] == 'low')
    if name in units:
        units_upd.append((name, len(card_rows), nlow))
    else:
        url = c[22] or ''
        units_new.append([f"card.{urllib.parse.quote(name)}", name, 'card', c[10], c[1], c[3], url,
                          'Text present' if c[13] else 'No text', 'printing link present' if '/card/' in url else 'name reference; printing unverified',
                          len(card_rows), nlow, 'Operation count obtainable from Operations; candidate index, not verified', 'mtg-dio 3.1.1'])
ids = [r[0][0] for r in rows]
assert len(ids) == len(set(ids)), [i for i, n in collections.Counter(ids).items() if n > 1]
json.dump({'ops': [r[0] for r in rows], 'meta': [{'comp': r[1], 'ability_id': r[3], 'gkind': r[4], 'contract': r[2]} for r in rows],
           'units_new': units_new, 'units_upd': units_upd}, open('extraction.json', 'w'), ensure_ascii=False)
C = collections.Counter
print('ops', len(rows), 'cards with ops', len({r[0][1] for r in rows}), 'of', len(targets))
print('units new', len(units_new), 'upd', len(units_upd), 'skipped', dict(skipped))
print(C(r[0][3] for r in rows), C((r[0][14], r[0][15]) for r in rows))
print('zero-op cards', sum(1 for n in targets if n not in {r[0][1] for r in rows}))
