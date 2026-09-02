"""EXP-2 money figure: for a few training conditions, show generated samples at
an early vs late checkpoint over the bimodal posterior, with the two posterior
mode means and the memorized training point marked.

    uv run python scripts/visualize_gmm_2d.py --run results/exp2/exp2_gmm_seed0 \
        --early 1000 --late 200000 --n-conditions 4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.ode_solver import generate_samples  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.gmm import GMMProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--early", type=int, default=1000)
    ap.add_argument("--late", type=int, default=200000)
    ap.add_argument("--n-conditions", type=int, default=4)
    ap.add_argument("--M", type=int, default=800)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run = Path(args.run)
    cfg = load_yaml(run / "config.yaml")
    dc = cfg["data"]
    prob = GMMProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
                             mode_scale=dc.get("mode_scale", 2.0), mode_std=dc.get("mode_std", 0.5),
                             A_kind=dc.get("A_kind", "project_x0"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)

    def load_model(it):
        m = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
        m.load_state_dict(torch.load(run / "checkpoints" / f"ckpt_{it}.pt", map_location="cpu")["model_state"])
        m.eval(); return m

    me, ml = load_model(args.early), load_model(args.late)
    idx = sorted(set(torch.linspace(0, X.shape[0]-1, args.n_conditions).round().long().tolist()))
    gen = torch.Generator().manual_seed(999)

    fig, axes = plt.subplots(1, len(idx), figsize=(4.0*len(idx), 4.2), squeeze=False)
    for c, i in enumerate(idx):
        ax = axes[0][c]; y_i = Y[i]; x_i = X[i].numpy()
        se = generate_samples(me, args.M, 2, y_i, source_std=dc.get("source_std", 1.0),
                              n_steps=100, method="rk4", generator=gen).numpy()
        sl = generate_samples(ml, args.M, 2, y_i, source_std=dc.get("source_std", 1.0),
                              n_steps=100, method="rk4", generator=gen).numpy()
        w, mus, _ = prob.posterior_params(y_i)
        ax.scatter(se[:, 0], se[:, 1], s=6, alpha=0.2, color="C0", label=f"early it={args.early}")
        ax.scatter(sl[:, 0], sl[:, 1], s=6, alpha=0.3, color="C3", label=f"late it={args.late}")
        for kk in range(mus.shape[0]):
            if w[kk] > 0.1:
                mm = mus[kk].numpy()
                ax.scatter([mm[0]], [mm[1]], marker="o", s=120, facecolor="none",
                           edgecolor="k", lw=1.5, zorder=5)
        ax.scatter([x_i[0]], [x_i[1]], marker="*", s=200, color="gold", edgecolor="k", zorder=6,
                   label="x^i (train)")
        ax.set_title(f"y={float(y_i):+.2f}"); ax.grid(alpha=0.3)
        if c == 0:
            ax.legend(fontsize=7)
    fig.suptitle("EXP-2 — selective memorization: late samples concentrate on the "
                 "posterior mode holding x^i and abandon the other")
    fig.tight_layout()
    out = args.out or str(run / "figures" / "gmm_collapse_2d.png")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140); print(f"wrote {out}")


if __name__ == "__main__":
    main()
