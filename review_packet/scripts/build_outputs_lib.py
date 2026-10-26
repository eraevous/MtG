import json
NEXT = {
    'structured': 'Confirm the typed gate against Oracle, then mark reviewed',
    'partial': 'Type the residue (see Residue column), then confirm',
    'inherits_parent': 'No gate of its own: review together with its enclosing spell/ability/mode',
    'needs_resegmenting': 'Merge with its cost row in Mechanics · Operations',
}


def next_action(r):  # copied from mechanics-kernel/build_outputs.py
    if r['conversion'] != 'out_of_scope':
        return NEXT[r['conversion']]
    k = r['parsed_kind']
    if k == 'replacement':
        return 'Wait for a replacement model (kernel can only read final events)'
    if k == 'keyword':
        return 'Expand the keyword into operations first'
    if '"' in r['clean_text'] or '“' in r['clean_text']:
        return 'Split the granted ability into its own operation'
    return 'Wait for a continuous/layer model'


def gate_summary(r):
    gs = r['operation']['initiation']['requirement_groups']
    return ' AND '.join('(' + ' OR '.join(
        (a['hook'] + (json.dumps(a['where'], separators=(',', ':')) if a.get('where') else '')) if a['kind'] == 'event'
        else f"{a['path']} {a['op']} {json.dumps(a['value'])}" for a in g['alternatives']) + ')' for g in gs)
