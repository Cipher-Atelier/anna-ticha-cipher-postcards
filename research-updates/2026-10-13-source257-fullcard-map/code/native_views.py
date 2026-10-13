#!/usr/bin/env python3
"""Materialize lossless, native RGB detail views; usage: INPUT OUTPUTROOT."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

BOTTOM = (65, 810, 1710, 1140)
RIGHT = (1330, 50, 1705, 855)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cw_box(box, height):
    """Native-local half-open box to 90-degree clockwise half-open box."""
    x0, y0, x1, y1 = box
    return (height - y1, x0, height - y0, x1)


def inverse_cw_box(box, height):
    u0, v0, u1, v1 = box
    return (v0, height - u1, v1, height - u0)


def exact_rows(rgb, width, box):
    x0, y0, x1, y1 = box
    return b"".join(rgb[(y * width + x0) * 3:(y * width + x1) * 3]
                    for y in range(y0, y1))


def coverage(rectangles, target):
    x0, y0, x1, y1 = target
    covered = sum(any(a <= x < c and b <= y < d for a, b, c, d in rectangles)
                  for y in range(y0, y1) for x in range(x0, x1))
    area = (x1 - x0) * (y1 - y0)
    return {"target_native_bbox": list(target), "target_pixels": area,
            "covered_pixels": covered, "uncovered_pixels": area - covered,
            "union_equals_target": covered == area}


def reserve_rectangles(width, height):
    """Disjoint grid cells outside the two detail context rectangles."""
    xs = sorted({0, width, BOTTOM[0], BOTTOM[2], RIGHT[0], RIGHT[2]})
    ys = sorted({0, height, BOTTOM[1], BOTTOM[3], RIGHT[1], RIGHT[3]})
    return [(a, b, c, d) for a, c in zip(xs, xs[1:])
            for b, d in zip(ys, ys[1:])
            if not any(x0 <= a and c <= x1 and y0 <= b and d <= y1
                       for x0, y0, x1, y1 in (BOTTOM, RIGHT))]


def build(input_file, output_root):
    input_file, output_root = Path(input_file), Path(output_root)
    pixels, results = output_root / "private-pixels", output_root / "results"
    pixels.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    source_bytes = input_file.read_bytes()
    with Image.open(input_file) as opened:
        if opened.mode != "RGB":
            raise ValueError("Input must already decode as RGB; conversion is forbidden")
        source = opened.copy()
    width, height = source.size
    if width < 1710 or height < 1140:
        raise ValueError("Input is smaller than the specified native rectangles")
    rgb = source.tobytes()
    entries = []

    def emit(name, native_box, rotation=0, rotated_box=None):
        native_box = tuple(native_box)
        expected_native = exact_rows(rgb, width, native_box)
        native = source.crop(native_box)
        assert native.tobytes() == expected_native
        expected = native if not rotation else native.transpose(Image.Transpose.ROTATE_270)
        target = pixels / name
        if target.exists():
            raise FileExistsError(target.name)
        expected.save(target, format="PNG")
        with Image.open(target) as saved:
            assert saved.mode == "RGB" and saved.size == expected.size
            assert saved.tobytes() == expected.tobytes()
        data = target.read_bytes()
        entry = {"filename": name, "native_source_bbox": list(native_box),
                 "rotation_clockwise_degrees": rotation,
                 "size": list(expected.size), "file_bytes": len(data),
                 "file_sha256": sha(data), "rgb_sha256": sha(expected.tobytes()),
                 "native_row_slice_sha256": sha(expected_native),
                 "proof": {"native_crop_equals_original_row_slices": True,
                           "saved_png_equals_expected_rgb": True,
                           "rotation_equals_exact_transpose": True if rotation else None}}
        if rotated_box is not None:
            entry["rightblock_cw_bbox"] = list(rotated_box)
        entries.append(entry)

    emit("bottom-context-native.png", BOTTOM)
    bottom_tiles = []
    for row, (y0, y1) in enumerate(((810, 930), (850, 970), (935, 1060), (1020, 1140)), 1):
        for col, x0 in enumerate((65, 345, 625, 905, 1185, 1380), 1):
            box = (x0, y0, min(x0 + 330, 1710), y1)
            bottom_tiles.append(box)
            emit(f"bottom-r{row}-c{col}-native.png", box)
    emit("rightblock-native.png", RIGHT)
    emit("rightblock-cw90.png", RIGHT, 90, (0, 0, 805, 375))
    right_tiles = []
    for index, u0 in enumerate((0, 280, 550), 1):
        box = (u0, 0, min(u0 + 300, 805), 375)
        local = inverse_cw_box(box, RIGHT[3] - RIGHT[1])
        native_box = (local[0] + RIGHT[0], local[1] + RIGHT[1],
                      local[2] + RIGHT[0], local[3] + RIGHT[1])
        right_tiles.append(native_box)
        emit(f"rightblock-cw90-tile{index}.png", native_box, 90, box)
    reserves = reserve_rectangles(width, height)
    manifest = {
        "schema": "native-detail-pack-v1", "coordinate_convention": "half-open [x0,y0,x1,y1]",
        "source": {"filename": input_file.name, "file_bytes": len(source_bytes),
                   "file_sha256": sha(source_bytes), "size": [width, height],
                   "mode": "RGB", "rgb_sha256": sha(rgb), "preserved_without_write": True},
        "operations": ["exact RGB row slices", "lossless PNG encoding", "optional exact 90CW transpose"],
        "rotation_mapping": {
            "native_origin": list(RIGHT[:2]), "native_size": [375, 805],
            "cw_size": [805, 375], "native_local_pixel_to_cw": "u=H-1-y; v=x; H=805",
            "native_local_box_to_cw": "[H-y1,x0,H-y0,x1]",
            "cw_box_to_native_source": "[1330+v0,50+H-u1,1330+v1,50+H-u0]"},
        "views": entries,
        "coverage": {"bottom_detail_tiles": coverage(bottom_tiles, BOTTOM),
                     "rightblock_rotated_tiles": coverage(right_tiles, RIGHT),
                     "fullcard": {"context_native_rectangles": [list(BOTTOM), list(RIGHT)],
                                  "reserve_other_native_rectangles": [list(b) for b in reserves],
                                  "reserve_instruction": "Inspect these remaining regions in the original source context later.",
                                  "original_context_filename": input_file.name,
                                  **coverage([BOTTOM, RIGHT] + reserves, (0, 0, width, height))}}}
    assert all(manifest["coverage"][k]["union_equals_target"] for k in manifest["coverage"])
    manifest_file = results / "native-views-manifest.json"
    if manifest_file.exists():
        raise FileExistsError(manifest_file.name)
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("outputroot")
    args = parser.parse_args()
    print(build(args.input, args.outputroot).name)


if __name__ == "__main__":
    main()
