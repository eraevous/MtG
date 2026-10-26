"""Render a Result as Markdown (for people) or JSON (for other programs)."""
import json


def _cell(v):
    return str(v).replace('|', '/').replace('\n', ' ')


def table(rows):
    cols = []
    for r in rows:
        for k in r:
            if k not in cols: cols.append(k)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    out += ['| ' + ' | '.join(_cell(r.get(c, '')) for c in cols) + ' |' for r in rows]
    return '\n'.join(out)


def markdown(res):
    lines = [f"# {res['title']}", '']
    lines += [f'- {s}' for s in res['summary']] + ['']
    ok, why = res['conclusive']
    lines += [f"**Conclusive:** {'yes' if ok else 'no'}. {why}", '']
    for h, content in res['sections']:
        lines += [f'## {h}', '']
        if isinstance(content, str): lines.append(content)
        elif content and isinstance(content[0], dict): lines.append(table(content))
        else: lines += [f'- {x}' for x in content]
        lines.append('')
    if res['uncertainty']:
        lines += ['## Uncertainty', ''] + [f'- {u}' for u in res['uncertainty']] + ['']
    if res['limitations']:
        lines += ['## Not modelled', ''] + [f'- {u}' for u in res['limitations']] + ['']
    return '\n'.join(lines)


def to_json(res):
    return json.dumps({k: v for k, v in res.items()}, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
