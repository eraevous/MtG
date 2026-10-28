"""Blind sample of untagged negatives for the role-detector audit v0.2 (Kate's design, 2026-10-28).

For each role: distinct card names with no capability claim of that role from any source (detector, Sheet tag,
hand label or review), split by whether the name is in an active deck; 20 per stratum, fixed seed.
Writes population.json (stratum sizes + seed) and blind_packet.jsonl (no detector or tag information).
Run from the repo root against KB r20261028.
"""
import json, random, sqlite3, sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROLES = ['spot_removal', 'protection', 'recursion', 'ramp', 'fixing', 'draw', 'closer', 'sac_outlet', 'token_maker']
PER_STRATUM = 20

c = sqlite3.connect('kb/mtg_cards_v0.2.sqlite'); c.row_factory = sqlite3.Row
deckcards = {r[0] for r in c.execute('select distinct card_name from active_deck_cards')}
names = [r[0] for r in c.execute('select card_name from cards where owned_min > 0 order by card_name')]
pop, packet = {}, []
for role in ROLES:
    claimed = {r[0] for r in c.execute('select distinct card_name from capability_claims where capability=?', (role,))}
    neg = [n for n in names if n not in claimed]
    strata = {'in_active_deck': [n for n in neg if n in deckcards], 'outside_active_decks': [n for n in neg if n not in deckcards]}
    rng = random.Random(f'audit-v0.2-untagged-{role}')
    pop[role] = {k: len(v) for k, v in strata.items()}
    for k, v in strata.items():
        for n in rng.sample(v, min(PER_STRATUM, len(v))):
            r = c.execute('select type_line, oracle_text from cards where card_name=?', (n,)).fetchone()
            packet.append({'role': role, 'stratum': k, 'card': n, 'type_line': r['type_line'], 'oracle_text': r['oracle_text']})
rng = random.Random('audit-v0.2-blind-order')
rng.shuffle(packet)
for i, p in enumerate(packet):
    p['item'] = f'U{i + 1:03d}'
(HERE / 'population.json').write_text(json.dumps({'kb_release': 'mtg-kb-v0.2.1-r20261028', 'seed_prefix': 'audit-v0.2-untagged-',
                                                  'per_stratum': PER_STRATUM, 'strata': pop}, indent=1) + '\n')
with open(HERE / 'blind_packet.jsonl', 'w', encoding='utf-8') as f:
    for p in packet:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')
print(json.dumps(pop), len(packet))
