#!/usr/bin/env python3
"""Check whether upstream AEC has moved past the pin, and test MtG's records against the new commit.
Standard library only (git on PATH). Used by .github/workflows/aec-upstream.yml (option B, Zach 2026-11-01).

  python3 tools/aec_sync.py                         # report only: is the pin current?
  python3 tools/aec_sync.py --test                  # also clone the upstream head, run aec check + scenarios
  python3 tools/aec_sync.py --test --write          # and, if every check passes, move the pin
  python3 tools/aec_sync.py --test --report FILE    # write a Markdown report (PR or issue body)

Exit codes: 0 pin is current, or upstream moved and every check passed (the pin is moved with --write);
            3 upstream moved and a check failed (nothing is written); 2 usage or network error.

Moving the pin never edits .aec/records.jsonl. If upstream changed the record format, the checks fail and a person
appends new record versions (append-only, .aec/README.md). The PR merge is Zach's decision (D-0021, D-0022).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = "tools/aec_upstream.json"


def git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def upstream_head(repo: str, branch: str = "main") -> str:
    out = git("ls-remote", repo, f"refs/heads/{branch}").split()
    if not out:
        raise RuntimeError(f"{repo} has no branch {branch}")
    return out[0]


def run_checks(aec_src: Path, root: Path) -> list[dict]:
    """aec check on the records, then aec impact on each scenario. Each result: name, ok, output."""
    env_cmd = [sys.executable, "-m", "aec"]
    jobs = [("check", ["check", ".aec/records.jsonl"])]
    for s in sorted((root / ".aec/scenarios").glob("*.jsonl")):
        jobs.append((f"impact {s.name}", ["impact", ".aec/records.jsonl", s.relative_to(root).as_posix()]))
    results = []
    for name, args in jobs:
        r = subprocess.run(env_cmd + args, cwd=root, capture_output=True, text=True,
                           env={"PYTHONPATH": str(aec_src), "PATH": "/usr/bin:/bin"})
        out = (r.stdout + r.stderr).strip()
        results.append({"name": name, "ok": r.returncode == 0, "output": out})
    return results


def summary_line(output: str) -> str:
    lines = [l for l in output.splitlines() if l.strip()]
    return lines[-1] if lines else "(no output)"


def moved_pin(pin: dict, head: str, date: str) -> dict:
    """The new pin. Keeps a history of earlier commits so a bump is visible in the file itself."""
    new = dict(pin)
    history = list(pin.get("history", []))
    history.append({"commit": pin["commit"], "date": pin.get("date")})
    new.update({"commit": head, "date": date, "history": history})
    new.pop("aec_version", None)  # stated by hand at the old pin; the report lists what changed instead
    return new


def render_report(pin: dict, head: str, log: list[str], results: list[dict]) -> str:
    ok = all(r["ok"] for r in results)
    lines = [
        f"Upstream AEC moved from `{pin['commit'][:7]}` to `{head[:7]}` ({len(log)} commit(s)).",
        "",
        "**Result:** " + ("every check passed at the new commit; this PR moves the pin."
                          if ok else "a check failed at the new commit; the pin was **not** moved."),
        "",
        "| Check | Result | Last line |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['name']} | {'pass' if r['ok'] else 'FAIL'} | `{summary_line(r['output'])}` |")
    lines += ["", "<details><summary>Upstream commits</summary>", "", *[f"- {l}" for l in log], "", "</details>", ""]
    if not ok:
        lines += ["Failing output:", ""]
        for r in results:
            if not r["ok"]:
                lines += [f"```\n$ aec {r['name']}\n{r['output'][-3000:]}\n```", ""]
        lines.append("If upstream changed the record format, append new record versions in `.aec/records.jsonl` "
                     "(never edit old lines), then re-run `python3 tools/aec_sync.py --test --write`.")
    lines += ["", "Structural checks only: a pass shows MtG's records still parse and resolve under the new AEC, "
              "not that the new AEC is better. Merging this PR is the decision to adopt it (D-0021, D-0022)."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--test", action="store_true", help="clone upstream head and run the checks")
    ap.add_argument("--write", action="store_true", help="move the pin when every check passes (needs --test)")
    ap.add_argument("--report", help="write a Markdown report here")
    ap.add_argument("--github-output", help="append key=value lines for GitHub Actions")
    a = ap.parse_args(argv)
    root = Path(a.root)
    pin = json.loads((root / PIN).read_text(encoding="utf-8"))
    try:
        head = upstream_head(pin["repo"])
    except RuntimeError as ex:
        print(f"aec_sync: {ex}", file=sys.stderr)
        return 2

    def out(**kv):
        if a.github_output:
            with open(a.github_output, "a", encoding="utf-8") as f:
                for k, v in kv.items():
                    f.write(f"{k}={v}\n")

    if head == pin["commit"]:
        print(f"aec_sync: pin {head[:7]} is current")
        out(moved="false")
        return 0
    print(f"aec_sync: upstream moved {pin['commit'][:7]} -> {head[:7]}")
    out(moved="true", head=head, short=head[:7])
    if not a.test:
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "aec"
        git("clone", "-q", pin["repo"], str(clone))
        git("checkout", "-q", head, cwd=clone)
        log = git("log", "--format=%h %ad %s", "--date=short", f"{pin['commit']}..{head}", cwd=clone).splitlines()
        date = git("log", "-1", "--format=%ad", "--date=short", head, cwd=clone).strip()
        results = run_checks(clone / "src", root)
    ok = all(r["ok"] for r in results)
    for r in results:
        print(f"  {'pass' if r['ok'] else 'FAIL'}  {r['name']}: {summary_line(r['output'])}")
    if a.report:
        Path(a.report).write_text(render_report(pin, head, log, results), encoding="utf-8")
    out(ok=str(ok).lower())
    if not ok:
        return 3
    if a.write:
        (root / PIN).write_text(json.dumps(moved_pin(pin, head, date), indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"aec_sync: pin moved to {head[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
