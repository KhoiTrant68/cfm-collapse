"""Effective bandwidth of a CIFAR-10 DDPM run, at every archived checkpoint.

The image-scale counterpart of scripts/test_heff_synthetic.py. For each archived
checkpoint of each run it draws M completions at C training conditions and records
the per-condition trace of the generated covariance and the generated mean. It then
fits, over a log-spaced bandwidth grid,

    h_eff    the one bandwidth whose exact kernel reference (Theorem 1) best explains
             the per-condition traces, in log space, and
    h_means  the one bandwidth whose reference means best explain the generated means,

each with a 95% bootstrap interval over conditions. The two use disjoint statistics,
so their agreement is an out-of-sample check. For h > 0 it also scores the reference
at h (no parameter), a constant multiple of it (one) and the power law of the paper
(two, whose slope is beta), exactly as the synthetic test does.

It runs where the checkpoints are (a Kaggle session): one resumable checkpoint is
~430 MB, far too large to bring back, while the JSON this writes is small.

Reads:  <work>/<run>/{config.yaml,checkpoints/ckpt_<iter>.pt}
Writes: <out>/heff_<run>.json

Usage:
    python -m scripts.heff_cifar_checkpoints --work results/exp3 \
        --runs exp3_cifar_heff_h4_s0 --M 128 --n-conditions 48 --out results/exp3/_heff
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import cond_vectors, generate
from src.utils import get_device, load_yaml

GRID = np.exp(np.linspace(np.log(0.5), np.log(40.0), 160))
N_BOOT = 500


def build_model(cfg, C, device):
    from src.models.unet import UNet
    m = cfg["model"]
    return UNet(in_channels=2 * C + 1, out_channels=C, base=m.get("base", 128),
                ch_mult=tuple(m.get("ch_mult", [1, 2, 2, 2])),
                num_res_blocks=m.get("num_res_blocks", 2),
                attn_resolutions=tuple(m.get("attn_resolutions", [16])),
                temb_dim=m.get("temb_dim", 512)).to(device)


def r2(y, yhat) -> float:
    return float(1.0 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def reference_grid(Xf, Yv, idx, grid, device):
    """Reference trace (G, C) and mean (G, C, d) for every grid bandwidth.

    Squared label distances are computed once; the kernel weights for all
    bandwidths then follow from them, in float64 and in log space.
    """
    X = Xf.to(device, torch.float64)
    Y = Yv.to(device, torch.float64)
    Q = Y[idx]                                                    # (C, k)
    D = torch.cdist(Q, Y) ** 2                                    # (C, N)
    x2 = (X ** 2).sum(1)                                          # (N,)
    tr = np.empty((len(grid), len(idx)))
    mu = np.empty((len(grid), len(idx), X.shape[1]), dtype=np.float32)
    for g, hp in enumerate(grid):
        W = torch.softmax(-D / (2.0 * float(hp) ** 2), dim=1)       # (C, N)
        m = W @ X                                                 # (C, d)
        tr[g] = (W @ x2 - (m ** 2).sum(1)).clamp_min(0).cpu().numpy()
        mu[g] = m.float().cpu().numpy()
    return tr, mu


@torch.no_grad()
def analyse_run(work: Path, run: str, M: int, n_cond: int, device, out: Path) -> dict | None:
    root = work / run
    cfg = load_yaml(root / "config.yaml")
    ckpts = sorted((p for p in root.glob("checkpoints/ckpt_*.pt") if p.stem != "ckpt_resume"),
                   key=lambda p: int(p.stem.split("_")[1]))
    if not ckpts:
        print(f"[skip] {run}: no archived checkpoints")
        return None
    dc, ev = cfg["data"], cfg["eval"]
    # the same instance train_exp3 trained on (problem_seed defaults to seed there)
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg.get("problem_seed", cfg["seed"]),
                                       data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"),
                                       dataset=dc.get("dataset", "cifar10"),
                                       cond_kind=dc.get("cond_kind", "inpaint"))
    C = problem.channels
    h = float(cfg["train"].get("y_noise_h", 0.0))
    Xf = problem.X.flatten(1)
    Yv = cond_vectors(problem)
    idx = sorted(set(np.linspace(0, problem.N - 1, n_cond).round().astype(int).tolist()))
    t0 = time.time()
    tr_ref, mu_ref = reference_grid(Xf, Yv, idx, GRID, device)
    g_h = int(np.argmin(np.abs(GRID - h))) if h > 0 else None
    print(f"{run}: h={h:g}, {len(idx)} conditions, reference grid in {time.time()-t0:.0f}s")

    model = build_model(cfg, C, device)
    rows = []
    for ck in ckpts:
        it = int(ck.stem.split("_")[1])
        state = torch.load(ck, map_location=device)
        model.load_state_dict(state["model_state"])
        model.eval()
        gen = torch.Generator(device=device).manual_seed(12345)
        tr_m, mu_m = [], []
        t1 = time.time()
        for i in idx:
            cond1 = problem.condition(problem.X[i:i + 1], rows=slice(i, i + 1))
            s = generate(model, cond1, M, ev["n_steps"], ev.get("ode_eps", 1e-3),
                         dc.get("source_std", 1.0), gen, device, channels=C)
            sf = s.flatten(1).to(torch.float64)
            tr_m.append(float(sf.var(dim=0, unbiased=True).sum()))
            mu_m.append(sf.mean(0).float().cpu().numpy())
        tr_m, mu_m = np.array(tr_m), np.stack(mu_m)
        ly = np.log(np.clip(tr_m, 1e-12, None))
        se_c = (ly[None, :] - np.log(np.clip(tr_ref, 1e-12, None))) ** 2       # (G, C)
        me_c = np.linalg.norm(mu_m[None] - mu_ref, axis=2)                      # (G, C)
        g, gm = int(np.argmin(se_c.sum(1))), int(np.argmin(me_c.mean(1)))
        rng = np.random.default_rng(it)
        bh, bm = [], []
        for _ in range(N_BOOT):
            b = rng.integers(0, len(idx), len(idx))
            bh.append(GRID[int(np.argmin(se_c[:, b].sum(1)))])
            bm.append(GRID[int(np.argmin(me_c[:, b].mean(1)))])
        res = {"iter": it, "h_eff": float(GRID[g]),
               "h_eff_ci": [float(np.percentile(bh, 2.5)), float(np.percentile(bh, 97.5))],
               "h_means": float(GRID[gm]),
               "h_means_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
               "h_eff_at_edge": g in (0, len(GRID) - 1),
               "r2_heff": r2(ly, np.log(np.clip(tr_ref[g], 1e-12, None))),
               "trace_measured": tr_m.tolist(),
               "trace_measured_mean": float(tr_m.mean())}
        if g_h is not None:
            lref = np.log(np.clip(tr_ref[g_h], 1e-12, None))
            c = float(np.exp((ly - lref).mean()))
            A = np.vstack([np.ones_like(lref), lref]).T
            coef, *_ = np.linalg.lstsq(A, ly, rcond=None)
            res.update({"r2_theory": r2(ly, lref), "r2_scale": r2(ly, lref + np.log(c)),
                        "r2_power": r2(ly, A @ coef), "beta": float(coef[1]),
                        "decades_ref": float(np.ptp(lref) / np.log(10))})
        rows.append(res)
        print(f"  it={it:>6d} h_eff={res['h_eff']:.2f} [{res['h_eff_ci'][0]:.2f},"
              f"{res['h_eff_ci'][1]:.2f}]  h_means={res['h_means']:.2f} "
              f"[{res['h_means_ci'][0]:.2f},{res['h_means_ci'][1]:.2f}]  "
              f"R2 h_eff {res['r2_heff']:.3f}"
              + (f" | theory {res['r2_theory']:.3f} scale {res['r2_scale']:.3f} "
                 f"power {res['r2_power']:.3f} beta {res['beta']:.3f}" if g_h is not None else "")
              + f"  ({time.time()-t1:.0f}s)", flush=True)

    result = {"run": run, "h": h, "seed": int(cfg["seed"]), "M": M,
              "conditions": idx, "grid": GRID.tolist(), "checkpoints": rows}
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"heff_{run}.json"
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"  wrote {path}")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="results/exp3", help="directory holding the runs")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--M", type=int, default=128)
    ap.add_argument("--n-conditions", type=int, default=48)
    ap.add_argument("--out", default="results/exp3/_heff")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()
    device = get_device(args.device)
    for run in args.runs:
        analyse_run(Path(args.work), run, args.M, args.n_conditions, device, Path(args.out))


if __name__ == "__main__":
    main()
