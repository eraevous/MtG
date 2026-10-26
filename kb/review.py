#!/usr/bin/env python3
"""Append-only human review overlay.

The overlay file (overrides/review_overlay.jsonl) is the source of truth for human judgement. It is
never rewritten: a correction is a new line that supersedes an earlier one. Each line carries the
Oracle text SHA (and, for contracts, the contract SHA) it was made against, so a text or parser
change makes the review stale instead of silently re-applying it. Lines are hash-chained.

  python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add \
      --contract 'card.The%20Necrobloom.op002' --decision verified --reviewer Zach \
      --source 'Oracle text + CR 702.52 (dredge)' --test necrobloom.dredge_land

A review is a SEMANTIC judgement: the contract says what the Oracle text says. It never certifies
runtime behaviour; runtime certificates are issued by the build from scenario runs (scenarios.py).
A `verified` review must cite scenario ids from scenarios/*.json that belong to this contract and
whose semantic assertions pass on the current contract version. Labels and placeholders are refused.
  python review.py ... show --card 'The Necrobloom'
  python review.py ... verify          # check the chain and every line's applicability
"""
import argparse, datetime, json, sqlite3, sys
from pathlib import Path
import kbfacts as F
import scenarios as SC

FIELDS = ['subject_kind', 'subject_id', 'card_name', 'decision', 'reviewer', 'reviewed_utc', 'source',
          'oracle_text_sha256', 'contract_sha256', 'tests', 'notes', 'supersedes', 'rules_text_sha256', 'scope', 'test_results']


def read_overlay(path):
    p = Path(path)
    if not p.exists(): return []
    out, prev = [], ''
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'): continue
        r = json.loads(line)
        body = {k: r.get(k) for k in FIELDS}
        if r.get('prev') != prev: raise ValueError(f'line {i}: hash chain broken')
        if r.get('review_id') != F.sha(prev, F.dumps(body)): raise ValueError(f'line {i}: review_id does not match content')
        prev = r['review_id']; out.append(r)
    return out


def check(con, body, registry=None):
    """Refuse reviews that would not be honest about what was reviewed. Returns the scenario results."""
    card = con.execute('select oracle_text_sha256 from cards where card_name=?', (body['card_name'],)).fetchone()
    if not card: raise ValueError('unknown card')
    if body['oracle_text_sha256'] != card[0]: raise ValueError('oracle_text_sha256 is not the current stored text')
    if body.get('scope', 'semantic') != 'semantic': raise ValueError('reviews are semantic only; runtime certification is issued by the build')
    rt = con.execute('select rules_text_sha256 from rules_text where card_name=?', (body['card_name'],)).fetchone()
    if rt and body.get('rules_text_sha256') != rt[0]: raise ValueError('rules_text_sha256 is not the current Oracle rules text')
    results = []
    if body['decision'] == 'verified':
        if not body['tests']: raise ValueError('a verified review must name at least one test')
        if not body['source']: raise ValueError('a verified review must cite its source')
        reg = registry if registry is not None else SC.load()
        for t in body['tests']:
            if not isinstance(t, str) or not SC.ID_RE.match(t): raise ValueError(f'test {t!r} is not a scenario id (placeholders are refused)')
            if t not in reg: raise ValueError(f'test {t!r} does not resolve to a scenario in scenarios/*.json')
            if reg[t]['contract_id'] != body['subject_id']: raise ValueError(f'scenario {t} tests another contract ({reg[t]["contract_id"]})')
            res = SC.run_semantic(con, reg[t])
            if not res['passed']: raise ValueError(f'scenario {t} does not pass on the current contract: ' +
                                                   json.dumps([r for r in res['results'] if not r['passed']], default=str)[:400])
            results.append({'scenario': t, 'scenario_sha256': res['scenario_sha256'], 'contract_sha256': res['contract_sha256'], 'passed': True})
    if body['subject_kind'] == 'operation_contract':
        k = con.execute('select contract_sha256,card_name from current_contracts where contract_id=?', (body['subject_id'],)).fetchone()
        if not k: raise ValueError('unknown contract')
        if k[1] != body['card_name']: raise ValueError('contract belongs to another card')
        if body['contract_sha256'] != k[0]: raise ValueError('contract_sha256 is not the current contract version')
        if body['decision'] == 'verified':
            q = con.execute('select queue_state,fails from validation_queue where contract_id=?', (body['subject_id'],)).fetchone()
            if q and q[1] > 0: raise ValueError('contract has failing validation checks; revise it before verifying')
            if q and q[0] == 'quarantined': raise ValueError('contract is quarantined (material Sheet/Oracle discrepancy); correct the Sheet first')
    return results


def append(con, path, body, registry=None):
    rows = read_overlay(path)
    body = dict(body, scope=body.get('scope', 'semantic'))
    body['test_results'] = check(con, body, registry)
    prev = rows[-1]['review_id'] if rows else ''
    rec = dict(body, prev=prev, review_id=F.sha(prev, F.dumps({k: body.get(k) for k in FIELDS})))
    with open(path, 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + '\n')
    return rec


def replay(con, path):
    """Load the overlay into the DB table (append-only; triggers forbid update/delete)."""
    n = 0
    for seq, r in enumerate(read_overlay(path), 1):
        con.execute('insert into review_overlay(seq,review_id,subject_kind,subject_id,card_name,decision,reviewer,reviewed_utc,source,'
                    'oracle_text_sha256,contract_sha256,tests_json,notes,supersedes,rules_text_sha256,scope,test_results_json) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (seq, r['review_id'], r['subject_kind'], r['subject_id'], r['card_name'], r['decision'], r['reviewer'],
                     r['reviewed_utc'], r['source'], r['oracle_text_sha256'], r.get('contract_sha256'), json.dumps(r['tests']),
                     r.get('notes'), r.get('supersedes'), r.get('rules_text_sha256'), r.get('scope') or 'semantic',
                     json.dumps(r.get('test_results')) if r.get('test_results') is not None else None))
        n += 1
    return n


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--db', required=True); p.add_argument('--overlay', required=True)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add')
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument('--contract'); g.add_argument('--claim', nargs=2, metavar=('CARD', 'CAPABILITY'))
    a.add_argument('--decision', required=True, choices=['verified', 'contradicted', 'rejected', 'needs_review', 'revoked'])
    a.add_argument('--reviewer', required=True); a.add_argument('--source', default='')
    a.add_argument('--test', action='append', default=[]); a.add_argument('--notes'); a.add_argument('--supersedes')
    s = sub.add_parser('show'); s.add_argument('--card')
    sub.add_parser('verify')
    args = p.parse_args()
    con = sqlite3.connect(Path(args.db).resolve().as_uri() + '?mode=ro', uri=True)
    if args.cmd == 'add':
        if args.contract:
            name, csha = con.execute('select card_name,contract_sha256 from current_contracts where contract_id=?', (args.contract,)).fetchone()
            kind, sid = 'operation_contract', args.contract
        else:
            name, csha, kind, sid = args.claim[0], None, 'capability_claim', f'{args.claim[0]}|{args.claim[1]}'
        osha = con.execute('select oracle_text_sha256 from cards where card_name=?', (name,)).fetchone()[0]
        rt = con.execute('select rules_text_sha256 from rules_text where card_name=?', (name,)).fetchone()
        body = {'subject_kind': kind, 'subject_id': sid, 'card_name': name, 'decision': args.decision, 'reviewer': args.reviewer,
                'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'source': args.source,
                'oracle_text_sha256': osha, 'contract_sha256': csha, 'tests': args.test, 'notes': args.notes, 'supersedes': args.supersedes,
                'rules_text_sha256': rt[0] if rt else None, 'scope': 'semantic'}
        print(json.dumps(append(con, args.overlay, body), indent=2))
        print('Rebuild (migrate_v02.py) to apply; the DB copy of the overlay is replayed from this file.', file=sys.stderr)
    elif args.cmd == 'show':
        rows = read_overlay(args.overlay)
        print(json.dumps([r for r in rows if not args.card or r['card_name'] == args.card], indent=2, ensure_ascii=False))
    else:
        rows = read_overlay(args.overlay)
        cur = {n: s for n, s in con.execute('select card_name,oracle_text_sha256 from cards')}
        stale = [r['review_id'][:12] for r in rows if cur.get(r['card_name']) != r['oracle_text_sha256']]
        print(json.dumps({'lines': len(rows), 'chain': 'ok', 'stale_text': stale}, indent=2))


if __name__ == '__main__':
    main()
