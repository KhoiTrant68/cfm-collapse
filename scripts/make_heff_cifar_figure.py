"""Figure: the effective bandwidth over training at image scale (CIFAR-10, DDPM U-Net).

One panel per training bandwidth h: h_eff fitted to the per-condition variances
(filled) and the bandwidth implied by the per-condition means (open), with 95%
bootstrap intervals over the 48 conditions, at every archived checkpoint of each run.
The dashed rule is h; the cross is the published seed-0 run's h_eff at 60000
iterations. The last panel plots the paper's across-condition slope beta against
h_eff / h at the same checkpoints.

Checkpoints before 5000 iterations are drawn in the bandwidth panels but left out of
the beta panel: at 2000 the model has not learned the conditional structure and the
two bandwidths disagree.

Reads:  results/exp3/_heff/heff_exp3_cifar_heff_h*_s*.json
Writes: paper/figures/fig_heff_cifar.png

Usage:
    PYTHONPATH=. uv run python scripts/make_heff_cifar_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, OI, save, style, use_paper_style

SRC = sorted(Path("results/exp3/_heff").glob("heff_exp3_cifar_heff_h*_s*.json"))
PUBLISHED_HEFF = {4.0: 4.80, 5.0: 5.75, 6.0: 7.05}   # seed 0, 60000 iterations
SEED_COLORS = {0: OI["blue"], 1: OI["vermillion"], 2: OI["green"]}
H_MARKERS = {4.0: "o", 5.0: "s", 6.0: "^"}
MIN_ITER_B = 5000
TICKS = [2000, 5000, 10000, 20000, 40000, 60000]


def bandwidth_panel(ax, runs, h, letter):
    ax.axhline(h, color=COLORS["theory"], ls="--", lw=1.0, zorder=1)
    ax.annotate(f"training $h={h:g}$", (0.02, h), xycoords=("axes fraction", "data"),
                xytext=(0, 4), textcoords="offset points", ha="left", va="bottom",
                fontsize=9, color="#222222")
    if h in PUBLISHED_HEFF:
        ax.plot([60000], [PUBLISHED_HEFF[h]], marker="x", ms=10, mew=2.0,
                color=COLORS["theory"], zorder=6, linestyle="none",
                label="published run, 60k")
    for r in sorted(runs, key=lambda r: r["seed"]):
        c = SEED_COLORS.get(r["seed"], OI["purple"])
        ck = r["checkpoints"]
        it = np.array([p["iter"] for p in ck])
        he = np.array([p["h_eff"] for p in ck])
        hm = np.array([p["h_means"] for p in ck])
        he_ci = np.array([p["h_eff_ci"] for p in ck]).T
        hm_ci = np.array([p["h_means_ci"] for p in ck]).T
        ax.errorbar(it, he, yerr=[he - he_ci[0], he_ci[1] - he], color=c, lw=2.0,
                    marker="o", ms=5.0, mec="white", mew=0.8, elinewidth=1.0,
                    zorder=3, label=f"seed {r['seed']}")
        ax.errorbar(it * 1.07, hm, yerr=[hm - hm_ci[0], hm_ci[1] - hm], color=c,
                    lw=0, marker="o", ms=5.0, mfc="white", mec=c, mew=1.3,
                    elinewidth=1.0, zorder=4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(3.6, 40)
    ax.set_yticks([4, 5, 6, 8, 10, 15, 20, 30])
    ax.set_yticklabels(["4", "5", "6", "8", "10", "15", "20", "30"])
    ax.minorticks_off()
    ax.set_xticks(TICKS)
    ax.set_xticklabels(["2k", "5k", "10k", "20k", "40k", "60k"])
    ax.set_xlabel("training iteration")
    ax.set_title(f"({letter}) CIFAR-10, $h={h:g}$", loc="left")
    style(ax)


def main() -> None:
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in SRC]
    if not runs:
        raise SystemExit("no h_eff results under results/exp3/_heff")
    hs = sorted({r["h"] for r in runs})
    use_paper_style()
    widths = [1.0] * len(hs) + [1.0]
    fig, axes = plt.subplots(1, len(hs) + 1, figsize=(4.1 * (len(hs) + 1), 4.1),
                             gridspec_kw={"width_ratios": widths})
    letters = "abcdefg"
    for k, h in enumerate(hs):
        bandwidth_panel(axes[k], [r for r in runs if r["h"] == h], h, letters[k])
    axes[0].set_ylabel("bandwidth  (filled: variances, open: means)")
    axes[0].legend(loc="upper right", fontsize=8.5, handletextpad=0.4)

    ax = axes[-1]
    for r in sorted(runs, key=lambda r: (r["h"], r["seed"])):
        c = SEED_COLORS.get(r["seed"], OI["purple"])
        ck = [p for p in r["checkpoints"] if p["iter"] >= MIN_ITER_B]
        x = np.array([p["h_eff"] for p in ck]) / r["h"]
        y = np.array([p.get("beta", np.nan) for p in ck])
        ax.plot(x, y, color=c, lw=1.2, alpha=0.55, zorder=2)
        ax.scatter(x, y, color=c, s=34, marker=H_MARKERS.get(r["h"], "o"),
                   edgecolors="white", linewidths=0.8, zorder=3,
                   label=f"$h={r['h']:g}$, seed {r['seed']}")
    ax.axhline(1.0, color=COLORS["theory"], ls="--", lw=1.0)
    ax.annotate(r"population optimum: $\beta=1$", (1.0, 1.0), xytext=(-4, -13),
                textcoords="offset points", ha="right", fontsize=8.5, color="#222222")
    ax.set_xlim(1.95, 0.95)
    ax.set_ylim(-0.2, 1.1)
    ax.set_xlabel(r"$h_{\mathrm{eff}}/h$  (training proceeds to the right)")
    ax.set_ylabel(r"tracking slope $\beta$")
    ax.set_title(rf"({letters[len(hs)]}) tracking slope against $h_{{\mathrm{{eff}}}}/h$",
                 loc="left")
    ax.legend(loc="upper left", fontsize=8)
    style(ax)

    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_heff_cifar.png")


if __name__ == "__main__":
    main()
