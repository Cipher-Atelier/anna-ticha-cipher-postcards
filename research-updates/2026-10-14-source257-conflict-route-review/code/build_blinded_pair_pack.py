#!/usr/bin/env python3
"""Geometry-only paired native boards; source decoding is gated explicitly.

prepare() reads frozen metadata only and removes historical judgments/features.
build() requires the pinned D13 protocol and PASS method gate, then verifies
every reused PNG and saved panel against original RGB rows before reader use.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys

from PIL import Image, ImageDraw, ImageFont


BOX = "native_bbox_xyxy_halfopen"
SOURCE_SIZE = (1785, 1175)
SOURCE_SHA = "7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4"
SOURCE_RGB_SHA = "5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94"
PINS = {
    "canonical": ("results/canonical-repeat-evidence-v1.json", "f0ca8fda6f56dda62c47920d6d955af8fd530f7c3e6945eebd8db1a7e017996a"),
    "references": ("results/effective70-profile-references-v1.json", "b5d588bbeb4e0210d4f3cd0cc3bea45cd7d77a88bdad9fe5037fc979d15e81bf"),
    "context_index": ("comparison-context-pack-v1/context-index.json", "76f81e4db718f3d9bfcf991e9c233d52e961a2dedc7163c4acc22c79abbf1333"),
    "helpers": ("code/assemble_native_comparison_sheets.py", "d7bcfd6a01cd32cd96a4de8734dac0b3320e56d001bd397b4911c785dfff45e2"),
}
PROTOCOL_SHA = "554f461bcf6a210b3bb91da3a36b78042410649083840002413f0bcc82d388dc"
READER_PROTOCOL_CANONICAL_SHA = "422eecdadb63b258a86475544ca2a9f12966c6c936823ddd0fb825914fadddc1"
RELATION = "GEOMETRIC_INTERSECTION_ONLY_NOT_OWNERSHIP_OR_ALIAS"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def canonical_sha(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode())


def write_new(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)


def read_pinned(path, expected):
    need(not path.is_symlink() and stat.S_ISREG(path.stat().st_mode), "Pinned input must be a regular file")
    raw = path.read_bytes()
    need(sha(raw) == expected, "Pinned input byte hash mismatch")
    return raw


def rectangle(value, size=SOURCE_SIZE):
    need(isinstance(value, list) and len(value) == 4 and all(type(x) is int for x in value), "Integer rectangle required")
    x0, y0, x1, y1 = value
    need(0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1], "Rectangle outside source")


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def cohort(canonical):
    rows = [row for row in canonical["core_pairs"] if row["status"] == "DEFERRED"
            and row["deferred_reason"] in {"READER_CANDIDATE_CONFLICT", "FINAL_AI_FEATURE_OR_BINDING_DEFERRED"}]
    pairs = [{"pair_id": row["pair_id"], "member_ids": list(row["member_ids"])} for row in rows]
    ids = sorted({ident for pair in pairs for ident in pair["member_ids"]})
    need(len(pairs) == len({p["pair_id"] for p in pairs}) == 38 and len(ids) == 29, "Exact38/29 cohort required")
    need(all(p["member_ids"] == sorted(set(p["member_ids"])) and len(p["member_ids"]) == 2
             and p["pair_id"] == "--".join(p["member_ids"]) for p in pairs), "Canonical pair ID error")
    return sorted(pairs, key=lambda row: row["pair_id"]), ids


def geometry_intake(canonical, references, index):
    pairs, ids = cohort(canonical)
    refs = {row["id"]: row for row in references["profiles"]}
    need(len(refs) == len(references["profiles"]), "Duplicate profile reference ID")
    windows = {row["focus_id"]: row for row in index["contexts"] if row["kind"] == "focus"}
    need(len(windows) == sum(row["kind"] == "focus" for row in index["contexts"]), "Duplicate context ID")
    profiles = []
    for ident in ids:
        need(ident in refs, "Missing selected29 profile lookup")
        profile = refs[ident]
        clean = {"id": ident, "base_bbox": copy.deepcopy(profile["base_native_bbox_xyxy_halfopen"]),
                 "approved_target_bbox": copy.deepcopy(profile["target_locator_native_bbox_xyxy_halfopen"]), "windows": {}}
        for kind in ("TIGHT", "CONTEXT"):
            need(ident + "-" + kind in windows, "Missing selected target window")
            context = windows[ident + "-" + kind]
            target = next((u for u in context["targets"] if u["id"] == ident), None)
            need(target is not None and context["target_ids"] == [ident], "Wrong context target")
            clean["region"] = target["region"]
            clean["rotation_degrees_clockwise"] = context["rotation_degrees_clockwise"]
            neighbors = [{"id": u["id"], "region": u["region"], BOX: copy.deepcopy(u[BOX])}
                         for u in context["intersecting_annotations"]]
            clean["windows"][kind] = {"context_id": context["context_id"], BOX: copy.deepcopy(context[BOX]),
                                       "intersecting_annotations": neighbors}
        profiles.append(clean)
    intake = {"schema": "source257-blinded-pair-source-geometry-v1", "source_size": list(SOURCE_SIZE),
              "pairs": pairs, "profiles": profiles, "intersection_semantics": RELATION,
              "rectangle_semantics": "APPROXIMATE_SEARCH_RECTANGLES_NOT_CONTOURS_OR_OWNERSHIP_MASKS"}
    validate_intake(intake, {row["pair_id"] for row in pairs})
    return intake


def validate_intake(intake, expected_pairs):
    need(set(intake) == {"schema", "source_size", "pairs", "profiles", "intersection_semantics", "rectangle_semantics"}, "Unapproved intake field")
    need(intake["schema"] == "source257-blinded-pair-source-geometry-v1" and intake["source_size"] == list(SOURCE_SIZE), "Wrong geometry schema/source size")
    pairs, rows = intake["pairs"], intake["profiles"]
    need(len(pairs) == len({p["pair_id"] for p in pairs}) == 38
         and {p["pair_id"] for p in pairs} == set(expected_pairs), "Exact38 pair coverage mismatch")
    ids = sorted({ident for pair in pairs for ident in pair["member_ids"]})
    profiles = {row["id"]: row for row in rows}
    need(len(rows) == len(profiles) == len(ids) == 29 and set(profiles) == set(ids), "Exact29 ID lookup mismatch")
    for pair in pairs:
        need(set(pair) == {"pair_id", "member_ids"} and len(pair["member_ids"]) == 2
             and pair["member_ids"] == sorted(set(pair["member_ids"])) and pair["pair_id"] == "--".join(pair["member_ids"]), "Pair geometry identifiers invalid")
    context_ids = set()
    for row in rows:
        need(set(row) == {"id", "base_bbox", "approved_target_bbox", "region", "rotation_degrees_clockwise", "windows"}, "Unapproved profile field")
        rectangle(row["base_bbox"]); rectangle(row["approved_target_bbox"])
        rotation = 90 if row["region"].startswith("right-R") else 0
        need(type(row["rotation_degrees_clockwise"]) is int and row["rotation_degrees_clockwise"] == rotation, "Source frame sign/rotation mismatch")
        need(set(row["windows"]) == {"TIGHT", "CONTEXT"}, "Two native windows required")
        x0, y0, x1, y1 = row["approved_target_bbox"]
        for kind, xpad, ypad in (("TIGHT", 3, 3), ("CONTEXT", 80, 90)):
            window = row["windows"][kind]
            need(set(window) == {"context_id", BOX, "intersecting_annotations"}, "Unapproved window field")
            need(window[BOX] == [max(0, x0 - xpad), max(0, y0 - ypad), min(1785, x1 + xpad), min(1175, y1 + ypad)], "Window geometry differs from frozen padding")
            need(window["context_id"] not in context_ids, "Context ID reused for different target windows")
            context_ids.add(window["context_id"])
            for neighbor in window["intersecting_annotations"]:
                need(set(neighbor) == {"id", "region", BOX}, "Neighbor prose or outcome leakage")
                rectangle(neighbor[BOX])
                need(intersects(window[BOX], neighbor[BOX]), "Nonintersecting neighbor geometry")
    return profiles


def prepare(d12, protocol_path, results):
    protocol = json.loads(read_pinned(protocol_path, PROTOCOL_SHA))
    view = protocol["source_reader_view"]
    need(canonical_sha(view) == READER_PROTOCOL_CANONICAL_SHA, "Reader-only protocol subsection pin mismatch")
    inputs = {name: json.loads(read_pinned(d12 / relative, expected)) for name, (relative, expected) in PINS.items() if name != "helpers"}
    intake = geometry_intake(inputs["canonical"], inputs["references"], inputs["context_index"])
    need({p["pair_id"] for p in intake["pairs"]} == set(protocol["fixed_pair_ids"])
         and {p["id"] for p in intake["profiles"]} == set(protocol["fixed_profile_ids"]), "Full protocol fixed cohort mismatch")
    intake_path, reader_path = results / "judge-source-geometry-intake-v1.json", results / "source-observation-protocol-v1.json"
    write_new(intake_path, encoded(intake));write_new(reader_path, encoded(view))
    return {"intake_sha256": sha(intake_path.read_bytes()), "reader_protocol_file_sha256": sha(reader_path.read_bytes()),
            "reader_protocol_canonical_sha256": canonical_sha(view), "pairs": len(intake["pairs"]), "ids": len(intake["profiles"]), "source_decoded": False}


def helpers(d12):
    relative, expected = PINS["helpers"]
    read_pinned(d12 / relative, expected)
    spec = importlib.util.spec_from_file_location("frozen_native_comparison_helpers", d12 / relative)
    module = importlib.util.module_from_spec(spec)
    original_flag = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = original_flag
    return module


def plan_boards(intake, sizes):
    profiles = {row["id"]: row for row in intake["profiles"]}
    boards = []
    for first in range(0, len(intake["pairs"]), 4):
        pair_rows = intake["pairs"][first:first + 4]
        row_panels = []
        for pair in pair_rows:
            row_panels.append([{"pair_id": pair["pair_id"], "id": ident, "window_kind": kind,
                                **copy.deepcopy(profiles[ident]["windows"][kind]),
                                "rotation_degrees_clockwise": profiles[ident]["rotation_degrees_clockwise"]}
                               for ident in pair["member_ids"] for kind in ("TIGHT", "CONTEXT")])
        widths = [max(240, max(sizes[row[column]["context_id"]][0] + 16 for row in row_panels)) for column in range(4)]
        panels, y = [], 8
        for row in row_panels:
            x = 8
            for column, panel in enumerate(row):
                width, height = sizes[panel["context_id"]]
                panel["sheet_panel_xyxy_halfopen"] = [x, y + 24, x + width, y + 24 + height]
                panel["label_origin"] = [x, y + 3]
                panel["label"] = f"{panel['id']} {panel[BOX]}"
                panels.append(panel);x += widths[column]
            y += max(sizes[panel["context_id"]][1] for panel in row) + 36
        size = [sum(widths) + 16, y + 8]
        need(size[1] <= 1800, "Native board exceeds maximum height")
        boards.append({"board_id": f"board-{len(boards) + 1:02d}", "size": size,
                       "pair_ids": [p["pair_id"] for p in pair_rows], "panels": panels})
    return boards


def check_immutable(snapshot_path, d12):
    snapshot = json.loads(snapshot_path.read_bytes())
    need(sorted(str(x.relative_to(d12)) for x in d12.rglob('*') if x.is_file()) == snapshot["D12_files"], "D12 frozen file set changed")
    need(sorted(str(x.relative_to(d12)) for x in d12.rglob('*') if x.is_dir()) == snapshot["D12_directories"], "D12 frozen directory set changed")
    for row in snapshot["files"]:
        path = Path(row["path"]);info = path.stat()
        need(sha(path.read_bytes()) == row["sha256"] and info.st_size == row["size"] and info.st_mtime_ns == row["mtime_ns"], "Frozen old input changed")
    return snapshot


def verify_source_panel(source, image, context, helper):
    expected = helper.expected_crop(source, context)
    need(image.mode == "RGB" and image.size == expected.size and image.tobytes() == expected.tobytes(), "Reused PNG differs from original crop")
    return helper.source_row_proof(source, image, context)


def build(d12, source_path, intake_path, protocol_path, gate_path, gate_sha, snapshot_path, output):
    need(not output.exists(), "Immutable output pack already exists")
    protocol = json.loads(read_pinned(protocol_path, PROTOCOL_SHA))
    gate = json.loads(read_pinned(gate_path, gate_sha))
    need(gate.get("gate_status", gate.get("status")) == "PASS", "Method PASS required before source decoding")
    need(PROTOCOL_SHA in [gate.get(key) for key in ("source_protocol_sha256", "protocol_sha256", "parent_protocol_sha256", "frozen_protocol_sha256")], "Method gate is not bound to this protocol")
    need(gate.get("source_reader_view_canonical_sha256") == READER_PROTOCOL_CANONICAL_SHA, "Method gate reader-only protocol pin mismatch")
    intake_raw = intake_path.read_bytes();intake = json.loads(intake_raw)
    profiles = validate_intake(intake, protocol["fixed_pair_ids"])
    metadata = {name: json.loads(read_pinned(d12 / relative, expected)) for name, (relative, expected) in PINS.items() if name != "helpers"}
    need(intake == geometry_intake(metadata["canonical"], metadata["references"], metadata["context_index"]), "Intake differs from immutable source geometry/cohort")
    check_immutable(snapshot_path, d12)
    helper = helpers(d12)
    source_raw = read_pinned(source_path, SOURCE_SHA)
    with Image.open(io.BytesIO(source_raw)) as opened:
        need(opened.mode == "RGB" and opened.size == SOURCE_SIZE and opened.getexif().get(274, 1) == 1, "Original source RGB/size/EXIF mismatch")
        source = opened.copy()
    need(sha(source.tobytes()) == SOURCE_RGB_SHA, "Original decoded RGB mismatch")
    context_index = json.loads(read_pinned(d12 / PINS["context_index"][0], PINS["context_index"][1]))
    contexts = {row["context_id"]: row for row in context_index["contexts"]}
    images, sizes, reused_proofs = {}, {}, []
    for profile in profiles.values():
        for window in profile["windows"].values():
            context = contexts[window["context_id"]]
            need(context[BOX] == window[BOX] and context["rotation_degrees_clockwise"] == profile["rotation_degrees_clockwise"], "Reused context geometry changed")
            png_path = d12 / "comparison-context-pack-v1" / context["private_png"]
            raw = png_path.read_bytes()
            with Image.open(io.BytesIO(raw)) as opened:
                image = opened.copy()
            rows = verify_source_panel(source, image, context, helper)
            cid = context["context_id"]
            images[cid], sizes[cid] = image, image.size
            reused_proofs.append({"context_id": cid, "png_sha256": sha(raw), "source_rows": rows})
    need(len(images) == 58, "Expected58 unique source windows for29 targets")
    boards = plan_boards(intake, sizes)
    need(sum(len(b["panels"]) for b in boards) == 152, "Expected152 direct paired panels")
    output.mkdir(mode=0o700);private = output / "private";private.mkdir(mode=0o700)
    proofs = [];font = ImageFont.load_default()
    for board in boards:
        canvas = Image.new("RGB", board["size"], (255, 255, 255));draw = ImageDraw.Draw(canvas)
        for panel in board["panels"]:
            bounds = list(draw.textbbox(tuple(panel["label_origin"]), panel["label"], font=font))
            need(all(not intersects(bounds, other["sheet_panel_xyxy_halfopen"]) for other in board["panels"]), "Label overlaps source pixels")
            panel["label_bbox_xyxy_halfopen"] = bounds
            draw.text(tuple(panel["label_origin"]), panel["label"], font=font, fill=(0, 0, 0))
            canvas.paste(images[panel["context_id"]], tuple(panel["sheet_panel_xyxy_halfopen"][:2]))
        board["private_png"] = "private/" + board["board_id"] + ".png"
        path = output / board["private_png"];buffer = io.BytesIO();canvas.save(buffer, format="PNG");write_new(path, buffer.getvalue())
        panel_proofs = []
        with Image.open(path) as reopened:
            need(reopened.mode == "RGB" and list(reopened.size) == board["size"], "Saved board RGB/geometry mismatch")
            for panel in board["panels"]:
                crop = reopened.crop(panel["sheet_panel_xyxy_halfopen"]);context = contexts[panel["context_id"]]
                need(crop.size == images[panel["context_id"]].size and crop.tobytes() == images[panel["context_id"]].tobytes(), "Saved panel differs from reused PNG")
                expected = helper.expected_crop(source, context)
                need(crop.size == expected.size and crop.tobytes() == expected.tobytes(), "Saved panel differs from original source crop")
                rows = helper.source_row_proof(source, crop, context)
                panel_proofs.append({"pair_id": panel["pair_id"], "context_id": panel["context_id"], "rgb_sha256": sha(crop.tobytes()), "source_rows": rows, "equals_reused_png_and_original_source": True})
        proofs.append({"board_id": board["board_id"], "png_sha256": sha(path.read_bytes()), "panels": panel_proofs})
    # All rows proven before exposing the completion/index marker to readers.
    snapshot = check_immutable(snapshot_path, d12)
    index = {"schema": "source257-blinded-pair-board-index-v1", "intake_whole_file_sha256": sha(intake_raw),
             "source_size": list(SOURCE_SIZE), "scale": 1, "intersection_semantics": RELATION, "boards": boards}
    write_new(output / "pair-index-v1.json", encoded(index))
    proof = {"schema": "source257-d13-private-source-panel-proof-v1", "status": "PASS", "protocol_sha256": PROTOCOL_SHA,
             "method_gate_whole_file_sha256": gate_sha, "intake_whole_file_sha256": sha(intake_raw),
             "source_encoded_sha256": SOURCE_SHA, "source_rgb_sha256": SOURCE_RGB_SHA,
             "source_decoded_only_after_method_PASS": True, "images_viewed_by_builder": False,
             "reused_pngs": reused_proofs, "boards": proofs, "frozen_inputs_unchanged": True}
    write_new(private / "pixel-proof-v1.json", encoded(proof))
    write_new(output / "private/input-immutability-after.json", encoded({**snapshot, "status": "PASS_UNCHANGED"}))
    return {"status": "PASS", "pairs": 38, "profiles": 29, "reused_pngs": 58, "paired_panels": 152,
            "boards": len(boards), "index_sha256": sha((output / "pair-index-v1.json").read_bytes()),
            "private_proof_whole_file_sha256": sha((private / "pixel-proof-v1.json").read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__);sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare");prep.add_argument("d12", type=Path);prep.add_argument("protocol", type=Path);prep.add_argument("results", type=Path)
    production = sub.add_parser("build")
    for name in ("d12", "source", "intake", "protocol", "gate", "snapshot", "output"):
        production.add_argument(name, type=Path)
    production.add_argument("--gate-sha256", required=True)
    args = parser.parse_args()
    if args.action == "prepare":result = prepare(args.d12, args.protocol, args.results)
    else:result = build(args.d12, args.source, args.intake, args.protocol, args.gate, args.gate_sha256, args.snapshot, args.output)
    print(json.dumps(result, sort_keys=True))
