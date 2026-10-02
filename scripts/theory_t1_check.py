"""Numerical checks of T1 (identifiability and stability of the effective bandwidth).

T1.a  d/dh xbar_h = Cov_p(x, D)/h^3,  d/dh T_h = Cov_p(|x - xbar_h|^2, D)/h^3,
      with D_i = |y - y^i|^2 and p the kernel weights at bandwidth h.
T1.b  |hhat - h*| <= 2|e| / kappa, kappa = min over a neighbourhood of u . F'(h),
      F(h) = (log T_h(y_c))_c, u = F'(h*)/|F'(h*)|.
T1.c  h^3 d/dh T_h -> Cov_unif(|x - xbar|^2, D) as h -> infinity, so kappa = O(h^-3).

The script (1) checks T1.a against centred finite differences, (2) checks the limit of
T1.c, (3) computes kappa(h) on the linear-Gaussian and CIFAR-10 training sets, and
(4) asks whether the stability bound explains the bootstrap interval widths measured
for h_eff: the predicted half-width 2 * rmse * sqrt(C) / kappa(h_eff) is compared with
the measured one across all synthetic checkpoints (Spearman) and at the bandwidths
where h_eff was poorly identified.

Writes: results/theory/t1_check.json
Usage:  PYTHONPATH=. uv run python scripts/theory_t1_check.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

OUT = Path("results/theory/t1_check.json")


def moments(X, Y, Q, h):
    """Weights, mean, trace and their h-derivatives at queries Q, all float64."""
    D = torch.cdist(Q, Y) ** 2                                   # (C, N)
    P = torch.softmax(-D / (2 * h * h), dim=1)
    xbar = P @ X                                                 # (C, d)
    r2 = ((X[None] - xbar[:, None]) ** 2).sum(-1)               # (C, N) |x - xbar|^2
    T = (P * r2).sum(1)
    Dbar = (P * D).sum(1, keepdim=True)
    dP = P * (D - Dbar) / h ** 3
    dxbar = dP @ X                                               # = Cov_p(x, D)/h^3
    dT = (P * (r2 - (P * r2).sum(1, keepdim=True)) * (D - Dbar)).sum(1) / h ** 3
    return P, xbar, T, dxbar, dT, D


def kappa(X, Y, Q, h, width=1.5, n=25):
    """min over [h/width, h*width] of u . F'(h'), u the unit direction of F'(h)."""
    _, _, T0, _, dT0, _ = moments(X, Y, Q, h)
    g0 = (dT0 / T0).numpy()
    u = g0 / (np.linalg.norm(g0) + 1e-300)
    vals = []
    for hp in np.exp(np.linspace(np.log(h / width), np.log(h * width), n)):
        _, _, T, _, dT, _ = moments(X, Y, Q, float(hp))
        vals.append(float(u @ (dT / T).numpy()))
    return min(vals), float(np.linalg.norm(g0))


def lg_problem(seed):
    cfg = load_yaml("configs/exp1_linear_gaussian.yaml")
    dc = cfg["data"]
    p = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=seed,
                                     prior_std=dc.get("prior_std", 1.0),
                                     A_kind=dc.get("A_kind", "random"))
    X, Y = p.sample_dataset(dc["N"], seed=seed + 1)
    idx = torch.linspace(0, X.shape[0] - 1, 20).round().long()
    return X.double(), Y.double(), Y.double()[idx]


def main() -> None:
    torch.set_default_dtype(torch.float64)
    out = {}
    X, Y, Q = lg_problem(0)

    # (1) T1.a against centred finite differences
    errs = []
    for h in (0.02, 0.05, 0.1, 0.3, 1.0):
        e = h * 1e-5
        _, xb_p, T_p, _, _, _ = moments(X, Y, Q, h + e)
        _, xb_m, T_m, _, _, _ = moments(X, Y, Q, h - e)
        _, _, _, dxb, dT, _ = moments(X, Y, Q, h)
        fd_T, fd_x = (T_p - T_m) / (2 * e), (xb_p - xb_m) / (2 * e)
        errs.append({"h": h,
                     "rel_err_dT": float((fd_T - dT).abs().max() / dT.abs().max()),
                     "rel_err_dxbar": float((fd_x - dxb).abs().max() / dxb.abs().max())})
    out["t1a_finite_difference"] = errs
    print("T1.a finite differences:", [(r["h"], f"{r['rel_err_dT']:.1e}", f"{r['rel_err_dxbar']:.1e}")
                                      for r in errs])

    # (2) T1.c: h^3 dT/dh -> Cov_unif(|x - xbar|^2, D)
    Dq = torch.cdist(Q, Y) ** 2
    r2u = ((X[None] - X.mean(0)[None, None]) ** 2).sum(-1)
    c_inf = ((r2u - r2u.mean(1, keepdim=True)) * (Dq - Dq.mean(1, keepdim=True))).mean(1)
    lim = []
    for h in (3.0, 10.0, 30.0, 100.0):
        _, _, _, _, dT, _ = moments(X, Y, Q, h)
        lim.append({"h": h, "max_rel_dev": float(((h ** 3 * dT - c_inf).abs() / c_inf.abs()).max())})
    out["t1c_limit"] = lim
    print("T1.c h^3 dT/dh vs c_inf:", [(r["h"], f"{r['max_rel_dev']:.2e}") for r in lim])

    # (3) kappa(h) on the linear-Gaussian (seed 0) and CIFAR-10 (h = 4 setup) training sets
    kap_lg = [{"h": float(h), "kappa": kappa(X, Y, Q, float(h))[0]}
              for h in np.exp(np.linspace(np.log(0.005), np.log(2.0), 25))]
    out["kappa_linear_gaussian"] = kap_lg
    try:
        from src.problems.inpainting import InpaintingProblem
        from src.train_exp3 import cond_vectors
        pc = InpaintingProblem.create(N=2000, seed=0, data_root="data", mask_kind="bottom_half",
                                      dataset="cifar10")
        Xc, Yc = pc.X.flatten(1).double(), cond_vectors(pc).double()
        Qc = Yc[np.linspace(0, 1999, 48).round().astype(int)]
        kap_c = [{"h": float(h), "kappa": kappa(Xc, Yc, Qc, float(h))[0]}
                 for h in (3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0)]
        out["kappa_cifar"] = kap_c
        print("kappa CIFAR-10:", [(r["h"], f"{r['kappa']:.3g}") for r in kap_c])
    except Exception as exc:                                   # CIFAR-10 not available
        print("CIFAR-10 skipped:", exc)

    # (4) does 2 * rmse * sqrt(C) / kappa(h_eff) explain the measured interval widths?
    rows = json.loads(Path("results/exp1/_heff/heff_synthetic.json").read_text(encoding="utf-8"))
    probs = {s: lg_problem(s) for s in (0, 1, 2)}
    pred, meas, recs = [], [], []
    for r in rows:
        if r["iter"] < 3000 or r.get("h_eff_at_edge"):
            continue
        Xs, Ys, Qs = probs[r.get("seed", 0)]
        k, _ = kappa(Xs, Ys, Qs, r["h_eff"])
        lo, hi = r["h_eff_ci"]
        p_half = 2 * r["rmse_log_heff"] * np.sqrt(len(Qs)) / max(k, 1e-12)
        m_half = (np.log(hi) - np.log(lo)) / 2 * r["h_eff"]   # half-width in h units
        recs.append({"run_h": r["h"], "seed": r.get("seed", 0), "iter": r["iter"],
                     "h_eff": r["h_eff"], "kappa": k, "pred_half": float(p_half),
                     "meas_half": float(m_half)})
        if k > 0:
            pred.append(p_half); meas.append(m_half)
    rk = lambda a: np.argsort(np.argsort(a))
    sp = float(np.corrcoef(rk(np.log(pred)), rk(np.log(meas)))[0, 1])
    out["width_vs_kappa"] = {"spearman_pred_vs_meas": sp, "n": len(pred),
                             "bound_holds_fraction": float(np.mean(np.array(meas) <= np.array(pred))),
                             "rows": recs}
    by_h = {}
    for rec in recs:
        by_h.setdefault(rec["run_h"], []).append(rec["kappa"])
    out["median_kappa_by_training_h"] = {str(h): float(np.median(v)) for h, v in by_h.items()}
    print(f"bound vs bootstrap half-width: Spearman {sp:.3f} over {len(pred)} checkpoints; "
          f"bound >= measured at {out['width_vs_kappa']['bound_holds_fraction']:.0%}")
    print("median kappa at h_eff, by training h:",
          {h: f"{v:.3g}" for h, v in out["median_kappa_by_training_h"].items()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
