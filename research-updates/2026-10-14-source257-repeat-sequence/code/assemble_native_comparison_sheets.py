#!/usr/bin/env python3
"""Assemble native comparison sheets; never display or classify image content.

Only opaque ID and integer-coordinate labels are drawn outside source panels.
The public-eligible index has geometry and file pins; raster digests and exact
source-row proofs are written only inside the pack's private directory.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BOX = "native_bbox_xyxy_halfopen"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)


def expected_crop(source: Image.Image, context: dict) -> Image.Image:
    crop = source.crop(context[BOX])
    return crop.transpose(Image.Transpose.ROTATE_270) if context["rotation_degrees_clockwise"] == 90 else crop


def source_row_proof(source: Image.Image, rendered: Image.Image, context: dict) -> list[dict]:
    """Independently recover native rows using integer offsets, not transpose.

    This also checks sheet panels read back from disk, rather than trusting a
    matching in-memory paste or an encoder's successful return.
    """
    x0, y0, x1, y1 = context[BOX]
    width, height = x1 - x0, y1 - y0
    rotated = context["rotation_degrees_clockwise"] == 90
    if rendered.mode != "RGB" or rendered.size != ((height, width) if rotated else (width, height)):
        raise ValueError("Unexpected panel mode or dimensions")
    raw = rendered.tobytes()
    rows = []
    for y in range(height):
        if rotated:
            native_row = b"".join(raw[3 * (x * height + height - 1 - y):3 * (x * height + height - 1 - y) + 3] for x in range(width))
        else:
            native_row = raw[y * width * 3:(y + 1) * width * 3]
        original_row = source.crop((x0, y0 + y, x1, y0 + y + 1)).tobytes()
        if native_row != original_row:
            raise ValueError("Saved RGB panel differs from original source row")
        rows.append({"native_y": y0 + y, "native_x_halfopen": [x0, x1], "rgb_sha256": sha(original_row)})
    return rows


def intersects(a: list[int], b: list[int]) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def layout(contexts: list[dict], sizes: dict[str, tuple[int, int]]) -> tuple[list[int], list[dict]]:
    if len(contexts) != 10:
        raise ValueError("Each sheet requires five TIGHT/CONTEXT pairs")
    column_widths = [max(330, max(sizes[c["context_id"]][0] + 16 for c in contexts[column::2])) for column in range(2)]
    y = 8
    panels = []
    for row in range(5):
        pair = contexts[row * 2:row * 2 + 2]
        for column, context in enumerate(pair):
            width, height = sizes[context["context_id"]]
            x = 8 + (column_widths[0] if column else 0)
            panels.append({"context_id": context["context_id"], "target_id": context["target_ids"][0],
                           "window_kind": context["focus_id"].rsplit("-", 1)[1], BOX: context[BOX],
                           "rotation_degrees_clockwise": context["rotation_degrees_clockwise"],
                           "private_png": context["private_png"],
                           "sheet_panel_xyxy_halfopen": [x, y + 24, x + width, y + 24 + height],
                           "label_origin": [x, y + 3]})
        y += max(sizes[c["context_id"]][1] for c in pair) + 36
    size = [sum(column_widths) + 16, y + 8]
    if size[1] > 1800:
        raise ValueError("Sheet exceeds frozen native-fit maximum height")
    return size, panels


def build(source_path: Path, pack: Path, lineage_path: Path, references_path: Path) -> dict:
    index_path = pack / "context-index.json"
    index_blob = index_path.read_bytes()
    lineage_blob = lineage_path.read_bytes()
    references_blob = references_path.read_bytes()
    index, lineage, references = map(json.loads, (index_blob, lineage_blob, references_blob))
    source_blob = source_path.read_bytes()
    if sha(source_blob) != index["pins"]["source_sha256"]:
        raise ValueError("Source file pin mismatch")
    if sha(references_blob) != lineage["input_file_pins"]["effective_references"]["sha256"]:
        raise ValueError("Effective reference pin mismatch")
    if index["pins"]["protocol_sha256"] != lineage["builder_protocol_sha256"]:
        raise ValueError("Frozen builder protocol lineage mismatch")
    with Image.open(io.BytesIO(source_blob)) as decoded:
        if decoded.mode != "RGB" or decoded.size != (1785, 1175) or decoded.getexif().get(274, 1) != 1:
            raise ValueError("Source mode, dimensions or EXIF orientation changed")
        source = decoded.copy()
    if sha(source.tobytes()) != "5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94":
        raise ValueError("Decoded source RGB pin mismatch")
    selected = [p["id"] for p in references["profiles"]]
    if selected != sorted(selected) or len(selected) != 70 or selected != index["selected_ids"]:
        raise ValueError("Expected the frozen sorted 70-ID cohort")
    lookup = {c["context_id"]: c for c in index["contexts"]}
    focus = [c for c in index["contexts"] if c["kind"] == "focus"]
    if [c["focus_id"] for c in focus] != [uid + "-" + kind for uid in selected for kind in ("TIGHT", "CONTEXT")]:
        raise ValueError("Focus ordering does not match frozen cohort")
    contexts_proof, sizes, png_blobs = [], {}, {}
    for context in index["contexts"]:
        png_blob = (pack / context["private_png"]).read_bytes()
        with Image.open(io.BytesIO(png_blob)) as saved:
            expected = expected_crop(source, context)
            if saved.mode != "RGB" or saved.size != expected.size or saved.tobytes() != expected.tobytes():
                raise ValueError("Saved context PNG does not equal native source crop")
            rows = source_row_proof(source, saved, context)
            sizes[context["context_id"]] = saved.size
        png_blobs[context["context_id"]] = png_blob
        contexts_proof.append({"context_id": context["context_id"], "png_sha256": sha(png_blob),
                               "source_rows": rows, "saved_png_equals_source_crop": True})
    sheet_dir = pack / "private" / "contact-sheets-v1"
    if sheet_dir.exists():
        raise ValueError("Contact sheet output already exists; no overwrite")
    sheet_dir.mkdir(mode=0o700)
    font = ImageFont.load_default()
    sheets, private_sheets = [], []
    for start in range(0, len(focus), 10):
        size, panels = layout(focus[start:start + 10], sizes)
        canvas = Image.new("RGB", size, (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        for panel in panels:
            label = f"{panel['target_id']} {panel['window_kind']} {panel[BOX]}"
            bound = list(draw.textbbox(tuple(panel["label_origin"]), label, font=font))
            if any(intersects(bound, p["sheet_panel_xyxy_halfopen"]) for p in panels):
                raise ValueError("Label would intersect source pixels")
            if bound[0] < 0 or bound[1] < 0 or bound[2] > size[0] or bound[3] > size[1]:
                raise ValueError("Label would leave canvas")
            panel["label"] = label
            panel["label_bbox_xyxy_halfopen"] = bound
            draw.text(tuple(panel["label_origin"]), label, font=font, fill=(0, 0, 0))
            with Image.open(io.BytesIO(png_blobs[panel["context_id"]])) as png:
                canvas.paste(png, tuple(panel["sheet_panel_xyxy_halfopen"][:2]))
        sheet_number = start // 10 + 1
        sheet_path = sheet_dir / f"sheet-{sheet_number:02d}.png"
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        write_new(sheet_path, buffer.getvalue())
        # Independent verification begins from the saved sheet and original JPEG.
        private_panels = []
        with Image.open(sheet_path) as reopened:
            if reopened.mode != "RGB" or list(reopened.size) != size:
                raise ValueError("Saved sheet changed mode or geometry")
            for panel in panels:
                context = lookup[panel["context_id"]]
                extracted = reopened.crop(panel["sheet_panel_xyxy_halfopen"])
                with Image.open(pack / panel["private_png"]) as png:
                    if extracted.size != png.size or extracted.tobytes() != png.tobytes():
                        raise ValueError("Saved sheet panel differs from context PNG")
                original = expected_crop(source, context)
                if extracted.size != original.size or extracted.tobytes() != original.tobytes():
                    raise ValueError("Saved sheet panel differs from source crop")
                rows = source_row_proof(source, extracted, context)
                private_panels.append({"context_id": context["context_id"],
                                       "saved_panel_rgb_sha256": sha(extracted.tobytes()),
                                       "context_png_sha256": sha(png_blobs[context["context_id"]]),
                                       "equals_saved_png": True, "equals_original_crop_exact90CW_or_native": True,
                                       "source_rows": rows})
        sheets.append({"sheet_id": f"sheet-{sheet_number:02d}", "private_png": str(sheet_path.relative_to(pack)),
                       "size": size, "unit_ids": selected[start // 2:start // 2 + 5], "panels": panels})
        private_sheets.append({"sheet_id": sheets[-1]["sheet_id"], "png_sha256": sha(sheet_path.read_bytes()),
                               "panels": private_panels})
    safe = {"schema": "source257-native-comparison-sheet-index-v1", "context_index_sha256": sha(index_blob),
            "lineage_sha256": sha(lineage_blob), "effective_references_file_sha256": sha(references_blob),
            "unit_count": 70, "sheet_count": 14, "panel_count": 140, "scale": 1,
            "source_labels_outside_panels": True, "pixel_digests_in_private_proof_only": True,
            "sheets": sheets}
    safe_path = pack / "contact-sheet-index.json"
    write_new(safe_path, encoded(safe))
    proof = {"schema": "source257-native-comparison-independent-private-proof-v1", "status": "PASS",
             "assembler_file_sha256": sha(Path(__file__).read_bytes()),
             "contact_sheet_index_sha256": sha(safe_path.read_bytes()), "source_encoded_sha256": sha(source_blob),
             "source_rgb_sha256": sha(source.tobytes()), "images_viewed": False, "pair_judgments": False,
             "verified_saved_context_count": len(contexts_proof), "verified_saved_sheet_panel_count": 140,
             "exact_source_rows_recovered_by_integer_offsets": True,
             "contexts": contexts_proof, "sheets": private_sheets}
    proof_path = sheet_dir / "independent-source-panel-proof.json"
    write_new(proof_path, encoded(proof))
    return {"status": "PASS", "context_count": len(contexts_proof), "sheet_count": len(sheets),
            "panel_count": 140, "sheet_sizes": [s["size"] for s in sheets],
            "index": str(safe_path), "index_sha256": sha(safe_path.read_bytes()),
            "private_proof": str(proof_path), "private_proof_sha256": sha(proof_path.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "pack", "lineage", "references"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.pack, args.lineage, args.references)))
