"""Plot EXP-3 inpainting collapse metrics vs iteration.

    uv run python scripts/analyze_exp3.py --run results/exp3/exp3_mnist_seed0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    run = Path(args.run)
    df = pd.read_csv(run / "raw" / "metrics.csv").sort_values("iter")

    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(df["iter"], df["pixel_var_inpaint_mean"], marker="o", color="C3",
            label="pixel variance in inpainted region")
    ax.plot(df["iter"], df["nn_dist_mean"], marker="s", color="C0",
            label="dist(generated mean, nearest train img)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel("value (log)")
    ax.set_title("EXP-3 — inpainting diversity collapses under overtraining")
    ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    out = args.out or str(run / "figures" / "exp3_collapse.png")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140); plt.close(fig)

    summary = {
        "iters": df["iter"].tolist(),
        "pixel_var_inpaint": df["pixel_var_inpaint_mean"].tolist(),
        "nn_dist": df["nn_dist_mean"].tolist(),
        "obs_recon_err": df["obs_recon_err_mean"].tolist(),
        "var_drop_ratio": float(df["pixel_var_inpaint_mean"].iloc[-1] /
                                df["pixel_var_inpaint_mean"].iloc[0]),
    }
    with open(run / "raw" / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
