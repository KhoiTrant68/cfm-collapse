"""Independent check of prop:survival: identity e_t=(1-t)I(t), four cases, and
the critical case. Integrates in tau=-log(1-t) (non-stiff) with tight tolerances.

State: x^v, x^*, I.   d/dtau x^v = (xi - x^v) + (1-t) Delta(x^v,t)
                       d/dtau x^* = (xi - x^*)
                       d/dtau I   = Delta(x^v,t)          (since ds/(1-s)=dtau)
"""
import numpy as np
from scipy.integrate import solve_ivp

rng = np.random.default_rng(1)
d = 3
xi = rng.normal(size=d)
x0 = rng.normal(size=d)
u = rng.normal(size=d); u /= np.linalg.norm(u)
M = rng.normal(size=(d, d)); M *= 0.7 / np.linalg.norm(M, 2)


def run(delta_fn, taus):
    def rhs(tau, y):
        xv, xs, I = y[:d], y[d:2 * d], y[2 * d:]
        r = np.exp(-tau)                       # 1-t
        D = delta_fn(xv, 1 - r)
        return np.concatenate([(xi - xv) + r * D, xi - xs, D])
    y0 = np.concatenate([x0, x0, np.zeros(d)])
    s = solve_ivp(rhs, (0, taus[-1]), y0, t_eval=taus, rtol=1e-11, atol=1e-13,
                  method="DOP853")
    return s.y


taus = np.array([np.log(1 / r) for r in (1e-1, 1e-2, 1e-3, 1e-4)])

print("A. identity e_t = (1-t) I(t) with x-dependent, non-monotone Delta")
worst = 0
for a, c in [(0.0, 1.0), (0.5, 0.3), (1.0, 2.0), (1.5, 0.5)]:
    f = lambda x, t, a=a, c=c: c * (1 - t) ** (-a) * (u + M @ np.sin(x))
    Y = run(f, taus)
    for k, tau in enumerate(taus):
        r = np.exp(-tau)
        e = Y[:d, k] - Y[d:2 * d, k]
        rhs_ = r * Y[2 * d:, k]
        rel = np.linalg.norm(e - rhs_) / max(np.linalg.norm(e), 1e-300)
        worst = max(worst, rel)
print(f"   worst relative mismatch over (a,c)x(1-t): {worst:.2e}")

print("\nB. Delta = c (1-t)^-a u : |e_t| vs closed form (c/a)((1-t)^{1-a}-(1-t))")
print(f"{'a':>5}{'c':>5}{'1-t':>9}{'|e| num':>13}{'closed':>13}{'rel':>9}")
for a, c in [(0.5, 1.0), (1.0, 2.0), (1.5, 0.5), (0.0, 1.0)]:
    f = lambda x, t, a=a, c=c: c * (1 - t) ** (-a) * u
    Y = run(f, taus)
    for k, tau in enumerate(taus):
        r = np.exp(-tau)
        e = np.linalg.norm(Y[:d, k] - Y[d:2 * d, k])
        cl = -c * r * np.log(r) if a == 0 else c / a * (r ** (1 - a) - r)
        print(f"{a:>5}{c:>5}{r:>9.0e}{e:>13.5e}{cl:>13.5e}{abs(e-cl)/cl:>9.1e}")

print("\nC. critical, rotating: Delta=c(1-t)^-1 R(theta)u, theta=log(1/(1-t)), plane")
c = 1.0
def rot(x, t):
    th = np.log(1 / (1 - t)); R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return c / (1 - t) * (R @ np.array([1.0, 0.0]))
d = 2; xi = np.array([0.3, -0.7]); x0 = np.zeros(2)
taus2 = np.array([np.log(1 / r) for r in (1e-2, 1e-3, 1e-4, 1e-5)])
Y = run(rot, taus2)
for k in range(len(taus2)):
    e = Y[:2, k] - Y[2:4, k]
    print(f"   1-t={np.exp(-taus2[k]):.0e} |e|={np.linalg.norm(e):.6f}  arg={np.arctan2(e[1], e[0]):+.4f}  (limit |e| = c/sqrt2 = {c/np.sqrt(2):.6f})")

print("\nD. an unbounded-but-not-divergent case not covered by 'four cases':")
# Delta = c (1-t)^-1 * g(theta) u with g s.t. (1-t)I oscillates with growing amplitude at
# rate that is unbounded along a subsequence and small along another. take e(tau) directly:
# e = r*I, I' = Delta => (e/r)' = Delta. choose e(tau)=A(tau) sin^2(tau) with A=tau (limsup inf, liminf 0)
# realise via Delta(tau) = d/dtau (e e^{tau}) e^{-...}; check trivial identity
tau = np.linspace(0, 40, 4001)
e = tau * np.sin(tau) ** 2
print("   e(tau)=tau sin^2(tau): limsup=inf, liminf=0 -> neither 'bounded', 'limit', nor '->inf'."
      f" min over last window {e[-400:].min():.3f}, max {e[-400:].max():.3f}")
