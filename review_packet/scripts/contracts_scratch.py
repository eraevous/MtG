import sqlite3,sys,json
sys.path.insert(0,'/mnt/project-files/mechanics-kernel/grammar-layer')
import semantics
kb=sqlite3.connect('file:/mnt/project-files/mechanics-kernel/sqlite-kb/mtg_cards_v0.2.sqlite?mode=ro',uri=True)
names=[r[0] for r in kb.execute("select card_name from cards where owned_min>0 and card_name not in (select distinct card_name from candidate_operations) and card_name not in ('______','Counters','Elemental')")]
oid={n:o for n,o in kb.execute("select card_name,oracle_id from external_oracle where run_id='bbdd0ad27a59e47d' and oracle_id is not null")}
tgt={n:oid.get(n) for n in names}
print(len(names),'no oracle:',[n for n,o in tgt.items() if not o])
db=sqlite3.connect('gl_scratch.sqlite')
ids=",".join("'%s'"%o for o in tgt.values() if o)
n=semantics.install_contracts(db, where=f"c.oracle_id in ({ids})")
db.commit(); print('contracts',n)
json.dump(tgt,open('targets.json','w'),indent=0)
