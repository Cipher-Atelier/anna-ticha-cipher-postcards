#!/usr/bin/env python3
"""Portable source257 spatial preparation. No image decoding or pair adjudication.

Optional graph input is structural preparation only, not scientific acceptance:
{schema: source257-positive-edge-graph-input-v1,
 purpose: PREPARATION_ONLY, new_positive_edges: [
 {member_ids: [A,B], origin: CORE_930|PRELOGGED_OLD_OLD_CLOSURE,
  evidence_reference: {path: ..., sha256: ..., json_pointer: ...},
  closure_prelog_reference: {...}, triggering_new_member: ..., proposed_member_ids: [...]}]}
Closure-only keys are mandatory for old-old additions. Actual paired eight-feature,
two-reader/final-AI gates must be checked by the later canonical evidence validator.
"""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = STAGE.parent
PINS = {
    "D9": ("source257-fullcard-annotation-next-20261013/results/fullcard-map-v2.json", "f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34"),
    "D10": ("source257-class-candidates-next-20261013/results/candidate-inventory-v1.json", "a2f13278119c6437821a416e1cf56483e7d3d879a48e3adaa363023c314b87a0"),
    "D11": ("source257-exclusion-refinement-next-20261013/results/context-refinement-delta-v2.json", "9bc9f35a2427dc2fad36bdff3cae8ca7d7ae4fb5c74844a46885f4c5fc8926a4"),
}
LOCAL_PINS = {
    "profiles": ("effective70-profile-references-v1.json", "b5d588bbeb4e0210d4f3cd0cc3bea45cd7d77a88bdad9fe5037fc979d15e81bf"),
    "metadata": ("input-pins-metadata-v1.json", "50d3ed50aa6a10233ce081c6bf575c7e5f11ea73fe35a0debe9df1685ce584dc"),
    "architecture": ("metadata-inventory-and-architecture-v1.json", "97dd365f39757c691f68e52f2585a6d187ffcb53550c01567cb5904f5ba191d4"),
    "inherited": ("inherited-candidate-sets-v1.json", "4bd2aa9a9589a5698d80abb07e19e53e0f0ec4a983ea0cfda4003ff8dd063139"),
    "core_pairs": ("pair-coverage-deferred-v1.json", "298caa5929a2432f369d8cce01f4cc320076d8cdea3140df6454887f5568465e"),
    "protocol": ("comparison-protocol-v1.json", "e0d0f9563e29af6463621f168b2d0797025b41d6fcb5d5e005063b098697691a"),
    "scope_addendum": ("scope-handling-addendum-v1.json", "f178d453c17930cbeed20aedeb95f70567b3c7d16708ec4ebfd555109985e647"),
    "method_gate": ("methods-protocol-gate-private-v2.json", "6678176673747857d9da60fb8552e8659282d6b24653ebfe7e74d9195fb48ae5"),
}
SOURCE = ("rebuild257258-run-20261013/source257/pc_hcp_257_pic.JPG", "7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def record_sha(record):
    return sha(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode())


def read_inputs(root=DEFAULT_ROOT, stage=STAGE):
    paths = {name: (root / rel, expected) for name, (rel, expected) in PINS.items()}
    paths.update({name: (stage / "results" / rel, expected) for name, (rel, expected) in LOCAL_PINS.items()})
    paths["source_encoded"] = (root / SOURCE[0], SOURCE[1])
    data = {}
    for name, (path, expected) in paths.items():
        raw = path.read_bytes()
        require(sha(raw) == expected, f"Immutable byte pin mismatch: {name}")
        if name != "source_encoded":
            data[name] = json.loads(raw)
    refs = {r["id"]: r for r in data["metadata"]["annotations"]}
    units = {r["id"]: r for r in data["D9"]["frozen_first_band"]["units"] + data["D9"]["new_units"]}
    require(len(units) == len(refs) == 307 and set(units) == set(refs), "307 reference universe mismatch")
    for ident, unit in units.items():
        require(record_sha(unit) == refs[ident]["immutable_record_canonical_sha256"], f"Immutable annotation mismatch: {ident}")
    return data, paths


def verify_unchanged(paths):
    for name, (path, expected) in paths.items():
        require(sha(path.read_bytes()) == expected, f"Input changed during operation: {name}")


def safe_output_path(output, protected):
    output = Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), "Output must not exist (including input aliases/hardlinks/symlinks)")
    require(output.parent.exists(), "Output parent must already exist")
    require(output == output.resolve(), "Output path must not traverse a symlink")
    require(output.resolve() not in {p.resolve() for p, _ in protected.values()}, "Output aliases protected input")
    return output


def write_once(output, value, protected):
    output = safe_output_path(output, protected)
    verify_unchanged(protected)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(output), flags, 0o644)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        verify_unchanged(protected)
    except BaseException:
        # A failed post-write immutable check must not leave an apparently valid output.
        output.unlink(missing_ok=True)
        raise


def pair_key(ids):
    require(len(ids) == 2 and len(set(ids)) == 2 and list(ids) == sorted(ids), "Pair must contain two canonically sorted distinct IDs")
    return "--".join(ids)


def evidence_reference(ref):
    require(isinstance(ref, dict) and set(ref) == {"path", "sha256", "json_pointer"}, "Evidence reference shape invalid")
    require(isinstance(ref["path"], str) and bool(ref["path"]), "Evidence path missing")
    require(isinstance(ref["json_pointer"], str) and ref["json_pointer"].startswith("/"), "Evidence pointer missing")
    require(isinstance(ref["sha256"], str) and len(ref["sha256"]) == 64 and all(c in "0123456789abcdef" for c in ref["sha256"]), "Evidence hash invalid")


def maximal_cliques(nodes, pairs):
    adjacency = {n: set() for n in nodes}
    for left, right in pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    found = []
    def visit(current, possible, excluded):
        if not possible and not excluded:
            if len(current) >= 2:
                found.append(tuple(sorted(current)))
            return
        pivot = max(possible | excluded, key=lambda n: len(possible & adjacency[n]), default=None)
        choices = possible - adjacency[pivot] if pivot else possible.copy()
        for node in sorted(choices):
            visit(current | {node}, possible & adjacency[node], excluded & adjacency[node])
            possible.remove(node)
            excluded.add(node)
    visit(set(), set(nodes), set())
    return sorted(found)


def make_graph(data, graph_input=None):
    eligible = {r["id"] for r in data["profiles"]["profiles"]}
    new = set(data["protocol"]["newly_recovered_ids"])
    inherited = data["inherited"]["positive_edges"]
    edges = [{"pair_id": e["pair_id"], "member_ids": e["member_ids"], "origin": "INHERITED_11", "evidence_reference": e["authority_reference"]} for e in inherited]
    extra = graph_input or {"schema": "source257-positive-edge-graph-input-v1", "purpose": "PREPARATION_ONLY", "new_positive_edges": []}
    require(extra.get("schema") == "source257-positive-edge-graph-input-v1" and extra.get("purpose") == "PREPARATION_ONLY", "Graph input must be explicit structural preparation")
    seen = {e["pair_id"] for e in edges}
    core = {p["pair_id"] for p in data["core_pairs"]["pairs"]}
    for edge in extra["new_positive_edges"]:
        key = pair_key(edge["member_ids"])
        require(set(edge["member_ids"]) <= eligible and key not in seen, "Unknown or duplicate graph edge")
        evidence_reference(edge["evidence_reference"])
        if edge["origin"] == "CORE_930":
            require(key in core, "Core edge outside mandatory 930")
        else:
            require(edge["origin"] == "PRELOGGED_OLD_OLD_CLOSURE", "Unsupported graph origin")
            require(not set(edge["member_ids"]) & new, "Closure edge must be old-old")
            evidence_reference(edge["closure_prelog_reference"])
            proposed = edge["proposed_member_ids"]
            require(len(proposed) == len(set(proposed)) and set(proposed) <= eligible, "Closure proposed set invalid")
            require(set(edge["member_ids"]) <= set(proposed) and edge["triggering_new_member"] in set(proposed) & new, "Closure lacks new-member trigger")
        edges.append({**edge, "pair_id": key})
        seen.add(key)
    for edge in edges:
        if edge["origin"] == "PRELOGGED_OLD_OLD_CLOSURE":
            require(all("--".join(sorted([edge["triggering_new_member"], ident])) in seen for ident in edge["member_ids"]), "Closure trigger lacks existing new-member edge witnesses")
    edges.sort(key=lambda e: e["pair_id"])
    cliques = []
    for members in maximal_cliques(eligible, [e["member_ids"] for e in edges]):
        cliques.append({"id": "GSET-" + record_sha(list(members))[:16], "member_ids": list(members), "membership_semantics": "SET_NOT_ALPHABET_PARTITION", "edge_witness_pair_ids": sorted("--".join(p) for p in itertools.combinations(members, 2))})
    memberships = {ident: sorted(c["id"] for c in cliques if ident in c["member_ids"]) for ident in sorted(eligible)}
    return {"schema": "source257-positive-graph-preparation-v1", "purpose": "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL", "evidence_validation": "STRUCTURAL_REFERENCES_ONLY_CANONICAL_PAIR_GATES_PENDING", "node_ids": sorted(eligible), "positive_edges": edges, "maximal_cliques": cliques, "memberships_are_sets": True, "memberships": memberships, "new_edge_count": len(edges) - 11}


def axis_for(region):
    if region.startswith("right-"):
        return "EXACT_90CW_HORIZONTAL_DECREASING_NATIVE_Y"
    if region == "frozen-first-band" or (region.startswith("bottom-B") and region[8:].isdigit()):
        return "NATIVE_HORIZONTAL_INCREASING_X"
    return "NO_IMPOSED_AXIS"


def projected_interval(box, axis):
    if axis == "EXACT_90CW_HORIZONTAL_DECREASING_NATIVE_Y":
        return [-box[3], -box[1]]
    if axis == "NATIVE_HORIZONTAL_INCREASING_X":
        return [box[0], box[2]]
    return None


def relation(left, right, axis):
    first, second = projected_interval(left, axis), projected_interval(right, axis)
    if first is None:
        return "UNORDERED_NO_IMPOSED_AXIS", None
    if first[1] + 8 < second[0]:
        return "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING", "LEFT_BEFORE_RIGHT"
    if second[1] + 8 < first[0]:
        return "ANNOTATION_WINDOW_PROJECTED_ORDER_NOT_READING", "RIGHT_BEFORE_LEFT"
    return "UNORDERED_PROJECTED_OVERLAP_OR_WITHIN_TOLERANCE", None


def intersects(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def assemble(data, graph_input=None):
    units = {r["id"]: r for r in data["D9"]["frozen_first_band"]["units"] + data["D9"]["new_units"]}
    refs = {r["id"]: r for r in data["metadata"]["annotations"]}
    profiles = {r["id"]: r for r in data["profiles"]["profiles"]}
    excluded = set(data["profiles"]["outside_cohort_excluded_whole_ids"])
    unresolved = set(data["profiles"]["unchanged_unresolved_annotation_ids"])
    require((len(profiles), len(excluded), len(unresolved)) == (70, 102, 135), "Wrong core70/102/135 scope")
    require(set(profiles) == set(data["protocol"]["eligible_ids"]), "Wrong frozen70 eligible IDs")
    require(set(profiles) | excluded | unresolved == set(units) and not (set(profiles) & excluded or excluded & unresolved or unresolved & set(profiles)), "Invalid core source partition")
    graph = make_graph(data, graph_input)
    regions = []
    for inherited_region in data["architecture"]["regions"]:
        name = inherited_region["region"]
        axis = axis_for(name)
        records = []
        for rank, entry in enumerate(inherited_region["spatial_order_annotation_refs"], 1):
            ident = entry["id"]
            unit = units[ident]
            membership = graph["memberships"].get(ident, [])
            records.append({
                "id": ident, "source_annotation_reference": refs[ident]["reference"],
                "source_record_canonical_sha256": refs[ident]["immutable_record_canonical_sha256"],
                "source_base_native_bbox_xyxy_halfopen": unit["native_bbox_xyxy_halfopen"],
                "source_physical_extent_status": unit["physical_extent_status"],
                "source_internal_partition": "UNMODIFIED_SOURCE_RECORD_REFERENCE",
                "display_rank": rank, "inherited_order_value": entry["order"], "rank_semantics": "DISPLAY_ONLY_NOT_READING_OR_ADJACENCY",
                "full_feature_label_status": "ELIGIBLE_PROFILE_REFERENCE" if ident in profiles else "UNKNOWN_FULL_FEATURE_LABEL" if ident in excluded else "UNKNOWN_INTERNAL_PARTITION",
                "profile_reference": profiles[ident]["profile_reference"] if ident in profiles else None,
                "approved_target_locator_sidecar": {"native_bbox_xyxy_halfopen": profiles[ident]["target_locator_native_bbox_xyxy_halfopen"], "profile_reference": profiles[ident]["profile_reference"], "semantics": "APPROVED_D11_APPROXIMATE_3_TO_5_PIXEL_SEARCH_RECTANGLE_NOT_MASK_NOT_BASE_REPLACEMENT"} if ident in profiles and profiles[ident]["cohort"] == "D11_ACCEPTED15" else None,
                "sequence_length": "UNKNOWN_LENGTH", "internal_cipher_unit_count": "UNKNOWN", "cipher_unit_identity": "UNKNOWN", "cipher_role": "UNKNOWN", "letter_value": "UNKNOWN",
                "repeat_status": "POSITIVE_GRAPH_MEMBERSHIPS_ONLY_CIPHER_EQUIVALENCE_UNKNOWN" if membership else "UNKNOWN_REPEAT_EQUIVALENCE",
                "candidate_graph_membership_ids": membership,
                "projected_interval": projected_interval(unit["native_bbox_xyxy_halfopen"], axis),
            })
        pair_relations = []
        for a, b in itertools.combinations(sorted(records, key=lambda r: r["id"]), 2):
            label, direction = relation(a["source_base_native_bbox_xyxy_halfopen"], b["source_base_native_bbox_xyxy_halfopen"], axis)
            pair_relations.append({"annotation_ids": [a["id"], b["id"]], "relation": label, "direction": direction, "adjacency_claim": False})
        regions.append({"region": name, "projection_axis": axis, "projection_geometry_source": "IMMUTABLE_D9_BASE_SEARCH_RECTANGLES", "tolerance_native_pixels": 8, "precedence_rule": "STRICT_PROJECTED_GAP_GREATER_THAN_8", "display_order_semantics": "INHERITED_ORDER_LOCAL_ORDER_DISPLAY_ONLY", "linguistic_reading_direction": "UNKNOWN", "cross_region_links": "UNKNOWN", "records": records, "pairwise_projected_relations": pair_relations})
    all_ids = sorted(units)
    overlaps = [{"annotation_ids": [a, b], "relation": "SEARCH_RECTANGLE_INTERSECTION_NOT_PROVEN_ALIAS", "geometry_source": "IMMUTABLE_D9_BASE_SEARCH_RECTANGLES", "cipher_double_count_claim": "UNKNOWN"} for a, b in itertools.combinations(all_ids, 2) if intersects(units[a]["native_bbox_xyxy_halfopen"], units[b]["native_bbox_xyxy_halfopen"])]
    return {
        "schema": "source257-spatial-preparation-v1", "purpose": "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL",
        "input_sha256": {name: expected for name, (_, expected) in {**PINS, **LOCAL_PINS}.items()}, "source_encoded_sha256": SOURCE[1],
        "source_rgb_sha256_from_pinned_D9": data["D9"]["source"]["rgb_sha256"], "source_pixel_handling": "ENCODED_BYTES_HASHED_NO_PIXEL_DECODE_OR_VIEW",
        "counts_are": "ANNOTATION_RECORDS_NOT_GLYPHS_OR_ALPHABET", "counts": {"source_annotations": 307, "eligible_profiles": 70, "excluded_whole_profiles": 102, "unresolved_records": 135, "geometric_regions": 15},
        "global_reading_order": "UNKNOWN", "global_cipher_string": None, "global_cipher_unit_count": "UNKNOWN", "cross_region_links": "UNKNOWN", "legacy_equivalence_labels": "UNTRUSTED_NOT_PROMOTED",
        "regions": regions, "graph": graph,
        "frozen_overlay_conflict_references": [{"input": "D9", "json_pointer": f"/frozen_overlay_conflicts/{i}", "canonical_sha256": record_sha(item)} for i, item in enumerate(data["D9"]["frozen_overlay_conflicts"])],
        "search_rectangle_intersections": overlaps,
        "limitations": ["No new pair outcomes inferred from profile text.", "Optional graph input validates structure and clique witnesses only; actual source evidence acceptance remains pending canonical paired-reader data.", "The8native-pixel margin combines two base-window approximations of plus/minus4; disjoint projections prove annotation-window order only, never physical whole-route boundaries, adjacency or reading order.", "D11 target sidecars are approximate3to5native-pixel search locators, not masks; they are excluded from the8pixel base-window geometry rule.", "Rectangles are approximate search windows, not ink masks; geometric relations establish neither adjacency nor linguistic order.", "Unknown record lengths and cipher-unit counts do not supply a token count or alphabet size."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--stage", type=Path, default=STAGE)
    parser.add_argument("--graph-input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data, protected = read_inputs(args.root, args.stage)
    graph = None
    if args.graph_input:
        raw = args.graph_input.read_bytes()
        protected["optional_graph_input"] = (args.graph_input, sha(raw))
        graph = json.loads(raw)
    safe_output_path(args.output, protected)
    output = assemble(data, graph)
    write_once(args.output, output, protected)
    print(json.dumps({"status": "PREPARATION_WRITTEN", "annotation_refs": 307, "new_graph_edges": output["graph"]["new_edge_count"], "output_sha256": sha(args.output.read_bytes())}))


if __name__ == "__main__":
    main()
