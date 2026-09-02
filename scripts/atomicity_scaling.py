"""When does the atomicity obstruction actually bite, and when does endpoint
smoothing help?

Prop atomicity says the endpoint law of *any* label-smoothed CFM is supported on
{x^1..x^N}, giving W2^2 >= F(y) := INT dist(x,{x^i})^2 p(x|y) dx, independent of
h. That is exact, but its *magnitude* is a property of how densely the N atoms
cover the posterior: F ~ N^{-2/d} for a fixed posterior. So the obstruction is
negligible when the atoms are dense (small d, large N) and dominant when they
are sparse (large d, small N).

This script measures F/tr(Sigma_post) across (d, N) and, in the same sweep,
compares the best achievable MMD of an atomic endpoint law against the best
achievable MMD once the endpoint is smoothed (X_1 = x^i + rho*xi). Everything
is computed from the *population* endpoint laws, so it bounds what any trained
model could do and is independent of optimisation.

    uv run python scripts/atomicity_scaling.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.distances import mmd_rbf, sinkhorn_distance  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402

HS = [0.01, 0.05, 0.1, 0.3, 0.5, 1.0]
RHOS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8]
# Sinkhorn is O(M^2) and ~100x costlier than MMD, so the OT column uses a coarser
# grid. It is the metric that matters here: an entropic OT divergence sees the
# atomic support that an RBF MMD at the median-heuristic bandwidth cannot.
HS_OT = [0.05, 0.1, 0.5]
RHOS_OT = [0.0, 0.1, 0.2, 0.3]
GRID = [(2, 50), (2, 200), (2, 1000), (5, 200), (10, 200), (10, 50)]
M = 800
M_OT = 400
N_COND = 6
N_COND_OT = 4
SEED = 0


def label_weights(y, Y, h):
    d2 = ((Y - y[None, :]) ** 2).sum(-1)
    logits = -d2 / (2 * h * h)
    return torch.softmax(logits - logits.max(), dim=0)


def main():
    print(f"{'d':>3} {'N':>5} {'trSig':>7} {'floor F':>9} {'F/trSig':>8} "
          f"{'MMD atomic':>11} {'MMD +rho':>9} {'rho*':>5} {'gain':>6}")
    print("-" * 72)
    for d, N in GRID:
        prob = LinearGaussianProblem.create(d=d, k=1, sigma_obs=0.1, seed=SEED,
                                            prior_std=1.0, A_kind="random")
        X, Y = prob.sample_dataset(N, seed=SEED + 1)
        X = X.double(); Y = Y.double()
        Sig = prob.Sigma_post.double()
        L = torch.linalg.cholesky(Sig)
        tr = float(torch.trace(Sig))
        idx = torch.linspace(0, N - 1, N_COND).round().long().tolist()

        floors, best_at, best_rh, best_rho = [], [], [], []
        for i in idx:
            y = Y[i]
            mu = prob.posterior_mean(y).double()
            g = torch.Generator().manual_seed(500 + i)
            ref = mu[None, :] + torch.randn(M, d, generator=g, dtype=torch.float64) @ L.T
            # exact atomicity floor at this y
            floors.append(float((torch.cdist(ref, X) ** 2).min(1).values.mean()))

            cell = {}
            for h in HS:
                w = label_weights(y, Y, h)
                sel = torch.multinomial(w, M, replacement=True, generator=g)
                base = X[sel]
                for rho in RHOS:
                    s = base + rho * torch.randn(base.shape, generator=g,
                                                 dtype=torch.float64) if rho > 0 else base
                    cell[(h, rho)] = mmd_rbf(s.float(), ref.float())
            at = min(v for (h, r), v in cell.items() if r == 0.0)
            rh_key = min(cell, key=cell.get)
            best_at.append(at); best_rh.append(cell[rh_key]); best_rho.append(rh_key[1])

        # ---- OT column: same comparison in a metric that sees the support ----
        ot_at, ot_rh = [], []
        for i in idx[:N_COND_OT]:
            y = Y[i]
            mu = prob.posterior_mean(y).double()
            g = torch.Generator().manual_seed(900 + i)
            ref = mu[None, :] + torch.randn(M_OT, d, generator=g, dtype=torch.float64) @ L.T
            cell = {}
            for h in HS_OT:
                w = label_weights(y, Y, h)
                sel = torch.multinomial(w, M_OT, replacement=True, generator=g)
                base = X[sel]
                for rho in RHOS_OT:
                    s = base + rho * torch.randn(base.shape, generator=g,
                                                 dtype=torch.float64) if rho > 0 else base
                    cell[(h, rho)] = sinkhorn_distance(s.float(), ref.float())
            ot_at.append(min(v for (h, r), v in cell.items() if r == 0.0))
            ot_rh.append(min(cell.values()))

        F = sum(floors) / len(floors)
        a = sum(best_at) / len(best_at)
        r = sum(best_rh) / len(best_rh)
        oa = sum(ot_at) / len(ot_at)
        orr = sum(ot_rh) / len(ot_rh)
        rho_star = max(set(best_rho), key=best_rho.count)
        print(f"{d:>3} {N:>5} {tr:>7.3f} {F:>9.4f} {F/tr:>8.4f} "
              f"{a:>11.4f} {r:>9.4f} {rho_star:>5} {a/max(r,1e-12):>5.2f}x "
              f"| OT {oa:>8.2f} {orr:>8.2f} {oa/max(orr,1e-12):>5.2f}x",
              flush=True)

    print("\nfloor F is the exact bound of eq (w2floor); MMD columns are the best")
    print("achievable over h (atomic) and over (h,rho) (smoothed endpoint).")


if __name__ == "__main__":
    main()
