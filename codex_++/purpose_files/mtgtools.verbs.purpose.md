# Module: mtgtools.verbs
> Implementations of the six verbs over the KB's read-only query layer (kb/kbq.py) and the grammar layer's collection loop discovery.

@ai-path: mtgtools.verbs
@ai-source-file: mtgtools/verbs.py
@ai-role: query
@ai-intent: "Answer an LLM's questions with evidence and say how far each answer is established; surface relationships it did not ask about."
@ai-version: 0.4.1
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: claims, kb
@ai-contracts: P-01, P-03, P-04, P-05

### Inputs and outputs
| Direction | What |
|---|---|
| In | sqlite3 connection (KB v0.2.1 schema), grammar/discovery/collection_loops.csv, decks/charters/*.json, decks/collection_policy.json, evaluator (compare only) |
| Out | (data, claims) per verb |

### Risks, invariants and known gaps
- No `oracle_text` interpretation here (P-01): links come from contract query indexes and the KB's FEEDS table, and loops from the grammar layer. Exception under review (C-010): to qualify links, the module reads the contracts' structured `object_filter`, a leading "this" in the trigger's event phrase, and type-line words in target-eligibility phrases.
- Each link carries a qualifier status (`compatible` / `unresolved` / `incompatible`) and a basis. Incompatible links are rejected and summarised, never silently dropped. Unknown qualifiers (counter type, token characteristics, controller, face) stay `unresolved`, never matched.
- Loops from the grammar layer whose step no recorded KB contract produces are `loops_contested` (`unsupported_by_contracts`, not proof of invalidity). A rejected route never removes a card's other interactions (`hypothesis` → `acts_on`).
- `check`: `evidence_grade` is the source, `verdict` is the structured assertion, and `grade` is decision_grade only when both hold. Invariant: decision-grade evidence never automatically makes a decision-grade conclusion.
- `context --deck` role counts are detected candidates from the KB's role patterns, not verified roles. `sole_detected_candidates` means the only detected candidate, not a verified sole provider. A caveat claim (mechanics, exploratory until every card-role assignment in the summary is reviewed) says so, after the 2026-10-28 Golden Argosy error.
- Collection policy (`decks/collection_policy.json`) is operational configuration. It records Zach's decision, and the tools never move cards.
- `explore --mode divergent` with a seed returns two-step chains forward from the seed through pathways the seed does not use itself, scored so that narrow pathways come first. It is a heuristic for surfacing unrequested relationships, not a measure of value.
- Coverage: in r20261104, 0 of 4,961 contracts are semantically reviewed, so mechanics claims are exploratory today.
- Counter links (r20261031): a `counter.put` link is compatible only when the producer's counter kind matches the listener's (a listener for `any` accepts every kind); a +1/+1 producer against a -1/-1 listener is rejected as incompatible, and proliferate or generic producers stay unresolved (`counter_kind_possible`). `card` reports the card's counter facets and order-of-operations note; `release` lists each candidate's -1/-1 roles from the KB facets, and falls back to the lexical flag only on a KB that predates them.
- Copy links (r20261104, C-024): a producer whose contract records `copy_of` links to the copied card's own abilities: `copy_enters` (its self enter trigger fires for the copy), `copy_chapters` (chapters reached on a Saga copy from one entering lore counter plus the recorded `created_token` counters), `copy_type` (a copy of an enchantment is an enchantment entering; compatible only when the observer's filter names a type). Counters put on the created token never feed the producer's own chapter triggers.
- Cost payment events (0.3.1, C-023): a cost's `on_payment` sacrifice or discard feeds links (`basis: paid_object`), because `query_index.feeds` lists resolution effects only. A trigger with a "this or another" alternative is not self-only; a trigger naming its own card ("Sharuum enters") is. Loops through a finality-counter return or an instant/sorcery are `once_only` under `loops_contested`. The first two are read-time workarounds to retire when C-023 lands in a KB release.
- `find` (0.4.0, Kate 2026-11-01): retrieval over `capability_claims` by a declared role vocabulary (ROLE_FAMILIES / ROLE_ALIASES), never Oracle text. Evidence classes: reviewed_capability (review overlay), detected_candidate (rule match / evaluator patterns, C-012), inventory_tag_only (Collection.Roles). `shape` (repeatable / one-shot / conditional) comes from the contract whose exact text holds the matched phrase and its recorded `unbound` conditions. Every answer is nonexhaustive and reports KB and inventory freshness separately.

- As-of collections (0.4.1, Kate 2026-11-04): a database built by `tools/asof_kb.py` carries a dated `collection_policy.json` (or `not_recorded`) and an `as_of` manifest. Verbs read that policy instead of today's, grounding and `find` freshness name the date, and `compare` needs the dated workbook. Card meaning stays at the base release.
