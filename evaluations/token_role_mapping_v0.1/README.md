# Token role mapping v0.1: collection-wide claim diff (kb patch 4)

`claim_diff.csv` lists every `mtg_eval.semantic_patterns` capability claim that differs between KB release r20261028 (DB sha c7f01455…) and a rebuild from the same export (d7a2d191…) with kb patch 4. That is 102 rows:

- **38 new claims:** fixing 18, land_drop 10, ramp 7, token_maker 1, plus one new contradiction (Tokka & Rahzar: a hand label says not fixing).
- **63 claims that were Sheet tags only now have Oracle evidence:** fixing 22+5, token_maker 15+1, draw 10+1, ramp 8+1.
- **1 claim gained Oracle evidence without a status change:** Noggle Robber.
- **Lost claims:** none.

All of these are machine-derived candidates, and none is reviewed.

## Kate's acceptance criteria (2026-10-29)

| Requirement | Status |
|---|---|
| Gold Pan: fixing via Treasure | detected (`tests/test_role_classifier.py`) |
| Galactic Wayfarer: delayed ramp via Lander | detected |
| A token given to someone else is not self-ramp/fixing/draw | regression tests. Only the imperative "create" counts, so "its controller creates" (Zuko's Exile) and "target player creates" (Prismari Command) produce nothing |
| Clue gives draw; Food gives lifegain | mapped |
| Costs and restrictions kept | partly. The evidence span names the token, and the cost lives in the token's definition. A typed "available through a token" claim level is not built; it belongs to the DIO bridge |
| Collection-wide changes reported | this file |
| New claims stay machine-derived | yes (`machine_supported`, unreviewed) |

Map and Mutagen are left as they are. Map's explore does not feed an audited role, and Mutagen was already `counter_source`.
