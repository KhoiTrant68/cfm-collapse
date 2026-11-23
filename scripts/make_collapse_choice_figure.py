"""Figure: the network chooses its image where the exact posterior collapses, and lands much later.

    PYTHONPATH=.:scripts python scripts/make_collapse_choice_figure.py

One panel per EDM model on CIFAR-10 (public, 1000 images, 500 images), on a common noise axis
(sampling runs left to right):

  * blue: the exact posterior over the training images of a class, w_j ~ exp(-|x - y_j|^2 / 2s^2),
    at x = y + s*eps with y a CIFAR-10 test image (solid: share of points whose largest weight is
    at least 1/2; dashed: at least 0.9) and, dotted, at x = y_i + s*eps with y_i a training image
    (share whose weight on y_i is at least 1/2). From results/paperB_20261121/collapse_sigma
    (scripts/paperB_collapse_sigma.py), for the training set of that model.
  * vermillion: the network's choice, the share of net->exact endpoints (network for sigma > s,
    exact field below) on the nearest training image of the network's own endpoint, with Wilson
    95% intervals; 500 latents per model.
  * black: landing, the share of exact->net endpoints (exact field for sigma > s, network below)
    that end on a training image (d1/d2 < 1/3).
Swap numbers from results/paperB_20261121/swap/swap_clocks.json (scripts/paperB_swap.py).

Writes results/paperB_20261121/collapse_sigma/fig_collapse_vs_choice.{pdf,png}.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import COLORS, FULL_W, OI, panel_title, shared_legend, use_paper_style

R = Path("results/paperB_20261121")
OUT = R / "collapse_sigma" / "fig_collapse_vs_choice"
MODELS = (("public", "full50k", "public model, 5000 per class"),
          ("sub1000", "sub1000_s0", "1000 images, 100 per class"),
          ("sub500", "sub500_s0", "500 images, 50 per class"))
EXACT, LEARNED, LAND = COLORS["exact"], COLORS["learned"], OI["black"]


def main():
    use_paper_style()
    col = json.loads((R / "collapse_sigma" / "summary.json").read_text(encoding="utf-8"))
    swap = json.loads((R / "swap" / "swap_clocks.json").read_text(encoding="utf-8"))["models"]
    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 2.25), sharey=True)
    record = {}
    for ax, (mkey, ckey, title), letter in zip(axes, MODELS, "abc"):
        sub = col["subsets"][ckey]
        sg = np.array([r["sigma"] for r in sub["fresh"]])
        f05 = np.array([r["frac_maxw_ge_0.5"] for r in sub["fresh"]])
        f09 = np.array([r["frac_maxw_ge_0.9"] for r in sub["fresh"]])
        own = np.array([r["frac_own_ge_0.5"] for r in sub["train"]])
        ax.plot(sg, f05, color=EXACT, lw=1.5)
        ax.plot(sg, f09, color=EXACT, lw=1.2, ls="--")
        ax.plot(sg, own, color=EXACT, lw=1.1, ls=":")

        m = swap[mkey]
        lv = m["levels"]
        s = np.array([L["s"] for L in lv])
        eqL = np.array([L["net2exact"]["eqL"]["p"] for L in lv])
        lo = np.array([L["net2exact"]["eqL"]["lo"] for L in lv])
        hi = np.array([L["net2exact"]["eqL"]["hi"] for L in lv])
        on = np.array([L["exact2net"]["on"]["p"] for L in lv])
        on_lo = np.array([L["exact2net"]["on"]["lo"] for L in lv])
        on_hi = np.array([L["exact2net"]["on"]["hi"] for L in lv])
        err = lambda p, a, b: [np.clip(p - a, 0, None), np.clip(b - p, 0, None)]   # Wilson at p=0 gives a ~1e-19 lower end
        ax.errorbar(s, eqL, yerr=err(eqL, lo, hi), color=LEARNED, marker="o", ms=3.2, lw=1.4,
                    capsize=1.5, elinewidth=0.8, zorder=4)
        ax.errorbar(s, on, yerr=err(on, on_lo, on_hi), color=LAND, marker="s", ms=2.8, lw=1.1,
                    ls=(0, (4, 2)), capsize=1.5, elinewidth=0.8, zorder=3)

        ax.set_xscale("log")
        ax.set_xlim(30, 0.01)
        ax.set_ylim(-0.03, 1.05)
        ax.set_xticks([10, 1, 0.1, 0.01])
        ax.set_xticklabels(["10", "1", "0.1", "0.01"])
        ax.set_xlabel(r"noise level $\sigma$")
        panel_title(ax, letter, title, fontsize=7.5)
        record[mkey] = {"collapse_subset": ckey,
                        "sigma_c": {k: sub[k] for k in sub if k.startswith("sigma_")},
                        "s": s.tolist(), "choice_eqL": eqL.tolist(), "landing_on": on.tolist()}
    axes[0].set_ylabel("fraction")
    shared_legend(fig, [("exact posterior, largest weight $\\geq 1/2$", "line", EXACT),
                        ("largest weight $\\geq 0.9$", "dashed", EXACT),
                        ("own weight at a noised training image $\\geq 1/2$", "line", EXACT),
                        ("network's choice (net$\\to$exact on its own image)", "marker", LEARNED),
                        ("landing (exact$\\to$net on a training image)", "marker", LAND)],
                  ncol=3, y=1.13)
    # the dotted entry: restyle the third handle
    leg = fig.legends[-1]
    leg.legend_handles[2].set_linestyle(":")
    leg.legend_handles[2].set_linewidth(1.4)
    leg.legend_handles[4].set_marker("s")
    fig.subplots_adjust(wspace=0.08, left=0.07, right=0.995, bottom=0.2, top=0.86)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT.with_suffix(f".{ext}"), bbox_inches="tight", pad_inches=0.02)
    OUT.with_suffix(".json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(f"wrote {OUT}.pdf/.png/.json")


if __name__ == "__main__":
    main()
