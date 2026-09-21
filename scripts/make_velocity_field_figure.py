"""The population velocity field itself, on the real d=2 instance.

Theorem 1 says the optimal field is v*(x,t,y) = sum_i w_i (x^i - x)/(1-t), a weighted
average of directions towards the atoms. This figure draws that field on a grid at two
times, for hard conditioning (h=0) and for label smoothing at the bandwidth h* that
matches the posterior variance. Arrows are unit length and coloured by the atom that
carries the largest weight there, so the picture shows where the flow is heading and
how sharply it commits. Atom marker area is the label weight p_i^{(h)}(y).

    uv run python -m scripts.make_velocity_field_figure

Writes paper/figures/fig_velocity_field.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.figstyle import COLORS, OI, panel_tag, save, use_paper_style  # noqa: E402
from src.metrics.kernel_theory import kernel_field, kernel_moments, kernel_weights  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402

use_paper_style()


def h_star(X, Y, y, target):
    lo, hi = 1e-3, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        _, cov, _ = kernel_moments(y, X, Y, mid)
        lo, hi = (mid, hi) if float(torch.trace(cov)) < target else (lo, mid)
    return 0.5 * (lo + hi)


def index_weights(x, t, X, Y, y, h):
    """Posterior weights of the index at points x (rows) and time t."""
    d2 = ((x[:, None, :] - t * X[None, :, :]) ** 2).sum(-1)
    lg = -d2 / (2.0 * (1.0 - t) ** 2)
    if h > 0:
        lg = lg - ((Y - y) ** 2).sum(-1)[None, :] / (2.0 * h * h)
    else:
        i0 = int(torch.argmin(((Y - y) ** 2).sum(-1)))
        mask = torch.full((X.shape[0],), -1e30, dtype=torch.float64)
        mask[i0] = 0.0
        lg = lg + mask[None, :]
    lg = lg - lg.max(dim=1, keepdim=True).values
    w = torch.exp(lg)
    return w / w.sum(dim=1, keepdim=True)


def main() -> None:
    torch.manual_seed(0)
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    Xt, Yt = prob.sample_dataset(200, seed=1)
    X, Y = Xt.to(torch.float64), Yt.to(torch.float64)
    Xn = X.numpy()
    i = int(np.argmin(np.abs(Y[:, 0].numpy() - np.median(Y[:, 0].numpy()))))
    y = Y[i]
    hs = h_star(X, Y, y, float(np.trace(prob.Sigma_post.numpy())))
    print(f"h* = {hs:.4f}")

    lo, hi = Xn.min(0) - 0.4, Xn.max(0) + 0.4
    gx, gy = np.meshgrid(np.linspace(lo[0], hi[0], 26), np.linspace(lo[1], hi[1], 26))
    pts = torch.tensor(np.stack([gx.ravel(), gy.ravel()], 1), dtype=torch.float64)

    cfgs = [(0.0, 0.5), (0.0, 0.9), (hs, 0.5), (hs, 0.9)]
    titles = [r"$h=0$, $t=0.5$", r"$h=0$, $t=0.9$", r"$h=h^\star$, $t=0.5$", r"$h=h^\star$, $t=0.9$"]
    palette = plt.get_cmap("tab20")
    fig, axes = plt.subplots(1, 4, figsize=(12.4, 3.4), sharex=True, sharey=True)
    for ax, (h, t), title, tag in zip(axes, cfgs, titles, "abcd"):
        w = index_weights(pts, t, X, Y, y, h)
        v = (w @ X - pts) / (1.0 - t)
        arg = w.argmax(dim=1).numpy()
        vn = v.numpy()
        vn = vn / (np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12)
        conf = w.max(dim=1).values.numpy()
        ax.quiver(pts[:, 0], pts[:, 1], vn[:, 0], vn[:, 1], color=[palette(a % 20) for a in arg],
                  alpha=0.35 + 0.65 * conf, angles="xy", scale=30, width=0.004)
        pw = kernel_weights(y, Y, h).numpy() if h > 0 else np.eye(len(Xn))[i]
        ax.scatter(Xn[:, 0], Xn[:, 1], s=np.minimum(6 + 900 * pw, 120), c="k", zorder=3, lw=0)
        ax.set_title(title, fontsize=9)
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        panel_tag(ax, tag)
    fig.tight_layout()
    save(fig, "fig_velocity_field.png")


if __name__ == "__main__":
    main()
