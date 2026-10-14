"""D14-only synthetic structural/evidence-boundary fixtures; no source pixels."""
import copy
import csv
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
import direct772_checkpoint as c
import check_direct772_checkpoint as check


def fixture_data():
    repo = Path(os.environ.get("SOURCE257_PUBLIC_REPOSITORY", Path(__file__).resolve().parents[3]))
    data, _ = c.load_metadata(repo)
    geometry = c.profiles(data)
    selected = data["queue"]["selected_pair_ids"]
    boards = []
    for offset in range(0, 64, 4):
        pairs = selected[offset:offset + 4]
        panels = []
        for pair in pairs:
            for ident in pair.split("--"):
                for kind, window in geometry[ident]["windows"].items():
                    panels.append({"pair_id": pair, "target_id": ident, "window_kind": kind, "context_id": window["context_id"], "native_bbox_xyxy_halfopen": window["native_bbox_xyxy_halfopen"], "rotation_degrees_clockwise": geometry[ident]["rotation_degrees_clockwise"]})
        boards.append({"board_id": f"SYNTHETIC-BOARD-{offset // 4 + 1:02d}", "pair_ids": pairs, "panels": panels})
    data["board_index"] = {"safe_intake_sha256": data["_hashes"]["intake"], "source_size": data["intake"]["source_size"], "scale": 1, "boards": boards}
    data["_hashes"]["board_index"] = "f" * 64
    data["_paths"]["board_index"] = "SYNTHETIC_FIXTURE_INDEX_NOT_A_SAVED_SCIENTIFIC_REPORT"
    data["_pair_boards"] = c.validate_index(data)
    target_rows = []
    for ident in data["queue"]["selected_profile_ids"]:
        p = geometry[ident]
        refs = [w["context_id"] for w in p["windows"].values()]
        features = {field: {"observation": "Synthetic fixture complete owned route feature " + field, "certainty": "SOURCE_SUPPORTED", "native_locator_boxes": [p["approved_target_bbox"]], "source_context_ids": refs, "ownership": "TARGET_ROUTE", "relevant_route_visibility": "FULL", "absence_claim": False, "continuity_source_witness": "Synthetic fixture visible continuous target path"} for field in c.FIELDS}
        element = {"description": "Synthetic fixture endpoint observed", "native_locator_boxes": [p["approved_target_bbox"]], "source_context_ids": refs, "ownership": "TARGET_ROUTE", "actual_visibility": "FULL", "continuity_source_witness": "Synthetic fixture continuous owned endpoint", "neighbor_ids": []}
        target_rows.append({"id": ident, "approved_target_native_bbox_xyxy_halfopen": p["approved_target_bbox"], "frame": p["frame"], "source_context_ids": refs, "full_route_description": "Synthetic fixture route only; no scientific observation", "binding_state": "SUPPORTED_TARGET_ROUTE", "complete_route_visibility": "FULL", "eight_features": features, "free_end_observations": [element], "bar_return_junctions": [], "competing_routes": [], "cipher_identity": "UNKNOWN", "letter_value": "UNKNOWN"})
    indexes = {r["id"]: i for i, r in enumerate(target_rows)}
    paired = []
    for pair in selected:
        members = pair.split("--")
        comparisons = {}
        for field in c.FIELDS:
            comparisons[field] = {"left_target_feature_ref": f"/target_observations/{indexes[members[0]]}/eight_features/{field}", "right_target_feature_ref": f"/target_observations/{indexes[members[1]]}/eight_features/{field}", "paired_source_grounds": "Synthetic fixture paired relation remains unsettled", "relation": "UNRESOLVED", "native_locator_boxes_left": [geometry[members[0]]["approved_target_bbox"]], "native_locator_boxes_right": [geometry[members[1]]["approved_target_bbox"]], "source_context_ids": [w["context_id"] for ident in members for w in geometry[ident]["windows"].values()], "relevant_visibility_left": "FULL", "relevant_visibility_right": "FULL", "ownership_supported_left": True, "ownership_supported_right": True, "difference_kind": "NONE"}
        paired.append({"pair_id": pair, "member_ids": members, "actual_native_board_id": data["_pair_boards"][pair], "coverage": "DIRECT_NATIVE_PAIRED_SOURCE_INSPECTION", "eight_paired_comparisons": comparisons, "candidate_outcome": c.UNCERTAIN, "significant_variation": [], "remaining_uncertainty": ["Synthetic fixture relation unresolved"], "cipher_identity": "UNKNOWN", "letter_value": "UNKNOWN", "allographic_significance": "UNKNOWN"})
    inputs = {key: data["_hashes"][name] for key, name in (("safe_protocol_sha256", "safe_protocol"), ("safe_intake_sha256", "intake"), ("queue_sha256", "queue"), ("context_index_sha256", "board_index"), ("output_format_sha256", "format"))}
    source = data["safe_protocol"]["original_source"]
    common = {"schema": "source257-direct772-reader-initial-v1", "reader": "Synthetic fixture reader", "phase": "INITIAL_SOURCE_ONLY_FROZEN", "frozen_utc": "2026-10-14T23:00:00Z", "input_pins": inputs, "original_source_pins": {"encoded_sha256": source["encoded_sha256"], "rgb_sha256": source["rgb_sha256"]}, "whole_private_proof_json_sha256": "a" * 64, "proof_before_view": True, "prior_exposure": {"geometry_and_batch_selection_seen": True, "historical_feature_or_outcome_claims_seen": False, "other_initial_reader_report_seen": False, "details": "Synthetic fixture only, not an actual source report"}, "coverage": {"scope": "FIXED_FIRST64_ONLY", "actual_pair_ids_viewed": selected, "actual_target_ids_inspected": data["queue"]["selected_profile_ids"], "actual_board_ids_viewed": list(dict.fromkeys(data["_pair_boards"].values()))}, "target_observations": target_rows, "pair_observations": paired}
    for name in ("reader_A", "reader_B", "final_review"):
        data[name] = copy.deepcopy(common)
        data["_hashes"][name] = {"reader_A": "a", "reader_B": "b", "final_review": "c"}[name] * 64
        data["_paths"][name] = "SYNTHETIC_FIXTURE_ONLY_" + name
    final = data["final_review"]
    final.update(schema="source257-direct772-final-ai-v1", reviewer="Synthetic fixture final reviewer", phase="FINAL_SOURCE_ADJUDICATION", frozen_utc="2026-10-14T23:30:00Z", conditioning={"both_initials_read": True, "is_blind_agreement": False, "details": "Synthetic conditioned fixture using same fabricated source facts"})
    final.pop("prior_exposure")
    final.pop("reader")
    final["input_pins"].update({key: data["_hashes"][name] for key, name in (("protocol_sha256", "protocol"), ("reader_A_sha256", "reader_A"), ("reader_B_sha256", "reader_B"), ("final_output_format_sha256", "final_format"))})
    for row in final["pair_observations"]:
        row["adjudication_grounds"] = "Synthetic fixture actual evidence explanation; relation remains unresolved"
    return data


class CheckpointFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = fixture_data()

    def setUp(self):
        self.d = copy.deepcopy(self.seed)

    def build(self):
        return c.build(self.d, fixture=True)

    def reject(self):
        with self.assertRaises((ValueError, KeyError)):
            self.build()

    def pair(self, name="reader_A"):
        return self.d[name]["pair_observations"][0]

    def fact(self, field="terminal_pattern", name="reader_A"):
        ident = self.pair(name)["member_ids"][0]
        return next(t for t in self.d[name]["target_observations"] if t["id"] == ident)["eight_features"][field]

    def repeat(self):
        for name in ("reader_A", "reader_B", "final_review"):
            row = self.pair(name)
            row.update(candidate_outcome=c.REPEAT, significant_variation=[], remaining_uncertainty=[])
            for comp in row["eight_paired_comparisons"].values():
                comp.update(relation="SUPPORTED_COMPATIBLE", paired_source_grounds="Synthetic fixture visible complete paired compatibility")

    def difference(self, kind="VISIBLE_FORM_VARIATION", field="terminal_pattern"):
        for name in ("reader_A", "reader_B", "final_review"):
            self.pair(name)["candidate_outcome"] = c.DIFFERENCE
            self.pair(name)["significant_variation"] = ["Synthetic fixture positive visible terminal direction variation"]
            self.pair(name)["eight_paired_comparisons"][field].update(relation="OBSERVED_DIFFERENCE", difference_kind=kind, paired_source_grounds="Synthetic fixture visible owned left/right terminal difference")

    def test_exact772_checkpoint_and_tsv(self):
        result = self.build()
        receipt = check.check(result, self.d, fixture=True)
        self.assertEqual(receipt["checked_pairs"], 64)
        self.assertEqual(receipt["not_inspected"], 708)
        self.assertEqual(result["checkpoint"]["next_pair"], "FC015--FC125")
        check.check_tsv(c.queue_tsv(result), result)

    def test_queue_order_changed(self):
        self.d["queue"]["ordered_queue"][:2] = reversed(self.d["queue"]["ordered_queue"][:2]); self.reject()

    def test_queue_wrong_ordinal(self):
        self.d["queue"]["ordered_queue"][64]["ordinal"] = 66; self.reject()

    def test_selected_not_exact_prefix(self):
        self.d["queue"]["selected_pair_ids"][-1] = self.d["queue"]["remaining_pair_ids"][0]; self.reject()

    def test_queue_wrong_remainder(self):
        self.d["queue"]["remaining_pair_ids"].pop(); self.reject()

    def test_no_repeat_previous_direct_pair(self):
        key = self.d["queue"]["ordered_queue"][0]["pair_id"]
        next(r for r in self.d["baseline"]["core_pairs"] if r["pair_id"] == key)["reader_A"]["coverage"] = "DIRECT_PAIRED_SOURCE_COMPARISON"; self.reject()

    def test_missing_actual_pair(self):
        self.d["reader_A"]["coverage"]["actual_pair_ids_viewed"].pop(); self.reject()

    def test_duplicate_planned_coverage_not_actual(self):
        vals=self.d["reader_B"]["coverage"]["actual_pair_ids_viewed"];vals[-1]=vals[0];self.reject()

    def test_missing_target_fact(self):
        self.d["reader_B"]["target_observations"].pop();self.reject()

    def test_missing_actual_board(self):
        self.d["reader_A"]["coverage"]["actual_board_ids_viewed"].pop();self.reject()

    def test_missing_final_pair(self):
        self.d["final_review"]["pair_observations"].pop();self.reject()

    def test_wrong_target_context(self):
        self.fact()["source_context_ids"]=["unknown-context"];self.reject()

    def test_wrong_target_pointer(self):
        self.pair()["eight_paired_comparisons"]["terminal_pattern"]["left_target_feature_ref"]="/target_observations/2/eight_features/terminal_pattern";self.reject()

    def test_invalid_frame_sign(self):
        self.d["reader_A"]["target_observations"][0]["frame"]="EXACT90CCW";self.reject()

    def test_neighbor_witness_outside_context(self):
        self.fact()["native_locator_boxes"]=[[0,0,1,1]];self.reject()

    def test_outside_locator_with_continuity_is_allowed(self):
        ident=self.pair()["member_ids"][0];p=c.profiles(self.d)[ident];box=p["windows"]["CONTEXT"]["native_bbox_xyxy_halfopen"]
        self.fact()["native_locator_boxes"]=[[box[0],box[1],box[0]+1,box[1]+1]]
        self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_outside_locator_unknown_continuity_rejected(self):
        self.fact()["continuity_source_witness"]="UNKNOWN";self.reject()

    def test_witness_not_present_in_named_tight_view(self):
        ident=self.pair()["member_ids"][0];p=c.profiles(self.d)[ident];box=p["windows"]["CONTEXT"]["native_bbox_xyxy_halfopen"]
        self.fact()["native_locator_boxes"]=[[box[0],box[1],box[0]+1,box[1]+1]]
        self.fact()["source_context_ids"]=[p["windows"]["TIGHT"]["context_id"]];self.reject()

    def test_unknown_is_not_absence(self):
        self.fact().update(certainty="UNRESOLVED",absence_claim=True);self.reject()

    def test_unknown_is_not_supported_fact(self):
        self.fact()["observation"]="UNKNOWN";self.reject()

    def test_partial_eight_rejected(self):
        self.pair()["eight_paired_comparisons"].pop("enclosures");self.reject()

    def test_complete_repeat_all_three(self):
        self.repeat();self.assertEqual(self.build()["pairs"][0]["source_observation"],c.REPEAT)

    def test_repeat_unknown_feature_not_wildcard(self):
        self.repeat();self.fact()["certainty"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_repeat_preserves_significant_variation(self):
        self.repeat();self.pair("reader_B")["significant_variation"]=["Visible return extent differs"];self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_repeat_requires_complete_owned_route(self):
        self.repeat();self.d["reader_A"]["target_observations"][0]["binding_state"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_repeat_uncertain_endpoint_blocks(self):
        self.repeat();self.d["reader_B"]["target_observations"][0]["free_end_observations"][0]["ownership"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_visible_variation_is_difference_alternative_to_repeat(self):
        self.difference();r=self.build()["pairs"][0];self.assertEqual(r["source_observation"],c.DIFFERENCE);self.assertEqual(r["common_visible_difference_features"][0]["difference_kind"],"VISIBLE_FORM_VARIATION")

    def test_structural_feature_difference(self):
        self.difference("STRUCTURAL_FEATURE_DIFFERENCE");self.assertEqual(self.build()["pairs"][0]["source_observation"],c.DIFFERENCE)

    def test_difference_survives_unrelated_uncertainty(self):
        self.difference();self.fact("attached_bars")["certainty"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.DIFFERENCE)

    def test_difference_relevant_uncertainty_defers(self):
        self.difference();self.fact()["certainty"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_difference_relevant_ownership_defers(self):
        self.difference();self.fact()["ownership"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_difference_relevant_visibility_defers(self):
        self.difference();self.pair()["eight_paired_comparisons"]["terminal_pattern"]["relevant_visibility_left"]="UNRESOLVED";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_noncommon_difference_kind_defers(self):
        self.difference();self.pair("reader_B")["eight_paired_comparisons"]["terminal_pattern"]["difference_kind"]="STRUCTURAL_FEATURE_DIFFERENCE";self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_uncertain_overall_label_preserves_common_local_difference(self):
        self.difference();self.pair("reader_B")["candidate_outcome"]=c.UNCERTAIN
        row=self.build()["pairs"][0];self.assertEqual(row["source_observation"],c.DIFFERENCE)
        self.assertEqual(row["source_reports"]["reader_B"]["candidate_outcome"],c.UNCERTAIN)
        self.assertEqual(len(row["source_reports"]["reader_A"]["local_observed_differences"]),1)
        self.assertTrue(row["source_reports"]["reader_A"]["significant_variation"])

    def test_relevant_feature_disagreement_defers_preserving_local_fact(self):
        self.difference();self.pair("reader_B")["candidate_outcome"]=c.UNCERTAIN
        self.pair("reader_B")["eight_paired_comparisons"]["terminal_pattern"].update(relation="UNRESOLVED",difference_kind="NONE")
        row=self.build()["pairs"][0];self.assertEqual(row["source_observation"],c.UNCERTAIN)
        self.assertEqual(len(row["source_reports"]["reader_A"]["local_observed_differences"]),1)
        self.assertTrue(row["source_reports"]["reader_B"]["remaining_uncertainty"])

    def test_structured_source_summaries_preserved_without_coercion(self):
        variation={"dimension":"terminal_pattern","kind":"VISIBLE_FORM_VARIATION","observation":"Synthetic terminal direction differs"}
        issue={"dimension":"attached_bars","issue":"Synthetic exact bar contact remains unresolved"}
        self.pair("reader_B")["significant_variation"]=[variation]
        self.pair("reader_B")["remaining_uncertainty"]=[issue]
        summary=self.build()["pairs"][0]["source_reports"]["reader_B"]
        self.assertEqual(summary["significant_variation"],[variation])
        self.assertEqual(summary["remaining_uncertainty"],[issue])

    def test_structured_variation_wrong_dimension(self):
        self.pair()["significant_variation"]=[{"dimension":"invented_field","kind":"VISIBLE_FORM_VARIATION","observation":"Synthetic variation"}];self.reject()

    def test_structured_variation_wrong_kind(self):
        self.pair()["significant_variation"]=[{"dimension":"terminal_pattern","kind":"DIFFERENT_CIPHER","observation":"Synthetic variation"}];self.reject()

    def test_structured_variation_missing_observation(self):
        self.pair()["significant_variation"]=[{"dimension":"terminal_pattern","kind":"VISIBLE_FORM_VARIATION"}];self.reject()

    def test_structured_uncertainty_missing_issue(self):
        self.pair()["remaining_uncertainty"]=[{"dimension":"attached_bars"}];self.reject()

    def test_matching_category_votes_without_feature_do_not_release(self):
        for name in ("reader_A","reader_B","final_review"):self.pair(name)["candidate_outcome"]=c.DIFFERENCE
        self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_prose_inequality_without_visible_fact_not_difference(self):
        self.difference();self.pair()["eight_paired_comparisons"]["terminal_pattern"].update(relation="UNRESOLVED",difference_kind="NONE",paired_source_grounds="Descriptions have different words")
        self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_wrong_actual_board(self):
        self.pair()["actual_native_board_id"]="SYNTHETIC-BOARD-16";self.reject()

    def test_board_wrong_target_geometry(self):
        self.d["board_index"]["boards"][0]["panels"][0]["rotation_degrees_clockwise"]=0;self.reject()

    def test_initial_conditioning_disclosed_not_blind(self):
        self.repeat();self.d["reader_A"]["prior_exposure"]["other_initial_reader_report_seen"]=True;self.assertEqual(self.build()["pairs"][0]["source_observation"],c.UNCERTAIN)

    def test_final_blind_claim_rejected(self):
        self.d["final_review"]["conditioning"]["is_blind_agreement"]=True;self.reject()

    def test_final_requires_actual_grounds(self):
        self.pair("final_review")["adjudication_grounds"]="";self.reject()

    def test_final_chronology(self):
        self.d["final_review"]["frozen_utc"]="2026-10-14T03:00:00Z";self.reject()

    def test_source_proof_hex_and_attestation(self):
        self.d["reader_A"]["whole_private_proof_json_sha256"]="z"*64;self.reject()

    def test_proof_before_view_required(self):
        self.d["reader_B"]["proof_before_view"]=False;self.reject()

    def test_original_source_pin(self):
        self.d["final_review"]["original_source_pins"]["rgb_sha256"]="0"*64;self.reject()

    def test_final_input_report_pin(self):
        self.d["final_review"]["input_pins"]["reader_B_sha256"]="0"*64;self.reject()

    def test_uninspected_never_uncertain(self):
        r=self.build();r["pairs"][64]["source_observation"]=c.UNCERTAIN
        with self.assertRaises(ValueError):check.check(r,self.d,fixture=True)

    def test_checkpoint_resume_tamper(self):
        r=self.build();r["checkpoint"]["next_ordinal"]=66
        with self.assertRaises(ValueError):check.check(r,self.d,fixture=True)

    def test_no_transitive_or_graph_update(self):
        self.repeat();r=self.build();self.assertNotIn("current_graph",r);self.assertNotIn("graph",r);self.assertIn("REUSED_UNCHANGED",r["baseline_reuse"]["graph_and_307_sequence"])

    def test_tsv_tampered_row(self):
        r=self.build()
        with self.assertRaises(ValueError):check.check_tsv(c.queue_tsv(r).replace("NOT_INSPECTED","UNCERTAIN",1),r)

    def test_tsv_has_no_trailing_whitespace(self):
        text=c.queue_tsv(self.build())
        self.assertTrue(all(line == line.rstrip() for line in text.splitlines()))

    def test_tsv_empty_verdicts_roundtrip_and_checked_values_unchanged(self):
        self.difference();result=self.build()
        parsed=list(csv.DictReader(io.StringIO(c.queue_tsv(result).split("\n",1)[1]),delimiter="\t"))
        self.assertEqual(len(parsed),772)
        self.assertTrue(all(row["source_observation"] == "" and row["inspection_status"] == "NOT_INSPECTED" for row in parsed[64:]))
        for row,source in zip(parsed[:64],result["pairs"][:64]):
            self.assertEqual(row,{"ordinal":str(source["ordinal"]),"pair_id":source["pair_id"],"left_id":source["member_ids"][0],"right_id":source["member_ids"][1],"inspection_status":source["inspection_status"],"source_observation":source["source_observation"]})

    def test_synthetic_never_production_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"scientific.json"
            with self.assertRaises(ValueError):c.write_production(p,self.build(),{})
            self.assertFalse(p.exists())

    def test_arbitrary_final_hash_never_production(self):
        with self.assertRaises(ValueError):c.build(self.d)

    def test_source_output_alias_hardlink_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"source.json";p.write_text("frozen")
            protected={"source":(p,c.digest(p.read_bytes()))}
            link=Path(tmp)/"hard.json";os.link(p,link)
            sym=Path(tmp)/"sym.json";sym.symlink_to(p)
            for output in (p,link,sym):
                with self.assertRaises(ValueError):c.write_once(output,{},protected)
            self.assertEqual(p.read_text(),"frozen")

    def test_changed_input_detected_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"input";p.write_text("old");protected={"input":(p,c.digest(p.read_bytes()))};p.write_text("new")
            output=Path(tmp)/"out"
            with self.assertRaises(ValueError):c.write_once(output,{},protected)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
