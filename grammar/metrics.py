"""Coverage and construction counts for a built grammar_layer.sqlite.

    python3 -I metrics.py grammar_layer.sqlite [--kb mtg_cards_v0.2.sqlite] > metrics.json

Headline metric (Kate/Zach 2026-10-21): the share of the collection's abilities that can be expressed through
reviewed templates without card-specific interpretation. Three readings are reported so they cannot be confused:
  parsed_complete      every part of the ability fell into a frame whose rules account for every word
  reviewed_complete    the same, and every one of those frames has an approved review (0 until Zach reviews)
  leverage             how many top frames would need review to reach a given reviewed_complete share
"""
import argparse
import collections
import json
import re
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COUNTED_KINDS = "('keyword','triggered','activated','spell','static','replacement','mode','loyalty','chapter','additional_cost')"


def pct(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def curve(counts, marks=(50, 80, 90, 95, 99)):
    counts = sorted(counts, reverse=True)
    tot = sum(counts)
    out, run, i = {}, 0, 0
    for m in marks:
        while i < len(counts) and run < tot * m / 100:
            run += counts[i]
            i += 1
        out[f'{m}%'] = i
    return out


def annotate(db):
    """Store ability-level completeness and the approved-frame set on the DB."""
    cols = [r[1] for r in db.execute('PRAGMA table_info(ability)')]
    if 'completeness' not in cols:
        db.execute('ALTER TABLE ability ADD COLUMN completeness TEXT')
        db.execute('ALTER TABLE ability ADD COLUMN reviewed INT')
    approved = {r[0] for r in db.execute(
        "SELECT frame_id FROM effective_frame_review WHERE frame_ok=1")} if has_view(db, 'effective_frame_review') else set()
    rows = db.execute('SELECT a.ability_id, f.completeness, f.frame_id FROM ability a JOIN part p USING(ability_id) '
                      'JOIN frame f ON f.frame_id=p.frame_id').fetchall()
    per = collections.defaultdict(list)
    for aid, comp, fid in rows:
        per[aid].append((comp, fid))
    upd = []
    for aid, lst in per.items():
        comps = {c for c, _ in lst}
        c = 'complete' if comps == {'complete'} else ('none' if comps == {'none'} else 'partial')
        upd.append((c, int(c == 'complete' and all(f in approved for _, f in lst)), aid))
    db.executemany('UPDATE ability SET completeness=?, reviewed=? WHERE ability_id=?', upd)
    db.commit()
    return approved


def has_view(db, name):
    return db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (name,)).fetchone() is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('db')
    ap.add_argument('--kb')
    a = ap.parse_args()
    db = sqlite3.connect(a.db)
    q = lambda s, *p: db.execute(s, p).fetchall()  # noqa: E731
    approved = annotate(db)
    M = {'manifest': dict(q('SELECT key, value FROM source_manifest'))}

    # ---- corpus shape
    M['corpus'] = {
        'cards_parsed': q("SELECT count(*) FROM card WHERE scope IN ('corpus','collection')")[0][0],
        'collection_cards': q("SELECT count(*) FROM card WHERE scope='collection'")[0][0],
        'abilities_by_kind': dict(q('SELECT kind, count(*) FROM ability GROUP BY 1 ORDER BY 2 DESC')),
        'parts_by_role': dict(q('SELECT role, count(*) FROM part GROUP BY 1 ORDER BY 2 DESC')),
    }
    nparts = q('SELECT count(*) FROM part')[0][0]
    frames = q('SELECT role, n_parts, n_cards, n_collection_parts, completeness FROM frame')
    M['constructions'] = {
        'distinct_frames': len(frames),
        'frames_by_role': dict(collections.Counter(r[0] for r in frames).most_common()),
        'frames_on_2plus_cards': sum(1 for r in frames if r[2] >= 2),
        'frames_on_5plus_cards': sum(1 for r in frames if r[2] >= 5),
        'share_of_parts_in_frames_on_2plus_cards': pct(sum(r[1] for r in frames if r[2] >= 2), nparts),
        'share_of_parts_in_frames_on_5plus_cards': pct(sum(r[1] for r in frames if r[2] >= 5), nparts),
        'frames_needed_to_cover_share_of_parts': curve([r[1] for r in frames]),
        'frames_needed_by_role': {role: curve([r[1] for r in frames if r[0] == role])
                                  for role in ('effect', 'trigger_event', 'cost', 'static', 'condition', 'keyword')},
        'parts_by_completeness': dict(collections.Counter(
            c for c, n in [(r[4], r[1]) for r in frames] for _ in range(n)).most_common()),
    }

    # ---- concept layer
    conc = q("SELECT f.frame_id, e.concept_id, c.semantic_type FROM frame f JOIN frame_concept_edge e USING(frame_id) "
             "JOIN concept c USING(concept_id)")
    by_frame = collections.defaultdict(set)
    for fid, cid, st in conc:
        by_frame[fid].add(cid)
    M['registry'] = {
        'concepts_defined': q('SELECT count(*) FROM concept')[0][0],
        'concepts_used': len({c for _, c, _ in conc}),
        'concepts_used_by_type': dict(collections.Counter(st for st in {(c, st) for _, c, st in conc} for st in [st[1]]).most_common()) if False else
        dict(collections.Counter(st for _, st in {(c, st) for _, c, st in conc}).most_common()),
        'edges': len(conc),
        'frames_with_edges': len(by_frame),
        'frames_with_2plus_concepts': sum(1 for v in by_frame.values() if len(v) >= 2),
        'concepts_by_dio_status': dict(q("SELECT dio_status, count(*) FROM concept WHERE concept_id IN "
                                         "(SELECT concept_id FROM frame_concept_edge) GROUP BY 1")),
        'edge_status': dict(q('SELECT status, count(*) FROM frame_concept_edge GROUP BY 1')),
    }
    # concept signatures: what an ability does, with every surface difference abstracted away
    sig = collections.Counter()
    sig_coll = collections.Counter()
    rows = q(f"SELECT a.ability_id, a.kind, p.role, p.frame_id, c.in_collection FROM ability a JOIN part p USING(ability_id) "
             f"JOIN card c USING(oracle_id) WHERE a.kind IN {COUNTED_KINDS} ORDER BY a.ability_id, p.ordinal")
    cur, parts, kind, incol = None, [], None, 0

    def flush():
        if cur is None:
            return
        s = kind + '|' + ' ; '.join(r + ':' + ('+'.join(sorted(by_frame.get(f, {'?'})))) for r, f in parts)
        sig[s] += 1
        if incol:
            sig_coll[s] += 1
    for aid, k, role, fid, ic in rows:
        if aid != cur:
            flush()
            cur, parts, kind, incol = aid, [], k, ic
        parts.append((role, fid))
    flush()
    M['registry']['distinct_concept_signatures'] = len(sig)
    M['registry']['signatures_needed_to_cover_share_of_abilities'] = curve(list(sig.values()))
    M['registry']['top_signatures'] = sig.most_common(25)

    # ---- collection coverage (headline)
    ab = q(f"SELECT a.kind, a.completeness, a.reviewed FROM ability a JOIN card c USING(oracle_id) "
           f"WHERE c.in_collection=1 AND a.kind IN {COUNTED_KINDS}")
    n = len(ab)
    comp = sum(1 for r in ab if r[1] == 'complete')
    rev = sum(1 for r in ab if r[2] == 1)
    kinds = collections.defaultdict(lambda: [0, 0])
    for k, c, _ in ab:
        kinds[k][0] += 1
        kinds[k][1] += c == 'complete'
    cards = q(f"SELECT c.oracle_id, min(a.completeness='complete') FROM card c JOIN ability a USING(oracle_id) "
              f"WHERE c.in_collection=1 AND a.kind IN {COUNTED_KINDS} GROUP BY 1")
    M['collection'] = {
        'abilities': n,
        'parsed_complete': comp, 'parsed_complete_pct': pct(comp, n),
        'reviewed_complete': rev, 'reviewed_complete_pct': pct(rev, n),
        'approved_frames': len(approved),
        'by_kind': {k: {'abilities': v[0], 'complete_pct': pct(v[1], v[0])} for k, v in sorted(kinds.items(), key=lambda x: -x[1][0])},
        'cards_with_every_ability_complete': sum(1 for _, m in cards if m), 'cards': len(cards),
        'cards_all_complete_pct': pct(sum(1 for _, m in cards if m), len(cards)),
        'parts': q('SELECT sum(n_collection_parts) FROM frame')[0][0],
        'parts_complete_pct': pct(q("SELECT sum(n_collection_parts) FROM frame WHERE completeness='complete'")[0][0],
                                  q('SELECT sum(n_collection_parts) FROM frame')[0][0]),
    }
    # frames the collection uses that also appear on cards Zach does not own
    fc = q("SELECT f.frame_id, max(c.in_collection), min(c.in_collection) FROM frame f JOIN part p USING(frame_id) "
           "JOIN ability a USING(ability_id) JOIN card c USING(oracle_id) GROUP BY 1")
    coll_frames = [r for r in fc if r[1] == 1]
    M['collection']['distinct_frames_used'] = len(coll_frames)
    M['collection']['frames_also_on_unowned_cards_pct'] = pct(sum(1 for r in coll_frames if r[2] == 0), len(coll_frames))
    M['collection']['frames_only_on_unowned_cards'] = sum(1 for r in fc if r[1] == 0)

    # ---- review leverage: review frames in order of collection impact
    ab_frames = collections.defaultdict(set)
    for aid, fid in q(f"SELECT a.ability_id, p.frame_id FROM ability a JOIN part p USING(ability_id) JOIN card c USING(oracle_id) "
                      f"JOIN frame f ON f.frame_id=p.frame_id WHERE c.in_collection=1 AND a.kind IN {COUNTED_KINDS} "
                      f"AND a.completeness='complete'"):
        ab_frames[aid].add(fid)
    order = [r[0] for r in q("SELECT frame_id FROM frame WHERE completeness='complete' AND n_collection_parts>0 "
                             "ORDER BY n_collection_parts DESC, n_parts DESC")]
    rank = {f: i for i, f in enumerate(order)}
    need = sorted(max(rank[f] for f in fs) + 1 for fs in ab_frames.values())
    lev = {}
    for k in (25, 50, 100, 200, 300, 500, 1000, 2000):
        lev[f'top_{k}_frames'] = pct(sum(1 for x in need if x <= k), n)
    lev['frames_for_all_complete_abilities'] = len(order)
    M['collection']['review_leverage_pct_of_abilities'] = lev

    if a.kb:
        M['contract_comparison'] = compare_contracts(db, a.kb)
    print(json.dumps(M, indent=1, default=str))


HOOK_OF = None


def compare_contracts(db, kb):
    """Agreement between this registry's concepts and the 0.3.0 drafted contracts, ability by ability."""
    kbc = sqlite3.connect(f'file:{kb}?mode=ro', uri=True)
    contracts = collections.defaultdict(list)
    import grammar
    for name, text, cj in kbc.execute('SELECT card_name, exact_text, contract_json FROM operation_contracts'):
        c = json.loads(cj)
        qi = c.get('query_index') or {}
        t = grammar.strip_reminder(grammar.prep(text or '', grammar.self_names(name, name)))[0]
        contracts[name].append((norm(t), {alias(h) for h in qi.get('hook_ids') or []},
                                {alias(h) for h in qi.get('feeds') or []}, c.get('kind')))
    intent = dict(db.execute("SELECT concept_id, dio_ref FROM concept"))
    rows = db.execute("""SELECT c.kb_card_name, a.ability_id, a.kind, a.text, group_concat(e.concept_id, ' ')
        FROM ability a JOIN card c USING(oracle_id) JOIN part p USING(ability_id)
        LEFT JOIN frame_concept_edge e ON e.frame_id=p.frame_id
        WHERE c.in_collection=1 AND a.kind IN ('triggered','activated','spell','static','replacement','loyalty','mode','chapter')
        GROUP BY a.ability_id""").fetchall()
    stats = collections.Counter()
    disagreements = []
    for name, aid, kind, text, concs in rows:
        cands = contracts.get(name) or []
        t = norm(text)
        match = None
        for ct in cands:
            if ct[0] and (ct[0] in t or t in ct[0]):
                match = ct
                break
        if not match:
            stats['no_matching_contract'] += 1
            continue
        stats['matched'] += 1
        concs = set((concs or '').split())
        ours_ev = {alias(hook_of(intent[c])) for c in concs if c.startswith('ev.')}
        ours_op = {alias(hook_of(intent[c])) for c in concs if c.startswith(('op.', 'cost.', 'kwa.'))}
        th, tf = match[1] - {'spell.resolve'}, match[2]
        if th and text.lower().startswith('as ') and ' enters' in text.lower():
            stats['as_enters_contract_trigger_vs_our_replacement'] += 1
            th = set()
        if th:
            stats['contract_trigger_hooks'] += 1
            if ours_ev & th:
                stats['trigger_hook_agree'] += 1
            else:
                disagreements.append(('trigger', name, text[:120], sorted(th), sorted(ours_ev)))
        if tf:
            stats['contract_feeds'] += 1
            if ours_op & tf:
                stats['feed_agree_any'] += 1
            else:
                disagreements.append(('result', name, text[:120], sorted(tf), sorted(ours_op)))
    out = dict(stats)
    if stats['contract_trigger_hooks']:
        out['trigger_hook_agree_pct'] = pct(stats['trigger_hook_agree'], stats['contract_trigger_hooks'])
    if stats['contract_feeds']:
        out['feed_agree_pct'] = pct(stats['feed_agree_any'], stats['contract_feeds'])
    out['sample_disagreements'] = disagreements[:40]
    return out


def hook_of(dio_ref):
    m = re.search(r':\s*([a-z_]+\.[a-z_.]+)', dio_ref)
    return m.group(1) if m else dio_ref


ALIAS = {'creature.enters_battlefield': 'battlefield.enter', 'artifact.enters_battlefield': 'battlefield.enter',
         'land.enters_battlefield': 'battlefield.enter', 'token.enters_battlefield': 'battlefield.enter',
         'zone.enter': 'zone.change', 'graveyard.enter': 'zone.change', 'zone.leave': 'zone.change',
         'card.return_to_battlefield': 'card.return_to_hand', 'timing.step_begin': 'turn.step.begin',
         'exile.enter': 'exile.enter', 'creature.card_enters_graveyard': 'zone.change'}


def alias(h):
    return ALIAS.get(h, h)


def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', (s or '').lower().replace('—', ' ')).strip()[:200]


if __name__ == '__main__':
    main()
