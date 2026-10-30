#!/usr/bin/env python3
"""Check and install the KB databases an agent needs for ontology-grounded card work. Standard library only.

The databases are derived and gitignored (data/README.md), so a fresh clone has none. Without them the
mtgtools verbs that read DIO contracts (card, explore, hypothesis, check) cannot run, and an agent falls back
to reading Oracle text with its own reasoning. This tool makes that state visible and fixable.

  python3 tools/kb_bootstrap.py status            # what is present, and the grounding level it allows
  python3 tools/kb_bootstrap.py status --json
  python3 tools/kb_bootstrap.py install           # find the pinned release zip locally, else download it
  python3 tools/kb_bootstrap.py install --zip PATH
  python3 tools/kb_bootstrap.py install --url URL

Grounding levels (status, also exit codes 0 / 3 / 4):
  kb_grounded     the KB database matches the release this checkout pins (tools/kb_release.json,
                  kb/MANIFEST.sha256). mtgtools reads DIO candidate contracts.
  kb_unpinned     a KB database is present but is not the pinned release. Usable; cite its release.
  doctrine_only   no KB database. The DIO documents are still in the repo (mtgtools dio), but any
                  interaction analysis is the agent's own reading of Oracle text and must say so.

install verifies the zip's sha256 when it is the pinned zip, and each database against kb/MANIFEST.sha256,
before it moves anything into kb/. It never overwrites a database that already matches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = Path(__file__).resolve().parent / 'kb_release.json'
KB = 'kb'
DOCTRINE = [
    'kb/reference_sources/MTG DECK INTERACTION ONTOLOGY v3_1_1.md',
    'kb/reference_sources/MTG DECK INTERACTION ONTOLOGY v3.1.1 — ADDENDUM(1).md',
    'kb/addendum/DIO_v3.1.1_compat_addendum_v0.1.md',
    'kb/reference_sources/MTG_Grammar_Rules_Vocabulary_Registry_v0.1.json',
]
EXIT = {'kb_grounded': 0, 'kb_unpinned': 3, 'doctrine_only': 4}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_pin(root: Path = ROOT) -> dict:
    pin = json.loads((root / 'tools' / 'kb_release.json').read_text(encoding='utf-8'))
    pin['expected'] = manifest_hashes(root, pin['databases'])
    return pin


def manifest_hashes(root: Path, names) -> dict:
    """The database hashes kb/MANIFEST.sha256 records for this release."""
    out = {}
    m = root / KB / 'MANIFEST.sha256'
    if m.exists():
        for line in m.read_text(encoding='utf-8').splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip() in names:
                out[parts[1].strip()] = parts[0]
    return out


def status(root: Path = ROOT) -> dict:
    pin = load_pin(root)
    dbs = {}
    for name in pin['databases']:
        p = root / KB / name
        if not p.exists():
            dbs[name] = {'present': False}
            continue
        got = sha256(p)
        dbs[name] = {'present': True, 'sha256': got, 'matches_pinned_release': got == pin['expected'].get(name)}
    main = dbs[pin['databases'][0]]
    level = 'doctrine_only' if not main['present'] else 'kb_grounded' if main['matches_pinned_release'] else 'kb_unpinned'
    data = root / 'data'
    collections = sorted(str(p.relative_to(root)) for p in list(data.glob('*.xlsx')) + list(data.glob('*.sqlite'))) if data.exists() else []
    doctrine = {d: (root / d).exists() for d in DOCTRINE}
    next_steps = []
    if level == 'doctrine_only':
        next_steps.append('python3 tools/kb_bootstrap.py install   (or --zip PATH / --url URL)')
        next_steps.append('Until then: read the DIO (python3 -m mtgtools dio TERM) and label every interaction claim '
                          '"not KB-grounded: own reading of Oracle text".')
    elif level == 'kb_unpinned':
        next_steps.append(f'The KB present is not {pin["release"]}. Cite the release mtgtools reports, or reinstall.')
    if not collections:
        next_steps.append('No inventory export or collection database in data/: evaluator and compare need one '
                          '(data/README.md, docs/BRING_YOUR_OWN_COLLECTION.md).')
    return {'grounding': level, 'pinned_release': pin['release'], 'databases': dbs, 'doctrine': doctrine,
            'collections_in_data': collections, 'next_steps': next_steps}


def render(s: dict) -> str:
    out = [f'grounding: {s["grounding"]}   (pinned release {s["pinned_release"]})']
    for name, d in s['databases'].items():
        state = 'missing' if not d['present'] else 'ok' if d['matches_pinned_release'] else 'present, not the pinned release'
        out.append(f'  kb/{name}: {state}')
    for path, ok in s['doctrine'].items():
        out.append(f'  {path}: {"ok" if ok else "MISSING"}')
    out.append(f'  collections in data/: {", ".join(s["collections_in_data"]) or "none"}')
    out += [f'next: {n}' for n in s['next_steps']]
    return '\n'.join(out)


def find_zip(pin: dict, root: Path = ROOT):
    for d in pin.get('search_dirs', []):
        p = (root / d if not os.path.isabs(d) else Path(d)) / pin['zip_name']
        if p.exists():
            return p
    return None


def download(url: str, dest: Path) -> Path:
    print(f'downloading {url}', file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, 'wb') as f:
        shutil.copyfileobj(r, f)
    return dest


def install(zip_path: Path, root: Path = ROOT, pin: dict | None = None) -> list[str]:
    """Extract the release databases from zip_path into kb/ after verifying them. Returns what was done."""
    pin = pin or load_pin(root)
    done = []
    if zip_path.name == pin['zip_name']:
        got = sha256(zip_path)
        if got != pin['zip_sha256']:
            raise ValueError(f'{zip_path} sha256 {got[:12]}… is not the pinned {pin["zip_sha256"][:12]}…')
    with zipfile.ZipFile(zip_path) as z, tempfile.TemporaryDirectory(dir=root / KB) as tmp:
        members = {Path(n).name: n for n in z.namelist() if Path(n).name in pin['databases']}
        for name in pin['databases']:
            target = root / KB / name
            if target.exists() and sha256(target) == pin['expected'].get(name):
                done.append(f'kb/{name}: already the pinned release')
                continue
            if name not in members:
                raise ValueError(f'{zip_path} has no {name}')
            out = Path(z.extract(members[name], tmp))
            got = sha256(out)
            want = pin['expected'].get(name)
            if want and got != want:
                raise ValueError(f'{name} in {zip_path} has sha256 {got[:12]}…, kb/MANIFEST.sha256 says {want[:12]}…')
            os.replace(out, target)
            done.append(f'kb/{name}: installed ({got[:12]}…)' + ('' if want else ' (no manifest hash to check)'))
    return done


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog='kb_bootstrap', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('status'); s.add_argument('--json', action='store_true')
    s = sub.add_parser('install'); g = s.add_mutually_exclusive_group(); g.add_argument('--zip'); g.add_argument('--url')
    a = p.parse_args(argv)
    if a.cmd == 'status':
        st = status()
        print(json.dumps(st, indent=2) if a.json else render(st))
        return EXIT[st['grounding']]
    pin = load_pin()
    try:
        if a.zip:
            zp = Path(a.zip)
        elif a.url:
            zp = download(a.url, Path(tempfile.mkdtemp()) / Path(a.url).name)
        else:
            zp = find_zip(pin)
            if zp is None:
                try:
                    zp = download(pin['url'], Path(tempfile.mkdtemp()) / pin['zip_name'])
                except OSError as e:
                    print(f'error: {pin["zip_name"]} is not in {", ".join(pin["search_dirs"])} and the download failed '
                          f'({e}). Ask Zach for the release zip, or pass --zip / --url. See data/README.md.', file=sys.stderr)
                    return 2
        for line in install(zp, pin=pin):
            print(line)
    except (ValueError, zipfile.BadZipFile, OSError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 2
    print(render(status()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
