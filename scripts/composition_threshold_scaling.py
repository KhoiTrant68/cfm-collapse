"""Basin probability of the midpoint just above the threshold (Theorem thm:composition).

Symmetric two-atom case: atoms {-1, +1}, averaged priors with log-odds +-2B, uniform unconditional
prior, guidance w = (1 + delta) w_c with w_c = 1/sinh^2 B. Near s = 0 the profile function is
F(s) = s (s^2 - delta) / cosh^2 B + O(s^5 + delta s^3), and with sigma = s / sqrt(delta) and
e^{2 theta} = beta / (delta cosh^2 B) the s-equation tends to the parameter-free equation

    d sigma / d theta = e^{2 theta} sigma (sigma^2 - 1) + sigma,

whose solutions behave like C e^theta as theta -> -inf. In the linear regime x = x0 e^{-tau}, so
sigma = x0 cosh(B) e^theta / delta, and the heuristic prediction is a basin (-x*, x*) with

    x* = C* delta / cosh B + o(delta),   P_0 = 2 phi(0) C* delta / cosh B + o(delta),

C* the separatrix value of the limit equation. This script computes C* by bisection, with the
exact stopping rule e^{2 theta}(1 - sigma^2) > 1, sigma < 1 (then sigma decreases forever) or
sigma > 1 (then it increases forever), and compares the prediction with the exact basin of
scripts/composition_counterexample.py. The asymptotic law is a conjecture checked numerically,
not a theorem of the paper.

    python -u -m scripts.composition_threshold_scaling
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import ndtr

from scripts.composition_counterexample import boundary, classifier, make_F, roots

OUT = pathlib.Path("results/composition_threshold_scaling_20261107")
THETA0 = -30.0
DELTAS = (0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 0.0003)
B_LIST = (1.0, 2.0, 3.0)


def limit_class(C, rtol=1e-12, atol=1e-14):
    """+1 if the limit-equation solution with sigma ~ C e^theta escapes, 0 if it is captured."""
    # In u = log sigma: du/dtheta = e^{2 theta}(e^{2u} - 1) + 1, well scaled from theta = THETA0.
    def rhs(th, y):
        return [math.exp(2 * th) * math.expm1(2 * y[0]) + 1]
    th, u = THETA0, math.log(C) + THETA0
    while True:
        if u > 0:
            return 1
        if -math.exp(2 * th) * math.expm1(2 * u) > 1:
            return 0
        sol = solve_ivp(rhs, (th, th + 0.25), [u], method="Radau", rtol=rtol, atol=atol)
        assert sol.success, sol.message
        th, u = sol.t[-1], sol.y[0, -1]


def separatrix(theta1=8.0, rtol=1e-12, atol=1e-14):
    """C* by integrating the separatrix backward from its slow branch sigma^2 = 1 - e^{-2 theta}.

    Backward in theta the branch attracts at rate about 2 e^{2 theta}, so starting on it at
    theta1 the error is damped; as theta -> -inf, u - theta tends to log C*.
    """
    def rhs(th, y):
        return [math.exp(2 * th) * math.expm1(2 * y[0]) + 1]
    u1 = 0.5 * math.log1p(-math.exp(-2 * theta1))
    sol = solve_ivp(rhs, (theta1, THETA0), [u1], method="Radau", rtol=rtol, atol=atol)
    assert sol.success, sol.message
    return math.exp(sol.y[0, -1] - THETA0)


def exact_basin(B, delta):
    w = (1 + delta) / math.sinh(B) ** 2
    F, dF = make_F(w, (0.5, 0.5), (B, -B), 0.0)
    label = classifier(F, roots(F, dF))
    hi = boundary(F, label, 0.0, 6.0)
    lo = boundary(F, label, 0.0, -6.0)
    return lo, hi, float(ndtr(hi) - ndtr(lo))


def main() -> int:
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    c_star = separatrix()
    c_check = {"theta1_6": separatrix(theta1=6.0), "theta1_10": separatrix(theta1=10.0),
               "rtol_1e-10": separatrix(rtol=1e-10, atol=1e-12)}
    # Forward classification on both sides of C*: below must be captured, above must escape.
    c_check["forward_below_1e-3"] = limit_class(c_star * (1 - 1e-3))
    c_check["forward_above_1e-3"] = limit_class(c_star * (1 + 1e-3))
    print(f"C* = {c_star:.12f}; checks {c_check}", flush=True)
    rows = []
    for B in B_LIST:
        for d in DELTAS:
            t0 = time.time()
            lo, hi, P = exact_basin(B, d)
            pred_x = c_star * d / math.cosh(B)
            pred_P = 2 * c_star * d / math.cosh(B) / math.sqrt(2 * math.pi)
            row = {"B": B, "delta": d, "basin_low": lo, "basin_high": hi, "P0": P,
                   "x_star_pred": pred_x, "P0_pred": pred_P, "ratio_x": hi / pred_x,
                   "ratio_P": P / pred_P, "seconds": time.time() - t0}
            rows.append(row)
            print(f"B={B:g} delta={d:g}: P0={P:.6e} pred={pred_P:.6e} ratio={P/pred_P:.5f} "
                  f"x*={hi:.6e} sym={-lo/hi:.12f}", flush=True)
    summary = {"script": "scripts/composition_threshold_scaling.py", "C_star": c_star,
               "C_star_check": c_check, "theta0": THETA0, "rows": rows, "python": sys.version,
               "numpy": np.__version__, "seconds": time.time() - start}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {OUT / 'summary.json'} in {summary['seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
