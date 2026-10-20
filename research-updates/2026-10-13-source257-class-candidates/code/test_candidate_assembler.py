"""Fixture tests for pre-write immutable-input protection."""
import os
from pathlib import Path
import tempfile
import unittest

from assemble_candidate_inventory import OUTPUT_NAMES, assemble, guard_paths


class InputProtection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.base = self.root / 'base.json'
        self.raw = [self.root / ('raw-' + str(n) + '.json') for n in range(4)]
        self.decisions = self.root / 'decisions.json'
        self.inputs = [self.base, *self.raw, self.decisions]
        self.out = self.root / 'out'
        for n, path in enumerate(self.inputs):
            path.write_bytes(('immutable-' + str(n)).encode())
        self.snapshot = {p: p.read_bytes() for p in self.inputs}

    def tearDown(self):
        self.tmp.cleanup()

    def unchanged(self):
        self.assertTrue(all(p.read_bytes() == data for p, data in self.snapshot.items()))

    def test_normal_paths_do_not_create_output(self):
        self.assertEqual(len(guard_paths(self.base, self.raw, self.decisions, self.out)), 4)
        self.assertFalse(self.out.exists())
        self.unchanged()

    def test_all_output_names_reject_input_symlink_before_read_or_write(self):
        self.out.mkdir()
        for name in OUTPUT_NAMES:
            alias = self.out / name
            alias.symlink_to(self.decisions)
            with self.assertRaisesRegex(ValueError, 'output aliases'):
                assemble(self.base, self.raw, self.decisions, self.out)
            self.unchanged()
            self.assertEqual(len(list(self.out.iterdir())), 1)
            alias.unlink()

    def test_all_output_names_reject_input_hardlink_before_write(self):
        self.out.mkdir()
        for name in OUTPUT_NAMES:
            alias = self.out / name
            os.link(self.decisions, alias)
            with self.assertRaisesRegex(ValueError, 'output hardlink'):
                assemble(self.base, self.raw, self.decisions, self.out)
            self.unchanged()
            alias.unlink()

    def test_direct_output_path_collision_includes_evidence(self):
        path = self.root / 'adjudication-evidence-v1.json'
        path.write_bytes(b'private-decision-input')
        with self.assertRaisesRegex(ValueError, 'output aliases'):
            assemble(self.base, self.raw, path, self.root)
        self.assertEqual(path.read_bytes(), b'private-decision-input')
        self.unchanged()

    def test_duplicate_raw_path_and_basename_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate raw basename'):
            assemble(self.base, [self.raw[0]] * 4, self.decisions, self.out)
        other = self.root / 'other'
        other.mkdir()
        duplicate = other / self.raw[0].name
        duplicate.write_bytes(b'another-input')
        with self.assertRaisesRegex(ValueError, 'duplicate raw basename'):
            assemble(self.base, [self.raw[0], duplicate, *self.raw[2:]], self.decisions, self.out)
        self.assertFalse(self.out.exists())
        self.unchanged()

    def test_duplicate_hardlinked_inputs_and_outputs_rejected(self):
        self.raw[1].unlink()
        os.link(self.raw[0], self.raw[1])
        with self.assertRaisesRegex(ValueError, 'hardlinked input'):
            guard_paths(self.base, self.raw, self.decisions, self.out)
        self.raw[1].unlink()
        self.raw[1].write_bytes(self.snapshot[self.raw[1]])
        self.out.mkdir()
        a, b = [self.out / n for n in OUTPUT_NAMES[:2]]
        a.write_bytes(b'prior-output')
        os.link(a, b)
        with self.assertRaisesRegex(ValueError, 'hardlinked output'):
            assemble(self.base, self.raw, self.decisions, self.out)
        self.assertEqual(a.read_bytes(), b'prior-output')
        self.unchanged()


if __name__ == '__main__':
    unittest.main()
