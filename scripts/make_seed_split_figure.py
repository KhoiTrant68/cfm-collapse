"""What the EXP-1 error bars are measuring, in a form that can be read off.

The previous figure was two jittered scatter columns labelled "instance fixed" and
"run fixed" -- the reader had to invert both labels to work out what was varying,
compare two clouds by eye to see that one is wider, and take the 78% split from the
caption because nothing in the picture showed it. Three things are drawn instead.

  (a) the two arms, labelled by what VARIES, with the run they share drawn in both
      and joined, so the paired structure is visible; the vertical spans make the
      widths directly comparable instead of leaving it to the eye.

  (b) the decomposition as standard deviations, with the quadrature sum against the
      published five-seed spread. This is the check the table reports in words: the
      two sources account for the observed bar, so nothing else of size is missing.

  (c) the part that matters for the paper's conclusions -- the collapse itself
      against the bars that measure it. The effect is 1 - 0.37 = 0.63 in ratio units
      and the widest bar is 0.14, so the bars being conservative changes the size of
      the error bars and not a single conclusion. Saying that is weaker than showing
      the two on one axis.

    uv run python -m scripts.make_seed_split_figure

Reads:  results/exp1/_seed_split/summary.json  (written by analyze_exp1_seed_split.py)
Writes: paper/figures/fig_seed_split.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from scripts.figstyle import use_paper_style  # noqa: E402

use_paper_style()
# this figure's annotations were laid out at the default sizes
plt.rcParams.update({"font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 10, "legend.fontsize": 8.5, "legend.frameon": True, "legend.framealpha": 0.92,
                     "xtick.labelsize": 9, "ytick.labelsize": 9})

SRC = Path("results/exp1/_seed_split/summary.json")
OUT = Path("paper/figures/fig_seed_split.png")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}


def main() -> None:
    s = json.loads(SRC.read_text(encoding="utf-8"))
    run = np.array(list(s["run_varying"].values()))
    inst = np.array(list(s["instance_varying"].values()))
    sd_run, sd_inst = s["std_run"], s["std_instance"]
    quad, pub = s["quadrature"], s["published_std_ddof1"]
    share = s["instance_share_of_variance"]
    # The two arms are anchored on one common run: seed 0 of each appears in both.
    anchor = float(list(s["run_varying"].values())[0])
    assert abs(anchor - float(list(s["instance_varying"].values())[0])) < 1e-12

    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.4))
    rng = np.random.default_rng(0)

    # ------------------------------------------------- (a) the two arms, paired
    ax = axes[0]
    for k, (v, col, mk) in enumerate((
            (run, OI["blue"], "o"), (inst, OI["vermillion"], "s"))):
        # The min-max span as a shaded block behind the points, so "wider" is a
        # height on the page rather than an impression of a cloud.
        ax.add_patch(plt.Rectangle((k - 0.26, v.min()), 0.52, v.max() - v.min(),
                                   facecolor=col, alpha=0.11, lw=0, zorder=1))
        ax.annotate(f"range {v.max() - v.min():.2f}", xy=(k, v.max()),
                    xytext=(0, 6), textcoords="offset points", fontsize=8.5,
                    color=col, ha="center")
        x = k + 0.075 * rng.standard_normal(len(v))
        ax.scatter(x, v, s=52, marker=mk, color=col, alpha=0.85, zorder=4,
                   edgecolor="white", linewidth=0.5)
        ax.errorbar([k - 0.40], [v.mean()], yerr=[np.std(v, ddof=1)], fmt="_",
                    markersize=18, capsize=5, color=OI["black"], lw=1.4, zorder=5)
    ax.plot([0, 1], [anchor, anchor], color="0.5", ls="--", lw=1.1, zorder=2)
    ax.scatter([0, 1], [anchor, anchor], s=100, facecolor="none",
               edgecolor=OI["black"], linewidth=1.5, zorder=6)
    ax.annotate("the one run\nboth arms share", xy=(1.0, anchor), xytext=(1.18, 0.30),
                ha="left", va="center", fontsize=8, color="0.35",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.5"))
    # The columns name themselves, so a legend is redundant -- and it had nowhere to
    # sit that did not cover either a point or a label.
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["training run\nvaries  (n=10)",
                        "problem instance\nvaries  (n=10)"], fontsize=9)
    ax.set_xlim(-0.62, 1.80); ax.set_ylim(0.15, 0.60)
    ax.set_ylabel(r"collapse ratio $\mathrm{tr}\,\mathrm{Cov}/\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_title("(a) ten runs each way, with what varies named", fontsize=10.5)
    ax.grid(alpha=0.3, axis="y")

    # ------------------------------------------- (b) the decomposition, and its check
    ax = axes[1]
    # The variance shares go on the tick labels rather than into a box that has
    # to be squeezed in somewhere; they belong to the bars they describe.
    names = [f"training run\n$\\sigma_{{\\mathrm{{run}}}}$   "
             f"({100 - share * 100:.0f}% of variance)",
             f"problem instance\n$\\sigma_{{\\mathrm{{inst}}}}$   "
             f"({share * 100:.0f}% of variance)",
             "in quadrature\n$\\sqrt{\\sigma^2+\\sigma^2}$"]
    vals = [sd_run, sd_inst, quad]
    cols = [OI["blue"], OI["vermillion"], OI["black"]]
    y = np.arange(3)[::-1]
    ax.barh(y, vals, height=0.55, color=cols, alpha=0.85)
    for yy, v in zip(y, vals):
        ax.text(v + 0.004, yy, f"{v:.4f}", va="center", fontsize=9.5)
    ax.axvline(pub, color=OI["green"], ls="--", lw=1.8,
               label=f"published 5-seed spread  {pub:.4f}")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 0.185)
    ax.set_xlabel("standard deviation of the collapse ratio")
    ax.set_title("(b) the two sources add up to the published bar", fontsize=10.5)
    ax.grid(alpha=0.3, axis="x"); ax.legend(fontsize=8, loc="upper right")

    # ------------------------------------------- (c) the bar against the effect
    ax = axes[2]
    mean = float(np.mean(np.concatenate([run, inst])))
    ax.axhline(1.0, color=OI["green"], ls=":", lw=1.8)
    ax.text(1.52, 1.0, "calibrated\n(no collapse)", fontsize=8.5, color=OI["green"],
            va="center")
    ax.axhline(0.0, color="0.4", ls=":", lw=1.4)
    ax.text(1.52, 0.0, "total collapse\n(an atom)", fontsize=8.5, color="0.4",
            va="center")
    for k, (sd, col, lab) in enumerate((
            (pub, OI["black"], f"as published\n$\\pm{pub:.3f}$"),
            (sd_run, OI["blue"], f"instance fixed\n$\\pm{sd_run:.3f}$"))):
        ax.errorbar([k], [mean], yerr=[sd], fmt="o", ms=9, capsize=9, lw=2.4,
                    color=col, zorder=5)
        ax.annotate(lab, xy=(k, mean - sd), xytext=(0, -16),
                    textcoords="offset points", ha="center", va="top", fontsize=8.5,
                    color=col)
    ax.annotate("", xy=(0.55, 1.0), xytext=(0.55, mean),
                arrowprops=dict(arrowstyle="<->", lw=1.6, color=OI["orange"]))
    ax.text(0.60, (1.0 + mean) / 2,
            f"the effect: ${1 - mean:.2f}$\n$= {(1 - mean) / pub:.1f}\\times$ the widest bar",
            fontsize=9, color=OI["orange"], va="center")
    ax.set_xlim(-0.6, 2.6); ax.set_ylim(-0.22, 1.28)
    ax.set_xticks([])
    ax.set_ylabel(r"collapse ratio $\mathrm{tr}\,\mathrm{Cov}/\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_title("(c) what the bars are next to what they measure", fontsize=10.5)
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle("EXP-1: most of every error bar in this paper is which operator $A$ "
                 "was drawn, not how the run went", fontsize=12, y=1.005)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUT}   (instance share {share * 100:.0f}%, effect "
          f"{(1 - mean) / pub:.1f}x the published bar)")


if __name__ == "__main__":
    main()
