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
        """Entropic OT cost via the log-domain Sinkhorn dual.

        The potentials f, g are carried in *cost* units, so the exponent is
        (f + g - C)/eps and the dual value is <f,mu> + <g,nu>. An earlier version
        mixed the two conventions -- it added a raw-unit potential to -C/eps
        inside the logsumexp -- which made the returned number unrelated to the
        transport cost: two identical Gaussians scored 3.34 and a point mass
        against a Gaussian scored 0. The three closed forms in
        scripts/verify_sinkhorn.py pin this down.

        eps-scaling: at the eps this paper needs (blur 0.1, p 2 -> eps 1e-2) a
        fixed-eps iteration converges too slowly to be trusted at 200 steps, so
        anneal eps down to its target and spend the iterations where they count.
        """
        a = a.to(torch.float64)
        b = b.to(torch.float64)
        C = _pairwise_sq_dists(a, b)
        if p == 1:
            C = C.clamp_min(0).sqrt()
        n, m = C.shape
        eps_target = blur ** p
        log_mu = torch.full((n,), -float(torch.tensor(float(n)).log()), dtype=torch.float64)
        log_nu = torch.full((m,), -float(torch.tensor(float(m)).log()), dtype=torch.float64)
        mu, nu = log_mu.exp(), log_nu.exp()

        f = torch.zeros(n, dtype=torch.float64)
        g = torch.zeros(m, dtype=torch.float64)
        eps0 = max(float(C.max()), eps_target)
        n_anneal = max(1, n_iters // 4)
        schedule = torch.logspace(
            float(torch.tensor(eps0).log10()), float(torch.tensor(eps_target).log10()),
            n_anneal, dtype=torch.float64)
        for k in range(n_iters):
            eps = float(schedule[min(k, n_anneal - 1)])
            f = -eps * torch.logsumexp((g[None, :] - C) / eps + log_nu[None, :], dim=1)
            g = -eps * torch.logsumexp((f[:, None] - C) / eps + log_mu[:, None], dim=0)
        return f @ mu + g @ nu

    ot_xy = _ot(x, y)
    ot_xx = _ot(x, x)
    ot_yy = _ot(y, y)
    return float((ot_xy - 0.5 * ot_xx - 0.5 * ot_yy).clamp_min(0.0))
