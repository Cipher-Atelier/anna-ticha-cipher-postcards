"""Small synthetic pixel fixtures verify geometry, privacy, immutability, rejection."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from build_feature_context_pack import (WHOLE, build, context_box, native_crop,
                                        rows_from_source, select_records, sha256)


class NativeContextTests(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (9, 7))
        self.image.putdata([(x*23, y*31, (x+y)*11) for y in range(7) for x in range(9)])

    def test_halfopen_rows_are_exact_interior_and_edge(self):
        for box in ([2, 1, 6, 4], [8, 6, 9, 7], [0, 0, 9, 7]):
            c = native_crop(self.image, box, False)
            expected = [self.image.getpixel((x,y)) for y in range(box[1],box[3]) for x in range(box[0],box[2])]
            self.assertEqual(list(c.getdata()), expected)
            self.assertEqual(c.tobytes(), rows_from_source(self.image, box))
            self.assertEqual(c.size, (box[2]-box[0],box[3]-box[1]))

    def test_context_padding_and_source_only_clipping(self):
        self.assertEqual(context_box([40, 50, 60, 70], (200, 200), True), [16, 34, 84, 86])
        self.assertEqual(context_box([40, 50, 60, 70], (200, 200), False), [24, 26, 76, 94])
        self.assertEqual(context_box([2, 3, 8, 6], (9, 7), True), [0, 0, 9, 7])
        self.assertEqual(context_box([2, 3, 8, 6], (9, 7), False), [0, 0, 9, 7])

    def test_right_clockwise_coordinates_and_inverse(self):
        box = [2, 1, 7, 4]
        c = native_crop(self.image, box, True)
        self.assertEqual(c.size, (3, 5))
        for y in range(3):
            for x in range(5):
                self.assertEqual(c.getpixel((2-y,x)), self.image.getpixel((x+2,y+1)))
        self.assertEqual(c.transpose(Image.Transpose.ROTATE_90).tobytes(), rows_from_source(self.image, box))

    def fixture(self, root):
        source, basepath = root/'source.png', root/'base.json'
        self.image.save(source)
        ref = {'file_sha256': sha256(source.read_bytes()), 'size': [9,7], 'rgb_sha256': sha256(self.image.tobytes())}
        frozen = {'id':'U001', 'native_bbox_xyxy_halfopen':[0,0,2,3], 'physical_extent_status':WHOLE,
                  'equivalence_class':'FORBIDDEN_LEGACY', 'raw_refs':['FORBIDDEN_RAW'], 'detached_mark_ownership':{'assigned':[]}}
        right = {'id':'FC001', 'native_bbox_xyxy_halfopen':[6,3,9,7], 'physical_extent_status':WHOLE, 'region':'right-R7-date-like'}
        bottom = {'id':'FC002', 'native_bbox_xyxy_halfopen':[2,3,5,6], 'physical_extent_status':WHOLE, 'region':'bottom-B2'}
        unresolved = {'id':'FC003', 'native_bbox_xyxy_halfopen':[0,0,9,7], 'physical_extent_status':'UNRESOLVED'}
        base = {'source':ref, 'frozen_first_band':{'units':[frozen], 'file_reference':'FORBIDDEN_REFERENCE'},
                'new_units':[right,bottom,unresolved], 'frozen_overlay_conflicts':[{'frozen_ids':['U001']}]}
        basepath.write_text(json.dumps(base))
        kwargs = {'expected_source':ref['file_sha256'], 'expected_base':sha256(basepath.read_bytes()),
                  'expected_rgb':ref['rgb_sha256'], 'expected_size':(9,7), 'enforce_inventory':False}
        return source, basepath, base, kwargs

    def test_build_roundtrip_private_proofs_public_allowlist_and_immutable_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, basepath, base, kwargs = self.fixture(root)
            original_source, original_base, original_object = source.read_bytes(), basepath.read_bytes(), copy.deepcopy(base)
            selected = select_records(base, self.image.size, kwargs['expected_source'], kwargs['expected_base'])
            self.assertEqual(base, original_object)
            result = build(source, basepath, root/'out', **kwargs)
            self.assertEqual((result['whole_count'],result['png_count'],result['right_clockwise_count'],result['conflict_count']), (3,6,1,1))
            self.assertEqual(source.read_bytes(), original_source)
            self.assertEqual(basepath.read_bytes(), original_base)
            public_bytes = (root/'out/results/context-index-v1.json').read_bytes()
            self.assertNotIn(b'FORBIDDEN', public_bytes)
            public = json.loads(public_bytes)
            self.assertEqual(public['records'], selected)
            allowed = {'id','native_base_bbox_xyxy_halfopen','native_context_bbox_xyxy_halfopen','rotation_clockwise_degrees','envelope_size','context_size','source_sha256','base_map_sha256','frozen_overlay_conflict'}
            self.assertTrue(all(set(r)==allowed for r in public['records']))
            for record in result['records']:
                for entry in record['images']:
                    path = root/'out'/entry['private_path']
                    self.assertEqual(sha256(path.read_bytes()), entry['png_sha256'])
                    with Image.open(path) as saved:
                        self.assertEqual(sha256(saved.tobytes()), entry['rgb_sha256'])
            self.assertEqual(len(list((root/'out/private-pixels').glob('*.png'))), 6)

    def test_hash_rejects_before_any_output_writes(self):
        for mismatch in ('expected_source','expected_base','expected_rgb'):
            with self.subTest(mismatch=mismatch), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                source, basepath, _, kwargs = self.fixture(root)
                kwargs[mismatch]='0'*64
                with self.assertRaises(ValueError):
                    build(source, basepath, root/'absent', **kwargs)
                self.assertFalse((root/'absent').exists())

    def test_invalid_bounds_and_inventory_reject_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source, basepath, base, kwargs = self.fixture(root)
            for bounds in ([0,0,10,7], [2,2,2,3], [-1,0,2,3], [0,0,1.5,3]):
                base['frozen_first_band']['units'][0]['native_bbox_xyxy_halfopen']=bounds
                basepath.write_text(json.dumps(base))
                kwargs['expected_base']=sha256(basepath.read_bytes())
                with self.assertRaises(ValueError):
                    build(source, basepath, root/'absent', **kwargs)
                self.assertFalse((root/'absent').exists())
            _, _, _, kwargs = self.fixture(root)
            kwargs['enforce_inventory']=True
            with self.assertRaises(ValueError):
                build(source, basepath, root/'absent', **kwargs)
            self.assertFalse((root/'absent').exists())


if __name__ == '__main__':
    unittest.main()
