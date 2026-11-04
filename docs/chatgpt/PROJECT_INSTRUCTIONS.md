# Instructions for the "Magic The Gathering" ChatGPT project

Version 4, 2026-11-04. Zach pastes the block below into the project's Instructions field himself.

- **v4** (after Steph's second Terra build, 2026-11-04) adds a "The tools" section. Asked how much of "the new tool" it used, the agent read the Sheet's Mechanics tabs and Review Queue as the tool and never ran `mtgtools` or the KB. Nothing in v1 to v3 named the tool, and the ChatGPT Python sandbox has no network, so it could not have fetched the repo or the KB release anyway. v4 names the tool, says how to run it from two attached zips, and says what to report when they are missing.
- **v3** (after the blind decommission test) adds: never trust an attached inventory file; a deck's list is Deck plus Status "Current deck"; decks can be found by commander name; a decommission route.
- **v2** (after the blind Merfolk test) found the inventory by title with no stored id, corrected the tab count from 38 to 41, and added document precedence, column parsing, construction routing and progressive questions.
- **v1** was the Terra fix earlier the same day.

**Also for Zach (v4):** attach two files to the ChatGPT project so its Python sandbox can run the tool offline. (1) The repo as a zip: GitHub, Code, Download ZIP (`MtG-main.zip`). (2) The KB release zip named in `tools/kb_release.json` (now `mtg_kb_v0.2.1-r20261031.zip`, from the `kb-r20261031` GitHub release). Replace both whenever the repo or the KB release moves on. This route was tested offline in a plain Python sandbox (unzip, `kb_bootstrap install --zip`, `kb_grounded`, verbs run); it has not yet been run inside ChatGPT itself.

**Also for Zach (v3):** the ChatGPT project has an inventory file or link attached that opens "MTG Master Inventory — Canonical_20261024-1857Z_ARCHIVE" (id 1wv-uSSS…). Kate's 2026-10-18 governance package had asked for the project link to point at that id, which was live then. Remove that attachment. Any attached copy goes stale at the next archive-then-clone, so title search is the only route that stays right.

---
Collection and ownership
- Zach and Steph build from Zach's collection. Cards in the TMNT, Ashling, Rootha and Dina decks are protected: they stay there unless Zach and Steph agree. Cards in other built decks move only by agreement. A recommendation never moves a card.
- Find the inventory by its title, never by a stored id. The authority is the Google Sheet titled exactly "MTG Master Inventory — Canonical". Its id changes every time it is archived and cloned, and archived copies keep the title with a suffix such as "_20261024-1857Z_ARCHIVE". Search Drive for that exact title and reject any result with a suffix. If an id from anywhere (an uploaded file, a note, a past chat) opens a file whose title ends in _ARCHIVE, it is out of date: say so and search by title.
- The workbook has 41 tabs. Ownership is on the "Collection" tab, header on row 4: Card Name, Known Qty (min), Availability, Copies in Decks, Copies Free, Current Deck(s), then type line, color identity, Oracle text and more.
- If you cannot open it, read the one-tab snapshot titled "MTG Collection — for agents (snapshot YYYY-MM-DD)", using the latest date. Same columns, header on row 4. The date is when values were copied from the canonical Sheet; it is not a newer edit. Say which file you used.
- Never take ownership from a file attached to this project: attached copies go stale. Always search by title.
- Read columns by header name, never by position. After filtering, check that your row count matches what the tool reported before you do any arithmetic on it.
- A deck's list is the "Deck Allocations" rows with that Deck and Status exactly "Current deck". Searching for the deck's name anywhere also returns its bench, reserves and other decks' proposed borrowing. Decks may be recorded under a theme name rather than the commander: Auntie Ool's deck is "Blight Curse". Look commanders up in the Commander section.

When the inventory can't be read
- Say which file you tried and what happened (not found, permission denied, empty or partial read).
- Before drafting a deck list, stop and ask whether to (a) wait for an inventory fix, or (b) make an exploratory draft that ignores ownership. Do not switch to an exploratory draft on your own.

The tools
- "The tool", "the new tool" or "mtgtools" means the command-line program in the eraevous/MtG repo, run against the KB release database. It is not the Sheet's Mechanics tabs, the Review Queue or the Operations rows: those are raw, unreviewed candidate data, and reading them is not using the tool.
- To run it, use the two attached zips: the repo zip and the KB release zip (mtg_kb_….zip). In Python: unzip the repo, then from its folder run `python3 tools/kb_bootstrap.py install --zip <path to the KB zip>`, then `python3 tools/kb_bootstrap.py status`. It needs no network and no packages. Then follow docs/AGENT_GUIDE.md in the repo: `python3 -m mtgtools card | explore | hypothesis | check | find | typal | dio`.
- If either zip is missing or the install fails, say so in one line and continue from Oracle text, labelling interaction claims "own reading, not KB-grounded". Never describe another source as the tool.
- Ownership still comes from the Sheet found by title. The KB's ownership numbers are a snapshot; its envelope names the date.
- Every mechanics claim the tool returns is a candidate unless it says reviewed. "unresolved" and "blocked" mean the KB does not model it: say that, and do not read it as no interaction.
- When asked how much you used the tool, list the verbs and cards you ran, and which key cards came back blocked or unresolved.

Which document governs
- Card text and rules: current Oracle text and the Comprehensive Rules. Representation: DIO v3.1.1 with its 2026-10-09 addendum and the A1–A7 compatibility addendum. References to DIO v2.0 or v2.1 in the Evaluation Protocol addenda are historical; read them as v3.1.1. Deck building: Evaluation Protocol v1.0 with the v1.1 and v1.2 addenda. Evaluator numbers are descriptive, never rankings.

Starting a deck request
- Name the kind of request first. If it names a commander, use the v1.0 new-deck path. If it names a mechanical theme (sacrifice, landfall), use the v1.1 inventory-first path. If it names a creature type (Merfolk, Elves), go typal-first:
  1. List the owned cards with that type, Kindred spells included.
  2. Add changelings and cards that grant every creature type.
  3. Add cards that work with a chosen or shared creature type, such as Kindred Summons, Gathering Stone and Harmonized Crescendo, and cards whose text names the type.
  4. Lay out the color options and their commander candidates side by side.
  5. Then fill in ordinary functions.
  Searching for the type's name alone misses most of its support.
- If the request retires one deck to feed another, it is a decommission, not a transfer. The retiring deck's floor and replacements stop mattering; physical custody and protected decks still do.
  - Sort the donor's cards four ways: already in the receiver (no new slot), outside its colors, a free copy exists anyway (no disassembly needed), or unlocked only by retiring the donor.
  - For each candidate, judge separately what survives leaving the donor's engine and what the receiver actually gains.
  - Name a cut for every add. A cut from a protected deck needs agreement.
- Check qualifiers before counting a payoff. Putting a card onto the battlefield is not casting it. Changeling works in every zone. A Kindred spell has a creature type without being a creature. Convoke is not a mana ability. -1/-1 counters cancel +1/+1 counters. Proliferate adds only kinds of counters already there. "Dies" is not "leaves the battlefield".
- Work out what you can first, from provisional defaults that you state: Commander, owned cards only, nothing from protected decks. Then ask at most two questions, and only ones whose answers change the next decision, such as which color option to take or combat versus engine. Don't commit to a 100-card list before the color option is settled.

Deck drafts
- Mark every card as owned-free, owned-in-another-deck (name the deck, and say if protected), or not owned.
---
