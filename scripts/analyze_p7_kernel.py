"""Re-evaluate existing p7y checkpoints against the exact kernel reference.

For every (h, seed) run this loads the final checkpoint, generates samples for a
fixed set of training conditions, and compares the *measured* trace-covariance to
the exact Theorem-10 target tr Cov_h(y^i) (not to tr Sigma_post). Produces the
primary P7 evidence table with error bars across seeds — no retraining.

    uv run python scripts/analyze_p7_kernel.py

Outputs:
    results/exp1/_theory/raw/p7_kernel.csv        (per h x seed)
    results/exp1/_theory/raw/p7_kernel_summary.csv (per h, mean +/- std over seeds)
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
from src.metrics.kernel_theory import cov_expansion, kernel_moments  # noqa: E402
from src.metrics.posterior_stats import sample_covariance_trace  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
HS = [0.01, 0.05, 0.1, 0.5]
SEEDS = [0, 1, 2, 3, 4]
N_COND = 20
M = 1000
N_STEPS = 100


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(
        d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
        prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    state = torch.load(run_dir / "checkpoints" / "ckpt_200000.pt", map_location="cpu")
    model.load_state_dict(state["model_state"]); model.eval()
    h = float(cfg["train"].get("y_noise_h", 0.0))
    return cfg, prob, X.float(), Y.float(), model, h


@torch.no_grad()
def eval_run(run_dir: Path) -> dict:
    cfg, prob, X, Y, model, h = rebuild(run_dir)
    gen = torch.Generator().manual_seed(cfg["seed"] + 3)
    idx = sorted(set(torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()))
    tr_meas, tr_kern, ratios, neffs, mean_errs = [], [], [], [], []
    for i in idx:
        y_i = Y[i]
        samples = generate_samples(model, M, prob.d, y_i, source_std=1.0,
                                   n_steps=N_STEPS, method="rk4", generator=gen).cpu()
        meas = sample_covariance_trace(samples)
        x_bar_h, cov_h, neff = kernel_moments(y_i, X, Y, h)
        kern = float(torch.trace(cov_h))
        tr_meas.append(meas); tr_kern.append(kern)
        ratios.append(meas / kern if kern > 0 else np.nan)
        neffs.append(neff)
        mean_errs.append(float(torch.linalg.norm(samples.to(torch.float64).mean(0) - x_bar_h)))
    pred_trace, j_fro_sq = cov_expansion(prob, h)
    tm, tk = float(np.mean(tr_meas)), float(np.mean(tr_kern))
    return {
        "h": h, "seed": cfg["seed"],
        "trace_meas": tm,
        "trace_kernel": tk,
        "trace_post": prob.posterior_trace(),
        "trace_expansion": pred_trace,        # Prop 15 closed form
        "j_fro_sq": j_fro_sq,
        # Primary metric: ratio of mean traces (matches the WORK_ORDER section-0
        # table, which averages tr Cov over conditions). The per-condition ratio
        # is ill-conditioned at tiny h, where Cov_h -> 0 for isolated conditions
        # (single-atom collapse regime), so we report its *median* only.
        "ratio_to_kernel": tm / tk if tk > 0 else float("nan"),
        "ratio_to_kernel_median": float(np.nanmedian(ratios)),
        "ratio_to_post": tm / prob.posterior_trace(),
        "n_eff": float(np.mean(neffs)),
        "mean_err_kernel": float(np.mean(mean_errs)),
    }


def main() -> None:
    rows = []
    for h in HS:
        for s in SEEDS:
            rd = ROOT / f"p7y_h{h}_seed{s}"
            if not (rd / "checkpoints" / "ckpt_200000.pt").exists():
                print(f"  skip (missing): {rd.name}")
                continue
            r = eval_run(rd)
            rows.append(r)
            print(f"  h={h:<4} seed={s}  meas={r['trace_meas']:.3f}  "
                  f"kernel={r['trace_kernel']:.3f}  ratio_k={r['ratio_to_kernel']:.3f}  "
                  f"n_eff={r['n_eff']:.1f}")

    if not rows:
        # Checkpoints are gitignored as "regenerable", so on a clean clone (or after
        # a cleanup) every run is skipped above. Writing an empty frame here would
        # silently truncate the tracked p7_kernel.csv that Tables 5-6 are built from.
        raise SystemExit(
            "No p7y checkpoints found under "
            f"{ROOT}/p7y_h*_seed*/checkpoints/ckpt_200000.pt -- retrain those runs "
            "before re-running this script. Refusing to overwrite the existing "
            "p7_kernel.csv with an empty table."
        )

    df = pd.DataFrame(rows)
    out = ROOT / "_theory" / "raw"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "p7_kernel.csv", index=False)

    summary_rows = []
    for h, g in df.groupby("h"):
        summary_rows.append({
            "h": h, "n_seeds": len(g),
            "trace_kernel": g["trace_kernel"].mean(),
            "trace_post": g["trace_post"].mean(),
            "trace_expansion": g["trace_expansion"].mean(),
            "trace_meas_mean": g["trace_meas"].mean(),
            "trace_meas_std": g["trace_meas"].std(ddof=0),
            "ratio_to_kernel_mean": g["ratio_to_kernel"].mean(),
            "ratio_to_kernel_std": g["ratio_to_kernel"].std(ddof=0),
            "ratio_to_post_mean": g["ratio_to_post"].mean(),
            "n_eff": g["n_eff"].mean(),
        })
    sdf = pd.DataFrame(summary_rows)
    sdf.to_csv(out / "p7_kernel_summary.csv", index=False)

    print("\n=== P7 summary (mean over seeds) ===")
    print(f"{'h':>5} | {'Cov_h':>7} | {'Sig_post':>8} | {'expand':>7} | "
          f"{'measured':>16} | {'ratio_kernel':>16} | {'n_eff':>6}")
    for r in summary_rows:
        print(f"{r['h']:>5} | {r['trace_kernel']:>7.3f} | {r['trace_post']:>8.3f} | "
              f"{r['trace_expansion']:>7.3f} | "
              f"{r['trace_meas_mean']:>7.3f} +/-{r['trace_meas_std']:>6.3f} | "
              f"{r['ratio_to_kernel_mean']:>7.3f} +/-{r['ratio_to_kernel_std']:>6.3f} | "
              f"{r['n_eff']:>6.1f}")
    print(f"\nwrote {out / 'p7_kernel.csv'} and p7_kernel_summary.csv")


if __name__ == "__main__":
    main()
