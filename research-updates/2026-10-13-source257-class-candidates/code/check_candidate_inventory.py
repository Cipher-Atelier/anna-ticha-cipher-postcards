#!/usr/bin/env python3
"""Validate physical candidate inventory structure, not visual judgments.

CLI: check_candidate_inventory.py INVENTORY BASEMAP OUTPUT [--pair-screen CSV]
Pinned base, whole-ID geometry, eligibility and full-signature equality are
mechanically checked. Source observations and grouping support need separate
human review. No source pixels, classifier, OCR, historical keys, or network.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re

BASE_SHA256 = 'f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34'
WHOLE = 'VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION'
SIGNATURE_FIELDS = ('path_topology', 'enclosures', 'openings', 'stem_pattern',
                    'attached_bars', 'connected_extra_strokes', 'terminal_pattern', 'owned_mark_profile')
TARGET_STATES = {'SUPPORTED_WHOLE_TARGET', 'UNCERTAIN_TARGET'}
MARK_STATES = {'NO_VISIBLE_COMPETING_MARK_IN_CONTEXT', 'CONTINUOUS_ATTACHED_PARTS_ONLY',
               'UNRESOLVED', 'BACKGROUND_CONFUNDED'}
RESOLVED_MARK_STATES = {'NO_VISIBLE_COMPETING_MARK_IN_CONTEXT', 'CONTINUOUS_ATTACHED_PARTS_ONLY'}
PAIR_FIELDS = ('unit_a', 'unit_b', 'outcome', 'reasons', 'source_comparison_ref')
PAIR_OUTCOMES = {'CLASS_CANDIDATE_SAME', 'STRUCTURAL_DIFFERENCE', 'ELIGIBILITY_BLOCKED', 'SOURCE_COMPARISON_DEFERRED'}
UNKNOWN_WORD = re.compile(r'(?<![A-Za-z0-9])(?:UNKNOWN|AMBIGUOUS|UNESTABLISHED|UNRESOLVED|UNCERTAIN|INDETERMINATE)(?![A-Za-z0-9])', re.I)


class InventoryError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InventoryError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def text_list(value, name, nonempty=True):
    require(isinstance(value, list) and all(text(v) for v in value), name + ' must be a list of nonempty strings')
    require(not nonempty or bool(value), name + ' must not be empty')


def id_list(value, name):
    text_list(value, name, nonempty=False)
    require(len(value) == len(set(value)), name + ' contains duplicate IDs')
    return set(value)


def signature(value, name, eligible):
    require(isinstance(value, dict) and set(value) == set(SIGNATURE_FIELDS), name + ' must have exactly the canonical signature fields')
    for key in SIGNATURE_FIELDS:
        require(text(value[key]), name + '.' + key + ' must be a nonempty string')
        if eligible:
            require(not UNKNOWN_WORD.search(value[key]), name + '.' + key + ' is unresolved for an eligible unit')


def base_inventory(base, expected_whole, expected_unresolved):
    try:
        all_units = base['frozen_first_band']['units'] + base['new_units']
        require(all(isinstance(u, dict) and text(u.get('id')) for u in all_units), 'Base units malformed')
        ids = [u['id'] for u in all_units]
        require(len(ids) == len(set(ids)), 'Duplicate base IDs')
        whole = {u['id']: u for u in all_units if u['physical_extent_status'] == WHOLE}
        unresolved = set(ids) - set(whole)
        frozen_ids = {u['id'] for u in base['frozen_first_band']['units']}
        conflicts = {uid for c in base['frozen_overlay_conflicts'] for uid in c['frozen_ids']} & frozen_ids
    except (KeyError, TypeError) as exc:
        raise InventoryError('Malformed base inventory: ' + str(exc)) from exc
    require(len(whole) == expected_whole, 'Base whole count mismatch')
    require(len(unresolved) == expected_unresolved, 'Base unresolved count mismatch')
    return whole, unresolved, conflicts


def validate_inventory(inventory, base, *, base_hash, expected_whole=172, expected_unresolved=135):
    require(isinstance(inventory, dict), 'Inventory must be an object')
    require(inventory.get('base_map_sha256') == base_hash, 'Inventory base_map_sha256 mismatch')
    whole, unresolved, conflicts = base_inventory(base, expected_whole, expected_unresolved)
    rows = inventory.get('records')
    require(isinstance(rows, list), 'records must be a list')
    require(all(isinstance(r, dict) and text(r.get('id')) for r in rows), 'Malformed record ID')
    row_ids = [r['id'] for r in rows]
    require(len(row_ids) == len(set(row_ids)), 'Duplicate record IDs')
    require(set(row_ids) == set(whole), 'records must cover exactly every base WHOLE ID')
    records = {r['id']: r for r in rows}
    for uid, row in records.items():
        require(row.get('base_native_bbox_xyxy_halfopen') == whole[uid]['native_bbox_xyxy_halfopen'], uid + ' base bbox changed')
        # bool/float coordinates compare equal to ints in Python: require types too.
        box = row.get('base_native_bbox_xyxy_halfopen')
        require(isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box), uid + ' bbox must be four exact integer coordinates')
        require(row.get('source_target_status') in TARGET_STATES, uid + ' invalid target status')
        require(row.get('mark_ownership_status') in MARK_STATES, uid + ' invalid mark ownership status')
        require(type(row.get('candidate_eligible')) is bool, uid + ' candidate_eligible must be bool')
        require(row.get('cipher_role') == 'UNKNOWN' and row.get('letter_value') == 'UNKNOWN', uid + ' cipher role/letter assignment forbidden')
        text_list(row.get('exclusion_reasons'), uid + ' exclusion_reasons', nonempty=False)
        text_list(row.get('evidence_views'), uid + ' evidence_views')
        eligible = row['candidate_eligible']
        signature(row.get('significant_signature'), uid + ' significant_signature', eligible)
        if eligible:
            require(row['source_target_status'] == 'SUPPORTED_WHOLE_TARGET', uid + ' eligible target must be supported whole')
            require(row['mark_ownership_status'] in RESOLVED_MARK_STATES, uid + ' unresolved mark ownership blocks eligibility')
            require(uid not in conflicts, uid + ' frozen overlay conflict blocks eligibility')
            require(uid not in unresolved, uid + ' base unresolved ID blocks eligibility')
            require(not row['exclusion_reasons'], uid + ' eligible record has exclusion reasons')
        else:
            require(bool(row['exclusion_reasons']), uid + ' deferred record needs exclusion reason')
    classes = inventory.get('candidate_classes')
    require(isinstance(classes, list), 'candidate_classes must be a list')
    class_ids = []
    grouped = []
    for group in classes:
        require(isinstance(group, dict), 'Malformed candidate class')
        cid = group.get('id')
        require(isinstance(cid, str) and re.fullmatch(r'SCG[0-9]{3}', cid) is not None, 'Class ID must be SCG###')
        class_ids.append(cid)
        members = group.get('member_ids')
        member_set = id_list(members, cid + ' member_ids')
        require(len(member_set) >= 2, cid + ' requires at least two unique members')
        require(member_set <= set(records), cid + ' includes IDs outside base WHOLE records')
        require(group.get('status') == 'FULL_VISIBLE_FEATURE_CANDIDATE', cid + ' invalid status')
        require(group.get('cipher_identity') == 'UNESTABLISHED' and group.get('letter_value') == 'UNKNOWN', cid + ' cipher identity/letter assignment forbidden')
        signature(group.get('significant_signature'), cid + ' significant_signature', True)
        text_list(group.get('merge_grounds'), cid + ' merge_grounds')
        # Excluded lookalikes may be structured source observations or ID strings;
        # only listness is structural, visual support is reviewed separately.
        require(isinstance(group.get('excluded_lookalikes'), list), cid + ' excluded_lookalikes must be a list')
        text_list(group.get('source_evidence_views'), cid + ' source_evidence_views')
        for uid in members:
            require(records[uid]['candidate_eligible'], cid + ' contains ineligible member ' + uid)
            require(group['significant_signature'] == records[uid]['significant_signature'], cid + ' full significant signature differs for ' + uid)
        grouped.extend(members)
    require(len(class_ids) == len(set(class_ids)), 'Duplicate candidate class IDs')
    require(len(grouped) == len(set(grouped)), 'Same physical unit appears in multiple candidate classes')
    singletons = id_list(inventory.get('eligible_singleton_ids'), 'eligible_singleton_ids')
    excluded = id_list(inventory.get('excluded_whole_ids'), 'excluded_whole_ids')
    preserved_unresolved = id_list(inventory.get('unresolved_source_ids'), 'unresolved_source_ids')
    require(preserved_unresolved == unresolved, 'unresolved_source_ids must preserve exactly every base unresolved ID')
    require(excluded == {uid for uid, r in records.items() if not r['candidate_eligible']}, 'excluded_whole_ids must exactly match false eligibility')
    require(singletons <= {uid for uid,r in records.items() if r['candidate_eligible']}, 'Singleton contains ineligible or non-WHOLE ID')
    partitions = [set(grouped), singletons, excluded]
    require(not any(a & b for a,b in itertools.combinations(partitions, 2)), 'WHOLE partitions overlap')
    require(set.union(*partitions) == set(whole), 'Classes/singletons/exclusions must partition every base WHOLE ID')
    require(not unresolved & (set(grouped) | singletons | excluded), 'Unresolved source IDs cannot enter WHOLE partitions')
    text_list(inventory.get('source_limits'), 'source_limits')
    if 'FC136' in unresolved:
        require(any('FC136' in limit for limit in inventory['source_limits']), 'source_limits must retain physical-cut unresolved reference FC136')
    return {'whole_count':len(records), 'unresolved_source_count':len(unresolved), 'eligible_count':len(records)-len(excluded),
            'excluded_whole_count':len(excluded), 'candidate_class_count':len(classes),
            'grouped_whole_count':len(grouped), 'eligible_singleton_count':len(singletons)}


def validate_pair_screen(path, whole_ids, *, inventory=None):
    expected = set(itertools.combinations(sorted(whole_ids), 2))
    seen = set()
    records = None
    class_by_member = {}
    if inventory is not None:
        # check_files validates the complete inventory before passing it here.
        # API callers may explicitly supply their already validated fixture.
        records = {r['id']: r for r in inventory['records']}
        require(set(records) == set(whole_ids), 'Pair-screen inventory WHOLE IDs mismatch')
        class_by_member = {uid: group['id'] for group in inventory['candidate_classes'] for uid in group['member_ids']}
    with Path(path).open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == list(PAIR_FIELDS), 'Pair-screen CSV columns must match canonical order')
        for number, row in enumerate(reader, 2):
            require(None not in row and all(isinstance(row.get(k), str) for k in PAIR_FIELDS), 'Malformed pair-screen row ' + str(number))
            a,b = row['unit_a'], row['unit_b']
            require(a != b and a in whole_ids and b in whole_ids, 'Pair-screen contains invalid/self/non-WHOLE ID at row ' + str(number))
            pair = tuple(sorted((a,b)))
            require(pair not in seen, 'Duplicate unordered pair-screen row ' + str(number))
            require(row['outcome'] in PAIR_OUTCOMES, 'Invalid pair-screen outcome at row ' + str(number))
            require(text(row['reasons']) and text(row['source_comparison_ref']), 'Pair-screen row needs reasons and source comparison reference')
            if records is not None:
                left, right = records[a], records[b]
                outcome = row['outcome']
                if not (left['candidate_eligible'] and right['candidate_eligible']):
                    require(outcome == 'ELIGIBILITY_BLOCKED', 'Ineligible pair must be ELIGIBILITY_BLOCKED at row ' + str(number))
                else:
                    same_signature = left['significant_signature'] == right['significant_signature']
                    same_class = a in class_by_member and class_by_member.get(a) == class_by_member.get(b)
                    if same_class:
                        require(same_signature and outcome == 'CLASS_CANDIDATE_SAME', 'Internal declared-class pair must be full-signature CLASS_CANDIDATE_SAME at row ' + str(number))
                    elif not same_signature:
                        require(outcome == 'STRUCTURAL_DIFFERENCE', 'Different eligible signatures must be STRUCTURAL_DIFFERENCE at row ' + str(number))
                    else:
                        require(outcome in {'SOURCE_COMPARISON_DEFERRED', 'STRUCTURAL_DIFFERENCE'}, 'Equal-signature pair outside a declared class cannot claim SAME at row ' + str(number))
            seen.add(pair)
    require(seen == expected, 'Pair-screen must cover exactly all unordered WHOLE pairs')
    return {'pair_screen_count':len(seen), 'expected_pair_screen_count':len(expected),
            'pair_screen_inventory_outcomes_checked': inventory is not None,
            'pair_screen_scope':'DECLARED_STRUCTURE_AND_OUTCOMES_ONLY_NOT_VISUAL_TRUTH_VALIDATION'}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_files(inventory_path, base_path, output_path, *, pair_screen=None,
                expected_base=BASE_SHA256, expected_whole=172, expected_unresolved=135):
    inventory_path, base_path, output_path = map(Path, (inventory_path,base_path,output_path))
    inputs = [inventory_path,base_path] + ([Path(pair_screen)] if pair_screen is not None else [])
    require(output_path.resolve() not in {p.resolve() for p in inputs}, 'Output path must differ from every input')
    if output_path.exists():
        require(not any(output_path.samefile(p) for p in inputs), 'Output aliases an immutable input')
    snapshots = {p:p.read_bytes() for p in inputs}
    require(sha256(snapshots[base_path]) == expected_base, 'Pinned base-map SHA256 mismatch')
    inventory, base = json.loads(snapshots[inventory_path]), json.loads(snapshots[base_path])
    counts = validate_inventory(inventory, base, base_hash=expected_base,
                                expected_whole=expected_whole, expected_unresolved=expected_unresolved)
    if pair_screen is not None:
        counts.update(validate_pair_screen(pair_screen, {r['id'] for r in inventory['records']}, inventory=inventory))
    require(all(p.read_bytes() == data for p,data in snapshots.items()), 'Immutable validation input changed during check')
    result = {'schema':'source257-class-candidate-inventory-validation-v1', 'status':'PASS',
              'base_map_sha256':expected_base, 'inventory_sha256':sha256(snapshots[inventory_path]),
              'input_files_unchanged':True, 'validation_scope':'STRUCTURAL_CHECKS_ONLY_SOURCE_JUDGMENTS_REQUIRE_SEPARATE_REVIEW', **counts}
    if pair_screen is not None:
        result['pair_screen_sha256'] = sha256(snapshots[Path(pair_screen)])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('base_map', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--pair-screen', type=Path)
    args = parser.parse_args()
    try:
        result = check_files(args.inventory, args.base_map, args.output, pair_screen=args.pair_screen)
    except (InventoryError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, 'FAIL: ' + str(exc) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
