#!/usr/bin/env python3
"""Recreate private, unmodified native RGB context evidence from pinned inputs.

Usage: build_feature_context_pack.py SOURCE BASE_MAP OUTPUT_ROOT
No network, legacy class references, OCR, segmentation, or image enhancement.
Public index is an explicit allowlist; per-crop image/RGB hashes stay private.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

SOURCE_SHA256 = '7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4'
BASE_SHA256 = 'f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34'
SOURCE_RGB_SHA256 = '5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94'
SOURCE_SIZE = (1785, 1175)
WHOLE = 'VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def context_box(box, size, right):
    x0, y0, x1, y1 = box
    px, py = (24, 16) if right else (16, 24)
    return [max(0, x0-px), max(0, y0-py), min(size[0], x1+px), min(size[1], y1+py)]


def validate_box(box, size):
    if (not isinstance(box, list) or len(box) != 4
            or any(type(v) is not int for v in box)):
        raise ValueError('Invalid half-open native box')
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1]):
        raise ValueError('Half-open native box outside source')


def rows_from_source(source, box):
    """Independent source-byte row extraction (does not call Image.crop)."""
    x0, y0, x1, y1 = box
    raw = source.tobytes()
    stride = source.width * 3
    return b''.join(raw[y*stride+x0*3:y*stride+x1*3] for y in range(y0, y1))


def native_crop(source, box, right):
    crop = source.crop(tuple(box))
    if crop.tobytes() != rows_from_source(source, box):
        raise ValueError('Native RGB source row mismatch')
    if right:
        rotated = crop.transpose(Image.Transpose.ROTATE_270)
        # Verify the exact clockwise mapping independently, plus inverse identity.
        old = crop.tobytes()
        expected = bytearray(len(old))
        for y in range(crop.height):
            for x in range(crop.width):
                a = (y*crop.width+x)*3
                b = (x*crop.height+(crop.height-1-y))*3
                expected[b:b+3] = old[a:a+3]
        if rotated.tobytes() != bytes(expected):
            raise ValueError('Exact clockwise transpose mismatch')
        if rotated.transpose(Image.Transpose.ROTATE_90).tobytes() != old:
            raise ValueError('Clockwise inverse mismatch')
        return rotated
    return crop


def select_records(base, size, source_hash, base_hash):
    conflicts = {i for c in base['frozen_overlay_conflicts'] for i in c['frozen_ids']}
    records = []
    seen = set()
    for layer, units in [('frozen', base['frozen_first_band']['units']), ('new', base['new_units'])]:
        for unit in units:
            if unit['physical_extent_status'] != WHOLE:
                continue
            uid = unit['id']
            if not isinstance(uid, str) or not uid or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-' for c in uid) or uid in seen:
                raise ValueError('Unsafe or duplicate physical ID')
            seen.add(uid)
            region = unit.get('region', '')
            right = region.startswith('right')
            if layer == 'new' and not (right or region.startswith('bottom')):
                raise ValueError('Unexpected whole-unit region')
            box = list(unit['native_bbox_xyxy_halfopen'])
            validate_box(box, size)
            ctx = context_box(box, size, right)
            rotation = 90 if right else 0
            sizes = [[b[3]-b[1], b[2]-b[0]] if right else [b[2]-b[0], b[3]-b[1]] for b in (box, ctx)]
            # Explicit allowlist: never copy geometric features, keys, labels,
            # raw references, aliases, or equivalence classes from the base.
            records.append({'id': uid, 'native_base_bbox_xyxy_halfopen': box,
                            'native_context_bbox_xyxy_halfopen': ctx,
                            'rotation_clockwise_degrees': rotation,
                            'envelope_size': sizes[0], 'context_size': sizes[1],
                            'source_sha256': source_hash, 'base_map_sha256': base_hash,
                            'frozen_overlay_conflict': layer == 'frozen' and uid in conflicts})
    return records


def json_bytes(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False)+'\n').encode('utf-8')


def build(source_path, base_path, output_root, *, expected_source=SOURCE_SHA256,
          expected_base=BASE_SHA256, expected_rgb=SOURCE_RGB_SHA256,
          expected_size=SOURCE_SIZE, enforce_inventory=True):
    source_path, base_path, output_root = map(Path, (source_path, base_path, output_root))
    source_bytes, base_bytes = source_path.read_bytes(), base_path.read_bytes()
    source_hash, base_hash = sha256(source_bytes), sha256(base_bytes)
    # All input/hash/inventory/path validation precedes the first output write.
    if source_hash != expected_source or base_hash != expected_base:
        raise ValueError('Pinned source/base SHA256 mismatch; no outputs written')
    with Image.open(source_path) as opened:
        if opened.mode != 'RGB' or opened.size != tuple(expected_size):
            raise ValueError('Pinned source RGB mode/size mismatch')
        source = opened.copy()
    if sha256(source.tobytes()) != expected_rgb:
        raise ValueError('Pinned source decoded RGB SHA256 mismatch')
    base = json.loads(base_bytes)
    if base['source'] != {'file_sha256': source_hash, 'size': list(source.size), 'rgb_sha256': expected_rgb}:
        raise ValueError('Base source reference mismatch')
    records = select_records(base, source.size, source_hash, base_hash)
    if enforce_inventory:
        units = base['frozen_first_band']['units'] + base['new_units']
        whole = [u for u in units if u['physical_extent_status'] == WHOLE]
        right = sum(r['rotation_clockwise_degrees'] == 90 for r in records)
        frozen_whole = sum(u['physical_extent_status'] == WHOLE for u in base['frozen_first_band']['units'])
        if (len(units), len(whole), len(records), right, frozen_whole,
            sum(r['frozen_overlay_conflict'] for r in records)) != (307, 172, 172, 107, 33, 16):
            raise ValueError('Frozen whole inventory mismatch')
    # Never let outputs overwrite input files, even under unusual CLI arguments.
    destinations = [output_root/'results'/'context-index-v1.json',
                    output_root/'results'/'feature-context-manifest-private-v1.json']
    for r in records:
        destinations.extend(output_root/'private-pixels'/f"{r['id']}-{kind}.png" for kind in ('envelope', 'context'))
    if any(p.resolve() in (source_path.resolve(), base_path.resolve()) for p in destinations):
        raise ValueError('Output would overwrite an immutable input')
    (output_root/'private-pixels').mkdir(parents=True, exist_ok=True)
    (output_root/'results').mkdir(parents=True, exist_ok=True)
    proofs = []
    for r in records:
        images = []
        for kind, key in [('envelope', 'native_base_bbox_xyxy_halfopen'), ('context', 'native_context_bbox_xyxy_halfopen')]:
            box = r[key]
            crop = native_crop(source, box, r['rotation_clockwise_degrees'] == 90)
            relative = Path('private-pixels') / f"{r['id']}-{kind}.png"
            path = output_root / relative
            crop.save(path, format='PNG')
            with Image.open(path) as decoded:
                if decoded.mode != 'RGB' or decoded.size != crop.size or decoded.tobytes() != crop.tobytes():
                    raise ValueError('Saved PNG decoded RGB mismatch')
            images.append({'kind': kind, 'private_path': str(relative), 'size': list(crop.size),
                           'png_sha256': sha256(path.read_bytes()), 'rgb_sha256': sha256(crop.tobytes()),
                           'native_source_rows_equal': True, 'saved_png_decoded_rgb_equal': True,
                           'right_exact_clockwise_mapping_and_inverse_equal': True if r['rotation_clockwise_degrees'] else None})
        proofs.append({**r, 'images': images})
    # Re-read inputs after generation: immutable source/map must still match bytes.
    if source_path.read_bytes() != source_bytes or base_path.read_bytes() != base_bytes:
        raise ValueError('Immutable inputs changed during generation')
    public = {'schema': 'source257-feature-context-index-v1', 'records': records}
    private = {'schema': 'source257-feature-context-manifest-private-v1',
               'private_only': True, 'source_sha256': source_hash, 'base_map_sha256': base_hash,
               'source_rgb_sha256': expected_rgb, 'source_size': list(source.size),
               'whole_count': len(records), 'png_count': len(records)*2,
               'native_unrotated_count': sum(r['rotation_clockwise_degrees'] == 0 for r in records),
               'right_clockwise_count': sum(r['rotation_clockwise_degrees'] == 90 for r in records),
               'conflict_count': sum(r['frozen_overlay_conflict'] for r in records),
               'source_and_base_unchanged_after_generation': True, 'records': proofs}
    destinations[0].write_bytes(json_bytes(public))
    destinations[1].write_bytes(json_bytes(private))
    return private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('base_map', type=Path)
    parser.add_argument('output_root', type=Path)
    args = parser.parse_args()
    manifest = build(args.source, args.base_map, args.output_root)
    print(json.dumps({k: manifest[k] for k in ('whole_count', 'png_count', 'native_unrotated_count', 'right_clockwise_count', 'conflict_count')}))


if __name__ == '__main__':
    main()
