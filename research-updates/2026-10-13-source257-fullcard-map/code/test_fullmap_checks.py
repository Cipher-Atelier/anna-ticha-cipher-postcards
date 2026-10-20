import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fullmap_checks import SOURCE_SHA, UNRESOLVED, WHOLE, validate


class FullmapChecksTests(unittest.TestCase):
    def setUp(self):
        self.frozen = {"units": [{"id": "f1", "native_bbox_xyxy_halfopen": [80, 810, 100, 850],
                                  "physical_extent_status": WHOLE,
                                  "single_cipher_unit_identity": "UNKNOWN", "repeated_class_validation": False}],
                       "source_quality": ["Synthetic fixture only"]}
        self.digest = hashlib.sha256(json.dumps(self.frozen).encode()).hexdigest()
        self.full = {"source": {"file_sha256": SOURCE_SHA, "size": [1785, 1175]},
                     "frozen_first_band": {"file_sha256": self.digest, "file_reference": "synthetic-frozen.json",
                                           "preserved_annotation_keys": ["source_quality"],
                                           "units": copy.deepcopy(self.frozen["units"])},
                     "new_units": [self.unit("n1"), self.unit("n2", UNRESOLVED)],
                     "frozen_overlay_conflicts": [],
                     "coverage_regions": [{"id": "bottom", "bbox": [65, 810, 1710, 1140],
                                           "state": "DECLARED_REVIEWED", "detail": "Synthetic only"}],
                     "source_quality": []}
        self.groups = {"groups": [{"id": "g1", "member_ids": ["f1", "n1"],
                                    "comparison_scope": "VISIBLE_BODY_GEOMETRY",
                                    "shared_features": ["a declared curve"], "visual_evidence_views": ["fixture.png"],
                                    "status": "CHECKED_VISUAL_SIMILARITY", "limits": ["No letter mapping"]}],
                       "deferred": [], "ungrouped_unit_ids": ["n2"]}

    @staticmethod
    def unit(ident, status=WHOLE):
        return {"id": ident, "native_bbox_xyxy_halfopen": [1340, 1000, 1400, 1100],
                "physical_extent_status": status, "cipher_role": "UNKNOWN", "geometric_features": "curve",
                "ambiguities": [], "evidence_views": ["fixture.png"], "region": "bottom", "order": 0,
                "overlap_with_frozen_ids": []}

    def check(self, groups=None):
        return validate(self.full, self.frozen, self.digest, groups)

    def test_unknown_role_whole_physical_unit_is_accepted(self):
        self.assertTrue(self.check(self.groups)["valid"])
        self.assertEqual(self.full["new_units"][0]["cipher_role"], "UNKNOWN")

    def test_frozen_changed_record_and_boolean_integer_substitution_rejected(self):
        for value in (True, 0):
            with self.subTest(value=value):
                self.full["frozen_first_band"]["units"][0]["repeated_class_validation"] = value
                self.assertFalse(self.check()["valid"])

    def test_digest_and_frozen_count_integrity(self):
        self.full["frozen_first_band"]["file_sha256"] = "wrong"
        self.assertFalse(self.check()["valid"])
        self.full["frozen_first_band"]["file_sha256"] = self.digest
        self.full["frozen_first_band"]["units"] = []
        self.assertFalse(self.check()["valid"])

    def test_bounds_rotation_error_and_boolean_are_diagnostics(self):
        for bounds in ([0, 0, 1175, 1785], [5, 2, 5, 8], [False, 0, 5, 8], [0, 1, "x", 9], None):
            with self.subTest(bounds=bounds):
                self.full["new_units"][0]["native_bbox_xyxy_halfopen"] = bounds
                self.assertFalse(self.check()["valid"])

    def test_ambiguous_unit_cannot_enter_group(self):
        self.groups["groups"][0]["member_ids"] = ["f1", "n2"]
        self.groups["ungrouped_unit_ids"] = ["n1"]
        self.assertFalse(self.check(self.groups)["valid"])

    def test_whole_new_unit_with_frozen_overlap_cannot_count_as_distinct_repeat(self):
        self.full["new_units"][0]["overlap_with_frozen_ids"] = ["f1"]
        result = self.check(self.groups)
        self.assertFalse(result["valid"])
        self.assertTrue(any("unresolved frozen-instance overlap" in item["message"] for item in result["errors"]))
        self.groups["groups"] = []
        self.groups["ungrouped_unit_ids"] = ["f1", "n1", "n2"]
        self.assertTrue(self.check(self.groups)["valid"])

    def test_missing_duplicate_or_unknown_class_membership_rejected(self):
        for members in (["f1"], ["f1", "f1"], ["f1", "missing"], ["f1", {}]):
            with self.subTest(members=members):
                self.groups["groups"][0]["member_ids"] = members
                self.assertFalse(self.check(self.groups)["valid"])

    def test_duplicate_flat_group_and_missing_ungrouped_rejected(self):
        self.groups["groups"].append(copy.deepcopy(self.groups["groups"][0]))
        self.groups["groups"][1]["id"] = "g2"
        self.assertFalse(self.check(self.groups)["valid"])
        self.groups["groups"].pop()
        self.groups["ungrouped_unit_ids"] = []
        self.assertFalse(self.check(self.groups)["valid"])

    def test_overlay_conflict_excludes_frozen_member(self):
        self.full["frozen_overlay_conflicts"] = [{"frozen_ids": ["f1"],
            "native_bbox_xyxy_halfopen": [80, 810, 100, 850], "detail": "Synthetic ownership conflict"}]
        self.assertFalse(self.check(self.groups)["valid"])

    def test_semantic_mapping_and_role_upgrade_rejected_without_modification(self):
        self.full["new_units"][0]["cipher_role"] = "LETTER"
        self.groups["groups"][0]["letter_mapping"] = "A"
        before = copy.deepcopy((self.full, self.groups))
        self.assertFalse(self.check(self.groups)["valid"])
        self.assertEqual((self.full, self.groups), before)

    def test_malformed_identifiers_order_and_source_size_return_errors(self):
        self.full["new_units"][0]["id"] = []
        self.full["new_units"][0]["order"] = True
        self.full["source"]["size"] = 42
        self.assertFalse(self.check()["valid"])

    def test_original_annotation_scope_reference_must_be_complete(self):
        self.full["frozen_first_band"]["preserved_annotation_keys"] = []
        self.assertFalse(self.check()["valid"])
        self.full["frozen_first_band"]["preserved_annotation_keys"] = ["source_quality"]
        self.full["frozen_first_band"]["file_reference"] = ""
        self.assertFalse(self.check()["valid"])

    def test_cli_uses_operator_file_digest_and_emits_diagnostics_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen = root / "frozen.json"
            full = root / "full.json"
            groups = root / "groups.json"
            output = root / "diagnostics.json"
            frozen.write_text(json.dumps(self.frozen))
            full.write_text(json.dumps(self.full))
            groups.write_text(json.dumps(self.groups))
            original = [p.read_bytes() for p in (frozen, full, groups)]
            command = [sys.executable, "-B", str(Path(__file__).with_name("fullmap_checks.py")),
                       str(full), str(frozen), "--groups", str(groups), str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(output.read_text())["valid"])
            self.assertEqual([p.read_bytes() for p in (frozen, full, groups)], original)
            self.full["new_units"][0]["native_bbox_xyxy_halfopen"] = [0, 0, 1175, 1785]
            full.write_text(json.dumps(self.full))
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertFalse(json.loads(output.read_text())["valid"])


if __name__ == "__main__":
    unittest.main()
