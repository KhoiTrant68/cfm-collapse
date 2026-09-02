"""Does a *trained* model attain the smoothed endpoint law of Prop tgtnoise?

Compares runs trained with endpoint noise rho>0 against rho=0 at the same label
bandwidth h, on the N=50 problem where the d=2 atomicity floor is largest.
Reports (i) trace(Cov) against the population prediction tr Cov_h + d*rho^2, and
(ii) MMD / entropic-OT distance from the generated samples to the analytic
posterior -- the quantity the atomicity floor lower-bounds.

    uv run python scripts/analyze_target_noise.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.flows.ode_solver import generate_samples  # noqa: E402
from src.metrics.distances import mmd_rbf, sinkhorn_distance  # noqa: E402
from src.metrics.kernel_theory import kernel_moments  # noqa: E402
from src.models.mlp_velocity import build_model  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

RUNS = [("rho=0.0", ["exp1_tgt_rho00_seed0", "exp1_tgt_rho00_seed1"]),
        ("rho=0.3", ["exp1_tgt_rho03_seed0", "exp1_tgt_rho03_seed1"])]
IT = 200000
M = 800
N_COND = 8


def main():
    print(f"{'run':>9} {'seed':>5} {'trCov':>8} {'pred':>8} {'MMD':>8} {'OT':>9} "
          f"{'|mean-mu|':>10}")
    print("-" * 62)
    agg = {}
    for label, names in RUNS:
        rows = []
        for name in names:
            run = Path("results/exp1") / name
            cfg = load_yaml(run / "config.yaml")
            dc = cfg["data"]
            rho = float(cfg["train"].get("target_noise_rho", 0.0))
            h = float(cfg["train"].get("y_noise_h", 0.0))
            prob = LinearGaussianProblem.create(
                d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
                prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
            X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
            m = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
            m.load_state_dict(torch.load(run / "checkpoints" / f"ckpt_{IT}.pt",
                                         map_location="cpu")["model_state"])
            m.eval()
            L = torch.linalg.cholesky(prob.Sigma_post.double())

            idx = torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()
            tc, pr, mm, ot, me = [], [], [], [], []
            for i in idx:
                y_i = Y[i]
                g = torch.Generator().manual_seed(4000 + i)
                s = generate_samples(m, M, prob.d, y_i,
                                     source_std=dc.get("source_std", 1.0),
                                     n_steps=100, method="rk4", generator=g).double()
                _, cov_h, _ = kernel_moments(y_i, X, Y, h)
                mu = prob.posterior_mean(y_i).double()
                ref = mu[None, :] + torch.randn(M, prob.d, generator=g,
                                                dtype=torch.float64) @ L.T
                tc.append(float(s.var(0, unbiased=False).sum()))
                pr.append(float(torch.trace(cov_h)) + prob.d * rho ** 2)
                mm.append(mmd_rbf(s.float(), ref.float()))
                ot.append(sinkhorn_distance(s.float(), ref.float()))
                me.append(float(torch.linalg.norm(s.mean(0) - mu)))
            r = (np.mean(tc), np.mean(pr), np.mean(mm), np.mean(ot), np.mean(me))
            rows.append(r)
            print(f"{label:>9} {cfg['seed']:>5} {r[0]:>8.4f} {r[1]:>8.4f} "
                  f"{r[2]:>8.4f} {r[3]:>9.3f} {r[4]:>10.4f}", flush=True)
        a = np.mean(np.array(rows), axis=0)
        agg[label] = a
        print(f"{label:>9} {'mean':>5} {a[0]:>8.4f} {a[1]:>8.4f} {a[2]:>8.4f} "
              f"{a[3]:>9.3f} {a[4]:>10.4f}\n")

    b, s_ = agg["rho=0.0"], agg["rho=0.3"]
    print(f"OT  ratio rho=0 / rho=0.3 : {b[3]/max(s_[3],1e-12):.2f}x")
    print(f"MMD ratio rho=0 / rho=0.3 : {b[2]/max(s_[2],1e-12):.2f}x")


if __name__ == "__main__":
    main()
