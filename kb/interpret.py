#!/usr/bin/env python3
"""Append-only interpretation log: what two or more readers said a card or mechanic does, and whether they agreed.

The log (overrides/interpretations.jsonl) records *dialogic* readings of Oracle text: a question about one card or
mechanic, each party's reading with its Comprehensive Rules citations, and the outcome of the exchange. It is the
record of the reading, not a review of a KB contract. Rows here never change a contract's verification state:
every row is `verification_state: candidate`, and only Zach promotes a reading, through review.py (semantic review
of a contract, with scenarios) or a decision event. This module refuses any other state.

  python3 kb/interpret.py add --kind card --name "The Necrobloom" \\
      --question "Does the seven-names branch replace the Plant, or add a Zombie?" \\
      --readings readings.json --outcome agreed --source HO-MTG-20261107-92QA \\
      [--contract card.The%20Necrobloom.op001] [--notes ...] [--supersedes <interpretation_id>]
  python3 kb/interpret.py show [--name NAME]
  python3 kb/interpret.py verify

`readings.json` is a list of {"party", "model", "reading", "cr_citations": [...]}. `party` names who spoke
(claude:mtg, kate, zach, ...), `model` the model that produced the words (gpt-5-mini, claude-fable-5-1, human).
Each reading cites at least one of: a CR rule number (702.52, 704.5q, 106.12a), "oracle" (the Oracle text alone
decides it) or "ruling:YYYY-MM-DD" (a Scryfall ruling). A reading with no evidence is refused, so is an "agreed"
outcome with fewer than two parties.

Second party (Zach 2026-11-18, HO-MTG-20261118-KN82 Q1): a fresh-context Claude (no build history) counts as the second
party when Kate is unavailable. A reading may carry "party_kind" (builder | kate | fresh_context_claude | zach | other);
a two-party row whose readings all come from one model family is refused unless one says fresh_context_claude.
`verify` reports each agreed/contested row's pair kind (cross_family, same_family_fresh_context), derived from the
models, so rows written before this field still say which kind of second party they had.
--cr-edition (KN82 Q7) records the CR edition the readings were checked against; new rows default to 2026-11-06.
--outcome closed (KN82, C20Q(3)) closes a needs-zach row Zach could not answer: it must --supersedes that row, say
why in --notes, and may carry no readings ("[]").

Optional fields (Kate's round-17 protocol amendments, 2026-11-07; PROPOSALS Zach has not adopted, so none is
required and every one is vocabulary-checked when present):
  --layer mechanics|dio_representation|deck_role     which of the three questions the row answers (amendment 1)
  per reading: "independent": true|false, "uncertainty": "...", "scenario": "..."   recorded before seeing the
      other party's reading, with the reader's own uncertainty and a concrete scenario (amendment 2)
  --disagreement-type oracle_rules|ontology_representation|contextual_role|insufficient_evidence   only on a
      contested or needs-zach row (amendment 3)
  --scenarios scenarios.json  {"positive": "...", "near_miss": "...", "kb_output_changed": true|false|null}
      a positive scenario and a near-miss counterexample for the reading, and whether KB/evaluator output changed
      when they were run (null = not run yet) (amendment 4)

Like review.py and reconcile.py, the file is hash-chained (chain.py): each line's id is the SHA-256 of the previous
id and the record body, so editing, reordering or deleting a line breaks `verify`. The log is the only home of these
readings (DIO section 2, one home per fact); nothing replays it into the SQLite build, and mtgtools reads it only as
evidence to display. When the card is in the KB the row binds to the current Oracle text SHA, so `verify` can report
readings made against text that has since changed.

@ai-semantic-role: candidate-source
"""
import argparse, datetime, json, os, re, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kbfacts as F   # chain.py's hashing; chain.py itself is release-pinned and has no late-field rule

FIELDS = ['utc', 'subject_kind', 'card_or_mechanic', 'oracle_id', 'oracle_text_sha256', 'contract_id', 'in_kb', 'kb_release',
          'question', 'readings', 'outcome', 'verification_state', 'source', 'recorded_by', 'notes', 'supersedes',
          # optional, from Kate's round-17 amendments (proposals): absent hashes as None, so rows without them stay valid
          'layer', 'disagreement_type', 'scenarios']
# Added after the log had rows (Zach 2026-11-18, HO-MTG-20261118-KN82 Q7): hashed only when present, so the 15 rows
# written before it keep their ids (see _canon).
LATE_FIELDS = ('cr_edition',)
ID_KEY = 'interpretation_id'
DEFAULT = HERE / 'overrides' / 'interpretations.jsonl'
DEFAULT_DB = HERE / 'mtg_cards_v0.2.sqlite'
SUBJECT_KINDS = ('card', 'mechanic')
OUTCOMES = ('agreed', 'contested', 'needs-zach', 'closed')
# 'closed' (KN82, C20Q(3)): a needs-zach question Zach could not answer is closed by a row that supersedes it and says
# why in notes. It records no reading (readings may be empty) and changes nothing about any other row.
CR_EDITION_DEFAULT = '2026-11-06'   # KN82 Q7: Zach "Yes"; the CR edition in force for new rows
CR_EDITION_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
# Only state this log may hold. Promotion is Zach's, and it happens elsewhere (review.py, decisions/).
CANDIDATE = 'candidate'
CR_RE = re.compile(r'^\d{3}(\.\d+[a-z]?)?$')          # 702, 702.52, 704.5q, 106.12a
RULING_RE = re.compile(r'^ruling:\d{4}-\d{2}-\d{2}$')
READING_KEYS = ('party', 'model', 'reading', 'cr_citations')
# Kate round 17 (kairos/kate-round-17.md), amendments 1-4. Proposals: optional until Zach adopts or drops them.
LAYERS = ('mechanics', 'dio_representation', 'deck_role')                                   # 1: which question
READING_OPTIONAL = {'independent': bool, 'uncertainty': str, 'scenario': str,              # 2: independent first reading
                    'party_kind': str}                                                         # KN82 Q1, below
# KN82 Q1 (Zach 2026-11-18 "Yes"): a fresh-context Claude (no build history) counts as the second party when Kate is
# unavailable. A reading may say which kind of party gave it; when every reading in a two-party row comes from one
# model family, the non-builder reading must say fresh_context_claude, so a same-family pair is always labelled.
PARTY_KINDS = ('builder', 'kate', 'fresh_context_claude', 'zach', 'other')
FAMILIES = (('claude', 'claude'), ('gpt', 'openai'), ('o1', 'openai'), ('o3', 'openai'), ('human', 'human'))


def family(model):
    """Model family from the model name (claude-*, gpt-*, human); 'other' when unknown. Derived, never stored."""
    m = (model or '').lower()
    return next((f for pre, f in FAMILIES if m.startswith(pre)), 'other')


def pair_kind(row):
    """How a row's second party relates to the first: cross_family, same_family_fresh_context, same_family, or single."""
    rs = row.get('readings') or []
    if len({r['party'] for r in rs}) < 2: return 'single'
    if len({family(r['model']) for r in rs}) > 1: return 'cross_family'
    return 'same_family_fresh_context' if any(r.get('party_kind') == 'fresh_context_claude' for r in rs) else 'same_family'
DISAGREEMENT_TYPES = ('oracle_rules', 'ontology_representation', 'contextual_role', 'insufficient_evidence')  # 3
SCENARIO_KEYS = ('positive', 'near_miss', 'kb_output_changed')                              # 4: executable consequences


def _canon(r):
    """chain.py's canonical body, plus LATE_FIELDS only when the record carries them. chain.py is release-pinned
    (kb/MANIFEST.sha256), so the late-field rule lives here; with no late field present the hash equals chain.py's."""
    return F.dumps({**{k: r.get(k) for k in FIELDS}, **{k: r[k] for k in LATE_FIELDS if k in r}})


def read(path=DEFAULT):
    """chain.read with LATE_FIELDS: same chain and id checks, line for line."""
    p = Path(path)
    if not p.exists(): return []
    out, prev = [], ''
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'): continue
        r = json.loads(line)
        if r.get('prev') != prev: raise ValueError(f'{p.name} line {i}: hash chain broken')
        if r.get(ID_KEY) != F.sha(prev, _canon(r)): raise ValueError(f'{p.name} line {i}: {ID_KEY} does not match content')
        prev = r[ID_KEY]; out.append(r)
    return out


def _append(path, body):
    rows = read(path)
    prev = rows[-1][ID_KEY] if rows else ''
    if body.get('cr_edition') is None: body = {k: v for k, v in body.items() if k != 'cr_edition'}
    rec = dict(body, prev=prev, **{ID_KEY: F.sha(prev, _canon(body))})
    with open(path, 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + '\n')
    return rec


def citation_ok(c):
    return isinstance(c, str) and (c == 'oracle' or bool(CR_RE.match(c)) or bool(RULING_RE.match(c)))


def check(body):
    """Refuse rows that would not be honest about who read what, on what evidence, and with what standing."""
    if body.get('verification_state') != CANDIDATE:
        raise ValueError(f'verification_state must be {CANDIDATE!r}: this log never promotes; Zach does, elsewhere')
    if body.get('subject_kind') not in SUBJECT_KINDS: raise ValueError(f'subject_kind must be one of {SUBJECT_KINDS}')
    if body.get('outcome') not in OUTCOMES: raise ValueError(f'outcome must be one of {OUTCOMES}')
    for k in ('card_or_mechanic', 'question', 'source', 'recorded_by'):
        if not body.get(k): raise ValueError(f'{k} is required')
    if body['subject_kind'] == 'card' and body.get('in_kb') and not body.get('oracle_id'):
        raise ValueError('a card that is in the KB must carry its oracle_id')
    readings = body.get('readings')
    if body['outcome'] == 'closed':
        if not body.get('supersedes'): raise ValueError('a closed row must supersede the needs-zach row it closes')
        if not body.get('notes'): raise ValueError('a closed row must say in notes why the question is closed')
        if not isinstance(readings, list): raise ValueError('readings must be a list')
    elif not isinstance(readings, list) or not readings: raise ValueError('readings must be a non-empty list')
    for i, r in enumerate(readings):
        if not isinstance(r, dict) or not set(READING_KEYS) <= set(r) or not set(r) <= set(READING_KEYS) | set(READING_OPTIONAL):
            raise ValueError(f'reading {i}: keys must be {READING_KEYS}, optionally {tuple(READING_OPTIONAL)}')
        for k in ('party', 'model', 'reading'):
            if not isinstance(r[k], str) or not r[k].strip(): raise ValueError(f'reading {i}: {k} is required')
        cites = r['cr_citations']
        if not isinstance(cites, list) or not cites: raise ValueError(f'reading {i}: cr_citations must name at least one of a CR rule, "oracle" or "ruling:YYYY-MM-DD"')
        for c in cites:
            if not citation_ok(c): raise ValueError(f'reading {i}: citation {c!r} is not a CR rule number, "oracle" or "ruling:YYYY-MM-DD"')
        for k, t in READING_OPTIONAL.items():   # amendment 2, when used
            if k in r and (not isinstance(r[k], t) or (t is str and not r[k].strip())):
                raise ValueError(f'reading {i}: {k} must be a non-empty {t.__name__}')
        if 'party_kind' in r and r['party_kind'] not in PARTY_KINDS:
            raise ValueError(f'reading {i}: party_kind must be one of {PARTY_KINDS}')
    parties = {r['party'] for r in readings}
    if body['outcome'] in ('agreed', 'contested') and len(parties) < 2:
        raise ValueError(f'outcome {body["outcome"]!r} needs readings from at least two parties; one party is needs-zach')
    if body['outcome'] in ('agreed', 'contested') and pair_kind(body) == 'same_family':
        raise ValueError('every reading comes from one model family: the second party counts only as a fresh-context '
                         'Claude (no build history), so mark its reading party_kind: fresh_context_claude (KN82 Q1)')
    ce = body.get('cr_edition')
    if ce is not None and not (isinstance(ce, str) and CR_EDITION_RE.match(ce)):
        raise ValueError('cr_edition must be the CR edition date, YYYY-MM-DD')
    if body.get('supersedes') and not re.fullmatch(r'[0-9a-f]{64}', body['supersedes']):
        raise ValueError('supersedes must be an interpretation_id')
    check_optional(body)


def check_optional(body):
    """Kate's round-17 amendments as optional fields. Absent is fine (they are proposals); present means well-formed."""
    if body.get('layer') is not None and body['layer'] not in LAYERS:
        raise ValueError(f'layer must be one of {LAYERS}')
    dt = body.get('disagreement_type')
    if dt is not None:
        if dt not in DISAGREEMENT_TYPES: raise ValueError(f'disagreement_type must be one of {DISAGREEMENT_TYPES}')
        if body['outcome'] == 'agreed': raise ValueError('an agreed row has no disagreement_type')
    sc = body.get('scenarios')
    if sc is not None:
        if not isinstance(sc, dict) or set(sc) != set(SCENARIO_KEYS):
            raise ValueError(f'scenarios keys must be exactly {SCENARIO_KEYS}')
        for k in ('positive', 'near_miss'):   # a pair: a reading with only a confirming case has not been tested
            if not isinstance(sc[k], str) or not sc[k].strip(): raise ValueError(f'scenarios.{k} is required when scenarios are given')
        if sc['kb_output_changed'] not in (True, False, None):
            raise ValueError('scenarios.kb_output_changed must be true, false or null (not run yet)')


def bind_to_kb(db, name, contract_id):
    """What the KB currently says about the card: identity, text hash, release. None of it is a judgement."""
    out = {'in_kb': False, 'oracle_id': None, 'oracle_text_sha256': None, 'kb_release': None}
    if not Path(db).exists(): return out
    con = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        row = con.execute('select c.oracle_text_sha256, i.oracle_id from cards c left join card_identity i on i.card_name=c.card_name '
                          'where c.card_name=?', (name,)).fetchone()
        if row:
            out.update(in_kb=True, oracle_text_sha256=row[0], oracle_id=row[1])
        manifest = Path(db).resolve().parent / 'SOURCE_MANIFEST.json'   # the release name lives beside the DB, as mtgtools reads it
        if manifest.exists():
            out['kb_release'] = json.loads(manifest.read_text(encoding='utf-8')).get('release')
        if contract_id:
            k = con.execute('select card_name from current_contracts where contract_id=?', (contract_id,)).fetchone()
            if not k: raise ValueError(f'unknown contract {contract_id}')
            if k[0] != name: raise ValueError(f'contract {contract_id} belongs to {k[0]!r}, not {name!r}')
    finally:
        con.close()
    return out


def add(path, body):
    check(body)
    if body['outcome'] == 'closed':   # it must close an open needs-zach row in this log, not any id
        target = next((r for r in read(path) if r[ID_KEY] == body['supersedes']), None)
        if not target or target['outcome'] != 'needs-zach':
            raise ValueError('a closed row must supersede a needs-zach row in this log')
    return _append(path, body)


def stale(path, db):
    """Interpretation ids whose card's stored Oracle text has changed since the row was written."""
    if not Path(db).exists(): return None
    con = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        cur = {n: s for n, s in con.execute('select card_name,oracle_text_sha256 from cards')}
    finally:
        con.close()
    return [r[ID_KEY] for r in read(path) if r.get('in_kb') and cur.get(r['card_or_mechanic']) != r.get('oracle_text_sha256')]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--file', default=str(DEFAULT)); ap.add_argument('--db', default=str(DEFAULT_DB))
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add')
    a.add_argument('--kind', required=True, choices=SUBJECT_KINDS); a.add_argument('--name', required=True, help='card name as the KB spells it, or the mechanic')
    a.add_argument('--question', required=True); a.add_argument('--outcome', required=True, choices=OUTCOMES)
    a.add_argument('--readings', required=True, help='JSON file: a list of {party, model, reading, cr_citations}; - for stdin')
    a.add_argument('--source', required=True, help='what authorised the round (handoff id, decision id)')
    a.add_argument('--contract', help='KB contract id the question is about, if one exists')
    a.add_argument('--oracle-id', help='for a card that is not in the KB')
    a.add_argument('--recorded-by', default=None, help='actor id (default: RELAYKIT_ACTOR or interpret.py)')
    a.add_argument('--notes'); a.add_argument('--supersedes')
    # Kate round 17 amendments (proposals): optional, vocabulary-checked when given
    a.add_argument('--layer', choices=LAYERS, help='which of the three questions this row answers (mechanics / DIO representation / deck role)')
    a.add_argument('--disagreement-type', choices=DISAGREEMENT_TYPES, help='why the parties differ; contested or needs-zach rows only')
    a.add_argument('--scenarios', help='JSON file: {"positive", "near_miss", "kb_output_changed": true|false|null}; - for stdin')
    a.add_argument('--cr-edition', default=CR_EDITION_DEFAULT, help=f'CR edition the readings were checked against (default {CR_EDITION_DEFAULT})')
    s = sub.add_parser('show'); s.add_argument('--name')
    sub.add_parser('verify')
    x = ap.parse_args(argv)
    if x.cmd == 'add':
        def load(arg): return json.load(sys.stdin) if arg == '-' else json.loads(Path(arg).read_text(encoding='utf-8'))
        readings = load(x.readings)
        scenarios = load(x.scenarios) if x.scenarios else None
        kb = bind_to_kb(x.db, x.name, x.contract) if x.kind == 'card' else {'in_kb': False, 'oracle_id': None, 'oracle_text_sha256': None, 'kb_release': None}
        if x.oracle_id and not kb['in_kb']: kb['oracle_id'] = x.oracle_id
        body = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'subject_kind': x.kind,
                'card_or_mechanic': x.name, 'contract_id': x.contract, **kb, 'question': x.question, 'readings': readings,
                'outcome': x.outcome, 'verification_state': CANDIDATE, 'source': x.source,
                'recorded_by': x.recorded_by or os.environ.get('RELAYKIT_ACTOR') or 'interpret.py', 'notes': x.notes, 'supersedes': x.supersedes,
                'layer': x.layer, 'disagreement_type': x.disagreement_type, 'scenarios': scenarios, 'cr_edition': x.cr_edition}
        print(json.dumps(add(x.file, body), indent=1, ensure_ascii=False))
    elif x.cmd == 'show':
        rows = read(x.file)
        print(json.dumps([r for r in rows if not x.name or r['card_or_mechanic'] == x.name], indent=1, ensure_ascii=False))
    else:
        rows = read(x.file)
        by = {}
        for r in rows: by[r['outcome']] = by.get(r['outcome'], 0) + 1
        # Kate's measure (round 17, a proposal): what matters is whether readings were tested, not how many agreed
        tested = sum(1 for r in rows if r.get('scenarios'))
        superseded = {r['supersedes'] for r in rows if r.get('supersedes')}
        pairs = {}
        for r in rows:
            if r['outcome'] in ('agreed', 'contested'): pairs[pair_kind(r)] = pairs.get(pair_kind(r), 0) + 1
        print(json.dumps({'lines': len(rows), 'chain': 'ok', 'by_outcome': by, 'stale_text': stale(x.file, x.db),
                          'open_needs_zach': [r[ID_KEY] for r in rows if r['outcome'] == 'needs-zach' and r[ID_KEY] not in superseded],
                          'second_party': pairs,
                          'with_scenarios': tested, 'kb_output_changed': sum(1 for r in rows if (r.get('scenarios') or {}).get('kb_output_changed') is True),
                          'promoted': 0, 'note': 'every row is a candidate; promotion happens in review.py or decisions/, never here'}, indent=1))


if __name__ == '__main__':
    main()
