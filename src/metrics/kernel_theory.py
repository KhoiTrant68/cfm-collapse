"""Exact finite-N kernel-regression reference curves (docs/THEORY.md Part B).

Label smoothing turns hard conditioning into a Gaussian kernel regression over
the training atoms. This module implements the *exact, parameter-free* reference
quantities from Proposition 8 / Theorem 10 / Proposition 13, against which the
generated moments should be compared. There are no fitted constants and no
asymptotics here: everything is computed directly from the training set.

Central objects
---------------
* ``kernel_weights``  -> p_j^(h)(y) ∝ K_h(y − y^j)          (Thm 10, eq. 10.1 / 9.1)
* ``kernel_moments``  -> (x̄_h, Cov_h, n_eff)               (Prop 13, eq. 13.1)
* ``kernel_field``    -> v_h^*(x,t,y) via the full posterior (Prop 8, eq. 8.1)
* ``cov_expansion``   -> tr Σ_post + h²‖J‖_F²               (Prop 15, closed form)

All kernel computations go through log-sum-exp: for small h and k=1 the raw ratio
of Gaussian weights between atoms overflows float easily (see WORK_ORDER §3).
"""
from __future__ import annotations

import torch

Tensor = torch.Tensor


def _as_f64(*ts: Tensor) -> tuple[Tensor, ...]:
    return tuple(t.to(torch.float64) for t in ts)


def _log_kernel_weights(y_q: Tensor, Y: Tensor, h: float) -> Tensor:
    """Unnormalised log label-kernel weights log K_h(y_q − y^j), shape (N,).

    The kernel normalisation (2π h²)^{-k/2} is common to every atom and drops
    out under the softmax, so it is omitted.

    For ``h == 0`` the weights concentrate on the nearest label, uniformly over
    *every* atom attaining that minimum. With distinct labels that is a single
    index (Corollary 11); with repeated labels -- class conditioning, say -- it is
    the whole tied set, which is the empirical conditional support the duplicate-label
    case of Proposition 2 collapses onto. Putting the mass on one arbitrary member
    of a tie instead would report n_eff = 1 and a zero reference covariance where
    the truth is the within-class scatter.
    """
    y_q, Y = _as_f64(y_q, Y)
    d2 = ((y_q[None, :] - Y) ** 2).sum(dim=-1)  # (N,)
    if h <= 0.0:
        dmin = d2.min()
        # Tolerance because the label vectors arrive through floating-point work.
        tied = d2 <= dmin + 1e-12 * (1.0 + dmin.abs())
        log_w = torch.full_like(d2, -float("inf"))
        log_w[tied] = 0.0
        return log_w
    return -0.5 * d2 / (h ** 2)


def kernel_weights(y_q: Tensor, Y: Tensor, h: float) -> Tensor:
    """p_j^(h)(y_q) ∝ K_h(y_q − y^j).  y_q:(k,), Y:(N,k) -> (N,).

    h == 0: uniform over argmin_j |y_q − y^j| -- a point mass when labels are
    distinct (Corollary 11), the tied set when they repeat.
    """
    return torch.softmax(_log_kernel_weights(y_q, Y, h), dim=0)


def n_eff(weights: Tensor) -> float:
    """Effective number of weighted atoms, 1 / Σ_j p_j²."""
    w = weights.to(torch.float64)
    return float(1.0 / (w ** 2).sum().clamp_min(1e-300))


def kernel_moments(y_q: Tensor, X: Tensor, Y: Tensor, h: float) -> tuple[Tensor, Tensor, float]:
    """(x̄_h, Cov_h, n_eff) at query y_q, per Proposition 13.

    x̄_h  = Σ_j p_j x^j
    Cov_h = Σ_j p_j (x^j − x̄_h)(x^j − x̄_h)ᵀ
    Returns x̄_h:(d,), Cov_h:(d,d) in float64, and the scalar n_eff.
    """
    X, = _as_f64(X)
    p = kernel_weights(y_q, Y, h)  # (N,) f64
    x_bar = (p[:, None] * X).sum(dim=0)  # (d,)
    centered = X - x_bar[None, :]  # (N,d)
    cov = (p[:, None, None] * centered[:, :, None] * centered[:, None, :]).sum(dim=0)
    return x_bar, cov, n_eff(p)


def kernel_moments_trace(y_q: Tensor, X: Tensor, Y: Tensor, h: float
                         ) -> tuple[Tensor, float, float]:
    """(x_bar_h, tr Cov_h, n_eff) without ever forming the d x d covariance.

    Same quantities as :func:`kernel_moments`, but using
    ``tr Cov_h = sum_j p_j |x^j - x_bar_h|^2``.  At image scale (d = 3072) the
    full matrix is 9.4M entries per query and only its trace is ever used, so
    this is the routine EXP-3 calls.
    """
    X, = _as_f64(X)
    p = kernel_weights(y_q, Y, h)                       # (N,) f64
    x_bar = (p[:, None] * X).sum(dim=0)                 # (d,)
    sq = ((X - x_bar[None, :]) ** 2).sum(dim=1)         # (N,)
    return x_bar, float((p * sq).sum()), n_eff(p)


def kernel_trace_cov(y_q: Tensor, X: Tensor, Y: Tensor, h: float) -> float:
    """tr Cov_h(y_q) — the exact P7 reference target (Thm 10 / Prop 13)."""
    _, cov, _ = kernel_moments(y_q, X, Y, h)
    return float(torch.trace(cov))


@torch.no_grad()
def kernel_field(x: Tensor, t: Tensor, y_q: Tensor, X: Tensor, Y: Tensor,
                 h: float, source_std: float = 1.0) -> Tensor:
    """v_h^*(x,t,y_q) via Proposition 8, eq. (8.1), with log-sum-exp.

    The posterior over training indices factorises into a *spatial* source term
    π0((x − t x^j)/(1−t)) and a *label* kernel K_h(y_q − y^j):

        w_j ∝ π0((x − t x^j)/(1−t)) · K_h(y_q − y^j),
        v_h^* = Σ_j w_j (x^j − x)/(1−t).

    Shapes: x:(P,d), t:(P,), y_q:(k,), X:(N,d), Y:(N,k) -> (P,d).
    """
    x, t, y_q, X, Y = _as_f64(x, t, y_q, X, Y)
    one_m_t = (1.0 - t).clamp_min(1e-6)[:, None]                         # (P,1)
    # source consistency: log π0((x − t x^j)/(1−t)), Gaussian N(0, source_std² I)
    x0 = (x[:, None, :] - t[:, None, None] * X[None, :, :]) / one_m_t[:, :, None]  # (P,N,d)
    log_src = -0.5 * (x0 ** 2).sum(dim=-1) / (source_std ** 2)           # (P,N)
    log_ker = _log_kernel_weights(y_q, Y, h)                            # (N,)
    log_w = log_src + log_ker[None, :]                                  # (P,N)
    w = torch.softmax(log_w, dim=1)                                     # (P,N)
    diff = (X[None, :, :] - x[:, None, :]) / one_m_t[:, :, None]         # (P,N,d)
    return (w[:, :, None] * diff).sum(dim=1)                            # (P,d)


def cov_expansion(problem, h: float) -> tuple[float, float]:
    """Closed-form Prop 15 prediction for the linear-Gaussian model.

    In the linear-Gaussian case μ(y) = Σ_post Aᵀ y / σ_obs² + const is *exactly*
    linear, so the Jacobian J = ∂μ/∂y = Σ_post Aᵀ / σ_obs² is constant and the
    O(h⁴) curvature term vanishes identically. Thus

        tr Cov_h(y) ≈ tr Σ_post + h² ‖J‖_F²        (eq. 15.2)

    Returns (predicted_trace, ‖J‖_F²).
    """
    Sigma_post = problem.Sigma_post.to(torch.float64)  # (d,d)
    A = problem.A.to(torch.float64)                    # (k,d)
    sigma_obs = float(problem.sigma_obs)
    J = Sigma_post @ A.T / (sigma_obs ** 2)            # (d,k)
    J_fro_sq = float((J ** 2).sum())
    trace_post = float(torch.trace(Sigma_post))
    return trace_post + (h ** 2) * J_fro_sq, J_fro_sq
