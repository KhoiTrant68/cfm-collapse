"""Numerically verify the label-smoothing = kernel-regression theory (§2.X).

Tests two central claims on the *actual* y-noise-trained checkpoints (p7y_h*):

  (†)  v_theta(x,t,y^i)  matches  v_h^*(x,t,y^i)  from
           v_h^*(x,t,y) = sum_j w_j (x^j - x)/(1-t),
           w_j ∝ π0((x - t x^j)/(1-t)) · K_h(y - y^j)
       *better* than it matches the single-example collapse field (★).

  (‡)  the empirical assignment of generated samples to nearest training
       point x^j reproduces the kernel mixture weights
           p_j(y^i) ∝ K_h(y^i - y^j).

Uses log-sum-exp throughout for numerical stability.

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
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.ode_solver import generate_samples  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")


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


def kernel_field(x, t, y_q, X, Y, h, source_std=1.0):
    """v_h^*(x,t,y_q) via (†) with log-sum-exp. x:(P,d), t:(P,), y_q:(k,)."""
    P = x.shape[0]
    one_m_t = (1.0 - t).clamp_min(1e-6)[:, None]                 # (P,1)
    x0 = (x[:, None, :] - t[:, None, None] * X[None, :, :]) / one_m_t[:, :, None]  # (P,N,d)
    log_src = -0.5 * (x0 ** 2).sum(-1) / (source_std ** 2)       # (P,N)
    if h > 0:
        log_ker = -0.5 * ((y_q[None, :] - Y) ** 2).sum(-1) / (h ** 2)  # (N,)
    else:  # h=0: point mass on nearest label (Regime I)
        d2 = ((y_q[None, :] - Y) ** 2).sum(-1)
        log_ker = torch.full_like(d2, -1e30); log_ker[d2.argmin()] = 0.0
    log_w = log_src + log_ker[None, :]                          # (P,N)
    w = torch.softmax(log_w, dim=1)                            # (P,N)
    diff = (X[None, :, :] - x[:, None, :]) / one_m_t[:, :, None]  # (P,N,d)
    return (w[:, :, None] * diff).sum(dim=1)                    # (P,d)


def star_field(x, t, x_i):
    return (x_i[None, :] - x) / (1.0 - t).clamp_min(1e-6)[:, None]


@torch.no_grad()
def verify_field(prob, X, Y, model, h, n_cond=12, P=1500, t_max=0.95, seed=0):
    g = torch.Generator().manual_seed(seed)
    idx = sorted(set(torch.linspace(0, X.shape[0] - 1, n_cond).round().long().tolist()))
    rel_tri, rel_star = [], []
    for i in idx:
        x_i, y_i = X[i], Y[i]
        x0 = torch.randn(P, prob.d, generator=g)
        t = t_max * torch.rand(P, generator=g)
        x = (1 - t)[:, None] * x0 + t[:, None] * x_i[None, :]   # on-manifold of cond i
        v_theta = model(x, t, y_i[None, :].expand(P, -1))
        v_tri = kernel_field(x, t, y_i, X, Y, h)
        v_star = star_field(x, t, x_i)
        rel_tri.append(float((torch.linalg.norm(v_theta - v_tri, dim=1) /
                              torch.linalg.norm(v_tri, dim=1).clamp_min(1e-8)).mean()))
        rel_star.append(float((torch.linalg.norm(v_theta - v_star, dim=1) /
                               torch.linalg.norm(v_star, dim=1).clamp_min(1e-8)).mean()))
    return torch.tensor(rel_tri).mean().item(), torch.tensor(rel_star).mean().item()


@torch.no_grad()
def verify_mixture(prob, X, Y, model, h, cond_idx, M=2000, seed=0):
    g = torch.Generator().manual_seed(seed)
    y_i = Y[cond_idx]
    samples = generate_samples(model, M, prob.d, y_i, source_std=1.0, n_steps=100,
                               method="rk4", generator=g)
    # assign each sample to nearest training point
    d2 = ((samples[:, None, :] - X[None, :, :]) ** 2).sum(-1)   # (M,N)
    assign = d2.argmin(1)
    q = torch.bincount(assign, minlength=X.shape[0]).float() / M
    # predicted kernel weights p_j ∝ K_h(y_i - y_j)
    logp = -0.5 * ((y_i[None, :] - Y) ** 2).sum(-1) / (h ** 2)
    p = torch.softmax(logp, dim=0)
    tv = 0.5 * float((q - p).abs().sum())
    return samples, q, p, tv


def main():
    print(f"{'h':>6} | {'rel_err v_theta vs (†)':>24} | {'rel_err v_theta vs (★)':>24}")
    print("-" * 62)
    runs = [("exp1_cond_seed0", 0.0), ("p7y_h0.05_seed0", 0.05),
            ("p7y_h0.1_seed0", 0.1), ("p7y_h0.5_seed0", 0.5)]
    results = []
    for name, _ in runs:
        rd = ROOT / name
        if not (rd / "checkpoints" / "ckpt_200000.pt").exists():
            continue
        cfg, prob, X, Y, model, h = rebuild(rd)
        rt, rs = verify_field(prob, X, Y, model, h)
        results.append((h, rt, rs, prob, X, Y, model))
        print(f"{h:>6.2f} | {rt:>24.4f} | {rs:>24.4f}")

    # mixture check + figure on the largest-h model (clearest multi-atom mixture)
    h, rt, rs, prob, X, Y, model = max(results, key=lambda r: r[0])
    # pick a condition with several neighbors within ~h
    cond = int(torch.linspace(0, X.shape[0] - 1, 12).round().long()[5])
    samples, q, p, tv = verify_mixture(prob, X, Y, model, h, cond)
    print(f"\n(‡) mixture check @ h={h}, condition i={cond}: "
          f"TV(empirical assignment, kernel weights) = {tv:.4f}")

    out = ROOT / "_theory" / "figures"; out.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.4))

    # (a) rel-err bars across h
    hs = [r[0] for r in results]
    ax1.plot(hs, [r[1] for r in results], "o-", color="C0", label="v_θ vs (†) kernel field")
    ax1.plot(hs, [r[2] for r in results], "s--", color="C3", label="v_θ vs (★) collapse field")
    ax1.set_xlabel("label-noise bandwidth h"); ax1.set_ylabel("relative L2 velocity error")
    ax1.set_title("(†) learned field matches kernel minimizer"); ax1.legend(); ax1.grid(alpha=0.3)

    # (b) empirical vs predicted mixture weights (top training points)
    topk = torch.topk(p, k=min(10, len(p))).indices
    xpos = range(len(topk))
    ax2.bar([i - 0.2 for i in xpos], p[topk], width=0.4, label="predicted p_j ∝ K_h", color="C0")
    ax2.bar([i + 0.2 for i in xpos], q[topk], width=0.4, label="empirical (generated)", color="C1")
    ax2.set_xticks(list(xpos)); ax2.set_xticklabels([int(j) for j in topk], fontsize=7)
    ax2.set_xlabel("training index j (top weights)"); ax2.set_ylabel("weight")
    ax2.set_title(f"(‡) mixture weights, h={h} (TV={tv:.3f})"); ax2.legend()

    # (c) d=2 scatter: samples + training points sized by predicted weight
    ax3.scatter(samples[:, 0], samples[:, 1], s=5, alpha=0.15, color="C1", label="generated")
    sizes = 20 + 600 * (p / p.max())
    ax3.scatter(X[:, 0], X[:, 1], s=sizes, facecolor="none", edgecolor="C0",
                linewidths=1.2, label="train pts (size ∝ p_j)")
    ax3.scatter([X[cond, 0]], [X[cond, 1]], marker="*", s=180, color="gold",
                edgecolor="k", zorder=5, label="x^i (own)")
    ax3.set_title("generated samples land on kernel-weighted train pts")
    ax3.legend(fontsize=7); ax3.set_aspect("equal", "datalim"); ax3.grid(alpha=0.3)

    fig.suptitle("Numerical verification of label-smoothing = kernel regression (†)/(‡)")
    fig.tight_layout(); fig.savefig(out / "kernel_theory_verification.png", dpi=140)
    print(f"wrote {out / 'kernel_theory_verification.png'}")


if __name__ == "__main__":
    main()
