"""E3 of docs/plan/main_track_plan_2026-10-11.md: the empirical NTK of v_theta in the label.

T1 models a trained conditional flow's dependence on the label y as a kernel learner
whose kernel spectrum decays as |w|^-zeta. Two things decide whether that model can
describe the networks at all:

  spectrum   the label-space NTK K(y, y') = E_{x,t} sum_o <d v_o(x,t,y)/d theta,
             d v_o(x,t,y')/d theta> on a uniform grid of labels: does its eigenvalue
             decay follow a power law l^-zeta (polynomial spectrum) or an exponential
             (a smooth, Gaussian-like kernel, for which the kernel model predicts that
             h_eff never reaches h)?
  laziness   how much the normalised kernel moves between initialisation, 1e4 and 2e5
             iterations.

The same decay fits are applied to the exponential kernel (zeta = 2) and the Gaussian
kernel on the same grid, so the reader can see what each fit returns on a known case.

Reads:  results/exp1/heff_p7y_h*_seed*/{config.yaml,checkpoints/ckpt_{100,10000,200000}.pt}
Writes: results/theory/e3_ntk_label.json
Usage:  PYTHONPATH=. python scripts/ntk_label_spectrum.py [--n-xt 64] [--n-label 256]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.func import functional_call, jacrev, vmap

from src.models.mlp_velocity import build_model
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

OUT = Path("results/theory/e3_ntk_label.json")
CKPTS = (100, 10000, 200000)
FIT = (3, 40)                      # eigen-index range for the decay fits


def label_ntk(model, xs, ts, ygrid) -> np.ndarray:
    params = {k: v.detach() for k, v in model.named_parameters()}

    def f(p, x, t, y):
        return functional_call(model, p, (x[None], t[None], y[None]))[0]

    L = ygrid.shape[0]
    K = torch.zeros(L, L, dtype=torch.float64)
    for x, t in zip(xs, ts):
        J = vmap(jacrev(f), in_dims=(None, None, None, 0))(params, x, t, ygrid)
        Jf = torch.cat([j.reshape(L, j.shape[1], -1) for j in J.values()], dim=-1)  # (L, d, P)
        K += torch.einsum("lop,mop->lm", Jf.double(), Jf.double())
    return (K / len(xs)).numpy()


def decay_fits(K: np.ndarray) -> dict:
    lam = np.sort(np.linalg.eigvalsh(K / K.shape[0]))[::-1]
    lam = np.maximum(lam, 1e-300)
    idx = np.arange(1, len(lam) + 1)
    a, b = FIT
    li, ll = np.log(idx[a - 1:b]), np.log(lam[a - 1:b])
    pw = np.polyfit(li, ll, 1)
    ex = np.polyfit(idx[a - 1:b], ll, 1)
    r2 = lambda yv, yh: float(1 - ((yv - yh) ** 2).sum() / ((yv - yv.mean()) ** 2).sum())
    return {"zeta_hat": float(-pw[0]), "r2_power": r2(ll, np.polyval(pw, li)),
            "exp_rate": float(-ex[0]), "r2_exponential": r2(ll, np.polyval(ex, idx[a - 1:b])),
            "eig_head": [float(v) for v in lam[:12]]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-xt", type=int, default=64)
    ap.add_argument("--n-label", type=int, default=256)
    ap.add_argument("--glob", default="heff_p7y_h*_seed*")
    a = ap.parse_args()
    torch.set_num_threads(8)
    rows = []
    for run in sorted(Path("results/exp1").glob(a.glob)):
        cfg = load_yaml(run / "config.yaml")
        dc = cfg["data"]
        ps = int(dc.get("problem_seed", cfg["seed"]))
        prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=ps,
                                            prior_std=dc.get("prior_std", 1.0),
                                            A_kind=dc.get("A_kind", "random"))
        X, Y = prob.sample_dataset(dc["N"], seed=ps + 1)
        X, Y = X.float(), Y.float()                               # the model is float32
        q = torch.quantile(Y[:, 0], torch.tensor([0.01, 0.99], dtype=Y.dtype))
        ygrid = torch.linspace(float(q[0]), float(q[1]), a.n_label)[:, None]
        g = torch.Generator().manual_seed(1234)
        i = torch.randint(0, X.shape[0], (a.n_xt,), generator=g)
        ts = 0.95 * torch.rand(a.n_xt, generator=g)
        xs = (1 - ts)[:, None] * torch.randn(a.n_xt, X.shape[1], generator=g) + ts[:, None] * X[i]
        model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k)
        kernels = {}
        for it in CKPTS:
            ck = run / "checkpoints" / f"ckpt_{it}.pt"
            if not ck.exists():
                continue
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model.eval()
            kernels[it] = label_ntk(model, xs, ts, ygrid)
        if not kernels:
            print(f"[skip] {run.name}: no checkpoints")
            continue
        nrm = {it: K / np.linalg.norm(K) for it, K in kernels.items()}
        its = sorted(kernels)
        row = {"run": run.name, "h": float(cfg["train"].get("y_noise_h", 0.0)), "seed": int(cfg["seed"]),
               "fits": {str(it): decay_fits(kernels[it]) for it in its},
               "scale": {str(it): float(np.linalg.norm(kernels[it]) / np.linalg.norm(kernels[its[0]]))
                         for it in its},
               "change_from_first": {str(it): float(np.linalg.norm(nrm[it] - nrm[its[0]])) for it in its},
               "change_1e4_to_last": float(np.linalg.norm(nrm[its[-1]] - nrm[10000]))
               if 10000 in nrm else float("nan")}
        rows.append(row)
        f = row["fits"]
        print(f"  {run.name:22s} " + "  ".join(
            f"it={it}: zeta={f[str(it)]['zeta_hat']:.2f} (R2 pow {f[str(it)]['r2_power']:.3f} / "
            f"exp {f[str(it)]['r2_exponential']:.3f})" for it in its)
              + f"  |dK| init->last {row['change_from_first'][str(its[-1])]:.3f}", flush=True)
    # what the fits return on known kernels on the same grid
    yy = np.linspace(-2, 2, a.n_label)
    D = np.abs(yy[:, None] - yy[None, :])
    ref = {"exponential_zeta2": decay_fits(np.exp(-D / 1.0)),
           "gaussian": decay_fits(np.exp(-D ** 2 / (2 * 0.3 ** 2)))}
    for k, v in ref.items():
        print(f"  reference {k:18s} zeta={v['zeta_hat']:.2f} (R2 pow {v['r2_power']:.3f} / exp {v['r2_exponential']:.3f})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"fit_range": FIT, "n_xt": a.n_xt, "n_label": a.n_label,
                               "reference": ref, "rows": rows}, indent=1), encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
