"""Small explicit fixtures for the experimental source-first card330 adapter."""
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from card330_replay import PICTURE, PACKAGE, verify_card330, validate_graphical_snapshot
from ledger_replay import VerificationError, load_key

REPO = Path(__file__).resolve().parents[2]


def fixture():
    """Handwritten expected data; no production decoder generates test expectations."""
    sequences = [['G01','G02','G03','G04','G05'], ['G10_CAP','A001','GA008'], ['U001']]
    groups = []
    for word, sequence in enumerate(sequences, 1):
        ident = f'L01W{word:02}'
        groups.append({'group_id':ident, 'line':1, 'spatial_group':word,
                       'bbox_xyxy':[word*100,800,word*100+90,900], 'class_sequence':sequence,
                       'bodies':[{'body_id':f'{ident}B{i:02}', 'class_id':token,
                                  'bbox_xyxy':[word*100,800,word*100+90,900]}
                                 for i, token in enumerate(sequence,1)]})
    return {'schema':'card330.class-first-ledger.v1', 'source':dict(PICTURE),
            'coverage':[{'line':1,'groups':3,'bbox_xyxy':[100,800,390,900]}], 'groups':groups,
            'unknown_alternatives':{
                'A001':{'candidate_classes':['G19'],'reason':'Unproven rounded/pointed family equality.'},
                'A008':{'candidate_classes':['G18','H440_N01_UNBARRED_LEFT_BOWL'],'reason':'Bar ownership unresolved.'},
                'U001':{'candidate_classes':['G20','G01'],'body_count_interval':[1,2],'reason':'Unsegmented cluster.'}},
            'punctuation':[{'id':'P01','line':1,'after_spatial_group':1,'features':'comma',
                            'bbox_xyxy':[180,850,190,870]}]}


class Card330GraphicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = load_key(REPO)

    def setUp(self):
        self.snapshot = fixture()
        self.aliases = {'GA008':'A008'}

    def replay(self):
        return validate_graphical_snapshot(self.snapshot, self.key, self.aliases)

    def fails(self, message):
        with self.assertRaisesRegex(VerificationError, message):
            self.replay()

    def test_known_words_masks_and_ch_accounting(self):
        result = self.replay()
        self.assertEqual([g['literal'] for g in result['groups']], ['vrely','ch[A001][A008]','[U001]'])
        self.assertEqual(result['counts'], {'groups':3,'encoded_slots':9,'invariant_mapped_bodies':6,
                         'emitted_invariant_letters':7,'unresolved_slot_occurrences':3,'capped_ch_bodies':1,
                         'unresolved_families':3,'observed_invariant_classes':6,'whole_body_count':None})
        self.assertEqual(self.snapshot, fixture(), 'Replay must not edit the immutable input.')

    def test_alias_is_required_not_guessed(self):
        self.aliases = {}
        self.fails('unknown class/undeclared family GA008')

    def test_alias_cannot_promote_family_to_key(self):
        self.aliases = {'GA008':'G18'}
        self.fails('unsupported identifier erratum')

    def test_duplicate_group(self):
        self.snapshot['groups'][1]['group_id'] = 'L01W01'
        self.fails('duplicate group ID')

    def test_reordered_groups(self):
        self.snapshot['groups'].reverse()
        self.fails('group IDs/order mismatch')

    def test_missing_group(self):
        self.snapshot['groups'].pop()
        self.fails('required group count mismatch')

    def test_duplicate_slot(self):
        self.snapshot['groups'][0]['bodies'][1]['body_id'] = 'L01W01B01'
        self.fails('duplicate slot ID')

    def test_sequence_disagrees_with_slot(self):
        self.snapshot['groups'][0]['bodies'][0]['class_id'] = 'G02'
        self.fails('slot ID/class sequence mismatch')

    def test_unknown_family(self):
        group = self.snapshot['groups'][2]
        group['class_sequence'][0] = group['bodies'][0]['class_id'] = 'U099'
        self.fails('unknown class/undeclared family U099')

    def test_invalid_candidate(self):
        self.snapshot['unknown_alternatives']['A001']['candidate_classes'] = ['G99']
        self.fails('invalid candidate classes')

    def test_family_cannot_accept_single_candidate(self):
        self.snapshot['unknown_alternatives']['A001']['accepted_class_id'] = 'G19'
        self.fails('unresolved record has accepted mapping')

    def test_family_cannot_accept_literal(self):
        self.snapshot['unknown_alternatives']['A001']['literal'] = 'c'
        self.fails('unresolved family has accepted literal')

    def test_family_cannot_accept_body_count(self):
        self.snapshot['unknown_alternatives']['U001']['body_count'] = 1
        self.fails('unresolved family has accepted body count')

    def test_group_slot_and_punctuation_bounds(self):
        targets = [self.snapshot['groups'][0], self.snapshot['groups'][0]['bodies'][0], self.snapshot['punctuation'][0]]
        for target in targets:
            with self.subTest(target=target):
                old = target['bbox_xyxy']
                target['bbox_xyxy'] = [0,800,1800,900]
                self.fails('out-of-bounds box')
                target['bbox_xyxy'] = old

    def test_punctuation_id_and_position(self):
        self.snapshot['punctuation'][0]['after_spatial_group'] = 4
        self.fails('invalid punctuation position/features')

    def test_wrong_source_fingerprint(self):
        self.snapshot['source']['sha256'] = '0'*64
        self.fails('source fingerprint/dimensions mismatch')



KNOWN_LITERAL = (
    'vrely dik, srde[R_L01W03B05]ko moje, za drahy listek. proc litujes, ze [A001]en\n'
    'tvuj nebyl pravdou[?] vzdy[R_L02W04B05] mam te toli[R_L02W07B05] rad[!] pra ve se chystam na zpate[A001]ni\n'
    'cestu do prahy. prijel jsem sem na pozi hod v n[R_L03W11_COUPLED_SPAN]i. vzpo mi nal jsem zd[A007] [R_L03W17B01][A008]a[-]\n'
    'le na svoji tak drahou amumku. tesim se na psanko nes mirne. vrely\n'
    'p[A002]zdrav a tisic dlouhych, va[A001]nivych p[A003]s od vecne [U001]veho pepouse.\n')


class Card330PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        shutil.copytree(REPO / PACKAGE, self.repo / PACKAGE)
        shutil.copytree(REPO / 'verification/anna-ticha/data', self.repo / 'verification/anna-ticha/data')
        (self.repo / 'anna-ticha').mkdir()
        shutil.copy2(REPO / 'anna-ticha/card-330.md', self.repo / 'anna-ticha/card-330.md')
        self.package = self.repo / PACKAGE

    def manifest(self):
        return json.loads((self.package / 'manifest.json').read_text())

    def write_manifest(self, manifest):
        (self.package / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def refresh(self, name):
        manifest = self.manifest()
        manifest['files_sha256'][name] = hashlib.sha256((self.package / name).read_bytes()).hexdigest()
        self.write_manifest(manifest)

    def journal(self, change):
        path = self.package / 'reconciliation-v3.json'
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value), encoding='utf-8')
        self.refresh(path.name)

    def csv(self, change):
        path = self.package / 'word-ledger.csv'
        with path.open(newline='') as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        change(rows)
        with path.open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fields,lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        self.refresh(path.name)

    def fails(self, message):
        with self.assertRaisesRegex(VerificationError,message):
            verify_card330(self.repo)

    def test_real_package_and_fixed_expected_projection(self):
        self.assertEqual((self.package/'literal.txt').read_bytes(), KNOWN_LITERAL.encode('utf-8'))
        result = verify_card330(self.repo)
        self.assertEqual(result['counts'],{'groups':65,'lines':5,'encoded_slots':264,
                         'provisionally_mapped_slots':251,'emitted_known_letters':254,
                         'unresolved_slot_occurrences':13,'unresolved_families':11,
                         'observed_known_classes':23,'capped_ch_slots':3,'physical_body_count':None})
        self.assertIsNone(result['accepted_date'])
        self.assertIsNone(result['accepted_postal_date'])

    def test_missing_package(self):
        shutil.rmtree(self.package)
        self.fails('Missing required experimental package: card330')

    def test_missing_group_with_reduced_aggregate(self):
        def change(journal):
            journal['groups'].pop()
            journal['coverage']['reviewed_groups'] = 64
        self.journal(change)
        self.fails('required final group count mismatch')

    def test_duplicate_and_reordered_group(self):
        self.journal(lambda j: j['groups'].__setitem__(1,j['groups'][0]))
        self.fails('duplicate final group ID')

    def test_reordered_groups(self):
        self.journal(lambda j: j['groups'].reverse())
        self.fails('final group IDs/order mismatch')

    def test_supported_wrong_class_cannot_trust_saved_literal(self):
        def change(journal):
            group = journal['groups'][0]
            group['proposed_class_sequence'][0] = 'G02'
            group['body_reviews'][0]['proposed_class'] = 'G02'
        self.journal(change)
        self.fails('L01W01: journal literal/key mapping mismatch')

    def test_journal_literal_mismatch(self):
        self.journal(lambda j: j['groups'][0].update(proposed_literal='wrong'))
        self.fails('journal literal/key mapping mismatch')

    def test_unknown_and_supported_historical_b_substitutions(self):
        path = self.package/'reconciliation-v3.json'
        original = path.read_bytes()
        for token in ('G99','G02'):
            with self.subTest(token=token):
                def change(journal):
                    journal['groups'][0]['B_sequence'][0] = token
                    journal['groups'][0]['body_reviews'][0]['B_class'] = token
                self.journal(change)
                self.fails('historical B projection mismatch')
                path.write_bytes(original)
                self.refresh(path.name)

    def test_invalid_historical_b_correspondence(self):
        self.journal(lambda j: j['groups'][0].update(B_correspondence=['L01.G99']))
        self.fails('invalid historical B correspondence')

    def test_csv_overflow_and_missing_cells(self):
        path = self.package/'word-ledger.csv'
        original = path.read_text()
        for overflow in (True,False):
            with self.subTest(overflow=overflow):
                lines = original.splitlines()
                lines[1] = lines[1]+',unvalidated' if overflow else lines[1].rsplit(',',1)[0]
                path.write_text('\n'.join(lines)+'\n')
                self.refresh(path.name)
                self.fails('malformed CSV row width/missing cell')
        path.write_text(original)
        self.refresh(path.name)

    def test_csv_literal_mismatch(self):
        self.csv(lambda rows: rows[0].update(literal='wrong'))
        self.fails('L01W01: CSV literal mismatch')

    def test_csv_row_counter_mismatch(self):
        self.csv(lambda rows: rows[0].update(provisionally_mapped_slots='6'))
        self.fails('CSV provisionally_mapped_slots mismatch')

    def test_ch_body_vs_letters(self):
        def change(rows):
            row = next(r for r in rows if 'G10_CAP' in r['class_sequence'])
            row['provisionally_mapped_slots'] = row['emitted_known_letters']
        self.csv(change)
        self.fails('CSV provisionally_mapped_slots mismatch')

    def test_manifest_aggregate_mismatch(self):
        manifest = self.manifest()
        manifest['counts']['emitted_known_letters'] = 251
        self.write_manifest(manifest)
        self.fails('manifest aggregate counters mismatch')

    def test_journal_counter_mismatch(self):
        self.journal(lambda j: j['coverage'].update(proposed_encoded_slots=265))
        self.fails('journal coverage counters mismatch')

    def test_slot_review_missing(self):
        self.journal(lambda j: j['groups'][0]['body_reviews'].pop())
        self.fails('missing historical slot review')

    def test_non_coupled_final_slot_index_mapping(self):
        self.journal(lambda j: j['groups'][0]['body_reviews'][0].update(final_encoded_slot_index=2))
        self.fails('final slot index mapping mismatch')

    def test_optional_nonbody_window_bounds(self):
        self.journal(lambda j: j['nonbody_marks'][0].update(source_window_xyxy=[0,0,1800,100]))
        self.fails('out-of-bounds window source_window_xyxy')

    def test_undeclared_mask(self):
        def change(journal):
            group = journal['groups'][0]
            group['proposed_class_sequence'][0] = 'U999'
            group['body_reviews'][0]['proposed_class'] = 'U999'
        self.journal(change)
        self.fails('undeclared final mask/class')

    def test_invalid_candidate(self):
        self.journal(lambda j: j['unresolved_declarations']['A001'].update(candidate_classes=['G99']))
        self.fails('invalid candidate classes')

    def test_unknown_cannot_gain_accepted_mapping(self):
        self.journal(lambda j: j['unresolved_declarations']['A001'].update(accepted_class_id='G19'))
        self.fails('unresolved record has accepted mapping')

    def test_unknown_cannot_gain_direct_literal(self):
        self.journal(lambda j: j['unresolved_declarations']['A001'].update(literal='c'))
        self.fails('unresolved declaration has accepted literal/class')

    def test_unknown_cannot_gain_body_count(self):
        self.journal(lambda j: j['unresolved_declarations']['A007'].update(physical_body_count=1))
        self.fails('unresolved declaration has accepted body count')

    def test_group_physical_count_remains_unknown(self):
        self.journal(lambda j: j['groups'][0].update(physical_body_count=5))
        self.fails('physical body count must remain unestablished')

    def test_coupled_candidates_cannot_gain_cartesian_combinations(self):
        def change(journal):
            sequences = [['G19','H440_N01_UNBARRED_LEFT_BOWL'],['G11','G19'],['G19','G19']]
            journal['unresolved_declarations']['R_L03W11_COUPLED_SPAN']['candidate_sequences'] = sequences
            group = next(g for g in journal['groups'] if g['group_id']=='L03W11')
            group['span_review']['candidate_sequences'] = sequences
        self.journal(change)
        self.fails('candidate correlation mismatch')

    def test_coupled_component_cannot_be_final_class(self):
        def change(journal):
            group = next(g for g in journal['groups'] if g['group_id']=='L03W11')
            group['body_reviews'][1]['proposed_class'] = 'G19'
        self.journal(change)
        self.fails('component promoted to independent final class')

    def test_coupled_slot_index_mapping(self):
        def change(journal):
            group = next(g for g in journal['groups'] if g['group_id']=='L03W11')
            group['body_reviews'][1]['final_encoded_slot_index'] = 1
        self.journal(change)
        self.fails('historical-to-final slot mapping mismatch')

    def test_missing_group_slot_punctuation_and_span_windows(self):
        cases = [('group',lambda j: j['groups'][0], 'source_group_window_xyxy'),
                 ('slot',lambda j: j['groups'][0]['body_reviews'][0], 'source_window_xyxy'),
                 ('punctuation',lambda j: j['punctuation'][0], 'bbox_xyxy'),
                 ('span',lambda j: j['unresolved_declarations']['R_L03W11_COUPLED_SPAN'],'source_window_xyxy')]
        path = self.package/'reconciliation-v3.json'
        original = path.read_bytes()
        for label, target, field in cases:
            with self.subTest(label=label):
                self.journal(lambda j: target(j).pop(field))
                self.fails('missing required window '+field)
                path.write_bytes(original)
                self.refresh(path.name)

    def test_out_of_bounds_final_window(self):
        self.journal(lambda j: j['groups'][0]['body_reviews'][0].update(source_window_xyxy=[0,0,1800,100]))
        self.fails('out-of-bounds window source_window_xyxy')

    def test_punctuation_mutation(self):
        self.journal(lambda j: j['punctuation'][0].update(features='point'))
        self.fails('assembled saved literal/punctuation mismatch')

    def test_literal_mutation_with_refreshed_hash(self):
        path = self.package/'literal.txt'
        path.write_text(KNOWN_LITERAL.replace('amumku','andulku'),encoding='utf-8')
        self.refresh(path.name)
        self.fails('assembled saved literal/punctuation mismatch')

    def test_article_diplomatic_mutation(self):
        path = self.repo/'anna-ticha/card-330.md'
        path.write_text(path.read_text().replace('amumku','andulku'),encoding='utf-8')
        self.fails('diplomatic literal/article mismatch')

    def test_manifest_cannot_accept_date(self):
        manifest = self.manifest()
        manifest['accepted_date'] = '1903-04-14'
        self.write_manifest(manifest)
        self.fails('manifest date must remain unresolved')

    def test_journal_cannot_eliminate_date_alternative(self):
        self.journal(lambda j: j['date'].update(picture_candidates=['14.IV.1903.']))
        self.fails('date alternatives/uncertainty changed')

    def test_finite_experiment_cannot_gain_success(self):
        self.journal(lambda j: j['finite_followup_experiment'].update(result='Assigned G03'))
        self.fails('finite experiment cannot accept A003 mapping')

    def test_refreshed_fingerprint_cannot_modify_frozen_snapshot(self):
        path = self.package/'phase-a-ledger.json'
        value = json.loads(path.read_text())
        value['groups'][0]['bodies'][0]['class_id'] = 'G02'
        path.write_text(json.dumps(value),encoding='utf-8')
        self.refresh(path.name)
        self.fails('immutable snapshot fingerprint mismatch')

    def test_missing_fingerprint_inventory_entry(self):
        manifest = self.manifest()
        del manifest['files_sha256']['phase-a-ledger.json']
        self.write_manifest(manifest)
        self.fails('required fingerprint inventory mismatch')

    def test_unrequested_source_is_not_needed(self):
        self.assertNotIn('explicit_source_identity',verify_card330(self.repo))


if __name__ == '__main__':
    unittest.main()
