"""Reviewer-facing projection of the v0.2 packets (Kate, 2026-10-28): the same 414 selections, no resampling.

Reviewers see only item, role, card, type_line and oracle_text. The 360 untagged and 54 challenge items are shuffled
together under opaque ids (R001-R414) and split into batches of 46. The private key maps R ids back to U/C ids,
stratum and mechanism; it is for analysis only and must not be given to reviewers."""
import json, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = 46
items = [json.loads(l) for name in ('blind_packet.jsonl', 'challenge_packet.jsonl') for l in open(HERE / name, encoding='utf-8')]
random.Random('audit-v0.2-reviewer-order').shuffle(items)
key, review = [], []
for i, p in enumerate(items):
    rid = f'R{i + 1:03d}'
    key.append({'review_item': rid, 'source_item': p['item'], 'stratum': p.get('stratum'), 'mechanism': p.get('mechanism'),
                'candidates_in_pool': p.get('candidates_in_pool')})
    review.append({'item': rid, 'role': p['role'], 'card': p['card'], 'type_line': p['type_line'], 'oracle_text': p['oracle_text']})
out = HERE / 'reviewer'
out.mkdir(exist_ok=True)
for b in range(0, len(review), BATCH):
    with open(out / f'batch_{b // BATCH + 1:02d}.jsonl', 'w', encoding='utf-8') as f:
        for r in review[b:b + BATCH]:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(HERE / 'private_key.jsonl', 'w', encoding='utf-8') as f:
    for k in key:
        f.write(json.dumps(k, ensure_ascii=False) + '\n')
print(len(review), 'items in', -(-len(review) // BATCH), 'batches')
