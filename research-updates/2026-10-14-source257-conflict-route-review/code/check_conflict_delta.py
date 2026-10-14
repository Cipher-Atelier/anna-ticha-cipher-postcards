#!/usr/bin/env python3
"""Check compact D13 evidence delta and graph-only spatial membership refresh."""
import argparse
import csv
import io
import itertools
import json
from collections import Counter
from pathlib import Path

import conflict_delta as core


def check(delta, data):
    need = core.require
    need(delta["schema"] == "source257-conflict-route-delta-v1", "Delta schema invalid")
    rows = core.exact_rows(delta["pair_dispositions"], data["protocol"]["fixed_pair_ids"], "pair_id", "Delta38")
    need(len(delta["target_fact_references"]) == 29 and {r["id"] for r in delta["target_fact_references"]} == set(data["protocol"]["fixed_profile_ids"]), "Delta does not cover exact29 source facts")
    need(delta["baseline_reference"] == {"path": core.BASELINE_PATH, "sha256": core.BASELINE_SHA}, "Baseline identity changed")
    overlay = delta["current_graph_overlay"]
    baseline_edges = {e["pair_id"] for e in data["baseline"]["graph"]["positive_edges"]}
    removed = {q["pair_id"] for q in overlay["quarantined_baseline_edges"]}
    added = {key for key, (_, row) in rows.items() if row["status"] == "SOURCE_GATED_SAME_CANDIDATE"}
    need(removed <= baseline_edges and overlay["added_positive_pair_ids"] == sorted(added), "Quarantine overreach or unsupported new edge")
    current = (baseline_edges - removed) | added
    need(overlay["current_positive_pair_ids"] == sorted(current), "Current graph is not the exact add/quarantine overlay")
    need(overlay["baseline_historical_graph_unchanged"] is True and overlay["memberships_are_sets"] is True, "Historical graph mutated or memberships forced to partition")
    for group in overlay["maximal_edge_complete_cliques"]:
        members = group["member_ids"]
        needed = sorted("--".join(p) for p in itertools.combinations(sorted(members), 2))
        need(set(needed) <= current and group["edge_witness_pair_ids"] == needed, "Transitive-only/non-clique membership")
    need(delta["conditional772"] == {"state": "NOT_EXECUTED_NO_ADMISSION_PRELOG", "additional_comparisons": 0, "scope_expansion_authorized_by_this_output": False}, "Conditional branch executed without a separate admitted scope")
    # Rebuild from frozen source reports, preserving every uncertainty/correction.
    need(delta == core.build(data), "Delta differs from frozen-input source-gated assembly")
    return {"schema": "source257-conflict-route-delta-check-v1", "status": "PASS_SYNTHETIC_FIXTURE_ONLY" if delta["purpose"] == "SYNTHETIC_FIXTURE_ONLY" else "PASS_SOURCE_GATED_DELTA", "reviewed_pair_records": 38, "target_fact_records": 29, "pair_status_counts": dict(Counter(row["status"] for _, row in rows.values())), "new_positive_edges": len(added), "quarantined_baseline_edges": len(removed), "current_positive_edges": len(current), "maximal_cliques": len(overlay["maximal_edge_complete_cliques"]), "annotation_refs_reused": 307, "conditional772_executed": False, "source_pixel_io": "NONE_REQUIRED"}


def check_sequence(text, delta, data):
    require = core.require
    require(text.startswith("# ANNOTATION_RECORDS_NOT_GLYPHS; DISPLAY_ONLY_NOT_READING; UNKNOWN_LENGTH; BASELINE_SOURCE_GEOMETRY_UNCHANGED\n"), "TSV qualifications missing")
    lines = text.splitlines(keepends=True)
    rows = list(csv.DictReader(io.StringIO("".join(lines[1:])), delimiter="\t"))
    require(len(rows) == len({row["id"] for row in rows}) == 307, "TSV exact307 references changed")
    require(Counter(row["full_feature_label_status"] for row in rows) == {"ELIGIBLE_PROFILE_REFERENCE": 70, "UNKNOWN_FULL_FEATURE_LABEL": 102, "UNKNOWN_INTERNAL_PARTITION": 135}, "TSV source eligibility changed")
    require(all(r["sequence_length"] == "UNKNOWN_LENGTH" and r["cipher_unit_identity"] == "UNKNOWN" for r in rows), "TSV invents glyph count or identity")
    require(text == core.current_sequence_tsv(delta, data["baseline"]), "TSV changes baseline source geometry or current membership data")
    return {"status": "PASS_BASELINE_GEOMETRY_CURRENT_MEMBERSHIP_ONLY", "annotation_rows": 307}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, default=core.STAGE / "results")
    parser.add_argument("--sequence-tsv", type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()
    data, protected = core.load(args.repository_root, args.input_directory)
    raw = args.input.read_bytes()
    protected["delta"] = (args.input, core.sha(raw))
    delta = json.loads(raw)
    report = check(delta, data)
    if args.sequence_tsv:
        raw = args.sequence_tsv.read_bytes()
        protected["sequence"] = (args.sequence_tsv, core.sha(raw))
        report["sequence"] = check_sequence(raw.decode("utf-8"), delta, data)
    core.verify_unchanged(protected)
    if args.report_output:
        core.write_once(args.report_output, report, protected)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
