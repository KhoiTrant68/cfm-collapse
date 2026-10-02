"""Theorem calib beyond Gaussian posteriors: a prior-free calibration bound.

Claim (any prior pi, any forward map g, y = g(x) + eta, eta ~ N(0, sigma^2 I_k)):
for any rule R(y) of regions, |P(X in R(Y)) - P(X in R(Y~))| <= TV, with Y~ = Y + h eps and
TV = TV(N(0, sigma^2 I_k), N(0, (sigma^2 + h^2) I_k)), which does not depend on pi or g.
If R(y) is a level-alpha credible region of the smoothed posterior pi_h(. | y) = law(X | Y~ = y)
(the infinite-data reference law), then P(X in R(Y~)) = alpha, so the reference law's coverage
at clean labels is within TV of alpha.

Check on the Gaussian-mixture problems (EXP-2: d = 2 with an information-losing projection, and
d = 8): exact highest-density regions of the mixture pi_h, coverage at clean and at noisy
labels, against the exact TV and its Pinsker bound.

Writes: results/theory/t3_general.json
Usage:  PYTHONPATH=. uv run --with scipy python scripts/theory_t3_general.py
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import numpy as np
import torch
from scipy.stats import chi2

from src.problems.gmm import GMMProblem, _mvn_logpdf

OUT = Path("results/theory/t3_general.json")


def tv_gauss(k, sigma, h):
    """Exact TV between N(0, sigma^2 I_k) and N(0, s^2 I_k), s^2 = sigma^2 + h^2."""
    if h == 0:
        return 0.0
    s2, v2 = sigma ** 2 + h ** 2, sigma ** 2
    c = k * v2 * s2 * math.log(s2 / v2) / (s2 - v2)     # |z|^2 where the densities cross
    return float(chi2.cdf(c / v2, k) - chi2.cdf(c / s2, k))


def pinsker(k, sigma, h):
    r = sigma ** 2 / (sigma ** 2 + h ** 2)
    return math.sqrt(k / 4 * (r - 1 - math.log(r)))


def log_mix(x, w, mus, covs):
    lp = torch.stack([_mvn_logpdf(x, mus[j], covs[j]) for j in range(len(w))], 1)
    return torch.logsumexp(lp + torch.log(w)[None], 1)


def coverage(p, h, alphas, n_pairs=1000, n_mc=3000, seed=0):
    g = torch.Generator().manual_seed(seed)
    ph = copy.copy(p); ph.sigma_obs = math.hypot(p.sigma_obs, h)
    X = p.sample_prior(n_pairs, generator=g); Y = p.forward(X, generator=g)
    Yn = Y + h * torch.randn(Y.shape, generator=g, dtype=torch.float64)
    hits = {"clean": {a: 0 for a in alphas}, "noisy": {a: 0 for a in alphas}}
    for i in range(n_pairs):
        for tag, y in (("clean", Y[i]), ("noisy", Yn[i])):
            w, mus, covs = ph.posterior_params(y)
            S = ph.sample_posterior(y, n_mc, generator=g)
            ls = log_mix(S, w, mus, covs)
            lx = float(log_mix(X[i:i + 1], w, mus, covs)[0])
            for a in alphas:                       # HPD region: log density above quantile
                if lx >= float(torch.quantile(ls, 1 - a)):
                    hits[tag][a] += 1
    return {tag: {str(a): v / n_pairs for a, v in d.items()} for tag, d in hits.items()}


def main() -> None:
    torch.set_default_dtype(torch.float64)
    out = []
    alphas = (0.5, 0.9)
    for name, kw in (("gmm_d2", dict(d=2, k=1, sigma_obs=0.2, A_kind="project_x0")),
                     ("gmm_d8", dict(d=8, k=2, sigma_obs=0.2, A_kind="random", seed=0))):
        p = GMMProblem.create(**kw)
        for ratio in (0.0, 0.5, 1.0, 2.0, 4.0):
            h = ratio * p.sigma_obs
            cov = coverage(p, h, alphas, seed=int(ratio * 10))
            rec = {"problem": name, "h_over_sigma": ratio, "k": p.k,
                   "tv_exact": tv_gauss(p.k, p.sigma_obs, h),
                   "tv_pinsker": pinsker(p.k, p.sigma_obs, h), **cov}
            rec["max_dev_clean"] = max(abs(cov["clean"][str(a)] - a) for a in alphas)
            rec["max_dev_noisy"] = max(abs(cov["noisy"][str(a)] - a) for a in alphas)
            out.append(rec)
            print(f"{name} h/sigma={ratio}: clean {cov['clean']} noisy {cov['noisy']} "
                  f"TV {rec['tv_exact']:.3f} (Pinsker {rec['tv_pinsker']:.3f})")
    n = 1000
    ok = True
    for r in out:
        r["diff"] = {str(a): abs(r["clean"][str(a)] - r["noisy"][str(a)]) for a in alphas}
        r["noisy_max_dev"] = r["max_dev_noisy"]
        ok &= all(r["diff"][str(a)] <= r["tv_exact"] + 3 * math.sqrt(2 * a * (1 - a) / n)
                  for a in alphas)
    summ = {"bound_holds_within_3se": bool(ok),
            "check": "|clean - noisy| <= TV + 3 se(diff), se(diff)=sqrt(2a(1-a)/n)",
            "max_noisy_dev_from_alpha": max(r["max_dev_noisy"] for r in out), "rows": out}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(f"|clean - noisy| <= TV + 3 s.e. everywhere: {ok}. Saved: {OUT}")


if __name__ == "__main__":
    main()
