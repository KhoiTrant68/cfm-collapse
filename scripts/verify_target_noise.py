"""Population-level check of the endpoint-smoothing remedy (no training needed).

Theory. With the endpoint replaced by X_1 = x^I + rho*xi (xi ~ N(0,I_d), fresh
every step) and the label smoothed as usual, the same mixture-coupling argument
that gives Theorem 1 yields the population endpoint law

    p_1(. | y) = sum_i p_i^(h)(y) N(x^i, rho^2 I_d),          (*)

which is absolutely continuous for every rho > 0. Proposition 6's Wasserstein
floor -- which holds for *any* law supported on {x^1..x^N} and does not depend
on h -- therefore does not apply.

This script evaluates (*) directly, so it measures what the *population
optimum* can achieve, independently of whether SGD gets there. It sweeps
(h, rho) and reports MMD / Sinkhorn / trace-covariance against the analytic
Gaussian posterior, with rho=0 reproducing the atomic baseline of the paper.

    uv run python scripts/verify_target_noise.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.distances import mmd_rbf, sinkhorn_distance  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

HS = [0.0, 0.01, 0.05, 0.1, 0.5]
RHOS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
M = 800
N_COND = 8
# Sinkhorn is O(M^2) per call and dominates a 30-cell sweep; compute it only for
# the cells the paper quotes.
SINKHORN_CELLS = {(0.0, 0.0), (0.1, 0.0), (0.5, 0.0),
                  (0.1, 0.1), (0.1, 0.2), (0.1, 0.3), (0.05, 0.2), (0.5, 0.2)}


def label_weights(y, Y, h):
    """p_i^(h)(y) proportional to K_h(y - y^i); h=0 -> nearest-label indicator."""
    d2 = ((Y - y[None, :]) ** 2).sum(-1)
    if h <= 0:
        w = torch.zeros_like(d2)
        w[int(torch.argmin(d2))] = 1.0
        return w
    logits = -d2 / (2 * h * h)
    return torch.softmax(logits - logits.max(), dim=0)


def sample_endpoint(w, X, rho, M, gen):
    """Draw M samples from sum_i w_i N(x^i, rho^2 I)."""
    idx = torch.multinomial(w, M, replacement=True, generator=gen)
    s = X[idx].clone()
    if rho > 0:
        s = s + rho * torch.randn(s.shape, generator=gen)
    return s


def main():
    cfg = load_yaml("configs/exp1_linear_gaussian.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(
        d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
        prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    X = X.to(torch.float64); Y = Y.to(torch.float64)
    Sig = prob.Sigma_post.to(torch.float64)
    L = torch.linalg.cholesky(Sig)


    idx = torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()
    print(f"trace(Sigma_post) = {float(torch.trace(Sig)):.4f}   "
          f"conditions = {idx}\n")
    print(f"{'h':>5} {'rho':>5} {'MMD':>9} {'Sinkhorn':>9} {'trCov':>8} "
          f"{'|mean-mu|':>10}")
    print("-" * 52)

    results = {}
    for h in HS:
        for rho in RHOS:
            do_sink = (h, rho) in SINKHORN_CELLS
            mmds, sinks, trcs, merr = [], [], [], []
            for i in idx:
                y = Y[i]
                w = label_weights(y, Y, h)
                gen_i = torch.Generator().manual_seed(1000 + i)
                s = sample_endpoint(w, X, rho, M, gen_i)
                mu = prob.posterior_mean(y).to(torch.float64)
                ref = mu[None, :] + torch.randn(M, prob.d, generator=gen_i,
                                                dtype=torch.float64) @ L.T
                mmds.append(mmd_rbf(s.float(), ref.float()))
                if do_sink:
                    sinks.append(sinkhorn_distance(s.float(), ref.float()))
                trcs.append(float(s.var(0, unbiased=False).sum()))
                merr.append(float(torch.linalg.norm(s.mean(0) - mu)))
            mm = sum(mmds) / len(mmds)
            sk = (sum(sinks) / len(sinks)) if sinks else float("nan")
            tc = sum(trcs) / len(trcs); me = sum(merr) / len(merr)
            results[(h, rho)] = (mm, sk, tc, me)
            sks = f"{sk:>9.3f}" if sinks else f"{'-':>9}"
            print(f"{h:>5} {rho:>5} {mm:>9.4f} {sks} {tc:>8.3f} {me:>10.4f}",
                  flush=True)
        print(flush=True)

    best = min(results, key=lambda k: results[k][0])
    base = min((k for k in results if k[1] == 0.0), key=lambda k: results[k][0])
    print(f"best overall      : h={best[0]}, rho={best[1]}  MMD={results[best][0]:.4f}")
    print(f"best atomic (rho=0): h={base[0]}, rho=0    MMD={results[base][0]:.4f}")
    print(f"reduction factor  : {results[base][0] / max(results[best][0], 1e-12):.1f}x")


if __name__ == "__main__":
    main()
