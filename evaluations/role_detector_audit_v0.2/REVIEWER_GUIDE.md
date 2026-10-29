# Reviewer guide: card roles (blind)

You will judge, from Oracle text alone, whether a card fills a strategic deck role. Judge each item on its own. Don't look up other sources about these cards' classifications, and don't consult anyone else.

## Answer format

Return one JSON line per item:

`{"item": "R001", "answer": "YES|NO|DEPENDS|UNRESOLVED", "evidence": "<the Oracle words you rely on>", "qualifiers": ["..."], "note": "<optional>"}`

- **YES**: the card has an actual ability that fills the role. Ordinary costs and normal game-state requirements count (paying mana, having a target, attacking, a creature dying). List any relevant conditions in `qualifiers`. A conditional ability is not automatically DEPENDS.
- **DEPENDS**: filling the role needs a nontrivial outside enabler or an unusually restrictive setup, or it hinges on a disputed reading of the definition. Name what it depends on.
- **NO**: there is no qualifying ability under the definition below.
- **UNRESOLVED**: you can't read the text or rules confidently enough to decide. Say why.

Every YES or DEPENDS needs `evidence`.

## Role definitions

Definitions marked **(accepted)** are the project owner's decisions. The rest are provisional working definitions. Apply them as written.

| Role | Fills the role | Record as a qualifier |
|---|---|---|
| spot_removal | Removes or neutralises one opposing permanent: destroy, exile, bounce, edict, lethal damage or -X/-X, fight | partial or conditional weakening, narrow targets, random modes |
| protection | Protects *other* permanents you control: hexproof, indestructible, ward, shield counters, phasing, protection, or equipment and auras that grant these | self-only protection; saving a permanent by bouncing or blinking it |
| recursion | Returns *other* cards from your graveyard to hand or battlefield, or lets you cast them from there | **(accepted)** Flashback and other ways a card reuses only itself are `self_reuse`, not recursion: answer NO and add the qualifier `self_reuse`. Temporary reanimation is a qualifier |
| ramp | Increases your mana production or speeds up your mana development beyond normal land drops. One-shot land ramp (e.g. a spell that puts a land onto the battlefield) counts | qualifiers: `persistent`, `repeatable`, `ritual` (one turn only), `restricted` (mana only for some spells), `conditional` |
| fixing | **(accepted)** Two separate things; say which in `qualifiers`. `land_colour_access` (a land and the colours it makes) and `nonland_fixing` (rocks, dorks, land search, any-colour effects). Answer YES only if the card improves colour *flexibility*, meaning it makes or finds more than one colour. For a land, list the colours it can produce, e.g. `colours:WU` | restricted colours, inefficient conversion |
| draw | Draws cards for net card advantage. Name the resource spent, if any | `replacement` (cycling, a draw that replaces itself: answer NO), `loot` (draw then discard: answer NO), `wheel`, `symmetric` |
| sac_outlet | Repeatable, at-will sacrifice of *another* permanent | **(accepted)** A one-shot sacrifice (ETB or spell) is not an outlet: answer NO and add the qualifier `one_shot_sacrifice` (a sacrifice-trigger generator). Self-sacrifice only: NO |
| token_maker | Creates tokens itself. **(accepted)** Cards that create Treasure, Food or Clue tokens are token makers | **(accepted)** Token multipliers, which add tokens only when another effect creates them: answer NO and add the qualifier `token_multiplier` |
| closer | A credible way to end the game: repeatable drain or damage to opponents, scaling team pump or evasion, alternate win | **(accepted)** A one-time drain of 2 is not a closer. Single-creature evasion is a qualifier |

Use Oracle text. Reminder text in parentheses explains a keyword; judge what the keyword actually does on this card.
