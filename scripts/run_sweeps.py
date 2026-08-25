"""Phase-B sweep orchestrator for EXP-1.

Launches many `python -m src.train` runs in parallel with a concurrency limit,
each subprocess thread-capped (CFM_NUM_THREADS) so we saturate the CPU without
oversubscribing. Runs whose metrics.csv already exists are skipped (resume).

Sweeps
------
  P5  : sigma_obs in {0.01, 0.5, 1.0}                (0.1 reuses main runs)
  P6  : N        in {50, 1000, 5000}                 (200 reuses main runs)
  P7y : y_noise_h in {0.01, 0.05, 0.1, 0.5}          (0 reuses main runs)
  P7i : interpolant_sigma in {0.1, 0.3}
  DK  : (d,k) in {(10,1),(10,10)}

Usage
-----
    uv run python scripts/run_sweeps.py --workers 5 --threads 5 --iters 200000
    uv run python scripts/run_sweeps.py --only p7y            # subset
    uv run python scripts/run_sweeps.py --dry-run
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import subprocess
import sys
import time
from pathlib import Path

CFG = "configs/exp1_linear_gaussian.yaml"
OUT = "results/exp1"
# Override for environments without `uv` (e.g. a Kaggle GPU notebook: torch
# there is already CUDA-enabled, and re-resolving deps via uv's pinned
# pytorch-cpu index would downgrade it back to CPU-only).
PYTHON_CMD = os.environ.get("CFM_PYTHON_CMD", "uv run python").split()


def build_specs(iters: int) -> dict[str, list[tuple[str, list[str]]]]:
    # T8: all sweeps raised to 5 seeds for mean +/- std (WORK_ORDER.md T8).
    seeds5 = [0, 1, 2, 3, 4]
    common = [f"train.max_iters={iters}", "model.conditional=true"]
    groups: dict[str, list[tuple[str, list[str]]]] = {}

    # P5 sigma_obs
    p5 = []
    for so in [0.01, 0.5, 1.0]:
        for s in seeds5:
            name = f"p5_sobs{so}_seed{s}"
            p5.append((name, common + [f"seed={s}", f"data.sigma_obs={so}", f"run_name={name}"]))
    groups["p5"] = p5

    # P6 N
    p6 = []
    for N in [50, 1000, 5000]:
        for s in seeds5:
            name = f"p6_N{N}_seed{s}"
            p6.append((name, common + [f"seed={s}", f"data.N={N}", f"run_name={name}"]))
    groups["p6"] = p6

    # P7 y-noise (remedy on the condition)
    p7y = []
    for h in [0.01, 0.05, 0.1, 0.5]:
        for s in seeds5:
            name = f"p7y_h{h}_seed{s}"
            p7y.append((name, common + [f"seed={s}", f"train.y_noise_h={h}", f"run_name={name}"]))
    groups["p7y"] = p7y

    # P7 interpolant-noise (remedy a la 2510.18118). "_c2" = corrected target
    # (eq. C.2, T2) -- the only target implemented now; suffix kept for
    # continuity with the pre-existing 3-seed corrected runs.
    p7i = []
    for sig in [0.1, 0.3]:
        for s in seeds5:
            name = f"p7i_sig{sig}_seed{s}_c2"
            p7i.append((name, common + [f"seed={s}", f"train.interpolant_sigma={sig}", f"run_name={name}"]))
    groups["p7i"] = p7i

    # d/k sweep
    dk = []
    for (d, k) in [(10, 1), (10, 10)]:
        for s in seeds5:
            name = f"dk_d{d}k{k}_seed{s}"
            dk.append((name, common + [f"seed={s}", f"data.d={d}", f"data.k={k}", f"run_name={name}"]))
    groups["dk"] = dk

    return groups


def already_done(name: str) -> bool:
    return Path(OUT, name, "raw", "metrics.csv").exists()


def run_one(name: str, overrides: list[str], threads: int, gpu: int | None) -> tuple[str, int, float]:
    env = dict(os.environ)
    env["CFM_NUM_THREADS"] = str(threads)
    if gpu is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    cmd = [*PYTHON_CMD, "-m", "src.train", "--config", CFG, "--out", OUT, "--set", *overrides]
    t0 = time.time()
    proc = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return name, proc.returncode, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--threads", type=int, default=5)
    ap.add_argument("--iters", type=int, default=200000)
    ap.add_argument("--only", nargs="*", default=None,
                    help="subset of groups: p5 p6 p7y p7i dk")
    ap.add_argument("--gpus", type=int, default=0,
                    help="round-robin CUDA_VISIBLE_DEVICES over 0..gpus-1 per worker "
                         "(e.g. 2 for a dual-T4 notebook). 0 = leave device selection alone.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    groups = build_specs(args.iters)
    keys = args.only or list(groups.keys())
    specs: list[tuple[str, list[str]]] = []
    for k in keys:
        specs.extend(groups[k])

    todo = [(n, ov) for (n, ov) in specs if not already_done(n)]
    print(f"groups={keys}  total={len(specs)}  todo={len(todo)}  skip(done)={len(specs)-len(todo)}")
    for n, ov in todo:
        print("  TODO", n)
    if args.dry_run:
        return
    if not todo:
        print("nothing to do")
        return

    t0 = time.time()
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, n, ov, args.threads, (i % args.gpus) if args.gpus > 0 else None): n
                for i, (n, ov) in enumerate(todo)}
        for fut in cf.as_completed(futs):
            name, rc, dt = fut.result()
            done += 1
            status = "OK" if rc == 0 else f"FAIL(rc={rc})"
            print(f"[{done}/{len(todo)}] {status} {name} ({dt:.0f}s)  "
                  f"elapsed={time.time()-t0:.0f}s", flush=True)
    print(f"ALL DONE in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
