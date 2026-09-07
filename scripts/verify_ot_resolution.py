"""Can the entropic OT divergence resolve the atomicity gap at the sample sizes used?

The paper scores the endpoint law against the analytic posterior in a debiased
entropic OT divergence and reads a gain from endpoint smoothing off the result. That
reading is only meaningful if the gap being measured is larger than the estimator's
own finite-sample floor -- the value the same divergence returns for two independent
M-sample draws from the SAME posterior, which is not zero and, in dimension, is not
small.

This script measures that floor at each (d, N) row of Table tab:floor, using the same
M, blur and iteration count as scripts/atomicity_scaling.py, so the two are directly
comparable. Read the floor next to the OT column: a difference smaller than the floor
is not a measurement.

The floor is a property of the estimator and the sample size, not of the model, so it
needs no checkpoints and no training.

    uv run python scripts/verify_ot_resolution.py

Writes: results/exp1/_theory/raw/ot_resolution.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.distances import sinkhorn_distance  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402

# Mirrors scripts/atomicity_scaling.py exactly.
GRID = [(2, 50), (2, 200), (2, 1000), (5, 200), (10, 200), (10, 50)]
M_OT = 400
N_COND_OT = 4
SEED = 0
OUT = Path("results/exp1/_theory/raw/ot_resolution.csv")


@torch.no_grad()
def main() -> None:
    rows = []
    print(f"{'d':>3} {'N':>5} {'trSig':>7} {'OT floor':>9} {'floor/trSig':>12}"
          f"   (two independent draws from the same posterior, M={M_OT})")
    print("-" * 74)
    for d, N in GRID:
        prob = LinearGaussianProblem.create(d=d, k=1, sigma_obs=0.1, seed=SEED,
                                            prior_std=1.0, A_kind="random")
        X, Y = prob.sample_dataset(N, seed=SEED + 1)
        Y = Y.double()
        Sig = prob.Sigma_post.double()
        L = torch.linalg.cholesky(Sig)
        tr = float(torch.trace(Sig))
        idx = torch.linspace(0, N - 1, N_COND_OT).round().long().tolist()

        floors = []
        for i in idx:
            mu = prob.posterior_mean(Y[i]).double()
            # Two draws, two independent streams, same law.
            ga = torch.Generator().manual_seed(900 + i)
            gb = torch.Generator().manual_seed(31337 + i)
            a = mu[None, :] + torch.randn(M_OT, d, generator=ga, dtype=torch.float64) @ L.T
            b = mu[None, :] + torch.randn(M_OT, d, generator=gb, dtype=torch.float64) @ L.T
            floors.append(sinkhorn_distance(a.float(), b.float()))
        f = sum(floors) / len(floors)
        rows.append({"d": d, "N": N, "trace_post": tr, "ot_floor": f,
                     "floor_over_trace": f / tr})
        print(f"{d:>3} {N:>5} {tr:>7.3f} {f:>9.4f} {f / tr:>12.4f}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nwrote {OUT}")
    print("Any OT difference smaller than the floor on its row is not resolved by "
          f"this estimator at M={M_OT}.")


if __name__ == "__main__":
    main()
