# Review packet: Dina

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Along the Crooked Way

> When this enchantment enters, return target creature card from your graveyard to your hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["recursion", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: recursion; target_lost: target creature; zone_transition_lost: card.return_to_hand: graveyard -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Arcane Signet

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Blight Mound

> Whenever a nontoken creature you control dies, create a 1/1 black and green Pest creature token with "When this token dies, you gain 1 life."

- action: kind `triggered`, hook `["dies", {"types": ["creature", "nontoken"]}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["pest"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: When this token dies, you gain 1 life.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bojuka Bog

> When this land enters, exile target player's graveyard.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target player; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bojuka Bog

> {T}: Add {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed B x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cauldron of Essence

> Whenever a creature you control dies, each opponent loses 1 life and you gain 1 life.

- action: kind `triggered`, hook `["dies", {"types": ["creature"]}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cauldron of Essence

> {1}{B}{G}, {T}, Sacrifice a creature: Return target creature card from your graveyard to the battlefield. Activate only as a sorcery.

- action: kind `activated`, hook `null`, cost `{"mana": [1, [["B"], ["G"]]], "sac": {"filter": "creature", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["recursion", 1]]`, gates `{"once_per_turn": false, "sorcery": true}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: recursion; target_lost: target creature; zone_transition_lost: card.return_to_battlefield: graveyard -> battlefield)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Chomping Changeling

> When this creature enters, destroy up to one target artifact or enchantment.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: up to one target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Deadly Dispute

> As an additional cost to cast this spell, sacrifice an artifact or creature.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: permanent.sacrifice: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Deadly Dispute

> Draw two cards and create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}], ["draw", 2]]`, gates `{}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Defiling Daemogoth

> Whenever a creature you control deals combat damage to a player, you gain 1 life.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature"]}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dina, Essence Brewer

> Whenever you sacrifice a creature, draw a card. This ability triggers only once each turn.

- action: kind `triggered`, hook `["sacrifice", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": true, "optional": false}`
- runtime: lossless compile

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Dina%2C%20Essence%20Brewer.op001 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test dina_essence_brewer.sacrifice_draw
```

## Dina, Soul Steeper

> Whenever you gain life, each opponent loses 1 life.

- action: kind `triggered`, hook `["lifegain", {}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Elvish Mystic

> {T}: Add {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed G x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Essenceknit Scholar

> When this creature enters, create a 1/1 black and green Pest creature token with "Whenever this token attacks, you gain 1 life."

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["pest"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: Whenever this token attacks, you gain 1 life.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gorma, the Gullet

> Whenever another creature you control dies, put a +1/+1 counter on Gorma.

- action: kind `triggered`, hook `["dies", {"types": ["creature"]}]`, cost `null`, outputs `[["counters", 1, "~"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Haywire Mite

> When this creature dies, you gain 2 life.

- action: kind `triggered`, hook `["dies", {"self": true}]`, cost `null`, outputs `[["life", 2]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Haywire Mite

> {G}, Sacrifice this creature: Exile target noncreature artifact or noncreature enchantment.

- action: kind `activated`, hook `null`, cost `{"mana": [0, [["G"]]], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target noncreature artifact; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## High Market

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## High Market

> {T}, Sacrifice a creature: You gain 1 life.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": {"filter": "creature", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["life", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Illegitimate Business

> When this land enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Illegitimate Business

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Llanowar Wastes

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Lord Dregg, Insect Invader

> {3}{G}, Sacrifice a token: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [3, [["G"]]], "sac": {"filter": "token", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Moldervine Reclamation

> Whenever a creature you control dies, you gain 1 life and draw a card.

- action: kind `triggered`, hook `["dies", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1], ["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mudflat Village

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Necroblossom Snarl

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Pestbrood Sloth

> When this creature dies, create two 1/1 black and green Pest creature tokens with "Whenever this token attacks, you gain 1 life."

- action: kind `triggered`, hook `["dies", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 2, "power": 1, "subtypes": ["pest"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: Whenever this token attacks, you gain 1 life.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Pizza Face, Gastromancer

> When Pizza Face enters, create a Food token.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "food", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["food"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Pizza Face, Gastromancer

> {10}, {T}, Sacrifice Pizza Face: You gain 15 life.

- action: kind `activated`, hook `null`, cost `{"mana": [10, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["life", 15]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Plumb the Forbidden

> As an additional cost to cast this spell, you may sacrifice one or more creatures.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Realm of Koh

> {T}: Add {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed B x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Realm of Koh

> {3}{B}, {T}: Create a 1/1 colorless Spirit creature token with "This token can't block or be blocked by non-Spirit creatures."

- action: kind `activated`, hook `null`, cost `{"mana": [3, [["B"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["spirit"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: This token can't block or be blocked by non-Spirit creatures.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Smothering Abomination

> Whenever you sacrifice a creature, draw a card.

- action: kind `triggered`, hook `["sacrifice", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sol Ring

> {T}: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## South Wind Avatar

> Whenever you gain life, each opponent loses 1 life.

- action: kind `triggered`, hook `["lifegain", {}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Springleaf Parade

> When this enchantment enters, create X 1/1 colorless Shapeshifter creature tokens with changeling. (They're every creature type.)

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 0, "power": 1, "subtypes": ["shapeshifter"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Starscape Cleric

> Whenever you gain life, each opponent loses 1 life.

- action: kind `triggered`, hook `["lifegain", {}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Malady

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Twilight Mire

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vicious Rivalry

> Destroy all artifacts and creatures with mana value X or less.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["wipe", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: wipe; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Woe Strider

> When this creature enters, create a 0/1 white Goat creature token.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 0, "subtypes": ["goat"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Woe Strider

> Sacrifice another creature: Scry 1.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": {"filter": "creature", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["scry_surveil", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Woodland Cemetery

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
