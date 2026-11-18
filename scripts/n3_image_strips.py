"""Dump a few EDM Heun trajectories as images, for the illustration figure (fig:intuition).

For each sample it saves, at every step k, the noisy state x_k, the network's prediction D(x_k), the exact
posterior mean m*(x_k), the endpoint, the endpoint's nearest training image of the class, and the relative
error rho_k = |D - m*| / |x_k - y1| (y1 = that nearest image). Everything in [-1, 1], 3x32x32, float16.

    python -u -m scripts.n3_image_strips --network <pkl> --edm-repo <edm> --cifar-root data \
        [--indices <npy>] --classes 1,7 --n-per-class 8 --out <file.npz>
"""
from __future__ import annotations

import argparse
import pathlib
import pickle
import sys

import numpy as np
import torch

from scripts.n3_edm_memorization import Exact, edm_sigmas, load_cifar_train


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", required=True); ap.add_argument("--edm-repo", required=True)
    ap.add_argument("--cifar-root", default="data"); ap.add_argument("--indices")
    ap.add_argument("--classes", default="1,7"); ap.add_argument("--n-per-class", type=int, default=8)
    ap.add_argument("--steps", type=int, default=18); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    X, lab = load_cifar_train(a.cifar_root)
    if a.indices:
        idx = torch.from_numpy(np.load(a.indices)).long(); X, lab = X[idx], lab[idx]
    X, lab = X.to(dev), lab.to(dev)
    sys.path.insert(0, str(pathlib.Path(a.edm_repo).resolve()))
    import dnnlib  # noqa: E402
    with dnnlib.util.open_url(a.network) as fh:
        net = pickle.load(fh)["ema"].to(dev).eval()
    sig = edm_sigmas(a.steps)
    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    out = {k: [] for k in ("x", "D", "m", "end", "y1", "y2", "rho", "label", "d1", "d2")}
    for c in [int(v) for v in a.classes.split(",")]:
        ex = Exact(X[lab == c]); B = a.n_per_class

        def D(x, s):
            cl = torch.nn.functional.one_hot(torch.full((B,), c, device=dev), net.label_dim).float()
            with torch.no_grad():
                return net(x.view(-1, 3, 32, 32).float(), torch.full((B,), float(s), device=dev), cl).reshape(B, -1).double()

        x = (torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64) * sig[0]).to(dev)
        xs, Ds, ms = [], [], []
        for i in range(a.steps):
            tc, tn = sig[i], sig[i + 1]
            Dk = D(x, tc); xs.append(x); Ds.append(Dk); ms.append(ex(x, tc))
            d = (x - Dk) / tc; xn = x + (tn - tc) * d
            if i < a.steps - 1:
                xn = x + (tn - tc) * (0.5 * d + 0.5 * (xn - D(xn, tn)) / tn)
            x = xn
        dv, di = ex.nearest(x)
        y1 = ex.Y[di[:, 0]]
        rho = torch.stack([(Ds[i] - ms[i]).norm(dim=1) / (xs[i] - y1).norm(dim=1) for i in range(a.steps)], 1)
        f16 = lambda t: t.float().cpu().numpy().astype(np.float16)  # noqa: E731
        out["x"].append(f16(torch.stack(xs, 1))); out["D"].append(f16(torch.stack(Ds, 1)))
        out["m"].append(f16(torch.stack(ms, 1))); out["end"].append(f16(x))
        out["y1"].append(f16(y1)); out["y2"].append(f16(ex.Y[di[:, 1]])); out["rho"].append(rho.cpu().numpy())
        out["label"].append(np.full(B, c)); out["d1"].append(dv[:, 0].cpu().numpy()); out["d2"].append(dv[:, 1].cpu().numpy())
    arr = {k: np.concatenate(v) for k, v in out.items()}
    arr["sigma"] = sig[:a.steps]
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **arr)
    print("saved", a.out, {k: v.shape for k, v in arr.items()}, "off-atom", float((arr["d1"] / arr["d2"] >= 1 / 3).mean()))


if __name__ == "__main__":
    main()
