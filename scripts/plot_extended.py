"""Plot the extended (long-overtraining) conditional run: collapse metrics vs
iteration on a shared log-x axis, with a marker where fixed-lr optimization
eventually destabilizes.

Usage
-----
    uv run python scripts/plot_extended.py \
        --run results/exp1/exp1_cond_seed0_ext \
        --out results/exp1/_analysis/figures/extended_trajectory.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Anything above this is treated as an ODE/optimization divergence, not a
# meaningful variance, and is drawn as an "x" on a capped axis.
DIVERGE = 1e3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_csv(Path(args.run) / "raw" / "metrics.csv")
    tr = df[df.group == "train"].sort_values("iter")
    trace_post = float(df.trace_post.iloc[0])

    it = tr["iter"].to_numpy()
    tc = tr["trace_cov_mean"].to_numpy()
    ve = tr["vel_rel_err_mean_mean"].to_numpy()
    mx = tr["mean_err_train_point_mean"].to_numpy()
    loss = tr["train_loss"].to_numpy()

    diverged = (tc > DIVERGE) | (mx > DIVERGE)

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.set_xscale("log"); ax.set_yscale("log")

    def plot_series(y, color, label, marker="o"):
        good = ~diverged & np.isfinite(y) & (y > 0)
        ax.plot(it[good], y[good], marker=marker, ms=5, color=color, label=label)

    plot_series(tc, "C3", "trace(Cov) [P1]")
    plot_series(ve, "C0", "rel. velocity error vs (★) [P2]")
    plot_series(mx, "C1", "‖mean − x^i‖ [P3]")
    plot_series(loss, "C7", "train loss")
    ax.axhline(trace_post, color="k", ls="--", lw=1.0, label=f"trace(Σ_post)={trace_post:.3f}")

    # mark divergence
    if diverged.any():
        xd = it[diverged][0]
        ax.axvline(xd, color="0.5", ls=":", lw=1.2)
        ax.text(xd, ax.get_ylim()[1], "  fixed-lr\n  divergence",
                va="top", ha="left", fontsize=8, color="0.35")

    ax.set_xlabel("training iteration")
    ax.set_ylabel("metric value")
    ax.set_title("Extended overtraining (seed 0): collapse deepens as loss→0, "
                 "until optimization destabilizes")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=140)
    print(f"wrote {args.out}")

    # print the pre-divergence best values
    good = ~diverged
    best_i = int(np.nanargmin(np.where(good, tc, np.inf)))
    print(f"min trace_cov (pre-divergence): {tc[best_i]:.4f} at iter {int(it[best_i])} "
          f"(vel_err={ve[best_i]:.3f}, mean_err_x={mx[best_i]:.3f}, loss={loss[best_i]:.3f})")


if __name__ == "__main__":
    main()
