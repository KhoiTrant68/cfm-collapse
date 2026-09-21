"""Check closed-form v* (Prop kernel-field / collapse / uncond / repeated) against brute-force
Monte Carlo conditional expectation E[X1-X0 | X_t=x, t, Ytilde=y] (window / ABC) and against
numerical integration of the joint density."""
import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(0)

def vstar_closed(x, t, y, X, Y, h):
    """x:(d,), X:(N,d), Y:(N,k). h=0 -> hard label (needs y in Y)."""
    d = X.shape[1]
    lw = -np.sum((x - t * X) ** 2, 1) / (2 * (1 - t) ** 2)
    if h > 0:
        lw += -np.sum((y - Y) ** 2, 1) / (2 * h ** 2)
    else:
        lw += np.where(np.all(np.isclose(Y, y), 1), 0, -np.inf)
    lw -= lw.max()
    w = np.exp(lw); w /= w.sum()
    return (w[:, None] * (X - x) / (1 - t)).sum(0), w

def vstar_mc(x, t, y, X, Y, h, n=4_000_000, delta=0.04):
    N, d = X.shape
    k = Y.shape[1]
    I = rng.integers(0, N, n)
    X0 = rng.standard_normal((n, d))
    Xt = (1 - t) * X0 + t * X[I]
    U = X[I] - X0
    Yt = Y[I] + (h * rng.standard_normal((n, k)) if h > 0 else 0)
    m = np.all(np.abs(Xt - x) < delta, 1) & np.all(np.abs(Yt - y) < delta, 1)
    return U[m].mean(0), m.sum()

def vstar_quad_1d(x, t, y, X, Y, h):
    """d=k=1 exact via density integration: E[U|Xt=x,Y=y] = sum_i f_i(x,y) (x^i-x)/(1-t) / sum_i f_i"""
    f = norm.pdf((x - t * X[:, 0]) / (1 - t)) / (1 - t) * norm.pdf(y - Y[:, 0], scale=h)
    return (f * (X[:, 0] - x) / (1 - t)).sum() / f.sum()

for d, k, N, h in [(1, 1, 4, 0.7), (2, 1, 3, 0.5), (2, 2, 3, 1.0)]:
    X = rng.normal(size=(N, d)) * 1.5
    Y = rng.normal(size=(N, k))
    for t in [0.3, 0.8]:
        x = t * X[1] + (1 - t) * rng.normal(size=d) * 0.7
        y = Y[1] + 0.3 * rng.normal(size=k)
        vc, w = vstar_closed(x, t, y, X, Y, h)
        vm, cnt = vstar_mc(x, t, y, X, Y, h, delta=0.05 if d * k < 3 else 0.12, n=6_000_000)
        extra = ''
        if d == 1 and k == 1:
            extra = f' quad={vstar_quad_1d(x[0], t, y[0], X, Y, h):.4f}'
        print(f'd={d} k={k} N={N} h={h} t={t}: closed={np.round(vc,4)} MC={np.round(vm,4)} (n_acc={cnt}){extra}')

# hard label h=0 : v = (x^i - x)/(1-t) exactly (checks Prop collapse (a)) via MC
d, k, N = 2, 1, 4
X = rng.normal(size=(N, d)); Y = np.arange(N, dtype=float)[:, None]
for t in [0.4, 0.9]:
    x = t * X[2] + (1 - t) * rng.normal(size=d)
    vc, w = vstar_closed(x, t, Y[2], X, Y, 0)
    print('h=0 collapse:', vc, (X[2] - x) / (1 - t), 'w=', np.round(w, 3))
    # MC conditioning on exact label: keep I==2
    n = 2_000_000
    X0 = rng.standard_normal((n, d)); Xt = (1 - t) * X0 + t * X[2]
    m = np.all(np.abs(Xt - x) < 0.05, 1)
    print('   MC (I=2 exact label):', (X[2] - X0[m]).mean(0), m.sum())

# repeated labels: two atoms share a label
X = rng.normal(size=(4, 2)); Y = np.array([[0.], [0.], [1.], [2.]])
t = 0.6; x = t * X[0] + (1 - t) * rng.normal(size=2)
vc, w = vstar_closed(x, t, np.array([0.]), X, Y, 0)
q = np.exp(-np.sum((x - t * X[:2]) ** 2, 1) / (2 * (1 - t) ** 2)); q /= q.sum()
print('repeated: closed', vc, 'q-formula', (q[:, None] * (X[:2] - x) / (1 - t)).sum(0), 'w', np.round(w, 4), 'q', np.round(q, 4))
n = 6_000_000
I = rng.integers(0, 2, n)  # given Y=y, I uniform on {0,1}
X0 = rng.standard_normal((n, 2)); Xt = (1 - t) * X0 + t * X[I]
m = np.all(np.abs(Xt - x) < 0.05, 1)
print('   MC:', (X[I] - X0)[m].mean(0), m.sum())

# unconditional
X = rng.normal(size=(5, 2)); t = 0.5
x = t * X[3] + (1 - t) * rng.normal(size=2)
lw = -np.sum((x - t * X) ** 2, 1) / (2 * (1 - t) ** 2); q = np.exp(lw - lw.max()); q /= q.sum()
vc = (q[:, None] * (X - x) / (1 - t)).sum(0)
n = 6_000_000; I = rng.integers(0, 5, n); X0 = rng.standard_normal((n, 2)); Xt = (1 - t) * X0 + t * X[I]
m = np.all(np.abs(Xt - x) < 0.05, 1)
print('uncond: closed', vc, 'MC', (X[I] - X0)[m].mean(0), m.sum())
