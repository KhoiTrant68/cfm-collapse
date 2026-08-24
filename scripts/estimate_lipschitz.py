"""Estimate Lip_x v_theta and compare the Cor-21 floor d/(3L) to L_trained.

Two estimates (WORK_ORDER T6):
  * Lower bound (empirical): largest singular value of the input-Jacobian
    d v_theta / d x at points sampled on the interpolation manifold, per t-slice
    t in {0.5, 0.9, 0.99, 0.999}. Report L(t), not just max_t.
  * Upper bound (crude): product of spectral norms of the linear layers
    (a global, t-independent bound).

Corollary 21 gives inf_{Lip_x v <= L} L_0(v) >= d/(3L). We report d/(3L(t))
against the trained loss to see whether the representation floor binds or the
plateau is optimisation-limited.

    uv run python scripts/estimate_lipschitz.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
RUN = "exp1_cond_seed0"
T_SLICES = [0.5, 0.9, 0.99, 0.999]
N_POINTS = 256


def rebuild(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                        seed=cfg["seed"], prior_std=dc.get("prior_std", 1.0),
                                        A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
    return cfg, prob, X.float(), Y.float(), model


def jac_specnorm(model, x_row, t_row, y_row):
    """Largest singular value of d v_theta / d x at a single point."""
    x = x_row.clone().requires_grad_(True)
    def f(xin):
        return model(xin[None, :], t_row[None], y_row[None, :])[0]
    J = torch.autograd.functional.jacobian(f, x, create_graph=False)  # (d, d)
    return float(torch.linalg.svdvals(J)[0])


def layer_upper_bound(model):
    """Product of spectral norms of the Linear layers (crude global upper bound)."""
    prod = 1.0
    for m in model.net:
        if isinstance(m, torch.nn.Linear):
            # only the columns acting on x contribute to Lip_x, but as a crude
            # upper bound we take the full weight spectral norm.
            prod *= float(torch.linalg.matrix_norm(m.weight.detach(), ord=2))
    return prod


def main():
    cfg, prob, X, Y, model = rebuild(ROOT / RUN)
    d = prob.d
    ckdir = ROOT / RUN / "checkpoints"
    it = max(int(p.stem.split("_")[1]) for p in ckdir.glob("ckpt_*.pt"))
    state = torch.load(ckdir / f"ckpt_{it}.pt", map_location="cpu")
    model.load_state_dict(state["model_state"]); model.eval()

    # trained loss at this checkpoint (from metrics.csv)
    md = pd.read_csv(ROOT / RUN / "raw" / "metrics.csv")
    L_trained = float(md[md.group == "train"].sort_values("iter").iloc[-1]["train_loss"])

    g = torch.Generator().manual_seed(7)
    idxs = torch.randint(0, X.shape[0], (N_POINTS,), generator=g)
    rows = []
    print(f"run={RUN} iter={it}  d={d}  L_trained={L_trained:.4f}\n")
    print(f"{'t':>7} | {'L(t) max':>9} | {'L(t) p95':>9} | {'L(t) med':>9} | {'d/(3L_max)':>10}")
    print("-" * 60)
    for t in T_SLICES:
        specs = []
        for j in idxs:
            x_i = X[j]
            x0 = torch.randn(d, generator=g)
            x_t = (1 - t) * x0 + t * x_i
            specs.append(jac_specnorm(model, x_t, torch.tensor(t), Y[j]))
        specs = np.array(specs)
        Lmax, Lp95, Lmed = specs.max(), np.percentile(specs, 95), np.median(specs)
        floor = d / (3 * Lmax)
        rows.append({"t": t, "L_max": Lmax, "L_p95": Lp95, "L_med": Lmed,
                     "floor_d_over_3L": floor, "L_trained": L_trained})
        print(f"{t:>7} | {Lmax:>9.2f} | {Lp95:>9.2f} | {Lmed:>9.2f} | {floor:>10.4f}")

    ub = layer_upper_bound(model)
    print(f"\ncrude spectral upper bound  Lip_x <= {ub:.3e}  -> d/(3L) >= {d/(3*ub):.3e}")
    df = pd.DataFrame(rows)
    out = ROOT / "_theory" / "raw"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "lipschitz.csv", index=False)

    Lmax_overall = df["L_max"].max()
    floor = d / (3 * Lmax_overall)
    verdict = ("optimisation-limited (floor << plateau)" if floor < 0.1 * L_trained
               else "representation floor may bind")
    print(f"\nmax_t L(t) = {Lmax_overall:.2f}  ->  Cor-21 floor d/(3L) = {floor:.4f}")
    print(f"L_trained = {L_trained:.4f}  ->  conclusion: {verdict}")
    print(f"wrote {out / 'lipschitz.csv'}")


if __name__ == "__main__":
    main()
