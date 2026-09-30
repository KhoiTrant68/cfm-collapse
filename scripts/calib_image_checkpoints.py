"""Posterior-free calibration of an image inpainting flow, at every archived checkpoint.

No reference posterior is needed: for a held-out image x* from the dataset's *test*
split, its hidden half is a draw from the true conditional law given its observed half.
So a calibrated sampler, conditioned on the observed half, must place x* like one of its
own draws. Per hidden pixel, u = share of generated values below the true value is then
Uniform(0,1), and the central 90% interval of the generated values covers the true value
90% of the time. We report, per checkpoint, pooled over test images and hidden pixels:

    pit_error      mean over a grid of |P(u <= a) - a|             (0 when calibrated)
    coverage_90    share of hidden pixels inside the 5%-95% sample interval
    extraction     share of samples that are a training image (memorisation ratio,
                   c = 1/9), the privacy-side reading of the same collapse

together with the generated per-pixel standard deviation. It runs where the checkpoints
are (Kaggle) and writes a small JSON; join it with heff_<run>.json by iteration.

Reads:  <work>/<run>/{config.yaml,checkpoints/ckpt_<iter>.pt}, the dataset's test split
Writes: <out>/calib_<run>.json

Usage:
    python -m scripts.calib_image_checkpoints --work results/exp3 \
        --runs exp3_cifar_heff_h4_s0 --n-test 64 --M 64 --out results/exp3/_heff
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from src.metrics.memorization import memorization_ratio
from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import generate
from src.utils import get_device, load_yaml

PIT_GRID = np.linspace(0.05, 0.95, 19)


def build_model(cfg, C, device):
    from src.models.unet import UNet
    m = cfg["model"]
    return UNet(in_channels=2 * C + 1, out_channels=C, base=m.get("base", 128),
                ch_mult=tuple(m.get("ch_mult", [1, 2, 2, 2])),
                num_res_blocks=m.get("num_res_blocks", 2),
                attn_resolutions=tuple(m.get("attn_resolutions", [16])),
                temb_dim=m.get("temb_dim", 512)).to(device)


def test_images(dataset: str, data_root: str, n: int, seed: int = 20260930) -> torch.Tensor:
    """n images of the test split, preprocessed exactly as the training images."""
    from torchvision import datasets
    if dataset == "mnist":
        ds = datasets.MNIST(root=data_root, train=False, download=True)
        x = ds.data.to(torch.float32) / 255.0
        x = torch.nn.functional.pad(x, (2, 2, 2, 2), value=0.0).unsqueeze(1)
    elif dataset == "cifar10":
        ds = datasets.CIFAR10(root=data_root, train=False, download=True)
        x = (torch.from_numpy(ds.data).to(torch.float32) / 255.0).permute(0, 3, 1, 2)
    else:
        raise ValueError(dataset)
    idx = torch.randperm(x.shape[0], generator=torch.Generator().manual_seed(seed))[:n]
    return x[idx].contiguous() * 2.0 - 1.0


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
    X_train = problem.X.flatten(1).to(torch.float64)
    X_test = test_images(dc.get("dataset", "cifar10"), dc.get("data_root", "data"), n_test)
    hidden = (1.0 - problem.mask_obs).bool().expand(C, -1, -1).flatten()      # (C*32*32,)
    model = build_model(cfg, C, device)
    rows = []
    for ck in ckpts:
        it = int(ck.stem.split("_")[1])
        model.load_state_dict(torch.load(ck, map_location=device)["model_state"])
        model.eval()
        gen = torch.Generator(device=device).manual_seed(999 + it)
        us, inside, extr, sd = [], [], [], []
        t0 = time.time()
        for j in range(n_test):
            xs = X_test[j:j + 1]
            s = generate(model, problem.condition(xs), M, ev["n_steps"], ev.get("ode_eps", 1e-3),
                         dc.get("source_std", 1.0), gen, device, channels=C)
            sf = s.flatten(1).to(torch.float64).cpu()                            # (M, D)
            truth = xs.flatten().to(torch.float64)
            sh, th = sf[:, hidden], truth[hidden]
            us.append((sh < th[None]).double().mean(0).numpy())
            lo, hi = torch.quantile(sh, 0.05, dim=0), torch.quantile(sh, 0.95, dim=0)
            inside.append(((th >= lo) & (th <= hi)).double().mean().item())
            sd.append(float(sh.std(0).mean()))
            extr.append(memorization_ratio(sf, X_train))
        u = np.concatenate(us)
        row = {"iter": it,
               "pit_error": float(np.mean([abs((u <= a).mean() - a) for a in PIT_GRID])),
               "coverage_90": float(np.mean(inside)),
               "extraction": float(np.mean(extr)),
               "pixel_sd": float(np.mean(sd))}
        rows.append(row)
        print(f"  {run} it={it:>6d} PIT error={row['pit_error']:.3f} "
              f"90% coverage={row['coverage_90']:.3f} extraction={row['extraction']:.3f} "
              f"pixel sd={row['pixel_sd']:.4f}  ({time.time() - t0:.0f}s)", flush=True)
    result = {"run": run, "h": float(cfg["train"].get("y_noise_h", 0.0)), "seed": int(cfg["seed"]),
              "n_test": n_test, "M": M, "checkpoints": rows}
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"_from{min_iter // 1000}k" if min_iter > 0 else ""
    path = out / f"calib_{run}{suffix}.json"
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"  wrote {path}")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="results/exp3")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--n-test", type=int, default=64)
    ap.add_argument("--M", type=int, default=64)
    ap.add_argument("--out", default="results/exp3/_heff")
    ap.add_argument("--min-iter", type=int, default=0)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()
    device = get_device(args.device)
    for run in args.runs:
        analyse_run(Path(args.work), run, args.n_test, args.M, device, Path(args.out),
                    min_iter=args.min_iter)


if __name__ == "__main__":
    main()
