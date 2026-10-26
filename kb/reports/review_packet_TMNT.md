# Review packet: TMNT

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Arcane Signet

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ash Barrens

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Baxter, Fly in the Ointment

> Whenever you draw a card, put a +1/+1 counter on Baxter.

- action: kind `triggered`, hook `["draw", {}]`, cost `null`, outputs `[["counters", 1, "~"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Casey Jones, Back Alley Brute

> Whenever Casey Jones attacks, put a +1/+1 counter on target attacking creature.

- action: kind `triggered`, hook `["attack", {"self": true}]`, cost `null`, outputs `[["counters", 1, "target attacking creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target attacking creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## City of Brass

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Crustacean Commando

> When this creature enters, create a Mutagen token. (It's an artifact with "{1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate only as a sorcery.")

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "mutagen", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["mutagen"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate; target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Devoted Druid

> {T}: Add {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed G x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dimension X Pizzasaur

> {2}, {T}, Sacrifice this creature: You gain 3 life and each opponent loses 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["drain", 3], ["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dragonskull Summit

> {T}: Add {B} or {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Flock Impostor

> When this creature enters, return up to one other target creature you control to its owner's hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target creature you control; zone_transition_lost: card.return_to_hand: battlefield -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Genghis Frog

> Whenever Genghis Frog or another Mutant you control enters, create a Mutagen token. (It's an artifact with "{1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate only as a sorcery.")

- action: kind `triggered`, hook `["enter", {"self_or_other": true, "types": ["sub:mutant"]}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "mutagen", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["mutagen"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate; target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gilded Goose

> When this creature enters, create a Food token. (It's an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.")

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "food", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["food"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {2}, {T}, Sacrifice this token: You gain 3 life.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gilded Goose

> {1}{G}, {T}: Create a Food token.

- action: kind `activated`, hook `null`, cost `{"mana": [1, [["G"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": "food", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["food"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gilded Goose

> {T}, Sacrifice a Food: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": {"filter": "food", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Grand Coliseum

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Haliya, Guided by Light

> Whenever Haliya or another creature or artifact you control enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self_or_other": true, "types": ["artifact", "creature"]}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Heaped Harvest

> When this artifact enters and when you sacrifice it, you may search your library for a basic land card, put it onto the battlefield tapped, then shuffle.

- action: kind `triggered`, hook `["sacrifice", {"self": true}]`, cost `null`, outputs `[]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.search: library -> battlefield)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Heaped Harvest

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hinterland Harbor

> {T}: Add {G} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Improvised Club

> As an additional cost to cast this spell, sacrifice an artifact or creature.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: permanent.sacrifice: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Michelangelo, Weirdness to 11

> When Michelangelo enters, create a Mutagen token. (It's an artifact with "{1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate only as a sorcery.")

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "mutagen", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["mutagen"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate; target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mighty Mutanimals

> When this creature enters, create a 2/2 red Mutant creature token.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 2, "subtypes": ["mutant"], "tapped": false, "toughness": 2, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mighty Mutanimals

> Alliance — Whenever another creature you control enters, put a +1/+1 counter on target creature you control.

- action: kind `triggered`, hook `["enter", {"other": true, "types": ["creature"]}]`, cost `null`, outputs `[["counters", 1, "target creature you control"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mutant Chain Reaction

> Destroy up to one target artifact, enchantment, or creature with flying. Create a Mutagen token. (It's an artifact with "{1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate only as a sorcery.")

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": "mutagen", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["mutagen"], "tapped": false, "toughness": 0, "types": ["artifact"]}], ["interaction", 1]]`, gates `{}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate; output_not_executed: interaction; target_lost: target creature; target_lost: up to one target artifact)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Peregrin Took

> Sacrifice three Foods: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": {"filter": "food", "n": 3}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Perilous Landscape

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Personify

> Exile target creature you control, then return that card to the battlefield under its owner's control. Create a 1/1 colorless Shapeshifter creature token with changeling. (It's every creature type.)

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["shapeshifter"], "tapped": false, "toughness": 1, "types": ["creature"]}], ["interaction", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target creature you control; zone_transition_lost: card.return_to_battlefield: graveyard -> battlefield; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ragost, Deft Gastronaut

> {1}, {T}, Sacrifice a Food: Ragost deals 3 damage to each opponent.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": {"filter": "food", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["drain", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ray Fillet, Wave Warrior

> Whenever a creature you control with a counter on it deals combat damage to a player, draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature", "sub:counter", "sub:it", "sub:on", "sub:with"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rocksteady, Mutant Marauder

> Whenever another nontoken creature you control enters, put a +1/+1 counter on target creature.

- action: kind `triggered`, hook `["enter", {"other": true, "types": ["creature", "nontoken"]}]`, cost `null`, outputs `[["counters", 1, "target creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rootbound Crag

> {T}: Add {R} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Shattered Landscape

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sol Ring

> {T}: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Spire Garden

> {T}: Add {R} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Thornspire Verge

> {T}: Add {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed R x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Turtle Lair

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Undergrowth Stadium

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
