# Reviewer guide: role audit v0.2 (blind)

You are judging, from Oracle text alone, whether a card fills a strategic deck role. You are **not** told what any detector, inventory tag or earlier reviewer said, and you must not look it up. Judge each item without consulting the other reviewer.

## Answer format

For each item, return one JSON line:

`{"item": "U001", "answer": "YES|NO|DEPENDS|UNRESOLVED", "evidence": "<the Oracle words you rely on>", "qualifiers": ["..."], "note": "<optional>"}`

- **YES**: the card fills the role under the definition below.
- **NO**: it does not.
- **DEPENDS**: it fills the role only under conditions or setups. Name them in `qualifiers`.
- **UNRESOLVED**: the definition doesn't settle it, or the rules are unclear. Say why in `note`.

## Role definitions

The definitions marked **(accepted)** are Zach's decisions (D-0008, 2026-10-28). The rest are proposals still under review (D-0009); apply them as written.

| Role | Fills the role | Record as a qualifier only |
|---|---|---|
| spot_removal | Removes or neutralises one opposing permanent: destroy, exile, bounce, edict, lethal damage or -X/-X, fight | Conditional or partial weakening, narrow targets, random modes |
| protection | Protects *other* permanents you control: hexproof, indestructible, ward, shield, phasing, protection, equipment that grants these | Self-only protection; saving by bounce or blink |
| recursion | Returns or recasts *other* cards from your graveyard | **(accepted)** Flashback and other self-reuse are `self_reuse`, not recursion. Temporary reanimation is a qualifier |
| ramp | Repeatable mana beyond your normal land drop | Rituals, restricted or conditional mana, cost reduction |
| fixing | **(accepted)** Report `land_colour_access` (lands) and `nonland_fixing` separately: say which in `qualifiers` | Restricted colours, inefficient conversion |
| draw | Draws cards for net card advantage | Loot or rummage, cycling, wheels, symmetric draw |
| sac_outlet | Repeatable, at-will sacrifice of another permanent | **(accepted)** One-shot sacrifices (ETB, spell) are qualifiers and sacrifice-trigger generators, not outlets. Self-sacrifice only does not count |
| token_maker | Creates tokens itself. **(accepted)** Cards that create Treasure, Food or Clue tokens are token makers | **(accepted)** Token multipliers (adding tokens only when another effect creates them) are `token_multiplier`, not token makers |
| closer | A credible route to ending the game: repeatable drain or damage to opponents, scaling team pump or evasion, alternate win | **(accepted)** A one-time drain of 2 is not a closer. Single-creature evasion is a qualifier |

Use Oracle text only. Reminder text in parentheses explains a keyword; judge the keyword's real effect on the card.

## Packets

- `blind_packet.jsonl`: 360 items (U001–U360). Cards with no claim of the given role from any source, 20 per role per stratum, in shuffled order. Most answers will be NO; that is expected.
- `challenge_packet.jsonl`: 54 items (C001–C054), chosen for mechanisms that are known to be hard. Judge only the `role` field. Ignore `mechanism`; it is there for the analysis.
