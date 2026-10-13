import copy,unittest
from native_annotation_diagnostics_v3 import diagnose_native
class Tests(unittest.TestCase):
    def fixture(self):
        u={'id':'U1','local_order':1,'native_bbox_xyxy_halfopen':[170,815,190,850],'bbox_precision_native_pixels':{},'geometric_features':'curve','physical_extent_status':'VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION','single_cipher_unit_identity':'UNKNOWN','owned_parts':'body','detached_mark_ownership':{'chosen':None},'exemplar_role':'POSITIVE_WHOLE_GEOMETRY_SINGLETON','equivalence_class':'S1','repeated_class_validation':False,'evidence_views':['raw.png'],'separator_evidence':{}}
        return {'units':[u],'classes':[{'id':'S1','members':['U1'],'role':'singleton'}],'scope':'first band partial','correlated_partition_and_mark_owner_alternatives':{},'unallocated_marks':[],'source_quality':[]}
    def test_unknown_role_permitted(self):
        d=diagnose_native(self.fixture());self.assertTrue(d['typed_structure_valid']);self.assertEqual(d['positive_whole_singleton_exemplars'],1)
    def test_geometry_failures(self):
        for box in ([190,815,170,850],[170,815,1786,850],[170,815,190,1176]):
            f=self.fixture();f['units'][0]['native_bbox_xyxy_halfopen']=box;self.assertFalse(diagnose_native(f)['typed_structure_valid'])
    def test_duplicate_and_missing_reference(self):
        f=self.fixture();f['units'].append(copy.deepcopy(f['units'][0]));self.assertFalse(diagnose_native(f)['typed_structure_valid'])
        f=self.fixture();f['units'][0]['equivalence_class']='absent';self.assertFalse(diagnose_native(f)['typed_structure_valid'])
    def test_numeric_class_members_returns_errors(self):
        f=self.fixture();f['classes'][0]['members']=5
        d=diagnose_native(f)
        self.assertFalse(d['typed_structure_valid'])
        self.assertTrue(any(e['field']=='classes[0].members' for e in d['errors']))
    def test_repeated_class_count_is_distinct_classes(self):
        f=self.fixture();second=copy.deepcopy(f['units'][0]);second['id']='U2';second['local_order']=2
        f['units'].append(second);f['classes'][0]['members']=['U1','U2']
        for u in f['units']:u['repeated_class_validation']=True
        d=diagnose_native(f)
        self.assertTrue(d['typed_structure_valid'])
        self.assertEqual(d['validated_repeated_equivalence_classes'],1)
if __name__=='__main__':unittest.main()
