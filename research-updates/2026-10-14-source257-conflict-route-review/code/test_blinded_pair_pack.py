"""New D13 geometry, blinding, native layout and corruption challenge fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont

import build_blinded_pair_pack as core


STAGE = Path(__file__).resolve().parents[1]
D12 = STAGE.parent / "2026-10-14-source257-repeat-sequence"


class BlindedPairPackFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = json.loads((STAGE / "results/judge-source-geometry-intake-v1.json").read_bytes())
        cls.pair_ids = {pair["pair_id"] for pair in cls.intake["pairs"]}
        cls.helper = core.helpers(D12)

    def fixture(self):
        return copy.deepcopy(self.intake)

    def test_exact38_and_29_lookup(self):
        profiles = core.validate_intake(self.intake, self.pair_ids)
        self.assertEqual(len(profiles), 29)
        self.assertEqual(len(self.pair_ids), 38)
        self.assertEqual(sum(len(p["windows"]) for p in profiles.values()), 58)

    def test_missing_duplicate_and_rebound_pair_rejected(self):
        for mutation in ("missing", "duplicate", "rebound"):
            with self.subTest(mutation=mutation):
                intake = self.fixture()
                if mutation == "missing":intake["pairs"].pop()
                elif mutation == "duplicate":intake["pairs"][-1] = copy.deepcopy(intake["pairs"][0])
                else:intake["pairs"][0]["pair_id"] = "UNLISTED--PAIR"
                with self.assertRaises(ValueError):core.validate_intake(intake, self.pair_ids)

    def test_missing_or_duplicate_profile_lookup_rejected(self):
        for mutation in ("missing", "duplicate"):
            with self.subTest(mutation=mutation):
                intake = self.fixture()
                if mutation == "missing":intake["profiles"].pop()
                else:intake["profiles"][-1] = copy.deepcopy(intake["profiles"][0])
                with self.assertRaisesRegex(ValueError, "Exact29"):
                    core.validate_intake(intake, self.pair_ids)

    def test_outcome_feature_and_neighbor_prose_cannot_enter_intake(self):
        for location in ("pair", "profile", "neighbor"):
            with self.subTest(location=location):
                intake = self.fixture()
                if location == "pair":intake["pairs"][0]["historical_outcome"] = "FORBIDDEN_FIXTURE"
                elif location == "profile":intake["profiles"][0]["significant_signature"] = {"FORBIDDEN_FIXTURE": True}
                else:intake["profiles"][0]["windows"]["CONTEXT"]["intersecting_annotations"][0]["ownership_prose"] = "FORBIDDEN_FIXTURE"
                with self.assertRaises(ValueError):core.validate_intake(intake, self.pair_ids)

    def test_right_CW_native_bottom_and_fixed_padding(self):
        seen = set()
        for profile in self.intake["profiles"]:
            expected = 90 if profile["region"].startswith("right-R") else 0
            seen.add(expected)
            self.assertEqual(profile["rotation_degrees_clockwise"], expected)
        self.assertEqual(seen, {0, 90})
        intake = self.fixture();intake["profiles"][0]["rotation_degrees_clockwise"] = -90
        with self.assertRaisesRegex(ValueError, "frame sign"):
            core.validate_intake(intake, self.pair_ids)
        intake = self.fixture();intake["profiles"][0]["windows"]["TIGHT"][core.BOX][0] += 1
        with self.assertRaisesRegex(ValueError, "padding"):
            core.validate_intake(intake, self.pair_ids)

    def sizes(self):
        sizes = {}
        for profile in self.intake["profiles"]:
            for window in profile["windows"].values():
                x0, y0, x1, y1 = window[core.BOX]
                sizes[window["context_id"]] = (y1-y0, x1-x0) if profile["rotation_degrees_clockwise"] else (x1-x0, y1-y0)
        return sizes

    def test_152_panels38_pairs_native_geometry_and_outside_labels(self):
        sizes = self.sizes();boards = core.plan_boards(self.intake, sizes)
        self.assertEqual(len(boards), 10)
        self.assertEqual(sum(len(b["panels"]) for b in boards), 152)
        self.assertEqual([p for board in boards for p in board["pair_ids"]], [p["pair_id"] for p in self.intake["pairs"]])
        for board in boards:
            self.assertLessEqual(len(board["pair_ids"]), 4)
            self.assertLessEqual(board["size"][1], 1800)
            drawing = ImageDraw.Draw(Image.new("RGB", board["size"]))
            for i, panel in enumerate(board["panels"]):
                rect = panel["sheet_panel_xyxy_halfopen"]
                self.assertEqual((rect[2]-rect[0], rect[3]-rect[1]), sizes[panel["context_id"]])
                self.assertEqual(panel["label"], f"{panel['id']} {panel[core.BOX]}")
                bounds = drawing.textbbox(tuple(panel["label_origin"]), panel["label"], font=ImageFont.load_default())
                self.assertFalse(any(core.intersects(bounds, other["sheet_panel_xyxy_halfopen"]) for other in board["panels"]))
                self.assertFalse(any(core.intersects(rect, other["sheet_panel_xyxy_halfopen"]) for other in board["panels"][i+1:]))

    def test_oversize_native_layout_rejected_without_scaling(self):
        sizes = {cid:(width, 500) for cid,(width, _) in self.sizes().items()}
        with self.assertRaisesRegex(ValueError, "maximum height"):
            core.plan_boards(self.intake, sizes)

    def test_exact_native_source_mapping_both_frames_and_corruption(self):
        source = Image.new("RGB", (11, 9))
        source.putdata([(x*19,y*23,(x+7*y)%256) for y in range(9) for x in range(11)])
        for rotation in (0, 90):
            with self.subTest(rotation=rotation):
                context = {core.BOX:[2,1,9,5], "rotation_degrees_clockwise":rotation}
                correct = self.helper.expected_crop(source, context)
                self.assertEqual(correct.getpixel((0,0)), source.getpixel((2,4 if rotation else 1)))
                rows = core.verify_source_panel(source, correct, context, self.helper)
                self.assertEqual([row["native_y"] for row in rows], [1,2,3,4])
                corrupt = correct.copy();corrupt.putpixel((1,2),(255,255,255))
                with self.assertRaisesRegex(ValueError, "differs from original"):
                    core.verify_source_panel(source, corrupt, context, self.helper)

    def test_failed_method_gate_blocks_before_source_decoding(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            gate_path = temporary / "synthetic-failed-gate.json"
            raw = core.encoded({"status":"FAIL", "source_protocol_sha256":core.PROTOCOL_SHA,
                                "source_reader_view_canonical_sha256":core.READER_PROTOCOL_CANONICAL_SHA})
            gate_path.write_bytes(raw)
            with patch.object(core.Image, "open") as decode:
                with self.assertRaisesRegex(ValueError, "Method PASS required"):
                    core.build(D12, temporary / "unavailable-original.JPG",
                               STAGE / "results/judge-source-geometry-intake-v1.json",
                               STAGE / "results/conflict-route-protocol-v1.json", gate_path,
                               core.sha(raw), STAGE / "results/pack-immutability-before-private-v1.json",
                               temporary / "never-created-pack")
                decode.assert_not_called()
            self.assertFalse((temporary / "never-created-pack").exists())


if __name__ == "__main__":
    unittest.main()
