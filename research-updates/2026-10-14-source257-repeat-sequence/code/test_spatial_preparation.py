#!/usr/bin/env python3
"""Scope, geometry, graph, unknown-length and immutable-write challenge fixtures."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import spatial_preparation as core
from check_spatial_preparation import check


class SpatialPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from public_repeat_bindings import load as load_public
        package = Path(__file__).resolve().parents[1]
        cls.inputs, cls.pins = load_public(package.parents[1], package / "data")
        cls.prepared = core.assemble(cls.inputs)

    def setUp(self):
        self.output = copy.deepcopy(self.prepared)

    def records(self):
        return [r for region in self.output["regions"] for r in region["records"]]

    def rejected(self):
        with self.assertRaises(ValueError):
            check(self.output, self.inputs)

    @staticmethod
    def graph_fixture():
        ref = {"path": "SYNTHETIC_FIXTURE_ONLY.json", "sha256": "0" * 64, "json_pointer": "/paired_witness"}
        return {"schema": "source257-positive-edge-graph-input-v1", "purpose": "PREPARATION_ONLY", "new_positive_edges": [
            {"member_ids": ["FC015", "FC066"], "origin": "CORE_930", "evidence_reference": ref},
            {"member_ids": ["FC015", "FC074"], "origin": "CORE_930", "evidence_reference": ref}]}

    def test_valid_inherited_only_preparation(self):
        report = check(self.output, self.inputs)
        self.assertEqual(report["annotation_refs"], 307)
        self.assertEqual(report["structural_new_edges"], 0)

    def test_missing307_record_rejected(self):
        self.output["regions"][0]["records"].pop()
        self.rejected()

    def test_wrong70_graph_scope_rejected(self):
        self.output["graph"]["node_ids"].pop()
        self.rejected()

    def test_assembler_rejects_swapped_eligible_with_same_count(self):
        altered = copy.deepcopy(self.inputs)
        altered["profiles"]["profiles"][0]["id"] = "FC001"
        with self.assertRaises(ValueError):
            core.assemble(altered)

    def test_wrong70_label_scope_rejected(self):
        r = next(r for r in self.records() if r["full_feature_label_status"] == "UNKNOWN_FULL_FEATURE_LABEL")
        r["full_feature_label_status"] = "ELIGIBLE_PROFILE_REFERENCE"
        self.rejected()

    def test_legacy_label_leak_rejected(self):
        self.records()[0]["historical_label"] = "S001"
        self.rejected()

    def test_unknown_length_coarsening_rejected(self):
        r = next(r for r in self.records() if r["full_feature_label_status"] == "UNKNOWN_INTERNAL_PARTITION")
        r["sequence_length"] = 1
        self.rejected()

    def test_whole_cipher_unithood_not_one(self):
        r = next(r for r in self.records() if r["full_feature_label_status"] == "ELIGIBLE_PROFILE_REFERENCE")
        r["internal_cipher_unit_count"] = 1
        self.rejected()

    def test_cipher_letter_leak_rejected(self):
        self.records()[0]["letter_value"] = "A"
        self.rejected()

    def test_source_status_change_rejected(self):
        self.records()[0]["source_physical_extent_status"] = "RESOLVED"
        self.rejected()

    def test_wrong_display_order_rejected(self):
        region = next(r for r in self.output["regions"] if r["region"] == "bottom-B2")
        region["records"].sort(key=lambda r: r["id"])
        self.rejected()

    def test_right_frame_wrong_sign_rejected(self):
        region = next(r for r in self.output["regions"] if r["region"] == "right-R1")
        region["projection_axis"] = "NATIVE_HORIZONTAL_INCREASING_X"
        self.rejected()

    def test_right_interval_wrong_sign_rejected(self):
        r = next(r for region in self.output["regions"] if region["region"] == "right-R1" for r in region["records"])
        y0, y1 = r["source_base_native_bbox_xyxy_halfopen"][1::2]
        r["projected_interval"] = [y0, y1]
        self.rejected()

    def test_overlap_cannot_be_precedence(self):
        pair = next(p for region in self.output["regions"] for p in region["pairwise_projected_relations"] if p["relation"] == "UNORDERED_PROJECTED_OVERLAP_OR_WITHIN_TOLERANCE")
        pair["relation"] = "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING"
        pair["direction"] = "LEFT_BEFORE_RIGHT"
        self.rejected()

    def test_geometry_boundary_eight_is_unordered(self):
        label, direction = core.relation([0, 0, 10, 10], [18, 0, 28, 10], "NATIVE_HORIZONTAL_INCREASING_X")
        self.assertEqual(label, "UNORDERED_PROJECTED_OVERLAP_OR_WITHIN_TOLERANCE")
        self.assertIsNone(direction)

    def test_geometry_nine_is_window_order_only(self):
        label, direction = core.relation([0, 0, 10, 10], [19, 0, 29, 10], "NATIVE_HORIZONTAL_INCREASING_X")
        self.assertEqual(label, "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING")
        self.assertEqual(direction, "LEFT_BEFORE_RIGHT")

    def test_unallocated_marks_no_axis(self):
        for region in self.output["regions"]:
            if region["region"] in {"bottom-unallocated-marks", "outer-top-red-trace"}:
                self.assertEqual(region["projection_axis"], "NO_IMPOSED_AXIS")
                self.assertTrue(all(p["relation"] == "UNORDERED_NO_IMPOSED_AXIS" for p in region["pairwise_projected_relations"]))

    def test_rectangle_overlap_not_alias(self):
        self.output["search_rectangle_intersections"][0]["relation"] = "PROVEN_ALIAS"
        self.rejected()

    def test_no_cross_region_link(self):
        self.output["regions"][0]["cross_region_links"] = "NEXT_ROW"
        self.rejected()

    def test_target_sidecar_cannot_replace_base_bbox(self):
        r = next(r for r in self.records() if r["id"] == "FC015")
        r["source_base_native_bbox_xyxy_halfopen"] = r["approved_target_locator_sidecar"]["native_bbox_xyxy_halfopen"]
        self.rejected()

    def test_frozen_conflict_omission_rejected(self):
        self.output["frozen_overlay_conflict_references"].pop()
        self.rejected()

    def test_transitive_nonclique_rejected(self):
        clique = self.output["graph"]["maximal_cliques"][0]
        clique["member_ids"].append("FC015")
        clique["member_ids"].sort()
        self.rejected()

    def test_overlapping_cliques_allowed_as_sets(self):
        self.output = core.assemble(self.inputs, self.graph_fixture())
        report = check(self.output, self.inputs)
        self.assertEqual(report["structural_new_edges"], 2)
        memberships = self.output["graph"]["memberships"]
        self.assertGreaterEqual(len(memberships["FC066"]), 2)
        self.assertGreaterEqual(len(memberships["FC074"]), 2)

    def test_forced_disjoint_membership_rejected(self):
        self.output = core.assemble(self.inputs, self.graph_fixture())
        self.output["graph"]["memberships"]["FC066"] = self.output["graph"]["memberships"]["FC066"][:1]
        self.rejected()

    def test_old_old_edge_without_prelog_rejected(self):
        fixture = self.graph_fixture()
        fixture["new_positive_edges"] = [{"member_ids": ["FC002", "FC004"], "origin": "CORE_930", "evidence_reference": fixture["new_positive_edges"][0]["evidence_reference"]}]
        with self.assertRaises(ValueError):
            core.assemble(self.inputs, fixture)

    def test_closure_without_trigger_edges_rejected(self):
        fixture = self.graph_fixture()
        ref = fixture["new_positive_edges"][0]["evidence_reference"]
        fixture["new_positive_edges"] = [{"member_ids": ["FC002", "FC004"], "origin": "PRELOGGED_OLD_OLD_CLOSURE", "evidence_reference": ref, "closure_prelog_reference": ref, "triggering_new_member": "FC015", "proposed_member_ids": ["FC002", "FC004", "FC015"]}]
        with self.assertRaises(ValueError):
            core.assemble(self.inputs, fixture)

    def test_synthetic_prelogged_closure_has_separate_origin(self):
        fixture = self.graph_fixture()
        ref = fixture["new_positive_edges"][0]["evidence_reference"]
        fixture["new_positive_edges"] = [
            {"member_ids": ["FC002", "FC015"], "origin": "CORE_930", "evidence_reference": ref},
            {"member_ids": ["FC004", "FC015"], "origin": "CORE_930", "evidence_reference": ref},
            {"member_ids": ["FC002", "FC004"], "origin": "PRELOGGED_OLD_OLD_CLOSURE", "evidence_reference": ref, "closure_prelog_reference": ref, "triggering_new_member": "FC015", "proposed_member_ids": ["FC002", "FC004", "FC015"]}]
        self.output = core.assemble(self.inputs, fixture)
        check(self.output, self.inputs)
        origins = [edge["origin"] for edge in self.output["graph"]["positive_edges"]]
        self.assertEqual(origins.count("INHERITED_11"), 11)
        self.assertEqual(origins.count("CORE_930"), 2)
        self.assertEqual(origins.count("PRELOGGED_OLD_OLD_CLOSURE"), 1)

    def test_safe_write_new_file_and_pins_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory).resolve()
            source = directory / "input.json"
            source.write_text("immutable")
            protected = {"fixture": (source, core.sha(source.read_bytes()))}
            destination = directory / "new.json"
            core.write_once(destination, {"fixture": True}, protected)
            self.assertEqual(json.loads(destination.read_text()), {"fixture": True})
            self.assertEqual(source.read_text(), "immutable")

    def test_source_output_alias_and_existing_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve() / "input.json"
            source.write_text("immutable")
            protected = {"fixture": (source, core.sha(source.read_bytes()))}
            with self.assertRaises(ValueError):
                core.write_once(source, {}, protected)
            self.assertEqual(source.read_text(), "immutable")

    def test_hardlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory).resolve()
            source, output = directory / "input.json", directory / "hardlink.json"
            source.write_text("immutable")
            os.link(source, output)
            with self.assertRaises(ValueError):
                core.write_once(output, {}, {"fixture": (source, core.sha(source.read_bytes()))})
            self.assertEqual(source.read_text(), "immutable")

    def test_symlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory).resolve()
            output = directory / "symlink.json"
            output.symlink_to(directory / "missing.json")
            with self.assertRaises(ValueError):
                core.write_once(output, {}, {})

    def test_symlink_parent_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory).resolve()
            actual, linked = directory / "actual", directory / "linked"
            actual.mkdir()
            linked.symlink_to(actual)
            with self.assertRaises(ValueError):
                core.write_once(linked / "new.json", {}, {})

    def test_failed_postwrite_pin_check_removes_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory).resolve()
            source, output = directory / "input.json", directory / "new.json"
            source.write_text("immutable")
            protected = {"fixture": (source, core.sha(source.read_bytes()))}
            original = core.verify_unchanged
            calls = []
            def injected_check(paths):
                calls.append(True)
                if len(calls) == 2:
                    raise ValueError("Synthetic post-write immutable violation")
                return original(paths)
            core.verify_unchanged = injected_check
            try:
                with self.assertRaises(ValueError):
                    core.write_once(output, {}, protected)
            finally:
                core.verify_unchanged = original
            self.assertFalse(output.exists())
            self.assertEqual(source.read_text(), "immutable")


if __name__ == "__main__":
    unittest.main()
