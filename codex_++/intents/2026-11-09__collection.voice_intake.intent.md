# Inventory-first intake (2026-11-09)

Zach asked that intakes of any kind check highly likely existing-inventory matches before external calls, and use batch APIs otherwise. Existing voice intake already batches 75 identifiers; extend that resolver instead of creating a parallel matching authority. Transcript and structured CSV capture share the same path. The bring-your-own importer does no network lookup during import; its explicit enrichment step already skips populated data and batches names.

## Trade-offs and dissent review

- P-05 risk: a stale inventory could be mistaken for current ownership. Countermeasure: read-only identity hints, source-text hash, unverified freshness, no quantity/allocation inference. Only the canonical Sheet can establish current custody.
- P-02 risk: a familiar card name could choose the wrong physical printing. Countermeasure: do not borrow set/number, finish, language, ID or URL from an existing copy; match supplied metadata only. Reconciliation flags missing printing identifiers. Existing external resolver semantics remain unchanged.
- Name normalization is allowed only when unique; conflicting normalized identities fall through. Local front-face aliases and ambiguous leading quantity words deliberately require external resolution because a partial inventory cannot establish global uniqueness.
- A supplied inventory is explicit and read-only, not automatically discovered from stale files or hard-coded Sheet IDs. Missing inventory retains compatibility with API-only mode and is visible as null in the report. Intake orchestration must provide the chosen inventory snapshot.
- Structured capture is an adapter into the existing resolver, not photo recognition or an inventory writer. No change to DIO, KB, mechanics, custody or protected allocations. All fixtures are synthetic.

## Checks

Regression tests cover local-only request counts, misses-only batching, duplicate physical rows, ambiguous names and two-face identities, source privacy, absent printing details, stale/zero-quantity identity hints, finish/language capture, no mutation or input/output path aliasing, malformed CSV and fuzzy deduplication. Fresh review identified an output-path collision risk and a language handoff gap; both are fixed with focused regressions. Run repository-required unit, grammar and drift checks before delivery. Real-network and phone latency remain unmeasured.

## Final local validation

213 unit tests ran: 174 passed, 39 skipped because KB data is unavailable. Grammar: 11 passed. Focused intake: 50 passed. Drift check against main 6320974 and whitespace check passed. Pinned Telosmith b0e202f structural check: zero errors/warnings; both existing DIO scenarios completed, and fresh code-impact reported zero affected records. Fresh-context review verified both corrective regressions and found no remaining blocker in the reviewed changes. No real-network calls or live inventory changes were made.
