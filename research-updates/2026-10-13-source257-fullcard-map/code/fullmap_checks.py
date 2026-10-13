#!/usr/bin/env python3
"""Validate closed record structure, not visual or historical truth.

CLI: FULLMAP FROZENFILE [--groups GROUPFILE] OUTPUT
FROZENFILE is explicitly selected by the operator. Its bytes are hashed and
compared with the full map declaration; its units must be exact deep copies.
The operator must independently pin that file's expected digest before use.
No records, roles, bounds, or groups are corrected by this validator.
Source quality and coverage states remain declarations, not visual proof.
New units retaining frozen overlaps cannot establish distinct repeat instances.
"""
import argparse
import hashlib
import json
from pathlib import Path

WHOLE = "VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION"
UNRESOLVED = "UNRESOLVED_SPAN"
SOURCE_SHA = "7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4"
SIZE = [1785, 1175]
SEMANTIC_FIELDS = {"letter", "letter_mapping", "plaintext", "cipher_letter", "alphabet", "semantic_mapping", "decoding"}


def validate(fullmap, frozen, frozen_sha, groups=None, expected_frozen_count=None):
    errors = []

    def error(location, message):
        errors.append({"location": location, "message": message})

    def array(value, location):
        if not isinstance(value, list):
            error(location, "must be a list")
            return []
        return value

    def object_(value, location):
        if not isinstance(value, dict):
            error(location, "must be an object")
            return {}
        return value

    def strings(value, location):
        items = array(value, location)
        if any(not isinstance(v, str) for v in items):
            error(location, "members must be strings")
        return items

    def box(value, location):
        if (not isinstance(value, list) or len(value) != 4
                or any(type(v) is not int for v in value)):
            error(location, "must be four integer native half-open coordinates; booleans are forbidden")
            return
        x0, y0, x1, y1 = value
        if not (0 <= x0 < x1 <= SIZE[0] and 0 <= y0 < y1 <= SIZE[1]):
            error(location, "must be nonempty and within native source bounds")

    def forbid_semantics(value, location):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in SEMANTIC_FIELDS:
                    error(location + "." + key, "semantic letter mapping is outside this geometry schema")
                forbid_semantics(child, location + "." + str(key))
        elif isinstance(value, list):
            for i, child in enumerate(value):
                forbid_semantics(child, f"{location}[{i}]")

    fullmap = object_(fullmap, "fullmap")
    source = object_(fullmap.get("source"), "source")
    if source.get("file_sha256") != SOURCE_SHA:
        error("source.file_sha256", "does not match the fixed source digest")
    source_size = source.get("size")
    if not isinstance(source_size, list) or source_size != SIZE or any(type(v) is not int for v in source_size):
        error("source.size", "must be native [1785,1175] integer dimensions")
    frozen_data = object_(frozen, "operator_frozen")
    expected_units = array(frozen_data.get("units"), "operator_frozen.units")
    band = object_(fullmap.get("frozen_first_band"), "frozen_first_band")
    if not isinstance(band.get("file_reference"), str) or not band.get("file_reference"):
        error("frozen_first_band.file_reference", "must identify the unchanged operator-selected original file")
    preserved_keys = strings(band.get("preserved_annotation_keys"), "frozen_first_band.preserved_annotation_keys")
    safe_keys = [key for key in preserved_keys if isinstance(key, str)]
    if len(safe_keys) != len(set(safe_keys)) or set(safe_keys) != set(frozen_data) - {"units"}:
        error("frozen_first_band.preserved_annotation_keys", "must reference every original top-level key other than units exactly once")
    if band.get("file_sha256") != frozen_sha:
        error("frozen_first_band.file_sha256", "does not match the operator-selected frozen file bytes")
    frozen_units = array(band.get("units"), "frozen_first_band.units")
    if expected_frozen_count is not None and len(expected_units) != expected_frozen_count:
        error("operator_frozen.units", f"must contain exactly {expected_frozen_count} frozen records")
    if json.dumps(frozen_units, sort_keys=True) != json.dumps(expected_units, sort_keys=True):
        error("frozen_first_band.units", "must equal the operator frozen records exactly, including order and every field")

    units = {}
    frozen_ids = set()
    new_units = array(fullmap.get("new_units"), "new_units")
    for kind, records in (("frozen_first_band.units", frozen_units), ("new_units", new_units)):
        for i, record in enumerate(records):
            location = f"{kind}[{i}]"
            record = object_(record, location)
            ident = record.get("id")
            if not isinstance(ident, str) or not ident:
                error(location + ".id", "must be a nonempty string")
            elif ident in units:
                error(location + ".id", "duplicate unit id")
            else:
                units[ident] = record
                if kind.startswith("frozen"):
                    frozen_ids.add(ident)
            if kind == "new_units":
                box(record.get("native_bbox_xyxy_halfopen"), location + ".native_bbox_xyxy_halfopen")
                if record.get("physical_extent_status") not in (WHOLE, UNRESOLVED):
                    error(location + ".physical_extent_status", "unknown physical extent declaration")
                if record.get("cipher_role") != "UNKNOWN":
                    error(location + ".cipher_role", "must preserve UNKNOWN")
                for field in ("geometric_features", "region"):
                    if not isinstance(record.get(field), str):
                        error(location + "." + field, "must be a string")
                array(record.get("ambiguities"), location + ".ambiguities")
                strings(record.get("evidence_views"), location + ".evidence_views")
                if type(record.get("order")) is not int:
                    error(location + ".order", "must be an integer, not boolean")
                overlap = strings(record.get("overlap_with_frozen_ids"), location + ".overlap_with_frozen_ids")
                if len([v for v in overlap if isinstance(v, str)]) != len(set(v for v in overlap if isinstance(v, str))):
                    error(location + ".overlap_with_frozen_ids", "duplicate frozen id")
                for ident_ in overlap:
                    if isinstance(ident_, str) and ident_ not in frozen_ids:
                        error(location + ".overlap_with_frozen_ids", "unknown frozen id")
            else:
                box(record.get("native_bbox_xyxy_halfopen"), location + ".native_bbox_xyxy_halfopen")

    conflicts = set()
    for i, conflict in enumerate(array(fullmap.get("frozen_overlay_conflicts"), "frozen_overlay_conflicts")):
        location = f"frozen_overlay_conflicts[{i}]"
        conflict = object_(conflict, location)
        ids = strings(conflict.get("frozen_ids"), location + ".frozen_ids")
        for ident in ids:
            if isinstance(ident, str):
                conflicts.add(ident)
                if ident not in frozen_ids:
                    error(location + ".frozen_ids", "unknown frozen id")
        box(conflict.get("native_bbox_xyxy_halfopen"), location + ".native_bbox_xyxy_halfopen")
        if not isinstance(conflict.get("detail"), str):
            error(location + ".detail", "must be a string")
    region_ids = set()
    for i, region in enumerate(array(fullmap.get("coverage_regions"), "coverage_regions")):
        location = f"coverage_regions[{i}]"
        region = object_(region, location)
        for field in ("id", "state", "detail"):
            if not isinstance(region.get(field), str):
                error(location + "." + field, "must be a string")
        rid = region.get("id")
        if isinstance(rid, str):
            if rid in region_ids:
                error(location + ".id", "duplicate coverage region id")
            region_ids.add(rid)
        box(region.get("bbox"), location + ".bbox")
    array(fullmap.get("source_quality"), "source_quality")

    assigned = set()
    if groups is not None:
        groups = object_(groups, "groups_file")
        group_ids = set()
        for i, group in enumerate(array(groups.get("groups"), "groups")):
            location = f"groups[{i}]"
            group = object_(group, location)
            gid = group.get("id")
            if not isinstance(gid, str) or not gid:
                error(location + ".id", "must be a nonempty string")
            elif gid in group_ids:
                error(location + ".id", "duplicate group id")
            else:
                group_ids.add(gid)
            members = strings(group.get("member_ids"), location + ".member_ids")
            safe_members = [m for m in members if isinstance(m, str)]
            if len(safe_members) < 2 or len(set(safe_members)) != len(safe_members):
                error(location + ".member_ids", "requires at least two unique members")
            for ident in safe_members:
                if ident not in units:
                    error(location + ".member_ids", "unknown member id: " + ident)
                elif units[ident].get("physical_extent_status") != WHOLE:
                    error(location + ".member_ids", "member is not a declared whole physical construction: " + ident)
                if ident in units and ident not in frozen_ids and units[ident].get("overlap_with_frozen_ids"):
                    error(location + ".member_ids", "new member retains unresolved frozen-instance overlap: " + ident)
                if ident in conflicts:
                    error(location + ".member_ids", "member has a frozen overlay conflict: " + ident)
                if ident in assigned:
                    error(location + ".member_ids", "unit occurs in more than one accepted flat group: " + ident)
                assigned.add(ident)
            if group.get("comparison_scope") not in ("VISIBLE_BODY_GEOMETRY", "WHOLE_CONSTRUCTION_GEOMETRY"):
                error(location + ".comparison_scope", "invalid geometry scope")
            if group.get("status") != "CHECKED_VISUAL_SIMILARITY":
                error(location + ".status", "must be CHECKED_VISUAL_SIMILARITY")
            for field in ("shared_features", "visual_evidence_views", "limits"):
                strings(group.get(field), location + "." + field)
            if not group.get("visual_evidence_views"):
                error(location + ".visual_evidence_views", "at least one declared evidence view is required")
        array(groups.get("deferred"), "deferred")
        remaining = strings(groups.get("ungrouped_unit_ids"), "ungrouped_unit_ids")
        safe_remaining = [v for v in remaining if isinstance(v, str)]
        if len(safe_remaining) != len(set(safe_remaining)):
            error("ungrouped_unit_ids", "duplicate id")
        if set(safe_remaining) != set(units) - assigned:
            error("ungrouped_unit_ids", "must contain exactly all units remaining outside accepted groups, including unresolved units")
        forbid_semantics(groups, "groups_file")
    forbid_semantics(new_units, "new_units")
    return {"schema": "fullmap-checks-v1", "valid": not errors, "errors": errors,
            "scope": "Closed record integrity and declared geometry constraints only; not visual or historical truth. Source quality and coverage states are declarations, not visual proof.",
            "operator_frozen_file_sha256": frozen_sha, "unit_count": len(units),
            "accepted_group_member_count": len(assigned), "inputs_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fullmap")
    parser.add_argument("frozenfile")
    parser.add_argument("--groups")
    parser.add_argument("output")
    args = parser.parse_args()
    if Path(args.output).resolve() in {Path(p).resolve() for p in (args.fullmap, args.frozenfile, args.groups) if p}:
        print(json.dumps({"valid": False, "errors": [{"location": "output", "message": "output must differ from every input"}]}))
        raise SystemExit(1)
    try:
        frozen_bytes = Path(args.frozenfile).read_bytes()
        result = validate(json.loads(Path(args.fullmap).read_text()), json.loads(frozen_bytes),
                          hashlib.sha256(frozen_bytes).hexdigest(),
                          json.loads(Path(args.groups).read_text()) if args.groups else None)
    except (OSError, ValueError, TypeError) as exc:
        result = {"schema": "fullmap-checks-v1", "valid": False,
                  "errors": [{"location": "input", "message": "Could not read or parse input: " + type(exc).__name__}], "inputs_modified": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"valid": result["valid"], "error_count": len(result["errors"])}))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
