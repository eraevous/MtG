# Review packet: Sharuum

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Anchovy & Banana Pizza

> When this artifact enters, destroy target creature.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target creature; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Anchovy & Banana Pizza

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Azorius Chancery

> {T}: Add {W}{U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed WU x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Azorius Signet

> {1}, {T}: Add {W}{U}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed WU x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bender's Waterskin

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bespoke Bō

> When this Equipment enters, return up to one other target nonland permanent to its owner's hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target nonland permanent; zone_transition_lost: card.return_to_hand: battlefield -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Blitzball

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Buzz Bots

> When this creature dies, draw a card.

- action: kind `triggered`, hook `["dies", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Chromatic Lantern

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Chromatic Star

> {1}, {T}, Sacrifice this artifact: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Coin of Mastery

> {T}: Create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cryogen Relic

> When this artifact enters or leaves the battlefield, draw a card.

- action: kind `triggered`, hook `["leave", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Crystal Grotto

> When this land enters, scry 1.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["scry_surveil", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Crystal Grotto

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Crystal%20Grotto.op002 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test crystal_grotto.tap_adds_c
```

## Crystal Grotto

> {1}, {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Crystal%20Grotto.op003 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test crystal_grotto.filter_any_color
```

## Disruptor of Currents

> When this creature enters, return up to one other target nonland permanent to its owner's hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target nonland permanent; zone_transition_lost: card.return_to_hand: battlefield -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Etherium Astrolabe

> {B}, {T}, Sacrifice an artifact: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [0, [["B"]]], "sac": {"filter": "artifact", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Executioner's Capsule

> {1}{B}, {T}, Sacrifice this artifact: Destroy target nonblack creature.

- action: kind `activated`, hook `null`, cost `{"mana": [1, [["B"]]], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target nonblack creature; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Firdoch Core

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Foot Headquarters

> When this land enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Foot Headquarters

> {T}: Add {W} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gloomlake Verge

> {T}: Add {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed U x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gold Pan

> When this Equipment enters, create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 0, "subtypes": ["treasure"], "tapped": false, "toughness": 0, "types": ["artifact"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Grim Bauble

> {2}{B}, {T}, Sacrifice this artifact: Surveil 2. (Look at the top two cards of your library, then put any number of them into your graveyard and the rest on top of your library in any order.)

- action: kind `activated`, hook `null`, cost `{"mana": [2, [["B"]]], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["scry_surveil", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Hulldrifter

> When this Vehicle enters, draw two cards.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 2]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Jwar Isle Refuge

> When this land enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Jwar Isle Refuge

> {T}: Add {U} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mechan Assembler

> Whenever another artifact you control enters, create a 2/2 colorless Robot artifact creature token. This ability triggers only once each turn.

- action: kind `triggered`, hook `["enter", {"other": true, "types": ["artifact"]}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 2, "subtypes": ["robot"], "tapped": false, "toughness": 2, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": true, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Nesting Bot

> When this creature dies, create a 1/1 colorless Servo artifact creature token.

- action: kind `triggered`, hook `["dies", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["servo"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Nutrient Block

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Omni-Cheese Pizza

> When this artifact enters, draw a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Omni-Cheese Pizza

> {1}, {T}, Sacrifice this artifact: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Omni-Cheese Pizza

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Orzhov Signet

> {1}, {T}: Add {W}{B}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed WB x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Pactdoll Terror

> Whenever this creature or another artifact you control enters, each opponent loses 1 life and you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self_or_other": true, "types": ["artifact"]}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Prismatic Lens

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Prismatic Lens

> {1}, {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Puppet Conjurer

> {U}, {T}: Create a 0/1 blue Homunculus artifact creature token.

- action: kind `activated`, hook `null`, cost `{"mana": [0, [["U"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 0, "subtypes": ["homunculus"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rescue Skiff

> When this Spacecraft enters, return target creature or enchantment card from your graveyard to the battlefield.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["recursion", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: recursion; target_lost: target creature; zone_transition_lost: card.return_to_battlefield: graveyard -> battlefield)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sanctum Gargoyle

> When this creature enters, you may return target artifact card from your graveyard to your hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["recursion", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: recursion; target_lost: target artifact; zone_transition_lost: card.return_to_hand: graveyard -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Scoured Barrens

> When this land enters, you gain 1 life.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["life", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Scoured Barrens

> {T}: Add {W} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sewer-veillance Cam

> When this artifact enters or leaves the battlefield, you may tap or untap target creature.

- action: kind `triggered`, hook `["leave", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target creature)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sewer-veillance Cam

> {3}{U}, Sacrifice this artifact: Draw two cards.

- action: kind `activated`, hook `null`, cost `{"mana": [3, [["U"]]], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["draw", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sharuum the Hegemon

> When Sharuum enters, you may return target artifact card from your graveyard to the battlefield.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["recursion", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: recursion; target_lost: target artifact; zone_transition_lost: card.return_to_battlefield: graveyard -> battlefield)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Solemn Simulacrum

> When this creature dies, you may draw a card.

- action: kind `triggered`, hook `["dies", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Silence

> {T}: Add {W} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Thopter Foundry

> {1}, Sacrifice a nontoken artifact: Create a 1/1 blue Thopter artifact creature token with flying. You gain 1 life.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": {"filter": "nontoken artifact", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["token", {"keywords": ["flying"], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["thopter"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}], ["life", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Treno, Dark City

> {T}: Add {U} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vanquish the Horde

> Destroy all creatures.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["wipe", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: wipe; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
