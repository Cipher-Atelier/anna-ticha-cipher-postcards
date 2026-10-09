"""Mutation regressions on temporary copies of the public saved evidence."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ledger_replay import REQUIRED_CARDS, VerificationError, verify_all

REPO = Path(__file__).resolve().parents[2]
CARD318_LITERAL = ('v den prvniho maje srdecny\npozdrav a dlouhou. vrelou pusu\n'
                   'sve touzene, predrahe andulce\nposila vzpominajici pepous.\n')
CARD316_LITERAL = ('jedu prave domu.\nboli mne hlavicka, jeste vice vsak srdecko po tobe,\n'
                   't[y/i] ma cista lilie! nescislne pozdrv[y/i] a pusu [U2]\ndopis co nejdrive,\n')
CARD326_LITERAL = ('srdecny dik za krasny listek, anusko draha! list zaslu v nejblizsich dnech.\n'
                   'vine te v duchu [k/z] sobe a tisic pus ti posila pe pouc.\n'
                   'jak se dari v ka[U1]enici? mas oped drivejsi byt?\n')
B_LITERAL = 'dosel muj l[i/y]sle[UNRESOLVED_CLUSTER] z nedele [QUESTION_LIKE_MARK]\n'
CD_LITERAL = ('C: ma z[C.cluster]ta anusko mam le tak nevys[l/o]ovytelne rad\n'
              'D: tecim se nesmirne na [D.cluster1][D.cluster2]ibeny dopis\n')


class LedgerReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        shutil.copytree(REPO / 'research-updates/evidence', self.repo / 'research-updates/evidence')
        shutil.copytree(REPO / 'verification/anna-ticha/data', self.repo / 'verification/anna-ticha/data')
        (self.repo / 'anna-ticha').mkdir()
        for card in REQUIRED_CARDS:
            shutil.copy2(REPO / f'anna-ticha/card-{card}.md', self.repo / f'anna-ticha/card-{card}.md')

    def package(self, card):
        return self.repo / f'research-updates/evidence/card{card}-2026-10-09'

    def read_manifest(self, card):
        return json.loads((self.package(card) / 'manifest.json').read_text())

    def save_manifest(self, card, manifest):
        (self.package(card) / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def mutate_manifest(self, card, change):
        manifest = self.read_manifest(card)
        change(manifest)
        self.save_manifest(card, manifest)

    def mutate_rows(self, card, change):
        path = self.package(card) / 'word-ledger.csv'
        with path.open(newline='') as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        change(rows)
        with path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        self.mutate_manifest(card, lambda m: m.update(ledger_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))

    def mutate_margin(self, name, change):
        path = self.package(318) / name
        ledger = json.loads(path.read_text())
        change(ledger)
        path.write_text(json.dumps(ledger), encoding='utf-8')
        self.mutate_manifest(318, lambda m: m['margin_sha256'].update({name: hashlib.sha256(path.read_bytes()).hexdigest()}))

    def fails(self, message):
        with self.assertRaisesRegex(VerificationError, message):
            verify_all(self.repo)

    def test_all_saved_packages_and_known_exact_literals(self):
        for card, expected in [(318, CARD318_LITERAL), (316, CARD316_LITERAL), (326, CARD326_LITERAL)]:
            self.assertEqual((self.package(card) / 'literal.txt').read_bytes(), expected.encode('utf-8'))
        self.assertEqual((self.package(318) / 'margin-b-literal.txt').read_text(), B_LITERAL)
        self.assertEqual((self.package(318) / 'margin-cd-literal.txt').read_text(), CD_LITERAL)
        report = verify_all(self.repo)
        self.assertEqual([c['card'] for c in report['cards']], list(REQUIRED_CARDS))
        expected = [(253,253,55,0,1),(193,193,42,0,0),(102,102,24,2,1),(96,96,17,0,0),
                    (150,152,31,0,1),(200,203,40,0,0),(195,196,41,0,0),(166,166,37,0,0),
                    (283,283,54,0,2),(132,135,34,1,1),(266,268,56,1,3),(240,243,53,0,4)]
        self.assertEqual([(c['mapped_bodies'], c['emitted_letters'], c['groups'],
                           c['alternative_bodies'], c['unknown_clusters']) for c in report['cards']], expected)
        self.assertEqual([r['invariant_mapped_bodies'] for r in report['card318_margins']], [19,35,27])

    def test_supported_but_wrong_class_is_not_trusted_csv_literal(self):
        self.mutate_rows(314, lambda rows: rows[0].update(classes=rows[0]['classes'].replace('G01', 'G02')))
        self.fails('card314.*L1W1: row literal/key mapping mismatch')

    def test_row_literal_mismatch(self):
        self.mutate_rows(315, lambda rows: rows[0].update(literal='wrong'))
        self.fails('card315.*L1W1: row literal/key mapping mismatch')

    def test_unknown_class(self):
        self.mutate_rows(314, lambda rows: rows[0].update(classes='G99'))
        self.fails('unknown class or undeclared mask G99')

    def test_aggregate_counters(self):
        for field in ('mapped_bodies', 'emitted_letters', 'observed_classes', 'word_groups',
                      'capped_ch_bodies', 'unknown_clusters', 'alternative_bodies'):
            with self.subTest(field=field):
                manifest = self.read_manifest(320)
                damaged = dict(manifest)
                damaged[field] += 1
                self.save_manifest(320, damaged)
                self.fails(f'aggregate {field} counter mismatch')
                self.save_manifest(320, manifest)

    def test_row_counter(self):
        self.mutate_rows(314, lambda rows: rows[0].update(mapped_bodies='6'))
        self.fails('L1W1: row mapped_bodies counter mismatch')

    def test_ch_is_one_body_but_two_letters(self):
        self.mutate_manifest(320, lambda m: m.update(emitted_letters=200))
        self.fails('aggregate emitted_letters counter mismatch')

    def test_ch_excluded_from_row_bodies_is_rejected(self):
        def change(rows):
            row = next(r for r in rows if 'G10_CAP' in r['classes'])
            row['mapped_bodies'] = str(int(row['mapped_bodies']) - 1)
        self.mutate_rows(320, change)
        self.fails('row mapped_bodies counter mismatch')

    def test_removed_record_even_when_manifest_group_count_updated(self):
        self.mutate_rows(314, lambda rows: rows.pop())
        self.mutate_manifest(314, lambda m: m.update(word_groups=54))
        self.fails('required record count mismatch')

    def test_duplicate_record(self):
        self.mutate_rows(314, lambda rows: rows.__setitem__(1, dict(rows[0])))
        self.fails('duplicate record ID')

    def test_reordered_record(self):
        self.mutate_rows(314, lambda rows: rows.__setitem__(slice(0,2), [rows[1],rows[0]]))
        self.fails('record order/indices mismatch')

    def test_malformed_indices(self):
        self.mutate_rows(314, lambda rows: rows[0].update(line='01'))
        self.fails('line: malformed integer')

    def test_wrong_region(self):
        self.mutate_rows(322, lambda rows: rows[0].update(region='BOTTOM'))
        self.fails('invalid region label')

    def test_missing_required_package(self):
        shutil.rmtree(self.package(328))
        self.fails('Missing required package: card328')

    def test_undeclared_alternative(self):
        self.mutate_rows(316, lambda rows: next(r for r in rows if 'A1' in r['classes']).update(classes='A3'))
        self.fails('undeclared mask A3')

    def test_invalid_alternative_candidate(self):
        self.mutate_manifest(316, lambda m: m['alternatives'][0].update(candidate_classes=['G05','G99']))
        self.fails('unknown alternative candidate')

    def test_wrong_alternative_literal(self):
        self.mutate_manifest(316, lambda m: m['alternatives'][0].update(literal='[i/y]'))
        self.fails('alternative mask mismatch')

    def test_duplicate_alternative_declaration(self):
        self.mutate_manifest(316, lambda m: m['alternatives'].append(dict(m['alternatives'][0])))
        self.fails('malformed/duplicate alternative ID')

    def test_alternative_counted_as_invariant(self):
        self.mutate_rows(316, lambda rows: next(r for r in rows if 'A1' in r['classes']).update(invariant_mapped_bodies='7'))
        self.fails('row invariant_mapped_bodies counter mismatch')

    def test_unknown_id_use_moved_to_wrong_record(self):
        def change(rows):
            row = next(r for r in rows if 'U2' in r['classes'])
            rows[0]['classes'] += ' U2'
            row['classes'] = row['classes'].replace(' U2', '')
        self.mutate_rows(314, change)
        self.fails('unknown ID use mismatch')

    def test_invalid_unknown_id(self):
        self.mutate_manifest(314, lambda m: m['unknowns'][0].update(id='U0'))
        self.fails('malformed/duplicate unknown ID')

    def test_undeclared_unknown_token(self):
        self.mutate_rows(314, lambda rows: next(r for r in rows if 'U2' in r['classes']).update(classes='U99'))
        self.fails('undeclared mask U99')

    def test_unknown_counted_as_body(self):
        self.mutate_manifest(314, lambda m: m['unknowns'][0].update(body_count=1))
        self.fails('unknown has accepted body count')

    def test_unknown_row_mask_counter(self):
        self.mutate_rows(314, lambda rows: next(r for r in rows if 'U2' in r['classes']).update(unknown_clusters='0'))
        self.fails('row unknown_clusters counter mismatch')

    def test_current_and_initial_source_box_bounds(self):
        for field in ('source_bbox_xyxy', 'initial_context_bbox_xyxy'):
            with self.subTest(field=field):
                path = self.package(314) / 'word-ledger.csv'
                original, manifest = path.read_bytes(), self.read_manifest(314)
                self.mutate_rows(314, lambda rows: rows[0].update({field:'[0, 0, 1800, 100]'}))
                self.fails(f'{field}: out-of-bounds box')
                path.write_bytes(original)
                self.save_manifest(314, manifest)

    def test_punctuation_mismatch(self):
        self.mutate_manifest(318, lambda m: m['replay_punctuation'][0].update(literal=','))
        self.fails('assembled saved literal/punctuation mismatch')

    def test_intraword_punctuation_mismatch(self):
        self.mutate_manifest(325, lambda m: m['intraword_punctuation'][0].update(after_class=5))
        self.fails('assembled saved literal/punctuation mismatch')

    def test_literal_mismatch_with_refreshed_fingerprint(self):
        path = self.package(318) / 'literal.txt'
        path.write_text(CARD318_LITERAL.replace('maje', 'maje,'))
        self.mutate_manifest(318, lambda m: m.update(literal_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        self.fails('assembled saved literal/punctuation mismatch')

    def test_diplomatic_article_mismatch(self):
        path = self.repo / 'anna-ticha/card-318.md'
        path.write_text(path.read_text().replace('v den prvniho maje srdecny', 'v den prvniho maje, srdecny'))
        self.fails('diplomatic literal/article mismatch')

    def test_ledger_fingerprint(self):
        path = self.package(314) / 'word-ledger.csv'
        path.write_bytes(path.read_bytes() + b'\n')
        self.fails('card314 ledger: fingerprint mismatch')

    def test_key_and_atlas_fingerprints(self):
        for name in ('key.csv','glyph_atlas.json'):
            with self.subTest(name=name):
                path = self.repo / 'verification/anna-ticha/data' / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                self.fails('unchanged .*: fingerprint mismatch')
                path.write_bytes(original)

    def test_manifest_key_fingerprint(self):
        self.mutate_manifest(314, lambda m: m.update(key_sha256='0'*64))
        self.fails('card314: key fingerprint/path mismatch')

    def test_margin_invariant_counter(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m.update(invariant_mapped_bodies=20))
        self.fails('margin B: invariant counter mismatch')

    def test_margin_unknown_candidate_partition_is_not_accepted(self):
        def change(ledger):
            unit = ledger['strips'][0]['groups'][1]['units'][1]
            unit['accepted_partition'] = unit['candidate_partition']
        self.mutate_margin('margin-cd-ledger.json', change)
        self.fails('margin C.cluster: unresolved record has accepted mapping')

    def test_csv_alternative_cannot_gain_accepted_value(self):
        self.mutate_manifest(316, lambda m: m['alternatives'][0].update(class_id='G05', key_value='y'))
        self.fails('card316 A1: unresolved record has accepted mapping')

    def test_margin_alternative_cannot_gain_accepted_partition(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m['groups'][2]['units'][1].update(
            accepted_partition=['G07'], literal_value='i'))
        self.fails('margin B.G3.U2: unresolved record has accepted mapping')

    def test_margin_alternative_cannot_gain_direct_literal(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m['groups'][2]['units'][1].update(literal='i'))
        self.fails('margin B.G3.U2: alternative mask mismatch')

    def test_margin_unknown_cannot_gain_direct_literal(self):
        self.mutate_margin('margin-cd-ledger.json', lambda m: m['strips'][0]['groups'][1]['units'][1].update(literal='la'))
        self.fails('margin C.cluster: unknown has accepted literal or invalid mask')

    def test_margin_unknown_candidate_cannot_gain_body_count(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m['groups'][2]['units'][-1].update(body_count=1))
        self.fails('unknown has accepted body count')

    def test_margin_unknown_id(self):
        self.mutate_margin('margin-cd-ledger.json', lambda m: m['strips'][1]['groups'][4]['units'][0].update(id='D.other'))
        self.fails('margin D: undeclared unknown ID')

    def test_margin_wrong_alternative(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m['groups'][2]['units'][1].update(candidates=['G07','G99']))
        self.fails('unknown alternative candidate')

    def test_margin_wrong_group_order(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m['groups'].reverse())
        self.fails('margin B: group IDs/order mismatch')

    def test_margin_box_bounds(self):
        self.mutate_margin('margin-cd-ledger.json', lambda m: m['strips'][0]['groups'][0].update(pre_review_context_bbox_xyxy=[1640,1085,1800,1130]))
        self.fails('pre_review_context_bbox_xyxy: out-of-bounds box')

    def test_margin_source_fingerprint(self):
        self.mutate_margin('margin-b-ledger.json', lambda m: m.update(source_sha256='0'*64))
        self.fails('margin: source fingerprint mismatch')

    def test_margin_literal_mismatch_with_refreshed_fingerprint(self):
        path = self.package(318) / 'margin-cd-literal.txt'
        path.write_text(CD_LITERAL.replace('tecim', 'tesim'))
        self.mutate_manifest(318, lambda m: m['margin_sha256'].update({path.name:hashlib.sha256(path.read_bytes()).hexdigest()}))
        self.fails('margin-cd-literal.txt: assembled saved literal mismatch')

    def test_duplicate_json_field_is_rejected(self):
        path = self.package(314) / 'manifest.json'
        text = path.read_text()
        path.write_text('{"word_groups":55,' + text[1:])
        self.fails('Duplicate JSON key: word_groups')


if __name__ == '__main__':
    unittest.main()
