#!/usr/bin/env python
"""Measure training throughput at the real batch size, before committing to a
multi-session run.

The smoke rehearsal checks the plumbing at batch 16, which says nothing about
how fast batch 128 runs: a small batch leaves the GPU idle, so its it/s
overstates the real rate several times over. Planning a 240000-iteration run
against that number books too few sessions. This times the actual training step
of the actual config -- same model, same batch, same AMP -- with evaluation left
out, since the real run evaluates eleven times in 240000 iterations and that is
negligible against the steps.

    python scripts/bench_throughput.py --config configs/exp3_cifar_ddpm_h4_long.yaml

The step below mirrors src.train_exp3.train line for line; if that loop changes,
change this with it.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.problems.inpainting import InpaintingProblem  # noqa: E402
from src.train_exp3 import smooth_cond  # noqa: E402
from src.utils import apply_overrides, get_device, load_yaml, set_seed  # noqa: E402


def build(cfg: dict, device):
    dc = cfg["data"]
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg["seed"],
                                       data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"),
                                       dataset=dc.get("dataset", "mnist"),
                                       cond_kind=dc.get("cond_kind", "inpaint"))
    C = problem.channels
    arch = cfg["model"].get("arch", "small")
    if arch == "ddpm":
        from src.models.unet import UNet
        model = UNet(in_channels=C + problem.cond_channels, out_channels=C,
                     base=cfg["model"].get("base", 128),
                     ch_mult=tuple(cfg["model"].get("ch_mult", [1, 2, 2, 2])),
                     num_res_blocks=cfg["model"].get("num_res_blocks", 2),
                     attn_resolutions=tuple(cfg["model"].get("attn_resolutions", [16])),
                     temb_dim=cfg["model"].get("temb_dim", 512),
                     dropout=cfg["model"].get("dropout", 0.0)).to(device)
    else:
        from src.models.unet_small import SmallUNet
        model = SmallUNet(in_channels=C + problem.cond_channels, out_channels=C,
                          base=cfg["model"].get("base", 32),
                          temb_dim=cfg["model"].get("temb_dim", 128)).to(device)
    return problem, model


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/exp3_cifar_ddpm_h4_long.yaml")
    ap.add_argument("--warmup", type=int, default=15,
                    help="untimed steps first: cuDNN autotuning and AMP scale settling")
    ap.add_argument("--iters", type=int, default=60, help="timed steps")
    ap.add_argument("--session-hours", type=float, default=8.0)
    ap.add_argument("--set", nargs="*", default=[], dest="overrides")
    args = ap.parse_args()

    config = Path(args.config)
    if not config.is_absolute():
        config = ROOT / config
    cfg = apply_overrides(load_yaml(config), args.overrides)
    device = get_device(cfg.get("device", "auto"))
    set_seed(cfg["seed"])

    problem, model = build(cfg, device)
    C = problem.channels
    X = problem.X.to(device)
    cond_all = problem.condition(problem.X).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["train"].get("lr", 2e-4))
    batch = cfg["train"].get("batch_size", 64)
    source_std = cfg["data"].get("source_std", 1.0)
    y_noise_h = float(cfg["train"].get("y_noise_h", 0.0))
    use_amp = bool(cfg["train"].get("amp", False)) and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    tgen = torch.Generator(device=device).manual_seed(cfg["seed"] + 2)
    cond_mask = None if problem.cond_kind == "class" else problem.mask_obs

    def step() -> None:
        idx = torch.randint(0, problem.N, (batch,), generator=tgen, device=device)
        x1 = X[idx]
        x0 = source_std * torch.randn(batch, C, 32, 32, generator=tgen, device=device)
        t = torch.rand(batch, generator=tgen, device=device)
        tt = t[:, None, None, None]
        x_t = (1 - tt) * x0 + tt * x1
        target = x1 - x0
        cond_b = smooth_cond(cond_all[idx], cond_mask, y_noise_h, tgen)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred = model(x_t, t, cond_b)
            loss = ((target - pred) ** 2).mean()
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()

    def sync() -> None:
        if device.type == "cuda":
            torch.cuda.synchronize()

    name = torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu"
    print(f"benchmarking {config.name}: batch={batch} amp={use_amp} "
          f"params={sum(p.numel() for p in model.parameters())/1e6:.2f}M on {name}")
    model.train()
    for _ in range(args.warmup):
        step()
    sync()
    t0 = time.perf_counter()
    for _ in range(args.iters):
        step()
    sync()
    rate = args.iters / (time.perf_counter() - t0)

    target = int(cfg["train"]["max_iters"])
    hours = target / rate / 3600
    sessions = math.ceil(hours / args.session_hours)
    print(f"\nthroughput   {rate:.2f} it/s at batch {batch}  "
          f"({rate*3600/1000:.1f}k iterations/hour)")
    print(f"full budget  {target} iterations ~ {hours:.1f} h of training")
    print(f"sessions     ~ {sessions} at {args.session_hours:g} h each "
          f"(plus evaluation; budget one spare)")
    if device.type == "cuda":
        peak = torch.cuda.max_memory_allocated() / 1e9
        print(f"peak memory  {peak:.1f} GB of "
              f"{torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
