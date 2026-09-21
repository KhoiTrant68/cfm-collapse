"""(b) loss-form bound on concrete examples, incl. the Lipschitz-hypothesis vs network
tension; (c) loss floor d/(3L) by direct minimisation on a 1-D Gaussian toy."""
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import lsq_linear

rng = np.random.default_rng(0)

# ------------------------------------------------------------------ (b) loss form
d = 2
xi = np.array([0.7, -0.4])
n = 4000
X0 = rng.normal(size=(n, d))
u = np.array([1.0, 0.0])
L_D = 0.8
M = np.array([[0.0, -1.0], [1.0, 0.0]]) * L_D       # spectral norm L_D


def make(a, cst, lin):
    """Delta(x,t) = (1-t)^-a (cst*u + lin*M x); Lipschitz const of Delta in x = lin*L_D*(1-t)^-a.
    For Assumption we take a=0 in the linear part so L_Delta = lin*L_D."""
    def D(x, t):
        return cst * (1 - t) ** (-a) * u[None, :] + lin * (x @ M.T)
    return D, lin * L_D


def loss_and_E(D, delta):
    # L_i = int_0^1 E|Delta(x*_s,s)|^2 ds  (x*_s = (1-s)X0 + s xi), quadrature over s, MC over X0
    def l2(s):
        xs = (1 - s) * X0 + s * xi
        return np.mean(np.sum(D(xs, s) ** 2, axis=1))
    # substitution to tame endpoint singularity: s = 1-exp(-tau)
    Li = quad(lambda tau: l2(1 - np.exp(-tau)) * np.exp(-tau), 0, 30, limit=200)[0]
    T = 1 - delta
    tauT = np.log(1 / delta)
    def rhs(tau, y):
        xv = y[:n * d].reshape(n, d); xs = y[n * d:].reshape(n, d)
        r = np.exp(-tau)
        return np.concatenate([((xi - xv) + r * D(xv, 1 - r)).ravel(), (xi - xs).ravel()])
    x0f = np.concatenate([X0.ravel(), X0.ravel()])
    s = solve_ivp(rhs, (0, tauT), x0f, rtol=1e-9, atol=1e-11, method="RK45")
    y = s.y[:, -1]
    E = np.sqrt(np.mean(np.sum((y[:n * d].reshape(n, d) - y[n * d:].reshape(n, d)) ** 2, axis=1)))
    return Li, E


print("B. loss-form: E(1-delta) <= e^{L_D} sqrt(L_i delta)  (L_i finite: a<1/2)")
print(f"{'a':>5}{'cst':>5}{'lin':>5}{'L_D':>6}{'delta':>8}{'L_i':>10}{'E meas':>11}{'bound':>11}{'ratio b/E':>10}")
for a, cst, lin in [(0.0, 1.0, 0.0), (0.25, 1.0, 0.0), (0.25, 1.0, 1.0), (0.4, 0.5, 2.0), (0.0, 0.0, 3.0)]:
    D, LD = make(a, cst, lin)
    for delta in (1e-2, 1e-3):
        Li, E = loss_and_E(D, delta)
        bound = np.exp(LD) * np.sqrt(Li * delta)
        print(f"{a:>5}{cst:>5}{lin:>5}{LD:>6.2f}{delta:>8.0e}{Li:>10.4f}{E:>11.5f}{bound:>11.5f}{bound/E:>10.2f}")

# violation with e^{L}->1 removed / the a>=1/2 cases have L_i = inf
print("\n   a=1/2 constant error: L_i = c^2 int (1-s)^-1 ds = infinity -> bound vacuous, "
      "yet deviation vanishes? (a<1):")
D, _ = make(0.5, 1.0, 0.0)
_, E = loss_and_E(D, 1e-3)
print(f"   E(1-1e-3) = {E:.5f}  (closed form (c/a)(delta^0.5 - delta)={2*(1e-3**.5-1e-3):.5f})")

# Lipschitz-hypothesis tension: a K-Lipschitz-in-x model has Lip(Delta)>=1/(1-t)-K
print("\n   Tension: model v = (xi-x)*min(1/(1-t),K) (K-Lipschitz in x). Delta = v - v*.")
for K in (10.0, 50.0):
    def D(x, t, K=K):
        return (xi[None, :] - x) * (min(1 / (1 - t), K) - 1 / (1 - t))
    for delta in (1e-2, 1e-3):
        Li, E = loss_and_E(D, delta)
        LD_needed = 1 / delta - K if 1 / delta > K else 0
        print(f"   K={K:>4} delta={delta:.0e}: L_i={Li:.4f} E meas={E:.4f}; "
              f"sqrt(L_i delta)={np.sqrt(Li*delta):.4f} (E is {E/np.sqrt(Li*delta):.0f}x larger); "
              f"ess-sup Lip(Delta) on [0,1-delta] = {LD_needed:.0f} -> e^L_D = e^{LD_needed:.0f}")

# ------------------------------------------------------------------ (c) floor
print("\nC. floor: pointwise inf_{L-Lip v} E|v - f|^2 vs d(1-Ls)^2, 1-D, x^i=0.9, then integrate")
xi1 = 0.9
def pointwise_min(L, s, m=801):
    t = 1 - s
    x = np.linspace(t * xi1 - 7 * s, t * xi1 + 7 * s, m)
    w = np.exp(-0.5 * ((x - t * xi1) / s) ** 2); w /= w.sum()
    f = (xi1 - x) / s
    dx = x[1] - x[0]
    # v = v0 + dx*cumsum([0, s_1..s_{m-1}]), |s_k|<=L: bounded LS in (v0, s_k)
    A = np.zeros((m, m)); A[:, 0] = 1.0
    for k in range(1, m):
        A[k:, k] = dx
    W = np.sqrt(w)[:, None]
    lb = np.r_[-np.inf, -L * np.ones(m - 1)]; ub = np.r_[np.inf, L * np.ones(m - 1)]
    res = lsq_linear(W * A, W[:, 0] * f, bounds=(lb, ub), method="bvls", max_iter=2000)
    return np.sum(w * (A @ res.x - f) ** 2)
L = 4.0
print(f"{'1-t':>6}{'numeric min':>14}{'d(1-Ls)^2':>12}{'liplb ok':>10}")
for s in (0.5, 0.25, 0.15, 0.1, 0.05, 0.01):
    mn = pointwise_min(L, s)
    lb = max(1 - L * s, 0) ** 2
    print(f"{s:>6}{mn:>14.6f}{lb:>12.6f}{str(mn >= lb - 1e-4):>10}")
# integral of the numerical pointwise minimum over t~U(0,1)
ss = np.linspace(1e-3, 1, 60)
vals = np.array([pointwise_min(L, s, m=401) for s in ss])
print(f"   int_0^1 numeric pointwise min dt = {np.trapezoid(vals, ss):.5f};  d/(3L) = {1/(3*L):.5f}")
