#!/usr/bin/env python3
"""Experimental card330 saved-graphical consistency helpers, entirely offline.

Unresolved encoded slots are not proven one-body glyphs. These checks do not
classify ink, certify reader blinding, establish a date, or prove historical text.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys

from ledger_replay import (VerificationError, check_boxes, fingerprint, integer,
                           load_key, no_accepted_mapping, read_json, require)

PICTURE = {
    'url': 'https://api.hcportal.eu/media/5007/pc_hcp_330_pic.JPG',
    'sha256': '206f29850350f429346d04bacc37c01bc377e50b1224a59d42bb6e785b781a05',
    'bytes': 1431536, 'width': 1785, 'height': 1175,
}
ADDRESS = {
    'url': 'https://api.hcportal.eu/media/5008/pc_hcp_330_adr.JPG',
    'sha256': '45d8a90465498208210bf1943c442dfa13d2bea303c705a7a8bd0f40b663d4d0',
    'bytes': 1060308, 'width': 1785, 'height': 1175,
}
PHASE_A_SHA = '274527cdad28a319d0b311d43525eb7b60992d682a40b03f844cd377142728e3'
IDENTIFIER_ERRATA = {'GA006': 'A006', 'GA007': 'A007', 'GA008': 'A008'}


def required_window(record, field, context):
    require(isinstance(record, dict) and field in record, f'{context}: missing required window {field}')
    box = record[field]
    require(isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box),
            f'{context}: malformed window {field}')
    x0, y0, x1, y1 = box
    require(0 <= x0 < x1 <= PICTURE['width'] and 0 <= y0 < y1 <= PICTURE['height'],
            f'{context}: out-of-bounds window {field}')
    return box


def all_saved_windows(value, context):
    """Check every declared coordinate field, including optional nonbody windows."""
    if isinstance(value, dict):
        for field, child in value.items():
            if field.endswith('_xyxy') or field == 'box':
                required_window(value, field, context)
            else:
                all_saved_windows(child, f'{context}.{field}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            all_saved_windows(child, f'{context}[{index}]')


def normalize_identifiers(aliases, declarations, key):
    """Only declared spelling errata; never turn an uncertainty into a key class."""
    require(isinstance(aliases, dict), 'card330: malformed identifier errata')
    require(len(set(aliases.values())) == len(aliases), 'card330: duplicate alias targets')
    for old, new in aliases.items():
        require(old in IDENTIFIER_ERRATA and new == IDENTIFIER_ERRATA[old],
                'card330: unsupported identifier erratum')
        require(old not in key and old not in declarations and new in declarations and new not in key,
                'card330: identifier erratum changes class role')
    return aliases


def unresolved_declarations(declarations, key):
    require(isinstance(declarations, dict), 'card330: malformed uncertainty declarations')
    for ident, record in declarations.items():
        context = f'card330 uncertainty {ident}'
        require(isinstance(ident, str) and re.fullmatch(r'[AU][0-9]{3}', ident) and
                ident not in key and isinstance(record, dict), f'{context}: invalid ID/declaration')
        no_accepted_mapping(record, context)
        require('literal' not in record and 'rendered_literal' not in record,
                f'{context}: unresolved family has accepted literal')
        require('body_count' not in record or record['body_count'] is None or
                record['body_count'] == 'not established', f'{context}: unresolved family has accepted body count')
        choices = record.get('candidate_classes')
        require(isinstance(choices, list) and choices and all(isinstance(c, str) and c in key for c in choices)
                and len(set(choices)) == len(choices), f'{context}: invalid candidate classes')
        if 'body_count_interval' in record:
            interval = record['body_count_interval']
            require(isinstance(interval, list) and len(interval) == 2 and
                    all(type(v) is int for v in interval) and 1 <= interval[0] <= interval[1],
                    f'{context}: malformed provisional body interval')
        require(isinstance(record.get('reason'), str) and record['reason'], f'{context}: missing uncertainty reason')
    return declarations


def validate_graphical_snapshot(snapshot, key, aliases=None):
    """Validate A's saved slots and preserve masks; apply only explicit ID errata.

    Returned counts distinguish known class assignments, unresolved slot
    occurrences and distinct families. No sum is labelled a whole body count.
    """
    require(isinstance(snapshot, dict) and snapshot.get('schema') == 'card330.class-first-ledger.v1',
            'card330 A: unsupported snapshot schema')
    source = snapshot.get('source', {})
    require(isinstance(source, dict) and all(source.get(k) == v for k, v in PICTURE.items()),
            'card330 A: source fingerprint/dimensions mismatch')
    size = [PICTURE['width'], PICTURE['height']]
    check_boxes(snapshot, size, 'card330 A')
    declarations = unresolved_declarations(snapshot.get('unknown_alternatives'), key)
    aliases = normalize_identifiers(aliases or {}, declarations, key)
    coverage = snapshot.get('coverage')
    require(isinstance(coverage, list) and coverage and
            [r.get('line') for r in coverage] == list(range(1, len(coverage) + 1)),
            'card330 A: coverage line IDs/order mismatch')
    expected = []
    for record in coverage:
        required_window(record, 'bbox_xyxy', 'card330 A coverage')
        line = integer(record['line'], 'card330 A coverage line', 1)
        count = integer(record.get('groups'), 'card330 A coverage groups', 1)
        expected.extend((line, word) for word in range(1, count + 1))
    groups = snapshot.get('groups')
    require(isinstance(groups, list) and len(groups) == len(expected), 'card330 A: required group count mismatch')
    seen_groups, seen_slots, used_families, observed = set(), set(), set(), set()
    totals = {'groups': len(groups), 'encoded_slots': 0, 'invariant_mapped_bodies': 0,
              'emitted_invariant_letters': 0, 'unresolved_slot_occurrences': 0, 'capped_ch_bodies': 0}
    projection = []
    for group, (line, word) in zip(groups, expected):
        require(isinstance(group, dict), 'card330 A: malformed group')
        required_window(group, 'bbox_xyxy', 'card330 A group')
        ident = group.get('group_id')
        require(ident not in seen_groups, f'card330 A: duplicate group ID {ident}')
        seen_groups.add(ident)
        require(ident == f'L{line:02}W{word:02}' and type(group.get('line')) is int and
                group['line'] == line and type(group.get('spatial_group')) is int and
                group['spatial_group'] == word, 'card330 A: group IDs/order mismatch')
        sequence, slots = group.get('class_sequence'), group.get('bodies')
        require(isinstance(sequence, list) and sequence and all(isinstance(c, str) for c in sequence)
                and isinstance(slots, list) and len(slots) == len(sequence), f'card330 A {ident}: slot sequence mismatch')
        normalized, values = [], []
        for index, (token, slot) in enumerate(zip(sequence, slots), 1):
            require(isinstance(slot, dict), f'card330 A {ident}: malformed encoded slot')
            required_window(slot, 'bbox_xyxy', f'card330 A {ident} slot')
            sid = slot.get('body_id')
            require(sid not in seen_slots, f'card330 A: duplicate slot ID {sid}')
            seen_slots.add(sid)
            require(sid == f'{ident}B{index:02}' and slot.get('class_id') == token,
                    f'card330 A {ident}: slot ID/class sequence mismatch')
            token = aliases.get(token, token)
            normalized.append(token)
            totals['encoded_slots'] += 1
            if token in key:
                values.append(key[token])
                observed.add(token)
                totals['invariant_mapped_bodies'] += 1
                totals['emitted_invariant_letters'] += len(key[token])
                totals['capped_ch_bodies'] += token == 'G10_CAP'
            else:
                require(token in declarations, f'card330 A {ident}: unknown class/undeclared family {token}')
                used_families.add(token)
                totals['unresolved_slot_occurrences'] += 1
                values.append(f'[{token}]')
        projection.append({'group_id': ident, 'line': line, 'spatial_group': word,
                           'class_sequence': normalized, 'literal': ''.join(values)})
    require(used_families == set(declarations), 'card330 A: unused uncertainty family declaration')
    totals['unresolved_families'] = len(used_families)
    totals['observed_invariant_classes'] = len(observed)
    totals['whole_body_count'] = None
    punctuation = snapshot.get('punctuation')
    require(isinstance(punctuation, list), 'card330 A: missing punctuation inventory')
    seen_marks = set()
    for index, mark in enumerate(punctuation, 1):
        require(isinstance(mark, dict) and mark.get('id') == f'P{index:02}' and mark['id'] not in seen_marks,
                'card330 A: punctuation IDs/order mismatch')
        required_window(mark, 'bbox_xyxy', 'card330 A punctuation')
        seen_marks.add(mark['id'])
        line = integer(mark.get('line'), 'card330 A punctuation line', 1)
        word = integer(mark.get('after_spatial_group'), 'card330 A punctuation group', 1)
        require((line, word) in expected and isinstance(mark.get('features'), str) and mark['features'],
                'card330 A: invalid punctuation position/features')
    return {'counts': totals, 'groups': projection}


def source_image_hash(path, source=PICTURE):
    """Explicit opt-in identity check; never downloads or emits image data."""
    path = Path(path)
    fingerprint(path, source['sha256'], 'card330 explicit source image')
    require(path.stat().st_size == source['bytes'], 'card330 explicit source image: byte count mismatch')
    # Exact known JPEG bytes pin its recorded dimensions; there is no pixel/classification check.
    return {'status': 'passed', 'sha256': source['sha256'], 'bytes': source['bytes'],
            'recorded_dimensions': [source['width'], source['height']],
            'scope': 'Exact saved-source identity only; no visual classification or date validation.'}


PACKAGE = 'research-updates/evidence/card330-2026-10-11'
DISPLAY_GROUPS = (11, 14, 17, 13, 10)
EXPECTED_IDS = tuple(f'L{line:02}W{word:02}' for line, count in enumerate(DISPLAY_GROUPS, 1)
                     for word in range(1, count + 1))
IMMUTABLE_FILES = {
    'phase-a-ledger.json': PHASE_A_SHA,
    'reader-b-initial.json': '628a4aceb8b5a423a4e5a097d0392fb41f262d994b18409eec5ca34d31cad404',
    'encoding-errata.json': 'dfc896ae2b2d58c8e16e57d7349252b3a3c198dc0cf34c39f60551a9e4713f3f',
    'reader-b-source-followup-before-a.json': 'd44859989f7f356320ae0291154422b78c3467de06c836209bae94a7e137e603',
    'reader-b-detail-followup-before-a.json': 'bb0498ebcbc73bc6a9f59552a9e75b7f948b2a75a64cf5861c6b41735e431eb8',
    'reader-b-key-projection-before-a.json': '2e41361f7465862dd295d52fa0431234fe5466bb228850692748f4a9d1eebb9c',
    'postmark-review.json': 'e21ca22696ee56b06571220788f359580c6ac100acf5c35dbc34e69db804640e',
    'postal-date-observations.json': '0a33a6a4a2c837fffd7bdd4bc02487b9098af31c5d7fda6da0431a0c514fb8d7',
    'sources.json': '4a115965e6ebdfeb08359d7f7241774c32ac1fa6c9275a79e903ab8ee42f09e9',
}
REQUIRED_FILES = set(IMMUTABLE_FILES) | {'reconciliation-v3.json', 'word-ledger.csv', 'literal.txt'}
UNRESOLVED_IDS = {'A001', 'A002', 'A003', 'A007', 'A008', 'U001', 'R_L01W03B05',
                  'R_L02W04B05', 'R_L02W07B05', 'R_L03W17B01', 'R_L03W11_COUPLED_SPAN'}
CSV_FIELDS = ['group_id', 'line', 'spatial_group', 'class_sequence', 'literal',
              'source_group_window_xyxy', 'encoded_slots', 'provisionally_mapped_slots',
              'emitted_known_letters', 'unresolved_slot_occurrences', 'capped_ch_slots']
PUNCTUATION_RENDER = {'comma': ',', 'point': '.', 'question-like hooked mark and point': '[?]',
                      'exclamation-like stroke and point': '[!]', 'terminal horizontal continuation': '[-]'}
FINAL_COUNTS = {'groups': 65, 'lines': 5, 'encoded_slots': 264, 'provisionally_mapped_slots': 251,
                'emitted_known_letters': 254, 'unresolved_slot_occurrences': 13,
                'unresolved_families': 11, 'observed_known_classes': 23,
                'capped_ch_slots': 3, 'physical_body_count': None}


def check_unresolved_final(record, ident, key):
    context = f'card330 final uncertainty {ident}'
    require(isinstance(record, dict), f'{context}: malformed declaration')
    no_accepted_mapping(record, context)
    require(not any(k in record for k in ('literal', 'rendered_literal', 'proposed_literal', 'proposed_class')),
            f'{context}: unresolved declaration has accepted literal/class')
    for field in ('body_count', 'physical_body_count', 'whole_body_count'):
        require(field not in record or record[field] is None or record[field] == 'not established',
                f'{context}: unresolved declaration has accepted body count')
    require(isinstance(record.get('reason'), str) and record['reason'], f'{context}: missing reason')
    has_classes, has_sequences = 'candidate_classes' in record, 'candidate_sequences' in record
    require(has_classes != has_sequences, f'{context}: candidate forms must be exclusive')
    if has_classes:
        choices = record['candidate_classes']
        require(isinstance(choices, list) and choices and all(isinstance(c, str) and c in key for c in choices)
                and len(set(choices)) == len(choices), f'{context}: invalid candidate classes')
    else:
        sequences = record['candidate_sequences']
        require(isinstance(sequences, list) and len(sequences) >= 2 and all(isinstance(seq, list) and seq and
                all(isinstance(c, str) and c in key for c in seq) for seq in sequences) and
                len({tuple(seq) for seq in sequences}) == len(sequences), f'{context}: invalid candidate sequences')
        required_window(record, 'source_window_xyxy', context)


def validate_reconciliation(journal, snapshot, key, b_projection=None):
    require(journal.get('schema') == 'card330.B-full-reconciliation-review.v3', 'card330: unsupported final journal schema')
    require(journal.get('source_sha256') == PICTURE['sha256'], 'card330: journal source fingerprint mismatch')
    require(journal.get('inputs') == {'A_sha256': PHASE_A_SHA,
            'B_initial_sha256': IMMUTABLE_FILES['reader-b-initial.json'],
            'B_key_projection_sha256': IMMUTABLE_FILES['reader-b-key-projection-before-a.json']},
            'card330: journal input fingerprints mismatch')
    require(journal.get('alias_normalization') == IDENTIFIER_ERRATA, 'card330: final identifier errata mismatch')
    # The immutable A snapshot and static display partition forbid evidence disappearing with edited totals.
    require([g.get('group_id') for g in snapshot.get('groups', [])] == list(EXPECTED_IDS),
            'card330: immutable A display partition mismatch')
    require([r.get('groups') for r in snapshot.get('coverage', [])] == list(DISPLAY_GROUPS),
            'card330: immutable A coverage mismatch')
    require(sum(len(g['bodies']) for g in snapshot['groups']) == 265, 'card330: immutable A historical slot count mismatch')
    required_window(snapshot.get('date'), 'bbox_xyxy', 'card330 A date')
    all_saved_windows(journal, 'card330 final')
    declarations = journal.get('unresolved_declarations')
    require(isinstance(declarations, dict) and set(declarations) == UNRESOLVED_IDS,
            'card330: final uncertainty IDs mismatch')
    for ident, record in declarations.items():
        check_unresolved_final(record, ident, key)
    groups = journal.get('groups')
    require(isinstance(groups, list) and len(groups) == 65, 'card330: required final group count mismatch')
    require(all(isinstance(group,dict) and isinstance(group.get('group_id'),str) for group in groups),
            'card330: malformed final group')
    ids = [group['group_id'] for group in groups]
    require(len(set(ids)) == len(ids), 'card330: duplicate final group ID')
    require(ids == list(EXPECTED_IDS), 'card330: final group IDs/order mismatch')
    b_ids = {}
    if b_projection is not None:
        require(b_projection.get('source_snapshot_sha256') == IMMUTABLE_FILES['reader-b-initial.json'],
                'card330: historical B projection input mismatch')
        for line in b_projection.get('lines', []):
            b_ids.update({g['group_id']:g['classes'] for g in line['groups']})
        for line in range(1,6):
            frozen_sequence = [t for record in b_projection['lines'] if record['line'] == line
                               for group in record['groups'] for t in group['classes']]
            reviewed_sequence = [t for group in groups if group.get('line') == line
                                 for t in group.get('B_sequence', [])]
            require(reviewed_sequence == frozen_sequence, f'card330 line{line}: historical B projection mismatch')
    seen, used, observed = set(), set(), set()
    rows = []
    totals = dict.fromkeys(FINAL_COUNTS, 0)
    totals.update(groups=65, lines=5, physical_body_count=None)
    for group, original, expected_id in zip(groups, snapshot['groups'], EXPECTED_IDS):
        ident = group.get('group_id')
        require(ident not in seen, f'card330: duplicate final group ID {ident}')
        seen.add(ident)
        require(ident == expected_id and type(group.get('line')) is int and group['line'] == original['line']
                and type(group.get('spatial_group')) is int and group['spatial_group'] == original['spatial_group'],
                'card330: final group IDs/order mismatch')
        box = required_window(group, 'source_group_window_xyxy', f'card330 {ident}')
        require('physical_body_count' in group and group['physical_body_count'] is None,
                f'card330 {ident}: physical body count must remain unestablished')
        a_sequence = [IDENTIFIER_ERRATA.get(t, t) for t in original['class_sequence']]
        require(isinstance(group.get('A_sequence'), list) and
                [IDENTIFIER_ERRATA.get(t, t) for t in group['A_sequence']] == a_sequence,
                f'card330 {ident}: historical A sequence mismatch')
        require(isinstance(group.get('B_sequence'), list) and all(isinstance(t,str) and
                (t in key or t in {'UNKNOWN_E_LIKE','UNKNOWN_LARGE_JOINED_FORM'}) for t in group['B_sequence']),
                f'card330 {ident}: unsupported historical B class')
        if b_projection is not None:
            refs = group.get('B_correspondence')
            require(isinstance(refs,list) and refs and len(set(refs)) == len(refs) and
                    all(ref in b_ids and ref.startswith(f"L{group['line']:02}.") for ref in refs),
                    f'card330 {ident}: invalid historical B correspondence')
            indices = [int(ref.split('.G')[1]) for ref in refs]
            require(indices == list(range(indices[0],indices[0]+len(indices))),
                    f'card330 {ident}: historical B correspondence range/order mismatch')
            referenced = [t for ref in refs for t in b_ids[ref]]
            require(any(referenced[start:start+len(group['B_sequence'])] == group['B_sequence']
                        for start in range(len(referenced))),
                    f'card330 {ident}: historical B correspondence sequence mismatch')
        reviews, sequence = group.get('body_reviews'), group.get('proposed_class_sequence')
        require(isinstance(sequence, list) and sequence and all(isinstance(t, str) for t in sequence),
                f'card330 {ident}: malformed final class sequence')
        require(isinstance(reviews, list) and len(reviews) == len(original['bodies']),
                f'card330 {ident}: missing historical slot review')
        require(isinstance(group.get('B_sequence'), list) and len(group['B_sequence']) == len(reviews),
                f'card330 {ident}: historical B sequence/review mismatch')
        for index, (review, old_slot) in enumerate(zip(reviews, original['bodies']), 1):
            require(isinstance(review, dict) and type(review.get('entry_index')) is int and review['entry_index'] == index,
                    f'card330 {ident}: historical slot indices/order mismatch')
            required_window(review, 'source_window_xyxy', f'card330 {ident} slot{index}')
            require(IDENTIFIER_ERRATA.get(review.get('A_class'), review.get('A_class')) == a_sequence[index - 1]
                    and review.get('B_class') == group['B_sequence'][index - 1],
                    f'card330 {ident}: historical A/B slot sequence mismatch')
            require(isinstance(review.get('review_reason'), str) and review['review_reason'],
                    f'card330 {ident}: missing slot review reason')
        if ident == 'L03W11':
            coupled = 'R_L03W11_COUPLED_SPAN'
            expected_sequences = [a_sequence[1:3], group['B_sequence'][1:3]]
            declaration, span = declarations[coupled], group.get('span_review')
            require(isinstance(span, dict), 'card330 coupled span: missing span review')
            required_window(span, 'source_window_xyxy', 'card330 coupled span')
            no_accepted_mapping(span, 'card330 coupled span')
            require(not any(k in span for k in ('literal','rendered_literal','body_count')),
                    'card330 coupled span: accepted literal/body count')
            require(declaration.get('candidate_sequences') == expected_sequences == span.get('candidate_sequences')
                    and expected_sequences == [['G19','H440_N01_UNBARRED_LEFT_BOWL'],['G11','G19']],
                    'card330 coupled span: candidate correlation mismatch')
            require(span.get('physical_body_count', 'missing') is None and 'candidate_classes' not in span,
                    'card330 coupled span: accepted count or independent alternatives')
            require(sequence == [a_sequence[0], coupled, a_sequence[-1]], 'card330 coupled span: final slot projection mismatch')
            require([r.get('final_encoded_slot_index') for r in reviews] == [1,2,2,3],
                    'card330 coupled span: historical-to-final slot mapping mismatch')
            require(reviews[0].get('proposed_class') == sequence[0] and reviews[3].get('proposed_class') == sequence[2],
                    'card330 coupled span: retained final classes mismatch')
            for review in reviews[1:3]:
                require('proposed_class' not in review and review.get('final_span_class_id') == coupled and
                        review.get('historical_component_class_id') in ('R_L03W11B02','R_L03W11B03') and
                        isinstance(review.get('observation_role'), str) and 'Historical' in review['observation_role'] and
                        isinstance(review.get('correlation_policy'), str) and 'candidate_sequences' in review['correlation_policy'],
                        'card330 coupled span: component promoted to independent final class')
        else:
            require(all(type(r.get('final_encoded_slot_index', index)) is int and
                        r.get('final_encoded_slot_index', index) == index for index,r in enumerate(reviews,1)),
                    f'card330 {ident}: final slot index mapping mismatch')
            require(len(sequence) == len(reviews) and [r.get('proposed_class') for r in reviews] == sequence,
                    f'card330 {ident}: review/final slot mapping mismatch')
        mapped = [token for token in sequence if token in key]
        masks = [token for token in sequence if token not in key]
        require(all(token in declarations for token in masks), f'card330 {ident}: undeclared final mask/class')
        used.update(masks)
        observed.update(mapped)
        # The journal's square-placeholder proposal is checked, never used as decoded output.
        require(group.get('proposed_literal') == ''.join(key[t] if t in key else '\u25a1' for t in sequence),
                f'card330 {ident}: journal literal/key mapping mismatch')
        row = {'group_id': ident, 'line': group['line'], 'spatial_group': group['spatial_group'],
               'class_sequence': ' '.join(sequence), 'literal': ''.join(key[t] if t in key else f'[{t}]' for t in sequence),
               'source_group_window_xyxy': json.dumps(box), 'encoded_slots': len(sequence),
               'provisionally_mapped_slots': len(mapped), 'emitted_known_letters': sum(len(key[t]) for t in mapped),
               'unresolved_slot_occurrences': len(masks), 'capped_ch_slots': mapped.count('G10_CAP')}
        for field, expected in (('entry_count',len(sequence)),('encoded_slot_count',len(sequence)),
                                ('mapped_entry_count',len(mapped)),('unknown_entry_count',len(masks))):
            require(integer(group.get(field), f'card330 {ident} {field}') == expected,
                    f'card330 {ident}: row {field} counter mismatch')
        for field in ('encoded_slots','provisionally_mapped_slots','emitted_known_letters','unresolved_slot_occurrences','capped_ch_slots'):
            totals[field] += row[field]
        rows.append(row)
    require(used == set(declarations), 'card330: unused final uncertainty declarations')
    totals['unresolved_families'], totals['observed_known_classes'] = len(used), len(observed)
    require(totals == FINAL_COUNTS, 'card330: derived final counts mismatch')
    coverage = journal.get('coverage', {})
    expected_coverage = {'reviewed_groups':65,'reviewed_lines':5,'display_groups_per_line':list(DISPLAY_GROUPS),
                         'A_and_B_historical_provisional_entries':265,'proposed_encoded_slots':264,
                         'provisionally_mapped_slots':251,'unresolved_slots':13,'physical_body_count':None}
    require(all(k in coverage and coverage[k] == v and type(coverage[k]) is type(v) for k,v in expected_coverage.items()),
            'card330: journal coverage counters mismatch')
    punctuation = journal.get('punctuation')
    require(isinstance(punctuation, list) and len(punctuation) == 13, 'card330: required punctuation count mismatch')
    marks = {}
    for index, mark in enumerate(punctuation, 1):
        require(mark.get('id') == f'P{index:02}', 'card330: punctuation IDs/order mismatch')
        required_window(mark, 'bbox_xyxy', 'card330 final punctuation')
        line = integer(mark.get('line'), 'card330 punctuation line', 1)
        word = integer(mark.get('after_spatial_group'), 'card330 punctuation group', 1)
        position = (line,word)
        require(1 <= line <= 5 and word <= DISPLAY_GROUPS[line-1] and position not in marks
                and mark.get('features') in PUNCTUATION_RENDER, 'card330: invalid/duplicate punctuation position or feature')
        marks[position] = PUNCTUATION_RENDER[mark['features']]
    literal = '\n'.join(' '.join(row['literal'] + marks.get((line,row['spatial_group']), '')
                                    for row in rows if row['line'] == line) for line in range(1,6)) + '\n'
    date = journal.get('date', {})
    require(date.get('picture_candidates') == ['14.IV.1903.','14.II.1903.'] and date.get('certainty') == 'uncertain' and date.get('preferred_month') == 'IV' and
            date.get('postal_result') == 'No accepted complete postal date/month; cannot arbitrate picture month.'
            and not any(k.startswith('accepted') and v is not None for k,v in date.items()),
            'card330: date alternatives/uncertainty changed')
    experiment = journal.get('finite_followup_experiment', {})
    required_window(experiment, 'source_bbox_xyxy', 'card330 finite experiment')
    require('Negative/inconclusive' in experiment.get('result', '') and declarations['A003'].get('new_family_possible') is True,
            'card330: finite experiment cannot accept A003 mapping')
    return rows, literal, totals


def verify_card330(repo=None, source_image=None):
    repo = Path(repo) if repo is not None else Path(__file__).resolve().parent.parent
    package = repo / PACKAGE
    require(package.is_dir(), 'Missing required experimental package: card330')
    manifest = read_json(package / 'manifest.json')
    require(manifest.get('schema') == 'card330.experimental-package.v1', 'card330: unsupported manifest schema')
    files = manifest.get('files_sha256')
    require(isinstance(files, dict) and set(files) == REQUIRED_FILES, 'card330: required fingerprint inventory mismatch')
    for name, digest in files.items():
        fingerprint(package / name, digest, f'card330 {name}')
    for name, digest in IMMUTABLE_FILES.items():
        require(files[name] == digest, f'card330 {name}: immutable snapshot fingerprint mismatch')
    key = load_key(repo)
    from ledger_replay import KEY_PATH, KEY_SHA, ATLAS_PATH, ATLAS_SHA
    require(manifest.get('key_path') == KEY_PATH and manifest.get('key_sha256') == KEY_SHA and
            manifest.get('atlas_path') == ATLAS_PATH and manifest.get('atlas_sha256') == ATLAS_SHA,
            'card330: key/atlas fingerprint/path mismatch')
    sources = read_json(package / 'sources.json')
    require(isinstance(sources, list) and [s.get('side') for s in sources] == ['picture','address'],
            'card330: source sides/order mismatch')
    for record, expected in zip(sources, (PICTURE,ADDRESS)):
        require(record.get('url') == expected['url'] and record.get('sha256') == expected['sha256'] and
                record.get('size_bytes') == expected['bytes'] and record.get('size_pixels') == [1785,1175],
                'card330: source metadata mismatch')
    snapshot = read_json(package / 'phase-a-ledger.json')
    errata = read_json(package / 'encoding-errata.json')
    require(errata.get('phase_A_sha256') == PHASE_A_SHA and
            {r.get('before'):r.get('after') for r in errata.get('corrections', [])} == IDENTIFIER_ERRATA,
            'card330: frozen identifier errata mismatch')
    validate_graphical_snapshot(snapshot, key, IDENTIFIER_ERRATA)
    b = read_json(package / 'reader-b-initial.json')
    require(b.get('source', {}).get('sha256') == PICTURE['sha256'] and
            [r.get('line') for r in b.get('lines', [])] == [1,2,3,4,5], 'card330 B: source/line metadata mismatch')
    require([len(line.get('groups', [])) for line in b['lines']] == [11,13,17,13,11],
            'card330 B: historical display partition mismatch')
    for line in b['lines']:
        for index, group in enumerate(line['groups'],1):
            require(group.get('group_id') == f"L{line['line']:02}.G{index:02}", 'card330 B: group IDs/order mismatch')
            required_window(group, 'bbox_xyxy', 'card330 B group')
    required_window(b.get('date'), 'bbox_xyxy', 'card330 B date')
    followup = read_json(package / 'reader-b-source-followup-before-a.json')
    require(followup.get('initial_snapshot_sha256') == IMMUTABLE_FILES['reader-b-initial.json'], 'card330 B: followup source snapshot mismatch')
    require(isinstance(followup.get('corrected_x_ranges_by_line'), dict) and
            set(followup['corrected_x_ranges_by_line']) == {'1','2','3','4','5'}, 'card330 B: missing followup line windows')
    require([len(followup['corrected_x_ranges_by_line'][str(line)]) for line in range(1,6)] == [11,13,17,13,11],
            'card330 B: missing followup group windows')
    for ranges in followup['corrected_x_ranges_by_line'].values():
        for interval in ranges:
            require(isinstance(interval,list) and len(interval)==2 and all(type(v) is int for v in interval) and
                    0 <= interval[0] < interval[1] <= 1785, 'card330 B: invalid followup x window')
    detail = read_json(package / 'reader-b-detail-followup-before-a.json')
    require(isinstance(detail.get('observations'), list) and len(detail['observations']) == 5,
            'card330 B: missing detailed followup observations')
    for observation in detail['observations']:
        required_window(observation,'box','card330 B detail followup')
    postal = read_json(package / 'postal-date-observations.json')
    require(postal.get('source_sha256') == ADDRESS['sha256'], 'card330 postal: source fingerprint mismatch')
    require([c.get('id') for c in postal.get('contexts', [])] == ['left_round_postmark','stamp_postmark'],
            'card330 postal: missing context observations')
    for context in postal['contexts']:
        required_window(context,'original_bbox_xyxy','card330 postal context')
        require(context.get('accepted_postal_date','missing') is None, 'card330 postal: accepted date must remain null')
    postmark = read_json(package / 'postmark-review.json')
    require(postmark.get('source_sha256') == ADDRESS['sha256'], 'card330 postmark: source fingerprint mismatch')
    for side in ('left','right'):
        required_window(postmark.get(side),'bbox_xyxy',f'card330 postmark {side}')
    rows,literal,counts = validate_reconciliation(read_json(package / 'reconciliation-v3.json'),snapshot,key,
                                                read_json(package / 'reader-b-key-projection-before-a.json'))
    require(manifest.get('counts') == counts, 'card330: manifest aggregate counters mismatch')
    require(manifest.get('accepted_date','missing') is None and manifest.get('accepted_postal_date','missing') is None
            and manifest.get('picture_date_candidates') == ['14.IV.1903.','14.II.1903.'],
            'card330: manifest date must remain unresolved')
    with (package / 'word-ledger.csv').open(encoding='utf-8',newline='') as stream:
        reader = csv.DictReader(stream,strict=True)
        require(reader.fieldnames == CSV_FIELDS, 'card330: derived CSV schema mismatch')
        saved = list(reader)
    require(all(None not in row and None not in row.values() for row in saved), 'card330: malformed CSV row width/missing cell')
    require(len(saved) == 65, 'card330: required CSV record count mismatch')
    for actual,expected in zip(saved,rows):
        for field in CSV_FIELDS:
            require(actual.get(field) == str(expected[field]), f"card330 {expected['group_id']}: CSV {field} mismatch")
    require((package / 'literal.txt').read_bytes() == literal.encode('utf-8'), 'card330: assembled saved literal/punctuation mismatch')
    article = repo / 'anna-ticha/card-330.md'
    require(article.is_file(), 'Missing required article: card-330.md')
    blocks = re.findall(r'^```text\n(.*?)^```\s*$',article.read_text(encoding='utf-8'),re.M|re.S)
    require(blocks and blocks[0] == literal,'card330: diplomatic literal/article mismatch')
    result = {'status':'passed','scope':'experimental saved-graphical consistency','card':330,'counts':counts,
              'accepted_date':None,'accepted_postal_date':None,
              'limits':['Provisional class equality and approximate source windows; replay does not inspect ink.',
                        'Encoded slots and unresolved families are not physical-body counts or accuracy.',
                        'Correlated alternatives retained as one span mask; no independent cross-combinations.',
                        'Source-first AI snapshots are not certified blind or human validation.',
                        'Coherent coordinated edits cannot be disproved by consistency checks.']}
    if source_image is not None:
        result['explicit_source_identity'] = source_image_hash(source_image)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-image',type=Path,help='Explicitly hash a local picture JPEG; no pixel/classification check.')
    args = parser.parse_args()
    try:
        print(json.dumps(verify_card330(source_image=args.source_image),ensure_ascii=False,indent=2))
    except (VerificationError,OSError,TypeError,KeyError,csv.Error) as exc:
        sys.exit(f'Experimental card330 replay failed: {exc}')
