"""Midpoint probability over the three-prior family at a two-atom tie (data for Figure fig:signed).

    PYTHONPATH=.:scripts python scripts/signed_combinations_probability.py [--workers 48]

The family of Figure fig:signed and scripts/signed_combinations_check.py: atoms -1, +1, source N(0,1),
three priors with restricted log-odds 2B(p) = 2B, 0, -2B (a condition favouring a, the
unconditional field, a condition favouring b) and coefficients c_+, 1 - c_+ - c_-, c_-. The profile
function is F(s) = c_+ tanh(s + B) + (1 - c_+ - c_-) tanh s + c_- tanh(s - B). For every (c_+, c_-)
on a 0.1 grid of [-1, 4]^2 this script computes the probability under N(0,1) that the exact flow
ends at the midpoint 0, with the machinery of scripts/composition_counterexample.py (the paper's
Table tab:composition): roots of F, stiff Radau integration with the proof-based stopping rules,
and bisection of the basin interval, here to absolute tolerance 1e-7 in x_0. Where F has no root
with negative slope the probability is 0 by Theorem thm:spectral (one dimension: no sink profile),
and no integration is done. An attracting root whose basin misses the 241-point search grid of
[-3, 3] (spacing 0.025) is reported as 0 and counted. B = 1 and B = 2.

Writes results/theory_signed_probability_20261121/{probability_B1.npz, probability_B2.npz,
summary.json}. Numerical, not part of a proof.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from scripts.composition_counterexample import boundary, classifier, endpoint, roots

OUT = Path("results/theory_signed_probability_20261121")
CS = np.round(np.linspace(-1.0, 4.0, 51), 4)
TOL = 1e-7


def make(cp: float, cm: float, B: float):
    c = np.array([cp, 1.0 - cp - cm, cm])
    Bs = np.array([B, 0.0, -B])

    def F(s):
        return float(np.sum(c * np.tanh(s + Bs)))

    def dF(s):
        return float(np.sum(c / np.cosh(s + Bs) ** 2))
    return F, dF


def cell(args):
    cp, cm, B = args
    F, dF = make(cp, cm, B)
    rts = roots(F, dF)
    if not any(d < 0 for _, d in rts):
        return {"cp": cp, "cm": cm, "sink": False, "p": 0.0}
    label = classifier(F, rts)
    inside = None
    for x0 in sorted(np.linspace(-3, 3, 241), key=abs):
        if endpoint(float(x0), F, label)[0] == 0:
            inside = float(x0)
            break
    if inside is None:
        return {"cp": cp, "cm": cm, "sink": True, "p": 0.0, "missed": True}
    lo = boundary(F, label, inside, -6.0, tol=TOL)
    hi = boundary(F, label, inside, 6.0, tol=TOL)
    return {"cp": cp, "cm": cm, "sink": True, "p": float(ndtr(hi) - ndtr(lo)), "lo": lo, "hi": hi}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=48)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"script": "scripts/signed_combinations_probability.py", "grid": CS.tolist(), "tol": TOL}
    for B in (1.0, 2.0):
        t0 = time.time()
        jobs = [(float(cp), float(cm), B) for cm in CS for cp in CS]
        with ProcessPoolExecutor(args.workers) as ex:
            res = list(ex.map(cell, jobs, chunksize=1))
        P = np.array([r["p"] for r in res]).reshape(len(CS), len(CS))      # rows c_-, columns c_+
        sink = np.array([r["sink"] for r in res]).reshape(len(CS), len(CS))
        missed = int(sum(r.get("missed", False) for r in res))
        np.savez_compressed(OUT / f"probability_B{B:g}.npz", cs=CS, P=P, sink=sink)
        i = int(np.argmin(np.abs(CS - 1.2))); j = int(np.argmin(np.abs(CS - 0.8)))
        summary[f"B{B:g}"] = {"cells": int(P.size), "sink_cells": int(sink.sum()),
                              "positive_cells": int((P > 0).sum()), "missed_sinks": missed,
                              "max_p": float(P.max()), "seconds": time.time() - t0}
        print(B, summary[f"B{B:g}"], flush=True)
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
