"""Strict, offline substitution in the explicitly declared PDF204 notation."""
import argparse
import json
from pathlib import Path
import unicodedata

NOTATION = 'pdf204-canonical'
KEY = json.loads(Path(__file__).with_name('key.json').read_text(encoding='utf-8'))['mapping']


def decode_text(ciphertext, *, notation, transcription=None):
    """Offsets are zero-based Unicode codepoints; body indices are zero-based.

    Explicit numeral and punctuation spans are retained and excluded from body totals.
    Unresolved glyph spans count as one body. No legacy normalization is applied.
    The ledger also records preserved numeral spans to make their treatment explicit.
    """
    if notation != NOTATION:
        raise ValueError(f'Unsupported notation: {notation!r}')
    if not isinstance(ciphertext, str):
        raise ValueError('ciphertext must be text')
    spans = {}
    occupied = set()
    for item in transcription or []:
        offset, text, kind = item.get('offset'), item.get('text'), item.get('kind')
        if (type(offset) is not int or offset < 0 or not isinstance(text, str) or not text
                or ciphertext[offset:offset + len(text)] != text
                or kind not in ('numeral', 'unknown_glyph', 'punctuation')
                or (kind == 'numeral' and not text.isdecimal())
                or (kind == 'punctuation' and not all(unicodedata.category(c).startswith('P') for c in text))):
            raise ValueError(f'Invalid transcription metadata: {item!r}')
        positions = set(range(offset, offset + len(text)))
        if occupied & positions:
            raise ValueError('Overlapping transcription metadata')
        occupied.update(positions)
        spans[offset] = item
    output, ledger = [], []
    bodies = letters = ch = offset = 0
    while offset < len(ciphertext):
        symbol = ciphertext[offset]
        if offset in spans:
            item = spans[offset]
            symbol, kind = item['text'], item['kind']
            if kind != 'punctuation':
                ledger.append({'offset': offset, 'body_index': None if kind == 'numeral' else bodies,
                               'symbol': symbol, 'kind': kind})
            bodies += kind == 'unknown_glyph'
            output.append(symbol)
            offset += len(symbol)
            continue
        if symbol in KEY:
            value = KEY[symbol]
            output.append(value)
            bodies += 1
            letters += len(value)
            ch += value == 'CH'
        elif symbol != '?' and (symbol.isspace() or unicodedata.category(symbol).startswith('P')):
            output.append(symbol)
        else:
            ledger.append({'offset': offset, 'body_index': bodies, 'symbol': symbol,
                           'kind': 'unknown_glyph' if symbol == '?' else 'unknown_symbol'})
            output.append(symbol)
            bodies += 1
        offset += 1
    return {'literal': ''.join(output), 'encoded_bodies': bodies, 'expanded_letters': letters,
            'ch_occurrences': ch, 'unknowns': ledger}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notation', required=True, choices=[NOTATION])
    parser.add_argument('ciphertext')
    args = parser.parse_args()
    print(json.dumps(decode_text(args.ciphertext, notation=args.notation), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
