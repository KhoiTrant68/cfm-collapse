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
from .metrics.kernel_theory import kernel_moments_trace
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
             source_std: float, gen, device, channels: int = 1) -> torch.Tensor:
    """Integrate the flow for a single fixed condition, M different x0 (Euler).

    ``cond1`` is (1, C+1, 32, 32); broadcast to M. Euler is enough because the
    collapsed trajectory is (near-)straight; stop at t=1-eps (t=1 singularity).
    """
    x = source_std * torch.randn(M, channels, 32, 32, generator=gen, device=device)
    cond = cond1.to(device).expand(M, -1, -1, -1)
    ts = torch.linspace(0.0, 1.0 - eps, n_steps + 1, device=device)
    for i in range(n_steps):
        t = torch.full((M,), float(ts[i]), device=device)
        h = float(ts[i + 1] - ts[i])
        x = x + h * model(x, t, cond)
    return x


def _nan_safe(fn, values) -> float:
    """Apply a nan-aware reduction, returning nan for an all-nan input.

    numpy warns on an all-nan slice, which at h=0 is every checkpoint: the ratio to
    a zero reference is undefined there by construction. Suppressing the warning at
    the point where the undefinedness is meaningful keeps real warnings visible.
    """
    arr = np.asarray(values, dtype=float)
    return float("nan") if arr.size == 0 or np.all(np.isnan(arr)) else float(fn(arr))


def smooth_cond(cond: torch.Tensor, mask_obs: torch.Tensor, h: float,
                gen=None) -> torch.Tensor:
    """Label smoothing for the image problem: y~ = y + h*eps.

    The conditioning tensor is [observed image ; mask]; the noise is added to the
    observed-image channels only, and only where the mask is 1, so the mask
    channel keeps identifying which pixels are observed. h=0 returns ``cond``
    untouched, so every pre-existing run is bit-identical.
    """
    if h <= 0.0:
        return cond
    C = cond.shape[1] - 1
    noise = torch.randn(cond.shape[0], C, *cond.shape[2:], generator=gen,
                        device=cond.device, dtype=cond.dtype)
    out = cond.clone()
    out[:, :C] = out[:, :C] + h * noise * mask_obs.to(cond.device)
    return out


def cond_vectors(problem) -> torch.Tensor:
    """The conditioning variable y^i as a flat vector over observed pixels only.

    This is the ``y`` of the theory: distances between these vectors are what the
    label kernel K_h acts on, so the mask channel (identical for every i) and the
    unobserved pixels (identically zero) must not be included -- they would add a
    constant to every pairwise distance and change nothing, but they would make
    the reported dimension k meaningless.
    """
    sel = problem.mask_obs.flatten().bool()                     # (32*32,)
    flat = problem.X.flatten(2)                                 # (N,C,1024)
    return flat[:, :, sel].flatten(1)                           # (N, C*|obs|)


@torch.no_grad()
def evaluate(model, problem, cfg, device, gen) -> dict:
    ev = cfg["eval"]
    M, n_steps = ev["M"], ev["n_steps"]
    eps = ev.get("ode_eps", 1e-3)
    source_std = cfg["data"].get("source_std", 1.0)
    mask_inpaint = (1.0 - problem.mask_obs).to(device)   # (1,32,32) 1 on region to fill
    n_pix = float(mask_inpaint.sum()) * problem.channels  # per-channel pixel count

    n_cond = min(ev["n_conditions"], problem.N)
    idx = torch.linspace(0, problem.N - 1, n_cond).round().long().tolist()
    idx = sorted(set(idx))

    Xdev = problem.X.to(device)
    h = float(cfg["train"].get("y_noise_h", 0.0))
    Xflat = Xdev.flatten(1).to(torch.float64)                 # (N,d) for kernel moments
    Yvec = cond_vectors(problem).to(device).to(torch.float64)  # (N,k)
    var_list, nn_list, obs_err = [], [], []
    trace_meas, trace_kern, ratio_kern, meanerr_kern, neff_list = [], [], [], [], []
    for i in idx:
        cond1 = problem.condition(problem.X[i:i+1])
        samples = generate(model, cond1, M, n_steps, eps, source_std, gen, device,
                           channels=problem.channels)  # (M,C,32,32)
        # ---- kernel-theory reference (Thm 10 / Prop 13), in image space ----
        sflat = samples.flatten(1).to(torch.float64)          # (M,d)
        tr_meas = float(sflat.var(dim=0, unbiased=False).sum())
        x_bar_h, tr_kern, n_ef = kernel_moments_trace(Yvec[i], Xflat, Yvec, h)
        trace_meas.append(tr_meas)
        trace_kern.append(tr_kern)
        # At h=0 the kernel puts all its mass on one atom, so tr Cov_h is exactly 0
        # and the ratio is undefined by construction, not by numerical accident --
        # read trace_cov and mean_err_kernel there instead.
        ratio_kern.append(tr_meas / tr_kern if tr_kern > 0 else float("nan"))
        meanerr_kern.append(float((sflat.mean(0) - x_bar_h).norm()))
        neff_list.append(n_ef)
        # pixel variance in the inpainted region, averaged over those pixels
        var_map = samples.var(dim=0, unbiased=False)              # (C,32,32)
        pix_var = float((var_map * mask_inpaint).sum() / n_pix)
        var_list.append(pix_var)
        # nearest training image to the generated MEAN (memorization)
        mean_img = samples.mean(0, keepdim=True)                  # (1,C,32,32)
        d = ((Xdev - mean_img) ** 2).flatten(1).mean(1)           # (N,)
        nn_list.append(float(d.min()))
        # observed-region reconstruction error (sanity: should stay small)
        obs = problem.mask_obs.to(device)
        obs_n = float(obs.sum()) * problem.channels
        oe = float((((mean_img[0] - Xdev[i]) ** 2) * obs).sum() / obs_n)
        obs_err.append(oe)

    return {
        "pixel_var_inpaint_mean": float(np.mean(var_list)),
        "pixel_var_inpaint_std": float(np.std(var_list)),
        "nn_dist_mean": float(np.mean(nn_list)),
        "obs_recon_err_mean": float(np.mean(obs_err)),
        # kernel reference (Thm 10 / Prop 13) -- the P7 quantities, in image space
        "trace_cov_mean": float(np.mean(trace_meas)),
        "trace_cov_kernel_mean": float(np.mean(trace_kern)),
        "ratio_to_kernel_mean": _nan_safe(np.nanmean, ratio_kern),
        "ratio_to_kernel_median": _nan_safe(np.nanmedian, ratio_kern),
        "mean_err_kernel_mean": float(np.mean(meanerr_kern)),
        "n_eff_mean": float(np.mean(neff_list)),
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
    C = problem.channels
    for r, i in enumerate(idx):
        cond1 = problem.condition(problem.X[i:i+1])
        obs_img = (problem.observation(problem.X[i:i+1])[0]).cpu()
        samples = generate(model, cond1, M, cfg["eval"]["n_steps"], eps,
                           cfg["data"].get("source_std", 1.0), gen, device, channels=C)
        mean_img = samples.mean(0, keepdim=True)
        d = ((Xdev - mean_img) ** 2).flatten(1).mean(1)
        nn_i = int(d.argmin())

        def show(ax, img, title=None):
            # img: (C,32,32) in [-1,1] -> HxW (gray) or HxWx3 in [0,1] (RGB)
            arr = img.cpu().numpy()
            if C == 1:
                ax.imshow(arr[0], cmap="gray", vmin=-1, vmax=1)
            else:
                rgb = ((arr.transpose(1, 2, 0) + 1.0) / 2.0).clip(0.0, 1.0)
                ax.imshow(rgb)
            ax.set_xticks([]); ax.set_yticks([])
            if title:
                ax.set_title(title, fontsize=7)
        show(axes[r][0], obs_img, "observed" if r == 0 else None)
        for m in range(M):
            show(axes[r][1 + m], samples[m], f"sample" if (r == 0 and m == 0) else None)
        show(axes[r][1 + M], problem.X[i], "true" if r == 0 else None)
        show(axes[r][2 + M], problem.X[nn_i], "NN-train" if r == 0 else None)
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
                                       mask_kind=dc.get("mask_kind", "bottom_half"),
                                       dataset=dc.get("dataset", "mnist"))
    C = problem.channels
    X = problem.X.to(device)
    cond_all = problem.condition(problem.X).to(device)       # (N,C+1,32,32)

    arch = cfg["model"].get("arch", "small")
    if arch == "small":
        model = SmallUNet(in_channels=2 * C + 1, out_channels=C,
                          base=cfg["model"].get("base", 32),
                          temb_dim=cfg["model"].get("temb_dim", 128)).to(device)
    elif arch == "ddpm":
        from .models.unet import UNet
        model = UNet(in_channels=2 * C + 1, out_channels=C,
                     base=cfg["model"].get("base", 128),
                     ch_mult=tuple(cfg["model"].get("ch_mult", [1, 2, 2, 2])),
                     num_res_blocks=cfg["model"].get("num_res_blocks", 2),
                     attn_resolutions=tuple(cfg["model"].get("attn_resolutions", [16])),
                     temb_dim=cfg["model"].get("temb_dim", 512),
                     dropout=cfg["model"].get("dropout", 0.0)).to(device)
    else:
        raise ValueError(f"Unknown model.arch={arch!r} (expected small|ddpm)")
    opt = torch.optim.Adam(model.parameters(), lr=cfg["train"].get("lr", 2e-4))
    batch = cfg["train"].get("batch_size", 64)
    source_std = dc.get("source_std", 1.0)
    max_iters = cfg["train"]["max_iters"]
    ckpts = cfg["train"].get("checkpoints") or [200, 1000, 5000, 20000, 50000]
    if isinstance(ckpts, (int, float, str)):
        ckpts = [ckpts]
    ckpts = sorted(set(int(c) for c in ckpts if int(c) <= max_iters) | {max_iters})
    # Evaluation happens at every entry of `checkpoints`; writing the weights out
    # is separate. One DDPM checkpoint is 143 MB, so the six-entry schedule costs
    # 858 MB per run, and eight seed runs filled the training machine's quota
    # mid-flight, killing two runs at iteration 20000. Only the final weights are
    # ever re-read (by reeval_exp3_cifar_ddpm.py), so a run that is not being
    # inspected along the way can set `save_checkpoints: [60000]` and still record
    # the full metric trajectory.
    keep = cfg["train"].get("save_checkpoints")
    if keep is None:
        keep = set(ckpts)
    elif not isinstance(keep, (list, tuple)):
        keep = {int(keep)}
    else:
        keep = {int(c) for c in keep}

    y_noise_h = float(cfg["train"].get("y_noise_h", 0.0))
    use_amp = bool(cfg["train"].get("amp", False)) and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    tgen = torch.Generator(device=device).manual_seed(cfg["seed"] + 2)
    egen = torch.Generator(device=device).manual_seed(cfg["seed"] + 3)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[{cfg['run_name']}] arch={arch} params={n_params/1e6:.2f}M N={problem.N} "
          f"max_iters={max_iters} h={cfg['train'].get('y_noise_h', 0.0)} device={device}")

    rows, loss_ema, t0 = [], None, time.time()
    ckset = set(ckpts)
    model.train()
    for it in range(1, max_iters + 1):
        idx = torch.randint(0, problem.N, (batch,), generator=tgen, device=device)
        x1 = X[idx]
        x0 = source_std * torch.randn(batch, C, 32, 32, generator=tgen, device=device)
        t = torch.rand(batch, generator=tgen, device=device)
        tt = t[:, None, None, None]
        x_t = (1 - tt) * x0 + tt * x1
        target = x1 - x0
        cond_b = smooth_cond(cond_all[idx], problem.mask_obs, y_noise_h, tgen)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred = model(x_t, t, cond_b)
            loss = ((target - pred) ** 2).mean()
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        lv = float(loss.detach())
        loss_ema = lv if loss_ema is None else 0.99 * loss_ema + 0.01 * lv

        if it in ckset:
            if it in keep:
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
                  f"nn_dist={r['nn_dist_mean']:.4f} ratio_kern={r['ratio_to_kernel_median']:.3f} "
                  f"n_eff={r['n_eff_mean']:.1f} loss={loss_ema:.4f} ({time.time()-t0:.0f}s)")

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
