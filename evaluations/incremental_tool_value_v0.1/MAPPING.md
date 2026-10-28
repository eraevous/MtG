# Arm assignment (revealed 2026-10-28, after Kate's blind adjudication)

- **P** = full mtgtools 0.2.0 (db8bd45): all six verbs (context, card, explore, hypothesis, compare, check).
- **Q** = same build, CLI restricted to `card` and `context` only.

Each case ran one fresh agent per arm; seed order per case was randomized.

`raw/` holds the unedited tool outputs (paths sanitized) that Kate asked for in her audit:
H01/P (Brigid, Conjurer's Closet, Teleportation Circle), H02/P (sacrifice and landfall paths),
H04/P (Fireweaver hints), H05/P (both chains), H08/P and H08/Q (the `context --deck` role
summaries behind the Golden Argosy "only board wipe" claim).
