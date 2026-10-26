## MTG DECK BUILDING AND EVALUATION PROTOCOL v1.2 ADDENDUM  
## PORTFOLIO ALLOCATION & TRADE REQUESTS  
**Namespace: mtg-dbep-portfolio**  
   
⸻  
   
## COMPATIBILITY  
This addendum is a compatible extension to **MTG Deck Building and Evaluation Protocol v1.0.0** and its v1.1 addendum.  
It assumes use of:  
* MTG Deck Interaction Ontology v2.0  
* MTG Deck Interaction Ontology v2.1 Addendum  
* MTG Deck Building and Evaluation Protocol v1.0  
* MTG Deck Building and Evaluation Protocol v1.1 Addendum  
It does not add new primitive card-interaction relations.  
The Interaction Ontology already describes what cards and modules do, what they require, what they expose, and how they connect. It explicitly separates capability/connectivity from evaluative questions such as whether a card is worth a slot.  
The existing Deck Building and Evaluation Protocol already recognizes allocation as part of opportunity cost:  
Does using the card here weaken another owned deck?  
and requires comparison between actual alternatives rather than isolated evaluation.  
It also already requires inventory records to distinguish owned count, assigned count, free count, and deck locations, and directs allocation decisions to consider target improvement, source harm, replacement availability, uniqueness, duplicate copies, and deliberate preservation of lower-value decks.  
This addendum promotes those concerns into a first-class **portfolio-level allocation process**.  
   
⸻  
   
## 1. PURPOSE  
The original protocol primarily asks:  
Given this deck, what card should enter or leave?  
The portfolio problem asks:  
Given every relevant physical card, every deck that may use those cards, and the user’s preservation constraints, where should each scarce card live?  
A local deck improvement may create a larger portfolio loss.  
Conversely, a card that appears unavailable to one deck may become available after a sequence of replacements or exchanges across several decks.  
The portfolio layer therefore evaluates:  
* permanent card custody;  
* temporary shared configurations;  
* deck-to-deck transfers;  
* swaps;  
* multi-deck exchange cycles;  
* contested cards;  
* shared modules;  
* replacement cascades;  
* deck protection constraints;  
* acceptable deck floors;  
* collection-wide marginal contribution.  
The objective is not to maximize the strength of one deck.  
The objective is not even necessarily to maximize raw total deck strength.  
The objective is:  
**Find allocations that improve the collection of decks the user actually wants to maintain, subject to ownership, coexistence, identity, play-experience, and preservation constraints.**  
   
⸻  
   
## 2. WHY A SEPARATE PORTFOLIO LAYER IS REQUIRED  
DeckEvaluator remains intentionally deck-local.  
Its candidate comparison model measures deltas such as:  
* intrinsic rate;  
* functional coverage;  
* mana;  
* modules;  
* redundancy;  
* dependency;  
* resilience;  
* contention;  
* closing power;  
* experiential fit;  
* inventory or cost.  
That is sufficient for:  
Should Deck A replace X with Y?  
It is not sufficient for:  
Should Deck A give X to Deck B if A can then receive Y from Deck C, which can replace Y with Z from the Free pool?  
That requires a graph whose nodes include **physical card copies, decks, replacements, modules, and allocation states**.  
The portfolio layer sits above individual DeckEvaluator results.  
   
⸻  
   
## 3. GOVERNING PRINCIPLE  
## OPTIMIZE CARDS LOCALLY ONLY AFTER ACCOUNTING FOR THEIR GLOBAL OPPORTUNITY COST  
A card does not possess a single universal “best deck.”  
Its allocation value depends on:  
* its contribution to a candidate deck;  
* the card it displaces there;  
* the contribution lost by its current deck;  
* the best replacement available to that source deck;  
* whether that replacement itself must be moved;  
* the resulting module and functional changes;  
* the coexistence regime;  
* the user’s preservation requirements.  
Therefore:  
**Portfolio value is marginal and state-dependent.**  
   
⸻  
   
## 4. PORTFOLIOSTATE  
Add a new top-level analytical object:  
```
portfolio_state:
  portfolio_id:
  version_date:
  inventory_source:
  inventory_confidence:

  physical_inventory:
  decks:
  configurations:
  free_pool:
  shared_modules:

  allocation_regimes:
  protected_decks:
  experimental_decks:

  unresolved_collisions:
  contested_cards:
  pending_claims:
  proposed_transactions:

  portfolio_constraints:
  deck_floors:
  identity_constraints:
  pristine_constraints:
  coexistence_requirements:
  complexity_limits:
  movement_preferences:

  evidence:
  uncertainties:

```
PortfolioState is authoritative for allocation questions in the same sense that DeckState is authoritative for deck-local questions.  
Do not perform exact allocation analysis when physical ownership or current deck allocations are materially uncertain.  
   
⸻  
   
## 5. PHYSICAL COPY IDENTITY  
Portfolio analysis operates on **physical copies**, not card names alone.  
The base protocol already requires tracking copies rather than inferring unavailability from repeated names.  
Extend inventory representation conceptually with:  
```
physical_copy:
  copy_id:
  card_name:
  edition:
  collector_number:
  foil_or_treatment:
  condition:
  proxy_status:

  current_location:
  current_configuration:
  protected_status:

  eligible_decks:
  allocation_history:

```
Two copies of the same card may have identical game function while having different allocation constraints.  
Examples:  
* one copy may belong to a pristine precon;  
* one may be foil and intentionally protected;  
* one may already be sleeved into a permanently assembled deck;  
* one may be considered freely movable;  
* one may be part of a shared Power Core.  
Do not collapse physical-copy constraints into card-name availability.  
   
⸻  
   
## 6. ALLOCATION REGIMES  
A physical collision exists only when two configurations must exist simultaneously.  
Add:  
```
allocation_regime:
  regime_id:
  name:
  coexistence_rule:
  eligible_decks:
  shared_cards_allowed:
  shared_modules_allowed:
  physical_reconfiguration_allowed:
  protected_sources:
  notes:

```
Core regime classes:  
## 6.1 SIMULTANEOUS / INDEPENDENT  
All decks in the regime must be physically playable at the same time.  
One physical copy cannot occupy more than one deck.  
Examples:  
* Dina-I  
* Ashling-I  
* TMNT-I  
* Sharuum-I  
* Brigid-I  
If all are meant to be brought assembled to Commander Night, they compete for unique copies.  
## 6.2 POWERED / EXCLUSIVE  
Only one configuration is expected to exist at a time.  
Cards may be shared between mutually exclusive powered builds.  
Example:  
```
Dina-P
Necrobloom-P

```
may both use the same five-card Power Core if only one powered deck will be instantiated at once.  
This is not an inventory collision.  
It is a configuration dependency.  
## 6.3 PROTECTED  
Cards in the protected source cannot be donated except by explicit override.  
Examples:  
* pristine precons;  
* archival lists;  
* sentimental decks;  
* collector treatments;  
* decks explicitly frozen against cannibalization.  
## 6.4 EXPERIMENTAL  
Temporary allocation may be modeled without changing authoritative physical state.  
This is useful for:  
* theorycrafting;  
* provisional powered builds;  
* candidate swaps;  
* temporary test nights;  
* borrowed Power Cores.  
## 6.5 HYBRID  
A portfolio may use several regimes simultaneously.  
A deck may have:  
* Independent configuration;  
* Powered configuration;  
* experimental configuration.  
These must be treated as distinct allocation objects.  
   
⸻  
   
## 7. CONFIGURATION IDENTITY  
A deck name alone is insufficient when multiple physical or powered forms exist.  
Use:  
```
deck_configuration:
  configuration_id:
  base_deck:
  regime:
  authoritative_list:
  status:

  shared_modules:
  configuration_only_cards:
  permanent_cards:

  must_coexist_with:
  mutually_exclusive_with:

  requirements_profile:
  floor_profile:

```
Example:  
```
Dina-I = independently assembled Dina
Dina-P = Dina with Biomass Power Core
Necrobloom-I = independent Necrobloom
Necrobloom-P = Necrobloom with Biomass Power Core

```
A card may be contested between Dina-I and Necrobloom-I while being legitimately shared between Dina-P and Necrobloom-P.  
   
⸻  
   
## 8. ALLOCATION CLAIM  
A deck does not merely “want” a card.  
It makes an **allocation claim**.  
```
allocation_claim:
  card_or_copy:
  requesting_configuration:
  current_configuration:
  regime:

  requested_role:
  requested_modules:
  bottlenecks_targeted:

  target_outgoing_card:
  target_gain:
    intrinsic_delta:
    functional_delta:
    module_delta:
    redundancy_delta:
    resilience_delta:
    bottleneck_relief:
    closing_power_delta:
    experiential_delta:

  source_loss_without_replacement:
    functional_loss:
    modules_weakened:
    redundancy_lost:
    resilience_loss:
    identity_effect:
    experiential_effect:

  replacement_set:
  replacement_adjusted_source_loss:

  portfolio_effect:
  classification:

  confidence:
  evidence:

```
Claims must expose **why** the card is scarce or valuable.  
Do not use raw synergy count as the primary basis for arbitration.  
The base protocol already establishes that graph degree alone is not value; scarcity, activation probability, relevance, output quality, and bottleneck relief matter.  
   
⸻  
   
## 9. REPLACEMENT SET  
Every serious request for an allocated card should search for replacement routes.  
```
replacement_set:
  source_configuration:
  departing_card:

  candidates:
    - card:
      current_location:
      acquisition_type:
      outgoing_if_needed:
      functional_match:
      module_match:
      rate_change:
      mana_change:
      resilience_change:
      experiential_change:
      dependency_change:
      confidence:

  best_available_replacement:
  replacement_chain_required:
  resulting_source_state:

```
Candidate sources may include:  
* Free pool;  
* unused copies;  
* another deck;  
* another shared module;  
* role-equivalent cards;  
* module redesign;  
* functional substitution rather than textual substitution.  
Replacement analysis should prefer **function and route preservation**, not identical wording.  
The base protocol explicitly distinguishes textual, functional, route, structural, protective, and inventory redundancy.  
   
⸻  
   
## 10. REPLACEMENT-ADJUSTED LOSS  
This is the central quantity in the protocol.  
Do not ask:  
How much does Deck A lose if Card X leaves?  
Ask:  
How much does Deck A lose after receiving its best feasible replacement?  
Conceptually:  
```
Replacement-Adjusted Source Loss
=
Value(Source before transfer)
−
Value(Source after best feasible repair)

```
Similarly:  
```
Target Improvement
=
Value(Target after receiving card and making required cut)
−
Value(Target before transfer)

```
The portfolio question becomes:  
```
Portfolio Delta
≈
Target Improvement
−
Replacement-Adjusted Source Loss
−
Secondary Cascade Costs

```
This is a reasoning model, not a demand for invented numerical precision.  
The base protocol already treats expected-contribution equations as conceptual frames rather than exact mathematics.  
Use ordinal or descriptive bands unless simulation or substantial evidence supports finer estimates.  
Suggested bands:  
```
transformative gain
large gain
meaningful gain
small gain
neutral
small loss
meaningful loss
large loss
structural damage

```
   
⸻  
   
## 11. REPLACEMENT SCARCITY  
A card’s claim strength depends partly on how replaceable it is in each deck.  
This produces **replacement scarcity**.  
A card may be excellent in two decks while having dramatically different allocation importance.  
Example:  
```
Dina with Mazirek:
very strong

Dina without Mazirek but with best available substitute:
meaningfully weaker

Necrobloom with Mazirek:
very strong

Necrobloom without Mazirek but with best available substitute:
almost unchanged

```
Dina therefore has the stronger permanent claim even if Mazirek has high raw synergy in Necrobloom.  
The relevant question is:  
**Which deck loses more irreplaceable function without this particular physical copy?**  
Replacement difficulty already exists in CardValueProfile.  
Portfolio analysis makes it comparative across decks.  
   
⸻  
   
## 12. TRANSFER  
A Transfer moves one physical card from one configuration to another.  
```
Deck A → Card X → Deck B

```
Record:  
```
transfer:
  card:
  source:
  destination:
  regime:

  source_replacement:
  destination_cut:

  source_delta:
  destination_delta:
  secondary_effects:
  portfolio_delta:

  classification:
  status:
  confidence:

```
A transfer recommendation is incomplete without identifying:  
* what enters the destination;  
* what leaves the destination;  
* what replaces the transferred card in the source;  
* whether that replacement is actually available;  
* whether the source remains above its required floor.  
   
⸻  
   
## 13. SWAP  
A Swap exchanges cards between two configurations.  
```
A gives X to B
B gives Y to A

```
Do not evaluate this as two independent transfers.  
Evaluate the resulting joint state.  
```
swap:
  deck_a:
  gives_a:
  receives_a:

  deck_b:
  gives_b:
  receives_b:

  deck_a_delta:
  deck_b_delta:
  interaction_between_changes:
  portfolio_delta:

  classification:

```
A swap can be especially efficient when each incoming card repairs the precise weakness created by the departing card.  
   
⸻  
   
## 14. EXCHANGE CYCLE  
An exchange cycle involves three or more configurations.  
Example:  
```
TMNT → Y → Sharuum
Sharuum → X → Dina
Dina → Wight → Necrobloom

```
with:  
```
Free Pool → Z → TMNT

```
Represent as:  
```
exchange_cycle:
  cycle_id:

  movements:
    - source:
      card:
      destination:

  prerequisite_replacements:
  affected_configurations:

  per_deck_deltas:
  portfolio_delta:

  weakest_resulting_deck:
  floor_checks:

  cycle_dependencies:
  reversible:
  status:
  confidence:

```
The system must evaluate the **final simultaneous state**, not greedily approve each edge in isolation.  
A locally negative intermediate transfer may be part of a globally favorable cycle.  
   
⸻  
   
## 15. ALLOCATION GRAPH  
Portfolio allocation can be represented as a graph.  
Nodes may include:  
* physical card copies;  
* deck configurations;  
* Free pool;  
* shared modules;  
* replacement candidates;  
* protected sources.  
Edges may include:  
* currently allocated to;  
* requested by;  
* replaceable by;  
* transferable to;  
* protected from;  
* shared with;  
* mutually exclusive with;  
* unlocks transfer of;  
* depends on release of.  
This graph is not the same as the Interaction Ontology graph.  
The Interaction Ontology models game-function connectivity.  
The Allocation Graph models **physical custody and substitution relationships**.  
Do not merge the two.  
Instead:  
```
Interaction Ontology
        ↓
Deck Evaluators
        ↓
Allocation Graph

```
DeckEvaluator provides contribution estimates used by portfolio decisions.  
   
⸻  
   
## 16. CONTESTED-CARD ARBITRATION  
A card is contested when:  
* too few physical copies exist;  
* multiple simultaneously instantiated configurations claim it;  
* sharing is disallowed by regime;  
* no current allocation satisfies all claims.  
Do not ask:  
Which deck has more synergy with the card?  
Evaluate:  
1. contribution with the card;  
2. best state without it;  
3. replacement scarcity;  
4. bottleneck relief;  
5. module criticality;  
6. resilience effect;  
7. identity or experiential significance;  
8. floor risk;  
9. other copies;  
10. global transaction opportunities.  
Suggested arbitration record:  
```
contested_card:
  card:
  copies_available:
  regime:

  claimants:
  current_custodian:

  claimant_profiles:
    - configuration:
      contribution_with_card:
      best_without_card:
      replacement_scarcity:
      bottleneck_effect:
      identity_importance:
      floor_effect:

  direct_arbitration:
  exchange_routes:
  shared_module_option:

  recommended_custody:
  confidence:

```
   
⸻  
   
## 17. SHARED MODULE DESIGNATION  
Permanent custody is sometimes the wrong question.  
A compact package may be designated as a **Shared Module** when:  
* multiple configurations benefit strongly from it;  
* those configurations are mutually exclusive in practice;  
* moving the package is manageable;  
* maintaining duplicate copies is unnecessary or impossible.  
```
shared_module:
  module_id:
  name:
  cards:
  physical_copy_ids:

  eligible_configurations:
  regime:

  insertion_requirements:
  cards_removed_when_inserted:
  mana_changes:
  module_changes:

  storage_method:
  switching_complexity:
  authoritative_home:

  protected_from_independent_use:

```
Example:  
```
Biomass Power Core

```
may contain five cards that move together between Dina-P and Necrobloom-P.  
The module should be treated as a unit during powered-build evaluation.  
Do not independently redistribute one member if doing so breaks the shared module unless the module itself is being revised.  
   
⸻  
   
## 18. SHARED-MODULE FOOTPRINT  
A shared module creates a different kind of cost:  
**configuration overhead**.  
Evaluate:  
* number of physical cards moved;  
* number of cuts restored when switching back;  
* sleeve compatibility;  
* token changes;  
* mana-base changes;  
* likelihood of assembly error;  
* bookkeeping burden;  
* whether the package remains coherent.  
A theoretically strong shared package may be undesirable if switching it requires rebuilding twenty cards.  
Shared modules should therefore have:  
```
switching_profile:
  cards_moved:
  cards_restored:
  mana_base_changes:
  bookkeeping_burden:
  physical_burden:
  error_risk:
  switch_frequency:

```
   
⸻  
   
## 19. PROTECTED ASSETS  
Portfolio optimization is constrained.  
Add protection levels:  
## HARD LOCK  
Do not move without explicit user override.  
Examples:  
* commander;  
* sentimental cards;  
* pristine precon components;  
* cards defining deck identity.  
## SOFT LOCK  
Movement is allowed only for a substantial gain.  
## PREFERENCE LOCK  
Movement is technically acceptable but carries experiential or organizational cost.  
## FREE  
No special custody preference.  
The existing protocol already treats aesthetic, thematic, play-pattern, power, acquisition, and fun requirements as legitimate DeckRequirements rather than noise.  
Portfolio optimization must preserve that principle.  
   
⸻  
   
## 20. DECK FLOOR  
Pure global maximization can produce unacceptable cannibalization.  
Therefore every protected or maintained configuration should have a **Deck Floor**.  
```
deck_floor:
  configuration:
  minimum_functional_coverage:
  minimum_identity_integrity:
  required_modules:
  required_play_pattern:
  minimum_resilience:
  minimum_mana_integrity:
  prohibited_losses:
  experiential_floor:

```
A proposed transaction that drops a maintained deck below its floor is rejected unless the user explicitly accepts that consequence.  
This prevents absurd results such as:  
Strip First Flight for eighteen useful cards because those cards improve stronger decks.  
The transaction might increase aggregate card efficiency while destroying a deck the user intentionally owns and wants preserved.  
That is not a portfolio improvement under the user’s actual requirements.  
   
⸻  
   
## 21. THREE-STAGE PORTFOLIO STANDARD  
Evaluate proposed reallocations in this order.  
## STAGE 1 — PRESERVE HARD CONSTRAINTS  
Reject transactions that violate:  
* physical ownership;  
* Commander legality;  
* color identity;  
* singleton requirements;  
* companion restrictions;  
* hard locks;  
* pristine-deck requirements;  
* simultaneous coexistence requirements.  
## STAGE 2 — PRESERVE DECK FLOORS  
Reject or escalate transactions that push a maintained configuration below its acceptable floor.  
## STAGE 3 — IMPROVE THE PORTFOLIO  
Within remaining feasible states, prefer allocations that improve:  
* bottleneck coverage;  
* module completeness;  
* route redundancy;  
* card quality;  
* resilience;  
* mana;  
* deck differentiation;  
* intended play experience;  
* aggregate expected contribution.  
This is **constrained portfolio optimization**, not raw maximization.  
   
⸻  
   
## 22. PORTFOLIO TRANSACTION CLASSES  
## PARETO IMPROVEMENT  
At least one deck improves and no affected maintained deck becomes meaningfully worse after replacement.  
These are the strongest portfolio recommendations.  
Example:  
```
Necrobloom + meaningful gain
Dina + neutral after replacement

```
## COMPENSATED PORTFOLIO IMPROVEMENT  
One or more decks decline slightly, remain safely above their floors, and another deck gains substantially more.  
Example:  
```
Necrobloom + large gain
Dina − small loss
Dina remains above required floor

```
This should be surfaced explicitly for user judgment.  
## REDISTRIBUTIVE IMPROVEMENT  
Aggregate performance changes little, but allocation improves:  
* deck differentiation;  
* thematic identity;  
* play-experience variety;  
* mechanical distinctness;  
* organizational simplicity.  
These may be good trades even without raw power gain.  
## NEUTRAL REALLOCATION  
No meaningful portfolio improvement.  
Avoid physical churn unless another user preference justifies it.  
## HARMFUL REALLOCATION  
Net portfolio loss or unacceptable floor violation.  
Reject.  
## UNCERTAIN  
Evidence is insufficient.  
Test or gather better data before permanent movement.  
   
⸻  
   
## 23. IDENTITY DIVERSITY  
Portfolio value may include **differentiation between decks**.  
Two individually strong decks can produce a weaker portfolio experience if both become mechanically similar.  
Evaluate:  
```
portfolio_diversity:
  play_pattern_overlap:
  signature_module_overlap:
  color_overlap:
  win_route_overlap:
  pacing_overlap:
  experiential_distinction:

```
A redistribution that moves a generically strong sacrifice payoff from one deck to another might slightly reduce aggregate power but substantially improve identity separation.  
That can be correct.  
Do not equate portfolio quality with homogeneous optimization.  
   
⸻  
   
## 24. POWER CONCENTRATION  
The inverse risk is overconcentration.  
If every scarce premium card migrates into one flagship deck, the portfolio may contain:  
* one extremely strong deck;  
* several hollowed-out shells.  
Track:  
```
power_concentration:
  strongest_configuration:
  scarce_card_share:
  unique_role_share:
  high-value_module_share:
  portfolio_imbalance:

```
No universal balance target is required.  
But the system should expose concentration when it materially changes the user’s collection.  
   
⸻  
   
## 25. REPLACEMENT CASCADE  
A replacement may itself be allocated.  
Example:  
```
Necrobloom requests Wight from Dina.

Dina's best replacement is X in Sharuum.

Sharuum's best replacement is Y in TMNT.

TMNT has a free substitute Z.

```
This creates:  
```
Free Z → TMNT
TMNT Y → Sharuum
Sharuum X → Dina
Dina Wight → Necrobloom

```
This is a **Replacement Cascade**.  
```
replacement_cascade:
  originating_claim:
  chain:
  terminal_source:
  affected_decks:

  final_state:
  per_deck_delta:
  portfolio_delta:

  weakest_link:
  uncertainty_propagation:

```
Do not stop replacement search merely because the first useful substitute is currently allocated.  
   
⸻  
   
## 26. EXCHANGE SEARCH  
For a contested card:  
1. identify the requesting deck’s gain;  
2. identify the current deck’s loss;  
3. search Free pool replacements;  
4. search unused owned copies;  
5. search functional replacements in other decks;  
6. search swaps;  
7. search short exchange cycles;  
8. test shared-module designation;  
9. compare final feasible states.  
Prefer low-complexity exchange structures when benefits are similar.  
A four-deck exchange that yields a marginal gain may not justify physical and bookkeeping burden.  
   
⸻  
   
## 27. TRANSACTION COMPLEXITY TAX  
Portfolio moves impose overhead.  
Add:  
```
transaction_complexity:
  decks_touched:
  cards_moved:
  modules_rebuilt:
  lands_changed:
  sleeve_or_storage_changes:
  bookkeeping_required:
  reversibility:
  error_risk:
  user_effort:

```
All else being equal:  
```
simple Pareto improvement
>
complex Pareto improvement
>
complex marginal improvement

```
Complexity has no independent value.  
This follows the base protocol’s governing principle that usefulness matters more than elaboration.  
   
⸻  
   
## 28. ALLOCATION STABILITY  
Do not churn cards endlessly between decks because tiny evaluation differences change.  
Use a **movement threshold**.  
A currently reasonable allocation should remain stable unless:  
* a new card enters the collection;  
* a deck’s requirements change;  
* a bottleneck is discovered;  
* testing changes expected contribution;  
* a new configuration becomes important;  
* a clearly superior replacement appears;  
* the user intentionally reprioritizes decks.  
This prevents portfolio analysis from becoming hypersensitive to small speculative deltas.  
   
⸻  
   
## 29. ACQUISITION AS AN ALLOCATION SOLUTION  
When permitted by the user’s acquisition constraints, an additional copy may be evaluated as an alternative to redistribution.  
```
acquisition_option:
  card:
  additional_copy_needed:
  cost:
  availability:
  user_acquisition_preference:
  conflicts_resolved:
  avoided_source_loss:

```
But acquisition should not be silently recommended when the construction scope is owned-only.  
The base protocol explicitly prohibits recommending acquisition when the scope does not allow it.  
   
⸻  
   
## 30. ALLOCATION ABLATION  
Extend ablation analysis across the portfolio.  
## COPY ABLATION  
Ask:  
If this physical copy vanished from the collection entirely, which decks meaningfully degrade?  
This reveals globally scarce cards.  
## DECK ABLATION  
Temporarily remove one deck from the coexistence regime.  
Ask:  
Which contested cards cease to be contested?  
This is useful for event-specific loadouts.  
## SHARED-MODULE ABLATION  
Remove a shared package.  
Ask:  
Which powered configurations lose coherence, and what independent states remain?  
   
⸻  
   
## 31. PORTFOLIO BOTTLENECKS  
Common portfolio bottlenecks include:  
* one copy of a uniquely important bridge;  
* too few sacrifice outlets across several decks;  
* insufficient graveyard recursion across multiple black decks;  
* one premium fixing land claimed by several five-color shells;  
* duplicated demand for the same protection card;  
* too few functional replacements for a role;  
* excessive concentration of flexible multirole cards;  
* protected precon copies removing otherwise useful inventory;  
* too much dependence on one shared Power Core;  
* too much physical switching overhead.  
A portfolio bottleneck is not necessarily a deck bottleneck.  
One deck may have adequate removal while the collection has insufficient removal to support four simultaneously assembled decks.  
   
⸻  
   
## 32. PORTFOLIO REDUNDANCY  
Extend redundancy beyond individual decks.  
## COPY REDUNDANCY  
Multiple physical copies exist.  
## FUNCTIONAL PORTFOLIO REDUNDANCY  
Several cards across the collection can fill the same role.  
## CONFIGURATION REDUNDANCY  
A deck can remain functional through several alternative builds.  
## SHARED-MODULE REDUNDANCY  
Multiple modules can serve the same powered role.  
## ALLOCATION REDUNDANCY  
Several feasible assignments produce roughly equivalent portfolio outcomes.  
High allocation redundancy makes card custody flexible.  
Low allocation redundancy indicates a genuinely scarce portfolio asset.  
   
⸻  
   
## 33. PORTFOLIO CLAIM STRENGTH  
A claim becomes stronger when:  
* the card completes a critical module;  
* the card relieves a real bottleneck;  
* the deck lacks alternatives;  
* the source deck has good alternatives;  
* the card supplies several scarce roles simultaneously;  
* the commander or architecture strongly amplifies it;  
* removing it from the source does not damage identity;  
* the target remains within the active coexistence regime.  
A claim becomes weaker when:  
* the card merely adds another payoff to an oversupplied role;  
* several replacements exist;  
* the deck already has strong functional coverage;  
* the card’s synergy is high but activation probability is low;  
* another deck depends on it structurally;  
* the move damages a protected identity or deck floor.  
   
⸻  
   
## 34. CONTINGENT CLAIMS  
Some allocation claims depend on other portfolio changes.  
Example:  
```
Necrobloom strongly wants Card A
only if Card B is also included.

```
Represent:  
```
contingent_claim:
  card:
  requesting_configuration:
  dependency:
  claim_strength_if_met:
  claim_strength_if_unmet:

```
Do not move a card based on synergy that exists only in an unapproved future configuration.  
   
⸻  
   
## 35. PORTFOLIO STATE TRANSITIONS  
Maintain the same state discipline used by DeckState.  
A portfolio recommendation may be:  
```
proposed
approved
physically_completed
rejected
reverted
experimental

```
Do not update authoritative inventory allocations until the movement is confirmed.  
The base protocol already requires proposed and confirmed deck changes to remain separate.  
The portfolio layer extends that rule to interdeck movement.  
   
⸻  
   
## 36. PORTFOLIO EVALUATION PROCESS  
## PHASE 1 — ESTABLISH AUTHORITATIVE INVENTORY  
Verify:  
* owned counts;  
* physical copies;  
* deck locations;  
* Free pool;  
* protected copies;  
* unknown locations;  
* shared modules.  
## PHASE 2 — ESTABLISH ACTIVE CONFIGURATIONS  
Identify:  
* which decks matter;  
* which configurations matter;  
* which must coexist;  
* which are mutually exclusive.  
## PHASE 3 — IMPORT DECK REQUIREMENTS  
For each maintained configuration, import:  
* identity;  
* functional requirements;  
* core modules;  
* locked cards;  
* desired play pattern;  
* aesthetic constraints;  
* acceptable power;  
* acceptable floor.  
## PHASE 4 — IDENTIFY CONTESTED ASSETS  
Find cards where:  
```
simultaneous claims > physical copies

```
within the active regime.  
## PHASE 5 — BUILD CLAIMS  
For every meaningful claimant:  
* identify role;  
* identify outgoing target card;  
* evaluate target gain;  
* evaluate source loss;  
* build replacement set.  
## PHASE 6 — CALCULATE REPLACEMENT-ADJUSTED LOSS  
Use best feasible repair, not naked removal.  
## PHASE 7 — SEARCH TRANSACTIONS  
Search:  
* direct transfers;  
* swaps;  
* short exchange cycles;  
* replacement cascades;  
* shared-module options.  
## PHASE 8 — APPLY CONSTRAINTS  
Reject states violating:  
* legality;  
* hard locks;  
* coexistence;  
* deck floors;  
* protected identity.  
## PHASE 9 — COMPARE FEASIBLE STATES  
Compare:  
* per-deck deltas;  
* portfolio delta;  
* identity effects;  
* power concentration;  
* transaction complexity;  
* configuration overhead.  
## PHASE 10 — CLASSIFY RECOMMENDATION  
Return:  
* Pareto improvement;  
* compensated portfolio improvement;  
* redistributive improvement;  
* neutral;  
* harmful;  
* uncertain.  
## PHASE 11 — USER JUDGMENT  
Do not automatically execute compensated losses, identity trades, or major redistribution merely because aggregate contribution improves.  
## PHASE 12 — UPDATE STATE  
After confirmed movement:  
* update physical copy locations;  
* update authoritative deck lists;  
* update Free pool;  
* update shared modules;  
* clear resolved claims;  
* re-evaluate affected decks only.  
   
⸻  
   
## 37. LOCAL VERSUS GLOBAL OPTIMA  
A deck-local optimum may not be portfolio-optimal.  
Example:  
```
Ashling's best possible 100
+
Dina's best possible 100

```
may require several of the same unique physical cards.  
The correct portfolio state may use:  
```
Ashling's second-best implementation
+
Dina's best implementation

```
if Ashling loses very little while Dina loses substantially without the shared card.  
Likewise:  
```
best theoretical version of every deck

```
is not a physically realizable portfolio state.  
Portfolio analysis must distinguish:  
```
unrestricted deck optimum
physical portfolio optimum

```
   
⸻  
   
## 38. MARGINAL CONTRIBUTION OVER RAW POWER  
Do not award custody based on statements such as:  
```
"This is one of the strongest cards in Necrobloom."

```
Ask instead:  
```
"What does Necrobloom lose if it does not receive this card?"

```
A powerful but redundant card may have low marginal value.  
A modest bridge that repairs a unique bottleneck may have enormous marginal value.  
This follows the base protocol’s rule that a bottleneck-relieving bridge may be more valuable than another payoff added to an already oversupplied sink.  
   
⸻  
   
## 39. PORTFOLIO REQUEST TYPES  
Users may invoke the layer with requests such as:  
## CLAIM REQUEST  
Does Necrobloom have a stronger claim to Wight of the Reliquary than Dina?  
## TRANSFER REQUEST  
What happens if Wight moves from Dina to Necrobloom?  
## REPLACEMENT REQUEST  
If Necrobloom takes Wight, what should Dina receive?  
## COLLISION REQUEST  
Which cards are contested between my eight assembled decks?  
## REBALANCE REQUEST  
Can these decks be improved by reallocating cards among them?  
## SHARED-MODULE REQUEST  
Which cards should become part of a Power Core?  
## PORTFOLIO OPTIMIZATION REQUEST  
Given my current collection, find reallocations that improve multiple decks without weakening any below their intended level.  
## EVENT LOADOUT REQUEST  
I’m bringing Ashling, Dina, Rootha, TMNT, and Sharuum tonight. Reconcile physical collisions for those five only.  
   
⸻  
   
## 40. STANDARD PORTFOLIO OUTPUT  
A complete portfolio analysis should return:  
## A. PORTFOLIO SNAPSHOT  
* inventory version;  
* active decks;  
* active configurations;  
* allocation regime;  
* protected decks;  
* Free pool confidence.  
## B. CURRENT COLLISIONS  
* contested cards;  
* number of copies;  
* claimant decks;  
* current custody.  
## C. HIGH-VALUE CLAIMS  
For each major claim:  
* requested role;  
* target gain;  
* source naked loss;  
* source replacement-adjusted loss;  
* claim strength.  
## D. REPLACEMENT MAP  
* best Free-pool replacements;  
* replacements held in other decks;  
* replacement cascades.  
## E. TRANSACTION OPTIONS  
* transfers;  
* swaps;  
* exchange cycles;  
* shared-module options.  
## F. DECK FLOOR CHECKS  
* decks improved;  
* decks weakened;  
* floor violations;  
* identity impacts.  
## G. PORTFOLIO EFFECT  
* Pareto;  
* compensated;  
* redistributive;  
* neutral;  
* harmful;  
* uncertain.  
## H. PHYSICAL MOVEMENT PLAN  
Exact:  
```
OUT / IN
source / destination
copy identity
configuration affected

```
## I. STATE STATUS  
* proposed;  
* confirmed;  
* experimental.  
## J. REMAINING QUESTIONS  
* uncertain ownership;  
* uncertain Oracle metadata;  
* performance assumptions needing testing.  
   
⸻  
   
## 41. COMPACT TRADE OUTPUT  
For smaller decisions:  
```
portfolio_trade:
  requested_card:
  source:
  destination:
  regime:

  destination_gain:
  source_replacement:
  replacement_adjusted_source_loss:

  portfolio_effect:
  deck_floor_status:
  identity_effect:
  complexity:

  classification:
  confidence:

```
   
⸻  
   
## 42. ANTI-GUTTING CHECK  
Before approving a transfer, ask:  
* Is the source deck still coherent?  
* Did it lose a signature module?  
* Did it lose a unique function?  
* Does the replacement actually preserve that function?  
* Did redundancy collapse?  
* Did the move create a new mana or curve problem?  
* Did the deck fall below its intended power or experiential floor?  
* Is the destination receiving a meaningful improvement or merely another strong card?  
* Is the source being harvested because it is less powerful rather than because the transfer is actually appropriate?  
* Is a shared-module configuration a better solution?  
   
⸻  
   
## 43. ANTI-HOARDING CHECK  
The opposite failure also exists.  
A deck should not retain a card merely because:  
* it currently owns it;  
* it once used it;  
* it has synergy with it;  
* removing it feels like weakening the deck in isolation.  
Ask:  
* Is the role redundant?  
* Is the card replaceable?  
* Does another deck have a more scarce use?  
* Would release create a larger portfolio improvement?  
* Can this deck remain at or above its intended floor?  
Historical custody does not create permanent entitlement.  
   
⸻  
   
## 44. ANTI-SYNERGY-COUNT CHECK  
Never award a contested card because one deck has more graph edges.  
The ontology explicitly separates connectivity from value.  
Portfolio arbitration should consider:  
```
verified usefulness
× activation likelihood
× scarcity
× module consequence
× replacement scarcity

```
not:  
```
number of interactions

```
   
⸻  
   
## 45. ADVERSARIAL TESTS  
A conforming portfolio evaluator should correctly handle:  
* one copy claimed by two simultaneously assembled decks;  
* two mutually exclusive powered decks sharing one copy without false collision;  
* a pristine precon refusing to donate a generically strong card;  
* a flashy card staying in a deck because no replacement exists;  
* a flashy card moving because its current role is highly redundant;  
* a source deck losing a card but becoming equal or stronger after replacement;  
* a three-deck exchange outperforming every direct transfer;  
* a Free-pool card unlocking a replacement cascade;  
* a shared five-card module being better than permanent custody;  
* aggregate strength increasing while one deck falls below its protected floor;  
* a mathematically favorable trade being rejected because it destroys deck identity;  
* a power-neutral redistribution improving portfolio diversity;  
* a theoretical allocation requiring the same physical card in two simultaneous configurations being rejected;  
* two copies of the same card being treated as separate physical resources;  
* uncertainty in ownership preventing a strong claim;  
* a move being recommended only provisionally until physically confirmed.  
   
⸻  
   
## 46. MINIMUM USEFUL PORTFOLIO ANALYSIS  
If time or data is limited:  
1. Establish active allocation regime.  
2. Verify contested physical copies.  
3. Compare each claimant’s marginal contribution.  
4. Find the source deck’s best realistic replacement.  
5. Reject moves that violate hard constraints or deck floors.  
6. Recommend only clear replacement-adjusted improvements.  
Everything beyond this should justify its analytical cost.  
   
⸻  
   
## 47. RELATIONSHIP TO KAIROS–GATE  
The full architecture becomes:  
```
Owned Physical Inventory
        ↓
MTG Deck Interaction Ontology
        ↓
Deck Building & Evaluation Protocol
        ↓
Inventory-First Construction
        ↓
Portfolio Allocation & Trade Requests
        ↓
Selected Deck Configuration
        ↓
Kairos–GATE Operational Doctrine
        ↓
Actual Play
        ↓
Observed Results
        ↓
Deck and Portfolio Revision

```
The layers answer different questions.  
**Interaction Ontology**  
What can these cards and modules do?  
**Deck Evaluator**  
How good and appropriate are they in this deck?  
**Inventory-First Construction**  
What coherent deck can this owned inventory produce?  
**Portfolio Allocation**  
Where should scarce physical cards and modules live across all maintained decks?  
**Kairos–GATE**  
Given the deck and current game state, what should the player do now?  
Do not collapse these questions into a single optimization system.  
   
⸻  
   
## 48. GOVERNING STANDARDS  
A successful portfolio evaluator should answer:  
* Which physical cards are genuinely scarce?  
* Which collisions are real under the active coexistence regime?  
* Which apparent collisions disappear under exclusive configurations?  
* Which deck has the strongest replacement-adjusted claim?  
* What does the source deck actually lose after repair?  
* Can a swap solve the conflict?  
* Can an exchange cycle improve all participants?  
* Can a Free-pool card unlock a cascade?  
* Should the card instead belong to a Shared Module?  
* Does any maintained deck fall below its acceptable floor?  
* Does the movement damage deck identity?  
* Does the result improve portfolio diversity or create excessive homogenization?  
* Is physical switching complexity justified?  
* Is the proposed state actually realizable with owned copies?  
* Has the change been proposed, or physically completed?  
The final standard is not:  
```
maximum card strength

```
nor:  
```
maximum total synergy

```
nor:  
```
maximum sum of isolated deck scores

```
The final standard is:  
**Given the physical collection and the decks the user actually cares about maintaining, does this allocation produce a more useful, coherent, resilient, and enjoyable portfolio of playable configurations?**  
   
⸻  
   
## 49. QUICK USE INSTRUCTION  
Use MTG Deck Interaction Ontology v2.0 plus v2.1, Deck Building and Evaluation Protocol v1.0 plus v1.1, and this Portfolio Allocation addendum.  
Begin by identifying:  
```
physical inventory
+
active configurations
+
allocation regime
+
protected assets
+
deck floors

```
Then:  
```
find contested cards
→ build claims
→ calculate target gain
→ search source replacements
→ calculate replacement-adjusted loss
→ search swaps and exchange cycles
→ test shared-module alternatives
→ enforce constraints and deck floors
→ compare feasible final portfolio states

```
Prefer:  
```
Pareto improvement

```
over compensated loss,  
and prefer:  
```
simple realizable improvement

```
over elaborate marginal optimization.  
Do not silently move cards.  
Do not confuse card names with physical copies.  
Do not treat historical custody as permanent entitlement.  
Do not gut functioning decks to improve stronger ones.  
Do not preserve weak allocations merely because they are already assembled.  
Do not evaluate a transfer without repairing the source deck.  
Do not evaluate an exchange cycle edge-by-edge when the final joint state is what matters.  
Do not optimize away identity, aesthetics, play experience, or intended deck diversity.  
   
⸻  
   
## 50. CORE PORTFOLIO DOCTRINE  
**A scarce card belongs where its absence is hardest to repair, not necessarily where its presence looks most spectacular.**  
**Evaluate the deck that receives the card and the deck that survives without it.**  
**Replacement-adjusted loss matters more than naked loss.**  
**A card may be unavailable locally but available through a global exchange.**  
**Physical conflicts exist only among configurations that must coexist.**  
**Some cards should have permanent homes. Some should belong to modules.**  
**Protect deck floors before optimizing portfolio ceilings.**  
**Prefer Pareto improvements. Expose compensated losses.**  
**Optimize the portfolio the user wants, not an imaginary collection of maximally cannibalized decks.**  
**Track copies, configurations, and transactions as state—not as assumptions.**  
**Local opportunity cost can be global.**  
   
⸻  
   
## 51. FINAL COMPRESSION  
For any contested card:  
```
WHO WANTS IT?
↓
WHAT DOES IT FIX?
↓
WHAT LEAVES THERE?
↓
WHAT BREAKS WHERE IT CAME FROM?
↓
WHAT BEST REPLACES IT?
↓
CAN AN EXCHANGE DO BETTER?
↓
DO ALL DECKS REMAIN ABOVE FLOOR?
↓
IS THE FINAL PHYSICAL STATE REALIZABLE?

```
Or, in compact form:  
**CLAIM → REPLACE → CASCADE → CONSTRAIN → COMPARE → ALLOCATE**  
That is the portfolio layer.  
