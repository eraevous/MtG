# Review policy (2026-10-22)

- `review_overlay.jsonl` holds human **semantic** reviews. Each one is a judgement that a contract says what the Oracle text says. Write lines only with `review.py add`. The file is append-only and hash-chained.
- A `verified` line must cite scenario ids from `scenarios/*.json`.
  - Each scenario must name the contract.
  - Each scenario must pass on the current contract version.
  - Labels, placeholders (`scenario:<name>`) and unknown ids are refused.
- A review never certifies runtime behaviour. Runtime certificates are issued by the build, only for a contract whose compile into the 0.3.0 engine action loses nothing and whose runtime scenario passes. The build records them in the DB table `runtime_certifications`.
- Quarantined contracts can't be verified. A contract is quarantined when its card has a material Sheet/Oracle discrepancy in `oracle_reconciliation.jsonl`.
- `oracle_reconciliation.jsonl` is append-only and hash-chained. It records targeted Sheet-vs-Oracle decisions. It never edits the Sheet.
- `verified_reviews.jsonl` is the empty v0.1 placeholder and is not read.
