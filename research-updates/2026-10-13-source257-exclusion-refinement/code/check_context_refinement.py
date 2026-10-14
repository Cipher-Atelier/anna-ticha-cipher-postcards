#!/usr/bin/env python3
"""Validate a bounded physical-context delta; structure is not visual proof.

Only stdlib is required. No image/source fetching, class inference, or baseline
rewriting occurs. See README-context-refinement.md for the deliberately explicit
evidence schema. Input whole-file hashes are checked before and after output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

BASELINE_SHA = "a2f13278119c6437821a416e1cf56483e7d3d879a48e3adaa363023c314b87a0"
ASSESSMENT_SHA = "9eb422f44900a795e2dc0f4cf2123dbf1571da33e2e748411e69c4520dee3de6"
CONTEXT_SHA = "c1dcfc1709b5c1d2e39b8f8414d2a7f7ed2d4389d1c9bef196ddc339be456d11"
IDS = ('FC015 FC078 FC079 FC089 FC090 FC102 FC104 FC107 FC108 FC109 '
       'FC114 FC122 FC125 FC126 FC127').split()
FEATURES = ('path_topology enclosures openings stem_pattern attached_bars '
            'connected_extra_strokes terminal_pattern owned_mark_profile').split()
BBOX = 'base_native_bbox_xyxy_halfopen'
UNCERTAIN = re.compile(r'(?<![A-Za-z0-9])(UNKNOWN|UNRESOLVED|UNCERTAIN|POSSIBLE|POSSIBLY|MAYBE|PERHAPS|WILDCARD|AMBIGUOUS|INDETERMINATE|UNESTABLISHED)(?![A-Za-z0-9])|\?', re.I)
BLOCKER_KINDS = {'LOCAL_SOURCE_DETAIL_UNRESOLVED_BY_THIS_METHOD', 'SOURCE_SUPPORTED_LOCAL_INFORMATION_LOSS', 'UNIDENTIFIABLE_SEMANTIC_ROLE',
                 'SCHEMA_CONVENTION_NEEDING_ANOTHER_INTERVENTION',
                 'RECOVERABLE_CONTEXT_ISSUE_NOT_RESOLVED_HERE', 'UNASSESSED'}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label}: nonempty text required')


def box(value, label):
    require(isinstance(value, list) and len(value) == 4 and all(type(n) is int for n in value), f'{label}: integer bbox required')
    require(0 <= value[0] < value[2] <= 1785 and 0 <= value[1] < value[3] <= 1175, f'{label}: bbox outside native source')


def exact_keys(obj, keys, label):
    require(isinstance(obj, dict) and set(obj) == set(keys), f'{label}: required exact keys {sorted(keys)}')


def refs(value, label, context, uid):
    require(isinstance(value, list) and bool(value), f'{label}: source-view references required')
    require(all(isinstance(x, str) and x and not x.startswith('/') and '..' not in x.split('/') for x in value), f'{label}: relative reference IDs required')
    if context is not None:
        known = {c['context_id']: c for c in context['contexts']}
        require(all(x in known and uid in known[x]['target_ids'] for x in value), f'{label}: unknown or wrong-target view')


def grounds(item, label, context, uid):
    text(item.get('graphical_grounds'), f'{label}.graphical_grounds')
    refs(item.get('source_view_refs'), label, context, uid)


def validate_delta(delta, baseline, assessment, context=None):
    """Pure structural checks. File pin/alias safety belongs to run()."""
    exact_keys(delta, {'schema', 'pins', 'cases', 'unchanged_scope', 'class_merge_claims', 'claimed_metrics'}, 'delta')
    require(delta['schema'] == 'source257-context-refinement-delta-v1', 'wrong delta schema')
    exact_keys(delta['pins'], {'baseline_sha256', 'assessment_protocol_sha256', 'context_index_sha256', 'reader_A_sha256', 'reader_B_sha256', 'reader_A_coordinate_addendum_sha256', 'reader_B_coordinate_erratum_sha256', 'reader_B_literal_mark_addendum_sha256'}, 'pins')
    require(delta['pins']['baseline_sha256'] == BASELINE_SHA and delta['pins']['assessment_protocol_sha256'] == ASSESSMENT_SHA and delta['pins']['context_index_sha256'] == CONTEXT_SHA, 'delta pins disagree with frozen inputs')
    for key in ('reader_A_sha256', 'reader_B_sha256', 'reader_A_coordinate_addendum_sha256', 'reader_B_coordinate_erratum_sha256', 'reader_B_literal_mark_addendum_sha256'):
        require(isinstance(delta['pins'][key], str) and re.fullmatch('[0-9a-f]{64}', delta['pins'][key]), f'{key}: frozen reader report hash required')
    require(delta['pins']['reader_A_sha256'] != delta['pins']['reader_B_sha256'], 'two distinct reader reports required')
    require(assessment['selected_ids'] == IDS, 'assessment cohort differs from frozen 15')
    records = {r['id']: r for r in baseline['records']}
    require(len(records) == 172 and len(baseline['unresolved_source_ids']) == 135, 'baseline collection counts changed')
    require(sum(r['candidate_eligible'] is True for r in records.values()) == 55, 'baseline eligibility changed')
    require(delta['class_merge_claims'] == [], 'no new class/merge claims permitted')
    untouched = {k: v for k, v in records.items() if k not in IDS}
    expected_scope = {'other_whole_annotation_ids': sorted(untouched),
                      'unresolved_source_ids': baseline['unresolved_source_ids'],
                      'policy': 'BASELINE_UNCHANGED_NO_PATCH_OUTSIDE_COHORT'}
    require(delta['unchanged_scope'] == expected_scope, 'other 157 units or 135 unresolved IDs changed')
    cases = delta['cases']
    require(isinstance(cases, list) and len(cases) == 15 and {c.get('id') for c in cases} == set(IDS), 'exactly all 15 unique fixed cases required')
    metrics = dict(window_barrier_before=15, window_barrier_discharged=0, window_barrier_partial=0,
                   window_barrier_retained=0, cases_with_new_blockers=0, cohort_eligible_before=0,
                   cohort_eligible_after=0, eligible_annotation_profiles_after=55,
                   excluded_annotation_profiles_after=117, unchanged_other_whole=157,
                   unchanged_unresolved_placeholders=135)
    casekeys = {'id', BBOX, 'candidate_eligible_before', 'window_barrier_after', 'old_id_target_identity',
                'old_id_target_identity_evidence', 'observed_target_native_bbox_xyxy_halfopen',
                'competing_alternatives', 'physical_features', 'significant_signature', 'mark_inventory',
                'alias_check', 'full_feature_eligibility_after', 'remaining_blockers', 'new_blockers',
                'source_view_refs', 'reader_disagreements', 'graphic_resolution', 'reader_support',
                'adjudicator_source_inspection', 'causal_attribution', 'cipher_role', 'functional_role', 'letter_value'}
    for case in cases:
        uid = case['id']; label = uid
        exact_keys(case, casekeys, label)
        box(case[BBOX], uid + '.base_bbox')
        require(case[BBOX] == records[uid][BBOX], f'{uid}: base bbox changed')
        require(records[uid]['candidate_eligible'] is False and case['candidate_eligible_before'] is False, f'{uid}: before must remain excluded')
        for key in ('cipher_role', 'functional_role', 'letter_value'):
            require(case[key] == 'UNKNOWN', f'{uid}: {key} must remain UNKNOWN')
        state = case['window_barrier_after']
        require(state in {'DISCHARGED', 'PARTIAL', 'RETAINED'}, f'{uid}: invalid barrier state')
        metrics['window_barrier_' + {'DISCHARGED':'discharged', 'PARTIAL':'partial', 'RETAINED':'retained'}[state]] += 1
        identity = case['old_id_target_identity']
        require(identity in {'SUPPORTED_SAME_TARGET', 'UNRESOLVED'}, f'{uid}: invalid old-ID identity')
        grounds(case['old_id_target_identity_evidence'], uid + '.identity', context, uid)
        target = case['observed_target_native_bbox_xyxy_halfopen']
        if target is not None:
            box(target, uid + '.observed_target')
        require(identity != 'SUPPORTED_SAME_TARGET' or target is not None, f'{uid}: supported target needs sidecar locator')
        alternatives = case['competing_alternatives']
        require(isinstance(alternatives, list) and bool(alternatives), f'{uid}: old competing alternatives required')
        oldlocators = {tuple(m['native_bbox_xyxy_halfopen']) for m in records[uid]['source_adjudication']['local_mark_locators']}
        covered = set()
        sides = set()
        for n, alternative in enumerate(alternatives):
            exact_keys(alternative, {'old_native_locator', 'new_native_locator', 'side', 'physical_component_ref', 'relation', 'connection_regions', 'graphical_grounds', 'source_view_refs'}, f'{uid}.alternative[{n}]')
            box(alternative['old_native_locator'], uid + '.old_locator'); covered.add(tuple(alternative['old_native_locator']))
            box(alternative['new_native_locator'], uid + '.new_locator')
            require(alternative['side'] in {'LEFT', 'RIGHT', 'OVERLAPPING'}, uid + ': invalid side'); sides.add(alternative['side'])
            component = alternative['physical_component_ref']
            exact_keys(component, {'component_id', 'annotation_ids', 'native_bbox_xyxy_halfopen'}, uid + '.component')
            text(component['component_id'], uid + '.component_id'); box(component['native_bbox_xyxy_halfopen'], uid + '.component_bbox')
            require(isinstance(component['annotation_ids'], list) and all(x in records or x in baseline['unresolved_source_ids'] for x in component['annotation_ids']), uid + ': unknown neighboring annotation reference')
            require(alternative['relation'] in {'CONTINUOUS_NEIGHBOR', 'CONTINUOUS_TARGET', 'BOUNDED_SEPARATE_NEIGHBOR', 'UNRESOLVED'}, uid + ': invalid physical relation')
            require(isinstance(alternative['connection_regions'], list), uid + ': connection-region list required')
            for region in alternative['connection_regions']: box(region, uid + '.connection_region')
            if state == 'DISCHARGED':
                require(alternative['relation'] != 'UNRESOLVED' and alternative['connection_regions'], uid + ': discharge needs physical relation and connection/complete-boundary regions')
            grounds(alternative, uid + '.alternative', context, uid)
        require(oldlocators <= covered, uid + ': omitted old competing-fragment locator')
        if uid in {'FC108', 'FC126', 'FC127'}:
            require({'LEFT','RIGHT'} <= sides, uid + ': both old sides must be explicitly considered')
        attribution = case['causal_attribution']
        exact_keys(attribution, {'old_context_native_bbox_xyxy_halfopen', 'required_evidence_native_bbox_xyxy_halfopen', 'required_evidence_within_old_context', 'gain_basis', 'graphical_grounds', 'source_view_refs'}, uid + '.causal_attribution')
        oldcontext = attribution['old_context_native_bbox_xyxy_halfopen']; needed = attribution['required_evidence_native_bbox_xyxy_halfopen']
        box(oldcontext, uid + '.old_context'); box(needed, uid + '.required_evidence')
        contained = oldcontext[0] <= needed[0] and oldcontext[1] <= needed[1] and oldcontext[2] >= needed[2] and oldcontext[3] >= needed[3]
        require(attribution['required_evidence_within_old_context'] is contained, uid + ': causal containment misreported')
        expected_basis = 'INSIDE_OLD_CONTEXT_NEW_COMPONENT_ALLOCATION' if contained else 'EXTENDS_BEYOND_OLD_CONTEXT'
        require(attribution['gain_basis'] == expected_basis, uid + ': causal gain basis disagrees with evidence geometry')
        grounds(attribution, uid + '.causal_attribution', context, uid)
        exact_keys(case['physical_features'], FEATURES, uid + '.physical_features')
        exact_keys(case['significant_signature'], FEATURES, uid + '.significant_signature')
        known_features = True
        for feature in FEATURES:
            entry = case['physical_features'][feature]
            exact_keys(entry, {'status', 'description', 'source_view_refs'}, uid + '.' + feature)
            require(entry['status'] in {'KNOWN', 'UNRESOLVED'}, uid + ': invalid feature state')
            text(entry['description'], uid + '.' + feature)
            refs(entry['source_view_refs'], uid + '.' + feature, context, uid)
            require(case['significant_signature'][feature] == entry['description'], uid + ': signature silently drops feature detail')
            known_features &= entry['status'] == 'KNOWN' and UNCERTAIN.search(entry['description']) is None
        marks = case['mark_inventory']
        require(isinstance(marks, list) and bool(marks), uid + ': every-mark inventory required')
        mark_covered = set(); marks_resolved = True
        for mark in marks:
            exact_keys(mark, {'native_locator', 'old_native_locators', 'appearance', 'physical_allocation', 'physical_component_id', 'functional_role', 'graphical_grounds', 'source_view_refs'}, uid + '.mark')
            box(mark['native_locator'], uid + '.mark_locator'); text(mark['appearance'], uid + '.mark_appearance')
            require(isinstance(mark['old_native_locators'], list), uid + ': old mark locator list required')
            for locator in mark['old_native_locators']: box(locator, uid + '.old_mark_locator'); mark_covered.add(tuple(locator))
            require(mark['physical_allocation'] in {'TARGET_CONTINUOUS', 'NEIGHBOR_COMPONENT', 'UNRESOLVED'}, uid + ': invalid mark allocation')
            require(mark['functional_role'] == 'UNKNOWN', uid + ': no semantic mark ownership inference')
            if mark['physical_allocation'] != 'UNRESOLVED': text(mark['physical_component_id'], uid + '.mark_component')
            marks_resolved &= mark['physical_allocation'] != 'UNRESOLVED'
            grounds(mark, uid + '.mark', context, uid)
        require(oldlocators <= mark_covered, uid + ': every old competing mark must remain inventoried')
        alias = case['alias_check']
        exact_keys(alias, {'status', 'checked_annotation_ids', 'graphical_grounds', 'source_view_refs'}, uid + '.alias')
        require(alias['status'] in {'NO_SAME_INSTANCE_ALIAS_OBSERVED_WITH_REFERENCED_NEIGHBORS', 'UNRESOLVED'}, uid + ': invalid alias status')
        require(isinstance(alias['checked_annotation_ids'], list) and bool(alias['checked_annotation_ids']) and all(x != uid and (x in records or x in baseline['unresolved_source_ids']) for x in alias['checked_annotation_ids']), uid + ': explicit valid neighboring alias references required')
        if context is not None:
            unresolved = set(baseline['unresolved_source_ids'])
            required_alias_refs = {ref['id'] for view in context['contexts']
                                   if view['kind'] == 'focus' and uid in view['target_ids']
                                   for ref in view.get('intersecting_annotations', []) if ref['id'] in unresolved}
            require(required_alias_refs <= set(alias['checked_annotation_ids']), uid + ': omitted focus-intersecting unresolved alias references')
        grounds(alias, uid + '.alias', context, uid)
        for category in ('remaining_blockers', 'new_blockers'):
            require(isinstance(case[category], list), uid + ': blocker list required')
            for blocker in case[category]:
                exact_keys(blocker, {'kind', 'description', 'graphical_grounds', 'source_view_refs'}, uid + '.blocker')
                require(blocker['kind'] in BLOCKER_KINDS, uid + ': blocker cause category required')
                text(blocker['description'], uid + '.blocker'); grounds(blocker, uid + '.blocker', context, uid)
        metrics['cases_with_new_blockers'] += bool(case['new_blockers'])
        refs(case['source_view_refs'], uid + '.views', context, uid)
        if context is not None:
            kinds = {c['kind'] for c in context['contexts'] if c['context_id'] in case['source_view_refs']}
            require({'region', 'focus'} <= kinds, uid + ': complete trajectory and focus views required')
        require(isinstance(case['reader_disagreements'], list) and all(isinstance(x, str) and x.strip() for x in case['reader_disagreements']), uid + ': preserve reader disagreements as list')
        text(case['graphic_resolution'], uid + '.graphic_resolution')
        support = case['reader_support']
        exact_keys(support, {'A', 'B'}, uid + '.reader_support')
        for reader, reading in support.items():
            exact_keys(reading, {'window_discharge_supported', 'eligibility_supported', 'basis_report_sha256', 'support_phase', 'graphical_grounds', 'source_view_refs'}, uid + '.' + reader)
            require(type(reading['window_discharge_supported']) is bool and type(reading['eligibility_supported']) is bool, uid + ': reader support booleans required')
            require(reading['support_phase'] in {'INITIAL_INDEPENDENT_READING', 'POST_FEEDBACK_COORDINATE_AUDIT', 'POST_FEEDBACK_LITERAL_MARK_AUDIT'}, uid + ': invalid reader support phase')
            require(reading['support_phase'] != 'POST_FEEDBACK_LITERAL_MARK_AUDIT' or reader == 'B', uid + ': literal mark support phase is B only')
            if reading['support_phase'] == 'POST_FEEDBACK_LITERAL_MARK_AUDIT':
                basis_key = 'reader_B_literal_mark_addendum_sha256'
            else:
                basis_key = f'reader_{reader}_sha256' if reading['support_phase'] == 'INITIAL_INDEPENDENT_READING' else ('reader_A_coordinate_addendum_sha256' if reader == 'A' else 'reader_B_coordinate_erratum_sha256')
            require(reading['basis_report_sha256'] == delta['pins'][basis_key], uid + ': reader support provenance disagrees with phase/pin')
            grounds(reading, uid + '.' + reader, context, uid)
        review = case['adjudicator_source_inspection']
        exact_keys(review, {'source_native_and_clockwise_verified', 'complete_target_features_inspected', 'graphical_grounds', 'source_view_refs'}, uid + '.scientific_review')
        require(review['source_native_and_clockwise_verified'] is True and review['complete_target_features_inspected'] is True, uid + ': native/rotation and complete-target scientific review required')
        grounds(review, uid + '.scientific_review', context, uid)
        if state == 'DISCHARGED':
            require(all(x['window_discharge_supported'] for x in support.values()), uid + ': accepted discharge requires both source readers support')
        eligible = case['full_feature_eligibility_after']
        require(type(eligible) is bool, uid + ': eligibility boolean required')
        gates = (state == 'DISCHARGED' and identity == 'SUPPORTED_SAME_TARGET' and known_features and marks_resolved
                 and alias['status'] == 'NO_SAME_INSTANCE_ALIAS_OBSERVED_WITH_REFERENCED_NEIGHBORS'
                 and not case['remaining_blockers'] and not case['new_blockers']
                 and all(x['eligibility_supported'] for x in support.values()))
        require(not eligible or gates, uid + ': eligibility fails a complete-feature/identity/mark/alias/reader/blocker gate')
        require(eligible or bool(case['remaining_blockers'] or case['new_blockers']), uid + ': excluded case needs explicit remaining blocker')
        metrics['cohort_eligible_after'] += eligible
    metrics['eligible_annotation_profiles_after'] += metrics['cohort_eligible_after']
    metrics['excluded_annotation_profiles_after'] -= metrics['cohort_eligible_after']
    require(delta['claimed_metrics'] == metrics and all(type(x) is int for x in delta['claimed_metrics'].values()), 'claimed counts differ from mechanically derived measurements')
    return metrics


def snapshot(path):
    require(not path.is_symlink(), 'input symlinks are forbidden')
    s = path.stat(); require(stat.S_ISREG(s.st_mode), 'input must be regular file')
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns), path.read_bytes()


def run(delta_path, baseline_path, assessment_path, output_path, context_path=None):
    paths = [Path(p) for p in (delta_path, baseline_path, assessment_path)]
    if context_path is not None: paths.append(Path(context_path))
    output = Path(output_path)
    # All aliases, including existing hardlinks, are rejected before any write.
    require(not os.path.lexists(output), 'output already exists or aliases an input; diagnostic is immutable')
    require(output.parent.is_dir(), 'output parent must already exist')
    snapshots = [snapshot(p) for p in paths]
    identities = [s[0][:2] for s in snapshots]
    require(len(set(identities)) == len(identities), 'immutable input aliases (including hardlinks) are forbidden')
    require(all(output.resolve() != p.resolve() for p in paths), 'output aliases immutable input')
    blobs = [s[1] for s in snapshots]
    require(sha(blobs[1]) == BASELINE_SHA, 'baseline SHA256 mismatch')
    require(sha(blobs[2]) == ASSESSMENT_SHA, 'assessment protocol SHA256 mismatch')
    if context_path is not None: require(sha(blobs[3]) == CONTEXT_SHA, 'context index SHA256 mismatch')
    objects = [json.loads(b) for b in blobs]
    metrics = validate_delta(objects[0], objects[1], objects[2], objects[3] if context_path is not None else None)
    for path, old in zip(paths, snapshots): require(snapshot(path) == old, 'immutable input changed before output')
    diagnostic = {'schema':'source257-context-refinement-check-v1', 'structural_validation':'PASS',
                  'visual_proof':'NOT_ESTABLISHED_BY_VALIDATOR', 'derived_metrics':metrics,
                  'input_whole_file_sha256':{name:sha(blob) for name,blob in zip(['delta','baseline','assessment_protocol','context_index'],blobs)},
                  'immutable_inputs_unchanged_before_write':True, 'immutable_inputs_unchanged_after_write':True,
                  'count_unit':'annotation feature profiles; not glyph/alphabet totals'}
    with output.open('x', encoding='utf-8') as handle:
        json.dump(diagnostic, handle, indent=2, sort_keys=True); handle.write('\n')
    for path, old in zip(paths, snapshots): require(snapshot(path) == old, 'immutable input changed after output')
    return diagnostic


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('delta'); p.add_argument('baseline'); p.add_argument('assessment_protocol'); p.add_argument('output')
    p.add_argument('--context-index')
    args = p.parse_args()
    try:
        result = run(args.delta, args.baseline, args.assessment_protocol, args.output, args.context_index)
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr); return 1
    print(json.dumps({'status':'PASS', 'metrics':result['derived_metrics'], 'visual_proof':'NOT_ESTABLISHED_BY_VALIDATOR'}, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
