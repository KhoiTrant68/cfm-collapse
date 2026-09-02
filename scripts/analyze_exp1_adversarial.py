"""Adversarial-pairing ablation: does conditional collapse need a *real* posterior?

Compares the real-pairing EXP-1 baseline (exp1_cond_seed*) against a variant
where Y is randomly permuted relative to X before training
(exp1_adv_shuffle_seed*, data.shuffle_labels=true in
configs/exp1_adversarial_shuffle.yaml). Proposition 4 only needs the y^i to be
pairwise distinct -- it never uses the true forward operator A -- so the
population theory predicts the SAME collapse curve (trace_cov, mean_err to the
assigned x^i) under shuffled labels, while mean_err_post (distance to the
*true* analytic posterior mean of that y, unrelated to the shuffled x^i)
should NOT collapse to zero. This is the conditional analogue of the
"Adversarial Pairings" experiment in Reu et al. (arXiv:2510.18118, cited as
gradvar2025 in the paper).

Usage
-----
    uv run python scripts/analyze_exp1_adversarial.py \
        --real "results/exp1/exp1_cond_seed*" \
        --shuffled "results/exp1/exp1_adv_shuffle_seed*" \
        --out results/exp1/_analysis_adversarial
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils import glob_seed_runs  # noqa: E402


def load_runs(pattern: str, group: str = "train") -> pd.DataFrame:
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
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=["iter", "mean", "std", "n"])
    g = df.groupby("iter")[col]
    return pd.DataFrame({"mean": g.mean(), "std": g.std(ddof=0), "n": g.count()}).reset_index()


def _plot_band(ax, agg, label, color, ls="-"):
    if agg.empty:
        return
    ax.plot(agg["iter"], agg["mean"], marker="o", ms=4, label=label, color=color, ls=ls)
    if (agg["n"] > 1).any():
        ax.fill_between(agg["iter"], agg["mean"] - agg["std"], agg["mean"] + agg["std"],
                         color=color, alpha=0.2)


def last(agg):
    return None if agg.empty else {"iter": int(agg["iter"].iloc[-1]),
                                    "mean": float(agg["mean"].iloc[-1]),
                                    "std": float(agg["std"].iloc[-1])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", required=True, help="glob for real-pairing run dirs (exp1_cond_seed*)")
    ap.add_argument("--shuffled", required=True, help="glob for shuffled-label run dirs")
    ap.add_argument("--out", default="results/exp1/_analysis_adversarial")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    real = load_runs(args.real)
    shuf = load_runs(args.shuffled)
    if real.empty:
        raise SystemExit(f"No real-pairing runs matched {args.real!r}")
    if shuf.empty:
        raise SystemExit(f"No shuffled-label runs matched {args.shuffled!r}")

    n_real = real["run"].nunique()
    n_shuf = shuf["run"].nunique()
    trace_post = float(real["trace_post"].iloc[0])

    tc_real = agg_over_seeds(real, "trace_cov_mean")
    tc_shuf = agg_over_seeds(shuf, "trace_cov_mean")
    mex_real = agg_over_seeds(real, "mean_err_train_point_mean")
    mex_shuf = agg_over_seeds(shuf, "mean_err_train_point_mean")
    mep_real = agg_over_seeds(real, "mean_err_post_mean")
    mep_shuf = agg_over_seeds(shuf, "mean_err_post_mean")

    # ---- Figure 1: trace(Cov) collapse, real vs shuffled pairing -----------
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, tc_real, f"real pairing ({n_real} seeds)", "C3")
    _plot_band(ax, tc_shuf, f"shuffled labels ({n_shuf} seeds)", "C1", ls="--")
    ax.axhline(trace_post, color="k", ls=":", lw=1.0, label=f"trace(Σ_post)={trace_post:.3f}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("trace(Cov) of generated samples")
    ax.set_title("Adversarial pairing: collapse persists under shuffled labels")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "adv_trace_cov.png", dpi=140)
    plt.close(fig)

    # ---- Figure 2: distance to assigned x^i vs distance to true mu_post ----
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    _plot_band(ax, mex_real, "‖mean − x^i‖, real pairing", "C3")
    _plot_band(ax, mex_shuf, "‖mean − x^i‖, shuffled (assigned point)", "C1", ls="--")
    _plot_band(ax, mep_shuf, "‖mean − μ_post(y^i)‖, shuffled (true-but-irrelevant posterior)", "C0", ls="-.")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel("distance")
    ax.set_title("Shuffled labels: mean converges to assigned x^i, not μ_post(y^i)",
                 fontsize=11)
    ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out / "figures" / "adv_mean_targets.png", dpi=140)
    plt.close(fig)

    summary = {
        "n_seeds_real": int(n_real),
        "n_seeds_shuffled": int(n_shuf),
        "trace_post": trace_post,
        "final_trace_cov_real": last(tc_real),
        "final_trace_cov_shuffled": last(tc_shuf),
        "final_mean_err_train_point_real": last(mex_real),
        "final_mean_err_train_point_shuffled": last(mex_shuf),
        "final_mean_err_post_real": last(mep_real),
        "final_mean_err_post_shuffled": last(mep_shuf),
    }
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nFigures + summary written to {out}")


if __name__ == "__main__":
    main()
