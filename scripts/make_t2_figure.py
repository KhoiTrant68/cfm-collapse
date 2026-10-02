"""Figure and pooled summary for T2 (spectral-bias model of h_eff).

(a) s(t) = h_eff at h = 0 against kernel time for the three kernels (seed 0, ell = sd(y)),
    with the predicted slopes -1/beta (Laplace beta = 2, Matern-3/2 beta = 4).
(b) h_eff(t) for each training bandwidth h under the Laplace kernel (seed 0): it falls and
    converges to h (dashed), as a strictly positive-definite kernel must.

Reads:  results/theory/t2_resolution.json
Writes: paper/figures/fig_t2_resolution.png, results/theory/t2_summary.json
Usage:  PYTHONPATH=. uv run python scripts/make_t2_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, H_COLORS, OI, save, style, use_paper_style

SRC = Path("results/theory/t2_resolution.json")
SUM = Path("results/theory/t2_summary.json")
KC = {"gaussian": OI["sky"], "matern32": OI["orange"], "laplace": OI["vermillion"]}
KL = {"gaussian": "Gaussian (exponential spectrum)", "matern32": "Matérn-3/2 ($\\beta=4$)",
      "laplace": "Laplace ($\\beta=2$)"}


def main() -> None:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    runs = d["runs"]
    summ = {}
    for kind in ("gaussian", "matern32", "laplace"):
        rs = [r for r in runs.values() if r["kind"] == kind]
        sl = [r["s_slope"] for r in rs if np.isfinite(r["s_slope"])]
        conv = [all(abs(np.log(v / max(float(h), 3e-3))) < 0.25
                    for h, v in r["final_h_eff"].items() if float(h) > 0) for r in rs]
        summ[kind] = {"mean_s_slope": float(np.mean(sl)) if sl else None, "n_slope": len(sl),
                      "median_p": float(np.median([r["p"] for r in rs])),
                      "median_r2": float(np.median([r["median_r2"] for r in rs])),
                      "median_abs_log_mean_vs_var": float(np.median(
                          [r["median_abs_log_mean_vs_var"] for r in rs])),
                      "converged_to_h": f"{sum(conv)}/{len(conv)}"}
    SUM.write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps(summ, indent=1))

    use_paper_style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.8))
    for kind in ("gaussian", "matern32", "laplace"):
        r = runs[f"{kind}_ell1.0_seed0"]
        rows = [x for x in r["rows"] if x["h"] == 0]
        a1.plot([x["t"] for x in rows], [x["h_eff"] for x in rows], color=KC[kind], lw=2.0,
                label=KL[kind])
    t = np.array([1e2, 1e5])
    for beta, kind in ((2, "laplace"), (4, "matern32")):
        a1.plot(t, 0.6 * (t / t[0]) ** (-1 / beta), color=KC[kind], ls=":", lw=1.2)
    a1.set_xscale("log"); a1.set_yscale("log")
    a1.set_xlabel("kernel time $t$"); a1.set_ylabel("$s(t)=h_{\\mathrm{eff}}$ at $h=0$")
    a1.set_title("(a) resolution shrinks as $t^{-1/\\beta}$", loc="left")
    a1.legend(loc="lower left", fontsize=8)
    style(a1)

    r = runs["laplace_ell1.0_seed0"]
    for h in (0.0, 0.01, 0.05, 0.1):
        rows = [x for x in r["rows"] if x["h"] == h]
        col = H_COLORS.get(h, OI["purple"])
        a2.plot([x["t"] for x in rows], [x["h_eff"] for x in rows], color=col, lw=2.0,
                label=f"$h={h:g}$")
        if h > 0:
            a2.axhline(h, color=col, ls="--", lw=0.9)
    a2.set_xscale("log"); a2.set_yscale("log")
    a2.set_xlabel("kernel time $t$"); a2.set_ylabel("$h_{\\mathrm{eff}}$")
    a2.set_title("(b) $h_{\\mathrm{eff}}$ falls to $h$ (Laplace kernel)", loc="left")
    a2.legend(loc="upper right", fontsize=8)
    style(a2)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_t2_resolution.png")


if __name__ == "__main__":
    main()
