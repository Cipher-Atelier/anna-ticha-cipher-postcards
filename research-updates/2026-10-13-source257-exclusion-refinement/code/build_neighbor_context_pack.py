#!/usr/bin/env python3
"""Build immutable native-pixel contexts for a pinned annotation cohort.

Only coordinates and IDs are read from the map/inventory. No segmentation,
recognition, class inference, pixel enhancement, or raster labels are applied.
The public index contains geometry; pixel and row digests stay in private/.
Requires Python 3.10+ and Pillow.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys

from PIL import Image


PROTOCOL_SCHEMA = "source257-neighbor-context-protocol-v1"
INDEX_SCHEMA = "source257-neighbor-context-index-v1"
PROOF_SCHEMA = "source257-neighbor-context-private-proof-v1"
BBOX_KEY = "native_bbox_xyxy_halfopen"
RELATION = "geometric_intersection_only_not_an_ownership_claim"


class PackError(ValueError):
    """Invalid or unsafe pack request, detected before output creation."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_keys(value: object, allowed: set[str], required: set[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise PackError(f"{label} must be an object")
    unknown = set(value) - allowed
    missing = required - set(value)
    if unknown or missing:
        raise PackError(f"{label}: unknown keys {sorted(unknown)}; missing keys {sorted(missing)}")
    return value


def nonnegative(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise PackError(f"{label} must be a nonnegative integer")
    return value


def bbox(value: object, size: tuple[int, int], label: str) -> tuple[int, int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 4 or any(type(n) is not int for n in value):
        raise PackError(f"{label} must contain four integer half-open coordinates")
    x0, y0, x1, y1 = value
    if not (0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1]):
        raise PackError(f"{label} is empty or outside the source")
    return tuple(value)


def intersects(a: tuple, b: tuple) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def expand(b: tuple, xpad: int, ypad: int, size: tuple) -> tuple:
    return (max(0, b[0] - xpad), max(0, b[1] - ypad),
            min(size[0], b[2] + xpad), min(size[1], b[3] + ypad))


def union(boxes: list[tuple]) -> tuple:
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def load_units(base: dict, size: tuple) -> dict:
    """Extract geometry for every map unit, including unresolved extents."""
    try:
        rows = [(u, "frozen-first-band") for u in base["frozen_first_band"]["units"]]
        rows += [(u, u["region"]) for u in base["new_units"]]
    except (KeyError, TypeError) as exc:
        raise PackError("base map lacks annotation geometry") from exc
    result = {}
    for u, region in rows:
        uid = u.get("id")
        if not isinstance(uid, str) or not uid or uid in result:
            raise PackError("map IDs must be unique nonempty strings")
        if not isinstance(region, str) or not region:
            raise PackError(f"invalid region for {uid}")
        result[uid] = {"id": uid, "region": region,
                       BBOX_KEY: bbox(u.get(BBOX_KEY), size, f"map {uid}")}
    if not result:
        raise PackError("map has no units")
    return result


def inventory_ids(inventory: dict, base_sha: str) -> set[str]:
    if inventory.get("base_map_sha256") != base_sha:
        raise PackError("inventory's base-map pin disagrees with the supplied map")
    try:
        # Deliberately never inspect candidate classes, signatures, or labels.
        ids = {r["id"] for r in inventory["records"]}
        for name in ("eligible_singleton_ids", "excluded_whole_ids", "unresolved_source_ids"):
            ids.update(inventory[name])
    except (KeyError, TypeError) as exc:
        raise PackError("inventory lacks its ID collections") from exc
    if not all(isinstance(uid, str) and uid for uid in ids):
        raise PackError("inventory IDs must be nonempty strings")
    return ids


def read_inputs(paths: list[Path], output: Path) -> tuple[list[bytes], list[tuple]]:
    """Check aliases before reading; no directories or output files are created."""
    identities, blobs = [], []
    resolved_output = output.resolve()
    if os.path.lexists(output):
        raise PackError("output already exists; packs are immutable")
    for path in paths:
        if path.is_symlink():
            raise PackError(f"input symlink is not allowed: {path.name}")
        try:
            info = path.stat()
        except OSError as exc:
            raise PackError(f"cannot stat input {path.name}") from exc
        if not stat.S_ISREG(info.st_mode):
            raise PackError(f"input is not a regular file: {path.name}")
        identity = (info.st_dev, info.st_ino)
        if identity in [v[:2] for v in identities]:
            raise PackError("inputs alias one another (including hardlinks)")
        resolved_input = path.resolve()
        if resolved_output == resolved_input or resolved_output in resolved_input.parents:
            raise PackError("output aliases or contains an input")
        identities.append((*identity, info.st_size, info.st_mtime_ns, info.st_ctime_ns))
        blobs.append(path.read_bytes())
    return blobs, identities


def check_unchanged(paths: list[Path], identities: list[tuple], blobs: list[bytes]) -> None:
    for path, expected, blob in zip(paths, identities, blobs):
        info = path.stat()
        now = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if path.is_symlink() or now != expected or path.read_bytes() != blob:
            raise PackError(f"input changed during preflight: {path.name}")


def validate_protocol(protocol: dict, actual: dict) -> tuple[list[str], dict, dict]:
    require_keys(protocol, {"schema", "pins", "selected_ids", "trajectory_padding", "focus"},
                 {"schema", "pins", "selected_ids"}, "protocol")
    if protocol["schema"] != PROTOCOL_SCHEMA:
        raise PackError("unsupported protocol schema")
    pins = require_keys(protocol["pins"], set(actual), set(actual), "protocol pins")
    for key, value in actual.items():
        if pins[key] != value:
            raise PackError(f"protocol pin mismatch: {key}")
    selected = protocol["selected_ids"]
    if (not isinstance(selected, list) or not selected
            or any(not isinstance(uid, str) or not uid for uid in selected)
            or len(selected) != len(set(selected))):
        raise PackError("selected_ids must be a nonempty list of unique strings")
    pad = require_keys(protocol.get("trajectory_padding", {}), {"cross_axis", "along_axis"}, set(), "trajectory padding")
    pad = {"cross_axis": nonnegative(pad.get("cross_axis", 80), "cross_axis"),
           "along_axis": nonnegative(pad.get("along_axis", 40), "along_axis")}
    focus = require_keys(protocol.get("focus", {}), {"enabled", "x_padding", "y_padding", "windows"}, set(), "focus")
    enabled = focus.get("enabled", True)
    if type(enabled) is not bool:
        raise PackError("focus.enabled must be boolean")
    focus = {"enabled": enabled, "x_padding": nonnegative(focus.get("x_padding", 80), "x_padding"),
             "y_padding": nonnegative(focus.get("y_padding", 90), "y_padding"), "windows": focus.get("windows", [])}
    if not isinstance(focus["windows"], list) or (focus["windows"] and not enabled):
        raise PackError("focus windows must be a list and cannot be provided when disabled")
    return selected, pad, focus


def plan_contexts(units: dict, selected: list[str], size: tuple, pad: dict, focus: dict) -> list[dict]:
    """Region membership controls context extent, never mark ownership."""
    contexts = []
    touched = sorted({units[uid]["region"] for uid in selected})
    for region in touched:
        region_units = [u for u in units.values() if u["region"] == region]
        clockwise = region.startswith("right-R")
        native_union = union([u[BBOX_KEY] for u in region_units])
        xpad, ypad = ((pad["cross_axis"], pad["along_axis"]) if clockwise
                      else (pad["along_axis"], pad["cross_axis"]))
        contexts.append({"kind": "region", "region": region,
                         "same_region_annotation_union_xyxy_halfopen": list(native_union),
                         "same_region_annotation_ids": sorted(u["id"] for u in region_units),
                         BBOX_KEY: expand(native_union, xpad, ypad, size),
                         "rotation_degrees_clockwise": 90 if clockwise else 0,
                         "target_ids": [uid for uid in selected if units[uid]["region"] == region]})
    if focus["enabled"]:
        if focus["windows"]:
            names = set()
            for window in focus["windows"]:
                require_keys(window, {"id", "target_ids", BBOX_KEY, "rotation_degrees_clockwise"},
                             {"id", "target_ids", BBOX_KEY}, "focus window")
                name, ids = window["id"], window["target_ids"]
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", name) or name in names:
                    raise PackError("focus window IDs must be unique safe identifiers")
                names.add(name)
                if (not isinstance(ids, list) or not ids or any(uid not in selected for uid in ids)
                        or len(set(ids)) != len(ids)):
                    raise PackError("focus window target_ids must be a unique nonempty subset of selected_ids")
                rectangle = bbox(window[BBOX_KEY], size, f"focus {name}")
                if any(not intersects(rectangle, units[uid][BBOX_KEY]) for uid in ids):
                    raise PackError("each focus target must geometrically intersect its window")
                regions = {units[uid]["region"] for uid in ids}
                if len(regions) > 1 and "rotation_degrees_clockwise" not in window:
                    raise PackError("a multi-region focus requires explicit rotation_degrees_clockwise")
                default_rotation = 90 if units[ids[0]]["region"].startswith("right-R") else 0
                rotation = window.get("rotation_degrees_clockwise", default_rotation)
                if type(rotation) is not int or rotation not in (0, 90):
                    raise PackError("focus rotation must be 0 or 90 degrees clockwise")
                if len(regions) == 1 and rotation != default_rotation:
                    raise PackError("single-region focus rotation must follow its region")
                contexts.append({"kind": "focus", "focus_id": name, BBOX_KEY: rectangle,
                                 "rotation_degrees_clockwise": rotation, "target_ids": ids})
        else:
            for uid in selected:
                contexts.append({"kind": "focus", "focus_id": uid, BBOX_KEY:
                                 expand(units[uid][BBOX_KEY], focus["x_padding"], focus["y_padding"], size),
                                 "rotation_degrees_clockwise": 90 if units[uid]["region"].startswith("right-R") else 0,
                                 "target_ids": [uid]})
    for i, context in enumerate(contexts, 1):
        context["context_id"] = f"context-{i:03d}"
        context["private_png"] = f"private/context-{i:03d}.png"
        context[BBOX_KEY] = list(context[BBOX_KEY])
        context["targets"] = [units[uid] for uid in context["target_ids"]]
        context["intersecting_annotations"] = [dict(u) for u in units.values() if intersects(context[BBOX_KEY], u[BBOX_KEY])]
        context["intersection_relation"] = RELATION
    return contexts


def render_context(source: Image.Image, context: dict) -> tuple[bytes, dict]:
    rect = context[BBOX_KEY]
    native = source.crop(rect)
    clockwise = context["rotation_degrees_clockwise"] == 90
    rendered = native.transpose(Image.Transpose.ROTATE_270) if clockwise else native.copy()
    inverse = rendered.transpose(Image.Transpose.ROTATE_90) if clockwise else rendered.copy()
    if inverse.size != native.size or inverse.tobytes() != native.tobytes():
        raise PackError("native pixel inverse transform verification failed")
    buffer = io.BytesIO()
    rendered.save(buffer, format="PNG")
    png = buffer.getvalue()
    # Verify encoded PNG pixels as well as the in-memory transpose.
    with Image.open(io.BytesIO(png)) as reopened:
        if reopened.mode != "RGB" or reopened.size != rendered.size or reopened.tobytes() != rendered.tobytes():
            raise PackError("PNG roundtrip altered pixels")
    row_bytes = native.width * 3
    raw = native.tobytes()
    rows = [{"native_y": rect[1] + i, "native_x_halfopen": [rect[0], rect[2]],
             "rgb_sha256": digest(raw[i * row_bytes:(i + 1) * row_bytes])} for i in range(native.height)]
    return png, {"context_id": context["context_id"], BBOX_KEY: rect,
                 "rotation_degrees_clockwise": context["rotation_degrees_clockwise"],
                 "png_sha256": digest(png), "png_size": list(rendered.size),
                 "native_crop_rgb_sha256": digest(raw), "rendered_rgb_sha256": digest(rendered.tobytes()),
                 "source_rows": rows, "inverse_verified_exact_rgb": True,
                 "inverse_mapping": ({"source_x": "native_x0 + rendered_y", "source_y": "native_y1 - 1 - rendered_x"}
                                     if clockwise else {"source_x": "native_x0 + rendered_x", "source_y": "native_y0 + rendered_y"}),
                 "pixel_processing": "native RGB decode, crop, exact integer transpose only"}


def build_pack(source_path: Path, base_path: Path, inventory_path: Path,
               protocol_path: Path, output: Path, expected_protocol_sha256: str | None = None) -> dict:
    paths = [Path(p) for p in (source_path, base_path, inventory_path, protocol_path)]
    output = Path(output)
    blobs, identities = read_inputs(paths, output)
    source_blob, base_blob, inventory_blob, protocol_blob = blobs
    shas = [digest(blob) for blob in blobs]
    if expected_protocol_sha256 is not None and shas[3] != expected_protocol_sha256:
        raise PackError("protocol whole-file SHA256 mismatch")
    try:
        base, inventory, protocol = [json.loads(b) for b in blobs[1:]]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackError("invalid input JSON") from exc
    if not all(isinstance(value, dict) for value in (base, inventory, protocol)):
        raise PackError("JSON inputs must be objects")
    # Source mode is pinned RGB. Reject implicit conversion or EXIF reorientation.
    with Image.open(io.BytesIO(source_blob)) as decoded:
        if decoded.mode != "RGB":
            raise PackError("source must decode directly as RGB")
        decoded.load()
        source = decoded.copy()
    source_rgb_sha = digest(source.tobytes())
    actual = {"source_sha256": shas[0], "source_rgb_sha256": source_rgb_sha,
              "source_size": list(source.size), "base_sha256": shas[1], "inventory_sha256": shas[2]}
    selected, pad, focus = validate_protocol(protocol, actual)
    base_source = base.get("source", {})
    if (base_source.get("file_sha256") != shas[0] or base_source.get("rgb_sha256") != source_rgb_sha
            or base_source.get("size") != list(source.size)):
        raise PackError("base map's source pins disagree with the supplied source")
    units = load_units(base, source.size)
    known_ids = inventory_ids(inventory, shas[1])
    if set(units) != known_ids:
        raise PackError("base map and inventory annotation ID sets disagree")
    if any(uid not in units for uid in selected):
        raise PackError("selected cohort contains an unknown annotation ID")
    contexts = plan_contexts(units, selected, source.size, pad, focus)
    rendered = [render_context(source, context) for context in contexts]
    private_proof = {"schema": PROOF_SCHEMA, "pins": actual, "protocol_sha256": shas[3],
                     "annotation_unit_count": len(units), "annotations_are_tokens": False,
                     "selected_ids": selected, "contexts": [proof for _, proof in rendered]}
    public_index = {"schema": INDEX_SCHEMA,
                    "pins": {"source_sha256": shas[0], "base_sha256": shas[1],
                             "inventory_sha256": shas[2], "protocol_sha256": shas[3]},
                    "source_size": list(source.size), "annotation_unit_count": len(units),
                    "annotations_are_tokens": False, "selected_ids": selected,
                    "trajectory_padding": pad, "focus_parameters": focus,
                    "intersection_relation": RELATION, "contexts": contexts}
    # All parsing, alias/pin validation, context planning, and exact pixel proofs
    # complete before the first output write. mkdir(exist_ok=False) claims the
    # destination without overwriting even a concurrently created empty pack.
    check_unchanged(paths, identities, blobs)
    if os.path.lexists(output):
        raise PackError("output appeared during preflight; packs are immutable")
    if not output.parent.is_dir():
        raise PackError("output parent must already exist")
    try:
        output.mkdir()
    except FileExistsError as exc:
        raise PackError("output appeared during creation; packs are immutable") from exc
    private_dir = output / "private"
    private_dir.mkdir(mode=0o700)
    for context, (png, _) in zip(contexts, rendered):
        with (output / context["private_png"]).open("xb") as stream:
            stream.write(png)
    with (private_dir / "pixel-proof.json").open("xb") as stream:
        stream.write(json_bytes(private_proof))
    with (output / "context-index.json").open("xb") as stream:
        stream.write(json_bytes(public_index))
    return public_index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("base", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--protocol-sha256", help="externally pinned protocol whole-file SHA256")
    args = parser.parse_args(argv)
    try:
        result = build_pack(args.source, args.base, args.inventory, args.protocol,
                            args.output_root, args.protocol_sha256)
    except (PackError, OSError, Image.UnidentifiedImageError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "created", "context_count": len(result["contexts"]),
                      "target_count": len(result["selected_ids"]), "output_root": str(args.output_root)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
