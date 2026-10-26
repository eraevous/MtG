"""Cut safety: coarse screen, then clause audit, then a label. No label means "safe to cut".

  protected                 a coarse flag fires (engine, large body, mythic, sole source,
                            thin commander-plan role, unpriced card, access loss >= 3 points)
  human_review_required     screened, but a consequential clause is unparsed or unpriced,
                            the record holds unknown evidence, or another card names it
  mechanically_audited_cut  screened and every clause is priced by the evaluator
"""
from . import access as A
from .inventory import BASICS
from .semantics import clause_audit


def audit_cut(state, card, models=None):
    inv = state.inv
    s = A.certify_cut(state, card, models)
    ca = clause_audit(inv.cards[card]['Oracle Text'], card)
    blockers = [f"{r['status']}: \"{r['clause'][:90]}\"" + (f" [{'; '.join(r['features'])}]" if r.get('features') else '')
                for r in ca if r['status'] in ('unparsed', 'unpriced feature', 'parsed, unpriced function')]
    unknown = sorted(f for f, v in inv.record(card).items() if v['status'] in ('tag_only', 'contradicted'))
    if unknown: blockers.append('unknown evidence (tag or label disagrees with rules): ' + ', '.join(unknown))
    short = card.split(',')[0].split(' // ')[0].lower()
    refs = sorted(o for o in set(state.library) | set(state.commanders) if o not in (card, A.BLANK)
                  and short in str(inv.cards[o]['Oracle Text']).lower())
    if refs: blockers.append('named by other cards: ' + ', '.join(refs))
    label = 'protected' if s['flags'] else 'human_review_required' if blockers else 'mechanically_audited_cut'
    return {'card': card, 'label': label, 'screened': not s['flags'], 'coarse_flags': s['flags'], 'audit_blockers': blockers,
            'clauses': ca, 'access_loss_T7': s['total_access_loss_T7'], 'role_delta': s['role_delta'], 'module_delta': s['module_delta']}


def audit_deck(state, protect=()):
    """label -> rows, each sorted by measured access loss (lowest first)."""
    ms = A._models(state)
    rows = [audit_cut(state, n, ms) for n in sorted(set(state.library)) if n not in BASICS and n != A.BLANK
            and not ms[n].is_land and n not in protect]
    by = {}
    for r in rows: by.setdefault(r['label'], []).append(r)
    for k in by: by[k].sort(key=lambda r: (r['access_loss_T7'], r['card']))
    return by
