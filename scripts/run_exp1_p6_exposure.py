"""P6 (collapse vs N) with the per-image exposure held fixed.

The published P6 sweep runs every N at a fixed 2e5 iterations and batch 256, so
the number of gradient samples each training point receives is 200000*256/N --
exactly proportional to 1/N. "Collapse ratio falls with N" and "collapse ratio
falls as optimisation progress per point falls" are therefore the same curve, and
the fixed-budget sweep cannot separate them. The EXP-3 image sweep showed the
distinction matters: most of the apparent N-dependence there was a budget effect
(spread 14.9x at fixed budget, 2.3x at fixed exposure).

This runs the EXP-1 control: the same N values, but with max_iters scaled so each
training point receives the same 51200 gradient samples (the value N=1000 gets in
the published sweep), against which the fixed-budget numbers can be read.

    N=50   ->    10000 iters
    N=200  ->    40000 iters
    N=1000 ->   200000 iters   (unchanged; this is the anchor)
    N=5000 ->  1000000 iters

Total is 1.25M iterations per seed. Runs are sequential on one GPU.

    uv run python scripts/run_exp1_p6_exposure.py [--seeds 5] [--gpu 0]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

CFG = "configs/exp1_linear_gaussian.yaml"
OUT = "results/exp1"
EXPOSURE = 51200          # gradient samples per training point
BATCH = 256
NS = [50, 200, 1000, 5000]


def iters_for(N: int) -> int:
    return int(EXPOSURE * N / BATCH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--python", default=os.environ.get("CFM_PYTHON_CMD", ".venv/bin/python"))
    args = ap.parse_args()

    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(args.gpu))
    Path("logs").mkdir(exist_ok=True)
    total = len(NS) * args.seeds
    done = 0
    t0 = time.time()
    for N in NS:
        it = iters_for(N)
        for s in range(args.seeds):
            name = f"p6exp_N{N}_seed{s}"
            if (Path(OUT) / name / "raw" / "metrics.csv").exists():
                print(f"[skip] {name} already done"); done += 1; continue
            cmd = [args.python, "-u", "-m", "src.train", "--config", CFG,
                   "--out", OUT, "--set",
                   f"seed={s}", f"data.N={N}", f"train.max_iters={it}",
                   "model.conditional=true", f"run_name={name}"]
            print(f"[{done+1}/{total}] {name}: N={N} iters={it} "
                  f"(exposure {EXPOSURE}/point)  elapsed {time.time()-t0:.0f}s",
                  flush=True)
            with open(f"logs/{name}.log", "w") as log:
                rc = subprocess.run(cmd, env=env, stdout=log,
                                    stderr=subprocess.STDOUT).returncode
            if rc != 0:
                print(f"    FAILED rc={rc} -- see logs/{name}.log", flush=True)
            done += 1
    print(f"P6 EXPOSURE SWEEP DONE in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
