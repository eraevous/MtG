#!/usr/bin/env python3
"""Render interpretation-log reading pages as markdown into build/readings/ (gitignored). D-0033 (b).

  python3 tools/render_readings.py                 # one page per subject in kb/overrides/interpretations.jsonl
  python3 tools/render_readings.py "Evolution Sage" proliferate
  python3 tools/render_readings.py --out build/readings --db kb/mtg_cards_v0.2.sqlite

Each page is a cache of `python3 -m mtgtools reading NAME`, never a home: it is rebuilt from the log and the KB, is
never committed (build/ is in .gitignore, and the script refuses an output directory git does not ignore), and says
`candidate` on every reading. It reads the verb's JSON and nothing else, so mtgtools stays a non-writer (the reviewer's
condition on D-0033). Rendered text is quoted data: readings are printed inside blockquotes, not as headings.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / 'kb' / 'overrides' / 'interpretations.jsonl'
OUT = ROOT / 'build' / 'readings'
HEADER = ('> **Generated, not a home.** Derived from the interpretation log (head `{head}`, {rows} rows, chain {chain}) and '
          'KB release `{release}` by tools/render_readings.py. Every reading below is a **candidate**: two readers agreeing is '
          'not a review, and {promoted} readings have been promoted. Cite the interpretation id and its candidate status, '
          'never this page.\n')


def subjects(log=LOG):
    seen = []
    for line in Path(log).read_text(encoding='utf-8').splitlines():
        if line.startswith('{'):
            n = json.loads(line).get('card_or_mechanic')
            if n and n not in seen:
                seen.append(n)
    return seen


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.casefold()).strip('-') or 'subject'


def fetch(name, db=None):
    cmd = [sys.executable, '-m', 'mtgtools'] + (['--db', db] if db else []) + ['reading', name]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    env = json.loads(p.stdout)
    if 'error' in env:
        raise SystemExit(f'mtgtools reading {name!r}: {env["error"]}')
    return env


def _quote(text):
    return '\n'.join('> ' + ln for ln in str(text or '').splitlines()) or '> (empty)'


def render(env):
    d, b = env['data'], env['data']['banner']
    out = [f"# Readings: {d['subject']} (candidate)\n",
           HEADER.format(head=(b['log_head'] or 'none')[:12], rows=b['log_rows'], chain=b['chain'],
                         release=('none (log only)' if env['grounding']['level'] == 'log_only' else env['collection'].get('release') or 'unknown'), promoted=b['promoted'])]
    if not d['current']:
        out.append('No current rows: nobody has asked about this yet. That is not the same as settled.\n')
    for v in d['current']:
        changed = ' · **Oracle text changed since this reading**' if v['oracle_text_changed_since'] else ''
        out.append(f"## {v['outcome']} · candidate · `{v['interpretation_id'][:10]}`{changed}\n")
        out.append('Question:\n\n' + _quote(v['question']) + '\n')
        for r in v['readings']:
            cites = ', '.join(r.get('cr_citations') or [])
            out.append(f"Reading by {r.get('party')} ({r.get('model')}), citing {cites}:\n\n" + _quote(r.get('reading')) + '\n')
            if r.get('uncertainty'):
                out.append(f"Uncertainty stated by {r.get('party')}:\n\n" + _quote(r['uncertainty']) + '\n')
            if r.get('scenario'):
                out.append(f"Scenario from {r.get('party')}:\n\n" + _quote(r['scenario']) + '\n')
        for k, label in (('positive', 'Positive scenario'), ('near_miss', 'Near-miss scenario')):
            if (v.get('scenarios') or {}).get(k):
                out.append(f'{label}:\n\n' + _quote(v['scenarios'][k]) + '\n')
        if v['notes']:
            out.append('Notes:\n\n' + _quote(v['notes']) + '\n')
        out.append(f"Source: {v['source']}\n")
    if d['superseded']:
        out.append('## Superseded\n')
        out += [f"- `{v['interpretation_id'][:10]}` ({v['outcome']}) superseded by `{v['superseded_by'][:10]}`" for v in d['superseded']]
        out.append('')
    if d['kb_contracts']:
        out.append('## KB contracts (candidate unless semantic_reviewed)\n')
        out += [f"- `{k['contract_id']}`: {k['queue_state']}" + (f" ({', '.join(k['failed_checks'])})" if k['failed_checks'] else '')
                for k in d['kb_contracts']]
        out.append('')
    out.append('## Limits\n')
    out += [f'- {x}' for x in d['limits']]
    return '\n'.join(out) + '\n'


def ignored(path):
    return subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT).returncode == 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('names', nargs='*'); ap.add_argument('--out', default=str(OUT)); ap.add_argument('--db')
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    if not ignored(out / 'probe.md'):
        raise SystemExit(f'{out} is not gitignored; reading pages must never be committed (D-0033 b)')
    out.mkdir(parents=True, exist_ok=True)
    for name in a.names or subjects():
        p = out / f'{slug(name)}.md'
        p.write_text(render(fetch(name, a.db)), encoding='utf-8')
        print(p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
