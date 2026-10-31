"""Tests for tools/drift_check.py. Each seeded violation must be caught, and the real repo must have no errors.

  python3 -m unittest discover -s tests
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import drift_check as D  # noqa: E402

PURPOSE = """# Module: m
@ai-path: m
@ai-source-file: {src}
@ai-dependencies: {deps}
"""


class Sandbox(unittest.TestCase):
    """A minimal repo with one frozen file, one purpose file and one append-only ledger."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "tools").mkdir()
        (self.root / "pkg").mkdir()
        (self.root / "codex_++/purpose_files").mkdir(parents=True)
        (self.root / "frozen.json").write_text('{"p": 1}\n')
        (self.root / "pkg/helper.py").write_text("X = 1\n")
        (self.root / "pkg/main.py").write_text("import helper\n")
        (self.root / "ledger.jsonl").write_text('{"id": 1}\n')
        self.write_purpose("pkg/main.py", "helper")
        self.rules = {
            "frozen": {"frozen.json": D.sha256(self.root / "frozen.json")},
            "purpose_dir": "codex_++/purpose_files",
            "semantic_owners": ["grammar/", "kb/"],
            "scan_exclude": ["tools/"],
            "append_only": ["ledger.jsonl"],
        }
        (self.root / "tools/drift_rules.json").write_text(json.dumps(self.rules))

    def tearDown(self):
        shutil.rmtree(self.root)

    def write_purpose(self, src, deps):
        (self.root / "codex_++/purpose_files/m.purpose.md").write_text(PURPOSE.format(src=src, deps=deps))

    def checks(self, report, level):
        return {(i["check"], i["path"]) for i in report.items if i["level"] == level}


class TestDriftCheck(Sandbox):
    def test_clean_sandbox(self):
        self.assertEqual(D.run(self.root).items, [])

    def test_frozen_edit_is_an_error(self):
        (self.root / "frozen.json").write_text('{"p": 2}\n')
        self.assertIn(("frozen", "frozen.json"), self.checks(D.run(self.root), "error"))

    def test_frozen_delete_is_an_error(self):
        (self.root / "frozen.json").unlink()
        self.assertIn(("frozen", "frozen.json"), self.checks(D.run(self.root), "error"))

    def test_missing_source_file_is_an_error(self):
        self.write_purpose("pkg/gone.py", "none")
        self.assertTrue(any(i["check"] == "purpose" for i in D.run(self.root).errors))

    def test_undeclared_local_import_warns(self):
        self.write_purpose("pkg/main.py", "none")
        self.assertTrue(any("does not declare" in i["msg"] for i in D.run(self.root).warnings))

    def test_stale_declared_dependency_warns(self):
        self.write_purpose("pkg/main.py", "helper, ghost")
        self.assertTrue(any("'ghost'" in i["msg"] for i in D.run(self.root).warnings))

    def test_external_dependencies_are_ignored(self):
        self.write_purpose("pkg/main.py", "helper, ext:openpyxl")
        self.assertEqual(D.run(self.root).items, [])

    def test_undeclared_semantic_authority_warns(self):
        (self.root / "evaluator").mkdir()
        (self.root / "evaluator/shortcut.py").write_text(
            "import sqlite3, re\nrows = db.execute('select oracle_text from cards')\n")
        self.assertIn(("semantic", "evaluator/shortcut.py"), self.checks(D.run(self.root), "warning"))

    def test_declared_semantic_role_is_accepted(self):
        (self.root / "evaluator").mkdir()
        (self.root / "evaluator/verify.py").write_text(
            "# @ai-semantic-role: verifier\nimport re\nq = 'select oracle_text from cards'\n")
        self.assertEqual(D.run(self.root).items, [])

    def test_semantic_owners_may_parse(self):
        (self.root / "grammar").mkdir()
        (self.root / "grammar/parse.py").write_text("import re\nq = 'oracle_text'\n")
        self.assertEqual(D.run(self.root).items, [])

    def test_strict_mode_fails_on_warnings(self):
        self.write_purpose("pkg/main.py", "none")
        self.assertEqual(D.main(["--root", str(self.root)]), 0)
        self.assertEqual(D.main(["--root", str(self.root), "--strict"]), 1)


class TestAppendOnly(Sandbox):
    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")

    def test_append_is_fine(self):
        with open(self.root / "ledger.jsonl", "a") as f:
            f.write('{"id": 2}\n')
        self.assertEqual(D.run(self.root, base="HEAD").errors, [])

    def test_rewrite_is_an_error(self):
        (self.root / "ledger.jsonl").write_text('{"id": 1, "edited": true}\n')
        self.assertIn(("append-only", "ledger.jsonl"), self.checks(D.run(self.root, base="HEAD"), "error"))

    def test_delete_is_an_error(self):
        (self.root / "ledger.jsonl").unlink()
        self.assertIn(("append-only", "ledger.jsonl"), self.checks(D.run(self.root, base="HEAD"), "error"))


class TestGovernedAndMirror(Sandbox):
    """P-09 (proposed): a DIO source pinned in .aec/records.jsonl; decision records mirror the decision log."""

    def setUp(self):
        super().setUp()
        (self.root / "ont").mkdir()
        (self.root / "ont/dio.md").write_text("# DIO\nGate rule.\n")
        (self.root / "ont/notes.md").write_text("ungoverned notes\n")
        (self.root / ".aec").mkdir()
        (self.root / "decisions.jsonl").write_text(
            '{"id": "D-1", "status": "proposed"}\n{"id": "D-1", "status": "accepted"}\n')
        self.records = [
            {"id": "SRC-dio", "version": 1, "type": "source", "subject": "formal-representation",
             "anchors": [{"path": "ont/dio.md", "sha256": D.sha256(self.root / "ont/dio.md"), "locator": "L1-2"}]},
            {"id": "SRC-notes", "version": 1, "type": "source", "subject": "notes",
             "anchors": [{"path": "ont/notes.md", "sha256": D.sha256(self.root / "ont/notes.md"), "locator": "L1"}]},
            {"id": "D-1", "version": 1, "type": "decision", "status": "proposed"},
            {"id": "D-1", "version": 2, "type": "decision", "status": "accepted"},
        ]
        self.write_records()
        self.rules.update({"aec_records": ".aec/records.jsonl", "governed_subjects": ["formal-representation"],
                           "decision_log": "decisions.jsonl"})
        (self.root / "tools/drift_rules.json").write_text(json.dumps(self.rules))

    def write_records(self):
        lines = ["// comment lines are skipped"] + [json.dumps(r) for r in self.records]
        (self.root / ".aec/records.jsonl").write_text("\n".join(lines) + "\n")

    def test_clean(self):
        self.assertEqual(D.run(self.root).items, [])

    def test_edited_dio_is_an_error(self):
        (self.root / "ont/dio.md").write_text("# DIO\nGate rule, renumbered.\n")
        self.assertIn(("governed", "ont/dio.md"), self.checks(D.run(self.root), "error"))

    def test_deleted_dio_is_an_error(self):
        (self.root / "ont/dio.md").unlink()
        self.assertIn(("governed", "ont/dio.md"), self.checks(D.run(self.root), "error"))

    def test_ungoverned_source_change_is_not_flagged(self):
        (self.root / "ont/notes.md").write_text("edited notes\n")
        self.assertEqual(D.run(self.root).items, [])

    def test_new_source_version_repins(self):
        (self.root / "ont/dio.md").write_text("# DIO 3.1.2\n")
        self.records.append({"id": "SRC-dio", "version": 2, "type": "source", "subject": "formal-representation",
                             "anchors": [{"path": "ont/dio.md", "sha256": D.sha256(self.root / "ont/dio.md"),
                                          "locator": "L1"}]})
        self.write_records()
        self.assertEqual(D.run(self.root).items, [])

    def test_mirror_status_disagreement_is_an_error(self):
        self.records.append({"id": "D-1", "version": 3, "type": "decision", "status": "rejected"})
        self.write_records()
        self.assertIn(("mirror", ".aec/records.jsonl"), self.checks(D.run(self.root), "error"))

    def test_mirror_unknown_decision_is_an_error(self):
        self.records.append({"id": "D-9", "version": 1, "type": "decision", "status": "proposed"})
        self.write_records()
        self.assertIn(("mirror", ".aec/records.jsonl"), self.checks(D.run(self.root), "error"))

    def test_no_records_file_means_not_adopted(self):
        (self.root / ".aec/records.jsonl").unlink()
        self.assertEqual(D.run(self.root).items, [])


class TestRealRepo(unittest.TestCase):
    def test_repo_has_no_drift_errors(self):
        report = D.run(ROOT)
        self.assertEqual(report.errors, [], D.render(report))


if __name__ == "__main__":
    unittest.main()
