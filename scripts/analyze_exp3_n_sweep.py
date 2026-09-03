"""Aggregate EXP-3 (MNIST inpainting) N-sweep runs into a summary table + figure.

Mirrors the P6 (N-sweep) treatment of EXP-1 (Table 6, Figure 2a), but for the
image experiment: at the final checkpoint, report inpaint-region pixel
variance and nearest-training-image distance as a function of N.

Reads:  results/exp3/exp3_N100/raw/metrics.csv
        results/exp3/exp3_mnist_seed0/raw/metrics.csv   (N=500 default)
        results/exp3/exp3_N2000/raw/metrics.csv
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
import pandas as pd

RUNS = {
    100: "results/exp3/exp3_N100",
    500: "results/exp3/exp3_mnist_seed0",
    2000: "results/exp3/exp3_N2000",
}


def final_row(run_dir: str) -> dict | None:
    csv = Path(run_dir) / "raw" / "metrics.csv"
    if not csv.exists():
        print(f"  [skip] {csv} not found — run scripts/run_exp3_n_sweep.sh first")
        return None
    df = pd.read_csv(csv)
    return df.sort_values("iter").iloc[-1].to_dict()


def main():
    rows = []
    for N, run_dir in RUNS.items():
        r = final_row(run_dir)
        if r is None:
            continue
        rows.append({
            "N": N,
            "pixel_var_inpaint": r["pixel_var_inpaint_mean"],
            "nn_dist": r["nn_dist_mean"],
            "iter": int(r["iter"]),
        })

    if len(rows) < 2:
        print("Need at least 2 of the 3 N values run. Nothing to aggregate yet.")
        return

    df = pd.DataFrame(rows).sort_values("N")
    out_dir = Path("results/exp3/_n_sweep")
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)

    # ---- figure ----
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    axes[0].plot(df["N"], df["pixel_var_inpaint"], "o-", color="tab:red")
    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].set_xlabel("N (training set size)")
    axes[0].set_ylabel("inpaint-region pixel variance")
    axes[0].set_title("EXP-3 N-sweep: variance vs N")
    axes[0].grid(alpha=0.3)

    axes[1].plot(df["N"], df["nn_dist"], "o-", color="tab:blue")
    axes[1].set_xscale("log"); axes[1].set_yscale("log")
    axes[1].set_xlabel("N (training set size)")
    axes[1].set_ylabel("dist to nearest training image")
    axes[1].set_title("EXP-3 N-sweep: NN-distance vs N")
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "n_sweep.png", dpi=150)
    plt.close(fig)

    # ---- markdown table (paste into paper appendix) ----
    lines = [
        "| N | iter | inpaint pixel var | NN dist to train image |",
        "|---|---|---|---|",
    ]
    for _, r in df.iterrows():
        lines.append(f"| {int(r.N)} | {int(r.iter)} | {r.pixel_var_inpaint:.4g} | {r.nn_dist:.4g} |")
    table_md = "\n".join(lines)
    (out_dir / "n_sweep_table.md").write_text(table_md + "\n")

    df.to_json(out_dir / "summary.json", orient="records", indent=2)
    print(table_md)
    print(f"\nSaved: {out_dir}/summary.json, {out_dir}/figures/n_sweep.png, "
          f"{out_dir}/n_sweep_table.md")


if __name__ == "__main__":
    main()
