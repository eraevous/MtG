"""Write DATA_DICTIONARY.md: the review CSV's columns, every categorical code, the naming convention, and a
glossary of every concept generated from the concept table, so it never drifts from the build.

    python3 -I dictionary.py grammar_layer.sqlite > DATA_DICTIONARY.md
"""
import sqlite3
import sys

HEAD = open(__file__.replace('dictionary.py', 'dictionary_head.md')).read()

PREFIX = [
    ('ev', 'event', 'something happened in the game; a trigger listens for it'),
    ('op', 'operation', 'something an ability does when it resolves or applies'),
    ('st', 'state predicate', 'something that is true right now; checked, never "happens"'),
    ('cost', 'cost', 'something paid to activate or cast'),
    ('amp', 'amplifier', 'scales a result ("for each", "equal to"); never a requirement'),
    ('time', 'timing / duration', 'when something may happen or how long it lasts'),
    ('rest', 'restriction', 'a limit on activation or casting ("only once each turn")'),
    ('cap', 'capacity', 'a per-turn or per-game cap'),
    ('choice', 'choice', 'a choice made by a player (modes, targets)'),
    ('proc', 'process link', 'how parts connect ("if you do", "then", "when you do")'),
    ('gate', 'gate', 'an intervening or resolution check'),
    ('struct', 'structure', 'card layout, not rules meaning (levels, chapters)'),
    ('kw', 'keyword ability', 'a keyword ability macro (flying, ward, station)'),
    ('kwa', 'keyword action', 'a keyword action macro (scry, earthbend, surveil)'),
]


def main():
    d = sqlite3.connect(sys.argv[1])
    used = dict(d.execute('SELECT concept_id, count(DISTINCT frame_id) FROM frame_concept_edge GROUP BY 1'))
    out = [HEAD, '\n## 7. Concept glossary\n',
           'Generated from the `concept` table. "Frames" is how many templates map to the concept. Keyword macros are '
           'listed by name only; each one expands to its rules definition.\n']
    rows = d.execute('SELECT concept_id, semantic_type, label, dio_ref, dio_status FROM concept ORDER BY concept_id').fetchall()
    for pre, name, gloss in PREFIX:
        rs = [r for r in rows if r[0].split('.')[0] == pre]
        if not rs:
            continue
        out.append(f'\n### `{pre}.` {name}: {gloss}\n')
        if pre in ('kw', 'kwa'):
            out.append(', '.join(f'`{r[0][len(pre) + 1:]}`' for r in rs) + '\n')
            continue
        out.append('| Concept | Means | DIO side | Status | Frames |\n|---|---|---|---|---|')
        for cid, typ, label, ref, status in rs:
            ref = (ref or '').replace('|', '/').replace('\n', ' ')
            out.append(f'| `{cid}` | {(label or "").replace("|", "/")} | {ref} | {status} | {used.get(cid, 0)} |')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
