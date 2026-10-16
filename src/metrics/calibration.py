"""Sample-based calibration of a conditional sampler against held-out truths.

A held-out pair (x*, y*) has x* drawn from the true conditional law given y*, so a
calibrated sampler conditioned on y* must treat x* as exchangeable with its own M draws
s_1..s_M. Every statistic here is a rank of x* among {x*, s_1..s_M}, so its law under
calibration is known exactly for finite M (no Gaussian or large-M assumption):

  marginal  per coordinate (a pixel, or one principal component of the hidden region):
            R = #{m : s_m < x*} is uniform on {0..M}. With u = (R + 1/2)/(M + 1), the
            central level-a interval covers x* iff |u - 1/2| <= a/2.
  joint     in the span of the top k principal components: the squared Mahalanobis
            distance of each of the M+1 points to the mean and covariance of the other M
            (leave one out, so the M+1 statistics are exchangeable). With
            u = (#{m : d_m < d*} + 1/2)/(M + 1), the level-a region covers x* iff u <= a.

The exact discrete null requires tie-free scores or randomized tie breaking (pass rng).
Legacy calls without rng retain midranks and need not follow that null with ties.
The reference curves below are what a calibrated sampler gets at the same M. A quantile
interval of the M draws, by contrast, covers a fresh draw less often than its nominal
level (about 0.87 for the 5%-95% interval at M = 64), so it has no exact reference.

Numpy only, so it can be tested without torch: scripts/test_calibration.py.
"""
from __future__ import annotations

import numpy as np

LEVELS = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
PIT_GRID = np.linspace(0.05, 0.95, 19)
_TOL = 1e-12


def _grid(M: int) -> np.ndarray:
    return (np.arange(M + 1) + 0.5) / (M + 1)


def reference_central(M: int, levels: np.ndarray = LEVELS) -> np.ndarray:
    """Coverage of the central level-a rank interval for a calibrated sampler with M draws."""
    return central_coverage(_grid(M), levels)


def reference_upper(M: int, levels: np.ndarray = LEVELS) -> np.ndarray:
    """Coverage of the one-sided level-a rank region for a calibrated sampler with M draws."""
    return upper_coverage(_grid(M), levels)


def reference_pit_cdf(M: int, grid: np.ndarray = PIT_GRID) -> np.ndarray:
    """P(u <= g) for a calibrated sampler with M draws."""
    return pit_cdf(_grid(M), grid)


def marginal_pit(samples: np.ndarray, truth: np.ndarray,
                 rng: np.random.Generator | None = None) -> np.ndarray:
    """Rank PIT; pass rng for exact randomized ranks under exchangeability with ties.

    With rng=None retain legacy midranks, whose discrete null requires no ties.
    """
    M = samples.shape[0]
    ties = (samples == truth[None]).sum(0)
    offset = 0.5 * ties if rng is None else rng.integers(0, ties + 1)
    below = (samples < truth[None]).sum(0) + offset
    return (below + 0.5) / (M + 1)


def central_coverage(u: np.ndarray, levels: np.ndarray = LEVELS) -> np.ndarray:
    """Share of the u values whose central level-a interval covers the truth, per level."""
    u = np.asarray(u).ravel()
    return np.array([float((np.abs(u - 0.5) <= a / 2 + _TOL).mean()) for a in levels])


def upper_coverage(u: np.ndarray, levels: np.ndarray = LEVELS) -> np.ndarray:
    """Share of the u values inside the one-sided level-a region, per level."""
    u = np.asarray(u).ravel()
    return np.array([float((u <= a + _TOL).mean()) for a in levels])


def pit_cdf(u: np.ndarray, grid: np.ndarray = PIT_GRID) -> np.ndarray:
    u = np.asarray(u).ravel()
    return np.array([float((u <= g + _TOL).mean()) for g in grid])


def loo_mahalanobis(Z: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """Z (P, k) -> (P,): each row's squared Mahalanobis distance to the mean and covariance
    of the other P-1 rows. A ridge of `ridge` times the mean variance keeps the distance
    finite when the draws have collapsed (a rank-deficient covariance)."""
    P, k = Z.shape
    out = np.empty(P)
    for i in range(P):
        rest = np.delete(Z, i, axis=0)
        diff = Z[i] - rest.mean(0)
        S = np.atleast_2d(np.cov(rest, rowvar=False))
        S = S + (ridge * np.trace(S) / k + _TOL) * np.eye(k)
        out[i] = float(diff @ np.linalg.solve(S, diff))
    return out


def joint_pit(samples_z: np.ndarray, truth_z: np.ndarray,
              rng: np.random.Generator | None = None) -> float:
    """samples_z (M, k), truth_z (k,) -> u in (0, 1); small u = the truth is central."""
    d = loo_mahalanobis(np.vstack([truth_z[None], samples_z]))
    M = samples_z.shape[0]
    ties = (d[1:] == d[0]).sum()
    offset = 0.5 * ties if rng is None else rng.integers(0, ties + 1)
    below = (d[1:] < d[0]).sum() + offset
    return float((below + 0.5) / (M + 1))


def pca_basis(X: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """X (N, D) -> mean (D,), top-k components (k, D), and each one's share of variance."""
    mu = X.mean(0)
    _, s, Vt = np.linalg.svd(X - mu, full_matrices=False)
    var = s ** 2
    return mu, Vt[:k], var[:k] / var.sum()
