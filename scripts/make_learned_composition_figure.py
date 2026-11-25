"""Figure fig:learned-composition of paper_theory: which network reproduces the exact midpoint probability.

    PYTHONPATH=.:scripts python scripts/make_learned_composition_figure.py

Parity plots, one per network parametrisation (the 2 x 2 design of Appendix app:learned-composition:
output = velocity or data, input = plain (x, t, y) or with the rescaled coordinate asinh(tx/(1-t)^2)):

  (a) cfm_v    velocity output, plain input (standard CFM)       results/learned_composition_20261021,
  (b) cfm_x    data output, plain input                          results/composition_ablation_20261105,
  (c) cfm_v_s  velocity output, rescaled input                   results/composition_ablation_20261105,
  (d) cfm_x_s  data output, rescaled input                       results/learned_composition_20261021,

with the triangle runs under the *_2d_* directories. Each point is one configuration (two atoms of
Theorem thm:composition with B = 1 or B = 2, or the triangle of Section sec:intervention-tests with
B = 2) at one guidance strength w/w_c: horizontally the exact probability that the composite ends at
the midpoint (the centre of the triangle) under N(0, I), E4 of results/learned_composition_20261021/
exact/summary.json and the centre fraction of results/learned_composition_2d_20261021/exact/
exact.json; vertically the learned occupancy, the fraction of the 2048 shared sources within
delta = 0.05 of the midpoint at 1 - t = 1e-5 (arm L3 of the per-seed summary.json files), as the
mean (marker) and population standard deviation (bar) over the five seeds, with each seed as a dot.
The diagonal is learned = exact. At the six strengths of Table tab:learned-composition (w/w_c = 0, 1,
1.1, 2, 5, 10) the values are its entries; the two-atom runs add 0.5, 0.8, 0.9, 1.2, 1.5 and the
triangle 0.5, 0.9, from the same files. Everything drawn is printed, with the mean absolute deviation
from the diagonal of each panel (the grey number in it).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from figstyle import COLORS, FULL_W, OI, lead_text, use_paper_style

LC1, LC2 = Path("results/learned_composition_20261021"), Path("results/learned_composition_2d_20261021")
AB1, AB2 = Path("results/composition_ablation_20261105"), Path("results/composition_ablation_2d_20261105")
SEEDS = range(5)
EPS, DELTA = 1e-5, 0.05
OUT = Path("paper_theory/figures/fig_learned_composition.pdf")
WIDTH = 0.98 * FULL_W                                   # printed at 0.98 textwidth
GREY = "#555555"
LEARNED = COLORS["learned"]
EXACT = COLORS["exact"]
PANELS = (("cfm_v", "Velocity", "standard CFM"), ("cfm_x", "Data prediction", ""),
          ("cfm_v_s", "Velocity", ""), ("cfm_x_s", "Data prediction", ""))
CONFIGS = (("B1", "two atoms, $B=1$", "o", 4.0), ("B2", "two atoms, $B=2$", "s", 3.6),
           ("tri", "triangle, $B=2$", "^", 4.4))


def root_of(variant: str, cfg: str) -> Path:
    base = (AB2 if variant in ("cfm_v_s", "cfm_x") else LC2) if cfg == "tri" else \
        (AB1 if variant in ("cfm_v_s", "cfm_x") else LC1)
    return base


def learned(variant: str, cfg: str) -> dict[float, list[float]]:
    """w/w_c -> per-seed L3 midpoint occupancy at eps = 1e-5, delta = 0.05."""
    B = {"B1": 1.0, "B2": 2.0, "tri": None}[cfg]
    per: dict[float, list[float]] = {}
    for seed in SEEDS:
        s = json.loads((root_of(variant, cfg) / f"{variant}_seed{seed}" / "summary.json")
                       .read_text(encoding="utf-8"))
        for arm in s["arms"]:
            if arm["arm"] != "L3" or (B is not None and arm["B"] != B):
                continue
            row = next(e for e in arm["by_eps"] if abs(e["eps"] - EPS) < 1e-12)
            per.setdefault(arm["r"], []).append(row[f"occ_{DELTA:g}"])
    for r, v in per.items():
        assert len(v) == len(SEEDS), (variant, cfg, r, len(v))
    return per


def exact(cfg: str) -> dict[float, float]:
    if cfg == "tri":
        rows = json.loads((LC2 / "exact" / "exact.json").read_text(encoding="utf-8"))["rows"]
        return {r["r"]: r["midpoint_fraction"] for r in rows}
    B = {"B1": 1.0, "B2": 2.0}[cfg]
    rows = json.loads((LC1 / "exact" / "summary.json").read_text(encoding="utf-8"))["rows"]
    return {r["r"]: r["basin_probability"] for r in rows if r["arm"] == "E4" and r["B"] == B}


def main() -> None:
    use_paper_style()
    W, H = WIDTH, 2.30
    fig = plt.figure(figsize=(W, H))
    left, gap, side, bottom = 0.50, 0.13, 1.36, 0.42
    axes = []
    ex = {c: exact(c) for c, *_ in CONFIGS}
    for k, (variant, name, sub) in enumerate(PANELS):
        ax = fig.add_axes(((left + k * (side + gap)) / W, bottom / H, side / W, side / H))
        ax.plot([0, 1], [0, 1], color=EXACT, lw=1.1, zorder=1)
        dev = []
        for cfg, lab, mk, ms in CONFIGS:
            L = learned(variant, cfg)
            for r in sorted(L):
                if r not in ex[cfg]:
                    continue
                x, v = ex[cfg][r], np.asarray(L[r])
                ax.plot([x] * len(v), v, ls="none", marker=mk, ms=ms * 0.45, color=LEARNED, alpha=0.35,
                        mew=0, zorder=2)
                ax.errorbar([x], [v.mean()], yerr=[v.std()], fmt=mk, ms=ms, color=LEARNED, mfc="white",
                            mew=0.9, elinewidth=0.8, capsize=1.6, zorder=3)
                dev.append(abs(v.mean() - x))
            print(variant, cfg, {r: (round(ex[cfg][r], 3), round(float(np.mean(L[r])), 3),
                                     round(float(np.std(L[r])), 3)) for r in sorted(L) if r in ex[cfg]})
        mad = float(np.mean(dev))
        print(f"  {variant}: mean |learned - exact| over {len(dev)} points = {mad:.4f}")
        ax.text(0.04, 0.96, "mean deviation\n" + rf"$|\,$learned$-$exact$\,|={mad:.3f}$",
                transform=ax.transAxes, ha="left", va="top", fontsize=6.3, color=GREY, linespacing=1.25)
        ax.set_xlim(-0.04, 1.04); ax.set_ylim(-0.04, 1.04); ax.set_aspect("equal")
        ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
        ax.set_xticklabels(["0", "0.5", "1"])
        if k == 0:
            ax.set_yticklabels(["0", "0.5", "1"])
            ax.set_ylabel("learned midpoint fraction")
        else:
            ax.set_yticklabels([])
        lead_text(ax, 0.0, 1.035, "abcd"[k], name, transform=ax.transAxes, fontsize=8.5)
        if sub:
            ax.text(1.0, 1.035, sub, transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5,
                    color=GREY)
        ax.tick_params(length=2.5, width=0.6)
        axes.append(ax)

    axes[0].text(0.55, 0.53, "learned = exact", rotation=45, rotation_mode="anchor", fontsize=6.3,
                 color=EXACT, ha="center", va="bottom", transform=axes[0].transData)
    axes[0].legend(handles=[Line2D([], [], ls="none", marker=mk, ms=ms, color=LEARNED, mfc="white",
                                   mew=0.9, label=lab) for _, lab, mk, ms in CONFIGS],
                   loc="lower right", bbox_to_anchor=(1.0, 0.10), fontsize=6.3, handletextpad=0.3,
                   borderaxespad=0.2, labelspacing=0.35, frameon=False)
    fig.text((left + 2 * side + 1.5 * gap) / W, 0.012, "exact probability that the composite ends at the "
             "midpoint", ha="center", va="bottom", fontsize=8)

    def header(k0, k1, text, color):
        xa = (left + k0 * (side + gap)) / W
        xb = (left + k1 * (side + gap) + side) / W
        y = (bottom + side + 0.27) / H
        fig.add_artist(Line2D([xa, xb], [y, y], color=color, lw=0.8))
        fig.text((xa + xb) / 2, y + 0.012, text, ha="center", va="bottom", fontsize=7.5, color=color)
    header(0, 1, r"plain input $(x,t,y)$: midpoint nearly empty", COLORS["atom"])
    header(2, 3, r"rescaled input $\operatorname{asinh}(tx/(1-t)^2)$: near the exact probability", LEARNED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, pad_inches=0.0)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
