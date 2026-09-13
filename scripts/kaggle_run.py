#!/usr/bin/env python
"""Run one session of a long EXP-3 run on a short-session host (Kaggle).

A free GPU session is shorter than the 240000-iteration h=4 budget, so the run
has to be chained: each session picks up the previous session's checkpoint,
trains until its wall-clock budget expires, and leaves a checkpoint for the
next. `scripts/verify_resume.py` checks that this changes nothing -- a chained
run is bit-identical to an uninterrupted one.

Typical Kaggle cell (session 1, nothing to resume from):

    !python /kaggle/input/cfm-collapse/scripts/kaggle_run.py \
        --config configs/exp3_cifar_ddpm_h4_long.yaml \
        --work /kaggle/working/results/exp3 \
        --data-root /kaggle/working/data \
        --max-hours 8.0

Session 2 and later, with session 1's notebook output attached as an input
dataset:

    ... --prev /kaggle/input/cfm-ddpm-session1/results/exp3

The script copies the previous run directory into the working directory first,
so metrics.csv, the figures and the archived checkpoints accumulate across
sessions instead of being scattered over several notebook outputs.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _run_name(config: Path, overrides: list[str]) -> str:
    for ov in reversed(overrides or []):
        if ov.startswith("run_name="):
            return ov.split("=", 1)[1]
    import yaml
    with open(config, encoding="utf-8") as f:
        return yaml.safe_load(f)["run_name"]


def _max_iters(config: Path, overrides: list[str]) -> int:
    for ov in reversed(overrides or []):
        if ov.startswith("train.max_iters="):
            return int(float(ov.split("=", 1)[1]))
    import yaml
    with open(config, encoding="utf-8") as f:
        return int(yaml.safe_load(f)["train"]["max_iters"])


def _batch(config: Path, overrides: list[str]) -> int:
    for ov in reversed(overrides or []):
        if ov.startswith("train.batch_size="):
            return int(float(ov.split("=", 1)[1]))
    import yaml
    with open(config, encoding="utf-8") as f:
        return int(yaml.safe_load(f)["train"].get("batch_size", 64))


def find_resume(run_dir: Path) -> Path | None:
    """The furthest-on checkpoint in `run_dir`, resume point or archived."""
    ck = run_dir / "checkpoints"
    if not ck.is_dir():
        return None
    rolling = ck / "ckpt_resume.pt"
    archived = sorted((p for p in ck.glob("ckpt_*.pt") if p.name != "ckpt_resume.pt"),
                      key=lambda p: int(p.stem.split("_")[1]))
    if not rolling.exists():
        return archived[-1] if archived else None
    if not archived:
        return rolling
    import torch
    at = int(torch.load(rolling, map_location="cpu")["iter"])
    return rolling if at >= int(archived[-1].stem.split("_")[1]) else archived[-1]


def checkpoint_iter(path: Path) -> int:
    import torch
    return int(torch.load(path, map_location="cpu")["iter"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True,
                    help="config path, absolute or relative to the repo root")
    ap.add_argument("--work", default="/kaggle/working/results/exp3",
                    help="writable output root for this session")
    ap.add_argument("--prev", default=None,
                    help="previous session's output root, to continue from")
    ap.add_argument("--data-root", default=None,
                    help="directory holding cifar-10-batches-py (default: repo data/)")
    ap.add_argument("--max-hours", type=float, default=8.0,
                    help="wall-clock budget; keep it under the host's session limit")
    ap.add_argument("--set", nargs="*", default=[], dest="overrides",
                    help="extra config overrides passed through to the trainer")
    args = ap.parse_args()

    config = Path(args.config)
    if not config.is_absolute():
        config = ROOT / config
    if not config.exists():
        print(f"config not found: {config}")
        return 2

    run_name = _run_name(config, args.overrides)
    target = _max_iters(config, args.overrides)
    work = Path(args.work).resolve()
    run_dir = work / run_name
    work.mkdir(parents=True, exist_ok=True)

    # ---- carry the previous session forward ------------------------------- #
    if args.prev:
        src = Path(args.prev) / run_name
        if not src.is_dir():
            print(f"--prev given but {src} does not exist; treating this as session 1")
        elif src.resolve() != run_dir.resolve():
            print(f"copying previous session from {src}")
            if run_dir.exists():
                shutil.rmtree(run_dir)
            shutil.copytree(src, run_dir)

    resume = find_resume(run_dir)
    start = 0
    if resume is not None:
        start = checkpoint_iter(resume)
        print(f"resuming from {resume} (iteration {start} of {target})")
        if start >= target:
            print("the run is already complete; nothing to do")
            return 0
    else:
        print(f"no checkpoint found under {run_dir}; starting from scratch")

    overrides = list(args.overrides)
    if args.data_root:
        overrides.append(f"data.data_root={args.data_root}")

    cmd = [sys.executable, "-u", "-m", "src.train_exp3",
           "--config", str(config), "--out", str(work),
           "--max-hours", str(args.max_hours)]
    if resume is not None:
        cmd += ["--resume", str(resume)]
    if overrides:
        cmd += ["--set", *overrides]

    print("$ " + " ".join(cmd), flush=True)
    t0 = time.time()
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    wall = time.time() - t0

    # ---- what the next session needs to know ------------------------------ #
    after = find_resume(run_dir)
    done = checkpoint_iter(after) if after is not None else start
    gained = done - start
    print("\n" + "=" * 68)
    print(f"session finished rc={rc} in {wall/3600:.2f} h")
    print(f"iterations {start} -> {done} of {target}")
    if gained > 0 and wall > 0:
        rate = gained / wall
        batch = _batch(config, args.overrides)
        print(f"throughput {rate:.2f} it/s at batch {batch}, evaluation included "
              f"({rate*3600/1000:.1f}k iterations per hour)")
        remaining = target - done
        if remaining > 0:
            hours = remaining / rate / 3600
            print(f"remaining {remaining} iterations ~ {hours:.1f} h "
                  f"~ {max(1, -(-hours // args.max_hours)):.0f} more session(s) "
                  f"at --max-hours {args.max_hours}")
    if done >= target:
        print("\nrun complete. kaggle_session.sh runs the analyses next; by hand:")
        print(f"  python -m scripts.reeval_exp3_cifar_ddpm --M 256 --n-conditions 48 "
              f"--runs {run_name}")
        print(f"  python -m scripts.beta_trajectory --runs {run_name}")
    elif os.environ.get("CFM_KAGGLE_SESSION"):
        # kaggle_session.sh has its own PREV= form; printing --prev here
        # would put the wrong command into the session log.
        print("\nnot finished: the next session is PREV=<this output> bash /tmp/s.sh")
    else:
        print("\nSave this notebook's output, attach it to the next session as an")
        print("input dataset, and re-run this cell with:")
        print(f"  --prev /kaggle/input/<that-dataset>/{work.name}")
    print("=" * 68)
    return rc


if __name__ == "__main__":
    sys.exit(main())
