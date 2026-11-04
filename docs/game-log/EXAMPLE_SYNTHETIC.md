# SYNTHETIC EXAMPLE: not a real game

> **Everything on this page is made up** to show how the template is filled in. It is not an observed outcome. Do not copy it into `games.csv` and never score it. The deck name is real only so that the example matches the predictions file.

```
GAME   date 2099-01-01   pod 4 players (who: SYNTHETIC A, B, C)   ended turn 10
WON    SYNTHETIC B    HOW  stall
WIPE   turn 6  kind destroy all creatures

MY DECK Sharuum  version SYNTHETIC-v0
  stalled vs blockers?            y
  rebuilt within ~3 turns of wipe? n
  commander removed               2 times
  out of mana in midgame (T6+)?   -
  bodies spent on costs, not attacks?  y
  line: SYNTHETIC: illustrative free text only
```

The same block as a CSV row (`game_id` starts with `SYNTH`, so the scorer prints a "SYNTHETIC DATA" banner if one ever reaches it):

```csv
SYNTH-EX-1,2099-01-01,4,SYNTHETIC A B C,Sharuum,SYNTHETIC-v0,10,SYNTHETIC B,stall,y,6,destroy all creatures,n,2,,y,SYNTHETIC: illustrative free text only
```

The test fixture `tests/fixtures/game_log/games_synthetic.csv` is synthetic in the same way.
