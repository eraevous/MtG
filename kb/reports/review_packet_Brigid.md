# Review packet: Brigid

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Blossoming Sands

> When this land enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Blossoming Sands

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Carrot Cake

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Case of the Uneaten Feast

> Whenever a creature you control enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"other": false, "types": ["creature"]}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cloudbound Moogle

> When this creature enters, put a +1/+1 counter on target creature.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["counters", 1, "target creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dawnstrike Vanguard

> At the beginning of your end step, if you control two or more tapped creatures, put a +1/+1 counter on each creature you control other than this creature.

- action: kind `triggered`, hook `["end_step", {}]`, cost `null`, outputs `[["counters", 1, "each creature you control other than this creature"]]`, gates `{"batch": false, "condition": ["tapped_creatures", 2], "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (distribution_lost: each creature you control other than this creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Drix Fatemaker

> When this creature enters, put a +1/+1 counter on target creature.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["counters", 1, "target creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Elvish Visionary

> When this creature enters, draw a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Guac & Marshmallow Pizza

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Haliya, Guided by Light

> Whenever Haliya or another creature or artifact you control enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self_or_other": true, "types": ["artifact", "creature"]}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hall of Oracles

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hall of Oracles

> {1}, {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hidden Hideout

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
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

## Naya Panorama

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ohran Frostfang

> Whenever a creature you control deals combat damage to a player, draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Qasali Pridemage

> {1}, Sacrifice this creature: Destroy target artifact or enchantment.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rayblade Trooper

> When this creature enters, put a +1/+1 counter on target creature you control.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["counters", 1, "target creature you control"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Saltcrusted Steppe

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sundering Growth

> Destroy target artifact or enchantment, then populate. (Create a token that's a copy of a creature token you control.)

- action: kind `spell`, hook `null`, cost `null`, outputs `[["interaction", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (cost_mana_type_lost: {G/W} {G/W}; output_not_executed: interaction; target_lost: target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Teleportation Circle

> At the beginning of your end step, exile up to one target artifact or creature you control, then return that card to the battlefield under its owner's control.

- action: kind `triggered`, hook `["end_step", {}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: up to one target artifact; zone_transition_lost: card.return_to_battlefield: graveyard -> battlefield; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## To Arms!

> Draw a card.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 1]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Undergrowth Leopard

> {1}, Sacrifice this creature: Destroy target artifact or enchantment.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Veteran Beastrider

> {2}{G}{W}: Creatures you control get +1/+1 until end of turn.

- action: kind `activated`, hook `null`, cost `{"mana": [2, [["G"], ["W"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["pump_team", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vigorbloom Annex

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
