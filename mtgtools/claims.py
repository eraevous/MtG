"""Claim records shared by every verb: what is asserted, what kind of support it needs, and how far it is established.

A claim's grade depends on its kind. Mechanical legality, deck performance and preference are graded separately, so
`decision_grade` on one kind never implies the others (Kate, 2026-10-27, amendment 2).
"""

KINDS = ('inventory', 'rules_text', 'mechanics', 'performance', 'preference')

# contract queue states that count as semantically established (P-03); everything else stays a candidate
REVIEWED_STATES = {'semantic_reviewed'}


def grade(kind, support):
    """decision_grade | exploratory | not_system_gradable, from the claim kind and its support level."""
    if kind not in KINDS:
        raise ValueError(f'unknown claim kind {kind!r}; expected one of {KINDS}')
    if kind == 'preference':
        return 'not_system_gradable'          # preferences belong to the person, recorded in a deck charter
    if kind == 'performance':
        return 'exploratory'                  # v0 has no validated performance evidence (evaluator is descriptive)
    if kind == 'inventory':
        return 'decision_grade' if support == 'collection_snapshot' else 'exploratory'
    if kind == 'rules_text':
        return 'decision_grade' if support == 'oracle' else 'exploratory'
    return 'decision_grade' if support in REVIEWED_STATES else 'exploratory'


def claim(text, kind, support, evidence=None, discovery=None, **extra):
    c = {'text': text, 'kind': kind, 'support': support, 'grade': grade(kind, support), 'evidence': evidence or []}
    if discovery:
        c['discovery'] = discovery            # requested | unrequested: retrieval vs. discovery (Kate, 2026-10-27)
    c.update(extra)
    return c
