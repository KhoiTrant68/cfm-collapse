"""Figure fig:learned-composition: learned versus exact guided label averaging.

(a) Two atoms (Theorem thm:composition), B = 1 and 2: probability of the midpoint endpoint of
    the composite L3 against w/w_c. The line is the exact endpoint mass (E4 of
    scripts/learned_composition_exact.py); markers are learned networks, the fraction of the 2048
    shared sources within delta = 0.05 of the midpoint at the terminal gap eps = 1e-5, mean and
    population sd over five seeds (scripts/learned_composition.py).
(b) The equilateral triangle of Section 6.2 (B = 2): the same quantities from
    scripts/learned_composition_2d.py; the exact value is the midpoint fraction of the first 4096
    shared sources under the exact composite.

The numbers drawn are printed and written to paper/figures/fig_learned_composition.json, which
scripts/verify_paper_numbers.py checks against the text.

Usage:  uv run python scripts/make_learned_composition_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from figstyle import FIGDIR, OI, style, use_paper_style

ROOT_1D = Path("results/learned_composition_20261021")
ROOT_2D = Path("results/learned_composition_2d_20261021")
SEEDS = range(5)
TABLE_1D = ("cfm_v", "cfm_v_tis", "cfm_v_sep", "cfm_x_s", "distill_x_s")   # appendix table
TABLE_2D = ("cfm_v", "cfm_x_s", "distill_x_s")
EPS, DELTA = 1e-5, 0.05
VARIANTS = {"cfm_x_s": ("data prediction, rescaled input", "o", "-"),
            "cfm_v": ("standard CFM (velocity)", "s", "none")}


def learned(root: Path, variant: str, B: float | None) -> dict[float, tuple[float, float]]:
    """r -> (mean, population sd) over seeds of the L3 midpoint occupancy."""
    per_r: dict[float, list[float]] = {}
    paths = [root / f"{variant}_seed{seed}" / "summary.json" for seed in SEEDS]
    paths = [q for q in paths if q.exists()]          # cfm_v_sep has four seeds
    assert len(paths) >= 4, (root, variant, len(paths))
    for q in paths:
        s = json.loads(q.read_text(encoding="utf-8"))
        for arm in s["arms"]:
            if arm["arm"] != "L3" or (B is not None and arm["B"] != B):
                continue
            row = next(e for e in arm["by_eps"] if abs(e["eps"] - EPS) < 1e-12)
            per_r.setdefault(arm["r"], []).append(row[f"occ_{DELTA:g}"])
    for r, v in per_r.items():
        assert len(v) == len(paths), (root, variant, B, r, len(v))
    return {r: (float(np.mean(v)), float(np.std(v))) for r, v in sorted(per_r.items())}


def exact_1d(B: float) -> dict[float, float]:
    rows = json.loads((ROOT_1D / "exact" / "summary.json").read_text(encoding="utf-8"))["rows"]
    return {r["r"]: r["basin_probability"] for r in sorted(rows, key=lambda r: r["r"])
            if r["arm"] == "E4" and r["B"] == B}


def exact_2d() -> dict[float, float]:
    rows = json.loads((ROOT_2D / "exact" / "exact.json").read_text(encoding="utf-8"))["rows"]
    return {r["r"]: r["midpoint_fraction"] for r in rows}


def draw(ax, exact, series, color, label_suffix="", legend=True):
    xs = [r if r > 0 else 0.3 for r in exact]          # w = 0 drawn at the left edge of the log axis
    ax.plot(xs, list(exact.values()), color=color, lw=1.6,
            label=None)
    for v, (name, marker, _) in VARIANTS.items():
        d = series[v]
        x = [r if r > 0 else 0.3 for r in d]
        m = [d[r][0] for r in d]
        e = [d[r][1] for r in d]
        face = color if v == "cfm_x_s" else "white"
        ax.errorbar(x, m, yerr=e, fmt=marker, ms=4.5, color=color, mfc=face, mew=1.1,
                    capsize=2, lw=0, elinewidth=1.0, label=None)


def main() -> None:
    use_paper_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 2.5))
    record: dict = {"eps": EPS, "delta": DELTA, "two_atoms": {}, "triangle": {}, "table": {}}
    for B in (1.0, 2.0, 3.0):
        record["table"][f"B={B:g}"] = {"exact": exact_1d(B), **{v: learned(ROOT_1D, v, B) for v in TABLE_1D}}
    record["table"]["triangle"] = {"exact": exact_2d(), **{v: learned(ROOT_2D, v, None) for v in TABLE_2D}}

    for B, color in ((1.0, OI["blue"]), (2.0, OI["green"])):
        ex = exact_1d(B)
        ser = {v: learned(ROOT_1D, v, B) for v in VARIANTS}
        draw(ax1, ex, ser, color, rf", $B={B:g}$")
        record["two_atoms"][f"B={B:g}"] = {"exact": ex, **ser}
    ax2_ex = exact_2d()
    ser2 = {v: learned(ROOT_2D, v, None) for v in VARIANTS}
    draw(ax2, ax2_ex, ser2, OI["vermillion"])
    record["triangle"] = {"exact": ax2_ex, **ser2}

    for ax, title in ((ax1, "(a) two atoms"), (ax2, r"(b) triangle, $B=2$")):
        ax.axvline(1.0, color=OI["black"], ls="--", lw=0.9)
        ax.set_xscale("log")
        ax.set_xlim(0.25, 12)
        ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel(r"$w/w_c$ ($w=0$ at the left edge)")
        ax.set_title(title, loc="left")
        style(ax)
    ax1.set_ylabel("midpoint probability")
    # Colour encodes the configuration (panel a), marker the field (panel b): two short legends.
    ax1.legend(handles=[Line2D([], [], color=OI["blue"], lw=1.6, label=r"$B=1$"),
                        Line2D([], [], color=OI["green"], lw=1.6, label=r"$B=2$")],
               loc="upper left", fontsize=8)
    grey = "#444444"
    ax2.legend(handles=[Line2D([], [], color=grey, lw=1.6, label="exact field"),
                        Line2D([], [], color=grey, marker="o", ls="none", label="data prediction, rescaled input"),
                        Line2D([], [], color=grey, marker="s", mfc="white", ls="none",
                               label="standard CFM (velocity)")],
               loc="upper left", fontsize=8)
    fig.tight_layout()
    out = FIGDIR / "fig_learned_composition.pdf"
    fig.savefig(out)
    (FIGDIR / "fig_learned_composition.json").write_text(
        json.dumps(record, indent=1, default=str), encoding="utf-8")
    for cfg, d in record["table"].items():
        for v, x in d.items():
            print(cfg, v, {r: (round(y, 3) if isinstance(y, float) else [round(z, 3) for z in y])
                           for r, y in x.items()})
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
