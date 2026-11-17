"""Directional contraction toward a training image along learned EDM trajectories (Prop. E of
docs/plan/theory_extensions_2026-11-11.md).

For the probability-flow ODE dx/dsigma = (x - D(x, sigma))/sigma and an image y, the distance n = |x - y|
obeys exactly
    d log n / d log sigma = (1 - q) - e_hat . b / n,
    q = int_0^1 e_hat^T J_D(y + tau e) e_hat dtau,   e = x - y,  b = D(y, sigma) - y.
q is the Rayleigh quotient of the denoiser Jacobian along the direction to y, averaged over the segment
[y, x]; mu = (1+sigma) lambda_max only bounds it. Since v^T J v = v . (J^T v), q needs one VJP per
quadrature point (no forward mode).

The script runs EDM's 18-step Heun sampler, takes the endpoint's nearest (y1) and second-nearest (y2)
training image of the class, and at every step records for k = 1, 2
  q{k}      segment average of e_hat^T J_D e_hat (midpoint rule, --nquad points),
  q{k}x     the same at x only (one-point proxy),
  r{k}      the residual term e_hat . b / n,
  q{k}e     the exact denoiser's segment-average q (analytic: Cov_w / sigma^2),
  n{k}      |x - y_k|,
and at the endpoint d1, d2 (off-atom when d1/d2 >= 1/3). The summary splits the change of log n1 over
noise windows into the contraction part -int (1 - q1) dlog sigma and the residual part int r1 dlog sigma,
and compares their sum with the actual change (the gap is the Heun discretisation).

    python -u -m scripts.n3_directional_q --network <pkl> --edm-repo <edm> --cifar-root data \
        [--indices <npy>] --n-per-class 100 --out <dir>
    python -u -m scripts.n3_directional_q --summarize <dir>
    python -u -m scripts.n3_directional_q --fake-net --data <npz> --cpu --out <dir>   # check: q = q_exact
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

from scripts.n3_edm_memorization import RATIO, Exact, auc, edm_sigmas, load_cifar_train

WINDOWS = ((0, 7), (7, 10), (10, 13), (13, 17))  # step ranges of the 18-step schedule: sigma 80->5.3->1.09->0.14->0.002


def rayleigh(f, z, v, dtype):
    """v^T J_f(z) v per row, as v . (J^T v) from one VJP (f is batch-diagonal)."""
    zr = z.to(dtype).detach().requires_grad_(True)
    y = f(zr)
    (g,) = torch.autograd.grad((y * v.to(y.dtype)).sum(), zr)
    return (g.double() * v).sum(1)


def exact_rayleigh(ex, z, v, sigma):
    """v^T Cov_w(z) v / sigma^2: the exact denoiser's Jacobian is Cov_w / sigma^2."""
    w = torch.softmax(ex.logits(z, sigma), 1)
    pv = v @ ex.Y.T                                                  # (B, n)
    mv = (w * pv).sum(1)
    return ((w * pv ** 2).sum(1) - mv ** 2) / sigma ** 2


def run(a):
    device = torch.device("cuda" if torch.cuda.is_available() and not a.cpu else "cpu")
    if a.data:
        z = np.load(a.data)
        X = torch.from_numpy(z["X"]).double(); lab = torch.from_numpy(z["labels"]).long()
    else:
        X, lab = load_cifar_train(a.cifar_root)
    if a.indices:
        idx = torch.from_numpy(np.load(a.indices)).long(); X, lab = X[idx], lab[idx]
    X, lab = X.to(device), lab.to(device)
    classes = sorted(int(c) for c in lab.unique())
    exact = {c: Exact(X[lab == c]) for c in classes}
    if a.fake_net:
        dtype = torch.float64
        def make_f(c, sigma):
            ex = exact[c]
            return lambda x: torch.softmax(ex.logits(x, sigma), 1) @ ex.Y
    else:
        dtype = torch.float32
        sys.path.insert(0, str(pathlib.Path(a.edm_repo).resolve()))
        import dnnlib  # noqa: E402
        with dnnlib.util.open_url(a.network) as fh:
            net = pickle.load(fh)["ema"].to(device).eval()
        for p in net.parameters():
            p.requires_grad_(False)
        def make_f(c, sigma):
            def f(x):
                cl = torch.nn.functional.one_hot(torch.full((len(x),), c, device=device), net.label_dim).float()
                s = torch.full((len(x),), float(sigma), device=device)
                return net(x.view(-1, 3, 32, 32).float(), s, cl).reshape(len(x), -1).to(x.dtype)
            return f
    sig = edm_sigmas(a.steps)
    taus = (torch.arange(a.nquad, dtype=torch.float64) + 0.5) / a.nquad
    keys = [f"{p}{k}" for k in (1, 2) for p in ("q", "qx", "r", "qe", "n")] + ["err", "rad1"]
    out = {k: [] for k in keys + ["label", "d1", "d2", "n1_end"]}
    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    t0 = time.time()
    for c in classes:
        ex = exact[c]
        for b0 in range(0, a.n_per_class, a.batch):
            B = min(a.batch, a.n_per_class - b0)
            x = (torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64) * sig[0]).to(device)
            xs = []
            with torch.no_grad():
                for i in range(a.steps):
                    xs.append(x)
                    tc, tn = sig[i], sig[i + 1]
                    d = (x - make_f(c, tc)(x.to(dtype)).double()) / tc
                    xn = x + (tn - tc) * d
                    if i < a.steps - 1:
                        xn = x + (tn - tc) * (0.5 * d + 0.5 * (xn - make_f(c, tn)(xn.to(dtype)).double()) / tn)
                    x = xn
            dv, di = ex.nearest(x)
            anchors = (ex.Y[di[:, 0]], ex.Y[di[:, 1]])
            rec = {k: torch.full((B, a.steps), float("nan"), dtype=torch.float64) for k in keys}
            for i in range(a.steps):
                s = sig[i]; f = make_f(c, s)
                with torch.no_grad():   # Theorem T1: field error and radial ratio toward y1 at x
                    Dx = f(xs[i].to(dtype)).double()
                    e1 = xs[i] - anchors[0]; n1 = e1.norm(dim=1).clamp_min(1e-30)
                    rec["err"][:, i] = (Dx - ex(xs[i], s)).norm(dim=1).cpu()
                    rec["rad1"][:, i] = ((e1 / n1[:, None]) * (Dx - anchors[0])).sum(1).div(n1).cpu()
                for k, y in zip((1, 2), anchors):
                    e = xs[i] - y; n = e.norm(dim=1); eh = e / n[:, None].clamp_min(1e-30)
                    q = sum(rayleigh(f, y + t * e, eh, dtype) for t in taus) / a.nquad
                    qe = sum(exact_rayleigh(ex, y + t * e, eh, s) for t in taus) / a.nquad
                    qx = rayleigh(f, xs[i], eh, dtype)
                    with torch.no_grad():
                        b = f(y.to(dtype)).double() - y
                    r = (eh * b).sum(1) / n.clamp_min(1e-30)
                    for p, val in (("q", q), ("qx", qx), ("r", r), ("qe", qe), ("n", n)):
                        rec[f"{p}{k}"][:, i] = val.detach().double().cpu()
            for k in keys:
                out[k].append(rec[k])
            out["label"].append(torch.full((B,), c)); out["d1"].append(dv[:, 0].cpu()); out["d2"].append(dv[:, 1].cpu())
            out["n1_end"].append((x - anchors[0]).norm(dim=1).cpu())
        print(f"  class {c} done, {time.time() - t0:.0f}s", flush=True)
    o = pathlib.Path(a.out); o.mkdir(parents=True, exist_ok=True)
    arr = {k: torch.cat(v).numpy() for k, v in out.items()}
    arr["sigma"] = np.asarray(sig[:a.steps]); arr["t"] = 1 / (1 + arr["sigma"])
    np.savez_compressed(o / "q_per_sample.npz", **arr)
    meta = {"network": "fake" if a.fake_net else a.network, "indices": a.indices, "n_per_class": a.n_per_class,
            "nquad": a.nquad, "seed": a.seed, "off_atom_frac": float((arr["d1"] / arr["d2"] >= RATIO).mean()),
            "seconds": time.time() - t0}
    (o / "q_run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


def summarize(d):
    D = pathlib.Path(d); L = ["# Directional contraction q along learned EDM trajectories (Prop. E)", "",
                              "q = segment average of e_hat^T J_D e_hat toward the endpoint's nearest image y1 (q1) "
                              "and second-nearest y2 (q2); qx = the same at x only; qe = exact denoiser; "
                              "AUC = P(off-atom score > on-atom score). log n1 changes by contraction "
                              "-int(1-q1) dlog sigma plus residual int r1 dlog sigma.", ""]
    rows = []
    for f in sorted(D.glob("**/q_per_sample.npz")):
        z = np.load(f); off = z["d1"] / z["d2"] >= RATIO; on = ~off
        med = lambda v, sel: float(np.nanmedian(v[sel])) if sel.any() else float("nan")  # noqa: E731
        fmt = lambda v: "-" if v != v else f"{v:.3f}"  # noqa: E731
        run_name = str(f.parent.relative_to(D)) or "."
        r = {"run": run_name, "n": int(len(off)), "off": int(off.sum()), "steps": [], "windows": []}
        L += [f"## {run_name} (n={len(off)}, off-atom {int(off.sum())})", "",
              "| sigma | q1 off | q1 on | AUC q1 | q1x off | q1x on | q1-q2 off | q1-q2 on | AUC q1-q2 | q1e on | r1 off | r1 on |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for i, s in enumerate(z["sigma"]):
            q1, q2 = z["q1"][:, i], z["q2"][:, i]
            st = {"sigma": float(s), "q1_off": med(q1, off), "q1_on": med(q1, on), "auc_q1": auc(q1[off], q1[on]),
                  "q1x_off": med(z["qx1"][:, i], off), "q1x_on": med(z["qx1"][:, i], on),
                  "dq_off": med(q1 - q2, off), "dq_on": med(q1 - q2, on), "auc_dq": auc((q1 - q2)[off], (q1 - q2)[on]),
                  "q1e_on": med(z["qe1"][:, i], on), "r1_off": med(z["r1"][:, i], off), "r1_on": med(z["r1"][:, i], on)}
            r["steps"].append(st)
            L.append(f"| {s:.4g} | " + " | ".join(fmt(st[k]) for k in ("q1_off", "q1_on", "auc_q1", "q1x_off", "q1x_on",
                     "dq_off", "dq_on", "auc_dq", "q1e_on", "r1_off", "r1_on")) + " |")
        ls = np.log(z["sigma"])
        L += ["", "Change of log n1 = log|x - y1| over noise windows (medians; gap = actual - contraction - residual):", "",
              "| window (sigma) | actual off | actual on | contraction off | contraction on | residual off | residual on | gap on |",
              "|---|---|---|---|---|---|---|---|"]
        for i0, i1 in WINDOWS:
            if i1 >= len(ls):
                continue
            dl = ls[i0:i1] - ls[i0 + 1:i1 + 1]                       # log(sigma_i / sigma_{i+1}) > 0
            avg = lambda v: 0.5 * (v[:, i0:i1] + v[:, i0 + 1:i1 + 1])  # noqa: E731
            act = np.log(z["n1"][:, i1]) - np.log(z["n1"][:, i0])
            con = -(avg(1 - z["q1"]) * dl).sum(1)
            res = (avg(z["r1"]) * dl).sum(1)
            w = {"from": float(z["sigma"][i0]), "to": float(z["sigma"][i1]),
                 "act_off": med(act, off), "act_on": med(act, on), "con_off": med(con, off), "con_on": med(con, on),
                 "res_off": med(res, off), "res_on": med(res, on), "gap_on": med(act - con - res, on)}
            r["windows"].append(w)
            L.append(f"| {w['from']:.3g} -> {w['to']:.3g} | " + " | ".join(fmt(w[k]) for k in
                     ("act_off", "act_on", "con_off", "con_on", "res_off", "res_on", "gap_on")) + " |")
        if "err" in z.files:
            L += ["", "Theorem T1: relative field error rho = |D - m*|/|x - y1| and radial ratio "
                  "rad1 = <e_hat, D - y1>/|x - y1| (= q1 + r1 exactly; landing needs rad1 < 1 late):", "",
                  "| sigma | rho off | rho on | frac rho<1 off | frac rho<1 on | AUC rho | rad1 off | rad1 on | AUC rad1 | max|rad1-q1-r1| |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for i, s in enumerate(z["sigma"]):
                rho = z["err"][:, i] / z["n1"][:, i]; rad = z["rad1"][:, i]
                frac = lambda v, sel: float((v[sel] < 1).mean()) if sel.any() else float("nan")  # noqa: E731
                gap = float(np.nanmax(np.abs(rad - z["q1"][:, i] - z["r1"][:, i])))
                L.append(f"| {s:.4g} | " + " | ".join(fmt(v) for v in (med(rho, off), med(rho, on), frac(rho, off),
                         frac(rho, on), auc(rho[off], rho[on]), med(rad, off), med(rad, on), auc(rad[off], rad[on]), gap)) + " |")
        fin = np.log(z["n1_end"]) - np.log(z["n1"][:, -1])
        L += ["", f"last Euler step (sigma {z['sigma'][-1]:.3g} -> 0, x -> D(x)): median change of log n1 "
              f"off {fmt(med(fin, off))}, on {fmt(med(fin, on))}", ""]
        rows.append(r)
    (D / "q_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    (D / "Q_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network"); ap.add_argument("--edm-repo")
    ap.add_argument("--cifar-root", default="data"); ap.add_argument("--data"); ap.add_argument("--indices")
    ap.add_argument("--n-per-class", type=int, default=100); ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--steps", type=int, default=18); ap.add_argument("--nquad", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--fake-net", action="store_true")
    ap.add_argument("--cpu", action="store_true"); ap.add_argument("--out"); ap.add_argument("--summarize", metavar="DIR")
    a = ap.parse_args()
    if a.summarize:
        return summarize(a.summarize)
    if not a.out or not (a.fake_net or (a.network and a.edm_repo)):
        ap.error("--out and either --fake-net or --network with --edm-repo are required")
    run(a)


if __name__ == "__main__":
    main()
