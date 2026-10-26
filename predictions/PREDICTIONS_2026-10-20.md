# Pre-game predictions, frozen 2026-10-20T16:09:35Z

mtg_eval 0.3.0; export `828a8970b459…`; 500 engine games per scenario; seed 20261018.
**sha256 of the JSON file:** `18657701bdba2bdc5beb60b4bd66632396b0e55c99fd8bed9bed80fa9bce589c`

Every line below is a **pre-game model inference**. Outcomes are **observed** only when Zach reports a game; explanations written after that are **post-hoc hypotheses** and are not scored.
Rule fixed before outcomes: bottom third (ranks 9-12 of 12) predicts the weakness; top third (ranks 1-4) predicts the strength; ties share the better rank; a measure on which 4 or more decks share the same value makes no prediction for those decks (it does not separate them). Vraska is excluded from scoring because its game shaped these checks.

## Measurements

| deck | close | recover | commander | contention | quality | attrition | mana | unopposed lethal by T10 | tokens/turn | engine coverage |
|---|---|---|---|---|---|---|---|---|---|---|
| Ashling | 2.0 | 1.143 | 0.0 | 0.0 | 2.5 | 0.429 | 0.592 | 0.806 | 0.14 | 14/63 |
| Blight Curse | 0.0 | 1.286 | 0.0 | 0.0 | 3.25 | 0.571 | 0.801 | 0.81 | 0.04 | 6/61 |
| Brigid | 7.0 | 0.778 | 0.0 | 0.021 | 2.4 | 0.667 | 0.587 | 0.956 | 0.28 | 8/65 |
| Counter Blitz | 2.0 | 0.875 | 0.0 | 0.0 | 2.33 | 0.5 | 0.514 | 0.84 | 0.18 | 8/63 |
| Dina | 5.0 | 0.857 | 0.0 | 0.0 | 1.83 | 0.571 | 0.626 | 0.856 | 0.32 | 12/63 |
| Limit Break | 3.0 | 1.0 | -1.0 | 0.0 | 3.0 | 0.667 | 0.514 | 0.854 | 1.42 | 4/63 |
| Necrobloom | 0.0 | 1.2 | 0.0 | 0.011 | 1.67 | 0.8 | 0.628 | 0.584 | 0.42 | 4/60 |
| Rootha | 3.0 | 1.0 | 0.0 | 0.0 | 2.67 | 0.429 | 0.7 | 0.736 | 0.37 | 10/64 |
| Shanid | 8.0 | 1.143 | -4.0 | 0.034 | 2.67 | 0.714 | 0.571 | 0.844 | 0.06 | 8/64 |
| Sharuum | 12.0 | 1.286 | -7.0 | 0.144 | 3.25 | 0.857 | 0.763 | 0.736 | 0.18 | 20/63 |
| TMNT | 13.0 | 0.636 | -8.0 | 0.0 | 2.5 | 0.273 | 0.565 | 0.956 | 0.28 | 12/61 |
| Vraska | 27.0 | 0.9 | -17.0 | 0.176 | 1.89 | 0.4 | 0.359 | 0.938 | 2.21 | 31/64 |

Measures: **close** = median damage by T10 against light blockers; **recover** = board power 3 turns after a T6 destroy wipe, as a share of power before; **commander** = median paired change in damage by T10 without the commander (negative = depends on it); **contention** = share of turns T5-T8 where bodies were spent before combat or a station waited for bodies; **quality** = median power per body at the end of T8 (added after hearing the Vraska account); **attrition** = board power 3 turns after a T6 wipe followed by three more commander removals, as a share of power before; **mana** = share of turns T6-T8 with spells waiting for mana

## Predictions by deck

### Ashling — confidence medium
- Weakness (close, rank 9 of 12): struggles to close once opponents have blockers; games go long or stall
- Strength (recover, rank 4 of 12): rebuilds quickly after a board wipe
- Weakness (attrition, rank 9 of 12): a wipe followed by repeated commander removal leaves it without a board

### Blight Curse — confidence low
- Weakness (close, rank 11 of 12): struggles to close once opponents have blockers; games go long or stall
- Strength (recover, rank 1 of 12): rebuilds quickly after a board wipe
- Strength (quality, rank 1 of 12): its bodies outclass ordinary blockers
- Weakness (mana, rank 12 of 12): mana-limited in the midgame; spells stay in hand

### Brigid — confidence low
- Weakness (recover, rank 11 of 12): after a board wipe, does not rebuild a threatening board within about three turns
- Weakness (contention, rank 9 of 12): several cards compete for the same bodies; spends creatures on costs instead of attacks
- Strength (attrition, rank 4 of 12): keeps a board through a wipe and repeated commander removal

### Counter Blitz — confidence low
- Weakness (close, rank 9 of 12): struggles to close once opponents have blockers; games go long or stall
- Weakness (recover, rank 9 of 12): after a board wipe, does not rebuild a threatening board within about three turns
- Weakness (quality, rank 9 of 12): its bodies are small; blockers and incidental removal outclass the board
- Strength (mana, rank 2 of 12): rarely short of mana in the midgame

### Dina — confidence medium
- Weakness (recover, rank 10 of 12): after a board wipe, does not rebuild a threatening board within about three turns
- Weakness (quality, rank 11 of 12): its bodies are small; blockers and incidental removal outclass the board

### Limit Break — confidence low
- Strength (quality, rank 3 of 12): its bodies outclass ordinary blockers
- Strength (attrition, rank 4 of 12): keeps a board through a wipe and repeated commander removal
- Strength (mana, rank 2 of 12): rarely short of mana in the midgame

### Necrobloom — confidence low
- Weakness (close, rank 11 of 12): struggles to close once opponents have blockers; games go long or stall
- Strength (recover, rank 3 of 12): rebuilds quickly after a board wipe
- Weakness (quality, rank 12 of 12): its bodies are small; blockers and incidental removal outclass the board
- Strength (attrition, rank 2 of 12): keeps a board through a wipe and repeated commander removal
- Weakness (mana, rank 9 of 12): mana-limited in the midgame; spells stay in hand

### Rootha — confidence medium
- Strength (quality, rank 4 of 12): its bodies outclass ordinary blockers
- Weakness (attrition, rank 9 of 12): a wipe followed by repeated commander removal leaves it without a board
- Weakness (mana, rank 10 of 12): mana-limited in the midgame; spells stay in hand

### Shanid — confidence low
- Strength (close, rank 4 of 12): pressures life totals through blockers
- Strength (recover, rank 4 of 12): rebuilds quickly after a board wipe
- Weakness (commander, rank 9 of 12): repeated commander removal hurts badly; the deck runs through its commander
- Weakness (contention, rank 10 of 12): several cards compete for the same bodies; spends creatures on costs instead of attacks
- Strength (quality, rank 4 of 12): its bodies outclass ordinary blockers
- Strength (attrition, rank 3 of 12): keeps a board through a wipe and repeated commander removal

### Sharuum — confidence medium
- Strength (close, rank 3 of 12): pressures life totals through blockers
- Strength (recover, rank 1 of 12): rebuilds quickly after a board wipe
- Weakness (commander, rank 10 of 12): repeated commander removal hurts badly; the deck runs through its commander
- Weakness (contention, rank 11 of 12): several cards compete for the same bodies; spends creatures on costs instead of attacks
- Strength (quality, rank 1 of 12): its bodies outclass ordinary blockers
- Strength (attrition, rank 1 of 12): keeps a board through a wipe and repeated commander removal
- Weakness (mana, rank 11 of 12): mana-limited in the midgame; spells stay in hand

### TMNT — confidence medium
- Strength (close, rank 2 of 12): pressures life totals through blockers
- Weakness (recover, rank 12 of 12): after a board wipe, does not rebuild a threatening board within about three turns
- Weakness (commander, rank 11 of 12): repeated commander removal hurts badly; the deck runs through its commander
- Weakness (attrition, rank 12 of 12): a wipe followed by repeated commander removal leaves it without a board
- Strength (mana, rank 4 of 12): rarely short of mana in the midgame

### Vraska (not scored) — confidence higher
- Strength (close, rank 1 of 12): pressures life totals through blockers
- Weakness (commander, rank 12 of 12): repeated commander removal hurts badly; the deck runs through its commander
- Weakness (contention, rank 12 of 12): several cards compete for the same bodies; spends creatures on costs instead of attacks
- Weakness (quality, rank 10 of 12): its bodies are small; blockers and incidental removal outclass the board
- Weakness (attrition, rank 11 of 12): a wipe followed by repeated commander removal leaves it without a board
- Strength (mana, rank 1 of 12): rarely short of mana in the midgame

## How to score

For each game, note: deck, pod size, result, turn it ended, and which of these happened: a board wipe (turn, kind), commander removed (how many times), stalled against blockers, ran out of mana, bodies spent on costs instead of attacks. A prediction is **supported** if its condition arose and the deck showed the predicted behaviour, **contradicted** if the condition arose and it did not, and **untested** if the condition never arose.
