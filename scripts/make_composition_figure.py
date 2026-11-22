"""Figure fig:composition of paper_theory: the bifurcation behind Theorem thm:composition, and its size.

    PYTHONPATH=.:scripts python scripts/make_composition_figure.py

(a) Profiles of the guided label average on the atoms -1, +1 (Theorem thm:composition): the zeros of
    F_w(s) = 2 tanh(s) (cosh^2 s - w sinh^2 B) / (cosh 2s + cosh 2B), eq. composition-mean, against
    w/w_c, w_c = 1/sinh^2 B. They are s = 0 and, for w > w_c, s = +-s_u with cosh s_u = sqrt(w/w_c)
    (the closed form cosh s_u = sqrt(w) sinh B), so in the coordinate s they depend on B only through
    w/w_c. Stability is the sign of F_w': F_w'(0) = sech^2 B (1 - w/w_c), and F_w'(+-s_u) > 0. In the
    profile time ds/du = F_w(s) + o(1), so for w > w_c the profiles in (-s_u, s_u) are attracted to
    the tie (shaded: the endpoint is the midpoint) and those outside leave for an atom. Curves are
    the closed forms; the circles are the roots computed numerically by
    scripts/composition_counterexample.py for B = 1, 2, 3 (results/theory_composition_20261019/
    summary.json), which this script checks against the closed form (|difference| < 1e-9) together
    with the sign of the computed slope F_w'(0).
(b) Probability P_0 under N(0,1) that the trajectory ends at the midpoint, rescaled by the
    prefactor of the near-threshold law P_0 ~ sqrt(2/pi) (w/w_c - 1)/cosh B
    (Appendix apx:threshold-scaling), against w/w_c - 1 on log-log axes: the exact basin
    probabilities of results/composition_threshold_scaling_20261107/summary.json (w/w_c - 1 from
    3e-4 to 0.3) and results/theory_composition_20261019/summary.json (w/w_c = 2, 10 and w = 1, 3),
    for B = 1, 2, 3. The dashed line y = x is the law; the dotted lines are P_0 = 1. Below the
    threshold P_0 = 0 (Theorem thm:composition(b)).

Nothing is computed here except closed forms; the plotted values are printed.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import COLORS, FULL_W, OI, panel_title, style, use_paper_style

SUMMARY = Path("results/theory_composition_20261019/summary.json")
SCALING = Path("results/composition_threshold_scaling_20261107/summary.json")
OUT = Path("paper_theory/figures/fig_composition.pdf")
WIDTH = 0.98 * FULL_W
GREY = "#555555"
BLEND = OI["vermillion"]
B_COLORS = {1.0: OI["blue"], 2.0: OI["green"], 3.0: OI["purple"]}
PREF = math.sqrt(2 / math.pi)


def load_rows():
    rows = [r for r in json.loads(SUMMARY.read_text(encoding="utf-8"))["rows"]
            if r["name"].startswith("symmetric_")]
    for r in rows:                                      # check the closed forms against the numerics
        ratio = r["w_over_wc"]
        assert (r["dF0"] < 0) == (ratio > 1), r["name"]
        outer = sorted(x["s"] for x in r["roots"] if abs(x["s"]) > 1e-9)
        if ratio > 1:
            su = math.acosh(math.sqrt(ratio))
            assert len(outer) == 2 and max(abs(outer[1] - su), abs(outer[0] + su)) < 1e-9, r["name"]
            assert all(x["dF"] > 0 for x in r["roots"] if abs(x["s"]) > 1e-9)
        else:
            assert not outer, r["name"]
    return rows


def main() -> None:
    use_paper_style()
    rows = load_rows()
    scal = json.loads(SCALING.read_text(encoding="utf-8"))["rows"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH, 2.55), gridspec_kw={"width_ratios": [1.0, 1.0]})

    # (a) pitchfork of profiles
    r_lo, r_hi, s_max = 0.3, 12.0, 2.45
    r = np.geomspace(1.0, r_hi, 400)
    su = np.arccosh(np.sqrt(r))
    ax1.axvspan(r_lo, r_hi, color="#f4f4f4", lw=0, zorder=0)                  # atoms
    ax1.fill_between(r, -su, su, color=BLEND, alpha=0.20, lw=0, zorder=1)     # midpoint
    ax1.plot([r_lo, 1.0], [0, 0], color=GREY, lw=1.3, ls=(0, (3, 2)), zorder=3)
    ax1.plot([1.0, r_hi], [0, 0], color=BLEND, lw=1.8, zorder=4)
    for sg in (1, -1):
        ax1.plot(r, sg * su, color=COLORS["atom"], lw=1.1, ls=(0, (3, 2)), zorder=4)
    ax1.axvline(1.0, color="#999999", lw=0.6, zorder=2)
    # numerically computed roots (all B; they coincide in s)
    for row in rows:
        ratio = row["w_over_wc"]
        if r_lo <= ratio <= r_hi:
            ss = [x["s"] for x in row["roots"]]
            ax1.plot([ratio] * len(ss), ss, "o", ms=3.6, mfc="white", mec=COLORS["atom"], mew=0.7,
                     zorder=6, clip_on=False)
    # phase-line arrows: direction of ds/du
    kw = dict(arrowstyle="-|>", lw=0.7, color=GREY, mutation_scale=6, shrinkA=0, shrinkB=0)
    for y0, y1 in ((0.25, 0.85), (-0.25, -0.85), (1.45, 2.05), (-1.45, -2.05)):
        ax1.annotate("", xy=(0.62, y1), xytext=(0.62, y0), arrowprops=kw, zorder=5)
    s4 = math.acosh(2.0)                                                     # w/w_c = 4
    for y0, y1 in ((s4 - 0.12, 0.18), (-s4 + 0.12, -0.18), (s4 + 0.12, s4 + 0.62), (-s4 - 0.12, -s4 - 0.62)):
        ax1.annotate("", xy=(4.0, y1), xytext=(4.0, y0), arrowprops=kw, zorder=5)
    ax1.text(0.40, 0.09, "tie repels", fontsize=6.5, color=GREY, ha="center", va="bottom")
    ax1.text(7.2, 0.09, "tie attracts", fontsize=6.5, color=BLEND, ha="center", va="bottom")
    ax1.text(7.2, -0.55, "ends at the\nmidpoint", fontsize=6.5, color=BLEND, ha="center", va="center",
             linespacing=1.0)
    ax1.text(0.33, 2.3, "ends at atom $+1$", fontsize=6.5, color=GREY, ha="left", va="top")
    ax1.text(0.33, -2.3, "ends at atom $-1$", fontsize=6.5, color=GREY, ha="left", va="bottom")
    ax1.annotate(r"$\cosh s_u=\sqrt{w/w_c}$", (8.0, math.acosh(math.sqrt(8.0))), xytext=(5.6, 2.25),
                 textcoords="data", fontsize=6.5, ha="center", va="top",
                 arrowprops=dict(arrowstyle="-", lw=0.5, color=COLORS["atom"], shrinkA=1, shrinkB=2))
    ax1.set_xscale("log")
    ax1.set_xlim(r_lo, r_hi); ax1.set_ylim(-s_max, s_max)
    ax1.set_xticks([0.5, 1, 2, 5, 10]); ax1.set_xticklabels(["0.5", "1", "2", "5", "10"])
    ax1.xaxis.set_minor_formatter(plt.NullFormatter())
    ax1.set_xlabel(r"guidance relative to threshold, $w/w_c$")
    ax1.set_ylabel(r"profile $s=tx/(1-t)^2$ at the tie")
    ax1.grid(False)
    panel_title(ax1, "a", r"At $w_c$ the tie turns attracting")
    style(ax1)

    # (b) scaling collapse of the basin probability
    pts: dict[float, dict[float, float]] = {}
    for row in scal:
        pts.setdefault(row["B"], {})[round(row["delta"], 12)] = row["P0"]
    for row in rows:
        d = row["w_over_wc"] - 1
        Bv = float(row["name"].split("_")[1][1:])
        if d > 0:
            pts.setdefault(Bv, {}).setdefault(round(d, 12), row["basin_probability"])
    x_line = np.geomspace(1e-4, 600, 50)
    ax2.plot(x_line, x_line, color=COLORS["theory"], lw=0.9, ls=(0, (4, 2)), zorder=2)
    ax2.text(1.6e-2, 2.2e-3, "$y=x$, the near-threshold law\n"
             r"$P_0\simeq\sqrt{2/\pi}\,(w/w_c-1)/\cosh B$", fontsize=6.5, ha="left", va="center",
             linespacing=1.3)
    marks = {1.0: dict(marker="o", ms=4.6, mfc="white", mew=0.8),       # distinct shapes, so that the
             2.0: dict(marker="s", ms=3.2, mfc="white", mew=0.8),       # coinciding series all show
             3.0: dict(marker="o", ms=1.9, mew=0.0)}
    for Bv, col in B_COLORS.items():
        d = np.array(sorted(pts[Bv]))
        P = np.array([pts[Bv][k] for k in d])
        y = P * math.cosh(Bv) / PREF
        ax2.plot(d, y, "-", color=col, lw=0.9, zorder=3)
        ax2.plot(d, y, ls="none", color=col, mec=col, zorder=4 + Bv, **marks[Bv])
        sat = math.cosh(Bv) / PREF
        ax2.axhline(sat, color=col, lw=0.7, ls=(0, (1, 1.5)), zorder=1)
        ax2.text(1.6e-4, sat * 1.12, rf"$B={Bv:g}$: $P_0=1$", fontsize=6.3, color=col, ha="left",
                 va="bottom")
        print(f"B={Bv:g}", [(float(a), round(float(b), 5)) for a, b in zip(d, P)])
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlim(1.2e-4, 600); ax2.set_ylim(1.5e-4, 40)
    ax2.set_xlabel(r"distance to the threshold, $w/w_c-1$")
    ax2.set_ylabel(r"rescaled probability $P_0\,\cosh B\,/\sqrt{2/\pi}$")
    panel_title(ax2, "b", r"The blend starts linearly at $w_c$")
    style(ax2)

    fig.tight_layout(w_pad=1.8)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
