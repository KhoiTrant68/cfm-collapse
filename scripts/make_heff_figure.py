"""Figure: trained conditional flows have an effective bandwidth that training shrinks.

(a) h_eff against training iteration on the linear-Gaussian problem, one colour per
    training bandwidth h: the line is the geometric mean over three seeds, the band
    their range, and the dashed rule the training bandwidth h that h_eff should
    approach. Checkpoints before 3000 iterations are omitted: the model has not
    learned the conditional structure yet and no bandwidth fits (R^2 < 0).
(b) The bandwidth fitted to the per-condition variances against the one implied by
    the per-condition means alone, with 95% bootstrap intervals over conditions. The
    two are estimated from disjoint statistics, so agreement on the identity line is
    an out-of-sample check. Open markers are h = 0.5, where the reference barely
    varies across conditions and h_eff is poorly identified.

Reads:  results/exp1/_heff/heff_synthetic.json
Writes: paper/figures/fig_heff_synthetic.png

Usage:
    PYTHONPATH=. uv run python scripts/make_heff_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, H_COLORS, save, style, use_paper_style

SRC = Path("results/exp1/_heff/heff_synthetic.json")
MIN_ITER = 3000
HS = (0.0, 0.01, 0.05, 0.1, 0.5)


def main() -> None:
    rows = [r for r in json.loads(SRC.read_text(encoding="utf-8")) if r["iter"] >= MIN_ITER]
    use_paper_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2),
                                   gridspec_kw={"width_ratios": [1.35, 1]})

    # (a) h_eff over training
    for h in HS:
        rs = [r for r in rows if r["h"] == h]
        its = sorted({r["iter"] for r in rs})
        vals = np.array([[r["h_eff"] for r in rs if r["iter"] == it] for it in its])
        gm = np.exp(np.log(vals).mean(1))
        c = H_COLORS[h]
        ax1.fill_between(its, vals.min(1), vals.max(1), color=c, alpha=0.15, lw=0)
        ax1.plot(its, gm, color=c, lw=2.0, marker="o", ms=4.5,
                 markeredgecolor="white", markeredgewidth=0.8, zorder=3)
        if h > 0:
            ax1.axhline(h, color=c, ls="--", lw=1.0, alpha=0.9, zorder=1)
        ax1.annotate(f"$h={h:g}$", (its[-1], gm[-1]), xytext=(9, 0),
                     textcoords="offset points", va="center", fontsize=9,
                     color="#222222", zorder=5,
                     bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlim(2.4e3, 4.5e5)
    ax1.set_xlabel("training iteration")
    ax1.set_ylabel(r"effective bandwidth $h_{\mathrm{eff}}$")
    ax1.set_title(r"(a) $h_{\mathrm{eff}}$ falls with training and stops at $h$",
                  loc="left")
    style(ax1)

    # (b) variance-fitted vs mean-implied bandwidth
    lo, hi = 5e-3, 1.5
    ax2.plot([lo, hi], [lo, hi], color=COLORS["theory"], ls="--", lw=1.2, zorder=1)
    for h in HS:
        rs = [r for r in rows if r["h"] == h]
        x = np.array([r["h_from_means"] for r in rs])
        y = np.array([r["h_eff"] for r in rs])
        xe = np.array([[r["h_from_means"] - r["h_means_ci"][0],
                        r["h_means_ci"][1] - r["h_from_means"]] for r in rs]).T
        ye = np.array([[r["h_eff"] - r["h_eff_ci"][0],
                        r["h_eff_ci"][1] - r["h_eff"]] for r in rs]).T
        c = H_COLORS[h]
        ax2.errorbar(x, y, xerr=np.clip(xe, 0, None), yerr=np.clip(ye, 0, None),
                     fmt="none", ecolor=c, elinewidth=0.8, alpha=0.6, zorder=2)
        open_marker = h == 0.5
        ax2.scatter(x, y, s=26, zorder=3, linewidths=1.2,
                    facecolors="white" if open_marker else c,
                    edgecolors=c if open_marker else "white",
                    label=f"$h={h:g}$" + (" (low range)" if open_marker else ""))
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlim(lo, hi)
    ax2.set_ylim(lo, hi)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xlabel("bandwidth implied by the means")
    ax2.set_ylabel(r"$h_{\mathrm{eff}}$ fitted to the variances")
    ax2.set_title("(b) two disjoint statistics, one bandwidth", loc="left")
    ax2.legend(loc="upper left", fontsize=8.5, handletextpad=0.3, borderaxespad=0.2)
    style(ax2)

    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_heff_synthetic.png")


if __name__ == "__main__":
    main()
