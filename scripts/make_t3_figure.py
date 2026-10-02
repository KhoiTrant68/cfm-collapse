"""Figure for T3: the calibration window predicted from the effective bandwidth.

(a) Coverage of the nominal 90% region against bandwidth on the linear-Gaussian problem
    (seed 0): the infinite-data smoothed posterior (Theorem 2c, over-coverage for h > 0), the
    local model with the finite effective sample (Theorem 2d, collapse branch at small h), and
    the measured coverage of every trained checkpoint placed at its h_eff (all seeds).
(b) Coverage predicted by the local model at h_eff against the measured coverage, with
    the exact coverage of the finite reference law at h_eff for comparison.

Reads:  results/theory/t3_coverage.json
Writes: paper/figures/fig_t3_coverage.png
Usage:  PYTHONPATH=. uv run python scripts/make_t3_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from scripts.figstyle import COLORS, H_COLORS, OI, save, style, use_paper_style
from scripts.theory_t3_coverage import (N_TEST, coverage_local_model, coverage_theory,
                                        problem)

SRC = Path("results/theory/t3_coverage.json")


def main() -> None:
    torch.set_default_dtype(torch.float64)
    d = json.loads(SRC.read_text(encoding="utf-8"))
    rows = d["t3d"]["rows"]
    pp, Xs, Ys = problem(0)
    g_t = torch.Generator().manual_seed(31337)
    Xt = pp.sample_prior(N_TEST, generator=g_t); Yt = pp.forward(Xt, generator=g_t)
    hs = np.exp(np.linspace(np.log(0.004), np.log(1.5), 30))
    inf_c, loc_c = [], []
    for h in hs:
        W = torch.softmax(-torch.cdist(Yt, Ys) ** 2 / (2 * h * h), dim=1)
        inf_c.append(coverage_theory(pp, float(h), float("inf"), 0.9))
        loc_c.append(coverage_local_model(pp, float(h), W[:25], 0.9))

    use_paper_style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.0), gridspec_kw={"width_ratios": [1.3, 1]})
    a1.axhline(0.9, color=COLORS["theory"], ls=":", lw=1.0)
    a1.plot(hs, inf_c, color=OI["sky"], lw=2.0, label="smoothed posterior, $N\\to\\infty$ (Thm. 2c)")
    a1.plot(hs, loc_c, color=COLORS["theory"], lw=2.0, label="finite effective sample (Thm. 2d)")
    for h in sorted({r["h"] for r in rows}):
        rs = [r for r in rows if r["h"] == h]
        a1.scatter([r["h_eff"] for r in rs], [r["measured_cov_90"] for r in rs], s=26,
                   color=H_COLORS.get(h, OI["purple"]), edgecolors="white", linewidths=0.7,
                   zorder=3, label=f"trained, $h={h:g}$")
    a1.set_xscale("log")
    a1.set_xlabel("bandwidth (trained models: $h_{\\mathrm{eff}}$)")
    a1.set_ylabel("held-out coverage of the 90% region")
    a1.set_ylim(0, 1.02)
    a1.set_title("(a) one bandwidth sets the calibration", loc="left")
    a1.legend(loc="lower right", fontsize=7.6, ncol=1, handletextpad=0.3)
    style(a1)

    a2.plot([0, 1], [0, 1], color=COLORS["theory"], ls="--", lw=1.0)
    a2.scatter([r["local_cov_90"] for r in rows], [r["measured_cov_90"] for r in rows], s=24,
               color=OI["vermillion"], edgecolors="white", linewidths=0.7, zorder=3,
               label="theory at $h_{\\mathrm{eff}}$ (Thm. 2d)")
    a2.scatter([r["ref_cov_90"] for r in rows], [r["measured_cov_90"] for r in rows], s=22,
               facecolors="none", edgecolors=OI["blue"], linewidths=1.0, zorder=2,
               label="reference law at $h_{\\mathrm{eff}}$")
    s = d["t3d"]["summary"]
    a2.text(0.97, 0.05, f"theory: $R^2$ = {s['local_model_vs_measured_90']['r2']:.2f}\n"
                        f"reference: $R^2$ = {s['reference_vs_measured_90']['r2']:.2f}",
            transform=a2.transAxes, ha="right", va="bottom", fontsize=8.5)
    a2.set_xlim(0, 1.02); a2.set_ylim(0, 1.02)
    a2.set_aspect("equal", adjustable="box")
    a2.set_xlabel("predicted coverage")
    a2.set_ylabel("measured coverage")
    a2.set_title("(b) predicted from $h_{\\mathrm{eff}}$ alone", loc="left")
    a2.legend(loc="upper left", fontsize=8)
    style(a2)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_t3_coverage.png")


if __name__ == "__main__":
    main()
