"""Measure the distance to the population optimum (WORK_ORDER T5, Question B).

For each checkpoint of a run, Monte-Carlo estimate on the SAME batch:

    L(v_theta) = E|| U - v_theta(X_t, t, Ytilde) ||^2         (empirical loss)
    L(v_h*)    = E|| U - v_h*(X_t, t, Ytilde) ||^2            (irreducible)
               = E[Var(U | X_t, t, Ytilde)]                   (Prop 1)
    gap        = L(v_theta) - L(v_h*)   >= 0

v_h* is the exact conditional-mean minimiser, evaluated via kernel_field (which
uses BOTH the spatial source factor and the label kernel, eq. 8.1). For h=0 the
minimiser is exact and L(v_h*) = 0 (Prop 4b), so gap = L(v_theta) -- the quantity
already logged. The new information is at h > 0.

    uv run python scripts/measure_optimality_gap.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.kernel_theory import kernel_field  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
RUNS = [("exp1_cond_seed0", 0.0)] + [(f"p7y_h{h}_seed0", h) for h in (0.01, 0.05, 0.1, 0.5)]
B = 200_000  # MC batch for the loss estimates


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                        seed=cfg["seed"], prior_std=dc.get("prior_std", 1.0),
                                        A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    h = float(cfg["train"].get("y_noise_h", 0.0))
    return cfg, prob, X.float(), Y.float(), model, h


@torch.no_grad()
def losses_at(model, X, Y, h, gen):
    """MC estimate of L(v_theta) and L(v_h*) on one shared batch."""
    N, d = X.shape
    idx = torch.randint(0, N, (B,), generator=gen)
    x1 = X[idx]
    x0 = torch.randn(B, d, generator=gen)
    t = torch.rand(B, generator=gen)
    x_t = (1 - t)[:, None] * x0 + t[:, None] * x1
    U = x1 - x0
    y_tilde = Y[idx] + (h * torch.randn(Y[idx].shape, generator=gen) if h > 0 else 0.0)
    # L(v_theta): batch the forward pass over chunks to bound memory
    l_theta, l_star = 0.0, 0.0
    cs = 20_000
    for s in range(0, B, cs):
        e = min(s + cs, B)
        v_th = model(x_t[s:e], t[s:e], y_tilde[s:e])
        l_theta += float(((U[s:e] - v_th) ** 2).sum())
        # v_h*: exact minimiser via kernel_field per-sample query y_tilde[j]
        # (queries differ per row, so loop is unavoidable but cheap vectorised
        #  inside kernel_field over atoms). Use a sub-batch python loop.
        v_star = _vhstar_batch(x_t[s:e], t[s:e], y_tilde[s:e], X, Y, h)
        l_star += float(((U[s:e] - v_star) ** 2).sum())
    return l_theta / B, l_star / B


@torch.no_grad()
def _vhstar_batch(x, t, y_q, X, Y, h):
    """v_h*(x_j, t_j, y_q_j) with a distinct query per row.

    kernel_field assumes a single shared query; here each row has its own
    y_tilde, so we compute the (P,N) posterior directly with log-sum-exp.
    """
    x, t, y_q, Xd, Yd = (a.to(torch.float64) for a in (x, t, y_q, X, Y))
    one_m_t = (1.0 - t).clamp_min(1e-6)[:, None]
    x0 = (x[:, None, :] - t[:, None, None] * Xd[None, :, :]) / one_m_t[:, :, None]
    log_src = -0.5 * (x0 ** 2).sum(-1)                                  # (P,N), source_std=1
    if h > 0:
        log_ker = -0.5 * ((y_q[:, None, :] - Yd[None, :, :]) ** 2).sum(-1) / (h ** 2)  # (P,N)
    else:
        d2 = ((y_q[:, None, :] - Yd[None, :, :]) ** 2).sum(-1)
        log_ker = torch.full_like(d2, -1e30)
        log_ker.scatter_(1, d2.argmin(1, keepdim=True), 0.0)
    w = torch.softmax(log_src + log_ker, dim=1)                        # (P,N)
    diff = (Xd[None, :, :] - x[:, None, :]) / one_m_t[:, :, None]
    return (w[:, :, None] * diff).sum(1).float()


def main():
    all_rows = []
    for name, _ in RUNS:
        rd = ROOT / name
        cfg, prob, X, Y, model, h = rebuild(rd)
        ckdir = rd / "checkpoints"
        ckpts = sorted(int(p.stem.split("_")[1]) for p in ckdir.glob("ckpt_*.pt"))
        gen = torch.Generator().manual_seed(1234)
        for it in ckpts:
            state = torch.load(ckdir / f"ckpt_{it}.pt", map_location="cpu")
            model.load_state_dict(state["model_state"]); model.eval()
            lt, ls = losses_at(model, X, Y, h, gen)
            gap = lt - ls
            all_rows.append({"run": name, "h": h, "iter": it,
                             "L_theta": lt, "L_star": ls, "gap": gap})
            print(f"  {name:22s} it={it:>7d}  L(v_θ)={lt:.4f}  L(v_h*)={ls:.4f}  gap={gap:.4f}")

    df = pd.DataFrame(all_rows)
    out = ROOT / "_theory" / "raw"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "optimality_gap.csv", index=False)
    neg = df[df.gap < -1e-3]
    if len(neg):
        print(f"\nWARNING: {len(neg)} rows with gap < 0 (should be >=0):")
        print(neg.to_string(index=False))
    else:
        print("\nAll gaps >= 0 (as required).")

    figdir = ROOT / "_theory" / "figures"; figdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, g in df.groupby("run"):
        ax.plot(g["iter"], g["gap"], "o-", label=f"{name} (h={g['h'].iloc[0]})")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("iteration"); ax.set_ylabel("optimality gap L(v_θ) − L(v_h*)")
    ax.set_title("Distance to the population optimum"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(figdir / "optimality_gap.png", dpi=140)
    print(f"wrote {out / 'optimality_gap.csv'} and figure")


if __name__ == "__main__":
    main()
