"""KB rebuild reproducibility, split into content and bytes (challenge C-001).

kb/test_acceptance.py T7 asserts that rebuilding mtg_cards_v0.2.sqlite under another hash seed gives a
byte-identical file. On 2026-11-16 that held under SQLite 3.53.1 and failed under SQLite 3.45.1 with the
same code and inputs, while the SQL dumps of the two files were identical. So the rebuild's content is
deterministic; the file's bytes also depend on the SQLite library that writes it.

These tests check what holds everywhere (content identity) and say plainly when byte identity can't be
judged here. They live outside kb/ because kb/MANIFEST.sha256 pins kb/test_acceptance.py, so changing that
file would need a new KB release. In environments whose SQLite differs from the release's, run the KB suite
with KB_SKIP_REBUILD=1 and rely on these instead (CI does).

  python3 tools/kb_bootstrap.py install && python3 -m unittest tests.test_kb_rebuild_content -v   (~25 s)
"""
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / 'kb'
DB = KB / 'mtg_cards_v0.2.sqlite'
V01 = KB / 'mtg_cards.sqlite'


def sqlite_writer_version(path):
    """(major, minor, patch) of the SQLite library that last wrote the file (header offset 96, SQLITE_VERSION_NUMBER)."""
    with open(path, 'rb') as f:
        n = int.from_bytes(f.read(100)[96:100], 'big')
    return (n // 1000000, n // 1000 % 1000, n % 1000)


def content_sha256(path):
    """sha256 of the database's SQL dump: every schema statement and every row, in rowid order."""
    c = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    h = hashlib.sha256()
    try:
        for line in c.iterdump():
            h.update(line.encode())
            h.update(b'\n')
    finally:
        c.close()
    return h.hexdigest()


class HelperTests(unittest.TestCase):
    """No KB needed."""

    def test_writer_version_reads_the_header(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'x.sqlite'
            c = sqlite3.connect(p)
            c.execute('create table t(a)')
            c.commit()
            c.close()
            self.assertEqual(sqlite_writer_version(p), sqlite3.sqlite_version_info)

    def test_content_hash_ignores_layout_but_not_rows(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, c_ = (Path(d) / n for n in ('a.sqlite', 'b.sqlite', 'c.sqlite'))
            for p, page, rows in ((a, 4096, [(1,), (2,)]), (b, 1024, [(1,), (2,)]), (c_, 4096, [(1,), (3,)])):
                con = sqlite3.connect(p)
                con.execute(f'pragma page_size={page}')
                con.execute('create table t(a)')
                con.executemany('insert into t values (?)', rows)
                con.commit()
                con.execute('vacuum')
                con.close()
            self.assertNotEqual(a.read_bytes(), b.read_bytes())       # different layout
            self.assertEqual(content_sha256(a), content_sha256(b))    # same content
            self.assertNotEqual(content_sha256(a), content_sha256(c_))  # different rows


# Same skip reason as the other KB-backed tests: the shared kairos-checks suite allows only known reasons.
@unittest.skipUnless(DB.exists() and V01.exists(), 'KB database not installed (python3 tools/kb_bootstrap.py install)')
class RebuildReproducibility(unittest.TestCase):
    """Rebuild once under another hash seed, then compare with the shipped database."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name) / 'rebuilt.sqlite'
        c = sqlite3.connect(DB.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            built = dict(c.execute('select key,value from meta'))['v02_built_utc']
            source_modified = c.execute('select source_modified_utc from import_runs').fetchone()[0]
        finally:
            c.close()
        # Same command as kb/test_acceptance.py T7.
        subprocess.run([sys.executable, str(KB / 'migrate_v02.py'), '--v01', str(V01), '--out', str(cls.out),
                        '--overlay', str(KB / 'overrides' / 'review_overlay.jsonl'), '--refresh-dir', str(KB / 'refresh'),
                        '--source-modified', source_modified, '--built-utc', built],
                       check=True, env=dict(os.environ, PYTHONHASHSEED='12345'), capture_output=True, cwd=cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_rebuild_content_is_identical(self):
        self.assertEqual(content_sha256(self.out), content_sha256(DB))

    def test_rebuild_bytes_are_identical_under_the_release_sqlite(self):
        writer = sqlite_writer_version(DB)
        if writer != sqlite3.sqlite_version_info:
            self.skipTest(f'C-001: byte identity is judged only under the SQLite that wrote the release '
                          f'({".".join(map(str, writer))}); this is {sqlite3.sqlite_version}. Content identity is checked above.')
        self.assertEqual(hashlib.sha256(self.out.read_bytes()).hexdigest(), hashlib.sha256(DB.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
