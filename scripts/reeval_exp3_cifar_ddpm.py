"""Re-evaluate the final CIFAR/DDPM checkpoints with enough samples to trust the number.

The in-training evaluation draws M=16 completions per condition and estimates
tr Cov from them. In d=3072 those 16 samples span at most 15 directions, so the
trace estimate carries a relative standard error of roughly sqrt(2/15) ~ 0.37 per
condition, or ~13% after averaging 8 conditions -- which is the size of the
non-monotone wobble seen along the training curves (h=6 reads 0.936, 0.773 and
1.173 at successive checkpoints). It also used ``unbiased=False``, biasing the
trace low by a further 1/M = 6.25%.

Neither needs retraining: the checkpoints are on disk. This re-evaluates them with
many more samples and the unbiased estimator, and reports a bootstrap interval so
the residual uncertainty is visible rather than assumed away. A split-half estimate
of the sampling noise is reported alongside, as a direct check that M is now large
enough.

Usage:
    uv run python scripts/reeval_exp3_cifar_ddpm.py [--M 256] [--n-conditions 16]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from src.metrics.kernel_theory import kernel_moments_trace
from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import cond_vectors, generate
from src.utils import get_device, load_yaml

RUNS = ["exp3_cifar_ddpm_h0", "exp3_cifar_ddpm_h4",
        "exp3_cifar_ddpm_h5", "exp3_cifar_ddpm_h6"]
OUT = Path("results/exp3/_cifar_ddpm")


def build_model(cfg, C, device):
    if cfg["model"].get("arch", "small") == "ddpm":
        from src.models.unet import UNet
        return UNet(in_channels=2 * C + 1, out_channels=C,
                    base=cfg["model"].get("base", 128),
                    ch_mult=tuple(cfg["model"].get("ch_mult", [1, 2, 2, 2])),
                    num_res_blocks=cfg["model"].get("num_res_blocks", 2),
                    attn_resolutions=tuple(cfg["model"].get("attn_resolutions", [16])),
                    temb_dim=cfg["model"].get("temb_dim", 512)).to(device)
    from src.models.unet_small import SmallUNet
    return SmallUNet(in_channels=2 * C + 1, out_channels=C,
                     base=cfg["model"].get("base", 32),
                     temb_dim=cfg["model"].get("temb_dim", 128)).to(device)


@torch.no_grad()
def reeval(run: str, M: int, n_cond: int, device) -> dict | None:
    root = Path("results/exp3") / run
    cfg = load_yaml(root / "config.yaml")
    ckpts = sorted(root.glob("checkpoints/ckpt_*.pt"),
                   key=lambda p: int(p.stem.split("_")[1]))
    if not ckpts:
        print(f"  [skip] {run}: no checkpoints")
        return None
    ck = ckpts[-1]
    it = int(ck.stem.split("_")[1])

    dc = cfg["data"]
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg["seed"],
                                       data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"),
                                       dataset=dc.get("dataset", "mnist"))
    C = problem.channels
    model = build_model(cfg, C, device)
    model.load_state_dict(torch.load(ck, map_location=device)["model_state"])
    model.eval()

    h = float(cfg["train"].get("y_noise_h", 0.0))
    ev = cfg["eval"]
    Xflat = problem.X.flatten(1).to(device).to(torch.float64)
    Yvec = cond_vectors(problem).to(device).to(torch.float64)
    gen = torch.Generator(device=device).manual_seed(12345)

    idx = sorted(set(np.linspace(0, problem.N - 1, n_cond).round().astype(int).tolist()))
    ratios, halves, tr_meas, tr_kern, mean_errs, neffs = [], [], [], [], [], []
    for i in idx:
        cond1 = problem.condition(problem.X[i:i + 1])
        s = generate(model, cond1, M, ev["n_steps"], ev.get("ode_eps", 1e-3),
                     dc.get("source_std", 1.0), gen, device, channels=C)
        sf = s.flatten(1).to(torch.float64)                       # (M,d)
        tm = float(sf.var(dim=0, unbiased=True).sum())            # unbiased trace
        _, tk, ne = kernel_moments_trace(Yvec[i], Xflat, Yvec, h)
        tr_meas.append(tm); tr_kern.append(tk); neffs.append(ne)
        mean_errs.append(float((sf.mean(0) - kernel_moments_trace(
            Yvec[i], Xflat, Yvec, h)[0]).norm()))
        if tk > 0:
            ratios.append(tm / tk)
            # split-half: two independent M/2 estimates, to size the sampling noise
            a = float(sf[:M // 2].var(dim=0, unbiased=True).sum()) / tk
            b = float(sf[M // 2:].var(dim=0, unbiased=True).sum()) / tk
            halves.append(abs(a - b) / 2.0)

    res = {"run": run, "h": h, "iter": it, "M": M, "n_conditions": len(idx),
           "trace_cov": float(np.mean(tr_meas)),
           "trace_cov_kernel": float(np.mean(tr_kern)),
           "mean_err_kernel": float(np.mean(mean_errs)),
           "n_eff": float(np.mean(neffs))}
    if ratios:
        r = np.array(ratios)
        boot = np.array([np.median(np.random.choice(r, len(r), replace=True))
                         for _ in range(2000)])
        res.update({"ratio_median": float(np.median(r)),
                    "ratio_mean": float(r.mean()),
                    "ratio_ci_lo": float(np.percentile(boot, 2.5)),
                    "ratio_ci_hi": float(np.percentile(boot, 97.5)),
                    "ratio_iqr_lo": float(np.percentile(r, 25)),
                    "ratio_iqr_hi": float(np.percentile(r, 75)),
                    "ratio_min": float(r.min()), "ratio_max": float(r.max()),
                    "split_half_noise": float(np.mean(halves)),
                    "ratio_per_condition": [float(v) for v in r],
                    "trace_kernel_per_condition": [float(v) for v in tr_kern],
                    "n_eff_per_condition": [float(v) for v in neffs]})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--n-conditions", type=int, default=16)
    args = ap.parse_args()

    device = get_device("auto")
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for run in RUNS:
        print(f"re-evaluating {run} (M={args.M}, {args.n_conditions} conditions)...")
        r = reeval(run, args.M, args.n_conditions, device)
        if r is None:
            continue
        out.append(r)
        if "ratio_median" in r:
            print(f"  h={r['h']:.0f} iter={r['iter']} ratio={r['ratio_median']:.3f} "
                  f"CI[{r['ratio_ci_lo']:.3f},{r['ratio_ci_hi']:.3f}] "
                  f"IQR[{r['ratio_iqr_lo']:.3f},{r['ratio_iqr_hi']:.3f}] "
                  f"range[{r['ratio_min']:.3f},{r['ratio_max']:.3f}] "
                  f"split-half +/-{r['split_half_noise']:.3f}  "
                  f"tr Cov={r['trace_cov']:.4g} vs Cov_h={r['trace_cov_kernel']:.4g}")
        else:
            print(f"  h={r['h']:.0f} iter={r['iter']} tr Cov={r['trace_cov']:.4g} "
                  f"(kernel reference is 0 at h=0)  |mean-x^i|={r['mean_err_kernel']:.4g}")

    with open(OUT / "reeval.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT}/reeval.json")


if __name__ == "__main__":
    main()
