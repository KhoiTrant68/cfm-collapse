"""Audit checks: prop:tgtnoise (endpoint smoothing) and prop:prop17 (interpolant noise).
Monte Carlo conditional expectations vs the paper's closed forms, ODE endpoints, sympy for c(t),
and the finiteness of the L2 objective for sigma>0 (E Var(Xdot|X_t,t,Y) diverges at t=0)."""
import numpy as np, sympy as sp
from scipy.integrate import solve_ivp, quad

rng = np.random.default_rng(0)

# ------------------------------------------------------------------ tgtnoise (d=1,k=1)
x_at = np.array([-1.5, 0.3, 2.0]); y_at = np.array([-1.0, 0.2, 0.9]); N = 3
h, rho = 0.5, 0.4

def wts(x, t, y):
    s2 = (1 - t) ** 2 + t ** 2 * rho ** 2
    lw = -(x - t * x_at) ** 2 / (2 * s2) - (y - y_at) ** 2 / (2 * h * h)   # -1/2 log s2 cancels across i
    w = np.exp(lw - lw.max()); return w / w.sum()

def v_tgt(x, t, y):
    s2 = (1 - t) ** 2 + t ** 2 * rho ** 2
    w = wts(x, t, y)
    return np.sum(w * (x_at + (t * rho ** 2 - (1 - t)) / s2 * (x - t * x_at)))

def mc_tgt(x, t, y, n=40_000_000, bx=0.02, by=0.02):
    tot = 0; cnt = 0
    for _ in range(n // 10_000_000):
        m = 10_000_000
        I = rng.integers(0, N, m); X0 = rng.standard_normal(m); xi = rng.standard_normal(m)
        eps = rng.standard_normal(m)
        X1 = x_at[I] + rho * xi
        Xt = (1 - t) * X0 + t * X1
        Y = y_at[I] + h * eps
        sel = (np.abs(Xt - x) < bx) & (np.abs(Y - y) < by)
        tot += (X1[sel] - X0[sel]).sum(); cnt += sel.sum()
    return tot / cnt, cnt

print("== tgtnoise: E[X1-X0 | X_t=x,t,Ytilde=y]  MC vs eq:tgtfield")
for (x, t, y) in [(0.2, 0.5, 0.1), (1.0, 0.9, 0.9), (-0.5, 0.3, -0.5)]:
    mc, c = mc_tgt(x, t, y)
    print(f"  x={x} t={t} y={y}: MC={mc:.4f} (n={c})  formula={v_tgt(x,t,y):.4f}")

# endpoint law: integrate ODE on [0,1] (field is smooth at t=1 for rho>0)
y0 = 0.1
def rhs(t, x): return v_tgt(x[0], t, y0)
nS = 4000
X0s = rng.standard_normal(nS); ends = []
for x0 in X0s:
    sol = solve_ivp(rhs, (0, 1), [x0], rtol=1e-8, atol=1e-10, method="LSODA")
    ends.append(sol.y[0, -1])
ends = np.array(ends)
p = np.exp(-(y0 - y_at) ** 2 / (2 * h * h)); p /= p.sum()
mean_th = (p * x_at).sum(); var_th = (p * (x_at - mean_th) ** 2).sum() + rho ** 2
print(f"  ODE endpoint (t=1 exactly): mean={ends.mean():.4f} (theory {mean_th:.4f}) var={ends.var():.4f} (theory {var_th:.4f})")
print("  min distance of ODE endpoints to nearest atom (should NOT be ~0):", np.abs(ends[:, None] - x_at).min(1).mean())
# v* at t=1 equals x  (a(1)=1)
print("  v*(x,1,y) - x =", v_tgt(0.7, 1.0, y0) - 0.7, "(claim: extends continuously to t=1)")

# ------------------------------------------------------------------ prop17 (d=1, h=0, label pins i)
print("\n== prop17: sigma=0.7, atom x^i=1.3")
sig = 0.7; xi_ = 1.3
gam = lambda t: sig * np.sqrt(t * (1 - t))
gd = lambda t: sig * (1 - 2 * t) / (2 * np.sqrt(t * (1 - t)))
s2f = lambda t: (1 - t) ** 2 + gam(t) ** 2
cf = lambda t: (-(1 - t) + sig ** 2 / 2 * (1 - 2 * t)) / s2f(t)
def mc_p17(x, t, n=20_000_000, bx=0.01):
    X0 = rng.standard_normal(n); Z = rng.standard_normal(n)
    Xt = (1 - t) * X0 + t * xi_ + gam(t) * Z
    sel = np.abs(Xt - x) < bx
    return (xi_ - X0[sel] + gd(t) * Z[sel]).mean(), sel.sum()
for (x, t) in [(0.5, 0.2), (1.0, 0.6), (1.4, 0.95)]:
    mc, c = mc_p17(x, t)
    print(f"  x={x} t={t}: MC={mc:.4f} (n={c}) formula={xi_ + cf(t)*(x - t*xi_):.4f}")
# sympy: c = 1/2 d/dt log s^2
t, S = sp.symbols('t sigma', positive=True)
s2 = (1 - t) ** 2 + S ** 2 * t * (1 - t)
c_sym = (-(1 - t) + S ** 2 / 2 * (1 - 2 * t)) / s2
print("  sympy  c - (1/2) d/dt log s^2 =", sp.simplify(c_sym - sp.diff(sp.log(s2), t) / 2))
print("  sympy  s^2 factorisation:", sp.factor(s2))
print("  sympy  lim_{t->1}(1-t)c:", sp.limit((1 - t) * c_sym, t, 1), "(sigma>0 gives -1/2);  sigma=0 ->", sp.limit(((1 - t) * c_sym).subs(S, 0), t, 1))
# flow
for x0 in [-1.2, 0.4, 2.5]:
    sol = solve_ivp(lambda tt, x: xi_ + cf(tt) * (x - tt * xi_), (0, 1 - 1e-6), [x0], rtol=1e-11, atol=1e-13, method="LSODA", dense_output=True)
    tt = 0.8
    print(f"  x0={x0}: ODE x(0.8)={sol.sol(tt)[0]:.6f}  closed form={tt*xi_+np.sqrt(s2f(tt))*x0:.6f};  x(1-1e-6)={sol.y[0,-1]:.5f} (atom {xi_})")

# L2 objective finiteness: E Var(Xdot|X_t,t,Y) = int_0^1 [1+gd^2 - c^2 s2] dt (per coordinate)
def var_t(tt): return 1 + gd(tt) ** 2 - cf(tt) ** 2 * s2f(tt)
print("  per-time conditional variance: t=1e-2:", var_t(1e-2), " t=1e-4:", var_t(1e-4), " t=1e-6:", var_t(1e-6), " t=0.5:", var_t(0.5), " t=1-1e-6:", var_t(1 - 1e-6))
for eps in [1e-2, 1e-4, 1e-6, 1e-8]:
    val = quad(var_t, eps, 0.5, limit=200)[0] + quad(var_t, 0.5, 1 - 1e-9, limit=200)[0]
    print(f"  int_eps^1 Var dt, eps={eps:g}: {val:.4f}   (sigma^2/4*log(1/eps)={sig**2/4*np.log(1/eps):.4f})")
print("  => inf_v L_sigma = +infinity for t~U(0,1): E|Xdot|^2 and E Var diverge logarithmically at t=0 (gamma-dot ~ t^{-1/2}).")
