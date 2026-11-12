"""Prediction test for the contraction sketch (docs/plan/theorem_sketch_late_error_2026-11-10.md):
along learned EDM trajectories, is the one-sided Lipschitz constant of the data prediction below 1
for samples that end on a training image and about 1 or above for those that do not?

EDM samples x = y + sigma n with denoiser D(x, sigma, c). In the paper's coordinates, Z_t = t x with
t = 1/(1+sigma), and the data prediction is xhat(Z, t) = D(Z/t, sigma), so
    mu_cfm = lambda_max(sym d_Z xhat) = (1 + sigma) * lambda_max(sym d_x D).
The exact denoiser m*(x) = sum_i w_i y_i over the class's training images has
d_x m* = Cov_w(y)/sigma^2 (symmetric, PSD), so mu*_cfm = (1 + sigma) lambda_max(Cov_w)/sigma^2.

At chosen sampler steps the script computes, per sample on the learned trajectory,
  mu_learned  (1+sigma) lambda_max(sym J_D), by power iteration with JVP and VJP (shifted so the top
              eigenvalue, not the largest in magnitude, is found);
  mu_exact    the same for the exact denoiser at the same point;
and at the endpoint d1, d2 to the class's training images (off-atom when d1/d2 >= 1/3).

    python -u -m scripts.n3_jacobian_mu --network <pkl> --edm-repo <edm> --cifar-root data \
        [--indices <npy>] --n-per-class 20 --out <dir>
    python -u -m scripts.n3_jacobian_mu --summarize <dir>
    python -u -m scripts.n3_jacobian_mu --fake-net --data <npz> --cpu --out <dir>   # check: mu_learned = mu_exact
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


def exact_mu(ex, x, sigma, iters):
    """(1+sigma) lambda_max(Cov_w)/sigma^2 for each row of x (Cov_w is PSD, so plain power iteration)."""
    w = torch.softmax(ex.logits(x, sigma), 1)                       # (B, n)
    m = w @ ex.Y                                                     # (B, D)
    v = torch.randn_like(x); v /= v.norm(dim=1, keepdim=True)
    lam = torch.zeros(len(x), dtype=x.dtype, device=x.device)
    for _ in range(iters):
        Yv = v @ ex.Y.T                                              # (B, n)
        Cv = (w * Yv) @ ex.Y - m * (m * v).sum(1, keepdim=True)      # Cov_w v
        lam = (v * Cv).sum(1)
        v = Cv / Cv.norm(dim=1, keepdim=True).clamp_min(1e-30)
    return (1 + sigma) * lam / sigma ** 2


def sym_matvec(f, x, v, mode):
    """sym(J_f(x)) v for a batch-diagonal f (each row depends only on its own row)."""
    if mode == "func":
        _, jv = torch.func.jvp(f, (x,), (v,))
        _, vjp_fn = torch.func.vjp(f, x)
        (jtv,) = vjp_fn(v)
    elif mode == "dvjp":  # J v as the VJP of the (linear in u) map u -> J^T u: exact, reverse mode only
        xr = x.detach().requires_grad_(True)
        y = f(xr)
        (jtv,) = torch.autograd.grad(y, xr, grad_outputs=v, retain_graph=True)
        u = torch.zeros_like(y, requires_grad=True)
        (g,) = torch.autograd.grad(y, xr, grad_outputs=u, create_graph=True)
        (jv,) = torch.autograd.grad(g, u, grad_outputs=v)
    else:  # central finite difference for J v, autograd for J^T v
        h = 1e-3 * x.norm(dim=1, keepdim=True).clamp_min(1.0) / v.norm(dim=1, keepdim=True).clamp_min(1e-12)
        with torch.no_grad():
            jv = (f(x + h * v) - f(x - h * v)) / (2 * h)
        xr = x.detach().requires_grad_(True)
        (jtv,) = torch.autograd.grad((f(xr) * v).sum(), xr)
    return 0.5 * (jv + jtv)


def learned_mu(f, x, sigma, iters, mode):
    """(1+sigma) lambda_max(sym J_f(x)) per row: power iteration, then a shifted pass for the top eigenvalue."""
    v = torch.randn_like(x); v /= v.norm(dim=1, keepdim=True)
    lam = torch.zeros(len(x), dtype=x.dtype, device=x.device)
    for _ in range(iters):                                           # dominant (largest |lambda|)
        w = sym_matvec(f, x, v, mode)
        lam = (v * w).sum(1)
        v = w / w.norm(dim=1, keepdim=True).clamp_min(1e-30)
    c = lam.abs()[:, None] + 1e-6                                    # S + cI is PSD
    v = torch.randn_like(x); v /= v.norm(dim=1, keepdim=True)
    top = torch.zeros_like(lam)
    for _ in range(iters):
        w = sym_matvec(f, x, v, mode) + c * v
        top = (v * w).sum(1) - c[:, 0]
        v = w / w.norm(dim=1, keepdim=True).clamp_min(1e-30)
    v = torch.randn_like(x); v /= v.norm(dim=1, keepdim=True)
    bot = torch.zeros_like(lam)
    for _ in range(iters):                                           # cI - S is PSD: its top is c - lambda_min
        w = c * v - sym_matvec(f, x, v, mode)
        bot = c[:, 0] - (v * w).sum(1)
        v = w / w.norm(dim=1, keepdim=True).clamp_min(1e-30)
    return (1 + sigma) * top.detach(), (1 + sigma) * lam.detach(), (1 + sigma) * bot.detach()


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
    rec_steps = [int(s) for s in a.record_steps.split(",")]
    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    out = {k: [] for k in ("label", "mu_learned", "lam_dom", "mu_min", "mu_exact", "d1", "d2")}
    precond = {"name": "exact", "sigma_data": None} if a.fake_net else \
        {"name": type(net).__name__, "sigma_data": float(getattr(net, "sigma_data", 0.5))}
    t0 = time.time()
    for c in classes:
        for b0 in range(0, a.n_per_class, a.batch):
            B = min(a.batch, a.n_per_class - b0)
            x = (torch.randn(B, X.shape[1], generator=gen, dtype=torch.float64) * sig[0]).to(device)
            muL = torch.full((B, len(rec_steps)), float("nan"), dtype=torch.float64)
            lamD = muL.clone(); muX = muL.clone(); muMin = muL.clone()
            for i in range(a.steps):
                tc, tn = sig[i], sig[i + 1]
                f = make_f(c, tc)
                if i in rec_steps:
                    k = rec_steps.index(i)
                    xi = x.to(dtype)
                    try:
                        m1, l1, b1 = learned_mu(f, xi, tc, a.iters, a.jvp)
                    except Exception as err:   # forward-mode AD unsupported by some op: fall back once
                        if a.jvp != "func":
                            raise
                        print(f"  torch.func failed ({type(err).__name__}: {err}); using double VJP", flush=True)
                        a.jvp = "dvjp"
                        m1, l1, b1 = learned_mu(f, xi, tc, a.iters, a.jvp)
                    muL[:, k] = m1.double().cpu(); lamD[:, k] = l1.double().cpu(); muMin[:, k] = b1.double().cpu()
                    muX[:, k] = exact_mu(exact[c], x, tc, a.iters).cpu()
                with torch.no_grad():
                    D = f(x.to(dtype)).double()
                    d = (x - D) / tc
                    xn = x + (tn - tc) * d
                    if i < a.steps - 1:
                        D2 = make_f(c, tn)(xn.to(dtype)).double()
                        xn = x + (tn - tc) * (0.5 * d + 0.5 * (xn - D2) / tn)
                    x = xn
            dv, _ = exact[c].nearest(x)
            for key, val in (("label", torch.full((B,), c)), ("mu_learned", muL), ("lam_dom", lamD), ("mu_min", muMin), ("mu_exact", muX),
                             ("d1", dv[:, 0].cpu()), ("d2", dv[:, 1].cpu())):
                out[key].append(val)
        print(f"  class {c} done, {time.time() - t0:.0f}s", flush=True)
    o = pathlib.Path(a.out); o.mkdir(parents=True, exist_ok=True)
    arr = {k: torch.cat(v).numpy() for k, v in out.items()}
    arr["sigma"] = np.array([sig[i] for i in rec_steps]); arr["t"] = 1 / (1 + arr["sigma"])
    np.savez_compressed(o / "mu_per_sample.npz", **arr)
    meta = {"network": "fake" if a.fake_net else a.network, "indices": a.indices, "n_per_class": a.n_per_class,
            "record_steps": rec_steps, "iters": a.iters, "jvp": a.jvp, "seed": a.seed, "precond": precond,
            "off_atom_frac": float((arr["d1"] / arr["d2"] >= RATIO).mean()), "seconds": time.time() - t0}
    (o / "mu_run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


def precond_coeffs(name, sigma, sigma_data):
    """(c_skip, c_out * c_in) of EDM's preconditioners, D(x) = c_skip x + c_out F(c_in x)."""
    if name == "EDMPrecond":
        sd = sigma_data
        return sd ** 2 / (sigma ** 2 + sd ** 2), sigma * sd / (sigma ** 2 + sd ** 2)
    if name == "VPPrecond":
        return 1.0, -sigma / np.sqrt(sigma ** 2 + 1)
    if name == "VEPrecond":
        return 1.0, sigma
    return None


def summarize(d):
    """Besides mu, reports the scaled raw-network term of the parametrization sketch: with
    J_D = c_skip I + c_out c_in J_F, the eigenvalue of sym J_F that sets lambda_max(sym J_D) is
    lam_F = (mu/(1+sigma) - c_skip) / (c_out c_in) (lambda_max of J_F if c_out c_in > 0, lambda_min if < 0),
    and sigma * lam_F stays O(1)-bounded away from 0 only if the network Jacobian grows like 1/sigma."""
    D = pathlib.Path(d); rows = []
    for f in sorted(D.glob("**/mu_per_sample.npz")):
        z = np.load(f); off = z["d1"] / z["d2"] >= RATIO
        rj = f.parent / "mu_run.json"
        meta = json.loads(rj.read_text(encoding="utf-8")) if rj.exists() else {}
        pc = meta.get("precond")
        if pc is None and meta.get("network") not in (None, "fake"):  # runs before precond was recorded
            net_path = str(meta["network"])  # public cond-vp pickle, or a train.py run (default --precond edm)
            pc = {"name": "VPPrecond" if "-vp" in net_path else "EDMPrecond", "sigma_data": 0.5, "inferred": True}
        r = {"run": str(f.parent.relative_to(D)) or ".", "n": int(len(off)), "off_frac": float(off.mean()),
             "precond": pc, "steps": []}
        for k, (s, t) in enumerate(zip(z["sigma"], z["t"])):
            mL, mX = z["mu_learned"][:, k], z["mu_exact"][:, k]
            g = lambda m, sel: float(np.median(m[sel])) if sel.any() else None  # noqa: E731
            st = {"sigma": float(s), "t": float(t),
                  "mu_learned_med_off": g(mL, off), "mu_learned_med_on": g(mL, ~off),
                  "frac_mu_below_1_off": float((mL[off] < 1).mean()) if off.any() else None,
                  "frac_mu_below_1_on": float((mL[~off] < 1).mean()) if (~off).any() else None,
                  "mu_exact_med": float(np.median(mX)), "auc_mu_learned": auc(mL[off], mL[~off])}
            if "mu_min" in z.files:
                mm = z["mu_min"][:, k]
                st.update(mu_min_med_off=g(mm, off), mu_min_med_on=g(mm, ~off))
            co = precond_coeffs(pc["name"], float(s), pc["sigma_data"]) if pc else None
            if co:
                # rho = 1 - lambda_max(sym J_D)/c_skip = -(c_out c_in / c_skip) * lam_F: the share of the exact
                # field's contraction (rho = 1 for J_D = 0) carried by the raw network; rho = O(sigma) when J_F is bounded
                rho = 1 - mL / ((1 + s) * co[0])
                st.update(rho_med_off=g(rho, off), rho_med_on=g(rho, ~off), auc_rho=auc(rho[off], rho[~off]),
                          rho_over_sigma_med_off=g(rho / s, off))
            r["steps"].append(st)
        rows.append(r)
    (D / "mu_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    fmt = lambda v: "-" if v is None or v != v else f"{v:.3f}"  # noqa: E731
    L = ["# mu = (1+sigma) lambda_max(sym dD/dx) along learned EDM trajectories", ""]
    for r in rows:
        L += [f"## {r['run']} (n={r['n']}, off-atom {r['off_frac']:.3f})", "",
              "| sigma | t | median mu off | median mu on | frac mu<1 off | frac mu<1 on | median mu* exact | AUC mu |",
              "|---|---|---|---|---|---|---|---|"]
        for s in r["steps"]:
            L.append(f"| {s['sigma']:.4g} | {s['t']:.4f} | {fmt(s['mu_learned_med_off'])} | {fmt(s['mu_learned_med_on'])} | "
                     f"{fmt(s['frac_mu_below_1_off'])} | {fmt(s['frac_mu_below_1_on'])} | {fmt(s['mu_exact_med'])} | "
                     f"{fmt(s['auc_mu_learned'])} |")
        L.append("")
        if any("mu_min_med_off" in s or "rho_med_off" in s for s in r["steps"]):
            L += [f"precond: {r['precond']}; mu_min = (1+sigma) lambda_min(sym J_D); rho = 1 - lambda_max(sym J_D)/c_skip, "
                  "the share of the exact field's contraction (exact: rho = 1) carried by the raw network", "",
                  "| sigma | t | median mu_min off | median mu_min on | median rho off | median rho on | median rho/sigma off | AUC rho |",
                  "|---|---|---|---|---|---|---|---|"]
            for s in r["steps"]:
                L.append(f"| {s['sigma']:.4g} | {s['t']:.4f} | {fmt(s.get('mu_min_med_off'))} | {fmt(s.get('mu_min_med_on'))} | "
                         f"{fmt(s.get('rho_med_off'))} | {fmt(s.get('rho_med_on'))} | {fmt(s.get('rho_over_sigma_med_off'))} | "
                         f"{fmt(s.get('auc_rho'))} |")
            L.append("")
    (D / "MU_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network"); ap.add_argument("--edm-repo")
    ap.add_argument("--cifar-root", default="data"); ap.add_argument("--data"); ap.add_argument("--indices")
    ap.add_argument("--n-per-class", type=int, default=20); ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--steps", type=int, default=18)
    ap.add_argument("--record-steps", default="9,11,13,15,17", help="sampler step indices (18-step schedule: "
                    "9 ~ t 0.34, 11 ~ 0.63, 13 ~ 0.88, 15 ~ 0.98, 17 ~ 0.998)")
    ap.add_argument("--iters", type=int, default=20); ap.add_argument("--jvp", choices=("func", "dvjp", "fd"), default="func")
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
