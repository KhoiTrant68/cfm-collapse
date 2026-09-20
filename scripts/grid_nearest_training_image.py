"""Are the completions in a saved sample grid on a CIFAR-10 training image?

The DDPM checkpoints are not kept, so the distance of individual samples to the training
set cannot be measured from the models. The saved grids are still enough: each 32x32
cell was drawn with ``imshow`` at about 3.4 pixels per source pixel, so sampling the cell
at the centre of every source pixel gives the sample back at its 8-bit values. Each recovered
cell is compared with all 50000 CIFAR-10 training images (the runs train on a random 2000
of them).

The ``true`` column of every grid is a training image by construction, so it calibrates
the recovery: its nearest image must be at distance ~0, and the crop that achieves this is
the crop used for the completions.

"On an atom" is the criterion of the paper (Yoon et al. 2023, as used by Buchanan et al.
2025): the distance to the nearest training image is below 1/3 of the distance to the second
nearest. The second nearest is taken over all 50000 images, not over the 2000 the run trained
on, so its distance is smaller than the run's and the ratio larger: the count of on-atom
samples here can only be an undercount. An absolute threshold does not work: the h = 0
completions, which are copies, sit at RMSE 0.006-0.015 from an image, but a trained network
at h > 0 reproduces an atom less exactly (0.017 and above).

    uv run --no-project --with numpy --with matplotlib python -m scripts.grid_nearest_training_image
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np

from scripts.make_image_bandwidth_figure import cells

BASE = Path("results/exp3")
OUT = BASE / "_grid_nn"
RATIO = 1.0 / 3.0           # on an atom: d1 / d2 below this (squared: 1/9)


def cifar_train(root: Path = Path("data/cifar-10-batches-py")) -> np.ndarray:
    xs = []
    for i in range(1, 6):
        with open(root / f"data_batch_{i}", "rb") as f:
            xs.append(pickle.load(f, encoding="bytes")[b"data"])
    x = np.concatenate(xs).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    return x                                                  # (50000, 32, 32, 3) uint8


def recover(cell: np.ndarray, inset: int) -> np.ndarray:
    """Sample a rendered cell at the centre of each of its 32x32 source pixels."""
    h, w = cell.shape[:2]
    ys = (inset + (np.arange(32) + 0.5) * (h - 2 * inset) / 32).astype(int)
    xs = (inset + (np.arange(32) + 0.5) * (w - 2 * inset) / 32).astype(int)
    return np.rint(cell[np.ix_(ys, xs)] * 255.0).astype(np.uint8)


def nearest(train: np.ndarray, img: np.ndarray) -> tuple[float, float, int]:
    """RMSE (in [0,1]) to the nearest and second-nearest training image, and the index."""
    flat = img.reshape(-1).astype(np.float32)
    m = np.concatenate([
        ((train[s:s + 5000].reshape(-1, 3072).astype(np.float32) - flat) ** 2).mean(axis=1)
        for s in range(0, len(train), 5000)])
    i = np.argpartition(m, 1)[:2]
    i = i[np.argsort(m[i])]
    return float(np.sqrt(m[i[0]])) / 255.0, float(np.sqrt(m[i[1]])) / 255.0, int(i[0])


def calibrate(train: np.ndarray, sheets: list) -> int:
    """Crop inset at which the ``true`` column is recovered best."""
    scores = {}
    for inset in range(0, 6):
        scores[inset] = float(np.mean([nearest(train, recover(row[7], inset))[0]
                                       for sheet in sheets for row in sheet]))
    inset = min(scores, key=scores.get)
    print("  crop calibration on the `true` column (mean RMSE to nearest image):",
          {k: round(v, 4) for k, v in scores.items()}, "->", inset)
    return inset


def run(name: str, it: int, train, inset: int) -> dict:
    sheet = cells(BASE / name / "figures" / f"grid_it{it}.png")
    rows = []
    for row in sheet:
        d_true = nearest(train, recover(row[7], inset))[0]
        comp = [nearest(train, recover(row[c], inset)) for c in range(1, 7)]
        rows.append({"true_rmse": d_true, "d1": [c[0] for c in comp], "d2": [c[1] for c in comp],
                     "index": [c[2] for c in comp]})
    ratio = np.array([a / b for r in rows for a, b in zip(r["d1"], r["d2"])])
    return {"run": name, "iter": it, "rows": rows, "n": int(ratio.size),
            "on_atom": int((ratio < RATIO).sum()), "median_ratio": float(np.median(ratio))}


def main() -> None:
    train = cifar_train()
    probe = [cells(BASE / "exp3_cifar_ddpm_h0" / "figures" / "grid_it60000.png"),
             cells(BASE / "exp3_cifar_ddpm_h0_seed1" / "figures" / "grid_it60000.png")]
    inset = calibrate(train, probe)
    runs = [(f"exp3_cifar_ddpm_h{h}" + (f"_seed{s}" if s else ""), 60000)
            for s in (0, 1, 2) for h in (0, 4, 5, 6)]
    runs += [("exp3_cifar_class_h0", 60000), ("exp3_cifar_class_h0p4", 60000)]
    results = []
    for name, it in runs:
        res = run(name, it, train, inset)
        tr = max(r["true_rmse"] for r in res["rows"])
        print(f"{name:28s} on an atom (d1/d2 < 1/3): {res['on_atom']:2d}/{res['n']}   "
              f"median d1/d2 {res['median_ratio']:.2f}   (true column max RMSE {tr:.4f})")
        assert tr < 0.012, f"{name}: the true column is not recovered ({tr:.4f})"
        results.append(res)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "grid_nn.json").write_text(json.dumps({"ratio": RATIO, "inset": inset,
                                                  "results": results}, indent=1))
    print(f"wrote {OUT / 'grid_nn.json'}")


if __name__ == "__main__":
    main()
