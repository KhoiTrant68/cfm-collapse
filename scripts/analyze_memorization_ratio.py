"""Memorization-ratio diagnostic (Yoon et al. 2023 / arXiv:2508.17689, c=1/9):
fraction of generated samples whose nearest training point dominates the
second-nearest one. Complements the trace(Cov)-based P1/P4 diagnostics with a
per-sample, literature-standard number.

Usage
-----
    uv run python scripts/analyze_memorization_ratio.py \
        --cond "results/exp1/exp1_cond_seed*_mr" \
        --uncond "results/exp1/exp1_uncond_seed*_mr" \
        --exp2 "results/exp2/exp2b_gmm_seed*_mr" \
        --out results/exp1/_analysis_memratio
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


def load_runs(pattern: str, group: str) -> pd.DataFrame:
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


def _plot_band(ax, a, label, color, ls="-"):
    if a.empty:
        return
    ax.plot(a["iter"], a["mean"], marker="o", ms=4, label=label, color=color, ls=ls)
    if (a["n"] > 1).any():
        ax.fill_between(a["iter"], a["mean"] - a["std"], a["mean"] + a["std"], color=color, alpha=0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True)
    ap.add_argument("--uncond", required=True)
    ap.add_argument("--exp2", default="")
    ap.add_argument("--out", default="results/exp1/_analysis_memratio")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    cond = load_runs(args.cond, "train")
    uncond = load_runs(args.uncond, "uncond")
    n_cond, n_uncond = cond["run"].nunique(), uncond["run"].nunique()

    mr_cond = agg(cond, "memorization_ratio_mean")
    mr_uncond = agg(uncond, "memorization_ratio_mean")

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, mr_cond, f"conditional ({n_cond} seeds)", "C3")
    _plot_band(ax, mr_uncond, f"unconditional ({n_uncond} seeds)", "C2")
    ax.set_xscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel("memorization ratio ($c=1/9$)")
    ax.set_title("Memorization ratio (Yoon et al. 2023): both rise, conditional far more")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "memorization_ratio.png", dpi=140)
    plt.close(fig)

    summary = {
        "n_seeds_cond": int(n_cond), "n_seeds_uncond": int(n_uncond),
        "cond_final": None if mr_cond.empty else mr_cond.iloc[-1].to_dict(),
        "uncond_final": None if mr_uncond.empty else mr_uncond.iloc[-1].to_dict(),
    }

    if args.exp2:
        exp2 = load_runs(args.exp2, "train")
        n_exp2 = exp2["run"].nunique()
        mr_exp2 = agg(exp2, "memorization_ratio_mean")
        summary["n_seeds_exp2"] = int(n_exp2)
        summary["exp2_final"] = None if mr_exp2.empty else mr_exp2.iloc[-1].to_dict()

    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nFigure + summary written to {out}")


if __name__ == "__main__":
    main()
