"""Animations for the project page: the result, and the family it belongs to.

Four, each showing something a still cannot.

  anim_cifar_training.gif   The collapse happening, on real images. Six completions
                            of the same masked photograph at successive training
                            iterations, from visibly different to pixel-identical --
                            and identical to a specific training image, shown in the
                            last column. The measured tr Cov falls 179.1 -> 0.431
                            across the frames.

  anim_cifar_bandwidth.gif  The remedy, and its ceiling. The same conditions at the
                            end of training, swept over the label bandwidth. Diversity
                            comes back as h grows, which is what a diversity metric
                            would reward -- while the fraction of samples that are
                            still training images stays high. Restored variance,
                            un-restored posterior, in photographs.

  anim_bandwidth_2d.gif     The whole family in one sweep. On the d=2 instance, the
                            exact endpoint law as h runs from 0 to large: a point
                            mass, then a kernel-weighted mixture that passes exactly
                            through tr Cov_h = tr Sigma_post, then the uniform
                            empirical measure. The two corollaries are the endpoints
                            of this animation.

  anim_guidance_3d.gif      The affine-hull result, rotated. Atoms spanning a plane in
                            R^3 and trajectories started off it, pulled in whatever
                            the guidance weight. Rotation is what makes the plane
                            legible; a fixed viewpoint hides it.

The first two are composed from grids already written during training, so they cost
nothing to rebuild. The last two integrate the closed-form fields.

    uv run python -m scripts.make_project_animations [--only NAME]

Writes: paper/figures/anim_*.gif
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageDraw, ImageFont

from src.metrics.kernel_theory import kernel_moments, kernel_weights
from src.problems.linear_gaussian import LinearGaussianProblem

FIGS = Path("paper/figures")
RUNS = Path("results/exp3")
OI = {"black": "#000000", "sky": "#56B4E9", "blue": "#0072B2",
      "vermillion": "#D55E00", "orange": "#E69F00", "green": "#009E73"}


# ------------------------------------------------------------------ image GIFs
def _font(size: int):
    """A readable font if the system has one; PIL's bitmap default is tiny."""
    for name in ("arial.ttf", "DejaVuSans.ttf", "Helvetica.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _banner(img: Image.Image, text: str, sub: str = "") -> Image.Image:
    """Add a caption strip above an existing grid image."""
    big, small = _font(30), _font(22)
    pad = 88 if sub else 52
    out = Image.new("RGB", (img.width, img.height + pad), "white")
    out.paste(img, (0, pad))
    d = ImageDraw.Draw(out)
    d.text((22, 14), text, fill=(0, 0, 0), font=big)
    if sub:
        d.text((22, 52), sub, fill=(190, 60, 0), font=small)
    return out


def _metric(run: str, it: int, col: str) -> float:
    df = pd.read_csv(RUNS / run / "raw" / "metrics.csv")
    return float(df[df["iter"] == it].iloc[0][col])


def cifar_training(fps=1.2):
    run = "exp3_cifar_ddpm_h0"
    its = [500, 2000, 8000, 20000, 40000, 60000]
    frames = []
    for it in its:
        p = RUNS / run / "figures" / f"grid_it{it}.png"
        if not p.exists():
            print(f"  [skip] {p} missing"); return
        tc = _metric(run, it, "trace_cov_mean")
        nn = _metric(run, it, "nn_dist_mean")
        frames.append(_banner(
            Image.open(p).convert("RGB"),
            f"hard conditioning (h=0)   iteration {it:,}",
            f"tr Cov = {tc:.4g}      distance to the nearest training image = {nn:.4g}"))
    frames += [frames[-1]] * 4                     # hold the endpoint
    out = FIGS / "anim_cifar_training.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=int(1000 / fps), loop=0)
    print(f"  {out.name}")


def cifar_bandwidth(fps=0.9):
    import json
    reev = {f"{float(r['h']):.0f}": r for r in
            json.loads((RUNS / "_cifar_ddpm" / "reeval.json").read_text("utf-8"))}
    frames = []
    for h in (0, 4, 5, 6):
        p = RUNS / f"exp3_cifar_ddpm_h{h}" / "figures" / "grid_it60000.png"
        if not p.exists():
            print(f"  [skip] {p} missing"); return
        r = reev[str(h)]
        frames.append(_banner(
            Image.open(p).convert("RGB"),
            f"label bandwidth h = {h}   (end of training)",
            f"tr Cov = {r['trace_cov']:.4g}      "
            f"fraction of samples that are training images = "
            f"{r['memorization_ratio']:.3f}"))
    frames = frames + frames[::-1][1:]             # sweep up and back
    out = FIGS / "anim_cifar_bandwidth.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=int(1000 / fps), loop=0)
    print(f"  {out.name}")


# -------------------------------------------------------------------- 2-d sweep
def bandwidth_2d(frames=64, fps=12):
    torch.manual_seed(0)
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    Xt, Yt = prob.sample_dataset(200, seed=1)
    X, Y = Xt.to(torch.float64), Yt.to(torch.float64)
    Xn = X.numpy()
    i = int(np.argmin(np.abs(Y[:, 0].numpy() - np.median(Y[:, 0].numpy()))))
    y = Y[i]
    tr_post = float(np.trace(prob.Sigma_post.numpy()))

    hs = np.concatenate([[0.0], np.geomspace(0.02, 8.0, frames - 1)])
    ws, trs, nes = [], [], []
    for h in hs:
        w = kernel_weights(y, Y, float(h)).numpy()
        _, cov, ne = kernel_moments(y, X, Y, float(h))
        ws.append(w); trs.append(float(torch.trace(cov))); nes.append(ne)

    # figsize x dpi must land on an integer: 10.2 * 100 is 1019.9999... in binary,
    # so the writer declares 1019 while the canvas is 1020 wide and every row is
    # offset by a pixel, shearing the whole animation.
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0),
                             gridspec_kw={"width_ratios": [1.25, 1.0]})
    ax, axc = axes
    ax.scatter(Xn[:, 0], Xn[:, 1], s=10, color=OI["black"], alpha=0.35, zorder=2)
    sc = ax.scatter(Xn[:, 0], Xn[:, 1], s=np.zeros(len(Xn)), color=OI["vermillion"],
                    alpha=0.8, edgecolors="none", zorder=4)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    ax.set_title(r"endpoint law $p_1=\sum_i p^{(h)}_i\delta_{x^i}$", fontsize=11)

    axc.plot(hs[1:], trs[1:], color=OI["blue"], lw=1.8, label=r"$\mathrm{tr}\,\mathrm{Cov}_h$")
    axc.axhline(tr_post, color=OI["vermillion"], ls="--", lw=1.3,
                label=r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    vline = axc.axvline(hs[1], color=OI["black"], lw=1.2)
    axc.set_xscale("log"); axc.set_yscale("log")
    axc.set_xlabel("bandwidth $h$"); axc.grid(alpha=0.3)
    axc.legend(fontsize=8, loc="upper left")
    axc.set_title("the reference curve, swept", fontsize=11)
    sup = fig.suptitle("", fontsize=12)

    def update(k):
        sc.set_sizes(12 + 2600 * ws[k])
        if k > 0:
            vline.set_xdata([hs[k], hs[k]])
        note = ("a single atom" if nes[k] < 1.05 else
                ("matches the posterior trace" if abs(trs[k] - tr_post) / tr_post < 0.03
                 else ("the uniform empirical measure" if nes[k] > 0.9 * len(Xn) else "")))
        sup.set_text(f"$h = {hs[k]:.3f}$        "
                     f"$n_{{\\mathrm{{eff}}}} = {nes[k]:.1f}$        "
                     f"$\\mathrm{{tr}}\\,\\mathrm{{Cov}}_h = {trs[k]:.3f}$"
                     + (f"        {note}" if note else ""))
        return [sc, vline, sup]

    fig.tight_layout()
    anim = animation.FuncAnimation(fig, update, frames=len(hs), blit=False)
    out = FIGS / "anim_bandwidth_2d.gif"
    anim.save(out, writer=animation.PillowWriter(fps=fps), dpi=100)
    plt.close(fig)
    print(f"  {out.name}")


# ------------------------------------------------------------------ rotating 3-d
def guidance_3d(n_az=60, fps=14, n_steps=8000):
    rng = np.random.default_rng(0)
    N, h = 6, 0.6
    X = rng.normal(size=(N, 2)) * 1.5
    Y = rng.normal(size=(N, 1))
    i = 2
    y = Y[i].copy()
    X3 = np.concatenate([X, np.zeros((N, 1))], 1)
    ts = 1.0 - np.geomspace(1.0, 1e-6, n_steps + 1)

    def path(w, x0):
        x, out = x0.copy(), [x0.copy()]
        for a, b in zip(ts[:-1], ts[1:]):
            dt = b - a
            z = (x[None, :] - a * X3) / (1 - a)
            lsp = -0.5 * (z ** 2).sum(1)
            lc = lsp - 0.5 * ((y[None, :] - Y) ** 2).sum(1) / h ** 2
            wc = np.exp(lc - lc.max()); wc /= wc.sum()
            qq = np.exp(lsp - lsp.max()); qq /= qq.sum()
            m = (1 + w) * (wc @ X3) - w * (qq @ X3)
            x = x + dt * (m - x) / (1 - a)
            out.append(x.copy())
        return np.stack(out)[::40]

    starts = rng.normal(size=(6, 3)) * 1.7
    paths = {w: [path(w, s) for s in starts] for w in (0.0, 15.0)}

    fig = plt.figure(figsize=(6.2, 5.2))
    ax = fig.add_subplot(projection="3d")
    gx = np.linspace(X3[:, 0].min() - 1.2, X3[:, 0].max() + 1.2, 2)
    gy = np.linspace(X3[:, 1].min() - 1.2, X3[:, 1].max() + 1.2, 2)
    GX, GY = np.meshgrid(gx, gy)

    def update(k):
        ax.clear()
        ax.plot_surface(GX, GY, np.zeros_like(GX), alpha=0.17, color=OI["sky"],
                        edgecolor="none")
        for w, c in ((0.0, OI["sky"]), (15.0, OI["vermillion"])):
            for j, tr in enumerate(paths[w]):
                ax.plot(tr[:, 0], tr[:, 1], tr[:, 2], color=c, lw=1.1, alpha=0.8,
                        label=(f"trajectory, $w={w:g}$" if j == 0 else None))
                ax.scatter(*tr[-1], s=28, color=c)
        ax.scatter(X3[:, 0], X3[:, 1], X3[:, 2], s=44, color=OI["black"],
                   label="training atoms")
        ax.scatter(*X3[i], marker="*", s=260, color=OI["blue"],
                   label="conditioned atom")
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=16 + 8 * np.sin(2 * np.pi * k / n_az), azim=-60 + 360 * k / n_az)
        ax.set_title("guidance cannot leave the affine hull", fontsize=11)
        ax.legend(fontsize=7.5, loc="upper left")
        return []

    anim = animation.FuncAnimation(fig, update, frames=n_az, blit=False)
    out = FIGS / "anim_guidance_3d.gif"
    anim.save(out, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)
    print(f"  {out.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    FIGS.mkdir(parents=True, exist_ok=True)
    jobs = {"cifar_training": cifar_training, "cifar_bandwidth": cifar_bandwidth,
            "bandwidth_2d": bandwidth_2d, "guidance_3d": guidance_3d}
    for name, fn in jobs.items():
        if args.only in (None, name):
            fn()
