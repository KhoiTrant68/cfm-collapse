"""Mode-coverage metrics for a multimodal posterior (EXP-2).

Given generated samples and the closed-form posterior modes (means + weights),
assign each sample to its nearest posterior mode and measure how many of the
*significant* modes are actually populated. Under a faithful posterior sampler
every significant mode is covered; under selective memorization the samples pile
onto the single mode that contains the memorized training point.
"""
from __future__ import annotations

import torch


def mode_coverage(samples: torch.Tensor, mode_means: torch.Tensor,
                  mode_weights: torch.Tensor, w_min: float = 0.1,
                  occ_tau: float = 0.1) -> dict:
    """
    samples      : (n, d)
    mode_means   : (K, d) posterior component means
    mode_weights : (K,)   posterior component weights
    w_min        : a mode is "significant" if its true weight > w_min
    occ_tau      : a significant mode counts as covered if its occupancy > occ_tau
    """
    s = samples.to(torch.float64)
    mm = mode_means.to(torch.float64)
    n = s.shape[0]

    # nearest-mode assignment (Euclidean)
    d2 = torch.cdist(s, mm) ** 2          # (n, K)
    assign = d2.argmin(dim=1)
    K = mm.shape[0]
    occ = torch.bincount(assign, minlength=K).to(torch.float64) / n

    sig = mode_weights.to(torch.float64) > w_min
    n_sig = int(sig.sum())
    covered = int(((occ > occ_tau) & sig).sum())
    coverage = covered / max(n_sig, 1)

    # total-variation-ish gap between empirical occupancy and true weights
    tv = 0.5 * float((occ - mode_weights.to(torch.float64)).abs().sum())

    return {
        "n_significant_modes": n_sig,
        "modes_covered": covered,
        "mode_coverage": coverage,       # in [0,1]; 1 = all significant modes hit
        "occupancy_tv": tv,              # 0 = occupancy matches true weights
        "max_occupancy": float(occ.max()),
    }
