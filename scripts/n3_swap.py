"""Proposal 2 of reports/Khoảng trống novelty sai số muộn.md: swap the denoiser partway through
sampling, in both directions, to separate "which training image" from "whether on a training image".

From the same Gaussian latents, EDM's deterministic Heun sampler (as in scripts/n3_edm_memorization.py)
is run with four denoisers:
  learned        D_theta at every sigma;
  exact          the exact class-conditional posterior mean m* at every sigma;
  net->exact     D_theta for sigma > s, m* for sigma <= s   (model early, exact field late);
  exact->net     m* for sigma > s, D_theta for sigma <= s   (exact early, model late; the direction
                 of the small-sigma swaps of Dodson et al. 2026, with the exact field as the donor).
For each swap level s it records, per sample, d1, d2 and the nearest training image of the class at
the endpoint. Off-atom means d1/d2 >= 1/3, as in App. C.4.

What the late-error picture predicts: net->exact ends on a training image for every s small enough
that the exact field still has time to contract (it is attracting near an atom), and its choice of
image is the one already made by the learned trajectory once s is below the commitment scale;
exact->net ends off-atom whenever the network's late Jacobian has mu >= 1 (no contraction), even if
the exact field had brought the state close to an image.

    python -u -m scripts.n3_swap --network <pkl|url> --edm-repo <edm> --cifar-root data \
        --n-per-class 50 --out <dir>
    python -u -m scripts.n3_swap --summarize <dir>
    python -u -m scripts.n3_swap --fake-net --data <npz with X, labels> --out <dir>   # smoke
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import torch

from scripts.n3_edm_memorization import RATIO, Exact, edm_sigmas, heun, load_cifar_train, make_net


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
    exact = {c: Exact(X[lab == c]) for c in classes}
    net, _ = make_net(a, device, exact)
    sig = edm_sigmas(a.steps)
    swaps = [float(s) for s in a.swap_sigmas.split(",")]
    runs = ["learned", "exact"] + [f"{k}@{s:g}" for s in swaps for k in ("net2exact", "exact2net")]
    rec = {r: {"d1": [], "d2": [], "nn": []} for r in runs}
    rec_x = {r: [] for r in runs if r != "learned"}   # distance of each endpoint to the learned endpoint
    labels = []
    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    t0 = time.time()
    for c in classes:
        for b0 in range(0, a.n_per_class, a.batch):
            B = min(a.batch, a.n_per_class - b0)
            x0 = torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64).to(device)
            L = torch.full((B,), c, dtype=torch.long, device=device)
            dens = {"learned": lambda x, s: net(x, s, L), "exact": lambda x, s: exact[c](x, s)}
            for s in swaps:
                dens[f"net2exact@{s:g}"] = (lambda sw: lambda x, s_: net(x, s_, L) if s_ > sw else exact[c](x, s_))(s)
                dens[f"exact2net@{s:g}"] = (lambda sw: lambda x, s_: exact[c](x, s_) if s_ > sw else net(x, s_, L))(s)
            ends = {}
            for r in runs:
                xe = heun(dens[r], x0, sig, lambda *_: None)
                v, i = exact[c].nearest(xe)
                rec[r]["d1"].append(v[:, 0].cpu()); rec[r]["d2"].append(v[:, 1].cpu()); rec[r]["nn"].append(i[:, 0].cpu())
                ends[r] = xe
            for r in rec_x:
                rec_x[r].append((ends[r] - ends["learned"]).norm(dim=1).cpu())
            labels.append(L.cpu())
        print(f"  class {c} done, {time.time() - t0:.0f}s", flush=True)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    arr = {"label": torch.cat(labels).numpy(), "swap_sigmas": np.array(swaps), "sigma": sig[:-1]}
    for r in runs:
        for k in ("d1", "d2", "nn"):
            arr[f"{r}:{k}"] = torch.cat(rec[r][k]).numpy()
    for r in rec_x:
        arr[f"{r}:dist_to_learned"] = torch.cat(rec_x[r]).numpy()
    np.savez_compressed(out / "swap_per_sample.npz", **arr)
    meta = {"network": "fake" if a.fake_net else a.network, "n_train": int(len(X)), "indices": a.indices,
            "n_per_class": a.n_per_class, "steps": a.steps, "seed": a.seed, "swap_sigmas": swaps,
            "seconds": time.time() - t0}
    (out / "swap_run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


def summarize(d):
    D = pathlib.Path(d)
    rows = []
    for f in sorted(D.glob("**/swap_per_sample.npz")):
        z = np.load(f)
        off = lambda r: z[f"{r}:d1"] / z[f"{r}:d2"] >= RATIO  # noqa: E731
        nnL, nnE = z["learned:nn"], z["exact:nn"]
        row = {"run": str(f.parent.relative_to(D)) or ".", "n": int(len(nnL)),
               "learned_off": float(off("learned").mean()), "exact_off": float(off("exact").mean()),
               "learned_eq_exact_nn": float((nnL == nnE).mean()), "levels": []}
        for s in z["swap_sigmas"]:
            lv = {"sigma": float(s), "t": float(1 / (1 + s))}
            for k in ("net2exact", "exact2net"):
                r = f"{k}@{s:g}"
                lv[k] = {"off": float(off(r).mean()), "nn_eq_learned": float((z[f"{r}:nn"] == nnL).mean()),
                         "nn_eq_exact": float((z[f"{r}:nn"] == nnE).mean()),
                         "median_d1": float(np.median(z[f"{r}:d1"])),
                         "median_dist_to_learned": float(np.median(z[f"{r}:dist_to_learned"]))}
            row["levels"].append(lv)
        rows.append(row)
    (D / "swap_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["# Proposal 2: denoiser swap at sigma = s", "",
         "off = fraction off-atom (d1/d2 >= 1/3); =L, =E = fraction whose nearest training image equals that of "
         "the learned / exact endpoint; d1 = median endpoint distance to the nearest image; abs-L = median "
         "distance of the exact->net endpoint to the learned endpoint.", ""]
    for r in rows:
        L += [f"## {r['run']} (n={r['n']}; learned off-atom {r['learned_off']:.3f}, exact off-atom "
              f"{r['exact_off']:.3f}, learned and exact share the nearest image {r['learned_eq_exact_nn']:.3f})", "",
              "| s | t | net->exact off | =L | =E | d1 | exact->net off | =L | =E | d1 | abs-L |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for lv in r["levels"]:
            A, Bv = lv["net2exact"], lv["exact2net"]
            L.append(f"| {lv['sigma']:.4g} | {lv['t']:.4f} | {A['off']:.3f} | {A['nn_eq_learned']:.3f} | "
                     f"{A['nn_eq_exact']:.3f} | {A['median_d1']:.3f} | {Bv['off']:.3f} | {Bv['nn_eq_learned']:.3f} | "
                     f"{Bv['nn_eq_exact']:.3f} | {Bv['median_d1']:.3f} | {Bv['median_dist_to_learned']:.3f} |")
        L.append("")
    (D / "SWAP_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network"); ap.add_argument("--edm-repo")
    ap.add_argument("--cifar-root", default="data"); ap.add_argument("--data"); ap.add_argument("--indices")
    ap.add_argument("--n-per-class", type=int, default=50); ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--steps", type=int, default=18)
    ap.add_argument("--swap-sigmas", default="5,2,1,0.5,0.2,0.1,0.05,0.02",
                    help="swap levels s; the denoiser changes for sigma <= s")
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
