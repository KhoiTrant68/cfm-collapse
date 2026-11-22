"""Figure fig:cifar-composition of paper_theory: exact guided label averaging on CIFAR-10 pairs.

    PYTHONPATH=.:scripts python scripts/make_theory_cifar_composition_figure.py

(a) Three of the eight pairs: training images x^i, x^j and their midpoint z, the non-training
    endpoint of the composite (Theorem thm:composition at d = 3072).
(b) Fraction of the 512 shared sources ending at z against w/w_c, for every pair (thin) and the mean
    over the eight pairs (thick), from results/cifar_composition_exact_20261105/summary.json.

The image tiles of (a) are not recomputed: the CIFAR-10 instance cifar2000_seed0.npz that
scripts/make_cifar_composition_figure.py reads is not committed. They are the nine images embedded in
the earlier version of this figure (drawn by that script from the data file for the pairs
(1491, 1514), (81, 819), (158, 230)), extracted losslessly with `pdfimages -png` into
results/cifar_composition_exact_20261105/figure_tiles/tile-000..008.png, row by row
(x^i, z, x^j).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from figstyle import COLORS, FULL_W, panel_title, style, use_paper_style

ROOT = Path("results/cifar_composition_exact_20261105")
TILES = ROOT / "figure_tiles"
OUT = Path("paper_theory/figures/fig_cifar_composition.pdf")
X0 = 0.3                       # w = 0 drawn here, left of an axis break
GREY = "#555555"


def main() -> None:
    use_paper_style()
    S = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))["pairs"]
    fig = plt.figure(figsize=(FULL_W, 2.3))
    gs = fig.add_gridspec(3, 5, width_ratios=(0.84, 0.84, 0.84, 0.5, 6.4), wspace=0.06, hspace=0.06,
                          left=0.01, right=0.985, bottom=0.17, top=0.88)
    for row in range(3):
        for col, title in enumerate((r"$x^i$", r"midpoint $z$", r"$x^j$")):
            ax = fig.add_subplot(gs[row, col])
            ax.imshow(np.asarray(Image.open(TILES / f"tile-{3 * row + col:03d}.png").convert("RGB")),
                      interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
            for s in ax.spines.values():
                s.set_visible(True)
                s.set_edgecolor(COLORS["generated"] if col == 1 else "#bbbbbb")
                s.set_linewidth(1.4 if col == 1 else 0.6)
            if row == 0:
                ax.set_title(title, fontsize=7.5, pad=3,
                             color=COLORS["generated"] if col == 1 else "#222222")
            if row == 0 and col == 0:
                ax.text(-0.08, 1.32, r"$\mathbf{(a)}$  Pairs and midpoints", transform=ax.transAxes,
                        ha="left", va="bottom", fontsize=8.5)

    ax = fig.add_subplot(gs[:, 4])
    ratios = sorted(float(k) for k in S[0]["mid"])
    xs = [X0 if r == 0 else r for r in ratios]
    ax.axvspan(0.25, 1.0, color="#f2f2f2", lw=0, zorder=0)
    for p in S:
        ax.plot(xs, [p["mid"][f"{r:.1f}"] for r in ratios], color="#a8a8a8", lw=0.7, zorder=1)
    mean = [float(np.mean([p["mid"][f"{r:.1f}"] for p in S])) for r in ratios]
    ax.plot(xs, mean, color=COLORS["generated"], lw=1.8, marker="o", ms=3.5, zorder=3)
    print("mean midpoint fraction:", dict(zip(ratios, np.round(mean, 4))))
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color="#a8a8a8", lw=0.7, label="single pair"),
                       Line2D([], [], color=COLORS["generated"], lw=1.8, marker="o", ms=3.5,
                              label=f"mean of {len(S)} pairs")],
              loc="upper left", fontsize=6.5, borderaxespad=0.4)
    ax.axvline(1.0, color=COLORS["theory"], ls="--", lw=0.9)
    ax.text(1.05, 0.97, r"$w=w_c$", transform=ax.get_xaxis_transform(), fontsize=7, va="top")
    ax.text(0.5, 0.1, r"zero for $w\leq0.9\,w_c$", transform=ax.get_xaxis_transform(),
            ha="center", va="center", fontsize=6.5, color=GREY)
    ax.set_xscale("log"); ax.set_xlim(0.25, 12)
    ax.set_xticks([X0, 1, 10]); ax.set_xticklabels(["0", "1", "10"])
    ax.xaxis.set_minor_locator(plt.matplotlib.ticker.FixedLocator([0.5, 0.9, 2, 3, 4, 5, 6, 7, 8, 9]))
    ax.xaxis.set_minor_formatter(plt.matplotlib.ticker.NullFormatter())
    xb = (np.log(0.39) - np.log(0.25)) / (np.log(12) - np.log(0.25))
    for dx in (-0.006, 0.006):
        ax.plot([xb + dx - 0.005, xb + dx + 0.005], [-0.025, 0.025], transform=ax.transAxes,
                color="#333333", clip_on=False, lw=0.6)
    ax.set_ylim(-0.01, 0.31)
    ax.set_xlabel(r"guidance relative to threshold, $w/w_c$")
    ax.set_ylabel(r"fraction of sources ending at $z$")
    panel_title(ax, "b", r"Exact composite, $d=3072$, $N=2000$, $B=1$")
    style(ax)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
