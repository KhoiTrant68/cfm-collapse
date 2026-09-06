"""Does the across-condition slope approach the theory's value with training?

The paper reports beta = 0.481 at h=4, where Theorem 10 predicts 1: the model
orders the conditions almost as the theory says, and compresses the range by half.
Reported as a level, that is a partial confirmation and nothing more. The question
this asks is whether it is a *transient*.

The reason to expect it might be: the conditions with the smallest tr Cov_h are the
ones whose kernel weight sits on one or two atoms, which is locally the h=0 regime
-- and h=0 collapse is optimisation-paced, taking the full 60000 iterations to fall
415x. If the deviation is an optimisation gap rather than a representation limit,
the model should be furthest above the reference exactly where the reference is
smallest, and should close that gap as training proceeds. beta would then rise
towards 1 over the run.

Two rival readings this distinguishes:

    optimisation gap    beta increases with iteration, and the paper can say the
                        theory is approached rather than missed
    representation      beta is flat, and 0.481 is a property of the model class

Competing functional forms (an additive variance floor, a hard floor, an affine
map) were fitted to the final checkpoint and all lose to the power law in log
space, so the exponent is the thing to explain.

Uses the saved intermediate checkpoints, so it needs no retraining. M is smaller
than the headline re-evaluation because a slope is unbiased under noise in the
response: measurement noise inflates the residual and depresses R^2, but does not
move the OLS estimate of beta.

    uv run python scripts/beta_trajectory.py [--M 96] [--n-conditions 48]

Reads:  results/exp3/exp3_cifar_ddpm_h{4,5,6}/checkpoints/*
Writes: results/exp3/_cifar_ddpm/beta_trajectory.json,
        paper/figures/fig_beta_trajectory.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.utils import get_device
from scripts.analyze_cifar_ddpm_stats import ols
from scripts.reeval_exp3_cifar_ddpm import reeval

RUNS = ["exp3_cifar_ddpm_h4", "exp3_cifar_ddpm_h5", "exp3_cifar_ddpm_h6"]
OUT = Path("results/exp3/_cifar_ddpm/beta_trajectory.json")
FIG = Path("paper/figures/fig_beta_trajectory.png")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9",
      "blue": "#0072B2", "vermillion": "#D55E00"}


def slope_at(r: dict) -> dict | None:
    """OLS of log measured on log predicted, across the evaluation conditions."""
    if "ratio_per_condition" not in r:
        return None
    ref = np.asarray(r["trace_kernel_per_condition"], float)
    meas = np.asarray(r["ratio_per_condition"], float) * ref
    ok = (ref > 0) & (meas > 0)
    if ok.sum() < 4:
        return None
    fit = ols(np.log10(ref[ok]), np.log10(meas[ok]))
    fit["iter"] = int(r["iter"])
    fit["h"] = float(r["h"])
    fit["decades"] = float(np.ptp(np.log10(ref[ok])))
    fit["aggregate_ratio"] = float(meas.sum() / ref.sum())
    return fit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, default=96)
    ap.add_argument("--n-conditions", type=int, default=48)
    args = ap.parse_args()
    device = get_device("auto")

    rows = []
    for run in RUNS:
        ckdir = Path("results/exp3") / run / "checkpoints"
        iters = sorted(int(p.stem.split("_")[1]) for p in ckdir.glob("ckpt_*.pt"))
        for it in iters:
            r = reeval(run, args.M, args.n_conditions, device, ckpt_iter=it)
            if r is None:
                continue
            fit = slope_at(r)
            if fit is None:
                continue
            rows.append(fit)
            print(f"  h={fit['h']:.0f} iter={fit['iter']:>6d}  "
                  f"beta={fit['slope']:+.3f} ({fit['se']:.3f})  "
                  f"R2={fit['r2']:.3f}  aggregate ratio={fit['aggregate_ratio']:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    for h, color in ((4.0, OI["blue"]), (5.0, OI["orange"]), (6.0, OI["vermillion"])):
        sub = sorted((r for r in rows if r["h"] == h), key=lambda r: r["iter"])
        if not sub:
            continue
        ax.errorbar([r["iter"] for r in sub], [r["slope"] for r in sub],
                    yerr=[r["se"] for r in sub], fmt="o-", capsize=3, color=color,
                    label=f"$h={h:.0f}$")
    ax.axhline(1.0, color=OI["black"], ls="--", lw=1.0,
               label=r"theory: $\beta=1$")
    ax.axhline(0.0, color=OI["black"], ls=":", lw=0.8,
               label=r"no tracking: $\beta=0$")
    ax.set_xscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel(r"across-condition slope $\beta$")
    ax.set_title("Does the model approach the kernel prediction, or sit beside it?")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=200)
    plt.close(fig)
    print(f"\nSaved: {OUT}, {FIG}")


if __name__ == "__main__":
    main()
