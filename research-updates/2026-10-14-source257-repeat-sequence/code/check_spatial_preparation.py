#!/usr/bin/env python3
"""Check spatial preparation invariants; never accept scientific pair outcomes."""
import argparse
import itertools
import json
import re
from pathlib import Path

import spatial_preparation as core


def check(output, data):
    need = core.require
    need(output.get("schema") == "source257-spatial-preparation-v1" and output.get("purpose") == "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL", "Wrong preparation schema/purpose")
    expected_pins = {name: expected for name, (_, expected) in {**core.PINS, **core.LOCAL_PINS}.items()}
    need(output["input_sha256"] == expected_pins and output["source_encoded_sha256"] == core.SOURCE[1], "Output input pins mismatch")
    need(output["source_rgb_sha256_from_pinned_D9"] == data["D9"]["source"]["rgb_sha256"], "RGB metadata pin mismatch")
    need(output["source_pixel_handling"] == "ENCODED_BYTES_HASHED_NO_PIXEL_DECODE_OR_VIEW", "Unexpected source handling")
    need(output["counts"] == {"source_annotations": 307, "eligible_profiles": 70, "excluded_whole_profiles": 102, "unresolved_records": 135, "geometric_regions": 15}, "Wrong307/70/102/135 scope")
    need(output["counts_are"] == "ANNOTATION_RECORDS_NOT_GLYPHS_OR_ALPHABET", "Record counts promoted to glyph counts")
    need(output["global_reading_order"] == output["global_cipher_unit_count"] == output["cross_region_links"] == "UNKNOWN" and output["global_cipher_string"] is None, "Invented global reading/units/string")
    need(output["legacy_equivalence_labels"] == "UNTRUSTED_NOT_PROMOTED", "Legacy labels promoted")
    def walk(value):
        if isinstance(value, dict):
            need(not {"equivalence_class", "exemplar_role", "symbol_count", "token_length"} & set(value), "Forbidden legacy/count field")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str):
            need(re.fullmatch(r"S\d{3}", value) is None, "Legacy S label leaked")
    walk(output)
    units = {r["id"]: r for r in data["D9"]["frozen_first_band"]["units"] + data["D9"]["new_units"]}
    refs = {r["id"]: r for r in data["metadata"]["annotations"]}
    profiles = {r["id"]: r for r in data["profiles"]["profiles"]}
    excluded = set(data["profiles"]["outside_cohort_excluded_whole_ids"])
    unresolved = set(data["profiles"]["unchanged_unresolved_annotation_ids"])

    graph = output["graph"]
    need(graph["purpose"] == "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL" and graph["evidence_validation"] == "STRUCTURAL_REFERENCES_ONLY_CANONICAL_PAIR_GATES_PENDING", "Graph science status overclaimed")
    need(graph["node_ids"] == sorted(profiles) and graph["memberships_are_sets"] is True, "Wrong70 graph or forced partition")
    inherited = {e["pair_id"]: e for e in data["inherited"]["positive_edges"]}
    additions = [e for e in graph["positive_edges"] if e["origin"] != "INHERITED_11"]
    # This checks only reference structure, closure trigger shape and core membership.
    expected_graph = core.make_graph(data, {"schema": "source257-positive-edge-graph-input-v1", "purpose": "PREPARATION_ONLY", "new_positive_edges": additions})
    need(graph["positive_edges"] == expected_graph["positive_edges"], "Missing/changed inherited or malformed new graph edges")
    need(len(inherited) == 11 and graph["new_edge_count"] == len(additions), "Wrong inherited/new graph counts")
    edge_ids = {e["pair_id"] for e in graph["positive_edges"]}
    need(len(edge_ids) == len(graph["positive_edges"]), "Duplicate positive edge")
    cliques = graph["maximal_cliques"]
    need(len({c["id"] for c in cliques}) == len(cliques), "Duplicate clique IDs")
    for clique in cliques:
        members = clique["member_ids"]
        need(members == sorted(set(members)) and len(members) >= 2 and set(members) <= set(profiles), "Invalid clique members")
        witnesses = sorted("--".join(pair) for pair in itertools.combinations(members, 2))
        need(set(witnesses) <= edge_ids and clique["edge_witness_pair_ids"] == witnesses, "Transitive/non-clique group or incomplete witnesses")
        need(clique["id"] == "GSET-" + core.record_sha(members)[:16] and clique["membership_semantics"] == "SET_NOT_ALPHABET_PARTITION", "Graph label/partition semantics invalid")
    need(cliques == expected_graph["maximal_cliques"], "Maximal clique family missing/forced disjoint partition")
    need(graph["memberships"] == expected_graph["memberships"], "Overlapping graph membership sets lost")

    region_meta = {r["region"]: r for r in data["architecture"]["regions"]}
    regions = output["regions"]
    need(len(regions) == len(region_meta) == 15 and {r["region"] for r in regions} == set(region_meta), "Wrong15 region scope")
    seen = []
    for region in regions:
        name = region["region"]
        source = region_meta[name]
        records = region["records"]
        expected_ids = [r["id"] for r in source["spatial_order_annotation_refs"]]
        need([r["id"] for r in records] == expected_ids, "Wrong inherited display rank (source arrays/IDs are not order)")
        seen.extend(expected_ids)
        # Independent axis convention; no imposed direction for loose marks/red trace.
        axis = "EXACT_90CW_HORIZONTAL_DECREASING_NATIVE_Y" if name.startswith("right-") else "NATIVE_HORIZONTAL_INCREASING_X" if name == "frozen-first-band" or re.fullmatch(r"bottom-B\d+", name) else "NO_IMPOSED_AXIS"
        need(region["projection_axis"] == axis and region["tolerance_native_pixels"] == 8, "Wrong frame/sign/tolerance")
        need(region["precedence_rule"] == "STRICT_PROJECTED_GAP_GREATER_THAN_8" and region["projection_geometry_source"] == "IMMUTABLE_D9_BASE_SEARCH_RECTANGLES", "Wrong geometry source/rule")
        need(region["cross_region_links"] == region["linguistic_reading_direction"] == "UNKNOWN", "Invented reading links/direction")
        need(region["display_order_semantics"] == "INHERITED_ORDER_LOCAL_ORDER_DISPLAY_ONLY", "Display rank promoted to reading order")
        for rank, record in enumerate(records, 1):
            ident = record["id"]
            unit = units[ident]
            box = unit["native_bbox_xyxy_halfopen"]
            need(record["source_annotation_reference"] == refs[ident]["reference"] and record["source_record_canonical_sha256"] == refs[ident]["immutable_record_canonical_sha256"], "Source reference/hash changed")
            need(record["source_base_native_bbox_xyxy_halfopen"] == box and record["source_physical_extent_status"] == unit["physical_extent_status"], "Immutable source geometry/internal status changed")
            need(record["source_internal_partition"] == "UNMODIFIED_SOURCE_RECORD_REFERENCE", "Internal partition changed")
            order_key = "local_order" if name == "frozen-first-band" else "order"
            need(record["display_rank"] == rank and record["inherited_order_value"] == unit[order_key] and record["rank_semantics"] == "DISPLAY_ONLY_NOT_READING_OR_ADJACENCY", "Display rank/source order changed")
            label = "ELIGIBLE_PROFILE_REFERENCE" if ident in profiles else "UNKNOWN_FULL_FEATURE_LABEL" if ident in excluded else "UNKNOWN_INTERNAL_PARTITION"
            need(record["full_feature_label_status"] == label, "Wrong70/excluded/unresolved label")
            need(record["profile_reference"] == (profiles[ident]["profile_reference"] if ident in profiles else None), "Profile authority changed")
            need(record["sequence_length"] == "UNKNOWN_LENGTH", "Unknown span coarsened to fixed token length")
            need(all(record[k] == "UNKNOWN" for k in ("internal_cipher_unit_count", "cipher_unit_identity", "cipher_role", "letter_value")), "Cipher unit/role/letter inferred")
            expected_sidecar = None
            if ident in profiles and profiles[ident]["cohort"] == "D11_ACCEPTED15":
                expected_sidecar = {"native_bbox_xyxy_halfopen": profiles[ident]["target_locator_native_bbox_xyxy_halfopen"], "profile_reference": profiles[ident]["profile_reference"], "semantics": "APPROVED_D11_APPROXIMATE_3_TO_5_PIXEL_SEARCH_RECTANGLE_NOT_MASK_NOT_BASE_REPLACEMENT"}
            need(record["approved_target_locator_sidecar"] == expected_sidecar, "D11 sidecar lost/reinterpreted")
            members = graph["memberships"].get(ident, [])
            need(record["candidate_graph_membership_ids"] == members, "Source graph memberships lost")
            need(record["repeat_status"] == ("POSITIVE_GRAPH_MEMBERSHIPS_ONLY_CIPHER_EQUIVALENCE_UNKNOWN" if members else "UNKNOWN_REPEAT_EQUIVALENCE"), "Singleton declared distinct symbol")
            interval = [-box[3], -box[1]] if axis.startswith("EXACT_") else [box[0], box[2]] if axis.startswith("NATIVE_") else None
            need(record["projected_interval"] == interval, "Wrong projected interval/frame sign")
        pairs = region["pairwise_projected_relations"]
        expected_pairs = {tuple(pair) for pair in itertools.combinations(sorted(expected_ids), 2)}
        need(len(pairs) == len(expected_pairs) and {tuple(p["annotation_ids"]) for p in pairs} == expected_pairs, "Geometric pair accounting incomplete/duplicate")
        by_id = {r["id"]: r for r in records}
        for pair in pairs:
            left, right = (by_id[n]["projected_interval"] for n in pair["annotation_ids"])
            label, direction = "UNORDERED_NO_IMPOSED_AXIS", None
            if left is not None:
                if right[0] - left[1] > 8:
                    label, direction = "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING", "LEFT_BEFORE_RIGHT"
                elif left[0] - right[1] > 8:
                    label, direction = "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING", "RIGHT_BEFORE_LEFT"
                else:
                    label = "UNORDERED_PROJECTED_OVERLAP_OR_WITHIN_TOLERANCE"
            need(pair["relation"] == label and pair["direction"] == direction and pair["adjacency_claim"] is False, "Overlap/near boundary promoted to precedence/adjacency")
    need(len(seen) == len(set(seen)) == 307 and set(seen) == set(units), "Not exactly307 unique source references")
    expected_conflicts = [{"input": "D9", "json_pointer": f"/frozen_overlay_conflicts/{i}", "canonical_sha256": core.record_sha(c)} for i, c in enumerate(data["D9"]["frozen_overlay_conflicts"])]
    need(output["frozen_overlay_conflict_references"] == expected_conflicts, "Frozen conflict refs changed/omitted")
    expected_overlaps = set()
    for a, b in itertools.combinations(sorted(units), 2):
        aa, bb = units[a]["native_bbox_xyxy_halfopen"], units[b]["native_bbox_xyxy_halfopen"]
        if aa[0] < bb[2] and bb[0] < aa[2] and aa[1] < bb[3] and bb[1] < aa[3]:
            expected_overlaps.add((a, b))
    overlaps = output["search_rectangle_intersections"]
    need(len(overlaps) == len(expected_overlaps) and {tuple(o["annotation_ids"]) for o in overlaps} == expected_overlaps, "Intersection inventory changed")
    need(all(o["relation"] == "SEARCH_RECTANGLE_INTERSECTION_NOT_PROVEN_ALIAS" and o["cipher_double_count_claim"] == "UNKNOWN" and o["geometry_source"] == "IMMUTABLE_D9_BASE_SEARCH_RECTANGLES" for o in overlaps), "Rectangle overlap promoted to alias/double count")
    return {"schema": "source257-spatial-preparation-validation-v1", "status": "PASS_PREPARATION_ONLY", "annotation_refs": len(seen), "eligible_profiles": len(profiles), "excluded_unknown_profiles": len(excluded), "unresolved_unknown_length_records": len(unresolved), "geometric_regions": len(regions), "inherited_edges": 11, "structural_new_edges": len(additions), "graph_cliques": len(cliques), "graph_semantics": "SETS_ALLOW_OVERLAP_NOT_ALPHABET", "scientific_pair_gates": "PENDING_CANONICAL_PAIR_DATA"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--root", type=Path, default=core.DEFAULT_ROOT)
    parser.add_argument("--stage", type=Path, default=core.STAGE)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()
    data, protected = core.read_inputs(args.root, args.stage)
    need = core.require
    need(not args.input.is_symlink(), "Preparation input cannot be symlink")
    raw = args.input.read_bytes()
    protected["preparation_input"] = (args.input, core.sha(raw))
    result = check(json.loads(raw), data)
    core.verify_unchanged(protected)
    if args.report_output:
        core.write_once(args.report_output, result, protected)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
