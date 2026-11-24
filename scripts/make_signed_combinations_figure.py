"""Figure fig:signed of paper_theory: which sampler recipes can blend two training examples.

    PYTHONPATH=.:scripts python scripts/make_signed_combinations_figure.py

(a) A scorecard of the recipes of Sections sec:posmix-sec:conjunction at a tie of two training
    points a, b. Each row draws the fields of the recipe at the tie as bars: a field with
    restricted log-odds 2B(p) (Section sec:conjunction) is a bar at B(p), pointing up when it is added
    and down when it is subtracted, with height proportional to its coefficient (scaled per row); a
    subtracted field strictly between the extreme ones while both extreme fields are added (the sign
    pattern that Proposition prop:twoatom requires for a blend) is vermillion. The right column is
    the probability under N(0,1) that the endpoint
    is the midpoint: 0 for every configuration where a result proves it (cited), and otherwise the
    value of results/theory_signed_combinations_20261121/summary.json (stiff integration with
    proof-based stopping rules, scripts/signed_combinations_check.py). For the rows proved zero the
    bars show one representative configuration (B = 2, guidance w = 2, negative guidance w = -1/2,
    the conjunction at w = w_c); the computed rows show exactly the configuration computed.
(b) The probability of the midpoint over the three-prior family B(p) in {B, 0, -B} at B = 1:
    coefficients c_+ (condition favouring a), c_- (favouring b), and 1 - c_+ - c_- for the
    unconditional field, one cell per point of the 0.1 grid, from results/theory_signed_probability_
    20261121/probability_B1.npz (scripts/signed_combinations_probability.py, the same integrator and
    stopping rules, basin ends bisected to 1e-7). The vermillion line bounds the region where F has a
    zero with negative slope (results/theory_signed_combinations_20261121/phase_map.npz, 0.05 grid);
    outside it the probability is 0. Inside it, 18 of the 582 grid cells with such a zero are left
    white: no source of the 0.025 search grid on [-3, 3] reaches the midpoint, so their probability is
    below 0.01. Dashed: the equal conjunction c_+ = c_- = (1+w)/2, which enters the region at w = w_c
    (dot). Star: the equal conjunction at w = 2 w_c of (a).

Result numbers in the labels are those of the current paper_theory build; if THEORY_AUX points to
its main.aux they are checked against it. Nothing is computed here except the conjunction threshold.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from scripts.figstyle import COLORS, FULL_W, OI, panel_title, style, use_paper_style

ROOT = Path("results/theory_signed_combinations_20261121")
PROB = Path("results/theory_signed_probability_20261121")
COMP = Path("results/theory_composition_20261019/summary.json")
OUT = Path("paper_theory/figures/fig_signed_combinations.pdf")
WIDTH = 0.98 * FULL_W
BLEND = OI["vermillion"]
GREY = "#555555"
# Numbers of the cited results in the current build (checked against THEORY_AUX when given).
REF = {"thm:endpoint": "4.4", "thm:posmix": "5.1", "prop:filtered": "5.2", "prop:cfgatom": "5.4",
       "cor:negcfg": "5.5", "thm:schedule": "5.6", "cor:twofields": "5.7", "thm:composition": "5.8",
       "prop:twoatom": "5.13"}


def check_refs() -> None:
    aux = os.environ.get("THEORY_AUX")
    if not aux:
        return
    text = Path(aux).read_text(encoding="utf-8", errors="replace")
    for key, num in REF.items():
        m = re.search(r"\\newlabel\{" + re.escape(key) + r"\}\{\{([^}]*)\}", text)
        assert m and m.group(1) == num, (key, num, m and m.group(1))
    print("  result numbers checked against", aux)


def rows(basins: dict) -> list[dict]:
    """Recipes: name, group, bars [(B(p), c)], probability (None: proved 0) and citation."""
    R = lambda k: REF[k]                                             # noqa: E731
    wc2 = 1 / math.sinh(2.0) ** 2
    b = {r["name"]: r for r in basins}

    def comp(name):
        r = b[name]
        return [(Bk, ck) for Bk, ck in zip(r["B"], r["c"])], r["midpoint_probability"]
    out = [
        dict(group="one field, or a positive mixture of any number", name="Label noise",
             bars=[(2.0, 1.0)], p=None, cite=f"Thm {R('thm:endpoint')}"),
        dict(name="Label averaging", bars=[(2.0, 0.5), (-2.0, 0.5)], p=None,
             cite=f"Thm {R('thm:posmix')}"),
        dict(name=r"Negative guidance, $w\in[-1,0)$", bars=[(2.0, 0.5), (0.0, 0.5)], p=None,
             cite=f"Cor {R('cor:negcfg')}"),
        dict(group="two fields, any signs", name=r"Guidance, $w\geq0$, fixed or scheduled",
             bars=[(2.0, 3.0), (0.0, -2.0)], p=None,
             cite=f"Prop {R('prop:cfgatom')}, Thm {R('thm:schedule')}"),
    ]
    bars, p = comp("negative_prompt_substituted")
    out.append(dict(name=r"Negative prompt by substitution", bars=bars, p=None,
                    cite=f"Cor {R('cor:twofields')}", computed=p))
    bars, p = comp("negative_prompt_opposite")
    out.append(dict(group="three fields", name=r"Prompt $a$, negative prompt $b$", bars=bars,
                    p=None, cite=f"Prop {R('prop:twoatom')}(b)", computed=p))
    out.append(dict(name=r"Conjunction, $w\leq w_c$", bars=[(2.0, (1 + wc2) / 2), (0.0, -wc2),
                                                           (-2.0, (1 + wc2) / 2)],
                    p=None, cite=f"Thm {R('thm:composition')}(b)"))
    bars, p = comp("conjunction_equal_B1_w2wc")
    out.append(dict(name=r"Conjunction, $B=1$, $w=2w_c$", bars=bars, p=p))
    bars, p = comp("conjunction_unequal_B2")
    out.append(dict(name=r"Unequal conjunction, $B=2$", bars=bars, p=p))
    bars, p = comp("negative_prompt_milder")
    out.append(dict(name=r"Prompt $a$, milder negative $a$", bars=bars, p=p))
    for r in out:                                          # the proved zeros that were also computed
        assert r.get("computed", 0.0) == 0.0, r["name"]
    return out


def draw_glyph(ax, y, bars, h=0.36) -> None:
    """Bars c_k at B(p_k); vermillion marks the sign pattern that Proposition prop:twoatom requires
    for a blend: an inner field subtracted while both extreme fields are added."""
    Bs = [Bk for Bk, _ in bars]
    lo, hi = min(Bs), max(Bs)
    ext_added = all(c > 0 for Bk, c in bars if Bk in (lo, hi))
    m = max(abs(c) for _, c in bars)
    ax.plot([-2.45, 2.45], [y, y], color="#b0b0b0", lw=0.5, zorder=1)
    for Bk, c in bars:
        inner = c < 0 and lo < Bk < hi and ext_added
        col = BLEND if inner else ("#3a3a3a" if c > 0 else "#9a9a9a")
        ax.add_patch(plt.Rectangle((Bk - 0.17, y), 0.34, -h * c / m, color=col, lw=0, zorder=2))


def main() -> None:
    use_paper_style()
    check_refs()
    S = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    recs = rows(S["basins"])
    W, H = WIDTH, 2.72
    fig = plt.figure(figsize=(W, H))
    ax_of = lambda x, y, w, h: fig.add_axes((x / W, y / H, w / W, h / H))   # noqa: E731

    # ---- (a) scorecard -------------------------------------------------------------------------
    ylines = []
    y = 0.0
    for r in recs:
        if "group" in r:
            y += 0.55 if ylines else 0.0
            ylines.append(("g", y, r["group"]))
            y += 0.95
        ylines.append(("r", y, r))
        y += 1.0
    ny = y
    top, bot = 2.36, 0.30
    x_name, w_name, x_gly, w_gly, x_pr, w_pr = 0.0, 1.72, 1.78, 0.72, 2.58, 1.04
    axn = ax_of(x_name, bot, w_name, top - bot)
    axg = ax_of(x_gly, bot, w_gly, top - bot)
    axp = ax_of(x_pr, bot, w_pr, top - bot)
    for a in (axn, axg, axp):
        a.set_ylim(ny - 0.4, -0.6)
        a.axis("off")
    axn.set_xlim(0, 1); axg.set_xlim(-2.6, 2.6); axp.set_xlim(0, 1.45)
    for kind, yy, r in ylines:
        if kind == "g":
            axn.text(0.0, yy, r, ha="left", va="center", fontsize=6.6, color=GREY, style="italic")
            for a, x0, x1 in ((axn, 0.0, 1.0), (axg, -2.6, 2.6), (axp, 0.0, 1.45)):
                a.plot([x0, x1], [yy + 0.48, yy + 0.48], color="#d0d0d0", lw=0.5, clip_on=False)
            continue
        axn.text(0.03, yy, r["name"], ha="left", va="center", fontsize=6.9)
        draw_glyph(axg, yy + 0.20, r["bars"], h=0.42)
        if r["p"] is None:
            axp.plot([0, 0], [yy - 0.3, yy + 0.3], color=COLORS["atom"], lw=1.2, solid_capstyle="butt")
            axp.text(0.05, yy, "0", ha="left", va="center", fontsize=6.6, color=COLORS["atom"])
            axp.text(0.15, yy, r["cite"], ha="left", va="center", fontsize=6.3, color=GREY)
        else:
            axp.barh(yy, r["p"], height=0.58, color=BLEND, lw=0)
            axp.text(r["p"] + 0.04, yy, f"{r['p']:.3f}", ha="left", va="center", fontsize=6.6,
                     color=BLEND)
    yh = -1.15
    axn.text(0.0, yh, r"$\mathbf{(a)}$  Recipes at a tie of $a$ and $b$", ha="left", va="bottom",
             fontsize=8.5, clip_on=False)
    axg.text(0.0, yh, "fields at the tie", ha="center", va="bottom", fontsize=7, clip_on=False)
    axg.text(-2.5, ny - 0.15, r"$\leftarrow b$", ha="left", va="top", fontsize=6.3, color=GREY)
    axg.text(2.5, ny - 0.15, r"$a\rightarrow$", ha="right", va="top", fontsize=6.3, color=GREY)
    axg.text(0.0, ny - 0.15, "favours", ha="center", va="top", fontsize=6.3, color=GREY)
    axp.text(0.0, yh, r"$\Pr(\mathrm{endpoint}=\mathrm{midpoint})$", ha="left", va="bottom",
             fontsize=7, clip_on=False)

    # ---- (b) probability over the three-prior family, B = 1 --------------------------------------
    Bm = 1.0
    z = np.load(PROB / f"probability_B{Bm:g}.npz")
    cs, P = z["cs"], z["P"]
    pm = np.load(ROOT / "phase_map.npz")
    side = 1.80
    xb = W - side - 0.55
    axb = ax_of(xb, 0.40, side, side)
    cmap = LinearSegmentedColormap.from_list("blend", ["#fdf0e6", "#f4a46c", BLEND, "#8c3a00"],
                                             N=256)
    d = (cs[1] - cs[0]) / 2
    edges = np.concatenate([cs - d, [cs[-1] + d]])
    mesh = axb.pcolormesh(edges, edges, np.ma.masked_where(P <= 0, P), cmap=cmap, vmin=0, vmax=1,
                          shading="flat", zorder=0, rasterized=True)
    axb.contour(pm["cs"], pm["cs"], pm[f"B{Bm:g}"].astype(float), levels=[0.5], colors=[BLEND],
                linewidths=0.8, zorder=3)
    axb.axhline(0, color="#999999", lw=0.6, zorder=1); axb.axvline(0, color="#999999", lw=0.6, zorder=1)
    axb.plot([0.5, cs[-1]], [0.5, cs[-1]], ls=(0, (3, 2)), color=COLORS["theory"], lw=0.8, zorder=4)
    wc = 1 / math.sinh(Bm) ** 2
    cw = (1 + wc) / 2
    axb.plot([cw], [cw], "o", ms=3.4, color=COLORS["theory"], zorder=6)
    axb.annotate(r"$w=w_c$", (cw, cw), xytext=(1.7, 0.35), textcoords="data", fontsize=6.5,
                 ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", lw=0.5, color=COLORS["theory"], shrinkA=1, shrinkB=2))
    axb.text(3.55, 3.15, r"$w\uparrow$", fontsize=6.5, ha="left", va="top")
    cj = [r for r in S["basins"] if r["name"] == "conjunction_equal_B1_w2wc"][0]
    cp0, cm0 = cj["c"][0], cj["c"][2]
    axb.plot([cp0], [cm0], marker="*", ms=9.0, color="white", mec="#222222", mew=0.6, zorder=7)
    axb.annotate(f"{cj['midpoint_probability']:.3f}", (cp0, cm0), xytext=(-0.55, 1.75),
                 textcoords="data", fontsize=6.3, color=BLEND, ha="center", va="center",
                 arrowprops=dict(arrowstyle="-", lw=0.5, color=BLEND, shrinkA=1, shrinkB=3))
    axb.text(-0.85, 3.85, "no blend:\nan endpoint is a\ntraining point a.s.", fontsize=6.3, color=GREY,
             ha="left", va="top", linespacing=1.05)
    axb.set_xlim(cs[0], cs[-1]); axb.set_ylim(cs[0], cs[-1]); axb.set_aspect("equal")
    axb.set_xticks(range(-1, 5)); axb.set_yticks(range(-1, 5))
    axb.set_xlabel(r"$c_+$, condition favouring $a$")
    axb.set_ylabel(r"$c_-$, condition favouring $b$", labelpad=1)
    axb.grid(False)
    style(axb)
    y_title = top + 0.55 * (top - bot) / (ny + 0.2)                  # baseline of the (a) title
    fig.text((xb - 0.36) / W, y_title / H, rf"$\mathbf{{(b)}}$  Three fields, $B={Bm:g}$",
             ha="left", va="bottom", fontsize=8.5)
    cax = ax_of(xb + side + 0.08, 0.40, 0.07, side)
    cb = fig.colorbar(mesh, cax=cax, ticks=[0, 0.5, 1])
    cb.ax.tick_params(labelsize=6.5, length=2, width=0.5)
    cb.outline.set_linewidth(0.5)
    cb.set_label(r"$\Pr(\mathrm{midpoint})$", fontsize=7, labelpad=2)
    print(f"B={Bm:g} map: max P", float(np.nanmax(P)), "cells with P > 0:", int((P > 0).sum()),
          "sink cells:", int(z["sink"].sum()))
    for r in recs:
        print(f"  {r['name']}: {'proved 0, ' + r['cite'] if r['p'] is None else round(r['p'], 4)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, pad_inches=0.0)
    plt.close(fig)
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
