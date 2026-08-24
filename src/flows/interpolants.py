"""Interpolants x_t between source x0 ~ pi_0 and target x1.

Deterministic linear interpolant (spec Section 2.1):

    x_t = (1 - t) x0 + t x1,     v_target = x1 - x0

Stochastic interpolant variant (spec Section 3.7, to contrast the two remedies
against 2510.18118):

    x_t = (1 - t) x0 + t x1 + sigma * sqrt(t (1 - t)) * Z,   Z ~ N(0, I)

For the stochastic case the conditional target velocity is still ``x1 - x0``
plus the drift of the added noise bridge; we use the standard result that the
regression target for E[dx_t/dt | x_t] is unchanged in expectation when the
noise is a Brownian-bridge-like term with the ``sqrt(t(1-t))`` schedule, so we
keep ``x1 - x0`` as the target for the network (this matches torchcfm's
``VariancePreserving``-style targets closely enough for our qualitative
comparison; the point of EXP-1 is the *deterministic* case which is exact).
"""
from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class InterpolantBatch:
    x_t: torch.Tensor       # (b, d)
    target: torch.Tensor    # (b, d)  regression target for v_theta
    t: torch.Tensor         # (b,)


class LinearInterpolant:
    """Deterministic linear interpolant. ``sigma=0`` is the exact EXP-1 case."""

    def __init__(self, sigma: float = 0.0):
        self.sigma = float(sigma)

    def sample(
        self,
        x0: torch.Tensor,
        x1: torch.Tensor,
        t: torch.Tensor,
        generator: torch.Generator | None = None,
    ) -> InterpolantBatch:
        t_col = t.reshape(-1, 1)
        x_t = (1.0 - t_col) * x0 + t_col * x1
        target = x1 - x0
        if self.sigma > 0.0:
            std = self.sigma * torch.sqrt(torch.clamp(t_col * (1.0 - t_col), min=0.0))
            z = torch.randn(x_t.shape, generator=generator, device=x_t.device, dtype=x_t.dtype)
            x_t = x_t + std * z
        return InterpolantBatch(x_t=x_t, target=target, t=t)


def closed_form_velocity(x: torch.Tensor, t: torch.Tensor, x1: torch.Tensor,
                         eps: float = 1e-6) -> torch.Tensor:
    """The collapsed minimizer (spec eq. ★):  v*(x, t, y^i) = (x^i - x)/(1 - t).

    ``eps`` guards the singularity at t=1; callers that evaluate this for a
    metric restrict t to <= 0.95 (spec Section 3.5), so eps only protects
    against exact-1.0 floating point inputs.
    """
    t_col = t.reshape(-1, 1)
    denom = torch.clamp(1.0 - t_col, min=eps)
    return (x1 - x) / denom
