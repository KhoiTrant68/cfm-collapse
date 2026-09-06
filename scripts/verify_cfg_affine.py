"""Check the claim behind the classifier-free-guidance corollary numerically.

The claim: for any guidance weight w, the CFG velocity

    v_w = (1+w) v_h^*(x,t,y) - w v_unc^*(x,t)

has the form (m_w(x,t) - x)/(1-t) where m_w is an *affine* combination of the
training atoms -- coefficients (1+w)w_i^(h) - w q_i, which sum to (1+w) - w = 1,
though they are no longer all nonnegative. Writing P for the orthogonal projection
onto the affine hull A of the atoms and q_t = x_t - P x_t for the component of the
trajectory orthogonal to A, that form forces

    d/dt q_t = -q_t / (1-t)      hence      q_t = (1-t) q_0,

so the orthogonal component decays exactly linearly and the endpoint law is
supported in A, whatever w is. When N <= d, A is Lebesgue-null in R^d, so no
guidance weight can make the conditional law absolutely continuous.

This integrates the true CFG ODE (no approximation of the weights) from a start
point deliberately placed off A, and checks q_t/(1-t) is constant to integrator
accuracy. It also reports the endpoint's distance to the nearest atom, which the
affine-hull result does not by itself control.

    uv run python scripts/verify_cfg_affine.py
"""
from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(0)


def make_instance(N: int, d: int, k: int):
    X = RNG.normal(size=(N, d)) * 1.5
    Y = RNG.normal(size=(N, k))
    return X, Y


def weights(x, t, X, Y, y, h):
    """Conditional kernel weights w_i^(h) and unconditional weights q_i."""
    z = (x[None, :] - t * X) / (1.0 - t)                 # (N, d)
    log_spatial = -0.5 * (z ** 2).sum(1)
    log_spatial -= log_spatial.max()
    spatial = np.exp(log_spatial)
    q = spatial / spatial.sum()
    if h <= 0:
        return None, q
    log_lab = -0.5 * ((y[None, :] - Y) ** 2).sum(1) / h ** 2
    log_w = log_spatial + log_lab
    log_w -= log_w.max()
    w = np.exp(log_w)
    return w / w.sum(), q


def cfg_velocity(x, t, X, Y, y, h, guidance, hard_index=None):
    wc, q = weights(x, t, X, Y, y, h)
    if h <= 0:                       # hard conditioning: all mass on one atom
        xbar_c = X[hard_index]
    else:
        xbar_c = wc @ X
    xbar_u = q @ X
    m_w = (1.0 + guidance) * xbar_c - guidance * xbar_u
    return (m_w - x) / (1.0 - t)


def integrate(x0, X, Y, y, h, guidance, hard_index, n_steps=20000, t_end=1 - 1e-6):
    """Explicit RK4 on a schedule that refines towards t = 1."""
    ts = 1.0 - np.geomspace(1.0, 1.0 - t_end, n_steps + 1)
    x = x0.copy()
    traj = [(0.0, x.copy())]
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        f = lambda tt, xx: cfg_velocity(xx, tt, X, Y, y, h, guidance, hard_index)
        k1 = f(a, x)
        k2 = f(a + dt / 2, x + dt / 2 * k1)
        k3 = f(a + dt / 2, x + dt / 2 * k2)
        k4 = f(b, x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        traj.append((b, x.copy()))
    return traj


def orth_component(x, X):
    """Component of x orthogonal to the affine hull of the rows of X."""
    base = X[0]
    B = X[1:] - base                       # spans the direction space of A
    Q, _ = np.linalg.qr(B.T)               # orthonormal basis of that span
    v = x - base
    return v - Q @ (Q.T @ v)


def main() -> None:
    print("N < d, so the affine hull is a proper (hence null) subspace\n")
    for h, guidance in ((0.0, 0.0), (0.0, 3.0), (0.0, 12.0),
                        (0.7, 0.0), (0.7, 3.0), (0.7, 12.0)):
        N, d, k = 6, 12, 2
        X, Y = make_instance(N, d, k)
        i = 2
        y = Y[i].copy()
        x0 = RNG.normal(size=d) * 2.0      # generic, so off the affine hull
        traj = integrate(x0, X, Y, y, h, guidance, hard_index=i)

        q0 = orth_component(traj[0][1], X)
        ratios, ts_shown = [], []
        for t, x in traj[::len(traj) // 6][1:]:
            qt = orth_component(x, X)
            if 1 - t <= 0:
                continue
            ratios.append(np.linalg.norm(qt) / ((1 - t) * np.linalg.norm(q0)))
            ts_shown.append(t)
        xT = traj[-1][1]
        dists = np.linalg.norm(X - xT[None, :], axis=1)
        j = int(dists.argmin())
        print(f"h={h:<4} w={guidance:<5} "
              f"|q_t| / ((1-t)|q_0|) = {np.min(ratios):.6f} .. {np.max(ratios):.6f}"
              f"   (theory: exactly 1)")
        print(f"{'':16}endpoint: nearest atom {j}"
              f"{' (= the conditioned one)' if j == i else ' (NOT the conditioned one)'}"
              f", distance {dists[j]:.3e}, "
              f"|q_T| = {np.linalg.norm(orth_component(xT, X)):.3e}")
    print("\nThe ratio being 1 to integrator accuracy is the claim: the orthogonal")
    print("component decays exactly like (1-t), for every guidance weight.")


if __name__ == "__main__":
    main()
