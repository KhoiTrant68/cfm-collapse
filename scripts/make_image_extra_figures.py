"""The rest of the CIFAR-10 sample grids, on the shared style.

``make_image_bandwidth_figure.py`` shows one seed at the last checkpoint. The DDPM runs
also saved grids through training, for two further seeds, and for two class-conditional
runs; none of it was in the paper. Everything here is cut out of those saved grids (the
35.75M-parameter U-Net checkpoints are not kept), plus the metrics the same runs wrote.

    uv run python -m scripts.make_image_extra_figures

Writes into paper/figures:
    fig_image_training.png        DDPM, h = 0, seed 0: iteration 500 ... 60000
    fig_image_bandwidth_seed1.png the h sweep of fig_image_bandwidth, seed 1
    fig_image_bandwidth_seed2.png ... and seed 2 (each seed draws its own training set)
    fig_image_class.png           class labels (N = 2000, ~200 per class): trace Cov against
                                  the within-class scatter, and the sample grids, h = 0 and 0.4
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.figstyle import COLORS, OI, panel_tag, predicted_rule, save, use_paper_style
from scripts.make_image_bandwidth_figure import N_COLS, cells

HEADERS = ["observed"] + ["completion"] * 6 + ["true", "nearest\ntrain image"]

BASE = Path("results/exp3")
ITERS = (500, 2000, 8000, 20000, 40000, 60000)


def draw_blocks(fig, gs, first_row, blocks, conds, *, label_x=-0.42, tags=True):
    """Stack blocks of grid rows: each block is (label, sheet); ``conds`` picks its rows."""
    r = first_row
    for b, (label, sheet) in enumerate(blocks):
        for k, cond in enumerate(conds):
            for c in range(N_COLS):
                ax = fig.add_subplot(gs[r, c])
                ax.imshow(sheet[cond][c], interpolation="nearest")
                ax.set_xticks([])
                ax.set_yticks([])
                for s in ax.spines.values():
                    s.set_visible(False)
                if b == 0 and k == 0:
                    ax.set_title(HEADERS[c], fontsize=7.5, pad=3)
                if c == 0 and k == 0:
                    ax.annotate(label, xy=(label_x, -0.05 - 0.5 * (len(conds) - 2)),
                                xycoords="axes fraction", ha="center", va="center",
                                rotation=90, fontsize=10, fontweight="bold")
                    if tags:
                        panel_tag(ax, "abcdefgh"[b], dx=-0.95, dy=0.92)
            r += 1
    return r


def sheets(runs):
    return [(label, cells(BASE / run / "figures" / f"grid_it{it}.png")) for label, run, it in runs]


def fig_training() -> None:
    conds = (0, 2)
    blocks = sheets([(f"${it:,}$".replace(",", "{,}"), "exp3_cifar_ddpm_h0", it) for it in ITERS])
    n = len(blocks) * len(conds)
    fig = plt.figure(figsize=(7.4, 0.80 * n + 0.8))
    gs = fig.add_gridspec(n, N_COLS, left=0.11, right=0.995, top=0.94, bottom=0.005,
                          wspace=0.05, hspace=0.06)
    draw_blocks(fig, gs, 0, blocks, conds, label_x=-0.55)
    save(fig, "fig_image_training.png")


def fig_seed(seed: int) -> None:
    conds = (0, 2)
    runs = [(f"$h={h:g}$", f"exp3_cifar_ddpm_h{h:g}_seed{seed}", 60000) for h in (0, 4, 5, 6)]
    blocks = sheets(runs)
    n = len(blocks) * len(conds)
    fig = plt.figure(figsize=(7.4, 0.86 * n + 0.9))
    gs = fig.add_gridspec(n, N_COLS, left=0.09, right=0.995, top=0.925, bottom=0.005,
                          wspace=0.05, hspace=0.06)
    draw_blocks(fig, gs, 0, blocks, conds)
    save(fig, f"fig_image_bandwidth_seed{seed}.png")


def fig_class() -> pd.DataFrame:
    runs = {0.0: "exp3_cifar_class_h0", 0.4: "exp3_cifar_class_h0p4"}
    met = {h: pd.read_csv(BASE / r / "raw" / "metrics.csv").sort_values("iter")
           for h, r in runs.items()}
    conds = (0, 1, 2, 3)
    blocks = sheets([(f"$h={h:g}$", r, 60000) for h, r in runs.items()])

    n_grid = len(blocks) * len(conds)
    fig = plt.figure(figsize=(7.4, 0.80 * n_grid + 4.2))
    gs = fig.add_gridspec(n_grid + 2, N_COLS, left=0.09, right=0.995, top=0.985, bottom=0.005,
                          wspace=0.05, hspace=0.06, height_ratios=[3.6, 1.5] + [1] * n_grid)
    ax = fig.add_subplot(gs[0, 1:8])
    colors = {0.0: OI["blue"], 0.4: OI["orange"]}
    for h, df in met.items():
        ax.plot(df["iter"], df["trace_cov_mean"], linestyle="none", marker="x", markersize=8,
                markeredgewidth=1.8, color=colors[h], label=f"$h={h:g}$: measured")
    pop = float(met[0.0]["trace_cov_kernel_mean"].iloc[0])
    predicted_rule(ax, pop, f"within-class scatter {pop:.0f}", where=0.02)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.05 * max(df["trace_cov_mean"].max() for df in met.values()))
    ax.set_xlabel("training iteration")
    ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$ of completions")
    ax.legend(loc="lower right")
    panel_tag(ax, "a", dx=-0.13)
    draw_blocks(fig, gs, 2, blocks, conds, tags=False)
    for b, letter in enumerate("bc"):
        panel_tag(fig.axes[1 + b * len(conds) * N_COLS], letter, dx=-0.95, dy=0.92)
    save(fig, "fig_image_class.png")
    return pd.concat({h: df.set_index("iter") for h, df in met.items()})


def main() -> None:
    use_paper_style()
    fig_training()
    fig_seed(1)
    fig_seed(2)
    met = fig_class()
    # numbers quoted in the caption of fig_image_class
    for h in (0.0, 0.4):
        df = met.loc[h]
        r = df["trace_cov_mean"] / df["trace_cov_kernel_mean"]
        print(f"h={h:g}: tr Cov / within-class scatter = {r.min():.2f}..{r.max():.2f}; "
              f"at 60000: {r.loc[60000]:.3f}; loss {df['train_loss'].iloc[0]:.3f} -> "
              f"{df['train_loss'].iloc[-1]:.3f}")
        assert abs(r.loc[60000] - 0.76) < 0.01 and df["train_loss"].iloc[-1] < 0.07


if __name__ == "__main__":
    main()
