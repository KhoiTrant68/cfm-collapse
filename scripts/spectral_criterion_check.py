"""Numerical check of the spectral sink/saddle criterion for guided label averaging.

The criterion (Appendix B, profile classification) concerns a non-atom candidate z
whose nearest atoms are tied. With xi = beta(t) P_L(x - t z) and the fast clock
du = beta dtau, the exact flow is asymptotically du xi = M(xi) - z, and a finite
root xi* of M = z attracts an open set of sources when H = D_L M(xi*) is negative
definite on L; when H is hyperbolic with a positive eigenvalue its basin is null.

Every configuration here puts all atoms on the unit sphere around z = 0, so every
atom is in the tie set and the blown-up equation is exact, with no off-tie term:

    dx/dtau = M(beta x) - x            (all t),
    dxi/du  = M(xi) + xi / (t beta),   dtau/du = 1/beta   (after t0 = 1/2).

M is the signed combination (1+w) * mean_k(Gibbs mean of prior k) - w * (uniform
Gibbs mean). For each configuration the script computes H = D M(0) at the profile
xi* = 0, its eigenvalues and trace, and the predicted class (sink / saddle /
source), and integrates 2048 (or 512) Gaussian sources to a sequence of fast
times u. It reports the fraction whose profile stays bounded (|xi| < 5), which
estimates Pr(X_1 = z), and the fraction that escapes (|xi| > u/20). This is a
finite-time numerical illustration, not part of any proof.

Configurations:
  tri2      d=2, equilateral triangle, three priors each favouring one vertex
            (log-weight B), averaged uniformly; isotropic H.
  simplex8  d=8, regular simplex with 9 vertices, same construction; isotropic H.
  rect2     d=2, rectangle (+-2, +-1), two product priors with per-axis
            log-odds +-(2B1, 2B2), B1=2, B2=0.5. At w=1 H is a saddle with
            NEGATIVE trace (the trace test of Lemma B.3 is silent there).
  cube8     d=8, hypercube with half-widths (2,2,2,2,1,1,1,1), 256 atoms scaled to
            the unit sphere, product priors with B=(2,2,2,2,.5,.5,.5,.5); at w=1
            a saddle with four positive eigenvalues and negative trace.

Usage:  uv run --no-project --with numpy --with scipy python scripts/spectral_criterion_check.py
"""
from __future__ import annotations

import itertools
import json
import math
import pathlib
import time

import numpy as np
from scipy.integrate import solve_ivp

OUT = pathlib.Path("results/theory_spectral_20261020")
U_CHECK = (1e1, 1e2, 1e3, 1e4)
T0 = 0.5


def simplex(n_vertices: int) -> np.ndarray:
    """Regular simplex on the unit sphere of R^{n-1}, centred at 0."""
    e = np.eye(n_vertices) - 1.0 / n_vertices
    u, s, _ = np.linalg.svd(e)
    v = e @ u[:, : n_vertices - 1]
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def vertex_priors(n: int, B: float) -> np.ndarray:
    logp = np.full((n, n), 0.0)
    logp[np.arange(n), np.arange(n)] = B
    return logp - np.log(np.exp(logp).sum(1, keepdims=True))


def product_config(half: np.ndarray, B: np.ndarray):
    signs = np.array(list(itertools.product((-1.0, 1.0), repeat=len(half))))
    atoms = signs * half
    scale = np.linalg.norm(half)
    atoms = atoms / scale                      # all on the unit sphere
    logp = np.stack([(+1) * signs @ B, (-1) * signs @ B])   # log-odds +-2B per axis
    logp = logp - np.log(np.exp(logp).sum(1, keepdims=True))
    return atoms, logp, scale


def gibbs_means(xi: np.ndarray, atoms: np.ndarray, logp: np.ndarray) -> np.ndarray:
    """xi: (n, d); logp: (K, N). Returns (K, n, d) Gibbs means."""
    logits = logp[:, None, :] + (xi @ atoms.T)[None, :, :]
    logits -= logits.max(-1, keepdims=True)
    w = np.exp(logits)
    w /= w.sum(-1, keepdims=True)
    return w @ atoms


class Field:
    def __init__(self, atoms, cond_logp, w):
        self.atoms, self.w = atoms, w
        N = len(atoms)
        self.logp = np.vstack([cond_logp, np.full((1, N), -math.log(N))])
        K = len(cond_logp)
        self.c = np.concatenate([np.full(K, (1 + w) / K), [-w]])

    def M(self, xi):
        return np.tensordot(self.c, gibbs_means(xi, self.atoms, self.logp), axes=1)

    def H0(self):
        h = np.zeros((self.atoms.shape[1],) * 2)
        for ck, lp in zip(self.c, self.logp):
            q = np.exp(lp)
            mu = q @ self.atoms
            h += ck * ((self.atoms * q[:, None]).T @ self.atoms - np.outer(mu, mu))
        return h


def run(field: Field, n_src: int, seed: int) -> dict:
    d = field.atoms.shape[1]
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n_src, d))
    # phase 1: x in tau-time, RK4, from t=0 to t0
    tau0 = -math.log(1 - T0)
    n1 = 2000
    h = tau0 / n1

    def f1(x, tau):
        t = 1 - math.exp(-tau)
        beta = t / (1 - t) ** 2
        return field.M(beta * x) - x

    tau = 0.0
    for _ in range(n1):
        k1 = f1(x, tau); k2 = f1(x + h / 2 * k1, tau + h / 2)
        k3 = f1(x + h / 2 * k2, tau + h / 2); k4 = f1(x + h * k3, tau + h)
        x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        tau += h
    beta0 = T0 / (1 - T0) ** 2
    y0 = np.concatenate([(beta0 * x).ravel(), [tau0]])

    def f2(u, y):
        xi = y[:-1].reshape(n_src, d)
        tau = y[-1]
        t = 1 - math.exp(-tau)
        beta = t / (1 - t) ** 2
        dxi = field.M(xi) + xi / (t * beta)
        return np.concatenate([dxi.ravel(), [1.0 / beta]])

    sol = solve_ivp(f2, (0.0, U_CHECK[-1]), y0, method="RK45", rtol=1e-8, atol=1e-10,
                    t_eval=U_CHECK)
    assert sol.success, sol.message
    rows = []
    for j, u in enumerate(sol.t):
        xi = sol.y[:-1, j].reshape(n_src, d)
        nrm = np.linalg.norm(xi, axis=1)
        tau = sol.y[-1, j]
        rows.append({"u": float(u), "gap_1_minus_t": float(math.exp(-tau)),
                     "frac_bounded": float((nrm < 5).mean()),
                     "frac_escaped": float((nrm > u / 20).mean()),
                     "median_norm_bounded": float(np.median(nrm[nrm < 5])) if (nrm < 5).any() else None})
    return {"n_src": n_src, "seed": seed, "nfev": int(sol.nfev), "checkpoints": rows}


def classify(h: np.ndarray, L_dim: int) -> dict:
    ev = np.linalg.eigvalsh(h)
    ev = ev[np.argsort(-np.abs(ev))][:L_dim]      # restrict to the tangent space
    ev = np.sort(ev)
    n_pos = int((ev > 1e-9).sum())
    n_zero = int((np.abs(ev) <= 1e-9).sum())
    kind = "nonhyperbolic" if n_zero else ("sink" if n_pos == 0 else
                                           ("source" if n_pos == L_dim else "saddle"))
    return {"eigenvalues": ev.round(6).tolist(), "trace": float(ev.sum()),
            "n_positive": n_pos, "class": kind}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    B = 2.0
    out = {"configs": []}
    t_start = time.time()

    # isotropic simplices: predicted threshold w_c = (1 - m^2)/m^2
    for name, n_v, n_src in (("tri2", 3, 2048), ("simplex8", 9, 2048)):
        atoms = simplex(n_v)
        m = (math.exp(B) - 1) / (math.exp(B) + n_v - 1)
        wc = (1 - m * m) / (m * m)
        for ratio in (0.5, 0.9, 1.1, 2.0, 5.0):
            fld = Field(atoms, vertex_priors(n_v, B), ratio * wc)
            pred = classify(fld.H0(), atoms.shape[1])
            res = run(fld, n_src, seed=11)
            out["configs"].append({"name": name, "d": atoms.shape[1], "N": n_v, "B": B,
                                   "w_over_wc": ratio, "w": ratio * wc, "w_c_formula": wc,
                                   "prediction": pred, "result": res})
            print(name, ratio, pred["class"], [r["frac_bounded"] for r in res["checkpoints"]],
                  f"{time.time() - t_start:.0f}s", flush=True)

    # anisotropic products: saddle with negative trace at w=1, sink at w=5
    for name, half, Bv, n_src in (
            ("rect2", np.array([2.0, 1.0]), np.array([2.0, 0.5]), 2048),
            ("cube8", np.array([2.0] * 4 + [1.0] * 4), np.array([2.0] * 4 + [0.5] * 4), 512)):
        atoms, logp, scale = product_config(half, Bv)
        for w in (1.0, 5.0):
            fld = Field(atoms, logp, w)
            pred = classify(fld.H0(), atoms.shape[1])
            res = run(fld, n_src, seed=11)
            out["configs"].append({"name": name, "d": atoms.shape[1], "N": len(atoms),
                                   "B_axes": Bv.tolist(), "half_widths": half.tolist(), "w": w,
                                   "prediction": pred, "result": res})
            print(name, w, pred["class"], pred["trace"], [r["frac_bounded"] for r in res["checkpoints"]],
                  f"{time.time() - t_start:.0f}s", flush=True)

    (OUT / "summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", OUT / "summary.json")


if __name__ == "__main__":
    main()
