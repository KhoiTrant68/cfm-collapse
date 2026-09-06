"""Which velocity errors survive the flow, and which the flow annihilates.

Checks the two claims behind the error-survival proposition. At h=0 the exact
field is v*(x,t) = (x^i - x)/(1-t), so for e_t = x_t^v - x_t^* the deviation obeys

    de/dt = Delta(x_t^v, t) - e_t/(1-t)

-- the second term is a contraction, not a growth, and getting that sign wrong
gives a bound five orders of magnitude loose, which is how the slip was caught.
With the integrating factor 1/(1-t),

    |e_t| <= (1-t) int_0^t |Delta(x_s,s)| / (1-s) ds  <=  eps sqrt((1-t) t),

so at truncation t = 1 - delta the deviation is at most eps sqrt(delta), and it
vanishes for ANY bounded L^2 error: the flow's own contraction annihilates bounded
perturbations.

The consequence is the point. Retaining conditional variance requires an error that
is *not* bounded. With |Delta| ~ c (1-t)^{-a} the bound is (c/a)((1-t)^{1-a} - (1-t)),
so the retained deviation vanishes for a < 1, equals c at a = 1, and diverges for
a > 1. A model can only keep variance by getting the field wrong at the same rate
the field itself blows up -- precisely the rate a finite Lipschitz network cannot
represent.

Part A checks the bound; part B locates the threshold at a = 1.

    uv run python scripts/verify_error_survival.py
"""
from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(0)


def integrate(d, xi, x0, delta, dfield, n_steps=200000):
    """Return (|e| at truncation, eps^2 = int |Delta|^2 dt) on a graded grid."""
    ts = 1.0 - np.geomspace(1.0, delta, n_steps + 1)
    xv, xs, eps2 = x0.copy(), x0.copy(), 0.0
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        dv = dfield(xv, a)
        eps2 += float(dv @ dv) * dt
        xv = xv + dt * ((xi - xv) / (1.0 - a) + dv)
        xs = xs + dt * ((xi - xs) / (1.0 - a))
    return float(np.linalg.norm(xv - xs)), eps2


d = 4
xi, x0 = RNG.normal(size=d), RNG.normal(size=d)
u = RNG.normal(size=d); u /= np.linalg.norm(u)

print("A. corrected bound  |e| <= eps sqrt(delta)")
print(f"{'a':>5} {'delta':>8} {'|e|':>11} {'eps':>10} {'eps*sqrt(d)':>12} {'slack':>11}")
worst = np.inf
for a in (0.0, 0.5):
    for delta in (1e-2, 1e-3, 1e-4):
        f = lambda x, t, a=a: u * (1.0 - t) ** (-a)
        e, eps2 = integrate(d, xi, x0, delta, f)
        eps = np.sqrt(eps2); bnd = eps * np.sqrt(delta)
        worst = min(worst, bnd - e)
        print(f"{a:>5.1f} {delta:>8.0e} {e:>11.3e} {eps:>10.4f} {bnd:>12.3e} "
              f"{bnd - e:>+11.3e}")
print(f"  worst slack {worst:+.3e}  {'HOLDS' if worst >= 0 else 'VIOLATED'}")

print("\nB. the exponent threshold: retained deviation as delta -> 0")
print(f"{'a':>5} " + " ".join(f"{f'd=1e-{k}':>11}" for k in (2, 3, 4, 5)))
for a in (0.0, 0.5, 0.9, 1.0, 1.1, 1.5):
    row = []
    for k in (2, 3, 4, 5):
        delta = 10.0 ** (-k)
        f = lambda x, t, a=a: u * (1.0 - t) ** (-a)
        e, _ = integrate(d, xi, x0, delta, f)
        row.append(f"{e:>11.3e}")
    print(f"{a:>5.1f} " + " ".join(row))
print("\n  a < 1: deviation -> 0 (contraction wins).  a >= 1: it does not.")
