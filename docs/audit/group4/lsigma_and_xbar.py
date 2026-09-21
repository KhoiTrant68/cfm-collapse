import numpy as np
from scipy.integrate import quad
# (A) cor:prop18 -- irreducible error of the pathwise target with gamma=sigma sqrt(t(1-t)), per coordinate:
#     Var(t) = 1 + gdot^2 - c^2 s^2 ; integrate over t in [eps,1-eps]
def var(t, s):
    g2 = s**2*t*(1-t); gd = s*(1-2*t)/(2*np.sqrt(t*(1-t)))
    s2 = (1-t)**2 + g2
    c = (-(1-t) + s**2/2*(1-2*t))/s2
    return 1 + gd**2 - c**2*s2
for s in (0.5, 1.0):
    print("sigma=%.1f" % s)
    for eps in (1e-2, 1e-4, 1e-6, 1e-8, 1e-10):
        val = quad(lambda t: var(t, s), eps, 1-eps, limit=500, points=[0.5])[0]
        print("  eps=%g  int Var dt = %.4f   (grows ~ %.3f*log(1/eps))" % (eps, val, s**2/4*2))
# (B) closed-form xbar_h vs huge-N sample (linear-Gaussian, k=1)
rng = np.random.default_rng(7)
d, so = 2, 0.1
A = np.array([[1.5410, -0.2934]]); S = float((A@A.T)[0,0]+so**2); B = (A.T/S)[:,0]
N = 4_000_000
X = rng.standard_normal((N, d)); Y = (X@A.T)[:,0] + so*rng.standard_normal(N)
for y0 in (0.4, 1.5):
    for h in (0.3, 1.0):
        w = np.exp(-0.5*((Y-y0)/h)**2); m = (w@X)/w.sum()
        cf = B*S/(S+h**2)*y0
        print("y=%.1f h=%.1f xbar_emp=%s  closed=%s  bias_emp=%s  -h^2 B y/S=%s" % (y0,h,np.round(m,4),np.round(cf,4),np.round(m-B*y0,4),np.round(-h**2*B*y0/S,4)))
