#!/usr/bin/env python3
"""Archive policy helpers. Nothing here edits the Sheet or an archive.

  python freeze_check.py guard-input export.xlsx
      refuse an archive as a build input (name contains _ARCHIVE or lives under an archive folder)
  python freeze_check.py status --db mtg_cards_v0.2.sqlite --live-modified 2026-10-15T19:03:42.774Z
      is the DB built from the Sheet's current revision? (pass the Sheet's Drive modifiedTime)
  python freeze_check.py verify-freeze --frozen "..._20261020-2100Z_ARCHIVE.xlsx" --live export.xlsx --manifest freezes.jsonl
      before a major structural change: the frozen copy must be named as an archive and hold the same
      Collection and Deck Allocations values as the live export; the result is appended to a manifest.

Policy (Zach, 2026-10-15/20): no Sheet edits during querying; an archive is recovery only, never the
source of current custody; copy + rename the original with timestamp + _ARCHIVE into the archive
folder, verify it, then change only the clone.
"""
import argparse, datetime, hashlib, json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE_MARKERS = ('_archive', '/archive/')


def is_archive(path):
    p = str(path).replace('\\', '/').lower()
    return any(m in p for m in ARCHIVE_MARKERS)


def guard_input(path):
    if is_archive(path): raise SystemExit(f'REFUSED: {path} is an archive; build only from a fresh export of the working Sheet')
    return {'input': str(path), 'archive_guard': 'ok'}


def status(db, live_modified):
    c = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    run = c.execute("select source_modified_utc,input_sha256,built_utc from import_runs order by built_utc desc limit 1").fetchone()
    built_from = run[0] if run else None
    return {'db_built_from_sheet_revision': built_from, 'sheet_modified_now': live_modified,
            'state': 'current' if built_from == live_modified else 'STALE: export the working Sheet and rebuild',
            'source_sha256': run[1] if run else None}


def custody_values(xlsx):
    sys.path.insert(0, str(HERE / 'vendor'))
    from mtg_eval import _adapter
    raw = _adapter.read_xlsx_selected(str(xlsx), {'Collection', 'Deck Allocations'})
    return hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()


def verify_freeze(frozen, live, manifest):
    if not is_archive(frozen): raise SystemExit('frozen copy must carry the _ARCHIVE name')
    if is_archive(live): raise SystemExit('live export must not be an archive')
    a, b = custody_values(frozen), custody_values(live)
    rec = {'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'frozen': Path(frozen).name,
           'frozen_sha256': hashlib.sha256(Path(frozen).read_bytes()).hexdigest(), 'live': Path(live).name,
           'custody_values_sha256': a, 'matches_live': a == b}
    with open(manifest, 'a', encoding='utf-8') as f: f.write(json.dumps(rec) + '\n')
    if a != b: raise SystemExit('frozen copy does not match the live custody values; do not restructure yet')
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest='cmd', required=True)
    x = s.add_parser('guard-input'); x.add_argument('path')
    x = s.add_parser('status'); x.add_argument('--db', default=str(HERE / 'mtg_cards_v0.2.sqlite')); x.add_argument('--live-modified', required=True)
    x = s.add_parser('verify-freeze'); x.add_argument('--frozen', required=True); x.add_argument('--live', required=True); x.add_argument('--manifest', default='freezes.jsonl')
    a = ap.parse_args()
    r = {'guard-input': lambda: guard_input(a.path), 'status': lambda: status(a.db, a.live_modified),
         'verify-freeze': lambda: verify_freeze(a.frozen, a.live, a.manifest)}[a.cmd]()
    print(json.dumps(r, indent=2))


if __name__ == '__main__':
    main()
