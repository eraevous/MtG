"""Compatibility reader: expose the cached database as mtg_eval 0.3 Inventory.
Old evaluator methods still re-derive some textual semantics; this bridge specifically caches
Inventory facts, role claims, and machine ability projections. No DIO candidate is auto-executed.
"""
import json,sqlite3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
from mtg_eval.inventory import Inventory,Row,NON_DECK
from mtg_eval import abilities

def db_open(path):
    p=Path(path).resolve()
    con=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    con.row_factory=sqlite3.Row
    return con

def _restore_sets(x,key=None):
    if isinstance(x,dict):return {k:_restore_sets(v,k) for k,v in x.items()}
    if isinstance(x,list):
        if key in ('types','subtypes','keywords','filter'):return set(_restore_sets(z) for z in x)
        if key=='mana' and len(x)==2:return (x[0],[_restore_sets(z,'types') for z in x[1]])
        if key=='condition' and len(x)==2:return tuple(x)
        return [_restore_sets(y) for y in x]
    return x

class SQLiteInventory(Inventory):
    def __init__(self,database):
        self.path=Path(database);self.db=db_open(database)
        self.sha256=self.db.execute("select value from meta where key='input_sha256'").fetchone()[0]
        self.cards={}
        for x in self.db.execute('select card_name,raw_json from cards'):
            if x['card_name'] not in NON_DECK:self.cards[x['card_name']]=Row(json.loads(x['raw_json']))
        self.decks={}
        for x in self.db.execute("SELECT deck,card_name,quantity,section FROM deck_allocations WHERE physically_assigned=1 ORDER BY row_id"):
            if x['card_name'] in self.cards:self.decks.setdefault(x['deck'],[]).append((x['card_name'],x['quantity'],x['section']))
        self._rec={}
        self.labels={}
    def record(self,name):
        if name not in self._rec:
            claims=self.db.execute("select capability,claim_status,evidence_text from capability_claims where card_name=? and source='mtg_eval.semantic_patterns'",(name,))
            statuses={'machine_supported':'supported','unverified_tag_only':'tag_only','machine_contradicted':'contradicted'}
            self._rec[name]={x['capability']:{'status':statuses.get(x['claim_status'],'tag_only'),'evidence':json.loads(x['evidence_text']) if x['evidence_text'] else {}} for x in claims}
        return self._rec[name]
    def source(self):
        return {'sheet_id':self.db.execute("select value from meta where key='canonical_sheet_id'").fetchone()[0],
                'source':'SQLite derived cache', 'sha256':self.sha256,
                'note':'Source workbook facts are read-only; unverified semantics are machine projections'}
    def cached_runtime_record(self,name):
        row=self.db.execute('select statics_json,unread_json from projected_card_statics where card_name=?',(name,)).fetchone()
        if row is None:raise KeyError(name)
        statics=_restore_sets(json.loads(row['statics_json']))
        unread=json.loads(row['unread_json'])
        rs=[]
        for x in self.db.execute('select * from projected_abilities where card_name=? order by ability_index',(name,)):
            a=json.loads(x['raw_ability_json'])
            if a.get('hook') is not None and isinstance(a['hook'],list):
                a['hook']=(a['hook'][0],_restore_sets(a['hook'][1]))
            if a.get('cost') is not None:a['cost']=_restore_sets(a['cost'])
            if 'gates' in a:a['gates']=_restore_sets(a['gates'])
            if 'outputs' in a:a['outputs']=[tuple(_restore_sets(v) for v in o) if isinstance(o,list) else o for o in a['outputs']]
            rs.append(a)
        return {'abilities':rs,'statics':statics,'unread':unread}
    def populate_runtime_cache(self,only_decks=None):
        names=self.cards if only_decks is None else {n for deck in only_decks for n,_,_ in self.decks[deck]}
        for n in names:
            abilities._CACHE[(self.sha256,n)]=self.cached_runtime_record(n)
        return len(names)

class SQLiteEvaluator:
    """Evaluator-compatible facade; hooks mtg_eval's existing API to the portable DB.
    Requires vendor mtg_eval 0.3 (provided in package)."""
    def __new__(cls,database,games=5000,seed=20261018,engine_games=300):
        from mtg_eval.api import Evaluator
        obj=object.__new__(Evaluator)
        obj.inv=SQLiteInventory(database)
        obj.inv.populate_runtime_cache()   # cache all once; no source-string reparse for engine
        obj.games,obj.seed,obj.engine_games=games,seed,engine_games
        obj._profiles={}
        return obj
