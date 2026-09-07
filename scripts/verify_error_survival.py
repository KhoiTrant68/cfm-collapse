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


# ---------------------------------------------------------------------------
def _measured_pacing():
    """D. Does the loss form describe the collapse that was actually measured?

    Part C checks the bound on constructed errors. This checks its *shape* on
    EXP-1. The corollary says the retained deviation scales like sqrt(Loss) at
    fixed truncation, so on log axes the conditional standard deviation against
    the training loss should have slope 1/2, with a prefactor exp(L_Delta) that
    the corollary does not pin down.

    Iterations 100 and 300 are excluded: the model is still leaving its
    initialisation there, holds data-scale variance, and is not collapsing, so
    including them fits a line through a regime the corollary does not describe.
    They are reported separately rather than silently dropped.
    """
    import glob

    import pandas as pd

    fs = sorted(glob.glob("results/exp1/exp1_cond_seed[0-9]/raw/metrics.csv"))
    if not fs:
        print("  (no EXP-1 runs found; skipped)")
        return
    m = pd.concat([pd.read_csv(f) for f in fs])
    m = m[m["group"] == "train"]
    g = m.groupby("iter")[["train_loss", "trace_cov_mean"]].mean()
    it = g.index.values
    loss = g["train_loss"].values
    std = np.sqrt(g["trace_cov_mean"].values)
    delta = 1e-3  # EXP-1's sampler truncation, eval.ode_eps

    print(f"  {'iter':>8} {'loss':>8} {'std':>8} {'std/sqrt(L*delta)':>19}")
    for i, l, s in zip(it, loss, std):
        print(f"  {i:>8} {l:>8.4f} {s:>8.4f} {s / np.sqrt(l * delta):>19.1f}")

    print(f"\n  {'fitted over':>16} {'n':>3} {'slope':>7} {'R^2':>7}"
          f"   (corollary predicts 1/2)")
    for lo in (0, 1000, 30000):
        k = it >= lo
        sl = np.polyfit(np.log(loss[k]), np.log(std[k]), 1)[0]
        r2 = np.corrcoef(np.log(loss[k]), np.log(std[k]))[0, 1] ** 2
        tag = "all checkpoints" if lo == 0 else f"iter >= {lo}"
        print(f"  {tag:>16} {int(k.sum()):>3} {sl:>7.3f} {r2:>7.3f}")

    k = it >= 1000
    sl = np.polyfit(np.log(loss[k]), np.log(std[k]), 1)[0]
    off = float(np.median(std[k] / np.sqrt(loss[k] * delta)))
    ok = abs(sl - 0.5) < 0.1
    print(f"\n  slope {sl:.3f} vs 1/2: {'agrees' if ok else 'DOES NOT AGREE'} "
          f"within 0.1; prefactor exp(L_Delta) ~ {off:.0f}, so the bound holds "
          f"with L_Delta >= {np.log(off):.2f}.")
    print("  One trajectory on one problem is consistent with the exponent the bound "
          "predicts;\n  it is not a demonstration that optimisation must follow it. "
          "The constant is loose,\n  and Figure fig_survival(c) says so.")


print("\n\nD. the loss form against the measured EXP-1 collapse")
_measured_pacing()


# ---------------------------------------------------------------------------
def _sharpness():
    """E. Is the bound attained, and does a>1 actually diverge?

    The proposition used to conclude "unbounded when a>1" from an upper bound that
    diverges, which does not follow -- e == 0 satisfies the same inequality. The
    threshold is now established by exhibiting an error that attains the bound:
    for the spatially constant Delta(x,t) = c(1-t)^{-a} u the identity

        e_t = (1-t) int_0^t Delta(x^v_s,s)/(1-s) ds

    evaluates in closed form to (c/a)((1-t)^{1-a} - (1-t)) u, so equality holds.
    This checks that closed form against the integrated ODE, which is the only
    part of the argument a slip could hide in, and then reads off the trichotomy
    at successively finer truncations.
    """
    dim = 4
    xi_, x0_ = RNG.normal(size=dim), RNG.normal(size=dim)
    u = RNG.normal(size=dim)
    u /= np.linalg.norm(u)

    def exact(eps, a, c=1.0):
        if abs(a) < 1e-12:
            return -c * eps * np.log(eps)
        return c * (eps ** (1.0 - a) - eps) / a

    def integrate(a, delta, c=1.0, n_steps=400000):
        ts = 1.0 - np.geomspace(1.0, delta, n_steps + 1)
        xv, xs = x0_.copy(), x0_.copy()
        for p_, q_ in zip(ts[:-1], ts[1:]):
            dt = q_ - p_
            xv = xv + dt * ((xi_ - xv) / (1 - p_) + c * u * (1 - p_) ** (-a))
            xs = xs + dt * ((xi_ - xs) / (1 - p_))
        return float(np.linalg.norm(xv - xs))

    print(f"  {'a':>5} {'1-t':>8} {'|e| integrated':>15} {'closed form':>13} "
          f"{'rel. err':>10}")
    worst = 0.0
    for a in (0.0, 0.5, 0.9, 1.0, 1.1, 1.3):
        for delta in (1e-2, 1e-4):
            got = integrate(a, delta)
            want = exact(delta, a)
            rel = abs(got - want) / max(want, 1e-12)
            worst = max(worst, rel)
            print(f"  {a:>5.1f} {delta:>8.0e} {got:>15.6f} {want:>13.6f} {rel:>10.2e}")
    print(f"\n  worst relative discrepancy {worst:.2e} "
          f"({'closed form confirmed' if worst < 5e-3 else 'MISMATCH'})")

    print("\n  the trichotomy, read off the closed form at finer truncations:")
    print(f"  {'a':>5} " + " ".join(f"{d:>11.0e}" for d in (1e-2, 1e-4, 1e-8, 1e-16)))
    for a in (0.5, 0.9, 1.0, 1.1, 1.3):
        vals = [exact(d, a) for d in (1e-2, 1e-4, 1e-8, 1e-16)]
        print(f"  {a:>5.1f} " + " ".join(f"{v:>11.3e}" for v in vals))
    print("  a < 1 -> 0, a = 1 -> c = 1 exactly, a > 1 -> infinity. The bound of (b) "
          "is attained,\n  so (c) settles the case (b) cannot.")


print("\n\nE. sharpness: the bound is attained, and a>1 diverges")
_sharpness()



# ---------------------------------------------------------------------------
def _converse():
    """F. Part (d) of the proposition: e_t = (1-t) I(t), with

        I(t) = int_0^t Delta(x_s^v, s) / (1-s) ds

    the accumulated weighted error. Every endpoint case for e_t is therefore a case
    for I at the scale (1-t)^{-1}, and the proposition lists four. Three are the
    trichotomy of part (c), already checked in E. The fourth -- I sitting AT the
    critical scale but with no limiting direction, so that e_t has no endpoint at all
    -- is what makes "in a direction that does not cancel" a real caveat rather than
    decoration, and an exhaustiveness claim needs its witness.

    Write the plane as C and take the spatially constant error

        Delta(t) = c (1-t)^{-1} exp(i theta),   theta(t) = log(1/(1-t)),

    critical in magnitude, its direction turning one radian per e-fold of (1-t).
    Substituting eps = 1-t = e^{-theta} (so ds/(1-s) = dphi):

        I = c int_0^theta e^{phi} e^{i phi} dphi = c (e^{(1+i)theta} - 1)/(1+i),
        e_t = eps * I = c e^{i theta}/(1+i) - c e^{-theta}/(1+i).

    So |e_t| -> c/sqrt(2): bounded, and bounded AWAY from zero, while arg(e_t)
    advances without settling. Critical magnitude alone is not sufficient for an
    endpoint; the direction has to converge too.

    The check integrates the perturbed and unperturbed flows rather than evaluating
    the closed form, so it tests the identity and not just the algebra.
    """
    c, xi = 1.0, 0.3 - 0.7j

    def run(eps_end: float, n_steps: int = 200_000) -> complex:
        # graded in eps, so dt/(1-t) is constant and explicit Euler stays stable
        eps_grid = np.geomspace(1.0, eps_end, n_steps + 1)
        xv = xs = 0.0 + 0.0j
        for e0, e1 in zip(eps_grid[:-1], eps_grid[1:]):
            dt = e0 - e1                      # dt = -d(eps) > 0
            drift = c * np.exp(1j * np.log(1.0 / e0)) / e0
            xv = xv + dt * ((xi - xv) / e0 + drift)
            xs = xs + dt * ((xi - xs) / e0)
        return xv - xs

    def closed(eps: float) -> complex:
        th = np.log(1.0 / eps)
        return c * (np.exp(1j * th) - np.exp(-th)) / (1.0 + 1j)

    print("  critical magnitude, direction turning one radian per e-fold of (1-t):")
    print(f"  {'1-t':>9} {'|e_t|':>9} {'|e| pred':>9} {'arg(e_t)':>10} "
          f"{'arg pred':>10} {'rel err':>9}")
    mags, ok = [], True
    for eps in (1e-2, 1e-3, 1e-4, 1e-5):
        got, want = run(eps), closed(eps)
        rel = abs(got - want) / abs(want)
        mags.append(abs(got))
        ok &= rel < 5e-3
        print(f"  {eps:>9.0e} {abs(got):>9.5f} {abs(want):>9.5f} "
              f"{np.angle(got):>10.5f} {np.angle(want):>10.5f} {rel:>9.2e}")

    lim = c / np.sqrt(2.0)
    ok &= max(abs(m - lim) for m in mags[1:]) < 0.02
    print(f"\n  |e_t| holds at {lim:.5f} (spread {max(mags)-min(mags):.1e} over four "
          f"decades of 1-t):\n  bounded, and bounded away from 0, while the argument "
          "advances by one radian per\n  e-fold and never settles. So e_t has no "
          f"endpoint: {'case 4 is occupied' if ok else 'CHECK FAILED'}.")
    print("  Exhaustiveness itself needs no experiment -- e_t = (1-t)I(t) is an "
          "identity, and a\n  limit that is 0, nonzero, infinite or absent exhausts "
          "the possibilities for any\n  function. What needed checking is that the "
          "fourth case is not vacuous.")
    return bool(ok)


print("\n\nF. the converse (d): the fourth case is occupied")
if not _converse():
    raise SystemExit(1)
