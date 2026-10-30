"""Look up the Deck Interaction Ontology (DIO) itself: the base v3.1.1, its 2026-10-09 addendum and the compatibility
addendum A1-A7. These documents govern formal representation (codex_++/project.purpose.md); the KB contracts are
candidates written in their vocabulary. This module only finds and quotes sections. It interprets nothing and needs
no database, so an agent can consult the ontology even when the KB is absent."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    ('DIO v3.1.1', ROOT / 'kb' / 'reference_sources' / 'MTG DECK INTERACTION ONTOLOGY v3_1_1.md'),
    ('DIO v3.1.1 addendum 2026-10-09', ROOT / 'kb' / 'reference_sources' / 'MTG DECK INTERACTION ONTOLOGY v3.1.1 — ADDENDUM(1).md'),
    ('DIO compatibility addendum A1-A7', ROOT / 'kb' / 'addendum' / 'DIO_v3.1.1_compat_addendum_v0.1.md'),
]
# Markdown headings, or the addendum's numbered bold lines ("**1.2 A reference is not ...**")
HEADING = re.compile(r'^(?:(#{1,6})\s+(.+?)|\*\*(\d+(?:\.\d+)*\.?\s+[^*]+?)\*\*)\s*$')
# Where to start for common questions; section numbers refer to DIO v3.1.1 unless the source is named.
READING_MAP = [
    ('Is this a real connection?', 'DIO v3.1.1 §7 (three checks before verified), §1 (gate rule)'),
    ('What does this card do, formally?', 'DIO v3.1.1 §11 (annotation procedure), §4 hooks, §5 operations'),
    ('Does state survive blink, bounce, copy, face-down?', 'DIO v3.1.1 §6.4 persistence table; addendum §2-§3'),
    ('Unconventional interactions and structural search', 'DIO v3.1.1 §9 (searches over qualified structure), §10 route patterns'),
    ('Packages, engines and loops', 'DIO v3.1.1 §8 modules, maturity ladder (a loop is verified only when it closes)'),
    ('Fuel, feedstock, sacrifice economy', 'addendum §6 contextual resource flow'),
    ('Replacement effects, references, event identity', 'addendum §1 and §4'),
    ('KB contract fields (actor, tapped_for_mana, typed mana, act_time, keywords)', 'compatibility addendum A1-A7'),
]


def sections():
    """Every section of every DIO source: (source, path, line, heading trail, text)."""
    out = []
    for label, path in SOURCES:
        if not path.exists():
            continue
        lines = path.read_text(encoding='utf-8').splitlines()
        trail, start, body = [], 1, []

        def flush():
            if trail and any(x.strip() for x in body):
                out.append({'source': label, 'file': str(path.relative_to(ROOT)), 'line': start,
                            'heading': ' > '.join(t for _, t in trail), 'text': '\n'.join(body).strip()})

        for i, line in enumerate(lines, 1):
            m = HEADING.match(line)
            if m:
                flush()
                title = (m.group(2) or m.group(3)).strip()
                level = len(m.group(1)) if m.group(1) else 2 + title.split()[0].rstrip('.').count('.')
                trail = [t for t in trail if t[0] < level] + [(level, title)]
                start, body = i, []
            else:
                body.append(line)
        flush()
    return out


def lookup(term, limit=5, max_chars=2500):
    """Sections that best match term, heading matches first. Returns (data, claims): doctrine, not claims about cards."""
    words = [w for w in re.findall(r'[\w.§-]+', term.lower()) if len(w) > 1 or w.isdigit()]
    if not words:
        raise ValueError('dio needs a term, such as "persistence", "blink", "connection" or "6.4"')
    num = term.strip().lstrip('§')
    scored = []
    for s in sections():
        head, text = s['heading'].lower(), s['text'].lower()
        score = sum(5 * head.count(w) + text.count(w) for w in words)
        if re.match(r'^\d+(\.\d+)*$', num) and re.search(rf'(^|> ){re.escape(num)}\.?\s', s['heading']):
            score += 100
        if score:
            scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    hits = []
    for score, s in scored[:limit]:
        text = s['text']
        hits.append({**s, 'score': score, 'text': text[:max_chars] + ('…' if len(text) > max_chars else ''),
                     'truncated': len(text) > max_chars})
    missing = [str(p.relative_to(ROOT)) for _, p in SOURCES if not p.exists()]
    data = {'authority': 'formal representation: DIO v3.1.1, its addendum and the compatibility addendum A1-A7 '
                         '(codex_++/project.purpose.md). Mechanical truth is Oracle text and the rules.',
            'sections': hits, 'matched': len(scored), 'missing_sources': missing, 'reading_map': [
                {'question': q, 'read': r} for q, r in READING_MAP]}
    return data, []
