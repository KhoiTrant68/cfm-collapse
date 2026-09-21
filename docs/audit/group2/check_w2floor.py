"""Audit check of prop:atomicity: W2^2(atomic law, posterior) >= F = E dist(X,{x^i})^2, independent of h.
Posterior N(0,I_2). Atoms: N iid N(0,I_2) points, labels y^i iid N(0,1), query y=0.3, kernel weights p_i^{(h)}.
Discrete OT via linear_sum_assignment on M posterior samples vs M atom-copies (multiplicities ~ M p_i)."""
import numpy as np
from scipy.optimize import linear_sum_assignment
rng = np.random.default_rng(5)
d, N, M = 2, 30, 1500
Xa = rng.standard_normal((N, d)); Ya = rng.standard_normal(N); y = 0.3
P = rng.standard_normal((M, d))                                  # posterior samples
Fbig = np.mean(np.min(((rng.standard_normal((400000, d))[:, None, :] - Xa[None]) ** 2).sum(-1), axis=1))
F_M = np.mean(np.min(((P[:, None, :] - Xa[None]) ** 2).sum(-1), axis=1))
print(f"F (400k MC) = {Fbig:.4f}; F on the M={M} OT sample = {F_M:.4f}")

def multiplicities(p, M):
    c = np.floor(p * M).astype(int); r = M - c.sum()
    idx = np.argsort(-(p * M - c))[:r]; c[idx] += 1; return c
for h in [0.05, 0.2, 0.5, 1.0, 3.0, 1e3]:
    lw = -(y - Ya) ** 2 / (2 * h * h); p = np.exp(lw - lw.max()); p /= p.sum()
    c = multiplicities(p, M); A = np.repeat(Xa, c, axis=0)
    C = ((P[:, None, :] - A[None]) ** 2).sum(-1)
    r, cc = linear_sum_assignment(C); w2 = C[r, cc].mean()
    # cost lower bound with the actual weights is >= F_M; also nearest-atom bound independent of h
    print(f"h={h:<7} n_eff={1/np.sum(p**2):6.2f}  W2^2(emp)={w2:.4f}  >= F_M={F_M:.4f} : {w2 >= F_M - 1e-12}   gap={w2 - F_M:.4f}")
# 1-D exact check: quantile coupling
print("\n1-D exact (quantile coupling), posterior N(0,1), N=30 atoms N(0,1):")
from scipy.stats import norm
xa = np.sort(rng.standard_normal(N)); F1 = np.mean(np.min((rng.standard_normal(2_000_000)[:, None] - xa[None]) ** 2, axis=1))
for h in [0.05, 0.5, 1e3]:
    ya = rng.standard_normal(N)
    lw = -(y - ya) ** 2 / (2 * h * h); p = np.exp(lw - lw.max()); p /= p.sum()
    order = np.argsort(rng.standard_normal(N)); xs = np.sort(xa); pp = p[np.argsort(xa)]
    cdf = np.r_[0, np.cumsum(pp)]; cdf[-1] = 1
    # W2^2 = sum_i int_{cdf_i}^{cdf_{i+1}} (Phi^{-1}(u) - x_i)^2 du
    from scipy.integrate import quad
    w2 = sum(quad(lambda u: (norm.ppf(u) - xs[i]) ** 2, max(cdf[i], 1e-12), min(cdf[i + 1], 1 - 1e-12))[0] for i in range(N) if cdf[i + 1] > cdf[i])
    print(f"   h={h}: exact W2^2={w2:.4f}   F={F1:.4f}   W2^2>=F: {w2 >= F1 - 5e-3}")
# N -> scaling of F: F ~ N^{-2/d}
print("\nF scaling (d=2): ", [(n, round(float(np.mean(np.min(((rng.standard_normal((50000, 2))[:, None, :] - rng.standard_normal((n, 2))[None]) ** 2).sum(-1), axis=1))), 4)) for n in [10, 40, 160, 640]])
