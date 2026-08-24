"""Posterior statistics of generated samples (spec Section 3.5, items 1-2).

For a fixed condition y^i we generate M samples and compute:
  - trace(Cov(samples))         -> compare to trace(Sigma_post)   [P1]
  - || mean(samples) - mu_post(y^i) ||                             (mean error)
  - || mean(samples) - x^i ||   -> collapse toward training point  [P3]
  - nearest-other-training-point distance for the sample mean      [P3]
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import torch


@dataclass
class PosteriorSampleStats:
    trace_cov: float
    mean_err_post: float          # ||mean - mu_post(y)||
    mean_err_train_point: float   # ||mean - x^i||        [P3]
    dist_to_nearest_other: float  # min_{j != i} ||mean - x^j||  [P3]
    ratio_own_vs_other: float     # mean_err_train_point / dist_to_nearest_other

    def as_dict(self) -> dict:
        return asdict(self)


def sample_covariance_trace(samples: torch.Tensor) -> float:
    """trace of the empirical covariance (unbiased, ddof=1)."""
    s = samples.to(torch.float64)
    n = s.shape[0]
    mean = s.mean(dim=0, keepdim=True)
    centered = s - mean
    # trace(Cov) = sum of per-dimension variances
    var = (centered ** 2).sum(dim=0) / (n - 1)
    return float(var.sum())


def posterior_sample_stats(
    samples: torch.Tensor,
    mu_post: torch.Tensor,
    x_train_point: torch.Tensor,
    all_train_points: torch.Tensor,
    own_index: int,
) -> PosteriorSampleStats:
    s = samples.to(torch.float64)
    mean = s.mean(dim=0)

    trace_cov = sample_covariance_trace(s)
    mean_err_post = float(torch.linalg.norm(mean - mu_post.to(torch.float64)))
    mean_err_train = float(torch.linalg.norm(mean - x_train_point.to(torch.float64)))

    others = all_train_points.to(torch.float64)
    dists = torch.linalg.norm(others - mean[None, :], dim=1)
    dists[own_index] = float("inf")  # exclude the own point
    dist_other = float(dists.min())

    ratio = mean_err_train / dist_other if dist_other > 0 else float("inf")
    return PosteriorSampleStats(
        trace_cov=trace_cov,
        mean_err_post=mean_err_post,
        mean_err_train_point=mean_err_train,
        dist_to_nearest_other=dist_other,
        ratio_own_vs_other=ratio,
    )
