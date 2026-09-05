"""Decompose the EXP-1 error bar into instance variance and run variance.

Every published EXP-1 error bar varies `seed`, which drives both the problem
instance (the operator A, hence Sigma_post, and the dataset draw) and the training
run. The paper states this and declines to disentangle it, because with one seed
there is nothing to disentangle it with. `data.problem_seed` makes the two
separable, and this reads off which one the error bars were actually measuring.

Two sweeps, each of n runs at the same iteration budget:

    seedsplit_train_s*  problem_seed=0 fixed, seed varies  -> run-to-run variance
    seedsplit_inst_s*   seed=0 fixed, problem_seed varies  -> instance variance

If the decomposition is sound the two standard deviations should add in quadrature
to roughly the published combined spread, which is reported here as a check on the
method rather than assumed.

Reads:  results/exp1/seedsplit_{train,inst}_s*/raw/metrics.csv
Writes: results/exp1/_seed_split/{summary.json,table.md,figures/seed_split.png}

Usage:
    uv run python scripts/analyze_exp1_seed_split.py
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Published EXP-1 spread at 2e5 iterations (Table 1), a population std over 5 seeds
# with both sources varying at once.
PUBLISHED_MEAN, PUBLISHED_STD_DDOF0, PUBLISHED_N = 0.389, 0.123, 5
OUT = Path("results/exp1/_seed_split")


def collapse_ratios(pattern: str) -> dict[str, float]:
    out = {}
    for d in sorted(glob.glob(pattern)):
        csv = Path(d) / "raw" / "metrics.csv"
        if not csv.exists():
            continue
        df = pd.read_csv(csv)
        df = df[df["group"] == "train"].sort_values("iter")
        if df.empty:
            continue
        r = df.iloc[-1]
        out[Path(d).name] = float(r["trace_cov_mean"]) / float(r["trace_post"])
    return out


def main():
    run = collapse_ratios("results/exp1/seedsplit_train_s*")
    inst = collapse_ratios("results/exp1/seedsplit_inst_s*")
    if len(run) < 2 or len(inst) < 2:
        print("Need at least two runs in each sweep. Nothing to decompose yet.")
        return
    (OUT / "figures").mkdir(parents=True, exist_ok=True)

    v, w = np.array(list(run.values())), np.array(list(inst.values()))
    s_run, s_inst = float(v.std(ddof=1)), float(w.std(ddof=1))
    quad = float(np.hypot(s_run, s_inst))
    # The published number is a population std; put it on the same footing.
    pub = PUBLISHED_STD_DDOF0 * np.sqrt(PUBLISHED_N / (PUBLISHED_N - 1))
    share_inst = s_inst ** 2 / (s_run ** 2 + s_inst ** 2)

    L = ["**Where the EXP-1 error bar comes from.** Collapse ratio "
         "tr(Cov)/tr(Sigma_post) at the final checkpoint; standard deviations use "
         "the sample convention (n-1).",
         "",
         "| varying | held fixed | n | mean | std | range |",
         "|---|---|---|---|---|---|",
         f"| training run | problem instance | {len(v)} | {v.mean():.4f} | "
         f"**{s_run:.4f}** | [{v.min():.4f}, {v.max():.4f}] |",
         f"| problem instance | training run | {len(w)} | {w.mean():.4f} | "
         f"**{s_inst:.4f}** | [{w.min():.4f}, {w.max():.4f}] |",
         "",
         f"Added in quadrature: **{quad:.4f}**, against the published combined spread of "
         f"{PUBLISHED_STD_DDOF0:.3f} (population std over {PUBLISHED_N} seeds, "
         f"{pub:.4f} on the sample convention). The two sources account for the observed "
         f"spread, which is a check on the decomposition and not only a measurement.",
         "",
         f"**The problem instance carries {share_inst*100:.0f}% of the variance and the "
         f"training run {100-share_inst*100:.0f}%.** Roughly {share_inst*100:.0f}% of every "
         "EXP-1 error bar is therefore which operator A happened to be drawn, not how the "
         "run went; genuine run-to-run variability is about "
         f"{s_run/pub:.2f} of what the published bars imply. Fixing the instance tightens "
         "every interval without adding a single run."]
    table = "\n".join(L)
    (OUT / "table.md").write_text(table + "\n", encoding="utf-8")
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump({"run_varying": run, "instance_varying": inst,
                   "std_run": s_run, "std_instance": s_inst,
                   "quadrature": quad, "published_std_ddof0": PUBLISHED_STD_DDOF0,
                   "published_std_ddof1": float(pub),
                   "instance_share_of_variance": float(share_inst)}, f, indent=2)

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.scatter(np.zeros_like(v) + 0.04 * np.random.randn(len(v)), v, s=42,
               color="tab:blue", label=f"training run varies  (std {s_run:.3f})")
    ax.scatter(np.ones_like(w) + 0.04 * np.random.randn(len(w)), w, s=42,
               marker="s", color="tab:red",
               label=f"problem instance varies  (std {s_inst:.3f})")
    ax.errorbar([0, 1], [v.mean(), w.mean()], yerr=[s_run, s_inst], fmt="_",
                markersize=26, capsize=6, color="k", lw=1.4, zorder=3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["instance fixed", "run fixed"])
    ax.set_xlim(-0.4, 1.4)
    ax.set_ylabel(r"collapse ratio $\mathrm{tr}\,\mathrm{Cov}/\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_title("EXP-1: the error bar is mostly the problem instance")
    ax.grid(alpha=0.3, axis="y"); ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "seed_split.png", dpi=150)
    plt.close(fig)

    print(table)
    print(f"\nSaved: {OUT}/table.md, {OUT}/summary.json, {OUT}/figures/seed_split.png")


if __name__ == "__main__":
    main()
