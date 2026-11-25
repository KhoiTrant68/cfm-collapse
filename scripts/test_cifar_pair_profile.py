"""Regression tests for the CIFAR handoff endpoint classification."""
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.cifar_pair_profile import classify_profile


class TestPairProfile(unittest.TestCase):
    def test_failed_legacy_continuation(self):
        path = Path(__file__).resolve().parents[1] / (
            "results/cifar_composition_exact_20261105/main/pair_1104_1984_B1.json")
        pair = json.loads(path.read_text())
        row = next(row for row in pair["rows"] if row["ratio"] == 2)
        state = row["handoff"][23]
        self.assertEqual(row["classes"][23], "atom:1984")
        for sign in (-1, 1):
            result = classify_profile(sign * state["q"], state["tau_handoff"],
                                      pair["r"], row["w"], pair["B"])
            self.assertEqual(result, ("mid", "inward barrier"))

    def test_signed_escape_and_symmetry(self):
        threshold = 1 / math.sinh(1)**2
        for w in (threshold / 2, threshold, 2 * threshold):
            for q, label in ((-2, "-"), (0, "mid"), (2, "+")):
                self.assertEqual(classify_profile(q, 1, 2, w, 1)[0], label)

    def test_regular_initial_time(self):
        self.assertEqual(classify_profile(0.1, 0, 1, 2, 1), ("mid", "profile event"))

    @patch("scripts.cifar_pair_profile.solve_ivp")
    def test_numerical_failure_is_unresolved(self, integrate):
        integrate.return_value.success = False
        self.assertEqual(classify_profile(0.1, 0, 1, 2, 1)[0], "unresolved")


if __name__ == "__main__":
    unittest.main()
