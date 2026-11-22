"""Signed combinations of exact fields at a two-atom tie (paper_theory, Section sec:conjunction).

    uv run --no-sync python -m scripts.signed_combinations_check

At a tie of two atoms a, b, with nu = (a-b)/2 and sigma the blown-up coordinate along nu, a field
sum_k c_k v_{p_k} with constant coefficients summing to one has the profile function

    F(sigma) = sum_k c_k tanh(sigma + B_k),   B_k = (1/2) log(p_k(a)/p_k(b)),

and at a root F'(sigma*) = 1 - sum_k c_k m_k^2 with m_k = tanh(sigma* + B_k). Theorem thm:spectral
in one dimension says that the midpoint has positive probability exactly when some root has
F' < 0 (all roots hyperbolic). Proposition prop:twoatom gives necessary conditions; this script

  1. tests them on random combinations (K = 2..5 priors) by locating downward zero crossings;
  2. maps the three-prior family B = (B, 0, -B) over the two conditional coefficients;
  3. computes the probability of the midpoint under N(0,1) for named configurations, with the
     stiff integrator and proof-based stopping rules of scripts/composition_counterexample.py.

Root location on a grid and stiff integration are numerical; nothing here is part of a proof.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from scripts.composition_counterexample import boundary, classifier, endpoint, roots

OUT = Path("results/theory_signed_combinations_20261121")
GRID = np.linspace(-30.0, 30.0, 24001) + 0.5 * 60.0 / 24000     # offset: no grid point at 0


def down_roots(c, B):
    F = (np.asarray(c)[:, None] * np.tanh(GRID[None] + np.asarray(B)[:, None])).sum(0)
    i = np.where((F[:-1] > 0) & (F[1:] < 0))[0]
    return GRID[i]


def random_test(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    tested = hits = viol_a = viol_b = 0
    for _ in range(n):
        K = int(rng.integers(2, 6)); B = np.sort(rng.uniform(-4, 4, K))
        c = rng.normal(size=K) * rng.uniform(0.5, 6)
        if abs(c.sum()) < 0.2:
            continue
        c = c / c.sum(); tested += 1
        if len(down_roots(c, B)):
            hits += 1
            viol_a += int(not (c[1:-1] < 0).any())
            viol_b += int(K == 3 and not (c[1] < 0 < c[0] and c[2] > 0))
    return {"tested": tested, "with_attracting_profile": hits,
            "violations_interior_negative": viol_a, "violations_three_prior_sign_pattern": viol_b}


def phase_map(B, cs):
    """attracting[i, j] for c_minus = cs[i] (prior favouring b), c_plus = cs[j] (favouring a)."""
    out = np.zeros((len(cs), len(cs)), bool)
    for i, cm in enumerate(cs):
        for j, cp in enumerate(cs):
            out[i, j] = len(down_roots((cp, 1 - cp - cm, cm), (B, 0.0, -B))) > 0
    return out


def basin(name, c, B):
    c, B = np.asarray(c, float), np.asarray(B, float)
    assert abs(c.sum() - 1) < 1e-12

    def F(s):
        return float(np.sum(c * np.tanh(s + B)))

    def dF(s):
        return float(np.sum(c / np.cosh(s + B) ** 2))
    rts = roots(F, dF)
    label = classifier(F, rts)
    row = {"name": name, "c": c.tolist(), "B": B.tolist(), "roots": [{"s": r, "dF": d} for r, d in rts]}
    if not any(d < 0 for _, d in rts):
        row["near_zero"] = {str(x0): endpoint(x0, F, label)[0] for x0 in (-1e-6, 1e-6, -0.5, 0.5)}
        row["midpoint_probability"] = 0.0
        return row
    inside = None
    for x0 in sorted(np.linspace(-3, 3, 241), key=abs):
        if endpoint(x0, F, label)[0] == 0:
            inside = float(x0); break
    if inside is None:
        row["midpoint_probability"] = 0.0
        return row
    lo, hi = boundary(F, label, inside, -6.0), boundary(F, label, inside, 6.0)
    row.update(basin_low=lo, basin_high=hi, midpoint_probability=float(ndtr(hi) - ndtr(lo)))
    return row


def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"script": "scripts/signed_combinations_check.py", "random_test": random_test()}
    print(res["random_test"], flush=True)

    cs = np.round(np.linspace(-1.0, 4.0, 101), 4)
    maps = {f"B{B:g}": phase_map(B, cs) for B in (1.0, 2.0)}
    np.savez_compressed(OUT / "phase_map.npz", cs=cs, **maps)
    res["phase_map"] = {k: {"attracting_cells": int(v.sum()),
                            "attracting_with_a_nonpositive_condition":
                                int(v[np.ix_(cs <= 0, np.ones_like(cs, bool))].sum()
                                    + v[np.ix_(np.ones_like(cs, bool), cs <= 0)].sum())}
                        for k, v in maps.items()}
    print(res["phase_map"], flush=True)

    B1 = 1.0; wc = 1 / math.sinh(B1) ** 2; w = 2 * wc
    configs = [
        # conjunction of two conditions, equal weights: Theorem thm:composition (exact value 0.4059)
        ("conjunction_equal_B1_w2wc", ((1 + w) / 2, -w, (1 + w) / 2), (B1, 0.0, -B1)),
        # conjunction with unequal weights on the two conditions
        ("conjunction_unequal_B2", (1.2, -1.0, 0.8), (2.0, 0.0, -2.0)),
        # positive prompt for a, negative prompt for b, unconditional: v_u + 3(v_a - v_u) - 1(v_b - v_u)
        ("negative_prompt_opposite", (3.0, -1.0, -1.0), (2.0, 0.0, -2.0)),
        # negative prompt as implemented by substitution: v_n + 3(v_a - v_n) (two fields)
        ("negative_prompt_substituted", (3.0, -2.0), (2.0, -2.0)),
        # positive prompt for a, negative prompt milder towards a, unconditional: interior prior negated
        ("negative_prompt_milder", (0.91, -4.0, 4.09), (2.0, 0.25, 0.0)),
    ]
    rows = []
    for name, c, B in configs:
        rows.append(basin(name, c, B))
        print(name, rows[-1]["midpoint_probability"], flush=True)
    res["basins"] = rows
    res["seconds"] = time.time() - t0
    (OUT / "summary.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"wrote {OUT / 'summary.json'} in {res['seconds']:.0f}s")


if __name__ == "__main__":
    main()
