"""Contract-grounded roles for the 0.3.0 evaluator (C-012, HO-MTG-20261110-5ARR).

mtg_eval assigns roles (draw, ramp, ...) from its own Oracle-text patterns. The KB already holds
DIO-shaped operation contracts, and each contract lists the DIO events it makes happen
(`query_index.feeds`, written by kb/contracts.py from `result.produces`). This module makes the
evaluator *read* those contracts for the roles a contract can carry, instead of citing them.

How a role is decided, per card:
  * Role in ROLE_MAP and the card has contracts: the contracts decide (always as a candidate). Supported when some
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
MAP_VERSION = 'contract-roles-0.1.3'
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


EXCLUDED_STATES = ('quarantined', 'rejected')   # validation_queue states that disqualify a contract


def contract_states(con, name):
    """{contract_id: (feeds, queue_state)} for the card's *current* contract versions, with the KB's
    effective review/reconciliation state (validation_queue). {} when the KB has no contract for it."""
    out = {}
    q = ('select k.contract_id, k.contract_json, q.queue_state from current_contracts k '
         'join validation_queue q on q.contract_id=k.contract_id and q.contract_version=k.contract_version '
         'where k.card_name=?')
    for cid, cj, state in con.execute(q, (name,)):
        out[cid] = (list((json.loads(cj).get('query_index') or {}).get('feeds') or []), state)
    return out


def contract_feeds(con, name):
    """{contract_id: [feeds]} for usable contracts (rejected or quarantined ones left out)."""
    return {cid: f for cid, (f, st) in contract_states(con, name).items() if st not in EXCLUDED_STATES}


LAND_NOT_RAMP = {'ramp': {'mana.add'}}   # mtg_eval semantics: a land's own mana is mana base, not ramp


UNCERTAIN = ('tag_only', 'contradicted')   # statuses mtg_eval treats as unknown evidence (access bounds, cut blockers)


def human_labels(name):
    """{role: True|False} from mtg_eval's hand labels (tmnt_function_labels.csv), read independently of
    the pattern record: capability_record() drops a false label when no pattern or tag fired."""
    from mtg_eval.semantics import load_labels, LABEL_COLS
    lab = load_labels().get(name)
    return {r: lab[c] == '1' for r, c in LABEL_COLS.items() if lab and c in lab and lab[c] in ('0', '1')} if lab else {}


def grounded_record(pattern_rec, feeds_by_contract, role_map=None, release=None, states=None, type_line=None, labels=None):
    """Merge the evaluator's pattern record with what the card's contracts say. Pure function.
    feeds_by_contract: {contract_id: [feeds]} or {contract_id: ([feeds], queue_state)}. Contracts whose
    queue_state is rejected or quarantined are left out. labels: {role: bool} human judgments, which win.
    A contract-derived role is always a candidate: ROLE_MAP is unreviewed, so a reviewed source contract
    does not promote the role; the source states are kept in contract_states."""
    role_map = ROLE_MAP if role_map is None else role_map
    states, feeds = dict(states or {}), {}
    for cid, v in (feeds_by_contract or {}).items():
        if isinstance(v, tuple): feeds[cid], states[cid] = v
        else: feeds[cid] = v
    excluded = sorted(c for c in feeds if states.get(c) in EXCLUDED_STATES)
    had_contracts = bool(feeds)
    feeds_by_contract = {c: f for c, f in feeds.items() if c not in excluded}
    labels = dict(labels or {})
    for role, v in (pattern_rec or {}).items():
        if 'label' in (v.get('evidence') or {}): labels.setdefault(role, bool(v['evidence']['label']))
    rec = {}
    for role, v in (pattern_rec or {}).items():
        basis = 'human_label' if role in labels else 'text_pattern_fallback'
        rec[role] = {'status': v['status'], 'evidence': dict(v.get('evidence') or {}, basis=basis)}
    for role, ok in labels.items():   # a false label with no pattern hit still blocks the role
        if role not in rec and not ok:
            rec[role] = {'status': 'contradicted', 'evidence': {'label': False, 'basis': 'human_label'}}
    if not feeds_by_contract:
        reason = 'all KB contracts rejected or quarantined' if had_contracts else 'no KB contract for this card'
        for v in rec.values():
            if v['evidence']['basis'] == 'human_label': continue
            v['evidence']['fallback_reason'] = reason
            if excluded: v['evidence']['excluded_contracts'] = excluded
        return rec
    is_land = 'land' in str(type_line or '').lower()
    for role, events in role_map.items():
        if is_land and role in LAND_NOT_RAMP: events = [e for e in events if e not in LAND_NOT_RAMP[role]]
        hits = sorted(cid for cid, fs in feeds_by_contract.items() if set(fs) & set(events))
        prior = (pattern_rec or {}).get(role)
        if role in labels:
            # a human judgment label (tmnt_function_labels) outranks both readers; keep it, note the contract
            if role not in rec:   # true label, no pattern hit
                rec[role] = {'status': 'supported', 'evidence': {'label': True, 'basis': 'human_label'}}
            rec[role]['evidence']['contract_says'] = 'supported' if hits else 'not_in_contract'
            continue
        rest_on = hits or sorted(feeds_by_contract)
        ev = {'basis': 'dio_contract', 'contracts': rest_on, 'events': list(events), 'map_version': MAP_VERSION,
              'contract_states': {c: states.get(c, 'unknown') for c in rest_on},
              'verification_state': VERIFICATION_STATE}
        if excluded: ev['excluded_contracts'] = excluded
        if release: ev['kb_release'] = release
        if prior: ev['pattern_status'] = prior['status']
        if hits:
            rec[role] = {'status': 'supported', 'evidence': ev}
        elif prior and prior['status'] in UNCERTAIN:
            ev['contract_says'] = 'not_in_contract'   # stays unknown evidence for access bounds and cut blockers
            rec[role] = {'status': prior['status'], 'evidence': ev}
        elif prior:
            rec[role] = {'status': 'not_in_contract', 'evidence': ev}   # pattern said yes, contracts don't: not counted
    for role, v in rec.items():
        if role not in role_map and v['evidence']['basis'] != 'human_label': v['evidence'].setdefault('fallback_reason', 'role not expressible in contract feeds (ROLE_MAP)')
    return rec


def _type_line(inv, name):
    row = (getattr(inv, 'cards', None) or {}).get(name)
    return str(row['Type Line']) if row is not None else None


def install(inv, role_map=None, labels_for=None):
    """Make inv.record() contract-grounded. inv is a SQLiteInventory (has .db and .record).
    labels_for(name) -> {role: bool}; defaults to mtg_eval's hand labels."""
    con = inv.db
    if labels_for is None:
        try:
            human_labels('')
            labels_for = human_labels
        except Exception:
            labels_for = lambda name: {}
    try:
        release = json.loads((Path(con.execute('pragma database_list').fetchone()[2]).parent / 'SOURCE_MANIFEST.json').read_text()).get('release')
    except Exception:
        release = None
    pattern_record = inv.record
    cache = {}
    def record(name):
        if name not in cache:
            cache[name] = grounded_record(pattern_record(name), contract_states(con, name), role_map, release,
                                         type_line=_type_line(inv, name), labels=labels_for(name))
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
    wrap_card(ev)
    wrap_reports(ev)
    return ev


REPORTS = ('deck', 'module', 'compare', 'upgrades', 'build', 'inventory', 'transfer', 'portfolio')


def roles_line(ev):
    rs = ev.inv.role_source
    return (f"Roles: {rs['basis']} ({rs['map_version']}, KB {rs['kb_release']}). Role counts rest on candidate "
            f"contract-to-role mappings (ROLE_MAP, unreviewed) and labelled text-pattern fallbacks.")


def wrap_reports(ev):
    """Every role-dependent report says its counts rest on candidate role mappings, and carries role_source."""
    for meth in REPORTS:
        plain = getattr(ev, meth, None)
        if plain is None: continue
        def wrapped(*a, _plain=plain, **k):
            res = _plain(*a, **k)
            if isinstance(res, dict) and 'limitations' in res:
                res['limitations'].append(roles_line(ev))
                if isinstance(res.get('data'), dict): res['data']['role_source'] = dict(ev.inv.role_source)
            return res
        setattr(ev, meth, wrapped)
    return ev


CAPABILITY_SECTION = 'Capability record (evidence per function)'


def wrap_card(ev):
    """Make Evaluator.card() show each role's basis: mtg_eval's table keeps only oracle/tag/label."""
    plain = ev.card
    def card(name, deck=None):
        res = plain(name, deck)
        n = res['title'].split(': ', 1)[1]
        rec = ev.inv.record(n)
        for heading, rows in res['sections']:
            if heading != CAPABILITY_SECTION or not isinstance(rows, list): continue
            for row in rows:
                e = (rec.get(row.get('function')) or {}).get('evidence') or {}
                row['basis'] = e.get('basis', '')
                row['contracts'] = ', '.join(e.get('contracts', []))
                row['verification'] = e.get('verification_state', '') if e.get('basis') == 'dio_contract' else ''
                row['pattern status'] = e.get('pattern_status', '')
                row['contract says'] = e.get('contract_says', '')
                row['fallback reason'] = e.get('fallback_reason', '')
        res['limitations'].append(roles_line(ev))
        return res
    ev.card = card
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
        g = grounded_record(pat, contract_states(inv.db, n), role_map, type_line=_type_line(inv, n), labels=human_labels(n))
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
