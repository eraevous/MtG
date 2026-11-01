# Module: tools.aec_sync
> Checks whether upstream AEC moved past the pin, tests MtG's .aec records at the new commit, and moves the pin only when every check passes.

@ai-path: tools.aec_sync
@ai-source-file: tools/aec_sync.py
@ai-role: governance
@ai-intent: "Keep the AEC pin current without letting an untested AEC version into MtG."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-06, P-09

### Inputs and outputs
| Direction | What |
|---|---|
| In | tools/aec_upstream.json, the upstream repo's main (git ls-remote, clone), .aec/records.jsonl, .aec/scenarios/ |
| Out | A report (Markdown), GitHub Actions outputs, and with --write a moved pin. Exit 0 current or passed, 3 a check failed, 2 error |

### Risks, invariants and known gaps
- Never edits .aec/records.jsonl; a record-format change upstream shows up as a failing check and needs a person.
- Structural only: a pass means MtG's records still parse and resolve under the new AEC, not that the new AEC is better.
- Runs upstream code (AEC's CLI) from a public repo Zach owns. If that repo ever had another maintainer, this would be running their code in CI.
- Used by .github/workflows/aec-upstream.yml (D-0022).
