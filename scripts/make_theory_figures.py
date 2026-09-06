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

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIGS = Path("paper/figures")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
RNG = np.random.default_rng(0)


# --------------------------------------------------------------------- survival
def survival(d=4, n_steps=120000, t_end=1 - 1e-5):
    xi, x0 = RNG.normal(size=d), RNG.normal(size=d)
    u = RNG.normal(size=d); u /= np.linalg.norm(u)
    ts = 1.0 - np.geomspace(1.0, 1.0 - t_end, n_steps + 1)

    def run(a):
        xv, xs, out = x0.copy(), x0.copy(), []
        for p, q in zip(ts[:-1], ts[1:]):
            dt = q - p
            xv = xv + dt * ((xi - xv) / (1 - p) + u * (1 - p) ** (-a))
            xs = xs + dt * ((xi - xs) / (1 - p))
            out.append(np.linalg.norm(xv - xs))
        return np.array(out)

    exps = [0.0, 0.5, 0.9, 1.0, 1.1, 1.3]
    colors = [OI["sky"], OI["green"], OI["orange"], OI["black"],
              OI["vermillion"], OI["purple"]]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    finals = []
    for a, c in zip(exps, colors):
        e = run(a)
        finals.append(e[-1])
        axes[0].plot(1 - ts[1:], e, color=c, lw=2.0 if a == 1.0 else 1.4,
                     label=rf"$a={a}$" + (r"  (threshold)" if a == 1.0 else ""))
    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].invert_xaxis()
    axes[0].set_xlabel(r"$1-t$   (time remaining, decreasing $\rightarrow$)")
    axes[0].set_ylabel(r"deviation $|e_t|$ from the collapsed trajectory")
    axes[0].set_title(r"error $|\Delta|\propto(1-t)^{-a}$: what reaches the endpoint",
                      fontsize=10.5)
    axes[0].grid(alpha=0.3); axes[0].legend(fontsize=8, loc="lower left")

    fine = np.linspace(0.0, 1.4, 29)
    vals = [run(a)[-1] for a in fine]
    axes[1].plot(fine, vals, "o-", ms=3.5, color=OI["blue"], lw=1.5)
    axes[1].axvline(1.0, color=OI["black"], ls="--", lw=1.2,
                    label=r"$a=1$: the field's own rate")
    axes[1].set_yscale("log")
    axes[1].set_xlabel(r"divergence exponent $a$")
    axes[1].set_ylabel(r"retained deviation at $t=1-10^{-5}$")
    axes[1].set_title("the threshold is exactly the field's rate", fontsize=10.5)
    axes[1].grid(alpha=0.3); axes[1].legend(fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(FIGS / "fig_survival.png", dpi=200)
    plt.close(fig)
    print("  fig_survival.png")


# --------------------------------------------------------------------- guidance
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
