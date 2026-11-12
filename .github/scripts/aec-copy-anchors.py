"""Copy the source files that .aec/records.jsonl anchors into the isolated check input.

Runs on the runner with the trusted base checkout as cwd, before any candidate code runs.
Only relative paths to regular, non-symlink files inside the checkout are copied; anything
else fails the step, so the candidate never sees a path chosen outside the base revision.
Usage: python3 -I -B .github/scripts/aec-copy-anchors.py DEST
"""
import json, shutil, sys
from pathlib import Path


def anchor_paths(records: Path) -> list[str]:
    out = set()
    for line in records.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '//')):   # AEC records allow // comment lines
            continue
        for a in json.loads(line).get('anchors') or []:
            out.add(a['path'])
    return sorted(out)


def copy_anchors(root: Path, dest: Path) -> list[str]:
    root = root.resolve()
    copied = []
    for rel in anchor_paths(root / '.aec' / 'records.jsonl'):
        p = Path(rel)
        if p.is_absolute() or '..' in p.parts:
            raise SystemExit(f'refusing anchor path outside the checkout: {rel!r}')
        src = root / p
        if src.is_symlink() or not src.is_file() or root not in src.resolve().parents:
            raise SystemExit(f'anchor is not a regular file in the checkout: {rel!r}')
        target = dest / p
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        copied.append(rel)
    return copied


if __name__ == '__main__':
    for rel in copy_anchors(Path.cwd(), Path(sys.argv[1])):
        print('anchor copied:', rel)
