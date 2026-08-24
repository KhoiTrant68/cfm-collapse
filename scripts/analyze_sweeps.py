"""Analyze Phase-B sweeps (P5 sigma_obs, P6 N, P7 remedies, d/k).

Reads the final-checkpoint train-group metrics from each sweep run, aggregates
across seeds, and renders one figure per prediction plus a JSON/markdown summary.
Robust to still-running sweeps (missing runs are skipped).

    uv run python scripts/analyze_sweeps.py --root results/exp1 --out results/exp1/_sweeps
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def final_row(run_dir: Path) -> dict | None:
    csv = run_dir / "raw" / "metrics.csv"
    if not csv.exists():
        return None
    df = pd.read_csv(csv)
    df = df[df["group"] == "train"]
    if df.empty:
        return None
    return df.sort_values("iter").iloc[-1].to_dict()


def collect(root: Path, pattern: str, value_regex: str) -> pd.DataFrame:
    """Return per-run final metrics with the swept value parsed from the name."""
    rows = []
    for rd in sorted(glob.glob(str(root / pattern))):
        rd = Path(rd)
        m = re.search(value_regex, rd.name)
        if not m:
            continue
        fr = final_row(rd)
        if fr is None:
            continue
        fr["_value"] = float(m.group(1))
        fr["_run"] = rd.name
        rows.append(fr)
    return pd.DataFrame(rows)


def agg(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=["_value", "mean", "std", "n"])
    g = df.groupby("_value")[col]
    return pd.DataFrame({"mean": g.mean(), "std": g.std(ddof=0), "n": g.count()}).reset_index()


def errbar(ax, a, label, color, **kw):
    if a.empty:
        return
    ax.errorbar(a["_value"], a["mean"], yerr=a["std"], marker="o", capsize=3,
                label=label, color=color, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/exp1")
    ap.add_argument("--out", default="results/exp1/_sweeps")
    args = ap.parse_args()
    root = Path(args.root)
    out = Path(args.out); (out / "figures").mkdir(parents=True, exist_ok=True)
    summary = {}

    # reference (main) runs = sigma_obs 0.1, N 200, h 0
    ref = collect(root, "exp1_cond_seed[0-9]", r"seed(\d+)")
    ref_tc = float(ref["trace_cov_mean"].mean()) if not ref.empty else None
    ref_tp = float(ref["trace_post"].mean()) if not ref.empty else None

    # ---------------- P5: sigma_obs ----------------------------------------
    p5 = collect(root, "p5_sobs*_seed*", r"sobs([0-9.]+)_")
    if not ref.empty:
        r = ref.copy(); r["_value"] = 0.1; p5 = pd.concat([p5, r], ignore_index=True)
    if not p5.empty:
        fig, ax = plt.subplots(figsize=(6.5, 4.2))
        errbar(ax, agg(p5, "trace_cov_mean"), "generated trace(Cov)", "C3")
        errbar(ax, agg(p5, "trace_post"), "trace(Σ_post) (truth)", "k")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("σ_obs"); ax.set_ylabel("trace(Cov) @ 200k")
        ax.set_title("P5 — collapse vs observation noise σ_obs")
        ax.legend(); ax.grid(True, which="both", alpha=0.3)
        fig.tight_layout(); fig.savefig(out / "figures" / "P5_sigma_obs.png", dpi=140); plt.close(fig)
        a_tc = agg(p5, "trace_cov_mean"); a_tp = agg(p5, "trace_post")
        summary["P5"] = {"sigma_obs": a_tc["_value"].tolist(),
                          "trace_cov": a_tc["mean"].tolist(),
                          "trace_post": a_tp["mean"].tolist(),
                          "ratio": (a_tc["mean"].values / a_tp["mean"].values).tolist()}

    # ---------------- P6: N -------------------------------------------------
    p6 = collect(root, "p6_N*_seed*", r"N(\d+)_")
    if not ref.empty:
        r = ref.copy(); r["_value"] = 200; p6 = pd.concat([p6, r], ignore_index=True)
    if not p6.empty:
        p6["ratio"] = p6["trace_cov_mean"] / p6["trace_post"]
        fig, ax = plt.subplots(figsize=(6.5, 4.2))
        errbar(ax, agg(p6, "ratio"), "trace(Cov)/trace(Σ_post)", "C3")
        ax.axhline(1.0, color="k", ls="--", lw=1, label="no collapse (=1)")
        ax.set_xscale("log")
        ax.set_xlabel("N (training set size)"); ax.set_ylabel("collapse ratio @ 200k")
        ax.set_title("P6 — collapse vs dataset size N (fixed capacity)")
        ax.legend(); ax.grid(True, which="both", alpha=0.3)
        fig.tight_layout(); fig.savefig(out / "figures" / "P6_N.png", dpi=140); plt.close(fig)
        a = agg(p6, "ratio")
        summary["P6"] = {"N": a["_value"].tolist(), "collapse_ratio": a["mean"].tolist()}

    # ---------------- P7: remedies -----------------------------------------
    p7y = collect(root, "p7y_h*_seed*", r"h([0-9.]+)_")
    if not ref.empty:
        r = ref.copy(); r["_value"] = 0.0; p7y = pd.concat([p7y, r], ignore_index=True)
    p7i = collect(root, "p7i_sig*_seed*", r"sig([0-9.]+)_")
    if not p7y.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        errbar(ax1, agg(p7y, "trace_cov_mean"), "y-noise (P7): trace(Cov)", "C3")
        if ref_tp:
            ax1.axhline(ref_tp, color="k", ls="--", lw=1, label="trace(Σ_post)")
        ax1.set_xlabel("y-noise bandwidth h"); ax1.set_ylabel("trace(Cov) @ 200k")
        ax1.set_title("P7 — variance restored by smoothing y"); ax1.legend(); ax1.grid(alpha=0.3)
        errbar(ax2, agg(p7y, "mean_err_post_mean"), "y-noise (P7): ‖mean−μ_post‖", "C0")
        ax2.set_xlabel("y-noise bandwidth h"); ax2.set_ylabel("posterior-mean error (bias)")
        ax2.set_title("P7 — bias introduced by the remedy"); ax2.legend(); ax2.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(out / "figures" / "P7_y_noise.png", dpi=140); plt.close(fig)
        ay = agg(p7y, "trace_cov_mean"); ab = agg(p7y, "mean_err_post_mean")
        summary["P7y"] = {"h": ay["_value"].tolist(), "trace_cov": ay["mean"].tolist(),
                           "mean_err_post": ab["mean"].tolist()}
    if not p7i.empty:
        ai = agg(p7i, "trace_cov_mean"); ab = agg(p7i, "mean_err_post_mean")
        summary["P7i"] = {"interp_sigma": ai["_value"].tolist(),
                           "trace_cov": ai["mean"].tolist(),
                           "mean_err_post": ab["mean"].tolist()}

    # ---------------- d/k ---------------------------------------------------
    dk_rows = []
    for rd in sorted(glob.glob(str(root / "dk_d*k*_seed*"))):
        rd = Path(rd)
        m = re.search(r"d(\d+)k(\d+)_seed(\d+)", rd.name)
        fr = final_row(rd)
        if fr and m:
            fr["d"] = int(m.group(1)); fr["k"] = int(m.group(2))
            dk_rows.append(fr)
    if not ref.empty:
        r0 = ref.iloc[0].to_dict(); r0["d"] = 2; r0["k"] = 1
    if dk_rows:
        dfdk = pd.DataFrame(dk_rows)
        dfdk["ratio"] = dfdk["trace_cov_mean"] / dfdk["trace_post"]
        g = dfdk.groupby(["d", "k"])["ratio"].mean().reset_index()
        summary["dk"] = g.to_dict(orient="records")

    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"\nWrote figures + summary to {out}")


if __name__ == "__main__":
    main()
