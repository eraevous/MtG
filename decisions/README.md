# Decisions

An append-only record of **design decisions** (Kate's amendment, 2026-10-26). This is separate from KB contract reviews, which live in `kb/overrides/review_overlay.jsonl`.

A decision here is a card swap, the acceptance or rejection of an architectural thesis, a change to the success criteria, a scope change, or a change to a purpose contract. One JSON object per line in `decision_events.jsonl`:

| field | meaning |
|---|---|
| `id` | `D-NNNN` |
| `utc` | when it was decided |
| `kind` | `card_swap`, `thesis`, `criteria_revision`, `scope`, `purpose_contract`, `repo`, `dio_revision` (proposed, D-0020), plus kinds already used in the log: `design`, `interface`, `derivation`, `role_definition`, `process` |
| `subject` | deck, module or contract affected |
| `proposed_by` / `challenged_by` / `decided_by` | who proposed it, who challenged it, who decided it (`zach`, `kate`, `claude-build`, `claude-aec`) |
| `status` | `proposed`, `accepted`, `rejected`, `superseded` |
| `decision` | what was decided, in one or two sentences |
| `reason`, `evidence` | why it was decided, and pointers to files, threads or games |
| `supersedes` | the id of an earlier event this one replaces. Earlier events are never edited. |

Rules:
- **Append only.** CI runs `tools/drift_check.py --base origin/main` and fails if earlier lines change.
- **Only Zach accepts.** An agent can append `proposed` events. Moving a decision to `accepted` takes an event with `decided_by: zach`.
- **DIO revisions** (`kind: dio_revision`, proposed in D-0020) say which DIO files change, minor or major by DIO §13, and who accepted it (Zach; Kate jointly where Zach says so, as for A1–A7). The same PR appends a new `SRC-dio*` record version in `.aec/records.jsonl` and includes the `aec impact` output (`.aec/README.md`).
- **Mirror.** A decision that rests on the DIO may also appear as a `decision` record in `.aec/records.jsonl`. This log stays its home; `tools/drift_check.py` fails if the mirror's status disagrees.
- **Criteria revisions** (`kind: criteria_revision`) give the new criteria version a name and say what observation motivated it. A prediction is scored only against the criteria version frozen with it.

`criteria/` holds the versioned evaluation criteria those events refer to.
