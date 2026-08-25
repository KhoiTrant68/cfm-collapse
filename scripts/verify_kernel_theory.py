"""Numerically verify the label-smoothing = kernel-regression theory.

Tests two central claims of docs/THEORY.md Part B on the *actual* y-noise-trained
checkpoints (p7y_h*), across all available seeds:

  (Prop 8, eq. 8.1)  v_theta(x,t,y^i)  matches the kernel minimiser v_h^*
       (kernel_field) *better* than the single-example collapse field (star).

  (Thm 10, eq. 10.1) the empirical assignment of generated samples to their
       nearest training point reproduces the label-kernel mixture weights
       p_j(y^i) proportional to K_h(y^i - y^j).

Outputs:
    results/exp1/_theory/raw/kernel_verification.csv          (per h x seed)
    results/exp1/_theory/figures/kernel_theory_verification.png

    uv run python scripts/verify_kernel_theory.py
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

from src.flows.interpolants import closed_form_velocity  # noqa: E402
from src.flows.ode_solver import generate_samples  # noqa: E402
from src.metrics.kernel_theory import kernel_field, kernel_weights, n_eff  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
HS = [0.01, 0.05, 0.1, 0.5]
SEEDS = [0, 1, 2, 3, 4]


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                        seed=cfg["seed"], prior_std=dc.get("prior_std", 1.0),
                                        A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    state = torch.load(run_dir / "checkpoints" / "ckpt_200000.pt", map_location="cpu")
    model.load_state_dict(state["model_state"]); model.eval()
    h = float(cfg["train"].get("y_noise_h", 0.0))
    return cfg, prob, X.float(), Y.float(), model, h


@torch.no_grad()
def verify_field(prob, X, Y, model, h, n_cond=12, P=1500, t_max=0.95, seed=0):
    """Relative L2 error of v_theta vs (8.1) kernel field vs (star) collapse field."""
    g = torch.Generator().manual_seed(seed)
    idx = sorted(set(torch.linspace(0, X.shape[0] - 1, n_cond).round().long().tolist()))
    rel_tri, rel_star = [], []
    for i in idx:
        x_i, y_i = X[i], Y[i]
        x0 = torch.randn(P, prob.d, generator=g)
        t = t_max * torch.rand(P, generator=g)
        x = (1 - t)[:, None] * x0 + t[:, None] * x_i[None, :]
        v_theta = model(x, t, y_i[None, :].expand(P, -1))
        v_tri = kernel_field(x, t, y_i, X, Y, h).float()
        v_star = closed_form_velocity(x, t, x_i).float()
        rel_tri.append(float((torch.linalg.norm(v_theta - v_tri, dim=1) /
                              torch.linalg.norm(v_tri, dim=1).clamp_min(1e-8)).mean()))
        rel_star.append(float((torch.linalg.norm(v_theta - v_star, dim=1) /
                               torch.linalg.norm(v_star, dim=1).clamp_min(1e-8)).mean()))
    return float(np.mean(rel_tri)), float(np.mean(rel_star))


@torch.no_grad()
def verify_mixture(prob, X, Y, model, h, cond_idx, M=2000, seed=0):
    g = torch.Generator().manual_seed(seed)
    y_i = Y[cond_idx]
    samples = generate_samples(model, M, prob.d, y_i, source_std=1.0, n_steps=100,
                               method="rk4", generator=g)
    d2 = ((samples[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    assign = d2.argmin(1)
    q = torch.bincount(assign, minlength=X.shape[0]).float() / M
    p = kernel_weights(y_i, Y, h).float()
    tv = 0.5 * float((q - p).abs().sum())
    return samples, q, p, tv


def main():
    rows = []
    cache = {}  # (h, seed) -> tensors for the figure
    print(f"{'h':>5} {'seed':>4} | {'rel_err vs kernel (8.1)':>22} | "
          f"{'rel_err vs star':>16} | {'TV mixture (10.1)':>16} | {'n_eff':>6}")
    print("-" * 82)
    for h in HS:
        for s in SEEDS:
            rd = ROOT / f"p7y_h{h}_seed{s}"
            if not (rd / "checkpoints" / "ckpt_200000.pt").exists():
                continue
            cfg, prob, X, Y, model, hh = rebuild(rd)
            rt, rs = verify_field(prob, X, Y, model, hh)
            cond = int(torch.linspace(0, X.shape[0] - 1, 12).round().long()[5])
            samples, q, p, tv = verify_mixture(prob, X, Y, model, hh, cond)
            neff = n_eff(p)
            rows.append({"h": hh, "seed": cfg["seed"], "rel_err_vs_kernel": rt,
                         "rel_err_vs_star": rs, "tv_mixture": tv, "n_eff": neff})
            cache[(h, s)] = (samples, q, p, X, cond, tv)
            print(f"{h:>5} {s:>4} | {rt:>22.4f} | {rs:>16.4f} | {tv:>16.4f} | {neff:>6.1f}")

    df = pd.DataFrame(rows)
    out_raw = ROOT / "_theory" / "raw"; out_raw.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_raw / "kernel_verification.csv", index=False)

    print("\n=== summary (mean +/- std over seeds) ===")
    print(f"{'h':>5} | {'rel_err vs kernel':>18} | {'rel_err vs star':>18} | {'TV mixture':>14}")
    summ = []
    
    for h, gdf in df.groupby("h"):
        rk_m, rk_s = gdf["rel_err_vs_kernel"].mean(), gdf["rel_err_vs_kernel"].std(ddof=0)
        rs_m, rs_s = gdf["rel_err_vs_star"].mean(), gdf["rel_err_vs_star"].std(ddof=0)
        tv_m, tv_s = gdf["tv_mixture"].mean(), gdf["tv_mixture"].std(ddof=0)
        summ.append((h, rk_m, rk_s, rs_m, rs_s, tv_m, tv_s))
        print(f"{h:>5} | {rk_m:>8.3f} +/-{rk_s:>6.3f} | {rs_m:>8.3f} +/-{rs_s:>6.3f} | "
              f"{tv_m:>6.3f} +/-{tv_s:>5.3f}")

    # ---- figure: use the largest-h, lowest-seed run that actually ran (clearest multi-atom mixture) ----
    out = ROOT / "_theory" / "figures"; out.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.4))

    hs = [t[0] for t in summ]
    ax1.errorbar(hs, [t[1] for t in summ], yerr=[t[2] for t in summ], fmt="o-",
                 color="C0", capsize=3, label="v_θ vs kernel field (8.1)")
    ax1.errorbar(hs, [t[3] for t in summ], yerr=[t[4] for t in summ], fmt="s--",
                 color="C3", capsize=3, label="v_θ vs collapse field (★)")
    ax1.set_xlabel("label-noise bandwidth h"); ax1.set_ylabel("relative L2 velocity error")
    ax1.set_title("(8.1) learned field matches kernel minimiser")
    ax1.legend(); ax1.grid(alpha=0.3)

    fig_seed = next(s for s in SEEDS if (0.5, s) in cache)
    samples, q, p, X, cond, tv = cache[(0.5, fig_seed)]
    topk = torch.topk(p, k=min(10, len(p))).indices
    xpos = range(len(topk))
    ax2.bar([i - 0.2 for i in xpos], p[topk], width=0.4, label="predicted p_j ∝ K_h", color="C0")
    ax2.bar([i + 0.2 for i in xpos], q[topk], width=0.4, label="empirical (generated)", color="C1")
    ax2.set_xticks(list(xpos)); ax2.set_xticklabels([int(j) for j in topk], fontsize=7)
    ax2.set_xlabel("training index j (top weights)"); ax2.set_ylabel("weight")
    ax2.set_title(f"(10.1) mixture weights, h=0.5 (TV={tv:.3f})"); ax2.legend()

    ax3.scatter(samples[:, 0], samples[:, 1], s=5, alpha=0.15, color="C1", label="generated")
    sizes = 20 + 600 * (p / p.max())
    ax3.scatter(X[:, 0], X[:, 1], s=sizes, facecolor="none", edgecolor="C0",
                linewidths=1.2, label="train pts (size ∝ p_j)")
    ax3.scatter([X[cond, 0]], [X[cond, 1]], marker="*", s=180, color="gold",
                edgecolor="k", zorder=5, label="x^i (own)")
    ax3.set_title("generated samples land on kernel-weighted train pts")
    ax3.legend(fontsize=7); ax3.set_aspect("equal", "datalim"); ax3.grid(alpha=0.3)

    fig.suptitle("Numerical verification of label-smoothing = kernel regression (Prop 8 / Thm 10)")
    fig.tight_layout(); fig.savefig(out / "kernel_theory_verification.png", dpi=140)
    print(f"\nwrote {out_raw / 'kernel_verification.csv'} and {out / 'kernel_theory_verification.png'}")


if __name__ == "__main__":
    main()
