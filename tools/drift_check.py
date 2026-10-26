#!/usr/bin/env python3
"""AEC drift check v0 for the MtG repo. Standard library only.

Runs mechanical checks of the repo against its declared contracts:

  frozen        Pinned files (the 2026-10-20 frozen predictions) still match their SHA-256.     [error]
  purpose       Each codex_++/purpose_files/*.purpose.md names a source file that exists, and
                its @ai-dependencies matches the source's local imports.                          [error / warning]
  semantic      Python outside the semantic owners (grammar/, kb/) that both handles
                `oracle_text` and uses regular expressions must declare `@ai-semantic-role:`
                (P-01: no undeclared competing semantic authority).                               [warning]
  append-only   Ledger files only grow: the base revision's content must be a prefix of
                the current content (needs --base <git ref>).                                     [error]

This checks structure, not purpose. A clean run does not show that P-00..P-05 survived.
See codex_++/project.purpose.md.

Usage:
  python3 tools/drift_check.py                 # all checks except append-only
  python3 tools/drift_check.py --base origin/main
  python3 tools/drift_check.py --strict        # warnings count as failures
  python3 tools/drift_check.py --json
  python3 tools/drift_check.py --hook          # Claude Code PostToolUse hook (reads hook JSON on stdin)
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = Path(__file__).resolve().parent / "drift_rules.json"


class Report:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, level: str, check: str, path: str, msg: str):
        self.items.append({"level": level, "check": check, "path": path, "msg": msg})

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "error"]

    @property
    def warnings(self):
        return [i for i in self.items if i["level"] == "warning"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_rules(root: Path) -> dict:
    path = root / "tools" / "drift_rules.json"
    return json.loads((path if path.exists() else RULES).read_text(encoding="utf-8"))


# --- frozen -----------------------------------------------------------------------------------
def check_frozen(root: Path, rules: dict, rep: Report):
    for rel, digest in rules.get("frozen", {}).items():
        p = root / rel
        if not p.exists():
            rep.add("error", "frozen", rel, "frozen file is missing")
        elif sha256(p) != digest:
            rep.add("error", "frozen", rel,
                    "frozen file changed. Frozen predictions are never edited; write a new, separately "
                    "versioned file instead")


# --- purpose ----------------------------------------------------------------------------------
TAG = re.compile(r"^\s*[-*]?\s*@([\w-]+):\s*(.*?)\s*$")


def parse_tags(text: str) -> dict[str, str]:
    tags: dict[str, str] = {}
    for line in text.splitlines():
        m = TAG.match(line)
        if m and m.group(1) not in tags:
            tags[m.group(1)] = m.group(2).strip().strip('"')
    return tags


def split_list(v: str) -> list[str]:
    v = v.strip()
    if not v or v.lower() in {"none", "n/a", "-"}:
        return []
    return [x.strip() for x in re.split(r"[,\s]+", v) if x.strip()]


def local_imports(src: Path) -> set[str]:
    """Top-level names of imports that resolve to sibling modules or packages of `src`."""
    try:
        tree = ast.parse(src.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    here = src.parent
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                names.add(node.module.split(".")[0])
            elif node.level:
                names.update(a.name for a in node.names)
            elif node.module:
                names.add(node.module.split(".")[0])
    return {n for n in names if (here / f"{n}.py").exists() or (here / n / "__init__.py").exists()}


def check_purpose(root: Path, rules: dict, rep: Report):
    pdir = root / rules.get("purpose_dir", "codex_++/purpose_files")
    for pf in sorted(pdir.glob("*.purpose.md")):
        rel = pf.relative_to(root).as_posix()
        tags = parse_tags(pf.read_text(encoding="utf-8"))
        src_rel = tags.get("ai-source-file", "")
        if not src_rel:
            rep.add("error", "purpose", rel, "missing @ai-source-file")
            continue
        if src_rel.lower() in {"n/a", "none"}:
            continue
        src = root / src_rel
        if not src.exists():
            rep.add("error", "purpose", rel, f"@ai-source-file {src_rel} does not exist")
            continue
        if src.suffix != ".py" or "ai-dependencies" not in tags:
            continue
        declared = set(split_list(tags["ai-dependencies"]))
        local_declared = {d for d in declared if not d.startswith("ext:")}
        observed = local_imports(src)
        for name in sorted(observed - local_declared):
            rep.add("warning", "purpose", rel,
                    f"{src_rel} imports local module '{name}', which @ai-dependencies does not declare")
        for name in sorted(local_declared - observed):
            rep.add("warning", "purpose", rel,
                    f"@ai-dependencies declares '{name}', but {src_rel} does not import it")


# --- semantic authority -----------------------------------------------------------------------
def imports_module(text: str, module: str) -> bool:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return bool(re.search(rf"\bimport\b[^\n]*\b{module}\b", text))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] == module for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and not node.level and (node.module or "").split(".")[0] == module:
            return True
    return False


def check_semantic(root: Path, rules: dict, rep: Report):
    owners = tuple(rules.get("semantic_owners", []))
    exclude = tuple(rules.get("scan_exclude", []))
    for py in sorted(root.rglob("*.py")):
        rel = py.relative_to(root).as_posix()
        if rel.startswith(owners) or rel.startswith(exclude) or "/fixtures/" in f"/{rel}":
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "oracle_text" not in text:
            continue
        uses_re = imports_module(text, "re")
        if uses_re and "@ai-semantic-role:" not in text:
            rep.add("warning", "semantic", rel,
                    "reads oracle_text and pattern-matches it outside grammar/ or kb/ without declaring "
                    "'@ai-semantic-role: verifier|candidate-source'. A competing semantic authority? (P-01)")


# --- append-only ------------------------------------------------------------------------------
def git_show(root: Path, ref: str, rel: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=root, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def check_append_only(root: Path, rules: dict, rep: Report, base: str):
    for rel in rules.get("append_only", []):
        old = git_show(root, base, rel)
        if old is None:
            continue  # new in this change
        p = root / rel
        if not p.exists():
            rep.add("error", "append-only", rel, f"append-only file deleted (exists at {base})")
            continue
        if not p.read_bytes().startswith(old):
            rep.add("error", "append-only", rel,
                    f"append-only file was rewritten, not appended (compared with {base}). Supersede "
                    "earlier entries with new entries instead")


# --- driver -----------------------------------------------------------------------------------
def run(root: Path = ROOT, base: str | None = None) -> Report:
    rules = load_rules(root)
    rep = Report()
    check_frozen(root, rules, rep)
    check_purpose(root, rules, rep)
    check_semantic(root, rules, rep)
    if base:
        check_append_only(root, rules, rep, base)
    return rep


def render(rep: Report) -> str:
    if not rep.items:
        return "drift_check: clean (structural checks only, not a purpose review)"
    lines = [f"[{i['level'].upper()}] {i['check']}: {i['path']}: {i['msg']}" for i in rep.items]
    lines.append(f"drift_check: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--base", help="git ref to compare append-only files against")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hook", action="store_true", help="Claude Code PostToolUse mode")
    a = ap.parse_args(argv)
    if a.hook:
        try:
            json.load(sys.stdin)  # payload unused in v0: we re-check the whole repo, which is fast
        except Exception:
            pass
        rep = run(Path(a.root))
        if rep.errors:
            print(render(rep), file=sys.stderr)
            return 2  # Claude Code feeds stderr back to the agent
        return 0
    rep = run(Path(a.root), a.base)
    print(json.dumps(rep.items, indent=1) if a.json else render(rep))
    failed = rep.errors or (a.strict and rep.warnings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
