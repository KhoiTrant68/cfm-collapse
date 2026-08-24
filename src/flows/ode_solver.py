"""Fixed-step ODE integrators for sampling: dx/dt = v_theta(x, t, y).

We integrate the probability-flow ODE from t=0 (x = x0 ~ pi_0) forward to
t = t_final. Both an explicit Euler and a classical RK4 are provided; RK4 is the
default because it is markedly more accurate at the same step count and this
project's conclusions depend on measuring *variance*, not on solver speed.

Singularity handling (spec Section 7.2)
---------------------------------------
The collapsed closed-form field v*(x,t,y) = (x^i - x)/(1 - t) is singular at
t=1. Along the *exact* collapsed trajectory the velocity is actually the finite
constant (x^i - x0), so the ODE itself is not stiff; the risk is purely that a
learned network, trained against large-magnitude targets near t=1, is noisy
there. We therefore stop integration at ``t_final = 1 - eps`` (default eps=1e-3)
rather than exactly 1. This is a *deliberate* treatment of the t=1 singularity,
not a numerical hack: at eps=1e-3 the residual gap to x(1) is O(eps) and its
contribution to the measured sample variance is O(eps^2), far below the collapse
signal we are trying to detect.
"""
from __future__ import annotations

import torch


@torch.no_grad()
def integrate(
    model,
    x0: torch.Tensor,
    y: torch.Tensor | None,
    n_steps: int = 100,
    method: str = "rk4",
    t0: float = 0.0,
    eps: float = 1e-3,
) -> torch.Tensor:
    """Integrate the flow from t0 to (1 - eps). Returns final state (same shape as x0).

    ``y`` is broadcast to the batch if given as a single (k,) vector.
    """
    device = x0.device
    x = x0.clone()
    t_final = 1.0 - eps
    ts = torch.linspace(t0, t_final, n_steps + 1, device=device)

    if y is not None and y.dim() == 1:
        y = y[None, :].expand(x0.shape[0], -1)

    def vf(state: torch.Tensor, t_scalar: float) -> torch.Tensor:
        t_vec = torch.full((state.shape[0],), float(t_scalar), device=device)
        return model(state, t_vec, y)

    for i in range(n_steps):
        t = float(ts[i])
        h = float(ts[i + 1] - ts[i])
        if method == "euler":
            x = x + h * vf(x, t)
        elif method == "rk4":
            k1 = vf(x, t)
            k2 = vf(x + 0.5 * h * k1, t + 0.5 * h)
            k3 = vf(x + 0.5 * h * k2, t + 0.5 * h)
            k4 = vf(x + h * k3, t + h)
            x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        else:
            raise ValueError(f"Unknown method={method}")
    return x


@torch.no_grad()
def generate_samples(
    model,
    n_samples: int,
    data_dim: int,
    y: torch.Tensor | None,
    source_std: float = 1.0,
    n_steps: int = 100,
    method: str = "rk4",
    eps: float = 1e-3,
    generator: torch.Generator | None = None,
    device: torch.device | None = None,
) -> torch.Tensor:
    """Draw ``n_samples`` fresh x0 and push them through the flow for fixed y."""
    device = device or next(model.parameters()).device
    x0 = source_std * torch.randn(n_samples, data_dim, generator=generator, device=device)
    y_dev = None if y is None else y.to(device, torch.float32)
    return integrate(model, x0, y_dev, n_steps=n_steps, method=method, eps=eps)
