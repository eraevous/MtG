**MTG DECK INTERACTION ONTOLOGY v3.1.1 — ADDENDUM**  
  
**Date: 2026-10-09**  
**Base: MTG Deck Interaction Ontology v3.1.1 (2026-10-06)**  
**Status: Compatible addendum; no primitive relation is added and no existing primitive changes meaning.**  
**Purpose: Preserve and normalize the interaction findings developed after v3.1.1, especially object/reference semantics, face-down masking, replacement composition, and contextual resource flow.**  
  
  
  
**0. WHY THIS ADDENDUM EXISTS**  
  
V3.1.1 survived a broad adversarial pass unusually well. The new material did not reveal a need for an Aristocrats, Blink, Haunt, Morph, Fuel, Storm, or other mechanic/archetype primitive. Instead, the failures and near-failures clustered around a small set of deeper abstractions that recur across many mechanics.  
  
This addendum consolidates those abstractions after a second pass over the discussion rather than preserving the discussion itself. Conversational scaffolding, false starts, overly broad analogies, and claims already expressible by V3.1.1 are collapsed back into the existing model. Only distinctions that change a connection, prevent a false inference, or expose a recurring architecture are promoted.  
  
The major findings are:  
  
	1.	**Predicates are checkpoint-local; references are not predicates.** A quality used to select or name an object need not remain true for a reference to keep pointing to that object.  
	2.	**Event identity is separate from subject qualification.** dies, leaves, enters, sacrifice, and similar events are identified first; creature/token/nontoken/artifact/etc. predicates are then evaluated at the checkpoint required by the listener.  
	3.	**Card/substrate continuity and game-object continuity are different relations.** Blink keeps the card lineage while replacing the game object.  
	4.	**Face-downness is a characteristic mask, not object replacement.** The same object continues while a rules-defined copiable interface substitutes for its ordinary characteristics.  
	5.	**Some rules/effects may track a successor object across a zone change even though the successor is not the same game object.** Identity and traceability must not be conflated.  
	6.	**Multiple replacement effects compose iteratively.** One applicable replacement is selected and applied, then applicability is reevaluated against the rewritten event.  
	7.	**Random branch selection is not player choice.** V3.1.1 needs a small stochastic branch description for mechanically random architectures.  
	8.	**Feedstock is a derived contextual role, not an intrinsic card type.** Consumption engines require typed, rate-bearing, network-dependent stock, and the quality of that stock depends on its future transitions and opportunity cost.  
	9.	**Resource-flow analysis is conditional.** It is a diagnostic lens for architectures that actually consume/recycle constrained stock, not a global objective function for decks.  
	10.	**Community archetype vocabulary is an external acceptance corpus.** The ontology must be at least expressive enough to reconstruct useful folk distinctions, but those labels are not imported into the ontology.  
  
These conclusions preserve the V3.1.1 governing principle: **make strange machines discoverable without making ordinary cards complicated.**  
  
  
  
**1. PREDICATE LOCALITY AND REFERENCE CONTRACTS**  
  
**1.1 Core rule: a predicate belongs to the checkpoint that tests it**  
  
A statement such as “target creature,” “that creature,” “equipped creature,” “attacking creature,” or “nontoken creature that died” contains one or more predicates, but those predicates do not automatically become permanent facts about the object.  
  
Use the general form:  
  
[  
P(x,S,t,c)  
]  
  
where:  
  
	●	x is the object;  
	●	S is the relevant game state;  
	●	t is the time or event snapshot;  
	●	c is the checkpoint at which the predicate is tested.  
  
A predicate true at targeting is not assumed true at resolution, departure, damage, or a later delayed trigger unless the later operation tests it again.  
  
**Doctrine:**  
  
> A predicate is authoritative only at the operation/checkpoint that actually tests it.  
  
This is a refinement of V3.1.1 requirement_group.checkpoint; it does not add a new primitive.  
  
**1.2 A reference is not the predicate that originally selected its referent**  
  
A relationship can be established because an object satisfies a predicate at binding time and continue after that predicate stops being true.  
  
Example shape:  
  
binding checkpoint:  
  
    choose object X such that creature(X) = true  
  
establish:  
  
    reference R -> X  
  
later:  
  
    creature(X) = false  
  
possible result:  
  
    R still -> X  
  
Whether the reference persists depends on the rules/effect defining the relationship, not on the noun used to describe the object when the relationship was created.  
  
This is the pattern behind:  
  
	●	Haunt referring to “the creature it haunts” even if the object stops being a creature;  
	●	delayed effects referring to “this creature” or “that creature” after a characteristic change;  
	●	links to exiled cards;  
	●	designations and tracked effects that bind a particular object;  
	●	attachments, where the opposite result can occur because continuing attachment legality *does* impose a persistence predicate.  
  
The important contrast is:  
  
HAUNT-LIKE LINK  
  
binding predicate:      creature  
  
continuing requirement: same referent, unless rule says otherwise  
  
EQUIPMENT ATTACHMENT  
  
binding predicate:      legal attachable object  
  
continuing requirement: attachment remains legal  
  
The same loss of creature can therefore leave one relationship intact and terminate another.  
  
**1.3 Reference Contract — derived, not stored as a new top-level record**  
  
For any state.kind: link, tracked_effect, attachment, designation, or delayed effect where this distinction matters, derive a **Reference Contract from existing records:**  
  
reference_contract:              # DERIVED VIEW  
  
  referent:  
  
  binding:  
  
    operation:  
  
    predicate:  
  
    checkpoint:  
  
  persistence_condition:  
  
  read:  
  
    operation:  
  
    predicate:  
  
    checkpoint:  
  
  successor_tracking:  
  
    mode: same_instance | authorized_successor | none  
  
    authority: rule | effect | null  
  
Its fields come from:  
  
	●	the creating operation and its requirement groups;  
	●	the resulting state.kind: link | tracked_effect | attachment | designation;  
	●	the state’s condition and persistence;  
	●	later operations that interpret/read the state;  
	●	any explicit rule/effect that authorizes tracking after a zone transition.  
  
Do not store a second copy where the information is already present.  
  
**1.4 Event identity and subject qualification are separate**  
  
V3.1.1 already says one event can expose several facets. This addendum sharpens the ordering:  
  
	1.	identify the event;  
	2.	identify its subject/referent;  
	3.	evaluate any listener-specific predicates at the required snapshot.  
  
For DIO, permanent.dies is the zone-change event defined by current rule 700.4: battlefield → graveyard. The identifier itself does **not encode creature = true. A listener for “a creature dies” is represented as:**  
  
permanent.dies  
  
  [object_filter: creature]  
  
  [evaluation_time: pre_departure]  
  
A listener for “a nontoken creature dies” adds nontoken. A listener for “an artifact dies” adds artifact. A generic dies listener has no such type qualifier.  
  
This matters because the same underlying transition can satisfy one observer and fail another.  
  
**Haunt / reverted-object acceptance example**  
  
Current rule 702.55b explicitly says the phrase “creature it haunts” continues to mean the object targeted by Haunt regardless of whether that object is still a creature. Rule 700.7 states the same general principle for “this [something]” references. Therefore:  
  
Haunt establishes R -> X while X is a creature  
  
X later ceases to be a creature  
  
R still -> X  
  
X goes battlefield -> graveyard  
  
DIO should expose the dies event from the transition and then let each observer test its own type predicates. It must not silently smuggle the old creature binding predicate into the departure snapshot, nor silently delete the reference because the predicate changed. Consequently, two observers of the same death may legitimately disagree about applicability: one may care only that the anchored object died, while another may additionally require that the dying object was a creature immediately before departure.  
  
The general lesson is more important than the card-specific interaction:  
  
> **References persist according to reference rules; predicates are re-evaluated according to listener checkpoints.**  
  
  
  
**2. OBJECT IDENTITY REFINED: SUBSTRATE, INCARNATION, VIEW, STATE**  
  
V3.1.1 correctly asks whether the same object continues, but post-v3.1.1 testing shows that the word “object” benefits from one further conceptual decomposition.  
  
**2.1 Four conceptual layers**  
  
These are conceptual layers, not four new top-level schemas.  
  
**1. Substrate / card lineage**  
  
The underlying physical card, token substrate, spell copy, card copy, etc. represented by object.substrate.  
  
For a physical card, this is what lets ordinary language say “the same card came back.”  
  
**2. Game-object incarnation**  
  
The current rules object represented by that substrate in its current zone.  
  
A zone change normally ends one incarnation and creates another. Current rule 400.7: an object that moves zones becomes a new object with no memory of or relation to its prior existence except for listed exceptions.  
  
**3. Active characteristic view**  
  
The current characteristics visible to ordinary game operations after copy effects, face-down rules, type/color/ability changes, and other continuous effects are applied.  
  
**4. Object-bound state and relationships**  
  
Counters, tapped status, damage, attachments, designations, links, tracked effects, capacities, permissions, history, and other V3.1.1 State.  
  
The compact conceptual formula is:  
  
Cards/substrates persist.  
  
Game objects incarnate.  
  
Characteristic views mutate.  
  
State attaches to an incarnation unless its scope says otherwise.  
  
**2.2 Same substrate does not mean same game object**  
  
Blink is the canonical case:  
  
physical card C  
  
battlefield:   incarnation C1  
  
      |  
  
      | exile  
  
      v  
  
exile:         incarnation C2  
  
      |  
  
      | return  
  
      v  
  
battlefield:   incarnation C3  
  
C1, C2, and C3 may share one physical card lineage while being different game objects.  
  
Therefore a blinked object normally loses:  
  
	●	counters;  
	●	damage;  
	●	tapped/untapped state;  
	●	attachments;  
	●	ordinary copy/type modifications;  
	●	tracked effects bound to the old incarnation;  
	●	historical/object state whose scope is object_instance.  
  
The returned incarnation receives fresh entry processing and fresh on-entry state.  
  
This is already the behavior encoded by the V3.1.1 persistence table; the addendum makes the identity distinction explicit so that “same card” is never mistaken for “same object.”  
  
**2.3 Successor traceability is not object identity**  
  
Some rules/effects are specifically authorized to find the new object that an old object became after a zone change. That does **not make the two incarnations the same object.**  
  
Call this **successor traceability.**  
  
Examples in the Comprehensive Rules include effects and triggered abilities that explicitly find the new object after a zone move. Rule 603.6e is one example; rule 400.7 contains multiple exceptions of this family.  
  
When needed, add optional detail inside a state.kind: link | tracked_effect or the operation that performs the tracking:  
  
tracking:  
  
  mode: same_instance | authorized_successor  
  
  authority: rule | effect  
  
  transition_scope:  
  
Open this detail only when cross-zone tracking changes a connection.  
  
**Doctrine:**  
  
> `same substrate`, `same game object`, and `effect can find successor` are three different propositions.  
  
**2.4 Characteristic change, face-down, phasing, and blink are now sharply separated**  
  
|Change                          |Substrate                          |Incarnation         |View                     |Object-bound state|  
|--------------------------------|-----------------------------------|--------------------|-------------------------|------------------|  
|ordinary characteristic mutation|same                               |same                |changed                  |kept by default   |  
|becomes a copy                  |same                               |same                |copied profile           |kept by default   |  
|turns face down/up              |same                               |same                |masked/unmasked          |kept by default   |  
|phases out/in                   |same                               |same                |ordinarily kept          |kept              |  
|blink                           |same physical card where applicable|**new**             |rebuilt                  |lost by default   |  
|bounce/recast                   |same physical card where applicable|**new** across moves|rebuilt; real cast occurs|lost by default   |  
  
This distinction should be used before introducing any mechanic-specific explanation.  
  
  
  
**3. FACE-DOWNNESS AS CHARACTERISTIC MASKING**  
  
Face-down permanents expose a real representational gap in V3.1.1. The base model has state.kind: status = face-down and correctly treats turning face up as same-object persistence, but its characteristic language does not explicitly describe what rule 708 does.  
  
**3.1 Face-downness is not ordinary copy and not ordinary additive mutation**  
  
Current rule 708.2 says a face-down spell/permanent has no characteristics other than those specified by the rule/effect allowing it to be face down; those listed characteristics are its copiable values.  
  
Thus face-downness:  
  
	●	preserves the current game-object incarnation;  
	●	suppresses/replaces the ordinary active characteristic profile;  
	●	can provide a standard 2/2 colorless nameless, typeless-within-creature-subtype, abilityless profile when no other profile is specified;  
	●	makes that masked profile copiable;  
	●	preserves object-bound state unless another rule changes it;  
	●	may coexist with special permissions/history that inspect the underlying card to determine whether/how it may be turned face up.  
  
**3.2 Add mask as a characteristic operation**  
  
Amend the optional characteristic-effect vocabulary:  
  
characteristic_effect:  
  
  axis: name | color | type | subtype | supertype | ability | power_toughness  
  
  operation: set | add | remove | retain | copy | mask  
  
  value:  
  
  source:  
  
  duration:  
  
  condition:  
  
  copiable: true | false  
  
mask means:  
  
> A rule/effect substitutes a defined active/copiable characteristic profile for characteristics that remain true of the underlying substrate but are not available to ordinary characteristic queries while the mask applies.  
  
Face-down rules are the primary current use. Do not use mask merely because an effect sets several characteristics at once. If a face-down permanent becomes a copy of another object, the copied values can change underneath the mask while the active face-down profile remains the one ordinary queries see; turning it face up can then expose the copied values. This is the kind of case mask is meant to preserve.  
  
**3.3 Hidden substrate information and permissions**  
  
Two face-down 2/2 permanents can have identical active characteristics while having different legal future operations because of how they became face down and what card lies underneath.  
  
Examples include:  
  
	●	Morph/disguise-like turn-up permissions;  
	●	manifest/manifest-dread style permissions that inspect the underlying card;  
	●	generic “turn target permanent face down” effects that may confer no inherent turn-up route.  
  
Therefore:  
  
same active view  
  
!=  
  
same underlying substrate  
  
!=  
  
same permission set/history  
  
The hidden substrate is not a second public characteristic profile. It is information consulted only by operations/rules authorized to inspect it.  
  
**3.4 Turning face up versus reinstantiation**  
  
Current rule 708.8 confirms that turning a face-down permanent face up:  
  
	●	keeps the same permanent/game object;  
	●	restores its normal copiable values;  
	●	preserves effects already applied to that permanent;  
	●	does not create an entry event.  
  
Blinking a face-down permanent is different:  
  
face-down incarnation C1 leaves  
  
C1 ends  
  
new incarnation C2/C3 is created through zone changes  
  
If it returns face up, no turn_face_up event occurred. The face-down object did not become face up; it ceased to exist and another incarnation entered.  
  
This is a canonical acceptance test for mask versus new_object.  
  
  
  
**4. ITERATIVE REPLACEMENT COMPOSITION**  
  
V3.1.1 correctly models an individual replacement as:  
  
proposed event -> resulting event  
  
That is insufficient when several replacement/prevention effects can affect the same event.  
  
Current rule 616.1 requires an iterative process: choose/apply an applicable effect according to the rule’s priority/chooser rules, rewrite the event, then reevaluate which effects are applicable to the modified event. Rule 616.2 explicitly allows one replacement to make another become applicable.  
  
**4.1 Replacement Composition Protocol**  
  
This is execution doctrine, not a new primitive relation:  
  
E0 = proposed event  
  
while applicable replacement/prevention effects remain:  
  
    determine applicable set A(Ei)  
  
    select one effect according to rule/effect ordering  
  
    apply it once  
  
    Ei+1 = rewritten event  
  
    reevaluate applicability against Ei+1  
  
final event = En  
  
Record order/choice only when it changes a deck-relevant connection.  
  
**4.2 Why this matters**  
  
Without iterative composition, an analyzer can falsely assume that:  
  
	●	every initially applicable replacement happens;  
	●	replacements commute;  
	●	a later replacement sees the original event rather than the rewritten one;  
	●	one replacement cannot enable or disable another.  
  
This is the gap exposed by counter/token/event modification chains such as the Earth Crystal/Michelangelo-style interaction discussed during testing.  
  
No new relation is needed. replacement remains an Operation kind and rewrites remains its result. The missing element is the composition protocol.  
  
  
  
**5. RANDOM BRANCH SELECTION**  
  
The community-archetype corpus exposed one small mechanical gap through Chaos/randomness decks.  
  
V3.1.1 choice correctly models a player choosing among legal branches. Random selection is not a choice and should not be encoded as one merely to reuse the schema.  
  
Add an optional process detail, opened only where randomness changes connectivity:  
  
random_selection:  
  
  population:  
  
  sample_size:  
  
  distribution: uniform | specified | unknown  
  
  with_replacement:  
  
  public_or_hidden:  
  
  branch_outputs:  
  
This records the mechanical selector, not expected-value analysis. Probabilities need not be computed unless another layer requests them.  
  
**Doctrine:**  
  
> player choice, opponent choice, deterministic rule selection, and random selection are different branch selectors.  
  
  
  
**6. CONTEXTUAL RESOURCE FLOW AND FEEDSTOCK**  
  
This is the largest extension in the addendum and the one most directly motivated by actual deck behavior.  
  
V3.1.1 already represents PRODUCES, CONSUMES, resource hooks, population, recursion, cadence, module limiting resources, contention, and resource lifecycle. What it lacks is a derived view that asks whether **qualified stock appears at the rate and in the states required by a consuming architecture.**  
  
**6.1 Feedstock is a contextual derived role**  
  
Add feedstock to the list of derived roles in section 9.  
  
Definition:  
  
> **Feedstock:** an object or resource state positioned upstream of a consuming/transition operation and mechanically usable by that route. Feedstock *quality* is contextual and depends on the opportunity cost and transition value exposed to evaluation.  
  
Feedstock is never an intrinsic tag on a card.  
  
The same ETB creature can be:  
  
	●	ordinary battlefield value in a deck with no replay route;  
	●	sacrifice feedstock in an Aristocrats engine;  
	●	reciprocal working stock in a graveyard/battlefield oscillator;  
	●	reanimation stock once in the graveyard;  
	●	combat stock when attacking/blocking is expected to kill it.  
  
Therefore:  
  
> **Role follows reachable network topology.**  
  
**6.2 Fuel/feedstock is typed, not fungible**  
  
A generic “creature fuel pool” is a false abstraction.  
  
Consumption and payoff operations may require:  
  
	●	token or nontoken;  
	●	card or noncard;  
	●	creature/artifact/land or combinations;  
	●	controller/owner restrictions;  
	●	another/self;  
	●	subtype/color/name restrictions;  
	●	battlefield object versus durable graveyard card;  
	●	attacking/blocking/tapped/untapped state;  
	●	a destination or history condition.  
  
The same body can satisfy a generic sacrifice outlet but fail a nontoken creature dies payoff or fail to become reusable graveyard stock because it was a token.  
  
A flow path is valid only when qualifiers match **all the way through the chain:**  
  
qualified feedstock  
  
      -> compatible sink/process  
  
      -> actual event bundle  
  
      -> qualified listener/payoff  
  
      -> resulting stock/state  
  
This reuses the V3.1.1 qualifier discipline; it does not create a second compatibility system.  
  
**6.3 Stock count and supply rate are different**  
  
A census of “token makers” or “recursive creatures” is not enough.  
  
Distinguish source modes:  
  
|Supply mode                 |Meaning                                                                                                |  
|----------------------------|-------------------------------------------------------------------------------------------------------|  
|**one_shot / burst**        |produces finite stock once unless the source itself is replayed                                        |  
|**autonomous**              |produces on its own clock once established; no same-resource seed required                             |  
|**conditional_exogenous**   |requires an external event/action not itself supplied by the stock being produced                      |  
|**conditional_endogenous**  |requires the same resource/event family it claims to replenish — “fuel that depends on fuel”           |  
|**regenerative**            |consumed stock returns itself or becomes usable again                                                  |  
|**self_replacing**          |consuming one unit produces replacement stock                                                          |  
|**reciprocal / oscillating**|existing stock alternates among states so another consumable unit is recreated without net new material|  
  
A deck with five autonomous repeatable sources is not equivalent to a deck with five producers that each require another creature to die first.  
  
**6.4 Spend economics: why some feedstock is better than other feedstock**  
  
The ontology should expose structural facts that let the evaluator estimate opportunity cost.  
  
Especially important classes/facts are:  
  
	●	**doomed:** scheduled to leave, die, sacrifice, or be exiled anyway;  
	●	**surplus:** currently contributes little unique ongoing value relative to available substitutes;  
	●	**regenerative/recurring:** can return after consumption;  
	●	**self-replacing:** consumption creates replacement stock;  
	●	**exit-positive:** has dies/LTB/sacrifice value of its own;  
	●	**destination-positive:** being in the graveyard/exile/hand is itself useful because of recursion, flashback-like permissions, graveyard counts, reanimation, etc.;  
	●	**invested:** carries counters, attachments, unique engine function, or other valuable state that consumption destroys.  
  
Only the structural facts belong in DIO. Whether their net trade is “worth it” belongs to evaluation.  
  
Structurally favorable feedstock is often already doomed. A temporary token/copy scheduled to disappear at end step can frequently be sacrificed first at little incremental cost, converting unavoidable loss into useful sacrifice/death/LTB events; the evaluator still decides whether that line is actually preferable in context.  
  
**6.5 Departure source is part of the route**  
  
Not every death/LTB chain is powered by a sacrifice outlet.  
  
Potential transition sources include:  
  
	●	deliberate sacrifice;  
	●	combat attrition from attacking;  
	●	combat attrition from blocking;  
	●	scheduled sacrifice/exile/destruction;  
	●	self-destruction;  
	●	opponent removal;  
	●	state-based consequences;  
	●	bounce/blink/exile where the receiver wants LTB rather than death;  
	●	other forced transitions.  
  
These produce different event bundles even when the destination is similar. A sacrifice payoff, dies payoff, LTB payoff, and graveyard-stock consumer therefore see different subsets of the flow.  
  
**6.6 Transition yield**  
  
A unit of feedstock can produce more than one useful output while moving through a process.  
  
For a nontoken creature card sacrificed from battlefield to graveyard, possible outputs include:  
  
sacrifice  
  
battlefield.leave  
  
dies  
  
graveyard.enter  
  
durable creature-card stock in graveyard  
  
its own LTB/dies text  
  
external listeners  
  
If the process simultaneously returns another creature from the graveyard, the activation can additionally produce:  
  
graveyard.leave  
  
battlefield.enter  
  
ETB / as-enters processing  
  
fresh battlefield feedstock for a later cycle  
  
Define **transition yield as the qualified event/resource/state bundle exposed by processing one unit of stock through a route.**  
  
This is derived from operations and event facets, not stored independently on the card. Resource-flow analysis is not limited to creature bodies; the same view can be opened for mana, cards, counters, land-play capacity, artifacts, or other finite/replenishing stock when doing so changes the answer.  
  
**6.7 Reciprocal oscillators / working stock**  
  
The Cauldron-style pattern discussed in testing is not ordinary one-way fuel consumption.  
  
Generic form:  
  
[  
(A_{BF}, B_{GY}) \rightarrow (A_{GY}, B_{BF})  
]  
  
followed later by:  
  
[  
(A_{GY}, B_{BF}) \rightarrow (A_{BF}, B_{GY})  
]  
  
The stock is largely conserved while objects alternate between states. Each edge can emit useful hooks: sacrifice, death, LTB, graveyard entry/leave, ETB, and card-specific effects.  
  
Call this a **reciprocal transition oscillator.**  
  
The creatures/cards in such a loop are often better described as **working stock than expendable fuel: they circulate through states while the engine harvests transition events.**  
  
After bootstrap, the limiting resource may shift away from bodies to:  
  
	●	tap/untap capacity;  
	●	mana;  
	●	once-per-turn capacity;  
	●	access to legal graveyard targets;  
	●	timing windows.  
  
This is why a module can be mechanically complete yet have a moving bottleneck.  
  
**6.8 Resource-flow derived view**  
  
Add a derived view, computed only for modules where finite stock or recycling materially constrains operation:  
  
resource_flow:                         # DERIVED VIEW  
  
  module_or_route:  
  
  resource_class:  
  
    required_predicates:  
  
    excluded_predicates:  
  
    relevant_zones:  
  
  supply:  
  
    burst_stock:  
  
    sources:  
  
      - operation:  
  
        output_profile:  
  
        quantity:  
  
        cadence:  
  
        mode: one_shot | autonomous | conditional_exogenous | conditional_endogenous | regenerative | self_replacing | reciprocal  
  
        prerequisites:  
  
        depends_on_same_resource:  
  
  consumers:  
  
    - operation:  
  
      accepted_profile:  
  
      consumption_mode:  
  
      capacity_or_nominal_demand:  
  
  transition_yield:  
  
    event_facets:  
  
    resulting_stock:  
  
    replacement_stock:  
  
    post_departure_access:  
  
  contention:  
  
    competing_consumers:  
  
    competing_nondestructive_uses:  
  
  cycle:  
  
    bootstrap_requirements:  
  
    replenishment_route:  
  
    limiting_resource_candidate:  
  
  evidence_quality:  
  
**Rate boundary**  
  
DIO can record/derive explicit cadence (each upkeep, once each turn, tap capacity, one-shot quantity) and structural dependencies. It should **not invent realized per-turn rates for contingent events without an evaluator/simulator.**  
  
Thus:  
  
	●	DIO answers **what can supply what, under what conditions, and on what nominal clock**;  
	●	DBEP/evaluation answers **whether that supply is sufficient for the deck’s purpose**;  
	●	simulation may estimate realized fodder/death/ETB throughput under draws and game states.  
  
This preserves the ontology/evaluation boundary.  
  
  
  
**7. RESOURCE FLOW IS A CONDITIONAL LENS, NOT THE PURPOSE OF A DECK**  
  
The Satisfactory/factory analogy was useful for discovering bottlenecks, recycling, typed flow, and oscillation, but it must not become the governing abstraction.  
  
The ultimate objective may be:  
  
	●	winning;  
	●	producing a particular play experience;  
	●	expressing a theme;  
	●	creating unusual interactions;  
	●	surviving or controlling a game;  
	●	attacking efficiently;  
	●	or simply having fun.  
  
A Gruul deck can have a coherent architecture as simple as:  
  
mana -> threat -> attack -> damage  
  
It does not become defective because it lacks a feedstock economy.  
  
**Goodhart guardrail:**  
  
> Analyze throughput only when throughput is a real constraint on the architecture being evaluated. Never substitute “maximize flow” for the deck’s actual purpose.  
  
This follows the V3.1.1 rule: open precision only when it changes the answer.  
  
  
  
**8. COMMUNITY ARCHETYPE VOCABULARY AS AN EXTERNAL ACCEPTANCE CORPUS**  
  
The community vocabulary — Aristocrats, Sacrifice, Spellslinger, Storm, Good Stuff, Tokens, Go Wide, Reanimator, Blink, Voltron, Stax, Eggs, Cheerios, Pod, Toolbox, Aikido, Rube Goldberg, and so on — is not imported into DIO.  
  
It is a **floor test for expressiveness.**  
  
For each external label, test:  
  
	1.	**Representation:** Can V3.1.1 + this addendum describe a canonical architecture without a bespoke field named after the label?  
	2.	**Distinction:** Can it separate that architecture from its nearest confusable neighbors?  
	3.	**Recoverability:** Given only the DIO structure, is enough information present to understand why a player would reasonably apply that label?  
  
The intended bidirectional experiment is:  
  
community label  
  
    -> independent structural test specification  
  
    -> DIO representation  
  
then hide the label  
  
DIO representation  
  
    -> recover plausible community label(s)  
  
The folk vocabulary is a **floor, not a ceiling. DIO should be able to describe architectures that lie between folk labels or have no established community name.**  
  
**8.1 Current corpus result**  
  
Companion file:  
  
MTG_DIO_v3.1.1_Community_Archetype_Acceptance_Corpus_v0.1.md  
  
Initial pass against the **frozen base V3.1.1, before this addendum: 89 vocabulary entries.**  
  
	●	67 PASS;  
	●	9 PASS* (structural pass, quantitative/evaluative adequacy requires another layer);  
	●	13 PARTIAL;  
	●	0 broad mechanical archetypes produced a total structural FAIL.  
  
The partials clustered around deeper abstractions rather than missing folk labels:  
  
	●	typed resource/feedstock flow and rate;  
	●	face-down characteristic masking;  
	●	substrate lineage vs object incarnation and successor traceability;  
	●	multiple replacement composition;  
	●	stochastic/random branches;  
	●	deliberate boundaries to strategic/evaluative/social concepts such as Tempo, Good Stuff, Battlecruiser, and Politics.  
  
This clustering is evidence in favor of the ontology’s abstraction level. This addendum is intended to close or materially narrow the mechanical gaps corresponding to feedstock/resource flow, face-down masking, identity/traceability, replacement composition, and random selection. The strategic/social boundaries remain boundaries. The corpus should be rerun against the amended model rather than assuming those PARTIAL results have automatically become PASS.  
  
  
  
**9. BOUNDARY FINDINGS: WHAT THIS ADDENDUM DOES NOT MOVE INTO DIO**  
  
**9.1 Strategic horizon and relative efficiency**  
  
Aggro, Midrange, Tempo, Rock, Zoo, Battlecruiser, Glass Cannon, and Good Stuff contain claims such as:  
  
	●	early/late relative to an expected game;  
	●	efficient relative to available alternatives;  
	●	resilient enough for a metagame;  
	●	standalone card quality;  
	●	clock preservation;  
	●	expected game horizon.  
  
DIO can describe the mechanical substrate — costs, combat routes, disruption, dependencies, recovery, failure domains — but the relative judgment belongs in DBEP/evaluation and sometimes Kairos.  
  
Do not add “aggro,” “tempo,” or “goodstuff” primitives merely to force complete label recovery.  
  
**9.2 Social/incentive state**  
  
Politics can involve mechanically representable choices, beneficiaries, targets, transfers, and opponent agency. Trust, bargaining, threat perception, and human incentive response belong in Kairos/social reasoning, not DIO.  
  
**9.3 Realized stochastic or gameplay rates**  
  
DIO may expose nominal cadence and random selectors. Monte Carlo frequency, draw probability, expected combat attrition, and realized fodder-per-turn belong in evaluators/simulators.  
  
  
  
**10. NEW AND REVISED ROUTE PATTERNS**  
  
These are derived patterns, not primitives.  
  
**10.1 Reference persistence / predicate decoupling**  
  
qualifying object selected  
  
-> persistent reference created  
  
-> object's qualifying characteristic changes  
  
-> reference survives if its own persistence condition survives  
  
-> later reader applies its own predicate at its own checkpoint  
  
**10.2 Characteristic masking**  
  
same object  
  
-> rules-defined mask substitutes active/copiable profile  
  
-> object-bound state/history/permissions persist  
  
-> remove mask / turn face up to expose normal copiable values  
  
**10.3 Reinstantiation through zone change**  
  
old incarnation  
  
-> zone transition  
  
-> new incarnation  
  
-> old object-bound state absent by default  
  
-> fresh entry if destination is battlefield  
  
Do not call this “turning face up,” “resetting the same object,” or other language that hides object replacement.  
  
**10.4 Harvest before expiry**  
  
doomed temporary object  
  
-> take available nondestructive uses  
  
-> deliberately consume before scheduled loss  
  
-> collect sacrifice/death/LTB/destination outputs  
  
-> scheduled loss has little or no remaining object to consume  
  
**10.5 Reciprocal transition oscillator**  
  
A in state/zone X + B in state/zone Y  
  
-> consume/transition A  
  
-> redeploy B into X  
  
-> later consume/transition B  
  
-> redeploy A into X  
  
-> repeat while harvesting both transition edges  
  
**10.6 Combat-harvest route**  
  
expendable or strategically expendable body  
  
-> attack or block for combat utility  
  
-> expected/accepted combat death or departure  
  
-> death/LTB/graveyard listeners and destination stock  
  
This is distinct from sacrifice even when both ultimately produce dies.  
  
  
  
**11. ACCEPTANCE TESTS ADDED BY THIS ADDENDUM**  
  
Status convention follows V3.1.1: **RC = current Comprehensive Rules re-read; DR = design requirement; IC = instance-specific card interaction must still be checked.**  
  
|# |Thesis                                                                                                                                                                              |Status                  |  
|--|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------|  
|38|A predicate used to select/name an object is not automatically a continuing predicate on the reference.                                                                             |RC 700.7 · DR           |  
|39|Haunt’s “creature it haunts” continues to identify the originally targeted object even if it stops being a creature.                                                                |RC 702.55b              |  
|40|`dies` is represented as battlefield→graveyard; creature/nontoken/artifact/etc. requirements are separate listener qualifiers evaluated at the appropriate snapshot.                |RC 700.4 · DR           |  
|41|A delayed trigger referring to a particular object can keep referring to it across characteristic changes but ordinarily not after it leaves and returns as a new object.           |RC 603.7c, 400.7        |  
|42|Same physical card/substrate across a zone change does not imply same game object.                                                                                                  |RC 400.7, 403.4         |  
|43|A rule/effect may be authorized to find a successor object without making predecessor and successor the same object.                                                                |RC 400.7 exceptions · DR|  
|44|Turning face down/up preserves the game-object incarnation; face-down rules substitute a copiable characteristic mask.                                                              |RC 708.2, 708.8         |  
|45|Blinking a face-down permanent and returning it face up is new-object reinstantiation, not a turn-face-up event.                                                                    |RC 400.7, 403.4, 708.8–9|  
|46|When multiple replacements apply, one is applied and the modified event is reevaluated until no applicable replacements remain.                                                     |RC 616.1, 616.1f, 616.2 |  
|47|Random branch selection must be distinguishable from a player/opponent choice.                                                                                                      |DR                      |  
|48|Feedstock is a contextual role derived from a route/network, not an intrinsic property of a card.                                                                                   |DR                      |  
|49|Feedstock compatibility preserves the same qualifier discipline as ordinary hook/operation compatibility. Token supply cannot automatically satisfy nontoken or durable-card routes.|DR                      |  
|50|A route-rich consumption engine may still be throughput-starved if qualified replenishment rate is below useful sink demand.                                                        |DR                      |  
|51|Autonomous supply, same-resource-dependent supply, regeneration, and reciprocal oscillation are structurally distinct replenishment modes.                                          |DR                      |  
|52|A doomed object can be high-quality feedstock because deliberate consumption captures value before unavoidable scheduled loss.                                                      |DR                      |  
|53|A reciprocal battlefield/graveyard loop can conserve working stock while repeatedly emitting departure and entry events.                                                            |DR                      |  
|54|Combat death/attrition is a different transition source from sacrifice even when both expose a dies facet.                                                                          |DR                      |  
|55|Resource-flow analysis is invoked only where resource circulation constrains the architecture; it is not a universal deck objective.                                                |DR                      |  
|56|Community archetype labels remain external acceptance tests: DIO must reconstruct their useful structural distinctions without importing them as primitives.                        |DR                      |  
  
  
  
**12. CONCRETE COMPATIBILITY PATCHES TO V3.1.1**  
  
This addendum intentionally makes few schema-level changes.  
  
**12.1 No changes**  
  
Unchanged:  
  
	●	five core nouns;  
	●	seven primitive relations;  
	●	AND-of-OR gate rule;  
	●	operation kinds;  
	●	hook qualifier discipline;  
	●	state/interpreter doctrine;  
	●	connection status/strength/polarity;  
	●	module contract;  
	●	ontology/evaluation/portfolio/Kairos separation.  
  
**12.2 Small vocabulary/schema extensions**  
  
**Characteristic effects**  
  
Add:  
  
operation: ... | mask  
  
for rules-defined characteristic masking such as face-down status.  
  
**State/link/tracked-effect optional precision**  
  
Allow optional:  
  
tracking:  
  
  mode: same_instance | authorized_successor  
  
  authority: rule | effect  
  
  transition_scope:  
  
only where successor traceability changes the answer.  
  
**Operation process optional precision**  
  
Allow:  
  
random_selection:  
  
  population:  
  
  sample_size:  
  
  distribution: uniform | specified | unknown  
  
  with_replacement:  
  
  public_or_hidden:  
  
  branch_outputs:  
  
only where a random selector changes connectivity.  
  
**12.3 Derived-view extensions**  
  
Add to section 9 derived roles:  
  
feedstock  
  
Add derived views:  
  
Reference Contract  
  
Resource Flow / Feedstock Flow  
  
The Reference Contract is computed from links/tracked state plus creating and reading Operations. Resource Flow is computed from operations, qualified hooks, cadence/capacity, resource lifecycle, and module structure.  
  
**12.4 Execution doctrine**  
  
Add the iterative **Replacement Composition Protocol from section 4. No new stored primitive is required.**  
  
  
  
**13. IMPLEMENTATION / ANNOTATION PROCEDURE DELTA**  
  
When a card or interaction raises one of these issues, extend the V3.1.1 annotation procedure with the following questions.  
  
**References and mutation**  
  
	1.	What predicate was required to bind/select the object?  
	2.	Did the operation create a continuing reference/link?  
	3.	What condition actually keeps that reference alive?  
	4.	What predicate does the later reader test, and at what checkpoint?  
  
**Identity and zones**  
  
	1.	Is this still the same game-object incarnation?  
	2.	If not, is only the physical card/substrate continuous?  
	3.	Does a rule/effect have explicit authority to track the successor object?  
  
**Face-down**  
  
	1.	What rule/effect defines the face-down mask?  
	2.	What active/copiable characteristics does the mask expose?  
	3.	What hidden-substrate information may a specific permission inspect?  
	4.	Is the action turning the same object face up, or replacing it through a zone transition?  
  
**Replacement effects**  
  
	1.	How many replacements/preventions are applicable to the proposed event?  
	2.	Who/rule chooses the next one?  
	3.	What is the rewritten event after it applies?  
	4.	Which effects are applicable *now*?  
  
**Resource flow**  
  
	1.	What exact qualified stock does the process consume?  
	2.	Where does that stock come from?  
	3.	Is supply one-shot, autonomous, conditional, endogenous, regenerative, self-replacing, or reciprocal?  
	4.	What is the nominal cadence/capacity?  
	5.	What event/resource/state bundle does the transition yield?  
	6.	What useful stock exists after the transition?  
	7.	What other processes compete for the same object/state?  
	8.	Is a real rate needed? If yes, hand the structure to evaluation/simulation rather than inventing one.  
  
  
  
**14. RECONCILIATION OF THE DISCUSSION INTO THE MODEL**  
  
This section exists to preserve the reasoning history without preserving every conversational detour.  
  
|Discussion finding                                                                |Final disposition                                                                                                                 |  
|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|  
|Haunt can remain linked after a haunted object stops being a creature.            |**Promoted** to reference persistence + predicate locality.                                                                       |  
|The noun used in a reference should permanently type the object.                  |**Rejected.** Binding predicate and continuing/read predicates are separate.                                                      |  
|`dies` should be treated as intrinsically creature-qualified.                     |**Rejected for DIO representation.** Use battlefield→graveyard event plus listener-specific type qualifiers.                      |  
|Magic behaves somewhat like an object-oriented system.                            |**Retained only as analogy.** More precise model: typed stateful objects/relations under guarded transitions and rewrites.        |  
|Face-down means the card’s identity becomes “2/2 with nothing else.”              |**Refined.** Same game object; active/copiable characteristic interface is masked while substrate/history/permissions may persist.|  
|Blink returns “the same object.”                                                  |**Rejected.** Same card lineage may return, but zone changes create new game-object incarnations by default.                      |  
|New object means no later rule can know what it became.                           |**Rejected.** Successor traceability is possible when explicitly authorized.                                                      |  
|Single replacement rewrite is enough.                                             |**Rejected.** Multiple replacements require iterative application and reevaluation.                                               |  
|Fuel can be represented by counting token makers/recursive bodies.                |**Rejected as insufficient.** Feedstock is typed, contextual, rate-bearing, and network-dependent.                                |  
|Repeatable fuel and one-shot fuel are equivalent counts.                          |**Rejected.** Cadence/replenishment mode matters.                                                                                 |  
|Best fuel is often already doomed.                                                |**Retained as structural/evaluative principle.** Scheduled loss lowers incremental consumption cost; evaluator decides magnitude. |  
|ETB creatures become fuel in recursion-heavy networks.                            |**Promoted.** Feedstock role is topology-dependent; transition yield can include future re-entry.                                 |  
|Cauldron-like exchange can alternate two bodies between battlefield and graveyard.|**Promoted** as reciprocal transition oscillator / working stock.                                                                 |  
|All sacrifice/death chains consume the same creature pool.                        |**Rejected.** Feedstock is typed and downstream qualifiers/destination stock matter.                                              |  
|Combat death can supply death/LTB networks.                                       |**Promoted** as a distinct transition source; it is not sacrifice.                                                                |  
|Factory/Satisfactory throughput is a good global theory of deck quality.          |**Rejected by Goodhart guardrail.** Flow analysis is local and subordinate to purpose.                                            |  
|Community labels should become ontology fields.                                   |**Rejected.** They are external acceptance tests.                                                                                 |  
|Community taxonomy is useful anyway.                                              |**Promoted** as an expressiveness floor and reverse-recognition benchmark.                                                        |  
  
  
  
**15. SOURCE BASIS AND RULES VERIFICATION**  
  
Rules-sensitive claims in this addendum were rechecked against the official **Magic: The Gathering Comprehensive Rules effective September 25, 2026.**  
  
Official rules page: https://magic.wizards.com/en/rules  
Official TXT used for verification: https://media.wizards.com/2026/downloads/MagicCompRules%2020260925.txt  
  
Especially relevant rules:  
  
	●	**400.7** — zone changes create new objects, with listed exceptions;  
	●	**403.4** — permanents entering the battlefield are new objects;  
	●	**603.6e, 603.7c** — examples of successor tracking and characteristic-change persistence for delayed/referential effects;  
	●	**616.1, 616.1f, 616.2** — ordering and iterative composition of replacement/prevention effects;  
	●	**700.4** — dies means battlefield → graveyard;  
	●	**700.7** — “this [something]” identifies the particular object even if it loses that quality;  
	●	**702.55b** — Haunt’s “creature it haunts” keeps referring to the target even if it is no longer a creature;  
	●	**708.2, 708.8–10** — face-down characteristic profiles, turn-face-up persistence, and copying interactions.  
  
Companion external test set:  
  
MTG_DIO_v3.1.1_Community_Archetype_Acceptance_Corpus_v0.1.md (2026-10-09)  
  
The community vocabulary is used only as an acceptance corpus; its terms are not normative ontology content.  
  
  
  
**16. GOVERNING PRINCIPLES ADDED BY THIS ADDENDUM**  
  
	●	**Predicates are local to checkpoints. References persist according to their own contracts.**  
	●	**Identify the event first; qualify its subject second.**  
	●	**Same card lineage, same game object, and successor traceability are different relations.**  
	●	**Face-downness masks characteristics; it does not replace the game object.**  
	●	**A new incarnation forgets object-bound state by default even when the physical card persists.**  
	●	**Replacement effects compose by rewrite and reevaluation, not by simultaneous checklist.**  
	●	**Random selection is not choice.**  
	●	**Feedstock is typed, contextual, and network-dependent.**  
	●	**Stock count is not supply rate.**  
	●	**The value of consuming an object includes what the transition emits and what useful state exists afterward.**  
	●	**Some engines consume stock; some recycle working stock through an oscillator.**  
	●	**Resource-flow analysis is a tool, not the objective function.**  
	●	**Community archetypes are tests of expressiveness, not ontology primitives.**  
	●	**When a deeper abstraction explains several folk mechanisms, prefer the abstraction.**  
  
The ontology should continue to make strange machines discoverable without making ordinary cards complicated.  
  
## END ADDENDUM  
