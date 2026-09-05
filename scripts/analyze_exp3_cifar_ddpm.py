"""Aggregate the realistic-capacity EXP-3 sweep (CIFAR-10, DDPM U-Net, 35.75M).

This is the first test of Theorem 10 outside d=2. The three h>0 runs aim at three
very different kernel references (tr Cov_h of roughly 79, 276 and 362 against 774
for the full empirical covariance), so agreement is three independent targets hit,
not one target hit three times. The h=0 run is the Proposition 4 control: there the
reference variance is exactly 0, so ratio_to_kernel is undefined by construction and
the columns to read are trace_cov and |mean - x^i|.

Reads:  results/exp3/exp3_cifar_ddpm_h{0,4,5,6}/raw/metrics.csv
Writes: results/exp3/_cifar_ddpm/summary.json
        results/exp3/_cifar_ddpm/table.md
        results/exp3/_cifar_ddpm/figures/cifar_ddpm.png

Usage:
    uv run python scripts/analyze_exp3_cifar_ddpm.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HS = [0, 4, 5, 6]
RUN = "results/exp3/exp3_cifar_ddpm_h{h}"
OUT = Path("results/exp3/_cifar_ddpm")


def load(h: int) -> pd.DataFrame | None:
    csv = Path(RUN.format(h=h)) / "raw" / "metrics.csv"
    if not csv.exists():
        print(f"  [skip] {csv} not found")
        return None
    return pd.read_csv(csv).sort_values("iter")


def main():
    runs = {h: df for h in HS if (df := load(h)) is not None}
    if not runs:
        print("No runs found.")
        return
    (OUT / "figures").mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- table
    L = ["**EXP-3 at realistic capacity** -- CIFAR-10 inpainting, DDPM U-Net "
         "(35.75M parameters), N=2000, 60000 iterations at batch 128 "
         "(3840 gradient samples per training image), seed 0.",
         "",
         "| h | n_eff | tr Cov_h (target) | tr Cov measured | ratio | "
         "&#124;mean - x&#772;_h&#124; | pixel var | NN dist |",
         "|---|---|---|---|---|---|---|---|"]
    summary = {}
    for h, df in runs.items():
        r = df.iloc[-1]
        ratio = "--" if h == 0 else f"{r['ratio_to_kernel_median']:.3f}"
        L.append(f"| {h} | {r['n_eff_mean']:.1f} | {r['trace_cov_kernel_mean']:.4g} | "
                 f"{r['trace_cov_mean']:.4g} | {ratio} | {r['mean_err_kernel_mean']:.4g} | "
                 f"{r['pixel_var_inpaint_mean']:.4g} | {r['nn_dist_mean']:.4g} |")
        summary[h] = {c: float(r[c]) for c in
                      ("iter", "trace_cov_mean", "trace_cov_kernel_mean",
                       "ratio_to_kernel_median", "mean_err_kernel_mean",
                       "n_eff_mean", "pixel_var_inpaint_mean", "nn_dist_mean",
                       "train_loss")}
    L += ["", "At h=0 the kernel reference is a single atom, so tr Cov_h is exactly 0 and "
              "the ratio is undefined; |mean - x&#772;_h| is then the distance to the "
              "memorised training image.", ""]

    # ---- ratio trajectories, the quantity Theorem 10 predicts to be 1 ----
    L += ["**Trajectory of ratio_to_kernel** (target 1).", "",
          "| iter | " + " | ".join(f"h={h}" for h in runs if h) + " |",
          "|---|" + "---|" * len([h for h in runs if h])]
    iters = sorted(set.intersection(*(set(df["iter"]) for h, df in runs.items() if h))) \
        if len([h for h in runs if h]) else []
    for it in iters:
        cells = []
        for h, df in runs.items():
            if not h:
                continue
            v = df[df["iter"] == it]["ratio_to_kernel_median"]
            cells.append(f"{float(v.iloc[-1]):.3f}" if len(v) else "--")
        L.append(f"| {it} | " + " | ".join(cells) + " |")

    # ---- h=0 collapse trajectory ----
    if 0 in runs:
        d0 = runs[0]
        L += ["", "**h=0 collapse trajectory** (Proposition 4 control).", "",
              "| iter | tr Cov | &#124;mean - x^i&#124; | pixel var | NN dist |",
              "|---|---|---|---|---|"]
        for _, r in d0.iterrows():
            L.append(f"| {int(r['iter'])} | {r['trace_cov_mean']:.4g} | "
                     f"{r['mean_err_kernel_mean']:.4g} | "
                     f"{r['pixel_var_inpaint_mean']:.4g} | {r['nn_dist_mean']:.4g} |")
        first, last = d0.iloc[0], d0.iloc[-1]
        fold = first["trace_cov_mean"] / last["trace_cov_mean"]
        L += ["", f"Collapse factor in tr Cov over the run: **{fold:.0f}x** "
                  f"({first['trace_cov_mean']:.4g} to {last['trace_cov_mean']:.4g})."]

    table = "\n".join(L)
    (OUT / "table.md").write_text(table + "\n", encoding="utf-8")
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # --------------------------------------------------------------- figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for h, df in runs.items():
        if not h:
            continue
        ax1.plot(df["iter"], df["ratio_to_kernel_median"], "o-",
                 label=f"$h={h}$  ($\\mathrm{{tr}}\\,\\mathrm{{Cov}}_h={df.iloc[-1]['trace_cov_kernel_mean']:.0f}$)")
    ax1.axhline(1.0, color="k", ls="--", lw=1.0, label="kernel optimum")
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("iteration"); ax1.set_ylabel("ratio to kernel covariance")
    ax1.set_title("does the model track $\\mathrm{Cov}_h$?")
    ax1.legend(fontsize=7); ax1.grid(alpha=0.3)

    if 0 in runs:
        d0 = runs[0]
        ax2.plot(d0["iter"], d0["trace_cov_mean"], "o-", color="tab:red",
                 label="$\\mathrm{tr}\\,\\mathrm{Cov}$")
        ax2.plot(d0["iter"], d0["mean_err_kernel_mean"], "s-", color="tab:blue",
                 label="$\\|\\mathrm{mean}-x^i\\|$")
        ax2.set_xscale("log"); ax2.set_yscale("log")
        ax2.set_xlabel("iteration"); ax2.set_title("$h=0$: collapse onto the atom")
        ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT / "figures" / "cifar_ddpm.png", dpi=150)
    plt.close(fig)

    print(table)
    print(f"\nSaved: {OUT}/table.md, {OUT}/summary.json, {OUT}/figures/cifar_ddpm.png")


if __name__ == "__main__":
    main()
