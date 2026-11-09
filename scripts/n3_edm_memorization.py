"""N3 (docs/plan/next_venue_plan_2026-11-09.md): does the field error of a trained EDM denoiser
against the exact field, measured partway through sampling, flag the samples that end on a
training image?

EDM parametrises sampling by sigma: x = y + sigma n, denoiser D(x, sigma, c) ~ E[y | x, c]. The
exact denoiser of a fixed training set is the Gaussian posterior mean over the training images of
class c,
    m*(x, sigma, c) = sum_i w_i y_i,  w_i ∝ exp(-|x - y_i|^2 / (2 sigma^2)),  y_i in class c,
and |D - m*| is the paper's scaled error (1-t)|Delta| under t = 1/(1+sigma) (the linear
interpolant x_t = t y + (1-t) z rescaled by 1/t). Class labels do not identify a training image,
so only the local transfer statement applies; this is a consistency check, not Theorem transfer.

From the same Gaussian latents this script runs EDM's deterministic Heun sampler (S_churn = 0)
with the network and, with --exact-path, with the exact denoiser, and records per sample and per
sigma step
  e_learned   |D_theta - m*| along the learned trajectory,
  e_exact     |D_theta - m*| along the exact trajectory (the null control of App. C.4),
  nn_hat      distance from D_theta to the nearest training image of the class (baseline a:
              needs no exact field),
  cond_diff   |D_theta(x, c) - mean_c' D_theta(x, c')| (baseline b, with --cond-diff; a
              classifier-free-guidance-like conditional signal for a model without a null label),
and at the endpoint d1, d2 and the nearest index within the class and over all training images.
A sample is off-atom when d1/d2 >= 1/3 within its class, as in App. C.4.

The network is an EDM pickle (path or URL; needs a checkout of https://github.com/NVlabs/edm on
--edm-repo for dnnlib/torch_utils). The training set is CIFAR-10 train from torchvision, in the
order EDM's dataset_tool writes it (data_batch_1..5), optionally restricted with --indices (the
indices.npy written by scripts/make_edm_cifar_subset.py). The model must have been trained on
exactly that set; EDM's augmentation conditions on augment labels that are zero at sampling, so
the exact field over the unaugmented images is the reference.

    python -u -m scripts.n3_edm_memorization --network <pkl|url> --edm-repo <edm> \
        --cifar-root data/cifar10 --n-per-class 100 --exact-path --cond-diff --out <dir>
    python -u -m scripts.n3_edm_memorization --summarize <dir>
    python -u -m scripts.n3_edm_memorization --fake-net --data <npz with X, labels> --out <dir>  # smoke
"""
from __future__ import annotations

import argparse
import json
import pathlib
import pickle
import sys
import time

import numpy as np
import torch

RATIO = 1.0 / 3.0


def edm_sigmas(steps, sigma_min=0.002, sigma_max=80.0, rho=7.0):
    i = np.arange(steps, dtype=np.float64)
    s = (sigma_max ** (1 / rho) + i / (steps - 1) * (sigma_min ** (1 / rho) - sigma_max ** (1 / rho))) ** rho
    return np.concatenate([s, [0.0]])


def load_cifar_train(root):
    import torchvision
    ds = torchvision.datasets.CIFAR10(root=root, train=True, download=False)
    X = torch.from_numpy(ds.data).permute(0, 3, 1, 2).reshape(len(ds.data), -1).double() / 127.5 - 1
    return X, torch.tensor(ds.targets, dtype=torch.long)


class Exact:
    """Exact posterior mean over the training images of one class (float64)."""

    def __init__(self, Y):
        self.Y = Y
        self.sq = (Y ** 2).sum(1)

    def logits(self, x, sigma):
        d2 = (x ** 2).sum(1, keepdim=True) - 2 * x @ self.Y.T + self.sq[None]
        return -d2 / (2 * sigma ** 2)

    def __call__(self, x, sigma):
        return torch.softmax(self.logits(x, sigma), 1) @ self.Y

    def nearest(self, x):
        d2 = ((x ** 2).sum(1, keepdim=True) - 2 * x @ self.Y.T + self.sq[None]).clamp_min(0)
        v, i = d2.topk(2, dim=1, largest=False)
        return v.sqrt(), i


def make_net(args, device, exact_by_class):
    """Return f(x_flat float64, sigma float, labels long) -> denoised (float64, flat)."""
    if args.fake_net:
        # Smoke-test stand-in: the exact denoiser plus a smooth label-dependent perturbation.
        def f(x, sigma, labels):
            out = torch.empty_like(x)
            for c in labels.unique():
                k = labels == c
                out[k] = exact_by_class[int(c)](x[k], sigma)
            return out + args.fake_scale * torch.tanh(x / (1 + sigma)) * (1 + labels[:, None].double() / 10)
        return f, 10
    sys.path.insert(0, str(pathlib.Path(args.edm_repo).resolve()))
    import dnnlib  # noqa: E402  (from the EDM checkout)
    with dnnlib.util.open_url(args.network) as fh:
        net = pickle.load(fh)["ema"].to(device).eval()

    @torch.no_grad()
    def f(x, sigma, labels):
        cl = torch.nn.functional.one_hot(labels, net.label_dim).to(device, torch.float32)
        s = torch.full((len(x),), float(sigma), device=device, dtype=torch.float64)
        return net(x.view(-1, 3, 32, 32), s, cl).to(torch.float64).reshape(len(x), -1)
    return f, net.label_dim


def heun(den, x0, sig, record):
    """EDM deterministic Heun sampler; record(i, x, D) at each first-order evaluation."""
    x = x0 * sig[0]
    n = len(sig) - 1
    for i in range(n):
        tc, tn = sig[i], sig[i + 1]
        D = den(x, tc)
        record(i, x, D)
        d = (x - D) / tc
        xn = x + (tn - tc) * d
        if i < n - 1:
            d2 = (xn - den(xn, tn)) / tn
            xn = x + (tn - tc) * (0.5 * d + 0.5 * d2)
        x = xn
    return x


@torch.no_grad()
def run(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    if args.data:
        z = np.load(args.data)
        X = torch.from_numpy(z["X"]).double(); lab = torch.from_numpy(z["labels"]).long()
    else:
        X, lab = load_cifar_train(args.cifar_root)
    if args.indices:
        idx = torch.from_numpy(np.load(args.indices)).long()
        X, lab = X[idx], lab[idx]
    X, lab = X.to(device), lab.to(device)
    classes = sorted(int(c) for c in lab.unique())
    exact = {c: Exact(X[lab == c]) for c in classes}
    allX = Exact(X)
    net, label_dim = make_net(args, device, exact)
    sig = edm_sigmas(args.steps)
    n_s = args.steps
    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    rec = {k: [] for k in ("label", "e_learned", "e_exact", "nn_hat", "cond_diff", "d1", "d2", "nn",
                           "d1_all", "nn_all", "exact_d1", "exact_d2", "exact_nn", "learned_exact_dist")}
    t0 = time.time()
    for c in classes:
        for b0 in range(0, args.n_per_class, args.batch):
            B = min(args.batch, args.n_per_class - b0)
            x0 = torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64).to(device)
            L = torch.full((B,), c, dtype=torch.long, device=device)
            eL = torch.zeros(B, n_s, dtype=torch.float64); nh = torch.zeros_like(eL); cd = torch.zeros_like(eL)

            def rec_learned(i, x, D):
                eL[:, i] = (D - exact[c](x, sig[i])).norm(dim=1).cpu()
                nh[:, i] = exact[c].nearest(D)[0][:, 0].cpu()
                if args.cond_diff:
                    Ds = torch.stack([net(x, sig[i], torch.full_like(L, k)) for k in range(label_dim)])
                    cd[:, i] = (D - Ds.mean(0)).norm(dim=1).cpu()
            xL = heun(lambda x, s: net(x, s, L), x0, sig, rec_learned)
            dv, di = exact[c].nearest(xL); dav, dai = allX.nearest(xL)
            eX = torch.full((B, n_s), float("nan"), dtype=torch.float64)
            ed = torch.full((B, 2), float("nan"), dtype=torch.float64); en = torch.full((B,), -1, dtype=torch.long)
            ld = torch.full((B,), float("nan"), dtype=torch.float64)
            if args.exact_path:
                def rec_exact(i, x, D):
                    eX[:, i] = (net(x, sig[i], L) - D).norm(dim=1).cpu()
                xE = heun(lambda x, s: exact[c](x, s), x0, sig, rec_exact)
                ev, ei = exact[c].nearest(xE)
                ed, en = ev.cpu(), ei[:, 0].cpu()
                ld = (xL - xE).norm(dim=1).cpu()
            for k, v in (("label", L.cpu()), ("e_learned", eL), ("e_exact", eX), ("nn_hat", nh), ("cond_diff", cd),
                         ("d1", dv[:, 0].cpu()), ("d2", dv[:, 1].cpu()), ("nn", di[:, 0].cpu()),
                         ("d1_all", dav[:, 0].cpu()), ("nn_all", dai[:, 0].cpu()),
                         ("exact_d1", ed[:, 0]), ("exact_d2", ed[:, 1]), ("exact_nn", en),
                         ("learned_exact_dist", ld)):
                rec[k].append(v)
        print(f"  class {c} done, {time.time() - t0:.0f}s", flush=True)
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
    arr = {k: torch.cat(v).numpy() for k, v in rec.items()}
    arr["sigma"] = sig[:-1]; arr["t"] = 1 / (1 + sig[:-1])
    np.savez_compressed(out / "per_sample.npz", **arr)
    meta = {"network": "fake" if args.fake_net else args.network, "n_train": int(len(X)),
            "indices": args.indices, "n_per_class": args.n_per_class, "steps": args.steps, "seed": args.seed,
            "exact_path": bool(args.exact_path), "cond_diff": bool(args.cond_diff),
            "off_atom_frac": float((arr["d1"] / arr["d2"] >= RATIO).mean()), "seconds": time.time() - t0}
    (out / "run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


def auc(pos, neg):
    """P(pos > neg) + P(pos = neg)/2, as in scripts/summarize_s10_cifar.py."""
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    x = np.concatenate([pos, neg]); r = np.empty(len(x)); o = x.argsort(kind="mergesort")
    r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def summarize(d):
    D = pathlib.Path(d)
    rows = []
    for f in sorted(D.glob("**/per_sample.npz")):
        z = np.load(f); off = z["d1"] / z["d2"] >= RATIO
        r = {"run": str(f.parent.relative_to(D)) or ".", "n": int(len(off)), "off_frac": float(off.mean()),
             "t": [float(v) for v in z["t"]], "sigma": [float(v) for v in z["sigma"]]}
        for k in ("e_learned", "e_exact", "nn_hat", "cond_diff"):
            a = z[k]
            r[f"auc_{k}"] = [auc(a[off, j], a[~off, j]) if np.isfinite(a[:, j]).any() and a[:, j].any() else None
                             for j in range(a.shape[1])]
        e_end = z["e_learned"][:, -1]
        r["final_e_vs_d1_max_rel"] = float(np.max(np.abs(z["d1"] - e_end) / np.maximum(e_end, 1e-12)))
        if np.isfinite(z["exact_d1"]).any():
            r["exact_off_frac"] = float((z["exact_d1"] / z["exact_d2"] >= RATIO).mean())
            on = ~off
            r["same_atom_on"] = float((z["nn"][on] == z["exact_nn"][on]).mean()) if on.any() else None
        rows.append(r)
    (D / "n3_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    fmt = lambda v: "–" if v is None or v != v else f"{v:.3f}"  # noqa: E731
    L = ["# N3: field error of an EDM denoiser against the exact field", ""]
    for r in rows:
        L += [f"## {r['run']} (n={r['n']}, off-atom {r['off_frac']:.3f}"
              + (f", exact off-atom {r['exact_off_frac']:.3f}, same image as exact among on-atom {fmt(r['same_atom_on'])}"
                 if "exact_off_frac" in r else "") + ")", "",
              f"final error vs d1, max relative deviation: {r['final_e_vs_d1_max_rel']:.4f}", "",
              "| sigma | t | AUC e_learned | AUC e_exact | AUC nn_hat | AUC cond_diff |", "|---|---|---|---|---|---|"]
        for j in range(len(r["t"])):
            L.append(f"| {r['sigma'][j]:.4g} | {r['t'][j]:.4f} | {fmt(r['auc_e_learned'][j])} | {fmt(r['auc_e_exact'][j])} | "
                     f"{fmt(r['auc_nn_hat'][j])} | {fmt(r['auc_cond_diff'][j])} |")
        L.append("")
    (D / "N3_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", help="EDM pickle path or URL")
    ap.add_argument("--edm-repo", help="checkout of NVlabs/edm (for dnnlib, torch_utils)")
    ap.add_argument("--cifar-root", default="data/cifar10", help="torchvision CIFAR-10 root (already downloaded)")
    ap.add_argument("--data", help="npz with X (N, 3072) in [-1, 1] and labels, instead of --cifar-root")
    ap.add_argument("--indices", help="indices.npy restricting the training set (from make_edm_cifar_subset)")
    ap.add_argument("--n-per-class", type=int, default=100)
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--steps", type=int, default=18)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exact-path", action="store_true")
    ap.add_argument("--cond-diff", action="store_true")
    ap.add_argument("--fake-net", action="store_true", help="smoke test without EDM")
    ap.add_argument("--fake-scale", type=float, default=0.05, help="perturbation of the fake net")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--summarize", metavar="DIR")
    a = ap.parse_args()
    if a.summarize:
        return summarize(a.summarize)
    if not a.out or not (a.fake_net or (a.network and a.edm_repo)):
        ap.error("--out and either --fake-net or --network with --edm-repo are required")
    run(a)


if __name__ == "__main__":
    main()
