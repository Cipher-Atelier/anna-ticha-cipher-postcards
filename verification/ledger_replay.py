#!/usr/bin/env python3
"""Offline consistency replay of saved proposals; no image classification or research."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

REQUIRED_CARDS = (314, 315, 316, 318, 319, 320, 322, 324, 325, 326, 327, 328)
KEY_PATH = 'verification/anna-ticha/data/key.csv'
ATLAS_PATH = 'verification/anna-ticha/data/glyph_atlas.json'
KEY_SHA = 'fe0a7272d6e372eefd4710b86f502e8c666fa5dfe8d1a17cc06df5e25deb0d95'
ATLAS_SHA = 'c517adfffa74588f9751fbc3fbd2f28ee707fd41c6ca4b961497c57321fd770b'
REGIONS = {318: ('A',), 322: ('MAIN', 'LEFT'), 324: ('LEFT', 'BOTTOM')}
GROUP_COUNTS = dict(zip(REQUIRED_CARDS, (55, 42, 24, 17, 31, 40, 41, 37, 54, 34, 56, 53)))
UNKNOWN_IDS = {314: ('U2',), 316: ('U2',), 319: ('U1',), 325: ('U1', 'U2'),
               326: ('U1',), 327: ('U1', 'U2', 'U3'), 328: ('U1', 'U2', 'U3', 'U4')}
ALTERNATIVE_IDS = {316: ('A1', 'A2'), 326: ('A1',), 327: ('A1',)}
ORIENTATIONS = {'NONE', 'CCW90', 'CW90', 'ROTATE_90_CCW', 'ROTATE_180'}
COUNTER_NAMES = {
    'groups': ('word_groups', 'words'),
    'mapped_bodies': ('mapped_bodies', 'invariant_mapped_bodies'),
    'emitted_letters': ('emitted_letters', 'emitted_nonunknown_letters', 'emitted_invariant_letters'),
    'distinct_classes': ('observed_classes', 'observed_invariant_classes', 'distinct_classes'),
    'capped_ch_bodies': ('capped_ch_bodies',),
    'unknown_clusters': ('unknown_clusters', 'unresolved_clusters'),
    'alternative_bodies': ('alternative_bodies',),
}


class VerificationError(ValueError):
    """A saved package cannot be consistently replayed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def sha(path):
    require(path.is_file(), f'Missing required file: {path.name}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(path, expected, context):
    require(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected),
            f'{context}: invalid SHA-256')
    require(sha(path) == expected, f'{context}: fingerprint mismatch')


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, f'Duplicate JSON key: {key}')
        obj[key] = value
    return obj


def read_json(path):
    require(path.is_file(), f'Missing required file: {path.name}')
    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    except json.JSONDecodeError as exc:
        raise VerificationError(f'{path.name}: malformed JSON') from exc


def integer(value, context, minimum=0):
    if isinstance(value, str):
        require(re.fullmatch(r'0|[1-9][0-9]*', value), f'{context}: malformed integer')
        value = int(value)
    require(type(value) is int and value >= minimum, f'{context}: invalid integer')
    return value


def check_boxes(value, size, context):
    """Bounds use saved dimensions, never downloaded pixels."""
    if isinstance(value, dict):
        for name, box in value.items():
            label = f'{context}.{name}'
            if name.endswith('bbox_xyxy'):
                if box is None and name == 'initial_context_bbox_xyxy':
                    continue
                if isinstance(box, str):
                    try:
                        box = json.loads(box)
                    except json.JSONDecodeError as exc:
                        raise VerificationError(f'{label}: malformed box') from exc
                    if box is None and name == 'initial_context_bbox_xyxy':
                        continue
                require(isinstance(box, list) and len(box) == 4 and
                        all(type(v) is int for v in box), f'{label}: malformed box')
                x0, y0, x1, y1 = box
                require(0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1],
                        f'{label}: out-of-bounds box')
            else:
                check_boxes(box, size, label)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_boxes(item, size, f'{context}[{index}]')


def load_key(repo):
    fingerprint(repo / KEY_PATH, KEY_SHA, 'unchanged key')
    fingerprint(repo / ATLAS_PATH, ATLAS_SHA, 'unchanged atlas')
    with (repo / KEY_PATH).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream, strict=True))
    key = {}
    for row in rows:
        require(row['class_id'] not in key, 'Duplicate key class')
        require(re.fullmatch('[a-z]+', row['literal']), 'Invalid key literal')
        key[row['class_id']] = row['literal']
    atlas = read_json(repo / ATLAS_PATH)
    atlas_key = {row['class_id']: row['literal'] for row in atlas}
    require(len(atlas_key) == len(atlas) and atlas_key == key, 'Key/atlas mapping mismatch')
    require(key['G10_CAP'] == 'ch' and key['H440_N01_UNBARRED_LEFT_BOWL'] == 't',
            'Established ch/t mapping mismatch')
    return key


def no_accepted_mapping(record, context):
    forbidden = {'literal_value', 'key_value', 'class_id', 'classes', 'mapped_bodies',
                 'invariant_mapped_bodies', 'value', 'partition'}
    require(not any(k in forbidden or k.startswith('accepted_') for k in record),
            f'{context}: unresolved record has accepted mapping')


def unknown_semantics(record, context, literal_mask=None):
    require(isinstance(record, dict), f'{context}: malformed unknown declaration')
    require(isinstance(record.get('status'), str) and record['status'], f'{context}: missing unknown status')
    no_accepted_mapping(record, context)
    require('literal' not in record or (literal_mask is not None and record['literal'] == literal_mask),
            f'{context}: unknown has accepted literal or invalid mask')
    require('body_count' not in record or record['body_count'] == 'not established',
            f'{context}: unknown has accepted body count')


def candidates(classes, key, context):
    require(isinstance(classes, list) and len(classes) == 2 and len(set(classes)) == 2,
            f'{context}: invalid alternative candidates')
    require(all(c in key for c in classes), f'{context}: unknown alternative candidate')
    return '[' + '/'.join(key[c] for c in classes) + ']'


def declaration_record(record, context):
    match = re.match(r'^L([1-9][0-9]*)(?:W| word)([1-9][0-9]*)(?:\b|\s)', record.get('record', ''))
    require(match is not None, f'{context}: malformed declaration record')
    return int(match[1]), int(match[2])


def declarations(manifest, card, key):
    unknowns, alternatives = {}, {}
    for item in manifest.get('unknowns', []):
        unknown_semantics(item, f'card{card} unknown', f"[{item.get('id')}]")
        ident = item.get('id')
        require(isinstance(ident, str) and re.fullmatch(r'U[1-9][0-9]*', ident) and ident not in unknowns,
                f'card{card}: malformed/duplicate unknown ID')
        if 'literal' in item:
            require(item['literal'] == f'[{ident}]', f'card{card}: unknown mask mismatch')
        unknowns[ident] = declaration_record(item, f'card{card} {ident}')
    for item in manifest.get('alternatives', []) + (manifest.get('ambiguous_bodies', [])
                                                  if isinstance(manifest.get('ambiguous_bodies', []), list) else []):
        ident = item.get('id')
        require(isinstance(ident, str) and re.fullmatch(r'A[1-9][0-9]*', ident) and ident not in alternatives,
                f'card{card}: malformed/duplicate alternative ID')
        no_accepted_mapping(item, f'card{card} {ident}')
        classes = item.get('candidate_classes', item.get('alternatives'))
        rendered = candidates(classes, key, f'card{card} {ident}')
        expected = '[y/i]' if card == 316 else '[k/z]'
        require(rendered == expected and item.get('literal', item.get('rendered_literal')) == rendered,
                f'card{card} {ident}: alternative mask mismatch')
        require(type(item.get('body_count', 1)) is int and item.get('body_count', 1) == 1, f'card{card} {ident}: alternative body count mismatch')
        alternatives[ident] = (declaration_record(item, f'card{card} {ident}'), rendered)
    require(set(unknowns) == set(UNKNOWN_IDS.get(card, ())), f'card{card}: unknown ID declarations mismatch')
    require(set(alternatives) == set(ALTERNATIVE_IDS.get(card, ())), f'card{card}: alternative ID declarations mismatch')
    return unknowns, alternatives


def rows_from_csv(path, card):
    base = ['line', 'word', 'classes', 'literal', 'source_bbox_xyxy', 'orientation']
    if card in REGIONS:
        base.insert(0, 'region')
    if card == 318:
        base.insert(base.index('orientation'), 'bbox_kind')
    if card == 316:
        base += ['invariant_mapped_bodies', 'alternative_bodies', 'unresolved_clusters']
    else:
        base += ['mapped_bodies']
        if card in UNKNOWN_IDS:
            base += ['unknown_clusters']
    if card != 318:
        base += ['initial_context_bbox_xyxy']
    if card in (326, 327):
        base += ['ambiguous_bodies']
    require(path.is_file(), f'Missing required file: {path.name}')
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        require(reader.fieldnames == base, f'card{card}: CSV schema mismatch')
        rows = list(reader)
    require(all(None not in row and None not in row.values() for row in rows),
            f'card{card}: malformed CSV row')
    require(len(rows) == GROUP_COUNTS[card], f'card{card}: required record count mismatch')
    return rows


def article_literal(repo, card, literal, block=0):
    path = repo / f'anna-ticha/card-{card}.md'
    require(path.is_file(), f'Missing required article: card-{card}.md')
    blocks = re.findall(r'^```text\n(.*?)^```\s*$', path.read_text(encoding='utf-8'), re.M | re.S)
    require(len(blocks) > block and blocks[block] == literal,
            f'card{card}: diplomatic literal/article mismatch (block {block + 1})')


def replay_card(repo, card, key):
    package = repo / f'research-updates/evidence/card{card}-2026-10-09'
    require(package.is_dir(), f'Missing required package: card{card}')
    manifest = read_json(package / 'manifest.json')
    size = manifest.get('source_size_pixels')
    require(isinstance(size, list) and len(size) == 2 and
            all(type(v) is int and v > 0 for v in size), f'card{card}: invalid saved source dimensions')
    require(re.fullmatch('[0-9a-f]{64}', manifest.get('source_sha256', '')), f'card{card}: invalid source fingerprint')
    for name, path, digest in (('key', KEY_PATH, KEY_SHA), ('atlas', ATLAS_PATH, ATLAS_SHA)):
        require(manifest.get(f'{name}_path') == path and manifest.get(f'{name}_sha256') == digest,
                f'card{card}: {name} fingerprint/path mismatch')
    fingerprint(package / 'word-ledger.csv', manifest.get('ledger_sha256'), f'card{card} ledger')
    fingerprint(package / 'literal.txt', manifest.get('literal_sha256'), f'card{card} literal')
    check_boxes(manifest, size, f'card{card} manifest')
    unknowns, alternatives = declarations(manifest, card, key)
    rows = rows_from_csv(package / 'word-ledger.csv', card)
    regions = REGIONS.get(card, ('',))
    records, decoded, totals, observed = {}, {}, dict.fromkeys(COUNTER_NAMES, 0), set()
    unknown_uses, alternative_uses = set(), set()
    previous = None
    for row in rows:
        region = row.get('region', '')
        require(region in regions, f'card{card}: invalid region label')
        line = integer(row['line'], f'card{card} line', 1)
        word = integer(row['word'], f'card{card} word', 1)
        ident = (region, line, word)
        require(ident not in records, f'card{card}: duplicate record ID {ident}')
        if previous is None or region != previous[0]:
            next_region = 0 if previous is None else regions.index(previous[0]) + 1
            require(next_region < len(regions) and region == regions[next_region] and (line, word) == (1, 1),
                    f'card{card}: record order/indices mismatch')
        elif line == previous[1]:
            require(word == previous[2] + 1, f'card{card}: record order/indices mismatch')
        else:
            require(line == previous[1] + 1 and word == 1, f'card{card}: record order/indices mismatch')
        previous = ident
        context = f'card{card} {region} L{line}W{word}'
        require(row['orientation'] in ORIENTATIONS, f'{context}: invalid orientation')
        check_boxes(row, size, context)
        tokens = row['classes'].split(' ')
        require(tokens and all(tokens), f'{context}: malformed class sequence')
        values, mapped, letters, unknown, alternative, capped = [], 0, 0, 0, 0, 0
        for token in tokens:
            # Card319's retained CSV calls its declared U1 cluster UNKNOWN.
            if card == 319 and token == 'UNKNOWN':
                token = 'U1'
            if token in key:
                values.append(key[token])
                mapped += 1
                letters += len(key[token])
                capped += token == 'G10_CAP'
                observed.add(token)
            elif token in unknowns:
                require(unknowns[token] == (line, word) and token not in unknown_uses,
                        f'{context}: unknown ID use mismatch')
                unknown_uses.add(token)
                values.append(f'[{token}]')
                unknown += 1
            elif token in alternatives:
                require(alternatives[token][0] == (line, word) and token not in alternative_uses,
                        f'{context}: alternative ID use mismatch')
                alternative_uses.add(token)
                values.append(alternatives[token][1])
                alternative += 1
            else:
                raise VerificationError(f'{context}: unknown class or undeclared mask {token}')
        require(''.join(values) == row['literal'], f'{context}: row literal/key mapping mismatch')
        # Intraword punctuation belongs to assembled output, not the CSV word literal.
        for mark in manifest.get('intraword_punctuation', []):
            if (mark.get('region', ''), mark.get('line'), mark.get('word')) == ident:
                offset = integer(mark.get('after_class'), f'{context} intraword offset', 1)
                require(offset < len(values) and mark.get('literal') == '-', f'{context}: invalid intraword punctuation')
                values[offset - 1] += mark['literal']
        literal = ''.join(values)
        row_counts = {'mapped_bodies': mapped, 'invariant_mapped_bodies': mapped,
                      'unknown_clusters': unknown, 'unresolved_clusters': unknown,
                      'alternative_bodies': alternative, 'ambiguous_bodies': alternative}
        for field, actual in row_counts.items():
            if field in row:
                require(integer(row[field], f'{context} {field}') == actual,
                        f'{context}: row {field} counter mismatch')
        for field, actual in (('mapped_bodies', mapped), ('emitted_letters', letters),
                              ('unknown_clusters', unknown), ('alternative_bodies', alternative),
                              ('capped_ch_bodies', capped)):
            totals[field] += actual
        records[ident], decoded[ident] = row, literal
    require(set(r[0] for r in records) == set(regions), f'card{card}: missing required region')
    require(unknown_uses == set(unknowns), f'card{card}: unused unknown declarations')
    require(alternative_uses == set(alternatives), f'card{card}: unused alternative declarations')
    totals['groups'], totals['distinct_classes'] = len(rows), len(observed)
    for metric, fields in COUNTER_NAMES.items():
        present = [field for field in fields if field in manifest]
        require(present, f'card{card}: missing aggregate {metric} counter')
        for field in present:
            require(integer(manifest[field], f'card{card} {field}') == totals[metric],
                    f'card{card}: aggregate {field} counter mismatch')
    punctuation = manifest.get('replay_punctuation', manifest.get('punctuation'))
    require(isinstance(punctuation, list), f'card{card}: missing structured punctuation')
    marks = {}
    for mark in punctuation:
        ident = (mark.get('region', ''), integer(mark.get('line'), 'punctuation line', 1),
                 integer(mark.get('after_word'), 'punctuation word', 1))
        require(ident in records and ident not in marks and mark.get('literal') in ('.', ',', '?', '!', '-', '? —'),
                f'card{card}: invalid/duplicate punctuation position or literal')
        marks[ident] = mark['literal']
    for mark in manifest.get('additional_marks', []):
        if 'literal' in mark:
            ident = (mark.get('region', ''), mark.get('line'), mark.get('after_word'))
            require(ident in records and mark['literal'] == '—', f'card{card}: invalid additional punctuation')
            marks[ident] = marks.get(ident, '') + ' ' + mark['literal']
    intra_seen = set()
    for mark in manifest.get('intraword_punctuation', []):
        ident = (mark.get('region', ''), mark.get('line'), mark.get('word'))
        require(ident in records and ident not in intra_seen, f'card{card}: invalid/duplicate intraword position')
        intra_seen.add(ident)
    blocks = []
    for region in regions:
        lines = []
        for line in sorted({ident[1] for ident in records if ident[0] == region}):
            lines.append(' '.join(decoded[i] + marks.get(i, '') for i in records if i[:2] == (region, line)))
        prefix = f'REGION {region}\n' if card in (322, 324) else ''
        blocks.append(prefix + '\n'.join(lines))
    literal = '\n\n'.join(blocks) + '\n'
    require(literal.encode('utf-8') == (package / 'literal.txt').read_bytes(), f'card{card}: assembled saved literal/punctuation mismatch')
    article_literal(repo, card, literal)
    return {'card': card, 'status': 'passed', **totals}, manifest


def replay_margins(repo, manifest, key):
    package = repo / 'research-updates/evidence/card318-2026-10-09'
    expected_files = {'margin-b-ledger.json', 'margin-cd-ledger.json', 'margin-b-literal.txt', 'margin-cd-literal.txt'}
    require(set(manifest.get('margin_sha256', {})) == expected_files, 'card318: marginal fingerprint inventory mismatch')
    for name, digest in manifest['margin_sha256'].items():
        fingerprint(package / name, digest, f'card318 {name}')
    b = read_json(package / 'margin-b-ledger.json')
    cd = read_json(package / 'margin-cd-ledger.json')
    for ledger in (b, cd):
        require(ledger.get('source_sha256') == manifest['source_sha256'] and
                ledger.get('source_url') == manifest['source_url'], 'card318 margin: source fingerprint mismatch')
        require(ledger.get('key_path') == KEY_PATH and ledger.get('key_sha256') == KEY_SHA,
                'card318 margin: key fingerprint/path mismatch')
        check_boxes(ledger, manifest['source_size_pixels'], 'card318 margin')
    profiles = {
        'B': (5, 19, {'B.G3.U2': ['G07', 'G05']}, {'B.G3.final_cluster'}),
        'C': (8, 35, {'C.G7.U6': ['G04', 'G11']}, {'C.cluster'}),
        'D': (6, 27, {}, {'D.cluster1', 'D.cluster2'}),
    }
    require(isinstance(cd.get('strips'), list) and [s.get('id') for s in cd['strips']] == ['C', 'D'],
            'card318 margin: strip IDs/order mismatch')
    rendered, reports = {}, []
    for name, strip in [('B', b)] + [(s['id'], s) for s in cd['strips']]:
        count, invariant, alt_ids, unknown_ids = profiles[name]
        require(strip.get('orientation') in ORIENTATIONS, f'card318 margin {name}: invalid orientation')
        groups = strip.get('groups', [])
        require(len(groups) == count and [g.get('group') for g in groups] == list(range(1, count + 1)) and
                all(type(g.get('group')) is int for g in groups), f'card318 margin {name}: group IDs/order mismatch')
        seen, mapped, words = set(), 0, []
        for group in groups:
            values = []
            require(isinstance(group.get('units'), list) and group['units'], f'card318 margin {name}: invalid units')
            for unit in group['units']:
                if isinstance(unit, str):
                    require(unit in key, f'card318 margin {name}: unknown class {unit}')
                    values.append(key[unit])
                    mapped += 1
                    continue
                require(isinstance(unit, dict), f'card318 margin {name}: malformed unit')
                ident = unit.get('id')
                require(isinstance(ident, str) and ident not in seen, f'card318 margin {name}: duplicate/malformed unit ID')
                seen.add(ident)
                if ident in alt_ids:
                    literal = candidates(unit.get('candidates'), key, f'card318 margin {ident}')
                    no_accepted_mapping(unit, f'card318 margin {ident}')
                    require(all(unit[field] == literal for field in ('literal', 'rendered_literal') if field in unit),
                            f'card318 margin {ident}: alternative mask mismatch')
                    require(unit['candidates'] == alt_ids[ident] and type(unit.get('body_count', 1)) is int and
                            unit.get('body_count', 1) == 1,
                            f'card318 margin {ident}: alternative semantics mismatch')
                    if 'review_preference' in unit:
                        require(unit['review_preference'] in unit['candidates'], f'card318 margin {ident}: invalid preference')
                    values.append(literal)
                else:
                    require(ident in unknown_ids, f'card318 margin {name}: undeclared unknown ID')
                    unknown_semantics(unit, f'card318 margin {ident}')
                    require(unit.get('body_count') == 'not established', f'card318 margin {ident}: unknown has accepted body count')
                    for field in ('candidate_partition',):
                        if field in unit:
                            require(isinstance(unit[field], list) and unit[field] and all(c in key for c in unit[field]),
                                    f'card318 margin {ident}: invalid candidate partition')
                    if 'one_body_candidate' in unit:
                        require(unit['one_body_candidate'] in key, f'card318 margin {ident}: invalid conditional candidate')
                    values.append('[UNRESOLVED_CLUSTER]' if name == 'B' else f'[{ident}]')
            words.append(''.join(values))
        require(seen == set(alt_ids) | unknown_ids, f'card318 margin {name}: missing unit ID')
        field = 'invariant_mapped_bodies' if name == 'B' else 'invariant_proposed_mappings'
        require(integer(strip.get(field), f'card318 margin {name} invariant') == mapped == invariant,
                f'card318 margin {name}: invariant counter mismatch')
        if name == 'B':
            require(integer(strip.get('unresolved_class_choice_bodies'), 'margin B alternative counter') == 1 and
                    integer(strip.get('unresolved_clusters'), 'margin B unknown counter') == 1 and
                    strip.get('whole_strip_body_count') == 'not established', 'card318 margin B: mask counters mismatch')
            require([m.get('id') for m in strip.get('separate_marks', [])] == ['B.terminal_mark'],
                    'card318 margin B: separate mark ID mismatch')
        rendered[name] = ' '.join(words)
        reports.append({'region': name, 'groups': count, 'invariant_mapped_bodies': mapped,
                        'alternative_bodies': len(alt_ids), 'unknown_clusters': len(unknown_ids)})
    b_literal = rendered['B'] + ' [QUESTION_LIKE_MARK]\n'
    cd_literal = 'C: ' + rendered['C'] + '\nD: ' + rendered['D'] + '\n'
    for name, literal, block in [('margin-b-literal.txt', b_literal, 1), ('margin-cd-literal.txt', cd_literal, 2)]:
        require(literal.encode('utf-8') == (package / name).read_bytes(), f'card318 {name}: assembled saved literal mismatch')
        article_literal(repo, 318, literal, block)
    return reports


def verify_all(repo=None):
    repo = Path(repo) if repo is not None else Path(__file__).resolve().parent.parent
    key = load_key(repo)
    cards, margins = [], []
    for card in REQUIRED_CARDS:
        report, manifest = replay_card(repo, card, key)
        cards.append(report)
        if card == 318:
            margins = replay_margins(repo, manifest, key)
    return {'status': 'passed', 'cards': cards, 'card318_margins': margins,
            'limits': ['Consistency of saved proposals only; no source classification or accuracy certification.',
                       'Saved dimensions support bounds checks, not source-image verification.',
                       'Coherent coordinated edits to evidence cannot be disproved by consistency checks.',
                       'Card330 candidates and date are excluded; no accepted ledger or original fingerprint.']}


if __name__ == '__main__':
    try:
        print(json.dumps(verify_all(), ensure_ascii=False, indent=2))
    except (VerificationError, OSError, csv.Error, TypeError, KeyError) as exc:
        sys.exit(f'Ledger replay failed: {exc}')
