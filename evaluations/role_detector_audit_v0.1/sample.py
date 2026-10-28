import sqlite3,random,json,sys
sys.path.insert(0,'kb'); import kbq
sys.path.insert(0,'kb/vendor'); from mtg_eval import semantics as S
c=sqlite3.connect('kb/mtg_cards_v0.2.sqlite'); c.row_factory=sqlite3.Row
decks=[r[0] for r in c.execute('select distinct deck from active_deck_cards')]
deckcards={n for d in decks for n in kbq.deck_cards(c,d)}
OUT=__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/'  # writes <role>.json next to this script; run from the repo root
TIER1={'spot_removal','protection','recursion'}  # tier 1 used larger samples (Kate's priority 1)
for role in sys.argv[1:]:
    n_in,n_out,t_in,t_out=(25,10,15,5) if role in TIER1 else (20,8,12,3)
    sole={}
    for d in decks:
        s=kbq.overlap(c,d)['sole_detected_candidates'].get(role)
        if s: sole.setdefault(s['card'],[]).append(d)
    pos=[r[0] for r in c.execute("select card_name from capability_claims where capability=? and source='mtg_eval.semantic_patterns' and claim_status='machine_supported' order by card_name",(role,))]
    tag=[r[0] for r in c.execute("select card_name from capability_claims where capability=? and source='mtg_eval.semantic_patterns' and claim_status='unverified_tag_only' order by card_name",(role,))]
    rng=random.Random(f'audit-2026-10-28-{role}')
    indeck=[p for p in pos if p in deckcards and p not in sole]; rest=[p for p in pos if p not in deckcards]
    sp=sorted(sole)+rng.sample(indeck,min(n_in,len(indeck)))+rng.sample(rest,min(n_out,len(rest)))
    ti=[t for t in tag if t in deckcards]; to=[t for t in tag if t not in deckcards]
    tg=rng.sample(ti,min(t_in,len(ti)))+rng.sample(to,min(t_out,len(to)))
    rows=[]
    for kind,names in (('positive',sp),('tag_only',tg)):
        for n in names:
            r=c.execute('select oracle_text,type_line from cards where card_name=?',(n,)).fetchone()
            rows.append({'role':role,'kind':kind,'card':n,'sole_in':sole.get(n,[]),'in_deck':n in deckcards,'span':S.oracle_functions(n,r[0],r[1]).get(role),'type':r[1],'oracle':r[0]})
    json.dump(rows,open(OUT+role+'.json','w'),indent=1,ensure_ascii=False)
    print(role,'pos',len(pos),'sole',len(sole),'sampled',len(sp),'tag_only',len(tag),'sampled',len(tg))
    for i,r in enumerate(rows):
        print(f"{i:2} [{r['kind'][:3]}]{'[SOLE '+','.join(r['sole_in'])+']' if r['sole_in'] else ''} {r['card']} | {r['type'][:30]} | span={r['span']!r}\n    {r['oracle'].replace(chr(10),' / ')[:260]}")
