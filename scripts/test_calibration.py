"""Checks of src/metrics/calibration.py on samplers whose calibration is known.

  calibrated     truth and draws from the same correlated Gaussian: every curve must sit
                 on its finite-M reference, up to Monte Carlo error
  collapsed      the draws are one point plus tiny noise: coverage near 0 at every level
  over-dispersed draws with twice the true scale: coverage above the reference

Usage:  uv run python scripts/test_calibration.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.calibration import (LEVELS, central_coverage, joint_pit, marginal_pit,  # noqa: E402
                                     pca_basis, reference_central, reference_upper,
                                     upper_coverage)

M, D, K, N_TEST = 64, 40, 8, 400


def run(scale: float, collapse: bool, rng: np.random.Generator):
    L = rng.standard_normal((D, D)) / np.sqrt(D)
    X_train = rng.standard_normal((2000, D)) @ L.T
    mu, V, _ = pca_basis(X_train, K)
    u_pix, u_pc, u_joint = [], [], []
    for _ in range(N_TEST):
        truth = rng.standard_normal(D) @ L.T
        if collapse:
            s = (rng.standard_normal(D) @ L.T)[None] + 1e-4 * rng.standard_normal((M, D))
        else:
            s = scale * rng.standard_normal((M, D)) @ L.T
        u_pix.append(marginal_pit(s, truth))
        zs, zt = (s - mu) @ V.T, (truth - mu) @ V.T
        u_pc.append(marginal_pit(zs, zt))
        u_joint.append(joint_pit(zs, zt))
    return (central_coverage(np.concatenate(u_pix)), central_coverage(np.concatenate(u_pc)),
            upper_coverage(np.array(u_joint)))


def main() -> None:
    rng = np.random.default_rng(0)
    ref_c, ref_u = reference_central(M), reference_upper(M)
    i90 = int(np.flatnonzero(np.isclose(LEVELS, 0.9))[0])
    print(f"reference at M={M}: central 90% = {ref_c[i90]:.4f}, one-sided 90% = {ref_u[i90]:.4f}")
    assert abs(ref_c[i90] - 59 / 65) < 1e-12 and abs(ref_u[i90] - 59 / 65) < 1e-12

    pix, pc, joint = run(1.0, False, rng)
    print("calibrated    max |dev|: pixel %.3f  pc %.3f  joint %.3f"
          % tuple(np.abs(c - r).max() for c, r in ((pix, ref_c), (pc, ref_c), (joint, ref_u))))
    assert np.abs(pix - ref_c).max() < 0.02        # 16000 correlated pixel ranks
    assert np.abs(pc - ref_c).max() < 0.03         # 3200 component ranks
    assert np.abs(joint - ref_u).max() < 0.07      # 400 images: 3 s.e. at a = 0.5

    pix, pc, joint = run(1.0, True, rng)
    print("collapsed     90%%: pixel %.3f  pc %.3f  joint %.3f" % (pix[i90], pc[i90], joint[i90]))
    assert pix[i90] < 0.05 and pc[i90] < 0.05 and joint[i90] < 0.05

    pix, pc, joint = run(2.0, False, rng)
    print("over-dispersed 50%%: pixel %.3f  pc %.3f  joint %.3f (reference %.3f / %.3f)"
          % (pix[4], pc[4], joint[4], ref_c[4], ref_u[4]))
    assert pix[4] > ref_c[4] + 0.1 and pc[4] > ref_c[4] + 0.1 and joint[4] > ref_u[4] + 0.1
    print("all calibration checks passed")


if __name__ == "__main__":
    main()
