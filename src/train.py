"""EXP-1 training + evaluation driver.

Trains a (conditional or unconditional) flow-matching velocity field on a
linear-Gaussian inverse problem and, at log-spaced checkpoints, measures the
posterior-collapse diagnostics P1/P2/P3 (and provides the P4 baseline by simply
running with ``model.conditional=false``).

Overtraining is the object of study, so there is NO early stopping (spec 7.3).

Usage
-----
    uv run python -m src.train --config configs/exp1_linear_gaussian.yaml
    uv run python -m src.train --config configs/exp1_linear_gaussian.yaml --smoke-test
    uv run python -m src.train --config ... --set train.max_iters=50000 model.conditional=false
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Allow running several seeds in parallel without oversubscribing the CPU:
# set CFM_NUM_THREADS to cap intra-op threads per process.
_nt = os.environ.get("CFM_NUM_THREADS")
if _nt:
    torch.set_num_threads(int(_nt))

from .flows.cfm import CFMTrainer
from .flows.interpolants import LinearInterpolant
from .flows.ode_solver import generate_samples
from .metrics.kernel_theory import cov_expansion, kernel_moments
from .metrics.memorization import memorization_ratio
from .metrics.posterior_stats import posterior_sample_stats, sample_covariance_trace
from .metrics.velocity_error import velocity_error_vs_closed_form
from .models.mlp_velocity import build_model
from .problems.linear_gaussian import LinearGaussianProblem
from .utils import (
    RunPaths,
    apply_overrides,
    default_checkpoints,
    dump_config,
    get_device,
    load_yaml,
    save_json,
    set_seed,
)


# --------------------------------------------------------------------------- #
# Smoke-test overrides (spec Section 7.5): whole pipeline in < ~2 minutes.
# --------------------------------------------------------------------------- #
def apply_smoke_test(cfg: dict) -> dict:
    cfg = dict(cfg)
    cfg.setdefault("data", {})
    cfg.setdefault("train", {})
    cfg.setdefault("eval", {})
    cfg["data"]["N"] = 32
    cfg["train"]["max_iters"] = 300
    cfg["train"]["checkpoints"] = [50, 150, 300]
    cfg["eval"]["n_eval_train"] = 4
    cfg["eval"]["n_heldout"] = 2
    cfg["eval"]["M"] = 128
    cfg["eval"]["n_steps"] = 20
    cfg["eval"]["vel_points"] = 256
    cfg["run_name"] = (cfg.get("run_name", "exp1") + "_smoke")
    return cfg


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #
@torch.no_grad()
def evaluate_conditional(model, problem, X, Y, cfg, device, gen) -> list[dict]:
    """Per-condition collapse diagnostics for train + held-out y (P1/P2/P3)."""
    ev = cfg["eval"]
    M = ev["M"]
    n_steps = ev["n_steps"]
    method = ev.get("ode_method", "rk4")
    eps = ev.get("ode_eps", 1e-3)
    source_std = cfg["data"].get("source_std", 1.0)
    h = float(cfg["train"].get("y_noise_h", 0.0))
    d = problem.d

    rows: list[dict] = []

    def eval_group(indices, group, x_points, y_points):
        recs = []
        for local, y_i in zip(indices, y_points):
            samples = generate_samples(
                model, M, d, y_i, source_std=source_std,
                n_steps=n_steps, method=method, eps=eps, generator=gen, device=device,
            ).cpu()
            mu_post = problem.posterior_mean(y_i)
            x_i = x_points[local] if group == "train" else None
            if group == "train":
                st = posterior_sample_stats(samples, mu_post, X[local], X, own_index=local)
                vel = velocity_error_vs_closed_form(
                    model, X[local], y_i, n_points=ev["vel_points"],
                    source_std=source_std, generator=gen, device=device,
                )
                # Exact kernel-regression reference (Thm 10 / Prop 13). These
                # depend only on (X, Y, h); ratio_to_kernel is the primary P7
                # metric measuring how close the model gets to the *population*
                # optimum, superseding ratio_to_post (WORK_ORDER T1/T4).
                x_bar_h, cov_h, neff = kernel_moments(y_i, X, Y, h)
                trace_kernel = float(torch.trace(cov_h))
                mean = samples.to(torch.float64).mean(0)
                recs.append({
                    **st.as_dict(), **vel,
                    "trace_cov_kernel": trace_kernel,
                    "n_eff": neff,
                    "ratio_to_kernel": st.trace_cov / trace_kernel if trace_kernel > 0 else float("nan"),
                    "mean_err_kernel": float(torch.linalg.norm(mean - x_bar_h)),
                    # per-sample nearest-neighbour memorization ratio (Yoon
                    # et al. 2023 / arXiv:2508.17689, c=1/9), complementing
                    # the sample-mean-based diagnostics above.
                    "memorization_ratio": memorization_ratio(samples, X),
                })
            else:
                # Held-out: no specific x^i; measure variance, posterior-mean
                # error, and distance of the sample mean to the nearest train pt.
                mean = samples.to(torch.float64).mean(0)
                dists = torch.linalg.norm(X.to(torch.float64) - mean[None, :], dim=1)
                recs.append({
                    "trace_cov": sample_covariance_trace(samples),
                    "mean_err_post": float(torch.linalg.norm(mean - mu_post.to(torch.float64))),
                    "dist_to_nearest_train": float(dists.min()),
                    "memorization_ratio": memorization_ratio(samples, X),
                })
        return recs

    # representative training conditions
    n_tr = min(ev["n_eval_train"], X.shape[0])
    tr_idx = torch.linspace(0, X.shape[0] - 1, n_tr).round().long().tolist()
    tr_idx = sorted(set(tr_idx))
    tr_recs = eval_group(tr_idx, "train", X, [Y[i] for i in tr_idx])
    rows.append(_aggregate(tr_recs, group="train", extra={
        "trace_post": problem.posterior_trace(),
    }))

    # held-out conditions (fresh draws from rho, not in the training set)
    n_ho = ev.get("n_heldout", 0)
    if n_ho > 0:
        g_ho = torch.Generator().manual_seed(int(cfg["data"].get("problem_seed", cfg["seed"])) + 7777)
        X_ho = problem.sample_prior(n_ho, generator=g_ho)
        Y_ho = problem.forward(X_ho, generator=g_ho)
        ho_recs = eval_group(list(range(n_ho)), "heldout", X_ho, [Y_ho[i] for i in range(n_ho)])
        rows.append(_aggregate(ho_recs, group="heldout", extra={
            "trace_post": problem.posterior_trace(),
        }))
    return rows


@torch.no_grad()
def evaluate_unconditional(model, problem, X, cfg, device, gen) -> list[dict]:
    """P4 baseline: unconditional generation should NOT collapse to a point."""
    ev = cfg["eval"]
    samples = generate_samples(
        model, ev["M"] * 4, problem.d, None,
        source_std=cfg["data"].get("source_std", 1.0),
        n_steps=ev["n_steps"], method=ev.get("ode_method", "rk4"),
        eps=ev.get("ode_eps", 1e-3), generator=gen, device=device,
    ).cpu()
    data_trace = sample_covariance_trace(X)
    return [{
        "group": "uncond",
        "trace_cov_mean": sample_covariance_trace(samples),
        "trace_cov_std": 0.0,
        "trace_post": problem.posterior_trace(),
        "trace_data": data_trace,
        # per-sample memorization ratio: even though the unconditional flow
        # spreads across the *full* empirical measure (Corollary 6) rather
        # than a single atom, every sample still lands near some training
        # point, so this should also be high at convergence.
        "memorization_ratio_mean": memorization_ratio(samples, X),
        "memorization_ratio_std": 0.0,
        "n_eval": 1,
    }]


def _aggregate(recs: list[dict], group: str, extra: dict) -> dict:
    out = {"group": group, "n_eval": len(recs)}
    if recs:
        keys = recs[0].keys()
        for k in keys:
            vals = np.array([r[k] for r in recs], dtype=float)
            out[f"{k}_mean"] = float(np.nanmean(vals))
            out[f"{k}_std"] = float(np.nanstd(vals))
    out.update(extra)
    return out


# --------------------------------------------------------------------------- #
# Training loop
# --------------------------------------------------------------------------- #
def train(cfg: dict, out_root: str | Path) -> Path:
    device = get_device(cfg.get("device", "auto"))
    set_seed(cfg["seed"])
    # The problem instance (operator A, dataset, held-out queries, adversarial
    # shuffle) and the training run are seeded separately, so that error bars can
    # isolate one from the other. Defaults to cfg["seed"], which reproduces every
    # run made before this split exactly.
    problem_seed = int(cfg["data"].get("problem_seed", cfg["seed"]))

    run_dir = Path(out_root) / cfg["run_name"]
    paths = RunPaths.make(run_dir)
    dump_config(cfg, run_dir / "config.yaml")

    # ---- problem + dataset -------------------------------------------------
    dc = cfg["data"]
    problem = LinearGaussianProblem.create(
        d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=problem_seed,
        prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"),
    )
    save_json(problem.to_dict(), run_dir / "problem.json")
    X, Y = problem.sample_dataset(dc["N"], seed=problem_seed + 1)

    if dc.get("shuffle_labels", False):
        # Adversarial-pairing ablation (cf. gradvar2025's shuffled-target test):
        # permute Y relative to X so (x^i, y^i) is no longer the true generative
        # pair. Proposition 4 only needs the y^i to be pairwise distinct -- it
        # never uses A or sigma_obs -- so the theory predicts collapse to the
        # *shuffled* x^i regardless. mu_post(y_i) below still uses the true A,
        # so it now targets an x unrelated to the shuffled x^i: a converging
        # mean_err_train_point alongside a non-converging mean_err_post is the
        # signature that memorisation tracks the (adversarial) label identity,
        # not any real posterior structure.
        g_shuf = torch.Generator().manual_seed(problem_seed + 9999)
        perm = torch.randperm(X.shape[0], generator=g_shuf)
        Y = Y[perm]
        save_json({"perm": perm.tolist()}, run_dir / "shuffle_perm.json")

    # ---- model + trainer ---------------------------------------------------
    conditional = cfg["model"].get("conditional", True)
    cond_dim = problem.k if conditional else 0
    model = build_model(cfg, data_dim=problem.d, cond_dim=cond_dim).to(device)

    interp = LinearInterpolant(sigma=cfg["train"].get("interpolant_sigma", 0.0))
    trainer = CFMTrainer(
        X, Y if conditional else None, interp, conditional=conditional,
        source_std=dc.get("source_std", 1.0),
        y_noise_h=cfg["train"].get("y_noise_h", 0.0),
        target_noise_rho=cfg["train"].get("target_noise_rho", 0.0), device=device,
    )

    opt_name = cfg["train"].get("optimizer", "adam").lower()
    lr = cfg["train"].get("lr", 1e-3)
    if opt_name == "adam":
        opt = torch.optim.Adam(model.parameters(), lr=lr)
    elif opt_name == "sgd":
        opt = torch.optim.SGD(
            model.parameters(), lr=lr,
            momentum=cfg["train"].get("momentum", 0.9),
        )
    else:
        raise ValueError(f"Unknown train.optimizer={opt_name!r} (expected adam|sgd)")
    batch_size = cfg["train"].get("batch_size", 256)
    max_iters = cfg["train"]["max_iters"]

    lr_schedule = cfg["train"].get("lr_schedule", "none").lower()
    if lr_schedule == "none":
        sched = None
    elif lr_schedule == "cosine":
        lr_min = cfg["train"].get("lr_min", lr * 1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(
            opt, T_max=max_iters, eta_min=lr_min,
        )
    else:
        raise ValueError(f"Unknown train.lr_schedule={lr_schedule!r} (expected none|cosine)")

    checkpoints = cfg["train"].get("checkpoints") or default_checkpoints(max_iters)
    if isinstance(checkpoints, (int, float, str)):
        checkpoints = [checkpoints]
    checkpoints = sorted(set(int(c) for c in checkpoints if int(c) <= max_iters) | {max_iters})

    train_gen = torch.Generator(device=device).manual_seed(cfg["seed"] + 2)
    eval_gen = torch.Generator(device=device).manual_seed(cfg["seed"] + 3)

    print(f"[{cfg['run_name']}] device={device} conditional={conditional} "
          f"N={dc['N']} d={problem.d} k={problem.k} sigma_obs={dc['sigma_obs']} "
          f"width={cfg['model'].get('width')} depth={cfg['model'].get('depth')} "
          f"optimizer={opt_name} lr={lr} lr_schedule={lr_schedule} "
          f"shuffle_labels={dc.get('shuffle_labels', False)} "
          f"max_iters={max_iters} trace_post={problem.posterior_trace():.5f}")

    metric_rows: list[dict] = []
    loss_ema = None
    t_start = time.time()

    def run_eval(it: int):
        model.eval()
        if conditional:
            rows = evaluate_conditional(model, problem, X, Y, cfg, device, eval_gen)
        else:
            rows = evaluate_unconditional(model, problem, X, cfg, device, eval_gen)
        cur_lr = opt.param_groups[0]["lr"]
        for r in rows:
            r.update({"iter": it, "train_loss": loss_ema, "lr": cur_lr,
                      "elapsed_s": time.time() - t_start})
            metric_rows.append(r)
        model.train()
        # brief console summary
        for r in rows:
            tc = r.get("trace_cov_mean", float("nan"))
            print(f"  iter={it:>7d} [{r['group']:>7s}] trace_cov={tc:.5e} "
                  f"trace_post={r.get('trace_post', float('nan')):.5e} "
                  f"vel_rel={r.get('vel_rel_err_mean_mean', float('nan')):.4f} "
                  f"mean_err_x={r.get('mean_err_train_point_mean', float('nan')):.4e} "
                  f"loss={loss_ema if loss_ema is None else round(loss_ema,5)}")

    # checkpoint at iter 0 (random init) is informative too
    ckpt_set = set(checkpoints)
    model.train()
    for it in range(1, max_iters + 1):
        opt.zero_grad(set_to_none=True)
        loss = trainer.loss_with_model(model, batch_size, generator=train_gen)
        loss.backward()
        opt.step()
        if sched is not None:
            sched.step()
        lv = float(loss.detach())
        loss_ema = lv if loss_ema is None else 0.99 * loss_ema + 0.01 * lv

        if it in ckpt_set:
            torch.save({"iter": it, "model_state": model.state_dict()},
                       paths.checkpoints / f"ckpt_{it}.pt")
            run_eval(it)

    df = pd.DataFrame(metric_rows)
    csv_path = paths.raw / "metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"[{cfg['run_name']}] done in {time.time()-t_start:.1f}s -> {csv_path}")
    return run_dir


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="results/exp1")
    ap.add_argument("--smoke-test", action="store_true")
    ap.add_argument("--set", nargs="*", default=[], dest="overrides",
                    help="Dotted overrides, e.g. train.max_iters=1000 model.conditional=false")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    cfg = apply_overrides(cfg, args.overrides)
    if args.smoke_test:
        cfg = apply_smoke_test(cfg)
    train(cfg, args.out)


if __name__ == "__main__":
    main()
