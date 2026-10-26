"""Build the 2026-10-24 mechanics review packet: ops grouped by mechanical class, allocated cards first."""
import csv, json, sqlite3, collections, sys
OUT = sys.argv[1]
d = json.load(open('extraction.json')); q = json.load(open('queue.json'))
kern = q['kernel']; qrow = {r[0]: r for r in q['queue']}
kb = sqlite3.connect('../kb/src2/mtg_cards.sqlite')
assigned = {n: a for n, a in kb.execute('select card_name, assigned from cards')}
decks = collections.defaultdict(set)
for n, dk in kb.execute('select card_name, deck from deck_allocations'):
    decks[n].add(dk)
TT = 'Token Triumph'

def cls(o):
    kind, hook, prod = o[3], o[5] or '-', o[8] or '-'
    return f'{kind} | {hook} -> {prod}'

ops = d['ops']
by = collections.defaultdict(list)
for o in ops: by[cls(o)].append(o)
def prio(o):
    dk = decks.get(o[1], set())
    return 0 if TT in dk else (1 if (assigned.get(o[1]) or 0) > 0 else 2)
# classes: biggest first, so one verdict covers the most rows
order = sorted(by, key=lambda c: (-len(by[c]), c))
cid = {c: f'C{i+1:02d}' for i, c in enumerate(order)}
H = ['class_id', 'class_signature', 'class_size', 'priority', 'decks', 'operation_id', 'card_name', 'kind',
     'oracle_clause', 'observes_hook', 'requirement', 'result_produces', 'payment', 'modifies', 'timing',
     'qualifiers', 'object_transition', 'status', 'confidence', 'in_review_queue', 'why_flagged',
     'kernel_readiness', 'kernel_gate', 'kernel_residue', 'kernel_next', 'note',
     'class_verdict', 'row_verdict', 'correction', 'reviewer_note']
P = {0: '1 Token Triumph', 1: '2 allocated', 2: '3 free'}
rows = []
for c in order:
    for o in sorted(by[c], key=lambda o: (prio(o), o[1], o[0])):
        k = kern[o[0]]; qr = qrow.get(o[0])
        rows.append([cid[c], c, len(by[c]), P[prio(o)], '; '.join(sorted(decks.get(o[1], []))), o[0], o[1], o[3],
                     o[4], o[5], o[6], o[8], o[9], o[10], o[11], o[12], o[13], o[14], o[15],
                     'yes' if qr else 'no', qr[4] if qr else '', k['conversion'], k['gate'], ' | '.join(k['residue']),
                     k['next'], o[17], '', '', '', ''])
with open(f'{OUT}/operations_by_class.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(H); w.writerows(rows)
# class summary
S = ['class_id', 'class_signature', 'ops', 'cards', 'token_triumph_ops', 'allocated_ops', 'low_confidence', 'requires_manual',
     'kernel_structured', 'kernel_partial', 'kernel_inherits_parent', 'kernel_out_of_scope', 'example_card', 'example_clause', 'class_verdict', 'reviewer_note']
with open(f'{OUT}/class_summary.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(S)
    for c in order:
        g = by[c]; kc = collections.Counter(kern[o[0]]['conversion'] for o in g)
        ex = sorted(g, key=lambda o: (prio(o), o[15] != 'medium', o[1]))[0]
        w.writerow([cid[c], c, len(g), len({o[1] for o in g}), sum(prio(o) == 0 for o in g), sum(prio(o) <= 1 for o in g),
                    sum(o[15] == 'low' for o in g), sum(o[14] == 'requires_manual_annotation' for o in g),
                    kc['structured'], kc['partial'], kc['inherits_parent'], kc['out_of_scope'], ex[1], ex[4], '', ''])
C = collections.Counter
print('classes', len(order), 'singletons', sum(len(by[c]) == 1 for c in order))
print('top', [(cid[c], c, len(by[c])) for c in order[:12]])
print('prio', C(P[prio(o)] for o in ops))
print('tt cards', len({o[1] for o in ops if prio(o) == 0}), 'alloc cards', len({o[1] for o in ops if prio(o) <= 1}))
