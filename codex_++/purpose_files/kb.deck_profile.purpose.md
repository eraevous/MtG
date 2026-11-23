# Module: kb.deck_profile
> Reusable deterministic composition and exact draw profiles over existing inventory rows, physical deck slots and evidenced role records.

@ai-path: kb.deck_profile
@ai-source-file: kb/deck_profile.py
@ai-role: evaluator_adapter
@ai-intent: "Make the composition consequences of a proposed list or cut inspectable without introducing another card rule engine."
@ai-version: 0.1.1
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: ext:kb.mana
@ai-contracts: P-00, P-01, P-02, P-03, P-04

Inputs: read-only inventory rows, inv.record(), explicit physical library slots, commanders and companion separately, optional role alias groups. KB inventories additionally expose current typed production contracts.
Outputs: counts/percentages, strict printed cost demand via kb.mana, candidate potential production, candidate entry hints, exact hypergeometric probabilities and numeric comparison deltas. Each role and production record retains its evidence. No writes, refresh, ranking, Oracle-text parsing or automatic semantic promotion.

Unknown types suppress land odds; unknown roles never become supported roles. Role probabilities describe access to the detected supported slots, not all possible providers. Incomplete lists retain conditional supplied-list counts and odds, explicitly labelled incomplete. Size completeness is not legality. Multi-face uncertainty is preserved instead of flattening a flexible land face into an additional card. Entry hints are not opening usability. Artifact creatures producing mana are categorized as dorks; card type percentages still overlap. `other` is the complement of land/creature/enchantment/artifact among known types and therefore includes instants, sorceries, planeswalkers and battles.

Tests: tests/test_deck_profile.py (synthetic only), including exact small-population arithmetic, identity and one-cut comparisons, role alias unions, typed costs, optional faces, production/entry uncertainty and rejected evidence.

0.1.1: comparison snapshots align omitted roles to a shared vocabulary using each side's own physical quantities and role evidence. Unknown coverage is independently computed, never zero-filled from an absent dictionary key. Explicit not-computed nulls remain null; detected supported absence remains zero when the evidence is available. Inputs are not mutated. Regression tests cover both exchange directions, full and individual comparisons, and incomplete cuts.
