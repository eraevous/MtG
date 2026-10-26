"""Export the reviewable templates, one row per whole construction, and apply a reviewed copy back.

    python3 -I review.py export grammar_layer.sqlite out_dir/          # writes template_review_*.csv
    python3 -I review.py apply  grammar_layer.sqlite reviewed.csv --reviewer Zach

One CSV row is one template with its complete composed semantics (frame_semantics): the trigger group with all
its alternatives, a replacement as one operation (proposed event -> resulting event), each result with its
relation and hook, and which slot fills which argument. A reviewer approves the construction as a whole, not
loose edges, so a coordinated trigger cannot be approved while one of its events is missing.

Columns you edit:
  verdict              approve | reject | fix | (blank = not reviewed)
  corrected_concepts   with fix: the full corrected edge set, space separated, each concept_id[:RELATION]
                       e.g. "ev.battlefield.enter:OBSERVES ev.attacker.declared:OBSERVES"
  note                 free text

Flags (context, not editable):
  addendum_dependent   the construction uses a concept whose DIO side waits on A1-A7 (dio_status addendum_pending)
  unmapped             no concept at all; needs a fix row or a new rule
  partial              words are left over; approving it does not make the template count as reviewed

Apply stores each verdict with the SHA-256 of the template text AND of its composed semantics. If a later grammar
or semantics version changes either, the verdict goes stale instead of carrying over.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import random
import sqlite3
import sys

FIELDS = ['frame_id', 'role', 'template', 'completeness', 'mechanical_class', 'flags', 'corpus_cards',
          'collection_cards', 'semantics', 'concepts', 'dio_status', 'examples', 'semantics_sha', 'verdict',
          'corrected_concepts', 'note']

VIEW = '''
DROP VIEW IF EXISTS effective_review;
CREATE VIEW effective_review AS
  SELECT r.* FROM review r JOIN frame f ON f.frame_id=r.frame_id JOIN frame_semantics s ON s.frame_id=r.frame_id
  WHERE r.frame_text_sha = f.frame_sha AND r.semantics_sha = s.semantics_sha
    AND r.rowid = (SELECT max(r2.rowid) FROM review r2 WHERE r2.frame_id=r.frame_id);
DROP VIEW IF EXISTS effective_frame_review;
CREATE VIEW effective_frame_review AS
  SELECT f.frame_id,
    CASE WHEN f.completeness='complete' AND r.verdict IN ('approve','fix') THEN 1 ELSE 0 END AS frame_ok
  FROM frame f JOIN effective_review r ON r.frame_id=f.frame_id;
'''

CLASSES = [
    ('replacement', lambda c, u: any(x['unit'] == 'operation' for x in u)),
    ('modal', lambda c, u: 'choice.modal' in c),
    ('mana', lambda c, u: 'op.mana.add' in c or 'ev.permanent.tapped_for_mana' in c),
    ('sacrifice', lambda c, u: any(x in c for x in ('cost.sacrifice_self', 'cost.sacrifice_other', 'op.permanent.sacrifice', 'ev.permanent.sacrifice'))),
    ('land_search', lambda c, u: 'op.card.search' in c),
    ('death_trigger', lambda c, u: 'ev.permanent.dies' in c),
    ('enter_trigger', lambda c, u: 'ev.battlefield.enter' in c),
    ('combat_trigger', lambda c, u: any(x in c for x in ('ev.attacker.declared', 'ev.blocker.declared', 'ev.combat.damage'))),
    ('cast_trigger', lambda c, u: any(x in c for x in ('ev.spell.cast', 'ev.spell.copied'))),
    ('step_trigger', lambda c, u: any(x in c for x in ('ev.turn.step.begin', 'ev.turn.phase.begin'))),
    ('tokens', lambda c, u: 'op.token.create' in c),
    ('counters', lambda c, u: any(x in c for x in ('op.counter.put', 'ev.counter.put', 'op.counter.remove'))),
    ('removal', lambda c, u: any(x in c for x in ('op.permanent.destroy', 'op.zone.exile', 'op.damage.deal', 'op.spell.counter'))),
    ('card_flow', lambda c, u: any(x in c for x in ('op.card.draw', 'op.card.discard', 'op.card.mill', 'op.zone.return'))),
    ('life', lambda c, u: any(x in c for x in ('op.life.gain', 'op.life.lose', 'ev.life.gain', 'ev.life.lose'))),
    ('pump_grant', lambda c, u: any(x in c for x in ('op.pt.modify', 'op.pt.set', 'op.ability.grant'))),
    ('keyword', lambda c, u: any(x.startswith(('kw.', 'kwa.')) for x in c)),
    ('cost', lambda c, u: any(x.startswith('cost.') for x in c)),
    ('condition', lambda c, u: any(x.startswith('st.') for x in c)),
]


def mech_class(concepts, units):
    for name, f in CLASSES:
        if f(concepts, units):
            return name
    return 'other' if concepts else 'unmapped'


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def ensure(db):
    cols = [r[1] for r in db.execute('PRAGMA table_info(frame)')]
    if 'frame_sha' not in cols:
        db.execute('ALTER TABLE frame ADD COLUMN frame_sha TEXT')
        db.executemany('UPDATE frame SET frame_sha=? WHERE frame_id=?',
                       [(sha(r + '\t' + t), fid) for fid, r, t in db.execute('SELECT frame_id, role, frame_text FROM frame')])
    rcols = [r[1] for r in db.execute('PRAGMA table_info(review)')]
    if 'semantics_sha' not in rcols:
        db.execute('ALTER TABLE review ADD COLUMN semantics_sha TEXT')
    db.executescript(VIEW)
    db.commit()


def examples(db, fid, k=3):
    rows = db.execute('''SELECT c.name, p.surface, c.in_collection FROM part p JOIN ability a USING(ability_id)
                         JOIN card c USING(oracle_id) WHERE p.frame_id=? GROUP BY c.name
                         ORDER BY c.in_collection DESC, c.name LIMIT ?''',
                      (fid, k)).fetchall()
    return ' || '.join(f'{n}{" [owned]" if o else ""}: {s}' for n, s, o in rows)


def frame_rows(db):
    status = dict(db.execute('SELECT concept_id, dio_status FROM concept'))
    edges = {}
    for fid, cid in db.execute('SELECT frame_id, concept_id FROM frame_concept_edge'):
        edges.setdefault(fid, []).append(cid)
    out = []
    for fid, role, ft, comp, nc, ncc, units, desc, ssha in db.execute(
            '''SELECT f.frame_id, f.role, f.frame_text, f.completeness, f.n_cards, f.n_collection_cards,
                      s.units_json, s.description, s.semantics_sha
               FROM frame f JOIN frame_semantics s USING(frame_id) WHERE f.n_collection_cards > 0
               ORDER BY f.n_collection_parts DESC, f.n_parts DESC'''):
        cs = sorted(set(edges.get(fid, [])))
        u = json.loads(units)
        flags = []
        if not cs:
            flags.append('unmapped')
        if any(status.get(c) == 'addendum_pending' for c in cs):
            flags.append('addendum_dependent')
        if comp != 'complete':
            flags.append(comp)
        ds = sorted({status.get(c, '?') for c in cs})
        out.append({'frame_id': fid, 'role': role, 'template': ft, 'completeness': comp,
                    'mechanical_class': mech_class(cs, u), 'flags': ' '.join(flags), 'corpus_cards': nc,
                    'collection_cards': ncc, 'semantics': desc, 'concepts': ' '.join(cs), 'dio_status': ' '.join(ds),
                    'semantics_sha': ssha})
    return out


def representative(rows, per_class=3):
    """A small review set that covers every mechanical class: the highest-impact complete templates of each
    class, plus one flagged (addendum-dependent, partial or unmapped) template where the class has one."""
    by = {}
    for r in rows:
        by.setdefault(r['mechanical_class'], []).append(r)
    pick = []
    for cls, rs in sorted(by.items()):
        clean = [r for r in rs if not r['flags']]
        flagged = [r for r in rs if r['flags']]
        pick += clean[:per_class]
        if flagged:
            pick.append(flagged[0])
    return sorted(pick, key=lambda r: (r['mechanical_class'], -r['collection_cards']))


def write(path, rows, db):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({**r, 'examples': examples(db, r['frame_id']), 'verdict': '', 'corrected_concepts': '', 'note': ''})


def export(dbpath, outdir):
    db = sqlite3.connect(dbpath)
    ensure(db)
    os.makedirs(outdir, exist_ok=True)
    rows = frame_rows(db)
    paths = []
    for name, sel in (('template_review_sample.csv', representative(rows)),
                      ('template_review_top300.csv', rows[:300]),
                      ('template_review_collection.csv', rows)):
        p = os.path.join(outdir, name)
        write(p, sel, db)
        paths.append(p)
    p = os.path.join(outdir, 'template_inventory_corpus.csv')
    with open(p, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['frame_id', 'role', 'template', 'completeness', 'corpus_parts', 'corpus_cards', 'collection_cards', 'semantics'])
        for r in db.execute('''SELECT f.frame_id, f.role, f.frame_text, f.completeness, f.n_parts, f.n_cards,
                                      f.n_collection_cards, s.description FROM frame f JOIN frame_semantics s USING(frame_id)
                               ORDER BY f.n_parts DESC'''):
            w.writerow(r)
    paths.append(p)
    print('\n'.join(paths))


def apply(dbpath, csvpath, reviewer):
    import semantics as sm
    db = sqlite3.connect(dbpath)
    ensure(db)
    known = {r[0] for r in db.execute('SELECT concept_id FROM concept')}
    shas = dict(db.execute('SELECT frame_id, frame_sha FROM frame'))
    texts = dict(db.execute('SELECT frame_id, frame_text FROM frame'))
    roles = dict(db.execute('SELECT frame_id, role FROM frame'))
    ssha = dict(db.execute('SELECT frame_id, semantics_sha FROM frame_semantics'))
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    n, bad = 0, []
    with open(csvpath, newline='', encoding='utf-8') as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):
            v = (row.get('verdict') or '').strip().lower()
            if not v:
                continue
            fid = int(row['frame_id'])
            if v not in ('approve', 'reject', 'fix'):
                bad.append(f'line {i}: verdict must be approve, reject or fix, got {v!r}')
                continue
            if fid not in shas or texts[fid] != row['template']:
                bad.append(f'line {i}: template {fid} no longer matches this build; re-export and review again')
                continue
            if row.get('semantics_sha') and row['semantics_sha'] != ssha.get(fid):
                bad.append(f'line {i}: the semantics of template {fid} changed since export; re-export and review again')
                continue
            note = row.get('note')
            if v == 'fix':
                spec = (row.get('corrected_concepts') or '').split()
                new = []
                for tok in spec:
                    cid, _, rel = tok.partition(':')
                    if cid not in known:
                        bad.append(f'line {i}: unknown concept {cid!r}')
                        new = None
                        break
                    new.append((cid, rel or 'PRODUCES'))
                if not new:
                    if new is not None:
                        bad.append(f'line {i}: fix needs corrected_concepts')
                    continue
                db.execute('DELETE FROM frame_concept_edge WHERE frame_id=?', (fid,))
                db.executemany('INSERT INTO frame_concept_edge VALUES(?,?,?,?,?,?)',
                               [(fid, c, r, json.dumps({'group': 'trigger', 'alt': k} if c.startswith('ev.') and roles[fid] == 'trigger_event' else {}),
                                 'review:' + reviewer, 'reviewed') for k, (c, r) in enumerate(new)])
                units = sm.compose(roles[fid], texts[fid], [(c, r, rid, json.loads(m) if m else {}) for _, c, r, m, rid, _ in
                                                           db.execute('SELECT * FROM frame_concept_edge WHERE frame_id=?', (fid,))])
                s2 = sm.sem_sha(units)
                db.execute('UPDATE frame_semantics SET units_json=?, description=?, semantics_sha=? WHERE frame_id=?',
                           (json.dumps(units, sort_keys=True), sm.describe(units), s2, fid))
                ssha[fid] = s2
                note = ((note or '') + ' | fixed to: ' + ' '.join(spec)).strip(' |')
            elif v == 'approve':
                db.execute("UPDATE frame_concept_edge SET status='reviewed' WHERE frame_id=?", (fid,))
            else:
                db.execute("UPDATE frame_concept_edge SET status='rejected' WHERE frame_id=?", (fid,))
            db.execute('INSERT INTO review(frame_id, concept_id, relation, verdict, corrected_concept, corrected_relation, '
                       'reviewer, reviewed_utc, note, frame_text_sha, semantics_sha) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                       (fid, '*', '*', v, row.get('corrected_concepts') or None, None, reviewer, now, note, shas[fid], ssha[fid]))
            n += 1
    db.commit()
    print(f'{n} verdicts applied')
    for b in bad:
        print('skipped', b, file=sys.stderr)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['export', 'apply'])
    ap.add_argument('db')
    ap.add_argument('path')
    ap.add_argument('--reviewer', default='Zach')
    a = ap.parse_args()
    export(a.db, a.path) if a.cmd == 'export' else apply(a.db, a.path, a.reviewer)
