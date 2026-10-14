"""New native64 scope, frame, pixel-corruption and release-gate fixtures."""
import copy
import json
from pathlib import Path
import unittest

from PIL import Image, ImageDraw, ImageFont
import build_direct64_native_pack as core

STAGE = Path(__file__).resolve().parents[1]


class Native64Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = json.loads((STAGE / "results/judge-source-geometry-intake-v1.json").read_bytes())
        cls.protocol = json.loads((STAGE / "results/direct772-protocol-v2.json").read_bytes())
        cls.gate = json.loads((STAGE / "results/method-protocol-gate-private-v1.json").read_bytes())
        cls.safe = json.loads((STAGE / "results/source-observation-protocol-v1.json").read_bytes())
        cls.helper = core.helper(STAGE.parent / "2026-10-14-source257-repeat-sequence")

    def planned(self, intake=None):
        intake = intake or self.intake
        sizes = {}
        for row in intake["profiles"]:
            for w in row["windows"].values():
                x0,y0,x1,y1 = w[core.BOX]
                sizes[w["context_id"]] = (y1-y0,x1-x0) if row["rotation_degrees_clockwise"] else (x1-x0,y1-y0)
        return core.plan(intake, sizes)

    def test_exact64_16_256_72_compact_scope(self):
        boards = self.planned(); panels = [p for b in boards for p in b["panels"]]
        self.assertEqual((len(boards),len(panels),len({p["context_id"] for p in panels})),(16,256,72))
        self.assertEqual([p for b in boards for p in b["pair_ids"]], [p["pair_id"] for p in self.intake["pairs"]])
        self.assertEqual(len({p["panel_id"] for p in panels}),256)
        self.assertTrue(all("intersecting_annotations" not in p for p in panels))

    def test_native_labels_outside_every_panel(self):
        font = ImageFont.load_default()
        for board in self.planned():
            self.assertLessEqual(board["size"][1],1800)
            draw = ImageDraw.Draw(Image.new("RGB",board["size"]))
            for p in board["panels"]:
                bound = draw.textbbox(p["label_origin"],p["label"],font=font)
                self.assertTrue(all(not self.helper.intersects(bound,q["sheet_panel_xyxy_halfopen"]) for q in board["panels"]))

    def test_wrong64_scope_rejected(self):
        intake = copy.deepcopy(self.intake);intake["pairs"].pop()
        with self.assertRaisesRegex(ValueError,"64/36"):
            self.planned(intake)

    def test_wrong_clockwise_sign_rejected(self):
        intake = copy.deepcopy(self.intake);intake["profiles"][0]["rotation_degrees_clockwise"] = -90
        with self.assertRaisesRegex(ValueError,"Frame sign"):
            self.planned(intake)

    def source(self):
        img = Image.new("RGB",(7,6));img.putdata([(x*20,y*30,(x+y)*13) for y in range(6) for x in range(7)])
        return img

    def test_both_native_frames_integer_row_proof(self):
        source = self.source()
        for rotation in (0,90):
            context = {core.BOX:[1,1,6,5],"rotation_degrees_clockwise":rotation}
            crop = self.helper.expected_crop(source,context)
            rows = core.verify_panel(source,crop,context,self.helper)
            self.assertEqual(len(rows),4)
            self.assertEqual([r["native_y"] for r in rows],[1,2,3,4])

    def test_corrupt_saved_native_pixel_rejected(self):
        source = self.source();context = {core.BOX:[1,1,6,5],"rotation_degrees_clockwise":90}
        crop = self.helper.expected_crop(source,context);crop.putpixel((0,0),(255,0,255))
        with self.assertRaisesRegex(ValueError,"Native source crop"):
            core.verify_panel(source,crop,context,self.helper)

    def test_actual_pinned_method_pass(self):
        core.gate_check(self.protocol,self.gate,self.safe)
        self.assertEqual(core.sha((STAGE/"results/direct772-protocol-v2.json").read_bytes()),core.PROTOCOL_SHA)
        self.assertEqual(core.sha((STAGE/"results/method-protocol-gate-private-v1.json").read_bytes()),core.GATE_SHA)

    def test_nonpass_or_rebound_gate_rejected(self):
        for changes in ({"status":"BLOCK"},{"source_protocol_sha256":"0"*64},{"safe_view_sha256":"0"*64}):
            gate = {**self.gate,**changes}
            with self.assertRaises(ValueError):
                core.gate_check(self.protocol,gate,self.safe)


if __name__ == "__main__":
    unittest.main()
