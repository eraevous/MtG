# .aec: AEC reasoning records for MtG

Status: **accepted** (D-0021, Zach, 2026-11-01). Format: AEC v0.3 records, upstream `eraevous/Telosmith` (formerly `eraevous/AEC`; moved 2026-11-05, DEC-095) pinned by commit in `tools/aec_upstream.json`. CI also runs Telosmith's `code-impact` (report-only, job summary) and `.claude/settings.json` runs its hook beside `tools/drift_check.py`; both report, neither blocks an edit.

This directory puts the Deck Interaction Ontology (DIO) into AEC's records, so that a DIO revision can be checked for impact before anyone has to remember what rests on it. Why, and what was compared, is in `docs/aec/DIO_AEC_REVIEW.md`.

| File | What |
|---|---|
| `records.jsonl` | Append-only. Authorities by subject; the DIO, its addendum, A1–A7 and the Grammar Registry as `source` records with raw-byte SHA-256 anchors; P-00 to P-09 as provisional records; the decisions that rest on the DIO |
| `scenarios/` | Change events for `aec impact`: DIO v3.1.2 adopted without and with Zach's authorization |

**One home per fact** (DIO §2, §9; P-09). Purpose wording lives in `codex_++/project.purpose.md`. Decisions live in `decisions/decision_events.jsonl`; a `decision` record here only mirrors one that depends on the DIO, and `tools/drift_check.py` (`mirror`) fails if its status disagrees with the log. The edge snapshot is generated, never committed.

## Commands

```bash
pip install "git+https://github.com/eraevous/Telosmith.git@$(python3 -c "import json;print(json.load(open('tools/aec_upstream.json'))['commit'])")"   # the editor hook needs exactly this install (below); for CLI use, PYTHONPATH=../Telosmith/src at that commit also works
python3 -m aec edges . -o .aec/edges.jsonl && python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl   # structural; prints each DIO anchor's state, fails on dangling code: links
python3 -m aec impact .aec/records.jsonl .aec/scenarios/dio_v312_authorized.jsonl
python3 -m aec source show SRC-dio@1 --max-lines 40          # quote the pinned DIO sections
python3 tools/drift_check.py                                                       # 'governed' and 'mirror' need no AEC checkout
```

## The editor hook (one line, since 2026-11-20)

`.claude/settings.json` runs Telosmith's hook through the one-line launcher from `aec init --hook-style line` (HO-AEC-20261117-DBN5, Telosmith propagation step D). The hook body (`aec hook project`: symlink refusal, edges refresh, `aec check`, `code-impact`) lives in the installed package, so a Telosmith fix reaches this repo by moving the pin, not by editing the settings file.

- **It runs only the aec pinned here.** Before any aec code runs, the launcher reads `commit` from `tools/aec_upstream.json` and accepts only a non-editable `pip install git+…@<that commit>` outside this repo. A `pip install --user` works too (Telosmith#99). A source checkout on `PYTHONPATH`, an editable install, another commit or no install exits 1 with one line saying which and the install command; for another commit the line names both the pinned and the installed commit. **Not supported, on purpose:** a source checkout or editable install, which the old inline hook did run. Exit codes otherwise match the old inline hook (0 clean, 2 records problem or symlink refusal).
- **Moving the pin moves the hook.** After a pin PR from `aec-upstream.yml` merges, reinstall with the command above or the hook refuses until you do.
- **Rollback:** revert the PR that installed the line (it restores the hook and the pin together), or, with Telosmith installed at the pinned commit (b91f78b or later), run `aec init --hooks --hook-style inline` in an empty directory and copy the second hook entry of its `.aec/snippets/claude-settings.json` back over this one.

## Keeping AEC current (D-0022)

MtG runs AEC only at the commit pinned in `tools/aec_upstream.json`. Every Monday, `.github/workflows/aec-upstream.yml` runs `tools/aec_sync.py`. It asks whether upstream `main` has moved; if so, it clones the new head and runs `aec check` and every scenario here. If all pass, it opens a PR that moves the pin, with the upstream commit list and the check results, and runs CI on it. If any fail, it opens or updates an issue with the output instead. Nothing merges by itself, and merging the PR is the decision to adopt that AEC version. You can run it any time from the Actions tab (Run workflow) or by hand:

```bash
python3 tools/aec_sync.py                  # is the pin current?
python3 tools/aec_sync.py --test           # test MtG's records at the upstream head
python3 tools/aec_sync.py --test --write   # and move the pin if everything passes
```

## When the DIO changes

1. Zach accepts the revision: append a decision event of kind `dio_revision` to `decisions/decision_events.jsonl`.
2. Append `SRC-dio` version 2 here (new anchors with the new SHA-256, `"relations":[{"rel":"supersedes","to":"SRC-dio@1"}]`). Never edit version 1.
3. Run `aec impact` with a change event `{"change":"revise","target":"SRC-dio@1","new":"SRC-dio@2","authorized_by":"AU-zach",...}`. Each `rebaseline` item is something to re-examine against the new version; decisions go to Zach.
4. Append new versions of the dependents once they are re-examined.

A clean `aec check` or `drift_check` is a structural result. It does not show that the DIO is right, that a contract follows it, or that P-00 survived.

### Updater execution boundary

The updater separates trusted planning, disposable candidate checks, and fresh publication
jobs. Candidate Python runs without network, credentials, a writable checkout, or access
to the publisher. Publication reconstructs only `tools/aec_upstream.json` from the trusted
base and planned full SHA. Candidate output is retained in the linked Actions run, never
imported as a patch or instructions. A pass is untrusted compatibility evidence, not an
independent security review; bump PRs remain drafts for review. A moved main fails closed
and requires a rerun. Existing candidate branches are never overwritten automatically.
