"""Aggregate EXP-2 (GMM) mode-coverage metrics across seeds and plot vs iteration.

    uv run python scripts/analyze_exp2.py --runs "results/exp2/exp2_gmm_seed*" --out results/exp2/_analysis
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


def load(pattern: str) -> pd.DataFrame:
    frames = []
    for rd in sorted(glob.glob(pattern)):
        csv = Path(rd) / "raw" / "metrics.csv"
        if csv.exists():
            df = pd.read_csv(csv); df["run"] = Path(rd).name
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def agg(df, col):
    g = df.groupby("iter")[col]
    return pd.DataFrame({"mean": g.mean(), "std": g.std(ddof=0), "n": g.count()}).reset_index()


def band(ax, a, label, color):
    ax.plot(a["iter"], a["mean"], marker="o", ms=4, color=color, label=label)
    if (a["n"] > 1).any():
        ax.fill_between(a["iter"], a["mean"] - a["std"], a["mean"] + a["std"], color=color, alpha=0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", default="results/exp2/_analysis")
    args = ap.parse_args()
    out = Path(args.out); (out / "figures").mkdir(parents=True, exist_ok=True)

    df = load(args.runs)
    if df.empty:
        raise SystemExit(f"no runs matched {args.runs}")
    n_seeds = df["run"].nunique()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    band(ax1, agg(df, "mode_coverage_mean"), "mode coverage", "C3")
    ax1.axhline(1.0, color="k", ls="--", lw=1, label="full coverage")
    ax1.axhline(0.5, color="0.6", ls=":", lw=1, label="1 of 2 modes")
    ax1.set_xscale("log"); ax1.set_ylim(0, 1.05)
    ax1.set_xlabel("iteration"); ax1.set_ylabel("fraction of posterior modes covered")
    ax1.set_title(f"EXP-2 — mode coverage collapses ({n_seeds} seeds)")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

    band(ax2, agg(df, "mmd_mean"), "MMD to true posterior", "C0")
    ax2b = ax2.twinx()
    band(ax2b, agg(df, "occupancy_tv_mean"), "occupancy TV", "C1")
    ax2.set_xscale("log")
    ax2.set_xlabel("iteration"); ax2.set_ylabel("MMD (C0)")
    ax2b.set_ylabel("occupancy TV (C1)")
    ax2.set_title("EXP-2 — distance to true posterior grows")
    ax2.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "exp2_mode_coverage.png", dpi=140); plt.close(fig)

    def last(a): return {"iter": int(a["iter"].iloc[-1]), "mean": float(a["mean"].iloc[-1]),
                          "std": float(a["std"].iloc[-1])}
    summary = {
        "n_seeds": n_seeds,
        "final_mode_coverage": last(agg(df, "mode_coverage_mean")),
        "final_mmd": last(agg(df, "mmd_mean")),
        "final_occupancy_tv": last(agg(df, "occupancy_tv_mean")),
        "final_dist_to_nearest_train": last(agg(df, "dist_to_nearest_train_mean")),
        "early_mode_coverage": {"iter": int(agg(df, "mode_coverage_mean")["iter"].iloc[0]),
                                 "mean": float(agg(df, "mode_coverage_mean")["mean"].iloc[0])},
    }
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
