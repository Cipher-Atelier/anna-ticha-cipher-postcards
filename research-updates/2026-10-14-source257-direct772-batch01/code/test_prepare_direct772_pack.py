"""New queue/no-repeat/blinding fixtures; no images are read."""
import copy
import json
import os
from pathlib import Path
import unittest

import prepare_direct772_pack as core

STAGE = Path(__file__).resolve().parents[1]


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repository = Path(os.environ.get("SOURCE257_PUBLIC_REPOSITORY", Path(__file__).resolve().parents[3]))
        d12 = STAGE.parent / "2026-10-14-source257-repeat-sequence"
        public_geometry = {"references": d12 / "data/effective70-profile-references-v1.json",
                           "context_index": d12 / "data/context-index-v1.json"}
        cls.inputs = {}
        for key, (relative, expected) in core.PINS.items():
            raw = (public_geometry[key] if key in public_geometry else repository / relative).read_bytes()
            if core.digest(raw) != expected:
                raise ValueError("Frozen fixture input pin mismatch")
            cls.inputs[key] = json.loads(raw)

    def setUp(self):
        self.data = copy.deepcopy(self.inputs)

    def queue(self):
        return core.queue(self.data["canonical"], self.data["D13_protocol"], self.data["D13_delta"])

    def test_exact_scope_and_saved_bytes(self):
        prepared = self.queue()
        self.assertEqual(core.encoded(prepared), (STAGE / "results/direct772-queue-v1.json").read_bytes())
        self.assertEqual((len(prepared["ordered_queue"]), len(prepared["selected_pair_ids"]), len(prepared["remaining_pair_ids"])), (772, 64, 708))
        self.assertEqual([r["ordinal"] for r in prepared["ordered_queue"]], list(range(1, 773)))
        self.assertEqual(prepared["selected_pair_ids"][-1], "FC015--FC123")
        self.assertEqual(prepared["remaining_pair_ids"][0], "FC015--FC125")

    def test_input_order_does_not_choose_batch(self):
        expected = self.queue()
        self.data["canonical"]["core_pairs"].reverse()
        self.assertEqual(self.queue(), expected)

    def test_wrong_coverage_rejected(self):
        row = next(r for r in self.data["canonical"]["core_pairs"] if r["deferred_reason"] == core.REASON)
        row["reader_A"]["coverage"] = "DIRECT_PAIRED_SOURCE_COMPARISON"
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.queue()

    def test_repeat_of_positive_edge_rejected(self):
        pair = self.queue()["ordered_queue"][0]
        self.data["canonical"]["graph"]["positive_edges"].append(pair)
        with self.assertRaisesRegex(ValueError, "Completed pair"):
            self.queue()

    def test_repeat_of_D13_pair_rejected(self):
        pair = self.queue()["ordered_queue"][0]
        self.data["D13_protocol"]["fixed_pair_ids"][0] = pair["pair_id"]
        self.data["D13_delta"]["pair_dispositions"][0]["pair_id"] = pair["pair_id"]
        with self.assertRaisesRegex(ValueError, "Completed pair"):
            self.queue()

    def test_missing_queue_pair_rejected(self):
        self.data["canonical"]["core_pairs"].pop(0)
        with self.assertRaisesRegex(ValueError, "Unique930"):
            self.queue()

    def test_geometry_blinding_and_saved_bytes(self):
        prepared = self.queue()
        self.data["references"]["profiles"][0]["significant_signature"] = {"secret": "FORBIDDEN_HISTORY"}
        intake = core.geometry(prepared, self.data["references"], self.data["context_index"])
        raw = core.encoded(intake)
        self.assertNotIn(b"FORBIDDEN_HISTORY", raw)
        self.assertNotIn(b"significant_signature", raw)
        self.assertNotIn(b"eligibility", raw)
        self.assertEqual(raw, (STAGE / "results/judge-source-geometry-intake-v1.json").read_bytes())
        self.assertEqual(len(intake["profiles"]), 36)
        self.assertEqual(len({w["context_id"] for r in intake["profiles"] for w in r["windows"].values()}), 72)

    def test_frame_sign_rejected(self):
        row = next(r for r in self.data["context_index"]["contexts"] if r.get("focus_id") == "FC002-TIGHT")
        row["rotation_degrees_clockwise"] = -90
        with self.assertRaisesRegex(ValueError, "Frame sign"):
            core.geometry(self.queue(), self.data["references"], self.data["context_index"])

    def test_changed_window_rejected(self):
        row = next(r for r in self.data["context_index"]["contexts"] if r.get("focus_id") == "FC002-TIGHT")
        row[core.BOX][0] += 1
        with self.assertRaisesRegex(ValueError, "padding"):
            core.geometry(self.queue(), self.data["references"], self.data["context_index"])


if __name__ == "__main__":
    unittest.main()
