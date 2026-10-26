"""Fetch complete set membership from the Scryfall API (one oracle identity per card, all printings in the set).

    python3 -I fetch_sets.py tla tle eoe eoc tmt tmc trk trc --out data/sets/

Each set is cached as data/sets/<code>.json with the set record and the members (oracle_id, name, collector
number, rarity, type_line, keywords). A set already cached is not fetched again unless --refresh is given and the
set's Scryfall record changed. Requests are spaced 150 ms apart (Scryfall asks for 50-100 ms).
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

API = 'https://api.scryfall.com'
UA = {'User-Agent': 'mtg-grammar-layer/0.2 (personal research)', 'Accept': 'application/json'}


def get(url):
    time.sleep(0.15)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def fetch(code, out, refresh=False):
    path = os.path.join(out, code + '.json')
    rec = get(f'{API}/sets/{code}')
    if os.path.exists(path) and not refresh:
        old = json.load(open(path))
        if old['set'].get('card_count') == rec.get('card_count'):
            return old
    members = []
    url = f'{API}/cards/search?' + urllib.parse.urlencode({'q': f'e:{code}', 'unique': 'prints', 'order': 'set', 'include_extras': 'false'})
    while url:
        page = get(url)
        for c in page['data']:
            members.append({'oracle_id': c.get('oracle_id') or (c.get('card_faces') or [{}])[0].get('oracle_id'),
                            'name': c['name'], 'collector_number': c['collector_number'], 'rarity': c.get('rarity'),
                            'type_line': c.get('type_line'), 'keywords': c.get('keywords', []), 'released_at': c.get('released_at')})
        url = page.get('next_page') if page.get('has_more') else None
    d = {'set': {k: rec.get(k) for k in ('code', 'name', 'set_type', 'released_at', 'card_count', 'parent_set_code')},
         'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'members': members}
    json.dump(d, open(path, 'w'), indent=0)
    return d


def first_seen(codes, out):
    """Earliest printing date of each keyword used in the given sets (one search per keyword, cached)."""
    path = os.path.join(out, 'keyword_first_seen.json')
    have = json.load(open(path)) if os.path.exists(path) else {}
    kws = set()
    for c in codes:
        for m in json.load(open(os.path.join(out, c + '.json')))['members']:
            kws.update(k.lower() for k in m.get('keywords', []))
    for k in sorted(kws - set(have)):
        url = f'{API}/cards/search?' + urllib.parse.urlencode({'q': f'keyword:"{k}"', 'unique': 'prints', 'order': 'released', 'dir': 'asc'})
        try:
            page = get(url)
            c = page['data'][0]
            have[k] = c.get('released_at')
        except Exception as e:  # a keyword Scryfall cannot search is recorded as unknown
            have[k] = None
    json.dump(have, open(path, 'w'), indent=0, sort_keys=True)
    return have


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('codes', nargs='+')
    ap.add_argument('--out', default='data/sets')
    ap.add_argument('--refresh', action='store_true')
    ap.add_argument('--first-seen', action='store_true', help='also record the earliest printing date of each keyword')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for c in a.codes:
        d = fetch(c, a.out, a.refresh)
        print(c, d['set']['name'], len(d['members']), 'printings', len({m['oracle_id'] for m in d['members']}), 'cards')
    if a.first_seen:
        fs = first_seen(a.codes, a.out)
        print(len(fs), 'keywords dated')
