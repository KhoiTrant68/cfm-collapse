"""Closed-form verification of THEORY Part C (Prop 17 / Cor 18).

No network involved -- these are algebraic/ODE identities of the stochastic
interpolant x_t = (1-t)x0 + t x1 + gamma(t)Z, gamma(t)=sigma*sqrt(t(1-t)):

  1. c(t) = 1/2 d/dt log s_t^2, with s_t^2 = (1-t)^2 + sigma^2 t(1-t)   [eq. 17.1]
  2. RK4 integration of  x' = x^i + c(t)(x - t x^i)  matches the closed-form
     flow  x_t = t x^i + s_t x0                                         [eq. 17.2]
  3. endpoint x_{1-1e-3} -> x^i for every sigma (endpoint invariance)   [eq. 17.3]
  4. (1-t)|c(t)| -> 1 for sigma=0, -> 1/2 for sigma>0                   [eq. 18.1]

    uv run python scripts/verify_prop17.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PASS, FAIL = "PASS", "FAIL"
_ok = True


def check(name: str, cond: bool, detail: str = "") -> None:
    global _ok
    _ok = _ok and bool(cond)
    print(f"[{PASS if cond else FAIL}] {name}" + (f"  ({detail})" if detail else ""))


def s2(t, sigma):
    return (1 - t) ** 2 + sigma ** 2 * t * (1 - t)


def c_of_t(t, sigma):
    return (-(1 - t) + 0.5 * sigma ** 2 * (1 - 2 * t)) / s2(t, sigma)


def main() -> None:
    torch.set_default_dtype(torch.float64)
    sigmas = [0.0, 0.1, 0.3, 1.0]

    # 1. c(t) == 1/2 d/dt log s_t^2  (central finite differences)
    print("--- 1. c(t) = 1/2 d/dt log s_t^2 ---")
    for sigma in sigmas:
        t = torch.linspace(0.05, 0.95, 50)
        dt = 1e-6
        num = (torch.log(s2(t + dt, sigma)) - torch.log(s2(t - dt, sigma))) / (2 * dt)
        err = float((0.5 * num - c_of_t(t, sigma)).abs().max())
        check(f"sigma={sigma}: c(t) matches 1/2 (log s^2)'", err < 1e-5, f"max err={err:.2e}")

    # 2. RK4 of x' = x^i + c(t)(x - t x^i) matches x_t = t x^i + s_t x0
    print("\n--- 2. flow matches closed form x_t = t x^i + s_t x0 ---")
    xi = torch.tensor([1.5, -0.7])
    x0s = torch.randn(200, 2)
    t0, t1, nstep = 1e-3, 1 - 1e-3, 4000
    grid = torch.linspace(t0, t1, nstep + 1)
    for sigma in sigmas:
        def field(x, t):
            return xi[None, :] + c_of_t(t, sigma) * (x - t * xi[None, :])
        # closed-form initial state at t0
        x = t0 * xi[None, :] + torch.sqrt(s2(torch.tensor(t0), sigma)) * x0s
        for j in range(nstep):
            t, h = grid[j], grid[j + 1] - grid[j]
            k1 = field(x, t)
            k2 = field(x + 0.5 * h * k1, t + 0.5 * h)
            k3 = field(x + 0.5 * h * k2, t + 0.5 * h)
            k4 = field(x + h * k3, t + h)
            x = x + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        closed = t1 * xi[None, :] + torch.sqrt(s2(torch.tensor(t1), sigma)) * x0s
        err = float((x - closed).abs().max())
        check(f"sigma={sigma}: RK4 == closed form (17.2)", err < 1e-6, f"max err={err:.2e}")

    # 3. endpoint invariance in sigma: x_t = t x^i + s_t x0 with s_t -> 0 as t->1
    #    for EVERY sigma. The residual scale sqrt(s2(t)) is what -> 0; it does so
    #    for all sigma, so p_1 = delta_{x^i} regardless of sigma (eq. 17.3).
    print("\n--- 3. endpoint invariance: sqrt(s2(t)) -> 0 for every sigma ---")
    for sigma in sigmas:
        scales = [float(torch.sqrt(s2(torch.tensor(1 - e), sigma))) for e in (1e-2, 1e-4, 1e-6)]
        monotone = scales[0] > scales[1] > scales[2]
        check(f"sigma={sigma}: residual scale -> 0 (delta_x^i limit)",
              monotone and scales[-1] < 2e-3,
              f"sqrt(s2) at 1-1e-2/1e-4/1e-6 = {scales[0]:.3e}/{scales[1]:.3e}/{scales[2]:.3e}")

    # 4. (1-t)|c(t)| -> 1 (sigma=0) / -> 1/2 (sigma>0) as t->1
    print("\n--- 4. Lipschitz blow-up rate (1-t)|c(t)| ---")
    t = torch.tensor(1 - 1e-6)
    for sigma in sigmas:
        val = float((1 - t) * c_of_t(t, sigma).abs())
        target = 1.0 if sigma == 0.0 else 0.5
        check(f"sigma={sigma}: (1-t)|c| -> {target}", abs(val - target) < 1e-3, f"got {val:.4f}")

    print("\n" + ("ALL PROP-17 CHECKS PASSED" if _ok else "SOME CHECKS FAILED"))
    sys.exit(0 if _ok else 1)


if __name__ == "__main__":
    main()
