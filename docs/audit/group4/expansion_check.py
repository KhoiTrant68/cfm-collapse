"""Independent check of prop:expansion / prop:nwrate on the linear-Gaussian instance (d=2,k=1).
Own implementation (no torch). Compares empirical Cov_h(y) with
 (a) exact population law  Sigma_post + J J^T h^2 S/(S+h^2)   (S=Sigma_Y)
 (b) the proposition's     Sigma_post + h^2 J J^T
and checks (N h^k)^{-1/2} spread scaling, the plug-in bias and design-point self weight."""
import numpy as np
rng = np.random.default_rng(12345)
d, k, so = 2, 1, 0.1
A = np.array([[1.5410, -0.2934]])
S = float((A @ A.T)[0,0] + so**2)                       # Sigma_Y
B = (A.T / S)                                     # d x 1 = J
Spost = np.linalg.inv(np.eye(d) + A.T @ A / so**2)
assert np.allclose(B, Spost @ A.T / so**2)
J = B
print("S_Y=%.4f trSpost=%.5f |J|^2=%.4f" % (S, np.trace(Spost), (J**2).sum()))
y0 = 0.4

def sample(N):
    X = rng.standard_normal((N, d)); Y = X @ A.T + so * rng.standard_normal((N, k)); return X, Y

def covh(X, Y, y, h):
    w = np.exp(-0.5 * ((Y[:, 0] - y) / h) ** 2); w /= w.sum()
    m = w @ X; Xc = X - m
    return (Xc * w[:, None]).T @ Xc, w

def pop(h): return Spost + (J @ J.T) * h**2 * S / (S + h**2)
def prop(h): return Spost + (J @ J.T) * h**2

# (1) closed-form population law vs a huge-N sample (validates the Gaussian-tilt algebra itself)
print("\n(1) huge-N check of population law, N=4e6, y=%.1f" % y0)
Xb, Yb = sample(4_000_000)
for h in (0.3, 0.6, 1.0, 2.0):
    C, w = covh(Xb, Yb, y0, h)
    print(" h=%.1f  emp trace %.5f  exact %.5f  prop %.5f | max|emp-exact|=%.2e  max|emp-prop|=%.2e" %
          (h, np.trace(C), np.trace(pop(h)), np.trace(prop(h)), np.abs(C - pop(h)).max(), np.abs(C - prop(h)).max()))
del Xb, Yb

# (2) repeated draws: level, plug-in bias, spread scaling
print("\n(2) repeated draws (R=60): mean / sd of trace, relative to exact; predicted plug-in bias factor (1 - sum p^2)")
res = []
for N in (2000, 20000):
    for h in (0.03, 0.06, 0.12, 0.25, 0.5, 1.0):
        R = 60 if N == 2000 else 30
        tr = []; sp = []
        for _ in range(R):
            X, Y = sample(N); C, w = covh(X, Y, y0, h); tr.append(np.trace(C)); sp.append((w**2).sum())
        tr = np.array(tr)
        ex = np.trace(pop(h)); nhk = N * h
        # plug-in shrink: within part scales by (1-sum p^2)
        pred_b = ex - np.trace(Spost) * np.mean(sp)  # crude
        res.append((N, h, nhk, tr.mean(), tr.std(), ex))
        print(" N=%5d h=%.2f Nh^k=%8.1f  mean %.5f (exact %.5f, rel %+.4f, pred-with-shrink rel %+.4f) sd/mean=%.5f  sd*sqrt(Nh)=%.4f" %
              (N, h, nhk, tr.mean(), ex, tr.mean()/ex - 1, pred_b/ex - 1, tr.std()/tr.mean(), tr.std()*np.sqrt(nhk)))
r = np.array(res)
sel = r[:, 2] >= 30
sl = np.polyfit(np.log(r[sel, 2]), np.log(r[sel, 4] / r[sel, 3]), 1)[0]
print(" fitted slope of rel spread vs Nh^k (Nh^k>=30): %.3f (pred -0.5)" % sl)

# (3) is the h^2 J J^T term resolvable? signal vs noise, and prop-vs-exact gap
print("\n(3) signal h^2|J|^2 vs noise sd of trace (from above, N=2000)")
for (N, h, nhk, m, s, ex) in res:
    if N == 2000:
        print(" h=%.2f  h^2|J|^2=%.4f  exact inflation=%.4f  sd(trace)=%.4f  ratio signal/sd=%.2f  prop-vs-exact level gap=%.2f%%" %
              (h, h**2*(J**2).sum(), np.trace(pop(h)-Spost), s, h**2*(J**2).sum()/s, 100*(np.trace(prop(h))/ex-1)))

# (4) design point: y = y^i, weight of self, effect on mean
print("\n(4) design-point self weight K_h(0)/sum_j K_h(y^i-y^j) vs 1/(N h rho sqrt(2pi))")
N = 20000; h = 0.05
X, Y = sample(N)
ws = []
for i in range(0, N, 500):
    w = np.exp(-0.5 * ((Y[:, 0] - Y[i, 0]) / h) ** 2); ws.append((w[i] / w.sum(), Y[i, 0]))
ws = np.array(ws)
rho = np.exp(-0.5 * ws[:, 1]**2 / S) / np.sqrt(2 * np.pi * S)
pred = 1 / (N * h * rho * np.sqrt(2 * np.pi))
print(" median ratio measured/pred = %.3f ; min rho(y^i) among 40 queries %.3f ; max self weight %.4f" % (np.median(ws[:, 0]/pred), rho.min(), ws[:, 0].max()))
# extreme design point
i = np.argmax(np.abs(Y[:, 0])); w = np.exp(-0.5 * ((Y[:, 0] - Y[i, 0]) / h) ** 2)
print(" extreme design point |y|=%.2f: self weight %.3f, n_eff=%.1f (Nh rho... local sample tiny)" % (abs(Y[i,0]), w[i]/w.sum(), 1/((w/w.sum())**2).sum()))
