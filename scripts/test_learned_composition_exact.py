"""Regression checks for the exact references of scripts/learned_composition_exact.py.

    PYTHONPATH=. python -m unittest scripts.test_learned_composition_exact
"""
import unittest

import torch

from scripts.learned_composition import EPS_OUT, ros2_states, w_c
from scripts.learned_composition_exact import endpoint_sets, vector_F, x_at


class ExactReferenceTests(unittest.TestCase):
    def test_threshold_has_no_midpoint_basin(self):
        # Theorem thm:composition(b) at w = w_c: only x0 = 0 reaches 0, the atoms split at 0.
        for B in (1.0, 2.0, 3.0):
            row = endpoint_sets("E4", B, 1.0)
            self.assertIsNone(row["basin"])
            self.assertEqual(row["basin_probability"], 0.0)
            self.assertLess(abs(row["split"]), 1e-6)

    def test_basin_above_threshold_matches_paper_table(self):
        # Table tab:composition: B = 1, w = 2 w_c gives probability 0.406.
        row = endpoint_sets("E4", 1.0, 2.0)
        lo, hi = row["basin"]
        self.assertAlmostEqual(hi, 0.5329026, places=6)
        self.assertAlmostEqual(lo, -hi, places=9)
        self.assertAlmostEqual(row["basin_probability"], 0.40590, places=4)

    def test_learned_integrator_keeps_the_certified_basin(self):
        # ros2_states on the exact composite (B = 1, w = 2 w_c; basin +-0.5329): sources just inside
        # stay at the midpoint to eps = 1e-5, sources just outside reach an atom. A fixed-step RK4
        # ejected the inside ones once the attraction became stiff.
        B, w = 1.0, 2 * w_c(1.0)

        def F(x, tau):
            s = (-torch.expm1(-tau) * torch.exp(2 * tau))[:, None] * x
            return (1 + w) / 2 * (torch.tanh(s + B) + torch.tanh(s - B)) - w * torch.tanh(s)
        x0 = torch.tensor([[0.0], [0.3], [0.52], [-0.52], [0.55], [-0.55], [1.5]], dtype=torch.float64)
        x = ros2_states(F, x0, rtol=1e-5)[:, 0, -1]
        self.assertTrue(bool((x[:4].abs() < 1e-3).all()), x)
        self.assertTrue(bool(((x[4:].abs() - 1).abs() < 1e-3).all()), x)

    def test_finite_cutoff_states_converge_to_the_atom(self):
        # Outside the basin the state at t = 1 - eps approaches 1 as eps falls.
        x = x_at([0.6], vector_F(2 * w_c(1.0), (0.5, 0.5), (1.0, -1.0), 0.0))[0]
        self.assertEqual(len(x), len(EPS_OUT))
        for eps, xe in zip(EPS_OUT, x):
            self.assertLess(abs(1 - xe), 4 * eps)     # a NaN state fails here too


if __name__ == "__main__":
    unittest.main()
