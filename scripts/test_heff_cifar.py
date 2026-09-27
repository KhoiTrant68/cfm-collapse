"""Does a trained CIFAR-10 flow behave like the kernel reference at a larger bandwidth?

Hypothesis (h_eff): the measured conditional variance at condition y^i is predicted by
the exact Nadaraya-Watson reference at ONE effective bandwidth h_eff per run,

    tr Cov_measured(y^i)  ~  tr Cov_{h_eff}(y^i),

with h_eff >= h the training bandwidth. One parameter per run predicts all 48
conditions, so it is a real test and not a per-condition refit.

It is scored in log space against:
    theory      h' = h, no free parameter (the paper's reference)
    scale       tr Cov = c * tr Cov_h, one free parameter (same count as h_eff)
    power       log tr Cov = a + beta log tr Cov_h, two free parameters (the paper's beta fit)

and checked out of sample on a statistic it was not fitted to: the observed-region
reconstruction error of the generated mean, whose reference value at bandwidth h' is
exact (Theorem 10) and whose measured value is stored in reeval.json.

Reads:  results/exp3/_cifar_ddpm/reeval.json, the CIFAR-10 training subset of each run
Writes: results/exp3/_cifar_ddpm/heff.json

Usage:
    uv run python scripts/test_heff_cifar.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from src.metrics.kernel_theory import kernel_moments_trace, kernel_weights
from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import cond_vectors
from src.utils import load_yaml

SRC = Path("results/exp3/_cifar_ddpm/reeval.json")
OUT = SRC.parent / "heff.json"
GRID = np.round(np.arange(3.0, 12.01, 0.05), 2)


def r2(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(1.0 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main() -> None:
    rows = [r for r in json.loads(SRC.read_text(encoding="utf-8")) if r["h"] > 0]
    out = []
    for r in rows:
        cfg = load_yaml(Path("results/exp3") / r["run"] / "config.yaml")
        dc = cfg["data"]
        problem = InpaintingProblem.create(
            N=dc["N"], seed=cfg["seed"], data_root=dc.get("data_root", "data"),
            mask_kind=dc.get("mask_kind", "bottom_half"),
            dataset=dc.get("dataset", "mnist"), cond_kind=dc.get("cond_kind", "inpaint"))
        X = problem.X.flatten(1).to(torch.float64)
        Y = cond_vectors(problem).to(torch.float64)
        C = problem.channels
        sel = problem.mask_obs.flatten().bool()
        n_obs = int(sel.sum()) * C
        idx = sorted(set(np.linspace(0, problem.N - 1, r["n_conditions"]).round()
                         .astype(int).tolist()))
        h = float(r["h"])

        ref = np.asarray(r["trace_kernel_per_condition"], float)
        meas = np.asarray(r["ratio_per_condition"], float) * ref
        # the stored reference must be reproduced exactly, or the conditions differ
        chk = np.array([kernel_moments_trace(Y[i], X, Y, h)[1] for i in idx])
        assert np.allclose(chk, ref, rtol=1e-6), (r["run"], np.abs(chk / ref - 1).max())

        # reference trace and observed-region error on the whole bandwidth grid
        tr_grid = np.empty((len(GRID), len(idx)))
        obs_grid = np.empty(len(GRID))
        for g, hp in enumerate(GRID):
            errs = []
            for c, i in enumerate(idx):
                tr_grid[g, c] = kernel_moments_trace(Y[i], X, Y, float(hp))[1]
                pw = kernel_weights(Y[i], Y, float(hp))
                ybar = (pw[:, None] * Y).sum(0)
                errs.append(float(((ybar - Y[i]) ** 2).sum() / n_obs))
            obs_grid[g] = np.mean(errs)

        ly = np.log(meas)
        ok = np.all(tr_grid > 0, axis=0) & (meas > 0)
        ly = ly[ok]
        sse = [((ly - np.log(tr_grid[g, ok])) ** 2).sum() for g in range(len(GRID))]
        g_star = int(np.argmin(sse))
        h_eff = float(GRID[g_star])
        pred_heff = np.log(tr_grid[g_star, ok])

        lref = np.log(ref[ok])
        c_hat = float(np.exp((ly - lref).mean()))
        pred_scale = lref + np.log(c_hat)
        A = np.vstack([np.ones_like(lref), lref]).T
        coef, *_ = np.linalg.lstsq(A, ly, rcond=None)
        pred_power = A @ coef

        # out of sample: bandwidth implied by the observed-region error alone
        g_obs = int(np.argmin(np.abs(obs_grid - r["obs_err_measured"])))

        res = {
            "run": r["run"], "h": h, "n": int(ok.sum()),
            "h_eff": h_eff, "at_grid_edge": g_star in (0, len(GRID) - 1),
            "r2_theory": r2(ly, lref), "r2_scale": r2(ly, pred_scale),
            "r2_heff": r2(ly, pred_heff), "r2_power": r2(ly, pred_power),
            "rmse_log_theory": float(np.sqrt(((ly - lref) ** 2).mean())),
            "rmse_log_scale": float(np.sqrt(((ly - pred_scale) ** 2).mean())),
            "rmse_log_heff": float(np.sqrt(((ly - pred_heff) ** 2).mean())),
            "rmse_log_power": float(np.sqrt(((ly - pred_power) ** 2).mean())),
            "scale_c": c_hat, "power_beta": float(coef[1]),
            "obs_err_measured": r["obs_err_measured"],
            "obs_err_pred_at_h": float(obs_grid[np.argmin(np.abs(GRID - h))]),
            "obs_err_pred_at_heff": float(obs_grid[g_star]),
            "h_from_obs_err": float(GRID[g_obs]),
            "sse_profile": [float(s) for s in sse],
        }
        out.append(res)
        print(f"{r['run']}: h={h:g} -> h_eff={h_eff:.2f}"
              f"{' (grid edge!)' if res['at_grid_edge'] else ''}  "
              f"R2 log: theory {res['r2_theory']:.3f} | scale {res['r2_scale']:.3f} | "
              f"h_eff {res['r2_heff']:.3f} | power(2p) {res['r2_power']:.3f}")
        print(f"    obs err measured {res['obs_err_measured']:.5f}; predicted at h "
              f"{res['obs_err_pred_at_h']:.5f}, at h_eff {res['obs_err_pred_at_heff']:.5f}; "
              f"bandwidth implied by obs err alone {res['h_from_obs_err']:.2f}")
    OUT.write_text(json.dumps({"grid": GRID.tolist(), "runs": out}, indent=2),
                   encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
