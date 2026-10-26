"""Run the 0.3.0 API through SQLite with runtime regex (v0.1 bridge), persisted facts (v0.2, same inventory),
or persisted facts with the 0.2.1 inventory policy (restored Offspring rows, Oracle rules text for reconciled cards).
  python parity_eval.py regex|facts|policy mtg_cards_v0.2.sqlite out.json"""
import json, sys, time, re
sys.path.insert(0, '.')
from bridge_v02 import open_evaluator
mode, db, out = sys.argv[1], sys.argv[2], sys.argv[3]
ev = open_evaluator(db, games=300, engine_games=4, use_facts=(mode != 'regex'), strict=(mode != 'regex'), policy=(mode == 'policy'))  # modes: regex | facts | policy
decks = sorted(ev.inv.decks)
calls = [('deck', (d,)) for d in decks]
calls += [('card', (c,)) for c in ['The Necrobloom', 'Avenger of Zendikar', 'Cultivate', 'Duty Beyond Death', 'Mechan Assembler',
                                   'Sol Ring', 'Tendershoot Dryad', 'Vraska, Soul of Stone', 'Pactdoll Terror', 'Altered Ego']]
calls += [('card', ('The Necrobloom', 'Necrobloom')), ('inventory', ()), ('build', ('The Necrobloom',)),
          ('compare', ('Necrobloom', [(ev.inv.deck_cards('Necrobloom')[5], 'Cultivate')])), ('upgrades', ('Vraska',)),
          ('transfer', (next(c for c in sorted(ev.inv.deck_cards('Sharuum')) if not ev.inv.is_land(c) and ev.inv.cards[c]['Section' if False else 'Card Name'] and ev.inv.legal_in(c, ev.inv.deck_ci('Vraska'))[0] and c not in ev.inv.commanders('Sharuum')), 'Sharuum', 'Vraska')), ('portfolio', ('Duty Beyond Death',))]
# count regex work done during queries (re module calls + compiled-pattern methods)
counts = {'re': 0}; where = {}
def prof(frame, event, arg):
    if event == 'c_call' and getattr(arg, '__qualname__', '').startswith('Pattern.'):
        counts['re'] += 1; f = frame.f_code; where[f'{f.co_filename.split("/")[-1]}:{f.co_name}'] = where.get(f'{f.co_filename.split("/")[-1]}:{f.co_name}', 0) + 1
    elif event == 'call' and frame.f_code.co_filename.endswith('/re/__init__.py') and frame.f_code.co_name in ('search', 'match', 'findall', 'sub', 'split', 'finditer', 'fullmatch'): counts['re'] += 1
res, t0 = {}, time.time()
for fn, args in calls:
    key = fn + ':' + json.dumps(args)
    sys.setprofile(prof)
    try:
        r = getattr(ev, fn)(*args)
    except Exception as e:
        r = {'error': repr(e)}
    finally:
        sys.setprofile(None)
    res[key] = json.loads(json.dumps(r, default=str, sort_keys=True))
summary = {'mode': mode, 'calls': len(calls), 'seconds': round(time.time() - t0, 1), 'regex_calls_during_queries': counts['re'],
           'regex_sites': dict(sorted(where.items(), key=lambda x: -x[1])[:12]), 'fact_misses': ev.facts.stats['misses'] if ev.facts else None}
json.dump({'summary': summary, 'results': res}, open(out, 'w'), sort_keys=True)
print(json.dumps(summary))
