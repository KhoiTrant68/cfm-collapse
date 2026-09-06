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

Part A checks the bound, part B locates the threshold at a = 1, and part C checks
the loss form E(1-delta) <= exp(L_Delta) sqrt(Loss * delta), whose only extra
hypothesis is a Lipschitz constant for the *error* -- zero for an error c(1-t)^{-1}u,
so it does not exclude the errors that survive.

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

def _loss_form():
    D = 4


    def make_delta(kind: str, scale: float, a: float):
        """Return (delta_fn, L_Delta). Magnitude grows like (1-t)^{-a}."""
        u = RNG.normal(size=D); u /= np.linalg.norm(u)
        if kind == "const":
            return (lambda x, t: scale * u * (1.0 - t) ** (-a)), 0.0
        M = RNG.normal(size=(D, D))
        M *= scale / np.linalg.norm(M, 2)          # spectral norm exactly `scale`
        return (lambda x, t: (M @ x) * (1.0 - t) ** (-a)), scale


    def loss_of(delta_fn, xi, n_mc=200000):
        """int_0^1 E_{x_0} |Delta((1-t)x_0 + t xi, t)|^2 dt, by Monte Carlo."""
        t = RNG.uniform(size=n_mc)
        x0 = RNG.normal(size=(n_mc, D))
        x = (1.0 - t)[:, None] * x0 + t[:, None] * xi[None, :]
        # vectorised evaluation for the two field shapes used here
        vals = np.stack([delta_fn(x[k], t[k]) for k in range(0, n_mc, 200)])
        return float((vals ** 2).sum(1).mean())


    def rms_deviation(delta_fn, xi, delta, n_paths=256, n_steps=4000):
        ts = 1.0 - np.geomspace(1.0, delta, n_steps + 1)
        x0 = RNG.normal(size=(n_paths, D))
        xv, xs = x0.copy(), x0.copy()
        for a, b in zip(ts[:-1], ts[1:]):
            dt = b - a
            dv = np.stack([delta_fn(xv[k], a) for k in range(n_paths)])
            xv = xv + dt * ((xi[None, :] - xv) / (1.0 - a) + dv)
            xs = xs + dt * ((xi[None, :] - xs) / (1.0 - a))
        return float(np.sqrt(((xv - xs) ** 2).sum(1).mean()))


    xi = RNG.normal(size=D)
    print(f"{'kind':>6} {'scale':>6} {'a':>4} {'L_D':>5} {'delta':>7} "
          f"{'E meas':>10} {'bound':>11} {'slack':>11}")
    worst = np.inf
    for kind in ("const", "linear"):
        for scale, a in ((0.5, 0.0), (2.0, 0.0), (1.0, 0.5), (1.0, 1.0)):
            f, LD = make_delta(kind, scale, a)
            loss = loss_of(f, xi)
            for delta in (1e-2, 1e-3):
                E = rms_deviation(f, xi, delta)
                bound = np.exp(LD) * np.sqrt(loss * delta)
                worst = min(worst, bound - E)
                print(f"{kind:>6} {scale:>6.1f} {a:>4.1f} {LD:>5.1f} {delta:>7.0e} "
                      f"{E:>10.4f} {bound:>11.4f} {bound - E:>+11.4f}")
    print(f"\nworst slack {worst:+.4e}   {'HOLDS' if worst >= 0 else 'VIOLATED'}")


print("\n\nC. loss form: E(1-delta) <= exp(L_Delta) sqrt(Loss * delta)")
_loss_form()
