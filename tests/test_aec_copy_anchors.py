""".github/scripts/aec-copy-anchors.py: the isolated Telosmith check gets the anchored source bytes
(Codex review on #41), and nothing outside the trusted checkout."""
import importlib.util, json, os, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('aec_copy_anchors', ROOT / '.github/scripts/aec-copy-anchors.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def repo(td, anchors, files):
    root = Path(td) / 'repo'; (root / '.aec').mkdir(parents=True)
    lines = ['// comment line', json.dumps({'id': 'SRC-x', 'anchors': [{'path': a, 'sha256': '0'} for a in anchors]})]
    (root / '.aec/records.jsonl').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True); (root / rel).write_text(text, encoding='utf-8')
    return root


class CopyAnchors(unittest.TestCase):
    def test_every_anchor_in_the_real_records_is_copied(self):
        with tempfile.TemporaryDirectory() as td:
            copied = C.copy_anchors(ROOT, Path(td))
            self.assertEqual(copied, C.anchor_paths(ROOT / '.aec/records.jsonl'))
            self.assertTrue(copied)
            for rel in copied:
                self.assertEqual((Path(td) / rel).read_bytes(), (ROOT / rel).read_bytes())

    def test_parent_and_absolute_paths_are_refused(self):
        for bad in ('../outside.md', '/etc/passwd'):
            with tempfile.TemporaryDirectory() as td:
                root = repo(td, [bad], {})
                with self.assertRaises(SystemExit):
                    C.copy_anchors(root, Path(td) / 'out')

    def test_symlinked_anchor_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = repo(td, ['kb/link.md'], {'kb/real.md': 'x'})
            os.symlink(root / 'kb/real.md', root / 'kb/link.md')
            with self.assertRaises(SystemExit):
                C.copy_anchors(root, Path(td) / 'out')

    def test_workflow_runs_the_copier_before_the_container(self):
        wf = (ROOT / '.github/workflows/aec-upstream.yml').read_text()
        check = wf.split('  check:', 1)[1].split('  publish:', 1)[0]
        self.assertLess(check.index('aec-copy-anchors.py'), check.index('docker run'))


if __name__ == '__main__':
    unittest.main()
