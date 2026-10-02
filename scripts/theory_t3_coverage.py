"""T3: calibration of the kernel reference law as a function of bandwidth (linear-Gaussian).

Model: x ~ N(mu_x, Sigma_x), y = A x + eta, eta ~ N(0, sigma^2 I).

T3.a  For fixed h, as N -> infinity the Nadaraya-Watson mixture at bandwidth h converges
      to the posterior of x given a label observed with noise variance s_h^2 = sigma^2 + h^2:
      Sigma_h = (Sigma_x^-1 + A^T A / s_h^2)^-1,  mu_h(y) = Sigma_h (Sigma_x^-1 mu_x + A^T y / s_h^2).
T3.b  For (x*, y*) drawn from the model, z = x* - mu_h(y*) ~ N(0, V_h) with
      V_h = Sigma_post + B_h Cov(y) B_h^T,  B_h = Sigma_post A^T/sigma^2 - Sigma_h A^T/s_h^2,
      Cov(y) = A Sigma_x A^T + sigma^2 I; the level-alpha region of N(mu_h, Sigma_h) covers
      x* with probability P[z^T Sigma_h^-1 z <= q_alpha].
T3.c  For fixed weights w and i.i.d. atoms with mean m and covariance S, the weighted mean
      has covariance S sum w^2 = S / n_eff and the weighted covariance has expectation
      (1 - 1/n_eff) S. With the atoms near y modelled as draws of the smoothed posterior,
      coverage(h, n_eff) = P[z^T ((1 - 1/n_eff) Sigma_h)^-1 z <= q_alpha],
      z ~ N(0, V_h + Sigma_h / n_eff).

The script checks T3.a-c by simulation, then predicts the held-out coverage of every
trained synthetic checkpoint from its h_eff alone, in two ways: the formula T3.c with
the n_eff that h_eff implies at each held-out condition, and the exact coverage of the
finite reference law at h_eff (its exact moments over the training atoms). Both are
compared with the measured coverage (results/exp1/_heff/audit_calibration_v2.json).

Writes: results/theory/t3_coverage.json, paper/figures/fig_t3_coverage.png
Usage:  PYTHONPATH=. uv run python scripts/theory_t3_coverage.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from scripts.audit_calibration_v2 import chi2_quantile
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

OUT = Path("results/theory/t3_coverage.json")
N_TEST = 100
MC = 400_000
ALPHAS = (0.5, 0.9)


def problem(seed):
    dc = load_yaml("configs/exp1_linear_gaussian.yaml")["data"]
    p = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=seed,
                                     prior_std=dc.get("prior_std", 1.0),
                                     A_kind=dc.get("A_kind", "random"))
    X, Y = p.sample_dataset(dc["N"], seed=seed + 1)
    return p, X.double(), Y.double()


def smoothed(p, h):
    """Sigma_h and the map y -> mu_h(y) of T3.a."""
    s2 = p.sigma_obs ** 2 + h ** 2
    Sx_inv = torch.linalg.inv(p.Sigma_x)
    Sh = torch.linalg.inv(Sx_inv + p.A.T @ p.A / s2)
    return Sh, (lambda y: (Sh @ ((Sx_inv @ p.mu_x)[:, None] + p.A.T @ y.T / s2)).T)


def V_of(p, h):
    s2 = p.sigma_obs ** 2 + h ** 2
    Sh, _ = smoothed(p, h)
    B = p.Sigma_post @ p.A.T / p.sigma_obs ** 2 - Sh @ p.A.T / s2
    covy = p.A @ p.Sigma_x @ p.A.T + p.sigma_obs ** 2 * torch.eye(p.k, dtype=torch.float64)
    return p.Sigma_post + B @ covy @ B.T, Sh


def gchi2_cdf(Z, C, q):
    """P[z^T C^-1 z <= q] for z ~ N(0, Z), by Monte Carlo on the eigenvalues."""
    L = torch.linalg.cholesky(C)
    Li = torch.linalg.inv(L)
    lam = torch.linalg.eigvalsh(Li @ Z @ Li.T).clamp_min(0).numpy()
    g = np.random.default_rng(0).standard_normal((MC, len(lam)))
    return float(np.mean((g ** 2 @ lam) <= q))


def coverage_theory(p, h, n_eff, alpha):
    V, Sh = V_of(p, h)
    q = chi2_quantile(alpha, p.d)
    if not np.isfinite(n_eff):
        return gchi2_cdf(V, Sh, q)
    return gchi2_cdf(V + Sh / n_eff, (1 - 1 / n_eff) * Sh, q)


def coverage_local_model(p, h, W, alpha, n_mc=800, top=40, seed=0):
    """Exact coverage under the local model, with the sampling of the atoms kept.

    Atoms a_i ~ N(mu_h, Sigma_h) i.i.d., weighted by the actual kernel weights w of each
    held-out condition (top `top` weights, renormalised); x* - mu_h ~ N(0, V_h)
    independent of them. The region is the level-alpha Mahalanobis region of the
    weighted sample moments, as for a trained model. Averaged over the conditions.
    """
    V, Sh = V_of(p, h)
    q = chi2_quantile(alpha, p.d)
    rng = np.random.default_rng(seed)
    Ls, Lv = np.linalg.cholesky(Sh.numpy()), np.linalg.cholesky(V.numpy())
    covs = []
    for w in W:
        w = np.sort(w.numpy())[::-1][:top]
        w = w / w.sum()
        a = rng.standard_normal((n_mc, len(w), p.d)) @ Ls.T                  # atoms - mu_h
        m = np.einsum("i,nid->nd", w, a)
        dev = a - m[:, None, :]
        C = np.einsum("i,nid,nie->nde", w, dev, dev) + 1e-12 * np.eye(p.d)
        z = rng.standard_normal((n_mc, p.d)) @ Lv.T - m                        # x* - weighted mean
        d2 = np.einsum("nd,nd->n", z, np.linalg.solve(C, z[..., None])[..., 0])
        covs.append(np.mean(d2 <= q))
    return float(np.mean(covs))


def main() -> None:
    torch.set_default_dtype(torch.float64)
    out = {}
    p, X, Y = problem(0)

    # ---- T3.a: large-N Nadaraya-Watson mixture against the closed form ---------------
    g = torch.Generator().manual_seed(7)
    Xb = p.sample_prior(400_000, generator=g); Yb = p.forward(Xb, generator=g)
    ya = []
    for h in (0.1, 0.3, 1.0):
        y0 = Yb[:5]
        W = torch.softmax(-torch.cdist(y0, Yb) ** 2 / (2 * h * h), dim=1)
        m = W @ Xb
        Sh, mu = smoothed(p, h)
        cov_err = max(float(torch.linalg.norm(((W[c][:, None] * (Xb - m[c])).T @ (Xb - m[c])) - Sh)
                            / torch.linalg.norm(Sh)) for c in range(5))
        ya.append({"h": h, "mean_err": float((m - mu(y0)).norm(dim=1).max()),
                   "cov_rel_err": cov_err})
    out["t3a"] = ya
    print("T3.a large-N NW vs closed form:", [(r["h"], f"{r['mean_err']:.3f}", f"{r['cov_rel_err']:.3f}")
                                             for r in ya])

    # ---- T3.b: Monte Carlo coverage of N(mu_h, Sigma_h) against the formula -----------
    gb = torch.Generator().manual_seed(11)
    xs = p.sample_prior(200_000, generator=gb); ys = p.forward(xs, generator=gb)
    tb = []
    for h in (0.0, 0.1, 0.3, 1.0):
        Sh, mu = smoothed(p, h)
        z = xs - mu(ys)
        d2 = (z @ torch.linalg.inv(Sh) * z).sum(1)
        for a in ALPHAS:
            q = chi2_quantile(a, p.d)
            tb.append({"h": h, "alpha": a, "mc": float((d2 <= q).double().mean()),
                       "formula": coverage_theory(p, h, float("inf"), a)})
    out["t3b"] = tb
    print("T3.b coverage MC vs formula:",
          [(r["h"], r["alpha"], f"{r['mc']:.3f}", f"{r['formula']:.3f}") for r in tb])

    # ---- T3.c: weighted moments of i.i.d. atoms --------------------------------------
    gc = np.random.default_rng(3)
    w = gc.dirichlet(np.ones(12) * 0.3); n_eff = 1 / np.sum(w ** 2)
    S = np.array([[1.0, 0.3], [0.3, 0.5]])
    covs, means = [], []
    for _ in range(40_000):
        a = gc.multivariate_normal(np.zeros(2), S, size=12)
        mbar = w @ a
        means.append(mbar); covs.append((w[:, None] * (a - mbar)).T @ (a - mbar))
    out["t3c"] = {"n_eff": float(n_eff),
                  "E_cov_over_S": float(np.mean(covs, 0)[0, 0] / S[0, 0]),
                  "pred_E_cov_over_S": float(1 - 1 / n_eff),
                  "Var_mean_over_S": float(np.var(np.array(means)[:, 0]) / S[0, 0]),
                  "pred_Var_mean_over_S": float(1 / n_eff)}
    print("T3.c identities:", {k: round(v, 4) for k, v in out["t3c"].items()})

    # ---- T3.d: predict the measured coverage of trained models from h_eff -------------
    rows = json.loads(Path("results/exp1/_heff/audit_calibration_v2.json").read_text(encoding="utf-8"))
    probs, cache = {}, {}
    preds = []
    for r in rows:
        s = r["seed"]
        if s not in probs:
            pp, Xs, Ys = problem(s)
            g_t = torch.Generator().manual_seed(s + 31337)
            Xt = pp.sample_prior(N_TEST, generator=g_t); Yt = pp.forward(Xt, generator=g_t)
            probs[s] = (pp, Xs, Ys, Xt, Yt)
        pp, Xs, Ys, Xt, Yt = probs[s]
        h = r["h_eff"]
        W = torch.softmax(-torch.cdist(Yt, Ys) ** 2 / (2 * h * h), dim=1)          # (100, N)
        neff = (1 / (W ** 2).sum(1)).numpy()
        m = W @ Xs
        rec = {"run": r["run"], "iter": r["iter"], "h": r["h"], "h_eff": h,
               "n_eff_median": float(np.median(neff))}
        for a in ALPHAS:
            q = chi2_quantile(a, pp.d)
            # exact coverage of the finite reference law at h_eff (its exact moments)
            inside = []
            for j in range(N_TEST):
                C = ((W[j][:, None] * (Xs - m[j])).T @ (Xs - m[j])) + 1e-12 * torch.eye(pp.d)
                z = Xt[j] - m[j]
                inside.append(float(z @ torch.linalg.solve(C, z)) <= q)
            rec[f"ref_cov_{int(a*100)}"] = float(np.mean(inside))
            # theory T3.c, averaged over the n_eff of the held-out conditions
            key = (s, round(np.log(h), 3), a)
            if key not in cache:
                bins = np.quantile(neff, [0.1, 0.3, 0.5, 0.7, 0.9])
                cache[key] = float(np.mean([coverage_theory(pp, h, max(b, 1.0001), a) for b in bins]))
            rec[f"theory_cov_{int(a*100)}"] = cache[key]
            rec[f"local_cov_{int(a*100)}"] = coverage_local_model(pp, h, W[:25], a)
            rec[f"measured_cov_{int(a*100)}"] = r[f"test_coverage_{int(a*100)}"]
        preds.append(rec)

    def score(a, b):
        a, b = np.asarray(a), np.asarray(b)
        rk = lambda v: np.argsort(np.argsort(v))
        return {"mae": float(np.mean(np.abs(a - b))),
                "r2": float(1 - np.sum((b - a) ** 2) / np.sum((b - b.mean()) ** 2)),
                "spearman": float(np.corrcoef(rk(a), rk(b))[0, 1])}

    summ = {}
    for a in (50, 90):
        meas = [x[f"measured_cov_{a}"] for x in preds]
        summ[f"theory_vs_measured_{a}"] = score([x[f"theory_cov_{a}"] for x in preds], meas)
        summ[f"reference_vs_measured_{a}"] = score([x[f"ref_cov_{a}"] for x in preds], meas)
        summ[f"theory_vs_reference_{a}"] = score([x[f"theory_cov_{a}"] for x in preds],
                                                 [x[f"ref_cov_{a}"] for x in preds])
        summ[f"local_model_vs_measured_{a}"] = score([x[f"local_cov_{a}"] for x in preds], meas)
        summ[f"local_model_vs_reference_{a}"] = score([x[f"local_cov_{a}"] for x in preds],
                                                      [x[f"ref_cov_{a}"] for x in preds])
    out["t3d"] = {"summary": summ, "rows": preds}
    for k, v in summ.items():
        print(f"T3.d {k:<28} MAE {v['mae']:.3f}  R2 {v['r2']:.3f}  Spearman {v['spearman']:.3f}")

    # ---- curve: theory coverage against bandwidth for seed 0 --------------------------
    hs = np.exp(np.linspace(np.log(0.004), np.log(1.5), 40))
    curve = []
    pp0, Xs0, Ys0, Xt0, Yt0 = probs[0]
    for h in hs:
        W = torch.softmax(-torch.cdist(Yt0, Ys0) ** 2 / (2 * h * h), dim=1)
        ne = float(np.median((1 / (W ** 2).sum(1)).numpy()))
        curve.append({"h": float(h), "n_eff": ne,
                      "cov90_theory": coverage_theory(pp0, float(h), max(ne, 1.0001), 0.9),
                      "cov90_infinite_N": coverage_theory(pp0, float(h), float("inf"), 0.9)})
    out["curve_seed0"] = curve
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
