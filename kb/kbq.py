#!/usr/bin/env python3
"""Inventory discovery from SQLite (v0.2). Read-only; no workbook, no simulator, no runtime regex
over Oracle text: every reading comes from persisted rows (cards, allocations, claims, contracts,
validation queue, review overlay, derived facts). Each answer states its evidence level.

  python kbq.py card 'The Necrobloom'
  python kbq.py destinations 'Avenger of Zendikar'
  python kbq.py available token_maker --ci BG --free
  python kbq.py overlap Necrobloom
  python kbq.py unverified --deck Necrobloom
  python kbq.py theme landfall --deck Necrobloom          (themes: see THEMES)
  python kbq.py packages --ci BG --theme landfall --free   (producer -> observer links)
  python kbq.py queue --deck Necrobloom --state ready_for_review
  python kbq.py mana --pays '{C}' --ci BG                    (typed mana sources that can pay a cost)
  python kbq.py keyword Offspring --ci WUBRG                 (owned cards with a keyword in the Oracle rules text)
"""
import argparse, json, sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLORS = 'WUBRG'
BASICS = {'Forest', 'Island', 'Swamp', 'Mountain', 'Plains', 'Wastes'}

# Theme predicates over a contract's exact text, hook, effects and costs (SQL over persisted rows).
# They find candidates for review; they are not verified semantics.
THEMES = {
    'landfall': "(k.contract_json LIKE '%land.enters_battlefield%' OR lower(k.exact_text) LIKE 'landfall%' "
                "OR lower(k.exact_text) LIKE '%whenever a land you control enters%' OR lower(k.exact_text) LIKE '%whenever one or more lands%enter%')",
    'dredge': "lower(k.exact_text) LIKE '%dredge%'",
    'repeatable_recursion': "(k.operation_kind IN ('trigger','activate','continuous') AND (k.contract_json LIKE '%\"from\":\"graveyard\"%' "
                            "OR lower(k.exact_text) LIKE '%from your graveyard%' OR lower(k.exact_text) LIKE '%lands from your graveyard%'))",
    'land_search': "(lower(k.exact_text) LIKE '%search your library for%land%')",
    'land_tokens_scaling': "(lower(k.exact_text) LIKE '%for each land%' OR lower(k.exact_text) LIKE '%number of lands%' "
                           "OR lower(k.exact_text) LIKE '%lands you control%' AND lower(k.exact_text) LIKE '%equal to%' "
                           "OR lower(k.exact_text) LIKE '%land token%' OR lower(k.exact_text) LIKE '%seven or more lands%')",
    'sacrifice_conversion': "(k.contract_json LIKE '%\"family\":\"sacrifice\"%' OR (lower(k.exact_text) LIKE '%sacrifice a%:%'))",
    'self_mill': "(lower(k.exact_text) LIKE '%mill%' OR k.contract_json LIKE '%card.mill%')",
    'extra_land_drops': "(lower(k.exact_text) LIKE '%play an additional land%' OR lower(k.exact_text) LIKE '%play lands from%' "
                        "OR lower(k.exact_text) LIKE '%put a land card from your hand onto the battlefield%')",
}
# producer effect -> hooks it can feed (DIO identifiers); a link is a candidate connection, never a verified one
FEEDS = {
    'token.create': ['battlefield.enter', 'token.enters_battlefield', 'creature.enters_battlefield', 'artifact.enters_battlefield'],
    'land_to_battlefield': ['land.enters_battlefield', 'battlefield.enter'],
    'permanent.sacrifice': ['permanent.sacrifice', 'permanent.dies', 'creature.card_enters_graveyard'],
    'permanent.destroy': ['permanent.dies'],
    'card.draw': ['card.draw'], 'card.discard': ['card.discard'], 'card.mill': ['card.mill', 'graveyard.enter'],
    'life.gain': ['life.gain'], 'counter.put': ['counter.put'], 'card.return_to_battlefield': ['battlefield.enter'],
}


def connect(db):
    c = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    return c


def rows(c, sql, p=()): return [dict(r) for r in c.execute(sql, p)]


def deck_ci(c, deck):
    cis = [r['color_identity'] or '' for r in c.execute(
        "select cd.color_identity from deck_allocations a join cards cd using(card_name) where a.deck=? and a.section='Commander' and a.counts_in_deck_100=1", (deck,))]
    return ''.join(x for x in COLORS if any(x in ci for ci in cis))


def legal(card, ci):
    if card['commander_legal_stored'] != 'Legal': return False, 'not Commander legal'
    if not set(x for x in (card['color_identity'] or '') if x in COLORS) <= set(ci): return False, f"identity {card['color_identity']} outside {ci or 'C'}"
    return True, ''


def evidence(c, name):
    claims = {}
    for r in c.execute('select capability,source,claim_status from capability_claims where card_name=?', (name,)):
        claims.setdefault(r['capability'], {})[r['source']] = r['claim_status']
    rev = {r['subject_id'].split('|', 1)[1]: (r['decision'], r['applicability']) for r in
           c.execute("select subject_id,decision,applicability from effective_reviews where subject_kind='capability_claim' and card_name=?", (name,))}
    out = {}
    for cap, src in claims.items():
        st = src.get('mtg_eval.semantic_patterns')
        level = ('reviewed_' + rev[cap][0] if cap in rev and rev[cap][1] == 'current' else
                 'machine_supported' if st == 'machine_supported' else 'machine_contradicted' if st == 'machine_contradicted'
                 else 'tag_only' if 'Collection.Roles' in src or st == 'unverified_tag_only' else 'machine_inferred')
        out[cap] = level
    return out


def card(c, name):
    cd = c.execute('select * from cards where card_name=?', (name,)).fetchone()
    if not cd:
        hits = [r[0] for r in c.execute('select card_name from cards where lower(card_name) like ? limit 8', (name.lower() + '%',))]
        raise SystemExit(f'not found; did you mean: {hits}')
    q = rows(c, 'select contract_id,operation_kind,queue_state,fails,warns,review_decision,exact_text from validation_queue where card_name=? order by contract_id', (name,))
    for r in q:
        r['failed_checks'] = [f"{x['check_id']}: {x['detail']}" for x in c.execute(
            "select check_id,detail from validation_checks where contract_id=? and result='fail'", (r['contract_id'],))]
    st = c.execute('select projection_status,projected_ability_count,unread_json from projected_card_statics where card_name=?', (name,)).fetchone()
    return {'card': {k: cd[k] for k in ('card_name', 'type_line', 'mana_cost', 'color_identity', 'oracle_text', 'oracle_text_sha256', 'commander_legal_stored')},
            'identity': dict(c.execute('select * from card_identity where card_name=?', (name,)).fetchone()),
            'custody': {'owned': cd['owned_min'], 'assigned': cd['assigned'], 'free': cd['free'],
                        'locations': rows(c, 'select deck,quantity,section,status_raw from deck_allocations where card_name=? and physically_assigned=1', (name,))},
            'capabilities': evidence(c, name),
            'parser_0.3.0': {'status': st['projection_status'], 'abilities': st['projected_ability_count'], 'unread': json.loads(st['unread_json'])} if st else None,
            'rules_text': dict(c.execute('select authority,oracle_run_id,oracle_id,match_status,identity_confirmed,material_discrepancy,'
                                         'evaluator_reads,reconciliation_id from rules_text where card_name=?', (name,)).fetchone() or {}),
            'reconciliation': dict(c.execute('select category,decision,evaluator_reads,quarantine_contracts,identity_confirmed,proposed_sheet_correction '
                                             'from effective_reconciliation where card_name=?', (name,)).fetchone() or {}) or None,
            'contracts': q,
            'verification': rows(c, 'select contract_id,oracle_identity_confirmed,rules_text_current,semantic_contract_reviewed,'
                                    'runtime_compilation_complete,runtime_scenario_tested,mechanically_supported,quarantined '
                                    'from contract_verification where card_name=? order by contract_id', (name,)),
            'reviews': rows(c, 'select subject_kind,subject_id,decision,reviewer,reviewed_utc,applicability from effective_reviews where card_name=?', (name,))}


def destinations(c, name):
    cd = c.execute('select * from cards where card_name=?', (name,)).fetchone()
    held = {r['deck']: r['q'] for r in c.execute('select deck,sum(quantity) q from deck_allocations where card_name=? and physically_assigned=1 group by deck', (name,))}
    out = []
    for (d,) in c.execute('select distinct deck from active_deck_cards order by deck'):
        ci = deck_ci(c, d); ok, why = legal(cd, ci)
        src = 'already in deck' if d in held else 'free copy' if cd['free'] > 0 or name in BASICS else \
              ('transfer from ' + ', '.join(sorted(held))) if held else 'none owned'
        out.append({'deck': d, 'deck_ci': ci, 'legal': ok, 'why_not': why, 'copy_source': src if ok else None})
    return {'card': name, 'owned': cd['owned_min'], 'free': cd['free'], 'held_by': held, 'destinations': out}


def available(c, role, ci=None, free=False, limit=40):
    out = []
    for r in c.execute('select distinct card_name from capability_claims where capability=? order by card_name', (role,)):
        cd = c.execute('select * from cards where card_name=?', (r[0],)).fetchone()
        if free and cd['free'] <= 0: continue
        if ci is not None and not legal(cd, ci)[0]: continue
        lv = evidence(c, r[0]).get(role)
        out.append({'card': r[0], 'free': cd['free'], 'assigned': cd['assigned'], 'ci': cd['color_identity'], 'evidence': lv})
    rank = {'reviewed_verified': 0, 'machine_supported': 1, 'machine_inferred': 2, 'tag_only': 3, 'machine_contradicted': 4}
    out.sort(key=lambda x: (rank.get(x['evidence'], 5), -x['free'], x['card']))
    return out[:limit]


def deck_cards(c, deck):
    return [r[0] for r in c.execute('select card_name from active_deck_cards where deck=? order by card_name', (deck,))]


def overlap(c, deck, min_roles=2):
    roles, per, level = {}, {}, {}
    for n in deck_cards(c, deck):
        ev = {k: v for k, v in evidence(c, n).items() if v in ('machine_supported', 'reviewed_verified')}
        per[n] = sorted(ev)
        for k, v in ev.items(): roles.setdefault(k, []).append(n); level[k, n] = v
    # roles are detected candidates, not verified functions: machine_supported means an Oracle pattern hit nobody
    # has reviewed, and a role can be filled by cards the patterns miss (Kate, 2026-10-28, Golden Argosy audit)
    return {'deck': deck, 'evidence': 'detected role candidates: unreviewed Oracle-pattern hits (machine_supported) plus reviewed claims; '
                                      'tags excluded; cards the patterns miss are not counted',
            'role_counts': {k: len(v) for k, v in sorted(roles.items(), key=lambda x: -len(x[1]))},
            'reviewed_role_counts': {k: sum(level[k, n] == 'reviewed_verified' for n in v) for k, v in roles.items()},
            'sole_detected_candidates': {k: {'card': v[0], 'evidence': level[k, v[0]]} for k, v in roles.items() if len(v) == 1},
            'multi_role_cards': {n: r for n, r in sorted(per.items(), key=lambda x: -len(x[1])) if len(r) >= min_roles}}


def unverified(c, deck=None):
    names = deck_cards(c, deck) if deck else [r[0] for r in c.execute('select card_name from cards')]
    out = {'tag_only': [], 'machine_contradicted': [], 'contracts_without_review': 0}
    for n in names:
        for cap, lv in evidence(c, n).items():
            if lv in ('tag_only', 'machine_contradicted'): out[lv].append({'card': n, 'capability': cap})
    marks = ','.join('?' * len(names))
    out['contracts_without_review'] = c.execute(f"select count(*) from validation_queue where card_name in ({marks}) and review_decision is null", names).fetchone()[0]
    out['contract_states'] = dict(c.execute(f"select queue_state,count(*) from validation_queue where card_name in ({marks}) group by 1", names).fetchall())
    return out


def theme(c, name, deck=None, ci=None, free=False):
    where = THEMES[name]
    sql = f"""select k.card_name,k.contract_id,k.operation_kind,k.exact_text,q.queue_state,cd.free,cd.assigned,cd.color_identity
              from current_contracts k join validation_queue q using(contract_id,contract_version) join cards cd using(card_name)
              where {where}"""
    out = rows(c, sql)
    if deck: out = [r for r in out if r['card_name'] in set(deck_cards(c, deck))]
    if ci is not None:
        out = [r for r in out if legal(c.execute('select * from cards where card_name=?', (r['card_name'],)).fetchone(), ci)[0]]
    if free: out = [r for r in out if r['free'] > 0]
    return out


def packages(c, ci, theme_name=None, free=False, deck=None, limit=60):
    """Candidate engine links within a pool: producer contract -> observer contract via a shared hook."""
    import kbfacts as F
    pool = set(deck_cards(c, deck)) if deck else None
    ks = {}
    for r in c.execute('select k.contract_id,k.card_name,k.contract_json,q.queue_state,cd.free,cd.commander_legal_stored,cd.color_identity '
                       'from current_contracts k join validation_queue q using(contract_id,contract_version) join cards cd using(card_name)'):
        if pool is not None and r['card_name'] not in pool: continue
        if pool is None and free and r['free'] <= 0: continue
        if not legal(r, ci)[0]: continue
        ks[r['contract_id']] = (r['card_name'], F.loads(r['contract_json']), r['queue_state'])
    theme_ids = {r['contract_id'] for r in theme(c, theme_name)} if theme_name else None
    links = []
    for pid, (pn, pk, ps) in ks.items():
        for eff in pk['query_index']['feeds']:
            for hook in FEEDS.get(eff, []):
                for oid, (on, ok_, os_) in ks.items():
                    if on == pn: continue
                    if hook not in ok_['query_index']['hook_ids'] or ok_['query_index']['hook_subject'] == 'self': continue
                    if theme_ids is not None and pid not in theme_ids and oid not in theme_ids: continue
                    links.append({'producer': pn, 'produces': eff, 'observer': on, 'hook': hook,
                                  'connection_status': 'semantic_reviewed' if ps == os_ == 'semantic_reviewed' else 'candidate',
                                  'producer_state': ps, 'observer_state': os_})
    seen, out = set(), []
    for l in links:
        k = (l['producer'], l['observer'], l['hook'])
        if k not in seen: seen.add(k); out.append(l)
    deg = {}
    for l in out: deg[l['observer']] = deg.get(l['observer'], 0) + 1
    out.sort(key=lambda l: (-deg[l['observer']], l['observer'], l['producer']))
    return {'pool': deck or ('free copies' if free else 'all owned'), 'ci': ci, 'links': len(out),
            'observers_by_feeders': dict(sorted(deg.items(), key=lambda x: -x[1])[:20]), 'sample': out[:limit]}


def _owner_filter(c, name, ci, free, deck):
    cd = c.execute('select * from cards where card_name=?', (name,)).fetchone()
    if free and cd['free'] <= 0: return None
    if deck and not c.execute('select 1 from active_deck_cards where deck=? and card_name=?', (deck, name)).fetchone(): return None
    if ci is not None:
        ok, why = legal_rules(c, cd, ci)
        if not ok: return None
    return cd


def legal_rules(c, cd, ci):
    """Commander legality from the Oracle rules layer when a refresh matched the card, else the Sheet's stored value."""
    e = c.execute('select o.legal_commander from rules_text t join external_oracle o on o.card_name=t.card_name and o.run_id=t.oracle_run_id '
                  "where t.card_name=? and t.authority='oracle_refresh'", (cd['card_name'],)).fetchone()
    lg = (e[0] == 'legal') if e and e[0] else cd['commander_legal_stored'] == 'Legal'
    if not lg: return False, 'not Commander legal'
    if not set(x for x in (cd['color_identity'] or '') if x in COLORS) <= set(ci): return False, f"identity {cd['color_identity']} outside {ci or 'C'}"
    return True, ''


def mana_sources(c, pays=None, mode=None, color=None, ci=None, free=False, deck=None, limit=80):
    """Typed mana production by contract: what each source can add, and whether that can pay a cost (A4 payability)."""
    import mana as MANA
    out = []
    for r in c.execute("select k.contract_id,k.card_name,k.exact_text,k.contract_json,q.queue_state from current_contracts k "
                       "join validation_queue q using(contract_id,contract_version) where k.contract_json like '%mana.add%' order by k.card_name,k.contract_id"):
        k = json.loads(r['contract_json'])
        for p in k['result']['produces']:
            m = p.get('mana')
            if p['id'] != 'mana.add' or not m or p.get('granted_to_other_object'): continue
            if mode and m['mode'] != mode: continue
            try:  # a chosen colour is one of WUBRG (never colorless), fixed when the permanent enters
                pools = [pl for ch in COLORS for pl in MANA.production_pools(m, chosen=ch)] if m['mode'] == 'chosen_color' else MANA.production_pools(m)
            except ValueError: pools = []
            types = sorted({u['type'] for pl in pools for u in pl}, key='WUBRGC'.index)
            if color and color.upper() not in types: continue
            ok = None
            if pays:
                try: ok = any(MANA.can_pay(pays, pl) for pl in pools)
                except ValueError: ok = None
                if ok is not True: continue
            cd = _owner_filter(c, r['card_name'], ci, free, deck)
            if cd is None: continue
            out.append({'card': r['card_name'], 'contract_id': r['contract_id'], 'text': r['exact_text'], 'mode': m['mode'], 'amount': m['amount'],
                        'can_add': types, 'restriction': m.get('restriction'), 'scaling': m.get('scaling'), 'pays': ok,
                        'queue_state': r['queue_state'], 'free': cd['free']})
    return out[:limit]


def keyword(c, kw, ci=None, free=False, deck=None, owned=True):
    """Owned cards whose rules text (Oracle when matched) has a line starting with the keyword. SQL over persisted
    rules_text_lines; excluded rows (non-game, tokens) never appear."""
    out = []
    for r in c.execute("select l.card_name,l.line,t.authority,t.identity_confirmed,t.evaluator_reads from rules_text_lines l join rules_text t using(card_name) "
                       "where t.evaluator_reads<>'excluded' and (l.line like ? || ' %' or l.line like ? || ',%' or l.line = ?) order by l.card_name,l.line_no",
                       (kw, kw, kw)):
        cd = _owner_filter(c, r['card_name'], ci, free, deck)
        if cd is None or (owned and (cd['owned_min'] or 0) <= 0): continue
        out.append({'card': r['card_name'], 'keyword_line': r['line'].split(' (')[0], 'owned': cd['owned_min'], 'free': cd['free'],
                    'ci': cd['color_identity'], 'commander_legal': legal_rules(c, cd, 'WUBRG')[0], 'rules_authority': r['authority'],
                    'identity_confirmed': bool(r['identity_confirmed']), 'evaluator_reads': r['evaluator_reads']})
    return out


def queue(c, deck=None, state=None, limit=50):
    sql = 'select q.*,cd.free from validation_queue q join cards cd using(card_name) where 1=1'
    p = []
    if deck: sql += ' and card_name in (select card_name from active_deck_cards where deck=?)'; p.append(deck)
    if state: sql += ' and queue_state=?'; p.append(state)
    return rows(c, sql + ' order by queue_state,card_name limit ?', p + [limit])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db', default=str(HERE / 'mtg_cards_v0.2.sqlite'))
    s = ap.add_subparsers(dest='cmd', required=True)
    x = s.add_parser('card'); x.add_argument('name')
    x = s.add_parser('destinations'); x.add_argument('name')
    x = s.add_parser('available'); x.add_argument('role'); x.add_argument('--ci'); x.add_argument('--free', action='store_true'); x.add_argument('--limit', type=int, default=40)
    x = s.add_parser('overlap'); x.add_argument('deck'); x.add_argument('--min', type=int, default=2)
    x = s.add_parser('unverified'); x.add_argument('--deck')
    x = s.add_parser('theme'); x.add_argument('name', choices=sorted(THEMES)); x.add_argument('--deck'); x.add_argument('--ci'); x.add_argument('--free', action='store_true')
    x = s.add_parser('packages'); x.add_argument('--ci', required=True); x.add_argument('--theme', choices=sorted(THEMES)); x.add_argument('--free', action='store_true'); x.add_argument('--deck'); x.add_argument('--limit', type=int, default=60)
    x = s.add_parser('queue'); x.add_argument('--deck'); x.add_argument('--state'); x.add_argument('--limit', type=int, default=50)
    x = s.add_parser('mana'); x.add_argument('--pays'); x.add_argument('--mode'); x.add_argument('--color'); x.add_argument('--ci'); x.add_argument('--free', action='store_true'); x.add_argument('--deck'); x.add_argument('--limit', type=int, default=80)
    x = s.add_parser('keyword'); x.add_argument('kw'); x.add_argument('--ci'); x.add_argument('--free', action='store_true'); x.add_argument('--deck')
    a = ap.parse_args(); c = connect(a.db)
    r = {'card': lambda: card(c, a.name), 'destinations': lambda: destinations(c, a.name),
         'available': lambda: available(c, a.role, a.ci, a.free, a.limit), 'overlap': lambda: overlap(c, a.deck, a.min),
         'unverified': lambda: unverified(c, a.deck), 'theme': lambda: theme(c, a.name, a.deck, a.ci, a.free),
         'packages': lambda: packages(c, a.ci, a.theme, a.free, a.deck, a.limit), 'queue': lambda: queue(c, a.deck, a.state, a.limit),
         'mana': lambda: mana_sources(c, a.pays, a.mode, a.color, a.ci, a.free, a.deck, a.limit),
         'keyword': lambda: keyword(c, a.kw, a.ci, a.free, a.deck)}[a.cmd]()
    print(json.dumps(r, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
