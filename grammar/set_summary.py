"""Per-set validation summary: cards, owned cards, tests, frames tested, ruling statuses, introduced mechanics.

python3 -I set_summary.py grammar_layer.sqlite > validation/per_set_summary.json
"""
import sqlite3,sys,json
d=sqlite3.connect(sys.argv[1])
q=lambda s,*a: d.execute(s,a).fetchall()
out={}
sets=[r[0] for r in q("select code from set_info order by released_at")]
for c in sets:
    role,name=q("select role,name from set_info where code=?",c)[0]
    n=q("select count(distinct oracle_id) from set_member where code=?",c)[0][0]
    owned=q("select count(distinct m.oracle_id) from set_member m join card k using(oracle_id) where m.code=? and k.in_collection",c)[0][0]
    tr=dict(q("select outcome,count(*) from test_result t join set_member m using(oracle_id) where m.code=? group by 1",c))
    claims=q("select count(distinct claim_id) from test_result t join set_member m using(oracle_id) where m.code=?",c)[0][0]
    frames=q("select count(distinct p.frame_id) from test_result t join set_member m using(oracle_id) join part p on p.ability_id=t.ability_id where m.code=?",c)[0][0]
    tested=q("select count(distinct t.oracle_id) from test_result t join set_member m using(oracle_id) where m.code=?",c)[0][0]
    towned=q("select count(distinct t.oracle_id) from test_result t join set_member m using(oracle_id) join card k using(oracle_id) where m.code=? and k.in_collection",c)[0][0]
    rs=dict(q("select status,count(*) from ruling_status r join set_member m using(oracle_id) where m.code=? group by 1",c))
    outd=q("select count(*) from ruling_status r join set_member m using(oracle_id) where m.code=? and outdated",c)[0][0]
    intro=[r[0] for r in q("select mechanic from mechanic_family where code=? and status_in_set='introduced' order by n_abilities desc",c)]
    out[c]=dict(name=name,role=role,cards=n,owned=owned,claims_applied=claims,tests=tr,frames_tested=frames,cards_tested=tested,owned_cards_tested=towned,ruling_status=rs,outdated=outd,introduced=intro)
tot=dict(frames=q("select count(distinct p.frame_id) from test_result t join part p on p.ability_id=t.ability_id")[0][0],
 claims=q("select count(*) from claim")[0][0],
 cards=q("select count(distinct oracle_id) from test_result")[0][0],
 owned=q("select count(distinct t.oracle_id) from test_result t join card k using(oracle_id) where k.in_collection")[0][0],
 abilities=q("select count(distinct ability_id) from test_result")[0][0],
 tests=dict(q("select outcome,count(*) from test_result group by 1")),
 owned_mech=q("select c.mechanic,count(distinct t.oracle_id) from test_result t join claim c using(claim_id) join card k using(oracle_id) where k.in_collection group by 1"))
out['_total']=tot
print(json.dumps(out,indent=1))
