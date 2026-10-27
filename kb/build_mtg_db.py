#!/usr/bin/env python3
"""Rebuild a portable, read-only derived MTG semantic SQLite index from a canonical XLSX export,
or from a bring-your-own collection database (collection/schema.sql; see docs/BRING_YOUR_OWN_COLLECTION.md).
Stdlib-only runtime, vendored v0.3.0 parser; never writes to the source workbook.
Manual review is *not* inferred from machine recognition. Verified rows must be provided separately.
"""
import argparse,collections,datetime,hashlib,json,re,sqlite3,sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'))
from mtg_eval.abilities import card_abilities
from mtg_eval.semantics import capability_record,oracle_functions,wipe_kind,protection_profile,clean,load_labels
from mtg_eval import collection_db
import inventory_adapter as ia

def jsonable(o):
    if isinstance(o,set):return sorted(o)
    if isinstance(o,tuple):return [jsonable(x) for x in o]
    if isinstance(o,list):return [jsonable(x) for x in o]
    if isinstance(o,dict):return {str(k):jsonable(v) for k,v in o.items()}
    return o

def dumps(o):return json.dumps(jsonable(o),ensure_ascii=False,separators=(',',':'),sort_keys=True)

def all_sheet_rows(path):
    # Read the cached data values of *every* sheet, not a formatting/formula-preserving backup.
    with ZipFile(path) as z:
        strs=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            strs=[''.join((v.text or '') for v in t.iter(f'{{{ia.NS}}}t')) for t in root.findall(f'{{{ia.NS}}}si')]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={r.get('Id'):r.get('Target').lstrip('/') for r in rel}
        for sheet in wb.findall(f'.//{{{ia.NS}}}sheet'):
            name=sheet.get('name'); target=targets.get(sheet.get(f'{{{ia.REL}}}id'))
            if not target: continue
            fn=target if target.startswith('xl/') else 'xl/'+target
            root=ET.fromstring(z.read(fn))
            for row in root.findall(f'.//{{{ia.NS}}}sheetData/{{{ia.NS}}}row'):
                v={}
                for c in row.findall(f'{{{ia.NS}}}c'):
                    if not c.get('r'):continue
                    cell=c.find(f'{{{ia.NS}}}v'); inline=c.find(f'{{{ia.NS}}}is')
                    if cell is not None:
                        raw=cell.text or ''
                        if c.get('t')=='s':raw=strs[int(raw)]
                    elif inline is not None: raw=''.join(t.text or '' for t in inline.iter(f'{{{ia.NS}}}t'))
                    else:continue
                    if raw!='':v[c.get('r')]=raw
                if v:yield (name,int(row.get('r')),dumps(v))

def safe_number(v):
    try:return float(v) if str(v).strip()!='' else None
    except (TypeError,ValueError):return None

def parse_runtime(name,oracle,typ,keywords):
    text=clean(oracle or '',name)
    # mtg_eval v0.3.0 normalizes the first name to ~ in non-reminder clauses.
    short=re.split(r'[ ,]',name.split(' // ')[0])[0].lower()
    if len(short)>3:text=re.sub(r'\b'+re.escape(short)+r'\b(?= (?:enters|attacks|deals|dies|leaves|gets|has|is))','~',text)
    return card_abilities(name,text,oracle or '',typ or '',keywords or '')

def build(workbook,db_path,jsonl_out=None):
    workbook=Path(workbook);db_path=Path(db_path)
    before=hashlib.sha256(workbook.read_bytes()).hexdigest()
    is_db=collection_db.is_collection_db(workbook)
    raw=collection_db.read(workbook) if is_db else ia.read_xlsx_selected(workbook)
    data=ia.normalize(raw)
    if data['health']['critical_problems'] or data['health']['high_problems']:
        raise ValueError('Critical or high inventory reconciliation error, refusing misleading rebuild')
    db_path.parent.mkdir(parents=True,exist_ok=True)
    if db_path.exists():db_path.unlink()
    c=sqlite3.connect(db_path)
    c.executescript((HERE/'schema.sql').read_text(encoding='utf-8'))
    parsersrc=(HERE/'vendor/mtg_eval/abilities.py').read_bytes()+(HERE/'vendor/mtg_eval/semantics.py').read_bytes()
    pv='mtg_eval_0.3.0:'+hashlib.sha256(parsersrc).hexdigest()[:16]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if is_db:
        ident=collection_db.identity(workbook)
        sheet_id,source_url,source_type=ident['source_sheet_id'] or 'collection:'+ident['label'],'','read-only collection database'
    else:
        sheet_id,source_url,source_type=ia.CANONICAL_ID,ia.CANONICAL_URL,'read-only mounted canonical workbook snapshot'
    source_meta={'canonical_sheet_id':sheet_id,'canonical_url':source_url,'input_sha256':before,
                 'input_name':workbook.name,'source_type':source_type,
                 'parser':pv,'import_utc':now,'candidate_policy':'none of the machine findings is automatically rules-verified',
                 'rebuild_policy':'regenerate after new live export; archives are rollback-only'}
    c.executemany('INSERT INTO meta VALUES(?,?)',[(k,str(v)) for k,v in source_meta.items()])
    c.execute('INSERT INTO source_snapshots(source_name,source_url,sha256,source_kind,imported_utc,notes) VALUES(?,?,?,?,?,?)',
        (workbook.name,source_url,before,'collection_db' if is_db else 'local_snapshot',now,'Source is never written to.'))
    collection_by={r['Card Name']:r for r in raw['Collection']}
    deck_allocs=raw['Deck Allocations']
    facts=data['facts']
    counters=collections.Counter()
    labels=load_labels()
    for f in facts:
        name=f['card_name'];r=collection_by[name]
        oracle=f['oracle_text_recorded'] or ''
        values=(name,f['owned_min'],f['assigned'],f['free_computed'],r.get('Availability',''),f['color_identity'],f['mana_cost'],
          safe_number(f['mana_value']),f['type_line'],r.get('Rarity',''),r.get('Roles',''),oracle,
          hashlib.sha256(oracle.encode()).hexdigest(),f['keywords_indexed'],f['produces_indexed'],r.get('ETB Tapped',''),
          r.get('Power',''),r.get('Toughness',''),f['commander_legal_recorded'],f['can_be_commander_recorded'],
          f['scryfall_url_recorded'],f['ownership'],r.get('Recorded / Printed Alias',''),r['_row'],dumps(r))
        c.execute('INSERT INTO cards VALUES ('+','.join('?'*len(values))+')',values)
        claims=capability_record(r,labels)
        for role in f['role_hints']:
            c.execute('INSERT OR IGNORE INTO capability_claims VALUES(?,?,?,?,?,?)',
              (name,role,'Collection.Roles','unverified_inventory_tag',None,'collection'))
        for function,info in claims.items():
            status={'supported':'machine_supported','tag_only':'unverified_tag_only','contradicted':'machine_contradicted'}.get(info['status'],'unverified')
            c.execute('INSERT OR IGNORE INTO capability_claims VALUES(?,?,?,?,?,?)',
              (name,function,'mtg_eval.semantic_patterns',status,dumps(info['evidence']),pv))
            counters['capability_claims']+=1
        for function,span in oracle_functions(name,oracle,f['type_line']).items():
            c.execute('INSERT OR IGNORE INTO capability_claims VALUES(?,?,?,?,?,?)',
              (name,function,'oracle_rule_match','machine_inferred',str(span),pv))
        try:
            parsed=parse_runtime(name,oracle,f['type_line'],f['keywords_indexed'])
            abilities=parsed['abilities'];unread=parsed['unread'];statics=parsed['statics']
            for i,a in enumerate(abilities):
                hk=a.get('hook')
                c.execute('INSERT INTO projected_abilities VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (name,i,a.get('kind') or 'unknown',hk[0] if isinstance(hk,tuple) else str(hk or ''),
                   dumps(hk[1]) if isinstance(hk,tuple) else None,dumps(a.get('cost')),dumps(a.get('gates')),
                   dumps(a.get('outputs')),a.get('line',''),a.get('unread',''),a.get('confidence','partial'),pv,dumps(a),'unverified_machine_projection'))
            status='partial' if unread else ('machine_parsed' if abilities or any(v for v in statics.values()) else 'no_projection')
            c.execute('INSERT INTO projected_card_statics VALUES(?,?,?,?,?,?,?)',
                (name,dumps(statics),dumps(unread),len(abilities),len(unread),status,pv))
            counters[status]+=1;counters['ability_projection_rows']+=len(abilities)
        except Exception as ex:
            c.execute('INSERT INTO qa_issues VALUES(?,?,?,?)',('parser_exception',name,'high',dumps({'error':str(ex)})))
            c.execute('INSERT INTO projected_card_statics VALUES(?,?,?,?,?,?,?)',
                  (name,'{}',dumps([str(ex)]),0,1,'parser_error',pv))
            counters['parser_error']+=1
        # typed effect profiles from mtg_eval 0.3, still unverified hypotheses
        t=clean(oracle,name)
        profile={'wipe_kinds':sorted(wipe_kind(t)), 'protection':jsonable(protection_profile(t))}
        c.execute('INSERT INTO typed_profiles VALUES(?,?,?,?)',(name,dumps(profile),pv,'unverified_machine_projection'))
    for row in deck_allocs:
        name=row.get('Card Name','');deck=row.get('Deck','')
        if not name or name not in collection_by:continue
        group=ia.status_group(row.get('Status',''))
        try:quantity=int(float(row.get('Quantity','0')))
        except (ValueError,TypeError): continue
        phys=int(group in ('physically_allocated','companion_outside_deck_100'))
        in100=int(group=='physically_allocated')
        c.execute('INSERT INTO deck_allocations VALUES(?,?,?,?,?,?,?,?,?,?)',
          (row['_row'],name,deck,row.get('Status',''),group,quantity,row.get('Section',''),phys,in100,dumps(row)))
    for row in data['operations']:
        n=row['Card Name']
        if n not in collection_by:
            c.execute('INSERT INTO qa_issues VALUES(?,?,?,?)',('operation_unknown_card',n,'high',dumps(row)));continue
        fields=('Operation ID','Card Name','source_row','Face/Scope','Operation Kind','Exact Oracle Clause','Observes / Input Hook',
                'Requirement Groups (AND)','Alternatives (OR)','Result Produces','Payment / Consumes','Modifies','Timing','Qualifiers','Object Transition','Status','Confidence','Source URL','Review Note')
        vals=[row.get(x,'') for x in fields]
        c.execute('INSERT INTO candidate_operations VALUES ('+','.join('?'*21)+')',
          tuple(vals[:2]+vals[2:]+['unverified_candidate',dumps(row)]))
    # Governance and vocabulary: store source documents in the same portable database.
    doc_inputs = [
      ('dio_v3.1.1','DIO v3.1.1','ontology','MTG DECK INTERACTION ONTOLOGY v3_1_1.md'),
      ('dio_v3.1.1_addendum','DIO v3.1.1 addendum','ontology_addendum','MTG DECK INTERACTION ONTOLOGY v3.1.1 — ADDENDUM(1).md'),
      ('dbep_v1.2_addendum','DBEP portfolio v1.2','evaluation_protocol','MTG DECK BUILDING AND EVALUATION PROTOCOL v1.2 ADDENDUM.md'),
      ('grammar_registry_v0.1','Grammar registry v0.1','vocabulary','MTG_Grammar_Rules_Vocabulary_Registry_v0.1.json'),
      ('kairos_gate','Kairos–GATE','operational_doctrine','KAIROS–GATE MAGIC THE GATHERING(1).md'),
    ]
    for did,title,kind,filename in doc_inputs:
        path=HERE/'reference_sources'/filename
        if path.exists():
            b=path.read_bytes()
            c.execute('INSERT INTO reference_documents VALUES(?,?,?,?,?)',
               (did,title,kind,hashlib.sha256(b).hexdigest(),b.decode('utf-8')))
    registry=HERE/'reference_sources/MTG_Grammar_Rules_Vocabulary_Registry_v0.1.json'
    if registry.exists():
        for domain in json.loads(registry.read_text(encoding='utf-8')).get('domains',[]):
            c.execute('INSERT INTO ontology_domains VALUES(?,?,?,?,?,?)',
              (domain['domain'],domain.get('purpose',''),domain.get('status',''),domain.get('source',''),domain.get('source_location',''),dumps(domain)))
    for f in facts:
        name=f['card_name']
        row=c.execute('SELECT projection_status,unread_fragment_count FROM projected_card_statics WHERE card_name=?',(name,)).fetchone()
        assigned=f['assigned']; nops=f['candidate_operations_indexed']
        is_commander=any(n==name and str(r.get('Section',''))=='Commander' and str(r.get('Status',''))=='Current deck' for r in deck_allocs for n in [r.get('Card Name')])
        score=100*bool(is_commander)+35*bool(assigned)+min(35,row[1]*3)+min(20,nops*2)+15*int(row[0]=='no_projection')
        reason=('active commander; ' if is_commander else '')+('allocated in deck; ' if assigned else '')+f'{row[1]} unread fragments; {nops} indexed candidate operations'
        c.execute('INSERT INTO review_backlog VALUES(?,?,?,?,?,?)',(name,score,reason,nops,row[1],row[0]))
    # Human reviews are external sidecar annotations, never inferred from regex parsing.
    reviews=HERE/'overrides/verified_reviews.jsonl'
    if reviews.exists():
        for line in reviews.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            rev=json.loads(line)
            card=rev['card_name'];stored=c.execute('SELECT oracle_text_sha256 FROM cards WHERE card_name=?',(card,)).fetchone()
            if not stored or rev.get('oracle_sha256')!=stored[0]:
                c.execute('INSERT INTO qa_issues VALUES(?,?,?,?)',('stale_human_review',card,'high',dumps(rev)))
                continue
            c.execute('INSERT INTO manual_reviews VALUES(?,?,?,?,?,?,?,?)',
               (card,rev.get('operation_id'),rev['review_scope'],rev['status'],rev['reviewer'],rev['reviewed_utc'],rev['source'],rev.get('notes','')))
    for row in data['issues']:
        c.execute('INSERT INTO qa_issues VALUES(?,?,?,?)',(row['kind'],row.get('card'),row['severity'],dumps(row)))
    c.executemany('INSERT INTO source_sheet_rows VALUES(?,?,?)',
        ((tab,r['_row'],dumps(r)) for tab,rows in raw.items() for r in rows) if is_db else all_sheet_rows(workbook))
    c.execute("INSERT INTO card_fts(card_fts) VALUES('rebuild')")
    c.commit()
    audit={
        'cards':c.execute('SELECT COUNT(*) FROM cards').fetchone()[0],
        'owned_cards':c.execute('SELECT COUNT(*) FROM cards WHERE owned_min>0').fetchone()[0],
        'known_copies':c.execute('SELECT SUM(owned_min) FROM cards').fetchone()[0],
        'deck_names':c.execute('SELECT COUNT(*) FROM deck_card_counts').fetchone()[0],
        'candidate_operations':c.execute('SELECT COUNT(*) FROM candidate_operations').fetchone()[0],
        'projected_abilities':c.execute('SELECT COUNT(*) FROM projected_abilities').fetchone()[0],
        'capability_claims':c.execute('SELECT COUNT(*) FROM capability_claims').fetchone()[0],
        'source_sheet_rows':c.execute('SELECT COUNT(*) FROM source_sheet_rows').fetchone()[0],
        'source_sheet_count':c.execute('SELECT COUNT(DISTINCT sheet_name) FROM source_sheet_rows').fetchone()[0],
        'unverified_candidate_ops':c.execute("SELECT COUNT(*) FROM candidate_operations WHERE verification_status='unverified_candidate'").fetchone()[0],
        'fully_rules_verified_operations':c.execute("SELECT COUNT(*) FROM candidate_operations WHERE verification_status='verified'").fetchone()[0],
        'machine_projections_by_status': dict(c.execute('SELECT projection_status,COUNT(*) FROM projected_card_statics GROUP BY projection_status').fetchall()),
        'qa_issues_by_severity':dict(c.execute('SELECT severity,COUNT(*) FROM qa_issues GROUP BY severity').fetchall()),
        'deck_card_counts':dict(c.execute('SELECT deck,total_cards FROM deck_card_counts').fetchall()),
        'review_backlog':c.execute('SELECT COUNT(*) FROM review_backlog').fetchone()[0],
        'ontology_domains':c.execute('SELECT COUNT(*) FROM ontology_domains').fetchone()[0],
        'embedded_project_documents':c.execute('SELECT COUNT(*) FROM reference_documents').fetchone()[0],
        'source_sha256':before,'parser_sha256':pv,
        'caveat':'Precomputed does not mean validated. Candidate operations and machine projections MUST NOT auto-execute as rules truth.'}
    c.close()
    if hashlib.sha256(workbook.read_bytes()).hexdigest()!=before:raise RuntimeError('Source workbook mutated')
    if jsonl_out:
        export_jsonl(db_path,Path(jsonl_out))
    return audit

def export_jsonl(db_path,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(db_path);con.row_factory=sqlite3.Row
    for table,filename in [('cards','cards.jsonl'),('deck_allocations','allocations.jsonl'),('candidate_operations','candidate_operations.jsonl'),
                           ('capability_claims','capability_claims.jsonl'),('projected_abilities','projected_abilities.jsonl'),('projected_card_statics','projected_statics.jsonl'),('typed_profiles','typed_profiles.jsonl'),('review_backlog','review_backlog.jsonl')]:
        with (outdir/filename).open('w',encoding='utf-8') as f:
            for x in con.execute(f'SELECT * FROM {table}'):
                d=dict(x)
                for k,v in list(d.items()):
                    if k.endswith('_json') and isinstance(v,str):
                        try:d[k]=json.loads(v)
                        except json.JSONDecodeError:pass
                f.write(dumps(d)+'\n')
    con.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('workbook');p.add_argument('--db',default=str(HERE/'mtg_cards.sqlite'));p.add_argument('--jsonl',default=None)
    args=p.parse_args();audit=build(args.workbook,args.db,args.jsonl)
    (Path(args.db).parent/'AUDIT.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
