"""Integrate the ODE dx/dt = v*(x,t,y) with the closed form to t=1-e^{-s}, compare endpoint law
with sum_i p_i^{(h)}(y) delta_{x^i} (Thm endpoint), cor zerobw / infbw, moments (Prop moments),
and check whether individual trajectories actually converge as t->1.
Time change s=-log(1-t): dx/ds = m(x,t) - x, m = sum_i w_i x^i."""
import numpy as np
from scipy.integrate import solve_ivp

rng = np.random.default_rng(1)

def make_rhs(X, Y, y, h, B, d):
    N = X.shape[0]
    if h is None:  # unconditional
        lab = np.zeros(N)
    elif h > 0:
        lab = -np.sum((y - Y) ** 2, 1) / (2 * h ** 2)
    else:
        lab = np.where(np.all(np.isclose(Y, y), 1), 0, -np.inf)
    def rhs(s, z):
        x = z.reshape(B, d)
        t = 1 - np.exp(-s); om = np.exp(-s)
        lw = -((x[:, None, :] - t * X[None]) ** 2).sum(-1) / (2 * om ** 2) + lab[None]
        lw -= lw.max(1, keepdims=True)
        w = np.exp(lw); w /= w.sum(1, keepdims=True)
        return ((w @ X) - x).ravel()
    return rhs

def run(X, Y, y, h, B=6000, smax=16.0, checkpoints=(6, 10, 16)):
    d = X.shape[1]
    x0 = rng.standard_normal((B, d))
    sol = solve_ivp(make_rhs(X, Y, y, h, B, d), (0, smax), x0.ravel(), method='LSODA',
                    rtol=1e-8, atol=1e-10, t_eval=list(checkpoints))
    traj = [sol.y[:, j].reshape(B, d) for j in range(len(checkpoints))]
    return traj

def nw(Y, y, h):
    lw = -np.sum((y - Y) ** 2, 1) / (2 * h ** 2); lw -= lw.max()
    p = np.exp(lw); return p / p.sum()

d, k, N = 2, 1, 4
X = np.array([[0., 0.], [3., 0.], [0., 3.], [3.5, 3.5]])
Y = np.array([[0.], [1.], [2.], [3.5]])
y = np.array([1.2])
for h in [0.3, 1.0, 3.0]:
    p = nw(Y, y, h)
    tr = run(X, Y, y, h)
    fin = tr[-1]
    idx = np.argmin(((fin[:, None] - X[None]) ** 2).sum(-1), 1)
    freq = np.bincount(idx, minlength=N) / len(idx)
    dist = np.sqrt(((fin[:, None] - X[None]) ** 2).sum(-1).min(1))
    B = len(idx); se = np.sqrt(p * (1 - p) / B)
    print(f'h={h}: p_i={np.round(p,4)}  empirical={np.round(freq,4)}  max|diff|/SE={np.max(np.abs(freq-p)/np.maximum(se,1e-9)):.2f}')
    print(f'    max dist to nearest atom at s=16: {dist.max():.2e}; s=10: {np.sqrt(((tr[1][:,None]-X[None])**2).sum(-1).min(1)).max():.2e}')
    print(f'    trajectory move between s=10 and s=16 (max): {np.abs(tr[2]-tr[1]).max():.2e}')
    # moments
    xbar = p @ X; C = ((X - xbar).T * p) @ (X - xbar)
    print('    moments closed tr', np.trace(C).round(4), ' empirical tr', np.trace(np.cov(fin.T, bias=True)).round(4))

# h -> 0 : y=y^i exact label with h small; and h=0 hard flow
p = nw(Y, Y[1], 0.05); print('h=0.05,y=y^1: p=', np.round(p, 6))
tr = run(X, Y, Y[1], 0.0, B=500)
print('h=0 hard label y=y^1: endpoints all at x^1?', np.abs(tr[-1] - X[1]).max())
# infinite bandwidth vs unconditional flow
tr_u = run(X, Y, y, None, B=6000)
idx = np.argmin(((tr_u[-1][:, None] - X[None]) ** 2).sum(-1), 1)
print('uncond freq', np.bincount(idx, minlength=N) / len(idx), 'target 0.25 each')
p = nw(Y, y, 1e4); print('h=1e4 p=', np.round(p, 6))

# unique nearest label, small h
p = nw(Y, np.array([1.2]), 0.05); print('zerobw h=0.05, y=1.2 (nearest label 1):', np.round(p, 8))

# ---- Prop moments example ----
Yx = np.array([0., 1., 10.]); Xx = np.array([0., 10., 0.])
for h in [0.05, 0.5, 1, 2, 3, 5, 10, 50, 1e3]:
    p = nw(Yx[:, None], np.array([0.]), h)
    xb = p @ Xx; v = p @ (Xx - xb) ** 2
    print(f'moments example h={h}: p={np.round(p,6)} tr={v:.4f}')
print('tr Xhat =', np.var(Xx), '=200/9 =', 200 / 9)
