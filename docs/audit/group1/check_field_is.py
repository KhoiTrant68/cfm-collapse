"""Higher-precision brute-force check of v* via importance sampling: E[U | X_t=x (window), Ytilde=y (window)].
Proposal: X_t ~ N(x, b^2 I) directly (so X_0=(X_t - t x^I)/(1-t)), weight = joint density ratio."""
import numpy as np
rng = np.random.default_rng(5)

def closed(x, t, y, X, Y, h):
    lw = -np.sum((x - t * X) ** 2, 1) / (2 * (1 - t) ** 2) - np.sum((y - Y) ** 2, 1) / (2 * h ** 2)
    w = np.exp(lw - lw.max()); w /= w.sum()
    return (w[:, None] * (X - x) / (1 - t)).sum(0)

def is_mc(x, t, y, X, Y, h, n=8_000_000, b=0.004, bw=0.06):
    N, d = X.shape; k = Y.shape[1]
    I = rng.integers(0, N, n)
    Xt = x + b * rng.standard_normal((n, d))
    X0 = (Xt - t * X[I]) / (1 - t)
    # density of (X_t) under model / proposal density (Jacobian (1-t)^-d common to all i, cancels in SNIS)
    lw = -0.5 * (X0 ** 2).sum(1) + 0.5 * ((Xt - x) ** 2).sum(1) / b ** 2
    eps = rng.standard_normal((n, k)); Yt = Y[I] + h * eps
    lw += -0.5 * ((Yt - y) ** 2).sum(1) / bw ** 2 * 1.0   # Gaussian window in y
    U = X[I] - X0
    w = np.exp(lw - lw.max())
    return (w[:, None] * U).sum(0) / w.sum()

for d, k, N, h in [(2, 1, 3, 0.5), (2, 2, 3, 1.0), (3, 2, 5, 0.8)]:
    X = rng.normal(size=(N, d)) * 1.5; Y = rng.normal(size=(N, k))
    for t in [0.3, 0.8]:
        x = t * X[1] + (1 - t) * rng.normal(size=d) * 0.7
        y = Y[1] + 0.3 * rng.normal(size=k)
        print(f'd={d} k={k} N={N} h={h} t={t}: closed={np.round(closed(x,t,y,X,Y,h),4)}  IS-MC={np.round(is_mc(x,t,y,X,Y,h),4)}')
