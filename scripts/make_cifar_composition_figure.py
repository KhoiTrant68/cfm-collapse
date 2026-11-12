"""Figure fig:cifar-composition: exact guided label averaging on CIFAR-10 pairs.

(a) Three of the eight pairs: training images x^i, x^j and the midpoint z = (x^i + x^j)/2, the
    non-training endpoint of the composite (Theorem thm:composition at d = 3072).
(b) Midpoint fraction of 512 shared sources against w/w_c for all eight pairs (thin) and their
    mean (thick), from results/cifar_composition_exact_20261105/summary.json.

    python scripts/make_cifar_composition_figure.py
The data file cifar2000_seed0.npz is the EXP-3 CIFAR-10 instance (not committed; see run.sh).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import FIGDIR, OI, style, use_paper_style

ROOT = Path("results/cifar_composition_exact_20261105")
SHOW = ((1491, 1514), (81, 819), (158, 230))   # the three most distant pairs


def img(v):
    return np.clip((v.reshape(3, 32, 32).transpose(1, 2, 0) + 1) / 2, 0, 1)


def main() -> None:
    use_paper_style()
    X = np.load(ROOT / "cifar2000_seed0.npz")["X"]
    S = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))["pairs"]
    fig = plt.figure(figsize=(9.2, 2.9))
    gs = fig.add_gridspec(len(SHOW), 5, width_ratios=(1, 1, 1, 0.75, 7.2), wspace=0.04, hspace=0.06,
                          left=0.02, right=0.99, bottom=0.17, top=0.9)
    for row, (i, j) in enumerate(SHOW):
        for col, (v, title) in enumerate(((X[i], r"$x^i$"), ((X[i] + X[j]) / 2, r"midpoint $z$"),
                                          (X[j], r"$x^j$"))):
            ax = fig.add_subplot(gs[row, col])
            ax.imshow(img(v), interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_edgecolor(OI["vermillion"] if col == 1 else "0.6"); s.set_linewidth(1.2)
            if row == 0:
                ax.set_title(title, fontsize=9)
    fig.text(0.005, 0.95, "(a)", fontsize=10)
    ax = fig.add_subplot(gs[:, 4])
    ratios = sorted(float(k) for k in S[0]["mid"])
    xs = [0.3 if r == 0 else r for r in ratios]          # w = 0 drawn at the left edge
    for p in S:
        ax.plot(xs, [p["mid"][f"{r:.1f}"] for r in ratios], color=OI["sky"], lw=0.9, alpha=0.8)
    mean = [np.mean([p["mid"][f"{r:.1f}"] for p in S]) for r in ratios]
    ax.plot(xs, mean, color=OI["vermillion"], lw=2, marker="o", ms=3.5, label="mean of 8 pairs")
    ax.plot([], [], color=OI["sky"], lw=0.9, label="single pair")
    ax.axvline(1, color="0.5", ls="--", lw=0.8)
    ax.text(1.04, 0.27, r"$w=w_c$", color="0.4", fontsize=8)
    ax.set_xscale("log"); ax.set_xlim(0.28, 11)
    ax.set_xlabel(r"$w/w_c$ ($w=0$ at the left edge)")
    ax.set_ylabel("midpoint fraction")
    ax.set_title("(b) exact composite, $d=3072$, $N=2000$", fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    style(ax)
    out = FIGDIR / "fig_cifar_composition.pdf"
    fig.savefig(out); print("wrote", out)
    # Pair distances against the nearest-neighbour distances of the 2000 images (checked by
    # verify_paper_numbers.py, which cannot read the uncommitted data file).
    G = X.astype(np.float64) @ X.T.astype(np.float64)
    n2 = np.diag(G)
    D = np.sqrt(np.maximum(n2[:, None] + n2[None] - 2 * G, 0)); np.fill_diagonal(D, np.inf)
    nn = D.min(1)
    info = {"median_nn": float(np.median(nn)), "shown": [list(p) for p in SHOW],
            "pairs": [{"pair": p["pair"], "dist": float(D[p["pair"][0], p["pair"][1]]),
                       "mutual_nn": bool(D[p["pair"][0]].argmin() == p["pair"][1]
                                         and D[p["pair"][1]].argmin() == p["pair"][0])} for p in S]}
    (FIGDIR / "fig_cifar_composition.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps(info))


if __name__ == "__main__":
    main()
