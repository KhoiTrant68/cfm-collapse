"""Pilot checks of the proposed theorem T1 (docs/plan/main_track_plan_2026-10-11.md, §6).

T1 models the label dependence of a trained conditional flow as a kernel learner of the
conditional moments f(y) = E[phi(X) | Y = y], started from the unconditional moments c.
Before proving anything, three questions:

A. ridge form: is the continuum equivalent kernel F^-1[1/(1+|w|^z)] a probability density?
   (Linnik: iff 0 < z <= 2.)
B. gradient-flow form: is F^-1[1 - exp(-|w|^-z)] a positive kernel?
C. on the real EXP-1 designs (k=1, h=0), kernel ridge regression of the atoms' moments:
   are the implied atom weights a probability vector (exponential kernel against
   Gaussian kernel), does one Gaussian Nadaraya-Watson bandwidth fit the implied moments,
   and does the per-condition bandwidth scale with the label density as p(y)^(-1/z), z=2?

Reads:  results/exp1/_heff/family_stats.npz (training sets of the heff_p7y runs)
Writes: results/theory/t1_equivalent_kernel.json
Usage:  uv run python scripts/theory_t1_equivalent_kernel.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

STATS = Path("results/exp1/_heff/family_stats.npz")
OUT = Path("results/theory/t1_equivalent_kernel.json")
RUNS = ("heff_p7y_h0_seed0", "heff_p7y_h0_seed1", "heff_p7y_h0_seed2")
LAMS = (1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
GRID = np.exp(np.linspace(np.log(2e-3), np.log(3.0), 300))


def inv_ft(transfer, w, u):
    """kappa(u) = (1/pi) int_0^inf cos(w u) T(w) dw for an even transfer T."""
    dw = w[1] - w[0]
    return np.array([np.sum(np.cos(w * x) * transfer) * dw / np.pi for x in u])


def kernels() -> dict:
    w = np.linspace(1e-6, 400, 400001)
    u = np.linspace(0, 12, 241)
    out = {}
    for z in (1.5, 2.0, 3.0, 4.0):
        k = inv_ft(1 / (1 + w ** z), w, u)
        out[f"ridge_z{z:g}"] = {"min": float(k.min()), "argmin_u": float(u[k.argmin()]),
                                "negative_share": float(-np.minimum(k, 0).sum() / np.abs(k).sum())}
    for z in (2.0, 4.0):
        k = inv_ft(1 - np.exp(-w ** (-z)), w, u)
        out[f"gradflow_z{z:g}"] = {"min": float(k.min()), "argmin_u": float(u[k.argmin()]),
                                   "negative_share": float(-np.minimum(k, 0).sum() / np.abs(k).sum())}
    return out


def nw_moments(X, Y, q, h):
    lw = -(q[:, None] - Y[None, :]) ** 2 / (2 * h * h)
    lw -= lw.max(1, keepdims=True)
    W = np.exp(lw)
    W /= W.sum(1, keepdims=True)
    return moments(W, X)


def moments(W, X):
    m = W @ X
    tr = (W * ((X[None] - m[:, None]) ** 2).sum(-1)).sum(1)
    return m, tr


def krr_weights(kern, Y, q, lam):
    """Weights over atoms of f(q) = c + k(q,Y)(K + N lam I)^-1 (phi(X) - c); rows sum to 1."""
    N = len(Y)
    S = kern(q[:, None], Y[None, :]) @ np.linalg.inv(kern(Y[:, None], Y[None, :]) + N * lam * np.eye(N))
    return S + (1 - S.sum(1, keepdims=True)) / N, S


def design(run: str, z) -> dict:
    X, Y = z[f"{run}/X"], z[f"{run}/Y"][:, 0]
    N, ell = len(Y), float(z[f"{run}/Y"][:, 0].std())
    expk = lambda a, b: np.exp(-np.abs(a - b) / ell)                       # spectrum ~ w^-2
    gauk = lambda a, b: np.exp(-(a - b) ** 2 / (2 * (0.3 * ell) ** 2))      # spectrum ~ e^-w^2
    q = np.quantile(Y, np.linspace(0.02, 0.98, 49))                        # across the density
    q_wide = np.linspace(Y.min() - 0.5, Y.max() + 0.5, 400)
    bw = 1.06 * Y.std() * N ** -0.2
    p_hat = np.exp(-(q[:, None] - Y[None, :]) ** 2 / (2 * bw * bw)).sum(1) / (N * bw * np.sqrt(2 * np.pi))
    ref = [nw_moments(X, Y, q, h) for h in GRID]
    ref_m, ref_t = np.stack([r[0] for r in ref]), np.stack([r[1] for r in ref])
    rows = []
    for lam in LAMS:
        Wd, _ = krr_weights(expk, Y, q_wide, lam)
        _, Sg = krr_weights(gauk, Y, q_wide, lam)
        W, _ = krr_weights(expk, Y, q, lam)
        m, tr = moments(W, X)
        lt = np.log(tr)
        se = ((lt[None] - np.log(np.maximum(ref_t, 1e-300))) ** 2).sum(1)
        g = int(se.argmin())
        hc = GRID[np.argmin(np.linalg.norm(ref_m - m[None], axis=2), axis=0)]
        inner = (hc > GRID[0] * 1.01) & (hc < GRID[-1] / 1.01)
        rows.append({
            "lam": lam,
            "median_n_eff": float(np.median(1 / (W ** 2).sum(1))),
            "exp_kernel_min_weight": float(Wd.min()),
            "gauss_kernel_negative_mass": float(-np.minimum(Sg, 0).sum(1).mean()),
            "one_bandwidth_r2": float(1 - se[g] / ((lt - lt.mean()) ** 2).sum()),
            "one_bandwidth_h": float(GRID[g]),
            "density_slope": float(np.polyfit(np.log(p_hat[inner]), np.log(hc[inner]), 1)[0])
            if inner.sum() > 5 else float("nan")})
    return {"N": N, "ell": ell, "rows": rows}


def main() -> None:
    z = np.load(STATS)
    out = {"kernels": kernels(), "designs": {r: design(r, z) for r in RUNS},
           "predicted_density_slope": -0.5}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, v in out["kernels"].items():
        print(f"  {k:14s} min {v['min']:+.4f} at u={v['argmin_u']:.2f}  negative share {v['negative_share']:.3f}")
    print("  run                lam     n_eff  min w(exp)  neg mass(gauss)  R2(one h)  h      slope")
    for r, dsg in out["designs"].items():
        for x in dsg["rows"]:
            print(f"  {r:18s} {x['lam']:7.0e} {x['median_n_eff']:6.1f}  {x['exp_kernel_min_weight']:+.1e}"
                  f"     {x['gauss_kernel_negative_mass']:.3f}          {x['one_bandwidth_r2']:+.3f}"
                  f"   {x['one_bandwidth_h']:.4f} {x['density_slope']:+.2f}")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
