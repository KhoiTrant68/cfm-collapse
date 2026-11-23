"""Figures for Theorem thm:relerr, Proposition prop:heun and Section sec:edm.

    python -m scripts.make_edm_figures

fig_intuition.pdf         one-step cartoon and EDM image strips from the same latent (Figure 1).
fig_unrolled.pdf          time-unrolled 1-D flows: interventions on the exact field and two learned fields (Figure 2).
fig_landscape.pdf         the exact landscape -log p_t in d=2 with an exact and a learned trajectory (Figure 3).
fig_relerr_mechanism.pdf  (no longer in the paper) toy flows in d=2, from fig_mechanism().
fig_edm_clocks.pdf        EDM on CIFAR-10: selection (swap), relative error by group, AUC against the baseline.
fig_heun.pdf              Heun step weights, the contraction threshold with measured errors, certificate coverage.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, OI, image_frame, panel_tag, portrait_axis, save, style, use_paper_style

try:
    from scripts.n3_edm_memorization import auc
except (ImportError, OSError):  # that module imports torch; the figures only need this helper
    def auc(pos, neg):
        """P(pos > neg) + P(pos = neg)/2; a copy of scripts.n3_edm_memorization.auc."""
        pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
        if len(pos) == 0 or len(neg) == 0:
            return float("nan")
        x = np.concatenate([pos, neg]); r = np.empty(len(x)); o = x.argsort(kind="mergesort")
        r[o] = np.arange(1, len(x) + 1)
        for v in np.unique(x):
            m = x == v
            r[m] = r[m].mean()
        return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))

R = Path("results")
GROUP = {"on": OI["blue"], "off": OI["vermillion"], "public": OI["orange"]}
STEPS = {18: OI["black"], 36: OI["green"], 64: OI["purple"]}


# --------------------------------------------------------------------------- toy mechanism
def _toy(atoms, x0, mode, n_steps=1500, t_end=1 - 1e-5):
    """RK4 for dZ/dt = (xhat - Z)/(1-t), xhat = m* + (1 - delta_t)(Z - m*), on a grid graded to t=1."""
    ts = 1 - np.geomspace(1.0, 1 - t_end, n_steps + 1)

    def mstar(z, t):
        d2 = ((z[:, None, :] - t * atoms[None]) ** 2).sum(-1) / (2 * (1 - t) ** 2)
        w = np.exp(-(d2 - d2.min(1, keepdims=True)))
        w /= w.sum(1, keepdims=True)
        return w @ atoms

    def rho(t):
        if mode == "exact":
            return 0.0
        if mode == "const":
            return 0.6
        return 1 - 0.6 * np.sqrt(1 - t)        # 1 - rho = 0.6 (1-t)^{1/2}: integrable against dt/(1-t)

    def f(t, z):
        m = mstar(z, t)
        return (m + rho(t) * (z - m) - z) / (1 - t)

    z = x0.copy(); out = [z.copy()]
    for a, b in zip(ts[:-1], ts[1:]):
        h = b - a
        k1 = f(a, z); k2 = f(a + h / 2, z + h / 2 * k1); k3 = f(a + h / 2, z + h / 2 * k2); k4 = f(b, z + h * k3)
        z = z + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(z.copy())
    return ts, np.stack(out)


def fig_mechanism():
    atoms = np.array([[-1.6, -0.9], [1.7, -0.6], [0.1, 1.7]])
    x0 = np.random.default_rng(3).normal(size=(70, 2)) * 1.25
    titles = {"exact": r"(a) exact field, $\varrho=0$", "const": r"(b) learned, $\varrho_t=0.6$",
              "late": r"(c) learned, $\varrho_t\to1$ late"}
    fig, axes = plt.subplots(1, 4, figsize=(7.6, 2.1), gridspec_kw={"width_ratios": [1, 1, 1, 1.3]})
    curves = {}
    for ax, (mode, ttl), tag in zip(axes[:3], titles.items(), "abc"):
        ts, P = _toy(atoms, x0, mode)
        ax.plot(P[:, :, 0], P[:, :, 1], color=COLORS["path"], alpha=0.25, lw=0.6, zorder=1)
        ax.scatter(P[0, :, 0], P[0, :, 1], s=5, color=COLORS["source"], alpha=0.6, lw=0, zorder=2)
        ax.scatter(P[-1, :, 0], P[-1, :, 1], s=14, color=COLORS["generated"], alpha=0.8,
                   edgecolors="white", linewidths=0.4, zorder=4)
        ax.scatter(atoms[:, 0], atoms[:, 1], marker="o", s=130, facecolors="none", edgecolors=COLORS["atom"],
                   linewidths=1.4, zorder=5)
        ax.set_xlim(-3.2, 3.2); ax.set_ylim(-3.0, 3.2)
        portrait_axis(ax); ax.set_title(ttl, fontsize=8.5, loc="left", pad=3)
        d = np.linalg.norm(P[:, :, None, :] - atoms[None, None], axis=-1)
        a = d[-1].argmin(1)
        curves[mode] = (1 - ts, np.median(d[:, np.arange(len(x0)), a], axis=1))
    ax = axes[3]
    for mode, c in (("exact", COLORS["reference"]), ("const", OI["green"]), ("late", COLORS["generated"])):
        e, n = curves[mode]
        ax.loglog(e[1:], n[1:], color=c, lw=1.8, label={"exact": r"$\varrho=0$", "const": r"$\varrho=0.6$",
                                                        "late": r"$\varrho_t\to1$"}[mode])
    ax.invert_xaxis(); ax.set_xlabel(r"$1-t$")
    ax.legend(fontsize=7.5, loc="lower left"); style(ax)
    ax.set_title("(d) median distance to atom", fontsize=8.5, loc="left", pad=3)
    fig.subplots_adjust(wspace=0.08)
    pos = ax.get_position(); ax.set_position([pos.x0 + 0.045, pos.y0, pos.width - 0.045, pos.height])
    save(fig, "fig_relerr_mechanism.pdf")


# --------------------------------------------------------------------------- two clocks
def _swap(path, header):
    rows, on = [], False
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.startswith(header):
            on = True; continue
        if on and ln.startswith("| ") and ln[2].isdigit():
            c = [x.strip() for x in ln.strip("|").split("|")]
            rows.append((float(c[0]), float(c[3])))
        elif on and rows and not ln.startswith("|"):
            break
    return np.array(rows)


def fig_clocks():
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.25))
    ax = axes[0]
    for path, hdr, lab, c in ((R / "n3_followup_sub500_20261111/SWAP_SUMMARY.md", "## swap_sub500", "subset (500)", GROUP["on"]),
                              (R / "n3_followup_20261111/SWAP_SUMMARY.md", "## swap_public", "public (50k)", GROUP["public"])):
        s = _swap(path, hdr)
        ax.semilogx(s[:, 0], 100 * s[:, 1], marker="o", ms=3.5, color=c, lw=1.6, label=lab)
    ax.invert_xaxis(); ax.set_xlabel(r"hand-over level $s$ ($\sigma$)"); ax.set_ylabel("same image as network (%)")
    ax.set_ylim(20, 103); ax.legend(fontsize=7, loc="lower right"); style(ax); panel_tag(ax, "a")
    ax.set_title("selection: early", fontsize=9)

    zs = np.load(R / "n3_rho_20261117/sub500/q_per_sample.npz"); zp = np.load(R / "n3_rho_20261117/public/q_per_sample.npz")
    on = zs["d1"] / zs["d2"] < 1 / 3
    sg = zs["sigma"]
    z2 = np.load(R / "n3_rho2_20261118/sub2000/q_per_sample.npz")
    on2 = z2["d1"] / z2["d2"] < 1 / 3
    ax = axes[1]
    for lab, v, c, ls in (("500: on-atom", (zs["err"] / zs["n1"])[on], GROUP["on"], "-"),
                          ("500: off-atom", (zs["err"] / zs["n1"])[~on], GROUP["off"], "-"),
                          ("2000: on-atom", (z2["err"] / z2["n1"])[on2], GROUP["on"], "--"),
                          ("2000: off-atom", (z2["err"] / z2["n1"])[~on2], GROUP["off"], "--"),
                          ("public", zp["err"] / zp["n1"], GROUP["public"], "-")):
        q = np.nanpercentile(v, [25, 50, 75], axis=0)
        ax.semilogx(sg, q[1], color=c, lw=1.4, ls=ls)
        if ls == "-":
            ax.fill_between(sg, q[0], q[2], color=c, alpha=0.15, lw=0)
    ax.axhline(1, ls=":", color=COLORS["theory"], lw=1.0)
    ax.set_xlim(20, 0.0015); ax.set_ylim(0, 1.08)
    ax.set_xlabel(r"noise level $\sigma$"); ax.set_ylabel(r"relative error $\varrho_t$")
    # factored legend: colour = group, line style = training-set size; it fits the empty lower-right corner
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], color=GROUP["on"], lw=1.4), Line2D([], [], color=GROUP["off"], lw=1.4),
          Line2D([], [], color=GROUP["public"], lw=1.4), Line2D([], [], color="k", lw=1.2, ls="-"),
          Line2D([], [], color="k", lw=1.2, ls="--")]
    leg = ax.legend(hs[:3], ["on-atom", "off-atom", "public"], fontsize=6.3, loc="upper left",
                    handlelength=1.4, borderaxespad=0.2, labelspacing=0.25,
                    frameon=True, facecolor="white", edgecolor="none", framealpha=1.0)   # masks the rule at 1
    ax.add_artist(leg)
    ax.legend(hs[3:], ["500 images", "2000 images"], fontsize=6.3, loc="lower right",
              handlelength=1.6, borderaxespad=0.2, labelspacing=0.25)
    style(ax); panel_tag(ax, "b")
    ax.set_title("landing: late", fontsize=9)

    ax = axes[2]
    for key, lab, c, ls in (("rhoA", r"$\varrho$, predictive anchor", GROUP["on"], "-"),
                            ("radA", "radial ratio", OI["green"], "-"),
                            ("dD", "NN distance of $D_\\theta$", COLORS["theory"], "--")):
        a = [auc(z2[key][~on2, i], z2[key][on2, i]) for i in range(len(z2["sigma"]))]
        ax.semilogx(z2["sigma"], a, color=c, lw=1.5, ls=ls, label=lab)
    rho2 = z2["err"] / z2["n1"]; sg2 = z2["sigma"]; inc = (1 - 0.5 * (rho2[:, :-1] + rho2[:, 1:])) * np.log(sg2[:-1] / sg2[1:])
    cum = [auc(-inc[~on2, 11:k].sum(1), -inc[on2, 11:k].sum(1)) for k in range(12, len(sg2))]
    ax.semilogx(sg2[12:], cum, color=OI["purple"], lw=1.8, label=r"late contraction")
    ax.set_xlim(60, 0.0015); ax.set_ylim(0.45, 1.02)
    ax.set_xlabel(r"noise level $\sigma$"); ax.set_ylabel("AUC (off- vs on-atom)")
    ax.legend(fontsize=6.3, loc="lower right", handlelength=1.6, borderaxespad=0.2); style(ax); panel_tag(ax, "c")
    ax.set_title("detector, 2000 images", fontsize=9)
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig_edm_clocks.pdf")


# --------------------------------------------------------------------------- Heun sampler
def _rhocrit(r):
    r = np.asarray(r, float)
    return np.where(r >= 0.5, 1.0, (np.sqrt(1 + 8 * r / (1 - r)) - 1) / 2)


def fig_heun():
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.25))
    r = np.linspace(0.2, 0.95, 400)
    kap, th = (1 - r) * (2 * r - 1) / (2 * r), (1 - r) / (2 * r)
    ax = axes[0]
    ax.axvspan(0.2, 0.5, color=OI["vermillion"], alpha=0.08, lw=0)
    ax.plot(r, r, color=COLORS["path"], lw=1.6, label=r"$r$ (on $x_k$)")
    ax.plot(r, kap, color=OI["vermillion"], lw=1.6, label=r"$\kappa$ (on $D_k$)")
    ax.plot(r, th, color=OI["blue"], lw=1.6, label=r"$\theta$ (on $\tilde D_k$)")
    ax.axhline(0, color="k", lw=0.6)
    ax.text(0.35, 2.62, "extrapolates\n" + r"($\kappa<0$)", ha="center", va="top", fontsize=7.5,
            color=OI["vermillion"], linespacing=1.0)   # head room above theta, clear of every curve
    ax.set_xlabel(r"step ratio $r=\sigma_{k+1}/\sigma_k$"); ax.set_ylabel("weight")
    ax.set_ylim(-1.0, 2.7); ax.legend(fontsize=7, loc="upper right", borderaxespad=0.2)
    style(ax); panel_tag(ax, "a")

    ax = axes[1]
    ax.fill_between(r, 0, _rhocrit(r), color=OI["green"], alpha=0.15, lw=0)
    ax.plot(r, _rhocrit(r), color=COLORS["theory"], lw=1.6)
    ax.text(0.62, 0.45, r"$c_k<1$", fontsize=8.5, color=OI["green"])
    ax.text(0.205, 0.72, r"$c_k\geq1$", fontsize=8.5)
    for S, c in STEPS.items():
        z = np.load(R / f"n3_steps_20261117/s{S}/sub500/q_per_sample.npz")
        on = z["d1"] / z["d2"] < 1 / 3
        rk = z["sigma"][1:] / z["sigma"][:-1]
        rt = np.median((z["errt"][:, :-1] / z["nt1"][:, :-1])[on], axis=0)
        ax.scatter(rk, rt, s=10, color=c, zorder=3, label=f"{S} steps", edgecolors="white", linewidths=0.3)
    ax.set_xlim(0.2, 0.95); ax.set_ylim(0, 1.05)
    ax.set_xlabel(r"step ratio $r_k$"); ax.set_ylabel(r"$\varrho$ at predictor (median)")
    ax.legend(fontsize=7, loc="lower left"); style(ax); panel_tag(ax, "b")

    ax = axes[2]
    for S, c in STEPS.items():
        z = np.load(R / f"n3_steps_20261117/s{S}/sub500/q_per_sample.npz")
        on = z["d1"] / z["d2"] < 1 / 3; sg = z["sigma"]; rk = sg[1:] / sg[:-1]
        rho = np.maximum(z["err"][:, :-1] / z["n1"][:, :-1], z["errt"][:, :-1] / z["nt1"][:, :-1])
        ka, th_ = np.abs((1 - rk) * (2 * rk - 1) / (2 * rk)), (1 - rk) / (2 * rk)
        ck = rk + ka * rho + th_ * rho * (rk + (1 - rk) * rho)
        ax.semilogx(sg[:-1], 100 * (ck[on] < 1).mean(0), color=c, lw=1.6, marker="o", ms=2.5, label=f"{S} steps")
    ax.set_xlim(100, 0.0015); ax.set_ylim(-3, 103)
    ax.set_xlabel(r"noise level $\sigma_k$"); ax.set_ylabel(r"on-atom with $c_k<1$ (%)")
    ax.legend(fontsize=7, loc="lower left"); style(ax); panel_tag(ax, "c")
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig_heun.pdf")


# --------------------------------------------------------------------------- intuition (Figure 1)
def _step_cartoon(ax, inside: bool):
    """One Euler step x -> x' = r x + (1-r) D: x' is closer to the image a iff D lies in the circle |y-a| < |x-a|."""
    from matplotlib.patches import Circle, FancyArrowPatch
    a = np.array([0.0, 0.0]); x = np.array([1.0, 0.55]); n = np.linalg.norm(x - a)
    Dp = np.array([-0.35, -0.25]) if inside else np.array([-0.15, 1.3])
    r = 0.45; xn = r * x + (1 - r) * Dp
    ax.add_patch(Circle(a, n, fill=True, facecolor=OI["green"] if inside else OI["vermillion"], alpha=0.08, lw=0))
    ax.add_patch(Circle(a, n, fill=False, ls="--", lw=0.9, ec=COLORS["path"]))
    ax.scatter(*a, s=70, marker="s", color=COLORS["atom"], zorder=5)
    ax.text(a[0] + 0.07, a[1] - 0.2, "training\nimage", fontsize=7, ha="left", va="top")
    ax.scatter(*x, s=30, color=COLORS["source"], zorder=5, edgecolors="k", linewidths=0.4)
    ax.text(x[0] + 0.07, x[1] + 0.05, r"$x$", fontsize=9)
    ax.scatter(*Dp, s=40, marker="D", color=COLORS["generated"], zorder=5)
    ax.text(Dp[0] - 0.17, Dp[1], "network's\nguess", fontsize=7, ha="right", va="center",
            color=COLORS["generated"])
    ax.plot([x[0], Dp[0]], [x[1], Dp[1]], ls=":", color=COLORS["path"], lw=0.9)
    ax.add_patch(FancyArrowPatch(x, xn, arrowstyle="-|>", mutation_scale=9, lw=1.4,
                                 color=OI["green"] if inside else OI["vermillion"], zorder=4))
    if inside:                                      # right of the image, below the arrow
        ax.text(xn[0] + 0.12, xn[1] - 0.1, "next", fontsize=7, ha="left", va="center")
    else:                                           # above the line x -> guess, on which the next state lies
        u = (Dp - x) / np.linalg.norm(Dp - x); nrm = np.array([-u[1], u[0]])
        nrm = nrm if nrm[1] > 0 else -nrm
        ax.text(*(xn + 0.24 * nrm), "next", fontsize=7, ha="center", va="center")
    ax.set_xlim(-1.75, 1.55); ax.set_ylim(-1.3, 1.65); portrait_axis(ax)
    ax.set_title(("guess inside the circle:\nstep moves closer" if inside else
                  "guess outside the circle:\nno guaranteed progress"), fontsize=8, pad=2,
                 color=OI["green"] if inside else OI["vermillion"])


def _img(v):
    return np.clip((np.asarray(v, np.float32).reshape(3, 32, 32).transpose(1, 2, 0) + 1) / 2, 0, 1)


def fig_intuition(sub_i: int, pub_i: int, steps=(5, 8, 10, 12, 14, 16)):
    zs = np.load(R / "n3_strips_20261118/sub500.npz"); zp = np.load(R / "n3_strips_20261118/public.npz")
    fig = plt.figure(figsize=(7.6, 3.55))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.0, 3.3], wspace=0.06)
    left = outer[0].subgridspec(2, 1, hspace=0.35)
    _step_cartoon(fig.add_subplot(left[0]), True); _step_cartoon(fig.add_subplot(left[1]), False)
    nc = len(steps) + 2
    right = outer[1].subgridspec(5, nc, height_ratios=[0.16, 1, 1, 1, 1], hspace=0.08, wspace=0.05)
    sg = zs["sigma"]
    for j, k in enumerate(steps):
        ax = fig.add_subplot(right[0, j]); ax.axis("off")
        ax.text(0.5, 0.0, rf"$\sigma={sg[k]:.2g}$", ha="center", va="bottom", fontsize=7.5)
    for j, t in enumerate(("output", "nearest\ntrain image")):
        ax = fig.add_subplot(right[0, len(steps) + j]); ax.axis("off")
        ax.text(0.5, 0.0, t, ha="center", va="bottom", fontsize=7)
    for blk, (z, i, name, col) in enumerate(((zs, sub_i, "trained on\n500 images", OI["blue"]),
                                             (zp, pub_i, "public model\n(50k images)", OI["orange"]))):
        lab = fig.add_subplot(right[1 + 2 * blk, len(steps):]); lab.axis("off")
        ratio = z["d1"][i] / z["d2"][i]
        lab.text(0.5, 0.5, name + "\n" + ("$\\Rightarrow$ copies the image" if ratio < 1 / 3 else
                                          "$\\Rightarrow$ new image"),
                 ha="center", va="center", fontsize=7.5, color=col, fontweight="bold")
        for row, key in enumerate(("x", "D")):
            for j, k in enumerate(steps):
                ax = fig.add_subplot(right[1 + 2 * blk + row, j])
                v = z[key][i, k].astype(np.float32)
                if key == "x":
                    v = v / np.sqrt(1 + sg[k] ** 2)            # rescale the noisy state for display
                ax.imshow(_img(v)); ax.set_xticks([]); ax.set_yticks([])
                for s_ in ax.spines.values():
                    s_.set_visible(key == "D"); s_.set_color(col); s_.set_linewidth(1.2)
                if key == "D":
                    rho = float(z["rho"][i, k])
                    ax.text(0.5, -0.06, rf"$\varrho={rho:.2f}$", transform=ax.transAxes, ha="center", va="top",
                            fontsize=6.5, color=OI["green"] if rho < 1 - 1e-3 else OI["vermillion"])
                if j == 0:
                    ax.set_ylabel({"x": "state $x$", "D": "guess $D(x)$"}[key], fontsize=7, labelpad=2)
            if row == 0:
                continue
            for j, v in enumerate((z["end"][i], z["y1"][i])):
                ax = fig.add_subplot(right[1 + 2 * blk + row, len(steps) + j])
                ax.imshow(_img(v.astype(np.float32)))
                image_frame(ax, COLORS["atom"] if j else col)
    save(fig, "fig_intuition.pdf")


# --------------------------------------------------------------------------- time-unrolled 1-D flows
def _m1d(z, t, atoms, p):
    lg = np.log(p)[None] - (z[:, None] - t * atoms[None]) ** 2 / (2 * (1 - t) ** 2)
    lg -= lg.max(1, keepdims=True); w = np.exp(lg); w /= w.sum(1, keepdims=True)
    return w @ atoms


def _run1d(F, z0, T=12.0, n=3000):
    """Integrate dz/dtau = F(z, t) in log time tau = -log(1-t) (the flow is dz/dt = F/(1-t)); RK4."""
    taus = np.linspace(0, T, n + 1); t = lambda s: 1 - np.exp(-s)  # noqa: E731
    z = z0.copy(); out = [z.copy()]
    for a, b in zip(taus[:-1], taus[1:]):
        h = b - a
        k1 = F(z, t(a)); k2 = F(z + h / 2 * k1, t(a + h / 2)); k3 = F(z + h / 2 * k2, t(a + h / 2)); k4 = F(z + h * k3, t(b))
        z = z + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(z.copy())
    return 1 - np.exp(-taus), np.array(out)


def fig_unrolled(exact_only: bool = False, out: str | Path = "fig_unrolled.pdf", select=None):
    """Small multiples in the style of time-unrolled transport diagrams: source density on top, paths, and the
    endpoint law at the bottom, where spikes are copies of training examples and smooth bumps are new samples.

    ``exact_only`` draws panels (a)-(c) only, the exact-field interventions, for the theory paper.
    ``select`` draws the listed panels (indices into the five below, e.g. [0, 3, 4] for the mechanism
    paper), relabelled (a), (b), ... in that order."""
    rng = np.random.default_rng(0)
    z0 = np.sort(rng.normal(size=1500))
    at4 = np.array([-2.1, -0.7, 0.7, 2.1]); p = np.array([0.12, 0.48, 0.28, 0.12]); pu = np.full(4, 0.25)
    at2 = np.array([-1.0, 1.0]); B = 1.0; wc = 1 / np.sinh(B) ** 2
    s = 1 / (1 + np.exp(-2 * B)); pp, pm, p2u = np.array([s, 1 - s]), np.array([1 - s, s]), np.array([0.5, 0.5])
    w_g, w_c2 = 2.0, 2 * wc
    panels = [
        ("label noise", "copies, reweighted", at4,
         lambda z, t: _m1d(z, t, at4, p) - z),
        ("guidance", "copies, sharper", at4,
         lambda z, t: (1 + w_g) * _m1d(z, t, at4, p) - w_g * _m1d(z, t, at4, pu) - z),
        (r"guidance$\circ$averaging", "blends appear", at2,
         lambda z, t: (1 + w_c2) * 0.5 * (_m1d(z, t, at2, pp) + _m1d(z, t, at2, pm)) - w_c2 * _m1d(z, t, at2, p2u) - z),
        (r"learned, $\varrho=0.6$", "still copies", at4,
         lambda z, t: 0.4 * (_m1d(z, t, at4, p) - z)),
        (r"learned, $\varrho\to1$", "new samples", at4,
         lambda z, t: 0.6 * np.sqrt(1 - t) * (_m1d(z, t, at4, p) - z)),
    ]
    chosen = list(select) if select is not None else ([0, 1, 2] if exact_only else [0, 1, 2, 3, 4])
    n_ex = sum(i < 3 for i in chosen); n_le = len(chosen) - n_ex
    ratios = [1] * n_ex + ([0.12] if n_ex and n_le else []) + [1] * n_le
    cols = list(range(n_ex)) + [n_ex + (1 if n_ex else 0) + j for j in range(n_le)]
    fig = plt.figure(figsize=(1.52 * len(chosen) + (0.2 if n_ex and n_le else 0.0), 2.9))
    gs = fig.add_gridspec(3, len(ratios), height_ratios=[0.22, 1, 0.34], width_ratios=ratios,
                          hspace=0.0, wspace=0.08)
    acol = [OI["sky"], OI["green"], OI["orange"], OI["purple"]]
    xs = np.linspace(-3.4, 3.4, 400)
    group_axes = {"exact": [], "learned": []}
    for k, (orig, c) in enumerate(zip(chosen, cols)):
        ttl, sub, atoms, F = panels[orig]
        ts, P = _run1d(F, z0)
        end = P[-1]
        near = np.abs(end[:, None] - atoms[None]).argmin(1)
        blend = (len(atoms) == 2) & (np.abs(end) < 0.1)
        top = fig.add_subplot(gs[0, c]); mid = fig.add_subplot(gs[1, c], sharex=top); bot = fig.add_subplot(gs[2, c], sharex=top)
        group_axes["exact" if orig < 3 else "learned"].append(top)
        top.fill_between(xs, 0, np.exp(-xs ** 2 / 2), color=COLORS["source"], alpha=0.45, lw=0)
        idx = np.linspace(0, len(z0) - 1, 140).astype(int)
        for i in idx:
            col = OI["vermillion"] if blend[i] else acol[near[i] if len(atoms) == 4 else (0 if near[i] == 0 else 3)]
            mid.plot(P[:, i], ts, color=col, lw=0.45, alpha=0.55)
        for a_ in atoms:
            mid.plot([a_, a_], [0.985, 1.0], color=COLORS["atom"], lw=1.0)
        if orig == 4:                               # new samples: a smooth density
            dens = np.exp(-(xs[:, None] - end[None]) ** 2 / (2 * 0.06 ** 2)).sum(1)
            bot.fill_between(xs, 0, -0.75 * dens / dens.max(), color=COLORS["generated"], alpha=0.75, lw=0)
        else:                                       # copies: point masses, drawn as stems of height = mass
            spots = np.append(atoms, 0.0) if len(atoms) == 2 else atoms
            for x_ in spots:
                m = float(np.mean(np.abs(end - x_) < 0.1))
                if m > 0.005:
                    bot.plot([x_, x_], [0, -m], color=COLORS["generated"], lw=2.2, solid_capstyle="butt")
                    bot.scatter([x_], [-m], s=10, color=COLORS["generated"], zorder=4)
        bot.scatter(atoms, np.zeros_like(atoms), marker="|", s=40, color=COLORS["atom"], zorder=3)
        if len(atoms) == 2:                         # the blend is not a training point: mark it in its own colour
            bot.scatter([0.0], [0.0], marker="|", s=40, color=COLORS["generated"], zorder=3)
        for a in (top, mid, bot):
            a.set_xticks([]); a.set_yticks([]); a.grid(False)
            for s_ in a.spines.values():
                s_.set_visible(False)
        mid.set_ylim(1.0, 0.0); mid.set_xlim(-3.4, 3.4)
        bot.set_ylim(-1.0, 0.1)
        top.set_ylim(0, 1.15)
        top.set_title(f"({'abcde'[k]}) {ttl}", fontsize=8, pad=1)
        bot.text(0.5, -0.12, sub, transform=bot.transAxes, ha="center", va="top", fontsize=7.5,
                 color=OI["vermillion"] if orig in (2, 4) else COLORS["atom"])
        if k == 0:
            mid.annotate("", xy=(-3.3, 0.95), xytext=(-3.3, 0.05),
                         arrowprops=dict(arrowstyle="-|>", color=COLORS["path"], lw=0.8))
            mid.text(-3.2, 0.5, r"$t$", fontsize=8, color=COLORS["path"], va="center")
            top.text(-3.4, 0.9, "noise", fontsize=6.5, color=COLORS["source"], va="top")
            bot.text(-3.4, -0.25, "output", fontsize=6.5, color=COLORS["generated"], va="top")
    heads = []
    for key, txt in (("exact", "exact field of the training set" if n_ex > 1 else "exact field"),
                     ("learned", "learned field")):
        if group_axes[key]:
            x0_ = min(a.get_position().x0 for a in group_axes[key])
            x1_ = max(a.get_position().x1 for a in group_axes[key])
            heads.append((x0_ + 0.01, x1_ - 0.01, txt))
    for x0_, x1_, txt in heads:
        fig.add_artist(plt.Line2D([x0_, x1_], [0.965, 0.965], color=COLORS["path"], lw=0.8))
        fig.text((x0_ + x1_) / 2, 0.975, txt, ha="center", va="bottom", fontsize=8.5, color=COLORS["path"])
    out = Path(out)
    if out.parent == Path("."):
        save(fig, out.name)
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        print(f"  wrote {out}")


# --------------------------------------------------------------------------- 3-D landscape
def fig_landscape():
    """The exact landscape -log p_t(z) of three training points sharpens into wells as t -> 1; the exact flow falls
    into one, a learned flow with relative error -> 1 stops on the wall. Heights are rescaled per panel."""
    atoms = np.array([[-1.6, -0.9], [1.7, -0.6], [0.1, 1.7]])
    x0 = np.array([[2.4, 1.0]])
    ts_e, Pe = _toy(atoms, x0[:1], "exact")
    ts_l, Pl = _toy(atoms, x0[:1], "late")
    g = np.linspace(-3.0, 3.0, 220); Xg, Yg = np.meshgrid(g, g)
    Z2 = np.stack([Xg.ravel(), Yg.ravel()], 1)

    def U(z, t):
        d2 = ((z[:, None, :] - t * atoms[None]) ** 2).sum(-1) / (2 * (1 - t) ** 2)
        m = d2.min(1)
        return m - np.log(np.exp(-(d2 - m[:, None])).sum(1)) + 2 * np.log(1 - t)

    def norm(u, cap):                               # log scale, so that narrow wells stay visible as funnels
        return np.log1p(u - u.min()) / cap

    shots = [(0.35, Pe, ts_e, "early: one smooth bowl"), (0.75, Pe, ts_e, "wells form at the images"),
             (0.985, Pe, ts_e, "exact field: falls in (copy)"), (0.985, Pl, ts_l, r"$\varrho\to1$: stops on the wall")]
    fig = plt.figure(figsize=(7.6, 1.7))
    for k, (t, P, ts, ttl) in enumerate(shots):
        ax = fig.add_subplot(1, 4, k + 1, projection="3d", computed_zorder=False)
        cap = float(np.log1p(np.ptp(U(Z2, t))))
        H = norm(U(Z2, t), cap).reshape(Xg.shape)
        ax.plot_surface(Xg, Yg, H, cmap="coolwarm", rstride=2, cstride=2, linewidth=0.1, edgecolor=(1, 1, 1, 0.15),
                        antialiased=True, alpha=0.95, rasterized=True)   # raster surface: the vector mesh was ~3 MB
        upto = ts <= t
        path = P[upto, 0, :]
        hp = (np.log1p(U(path, t) - U(Z2, t).min()) / cap)
        ax.plot(path[:, 0], path[:, 1], hp + 0.03, color="#2E7D32", lw=1.6, zorder=10)
        ax.scatter(path[-1, 0], path[-1, 1], hp[-1] + 0.05, s=22, color="#8BC34A", edgecolors="#1B5E20",
                   linewidths=0.7, zorder=11, depthshade=False)
        ax.view_init(elev=42, azim=-100); ax.set_axis_off(); ax.set_zlim(0, 1.0)
        ax.set_box_aspect((1, 1, 0.62), zoom=1.25)
        ax.set_title(f"({'abcd'[k]}) " + (rf"$t={t}$" if k < 3 else rf"$t={t}$") + "\n" + ttl, fontsize=7.8, pad=-2,
                     color=OI["vermillion"] if k == 3 else "black")
    fig.subplots_adjust(left=0, right=1, bottom=-0.34, top=0.88, wspace=-0.12)
    # a 3-D axis keeps its whole box in the tight bounding box, which left an empty band under the
    # funnels; crop to the drawn content instead
    from matplotlib.transforms import Bbox
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    out = Path("figures_out/fig_landscape.pdf")
    fig.savefig(out, dpi=300, bbox_inches=Bbox.from_extents(bb.x0, bb.y0 + 0.2 * bb.height, bb.x1, bb.y1 + 0.02))
    plt.close(fig)
    print(f"  wrote {out}")


if __name__ == "__main__":
    use_paper_style()
    fig_unrolled(); fig_landscape(); fig_clocks(); fig_heun()
    fig_intuition(sub_i=17, pub_i=17)        # needs results/n3_strips_20261118 (scripts/n3_image_strips.py)
