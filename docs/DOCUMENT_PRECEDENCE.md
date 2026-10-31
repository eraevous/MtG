# Which document governs

Status: **proposed** (D-0016), pending Zach. Until he accepts it, read it as the agents' working reading of the project's sources, not as a decision.

**Why this exists.** Zach's blind ChatGPT test on 2026-10-31 ("I would like a Merfolk deck") found that agents had to reconstruct the source hierarchy from dates and addenda. The Evaluation Protocol v1.2 addendum says it is compatible with DIO v2.0 and v2.1, while the project uses DIO v3.1.1. The ChatGPT project instructions named an archived inventory id and gave a wrong tab count. This page states the order once.

## 1. One authority per question

| Question | Governing source | Not an authority |
|---|---|---|
| Who owns which copies, and where they are | The live Google Sheet titled exactly **MTG Master Inventory — Canonical** (no `_ARCHIVE` suffix). Find it by title. | Any stored Sheet id, the agent snapshot, xlsx exports, the KB |
| Who may use the collection; protected decks | `decks/collection_policy.json` (Zach, 2026-10-27): TMNT, Ashling, Rootha, Dina are protected | Anything inferred from deck lists |
| What a card says and does | Current Oracle text and the Comprehensive Rules | Sheet text, KB contracts, grammar parses |
| How mechanics are represented | DIO **v3.1.1**, its 2026-10-09 addendum, and the accepted A1–A7 compatibility addendum (`kb/addendum/`) | DIO v2.0, v2.1, v3.1.2 candidate |
| How decks are built and evaluated | Evaluation Protocol v1.0 with its v1.1 and v1.2 addenda, as read through §2 below | Evaluator numbers |
| How to play a deck | Kairos–GATE | |
| What Zach wants | Zach, and the deck charters he approves (`decks/charters/`) | Any model's inference |
| How work in this repo is done | `AGENTS.md`, `CHARTER.md`, hooks, CI | |

## 2. Reading older documents

- **A later version supersedes an earlier one on the same subject.** An addendum that says it extends an older base still applies, but its references to older versions are historical.
- **The Evaluation Protocol addenda name DIO v2.0 and v2.1.** Read those references as DIO v3.1.1. Where a v2.x term has no v3.1.1 counterpart, say so in the answer rather than inventing a mapping. This is a reading of version labels, not a claim that the vocabularies are identical.
- **Construction paths.** The v1.0 new-deck procedure (requirements profile, then the commander's hooks) applies when the request names a commander. The v1.1/v1.2 inventory-first path (thesis, modules, color topology, then commander) applies when the request names a mechanical thesis. A request that names a creature type follows the typal-first path in `docs/AGENT_GUIDE.md` §6 (proposed in D-0016). A request for swaps or transfers follows the v1.2 portfolio rules.
- **Derived artifacts carry their own limits.** The KB, the grammar layer and `mtg_eval` are rebuilt from sources and never govern. Their outputs must carry evidence status (P-03). The evaluator fully types only 4–31 of the 60–65 nonland cards in a deck (median 10), so its numbers are descriptive, not rankings (P-04).

## 3. Inventory: resolve by title, then check

1. Search Drive for the exact title `MTG Master Inventory — Canonical`. Exclude any title with a suffix (`_ARCHIVE`, a timestamp). Exactly one file should match.
2. Treat any stored id (in instructions, docs, release notes, adapters) as a hint. If the id opens a file whose title has a suffix, it is an archive: say so and use the title search instead.
3. The workbook has **41 tabs** as of 2026-10-25 (the 2026-10-24 export also has 41). Ownership is on the `Collection` tab, with the header on row 4. Older notes that say 38 are wrong.
4. If you can't open the Sheet (it is shared with Zach only), use the agent snapshot, the one-tab Sheet titled `MTG Collection — for agents (snapshot YYYY-MM-DD)`. The date in its title is the day it was copied. It holds values copied from the live Sheet, which was last modified on 2026-10-25, so a later snapshot date does not mean newer data. Name the snapshot you used.
5. Map columns by header name, never by position. After any parse, check that your record count matches the count the connector or query reported. A tool that returns row numbers alongside the columns shifts every positional index; in the 2026-10-31 test, a positional parser reported zero Merfolk when there were 35.

## 4. When sources disagree

Say which sources disagree and which one this page says governs. If the disagreement touches project purpose (`codex_++/project.purpose.md`), the purpose wins until Zach decides; log it in `challenges/ledger.jsonl` and do not resolve it yourself.
