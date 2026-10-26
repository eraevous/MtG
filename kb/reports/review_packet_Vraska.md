# Review packet: Vraska

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## Arcane Signet

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bespoke Bō

> When this Equipment enters, return up to one other target nonland permanent to its owner's hand.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target nonland permanent; zone_transition_lost: card.return_to_hand: battlefield -> hand)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Bident of Thassa

> Whenever a creature you control deals combat damage to a player, you may draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Boosted Sloop

> Whenever you attack, draw a card, then discard a card.

- action: kind `triggered`, hook `["attack", {"self": false}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": true, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Boros Signet

> {1}, {T}: Add {R}{W}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed RW x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Carrot Cake

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Command Tower

> {T}: Add one mana of any color in your commander's color identity.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cori-Steel Cutter

> Flurry — Whenever you cast your second spell each turn, create a 1/1 white Monk creature token with prowess. You may attach this Equipment to it. (Whenever you cast a noncreature spell, the token gets +1/+1 until end of turn.)

- action: kind `triggered`, hook `["cast", ["second spell"]]`, cost `null`, outputs `[["token", {"keywords": ["prowess"], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["monk"], "tapped": false, "toughness": 1, "types": ["creature"]}]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (optional_lost: may)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Coruscation Mage

> Whenever you cast a noncreature spell, this creature deals 1 damage to each opponent.

- action: kind `triggered`, hook `["cast", ["noncreature"]]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Counterspell

> Counter target spell.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["interaction", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target spell)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Craterclaw Colossus

> When this creature enters, creatures you control gain trample and get +X/+0 until end of turn, where X is the number of artifacts you control.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["pump_team_x", "artifacts"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (amplifier_lost: where x is the number of artifacts you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Cryogen Relic

> When this artifact enters or leaves the battlefield, draw a card.

- action: kind `triggered`, hook `["leave", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Curiosity Crafter

> Whenever a creature token you control deals combat damage to a player, draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["creature", "token"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Dreams of Laguna

> Surveil 1, then draw a card. (To surveil 1, look at the top card of your library. You may put it into your graveyard.)

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 1], ["scry_surveil", 1]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Elsewhere Flask

> When this artifact enters, draw a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ferrous Lake

> {1}, {T}: Add {U}{R}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed UR x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Fields of Strife

> {T}: Add {R} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Fields of Strife

> {2}{R}{W}, {T}: Surveil 1. (Look at the top card of your library. You may put it into your graveyard.)

- action: kind `activated`, hook `null`, cost `{"mana": [2, [["R"], ["W"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["scry_surveil", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Fire Nation Palace

> {T}: Add {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed R x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Fountainport Bell

> {1}, Sacrifice this artifact: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Gossip's Talent

> Whenever a creature you control enters, surveil 1.

- action: kind `triggered`, hook `["enter", {"other": false, "types": ["creature"]}]`, cost `null`, outputs `[["scry_surveil", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Guidelight Matrix

> When this artifact enters, draw a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Improvised Club

> As an additional cost to cast this spell, sacrifice an artifact or creature.

- action: kind `additional_cost`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: permanent.sacrifice: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Instant Ramen

> When this artifact enters, draw a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Instant Ramen

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Melded Moxite

> {3}, Sacrifice this artifact: Create a tapped 2/2 colorless Robot artifact creature token.

- action: kind `activated`, hook `null`, cost `{"mana": [3, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": false}`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 2, "subtypes": ["robot"], "tapped": true, "toughness": 2, "types": ["artifact", "creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Mouser Foundry

> When this artifact enters or leaves the battlefield, create a 1/1 colorless Robot artifact creature token.

- action: kind `triggered`, hook `["leave", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["robot"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
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

## Ooze Spill

> Counter target spell. Create a Mutagen token. (It's an artifact with "{1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate only as a sorcery.")

- action: kind `spell`, hook `null`, cost `null`, outputs `[["token", {"keywords": [], "kind": "mutagen", "mana_sac": false, "n": 1, "power": 0, "subtypes": ["mutagen"], "tapped": false, "toughness": 0, "types": ["artifact"]}], ["interaction", 1]]`, gates `{}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {1}, {T}, Sacrifice this token: Put a +1/+1 counter on target creature. Activate; output_not_executed: interaction; target_lost: target creature; target_lost: target spell)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rabanastre, Royal City

> {T}: Add {R} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Raff, Weatherlight Stalwart

> {3}{W}{W}: Creatures you control get +1/+1 and gain vigilance until end of turn.

- action: kind `activated`, hook `null`, cost `{"mana": [3, [["W"], ["W"]]], "sac": null, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["pump_team", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Reckless Fireweaver

> Whenever an artifact you control enters, this creature deals 1 damage to each opponent.

- action: kind `triggered`, hook `["enter", {"other": false, "types": ["artifact"]}]`, cost `null`, outputs `[["drain", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Retrofitter Foundry

> {2}, {T}: Create a 1/1 colorless Servo artifact creature token.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["servo"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Retrofitter Foundry

> {1}, {T}, Sacrifice a Servo: Create a 1/1 colorless Thopter artifact creature token with flying.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": {"filter": "servo", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": ["flying"], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["thopter"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Retrofitter Foundry

> {T}, Sacrifice a Thopter: Create a 4/4 colorless Construct artifact creature token.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": {"filter": "thopter", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 4, "subtypes": ["construct"], "tapped": false, "toughness": 4, "types": ["artifact", "creature"]}]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rivendell

> {T}: Add {U}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed U x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Saheeli, Sublime Artificer

> Whenever you cast a noncreature spell, create a 1/1 colorless Servo artifact creature token.

- action: kind `triggered`, hook `["cast", ["noncreature"]]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["servo"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sai, Master Thopterist

> Whenever you cast an artifact spell, create a 1/1 colorless Thopter artifact creature token with flying.

- action: kind `triggered`, hook `["cast", ["artifact"]]`, cost `null`, outputs `[["token", {"keywords": ["flying"], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["thopter"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sai, Master Thopterist

> {1}{U}, Sacrifice two artifacts: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [1, [["U"]]], "sac": {"filter": "artifact", "n": 2}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sami, Ship's Engineer

> At the beginning of your end step, if you control two or more tapped creatures, create a tapped 2/2 colorless Robot artifact creature token.

- action: kind `triggered`, hook `["end_step", {}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 2, "subtypes": ["robot"], "tapped": true, "toughness": 2, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": ["tapped_creatures", 2], "once_per_turn": false, "optional": false}`
- runtime: lossless compile
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

## Shivan Reef

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sokka, Bold Boomeranger

> Whenever you cast an artifact or Lesson spell, put a +1/+1 counter on Sokka.

- action: kind `triggered`, hook `["cast", ["artifact", "lesson"]]`, cost `null`, outputs `[["counters", 1, "~"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sol Ring

> {T}: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Spicy Oatmeal Pizza

> {2}, {T}, Sacrifice this artifact: You gain 3 life.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["life", 3]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Spire of Industry

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Springleaf Drum

> {T}, Tap an untapped creature you control: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": {"kind": "creature", "n": 1}, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Sulfur Falls

> {T}: Add {U} or {R}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Talisman of Progress

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Thopter Spy Network

> At the beginning of your upkeep, if you control an artifact, create a 1/1 colorless Thopter artifact creature token with flying.

- action: kind `triggered`, hook `["upkeep", {}]`, cost `null`, outputs `[["token", {"keywords": ["flying"], "kind": null, "mana_sac": false, "n": 1, "power": 1, "subtypes": ["thopter"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": ["control", "artifact"], "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Thopter Spy Network

> Whenever one or more artifact creatures you control deal combat damage to a player, draw a card.

- action: kind `triggered`, hook `["combat_damage", {"types": ["artifact"]}]`, cost `null`, outputs `[["draw", 1]]`, gates `{"batch": true, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Uthros Scanship

> When this Spacecraft enters, draw two cards, then discard a card.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["draw", 2]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (zone_transition_lost: card.discard: hand -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vraska, Soul of Stone

> Whenever you cast a noncreature spell, create a 1/1 colorless Sculpture Treasure artifact creature token with "{T}, Sacrifice this token: Add one mana of any color."

- action: kind `triggered`, hook `["cast", ["noncreature"]]`, cost `null`, outputs `[["token", {"keywords": [], "kind": "treasure", "mana_sac": true, "n": 1, "power": 1, "subtypes": ["sculpture", "treasure"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- warning: C12_granted_ability: quoted ability granted to another object; check that its outputs are not counted as this operation's
- runtime: lossy compile, so no runtime certificate even after review (granted_ability: {T}, Sacrifice this token: Add one mana of any color.; zone_transition_lost: permanent.sacrifice: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Whirler Rogue

> When this creature enters, create two 1/1 colorless Thopter artifact creature tokens with flying.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": ["flying"], "kind": null, "mana_sac": false, "n": 2, "power": 1, "subtypes": ["thopter"], "tapped": false, "toughness": 1, "types": ["artifact", "creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## White Auracite

> When this artifact enters, exile target nonland permanent an opponent controls until this artifact leaves the battlefield.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["interaction", 1]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target nonland permanent an opponent controls; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## White Auracite

> {T}: Add {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed W x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Wurmwall Sweeper

> When this Spacecraft enters, surveil 2.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["scry_surveil", 2]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
