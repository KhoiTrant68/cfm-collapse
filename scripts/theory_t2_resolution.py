"""T2: where the effective bandwidth comes from -- a spectral-bias model in label space.

Model. The trained field depends on the label y only through conditional moments of the
endpoint, E[phi(X) | Y~ = y], phi in {x, |x|^2}. A model with spectral bias learns these
functions of y by kernel gradient flow in L2(rho_h), rho_h the law of the smoothed label
Y~ = Y + h eps, started from the unconditional moments c = E[phi(X)]:

    f_t = c + (I - exp(-t T_k)) (f* - c),   (T_k g)(y) = E_rho[k(y, Z) g(Z)],

with f* the exact Nadaraya-Watson moments at bandwidth h (Theorem endpoint). Nothing is
trained: f_t is computed exactly from the eigendecomposition of the kernel on rho_h
(Gauss-Hermite nodes around each training label). At each t we read the per-condition
variance tr Cov_t = S_t - |m_t|^2 and mean m_t at the 20 EXP-1 conditions and fit h_eff and
h_mean with the estimator of the paper (eq. heff).

Questions. (1) Is the model at every t a Nadaraya-Watson mixture at one bandwidth
(h_mean ~ h_eff, log-trace fit R^2)? (2) Does h_eff fall with t and stop at h? (3) Which
law h_eff^p = h^p + s(t)^p does it follow, and how does s(t) scale with t, for kernels
of different spectral decay (Gaussian: exponential; Matern-3/2: |w|^-4; Laplace: |w|^-2)?
These are compared with the trained networks (p = 1.3; s falls ~10x per decade of
iterations between 1e4 and 1e5, results/_heff_law.json).

Writes: results/theory/t2_resolution.json
Usage:  PYTHONPATH=. uv run python scripts/theory_t2_resolution.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from scripts.theory_t1_check import lg_problem

OUT = Path("results/theory/t2_resolution.json")
GRID = np.exp(np.linspace(np.log(3e-3), np.log(5.0), 240))
HS = (0.0, 0.01, 0.05, 0.1)
TS = np.exp(np.linspace(np.log(1e0), np.log(1e7), 29))
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(15)       # nodes for N(0, 1)
GH_W = GH_W / GH_W.sum()


def kern(kind, a, b, ell):
    r = np.abs(a[:, None] - b[None, :]) / ell
    if kind == "gaussian":
        return np.exp(-0.5 * r ** 2)
    if kind == "matern32":
        return (1 + np.sqrt(3) * r) * np.exp(-np.sqrt(3) * r)
    if kind == "laplace":
        return np.exp(-r)
    raise ValueError(kind)


def nw(Yq, Y, X, h):
    """Nadaraya-Watson weights at bandwidth h (h = 0: nearest training label)."""
    D = (Yq[:, None] - Y[None, :]) ** 2
    if h == 0:
        P = (D == D.min(1, keepdims=True)).astype(float)
        return P / P.sum(1, keepdims=True)
    L = -D / (2 * h * h)
    L -= L.max(1, keepdims=True)
    P = np.exp(L)
    return P / P.sum(1, keepdims=True)


def reference(X, Y, Q, grid):
    tr = np.empty((len(grid), len(Q))); mu = np.empty((len(grid), len(Q), X.shape[1]))
    for g, hp in enumerate(grid):
        P = nw(Q, Y, X, hp)
        mu[g] = P @ X
        tr[g] = (P * ((X[None] - mu[g][:, None]) ** 2).sum(-1)).sum(1)
    return tr, mu


def fit(tr_ref, mu_ref, T, m):
    ok = T > 0
    se = ((np.log(T[ok])[None] - np.log(tr_ref[:, ok])) ** 2).sum(1)
    g = int(np.argmin(se))
    me = np.linalg.norm(m[None] - mu_ref, axis=2).mean(1)
    gm = int(np.argmin(me))
    ly = np.log(T[ok]); r2 = 1 - se[g] / ((ly - ly.mean()) ** 2).sum()
    return GRID[g], GRID[gm], float(r2), int(ok.sum())


def flow(kind, ell, X, Y, Q, h):
    """Exact kernel gradient flow of the conditional moments, evaluated at Q for all TS."""
    if h == 0:
        Z, w = Y.copy(), np.full(len(Y), 1 / len(Y))
    else:
        Z = (Y[:, None] + h * GH_X[None]).ravel()
        w = np.repeat(GH_W[None], len(Y), 0).ravel() / len(Y)
    P = nw(Z, Y, X, h)
    F = np.concatenate([P @ X, (P @ (X ** 2).sum(1))[:, None]], 1)   # f*(Z): m, S
    c = (w[:, None] * F).sum(0)
    R = F - c
    sw = np.sqrt(w)
    B = sw[:, None] * kern(kind, Z, Z, ell) * sw[None]
    lam, U = np.linalg.eigh(B)
    lam = np.clip(lam, 0, None)
    proj = U.T @ (sw[:, None] * R)                                  # (M, 3)
    KQ = kern(kind, Q, Z, ell) * sw[None]                           # (C, M)
    KU = KQ @ U
    out = []
    for t in TS:
        gain = np.where(lam > 1e-14, -np.expm1(-t * lam) / np.maximum(lam, 1e-300), t)
        Ft = c + KU @ (gain[:, None] * proj)
        m, S = Ft[:, :2], Ft[:, 2]
        out.append((m, S - (m ** 2).sum(1)))
    return out


def power_law(rows):
    """Fit h_eff^p = h^p + s(t)^p, s(t) = h_eff at h = 0, one p for all t."""
    def loss(p):
        e = [np.log(r["h_eff"]) - np.log(r["h"] ** p + r["s"] ** p) / p for r in rows]
        return float(np.mean(np.square(e)))
    res = minimize_scalar(loss, bounds=(0.5, 4.0), method="bounded")
    add = loss(2.0)
    return float(res.x), float(np.sqrt(res.fun)), float(np.sqrt(add))


def slope(ts, ss, lo, hi):
    """log-log slope of s(t) where s falls from lo*s0-ish: between the given s levels."""
    ts, ss = np.asarray(ts), np.asarray(ss)
    k = (ss < hi) & (ss > lo)
    if k.sum() < 3:
        return float("nan")
    return float(np.polyfit(np.log(ts[k]), np.log(ss[k]), 1)[0])


def main() -> None:
    out = {"TS": TS.tolist(), "runs": {}}
    for seed in (0, 1, 2):
        X, Y, Q = (a.numpy() for a in lg_problem(seed))
        Y, Q = Y[:, 0], Q[:, 0]
        tr_ref, mu_ref = reference(X, Y, Q, GRID)
        ysd = float(Y.std())
        for kind in ("gaussian", "matern32", "laplace"):
            for ell_rel in (0.3, 1.0):
                ell = ell_rel * ysd
                key = f"{kind}_ell{ell_rel}_seed{seed}"
                rec = {"kind": kind, "ell": ell, "seed": seed, "rows": []}
                for h in HS:
                    for t, (m, T) in zip(TS, flow(kind, ell, X, Y, Q, h)):
                        he, hm, r2, nok = fit(tr_ref, mu_ref, T, m)
                        rec["rows"].append({"h": h, "t": float(t), "h_eff": float(he),
                                            "h_mean": float(hm), "r2": r2, "n_pos": nok})
                s_of_t = {r["t"]: r["h_eff"] for r in rec["rows"] if r["h"] == 0}
                pl = [dict(r, s=s_of_t[r["t"]]) for r in rec["rows"]
                      if r["h"] > 0 and r["n_pos"] == len(Q) and s_of_t[r["t"]] > 4e-3]
                rec["p"], rec["rmse_p"], rec["rmse_additive"] = power_law(pl)
                ts = sorted(s_of_t); ss = [s_of_t[t] for t in ts]
                rec["s_slope"] = slope(ts, ss, 0.012, 0.2)
                agree = [abs(np.log(r["h_mean"] / r["h_eff"])) for r in rec["rows"]
                         if r["n_pos"] == len(Q) and r["h_eff"] < 1.0]
                rec["median_abs_log_mean_vs_var"] = float(np.median(agree))
                rec["median_r2"] = float(np.median([r["r2"] for r in rec["rows"]
                                                    if r["n_pos"] == len(Q) and r["h_eff"] < 1.0]))
                fin = {h: [r["h_eff"] for r in rec["rows"] if r["h"] == h][-1] for h in HS}
                rec["final_h_eff"] = {str(h): float(v) for h, v in fin.items()}
                out["runs"][key] = rec
                print(f"{key:28s} p={rec['p']:.2f} (rmse {rec['rmse_p']:.3f}, additive "
                      f"{rec['rmse_additive']:.3f})  ds/dlogt={rec['s_slope']:.2f}  "
                      f"|log hm/he|={rec['median_abs_log_mean_vs_var']:.3f}  "
                      f"R2={rec['median_r2']:.2f}  final={ {h: round(v, 4) for h, v in fin.items()} }")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
