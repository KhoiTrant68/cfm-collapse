"""Audit checks: prop:cfg (guided field, affine-hull confinement q_t=(1-t)q_0) and prop:cfgatom (endpoints are atoms).
(1) MC check of v_c, v_unc closed forms and guided combination;  (2) q_t/(1-t) identity;  (3) N>d endpoints;
(4) N=2, d=1 degenerate/equidistant cases and existence of stable non-atom fixed points of the fast dynamics."""
import numpy as np
from scipy.integrate import solve_ivp
rng = np.random.default_rng(3)

def make_field(X, Y, h, y, w):
    N = len(X)
    if h > 0:
        lk = -np.sum((y - Y) ** 2, axis=1) / (2 * h * h)
    else:  # hard label: y equals label of atom `y` (int index)
        lk = np.full(N, -np.inf); lk[y] = 0.0
    def parts(x, t):
        ls = -np.sum((x - t * X) ** 2, axis=1) / (2 * (1 - t) ** 2)
        a = ls + lk; a = np.exp(a - a.max()); a /= a.sum()
        b = np.exp(ls - ls.max()); b /= b.sum()
        return a, b
    def v(x, t):
        a, b = parts(x, t)
        m = ((1 + w) * a - w * b) @ X
        return (m - x) / (1 - t)
    return v, parts

# ---------------------------------------------------------------- (1) MC check of fields, d=2, N=3, k=1
X = np.array([[0., 0.], [1.5, 0.3], [-0.5, 1.6]]); Y = np.array([[0.], [0.6], [-0.4]]); h = 0.7; y = np.array([0.2]); t = 0.5
xq = np.array([0.4, 0.5])
v_c, parts = make_field(X, Y, h, y, 0.0); v_g, _ = make_field(X, Y, h, y, 3.0)
tot_c = np.zeros(2); n_c = 0; tot_u = np.zeros(2); n_u = 0
for _ in range(10):
    m = 8_000_000
    I = rng.integers(0, 3, m); X0 = rng.standard_normal((m, 2)); eps = rng.standard_normal(m)
    Xt = (1 - t) * X0 + t * X[I]; Yt = Y[I, 0] + h * eps
    s = np.linalg.norm(Xt - xq, axis=1) < 0.15
    U = X[I][s] - X0[s]
    tot_u += U.sum(0); n_u += s.sum()
    s2 = s & (np.abs(Yt - y[0]) < 0.06)
    U2 = (X[I] - X0)[s2]; tot_c += U2.sum(0); n_c += s2.sum()
_, b = parts(xq, t)
vunc = (b @ X - xq) / (1 - t)
print("(1) MC v_c   :", tot_c / n_c, f"(n={n_c})  closed form:", v_c(xq, t))
print("    MC v_unc :", tot_u / n_u, f"(n={n_u})  closed form:", vunc)
mc_g = 4 * tot_c / n_c - 3 * tot_u / n_u
print("    guided w=3 from MC:", mc_g, " closed form:", v_g(xq, t))

# ---------------------------------------------------------------- (2) orthogonal component
def run(v, x0, T=1 - 1e-6):
    return solve_ivp(lambda t, x: v(x, t), (0, T), x0, method="LSODA", rtol=1e-9, atol=1e-12, dense_output=True)

print("\n(2) q_t/(1-t)q_0 identity, d=3, six atoms spanning a plane")
B = rng.standard_normal((6, 2)); Ppl = np.array([[1, 0, 0], [0, 1, 0]]).T  # plane z=0 offset
Xp = np.c_[B, np.full(6, 0.4)]; Yp = rng.standard_normal((6, 1))
for hh in [0.0, 0.7]:
    for ww in [0.0, 3.0, 12.0]:
        v, _ = make_field(Xp, Yp if hh > 0 else Yp, hh, np.array([0.1]) if hh > 0 else 2, ww)
        x0 = rng.standard_normal(3); sol = run(v, x0)
        errs = [abs(sol.sol(tt)[2] - 0.4) / (abs(x0[2] - 0.4) * (1 - tt)) - 1 for tt in [0.1, 0.5, 0.9, 0.999, 1 - 1e-5]]
        print(f"   h={hh} w={ww}: max|q_t/((1-t)q_0)-1| = {max(map(abs,errs)):.2e}; end point {np.round(sol.y[:,-1],4)}")

# ---------------------------------------------------------------- (3) N>d: do endpoints land on atoms?
print("\n(3) N=5 atoms in d=2 (hull = R^2), h=0.7 : distance of endpoint (t=1-1e-6) to nearest atom")
X5 = rng.standard_normal((5, 2)) * 1.5; Y5 = rng.standard_normal((5, 1))
for ww in [0.0, 3.0, 12.0, 50.0]:
    v, _ = make_field(X5, Y5, 0.7, np.array([0.2]), ww)
    ds = []; ends = []
    for _ in range(60):
        sol = run(v, rng.standard_normal(2)); e = sol.y[:, -1]
        ds.append(np.min(np.linalg.norm(X5 - e, axis=1))); ends.append(np.argmin(np.linalg.norm(X5 - e, axis=1)))
    print(f"   w={ww}: max dist to nearest atom {max(ds):.2e}; #distinct atoms reached {len(set(ends))}; max|x_end| = {max(np.linalg.norm(sol.y[:, -1]) for _ in [0]):.2f}")

# ---------------------------------------------------------------- (4) 1-D, N=2: fast-dynamics fixed points
print("\n(4) N=2, d=1, atoms +-1. z = x t/(1-t)^2 ; m(z)=(1+w)tanh(z+b)-w tanh(z), b=0.5*log(a/(1-a))")
zz = np.linspace(-40, 40, 400001)
for w in [0, 1, 3, 12, 100]:
    for b in [0.0, 0.3, 1.0, 3.0]:
        g = (1 + w) * np.tanh(zz + b) - w * np.tanh(zz)
        roots = zz[:-1][np.sign(g[:-1]) != np.sign(g[1:])]
        stable = [r for r in roots if ((1 + w) / np.cosh(r + b) ** 2 - w / np.cosh(r) ** 2) < 0]
        if len(roots) != 1 or stable:
            print(f"   w={w} b={b}: roots {np.round(roots,3)}, stable roots {np.round(stable,3)}")
print("   (only cases with !=1 root or a stable root are printed)")
# simulate N=2 with h>0, w=12: fraction of random x0 ending away from atoms
Xa = np.array([[-1.0], [1.0]]); Ya = np.array([[0.0], [1.0]])
for ww in [3.0, 12.0, 100.0]:
    v, _ = make_field(Xa, Ya, 0.7, np.array([0.5]), ww)
    ends = np.array([run(v, rng.standard_normal(1)).y[0, -1] for _ in range(80)])
    print(f"   N=2,h=0.7,w={ww}: endpoints in {sorted(set(np.round(ends,2)))}  (max dist to atoms {np.min(np.abs(ends[:,None]-Xa.T),axis=1).max():.1e})")
# equidistant y (a=1/2) and symmetric start x0=0 => x_t = 0 for all t (non-atom endpoint, measure-zero start)
Ya = np.array([[-1.0], [1.0]])
for ww in [0.0, 3.0]:
    v, _ = make_field(Xa, Ya, 0.7, np.array([0.0]), ww)
    print(f"   equidistant y, x0=0, w={ww}: x(1-1e-6) = {run(v, np.array([0.0])).y[0,-1]:.3e}; generic x0=0.3 ->", np.round(run(v, np.array([0.3])).y[0, -1], 5))
# N=1
X1 = np.array([[2.0, -1.0]]); v, _ = make_field(X1, np.array([[0.]]), 0.7, np.array([0.3]), 5.0)
print("   N=1, w=5, x0=(3,3): end", np.round(run(v, np.array([3., 3.])).y[:, -1], 5), "(atom (2,-1))")
# exactly coincident atoms
Xc = np.array([[1.0, 0.0], [1.0, 0.0], [-1.0, 1.0]]); Yc = np.array([[0.], [0.5], [1.]])
v, _ = make_field(Xc, Yc, 0.7, np.array([0.2]), 3.0)
print("   coincident atoms: end", np.round(run(v, np.array([0.3, 0.3])).y[:, -1], 5))
