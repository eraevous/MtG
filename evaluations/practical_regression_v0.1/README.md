# Practical-question regression corpus v0.1 (frozen 2026-11-01)

These are the ten everyday questions from the first practical run (mtgtools 0.3.0, KB r20261031). The builder chose and graded them, so per Kate (2026-11-01) they are regression cases, not held-out evidence. The next blind test uses real questions from Zach and Steph.

| # | Question | Verb | 0.3.0 behavior | Expected now | Test |
|---|---|---|---|---|---|
| 1 | Where are my Sol Rings / Swords to Plowshares, can I use them? | `card` | correct tiers | unchanged | `test_card_reports_availability_under_the_policy` |
| 2 | Do I own Cyclonic Rift / Ashnod's Altar? | `card` | "not found" implied a later acquisition | says not owned, acquired later or misspelt: the KB can't tell | `Find.test_missing_card_is_not_assumed_acquired` |
| 3 | What is Sharuum weakest at, which free cards fix it? | `mtg_eval upgrades` | useful; Amalia counted as a wipe; cuts Sharuum's own cheap artifacts | open: C-012 role patterns; the evaluator does not price what a cut loses | none yet (evaluator is vendored) |
| 4 | Selfcraft Mechan → Swift Demise in Sharuum? | `compare` | descriptive profile | unchanged | none |
| 5 | Free black sacrifice package | `explore sacrifice_conversion`, `find --role sacrifice` | cost-paid outlets invisible | outlets link; `find` lists outlets apart from payoffs | `test_sacrifice_outlet_links_to_aristocrat`, `Find.test_payoffs_are_listed_apart_from_outlets` |
| 6 | Viscera Seer + Blood Artist? | `hypothesis` | no link; false acts_on | compatible sacrifice → dies link; no acts_on; not a loop | `test_sacrifice_outlet_links_to_aristocrat`, `test_a_player_target_never_acts_on_a_card` |
| 7 | Cirith Ungol Patrol + Wolfbat a loop? | `hypothesis` | listed as a loop | `once_only` (finality counter) | `test_a_finality_counter_ends_a_loop_after_one_pass` |
| 8 | What connects to Sharuum's enter trigger? | `explore` | land drops linked to "Sharuum enters" | self-only: blink and copy routes | `test_a_legendary_card_named_by_its_short_name_is_self` |
| 9 | Can I build Elves? | `typal Elf --free` | correct census | unchanged | typal tests |
| 10 | Check "Sol Ring is free" | `check` | CONTRADICTED, decision grade | unchanged | check tests |

Negative controls Kate asked for that still need a test: Amalia's conditional wipe in the evaluator (C-012), and Sharuum's cheap artifacts as cuts (the evaluator must price what a cut loses).
