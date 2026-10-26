#!/usr/bin/env python3
"""Fast read-only query client for portable MTG SQLite database. Prints JSON, no workbook parsing."""
import argparse,json,sqlite3
from pathlib import Path
HERE=Path(__file__).resolve().parent

def dbconnect(path):
    p=Path(path).resolve()
    if not p.exists(): raise FileNotFoundError(p)
    c=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    c.row_factory=sqlite3.Row
    return c

def q(c,sql,params=()):return [dict(x) for x in c.execute(sql,params)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default=str(HERE/'mtg_cards.sqlite'))
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('stats')
    a=sub.add_parser('card');a.add_argument('name')
    a=sub.add_parser('abilities');a.add_argument('name')
    a=sub.add_parser('deck');a.add_argument('name')
    a=sub.add_parser('search');a.add_argument('term');a.add_argument('--limit',type=int,default=25)
    a=sub.add_parser('role');a.add_argument('role');a.add_argument('--free',action='store_true');a.add_argument('--limit',type=int,default=30)
    a=sub.add_parser('operations');a.add_argument('name')
    a=sub.add_parser('review');a.add_argument('--deck');a.add_argument('--limit',type=int,default=30)
    a=sub.add_parser('ontology');a.add_argument('domain')
    a=sub.add_parser('sql');a.add_argument('statement')
    args=p.parse_args();c=dbconnect(args.db)
    if args.cmd=='stats':
        rows={'cards':c.execute('select count(*) from cards').fetchone()[0],
          'owned_card_names':c.execute('select count(*) from cards where owned_min>0').fetchone()[0],
          'owned_copies':c.execute('select sum(owned_min) from cards').fetchone()[0],
          'decks':q(c,'select * from deck_card_counts order by deck'),
          'candidate_operations':c.execute('select count(*) from candidate_operations').fetchone()[0],
          'simulator_projection_abilities':c.execute('select count(*) from projected_abilities').fetchone()[0],
          'rules_verified_operations':c.execute("select count(*) from candidate_operations where verification_status='verified'").fetchone()[0],
          'source':q(c,'select key,value from meta')}
    elif args.cmd=='card':
        rows=q(c,'select card_name,owned_min,assigned,free,color_identity,mana_cost,mana_value,type_line,roles_stored,oracle_text,keywords_stored,produces_stored,scryfall_url,commander_legal_stored from cards where card_name=?',(args.name,))
        if rows:
            rows={'card':rows[0], 'assignments':q(c,'select deck,quantity,section,status_group from deck_allocations where card_name=? and physically_assigned=1',(args.name,)),
                  'capabilities':q(c,'select capability,source,claim_status,evidence_text from capability_claims where card_name=?',(args.name,)),
                  'parser':q(c,'select projected_ability_count,unread_fragment_count,projection_status,unread_json from projected_card_statics where card_name=?',(args.name,)),
                  'legacy_candidate_count':c.execute('select count(*) from candidate_operations where card_name=?',(args.name,)).fetchone()[0]}
    elif args.cmd=='abilities':
        rows={'abilities':q(c,'select kind,hook,hook_details_json,cost_json,gates_json,outputs_json,clause,unread,projection_status,runtime_verification from projected_abilities where card_name=? order by ability_index',(args.name,)),
              'statics':q(c,'select statics_json,unread_json from projected_card_statics where card_name=?',(args.name,))}
    elif args.cmd=='deck':
        rows=q(c,'select card_name,quantity,section from active_deck_cards where deck=? order by section,card_name',(args.name,))
    elif args.cmd=='search':
        rows=q(c,'select card_name,substr(oracle_text,1,180) as oracle_excerpt,free,assigned from cards where rowid in (select rowid from card_fts where card_fts match ? limit ?) order by card_name',(args.term,args.limit))
    elif args.cmd=='role':
        rows=q(c,'''SELECT DISTINCT c.card_name,c.free,c.assigned,c.color_identity,r.claim_status,r.source
                   FROM capability_claims r JOIN cards c ON c.card_name=r.card_name
                   WHERE r.capability=? AND (?=0 OR c.free>0)
                   ORDER BY (r.claim_status='machine_supported') DESC,c.free DESC,c.card_name LIMIT ?''',(args.role,int(args.free),args.limit))
    elif args.cmd=='operations':
        rows=q(c,'select operation_id,operation_kind,oracle_clause,observes_hook,requirement_groups,result_produces,payment_consumes,source_status,verification_status from candidate_operations where card_name=?',(args.name,))
    elif args.cmd=='review':
        if args.deck:rows=q(c,'''SELECT DISTINCT r.* FROM review_backlog r JOIN deck_allocations a ON a.card_name=r.card_name
                  WHERE a.deck=? AND a.counts_in_deck_100=1 ORDER BY r.priority_score DESC,r.card_name LIMIT ?''',(args.deck,args.limit))
        else:rows=q(c,'select * from review_backlog order by priority_score desc,card_name limit ?',(args.limit,))
    elif args.cmd=='ontology':
        rows=q(c,'select * from ontology_domains where domain=?',(args.domain,))
    elif args.cmd=='sql':
        st=args.statement.strip()
        if not st.lower().startswith(('select ','with ','pragma table_info')) or ';' in st.rstrip(';'):
            p.error('read-only SELECT/WITH query only')
        rows=q(c,st)
    print(json.dumps(rows,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
