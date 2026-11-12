"""List the mutual-nearest-neighbour pairs of the EXP-3 CIFAR-10 images and draw a random subset.

For every pair (i, j) of mutual nearest neighbours this prints the candidate margin
min_{k != i,j} |x^k - z|^2 / r^2, z = (x^i + x^j)/2, r = |x^i - x^j|/2, which Theorem spectral(c)
needs to exceed 1. The eight pairs of the main composition run are the eight largest margins; the
random subset is drawn uniformly from the remaining pairs with a fixed seed, so that the
composition can be checked on pairs that were not selected for their margin.

    python -m scripts.cifar_mutual_pairs --data results/cifar_composition_exact_20261105/cifar2000_seed0.npz \
        --subset 12 --seed 20261108 --out results/cifar_composition_random_20261108/pairs.json
"""
import argparse, json, pathlib
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--subset", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261108)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    X = np.load(a.data)["X"].astype(np.float64)
    n2 = (X ** 2).sum(1)
    D2 = n2[:, None] + n2[None] - 2 * X @ X.T
    np.fill_diagonal(D2, np.inf)
    nn = D2.argmin(1)
    pairs = sorted({(min(i, int(nn[i])), max(i, int(nn[i]))) for i in range(len(X)) if nn[nn[i]] == i})
    rows = []
    for i, j in pairs:
        z = (X[i] + X[j]) / 2
        r2 = ((X[i] - X[j]) ** 2).sum() / 4
        d = ((X - z) ** 2).sum(1); d[[i, j]] = np.inf
        rows.append({"pair": [i, j], "margin_sq": float(d.min() / r2), "dist": float(2 * np.sqrt(r2))})
    rows.sort(key=lambda p: -p["margin_sq"])
    top, rest = rows[:a.top], rows[a.top:]
    rng = np.random.default_rng(a.seed)
    pick = sorted(rng.choice(len(rest), size=a.subset, replace=False).tolist())
    out = {"n_pairs": len(rows), "min_margin_sq": min(p["margin_sq"] for p in rows), "top": top,
           "random": [rest[k] for k in pick], "seed": a.seed, "all": rows}
    p = pathlib.Path(a.out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(len(rows), "mutual pairs; min margin", round(out["min_margin_sq"], 3))
    print("top:", [tuple(p["pair"]) for p in top])
    print("random:", [(tuple(p["pair"]), round(p["margin_sq"], 2)) for p in out["random"]])


if __name__ == "__main__":
    main()
