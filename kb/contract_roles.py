"""Contract-grounded roles for the 0.3.0 evaluator (C-012, HO-MTG-20261110-5ARR).

mtg_eval assigns roles (draw, ramp, ...) from its own Oracle-text patterns. The KB already holds
DIO-shaped operation contracts, and each contract lists the DIO events it makes happen
(`query_index.feeds`, written by kb/contracts.py from `result.produces`). This module makes the
evaluator *read* those contracts for the roles a contract can carry, instead of citing them.

How a role is decided, per card:
  * Role in ROLE_MAP and the card has contracts: the contracts decide. Supported when some
    contract feeds a mapped event; otherwise `not_in_contract` (never counted). basis: dio_contract.
  * A human judgment label (evidence 'label', from the TMNT function labels) is kept as it is,
    basis: human_label, with what the contract says beside it.
  * Role not in ROLE_MAP (the contract vocabulary can't express it yet, e.g. removal scope),
    or the card has no contract: the evaluator's own pattern result is kept, labelled
    basis: text_pattern_fallback. Nothing is left without a basis.

Every mapping in ROLE_MAP is a candidate (lane reading of DIO event ids against evaluator roles),
not a reviewed DIO statement, and the map is not part of the pinned DIO (P-09). Contracts
themselves are candidates too (0 semantically reviewed at r20261104); grounding here means
"read from the KB contract", not "verified".

Nothing pinned is changed: vendor mtg_eval, sqlite_bridge.py and bridge_v02.py are untouched.
Use open_grounded_evaluator() instead of bridge_v02.open_evaluator(); the default path is unchanged.
"""
import json, sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP_VERSION = 'contract-roles-0.1.0'
VERIFICATION_STATE = 'candidate'

# evaluator role -> DIO event ids (kb/events.py vocabulary) that make a contract perform it.
# Deliberately absent (fallback, labelled): spot_removal / wipe (feeds carry no target-vs-each
# scope), recursion (card.return_to_* doesn't say whose card or from which zone), closer,
# protection, and the type/payoff roles, which are not events.
ROLE_MAP = {
    'draw': ['card.draw'],
    'ramp': ['mana.add', 'land_to_battlefield'],
    'counterspell': ['spell.countered'],
    'token_maker': ['token.create'],
    'counter_source': ['counter.put'],
    'lifegain_source': ['life.gain'],
}


def contract_feeds(con, name):
    """{contract_id: [feeds]} for a card, or {} when the KB has no contract for it."""
    out = {}
    for cid, cj in con.execute('select contract_id, contract_json from operation_contracts where card_name=?', (name,)):
        out[cid] = list((json.loads(cj).get('query_index') or {}).get('feeds') or [])
    return out


def grounded_record(pattern_rec, feeds_by_contract, role_map=None, release=None):
    """Merge the evaluator's pattern record with what the card's contracts say. Pure function."""
    role_map = ROLE_MAP if role_map is None else role_map
    rec = {}
    for role, v in (pattern_rec or {}).items():
        rec[role] = {'status': v['status'], 'evidence': dict(v.get('evidence') or {}, basis='text_pattern_fallback')}
    if not feeds_by_contract:
        for v in rec.values(): v['evidence']['fallback_reason'] = 'no KB contract for this card'
        return rec
    for role, events in role_map.items():
        hits = sorted(cid for cid, fs in feeds_by_contract.items() if set(fs) & set(events))
        prior = (pattern_rec or {}).get(role)
        if prior and 'label' in (prior.get('evidence') or {}):
            # a human judgment label (tmnt_function_labels) outranks both readers; keep it, note the contract
            rec[role]['evidence'].update(basis='human_label', contract_says='supported' if hits else 'not_in_contract')
            continue
        ev = {'basis': 'dio_contract', 'contracts': hits or sorted(feeds_by_contract), 'events': list(events),
              'map_version': MAP_VERSION, 'verification_state': VERIFICATION_STATE}
        if release: ev['kb_release'] = release
        if prior: ev['pattern_status'] = prior['status']
        if hits:
            rec[role] = {'status': 'supported', 'evidence': ev}
        elif prior:
            rec[role] = {'status': 'not_in_contract', 'evidence': ev}   # pattern said yes, contracts don't: not counted
    for role, v in rec.items():
        if role not in role_map: v['evidence'].setdefault('fallback_reason', 'role not expressible in contract feeds (ROLE_MAP)')
    return rec


def install(inv, role_map=None):
    """Make inv.record() contract-grounded. inv is a SQLiteInventory (has .db and .record)."""
    con = inv.db
    try:
        release = json.loads((Path(con.execute('pragma database_list').fetchone()[2]).parent / 'SOURCE_MANIFEST.json').read_text()).get('release')
    except Exception:
        release = None
    pattern_record = inv.record
    cache = {}
    def record(name):
        if name not in cache:
            cache[name] = grounded_record(pattern_record(name), contract_feeds(con, name), role_map, release)
        return cache[name]
    inv.record = record
    inv._rec = {}
    inv.role_source = {'basis': 'dio_contract with labelled text_pattern_fallback', 'map_version': MAP_VERSION,
                       'kb_release': release, 'verification_state': VERIFICATION_STATE}
    return inv


def open_grounded_evaluator(database, **kw):
    """bridge_v02.open_evaluator with contract-grounded roles. Same arguments."""
    import sys
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    from bridge_v02 import open_evaluator
    ev = open_evaluator(database, **kw)
    install(ev.inv)
    return ev


def role_report(database, names, role_map=None):
    """For each card: pattern roles vs grounded roles, with basis. Read-only; for review, not decisions."""
    import sys
    for p in (str(HERE), str(HERE / 'vendor')):
        if p not in sys.path: sys.path.insert(0, p)
    from sqlite_bridge import SQLiteInventory
    inv = SQLiteInventory(database)
    out = {}
    for n in names:
        pat = inv.record(n) if n in inv.cards else {}
        g = grounded_record(pat, contract_feeds(inv.db, n), role_map)
        out[n] = {r: {'status': v['status'], 'basis': v['evidence']['basis'], 'pattern_status': (pat.get(r) or {}).get('status')}
                  for r, v in sorted(g.items())}
    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Compare pattern roles with contract-grounded roles (read-only).')
    ap.add_argument('--db', default=str(HERE / 'mtg_cards_v0.2.sqlite'))
    ap.add_argument('cards', nargs='+')
    a = ap.parse_args()
    print(json.dumps({'map_version': MAP_VERSION, 'verification_state': VERIFICATION_STATE,
                      'cards': role_report(a.db, a.cards)}, indent=1, ensure_ascii=False))
