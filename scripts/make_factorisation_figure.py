"""The index posterior, factor by factor -- the paper's structural claim, drawn.

Everything in this paper follows from one identity: the posterior over which
training atom the flow is heading for factorises as

    w_i(x, t, y)  proportional to  pi_0( (x - t x^i) / (1-t) )  *  K_h(y - y^i)
                                   \______ spatial ______/       \__ label __/

The spatial factor is a Nadaraya-Watson smoother whose bandwidth is the flow time
1-t: it is imposed by the clock, sharpens to a nearest-neighbour rule as t -> 1,
and is identical in the conditional and unconditional fields. The label factor's
bandwidth is a modelling choice, and it is the one this paper is about.

Read left to right, the panels are the mechanism. The label factor alone selects a
band of eligible atoms and does not move with t. The spatial factor alone is broad
at mid-time and collapses onto whatever atom the trajectory is nearest by t = 0.95.
Their product is what the flow actually follows, and it concentrates on a single
atom -- one that the label factor had to admit in the first place.

Computed on the real EXP-1 instance (d=2, k=1, N=200), not sketched: the weights
are evaluated from the same expressions the training code uses.

    uv run python scripts/make_factorisation_figure.py

Writes: paper/figures/fig_factorisation.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from src.problems.linear_gaussian import LinearGaussianProblem

OUT = Path("paper/figures/fig_factorisation.png")
OI = {"black": "#000000", "sky": "#56B4E9", "blue": "#0072B2",
      "vermillion": "#D55E00", "orange": "#E69F00"}


def weights(X, Y, x, t, y, h, source_std=1.0):
    """The two factors of the index posterior, each normalised for display."""
    spatial_log = -0.5 * (((x[None, :] - t * X) / (1.0 - t)) ** 2).sum(1) / source_std ** 2
    label_log = -0.5 * ((y - Y) ** 2).sum(1) / h ** 2
    def norm(v):
        v = v - v.max()
        e = np.exp(v)
        return e / e.sum()
    return norm(spatial_log), norm(label_log), norm(spatial_log + label_log)


def main() -> None:
    torch.manual_seed(0)
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    X, Y = prob.sample_dataset(200, seed=1)
    X, Y = X.numpy().astype(float), Y.numpy().astype(float)

    i = int(np.argmin(np.abs(Y[:, 0] - np.median(Y[:, 0]))))   # a central query
    y, xi = Y[i], X[i]
    h = 0.1
    x0 = np.array([1.6, -1.4])                                  # a source draw

    # The third panel is the point: at mid-time neither factor alone selects an
    # atom, and it is their intersection that does. Showing the spatial factor at
    # t=0.95 instead would make the label factor look irrelevant, because by then
    # the trajectory sits on its atom and the spatial factor alone suffices.
    panels = [
        ("label factor $K_h(y-y^j)$\n(does not move with $t$)", "label", 0.5),
        ("spatial factor at $t=0.5$", "spatial", 0.5),
        ("their product at $t=0.5$", "product", 0.5),
        ("their product at $t=0.95$", "product", 0.95),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.7))
    for ax, (title, which, t) in zip(axes, panels):
        xt = (1.0 - t) * x0 + t * xi                            # on the exact path
        sp, lb, pr = weights(X, Y, xt, t, y, h)
        w = {"spatial": sp, "label": lb, "product": pr}[which]
        order = np.argsort(w)
        sc = ax.scatter(X[order, 0], X[order, 1], c=w[order], s=14 + 900 * w[order],
                        cmap="viridis", norm=matplotlib.colors.PowerNorm(0.45),
                        edgecolors="none", zorder=3)
        ax.scatter(*xi, marker="*", s=190, facecolor="none",
                   edgecolor=OI["vermillion"], linewidths=1.6, zorder=5,
                   label="queried atom $x^i$")
        if which != "label":
            ax.scatter(*xt, marker="x", s=60, color=OI["vermillion"], linewidths=1.8,
                       zorder=5, label=f"$x_t$ at $t={t}$")
        ax.set_title(title, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
        ax.legend(fontsize=7, loc="lower left", framealpha=0.9)
        neff = 1.0 / (w ** 2).sum()
        ax.text(0.97, 0.03, f"$n_{{\\mathrm{{eff}}}}={neff:.1f}$", ha="right",
                transform=ax.transAxes, fontsize=8.5, color=OI["black"])
        for sp_ in ax.spines.values():
            sp_.set_alpha(0.35)
    fig.colorbar(sc, ax=axes, fraction=0.016, pad=0.012,
                 label="weight on atom $x^j$")
    fig.suptitle(
        r"$w_j^{(h)}(x,t,y)\;\propto\;"
        r"\pi_0\left(\frac{x-tx^j}{1-t}\right)\;\cdot\;K_h(y-y^j)$",
        fontsize=14, y=1.15)
    fig.text(0.5, 1.03,
             "left factor: bandwidth $1-t$, imposed by the clock and identical in the "
             "unconditional field        "
             "right factor: bandwidth $h$, a modelling choice, and the subject here",
             ha="center", fontsize=9.5)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
