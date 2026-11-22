"""Figures of paper B (paper_mechanism/), redrawn at their printed widths.

    PYTHONPATH=.:scripts python scripts/make_paperB_figures.py [name ...]

Writes into paper_mechanism/figures (names as in paper_mechanism/main.tex):
    fig_intuition.pdf          Figure 1: one sampling step, and the guesses of two EDM models on one latent.
    fig_unrolled_learned.pdf   Figure 2: 1-D flows unrolled in time, exact field and two learned fields.
    fig_landscape.pdf          the exact landscape -log p_t in d=2, with an exact and a learned trajectory.
    fig_exp1_collapse.pdf      EXP-1 at h=0, five seeds.
    fig_cifar_collapse.pdf     CIFAR-10 U-Net at h=0: generated variance, and completions through training.
    fig_kernel_tracking.pdf    label smoothing against the kernel reference, EXP-1 and CIFAR-10.
    fig_edm_clocks.pdf         EDM: selection (swap), relative error by group, detector AUCs.
    fig_heun.pdf               Heun step weights, the contraction threshold, certificate coverage.
    fig_image_training.pdf     appendix: CIFAR-10 completions at every checkpoint.
    fig_image_class.pdf        appendix: class-conditional CIFAR-10.

Since the second figure design (scripts/make_paperB_figures_v2.py), paper_mechanism/main.tex includes only
fig_heun, fig_image_training and fig_image_class from this script; the other figures above are superseded by
fig_teaser, fig_mechanism, fig_collapse, fig_collapse_details and fig_landing, and are kept for reference.

Every plotted number and image is read from results/ (or, for the toy flows of Figures 2 and 3,
computed here from the closed-form fields); nothing is typed in. Needs numpy and matplotlib only
(no pandas, no torch). The scripts this replaces for paper B, make_edm_figures.py and
make_results_figures.py, are left as they are: they still draw paper/ and paper_theory/.
"""
from __future__ import annotations

import csv
import glob
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from scripts.figstyle import COLORS, FULL_W, OI, use_paper_style
from scripts.make_edm_figures import _img, _m1d, _rhocrit, _run1d, _swap, _toy, auc
from scripts.make_image_bandwidth_figure import cells

R = Path("results")
OUT = Path("paper_mechanism/figures")
EXP1 = R / "exp1"
EXP3 = R / "exp3"

EXACT, LEARNED, ATOM = COLORS["exact"], COLORS["learned"], COLORS["atom"]
GREY = "#6E6E6E"
LIGHT = "#BDBDBD"
GOOD = OI["green"]            # a step that contracts toward the image
# EDM models: the memorising 500-image model is drawn in black (its samples are training images),
# the public model in orange; on-/off-atom groups are black / vermillion.
M500, MPUB = "#222222", OI["orange"]
ON, OFF = "#222222", OI["vermillion"]
STEPS = {18: "#222222", 36: OI["green"], 64: OI["purple"]}


# --------------------------------------------------------------------------- helpers
def save(fig, name: str, pad: float = 0.015, **kw) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=pad, **kw)
    plt.close(fig)
    print(f"  wrote {OUT / name}")


def axes_in(fig, x, y, w, h, **kw):
    """An axis placed in inches from the lower-left corner of the figure."""
    W, H = fig.get_size_inches()
    return fig.add_axes([x / W, y / H, w / W, h / H], **kw)


def title(ax, letter: str, text: str = "", fs: float = 8.5, pad: float = 4.0):
    """'(a) takeaway' at the top left of a panel: the letter in bold sans, the text in regular weight.
    (Mathtext \\bf would set the letter in bold STIX serif.)"""
    t1 = ax.annotate(f"({letter})", xy=(0, 1), xycoords="axes fraction", xytext=(0, pad),
                     textcoords="offset points", fontweight="bold", fontsize=fs, ha="left", va="bottom")
    if text:
        ax.annotate(" " + text, xy=(1, 0), xycoords=t1, ha="left", va="bottom", fontsize=fs)
    return t1


def figtitle(fig, x: float, y: float, letter: str, text: str = "", fs: float = 8.5):
    """The same at figure coordinates (inches from the lower left)."""
    from matplotlib.text import Annotation
    W, H = fig.get_size_inches()
    t1 = fig.text(x / W, y / H, f"({letter})", fontweight="bold", fontsize=fs, ha="left", va="bottom")
    if text:
        fig.add_artist(Annotation(" " + text, xy=(1, 0), xycoords=t1, ha="left", va="bottom", fontsize=fs))
    return t1


def label(ax, x, y, text, color, ha="left", va="center", dx=3.0, dy=0.0, fs=7.0, **kw):
    """Direct label of a line, in its own colour."""
    return ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                       color=color, fontsize=fs, **kw)


def blank(ax) -> None:
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)


def tile(ax, img, frame=None, lw=1.0) -> None:
    """An image with a thin frame of the given colour (no frame if None)."""
    ax.imshow(img, interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(frame is not None)
        if frame is not None:
            s.set_color(frame); s.set_linewidth(lw)


def read_csv(path) -> dict[str, np.ndarray]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows]
        try:
            out[k] = np.array([float(v) if v != "" else np.nan for v in vals])
        except ValueError:
            out[k] = np.array(vals)
    return out


def seed_mean(pattern: str, group: str, col: str):
    """Mean and population SD across the five seeds, per iteration."""
    files = sorted(glob.glob(pattern))
    assert len(files) == 5, pattern
    per = []
    for f in files:
        d = read_csv(f)
        keep = d["group"] == group
        per.append(dict(zip(d["iter"][keep].astype(int), d[col][keep])))
    its = sorted(set.intersection(*(set(p) for p in per)))
    v = np.array([[p[i] for i in its] for p in per])
    return np.array(its, float), v.mean(0), v.std(0)


def band(ax, x, m, sd, color, ls="-", marker="o", ms=3.0, lw=1.4, alpha=0.15):
    ax.plot(x, m, color=color, ls=ls, marker=marker, ms=ms, lw=lw, mec="white", mew=0.4)
    ax.fill_between(x, m - sd, m + sd, color=color, alpha=alpha, lw=0)


def frac_q(z):
    return z["d1"] / z["d2"]


# --------------------------------------------------------------------------- Figure 1
def _cartoon(ax):
    """One Euler step x -> x' = r x + (1-r) D. x' is closer to the image a iff D lies inside the circle
    of radius |x-a| around a (for this r), which is the condition rho < 1 of Theorem thm:relerr."""
    a = np.array([0.0, 0.0]); x = np.array([1.0, 0.55]); n = np.linalg.norm(x - a); r = 0.45
    d_in, d_out = np.array([-0.35, -0.25]), np.array([1.25, 1.62])
    ax.add_patch(Circle(a, n, facecolor=GOOD, alpha=0.10, lw=0))
    ax.add_patch(Circle(a, n, fill=False, ls=(0, (3, 2)), lw=0.8, ec=GREY))
    ax.text(0.5, -0.78, r"$\varrho<1$", fontsize=7.5, color=GOOD, ha="center")
    ax.text(-1.0, 1.2, r"$\varrho>1$", fontsize=7.5, color=GREY, ha="center")
    ax.scatter(*a, s=42, marker="s", color=ATOM, zorder=5)
    ax.text(0.0, -0.2, "training\nimage", fontsize=6.5, ha="center", va="top", linespacing=0.95)
    for d, good in ((d_in, True), (d_out, False)):
        xn = r * x + (1 - r) * d
        c = GOOD if good else GREY
        ax.plot(*zip(x, d), ls=":", color=LEARNED, lw=0.8, zorder=2)
        ax.add_patch(FancyArrowPatch(x, xn, arrowstyle="-|>", mutation_scale=8, lw=1.3, color=c,
                                     zorder=4, shrinkA=2, shrinkB=0))
        ax.scatter(*d, s=26, marker="D", color=LEARNED, zorder=5, lw=0)
    ax.scatter(*x, s=24, color="white", edgecolors="k", linewidths=0.8, zorder=6)
    ax.text(x[0] + 0.09, x[1] - 0.05, r"$x$", fontsize=8.5, va="center")
    ax.text(d_in[0] - 0.1, d_in[1] - 0.04, "guess", fontsize=6.8, color=LEARNED, ha="right", va="center")
    ax.text(d_out[0] - 0.1, d_out[1] + 0.02, "guess", fontsize=6.8, color=LEARNED, ha="right", va="center")
    xi = r * x + (1 - r) * d_in
    ax.text(xi[0] + 0.06, xi[1] - 0.16, "closer", fontsize=6.8, color=GOOD, ha="left", va="center")
    xo = r * x + (1 - r) * d_out
    ax.text(xo[0] + 0.08, xo[1] - 0.04, "farther", fontsize=6.8, color=GREY, ha="left", va="center")
    ax.set_xlim(-1.45, 1.75); ax.set_ylim(-1.32, 1.85); ax.set_aspect("equal")
    blank(ax)


def fig_intuition(i: int = 17, steps=(5, 8, 10, 12, 14, 16)):
    zs = np.load(R / "n3_strips_20261118/sub500.npz"); zp = np.load(R / "n3_strips_20261118/public.npz")
    sg = zs["sigma"]
    assert np.allclose(sg, zp["sigma"])
    W, H = FULL_W, 2.86
    fig = plt.figure(figsize=(W, H))
    # (a) the cartoon
    ax = axes_in(fig, 0.0, 0.3, 1.78, 1.78 * 3.17 / 3.2)
    _cartoon(ax)
    figtitle(fig, 0.0, H - 0.15, "a", "one sampling step")
    fig.text(0.0, (H - 0.32) / H, "moves $x$ toward the network's guess", fontsize=7, va="bottom", color=GREY)

    # (b) the guesses of two models on one latent
    s, g = 0.455, 0.035                      # tile size and gap, inches
    x0 = 2.37
    xs = [x0 + j * (s + g) for j in range(len(steps))]
    xo = xs[-1] + s + 0.16
    xe = [xo, xo + s + g]
    y2 = 1.3
    y1 = y2 + s + 0.2
    figtitle(fig, 1.95, H - 0.15, "b", "the same latent through two EDM models")
    # column heads
    fig.text((xs[0] + xs[-1] + s) / 2 / W, (y1 + s + 0.17) / H, r"guess $D_\theta(x)$ at noise level $\sigma$",
             ha="center", va="bottom", fontsize=7)
    fig.add_artist(Line2D([xs[0] / W, (xs[-1] + s) / W], [(y1 + s + 0.155) / H] * 2, color=LIGHT, lw=0.6))
    for j, k in enumerate(steps):
        fig.text((xs[j] + s / 2) / W, (y1 + s + 0.03) / H, f"{sg[k]:.2g}", ha="center", va="bottom", fontsize=7)
    for xx, t in zip(xe, ("output", "nearest\ntraining\nimage")):
        fig.text((xx + s / 2) / W, (y1 + s + 0.03) / H, t, ha="center", va="bottom", fontsize=6.5,
                 linespacing=0.9)
    rows = ((zs, y1, M500, "500\nimages"), (zp, y2, MPUB, "public\n(50k)"))
    for z, y, col, name in rows:
        fig.text((xs[0] - 0.07) / W, (y + s / 2) / H, name, ha="right", va="center", fontsize=7, color=col,
                 linespacing=0.95, fontweight="bold")
        for j, k in enumerate(steps):
            tile(axes_in(fig, xs[j], y, s, s), _img(z["D"][i, k].astype(np.float32)), col, 0.9)
        tile(axes_in(fig, xe[0], y, s, s), _img(z["end"][i].astype(np.float32)), col, 0.9)
        tile(axes_in(fig, xe[1], y, s, s), _img(z["y1"][i].astype(np.float32)), LIGHT, 0.6)
    # the relative error of each guess, aligned with the columns
    ph = 0.8
    ax = axes_in(fig, xs[0], 0.33, xs[-1] + s - xs[0], ph)
    pad = (s / 2) / (s + g)
    ax.set_xlim(-pad, len(steps) - 1 + pad); ax.set_ylim(-0.04, 1.1)
    xx = np.arange(len(steps))
    ax.axhline(1, color=GREY, ls=(0, (3, 2)), lw=0.8)
    ax.text(-pad + 0.08, 0.95, r"$\varrho=1$: no contraction", fontsize=6.5, color=GREY, va="top")
    for z, col in ((zs, M500), (zp, MPUB)):
        v = z["rho"][i, list(steps)]
        ax.plot(xx, v, color=col, marker="o", ms=3.2, lw=1.3, mec="white", mew=0.4, clip_on=False)
        label(ax, xx[-1], v[-1], rf"$\varrho={v[-1]:.2f}$", col, dx=5, fs=6.6,
              dy=3 if col == MPUB else -3, va="bottom" if col == MPUB else "top")
    ax.set_xticks(xx, [f"{sg[k]:.2g}" for k in steps])
    ax.set_yticks([0, 0.5, 1])
    ax.set_ylabel(r"relative error $\varrho$", fontsize=7)
    ax.set_xlabel(r"noise level $\sigma$", fontsize=7, labelpad=1)
    ax.tick_params(labelsize=6.5)
    # the verdict under the two end columns of each row
    for z, col, yy, word in ((zs, M500, y1, "copy"), (zp, MPUB, y2, "new image")):
        q = float(frac_q(z)[i])
        fig.text((xe[0] + xe[1] + s) / 2 / W, (yy - 0.03) / H, word + rf", $d_1/d_2={q:.2f}$", fontsize=6.6,
                 color=col, va="top", ha="center")
    save(fig, "fig_intuition.pdf")


# --------------------------------------------------------------------------- Figure 2
def fig_unrolled_learned():
    """Panels (a) label noise on the exact field, (b) learned with relative error 0.6, (c) learned with relative
    error tending to 1; the fields are those of make_edm_figures.fig_unrolled (indices 0, 3, 4)."""
    rng = np.random.default_rng(0)
    z0 = np.sort(rng.normal(size=1500))
    at4 = np.array([-2.1, -0.7, 0.7, 2.1]); p = np.array([0.12, 0.48, 0.28, 0.12])
    panels = [
        ("exact", "label noise", "copies (reweighted)",
         lambda z, t: _m1d(z, t, at4, p) - z),
        ("learned", r"$\varrho=0.6$", "still copies",
         lambda z, t: 0.4 * (_m1d(z, t, at4, p) - z)),
        ("learned", r"$\varrho_t\to1$ late", "new samples",
         lambda z, t: 0.6 * np.sqrt(1 - t) * (_m1d(z, t, at4, p) - z)),
    ]
    lane = ["#009E73", "#E69F00", "#CC79A7", "#56B4E9"]
    W, H = 0.62 * FULL_W, 2.45
    fig = plt.figure(figsize=(W, H))
    gs = fig.add_gridspec(3, 4, height_ratios=[0.2, 1, 0.36], width_ratios=[1, 0.1, 1, 1],
                          hspace=0.0, wspace=0.07, left=0.05, right=0.995, top=0.84, bottom=0.1)
    xs = np.linspace(-3.4, 3.4, 400)
    tops = {}
    for k, ((kind, ttl, sub, F), c) in enumerate(zip(panels, (0, 2, 3))):
        ts, P = _run1d(F, z0)
        end = P[-1]
        near = np.abs(end[:, None] - at4[None]).argmin(1)
        top = fig.add_subplot(gs[0, c]); mid = fig.add_subplot(gs[1, c], sharex=top)
        bot = fig.add_subplot(gs[2, c], sharex=top)
        tops.setdefault(kind, []).append(top)
        out_c = EXACT if kind == "exact" else LEARNED
        top.fill_between(xs, 0, np.exp(-xs ** 2 / 2), color=LIGHT, alpha=0.6, lw=0)
        for j in np.linspace(0, len(z0) - 1, 140).astype(int):
            mid.plot(P[:, j], ts, color=lane[near[j]], lw=0.45, alpha=0.6)
        if kind == "learned" and k == 2:            # new samples: a smooth density
            dens = np.exp(-(xs[:, None] - end[None]) ** 2 / (2 * 0.06 ** 2)).sum(1)
            bot.fill_between(xs, 0, -0.75 * dens / dens.max(), color=out_c, alpha=0.8, lw=0)
        else:                                       # copies: point masses, stems of height = mass
            for x_ in at4:
                m = float(np.mean(np.abs(end - x_) < 0.1))
                if m > 0.005:
                    bot.plot([x_, x_], [0, -m], color=out_c, lw=2.0, solid_capstyle="butt")
                    bot.scatter([x_], [-m], s=9, color=out_c, zorder=4, lw=0)
        bot.scatter(at4, np.zeros_like(at4), marker="|", s=36, color=ATOM, zorder=3, lw=1.0)
        for a in (top, mid, bot):
            blank(a)
        mid.set_ylim(1.0, 0.0); mid.set_xlim(-3.4, 3.4)
        bot.set_ylim(-1.0, 0.1); top.set_ylim(0, 1.15)
        title(top, "abc"[k], ttl, fs=8, pad=1)
        bot.text(0.5, -0.1, sub, transform=bot.transAxes, ha="center", va="top", fontsize=7.2, color=out_c)
        if k == 0:
            mid.annotate("", xy=(-3.3, 0.95), xytext=(-3.3, 0.05),
                         arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.7))
            mid.text(-3.15, 0.5, r"$t$", fontsize=8, color=GREY, va="center")
            top.text(-3.4, 0.95, "noise", fontsize=6.5, color=GREY, va="top")
            bot.text(-3.4, -0.3, "output", fontsize=6.5, color=GREY, va="top")
    for kind, txt in (("exact", "exact field"), ("learned", "learned field")):
        axs = tops[kind]
        a0 = min(a.get_position().x0 for a in axs) + 0.01
        a1 = max(a.get_position().x1 for a in axs) - 0.01
        col = EXACT if kind == "exact" else LEARNED
        fig.add_artist(Line2D([a0, a1], [0.955, 0.955], color=col, lw=0.8))
        fig.text((a0 + a1) / 2, 0.965, txt, ha="center", va="bottom", fontsize=8, color=col)
    save(fig, "fig_unrolled_learned.pdf")


# --------------------------------------------------------------------------- landscape
def fig_landscape():
    """-log p_t of three training points at three times, with the exact flow (blue) and a learned flow with
    relative error -> 1 (vermillion) from the same start. Heights are rescaled per panel (log scale)."""
    from matplotlib.transforms import Bbox
    atoms = np.array([[-1.6, -0.9], [1.7, -0.6], [0.1, 1.7]])
    x0 = np.array([[2.4, 1.0]])
    ts_e, Pe = _toy(atoms, x0, "exact")
    ts_l, Pl = _toy(atoms, x0, "late")
    gx = np.linspace(-3.0, 3.0, 200); Xg, Yg = np.meshgrid(gx, gx)
    Z2 = np.stack([Xg.ravel(), Yg.ravel()], 1)

    def U(z, t):
        d2 = ((z[:, None, :] - t * atoms[None]) ** 2).sum(-1) / (2 * (1 - t) ** 2)
        m = d2.min(1)
        return m - np.log(np.exp(-(d2 - m[:, None])).sum(1)) + 2 * np.log(1 - t)

    shots = [(0.35, "one smooth bowl"), (0.75, "a well per training point"),
             (0.985, "the wells narrow to points")]
    W = FULL_W
    fig = plt.figure(figsize=(W, 1.95))
    for k, (t, ttl) in enumerate(shots):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d", computed_zorder=False)
        u = U(Z2, t); umin = u.min()
        cap = float(np.log1p(np.ptp(u)))
        Hs = (np.log1p(u - umin) / cap).reshape(Xg.shape)
        ax.plot_surface(Xg, Yg, Hs, cmap="Greys_r", vmin=-0.35, vmax=1.25, rstride=2, cstride=2,
                        linewidth=0.08, edgecolor=(1, 1, 1, 0.12), antialiased=True, alpha=0.95,
                        rasterized=True)
        for P, ts, col in ((Pe, ts_e, EXACT), (Pl, ts_l, LEARNED)):
            path = P[ts <= t, 0, :]
            hp = np.log1p(U(path, t) - umin) / cap
            ax.plot(path[:, 0], path[:, 1], hp + 0.03, color=col, lw=1.5, zorder=10)
            ax.scatter(path[-1, 0], path[-1, 1], hp[-1] + 0.05, s=16, color=col, edgecolors="white",
                       linewidths=0.5, zorder=11, depthshade=False)
        ax.view_init(elev=42, azim=-100); ax.set_axis_off(); ax.set_zlim(0, 1.0)
        ax.set_box_aspect((1, 1, 0.62), zoom=1.3)
        if k == 2:                                  # direct labels at the two endpoints
            pe, pl = Pe[ts_e <= t, 0, :][-1], Pl[ts_l <= t, 0, :][-1]
            ax.text(pe[0] + 0.35, pe[1], np.log1p(U(pe[None], t) - umin)[0] / cap + 0.02, "exact: copy",
                    color=EXACT, fontsize=7, zorder=12)
            ax.text(pl[0] + 0.35, pl[1], np.log1p(U(pl[None], t) - umin)[0] / cap + 0.05, "learned:\nstops",
                    color=LEARNED, fontsize=7, zorder=12, linespacing=0.95)
    fig.subplots_adjust(left=0, right=1, bottom=-0.3, top=0.9, wspace=-0.05)
    for k, (t, ttl) in enumerate(shots):
        pos = fig.axes[k].get_position()
        figtitle(fig, (pos.x0 + 0.03) * FULL_W, 0.9 * 1.95, "abc"[k], rf"$t={t}$: {ttl}", fs=8)
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    fig.savefig(OUT / "fig_landscape.pdf", dpi=300,
                bbox_inches=Bbox.from_extents(bb.x0, bb.y0 + 0.17 * bb.height, bb.x1, bb.y1 + 0.02))
    plt.close(fig)
    print(f"  wrote {OUT / 'fig_landscape.pdf'}")


# --------------------------------------------------------------------------- EXP-1
def fig_exp1():
    const = f"{EXP1}/exp1_cond_seed[0-4]/raw/metrics.csv"
    cosine = f"{EXP1}/exp1_ext_sched_seed[0-4]/raw/metrics.csv"
    uncond = f"{EXP1}/exp1_uncond_seed[0-4]/raw/metrics.csv"
    it_c, tc, tc_sd = seed_mean(const, "train", "trace_cov_mean")
    it_s, ts_, ts_sd = seed_mean(cosine, "train", "trace_cov_mean")
    it_u, tu, tu_sd = seed_mean(uncond, "uncond", "trace_cov_mean")
    post = seed_mean(const, "train", "trace_post")[1].mean()
    data = seed_mean(uncond, "uncond", "trace_data")[1].mean()
    assert abs(tc[list(it_c).index(200000)] - 0.396) < 5e-4
    assert abs(ts_[list(it_s).index(1000000)] - 0.120) < 5e-4

    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 2.0))
    ax = axes[0]
    band(ax, it_u, tu, tu_sd, GREY)
    band(ax, it_c, tc, tc_sd, LEARNED)
    band(ax, it_s, ts_, ts_sd, LEARNED, ls="--", marker="s")
    ax.axhline(data, color=GREY, ls=":", lw=1.0)
    ax.axhline(post, color=EXACT, ls=":", lw=1.0)
    ax.text(110, data * 1.13, r"unconditional, at $\mathrm{tr}\,\widehat\Sigma_X$", fontsize=6.5, color=GREY)
    ax.text(110, post * 0.58, r"$\mathrm{tr}\,\Sigma_{\rm post}$ (exact posterior)", fontsize=6.5, color=EXACT)
    label(ax, it_c[-1], tc[-1], f"{tc[-1]:.2f}", LEARNED, dx=-2, dy=-7, ha="right", fs=6.5)
    label(ax, it_s[-1], ts_[-1], f"{ts_[-1]:.2f}", LEARNED, dx=3, dy=0, fs=6.5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(0.06, 4.0)
    ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    title(ax, "a", "variance collapses")

    ax = axes[1]
    for pat, ls, mk in ((const, "-", "o"), (cosine, "--", "s")):
        for col, c in (("mean_err_train_point_mean", ATOM), ("mean_err_post_mean", EXACT)):
            it, m, sd = seed_mean(pat, "train", col)
            band(ax, it, m, sd, c, ls=ls, marker=mk, alpha=0.1)
    ax.set_xscale("log")
    ax.text(150, 0.98, r"to the training atom $x^i$", fontsize=6.8, color=ATOM, va="bottom")
    ax.text(150, 0.28, "to the posterior mean", fontsize=6.8, color=EXACT, va="bottom")
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("distance of generated mean")
    title(ax, "b", "mean moves to the atom")

    ax = axes[2]
    for pat, ls, mk in ((const, "-", "o"), (cosine, "--", "s")):
        it, m, sd = seed_mean(pat, "train", "vel_rel_err_mean_mean")
        band(ax, it, m, sd, LEARNED, ls=ls, marker=mk)
    ax.set_xscale("log"); ax.set_ylim(0, 0.9)
    ax.set_ylabel(r"rel. velocity error to $(\star)$")
    title(ax, "c", r"field approaches $(\star)$")
    for ax in axes:
        ax.set_xlabel("training iteration")
        ax.set_xlim(70, 1.6e6)
    hs = [Line2D([], [], color="k", lw=1.3, marker="o", ms=3), Line2D([], [], color="k", lw=1.3, ls="--",
                                                                      marker="s", ms=3)]
    fig.legend(hs, ["constant learning rate", r"cosine schedule to $10^6$"], loc="upper center", ncol=2,
               bbox_to_anchor=(0.5, 1.07), fontsize=7, columnspacing=2.0, handlelength=2.4)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_exp1_collapse.pdf")


# --------------------------------------------------------------------------- CIFAR-10 collapse
def fig_cifar():
    runs = ["exp3_cifar_ddpm_h0", "exp3_cifar_ddpm_h0_seed1", "exp3_cifar_ddpm_h0_seed2"]
    met = [read_csv(EXP3 / r / "raw" / "metrics.csv") for r in runs]
    first = dict(zip(met[0]["iter"].astype(int), met[0]["trace_cov_mean"]))
    assert abs(first[500] - 179.1) < 0.05 and abs(first[60000] - 0.431) < 5e-4
    iters = (500, 2000, 8000, 60000)
    cond, comp = 0, (1, 2, 3, 4)                    # the frog; four of the six completions

    W, H = FULL_W, 2.25
    fig = plt.figure(figsize=(W, H))
    ax = axes_in(fig, 0.42, 0.36, 2.2, 1.55)
    shades = [LEARNED, "#E8955E", "#F2C29F"]
    for m, c, mk, nm in zip(met, shades, ("o", "s", "^"), ("instance 1", "2", "3")):
        ax.plot(m["iter"], m["trace_cov_mean"], color=c, marker=mk, ms=3.2, lw=1.3, mec="white", mew=0.4)
    for it in iters:                                 # the checkpoints shown on the right
        ax.plot(it, first[it], marker="o", ms=6.5, mfc="none", mec="k", mew=0.7, zorder=5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.text(0.04, 0.17, "three instances (overlapping)", transform=ax.transAxes, color=LEARNED, fontsize=6.6)
    ax.plot([0.07], [0.09], transform=ax.transAxes, marker="o", ms=6.5, mfc="none", mec="k", mew=0.7)
    ax.text(0.12, 0.09, "shown in (b)", transform=ax.transAxes, fontsize=6.6, va="center")
    figtitle(fig, 0.0, 2.06, "a", "generated variance collapses")

    s, g = 0.42, 0.03
    x0 = 3.6
    cols = [x0, x0 + s + 0.1] + [x0 + s + 0.1 + j * (s + g) for j in range(1, len(comp))] \
        + [x0 + s + 0.1 + len(comp) * (s + g) + 0.07]
    yt = 0.1 + (len(iters) - 1) * (s + g)
    figtitle(fig, 2.95, 2.06, "b", "completions of one condition, instance 1")
    heads = ["observed"] + ["completions from four sources $x_0$"] + [""] * (len(comp) - 1) + ["training image"]
    for j, (xx, hd) in enumerate(zip(cols, heads)):
        if hd and j == 1:
            fig.text((cols[1] + cols[len(comp)] + s) / 2 / W, (yt + s + 0.04) / H, hd, ha="center",
                     va="bottom", fontsize=7)
        elif hd:
            fig.text((xx + s / 2) / W, (yt + s + 0.04) / H, hd, ha="center", va="bottom", fontsize=7,
                     linespacing=0.9)
    for r, it in enumerate(iters):
        y = yt - r * (s + g)
        sheet = cells(EXP3 / runs[0] / "figures" / f"grid_it{it}.png")
        imgs = [sheet[cond][0]] + [sheet[cond][c] for c in comp] + [sheet[cond][7]]
        for j, (xx, im) in enumerate(zip(cols, imgs)):
            fr = LIGHT if j == 0 else (ATOM if j == len(imgs) - 1 else LEARNED)
            tile(axes_in(fig, xx, y, s, s), im, fr, 0.8)
        fig.text((x0 - 0.06) / W, (y + s / 2) / H, f"{it:,}".replace(",", r"$\,$") + "\n" +
                 rf"$\mathrm{{tr}}={first[it]:.3g}$", ha="right", va="center", fontsize=6.5, linespacing=1.0)
    fig.text((x0 - 0.06) / W, (yt + s + 0.04) / H, "iteration", ha="right", va="bottom", fontsize=7)
    save(fig, "fig_cifar_collapse.pdf", dpi=300)


# --------------------------------------------------------------------------- kernel tracking
def ols(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    slope = float((xc * yc).sum() / (xc * xc).sum())
    resid = yc - slope * xc
    se = float(np.sqrt((resid ** 2).sum() / (len(x) - 2) / (xc * xc).sum()))
    return slope, float(y.mean() - slope * x.mean()), se


def fig_kernel():
    d = read_csv(EXP1 / "_theory" / "raw" / "p7_kernel.csv")
    hs = sorted(set(d["h"]))
    def agg(col, f=np.mean):
        return np.array([f(d[col][d["h"] == h]) for h in hs])
    meas, meas_sd = agg("trace_meas"), agg("trace_meas", np.std)
    kern, post = agg("trace_kernel"), agg("trace_post")
    ratio, ratio_sd = agg("ratio_to_kernel"), agg("ratio_to_kernel", np.std)
    neff = agg("n_eff")
    assert np.allclose(ratio, [1.308, 1.002, 0.994, 1.011], atol=5e-4), ratio
    rows = json.loads((EXP3 / "_cifar_ddpm" / "reeval.json").read_text(encoding="utf-8"))
    by_h = {float(r["h"]): r for r in rows}
    x = np.arange(len(hs))

    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 2.05), gridspec_kw={"width_ratios": [1, 1, 1.1]})
    ax = axes[0]
    ax.plot(x, post, color=EXACT, ls=":", lw=1.1)
    ax.plot(x, kern, color=ATOM, ls="--", lw=1.0, marker="s", ms=4, mfc="white", mew=0.9)
    ax.errorbar(x, meas, yerr=meas_sd, marker="o", ms=3.5, ls="none", capsize=2, elinewidth=0.9,
                color=LEARNED, zorder=4)
    ax.set_xticks(x, [f"{h:g}" for h in hs]); ax.set_xlim(-0.35, len(hs) - 0.45)
    ax.set_xlabel("label bandwidth $h$"); ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$")
    ax.set_ylim(0.3, 1.6)
    hd = [Line2D([], [], color=LEARNED, marker="o", ms=3.5, ls="none"),
          Line2D([], [], color=ATOM, ls="--", lw=1.0, marker="s", ms=4, mfc="white", mew=0.9),
          Line2D([], [], color=EXACT, ls=":", lw=1.1)]
    ax.legend(hd, ["generated (5 seeds)", r"reference $\mathrm{tr}\,\mathrm{Cov}_h$", r"$\mathrm{tr}\,\Sigma_{\rm post}$"],
              loc="lower right", fontsize=6.5, handlelength=1.8, borderaxespad=0.2, labelspacing=0.25)
    title(ax, "a", r"EXP-1 follows $\mathrm{Cov}_h$")

    ax = axes[1]
    ax.axhline(1.0, color=ATOM, ls="--", lw=1.0)
    ax.errorbar(x, ratio, yerr=ratio_sd, marker="o", ms=3.5, ls="none", capsize=2, elinewidth=0.9,
                color=LEARNED)
    for j, (xi, n, r_, sd) in enumerate(zip(x, neff, ratio, ratio_sd)):
        if j == 0:
            ax.text(xi + 0.1, r_ + sd - 0.02, rf"$n_{{\rm eff}}={n:.1f}$", ha="left", va="top", fontsize=6.5,
                    color=GREY)
        else:
            ax.text(xi, r_ + sd + 0.03, f"{n:.1f}", ha="center", va="bottom", fontsize=6.5, color=GREY)
    ax.set_xticks(x, [f"{h:g}" for h in hs]); ax.set_xlim(-0.45, len(hs) - 0.55)
    ax.set_ylim(0.8, 1.88)
    ax.set_xlabel("label bandwidth $h$"); ax.set_ylabel(r"generated / reference")
    title(ax, "b", r"ratio $\approx1$ unless $n_{\rm eff}$ is small")

    ax = axes[2]
    hcol = {4.0: OI["orange"], 6.0: OI["purple"]}
    lo, hi = np.inf, -np.inf
    for h in (4.0, 6.0):
        r = by_h[h]
        ref = np.asarray(r["trace_kernel_per_condition"], float)
        mv = np.asarray(r["ratio_per_condition"], float) * ref
        ok = (ref > 0) & (mv > 0)
        lx, ly = np.log10(ref[ok]), np.log10(mv[ok])
        slope, icpt, se = ols(lx, ly)
        c = hcol[h]
        ax.scatter(lx, ly, s=9, color=c, alpha=0.75, lw=0, zorder=3)
        xx = np.linspace(lx.min(), lx.max(), 2)
        ax.plot(xx, icpt + slope * xx, color=c, lw=1.4, zorder=4)
        lo, hi = min(lo, lx.min(), ly.min()), max(hi, lx.max(), ly.max())
        ax.text(0.97, 0.26 if h == 4.0 else 0.15, rf"$h={h:g}$: slope ${slope:.2f}$", color=c, fontsize=6.8,
                ha="right", va="bottom", transform=ax.transAxes)
    lo, hi = lo - 0.3, hi + 0.3
    ax.plot([lo, hi], [lo, hi], color=ATOM, ls="--", lw=1.0, zorder=2)
    ax.text(0.97, 0.04, "dashed: exact field, slope 1", color=ATOM, fontsize=6.5, ha="right", va="bottom",
            transform=ax.transAxes)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"reference $\log_{10}\mathrm{tr}\,\mathrm{Cov}_h$")
    ax.set_ylabel(r"generated $\log_{10}\mathrm{tr}\,\mathrm{Cov}$")
    title(ax, "c", "CIFAR-10 does not")
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_kernel_tracking.pdf")


# --------------------------------------------------------------------------- EDM: two clocks
def fig_clocks():
    zs = np.load(R / "n3_rho_20261117/sub500/q_per_sample.npz")
    zp = np.load(R / "n3_rho_20261117/public/q_per_sample.npz")
    z2 = np.load(R / "n3_rho2_20261118/sub2000/q_per_sample.npz")
    on, on2 = frac_q(zs) < 1 / 3, frac_q(z2) < 1 / 3
    sg = zs["sigma"]
    XL = (25, 0.0015)

    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 2.1))
    ax = axes[0]
    for path, hdr, c, nm in ((R / "n3_followup_sub500_20261111/SWAP_SUMMARY.md", "## swap_sub500", M500,
                              "500 images"),
                             (R / "n3_followup_20261111/SWAP_SUMMARY.md", "## swap_public", MPUB, "public")):
        s = _swap(path, hdr)
        ax.semilogx(s[:, 0], 100 * s[:, 1], marker="o", ms=3.2, color=c, lw=1.4, mec="white", mew=0.4)
        if c == M500:
            # under the flat part of its line, right of sigma = 1, where no other line runs
            ax.text(0.05, 95.5, nm, color=c, fontsize=6.8, ha="center", va="top")
        else:
            label(ax, s[0, 0], 100 * s[0, 1], nm, c, ha="right", dx=-4, fs=6.8)
    ax.axvline(1, color=GREY, ls=(0, (3, 2)), lw=0.7)
    ax.set_xlim(*XL); ax.set_ylim(20, 104)
    ax.set_xlabel(r"switch to exact field at $\sigma=s$")
    ax.set_ylabel("same image as the\nnetwork's own sample (%)", linespacing=1.0)
    title(ax, "a", "the image is chosen early")

    ax = axes[1]
    series = (((zs["err"] / zs["n1"])[on], ON, "-", True), ((zs["err"] / zs["n1"])[~on], OFF, "-", True),
              ((z2["err"] / z2["n1"])[on2], ON, "--", False), ((z2["err"] / z2["n1"])[~on2], OFF, "--", False),
              (zp["err"] / zp["n1"], MPUB, "-", True))
    for v, c, ls, fill in series:
        q = np.nanpercentile(v, [25, 50, 75], axis=0)
        ax.semilogx(sg, q[1], color=c, lw=1.3, ls=ls)
        if fill:
            ax.fill_between(sg, q[0], q[2], color=c, alpha=0.13, lw=0)
    ax.axhline(1, color=GREY, ls=(0, (3, 2)), lw=0.7)
    ax.axvline(1, color=GREY, ls=(0, (3, 2)), lw=0.7)
    ax.set_xlim(*XL); ax.set_ylim(0, 1.08)
    ax.set_xlabel(r"noise level $\sigma$"); ax.set_ylabel(r"relative error $\varrho$ (median)")
    hs = [Line2D([], [], color=ON, lw=1.3), Line2D([], [], color=OFF, lw=1.3), Line2D([], [], color=MPUB, lw=1.3),
          Line2D([], [], color=GREY, lw=1.1), Line2D([], [], color=GREY, lw=1.1, ls="--")]
    leg = ax.legend(hs[:3], ["on-atom", "off-atom", "public"], loc="upper left", bbox_to_anchor=(0.0, 0.93),
                    fontsize=6.3, handlelength=1.5, borderaxespad=0.2, labelspacing=0.22)
    ax.add_artist(leg)
    ax.legend(hs[3:], ["500 images", "2000 images"], loc="lower right", fontsize=6.3, handlelength=1.7,
              borderaxespad=0.2, labelspacing=0.22)
    title(ax, "b", "landing is decided late")

    ax = axes[2]
    sg2 = z2["sigma"]
    rho2 = z2["err"] / z2["n1"]
    inc = (1 - 0.5 * (rho2[:, :-1] + rho2[:, 1:])) * np.log(sg2[:-1] / sg2[1:])
    cum = [auc(-inc[~on2, 11:k].sum(1), -inc[on2, 11:k].sum(1)) for k in range(12, len(sg2))]
    for key, lab, c, ls in (("dD", r"distance of $D_\theta$ to data", GREY, "--"),
                            ("rhoA", r"relative error $\varrho$", OI["sky"], "-"),
                            ("radA", "radial ratio", OI["green"], "-")):
        a = [auc(z2[key][~on2, i], z2[key][on2, i]) for i in range(len(sg2))]
        ax.semilogx(sg2, a, color=c, lw=1.3, ls=ls, label=lab)
    ax.semilogx(sg2[12:], cum, color=OI["purple"], lw=2.0, label=r"late contraction $\int(1-\varrho)$")
    ax.axvline(1, color=GREY, ls=(0, (3, 2)), lw=0.7)
    ax.set_xlim(*XL); ax.set_ylim(0.45, 1.03)
    ax.set_xlabel(r"noise level $\sigma$"); ax.set_ylabel("AUC, off- vs on-atom")
    ax.legend(loc="lower right", fontsize=6.3, handlelength=1.6, borderaxespad=0.2, labelspacing=0.3)
    title(ax, "c", "detecting off-atom samples")
    fig.tight_layout(w_pad=0.9)
    save(fig, "fig_edm_clocks.pdf")


# --------------------------------------------------------------------------- Heun
def fig_heun():
    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 2.05))
    r = np.linspace(0.2, 0.95, 400)
    kap, th = (1 - r) * (2 * r - 1) / (2 * r), (1 - r) / (2 * r)
    ax = axes[0]
    ax.axvspan(0.2, 0.5, color=LEARNED, alpha=0.07, lw=0)
    ax.axhline(0, color="k", lw=0.5)
    for y, c, lab in ((r, GREY, r"$r$ on $x_k$"), (kap, LEARNED, r"$\kappa$ on $D_k$"),
                      (th, EXACT, r"$\theta$ on $\tilde D_k$")):
        ax.plot(r, y, color=c, lw=1.4)
    label(ax, 0.95, 0.95, r"$r$ on $x_k$", GREY, ha="right", dx=0, dy=6, va="bottom", fs=6.8)
    label(ax, 0.62, ((1 - 0.62) * (2 * 0.62 - 1) / 1.24), r"$\kappa$ on $D_k$", LEARNED, dx=0, dy=-4,
          va="top", fs=6.8)
    label(ax, 0.29, (1 - 0.29) / 0.58, r"$\theta$ on $\tilde D_k$", EXACT, dx=4, dy=2, fs=6.8)
    ax.text(0.35, -0.75, "extrapolates\n" + r"($\kappa<0$)", ha="center", va="center", fontsize=6.8,
            color=LEARNED, linespacing=1.0)
    ax.set_xlim(0.2, 0.95); ax.set_ylim(-1.0, 2.1)
    ax.set_xlabel(r"step ratio $r=\sigma_{k+1}/\sigma_k$"); ax.set_ylabel("weight in a Heun step")
    title(ax, "a", "short steps extrapolate")

    ax = axes[1]
    ax.fill_between(r, 0, _rhocrit(r), color=GOOD, alpha=0.12, lw=0)
    ax.plot(r, _rhocrit(r), color=ATOM, lw=1.2)
    ax.text(0.47, 0.5, "$c_k<1$:\ncontracts", fontsize=6.8, color=GOOD, ha="center", linespacing=1.0)
    ax.text(0.215, 0.62, r"$c_k\geq1$", fontsize=6.8, color=ATOM, ha="left")
    for S, c in STEPS.items():
        z = np.load(R / f"n3_steps_20261117/s{S}/sub500/q_per_sample.npz")
        on = frac_q(z) < 1 / 3
        rk = z["sigma"][1:] / z["sigma"][:-1]
        rt = np.median((z["errt"][:, :-1] / z["nt1"][:, :-1])[on], axis=0)
        ax.plot(rk, rt, color=c, lw=0.6, alpha=0.6)
        ax.scatter(rk, rt, s=9, color=c, zorder=3, edgecolors="white", linewidths=0.3)
        j = int(np.argmax(rt))                      # label each schedule above its first, highest point
        y_lab = 1.10 if S == max(STEPS) else 1.035  # stagger the last label so neighbours never touch
        ax.text(rk[j] + 0.005, y_lab, f"{S} steps", color=c, fontsize=6.8, ha="left", va="bottom")
    ax.set_xlim(0.2, 0.95); ax.set_ylim(0, 1.16)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel(r"step ratio $r_k$"); ax.set_ylabel(r"$\varrho$ at the predictor (median)")
    title(ax, "b", r"threshold $\varrho_{\rm crit}(r)$")

    ax = axes[2]
    ends = {}
    for S, c in STEPS.items():
        z = np.load(R / f"n3_steps_20261117/s{S}/sub500/q_per_sample.npz")
        on = frac_q(z) < 1 / 3; sg = z["sigma"]; rk = sg[1:] / sg[:-1]
        rho = np.maximum(z["err"][:, :-1] / z["n1"][:, :-1], z["errt"][:, :-1] / z["nt1"][:, :-1])
        ka, th_ = np.abs((1 - rk) * (2 * rk - 1) / (2 * rk)), (1 - rk) / (2 * rk)
        ck = rk + ka * rho + th_ * rho * (rk + (1 - rk) * rho)
        v = 100 * (ck[on] < 1).mean(0)
        ax.semilogx(sg[:-1], v, color=c, lw=1.3, marker="o" if S == 18 else None, ms=2.2, mec="white", mew=0.3,
                    ls="-" if S == 18 else ("--" if S == 36 else ":"))
        ends[S] = (sg[:-1], v)
    s18, v18 = ends[18]
    ax.text(0.5, 106, "36 and 64 steps", color=STEPS[36], fontsize=6.8, ha="center", va="bottom")
    k = int(np.argmin(v18 > 50))
    label(ax, s18[k], v18[k], "18 steps", STEPS[18], dx=-5, ha="right", fs=6.8)
    ax.set_xlim(100, 0.0015); ax.set_ylim(-4, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel(r"noise level $\sigma_k$"); ax.set_ylabel(r"on-atom samples with $c_k<1$ (%)")
    title(ax, "c", "more steps certify every step")
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_heun.pdf")


# --------------------------------------------------------------------------- appendix: image grids
def fig_image_training():
    iters = (500, 2000, 8000, 20000, 40000, 60000)
    run = "exp3_cifar_ddpm_h0"
    sheets = {it: cells(EXP3 / run / "figures" / f"grid_it{it}.png") for it in iters}
    met = read_csv(EXP3 / run / "raw" / "metrics.csv")
    tr = dict(zip(met["iter"].astype(int), met["trace_cov_mean"]))
    conds, comp = (0, 2), (1, 2, 3, 4, 5, 6)
    s, g, gb = 0.38, 0.025, 0.2
    W = FULL_W
    nb = 1 + len(comp) + 1
    bw = nb * s + (nb - 1) * g + 0.06 + 0.06
    x0 = W - 2 * bw - gb
    H = len(iters) * (s + g) + 0.42
    fig = plt.figure(figsize=(W, H))
    for b, cond in enumerate(conds):
        bx = x0 + b * (bw + gb)
        xs = [bx] + [bx + s + 0.06 + j * (s + g) for j in range(len(comp))]
        xs.append(xs[-1] + s + 0.06)
        top = (len(iters) - 1) * (s + g) + 0.02
        fig.text((xs[0] + s / 2) / W, (top + s + 0.04) / H, "observed", ha="center", va="bottom", fontsize=6.8)
        fig.text((xs[1] + xs[len(comp)] + s) / 2 / W, (top + s + 0.04) / H, "six completions",
                 ha="center", va="bottom", fontsize=6.8)
        fig.text((xs[-1] + s / 2) / W, (top + s + 0.04) / H, "training\nimage", ha="center", va="bottom",
                 fontsize=6.8, linespacing=0.9)
        for r, it in enumerate(iters):
            y = top - r * (s + g)
            row = sheets[it][cond]
            imgs = [row[0]] + [row[c] for c in comp] + [row[7]]
            for j, (xx, im) in enumerate(zip(xs, imgs)):
                fr = LIGHT if j == 0 else (ATOM if j == len(imgs) - 1 else LEARNED)
                tile(axes_in(fig, xx, y, s, s), im, fr, 0.7)
            if b == 0:
                fig.text((bx - 0.06) / W, (y + s / 2) / H, f"{it:,}".replace(",", r"$\,$") + "\n"
                         + rf"$\mathrm{{tr}}={tr[it]:.3g}$", ha="right", va="center", fontsize=6.5,
                         linespacing=1.0)
        if b == 0:
            fig.text((bx - 0.06) / W, (top + s + 0.04) / H, "iteration", ha="right", va="bottom", fontsize=6.8)
    save(fig, "fig_image_training.pdf", dpi=300)


def fig_image_class():
    runs = {0.0: "exp3_cifar_class_h0", 0.4: "exp3_cifar_class_h0p4"}
    met = {h: read_csv(EXP3 / r / "raw" / "metrics.csv") for h, r in runs.items()}
    for m in met.values():
        o = np.argsort(m["iter"])
        for k in m:
            m[k] = m[k][o]
    pop = float(met[0.0]["trace_cov_kernel_mean"][0])
    conds, comp = (0, 1, 2, 3), (1, 2, 3, 4, 5, 6)
    W = FULL_W
    s, g = 0.33, 0.022
    H = 2 * len(conds) * (s + g) + 0.6
    fig = plt.figure(figsize=(W, H))
    # (a) trace against iteration
    hcol = {0.0: LEARNED, 0.4: OI["orange"]}
    ax = axes_in(fig, 0.45, H - 1.95, 1.75, 1.55)
    ax.axhline(pop, color=ATOM, ls="--", lw=1.0)
    ax.text(600, pop * 1.03, f"within-class scatter {pop:.0f}", fontsize=6.5, color=ATOM, va="bottom")
    for h, m in met.items():
        ax.plot(m["iter"], m["trace_cov_mean"], color=hcol[h], marker="o", ms=3.2, lw=1.3, mec="white",
                mew=0.4)
        label(ax, m["iter"][-1], m["trace_cov_mean"][-1], f"$h={h:g}$", hcol[h], dx=4,
              dy=6 if h == 0.4 else -6, fs=6.8)
    ax.set_xscale("log"); ax.set_ylim(0, 1100)
    ax.set_xlabel("training iteration"); ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$ of completions")
    title(ax, "a", "variance stays high")
    # (b, c) grids at 60000
    x0 = 2.95
    xs = [x0] + [x0 + s + 0.05 + j * (s + g) for j in range(len(comp))]
    xs.append(xs[-1] + s + 0.05)
    ytop = H - 0.32 - s
    for b, (h, run) in enumerate(runs.items()):
        sheet = cells(EXP3 / run / "figures" / "grid_it60000.png")
        for r, cond in enumerate(conds):
            y = ytop - (b * len(conds) + r) * (s + g) - b * 0.1
            row = sheet[cond]
            imgs = [row[0]] + [row[c] for c in comp] + [row[7]]
            for j, (xx, im) in enumerate(zip(xs, imgs)):
                fr = LIGHT if j == 0 else (ATOM if j == len(imgs) - 1 else hcol[h])
                tile(axes_in(fig, xx, y, s, s), im, fr, 0.7)
            if r == 0:
                fig.text((x0 - 0.1) / W, (y + s - 0.02) / H, f"({'bc'[b]})", fontweight="bold", ha="right", va="top",
                         fontsize=8.5)
                fig.text((x0 - 0.1) / W, (y + s / 2 - (len(conds) - 1) * (s + g) / 2 - 0.05) / H, f"$h={h:g}$",
                         ha="right", va="center", fontsize=7.5, color=hcol[h], rotation=90)
    yh = ytop + s + 0.04
    fig.text((xs[0] + s / 2) / W, yh / H, "observed", ha="center", va="bottom", fontsize=6.8)
    fig.text((xs[1] + xs[len(comp)] + s) / 2 / W, yh / H, "six completions at iteration 60$\\,$000",
             ha="center", va="bottom", fontsize=6.8)
    fig.text((xs[-1] + s / 2) / W, yh / H, "true\nimage", ha="center", va="bottom", fontsize=6.8,
             linespacing=0.9)
    save(fig, "fig_image_class.pdf", dpi=300)


ALL = {"intuition": fig_intuition, "unrolled": fig_unrolled_learned, "landscape": fig_landscape,
       "exp1": fig_exp1, "cifar": fig_cifar, "kernel": fig_kernel, "clocks": fig_clocks, "heun": fig_heun,
       "image_training": fig_image_training, "image_class": fig_image_class}

if __name__ == "__main__":
    use_paper_style()
    for name in (sys.argv[1:] or ALL):
        ALL[name]()
