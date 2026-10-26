"""Property/metamorphic invariant tests for the MTG semantic kernel.
Run: python3 invariants_v021d.py <bundle_dir> [trials]
No dependencies; seeded random generation so failures are reproducible."""
import sys, random, copy, json
sys.path.insert(0, sys.argv[1])
from mtg_semantic_kernel_v0_2_1 import one_event_match, evaluate, YES, NO, UNKNOWN
from result_projection_v0_2_1b import project_resolved_effects
N=int(sys.argv[2]) if len(sys.argv)>2 else 3000
rng=random.Random(20261016)

HOOKS=['battlefield.enter','battlefield.leave','graveyard.enter','permanent.dies','permanent.sacrifice',
       'permanent.destroy','token.create','card.discard','card.mill','spell.cast','card.return_to_battlefield']
LHOOKS=HOOKS+['creature.enters_battlefield','land.enters_battlefield','artifact.enters_battlefield','token.enters_battlefield']
TYPES=[['creature'],['artifact'],['land'],['artifact','creature'],['enchantment']]
ZONES=['graveyard','exile','hand','library','battlefield']
def rand_snap(hook):
    s={}
    if rng.random()<.8: s['types']=rng.choice(TYPES)
    if rng.random()<.6: s['controller']=rng.choice(['you','opponent'])
    if rng.random()<.5: s['colors']=rng.choice([['R'],['U','R'],['G'],[]])
    if hook in ('battlefield.leave','permanent.sacrifice','permanent.destroy','card.discard','card.mill') and rng.random()<.7:
        s['to_zone']=rng.choice(ZONES)
    if hook=='graveyard.enter' and rng.random()<.7: s['from_zone']=rng.choice(ZONES)
    if hook=='token.create' and rng.random()<.7: s['quantity']=rng.choice([0,1,2,3])
    if hook=='battlefield.enter' and rng.random()<.3: s['token']=rng.choice([True,False])
    if rng.random()<.3: s['object_id']=rng.choice(['o1','o2','o3'])
    return s
_ctr=[0]
def rand_event(eid=None):
    h=rng.choice(HOOKS); _ctr[0]+=1
    return {'event_id':eid or f'e{_ctr[0]}','hook':h,'snapshots':{'event':rand_snap(h)}}
def rand_listener():
    h=rng.choice(LHOOKS); w={}
    if rng.random()<.6: w['types']=rng.choice(TYPES[:3])
    if rng.random()<.4: w['controller']=rng.choice(['you','opponent'])
    if rng.random()<.2: w['colors']=[rng.choice(['R','red','U'])]
    if h=='graveyard.enter' and rng.random()<.3: w['from_zone']='battlefield'
    return {'kind':'event','hook':h,'where':w}
def scn(events,alt):
    return {'id':'p','operation':{'initiation':{'requirement_groups':[{'id':'g','alternatives':[alt]}]}},
            'events':events,'events_complete':True}
def G(events,alt):
    g=evaluate(scn(events,alt))['groups'][0]; return (g['status'],g['matched_event_count'])

violations={}
def record(name,example):
    violations.setdefault(name,[]).append(example)

for t in range(N):
    events=[rand_event() for _ in range(rng.randint(1,4))]
    alt=rand_listener()
    base=G(events,alt)
    # M1 permutation invariance
    sh=events[:]; rng.shuffle(sh)
    if G(sh,alt)!=base: record('M1 permutation changes result',(events,alt,base,G(sh,alt)))
    # M2 exact duplicate record (same event_id, same facts) changes nothing
    dup=events+[copy.deepcopy(rng.choice(events))]
    if G(dup,alt)!=base: record('M2 duplicate record changes result',(events,alt,base,G(dup,alt)))
    # M3 adding an unrelated event (fresh id, provably non-matching) changes nothing
    extra=rand_event()
    if one_event_match(extra,alt)==NO:
        r=G(events+[extra],alt)
        if r!=base: record('M3 unrelated event changes result',(events,extra,alt,base,r))
    # M4 information loss: dropping one known fact never flips YES<->NO
    e=rng.choice(events); snap=e['snapshots']['event']
    if snap:
        k=rng.choice(list(snap)); red=copy.deepcopy(e); del red['snapshots']['event'][k]
        full=one_event_match(e,alt); less=one_event_match(red,alt)
        if less!=full and less!=UNKNOWN: record(f'M4 dropping a fact creates certainty',(e,k,alt,full,less))

# M5 equivalent descriptions of one death must agree on every listener
deaths=[{'hook':'permanent.dies','snapshots':{'event':{'types':['creature'],'controller':'you'}}},
        {'hook':'graveyard.enter','snapshots':{'event':{'types':['creature'],'controller':'you','from_zone':'battlefield','to_zone':'graveyard'}}},
        {'hook':'battlefield.leave','snapshots':{'event':{'types':['creature'],'controller':'you','from_zone':'battlefield','to_zone':'graveyard'}}},
        {'hook':'permanent.sacrifice','snapshots':{'event':{'types':['creature'],'controller':'you','to_zone':'graveyard'}}}]
dl=[{'kind':'event','hook':h,'where':w} for h,w in [('permanent.dies',{}),('battlefield.leave',{}),('graveyard.enter',{}),
     ('graveyard.enter',{'from_zone':'battlefield'}),('battlefield.leave',{'to_zone':'graveyard'}),('permanent.dies',{'types':['creature']})]]
for alt in dl:
    rs=[one_event_match(d,alt) for d in deaths]
    # sacrifice is a superset event, so only compare the first three (same occurrence, same facts)
    if len(set(rs[:3]))>1: record('M5 equivalent death descriptions disagree',(alt,dict(zip(['dies','gy.enter','bf.leave','sac'],rs))))
# equivalent entry descriptions
entries=[{'hook':'battlefield.enter','snapshots':{'event':{'types':['artifact','creature'],'colors':['R'],'controller':'You','to_zone':'battlefield'}}},
         {'hook':'creature.enters_battlefield','snapshots':{'event':{'types':['Artifact Creature'],'colors':['red'],'controller':'you','to_zone':'Battlefield'}}},
         {'hook':'battlefield.enter','where':{'types':['artifact','creature'],'colors':['red']},'snapshots':{'event':{'controller':'you','to_zone':'battlefield'}}}]
el=[{'kind':'event','hook':h,'where':w} for h,w in [('battlefield.enter',{'types':['creature']}),('artifact.enters_battlefield',{}),
     ('battlefield.enter',{'colors':['R']}),('battlefield.enter',{'controller':'you'}),('battlefield.enter',{'to_zone':'battlefield'})]]
for alt in el:
    rs=[one_event_match(d,alt) for d in entries]
    if len(set(rs))>1: record('M5 equivalent entry descriptions disagree',(alt,rs))
# token batch vs its complete child projection must agree for entry listeners
for alt in el+[{'kind':'event','hook':'battlefield.enter','where':{'to_zone':'battlefield'}}]:
    b={'event_id':'b','hook':'token.create','snapshots':{'event':{'types':['artifact','creature'],'colors':['R'],'controller':'you','quantity':1}}}
    kids=project_resolved_effects([{'kind':'token_create','quantity':1,'controller':'you','token':{'types':['artifact','creature'],'colors':['R']}}],'k')
    if G([b],alt)!=G(kids,alt): record('M5 raw batch vs its projection disagree',(alt,G([b],alt),G(kids,alt)))

# M6 identity: independent explicit action ids must never share object/event identities
ids={}
eff=[{'kind':'zone_move','from':'graveyard','to':'battlefield','types':['artifact']},
     {'kind':'token_create','quantity':2,'token':{'types':['creature']}}]
reg=set()
for aid in ['a','a:1:token','a:0','a:1']:
    try: out=project_resolved_effects(eff+eff,aid,used_action_ids=reg)
    except ValueError as x: continue
    for e in out:
        for key in ('event_id',):
            if e[key] in ids: record('M6 distinct action_ids collide',(aid,ids[e[key]],e[key]))
            ids[e[key]]=aid
        oid=e['snapshots']['event'].get('object_id')
        if oid:
            if ('o',oid) in ids: record('M6 distinct action_ids collide (object_id)',(aid,ids[('o',oid)],oid))
            ids[('o',oid)]=aid
# M6b idempotence: projecting the SAME resolution twice (default ids) must not create two occurrences
r1=project_resolved_effects([eff[0]]); r2=project_resolved_effects([eff[0]])
cnt=G(r1+r2,{'kind':'event','hook':'battlefield.enter','where':{'types':['artifact']}})
if cnt!=('satisfied',1): record('M6b re-projecting one resolution double-counts (default ids)',cnt)

print(f'trials={N}')
for name,ex in sorted(violations.items()):
    print(f'\n### {name}: {len(ex)} violations; first example:')
    print('  ',json.dumps(ex[0],default=str)[:900])
if not violations: print('no violations')

# ---- Family 2: ledgers with token batches and per-token children ----
v2={}
def rec2(n,x): v2.setdefault(n,[]).append(x)
SUB=[['Treasure'],['Food'],['Clue'],['Zombie']]
for t in range(N):
    events=[]; 
    for b in range(rng.randint(1,2)):
        bid=f'B{t}_{b}'; q=rng.choice([1,2,3,None])
        bs={'types':['artifact'],'subtypes':rng.choice(SUB)}
        if q is not None: bs['quantity']=q
        events.append({'event_id':bid,'hook':'token.create','snapshots':{'event':bs}})
        nk=rng.choice([0,1,2,3]) if q is None else rng.choice([0,q,q,max(q-1,0)])
        for j in range(nk):
            cs={'types':['artifact'],'token':True,'subtypes':bs['subtypes'] if rng.random()<.8 else rng.choice(SUB)}
            events.append({'event_id':f'{bid}:t{j}','hook':'battlefield.enter','derived_from':bid,'snapshots':{'event':cs}})
    for _ in range(rng.randint(0,2)): events.append(rand_event())
    alt={'kind':'event','hook':'battlefield.enter','where':rng.choice([{},{'subtypes':['Treasure']},{'types':['artifact']},{'subtypes':['Food']}])}
    base=G(events,alt)
    sh=events[:]; rng.shuffle(sh)
    if G(sh,alt)!=base: rec2('F2-M1 permutation changes result',(events,alt,base,G(sh,alt)))
    extra=rand_event()
    if one_event_match(extra,alt)==NO and G(events+[extra],alt)!=base: rec2('F2-M3 unrelated event changes result',(events,extra,alt,base))
    # a child that exists and matches must never yield 'failed' in a complete ledger
    if any(e.get('derived_from') and one_event_match(e,alt)==YES for e in events) and base[0]==NO:
        rec2('F2-X a matching token entry is present but the listener FAILS',(events,alt,base))
    # count must never be below the number of matching children
    m=sum(1 for e in events if e.get('derived_from') and one_event_match(e,alt)==YES)
    if base[1] is not None and base[1]<m: rec2('F2-Y count below matching children',(events,alt,base,m))

# ---- Family 3: optional effects with unknown choice ----
OPT=[{'kind':'zone_move','from':'battlefield','to':'graveyard','types':['creature'],'object_id':'p1'},
     {'kind':'zone_move','from':'graveyard','to':'battlefield','types':['creature']},
     {'kind':'sacrifice','types':['creature'],'to_zone':'graveyard','object_id':'p1'},
     {'kind':'destroy','types':['creature'],'to_zone':'graveyard'},
     {'kind':'token_create','quantity':1,'token':{'types':['creature']}}]
OL=[{'kind':'event','hook':h,'where':w} for h,w in [('permanent.dies',{}),('permanent.sacrifice',{}),('permanent.destroy',{}),
     ('battlefield.leave',{}),('battlefield.enter',{'types':['creature']}),('graveyard.enter',{})]]
for e in OPT:
    yes=project_resolved_effects([{**e,'optional':True,'chosen':True}],'y')
    unk=project_resolved_effects([{**e,'optional':True}],'u')
    for alt in OL:
        a=G(yes,alt)[0]; b=G(unk,alt)[0]
        if a==YES and b==NO: rec2('F3 unknown optional choice gives FAILED where chosen gives satisfied',(e['kind'],e.get('to'),alt['hook'],a,b))
        if a==NO and b==UNKNOWN: rec2('F3b unknown optional choice gives unknown where chosen proves failed',(e['kind'],e.get('to'),alt['hook'],a,b))

# ---- Family 4: bounded quantity ----
from semantic_expression_v0_2_1 import Bounds
bq=project_resolved_effects([{'kind':'token_create','quantity':Bounds(1,3),'token':{'types':['creature']}}],'q')
if G(bq,{'kind':'event','hook':'battlefield.enter','where':{'types':['creature']}})[0]!=YES:
    rec2('F4 quantity Bounds(1,3) cannot prove an entry happened',G(bq,{'kind':'event','hook':'battlefield.enter','where':{'types':['creature']}}))

for name,ex in sorted(v2.items()):
    print(f'\n### {name}: {len(ex)} violations; first example:')
    print('  ',json.dumps(ex[0],default=str)[:1200])
print('\nall M5 examples:'); [print('  ',x) for k in violations if k.startswith('M5') for x in violations[k]]
