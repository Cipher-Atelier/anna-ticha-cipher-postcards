#!/usr/bin/env python3
"""Synthetic final reviews challenge acceptance gates; never source judgments."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import canonical_repeat_evidence as core
from check_canonical_repeat_evidence import check, check_sequence_tsv


def public_inputs():
    from public_repeat_bindings import load as load_public
    package = Path(__file__).resolve().parents[1]
    data, protected = load_public(package.parents[1], package / "data")
    for name, (filename, expected) in core.FINAL_REVIEW_PINS.items():
        core.attach_review(data, protected, name, package / "data" / filename, expected)
    return data, protected


def synthetic_reviews(data):
    scope, aa, bb, both, _ = core.raw_core(data)
    pins = {"protocol_sha256": data["_hashes"]["protocol"], "reader_A_sha256": data["_hashes"]["reader_A"], "reader_B_sha256": data["_hashes"]["reader_B"], "reader_B_confirmation_sha256": data["_hashes"]["confirmation_B"], "closure_prelog_sha256": data["_hashes"]["closure_prelog"]}
    def row(key):
        members = key.split("--")
        checks = {}
        for field in core.FIELDS:
            witnesses = [data["reader_B"]["observation_dictionary"][ident]["eight_feature_observations"][field] for ident in members]
            checks[field] = {"left_observation": witnesses[0]["observation"], "right_observation": witnesses[1]["observation"], "left_native_locator_bbox_xyxy_halfopen": witnesses[0]["native_locator_bbox_xyxy_halfopen"], "right_native_locator_bbox_xyxy_halfopen": witnesses[1]["native_locator_bbox_xyxy_halfopen"], "relation": "SUPPORTED_SAME_VISIBLE_RELATION", "source_view_refs": witnesses[0]["view_refs"] + witnesses[1]["view_refs"]}
        return {"pair_id": key, "member_ids": members, "decision": core.ACCEPT, "eight_feature_checks": checks, "variation_assessment": {"left_observed_variation": "SYNTHETIC left feature variation for fixture only.", "right_observed_variation": "SYNTHETIC right feature variation for fixture only.", "paired_assessment": "SYNTHETIC FIXTURE ONLY: copied field locators exercise structural gates, not a new source comparison.", "not_normalized_away": ["Synthetic terminal relation preserved"]}, "remaining_uncertainty": []}
    data["final_core"] = {"schema": "source257-repeat-final-ai-review-v1", "synthetic_fixture_only": True, "input_pins": pins, "core_pair_reviews": [row(key) for key in sorted(both)]}
    closure_pins = {**pins, "closure_A_sha256": data["_hashes"]["closure_A"], "closure_B_sha256": data["_hashes"]["closure_B"]}
    data["final_closure"] = {"schema": "source257-repeat-final-ai-closure-review-v1", "synthetic_fixture_only": True, "input_pins": closure_pins, "closure_pair_reviews": [row(r["pair_id"]) for r in data["closure_prelog"]["requests"]]}
    for name in ("final_core", "final_closure"):
        data["_hashes"][name] = core.spatial.record_sha(data[name])
        data["_paths"][name] = "SYNTHETIC_FIXTURE_ONLY_" + name + ".json"


class CanonicalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, _ = public_inputs()
        cls.fixture = copy.deepcopy(cls.raw)
        synthetic_reviews(cls.fixture)
        cls.output = core.build(cls.fixture)

    def setUp(self):
        self.data = copy.deepcopy(self.fixture)

    def rejected_input(self):
        with self.assertRaises((ValueError, KeyError)):
            core.build(self.data)

    def test_synthetic_complete_gates_pass(self):
        report = check(self.output, self.fixture)
        self.assertEqual(report["status"], "PASS_SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(report["accepted_different_graphics"], 0)
        self.assertEqual(report["spatial_annotation_refs"], 307)

    def test_no_default_image_io(self):
        original = Path.read_bytes
        def guarded(path):
            self.assertNotIn(path.suffix.lower(), {".jpg", ".jpeg", ".png"})
            return original(path)
        with patch.object(Path, "read_bytes", guarded):
            loaded, _ = public_inputs()
        self.assertEqual(len(loaded["reader_A"]["pairs"]), 930)

    def test_no_false_current_source_read_claim(self):
        altered = copy.deepcopy(self.output)
        altered["spatial"]["source_pixel_handling"] = "ENCODED_BYTES_HASHED_NO_PIXEL_DECODE_OR_VIEW"
        with self.assertRaises(ValueError):
            check(altered, self.fixture)

    def test_tsv_roundtrip(self):
        report = check_sequence_tsv(core.sequence_tsv(self.output), self.output)
        self.assertEqual(report["annotation_rows"], 307)

    def test_tsv_tampered_membership_row_rejected(self):
        text = core.sequence_tsv(self.output)
        old = next(r["id"] for region in self.output["spatial"]["regions"] for r in region["records"] if r["candidate_graph_membership_ids"])
        lines = text.splitlines(keepends=True)
        index = next(i for i, line in enumerate(lines) if "\t" + old + "\t" in line)
        cells = lines[index].rstrip("\n").split("\t")
        cells[6] = "[]"
        lines[index] = "\t".join(cells) + "\n"
        with self.assertRaises(ValueError):
            check_sequence_tsv("".join(lines), self.output)

    def test_missing_final_review_blocks_assembly(self):
        del self.data["final_core"]
        self.rejected_input()

    def test_matching_arbitrary_final_hash_not_frozen_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fake-final.json"
            path.write_text(json.dumps(self.data["final_core"]))
            own_hash = core.spatial.sha(path.read_bytes())
            with self.assertRaises(ValueError):
                core.attach_review(self.data, {}, "final_core", path, own_hash)

    def test_synthetic_production_write_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "production.json"
            with self.assertRaises(ValueError):
                core.write_canonical_once(path, self.output, {})
            self.assertFalse(path.exists())

    def test_missing_930_pair_rejected(self):
        self.data["reader_A"]["pairs"].pop()
        self.rejected_input()

    def test_duplicate_930_pair_rejected(self):
        self.data["reader_B"]["pairs"][-1] = copy.deepcopy(self.data["reader_B"]["pairs"][0])
        self.rejected_input()

    def test_reversed_pair_rejected(self):
        self.data["reader_A"]["pairs"][0]["member_ids"].reverse()
        self.rejected_input()

    def test_missing_B_actual_confirmation_rejected(self):
        self.data["confirmation_B"]["confirmations"].pop()
        self.rejected_input()

    def test_false_B_source_panel_rejected(self):
        self.data["confirmation_B"]["confirmations"][0]["actual_direct_pair_view"]["panels"][0]["source_panel_equal"] = False
        self.rejected_input()

    def test_B_recheck_unknown_field_rejected(self):
        self.data["confirmation_B"]["confirmations"][0]["eight_feature_recheck"]["openings"]["relation"] = "UNKNOWN"
        self.rejected_input()

    def test_A_paired_text_cannot_be_rebound(self):
        key = self.data["final_core"]["core_pair_reviews"][0]["pair_id"]
        row = next(r for r in self.data["reader_A"]["pairs"] if r["pair_id"] == key)
        row["evidence"]["eight_feature_comparisons"]["openings"]["left_source_observation"] = "Generic common body"
        self.rejected_input()

    def test_prescreen_cannot_support_positive(self):
        key = self.data["final_core"]["core_pair_reviews"][0]["pair_id"]
        row = next(r for r in self.data["reader_A"]["pairs"] if r["pair_id"] == key)
        row["source_coverage"] = "METADATA_PRESCREEN_WITH_SEPARATE_UNIT_SOURCE_OBSERVATIONS"
        self.rejected_input()

    def test_final_review_missing_pair_rejected(self):
        self.data["final_core"]["core_pair_reviews"].pop()
        self.rejected_input()

    def test_final_wrong_input_pin_rejected(self):
        self.data["final_core"]["input_pins"]["reader_B_sha256"] = "0" * 64
        self.rejected_input()

    def test_final_missing_eighth_feature_rejected(self):
        del self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["owned_mark_profile"]
        self.rejected_input()

    def test_final_unknown_relation_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["owned_mark_profile"]["relation"] = "UNKNOWN"
        self.rejected_input()

    def test_final_unknown_observation_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["owned_mark_profile"]["left_observation"] = "UNKNOWN"
        self.rejected_input()

    def test_final_invalid_locator_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]["left_native_locator_bbox_xyxy_halfopen"] = [-1, 0, 3, 3]
        self.rejected_input()

    def test_final_unrelated_valid_image_locator_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]["left_native_locator_bbox_xyxy_halfopen"] = [0, 0, 4, 4]
        self.rejected_input()

    def test_final_missing_source_views_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]["source_view_refs"] = []
        self.rejected_input()

    def test_final_unknown_context_reference_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]["source_view_refs"] = ["context-999999"]
        self.rejected_input()

    def test_final_known_wrong_target_context_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]["source_view_refs"] = ["context-013", "context-014"]
        self.rejected_input()

    def test_final_context_dictionary_wrong_coordinates_rejected(self):
        witness = self.data["final_core"]["core_pair_reviews"][0]["eight_feature_checks"]["terminal_pattern"]
        witness["source_view_refs"][0] = {"context_id": witness["source_view_refs"][0], "native_bbox_xyxy_halfopen": [0, 0, 10, 10]}
        self.rejected_input()

    def test_final_neighbor_locator_within_context_rejected(self):
        review = self.data["final_core"]["core_pair_reviews"][0]
        ident = review["member_ids"][0]
        context = core.context_views(self.data, ident)["CONTEXT"]["native_crop_bbox"]
        review["eight_feature_checks"]["terminal_pattern"]["left_native_locator_bbox_xyxy_halfopen"] = [context[0], context[1], context[0] + 2, context[1] + 2]
        self.rejected_input()

    def test_final_accept_with_uncertainty_rejected(self):
        self.data["final_core"]["core_pair_reviews"][0]["remaining_uncertainty"] = ["SYNTHETIC unresolved terminal relation"]
        self.rejected_input()

    def test_final_defer_preserves_both_reader_positives(self):
        review = self.data["final_core"]["core_pair_reviews"][0]
        key = review["pair_id"]
        review["decision"] = core.DEFER
        review["remaining_uncertainty"] = ["SYNTHETIC unresolved terminal relation"]
        review["eight_feature_checks"]["terminal_pattern"]["relation"] = "UNRESOLVED"
        out = core.build(self.data)
        row = next(r for r in out["core_pairs"] if r["pair_id"] == key)
        self.assertEqual(row["status"], "DEFERRED")
        self.assertEqual(row["deferred_reason"], "FINAL_AI_FEATURE_OR_BINDING_DEFERRED")
        self.assertEqual(row["reader_A"]["status"], core.SAME)
        self.assertEqual(row["reader_B"]["status"], core.SAME)
        self.assertNotIn(key, {e["pair_id"] for e in out["graph"]["positive_edges"]})

    def test_derived_single_reader_negative_never_accepted(self):
        rows = [r for r in self.output["core_pairs"] if r["reader_B"]["coverage"] == "DERIVED_UNIT_SOURCE_FEATURE_CONTRAST" and r["reader_B"]["status"] == "DIFFERENT_GRAPHICS"]
        self.assertEqual(len(rows), 772)
        self.assertTrue(all(r["status"] == "DEFERRED" for r in rows))

    def test_raw_positive_conflicts_preserved_deferred(self):
        rows = [r for r in self.output["core_pairs"] if r["deferred_reason"] == "READER_CANDIDATE_CONFLICT"]
        self.assertEqual(len(rows), 37)
        self.assertTrue(all(r["status"] == "DEFERRED" for r in rows))

    def test_prelog_wrong_pin_rejected(self):
        self.data["closure_A"]["prelog_sha256"] = "0" * 64
        self.rejected_input()

    def test_prelog_future_to_A_result_freeze_rejected(self):
        self.data["closure_prelog"]["frozen_utc"] = "2030-01-01T00:00:00+00:00"
        self.rejected_input()

    def test_B_before_view_attestation_not_timestamp_proof(self):
        self.assertEqual(self.output["chronology"]["B_before_view_basis"], "PRELOG_BOUND_BEFORE_VIEW_ATTESTATION_NOT_INTRINSIC_TIMESTAMP_PROOF")

    def test_closure_13th_pair_rejected(self):
        self.data["closure_A"]["pairs"].append(copy.deepcopy(self.data["closure_A"]["pairs"][0]))
        self.rejected_input()

    def test_closure_missing_B_pair_rejected(self):
        self.data["closure_B"]["results"].pop()
        self.rejected_input()

    def test_closure_missing_trigger_witness_rejected(self):
        self.data["closure_prelog"]["requests"][0]["triggers"][0]["existing_core_candidate_witnesses"] = ["FC002--FC015"]
        self.rejected_input()

    def test_closure_final_defer_removes_edge(self):
        row = self.data["final_closure"]["closure_pair_reviews"][0]
        key = row["pair_id"]
        row["decision"] = core.DEFER
        row["remaining_uncertainty"] = ["SYNTHETIC closure defer"]
        result = core.build(self.data)
        self.assertNotIn(key, {e["pair_id"] for e in result["graph"]["positive_edges"]})

    def test_checker_rejects_fake_accepted_negative(self):
        altered = copy.deepcopy(self.output)
        row = next(r for r in altered["core_pairs"] if r["reader_B"]["status"] == "DIFFERENT_GRAPHICS")
        row["status"] = "ACCEPTED_DIFFERENT_GRAPHICS"
        with self.assertRaises(ValueError):
            check(altered, self.fixture)

    def test_checker_rejects_unsupported_graph_edge(self):
        altered = copy.deepcopy(self.output)
        altered["graph"]["positive_edges"].append({"pair_id": "FC002--FC015"})
        with self.assertRaises(ValueError):
            check(altered, self.fixture)

    def test_checker_rejects_nonclique_group(self):
        altered = copy.deepcopy(self.output)
        altered["graph"]["maximal_cliques"][0]["member_ids"].append("FC002")
        with self.assertRaises(ValueError):
            check(altered, self.fixture)

    def test_checker_rejects_unknown_length_coarsening(self):
        altered = copy.deepcopy(self.output)
        altered["spatial"]["regions"][0]["records"][0]["sequence_length"] = 1
        with self.assertRaises(ValueError):
            check(altered, self.fixture)


if __name__ == "__main__":
    unittest.main()
