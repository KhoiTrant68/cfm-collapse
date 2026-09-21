import re, math
t = open(r'D:\AwesomeCV\cfm-collapse\paper\main.tex', encoding='utf8').read()
labels = set(re.findall(r'\\label\{([^}]+)\}', t))
refs = re.findall(r'\\(?:ref|eqref|autoref|proofin)\{([^}]+)\}', t)
print('missing label targets:', sorted(set(r for r in refs if r not in labels)))

# Part 3 recomputation
print('200^(-1/2)  =', round(200 ** -0.5, 4))
print('2000^(-1/3072) =', round(2000 ** (-1 / 3072), 5))
print('2000^(-1/1536) =', round(2000 ** (-1 / 1536), 5), '(if the relevant dim is the unobserved half)')
print('2000^(-2/3072) =', round(2000 ** (-2 / 3072), 5))
d, L = 2, 65.7
fl = d / (3 * L)
print('d/(3L) =', round(fl, 5), ' plateau/floor =', round(0.48 / fl, 1))
print('ln 25 =', round(math.log(25), 3))
# the atoms-floor at d=2, N=200 in W2^2 units and the log-corrected iid rate
print('sqrt(log N / N) at N=200 =', round(math.sqrt(math.log(200) / 200), 3))
# Shannon lower bound for Gaussian target: D >= d det(S)^(1/d) N^(-2/d); ratio to tr S = geom/arith mean * N^(-2/d)
for N, dd in [(200, 2), (2000, 3072)]:
    print('N^(-2/d) N=%d d=%d: %.5f' % (N, dd, N ** (-2 / dd)))
# 2-point check of counterexample in prop:moments
import numpy as np
y = np.array([0., 1., 10.]); x = np.array([0., 10., 0.])
for h in (0.05, 2.0, 1e3):
    w = np.exp(-0.5 * (y / h) ** 2); w /= w.sum(); m = w @ x
    print('h=%g p=%s trCov=%.3f' % (h, np.round(w, 6), w @ (x - m) ** 2))
print('200/9 =', round(200 / 9, 3))
