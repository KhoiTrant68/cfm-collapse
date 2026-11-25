"""Draw the CIFAR-10 pair endpoints and observed midpoint fractions for the eight selected pairs.

Run python scripts/make_theory_cifar_composition_figure.py from the repository or
supplement root. The small image archive contains the native 32-by-32 RGB training
images for all eight measured pairs. Use scripts/make_cifar_composition_figure.py
with the full CIFAR instance to regenerate it.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import COLORS, FULL_W, lead_text, panel_title, style, use_paper_style

RESULTS = Path("results/cifar_composition_replay")
IMAGES = RESULTS / "selected_images.npz"
OUT = Path("paper_theory/figures/fig_cifar_composition.pdf")


def main() -> None:
    use_paper_style()
    curves = json.loads((RESULTS / "summary.json").read_text())["selected"]
    pairs = sorted(curves, key=lambda pair: curves[pair]["10.0"])
    fig = plt.figure(figsize=(FULL_W, 4.5))
    lead_text(fig, 0.015, 0.973, "a", "Training pairs and their pixelwise midpoints",
              fontsize=9, va="top")
    grid = fig.add_gridspec(3, len(pairs), left=0.155, right=0.985, top=0.905, bottom=0.515,
                            hspace=0.055, wspace=0.055)
    with np.load(IMAGES) as archive:
        for col, pair in enumerate(pairs):
            first, second = [archive[i].astype(float) / 255 for i in pair.split("/")]
            midpoint = (first + second) / 2
            for row, im in enumerate((first, midpoint, second)):
                ax = fig.add_subplot(grid[row, col])
                ax.imshow(im, interpolation="nearest")
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(row == 1)
                    spine.set_color(COLORS["generated"])
                    spine.set_linewidth(0.9)
                if col == 0:
                    label = (r"Image $x^i$", r"Midpoint $z$", r"Image $x^j$")[row]
                    ax.text(-0.18, 0.5, label, transform=ax.transAxes, ha="right", va="center")
                if row == 2:
                    ax.text(0.5, -0.16, f"{curves[pair]['10.0']:.1%}", transform=ax.transAxes,
                            ha="center", va="top", fontsize=8)
                    if col == 0:
                        ax.text(-0.18, -0.16, r"At $10w_c$", transform=ax.transAxes,
                                ha="right", va="top", fontsize=8)

    ax = fig.add_axes([0.112, 0.105, 0.855, 0.30])
    ratios = sorted(curves[pairs[0]], key=float)
    xs = np.arange(len(ratios))
    values = np.array([[curves[pair][r] for r in ratios] for pair in pairs])
    # Separate measured strengths on each side. No interpolation across the unsampled threshold.
    split = next(i for i, r in enumerate(ratios) if float(r) > 1)
    for segment in (slice(None, split), slice(split, None)):
        for j, row in enumerate(values):
            ax.plot(xs[segment], row[segment], color="#888888", lw=0.85, marker=".", ms=3.4,
                    label="Individual pair" if segment.start is None and j == 0 else None)
        ax.plot(xs[segment], values.mean(axis=0)[segment], color=COLORS["generated"], lw=1.8,
                marker="o", ms=4, zorder=3, label="Mean of eight pairs" if segment.start is None else None)
    ax.axvline(split - 0.5, color="#444444", ls="--", lw=0.8)
    ax.text(split - 0.43, 0.94, r"$w=w_c$", ha="left", va="top", fontsize=8)
    ax.set_xticks(xs, [f"{float(r):g}" for r in ratios])
    ax.set_xlim(-0.16, len(xs) - 0.84)
    ax.set_ylim(-0.045, 1.035)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "0.25", "0.5", "0.75", "1"])
    ax.grid(axis="x", visible=False)
    ax.set_xlabel(r"Sampled guidance strength, $w/w_c$")
    ax.set_ylabel("Midpoint fraction")
    ax.legend(loc="upper left", fontsize=8)
    panel_title(ax, "b", "Fraction of 512 shared sources reaching the midpoint", fontsize=9)
    style(ax)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)
    (OUT.parent / "fig_cifar_curve.json").write_text(json.dumps(curves, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
