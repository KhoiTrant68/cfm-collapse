"""Interpolants x_t between source x0 ~ pi_0 and target x1.

Deterministic linear interpolant (docs/THEORY.md Section 0):

    x_t = (1 - t) x0 + t x1,     v_target = x1 - x0

Stochastic interpolant variant (docs/THEORY.md Part C, eq. C.1/C.2):

    x_t   = (1 - t) x0 + t x1 + gamma(t) Z,    gamma(t) = sigma * sqrt(t (1 - t))
    U     = d/dt x_t = x1 - x0 + gamma_dot(t) Z

The pathwise-derivative target is x1 - x0 + gamma_dot(t) Z, using the **same**
Z that generated x_t. Regressing on x1 - x0 alone is a *different* objective and
does not recover the marginal velocity field of the path (C.1) -- see the note
in THEORY Part C. gamma_dot(t) = sigma (1 - 2t) / (2 sqrt(t(1-t))) is integrable
but blows up like |t(1-t)|^{-1/2} at the endpoints; we clamp t into [eps, 1-eps]
with eps = 1e-4. This is a deliberate treatment of an integrable singularity,
not an approximation of convenience.
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
    """Linear interpolant. ``sigma=0`` is the exact deterministic EXP-1 case.

    For ``sigma>0`` (Part C) both x_t and the regression target use the same Z:

        gamma(t)     = sigma * sqrt(t(1-t))
        gamma_dot(t) = sigma * (1 - 2t) / (2 sqrt(t(1-t)))
        x_t    = (1-t) x0 + t x1 + gamma(t) Z
        target = x1 - x0 + gamma_dot(t) Z          # eq. (C.2)
    """

    def __init__(self, sigma: float = 0.0, t_eps: float = 1e-4):
        self.sigma = float(sigma)
        self.t_eps = float(t_eps)

    def sample(
        self,
        x0: torch.Tensor,
        x1: torch.Tensor,
        t: torch.Tensor,
        generator: torch.Generator | None = None,
    ) -> InterpolantBatch:
        target = x1 - x0
        if self.sigma <= 0.0:
            t_col = t.reshape(-1, 1)
            x_t = (1.0 - t_col) * x0 + t_col * x1
            return InterpolantBatch(x_t=x_t, target=target, t=t)

        # Stochastic interpolant: clamp t away from the endpoints so gamma_dot,
        # which diverges like |t(1-t)|^{-1/2}, stays finite. This is a deliberate
        # treatment of an integrable singularity (THEORY Part C), not a fudge.
        t = t.clamp(self.t_eps, 1.0 - self.t_eps)
        t_col = t.reshape(-1, 1)
        s = torch.sqrt(t_col * (1.0 - t_col))
        gamma = self.sigma * s
        gamma_dot = self.sigma * (1.0 - 2.0 * t_col) / (2.0 * s)
        z = torch.randn(x0.shape, generator=generator, device=x0.device, dtype=x0.dtype)
        x_t = (1.0 - t_col) * x0 + t_col * x1 + gamma * z
        target = target + gamma_dot * z            # (C.2): same Z as x_t
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
