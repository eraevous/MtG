# Deterministic composition profiles (draft)

The grounded evaluator and `mtgtools compare` attach `data.composition_profile` to their reports. It uses the existing read-only inventory adapter and the same physical `DeckState` as the evaluator. It is descriptive and exploratory, not a ranking or a playability certificate.

```python
from kb.contract_roles import open_grounded_evaluator

ev = open_grounded_evaluator(database, engine_games=0)
result = ev.compare(deck, [(cut, addition)])
comparison = result['data']['composition_profile']
# comparison['before'], comparison['after'], comparison['deltas']
# comparison['individual_changes']: each exchange applied to the original list
```

For an existing workbook or collection-database Evaluator, call `kb.profile_reports.install_profiles(ev)` once. That path retains labelled evaluator-pattern role evidence. The grounded evaluator retains KB/DIO or fallback evidence per role. Both use the same helper. To profile a full explicit proposed list directly, call `kb.deck_profile.profile(inv, library, commanders, companion)` with one name per physical copy; no list is written back.

Supported surfaces:

| Surface | Profile location/content |
|---|---|
| Grounded `deck` | Current library and separate commander costs |
| Grounded `compare`, `mtgtools compare` | Full before/after and deltas; each exchange separately |
| Grounded `upgrades` | Current list, each proposed swap, each displayed standalone cut |
| Grounded `build` | Actual proposed list including basic multiplicity, even if incomplete |
| Direct wrapped Evaluator | Same four methods |

Not wired: `module`, `inventory`, `transfer`, `portfolio`, direct unwrapped Evaluator and `bridge_v02.open_evaluator`. No Fathom integration or new dependency. Existing goldfish sections are unchanged; their normalized mana is **not** the strict demand reported here.

## Synthetic example

`tests/test_deck_profile.py` constructs an invented library with 36 copies of **Basic**, one **Outlet Tutor**, and 62 **Spell**, plus **Leader** outside the library and a companion outside the 100. Names, records and decklist are synthetic; this is an arithmetic fixture, not a legal deck recommendation.

| Metric | Before | Cut one Basic | Delta |
|---|---:|---:|---:|
| Library slots | 99 | 98 | -1 |
| Land cards | 36 | 35 | -1 |
| Land percentage | 36.363636 | 35.714286 | -0.649351 percentage points |
| P(0–1 land cards in seven) | 0.201471 | 0.211889 | +0.010418 |
| P(2–4 land cards in seven) | 0.740268 | 0.734405 | -0.005864 |
| P(at least 3 land cards in seven) | 0.501077 | 0.485809 | -0.015268 |
| Size status | size_complete | incomplete | — |

The after odds describe only the supplied 98 slots, not a completed Commander deck. An unchanged list has zero numeric deltas. Swapping **Outlet Tutor** for **Outlet** preserves the supported sacrifice-outlet count but removes a detected tutor; undetected tutor capability remains unknown. A synthetic W/G land exchange preserves potential color counts while changing the inventory entry hints from untapped to tapped; that never proves available opening mana.

## Units, coverage and limits

- Counts and percentages use physical library slots; commander and companion never enter the draw denominator. Types overlap (an artifact creature counts in both). `other` is the complement of land/creature/enchantment/artifact among known types. Missing type rows are reported separately.
- Curve and mean use known nonland mana values, with unknown slots beside them. Multi-face rows retain face text and count as one physical card; unresolved zone/layout semantics suppress affected aggregates rather than assume a land face is a land in the library.
- Strict printed cost demand reuses `kb.mana.parse_cost`: WUBRG pips, generic and true C remain separate. Hybrid, Phyrexian and X symbols remain conditional, not paid or discarded. Commander costs are separate. Blank/malformed or multiple-face costs are unknown. Additional and alternative costs are not modeled.
- Potential mana colors come from current usable KB production contracts, with source state and candidate interpretation; missing contracts may fall back to labelled `Produces` inventory fields. Rejected/quarantined evidence is excluded. Color identity is never substituted for production. Counts overlap and do not imply simultaneous availability. Entry hints consume `ETB Tapped` as a candidate inventory hint, not a timing guarantee. Unknown production is never assigned C.
- Always-usable, fetch and opening usable-source counts remain null. Dorks and rocks require setup; commander-supplied or tap-triggered mana is not inserted into opening sources. Candidate source categories use land, then creature/dork, then artifact/rock, then other priority; type counts themselves overlap.
- Hypergeometric arithmetic uses exact integer combinations/Fractions, serialized as numeric probabilities. Each window includes exact-k, 0–1, 2–4 and at-least-3 land probabilities. Opening seven; turn 3 is nine seen on the play skipping the first draw, or ten on the draw/multiplayer. No mulligans, selection, extra draws or mill. Seeing a card is not casting it or making a land drop.
- Role odds are P(at least one **detected supported slot**). Alias groups union physical positions, never sum overlapping aliases. Tag-only, contradicted and undetected evidence stays unknown; zero detected providers is not verified absence. Every reported role retains its source and verification state.
- `delta` is after minus before, including probability units (multiply by 100 for percentage points). Unknown values yield null deltas. Size status checks only 100 cards including one or two commanders; it does not establish format legality, ownership availability or playability.

Run the synthetic slice with `python3 -m unittest discover -s tests -p test_deck_profile.py`. Its integration case runs all four actual vendor reports through the existing collection database reader without real cards or inventory.
