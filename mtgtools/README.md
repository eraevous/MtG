# mtg: tools a conversational AI can think with

Six read-only verbs over Zach's MTG knowledgebase, with JSON output. A chat model (Claude, ChatGPT, …) calls them to answer exploratory questions such as "what could Terra do beyond the obvious enchantment plan?" The tools return the evidence and how far it is established. The model does the conversation, and the person decides.

Standard library only. Python 3.10+.

## Setup

The verbs read the KB database, which is not in Git. Put `mtg_cards_v0.2.sqlite` (and `SOURCE_MANIFEST.json`, already in `kb/`) where `data/README.md` says. `compare` also needs an inventory export (`--workbook`, `MTG_WORKBOOK`, or the newest `data/*.xlsx`).

A different collection: pass `--db path/to/your.sqlite`, built with `kb/migrate_v02.py` from your own export. A plain "bring your own collection" path is planned separately.

## Verbs

| verb | asks | example |
|---|---|---|
| `context [--deck D]` | What is in the collection or a deck, and what does its charter say? | `python3 -m mtgtools context --deck Vraska` |
| `card NAME` | Oracle text, the contract readings and their review state, and where the copies are | `python3 -m mtgtools card "Terra, Magical Adept"` |
| `explore [SEED] [--ci C] [--deck D] [--free] [--mode focused\|divergent]` | What could connect here? Seed is optional: a card, a commander or a theme (`landfall`, `self_mill`, …) | `python3 -m mtgtools explore "Terra, Magical Adept" --mode divergent` |
| `hypothesis A B [--effect E] [--ci C]` | What would have to hold for A and B to interact, which links are unverified, and what argues against it? | `python3 -m mtgtools hypothesis "Cauldron of Essence" Knightfisher` |
| `compare DECK OUT=IN …` | What does the evaluator's descriptive profile do under these swaps? | `python3 -m mtgtools compare TMNT "Crustacean Commando=Knockout Maneuver"` |
| `check FILE\|-` | For each claim in a draft answer, what does it rest on, and what is missing? | `echo '[{"text":"…","kind":"mechanics","cards":["…"]}]' \| python3 -m mtgtools check -` |

`explore` modes:
- **focused** (default with a seed): links and loop candidates that touch the seed. This answers what was asked (`discovery: requested`).
- **divergent** (default without a seed): with a seed, two-step chains *forward from the seed* through pathways the seed does not use itself, narrow pathways first. Without a seed, links and loops across the pool, rarest pathways first. This surfaces what nobody asked about (`discovery: unrequested`).

## Reading the output

Every response is one envelope: `tool`, `version`, `verb`, `query`, `collection` (KB release and inventory snapshot hash), `summary`, `claims`, `data`, or `error`.

Each claim has a **kind**, and its **grade** is set per kind:

| kind | decision_grade when | otherwise |
|---|---|---|
| `inventory` | it comes from the named collection snapshot | exploratory |
| `rules_text` | the text is Scryfall Oracle with confirmed identity | exploratory |
| `mechanics` | every contract it rests on is `semantic_reviewed` | exploratory |
| `performance` | never in v0: the evaluator is descriptive and unvalidated | exploratory |
| `preference` | never: it belongs to the person, in `decks/charters/` | not_system_gradable |

`decision_grade` on one kind says nothing about the others. A legal, owned, mechanically verified interaction can still be a poor fit for someone's deck.

**State of the evidence (r20261024d).** 0 of 4,961 contracts are semantically reviewed, so today every mechanics claim is exploratory. Links match an effect to a trigger hook, without checking qualifiers such as whose permanent or which type, so treat each link as a lead to read. Absence of a link proves nothing.

## Tests

`python3 -m unittest tests.test_mtgtools`. The verb tests skip when the KB database is absent. The held-out evaluation is Kate's eight frozen Terra questions (v1.0, prompt sha256 `eab81c1cb306…`), run against the first usable version. The expected-answer notes are kept away from whoever builds the tools.
