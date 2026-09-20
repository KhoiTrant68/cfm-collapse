"""Image-domain sample grids, swept over the label bandwidth h (CIFAR-10 DDPM, EXP-3).

Each ``grid_it*.png`` the DDPM runs wrote is a 4 x 9 sheet of 32x32 cells (observed top
half; six completions of the same masked image from different x_0; the true image; the
nearest training image) with its own title and column labels in default matplotlib
style. This recomposes the last checkpoint of the four bandwidths onto one sheet, so
that the collapse at h = 0 and what h > 0 does to it are read down a column instead of
across four files, with the labels and colours of the rest of the paper.

The cells are cut out of the saved grids rather than re-sampled: the checkpoints of the
35.75M-parameter U-Nets are not kept (they are regenerable, and gitignored), and the
grids are the images the reported statistics were computed alongside.

    uv run python -m scripts.make_image_bandwidth_figure

Writes paper/figures/fig_image_bandwidth.png.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, panel_tag, save, use_paper_style

RUNS = {0.0: "exp3_cifar_ddpm_h0", 4.0: "exp3_cifar_ddpm_h4",
        5.0: "exp3_cifar_ddpm_h5", 6.0: "exp3_cifar_ddpm_h6"}
ITER = 60000
CONDITIONS = (0, 2)          # rows of the saved grid to show: the frog and the car
N_ROWS, N_COLS = 4, 9        # layout of every saved grid
HEADERS = ["observed"] + ["completion"] * 6 + ["true image", "training image\nnearest the mean"]


def _runs(mask: np.ndarray, min_len: int) -> list[tuple[int, int]]:
    """Maximal runs of True at least ``min_len`` long, as (start, stop)."""
    out, start = [], None
    for i, v in enumerate(np.append(mask, False)):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    return out


def cells(path: Path) -> list[list[np.ndarray]]:
    """Cut a saved grid into its N_ROWS x N_COLS cells, frames included."""
    img = mpimg.imread(path)[..., :3]
    dark = (img < 0.98).any(axis=-1)                       # anything that is not paper
    rows = _runs(dark.sum(axis=1) > 50, 60)
    assert len(rows) == N_ROWS, f"{path}: found {len(rows)} cell rows, expected {N_ROWS}"
    grid = []
    for (a, b) in rows:
        cols = _runs(dark[a:b].sum(axis=0) > 0, 60)
        assert len(cols) == N_COLS, f"{path}: found {len(cols)} cell columns in a row"
        grid.append([img[a:b, c:d] for (c, d) in cols])
    return grid


def main() -> None:
    use_paper_style()
    base = Path("results/exp3")
    sheets = {h: cells(base / run / "figures" / f"grid_it{ITER}.png") for h, run in RUNS.items()}

    n_blocks = len(RUNS)
    fig = plt.figure(figsize=(7.4, 0.86 * n_blocks * len(CONDITIONS) + 0.9))
    gs = fig.add_gridspec(n_blocks * len(CONDITIONS), N_COLS, left=0.09, right=0.995,
                          top=0.925, bottom=0.005, wspace=0.05, hspace=0.06)
    for b, (h, sheet) in enumerate(sheets.items()):
        for r, cond in enumerate(CONDITIONS):
            for c in range(N_COLS):
                ax = fig.add_subplot(gs[b * len(CONDITIONS) + r, c])
                ax.imshow(sheet[cond][c], interpolation="nearest")
                ax.set_xticks([])
                ax.set_yticks([])
                for s in ax.spines.values():
                    s.set_visible(False)
                if b == 0 and r == 0:
                    ax.set_title(HEADERS[c], fontsize=8, pad=3)
                if c == 0 and r == 0:
                    ax.annotate(f"$h={h:g}$", xy=(-0.42, -0.05), xycoords="axes fraction",
                                ha="center", va="center", rotation=90, fontsize=10.5,
                                fontweight="bold")
                if c == 0 and r == 0:
                    panel_tag(ax, "abcd"[b], dx=-0.95, dy=0.92)
    save(fig, "fig_image_bandwidth.png")


if __name__ == "__main__":
    main()
