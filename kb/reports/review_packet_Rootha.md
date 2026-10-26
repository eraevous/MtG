# Review packet: Rootha

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Arcane Signet

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Archmage Emeritus

> Magecraft — Whenever you cast or copy an instant or sorcery spell, draw a card.

- action: kind `triggered`, hook `["cast", ["instant", "sorcery"]]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Big Score

> As an additional cost to cast this spell, discard a card.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Big Score

> Draw two cards and create two Treasure tokens. (They're artifacts with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 2, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}], ["draw", 2]]`, gates `{}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cascade Bluffs

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Counterspell

> Counter target spell.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["interaction", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target spell)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cursed Mirror

> {T}: Add {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed R x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Enduring Curiosity

> Whenever a creature you control deals combat damage to a player, draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Frostboil Snarl

> {T}: Add {U} or {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Galazeth Prismari

> When Galazeth Prismari enters, create a Treasure token.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Magma Opus

> {U/R}{U/R}, Discard this card: Create a Treasure token.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: discard: Discard this card; cost_mana_type_lost: {U/R} {U/R})
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Preordain

> Scry 2, then draw a card. (To scry 2, look at the top two cards of your library, then put any number of them on the bottom and the rest on top in any order.)

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 1], ["scry_surveil", 2]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rapturous Moment

> Draw three cards, then discard two cards. Add {U}{U}{R}{R}{R}.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3], ["mana", 5]]`, gates `{}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed UURRR x5; action: amount only; zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Seize the Spoils

> As an additional cost to cast this spell, discard a card.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Seize the Spoils

> Draw two cards and create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}], ["draw", 2]]`, gates `{}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Shivan Reef

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

## Storm-Kiln Artist

> Magecraft — Whenever you cast or copy an instant or sorcery spell, create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `triggered`, hook `["cast", ["instant", "sorcery"]]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sulfur Falls

> {T}: Add {U} or {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Tablet of Discovery

> {T}: Add {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed R x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Talisman of Creativity

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Treasure Cruise

> Draw three cards.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Unexpected Assistance

> Draw three cards, then discard a card.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
