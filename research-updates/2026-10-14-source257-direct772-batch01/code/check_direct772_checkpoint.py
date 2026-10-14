#!/usr/bin/env python3
"""Check exact source-gated checkpoint and optional human-readable queue TSV."""
import argparse
import json
from pathlib import Path
import direct772_checkpoint as core


def check(result, data, fixture=False):
    rows = result["pairs"]
    core.need(len(rows) == 772 and [(r["ordinal"], r["pair_id"], r["member_ids"]) for r in rows] == [(r["ordinal"], r["pair_id"], r["member_ids"]) for r in data["queue"]["ordered_queue"]], "Checkpoint exact772/order/member binding changed")
    for row in rows[:64]:
        core.need(row["inspection_status"] == "CHECKED_BY_TWO_SOURCE_READERS_AND_FINAL_AI" and row["source_observation"] in {core.REPEAT, core.DIFFERENCE, core.UNCERTAIN} and set(row["source_reports"]) == {"reader_A", "reader_B", "final_review"}, "Checked prefix lacks actual three-report evidence")
    for row in rows[64:]:
        core.need(row == {**data["queue"]["ordered_queue"][row["ordinal"] - 1], "inspection_status": "NOT_INSPECTED"}, "Uninspected pair must not acquire observation/uncertainty verdict or fake evidence")
    core.need(result == core.build(data, fixture=fixture), "Saved checkpoint differs from complete evidence rebuild")
    return {"schema": "source257-direct772-checkpoint-check-v1", "status": "PASS_SYNTHETIC_FIXTURE" if fixture else "PASS_PINNED_SOURCE_ATTESTED_CHECKPOINT", "queue_pairs": 772, "checked_pairs": 64, "not_inspected": 708, "source_profiles_per_report": 36, "boards_per_report": 16, "next_ordinal": 65, "next_pair": result["checkpoint"]["next_pair"], "source_observation_counts": result["checkpoint"]["checked_source_observation_counts"], "graph_and_sequence": "REUSED_UNCHANGED", "source_pixel_io": "NONE_REQUIRED"}


def check_tsv(text, result):
    core.need(text == core.queue_tsv(result), "Queue TSV tampering/scope/status mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, default=core.STAGE / "results")
    parser.add_argument("--queue-tsv", type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()
    data, protected = core.load(args.repository_root, args.input_directory)
    protected["checked_checkpoint"] = (args.checkpoint, core.digest(args.checkpoint.read_bytes()))
    result = json.loads(args.checkpoint.read_text())
    receipt = check(result, data)
    if args.queue_tsv:
        protected["checked_tsv"] = (args.queue_tsv, core.digest(args.queue_tsv.read_bytes()))
        check_tsv(args.queue_tsv.read_text(), result)
    core.verify_unchanged(protected)
    if args.report_output:
        core.write_once(args.report_output, receipt, protected)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
