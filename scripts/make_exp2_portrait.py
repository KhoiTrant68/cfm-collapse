"""EXP-2 in trajectory space: the collapse picks the posterior mode that holds x^i.

Laid out as Delay Flow Matching (ICLR 2026, Fig. 2) draws its toy problems: for each
condition, the source draws (blue), the paths they follow (thin grey), and where they
land (vermillion), over the closed-form bimodal posterior, with one legend for the whole
figure. Two rows -- an early checkpoint that is still a posterior sampler and the last
checkpoint -- so the same source draws can be seen going to both modes and then to one.

    uv run python -m scripts.make_exp2_portrait

Writes paper/figures/fig_exp2_portrait.png.

The share of late samples landing in the mode that contains x^i is what the caption of
the EXP-2 figure quotes (0.999 / 0.766 / 0.990 / 1.000, from 800 draws per condition).
It is recomputed here from 20000 draws and asserted to agree with the quoted value to
within four binomial standard errors of an 800-draw estimate, so the figure cannot
drift from the text; the panels themselves carry no number, because a second draw of
the same 800 samples would print a different third decimal than the caption.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from scripts.figstyle import (COLORS, flow_model, panel_tag, portrait_axis, save,
                              shared_legend, trajectory_bundle, use_paper_style)
from src.flows.ode_solver import generate_samples
from src.models.mlp_velocity import build_model
from src.problems.gmm import GMMProblem
from src.utils import load_yaml

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse

RUN = Path("results/exp2/exp2b_gmm_seed0_mr")
EARLY, LATE = 1000, 300000
N_COND = 4
M = 800           # samples behind the reported shares
M_CHECK = 20000   # samples behind the recomputed shares
N_PATHS = 70      # paths actually drawn
REPORTED_SHARES = (0.999, 0.766, 0.990, 1.000)   # main.tex, EXP-2 qualitative figure


def load(cfg, prob, it):
    m = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    m.load_state_dict(torch.load(RUN / "checkpoints" / f"ckpt_{it}.pt",
                                 map_location="cpu")["model_state"])
    m.eval()
    return m


def mode_of_atom(x_i: np.ndarray, mus: np.ndarray, w: np.ndarray) -> int:
    """The significant posterior mode nearest to the memorised atom."""
    sig = np.where(w > 0.1)[0]
    return int(sig[np.argmin(np.linalg.norm(mus[sig] - x_i, axis=1))])


def share_on_mode(samples: np.ndarray, mus: np.ndarray, k: int) -> float:
    assign = np.argmin(((samples[:, None, :] - mus[None]) ** 2).sum(-1), axis=1)
    return float((assign == k).mean())


def draw_posterior(ax, w, mus, covs) -> None:
    """Each significant mode as an ellipse at 1 and 2 sd, faded by nothing but its weight."""
    for wk, mu, cov in zip(w, mus, covs):
        if wk <= 0.1:
            continue
        vals, vecs = np.linalg.eigh(np.asarray(cov, dtype=float))
        ang = np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1]))
        for kk, fill in ((2.0, True), (1.0, False)):
            ax.add_patch(Ellipse(mu, 2 * kk * np.sqrt(vals[-1]), 2 * kk * np.sqrt(vals[0]),
                                 angle=ang, fill=fill, facecolor=COLORS["source"],
                                 alpha=0.22 if fill else 1.0, edgecolor=COLORS["reference"],
                                 lw=1.4, zorder=0))


def main() -> None:
    use_paper_style()
    cfg = load_yaml(RUN / "config.yaml")
    dc = cfg["data"]
    prob = GMMProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                             seed=cfg["seed"], mode_scale=dc.get("mode_scale", 2.0),
                             mode_std=dc.get("mode_std", 0.5),
                             A_kind=dc.get("A_kind", "project_x0"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    models = {it: load(cfg, prob, it) for it in (EARLY, LATE)}
    idx = sorted(set(torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()))
    src_std = dc.get("source_std", 1.0)

    # the paper's shares, recomputed from many more draws
    gen = torch.Generator().manual_seed(999)
    shares = {}
    for i in idx:
        for it in (EARLY, LATE):
            s = generate_samples(models[it], M_CHECK, 2, Y[i], source_std=src_std,
                                 n_steps=100, method="rk4", generator=gen).numpy()
            w, mus, _ = prob.posterior_params(Y[i])
            k = mode_of_atom(X[i].numpy(), mus.numpy(), w.numpy())
            shares[(i, it)] = share_on_mode(s, mus.numpy(), k)
    late = tuple(round(shares[(i, LATE)], 3) for i in idx)
    early = tuple(round(shares[(i, EARLY)], 3) for i in idx)
    print(f"late share on the x^i mode ({M_CHECK} draws):", late, " quoted:", REPORTED_SHARES)
    print("early share (the paper says about 0.5):", early)
    for a, b in zip(late, REPORTED_SHARES):
        tol = 4 * np.sqrt(b * (1 - b) / M) + 0.004
        assert abs(a - b) < tol, "the shares the paper quotes no longer match the checkpoints"

    x0 = np.random.default_rng(0).normal(size=(N_PATHS, 2)) * src_std
    fig, axes = plt.subplots(2, len(idx), figsize=(2.55 * len(idx), 5.35))
    for c, i in enumerate(idx):
        w, mus, covs = prob.posterior_params(Y[i])
        xi = X[i].numpy()
        for r, it in enumerate((EARLY, LATE)):
            ax = axes[r][c]
            paths = flow_model(models[it], x0, Y[i], n_steps=200)
            draw_posterior(ax, w.numpy(), mus.numpy(), covs.numpy())
            trajectory_bundle(ax, paths, end_size=22)
            ax.scatter([xi[0]], [xi[1]], marker="*", s=150, color=COLORS["atom"],
                       edgecolors="white", linewidths=0.8, zorder=6)
            portrait_axis(ax)
            ax.set_xlim(-3.6, 3.6)
            ax.set_ylim(-3.6, 3.6)
            if r == 0:
                ax.set_title(f"$y={float(Y[i]):+.2f}$", fontsize=10.5, pad=6)
            if c == 0:
                ax.set_ylabel("$10^3$ iterations" if it == EARLY else "$3{\\cdot}10^5$ iterations",
                              fontsize=10)
    for a, letter in zip(axes[:, 0], "ab"):
        panel_tag(a, letter, dx=-0.16)
    fig.subplots_adjust(top=0.90, bottom=0.02, left=0.06, right=0.995, hspace=0.06,
                        wspace=0.04)
    shared_legend(fig, [("source $x_0$", "marker", COLORS["source"]),
                        ("path", "line", COLORS["path"]),
                        ("generated", "marker", COLORS["generated"]),
                        ("training atom $x^i$", "marker", COLORS["atom"]),
                        ("true posterior modes", "patch", COLORS["reference"])],
                  y=1.0, ncol=5)
    save(fig, "fig_exp2_portrait.png")


if __name__ == "__main__":
    main()
