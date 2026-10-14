#!/usr/bin/env python3
"""Canonical coverage, three-gate provenance, clique and spatial invariants."""
import argparse
import copy
import csv
import io
import json
from collections import Counter
from pathlib import Path

import canonical_repeat_evidence as core
from check_spatial_preparation import check as check_spatial


def check(output, data):
    need = core.need
    need(output["schema"] == "source257-canonical-repeat-evidence-v1", "Wrong canonical schema")
    expected = core.build(data)
    scope = {p["pair_id"] for p in data["core_pairs"]["pairs"]}
    rows = core.indexed(output["core_pairs"], scope, "Canonical930")
    closure_scope = {r["pair_id"] for r in data["closure_prelog"]["requests"]}
    core.indexed(output["closure_pairs"], closure_scope, "Canonical closure12")
    allowed = {core.ACCEPTED, "DEFERRED"}
    need(all(row["status"] in allowed for _, row in rows.values()), "Unsupported canonical status or derived negative promoted")
    need(output["summary"]["accepted_different_graphics"] == 0, "Single/derived negative cannot be accepted")
    for key, (_, row) in rows.items():
        a = core.resolve(data, row["reader_A"]["raw_reference"])
        b = core.resolve(data, row["reader_B"]["raw_reference"])
        need(a["pair_id"] == b["pair_id"] == key, "Canonical reader ref bound to wrong pair")
        need(a["status"] == row["reader_A"]["status"] and b["status"] == row["reader_B"]["status"], "Reader disagreement/status rewritten")
        need(row["reader_A"]["coverage"] == a["source_coverage"] and row["reader_B"]["coverage"] == b["coverage"], "Reader coverage upgraded")
        if row["status"] == core.ACCEPTED:
            need(a["status"] == b["status"] == core.SAME, "Missing two-reader positive gate")
            need(a["source_coverage"] == b["coverage"] == "DIRECT_PAIRED_SOURCE_COMPARISON", "Derived/prescreen edge promoted")
            review = core.resolve(data, row["final_AI_reference"])
            need(review["pair_id"] == key and review["decision"] == core.ACCEPT, "FinalAI gate missing/deferred")
            need(core.resolve(data, row["reader_B_actual_confirmation_reference"])["pair_id"] == key, "B actual paired confirmation missing")
            need(row["deferred_reason"] is None, "Accepted pair retains unresolved deferral")
        else:
            need(bool(row["deferred_reason"]), "Deferred pair has no reason")
    # Verify all source pointers resolve to the raw frozen fields, not profile-text matches.
    for ident, features in output["source_feature_witnesses"].items():
        need(set(features) == set(core.FIELDS), "Canonical source witness inventory missing dimension")
        for field, refs in features.items():
            for reference in refs.values():
                core.resolve(data, reference)
            need(ident in refs["reader_B_feature_witness"]["json_pointer"], "Source witness points to wrong profile")
    need(output["graph"] == output["spatial"]["graph"], "Graph/spatial membership mismatch")
    accepted_ids = {r["pair_id"] for r in output["core_pairs"] + output["closure_pairs"] if r["status"] == core.ACCEPTED}
    inherited = {e["pair_id"] for e in data["inherited"]["positive_edges"]}
    need({e["pair_id"] for e in output["graph"]["positive_edges"]} == accepted_ids | inherited, "Unsupported graph edge or inherited edge omitted")
    # Reuse frozen geometric checker by explicitly restoring its preparation envelope;
    # all actual window geometry, UNKNOWN semantics, memberships and cliques are checked.
    geometric = copy.deepcopy(output["spatial"])
    need(geometric["schema"] == "source257-canonical-spatial-repeat-v1", "Wrong canonical spatial schema")
    expected_handling = "CURRENT_ENCODED_BYTES_HASH_VERIFIED_NO_PIXEL_DECODE_OR_VIEW" if data.get("_current_encoded_verification") else "PINNED_READER_ORIGINAL_SOURCE_PROOFS_AND_D9_METADATA_NO_CURRENT_PIXEL_OR_JPEG_READ"
    need(geometric["source_pixel_handling"] == expected_handling, "Canonical falsely claims a current source/JPEG read")
    geometric["schema"] = "source257-spatial-preparation-v1"
    geometric["purpose"] = "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL"
    geometric["graph"]["purpose"] = "PREPARATION_ONLY_NOT_SCIENTIFIC_FINAL"
    geometric["graph"]["evidence_validation"] = "STRUCTURAL_REFERENCES_ONLY_CANONICAL_PAIR_GATES_PENDING"
    geometric["source_pixel_handling"] = "ENCODED_BYTES_HASHED_NO_PIXEL_DECODE_OR_VIEW"
    spatial_report = check_spatial(geometric, data)
    need(output == expected, "Canonical evidence differs from deterministic frozen-input assembly")
    return {"schema": "source257-canonical-repeat-evidence-validation-v1", "status": "PASS_SYNTHETIC_FIXTURE_ONLY" if output["purpose"] == "SYNTHETIC_FIXTURE_ONLY_NOT_SCIENTIFIC" else "PASS_CANONICAL_SOURCE_GATES", "core_pairs": 930, "closure_pairs": 12, "accepted_different_graphics": 0, "core_status_counts": dict(Counter(r["status"] for r in output["core_pairs"])), "closure_status_counts": dict(Counter(r["status"] for r in output["closure_pairs"])), "positive_edges_including_inherited": len(output["graph"]["positive_edges"]), "maximal_edge_complete_cliques": len(output["graph"]["maximal_cliques"]), "spatial_annotation_refs": spatial_report["annotation_refs"], "source_pixel_io": "NONE_REQUIRED"}


def check_sequence_tsv(text, canonical):
    core.need(text.startswith(core.TSV_NOTICE), "TSV annotations/display/UNKNOWN qualification missing")
    rows = list(csv.DictReader(io.StringIO(text[len(core.TSV_NOTICE):]), delimiter="\t"))
    core.need(len(rows) == len({r["id"] for r in rows}) == 307, "TSV must contain307 distinct annotation IDs")
    labels = Counter(row["full_feature_label_status"] for row in rows)
    core.need(labels == {"ELIGIBLE_PROFILE_REFERENCE": 70, "UNKNOWN_FULL_FEATURE_LABEL": 102, "UNKNOWN_INTERNAL_PARTITION": 135}, "TSV wrong70/102/135 scope")
    core.need(all(row["sequence_length"] == "UNKNOWN_LENGTH" and row["cipher_unit_identity"] == "UNKNOWN" for row in rows), "TSV invented unit length/identity")
    core.need(text == core.sequence_tsv(canonical), "TSV row differs from validated canonical source/graph/display data")
    return {"annotation_rows": 307, "eligible_profiles": 70, "excluded_unknown_labels": 102, "unresolved_records": 135, "status": "PASS_TSV_CANONICAL_ROUNDTRIP"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--root", type=Path, default=core.spatial.DEFAULT_ROOT)
    parser.add_argument("--stage", type=Path, default=core.spatial.STAGE)
    parser.add_argument("--public-repository-root", type=Path)
    parser.add_argument("--public-data-directory", type=Path)
    parser.add_argument("--published-data-relative")
    parser.add_argument("--verify-original-source", type=Path)
    for name in ("final-core", "final-closure"):
        parser.add_argument("--" + name, type=Path, required=True)
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--report-output", type=Path)
    parser.add_argument("--sequence-tsv", type=Path)
    args = parser.parse_args()
    if args.public_repository_root or args.public_data_directory:
        core.need(args.public_repository_root is not None and args.public_data_directory is not None, "Public repository root and data directory must be supplied together")
        from public_repeat_bindings import load as load_public
        data, protected = load_public(args.public_repository_root, args.public_data_directory, published_data_relative=args.published_data_relative)
    else:
        data, protected = core.load(args.root, args.stage)
    for name in ("final_core", "final_closure"):
        core.attach_review(data, protected, name, getattr(args, name), getattr(args, name + "_sha256"))
    if args.verify_original_source:
        core.need(core.spatial.sha(args.verify_original_source.read_bytes()) == core.spatial.SOURCE[1], "Optional current source encoded pin mismatch")
        protected["optional_current_source"] = (args.verify_original_source, core.spatial.SOURCE[1])
        data["_current_encoded_verification"] = {"sha256": core.spatial.SOURCE[1], "method": "CURRENT_ENCODED_BYTES_HASH_ONLY_NO_PIXEL_DECODE_OR_VIEW"}
    need = core.need
    need(not args.input.is_symlink(), "Canonical input cannot be symlink")
    raw = args.input.read_bytes()
    protected["canonical_output"] = (args.input, core.spatial.sha(raw))
    report = check(json.loads(raw), data)
    if args.sequence_tsv:
        tsv_raw = args.sequence_tsv.read_bytes()
        protected["sequence_tsv"] = (args.sequence_tsv, core.spatial.sha(tsv_raw))
        report["sequence_tsv"] = check_sequence_tsv(tsv_raw.decode("utf-8"), json.loads(raw))
    core.spatial.verify_unchanged(protected)
    if args.report_output:
        core.spatial.write_once(args.report_output, report, protected)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
