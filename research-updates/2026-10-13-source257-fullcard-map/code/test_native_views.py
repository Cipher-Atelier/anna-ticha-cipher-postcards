import unittest

from PIL import Image

from native_views import coverage, cw_box, exact_rows, inverse_cw_box


class NativeViewsTests(unittest.TestCase):
    def setUp(self):
        self.width, self.height = 7, 5
        self.rgb = bytes(channel for y in range(self.height) for x in range(self.width)
                         for channel in (x * 17, y * 31, x + y * self.width))
        self.image = Image.frombytes("RGB", (self.width, self.height), self.rgb)

    def test_native_exact_crop_rows_and_half_open_edges(self):
        for box in ((0, 0, 1, 1), (6, 4, 7, 5), (1, 2, 6, 5), (0, 0, 7, 5)):
            with self.subTest(box=box):
                self.assertEqual(self.image.crop(box).tobytes(), exact_rows(self.rgb, self.width, box))
                self.assertEqual(len(exact_rows(self.rgb, self.width, box)),
                                 (box[2] - box[0]) * (box[3] - box[1]) * 3)

    def test_cw_corner_boxes_invert_and_match_pixels(self):
        rotated = self.image.transpose(Image.Transpose.ROTATE_270)
        for box in ((0, 0, 1, 1), (6, 0, 7, 1), (0, 4, 1, 5), (6, 4, 7, 5),
                    (1, 1, 6, 4), (0, 0, 7, 5)):
            with self.subTest(box=box):
                mapped = cw_box(box, self.height)
                self.assertEqual(inverse_cw_box(mapped, self.height), box)
                expected = self.image.crop(box).transpose(Image.Transpose.ROTATE_270)
                self.assertEqual(rotated.crop(mapped).size, expected.size)
                self.assertEqual(rotated.crop(mapped).tobytes(), expected.tobytes())
        for y in range(self.height):
            for x in range(self.width):
                self.assertEqual(rotated.getpixel((self.height - 1 - y, x)), self.image.getpixel((x, y)))

    def test_union_coverage_counts_overlap_once_and_detects_gap(self):
        complete = coverage([(0, 0, 3, 2), (2, 0, 5, 2)], (0, 0, 5, 2))
        self.assertEqual(complete["covered_pixels"], 10)
        self.assertTrue(complete["union_equals_target"])
        incomplete = coverage([(0, 0, 2, 2), (3, 0, 5, 2)], (0, 0, 5, 2))
        self.assertEqual(incomplete["uncovered_pixels"], 2)
        self.assertFalse(incomplete["union_equals_target"])


if __name__ == "__main__":
    unittest.main()
