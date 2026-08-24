"""Velocity error vs. the closed-form collapsed minimizer (★) — P2.

We measure how close the learned field v_theta(x, t, y^i) is to

    v*(x, t, y^i) = (x^i - x) / (1 - t)

We sample (x, t) *on the interpolant manifold* the network was trained on
(x = (1-t) x0 + t x^i for random x0), because that is where the closed-form
prediction (★) is the actual conditional expectation. We restrict t to
[0, t_max] with t_max = 0.95 to stay away from the t=1 singularity of (★)
(spec Section 3.5 item 3).
"""
from __future__ import annotations

import torch

from ..flows.interpolants import closed_form_velocity


@torch.no_grad()
def velocity_error_vs_closed_form(
    model,
    x_train_point: torch.Tensor,     # (d,)  x^i
    y_cond: torch.Tensor,            # (k,)  y^i
    n_points: int = 2000,
    t_max: float = 0.95,
    source_std: float = 1.0,
    generator: torch.Generator | None = None,
    device: torch.device | None = None,
) -> dict:
    """Return relative and absolute L2 velocity error, averaged over (x, t)."""
    device = device or next(model.parameters()).device
    d = x_train_point.shape[0]
    x1 = x_train_point.to(device, torch.float32)[None, :].expand(n_points, -1)
    y = y_cond.to(device, torch.float32)[None, :].expand(n_points, -1)

    x0 = source_std * torch.randn(n_points, d, generator=generator, device=device)
    t = t_max * torch.rand(n_points, generator=generator, device=device)
    t_col = t[:, None]
    x = (1.0 - t_col) * x0 + t_col * x1  # on-manifold interpolant point

    v_pred = model(x, t, y)
    v_star = closed_form_velocity(x, t, x1)

    err = torch.linalg.norm(v_pred - v_star, dim=1)
    denom = torch.linalg.norm(v_star, dim=1).clamp_min(1e-8)
    rel = (err / denom)
    return {
        "vel_rel_err_mean": float(rel.mean()),
        "vel_rel_err_median": float(rel.median()),
        "vel_abs_err_mean": float(err.mean()),
    }
