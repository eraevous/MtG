# Game log: one game, two minutes

Copy the block below into a note on your phone after each game. Write one `MY DECK` block for each of your decks in the pod. Leave a box blank if it didn't come up or you didn't notice. Blank is never scored. `n` means you saw that it didn't happen.

```
GAME   date ____-__-__   pod __ players (who: ________)   ended turn __
WON    ________    HOW  close / stall / wipe-recover / commander removal / attrition / mana-screw
WIPE   turn __  kind ________        (blank = no wipe)

MY DECK ________  version ____
  stalled vs blockers?            y / n / -   (- = no blockers that mattered)
  rebuilt within ~3 turns of wipe? y / n / -   (- = no wipe)
  commander removed               __ times
  out of mana in midgame (T6+)?   y / n / -   (- = game ended earlier)
  bodies spent on costs, not attacks?  y / n / -
  line: ________________________________________
```

## Into the CSV

Each `MY DECK` block becomes one row of `docs/game-log/games.csv`. The game fields repeat on each row, and every row of the same game shares its `game_id` (use something like `2026-11-08-a`).

| column | from the note | values |
|---|---|---|
| `game_id` | your label | text; one per game |
| `date` | date | `YYYY-MM-DD` |
| `pod_size`, `pod` | pod | number; who played |
| `deck`, `deck_version` | MY DECK, version | deck name as in `predictions/PREDICTIONS_2026-10-20.md`; any version label (date of last change is fine) |
| `turns` | ended turn | number |
| `winner`, `how` | WON, HOW | text; one of the six words or blank |
| `stalled_vs_blockers` | stalled vs blockers | `y` / `n` / blank |
| `wipe_turn`, `wipe_kind` | WIPE | number or blank; text |
| `rebuilt_within_3` | rebuilt within ~3 turns | `y` / `n` / blank |
| `commander_removals` | commander removed | number |
| `ran_out_of_mana` | out of mana in midgame | `y` / `n` / blank |
| `bodies_on_costs` | bodies spent on costs | `y` / `n` / blank |
| `note` | line | free text (quote it if it has commas) |

The fields follow the "How to score" list in `predictions/PREDICTIONS_2026-10-20.md`. `rebuilt_within_3` uses the wording of the prediction lines. `how` and `note` are kept for you and are never scored.

## Scoring

```bash
python3 tools/score_predictions.py            # reads docs/game-log/games.csv
```

With no games it prints `0 games recorded; nothing scored`. Rules for each measure are in the docstring of `tools/score_predictions.py`. Four measures (close, recover, contention, mana) have a rule. Three (commander, attrition, quality) are reported as "rule not fixed" (C-025). Games dated on or before 2026-10-20 and Vraska games are never scored.

Only real games go in `games.csv`. See `EXAMPLE_SYNTHETIC.md` for a filled-in example, which is not a real game.
