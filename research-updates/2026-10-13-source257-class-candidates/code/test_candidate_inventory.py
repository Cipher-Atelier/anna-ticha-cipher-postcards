"""Synthetic structural adversaries: these tests make no source judgments."""
import copy
import csv
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from check_candidate_inventory import (InventoryError, PAIR_FIELDS, SIGNATURE_FIELDS,
                                       WHOLE, check_files, sha256, validate_inventory,
                                       validate_pair_screen)


class CandidateInventoryTests(unittest.TestCase):
    def setUp(self):
        self.base = {'frozen_first_band': {'units': [self.unit('U001'),self.unit('U002')]},
                     'new_units': [self.unit('FC001'),self.unit('FC136',False)],
                     'frozen_overlay_conflicts':[{'frozen_ids':['U002']}]}
        self.sig = dict.fromkeys(SIGNATURE_FIELDS, 'visible definite feature')
        self.inv = {'base_map_sha256':'fixture-hash', 'records':[self.record('U001'),self.record('U002',False),self.record('FC001')],
                    'candidate_classes':[self.group(['U001','FC001'])], 'eligible_singleton_ids':[],
                    'excluded_whole_ids':['U002'], 'unresolved_source_ids':['FC136'],
                    'source_limits':['FC136 physical-cut span remains unresolved; no extension.']}

    def unit(self, uid, whole=True):
        return {'id':uid, 'native_bbox_xyxy_halfopen':[1,2,3,4],
                'physical_extent_status':WHOLE if whole else 'UNRESOLVED_PHYSICAL_EXTENT'}

    def record(self, uid, eligible=True):
        return {'id':uid, 'base_native_bbox_xyxy_halfopen':[1,2,3,4],
                'source_target_status':'SUPPORTED_WHOLE_TARGET', 'significant_signature':copy.deepcopy(self.sig),
                'mark_ownership_status':'CONTINUOUS_ATTACHED_PARTS_ONLY', 'candidate_eligible':eligible,
                'exclusion_reasons':[] if eligible else ['Frozen overlay conflict.'], 'evidence_views':['native-context'],
                'cipher_role':'UNKNOWN','letter_value':'UNKNOWN'}

    def group(self, members, cid='SCG001'):
        return {'id':cid,'member_ids':members,'significant_signature':copy.deepcopy(self.sig),
                'merge_grounds':['Exact full visible-feature correspondence.'], 'excluded_lookalikes':[],
                'source_evidence_views':['native-context-pairs'], 'status':'FULL_VISIBLE_FEATURE_CANDIDATE',
                'cipher_identity':'UNESTABLISHED','letter_value':'UNKNOWN'}

    def validate(self, inv=None, base=None):
        return validate_inventory(inv or self.inv, base or self.base, base_hash='fixture-hash', expected_whole=3, expected_unresolved=1)

    def rejects(self, fn):
        with self.assertRaises(InventoryError):
            fn()

    def test_eligible_physical_unknown_cipher_role_accepted(self):
        before=copy.deepcopy(self.base)
        result=self.validate()
        self.assertEqual((result['eligible_count'],result['grouped_whole_count'],result['excluded_whole_count']), (2,2,1))
        self.assertEqual(self.base,before)

    def test_same_body_different_attached_bar_or_owned_profile_rejected(self):
        for field in ('attached_bars','owned_mark_profile','connected_extra_strokes','terminal_pattern'):
            with self.subTest(field=field):
                inv=copy.deepcopy(self.inv)
                inv['records'][2]['significant_signature'][field]='Different visible attached feature'
                self.rejects(lambda:self.validate(inv))

    def test_unknown_ownership_and_uncertain_target_block_eligibility(self):
        for field,value in [('mark_ownership_status','UNRESOLVED'),('mark_ownership_status','BACKGROUND_CONFUNDED'),('source_target_status','UNCERTAIN_TARGET')]:
            with self.subTest(field=field,value=value):
                inv=copy.deepcopy(self.inv); inv['records'][0][field]=value
                self.rejects(lambda:self.validate(inv))

    def test_frozen_conflict_cannot_become_eligible_even_with_resolved_signature(self):
        inv=copy.deepcopy(self.inv)
        inv['records'][1]['candidate_eligible']=True
        inv['records'][1]['exclusion_reasons']=[]
        inv['excluded_whole_ids']=[]; inv['eligible_singleton_ids']=['U002']
        self.rejects(lambda:self.validate(inv))

    def test_unresolved_source_id_never_grouped_and_preserved_exactly(self):
        for mutate in (lambda i:i['candidate_classes'][0]['member_ids'].append('FC136'),
                       lambda i:i.update(unresolved_source_ids=[]),
                       lambda i:i['unresolved_source_ids'].append('FC136'),
                       lambda i:i['eligible_singleton_ids'].append('FC136'),
                       lambda i:i['records'].append(self.record('FC136'))):
            inv=copy.deepcopy(self.inv); mutate(inv)
            self.rejects(lambda:self.validate(inv))

    def test_exact_whole_record_and_partition_coverage(self):
        changes=[lambda i:i['records'].pop(), lambda i:i['records'].append(copy.deepcopy(i['records'][0])),
                 lambda i:i['excluded_whole_ids'].clear(), lambda i:i['eligible_singleton_ids'].append('U001'),
                 lambda i:i['candidate_classes'].clear(), lambda i:i['excluded_whole_ids'].append('U002')]
        for mutate in changes:
            inv=copy.deepcopy(self.inv); mutate(inv)
            self.rejects(lambda:self.validate(inv))
        inv=copy.deepcopy(self.inv);inv['candidate_classes']=[];inv['eligible_singleton_ids']=['U001','FC001']
        self.assertEqual(self.validate(inv)['eligible_singleton_count'],2)

    def test_exact_bbox_and_base_reference_reject_without_mutating_base(self):
        before=copy.deepcopy(self.base)
        for box in ([1,2,3,5],[True,2,3,4],[1.0,2,3,4]):
            inv=copy.deepcopy(self.inv);inv['records'][0]['base_native_bbox_xyxy_halfopen']=box
            self.rejects(lambda:self.validate(inv))
        inv=copy.deepcopy(self.inv);inv['base_map_sha256']='another-base'
        self.rejects(lambda:self.validate(inv))
        self.assertEqual(self.base,before)

    def test_unknown_feature_is_not_eligible_and_signature_fields_are_exact(self):
        for value in ('UNKNOWN','ambiguous enclosed area','UNESTABLISHED','UNRESOLVED',
                      'uncertain attached feature','INDETERMINATE',''):
            inv=copy.deepcopy(self.inv);inv['records'][0]['significant_signature']['enclosures']=value
            self.rejects(lambda:self.validate(inv))
        inv=copy.deepcopy(self.inv);inv['records'][0]['significant_signature']['extra']='legacy'
        self.rejects(lambda:self.validate(inv))
        # Deferred records can retain unresolved feature observations, with reasons.
        inv=copy.deepcopy(self.inv);inv['records'][1]['significant_signature']['enclosures']='UNKNOWN'
        self.assertEqual(self.validate(inv)['excluded_whole_count'],1)

    def test_no_cipher_or_letter_assignments_on_records_or_classes(self):
        for container,field,value in [('records','cipher_role','ALPHABETIC'),('records','letter_value','A'),
                                      ('candidate_classes','cipher_identity','ESTABLISHED'),('candidate_classes','letter_value','A')]:
            inv=copy.deepcopy(self.inv);inv[container][0][field]=value
            self.rejects(lambda:self.validate(inv))

    def test_no_transitive_close_grouping_or_duplicate_classes_or_members(self):
        base=copy.deepcopy(self.base);base['new_units'].append(self.unit('FC002'))
        inv=copy.deepcopy(self.inv);inv['records'].append(self.record('FC002'))
        inv['records'][-1]['significant_signature']['openings']='Close but different opening'
        inv['candidate_classes'][0]['member_ids'].append('FC002')
        self.rejects(lambda:validate_inventory(inv,base,base_hash='fixture-hash',expected_whole=4,expected_unresolved=1))
        for change in (lambda i:i['candidate_classes'].append(copy.deepcopy(i['candidate_classes'][0])),
                       lambda i:i['candidate_classes'].append(self.group(['U001','FC001'],'SCG002')),
                       lambda i:i['candidate_classes'][0].update(member_ids=['U001']),
                       lambda i:i['candidate_classes'][0].update(member_ids=['U001','U001']),
                       lambda i:i['candidate_classes'][0].update(merge_grounds=[]),
                       lambda i:i['candidate_classes'][0].update(source_evidence_views=[])):
            inv=copy.deepcopy(self.inv);change(inv)
            self.rejects(lambda:self.validate(inv))

    def write_pairs(self,path,pairs):
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=PAIR_FIELDS);w.writeheader()
            for a,b in pairs:
                w.writerow(dict(zip(PAIR_FIELDS,(a,b,'SOURCE_COMPARISON_DEFERRED','Requires comparison','context-reference'))))

    def test_pair_total_duplicate_reverse_missing_and_foreign_ids(self):
        ids={'U001','U002','FC001'};allpairs=list(itertools.combinations(sorted(ids),2))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pairs.csv'
            self.write_pairs(path,[(b,a) for a,b in allpairs])
            self.assertEqual(validate_pair_screen(path,ids)['pair_screen_count'],3)
            for pairs in (allpairs[:-1],allpairs+[(allpairs[0][1],allpairs[0][0])],allpairs+[('U001','FC136')],allpairs+[('U001','U001')]):
                self.write_pairs(path,pairs)
                self.rejects(lambda:validate_pair_screen(path,ids))

    def write_declared_pairs(self, path, rows):
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=PAIR_FIELDS);w.writeheader()
            for a,b,outcome in rows:
                w.writerow(dict(zip(PAIR_FIELDS,(a,b,outcome,'Recorded source comparison grounds','native-context-reference'))))

    def test_pair_internal_declared_class_requires_same_and_blocks_excluded_pairs(self):
        ids={'U001','U002','FC001'}
        rows=[('U001','FC001','CLASS_CANDIDATE_SAME'),
              ('U002','FC001','ELIGIBILITY_BLOCKED'),('U001','U002','ELIGIBILITY_BLOCKED')]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pairs.csv'
            self.write_declared_pairs(path,rows)
            self.assertTrue(validate_pair_screen(path,ids,inventory=self.inv)['pair_screen_inventory_outcomes_checked'])
            for outcome in ('SOURCE_COMPARISON_DEFERRED','STRUCTURAL_DIFFERENCE','ELIGIBILITY_BLOCKED'):
                changed=copy.deepcopy(rows);changed[0]=('U001','FC001',outcome)
                self.write_declared_pairs(path,changed)
                self.rejects(lambda:validate_pair_screen(path,ids,inventory=self.inv))
            for outcome in ('CLASS_CANDIDATE_SAME','SOURCE_COMPARISON_DEFERRED','STRUCTURAL_DIFFERENCE'):
                changed=copy.deepcopy(rows);changed[1]=('U002','FC001',outcome)
                self.write_declared_pairs(path,changed)
                self.rejects(lambda:validate_pair_screen(path,ids,inventory=self.inv))

    def test_pair_positive_claim_for_unresolved_owner_rejected(self):
        inv=copy.deepcopy(self.inv)
        inv['records'][0].update(candidate_eligible=False,mark_ownership_status='UNRESOLVED',exclusion_reasons=['Detached-mark ownership unresolved.'])
        inv.update(candidate_classes=[],eligible_singleton_ids=['FC001'],excluded_whole_ids=['U001','U002'])
        self.validate(inv)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pairs.csv'
            self.write_declared_pairs(path,[('U001','FC001','CLASS_CANDIDATE_SAME'),('U002','FC001','ELIGIBILITY_BLOCKED'),('U001','U002','ELIGIBILITY_BLOCKED')])
            self.rejects(lambda:validate_pair_screen(path,{'U001','U002','FC001'},inventory=inv))

    def test_pair_different_bar_requires_difference_equal_signature_not_auto_same(self):
        inv=copy.deepcopy(self.inv)
        inv.update(candidate_classes=[],eligible_singleton_ids=['U001','FC001'])
        inv['records'][2]['significant_signature']['attached_bars']='Additional continuous attached bar'
        self.validate(inv)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pairs.csv'
            for outcome in ('CLASS_CANDIDATE_SAME','SOURCE_COMPARISON_DEFERRED','ELIGIBILITY_BLOCKED','STRUCTURAL_DIFFERENCE'):
                rows=[('U001','FC001',outcome),('U002','FC001','ELIGIBILITY_BLOCKED'),('U001','U002','ELIGIBILITY_BLOCKED')]
                self.write_declared_pairs(path,rows)
                if outcome=='STRUCTURAL_DIFFERENCE':
                    self.assertEqual(validate_pair_screen(path,{'U001','U002','FC001'},inventory=inv)['pair_screen_count'],3)
                else:
                    self.rejects(lambda:validate_pair_screen(path,{'U001','U002','FC001'},inventory=inv))
            inv['records'][2]['significant_signature']=copy.deepcopy(inv['records'][0]['significant_signature'])
            self.validate(inv)
            for outcome in ('CLASS_CANDIDATE_SAME','ELIGIBILITY_BLOCKED','SOURCE_COMPARISON_DEFERRED','STRUCTURAL_DIFFERENCE'):
                self.write_declared_pairs(path,[('U001','FC001',outcome),('U002','FC001','ELIGIBILITY_BLOCKED'),('U001','U002','ELIGIBILITY_BLOCKED')])
                if outcome in ('SOURCE_COMPARISON_DEFERRED','STRUCTURAL_DIFFERENCE'):
                    self.assertEqual(validate_pair_screen(path,{'U001','U002','FC001'},inventory=inv)['pair_screen_count'],3)
                else:
                    self.rejects(lambda:validate_pair_screen(path,{'U001','U002','FC001'},inventory=inv))

    def test_file_entrypoint_always_crosschecks_pair_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);basepath=root/'base.json';invpath=root/'inventory.json';pairs=root/'pairs.csv';out=root/'out.json'
            basepath.write_text(json.dumps(self.base));basehash=sha256(basepath.read_bytes())
            inv=copy.deepcopy(self.inv);inv['base_map_sha256']=basehash;invpath.write_text(json.dumps(inv))
            kwargs={'expected_base':basehash,'expected_whole':3,'expected_unresolved':1,'pair_screen':pairs}
            self.write_pairs(pairs,list(itertools.combinations(sorted({'U001','U002','FC001'}),2)))
            self.rejects(lambda:check_files(invpath,basepath,out,**kwargs))
            self.assertFalse(out.exists())
            self.write_declared_pairs(pairs,[('U001','FC001','CLASS_CANDIDATE_SAME'),('U002','FC001','ELIGIBILITY_BLOCKED'),('U001','U002','ELIGIBILITY_BLOCKED')])
            result=check_files(invpath,basepath,out,**kwargs)
            self.assertEqual(result['status'],'PASS')
            self.assertTrue(result['pair_screen_inventory_outcomes_checked'])

    def test_file_hash_reject_output_guard_and_inputs_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);basepath=root/'base.json';invpath=root/'inventory.json';out=root/'out.json'
            basepath.write_text(json.dumps(self.base));basehash=sha256(basepath.read_bytes())
            inv=copy.deepcopy(self.inv);inv['base_map_sha256']=basehash;invpath.write_text(json.dumps(inv))
            originals=(basepath.read_bytes(),invpath.read_bytes())
            kwargs={'expected_base':basehash,'expected_whole':3,'expected_unresolved':1}
            result=check_files(invpath,basepath,out,**kwargs)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual((basepath.read_bytes(),invpath.read_bytes()),originals)
            self.rejects(lambda:check_files(invpath,basepath,invpath,**kwargs))
            self.rejects(lambda:check_files(invpath,basepath,basepath,**kwargs))
            alias=root/'alias';alias.symlink_to(basepath)
            self.rejects(lambda:check_files(invpath,basepath,alias,**kwargs))
            kwargs['expected_base']='0'*64
            self.rejects(lambda:check_files(invpath,basepath,root/'absent/out.json',**kwargs))
            self.assertFalse((root/'absent').exists())
            self.assertEqual((basepath.read_bytes(),invpath.read_bytes()),originals)


if __name__=='__main__':
    unittest.main()
