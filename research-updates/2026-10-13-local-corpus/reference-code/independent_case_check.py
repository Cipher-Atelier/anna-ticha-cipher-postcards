"""Independent read-only reconstruction from released canonical source records.

No runner/core/helper imports, source rendering, network, or previous projections.
Unsupported ledger adapters fail rather than silently reinterpret source evidence.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEY = ROOT.parent / 'anna-card330-research/verification/anna-ticha/data/key.csv'
KEY_SHA = 'fe0a7272d6e372eefd4710b86f502e8c666fa5dfe8d1a17cc06df5e25deb0d95'
# Independently reviewed output-format generations, bound to immutable releases.
ORDINARY_RENDERING = {
    'ff5c454508ed2b9a586513aa55d653cb35136612993528e6415097d87cb34c5a': 'text_only',
    '83515492af21f5f2fa1f162d2f344993ae8c92c94273daa2eabf74fbfde996e2': 'text_and_marks',
    '762930cd5904b2e1c83fc6b175c03e854167822bceb5e22209808333d5aac115': 'text_marks_print_and_null_uncertainty',
    'd3136f10dd0803a7e68434187812e36c39c6934e83d7b2a5c94700a57fe8dd38': 'text_marks_print_and_null_uncertainty',
    '122b9fd756ccf3b57abc6f137b0563c28f1a97ed2affd0b7c2f5e9cfb3930685': 'text_marks_print_and_null_uncertainty',
}
PREKEY_RUNNER = '122b9fd756ccf3b57abc6f137b0563c28f1a97ed2affd0b7c2f5e9cfb3930685'
NEUTRAL_ATLAS = ROOT.parent / 'card330-local-source/reader-a/atlas-class-only.json'
NEUTRAL_ATLAS_SHA = '4073dedf037195260165a77023948d3d01f62addc11a164a2fe268f1e608c0c3'
COUNT_FIELDS = ['representation_slots', 'provisionally_mapped_slots',
                'masked_representation_slots', 'emitted_known_letters',
                'capped_ch_slots', 'recorded_punctuation_marks', 'uncertain_punctuation_masks']
FIELDS = ['record_type', 'card_id', 'face', 'region_id', 'row_id', 'row_index',
          'group_id', 'group_index', 'unit_id', 'unit_index', 'unit_bbox_xyxy',
          'group_bbox_xyxy', 'row_bbox_xyxy', 'orientation', 'class_id_recorded',
          'alternatives_recorded', 'status_recorded', 'shape_notes_recorded',
          'raw_unit_recorded', 'emitted', 'representation_slots',
          'provisionally_mapped_slots', 'masked_representation_slots',
          'emitted_known_letters', 'physical_body_count', 'reader_physical_body_count_recorded',
          'masked_by_source_review_overlay', 'source_review_mask_reason']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def resolve(ref):
    path = (ROOT / ref['path']).resolve()
    assert path.is_relative_to(ROOT) and digest(path) == ref['sha256'], ref
    return read(path)


def check_code_bindings(release, receipt):
    """Scalar code/source bindings only; no imports or reconstruction."""
    assert release['runner_sha256'] in ORDINARY_RENDERING, 'Unreviewed runner rendering generation'
    code_directory = (ROOT / release.get('code_snapshot_directory', '.')).resolve()
    assert code_directory.is_relative_to(ROOT), 'Code snapshot outside completion root'
    modules = [('runner', 'run_cases.py'), ('shared_core', 'shared_replay.py'),
               ('source_adapters', 'source_adapters.py')]
    if release['runner_sha256'] == PREKEY_RUNNER:
        modules.append(('source_preflight', 'source_preflight.py'))
        assert receipt['code_sha256']['neutral_class_atlas'] == NEUTRAL_ATLAS_SHA, 'Neutral class-only atlas receipt mismatch'
        assert digest(NEUTRAL_ATLAS) == NEUTRAL_ATLAS_SHA, 'Neutral class-only atlas bytes drift'
    for name, label in modules:
        actual = digest(code_directory / label)
        assert receipt['code_sha256'][name] == actual, 'Receipt code fingerprint mismatch: ' + name
        assert release[name + '_sha256'] == actual, 'Release code fingerprint mismatch: ' + name


def validate_nontext_record(record, rendering):
    """Explicit source null means no recorded uncertainty, never certainty."""
    assert isinstance(record.get('shape_note'), str) and record['shape_note'], 'Nontext shape note must be a nonempty string'
    assert 'uncertainty' in record, 'Nontext uncertainty field must be present'
    uncertainty = record['uncertainty']
    if uncertainty is None:
        assert rendering == 'text_marks_print_and_null_uncertainty', 'Explicit null uncertainty requires reviewed null-aware mode'
    else:
        assert isinstance(uncertainty, str) and uncertainty, 'Nontext uncertainty must be a nonempty string or explicit null'


def check(case_path, release_path, release_sha, output, reproduction=None):
    assert digest(release_path) == release_sha
    release = read(release_path)
    rendering = ORDINARY_RENDERING[release['runner_sha256']]
    assert any((ROOT / ref['path']).resolve() == case_path.resolve()
               and ref['sha256'] == digest(case_path) for ref in release['cases'])
    case = read(case_path)
    assert digest(KEY) == KEY_SHA
    with KEY.open(encoding='utf-8-sig', newline='') as stream:
        key = {r['class_id']: r['literal'] for r in csv.DictReader(stream)}
    assert len(key) == 24
    receipt = read(output / 'replay-receipt.json')
    references = {}

    def refs(obj):
        if isinstance(obj, dict):
            if set(obj) == {'path', 'sha256'}:
                resolve(obj)
                references[obj['path']] = obj['sha256']
            else:
                for value in obj.values():
                    refs(value)
        elif isinstance(obj, list):
            for value in obj:
                refs(value)

    refs(case)
    selection = resolve(case['selection'])
    sources = {f['face']: f for f in selection['faces']}
    for source in sources.values():
        assert digest(source['local_path']) == source['sha256']
        assert Path(source['local_path']).stat().st_size == source['bytes']
    overlay = resolve(case['overlay'])
    masks = {r['unit_id']: r for r in overlay['records']}
    assert len(masks) == len(overlay['records'])
    review = resolve(case['review'])
    assert set(masks) == {r['unit_id'] for r in review['proposed_additional_masks']}
    expected_files = {}
    document_counts, region_counts, summaries, punctuation, row_metadata, scopes = {}, {}, {}, {}, {}, {}
    original_punctuation = {}
    ordered_scopes, total_rows, all_units = [], 0, {}
    sections = []
    notes = ['Source coding is uncertain; ordinary text is copied exactly. No date normalization, context repair or translation.']
    diplomatic = resolve(case['diplomatic'])
    ordinary_count = 0
    for face in ('picture', 'address'):
        for profile in case['faces'][face]['cipher_ledgers']:
            sid = profile['scope_id']
            document = resolve(profile['ledger'])
            adapter = profile.get('metadata_adapter', 'canonical')
            assert adapter in ('canonical', 'source_graphical_ledger_v1_card211', 'source_terminal_group_punctuation_v1_card213'), 'Adapter needs independent review'
            if adapter == 'source_terminal_group_punctuation_v1_card213':
                assert case['card_id'] == 213 and document['orientation'] == 'NONE'
            if adapter == 'source_graphical_ledger_v1_card211':
                assert case['card_id'] == 211 and document['schema_version'] == 'source_graphical_ledger_v1'
                assert document['physical_glyph_total'] is None
                assert document['source_dimensions'] == sources[face]['dimensions']
                for field in ('sha256', 'bytes', 'dimensions', 'source_url'):
                    assert document['source_metadata'][field] == sources[face][field]
            assert document['card'] == case['card_id'] and document['orientation'] == profile['orientation']
            dims = sources[face]['dimensions']
            if profile['orientation'] in ('CW90', 'CCW90'):
                dims = list(reversed(dims))
            assert profile['orientation'] in ('NONE', 'CW90', 'CCW90', 'ROTATE_180')
            assert document['oriented_dimensions'] == dims
            binding = resolve(profile['regions'])
            regions = binding['regions']
            row_regions = {rid: region['region_id'] for region in regions for rid in region['row_ids']}
            assert list(row_regions) == [row['id'] for row in document['rows']]
            scopes[sid] = {'face': face, 'regions': regions, 'row_region_ids': row_regions}
            counts = Counter(dict.fromkeys(COUNT_FIELDS, 0))
            original_punctuation[sid] = {g['id']: g['punctuation'] for row in document['rows'] for g in row['groups'] if g.get('punctuation')}
            tokens, group_summaries, marks, lines = [], [], [], []
            distinct = set()
            scoped_masks = 0
            for ri, row in enumerate(document['rows'], 1):
                words = []
                for gi, group in enumerate(row['groups'], 1):
                    gc = Counter(dict.fromkeys(COUNT_FIELDS, 0))
                    unit_text = {}
                    for ui, unit in enumerate(group['units'], 1):
                        uid = unit['id']
                        assert uid not in all_units
                        assert unit['status'] in ('provisional_known_class', 'unresolved_shape', 'unresolved_span'), 'New status needs explicit check'
                        proposed_physical = unit.get('physical_body_count')
                        assert proposed_physical is None or type(proposed_physical) is int and proposed_physical == 1
                        x0, y0, x1, y1 = unit['bbox_xyxy']
                        assert all(type(v) is int for v in (x0, y0, x1, y1))
                        assert 0 <= x0 < x1 <= dims[0] and 0 <= y0 < y1 <= dims[1]
                        cid = unit.get('class_id')
                        mask = masks.get(uid)
                        if mask:
                            assert mask['face'] == face and mask['raw_class_id'] == cid
                            assert mask['raw_status'] == unit['status'] == 'provisional_known_class'
                            assert mask['raw_bbox_xyxy'] == unit['bbox_xyxy'] and not unit['alternatives']
                            scoped_masks += 1
                        uncertain = unit['status'] != 'provisional_known_class' or bool(unit.get('alternatives')) or cid is None or mask is not None
                        emitted = f'[U:{uid}]' if uncertain else key[cid]
                        unit_text[uid] = emitted
                        if not uncertain:
                            distinct.add(cid)
                        gc.update(representation_slots=1, provisionally_mapped_slots=int(not uncertain),
                                  masked_representation_slots=int(uncertain), emitted_known_letters=0 if uncertain else len(emitted),
                                  capped_ch_slots=int(not uncertain and cid == 'G10_CAP'))
                        token = dict(record_type='unit', card_id=case['card_id'], face=face, region_id=row_regions[row['id']],
                                     row_id=row['id'], row_index=ri, group_id=group['id'], group_index=gi,
                                     unit_id=uid, unit_index=ui, unit_bbox_xyxy=unit['bbox_xyxy'], group_bbox_xyxy=group['bbox_xyxy'],
                                     row_bbox_xyxy=row.get('bbox_xyxy'), orientation=profile['orientation'], class_id_recorded=cid,
                                     alternatives_recorded=unit.get('alternatives', []), status_recorded=unit['status'],
                                     shape_notes_recorded=unit.get('shape_notes'), raw_unit_recorded=unit, emitted=emitted,
                                     representation_slots=1, provisionally_mapped_slots=int(not uncertain), masked_representation_slots=int(uncertain),
                                     emitted_known_letters=0 if uncertain else len(emitted), physical_body_count=None,
                                     reader_physical_body_count_recorded=unit.get('physical_body_count'),
                                     masked_by_source_review_overlay=mask is not None, source_review_mask_reason=mask['reason'] if mask else None)
                        tokens.append(token)
                        all_units[uid] = token
                    before, after = {}, {}
                    for mi, mark in enumerate(group.get('punctuation', []), 1):
                        if adapter == 'source_terminal_group_punctuation_v1_card213':
                            assert len(group['punctuation']) == 1 and group['units']
                            assert set(mark) == {'mark', 'ownership', 'bbox_xyxy'} and mark['ownership'] == 'terminal_group'
                            assert mark['mark'] in ('.', ',', '-')
                            mark = dict(id=group['id'] + '-RECORDED-MARK-' + str(mi), literal=mark['mark'], status='recorded',
                                        after_unit_id=group['units'][-1]['id'], bbox_xyxy=mark['bbox_xyxy'],
                                        original_source_punctuation_record=mark,
                                        metadata_view_operation='Source-recorded terminal_group mark projected to canonical boundary metadata; no source certainty or glyph ownership upgrade.')
                        uncertain = mark['status'] in ('uncertain', 'unresolved') or mark.get('literal') is None
                        rendered = f"[P:{mark['id']}]" if uncertain else mark['literal']
                        target = before if 'before_unit_id' in mark else after
                        uid = mark.get('before_unit_id', mark.get('after_unit_id'))
                        assert uid in unit_text and uid not in target
                        target[uid] = rendered
                        gc.update(recorded_punctuation_marks=1, uncertain_punctuation_masks=int(uncertain))
                        marks.append(dict(row_id=row['id'], group_id=group['id'], id=mark['id'], bbox_xyxy=mark['bbox_xyxy'],
                                          recorded=mark, emitted=rendered, card_id=case['card_id'], face=face, region_id=row_regions[row['id']]))
                    words.append(''.join(before.get(uid, '') + text + after.get(uid, '') for uid, text in unit_text.items()))
                    group_summaries.append(dict(row_id=row['id'], group_id=group['id'], bbox_xyxy=group['bbox_xyxy'],
                                                counts={k: gc[k] for k in COUNT_FIELDS}, physical_body_count=None,
                                                card_id=case['card_id'], face=face, region_id=row_regions[row['id']]))
                    counts.update(gc)
                lines.append(' '.join(words))
            counts['observed_known_classes'] = len(distinct)
            counts['additional_source_review_masks'] = scoped_masks
            document_counts[sid] = dict(counts)
            summaries[sid], punctuation[sid] = group_summaries, marks
            row_metadata[sid] = [{k: v for k, v in row.items() if k != 'groups'} for row in document['rows']]
            region_counts[sid] = []
            for region in regions:
                rc = Counter()
                for g in group_summaries:
                    if g['region_id'] == region['region_id']:
                        rc.update(g['counts'])
                region_counts[sid].append(dict(face=face, region_id=region['region_id'], orientation=profile['orientation'],
                                               counts={k: v for k, v in rc.items() if v > 0}, physical_body_count=None))
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
            writer.writeheader()
            for token in tokens:
                writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')) if isinstance(v, (dict, list))
                                 else '' if v is None else v for k, v in token.items()})
            expected_files[sid + '-tokens.csv'] = stream.getvalue().encode()
            expected_files[sid + '-literal-lines.txt'] = ('\n'.join(lines) + '\n').encode()
            by_row = dict(zip([r['id'] for r in document['rows']], lines))
            for region in regions:
                sections.append(face.upper() + ' CIPHER / ' + region['role'] + ' / ' + region['region_id'] + ' / ' + profile['orientation'])
                sections.extend(by_row[rid] for rid in region['row_ids'])
                sections.append('')
            ordered_scopes.append(sid)
            total_rows += len(lines)
        sections.append(face.upper() + (' ORDINARY SOURCE RECORDS / DIRECT TEXT AND NON-TEXT MARKS'
                                       if rendering == 'text_marks_print_and_null_uncertainty'
                                       else ' ORDINARY HANDWRITING / DIRECT TRANSCRIPTION'))
        for i, record in enumerate(next(f for f in diplomatic['faces'] if f['face'] == face)['records'], 1):
            if record['transcription'] is None:
                validate_nontext_record(record, rendering)
                sections.append('[NON-TEXT ORDINARY GRAPHICAL MARK / RECORD ' + str(i) + ']\nRECORDED SHAPE NOTE (not a transcription): ' + record['shape_note'])
            else:
                assert isinstance(record['transcription'], str) and record['transcription']
                prefix = '[DIRECT PRINTED TEXT / RECORD ' + str(i) + ']\n' if record.get('recorded_kind') == 'direct_printed_text' else ''
                if prefix:
                    assert rendering == 'text_marks_print_and_null_uncertainty'
                sections.append(prefix + record['transcription'])
            uncertainty = record['uncertainty']
            if uncertainty is None:
                assert rendering == 'text_marks_print_and_null_uncertainty'
                uncertainty = '[NO RECORDED UNCERTAINTY; source field is null, not certified certainty]'
            notes.append(face + ' record ' + str(i) + ' ' + json.dumps(record['bbox_xyxy']) + ': ' + uncertainty)
            ordinary_count += 1
        sections.append('')
    warnings = {k: review[k] for k in ('fragment_group_boundary_warnings', 'ordinary_transcription_warnings')}
    for k, entries in warnings.items():
        notes.append(k)
        notes.extend(json.dumps(e, ensure_ascii=False, sort_keys=True, indent=2) for e in entries)
    expected_files['both-face-literal.txt'] = ('\n'.join(sections) + '\n').encode()
    expected_files['both-face-uncertainty-notes.txt'] = ('\n'.join(notes) + '\n').encode()
    for name, data in expected_files.items():
        assert (output / name).read_bytes() == data, name
    assert receipt['outputs_sha256'] == {n: hashlib.sha256(b).hexdigest() for n, b in expected_files.items()}
    expected_parts = dict(card_id=case['card_id'], source_faces=sources, faces_profiles=case['faces'],
                          geometric_editorial_scope_order=ordered_scopes, counts_by_cipher_document=document_counts,
                          counts_by_region=region_counts, groups_by_document=summaries, recorded_punctuation_by_document=punctuation,
                          row_source_metadata_by_document=row_metadata, regions=scopes, physical_body_count=None,
                          warnings=warnings, preprojection_provenance=case['preprojection_provenance'])
    for k, v in expected_parts.items():
        assert receipt[k] == v, k
    if release['runner_sha256'] in ('d3136f10dd0803a7e68434187812e36c39c6934e83d7b2a5c94700a57fe8dd38', PREKEY_RUNNER):
        assert receipt['original_source_punctuation_by_document'] == original_punctuation
    if 'ordinary_records_by_face' in receipt:
        assert receipt['ordinary_records_by_face'] == {f['face']: f['records'] for f in diplomatic['faces']}
        ordinary_counts = {
            f['face']: dict(recorded_scope_records=len(f['records']),
                            direct_transcribed_strings=sum(r['transcription'] is not None for r in f['records']),
                            nontext_graphical_marks=sum(r['transcription'] is None for r in f['records']))
            for f in diplomatic['faces']}
        if rendering == 'text_marks_print_and_null_uncertainty':
            for f in diplomatic['faces']:
                ordinary_counts[f['face']]['direct_printed_records'] = sum(r.get('recorded_kind') == 'direct_printed_text' for r in f['records'])
        assert receipt['ordinary_record_counts_by_face'] == ordinary_counts
        assert receipt['source_review_mode'] == review.get('source_review_mode')
    for k, v in receipt['frozen_refs'].items():
        assert v == case[k]
        resolve(v)
    check_code_bindings(release, receipt)
    assert set(masks) <= set(all_units)
    if reproduction:
        assert {x.name for x in output.iterdir() if x.is_file()} == {x.name for x in reproduction.iterdir() if x.is_file()}
        for path in output.iterdir():
            if path.is_file():
                assert path.read_bytes() == (reproduction / path.name).read_bytes()
    return dict(status='PASS', card_id=case['card_id'], csv_records_all_fields=len(all_units),
                groups=sum(map(len, summaries.values())), cipher_rows=total_rows, exact_review_masks=len(masks),
                ordinary_records=ordinary_count, warning_objects=sum(map(len, warnings.values())),
                counts_by_document=document_counts, unique_manifest_refs=len(references),
                reconstructed_output_files=len(expected_files), compared_reproduction_files=len(expected_files) + 1 if reproduction else 0,
                output_hashes={p.name: digest(p) for p in output.iterdir() if p.is_file()},
                imports_of_runner_core_or_old_helpers=False, old_projections_or_suites_run=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--release-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reproduction', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.case, args.release, args.release_sha, args.output, args.reproduction), ensure_ascii=False, indent=2))
