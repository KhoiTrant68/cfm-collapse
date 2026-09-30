"""Does the audit predict posterior calibration? (linear-Gaussian problem)

The audit (h_eff, the tracking slope beta, the on-atom fraction) is computed from the
training set and the model alone. On the linear-Gaussian problem the true posterior is
known in closed form, so calibration can be measured directly on held-out pairs
(x*, y*) drawn from the prior and the forward model:

    coverage_50, coverage_90   share of x* inside the 50% / 90% Mahalanobis region of
                               the generated samples (nominal 0.5 / 0.9)
    calibration_error          |coverage_50 - 0.5| + |coverage_90 - 0.9|
    w2_post                    Gaussian (Bures) W2 between the generated moments and the
                               true posterior, averaged over held-out y*
    extraction                 share of generated samples that are a training point
                               (memorisation ratio, c = 1/9), at held-out y*

For every run heff_p7y_h*_seed* and checkpoint from 3000 iterations on, this measures
those, reads the audit statistics of the same checkpoint from heff_synthetic.json,
adds the on-atom fraction at the training conditions, and reports Spearman
correlations between audit and calibration across all (run, checkpoint) pairs.

Reads:  results/exp1/heff_p7y_h*_seed*/{config.yaml,checkpoints/},
        results/exp1/_heff/heff_synthetic.json
Writes: results/exp1/_heff/audit_calibration.json

Usage:
    PYTHONPATH=. uv run python scripts/audit_calibration_synthetic.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from src.flows.ode_solver import generate_samples
from src.metrics.memorization import memorization_ratio
from src.models.mlp_velocity import build_model
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

RUNS = sorted(Path("results/exp1").glob("heff_p7y_h*_seed*"))
HEFF = Path("results/exp1/_heff/heff_synthetic.json")
OUT = Path("results/exp1/_heff/audit_calibration.json")
MIN_ITER = 3000
N_HELDOUT = 100
M = 400
CHI2_2 = {0.5: 1.3862944, 0.9: 4.6051702}      # chi-square quantiles, 2 dof


def sqrtm_psd(A: torch.Tensor) -> torch.Tensor:
    w, V = torch.linalg.eigh(A)
    return (V * w.clamp_min(0).sqrt()) @ V.T


def bures_w2(m1, C1, m2, C2) -> float:
    s2 = sqrtm_psd(C2)
    cross = sqrtm_psd(s2 @ C1 @ s2)
    return float(((m1 - m2) ** 2).sum() + torch.trace(C1 + C2 - 2 * cross))


def rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    r[order] = np.arange(len(a))
    for v in np.unique(a):                      # average ties
        m = a == v
        r[m] = r[m].mean()
    return r


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    return float(np.corrcoef(ra, rb)[0, 1])


@torch.no_grad()
def main() -> None:
    torch.set_num_threads(8)
    audit = {(r["run"], r["iter"]): r for r in json.loads(HEFF.read_text(encoding="utf-8"))}
    rows = []
    for run in RUNS:
        cfg = load_yaml(run / "config.yaml")
        dc, ev = cfg["data"], cfg["eval"]
        ps = int(dc.get("problem_seed", cfg["seed"]))
        problem = LinearGaussianProblem.create(
            d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=ps,
            prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
        X, Y = problem.sample_dataset(dc["N"], seed=ps + 1)
        g_ho = torch.Generator().manual_seed(ps + 31337)       # disjoint from training
        X_ho = problem.sample_prior(N_HELDOUT, generator=g_ho)
        Y_ho = problem.forward(X_ho, generator=g_ho)
        Sig = problem.Sigma_post.to(torch.float64)
        mu_ho = problem.posterior_mean(Y_ho).to(torch.float64)
        tr_idx = sorted(set(torch.linspace(0, X.shape[0] - 1, ev["n_eval_train"])
                            .round().long().tolist()))
        model = build_model(cfg, data_dim=problem.d, cond_dim=problem.k)
        h = float(cfg["train"].get("y_noise_h", 0.0))

        def sample(y, gen):
            return generate_samples(model, M, problem.d, y,
                                    source_std=dc.get("source_std", 1.0),
                                    n_steps=ev["n_steps"], method=ev.get("ode_method", "rk4"),
                                    eps=ev.get("ode_eps", 1e-3), generator=gen,
                                    device="cpu").to(torch.float64)

        ckpts = sorted((p for p in run.glob("checkpoints/ckpt_*.pt")
                        if int(p.stem.split("_")[1]) >= MIN_ITER),
                       key=lambda p: int(p.stem.split("_")[1]))
        for ck in ckpts:
            it = int(ck.stem.split("_")[1])
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model.eval()
            gen = torch.Generator().manual_seed(777 + it)
            cov = {0.5: [], 0.9: []}
            w2, extr = [], []
            for j in range(N_HELDOUT):
                s = sample(Y_ho[j], gen)
                m, C = s.mean(0), torch.cov(s.T)
                diff = X_ho[j].to(torch.float64) - m
                d2 = float(diff @ torch.linalg.solve(C + 1e-10 * torch.eye(problem.d,
                                                     dtype=torch.float64), diff))
                for a in cov:
                    cov[a].append(d2 <= CHI2_2[a])
                w2.append(bures_w2(m, C, mu_ho[j], Sig))
                extr.append(memorization_ratio(s, X))
            on_atom = float(np.mean([memorization_ratio(sample(Y[i], gen), X) for i in tr_idx]))
            a = audit.get((run.name, it), {})
            c50, c90 = float(np.mean(cov[0.5])), float(np.mean(cov[0.9]))
            row = {"run": run.name, "h": h, "seed": int(cfg["seed"]), "iter": it,
                   "coverage_50": c50, "coverage_90": c90,
                   "calibration_error": abs(c50 - 0.5) + abs(c90 - 0.9),
                   "w2_post": float(np.mean(w2)), "extraction": float(np.mean(extr)),
                   "on_atom_train": on_atom,
                   "h_eff": a.get("h_eff"), "beta": a.get("power_beta"),
                   "r2_heff": a.get("r2_heff")}
            rows.append(row)
            print(f"{run.name:<24} it={it:>6d}  h_eff={row['h_eff']:.4f}  "
                  f"cov50={c50:.2f} cov90={c90:.2f}  W2={row['w2_post']:.4f}  "
                  f"extraction={row['extraction']:.2f}  on-atom(train)={on_atom:.2f}",
                  flush=True)

    calib = ("coverage_90", "calibration_error", "w2_post", "extraction")
    auditk = ("h_eff", "on_atom_train", "beta")
    corr = {f"{a}~{c}": spearman([r[a] for r in rows], [r[c] for r in rows])
            for a in auditk for c in calib}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"rows": rows, "spearman": corr,
                               "n_heldout": N_HELDOUT, "M": M}, indent=1), encoding="utf-8")
    print("\nSpearman correlations across (run, checkpoint):")
    for k, v in corr.items():
        print(f"  {k:<36} {v:+.3f}")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
