"""`mtgtools reading NAME`: what the interpretation log says about one card or mechanic, as JSON (D-0033).

A reading page is derived, never stored (DIO section 2, one home per fact). It joins the rows of
kb/overrides/interpretations.jsonl about NAME and, when the KB database is present, the card's current Oracle text hash
and its KB contracts. It parses no card text (P-01), promotes nothing (P-03: `candidate` is the only state it can
print, whatever a row says), judges no usefulness (P-04) and writes no file. A rendered page, if anyone wants one, is a
gitignored build output of tools/render_readings.py, never of this module (D-0033 (b)).

@ai-semantic-role: candidate-source
"""
from . import kb  # puts kb/ on sys.path
import interpret  # kb/interpret.py: the log's own reader, which checks the hash chain

from .claims import claim

CANDIDATE = 'candidate'
LIMITS = ['Every reading here is a candidate: two readers agreeing is not a review, and nothing in the log changes a '
          "contract's verification state (INTERPRETATIONS_POLICY.md). Only Zach promotes, through review.py or a decision event.",
          'A page lists only rows whose subject is NAME. It does not yet follow a card to the mechanic rows it inherits, '
          'or a deck to the readings it turns on (--deck): both need a hook-to-mechanic join that is not built.',
          'Absence of a row means nobody has asked, not that the question is settled.']


def _rows(log):
    try:
        return interpret.read(log), 'ok'
    except ValueError as e:                    # a broken chain is reported, not hidden; no row is trusted then
        return [], f'broken: {e}'


def _current_sha(c, name):
    if c is None:
        return None
    r = c.execute('select oracle_text_sha256 from cards where card_name=?', (name,)).fetchone()
    return r[0] if r else None


def _row_view(r, superseded_by, current_sha):
    text_changed = None
    if r.get('in_kb') and current_sha is not None:
        text_changed = current_sha != r.get('oracle_text_sha256')
    return {'interpretation_id': r['interpretation_id'], 'utc': r.get('utc'), 'subject_kind': r.get('subject_kind'),
            'question': r.get('question'), 'outcome': r.get('outcome'), 'layer': r.get('layer'),
            'disagreement_type': r.get('disagreement_type'), 'scenarios': r.get('scenarios'), 'contract_id': r.get('contract_id'),
            'readings': [{k: x.get(k) for k in ('party', 'model', 'reading', 'cr_citations', 'uncertainty', 'scenario', 'party_kind', 'independent')
                          if x.get(k) is not None} for x in (r.get('readings') or [])],
            'verification_state': CANDIDATE, 'logged_state': r.get('verification_state'),
            'oracle_text_changed_since': text_changed, 'superseded_by': superseded_by,
            'source': r.get('source'), 'notes': r.get('notes'), 'supersedes': r.get('supersedes')}


def reading(name, c=None, log=interpret.DEFAULT):
    """Page for NAME (card or mechanic, matched case-insensitively). `c` is an optional read-only KB connection."""
    rows, chain = _rows(log)
    later = {r['supersedes']: r['interpretation_id'] for r in rows if r.get('supersedes')}
    mine = [r for r in rows if (r.get('card_or_mechanic') or '').casefold() == name.casefold()]
    canonical = mine[0]['card_or_mechanic'] if mine else name
    sha = _current_sha(c, canonical)
    views = [_row_view(r, later.get(r['interpretation_id']), sha) for r in mine]
    current = [v for v in views if not v['superseded_by']]
    by_outcome = {}
    for v in current:
        by_outcome.setdefault(v['outcome'], []).append(v['interpretation_id'])
    contracts = None
    if c is not None and sha is not None:
        contracts = [{k: x[k] for k in ('contract_id', 'queue_state', 'failed_checks')} for x in kb.card(c, canonical)['contracts']]
    gaps = [{'interpretation_id': v['interpretation_id'], 'note': v['notes']} for v in current if v['notes']]
    data = {'subject': canonical, 'banner': {'verification_state': CANDIDATE, 'promoted': 0, 'chain': chain,
                                             'log_rows': len(rows), 'log_head': rows[-1]['interpretation_id'] if rows else None},
            'current': current, 'superseded': [v for v in views if v['superseded_by']], 'by_outcome': by_outcome,
            'kb_contracts': contracts, 'notes': gaps, 'limits': LIMITS}
    claims = []
    for v in current:
        parties = ', '.join(f"{x.get('party')} ({x.get('model')})" for x in v['readings']) or 'no reading recorded'
        ev = [v['interpretation_id']] + ([v['contract_id']] if v['contract_id'] else [])
        if v['oracle_text_changed_since']:
            ev.append('oracle_text_changed_since_reading')
        claims.append(claim(f"{v['outcome']}: {v['question']} Readers: {parties}.", 'mechanics', CANDIDATE, evidence=ev))
    if chain != 'ok':
        claims.append(claim(f'The interpretation log failed its hash-chain check ({chain}); no row is shown.', 'mechanics',
                            CANDIDATE, evidence=[str(log)]))
    return data, claims
