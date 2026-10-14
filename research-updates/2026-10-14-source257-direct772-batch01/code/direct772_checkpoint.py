#!/usr/bin/env python3
"""Bounded direct-source checkpoint; Python3.10 stdlib, no pixel/proof reads.

Only fixed frozen source-report hashes authorize production. Synthetic fixtures
exercise the pure builder and can never authorize a production write. Safe-write
and reference checks adapted from D13 conflict_delta.py SHA256
3c952315e98aa27ed717fbcaf6993b9a8c95f182e5fbfea1344e737d98b4e9a3.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
INPUT_PINS = {
    "protocol": ("direct772-protocol-v2.json", "43d8e1c6dd86520b0b0e4f58f88c19bdfb025830978aacff3069852f709b0797"),
    "safe_protocol": ("source-observation-protocol-v1.json", "647b640943976508ea1020c9699f51819cde6acb6db9ba47ddb658c8f2daa844"),
    "queue": ("direct772-queue-v1.json", "ecfb18d68ac7135f3c3215f0ec1843a199f1eda20840ab6cf98003a8b37818c0"),
    "intake": ("judge-source-geometry-intake-v1.json", "64745684aecba5f547b4033d2d9425a8864955b94078f88aa9ae3620d0f96bca"),
    "format": ("source-reader-output-format-v2.json", "5f4b05db7c5babc6836dcfdecfcd904a5ca32205fb392e615dc711ff40b0843d"),
    "final_format": ("final-output-format-v1.json", "1c17bdcc929a7c1e5d279c2ad1435f56279f3c469cc8092b2841b291a0f4b4b1"),
}
PUBLIC_PINS = {
    "baseline": ("research-updates/2026-10-14-source257-repeat-sequence/data/canonical-repeat-evidence-v1.json", "5083d313a78796ac32f21f71d93b9b53b230874782f8a4558324b12d7e2d8348"),
    "D13_protocol": ("research-updates/2026-10-14-source257-conflict-route-review/results/conflict-route-protocol-v1.json", "554f461bcf6a210b3bb91da3a36b78042410649083840002413f0bcc82d388dc"),
    "D13_delta": ("research-updates/2026-10-14-source257-conflict-route-review/results/conflict-route-delta-v1.json", "32e69668c238ab0ce02c08a257a3235ebc0235ae887e643627c28b5a7608049a"),
}
BOARD_PIN = ("pair-context-pack-v1/pair-index-v1.json", "e5bde69314dd64b6fde7df429688808e3a12b74429addfa4f566fc3bca37a7fb")
METHOD_GATE_PIN = ("method-protocol-gate-private-v1.json", "bec5786f9e46968044d84740bd42b249de604ec4d7ed5eb30fb044cd47da6fee")
FROZEN_EVIDENCE_PINS = {
    "reader_A": ("source-reader-A-initial-v1.json", "02a42214d3b1c84c98eb73f90c31442f4b58149540fc7d714d08b8b67ea51136"),
    "reader_B": ("source-reader-B-initial-v1.json", "ce8c857aea674ef266bc22e6fa4a4fcd94c57eb1d4cd7bd86820157400e9278e"),
    "final_review": ("direct772-final-ai-v1.json", "c2bff888107c17cda8c1d4518e1c635642b88c5ca39c5518bd09b2008456fa3c"),
}  # Bound to actual immutable source reports; new versions require code review.
FIELDS = ("path_topology", "enclosures", "openings", "stem_pattern", "attached_bars", "connected_extra_strokes", "terminal_pattern", "owned_mark_profile")
REPEAT = "FULL_GRAPHICAL_REPEAT_SUPPORT"
DIFFERENCE = "OBSERVED_GRAPHICAL_DIFFERENCE"
UNCERTAIN = "UNCERTAIN"
KINDS = {"STRUCTURAL_FEATURE_DIFFERENCE", "VISIBLE_FORM_VARIATION"}
CODE_FILES = ("direct772_checkpoint.py", "check_direct772_checkpoint.py", "test_direct772_checkpoint.py")


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def literal(value):
    need(isinstance(value, str) and bool(value.strip()), "Concrete statement required")


def concrete(value):
    literal(value)
    need(value.strip().upper() not in {"UNKNOWN", "UNRESOLVED", "NONE", "N/A", "?", "*", "SAME", "DIFFERENT"} and not value.strip().upper().startswith(("UNKNOWN ", "UNRESOLVED ", "NOT VISIBLE")), "Unknown cannot support a source fact")


def timestamp(value):
    literal(value)
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(result.tzinfo is not None, "Timestamp timezone required")
    return result


def hexhash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def exact(values, expected, label):
    need(isinstance(values, list) and len(values) == len(set(values)) and set(values) == set(expected), label + " actual coverage mismatch")


def records(rows, expected, field, label):
    need(isinstance(rows, list), label + " records required")
    result = {}
    for index, row in enumerate(rows):
        ident = row[field]
        need(ident not in result, label + " duplicate ID")
        result[ident] = (index, row)
    need(set(result) == set(expected) and len(rows) == len(expected), label + " scope mismatch")
    return result


def read_pin(data, protected, name, path, expected):
    need(not path.is_symlink() and path.is_file(), "Pinned regular input required: " + name)
    raw = path.read_bytes()
    need(digest(raw) == expected, "Input SHA mismatch: " + name)
    data[name] = json.loads(raw)
    protected[name] = (path, expected)


def load_metadata(repository_root, input_directory=STAGE / "results"):
    repository_root, input_directory = Path(repository_root).resolve(), Path(input_directory).resolve()
    data, protected = {}, {}
    for name, (relative, pin) in INPUT_PINS.items():
        read_pin(data, protected, name, input_directory / relative, pin)
    for name, (relative, pin) in PUBLIC_PINS.items():
        read_pin(data, protected, name, repository_root / relative, pin)
    data["_hashes"] = {name: pin for name, (_, pin) in protected.items()}
    data["_paths"] = {name: relative for name, (relative, _) in {**INPUT_PINS, **PUBLIC_PINS}.items()}
    data["_code_sha256"] = {name: digest((Path(__file__).parent / name).read_bytes()) for name in CODE_FILES}
    for name, pin in data["_code_sha256"].items():
        protected["code/" + name] = (Path(__file__).parent / name, pin)
    validate_metadata(data)
    return data, protected


def load(repository_root, input_directory=STAGE / "results"):
    need(BOARD_PIN is not None and METHOD_GATE_PIN is not None, "Actual index/method gate not frozen")
    need(set(FROZEN_EVIDENCE_PINS) == {"reader_A", "reader_B", "final_review"}, "Actual production report hashes not frozen")
    data, protected = load_metadata(repository_root, input_directory)
    specs = {"board_index": BOARD_PIN, "method_gate": METHOD_GATE_PIN, **FROZEN_EVIDENCE_PINS}
    for name, (relative, pin) in specs.items():
        parent = Path(input_directory).parent if name == "board_index" else Path(input_directory)
        read_pin(data, protected, name, parent / relative, pin)
        data["_hashes"][name], data["_paths"][name] = pin, relative
    data["_pair_boards"] = validate_index(data)
    need(data["method_gate"]["status"] == "PASS" and data["method_gate"]["source_protocol_sha256"] == data["_hashes"]["protocol"], "Actual method gate not bound to authoritative protocol")
    return data, protected


def validate_metadata(data):
    q, base = data["queue"], data["baseline"]
    rows = q["ordered_queue"]
    need(len(rows) == 772 and [r["ordinal"] for r in rows] == list(range(1, 773)), "Exact contiguous772 queue required")
    ids = [r["pair_id"] for r in rows]
    need(ids == sorted(set(ids)), "Queue lexical order/unique IDs changed")
    for row in rows:
        need(row["member_ids"] == sorted(set(row["member_ids"])) and len(row["member_ids"]) == 2 and row["pair_id"] == "--".join(row["member_ids"]), "Pair member binding invalid")
    need(q["selected_pair_ids"] == ids[:64] and q["remaining_pair_ids"] == ids[64:], "First64/remainder708 changed")
    need(q["selected_profile_ids"] == sorted({ident for r in rows[:64] for ident in r["member_ids"]}) and len(q["selected_profile_ids"]) == 36, "Selected36 targets changed")
    selected = [r for r in base["core_pairs"] if r["deferred_reason"] == "PRESCREEN_WITH_SINGLE_READER_DERIVED_CONTRAST_NOT_ACCEPTED_NEGATIVE"]
    need(ids == sorted(r["pair_id"] for r in selected), "Queue not exact eligible772 baseline source-coverage cohort")
    for row in selected:
        need(row["status"] == "DEFERRED" and row["reader_A"]["coverage"] == "METADATA_PRESCREEN_WITH_SEPARATE_UNIT_SOURCE_OBSERVATIONS" and row["reader_B"]["coverage"] == "DERIVED_UNIT_SOURCE_FEATURE_CONTRAST" and row["reader_B_actual_confirmation_reference"] is None, "Previously inspected pair in queue")
    previous = {r["pair_id"] for r in base["core_pairs"] if any(r[k]["coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON" for k in ("reader_A", "reader_B")) or r["reader_B_actual_confirmation_reference"] is not None}
    previous |= {r["pair_id"] for r in base["graph"]["positive_edges"]} | {r["pair_id"] for r in base["closure_pairs"]} | set(data["D13_protocol"]["fixed_pair_ids"])
    need(not set(ids) & previous, "Previously directly compared/accepted pair repeated")
    need([r["pair_id"] for r in data["intake"]["pairs"]] == ids[:64] and sorted(p["id"] for p in data["intake"]["profiles"]) == q["selected_profile_ids"], "Intake exact64/36 mismatch")
    need(data["safe_protocol"] == data["protocol"]["source_reader_view"] and tuple(data["safe_protocol"]["feature_dimensions"]) == FIELDS, "Safe protocol/feature dimensions changed")
    for field, name in (("queue_sha256", "queue"), ("intake_sha256", "intake"), ("output_format_sha256", "format"), ("baseline_canonical_sha256", "baseline"), ("D13_delta_sha256", "D13_delta")):
        need(data["protocol"]["input_pins"][field] == data["_hashes"][name], "Protocol input pin changed")
    need(data["D13_delta"]["current_graph_overlay"]["current_positive_pair_ids"] == sorted(e["pair_id"] for e in base["graph"]["positive_edges"]), "Baseline graph changed before this pair-only stage")


def profiles(data):
    return {p["id"]: p for p in data["intake"]["profiles"]}


def validate_index(data):
    index, geometry = data["board_index"], profiles(data)
    need(index["safe_intake_sha256"] == data["_hashes"]["intake"] and index["source_size"] == data["intake"]["source_size"] and index["scale"] == 1, "Index intake/size/scale mismatch")
    need(len(index["boards"]) == 16 and len({b["board_id"] for b in index["boards"]}) == 16, "Actual16 boards required")
    mapping = {}
    for board in index["boards"]:
        for pair in board["pair_ids"]:
            need(pair in data["queue"]["selected_pair_ids"] and pair not in mapping, "Board pair repeated or outside first64")
            mapping[pair] = board["board_id"]
            panels = [p for p in board["panels"] if p["pair_id"] == pair]
            need(len(panels) == 4 and {(p["target_id"], p["window_kind"]) for p in panels} == {(ident, kind) for ident in pair.split("--") for kind in ("TIGHT", "CONTEXT")}, "Both actual tight/context views required")
            for panel in panels:
                p = geometry[panel["target_id"]]
                window = p["windows"][panel["window_kind"]]
                need(panel["context_id"] == window["context_id"] and panel["native_bbox_xyxy_halfopen"] == window["native_bbox_xyxy_halfopen"] and panel["rotation_degrees_clockwise"] == p["rotation_degrees_clockwise"], "Wrong target context/frame in board")
    need(set(mapping) == set(data["queue"]["selected_pair_ids"]), "Paired index missing selected pair")
    return mapping


def context_ids(data, ids, refs, complete=False):
    allowed = {w["context_id"] for ident in ids for w in profiles(data)[ident]["windows"].values()}
    need(isinstance(refs, list) and refs and len(refs) == len(set(refs)) and set(refs) <= allowed, "Unknown/wrong-target source context")
    if complete:
        need(set(refs) == allowed, "Both tight/context references required")


def boxes(data, ident, values, refs=None):
    need(isinstance(values, list) and values, "Native witnesses required")
    context = profiles(data)[ident]["windows"]["CONTEXT"]["native_bbox_xyxy_halfopen"]
    w, h = data["intake"]["source_size"]
    for box in values:
        need(isinstance(box, list) and len(box) == 4 and all(type(n) is int for n in box), "Native witness must have four integers")
        x0, y0, x1, y1 = box
        need(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h and context[0] <= x0 < x1 <= context[2] and context[1] <= y0 < y1 <= context[3], "Witness outside correct expanded context")
        if refs is not None:
            named = [v["native_bbox_xyxy_halfopen"] for v in profiles(data)[ident]["windows"].values() if v["context_id"] in refs]
            need(any(c[0] <= x0 < x1 <= c[2] and c[1] <= y0 < y1 <= c[3] for c in named), "Native witness absent from its named source view")
    # No intersection/containment gate on approximate target search locators.


def pins(data, report, mapping):
    for key, name in mapping.items():
        need(report["input_pins"].get(key) == data["_hashes"][name], "Report pin mismatch: " + key)


def target_facts(data, report):
    targets = records(report["target_observations"], data["queue"]["selected_profile_ids"], "id", "Target36")
    geometry = profiles(data)
    for ident, (_, target) in targets.items():
        p = geometry[ident]
        need(target["approved_target_native_bbox_xyxy_halfopen"] == p["approved_target_bbox"], "Approximate target locator changed")
        need(p["rotation_degrees_clockwise"] in (0, 90) and target["frame"] == p["frame"] == ("EXACT90CW" if p["rotation_degrees_clockwise"] == 90 else "NATIVE0"), "Target frame/sign mismatch")
        context_ids(data, [ident], target["source_context_ids"], True)
        literal(target["full_route_description"])
        need(target["binding_state"] in {"SUPPORTED_TARGET_ROUTE", "UNRESOLVED"} and target["complete_route_visibility"] in {"FULL", "UNRESOLVED"}, "Target binding/visibility invalid")
        need(target["cipher_identity"] == target["letter_value"] == "UNKNOWN", "Cipher/letter identity inferred")
        need(set(target["eight_features"]) == set(FIELDS), "Target needs exact eight dimensions")
        for feature in target["eight_features"].values():
            literal(feature["observation"])
            literal(feature["continuity_source_witness"])
            need(feature["certainty"] in {"SOURCE_SUPPORTED", "UNRESOLVED"} and feature["ownership"] in {"TARGET_ROUTE", "UNRESOLVED"} and feature["relevant_route_visibility"] in {"FULL", "UNRESOLVED"} and type(feature["absence_claim"]) is bool, "Feature support/ownership/visibility invalid")
            boxes(data, ident, feature["native_locator_boxes"], feature["source_context_ids"])
            context_ids(data, [ident], feature["source_context_ids"])
            if feature["certainty"] == "SOURCE_SUPPORTED":
                concrete(feature["observation"])
            if feature["ownership"] == "TARGET_ROUTE":
                concrete(feature["continuity_source_witness"])
            if feature["absence_claim"]:
                need(feature_supported(feature), "Unknown/partial/unowned feature cannot establish absence")
        for field in ("free_end_observations", "bar_return_junctions", "competing_routes"):
            need(isinstance(target[field], list), "Route elements missing")
            for element in target[field]:
                literal(element["description"])
                literal(element["continuity_source_witness"])
                need(element["ownership"] in {"TARGET_ROUTE", "NEIGHBOR_ROUTE", "UNRESOLVED"} and element["actual_visibility"] in {"FULL", "UNRESOLVED"}, "Route element visibility/ownership invalid")
                boxes(data, ident, element["native_locator_boxes"], element["source_context_ids"])
                context_ids(data, [ident], element["source_context_ids"])
                if element["ownership"] in {"TARGET_ROUTE", "NEIGHBOR_ROUTE"}:
                    concrete(element["continuity_source_witness"])
                known = {n["id"] for n in p["windows"]["CONTEXT"]["intersecting_annotations"]} - {ident}
                need(isinstance(element["neighbor_ids"], list) and set(element["neighbor_ids"]) <= known, "Unknown neighboring route ID")
    return targets


def feature_supported(feature):
    return feature["certainty"] == "SOURCE_SUPPORTED" and feature["ownership"] == "TARGET_ROUTE" and feature["relevant_route_visibility"] == "FULL"


def summary_statement(value, field):
    """Preserve literal and frozen B's dimension-tagged summaries without coercion."""
    if isinstance(value, str):
        literal(value)
        return
    expected = {"dimension", "kind", "observation"} if field == "significant_variation" else {"dimension", "issue"}
    need(isinstance(value, dict) and set(value) == expected and value["dimension"] in FIELDS, "Structured source summary dimension/shape invalid")
    if field == "significant_variation":
        need(value["kind"] in KINDS, "Structured variation kind invalid")
    literal(value["observation" if field == "significant_variation" else "issue"])


def report_rows(data, name, final=False):
    report = data[name]
    need(report["schema"] == ("source257-direct772-final-ai-v1" if final else "source257-direct772-reader-initial-v1") and report["phase"] == ("FINAL_SOURCE_ADJUDICATION" if final else "INITIAL_SOURCE_ONLY_FROZEN"), "Report schema/phase invalid")
    label = report["reviewer" if final else "reader"]
    literal(label)
    need("/" not in label and "\\" not in label, "Operational reader path prohibited")
    frozen = timestamp(report["frozen_utc"])
    need(frozen >= timestamp(data["protocol"]["frozen_utc"]), "Report freeze precedes protocol")
    pins(data, report, {"safe_protocol_sha256": "safe_protocol", "safe_intake_sha256": "intake", "queue_sha256": "queue", "context_index_sha256": "board_index", "output_format_sha256": "format"})
    source = data["safe_protocol"]["original_source"]
    need(report["original_source_pins"] == {"encoded_sha256": source["encoded_sha256"], "rgb_sha256": source["rgb_sha256"]}, "Whole original source pins wrong")
    need(hexhash(report["whole_private_proof_json_sha256"]) and report["proof_before_view"] is True, "Actual whole-proof/before-view attestation required")
    if final:
        pins(data, report, {"protocol_sha256": "protocol", "reader_A_sha256": "reader_A", "reader_B_sha256": "reader_B", "final_output_format_sha256": "final_format"})
        c = report["conditioning"]
        need(c["both_initials_read"] is True and c["is_blind_agreement"] is False, "Final conditioning disclosure missing")
        literal(c["details"])
        need(frozen >= max(timestamp(data[n]["frozen_utc"]) for n in ("reader_A", "reader_B")), "Final freeze precedes an initial")
    else:
        exposure = report["prior_exposure"]
        need(all(type(exposure[k]) is bool for k in ("geometry_and_batch_selection_seen", "historical_feature_or_outcome_claims_seen", "other_initial_reader_report_seen")), "Actual source exposure booleans required")
        literal(exposure["details"])
    coverage = report["coverage"]
    need(coverage["scope"] == "FIXED_FIRST64_ONLY", "Report outside bounded scope")
    exact(coverage["actual_pair_ids_viewed"], data["queue"]["selected_pair_ids"], "Pair64")
    exact(coverage["actual_target_ids_inspected"], data["queue"]["selected_profile_ids"], "Target36")
    exact(coverage["actual_board_ids_viewed"], set(data["_pair_boards"].values()), "Board16")
    targets = target_facts(data, report)
    rows = records(report["pair_observations"], data["queue"]["selected_pair_ids"], "pair_id", "Pair64")
    for key, (_, row) in rows.items():
        need(row["member_ids"] == key.split("--") and row["actual_native_board_id"] == data["_pair_boards"][key] and row["coverage"] == "DIRECT_NATIVE_PAIRED_SOURCE_INSPECTION", "Actual pair/board/direct-coverage binding invalid")
        need(row["candidate_outcome"] in {REPEAT, DIFFERENCE, UNCERTAIN}, "Unknown source category")
        need(row["cipher_identity"] == row["letter_value"] == row["allographic_significance"] == "UNKNOWN", "Cipher/allographic significance inferred")
        for field in ("significant_variation", "remaining_uncertainty"):
            need(isinstance(row[field], list), "Raw variation/uncertainty list required")
            for statement in row[field]:
                summary_statement(statement, field)
        if final:
            concrete(row["adjudication_grounds"])
        comparisons = row["eight_paired_comparisons"]
        need(set(comparisons) == set(FIELDS), "Missing paired dimension")
        for field, check in comparisons.items():
            literal(check["paired_source_grounds"])
            need(check["relation"] in {"SUPPORTED_COMPATIBLE", "OBSERVED_DIFFERENCE", "UNRESOLVED"} and check["difference_kind"] in KINDS | {"NONE"}, "Paired relation/kind invalid")
            need((check["relation"] == "OBSERVED_DIFFERENCE") == (check["difference_kind"] in KINDS), "Difference kind must describe exactly a local observed difference")
            if check["relation"] != "UNRESOLVED":
                concrete(check["paired_source_grounds"])
            context_ids(data, row["member_ids"], check["source_context_ids"], True)
            for side, ident in zip(("left", "right"), row["member_ids"]):
                need(check[side + "_target_feature_ref"] == f"/target_observations/{targets[ident][0]}/eight_features/{field}", "Paired fact reference targets wrong ID/feature")
                boxes(data, ident, check["native_locator_boxes_" + side], check["source_context_ids"])
                need(check["relevant_visibility_" + side] in {"FULL", "UNRESOLVED"} and type(check["ownership_supported_" + side]) is bool, "Relevant paired visibility/ownership missing")
    return targets, rows


def visible_difference_keys(row, targets):
    result = set()
    for field, check in row["eight_paired_comparisons"].items():
        if check["relation"] != "OBSERVED_DIFFERENCE":
            continue
        owned = all(feature_supported(targets[ident][1]["eight_features"][field]) and check["ownership_supported_" + side] and check["relevant_visibility_" + side] == "FULL" for side, ident in zip(("left", "right"), row["member_ids"]))
        if owned:
            result.add((field, check["difference_kind"]))
    return result


def full_repeat(row, targets):
    if row["candidate_outcome"] != REPEAT or row["remaining_uncertainty"] or row["significant_variation"]:
        return False
    for ident in row["member_ids"]:
        target = targets[ident][1]
        if target["binding_state"] != "SUPPORTED_TARGET_ROUTE" or target["complete_route_visibility"] != "FULL" or not all(feature_supported(f) for f in target["eight_features"].values()):
            return False
        if any(e["ownership"] == "UNRESOLVED" or e["actual_visibility"] != "FULL" for field in ("free_end_observations", "bar_return_junctions", "competing_routes") for e in target[field]):
            return False
    return all(c["relation"] == "SUPPORTED_COMPATIBLE" and c["relevant_visibility_left"] == c["relevant_visibility_right"] == "FULL" and c["ownership_supported_left"] and c["ownership_supported_right"] for c in row["eight_paired_comparisons"].values())


def reference(data, name, pointer):
    return {"path": data["_paths"][name], "sha256": data["_hashes"][name], "json_pointer": pointer}


def build(data, fixture=False):
    validate_metadata(data)
    need(data["_pair_boards"] == validate_index(data), "Actual pair-board mapping changed")
    if not fixture:
        need(set(FROZEN_EVIDENCE_PINS) == {"reader_A", "reader_B", "final_review"}, "Actual production evidence not frozen")
        need(all(data["_hashes"].get(n) == pin for n, (_, pin) in FROZEN_EVIDENCE_PINS.items()), "Unregistered scientific evidence hash")
    parsed = {name: report_rows(data, name, final=name == "final_review") for name in ("reader_A", "reader_B", "final_review")}
    fresh = all(data[name]["prior_exposure"]["historical_feature_or_outcome_claims_seen"] is False and data[name]["prior_exposure"]["other_initial_reader_report_seen"] is False for name in ("reader_A", "reader_B"))
    output = []
    for queued in data["queue"]["ordered_queue"]:
        row = {**queued, "inspection_status": "NOT_INSPECTED"}
        if queued["ordinal"] <= 64:
            names = ("reader_A", "reader_B", "final_review")
            observations = [parsed[n][1][queued["pair_id"]][1] for n in names]
            common = set.intersection(*(visible_difference_keys(r, parsed[n][0]) for n, r in zip(names, observations)))
            repeat = fresh and all(full_repeat(r, parsed[n][0]) for n, r in zip(names, observations))
            # Shared positively supported local facts survive unrelated whole-
            # pair uncertainty. Raw category disagreements remain in sources.
            difference = fresh and bool(common)
            outcome = REPEAT if repeat else DIFFERENCE if difference else UNCERTAIN
            sources = {}
            for name, observation in zip(names, observations):
                index = parsed[name][1][queued["pair_id"]][0]
                local = [{"feature": f, "difference_kind": c["difference_kind"], "relevant_feature_reference": reference(data, name, f"/pair_observations/{index}/eight_paired_comparisons/{f}")} for f, c in observation["eight_paired_comparisons"].items() if c["relation"] == "OBSERVED_DIFFERENCE"]
                sources[name] = {"reference": reference(data, name, f"/pair_observations/{index}"), "candidate_outcome": observation["candidate_outcome"], "local_observed_differences": local, "significant_variation": observation["significant_variation"], "remaining_uncertainty": observation["remaining_uncertainty"]}
            row.update(inspection_status="CHECKED_BY_TWO_SOURCE_READERS_AND_FINAL_AI", source_observation=outcome, common_visible_difference_features=[{"feature": f, "difference_kind": k} for f, k in sorted(common)] if difference else [], source_reports=sources, cipher_identity="UNKNOWN", allographic_significance="UNKNOWN")
        output.append(row)
    counts = {category: sum(r.get("source_observation") == category for r in output) for category in (REPEAT, DIFFERENCE, UNCERTAIN)}
    return {"schema": "source257-direct772-checkpoint-v1", "purpose": "SYNTHETIC_FIXTURE_ONLY" if fixture else "SOURCE_ATTESTED_PAIR_OBSERVATIONS_NO_GRAPH_UPDATE", "input_sha256": data["_hashes"], "code_sha256": data["_code_sha256"], "queue_reference": reference(data, "queue", "/ordered_queue"), "baseline_reuse": {"canonical": {"path": PUBLIC_PINS["baseline"][0], "sha256": PUBLIC_PINS["baseline"][1]}, "graph_and_307_sequence": "REUSED_UNCHANGED_NO_TRANSITIVE_UPDATE_NO_REVALIDATION"}, "pairs": output, "checkpoint": {"queue_count": 772, "completed_prefix": 64, "last_completed_pair": data["queue"]["ordered_queue"][63]["pair_id"], "not_inspected": 708, "next_ordinal": 65, "next_pair": data["queue"]["ordered_queue"][64]["pair_id"], "actual_coverage_by_report": {n: {"pairs": len(data[n]["coverage"]["actual_pair_ids_viewed"]), "targets": len(data[n]["coverage"]["actual_target_ids_inspected"]), "boards": len(data[n]["coverage"]["actual_board_ids_viewed"])} for n in parsed}, "checked_source_observation_counts": counts, "stop_reason": "PREDECLARED_BATCH_CAPACITY64_REMAINDER_AUTHORIZED_AND_AVAILABLE_NOT_EVALUATED"}, "provenance_limit": "PINNED_AI_SOURCE_ATTESTATIONS_NO_CURRENT_JPEG_OR_PRIVATE_PROOF_READ_NO_MECHANICAL_TARGET_BINDING_PROOF", "semantic_limits": "NO_CIPHER_CANNOT_LINK_NO_ALPHABET_NO_LETTERS_NO_GLOBAL_READING_ORDER_NO_TRANSITIVE_GRAPH_UPDATE"}


def queue_tsv(result):
    stream = io.StringIO(newline="")
    stream.write("# PAIR_INSPECTION_CHECKPOINT_NOT_CIPHER_RELATIONS; REMAINDER_NOT_INSPECTED_HAS_NO_SOURCE_VERDICT\n")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(("ordinal", "pair_id", "left_id", "right_id", "inspection_status", "source_observation"))
    for row in result["pairs"]:
        writer.writerow((row["ordinal"], row["pair_id"], *row["member_ids"], row["inspection_status"], row.get("source_observation", "")))
    return stream.getvalue()


def verify_unchanged(protected):
    for name, (path, pin) in protected.items():
        need(digest(path.read_bytes()) == pin, "Protected bytes changed: " + name)


def write_once(output, value, protected, text=False):
    output = Path(output).absolute()
    need(not output.exists() and not output.is_symlink(), "Output exists/aliases input/hardlink/symlink")
    need(output.parent.exists() and output == output.resolve(), "Output parent missing or traverses symlink")
    need(output.resolve() not in {p.resolve() for p, _ in protected.values()}, "Output aliases input")
    verify_unchanged(protected)
    fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(value if text else json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        verify_unchanged(protected)
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def write_production(output, result, protected):
    need(result["purpose"] != "SYNTHETIC_FIXTURE_ONLY" and set(FROZEN_EVIDENCE_PINS) == {"reader_A", "reader_B", "final_review"}, "Synthetic/unknown reports cannot authorize production write")
    need(all(result["input_sha256"].get(n) == pin for n, (_, pin) in FROZEN_EVIDENCE_PINS.items()), "Production report hashes not registered")
    write_once(output, result, protected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, default=STAGE / "results")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--queue-tsv", type=Path)
    args = parser.parse_args()
    data, protected = load(args.repository_root, args.input_directory)
    result = build(data)
    from check_direct772_checkpoint import check
    receipt = check(result, data)
    write_production(args.output, result, protected)
    if args.queue_tsv:
        protected["written_checkpoint"] = (args.output, digest(args.output.read_bytes()))
        write_once(args.queue_tsv, queue_tsv(result), protected, True)
    print(json.dumps({"status": "WRITTEN", "sha256": digest(args.output.read_bytes()), "checkpoint": receipt}, sort_keys=True))


if __name__ == "__main__":
    main()
