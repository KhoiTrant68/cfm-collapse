"""Aggregate EXP-3 (MNIST inpainting) N-sweep runs into summary tables + figure.

Mirrors the P6 (N-sweep) treatment of EXP-1 (Table 6, Figure 2a), but for the
image experiment: report inpaint-region pixel variance and nearest-training-image
distance as a function of N.

Two sweeps are reported, because either one alone is misleading. At a fixed
iteration budget the per-image gradient exposure is 30000*64/N, i.e. exactly
proportional to 1/N, so a "collapse vs N" curve measured that way cannot be told
apart from a "collapse vs optimisation progress" curve. Sweep B therefore holds
the per-image exposure fixed at 3840 gradient samples instead (N=100 at 6k
iterations, N=500 at 30k, N=2000 at 120k), and `matched_loss_table` adds a third
control that lines the runs up by training loss.

Sweep A (constant budget, 30000 iters, 3 seeds):
    results/exp3/exp3_N100_gpu{,_seed1,_seed2}/raw/metrics.csv
    results/exp3/exp3_N500_gpu, exp3_mnist_seed1, exp3_mnist_seed2
    results/exp3/exp3_N2000_gpu{,_seed1,_seed2}
Sweep B (constant exposure, 3840 samples/image, seed 0):
    results/exp3/exp3_N100_e6k, exp3_N500_gpu, exp3_N2000_e120k

Writes: results/exp3/_n_sweep/summary.json
        results/exp3/_n_sweep/figures/n_sweep.png
        results/exp3/_n_sweep/n_sweep_table.md   (paste straight into the paper)

Usage:
    uv run python scripts/analyze_exp3_n_sweep.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BUDGET_ITERS = 30000
EXPOSURE = 3840          # gradient samples per training image, = 30000*64/500

# N -> list of run directories, all at BUDGET_ITERS.
SWEEP_BUDGET = {
    100:  ["exp3_N100_gpu", "exp3_N100_gpu_seed1", "exp3_N100_gpu_seed2"],
    500:  ["exp3_N500_gpu", "exp3_mnist_seed1", "exp3_mnist_seed2"],
    2000: ["exp3_N2000_gpu", "exp3_N2000_gpu_seed1", "exp3_N2000_gpu_seed2"],
}
# N -> (run directory, iteration), each giving EXPOSURE samples per image.
SWEEP_EXPOSURE = {
    100:  ("exp3_N100_e6k", 6000),
    500:  ("exp3_N500_gpu", 30000),
    2000: ("exp3_N2000_e120k", 120000),
}
METRICS = ("pixel_var_inpaint_mean", "nn_dist_mean")


def read(run: str) -> pd.DataFrame | None:
    csv = Path("results/exp3") / run / "raw" / "metrics.csv"
    if not csv.exists():
        print(f"  [skip] {csv} not found -- run scripts/run_exp3_n_sweep.sh first")
        return None
    return pd.read_csv(csv).sort_values("iter")


def row_at(run: str, it: int) -> pd.Series | None:
    df = read(run)
    if df is None:
        return None
    sel = df[df["iter"].astype(int) == it]
    if sel.empty:
        print(f"  [skip] {run} has no iter={it} checkpoint (has {list(df['iter'])})")
        return None
    return sel.iloc[-1]


def loglog_exponent(N: np.ndarray, y: np.ndarray) -> float:
    return float(np.polyfit(np.log(N), np.log(y), 1)[0])


def matched_loss_table(levels=(0.03, 0.02, 0.015, 0.01)) -> list[dict]:
    """Third control: line the runs up by training loss rather than by iteration."""
    pool: dict[int, pd.DataFrame] = {}
    for N, runs in SWEEP_BUDGET.items():
        extra = [SWEEP_EXPOSURE[N][0]] if SWEEP_EXPOSURE[N][0] not in runs else []
        frames = [df for df in (read(r) for r in runs + extra) if df is not None]
        if frames:
            pool[N] = pd.concat(frames).sort_values("train_loss")
    out = []
    for lvl in levels:
        rec: dict = {"train_loss": lvl}
        for N, p in pool.items():
            rec[N] = (float(np.interp(lvl, p["train_loss"], p["pixel_var_inpaint_mean"]))
                      if p["train_loss"].min() <= lvl <= p["train_loss"].max() else None)
        out.append(rec)
    return out


def main():
    # ---- Sweep A: constant budget, seed statistics ----
    budget = []
    for N, runs in SWEEP_BUDGET.items():
        rs = [r for r in (row_at(run, BUDGET_ITERS) for run in runs) if r is not None]
        if not rs:
            continue
        rec = {"N": N, "iter": BUDGET_ITERS, "n_seeds": len(rs),
               "samples_per_image": BUDGET_ITERS * 64 / N}
        for m in METRICS:
            v = np.array([r[m] for r in rs], float)
            rec[m] = float(v.mean())
            rec[m + "_std"] = float(v.std(ddof=1)) if len(v) > 1 else 0.0
        budget.append(rec)

    # ---- Sweep B: constant per-image exposure ----
    exposure = []
    for N, (run, it) in SWEEP_EXPOSURE.items():
        r = row_at(run, it)
        if r is None:
            continue
        exposure.append({"N": N, "iter": it, "n_seeds": 1,
                         "samples_per_image": it * 64 / N,
                         **{m: float(r[m]) for m in METRICS},
                         "train_loss": float(r["train_loss"])})

    if len(budget) < 2 or len(exposure) < 2:
        print("Need at least 2 N values in each sweep. Nothing to aggregate yet.")
        return

    dfa = pd.DataFrame(budget).sort_values("N")
    dfb = pd.DataFrame(exposure).sort_values("N")
    expo_a = loglog_exponent(dfa["N"].values, dfa["pixel_var_inpaint_mean"].values)
    expo_b = loglog_exponent(dfb["N"].values, dfb["pixel_var_inpaint_mean"].values)

    out_dir = Path("results/exp3/_n_sweep")
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)

    # ---- figure: the two sweeps side by side, on a shared scale ----
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4))
    axes[0].errorbar(dfa["N"], dfa["pixel_var_inpaint_mean"],
                     yerr=dfa["pixel_var_inpaint_mean_std"], fmt="o-", capsize=3,
                     color="tab:red", label=f"slope {expo_a:+.2f}")
    axes[0].set_title(f"constant budget ({BUDGET_ITERS} iters, 3 seeds)")
    axes[1].plot(dfb["N"], dfb["pixel_var_inpaint_mean"], "s-", color="tab:blue",
                 label=f"slope {expo_b:+.2f}")
    axes[1].set_title(f"constant exposure ({EXPOSURE} samples/image)")
    lo = min(dfa["pixel_var_inpaint_mean"].min(), dfb["pixel_var_inpaint_mean"].min())
    hi = max(dfa["pixel_var_inpaint_mean"].max(), dfb["pixel_var_inpaint_mean"].max())
    for ax in axes:
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_ylim(lo / 3, hi * 3)          # shared scale: the contrast is the point
        ax.set_xlabel("N (training set size)")
        ax.set_ylabel("inpaint-region pixel variance")
        ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "n_sweep.png", dpi=150)
    plt.close(fig)

    # ---- markdown tables ----
    L = [f"**Sweep A -- constant budget ({BUDGET_ITERS} iters, mean +/- std over 3 seeds).**",
         "",
         "| N | grad samples / image | inpaint pixel var | NN dist to train image |",
         "|---|---|---|---|"]
    for _, r in dfa.iterrows():
        L.append(f"| {int(r.N)} | {int(r.samples_per_image)} | "
                 f"{r.pixel_var_inpaint_mean:.3g} +/- {r.pixel_var_inpaint_mean_std:.2g} | "
                 f"{r.nn_dist_mean:.3g} +/- {r.nn_dist_mean_std:.2g} |")
    ratio_a = dfa.pixel_var_inpaint_mean.max() / dfa.pixel_var_inpaint_mean.min()
    ratio_b = dfb.pixel_var_inpaint_mean.max() / dfb.pixel_var_inpaint_mean.min()
    L += ["", f"Power-law exponent in N: **{expo_a:+.3f}** (spread {ratio_a:.1f}x). "
              "Per-image exposure is proportional to 1/N here, so an exponent of ~+1 is "
              "equally consistent with a dependence on optimisation progress rather than "
              "on N itself. Sweep B is the control.",
          "",
          f"**Sweep B -- constant per-image exposure ({EXPOSURE} gradient samples, seed 0).**",
          "",
          "| N | iters | inpaint pixel var | NN dist to train image | final train loss |",
          "|---|---|---|---|---|"]
    for _, r in dfb.iterrows():
        L.append(f"| {int(r.N)} | {int(r.iter)} | {r.pixel_var_inpaint_mean:.3g} | "
                 f"{r.nn_dist_mean:.3g} | {r.train_loss:.4f} |")
    L += ["", f"Power-law exponent in N: **{expo_b:+.3f}** (spread {ratio_b:.2f}x). "
              "Holding the optimisation budget per image fixed removes most of the "
              "apparent N-dependence.",
          "",
          "**Control C -- runs lined up by training loss** (pixel variance, interpolated "
          "over every checkpoint of every run at that N).",
          "",
          "| train loss | N=100 | N=500 | N=2000 |",
          "|---|---|---|---|"]
    ml = matched_loss_table()
    for rec in ml:
        cells = " | ".join("--" if rec.get(N) is None else f"{rec[N]:.3g}"
                           for N in (100, 500, 2000))
        L.append(f"| {rec['train_loss']} | {cells} |")

    table_md = "\n".join(L)
    (out_dir / "n_sweep_table.md").write_text(table_md + "\n", encoding="utf-8")
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump({"constant_budget": budget, "constant_exposure": exposure,
                   "matched_loss": ml,
                   "exponent_constant_budget": expo_a,
                   "exponent_constant_exposure": expo_b}, f, indent=2)
    print(table_md)
    print(f"\nSaved: {out_dir}/summary.json, {out_dir}/figures/n_sweep.png, "
          f"{out_dir}/n_sweep_table.md")


if __name__ == "__main__":
    main()
