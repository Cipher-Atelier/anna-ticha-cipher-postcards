#!/usr/bin/env python3
"""Gated native64 paired boards and private original-source row proofs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

import prepare_direct772_pack as prep

BOX = prep.BOX
PROTOCOL_SHA = "43d8e1c6dd86520b0b0e4f58f88c19bdfb025830978aacff3069852f709b0797"
GATE_SHA = "bec5786f9e46968044d84740bd42b249de604ec4d7ed5eb30fb044cd47da6fee"
SAFE_PINS = {
    "source-observation-protocol-v1.json": "647b640943976508ea1020c9699f51819cde6acb6db9ba47ddb658c8f2daa844",
    "judge-source-geometry-intake-v1.json": "64745684aecba5f547b4033d2d9425a8864955b94078f88aa9ae3620d0f96bca",
    "source-reader-output-format-v2.json": "5f4b05db7c5babc6836dcfdecfcd904a5ca32205fb392e615dc711ff40b0843d",
    "direct772-queue-v1.json": "ecfb18d68ac7135f3c3215f0ec1843a199f1eda20840ab6cf98003a8b37818c0",
}
HELPER_SHA = "d7bcfd6a01cd32cd96a4de8734dac0b3320e56d001bd397b4911c785dfff45e2"
SOURCE_SHA = "7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4"
RGB_SHA = "5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94"
need = prep.need
sha = prep.digest
encoded = prep.encoded


def pinned(path, expected):
    need(path.is_file() and not path.is_symlink(), "Pinned regular file required")
    raw = path.read_bytes()
    need(sha(raw) == expected, "Pinned byte mismatch: " + path.name)
    return raw


def gate_check(protocol, gate, safe):
    need(gate.get("status") == "PASS" and gate.get("blockers") == [], "Explicit method PASS required")
    need(gate.get("source_protocol_sha256") == PROTOCOL_SHA, "Protocol gate binding mismatch")
    names = ("safe_view_sha256", "safe_intake_sha256", "output_format_sha256", "queue_sha256")
    for name, expected in zip(names, SAFE_PINS.values()):
        need(gate.get(name) == expected, "Method safe input binding mismatch")
    need(protocol["source_reader_view"] == safe, "Safe view differs from frozen protocol")


def helper(d12):
    path = d12 / "code/assemble_native_comparison_sheets.py"
    pinned(path, HELPER_SHA)
    spec = importlib.util.spec_from_file_location("frozen_native_rows", path)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


def snapshot(roots, source):
    trees = []
    for root in roots:
        rows = sorted(x for x in root.rglob("*") if ".git" not in x.relative_to(root).parts)
        trees.append({"root": str(root), "directories": [str(x.relative_to(root)) for x in rows if x.is_dir()],
                      "files": [{"relative": str(x.relative_to(root)), "sha256": sha(x.read_bytes()),
                                 "size": x.stat().st_size, "mtime_ns": x.stat().st_mtime_ns} for x in rows if x.is_file()]})
    return {"trees": trees, "source": {"path": str(source), "sha256": sha(source.read_bytes()),
            "size": source.stat().st_size, "mtime_ns": source.stat().st_mtime_ns}}


def unchanged(saved):
    need(snapshot([Path(t["root"]) for t in saved["trees"]], Path(saved["source"]["path"])) == saved,
         "Protected old file bytes, timestamps or directory sets changed")


def plan(intake, sizes):
    profiles = {r["id"]: r for r in intake["profiles"]}
    pairs = intake["pairs"]
    need(len(pairs) == len({r["pair_id"] for r in pairs}) == 64 and len(profiles) == 36, "Exact64/36 required")
    boards = []
    serial = 0
    for start in range(0, 64, 4):
        rows = []
        for pair in pairs[start:start+4]:
            row = []
            for ident in pair["member_ids"]:
                profile = profiles[ident]
                rotation = profile["rotation_degrees_clockwise"]
                need(rotation == (90 if profile["region"].startswith("right-R") else 0), "Frame sign mismatch")
                for kind in ("TIGHT", "CONTEXT"):
                    window = profile["windows"][kind]
                    serial += 1
                    row.append({"panel_id": f"panel-{serial:04d}", "pair_id": pair["pair_id"], "target_id": ident,
                                "context_id": window["context_id"], "window_kind": kind, BOX: list(window[BOX]),
                                "rotation_degrees_clockwise": rotation})
            rows.append(row)
        widths = [max(240, max(sizes[row[c]["context_id"]][0] + 16 for row in rows)) for c in range(4)]
        panels, y = [], 8
        for row in rows:
            x = 8
            for col, panel in enumerate(row):
                w, h = sizes[panel["context_id"]]
                panel.update(sheet_panel_xyxy_halfopen=[x, y+24, x+w, y+24+h], label_origin=[x, y+3],
                             label=f"{panel['target_id']} {panel[BOX]}")
                panels.append(panel)
                x += widths[col]
            y += max(sizes[panel["context_id"]][1] for panel in row) + 36
        size = [sum(widths)+16, y+8]
        need(size[1] <= 1800, "Native board exceeds1800")
        boards.append({"board_id": f"board-{len(boards)+1:02d}", "size": size,
                       "pair_ids": [r["pair_id"] for r in pairs[start:start+4]], "panels": panels,
                       "private_png": f"private/board-{len(boards)+1:02d}.png"})
    need(serial == 256, "Exact256 panels required")
    return boards


def verify_panel(source, panel, context, helpers):
    expected = helpers.expected_crop(source, context)
    need(panel.mode == "RGB" and panel.size == expected.size and panel.tobytes() == expected.tobytes(), "Native source crop mismatch")
    return helpers.source_row_proof(source, panel, context)


def write_new(path, raw):
    with path.open("xb") as out:
        out.write(raw)


def build(stage, repository, d12, source_path, output):
    need(not output.exists() and not output.is_symlink(), "New output pack required")
    results = stage / "results"
    protocol = json.loads(pinned(results / "direct772-protocol-v2.json", PROTOCOL_SHA))
    gate = json.loads(pinned(results / "method-protocol-gate-private-v1.json", GATE_SHA))
    safe = {name: json.loads(pinned(results / name, expected)) for name, expected in SAFE_PINS.items()}
    gate_check(protocol, gate, safe["source-observation-protocol-v1.json"])
    intake = safe["judge-source-geometry-intake-v1.json"]
    references = json.loads(pinned(d12 / prep.PINS["references"][0], prep.PINS["references"][1]))
    index = json.loads(pinned(d12 / prep.PINS["context_index"][0], prep.PINS["context_index"][1]))
    need(intake == prep.geometry(safe["direct772-queue-v1.json"], references, index), "Intake reconstruction mismatch")
    helpers = helper(d12)
    # Freeze old trees before any source decode or new pack creation.
    before = snapshot([d12, stage.parent / "source257-conflict-route-review-next-20261014", repository], source_path)
    need(before["source"]["sha256"] == SOURCE_SHA, "Original encoded pin mismatch")
    write_new(results / "input-immutability-before-private-v1.json", encoded(before))
    # All actual protocol, gate and metadata checks above precede Image.open.
    with Image.open(io.BytesIO(pinned(source_path, SOURCE_SHA))) as opened:
        need(opened.mode == "RGB" and opened.size == (1785, 1175) and opened.getexif().get(274, 1) == 1, "Original source mode/size/EXIF mismatch")
        source = opened.copy()
    need(sha(source.tobytes()) == RGB_SHA, "Original decoded RGB mismatch")
    contexts = {r["context_id"]: r for r in index["contexts"]}
    images, sizes, reused = {}, {}, []
    for profile in intake["profiles"]:
        for window in profile["windows"].values():
            cid = window["context_id"]; context = contexts[cid]
            need(context[BOX] == window[BOX] and context["rotation_degrees_clockwise"] == profile["rotation_degrees_clockwise"], "Context binding mismatch")
            path = d12 / "comparison-context-pack-v1" / context["private_png"]
            raw = path.read_bytes()
            with Image.open(io.BytesIO(raw)) as opened:
                image = opened.copy()
            rows = verify_panel(source, image, context, helpers)
            images[cid], sizes[cid] = image, image.size
            reused.append({"context_id": cid, "png_sha256": sha(raw), "original_rows": rows})
    need(len(images) == 72, "Exact72 reused PNGs required")
    boards = plan(intake, sizes)
    output.mkdir(mode=0o700); (output / "private").mkdir(mode=0o700)
    proofs = []; font = ImageFont.load_default()
    for board in boards:
        canvas = Image.new("RGB", board["size"], (255, 255, 255)); draw = ImageDraw.Draw(canvas)
        for panel in board["panels"]:
            bounds = list(draw.textbbox(tuple(panel["label_origin"]), panel["label"], font=font))
            need(0 <= bounds[0] < bounds[2] <= board["size"][0] and 0 <= bounds[1] < bounds[3] <= board["size"][1], "Label outside canvas")
            need(all(not helpers.intersects(bounds, other["sheet_panel_xyxy_halfopen"]) for other in board["panels"]), "Label overlaps source pixels")
            panel["label_bbox_xyxy_halfopen"] = bounds
            draw.text(tuple(panel["label_origin"]), panel["label"], font=font, fill=(0, 0, 0))
            canvas.paste(images[panel["context_id"]], tuple(panel["sheet_panel_xyxy_halfopen"][:2]))
        path = output / board["private_png"]; buffer = io.BytesIO(); canvas.save(buffer, format="PNG"); write_new(path, buffer.getvalue())
        panel_proofs = []
        with Image.open(path) as saved:
            need(saved.mode == "RGB" and list(saved.size) == board["size"], "Saved board geometry mismatch")
            for panel in board["panels"]:
                cropped = saved.crop(panel["sheet_panel_xyxy_halfopen"]); cid = panel["context_id"]
                need(cropped.size == images[cid].size and cropped.tobytes() == images[cid].tobytes(), "Saved panel differs from reused PNG")
                rows = verify_panel(source, cropped, contexts[cid], helpers)
                panel_proofs.append({"panel_id": panel["panel_id"], "context_id": cid, "rgb_sha256": sha(cropped.tobytes()),
                                     "equals_original_and_reused_png": True, "original_rows": rows})
        proofs.append({"board_id": board["board_id"], "png_sha256": sha(path.read_bytes()), "panels": panel_proofs})
    unchanged(before)
    proof = {"schema": "source257-direct64-private-source-panel-proof-v1", "status": "PASS", "protocol_sha256": PROTOCOL_SHA,
             "method_gate_whole_file_sha256": GATE_SHA, "safe_input_whole_file_sha256": SAFE_PINS,
             "source_encoded_sha256": SOURCE_SHA, "source_rgb_sha256": RGB_SHA, "source_decoded_after_actual_method_PASS": True,
             "images_viewed_by_builder": False, "integer_offset_source_row_recovery": True, "reused_pngs": reused,
             "boards": proofs, "old_inputs_and_directory_sets_unchanged": True}
    proof_path = output / "private/source-panel-proof-v1.json"; write_new(proof_path, encoded(proof))
    compact = {"schema": "source257-direct64-native-pair-index-v1", "scale": 1, "source_size": [1785, 1175],
               "safe_intake_sha256": SAFE_PINS["judge-source-geometry-intake-v1.json"],
               "private_proof_whole_file_sha256": sha(proof_path.read_bytes()),
               "profile_and_neighbor_geometry": "REFERENCE_SHARED_SAFE_INTAKE_BY_TARGET_AND_CONTEXT_ID",
               "source_png_base": "D12/comparison-context-pack-v1/private", "source_png_pattern": "{context_id}.png",
               "board_count": 16, "pair_count": 64, "target_count": 36, "unique_context_count": 72, "panel_count": 256,
               "labels_outside_source_pixels": True, "boards": boards}
    index_path = output / "pair-index-v1.json"; write_new(index_path, encoded(compact))
    write_new(output / "private/input-immutability-after-v1.json", encoded({"status": "PASS", "before_snapshot_whole_file_sha256": sha(encoded(before)), "all_old_bytes_timestamps_directory_sets_unchanged": True}))
    return {"status": "PASS", "boards": 16, "panels": 256, "contexts": 72, "pairs": 64, "targets": 36,
            "board_sizes": [b["size"] for b in boards], "index_sha256": sha(index_path.read_bytes()),
            "private_proof_whole_file_sha256": sha(proof_path.read_bytes()), "old_inputs_unchanged": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("stage", "repository", "d12", "source", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.stage, args.repository, args.d12, args.source, args.output), sort_keys=True))
