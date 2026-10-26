#!/usr/bin/env python3
"""Read-only MTG canonical inventory adapter.

Purpose: use the Collection and Deck Allocations as sources of copy facts;
interpret Mechanics Units/Operations as candidate annotations, never verified rules.
Consumes an OOXML workbook exported/snapshotted from canonical Google Sheets.
No dependencies outside Python standard library. Never modifies source workbook.
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CANONICAL_ID = '1N1xBUkL_aYKpPcR8WJJVpeicgE8A06dqeUBM-hUa3Xo'
CANONICAL_URL = 'https://docs.google.com/spreadsheets/d/' + CANONICAL_ID + '/edit'
HEADER_ROWS = {'Collection': 4, 'Deck Allocations': 4,
               'Mechanics · Units': 1, 'Mechanics · Operations': 1}
REQUIRED_COLLECTION = {'Card Name', 'Known Qty (min)', 'Copies in Decks',
                       'Copies Free', 'Oracle Text', 'Roles', 'Color Identity'}
REQUIRED_ALLOC = {'Card Name', 'Deck', 'Status', 'Quantity'}


def _idx(cell_reference):
    col = re.match(r'[A-Z]+', cell_reference).group(0)
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx_selected(path, wanted=None):
    """Read data-only values and cached formula outputs from selected OOXML tabs."""
    wanted = wanted or set(HEADER_ROWS)
    output = {}
    with ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall(f'{{{NS}}}si'):
                strings.append(''.join(t.text or '' for t in si.iter(f'{{{NS}}}t')))
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        relations = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        byid = {r.get('Id'): r.get('Target').lstrip('/') for r in relations}
        for sheet in wb.findall(f'.//{{{NS}}}sheet'):
            name = sheet.get('name')
            if name not in wanted:
                continue
            rel = sheet.get(f'{{{REL}}}id')
            if rel not in byid:
                raise ValueError(f'Workbook missing relationship for {name}')
            target = byid[rel]
            target = target if target.startswith('xl/') else 'xl/' + target
            root = ET.fromstring(z.read(target))
            all_rows = []
            for row in root.findall(f'.//{{{NS}}}sheetData/{{{NS}}}row'):
                cells = {}
                for c in row.findall(f'{{{NS}}}c'):
                    cr = c.get('r')
                    if not cr:
                        continue
                    v = c.find(f'{{{NS}}}v')
                    inline = c.find(f'{{{NS}}}is')
                    if v is not None:
                        value = v.text or ''
                        if c.get('t') == 's':
                            value = strings[int(value)]
                    elif inline is not None:
                        value = ''.join(t.text or '' for t in inline.iter(f'{{{NS}}}t'))
                    else:
                        # Uncached formulas and blank cells remain unknown, not 0.
                        continue
                    cells[_idx(cr)] = value
                if cells:
                    all_rows.append((int(row.get('r')), cells))
            header_num = HEADER_ROWS[name]
            heads = next((v for r, v in all_rows if r == header_num), None)
            if heads is None:
                raise ValueError(f'Missing header row {header_num} in {name}')
            headers = {k: str(v).strip() for k, v in heads.items()}
            rows = []
            for row_number, cells in all_rows:
                if row_number <= header_num:
                    continue
                record = {h: cells.get(i, '') for i, h in headers.items() if h}
                if any(str(v).strip() for v in record.values()):
                    record['_row'] = row_number
                    rows.append(record)
            output[name] = rows
    if set(output) != set(wanted):
        raise ValueError(f'Missing tabs: {set(wanted) - set(output)}')
    return output


def qty(raw, label, diagnostics):
    try:
        v = float(raw)
        if not v.is_integer() or v < 0:
            raise ValueError()
        return int(v)
    except (ValueError, TypeError):
        diagnostics.append(f'Invalid nonnegative integer quantity for {label}: {raw!r}')
        return None


def status_group(label):
    label = str(label).strip()
    if label == 'Current deck':
        return 'physically_allocated'
    if label == 'Companion':
        return 'companion_outside_deck_100'
    if label.startswith('Candidate') or label == 'Held-out candidate':
        return 'proposal_no_physical_move'
    if 'bench' in label.lower() or 'reserve' in label.lower() or label in ('Land pool', 'Unallocated', 'Evaluated / available'):
        return 'available_or_bench_not_allocated'
    if label.startswith('Free / unassigned'):
        return 'free_not_allocated'
    return 'other_not_allocated'


def normalize(raw):
    errors = []
    collection, allocations, units, operations = [raw[k] for k in HEADER_ROWS]
    if collection and not REQUIRED_COLLECTION <= set(collection[0]):
        errors.append('Collection mandatory columns missing')
    if allocations and not REQUIRED_ALLOC <= set(allocations[0]):
        errors.append('Deck Allocations mandatory columns missing')
    card_by_name, duplicate_names = {}, []
    for r in collection:
        name = str(r.get('Card Name', '')).strip()
        if not name:
            continue
        if name in card_by_name:
            duplicate_names.append(name)
        card_by_name[name] = r
    status_counts, assigned, decks, external = collections.Counter(), collections.Counter(), collections.defaultdict(list), []
    for r in allocations:
        name = str(r.get('Card Name', '')).strip()
        g = status_group(r.get('Status', ''))
        status_counts[g] += 1
        count = qty(r.get('Quantity', ''), f'allocation row {r["_row"]} ({name})', errors)
        if count is None:
            continue
        if name not in card_by_name:
            external.append(name)
        if g in ('physically_allocated', 'companion_outside_deck_100'):
            assigned[name] += count
            if g == 'physically_allocated':
                decks[str(r.get('Deck', '')).strip()].append({'card': name, 'quantity': count, 'section': r.get('Section',''), 'source_row':r['_row']})
    op_by_card = collections.defaultdict(list)
    op_status = collections.Counter()
    for r in operations:
        n = r.get('Card Name', '')
        op_by_card[n].append(r)
        op_status[str(r.get('Status', '')).strip()] += 1
    unit_by_name = {r['Card Name']:r for r in units if r.get('Card Name')}
    facts, issues, role_hints = [], [], collections.defaultdict(list)
    for name, r in card_by_name.items():
        owned = qty(r.get('Known Qty (min)'), f'Collection owned ({name})', errors)
        reported_assigned = qty(r.get('Copies in Decks'), f'Collection assigned ({name})', errors)
        reported_free = qty(r.get('Copies Free'), f'Collection free ({name})', errors)
        computed_assigned = assigned[name]
        free = owned-computed_assigned if owned is not None else None
        if owned is not None and computed_assigned > owned:
            issues.append({'severity':'critical','kind':'overallocated','card':name,'owned':owned,'assigned':computed_assigned})
        if reported_assigned is not None and reported_assigned != computed_assigned:
            issues.append({'severity':'high','kind':'collection_assigned_mismatch','card':name,'stored':reported_assigned,'computed':computed_assigned})
        if reported_free is not None and free is not None and reported_free != free:
            issues.append({'severity':'high','kind':'collection_free_mismatch','card':name,'stored':reported_free,'computed':free})
        unit = unit_by_name.get(name)
        if unit:
            uassigned = qty(unit.get('Assigned Qty'), f'Unit assigned ({name})', errors)
            if uassigned is not None and uassigned != computed_assigned:
                issues.append({'severity':'low','kind':'stale_mechanics_unit_assignment','card':name,'stored':uassigned,'computed':computed_assigned})
        roles = [x.strip() for x in str(r.get('Roles','')).split(';') if x.strip()]
        for role in roles:
            role_hints[role].append(name)
        facts.append({
            'card_name':name, 'owned_min':owned, 'assigned':computed_assigned, 'free_computed':free,
            'ownership':r.get('Ownership',''), 'color_identity':r.get('Color Identity',''),
            'mana_cost':r.get('Mana Cost',''), 'mana_value':r.get('Mana Value',''),
            'type_line':r.get('Type Line',''), 'commander_legal_recorded':r.get('Commander Legal',''),
            'can_be_commander_recorded':r.get('Can Be Commander',''),
            'oracle_text_recorded':r.get('Oracle Text',''), 'scryfall_url_recorded':r.get('Scryfall URL',''),
            'role_hints':roles, 'keywords_indexed':r.get('Keywords',''), 'produces_indexed':r.get('Produces',''),
            'evidence':{'ownership':'Collection plus Deck Allocations','oracle_text':'stored inventory text; not freshly Oracle-verified',
                        'roles':'unverified inventory tag hints','mechanics':'candidate-only unless independently promoted'},
            'candidate_operations_indexed':len(op_by_card.get(name,[]))
        })
    facts.sort(key=lambda r:r['card_name'].casefold())
    count_decks = {n:sum(c['quantity'] for c in v) for n,v in decks.items()}
    for d, n in count_decks.items():
        if n != 100:
            issues.append({'severity':'high','kind':'deck_size_not_100','deck':d,'count':n})
    for x in duplicate_names:
        issues.append({'severity':'critical','kind':'duplicate_collection_name','card':x})
    for n in set(external):
        issues.append({'severity':'critical','kind':'allocation_unknown_card','card':n})
    health = {
        'cards_in_collection':len(facts),'card_names_with_known_copies':sum(bool((r['owned_min'] or 0)>0) for r in facts),
        'known_physical_copy_minimum':sum(r['owned_min'] or 0 for r in facts),
        'current_decks':len(decks),'deck_counts':dict(sorted(count_decks.items())),
        'allocation_status_rows':dict(sorted(status_counts.items())),
        'mechanics_units':len(units),'mechanics_operations':len(operations),
        'mechanics_statuses':dict(op_status),
        'known_problems':dict(collections.Counter(i['kind'] for i in issues)),
        'critical_problems':sum(i['severity']=='critical' for i in issues),
        'high_problems':sum(i['severity']=='high' for i in issues),
        'parse_errors':errors,
        'model_note':'Functional role tags and candidate operations are NOT independently rules-verified.'
    }
    deck_lists = [{'deck':n,'card_count':count_decks[n],'named_rows':len(rows),'cards':rows} for n,rows in sorted(decks.items())]
    operation_index = [{k:v for k,v in r.items() if k != '_row'} | {'source_row':r['_row'],'evidence_status':'extracted_candidate_not_verified'} for r in operations]
    return {'health':health,'facts':facts,'deck_lists':deck_lists,'operations':operation_index,
            'role_hints':{k:sorted(v) for k,v in sorted(role_hints.items())}, 'issues':issues}


def dump_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')


def jsonl(path, rows):
    with path.open('w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')


def build(workbook, outdir, source_id=CANONICAL_ID):
    workbook=Path(workbook); outdir=Path(outdir)
    start=hashlib.sha256(workbook.read_bytes()).hexdigest()
    data=normalize(read_xlsx_selected(workbook))
    if any(x['severity']=='critical' for x in data['issues']):
        raise ValueError(f'Critical inventory issues: {data["health"]["critical_problems"]}')
    outdir.mkdir(parents=True, exist_ok=True)
    provenance={'live_canonical_id':source_id,'live_canonical_url':CANONICAL_URL,
                'input_file_name':workbook.name, 'input_sha256':start,
                'snapshot_mode':'read-only local OOXML extract; refresh after live inventory changes',
                'verified_live_sentinels':['Arcane Signet Collection assigned=9; Mechanics Unit assigned=7',
                                           '38 tabs; current deck count 12'],
                'project_reference_status':'external project configured file ID must be updated separately'}
    dump_json(outdir/'SOURCE_AND_AUTHORITY.json',provenance)
    dump_json(outdir/'health.json',data['health'])
    dump_json(outdir/'discrepancies.json',data['issues'])
    dump_json(outdir/'deck_lists.json',data['deck_lists'])
    dump_json(outdir/'role_hint_index.json',data['role_hints'])
    jsonl(outdir/'card_facts.jsonl',data['facts'])
    jsonl(outdir/'mechanics_candidates.jsonl',data['operations'])
    end=hashlib.sha256(workbook.read_bytes()).hexdigest()
    if start != end:
        raise RuntimeError('Source workbook hash changed unexpectedly!')
    return data['health']


def query(outdir, card=None, deck=None):
    outdir=Path(outdir)
    if card:
        with (outdir/'card_facts.jsonl').open(encoding='utf-8') as f:
            result=[json.loads(s) for s in f if json.loads(s).get('card_name','').casefold()==card.casefold()]
        print(json.dumps(result,indent=2,ensure_ascii=False))
    if deck:
        rows=json.loads((outdir/'deck_lists.json').read_text())
        print(json.dumps([r for r in rows if r['deck'].casefold()==deck.casefold()],indent=2,ensure_ascii=False))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workbook',help='Read-only OOXML snapshot of live canonical sheet')
    p.add_argument('--outdir',default='generated',help='Location for regenerated AI-friendly indexes')
    p.add_argument('--card',help='Query an exported card fact record')
    p.add_argument('--deck',help='Query an exported full 100-card deck list')
    a=p.parse_args()
    if a.workbook:
        print(json.dumps(build(a.workbook,a.outdir),indent=2))
    else:
        if not (a.card or a.deck):p.error('Supply --workbook to build or --card/--deck to query')
        query(a.outdir,a.card,a.deck)

if __name__=='__main__': main()
