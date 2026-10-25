"""When do learned composite trajectories leave the tie? Paths against the exact flow.

For trained fields of scripts/learned_composition.py, integrates the composite L3 from the shared
sources and records, on a grid of times, the fraction of all sources with |x_t| < 0.05 and the
median |x_t| over the sources in the exact midpoint basin. The exact composite is integrated from
2048 of the same sources with x_at; the learned ones use ros2_states, as the main evaluation.

    python -u -m scripts.learned_composition_paths --variants cfm_v distill_x_s cfm_x_s
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
import torch

from scripts.learned_composition import (EVAL_RTOL, N_EVAL, N_SOURCES, SOURCE_SEED, Field, arm_coefficients,
                                         learned_mean, ros2_states, w_c, x_at)
from scripts.learned_composition_exact import vector_F

ROOT = pathlib.Path("results/learned_composition_20261021")
TAU_GRID = np.round(np.arange(0.0, 11.5 + 1e-9, 0.1), 6)
CASES = ((1.0, 2.0), (1.0, 10.0), (2.0, 2.0), (2.0, 10.0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="+", default=["cfm_v", "distill_x_s", "cfm_x_s"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    src = torch.randn(N_SOURCES, generator=torch.Generator().manual_seed(SOURCE_SEED))[:N_EVAL]
    exact = {(r["arm"], r["B"], r["r"]): r for r in
             json.loads((ROOT / "exact" / "summary.json").read_text())["rows"]}
    out = {"tau": TAU_GRID.tolist(), "cases": {}}
    sub = src[:2048].double().numpy()
    for B, r in CASES:
        w = r * w_c(B)
        lo, hi = exact[("E4", B, r)]["basin"]
        inside = ((src > lo) & (src < hi)).numpy()
        ex = x_at(sub, vector_F(w, (0.5, 0.5), (B, -B), 0.0), TAU_GRID).T    # (time, source)
        sub_in = (sub > lo) & (sub < hi)
        case = {"exact_occ": (np.abs(ex) < 0.05).mean(1).tolist(),
                "exact_median_abs_in_basin": np.median(np.abs(ex[:, sub_in]), 1).tolist(), "learned": {}}
        for v in args.variants:
            for seed in args.seeds:
                d = ROOT / f"{v}_seed{seed}"
                if not (d / "field.pt").exists():
                    continue
                field = Field(v).to(device)
                field.load_state_dict(torch.load(d / "field.pt", map_location=device))
                field.eval()
                F = learned_mean(field, *arm_coefficients("L3", B, w), device)
                xs = ros2_states(F, src.double().to(device)[:, None], TAU_GRID,
                                 rtol=EVAL_RTOL[0])[:, 0].T.cpu().numpy()          # (time, source)
                case["learned"][f"{v}_seed{seed}"] = {
                    "occ": (np.abs(xs) < 0.05).mean(1).tolist(),
                    "median_abs_in_basin": np.median(np.abs(xs[:, inside]), 1).tolist()}
                print(v, seed, B, r, "occ at tau=4.6, 6.9, 11.5:",
                      [round(float((np.abs(xs[i]) < 0.05).mean()), 4) for i in (46, 69, 115)], flush=True)
        out["cases"][f"B{B:g}_r{r:g}"] = case
    (ROOT / "paths.json").write_text(json.dumps(out), encoding="utf-8")
    print("wrote", ROOT / "paths.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
