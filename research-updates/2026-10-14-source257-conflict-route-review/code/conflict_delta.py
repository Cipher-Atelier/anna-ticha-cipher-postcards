#!/usr/bin/env python3
"""Source257 bounded conflict delta, JSON-only and Python3.10 standard library.

Readers use the separately frozen source-reader-output-format-v1.json. Production
evidence bindings grow only when actual initial/audit/final reports are frozen;
no arbitrary caller-supplied final hash can authorize a scientific output.
Historical audit format: correction_claims[{claim_id,target_ids,old_fact_reference:
{artifact_sha256,json_pointer},old_literal,corrected_source_fact,
new_source_fact_refs:[{reader:A|B,json_pointer}],native_locator_boxes,
source_context_ids,dependent_edge_claims:[{pair_id,accepted_edge_evidence_reference,
fact_dependency_grounds}]}]. Final format: pair_reviews (same paired-comparison
shape as initial, candidate_outcome), correction_reviews[{claim_id,decision:
SUPPORTED_SOURCE_FACT_CORRECTION|UNRESOLVED_OR_REPEATED_DISAGREEMENT,grounds}],
quarantine_reviews[{pair_id,claim_id,decision:QUARANTINE_EXACT_DEPENDENT_EDGE|
RETAIN_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT,grounds}]. All post-initial reports pin
both initial file hashes; final pins both historical-audit hashes as well.

Safe-write and maximal-clique routines adapted from D12 spatial_preparation.py
SHA256 cc55ec0c89bbfc2ddd087b4b8a0dc4fdd4d2674bf29ddde50534e4320ecc6b52.
No JPEG, private pixel-proof, or conditional772 source work is performed here.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import itertools
import json
import os
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
BASELINE_PATH = "research-updates/2026-10-14-source257-repeat-sequence/data/canonical-repeat-evidence-v1.json"
BASELINE_SHA = "5083d313a78796ac32f21f71d93b9b53b230874782f8a4558324b12d7e2d8348"
INPUT_PINS = {
    "protocol": ("conflict-route-protocol-v1.json", "554f461bcf6a210b3bb91da3a36b78042410649083840002413f0bcc82d388dc"),
    "safe_protocol": ("source-observation-protocol-v1.json", "e17e2c6d026061ed5f0ced2488ff5ddca881ed433e8e8ea2fd36f2cf9c99750e"),
    "intake": ("judge-source-geometry-intake-v1.json", "5f755122a874c6b6d036d540f9bcdcfb9b976c27eebbd37e2621bd5f24bb20b7"),
    "format": ("source-reader-output-format-v1.json", "f4b01c4d83d62e035f05a0d67a7ed83e59ec95ff8e6ea377077c426d2ca19138"),
    "audit_format": ("historical-audit-output-format-v1.json", "13429c28449eb79c20da7e355d3a2b798b8072a25eb3dbee13282eef36b985e0"),
    "final_format": ("final-ai-output-format-v1.json", "8f8fbe14d69742bde90f9a4bde10e9fa1648489c8bcf37eff878eaf3c93a1ab1"),
    "dependency_format_addendum": ("format-clarification-addendum-v1.json", "46dce07c66f6fca550a01c50fab12100e2dce3397f8084b57998dce7f4a5b3bf"),
}
BOARD_PIN = ("pair-context-pack-v1/pair-index-v1.json", "9d23148b57a02d2f86e92379e3006887d560aa867e789942b2fff75ba7a0c18c")
FROZEN_EVIDENCE_PINS = {
    "reader_A": ("source-reader-A-initial-v1.json", "d198a1afbc883d908f986359c574f7efec9ccd1513d391a6e0ea8bf3ed145215"),
    "reader_B": ("source-reader-B-initial-v1.json", "1e37a9ade8e23035dd76c0e00d1e74366eb6eef81ebba54eaeea6d4c1104f599"),
    "historical_claims": ("relevant-historical-claims-v1.json", "3a892b8661c6ca89f403e567e4ee3c31c3ac64d0c2f4e758c9712cd0566aece9"),
    "history_A": ("source-reader-A-historical-audit-v1.json", "4693e0df900dc4f004f03888e1513672ba5aeca26610cf9b2a1a6ad6cca274b0"),
    "history_B": ("source-reader-B-historical-audit-v1.json", "31f7b8788e8d90c9035e7879bc64b1568a842d46a0a1e6e47288915cbe8857a2"),
    "final_review": ("conflict-route-final-ai-v1.json", "f267c434acf59b2f2ebc63e880928a236a2d053edf918d31462c5ace1874bb00"),
}  # Historical/final reports must be explicitly added only after actual freeze.
FIELDS = ("path_topology", "enclosures", "openings", "stem_pattern", "attached_bars", "connected_extra_strokes", "terminal_pattern", "owned_mark_profile")
SAME = "SAME_FULL_VISIBLE_FEATURE_CANDIDATE"
DIFFERENT = "DIFFERENT_FULL_VISIBLE_GRAPHICS"
VARIATION = "VISIBLE_VARIATION_RELATION_UNRESOLVED"
BINDING = "CONNECTION_OR_BINDING_UNRESOLVED"
OUTCOMES = {SAME, DIFFERENT, VARIATION, BINDING}
INVARIANTS = {"TOPOLOGY", "ENCLOSURE", "ATTACHMENT", "TERMINAL_PRESENCE"}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def literal(value):
    require(isinstance(value, str) and bool(value.strip()), "Concrete source statement missing")


def concrete(value):
    literal(value)
    upper = value.strip().upper()
    require(upper not in {"UNKNOWN", "UNRESOLVED", "NONE", "N/A", "?", "*", "SAME"} and not upper.startswith(("UNKNOWN ", "UNRESOLVED ", "NOT VISIBLE")), "Unknown source information cannot be treated as a supported fact/absence")


def timestamp(value):
    literal(value)
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "Freeze timestamp must declare timezone")
    return parsed


def get_pointer(value, pointer):
    require(isinstance(pointer, str) and pointer.startswith("/"), "Absolute JSON pointer required")
    for component in pointer[1:].split("/"):
        component = component.replace("~1", "/").replace("~0", "~")
        value = value[int(component)] if isinstance(value, list) else value[component]
    return value


def pair_id(members):
    require(isinstance(members, list) and len(members) == 2 and members == sorted(set(members)), "Pair IDs must be sorted and distinct")
    return "--".join(members)


def exact_rows(rows, ids, field, label):
    require(isinstance(rows, list), label + " must be a list")
    mapping = {}
    for index, row in enumerate(rows):
        ident = row[field]
        require(ident not in mapping, label + " duplicate ID")
        mapping[ident] = (index, row)
    require(set(mapping) == set(ids) and len(rows) == len(ids), label + " fixed scope mismatch")
    return mapping


def load(repository_root, input_directory=STAGE / "results"):
    repository_root, input_directory = Path(repository_root).resolve(), Path(input_directory).resolve()
    specs = {"baseline": (repository_root / BASELINE_PATH, BASELINE_SHA)}
    specs.update({n: (input_directory / f, h) for n, (f, h) in {**INPUT_PINS, **FROZEN_EVIDENCE_PINS}.items()})
    specs["board_index"] = (input_directory.parent / BOARD_PIN[0], BOARD_PIN[1])
    data, protected = {}, {}
    for name, (path, expected) in specs.items():
        require(not path.is_symlink(), "Input symlink rejected")
        raw = path.read_bytes()
        require(sha(raw) == expected, "Immutable input SHA mismatch: " + name)
        data[name], protected[name] = json.loads(raw), (path, expected)
    data["_hashes"] = {n: h for n, (_, h) in protected.items()}
    data["_repository_root"] = repository_root
    data["_protected"] = protected
    data["_pair_boards"] = validate_board_index(data)
    return data, protected


def validate_board_index(data):
    profiles = profile_map(data)
    expected_pairs = set(data["protocol"]["fixed_pair_ids"])
    require(data["board_index"]["intake_whole_file_sha256"] == data["_hashes"]["intake"] and data["board_index"]["source_size"] == data["intake"]["source_size"] and data["board_index"]["scale"] == 1, "Paired index input/size/scale changed")
    require(set(profiles) == set(data["protocol"]["fixed_profile_ids"]) and len(data["intake"]["profiles"]) == 29, "Safe geometry exact29 scope mismatch")
    require({p["pair_id"] for p in data["intake"]["pairs"]} == expected_pairs and len(data["intake"]["pairs"]) == 38, "Safe intake exact38 pair scope mismatch")
    result = {pair: [] for pair in expected_pairs}
    for board in data["board_index"]["boards"]:
        for key in board["pair_ids"]:
            require(key in result and board["board_id"] not in result[key], "Board scope or duplicate pair invalid")
            result[key].append(board["board_id"])
            panels = [p for p in board["panels"] if p["pair_id"] == key]
            require(len(panels) == 4 and {(p["id"], p["window_kind"]) for p in panels} == {(ident, kind) for ident in key.split("--") for kind in ("TIGHT", "CONTEXT")}, "Board must contain actual tight/context panels for both IDs")
            for panel in panels:
                target = profiles[panel["id"]]
                window = target["windows"][panel["window_kind"]]
                require(panel["context_id"] == window["context_id"] and panel["native_bbox_xyxy_halfopen"] == window["native_bbox_xyxy_halfopen"] and panel["rotation_degrees_clockwise"] == target["rotation_degrees_clockwise"], "Board target/native geometry/frame differs from safe intake")
    require(all(result.values()), "Actual board index omits a required pair")
    return result


def verify_unchanged(protected):
    for name, (path, expected) in protected.items():
        require(sha(path.read_bytes()) == expected, "Input changed during operation: " + name)


def write_once(output, value, protected, *, text=False):
    output = Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), "Output exists or aliases an input/hardlink/symlink")
    require(output.parent.exists() and output == output.resolve(), "Output parent missing or traverses symlink")
    require(output.resolve() not in {p.resolve() for p, _ in protected.values()}, "Output aliases an input")
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


def profile_map(data):
    return {p["id"]: p for p in data["intake"]["profiles"]}


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def coordinates(data, ident, boxes, *, target=True):
    require(isinstance(boxes, list) and bool(boxes), "Native source locators missing")
    profile = profile_map(data)[ident]
    w, h = data["intake"]["source_size"]
    context = profile["windows"]["CONTEXT"]["native_bbox_xyxy_halfopen"]
    for box in boxes:
        require(isinstance(box, list) and len(box) == 4 and all(type(n) is int for n in box), "Native box must be four integers")
        x0, y0, x1, y1 = box
        require(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h, "Native box outside source")
        require(context[0] <= x0 < x1 <= context[2] and context[1] <= y0 < y1 <= context[3], "Locator outside target source context")
        if target:
            require(intersects(box, profile["approved_target_bbox"]), "Locator refers to neighboring context rather than target search window")


def context_ids(data, ids, references, *, complete=False):
    require(isinstance(references, list) and bool(references), "Source context references missing")
    allowed = {view["context_id"] for ident in ids for view in profile_map(data)[ident]["windows"].values()}
    require(set(references) <= allowed and len(references) == len(set(references)), "Unknown or wrong-target context reference")
    if complete:
        require(set(references) == allowed, "Complete tight+context source references required")


def contextual_witnesses(data, ids, boxes):
    """Historical/addendum witnesses may include a competing neighboring route."""
    require(ids and isinstance(boxes, list) and boxes, "Historical source witness scope missing")
    for box in boxes:
        valid = False
        for ident in ids:
            try:
                coordinates(data, ident, [box], target=False)
                valid = True
                break
            except ValueError:
                pass
        require(valid, "Historical witness lies outside every named target's source context")


def require_pins(data, report, expected):
    for key, name in expected.items():
        require(report["input_pins"].get(key) == data["_hashes"][name], "Report input pin mismatch: " + key)


def source_only(report):
    exposure = report["prior_exposure"]
    return exposure["historical_feature_or_outcome_claims_seen"] is False and exposure["other_initial_reader_report_seen"] is False


def validate_target_facts(data, targets):
    geometry = profile_map(data)
    for ident, (_, target) in targets.items():
        require(target["approved_target_native_bbox_xyxy_halfopen"] == geometry[ident]["approved_target_bbox"], "Approved target locator changed")
        expected_frame = "EXACT90CW" if geometry[ident]["rotation_degrees_clockwise"] == 90 else "NATIVE0"
        require(target["frame"] == expected_frame, "Source frame/sign mismatch")
        context_ids(data, [ident], target["source_context_ids"], complete=True)
        literal(target["full_route_description"])
        require(target["binding_state"] in {"SUPPORTED_TARGET_ROUTE", BINDING}, "Target binding state invalid")
        require(target["cipher_identity"] == target["letter_value"] == "UNKNOWN", "Cipher identity/letter inferred")
        require(set(target["eight_features"]) == set(FIELDS), "Missing target feature dimension")
        for feature in target["eight_features"].values():
            literal(feature["observation"])
            require(feature["certainty"] in {"SOURCE_SUPPORTED", "UNRESOLVED"}, "Feature certainty invalid")
            require(type(feature["absence_claim"]) is bool and feature["relevant_route_visibility"] in {"FULL", "UNRESOLVED"}, "Absence/visibility field invalid")
            coordinates(data, ident, feature["native_locator_boxes"])
            context_ids(data, [ident], feature["source_context_ids"])
            if feature["certainty"] == "SOURCE_SUPPORTED":
                concrete(feature["observation"])
            if feature["absence_claim"]:
                require(feature["certainty"] == "SOURCE_SUPPORTED" and feature["relevant_route_visibility"] == "FULL", "Unknown/partial route cannot prove absence")
        for field in ("free_end_observations", "bar_return_junctions", "competing_routes"):
            require(isinstance(target[field], list), "Route-element list missing")
            for element in target[field]:
                require(element["ownership"] in {"TARGET_ROUTE", "NEIGHBOR_ROUTE", "UNRESOLVED"} and element["actual_visibility"] in {"FULL", "UNRESOLVED"}, "Route ownership/visibility invalid")
                coordinates(data, ident, element["native_locator_boxes"], target=element["ownership"] == "TARGET_ROUTE")
                context_ids(data, [ident], element["source_context_ids"])
                literal(element["continuity_source_witness"])
                require(isinstance(element["neighbor_ids"], list), "Competing neighbor IDs missing")
                neighbor_ids = {r["id"] for r in geometry[ident]["windows"]["CONTEXT"]["intersecting_annotations"]} - {ident}
                require(set(element["neighbor_ids"]) <= neighbor_ids, "Neighbor ID lies outside this source context")


def validate_initial(data, name):
    report = data[name]
    require(report["schema"] == "source257-conflict-route-reader-initial-v1" and report["phase"] == "INITIAL_SOURCE_ONLY_FROZEN", "Initial reader phase/schema invalid")
    literal(report["reader"])
    require("/" not in report["reader"] and "\\" not in report["reader"], "Reader label must not contain operational paths")
    literal(report["frozen_utc"])
    require_pins(data, report, {"safe_protocol_sha256": "safe_protocol", "safe_intake_sha256": "intake", "context_index_sha256": "board_index", "output_format_sha256": "format"})
    protocol = data["protocol"]
    require(report["original_source_pins"] == {"encoded_sha256": protocol["input_sha256"]["source_encoded"], "rgb_sha256": protocol["input_sha256"]["source_RGB"]}, "Whole-original source pins mismatch")
    proof = report["whole_private_proof_json_sha256"]
    require(isinstance(proof, str) and len(proof) == 64 and all(c in "0123456789abcdef" for c in proof), "Whole proof JSON hash missing")
    literal(report["prior_exposure"]["details"])
    require(all(type(report["prior_exposure"][key]) is bool for key in ("geometry_and_cohort_selection_seen", "historical_feature_or_outcome_claims_seen", "other_initial_reader_report_seen")), "Prior exposure must be disclosed as booleans")
    pairs, ids = protocol["fixed_pair_ids"], protocol["fixed_profile_ids"]
    require(len(pairs) == 38 and len(ids) == 29, "Protocol fixed38/29 scope changed")
    require(len(report["actual_pair_ids_viewed"]) == len(set(report["actual_pair_ids_viewed"])) == 38 and set(report["actual_pair_ids_viewed"]) == set(pairs), "Actual paired-view coverage not exact38")
    targets = exact_rows(report["target_observations"], ids, "id", name + " target facts")
    validate_target_facts(data, targets)
    rows = exact_rows(report["pair_observations"], pairs, "pair_id", name + " paired observations")
    for key, (_, row) in rows.items():
        require(pair_id(row["member_ids"]) == key and row["coverage"] == "DIRECT_NATIVE_PAIRED_SOURCE_INSPECTION", "Incorrect pair binding or actual direct coverage")
        require(row["actual_native_board_id"] in data["_pair_boards"][key], "Pair source board does not contain this pair")
        require(row["candidate_outcome"] in OUTCOMES and row["cipher_identity"] == row["letter_value"] == "UNKNOWN", "Outcome/semantic limit invalid")
        require(isinstance(row["significant_variation"], list) and isinstance(row["remaining_uncertainty"], list), "Variation/uncertainty list missing")
        validate_paired_features(data, report, row, targets)
    return targets, rows


def validate_paired_features(data, report, row, targets):
    checks = row["eight_paired_comparisons"]
    require(set(checks) == set(FIELDS), "Paired comparison missing one of eight dimensions")
    for field, comparison in checks.items():
        literal(comparison["paired_source_grounds"])
        require(comparison["relation"] in {"SUPPORTED_COMPATIBLE", "POSITIVELY_INCOMPATIBLE", "UNRESOLVED"}, "Paired relation invalid")
        require(comparison["incompatibility_kind"] in INVARIANTS | {"UNVALIDATED_VARIATION", "NONE"}, "Incompatibility kind invalid")
        context_ids(data, row["member_ids"], comparison["source_context_ids"], complete=True)
        for side, ident in zip(("left", "right"), row["member_ids"]):
            pointer = comparison[side + "_target_feature_ref"]
            expected = f"/target_observations/{targets[ident][0]}/eight_features/{field}"
            require(pointer == expected and get_pointer(report, pointer) == targets[ident][1]["eight_features"][field], "Paired feature reference bound to wrong target/field")
            coordinates(data, ident, comparison["native_locator_boxes_" + side])
            require(comparison["relevant_visibility_" + side] in {"FULL", "UNRESOLVED"} and type(comparison["ownership_supported_" + side]) is bool, "Paired visibility/ownership missing")


def complete_gate(row, targets):
    for ident in row["member_ids"]:
        target = targets[ident][1]
        if target["binding_state"] != "SUPPORTED_TARGET_ROUTE":
            return False
        if any(f["certainty"] != "SOURCE_SUPPORTED" or f["relevant_route_visibility"] != "FULL" for f in target["eight_features"].values()):
            return False
        if any(e["ownership"] == "UNRESOLVED" or e["actual_visibility"] != "FULL" for key in ("free_end_observations", "bar_return_junctions", "competing_routes") for e in target[key]):
            return False
    return all(f["relevant_visibility_left"] == f["relevant_visibility_right"] == "FULL" and f["ownership_supported_left"] and f["ownership_supported_right"] for f in row["eight_paired_comparisons"].values())


def supports(row, targets, outcome):
    if row["candidate_outcome"] != outcome:
        return False
    if outcome == SAME:
        return complete_gate(row, targets) and not row["remaining_uncertainty"] and all(c["relation"] == "SUPPORTED_COMPATIBLE" and c["incompatibility_kind"] == "NONE" for c in row["eight_paired_comparisons"].values())
    return outcome == DIFFERENT and bool(difference_invariants(row, targets))


def difference_invariants(row, targets):
    supported = set()
    for field, comparison in row["eight_paired_comparisons"].items():
        if comparison["relation"] != "POSITIVELY_INCOMPATIBLE" or comparison["incompatibility_kind"] not in INVARIANTS:
            continue
        visible_owned = True
        for side, ident in zip(("left", "right"), row["member_ids"]):
            target = targets[ident][1]
            feature = target["eight_features"][field]
            visible_owned &= target["binding_state"] == "SUPPORTED_TARGET_ROUTE" and feature["certainty"] == "SOURCE_SUPPORTED" and feature["relevant_route_visibility"] == "FULL" and comparison["relevant_visibility_" + side] == "FULL" and comparison["ownership_supported_" + side]
        if visible_owned:
            supported.add((field, comparison["incompatibility_kind"]))
    return supported


def cliques(nodes, edges):
    neighbors = {n: set() for n in nodes}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    result = []
    def search(selected, possible, excluded):
        if not possible and not excluded:
            if len(selected) > 1:
                result.append(tuple(sorted(selected)))
            return
        pivot = max(possible | excluded, key=lambda n: len(possible & neighbors[n]), default=None)
        for node in sorted(possible - neighbors[pivot] if pivot else possible.copy()):
            search(selected | {node}, possible & neighbors[node], excluded & neighbors[node])
            possible.remove(node)
            excluded.add(node)
    search(set(), set(nodes), set())
    return [{"id": "GSET-" + canonical_sha(list(members))[:16], "member_ids": list(members), "edge_witness_pair_ids": sorted("--".join(p) for p in itertools.combinations(members, 2)), "membership_semantics": "SET_NOT_ALPHABET_PARTITION"} for members in sorted(result)]


def raw_ref(data, name, pointer):
    return {"input": name, "sha256": data["_hashes"][name], "json_pointer": pointer}


def old_fact(data, reference):
    """Resolve only declared baseline JSON inputs, checking selected public bytes."""
    identity = reference["artifact_sha256"]
    baseline = data["baseline"]
    candidates = [(name, binding) for name, binding in baseline["input_bindings"].items() if binding["sha256"] == identity]
    require(len(candidates) == 1, "Historical source identity not uniquely bound by frozen baseline")
    name, binding = candidates[0]
    selected = baseline.get("public_selection_bindings", {}).get("inputs", {}).get(name, {})
    expected = selected.get("selected_whole_file_sha256", identity)
    relative = Path(binding["path"])
    require(not relative.is_absolute() and ".." not in relative.parts and relative.suffix == ".json", "Historical reference must be declared portable JSON")
    path = data["_repository_root"] / relative
    require(not path.is_symlink(), "Historical input symlink rejected")
    raw = path.read_bytes()
    require(sha(raw) == expected, "Historical selected input SHA mismatch")
    data["_protected"]["historical_" + name] = (path, expected)
    return get_pointer(json.loads(raw), reference["json_pointer"])


def correction_source_support(data, reference):
    report = data["reader_" + reference["reader"]]
    parts = reference["json_pointer"].split("/")
    target = report["target_observations"][int(parts[2])]
    if parts[3] == "eight_features" and len(parts) >= 5:
        feature = target["eight_features"][parts[4]]
        return target["binding_state"] == "SUPPORTED_TARGET_ROUTE" and feature["certainty"] == "SOURCE_SUPPORTED" and feature["relevant_route_visibility"] == "FULL"
    if parts[3] == "full_route_description":
        feature = target["eight_features"]["path_topology"]
        return target["binding_state"] == "SUPPORTED_TARGET_ROUTE" and feature["certainty"] == "SOURCE_SUPPORTED" and feature["relevant_route_visibility"] == "FULL"
    if parts[3] in {"free_end_observations", "bar_return_junctions", "competing_routes"} and len(parts) >= 5:
        element = target[parts[3]][int(parts[4])]
        return element["ownership"] in {"TARGET_ROUTE", "NEIGHBOR_ROUTE"} and element["actual_visibility"] == "FULL"
    return False


def validate_history(data, name):
    report = data[name]
    require(report["schema"] == "source257-conflict-route-historical-audit-v1" and report["phase"] == "POST_BOTH_INITIAL_FREEZES_HISTORICAL_AUDIT", "Historical audit is not a separate post-initial addendum")
    literal(report["reader"])
    require("/" not in report["reader"] and "\\" not in report["reader"], "Historical reader label must be safe")
    require(timestamp(report["frozen_utc"]) >= max(timestamp(data[n]["frozen_utc"]) for n in ("reader_A", "reader_B")), "Historical result freeze precedes both initial freezes")
    exposure = report["exposure"]
    require(exposure["own_initial_report_read"] is True and exposure["compact_historical_claims_read"] is True and type(exposure["other_initial_report_read"]) is bool, "Historical exposure disclosures missing")
    literal(exposure["details"])
    require_pins(data, report, {"baseline_sha256": "baseline", "reader_A_sha256": "reader_A", "reader_B_sha256": "reader_B"})
    require_pins(data, report, {"audit_output_format_sha256": "audit_format", "historical_claims_sha256": "historical_claims"})
    label = "A" if name == "history_A" else "B"
    own_report = data["reader_" + label]
    targets = exact_rows(report["target_audit_records"], data["protocol"]["fixed_profile_ids"], "id", "Historical exact29 target audit coverage")
    pair_rows = exact_rows(report["pair_audit_records"], data["protocol"]["fixed_pair_ids"], "pair_id", "Historical exact38 pair audit coverage")
    for ident, (_, row) in targets.items():
        require(row["status"] in {"NO_CONFIRMED_LITERAL_CORRECTION", "SOURCE_FACT_CORRECTION_CLAIMED", "SUPPORT_QUALIFICATION_ONLY", "SOURCE_UNRESOLVED"}, "Target audit status invalid")
        literal(row["grounds"])
        require(isinstance(row["claim_ids"], list) and isinstance(row["support_qualification_ids"], list), "Target audit claim links missing")
        require(isinstance(row["own_initial_source_fact_refs"], list) and row["own_initial_source_fact_refs"], "Target audit must cite its own source facts")
        for pointer in row["own_initial_source_fact_refs"]:
            require(pointer.startswith("/target_observations/"), "Target audit must cite own source facts")
            require(own_report["target_observations"][int(pointer.split("/")[2])]["id"] == ident, "Target audit cites another target's source fact")
            get_pointer(own_report, pointer)
    for key, (_, row) in pair_rows.items():
        require(pair_id(row["member_ids"]) == key and row["status"] in {"NO_CONFIRMED_CORRECTION", "CORRECTION_AFFECTS_COMPARISON", "SUPPORT_QUALIFICATION_ONLY", "SOURCE_UNRESOLVED"}, "Pair historical audit scope/status invalid")
        require(get_pointer(own_report, row["own_initial_pair_ref"])["pair_id"] == key, "Pair audit points to another initial pair")
        literal(row["grounds"])
    claims = {}
    for index, claim in enumerate(report["correction_claims"]):
        ident = claim["claim_id"]
        require(ident not in claims and set(claim["target_ids"]) <= set(data["protocol"]["fixed_profile_ids"]), "Historical correction scope/ID invalid")
        require(old_fact(data, claim["old_fact_reference"]) == claim["old_literal"], "Old literal differs from exact historical pointer")
        concrete(claim["corrected_source_fact"])
        require(claim["corrected_source_fact"] != claim["old_literal"], "Identical literal is not a factual correction")
        require({r["reader"] for r in claim["new_source_fact_refs"]} == {label} and claim["new_source_fact_refs"], "Historical audit cites only its own frozen initial source facts")
        for reference in claim["new_source_fact_refs"]:
            source_report = data["reader_" + reference["reader"]]
            pointer = reference["json_pointer"]
            parts = pointer.split("/")
            require(len(parts) >= 4 and parts[1] == "target_observations" and parts[3] in {"full_route_description", "eight_features", "free_end_observations", "bar_return_junctions", "competing_routes", "binding_state"}, "Correction must cite an actual fresh target source fact")
            require(source_report["target_observations"][int(parts[2])]["id"] in claim["target_ids"], "Correction cites another target's fact")
            value = get_pointer(source_report, pointer)
            require(value is not None, "Fresh source fact reference missing")
        contextual_witnesses(data, claim["target_ids"], claim["native_locator_boxes"])
        context_ids(data, claim["target_ids"], claim["source_context_ids"])
        claims[ident] = (index, claim)
    qualifications = {}
    for index, entry in enumerate(report["support_qualification_records"]):
        ident = entry["qualification_id"]
        require(ident not in qualifications and ident not in claims, "Duplicate historical qualification/claim ID")
        require(set(entry["target_ids"]) <= set(data["protocol"]["fixed_profile_ids"]) and set(entry["pair_ids"]) <= set(data["protocol"]["fixed_pair_ids"]), "Qualification exceeds fixed38/29 scope")
        require(entry["kind"] in {"OVERSTATEMENT_OF_CERTAINTY", "RETRACTION_OF_PREVIOUS_SOURCE_SUPPORT_CLAIM", "HISTORICAL_DISAGREEMENT_ONLY"}, "Support qualification kind invalid")
        require(old_fact(data, entry["old_fact_reference"]) == entry["old_literal"], "Qualification old literal differs from exact historical pointer")
        concrete(entry["qualification"])
        require(isinstance(entry["own_initial_source_fact_refs"], list) and entry["own_initial_source_fact_refs"], "Qualification must cite its own target source facts")
        for reference in entry["own_initial_source_fact_refs"]:
            pointer = reference["json_pointer"] if isinstance(reference, dict) else reference
            if isinstance(reference, dict):
                require(reference.get("reader") == label, "Qualification cannot cite another initial reader as own observation")
            require(pointer.startswith("/target_observations/"), "Qualification must cite own source target facts")
            require(own_report["target_observations"][int(pointer.split("/")[2])]["id"] in entry["target_ids"], "Qualification cites another target's source fact")
            get_pointer(own_report, pointer)
        contextual_witnesses(data, entry["target_ids"], entry["native_locator_boxes"])
        context_ids(data, entry["target_ids"], entry["source_context_ids"])
        qualifications[ident] = (index, entry)
    for _, row in targets.values():
        require(set(row["claim_ids"]) <= set(claims) and set(row["support_qualification_ids"]) <= set(qualifications), "Target audit cites unknown claim/qualification")
    for _, row in pair_rows.values():
        require(set(row["claim_ids"]) <= set(claims) and set(row["support_qualification_ids"]) <= set(qualifications), "Pair audit cites unknown claim/qualification")
    return claims, qualifications


def build(data):
    roles = {"reader_A", "reader_B", "history_A", "history_B", "historical_claims", "final_review", "board_index"}
    require(roles <= set(data), "Complete frozen initial reports, historical audits, final source audit and board index are required")
    fixture = data.get("_synthetic_fixture_only") is True
    require(data["_hashes"]["baseline"] == BASELINE_SHA and data["_hashes"]["board_index"] == BOARD_PIN[1], "Scientific baseline or paired-index identity changed")
    if not fixture:
        require(roles - {"board_index"} <= set(FROZEN_EVIDENCE_PINS), "Production evidence identities not yet frozen in this version")
        require(all(data["_hashes"][name] == FROZEN_EVIDENCE_PINS[name][1] for name in roles - {"board_index"}), "Production scientific input hash is not this version's frozen identity")
    a_targets, aa = validate_initial(data, "reader_A")
    b_targets, bb = validate_initial(data, "reader_B")
    audited = {name: validate_history(data, name) for name in ("history_A", "history_B")}
    histories = {name: result[0] for name, result in audited.items()}
    final = data["final_review"]
    require(final["schema"] == "source257-conflict-route-final-ai-v1", "Final source-audit schema invalid")
    literal(final["reviewer"])
    require("/" not in final["reviewer"] and "\\" not in final["reviewer"], "Final reviewer label must be safe")
    require(timestamp(final["frozen_utc"]) >= max(timestamp(data[n]["frozen_utc"]) for n in ("history_A", "history_B")), "Final result freeze precedes historical addenda")
    require_pins(data, final, {"protocol_sha256": "protocol", "baseline_sha256": "baseline", "reader_A_sha256": "reader_A", "reader_B_sha256": "reader_B", "historical_A_sha256": "history_A", "historical_B_sha256": "history_B"})
    require_pins(data, final, {"historical_claims_sha256": "historical_claims", "final_output_format_sha256": "final_format"})
    for key, name in (("geometry_intake_sha256", "intake"), ("paired_index_sha256", "board_index")):
        if key in final["input_pins"]:
            require(final["input_pins"][key] == data["_hashes"][name], "Final source geometry pin mismatch")
    require(final["conditioning"]["is_blind_agreement"] is False and final["conditioning"]["both_initials_read"] is True and final["conditioning"]["historical_addenda_read"] is True, "Final source audit must disclose historical/reader conditioning")
    literal(final["conditioning"]["details"])
    source = final["source_verification"]
    require(source["whole_original_encoded_sha256"] == data["protocol"]["input_sha256"]["source_encoded"] and source["whole_original_rgb_sha256"] == data["protocol"]["input_sha256"]["source_RGB"], "Final whole-source original pins mismatch")
    require(isinstance(source["whole_private_proof_json_sha256"], str) and len(source["whole_private_proof_json_sha256"]) == 64 and all(c in "0123456789abcdef" for c in source["whole_private_proof_json_sha256"]) and source["proof_before_view"] is True and source["target_binding_is_source_judgment"] is True, "Final source proof-before-view attestation missing")
    coverage = final["coverage"]
    require(coverage["scope"] == "FIXED38_ONLY" and len(coverage["actual_pair_ids_viewed"]) == 38 and set(coverage["actual_pair_ids_viewed"]) == set(data["protocol"]["fixed_pair_ids"]), "Final source audit actual pair coverage not exact38")
    require(len(coverage["actual_target_ids_inspected"]) == 29 and set(coverage["actual_target_ids_inspected"]) == set(data["protocol"]["fixed_profile_ids"]), "Final source audit target coverage not exact29")
    require(set(coverage["source_board_ids"]) == {board for ids in data["_pair_boards"].values() for board in ids}, "Final source audit board coverage missing")
    final_rows = exact_rows(final["pair_reviews"], data["protocol"]["fixed_pair_ids"], "pair_id", "Final source audit")
    # Final paired checks bind to its own exact source target observations.
    final_targets = exact_rows(final["target_observations"], data["protocol"]["fixed_profile_ids"], "id", "Final source target facts")
    validate_target_facts(data, final_targets)
    rows = []
    for key in data["protocol"]["fixed_pair_ids"]:
        ai, ar = aa[key]
        bi, br = bb[key]
        fi, fr = final_rows[key]
        require(pair_id(fr["member_ids"]) == key and fr["candidate_outcome"] in OUTCOMES, "Final pair scope/outcome invalid")
        require(fr["coverage"] == "DIRECT_NATIVE_PAIRED_SOURCE_INSPECTION" and fr["actual_native_board_id"] in data["_pair_boards"][key], "Final pair actual board/direct coverage missing")
        require(fr["cipher_identity"] == fr["letter_value"] == "UNKNOWN" and isinstance(fr["remaining_uncertainty"], list) and isinstance(fr["significant_variation"], list), "Final source uncertainty/semantic limits missing")
        validate_paired_features(data, final, fr, final_targets)
        same = source_only(data["reader_A"]) and source_only(data["reader_B"]) and all(supports(row, targets, SAME) for row, targets in ((ar, a_targets), (br, b_targets), (fr, final_targets)))
        different = source_only(data["reader_A"]) and source_only(data["reader_B"]) and all(supports(row, targets, DIFFERENT) for row, targets in ((ar, a_targets), (br, b_targets), (fr, final_targets)))
        if different:
            common = set.intersection(*(difference_invariants(row, targets) for row, targets in ((ar, a_targets), (br, b_targets), (fr, final_targets))))
            different = bool(common)
        status = "SOURCE_GATED_SAME_CANDIDATE" if same else "SOURCE_GATED_GRAPHICAL_DIFFERENCE_NOT_CANNOT_LINK" if different else "DEFERRED_BINDING" if BINDING in {ar["candidate_outcome"], br["candidate_outcome"], fr["candidate_outcome"]} else "DEFERRED_VARIATION"
        rows.append({"pair_id": key, "member_ids": ar["member_ids"], "status": status, "reader_A_outcome": ar["candidate_outcome"], "reader_B_outcome": br["candidate_outcome"], "final_AI_outcome": fr["candidate_outcome"], "reader_A_reference": raw_ref(data, "reader_A", f"/pair_observations/{ai}"), "reader_B_reference": raw_ref(data, "reader_B", f"/pair_observations/{bi}"), "final_AI_reference": raw_ref(data, "final_review", f"/pair_reviews/{fi}"), "uncertainty_preservation": "RAW_INITIAL_AND_FINAL_OBSERVATIONS_RETAINED_BY_EXACT_REFERENCE", "cipher_identity": "UNKNOWN"})
    corrections = []
    review_map = exact_rows(final["correction_reviews"], {k for claims in histories.values() for k in claims}, "claim_id", "Final correction audit")
    claim_lookup = {}
    for name, claims in histories.items():
        for claim_id, (index, claim) in claims.items():
            require(claim_id not in claim_lookup, "Correction claim IDs must be globally unique")
            claim_lookup[claim_id] = claim
            review_index, review = review_map[claim_id]
            require(review["decision"] in {"SUPPORTED_SOURCE_FACT_CORRECTION", "UNRESOLVED_OR_REPEATED_DISAGREEMENT"}, "Correction review decision invalid")
            for field in ("old_fact_reference", "old_literal"):
                if field in review:
                    require(review[field] == claim[field], "Final correction review cites a different historical literal/source")
            concrete(review["grounds"])
            contextual_witnesses(data, claim["target_ids"], review["native_locator_boxes"])
            context_ids(data, claim["target_ids"], review["source_context_ids"])
            if review["decision"] == "SUPPORTED_SOURCE_FACT_CORRECTION":
                require(all(correction_source_support(data, reference) for reference in claim["new_source_fact_refs"]), "Supported factual correction relies on unresolved or unowned fresh source facts")
            corrections.append({"claim_id": claim_id, "status": review["decision"], "historical_addendum_reference": raw_ref(data, name, f"/correction_claims/{index}"), "final_AI_reference": raw_ref(data, "final_review", f"/correction_reviews/{review_index}"), "accepted_scope": "FINAL_SOURCE_GROUNDS_AND_WITNESSES_ONLY_NOT_ENTIRE_UNQUALIFIED_PROPOSED_CLAIM", "source_statement_reference": raw_ref(data, "final_review", f"/correction_reviews/{review_index}/grounds")})
    qualification_refs = []
    qualification_scope = {ident for _, qualifications in audited.values() for ident in qualifications}
    qualification_reviews = exact_rows(final["qualification_reviews"], qualification_scope, "qualification_id", "Final support-qualification review")
    for name, (_, qualifications) in audited.items():
        for ident, (index, qualification) in qualifications.items():
            require(ident not in claim_lookup, "Historical IDs must be globally unique across both readers")
            claim_lookup[ident] = qualification
            review_index, review = qualification_reviews[ident]
            require(review["decision"] in {"SUPPORTED_SOURCE_SUPPORT_QUALIFICATION", "REPEATED_DISAGREEMENT_ONLY", "SOURCE_QUALIFICATION_UNRESOLVED"}, "Qualification review decision invalid")
            concrete(review["grounds"])
            for field in ("old_fact_reference", "old_literal"):
                if field in review:
                    require(review[field] == qualification[field], "Final qualification review cites a different historical literal/source")
            contextual_witnesses(data, qualification["target_ids"], review["native_locator_boxes"])
            context_ids(data, qualification["target_ids"], review["source_context_ids"])
            qualification_refs.append({"qualification_id": ident, "kind": qualification["kind"], "status": review["decision"], "historical_addendum_reference": raw_ref(data, name, f"/support_qualification_records/{index}"), "final_AI_reference": raw_ref(data, "final_review", f"/qualification_reviews/{review_index}"), "not_a_factual_opposite": True})
    baseline_edges = {e["pair_id"]: e for e in data["baseline"]["graph"]["positive_edges"]}
    expected_dependencies = set()
    for claim_id, claim in claim_lookup.items():
        for dependency in claim["dependent_edge_claims"]:
            key = dependency["pair_id"]
            require(key in baseline_edges and set(claim["target_ids"]) & set(baseline_edges[key]["member_ids"]), "Historical dependency lies outside exact incident accepted edges")
            require(dependency["accepted_edge_evidence_reference"] == baseline_edges[key]["evidence_reference"], "Historical dependency does not name the actual accepted edge authority")
            require((key, claim_id) not in expected_dependencies, "Duplicate historical dependency")
            expected_dependencies.add((key, claim_id))
    actual_dependencies = [(review["pair_id"], review.get("claim_id", review.get("qualification_id"))) for review in final["quarantine_reviews"]]
    require(len(actual_dependencies) == len(set(actual_dependencies)) and set(actual_dependencies) == expected_dependencies, "Final dependency audit coverage must be exact, including unsupported/unresolved claims")
    quarantined_by_edge, unresolved_dependencies, dependency_reviews = {}, [], []
    for index, review in enumerate(final["quarantine_reviews"]):
        key = review["pair_id"]
        claim_id = review.get("claim_id", review.get("qualification_id"))
        require(key in baseline_edges and claim_id in claim_lookup, "Quarantine extends beyond a referenced accepted baseline edge/correction")
        claim = claim_lookup[claim_id]
        factual = any(c["claim_id"] == claim_id and c["status"] == "SUPPORTED_SOURCE_FACT_CORRECTION" for c in corrections)
        qualification = any(q["qualification_id"] == claim_id and q["kind"] != "HISTORICAL_DISAGREEMENT_ONLY" and q["status"] == "SUPPORTED_SOURCE_SUPPORT_QUALIFICATION" for q in qualification_refs)
        dependencies = [c for c in claim["dependent_edge_claims"] if c["pair_id"] == key]
        require(len(dependencies) == 1 and set(claim["target_ids"]) & set(baseline_edges[key]["member_ids"]), "Quarantine has no exact incident source-fact dependency")
        require(dependencies[0]["accepted_edge_evidence_reference"] == baseline_edges[key]["evidence_reference"], "Quarantine does not cite the accepted edge's actual authority")
        concrete(dependencies[0]["fact_dependency_grounds"])
        require(review["decision"] in {"QUARANTINE_EXACT_DEPENDENT_EDGE", "RETAIN_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT", "DEFER_EXACT_DEPENDENCY"}, "Quarantine review decision invalid")
        concrete(review["grounds"])
        require(review["accepted_authority_effect"] in {"SOURCE_FACT_CONTRADICTED", "SPECIFIC_AUTHORITATIVE_SUPPORT_NOT_ESTABLISHED", "EXISTING_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT", "DEPENDENCY_SOURCE_SUPPORT_UNRESOLVED"}, "Exact accepted-authority impact assessment missing")
        reference = raw_ref(data, "final_review", f"/quarantine_reviews/{index}")
        dependency_reviews.append({"pair_id": key, "claim_id": claim_id, "decision": review["decision"], "accepted_authority_effect": review["accepted_authority_effect"], "final_AI_reference": reference})
        if review["decision"] == "QUARANTINE_EXACT_DEPENDENT_EDGE":
            require(factual or qualification, "Repeated disagreement alone cannot quarantine an accepted edge")
            require(review["accepted_authority_effect"] in {"SOURCE_FACT_CONTRADICTED", "SPECIFIC_AUTHORITATIVE_SUPPORT_NOT_ESTABLISHED"}, "Accounted-for/unresolved authority cannot be quarantined on that basis")
            quarantined_by_edge.setdefault(key, []).append({"claim_id": claim_id, "final_AI_reference": reference})
        elif review["decision"] == "RETAIN_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT":
            require(review["accepted_authority_effect"] == "EXISTING_FINAL_EVIDENCE_ACCOUNTS_FOR_FACT", "Retaining as accounted-for requires that exact final evidence finding")
        else:
            require(review["accepted_authority_effect"] == "DEPENDENCY_SOURCE_SUPPORT_UNRESOLVED", "Deferred dependency must explicitly remain unresolved")
            require_pins(data, final, {"dependency_format_addendum_sha256": "dependency_format_addendum"})
            unresolved_dependencies.append({"pair_id": key, "claim_id": claim_id, "status": "UNVALIDATED_INHERITED_AUTHORITY_NO_QUARANTINE", "final_AI_reference": reference})
    quarantines = [{"pair_id": key, "source_dependency_reviews": refs} for key, refs in sorted(quarantined_by_edge.items())]
    removed = {q["pair_id"] for q in quarantines}
    added = {r["pair_id"] for r in rows if r["status"] == "SOURCE_GATED_SAME_CANDIDATE"}
    require(not added & set(baseline_edges), "Fixed review scope must not redo accepted baseline edges")
    current = (set(baseline_edges) - removed) | added
    nodes = data["baseline"]["graph"]["node_ids"]
    groups = cliques(nodes, [key.split("--") for key in sorted(current)])
    return {"schema": "source257-conflict-route-delta-v1", "purpose": "SYNTHETIC_FIXTURE_ONLY" if fixture else "SOURCE_GATED_GRAPHICAL_DELTA_NOT_CIPHER_IDENTITIES", "baseline_reference": {"path": BASELINE_PATH, "sha256": BASELINE_SHA}, "input_sha256": data["_hashes"], "pair_dispositions": rows, "target_fact_references": [{"id": ident, "reader_A": raw_ref(data, "reader_A", f"/target_observations/{a_targets[ident][0]}"), "reader_B": raw_ref(data, "reader_B", f"/target_observations/{b_targets[ident][0]}"), "final_AI": raw_ref(data, "final_review", f"/target_observations/{final_targets[ident][0]}")} for ident in data["protocol"]["fixed_profile_ids"]], "correction_dispositions": corrections, "support_qualification_references": qualification_refs, "current_graph_overlay": {"baseline_historical_graph_unchanged": True, "added_positive_pair_ids": sorted(added), "quarantined_baseline_edges": quarantines, "unresolved_dependency_edges": unresolved_dependencies, "dependency_review_dispositions": dependency_reviews, "current_positive_pair_ids": sorted(current), "maximal_edge_complete_cliques": groups, "memberships_are_sets": True, "memberships": {n: sorted(g["id"] for g in groups if n in g["member_ids"]) for n in nodes}}, "conditional772": {"state": "NOT_EXECUTED_NO_ADMISSION_PRELOG", "additional_comparisons": 0, "scope_expansion_authorized_by_this_output": False}, "fixed_scope": {"review_pairs": 38, "review_targets": 29, "eligible_profiles": 70, "excluded_whole": 102, "unresolved_records": 135, "annotation_refs": 307}, "source_provenance": "PINNED_SOURCE_READER_AND_FINAL_AI_ATTESTATIONS_NO_CURRENT_JPEG_OR_PRIVATE_PROOF_READ_NO_MECHANICAL_TARGET_BINDING_PROOF", "semantic_limits": "NO_ALPHABET_PARTITION_NO_CIPHER_CANNOT_LINK_NO_LETTERS_NO_NEW_READING_ORDER"}


def current_sequence_tsv(delta, baseline):
    columns = ("region", "display_rank", "id", "inherited_order", "base_bbox", "full_feature_label_status", "candidate_graph_membership_ids", "repeat_status", "sequence_length", "cipher_unit_identity")
    stream = io.StringIO(newline="")
    stream.write("# ANNOTATION_RECORDS_NOT_GLYPHS; DISPLAY_ONLY_NOT_READING; UNKNOWN_LENGTH; BASELINE_SOURCE_GEOMETRY_UNCHANGED\n")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(columns)
    for region in baseline["spatial"]["regions"]:
        for row in region["records"]:
            membership = delta["current_graph_overlay"]["memberships"].get(row["id"], [])
            status = "POSITIVE_GRAPH_MEMBERSHIPS_ONLY_CIPHER_EQUIVALENCE_UNKNOWN" if membership else "UNKNOWN_REPEAT_EQUIVALENCE"
            writer.writerow((region["region"], row["display_rank"], row["id"], row["inherited_order_value"], json.dumps(row["source_base_native_bbox_xyxy_halfopen"], separators=(",", ":")), row["full_feature_label_status"], json.dumps(membership, separators=(",", ":")), status, row["sequence_length"], row["cipher_unit_identity"]))
    return stream.getvalue()


def write_production(output, result, protected):
    require(result["purpose"] != "SYNTHETIC_FIXTURE_ONLY", "Synthetic reviews cannot be written as production results")
    require("final_review" in FROZEN_EVIDENCE_PINS and result["input_sha256"].get("final_review") == FROZEN_EVIDENCE_PINS["final_review"][1], "Unknown production final review hash")
    write_once(output, result, protected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, default=STAGE / "results")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-tsv", type=Path)
    args = parser.parse_args()
    data, protected = load(args.repository_root, args.input_directory)
    result = build(data)
    from check_conflict_delta import check, check_sequence
    check(result, data)
    write_production(args.output, result, protected)
    changed = bool(result["current_graph_overlay"]["added_positive_pair_ids"] or result["current_graph_overlay"]["quarantined_baseline_edges"])
    if args.sequence_tsv and changed:
        protected["written_delta"] = (args.output, sha(args.output.read_bytes()))
        text = current_sequence_tsv(result, data["baseline"])
        check_sequence(text, result, data)
        write_once(args.sequence_tsv, text, protected, text=True)
    print(json.dumps({"status": "WRITTEN", "sha256": sha(args.output.read_bytes()), "sequence_tsv": "WRITTEN" if args.sequence_tsv and changed else "REUSE_PINNED_BASELINE_NO_REDUNDANT_TSV"}, sort_keys=True))


if __name__ == "__main__":
    main()
