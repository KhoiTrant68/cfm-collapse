#!/usr/bin/env python
"""Chaining a run across sessions must not change the run.

The CIFAR-10 DDPM budget is longer than a free GPU session, so the extended
h=4 run has to stop and restart. That is only legitimate if a stopped-and-
resumed run is the *same* run as an uninterrupted one -- if it were merely
close, "beta is still rising at 60k" would be a statement about the chaining
and not about the model. This script checks it the only way that settles it:
train straight through, train the same budget with a stop in the middle, and
compare every weight.

    python scripts/verify_resume.py            # CPU, ~1 minute

Both the clean stop (`--max-hours` expiring) and an archived checkpoint are
exercised. Exits non-zero if any weight differs.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "exp3_inpainting.yaml"
RUN = "exp3_default_smoke"


def train(out: Path, *extra: str) -> None:
    cmd = [sys.executable, "-m", "src.train_exp3", "--config", str(CONFIG),
           "--smoke-test", "--out", str(out), *extra, "--set", "device=cpu"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        raise SystemExit(f"training failed: {' '.join(cmd)}")


def weights(path: Path) -> dict:
    return torch.load(path, map_location="cpu", weights_only=False)["model_state"]


def compare(a: Path, b: Path, what: str) -> float:
    wa, wb = weights(a), weights(b)
    if set(wa) != set(wb):
        raise SystemExit(f"{what}: different parameter sets")
    worst = max((wa[k] - wb[k]).abs().max().item() for k in wa)
    verdict = "identical" if worst == 0.0 else f"DIFFER by {worst:.3e}"
    print(f"  {what}: {len(wa)} tensors, {verdict}")
    return worst


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="verify_resume_"))
    try:
        print("straight run (200 iterations)")
        train(tmp / "straight")
        ref = tmp / "straight" / RUN / "checkpoints" / "ckpt_200.pt"

        print("resume from the archived iteration-100 checkpoint")
        train(tmp / "fromckpt", "--resume",
              str(tmp / "straight" / RUN / "checkpoints" / "ckpt_100.pt"))

        print("clean mid-stream stop, then resume")
        train(tmp / "stopped", "--max-hours", "0.0015")
        stop = tmp / "stopped" / RUN / "checkpoints" / "ckpt_resume.pt"
        if not stop.exists():
            raise SystemExit("the wall-clock budget wrote no resume checkpoint")
        at = torch.load(stop, map_location="cpu", weights_only=False)["iter"]
        print(f"  stopped at iteration {at}")
        train(tmp / "continued", "--resume", str(stop))

        print("\ncomparing against the uninterrupted run")
        worst = max(
            compare(ref, tmp / "fromckpt" / RUN / "checkpoints" / "ckpt_200.pt",
                    "resumed from archived checkpoint"),
            compare(ref, tmp / "continued" / RUN / "checkpoints" / "ckpt_200.pt",
                    "resumed after a clean stop"),
        )
        print()
        if worst != 0.0:
            print(f"FAIL: chaining changes the run (max weight difference {worst:.3e})")
            return 1
        print("ok: a chained run is bit-identical to an uninterrupted one")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
