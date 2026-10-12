"""Theorem B (docs/theory/theorem_B.tex; Theorem thm:labelmix, App. apx:thmB) on the linear-Gaussian problem.

For the Nadaraya--Watson mixture sum_i p_i^{(h)}(y) delta_{x^i} over a training set of
the EXP-1 problem (d = 2, k = 1, sigma = 0.1, prior N(0, I)), and the statistic
s(x) = x_1, this measures the coverage C_alpha of the mixture's central alpha-interval
at fresh pairs (x*, y*) and compares |C_alpha - alpha| with the theorem's right-hand side

    2 L E r(Y*) + 8 E n_eff(Y*)^{-1/2} + sqrt(2 a_max log(1/delta)),   delta = 0.05.

Here F(u | y) is Gaussian with mean linear in y, so L = phi(0) |dm/dy| / sd is exact. Also
reported: 2 E D(Y*), the sup-norm CDF error the proof bounds (Step 2), to show where the
bound loses. Five training sets per N, N in {200, 2000, 10000}, h on a geometric grid.

Writes: results/theory/theorem_b_check.json
Usage:  python scripts/theory_b_check.py [--m-star 4000]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from src.problems.linear_gaussian import LinearGaussianProblem

SIGMA, D, K = 0.1, 2, 1
ALPHAS = (0.5, 0.9)
DELTA = 0.05
HS = np.geomspace(0.003, 3.0, 25)


def norm_cdf(z):
    return 0.5 * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))


def run(N: int, seed: int, m_star: int, chunk: int = 400) -> list[dict]:
    p = LinearGaussianProblem.create(d=D, k=K, sigma_obs=SIGMA, seed=0, prior_std=1.0, A_kind="random")
    X, Y = (t.numpy() for t in p.sample_dataset(N, seed=1000 + seed))
    Xs, Ys = (t.numpy() for t in p.sample_dataset(m_star, seed=50000 + seed))
    S, Ss = X[:, 0], Xs[:, 0]
    Sp = p.Sigma_post.numpy()
    sd = math.sqrt(Sp[0, 0])
    slope = (Sp @ p.A.numpy().T / SIGMA ** 2)[0, 0]      # d m_1 / d y   (k = 1)
    L = abs(slope) / (sd * math.sqrt(2 * math.pi))
    order = np.argsort(S)
    S_sorted = S[order]
    m_star_mean = np.array([(Sp @ p.A.numpy().T / SIGMA ** 2 @ y)[0] for y in Ys])
    grid = np.linspace(-5, 5, 401)                          # for the sup-norm CDF error
    rows = []
    for h in HS:
        r_sum = ninv_sum = 0.0
        a = np.zeros(N)
        cover = {al: 0 for al in ALPHAS}
        dsum = 0.0
        for c0 in range(0, m_star, chunk):
            ys = Ys[c0:c0 + chunk, 0]
            d2 = (ys[:, None] - Y[None, :, 0]) ** 2
            lw = -d2 / (2 * h * h)
            lw -= lw.max(1, keepdims=True)
            P = np.exp(lw)
            P /= P.sum(1, keepdims=True)
            r_sum += float((P * np.sqrt(d2)).sum())
            ninv_sum += float(np.sqrt((P ** 2).sum(1)).sum())
            a += P.sum(0)
            cum = np.cumsum(P[:, order], axis=1)
            s_true = Ss[c0:c0 + chunk]
            for al in ALPHAS:
                lo_i = (cum >= (1 - al) / 2 - 1e-12).argmax(1)
                hi_i = (cum >= (1 + al) / 2 - 1e-12).argmax(1)
                cover[al] += int(((s_true >= S_sorted[lo_i]) & (s_true <= S_sorted[hi_i])).sum())
            # sup-norm CDF error on a grid of u, against the exact Gaussian conditional
            mu = m_star_mean[c0:c0 + chunk][:, None]
            F = norm_cdf((grid[None, :] - mu) / sd)
            idx = np.searchsorted(S_sorted, grid, side="right")
            Fh = np.concatenate([np.zeros((len(ys), 1)), cum], 1)[:, idx]
            dsum += float(np.abs(Fh - F).max(1).sum())
        Er, En, amax = r_sum / m_star, ninv_sum / m_star, float((a / m_star).max())
        terms = {"bias": 2 * L * Er, "fluct": 8 * En, "conc": math.sqrt(2 * amax * math.log(1 / DELTA))}
        row = {"N": N, "seed": seed, "h": float(h), "L": L, "E_r": Er, "E_neff_inv_sqrt": En,
               "a_max": amax, "two_E_D": 2 * dsum / m_star, "bound": sum(terms.values()), **terms}
        for al in ALPHAS:
            C = cover[al] / m_star
            row[f"cov_{al}"] = C
            row[f"err_{al}"] = abs(C - al)
            row[f"mc_se_{al}"] = math.sqrt(al * (1 - al) / m_star)
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-star", type=int, default=4000)
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()
    rows = []
    for N in (200, 2000, 10000):
        for s in range(args.seeds):
            rows += run(N, s, args.m_star)
        rs = [r for r in rows if r["N"] == N]
        viol = sum(r[f"err_{al}"] - 2 * r[f"mc_se_{al}"] > r["bound"] for r in rs for al in ALPHAS)
        viol_D = sum(r[f"err_{al}"] - 2 * r[f"mc_se_{al}"] > r["two_E_D"] for r in rs for al in ALPHAS)
        print(f"N={N}: bound violated (beyond 2 MC s.e.) at {viol}/{2 * len(rs)}; "
              f"2E[D] violated at {viol_D}")
        for h in HS[::4]:
            hr = [r for r in rs if abs(r["h"] - h) < 1e-12]
            f = lambda k: np.mean([r[k] for r in hr])
            print(f"   h={h:.4f}  |C-0.9|={f('err_0.9'):.3f}  2E[D]={f('two_E_D'):.3f}  "
                  f"bound={f('bound'):.3f} (bias {f('bias'):.3f}, fluct {f('fluct'):.3f}, "
                  f"conc {f('conc'):.3f})  n_eff^-1/2={f('E_neff_inv_sqrt'):.3f}")
    summ = {}
    for N in (200, 2000, 10000):
        rs = [r for r in rows if r["N"] == N]
        by_h = {}
        for r in rs:
            by_h.setdefault(r["h"], []).append(r)
        mean = {h: {k: float(np.mean([r[k] for r in v])) for k in ("bound", "err_0.9", "err_0.5", "two_E_D")}
                for h, v in by_h.items()}
        hb = min(mean, key=lambda h: mean[h]["bound"])
        he = min(mean, key=lambda h: mean[h]["err_0.9"])
        summ[str(N)] = {"h_min_bound": hb, "min_bound": mean[hb]["bound"],
                        "err90_at_h_min_bound": mean[hb]["err_0.9"],
                        "h_min_err90": he, "min_err90": mean[he]["err_0.9"],
                        "violations": int(sum(r[f"err_{al}"] - 2 * r[f"mc_se_{al}"] > r["bound"]
                                          for r in rs for al in ALPHAS)),
                        "cases": 2 * len(rs),
                        "ratio_bound_to_2ED_median": float(np.median([r["bound"] / r["two_E_D"] for r in rs]))}
        print(f"N={N}: bound minimal at h={hb:.4f} ({mean[hb]['bound']:.3f}; measured |C-0.9| there "
              f"{mean[hb]['err_0.9']:.3f}); measured error minimal at h={he:.4f} ({mean[he]['err_0.9']:.3f}); "
              f"median bound / 2E[D] = {summ[str(N)]['ratio_bound_to_2ED_median']:.2f}")
    out = {"sigma": SIGMA, "d": D, "k": K, "delta": DELTA, "alphas": ALPHAS, "summary": summ, "rows": rows}
    path = Path("results/theory/theorem_b_check.json")
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("Saved:", path)


if __name__ == "__main__":
    main()
