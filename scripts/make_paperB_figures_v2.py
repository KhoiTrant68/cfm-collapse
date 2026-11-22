"""Figures of paper B (paper_mechanism/), second design, drawn at their printed widths.

    PYTHONPATH=.:scripts python scripts/make_paperB_figures_v2.py [teaser mechanism landing collapse details]
    (FIGOUT=<dir> writes elsewhere than paper_mechanism/figures, for previews.)

Writes into paper_mechanism/figures (names as in paper_mechanism/main.tex):

  fig_teaser.pdf       Figure 1 (fig:intuition), "one latent, two clocks". One Gaussian latent sampled by the public
                       EDM model (never copies) and by a model trained on 500 images (copies). For each model, the
                       network's guess D_theta(x_k) and the exact field's guess m*(x_k) (the class posterior mean
                       over the training images, at the network's own state x_k) at the levels sigma_7..sigma_17
                       of the 18-step Heun schedule, then the output and its nearest training image. Below, on the
                       same column axis, the two clocks measured by the denoiser swaps at level s (500 latents,
                       public model thick, 500-image model thin): the choice, the share of net->exact endpoints on
                       the nearest training image of the network's own endpoint (=L; which image is reached, not
                       landing, since net->exact always ends on a training image), and landing, the share of
                       exact->net endpoints on a training image (1 - off). Dotted lines: where the public model's
                       curves pass 1/2, interpolated in log s (s = 2.48 and 0.51, swap_clocks.json s_sel50, s_land).
  fig_mechanism.pdf    Figure 2 (fig:mechanism; replaces fig_unrolled_learned.pdf and fig_landscape.pdf): 1-D flows
                       over the exact density p_t of four training points, for the exact field and two learned
                       fields x1hat = m* + rho_t (z - m*); the rho_t profiles; the distance to the training point.
  fig_collapse.pdf     Figure 3 (fig:collapse; replaces fig_exp1_collapse, fig_cifar_collapse, fig_kernel_tracking):
                       EXP-1 variance through training, CIFAR-10 completions through training, and generated against
                       reference variance under label smoothing (CIFAR-10 at h = 4 from three retrained instances;
                       h = 6 drawn without a slope, which does not replicate across instances).
  fig_landing.pdf      Figure 5 (fig:landing; replaces fig_edm_clocks.pdf): rho along EDM trajectories by outcome
                       and model; the late contraction per sample; AUCs at sigma >= 0.585 only (below, the
                       nearest-neighbour baseline is bookkeeping: D_theta at sigma = 0.002 is the sample).
  fig_collapse_details.pdf  Appendix (fig:collapse-details): the EXP-1 and CIFAR-10 panels moved out of the main text.
The appendix figures fig_heun, fig_image_training and fig_image_class are still drawn by make_paperB_figures.py, and
fig_swap by make_swap_figure.py.

Data (every number and image drawn is read from these files, or computed here as stated):
  results/n3_strips_20261118/{public,sub500}.npz   x, D, m, end, y1, y2, rho, d1, d2, sigma (scripts/n3_image_strips.py;
      same seed and classes for both models, so latent i is the same Gaussian draw in both files).
  results/n3_followup_20261111/swap_summary.json, results/n3_followup_sub500_20261111/swap_summary.json
      =L of net->exact and the off-atom share of exact->net, public and 500-image models.
  results/n3_rho_20261117/{sub500,public}/q_per_sample.npz, results/n3_rho2_20261118/sub2000/q_per_sample.npz
      err = |D - m*|, n1 = |x - y1|, d1, d2, dD (distance of D to its nearest training image), rhoA, radA (relative
      error and radial ratio anchored at the nearest training image of D), sigma.
  results/exp1/exp1_{cond,ext_sched,uncond}_seed*/raw/metrics.csv, results/exp1/_theory/raw/p7_kernel.csv,
  results/exp3/exp3_cifar_ddpm_h0*/{raw/metrics.csv,figures/grid_it*.png},
  results/exp3/_rerun/reeval_exp3_cifar_heff_h{4,6}_s{0,1,2}/reeval.json (per-condition reference and ratio).
Computed here: rho = err / n1; the late contraction C = int_{0.002}^{0.585} (1 - rho) dlog(1/sigma) by the
trapezoidal rule on the sampler's levels (as in the paper); AUCs with the rank formula of
scripts/n3_edm_memorization.auc; OLS slopes of log10 generated on log10 reference variance; the toy flows of
Figure 2 by RK4 from the closed-form fields; whether an image tile "is" the output's nearest training image y1,
by the off-atom criterion applied to the tile v: |v - y1| < |v - y2| / 3, with y2 the output's second-nearest
training image.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from scripts.figstyle import COLORS, FULL_W, OI, use_paper_style
from scripts.make_edm_figures import _img, auc
from scripts.make_paperB_figures import axes_in, blank, figtitle, frac_q, tile, title

R = Path("results")
OUT = Path(os.environ.get("FIGOUT", "paper_mechanism/figures"))


def save(fig, name: str, pad: float = 0.015, **kw) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=pad, **kw)
    plt.close(fig)
    print(f"  wrote {OUT / name}")


EXACT, LEARNED, ATOM = COLORS["exact"], COLORS["learned"], COLORS["atom"]
GREY = "#6E6E6E"
LIGHT = "#BDBDBD"
FAINT = "#E9E9E9"
COPY = "#222222"          # outcome "copies a training image" (on-atom): near-black
NEW = OI["vermillion"]    # outcome "new image" (off-atom)


# --------------------------------------------------------------------------- helpers
def rho_of(z):
    return z["err"] / z["n1"]


def late_contraction(z, k0: int = 11):
    """C = int (1 - rho) dlog(1/sigma) from sigma_k0 (= 0.585 on the 18-step schedule) to sigma_17 = 0.002."""
    rho, sg = rho_of(z), z["sigma"]
    inc = (1 - 0.5 * (rho[:, :-1] + rho[:, 1:])) * np.log(sg[:-1] / sg[1:])
    return inc[:, k0:].sum(1)


def swap_levels(path: Path, run: str):
    rows = {r["run"]: r for r in json.loads(path.read_text(encoding="utf-8"))}[run]["levels"]
    s = np.array([r["sigma"] for r in rows])
    choice = np.array([r["net2exact"]["nn_eq_learned"] for r in rows])
    land = np.array([1 - r["exact2net"]["off"] for r in rows])
    return s, choice, land


def on_image(v, y1, y2) -> bool:
    """The tile v counts as the training image y1 by the paper's off-atom criterion applied to v."""
    return float(np.linalg.norm(v - y1)) < float(np.linalg.norm(v - y2)) / 3


def framed(ax, img, color, lw=1.0):
    tile(ax, img, color, lw)


# --------------------------------------------------------------------------- Figure 1
def fig_teaser(i: int = 7, k0: int = 7):
    """One latent, two clocks.

    Tiles: rows D_theta(x_k) and m*(x_k) of results/n3_strips_20261118/{public,sub500}.npz for latent i at the
    levels k0..17 of the 18-step schedule, then the output and its nearest training image y1. Frames: vermillion
    (network) or blue (exact field), black where the tile is y1 by on_image(). Plot: the two clocks of the
    denoiser swaps (swap_summary.json; 500 latents per model; public model thick, 500-image model thin), drawn at
    the swap level s on the same log-sigma scale as the columns (linear interpolation of log sigma between
    neighbouring levels). Choice (vermillion): share of net->exact endpoints (network for sigma > s, exact field
    below) whose nearest training image is that of the network's own endpoint (=L). Landing (blue): share of
    exact->net endpoints (exact field for sigma > s, network below) on a training image (1 - off). Each clock is
    the level at which the public model's curve passes 1/2, interpolated in log s between swap levels, as in
    results/paperB_20261121/swap/swap_clocks.json (s_sel50 = 2.48, s_land = 0.51)."""
    zp = np.load(R / "n3_strips_20261118/public.npz")
    zs = np.load(R / "n3_strips_20261118/sub500.npz")
    sg = zp["sigma"]
    assert np.allclose(sg, zs["sigma"])
    ks = list(range(k0, len(sg)))                      # columns: the sampler's levels sigma_k0 ... 0.002
    nc = len(ks)

    W, H = FULL_W, 3.2
    fig = plt.figure(figsize=(W, H))
    s, g = 0.36, 0.03                                   # tile and gap (inches)
    x0 = 0.86                                           # left edge of the first column
    xs = [x0 + j * (s + g) for j in range(nc)]
    xe = xs[-1] + s + 0.16                              # the last column: sigma -> 0
    cx = [x + s / 2 for x in xs]
    ytop = H - 0.19 - s                                 # rows, top to bottom: public D, m*; 500-image D, m*
    pair_gap = 0.17
    yrows = [ytop, ytop - (s + g), ytop - 2 * (s + g) - pair_gap, ytop - 3 * (s + g) - pair_gap]

    yh = ytop + s + 0.035                               # column heads: the noise level of each column
    for j, k in enumerate(ks):
        fig.text(cx[j] / W, yh / H, f"{sg[k]:.2g}", ha="center", va="bottom", fontsize=6.6)
    fig.text((x0 - 0.07) / W, yh / H, r"$\sigma$", ha="right", va="bottom", fontsize=7.5)
    fig.text((xe + s / 2) / W, yh / H, "final", ha="center", va="bottom", fontsize=6.8)

    models = ((zp, "public model", yrows[0], yrows[1]), (zs, "500 images", yrows[2], yrows[3]))
    for z, nm, yD, ym in models:
        y1 = z["y1"][i].astype(np.float32); y2 = z["y2"][i].astype(np.float32)
        for j, k in enumerate(ks):
            D = z["D"][i, k].astype(np.float32); m = z["m"][i, k].astype(np.float32)
            framed(axes_in(fig, xs[j], yD, s, s), _img(D), ATOM if on_image(D, y1, y2) else LEARNED)
            framed(axes_in(fig, xs[j], ym, s, s), _img(m), ATOM if on_image(m, y1, y2) else EXACT)
        end = z["end"][i].astype(np.float32)
        framed(axes_in(fig, xe, yD, s, s), _img(end), ATOM if on_image(end, y1, y2) else LEARNED, 1.3)
        framed(axes_in(fig, xe, ym, s, s), _img(y1), ATOM, 1.3)
        fig.text((x0 - 0.06) / W, (yD + s / 2) / H, "network\n" + r"$D_\theta(x)$", ha="right", va="center",
                 fontsize=6.6, color=LEARNED, linespacing=0.95)
        fig.text((x0 - 0.06) / W, (ym + s / 2) / H, "exact field\n" + r"$m^\star(x)$", ha="right", va="center",
                 fontsize=6.6, color=EXACT, linespacing=0.95)
        fig.text(0.05 / W, (ym + s + g / 2) / H, nm, ha="center", va="center", fontsize=7.2,
                 fontweight="bold", rotation=90)
        q = float(z["d1"][i] / z["d2"][i])
        verdict = (rf"copy  $d_1/d_2={q:.2f}$" if q < 1 / 3 else rf"new image  $d_1/d_2={q:.2f}$")
        fig.text((xe + s) / W, (ym - 0.03) / H, verdict, ha="right", va="top", fontsize=6.4,
                 color=COPY if q < 1 / 3 else NEW)

    # ---- the two clocks of the swaps, on the same column axis
    yp = 0.33
    ph = yrows[3] - 0.17 - yp
    ax = axes_in(fig, x0, yp, xs[-1] + s - x0, ph)
    half = (s / 2) / (s + g)
    ax.set_xlim(-half, nc - 1 + half)
    lsg = np.log(sg[ks])

    def col(sig):                                        # sigma -> fractional column (log-linear between levels)
        return np.interp(-np.log(sig), -lsg, np.arange(nc))

    def half_level(lv, p):                               # swap level at which p first reaches 1/2, log-s interp.
        j = int(np.flatnonzero(p >= 0.5)[0])
        f = (0.5 - p[j - 1]) / (p[j] - p[j - 1])
        return float(np.exp(np.log(lv[j - 1]) + f * (np.log(lv[j]) - np.log(lv[j - 1]))))

    s_pub, ch_pub, land_pub = swap_levels(R / "n3_followup_20261111/swap_summary.json", "swap_public")
    s_mem, ch_mem, land_mem = swap_levels(R / "n3_followup_sub500_20261111/swap_summary.json", "swap_sub500")
    assert np.allclose(s_pub, s_mem)
    s_choice, s_land = half_level(s_pub, ch_pub), half_level(s_pub, land_pub)
    # the same clocks as swap_clocks.json (s_sel50 = 2.483, s_land = 0.506), quoted in the caption
    assert abs(s_choice - 2.483) < 0.005 and abs(s_land - 0.506) < 0.005, (s_choice, s_land)
    for v, c in ((ch_mem, LEARNED), (land_mem, EXACT)):            # thin: the 500-image model
        ax.plot(col(s_mem), v, color=c, lw=0.9, alpha=0.8, zorder=2)
    for v, c, mk in ((ch_pub, LEARNED, "o"), (land_pub, EXACT, "s")):   # thick: the public model
        ax.plot(col(s_pub), v, color=c, lw=1.6, marker=mk, ms=2.6, mec="white", mew=0.4, zorder=3)
    ax.set_ylim(0, 1.32)
    ax.set_yticks([0, 0.5, 1])
    ax.spines["left"].set_bounds(0, 1)
    ax.set_ylabel("share of samples", fontsize=6.6, labelpad=2)
    ax.set_xticks(np.arange(nc), [f"{sg[k]:.2g}" for k in ks])
    ax.tick_params(axis="x", labelsize=6.6)
    ax.tick_params(axis="y", labelsize=6.6)
    ax.set_xlabel(r"noise level $\sigma$ (one column per sampler step; a swap at level $s$ is drawn at $\sigma=s$)",
                  fontsize=7, labelpad=1.5)
    ax.grid(False)
    # direct labels
    ax.text(col(5.0) + 0.42, 0.50, "choice", color=LEARNED, fontsize=6.8, ha="left", va="bottom")
    ax.text(col(0.5) + 0.62, 0.42, "landing", color=EXACT, fontsize=6.8, ha="left", va="center")
    ax.text(col(5.0) + 0.05, 0.89, "500 images", color=GREY, fontsize=6.3, ha="left", va="top")
    # the two clocks: where the public model's curves pass one half
    for jj, txt in ((float(col(s_choice)), "half chosen"), (float(col(s_land)), "half landed")):
        ax.plot([jj, jj], [0, 1.16], color=GREY, lw=0.6, ls=":", zorder=1)
        ax.text(jj, 1.17, txt, ha="center", va="bottom", fontsize=6.8, fontweight="bold")
    save(fig, "fig_teaser.pdf", dpi=300)


# --------------------------------------------------------------------------- Figure 2 (toy mechanism)
AT4 = np.array([-2.1, -0.7, 0.7, 2.1])
P4 = np.array([0.12, 0.48, 0.28, 0.12])


def _toy_fields():
    """The three 1-D fields of the mechanism figure (those of make_paperB_figures.fig_unrolled_learned): the exact
    field (rho = 0) and learned fields x1hat = m* + rho_t (z - m*) with rho_t = 0.6 and 1 - rho_t = 0.6 (1-t)^(1/2).
    dz/dtau = F(z, t) in log time tau = -log(1 - t)."""
    from scripts.make_edm_figures import _m1d
    return [
        ("exact", lambda t: 0.0 * t, lambda z, t: _m1d(z, t, AT4, P4) - z),
        ("rho06", lambda t: 0.6 + 0.0 * t, lambda z, t: 0.4 * (_m1d(z, t, AT4, P4) - z)),
        ("late", lambda t: 1 - 0.6 * np.sqrt(1 - t), lambda z, t: 0.6 * np.sqrt(1 - t) * (_m1d(z, t, AT4, P4) - z)),
    ]


def fig_mechanism():
    """(a-c) 1-D flows from 1500 sources over the exact density p_t (grey, normalised per time), with the output law
    at the bottom; (d) the relative error rho_t of the three fields; (e) the median distance (IQR shaded) of the
    trajectories to the training point their endpoint is nearest to. RK4 in log time (make_edm_figures._run1d)."""
    from matplotlib.colors import LinearSegmentedColormap
    from scripts.make_edm_figures import _run1d
    rng = np.random.default_rng(0)
    z0 = np.sort(rng.normal(size=1500))
    fields = _toy_fields()
    runs = {k: _run1d(F, z0) for k, _, F in fields}

    W, H = FULL_W, 2.42
    fig = plt.figure(figsize=(W, H))
    cw, gap, xl = 1.3, 0.1, 0.16                      # unrolled column width, gap, left margin (inches)
    ytop_h, ymid_h, ybot_h = 0.24, 1.22, 0.36         # heights of the source, path and output rows
    ybot = 0.2
    ymid = ybot + ybot_h
    ytp = ymid + ymid_h
    xs = np.linspace(-3.4, 3.4, 600)
    # exact density p_t(x), normalised per row so that every tube keeps its contrast
    tg = np.linspace(0.0, 0.997, 420)
    sd = (1 - tg)[:, None]
    dens = (P4[None, None, :] * np.exp(-(xs[None, :, None] - tg[:, None, None] * AT4[None, None, :]) ** 2
                                        / (2 * sd[..., None] ** 2)) / sd[..., None]).sum(-1)
    dens /= dens.max(1, keepdims=True)
    cmap = LinearSegmentedColormap.from_list("bg", ["#FFFFFF", "#C4C4C4"])
    heads = {"exact": (r"exact field, $\varrho=0$", "copies", EXACT),
             "rho06": (r"learned, $\varrho_t=0.6$", "still copies", LEARNED),
             "late": (r"learned, $\varrho_t\to1$ late", "new samples", LEARNED)}
    for c, (key, _, _) in enumerate(fields):
        ts, P = runs[key]
        end = P[-1]
        x = xl + c * (cw + gap)
        col = heads[key][2]
        top = axes_in(fig, x, ytp, cw, ytop_h); mid = axes_in(fig, x, ymid, cw, ymid_h)
        bot = axes_in(fig, x, ybot, cw, ybot_h)
        top.fill_between(xs, 0, np.exp(-xs ** 2 / 2), color=LIGHT, alpha=0.7, lw=0)
        mid.imshow(dens ** 0.6, extent=(xs[0], xs[-1], tg[-1], tg[0]), aspect="auto", cmap=cmap,
                   interpolation="bilinear", rasterized=True, zorder=0)
        for j in np.linspace(15, len(z0) - 16, 64).astype(int):     # 64 of the 1500, the extreme tails left out
            mid.plot(P[:, j], ts, color=col, lw=0.45, alpha=0.7, zorder=2)
        if key == "late":                            # new samples: a smooth density
            kde = np.exp(-(xs[:, None] - end[None]) ** 2 / (2 * 0.06 ** 2)).sum(1)
            bot.fill_between(xs, 0, -0.78 * kde / kde.max(), color=col, alpha=0.85, lw=0)
        else:                                        # copies: point masses, stems of height = mass
            for a_ in AT4:
                m = float(np.mean(np.abs(end - a_) < 0.1))
                if m > 0.005:
                    bot.plot([a_, a_], [0, -m], color=col, lw=2.0, solid_capstyle="butt")
                    bot.scatter([a_], [-m], s=8, color=col, zorder=4, lw=0)
        bot.scatter(AT4, np.zeros_like(AT4), marker="|", s=34, color=ATOM, zorder=3, lw=1.0)
        for a in (top, mid, bot):
            blank(a); a.set_xlim(xs[0], xs[-1])
        mid.set_ylim(1.0, 0.0); bot.set_ylim(-1.0, 0.12); top.set_ylim(0, 1.15)
        title(top, "abc"[c], heads[key][0], fs=7.8, pad=1)
        bot.text(0.5, -0.06, heads[key][1], transform=bot.transAxes, ha="center", va="top", fontsize=7,
                 color=col)
        if c == 0:
            mid.annotate("", xy=(-3.25, 0.93), xytext=(-3.25, 0.07),
                         arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.7))
            mid.text(-3.08, 0.5, r"$t$", fontsize=8, color=GREY, va="center")
            top.text(-3.4, 0.98, "noise", fontsize=6.4, color=GREY, va="top")
            bot.text(-3.4, -0.32, "output", fontsize=6.4, color=GREY, va="top")

    # (d) relative error, (e) distance to the training point reached, against 1 - t on a log axis
    xr0 = xl + 3 * cw + 2 * gap + 0.55
    wr = W - xr0 - 0.2
    hd = 0.86
    ax_d = axes_in(fig, xr0, ytp + ytop_h - hd, wr, hd)
    ax_e = axes_in(fig, xr0, ybot + 0.12, wr, ytp + ytop_h - hd - 0.42 - ybot - 0.12)
    eps = np.geomspace(1.0, 6e-6, 400)
    styles = {"exact": (EXACT, "-"), "rho06": (LEARNED, (0, (4, 2))), "late": (LEARNED, "-")}
    for key, rho_t, _ in fields:
        c, ls = styles[key]
        ax_d.plot(eps, rho_t(1 - eps), color=c, ls=ls, lw=1.3)
        ts, P = runs[key]
        end = P[-1]
        a_end = AT4[np.abs(end[:, None] - AT4[None]).argmin(1)]
        n = np.abs(P - a_end[None])
        q = np.percentile(n, [25, 50, 75], axis=1)
        e_ = 1 - ts
        keep = e_ > 6e-6
        ax_e.fill_between(e_[keep], q[0][keep], q[2][keep], color=c, alpha=0.12, lw=0)
        ax_e.plot(e_[keep], q[1][keep], color=c, ls=ls, lw=1.3)
    late = fields[2][1]
    ax_d.fill_between(eps, late(1 - eps), 1, color=LEARNED, alpha=0.12, lw=0)
    ax_d.axhline(1, color=GREY, lw=0.6, ls=":")
    for a in (ax_d, ax_e):
        a.set_xscale("log"); a.set_xlim(1.0, 6e-6)
        a.tick_params(labelsize=6.5)
    ax_d.set_ylim(-0.04, 1.08); ax_d.set_yticks([0, 0.5, 1])
    ax_d.set_xticklabels([])
    ax_d.set_ylabel(r"relative error $\varrho_t$", fontsize=7)
    ax_e.set_yscale("log"); ax_e.set_ylim(3e-6, 6)
    ax_e.set_yticks([1e-5, 1e-3, 1e-1])
    ax_e.set_ylabel("distance to the\ntraining point", fontsize=7, linespacing=0.95)
    ax_e.set_xlabel(r"time left $1-t$", fontsize=7, labelpad=1)
    for a in (ax_d, ax_e):
        a.grid(False)
    title(ax_d, "d", r"relative error", fs=7.8, pad=2)
    title(ax_e, "e", "distance left", fs=7.8, pad=2)
    ax_d.text(3e-3, 0.86, r"$1-\varrho_t\to0$", color=LEARNED, fontsize=6.5, ha="center", va="top")
    ax_d.text(1.2e-5, 0.56, r"$\varrho_t=0.6$", color=LEARNED, fontsize=6.5, ha="right", va="top")
    ax_d.text(1.2e-5, 0.05, r"exact, $\varrho_t=0$", color=EXACT, fontsize=6.5, ha="right", va="bottom")
    # which curve is which panel, at the right end of (e)
    for key, tag in (("exact", "a"), ("rho06", "b"), ("late", "c")):
        ts, P = runs[key]
        end = P[-1]
        a_end = AT4[np.abs(end[:, None] - AT4[None]).argmin(1)]
        e_ = 1 - ts
        j = int(np.searchsorted(-e_, -1.2e-5))
        v = float(np.median(np.abs(P[j] - a_end)))
        ax_e.annotate(f"({tag})", (e_[j], v), xytext=(2, 0), textcoords="offset points", fontsize=6.3,
                      color=styles[key][0], ha="left", va="center", annotation_clip=False)
    save(fig, "fig_mechanism.pdf", dpi=300)


# --------------------------------------------------------------------------- Figure 5 (landing in EDM models)
def fig_landing():
    """(a) Median relative error rho = err / n1 (IQR shaded for the 500-image model) of on-atom and off-atom
    samples, 500-image model (n3_rho sub500) and 2000-image model (n3_rho2 sub2000), and of the public model
    (n3_rho public). (b) Per sample, the late contraction C = int_{0.002}^{0.585} (1 - rho) dlog(1/sigma) by
    model and outcome, with medians and the AUC of -C. (c) Balanced 2000-image model: AUC (off- vs on-atom) at
    each sigma >= 0.585 of rho and of the radial ratio, both anchored at the nearest training image of
    D_theta(x, sigma) (rhoA, radA), and of the distance from D_theta to its nearest training image (dD); the AUC
    of C, whose window starts at sigma = 0.585, as one point there."""
    zs = np.load(R / "n3_rho_20261117/sub500/q_per_sample.npz")
    z2 = np.load(R / "n3_rho2_20261118/sub2000/q_per_sample.npz")
    zp = np.load(R / "n3_rho_20261117/public/q_per_sample.npz")
    sg = zs["sigma"]
    for z in (z2, zp):
        assert np.allclose(z["sigma"], sg)
    on_s, on_2 = frac_q(zs) < 1 / 3, frac_q(z2) < 1 / 3
    assert (~on_s).sum() == 41 and (~on_2).sum() == 501

    W, H = FULL_W, 2.1
    fig = plt.figure(figsize=(W, H))
    yb, hh = 0.36, 1.45
    ax = axes_in(fig, 0.4, yb, 2.22, hh)
    XL = (25, 0.0015)
    ax.axvspan(0.585, 0.002, ymax=1 / 1.22, color=FAINT, lw=0, zorder=0)
    ax.text(np.sqrt(0.585 * 0.002), 1.04, r"late window of $C$", ha="center", va="bottom", fontsize=6.4,
            color=GREY)
    series = ((rho_of(zs)[on_s], COPY, "-", True), (rho_of(zs)[~on_s], NEW, "-", True),
              (rho_of(z2)[on_2], COPY, (0, (4, 2)), False), (rho_of(z2)[~on_2], NEW, (0, (4, 2)), False),
              (rho_of(zp), NEW, (0, (1, 1.3)), False))
    for v, c, ls, fill in series:
        q = np.percentile(v, [25, 50, 75], axis=0)
        ax.plot(sg, q[1], color=c, lw=1.3, ls=ls, zorder=3)
        if fill:
            ax.fill_between(sg, q[0], q[2], color=c, alpha=0.13, lw=0, zorder=2)
    ax.axhline(1, color=GREY, lw=0.6, ls=":", zorder=1, xmax=1)
    ax.set_xscale("log"); ax.set_xlim(*XL); ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.5, 1]); ax.spines["left"].set_bounds(0, 1)
    ax.set_xlabel(r"noise level $\sigma$"); ax.set_ylabel(r"relative error $\varrho$ (median)")
    ax.grid(False)
    title(ax, "a", "new images lose contraction first")
    hs = [Line2D([], [], color=GREY, lw=1.2, ls=ls) for ls in ("-", (0, (4, 2)), (0, (1, 1.3)))]
    ax.legend(hs, ["500 images", "2000 images", "public"], loc="upper left", fontsize=6.3,
              handlelength=2.2, borderaxespad=0.2, labelspacing=0.2, bbox_to_anchor=(0.0, 0.84))
    k = 13                                            # sigma = 0.14: label the 500-image medians there
    med_on, med_off = np.median(rho_of(zs)[on_s][:, k]), np.median(rho_of(zs)[~on_s][:, k])
    ax.annotate("copies (on-atom)", (sg[k], med_on), xytext=(5, -1), textcoords="offset points", color=COPY,
                fontsize=6.6, ha="left", va="top")
    kn = 10
    ax.annotate("new images\n(off-atom)", (sg[kn], np.median(rho_of(zs)[~on_s][:, kn])), xytext=(-6, 3),
                textcoords="offset points", color=NEW, fontsize=6.6, ha="right", va="bottom", linespacing=0.95)

    # (b) the late contraction per sample
    axb = axes_in(fig, 3.28, yb, 1.5, hh)
    rows = [("500\nimages", late_contraction(zs), on_s), ("2000\nimages", late_contraction(z2), on_2),
            ("public", late_contraction(zp), np.zeros(len(zp["d1"]), bool))]
    rng = np.random.default_rng(1)
    y = 0.0
    for nm, C, on in rows:
        y_first = y
        for grp, c in ((on, COPY), (~on, NEW)):
            if grp.sum() == 0:
                continue
            v = C[grp]
            jit = rng.uniform(-0.3, 0.3, len(v))
            axb.scatter(v, y + jit, s=1.5, color=c, alpha=0.3, lw=0, rasterized=True)
            med = float(np.median(v))
            axb.plot([med, med], [y - 0.4, y + 0.4], color=c, lw=1.6, solid_capstyle="butt")
            axb.text(med, y + 0.43, f"{med:.2f}", ha="center", va="bottom", fontsize=6.0, color=c)
            y -= 1.0
        y_last = y + 1.0
        axb.text(-0.12, (y_first + y_last) / 2, nm, ha="right", va="center", fontsize=6.5, linespacing=0.95)
        if on.any():                                 # in the empty space of the off-atom row
            a = auc(-C[~on], -C[on])
            axb.text(3.38, y_last, f"AUC {a:.3f}", ha="right", va="center", fontsize=6.2, color=GREY)
        y -= 0.5
    axb.set_yticks([]); axb.set_ylim(y + 0.55, 0.8)
    axb.set_xlim(0, 3.4)
    axb.set_xlabel(r"late contraction $C$")
    axb.spines["left"].set_visible(False)
    axb.grid(False)
    title(axb, "b", "per sample")

    # (c) AUC at sigma >= 0.585 on the balanced model
    axc = axes_in(fig, 5.3, yb, 1.17, hh)
    kk = np.arange(0, 12)
    curves = {}
    for key, c, ls in (("dD", GREY, (0, (4, 2))), ("rhoA", OI["sky"], "-"), ("radA", OI["green"], "-")):
        a = np.array([auc(z2[key][~on_2, i], z2[key][on_2, i]) for i in kk])
        curves[key] = a
        axc.plot(sg[kk], a, color=c, lw=1.2, ls=ls)
    assert abs(curves["dD"][11] - 0.990) < 5e-4
    aC = auc(-late_contraction(z2)[~on_2], -late_contraction(z2)[on_2])
    assert abs(aC - 0.983) < 5e-4
    axc.scatter([sg[11]], [aC], s=16, color=OI["purple"], zorder=5, lw=0)
    axc.set_xscale("log"); axc.set_xlim(100, 0.4); axc.set_ylim(0.45, 1.03)
    axc.set_xlabel(r"noise level $\sigma$"); axc.set_ylabel("AUC, off- vs on-atom")
    axc.grid(False)
    axc.text(35, 0.615, "radial\nratio", color=OI["green"], fontsize=6.2, ha="center", va="bottom",
             linespacing=0.9)
    axc.text(2.5, 0.68, r"$\varrho$", color=OI["sky"], fontsize=7, ha="left", va="center")
    axc.text(13, 0.88, "distance\n" + r"of $D_\theta$", color=GREY, fontsize=6.2, ha="center", va="center",
             linespacing=0.9)
    axc.annotate(r"$C$", (sg[11], aC), xytext=(-1, -6), textcoords="offset points", color=OI["purple"],
                 fontsize=6.6, ha="center", va="top")
    title(axc, "c", "detection, 2000 images")
    save(fig, "fig_landing.pdf", dpi=300)


# --------------------------------------------------------------------------- Figure 3 (collapse in trained nets)
def _ols(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    slope = float((xc * yc).sum() / (xc * xc).sum())
    return slope, float(y.mean() - slope * x.mean())


def _reeval(path: Path):
    r = json.loads(path.read_text(encoding="utf-8"))
    r = r[0] if isinstance(r, list) else r
    ref = np.asarray(r["trace_kernel_per_condition"], float)
    meas = np.asarray(r["ratio_per_condition"], float) * ref
    return ref, meas


def fig_collapse():
    """(a) EXP-1 at h = 0: generated conditional variance through training, five seeds (mean, population SD);
    constant learning rate (solid) and cosine schedule (dashed); unconditional model (grey); references
    tr Sigma_post (exact posterior) and tr Xhat. (b) CIFAR-10 U-Net at h = 0, first instance: completions of one
    condition at four checkpoints (cells of results/exp3/exp3_cifar_ddpm_h0/figures/grid_it*.png) with the
    training-time trace. (c) Generated against reference variance under label smoothing: EXP-1 (each seed and h,
    results/exp1/_theory/raw/p7_kernel.csv) and CIFAR-10 at h = 4 (three retrained instances, 48 conditions each,
    results/exp3/_rerun/reeval_exp3_cifar_heff_h4_s*/reeval.json, with their OLS slopes on log10) and h = 6 (the
    same instances, grey; no slope drawn)."""
    from scripts.make_image_bandwidth_figure import cells
    from scripts.make_paperB_figures import EXP1, EXP3, band, read_csv, seed_mean
    W, H = FULL_W, 2.2
    fig = plt.figure(figsize=(W, H))
    yb, hh = 0.36, 1.5

    # (a)
    const = f"{EXP1}/exp1_cond_seed[0-4]/raw/metrics.csv"
    cosine = f"{EXP1}/exp1_ext_sched_seed[0-4]/raw/metrics.csv"
    uncond = f"{EXP1}/exp1_uncond_seed[0-4]/raw/metrics.csv"
    it_c, tc, tc_sd = seed_mean(const, "train", "trace_cov_mean")
    it_s, ts_, ts_sd = seed_mean(cosine, "train", "trace_cov_mean")
    it_u, tu, tu_sd = seed_mean(uncond, "uncond", "trace_cov_mean")
    post = seed_mean(const, "train", "trace_post")[1].mean()
    data = seed_mean(uncond, "uncond", "trace_data")[1].mean()
    assert abs(tc[list(it_c).index(200000)] - 0.396) < 5e-4 and abs(ts_[list(it_s).index(1000000)] - 0.120) < 5e-4
    ax = axes_in(fig, 0.42, yb, 1.62, hh)
    band(ax, it_u, tu, tu_sd, GREY, ms=2.4, lw=1.1)
    band(ax, it_c, tc, tc_sd, LEARNED, ms=2.4, lw=1.2)
    band(ax, it_s, ts_, ts_sd, LEARNED, ls=(0, (3, 1.5)), marker="s", ms=2.2, lw=1.2)
    ax.axhline(post, color=EXACT, ls=":", lw=1.0)
    ax.axhline(data, color=GREY, ls=":", lw=0.8)
    ax.text(90, post * 0.8, r"exact posterior $\mathrm{tr}\,\Sigma_{\rm post}$", fontsize=6.3, color=EXACT,
            va="top")
    ax.text(90, data * 1.12, "unconditional", fontsize=6.3, color=GREY, va="bottom")
    ax.annotate(f"constant lr\n{tc[-1]:.2f}", (it_c[-1], tc[-1]), xytext=(-9, -5), textcoords="offset points",
                fontsize=6.2, color=LEARNED, ha="right", va="top", linespacing=0.95)
    ax.annotate(f"cosine\n{ts_[-1]:.2f}", (it_s[-1], ts_[-1]), xytext=(4, 1), textcoords="offset points",
                fontsize=6.2, color=LEARNED, ha="left", va="center", linespacing=0.95)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(60, 2.5e6); ax.set_ylim(0.07, 4.0)
    ax.set_xlabel("training iteration"); ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.grid(False)
    title(ax, "a", "EXP-1 collapses")

    # (b) CIFAR completions through training
    runs = ["exp3_cifar_ddpm_h0"]
    met = read_csv(EXP3 / runs[0] / "raw" / "metrics.csv")
    tr = dict(zip(met["iter"].astype(int), met["trace_cov_mean"]))
    assert abs(tr[500] - 179.1) < 0.05 and abs(tr[60000] - 0.431) < 5e-4
    iters = (500, 2000, 8000, 60000)
    cond, comp = 0, (1, 2, 3, 4)
    s, g = 0.3, 0.025
    xb0 = 2.62
    cols = [xb0] + [xb0 + s + 0.07 + j * (s + g) for j in range(len(comp))]
    cols.append(cols[-1] + s + 0.07)
    ytop_t = yb + hh - s - 0.26
    for r, it in enumerate(iters):
        y = ytop_t - r * (s + g + 0.03)
        sheet = cells(EXP3 / runs[0] / "figures" / f"grid_it{it}.png")
        imgs = [sheet[cond][0]] + [sheet[cond][c] for c in comp] + [sheet[cond][7]]
        for j, (xx, im) in enumerate(zip(cols, imgs)):
            fr = LIGHT if j == 0 else (ATOM if j == len(imgs) - 1 else LEARNED)
            tile(axes_in(fig, xx, y, s, s), im, fr, 0.7)
        fig.text((xb0 - 0.05) / W, (y + s / 2) / H, f"{it:,}".replace(",", r"$\,$") + "\n" +
                 rf"tr ${tr[it]:.3g}$", ha="right", va="center", fontsize=6.0, linespacing=1.0)
    hy = ytop_t + s + 0.03
    fig.text((cols[0] + s / 2) / W, hy / H, "top\nhalf", ha="center", va="bottom", fontsize=6.0, linespacing=0.9)
    fig.text((cols[1] + cols[len(comp)] + s) / 2 / W, hy / H, "completions", ha="center", va="bottom",
             fontsize=6.3)
    fig.text((cols[-1] + s / 2) / W, hy / H, "training\nimage", ha="center", va="bottom", fontsize=6.0,
             linespacing=0.9)
    fig.text((xb0 - 0.05) / W, hy / H, "iteration", ha="right", va="bottom", fontsize=6.3)
    figtitle(fig, 2.2, yb + hh + 4.0 / 72, "b", "CIFAR-10 U-Net collapses", fs=8.5)

    # (c) parity: generated against reference variance
    axc = axes_in(fig, 5.05, yb, 1.42, hh)
    d = read_csv(EXP1 / "_theory" / "raw" / "p7_kernel.csv")
    axc.scatter(d["trace_kernel"], d["trace_meas"], s=7, color=OI["green"], lw=0, alpha=0.85, zorder=4)
    shades = ["#D55E00", "#E8955E", "#F2B48A"]
    slopes = []
    for j, sh in enumerate(shades):
        ref, meas = _reeval(R / f"exp3/_rerun/reeval_exp3_cifar_heff_h4_s{j}/reeval.json")
        ok = (ref > 0) & (meas > 0)
        lx, ly = np.log10(ref[ok]), np.log10(meas[ok])
        sl, ic = _ols(lx, ly)
        slopes.append(sl)
        axc.scatter(ref[ok], meas[ok], s=3.5, color=sh, lw=0, alpha=0.8, zorder=3)
        xx = np.array([lx.min(), lx.max()])
        axc.plot(10 ** xx, 10 ** (ic + sl * xx), color=sh, lw=1.0, zorder=5)
        ref6, meas6 = _reeval(R / f"exp3/_rerun/reeval_exp3_cifar_heff_h6_s{j}/reeval.json")
        axc.scatter(ref6, meas6, s=3.5, color=LIGHT, lw=0, alpha=0.9, zorder=2)
    assert np.allclose(sorted(slopes), [0.3159, 0.3438, 0.4267], atol=5e-4), slopes
    lo, hi = 3e-3, 3e3
    axc.plot([lo, hi], [lo, hi], color=ATOM, ls="--", lw=0.8, zorder=1)
    axc.set_xscale("log"); axc.set_yscale("log")
    axc.set_xlim(lo, hi); axc.set_ylim(lo, hi)
    axc.set_xticks([1e-2, 1, 1e2]); axc.set_yticks([1e-2, 1, 1e2])
    axc.set_xlabel(r"reference $\mathrm{tr}\,\mathrm{Cov}_h$"); axc.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    axc.grid(False)
    axc.text(1.6, 0.35, "EXP-1", color=OI["green"], fontsize=6.4, ha="left", va="top")
    axc.text(4e-3, 2.4e3, "CIFAR-10, $h=4$:\n" + rf"slopes {min(slopes):.2f}$-${max(slopes):.2f}",
             color=LEARNED, fontsize=6.2, ha="left", va="top", linespacing=0.95)
    axc.text(2.4e3, 75, "$h=6$", color=GREY, fontsize=6.2, ha="right", va="top")
    axc.text(0.012, 0.03, "exact field", color=ATOM, fontsize=6.2, ha="left", va="bottom", rotation=45,
             rotation_mode="anchor")
    axc.set_aspect("equal", adjustable="box")
    title(axc, "c", "label smoothing")
    save(fig, "fig_collapse.pdf", dpi=300)


def fig_collapse_details():
    """Appendix companion of fig_collapse (the panels moved out of the main text). (a, b) EXP-1 at h = 0, five
    seeds (mean, population SD; constant learning rate solid, cosine schedule dashed): distance of the generated
    mean to the training atom x^i and to the posterior mean, and the relative velocity error to the collapsed
    field (*). (c) EXP-1 with label smoothing: generated over reference variance per h (mean, population SD over
    seeds) with the effective number of atoms n_eff. (d) CIFAR-10 U-Net at h = 0: training-time trace of the
    three independently redrawn instances (results/exp3/exp3_cifar_ddpm_h0{,_seed1,_seed2}/raw/metrics.csv)."""
    from scripts.make_paperB_figures import EXP1, EXP3, band, read_csv, seed_mean
    const = f"{EXP1}/exp1_cond_seed[0-4]/raw/metrics.csv"
    cosine = f"{EXP1}/exp1_ext_sched_seed[0-4]/raw/metrics.csv"
    W, H = FULL_W, 1.85
    fig = plt.figure(figsize=(W, H))
    yb, hh, w = 0.36, 1.2, 1.12
    xs_ = [0.4, 2.0, 3.55, 5.2]
    ax = axes_in(fig, xs_[0], yb, w, hh)
    for pat, ls, mk in ((const, "-", "o"), (cosine, (0, (3, 1.5)), "s")):
        for colname, c in (("mean_err_train_point_mean", ATOM), ("mean_err_post_mean", EXACT)):
            it, m, sd = seed_mean(pat, "train", colname)
            band(ax, it, m, sd, c, ls=ls, marker=mk, ms=2.2, lw=1.1, alpha=0.1)
    ax.set_xscale("log"); ax.set_ylim(0, 1.2); ax.set_xlim(60, 2.5e6)
    ax.text(120, 1.0, r"to the atom $x^i$", fontsize=6.3, color=ATOM, va="bottom")
    ax.text(120, 0.03, "to the posterior mean", fontsize=6.3, color=EXACT, va="bottom")
    ax.set_ylabel("distance of the\ngenerated mean", linespacing=0.95)
    title(ax, "a", "EXP-1: mean")
    ax = axes_in(fig, xs_[1], yb, w, hh)
    for pat, ls, mk in ((const, "-", "o"), (cosine, (0, (3, 1.5)), "s")):
        it, m, sd = seed_mean(pat, "train", "vel_rel_err_mean_mean")
        band(ax, it, m, sd, LEARNED, ls=ls, marker=mk, ms=2.2, lw=1.1)
    ax.set_xscale("log"); ax.set_ylim(0, 0.9); ax.set_xlim(60, 2.5e6)
    ax.set_ylabel(r"velocity error to $(\star)$")
    ax.text(120, 0.5, "solid: constant lr\ndashed: cosine", fontsize=6.2, color=LEARNED, ha="left", va="top",
            linespacing=1.0)
    title(ax, "b", "EXP-1: field")
    for a in fig.axes:
        a.set_xlabel("training iteration"); a.grid(False)
    # (c) ratio to the kernel reference
    d = read_csv(EXP1 / "_theory" / "raw" / "p7_kernel.csv")
    hs = sorted(set(d["h"]))
    ratio = np.array([np.mean(d["ratio_to_kernel"][d["h"] == h]) for h in hs])
    ratio_sd = np.array([np.std(d["ratio_to_kernel"][d["h"] == h]) for h in hs])
    neff = np.array([np.mean(d["n_eff"][d["h"] == h]) for h in hs])
    assert np.allclose(ratio, [1.308, 1.002, 0.994, 1.011], atol=5e-4), ratio
    ax = axes_in(fig, xs_[2], yb, w, hh)
    x = np.arange(len(hs))
    ax.axhline(1.0, color=ATOM, ls="--", lw=0.8)
    ax.errorbar(x, ratio, yerr=ratio_sd, marker="o", ms=3, ls="none", capsize=2, elinewidth=0.8, color=LEARNED)
    for j, (xi, n, r_, sd) in enumerate(zip(x, neff, ratio, ratio_sd)):
        ax.text(xi + (0.12 if j == 0 else 0), r_ + sd + 0.03, (rf"$n_{{\rm eff}}={n:.1f}$" if j == 0 else f"{n:.1f}"),
                ha="left" if j == 0 else "center", va="bottom", fontsize=6.2, color=GREY)
    ax.set_xticks(x, [f"{h:g}" for h in hs]); ax.set_xlim(-0.45, len(hs) - 0.55); ax.set_ylim(0.8, 1.9)
    ax.set_xlabel("label bandwidth $h$"); ax.set_ylabel("generated / reference")
    ax.grid(False)
    title(ax, "c", r"EXP-1: ratio to $\mathrm{Cov}_h$")
    # (d) CIFAR-10 trace through training, three instances
    runs = ["exp3_cifar_ddpm_h0", "exp3_cifar_ddpm_h0_seed1", "exp3_cifar_ddpm_h0_seed2"]
    ax = axes_in(fig, xs_[3], yb, w, hh)
    for r, c, mk in zip(runs, [LEARNED, "#E8955E", "#F2B48A"], ("o", "s", "^")):
        m = read_csv(EXP3 / r / "raw" / "metrics.csv")
        ax.plot(m["iter"], m["trace_cov_mean"], color=c, marker=mk, ms=2.6, lw=1.1, mec="white", mew=0.3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration"); ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.text(0.05, 0.08, "three instances", transform=ax.transAxes, fontsize=6.3, color=LEARNED)
    ax.grid(False)
    title(ax, "d", "CIFAR-10, $h=0$")
    save(fig, "fig_collapse_details.pdf")


ALL = {"teaser": fig_teaser, "mechanism": fig_mechanism, "landing": fig_landing, "collapse": fig_collapse,
       "details": fig_collapse_details}

if __name__ == "__main__":
    use_paper_style()
    for name in (sys.argv[1:] or ALL):
        ALL[name]()
