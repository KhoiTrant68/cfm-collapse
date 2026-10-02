"""T2 at the level of the field: a label-filtered population field and its endpoint law.

Model. A learner that resolves the label only to a scale s replaces the population field
v*_h(x, t, y) by its average over nearby labels,

    v_phi(x, t, y) = E_u[ v*_h(x, t, y - u) ],   u ~ phi_s = N(0, s^2),

which is again sum_i w~_i (x^i - x)/(1 - t) with w~_i = E_u[w_i(x, t, y - u)] >= 0. The
proposition in the paper says its endpoint law stays on the training atoms. This script
(1) integrates the flow of v_phi exactly (time change tau = -log(1 - t), so dx/dtau =
m - x) and checks that the endpoints are atoms; (2) compares the endpoint weights q~ with
the label-averaged weights q = E_u[p^(h)(y - u)] (the weights the field has at t = 0) and
with the Nadaraya-Watson law at the convolved bandwidth sqrt(h^2 + s^2); and (3) fits the
effective bandwidth to q over a grid of (h, s) and reads off the additive exponent p in
h_eff^p = h^p + s_eff^p, to compare with p = 1.3 of the trained networks.

Writes: results/theory/t2_filtered.json
Usage:  PYTHONPATH=. uv run --with scipy python scripts/theory_t2_filtered.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import minimize_scalar
from scipy.stats import norm

from scripts.theory_t1_check import lg_problem
from scripts.theory_t2_resolution import GRID, fit, nw, reference

OUT = Path("results/theory/t2_filtered.json")
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(15)
GH_W = GH_W / GH_W.sum()


def averaged_weights(Yq, Y, h, s, n_u=4001):
    """q_i(y) = E_u p_i^(h)(y - u), u ~ N(0, s^2); exact Voronoi masses at h = 0."""
    if s == 0:
        return nw(Yq, Y, None, h)
    if h == 0:
        order = np.argsort(Y); ys = Y[order]
        mid = np.concatenate([[-np.inf], (ys[1:] + ys[:-1]) / 2, [np.inf]])
        Q = np.zeros((len(Yq), len(Y)))
        for c, y in enumerate(Yq):           # P(y - u in cell of ys[j])
            cdf = norm.cdf((y - mid) / s)
            Q[c, order] = cdf[:-1] - cdf[1:]
        return Q
    u = np.linspace(-7 * s, 7 * s, n_u); wu = norm.pdf(u / s); wu /= wu.sum()
    Q = np.zeros((len(Yq), len(Y)))
    for c, y in enumerate(Yq):
        Q[c] = wu @ nw(y - u, Y, None, h)
    return Q


def moments(P, X):
    m = P @ X
    T = (P * ((X[None] - m[:, None]) ** 2).sum(-1)).sum(1)
    return m, T


def filtered_flow(X, Y, y, h, s, n_part=300, dtau=0.04, delta=1e-4, seed=0):
    """Endpoints of the flow of v_phi from N(0, I) at label y (torch, float64)."""
    Xt = torch.tensor(X); Yt = torch.tensor(Y)
    u = torch.tensor(GH_X * s); wu = torch.tensor(GH_W)
    lb = -((y - u)[:, None] - Yt[None]) ** 2 / (2 * h * h)        # (U, N)
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n_part, X.shape[1], generator=g, dtype=torch.float64)

    def field(x, tau):
        t = 1 - math.exp(-tau)
        la = -((x[:, None, :] - t * Xt[None]) ** 2).sum(-1) / (2 * (1 - t) ** 2)  # (P, N)
        w = torch.softmax(la[:, None, :] + lb[None], dim=2)                       # (P, U, N)
        wt = (w * wu[None, :, None]).sum(1)                                        # (P, N)
        return wt @ Xt - x

    tau, tau_end = 0.0, -math.log(delta)
    while tau < tau_end - 1e-12:
        dt = min(dtau, tau_end - tau)
        k1 = field(x, tau); k2 = field(x + dt / 2 * k1, tau + dt / 2)
        k3 = field(x + dt / 2 * k2, tau + dt / 2); k4 = field(x + dt * k3, tau + dt)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        tau += dt
    d = torch.cdist(x, Xt)
    dmin, idx = d.min(1)
    q = np.bincount(idx.numpy(), minlength=len(Y)) / n_part
    return q, float(dmin.max()), float(torch.cdist(Xt, Xt).add(torch.eye(len(Y)) * 1e9).min())


def tv(a, b):
    return float(0.5 * np.abs(a - b).sum(-1).mean())


def main() -> None:
    out = {}
    X, Y, Q = (a.numpy() for a in lg_problem(0))
    Y, Q = Y[:, 0], Q[:, 0]
    tr_ref, mu_ref = reference(X, Y, Q, GRID)

    # (1)-(2) flow of the filtered field at 8 conditions
    flows = []
    cond = Q[::4][:5]
    for h, s in ((0.01, 0.02), (0.01, 0.05), (0.05, 0.05), (0.01, 0.1), (0.1, 0.1)):
        qt = []; dmax = 0.0
        for c, y in enumerate(cond):
            q, dm, _ = filtered_flow(X, Y, float(y), h, s, seed=c)
            qt.append(q); dmax = max(dmax, dm)
        qt = np.array(qt)
        qa = averaged_weights(cond, Y, h, s)
        qc = nw(cond, Y, None, math.hypot(h, s))
        mt, Tt = moments(qt, X); ma, Ta = moments(qa, X); mc, Tc = moments(qc, X)
        rec = {"h": h, "s": s, "max_endpoint_dist_to_atom": dmax,
               "tv_flow_vs_averaged": tv(qt, qa), "tv_flow_vs_convolved_nw": tv(qt, qc),
               "tv_mc_floor": float(np.mean([0.5 * np.abs(np.random.default_rng(i).multinomial(
                   300, qa[i] / qa[i].sum()) / 300 - qa[i]).sum() for i in range(len(cond))])),
               "trace_flow": float(Tt.mean()), "trace_averaged": float(Ta.mean()),
               "trace_convolved": float(Tc.mean())}
        flows.append(rec)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()})
    out["flow"] = flows

    # (3) effective bandwidth of the averaged weights and the additive exponent
    rows = []
    S = np.exp(np.linspace(np.log(0.004), np.log(0.4), 14))
    for s in S:
        for h in (0.0, 0.01, 0.02, 0.05, 0.1):
            P = averaged_weights(Q, Y, h, float(s))
            m, T = moments(P, X)
            he, hm, r2, nok = fit(tr_ref, mu_ref, T, m)
            rows.append({"h": h, "s": float(s), "h_eff": float(he), "h_mean": float(hm),
                         "r2": r2})
    s_eff = {r["s"]: r["h_eff"] for r in rows if r["h"] == 0}
    pl = [dict(r, se=s_eff[r["s"]]) for r in rows if r["h"] > 0 and r["r2"] > 0]

    def loss(p):
        return float(np.mean([(np.log(r["h_eff"]) - np.log(r["h"] ** p + r["se"] ** p) / p) ** 2
                              for r in pl]))
    res = minimize_scalar(loss, bounds=(0.5, 4), method="bounded")
    out["averaged"] = {"rows": rows, "p": float(res.x), "rmse_p": math.sqrt(res.fun),
                       "rmse_p2": math.sqrt(loss(2.0)),
                       "s_eff_over_s": {f"{s:.4g}": s_eff[s] / s for s in s_eff},
                       "median_r2": float(np.median([r["r2"] for r in rows])),
                       "median_abs_log_mean_vs_var": float(np.median(
                           [abs(np.log(r["h_mean"] / r["h_eff"])) for r in rows]))}
    print(f"averaged weights: p = {res.x:.2f} (rmse {math.sqrt(res.fun):.3f}; p=2: "
          f"{math.sqrt(loss(2.0)):.3f}); median R2 {out['averaged']['median_r2']:.2f}; "
          f"|log hm/he| {out['averaged']['median_abs_log_mean_vs_var']:.3f}")
    print("s_eff/s:", {k: round(v, 2) for k, v in out["averaged"]["s_eff_over_s"].items()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
