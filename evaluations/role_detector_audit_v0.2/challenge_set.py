"""Mechanism challenge set for the role-detector audit v0.2. Tests known failure mechanisms; it is NOT
used for population recall (Kate, 2026-10-28). Up to 5 owned cards per mechanism, fixed seed. Run from the repo root."""
import json, random, re, sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
# mechanism -> (role it may bear on, Oracle-text pattern used only to pick candidates)
MECHANISMS = {
    'offspring': ('token_maker', r'\boffspring\b'), 'encore': ('token_maker', r'\bencore\b'), 'populate': ('token_maker', r'\bpopulate\b'),
    'myriad': ('token_maker', r'\bmyriad\b'), 'token_replacement': ('token_maker', r'tokens? would be created|those tokens plus'),
    'flashback': ('recursion', r'\bflashback\b'), 'dredge': ('recursion', r'\bdredge\b'), 'reanimation': ('recursion', r'from (?:a|your) graveyard (?:to|onto) the battlefield'),
    'cycling': ('draw', r'\bcycling\b'), 'ward_grant': ('protection', r'(?:have|has|gains?) ward'),
    'equipment_protection': ('protection', r'equipped creature (?:has|gets [^.]*and has) [^.]*(?:hexproof|indestructible)'),
    'conditional_sacrifice': ('sac_outlet', r'you may sacrifice (?:a|an|another)'), 'restricted_mana': ('ramp', r'spend this mana only'),
}
c = sqlite3.connect('kb/mtg_cards_v0.2.sqlite'); c.row_factory = sqlite3.Row
rows = c.execute('select card_name, type_line, oracle_text from cards where owned_min > 0 order by card_name').fetchall()
out = []
for mech, (role, pat) in MECHANISMS.items():
    hits = [r for r in rows if re.search(pat, (r['oracle_text'] or '').lower())]
    for r in random.Random(f'audit-v0.2-challenge-{mech}').sample(hits, min(5, len(hits))):
        out.append({'mechanism': mech, 'role': role, 'card': r['card_name'], 'type_line': r['type_line'], 'oracle_text': r['oracle_text'], 'candidates_in_pool': len(hits)})
random.Random('audit-v0.2-challenge-order').shuffle(out)
with open(HERE / 'challenge_packet.jsonl', 'w', encoding='utf-8') as f:
    for i, p in enumerate(out):
        p['item'] = f'C{i + 1:03d}'
        f.write(json.dumps(p, ensure_ascii=False) + '\n')
print(len(out), {m: sum(p['mechanism'] == m for p in out) for m in MECHANISMS})
