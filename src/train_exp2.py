"""EXP-2 driver: Gaussian-mixture posterior, tracking mode coverage vs iteration.

Reuses the same CFM machinery as EXP-1 (models/flows), but the problem has a
multimodal closed-form posterior (src/problems/gmm.py) and the evaluation
measures selective memorization: mode coverage, occupancy TV, and MMD/Sinkhorn
distance to the true posterior, all as a function of training iteration.

    uv run python -m src.train_exp2 --config configs/exp2_gmm.yaml
    uv run python -m src.train_exp2 --config configs/exp2_gmm.yaml --smoke-test
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

from .flows.cfm import CFMTrainer
from .flows.interpolants import LinearInterpolant
from .flows.ode_solver import generate_samples
from .metrics.distances import mmd_rbf, sinkhorn_distance
from .metrics.mode_coverage import mode_coverage
from .metrics.posterior_stats import sample_covariance_trace
from .models.mlp_velocity import build_model
from .problems.gmm import GMMProblem
from .utils import RunPaths, apply_overrides, dump_config, get_device, load_yaml, save_json, set_seed


def apply_smoke_test(cfg: dict) -> dict:
    cfg = dict(cfg)
    cfg.setdefault("data", {}); cfg.setdefault("train", {}); cfg.setdefault("eval", {})
    cfg["data"]["N"] = 64
    cfg["train"]["max_iters"] = 400
    cfg["train"]["checkpoints"] = [100, 400]
    cfg["eval"]["n_eval_train"] = 3
    cfg["eval"]["M"] = 200
    cfg["eval"]["n_steps"] = 20
    cfg["run_name"] = cfg.get("run_name", "exp2") + "_smoke"
    return cfg


@torch.no_grad()
def evaluate(model, problem: GMMProblem, X, Y, cfg, device, gen) -> dict:
    ev = cfg["eval"]
    M = ev["M"]
    n_steps = ev["n_steps"]
    method = ev.get("ode_method", "rk4")
    source_std = cfg["data"].get("source_std", 1.0)

    n_tr = min(ev["n_eval_train"], X.shape[0])
    idx = torch.linspace(0, X.shape[0] - 1, n_tr).round().long().tolist()
    idx = sorted(set(idx))

    recs = []
    post_gen = torch.Generator().manual_seed(cfg["seed"] + 999)
    for i in idx:
        y_i = Y[i]
        samples = generate_samples(model, M, problem.d, y_i, source_std=source_std,
                                   n_steps=n_steps, method=method, generator=gen,
                                   device=device).cpu()
        w, mus, _ = problem.posterior_params(y_i)
        mc = mode_coverage(samples, mus, w)
        true_post = problem.sample_posterior(y_i, M, generator=post_gen)
        mmd = mmd_rbf(samples, true_post)
        try:
            sink = sinkhorn_distance(samples, true_post, blur=0.1)
        except Exception:
            sink = float("nan")
        # distance of generated mean to nearest training point (memorization)
        mean = samples.to(torch.float64).mean(0)
        d_train = float(torch.linalg.norm(X.to(torch.float64) - mean[None, :], dim=1).min())
        recs.append({**mc, "mmd": mmd, "sinkhorn": sink,
                     "trace_cov": sample_covariance_trace(samples),
                     "dist_to_nearest_train": d_train})

    out = {"group": "train", "n_eval": len(recs)}
    for k in recs[0]:
        vals = np.array([r[k] for r in recs], float)
        out[f"{k}_mean"] = float(np.nanmean(vals))
        out[f"{k}_std"] = float(np.nanstd(vals))
    return out


def train(cfg: dict, out_root: str | Path) -> Path:
    device = get_device(cfg.get("device", "auto"))
    set_seed(cfg["seed"])
    run_dir = Path(out_root) / cfg["run_name"]
    paths = RunPaths.make(run_dir)
    dump_config(cfg, run_dir / "config.yaml")

    dc = cfg["data"]
    problem = GMMProblem.create(
        d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=cfg["seed"],
        mode_scale=dc.get("mode_scale", 2.0), mode_std=dc.get("mode_std", 0.5),
        A_kind=dc.get("A_kind", "project_x0"),
    )
    save_json(problem.to_dict(), run_dir / "problem.json")
    X, Y = problem.sample_dataset(dc["N"], seed=cfg["seed"] + 1)

    model = build_model(cfg, data_dim=problem.d, cond_dim=problem.k).to(device)
    interp = LinearInterpolant(sigma=cfg["train"].get("interpolant_sigma", 0.0))
    trainer = CFMTrainer(X, Y, interp, conditional=True,
                         source_std=dc.get("source_std", 1.0),
                         y_noise_h=cfg["train"].get("y_noise_h", 0.0), device=device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["train"].get("lr", 1e-3))

    batch = cfg["train"].get("batch_size", 256)
    max_iters = cfg["train"]["max_iters"]
    ckpts = cfg["train"].get("checkpoints") or [100, 300, 1000, 3000, 10000, 30000, 100000, 200000]
    if isinstance(ckpts, (int, float, str)):
        ckpts = [ckpts]
    ckpts = sorted(set(int(c) for c in ckpts if int(c) <= max_iters) | {max_iters})

    tgen = torch.Generator(device=device).manual_seed(cfg["seed"] + 2)
    egen = torch.Generator(device=device).manual_seed(cfg["seed"] + 3)
    print(f"[{cfg['run_name']}] GMM d={problem.d} k={problem.k} N={dc['N']} "
          f"sigma_obs={dc['sigma_obs']} max_iters={max_iters}")

    rows, loss_ema, t0 = [], None, time.time()
    ckset = set(ckpts)
    model.train()
    for it in range(1, max_iters + 1):
        opt.zero_grad(set_to_none=True)
        loss = trainer.loss_with_model(model, batch, generator=tgen)
        loss.backward(); opt.step()
        lv = float(loss.detach())
        loss_ema = lv if loss_ema is None else 0.99 * loss_ema + 0.01 * lv
        if it in ckset:
            torch.save({"iter": it, "model_state": model.state_dict()},
                       paths.checkpoints / f"ckpt_{it}.pt")
            model.eval()
            r = evaluate(model, problem, X, Y, cfg, device, egen)
            r.update({"iter": it, "train_loss": loss_ema, "elapsed_s": time.time() - t0})
            rows.append(r); model.train()
            print(f"  it={it:>7d} coverage={r['mode_coverage_mean']:.3f} "
                  f"occ_tv={r['occupancy_tv_mean']:.3f} mmd={r['mmd_mean']:.4f} "
                  f"trace_cov={r['trace_cov_mean']:.3f} loss={loss_ema:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(paths.raw / "metrics.csv", index=False)
    print(f"[{cfg['run_name']}] done in {time.time()-t0:.1f}s")
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="results/exp2")
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
