# mtg: tools a conversational AI can think with

Seven read-only verbs over Zach's MTG knowledgebase, with JSON output. A chat model (Claude, ChatGPT, …) calls them to answer exploratory questions such as "what could Terra do beyond the obvious enchantment plan?" The tools return the evidence and how far it is established. The model does the conversation, and the person decides.

Standard library only. Python 3.10+.

## Setup

The verbs read the KB database, which is not in Git. `python3 tools/kb_bootstrap.py install` puts `mtg_cards_v0.2.sqlite` in `kb/` (details in `data/README.md`). `dio` needs no database. `compare` also needs an inventory export (`--workbook`, `MTG_WORKBOOK`, or the newest `data/*.xlsx`).

A different collection: pass `--db path/to/your.sqlite`, built with `kb/migrate_v02.py` from your own export. A plain "bring your own collection" path is planned separately.

## Verbs

| verb | asks | example |
|---|---|---|
| `context [--deck D]` | What is in the collection or a deck, and what does its charter say? | `python3 -m mtgtools context --deck Vraska` |
| `card NAME` | Oracle text, the contract readings and their review state, and where the copies are | `python3 -m mtgtools card "Terra, Magical Adept"` |
| `explore [SEED] [--ci C] [--deck D] [--free] [--mode focused\|divergent]` | What could connect here? Seed is optional: a card, a commander or a theme (`landfall`, `self_mill`, …) | `python3 -m mtgtools explore "Terra, Magical Adept" --mode divergent` |
| `hypothesis A B [--effect E] [--ci C]` | What would have to hold for A and B to interact, which links are unverified, and what argues against it? | `python3 -m mtgtools hypothesis "Cauldron of Essence" Knightfisher` |
| `compare DECK OUT=IN …` | What does the evaluator's descriptive profile do under these swaps? | `python3 -m mtgtools compare TMNT "Crustacean Commando=Knockout Maneuver"` |
| `dio TERM` | What does the ontology say? Quotes the DIO v3.1.1, addendum and A1–A7 sections that match, with file and line, plus a reading map. No database needed | `python3 -m mtgtools dio persistence`, `python3 -m mtgtools dio 7` |
| `typal TYPE [--ci C] [--free]` | For a creature-type request: which owned cards have the type, which changelings and chosen-type cards support it, which commanders cover which color identities, and which copies sit in protected decks | `python3 -m mtgtools typal Merfolk` |
| `release DONOR --to RECEIVER` | If DONOR is retired, which of its cards does RECEIVER already run, which can't it use, which have a free copy anyway, and which does only the decommission unlock? Decks resolve by name or by commander | `python3 -m mtgtools release "Auntie Ool" --to TMNT` |
| `check FILE\|-` | For each claim in a draft answer, what does it rest on, what is missing, and does a structured assertion hold? | `echo '[{"text":"…","kind":"inventory","cards":["…"],"assert":{"free_min":1}}]' \| python3 -m mtgtools check -` |

`explore` modes:
- **focused** (default with a seed): links and loop candidates that touch the seed. This answers what was asked (`discovery: requested`).
- **divergent** (default without a seed): with a seed, two-step chains *forward from the seed* through pathways the seed does not use itself, narrow pathways first. Without a seed, links and loops across the pool, rarest pathways first. This surfaces what nobody asked about (`discovery: unrequested`).

`typal` buckets: `members` (the type line has the type, Kindred spells included), `every_type` (Changeling keyword, or text granting every creature type), `names_the_type`, `type_support` (chosen-type or shared-type wording, or the KB tags `Choose a creature type`/`Changeling`), and `tagged_only` (a typal tag without chosen-type wording, usually about another type). Members and the Changeling keyword come from recorded fields. Every other bucket comes from a declared lexical lookup over the KB rules text (`basis: lexical:…`, support `lexical_match`). Those hits are retrieval candidates, never contract readings (P-01). `tag_gaps` lists the cards that only the lookup found, because the KB capability tags miss them; that is a data-layer gap. Whether a payoff counts a card (cast or enters, Changeling in every zone, Kindred) is decided by the DIO qualifiers, not by the census.

## Reading the output

Every response is one envelope: `tool`, `version`, `verb`, `query`, `collection` (KB release and inventory snapshot hash), `grounding`, `summary`, `claims`, `data`, or `error`.

`grounding.level` says what the answer rests on: `kb_grounded` (the pinned KB release), `kb_unpinned` (another KB build), `doctrine_only` (no KB: nothing rests on DIO contracts) or `doctrine` (a `dio` lookup). Agents carry it into their answer (`docs/AGENT_GUIDE.md`).

Each claim has a **kind**, and its **grade** is set per kind:

| kind | decision_grade when | otherwise |
|---|---|---|
| `inventory` | it comes from the named collection snapshot | exploratory |
| `rules_text` | the text is Scryfall Oracle with confirmed identity | exploratory |
| `mechanics` | every contract it rests on is `semantic_reviewed` | exploratory |
| `performance` | never in v0: the evaluator is descriptive and unvalidated | exploratory |
| `preference` | never: it belongs to the person, in `decks/charters/` | not_system_gradable |

`decision_grade` on one kind says nothing about the others. A legal, owned, mechanically verified interaction can still be a poor fit for someone's deck.

**A good source is not a true claim (`check`).** Each checked claim has:
- `evidence_grade`: how good the source is.
- `verdict`: whether the claim's structured `assert` holds. The values are `SUPPORTED`, `CONTRADICTED`, `UNKNOWN` (cards missing, or no policy recorded), and `NOT_CHECKED` (no assertion, or a kind with no mechanical check).
- `grade`: `decision_grade` only when a decision-grade source settles the assertion.

The verdict's object is the assertion (`verdict_on: assertion`), never the sentence: a true assertion next to a false sentence is still `SUPPORTED`, and `text_judged` stays false. A `CONTRADICTED` verdict at `decision_grade` means the contradiction is established, not that the sentence was checked. Assertion keys:
- `inventory`: `owned_min`, `free_min`, `usable_without_asking_min`, `usable_by_agreement_min`, `in_deck`.
- `rules_text`: `text_contains`.

**Links and their qualifiers.** A link matches an effect to a trigger hook, then tests the qualifiers the contracts record:
- the object type filter, such as "an artifact or Artificer you control";
- "this … enters" self-triggers;
- the types a targeted ability accepts.

Every link has `qualifiers` and a `basis`:
- `compatible`: a recorded qualifier is satisfied.
- `unresolved`: the record can't decide, for example on counter type, a token's characteristics, which face, or controller. An unresolved link is a lead, not a match.
- `incompatible`: the link is rejected, and counted with reasons in `rejected_links`.

Same-card links show a card feeding itself, such as Terra's chapter IV returning her front face. Self-enter links cover a copy or return of a targeted permanent. Grammar-layer loops whose step no recorded KB contract produces are listed under `loops_contested` (`unsupported_by_contracts`): not supported by the contracts as they stand, which is not proof the loop is invalid. A target phrase with "or" that misses stays unresolved until the KB represents disjunctions. Rejecting one route never removes a card: `hypothesis` also lists `acts_on`, the targeted abilities whose target type fits the other card. Absence of a link still proves nothing.

**Collection policy.** `decks/collection_policy.json` records who may use the collection and which decks are protected. `context` reports it. `card` gives availability in tiers:
- free copies;
- copies in protected decks;
- copies in other built decks, which can move by agreement;
- planned-only allocations, which are not physical moves.

The tools never move cards.

**State of the evidence (r20261030).** 0 of 4,961 contracts are semantically reviewed, so today every mechanics claim is exploratory.

## Tests

`python3 -m unittest tests.test_mtgtools`. Qualifier matching is tested on hand-built contracts and runs everywhere. The verb tests skip when the KB database is absent.

Kate's eight Terra questions (v1.0, prompt sha256 `eab81c1cb306…`) were run twice against 0.1.0 @ `4951faa`: once by the builder and once by a fresh-context agent. They are no longer held out. They now serve as regression tests, covering Terra × Banishing Light, Terra's own cycle, energy/lore, Era of Innovation, Decoction Module and the `check` verdict. The next blind evaluation needs new prompts.
