"""Figure fig:intervention-validation in the paper style.

    python -m scripts.make_intervention_validation_figure

The three panels were first drawn by ``summarize_novelty_interventions.py`` with matplotlib
defaults. This script draws the same quantities from the same saved records, with the shared
colours and fonts of ``scripts.figstyle``; it reads only, and writes only the figure.

  left    mean nearest-atom distance against the terminal gap, d=2, random atoms, h=1,
          averaged over the five geometry seeds (exact-field-stress-five-seeds)
  middle  nearest-atom distance of a source 1e-8 from a symmetric tie under field averaging
          (tie-neighborhood-boundary)
  right   normalised energy between learned and exact label averages at fresh labels, per
          checkpoint seed and their mean (learned-label-averaging-five-seeds)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, FULL_W, OI, direct_label, panel_title, style, use_paper_style

ROOT = Path("results/novelty_interventions_20261016")
OUT = Path("paper_theory/figures/fig_intervention_validation.pdf")
WIDTH = 0.98 * FULL_W            # printed at 0.98 textwidth
GREY = "#555555"


def rows(suite: str) -> list[dict]:
    rec = json.loads((ROOT / suite / "results.json").read_text(encoding="utf-8"))
    assert rec["status"] == "completed"
    return rec["rows"]


def main() -> None:
    use_paper_style()
    stress = rows("exact-field-stress-five-seeds")
    ties = rows("tie-neighborhood-boundary")
    learned = rows("learned-label-averaging-five-seeds")

    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.3))

    # (a) every arm converges to an atom at the rate of the gap
    ax = axes[0]
    gaps = [1e-2, 1e-4, 1e-6]
    arms = [("cfg", 0.0, "single field", COLORS["theory"], "o", "-"),
            ("cfg", 12.0, r"guidance $w=12$", OI["orange"], "s", "-"),
            ("average_fields", 0.0, "field average", OI["blue"], "^", "--"),
            ("average_priors", 0.0, "prior average", OI["green"], "D", ":")]
    for arm, w, lab, c, mk, ls in arms:
        ys = [np.mean([r["mean_nearest"] for r in stress
                       if r["d"] == 2 and r["geometry"] == "random" and r["h"] == 1.0
                       and r["eps"] == g and r["arm"] == arm and r["w"] == w]) for g in gaps]
        ax.loglog(gaps, ys, color=c, marker=mk, ms=3.2, lw=1.1, ls=ls, label=lab)
    ax.invert_xaxis()
    ax.set_xlabel(r"terminal gap $1-T$")
    ax.set_ylabel("mean nearest-atom distance")
    ax.set_ylim(5e-7, 0.1)
    ax.legend(fontsize=6.5, loc="lower left", handlelength=2.2, borderaxespad=0.3, labelspacing=0.3)
    panel_title(ax, "a", "Exact fields reach atoms")

    # (b) a source close to a tie leaves it late, or not before T, but its limit is still an atom
    ax = axes[1]
    # Every curve here is the field average of (a), so h=1 keeps its blue triangles; the two
    # bandwidths still at the tie at the cutoff are grey, not vermillion, because their limit is
    # an atom too (vermillion means a blend everywhere else in the paper).
    for h, c, mk, ms, ls in ((0.05, "#9a9a9a", "o", 5.0, "-"), (0.2, GREY, "s", 2.6, "--"),
                             (1.0, OI["blue"], "^", 3.2, "--")):
        rr = sorted((r for r in ties if r["arm"] == "average_fields" and r["h"] == h and r["x0"] == 1e-8),
                    key=lambda r: -r["eps"])
        ax.loglog([r["eps"] for r in rr], [max(r["nearest_atom_distance"], 1e-15) for r in rr],
                  color=c, marker=mk, ms=ms, lw=1.1, ls=ls, mfc="white" if h == 0.05 else c)
    ax.set_xticks([1e-2, 1e-4, 1e-6, 1e-8])
    ax.invert_xaxis()
    ax.text(0.5, 0.86, r"$h=0.05$ (circles), $0.2$ (squares):" "\n" "still at the tie", transform=ax.transAxes, ha="center",
            va="top", fontsize=6.5, color=GREY)
    ax.text(0.05, 0.1, r"$h=1$: reaches an atom", transform=ax.transAxes, ha="left", va="center",
            fontsize=6.5, color=OI["blue"])
    ax.set_xlabel(r"terminal gap $1-T$")
    ax.set_ylabel("nearest-atom distance")
    panel_title(ax, "b", r"Near a tie (offset $10^{-8}$)")

    # (c) learned versus exact label averages
    ax = axes[2]
    radii = (0.0, 0.5, 1.5)
    seeds = sorted({r["seed"] for r in learned})
    per_seed = []
    for s in seeds:
        ys = [np.mean([r["network_reference_energy_normalized"] for r in learned
                       if r["seed"] == s and r["query_type"] == "fresh" and r["radius_in_label_std"] == a])
              for a in radii]
        per_seed.append(ys)
        ax.plot(radii, ys, color="#9a9a9a", lw=0.7, marker="o", ms=2.0, alpha=0.9)
    mean = np.mean(per_seed, axis=0)
    ax.plot(radii, mean, color=COLORS["learned"], lw=1.6, marker="o", ms=3.5)
    direct_label(ax, radii[-1], mean[-1], f"mean of\n{len(seeds)} seeds", COLORS["learned"], dx=4)
    top = int(np.argmax([y[-1] for y in per_seed]))
    direct_label(ax, radii[-1], per_seed[top][-1], "one seed", "#777777", dx=4)
    ax.set_xticks(radii)
    ax.set_xlim(-0.08, 1.95)
    ax.set_xlabel("averaging radius / label s.d.")
    ax.set_ylabel("energy distance to exact (normalised)")
    panel_title(ax, "c", "Learned vs exact averages")

    for ax in axes:
        style(ax)
    fig.tight_layout(w_pad=0.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
