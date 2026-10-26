# Held-out set: Star Trek (TRK + TRC), 2026-10-22

**What was frozen.** Before validation.py read any ruling, it froze the 419 generated contracts for every TRK and
TRC card. The freeze is `heldout_trk_trc_predictions.json`, sha256
`bc22d31b15e0d2ef0954507763d1c29ebf8fef22f33e2885c4f54b34446329ab`. I did not look at TRK card texts while I was
tuning the grammar.

**Contamination disclosure.** While I was writing the station and sneak claims, I read pooled ruling texts for
those mechanics. Those texts may have included TRK or MSH rulings. TRK turned out to have no station rulings at
all, so this did not affect anything below. It is still recorded here.

## What TRK's rulings actually test

Scryfall carries only 32 rulings for TRK + TRC. There are 10 distinct texts. Every one is a reprint ruling, for the
shocklands, Engineered Explosives, Refute and Reckless Impulse. Star Trek's own new mechanics ("strange new
worlds", "seek out") have no rulings yet. Wizards' release notes for the set cannot be fetched from here (see
REPORT §7). As a test of novel grammar, this held-out set is therefore weak.

I graded each ruling by hand against the frozen contract:

| # | Card(s) | Ruling, in short | Grade | Why |
|---|---|---|---|---|
| 1 | Refute | An illegal target means the spell doesn't resolve, so no draw or discard | **right** | The target is an eligibility group on `spell` in the stack. Counter, draw and discard are steps 1 to 3 of the same resolution. The fizzle itself is generic CR 608.2b, which no contract needs to restate. |
| 2 | Reckless Impulse | You still pay costs and follow timing permissions | **right, with a defect found** | The permission adds no cost waiver and no timing override, which agrees with the ruling. But "you may **play** those cards" was mapped to `op.permission.cast`. Play includes lands (CR 305.1), so that is wrong. |
| 3 | 10 shocklands | If an effect puts it onto the battlefield tapped, paying 2 life doesn't untap it | **insufficient representation, with a defect found** | The tapped entry is modelled only as the `if_not` branch of the land's own choice. Nothing represents "an entry status set by another effect". The frame `as <self> enters, you may pay <n> life` is partial, and the "may" was lost, so the life payment read as guaranteed. |
| 4–6 | shocklands (3 texts) | Two basic land types, but not basic | not a contract claim | Type-line facts. They live in `card.type_line`, not in ability contracts. They are correct there. |
| 7 | Engineered Explosives | Colorless mana adds no counter | insufficient representation | Sunburst is a keyword with no reminder text in Oracle, so no macro expansion exists for it. |
| 8 | Engineered Explosives | X in a permanent's mana cost is 0 | insufficient representation | Mana value is not modelled. |
| 9 | Engineered Explosives | Tokens that aren't copies have mana value 0 | no applicable contract | A general rule. |
| 10 | Engineered Explosives | You may choose any X | insufficient representation | The cast cost with X is not a contract field yet. |

**Score:** 2 right out of 10, 0 wrong claims, 5 insufficient representation, 3 not applicable to contracts. I found
two real grammar defects while checking (rows 2 and 3).

**Station on held-out cards.** The station tests derived from EOE rulings apply automatically to the 9 TRK/TRC
cards with station. All 63 of those tests pass. They exercise reminder-text expansion, sorcery timing, the
threshold striations and the tap-another-creature cost. That is the one place where the held-out set shows
reusable tests transferring to unseen cards.

## Fixed after the freeze (concepts 0.2.1, semantics 0.1.1)

- "play" permissions map to `op.permission.play`.
- A literal "you may" in a partly read frame marks the operation optional.

This changed 75 contracts across the corpus. The frozen file is untouched. Rerunning validation reuses it through
`--frozen` and never re-freezes after the rulings have been read.
