# Oracle refresh, 2026-10-21

- **Source:** Scryfall bulk `oracle_cards`, updated 2026-10-21T09:01:59Z.
  - Downloaded file: `oracle-cards-20261021090159.jsonl.gz`, sha256 `4f0593ac…aaf6`. It has 38,940 objects.
  - Converted to a JSON array; the array's sha256 is `7169fe9a…4c815`, the value recorded in the snapshot.
- **Tool:** `oracle_refresh-0.2.1`.
- **Snapshot:** `refresh/oracle_refresh_2026-10-21_7e517de93bb47238.jsonl`.
- **DB:** `mtg_cards_v0.2.sqlite`, rebuilt with `--source-modified 2026-10-15T19:03:42.774Z`.
- **Tests:** test_v02.py passes 20/20, and test_mtg_db.py passes 12 with 1 skipped.
- **Unchanged:** `cards`, the review overlay and the Google Sheet were not touched.

## oracle_id coverage

3,371 of 3,372 cards now have an `oracle_id`. That is 99.97%.

| Match | Cards |
|---|---|
| Exact name, text identical | 3,157 |
| Exact name, text differs | 208 (QA `oracle_text_discrepancy`) |
| Diacritic- or punctuation-blind name | 3 (QA `oracle_name_spelling`) |
| Not found | 1: `Elemental`, a token name in the Sheet (QA `oracle_card_not_found`) |

The three spelling items are cases where the Sheet's name differs from Oracle:

| Sheet | Oracle |
|---|---|
| Dunedain Blade | Dúnedain Blade |
| Gideon the Oathsworn | Gideon, the Oathsworn |
| Sandbender's Storm | Sandbenders' Storm |

Commander legality from Scryfall:

- 3,368 cards are legal.
- `Counters` and `______` are not legal. Both are non-game or Un- objects.
- `Elemental` is unknown.

## The 208 text discrepancies

The per-card list is in `oracle_refresh_2026-10-21_discrepancies.csv`, which has a `finding` column. Every item is open with severity medium, because no discrepant card has a verified review.

| Class | Count | Meaning |
|---|---|---|
| format_only | 84 | Multi-face cards (prepare, adventure, transform, split). The Sheet writes each face as `Name {cost}` with blank-line separators; Oracle uses `//`. The rules text matches. |
| reminder_text | 75 | Only reminder text differs, usually because the Sheet drops it, e.g. `{E} (an energy counter)`. |
| self_reference_templating | 10 | The Sheet uses the card's name where Oracle now says "this creature", or the reverse. |
| punctuation_only | 9 | Straight vs curly quotes, or planeswalker loyalty brackets. |
| substantive (auto) | 30 | Checked by hand. 22 are more face-header formatting, 2 are keyword order, 2 are a stray period, and 1 is Class line breaks. The real ones are listed below. |

### Real differences worth a Sheet correction

1. **Medic's Kitesail:** the Sheet says Equip {3}, but Oracle says Equip {2}. This is a cost error.
2. **Finch Formation, Rust-Shield Rampager, Thornplate Intimidator:** the Sheet recorded the *Offspring token* text. That text ends in "(This token's mana cost is …)" and drops the `Offspring {N}` keyword, so the deck evaluators can't see the token-copy option.
3. **Polliwallop:** the Sheet writes out the effect, but the `Affinity for Frogs` keyword is missing.
4. **Whiplash Wordsmith:** the Sheet doesn't have the prepare spell face (Vicious Verse deals 1 damage to target opponent).
5. **Counters:** a Jumpstart front card, not a game card. Scryfall has two with this name (theme {G} and {B}), and the refresh matched the {B} one. The Sheet says {G}. This can be ignored or deleted from the inventory.

One wording difference doesn't change function. **Detective's Phoenix** has older bestow and self-reference wording.

## Fix made to the refresh tool (0.2.0 → 0.2.1)

The first 0.2.0 run took the first Scryfall object with a matching name. That gave wrong identities to four cards:

- *Pick Your Poison* matched the `funny` playtest card.
- *Savage Lands*, *Earth Rumble* and *Counters* matched Jumpstart front cards.

That snapshot was never shared, so I removed it. It is kept outside the project for reference.

0.2.1 makes two changes:

- **Ranking:** when names collide, it prefers playable, Commander-legal, non-`funny` objects.
- **Fallback:** if no exact name matches, it tries a diacritic- and punctuation-blind name and opens an `oracle_name_spelling` QA item.

`test_v02.py`'s refresh test now counts QA items for its own fixture run only. Before, it counted every refresh in the copied DB and failed (212 ≠ 1) once a real snapshot existed.

## To rerun

```
curl -s https://api.scryfall.com/bulk-data/oracle-cards        # take jsonl_download_uri (no JSON-array download_uri any more)
python -c "import gzip,json,sys; json.dump([json.loads(l) for l in gzip.open(sys.argv[1],'rt') if l.strip()], open(sys.argv[2],'w'))" in.jsonl.gz out.json
python oracle_refresh.py snapshot --db mtg_cards_v0.2.sqlite --scryfall out.json --out refresh/ --source-updated-at <updated_at>
PYTHONHASHSEED=0 python migrate_v02.py --v01 mtg_cards.sqlite --out mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl --refresh-dir refresh --source-modified <Drive modifiedTime>
```
