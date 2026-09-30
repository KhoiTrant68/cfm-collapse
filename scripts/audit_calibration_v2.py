"""Audit versus calibration, with baselines and a validation split (reviewer checks).

Round 3 of the simulated review asked three things of the h_eff-predicts-calibration
result: (i) whether h_eff beats predictors that also move monotonically with training
(the training loss, the iteration, the raw generated variance), including after
controlling for the iteration; (ii) how to use h_eff without knowing the posterior;
(iii) whether it holds beyond a 2-D Gaussian posterior. This script produces the data
for all three, for the linear-Gaussian runs (results/exp1/heff_p7y_*) and the d = 8
Gaussian-mixture runs (results/exp2/heff_gmm_*).

For every run and checkpoint from 3000 iterations it records

  audit (training set only)   h_eff and h_mean at 20 training conditions (fitted as in
                              the paper), the raw generated trace, the on-atom fraction,
                              the training loss (EMA at the checkpoint), the iteration
  calibration (held out)      at 100 test pairs and, separately, 30 validation pairs
                              (x*, y*) drawn from the prior and the forward model:
                              - coverage of the 50% / 90% Mahalanobis regions
                              - PIT error: u = share of samples below x* per coordinate;
                                a calibrated sampler has u ~ Uniform(0,1); the error is
                                mean over a grid of |P(u <= a) - a|. It needs no
                                posterior, only held-out pairs, and is valid for
                                multimodal posteriors
                              - extraction: share of samples that are training points
                              - W2 to the true posterior (Gaussian case only), median

Reads:  results/exp1/heff_p7y_*/, results/exp2/heff_gmm_*/ (config, checkpoints, metrics)
Writes: results/<exp>/_heff/audit_calibration_v2.json

Usage:
    PYTHONPATH=. uv run python scripts/audit_calibration_v2.py --exp exp1
    PYTHONPATH=. uv run python scripts/audit_calibration_v2.py --exp exp2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.flows.ode_solver import generate_samples
from src.metrics.kernel_theory import kernel_weights
from src.metrics.memorization import memorization_ratio
from src.models.mlp_velocity import build_model
from src.problems.gmm import GMMProblem
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

MIN_ITER = 3000
N_TEST, N_VAL, N_TRAIN_COND, M = 100, 30, 20, 400
GRID = np.exp(np.linspace(np.log(1e-3), np.log(5.0), 240))
PIT_GRID = np.linspace(0.05, 0.95, 19)
CHI2_2 = {0.5: 1.3862944, 0.9: 4.6051702}


def chi2_quantile(q: float, dof: int) -> float:
    """Wilson-Hilferty approximation; exact enough for a coverage threshold."""
    from statistics import NormalDist
    z = NormalDist().inv_cdf(q)
    return dof * (1 - 2 / (9 * dof) + z * np.sqrt(2 / (9 * dof))) ** 3


def load_problem(cfg, exp):
    dc = cfg["data"]
    if exp == "exp1":
        ps = int(dc.get("problem_seed", cfg["seed"]))
        p = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                         seed=ps, prior_std=dc.get("prior_std", 1.0),
                                         A_kind=dc.get("A_kind", "random"))
        X, Y = p.sample_dataset(dc["N"], seed=ps + 1)
        return p, X, Y, ps
    p = GMMProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
                          mode_scale=dc.get("mode_scale", 2.0), mode_std=dc.get("mode_std", 0.5),
                          A_kind=dc.get("A_kind", "project_x0"))
    X, Y = p.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    return p, X, Y, int(cfg["seed"])


def reference(X, Y, idx):
    X, Y = X.to(torch.float64), Y.to(torch.float64)
    D = torch.cdist(Y[idx], Y) ** 2
    x2 = (X ** 2).sum(1)
    tr = np.empty((len(GRID), len(idx)))
    mu = np.empty((len(GRID), len(idx), X.shape[1]))
    for g, hp in enumerate(GRID):
        W = torch.softmax(-D / (2 * hp ** 2), dim=1)
        m = W @ X
        tr[g] = (W @ x2 - (m ** 2).sum(1)).clamp_min(1e-300).numpy()
        mu[g] = m.numpy()
    return tr, mu


def sqrtm_psd(A):
    w, V = torch.linalg.eigh(A)
    return (V * w.clamp_min(0).sqrt()) @ V.T


def pair_metrics(s, xs, X, post=None):
    """Calibration statistics of samples s (M,d) against one held-out x*."""
    d = s.shape[1]
    m, C = s.mean(0), torch.cov(s.T).reshape(d, d)
    diff = xs - m
    d2 = float(diff @ torch.linalg.solve(C + 1e-10 * torch.eye(d, dtype=torch.float64), diff))
    out = {"in50": d2 <= chi2_quantile(0.5, d), "in90": d2 <= chi2_quantile(0.9, d),
           "u": (s < xs[None, :]).double().mean(0).numpy(),
           "extr": memorization_ratio(s, X)}
    if post is not None:
        mu, S = post
        s2 = sqrtm_psd(S)
        out["w2"] = float(((m - mu) ** 2).sum() + torch.trace(C + S - 2 * sqrtm_psd(s2 @ C @ s2)))
    return out


def summarise(rows):
    u = np.concatenate([r["u"] for r in rows])
    c50 = float(np.mean([r["in50"] for r in rows]))
    c90 = float(np.mean([r["in90"] for r in rows]))
    out = {"coverage_50": c50, "coverage_90": c90,
           "calibration_error": abs(c50 - 0.5) + abs(c90 - 0.9),
           "pit_error": float(np.mean([abs((u <= a).mean() - a) for a in PIT_GRID])),
           "extraction": float(np.mean([r["extr"] for r in rows]))}
    if "w2" in rows[0]:
        out["w2_median"] = float(np.median([r["w2"] for r in rows]))
    return out


@torch.no_grad()
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=["exp1", "exp2"], required=True)
    args = ap.parse_args()
    torch.set_num_threads(8)
    pattern = "heff_p7y_h*_seed*" if args.exp == "exp1" else "heff_gmm_h*_seed*"
    runs = sorted(Path(f"results/{args.exp}").glob(pattern))
    out_rows = []
    for run in runs:
        cfg = load_yaml(run / "config.yaml")
        dc, ev = cfg["data"], cfg["eval"]
        problem, X, Y, ps = load_problem(cfg, args.exp)
        X64 = X.to(torch.float64)
        h = float(cfg["train"].get("y_noise_h", 0.0))
        g_t = torch.Generator().manual_seed(ps + 31337)
        X_te = problem.sample_prior(N_TEST, generator=g_t); Y_te = problem.forward(X_te, generator=g_t)
        g_v = torch.Generator().manual_seed(ps + 4242)
        X_va = problem.sample_prior(N_VAL, generator=g_v); Y_va = problem.forward(X_va, generator=g_v)
        gauss = args.exp == "exp1"
        if gauss:
            Sig = problem.Sigma_post.to(torch.float64)
            mu_te = problem.posterior_mean(Y_te).to(torch.float64)
        idx = sorted(set(torch.linspace(0, X.shape[0] - 1, N_TRAIN_COND).round().long().tolist()))
        tr_ref, mu_ref = reference(X, Y, idx)
        g_h = int(np.argmin(np.abs(GRID - h))) if h > 0 else None
        metrics = pd.read_csv(run / "raw" / "metrics.csv")
        if "group" in metrics:
            metrics = metrics[metrics["group"] == "train"]
        loss_at = dict(zip(metrics["iter"], metrics.get("train_loss", pd.Series(dtype=float))))
        model = build_model(cfg, data_dim=problem.d, cond_dim=problem.k)

        def sample(y, gen):
            return generate_samples(model, M, problem.d, y, source_std=dc.get("source_std", 1.0),
                                    n_steps=ev.get("n_steps", 100),
                                    method=ev.get("ode_method", "rk4"),
                                    eps=ev.get("ode_eps", 1e-3), generator=gen,
                                    device="cpu").to(torch.float64)

        ckpts = sorted((p for p in run.glob("checkpoints/ckpt_*.pt")
                        if int(p.stem.split("_")[1]) >= MIN_ITER),
                       key=lambda p: int(p.stem.split("_")[1]))
        for ck in ckpts:
            it = int(ck.stem.split("_")[1])
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model.eval()
            gen = torch.Generator().manual_seed(777 + it)
            # audit at training conditions
            tr_m, mu_m, on_atom = [], [], []
            for i in idx:
                s = sample(Y[i], gen)
                tr_m.append(float(s.var(0, unbiased=True).sum())); mu_m.append(s.mean(0).numpy())
                on_atom.append(memorization_ratio(s, X))
            tr_m, mu_m = np.array(tr_m), np.stack(mu_m)
            ly = np.log(np.clip(tr_m, 1e-300, None))
            sse = ((ly[None] - np.log(tr_ref)) ** 2).sum(1)
            mean_err = np.linalg.norm(mu_m[None] - mu_ref, axis=2).mean(1)
            row = {"run": run.name, "h": h, "seed": int(cfg["seed"]), "iter": it,
                   "h_eff": float(GRID[int(np.argmin(sse))]),
                   "h_mean": float(GRID[int(np.argmin(mean_err))]),
                   "trace_raw": float(tr_m.mean()), "on_atom_train": float(np.mean(on_atom)),
                   "train_loss": float(loss_at.get(it, np.nan))}
            if g_h is not None:
                lref = np.log(tr_ref[g_h])
                A = np.vstack([np.ones_like(lref), lref]).T
                row["beta"] = float(np.linalg.lstsq(A, ly, rcond=None)[0][1])
            for name, Xs, Ys in (("test", X_te, Y_te), ("val", X_va, Y_va)):
                pr = []
                for j in range(Xs.shape[0]):
                    post = (mu_te[j], Sig) if (gauss and name == "test") else None
                    pr.append(pair_metrics(sample(Ys[j], gen), Xs[j].to(torch.float64), X64, post))
                row.update({f"{name}_{k}": v for k, v in summarise(pr).items()})
            out_rows.append(row)
            print(f"{run.name:<24} it={it:>6d} h_eff={row['h_eff']:.4f} h_mean={row['h_mean']:.4f} "
                  f"cov90 test={row['test_coverage_90']:.2f} val={row['val_coverage_90']:.2f} "
                  f"PIT={row['test_pit_error']:.3f} extr={row['test_extraction']:.2f} "
                  f"loss={row['train_loss']:.4f}", flush=True)
    out = Path(f"results/{args.exp}/_heff/audit_calibration_v2.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_rows, indent=1), encoding="utf-8")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
