"""Figure fig:swap of paper B: the trained sampler chooses its image early and lands late.

Two hybrids of the deterministic EDM sampler on CIFAR-10, 500 sources per model:
  net->exact: trained denoiser for sigma > s, exact empirical denoiser below s;
  exact->net: exact denoiser for sigma > s, trained denoiser below s.

(a) Image grid, public EDM model (trained on all 50000 CIFAR-10 training images). For a few sources,
    the training image on which net->exact ends when the switch is at s (columns, s decreasing);
    the first column is the exact field from the start, the last one the nearest training image of
    the network's own endpoint. Frames: vermillion = same image as the network's own endpoint,
    blue = same image as the exact field's endpoint. The indices stored in swap_per_sample.npz are
    indices within the training images of the source's class, in torchvision order
    (scripts/n3_swap.py: Exact(X[lab == c])), and torchvision reads data_batch_1..5 in order, so
    the image is X[Y == label][nn] with X, Y read here from the same python batches.
(b) Curves against s: "choice" = fraction of net->exact endpoints whose nearest training image is
    the network's own (=L); "landing" = fraction of exact->net endpoints on a training image
    (1 - off-atom). Public model thick, 1000-image model thin.

Reads results/n3_followup_20261111/{swap_summary.json, swap_public/swap_per_sample.npz}.
Usage: PYTHONPATH=.:scripts python scripts/make_swap_figure.py [--cifar DIR]
Writes paper_mechanism/figures/fig_swap.pdf and fig_swap.json.
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figstyle import COLORS, FULL_W, style, use_paper_style

ROOT = Path("results/n3_followup_20261111")
OUT = Path("paper_mechanism/figures/fig_swap.pdf")
CIFAR_DEFAULT = Path("/mnt/data/khoitm8/datasets/cifar10/cifar-10-batches-py")
GRID_S = (5.0, 2.0, 1.0, 0.5, 0.2)
LEARNED, EXACT = COLORS["learned"], COLORS["exact"]


def load_cifar(d: Path):
    xs, ys = [], []
    for i in range(1, 6):
        with open(d / f"data_batch_{i}", "rb") as f:
            b = pickle.load(f, encoding="bytes")
        xs.append(b[b"data"]); ys += b[b"labels"]
    x = np.concatenate(xs).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    return x, np.asarray(ys)


def pick_sources(z, k: int = 3) -> list[int]:
    """Sources whose exact and learned endpoints differ, and whose net->exact image switches
    from another image to the network's own as s decreases (the generic case); one per class."""
    L, E = z["learned:nn"], z["exact:nn"]
    out, seen = [], set()
    for i in range(len(L)):
        if L[i] == E[i] or z["label"][i] in seen:
            continue
        seq = [z[f"net2exact@{s:g}:nn"][i] for s in GRID_S]
        if seq[0] != L[i] and seq[-1] == L[i] and len(set(seq)) >= 2:
            out.append(i); seen.add(z["label"][i])
        if len(out) == k:
            break
    return out


def frame(ax, color, lw=1.6):
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(color); s.set_linewidth(lw)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cifar", type=Path, default=CIFAR_DEFAULT)
    args = ap.parse_args()
    use_paper_style()
    summ = {r["run"]: r for r in json.loads((ROOT / "swap_summary.json").read_text(encoding="utf-8"))}
    z = np.load(ROOT / "swap_public" / "swap_per_sample.npz")
    X, Y = load_cifar(args.cifar)
    by_class = {c: X[Y == c] for c in np.unique(Y)}
    assert all(z[k].max() < len(by_class[0]) for k in ("learned:nn", "exact:nn"))
    rows = pick_sources(z)

    fig = plt.figure(figsize=(FULL_W, 2.45))
    ncol = len(GRID_S) + 2
    gl = fig.add_gridspec(len(rows), ncol, left=0.045, right=0.50, bottom=0.12, top=0.83,
                          wspace=0.06, hspace=0.06)
    heads = ["exact\nonly"] + [rf"$s={s:g}$" for s in GRID_S] + ["network\nonly"]
    record = {"rows": []}
    for r, i in enumerate(rows):
        L, E = int(z["learned:nn"][i]), int(z["exact:nn"][i])
        idx = [E] + [int(z[f"net2exact@{s:g}:nn"][i]) for s in GRID_S] + [L]
        record["rows"].append({"source": int(i), "class": int(z["label"][i]), "index_in_class": idx})
        cls = int(z["label"][i])
        for c, j in enumerate(idx):
            ax = fig.add_subplot(gl[r, c])
            ax.imshow(by_class[cls][j], interpolation="nearest")
            frame(ax, LEARNED if j == L else (EXACT if j == E else "#bbbbbb"))
            if r == 0:
                ax.set_title(heads[c], fontsize=7, pad=3, linespacing=1.0)
    fig.text(0.045, 0.955, r"$\mathbf{(a)}$  image reached when the exact field takes over at $s$",
             fontsize=8.5, ha="left", va="center")
    fig.text(0.272, 0.07, r"switch later ($s\downarrow$) $\longrightarrow$", fontsize=7,
             ha="center", color="#444444")
    fig.text(0.272, 0.0, "frame: vermillion = the network's own image, blue = the exact field's image",
             fontsize=6.3, ha="center", color="#555555")

    ax = fig.add_axes([0.60, 0.17, 0.38, 0.66])
    for run, lw, alpha, tag in (("swap_public", 2.0, 1.0, "public"), ("swap_sub1000", 1.0, 0.55, r"$N{=}1000$")):
        lv = summ[run]["levels"]
        s = np.array([l["sigma"] for l in lv])
        choice = [l["net2exact"]["nn_eq_learned"] for l in lv]
        land = [1 - l["exact2net"]["off"] for l in lv]
        ax.plot(s, choice, color=LEARNED, lw=lw, alpha=alpha, marker="o", ms=3 if lw > 1 else 2)
        ax.plot(s, land, color=EXACT, lw=lw, alpha=alpha, marker="s", ms=3 if lw > 1 else 2)
        record[run] = {"s": s.tolist(), "choice": choice, "landing": land}
    sp = np.array(record["swap_public"]["s"])
    lo, hi = sp.min() / 1.25, sp.max() * 1.25
    ax.set_xscale("log"); ax.set_xlim(hi, lo); ax.set_ylim(-0.03, 1.22)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"switch noise level $s$   (sampling runs left $\to$ right)")
    ax.set_ylabel("fraction of samples")
    # The two windows, named in a band above the data.
    ax.axvspan(hi, 1.0, color=LEARNED, alpha=0.07, lw=0)
    ax.axvspan(0.2, lo, color=EXACT, alpha=0.07, lw=0)
    ax.text(np.sqrt(hi * 1.0), 1.13, "image chosen", color=LEARNED, fontsize=7.5,
            ha="center", va="center", fontweight="bold")
    ax.text(np.sqrt(0.2 * lo), 1.13, "landed", color=EXACT, fontsize=7.5,
            ha="center", va="center", fontweight="bold")
    # Direct labels, each in empty space next to its curve.
    # (choice: net->exact ends on the network's own image; landing: exact->net ends on a
    # training image; both spelled out in the caption.)
    ax.text(4.3, 0.66, "choice", color=LEARNED, fontsize=7.5, ha="left", va="center",
            fontweight="bold")
    ax.text(0.17, 0.30, "landing", color=EXACT, fontsize=7.5, ha="left", va="center",
            fontweight="bold")
    ax.set_title(r"$\mathbf{(b)}$  chosen early, landed late", loc="left")
    style(ax)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    OUT.with_suffix(".json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print("wrote", OUT, "rows", rows)


if __name__ == "__main__":
    main()
