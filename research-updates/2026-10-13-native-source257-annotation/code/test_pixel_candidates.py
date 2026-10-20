import unittest
from PIL import Image
from pixel_candidates import components, relations
class Tests(unittest.TestCase):
    def test_diagonal_detached_offsets(self):
        im=Image.new('L',(4,3),255);im.putpixel((0,0),0);im.putpixel((1,1),0);im.putpixel((3,2),0)
        cs,p=components(im,65,(170,815))
        self.assertEqual([c['area'] for c in cs],[2,1]);self.assertEqual(cs[0]['native_bbox_xyxy_halfopen'],[170,815,172,817]);self.assertEqual(cs[1]['native_bbox_xyxy_halfopen'],[173,817,174,818]);self.assertEqual(p,[1,1,0,1])
    def test_threshold_merge_and_boundary(self):
        im=Image.new('L',(3,1));im.putdata([65,85,65])
        a,_=components(im,65);b,_=components(im,85)
        self.assertEqual(len(a),2);self.assertEqual(len(b),1);self.assertEqual([e['relation'] for e in relations(a,b)],['merge','merge']);self.assertEqual([e['relation'] for e in relations(b,a)],['split','split'])
    def test_exact_crop_slice(self):
        im=Image.new('RGB',(5,4));im.putdata([(n,n+1,n+2) for n in range(20)])
        raw=im.tobytes();expected=b''.join(raw[(y*5+1)*3:(y*5+4)*3] for y in range(1,3))
        self.assertEqual(im.crop((1,1,4,3)).tobytes(),expected)
if __name__=='__main__':unittest.main()
