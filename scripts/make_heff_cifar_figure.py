"""Figure: the effective bandwidth over training at image scale (CIFAR-10, DDPM U-Net).

(a) h_eff fitted to the per-condition variances (filled) and the bandwidth implied by
    the per-condition means (open), with 95% bootstrap intervals over the 48
    conditions, at every archived checkpoint of each run. The dashed rule is the
    training bandwidth h; the cross is the published run's h_eff at 60000 iterations.
(b) The across-condition slope beta of the paper against h_eff / h at the same
    checkpoints: the slope rises as h_eff approaches h, so the partial tracking the
    paper reports is a model whose effective bandwidth has not yet reached h.

Checkpoints before 5000 iterations are shown in (a) but left out of (b): at 2000 the
model has not learned the conditional structure and the two bandwidths disagree.

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
SEED_COLORS = [OI["blue"], OI["vermillion"], OI["green"]]
MIN_ITER_B = 5000


def main() -> None:
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in SRC]
    if not runs:
        raise SystemExit("no h_eff results under results/exp3/_heff")
    use_paper_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2),
                                   gridspec_kw={"width_ratios": [1.3, 1]})

    hs = sorted({r["h"] for r in runs})
    for h in hs:
        ax1.axhline(h, color=COLORS["theory"], ls="--", lw=1.0, zorder=1)
        ax1.annotate(f"$h={h:g}$", (1.01, h), xycoords=("axes fraction", "data"),
                     va="center", fontsize=9, color="#222222", annotation_clip=False)
        if h in PUBLISHED_HEFF:
            ax1.plot([60000], [PUBLISHED_HEFF[h]], marker="x", ms=10, mew=2.0,
                     color=COLORS["theory"], zorder=6, linestyle="none",
                     label="published run, 60k")

    for k, r in enumerate(sorted(runs, key=lambda r: (r["h"], r["seed"]))):
        c = SEED_COLORS[k % len(SEED_COLORS)]
        ck = r["checkpoints"]
        it = np.array([p["iter"] for p in ck])
        he = np.array([p["h_eff"] for p in ck])
        hm = np.array([p["h_means"] for p in ck])
        he_ci = np.array([p["h_eff_ci"] for p in ck]).T
        hm_ci = np.array([p["h_means_ci"] for p in ck]).T
        lab = f"seed {r['seed']}"
        ax1.errorbar(it, he, yerr=[he - he_ci[0], he_ci[1] - he], color=c, lw=2.0,
                     marker="o", ms=5.5, mec="white", mew=0.8, capsize=0,
                     elinewidth=1.0, zorder=3, label=f"{lab}: from variances")
        ax1.errorbar(it * 1.07, hm, yerr=[hm - hm_ci[0], hm_ci[1] - hm], color=c,
                     lw=0, marker="o", ms=5.5, mfc="white", mec=c, mew=1.3,
                     elinewidth=1.0, zorder=4, label=f"{lab}: from means")

        sel = it >= MIN_ITER_B
        beta = np.array([p.get("beta", np.nan) for p in ck])
        x, y = he[sel] / r["h"], beta[sel]
        ax2.plot(x, y, color=c, lw=1.4, alpha=0.6, zorder=2)
        ax2.scatter(x, y, color=c, s=36, edgecolors="white", linewidths=0.8, zorder=3,
                    label=f"$h={r['h']:g}$, {lab}")
        ax2.annotate(f"{it[sel][-1] // 1000}k", (x[-1], y[-1]), xytext=(5, 5),
                     textcoords="offset points", fontsize=8.5, color="#444444")
    ax2.annotate(f"{MIN_ITER_B // 1000}k", (1.91, 0.0), xytext=(0, 10),
                 textcoords="offset points", ha="center", fontsize=8.5, color="#444444")

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_yticks([4, 5, 6, 8, 10, 15])
    ax1.set_yticklabels(["4", "5", "6", "8", "10", "15"])
    ax1.minorticks_off()
    ax1.set_xticks([2000, 5000, 10000, 20000, 40000, 60000])
    ax1.set_xticklabels(["2k", "5k", "10k", "20k", "40k", "60k"])
    ax1.set_xlabel("training iteration")
    ax1.set_ylabel("bandwidth")
    ax1.set_title(r"(a) CIFAR-10: $h_{\mathrm{eff}}$ falls towards $h$", loc="left")
    ax1.legend(loc="upper right", fontsize=8, handletextpad=0.4)
    style(ax1)

    ax2.axhline(1.0, color=COLORS["theory"], ls="--", lw=1.0)
    ax2.annotate(r"population optimum: $\beta=1$", (1.0, 1.0), xytext=(-4, -13),
                 textcoords="offset points", ha="right", fontsize=8.5, color="#222222")
    ax2.set_xlim(2.05, 0.95)
    ax2.set_ylim(-0.15, 1.1)
    ax2.set_xlabel(r"$h_{\mathrm{eff}}/h$  (training proceeds to the right)")
    ax2.set_ylabel(r"tracking slope $\beta$")
    ax2.set_title(r"(b) $\beta$ rises as $h_{\mathrm{eff}}\to h$", loc="left")
    ax2.legend(loc="upper left", fontsize=8.5)
    style(ax2)

    fig.tight_layout(w_pad=2.5)
    save(fig, "fig_heff_cifar.png")


if __name__ == "__main__":
    main()
