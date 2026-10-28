# Incremental tool value: paired run of Kate's blind packet v0.1

- **Packet:** "MTG Incremental Tool Value — Blind Prompt Packet v0.1", sha256 `4ed1b6bc4f9c7311d3148d44c25baa5b245d82d630c5dc0fa617b68bccaa8a2f`. It contains no answer key.
- **Frozen system:** mtgtools at `db8bd45` (0.2.0), KB `mtg-kb-v0.2.1-r20261024d`, inventory snapshot `d7a2d191…4bab4`, and `decks/collection_policy.json` as of `db8bd45`. The 0.2.1 fixes (`60dda57`) were not used.
- **Arms:** one arm allowed only `context` and `card`, which the harness enforced with a "not available" error for the other verbs. The other arm allowed all six verbs. The arms are labelled **P** and **Q**, and the mapping is held back from the adjudicator. Blinding is imperfect: a transcript can show a "not available" error.
- **Procedure:**
  - Each of the 16 runs used a fresh-context agent with one question, the same model and the same instructions.
  - No agent saw the tool source, the other arm, earlier runs or the Terra material.
  - The two arms of each case were launched together, with the order randomised per case.
  - The instructions are in `INSTRUCTIONS.md`.
- **Deviations:**
  - Each run's tool budget was uncapped.
  - Some agents batched many CLI calls inside one shell step, so "raw tool outputs saved" is the better count of calls (`RUN_METRICS.md`).
  - One agent left two helper files outside its output folder.
  - One agent printed 12 repeat `card` calls without saving them.
- **Files:** one transcript per case and arm (`P/H0n.md`, `Q/H0n.md`). The raw tool outputs (about 4.6 MB) are kept off-repo and available on request.
- **Not scored here.** Adjudication is Kate's, or an independent reviewer's, against Oracle and rules plus snapshot evidence.
