# The grammar of the collection, v0.2 (2026-10-22)

This version follows Kate's critique of v0.1 and Zach's request for set-level and rulings validation. It covers:

- coordinated triggers and replacement composites;
- typed slot→qualifier binding, so that every ability compiles to a DIO §5 operation contract;
- a small representative review sample, plus a fresh blind semantic sample;
- collection discovery as its own use case;
- two validation layers: sets and Scryfall rulings, with a held-out set.

Everything is in `grammar_layer.sqlite`. The v0.1 database is in `archive/`.

**Headline numbers**

| Measure | Value |
|---|---|
| Collection abilities fully parsed into templates | 5,621 / 6,858 (**82.0%**) |
| Collection abilities expressible through *reviewed* templates | **0%**: nothing has been reviewed yet |
| Share that reviewing the top 300 templates would cover | 64.5% |
| Generated ability contracts | 6,858 collection, 8,637 including the validation sets |
| Blind sample, seed 4471, 50 abilities: whole contract right | **68%**; structure right 92% |
| Agreement with the earlier contract drafter | trigger hooks 95.6%, result hooks 94.9% |
| Rulings regression tests | 41 claims, 733 test runs on 169 abilities of 184 cards (56 owned); 0 contradictions left |
| Collection loop candidates | 2,125 (11 guaranteed, 46 optional, 153 conditional, 1,915 possible) |

Source: Scryfall Oracle bulk 2026-10-21, and Scryfall rulings bulk 2026-10-21 (79,706 lines, sha256 409a959c…).
Versions: grammar 0.2.0, concepts 0.2.1, semantics 0.1.1, validation 0.1.0. Numbers come from `metrics.json`,
`discovery/discovery_summary.json`, `validation/validation_run.json` and `validation/per_set_summary.json`.

## 1. Kate's corrections

**Coordinated events.** "Enter or attack" and "enter or die" are now one trigger requirement group with
alternatives (DIO §5.1). The subject is shared. A bare second verb shares the object only when that verb is
transitive.

- frame 514 `whenever <self> enter or attack` → `TRIGGER any of [battlefield.enter | attacker.declared]`
- `whenever <self> enter or die` → `any of [battlefield.enter | permanent.dies]`

The combined concepts from v0.1 (`ev.enter_or_attack` and the like) are gone.

**Replacement composites.** "If X would die, exile it instead" is one operation of kind `replacement`, with
`rewrites {proposed: permanent.dies, resulting: exile.enter, mode: substitute}`. It is no longer two independent
edges. The modes are substitute, modify and prevent (§5.4).

**Typed slots.** Each slot occurrence binds to DIO §4.1 qualifiers plus the addendum names:

- object type, subtype and supertype, with `type_logic: any_of` for "creature or Vehicle";
- controller, owner and `relation_to_observer`;
- `exclude_self` for "another";
- cardinality (`each_object` or `one_or_more`) and `simultaneity_group`;
- token or nontoken, counters, status, zone and zone owner;
- the mana mode;
- `act_time` (paid_as_cost, on_resolution or continuous) and certainty (guaranteed, optional or conditional).

A token's granted ability takes its host as `source_unit`. That is the drafter bug from v0.1, and it is not
repeated here. A part the grammar cannot read stays in the contract as `unread`. It is never dropped.

**Review unit.** The unit of review is the whole frame semantics, not single edges. Verdicts are keyed to
frame_sha plus semantics_sha, so they go stale when either changes. Frame ids are not stable across builds, but
the shas are.

`review/template_review_sample.csv` has **74 rows**: about four per mechanical class over 21 classes. It
includes every addendum-dependent class and the unmapped residue, so none of them can be approved wholesale. The
top-300 and full collection files are still there for later.

## 2. Is it right? The blind sample

I drew 50 owned abilities with an untouched seed and graded each whole contract against Oracle and the rules.
Details are in `validation/blind_sample_seed4471.md`.

| Grade | n |
|---|---|
| Correct (hooks, roles, composition and every material qualifier) | 34 |
| Minor (one qualifier missing or wrong) | 12 |
| Wrong (hook, role or component) | 4 |

The four wrong ones were fixed after grading: choose target, the return-to-battlefield hook, the choice's legal
set, and the recipient of "is dealt damage". Ten of the twelve minor ones were fixed too. A regrade comes out at
47/3/0, but it is contaminated by the fixes, so **the next blind sample needs a new seed**. Named predefined
tokens (Heartwood, Mutagen, Cadet) are still open.

## 3. Collection discovery

`discovery.py` summarises each owned ability as three lists:

- **produces:** events from its results and from its paid costs;
- **observes:** its trigger;
- **needs:** its non-mana costs.

It links producers to observers on hook, type, subtype, token, controller, actor, counter kind, destination and
self-reference.

This answers Kate's query: card A produces an event that card B observes, and B's output re-enables A. The result
is **117,302 flow edges and 2,125 two-card loops**, in `discovery/collection_loops.csv`. Certainty is never higher
than the weakest link. An ability with any unread part only yields "possible". Spells can't close a loop.

The strongest candidates include:

- Drowned Rusalka ↔ Cryptcaller Chariot
- Cauldron of Essence / Necrosavant / Sephiroth ↔ Wingmantle Chaplain
- Bard the Bowman / Lakeshore Apothecary ↔ Cloaked Cadet
- Genghis Frog ↔ Salvation Swan
- Rat King with sacrifice outlets

These are candidates for judgement, not verified combos. 1,915 of the loops are "possible" only.

## 4. Set-level layer

Each fetched set is stored complete. Commander products are fetched as their own sets.

| Set | Role | Cards | Owned | Introduced (by first-seen date) |
|---|---|---|---|---|
| TLA Avatar | training | 286 | 181 | earthbend, firebending, airbend |
| TLE Avatar Eternal | training | 242 | 23 | (reprints of the same) |
| EOE Edge of Eternities | training | 266 | 153 | warp, station, void |
| EOC EOE Commander | training | 171 | 54 | station |
| TMT TMNT | training | 195 | 135 | sneak, disappear |
| TMC TMNT Eternal | training | 117 | 82 | |
| TRK Star Trek | **held out** | 159 | 11 | strange new worlds |
| TRC Star Trek Commander | **held out** | 53 | 1 | strange new worlds, seek out |

MSH (Marvel Super Heroes) is fetched but not yet evaluated.

`mechanic_family` records, per set, every keyword and keyword action as introduced or returning. It also records
the grammatical variants of each one (the templates, how complete they are, and how many abilities use them).

Release notes from Wizards, meaning both the general mechanic definitions and the card clarifications, are not
linked yet. See §7.

## 5. Rulings layer

**Ingestion.** One bulk download replaces per-card API calls. Each ruling is stored under its oracle_id with
its source, publication date, bulk file name and sha, and ingest time. The ruling_sha is computed over oracle_id,
source, date and text, and identical rulings are deduplicated (43 were). A rerun skips anything already there.

**Claims.** Claims are specific, typed assertions, never text similarity:

- trigger, cost or not-cost, targeting, timing;
- macro expansion read from the printed reminder text;
- zone return, entry status, counter thresholds;
- mana ability or not;
- once per turn.

Curated claims are tied to the exact ruling. The rest come from six generic patterns. Every claim is
`proposed`, and nothing is promoted to verified.

**Tests attach to a construction or mechanic**, so one ruling tests every card that uses it:

| Mechanic | Claims | Test runs | Cards | Owned | Result |
|---|---|---|---|---|---|
| earthbend | 9 | 288 | 36 | 15 | all pass |
| station | 9 | 282 | 40 | 13 | 280 pass, 2 not representable (last-known power, negative power) |
| sneak | 4 | 144 | 90 | 22 | all pass |
| generic patterns (6 kinds) | 19 | 19 | 19 | 6 | 13 pass, 5 ambiguous, 1 not representable |

Totals: **41 reusable claims, 733 test runs, 163 distinct templates exercised, 184 cards affected, 56 of them
owned.** Per-claim detail is in `validation/claims_and_tests.csv`. Per-set detail is in
`validation/per_set_summary.json`.

**Disagreement report.** `validation/disagreements.csv` covers the 2,522 rulings on cards in these sets:

| Status | n |
|---|---|
| confirmed | 22 |
| contradiction | **0** (11 in the first run) |
| insufficient representation | 2 |
| ambiguous | 5 |
| not converted into any claim | 2,493 |
| flagged potentially outdated (pre-2024-11-08 terminology) | 18 |

The first run's 11 contradictions were real findings. Five were grammar gaps:

- the station striations;
- "Station only" as a restriction;
- "put … counters equal to";
- the counter threshold;
- the declare-blockers step.

Two were extraction errors in a generic pattern, and the rest were coarse per-frame judging of coordinated
triggers. All are fixed.

**An unconverted ruling is not a confirmation.** The 2,493 unconverted rulings are the work queue for the next
claims, not evidence that anything is right.

## 6. Held-out set (Star Trek)

Contracts for TRK and TRC were frozen (sha256 `bc22d31b…`, 419 contracts) before any ruling was read. Results are
in `validation/heldout_trk.md`.

TRK's rulings turned out to be all reprint rulings: shocklands, Engineered Explosives, Refute and Reckless Impulse.
Star Trek's new mechanics have none yet, so it is a weak test.

- **Of 10 distinct rulings:** 2 right, 0 wrong claims, 5 insufficient representation, 3 not contract claims.
- **Two real defects found:** "play" had been mapped to cast permission, and a "you may" in a partly read frame
  was lost. Both are fixed after the freeze, which changed 75 contracts.
- **Station transfers:** the station tests built from EOE rulings ran on the 9 held-out station cards, and all 63
  pass.

Disclosure: while writing the station and sneak claims, I glimpsed pooled ruling texts that may have included TRK
or MSH rulings.

## 7. Blocked, open and not done

- **Wizards hosts are blocked.** magic.wizards.com and media.wizards.com return 403 from this environment. That
  means the release notes, the mechanic articles and the Comprehensive Rules text can't be fetched. CR citations
  are from knowledge, not fetched text. Adding those two domains to the environment's network allowlist unblocks
  release-note linking and a CR-text authority table.
- **Not representable yet:**
  - named predefined tokens;
  - `evaluation_time` on amplifiers (last-known information);
  - the sneak entry status, which is carried but not modelled as an attacking state;
  - an entry status imposed by another effect (the shockland ruling);
  - mana value and X;
  - type-line facts in contracts.
- **The remaining parse gap:** 1,237 owned abilities are partial or unparsed. They are mostly long replacements,
  unusual noun phrases and the newest mechanics.
- **Untouched, by design:** the Google Sheet, the KB and its review overlay, and the SQLite thread's P0, A1–A7 and
  release work. 261 concepts are `addendum_pending`, nearly all of them keyword macros. A1–A7 decides those.

## 8. Next

1. **Zach reviews `review/template_review_sample.csv`** (74 rows, the whole frame semantics per row), then
   applies it with `review.py apply`. That is the first non-zero reading of the headline metric. It also shows
   whether the per-row semantics are inspectable enough to move on to the top 300.
2. Draw a new blind sample with a new seed after the review.
3. Write claims for the 2,493 unconverted rulings in impact order: first the generic patterns that reach many
   cards, then the curated claims for the rest.
4. Fetch Wizards release notes and the CR once the hosts are allowed, then evaluate MSH as a second held-out set.
