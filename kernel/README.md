# Semantic kernel v0.2.1e + invariant suite v0.2.1d

Regression material from the 2026-10-15/16 kernel work, imported from the build project (`mechanics-kernel/real-decks/kernel_v0_2_1e/` and `mechanics-kernel/invariants_v021d.py`). It is **not** part of the KB release: the KB (`kb/`) and the grammar layer (`grammar/`) superseded this kernel as the mechanics path.

What the invariants check (seeded, 3,000 trials, no dependencies): unique object ids, unrelated events never change counts, information loss never yields certainty, equivalent descriptions agree, and projection keeps the facts needed downstream. Together these are the P-02 property "information loss must never yield certainty".

Run: `python3 kernel/invariants_v021d.py kernel/semantic_v0_2_1e [trials]`. `tests/test_kernel_invariants.py` runs it in CI and fails on any family not listed as known.

Current result: one known violation. M6b: re-projecting one resolution with default ids double-counts, 1 case in 3,000. It is tracked as C-009.

| file | sha256 |
|---|---|
| invariants_v021d.py | 24139a110c026ccc746ba74cdd9bc42c96055ef49808884406f65e95dcc28767 |
| semantic_v0_2_1e/mtg_semantic_kernel_v0_2_1.py | f284c64a0ddc5ef1573ee5446cf51ec7539b113657e0c87dafd3243804af167c |
| semantic_v0_2_1e/result_projection_v0_2_1b.py | 7e7f81497a90df9017ad2672b4e4ef5d54dd9c12780ddc1d9ba30b2acc303b5b |
| semantic_v0_2_1e/semantic_expression_v0_2_1.py | c2fe1322ffe6bf44c0ddb8e78b003f5a39e102bbbd05d20343e2a203ace871c0 |
