# @ai-semantic-role: candidate-source  (exploration over persisted KB contract text; every reading is a candidate)
# Scratch exploration (not repo code). Reads persisted KB rows only; every reading is a CANDIDATE.
import sqlite3, re, json, collections
c=sqlite3.connect('file:kb/mtg_cards_v0.2.sqlite?mode=ro',uri=True); c.row_factory=sqlite3.Row
def ok_ci(ci): return set((ci or '').replace(',','').replace(' ','')) <= set('WUR')
cards={r['card_name']:r for r in c.execute("select * from cards")}
alloc=collections.defaultdict(list)
for r in c.execute("select card_name,deck,quantity from active_deck_cards"): alloc[r['card_name']].append(r['deck'])
vraska=set(n for n,d in alloc.items() if 'Vraska' in d)
pool=[n for n,r in cards.items() if ok_ci(r['color_identity']) and 'Basic Land' not in (r['type_line'] or '')]
ops=collections.defaultdict(list)
for r in c.execute("select card_name,operation_kind,exact_text from current_contracts"):
    if r['card_name'] in cards: ops[r['card_name']].append((r['operation_kind'],r['exact_text']))
P={
 'ART_ENTER_OBS': r"whenever (an?|one or more|another) (nontoken )?(artifact|artifact creature|token|creature token)s?[^.]{0,40}(enters|you control enters|are created)|whenever you create (an?|one or more) [^.]{0,30}token",
 'ART_CAST_OBS': r"whenever you cast (an )?artifact spell|whenever you cast a noncreature spell",
 'MAKES_ARTIFACT': r"create[^.]{0,60}(artifact|treasure|thopter|clue|food|servo|construct|powerstone|map|gold|blood|sculpture|robot)",
 'ANTHEM': r"(artifact creatures|creature tokens|creatures|thopters|tokens) you control get \+\d|(artifact creatures|creatures) you control (have|gain) [^.]{0,30}(flying|double strike|trample)",
 'PROTECT': r"(indestructible|hexproof|protection from|phase out|ward)",
 'RECUR_ART': r"return (target |up to [^.]{0,10})?(artifact|permanent|creature)[^.]{0,40}from your graveyard",
 'UNTAP': r"untap (target|all|each|up to)[^.]{0,40}(artifact|creature|permanent)",
 'PAYOFF_DAMAGE': r"(deals? \d+ damage to each opponent|each opponent loses \d+ life|deals 1 damage to (any target|each opponent))",
}
hits=collections.defaultdict(dict)
for n in pool:
    for kind,text in ops.get(n,[]):
        t=(text or '').lower()
        for k,p in P.items():
            if re.search(p,t): hits[n].setdefault(k,[]).append(text[:160])
def where(n):
    r=cards[n]; d=alloc.get(n,[])
    return ('IN VRASKA' if n in vraska else ('free' if r['free']>0 else 'allocated:'+','.join(d)))
out=collections.defaultdict(list)
for n,h in hits.items():
    for k in h: out[k].append(n)
json.dump({k:{n:{'where':where(n),'text':hits[n][k][0],'mv':cards[n]['mana_value'],'type':cards[n]['type_line']} for n in v} for k,v in out.items()}, open('vraska_hits.json','w'), indent=1)
for k in P:
    v=out.get(k,[]); inV=[n for n in v if n in vraska]; fr=[n for n in v if n not in vraska and cards[n]['free']>0]
    print(f"{k}: total {len(v)} | in Vraska {len(inV)} | free {len(fr)} | allocated elsewhere {len(v)-len(inV)-len(fr)}")
print('Vraska deck cards with ops:', len(vraska), 'pool WUR-legal:', len(pool))
