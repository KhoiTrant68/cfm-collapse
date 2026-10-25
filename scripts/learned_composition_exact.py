"""Exact references E1-E4 for scripts/learned_composition.py.

Two atoms {-1, 1}, ell = h = 1, so the query offset u0 is B. In tau = -log(1-t) every exact
field here is dx/dtau = F(s) - x with s = t x/(1-t)^2:

  E1  conditional at the query 0 (= unconditional)    F = tanh s
  E2  label average                                   F = (tanh(s+B) + tanh(s-B))/2
  E3  single-label guidance at +u0                    F = (1+w) tanh(s+B) - w tanh s
  E4  guided label average (Theorem thm:composition)  F = (1+w)(tanh(s+B) + tanh(s-B))/2 - w tanh s

Flows on the line preserve order, so every set computed here is an interval of sources:

  * endpoint basins, with the certified stopping rules of scripts/composition_counterexample.py
    (the midpoint basin of E4 for w > w_c; the split point between the two atoms otherwise);
  * finite-cutoff sets {x0 : |X_{1-eps}(x0)| < delta}, by bisection on the increasing time-(1-eps)
    map, integrated with Radau.

These are numerical evaluations of exact fields, not proofs.

    python -u -m scripts.learned_composition_exact --workers 16
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.special import ndtr

from scripts.composition_counterexample import (ATOL, RTOL, boundary, classifier, endpoint,
                                                make_F, roots)
from scripts.learned_composition import B_LIST, DELTAS, EPS_OUT, R_LIST, beta_of, w_c, x_at

OUT = pathlib.Path("results/learned_composition_20261021/exact")
RTOL_FINITE = 1e-10   # finite-cutoff states; the endpoint basins keep RTOL of the certified rules
LEVEL_TOL = 1e-7      # bisection tolerance on x0 for the finite-cutoff intervals
# At w = w_c the slope at the tie is 0, and rounding gives -1e-16 (B = 1) or -1e-17 (B = 2);
# that must not count as an attracting root. The true slopes elsewhere are >= 1e-3 in size.
SLOPE_TOL = 1e-12


def params(kind, B, w):
    """(w, lam, B_k, B_u) of make_F for each exact arm."""
    if kind == "E1":
        return 0.0, (1.0,), (0.0,), 0.0
    if kind == "E2":
        return 0.0, (0.5, 0.5), (B, -B), 0.0
    if kind == "E3":
        return w, (1.0,), (B,), 0.0
    if kind == "E4":
        return w, (0.5, 0.5), (B, -B), 0.0
    raise ValueError(kind)


def vector_F(w, lam, Bk, Bu):
    """The exact posterior mean F(x, tau) = F_s(beta x) on an array of x, for x_at."""
    lam, Bk = np.asarray(lam, float), np.asarray(Bk, float)

    def F(x, tau):
        s = beta_of(tau) * x
        return (1 + w) * np.tanh(s[:, None] + Bk) @ lam - w * np.tanh(s + Bu)
    return F


def solve_levels(F, symmetric, lo=-6.0, hi=6.0, tol=LEVEL_TOL):
    """x0 with X_{1-eps}(x0) = +-delta for every (eps, delta), by simultaneous bisection on the
    increasing time-(1-eps) maps. With an odd field only +delta is solved."""
    targets = [(i, d, sgn) for i in range(len(EPS_OUT)) for d in DELTAS
               for sgn in ((1,) if symmetric else (-1, 1))]
    level = np.array([sgn * d for _, d, sgn in targets])
    col = np.array([i for i, _, _ in targets])
    a, b = np.full(len(targets), lo), np.full(len(targets), hi)
    ends = x_at([lo, hi], F, rtol=RTOL_FINITE)
    b = np.where(ends[0, col] >= level, lo, b)          # the level is not crossed inside [lo, hi]
    a = np.where(ends[1, col] <= level, hi, a)
    while (b - a).max() > tol:
        live = b - a > tol
        mid = 0.5 * (a + b)
        below = np.zeros(len(targets), bool)
        below[live] = x_at(mid[live], F, rtol=RTOL_FINITE)[np.arange(live.sum()), col[live]] < level[live]
        a = np.where(live & below, mid, a)
        b = np.where(live & ~below, mid, b)
    root = 0.5 * (a + b)
    out = {}
    for (i, d, sgn), r in zip(targets, root):
        out[(i, d, sgn)] = float(r)
        if symmetric:
            out[(i, d, -1)] = -float(r)
    return out


def endpoint_sets(kind, B, r):
    """Midpoint basin, or the split point between the atoms, of one exact arm."""
    w = r * w_c(B) if kind in ("E3", "E4") else 0.0
    F, dF = make_F(*params(kind, B, w))
    rts = roots(F, dF)
    label = classifier(F, rts)
    row = {"arm": kind, "B": B, "r": r, "w": w, "roots": [{"s": a, "dF": d} for a, d in rts]}
    stable = [a for a, d in rts if d < -SLOPE_TOL]
    if stable:
        inside = None
        for x0 in sorted(np.linspace(-3, 3, 241), key=abs):
            if endpoint(x0, F, label)[0] == 0:
                inside = float(x0); break
        if inside is None:
            for x0 in (1e-3, -1e-3, 1e-6, -1e-6, 0.0):
                if endpoint(x0, F, label)[0] == 0:
                    inside = float(x0); break
        if inside is None:
            row.update(basin=None, basin_probability=0.0)
        else:
            lo, hi = boundary(F, label, inside, -6.0), boundary(F, label, inside, 6.0)
            row.update(basin=[lo, hi], basin_probability=float(ndtr(hi) - ndtr(lo)))
        row["split"] = None
    else:
        # No attracting profile: one split point between the sources reaching -1 and +1.
        a, b = -6.0, 6.0
        assert endpoint(a, F, label)[0] == -1 and endpoint(b, F, label)[0] == 1
        while b - a > 1e-10:
            m = 0.5 * (a + b)
            if endpoint(m, F, label)[0] == 1:
                b = m
            else:
                a = m
        row.update(basin=None, basin_probability=0.0, split=0.5 * (a + b))
    return row


def run(job):
    """One exact arm: its endpoint sets and its finite-cutoff intervals."""
    kind, B, r = job
    row = endpoint_sets(kind, B, r)
    row["finite"] = []
    levels = solve_levels(vector_F(*params(kind, B, row["w"])), symmetric=kind != "E3")
    for i, eps in enumerate(EPS_OUT):
        for d in DELTAS:
            lo, hi = levels[(i, d, -1)], levels[(i, d, 1)]
            row["finite"].append({"eps": eps, "delta": d, "interval": [lo, hi],
                                  "probability": float(ndtr(hi) - ndtr(lo))})
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    start = time.time()
    jobs = [("E1", 0.0, 0.0)]
    for B in B_LIST:
        jobs.append(("E2", B, 0.0))
        for r in R_LIST:
            jobs += [("E3", B, r), ("E4", B, r)]
    if args.smoke:
        jobs = [("E4", 1.0, 2.0), ("E2", 1.0, 0.0)]
    with Pool(args.workers) as pool:
        rows = []
        for row in pool.imap_unordered(run, jobs):
            rows.append(row)
            print(row["arm"], row["B"], row["r"], row["basin_probability"], row["split"], flush=True)
    rows.sort(key=lambda r: (r["arm"], r["B"], r["r"]))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"script": "scripts/learned_composition_exact.py", "rtol": RTOL, "atol": ATOL,
               "rtol_finite": RTOL_FINITE, "level_tol": LEVEL_TOL, "slope_tol": SLOPE_TOL,
               "python": sys.version, "seconds": time.time() - start, "rows": rows}
    name = "summary_smoke.json" if args.smoke else "summary.json"
    (OUT / name).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {OUT / name} in {summary['seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
