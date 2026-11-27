# Module: kb.profile_reports
> Add the single physical profile implementation to existing evaluator reports without editing pinned vendor code.

@ai-path: kb.profile_reports
@ai-source-file: kb/profile_reports.py
@ai-role: evaluator_adapter
@ai-intent: "Give current decks and proposed exchanges the same numeric before/after representation."
@ai-version: 0.1.1
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: ext:kb.deck_profile, ext:mtgtools.verbs
@ai-contracts: P-00, P-01, P-03, P-04

`install_profiles(ev)` is opt-in and idempotent. Wired by open_grounded_evaluator and mtgtools compare. Supports deck, compare (whole proposal and individual exchanges), upgrades (each proposed swap and displayed standalone cut), build (actual temporary physical state, preserving basic multiplicity). Machine-readable profiles live at data.composition_profile; reports show composition summary tables and comparison deltas.

Uses existing evaluator deck/card alias resolution and DeckState. Does not change recommendations, goldfish simulation, allocations or pinned semantics. Build restores its temporary _state capture even on failure; the existing build and this adapter are not thread safe. Other report methods and direct unwrapped Evaluator/bridge_v02 callers are explicitly out of scope. Legacy goldfish sections keep their original semantics and are not strict composition demand.

Tests: tests/test_deck_profile.py, including all four real vendor reports over a synthetic collection database through the existing collection adapter.

0.1.1 display correction: rendered panels expose absolute composition, curve, candidate supply, strict demand and all draw windows for current/full proposals and each individual swap or incomplete cut. Probability values are percentages and their changes are percentage points; nulls render as unknown. The numeric profile payload and model are unchanged. Synthetic rendered-output tests cover 38-to-40 lands, standalone cuts, upgrade/build panels, unresolved faces and equal-source timing-unknown controls.
