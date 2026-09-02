"""Aggregate EXP-1 metrics across seeds and render the core P1/P2/P3/P4 figures.

Reads ``raw/metrics.csv`` from one or more run directories (globbed), averages
across seeds (mean +/- std), and writes figures + a summary JSON.

Usage
-----
    uv run python scripts/analyze_exp1.py \
        --cond "results/exp1/exp1_cond_seed*" \
        --uncond "results/exp1/exp1_uncond_seed*" \
        --out results/exp1/_analysis
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils import glob_seed_runs  # noqa: E402


def load_runs(pattern: str, group: str) -> pd.DataFrame:
    frames = []
    for run_dir in glob_seed_runs(pattern):
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


def agg_over_seeds(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Return per-iter mean/std of ``col`` across seeds/runs."""
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=["iter", "mean", "std", "n"])
    g = df.groupby("iter")[col]
    out = pd.DataFrame({"mean": g.mean(), "std": g.std(ddof=0), "n": g.count()}).reset_index()
    return out


def _plot_band(ax, agg, label, color, ls="-"):
    if agg.empty:
        return
    ax.plot(agg["iter"], agg["mean"], marker="o", ms=4, label=label, color=color, ls=ls)
    if (agg["n"] > 1).any():
        ax.fill_between(agg["iter"], agg["mean"] - agg["std"], agg["mean"] + agg["std"],
                        color=color, alpha=0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True, help="glob for conditional run dirs")
    ap.add_argument("--uncond", default="", help="glob for unconditional run dirs")
    ap.add_argument("--out", default="results/exp1/_analysis")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    cond = load_runs(args.cond, "train")
    cond_ho = load_runs(args.cond, "heldout")
    uncond = load_runs(args.uncond, "uncond") if args.uncond else pd.DataFrame()

    if cond.empty:
        raise SystemExit(f"No conditional runs matched {args.cond!r}")

    # trace_post / trace_data are per-run constants that depend on the seed (the
    # seed draws the problem instance A and the dataset), so `.iloc[0]` would pin
    # the reference line to seed 0 while the plotted curves are seed means. Over
    # 5 seeds trace_data ranges 1.76-2.17; using seed 0's 2.17 against a 5-seed
    # mean curve understates how exactly the unconditional run matches Sigma_X.
    def _ref(df, col):
        per_run = df.groupby("run")[col].first()
        return float(per_run.mean()), float(per_run.std(ddof=0))

    trace_post, trace_post_sd = _ref(cond, "trace_post")
    n_seeds = cond["run"].nunique()

    # ---------------- P1: variance collapse ---------------------------------
    tc = agg_over_seeds(cond, "trace_cov_mean")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, tc, "conditional (generated)", "C3")
    ax.axhline(trace_post, color="k", ls="--", lw=1.2, label=f"trace(Σ_post)={trace_post:.3f}±{trace_post_sd:.3f}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("trace(Cov) of generated samples")
    ax.set_title(f"P1 — Posterior variance collapse ({n_seeds} seed(s))")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "P1_variance_collapse.png", dpi=140)
    plt.close(fig)

    # ---------------- P2: velocity error vs closed form ---------------------
    ve = agg_over_seeds(cond, "vel_rel_err_mean_mean")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, ve, "relative L2 error vs (★)", "C0")
    ax.set_xscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel("‖v_θ − v*‖ / ‖v*‖  (mean over conditions)")
    ax.set_title(f"P2 — Convergence to closed-form minimizer (★) ({n_seeds} seed(s))")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "P2_velocity_error.png", dpi=140)
    plt.close(fig)

    # ---------------- P4: conditional vs unconditional ----------------------
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, tc, "conditional", "C3")
    if not uncond.empty:
        tcu = agg_over_seeds(uncond, "trace_cov_mean")
        _plot_band(ax, tcu, "unconditional (baseline)", "C2", ls="-")
        if "trace_data" in uncond.columns:
            td, td_sd = _ref(uncond, "trace_data")
            ax.axhline(td, color="C2", ls=":", lw=1.0,
                       label=f"trace(Σ̂_X)={td:.3f}±{td_sd:.3f}")
    ax.axhline(trace_post, color="k", ls="--", lw=1.0, label=f"trace(Σ_post)={trace_post:.3f}±{trace_post_sd:.3f}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("trace(Cov) of generated samples")
    ax.set_title(f"P4 — Conditional vs unconditional ({n_seeds} seed(s))")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "P4_cond_vs_uncond.png", dpi=140)
    plt.close(fig)

    # ---------------- P3 (bonus): collapse toward the training point --------
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    mex = agg_over_seeds(cond, "mean_err_train_point_mean")
    mep = agg_over_seeds(cond, "mean_err_post_mean")
    don = agg_over_seeds(cond, "dist_to_nearest_other_mean")
    _plot_band(ax, mex, "‖mean − x^i‖ (own train point)", "C3")
    _plot_band(ax, mep, "‖mean − μ_post(y^i)‖", "C0")
    _plot_band(ax, don, "dist to nearest other x^j", "C7", ls=":")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("distance")
    ax.set_title(f"P3 — Sample mean collapses to the training point ({n_seeds} seed(s))")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "P3_collapse_to_train_point.png", dpi=140)
    plt.close(fig)

    # ---------------- numeric summary ---------------------------------------
    def last(agg):
        return None if agg.empty else {"iter": int(agg["iter"].iloc[-1]),
                                       "mean": float(agg["mean"].iloc[-1]),
                                       "std": float(agg["std"].iloc[-1])}
    summary = {
        "n_seeds_cond": int(n_seeds),
        "trace_post": trace_post,
        "final_cond_trace_cov": last(tc),
        "final_cond_vel_rel_err": last(ve),
        "final_cond_mean_err_train_point": last(mex),
        "final_cond_mean_err_post": last(mep),
    }
    if not uncond.empty:
        summary["n_seeds_uncond"] = int(uncond["run"].nunique())
        summary["final_uncond_trace_cov"] = last(agg_over_seeds(uncond, "trace_cov_mean"))
        summary["trace_data"] = _ref(uncond, "trace_data")[0] if "trace_data" in uncond else None
    if not cond_ho.empty:
        summary["final_heldout_trace_cov"] = last(agg_over_seeds(cond_ho, "trace_cov_mean"))
        summary["final_heldout_mean_err_post"] = last(agg_over_seeds(cond_ho, "mean_err_post_mean"))

    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nFigures + summary written to {out}")


if __name__ == "__main__":
    main()
