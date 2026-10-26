"""Which inventory rows the evaluator treats as game cards, and which rules text it reads.

The working Sheet stays the inventory authority (ownership, custody, decks); nothing here edits it.
For the cards a reconciliation record marks `evaluator_reads: oracle`, the evaluator reads the matched
Oracle rules text (and, where the record lists it, the Oracle type line) instead of the Sheet's text.
Rows marked `excluded` (non-game cards, tokens) are removed. This replaces the hard-coded NON_DECK set
of mtg_eval 0.3.0, which also hid three owned Offspring creatures.
"""
import json
from mtg_eval.inventory import Row

ALWAYS_EXCLUDED = {'______'}


def overrides(con):
    """{card_name: {'evaluator_reads', 'oracle_text', 'type_line'}} from the rules-text layer; {} on a v0.1 DB."""
    try:
        rows = con.execute("select t.card_name,t.evaluator_reads,t.rules_text,e.fields_json,o.faces_json,o.legal_commander from rules_text t "
                           "left join effective_reconciliation e using(card_name) "
                           "left join external_oracle o on o.card_name=t.card_name and o.run_id=t.oracle_run_id "
                           "where t.evaluator_reads<>'sheet'").fetchall()
    except Exception:
        return {}
    out = {}
    for name, reads, text, fields, faces, legal in rows:
        fields = json.loads(fields or '[]'); faces = json.loads(faces or 'null') or []
        o = {'evaluator_reads': reads}
        if reads == 'oracle':
            o['oracle_text'] = text
            if 'Type Line' in fields and faces: o['type_line'] = ' // '.join(f['type_line'] for f in faces if f.get('type_line'))
            if 'Commander Legal' in fields and legal: o['commander_legal'] = 'Legal' if legal == 'legal' else 'Not legal'
        out[name] = o
    return out


def apply(inv, con):
    """Patch an SQLiteInventory in memory. Returns the names whose rules text now comes from Oracle."""
    ov = overrides(con)
    for n in ALWAYS_EXCLUDED: inv.cards.pop(n, None)
    oracle = []
    for name in sorted(ov):
        o = ov[name]
        if o['evaluator_reads'] == 'excluded':
            inv.cards.pop(name, None); continue
        if name not in inv.cards:
            raw = con.execute('select raw_json from cards where card_name=?', (name,)).fetchone()
            if raw is None: continue
            inv.cards[name] = Row(json.loads(raw[0]))
        r = inv.cards[name]
        r['Oracle Text'] = o['oracle_text']
        if o.get('type_line'): r['Type Line'] = o['type_line']
        if o.get('commander_legal'): r['Commander Legal'] = o['commander_legal']
        oracle.append(name)
    return oracle
