#!/usr/bin/env python3
"""Prepare a fixed lexical queue and blinded geometry; no image modules or I/O."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

BOX = "native_bbox_xyxy_halfopen"
REASON = "PRESCREEN_WITH_SINGLE_READER_DERIVED_CONTRAST_NOT_ACCEPTED_NEGATIVE"
A_COVERAGE = "METADATA_PRESCREEN_WITH_SEPARATE_UNIT_SOURCE_OBSERVATIONS"
B_COVERAGE = "DERIVED_UNIT_SOURCE_FEATURE_CONTRAST"
PINS = {
    "canonical": ("research-updates/2026-10-14-source257-repeat-sequence/data/canonical-repeat-evidence-v1.json", "5083d313a78796ac32f21f71d93b9b53b230874782f8a4558324b12d7e2d8348"),
    "D13_protocol": ("research-updates/2026-10-14-source257-conflict-route-review/results/conflict-route-protocol-v1.json", "554f461bcf6a210b3bb91da3a36b78042410649083840002413f0bcc82d388dc"),
    "D13_delta": ("research-updates/2026-10-14-source257-conflict-route-review/results/conflict-route-delta-v1.json", "32e69668c238ab0ce02c08a257a3235ebc0235ae887e643627c28b5a7608049a"),
    "references": ("results/effective70-profile-references-v1.json", "b5d588bbeb4e0210d4f3cd0cc3bea45cd7d77a88bdad9fe5037fc979d15e81bf"),
    "context_index": ("comparison-context-pack-v1/context-index.json", "76f81e4db718f3d9bfcf991e9c233d52e961a2dedc7163c4acc22c79abbf1333"),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def queue(canonical, protocol, delta):
    core = canonical["core_pairs"]
    need(len(core) == len({r["pair_id"] for r in core}) == 930, "Unique930 core required")
    rows = sorted((r for r in core if r["deferred_reason"] == REASON), key=lambda r: r["pair_id"])
    need(len(rows) == 772, "Exact772 queue required")
    for row in rows:
        need(row["status"] == "DEFERRED" and row["reader_A"]["coverage"] == A_COVERAGE
             and row["reader_B"]["coverage"] == B_COVERAGE, "Queue coverage mismatch")
        ids = row["member_ids"]
        need(len(ids) == 2 and ids == sorted(set(ids)) and row["pair_id"] == "--".join(ids), "Pair identifier mismatch")
    ordered = [{"ordinal": i + 1, "pair_id": r["pair_id"], "member_ids": list(r["member_ids"])} for i, r in enumerate(rows)]
    queued = {r["pair_id"] for r in ordered}
    direct = {r["pair_id"] for r in core if any(r[k]["coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON" for k in ("reader_A", "reader_B"))
              or r["reader_B_actual_confirmation_reference"] is not None}
    positives = {r["pair_id"] for r in canonical["graph"]["positive_edges"]}
    closure = {r["pair_id"] for r in canonical["closure_pairs"]}
    previous = set(protocol["fixed_pair_ids"])
    need(len(previous) == 38 and previous == {r["pair_id"] for r in delta["pair_dispositions"]}, "D13 fixed38 mismatch")
    need(not queued & (direct | positives | closure | previous), "Completed pair repeated")
    selected = ordered[:64]
    ids = sorted({i for r in selected for i in r["member_ids"]})
    need(len(ids) == 36, "Selected64 must have36 target IDs")
    need((ordered[0]["pair_id"], ordered[63]["pair_id"], ordered[64]["pair_id"])
         == ("FC002--FC015", "FC015--FC123", "FC015--FC125"), "Lexical batch boundary mismatch")
    pins = {k: {"path": path, "path_root": "D12" if k in {"references", "context_index"} else "PUBLIC_REPOSITORY", "sha256": sha}
            for k, (path, sha) in PINS.items()}
    return {"schema": "source257-direct772-queue-v1", "selection_rule": "LEXICAL_ASCENDING_PAIR_ID_FIRST64_NO_SIMILARITY_METRIC",
            "provenance": {"input_pins": pins, "canonical_core_pointer": "/core_pairs", "deferred_reason": REASON,
                           "required_reader_A_coverage": A_COVERAGE, "required_reader_B_coverage": B_COVERAGE,
                           "source_pixels_decoded": False},
            "ordered_queue": ordered, "selected_pair_ids": [r["pair_id"] for r in selected],
            "remaining_pair_ids": [r["pair_id"] for r in ordered[64:]], "selected_profile_ids": ids,
            "scope": {"queue_pairs": 772, "selected_pairs": 64, "remaining_pairs": 708, "selected_profiles": 36},
            "no_repeat_checks": {"D12_direct_core_pairs": len(direct), "D12_positive_edges": len(positives),
                                 "D12_closure_pairs": len(closure), "D13_fixed_pairs": len(previous),
                                 "intersection_with_queue": 0}}


def rectangle(box):
    need(isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box), "Integer box required")
    need(0 <= box[0] < box[2] <= 1785 and 0 <= box[1] < box[3] <= 1175, "Box outside source")


def geometry(prepared, references, index):
    refs = {r["id"]: r for r in references["profiles"]}
    need(len(refs) == len(references["profiles"]) == 70, "Unique70 references required")
    windows = {r["focus_id"]: r for r in index["contexts"] if r["kind"] == "focus"}
    need(len(windows) == 140 and index["source_size"] == [1785, 1175], "Unique140 focus windows required")
    profiles = []
    for ident in prepared["selected_profile_ids"]:
        need(ident in refs, "Missing selected36 lookup")
        ref = refs[ident]
        row = {"id": ident, "base_bbox": copy.deepcopy(ref["base_native_bbox_xyxy_halfopen"]),
               "approved_target_bbox": copy.deepcopy(ref["target_locator_native_bbox_xyxy_halfopen"]), "windows": {}}
        rectangle(row["base_bbox"]); rectangle(row["approved_target_bbox"])
        for kind, xpad, ypad in (("TIGHT", 3, 3), ("CONTEXT", 80, 90)):
            window = windows[ident + "-" + kind]
            need(window["target_ids"] == [ident], "Incorrect window target")
            target = next(r for r in window["targets"] if r["id"] == ident)
            rotation = 90 if target["region"].startswith("right-R") else 0
            need(type(window["rotation_degrees_clockwise"]) is int and window["rotation_degrees_clockwise"] == rotation, "Frame sign mismatch")
            if "region" in row:
                need(row["region"] == target["region"] and row["rotation_degrees_clockwise"] == rotation, "Inconsistent target frame")
            row.update(region=target["region"], rotation_degrees_clockwise=rotation, frame="EXACT90CW" if rotation else "NATIVE0")
            x0, y0, x1, y1 = row["approved_target_bbox"]
            expected = [max(0, x0-xpad), max(0, y0-ypad), min(1785, x1+xpad), min(1175, y1+ypad)]
            need(window[BOX] == expected, "Frozen search window padding mismatch")
            neighbors = []
            for neighbor in window["intersecting_annotations"]:
                box = neighbor[BOX]; rectangle(box)
                need(box[0] < expected[2] and expected[0] < box[2] and box[1] < expected[3] and expected[1] < box[3], "Nonintersecting neighbor")
                neighbors.append({"id": neighbor["id"], "region": neighbor["region"], BOX: list(box)})
            row["windows"][kind] = {"context_id": window["context_id"], BOX: list(expected), "intersecting_annotations": neighbors}
        profiles.append(row)
    need(len(profiles) == 36 and len({w["context_id"] for r in profiles for w in r["windows"].values()}) == 72, "Exact36 profiles/72 contexts required")
    pairs = [{"pair_id": r["pair_id"], "member_ids": list(r["member_ids"])} for r in prepared["ordered_queue"][:64]]
    return {"schema": "source257-direct64-source-geometry-v1", "source_size": [1785, 1175], "pairs": pairs, "profiles": profiles,
            "rectangle_semantics": "APPROXIMATE_SEARCH_LOCATORS_NOT_UNIT_MASKS_BOUNDARIES_CONTOURS_OR_OWNERSHIP",
            "intersection_semantics": "GEOMETRIC_INTERSECTION_ONLY_NOT_OWNERSHIP_OR_ALIAS"}


def prepare(repository, d12, results):
    inputs, originals = {}, {}
    for name, (relative, expected) in PINS.items():
        path = (d12 if name in {"references", "context_index"} else repository) / relative
        need(not path.is_symlink() and path.is_file(), "Pinned regular file required")
        raw = path.read_bytes(); need(digest(raw) == expected, "Input pin mismatch: " + name)
        inputs[name] = json.loads(raw); originals[path] = raw
    prepared = queue(inputs["canonical"], inputs["D13_protocol"], inputs["D13_delta"])
    intake = geometry(prepared, inputs["references"], inputs["context_index"])
    paths = [(results / "direct772-queue-v1.json", encoded(prepared)), (results / "judge-source-geometry-intake-v1.json", encoded(intake))]
    need(results.is_dir() and all(not p.exists() and not p.is_symlink() for p, _ in paths), "New output paths required")
    for path, raw in paths:
        with path.open("xb") as stream:
            stream.write(raw)
    need(all(path.read_bytes() == raw for path, raw in originals.items()), "Frozen input changed")
    return {"queue_sha256": digest(paths[0][1]), "intake_sha256": digest(paths[1][1]), **prepared["scope"], "unique_contexts": 72, "source_decoded": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--d12", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.repository_root, args.d12, args.results), sort_keys=True))


if __name__ == "__main__":
    main()
