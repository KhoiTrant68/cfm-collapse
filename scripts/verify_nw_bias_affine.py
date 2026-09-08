"""Affine mu does NOT kill the Nadaraya-Watson bias: the design-density term survives.

The claim being checked is the proviso attached to the NW-rate proposition, that the
leading bias coefficient

    B(y) := Laplacian(mu)(y) + 2 grad(mu)(y)^T grad(log rho_Y)(y)

is nonzero. An earlier draft asserted that affine mu makes this vanish identically,
and hence that the linear-Gaussian instance we test has zero bias at every h. That is
wrong. Affineness kills only the FIRST term. The second term is
grad(mu)^T grad(log rho_Y), which for mu(y) = By and a centred Gaussian design
rho_Y = N(0, Sigma_Y) equals -B Sigma_Y^{-1} y -- zero only at y = 0.

The linear-Gaussian instance is exactly this case, so the bias is generically nonzero
away from the origin, and the MSE is NOT monotone in h.

Part A checks the exact closed form for the population kernel-weighted mean. With a
Gaussian kernel K_h = N(0, h^2 I) against a Gaussian design, the h-tilted label
posterior is Gaussian with mean Sigma_Y (Sigma_Y + h^2 I)^{-1} y, so

    xbar_h(y) = B Sigma_Y (Sigma_Y + h^2 I)^{-1} y,
    Bias(y,h) = xbar_h(y) - mu(y) = -B h^2 (Sigma_Y + h^2 I)^{-1} y,

verified here against numerical quadrature.

Part B checks that this exact bias agrees to leading order with the general NW bias
formula the paper quotes, i.e. Bias / h^2 -> -B Sigma_Y^{-1} y = (1/2) mu_2(K) B(y)
with mu_2(K) = 1 for the standard Gaussian kernel. Two independent derivations, one
closed form and one the textbook expansion, landing on the same coefficient.

Part C checks the consequence: at y != 0 the finite-N MSE of the NW estimator is
U-shaped in h with an interior minimum near N^{-1/(k+4)}, not monotone. At y = 0 the
bias does vanish by symmetry and the MSE decreases in h -- so y = 0 is the special
point, not the generic one.

Parameters follow the EXP-1 setup of the paper: d=2, k=1, sigma_obs=0.1.

    uv run python scripts/verify_nw_bias_affine.py
"""
from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(0)


def linear_gaussian(d=2, k=1, sigma_obs=0.1, seed=0):
    """The paper's instance: Y = A X + eta, X ~ N(0,I_d), eta ~ N(0, sigma_obs^2 I_k).

    Returns (A, Sigma_Y, B) where mu(y) = E[X | Y=y] = B y is affine.
    """
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((k, d)) / np.sqrt(d)
    Sigma_X = np.eye(d)
    Sigma_Y = A @ Sigma_X @ A.T + sigma_obs**2 * np.eye(k)
    B = Sigma_X @ A.T @ np.linalg.inv(Sigma_Y)  # d x k
    # B is exactly the Jacobian J = Sigma_post A^T / sigma_obs^2 the paper already
    # names (Woodbury), so the bias coefficient is written in existing notation.
    Sigma_post = np.linalg.inv(np.eye(d) + A.T @ A / sigma_obs**2)
    assert np.allclose(B, Sigma_post @ A.T / sigma_obs**2), "B should equal J"
    return A, Sigma_Y, B


def bias_closed_form(B, Sigma_Y, y, h):
    """-B h^2 (Sigma_Y + h^2 I)^{-1} y."""
    k = Sigma_Y.shape[0]
    return -B @ np.linalg.solve(Sigma_Y + h**2 * np.eye(k), h**2 * y)


def bias_quadrature(B, Sigma_Y, y, h, span=14.0, per_width=2000):
    """Population kernel-weighted mean minus mu(y), by direct 1-D quadrature (k=1).

    The grid is centred on the kernel query y and resolved to per_width points per
    min(h, sd of rho_Y), so the narrow-kernel cases stay accurate; nothing about the
    closed form under test is used to place it.
    """
    assert Sigma_Y.shape == (1, 1)
    s = np.sqrt(Sigma_Y[0, 0])
    lo, hi = min(-span * s, y[0] - span * h), max(span * s, y[0] + span * h)
    n_grid = int((hi - lo) / (min(h, s) / per_width)) + 1
    grid = np.linspace(lo, hi, n_grid)
    rho = np.exp(-0.5 * grid**2 / Sigma_Y[0, 0])
    ker = np.exp(-0.5 * (y[0] - grid) ** 2 / h**2)
    wt = rho * ker
    ybar = np.trapezoid(wt * grid, grid) / np.trapezoid(wt, grid)
    return (B @ np.array([ybar])) - (B @ y)


def part_a():
    print("Part A: exact closed form vs quadrature (Gaussian design, affine mu)")
    _, Sigma_Y, B = linear_gaussian()
    s = float(np.sqrt(Sigma_Y[0, 0]))
    print(f"  instance: Sigma_Y={Sigma_Y[0, 0]:.6f} (sd s={s:.4f}), B={np.round(B.ravel(), 4)}")
    worst = 0.0
    for y_mult in (0.0, 0.3, 1.0, 2.0):
        for h in (0.05 * s, 0.1 * s, 0.3 * s, 0.7 * s):
            y = np.array([y_mult * s])
            cf = bias_closed_form(B, Sigma_Y, y, h)
            qd = bias_quadrature(B, Sigma_Y, y, h)
            err = np.max(np.abs(cf - qd))
            worst = max(worst, err)
            print(
                f"  y={y_mult:.1f}s  h={h:6.4f}  |bias|={np.linalg.norm(cf):.6f}"
                f"   closed-form vs quadrature err={err:.2e}"
            )
    assert worst < 1e-8, worst
    print(f"  max discrepancy {worst:.2e}  -- closed form confirmed\n")


def part_b():
    print("Part B: exact bias / h^2  ->  -B Sigma_Y^{-1} y  (the paper's formula)")
    _, Sigma_Y, B = linear_gaussian()
    s = float(np.sqrt(Sigma_Y[0, 0]))
    for y_mult in (0.3, 1.0, 2.0):
        y = np.array([y_mult * s])
        target = -B @ np.linalg.solve(Sigma_Y, y)  # (1/2) mu_2(K) * Bcoef(y), mu_2=1
        assert np.linalg.norm(target) > 0.1, "coefficient should be nonzero for y != 0"
        print(f"  y={y_mult:.1f}s  asymptotic coefficient = {np.round(target, 4)}")
        prev = None
        for h in (0.2 * s, 0.1 * s, 0.05 * s, 0.025 * s):
            ratio = bias_closed_form(B, Sigma_Y, y, h) / h**2
            rel = np.linalg.norm(ratio - target) / np.linalg.norm(target)
            note = "" if prev is None else f"  (x{prev / rel:5.2f} per halving)"
            print(f"      h={h:6.4f}  bias/h^2 = {np.round(ratio, 4)}"
                  f"   rel.err={rel:.3e}{note}")
            if prev is not None:
                assert 3.5 < prev / rel < 4.5, "expected O(h^2) convergence"
            prev = rel
        assert prev < 1e-3, prev
    # And the one point where affineness DOES give zero bias:
    zero = bias_closed_form(B, Sigma_Y, np.array([0.0]), 0.3 * s)
    assert np.allclose(zero, 0.0), zero
    print("  convergence is O(h^2) to the quoted coefficient, which is nonzero;")
    print("  at y=0 the bias is exactly 0 (symmetry), so y=0 is the special point\n")


def nw_mse(B, A, Sigma_Y, y, h, N, n_rep=4000, sigma_obs=0.1, seed=1):
    """Monte-Carlo MSE of the NW estimator of mu(y) from N i.i.d. training pairs."""
    rng = np.random.default_rng(seed)
    d, k = B.shape
    mu_y = B @ y
    errs = np.empty((n_rep, d))
    for r in range(n_rep):
        X = rng.standard_normal((N, d))
        Y = X @ A.T + sigma_obs * rng.standard_normal((N, k))
        w = np.exp(-0.5 * np.sum((y[None, :] - Y) ** 2, axis=1) / h**2)
        tot = w.sum()
        if tot <= 0:
            errs[r] = np.nan
            continue
        errs[r] = (w @ X) / tot - mu_y
    return float(np.nanmean(np.sum(errs**2, axis=1)))


def part_c():
    print("Part C: finite-N MSE(h) is U-shaped at y != 0, decreasing at y = 0")
    A, Sigma_Y, B = linear_gaussian()
    s = float(np.sqrt(Sigma_Y[0, 0]))
    N, k = 2000, 1
    hs = s * np.array([0.02, 0.04, 0.08, 0.16, 0.32, 0.64])
    for y_mult in (1.0, 0.0):
        y = np.array([y_mult * s])
        mses = np.array([nw_mse(B, A, Sigma_Y, y, h, N) for h in hs])
        argmin = int(np.argmin(mses))
        shape = "U-shaped (interior minimum)" if 0 < argmin < len(hs) - 1 \
            else "monotone over the grid"
        print(f"  y={y_mult:.1f}s  N={N}")
        for h, m in zip(hs, mses):
            print(f"      h={h:6.4f}  MSE={m:.3e}")
        print(f"    -> argmin at h={hs[argmin]:.4f}: {shape}")
        print(f"       (h* ~ s N^-1/(k+4) = {s * N ** (-1 / (k + 4)):.4f})")
        if y_mult != 0.0:
            assert 0 < argmin < len(hs) - 1, "expected an interior minimum at y != 0"
        else:
            assert argmin == len(hs) - 1, "expected monotone decrease at y = 0"
    print()


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    print("All checks passed: affine mu does not annihilate the NW bias.")
