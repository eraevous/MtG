# Review packet: Counter Blitz

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

## Bane of Progress

> When this creature enters, destroy all artifacts and enchantments. Put a +1/+1 counter on this creature for each permanent destroyed this way.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["counters", 1, "this creature for each permanent destroyed this way"], ["wipe", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (amplifier_lost: for each permanent destroyed this way; output_not_executed: wipe; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Brushland

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Chasm Skulker

> Whenever you draw a card, put a +1/+1 counter on this creature.

- action: kind `triggered`, hook `["draw", {}]`, cost `null`, outputs `[["counters", 1, "this creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Damning Verdict

> Destroy all creatures with no counters on them.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["wipe", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: wipe; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Duskshell Crawler

> When this creature enters, put a +1/+1 counter on target creature.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["counters", 1, "target creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Flooded Grove

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Forge of Heroes

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Fortified Village

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Glacial Fortress

> {T}: Add {W} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hinterland Harbor

> {T}: Add {G} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Nesting Grounds

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## O'aka, Traveling Merchant

> {T}, Remove a counter from a nonland permanent you control: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: remove_counters: Remove a counter from a nonland permanent you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Overflowing Basin

> {1}, {T}: Add {G}{U}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed GU x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Port Town

> {T}: Add {W} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Pull from Tomorrow

> Draw X cards, then discard a card.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 0]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (cost_mana_type_lost: {X}; zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Skycloud Expanse

> {1}, {T}: Add {W}{U}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed WU x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sol Ring

> {T}: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sphere Grid

> Whenever a creature you control deals combat damage to a player, put a +1/+1 counter on that creature.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature"]}]`, cost `null`, outputs `[["counters", 1, "that creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sungrass Prairie

> {1}, {T}: Add {G}{W}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed GW x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sunpetal Grove

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Enlightenment

> {T}: Add {W} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Mystery

> {T}: Add {G} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Plenty

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Tireless Tracker

> Landfall — Whenever a land you control enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.")

- action: kind `triggered`, hook `["landfall", {}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "clue", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["clue"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {2}, Sacrifice this token: Draw a card.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Tireless Tracker

> Whenever you sacrifice a Clue, put a +1/+1 counter on this creature.

- action: kind `triggered`, hook `["sacrifice", {"types": ["sub:clue"]}]`, cost `null`, outputs `[["counters", 1, "this creature"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vineglimmer Snarl

> {T}: Add {G} or {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Wakka, Devoted Guardian

> Whenever Wakka deals combat damage to a player, destroy up to one target artifact that player controls and put a +1/+1 counter on Wakka.

- action: kind `triggered`, hook `["combat_damage", {"self": true}]`, cost `null`, outputs `[["counters", 1, "~"], ["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: up to one target artifact; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Walking Ballista

> {4}: Put a +1/+1 counter on this creature.

- action: kind `activated`, hook `null`, cost `{"mana": [4, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["counters", 1, "this creature"]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
