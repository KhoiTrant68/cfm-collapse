"""Guided label averaging with the exact field on CIFAR-10 pairs (Theorem thm:composition at d = 3072).

The instance is the EXP-3 CIFAR-10 problem (N = 2000, seed 0, bottom-half inpainting): atoms x^k
are training images in R^3072 and labels y^k their visible top halves in R^1536. For a pair (i, j)
whose midpoint z = (x^i + x^j)/2 is a candidate limit (every other atom is farther from z than
r = |x^i - x^j|/2), average the exact conditional fields at the queries y^i and y^j, with Gaussian
label noise h, and apply guidance:

    m_w(x,t) = (1+w) [m(x,t; y^i) + m(x,t; y^j)] / 2 - w m_unc(x,t),     dx/dtau = m_w - x,

with tau = -log(1-t) and posterior weights q_k ~ p_k(y) exp((t<x,x^k> - t^2|x^k|^2/2)/(1-t)^2).
Once every one of the three posteriors puts all but `--handoff` of its mass on {i, j}, the flow
along e = (x^i - x^j)/(2r) is exactly the two-atom flow of Theorem thm:composition: with
q = <x - t z, e> and s = beta r q (beta = t/(1-t)^2),

    dq/dtau = r F_w(s) - q,    F_w(s) = (1+w)/2 [tanh(s+B) + tanh(s-B)] - w tanh s,

with B = |y^i - y^j|^2 / (4 h^2); the label bandwidth h is set from the target B. This script
integrates the full field per source with an adaptive embedded Runge-Kutta method (Bogacki-
Shampine 3(2)) until the posterior concentrates on the pair (hand-off to the exact one-dimensional
equation, integrated with Radau and classified by the roots of F_w) or on a single atom (an atom
endpoint, which guidance keeps). Sources that do neither by `--tau-max` are reported as unresolved.

    python -m scripts.cifar_composition_exact --data cifar2000_seed0.npz --pair 292 1938 --B 1 \
        --ratios 0.5 2 5 10 --sources 256 --out results/cifar_composition_exact_20261105
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import time

import numpy as np
import torch
from scipy.integrate import solve_ivp


def F(s, w, B):
    return (1 + w) / 2 * (np.tanh(s + B) + np.tanh(s - B)) - w * np.tanh(s)


def classify_1d(q0: float, tau0: float, r: float, w: float, B: float, tau_end: float = 40.0):
    """Exact two-atom flow from (q0, tau0): 'mid' if it ends at the tie, else '+' / '-'."""
    wc = 1 / math.sinh(B) ** 2
    s_u = math.acosh(math.sqrt(w) * math.sinh(B)) if w > wc else 0.0

    def rhs(tau, y):
        u = math.exp(-tau)                     # 1 - t, kept exact
        beta = (1 - u) / u ** 2
        s = beta * r * y[0]
        return [r * F(s, w, B) - y[0]]

    def jac(tau, y):
        u = math.exp(-tau)                     # 1 - t, kept exact
        beta = (1 - u) / u ** 2
        s = beta * r * y[0]
        with np.errstate(over="ignore"):
            dF = (1 + w) / 2 * (1 / np.cosh(s + B) ** 2 + 1 / np.cosh(s - B) ** 2) - w / np.cosh(s) ** 2
        return [[r * dF * beta * r - 1]]

    sol = solve_ivp(rhs, (tau0, tau_end), [q0], method="Radau", jac=jac, rtol=1e-10, atol=1e-14)
    u = math.exp(-sol.t[-1])
    s_end = (1 - u) / u ** 2 * r * sol.y[0, -1]
    if w > wc and abs(s_end) < s_u:
        return "mid", float(s_end)
    return ("+" if s_end > 0 else "-"), float(s_end)


class Field:
    def __init__(self, X, Y, i, j, h, device):
        self.X = X.to(device)                                  # (N, d) float64
        self.Xn2 = (self.X ** 2).sum(1)                        # (N,)
        Y = Y.to(device)
        lp = lambda y: -((Y - y) ** 2).sum(1) / (2 * h ** 2)
        self.logp = torch.stack([lp(Y[i]), lp(Y[j]), torch.zeros(len(Y), device=device, dtype=X.dtype)])
        self.i, self.j = i, j

    def posteriors(self, x, t, u=None):
        """x (S,d), t (S,) -> weights (3, S, N) for the fields at y^i, y^j and unconditional."""
        u = (1 - t)[:, None] if u is None else u[:, None]
        a = (t[:, None] * (x @ self.X.T) - 0.5 * t[:, None] ** 2 * self.Xn2[None]) / u ** 2
        return torch.softmax(self.logp[:, None, :] + a[None], dim=-1)

    def rhs(self, x, tau, w):
        u = torch.exp(-tau)
        q = self.posteriors(x, 1 - u, u)
        m = q @ self.X                                         # (3, S, d)
        return (1 + w) / 2 * (m[0] + m[1]) - w * m[2] - x, q


def run(args):
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    D = np.load(args.data)
    X = torch.from_numpy(D["X"]).double()
    Y = torch.from_numpy(D["Y"]).double()
    i, j = args.pair
    z = (X[i] + X[j]) / 2
    r = float((X[i] - X[j]).norm() / 2)
    e = (X[i] - X[j]) / (2 * r)
    others = torch.ones(len(X), dtype=torch.bool); others[[i, j]] = False
    margin = float(((X[others] - z) ** 2).sum(1).min() / r ** 2)
    dy2 = float(((Y[i] - Y[j]) ** 2).sum())
    h = math.sqrt(dy2 / (4 * args.B))
    wc = 1 / math.sinh(args.B) ** 2
    field = Field(X, Y, i, j, h, dev)
    g = torch.Generator().manual_seed(args.source_seed)
    x0 = torch.randn(args.sources, X.shape[1], generator=g, dtype=torch.float64)
    out = {"pair": [i, j], "r": r, "margin_sq": margin, "dy2": dy2, "B": args.B, "h": h, "w_c": wc,
           "sources": args.sources, "source_seed": args.source_seed, "handoff": args.handoff,
           "rtol": args.rtol, "tau_max": args.tau_max, "device": str(dev), "rows": []}
    ez, ee = z.to(dev), e.to(dev)
    for ratio in args.ratios:
        w = ratio * wc
        start = time.time()
        x = x0.to(dev).clone()
        tau = torch.full((len(x),), args.tau0, dtype=torch.float64, device=dev)
        dt = torch.full_like(tau, 1e-3)
        active = torch.ones(len(x), dtype=torch.bool, device=dev)
        result = ["unresolved"] * len(x)
        detail = [None] * len(x)
        k1, _ = field.rhs(x, tau, w)
        steps = 0
        while active.any() and steps < args.max_steps:
            steps += 1
            idx = active.nonzero().squeeze(1)
            xa, ta, ha, f1 = x[idx], tau[idx], dt[idx][:, None], k1[idx]
            f2, _ = field.rhs(xa + 0.5 * ha * f1, ta + 0.5 * ha[:, 0], w)
            f3, _ = field.rhs(xa + 0.75 * ha * f2, ta + 0.75 * ha[:, 0], w)
            xn = xa + ha * (2 * f1 + 3 * f2 + 4 * f3) / 9
            f4, qn = field.rhs(xn, ta + ha[:, 0], w)
            err = ha * (-5 * f1 / 72 + f2 / 12 + f3 / 9 - f4 / 8)
            scale = args.atol + args.rtol * torch.maximum(xa.abs(), xn.abs())
            en = (err / scale).pow(2).mean(1).sqrt()
            ok = en <= 1
            fac = torch.clamp(0.9 * en.clamp_min(1e-10) ** (-1 / 3), 0.2, 5.0)
            acc = idx[ok]
            x[acc], tau[acc], k1[acc] = xn[ok], ta[ok] + ha[ok, 0], f4[ok]
            dt[idx] = ha[:, 0] * fac
            # Classification of the accepted states.
            qa = qn[:, ok]                                     # (3, n_acc, N)
            pair_mass = (qa[:, :, i] + qa[:, :, j]).min(0).values
            top = qa.max(-1)
            single = top.values.min(0).values
            same = (top.indices == top.indices[0:1]).all(0)
            for n, s in enumerate(acc.tolist()):
                if same[n] and single[n] > 1 - args.handoff:
                    result[s] = f"atom:{int(top.indices[0, n])}"; active[s] = False
                elif pair_mass[n] > 1 - args.handoff:
                    t = 1 - math.exp(-float(tau[s]))
                    qv = float(((x[s] - t * ez) * ee).sum())
                    lab, s_end = classify_1d(qv, float(tau[s]), r, w, args.B)
                    result[s] = "mid" if lab == "mid" else f"atom:{i if lab == '+' else j}"
                    detail[s] = {"tau_handoff": float(tau[s]), "q": qv, "s_end": s_end}
                    active[s] = False
                elif float(tau[s]) > args.tau_max:
                    active[s] = False
        mid = sum(r_ == "mid" for r_ in result)
        unres = sum(r_ == "unresolved" for r_ in result)
        pair_atoms = sum(r_ in (f"atom:{i}", f"atom:{j}") for r_ in result)
        row = {"ratio": ratio, "w": w, "midpoint": mid / len(result), "unresolved": unres / len(result),
               "pair_atoms": pair_atoms / len(result), "steps": steps, "seconds": time.time() - start,
               "classes": result, "handoff": detail}
        out["rows"].append(row)
        print(f"w/w_c={ratio:g}: midpoint {mid}/{len(result)}, pair atoms {pair_atoms}, "
              f"unresolved {unres}, steps {steps}, {time.time() - start:.0f}s", flush=True)
    p = pathlib.Path(args.out); p.mkdir(parents=True, exist_ok=True)
    (p / f"pair_{i}_{j}_B{args.B:g}.json").write_text(json.dumps(out), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--pair", type=int, nargs=2, required=True)
    ap.add_argument("--B", type=float, default=1.0)
    ap.add_argument("--ratios", type=float, nargs="+", default=[0.5, 2.0, 5.0, 10.0])
    ap.add_argument("--sources", type=int, default=256)
    ap.add_argument("--source-seed", type=int, default=20261105)
    ap.add_argument("--tau0", type=float, default=1e-4)
    ap.add_argument("--tau-max", type=float, default=30.0)
    ap.add_argument("--handoff", type=float, default=1e-12)
    ap.add_argument("--rtol", type=float, default=1e-6)
    ap.add_argument("--atol", type=float, default=1e-9)
    ap.add_argument("--max-steps", type=int, default=200000)
    ap.add_argument("--out", default="results/cifar_composition_exact_20261105")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
