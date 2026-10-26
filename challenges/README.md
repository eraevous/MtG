# Challenges

Unresolved objections, open tensions and known defects that must not disappear just because a task finished or a spec changed. One JSON object per line in `ledger.jsonl`, append only (CI-enforced).

Fields: `id` (C-NNN), `utc`, `raised_by`, `against` (contract, decision, file or doc), `claim`, `evidence`, `severity` (`info`, `minor`, `major`, `blocking`), `status` (`open`, `resolved`, `wont_fix`, `superseded`), `disposition`.

To change a challenge's status, append a new line with the same `id` and a `disposition`. Never edit the original line. Resolving a challenge requires an explicit disposition with a rationale. Challenges about design intent are resolved by Zach.
