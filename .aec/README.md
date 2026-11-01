# .aec: AEC reasoning records for MtG

Status: **accepted** (D-0021, Zach, 2026-11-01). Format: AEC v0.3 records, upstream `eraevous/AEC` pinned in `tools/aec_upstream.json`.

This directory puts the Deck Interaction Ontology (DIO) into AEC's records, so that a DIO revision can be checked for impact before anyone has to remember what rests on it. Why, and what was compared, is in `docs/aec/DIO_AEC_REVIEW.md`.

| File | What |
|---|---|
| `records.jsonl` | Append-only. Authorities by subject; the DIO, its addendum, A1–A7 and the Grammar Registry as `source` records with raw-byte SHA-256 anchors; P-00 to P-09 as provisional records; the decisions that rest on the DIO |
| `scenarios/` | Change events for `aec impact`: DIO v3.1.2 adopted without and with Zach's authorization |

**One home per fact** (DIO §2, §9; P-09). Purpose wording lives in `codex_++/project.purpose.md`. Decisions live in `decisions/decision_events.jsonl`; a `decision` record here only mirrors one that depends on the DIO, and `tools/drift_check.py` (`mirror`) fails if its status disagrees with the log. The edge snapshot is generated, never committed.

## Commands

```bash
git clone https://github.com/eraevous/AEC ../AEC && git -C ../AEC checkout $(python3 -c "import json;print(json.load(open('tools/aec_upstream.json'))['commit'])")
PYTHONPATH=../AEC/src python3 -m aec check .aec/records.jsonl                     # structural; prints each DIO anchor's state
PYTHONPATH=../AEC/src python3 -m aec impact .aec/records.jsonl .aec/scenarios/dio_v312_authorized.jsonl
PYTHONPATH=../AEC/src python3 -m aec source show SRC-dio@1 --max-lines 40          # quote the pinned DIO sections
python3 tools/drift_check.py                                                       # 'governed' and 'mirror' need no AEC checkout
```

## When the DIO changes

1. Zach accepts the revision: append a decision event of kind `dio_revision` to `decisions/decision_events.jsonl`.
2. Append `SRC-dio` version 2 here (new anchors with the new SHA-256, `"relations":[{"rel":"supersedes","to":"SRC-dio@1"}]`). Never edit version 1.
3. Run `aec impact` with a change event `{"change":"revise","target":"SRC-dio@1","new":"SRC-dio@2","authorized_by":"AU-zach",...}`. Each `rebaseline` item is something to re-examine against the new version; decisions go to Zach.
4. Append new versions of the dependents once they are re-examined.

A clean `aec check` or `drift_check` is a structural result. It does not show that the DIO is right, that a contract follows it, or that P-00 survived.
