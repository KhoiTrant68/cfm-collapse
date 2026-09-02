"""Per-sample nearest-neighbour memorization ratio.

Standard literature diagnostic (Yoon et al. 2023; used e.g. by Buchanan,
Pai, Ma & De Bortoli, "On the Edge of Memorization in Diffusion Models",
arXiv:2508.17689): a generated sample is "memorized" if its squared distance
to the nearest training point is at most ``threshold`` times its squared
distance to the second-nearest training point. Reporting the fraction of
memorized samples is a per-sample complement to the aggregate trace(Cov)
diagnostics used elsewhere in this repo.
"""
from __future__ import annotations

import torch


def memorization_ratio(
    samples: torch.Tensor,
    X_train: torch.Tensor,
    threshold: float = 1.0 / 9.0,
) -> float:
    """Fraction of ``samples`` whose nearest training point dominates the
    second-nearest one: ``d(1)^2 <= threshold * d(2)^2``.

    ``threshold=1/9`` matches arXiv:2508.17689's default (their ``c``);
    equivalently a ratio of raw distances below ``1/3``.
    """
    s = samples.to(torch.float64)
    X = X_train.to(torch.float64)
    d2 = torch.cdist(s, X, p=2) ** 2  # (n_samples, N_train)
    top2 = torch.topk(d2, k=min(2, X.shape[0]), dim=1, largest=False).values
    if top2.shape[1] < 2:
        return float("nan")
    memorized = top2[:, 0] <= threshold * top2[:, 1]
    return float(memorized.to(torch.float64).mean())
