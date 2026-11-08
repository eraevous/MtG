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



class IntakeSafetyTests(unittest.TestCase):
    @staticmethod
    def batch(cards):
        # A synthetic response, independent of endpoint identifier behavior.
        class BatchTransport(FakeTransport):
            def __call__(self, req, timeout):
                if req.full_url == COLLECTION_URL:
                    self.requests.append(req)
                    return Response({"data": cards})
                return super().__call__(req, timeout)
        return BatchTransport([])

    def test_set_without_number_never_accepts_other_set(self):
        fake = self.batch([card(set_code="c21", n="263")])
        report = resolve(parse("Sol Ring set CMM"), client(fake))
        self.assertEqual(json.loads(fake.requests[0].data)["identifiers"],
                         [{"name": "Sol Ring", "set": "cmm"}])
        self.assertEqual(report["cards"][0]["status"], "review")
        self.assertIn("set differs", report["cards"][0]["reason"])
        self.assertEqual(len(list(csv.DictReader(io.StringIO(csv_content(report))))), 0)

    def test_set_without_number_prefers_requested_set(self):
        fake = self.batch([card(set_code="c21", n="263"), card()])
        report = resolve(parse("Sol Ring set CMM; Sol Ring set C21 number 263"), client(fake))
        self.assertEqual(report["accepted"], 2)
        self.assertEqual([r["set_code"] for r in report["cards"]], ["cmm", "c21"])

    def test_number_word_names_resolve_without_inflating_quantity(self):
        names = ["Seven Dwarves", "One with Nothing", "Two-Headed Giant"]
        fake = FakeTransport([card(n, n=str(i)) for i, n in enumerate(names)])
        report = resolve(parse(";".join(names)), client(fake))
        self.assertEqual(report["accepted"], 3)
        self.assertEqual(report["requests"], 1)
        self.assertEqual([r["quantity"] for r in report["cards"]], [1, 1, 1])
        self.assertEqual([r["requested_name"] for r in report["cards"]], names)

    def test_explicit_quantity_and_printing_stay_supported(self):
        fake = FakeTransport([card("Seven Dwarves")])
        report = resolve(parse("two copies of Seven Dwarves; Seven Dwarves set CMM number 396"), client(fake))
        self.assertEqual(report["accepted"], 2)
        self.assertEqual([r["quantity"] for r in report["cards"]], [2, 1])

    def test_both_number_word_interpretations_require_review(self):
        fake = FakeTransport([card("Seven Dwarves"), card("Dwarves", n="2")])
        report = resolve(parse("Seven Dwarves"), client(fake))
        self.assertEqual(report["review"], 1)
        row = report["cards"][0]
        self.assertEqual((row["quantity"], row["alternate_quantity"]), (1, 7))
        self.assertIn("quantity", row["reason"])
        self.assertEqual(len(list(csv.DictReader(io.StringIO(csv_content(report))))), 0)

    def test_quantity_ambiguity_survives_multiple_printings(self):
        for duplicate_name in ("Dwarves", "Seven Dwarves"):
            with self.subTest(duplicate_name=duplicate_name):
                fake = self.batch([card("Seven Dwarves"), card("Dwarves", n="2"),
                                   card(duplicate_name, n="3")])
                report = resolve(parse("Seven Dwarves"), client(fake), 0)
                self.assertEqual(report["review"], 1)
                self.assertEqual(report["accepted"], 0)

    def test_uncertain_number_word_fuzzy_does_not_inflate_quantity(self):
        fake = FakeTransport([], {"Seven Dwarves": card("Seven Dwarves")})
        report = resolve(parse("Seven Dwarves"), client(fake))
        self.assertEqual(report["review"], 1)
        self.assertEqual(report["cards"][0]["quantity"], 1)
        self.assertEqual(report["cards"][0]["alternate_quantity"], 7)

    def test_word_quantity_before_nameless_printing(self):
        report = resolve(parse("two CMM 396; two set CMM number 396"), client(FakeTransport()))
        self.assertEqual(report["accepted"], 2)
        self.assertEqual([r["quantity"] for r in report["cards"]], [2, 2])

    def test_number_word_prefix_is_not_part_of_longer_word(self):
        entry = parse("Oneirophage")[0]
        self.assertEqual((entry.name, entry.quantity), ("Oneirophage", 1))

    def test_multiple_printings_never_choose_arbitrarily(self):
        for cards in [[card(), card(set_code="c21", n="263")],
                      [card(), card(n="999")]]:
            with self.subTest(cards=cards):
                report = resolve(parse("Sol Ring"), client(self.batch(cards)), 0)
                self.assertEqual(report["accepted"], 0)

    def test_same_front_alias_different_cards_is_ambiguous(self):
        cards = [card("Front // Back One"), card("Front // Back Two", n="2")]
        for c in cards:
            c["card_faces"] = [{"name": n} for n in c["name"].split(" // ")]
        report = resolve(parse("Front"), client(self.batch(cards + cards[:1])), 0)
        self.assertEqual(report["accepted"], 0)

    def test_429_aborts_fuzzy_and_batch_paths(self):
        import urllib.error
        from collection.voice_intake import RateLimitError
        for rate_on_post, expected_calls in [(False, 2), (True, 1)]:
            with self.subTest(rate_on_post=rate_on_post):
                calls = []
                def opener(req, timeout):
                    calls.append(req)
                    if rate_on_post or req.get_method() == "GET":
                        raise urllib.error.HTTPError(req.full_url, 429, "limited", {}, None)
                    return Response({"data": []})
                c = client(opener)
                with self.assertRaises(RateLimitError):
                    resolve(parse(";".join("Unknown Card " + str(i) for i in range(10))), c)
                self.assertEqual(len(calls), expected_calls)

    def test_429_cli_exits_fatal_without_writing_artifacts(self):
        import tempfile
        import urllib.error
        from contextlib import redirect_stderr
        from unittest.mock import patch
        from collection import voice_intake
        def opener(req, timeout):
            if req.get_method() == "GET":
                raise urllib.error.HTTPError(req.full_url, 429, "limited", {}, None)
            return Response({"data": []})
        c = client(opener)
        with tempfile.TemporaryDirectory() as tmp:
            csv_path, review_path = Path(tmp) / "out.csv", Path(tmp) / "review.json"
            with patch.object(voice_intake, "ScryfallClient", return_value=c), \
                 patch("sys.stdin", io.StringIO("Unknown Card")), redirect_stderr(io.StringIO()):
                exit_code = voice_intake.main(["-", "--csv", str(csv_path), "--review", str(review_path)])
            self.assertEqual(exit_code, 2)
            self.assertFalse(csv_path.exists())
            self.assertFalse(review_path.exists())

    def test_back_face_cannot_be_exact_acceptance(self):
        delver = card("Delver of Secrets // Insectile Aberration")
        delver["card_faces"] = [{"name": "Delver of Secrets"}, {"name": "Insectile Aberration"}]
        report = resolve(parse("Insectile Aberration; Delver of Secrets"), client(self.batch([delver])), 0)
        self.assertEqual([r["status"] for r in report["cards"]], ["unresolved", "accepted"])
        report = resolve(parse("Insectile Aberration set CMM number 396"), client(self.batch([delver])), 0)
        self.assertEqual(report["review"], 1)

    def test_exact_full_name_wins_over_other_cards_back_face(self):
        rampant = card("Rampant Growth")
        student = card("Studious First-Year // Rampant Growth", n="2")
        student["card_faces"] = [{"name": "Studious First-Year"}, {"name": "Rampant Growth"}]
        report = resolve(parse("Rampant Growth; Studious First-Year"),
                         client(self.batch([rampant, student])), 0)
        self.assertEqual(report["accepted"], 2)
        self.assertEqual([r["name"] for r in report["cards"]], [rampant["name"], student["name"]])

if __name__ == "__main__":
    unittest.main()
