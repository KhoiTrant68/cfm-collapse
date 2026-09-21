"""Claim at main.tex l.2914-2917: endpoint is delta_{x^i} 'whether or not the target is correct' (target X1-X0 without gammadot*Z).
Population field for the mis-specified target: v'(x,t)=x^i-(1-t)/s_t^2 (x-t x^i).  Its flow: u=x-t x^i, u' = -(1-t)/s^2 u."""
import numpy as np
from scipy.integrate import solve_ivp, quad
xi_ = 1.3
for sig in [0.0, 0.1, 0.3, 0.7, 1.0]:
    s2 = lambda t: (1 - t) ** 2 + sig ** 2 * t * (1 - t)
    f = lambda t, x: xi_ - (1 - t) / s2(t) * (x - t * xi_) if sig > 0 else xi_ - (x - t * xi_) / (1 - t)
    x0 = 1.0
    sol = solve_ivp(f, (0, 1 - 1e-9), [x0], rtol=1e-12, atol=1e-14, method="LSODA")
    kappa = sig ** (2 / (1 - sig ** 2)) if 0 < sig < 1 else (np.exp(-1) if sig == 1 else 0.0)
    print(f"sigma={sig}: endpoint from x0=1: {sol.y[0,-1]:.6f} ; atom {xi_} ; endpoint-atom={sol.y[0,-1]-xi_:.5f} ; predicted kappa*x0 = {kappa:.5f}")
