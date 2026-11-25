"""Regenerate the CIFAR pair image archive, geometry and midpoint figure from the full instance.

    python scripts/make_cifar_composition_figure.py --data cifar2000_seed0.npz
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from make_theory_cifar_composition_figure import IMAGES, main as draw_figure

OUTDIR = Path("paper_theory/figures")

ROOT = Path("results/cifar_composition_exact_20261105")


def img(v):
    return np.clip((v.reshape(3, 32, 32).transpose(1, 2, 0) + 1) / 2, 0, 1)


def write_geometry(X, S):
    # Pair distances against the nearest-neighbour distances of the 2000 images (checked by
    # verify_paper_numbers.py, which cannot read the uncommitted data file).
    X = X.astype(np.float64, copy=False)
    G = X @ X.T
    n2 = np.diag(G)
    D = np.sqrt(np.maximum(n2[:, None] + n2[None] - 2 * G, 0)); np.fill_diagonal(D, np.inf)
    nn = D.min(1)
    info = {"median_nn": float(np.median(nn)), "shown": [p["pair"] for p in sorted(S, key=lambda p: p["mid"]["10.0"])],
            "pairs": [{"pair": p["pair"], "dist": float(D[p["pair"][0], p["pair"][1]]),
                       "mutual_nn": bool(D[p["pair"][0]].argmin() == p["pair"][1]
                                         and D[p["pair"][1]].argmin() == p["pair"][0])} for p in S]}
    (OUTDIR / "fig_cifar_composition.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print("wrote pair geometry")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "cifar2000_seed0.npz")
    parser.add_argument("--geometry-only", action="store_true", help="regenerate the pair distances for the paper")
    args = parser.parse_args()
    X = np.load(args.data)["X"]
    curves = json.loads(Path("results/cifar_composition_replay/summary.json").read_text())["selected"]
    S = [{"pair": [int(i) for i in key.split("/")], "mid": values} for key, values in curves.items()]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    write_geometry(X, S)
    if args.geometry_only:
        return
    ids = sorted({i for row in S for i in row["pair"]})
    images = {str(i): np.rint(255 * img(X[i])).astype(np.uint8) for i in ids}
    np.savez_compressed(IMAGES, **images)
    draw_figure()


if __name__ == "__main__":
    main()
