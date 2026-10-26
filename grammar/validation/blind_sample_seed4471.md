# Blind semantic sample, seed 4471 (2026-10-22)

**What was sampled.** 50 abilities, drawn at random with seed 4471 from owned, fully parsed, non-keyword
abilities. This seed was not used while the grammar or the qualifiers were developed.

**Graded against.** Each generated DIO contract (grammar 0.2.0, concepts 0.2.0, semantics 0.1.0) was read next to
the Oracle text and checked against the rules. The earlier contract drafter was not consulted. The rendered
contracts are in `blind_sample_seed4471_contracts.txt`.

**Grades:**

- **C (correct):** every hook, relation and composition is right, and every material qualifier is present.
- **M (minor):** the structure is right, but a qualifier is missing or wrong.
- **W (wrong):** a wrong hook, a wrong argument role, or a wrong or missing component.

| Grade | Count | Share |
|---|---|---|
| C | 34 | 68% |
| M | 12 | 24% |
| W | 4 | 8% |
| Structure right (C + M) | 46 | **92%** |

Earlier hand checks scored 111 of 115. That figure measured edge mapping only, on samples that were also used to
fix the grammar, so the two are not comparable. This sample grades the whole contract, qualifiers included, on
an untouched seed. 68% is the honest figure for complete semantic correctness today.

## The four W

| Card | Problem | Class | Fixed after grading |
|---|---|---|---|
| Swallowed by Leviathan | "Choose target spell" was read as choosing a value, not choosing a target | choice vs target (also Lulu) | yes: new `choice.target` concept and rule, which adds an eligibility group |
| Terra, Magical Adept | Returning a card to the battlefield got the hook `card.return_to_hand` | destination decides the hook | yes: the hook now follows the bound destination |
| Haunting Voyage | Same return-hook bug. "Choose a creature type" bound "a creature" as a permanent | choice legal set | yes, both |
| Cryoshatter | In "is dealt damage", the enchanted creature was the subject (source) instead of the recipient | argument role | yes: passive "is dealt" now binds the recipient (`to`) |

## The twelve M

| Card | Problem | Status |
|---|---|---|
| Heartwood Crafter, Michelangelo | Named predefined token (Heartwood, Mutagen) loses its name | open: the noun phrase chunker does not take an unknown word before "token" |
| Stingerquill Charm | "named Cadet" lost | partly: `name` is read when it is inside the noun phrase |
| Skilled Battlecarver | "During your turn" had no turn scope | fixed: timing terms carry `turn_scope` |
| Eirdu | Paying {B} inside an effect had no hook | fixed: `op.pay` binds `mana.spend`, `life.pay` or `energy.pay` |
| Nature's Lore | Result order lost (search, put, then shuffle) | fixed: every result carries `step` |
| Grafted Growth | "creature or Vehicle" read as both | fixed: `type_logic: any_of`, and discovery compares the union |
| Appa | Airbend's target was not bound to the macro | fixed: keyword units carry bound arguments |
| Hunter's Axe, Skarrg | "gets +X and has/gains Y": the second predicate lost its subject | fixed: coordinated predicates inherit the subject, marked `inherited` |
| Pyrrhic Strike | "you may blight 2": optional cost not marked | fixed: optional cost components carry `optional` |
| Ophiomancer | "control no Snakes": the zero count was lost | fixed: `st.control` carries a `comparison` |

After the fixes, I regraded the same 50 abilities, matching them by card and Oracle text. They come out at C 47,
M 3 and W 0. The three remaining M are all named tokens: Heartwood, Mutagen and Cadet.

That figure is contaminated, because I made the fixes while looking at this sample. **The next blind sample has to
use a new seed.**
