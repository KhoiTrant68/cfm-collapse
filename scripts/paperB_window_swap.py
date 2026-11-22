"""E1 of docs/plan/paperB_gpu_experiments_2026-11-21.md: the exact field on a window of noise levels.

    python -u -m scripts.paperB_window_swap --network <pkl> --edm-repo <edm> --cifar-root <root> \
        --n-per-class 100 --out <dir>
    python -m scripts.paperB_window_swap --summarize <dir>

From the same Gaussian latents, EDM's deterministic Heun sampler (scripts/n3_edm_memorization.heun)
is run with the exact class posterior mean m* on a window of noise levels and the network
elsewhere: the denoiser at an evaluation level s is m* if lo < s <= hi and D_theta otherwise.
Window (lo, inf) is the exact->net swap at lo, window (0, hi) the net->exact swap at hi, and
windows with 0 < lo < hi < inf hand the state back to the network at lo after the exact field has
contracted it on (lo, hi]. The pre-registered predictions (P1.1-P1.3) are in the plan document;
this script only records, per sample, the endpoint distances d1, d2 to the nearest and second
nearest training image of the class, the nearest image index, and the distance to the learned
endpoint. Off-atom means d1/d2 >= 1/3, as everywhere in the paper.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import time

import numpy as np
import torch

from scripts.n3_edm_memorization import RATIO, Exact, edm_sigmas, heun, load_cifar_train, make_net

DEFAULT_WINDOWS = ("0.02:inf,0.05:inf,0.1:inf,0.2:inf,0.5:inf,1:inf,"      # exact->net at lo (P1.1)
                   "0:0.02,0:0.1,0:0.5,"                                     # net->exact at hi
                   "0.02:0.5,0.05:0.5,0.1:0.5,0.05:2,0.1:2,0.05:5,0.1:1")   # middle windows (P1.2)


def parse_windows(spec):
    out = []
    for w in spec.split(","):
        lo, hi = w.split(":")
        out.append((float(lo), math.inf if hi == "inf" else float(hi)))
    return out


def wname(lo, hi):
    return f"exact({lo:g},{'inf' if math.isinf(hi) else f'{hi:g}'}]"


@torch.no_grad()
def run(a):
    device = torch.device("cuda" if torch.cuda.is_available() and not a.cpu else "cpu")
    if a.data:
        z = np.load(a.data)
        X = torch.from_numpy(z["X"]).double(); lab = torch.from_numpy(z["labels"]).long()
    else:
        X, lab = load_cifar_train(a.cifar_root)
    if a.indices:
        idx = torch.from_numpy(np.load(a.indices)).long()
        X, lab = X[idx], lab[idx]
    X, lab = X.to(device), lab.to(device)
    classes = sorted(int(c) for c in lab.unique())
    if a.classes:
        classes = [c for c in classes if c in {int(k) for k in a.classes.split(",")}]
    exact = {c: Exact(X[lab == c]) for c in classes}
    net, _ = make_net(a, device, exact)
    sig = edm_sigmas(a.steps)
    windows = parse_windows(a.windows)
    runs = ["learned", "exact"] + [wname(lo, hi) for lo, hi in windows]
    rec = {r: {"d1": [], "d2": [], "nn": [], "dist_to_learned": []} for r in runs}
    labels = []
    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    t0 = time.time()
    for c in classes:
        for b0 in range(0, a.n_per_class, a.batch):
            B = min(a.batch, a.n_per_class - b0)
            x0 = torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64).to(device)
            L = torch.full((B,), c, dtype=torch.long, device=device)
            dens = {"learned": lambda x, s: net(x, s, L), "exact": lambda x, s: exact[c](x, s)}
            for lo, hi in windows:
                dens[wname(lo, hi)] = (lambda lo_, hi_: lambda x, s_: exact[c](x, s_) if lo_ < s_ <= hi_
                                       else net(x, s_, L))(lo, hi)
            ends = {}
            for r in runs:
                xe = heun(dens[r], x0, sig, lambda *_: None)
                v, i = exact[c].nearest(xe)
                rec[r]["d1"].append(v[:, 0].cpu()); rec[r]["d2"].append(v[:, 1].cpu()); rec[r]["nn"].append(i[:, 0].cpu())
                ends[r] = xe
            for r in runs:
                rec[r]["dist_to_learned"].append((ends[r] - ends["learned"]).norm(dim=1).cpu())
            labels.append(L.cpu())
        print(f"  class {c} done, {time.time() - t0:.0f}s", flush=True)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    arr = {"label": torch.cat(labels).numpy(), "sigma": sig[:-1],
           "windows": np.array([[lo, hi] for lo, hi in windows])}
    for r in runs:
        for k in rec[r]:
            arr[f"{r}:{k}"] = torch.cat(rec[r][k]).numpy()
    np.savez_compressed(out / "window_per_sample.npz", **arr)
    meta = {"network": "fake" if a.fake_net else a.network, "n_train": int(len(X)), "indices": a.indices,
            "n_per_class": a.n_per_class, "classes": classes, "steps": a.steps, "seed": a.seed,
            "windows": [[lo, None if math.isinf(hi) else hi] for lo, hi in windows],
            "device": str(device), "seconds": time.time() - t0}
    (out / "window_run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


def summarize(d):
    D = pathlib.Path(d)
    rows = []
    for f in sorted(D.glob("**/window_per_sample.npz")):
        z = np.load(f)
        names = sorted({k.split(":")[0] for k in z.files if ":" in k})
        nnL = z["learned:nn"]
        for r in names:
            off = z[f"{r}:d1"] / z[f"{r}:d2"] >= RATIO
            rows.append({"run": str(f.parent.relative_to(D)) or ".", "denoiser": r, "n": int(len(off)),
                         "off_atom": float(off.mean()), "same_image_as_learned": float((z[f"{r}:nn"] == nnL).mean()),
                         "median_d1": float(np.median(z[f"{r}:d1"])),
                         "median_dist_to_learned": float(np.median(z[f"{r}:dist_to_learned"]))})
    (D / "window_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["| run | denoiser | n | off-atom | same image as learned | median d1 | median dist. to learned |",
         "|---|---|---|---|---|---|---|"]
    L += [f"| {r['run']} | {r['denoiser']} | {r['n']} | {r['off_atom']:.3f} | {r['same_image_as_learned']:.3f} | "
          f"{r['median_d1']:.3f} | {r['median_dist_to_learned']:.3f} |" for r in rows]
    (D / "WINDOW_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network"); ap.add_argument("--edm-repo")
    ap.add_argument("--cifar-root", default="data"); ap.add_argument("--data"); ap.add_argument("--indices")
    ap.add_argument("--n-per-class", type=int, default=100); ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--classes", help="comma-separated subset of classes (smoke tests)")
    ap.add_argument("--steps", type=int, default=18)
    ap.add_argument("--windows", default=DEFAULT_WINDOWS, help="lo:hi pairs; the exact field is used for lo < sigma <= hi")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fake-net", action="store_true"); ap.add_argument("--fake-scale", type=float, default=0.05)
    ap.add_argument("--cpu", action="store_true"); ap.add_argument("--out"); ap.add_argument("--summarize", metavar="DIR")
    a = ap.parse_args()
    if a.summarize:
        return summarize(a.summarize)
    if not a.out or not (a.fake_net or (a.network and a.edm_repo)):
        ap.error("--out and either --fake-net or --network with --edm-repo are required")
    run(a)


if __name__ == "__main__":
    main()
