"""Correctness guards for EXP-1 (spec Section 12: rule out 'right answer, wrong
reason' bugs). Run:

    uv run python scripts/sanity_checks.py

Checks
------
1. Analytic posterior satisfies the linear-Gaussian normal equations, and a
   Monte-Carlo posterior (rejection-free, via the joint Gaussian) matches it.
2. Integrating the EXACT closed-form field (★) with our ODE solver maps every
   source x0 onto the training point x^i (verifies solver + interpolant + (★)
   are mutually consistent, and that the t=1 handling is benign).
3. The unconditional model genuinely ignores y (no condition leak).
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

# Windows consoles default to cp1252; force UTF-8 so the ★/‖/ε glyphs print.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.interpolants import closed_form_velocity  # noqa: E402
from src.flows.ode_solver import integrate  # noqa: E402
from src.models.mlp_velocity import MLPVelocity  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402


def check_posterior():
    torch.manual_seed(0)
    d, k = 3, 2
    prob = LinearGaussianProblem.create(d=d, k=k, sigma_obs=0.3, seed=1)

    # (a) normal equations: precision @ mu_post = Sigma_x^-1 mu_x + A^T y / s^2
    y = torch.randn(k, dtype=torch.float64)
    mu = prob.posterior_mean(y)
    precision = torch.linalg.inv(prob.Sigma_post)
    rhs = prob._Sigma_x_inv @ prob.mu_x + prob.A.T @ y / prob.sigma_obs ** 2
    resid = torch.linalg.norm(precision @ mu - rhs)
    assert resid < 1e-8, f"normal-equation residual too big: {resid}"

    # (b) Monte-Carlo posterior from the joint Gaussian p(x,y).
    #     Cov = [[Sx, Sx A^T],[A Sx, A Sx A^T + s^2 I]].
    N = 400_000
    g = torch.Generator().manual_seed(7)
    X = prob.sample_prior(N, generator=g)
    Y = prob.forward(X, generator=g)
    # condition on y0 by local weighting (narrow band) -> approximate posterior
    y0 = y
    band = 0.05
    w = torch.exp(-((Y - y0[None, :]) ** 2).sum(1) / (2 * band ** 2))
    w = w / w.sum()
    mc_mean = (w[:, None] * X).sum(0)
    mc_cov_trace = float((w[:, None] * (X - mc_mean) ** 2).sum())  # weighted trace
    err_mean = float(torch.linalg.norm(mc_mean - mu))
    trace_ratio = mc_cov_trace / prob.posterior_trace()
    print(f"[posterior] normal-eq resid={resid:.2e}  MC mean err={err_mean:.3f}  "
          f"MC/analytic trace ratio={trace_ratio:.3f} (band-broadened, expect >1)")
    assert err_mean < 0.15, "MC posterior mean far from analytic"


def check_closed_form_flow():
    """Integrating (★) must send x0 -> x^i for every x0."""
    torch.manual_seed(0)
    d = 4
    x_i = torch.randn(1, d)

    class ExactField(torch.nn.Module):
        def forward(self, x, t, y=None):
            return closed_form_velocity(x, t, x_i.to(x.device).expand_as(x))

    field = ExactField()
    x0 = 3.0 * torch.randn(500, d)
    for method, eps in [("rk4", 1e-3), ("euler", 1e-3)]:
        xf = integrate(field, x0, None, n_steps=100, method=method, eps=eps)
        gap = float(torch.linalg.norm(xf - x_i, dim=1).mean())
        spread = float(xf.std(0).sum())
        print(f"[flow ★] method={method:5s} mean ‖x(1-ε)-x^i‖={gap:.3e}  "
              f"residual spread={spread:.3e}  (both should be ~O(ε))")
        assert gap < 5e-2, f"{method}: flow did not collapse to x^i"


def check_no_condition_leak():
    torch.manual_seed(0)
    model = MLPVelocity(data_dim=2, cond_dim=0)  # unconditional
    x = torch.randn(16, 2)
    t = torch.rand(16)
    y1 = torch.randn(16, 1)
    y2 = torch.randn(16, 1) + 10.0
    out1 = model(x, t, y1)
    out2 = model(x, t, y2)
    assert torch.allclose(out1, out2), "unconditional model leaked y!"
    print("[leak] unconditional model output invariant to y: OK")


if __name__ == "__main__":
    check_posterior()
    check_closed_form_flow()
    check_no_condition_leak()
    print("\nAll sanity checks passed.")
