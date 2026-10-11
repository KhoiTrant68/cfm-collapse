"""Held-out calibration of an image inpainting flow at many levels, per pixel and in PCA space.

Extends scripts/calib_image_checkpoints.py, which reports one level (90%) per pixel.
The same 64 test images and the same draws (same generator seeds), so its numbers can
be joined; but every statistic here is a rank of the true image among the M draws
(src/metrics/calibration.py), whose law under calibration is exact at finite M:

  pixel        central-interval coverage per hidden pixel at every level, and the PIT CDF
  pc_marginal  the same per principal component of the hidden region (PCA fitted on the
               run's own training images): k = 8 and k = 32 components, and the 90%
               coverage of each of the 32 separately
  joint        one region per test image in the span of the top k components
               (leave-one-out Mahalanobis rank): k = 8 and k = 32

Per-pixel coverage cannot see correlations between pixels; the components and the joint
region can. Each comes with its calibrated reference at the same M.

Reads:  <work>/<run>/{config.yaml,checkpoints/ckpt_<iter>.pt}, the dataset's test split
Writes: <out>/calib_levels_<run>.json

Usage:
    python -m scripts.calib_image_levels --work results/exp3 \
        --runs exp3_cifar_heff_h4_s0 --n-test 64 --M 64 --out results/exp3/_rerun
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from scripts.calib_image_checkpoints import build_model, test_images
from src.metrics.calibration import (LEVELS, PIT_GRID, central_coverage, joint_pit, marginal_pit,
                                     pca_basis, pit_cdf, reference_central, reference_pit_cdf,
                                     reference_upper, upper_coverage)
from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import generate
from src.utils import get_device, load_yaml

K_MAX = 32
K_JOINT = (8, 32)


@torch.no_grad()
def analyse_run(work: Path, run: str, n_test: int, M: int, device, out: Path,
                min_iter: int = 0) -> dict | None:
    root = work / run
    cfg = load_yaml(root / "config.yaml")
    ckpts = sorted((p for p in root.glob("checkpoints/ckpt_*.pt")
                    if p.stem != "ckpt_resume" and int(p.stem.split("_")[1]) >= min_iter),
                   key=lambda p: int(p.stem.split("_")[1]))
    if not ckpts:
        print(f"[skip] {run}: no archived checkpoints")
        return None
    dc, ev = cfg["data"], cfg["eval"]
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg.get("problem_seed", cfg["seed"]),
                                       data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"),
                                       dataset=dc.get("dataset", "cifar10"),
                                       cond_kind=dc.get("cond_kind", "inpaint"))
    C = problem.channels
    hidden = (1.0 - problem.mask_obs).bool().expand(C, -1, -1).flatten()      # (C*32*32,)
    X_hid = problem.X.flatten(1)[:, hidden].to(torch.float64).numpy()
    k_max = min(K_MAX, X_hid.shape[0] - 1, X_hid.shape[1])
    mu, V, explained = pca_basis(X_hid, k_max)
    X_test = test_images(dc.get("dataset", "cifar10"), dc.get("data_root", "data"), n_test)
    model = build_model(cfg, C, device)
    rows = []
    for ck in ckpts:
        it = int(ck.stem.split("_")[1])
        model.load_state_dict(torch.load(ck, map_location=device)["model_state"])
        model.eval()
        gen = torch.Generator(device=device).manual_seed(999 + it)   # as calib_image_checkpoints
        u_pix, u_pc, u_joint, q90, sd = [], [], {k: [] for k in K_JOINT if k <= k_max}, [], []
        t0 = time.time()
        for j in range(n_test):
            xs = X_test[j:j + 1]
            s = generate(model, problem.condition(xs), M, ev["n_steps"], ev.get("ode_eps", 1e-3),
                         dc.get("source_std", 1.0), gen, device, channels=C)
            sh = s.flatten(1).to(torch.float64).cpu()[:, hidden].numpy()             # (M, Dh)
            th = xs.flatten()[hidden].to(torch.float64).numpy()
            u_pix.append(marginal_pit(sh, th))
            lo, hi = np.quantile(sh, 0.05, axis=0), np.quantile(sh, 0.95, axis=0)
            q90.append(float(((th >= lo) & (th <= hi)).mean()))
            sd.append(float(sh.std(0, ddof=1).mean()))
            zs, zt = (sh - mu) @ V.T, (th - mu) @ V.T
            u_pc.append(marginal_pit(zs, zt))
            for k in u_joint:
                u_joint[k].append(joint_pit(zs[:, :k], zt[:k]))
        u_pix, u_pc = np.concatenate(u_pix), np.stack(u_pc)                      # (n*Dh,), (n, K)
        i90 = int(np.flatnonzero(np.isclose(LEVELS, 0.9))[0])
        row = {"iter": it,
               "pixel": {"coverage": central_coverage(u_pix).tolist(),
                         "pit_cdf": pit_cdf(u_pix).tolist()},
               "pixel_quantile_cov90": float(np.mean(q90)),
               "pixel_sd": float(np.mean(sd)),
               "pc_marginal": {f"k{k}": central_coverage(u_pc[:, :k]).tolist()
                               for k in (8, k_max) if k <= k_max},
               "pc_cov90_by_component": [float(central_coverage(u_pc[:, c])[i90])
                                         for c in range(k_max)],
               "joint": {f"k{k}": {"coverage": upper_coverage(np.array(v)).tolist(), "u": v}
                         for k, v in u_joint.items()}}
        rows.append(row)
        jt = "  ".join(f"joint k{k} {row['joint'][f'k{k}']['coverage'][i90]:.3f}" for k in u_joint)
        print(f"  {run} it={it:>6d} 90%: pixel {row['pixel']['coverage'][i90]:.3f} "
              f"pc8 {row['pc_marginal']['k8'][i90]:.3f}  {jt}  "
              f"(quantile {row['pixel_quantile_cov90']:.3f})  ({time.time() - t0:.0f}s)", flush=True)
    result = {"run": run, "h": float(cfg["train"].get("y_noise_h", 0.0)), "seed": int(cfg["seed"]),
              "n_test": n_test, "M": M, "levels": LEVELS.tolist(), "pit_grid": PIT_GRID.tolist(),
              "reference": {"central": reference_central(M).tolist(),
                            "upper": reference_upper(M).tolist(),
                            "pit_cdf": reference_pit_cdf(M).tolist()},
              "pca": {"k_max": k_max, "fitted_on": f"{X_hid.shape[0]} training images, hidden region",
                      "explained": explained.tolist()},
              "checkpoints": rows}
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"_from{min_iter // 1000}k" if min_iter > 0 else ""
    path = out / f"calib_levels_{run}{suffix}.json"
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"  wrote {path}")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="results/exp3")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--n-test", type=int, default=64)
    ap.add_argument("--M", type=int, default=64)
    ap.add_argument("--out", default="results/exp3/_rerun")
    ap.add_argument("--min-iter", type=int, default=0)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()
    device = get_device(args.device)
    for run in args.runs:
        analyse_run(Path(args.work), run, args.n_test, args.M, device, Path(args.out),
                    min_iter=args.min_iter)


if __name__ == "__main__":
    main()
