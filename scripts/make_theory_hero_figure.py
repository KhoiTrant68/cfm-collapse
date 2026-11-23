"""Figure fig:unrolled of paper_theory (Figure 1): where every source ends, on a triangle of training points.

    PYTHONPATH=.:scripts python scripts/make_theory_hero_figure.py

Endpoint basin maps of three exact fields on the triangle of Section sec:intervention-tests (three
training points a_1, a_2, a_3 on the unit circle, conditional priors favouring one vertex each with
B = 2, uniform unconditional prior; v_k is the exact field of the condition favouring a_k):

  (a) v_1                                      one field (label noise at one query, Theorem thm:endpoint)
  (b) (1+w) v_1 - w v_unc,             w=2w_c  guidance, two fields (Corollary cor:twofields)
  (c) (1+w) (1/3) sum_k v_k - w v_unc, w=2w_c  guidance on the average of the three conditional
                                               fields, the conjunction (Theorem thm:spectral)
  (d) the same kind of blend on CIFAR-10: two training images and their midpoint, the image tiles
      of Figure fig:cifar-composition (pair (158, 230); see make_theory_cifar_composition_figure.py).

Every pixel of (a)-(c) is an initial point x0 of a 500 x 500 grid on [-2.5, 2.5]^2, coloured by the
endpoint of its exact trajectory: a training point (blue, green, purple) or a blend (vermillion: the
centre of the triangle, darker; the midpoint of an edge, lighter). Dashed circles: radius 1 and 2,
one and two standard deviations of pi_0. The bars under the maps are the endpoint law: atoms a_1,
a_2, a_3, the three edge midpoints together, the centre. The classes and the endpoint probabilities
under pi_0 = N(0, I_2)
(Monte Carlo over 32768 fresh sources) are read from results/theory_basin_map_20261121/, written by
scripts/theory_basin_map.py, which integrates the exact fields in float64 and reproduces, source by
source, the centre fractions of results/learned_composition_2d_20261021/exact/exact.json. Nothing is
computed here except colours and positions; the probabilities drawn are printed to stdout.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from PIL import Image

from scripts.figstyle import COLORS, FULL_W, OI, use_paper_style

ROOT = Path("results/theory_basin_map_20261121")
TILES = Path("results/cifar_composition_exact_20261105/figure_tiles")
OUT = Path("paper_theory/figures/fig_unrolled_exact.pdf")
GREY = "#555555"
ATOM = [OI["blue"], OI["green"], OI["purple"]]          # a_1 (top), a_2 (lower left), a_3 (lower right)
BLEND = OI["vermillion"]
PANELS = (("one_r0", "Label noise", r"one exact field  $v_1$"),
          ("cfg_r2", r"Guidance, $w=2w_c$", r"$(1+w)\,v_1-w\,v_{\mathrm{unc}}$"),
          ("conj_r2", r"Conjunction, $w=2w_c$", r"$(1+w)\,\frac{1}{3}(v_1+v_2+v_3)-w\,v_{\mathrm{unc}}$"))
HALO = [__import__("matplotlib.patheffects", fromlist=["withStroke"]).withStroke(linewidth=1.8,
                                                                              foreground="white")]


def tint(color: str, f: float) -> np.ndarray:
    """Mix a colour with white; f = 1 keeps it, f = 0 is white."""
    return 1 - f * (1 - np.asarray(to_rgb(color)))


CLASS_RGB = np.array([tint(ATOM[0], 0.50), tint(ATOM[1], 0.50), tint(ATOM[2], 0.50),
                      tint(BLEND, 0.92),                           # centre of the triangle
                      tint(BLEND, 0.50), tint(BLEND, 0.50), tint(BLEND, 0.50),   # edge midpoints
                      tint("#888888", 1.0)])                       # unresolved (none occur)


def draw_map(ax, cls, g, A, show_blends: bool) -> None:
    L = g[-1]
    ax.imshow(CLASS_RGB[cls], origin="lower", extent=(-L, L, -L, L), interpolation="nearest",
              zorder=0, rasterized=True)
    for k in np.unique(cls):                                       # crisp cell boundaries
        ax.contour(g, g, (cls == k).astype(float), levels=[0.5], colors="white", linewidths=0.45,
                   zorder=1)
    th = np.linspace(0, 2 * np.pi, 400)
    for rad in (1.0, 2.0):                                         # source density pi_0: 1 and 2 sd
        ax.plot(rad * np.cos(th), rad * np.sin(th), color="#333333", lw=0.45, ls=(0, (3, 2)),
                alpha=0.55, zorder=2)
    tri = np.vstack([A, A[:1]])
    ax.plot(tri[:, 0], tri[:, 1], color="#333333", lw=0.5, alpha=0.45, zorder=2)
    ax.scatter(A[:, 0], A[:, 1], marker="^", s=34, color=COLORS["atom"], edgecolors="white",
               linewidths=0.6, zorder=5)
    if show_blends:
        mids = np.vstack([np.zeros((1, 2)), [(A[i] + A[j]) / 2 for i, j in ((1, 2), (0, 2), (0, 1))]])
        ax.scatter(mids[:, 0], mids[:, 1], marker="D", s=20, color=BLEND, edgecolors="white",
                   linewidths=0.6, zorder=5)
    ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#999999"); s.set_linewidth(0.6)


def draw_law(ax, mc) -> None:
    """Stacked bar of the endpoint law: a_1, a_2, a_3, edge midpoints, centre."""
    segs = [(mc["atom0"]["p"], CLASS_RGB[0], "a"), (mc["atom1"]["p"], CLASS_RGB[1], "a"),
            (mc["atom2"]["p"], CLASS_RGB[2], "a"), (mc["edges"]["p"], CLASS_RGB[4], "e"),
            (mc["centre"]["p"], CLASS_RGB[3], "c")]
    x = 0.0
    small = []
    for p, col, kind in segs:
        if p <= 0:
            continue
        ax.barh(0, p, left=x, height=1.0, color=col, edgecolor="white", linewidth=0.5)
        txt = (f"{100 * p:.1f}%" if p > 0.995 else f"{100 * p:.0f}%") if p >= 0.095 else None
        if txt:
            ax.text(x + p / 2, 0, txt, ha="center", va="center", fontsize=6.5,
                    color="white" if kind == "c" else "#1a1a1a")
        else:
            small.append(p)
        x += p
    if small:
        ax.text(1.0, -0.62, rf"$a_2$, $a_3$: {100 * small[0]:.1f}% each", ha="right", va="top",
                fontsize=6.0, color=GREY)
    ax.set_xlim(0, 1); ax.set_ylim(-0.5, 0.5)
    ax.axis("off")


def main() -> None:
    use_paper_style()
    z = np.load(ROOT / "maps.npz")
    S = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    g, A = z["grid"], z["atoms"]
    W, H = FULL_W, 2.66
    fig = plt.figure(figsize=(W, H))
    inch = lambda x, y, w, h: fig.add_axes((x / W, y / H, w / W, h / H))   # noqa: E731
    text = lambda x, y, t, **kw: fig.text(x / W, y / H, t, **kw)          # noqa: E731
    side, gap, x0, y0 = 1.70, 0.13, 0.03, 0.38
    y_title, y_formula, y_bar = y0 + side + 0.19, y0 + side + 0.045, 0.19
    axes = []
    for k, (tag, name, formula) in enumerate(PANELS):
        xk = x0 + k * (side + gap)
        ax = inch(xk, y0, side, side)
        draw_map(ax, z[tag], g, A, show_blends=(tag.startswith("conj")))
        text(xk, y_title, rf"$\mathbf{{({'abc'[k]})}}$  {name}", ha="left", va="bottom", fontsize=8.5)
        text(xk, y_formula, formula, ha="left", va="bottom", fontsize=7.0, color="#222222")
        if k < 2:                                                  # name the training points
            for j, (dx, dy, ha) in enumerate(((0.0, 0.19, "center"), (-0.13, -0.06, "right"),
                                              (0.13, -0.06, "left"))):
                ax.text(A[j, 0] + dx, A[j, 1] + dy, rf"$a_{j + 1}$", ha=ha, va="center",
                        fontsize=7, color="#1a1a1a", path_effects=HALO, zorder=6)
        mc = S["fields"][tag]["mc"]
        draw_law(inch(xk, y_bar, side, 0.12), mc)
        axes.append(ax)
        print(tag, {k2: round(v["p"], 4) for k2, v in mc.items() if isinstance(v, dict)})

    a = axes[0]
    a.text(np.cos(-0.80) * 2.02, np.sin(-0.80) * 2.02, r"$\pi_0$", fontsize=7, color="#333333",
           ha="left", va="top", path_effects=HALO)
    a.annotate("training\npoint", A[1], xytext=(-2.3, 0.62), textcoords="data", fontsize=6.5,
               color="#1a1a1a", ha="left", va="bottom", linespacing=1.0, path_effects=HALO,
               arrowprops=dict(arrowstyle="-", lw=0.5, color="#1a1a1a", shrinkA=1, shrinkB=4))
    c = axes[2]
    c.annotate("centre", (0, 0), xytext=(0.62, 1.85), textcoords="data", fontsize=6.5, color=BLEND,
               ha="left", va="center", path_effects=HALO,
               arrowprops=dict(arrowstyle="-", lw=0.5, color=BLEND, shrinkA=1, shrinkB=3))
    c.annotate("edge\nmidpoint", (A[0] + A[1]) / 2, xytext=(-2.35, 1.75), textcoords="data",
               fontsize=6.5, color=BLEND, ha="left", va="center", linespacing=1.0, path_effects=HALO,
               arrowprops=dict(arrowstyle="-", lw=0.5, color=BLEND, shrinkA=1, shrinkB=3))

    # (d) the same kind of endpoint on CIFAR-10
    xd = x0 + 3 * (side + gap) + 0.04
    ts = 0.50
    for i, (tile, lab, col) in enumerate(((6, r"$x^i$", "#999999"), (7, "blend", BLEND),
                                          (8, r"$x^j$", "#999999"))):
        ax = inch(xd, y0 + side - (i + 1) * ts - i * 0.10, ts, ts)
        ax.imshow(np.asarray(Image.open(TILES / f"tile-{tile:03d}.png").convert("RGB")),
                  interpolation="lanczos")
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(True); s.set_color(col); s.set_linewidth(1.3 if i == 1 else 0.6)
        ax.text(1.08, 0.5, lab, transform=ax.transAxes, ha="left", va="center", fontsize=7,
                color=BLEND if i == 1 else "#222222")
        if i == 0:
            text(xd, y_title, r"$\mathbf{(d)}$  CIFAR-10", ha="left", va="bottom", fontsize=8.5)
            text(xd, y_formula, r"$d=3072$", ha="left", va="bottom", fontsize=7.0, color="#222222")
        if i == 1:
            ax.text(1.08, 0.18, r"$=\frac{1}{2}(x^i+x^j)$", transform=ax.transAxes, ha="left",
                    va="center", fontsize=6.0, color=BLEND)

    # group headers: what the number of fields does to the endpoints
    def header(xa, xb, text, color):
        y = (y0 + side + 0.44) / H
        fig.add_artist(plt.Line2D([xa / W, xb / W], [y, y], color=color, lw=0.8))
        fig.text((xa + xb) / 2 / W, y + 0.012, text, ha="center", va="bottom", fontsize=7.5,
                 color=color)
    header(x0 + 0.02, x0 + 2 * side + gap - 0.02, "one or two fields: almost every source ends on a training point",
           COLORS["atom"])
    header(x0 + 2 * (side + gap) + 0.02, W - 0.03, "three or more fields: blends of training points", BLEND)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, pad_inches=0.0)
    plt.close(fig)
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
