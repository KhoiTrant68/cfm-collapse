"""Tighter re-check of tgtnoise: MC at t=0.9 with more samples, and vectorised RK4 for the endpoint law (3e4 paths)."""
import numpy as np
rng = np.random.default_rng(1)
x_at = np.array([-1.5, 0.3, 2.0]); y_at = np.array([-1.0, 0.2, 0.9]); N = 3
h, rho = 0.5, 0.4
def vfield(x, t, y):
    s2 = (1 - t) ** 2 + t ** 2 * rho ** 2
    lw = -(x[:, None] - t * x_at) ** 2 / (2 * s2) - (y - y_at) ** 2 / (2 * h * h)
    w = np.exp(lw - lw.max(1, keepdims=True)); w /= w.sum(1, keepdims=True)
    return (w * (x_at + (t * rho ** 2 - (1 - t)) / s2 * (x[:, None] - t * x_at))).sum(1)
# MC at (x=1.0,t=0.9,y=0.9)
x, t, y = 1.0, 0.9, 0.9
num = 0; cnt = 0; sq = 0
for _ in range(6):
    m = 10_000_000
    I = rng.integers(0, N, m); X0 = rng.standard_normal(m); xi = rng.standard_normal(m); eps = rng.standard_normal(m)
    X1 = x_at[I] + rho * xi; Xt = (1 - t) * X0 + t * X1; Y = y_at[I] + h * eps
    sel = (np.abs(Xt - x) < 0.03) & (np.abs(Y - y) < 0.05)
    U = (X1 - X0)[sel]; num += U.sum(); sq += (U**2).sum(); cnt += sel.sum()
mu = num / cnt; se = np.sqrt((sq / cnt - mu**2) / cnt)
print(f"MC={mu:.4f} +- {se:.4f} (n={cnt}); formula={vfield(np.array([x]), t, y)[0]:.4f}")
# vectorised RK4 endpoint law, t in [0,1] (field smooth at t=1 because rho>0)
y0 = 0.1; n = 30_000; xs = rng.standard_normal(n); K = 400; dt = 1.0 / K
for k in range(K):
    tt = k * dt
    k1 = vfield(xs, tt, y0); k2 = vfield(xs + dt/2*k1, tt + dt/2, y0); k3 = vfield(xs + dt/2*k2, tt + dt/2, y0); k4 = vfield(xs + dt*k3, tt + dt, y0)
    xs = xs + dt/6*(k1 + 2*k2 + 2*k3 + k4)
p = np.exp(-(y0 - y_at) ** 2 / (2 * h * h)); p /= p.sum()
m_th = (p * x_at).sum(); v_th = (p * (x_at - m_th) ** 2).sum() + rho ** 2
print(f"endpoint mean {xs.mean():.4f} (theory {m_th:.4f}, se {xs.std()/np.sqrt(n):.4f}); var {xs.var():.4f} (theory {v_th:.4f})")
# compare CDF with mixture of N(x_i, rho^2)
from scipy.stats import norm
grid = np.linspace(-3, 3.5, 14)
emp = np.array([(xs < g).mean() for g in grid]); th = np.array([(p * norm.cdf((g - x_at) / rho)).sum() for g in grid])
print("max |empirical CDF - mixture CDF| =", np.abs(emp - th).max())
