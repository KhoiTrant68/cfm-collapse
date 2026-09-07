"""The distance to the true posterior, with the two scales that make it readable.

The old figure plotted MMD against h next to a line at 0 and Sinkhorn against h next
to its own minimum. Neither comparison means anything: 0 is not reachable by any
finite sample, and a curve's own minimum is not a reference. A reader could see that
the curves fall and stop, and had no way to judge whether 0.012 at h=0.5 is close or
far. Two computed references fix that, and both come from ground truth alone, with no
trained model in them (scripts/analyze_posterior_reference_scales.py):

  the sampling floor    two independent M-sample draws from the SAME true posterior.
                        What a method that had exactly recovered p(.|y) would still
                        measure at this sample size. This is the bottom of the axis.

  the atomic prediction the true posterior against sum_i p_i^(h) delta_{x^i}, the law
                        Theorem 10 says the trained model converges to. Not an
                        estimator artefact -- it is where the theory puts the model.

Three panels:

  (a) MMD on a log axis, all three levels. The measured curve tracks the atomic
      prediction down, and the atomic prediction levels off more than an order of
      magnitude above the sampling floor. That gap is Proposition 14 and no bandwidth
      closes it.

  (b) the same in W_2 units -- sqrt of the entropic OT divergence, which is a length
      in the data's own units -- against the posterior's own width sqrt(tr Sigma_post).
      "0.33 units from a posterior 1.00 units wide" is a statement a reader can hold;
      an MMD of 0.012 is not.

  (c) why the floor is there: n_eff, the number of training atoms the mixture
      actually uses. Even at h=0.5 it is 66 of 200, so the generated law is a finite
      mixture of point masses whatever the variance says.

    uv run python -m scripts.make_posterior_distance_figure

Reads:  results/exp1/_theory/raw/posterior_{distance_exp1,reference_scales}.csv
Writes: paper/figures/fig_posterior_distance.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW = Path("results/exp1/_theory/raw")
OUT = Path("paper/figures/fig_posterior_distance.png")
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
TRACE_POST = 1.00405   # tr Sigma_post at the EXP-1 configuration


def main() -> None:
    m = pd.read_csv(RAW / "posterior_distance_exp1.csv").sort_values("h")
    r = pd.read_csv(RAW / "posterior_reference_scales.csv").sort_values("h")
    assert np.allclose(m["h"].values, r["h"].values), "the two sweeps must align"
    x = np.arange(len(m))
    labels = [f"{h:g}" for h in m["h"]]

    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.5))

    # -------------------------------------------------------------- (a) MMD
    ax = axes[0]
    floor = float(r["mmd_floor"].mean())
    ax.axhspan(floor * 0.55, floor * 1.8, color=OI["green"], alpha=0.16, lw=0)
    ax.axhline(floor, color=OI["green"], ls="-", lw=1.6,
               label=f"sampling floor  {floor:.5f}\n(exact recovery, $M{=}1000$)")
    ax.plot(x, r["mmd_atomic"], "s--", color=OI["orange"], lw=1.8, ms=7,
            label=r"atomic prediction $\sum_i p_i^{(h)}\delta_{x^i}$")
    ax.errorbar(x, m["mmd_to_post"], yerr=m["mmd_std"], fmt="o-", color=OI["blue"],
                lw=2.0, ms=7, capsize=3, label="trained model, measured")
    ax.set_yscale("log")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel(r"label-noise bandwidth $h$")
    ax.set_ylabel(r"MMD to $\mathcal{N}(\mu_{\mathrm{post}},\Sigma_{\mathrm{post}})$")
    ax.set_title("(a) the measured curve falls onto the atomic prediction,\n"
                 "which stops far above the sampling floor", fontsize=10)
    gap = float(r["mmd_atomic"].iloc[-1] / floor)
    ax.annotate("", xy=(len(x) - 1, floor), xytext=(len(x) - 1, r["mmd_atomic"].iloc[-1]),
                arrowprops=dict(arrowstyle="<->", lw=1.6, color=OI["vermillion"]))
    ax.annotate(f"${gap:.0f}\\times$", xy=(len(x) - 1, np.sqrt(floor * r["mmd_atomic"].iloc[-1])),
                xytext=(-8, 0), textcoords="offset points", ha="right", va="center",
                fontsize=10, color=OI["vermillion"])
    ax.grid(alpha=0.3); ax.legend(fontsize=7.5, loc="lower left")

    # ----------------------------------------- (b) the same as a length, in W_2
    ax = axes[1]
    w_meas = np.sqrt(m["sinkhorn_to_post"].clip(lower=0))
    w_atom = np.sqrt(r["sinkhorn_atomic"].clip(lower=0))
    w_floor = float(np.sqrt(max(r["sinkhorn_floor"].mean(), 0.0)))
    post_sd = float(np.sqrt(TRACE_POST))
    ax.axhline(post_sd, color=OI["black"], ls=":", lw=1.6)
    ax.text(len(x) - 1, post_sd * 1.06,
            r"the posterior's own width $\sqrt{\mathrm{tr}\,\Sigma_{\mathrm{post}}}"
            f"={post_sd:.2f}$", fontsize=8.5, ha="right", va="bottom")
    ax.axhline(w_floor, color=OI["green"], ls="-", lw=1.6,
               label=f"sampling floor  {w_floor:.3f}")
    ax.plot(x, w_atom, "s--", color=OI["orange"], lw=1.8, ms=7,
            label="atomic prediction")
    ax.plot(x, w_meas, "o-", color=OI["blue"], lw=2.0, ms=7,
            label="trained model, measured")
    ax.set_yscale("log")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel(r"label-noise bandwidth $h$")
    ax.set_ylabel(r"$\sqrt{S_\varepsilon}$ to the posterior   (data units)")
    ax.set_title("(b) as a length: the best bandwidth still sits\n"
                 f"{w_atom.iloc[-1] / post_sd * 100:.0f}\\% of a posterior width away",
                 fontsize=10)
    ax.grid(alpha=0.3); ax.legend(fontsize=7.5, loc="lower left")

    # ------------------------------------------------------- (c) why: the support
    ax = axes[2]
    N = 200
    ax.bar(x, r["n_eff"], color=OI["purple"], alpha=0.85, width=0.6)
    for xi, v in zip(x, r["n_eff"]):
        ax.text(xi, v + 2.5, f"{v:.1f}", ha="center", fontsize=9)
    ax.axhline(N, color=OI["black"], ls=":", lw=1.6)
    ax.text(0.02, N * 0.955, f"all $N={N}$ training points", fontsize=8.5,
            transform=ax.get_yaxis_transform(), va="top")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, N * 1.12)
    ax.set_xlabel(r"label-noise bandwidth $h$")
    ax.set_ylabel(r"$n_{\mathrm{eff}}=1/\sum_j (p_j^{(h)})^2$")
    ax.set_title("(c) why the floor is there: the law is a mixture\n"
                 "of this many point masses, at every $h$", fontsize=10)
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle("Raising $h$ restores variance and moves the law towards the "
                 "posterior, but the law it moves towards is atomic",
                 fontsize=12.5, y=1.01)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {OUT}")
    print(f"  MMD: measured {m['mmd_to_post'].iloc[-1]:.4f}, atomic prediction "
          f"{r['mmd_atomic'].iloc[-1]:.4f}, sampling floor {floor:.5f} "
          f"({gap:.0f}x above it)")
    print(f"  W_2: measured {w_meas.iloc[-1]:.3f}, atomic {w_atom.iloc[-1]:.3f}, "
          f"floor {w_floor:.3f}, posterior width {post_sd:.3f}")


if __name__ == "__main__":
    main()
