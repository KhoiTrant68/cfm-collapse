"""EXP-1 with the problem instance held fixed, so error bars mean one thing.

Every published EXP-1 error bar varies `seed`, which drives both the problem
instance (the operator A, hence Sigma_post, and the dataset draw) and the training
run. A spread of 0.035-0.186 in tr Cov at 1e6 iterations therefore says nothing
about run-to-run variability on its own: part of it is that some draws of A give
an intrinsically harder problem. The paper flags this without being able to
separate it.

`data.problem_seed` (added alongside this script, defaulting to `seed` so that
every earlier run reproduces exactly) fixes the instance. This runs two sweeps:

  training  -- instance fixed at problem_seed=0, seed varies: pure run-to-run spread
  instance  -- seed fixed at 0, problem_seed varies: pure instance-to-instance spread

Their variances should roughly add up to the spread of the published sweep, which
is a check on the decomposition as well as a measurement.

These are the small d=2 MLP runs: measured 221 it/s, GPU at 6%, one CPU core each,
so they are launched together rather than one at a time.

    uv run python scripts/run_exp1_seed_split.py [--seeds 10] [--iters 200000]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path

CFG = "configs/exp1_linear_gaussian.yaml"
OUT = "results/exp1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--iters", type=int, default=200000)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--max-parallel", type=int, default=10)
    ap.add_argument("--python", default=os.environ.get("CFM_PYTHON_CMD", ".venv/bin/python"))
    args = ap.parse_args()

    jobs = []
    for s in range(args.seeds):
        # vary the training run, hold the instance
        jobs.append((f"seedsplit_train_s{s}", [f"seed={s}", "data.problem_seed=0"]))
        # vary the instance, hold the training run
        jobs.append((f"seedsplit_inst_s{s}", ["seed=0", f"data.problem_seed={s}"]))

    Path("logs").mkdir(exist_ok=True)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(args.gpu), OMP_NUM_THREADS="2")
    t0 = time.time()
    running: list[tuple[str, subprocess.Popen]] = []
    pending = list(jobs)

    while pending or running:
        while pending and len(running) < args.max_parallel:
            name, overrides = pending.pop(0)
            if (Path(OUT) / name / "raw" / "metrics.csv").exists():
                print(f"[skip] {name}", flush=True)
                continue
            cmd = [args.python, "-u", "-m", "src.train", "--config", CFG, "--out", OUT,
                   "--set", *overrides, f"train.max_iters={args.iters}",
                   "model.conditional=true", f"run_name={name}"]
            log = open(f"logs/{name}.log", "w")
            running.append((name, subprocess.Popen(cmd, env=env, stdout=log,
                                                   stderr=subprocess.STDOUT)))
            print(f"[launch] {name}  ({len(running)} running, {len(pending)} queued, "
                  f"{time.time()-t0:.0f}s)", flush=True)
        done = [(n, p) for n, p in running if p.poll() is not None]
        for n, p in done:
            print(f"[done] {n} rc={p.returncode} ({time.time()-t0:.0f}s)", flush=True)
        running = [(n, p) for n, p in running if p.poll() is None]
        if running and not done:
            time.sleep(10)
    print(f"SEED SPLIT SWEEP DONE in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
