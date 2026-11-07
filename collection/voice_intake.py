#!/usr/bin/env python3
"""Dictated MTG card entries → Scryfall batch lookup → reviewable CSV and JSON.

Input is speech-to-text, NOT raw audio. Never writes inventory or KB.
Python 3.10+, standard library only. See docs/VOICE_INTAKE.md.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

COLLECTION_URL = "https://api.scryfall.com/cards/collection"
NAMED_URL = "https://api.scryfall.com/cards/named"
USER_AGENT = "eraevous-MtG-voice-intake/0.1 (+https://github.com/eraevous/MtG)"
MIN_REQUEST_INTERVAL = 0.55  # Scryfall's card endpoints: no faster than 2/s
WORD_QTY = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
QTY = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
SET_CODE = r"(?:[A-Za-z0-9]{2,6}|[A-Za-z](?:\s+[A-Za-z]){1,5})"
NUMBER = r"[0-9]+[A-Za-z★*]?"


@dataclass
class Entry:
    line: int
    raw: str
    quantity: int = 1
    name: str = ""
    set_code: str = ""
    collector_number: str = ""
    error: str = ""

    def identifier(self):
        if self.set_code and self.collector_number:
            return {"set": self.set_code, "collector_number": self.collector_number}
        if self.name:
            return {"name": self.name}
        return None


def fold(text):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", text)
                  .encode("ascii", "ignore").decode().lower())


def parse(text):
    chunks = re.split(r"(?:\r?\n|;|\bnext card\b|\bnew card\b)", text, flags=re.I)
    return [parse_line(t.strip(" ,.: \t"), i)
            for i, t in enumerate(c for c in chunks if c.strip(" ,.: \t"), 1)]


def parse_line(raw, line):
    e = Entry(line, raw)
    t = raw.strip().strip(".;")
    prefix = re.match(rf"^(?P<n>{QTY})\s*(?:x\s*|copies?\s+of\s+|cards?\s+of\s+|copies?\s+)?(?P<rest>.+)$", t, re.I)
    if prefix and not re.match(r"^(?:number|#)\b", prefix["rest"], re.I):
        n = prefix["n"].lower()
        e.quantity = int(n) if n.isdecimal() else WORD_QTY[n]
        t = prefix["rest"].strip()
    printed = re.match(rf"^(?P<name>.+?)\s*\((?P<set>[A-Za-z0-9]{{2,6}})\)\s*#?(?P<num>{NUMBER})$", t, re.I)
    if printed:
        e.name, e.set_code, e.collector_number = (
            printed["name"].strip(), printed["set"].lower(), printed["num"])
        return e
    # Spoken metadata requires explicit 'set' / 'number'; don't guess full set names.
    set_match = re.search(
        rf"\bset(?:\s+(?:code|symbol))?\s+(?P<code>{SET_CODE})(?=\s*(?:,|\bnumber\b|\bcollector\b|\bcard\s+number\b|$))",
        t, re.I)
    num_match = re.search(
        rf"\b(?:collector\s+number|card\s+number|number|#)\s*(?P<num>{NUMBER})(?!\w)", t, re.I)
    if set_match:
        code = re.sub(r"[\s-]+", "", set_match["code"]).lower()
        e.set_code = code if re.fullmatch(r"[a-z0-9]{2,6}", code) else ""
        if not e.set_code:
            e.error = "Set name/code ambiguous; say the 2–6 character set code"
    if num_match:
        e.collector_number = num_match["num"]
    if set_match or num_match:
        for start, end in sorted([m.span() for m in (set_match, num_match) if m], reverse=True):
            t = t[:start] + t[end:]
        t = re.sub(r"^(?:from|of|card)\s+", "", t.strip(" ,:-"), flags=re.I)
        t = re.sub(r"\bfrom\s*$", "", t, flags=re.I)
        e.name = t.strip(" ,:-")
        if e.collector_number and not e.set_code:
            e.error = e.error or "Collector number without an identifiable set code"
        if e.set_code and not e.collector_number and not e.name:
            e.error = "Set code without name or number"
        return e
    shorthand = re.fullmatch(rf"(?P<set>[A-Za-z0-9]{{2,6}})\s+#?(?P<num>{NUMBER})", t)
    if shorthand:
        e.set_code, e.collector_number = shorthand["set"].lower(), shorthand["num"]
        return e
    e.name = t.strip(" ,:-")
    if len(e.name) < 2 or e.name.isdecimal():
        e.error = "Not enough information to identify a card"
    return e


class ScryfallClient:
    def __init__(self, opener=None, sleep=None, clock=None):
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleep or time.sleep
        self.clock = clock or time.monotonic
        self.last_call = None
        self.requests = 0

    def request(self, url, payload=None):
        if self.last_call is not None:
            delay = MIN_REQUEST_INTERVAL - (self.clock() - self.last_call)
            if delay > 0:
                self.sleep(delay)
        self.last_call = self.clock()
        headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            url, method="POST" if payload is not None else "GET",
            data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        self.requests += 1
        try:
            with self.opener(req, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as err:
            if err.code == 429:
                raise RuntimeError("Scryfall rate limited (429): stop and retry later") from err
            raise RuntimeError(f"Scryfall HTTP {err.code}; inventory unchanged") from err
        except (urllib.error.URLError, TimeoutError) as err:
            raise RuntimeError(f"Scryfall unavailable: {err}; inventory unchanged") from err

    def collection(self, identifiers):
        cards = []
        for offset in range(0, len(identifiers), 75):
            data = self.request(COLLECTION_URL, {"identifiers": identifiers[offset:offset + 75]})
            cards.extend(data.get("data", []))
        return cards

    def fuzzy(self, name):
        url = NAMED_URL + "?" + urllib.parse.urlencode({"fuzzy": name})
        try:
            return self.request(url)
        except RuntimeError:
            return None


def resolve(entries, client, fuzzy_budget=5):
    identifiers, seen = [], set()
    for e in entries:
        ident = e.identifier() if not e.error else None
        if ident is None:
            continue
        key = json.dumps(ident, sort_keys=True)
        if key not in seen:
            seen.add(key)
            identifiers.append(ident)
    cards = client.collection(identifiers) if identifiers else []
    by_print = {(c.get("set", "").lower(), str(c.get("collector_number", ""))): c for c in cards}
    by_name = {}
    for c in cards:
        for name in [c.get("name", "")] + [face.get("name", "") for face in c.get("card_faces", [])]:
            if name:
                by_name.setdefault(fold(name), []).append(c)

    results, fuzzy_used = [], 0
    for e in entries:
        row = {"line": e.line, "spoken": e.raw, "quantity": e.quantity,
               "requested_name": e.name or None, "requested_set": e.set_code or None,
               "requested_number": e.collector_number or None}
        if e.error or not e.identifier():
            results.append({**row, "status": "unresolved", "reason": e.error or "no identifier"})
            continue
        if e.set_code and e.collector_number:
            card = by_print.get((e.set_code, e.collector_number))
        else:
            matches = by_name.get(fold(e.name), [])
            card = matches[0] if len({c.get("id") for c in matches}) == 1 else None
        method = "batch-exact"
        if card is None and e.name and not (e.set_code and e.collector_number) and fuzzy_used < fuzzy_budget:
            fuzzy_used += 1
            card = client.fuzzy(e.name)
            method = "fuzzy-suggestion"
        if not card or card.get("object") == "error":
            results.append({**row, "status": "unresolved",
                            "reason": "not found (or fuzzy budget exhausted)"})
            continue
        spoken_names = {fold(card.get("name", ""))} | {
            fold(face.get("name", "")) for face in card.get("card_faces", [])}
        mismatch = bool(e.name and e.set_code and e.collector_number
                        and fold(e.name) not in spoken_names)
        status = "review" if mismatch or method == "fuzzy-suggestion" else "accepted"
        results.append({**row, "status": status,
                        "reason": "spoken name differs from set+number printing" if mismatch else
                                  "fuzzy name suggestion; confirm first" if method == "fuzzy-suggestion" else None,
                        "name": card.get("name"), "set_code": card.get("set"),
                        "collector_number": str(card.get("collector_number", "")),
                        "scryfall_id": card.get("id"), "scryfall_uri": card.get("scryfall_uri"),
                        "method": method})
    return {"source": "Scryfall API", "entries": len(entries), "requests": client.requests,
            "accepted": sum(r["status"] == "accepted" for r in results),
            "review": sum(r["status"] == "review" for r in results),
            "unresolved": sum(r["status"] == "unresolved" for r in results),
            "cards": results}


def csv_content(report):
    out = io.StringIO()
    writer = csv.DictWriter(out,
        fieldnames=["Card Name", "Quantity", "Set Code", "Collector Number", "Notes"],
        lineterminator="\n")
    writer.writeheader()
    for r in report["cards"]:
        if r["status"] == "accepted":
            writer.writerow({"Card Name": r["name"], "Quantity": r["quantity"],
                             "Set Code": r["set_code"], "Collector Number": r["collector_number"],
                             "Notes": f"voice-intake line {r['line']}"})
    return out.getvalue()


def main(argv=None):
    p = argparse.ArgumentParser(description="Fast batch Scryfall lookup from speech-to-text; no inventory edits")
    p.add_argument("transcript", help="UTF-8 file or '-' for stdin")
    p.add_argument("--csv", help="Write exact accepted entries (review before importing)")
    p.add_argument("--review", help="Write complete review JSON (default stdout)")
    p.add_argument("--fuzzy-budget", type=int, default=5, help="Max fuzzy suggestions (0–20)")
    a = p.parse_args(argv)
    if not 0 <= a.fuzzy_budget <= 20:
        p.error("--fuzzy-budget must be between 0 and 20")
    text = sys.stdin.read() if a.transcript == "-" else Path(a.transcript).read_text(encoding="utf-8-sig")
    entries = parse(text)
    if not entries:
        p.error("no cards found in transcript")
    client = ScryfallClient()
    try:
        report = resolve(entries, client, a.fuzzy_budget)
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc), "entries": len(entries),
                          "requests": client.requests}), file=sys.stderr)
        return 2
    if a.review:
        Path(a.review).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if a.csv:
        Path(a.csv).write_text(csv_content(report), encoding="utf-8")
    if not a.review:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['accepted']} accepted, {report['review']} review, "
              f"{report['unresolved']} unresolved; {report['requests']} Scryfall calls")
    return 0 if not (report["review"] or report["unresolved"]) else 1


if __name__ == "__main__":
    sys.exit(main())
