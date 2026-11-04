"""Saga chapters and token copies (C-024): the contract shapes a Saga or copy deck needs.

Standard library only. Two drafted readings, both candidates (never reviewed by this module):

  chapter(clause, face_type, face_text)
      A chapter ability ("I, II, III — ...", "II — Crescent Fang — ...") on a Saga face is a triggered ability (CR 714.2b).
      It triggers when a lore counter put on that Saga makes the number of lore counters reach or pass the chapter number
      (CR 714.2c). A Saga enters with one lore counter and gets one after its controller's draw step (CR 714.3a-b); once
      it has at least as many lore counters as its final chapter and no chapter ability of it is on the stack, it is
      sacrificed (CR 714.4). Read ahead lets it enter with more (CR 702.155).

  copies(clause, name)
      "Create a token that's a copy of target nonlegendary enchantment you control" and populate. A token copy takes the
      copied object's copiable values, including its abilities (CR 707.2, 111.4), so the copy's own enter triggers and,
      for a Saga, its chapter abilities belong to the token. "Put up to three lore counters on it" afterwards puts the
      counters on the token.

The Comprehensive Rules references are the rules authority; this module only records which rule a reading relies on.
"""
import re
import unicodedata

DRAFTER = 'saga-copy-0.1.0'

ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
CHAPTER = re.compile(r'^\s*((?:I|II|III|IV|V|VI|VII|VIII|IX|X)(?:\s*,\s*(?:I|II|III|IV|V|VI|VII|VIII|IX|X))*)\s*[—–-]\s*(.*)$', re.S)
NAMED = re.compile(r'^([^—–.:"]{1,40}?)\s*[—–]\s*(.*)$', re.S)   # "Crescent Fang — Search your library ..."


def _norm(s):
    s = unicodedata.normalize('NFKC', str(s or '')).replace('−', '-')
    return re.sub(r'\s+', ' ', s).strip()


def chapters_on(face_text):
    """Every chapter number printed on a face, in order."""
    out = set()
    for line in str(face_text or '').split('\n'):
        m = CHAPTER.match(_norm(line))
        if m:
            out |= {ROMAN[x.strip()] for x in m.group(1).split(',')}
    return sorted(out)


def chapter(clause, face_type, face_text):
    """The chapter reading of a clause on a Saga face, or None. face_text is the whole Oracle text of that face."""
    if 'saga' not in (face_type or '').lower():
        return None
    m = CHAPTER.match(_norm(clause))
    if not m:
        return None
    nums = [ROMAN[x.strip()] for x in m.group(1).split(',')]
    body = m.group(2)
    nm = NAMED.match(body)
    name = None
    if nm and not re.match(r'^(?:you|target|each|create|put|draw|search|return|exile|destroy|look|add)\b', nm.group(1), re.I):
        name, body = nm.group(1).strip(), nm.group(2)
    every = chapters_on(face_text) or nums
    final = max(every)
    low = _norm(face_text).lower()
    return {
        'drafter': DRAFTER, 'chapters': nums, 'chapter_name': name, 'body': body.strip(), 'final_chapter': final, 'all_chapters': every,
        'read_ahead': bool(re.search(r'\bread ahead\b', low)),
        'trigger': {'id': 'counter.put', 'counter_kind': 'lore', 'counter_holder': 'permanent', 'subject': 'this',
                    'condition': 'for each chapter N listed, the number of lore counters on this Saga goes from below N to N or more'
                                 + (f" (one trigger per chapter: {', '.join(map(str, nums))})" if len(nums) > 1 else f' (N = {nums[0]})'),
                    'rule': 'CR 714.2b-c'},
        'lifecycle': {'enters_with': {'kind': 'lore', 'amount': 1, 'rule': 'CR 714.3a'},
                      'after_draw_step': {'kind': 'lore', 'amount': 1, 'rule': 'CR 714.3b'},
                      'sacrificed_after_final': {'final_chapter': final, 'rule': 'CR 714.4'}},
    }


COPY = re.compile(r"\bcreate (?P<n>a|an|one|two|three|four|five|x|that many|\w+) (?:tapped (?:and attacking )?)?tokens? that(?:'s| is| are) "
                  r"(?:a )?cop(?:y|ies) of (?P<obj>.+?)(?=, except\b|\. |\.$|$| tapped\b| that\b| for each\b)(?:, except (?P<exc>[^.]+))?", re.I)
SELF = re.compile(r'^(?:this (?:creature|artifact|enchantment|permanent|saga|land|card)|it|~)$')


def copies(clause, name=''):
    """Token-copy readings in a clause: [{'source', 'filter', 'except', 'then_counters', 'rule'}]."""
    low = _norm(clause).lower()
    low = re.sub(r'\([^)]*\)', '', low)
    short = {x.lower() for x in {name, name.split(' // ')[0], name.split(',')[0]} if len(x) > 3}
    out = []
    for m in COPY.finditer(low):
        obj = m.group('obj').strip()
        for s in sorted(short, key=len, reverse=True):
            obj = obj.replace(s, '~')
        if obj.startswith(('target ', 'up to one target ', 'another target ')):
            source, filt = 'target', re.sub(r'^(?:up to one |another )?target ', '', obj)
        elif SELF.match(obj):
            source, filt = 'self' if obj != 'it' else 'referent', None
        elif obj.startswith(('a ', 'an ')):
            source, filt = 'chosen', re.sub(r'^an? ', '', obj)
        else:
            source, filt = 'referent', obj
        out.append({'source': source, 'filter': filt, 'object_text': m.group('obj').strip(), 'except': m.group('exc'),
                    'then_counters': _then_counters(low[m.end():]), 'rule': 'CR 707.2, 111.4: the token has the copied object\'s abilities'})
    if re.search(r'\bpopulate\b', low):
        out.append({'source': 'chosen', 'filter': 'creature token you control', 'object_text': 'populate', 'except': None,
                    'then_counters': None, 'rule': 'populate (CR 701): a copy of a creature token you control'})
    return out


def _then_counters(rest):
    m = re.search(r"(?:(if it's an? (\w+)), )?put (up to )?(a|an|one|two|three|four|five|\w+) (lore|\+1/\+1|-1/-1|\w+) counters? on (?:it|that token|the token)\b", rest)
    if not m:
        return None
    n = {'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}.get(m.group(4), m.group(4))
    return {'kind': m.group(5), 'amount': n, 'up_to': bool(m.group(3)), 'condition': m.group(1), 'condition_type': m.group(2),
            'recipient': 'created_token', 'text': m.group(0)}


def bound_conditions(copy_list):
    """Condition phrases these readings bind, so the drafter does not report them as unbound."""
    return [c['then_counters']['condition'] for c in copy_list if c.get('then_counters') and c['then_counters'].get('condition')]


def chapters_reached(have_after_enter, added, saga_chapters):
    """Which chapters trigger on a Saga that enters with `have_after_enter` lore counters and then gets `added` more."""
    top = have_after_enter + (added or 0)
    return [n for n in saga_chapters if n <= top]
