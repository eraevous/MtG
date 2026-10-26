"""Hash-chained, append-only JSONL files (review overlay, Oracle reconciliation).

Each line holds the record's fields plus `prev` (the previous line's id) and an id that is the SHA-256
of prev + the canonical record. Editing, reordering or deleting any line breaks the chain."""
import json
from pathlib import Path
import kbfacts as F


def read(path, fields, id_key):
    p = Path(path)
    if not p.exists(): return []
    out, prev = [], ''
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'): continue
        r = json.loads(line)
        if r.get('prev') != prev: raise ValueError(f'{p.name} line {i}: hash chain broken')
        if r.get(id_key) != F.sha(prev, F.dumps({k: r.get(k) for k in fields})): raise ValueError(f'{p.name} line {i}: {id_key} does not match content')
        prev = r[id_key]; out.append(r)
    return out


def append(path, fields, id_key, body):
    rows = read(path, fields, id_key)
    prev = rows[-1][id_key] if rows else ''
    rec = dict(body, prev=prev, **{id_key: F.sha(prev, F.dumps({k: body.get(k) for k in fields}))})
    with open(path, 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + '\n')
    return rec
