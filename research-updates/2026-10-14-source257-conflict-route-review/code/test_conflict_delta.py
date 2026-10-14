#!/usr/bin/env python3
"""D13 synthetic gate fixtures; no manuscript feature judgments are created."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import conflict_delta as core
from check_conflict_delta import check, check_sequence


def fixture_reports(data):
    profiles = data["intake"]["profiles"]
    pins = {"safe_protocol_sha256": data["_hashes"]["safe_protocol"], "safe_intake_sha256": data["_hashes"]["intake"], "context_index_sha256": data["_hashes"]["board_index"], "output_format_sha256": data["_hashes"]["format"]}
    targets = []
    for profile in profiles:
        ident = profile["id"]
        contexts = [v["context_id"] for v in profile["windows"].values()]
        box = profile["approved_target_bbox"]
        targets.append({"id": ident, "approved_target_native_bbox_xyxy_halfopen": box, "frame": "EXACT90CW" if profile["rotation_degrees_clockwise"] == 90 else "NATIVE0", "source_context_ids": contexts, "full_route_description": "SYNTHETIC fixture only, no actual source conclusion.", "binding_state": "SUPPORTED_TARGET_ROUTE", "eight_features": {f: {"observation": "SYNTHETIC fixture source fact for " + f, "certainty": "SOURCE_SUPPORTED", "native_locator_boxes": [box], "source_context_ids": contexts, "absence_claim": False, "relevant_route_visibility": "FULL"} for f in core.FIELDS}, "free_end_observations": [{"description": "SYNTHETIC endpoint", "native_locator_boxes": [box], "source_context_ids": contexts, "ownership": "TARGET_ROUTE", "actual_visibility": "FULL", "continuity_source_witness": "SYNTHETIC continuity witness, not a real image interpretation.", "neighbor_ids": []}], "bar_return_junctions": [], "competing_routes": [], "cipher_identity": "UNKNOWN", "letter_value": "UNKNOWN"})
    indices = {t["id"]: i for i, t in enumerate(targets)}
    rows = []
    for key in data["protocol"]["fixed_pair_ids"]:
        members = key.split("--")
        checks = {}
        for field in core.FIELDS:
            checks[field] = {"left_target_feature_ref": f"/target_observations/{indices[members[0]]}/eight_features/{field}", "right_target_feature_ref": f"/target_observations/{indices[members[1]]}/eight_features/{field}", "paired_source_grounds": "SYNTHETIC fixture paired relation only.", "relation": "SUPPORTED_COMPATIBLE", "native_locator_boxes_left": [targets[indices[members[0]]]["approved_target_native_bbox_xyxy_halfopen"]], "native_locator_boxes_right": [targets[indices[members[1]]]["approved_target_native_bbox_xyxy_halfopen"]], "source_context_ids": targets[indices[members[0]]]["source_context_ids"] + targets[indices[members[1]]]["source_context_ids"], "relevant_visibility_left": "FULL", "relevant_visibility_right": "FULL", "ownership_supported_left": True, "ownership_supported_right": True, "incompatibility_kind": "NONE"}
        rows.append({"pair_id": key, "member_ids": members, "actual_native_board_id": data["_pair_boards"][key][0], "coverage": "DIRECT_NATIVE_PAIRED_SOURCE_INSPECTION", "eight_paired_comparisons": checks, "candidate_outcome": core.SAME, "significant_variation": ["SYNTHETIC fixture variation preserved"], "remaining_uncertainty": [], "cipher_identity": "UNKNOWN", "letter_value": "UNKNOWN"})
    for label in ("A", "B"):
        data["reader_" + label] = {"schema": "source257-conflict-route-reader-initial-v1", "reader": "Synthetic fixture reader " + label, "phase": "INITIAL_SOURCE_ONLY_FROZEN", "frozen_utc": "2026-10-14T03:00:00+00:00", "input_pins": pins, "original_source_pins": {"encoded_sha256": data["protocol"]["input_sha256"]["source_encoded"], "rgb_sha256": data["protocol"]["input_sha256"]["source_RGB"]}, "whole_private_proof_json_sha256": "0" * 64, "prior_exposure": {"geometry_and_cohort_selection_seen": True, "historical_feature_or_outcome_claims_seen": False, "other_initial_reader_report_seen": False, "details": "SYNTHETIC fixture, no real image inspection."}, "actual_pair_ids_viewed": list(data["protocol"]["fixed_pair_ids"]), "target_observations": copy.deepcopy(targets), "pair_observations": copy.deepcopy(rows)}
        data["_hashes"]["reader_" + label] = core.canonical_sha(data["reader_" + label])
    for label in ("A", "B"):
        data["historical_claims"] = {"schema": "SYNTHETIC_HISTORICAL_CLAIMS_ONLY", "claims": []}
        data["_hashes"]["historical_claims"] = core.canonical_sha(data["historical_claims"])
        data["history_" + label] = {"schema": "source257-conflict-route-historical-audit-v1", "reader": "Synthetic historical audit " + label, "frozen_utc": "2026-10-14T03:01:00+00:00", "exposure": {"own_initial_report_read": True, "compact_historical_claims_read": True, "other_initial_report_read": False, "details": "SYNTHETIC post-feedback exposure."}, "phase": "POST_BOTH_INITIAL_FREEZES_HISTORICAL_AUDIT", "input_pins": {"baseline_sha256": core.BASELINE_SHA, "reader_A_sha256": data["_hashes"]["reader_A"], "reader_B_sha256": data["_hashes"]["reader_B"], "historical_claims_sha256": data["_hashes"]["historical_claims"], "audit_output_format_sha256": data["_hashes"]["audit_format"]}, "target_audit_records": [{"id": t["id"], "status": "NO_CONFIRMED_LITERAL_CORRECTION", "claim_ids": [], "support_qualification_ids": [], "own_initial_source_fact_refs": [f"/target_observations/{i}/eight_features/path_topology/observation"], "grounds": "SYNTHETIC historical comparison only."} for i, t in enumerate(targets)], "pair_audit_records": [{"pair_id": row["pair_id"], "member_ids": row["member_ids"], "status": "NO_CONFIRMED_CORRECTION", "claim_ids": [], "support_qualification_ids": [], "own_initial_pair_ref": f"/pair_observations/{i}", "grounds": "SYNTHETIC pair audit only."} for i, row in enumerate(rows)], "correction_claims": [], "support_qualification_records": []}
        data["_hashes"]["history_" + label] = core.canonical_sha(data["history_" + label])
    data["final_review"] = {"schema": "source257-conflict-route-final-ai-v1", "input_pins": {"protocol_sha256": data["_hashes"]["protocol"], "baseline_sha256": core.BASELINE_SHA, "reader_A_sha256": data["_hashes"]["reader_A"], "reader_B_sha256": data["_hashes"]["reader_B"], "historical_A_sha256": data["_hashes"]["history_A"], "historical_B_sha256": data["_hashes"]["history_B"], "historical_claims_sha256": data["_hashes"]["historical_claims"], "final_output_format_sha256": data["_hashes"]["final_format"]}, "conditioning": {"both_initials_read": True, "historical_addenda_read": True, "is_blind_agreement": False, "details": "SYNTHETIC final source conditioning."}, "source_verification": {"whole_original_encoded_sha256": data["protocol"]["input_sha256"]["source_encoded"], "whole_original_rgb_sha256": data["protocol"]["input_sha256"]["source_RGB"], "whole_private_proof_json_sha256": "0" * 64, "proof_before_view": True, "target_binding_is_source_judgment": True}, "coverage": {"scope": "FIXED38_ONLY", "actual_pair_ids_viewed": list(data["protocol"]["fixed_pair_ids"]), "actual_target_ids_inspected": list(data["protocol"]["fixed_profile_ids"]), "source_board_ids": sorted({board for ids in data["_pair_boards"].values() for board in ids})}, "target_observations": copy.deepcopy(targets), "pair_reviews": copy.deepcopy(rows), "correction_reviews": [], "qualification_reviews": [], "quarantine_reviews": []}
    data["_hashes"]["final_review"] = core.canonical_sha(data["final_review"])
    data["final_review"].update(reviewer="Synthetic separate final audit", frozen_utc="2026-10-14T03:02:00+00:00")
    data["_synthetic_fixture_only"] = True


class ConflictDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repository = Path(os.environ.get("SOURCE257_PUBLIC_REPOSITORY", str(Path(__file__).resolve().parents[3])))
        cls.raw, _ = core.load(repository)
        cls.actual_initials = {name: cls.raw[name] for name in ("reader_A", "reader_B")}
        fixture_reports(cls.raw)
        cls.output = core.build(cls.raw)

    def setUp(self):
        self.data = {**self.raw, "_hashes": dict(self.raw["_hashes"]), "_protected": dict(self.raw["_protected"])}
        for name in ("reader_A", "reader_B", "history_A", "history_B", "final_review"):
            self.data[name] = copy.deepcopy(self.raw[name])

    def invalid(self):
        with self.assertRaises((ValueError, KeyError)):
            core.build(self.data)

    def test_synthetic_complete_reports_pass(self):
        self.assertEqual(check(self.output, self.raw)["status"], "PASS_SYNTHETIC_FIXTURE_ONLY")

    def test_wrong38_pair_scope_rejected(self):
        self.data["reader_A"]["pair_observations"].pop()
        self.invalid()

    def test_duplicate_pair_rejected(self):
        self.data["reader_A"]["pair_observations"][-1] = self.data["reader_A"]["pair_observations"][0]
        self.invalid()

    def test_omitted29_target_fact_rejected(self):
        self.data["reader_B"]["target_observations"].pop()
        self.invalid()

    def test_historical_audit_coverage_cannot_omit_target(self):
        self.data["history_A"]["target_audit_records"].pop()
        self.invalid()

    def test_historical_audit_coverage_cannot_omit_pair(self):
        self.data["history_B"]["pair_audit_records"].pop()
        self.invalid()

    def test_wrong_target_context_rejected(self):
        self.data["reader_A"]["target_observations"][0]["source_context_ids"] = self.data["reader_A"]["target_observations"][1]["source_context_ids"]
        self.invalid()

    def test_invalid_source_frame_rejected(self):
        self.data["reader_B"]["target_observations"][0]["frame"] = "NATIVE0"
        self.invalid()

    def test_invalid_final_source_frame_rejected(self):
        self.data["final_review"]["target_observations"][0]["frame"] = "NATIVE0"
        self.invalid()

    def test_wrong_pair_board_rejected(self):
        self.data["reader_A"]["pair_observations"][0]["actual_native_board_id"] = "board-999"
        self.invalid()

    def test_unknown_cannot_be_absence(self):
        feature = self.data["reader_A"]["target_observations"][0]["eight_features"]["attached_bars"]
        feature.update(observation="UNKNOWN", certainty="UNRESOLVED", absence_claim=True, relevant_route_visibility="UNRESOLVED")
        self.invalid()

    def test_unknown_feature_defers_never_wildcard(self):
        target = self.data["reader_A"]["target_observations"][0]
        target["eight_features"]["attached_bars"].update(observation="UNKNOWN", certainty="UNRESOLVED", relevant_route_visibility="UNRESOLVED")
        output = core.build(self.data)
        self.assertTrue(all(r["status"].startswith("DEFERRED") for r in output["pair_dispositions"] if target["id"] in r["member_ids"]))

    def test_partial_eight_feature_positive_rejected(self):
        del self.data["reader_A"]["pair_observations"][0]["eight_paired_comparisons"]["owned_mark_profile"]
        self.invalid()

    def test_pair_feature_pointer_wrong_target_rejected(self):
        self.data["reader_A"]["pair_observations"][0]["eight_paired_comparisons"]["path_topology"]["left_target_feature_ref"] = "/target_observations/28/eight_features/path_topology"
        self.invalid()

    def test_partial_free_end_visibility_defers(self):
        target = self.data["reader_A"]["target_observations"][0]
        target["free_end_observations"][0]["actual_visibility"] = "UNRESOLVED"
        output = core.build(self.data)
        self.assertTrue(all(r["status"].startswith("DEFERRED") for r in output["pair_dispositions"] if target["id"] in r["member_ids"]))

    def set_difference(self, kind):
        for report, field in ((self.data["reader_A"], "pair_observations"), (self.data["reader_B"], "pair_observations"), (self.data["final_review"], "pair_reviews")):
            row = report[field][0]
            row["candidate_outcome"] = core.DIFFERENT
            row["eight_paired_comparisons"]["terminal_pattern"].update(relation="POSITIVELY_INCOMPATIBLE", incompatibility_kind=kind)

    def test_difference_on_mere_length_variation_not_released(self):
        self.set_difference("UNVALIDATED_VARIATION")
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_VARIATION")

    def test_supported_terminal_presence_difference_not_graph_edge(self):
        self.set_difference("TERMINAL_PRESENCE")
        output = core.build(self.data)
        row = output["pair_dispositions"][0]
        self.assertEqual(row["status"], "SOURCE_GATED_GRAPHICAL_DIFFERENCE_NOT_CANNOT_LINK")
        self.assertNotIn(row["pair_id"], output["current_graph_overlay"]["added_positive_pair_ids"])

    def test_difference_partial_relevant_end_visibility_defers(self):
        self.set_difference("TERMINAL_PRESENCE")
        self.data["reader_A"]["pair_observations"][0]["eight_paired_comparisons"]["terminal_pattern"]["relevant_visibility_right"] = "UNRESOLVED"
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_VARIATION")

    def test_supported_difference_survives_unrelated_feature_uncertainty(self):
        self.set_difference("TERMINAL_PRESENCE")
        for name in ("reader_A", "reader_B", "final_review"):
            target = self.data[name]["target_observations"][0]
            target["eight_features"]["attached_bars"].update(observation="UNKNOWN", certainty="UNRESOLVED", relevant_route_visibility="UNRESOLVED")
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "SOURCE_GATED_GRAPHICAL_DIFFERENCE_NOT_CANNOT_LINK")

    def test_mismatched_difference_invariant_kinds_defer(self):
        self.set_difference("TERMINAL_PRESENCE")
        self.data["reader_B"]["pair_observations"][0]["eight_paired_comparisons"]["terminal_pattern"]["incompatibility_kind"] = "ATTACHMENT"
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_VARIATION")

    def test_difference_unowned_relevant_witness_defers(self):
        self.set_difference("TERMINAL_PRESENCE")
        self.data["final_review"]["pair_reviews"][0]["eight_paired_comparisons"]["terminal_pattern"]["ownership_supported_right"] = False
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_VARIATION")

    def test_difference_unresolved_target_binding_defers(self):
        self.set_difference("TERMINAL_PRESENCE")
        self.data["reader_B"]["target_observations"][0]["binding_state"] = core.BINDING
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_VARIATION")

    def test_other_reader_exposure_is_not_blind_support(self):
        self.data["reader_A"]["prior_exposure"]["other_initial_reader_report_seen"] = True
        self.assertTrue(all(r["status"].startswith("DEFERRED") for r in core.build(self.data)["pair_dispositions"]))

    def test_binding_uncertainty_retained(self):
        self.data["reader_A"]["pair_observations"][0]["candidate_outcome"] = core.BINDING
        self.assertEqual(core.build(self.data)["pair_dispositions"][0]["status"], "DEFERRED_BINDING")

    def test_transitive_clique_rejected(self):
        output = copy.deepcopy(self.output)
        group = output["current_graph_overlay"]["maximal_edge_complete_cliques"][0]
        group["member_ids"].append("U002")
        with self.assertRaises(ValueError):
            check(output, self.raw)

    def test_overlapping_memberships_not_forced_to_partition(self):
        output = copy.deepcopy(self.output)
        memberships = output["current_graph_overlay"]["memberships"]
        ident = next(n for n, groups in memberships.items() if len(groups) > 1)
        memberships[ident] = memberships[ident][:1]
        with self.assertRaises(ValueError):
            check(output, self.raw)

    def test_quarantine_overreach_without_factual_correction_rejected(self):
        self.data["final_review"]["quarantine_reviews"] = [{"pair_id": "FC002--FC013", "claim_id": "unfounded", "decision": "QUARANTINE_EXACT_DEPENDENT_EDGE", "grounds": "Synthetic claim"}]
        self.invalid()

    def add_correction(self):
        edge = next(e for e in self.data["baseline"]["graph"]["positive_edges"] if e["pair_id"] == "FC013--FC068")
        reference = {"artifact_sha256": self.data["baseline"]["input_bindings"]["D10"]["sha256"], "json_pointer": "/candidate_classes/2/significant_signature/attached_bars"}
        old = core.old_fact(self.data, reference)
        indices = {t["id"]: i for i, t in enumerate(self.data["reader_A"]["target_observations"])}
        target = self.data["reader_A"]["target_observations"][indices["FC013"]]
        claim = {"claim_id": "SYNTHETIC-C1", "target_ids": ["FC013"], "old_fact_reference": reference, "old_literal": old, "corrected_source_fact": "SYNTHETIC source correction only; not a historical finding.", "new_source_fact_refs": [{"reader": "A", "json_pointer": f"/target_observations/{indices['FC013']}/eight_features/attached_bars/observation"}], "native_locator_boxes": [target["approved_target_native_bbox_xyxy_halfopen"]], "source_context_ids": target["source_context_ids"], "dependent_edge_claims": [{"pair_id": edge["pair_id"], "accepted_edge_evidence_reference": edge["evidence_reference"], "fact_dependency_grounds": "SYNTHETIC exact authority dependency, not a real finding."}]}
        self.data["history_A"]["correction_claims"] = [claim]
        self.data["final_review"]["correction_reviews"] = [{"claim_id": claim["claim_id"], "decision": "SUPPORTED_SOURCE_FACT_CORRECTION", "grounds": "SYNTHETIC full source fact adjudication.", "native_locator_boxes": claim["native_locator_boxes"], "source_context_ids": claim["source_context_ids"]}]
        self.data["final_review"]["quarantine_reviews"] = [{"pair_id": edge["pair_id"], "claim_id": claim["claim_id"], "decision": "QUARANTINE_EXACT_DEPENDENT_EDGE", "accepted_authority_effect": "SOURCE_FACT_CONTRADICTED", "grounds": "SYNTHETIC exact edge quarantine only."}]
        return claim, edge

    def test_quarantine_only_exact_supported_dependency(self):
        _, edge = self.add_correction()
        output = core.build(self.data)
        removed = output["current_graph_overlay"]["quarantined_baseline_edges"]
        self.assertEqual([q["pair_id"] for q in removed], [edge["pair_id"]])
        others = {e["pair_id"] for e in self.data["baseline"]["graph"]["positive_edges"]} - {edge["pair_id"]}
        self.assertTrue(others <= set(output["current_graph_overlay"]["current_positive_pair_ids"]))

    def test_wrong_historical_literal_rejected(self):
        claim, _ = self.add_correction()
        claim["old_literal"] = "Not the exact historical field"
        self.invalid()

    def test_missing_final_correction_native_witness_rejected(self):
        self.add_correction()
        del self.data["final_review"]["correction_reviews"][0]["native_locator_boxes"]
        self.invalid()

    def test_missing_final_correction_source_context_rejected(self):
        self.add_correction()
        del self.data["final_review"]["correction_reviews"][0]["source_context_ids"]
        self.invalid()

    def test_omitted_explicit_dependency_review_rejected(self):
        self.add_correction()
        self.data["final_review"]["quarantine_reviews"] = []
        self.invalid()

    def test_missing_historical_exposure_rejected(self):
        del self.data["history_A"]["exposure"]
        self.invalid()

    def test_missing_historical_reader_rejected(self):
        del self.data["history_A"]["reader"]
        self.invalid()

    def test_missing_historical_timestamp_rejected(self):
        del self.data["history_A"]["frozen_utc"]
        self.invalid()

    def test_audit_row_cites_another_target_rejected(self):
        self.data["history_A"]["target_audit_records"][0]["own_initial_source_fact_refs"] = ["/target_observations/1/full_route_description"]
        self.invalid()

    def test_supported_correction_cannot_cite_unknown_feature(self):
        claim, _ = self.add_correction()
        index = int(claim["new_source_fact_refs"][0]["json_pointer"].split("/")[2])
        self.data["reader_A"]["target_observations"][index]["eight_features"]["attached_bars"].update(observation="UNKNOWN", certainty="UNRESOLVED", relevant_route_visibility="UNRESOLVED")
        self.invalid()

    def test_unresolved_dependency_retains_but_flags_exact_edge(self):
        _, edge = self.add_correction()
        self.data["final_review"]["correction_reviews"][0]["decision"] = "UNRESOLVED_OR_REPEATED_DISAGREEMENT"
        review = self.data["final_review"]["quarantine_reviews"][0]
        review.update(decision="DEFER_EXACT_DEPENDENCY", accepted_authority_effect="DEPENDENCY_SOURCE_SUPPORT_UNRESOLVED")
        self.data["final_review"]["input_pins"]["dependency_format_addendum_sha256"] = self.data["_hashes"]["dependency_format_addendum"]
        output = core.build(self.data)
        overlay = output["current_graph_overlay"]
        self.assertEqual(overlay["quarantined_baseline_edges"], [])
        self.assertIn(edge["pair_id"], overlay["current_positive_pair_ids"])
        self.assertEqual([r["pair_id"] for r in overlay["unresolved_dependency_edges"]], [edge["pair_id"]])

    def test_unresolved_dependency_without_addendum_pin_rejected(self):
        self.add_correction()
        review = self.data["final_review"]["quarantine_reviews"][0]
        review.update(decision="DEFER_EXACT_DEPENDENCY", accepted_authority_effect="DEPENDENCY_SOURCE_SUPPORT_UNRESOLVED")
        self.invalid()

    def test_repeated_disagreement_not_correction_quarantine(self):
        self.add_correction()
        self.data["final_review"]["correction_reviews"][0]["decision"] = "UNRESOLVED_OR_REPEATED_DISAGREEMENT"
        self.invalid()

    def test_existing_final_evidence_can_retain_edge(self):
        self.add_correction()
        self.data["final_review"]["quarantine_reviews"][0]["decision"] = "RETAIN_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT"
        self.data["final_review"]["quarantine_reviews"][0]["accepted_authority_effect"] = "EXISTING_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT"
        self.assertEqual(core.build(self.data)["current_graph_overlay"]["quarantined_baseline_edges"], [])

    def test_audit_cannot_require_or_cite_other_reader_as_own_fact(self):
        claim, _ = self.add_correction()
        claim["new_source_fact_refs"][0]["reader"] = "B"
        self.invalid()

    def add_qualification(self):
        claim, edge = self.add_correction()
        qualification = {"qualification_id": "SYNTHETIC-Q1", "target_ids": claim["target_ids"], "pair_ids": [], "kind": "OVERSTATEMENT_OF_CERTAINTY", "old_fact_reference": claim["old_fact_reference"], "old_literal": claim["old_literal"], "qualification": "SYNTHETIC precise accepted authority lacks source support, without a contrary fact.", "own_initial_source_fact_refs": claim["new_source_fact_refs"], "native_locator_boxes": claim["native_locator_boxes"], "source_context_ids": claim["source_context_ids"], "dependent_edge_claims": claim["dependent_edge_claims"]}
        self.data["history_A"]["correction_claims"] = []
        self.data["history_A"]["support_qualification_records"] = [qualification]
        self.data["final_review"]["correction_reviews"] = []
        self.data["final_review"]["qualification_reviews"] = [{"qualification_id": "SYNTHETIC-Q1", "decision": "SUPPORTED_SOURCE_SUPPORT_QUALIFICATION", "grounds": "SYNTHETIC exact source authority impact.", "native_locator_boxes": claim["native_locator_boxes"], "source_context_ids": claim["source_context_ids"]}]
        q = self.data["final_review"]["quarantine_reviews"][0]
        q.pop("claim_id")
        q["qualification_id"] = "SYNTHETIC-Q1"
        q["accepted_authority_effect"] = "SPECIFIC_AUTHORITATIVE_SUPPORT_NOT_ESTABLISHED"
        return qualification, edge

    def test_precise_support_qualification_can_quarantine_without_opposite_fact(self):
        self.add_qualification()
        output = core.build(self.data)
        self.assertEqual(output["correction_dispositions"], [])
        self.assertEqual([r["pair_id"] for r in output["current_graph_overlay"]["quarantined_baseline_edges"]], ["FC013--FC068"])

    def test_qualification_cites_another_target_rejected(self):
        qualification, _ = self.add_qualification()
        qualification["own_initial_source_fact_refs"] = ["/target_observations/0/full_route_description"]
        self.invalid()

    def test_qualification_empty_source_refs_rejected(self):
        qualification, _ = self.add_qualification()
        qualification["own_initial_source_fact_refs"] = []
        self.invalid()

    def test_disagreement_only_cannot_be_quarantined(self):
        qualification, _ = self.add_qualification()
        qualification["kind"] = "HISTORICAL_DISAGREEMENT_ONLY"
        self.invalid()

    def test_final_reviewer_metadata_required(self):
        del self.data["final_review"]["reviewer"]
        self.invalid()

    def test_final_time_metadata_required(self):
        del self.data["final_review"]["frozen_utc"]
        self.invalid()

    def test_final_proof_whole_sha_must_be_lower_hex(self):
        self.data["final_review"]["source_verification"]["whole_private_proof_json_sha256"] = "z" * 64
        self.invalid()

    def test_actual_initial_uncertainty_does_not_autoquarantine(self):
        for name, report in self.actual_initials.items():
            self.data[name] = report
        a, _ = core.validate_initial(self.data, "reader_A")
        b, _ = core.validate_initial(self.data, "reader_B")
        self.assertEqual((len(a), len(b)), (29, 29))
        # No source conclusion is produced: this checks that validation of raw
        # uncertainty itself has no current-graph mutation side effect.
        self.assertEqual(self.data["baseline"]["graph"]["positive_edges"], self.raw["baseline"]["graph"]["positive_edges"])

    def test_production_fake_final_hash_rejected(self):
        self.data.pop("_synthetic_fixture_only")
        self.data["_hashes"]["final_review"] = "f" * 64
        self.invalid()

    def test_synthetic_production_write_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory).resolve() / "production.json"
            with self.assertRaises(ValueError):
                core.write_production(destination, self.output, {})
            self.assertFalse(destination.exists())

    def test_source_output_alias_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve() / "source.json"
            source.write_text("immutable")
            with self.assertRaises(ValueError):
                core.write_once(source, {}, {"source": (source, core.sha(source.read_bytes()))})
            self.assertEqual(source.read_text(), "immutable")

    def test_output_hardlink_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory).resolve()
            source, hard, sym = folder / "source.json", folder / "hard.json", folder / "sym.json"
            source.write_text("immutable")
            os.link(source, hard)
            sym.symlink_to(source)
            for path in (hard, sym):
                with self.assertRaises(ValueError):
                    core.write_once(path, {}, {"source": (source, core.sha(source.read_bytes()))})

    def test_tsv_membership_only_roundtrip(self):
        text = core.current_sequence_tsv(self.output, self.raw["baseline"])
        self.assertEqual(check_sequence(text, self.output, self.raw)["annotation_rows"], 307)

    def test_tsv_geometry_or_unknown_length_tamper_rejected(self):
        text = core.current_sequence_tsv(self.output, self.raw["baseline"]).replace("UNKNOWN_LENGTH\tUNKNOWN", "1\tUNKNOWN", 1)
        with self.assertRaises(ValueError):
            check_sequence(text, self.output, self.raw)

    def test_conditional772_not_executed(self):
        self.assertEqual(self.output["conditional772"]["additional_comparisons"], 0)
        altered = copy.deepcopy(self.output)
        altered["conditional772"]["additional_comparisons"] = 1
        with self.assertRaises(ValueError):
            check(altered, self.raw)


if __name__ == "__main__":
    unittest.main()
