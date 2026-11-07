#!/usr/bin/env python3
"""Reconcile verified intake against a CSV export of the Collection tab.

Read-only with respect to the canonical inventory, deck assignments and KB.
Accepts PR #36's verified CSV or the complete voice-intake review JSON.
No dependencies beyond Python's standard library. Inventory authority remains the
canonical Google Sheet; exports and this script's outputs are staging artifacts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_TITLE = 'MTG Master Inventory — Canonical'
MANDATORY = ('Card Name', 'Known Qty (min)', 'Copies in Decks', 'Copies Free', 'Current Deck(s)')
DETAIL_COLUMNS = ('source_line', 'card_name', 'quantity', 'set_code', 'collector_number',
                  'finish', 'identity_status', 'identity_evidence', 'source_text', 'notes')
RECON_COLUMNS = ('card_name', 'match_status', 'canonical_row', 'known_qty_before',
                 'new_copies', 'proposed_known_qty_min', 'copies_in_decks',
                 'free_before', 'proposed_free_min', 'current_decks', 'review_required',
                 'review_reason', 'printings')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(text):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', str(text))
                  .encode('ascii', 'ignore').decode('ascii').casefold())


def integer(value, field, row, *, default=None):
    s = str(value if value is not None else '').strip()
    if not s and default is not None:
        return default
    if not re.fullmatch(r'\d+', s):
        raise ValueError(f'row {row}: {field} must be a nonnegative whole number, got {s!r}')
    return int(s)


def read_collection(path):
    """Find headings by name (normally row four) and reject partial/duplicate rows."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        lines = list(csv.reader(f))
    header_at = next((i for i, r in enumerate(lines[:12]) if set(MANDATORY).issubset(r)), None)
    if header_at is None:
        raise ValueError('Collection CSV lacks required named headers: ' + ', '.join(MANDATORY))
    header = lines[header_at]
    entries = {}
    for idx, cells in enumerate(lines[header_at + 1:], header_at + 2):
        if not cells or not any(v.strip() for v in cells):
            continue
        row = dict(zip(header, cells + [''] * max(0, len(header) - len(cells))))
        name = row['Card Name'].strip()
        if not name:
            raise ValueError(f'Collection row {idx}: values without card name')
        if name in entries:
            raise ValueError(f'Collection has duplicate card name: {name!r}')
        owned = integer(row['Known Qty (min)'], 'Known Qty (min)', idx)
        in_decks = integer(row['Copies in Decks'], 'Copies in Decks', idx)
        free = integer(row['Copies Free'], 'Copies Free', idx)
        entries[name] = dict(row=row, row_number=idx, owned=owned, assigned=in_decks, free=free)
    return entries, header_at + 1


def read_intake(path):
    """Accept exact Scryfall results or a reviewed/edited CSV, retaining nonaccepted JSON rows."""
    path = Path(path)
    if path.suffix.lower() == '.json':
        raw = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(raw.get('cards'), list):
            raise ValueError('Intake JSON must contain cards[] (voice_intake.py review report)')
        rows = []
        for i, item in enumerate(raw['cards'], 1):
            status = str(item.get('status') or 'unresolved').lower()
            rows.append({'source_line': item.get('line', i), 'card_name': item.get('name') or '',
                         'quantity': item.get('quantity'), 'set_code': item.get('set_code') or '',
                         'collector_number': item.get('collector_number') or '',
                         'finish': item.get('finish') or '', 'identity_status': status,
                         'identity_evidence': item.get('method') or '',
                         'source_text': item.get('spoken') or '',
                         'notes': item.get('reason') or ''})
        return rows
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if not rows or not ('Card Name' in rows[0] and 'Quantity' in rows[0]):
        raise ValueError('Intake CSV must have Card Name and Quantity columns')
    result = []
    for i, row in enumerate(rows, 2):
        result.append({'source_line': row.get('Line', i), 'card_name': row['Card Name'],
                       'quantity': row['Quantity'], 'set_code': row.get('Set Code') or '',
                       'collector_number': row.get('Collector Number') or '',
                       'finish': row.get('Finish') or '',
                       'identity_status': row.get('Status') or 'accepted',
                       'identity_evidence': row.get('Method') or 'accepted-csv',
                       'source_text': row.get('Original Dictation') or '',
                       'notes': row.get('Notes') or ''})
    return result


def csv_write(path, rows, fields):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def reconcile(collection, intake, *, require_finish=False):
    """Produce reviewable proposals, never inferred physical changes."""
    folded = defaultdict(list)
    for name in collection:
        folded[norm(name)].append(name)
    candidates = defaultdict(list)
    details, review = [], []
    for i, source in enumerate(intake, 1):
        row = dict(source)
        for key in DETAIL_COLUMNS:
            row.setdefault(key, '')
        name = str(row.get('card_name') or '').strip()
        status = str(row.get('identity_status') or '').strip().lower()
        row['identity_status'] = status
        row['card_name'] = name
        try:
            q = integer(row.get('quantity'), 'quantity', row.get('source_line') or i)
            if q == 0:
                raise ValueError('quantity must be positive')
        except ValueError as exc:
            row['notes'] = (str(row.get('notes') or '') + '; ' + str(exc)).strip('; ')
            status = 'unresolved'
            q = 0
        row['quantity'] = q
        finish = str(row.get('finish') or '').strip().lower()
        row['finish'] = finish
        details.append(row)
        if status != 'accepted' or not name or not q:
            review.append({'source_line': row.get('source_line'), 'reason': 'identity_not_accepted',
                           'card_name': name, 'status': status})
            continue
        if name not in collection and folded.get(norm(name)):
            review.append({'source_line': row.get('source_line'), 'reason': 'possible_alias_requires_review',
                           'card_name': name, 'canonical_candidates': folded[norm(name)]})
            continue
        if require_finish and not finish:
            review.append({'source_line': row.get('source_line'), 'reason': 'finish_unspecified',
                           'card_name': name})
            continue
        candidates[name].append(row)
    proposals = []
    for name in sorted(candidates, key=str.casefold):
        incoming = candidates[name]
        base = collection.get(name)
        before = base['owned'] if base else 0
        assigned = base['assigned'] if base else 0
        free_before = base['free'] if base else 0
        add = sum(r['quantity'] for r in incoming)
        new = before + add
        issues = []
        if base and before < assigned:
            issues.append('existing_overallocated')
        if base and free_before != max(0, before - assigned):
            issues.append('current_free_does_not_equal_qty_minus_deck_copies')
        if any(not r['finish'] for r in incoming):
            issues.append('some_printing_finishes_unspecified')
        proposals.append({
            'card_name': name, 'match_status': 'existing_exact' if base else 'new_exact_name',
            'canonical_row': base['row_number'] if base else '',
            'known_qty_before': before, 'new_copies': add, 'proposed_known_qty_min': new,
            'copies_in_decks': assigned, 'free_before': free_before,
            'proposed_free_min': max(0, new - assigned),
            'current_decks': base['row']['Current Deck(s)'] if base else '',
            'review_required': 'YES' if issues else 'NO', 'review_reason': '; '.join(issues),
            'printings': '; '.join(f"{r['set_code'] or '?'} #{r['collector_number'] or '?'}"
                                   f" [{r['finish'] or 'finish unknown'}] ×{r['quantity']}" for r in incoming)})
    accounted = sum(r['new_copies'] for r in proposals)
    accepted_row_ids = {id(v) for group in candidates.values() for v in group}
    skipped = sum(r['quantity'] for r in details if id(r) not in accepted_row_ids)
    assert accounted + skipped == sum(r['quantity'] for r in details)
    result = {
        'status': 'PROPOSAL_ONLY_NOT_APPLIED',
        'collection_names_read': len(collection),
        'intake_rows_read': len(details), 'intake_physical_copies_read': sum(r['quantity'] for r in details),
        'proposal_names': len(proposals), 'proposal_copies': accounted,
        'review_rows': len(review), 'skipped_copies': skipped,
        'finish_unspecified_rows': sum(not r['finish'] for r in details if r['identity_status'] == 'accepted'),
        'review': review,
        'limits': ['Source CSV may not be the latest canonical Sheet; the caller must verify title and freshness.',
                   'Staging never proves ownership or changes allocations; approval and physical verification are separate.',
                   'An absent name means absent from this source only, not known unowned.',
                   'Finish unknown never means nonfoil.'],
    }
    return proposals, details, result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build an MTG intake reconciliation review packet; never apply changes')
    parser.add_argument('--collection', required=True, help='CSV export of canonical Collection tab (row 4 header)')
    parser.add_argument('--intake', required=True, help='accepted CSV or complete review JSON from voice_intake')
    parser.add_argument('--output', required=True, help='directory for proposal.csv, intake_detail.csv, review.json')
    parser.add_argument('--source-title', required=True, help='externally verified Google Sheet title; not a trust claim')
    parser.add_argument('--require-finish', action='store_true', help='quarantine rows whose foil/finish was not recorded')
    args = parser.parse_args(argv)
    if args.source_title != CANONICAL_TITLE:
        parser.error('source-title is not the exact canonical Sheet title; archive or snapshot must not be treated as live')
    try:
        collection, header_at = read_collection(args.collection)
        intake = read_intake(args.intake)
        proposals, details, report = reconcile(collection, intake, require_finish=args.require_finish)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f'Intake reconciliation failed: {exc}\n')
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    csv_write(out / 'proposal.csv', proposals, RECON_COLUMNS)
    csv_write(out / 'intake_detail.csv', details, DETAIL_COLUMNS)
    report.update({'generated_utc': datetime.now(timezone.utc).isoformat(),
                   'canonical_title_declared': args.source_title,
                   'canonical_header_row': header_at,
                   'collection_csv_sha256': digest(args.collection),
                   'intake_source_sha256': digest(args.intake),
                   'intake_source': Path(args.intake).name})
    (out / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'out': str(out), 'status': report['status'], 'proposal_names': report['proposal_names'],
                      'proposal_copies': report['proposal_copies'], 'review_rows': report['review_rows']},
                     ensure_ascii=False))
    return 0 if not report['review_rows'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
