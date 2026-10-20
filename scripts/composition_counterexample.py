"""Exact two-atom check of guided label averaging (Theorem thm:composition).

Atoms {-1,+1} in R. Conditional priors with log-odds 2*B_k are averaged with
weights lam_k; the unconditional prior has log-odds 2*B_u; guidance strength w.
In tau = -log(1-t) the exact guided field is

    dx/dtau = F(s) - x,  s = t x/(1-t)^2,
    F(s) = (1+w) sum_k lam_k tanh(s+B_k) - w tanh(s+B_u).

After a short burn-in in x, the script integrates s, whose equation is
ds/dtau = beta F(s) + (1+eps/t) s with beta = t/eps^2, and stops at the first
time a sufficient condition from the paper's proofs fixes the limit:

  * s above max(0, largest root of F) (or below min(0, smallest root)): the
    limit is the atom +1 (or -1), because s then moves monotonically away;
  * s within delta of a root s* with F(s*-delta) > 0 > F(s*+delta) and
    beta*min(F(s*-delta), -F(s*+delta)) > (1+eps/t)(|s*|+delta): the limit is
    the midpoint 0 (the moving barrier of the proof).

These rules are exact; their evaluation uses a stiff numerical integrator, so
the output is a numerical check of the theorem, not part of its proof. Flows in
one dimension preserve order, so the basin of 0 is an interval whose endpoints
are found by bisection; its probability is taken under the N(0,1) source.

Usage:  uv run --no-project --with numpy --with scipy python scripts/composition_counterexample.py
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import ndtr

OUT = pathlib.Path("results/theory_composition_20261019")
BURN_IN = 0.5          # tau at which the s-variable takes over
TAU_MAX = 40.0         # beta(40) ~ 5e34; no trajectory here needs that long
CHUNK = 0.25           # stopping rules are checked at the end of each chunk
RTOL, ATOL = 1e-11, 1e-13


def make_F(w, lam, B, Bu):
    lam, B = np.asarray(lam, float), np.asarray(B, float)

    def F(s):
        return (1 + w) * np.sum(lam * np.tanh(s + B)) - w * math.tanh(s + Bu)

    def dF(s):
        return (1 + w) * np.sum(lam / np.cosh(s + B) ** 2) - w / math.cosh(s + Bu) ** 2
    return F, dF


def roots(F, dF, span=60.0, n=24001):
    grid = np.linspace(-span, span, n)
    vals = np.array([F(s) for s in grid])
    out = []
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if fa == 0.0:
            out.append(a)
        elif fa * fb < 0:
            out.append(brentq(F, a, b, xtol=1e-14))
    return [(r, dF(r)) for r in out]


def classifier(F, rts):
    """Return a function tau, s -> label or None using the exact stopping rules."""
    lo, hi = min(r for r, _ in rts), max(r for r, _ in rts)
    barriers = []
    for r, d in rts:
        if d < 0:
            delta = 1e-3
            while delta < 1.0 and F(r - 2 * delta) > 0 > F(r + 2 * delta):
                delta *= 2
            gap = min(F(r - delta), -F(r + delta))
            if gap > 0:
                barriers.append((r, delta, gap))

    def label(tau, s):
        eps = math.exp(-tau); t = -math.expm1(-tau); beta = t / eps ** 2
        # Beyond every root F has the sign of F(+-inf) = +-1, and with s of the
        # same sign both terms of ds/dtau push s further out.
        if s > max(hi, 0.0):
            return 1
        if s < min(lo, 0.0):
            return -1
        for r, delta, gap in barriers:
            if abs(s - r) <= delta and beta * gap > (1 + eps / t) * (abs(r) + delta):
                return 0
        return None
    return label


def endpoint(x0, F, label):
    """Integrate from x0 at t=0; return (label, tau at which it was fixed)."""
    burn = solve_ivp(lambda tau, x: [F(-math.expm1(-tau) * x[0] / math.exp(-2 * tau)) - x[0]],
                     (0.0, BURN_IN), [x0], method="Radau", rtol=RTOL, atol=ATOL)
    assert burn.success, burn.message
    t = -math.expm1(-BURN_IN); s0 = t * burn.y[0, -1] / math.exp(-2 * BURN_IN)

    def rhs(tau, s):
        eps = math.exp(-tau); t = -math.expm1(-tau)
        return [t / eps ** 2 * F(s[0]) + (1 + eps / t) * s[0]]

    # Each stopping condition is forward invariant, so checking it at the end of
    # short chunks loses nothing (an event on a step function would).
    tau, s = BURN_IN, s0
    while label(tau, s) is None and tau < TAU_MAX:
        sol = solve_ivp(rhs, (tau, tau + CHUNK), [s], method="Radau", rtol=RTOL, atol=ATOL)
        assert sol.success, sol.message
        tau, s = sol.t[-1], sol.y[0, -1]
    return label(tau, s), tau


def boundary(F, label, inside, outside, tol=1e-12):
    """Bisection between x0 = inside (limit 0) and x0 = outside (limit an atom)."""
    a, b = inside, outside
    while abs(b - a) > tol * max(1.0, abs(a)):
        m = 0.5 * (a + b)
        if endpoint(m, F, label)[0] == 0:
            a = m
        else:
            b = m
    return 0.5 * (a + b)


def run_config(name, w, lam, B, Bu, probes=(-2.0, -1.0, -0.2, 0.0, 0.2, 1.0, 2.0)):
    F, dF = make_F(w, lam, B, Bu)
    rts = roots(F, dF)
    label = classifier(F, rts)
    row = {"name": name, "w": w, "lam": list(lam), "B": list(B), "B_u": Bu,
           "roots": [{"s": r, "dF": d} for r, d in rts]}
    stable = [r for r, d in rts if d < 0]
    row["probes"] = {str(x0): endpoint(x0, F, label)[0] for x0 in probes}
    if stable:
        # A source inside the basin: the trajectory through s* at late times
        # maps back to some x0; search outward from the probe closest to 0.
        inside = None
        for x0 in sorted(np.linspace(-3, 3, 241), key=abs):
            if endpoint(x0, F, label)[0] == 0:
                inside = float(x0); break
        if inside is None:
            for x0 in (1e-3, -1e-3, 1e-6, -1e-6, 0.0):
                if endpoint(x0, F, label)[0] == 0:
                    inside = float(x0); break
        if inside is not None:
            lo = boundary(F, label, inside, -6.0)
            hi = boundary(F, label, inside, 6.0)
            row.update(basin_low=lo, basin_high=hi,
                       basin_probability=float(ndtr(hi) - ndtr(lo)))
        else:
            row.update(basin_low=None, basin_high=None, basin_probability=0.0)
    else:
        # Only the midpoint tie remains; check that sources near it leave.
        row["near_tie"] = {str(x0): endpoint(x0, F, label)[0]
                           for x0 in (-1e-6, -1e-9, 1e-9, 1e-6)}
        row["basin_probability"] = 0.0
    return row


def main() -> int:
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    # Symmetric family: threshold w_c = 1/sinh(B)^2; closed form for the unstable
    # root s_u with cosh(2 s_u) = 2 w sinh(B)^2 - 1.
    for B in (1.0, 2.0, 3.0):
        wc = 1 / math.sinh(B) ** 2
        for ratio in (0.5, 0.9, 1.1, 2.0, 10.0):
            w = ratio * wc
            row = run_config(f"symmetric_B{B:g}_w{ratio:g}wc", w, (0.5, 0.5), (B, -B), 0.0)
            row.update(w_c=wc, w_over_wc=ratio, dF0=(1 + w) / math.cosh(B) ** 2 - w)
            arg = 2 * w * math.sinh(B) ** 2 - 1
            row["s_u_closed_form"] = 0.5 * math.acosh(arg) if arg > 1 else None
            rows.append(row); print(row["name"], row.get("basin_probability"), flush=True)
        for w in (1.0, 3.0):
            row = run_config(f"symmetric_B{B:g}_w{w:g}", w, (0.5, 0.5), (B, -B), 0.0)
            row.update(w_c=wc, w_over_wc=w / wc, dF0=(1 + w) / math.cosh(B) ** 2 - w)
            arg = 2 * w * math.sinh(B) ** 2 - 1
            row["s_u_closed_form"] = 0.5 * math.acosh(arg)
            rows.append(row); print(row["name"], row.get("basin_probability"), flush=True)
    # Perturbations away from symmetry (open-set statement).
    for name, w, lam, B, Bu in (
        ("weights_0.6_0.4", 1.0, (0.6, 0.4), (2.0, -2.0), 0.0),
        ("unequal_log_odds", 1.0, (0.5, 0.5), (2.0, -1.5), 0.0),
        ("nonuniform_unconditional", 1.0, (0.5, 0.5), (2.0, -2.0), 0.3),
        ("all_three", 1.0, (0.55, 0.45), (2.2, -1.8), -0.2),
    ):
        row = run_config(name, w, lam, B, Bu)
        rows.append(row); print(row["name"], row.get("basin_probability"), flush=True)
    summary = {
        "script": "scripts/composition_counterexample.py",
        "stopping_rules": "exact sufficient conditions; numerical Radau integration",
        "rtol": RTOL, "atol": ATOL, "burn_in_tau": BURN_IN, "tau_max": TAU_MAX,
        "python": sys.version, "numpy": np.__version__,
        "seconds": time.time() - start, "rows": rows,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {OUT/'summary.json'} in {summary['seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
