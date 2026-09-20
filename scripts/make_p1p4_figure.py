"""P1-P4 as one figure, because they are one story told on one clock.

The four exact-theory observables were four separate plots, and a reader had to
reconstruct from them that they are the same event seen four ways. They share an
x-axis, they turn at the same moment, and each is only interesting relative to a
target the others also reference. So: one figure, one clock, and the crossover drawn
identically in every panel.

    (a) the variance    tr Cov starts at tr Sigma_post -- the sampler is calibrated
                        -- and then falls away from it.
    (b) the mean        the clearest panel: the generated mean's distance to the
                        posterior mean rises while its distance to the training
                        point falls, and they cross. Before the crossing the model
                        is answering the inverse problem; after it, it is returning
                        a memorised image.
    (c) the field       the velocity field's relative error against the collapsed
                        closed form (x^i - x)/(1-t), falling towards it.
    (d) the contrast    the unconditional baseline on the same axes, holding
                        data-scale variance throughout. The distinction is not
                        "memorises or not" but which empirical measure is memorised.

The vertical band is the same in all four: the iteration at which (b) crosses. It is
the visual thread -- nothing in the four panels turns at a different time.

    uv run python -m scripts.make_p1p4_figure

Reads:  results/exp1/exp1_{cond,uncond}_seed*/raw/metrics.csv
Writes: paper/figures/fig_p1p4.png
"""
from __future__ import annotations

import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from scripts.figstyle import use_paper_style  # noqa: E402

use_paper_style()
# these legends sit over data and were laid out with a frame
plt.rcParams.update({"legend.frameon": True, "legend.framealpha": 0.92})

OUT = Path("paper/figures/fig_p1p4.png")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}


def gather(pattern: str, group: str = "train") -> pd.DataFrame:
    """Stack the per-seed curves, keeping one row per (seed, iteration)."""
    frames = []
    for d in sorted(glob.glob(pattern)):
        f = Path(d) / "raw" / "metrics.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        df = df[df["group"] == group].copy()
        if df.empty:
            continue
        df["seed"] = Path(d).name
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def band(ax, df, col, color, label, ls="-"):
    g = df.groupby("iter")[col]
    m, s = g.mean(), g.std(ddof=0).fillna(0.0)
    ax.plot(m.index, m.values, ls, color=color, lw=1.8, marker="o", ms=3.5,
            label=label)
    ax.fill_between(m.index, m - s, m + s, color=color, alpha=0.18, lw=0)
    return m


def main() -> None:
    cond = gather("results/exp1/exp1_cond_seed[0-9]")
    # The unconditional runs label their rows "uncond", not "train"; filtering
    # for "train" silently returns nothing and panel (d) then redraws panel (a).
    unc = gather("results/exp1/exp1_uncond_seed[0-9]", group="uncond")
    if cond.empty:
        print("no conditional runs found"); return
    trace_post = float(cond["trace_post"].iloc[0])

    # The crossover: where the generated mean stops being nearer the posterior mean
    # than the training point. Every panel is marked at the same place.
    g = cond.groupby("iter")
    d_post = g["mean_err_post_mean"].mean()
    d_train = g["mean_err_train_point_mean"].mean()
    sign = np.sign(d_train.values - d_post.values)
    cross = lo = hi = None
    for k in range(1, len(sign)):
        if sign[k] != sign[k - 1]:
            # The crossing is bracketed by two checkpoints and nothing finer was
            # evaluated, so report the bracket. A midpoint would imply a precision
            # the evaluation grid does not have.
            lo, hi = int(d_post.index[k - 1]), int(d_post.index[k])
            cross = True
            break

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 6.6), sharex=True)
    for ax in axes.ravel():
        if cross:
            ax.axvspan(lo, hi, color=OI["orange"], alpha=0.14, lw=0)
        ax.set_xscale("log"); ax.grid(alpha=0.3)

    # (a) the variance ------------------------------------------------------
    ax = axes[0, 0]
    band(ax, cond, "trace_cov_mean", OI["blue"], "generated, conditional")
    ax.axhline(trace_post, color=OI["black"], ls=":", lw=1.5,
               label=rf"$\mathrm{{tr}}\,\Sigma_{{\mathrm{{post}}}}={trace_post:.3f}$")
    ax.set_yscale("log")
    ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$")
    ax.set_title("(a) the conditional variance leaves the posterior", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")

    # (b) the mean ----------------------------------------------------------
    ax = axes[0, 1]
    band(ax, cond, "mean_err_post_mean", OI["sky"],
         r"to the posterior mean $\mu_{\mathrm{post}}$")
    band(ax, cond, "mean_err_train_point_mean", OI["vermillion"],
         r"to the training point $x^i$")
    ax.set_yscale("log"); ax.set_ylabel("distance of the generated mean")
    ax.set_title("(b) the mean swaps targets", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")

    # (c) the field ---------------------------------------------------------
    ax = axes[1, 0]
    band(ax, cond, "vel_rel_err_mean_mean", OI["green"],
         r"relative $L^2$ error vs $(x^i-x)/(1-t)$")
    ax.set_ylabel("velocity error")
    ax.set_xlabel("training iteration")
    ax.set_title("(c) the field converges to the collapsed closed form",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")

    # (d) the contrast ------------------------------------------------------
    ax = axes[1, 1]
    band(ax, cond, "trace_cov_mean", OI["blue"], "conditional")
    if not unc.empty:
        band(ax, unc, "trace_cov_mean", OI["green"], "unconditional baseline")
        td = float(unc.groupby("iter")["trace_cov_mean"].mean().iloc[-1])
        ax.axhline(td, color=OI["green"], ls=":", lw=1.5,
                   label=f"data scale, {td:.2f}")
    ax.axhline(trace_post, color=OI["black"], ls=":", lw=1.5,
               label=r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_yscale("log"); ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$")
    ax.set_xlabel("training iteration")
    ax.set_title("(d) the unconditional model holds its variance", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")

    if cross:
        fig.text(0.5, 0.965,
                 "the band marks the same moment in all four panels: between "
                 f"{lo:,} and {hi:,} iterations the generated mean stops being "
                 "nearer the posterior mean than the training point",
                 ha="center", fontsize=10, color=OI["orange"])
    fig.suptitle("One event, four observables, one clock  (EXP-1, 5 seeds, "
                 "band = across-seed spread)", fontsize=12.5, y=1.015)
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUT}   (crossover bracketed by {lo}-{hi} iterations)"
          if cross else f"Saved: {OUT}")


if __name__ == "__main__":
    main()
