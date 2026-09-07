"""Two reference scales for the posterior-distance measurement (T7).

The measured MMD/Sinkhorn to the true posterior is a number with no scale attached.
0.0117 at h=0.5 sounds small; whether it is small depends on what it is being
compared with, and the figure that reported it compared it with 0, which is not
reachable by any finite sample. So compute the two scales that make it readable,
both from ground truth alone -- no trained model is involved, which is why this can
be run after the checkpoints were deleted:

  the sampling floor    MMD/Sinkhorn between two independent M-sample draws from the
                        *same* true posterior. This is what a method that had exactly
                        recovered p(.|y) would still measure at this sample size. It
                        is the bottom of the axis in practice, not 0.

  the atomic prediction MMD/Sinkhorn between the true posterior and the kernel
                        mixture sum_i p_i^(h) delta_{x^i} over the training atoms --
                        the law Theorem 10 says the trained model converges to. Not a
                        floor imposed by the estimator: it is where the theory puts
                        the model.

Read together with the measured curve these say the thing the paper claims: raising h
moves the model down towards the atomic prediction, and the atomic prediction itself
stops far above the sampling floor. Restoring variance is not recovering the
posterior, and the gap that remains is quantified rather than asserted.

    uv run python scripts/analyze_posterior_reference_scales.py

Reads:  results/exp1/{exp1_cond_seed0,p7y_h*_seed0}/config.yaml   (data only)
Writes: results/exp1/_theory/raw/posterior_reference_scales.csv
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

from src.metrics.distances import mmd_rbf, sinkhorn_distance  # noqa: E402
from src.metrics.kernel_theory import kernel_weights, n_eff  # noqa: E402
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402
from src.utils import load_yaml  # noqa: E402

ROOT = Path("results/exp1")
# Same runs, same conditions, same M as analyze_posterior_distance_exp1.py, so the
# references land on the same axes as the measurement.
RUNS = [("exp1_cond_seed0", 0.0)] + [(f"p7y_h{h}_seed0", h) for h in (0.01, 0.05, 0.1, 0.5)]
N_COND = 8
M = 1000


def build_problem(run_dir: Path):
    cfg = load_yaml(run_dir / "config.yaml")
    dc = cfg["data"]
    prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"],
                                        seed=cfg["seed"], prior_std=dc.get("prior_std", 1.0),
                                        A_kind=dc.get("A_kind", "random"))
    X, Y = prob.sample_dataset(dc["N"], seed=cfg["seed"] + 1)
    return cfg, prob, X.float(), Y.float()


def true_posterior_samples(prob, y_i, M, gen):
    mu = prob.posterior_mean(y_i).to(torch.float64)
    L = torch.linalg.cholesky(prob.Sigma_post)
    z = torch.randn(M, prob.d, generator=gen, dtype=torch.float64)
    return (mu[None, :] + z @ L.T).float()


def atomic_samples(y_i, X, Y, h, M, gen):
    """M draws from sum_i p_i^(h) delta_{x^i}: the law Theorem 10 predicts."""
    w = kernel_weights(y_i, Y, h).to(torch.float64)
    idx = torch.multinomial(w, M, replacement=True, generator=gen)
    return X[idx].float(), n_eff(w)


@torch.no_grad()
def main():
    rows = []
    for name, h_declared in RUNS:
        cfg, prob, X, Y = build_problem(ROOT / name)
        h = float(cfg["train"].get("y_noise_h", 0.0))
        assert abs(h - h_declared) < 1e-12, (name, h, h_declared)

        idx = sorted(set(torch.linspace(0, X.shape[0] - 1, N_COND).round().long().tolist()))
        mmd_at, sink_at, mmd_fl, sink_fl, neffs = [], [], [], [], []
        for i in idx:
            y_i = Y[i]
            # Two independent draws from the same posterior: the sampling floor.
            g_a = torch.Generator().manual_seed(cfg["seed"] + 555 + i)
            g_b = torch.Generator().manual_seed(cfg["seed"] + 9001 + i)
            t_a = true_posterior_samples(prob, y_i, M, g_a)
            t_b = true_posterior_samples(prob, y_i, M, g_b)
            mmd_fl.append(mmd_rbf(t_a, t_b))
            sink_fl.append(sinkhorn_distance(t_a, t_b, blur=0.1))

            # The atomic prediction against the same ground truth.
            g_c = torch.Generator().manual_seed(cfg["seed"] + 4242 + i)
            a_s, ne = atomic_samples(y_i, X, Y, h, M, g_c)
            neffs.append(ne)
            mmd_at.append(mmd_rbf(a_s, t_a))
            sink_at.append(sinkhorn_distance(a_s, t_a, blur=0.1))

        rows.append({
            "run": name, "h": h,
            "mmd_atomic": float(np.mean(mmd_at)), "mmd_atomic_std": float(np.std(mmd_at)),
            "sinkhorn_atomic": float(np.mean(sink_at)),
            "sinkhorn_atomic_std": float(np.std(sink_at)),
            "mmd_floor": float(np.mean(mmd_fl)), "mmd_floor_std": float(np.std(mmd_fl)),
            "sinkhorn_floor": float(np.mean(sink_fl)),
            "sinkhorn_floor_std": float(np.std(sink_fl)),
            "n_eff": float(np.mean(neffs)),
        })
        r = rows[-1]
        print(f"  h={h:<5} atomic: MMD={r['mmd_atomic']:.4f} Sink={r['sinkhorn_atomic']:.3f}"
              f"   floor: MMD={r['mmd_floor']:.5f} Sink={r['sinkhorn_floor']:.4f}"
              f"   n_eff={r['n_eff']:.1f}")

    df = pd.DataFrame(rows)
    out = ROOT / "_theory" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "posterior_reference_scales.csv", index=False)

    best = df.loc[df["mmd_atomic"].idxmin()]
    print(f"\nThe atomic prediction bottoms out at h={best['h']:g}: "
          f"MMD={best['mmd_atomic']:.4f} against a sampling floor of "
          f"{best['mmd_floor']:.5f} -- a factor of "
          f"{best['mmd_atomic'] / max(best['mmd_floor'], 1e-12):.0f}. "
          "No bandwidth closes that gap, which is Proposition 14.")
    print(f"wrote {out / 'posterior_reference_scales.csv'}")


if __name__ == "__main__":
    main()
