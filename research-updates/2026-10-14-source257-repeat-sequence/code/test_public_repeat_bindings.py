"""Challenge fixed public identities without source images or private proofs.

In a published package, paths derive from its normal repository/data layout.
For local staged checks, explicitly set SOURCE257_PUBLIC_REPOSITORY and
SOURCE257_PUBLIC_DATA_DIR. All destructive fixtures use temporary copies.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import canonical_repeat_evidence as canonical
import public_repeat_bindings as public
import spatial_preparation as spatial


PACKAGE = Path(__file__).resolve().parents[1]
PUBLISHED_DATA = "research-updates/2026-10-14-source257-repeat-sequence/data"


class PublicBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repository = Path(os.environ.get("SOURCE257_PUBLIC_REPOSITORY", PACKAGE.parents[1])).resolve()
        data = Path(os.environ.get("SOURCE257_PUBLIC_DATA_DIR", PACKAGE / "data")).resolve()
        alias = {} if data.is_relative_to(repository) else {"published_data_relative": PUBLISHED_DATA}
        cls.actual_data, cls.actual_protected = public.load(repository, data, **alias)
        cls.base_blobs = {relative: (repository / relative).read_bytes() for relative, _ in public.PUBLIC_BASE.values()}
        cls.selected_blobs = {filename: (data / filename).read_bytes() for _, filename, _, _ in public.SEED_BINDINGS.values()}
        cls.selected_blobs[public.LEDGER_NAME] = (data / public.LEDGER_NAME).read_bytes()
        cls.seed_ledger = json.loads(cls.selected_blobs[public.LEDGER_NAME])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="public-repeat-bindings-")
        self.addCleanup(self.temp.cleanup)
        self.repository = Path(self.temp.name).resolve() / "repo"
        self.data = self.repository / PUBLISHED_DATA
        self.data.mkdir(parents=True)
        for relative, raw in self.base_blobs.items():
            path = self.repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        for name, raw in self.selected_blobs.items():
            (self.data / name).write_bytes(raw)

    def load(self, **kwargs):
        return public.load(self.repository, self.data, **kwargs)

    def row(self, ledger, name):
        logical = public.SEED_BINDINGS[name][0]
        return next(row for row in ledger["files"] if row["source_logical_id"] == logical)

    def test_actual_selected_load_and_fixed_original_identity(self):
        data, protected = self.load()
        self.assertEqual(len(data["metadata"]["annotations"]), 307)
        self.assertEqual(len(data["reader_A"]["pairs"]), 930)
        self.assertEqual(len(data["reader_B"]["observation_dictionary"]), 70)
        self.assertEqual(len(data["context_index"]["contexts"]), 152)
        self.assertEqual(data["reader_A"]["reader"], "Separate AI reader A")
        original, selected = public.SEED_BINDINGS["reader_A"][2:]
        self.assertNotEqual(original, selected)
        self.assertEqual(data["_hashes"]["reader_A"], original)
        self.assertEqual(protected["reader_A"][1], selected)
        self.assertEqual(data["closure_prelog"]["reader_initial_pins"]["A"], original)
        self.assertEqual(data["_public_bindings"]["inputs"]["reader_A"]["selected_whole_file_sha256"], selected)
        self.assertEqual(canonical.resolve(data, canonical.ref(data, "reader_A", "/schema")), data["reader_A"]["schema"])
        self.assertEqual(len(protected), 21)
        self.assertNotIn("final_core", data)
        self.assertNotIn("source_encoded", protected)

    def test_missing_source_and_proofs_never_accessed(self):
        self.assertFalse((self.repository / spatial.SOURCE[0]).exists())
        original_read = Path.read_bytes
        seen = []
        def guard(path):
            self.assertEqual(path.suffix, ".json")
            self.assertNotIn("proof", path.name.lower())
            seen.append(path.name)
            return original_read(path)
        with patch.object(Path, "read_bytes", guard):
            data, protected = self.load()
        self.assertEqual(len(data["profiles"]["profiles"]), 70)
        self.assertEqual(set(seen), {path.name for path, _ in protected.values()})

    def test_selected_semantic_edit_rejected_by_actual_byte_hash(self):
        path = self.data / public.SEED_BINDINGS["reader_A"][1]
        value = json.loads(path.read_bytes())
        value["reader"] = "Altered reader label"
        path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "selected byte hash mismatch: reader_A"):
            self.load()

    def test_existing_public_baseline_mutation_rejected(self):
        path = self.repository / public.PUBLIC_BASE["D9"][0]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "selected byte hash mismatch: D9"):
            self.load()

    def test_unknown_ledger_hash_rejected_even_for_json_equivalent_bytes(self):
        path = self.data / public.LEDGER_NAME
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Unknown seed selection ledger hash"):
            self.load()

    def test_ledger_cannot_rebind_origin_or_selected_hash_or_filename(self):
        for key, value in (("original_whole_file_sha256", "0" * 64),
                           ("selected_whole_file_sha256", "1" * 64),
                           ("selected_file", "another.json")):
            with self.subTest(key=key):
                ledger = copy.deepcopy(self.seed_ledger)
                self.row(ledger, "reader_A")[key] = value
                with self.assertRaisesRegex(ValueError, "Rebound original or selected"):
                    public.validate_ledger(ledger)

    def test_ledger_cannot_add_or_duplicate_original_binding(self):
        for kind in ("unlisted", "duplicate", "omitted"):
            with self.subTest(kind=kind):
                ledger = copy.deepcopy(self.seed_ledger)
                if kind == "unlisted":
                    ledger["files"][0]["source_logical_id"] = "D12_RESULTS:unlisted.json"
                elif kind == "duplicate":
                    ledger["files"][0] = copy.deepcopy(ledger["files"][1])
                else:
                    ledger["files"].pop()
                with self.assertRaises(ValueError):
                    public.validate_ledger(ledger)

    def test_unsafe_ledger_paths_rejected_before_binding(self):
        for value in ("/absolute.json", "../escape.json", "nested/../escape.json", "nested\\escape.json", "./file.json", "nested//file.json", "C:/escape.json"):
            with self.subTest(path=value):
                ledger = copy.deepcopy(self.seed_ledger)
                self.row(ledger, "reader_A")["selected_file"] = value
                with self.assertRaisesRegex(ValueError, "Unsafe public relative path"):
                    public.validate_ledger(ledger)

    def test_ledger_cannot_expand_or_change_privacy_filter(self):
        for name in ("reader_A", "closure_B", "reader_B"):
            with self.subTest(name=name):
                ledger = copy.deepcopy(self.seed_ledger)
                self.row(ledger, name)["exact_json_pointer_transformations"] = [{"json_pointer": "/pairs", "operation": "REMOVE_SCIENTIFIC_EVIDENCE"}]
                with self.assertRaisesRegex(ValueError, "Unknown privacy filter"):
                    public.validate_ledger(ledger)

    def test_selected_symlink_rejected(self):
        path = self.data / public.SEED_BINDINGS["reader_A"][1]
        target = self.repository / "outside.json"
        path.replace(target)
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.load()

    def test_changed_consumer_origin_cannot_be_silently_bound(self):
        with patch.dict(canonical.RAW_PINS, {"reader_A": ("repeat-reader-A-v1.json", "0" * 64)}):
            with self.assertRaisesRegex(ValueError, "Unbound consumer original"):
                self.load()

    def test_307_original_record_hash_and_unique_reference_guards(self):
        for kind in ("record_edit", "duplicate_reference"):
            with self.subTest(kind=kind):
                data = copy.deepcopy(self.actual_data)
                if kind == "record_edit":
                    data["D9"]["new_units"][0]["native_bbox_xyxy_halfopen"][0] += 1
                else:
                    data["metadata"]["annotations"][0] = copy.deepcopy(data["metadata"]["annotations"][1])
                with self.assertRaisesRegex(ValueError, "Immutable"):
                    public.validate_reference_universe(data)

    def test_protected_hash_is_selected_bytes_and_detects_postload_edit(self):
        _, protected = self.load()
        spatial.verify_unchanged(protected)
        path = protected["closure_B"][0]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Input changed"):
            spatial.verify_unchanged(protected)

    def test_actual_public_paths_and_declared_mismatch(self):
        data, _ = self.load()
        for name, relative in data["_paths"].items():
            public.safe_relative(relative)
            self.assertTrue((self.repository / relative).is_file())
            self.assertEqual(data["_public_bindings"]["inputs"][name]["path"], relative)
        with self.assertRaisesRegex(ValueError, "disagrees with actual"):
            self.load(published_data_relative="research-updates/wrong/data")

    def test_external_staging_requires_explicit_safe_public_destination(self):
        alternate_root = self.repository / "alternate"
        alternate_root.mkdir()
        for relative, raw in self.base_blobs.items():
            path = alternate_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "External staging requires"):
            public.load(alternate_root, self.data)
        with self.assertRaisesRegex(ValueError, "Unsafe public relative path"):
            public.load(alternate_root, self.data, published_data_relative="../escape")
        data, _ = public.load(alternate_root, self.data, published_data_relative=PUBLISHED_DATA)
        self.assertEqual(data["_paths"]["reader_A"], PUBLISHED_DATA + "/repeat-reader-A-v1.json")
        serialized = json.dumps(data["_public_bindings"])
        self.assertNotIn(str(self.repository), serialized)
        self.assertNotIn(str(self.data), serialized)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON object key"):
            public.json_object(b'{"key":1,"key":2}')


if __name__ == "__main__":
    unittest.main()
