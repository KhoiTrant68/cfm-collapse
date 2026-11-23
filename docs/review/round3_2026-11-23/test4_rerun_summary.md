# Test 4 (thm:relerr) rerun, main session, 2026-11-23

Same script as numeric/test4b_split.py (copied with the fixed exactflow.py), horizon extended to tau=160
(1-t = e^-160); landing = distance to nearest atom < 1e-6 at the last tau. Variants 4 and 13 hang near
the float floor (~1e-13) beyond tau~40, so they were run to tau=40 only, with a 4-minute limit.

| variant | lands | n(40)/n(2) measured vs predicted | reading |
|---|---|---|---|
| rho=0.3 radial | yes | 2.99e-12 vs 2.80e-12 | (b) |
| rho=0.6 radial | yes | 2.505e-07 vs 2.505e-07 | (b) |
| rho=0.9 radial | yes at tau=160 (no at 40) | 2.237e-02 vs 2.237e-02 | (b); round-1 "fail" was the tau=40 cutoff |
| rho=0.99 radial | no by tau=160 (n=0.20) | 6.839e-01 vs 6.839e-01 | (b) says it lands, at rate (1-t)^0.01: not reachable in floating point |
| rho=0.9 + gamma 0.3(1-t)^0.3 outward | yes | (no formula) | (b) with vanishing gamma |
| rho=0.9 + gamma 0.05 constant | no, stalls at 0.50 = gamma/(1-rho) | (no formula) | hypothesis of (b) violated on purpose |
| (c) 1-rho=0.6(1-t)^0.5 | no, stalls 0.41 | 0.6431 vs 0.6431 | (c): integral of (1-rho) finite |
| (c) 1-rho=0.6(1-t)^0.1 | no, stalls 3.5e-3 | 8.209e-03 vs 8.209e-03 | (c) |
| (c) 1-rho=0.6/(1+tau)^2 | no, stalls 0.68 | 0.8308 vs 0.8308 | (c) |
| 1-rho=0.6/(1+tau), integral diverges | still shrinking (0.06 at 160) | 0.2083 vs 0.2083 | lands like tau^-0.6, too slow to see |
| 1-rho=2/(1+tau), integral diverges | still shrinking (1.1e-4 at 160) | 5.354e-03 vs 5.354e-03 | lands like tau^-2 |
| rho=1 exactly | no, frozen | 1.000 | (d) |
| rho=0.9, error rotated 90 deg | yes | follows e^-tau until float floor 3e-13 | lands faster than radial: radial ratio ~0 |
| rho_t=1 but error rotated 60 deg (e = n) | yes | 5.603e-09 vs 5.603e-09 | lands although e/n = 1: the radial ratio (0.5), not e/n, decides |

Verdict: every variant agrees with thm:relerr. No variant contradicts the theorem. The earlier "fails" came
from the tau=40 landing threshold and from the solver hanging at the float floor, not from the theorem.
Caveat for paper B: at rho ~ 0.99 (EDM measures ~0.997) landing and stopping short cannot be told apart at
any practical cutoff, so the EDM evidence is "consistent with", not a test of, the theorem.
