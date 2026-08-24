"""EXP-3 driver: MNIST inpainting with a small U-Net (qualitative collapse demo).

For a fixed observed top-half y, we generate many completions from different x0
and track (a) pixel-wise variance in the inpainted region -> collapses to ~0 when
the model memorizes, and (b) distance from the generated mean to the nearest
training image -> ~0 + identical to the memorized sample.

    uv run python -m src.train_exp3 --config configs/exp3_inpainting.yaml --smoke-test
    uv run python -m src.train_exp3 --config configs/exp3_inpainting.yaml
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

_nt = os.environ.get("CFM_NUM_THREADS")
if _nt:
    torch.set_num_threads(int(_nt))

from .models.unet_small import SmallUNet
from .problems.inpainting import InpaintingProblem
from .utils import RunPaths, apply_overrides, dump_config, get_device, load_yaml, set_seed


def apply_smoke_test(cfg: dict) -> dict:
    cfg = dict(cfg)
    cfg.setdefault("data", {}); cfg.setdefault("train", {}); cfg.setdefault("eval", {})
    cfg["data"]["N"] = 64
    cfg["train"]["max_iters"] = 200
    cfg["train"]["checkpoints"] = [100, 200]
    cfg["train"]["batch_size"] = 32
    cfg["eval"]["n_conditions"] = 2
    cfg["eval"]["M"] = 8
    cfg["eval"]["n_steps"] = 10
    cfg["run_name"] = cfg.get("run_name", "exp3") + "_smoke"
    return cfg


@torch.no_grad()
def generate(model, cond1: torch.Tensor, M: int, n_steps: int, eps: float,
             source_std: float, gen, device) -> torch.Tensor:
    """Integrate the flow for a single fixed condition, M different x0 (Euler).

    ``cond1`` is (1, 2, 32, 32); broadcast to M. Euler is enough because the
    collapsed trajectory is (near-)straight; stop at t=1-eps (t=1 singularity).
    """
    x = source_std * torch.randn(M, 1, 32, 32, generator=gen, device=device)
    cond = cond1.to(device).expand(M, -1, -1, -1)
    ts = torch.linspace(0.0, 1.0 - eps, n_steps + 1, device=device)
    for i in range(n_steps):
        t = torch.full((M,), float(ts[i]), device=device)
        h = float(ts[i + 1] - ts[i])
        x = x + h * model(x, t, cond)
    return x


@torch.no_grad()
def evaluate(model, problem, cfg, device, gen) -> dict:
    ev = cfg["eval"]
    M, n_steps = ev["M"], ev["n_steps"]
    eps = ev.get("ode_eps", 1e-3)
    source_std = cfg["data"].get("source_std", 1.0)
    mask_inpaint = (1.0 - problem.mask_obs).to(device)   # (1,32,32) 1 on region to fill
    n_pix = float(mask_inpaint.sum())

    n_cond = min(ev["n_conditions"], problem.N)
    idx = torch.linspace(0, problem.N - 1, n_cond).round().long().tolist()
    idx = sorted(set(idx))

    Xdev = problem.X.to(device)
    var_list, nn_list, obs_err = [], [], []
    for i in idx:
        cond1 = problem.condition(problem.X[i:i+1])
        samples = generate(model, cond1, M, n_steps, eps, source_std, gen, device)  # (M,1,32,32)
        # pixel variance in the inpainted region, averaged over those pixels
        var_map = samples.var(dim=0, unbiased=False)              # (1,32,32)
        pix_var = float((var_map * mask_inpaint).sum() / n_pix)
        var_list.append(pix_var)
        # nearest training image to the generated MEAN (memorization)
        mean_img = samples.mean(0, keepdim=True)                  # (1,1,32,32)
        d = ((Xdev - mean_img) ** 2).flatten(1).mean(1)           # (N,)
        nn_list.append(float(d.min()))
        # observed-region reconstruction error (sanity: should stay small)
        obs = problem.mask_obs.to(device)
        oe = float((((mean_img[0] - Xdev[i]) ** 2) * obs).sum() / obs.sum())
        obs_err.append(oe)

    return {
        "pixel_var_inpaint_mean": float(np.mean(var_list)),
        "pixel_var_inpaint_std": float(np.std(var_list)),
        "nn_dist_mean": float(np.mean(nn_list)),
        "obs_recon_err_mean": float(np.mean(obs_err)),
    }


@torch.no_grad()
def save_sample_grid(model, problem, cfg, device, path: Path, n_cond=4, M=6):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    gen = torch.Generator(device=device).manual_seed(2024)
    idx = sorted(set(torch.linspace(0, problem.N - 1, n_cond).round().long().tolist()))
    eps = cfg["eval"].get("ode_eps", 1e-3)
    ncols = M + 3  # observed | M samples | true | nearest-train
    fig, axes = plt.subplots(len(idx), ncols, figsize=(1.1 * ncols, 1.1 * len(idx)),
                             squeeze=False)
    Xdev = problem.X.to(device)
    for r, i in enumerate(idx):
        cond1 = problem.condition(problem.X[i:i+1])
        obs_img = (problem.observation(problem.X[i:i+1])[0, 0]).cpu()
        samples = generate(model, cond1, M, cfg["eval"]["n_steps"], eps,
                           cfg["data"].get("source_std", 1.0), gen, device)
        mean_img = samples.mean(0, keepdim=True)
        d = ((Xdev - mean_img) ** 2).flatten(1).mean(1)
        nn_i = int(d.argmin())

        def show(ax, img, title=None):
            ax.imshow(img.cpu().numpy(), cmap="gray", vmin=-1, vmax=1)
            ax.set_xticks([]); ax.set_yticks([])
            if title:
                ax.set_title(title, fontsize=7)
        show(axes[r][0], obs_img, "observed" if r == 0 else None)
        for m in range(M):
            show(axes[r][1 + m], samples[m, 0], f"sample" if (r == 0 and m == 0) else None)
        show(axes[r][1 + M], problem.X[i, 0], "true" if r == 0 else None)
        show(axes[r][2 + M], problem.X[nn_i, 0], "NN-train" if r == 0 else None)
    fig.suptitle("EXP-3 inpainting: same observed top, different x0", fontsize=9)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130); plt.close(fig)


def train(cfg: dict, out_root: str | Path) -> Path:
    device = get_device(cfg.get("device", "auto"))
    set_seed(cfg["seed"])
    run_dir = Path(out_root) / cfg["run_name"]
    paths = RunPaths.make(run_dir)
    dump_config(cfg, run_dir / "config.yaml")

    dc = cfg["data"]
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg["seed"],
                                       data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"))
    X = problem.X.to(device)
    cond_all = problem.condition(problem.X).to(device)       # (N,2,32,32)

    model = SmallUNet(in_channels=3, out_channels=1,
                      base=cfg["model"].get("base", 32),
                      temb_dim=cfg["model"].get("temb_dim", 128)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["train"].get("lr", 2e-4))
    batch = cfg["train"].get("batch_size", 64)
    source_std = dc.get("source_std", 1.0)
    max_iters = cfg["train"]["max_iters"]
    ckpts = cfg["train"].get("checkpoints") or [200, 1000, 5000, 20000, 50000]
    if isinstance(ckpts, (int, float, str)):
        ckpts = [ckpts]
    ckpts = sorted(set(int(c) for c in ckpts if int(c) <= max_iters) | {max_iters})

    tgen = torch.Generator(device=device).manual_seed(cfg["seed"] + 2)
    egen = torch.Generator(device=device).manual_seed(cfg["seed"] + 3)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[{cfg['run_name']}] UNet params={n_params/1e6:.2f}M N={problem.N} "
          f"max_iters={max_iters} device={device}")

    rows, loss_ema, t0 = [], None, time.time()
    ckset = set(ckpts)
    model.train()
    for it in range(1, max_iters + 1):
        idx = torch.randint(0, problem.N, (batch,), generator=tgen, device=device)
        x1 = X[idx]
        x0 = source_std * torch.randn(batch, 1, 32, 32, generator=tgen, device=device)
        t = torch.rand(batch, generator=tgen, device=device)
        tt = t[:, None, None, None]
        x_t = (1 - tt) * x0 + tt * x1
        target = x1 - x0
        pred = model(x_t, t, cond_all[idx])
        loss = ((target - pred) ** 2).mean()
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        lv = float(loss.detach())
        loss_ema = lv if loss_ema is None else 0.99 * loss_ema + 0.01 * lv

        if it in ckset:
            torch.save({"iter": it, "model_state": model.state_dict()},
                       paths.checkpoints / f"ckpt_{it}.pt")
            model.eval()
            r = evaluate(model, problem, cfg, device, egen)
            r.update({"iter": it, "train_loss": loss_ema, "elapsed_s": time.time() - t0})
            rows.append(r)
            save_sample_grid(model, problem, cfg, device,
                             paths.figures / f"grid_it{it}.png",
                             n_cond=cfg["eval"].get("grid_conditions", 4),
                             M=cfg["eval"].get("grid_M", 6))
            model.train()
            print(f"  it={it:>6d} pix_var_inpaint={r['pixel_var_inpaint_mean']:.4f} "
                  f"nn_dist={r['nn_dist_mean']:.4f} obs_err={r['obs_recon_err_mean']:.4f} "
                  f"loss={loss_ema:.4f} ({time.time()-t0:.0f}s)")

    pd.DataFrame(rows).to_csv(paths.raw / "metrics.csv", index=False)
    print(f"[{cfg['run_name']}] done in {time.time()-t0:.1f}s")
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="results/exp3")
    ap.add_argument("--smoke-test", action="store_true")
    ap.add_argument("--set", nargs="*", default=[], dest="overrides")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    cfg = apply_overrides(cfg, args.overrides)
    if args.smoke_test:
        cfg = apply_smoke_test(cfg)
    train(cfg, args.out)


if __name__ == "__main__":
    main()
