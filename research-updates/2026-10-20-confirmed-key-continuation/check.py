"""Replay frozen anchor and any derived cards without private inputs or network."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from decode import NOTATION, decode_text

EXPECTED_KEY = dict(zip('12345678bcdfghmnpqrstř',
                        ['Y', 'U', 'O', 'I', 'E', 'A', 'J', 'L', 'P', 'S', 'T', 'V',
                         'Z', 'R', 'N', 'M', 'B', 'K', 'H', 'C', 'D', 'CH']))
PDF_SHA256 = 'da35fdcacd0e47014e34c9d22cfeca74d577b7ed1526ec8a36b17106d5d4a11b'
ROWS_SHA256 = '8b0c2c0ce69adf65838d7cbac0ed40ca48b8d9054cdfe75d738c945a9520f183'
COUNTS = ('encoded_bodies', 'expanded_letters', 'ch_occurrences', 'unknowns')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def replay(lines, notation):
    require(notation == NOTATION, f'Unsupported notation: {notation!r}')
    require(isinstance(lines, list) and lines, 'lines must be a nonempty list')
    totals = dict.fromkeys(COUNTS, 0)
    seen = set()
    for line in lines:
        identifier = line.get('line_id')
        require(isinstance(identifier, str) and identifier and identifier not in seen,
                'Missing or duplicate line_id')
        seen.add(identifier)
        result = decode_text(line['ciphertext'], notation=notation, transcription=line.get('transcription'))
        require(result['literal'] == line.get('literal'), f'{identifier}: literal mismatch')
        require(result['unknowns'] == line.get('unknowns', []), f'{identifier}: unknown ledger mismatch')
        for name in COUNTS:
            value = (sum(entry['kind'] != 'numeral' for entry in result[name])
                     if name == 'unknowns' else result[name])
            if name in line:
                require(line[name] == result[name], f'{identifier}: {name} mismatch')
            totals[name] += value
    return {'rows': len(lines), **totals}


def check_card(card):
    require(isinstance(card.get('card_id'), (str, int)) and bool(str(card['card_id'])), 'Missing card_id')
    source = card.get('source', {})
    require(isinstance(source.get('url'), str) and source['url'].startswith('https://'), 'Missing source URL')
    require(isinstance(source.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', source['sha256']), 'Invalid source SHA256')
    require(bool(card.get('orientation')), 'Missing orientation')
    totals = replay(card.get('lines'), card.get('notation'))
    lines = {line['line_id']: line['ciphertext'] for line in card['lines']}
    for entry in card.get('uncertainty_ledger', []):
        if 'offset' not in entry or 'selected' not in entry:
            continue
        identifier = entry.get('line_id')
        require(isinstance(identifier, str) and identifier in lines,
                'Current uncertainty ledger has unknown line_id')
        offset, selected = entry['offset'], entry['selected']
        require(type(offset) is int and 0 <= offset <= len(lines[identifier]),
                f'{identifier}: invalid uncertainty offset')
        require(isinstance(selected, str),
                f'{identifier}: invalid uncertainty selected text')
        require(lines[identifier][offset:offset + len(selected)] == selected,
                f'{identifier}: uncertainty selected span mismatch')
    for name in COUNTS:
        if name in card:
            require(card[name] == totals[name], f'Card {name} mismatch')
    return totals


def check_package(directory, *, include_cards=True):
    directory = Path(directory)
    key = json.loads((directory / 'key.json').read_text(encoding='utf-8'))
    require(key.get('notation') == NOTATION and key.get('mapping') == EXPECTED_KEY, 'Frozen key mismatch')
    require(key.get('provenance', {}).get('pdf_sha256') == PDF_SHA256, 'Key PDF provenance mismatch')
    anchor = json.loads((directory / 'anchor204.json').read_text(encoding='utf-8'))
    require(anchor.get('card_id') == '204', 'Anchor card identity mismatch')
    require(anchor.get('provenance', {}).get('pdf_sha256') == PDF_SHA256, 'Anchor PDF provenance mismatch')
    lines = anchor.get('lines', [])
    require([line.get('line_id') for line in lines] == [str(i) for i in range(1, 13)] + ['M1', 'M2'], 'Anchor line IDs mismatch')
    digest = hashlib.sha256(json.dumps(lines, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(digest == ROWS_SHA256, 'Frozen anchor rows mismatch')
    totals = replay(lines, anchor.get('notation'))
    require(totals == {'rows': 14, 'encoded_bodies': 571, 'expanded_letters': 576, 'ch_occurrences': 5, 'unknowns': 0}, 'Anchor totals mismatch')
    cards = {}
    if include_cards:
        catalogue = json.loads((directory / 'catalogue-records.json').read_text(encoding='utf-8'))
        for path in sorted((directory / 'cards').glob('*.json')):
            card = json.loads(path.read_text(encoding='utf-8'))
            identifier = str(card.get('card_id'))
            require(identifier not in cards, f'Duplicate card ID: {identifier}')
            records = [record for record in catalogue['cards']
                       if str(record.get('card_id')) == identifier]
            require(len(records) == 1, f'{identifier}: missing or duplicate catalogue source record')
            source = card.get('source', {})
            face = source.get('face', 'Picture side')
            require(isinstance(face, str) and face in ('Picture side', 'Address side'),
                    f'{identifier}: invalid source face')
            images = [image.get('original_url') for image in records[0].get('image_records', [])
                      if image.get('title') == face]
            require(len(images) == 1 and isinstance(images[0], str) and images[0]
                    and source.get('url') == images[0],
                    f'{identifier}: source URL does not match catalogue {face}')
            cards[identifier] = check_card(card)
    return {'status': 'passed', 'anchor': totals, 'cards': cards}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        report = check_package(args.directory)
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'check failed: {error}\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
