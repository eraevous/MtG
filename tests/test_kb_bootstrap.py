"""tools/kb_bootstrap.py on a throwaway repo layout: status levels, and install refusing anything that does not match
the release manifest. Runs everywhere; no real database needed."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import kb_bootstrap as kbb  # noqa: E402

DBS = {'mtg_cards_v0.2.sqlite': b'v02 database bytes', 'mtg_cards.sqlite': b'v01 database bytes'}


class Bootstrap(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / 'kb').mkdir()
        (self.root / 'tools').mkdir()
        (self.root / 'kb' / 'MANIFEST.sha256').write_text(
            ''.join(f'{hashlib.sha256(b).hexdigest()}  {n}\n' for n, b in DBS.items()), encoding='utf-8')
        (self.root / 'tools' / 'kb_release.json').write_text(json.dumps({
            'release': 'test-release', 'zip_name': 'rel.zip', 'zip_sha256': 'unused', 'url': 'http://invalid/',
            'databases': list(DBS), 'search_dirs': ['data']}), encoding='utf-8')
        for d in kbb.DOCTRINE:
            (self.root / d).parent.mkdir(parents=True, exist_ok=True)
            (self.root / d).write_text('doc', encoding='utf-8')

    def make_zip(self, name='other.zip', **override):
        z = self.root / name
        with zipfile.ZipFile(z, 'w') as f:
            for n, b in {**DBS, **override}.items():
                f.writestr(f'release_dir/{n}', b)
        return z

    def test_without_databases_grounding_is_doctrine_only(self):
        st = kbb.status(self.root)
        self.assertEqual(st['grounding'], 'doctrine_only')
        self.assertTrue(all(st['doctrine'].values()))
        self.assertTrue(any('kb_bootstrap.py install' in n for n in st['next_steps']))

    def test_install_verifies_then_grounds(self):
        done = kbb.install(self.make_zip(), self.root)
        self.assertEqual(len(done), 2)
        self.assertEqual(kbb.status(self.root)['grounding'], 'kb_grounded')
        again = kbb.install(self.make_zip(), self.root)
        self.assertTrue(all('already' in d for d in again))

    def test_install_refuses_a_database_that_does_not_match_the_manifest(self):
        with self.assertRaises(ValueError):
            kbb.install(self.make_zip(**{'mtg_cards_v0.2.sqlite': b'tampered'}), self.root)
        self.assertFalse((self.root / 'kb' / 'mtg_cards_v0.2.sqlite').exists())

    def test_pinned_zip_name_with_wrong_hash_is_refused(self):
        with self.assertRaises(ValueError):
            kbb.install(self.make_zip('rel.zip'), self.root)

    def test_a_different_database_is_unpinned_not_grounded(self):
        (self.root / 'kb' / 'mtg_cards_v0.2.sqlite').write_bytes(b'someone else\'s build')
        self.assertEqual(kbb.status(self.root)['grounding'], 'kb_unpinned')

    def test_the_repo_pin_names_the_release_the_kb_manifest_describes(self):
        pin = json.loads((ROOT / 'tools' / 'kb_release.json').read_text(encoding='utf-8'))
        manifest = json.loads((ROOT / 'kb' / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(pin['release'], manifest['release'])
        self.assertEqual(set(kbb.manifest_hashes(ROOT, pin['databases'])), set(pin['databases']))


if __name__ == '__main__':
    unittest.main()
