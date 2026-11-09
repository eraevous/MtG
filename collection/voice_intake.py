#!/usr/bin/env python3
"""MTG transcript/CSV entries → inventory first → batch lookup → reviewable staging.

Input is speech-to-text, NOT raw audio. Never writes inventory or KB.
Python 3.10+, standard library only. See docs/VOICE_INTAKE.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

if __package__:
    from .mtgcollection import fold, name_matcher
else:
    from mtgcollection import fold, name_matcher

COLLECTION_URL = "https://api.scryfall.com/cards/collection"
NAMED_URL = "https://api.scryfall.com/cards/named"
USER_AGENT = "eraevous-MtG-voice-intake/0.1 (+https://github.com/eraevous/MtG)"
MIN_REQUEST_INTERVAL = 0.55  # Scryfall's card endpoints: no faster than 2/s
WORD_QTY = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
QTY = r"(?:\d+|(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)"
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
    alternate_name: str = ""
    finish: str = ""
    language: str = ""

    def identifier(self):
        if self.set_code and self.collector_number:
            return {"set": self.set_code, "collector_number": self.collector_number}
        if self.name:
            return {"name": self.name, **({"set": self.set_code} if self.set_code else {})}
        return None


def parse(text):
    chunks = re.split(r"(?:\r?\n|;|\bnext card\b|\bnew card\b)", text, flags=re.I)
    return [parse_line(t.strip(" ,.: \t"), i)
            for i, t in enumerate((c for c in chunks if c.strip(" ,.: \t")), 1)]


def parse_line(raw, line):
    e = _parse_line(raw, line)
    # A bare number word may belong to the card name, not its quantity.
    word = re.match(r"^(one|two|three|four|five|six|seven|eight|nine|ten)\b(.*)$", raw, re.I)
    if e.name and word and not re.match(r"^\s+(?:x\b|copies?\b|cards?\s+of\b)", word[2], re.I):
        original = _parse_line(raw, line, quantity=False)
        if original.name and original.name != e.name:
            e.alternate_name = original.name
    return e


def _parse_line(raw, line, quantity=True):
    e = Entry(line, raw)
    t = raw.strip().strip(".;")
    prefix = re.match(rf"^(?P<n>{QTY})\s*(?:x\s*|copies?\s+of\s+|cards?\s+of\s+|copies?\s+)?(?P<rest>.+)$", t, re.I)
    if quantity and prefix and not re.match(r"^(?:number|#)\b", prefix["rest"], re.I):
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


def csv_rows(text):
    """Read a named-header CSV, including canonical exports with a title preamble."""
    lines = list(csv.reader(io.StringIO(text), strict=True))
    for offset, header in enumerate(lines[:12]):
        if "Card Name" in header or "Name" in header:
            if len(header) != len(set(header)) or {"Card Name", "Name"} <= set(header):
                raise ValueError("CSV has duplicate or ambiguous name headers")
            name_key = "Card Name" if "Card Name" in header else "Name"
            rows = []
            for line, cells in enumerate(lines[offset + 1:], offset + 2):
                if not any(c.strip() for c in cells):
                    continue
                if len(cells) > len(header):
                    raise ValueError(f"CSV row {line} has more cells than headers")
                row = dict(zip(header, cells + [""] * (len(header) - len(cells))))
                rows.append((line, row, name_key))
            return rows
    raise ValueError("CSV requires Card Name or Name header in the first 12 rows")


def parse_csv(text):
    """Structured capture for photos, lists and other adapters; no quantity-word parsing."""
    entries = []
    for line, row, name_key in csv_rows(text):
        quantity = row.get("Quantity", "1").strip()
        valid_quantity = bool(re.fullmatch(r"[0-9]+", quantity)) and int(quantity) > 0
        e = Entry(line, row.get("Original Dictation") or row.get("Source Text") or row[name_key],
                  quantity=int(quantity) if valid_quantity else 0,
                  name=row[name_key].strip(), set_code=row.get("Set Code", "").strip().lower(),
                  collector_number=row.get("Collector Number", "").strip(),
                  finish=row.get("Finish", "").strip(), language=row.get("Language", "").strip())
        if not valid_quantity:
            e.error = "Quantity must be a positive whole number"
        elif e.collector_number and not e.set_code:
            e.error = "Collector number without an identifiable set code"
        elif not e.identifier():
            e.error = "Not enough information to identify a card"
        entries.append(e)
    return entries


class InventoryIndex:
    """Read-only identity hints, never ownership or a current-Oracle authority.

    Only explicit physical Set Code / Collector Number columns constrain printing.
    A Scryfall URL in a card-level inventory is NOT a record of the owned printing.
    """
    def __init__(self, text):
        self.rows = []
        self.by_name, self.by_folded, self.by_print = {}, {}, {}
        for line, row, name_key in csv_rows(text):
            name = row[name_key].strip()
            if not name:
                raise ValueError(f"Inventory row {line} has no card name")
            item = {"name": name, "set": row.get("Set Code", "").strip().lower(),
                    "collector_number": row.get("Collector Number", "").strip(), "line": line}
            self.rows.append(item)
            self.by_name.setdefault(name.casefold(), []).append(item)
            if fold(name):
                self.by_folded.setdefault(fold(name), []).append(item)
            if item["set"] and item["collector_number"]:
                self.by_print.setdefault((item["set"], item["collector_number"]), []).append(item)
        self.provenance = {"text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                           "rows": len(self.rows), "freshness": "not_verified",
                           "role": "identity_hints_only_not_current_ownership"}

    def match(self, entry):
        if entry.error or entry.quantity <= 0 or not entry.identifier():
            return None
        # A snapshot cannot prove the other quantity/name interpretation does not exist.
        if entry.alternate_name:
            return None
        exact_print = bool(entry.set_code and entry.collector_number)
        if exact_print:
            candidates = self.by_print.get((entry.set_code, entry.collector_number), [])
            if entry.name and any(fold(c["name"]) != fold(entry.name) for c in candidates):
                return None
        else:
            candidates = self.by_name.get(entry.name.casefold()) or self.by_folded.get(fold(entry.name), [])
            if entry.set_code:
                candidates = [c for c in candidates if c["set"] == entry.set_code]
        # Duplicate holdings are fine, conflicting identities/normalized aliases are not.
        if len({c["name"] for c in candidates}) != 1:
            return None
        return {"name": candidates[0]["name"], "set_code": entry.set_code or None,
                "collector_number": entry.collector_number or None,
                "scryfall_id": None, "scryfall_uri": None,
                "method": "inventory-exact", "status": "accepted", "reason": None,
                "identity_scope": "set_and_number" if exact_print else "card_name",
                "printing_status": "recorded_set_and_number_match" if exact_print else "not_identified",
                "inventory_rows": [c["line"] for c in candidates]}


class RateLimitError(RuntimeError):
    """Abort the entire intake after a rate-limit response."""


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
                raise RateLimitError("Scryfall rate limited (429): stop and retry later") from err
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
        except RateLimitError:
            raise
        except RuntimeError:
            return None


def unique_name_match(cards, name):
    """Use collection precedence, but do not choose an arbitrary tied printing."""
    winner = matching_card(cards, name)
    if winner is None:
        return None
    for candidate in cards:
        # A lower-priority face cannot displace a full name. A tied identity can.
        other = matching_card([candidate, winner], name)
        if other.get("id") != winner.get("id"):
            return None
    return winner


def matching_card(cards, name):
    winner = name_matcher(cards)(name)
    if winner and "//" in name and fold(name) != fold(winner.get("name", "")):
        return None
    return winner


def resolve(entries, client, fuzzy_budget=5, inventory=None):
    entries = list(entries)
    local = [inventory.match(e) if inventory else None for e in entries]
    identifiers, seen = [], set()
    for e, hit in zip(entries, local):
        if hit or e.quantity <= 0:
            continue
        ident = e.identifier() if not e.error else None
        if ident is None:
            continue
        options = [ident]
        if e.alternate_name and not (e.set_code and e.collector_number):
            options.append({"name": e.alternate_name,
                            **({"set": e.set_code} if e.set_code else {})})
        for option in options:
            key = json.dumps(option, sort_keys=True)
            if key not in seen:
                seen.add(key)
                identifiers.append(option)
    cards = client.collection(identifiers) if identifiers else []
    by_print = {(c.get("set", "").lower(), str(c.get("collector_number", ""))): c for c in cards}

    results, fuzzy_used = [], 0
    fuzzy_cache = {}
    for e, hit in zip(entries, local):
        row = {"line": e.line, "spoken": e.raw, "quantity": e.quantity,
               "requested_name": e.name or None, "requested_set": e.set_code or None,
               "requested_number": e.collector_number or None,
               "finish": e.finish or None, "language": e.language or None}
        if e.alternate_name:
            row["alternate_name"] = e.alternate_name
            row["alternate_quantity"] = 1
        if e.error or e.quantity <= 0 or not e.identifier():
            results.append({**row, "status": "unresolved",
                            "reason": e.error or "invalid quantity or no identifier"})
            continue
        if hit:
            results.append({**row, **hit})
            continue
        if e.set_code and e.collector_number:
            card = by_print.get((e.set_code, e.collector_number))
            candidates = [card] if card else []
        else:
            # Prefer the requested set even if another entry returned another printing.
            candidates = [c for c in cards if not e.set_code or c.get("set", "").lower() == e.set_code]
            if not candidates:
                candidates = cards  # Preserve a mismatched result for explicit review below.
            card = None
        primary = unique_name_match(candidates, e.name) if e.name else None
        alternate = unique_name_match(candidates, e.alternate_name) if e.alternate_name else None
        match = lambda name: matching_card(candidates, name)
        ambiguous_quantity = bool(e.alternate_name and match(e.name) and match(e.alternate_name))
        name = e.name
        if alternate or (e.alternate_name and not primary):
            name = e.alternate_name
            row.update(quantity=1, requested_name=name)
            row.update(alternate_name=e.name, alternate_quantity=e.quantity)
        if not (e.set_code and e.collector_number):
            card = alternate or primary
        method = "batch-exact"
        if card is None and name and not (e.set_code and e.collector_number):
            if name not in fuzzy_cache and fuzzy_used < fuzzy_budget:
                fuzzy_used += 1
                fuzzy_cache[name] = client.fuzzy(name)
            card = fuzzy_cache.get(name)
            method = "fuzzy-suggestion"
        if not card or card.get("object") == "error":
            results.append({**row, "status": "unresolved",
                            "reason": "not found (or fuzzy budget exhausted)"})
            continue
        mismatch = bool(name and e.set_code and e.collector_number
                        and not matching_card([card], name))
        set_mismatch = bool(e.set_code and e.set_code != card.get("set", "").lower())
        reason = ("spoken set differs from resolved printing" if set_mismatch else
                  "number word may be quantity or part of card name; confirm first" if ambiguous_quantity else
                  "spoken name differs from set+number printing" if mismatch else
                  "fuzzy name suggestion; confirm first" if method == "fuzzy-suggestion" else None)
        results.append({**row, "status": "review" if reason else "accepted", "reason": reason,
                        "name": card.get("name"), "set_code": card.get("set"),
                        "collector_number": str(card.get("collector_number", "")),
                        "scryfall_id": card.get("id"), "scryfall_uri": card.get("scryfall_uri"),
                        "method": method})
    source = "Inventory snapshot" if inventory else "Scryfall API"
    if inventory and client.requests:
        source += " + Scryfall API"
    return {"source": source,
            "inventory": inventory.provenance if inventory else None,
            "inventory_matches": sum(hit is not None for hit in local),
            "limits": ["Inventory matches are recorded identity hints, not current ownership or Oracle verification.",
                       "An absent inventory name is not evidence of being unowned.",
                       "Unknown printing, finish or language is never inferred from an existing copy."],
            "entries": len(entries), "requests": client.requests,
            "accepted": sum(r["status"] == "accepted" for r in results),
            "review": sum(r["status"] == "review" for r in results),
            "unresolved": sum(r["status"] == "unresolved" for r in results),
            "cards": results}


def csv_content(report):
    out = io.StringIO()
    writer = csv.DictWriter(out,
        fieldnames=["Card Name", "Quantity", "Set Code", "Collector Number", "Finish", "Language", "Method", "Notes"],
        lineterminator="\n")
    writer.writeheader()
    for r in report["cards"]:
        if r["status"] == "accepted":
            writer.writerow({"Card Name": r["name"], "Quantity": r["quantity"],
                             "Set Code": r["set_code"], "Collector Number": r["collector_number"],
                             "Finish": r.get("finish"), "Language": r.get("language"),
                             "Method": r["method"],
                             "Notes": f"intake line {r['line']}; {r['method']}"})
    return out.getvalue()


def validate_paths(inputs, outputs):
    """Reject input/output and output/output aliases before lookup or any writes."""
    paths = [(label, Path(path), False) for label, path in inputs if path]
    paths += [(label, Path(path), True) for label, path in outputs if path]
    for i, (left_label, left, left_output) in enumerate(paths):
        for right_label, right, right_output in paths[i + 1:]:
            if not (left_output or right_output):
                continue
            aliases = left.resolve() == right.resolve()
            if not aliases and left.exists() and right.exists():
                aliases = left.samefile(right)
            if aliases:
                raise ValueError(f"{left_label} and {right_label} must refer to different files")


def main(argv=None):
    p = argparse.ArgumentParser(description="Inventory-first transcript/CSV intake, then batch Scryfall lookup; no inventory edits")
    p.add_argument("transcript", help="UTF-8 file or '-' for stdin")
    p.add_argument("--inventory", help="Local inventory CSV identity hints (read-only; no ownership assertions)")
    p.add_argument("--input-format", choices=("text", "csv"), default="text",
                   help="Transcript text, or structured CSV from any capture adapter")
    p.add_argument("--csv", help="Write exact accepted entries (review before importing)")
    p.add_argument("--review", help="Write complete review JSON (default stdout)")
    p.add_argument("--fuzzy-budget", type=int, default=5, help="Max fuzzy suggestions (0–20)")
    a = p.parse_args(argv)
    if not 0 <= a.fuzzy_budget <= 20:
        p.error("--fuzzy-budget must be between 0 and 20")
    try:
        if a.transcript == "-":
            import os
            import stat
            try:
                stdin_stat = os.fstat(sys.stdin.fileno())
            except (AttributeError, OSError, ValueError):
                stdin_stat = None
            if stdin_stat is not None and stat.S_ISREG(stdin_stat.st_mode):
                for label, path in (("CSV output", a.csv), ("review output", a.review)):
                    if path:
                        output = Path(path)
                        if output.exists() and os.path.samestat(stdin_stat, output.stat()):
                            raise ValueError(f"capture input and {label} must refer to different files")
        validate_paths([("capture input", None if a.transcript == "-" else a.transcript), ("inventory input", a.inventory)],
                       [("CSV output", a.csv), ("review output", a.review)])
        text = sys.stdin.read() if a.transcript == "-" else Path(a.transcript).read_text(encoding="utf-8-sig")
        entries = parse_csv(text) if a.input_format == "csv" else parse(text)
        inventory = InventoryIndex(Path(a.inventory).read_text(encoding="utf-8-sig")) if a.inventory else None
    except (OSError, ValueError, csv.Error) as exc:
        p.error(str(exc))
    if not entries:
        p.error("no cards found in transcript")
    client = ScryfallClient()
    try:
        report = resolve(entries, client, a.fuzzy_budget, inventory=inventory)
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
