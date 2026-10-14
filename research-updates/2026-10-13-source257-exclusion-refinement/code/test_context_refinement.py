"""Eight bounded synthetic fixtures for scientific claim failure modes.

No corpus images, old tests, network, or class membership are used. Synthetic
evidence is explicitly NOT an assessment of manuscript pixels.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

import check_context_refinement as checker


def fixture():
    ids = checker.IDS + [f'S{i:03}' for i in range(157)]
    records = [{'id':uid, checker.BBOX:[10,10,30,40], 'candidate_eligible':i >= 15 and i < 70,
                'source_adjudication':{'local_mark_locators':[{'native_bbox_xyxy_halfopen':[10,10,15,20]}]}}
               for i,uid in enumerate(ids)]
    baseline = {'records':records, 'unresolved_source_ids':[f'X{i:03}' for i in range(135)]}
    common = {'graphical_grounds':'SYNTHETIC TEST ONLY: continuous branch traced to the complete neighboring contour.', 'source_view_refs':['synthetic-region','synthetic-focus']}
    feature = {'status':'KNOWN', 'description':'SYNTHETIC TEST ONLY: one open contour and two terminals.', 'source_view_refs':common['source_view_refs']}
    cases = []
    for uid in checker.IDS:
        alternatives = []
        for side in ('LEFT','RIGHT'):
            alternatives.append({'old_native_locator':[10,10,15,20], 'new_native_locator':[10,10,15,20], 'side':side,
                                 'physical_component_ref':{'component_id':'synthetic-neighbor','annotation_ids':['S000'],'native_bbox_xyxy_halfopen':[5,5,20,45]},
                                 'relation':'CONTINUOUS_NEIGHBOR', 'connection_regions':[[10,10,15,20]], **common})
        cases.append({'id':uid, checker.BBOX:[10,10,30,40], 'candidate_eligible_before':False,
                      'window_barrier_after':'DISCHARGED', 'old_id_target_identity':'SUPPORTED_SAME_TARGET',
                      'old_id_target_identity_evidence':copy.deepcopy(common), 'observed_target_native_bbox_xyxy_halfopen':[16,10,30,40],
                      'competing_alternatives':alternatives, 'physical_features':{k:copy.deepcopy(feature) for k in checker.FEATURES},
                      'significant_signature':{k:feature['description'] for k in checker.FEATURES},
                      'mark_inventory':[{'native_locator':[10,10,15,20],'old_native_locators':[[10,10,15,20]],'appearance':'synthetic competing branch',
                                         'physical_allocation':'NEIGHBOR_COMPONENT','physical_component_id':'synthetic-neighbor','functional_role':'UNKNOWN',**common}],
                      'alias_check':{'status':'NO_SAME_INSTANCE_ALIAS_OBSERVED_WITH_REFERENCED_NEIGHBORS','checked_annotation_ids':['S000'],**common},
                      'full_feature_eligibility_after':True, 'remaining_blockers':[], 'new_blockers':[], 'source_view_refs':common['source_view_refs'],
                      'reader_disagreements':[], 'graphic_resolution':'SYNTHETIC TEST ONLY: separate complete components traced.',
                      'reader_support':{r:{'window_discharge_supported':True,'eligibility_supported':True,'basis_report_sha256':('c' if r=='A' else 'e')*64,'support_phase':('POST_FEEDBACK_COORDINATE_AUDIT' if r=='A' else 'POST_FEEDBACK_LITERAL_MARK_AUDIT'),**common} for r in ('A','B')},
                      'adjudicator_source_inspection':{'source_native_and_clockwise_verified':True,'complete_target_features_inspected':True,**common},
                      'causal_attribution':{'old_context_native_bbox_xyxy_halfopen':[0,0,50,50],'required_evidence_native_bbox_xyxy_halfopen':[5,5,30,45],
                                           'required_evidence_within_old_context':True,'gain_basis':'INSIDE_OLD_CONTEXT_NEW_COMPONENT_ALLOCATION',**common},
                      'cipher_role':'UNKNOWN','functional_role':'UNKNOWN','letter_value':'UNKNOWN'})
    delta = {'schema':'source257-context-refinement-delta-v1',
             'pins':{'baseline_sha256':checker.BASELINE_SHA,'assessment_protocol_sha256':checker.ASSESSMENT_SHA,
                     'context_index_sha256':checker.CONTEXT_SHA,'reader_A_sha256':'a'*64,'reader_B_sha256':'b'*64,
                     'reader_A_coordinate_addendum_sha256':'c'*64,'reader_B_coordinate_erratum_sha256':'d'*64,'reader_B_literal_mark_addendum_sha256':'e'*64},
             'cases':cases, 'unchanged_scope':{'other_whole_annotation_ids':sorted(ids[15:]),'unresolved_source_ids':baseline['unresolved_source_ids'],
                                             'policy':'BASELINE_UNCHANGED_NO_PATCH_OUTSIDE_COHORT'}, 'class_merge_claims':[],
             'claimed_metrics':{'window_barrier_before':15,'window_barrier_discharged':15,'window_barrier_partial':0,'window_barrier_retained':0,
                                'cases_with_new_blockers':0,'cohort_eligible_before':0,'cohort_eligible_after':15,'eligible_annotation_profiles_after':70,
                                'excluded_annotation_profiles_after':102,'unchanged_other_whole':157,'unchanged_unresolved_placeholders':135}}
    return delta, baseline, {'selected_ids':checker.IDS}


class ContextRefinementFixtures(unittest.TestCase):
    def setUp(self):
        self.delta, self.baseline, self.protocol = fixture()

    def validate(self):
        return checker.validate_delta(self.delta, self.baseline, self.protocol)

    def test_01_discharged_barrier_new_blocker_cannot_promote(self):
        self.assertEqual(self.validate()['cohort_eligible_after'],15)
        self.delta['cases'][0]['new_blockers'] = [{'kind':'LOCAL_SOURCE_DETAIL_UNRESOLVED_BY_THIS_METHOD','description':'Tiny new loop closure cannot be established.',
                                                  'graphical_grounds':'SYNTHETIC TEST ONLY: dark closure junction is locally merged.','source_view_refs':['synthetic-focus']}]
        with self.assertRaisesRegex(checker.ValidationError,'eligibility fails'): self.validate()
        self.delta['cases'][0]['full_feature_eligibility_after'] = False
        self.delta['claimed_metrics'].update(cases_with_new_blockers=1,cohort_eligible_after=14,eligible_annotation_profiles_after=69,excluded_annotation_profiles_after=103)
        result=self.validate(); self.assertEqual((result['window_barrier_discharged'],result['cohort_eligible_after']),(15,14))

    def test_02_omitted_significant_feature(self):
        del self.delta['cases'][0]['physical_features']['terminal_pattern']
        with self.assertRaisesRegex(checker.ValidationError,'physical_features'): self.validate()

    def test_03_uncertain_signature_cannot_admit_common_body(self):
        for description in ('Possible tiny enclosure; closure unresolved.', 'UNRESOLVED_CLOSURE', 'UNKNOWN_COUNTER',
                            'AMBIGUOUS inner space', 'INDETERMINATE return', 'UNESTABLISHED closure'):
            with self.subTest(description=description):
                self.delta,_,_=fixture(); c=self.delta['cases'][0]
                c['physical_features']['enclosures']['description']=description
                c['significant_signature']['enclosures']=description
                with self.assertRaisesRegex(checker.ValidationError,'eligibility fails'): self.validate()

    def test_04_bbox_outside_cohort_duplicate_and_other_scope(self):
        original=copy.deepcopy(self.delta)
        for mutation in ('bbox','float','bool','outside','duplicate','unresolved'):
            with self.subTest(mutation=mutation):
                self.delta=copy.deepcopy(original)
                if mutation=='bbox': self.delta['cases'][0][checker.BBOX][0]=11
                if mutation=='float': self.delta['cases'][0][checker.BBOX][0]=10.0
                if mutation=='bool': self.delta['cases'][0][checker.BBOX][0]=True
                if mutation=='outside': self.delta['cases'][0]['id']='S000'
                if mutation=='duplicate': self.delta['cases'][0]['id']=self.delta['cases'][1]['id']
                if mutation=='unresolved': self.delta['unchanged_scope']['unresolved_source_ids']=[]
                with self.assertRaises(checker.ValidationError): self.validate()

    def test_05_graphical_grounds_and_both_sides_required(self):
        self.delta['cases'][0]['competing_alternatives'][0]['graphical_grounds']=''
        with self.assertRaisesRegex(checker.ValidationError,'graphical_grounds'): self.validate()
        self.delta,_,_=fixture()
        self.delta['cases'][-2]['competing_alternatives']=self.delta['cases'][-2]['competing_alternatives'][:1]
        with self.assertRaisesRegex(checker.ValidationError,'both old sides'): self.validate()

    def test_06_bogus_counts_and_causal_attribution(self):
        self.delta['claimed_metrics']['eligible_annotation_profiles_after']=71
        with self.assertRaisesRegex(checker.ValidationError,'claimed counts'): self.validate()
        self.delta,_,_=fixture()
        self.delta['cases'][0]['causal_attribution']['gain_basis']='EXTENDS_BEYOND_OLD_CONTEXT'
        with self.assertRaisesRegex(checker.ValidationError,'causal gain basis'): self.validate()

    def test_07_output_alias_prewrite_including_hardlink(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory); source=p/'immutable.json'; source.write_text('{"sentinel":"unchanged"}')
            alias=p/'output.json'; os.link(source,alias)
            before=source.read_bytes()
            with self.assertRaisesRegex(checker.ValidationError,'output already exists'):
                checker.run(source,source,source,alias)
            self.assertEqual(source.read_bytes(),before)
            self.assertEqual(alias.read_bytes(),before)

    def test_08_detached_unallocated_mark_and_ambiguous_old_identity(self):
        for mutation in ('mark','identity','alias','reader','provenance','wrong_hash','A_B_phase'):
            with self.subTest(mutation=mutation):
                self.delta,_,_=fixture(); c=self.delta['cases'][0]
                if mutation=='mark': c['mark_inventory'][0]['physical_allocation']='UNRESOLVED'
                if mutation=='identity': c['old_id_target_identity']='UNRESOLVED'
                if mutation=='alias': c['alias_check']['status']='UNRESOLVED'
                if mutation=='reader': c['reader_support']['B']['eligibility_supported']=False
                if mutation=='provenance': c['reader_support']['B']['support_phase']='INITIAL_INDEPENDENT_READING'
                if mutation=='wrong_hash': c['reader_support']['B']['basis_report_sha256']='d'*64
                if mutation=='A_B_phase': c['reader_support']['A']['support_phase']='POST_FEEDBACK_LITERAL_MARK_AUDIT'
                with self.assertRaisesRegex(checker.ValidationError,'provenance|B only|eligibility fails'): self.validate()
        self.delta,_,_=fixture()
        context={'contexts':[{'context_id':'synthetic-region','kind':'region','target_ids':checker.IDS},
                             {'context_id':'synthetic-focus','kind':'focus','target_ids':checker.IDS,
                              'intersecting_annotations':[{'id':'X000'}]}]}
        with self.assertRaisesRegex(checker.ValidationError,'omitted focus-intersecting unresolved'):
            checker.validate_delta(self.delta,self.baseline,self.protocol,context)
        for case in self.delta['cases']: case['alias_check']['checked_annotation_ids'].append('X000')
        self.assertEqual(checker.validate_delta(self.delta,self.baseline,self.protocol,context)['cohort_eligible_after'],15)


if __name__ == '__main__': unittest.main()
