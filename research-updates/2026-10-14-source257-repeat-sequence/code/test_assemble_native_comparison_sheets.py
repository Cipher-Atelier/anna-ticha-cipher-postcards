"""Synthetic fixtures for the new integer mapping and native sheet layout."""
import unittest

from PIL import Image, ImageDraw, ImageFont

from assemble_native_comparison_sheets import BOX, expected_crop, intersects, layout, source_row_proof


class NativeSheetFixtures(unittest.TestCase):
    def test_asymmetric_crop_both_frames_and_corruption(self):
        source = Image.new("RGB", (11, 9))
        source.putdata([(x * 19, y * 23, (x + 7 * y) % 256) for y in range(9) for x in range(11)])
        for rotation in (0, 90):
            context = {BOX: [2, 1, 9, 5], "rotation_degrees_clockwise": rotation}
            rendered = expected_crop(source, context)
            rows = source_row_proof(source, rendered, context)
            self.assertEqual([row["native_y"] for row in rows], [1, 2, 3, 4])
            damaged = rendered.copy()
            damaged.putpixel((1, 2), (255, 255, 255))
            with self.assertRaisesRegex(ValueError, "differs"):
                source_row_proof(source, damaged, context)
            with self.assertRaisesRegex(ValueError, "dimensions"):
                source_row_proof(source, Image.new("RGB", (1, 1)), context)

    def test_mixed_native_panels_and_labels_do_not_overlap(self):
        contexts, sizes = [], {}
        for unit in range(5):
            for kind in ("TIGHT", "CONTEXT"):
                uid = f"U{unit:03d}"
                cid = f"c-{len(contexts)}"
                contexts.append({"context_id": cid, "target_ids": [uid], "focus_id": uid + "-" + kind,
                                 BOX: [100, 200, 140, 260], "rotation_degrees_clockwise": 0,
                                 "private_png": cid + ".png"})
                sizes[cid] = ((41 + unit, 30 + unit) if kind == "TIGHT" else (205 + unit, 240 - unit))
        size, panels = layout(contexts, sizes)
        self.assertLessEqual(size[1], 1800)
        self.assertEqual(len(panels), 10)
        drawing = ImageDraw.Draw(Image.new("RGB", size))
        for panel in panels:
            rect = panel["sheet_panel_xyxy_halfopen"]
            self.assertEqual((rect[2] - rect[0], rect[3] - rect[1]), sizes[panel["context_id"]])
            text = f"{panel['target_id']} {panel['window_kind']} {panel[BOX]}"
            bounds = drawing.textbbox(tuple(panel["label_origin"]), text, font=ImageFont.load_default())
            self.assertFalse(any(intersects(bounds, other["sheet_panel_xyxy_halfopen"]) for other in panels))
            self.assertFalse(any(intersects(rect, other["sheet_panel_xyxy_halfopen"]) for other in panels if other is not panel))
        oversized = {cid: (width, 400) for cid, (width, _) in sizes.items()}
        with self.assertRaisesRegex(ValueError, "maximum height"):
            layout(contexts, oversized)
        with self.assertRaisesRegex(ValueError, "five"):
            layout(contexts[:8], sizes)


if __name__ == "__main__":
    unittest.main()
