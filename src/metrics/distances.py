"""Self-contained torch implementations of MMD and (entropic) Sinkhorn distance.

The spec suggests ``geomloss`` for these, but geomloss depends on KeOps which is
painful to build on Windows. For the sample sizes in EXP-1/EXP-2 (<= a few
thousand points) a plain O(n*m) torch implementation is fast enough and removes
a fragile dependency. If ``geomloss`` is installed, ``sinkhorn_distance`` will
prefer it for a cross-check.
"""
from __future__ import annotations

import torch

try:  # optional reference implementation
    from geomloss import SamplesLoss  # type: ignore
    _HAS_GEOMLOSS = True
except Exception:  # pragma: no cover - geomloss is optional
    _HAS_GEOMLOSS = False


def _pairwise_sq_dists(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    x2 = (x * x).sum(-1, keepdim=True)
    y2 = (y * y).sum(-1, keepdim=True).T
    return (x2 + y2 - 2.0 * x @ y.T).clamp_min(0.0)


def mmd_rbf(x: torch.Tensor, y: torch.Tensor,
            bandwidths: tuple[float, ...] | None = None) -> float:
    """Unbiased-ish multi-bandwidth RBF MMD^2. Median-heuristic if not given."""
    x = x.to(torch.float64)
    y = y.to(torch.float64)
    dxx = _pairwise_sq_dists(x, x)
    dyy = _pairwise_sq_dists(y, y)
    dxy = _pairwise_sq_dists(x, y)

    if bandwidths is None:
        with torch.no_grad():
            med = torch.median(dxy).clamp_min(1e-12)
        scales = (0.5, 1.0, 2.0)
        bandwidths = tuple(float(med) * s for s in scales)

    total = 0.0
    for h in bandwidths:
        kxx = torch.exp(-dxx / (2 * h))
        kyy = torch.exp(-dyy / (2 * h))
        kxy = torch.exp(-dxy / (2 * h))
        total += float(kxx.mean() + kyy.mean() - 2 * kxy.mean())
    return total / len(bandwidths)


def sinkhorn_distance(x: torch.Tensor, y: torch.Tensor,
                      blur: float = 0.05, p: int = 2,
                      n_iters: int = 200, prefer_geomloss: bool = True) -> float:
    """Entropic-regularized OT (Sinkhorn divergence-ish).

    Returns the debiased Sinkhorn divergence S(x,y) = OT(x,y) - 0.5 OT(x,x)
    - 0.5 OT(y,y), which is >= 0 and 0 iff x == y in distribution.
    """
    if prefer_geomloss and _HAS_GEOMLOSS:
        loss = SamplesLoss("sinkhorn", p=p, blur=blur)
        return float(loss(x.to(torch.float32), y.to(torch.float32)))

    def _ot(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        a = a.to(torch.float64)
        b = b.to(torch.float64)
        C = _pairwise_sq_dists(a, b)
        if p == 1:
            C = C.clamp_min(0).sqrt()
        n, m = C.shape
        eps = blur ** p
        mu = torch.full((n,), 1.0 / n, dtype=torch.float64)
        nu = torch.full((m,), 1.0 / m, dtype=torch.float64)
        u = torch.zeros(n, dtype=torch.float64)
        v = torch.zeros(m, dtype=torch.float64)
        log_mu = torch.log(mu)
        log_nu = torch.log(nu)
        K = -C / eps
        for _ in range(n_iters):
            u = eps * (log_mu - torch.logsumexp(K + v[None, :], dim=1)) + u
            v = eps * (log_nu - torch.logsumexp(K.T + u[None, :], dim=1)) + v
        P = torch.exp((K + u[:, None] + v[None, :]) / 1.0)  # not needed for cost
        # transport cost via dual: <u,mu> + <v,nu>
        return (u @ mu + v @ nu)

    ot_xy = _ot(x, y)
    ot_xx = _ot(x, x)
    ot_yy = _ot(y, y)
    return float((ot_xy - 0.5 * ot_xx - 0.5 * ot_yy).clamp_min(0.0))
