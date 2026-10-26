#!/usr/bin/env python3
"""Build mtg_cards_v0.2.sqlite from a v0.1 database. Deterministic, additive, never edits the input.

  PYTHONHASHSEED=0 python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite \
      --overlay overrides/review_overlay.jsonl [--refresh-dir refresh/] [--source-modified 2026-10-15T19:03:42.774Z]

Steps: copy v0.1 -> add v0.2 schema -> provisional card identity/faces -> DIO compatibility addendum
-> replay the review overlay, Oracle refresh snapshots and Oracle reconciliation -> rules-text layer
(Oracle is the rules authority; the Sheet stays the inventory authority) -> persist derived facts
(the only regex run, on the policy-applied inventory) -> draft operation contracts + validation checks
-> runtime loss analysis -> compile semantically reviewed, lossless contracts -> runtime certificates
from scenario runs -> the six verification states -> provenance. Writes to a temp file and renames on success.
"""
import argparse, datetime, json, os, re, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kbfacts as F, contracts as K, review as R, oracle_refresh as O, reconcile as RC, scenarios as SC
from freeze_check import is_archive

TOOL = 'migrate_v02-0.2.1'
SCHEMA_VERSION = '0.2.1'


def archive_guard(name):
    """Archives are recovery copies; never a build input for current custody."""
    if is_archive(name): raise SystemExit(f'refusing archive as build input: {name}')
    return 'not_archive'


def load_addendum(con, path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    ad = d['addendum']
    for h in d['hook_identifiers']:
        con.execute('insert into ontology_addendum values(?,?,?,?,?)', (ad, 'hook_identifier', h['value'], h.get('decision'), json.dumps(h)))
    for x in d['aliases']:
        con.execute('insert into ontology_addendum values(?,?,?,?,?)', (ad, 'alias', x['legacy'], x.get('decision'), json.dumps(x)))
    for x in d['domains']:
        con.execute('insert into ontology_addendum values(?,?,?,?,?)', (ad, 'domain', x['domain'], x.get('decision'), json.dumps(x)))
    for x in d['keyword_macros']:
        con.execute('insert into ontology_addendum values(?,?,?,?,?)', (ad, 'keyword_macro', x['id'], x.get('decision'), json.dumps(x)))
    return ad, {h['value'] for h in d['hook_identifiers']}


def build_rules_text(con):
    """One row per card: Oracle (latest matched refresh) is the rules authority unless a reconciliation excludes the row."""
    latest = {}
    for r in con.execute('select e.*, r.started_utc from external_oracle e join oracle_refresh_runs r using(run_id) order by r.started_utc'):
        latest[r['card_name']] = r
    rec = {r['card_name']: r for r in con.execute('select * from effective_reconciliation')}
    n = 0
    for c in con.execute('select card_name,oracle_text,oracle_text_sha256 from cards order by card_name').fetchall():
        e, z = latest.get(c['card_name']), rec.get(c['card_name'])
        reads = z['evaluator_reads'] if z else 'sheet'
        material = int(bool(z and z['material']))
        if z and reads == 'excluded':
            row = ('excluded (' + z['category'] + ')', e and e['run_id'], e and e['oracle_id'], None, None, e and e['match_status'],
                   int(bool(z['identity_confirmed'])))
        elif e is not None and e['match_status'] != 'not_found':
            ident = 1
            if z and z['identity_confirmed'] is not None: ident = int(bool(z['identity_confirmed']))
            row = ('oracle_refresh', e['run_id'], e['oracle_id'], e['external_text'], e['external_text_sha256'], e['match_status'], ident)
        else:
            row = ('inventory_row (no Oracle match)', None, None, c['oracle_text'], c['oracle_text_sha256'], e and e['match_status'], 0)
        con.execute('insert into rules_text values(?,?,?,?,?,?,?,?,?,?,?,?)', (c['card_name'], row[0], row[1], row[2], row[3], row[4],
                    c['oracle_text_sha256'], row[5], row[6], material, reads, z and z['reconciliation_id']))
        for i, line in enumerate([x.strip() for x in (row[3] or '').split('\n') if x.strip() and x.strip() != '//']):
            con.execute('insert into rules_text_lines values(?,?,?)', (c['card_name'], i, line))
        n += 1
    return n


FACE_HEADER = re.compile(r"^[A-Z][\w' ,\-]+ (?:— (?:\{[^}]*\})+, (?:Sorcery|Instant)|\((?:\{[^}]*\})+\)):\s*")


def rules_key(t, name, keep_reminder=False):
    t = FACE_HEADER.sub('', t.strip())
    if keep_reminder: t = t.replace('(', ' ').replace(')', ' ')
    k = K.clause_key(t, name).replace(' - ', ' ')
    return re.sub(r"['\"]", '', re.sub(r'\s+', ' ', k)).strip()


def rules_text_current(contract_text, rt, name):
    """Does the contract's clause say what the Oracle rules text says? Representational differences
    (face headers, reminder text, self-reference, quotes, dashes) are normalised away."""
    if rt is None or rt['authority'] != 'oracle_refresh' or not rt['identity_confirmed'] or rt['material_discrepancy']: return False
    if rt['match_status'] in ('identical', 'normalized_equal'): return True
    return any(bool(k) and k in rules_key(rt['rules_text'] or '', name, kr) for kr in (False, True) for k in [rules_key(contract_text, name, kr)])


def compile_and_certify(con, built, registry, oracle_run):
    """Loss analysis for every contract; compile the reviewed lossless ones; issue runtime certificates."""
    for t in ('compiled_actions', 'compile_losses', 'runtime_certifications'): con.execute(f'delete from {t}')
    by_contract = {}
    for s in registry.values(): by_contract.setdefault(s['contract_id'], []).append(s)
    stats = {'lossless': 0, 'lossy': 0, 'compiled': 0, 'certified': 0, 'cert_failed': 0}
    rows = con.execute('select q.contract_id,q.contract_version,q.card_name,q.queue_state,k.contract_sha256,k.contract_json,k.proposed_action_json,'
                       'e.review_id from validation_queue q join operation_contracts k using(contract_id,contract_version) '
                       "left join effective_reviews e on e.subject_kind='operation_contract' and e.subject_id=q.contract_id").fetchall()
    for q in rows:
        c = F.loads(q['contract_json']); act = json.loads(q['proposed_action_json']) if q['proposed_action_json'] else None
        losses = K.runtime_losses(c, act)
        con.executemany('insert or ignore into compile_losses values(?,?,?,?,?)',
                        [(q['contract_id'], q['contract_version'], K.COMPILER_VERSION, code, d) for code, d in losses])
        if losses:
            stats['lossy'] += 1
            if q['queue_state'] == 'semantic_reviewed':
                con.execute('insert or ignore into qa_queue values(?,?,?,?,?,?,?,?)', (F.sha('compile', q['contract_id'], q['contract_sha256'])[:16],
                            'reviewed_contract_lossy_compile', q['card_name'], 'medium', K.COMPILER_VERSION, built,
                            json.dumps({'contract_id': q['contract_id'], 'losses': losses[:10]}), 'open'))
            continue
        stats['lossless'] += 1
        if q['queue_state'] == 'semantic_reviewed':
            compiled = K.compile_action(c, act, q['review_id'])
            con.execute('insert into compiled_actions values(?,?,?,?,?,?)', (q['contract_id'], q['contract_version'], q['card_name'],
                        K.COMPILER_VERSION, json.dumps(compiled), q['review_id'])); stats['compiled'] += 1
        for s in by_contract.get(q['contract_id'], []):
            if 'runtime' not in s: continue
            card = con.execute('select type_line from cards where card_name=?', (q['card_name'],)).fetchone()[0] or ''
            types = [w for w in ('artifact', 'creature', 'enchantment', 'land', 'planeswalker') if w in card.lower()] or ['permanent']
            obs = SC.run_action(act, q['card_name'], types)
            ok, _ = SC.check_runtime(s['runtime']['expect'], obs)
            con.execute('insert into runtime_certifications values(?,?,?,?,?,?,?,?,?,?,?,?,?)', (q['contract_id'], q['contract_version'],
                        q['contract_sha256'], s['id'], s['scenario_sha256'], K.COMPILER_VERSION, oracle_run, F.sha(F.dumps(act)),
                        json.dumps(s['runtime']['expect'], sort_keys=True), json.dumps(obs, sort_keys=True), int(ok), SC.SCENARIO_VERSION, built))
            stats['certified' if ok else 'cert_failed'] += 1
    return stats


def verification_states(con):
    rt = {r['card_name']: r for r in con.execute('select * from rules_text')}
    lossy = {(a, b) for a, b in con.execute('select contract_id,contract_version from compile_losses where compiler_version=?', (K.COMPILER_VERSION,))}
    cert = {(a, b) for a, b in con.execute('select contract_id,contract_version from runtime_certifications where passed=1 and compiler_version=?', (K.COMPILER_VERSION,))}
    n = 0
    for q in con.execute('select q.contract_id,q.contract_version,q.card_name,q.queue_state,k.exact_text from validation_queue q '
                         'join operation_contracts k using(contract_id,contract_version)').fetchall():
        key = (q['contract_id'], q['contract_version']); r = rt.get(q['card_name'])
        quar = int(q['queue_state'] == 'quarantined')
        s = {'oracle_identity_confirmed': int(bool(r and r['identity_confirmed'])),
             'rules_text_current': int(not quar and rules_text_current(q['exact_text'], r, q['card_name'])),
             'semantic_contract_reviewed': int(q['queue_state'] == 'semantic_reviewed'),
             'runtime_compilation_complete': int(key not in lossy),
             'runtime_scenario_tested': int(key in cert)}
        s['mechanically_supported'] = int(all(s.values()) and not quar)
        detail = {'queue_state': q['queue_state'], 'rules_authority': r and r['authority'], 'oracle_match': r and r['match_status']}
        con.execute('insert into contract_verification values(?,?,?,?,?,?,?,?,?,?,?)', (q['contract_id'], q['contract_version'], q['card_name'],
                    *s.values(), quar, json.dumps(detail)))
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v01', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--overlay', required=True); ap.add_argument('--source-modified')
    ap.add_argument('--refresh-dir', help='directory of oracle_refresh_*.jsonl snapshots to replay')
    ap.add_argument('--reconciliation', default=str(HERE / 'overrides' / 'oracle_reconciliation.jsonl'))
    ap.add_argument('--addendum', default=str(HERE / 'addendum' / 'registry_delta_v0.1.json'))
    ap.add_argument('--scenarios', default=str(HERE / 'scenarios'))
    ap.add_argument('--built-utc', help='fixed timestamp for reproducible builds')
    a = ap.parse_args()
    built = a.built_utc or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    src = sqlite3.connect(Path(a.v01).resolve().as_uri() + '?mode=ro', uri=True)
    meta = dict(src.execute('select key,value from meta'))
    archive_guard(meta.get('input_name', '')); archive_guard(a.v01)
    tmp = Path(a.out).with_suffix('.building')
    if tmp.exists(): tmp.unlink()
    con = sqlite3.connect(tmp); src.backup(con); src.close()
    con.row_factory = sqlite3.Row
    con.executescript((HERE / 'schema_v02.sql').read_text())

    # 1. provisional identity ---------------------------------------------------------
    cards = {r['card_name']: dict(r) for r in con.execute('select * from cards')}
    for name, c in cards.items():
        m = re.search(r'scryfall\.com/card/([^/]+)/([^/]+)/', c['scryfall_url'] or '')
        con.execute('insert into card_identity values(?,?,?,?,?,?,?,?)',
                    (name, None, 'multi_face' if ' // ' in name else None, m and m.group(1), m and m.group(2), c['scryfall_url'],
                     'inventory_row (oracle_id pending refresh)', None))
        for f in K.faces(c):
            con.execute('insert into card_faces values(?,?,?,?,?,?,?,?)', (name, f['face_index'], f['face_name'], f['mana_cost'],
                        f['type_line'], f['oracle_text'], 'inventory_row', None))

    # 2. DIO compatibility addendum + registry vocabulary ---------------------------------
    addendum, add_hooks = load_addendum(con, a.addendum)
    vocab = set(add_hooks)
    for (dj,) in con.execute("select definition_json from ontology_domains where domain like 'hook.identifier.%'"):
        vocab |= {v['value'] for v in json.loads(dj).get('values', [])}
    print('addendum', addendum, 'hook vocabulary', len(vocab))

    # 3. human review overlay, Oracle refresh, reconciliation, rules-text layer -----------
    print('reviews replayed', R.replay(con, a.overlay))
    print('oracle refresh snapshots replayed', O.replay(con, a.refresh_dir))
    print('reconciliation records replayed', RC.replay(con, a.reconciliation))
    print('rules_text rows', build_rules_text(con))
    oracle_run = (con.execute('select run_id from oracle_refresh_runs order by started_utc desc limit 1').fetchone() or [None])[0]

    # 4. derived facts on the policy-applied inventory ----------------------------------------
    sys.path.insert(0, str(Path(a.v01).resolve().parent)); sys.path.insert(0, str(Path(a.v01).resolve().parent / 'vendor'))
    from sqlite_bridge import SQLiteInventory
    import kb_policy
    inv = SQLiteInventory(a.v01)
    inv.oracle_read = kb_policy.apply(inv, con)
    print('evaluator reads Oracle rules text for', inv.oracle_read)
    from bridge_v02 import DERIVATION_VERSION
    n = 0
    for kind, key, card, val in F.derive(inv):
        con.execute('insert or ignore into derived_facts values(?,?,?,?,?)', (kind, key, card, F.dumps(val), DERIVATION_VERSION)); n += 1
    inv0 = SQLiteInventory(a.v01)  # the Sheet-text reading too, so policy=False (v0.1-equivalent inventory) also runs without regex
    for kind, key, card, val in F.derive(inv0):
        con.execute('insert or ignore into derived_facts values(?,?,?,?,?)', (kind, key, card, F.dumps(val), DERIVATION_VERSION)); n += 1
    print('derived facts', n, 'rows', con.execute('select count(*) from derived_facts').fetchone()[0])

    # 5. contracts + validation -------------------------------------------------------
    proj = {}
    for r in con.execute('select * from projected_abilities order by card_name,ability_index'): proj.setdefault(r['card_name'], []).append(dict(r))
    nc = 0
    for op in con.execute('select * from candidate_operations order by operation_id').fetchall():
        op = dict(op)
        contract, action, checks = K.draft(op, cards[op['card_name']], vocab, proj.get(op['card_name'], []))
        csha = K.contract_sha(contract, action)
        con.execute('insert into operation_contracts values(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (op['operation_id'], 1, csha, op['card_name'], op['operation_id'], contract['source_unit']['face'], contract['exact_text'],
                     cards[op['card_name']]['oracle_text_sha256'], contract['kind'] or 'unclassified', F.dumps(contract),
                     json.dumps(action) if action else None, K.DRAFTER_VERSION, built))
        con.executemany('insert into validation_checks values(?,?,?,?,?)', [(op['operation_id'], 1, i, r, d) for i, r, d in checks])
        nc += 1
    print('contracts', nc)

    # 6. loss analysis, compile, runtime certificates, verification states -----------------
    registry = SC.load(a.scenarios)
    print('scenarios', len(registry), compile_and_certify(con, built, registry, oracle_run))
    print('verification rows', verification_states(con))

    # 7. provenance -------------------------------------------------------------------
    con.execute('insert into import_runs values(?,?,?,?,?,?,?,?,?)', (F.sha(TOOL, meta['input_sha256'], built)[:16], 'v0.2_migration',
                meta.get('input_name'), meta['input_sha256'], meta.get('canonical_sheet_id'), a.source_modified, 'not_archive', built, TOOL))
    con.execute('insert into schema_migrations values(?,?,?,?)', ('0.2.0', built, TOOL, 'derived facts, identity scaffold, contracts, validation queue, review overlay, compiler'))
    con.execute('insert into schema_migrations values(?,?,?,?)', (SCHEMA_VERSION, built, TOOL,
                'rules-text authority + reconciliation + quarantine, DIO addendum, loss gate, scenarios, runtime certificates, six verification states'))
    for k, v in {'schema_version': SCHEMA_VERSION, 'derivation_version': DERIVATION_VERSION, 'drafter_version': K.DRAFTER_VERSION,
                 'compiler_version': K.COMPILER_VERSION, 'addendum_version': addendum, 'scenario_version': SC.SCENARIO_VERSION,
                 'scenario_registry_sha256': SC.registry_sha(a.scenarios), 'oracle_run_id': oracle_run or '', 'v02_built_utc': built,
                 'authority': 'working Google Sheet: inventory authority (source of cards.*); matched Oracle refresh: rules-text authority (rules_text); '
                              'this DB is derived and regenerable; reviews and reconciliations live in overrides/*.jsonl'}.items():
        con.execute('insert or replace into meta values(?,?)', (k, v))
    con.commit()
    assert con.execute('pragma integrity_check').fetchone()[0] == 'ok'
    assert not con.execute('pragma foreign_key_check').fetchall()
    con.execute('vacuum'); con.close()
    os.replace(tmp, a.out)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
