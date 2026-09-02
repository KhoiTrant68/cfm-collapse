"""Analyze the 5-seed extended run WITH a cosine LR schedule
(configs/exp1_extended_schedule.yaml), and compare against the original
single-seed fixed-LR extended run (exp1_cond_seed0_ext) which diverges near
10^6 iterations. Produces the figure replacing fig_extended.png.

Usage
-----
    uv run python scripts/analyze_exp1_extended_schedule.py \
        --sched "results/exp1/exp1_ext_sched_seed*" \
        --fixed_lr results/exp1/exp1_cond_seed0_ext \
        --out results/exp1/_analysis_ext_sched
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def load_runs(pattern: str, group: str = "train") -> pd.DataFrame:
    frames = []
    for run_dir in sorted(glob.glob(pattern)):
        csv = Path(run_dir) / "raw" / "metrics.csv"
        if not csv.exists():
            continue
        df = pd.read_csv(csv)
        df = df[df["group"] == group].copy()
        df["run"] = Path(run_dir).name
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def agg(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=["iter", "mean", "std", "n"])
    g = df.groupby("iter")[col]
    return pd.DataFrame({"mean": g.mean(), "std": g.std(ddof=0), "n": g.count()}).reset_index()


def _plot_band(ax, a, label, color, ls="-", marker="o"):
    if a.empty:
        return
    ax.plot(a["iter"], a["mean"], marker=marker, ms=4, label=label, color=color, ls=ls)
    if (a["n"] > 1).any():
        ax.fill_between(a["iter"], a["mean"] - a["std"], a["mean"] + a["std"], color=color, alpha=0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sched", required=True)
    ap.add_argument("--fixed_lr", default="")
    ap.add_argument("--out", default="results/exp1/_analysis_ext_sched")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    sched = load_runs(args.sched)
    n_seeds = sched["run"].nunique()

    cols = ["trace_cov_mean", "vel_rel_err_mean_mean", "mean_err_train_point_mean", "train_loss"]
    labels = ["trace(Cov)", "vel. rel. error", "||mean-x^i||", "train loss"]
    colors = ["C3", "C0", "C1", "C7"]

    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for c, lab, col in zip(cols, labels, colors):
        _plot_band(ax, agg(sched, c), f"{lab} (schedule, {n_seeds} seeds)", col)
    if args.fixed_lr:
        fixed = load_runs(args.fixed_lr)
        if not fixed.empty:
            fixed = fixed[fixed["iter"] <= 700000]  # exclude the post-divergence point
            _plot_band(ax, agg(fixed, "trace_cov_mean"), "trace(Cov) (fixed lr, 1 seed, pre-divergence)",
                      "C3", ls="--", marker="x")
    ax.axvline(1000000, color="gray", ls=":", lw=1.0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("metric value")
    ax.set_title(f"Cosine LR schedule avoids divergence, tracked to 1e6 iters ({n_seeds} seeds)")
    ax.legend(fontsize=7); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "extended_schedule.png", dpi=140)
    plt.close(fig)

    summary = {"n_seeds": int(n_seeds)}
    for c in cols + ["mean_err_post_mean", "memorization_ratio_mean"]:
        a = agg(sched, c)
        if not a.empty:
            last = a.iloc[-1]
            summary[c] = {"iter": int(last["iter"]), "mean": float(last["mean"]), "std": float(last["std"])}
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nFigure + summary written to {out}")


if __name__ == "__main__":
    main()
