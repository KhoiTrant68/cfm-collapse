"""Distance from generated law to the TRUE posterior for EXP-1 (WORK_ORDER T7).

EXP-1 has an analytic Gaussian posterior N(mu_post(y), Sigma_post), so we can
draw exact ground-truth samples. For hard conditioning (h=0) and each label-noise
run (p7y_h*), we measure MMD and Sinkhorn divergence between generated samples
and true-posterior samples at the final checkpoint.

This is the direct test of the atomicity obstruction (Prop 14): p_h^gen is atomic
for every h, while p(.|y) is continuous, so the distance must NOT go to 0 at any
h -- not even the h that best matches the trace covariance. "Restoring variance"
is not "recovering the posterior".

    uv run python scripts/analyze_posterior_distance_exp1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.ode_solver import generate_samples  # noqa: E402
from src.metrics.distances import mmd_rbf, sinkhorn_distance  # noqa: E402
from src.metrics.kernel_theory import kernel_trace_cov  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
RUNS = [("exp1_cond_seed0", 0.0)] + [(f"p7y_h{h}_seed0", h) for h in (0.01, 0.05, 0.1, 0.5)]
N_COND = 8
M = 1000


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                        seed=cfg["seed"], prior_std=dc.get("prior_std", 1.0),
                                        A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    h = float(cfg["train"].get("y_noise_h", 0.0))
    return cfg, prob, X.float(), Y.float(), model, h


def true_posterior_samples(prob, y_i, M, gen):
    mu = prob.posterior_mean(y_i).to(torch.float64)          # (d,)
    L = torch.linalg.cholesky(prob.Sigma_post)               # (d,d) f64
    z = torch.randn(M, prob.d, generator=gen, dtype=torch.float64)
    return (mu[None, :] + z @ L.T).float()


@torch.no_grad()
def main():
    rows = []
    for name, _ in RUNS:
        rd = ROOT / name
        cfg, prob, X, Y, model, h = rebuild(rd)
        state = torch.load(rd / "checkpoints" / "ckpt_200000.pt", map_location="cpu")
        model.load_state_dict(state["model_state"]); model.eval()
        gen = torch.Generator().manual_seed(cfg["seed"] + 3)
        tgen = torch.Generator().manual_seed(cfg["seed"] + 555)
        idx = sorted(set(torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()))
        mmds, sinks, kern = [], [], []
        for i in idx:
            y_i = Y[i]
            gsamp = generate_samples(model, M, prob.d, y_i, source_std=1.0,
                                     n_steps=100, method="rk4", generator=gen).cpu()
            tsamp = true_posterior_samples(prob, y_i, M, tgen)
            mmds.append(mmd_rbf(gsamp, tsamp))
            sinks.append(sinkhorn_distance(gsamp, tsamp, blur=0.1))
            kern.append(kernel_trace_cov(y_i, X, Y, h))
        rows.append({"run": name, "h": h,
                     "mmd_to_post": float(np.mean(mmds)), "mmd_std": float(np.std(mmds)),
                     "sinkhorn_to_post": float(np.mean(sinks)), "sinkhorn_std": float(np.std(sinks)),
                     "trace_kernel": float(np.mean(kern))})
        print(f"  {name:22s} h={h:<4}  MMD={np.mean(mmds):.4f}  "
              f"Sinkhorn={np.mean(sinks):.4f}  (Cov_h={np.mean(kern):.3f})")

    df = pd.DataFrame(rows)
    out = ROOT / "_theory" / "raw"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "posterior_distance_exp1.csv", index=False)
    print("\nProp 14 check: does any h drive MMD/Sinkhorn to ~0?")
    best_h = df.loc[df["mmd_to_post"].idxmin()]
    print(f"  min MMD is at h={best_h['h']} (MMD={best_h['mmd_to_post']:.4f}) -- "
          f"{'stays > 0 (atomic, as predicted)' if best_h['mmd_to_post'] > 1e-3 else 'near 0 (!)'}")
    print(f"wrote {out / 'posterior_distance_exp1.csv'}")


if __name__ == "__main__":
    main()
