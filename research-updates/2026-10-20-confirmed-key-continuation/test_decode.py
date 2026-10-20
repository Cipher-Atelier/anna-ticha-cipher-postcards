"""Offline regression tests for the frozen confirmed-key experiment."""
import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class ConfirmedKeyTests(unittest.TestCase):
    def decoder(self):
        self.assertTrue((ROOT / 'decode.py').exists(), 'strict decoder is not implemented')
        return importlib.import_module('decode')

    def checker(self):
        self.assertTrue((ROOT / 'check.py').exists(), 'package checker is not implemented')
        return importlib.import_module('check')

    def test_ch_and_canonical_q_g_are_distinct(self):
        result = self.decoder().decode_text('qg ř,\n14!', notation='pdf204-canonical')
        self.assertEqual(result['literal'], 'KZ CH,\nYI!')
        self.assertEqual((result['encoded_bodies'], result['expanded_letters'], result['ch_occurrences']), (5, 6, 1))

    def test_unsupported_notation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'notation'):
            self.decoder().decode_text('g9', notation='legacy460')

    def test_unknowns_are_preserved_with_positions(self):
        result = self.decoder().decode_text('g 9?X.', notation='pdf204-canonical')
        self.assertEqual(result['literal'], 'Z 9?X.')
        self.assertEqual(result['unknowns'], [
            {'offset': 2, 'body_index': 1, 'symbol': '9', 'kind': 'unknown_symbol'},
            {'offset': 3, 'body_index': 2, 'symbol': '?', 'kind': 'unknown_glyph'},
            {'offset': 4, 'body_index': 3, 'symbol': 'X', 'kind': 'unknown_symbol'},
        ])

    def test_numeral_metadata_excludes_plain_number_from_cipher(self):
        result = self.decoder().decode_text('14 ř', notation='pdf204-canonical', transcription=[
            {'offset': 0, 'text': '14', 'kind': 'numeral'}])
        self.assertEqual(result['literal'], '14 CH')
        self.assertEqual(result['encoded_bodies'], 1)
        self.assertEqual(result['unknowns'], [{'offset': 0, 'body_index': None, 'symbol': '14', 'kind': 'numeral'}])

    def test_explicit_question_mark_is_punctuation(self):
        result = self.decoder().decode_text('q? ?', notation='pdf204-canonical', transcription=[
            {'offset': 1, 'text': '?', 'kind': 'punctuation'}])
        self.assertEqual(result['literal'], 'K? ?')
        self.assertEqual(result['encoded_bodies'], 2)
        self.assertEqual(result['unknowns'], [
            {'offset': 3, 'body_index': 1, 'symbol': '?', 'kind': 'unknown_glyph'}])
        with self.assertRaises(ValueError):
            self.decoder().decode_text('q', notation='pdf204-canonical', transcription=[
                {'offset': 0, 'text': 'q', 'kind': 'punctuation'}])

    def test_bad_metadata_rejected(self):
        for metadata in ([{'offset': 0, 'text': '2', 'kind': 'numeral'}],
                         [{'offset': 0, 'text': '1', 'kind': 'guess'}],
                         [{'offset': 0, 'text': '14', 'kind': 'numeral'}, {'offset': 1, 'text': '4', 'kind': 'numeral'}]):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                self.decoder().decode_text('14', notation='pdf204-canonical', transcription=metadata)

    def test_frozen_anchor_and_counts(self):
        result = self.checker().check_package(ROOT, include_cards=False)
        self.assertEqual(result['anchor'], {'rows': 14, 'encoded_bodies': 571, 'expanded_letters': 576, 'ch_occurrences': 5, 'unknowns': 0})

    def test_checker_rejects_coherently_changed_anchor(self):
        self.decoder()
        check = self.checker()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ('key.json', 'anchor204.json'):
                (target / name).write_bytes((ROOT / name).read_bytes())
            data = json.loads((target / 'anchor204.json').read_text())
            data['lines'][0]['ciphertext'] = 'q'
            data['lines'][0]['literal'] = 'K'
            (target / 'anchor204.json').write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                check.check_package(target, include_cards=False)

    def test_card_unknown_ledger_and_source_validation(self):
        check = self.checker()
        card = {'card_id': 'test', 'notation': 'pdf204-canonical',
                'source': {'url': 'https://example.org/source.JPG', 'sha256': 'a' * 64},
                'orientation': '90 degrees CCW', 'lines': [
                    {'line_id': '1', 'ciphertext': 'q?', 'literal': 'K?', 'unknowns': [
                        {'offset': 1, 'body_index': 1, 'symbol': '?', 'kind': 'unknown_glyph'}]}]}
        self.assertEqual(check.check_card(card)['encoded_bodies'], 2)
        for field, value in [('literal', 'KK'), ('unknowns', [])]:
            bad = copy.deepcopy(card)
            bad['lines'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                check.check_card(bad)
        bad = copy.deepcopy(card)
        bad['source']['sha256'] = 'missing'
        with self.assertRaises(ValueError):
            check.check_card(bad)

    def test_cli_requires_explicit_notation(self):
        self.decoder()
        result = subprocess.run([sys.executable, str(ROOT / 'decode.py'), 'qg'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        result = subprocess.run([sys.executable, str(ROOT / 'decode.py'), '--notation', 'pdf204-canonical', 'qgř'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['literal'], 'KZCH')


if __name__ == '__main__':
    unittest.main()
