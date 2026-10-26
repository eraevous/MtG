"""Full-corpus parity: v0.1 cached projections/claims vs a fresh 0.3.0 parse of the same stored rows."""
import sys,json
sys.path.insert(0,sys.argv[1]); sys.path.insert(0,sys.argv[1]+'/vendor')
from sqlite_bridge import SQLiteInventory
from build_mtg_db import jsonable
from mtg_eval import abilities, semantics
from mtg_eval.inventory import Row
inv=SQLiteInventory(sys.argv[1]+'/mtg_cards.sqlite')
labels=semantics.load_labels()
bad_rec,bad_cap,n=[],[],0
for name,row in inv.cards.items():
    n+=1
    abilities._CACHE.pop((inv.sha256,name),None); fresh=abilities.card_record(inv,name)
    if jsonable(fresh)!=jsonable(inv.cached_runtime_record(name)): bad_rec.append(name)
    cr=semantics.capability_record(row,labels); br=inv.record(name)
    if {k:v['status'] for k,v in cr.items()}!={k:v['status'] for k,v in br.items()}: bad_cap.append(name)
print(json.dumps({'cards':n,'projection_mismatch':len(bad_rec),'claim_status_mismatch':len(bad_cap),'examples':bad_rec[:5]+bad_cap[:5]}))
