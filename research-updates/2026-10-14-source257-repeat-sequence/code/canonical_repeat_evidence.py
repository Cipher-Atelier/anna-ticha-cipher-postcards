#!/usr/bin/env python3
"""Canonical source257 evidence gates. JSON only; no default JPEG or pixel I/O.

Frozen original reader files remain authoritative. Publication path/hash selection
must be an explicit separately reviewed adapter, never an unchecked hash bypass.
No final output is written without real separately pinned final-AI review inputs.
"""
import argparse
import copy
import csv
import datetime as dt
import io
import itertools
import json
import os
from collections import Counter
from pathlib import Path

import spatial_preparation as spatial

need = spatial.require
SAME = "SAME_FULL_VISIBLE_FEATURE_CANDIDATE"
ACCEPT = "ACCEPT_FULL_VISIBLE_FEATURE_CANDIDATE"
DEFER = "DEFER_FEATURE_OR_BINDING"
ACCEPTED = "ACCEPTED_SAME_FULL_VISIBLE_FEATURE_CANDIDATE"
FIELDS = ("path_topology", "enclosures", "openings", "stem_pattern", "attached_bars", "connected_extra_strokes", "terminal_pattern", "owned_mark_profile")
RAW_PINS = {
    "reader_A": ("repeat-reader-A-v1.json", "1ee9e7f155562098018fbf7b471c8a83713b1216ddef5a8b78f057eb396f586d"),
    "reader_B": ("repeat-reader-B-v1.json", "57c34ca20119a8de119fef941f5d3be18e9d7185f0f7c5060e485b41d93160b2"),
    "confirmation_B": ("repeat-reader-B-paired-confirmation-addendum-v1.json", "1a1827cff72705dcbe683799619c2e700fc7a451deb84af497144810eeaddf06"),
    "closure_prelog": ("targeted-closure-prelog-v1.json", "cba6e8bd6da5f3cb779181e9c5e1636c27790ad1047126d17df55e3de2c55229"),
    "closure_A": ("repeat-reader-A-closure-v1.json", "ef374c4da855a2097cc47d63f73faee36be8b12bf87540d6c2b4c65c97231e2b"),
    "closure_B": ("repeat-reader-B-closure-v1.json", "8f4c78dba4cbb06b3b5159554c39f0c23601166820819a0d29be61b1deae03c2"),
}
CONTEXT_PIN = ("comparison-context-pack-v1/context-index.json", "76f81e4db718f3d9bfcf991e9c233d52e961a2dedc7163c4acc22c79abbf1333")
FINAL_REVIEW_PINS = {
    "final_core": ("repeat-final-ai-review-v2.json", "25dae066532e513ffc25d9f9db838915f5836177241d610aafbdcd00e661d8dd"),
    "final_closure": ("repeat-closure-final-ai-review-v2.json", "1ce734f238a5e9dd88db22205fea108cc53c7f19f4cc10d7bfd2cf5f8e37072e"),
}


def load(root=spatial.DEFAULT_ROOT, stage=spatial.STAGE):
    """Load pinned JSON only. Encoded/RGB source hashes remain metadata pins."""
    data, protected = {}, {}
    paths = {n: (root / p, h) for n, (p, h) in spatial.PINS.items()}
    paths.update({n: (stage / "results" / p, h) for n, (p, h) in {**spatial.LOCAL_PINS, **RAW_PINS}.items()})
    paths["context_index"] = (stage / CONTEXT_PIN[0], CONTEXT_PIN[1])
    for name, (path, expected) in paths.items():
        raw = path.read_bytes()
        need(spatial.sha(raw) == expected, f"Canonical immutable pin mismatch: {name}")
        data[name], protected[name] = json.loads(raw), (path, expected)
    refs = {r["id"]: r for r in data["metadata"]["annotations"]}
    units = data["D9"]["frozen_first_band"]["units"] + data["D9"]["new_units"]
    need(len(units) == len(refs) == 307, "Immutable307 scope mismatch")
    for record in units:
        need(spatial.record_sha(record) == refs[record["id"]]["immutable_record_canonical_sha256"], "Immutable source record changed")
    data["_hashes"] = {name: expected for name, (_, expected) in protected.items()}
    data["_paths"] = {name: str(path.relative_to(root)) if path.is_relative_to(root) else path.name for name, (path, _) in protected.items()}
    return data, protected


def attach_review(data, protected, name, path, expected_sha256):
    need(name in {"final_core", "final_closure"}, "Unknown review input")
    need(expected_sha256 == FINAL_REVIEW_PINS[name][1], "Final review must match this version's frozen scientific review pin")
    raw = path.read_bytes()
    need(spatial.sha(raw) == expected_sha256, f"Final review pin mismatch: {name}")
    need(not path.is_symlink() and path.resolve().parent == protected["reader_A"][0].resolve().parent, "Final reviews must be explicit real files beside the pinned selected reader inputs")
    data[name] = json.loads(raw)
    data["_hashes"][name] = expected_sha256
    data["_paths"][name] = (Path(data["_paths"]["reader_A"]).parent / path.name).as_posix()
    protected[name] = (path, expected_sha256)
    if "_public_bindings" in data:
        data["_public_bindings"]["inputs"][name] = {"path": data["_paths"][name], "original_whole_file_sha256": expected_sha256, "selected_whole_file_sha256": expected_sha256, "filter_identity": "BYTE_IDENTICAL", "binding_authority": "FROZEN_FINAL_REVIEW_PINS_IN_CODE"}


def ref(data, name, pointer):
    return {"input": name, "sha256": data["_hashes"][name], "json_pointer": pointer}


def resolve(data, reference):
    need(reference["sha256"] == data["_hashes"][reference["input"]], "Raw reference SHA mismatch")
    value = data[reference["input"]]
    for part in reference["json_pointer"].strip("/").split("/"):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def indexed(rows, expected, label):
    need(isinstance(rows, list), f"{label} rows not a list")
    result = {}
    for index, row in enumerate(rows):
        key = spatial.pair_key(row["member_ids"])
        need(key == row["pair_id"] and key not in result, f"{label} duplicate/reversed/incorrect pair ID")
        result[key] = (index, row)
    need(set(result) == set(expected), f"{label} exact pair universe mismatch")
    return result


def concrete(text):
    need(isinstance(text, str) and bool(text.strip()), "Missing concrete observation")
    normalized = text.strip().upper()
    need(normalized not in {"UNKNOWN", "UNRESOLVED", "N/A", "SAME", "*", "?", "NONE"}, "Wildcard observation cannot support positive")
    need(not normalized.startswith(("UNKNOWN ", "UNRESOLVED ", "UNCERTAIN ", "NOT OBSERVED")), "Unresolved observation cannot support positive")


def bbox(box, size):
    need(isinstance(box, list) and len(box) == 4 and all(type(n) is int for n in box), "Native locator must be four integer coordinates")
    x0, y0, x1, y1 = box
    need(0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1], "Native locator invalid or outside source")


def views(refs, data=None, member_ids=None, require_complete=False):
    need(isinstance(refs, list) and bool(refs), "Missing source view references")
    need(all(isinstance(v, (str, dict)) and bool(v) for v in refs), "Empty source view reference")
    if data is None:
        return
    known = {c["context_id"]: c for c in data["context_index"]["contexts"]}
    seen = set()
    for reference in refs:
        context_id = reference if isinstance(reference, str) else reference.get("context_id")
        need(context_id in known, "Unknown source context reference")
        context = known[context_id]
        if isinstance(reference, dict):
            for key in ("native_bbox_xyxy_halfopen", "native_crop_bbox", "native_bbox"):
                if key in reference:
                    need(reference[key] == context["native_bbox_xyxy_halfopen"], "View coordinates differ from pinned context index")
            for key in ("rotation_degrees_clockwise", "frame_degrees_clockwise"):
                if key in reference:
                    need(reference[key] == context["rotation_degrees_clockwise"], "View rotation differs from pinned context index")
        if member_ids is not None:
            need(set(context["target_ids"]) & set(member_ids), "Wrong-target context supplied as evidence")
            for ident in member_ids:
                for kind, view in context_views(data, ident).items():
                    if view["context_id"] == context_id:
                        seen.add((ident, kind))
    if require_complete:
        need(seen == {(ident, kind) for ident in member_ids for kind in ("TIGHT", "CONTEXT")}, "FinalAI views must cover actual TIGHT+CONTEXT for both target IDs")


def context_views(data, ident):
    return data["reader_B"]["observation_dictionary"][ident]["source_view_refs"]


def local_witness(data, ident, box):
    bbox(box, data["D9"]["source"]["size"])
    crops = [v["native_crop_bbox"] for v in context_views(data, ident).values()]
    need(any(c[0] <= box[0] < box[2] <= c[2] and c[1] <= box[1] < box[3] <= c[3] for c in crops), "Locator is unrelated to target source context")
    profile = next(p for p in data["profiles"]["profiles"] if p["id"] == ident)
    target = profile["target_locator_native_bbox_xyxy_halfopen"]
    # Exact window intersection is a necessary mechanical locality check only.
    # Physical-route binding remains the source readers' and final AI's judgment.
    need(spatial.intersects(box, target), "Witness lies on neighboring context rather than approved target search box")


def validate_source_observations(data):
    eligible = {p["id"]: p for p in data["profiles"]["profiles"]}
    aa = data["reader_A"]["source_observations"]
    bb = data["reader_B"]["observation_dictionary"]
    need(len(aa) == len({x["id"] for x in aa}) == 70 and {x["id"] for x in aa} == set(bb) == set(eligible), "Reader observation scope is not exact70")
    contexts = {c["context_id"]: c for c in data["context_index"]["contexts"]}
    need(len(contexts) == len(data["context_index"]["contexts"]) and set(data["context_index"]["selected_ids"]) == set(eligible), "Pinned context-index target universe mismatch")
    for observation in aa:
        ident = observation["id"]
        need(observation["observation_id"] == "A-" + ident and observation["native_target_search_bbox_xyxy_halfopen"] == eligible[ident]["target_locator_native_bbox_xyxy_halfopen"], "ReaderA target-route authority mismatch")
        need(set(observation["features"]) == set(FIELDS), "ReaderA feature inventory incomplete")
        need(set(observation["view_references"]) == {"TIGHT", "CONTEXT"}, "ReaderA tight/context coverage missing")
        for feature in FIELDS:
            concrete(observation["features"][feature])
        for kind, view in observation["view_references"].items():
            bbox(view["native_bbox_xyxy_halfopen"], data["D9"]["source"]["size"])
            need(view["context_id"] == bb[ident]["source_view_refs"][kind]["context_id"], "Reader source context IDs disagree")
            context = contexts[view["context_id"]]
            need(context["target_ids"] == [ident] and context["native_bbox_xyxy_halfopen"] == view["native_bbox_xyxy_halfopen"] and context["rotation_degrees_clockwise"] == observation["frame_degrees_clockwise"], "A context target/nativecoords/frame differs from pinned index")
            need(any(t["id"] == ident and t["native_bbox_xyxy_halfopen"] == eligible[ident]["base_native_bbox_xyxy_halfopen"] for t in context["targets"]), "Context target metadata differs from immutable base annotation")
    for ident, observation in bb.items():
        need(observation["id"] == ident and observation["certified_target_route"] == eligible[ident]["target_locator_native_bbox_xyxy_halfopen"], "ReaderB target-route authority mismatch")
        need(set(observation["eight_feature_observations"]) == set(FIELDS), "ReaderB feature inventory incomplete")
        for kind, view in observation["source_view_refs"].items():
            context = contexts[view["context_id"]]
            need(context["target_ids"] == [ident] and view["native_crop_bbox"] == context["native_bbox_xyxy_halfopen"], "B context target/nativecoords differs from pinned index")
            need(observation["frame"] in ({"EXACT90CW"} if context["rotation_degrees_clockwise"] == 90 else {"NATIVE", "NATIVE0"}), "B frame differs from pinned source rotation")
        for feature in FIELDS:
            witness = observation["eight_feature_observations"][feature]
            concrete(witness["observation"])
            local_witness(data, ident, witness["native_locator_bbox_xyxy_halfopen"])
            views(witness["view_refs"], data, [ident])
            need(set(witness["view_refs"]) == {v["context_id"] for v in observation["source_view_refs"].values()}, "ReaderB feature view refs mismatch")
    return {o["id"]: (i, o) for i, o in enumerate(aa)}


def raw_core(data):
    scope = {p["pair_id"] for p in data["core_pairs"]["pairs"]}
    need(len(scope) == 930, "Mandatory930 scope mismatch")
    a = indexed(data["reader_A"]["pairs"], scope, "ReaderA core")
    b = indexed(data["reader_B"]["pairs"], scope, "ReaderB core")
    both = {k for k in scope if a[k][1]["status"] == b[k][1]["status"] == SAME}
    confirmation = data["confirmation_B"]
    need(confirmation["initial_artifact_sha256"] == data["_hashes"]["reader_B"] and confirmation["initial_artifact_unchanged"] is True and confirmation["all_eight_dimensions_compared_per_pair"] is True, "B confirmation authority invalid")
    confirmations = {}
    for i, row in enumerate(confirmation["confirmations"]):
        key = row["pair_id"]
        need(key not in confirmations, "Duplicate B confirmation")
        confirmations[key] = (i, row)
    bpositive = {k for k in scope if b[k][1]["status"] == SAME}
    need(set(confirmations) == bpositive and len(confirmations) == confirmation["actual_side_by_side_pair_count"] == len(bpositive), "B direct confirmation universe mismatch")
    for key, (_, row) in confirmations.items():
        need(row["outcome"] == "CONFIRMED_INITIAL_GRAPHICAL_CANDIDATE_EDGE" and set(row["eight_feature_recheck"]) == set(FIELDS), "B positive recheck missing")
        panels = row["actual_direct_pair_view"]["panels"]
        need(len(panels) == 4 and {(p["id"], p["kind"]) for p in panels} == {(n, t) for n in b[key][1]["member_ids"] for t in ("TIGHT", "CONTEXT")}, "B actual paired panels incomplete")
        need(all(p["source_panel_equal"] is True and p["pair_id"] == key for p in panels), "B paired source equality attestation missing")
        need(all(p["source_context_id"] == context_views(data, p["id"])[p["kind"]]["context_id"] for p in panels), "B actual paired panel context bound to wrong target")
    return scope, a, b, both, confirmations


def validate_core_positive(data, key, a, b, confirmations, observations):
    _, ar = a[key]
    _, br = b[key]
    need(ar["status"] == br["status"] == SAME, "Both reader positive gates required")
    need(ar["source_coverage"] == br["coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON", "Positive edge lacks direct paired coverage")
    aa = ar["evidence"]["eight_feature_comparisons"]
    bb = br["eight_feature_comparison"]
    bc = confirmations[key][1]["eight_feature_recheck"]
    need(set(aa) == set(bb) == set(bc) == set(FIELDS), "Positive reader gate does not cover all8")
    left, right = ar["member_ids"]
    need(ar["source_observations"] == ["A-" + left, "A-" + right] and br["observation_refs"] == [left, right], "Pair observation binding mismatch")
    views(ar["evidence"]["complete_contexts"], data, [left, right])
    need(bool(ar["evidence"]["paired_view"]), "A paired source view missing")
    for field in FIELDS:
        need(aa[field]["relation"] == "SUPPORTED_IN_PAIRED_SOURCE", "A positive field relation unsupported")
        for side, ident in (("left", left), ("right", right)):
            need(aa[field][side + "_source_observation"] == observations[ident][1]["features"][field], "A paired observation differs from raw source witness")
            concrete(aa[field][side + "_source_observation"])
            expected = f"{ident}/eight_feature_observations/{field}"
            need(bb[field][side + "_observation_ref"] == bc[field][side + "_observation_ref"] == expected, "B field observation reference misbound")
        need(bb[field]["relation"] == bc[field]["relation"] == "SUPPORTED_SAME_VISIBLE_RELATION", "B positive field/recheck relation unsupported")


def parse_time(value):
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(result.tzinfo is not None, "Freeze timestamp must include timezone")
    return result


def validate_prelog(data, core_a, core_b, both):
    prelog = data["closure_prelog"]
    need(prelog["frozen_before_phase2_targeted_pair_view"] is True, "Closure prelog not frozen before view")
    need(prelog["protocol_sha256"] == data["_hashes"]["protocol"], "Closure protocol pin mismatch")
    need(prelog["reader_initial_pins"] == {"A": data["_hashes"]["reader_A"], "B": data["_hashes"]["reader_B"]}, "Prelog reader pins mismatch")
    need(set(prelog["core_candidate_intersection"]) == both and len(prelog["core_candidate_intersection"]) == len(both), "Prelog core witness intersection changed")
    inherited = {e["pair_id"] for e in data["inherited"]["positive_edges"]}
    need(set(prelog["excluded_inherited_pair_ids"]) == inherited and len(inherited) == 11, "Prelog must exclude inherited11")
    new = set(data["protocol"]["newly_recovered_ids"])
    requests = prelog["requests"]
    need(len(requests) == 12, "Closure exact12 scope changed")
    result = {}
    for i, request in enumerate(requests):
        key = spatial.pair_key(request["member_ids"])
        need(key == request["pair_id"] and key not in result and key not in inherited and not set(request["member_ids"]) & new, "Unlogged/duplicate/inherited/new-member closure edge")
        need(request["triggers"], "Closure trigger missing")
        for trigger in request["triggers"]:
            member = trigger["trigger_new_id"]
            proposed = trigger["proposed_set"]
            expected = {"--".join(sorted([ident, member])) for ident in request["member_ids"]}
            need(member in new and set(proposed) == set(request["member_ids"]) | {member} and len(proposed) == 3, "Closure trigger/proposed set invalid")
            need(set(trigger["existing_core_candidate_witnesses"]) == expected <= both, "Closure lacks both-reader core edge witnesses")
            need(all(core_a[k][1]["status"] == core_b[k][1]["status"] == SAME for k in expected), "Closure inferred through unsupported core trigger")
        result[key] = (i, request)
    return result


def validate_closure_readers(data, requests):
    ca, cb = data["closure_A"], data["closure_B"]
    expected = set(requests)
    a = indexed(ca["pairs"], expected, "ReaderA closure")
    b = indexed(cb["results"], expected, "ReaderB closure")
    prelog_sha = data["_hashes"]["closure_prelog"]
    need(ca["prelog_sha256"] == cb["prelog_sha256"] == prelog_sha, "Closure input prelog pins invalid")
    need(parse_time(data["closure_prelog"]["frozen_utc"]) < parse_time(ca["freeze_utc"]), "A closure timestamp predates prelog")
    need(ca["source_equivalence_proved_before_first_closure_view"] is True and cb["source_proof_before_targeted_view"] is True, "Closure proof-before-view attestation missing")
    need(ca["initial_reader_A_sha256"] == data["_hashes"]["reader_A"], "A closure initial pin mismatch")
    need(cb["initial_and_confirmation_immutable_pins"] == {RAW_PINS[n][0]: data["_hashes"][n] for n in ("reader_B", "confirmation_B")}, "B closure initial/confirmation pins mismatch")
    for name, reader, rows in (("closure_A", ca, a), ("closure_B", cb, b)):
        need(reader["source_encoded_sha256"] == spatial.SOURCE[1] and reader["source_rgb_sha256"] == data["D9"]["source"]["rgb_sha256"], "Closure source pixel metadata pin mismatch")
        for key, (_, row) in rows.items():
            need(row["status"] == SAME and row.get("source_coverage", row.get("coverage")) == "DIRECT_PAIRED_SOURCE_COMPARISON", "Closure reader gate not positive/direct")
            features = row["eight_feature_comparisons"] if name == "closure_A" else row["eight_feature_comparison"]
            need(set(features) == set(FIELDS), "Closure reader missing8fields")
            for field, feature in features.items():
                relation = feature["paired_relation"] if name == "closure_A" else feature["outcome"]
                expected_relation = "BOTH_POSITIVELY_VISIBLE_AND_COMPATIBLE_IN_DIRECT_NATIVE_SOURCE_COMPARISON" if name == "closure_A" else "SUPPORTED_SAME_VISIBLE_FEATURE_RELATION"
                need(relation == expected_relation, "Closure paired feature relation unsupported")
                for side, ident in zip(("left", "right"), row["member_ids"]):
                    witness = feature[side]
                    concrete(witness["observation"])
                    locator = witness["native_target_witness_bbox_xyxy_halfopen"] if name == "closure_A" else witness["native_locator_bbox_xyxy_halfopen"]
                    local_witness(data, ident, locator)
                    refs = [witness["tight_context_id"], witness["expanded_context_id"]] if name == "closure_A" else witness["source_refs"]
                    need(set(refs) == {v["context_id"] for v in context_views(data, ident).values()}, "Closure feature source refs invalid")
            request = requests[key][1]
            if name == "closure_A":
                need(row["prelogged_trigger_references"] == request["triggers"] and row["unknown_wildcards_used"] is False, "A closure trigger/wildcard gate invalid")
            else:
                need(row["trigger_prelog_reference"]["triggers"] == request["triggers"] and row["new_binding_or_visibility_ambiguity"] is None, "B closure trigger/binding gate invalid")
    return a, b


def review_pins(data, review, closure=False):
    pins = review.get("input_pins", review.get("pins", {}))
    aliases = {
        "protocol": ("protocol_sha256", "comparison_protocol_sha256"),
        "reader_A": ("reader_A_sha256",), "reader_B": ("reader_B_sha256",),
        "closure_prelog": ("closure_prelog_sha256", "prelog_sha256"),
    }
    for name, keys in aliases.items():
        present = [pins[k] for k in keys if k in pins]
        need(present and all(v == data["_hashes"][name] for v in present), f"Final AI pin mismatch: {name}")
    if "reader_B_confirmation_sha256" in pins:
        need(pins["reader_B_confirmation_sha256"] == data["_hashes"]["confirmation_B"], "FinalAI B confirmation pin invalid")
    if closure:
        for name, aliases in (("closure_A", ("closure_A_sha256", "reader_A_closure_sha256")), ("closure_B", ("closure_B_sha256", "reader_B_closure_sha256"))):
            need(any(pins.get(k) == data["_hashes"][name] for k in aliases), f"Final closure AI pin mismatch: {name}")


def validate_final_review(data, name, universe, closure=False):
    review = data[name]
    expected_schemas = {"source257-repeat-final-ai-review-v1"} if not closure else {"source257-repeat-closure-final-ai-review-v1", "source257-repeat-final-ai-closure-review-v1", "source257-repeat-final-ai-review-v1"}
    need(review.get("schema") in expected_schemas, "FinalAI schema invalid")
    review_pins(data, review, closure)
    field = "closure_pair_reviews" if closure else "core_pair_reviews"
    rows = indexed(review[field], universe, "FinalAI " + field)
    for key, (_, row) in rows.items():
        need(row["decision"] in {ACCEPT, DEFER}, "Unsupported finalAI decision")
        need(set(row["eight_feature_checks"]) == set(FIELDS), "FinalAI must preserve all8 feature checks")
        variation = row["variation_assessment"]
        need(isinstance(variation, dict), "FinalAI variation assessment requires paired structured observations")
        for field in ("left_observed_variation", "right_observed_variation", "paired_assessment"):
            concrete(variation[field])
        need(isinstance(variation["not_normalized_away"], list) and bool(variation["not_normalized_away"]), "FinalAI variation safeguards missing")
        for item in variation["not_normalized_away"]:
            concrete(item)
        need("remaining_uncertainty" in row, "FinalAI uncertainty field missing")
        for field, witness in row["eight_feature_checks"].items():
            for side, ident in zip(("left", "right"), row["member_ids"]):
                if row["decision"] == ACCEPT:
                    concrete(witness[side + "_observation"])
                else:
                    need(isinstance(witness[side + "_observation"], str), "Deferred source observation missing")
                local_witness(data, ident, witness[side + "_native_locator_bbox_xyxy_halfopen"])
            views(witness["source_view_refs"], data, row["member_ids"], True)
            if row["decision"] == ACCEPT:
                need(witness["relation"] == "SUPPORTED_SAME_VISIBLE_RELATION", "FinalAI positive cannot use UNKNOWN/incompatible relation")
        if row["decision"] == ACCEPT:
            need(row["remaining_uncertainty"] in (None, [], "", "NONE"), "FinalAI accepts despite unresolved uncertainty")
    return rows


def unit_source_refs(data, ident, observations):
    result = {}
    for field in FIELDS:
        index = observations[ident][0]
        result[field] = {"reader_A_observation": ref(data, "reader_A", f"/source_observations/{index}/features/{field}"), "reader_A_native_locator": ref(data, "reader_A", f"/source_observations/{index}/native_target_search_bbox_xyxy_halfopen"), "reader_A_views": ref(data, "reader_A", f"/source_observations/{index}/view_references"), "reader_B_feature_witness": ref(data, "reader_B", f"/observation_dictionary/{ident}/eight_feature_observations/{field}")}
    return result


def reason_for(a, b):
    if (a["status"] == SAME) != (b["status"] == SAME):
        return "READER_CANDIDATE_CONFLICT"
    if a["status"] == "DEFERRED_PRESCREEN" and b["status"] == "DIFFERENT_GRAPHICS" and b["coverage"] == "DERIVED_UNIT_SOURCE_FEATURE_CONTRAST":
        return "PRESCREEN_WITH_SINGLE_READER_DERIVED_CONTRAST_NOT_ACCEPTED_NEGATIVE"
    if a["status"] == "DIFFERENT_GRAPHICS" and b["status"] != "DIFFERENT_GRAPHICS":
        return "ONE_READER_DIFFERENCE_WITH_OTHER_READER_DEFERRED"
    return "READER_DEFERRED_FEATURE_OR_BINDING"


def build(data):
    need("final_core" in data and "final_closure" in data, "Real final core+closure reviews required before canonical assembly")
    observations = validate_source_observations(data)
    scope, aa, bb, both, confirmations = raw_core(data)
    requests = validate_prelog(data, aa, bb, both)
    ca, cb = validate_closure_readers(data, requests)
    final_core = validate_final_review(data, "final_core", both)
    final_closure = validate_final_review(data, "final_closure", set(requests), True)
    rows = []
    for key in sorted(scope):
        ia, a = aa[key]
        ib, b = bb[key]
        record = {"pair_id": key, "member_ids": a["member_ids"], "scope": "CORE_930", "cohort": a["cohort"], "reader_A": {"raw_reference": ref(data, "reader_A", f"/pairs/{ia}"), "status": a["status"], "coverage": a["source_coverage"]}, "reader_B": {"raw_reference": ref(data, "reader_B", f"/pairs/{ib}"), "status": b["status"], "coverage": b["coverage"]}, "eight_feature_source_witnesses": {side: {"canonical_json_pointer": f"/source_feature_witnesses/{ident}"} for side, ident in zip(("left", "right"), a["member_ids"])}, "status": "DEFERRED", "deferred_reason": reason_for(a, b), "final_AI_reference": None, "reader_B_actual_confirmation_reference": None}
        if key in both:
            validate_core_positive(data, key, aa, bb, confirmations, observations)
            final_index, final = final_core[key]
            record["final_AI_reference"] = ref(data, "final_core", f"/core_pair_reviews/{final_index}")
            record["reader_B_actual_confirmation_reference"] = ref(data, "confirmation_B", f"/confirmations/{confirmations[key][0]}")
            record["paired_gate_references"] = {"reader_A": ref(data, "reader_A", f"/pairs/{ia}/evidence/eight_feature_comparisons"), "reader_B": ref(data, "reader_B", f"/pairs/{ib}/eight_feature_comparison"), "reader_B_confirmation": ref(data, "confirmation_B", f"/confirmations/{confirmations[key][0]}/eight_feature_recheck"), "final_AI": ref(data, "final_core", f"/core_pair_reviews/{final_index}/eight_feature_checks")}
            record["status"] = ACCEPTED if final["decision"] == ACCEPT else "DEFERRED"
            record["deferred_reason"] = None if record["status"] == ACCEPTED else "FINAL_AI_FEATURE_OR_BINDING_DEFERRED"
        rows.append(record)
    closure_rows = []
    accepted_core = {r["pair_id"] for r in rows if r["status"] == ACCEPTED}
    for key in sorted(requests):
        request_index, request = requests[key]
        ai, a = ca[key]
        bi, b = cb[key]
        fi, final = final_closure[key]
        active_triggers = [trigger for trigger in request["triggers"] if set(trigger["existing_core_candidate_witnesses"]) <= accepted_core]
        accepted = final["decision"] == ACCEPT and bool(active_triggers)
        closure_rows.append({"pair_id": key, "member_ids": request["member_ids"], "scope": "PRELOGGED_OLD_OLD_CLOSURE_12", "prelog_reference": ref(data, "closure_prelog", f"/requests/{request_index}"), "reader_A_reference": ref(data, "closure_A", f"/pairs/{ai}"), "reader_B_reference": ref(data, "closure_B", f"/results/{bi}"), "reader_A_status": a["status"], "reader_B_status": b["status"], "reader_A_coverage": a["source_coverage"], "reader_B_coverage": b["coverage"], "eight_feature_reader_A_reference": ref(data, "closure_A", f"/pairs/{ai}/eight_feature_comparisons"), "eight_feature_reader_B_reference": ref(data, "closure_B", f"/results/{bi}/eight_feature_comparison"), "final_AI_reference": ref(data, "final_closure", f"/closure_pair_reviews/{fi}"), "active_finally_accepted_trigger_ids": sorted({t["trigger_new_id"] for t in active_triggers}), "status": ACCEPTED if accepted else "DEFERRED", "deferred_reason": None if accepted else "FINAL_AI_FEATURE_OR_BINDING_DEFERRED" if final["decision"] != ACCEPT else "NO_FINALLY_ACCEPTED_NEW_MEMBER_TRIGGER"})
    graph_input = {"schema": "source257-positive-edge-graph-input-v1", "purpose": "PREPARATION_ONLY", "new_positive_edges": []}
    for group, review_name in ((rows, "final_core"), (closure_rows, "final_closure")):
        for row in group:
            if row["status"] != ACCEPTED:
                continue
            rr = row["final_AI_reference"]
            edge = {"member_ids": row["member_ids"], "origin": "CORE_930" if row["scope"] == "CORE_930" else "PRELOGGED_OLD_OLD_CLOSURE", "evidence_reference": {"path": data["_paths"][review_name], "sha256": data["_hashes"][review_name], "json_pointer": rr["json_pointer"]}}
            if row["scope"] != "CORE_930":
                request = requests[row["pair_id"]][1]
                trigger = next(t for t in request["triggers"] if t["trigger_new_id"] in row["active_finally_accepted_trigger_ids"])
                edge.update({"triggering_new_member": trigger["trigger_new_id"], "proposed_member_ids": trigger["proposed_set"], "closure_prelog_reference": {"path": data["_paths"]["closure_prelog"], "sha256": data["_hashes"]["closure_prelog"], "json_pointer": row["prelog_reference"]["json_pointer"]}})
            graph_input["new_positive_edges"].append(edge)
    prep = spatial.assemble(data, graph_input)
    fixture = bool(data["final_core"].get("synthetic_fixture_only") or data["final_closure"].get("synthetic_fixture_only"))
    purpose = "SYNTHETIC_FIXTURE_ONLY_NOT_SCIENTIFIC" if fixture else "SOURCE_GATED_GRAPHICAL_CANDIDATES_NOT_CIPHER_IDENTITIES"
    graph = copy.deepcopy(prep["graph"])
    graph.update({"purpose": purpose, "evidence_validation": "TWO_SOURCE_READERS_B_ACTUAL_CONFIRMATION_AND_SEPARATE_FINAL_AI_GATES_VALIDATED"})
    prep["purpose"] = purpose
    prep["graph"] = graph
    prep["schema"] = "source257-canonical-spatial-repeat-v1"
    prep["source_pixel_handling"] = "CURRENT_ENCODED_BYTES_HASH_VERIFIED_NO_PIXEL_DECODE_OR_VIEW" if data.get("_current_encoded_verification") else "PINNED_READER_ORIGINAL_SOURCE_PROOFS_AND_D9_METADATA_NO_CURRENT_PIXEL_OR_JPEG_READ"
    prep["canonical_gate_state"] = "SYNTHETIC_FIXTURE_ONLY" if fixture else "SOURCE_GATE_COMPLETE"
    prep["limitations"] = [item for item in prep["limitations"] if not item.startswith("Optional graph input")]
    prep["limitations"].append("Accepted edges are full-visible-feature graphical candidates; no cipher identity, alphabet partition, linguistic order or negative cannot-link is inferred.")
    result = {"schema": "source257-canonical-repeat-evidence-v1", "purpose": purpose, "input_bindings": {name: {"path": data["_paths"][name], "sha256": digest} for name, digest in sorted(data["_hashes"].items())}, "source_verification": "PINNED_READER_SOURCE_PROOF_ATTESTATIONS_AND_D9_METADATA_NO_DEFAULT_JPEG_REQUIRED", "source_feature_witnesses": {ident: unit_source_refs(data, ident, observations) for ident in sorted(observations)}, "core_pairs": rows, "closure_pairs": closure_rows, "inherited_positive_edges": data["inherited"]["positive_edges"], "inherited_candidate_sets": data["inherited"]["candidate_sets"], "graph": graph, "spatial": prep, "summary": {"core_scope": 930, "core_status_counts": dict(Counter(r["status"] for r in rows)), "core_deferred_reasons": dict(Counter(r["deferred_reason"] for r in rows if r["status"] == "DEFERRED")), "accepted_different_graphics": 0, "both_initial_reader_candidates": len(both), "reader_A_direct_core_pairs": sum(r["source_coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON" for _, r in aa.values()), "reader_B_initial_direct_core_pairs": sum(r["coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON" for _, r in bb.values()), "reader_B_actual_confirmed_core_pairs": len(confirmations), "direct_comparisons_not_exhaustive": True, "closure_scope": 12, "closure_status_counts": dict(Counter(r["status"] for r in closure_rows)), "inherited_edges": 11, "graph_positive_edges": len(graph["positive_edges"]), "maximal_graph_cliques": len(graph["maximal_cliques"]), "profiles_with_graph_membership": sum(bool(m) for m in graph["memberships"].values()), "profiles_without_graph_membership": sum(not m for m in graph["memberships"].values()), "newly_recovered_profiles_linked": sum(bool(graph["memberships"][ident]) for ident in data["protocol"]["newly_recovered_ids"]), "cipher_identity": "UNKNOWN"}, "chronology": {"prelog_reference": ref(data, "closure_prelog", "/frozen_utc"), "A_result_freeze_timestamp_after_prelog_not_first_view_timestamp": True, "A_before_view_basis": "PINNED_PRELOG_BOUND_BEFORE_VIEW_ATTESTATION", "B_before_view_basis": "PRELOG_BOUND_BEFORE_VIEW_ATTESTATION_NOT_INTRINSIC_TIMESTAMP_PROOF"}}

    if "_public_bindings" in data:
        result["public_selection_bindings"] = data["_public_bindings"]
    result["current_original_encoded_verification"] = data.get("_current_encoded_verification")
    return result


TSV_COLUMNS = ("region", "display_rank", "id", "inherited_order", "base_bbox", "full_feature_label_status", "candidate_graph_membership_ids", "repeat_status", "sequence_length", "cipher_unit_identity")
TSV_NOTICE = "# ANNOTATION_RECORDS_NOT_GLYPHS; DISPLAY_ONLY_NOT_READING; CROSS_REGION_LINKS_UNKNOWN\n# ALL_SEQUENCE_LENGTHS_UNKNOWN; NO_CONCATENATED_CIPHERTEXT\n"


def sequence_tsv(canonical):
    """Export an already-validated canonical result; no source work or text string."""
    stream = io.StringIO(newline="")
    stream.write(TSV_NOTICE)
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(TSV_COLUMNS)
    for region in canonical["spatial"]["regions"]:
        for row in region["records"]:
            writer.writerow((region["region"], row["display_rank"], row["id"], row["inherited_order_value"], json.dumps(row["source_base_native_bbox_xyxy_halfopen"], separators=(",", ":")), row["full_feature_label_status"], json.dumps(row["candidate_graph_membership_ids"], separators=(",", ":")), row["repeat_status"], row["sequence_length"], row["cipher_unit_identity"]))
    return stream.getvalue()


def write_text_once(output, text, protected):
    output = spatial.safe_output_path(output, protected)
    spatial.verify_unchanged(protected)
    fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        spatial.verify_unchanged(protected)
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def write_canonical_once(output, result, protected):
    need(result["purpose"] != "SYNTHETIC_FIXTURE_ONLY_NOT_SCIENTIFIC", "Synthetic fixtures cannot be written as production evidence")
    spatial.write_once(output, result, protected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=spatial.DEFAULT_ROOT)
    parser.add_argument("--stage", type=Path, default=spatial.STAGE)
    parser.add_argument("--public-repository-root", type=Path)
    parser.add_argument("--public-data-directory", type=Path)
    parser.add_argument("--published-data-relative")
    for name in ("final-core", "final-closure"):
        parser.add_argument("--" + name, type=Path, required=True)
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-tsv", type=Path)
    parser.add_argument("--verify-original-source", type=Path)
    args = parser.parse_args()
    if args.public_repository_root or args.public_data_directory:
        need(args.public_repository_root is not None and args.public_data_directory is not None, "Public repository root and data directory must be supplied together")
        from public_repeat_bindings import load as load_public
        data, protected = load_public(args.public_repository_root, args.public_data_directory, published_data_relative=args.published_data_relative)
    else:
        data, protected = load(args.root, args.stage)
    for name in ("final_core", "final_closure"):
        attach_review(data, protected, name, getattr(args, name), getattr(args, name + "_sha256"))
    if args.verify_original_source:
        need(spatial.sha(args.verify_original_source.read_bytes()) == spatial.SOURCE[1], "Optional original source encoded pin mismatch")
        protected["optional_original_source"] = (args.verify_original_source, spatial.SOURCE[1])
        data["_current_encoded_verification"] = {"sha256": spatial.SOURCE[1], "method": "CURRENT_ENCODED_BYTES_HASH_ONLY_NO_PIXEL_DECODE_OR_VIEW"}
    spatial.safe_output_path(args.output, protected)
    if args.sequence_tsv:
        spatial.safe_output_path(args.sequence_tsv, protected)
        need(args.sequence_tsv.resolve() != args.output.resolve(), "TSV cannot alias canonical output")
    result = build(data)
    need(result["purpose"] != "SYNTHETIC_FIXTURE_ONLY_NOT_SCIENTIFIC", "Synthetic fixtures cannot be written as production evidence")
    from check_canonical_repeat_evidence import check, check_sequence_tsv
    check(result, data)
    write_canonical_once(args.output, result, protected)
    if args.sequence_tsv:
        protected["written_canonical_output"] = (args.output, spatial.sha(args.output.read_bytes()))
        text = sequence_tsv(result)
        check_sequence_tsv(text, result)
        write_text_once(args.sequence_tsv, text, protected)
    print(json.dumps({"status": "CANONICAL_WRITTEN", "sha256": spatial.sha(args.output.read_bytes()), "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
