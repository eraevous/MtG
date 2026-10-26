#!/usr/bin/env python3
"""Package one self-contained release: DB(s), code, overrides, refresh snapshots, scenarios, addendum,
reports, reference sources, SOURCE_MANIFEST.json and MANIFEST.sha256 (every file's SHA-256).

  python release.py --out /path/to/mtg_kb_v0.2.1        (then zip the folder; run the suites from the extracted copy)
"""
import argparse, hashlib, json, shutil, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review as R, reconcile as RC, scenarios as SC

INCLUDE = ['mtg_cards.sqlite', 'mtg_cards_v0.2.sqlite', 'schema.sql', 'schema_v02.sql', 'README.md', 'README_v0.2.md', 'RELEASE_NOTES_v0.2.1.md', 'RELEASE_NOTES_v0.2.1-r20261024.md', 'RELEASE_NOTES_v0.2.1-r20261024b.md', 'RELEASE_NOTES_v0.2.1-r20261024c.md', 'RELEASE_NOTES_v0.2.1-r20261024d.md',
           'ONTOLOGY_ALIGNMENT.md', 'CLAUDE_HANDOFF.md', 'AUDIT.json', 'VERSION.json',
           'addendum', 'overrides', 'refresh', 'scenarios', 'reports', 'reference_sources', 'vendor', 'mtg_eval_release',
           'MTG_Inventory_Governance_2026-10-18']
SKIP = {'__pycache__', '.building'}
RELEASE = 'mtg-kb-v0.2.1-r20261024d'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def copy(out):
    for name in INCLUDE + sorted(p.name for p in HERE.glob('*.py')):
        src = HERE / name
        if not src.exists(): continue
        if src.is_dir(): shutil.copytree(src, out / name, ignore=shutil.ignore_patterns(*SKIP, '*.pyc'))
        else: shutil.copy2(src, out / name)


def manifest(out):
    db = sqlite3.connect((out / 'mtg_cards_v0.2.sqlite').resolve().as_uri() + '?mode=ro', uri=True)
    meta = dict(db.execute('select key,value from meta'))
    run = db.execute('select * from oracle_refresh_runs order by started_utc desc limit 1').fetchone()
    cols = [d[0] for d in db.execute('select * from oracle_refresh_runs limit 0').description]
    run = dict(zip(cols, run))
    imp = db.execute('select source_drive_id,source_modified_utc,built_utc,tool from import_runs').fetchone()
    q = lambda s: db.execute(s).fetchone()[0]
    reviews = R.read_overlay(out / 'overrides' / 'review_overlay.jsonl')
    recs = RC.read(out / 'overrides' / 'oracle_reconciliation.jsonl')
    v = db.execute('select sum(oracle_identity_confirmed),sum(rules_text_current),sum(semantic_contract_reviewed),sum(runtime_compilation_complete),'
                   'sum(runtime_scenario_tested),sum(mechanically_supported),sum(quarantined) from contract_verification').fetchone()
    m = {
        'release': RELEASE, 'schema_version': meta['schema_version'], 'built_utc': meta['v02_built_utc'],
        'authorities': {'inventory': 'working Google Sheet (cards.* via the v0.1 import; never edited)',
                        'rules_text': f"Scryfall Oracle, refresh run {run['run_id']} (rules_text table)",
                        'semantic_review': 'overrides/review_overlay.jsonl (append-only, hash-chained)',
                        'runtime_certification': 'issued by the build from scenarios/*.json (runtime_certifications table)'},
        'inventory_source': {'canonical_sheet_id': imp[0], 'drive_modified_utc': imp[1], 'input_name': meta.get('input_name'),
                             'input_sha256': meta['input_sha256'], 'v01_database_sha256': sha(out / 'mtg_cards.sqlite'),
                             'note': 'read-only export; no Sheet edit during this release'},
        'oracle_refresh': {'run_id': run['run_id'], 'source_kind': run['source_kind'], 'source_name': run['source_name'],
                           'source_json_array_sha256': run['source_sha256'], 'source_updated_at': run['source_updated_at'],
                           'downloaded_file': run['source_name'].replace('.json', '.jsonl.gz') + ' (Scryfall bulk download, converted to a JSON array)',
                           'tool_version': run['tool_version'], 'snapshot': run['notes'], 'snapshot_sha256': sha(out / 'refresh' / run['notes']),
                           'cards_matched': run['cards_matched'], 'cards_unmatched': run['cards_unmatched'], 'discrepancies': run['discrepancies']},
        'overrides': {'review_overlay': {'lines': len(reviews), 'head': reviews[-1]['review_id'] if reviews else None,
                                         'sha256': sha(out / 'overrides' / 'review_overlay.jsonl')},
                      'oracle_reconciliation': {'lines': len(recs), 'head': recs[-1]['reconciliation_id'] if recs else None,
                                                'sha256': sha(out / 'overrides' / 'oracle_reconciliation.jsonl')}},
        'scenarios': {'count': len(SC.load(out / 'scenarios')), 'registry_sha256': SC.registry_sha(out / 'scenarios'), 'version': meta['scenario_version']},
        'addendum': {'version': meta['addendum_version'], 'registry_delta_sha256': sha(out / 'addendum' / 'registry_delta_v0.1.json')},
        'versions': {k: meta[k] for k in ('derivation_version', 'drafter_version', 'compiler_version')} | {'mtg_eval_vendored': '0.3.0+kb2', 'migrate': imp[3]},
        'database': {'file': 'mtg_cards_v0.2.sqlite', 'sha256': sha(out / 'mtg_cards_v0.2.sqlite'), 'bytes': (out / 'mtg_cards_v0.2.sqlite').stat().st_size,
                     'counts': {'cards': q('select count(*) from cards'), 'candidate_operations': q('select count(*) from candidate_operations'),
                                'contracts': q('select count(*) from operation_contracts'), 'derived_facts': q('select count(*) from derived_facts'),
                                'oracle_ids': q('select count(*) from card_identity where oracle_id is not null'),
                                'queue': dict(db.execute('select queue_state,count(*) from validation_queue group by 1').fetchall()),
                                'verification': dict(zip(['oracle_identity_confirmed', 'rules_text_current', 'semantic_contract_reviewed',
                                                          'runtime_compilation_complete', 'runtime_scenario_tested', 'mechanically_supported', 'quarantined'], v)),
                                'runtime_certifications': q('select count(*) from runtime_certifications where passed=1'),
                                'compiled_actions': q('select count(*) from compiled_actions')}},
        'rebuild': f"python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl "
                   f"--refresh-dir refresh --source-modified {imp[1]} --built-utc {meta['v02_built_utc']}",
        'tests': 'python -m unittest test_v02.py test_mtg_db.py test_acceptance.py',
    }
    (out / 'SOURCE_MANIFEST.json').write_text(json.dumps(m, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = [f'{sha(p)}  {p.relative_to(out).as_posix()}' for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'MANIFEST.sha256']
    (out / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return m, len(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists(): raise SystemExit(f'{out} exists; a release folder is never overwritten')
    out.mkdir(parents=True)
    copy(out)
    m, n = manifest(out)
    print(json.dumps({'release': str(out), 'files': n, 'database_sha256': m['database']['sha256']}, indent=1))


if __name__ == '__main__':
    main()
