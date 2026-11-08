"""No-network checks for fast MTG voice intake."""
import csv
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collection.voice_intake import parse, parse_line, resolve, csv_content, ScryfallClient, COLLECTION_URL, NAMED_URL


def card(name="Sol Ring", set_code="cmm", n="396"):
    return {"object": "card", "id": set_code + ":" + n, "name": name,
            "set": set_code, "collector_number": n, "scryfall_uri": "https://scryfall.com/card/"}


class Response(io.BytesIO):
    def __init__(self, payload):
        super().__init__(json.dumps(payload).encode("utf-8"))


class FakeTransport:
    def __init__(self, available=None, fuzzy=None):
        self.available = available
        self.fuzzy = fuzzy or {}
        self.requests = []

    def __call__(self, req, timeout):
        self.requests.append(req)
        if req.full_url == COLLECTION_URL:
            data = []
            for ident in json.loads(req.data)["identifiers"]:
                if "collector_number" in ident:
                    code, num = ident["set"], ident["collector_number"]
                    if self.available is None:
                        data.append(card("Card " + num, code, num))
                    else:
                        data.extend(c for c in self.available if c["set"] == code and c["collector_number"] == num)
                elif "name" in ident and self.available is not None:
                    data.extend(c for c in self.available if c["name"].casefold() == ident["name"].casefold())
            return Response({"object": "list", "data": data, "not_found": []})
        if req.full_url.startswith(NAMED_URL):
            from urllib.parse import parse_qs, urlsplit
            name = parse_qs(urlsplit(req.full_url).query)["fuzzy"][0]
            return Response(self.fuzzy.get(name, {"object": "error"}))
        raise AssertionError(req.full_url)


def client(fake):
    return ScryfallClient(opener=fake, sleep=lambda n: None, clock=lambda: 0.0)


class VoiceIntakeTests(unittest.TestCase):
    def test_dictation_and_print_notation(self):
        rows = parse("three copies of Sol Ring set symbol C M M number 396;"
                     "two Lightning Bolt (M11) 146 next card CMM 396")
        self.assertEqual([(e.quantity, e.name, e.set_code, e.collector_number) for e in rows],
                         [(3, "Sol Ring", "cmm", "396"), (2, "Lightning Bolt", "m11", "146"),
                          (1, "", "cmm", "396")])
        self.assertEqual(parse_line("one Atraxa, Praetors Voice set ONE number 196", 1).name,
                         "Atraxa, Praetors Voice")
        self.assertTrue(parse_line("Lightning Bolt number 146", 1).error)
        self.assertTrue(parse_line("Sol Ring set Commander Masters number 396", 1).error)

    def test_sixty_cards_one_request(self):
        fake = FakeTransport()
        report = resolve(parse("\n".join("CMM " + str(i) for i in range(1, 61))), client(fake))
        self.assertEqual((report["accepted"], report["requests"]), (60, 1))
        self.assertEqual(fake.requests[0].get_method(), "POST")
        self.assertEqual(len(json.loads(fake.requests[0].data)["identifiers"]), 60)
        self.assertIn("User-agent", fake.requests[0].headers)

    def test_chunking_and_dedupe(self):
        fake = FakeTransport()
        report = resolve(parse("\n".join("CMM " + str(i) for i in range(1, 87))), client(fake))
        self.assertEqual((report["accepted"], report["requests"]), (86, 2))
        self.assertEqual([len(json.loads(x.data)["identifiers"]) for x in fake.requests], [75, 11])
        fake2 = FakeTransport()
        report2 = resolve(parse("CMM 396; 2 CMM 396"), client(fake2))
        self.assertEqual(report2["accepted"], 2)
        self.assertEqual(len(json.loads(fake2.requests[0].data)["identifiers"]), 1)

    def test_name_conflict_and_fuzzy_never_auto_accept(self):
        fake = FakeTransport([card()])
        report = resolve(parse("Lightning Bolt set CMM number 396"), client(fake))
        self.assertEqual(report["review"], 1)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(csv_content(report))))), 0)
        fake2 = FakeTransport([], {"Sole Rung": card()})
        report2 = resolve(parse("Sole Rung"), client(fake2))
        self.assertEqual((report2["review"], report2["requests"]), (1, 2))
        self.assertEqual(len(list(csv.DictReader(io.StringIO(csv_content(report2))))), 0)

    def test_exact_name_and_fuzzy_budget(self):
        fake = FakeTransport([card()])
        report = resolve(parse("two copies of Sol Ring"), client(fake))
        row = list(csv.DictReader(io.StringIO(csv_content(report))))[0]
        self.assertEqual((row["Card Name"], row["Quantity"], row["Set Code"]),
                         ("Sol Ring", "2", "cmm"))
        fake2 = FakeTransport([])
        report2 = resolve(parse(";".join("Not A Card " + str(i) for i in range(60))),
                          client(fake2), fuzzy_budget=3)
        self.assertEqual((report2["unresolved"], report2["requests"]), (60, 4))

    def test_unknown_number_not_inventory(self):
        fake = FakeTransport([])
        report = resolve(parse("set CMM number 9999"), client(fake))
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(csv_content(report))))), 0)


if __name__ == "__main__":
    unittest.main()
