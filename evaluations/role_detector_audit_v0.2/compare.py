"""Compare frozen reviewer A and B answers: per-role agreement, a reconciliation record, and weighted miss-rate estimates.

Reads reviewer/, reviews/reviewer_{A,B}/, private_key.jsonl and adjudication_claude.jsonl (proposed answers for every
disagreement); writes agreement.json and reconciliation.jsonl. Agreed answers stand; adjudicated ones are labelled proposed.
The challenge set is reported separately and never enters the population estimates.
"""
import glob, json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ['YES', 'DEPENDS', 'NO', 'UNRESOLVED']

def load(pattern):
    rows = {}
    for f in sorted(glob.glob(os.path.join(HERE, pattern))):
        for line in open(f, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                rows[r.get('item') or r['review_item']] = r
    return rows

def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in CATS) / n / n
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)

def upper95(x, n):
    # One-sided 95% Clopper-Pearson upper bound by bisection (no scipy).
    if x == n:
        return 1.0
    def tail(p):  # P(X <= x | n, p)
        from math import comb
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))
    lo, hi = x / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail(mid) > 0.05 else (lo, mid)
    return hi

def main():
    items, key = load('reviewer/batch_*.jsonl'), load('private_key.jsonl')
    A, B = load('reviews/reviewer_A/batch_*.jsonl'), load('reviews/reviewer_B/batch_*.jsonl')
    assert set(items) == set(key) == set(A) == set(B), 'packets and reviews must cover the same items'
    adj = load('adjudication_claude.jsonl')
    pop = json.load(open(os.path.join(HERE, 'population.json')))['strata']
    groups, finals, recon = defaultdict(list), defaultdict(list), []
    for rid in sorted(items):
        it, k, a, b = items[rid], key[rid], A[rid], B[rid]
        part = 'challenge' if k['stratum'] is None else 'untagged'
        groups[(part, it['role'], k['stratum'])].append((a['answer'], b['answer']))
        recon.append({'review_item': rid, 'source_item': k['source_item'], 'role': it['role'], 'card': it['card'],
                      'stratum': k['stratum'], 'mechanism': k['mechanism'], 'agree': a['answer'] == b['answer'],
                      'A': {f: a.get(f) for f in ('answer', 'evidence', 'qualifiers', 'note')},
                      'B': {f: b.get(f) for f in ('answer', 'evidence', 'qualifiers', 'note')},
                      'adjudication': adj.get(rid)})
        final = a['answer'] if a['answer'] == b['answer'] else (adj[rid]['answer'] if rid in adj else 'UNRESOLVED')
        finals[(part, it['role'], k['stratum'])].append(final)
    out = {'roles': {}, 'overall': {}}
    for part in ('untagged', 'challenge'):
        pairs = [p for (pt, _, _), ps in groups.items() if pt == part for p in ps]
        out['overall'][part] = {'n': len(pairs), 'agreement': round(sum(a == b for a, b in pairs) / len(pairs), 3),
                                'kappa': kappa(pairs)}
    for role in sorted({r for _, r, _ in groups}):
        row = {}
        for part in ('untagged', 'challenge'):
            pairs = [p for (pt, r, _), ps in groups.items() if pt == part and r == role for p in ps]
            if pairs:
                row[part] = {'n': len(pairs), 'agreement': round(sum(a == b for a, b in pairs) / len(pairs), 3),
                             'kappa': kappa(pairs), 'A': dict(Counter(a for a, _ in pairs)),
                             'B': dict(Counter(b for _, b in pairs))}
        # Weighted estimate of owned cards with no claim of this role that should have one. Two bounds per reviewer:
        # YES only, and YES or DEPENDS. Both reviewers YES gives a conservative floor.
        est = {}
        for label, hit in (('A_yes', lambda a, b: a == 'YES'), ('B_yes', lambda a, b: b == 'YES'),
                           ('both_yes', lambda a, b: a == b == 'YES'),
                           ('either_yes_or_depends', lambda a, b: 'YES' in (a, b) or 'DEPENDS' in (a, b))):
            total = 0.0
            for stratum, size in pop[role].items():
                ps = groups[('untagged', role, stratum)]
                total += size * sum(hit(a, b) for a, b in ps) / len(ps)
            est[label] = round(total)
        for label, ok in (('adjudicated_yes', ('YES',)), ('adjudicated_yes_or_depends', ('YES', 'DEPENDS'))):
            total, hi = 0.0, 0.0
            for stratum, size in pop[role].items():
                fs = finals[('untagged', role, stratum)]
                x = sum(f in ok for f in fs)
                total += size * x / len(fs)
                hi += size * upper95(x, len(fs))
            est[label] = round(total)
            est[label + '_upper95'] = round(hi)  # sum of per-stratum one-sided 95% bounds: conservative
        row['estimated_missed_cards'] = est
        row['untagged_population'] = sum(pop[role].values())
        out['roles'][role] = row
    json.dump(out, open(os.path.join(HERE, 'agreement.json'), 'w'), indent=1)
    with open(os.path.join(HERE, 'reconciliation.jsonl'), 'w', encoding='utf-8') as f:
        for r in recon:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    out['disagreements'] = sum(not r['agree'] for r in recon)
    out['adjudicated'] = sum(r['adjudication'] is not None for r in recon if not r['agree'])
    print(json.dumps(out['overall']), out['disagreements'], out['adjudicated'])
    for role, row in out['roles'].items():
        u, c = row['untagged'], row.get('challenge', {})
        print(f"{role:13} untagged agree {u['agreement']:.2f} k={u['kappa']} A={u['A']} B={u['B']} | "
              f"challenge agree {c.get('agreement')} k={c.get('kappa')} | est {row['estimated_missed_cards']} of {row['untagged_population']}")

if __name__ == '__main__':
    main()
