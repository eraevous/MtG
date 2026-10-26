# Review packet: Blight Curse

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Arcane Signet

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Burning Curiosity

> As an additional cost to cast this spell, you may blight 1. (You may put a -1/-1 counter on a creature you control.)

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cathartic Reunion

> As an additional cost to cast this spell, discard two cards.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cathartic Reunion

> Draw three cards.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Channeler Initiate

> {T}, Remove a -1/-1 counter from this creature: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: remove_counters: Remove a -1/-1 counter from this creature; mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Commander's Sphere

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Commander's Sphere

> Sacrifice this artifact: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Contagion Clasp

> {4}, {T}: Proliferate.

- action: kind `activated`, hook `null`, cost `{"mana": [4, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["proliferate", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: proliferate)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Devoted Druid

> {T}: Add {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed G x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dragonskull Summit

> {T}: Add {B} or {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Evolution Sage

> Landfall — Whenever a land you control enters, proliferate.

- action: kind `triggered`, hook `["landfall", {}]`, cost `null`, outputs `[["proliferate", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: proliferate)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Golgari Rot Farm

> {T}: Add {B}{G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed BG x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Grave Venerations

> Whenever a creature you control dies, each opponent loses 1 life and you gain 1 life.

- action: kind `triggered`, hook `["dies", {"types": ["creature"]}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gruul Turf

> {T}: Add {R}{G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed RG x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Harmonize

> Draw three cards.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ifnir Deadlands

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ifnir Deadlands

> {T}, Pay 1 life: Add {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: pay_life: Pay 1 life; mana_type_lost: contract: fixed B x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Nesting Grounds

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rakdos Carnarium

> {T}: Add {B}{R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed BR x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rootbound Crag

> {T}: Add {R} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sol Ring

> {T}: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Wickerbough Elder

> {G}, Remove a -1/-1 counter from this creature: Destroy target artifact or enchantment.

- action: kind `activated`, hook `null`, cost `{"mana": [0, [["G"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: remove_counters: Remove a -1/-1 counter from this creature; output_not_executed: interaction; target_lost: target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Wickersmith's Tools

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Woodland Cemetery

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
