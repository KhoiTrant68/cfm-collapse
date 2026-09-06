"""The mechanism, from integrated trajectories rather than drawn arrows.

Three exact population flows on the same real problem instance (d=2, k=1, N=200),
each integrated from the same 160 draws of the source, with the true posterior drawn
underneath:

    h = 0        the label identifies one atom and every trajectory lands on it;
                 the endpoint law is a point mass and the conditional variance is
                 zero for any parameterisation.
    h = h*       the bandwidth is chosen, by bisection, so that tr Cov_h equals
                 tr Sigma_post *exactly*. The generated law now has precisely the
                 right conditional variance -- and is still a finite sum of point
                 masses. This panel is the paper's title.
    endpoint     smoothing the endpoint instead moves the support off the atoms and
                 gives an absolutely continuous law, the only one of the three that
                 could be a posterior at all.

The lower row makes the middle panel's point unmissable: the same three laws
projected onto the posterior's principal axis, against the true posterior density.
Matching the second moment and matching the distribution are different things, and
at h* the first holds while the second fails completely.

Nothing here is sketched. The fields are the closed forms of the paper, integrated
with RK4 on a grid graded towards t=1.

    uv run python -m scripts.make_mechanism_figure

Writes: paper/figures/fig_mechanism.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from src.metrics.kernel_theory import kernel_field, kernel_weights, kernel_moments
from src.problems.linear_gaussian import LinearGaussianProblem

OUT = Path("paper/figures/fig_mechanism.png")
OI = {"black": "#000000", "sky": "#56B4E9", "blue": "#0072B2",
      "vermillion": "#D55E00", "orange": "#E69F00", "green": "#009E73"}
N_PATHS, N_STEPS, T_END = 160, 400, 1.0 - 1e-3


def flow(X, Y, y, h, x0, source_std=1.0):
    """Integrate the exact kernel field from every row of x0 (RK4, graded grid)."""
    ts = 1.0 - np.geomspace(1.0, 1.0 - T_END, N_STEPS + 1)
    x = torch.tensor(x0, dtype=torch.float64)
    traj = [x.clone()]
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        def f(tt, xx):
            t_vec = torch.full((xx.shape[0],), float(tt), dtype=torch.float64)
            return kernel_field(xx, t_vec, y, X, Y, h, source_std)
        k1 = f(a, x); k2 = f(a + dt / 2, x + dt / 2 * k1)
        k3 = f(a + dt / 2, x + dt / 2 * k2); k4 = f(b, x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        traj.append(x.clone())
    return np.stack([p.numpy() for p in traj]), x.numpy()


def bandwidth_matching_posterior(X, Y, y, target, lo=1e-3, hi=5.0):
    """Bisect for h with tr Cov_h(y) = tr Sigma_post."""
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        _, cov, _ = kernel_moments(y, X, Y, mid)
        if float(torch.trace(cov)) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def posterior_ellipse(ax, mu, Sigma, **kw):
    vals, vecs = np.linalg.eigh(Sigma)
    ang = np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1]))
    from matplotlib.patches import Ellipse
    for k in (1.0, 2.0):
        ax.add_patch(Ellipse(mu, 2 * k * np.sqrt(vals[-1]), 2 * k * np.sqrt(vals[0]),
                             angle=ang, fill=(k == 2.0), facecolor=OI["sky"],
                             alpha=0.22 if k == 2.0 else 1.0, edgecolor=OI["blue"],
                             lw=1.8, zorder=0, **kw))


def main() -> None:
    torch.manual_seed(0)
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    Xt, Yt = prob.sample_dataset(200, seed=1)
    X, Y = Xt.to(torch.float64), Yt.to(torch.float64)
    Xn = X.numpy()

    i = int(np.argmin(np.abs(Y[:, 0].numpy() - np.median(Y[:, 0].numpy()))))
    y, xi = Y[i], Xn[i]
    Sigma = prob.Sigma_post.numpy().astype(float)
    mu = prob.posterior_mean(Y[i:i + 1].to(torch.float32)).numpy()[0].astype(float)
    tr_post = float(np.trace(Sigma))

    h_star = bandwidth_matching_posterior(X, Y, y, tr_post)
    _, cov_star, _ = kernel_moments(y, X, Y, h_star)
    print(f"  h* = {h_star:.4f}  ->  tr Cov_h = {float(torch.trace(cov_star)):.4f} "
          f"vs tr Sigma_post = {tr_post:.4f}")

    rng = np.random.default_rng(0)
    x0 = rng.normal(size=(N_PATHS, 2))
    rho = 0.30

    runs = []
    for h in (0.0, h_star):
        paths, ends = flow(X, Y, y, h, x0)
        runs.append((paths, ends))
    # Endpoint smoothing: p_1 = sum_i p_i N(x^i, rho^2 I), sampled directly.
    p = kernel_weights(y, Y, h_star).numpy()
    idx = rng.choice(len(p), size=N_PATHS, p=p)
    ends_ep = Xn[idx] + rho * rng.normal(size=(N_PATHS, 2))

    titles = [
        (r"hard conditioning  ($h=0$)",
         "every trajectory lands on one atom\n"
         r"$p_1=\delta_{x^i}$  —  zero conditional variance"),
        (rf"label smoothing at $h^\star={h_star:.2f}$",
         "bandwidth tuned so that $\\mathrm{tr}\\,\\mathrm{Cov}_h"
         "=\\mathrm{tr}\\,\\Sigma_{\\mathrm{post}}$ exactly\n"
         "right variance, wrong support: still atoms"),
        (rf"endpoint smoothing  ($\rho={rho}$)",
         "support moves off the atoms\n"
         "absolutely continuous — a posterior is reachable"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(12.4, 7.1),
                             gridspec_kw={"height_ratios": [2.5, 1.0]})
    lim = None
    for c in range(3):
        ax = axes[0, c]
        posterior_ellipse(ax, mu, Sigma)
        ax.scatter(Xn[:, 0], Xn[:, 1], s=9, color=OI["black"], alpha=0.45, zorder=2,
                   label="training atoms $x^i$")
        if c < 2:
            paths, ends = runs[c]
            ax.plot(paths[:, :, 0], paths[:, :, 1], color=OI["black"], alpha=0.10,
                    lw=0.6, zorder=1)
        else:
            ends = ends_ep
        if c == 1:
            w = kernel_weights(y, Y, h_star).numpy()
            keep = w > 1e-3
            ax.scatter(Xn[keep, 0], Xn[keep, 1], s=8 + 900 * w[keep],
                       color=OI["vermillion"], alpha=0.7, edgecolors="white",
                       linewidths=0.8, zorder=4,
                       label=r"generated law, area $\propto p^{(h)}_i$")
        else:
            ax.scatter(ends[:, 0], ends[:, 1], s=26 if c == 2 else 150,
                       color=OI["vermillion"], alpha=0.55 if c == 2 else 1.0,
                       edgecolors="white" if c == 0 else "none", linewidths=0.9,
                       zorder=4, label="generated law")
        ax.scatter(*xi, s=14, color=OI["black"], zorder=6)
        ax.set_title(titles[c][0], fontsize=11.5, pad=8)
        ax.text(0.5, -0.055, titles[c][1], transform=ax.transAxes, ha="center",
                va="top", fontsize=8.8)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
        ax.legend(fontsize=7.4, loc="upper left", framealpha=0.92)
        if lim is None:
            lim = (ax.get_xlim(), ax.get_ylim())
        ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1])
        for s_ in ax.spines.values():
            s_.set_alpha(0.35)

    # --- lower row: the same laws on the posterior's principal axis -----------
    vals, vecs = np.linalg.eigh(Sigma)
    u = vecs[:, -1]
    grid = np.linspace(-3.2, 3.2, 400)
    dens = np.exp(-0.5 * grid ** 2 / vals[-1]) / np.sqrt(2 * np.pi * vals[-1])
    for c in range(3):
        ax = axes[1, c]
        ax.plot(grid, dens, color=OI["sky"], lw=1.8, zorder=1,
                label="true posterior")
        if c == 0:
            ax.axvline((xi - mu) @ u, color=OI["vermillion"], lw=2.2, zorder=3,
                       label="generated")
        elif c == 1:
            w = kernel_weights(y, Y, h_star).numpy()
            proj = (Xn - mu) @ u
            keep = w > 1e-3
            ax.vlines(proj[keep], 0, w[keep] / w[keep].max() * dens.max(),
                      color=OI["vermillion"], lw=1.6, zorder=3, label="generated")
        else:
            ax.hist((ends_ep - mu) @ u, bins=26, density=True, color=OI["vermillion"],
                    alpha=0.6, zorder=2, label="generated")
        ax.set_xlim(-3.2, 3.2); ax.set_yticks([])
        ax.set_xlabel("projection on the posterior's principal axis", fontsize=8.5)
        ax.legend(fontsize=7.4, loc="upper right", framealpha=0.92)
        for s_ in ax.spines.values():
            s_.set_alpha(0.35)

    fig.tight_layout(h_pad=2.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
