"""Instance variance versus optimisation variance, from the 2 x 2 Kaggle runs.

Reads   results/exp3/exp3_cifar_ddpm_split_p{P}_s{S}/raw/metrics.csv
Writes  results/exp3/_variance_split/split.json and split.md

For each metric at the last common iteration it gives the four values and two contrasts:

    optimisation spread   runs that share problem_seed and differ in seed
    instance spread       runs that share seed and differ in problem_seed

With two levels of each factor these are differences, not variances, so they are reported as
absolute and relative (to the grand mean) gaps, on the log scale for tr Cov. A 2 x 2 design cannot
support a variance-component estimate with an error bar; the point is to see which contrast is
larger and by how much, and to say so plainly.

    uv run python scripts/analyze_variance_split.py
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

RUN = "results/exp3/exp3_cifar_ddpm_split_p{p}_s{s}/raw/metrics.csv"
OUT = Path("results/exp3/_variance_split")
METRICS = ["trace_cov_mean", "ratio_to_kernel_median", "n_eff_mean", "nn_dist_mean", "train_loss"]
LOG_METRICS = {"trace_cov_mean", "ratio_to_kernel_median", "train_loss"}


def main() -> None:
    rows = {}
    for p, s in itertools.product((0, 1), (0, 1)):
        f = Path(RUN.format(p=p, s=s))
        if f.exists():
            rows[(p, s)] = pd.read_csv(f)
    if len(rows) < 2:
        raise SystemExit("need at least two finished runs; nothing to compare")
    it = min(int(df["iter"].max()) for df in rows.values())
    last = {k: df[df["iter"] == it].iloc[-1] for k, df in rows.items()}
    print(f"comparing at iteration {it} with runs {sorted(rows)}")

    out = {"iteration": it, "runs": [list(k) for k in sorted(rows)], "metrics": {}}
    lines = [f"Compared at iteration {it}. Runs (problem_seed, seed): {sorted(rows)}.", "",
             "| metric | " + " | ".join(f"p{p} s{s}" for p, s in sorted(rows)) +
             " | optimisation gap | instance gap |", "|---|" + "---|" * (len(rows) + 2)]
    for m in METRICS:
        if m not in next(iter(last.values())).index:
            continue
        v = {k: float(last[k][m]) for k in last}
        g = (lambda x: np.log(x)) if m in LOG_METRICS else (lambda x: x)

        def gap(pairs):
            ds = [abs(g(v[a]) - g(v[b])) for a, b in pairs if a in v and b in v and v[a] > 0 and v[b] > 0]
            return float(np.mean(ds)) if ds else float("nan")

        opt = gap([((0, 0), (0, 1)), ((1, 0), (1, 1))])   # same instance, different seed
        ins = gap([((0, 0), (1, 0)), ((0, 1), (1, 1))])   # same seed, different instance
        out["metrics"][m] = {"values": {f"p{p}s{s}": x for (p, s), x in v.items()},
                             "optimisation_gap": opt, "instance_gap": ins,
                             "scale": "log" if m in LOG_METRICS else "linear"}
        lines.append(f"| {m} | " + " | ".join(f"{v.get(k, float('nan')):.4g}" for k in sorted(rows)) +
                     f" | {opt:.3g} | {ins:.3g} |")
    lines += ["", "Gaps are mean absolute differences (natural log for tr Cov, ratio and loss). "
              "A larger optimisation gap than instance gap says the spread in the paper's "
              "three-instance runs is mostly training randomness; the reverse says it is the instance."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "split.json").write_text(json.dumps(out, indent=2))
    (OUT / "split.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
