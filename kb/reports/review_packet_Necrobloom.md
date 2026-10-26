# Review packet: Necrobloom

Each contract below passed every validation check. A verified review is a semantic judgement (the contract says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.

## All-Fates Scroll

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Aron, Benalia's Ruin

> {W}{B}, {T}, Sacrifice another creature: Put a +1/+1 counter on each creature you control.

- action: kind `activated`, hook `null`, cost `{"mana": [0, [["W"], ["B"]]], "sac": {"filter": "creature", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["counters", 1, "each creature you control"]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (distribution_lost: each creature you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Avenger of Zendikar

> Landfall — Whenever a land you control enters, you may put a +1/+1 counter on each Plant creature you control.

- action: kind `triggered`, hook `["landfall", {}]`, cost `null`, outputs `[["counters", 1, "each plant creature you control"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": true}`
- runtime: lossy compile, so no runtime certificate even after review (distribution_lost: each plant creature you control)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Avenger%20of%20Zendikar.op002 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test avenger_of_zendikar.landfall_counters
```

## Cremate

> Exile target card from a graveyard.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["interaction", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target card; zone_transition_lost: exile.enter: graveyard -> exile)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Cremate.op001 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test cremate.exile_target_from_graveyard
```

## Cremate

> Draw a card.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 1]]`, gates `{}`
- runtime: lossless compile

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Cremate.op002 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test cremate.draw
```

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

## Foggy Bottom Swamp

> {T}: Add {B} or {G}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Foggy Bottom Swamp

> {4}, {T}, Sacrifice this land: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [4, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Game Over

> Destroy all creatures.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["wipe", 1]]`, gates `{}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: wipe; zone_transition_lost: permanent.destroy: battlefield -> graveyard)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Great Forest Druid

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Great%20Forest%20Druid.op001 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test great_forest_druid.any_color
```

## Harmonize

> Draw three cards.

- action: kind `spell`, hook `null`, cost `null`, outputs `[["draw", 3]]`, gates `{}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Jund Panorama

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Misty Palms Oasis

> {T}: Add {W} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Misty Palms Oasis

> {4}, {T}, Sacrifice this land: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [4, []], "sac": null, "sac_self": true, "tap_other": null, "tap_self": true}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Northampton Farm

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Northampton Farm

> {1}, {T}: Exile target creature you own.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["interaction", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossy compile, so no runtime certificate even after review (output_not_executed: interaction; target_lost: target creature; zone_transition_lost: exile.enter: battlefield -> exile)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Orzhov Basilica

> {T}: Add {W}{B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed WB x2; action: amount only)

```
python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract card.Orzhov%20Basilica.op003 \
    --decision verified --reviewer Zach --source 'Oracle text + CR' --test orzhov_basilica.tap_adds_wb
```

## Piranha Marsh

> {T}: Add {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed B x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Rat King, Pale Piper

> {2}, Sacrifice a token: Draw a card.

- action: kind `activated`, hook `null`, cost `{"mana": [2, []], "sac": {"filter": "token", "n": 1}, "sac_self": false, "tap_other": null, "tap_self": false}`, outputs `[["draw", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Ride the Shoopuf

> Landfall — Whenever a land you control enters, put a +1/+1 counter on target creature you control.

- action: kind `triggered`, hook `["landfall", {}]`, cost `null`, outputs `[["counters", 1, "target creature you control"]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossy compile, so no runtime certificate even after review (target_lost: target creature you control)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Selesnya Guildgate

> {T}: Add {G} or {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Study Hall

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Temple of Silence

> {T}: Add {W} or {B}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: alternatives  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Terminal Moraine

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## The Earth King

> When The Earth King enters, create a 4/4 green Bear creature token.

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["token", {"keywords": [], "kind": null, "mana_sac": false, "n": 1, "power": 4, "subtypes": ["bear"], "tapped": false, "toughness": 4, "types": ["creature"]}]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Tranquil Garden

> {T}: Add {C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: colorless C x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Twilight Diviner

> When this creature enters, surveil 2. (Look at the top two cards of your library, then put any number of them into your graveyard and the rest on top of your library in any order.)

- action: kind `triggered`, hook `["enter", {"self": true}]`, cost `null`, outputs `[["scry_surveil", 2]]`, gates `{"batch": false, "condition": null, "once_per_turn": false, "optional": false}`
- runtime: lossless compile
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Viridescent Bog

> {1}, {T}: Add {B}{G}.

- action: kind `activated`, hook `null`, cost `{"mana": [1, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed BG x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vivid Meadow

> {T}: Add {W}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: fixed W x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Vivid Meadow

> {T}, Remove a charge counter from this land: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: remove_counters: Remove a charge counter from this land; mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Weather Maker

> {T}: Add one mana of any color.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 1]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (mana_type_lost: contract: any_color  x1; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible

## Weather Maker

> {T}, Remove two charge counters from this artifact: Add {C}{C}.

- action: kind `activated`, hook `null`, cost `{"mana": [0, []], "sac": null, "sac_self": false, "tap_other": null, "tap_self": true}`, outputs `[["mana", 2]]`, gates `{"once_per_turn": false, "sorcery": false}`
- warning: C15_engine_mana_colour: 0.3.0 action records only the amount of mana; colour/type lives in the contract and the goldfish CardModel
- runtime: lossy compile, so no runtime certificate even after review (cost_lost: remove_counters: Remove two charge counters from this artifact; mana_type_lost: contract: colorless CC x2; action: amount only)
- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible
