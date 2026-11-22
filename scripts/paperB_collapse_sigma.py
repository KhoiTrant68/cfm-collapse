"""E7: at which noise level does the exact posterior commit to one training image?

    python -m scripts.paperB_collapse_sigma --cifar-tar <cifar-10-python.tar.gz> --out <dir>

For the class-conditional exact field of EDM's CIFAR-10 models, the posterior over the training
images of a class at a noisy point x is w_j proportional to exp(-|x - y_j|^2 / (2 sigma^2)). This script measures,
on the training subsets actually used (500 images seed 0 and 1, 1000 seed 0, 2000 seed 0, and all
50000), how the posterior concentrates as sigma decreases:

  * fresh points: x = t + sigma * eps with t a CIFAR-10 TEST image of the class (a stand-in for a
    sample of the data distribution), eps fixed per point; we record the largest posterior weight
    max_j w_j, its quantiles over points, and the fraction of points with max_j w_j >= 0.5 and >= 0.9;
  * training points: x = y_i + sigma * eps; we record the weight on y_i itself (retrieval).

This is the collapse of Biroli et al. (2024) measured directly on the data, and it is compared in
the paper with the noise level at which the trained networks select their image (denoiser swap).
The subsets are regenerated exactly as scripts/make_edm_cifar_subset.py does (numpy
default_rng(seed), rng.choice per class without replacement, torchvision order = data_batch_1..5)
and checked against the nearest-training-image vectors saved in results/n3_strips_20261118.

Numpy only; reads the CIFAR-10 python tarball directly.
"""
from __future__ import annotations

import argparse
import json
import pickle
import tarfile
import time
from pathlib import Path

import numpy as np

SUBSETS = [(500, 0), (500, 1), (1000, 0), (2000, 0), (50000, None)]


def load_cifar(tar_path):
    xs, ys = [], []
    with tarfile.open(tar_path, "r:gz") as tf:
        def read(name):
            d = pickle.load(tf.extractfile(f"cifar-10-batches-py/{name}"), encoding="bytes")
            return np.asarray(d[b"data"], np.uint8), np.asarray(d[b"labels"], np.int64)
        for k in range(1, 6):
            x, y = read(f"data_batch_{k}"); xs.append(x); ys.append(y)
        xt, yt = read("test_batch")
    X = np.concatenate(xs).astype(np.float64) / 127.5 - 1.0       # CHW-flattened, as in EDM / torchvision
    return X, np.concatenate(ys), xt.astype(np.float64) / 127.5 - 1.0, yt


def subset_indices(y, n, seed):
    if seed is None:
        return np.arange(len(y))
    rng = np.random.default_rng(seed)
    return np.sort(np.concatenate([rng.choice(np.flatnonzero(y == c), n // 10, replace=False) for c in range(10)]))


def verify_against_strips(X, idx, strips_path):
    """Every saved nearest-training-image vector must be an image of the regenerated subset."""
    z = np.load(strips_path)
    out = []
    S = X[idx]
    for v in z["y1"].astype(np.float64):
        d = np.abs(S - v[None]).max(1)
        out.append(float(d.min()))
    return out                                       # float16 storage: matches have max error <= ~2e-3


def softmax_rows(L):
    L = L - L.max(1, keepdims=True)
    W = np.exp(L)
    return W / W.sum(1, keepdims=True)


def curves(Y, T, eps, sigmas, self_index=None):
    """Posterior statistics at x = T + sigma * eps against the atoms Y (rows)."""
    G = (T ** 2).sum(1)[:, None] - 2 * T @ Y.T + (Y ** 2).sum(1)[None]          # |t - y_j|^2
    H = (eps * T).sum(1)[:, None] - eps @ Y.T                                     # <eps, t - y_j>
    rows = []
    for s in sigmas:
        W = softmax_rows(-G / (2 * s * s) - H / s)          # the row constant -|eps|^2/2 cancels
        mx = W.max(1)
        ent = -(W * np.log(np.clip(W, 1e-300, None))).sum(1)
        r = {"sigma": float(s), "maxw_q10": float(np.quantile(mx, 0.1)), "maxw_median": float(np.median(mx)),
             "maxw_q90": float(np.quantile(mx, 0.9)), "frac_maxw_ge_0.5": float((mx >= 0.5).mean()),
             "frac_maxw_ge_0.9": float((mx >= 0.9).mean()), "entropy_median": float(np.median(ent))}
        if self_index is not None:
            own = W[np.arange(len(T)), self_index]
            r.update({"own_median": float(np.median(own)), "frac_own_ge_0.5": float((own >= 0.5).mean())})
        rows.append(r)
    return rows


def crossing(rows, key, level):
    """Largest sigma at which rows[key] >= level (rows ordered by decreasing sigma), interpolated in log sigma."""
    s = np.array([r["sigma"] for r in rows]); v = np.array([r[key] for r in rows])
    order = np.argsort(-s); s, v = s[order], v[order]
    above = np.flatnonzero(v >= level)
    if not len(above):
        return None
    i = above[0]
    if i == 0:
        return float(s[0])
    s0, s1, v0, v1 = s[i - 1], s[i], v[i - 1], v[i]
    f = (level - v0) / (v1 - v0) if v1 != v0 else 1.0
    return float(np.exp(np.log(s0) + f * (np.log(s1) - np.log(s0))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cifar-tar", required=True)
    ap.add_argument("--strips", default="results/n3_strips_20261118")
    ap.add_argument("--out", required=True)
    ap.add_argument("--train-points", type=int, default=200, help="training points per class for retrieval")
    a = ap.parse_args()
    t0 = time.time()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    X, y, Xt, yt = load_cifar(a.cifar_tar)
    sigmas = np.geomspace(80, 0.002, 81)
    edm18 = (80 ** (1 / 7) + np.arange(18) / 17 * (0.002 ** (1 / 7) - 80 ** (1 / 7))) ** 7
    res = {"script": "scripts/paperB_collapse_sigma.py", "sigmas": sigmas.tolist(), "edm18": edm18.tolist(), "subsets": {}}

    checks = {}
    idx500 = subset_indices(y, 500, 0)
    checks["sub500_s0_vs_strips_maxerr"] = verify_against_strips(X, idx500, Path(a.strips) / "sub500.npz")
    checks["public_vs_strips_maxerr"] = verify_against_strips(X, np.arange(len(y)), Path(a.strips) / "public.npz")
    res["checks"] = {k: {"max_of_min_errors": max(v), "n": len(v)} for k, v in checks.items()}
    print("checks", res["checks"], flush=True)

    rng = np.random.default_rng(20261121)
    eps_test = rng.normal(size=Xt.shape)
    for n, seed in SUBSETS:
        name = f"sub{n}_s{seed}" if seed is not None else "full50k"
        idx = subset_indices(y, n, seed)
        Xs, ys = X[idx], y[idx]
        fresh, train, nn = [], [], []
        for c in range(10):
            Y = Xs[ys == c]
            T = Xt[yt == c]; E = eps_test[yt == c]
            fresh.append(curves(Y, T, E, sigmas))
            k = min(a.train_points, len(Y))
            sel = rng.choice(len(Y), k, replace=False)
            train.append(curves(Y, Y[sel], rng.normal(size=(k, Y.shape[1])), sigmas, self_index=sel))
            # nearest-neighbour distances: test -> train, and train -> other train
            Gt = (T ** 2).sum(1)[:, None] - 2 * T @ Y.T + (Y ** 2).sum(1)[None]
            Gy = (Y ** 2).sum(1)[:, None] - 2 * Y @ Y.T + (Y ** 2).sum(1)[None]
            np.fill_diagonal(Gy, np.inf)
            nn.append((np.sqrt(np.clip(Gt.min(1), 0, None)), np.sqrt(np.clip(Gy.min(1), 0, None))))
        def pool(cls_rows):
            keys = [k for k in cls_rows[0][0] if k != "sigma"]
            return [{"sigma": cls_rows[0][i]["sigma"], **{k: float(np.mean([cr[i][k] for cr in cls_rows])) for k in keys}}
                    for i in range(len(cls_rows[0]))]
        F, Tr = pool(fresh), pool(train)
        d_test = np.concatenate([u for u, _ in nn]); d_train = np.concatenate([v for _, v in nn])
        res["subsets"][name] = {
            "n": int(n), "seed": seed, "per_class": int(n // 10),
            "fresh": F, "train": Tr,
            "nn_test_to_train_median": float(np.median(d_test)), "nn_train_to_train_median": float(np.median(d_train)),
            "sigma_c_median_maxw_0.5": crossing(F, "maxw_median", 0.5),
            "sigma_c_frac_maxw_ge_0.5_reaches_0.9": crossing(F, "frac_maxw_ge_0.5", 0.9),
            "sigma_c_frac_maxw_ge_0.9_reaches_0.9": crossing(F, "frac_maxw_ge_0.9", 0.9),
            "sigma_retrieval_own_median_0.5": crossing(Tr, "own_median", 0.5),
        }
        print(name, {k: v for k, v in res["subsets"][name].items() if k.startswith(("sigma", "nn"))}, flush=True)
    res["seconds"] = time.time() - t0
    (out / "summary.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"wrote {out / 'summary.json'} in {res['seconds']:.0f}s")


if __name__ == "__main__":
    main()
