"""Pictures for the proofs that are hardest to hold in the head.

Four results whose statements are short and whose content is not obvious, each
drawn from the same closed forms the proofs use. Nothing here is a sketch.

  fig_survival.png    Which velocity errors survive the flow. The exact field's
                      linear part is -(1-t)^{-1}, a contraction whose strength
                      diverges, so a perturbation only reaches the endpoint if it
                      diverges at the same rate. Left: the deviation along the
                      clock for errors growing like (1-t)^{-a}; the a = 1 curve is
                      the separatrix, flat at the error's own coefficient. Right: the
                      retained deviation at a fixed truncation against a. At any
                      finite truncation this is smooth -- the threshold is a
                      statement about the limit -- and it shows here as the crossing
                      of O(1) at exactly a = 1.

  fig_guidance.png    Classifier-free guidance cannot leave the affine hull of the
                      training set. Left: the component of the trajectory
                      orthogonal to that hull, which decays exactly like (1-t) for
                      every guidance weight -- the identity the proof turns on.
                      Right, in three dimensions because the result is about
                      dimension: atoms spanning a plane, trajectories starting off it
                      and pulled onto it whatever the guidance weight.

  fig_window.png      The bandwidth window for repeated labels. n_eff against h for
                      clusters of a given size: a plateau at the cluster size while
                      eps << h << Delta, falling to 1 below it and rising to N
                      above. The window exists exactly when clusters are tight
                      relative to their separation.

  fig_interpolant.png Why interpolant noise is inert. The flow is x_t = t x^i +
                      s_t x_0 with s_t^2 = (1-t)^2 + gamma(t)^2, and every valid
                      schedule has gamma(1) = 0, so s_1 = 0 whatever sigma is. The
                      envelope is wider in the middle and pinned at both ends.

    uv run python -m scripts.make_theory_figures

Writes: paper/figures/fig_{survival,guidance,window,interpolant}.png
"""
from __future__ import annotations

import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from scripts.figstyle import use_paper_style  # noqa: E402

use_paper_style()
# these legends sit over data and were laid out with a frame
plt.rcParams.update({"legend.frameon": True, "legend.framealpha": 0.92})

FIGS = Path("paper/figures")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
RNG = np.random.default_rng(0)


# --------------------------------------------------------------------- survival
def survival(d=4, n_steps=40000):
    """Proposition prop:survival, drawn three ways.

    The deviation has a closed form. With Delta = c (1-t)^{-a} u, |u| = 1, the
    deviation e_t = x^v_t - x^*_t obeys e' = -e/(1-t) + c(1-t)^{-a} u from e_0 = 0,
    and the integrating factor 1/(1-t) gives

        |e_t| = (c/a) ((1-t)^{1-a} - (1-t)),      |e_t| = -c (1-t) log(1-t) at a = 0,

    which is the proposition's bound attained with equality. Writing eps = 1-t, the
    trichotomy is visible in the exponent alone: eps^{1-a} -> 0 for a < 1, -> 1 at
    a = 1, -> infinity for a > 1.
    """
    def exact(eps, a, c=1.0):
        eps = np.asarray(eps, dtype=float)
        if abs(a) < 1e-12:
            return -c * eps * np.log(eps)
        return c * (eps ** (1.0 - a) - eps) / a

    def integrate(a, t_end, c=1.0):
        """The same quantity from the ODE, as a check that the closed form is right."""
        xi, x0 = RNG.normal(size=d), RNG.normal(size=d)
        u = RNG.normal(size=d); u /= np.linalg.norm(u)
        ts = 1.0 - np.geomspace(1.0, 1.0 - t_end, n_steps + 1)
        xv, xs = x0.copy(), x0.copy()
        for p_, q_ in zip(ts[:-1], ts[1:]):
            dt = q_ - p_
            xv = xv + dt * ((xi - xv) / (1 - p_) + c * u * (1 - p_) ** (-a))
            xs = xs + dt * ((xi - xs) / (1 - p_))
        return float(np.linalg.norm(xv - xs))

    fig, axes = plt.subplots(1, 3, figsize=(14.6, 4.3))

    # ---------------------------------------------------- (a) along the clock
    ax = axes[0]
    eps = np.geomspace(1.0, 1e-6, 400)
    exps = [0.0, 0.5, 0.9, 1.0, 1.1, 1.3]
    colors = [OI["sky"], OI["green"], OI["orange"], OI["black"],
              OI["vermillion"], OI["purple"]]
    for a, c in zip(exps, colors):
        ax.plot(eps, exact(eps, a), color=c, lw=2.6 if a == 1.0 else 1.5,
                label=rf"$a={a}$" + ("  (threshold)" if a == 1.0 else ""))
        # The ODE, at three points per curve: the closed form is not a fit.
        for te in (1 - 1e-2, 1 - 1e-4, 1 - 1e-6):
            ax.plot([1 - te], [integrate(a, te)], "o", ms=4.5, mfc="none",
                    mec=c, mew=1.2, zorder=5)
    ax.plot([], [], "o", ms=4.5, mfc="none", mec="0.35", mew=1.2,
            label="ODE, integrated")
    ax.axhline(1.0, color=OI["black"], ls=":", lw=1.0)
    # Say what each curve does at the endpoint, at the endpoint.
    for a, c, txt in ((1.3, OI["purple"], r"$\to\infty$"),
                      (1.0, OI["black"], r"$\to c$"),
                      (0.5, OI["green"], r"$\to 0$")):
        ax.annotate(txt, xy=(1e-6, exact(1e-6, a)), xytext=(6, 0),
                    textcoords="offset points", fontsize=10, color=c,
                    va="center", ha="left", annotation_clip=False)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.invert_xaxis()
    ax.set_ylim(1e-7, 1e3)
    ax.set_xlabel(r"$1-t$   (time remaining, decreasing $\rightarrow$)")
    ax.set_ylabel(r"deviation $|e_t|$ from the collapsed trajectory")
    ax.set_title(r"(a) an error $|\Delta|=c(1-t)^{-a}$ along the clock",
                 fontsize=10.5)
    ax.grid(alpha=0.3); ax.legend(fontsize=7.5, loc="lower left", ncol=2)

    # ------------------------------------------------- (b) the limit, as a pivot
    ax = axes[1]
    aa = np.linspace(0.0, 2.0, 401)
    deltas = [1e-2, 1e-3, 1e-4, 1e-6, 1e-8]
    greys = plt.cm.viridis(np.linspace(0.15, 0.85, len(deltas)))
    for dl, col in zip(deltas, greys):
        ax.plot(aa, [exact(dl, a) for a in aa], color=col, lw=1.8,
                label=rf"$\delta=10^{{{int(np.log10(dl))}}}$")
    ax.axvline(1.0, color=OI["black"], ls="--", lw=1.4)
    ax.plot([1.0], [1.0], "o", color=OI["black"], ms=7, zorder=6)
    ax.set_yscale("log"); ax.set_ylim(1e-9, 1e9)
    ax.annotate(r"$\rightarrow 0$", xy=(0.45, 1e-6), fontsize=13,
                color=OI["sky"], ha="center")
    ax.annotate(r"$\rightarrow \infty$", xy=(1.6, 1e6), fontsize=13,
                color=OI["vermillion"], ha="center")
    ax.annotate("every truncation\npasses through $(1,\\,c)$", xy=(1.0, 1.0),
                xytext=(1.18, 3e-5), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.8, color=OI["black"]))
    ax.set_xlabel(r"divergence exponent $a$")
    ax.set_ylabel(r"deviation retained at $t=1-\delta$")
    ax.set_title("(b) the threshold is a limit, so vary the truncation",
                 fontsize=10.5)
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="upper left", ncol=1)

    # ------------------------------------- (c) the loss form against measurement
    ax = axes[2]
    dl = 1e-3     # EXP-1's sampler truncation (eval.ode_eps)
    # Span the measured losses and no further: an extrapolated fit line over
    # three decades when the data occupies one invites a reading the data
    # does not support.
    lo = np.geomspace(0.3, 4.0, 100)
    ax.plot(lo, np.sqrt(lo * dl), color=OI["black"], lw=2.0,
            label=r"bound $\sqrt{\mathcal{L}\delta}$  ($L_\Delta=0$)")
    fs = sorted(glob.glob("results/exp1/exp1_cond_seed[0-9]/raw/metrics.csv"))
    if fs:
        m = pd.concat([pd.read_csv(f) for f in fs])
        m = m[m["group"] == "train"]
        g = m.groupby("iter")[["train_loss", "trace_cov_mean"]].mean()
        std = np.sqrt(g["trace_cov_mean"].values)
        loss = g["train_loss"].values
        it = g.index.values
        # Iterations 100 and 300 are still leaving initialisation -- data-scale
        # variance, no collapse under way -- so they are drawn but not fitted.
        fitm = it >= 1000
        ax.scatter(loss[~fitm], std[~fitm], s=44, facecolor="none",
                   edgecolor="0.55", linewidth=1.2, zorder=5,
                   label="pre-collapse (not fitted)")
        sc = ax.scatter(loss[fitm], std[fitm], c=np.log10(it[fitm]), cmap="viridis",
                        s=52, zorder=6, edgecolor="white", linewidth=0.6,
                        label="EXP-1 checkpoints (5 seeds)")
        cb = fig.colorbar(sc, ax=ax, pad=0.02)
        cb.set_label(r"$\log_{10}$ iteration", fontsize=8.5)
        cb.ax.tick_params(labelsize=7.5)
        sl, ic = np.polyfit(np.log(loss[fitm]), np.log(std[fitm]), 1)
        rr = np.corrcoef(np.log(loss[fitm]), np.log(std[fitm]))[0, 1] ** 2
        late = it >= 30000
        sl2 = np.polyfit(np.log(loss[late]), np.log(std[late]), 1)[0]
        ax.plot(lo, np.exp(ic) * lo ** sl, color=OI["vermillion"], ls="--", lw=1.6,
                label=rf"fit: slope ${sl:.3f}$, $R^2={rr:.2f}$")
        ax.axhline(1.0, color=OI["green"], ls=":", lw=1.4,
                   label=r"calibrated: $\sqrt{\mathrm{tr}\,\Sigma_{\mathrm{post}}}$")
        off = float(np.median(std[fitm] / np.sqrt(loss[fitm] * dl)))
        ax.annotate("the exponent is the prediction; the constant is not:\n"
                    f"slope ${sl:.3f}$ against $0.5$ (${sl2:.3f}$ over the last\n"
                    f"three checkpoints), offset $e^{{L_\\Delta}}\\approx{off:.0f}$",
                    xy=(0.03, 0.965), xycoords="axes fraction", fontsize=7.6,
                    ha="left", va="top",
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.8"))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.28, 4.4); ax.set_ylim(1.2e-2, 2.6)
    # Over less than a decade the default log locator lays minor labels on top of
    # each other; name the ticks.
    from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
    ax.xaxis.set_major_locator(FixedLocator([0.3, 0.5, 1.0, 2.0, 4.0]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_major_locator(FixedLocator([0.02, 0.05, 0.1, 0.3, 1.0, 2.0]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlabel(r"training loss $\mathcal{L}_i$")
    ax.set_ylabel(r"conditional std $\sqrt{\mathrm{tr}\,\mathrm{Cov}}$ retained")
    ax.set_title(r"(c) the loss form, measured: collapse is paced by $\sqrt{\mathcal{L}}$",
                 fontsize=10.5)
    ax.grid(alpha=0.3); ax.legend(fontsize=7.0, loc="lower right")

    fig.tight_layout(); fig.savefig(FIGS / "fig_survival.png", dpi=200)
    plt.close(fig)
    print("  fig_survival.png")


def guidance(N=6, d=2, n_steps=30000, t_end=1 - 1e-6):
    X = RNG.normal(size=(N, d)) * 1.5
    Y = RNG.normal(size=(N, 1))
    i, h = 2, 0.6
    y = Y[i].copy()
    ts = 1.0 - np.geomspace(1.0, 1.0 - t_end, n_steps + 1)
    def hull_basis(pts, tol=1e-9):
        """Orthonormal basis of the affine hull's *direction space*, rank-truncated.

        np.linalg.qr on a (d, N-1) matrix returns a full d x d basis whenever
        N-1 >= d, even if the differences span a proper subspace -- which makes the
        orthogonal component identically zero and turns this plot into noise over
        noise. Use the SVD and keep only the directions that are actually spanned.
        """
        B = pts[1:] - pts[0]
        U, sv, _ = np.linalg.svd(B.T, full_matrices=False)
        return pts[0], U[:, sv > tol * max(sv[0], 1.0)]

    base, Q = hull_basis(X)

    def orth(x):
        v = x - base
        return v - Q @ (Q.T @ v)

    def run(w, x0):
        x, out = x0.copy(), []
        for p, q in zip(ts[:-1], ts[1:]):
            dt = q - p
            z = (x[None, :] - p * X) / (1 - p)
            lsp = -0.5 * (z ** 2).sum(1)
            lc = lsp - 0.5 * ((y[None, :] - Y) ** 2).sum(1) / h ** 2
            wc = np.exp(lc - lc.max()); wc /= wc.sum()
            qq = np.exp(lsp - lsp.max()); qq /= qq.sum()
            m = (1 + w) * (wc @ X) - w * (qq @ X)
            x = x + dt * (m - x) / (1 - p)
            out.append(np.linalg.norm(orth(x)))
        return np.array(out), x

    # d = 2 with N = 6 spans the plane, so use a 3-d embedding for the hull picture.
    X3 = np.concatenate([X, np.zeros((N, 1))], 1)      # atoms in a plane of R^3
    base3, Q3 = hull_basis(X3)                         # rank 2, so z is orthogonal

    def run3(w, x0):
        x, out = x0.copy(), []
        for p, q in zip(ts[:-1], ts[1:]):
            dt = q - p
            z = (x[None, :] - p * X3) / (1 - p)
            lsp = -0.5 * (z ** 2).sum(1)
            lc = lsp - 0.5 * ((y[None, :] - Y) ** 2).sum(1) / h ** 2
            wc = np.exp(lc - lc.max()); wc /= wc.sum()
            qq = np.exp(lsp - lsp.max()); qq /= qq.sum()
            m = (1 + w) * (wc @ X3) - w * (qq @ X3)
            x = x + dt * (m - x) / (1 - p)
            v = x - base3
            out.append(np.linalg.norm(v - Q3 @ (Q3.T @ v)))
        return np.array(out), x

    fig = plt.figure(figsize=(11.6, 4.3))
    axes = [fig.add_subplot(1, 2, 1),
            fig.add_subplot(1, 2, 2, projection="3d")]
    x0_3 = np.array([1.2, -0.9, 1.7])                  # deliberately off the plane
    v0 = x0_3 - base3
    q0 = np.linalg.norm(v0 - Q3 @ (Q3.T @ v0))         # the true |q_0|, at t=0
    for w, c in zip((0.0, 2.0, 6.0, 15.0),
                    (OI["sky"], OI["green"], OI["orange"], OI["vermillion"])):
        qt, _ = run3(w, x0_3)
        axes[0].plot(1 - ts[1:], qt / q0, color=c, lw=1.5, label=f"$w={w:g}$")
    axes[0].plot(1 - ts[1:], 1 - ts[1:], color=OI["black"], ls="--", lw=1.4,
                 label=r"$(1-t)$, the identity")
    axes[0].set_xscale("log"); axes[0].set_yscale("log"); axes[0].invert_xaxis()
    axes[0].set_xlabel(r"$1-t$")
    axes[0].set_ylabel(r"$|q_t| / |q_0|$, component off the affine hull")
    axes[0].set_title(r"guidance cannot leave the hull: $q_t=(1-t)q_0$", fontsize=10.5)
    axes[0].grid(alpha=0.3); axes[0].legend(fontsize=8, loc="lower left")

    # The result is about dimension, so draw the dimension. The atoms lie in a
    # plane of R^3; trajectories start off it and are pulled onto it, whatever the
    # guidance weight, because the orthogonal component obeys q_t = (1-t) q_0
    # exactly. A 2-d projection cannot show that.
    ax = axes[1]
    gx = np.linspace(X3[:, 0].min() - 1, X3[:, 0].max() + 1, 2)
    gy = np.linspace(X3[:, 1].min() - 1, X3[:, 1].max() + 1, 2)
    GX, GY = np.meshgrid(gx, gy)
    ax.plot_surface(GX, GY, np.zeros_like(GX), alpha=0.16, color=OI["sky"],
                    edgecolor="none", zorder=0)
    ax.text(gx[0], gy[1], 0.05, "affine hull of the training set", fontsize=8,
            color=OI["blue"])

    def path3(w, x0):
        x, out = x0.copy(), [x0.copy()]
        for p_, q_ in zip(ts[:-1], ts[1:]):
            dt = q_ - p_
            z = (x[None, :] - p_ * X3) / (1 - p_)
            lsp = -0.5 * (z ** 2).sum(1)
            lc = lsp - 0.5 * ((y[None, :] - Y) ** 2).sum(1) / h ** 2
            wc = np.exp(lc - lc.max()); wc /= wc.sum()
            qq = np.exp(lsp - lsp.max()); qq /= qq.sum()
            m = (1 + w) * (wc @ X3) - w * (qq @ X3)
            x = x + dt * (m - x) / (1 - p_)
            out.append(x.copy())
        return np.stack(out)

    starts = np.array([[1.2, -0.9, 1.7], [-1.6, 1.1, -1.9], [0.4, 2.0, 2.3],
                       [2.2, 0.6, -1.4], [-0.9, -1.8, 1.2]])
    for w, c in zip((0.0, 15.0), (OI["sky"], OI["vermillion"])):
        for j, st in enumerate(starts):
            tr = path3(w, st)[::40]
            ax.plot(tr[:, 0], tr[:, 1], tr[:, 2], color=c, lw=1.1, alpha=0.75,
                    label=(f"trajectory, $w={w:g}$" if j == 0 else None))
            ax.scatter(*tr[-1], s=26, color=c, zorder=6)
    ax.scatter(X3[:, 0], X3[:, 1], X3[:, 2], s=42, color=OI["black"], zorder=7,
               label="training atoms")
    ax.scatter(*X3[i], marker="*", s=260, color=OI["blue"], zorder=8,
               label="conditioned atom")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_zlabel("off-hull direction", fontsize=8.5, labelpad=-8)
    ax.view_init(elev=18, azim=-58)
    ax.set_title("whatever $w$, the trajectory is pulled into the hull",
                 fontsize=10.5, pad=0)
    ax.legend(fontsize=7.2, loc="upper left", framealpha=0.9)
    fig.tight_layout(); fig.savefig(FIGS / "fig_guidance.png", dpi=200)
    plt.close(fig)
    print("  fig_guidance.png")


# ----------------------------------------------------------------------- window
def window(N=240, k=3):
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for csize, eps, c in ((6, 0.02, OI["sky"]), (20, 0.02, OI["green"]),
                          (60, 0.02, OI["orange"]), (20, 0.30, OI["vermillion"])):
        n_cl = N // csize
        centres = RNG.normal(size=(n_cl, k)) * 3.0
        Y = np.repeat(centres, csize, 0) + RNG.normal(size=(N, k)) * eps
        yq = Y[0]
        hs = np.geomspace(3e-3, 30.0, 160)
        ne = []
        for h in hs:
            lg = -0.5 * ((yq[None, :] - Y) ** 2).sum(1) / h ** 2
            w = np.exp(lg - lg.max()); w /= w.sum()
            ne.append(1.0 / (w ** 2).sum())
        ax.plot(hs, ne, color=c, lw=1.7,
                label=rf"$|C|={csize}$, $\varepsilon={eps}$")
        ax.axhline(csize, color=c, ls=":", lw=1.0, alpha=0.7)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("bandwidth $h$")
    ax.set_ylabel(r"$n_{\mathrm{eff}}$")
    ax.set_title(r"repeated labels: a plateau at $|C|$ while "
                 r"$\varepsilon\ll h\ll\Delta$", fontsize=10.5)
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(FIGS / "fig_window.png", dpi=200)
    plt.close(fig)
    print("  fig_window.png")


# ------------------------------------------------------------------ interpolant
def interpolant():
    t = np.linspace(0, 1, 400)
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.7))
    for sig, c in zip((0.0, 0.5, 1.0, 2.0),
                      (OI["black"], OI["sky"], OI["green"], OI["vermillion"])):
        s_t = np.sqrt((1 - t) ** 2 + sig ** 2 * t * (1 - t))
        axes[0].plot(t, s_t, color=c, lw=1.7, label=rf"$\sigma={sig:g}$")
        axes[1].plot(t, s_t ** 2, color=c, lw=1.7, label=rf"$\sigma={sig:g}$")
    for ax, ttl in zip(axes, (r"$s_t$: the width of the flow's own envelope",
                              r"$s_t^2=(1-t)^2+\gamma(t)^2$")):
        ax.axvline(1.0, color=OI["black"], ls=":", lw=1.0)
        ax.set_xlabel("$t$"); ax.set_title(ttl, fontsize=10.5)
        ax.grid(alpha=0.3); ax.legend(fontsize=8)
    axes[0].annotate(r"$s_1=0$ for every $\sigma$", xy=(1.0, 0.0), xytext=(0.62, 0.55),
                     arrowprops=dict(arrowstyle="->", color=OI["vermillion"], lw=1.3),
                     color=OI["vermillion"], fontsize=10)
    fig.suptitle(r"interpolant noise is inert because any valid schedule has "
                 r"$\gamma(1)=0$", fontsize=11.5, y=1.02)
    fig.tight_layout(); fig.savefig(FIGS / "fig_interpolant.png", dpi=200,
                                    bbox_inches="tight")
    plt.close(fig)
    print("  fig_interpolant.png")


if __name__ == "__main__":
    FIGS.mkdir(parents=True, exist_ok=True)
    survival()
    guidance()
    window()
    interpolant()
