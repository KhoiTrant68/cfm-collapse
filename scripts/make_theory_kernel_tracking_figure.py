"""Figure fig:kernel-tracking of paper_theory: do trained networks follow the label-noise reference?

    python -m scripts.make_theory_kernel_tracking_figure

Theorem thm:endpoint fixes, for label noise of bandwidth h, the variance tr Cov_h of the
label-weighted training examples. This compares it with the variance of samples from trained
networks. It reads only saved records and writes only the figure; nothing is trained or sampled.

  (a) linear-Gaussian problem (d=2, N=200, five seeds): generated tr Cov over tr Cov_h per seed and
      bandwidth, with the mean and population SD over seeds and the effective number of atoms
      n_eff (results/exp1/_theory/raw/p7_kernel.csv; Table tab:p7kernel).
  (b) CIFAR-10 inpainting at h=4: generated against reference trace at the 48 conditions of each of
      the three networks retrained on independent draws of the training set, with their OLS slopes
      on log10 (results/exp3/_rerun/reeval_exp3_cifar_heff_h4_s{0,1,2}/reeval.json; Table
      tab:cifar-kernel, "slope, three draws"). The exact field puts every point on y = x.

The figure is drawn from these records alone and shares no file with any other figure.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from scripts.figstyle import COLORS, FULL_W, panel_title, style, use_paper_style

P7 = Path("results/exp1/_theory/raw/p7_kernel.csv")
CIFAR = Path("results/exp3/_rerun")
OUT = Path("paper_theory/figures/fig_kernel_tracking.pdf")
GREY = "#555555"
LEARNED = COLORS["learned"]          # vermillion: what a trained network generates
EXACT = COLORS["theory"]             # black dashed: the exact-field prediction
MARKERS = ("o", "s", "^")            # one per retrained draw, so identity is not colour alone


def read_p7() -> dict[float, dict[str, np.ndarray]]:
    with P7.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"{P7} is empty")
    out: dict[float, dict[str, list]] = {}
    for r in rows:
        d = out.setdefault(float(r["h"]), {"ratio": [], "n_eff": []})
        d["ratio"].append(float(r["ratio_to_kernel"]))
        d["n_eff"].append(float(r["n_eff"]))
    return {h: {k: np.asarray(v) for k, v in d.items()} for h, d in sorted(out.items())}


def read_reeval(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec = rec[0] if isinstance(rec, list) else rec
    ref = np.asarray(rec["trace_kernel_per_condition"], float)
    meas = np.asarray(rec["ratio_per_condition"], float) * ref
    return ref, meas


def ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    xc, yc = x - x.mean(), y - y.mean()
    slope = float((xc * yc).sum() / (xc * xc).sum())
    return slope, float(y.mean() - slope * x.mean())


def main() -> None:
    use_paper_style()
    p7 = read_p7()
    hs = list(p7)
    mean = np.array([p7[h]["ratio"].mean() for h in hs])
    sd = np.array([p7[h]["ratio"].std() for h in hs])          # population SD, as in the table
    neff = np.array([p7[h]["n_eff"].mean() for h in hs])
    # The printed values of Table tab:p7kernel; stop rather than draw a figure that disagrees.
    assert np.allclose(mean, [1.308, 1.002, 0.994, 1.011], atol=5e-4), mean
    assert np.allclose(sd, [0.376, 0.050, 0.039, 0.022], atol=5e-4), sd
    assert np.allclose(neff, [3.5, 13.6, 26.0, 101.5], atol=0.05), neff

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(FULL_W, 2.45), gridspec_kw={"width_ratios": (1.0, 1.0)})

    # (a) ratio per bandwidth: seeds as dots, mean and SD on top, the exact-field value as a rule
    x = np.arange(len(hs))
    ax.axhline(1.0, color=EXACT, ls="--", lw=0.9, zorder=1)
    ax.text(1.5, 0.985, "exact field: 1", ha="center", va="top", fontsize=6.5, color=EXACT)
    jitter = np.linspace(-0.12, 0.12, 5)
    for xi, h in zip(x, hs):
        ax.scatter(xi + jitter[: len(p7[h]["ratio"])] - 0.16, p7[h]["ratio"], s=9, color=LEARNED,
                   alpha=0.45, lw=0, zorder=2)
    ax.errorbar(x + 0.12, mean, yerr=sd, marker="o", ms=4, ls="none", capsize=2.5, elinewidth=1.0,
                color=LEARNED, mec="white", mew=0.6, zorder=3)
    for j, (xi, n) in enumerate(zip(x, neff)):
        ax.text(xi, 2.12, (rf"$n_{{\rm eff}}={n:.1f}$" if j == 0 else f"{n:.1f}"), ha="center", va="top",
                fontsize=6.5, color=GREY)
    ax.set_xticks(x, [f"{h:g}" for h in hs])
    ax.set_xlim(-0.55, len(hs) - 0.45)
    ax.set_ylim(0.8, 2.15)
    ax.set_xlabel("label bandwidth $h$")
    ax.set_ylabel(r"generated / reference variance")
    ax.legend(handles=[Line2D([], [], marker="o", ls="none", color=LEARNED, alpha=0.45, ms=3.5, mew=0,
                              label="one seed"),
                       Line2D([], [], marker="o", ls="-", color=LEARNED, ms=4, mec="white", mew=0.6,
                              label="mean $\\pm$ SD, 5 seeds")],
              loc="upper right", bbox_to_anchor=(1.0, 0.86), fontsize=6.5, borderaxespad=0.2)
    panel_title(ax, "a", r"Linear-Gaussian, $d=2$: ratio to $\mathrm{tr\,Cov}_h$")

    # (b) CIFAR-10, h = 4: per-condition parity on log axes, one OLS line per retrained draw
    lo, hi = 2e-1, 2e3
    bx.plot([lo, hi], [lo, hi], color=EXACT, ls="--", lw=0.9, zorder=1)
    bx.text(25, 6, "exact field: slope 1", rotation=45, rotation_mode="anchor", ha="left",
            va="bottom", fontsize=6.5, color=EXACT)
    slopes = []
    for j, mk in enumerate(MARKERS):
        path = CIFAR / f"reeval_exp3_cifar_heff_h4_s{j}" / "reeval.json"
        if not path.is_file():
            raise FileNotFoundError(f"missing CIFAR record {path}")
        ref, meas = read_reeval(path)
        ok = (ref > 0) & (meas > 0)
        if (~ok).any():
            print(f"  draw {j}: dropped {int((~ok).sum())} conditions with a non-positive trace")
        lx, ly = np.log10(ref[ok]), np.log10(meas[ok])
        sl, ic = ols(lx, ly)
        slopes.append(sl)
        bx.scatter(ref[ok], meas[ok], s=9, marker=mk, facecolor="none", edgecolor=LEARNED, lw=0.6,
                   alpha=0.75, zorder=3)
        xx = np.array([lx.min(), lx.max()])
        bx.plot(10 ** xx, 10 ** (ic + sl * xx), color=LEARNED, lw=1.0, zorder=4,
                ls=("-", (0, (4, 1.5)), (0, (1, 1)))[j])
    # Table tab:cifar-kernel prints 0.34, 0.32, 0.43 for the three draws.
    assert np.allclose(slopes, [0.3438, 0.3159, 0.4267], atol=5e-4), slopes
    bx.set_xscale("log"); bx.set_yscale("log")
    bx.set_xlim(lo, hi); bx.set_ylim(lo, hi)
    bx.set_aspect("equal", adjustable="box")
    bx.set_xlabel(r"reference $\mathrm{tr\,Cov}_h$")
    bx.set_ylabel(r"generated $\mathrm{tr\,Cov}$")
    bx.legend(handles=[Line2D([], [], marker=mk, ls=ls, color=LEARNED, mfc="none", ms=4, lw=1.0,
                              label=f"draw {j + 1}: slope {sl:.2f}")
                       for j, (mk, ls, sl) in enumerate(zip(MARKERS, ("-", (0, (4, 1.5)), (0, (1, 1))), slopes))],
              loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=6.5, borderaxespad=0.0,
              handlelength=2.4,
              title="three retrained networks,\n48 conditions each", title_fontsize=6.5)
    panel_title(bx, "b", r"CIFAR-10 inpainting, $h=4$")

    for a in (ax, bx):
        style(a)
    fig.tight_layout(w_pad=1.5)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"  slopes at h=4: {[round(s, 4) for s in slopes]}")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
