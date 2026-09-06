"""Animate the collapse -- the one thing a static figure cannot show.

Figure 1 of the paper shows where the three exact flows end. What it cannot show is
*when* they get there, and the timing is the whole of the phenomenon: the index
posterior is broad for most of the interval and concentrates only in the last few
percent of the clock, which is why collapse looks like it happens suddenly and why
a sampler that stops early sees something quite different from one that does not.

Three panels, one clock, the same 200 source draws under each exact population field:

    h = 0        every trajectory converging to a single atom
    h = h*       the bandwidth at which tr Cov_h equals tr Sigma_post exactly, so
                 the cloud keeps the right spread while never leaving the atoms
    endpoint     the same weights with the support moved off the atoms

The lower strip tracks n_eff along the clock, which is what is actually collapsing:
for h > 0 it falls from N towards its endpoint value as the spatial factor sharpens.

Written for the supplementary material and the repository, not the PDF.

    uv run python -m scripts.make_collapse_animation [--fps 20] [--frames 90]

Writes: paper/figures/anim_collapse.gif
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

from src.metrics.kernel_theory import kernel_field, kernel_weights, kernel_moments
from src.problems.linear_gaussian import LinearGaussianProblem

OUT = Path("paper/figures/anim_collapse.gif")
OI = {"black": "#000000", "sky": "#56B4E9", "blue": "#0072B2",
      "vermillion": "#D55E00", "orange": "#E69F00"}


def rollout(X, Y, y, h, x0, ts, source_std=1.0):
    """Positions at every time in `ts` (RK4 between consecutive times)."""
    x = torch.tensor(x0, dtype=torch.float64)
    out = [x.numpy().copy()]
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        def f(tt, xx):
            tv = torch.full((xx.shape[0],), float(tt), dtype=torch.float64)
            return kernel_field(xx, tv, y, X, Y, h, source_std)
        k1 = f(a, x); k2 = f(a + dt / 2, x + dt / 2 * k1)
        k3 = f(a + dt / 2, x + dt / 2 * k2); k4 = f(b, x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(x.numpy().copy())
    return np.stack(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=18)
    ap.add_argument("--frames", type=int, default=90)
    ap.add_argument("--paths", type=int, default=200)
    args = ap.parse_args()

    torch.manual_seed(0)
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    Xt, Yt = prob.sample_dataset(200, seed=1)
    X, Y = Xt.to(torch.float64), Yt.to(torch.float64)
    Xn = X.numpy()
    i = int(np.argmin(np.abs(Y[:, 0].numpy() - np.median(Y[:, 0].numpy()))))
    y = Y[i]
    tr_post = float(np.trace(prob.Sigma_post.numpy()))

    lo, hi = 1e-3, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        _, cov, _ = kernel_moments(y, X, Y, mid)
        lo, hi = (mid, hi) if float(torch.trace(cov)) < tr_post else (lo, mid)
    h_star = 0.5 * (lo + hi)

    # Graded clock: most frames near t=1, where everything happens.
    ts = 1.0 - np.geomspace(1.0, 1e-3, args.frames)
    rng = np.random.default_rng(0)
    x0 = rng.normal(size=(args.paths, 2))
    rho = 0.30

    pos0 = rollout(X, Y, y, 0.0, x0, ts)
    posh = rollout(X, Y, y, h_star, x0, ts)
    # Endpoint smoothing shares the h* flow, then relaxes onto a continuous law: we
    # show it as the same trajectories with an isotropic jitter faded in near t=1.
    jitter = rng.normal(size=(args.paths, 2))

    def neff_along(h, n_probe=24):
        """Median n_eff of the index posterior over actual trajectories.

        Evaluating at the mean position of the cloud would be a point no
        trajectory visits, and at late times that point is nowhere near any atom.
        """
        probe = np.linspace(0, args.paths - 1, n_probe).astype(int)
        vals = []
        for k, t in enumerate(ts):
            pts = (pos0 if h == 0.0 else posh)[k][probe]
            xt = torch.tensor(pts, dtype=torch.float64)             # (P, d)
            z = (xt[:, None, :] - t * X[None, :, :]) / (1 - t)      # (P, N, d)
            lg = -0.5 * (z ** 2).sum(-1)
            if h > 0.0:
                lg = lg - 0.5 * ((y - Y) ** 2).sum(1)[None, :] / h ** 2
            w = torch.softmax(lg, dim=1).numpy()
            vals.append(float(np.median(1.0 / (w ** 2).sum(1))))
        return np.array(vals)

    neff_h = neff_along(h_star)

    fig = plt.figure(figsize=(12.6, 5.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[3.0, 1.0], hspace=0.32, wspace=0.08)
    axes = [fig.add_subplot(gs[0, c]) for c in range(3)]
    axn = fig.add_subplot(gs[1, :])
    lim = (Xn[:, 0].min() - 0.6, Xn[:, 0].max() + 0.6,
           Xn[:, 1].min() - 0.6, Xn[:, 1].max() + 0.6)

    titles = [r"hard conditioning  ($h=0$)",
              rf"label smoothing  ($h^\star={h_star:.2f}$)",
              rf"endpoint smoothing  ($\rho={rho}$)"]
    scats, tails, readouts = [], [], []
    for ax, ttl in zip(axes, titles):
        ax.scatter(Xn[:, 0], Xn[:, 1], s=8, color=OI["black"], alpha=0.4, zorder=2)
        tails.append(ax.plot([], [], lw=0.5, alpha=0.18, color=OI["black"])[0])
        scats.append(ax.scatter([], [], s=26, color=OI["vermillion"], alpha=0.8,
                                edgecolors="none", zorder=4))
        # The h=0 cloud ends as 160 points on one atom, i.e. one dot: annotate the
        # spread so what the eye cannot resolve is still on screen.
        readouts.append(ax.text(0.5, -0.045, "", transform=ax.transAxes,
                                ha="center", va="top", fontsize=9.5,
                                color=OI["vermillion"]))
        ax.set_title(ttl, fontsize=11)
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
        for s_ in ax.spines.values():
            s_.set_alpha(0.35)

    axn.plot(ts, neff_h, color=OI["blue"], lw=1.8, label=r"median $n_{\mathrm{eff}}$ along a trajectory, at $h^\star$")
    axn.axhline(1.0, color=OI["vermillion"], lw=1.2, ls="--",
                label=r"$n_{\mathrm{eff}}=1$ (a single atom)")
    marker = axn.axvline(ts[0], color=OI["black"], lw=1.2)
    axn.set_yscale("log"); axn.set_xlim(0, 1)
    axn.set_xlabel("flow time $t$", fontsize=9)
    axn.set_ylabel(r"$n_{\mathrm{eff}}$", fontsize=9)
    axn.legend(fontsize=8, loc="lower left"); axn.grid(alpha=0.3)
    sup = fig.suptitle("", fontsize=12)

    def update(k):
        t = ts[k]
        fade = float(np.clip((t - 0.9) / 0.1, 0, 1))       # ease the jitter in
        pts = [pos0[k], posh[k], posh[k] + rho * fade * jitter]
        for sc, tl, ro, pp, hist in zip(scats, tails, readouts, pts,
                                        (pos0[:k + 1], posh[:k + 1], posh[:k + 1])):
            sc.set_offsets(pp)
            tl.set_data(hist[:, ::12, 0], hist[:, ::12, 1])
            sd = float(np.sqrt(((pp - pp.mean(0)) ** 2).sum(1).mean()))
            ro.set_text(f"spread of the cloud: {sd:.3f}")
        marker.set_xdata([t, t])
        sup.set_text(f"$t = {t:.4f}$        "
                     f"$n_{{\\mathrm{{eff}}}}(h^\\star) = {neff_h[k]:.1f}$")
        return scats + tails + readouts + [marker, sup]

    anim = animation.FuncAnimation(fig, update, frames=len(ts), blit=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    anim.save(OUT, writer=animation.PillowWriter(fps=args.fps))
    plt.close(fig)
    print(f"Saved: {OUT}  ({len(ts)} frames, h*={h_star:.4f})")


if __name__ == "__main__":
    main()
