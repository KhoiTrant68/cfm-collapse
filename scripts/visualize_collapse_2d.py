"""2D visualization of posterior collapse (only for d=2 runs).

For a handful of training conditions y^i, overlay:
  - the analytic Gaussian posterior (mean + covariance ellipse),
  - the true training point x^i,
  - samples generated at an EARLY checkpoint (still ~Bayesian),
  - samples generated at a LATE checkpoint (collapsed onto x^i).

This is the "money figure": it shows that overtraining turns a correct posterior
sampler into a delta at the memorized training point.

Usage
-----
    uv run python scripts/visualize_collapse_2d.py \
        --run results/exp1/exp1_cond_seed0 --early 1000 --late 200000 \
        --n-conditions 4 --out results/exp1/_analysis_seed0/figures/collapse_2d.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.ode_solver import generate_samples  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402


def cov_ellipse(ax, mean, cov, n_std=2.0, **kw):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    theta = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * n_std * np.sqrt(np.maximum(vals, 1e-12))
    from matplotlib.patches import Ellipse
    e = Ellipse(xy=mean, width=w, height=h, angle=theta, fill=False, **kw)
    ax.add_patch(e)


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(
        d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
        prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"),
    )
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    return cfg, prob, X, Y


def load_model(cfg, prob, ckpt_path):
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    state = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(state["model_state"])
    model.eval()
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--early", type=int, default=1000)
    ap.add_argument("--late", type=int, default=200000)
    ap.add_argument("--n-conditions", type=int, default=4)
    ap.add_argument("--M", type=int, default=600)
    ap.add_argument("--zoom", type=float, default=0.4,
                    help="half-width of the per-panel inset window around x^i")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run_dir = Path(args.run)
    cfg, prob, X, Y = rebuild(run_dir)
    assert prob.d == 2, "visualize_collapse_2d only supports d=2"

    m_early = load_model(cfg, prob, run_dir / "checkpoints" / f"ckpt_{args.early}.pt")
    m_late = load_model(cfg, prob, run_dir / "checkpoints" / f"ckpt_{args.late}.pt")

    idx = torch.linspace(0, X.shape[0] - 1, args.n_conditions).round().long().tolist()
    idx = sorted(set(idx))
    gen = torch.Generator().manual_seed(12345)

    ncol = len(idx)
    fig, axes = plt.subplots(1, ncol, figsize=(4.0 * ncol, 4.2), squeeze=False)
    cov = prob.Sigma_post.numpy()

    for col, i in enumerate(idx):
        ax = axes[0][col]
        y_i = Y[i]
        x_i = X[i].numpy()
        mu = prob.posterior_mean(y_i).numpy()

        s_e = generate_samples(m_early, args.M, 2, y_i, source_std=cfg["data"].get("source_std", 1.0),
                               n_steps=100, method="rk4", generator=gen).numpy()
        s_l = generate_samples(m_late, args.M, 2, y_i, source_std=cfg["data"].get("source_std", 1.0),
                               n_steps=100, method="rk4", generator=gen).numpy()

        ax.scatter(s_e[:, 0], s_e[:, 1], s=6, alpha=0.25, color="C0",
                   label=f"early (it={args.early})")
        ax.scatter(s_l[:, 0], s_l[:, 1], s=8, alpha=0.5, color="C3", zorder=4,
                   label=f"late (it={args.late})")
        cov_ellipse(ax, mu, cov, n_std=2.0, edgecolor="k", lw=1.5, ls="--",
                    label="posterior 2σ")
        ax.scatter([mu[0]], [mu[1]], marker="+", s=140, color="k", label="μ_post")
        # hollow star so a fully collapsed red cluster underneath stays visible
        ax.scatter([x_i[0]], [x_i[1]], marker="*", s=220, facecolor="none",
                   edgecolor="goldenrod", lw=1.6, zorder=6, label="x^i (train)")
        ax.set_title(f"condition i={i}")
        ax.set_aspect("equal", "datalim")
        if col == 0:
            ax.legend(fontsize=7, loc="upper left")
        ax.grid(alpha=0.3)

        # Late collapse is often far tighter than the posterior scale (trace(Cov)
        # can reach ~1e-4), so the red cloud is a sub-pixel dot on the main axes.
        # An inset zoomed to the late cluster is what actually shows the collapse.
        tr_cov = float(s_l.var(axis=0).sum())
        half = args.zoom  # fixed window so panels are directly comparable
        axin = ax.inset_axes([0.56, 0.04, 0.42, 0.42])
        axin.scatter(s_l[:, 0], s_l[:, 1], s=8, alpha=0.5, color="C3", zorder=4)
        axin.scatter([x_i[0]], [x_i[1]], marker="*", s=200, facecolor="none",
                     edgecolor="goldenrod", lw=1.6, zorder=6)
        axin.set_xlim(x_i[0] - half, x_i[0] + half)
        axin.set_ylim(x_i[1] - half, x_i[1] + half)
        axin.set_xticks([]); axin.set_yticks([])
        for sp in axin.spines.values():
            sp.set_edgecolor("0.4")
        axin.text(0.04, 0.04, f"zoom ±{half:g}\ntr Cov={tr_cov:.1e}",
                  transform=axin.transAxes, fontsize=6.5, va="bottom", ha="left",
                  bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75))

    fig.suptitle("Posterior collapse onto the memorized training point (d=2)")
    fig.tight_layout()
    out = args.out or str(run_dir / "figures" / "collapse_2d.png")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
