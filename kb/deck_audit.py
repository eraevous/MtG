#!/usr/bin/env python3
"""Quantitative semantic-readiness audit of one deck, from SQLite only.

For every nonland card: recorded Oracle text, candidate operations, contracts by validation state,
cached 0.3.0 typed projections, unread clauses, review (verified) status, and runtime compiler
eligibility. Then the focus themes (landfall, dredge, repeatable recursion, land search, land
tokens/scaling, sacrifice-resource conversion, ...) with why each blocked contract is blocked.

  python deck_audit.py Necrobloom --out reports/   ->  audit_Necrobloom.md / .csv / .json
"""
import argparse, collections, csv, json, shlex
from pathlib import Path
import kbq

FOCUS = ['landfall', 'dredge', 'repeatable_recursion', 'land_search', 'land_tokens_scaling', 'sacrifice_conversion', 'self_mill', 'extra_land_drops']
CHECK_LABEL = {
    'C03_operation_kind': 'operation kind unclassified', 'C04_hook': 'trigger has no hook / hook outside registry',
    'C05_face': 'multi-face clause not located on one face', 'C06_source_annotation': 'source row needs manual annotation',
    'C07_costs': 'cost missing or unparsed', 'C08_effects': 'no effect recorded', 'C09_bound_semantics': 'unbound branch/condition/scaling/modes',
    'C10_zone_transitions': 'zone transition unbound', 'C13_not_reminder_text': 'clause is reminder text', 'C14_mana_typed': 'mana production not typed', 'C11_executable_shape': '0.3.0 action missing text or disagrees'}


def eligibility(states, has_action, compiled):
    if compiled: return 'compiled (semantic review + lossless)'
    if any(s == 'ready_for_review' and a for s, a in zip(states, has_action)): return 'eligible after review'
    if any(s == 'ready_for_review' for s in states): return 'reviewable, no executable action'
    if states: return 'blocked'
    return 'no candidate operations'


def audit(c, deck):
    names = [n for n in kbq.deck_cards(c, deck)]
    rows = []
    for n in names:
        cd = c.execute('select * from cards where card_name=?', (n,)).fetchone()
        if 'Land' in (cd['type_line'] or '').split(' // ')[0] and 'Creature' not in (cd['type_line'] or ''): continue
        st = c.execute('select * from projected_card_statics where card_name=?', (n,)).fetchone()
        qs = kbq.rows(c, 'select q.contract_id,q.queue_state,k.proposed_action_json is not null as has_action from validation_queue q '
                         'join operation_contracts k using(contract_id,contract_version) where q.card_name=?', (n,))
        compiled = c.execute('select count(*) from runtime_verified_actions where card_name=?', (n,)).fetchone()[0]
        reviews = c.execute("select count(*) from effective_reviews where card_name=? and decision='verified' and applicability='current'", (n,)).fetchone()[0]
        unread = json.loads(st['unread_json']) if st else []
        rows.append({'card': n, 'type_line': cd['type_line'], 'oracle_recorded': bool(cd['oracle_text']), 'oracle_sha12': (cd['oracle_text_sha256'] or '')[:12],
                     'candidate_ops': c.execute('select count(*) from candidate_operations where card_name=?', (n,)).fetchone()[0],
                     'contracts_ready': sum(q['queue_state'] == 'ready_for_review' for q in qs),
                     'contracts_blocked': sum(q['queue_state'] == 'blocked' for q in qs),
                     'contracts_with_action': sum(bool(q['has_action']) for q in qs),
                     'projected_abilities': st['projected_ability_count'] if st else 0, 'projection_status': st['projection_status'] if st else 'none',
                     'unread_clauses': len(unread), 'unread_text': ' | '.join(unread),
                     'verified_reviews': reviews, 'compiled_actions': compiled,
                     'runtime_eligibility': eligibility([q['queue_state'] for q in qs], [bool(q['has_action']) for q in qs], compiled)})
    names_nl = {r['card'] for r in rows}
    themes = {}
    for t in FOCUS:
        hits = [r for r in kbq.theme(c, t) if r['card_name'] in names_nl]
        reasons = collections.Counter()
        for h in hits:
            for (chk,) in c.execute("select check_id from validation_checks where contract_id=? and result='fail'", (h['contract_id'],)):
                reasons[CHECK_LABEL.get(chk, chk)] += 1
        themes[t] = {'cards': sorted({h['card_name'] for h in hits}), 'contracts': len(hits),
                     'ready_for_review': sum(h['queue_state'] == 'ready_for_review' for h in hits),
                     'blocked': sum(h['queue_state'] == 'blocked' for h in hits),
                     'semantic_reviewed': sum(h['queue_state'] == 'semantic_reviewed' for h in hits), 'quarantined': sum(h['queue_state'] == 'quarantined' for h in hits),
                     'block_reasons': dict(reasons.most_common()),
                     'contracts_detail': [{'card': h['card_name'], 'state': h['queue_state'], 'text': h['exact_text']} for h in hits]}
        for r in rows:
            if r['card'] in themes[t]['cards']: r.setdefault('themes', []).append(t)
    for r in rows: r['themes'] = ', '.join(r.get('themes', []))
    return rows, themes


def render(deck, rows, themes):
    tot = collections.Counter(r['runtime_eligibility'] for r in rows)
    ps = collections.Counter(r['projection_status'] for r in rows)
    L = [f'# Semantic readiness audit: {deck} (v0.2)', '',
         f'Nonland cards: **{len(rows)}**. Candidate operations: **{sum(r["candidate_ops"] for r in rows)}**. '
         f'Contracts ready for review: **{sum(r["contracts_ready"] for r in rows)}**; blocked: **{sum(r["contracts_blocked"] for r in rows)}**. '
         f'Verified reviews: **{sum(r["verified_reviews"] for r in rows)}**. Compiled runtime actions: **{sum(r["compiled_actions"] for r in rows)}**.', '',
         f'0.3.0 projection status: ' + ', '.join(f'{k} {v}' for k, v in ps.most_common()) +
         f'. Unread clauses across the deck: **{sum(r["unread_clauses"] for r in rows)}**.', '',
         '## Runtime compiler eligibility', '', '| Eligibility | Cards |', '|---|---:|'] + \
        [f'| {k} | {v} |' for k, v in tot.most_common()] + ['', '## Focus themes', '',
         '| Theme | Cards | Contracts | Ready | Blocked | Reviewed | Main block reasons |', '|---|---:|---:|---:|---:|---:|---|'] + \
        [f"| {t} | {len(v['cards'])} | {v['contracts']} | {v['ready_for_review']} | {v['blocked']} | {v['semantic_reviewed']} | " +
         '; '.join(f'{k} ({n})' for k, n in list(v['block_reasons'].items())[:3]) + ' |' for t, v in themes.items()]
    for t, v in themes.items():
        if not v['contracts']: continue
        L += ['', f'### {t}', ''] + [f"- **{d['card']}** ({d['state']}): {d['text'][:170]}" for d in v['contracts_detail']]
    L += ['', '## Every nonland card', '', '| Card | Ops | Ready | Blocked | Projected | Status | Unread | Verified | Eligibility | Themes |', '|---|---:|---:|---:|---:|---|---:|---:|---|---|']
    for r in sorted(rows, key=lambda r: (r['runtime_eligibility'], -r['unread_clauses'], r['card'])):
        L.append(f"| {r['card']} | {r['candidate_ops']} | {r['contracts_ready']} | {r['contracts_blocked']} | {r['projected_abilities']} | {r['projection_status']} | {r['unread_clauses']} | {r['verified_reviews']} | {r['runtime_eligibility']} | {r['themes']} |")
    return '\n'.join(L) + '\n'


def packet(c, deck):
    """Contracts a reviewer can act on now: ready for review and carrying an executable action."""
    import scenarios as SC
    names, reg = set(kbq.deck_cards(c, deck)), SC.load()
    L = [f'# Review packet: {deck}', '', 'Each contract below passed every validation check. A verified review is a semantic judgement (the contract '
         'says what the Oracle text says) and must cite at least one scenario id that passes on the contract; it does not certify runtime '
         'behaviour. Runtime certificates come from the build, only for lossless compiles with a passing runtime scenario.', '']
    for r in c.execute("select q.contract_id,q.card_name,k.exact_text,k.proposed_action_json,q.warns from validation_queue q join operation_contracts k "
                       "using(contract_id,contract_version) where q.queue_state='ready_for_review' and k.proposed_action_json is not null order by q.card_name"):
        if r['card_name'] not in names: continue
        a = json.loads(r['proposed_action_json'])
        warn = [f"{x['check_id']}: {x['detail']}" for x in c.execute("select check_id,detail from validation_checks where contract_id=? and result='warn'", (r['contract_id'],))]
        L += [f"## {r['card_name']}", '', f"> {r['exact_text']}", '',
              f"- action: kind `{a.get('kind')}`, hook `{json.dumps(a.get('hook'))}`, cost `{json.dumps(a.get('cost'))}`, outputs `{json.dumps(a.get('outputs'))}`, gates `{json.dumps(a.get('gates'))}`"]
        L += [f'- warning: {w}' for w in warn]
        loss = [f"{a}: {b}" for a, b in c.execute('select loss_code,detail from compile_losses where contract_id=?', (r['contract_id'],))]
        L += [f'- runtime: lossy compile, so no runtime certificate even after review ({"; ".join(loss[:4])})' if loss else '- runtime: lossless compile']
        tests = [s for s in reg.values() if s['contract_id'] == r['contract_id']]
        if tests:
            L += ['', '```', f"python review.py --db mtg_cards_v0.2.sqlite --overlay overrides/review_overlay.jsonl add --contract {shlex.quote(r['contract_id'])} \\",
                  "    --decision verified --reviewer Zach --source 'Oracle text + CR' " + ' '.join(f'--test {shlex.quote(t["id"])}' for t in tests), '```', '']
        else:
            L += ['- no scenario covers this contract yet: add one to scenarios/*.json (it must pass on the contract) before a verified review is possible', '']
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('deck'); ap.add_argument('--db', default=str(kbq.HERE / 'mtg_cards_v0.2.sqlite')); ap.add_argument('--out', default='reports')
    a = ap.parse_args(); c = kbq.connect(a.db)
    rows, themes = audit(c, a.deck)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / f'audit_{a.deck}.md').write_text(render(a.deck, rows, themes), encoding='utf-8')
    with open(out / f'audit_{a.deck}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out / f'audit_{a.deck}.json').write_text(json.dumps({'deck': a.deck, 'cards': rows, 'themes': themes}, indent=1, ensure_ascii=False), encoding='utf-8')
    (out / f'review_packet_{a.deck}.md').write_text(packet(c, a.deck), encoding='utf-8')
    print(f'{len(rows)} nonland cards; wrote {out}/audit_{a.deck}.md and review_packet_{a.deck}.md')


if __name__ == '__main__':
    main()
