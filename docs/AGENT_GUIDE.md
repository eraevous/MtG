# Agent guide: card, deck and interaction questions

Read this before you analyse any card, deck, swap or interaction in this repo. It applies to every agent (Claude Code, Codex, ChatGPT with the repo). `AGENTS.md` covers how to change the repo; this file covers how to answer MTG questions with it.

**Why this exists.** On 2026-10-30 a blind Codex thread evaluated new cards using the purpose docs, the inventory and the evaluator. It never opened the DIO (Deck Interaction Ontology) and found no KB database, so its interaction analysis was its own reading of Oracle text. Nothing told it otherwise. The project exists to make interactions discoverable *through the ontology* (P-00, VISION "Why the ontology came first"), so an answer that skips it misses the point even when every sentence in it is true.

## 1. Preflight: what can you ground on?

```bash
python3 tools/kb_bootstrap.py status
```

| Level | Means | Do |
|---|---|---|
| `kb_grounded` | The KB database is the release this checkout pins. `mtgtools` reads DIO candidate contracts. | Go on. |
| `kb_unpinned` | A KB is present but it is a different release. | Go on, and cite the release `mtgtools` reports. |
| `doctrine_only` | No KB database. | Run `python3 tools/kb_bootstrap.py install`. It looks for the pinned release zip in `data/` and in the Claude project files, then tries the GitHub release asset. Pass `--zip PATH` if someone gives you the zip. |

If the install fails, you can still continue, but read section 5 first: every interaction claim must then say it is your own reading.

The DIO documents are in the repo (`kb/reference_sources/`, `kb/addendum/`) and need no database.

## 2. Ownership and availability

- `python3 -m mtgtools context [--deck D]` lists what is in the collection or a deck, and what its charter says.
- `python3 -m mtgtools card NAME` gives where the copies are, by policy tier (`decks/collection_policy.json`).
- `python3 -m mtgtools typal TYPE` does the same for a whole creature type and its support cards (§6.2).

Zach's inventory authority is the live Google Sheet titled exactly "MTG Master Inventory — Canonical". Find it by title, not by a stored id (`docs/DOCUMENT_PRECEDENCE.md` §3). Exports and the KB are snapshots. Say which snapshot you used: every `mtgtools` envelope names it under `collection`.

## 3. Ontology-grounded discovery

This is the step the Codex thread skipped. For each card in question:

1. **Read what the KB records:** run `python3 -m mtgtools card NAME`. It returns the Oracle text, the DIO contract readings (hooks, operations, requirement groups) and their review state.
2. **If the card is not in the KB:** a card acquired after the KB's inventory snapshot has no contract yet. `card` says so. Get its exact Oracle text from Scryfall (`https://api.scryfall.com/cards/named?exact=NAME`) when you have network access; if you work from memory, say so. Annotate it yourself with the DIO procedure (`python3 -m mtgtools dio 11`): one Operation per ability that matters, with requirement groups, amplifiers and result, in DIO vocabulary (`dio 4` hooks, `dio 5` operations). Label that annotation `agent-drafted, not in KB`.
3. **Find what connects:**
   - `explore NAME` (focused mode) lists links and loop candidates touching the card.
   - `explore NAME --mode divergent` lists two-step chains through pathways the card does not use itself. This is where unconventional interactions show up.
   - For a card that is not in the KB, explore from the owned side instead: a theme (`landfall`, `sacrifice_conversion`, `self_mill`, …) or the owned cards its hooks would feed.
4. **Test each candidate connection:** `hypothesis A B` reports what must hold, which links are unverified, and what argues against the connection. Then apply the DIO's three checks before you call it real (`dio 7`):
   - the output reaches the operation that holds the payoff;
   - it satisfies a requirement, not an amplifier;
   - it is qualified, not just similar.
5. **Look for structure, not tags:**
   - the structural searches in DIO §9 (`dio 9`);
   - the route patterns in §10 (blink, bounce, sacrifice, laundering, …);
   - the persistence table in §6.4 for anything that changes zones, copies or turns face down;
   - addendum §6 for fuel and feedstock.
6. **When the verbs run out:** `explore` cannot seed from a card that is not in the KB, and a token whose characteristics the contracts do not record (Treasure, for example) gives unresolved noise. Then query the KB directly: `kb/kbq.py`, or read-only SQL (`mode=ro`) on `kb/mtg_cards_v0.2.sqlite`, for example owned cards whose contracts trigger on the hook your annotation produces. That is expected. Say which queries you ran.
7. **Record what the KB missed:** when you find a connection the contracts do not support (a missing link, a contract that misreads Oracle text), list it in your answer as a KB gap. Append it to `challenges/ledger.jsonl` only if you were asked to change the repo.
8. **Check your draft:** `check` grades each claim in a draft answer by kind, and tests structured assertions (`mtgtools/README.md`).

`python3 -m mtgtools dio TERM` quotes the matching DIO sections, with file and line, and works with or without the KB. Its `reading_map` says where to start for common questions. Cite the sections you relied on.

## 4. What the evaluator is and is not

`kb/vendor/mtg_eval` (`deck`, `card`, `module`, `compare`, …) reads the inventory export or a collection database. Its roles and module memberships come from **its own text patterns** (`mtg_eval.semantic_patterns`), not from DIO contracts, even when the KB is present (challenge C-012). Its numbers are descriptive profiles, not rankings (P-04). Use it for deck shape: curve, counts, coverage, swap deltas. Do not cite it as evidence that an interaction exists or works.

## 5. Label the answer

End every card, deck or interaction answer with a grounding line. For example:

> **Grounding:** KB `mtg-kb-v0.2.1-r20261030` (kb_grounded); DIO v3.1.1 §7, §10, addendum §6. Mechanics are candidate contracts, 0 semantically reviewed. Card X and Card Y are not in the KB: agent-drafted annotation. Evaluator used for curve only.

The rules behind this line:

- **Verification state.** State it for every mechanics claim (`AGENTS.md`, hard rules). Today no contract is semantically reviewed, so every mechanics claim is exploratory.
- **No KB.** Say: *"Not KB-grounded: interaction analysis is my own reading of Oracle text, checked against DIO §… by hand."* Do not let a confident answer hide this.
- **Hypothetical and unowned cards.** Label them as such.
- **Authority.** Oracle text and the rules decide mechanics; the DIO decides representation; Zach decides intent. Disagreeing with a candidate contract is fine and useful. Record it as a disagreement, never as a fix.

## 6. Construction requests: route first, ask little

**Why.** Zach's blind ChatGPT test on 2026-10-31 asked only "I would like a Merfolk deck." The agent found the inventory, but no procedure told it what kind of construction problem it had. A search for the word "Merfolk" missed the type's strongest support (Harmonized Crescendo, Gathering Stone, Kindred Summons, Distant Melody, Urza's Incubator). The test's conclusion: the gap is between the request and the analysis, not in the ontology.

**Which document governs** is in `docs/DOCUMENT_PRECEDENCE.md`. Read it when two sources disagree.

### 6.1 Name the problem

| The request names | Path | Starts with |
|---|---|---|
| A commander | Protocol v1.0 new-deck | the requirements profile, then the commander's hooks |
| A mechanical thesis (sacrifice, blink, landfall) | v1.1/v1.2 inventory-first | `explore THEME --free`, then modules, color topology, commander |
| A creature type (Merfolk, Elves) | typal-first, §6.2 (proposed, D-0016) | `typal TYPE` |
| Swaps or transfers between decks that all stay playable | v1.2 portfolio allocation | `card NAME` availability tiers, donor-deck impact |
| Retiring a deck to feed another | decommission, §6.5 (proposed, D-0017) | `release DONOR --to RECEIVER` |

### 6.2 Typal-first path (proposed)

Creature type → owned type population → generic type support → mechanical clusters → color topology → commander candidates → functional completion.

1. `python3 -m mtgtools typal TYPE` lists, with availability under the collection policy:
   - `members`: the type is on the type line, creatures and Kindred spells alike;
   - `every_type`: Changeling and effects that grant every creature type;
   - `names_the_type`: cards whose text names the type (Seahunter);
   - `type_support`: chosen-type and shared-type cards (Kindred Summons, Gathering Stone);
   - `tagged_only`: cards with a typal tag but no chosen-type wording, probably about another type.

   It also gives `commander_candidates` (owned members that can be commander, with how many members and support cards fit each identity), `identities_without_type_commander` and `held_in_protected_decks`. Lexical hits are retrieval candidates. Read each card before you count it.
2. Find mechanical clusters among the members with `explore CARD` on the members that matter. The type is the identity; the clusters are what the deck does.
3. Lay out the color options side by side, and do not rank them on thematic fit alone. Merfolk example: mono-U behind Emperor Mihail II has 21 members; W–U has 32 but no owned Merfolk commander.
4. Add ordinary functions (ramp, removal, draw, protection) from the free pool.
5. **Check the qualifiers before counting a payoff.** DIO §4.1 lists creature type and chosen type as qualifier axes.
   - A card put onto the battlefield was not cast: Seahunter does not trigger Emperor Mihail II.
   - Changeling applies in every zone.
   - A Kindred spell has a creature type without being a creature.
   - Convoke taps creatures to pay a cost, which is not activating a mana ability (A1).
6. Never plan around a card whose every copy is in a protected deck. Name it and offer the free alternative.

### 6.3 Progressive requirements

- Start from provisional defaults and state them: Commander format, owned cards only, no copies taken from protected decks, a casual-focused power level.
- Do everything you can without the person first: census, color options, commander candidates.
- Then ask at most two questions, and only ones whose answer changes the next decision. For Merfolk: "Mono-blue behind Emperor Mihail II, or white–blue with a non-Merfolk commander?" and "Combat army or value engine?"
- Do not send a questionnaire, and do not commit to a 100-card list before the color option is settled.

### 6.4 Reading inventory results

- Map columns by header name, never by position.
- Check your record count against the count the connector reported. In the 2026-10-31 test, a positional parser reported zero Merfolk out of 35.
- A deck's list is the rows with that Deck **and** Status "Current deck". A search for the deck's name anywhere in a row also returns its bench, its reserves and other decks' proposed borrowing. In the 2026-10-31 test, "TMNT" matched 158 rows, of which 92 were the deck. `mtgtools` already counts only current-deck rows.
- A deck may be recorded under a name other than its commander's: Auntie Ool's deck is "Blight Curse". `mtgtools` accepts either name.

### 6.5 Decommission: retiring a deck to feed another (proposed)

Taking cards from a deck that stays playable is a v1.2 transfer: the donor's engine, replacements and deck floor stay constraints. Retiring the donor is a different operation, and its floor stops mattering. Physical custody still matters.

1. **Decommission.** Settle the donor's final list and mark the decommission proposed. It becomes approved when Zach says so, and complete only when he confirms it physically. A protected donor needs Zach and Steph to agree.
2. **Release audit.** `python3 -m mtgtools release DONOR --to RECEIVER` splits the donor's nonbasic cards four ways:
   - already in the receiver: singleton, so no new slot;
   - outside the receiver's color identity;
   - a free copy exists elsewhere: no disassembly needed, so don't credit the decommission for it;
   - unlocked only by the decommission.
3. **Target absorption.** For each unlocked or free candidate, judge three things separately:
   - its intrinsic value;
   - its extracted value: how much of its function survives leaving the donor's engine;
   - its absorbed value: what the receiver actually gains.

   Test the links with `hypothesis`, and check the qualifiers. -1/-1 counters cancel +1/+1 counters. Proliferate adds only counters of kinds already there. Dies is not leaves the battlefield. A token-entry trigger that fires once per turn fires once for a batch.
4. **Cuts.** Name the receiver cut for every add, and test the whole exchange (`compare RECEIVER OUT=IN …`). A cut from a protected receiver needs agreement. A recommendation is never a move.
5. **Return.** Released copies the receiver doesn't take go back to the free pool. Allocations change in the Sheet only after physical confirmation, under archive-then-clone.

## Where things are

| What | Path |
|---|---|
| DIO v3.1.1 and the 2026-10-09 addendum | `kb/reference_sources/` |
| Compatibility addendum A1–A7 (KB contract fields) | `kb/addendum/`, accepted copy in `docs/handoff/` |
| Grammar and rules vocabulary registry | `kb/reference_sources/MTG_Grammar_Rules_Vocabulary_Registry_v0.1.json` |
| Evaluation Protocol v1.2 addendum, Kairos–GATE | `kb/reference_sources/` |
| Tool reference | `mtgtools/README.md` |
| Which document governs; resolving the inventory by title | `docs/DOCUMENT_PRECEDENCE.md` |
| KB pin and download location | `tools/kb_release.json`, `data/README.md` |
