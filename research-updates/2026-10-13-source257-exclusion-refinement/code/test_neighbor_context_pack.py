"""Seven synthetic boundary/immutability fixtures; never open corpus pixels."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from build_neighbor_context_pack import BBOX_KEY, PackError, PROTOCOL_SCHEMA, build_pack


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


class NativeContextFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "synthetic.png"
        self.base = self.root / "map.json"
        self.inventory = self.root / "inventory.json"
        self.protocol = self.root / "protocol.json"
        self.output = self.root / "new-pack"
        self.pixels = Image.new("RGB", (17, 13))
        self.pixels.putdata([((x * 17 + y) % 256, (x + y * 19) % 256, (x * 7 + y * 11) % 256)
                             for y in range(13) for x in range(17)])
        self.pixels.save(self.source)
        self.map = {"source": {"file_sha256": sha(self.source.read_bytes()), "size": [17, 13],
                               "rgb_sha256": sha(self.pixels.tobytes())},
                    "frozen_first_band": {"units": [{"id": "U1", BBOX_KEY: [0, 10, 2, 12]}]},
                    "new_units": [
                        {"id": "A", "region": "right-R1", BBOX_KEY: [10, 2, 12, 5]},
                        {"id": "B", "region": "right-R1", BBOX_KEY: [9, 8, 11, 11],
                         "physical_extent_status": "UNRESOLVED_SPAN"},
                        {"id": "C", "region": "right-R2", BBOX_KEY: [13, 3, 16, 6]},
                        {"id": "D", "region": "bottom-B2", BBOX_KEY: [3, 9, 6, 11]},
                        {"id": "E", "region": "bottom-B2", BBOX_KEY: [7, 10, 9, 12]}]}
        write_json(self.base, self.map)
        write_json(self.inventory, {"base_map_sha256": sha(self.base.read_bytes()),
                                   "records": [{"id": uid} for uid in ["U1", "A", "C", "D", "E"]],
                                   "eligible_singleton_ids": [], "excluded_whole_ids": [],
                                   "unresolved_source_ids": ["B"],
                                   "candidate_classes": {"unused": "DO_NOT_COPY_INTO_CONTEXT"}})
        self.request = {"schema": PROTOCOL_SCHEMA,
                        "pins": {"source_sha256": sha(self.source.read_bytes()),
                                 "source_rgb_sha256": sha(self.pixels.tobytes()), "source_size": [17, 13],
                                 "base_sha256": sha(self.base.read_bytes()),
                                 "inventory_sha256": sha(self.inventory.read_bytes())},
                        "selected_ids": ["A"], "trajectory_padding": {"cross_axis": 1, "along_axis": 2},
                        "focus": {"enabled": False}}

    def run_pack(self, request=None, output=None, **kwargs):
        write_json(self.protocol, request or self.request)
        return build_pack(self.source, self.base, self.inventory, self.protocol, output or self.output, **kwargs)

    def test_full_region_union_includes_unresolved_and_neighbors_are_not_owners(self):
        index = self.run_pack()
        region = index["contexts"][0]
        self.assertEqual(region[BBOX_KEY], [8, 0, 13, 13])
        self.assertEqual(region["same_region_annotation_ids"], ["A", "B"])
        self.assertEqual(region["target_ids"], ["A"])
        self.assertEqual({u["id"] for u in region["intersecting_annotations"]}, {"A", "B", "E"})
        # C starts exactly at the half-open crop boundary and must be excluded.
        self.assertEqual(region["intersection_relation"], "geometric_intersection_only_not_an_ownership_claim")
        public = (self.output / "context-index.json").read_text()
        self.assertNotIn("DO_NOT_COPY_INTO_CONTEXT", public)
        self.assertNotIn("png_sha256", public)
        self.assertNotIn("rgb_sha256", public)
        self.assertNotIn("source_rows", public)
        self.assertEqual(index["annotation_unit_count"], 6)
        self.assertFalse(index["annotations_are_tokens"])

    def test_exact_clockwise_pixels_inverse_and_private_source_rows(self):
        index = self.run_pack()
        entry = index["contexts"][0]
        with Image.open(self.output / entry["private_png"]) as rendered:
            self.assertEqual(rendered.size, (13, 5))
            for y in range(rendered.height):
                for x in range(rendered.width):
                    self.assertEqual(rendered.getpixel((x, y)), self.pixels.getpixel((8 + y, 12 - x)))
        proof = json.loads((self.output / "private/pixel-proof.json").read_text())["contexts"][0]
        self.assertTrue(proof["inverse_verified_exact_rgb"])
        self.assertEqual(proof["png_sha256"], sha((self.output / entry["private_png"]).read_bytes()))
        self.assertEqual(len(proof["source_rows"]), 13)
        for row in proof["source_rows"]:
            source_row = self.pixels.crop((8, row["native_y"], 13, row["native_y"] + 1))
            self.assertEqual(row["rgb_sha256"], sha(source_row.tobytes()))

    def test_bottom_and_frozen_padding_axes_clipping_and_unrotated_pixels(self):
        request = copy.deepcopy(self.request)
        request["selected_ids"] = ["U1", "D"]
        index = self.run_pack(request)
        regions = {c["region"]: c for c in index["contexts"]}
        self.assertEqual(regions["frozen-first-band"][BBOX_KEY], [0, 9, 4, 13])
        self.assertEqual(regions["bottom-B2"][BBOX_KEY], [1, 8, 11, 13])
        self.assertEqual(len(regions), 2)
        for entry in regions.values():
            self.assertEqual(entry["rotation_degrees_clockwise"], 0)
            with Image.open(self.output / entry["private_png"]) as actual:
                self.assertEqual(actual.tobytes(), self.pixels.crop(entry[BBOX_KEY]).tobytes())

    def test_focus_defaults_explicit_windows_and_rotation_frames(self):
        request = copy.deepcopy(self.request)
        request.pop("focus")
        index = self.run_pack(request)
        focus = next(c for c in index["contexts"] if c["kind"] == "focus")
        self.assertEqual(focus[BBOX_KEY], [0, 0, 17, 13])
        self.assertEqual(focus["rotation_degrees_clockwise"], 90)
        request["selected_ids"] = ["A", "D"]
        request["focus"] = {"windows": [{"id": "mixed", "target_ids": ["A", "D"], BBOX_KEY: [2, 1, 13, 12]}]}
        with self.assertRaisesRegex(PackError, "multi-region"):
            self.run_pack(request, self.root / "invalid-mixed")
        self.assertFalse((self.root / "invalid-mixed").exists())
        request["focus"]["windows"][0]["rotation_degrees_clockwise"] = 0
        explicit = self.run_pack(request, self.root / "explicit-pack")
        focus = next(c for c in explicit["contexts"] if c["kind"] == "focus")
        self.assertEqual(focus[BBOX_KEY], [2, 1, 13, 12])
        self.assertEqual(focus["rotation_degrees_clockwise"], 0)
        request["focus"]["windows"][0]["target_ids"] = ["A"]
        with self.assertRaisesRegex(PackError, "follow its region"):
            self.run_pack(request, self.root / "wrong-rotation")

    def test_whole_file_and_rgb_pins_fail_before_any_output(self):
        for key in self.request["pins"]:
            request = copy.deepcopy(self.request)
            request["pins"][key] = [18, 13] if key == "source_size" else "0" * 64
            with self.subTest(pin=key), self.assertRaisesRegex(PackError, "pin mismatch"):
                self.run_pack(request)
            self.assertFalse(self.output.exists())
        with self.assertRaisesRegex(PackError, "protocol whole-file"):
            self.run_pack(expected_protocol_sha256="0" * 64)
        self.assertFalse(self.output.exists())

    def test_input_aliases_hardlinks_symlinks_and_output_ancestry_rejected(self):
        write_json(self.protocol, self.request)
        hardlink = self.root / "hardlink.json"
        hardlink.hardlink_to(self.base)
        symlink = self.root / "symlink.json"
        symlink.symlink_to(self.base)
        for alias in (hardlink, symlink, self.base):
            with self.subTest(alias=alias.name), self.assertRaises(PackError):
                build_pack(self.source, self.base, alias, self.protocol, self.output)
            self.assertFalse(self.output.exists())
        # An existing parent cannot become the pack, nor can an input path.
        for destination in (self.root, self.source):
            with self.assertRaises(PackError):
                build_pack(self.source, self.base, self.inventory, self.protocol, destination)
        output_link = self.root / "output-hardlink"
        output_link.hardlink_to(self.source)
        dangling_output = self.root / "dangling-output"
        dangling_output.symlink_to(self.root / "missing-target")
        for destination in (output_link, dangling_output):
            with self.assertRaisesRegex(PackError, "immutable"):
                build_pack(self.source, self.base, self.inventory, self.protocol, destination)
        self.assertEqual(sha(self.source.read_bytes()), self.request["pins"]["source_sha256"])

    def test_existing_pack_and_invalid_geometry_cohort_are_immutable(self):
        self.run_pack()
        before = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(PackError, "immutable"):
            self.run_pack()
        after = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        request = copy.deepcopy(self.request)
        for selected in (["unknown"], ["A", "A"], []):
            request["selected_ids"] = selected
            destination = self.root / "bad-cohort"
            with self.assertRaises(PackError):
                self.run_pack(request, destination)
            self.assertFalse(destination.exists())
        request["selected_ids"] = ["A"]
        request["focus"] = {"windows": [{"id": "bad", "target_ids": ["A"], BBOX_KEY: [-1, 0, 3, 2]}]}
        with self.assertRaises(PackError):
            self.run_pack(request, self.root / "bad-geometry")
        self.assertFalse((self.root / "bad-geometry").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
