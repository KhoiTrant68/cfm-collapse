"""Figure fig:composition: the mechanism and the phase diagram of guided label averaging.

(a) The composite posterior mean F_w(s) of Theorem thm:composition (closed form,
    eq. composition-mean) for B=2 below, at and above the threshold w_c = 1/sinh^2 B.
    Its slope at the tie s=0 changes sign at w_c.
(b) Probability under N(0,1) that the trajectory ends at the non-training midpoint,
    read from results/theory_composition_20261019/summary.json (written by
    scripts/composition_counterexample.py), against w/w_c on a log axis.

Usage:  uv run python scripts/make_composition_figure.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import FIGDIR, OI, style, use_paper_style

SUMMARY = Path("results/theory_composition_20261019/summary.json")


def F(s, w, B):
    return 2 * np.tanh(s) * (np.cosh(s) ** 2 - w * math.sinh(B) ** 2) / (np.cosh(2 * s) + math.cosh(2 * B))


def main() -> None:
    use_paper_style()
    rows = json.loads(SUMMARY.read_text(encoding="utf-8"))["rows"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.1))

    B = 2.0
    wc = 1 / math.sinh(B) ** 2
    s = np.linspace(-3.5, 3.5, 701)
    for ratio, color, ls in ((0.5, OI["blue"], "-"), (1.0, OI["black"], "--"), (10.0, OI["vermillion"], "-")):
        ax1.plot(s, F(s, ratio * wc, B), color=color, ls=ls, lw=1.8, label=rf"$w={ratio:g}\,w_c$")
    ax1.axhline(0, color="#888888", lw=0.8)
    ax1.axvline(0, color="#888888", lw=0.8)
    ax1.set_xlabel(r"$s=tx/(1-t)^2$")
    ax1.set_ylabel(r"composite mean $F_w(s)$")
    ax1.set_title(r"(a) mechanism, $B=2$", loc="left")
    ax1.legend(loc="upper left")
    style(ax1)

    colors = {1.0: OI["blue"], 2.0: OI["green"], 3.0: OI["vermillion"]}
    for Bv, color in colors.items():
        pts = sorted((r["w"] * math.sinh(Bv) ** 2, r["basin_probability"])
                     for r in rows if r["name"].startswith(f"symmetric_B{Bv:g}_"))
        x, y = zip(*pts)
        ax2.plot(x, y, "o-", color=color, ms=5, lw=1.5, label=rf"$B={Bv:g}$")
    ax2.axvline(1.0, color=OI["black"], ls="--", lw=1.0)
    ax2.text(1.06, 0.95, r"$w=w_c$", fontsize=9, va="top")
    ax2.set_xscale("log")
    ax2.set_xlabel(r"guidance relative to threshold, $w/w_c$")
    ax2.set_ylabel(r"$\Pr(X_1=0)$ under $\pi_0$")
    ax2.set_ylim(-0.03, 1.03)
    ax2.set_title("(b) probability of the non-training endpoint", loc="left")
    ax2.legend(loc="center left")
    style(ax2)

    fig.tight_layout()
    out = FIGDIR / "fig_composition.pdf"
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
