import json, sys, collections, openpyxl
sys.path.insert(0, '/mnt/project-files/mechanics-kernel')
from convert import Conv
from build_outputs_lib import next_action, gate_summary
COLS = ['Operation ID', 'Card Name', 'Face/Scope', 'Operation Kind', 'Exact Oracle Clause', 'Observes / Input Hook',
        'Requirement Groups (AND)', 'Alternatives (OR)', 'Result Produces', 'Payment / Consumes', 'Modifies', 'Timing',
        'Qualifiers', 'Object Transition', 'Status', 'Confidence', 'Source URL', 'Review Note']
d = json.load(open('extraction.json'))
wb = openpyxl.load_workbook('../kb/canonical_20261024c.xlsx', read_only=True, data_only=True)
coll = {r[0]: r for r in ([list(x) + [None] * 25 for x in wb['Collection'].values][4:]) if r[0]}
queue, kern = [], {}
for r in d['ops']:
    row = dict(zip(COLS, r))
    res = Conv(row).convert()
    kern[r[0]] = res
    if r[15] != 'low' and r[14] != 'requires_manual_annotation':
        continue
    alloc = int(coll[r[1]][3] or 0)
    if r[14] == 'requires_manual_annotation': why = 'Grammar parse incomplete'
    elif r[3] == 'replacement': why = 'Replacement and overwritten-event check'
    elif 'copy' in (r[13] or '') or 'copy' in r[4].lower(): why = 'Copy / cast / object continuity'
    elif r[13] or 'exile' in r[12] or 'graveyard' in r[12]: why = 'Zone transition / linked effect check'
    else: why = 'Qualified timing and resource gates'
    pri = 'High' if alloc > 0 else ('Medium' if r[14] == 'requires_manual_annotation' else 'Low')
    queue.append([r[0], r[1], alloc, pri, why, r[14], r[15], 'Unreviewed', r[16],
                  'Open source clause; verify correct checkpoints and outputs before admitting graph connection',
                  res['conversion'], gate_summary(res), ' | '.join(res['residue']), next_action(res)])
json.dump({'queue': queue, 'kernel': {k: {'conversion': v['conversion'], 'gate': gate_summary(v), 'residue': v['residue'], 'next': next_action(v), 'parsed_kind': v['parsed_kind']} for k, v in kern.items()}},
          open('queue.json', 'w'), ensure_ascii=False)
C = collections.Counter
print(len(queue), C(q[3] for q in queue), C(q[4] for q in queue), C(q[10] for q in queue))
print('all ops kernel', C(v['conversion'] for v in kern.values()))
