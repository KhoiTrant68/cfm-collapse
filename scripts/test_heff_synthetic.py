"""Effective-bandwidth test on EXP-1, checkpoint by checkpoint.

Hypothesis (h_eff): a trained conditional flow behaves like the exact kernel reference
of Theorem 10 at ONE effective bandwidth h_eff >= h per checkpoint, shared by all
evaluation conditions, and h_eff falls towards h as training proceeds.

For each run heff_p7y_h{h}_seed0 and each saved checkpoint this draws M samples at the
20 training conditions used throughout EXP-1 and fits h_eff to the per-condition
generated trace, in log space, over a log-spaced grid. It is scored against

    theory   h' = h, no free parameter
    scale    tr Cov = c * tr Cov_h, one free parameter (same count as h_eff)
    power    log tr Cov = a + beta log tr Cov_h, two free parameters

and checked out of sample on the per-condition generated MEAN, which the fit never
sees: at bandwidth h' the reference mean is x_bar_{h'}(y) (Theorem 10), so the
bandwidth that best explains the means should agree with the one fitted to the
variances if the hypothesis is right.

Reads:  results/exp1/heff_p7y_h*_seed0/{config.yaml,checkpoints/}
Writes: results/exp1/_heff/heff_synthetic.json

Usage:
    PYTHONPATH=. uv run python scripts/test_heff_synthetic.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from src.flows.ode_solver import generate_samples
from src.metrics.kernel_theory import kernel_moments
from src.models.mlp_velocity import build_model
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

RUNS = sorted(Path("results/exp1").glob("heff_p7y_h*_seed0"))
OUT = Path("results/exp1/_heff/heff_synthetic.json")
GRID = np.exp(np.linspace(np.log(3e-3), np.log(5.0), 240))


def r2(y, yhat):
    return float(1.0 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def reference(X, Y, idx, grid):
    """Reference trace and mean at every grid bandwidth and condition."""
    tr = np.empty((len(grid), len(idx)))
    mu = np.empty((len(grid), len(idx), X.shape[1]))
    for g, hp in enumerate(grid):
        for c, i in enumerate(idx):
            xb, cov, _ = kernel_moments(Y[i], X, Y, float(hp))
            tr[g, c] = float(torch.trace(cov))
            mu[g, c] = xb.numpy()
    return tr, mu


@torch.no_grad()
def main() -> None:
    torch.set_num_threads(8)
    out = []
    for run in RUNS:
        cfg = load_yaml(run / "config.yaml")
        dc, ev = cfg["data"], cfg["eval"]
        ps = int(dc.get("problem_seed", cfg["seed"]))
        problem = LinearGaussianProblem.create(
            d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=ps,
            prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
        X, Y = problem.sample_dataset(dc["N"], seed=ps + 1)
        X64, Y64 = X.to(torch.float64), Y.to(torch.float64)
        h = float(cfg["train"].get("y_noise_h", 0.0))
        idx = sorted(set(torch.linspace(0, X.shape[0] - 1, ev["n_eval_train"])
                         .round().long().tolist()))
        tr_ref, mu_ref = reference(X64, Y64, idx, GRID)
        tr_h = np.array([float(torch.trace(kernel_moments(Y64[i], X64, Y64, h)[1]))
                         for i in idx])
        mu_h = np.stack([kernel_moments(Y64[i], X64, Y64, h)[0].numpy() for i in idx])

        model = build_model(cfg, data_dim=problem.d, cond_dim=problem.k)
        ckpts = sorted(run.glob("checkpoints/ckpt_*.pt"),
                       key=lambda p: int(p.stem.split("_")[1]))
        gen = torch.Generator().manual_seed(4242)
        for ck in ckpts:
            it = int(ck.stem.split("_")[1])
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model.eval()
            tr_m, mu_m = [], []
            for i in idx:
                s = generate_samples(model, ev["M"], problem.d, Y[i],
                                     source_std=dc.get("source_std", 1.0),
                                     n_steps=ev["n_steps"], method=ev.get("ode_method", "rk4"),
                                     eps=ev.get("ode_eps", 1e-3), generator=gen,
                                     device="cpu").to(torch.float64)
                tr_m.append(float(s.var(dim=0, unbiased=True).sum()))
                mu_m.append(s.mean(0).numpy())
            tr_m, mu_m = np.array(tr_m), np.stack(mu_m)
            ly = np.log(tr_m)

            sse = ((ly[None, :] - np.log(tr_ref)) ** 2).sum(1)
            g = int(np.argmin(sse))
            mean_err = np.linalg.norm(mu_m[None] - mu_ref, axis=2).mean(1)   # (grid,)
            g_mean = int(np.argmin(mean_err))
            res = {"h": h, "iter": it, "h_eff": float(GRID[g]),
                   "h_eff_at_edge": g in (0, len(GRID) - 1),
                   "h_from_means": float(GRID[g_mean]),
                   "trace_measured_mean": float(tr_m.mean()),
                   "trace_ref_h_mean": float(tr_h.mean()),
                   "r2_heff": r2(ly, np.log(tr_ref[g])),
                   "rmse_log_heff": float(np.sqrt(sse[g] / len(ly))),
                   "mean_err_at_h": float(np.linalg.norm(mu_m - mu_h, axis=1).mean()),
                   "mean_err_at_heff": float(mean_err[g]),
                   "mean_err_best": float(mean_err[g_mean])}
            if h > 0:
                lref = np.log(tr_h)
                c = float(np.exp((ly - lref).mean()))
                A = np.vstack([np.ones_like(lref), lref]).T
                coef, *_ = np.linalg.lstsq(A, ly, rcond=None)
                res.update({
                    "r2_theory": r2(ly, lref), "r2_scale": r2(ly, lref + np.log(c)),
                    "r2_power": r2(ly, A @ coef), "scale_c": c, "power_beta": float(coef[1]),
                    "rmse_log_theory": float(np.sqrt(((ly - lref) ** 2).mean())),
                    "rmse_log_scale": float(np.sqrt(((ly - lref - np.log(c)) ** 2).mean()))})
            out.append(res)
            print(f"h={h:<5g} it={it:>6d}  h_eff={res['h_eff']:.4f}  "
                  f"h_means={res['h_from_means']:.4f}  R2(h_eff)={res['r2_heff']:.3f}  "
                  + (f"R2 theory/scale/power={res['r2_theory']:.3f}/{res['r2_scale']:.3f}/"
                     f"{res['r2_power']:.3f}  " if h > 0 else "")
                  + f"mean err @h {res['mean_err_at_h']:.3f} @h_eff {res['mean_err_at_heff']:.3f}",
                  flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
