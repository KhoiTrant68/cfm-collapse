"""Generate additional publication figures for the manuscript from the theory CSVs.

These visualise results that are currently text/table-only in the paper: the
optimality gap (T5), the atomicity / posterior-distance floor (T7), the Lipschitz
representation floor (T6), and a consolidated P7 kernel-tracking summary. Output PNGs
go straight into paper/figures/.

    uv run python scripts/make_paper_figures.py

Design: colourblind-safe Okabe-Ito palette in fixed order; one y-axis per panel (no
dual-axis); recessive grid; a legend whenever >=2 series are drawn.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("results/exp1/_theory/raw")
OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colourblind-safe palette, fixed order.
OI = {
    "black": "#000000", "orange": "#E69F00", "sky": "#56B4E9",
    "green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
    "vermillion": "#D55E00", "purple": "#CC79A7",
}
H_COLORS = {0.0: OI["black"], 0.01: OI["orange"], 0.05: OI["sky"],
            0.1: OI["green"], 0.5: OI["blue"]}

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#cccccc", "grid.alpha": 0.4,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
    "lines.linewidth": 2.0, "lines.markersize": 7,
})


def style(ax):
    ax.tick_params(length=3, width=0.8)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.8)


# --------------------------------------------------------------------------
def fig_optimality_gap():
    df = pd.read_csv(ROOT / "optimality_gap.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    for h, g in df.groupby("h"):
        g = g.sort_values("iter")
        ax1.plot(g["iter"], g["gap"], marker="o", color=H_COLORS.get(h, "gray"),
                 label=f"$h={h:g}$")
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("iteration"); ax1.set_ylabel(r"gap $L(v_\theta)-L(v_h^\star)$")
    ax1.set_title("(a) optimality gap decays to 0 at every $h$")
    ax1.legend(title=None, ncol=2, fontsize=9)
    style(ax1)

    # irreducible error L_star at the final checkpoint vs h
    last = df.sort_values("iter").groupby("h").tail(1).sort_values("h")
    ax2.plot(last["h"], last["L_star"], marker="s", color=OI["vermillion"])
    for _, r in last.iterrows():
        ax2.annotate(f"{r['L_star']:.2f}", (r["h"], r["L_star"]),
                     textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax2.set_xlabel("label-noise bandwidth $h$")
    ax2.set_ylabel(r"irreducible error $L(v_h^\star)$")
    ax2.set_title("(b) smoothing raises the irreducible error")
    style(ax2)
    fig.tight_layout(); fig.savefig(OUT / "fig_optgap.png"); plt.close(fig)
    print("wrote fig_optgap.png")


def fig_posterior_distance():
    df = pd.read_csv(ROOT / "posterior_distance_exp1.csv").sort_values("h")
    x = np.arange(len(df)); labels = [f"{h:g}" for h in df["h"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    ax1.errorbar(x, df["mmd_to_post"], yerr=df["mmd_std"], marker="o",
                 color=OI["blue"], capsize=3, label="MMD to true posterior")
    ax1.axhline(0, color=OI["vermillion"], ls="--", lw=1.5,
                label="continuous-posterior target (0)")
    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_xlabel("label-noise bandwidth $h$"); ax1.set_ylabel("MMD to posterior")
    ax1.set_title("(a) MMD falls with $h$ but never reaches 0")
    ax1.legend(fontsize=9); style(ax1)

    ax2.plot(x, df["sinkhorn_to_post"], marker="s", color=OI["green"],
             label="Sinkhorn to posterior")
    ax2.axhline(df["sinkhorn_to_post"].min(), color="#888888", ls=":", lw=1.2)
    ax2.set_xticks(x); ax2.set_xticklabels(labels)
    ax2.set_xlabel("label-noise bandwidth $h$"); ax2.set_ylabel("Sinkhorn distance")
    ax2.set_title("(b) Sinkhorn plateaus above 0 (atomicity floor)")
    ax2.legend(fontsize=9); style(ax2)
    fig.tight_layout(); fig.savefig(OUT / "fig_posterior_distance.png"); plt.close(fig)
    print("wrote fig_posterior_distance.png")


def fig_lipschitz():
    df = pd.read_csv(ROOT / "lipschitz.csv").sort_values("t")
    x = np.arange(len(df)); labels = [f"{t:g}" for t in df["t"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    ax1.plot(x, df["L_max"], marker="o", color=OI["vermillion"], label=r"$\max$")
    ax1.plot(x, df["L_p95"], marker="^", color=OI["orange"], label="p95")
    ax1.plot(x, df["L_med"], marker="s", color=OI["blue"], label="median")
    ax1.set_yscale("log")
    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_xlabel("time $t$"); ax1.set_ylabel(r"empirical $\mathrm{Lip}_x v_\theta$")
    ax1.set_title("(a) learned field steepens as $t\\to1$")
    ax1.legend(fontsize=9); style(ax1)

    ax2.plot(x, df["floor_d_over_3L"], marker="o", color=OI["green"],
             label=r"representation floor $d/(3L)$")
    ax2.axhline(df["L_trained"].iloc[0], color=OI["black"], ls="--", lw=1.5,
                label=f"observed plateau ({df['L_trained'].iloc[0]:.2f})")
    ax2.set_yscale("log")
    ax2.set_xticks(x); ax2.set_xticklabels(labels)
    ax2.set_xlabel("time $t$"); ax2.set_ylabel("loss scale")
    ax2.set_title(r"(b) floor $\ll$ plateau $\Rightarrow$ optimisation-limited")
    ax2.legend(fontsize=9); style(ax2)
    fig.tight_layout(); fig.savefig(OUT / "fig_lipschitz.png"); plt.close(fig)
    print("wrote fig_lipschitz.png")


def fig_p7_summary():
    df = pd.read_csv(ROOT / "p7_kernel.csv")
    g = df.groupby("h")
    hs = sorted(df["h"].unique())
    x = np.arange(len(hs)); labels = [f"{h:g}" for h in hs]
    meas_m = g["trace_meas"].mean().reindex(hs)
    meas_s = g["trace_meas"].std(ddof=0).reindex(hs)
    kern = g["trace_kernel"].mean().reindex(hs)
    post = g["trace_post"].mean().reindex(hs)
    ratio_m = g["ratio_to_kernel"].mean().reindex(hs)
    ratio_s = g["ratio_to_kernel"].std(ddof=0).reindex(hs)
    neff = g["n_eff"].mean().reindex(hs)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4.2))
    ax1.errorbar(x, meas_m, yerr=meas_s, marker="o", color=OI["blue"],
                 capsize=3, label=r"measured $\mathrm{tr}\,\mathrm{Cov}$ (5 seeds)")
    ax1.plot(x, kern, marker="s", color=OI["vermillion"], ls="--",
             label=r"kernel target $\mathrm{tr}\,\mathrm{Cov}_h$ (Thm 2)")
    ax1.plot(x, post, marker="^", color=OI["green"], ls=":",
             label=r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_xlabel("bandwidth $h$"); ax1.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$")
    ax1.set_title("(a) model tracks $\\mathrm{Cov}_h$, not $\\Sigma_{\\mathrm{post}}$")
    ax1.legend(fontsize=8.5); style(ax1)

    ax2.axhspan(0.95, 1.05, color=OI["green"], alpha=0.12)
    ax2.errorbar(x, ratio_m, yerr=ratio_s, marker="o", color=OI["blue"], capsize=3)
    ax2.axhline(1.0, color=OI["black"], ls="--", lw=1.2)
    ax2.set_xticks(x); ax2.set_xticklabels(labels)
    ax2.set_xlabel("bandwidth $h$"); ax2.set_ylabel("ratio to kernel")
    ax2.set_title("(b) ratio-to-kernel $\\approx 1$ for $h\\geq0.05$")
    style(ax2)

    ax3.plot(x, neff, marker="s", color=OI["purple"])
    ax3.axhline(200, color="#888888", ls=":", lw=1.2)
    ax3.annotate("N = 200 atoms", (x[0], 200), textcoords="offset points",
                 xytext=(4, -12), fontsize=9, color="#555555")
    for xi, v in zip(x, neff):
        ax3.annotate(f"{v:.0f}", (xi, v), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=9)
    ax3.set_xticks(x); ax3.set_xticklabels(labels)
    ax3.set_xlabel("bandwidth $h$"); ax3.set_ylabel(r"effective # atoms $n_{\mathrm{eff}}$")
    ax3.set_title("(c) generated law stays atomic ($n_{\\mathrm{eff}}\\ll N$)")
    style(ax3)
    fig.tight_layout(); fig.savefig(OUT / "fig_p7_summary.png"); plt.close(fig)
    print("wrote fig_p7_summary.png")


if __name__ == "__main__":
    fig_optimality_gap()
    fig_posterior_distance()
    fig_lipschitz()
    fig_p7_summary()
    print("done")
