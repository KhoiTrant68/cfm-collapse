"""The mechanism as a schematic, for the introduction.

This is the idea before the evidence. It carries no data: the atoms, weights and
arrows are chosen to be legible, so a reader meets the three endpoint laws --
a point mass, a weighted mixture over the *same* atoms, and an absolutely
continuous law -- in one glance and before any notation. Its companion,
scripts/make_mechanism_figure.py, shows the same three scenes computed on a real
instance with integrated trajectories; that one is the evidence, and it is placed
after the theory it verifies.

Original framing follows.

Three panels over the same scene: a continuous true posterior (shaded), the
training atoms that fall inside it (black), and where the exact population flow
actually sends its samples (red).

    h = 0        the label identifies one atom, every initial condition lands on
                 it, and the endpoint law is a single point mass -- zero variance
                 no matter how the model is parameterised (the exact-collapse proposition).
    h > 0        the label is smoothed, so the endpoint law becomes a kernel-
                 weighted mixture over atoms (the endpoint theorem). The second moment can
                 be made to match the posterior's exactly; the law is still a
                 finite sum of point masses, and the Wasserstein distance to the
                 posterior has a floor that no h removes (the atomicity proposition).
    endpoint     smoothing the endpoint instead moves the support off the atoms,
                 giving an absolutely continuous law (the endpoint-smoothing
                 proposition) -- the only
                 one of the three that can be a posterior at all.

The middle panel is the paper's title: restored variance, un-restored posterior.

    uv run python -m scripts.make_mechanism_schematic

Writes: paper/figures/fig_mechanism_schematic.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

OUT = Path("paper/figures/fig_mechanism_schematic.png")

# Okabe-Ito, matching scripts/make_paper_figures.py.
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9",
      "green": "#009E73", "blue": "#0072B2", "vermillion": "#D55E00",
      "purple": "#CC79A7"}

ATOMS = np.array([[-1.15, 0.55], [-0.35, -0.75], [0.30, 0.85],
                  [0.95, -0.35], [1.35, 0.60], [-0.85, -0.20]])
TARGET = 3                      # the atom whose label was queried
WEIGHTS = np.array([0.10, 0.06, 0.17, 0.42, 0.19, 0.06])   # kernel weights at h > 0
RNG = np.random.default_rng(0)


def start_points(n: int = 9, r: float = 2.35) -> np.ndarray:
    a = np.linspace(0, 2 * np.pi, n, endpoint=False) + 0.22
    return np.c_[r * np.cos(a), r * np.sin(a) * 0.72]


def scene(ax, title: str, subtitle: str) -> None:
    ax.add_patch(Ellipse((0.05, 0.05), 3.5, 2.35, angle=-12, facecolor=OI["sky"],
                         alpha=0.16, edgecolor=OI["sky"], lw=1.2, zorder=0))
    ax.scatter(ATOMS[:, 0], ATOMS[:, 1], s=34, color=OI["black"], zorder=4,
               label="training atoms $x^i$")
    ax.set_xlim(-2.7, 2.7); ax.set_ylim(-2.0, 2.0)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=11, pad=7)
    ax.text(0.5, -0.10, subtitle, transform=ax.transAxes, ha="center",
            va="top", fontsize=8.6)
    for sp in ax.spines.values():
        sp.set_alpha(0.35)


def arrows(ax, targets: np.ndarray, jitter: float = 0.0) -> None:
    for k, s in enumerate(start_points()):
        t = targets[k % len(targets)]
        if jitter:
            t = t + RNG.normal(scale=jitter, size=2)
        ax.annotate("", xy=t, xytext=s,
                    arrowprops=dict(arrowstyle="->", color=OI["black"], alpha=0.30,
                                    lw=0.9, shrinkA=2, shrinkB=3,
                                    connectionstyle="arc3,rad=0.13"), zorder=2)
        ax.plot(*s, marker="o", ms=2.6, color=OI["black"], alpha=0.45, zorder=3)


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 4.0))

    # --- h = 0 -------------------------------------------------------------
    ax = axes[0]
    scene(ax, r"hard conditioning  ($h=0$)",
          "every initial condition lands on one atom\n"
          r"$p_1=\delta_{x^i}$   —   zero conditional variance")
    arrows(ax, ATOMS[TARGET][None, :])
    ax.scatter(*ATOMS[TARGET], s=250, color=OI["vermillion"], zorder=5,
               edgecolors="white", linewidths=1.1, label="generated law")
    # Redraw the atom on top: the law sits exactly on it, and that must be visible.
    ax.scatter(*ATOMS[TARGET], s=26, color=OI["black"], zorder=6)

    # --- h > 0 -------------------------------------------------------------
    ax = axes[1]
    scene(ax, r"label smoothing  ($h>0$)",
          "kernel-weighted mixture over the same atoms\n"
          r"variance can match $\Sigma_{\mathrm{post}}$ — support cannot")
    order = np.argsort(-WEIGHTS)[:4]
    arrows(ax, ATOMS[order])
    ax.scatter(ATOMS[:, 0], ATOMS[:, 1], s=60 + 620 * WEIGHTS,
               color=OI["vermillion"], zorder=5, edgecolors="white", linewidths=1.1,
               label=r"generated law, area $\propto p_i^{(h)}$")
    # Same again: the mass is spread over atoms, not moved off them.
    ax.scatter(ATOMS[:, 0], ATOMS[:, 1], s=26, color=OI["black"], zorder=6)

    # --- endpoint smoothing ------------------------------------------------
    ax = axes[2]
    scene(ax, "endpoint smoothing",
          "support moves off the atoms\n"
          "absolutely continuous — a posterior is now reachable")
    arrows(ax, ATOMS[order], jitter=0.16)
    for (cx, cy), w in zip(ATOMS, WEIGHTS):
        cloud = RNG.normal(scale=0.17, size=(int(340 * w) + 14, 2)) + (cx, cy)
        ax.scatter(cloud[:, 0], cloud[:, 1], s=7, color=OI["vermillion"],
                   alpha=0.42, edgecolors="none", zorder=5)
    ax.scatter([], [], s=40, color=OI["vermillion"], label="generated law")

    for ax in axes:
        ax.legend(loc="upper left", fontsize=7.4, framealpha=0.92,
                  borderpad=0.35, handletextpad=0.5)
    axes[0].text(-2.55, -1.85, "shaded: true posterior $p(\\cdot\\mid y)$",
                 fontsize=7.6, color=OI["blue"], alpha=0.9)

    fig.tight_layout(rect=(0, 0.035, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200)
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
