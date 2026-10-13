#!/usr/bin/env python3
"""Assemble explicit source adjudications; never infer a class from a profile.

All inputs are immutable. Decisions are separately reviewed source judgments.
This program checks their complete scope and emits reproducible metadata screens.
It performs no OCR, glyph classification, optimization, or letter assignment.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

from check_candidate_inventory import BASE_SHA256, SIGNATURE_FIELDS, WHOLE, validate_inventory

OUTPUT_NAMES = ('candidate-inventory-v1.json', 'candidate-pair-screen-v1.csv',
                'candidate-source-order-v1.csv', 'adjudication-evidence-v1.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def guard_paths(base_path, raw_paths, decision_path, output_dir):
    """Reject aliases before creating a directory or writing any output."""
    inputs = [base_path, *raw_paths, decision_path]
    require(len(raw_paths) == 4, 'exactly four independent raw inputs required')
    require(len({p.name for p in raw_paths}) == len(raw_paths), 'duplicate raw basename')
    require(len({p.resolve() for p in inputs}) == len(inputs), 'duplicate/aliased input path')
    for a, b in itertools.combinations(inputs, 2):
        require(not (a.exists() and b.exists() and a.samefile(b)), 'hardlinked input aliases')
    outputs = [output_dir / name for name in OUTPUT_NAMES]
    for out in outputs:
        for inp in inputs:
            require(out.resolve() != inp.resolve(), 'output aliases immutable input: ' + out.name)
            require(not (out.exists() and inp.exists() and out.samefile(inp)),
                    'output hardlink aliases immutable input: ' + out.name)
    for a, b in itertools.combinations(outputs, 2):
        require(a.resolve() != b.resolve(), 'outputs resolve to same path')
        require(not (a.exists() and b.exists() and a.samefile(b)), 'hardlinked output aliases')
    return outputs


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def assemble(base_path, raw_paths, decision_path, output_dir):
    paths = [base_path, *raw_paths, decision_path]
    guard_paths(base_path, raw_paths, decision_path, output_dir)
    snapshots = {p: p.read_bytes() for p in paths}
    require(sha(snapshots[base_path]) == BASE_SHA256, 'base pin mismatch')
    base = json.loads(snapshots[base_path])
    decisions = json.loads(snapshots[decision_path])
    raw = {}
    for path in raw_paths:
        require(sha(snapshots[path]) == decisions['raw_input_sha256'][path.name], 'raw pin mismatch: ' + path.name)
        data = json.loads(snapshots[path])
        rows = {r.get('unit_id', r.get('id')): r for r in data['records']}
        require(len(rows) == len(data['records']), 'duplicate raw ID')
        raw[path.name] = rows
    all_units = base['frozen_first_band']['units'] + base['new_units']
    whole = {u['id']: u for u in all_units if u['physical_extent_status'] == WHOLE}
    chosen = decisions['records']
    require(set(chosen) == set(whole), 'decisions must cover all WHOLE records')
    records, reconciliations = [], []
    for uid, unit in whole.items():
        d = chosen[uid]
        require(set(d['significant_signature']) == set(SIGNATURE_FIELDS), uid + ' signature fields')
        sources = {name: rows[uid] for name, rows in raw.items() if uid in rows}
        require(len(sources) == 2, uid + ' must have paired independent source audits')
        row = dict(id=uid, base_native_bbox_xyxy_halfopen=unit['native_bbox_xyxy_halfopen'],
                   source_target_status=d['source_target_status'], significant_signature=d['significant_signature'],
                   mark_ownership_status=d['mark_ownership_status'], candidate_eligible=d['candidate_eligible'],
                   exclusion_reasons=d['exclusion_reasons'], evidence_views=d['evidence_views'],
                   cipher_role='UNKNOWN', letter_value='UNKNOWN',
                   source_adjudication=d['source_adjudication'])
        if 'observed_target_bbox_xyxy_halfopen' in d:
            row['observed_target_bbox_xyxy_halfopen'] = d['observed_target_bbox_xyxy_halfopen']
        records.append(row)
        observations = {}
        for name, r in sources.items():
            observations[name] = {k: v for k, v in r.items() if k in (
                'source_body_boundary_status', 'visible_connected_path', 'visible_connected_paths',
                'visible_branches', 'visible_loops', 'visible_opening', 'attached_bar_locations',
                'visible_endpoints', 'connected_extra_strokes', 'local_marks', 'local_mark_status',
                'mark_ownership_status', 'significant_feature_signature', 'full_sign_candidate_eligibility',
                'exclusion_reasons', 'exclusions', 'comparison_variants', 'variant_differences')}
        reconciliations.append(dict(id=uid, paired_observations=observations,
                                    reconciliation=d['source_adjudication'],
                                    preserved_variation=d.get('preserved_variation', [])))
    classes = decisions['candidate_classes']
    member_to_class = {u: c['id'] for c in classes for u in c['member_ids']}
    inventory = dict(schema='source257-full-visible-feature-candidate-inventory-v1',
                     base_map_sha256=BASE_SHA256, records=records, candidate_classes=classes,
                     eligible_singleton_ids=[r['id'] for r in records if r['candidate_eligible'] and r['id'] not in member_to_class],
                     excluded_whole_ids=[r['id'] for r in records if not r['candidate_eligible']],
                     unresolved_source_ids=[u['id'] for u in all_units if u['physical_extent_status'] != WHOLE],
                     source_limits=decisions['source_limits'])
    counts = validate_inventory(inventory, base, base_hash=BASE_SHA256)
    require(all(p.read_bytes() == data for p, data in snapshots.items()), 'input changed before output')
    guard_paths(base_path, raw_paths, decision_path, output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    invpath = output_dir / 'candidate-inventory-v1.json'
    write_json(invpath, inventory)
    index = {r['id']: r for r in records}
    outcomes = {}
    with (output_dir / 'candidate-pair-screen-v1.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['unit_a', 'unit_b', 'outcome', 'reasons', 'source_comparison_ref'])
        for a, b in itertools.combinations(sorted(whole), 2):
            left, right = index[a], index[b]
            if not (left['candidate_eligible'] and right['candidate_eligible']):
                outcome, reason, ref = 'ELIGIBILITY_BLOCKED', 'At least one complete-feature or ownership decision remains excluded.', 'adjudication-evidence-v1.json#' + a + '+' + b
            elif a in member_to_class and member_to_class.get(a) == member_to_class.get(b):
                outcome, reason, ref = 'CLASS_CANDIDATE_SAME', 'Every significant feature compared in verified whole target and context; same full signature.', 'candidate-inventory-v1.json#' + member_to_class[a]
            elif left['significant_signature'] != right['significant_signature']:
                fields = [k for k in SIGNATURE_FIELDS if left['significant_signature'][k] != right['significant_signature'][k]]
                outcome, reason, ref = 'STRUCTURAL_DIFFERENCE', 'Declared known significant signature differs: ' + ', '.join(fields), 'candidate-inventory-v1.json#' + a + '+' + b
            else:
                outcome, reason, ref = 'SOURCE_COMPARISON_DEFERRED', 'Same coarse full-feature profile; no accepted all-pair source comparison for this pair.', 'adjudication-evidence-v1.json#unreviewed-compatible-pairs'
            writer.writerow([a, b, outcome, reason, ref])
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
    with (output_dir / 'candidate-source-order-v1.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['source_order', 'unit_id', 'region', 'base_native_bbox_xyxy_halfopen', 'physical_extent_status', 'candidate_status', 'candidate_class', 'cipher_role', 'letter_value'])
        for n, u in enumerate(all_units, 1):
            uid = u['id']
            status = 'UNRESOLVED_PHYSICAL_SPAN_PLACEHOLDER' if uid not in index else ('ELIGIBLE_SINGLETON' if index[uid]['candidate_eligible'] else 'EXCLUDED_WHOLE')
            if uid in member_to_class:
                status = 'FULL_VISIBLE_FEATURE_CANDIDATE'
            writer.writerow([n, uid, u.get('region', 'frozen-first-band'), json.dumps(u['native_bbox_xyxy_halfopen']), u['physical_extent_status'], status, member_to_class.get(uid, ''), 'UNKNOWN', 'UNKNOWN'])
    evidence = dict(schema='source257-candidate-adjudication-evidence-v1',
                    source_proof=decisions['source_proof'], raw_input_sha256=decisions['raw_input_sha256'],
                    base_map_sha256=BASE_SHA256, decision_input_sha256=sha(snapshots[decision_path]),
                    counts=counts, pair_outcomes=outcomes,
                    pair_screen_scope='14706 metadata comparisons; positive source claims only for explicitly checked internal class pairs. The screen is not 14706 visual identity judgments.',
                    method=decisions['method'], source_limits=decisions['source_limits'],
                    decision_cases=decisions['decision_cases'], negative_body_lookalikes=decisions['negative_body_lookalikes'],
                    records=reconciliations)
    write_json(output_dir / 'adjudication-evidence-v1.json', evidence)
    require(all(p.read_bytes() == data for p, data in snapshots.items()), 'input changed during assembly')
    return dict(**counts, pair_outcomes=outcomes, pair_count=sum(outcomes.values()), inventory_sha256=sha(invpath.read_bytes()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True)
    for name in ['bottom-a', 'bottom-b', 'right-a', 'right-b']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--decisions', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(assemble(a.base, [a.bottom_a, a.bottom_b, a.right_a, a.right_b], a.decisions, a.output_dir)))


if __name__ == '__main__':
    main()
