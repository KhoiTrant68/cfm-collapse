# Numerical stress tests of papers A and B (round 3)

Repo: cfm-collapse, branch paper-split-drafts, commit 834f3bf. I did not modify the repo.
Scripts and raw outputs are in `.../round3/numeric/`: `exactflow.py` (the integrator), `test1_twofields.py`, `test1b_extremes.py`, `test2_twoatom.py`, `test2b_nearthreshold.py`, `test3_signrule.py`, `test4_relerr.py`, `test4b_split.py`, `test5_triangle.py`, `test5b_paired.py`, plus `*.json` and `*.log`.

## Conventions and method (checked against the papers)

- Paper A, eq. (prior-field): linear interpolant X_t=(1-t)X_0+tX_1, X_0~N(0,I). v_p=sum_j q_{p,j}(x^j-x)/(1-t), with q_{p,j} proportional to p_j exp(-|x-t x^j|^2/(2(1-t)^2)). Paper B uses the same form, v*=(m*-x)/(1-t).
- A combination sum c_k v_{p_k} with sum c_k=1 is integrated in log-time tau=-log(1-t) as dx/dtau = mbar - x. The integrator is an explicit, per-sample adaptive Dormand-Prince 5(4) with rtol 1e-8 and atol min(1e-10, 1e-7/beta), where beta=t/(1-t)^2. It is explicit on purpose: an L-stable implicit step would wrongly stabilise repelling ties and create fake blends.
- Logits are computed as pairwise differences relative to the nearest scaled atom, and 1-t is taken as exp(-tau) directly. A first version computed 1-t as 1.0-t; that broke at tau>36, which only the tau=40 runs of test 4 reach. I fixed it and re-ran the sanity check, which gave identical results.
- Stopping rules:
  - atom: |x-a| < 0.25 times the separation of a, and every component posterior puts more than 1-1e-9 on a;
  - tie: the support has at least 2 atoms, its circumcentre z has exactly those atoms as nearest atoms, and the blown-up position xi=beta*P_L(x-tz) satisfies |xi|<20 over an accumulated fast time sigma (d sigma = beta d tau) of at least S_stop;
  - otherwise "unresolved" when tau reaches tau_max.
- **Cutoff:** tau_max=13 (1-t = 2.3e-6) for tests 1, 2, 3 and 5. In float64 the logit error grows like 1e-16*e^{2tau}, about 1e-5 at tau=13. The default is S_stop=1e3; tests 2 and 5 also ran with 1e4, 1e5 and 1e6 as sensitivity checks. Test 4 runs to tau=40 (1-t=4e-18) with rtol 1e-12.
- **Not run:** in every test below, no source was left unresolved.
- **Independence:** the stopping rules are modelled on the paper's two-stage idea (a blown-up profile, sigma windows), but the code was written from scratch. I did not run or read the repo scripts.

## Test 1: cor:twofields (any two exact fields with positive priors)

**Setup.**
- Main run: 148 configurations with d in {1,2,8} and N=3..8. Atom sets are random Gaussian, cospherical (every atom tied at 0, the worst case), or a regular simplex.
- Four recipes per geometry:
  - random c in [-4,5] with random log-priors (sd 2);
  - guidance (1+w)v_p - w v_unif with w in {0.5,2,8};
  - negative prompting by substitution, v_neg + s(v_pos - v_neg) with s in {1.5,3,7.5}, the priors peaked (+3) on different atoms;
  - c=-3 with opposed peaked priors.
- 384 Gaussian sources per configuration.
- Extremes run (`test1b`): triangle, square, cube corners (d=3) and three collinear atoms. c in {-10,10,30}, priors either near-tied or opposed, plus a bounded-variation guidance schedule w(t)=0, then 12 on [0.5,0.9), then 3. 1024 sources each.

**Prediction.** The endpoint is an atom almost surely.

**Measured.**

| run | configurations | sources | fraction at an atom | ties | unresolved |
|---|---|---|---|---|---|
| main (d=1/2/8) | 24/52/72 | 56,832 | 1.000 in every configuration | 0 | 0 |
| extremes and schedule | 28 | 28,672 | 1.000 in every configuration | 0 | 0 |

**Positive control.** The same code does detect blends when they exist (tests 2, 3 and 5).

**Verdict: agrees.**

## Test 2: prop:twoatom(c) / thm:composition threshold w_c = 1/sinh^2 B

**Setup.**
- d=1, atoms at -1 and 1, the field (1+w)/2 [v_{+B} + v_{-B}] - w v_unc. The priors have log-odds +-2B, so B(p) = +-B.
- On the line, flows preserve order, so the basin of 0 is an interval (-x+, x+). I located x+ by bisection (40 halvings) and set P0 = 2 Phi(x+) - 1.
- Spot checks: Monte Carlo with 4096 sources.

**Prediction.**
- P0=0 for w <= w_c (only the source 0 reaches the midpoint), and P0>0 for w > w_c.
- Near the threshold, the paper's formal law P0 ~ sqrt(2/pi)(w/w_c - 1)/cosh B.
- Unstable roots at cosh s_u = sqrt(w) sinh B.
- Table tab:composition.

**Measured** (S_stop=1e4; rows marked * re-run with S_stop=1e5 and 1e6, which agree with each other):

| B | w/w_c=0.5 | 0.9 | 0.99 | 1.01 | 1.03 | 1.1 | 1.5 | 2 | 5 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0 | 0 | 0 | 0.00705 | 0.02102 | 0.0685 | 0.3007 | 0.5134 | 0.9463 | 0.9987 |
| 1 | 0 | 0 | 0 | 0.00516 | 0.01540 | 0.0504 | 0.2286 | 0.4059 | 0.8783 | 0.9915 |
| 2 | 0 | 0 | 0* | 0.00212 | 0.00633 | 0.0208 | 0.0978 | 0.1824 | 0.5322 | 0.8093 |
| 3 | 0 | 0* | 0* | 0.00079* | 0.00237* | 0.0078 | 0.0368 | 0.0694 | 0.2208 | 0.3958 |

- **Near-threshold law** at w/w_c=1.01: 0.00708, 0.00517, 0.00212 and 0.00079. These match the measured values to within 0.5%.
- **Unstable roots:** the numerical s_u equals the closed form in every case (to 5 digits).
- **Paper table tab:composition:**
  - B=1: w/w_c = 1.1, 2 and 10, and w = 1 and 3: 0.050, 0.406, 0.991, 0.179, 0.808. I get 0.0504, 0.4059, 0.9915, 0.1793, 0.8083.
  - B=2: 0.021, 0.182, 0.809, 0.891, 0.999. I get 0.0208, 0.1824, 0.8093, 0.8912, 0.9990.
  - B=3: 0.008, 0.069, 0.396, 0.987, >0.999. I get 0.0078, 0.0694, 0.3958, 0.9873, 0.99994.
  - All entries agree to 3 decimals.
- **Monte Carlo (4096)** agrees with the bisection values within sampling error.

**Discretisation artefact, now resolved.**
- With S_stop=1e4, three sub-threshold entries came out spuriously positive: B=3, w/w_c=0.99 gave P0=3.4e-4, and B=2 and 3 gave x+ of about 1e-6.
- B=3, w/w_c=1.01 was overestimated: 0.00109 against the law's 0.00079.
- Cause: near threshold the tie repels only at rate F'(0) = sech^2 B (1 - w/w_c), about 1e-4 at B=3. So sources need a fast time of sigma >> 1e4 to leave the tie.
- With S_stop=1e5 or 1e6, all sub-threshold entries are 0 (x+ at the bisection floor of 7e-13), and B=3 at 1.01 gives 0.00079.
- This is a stopping-rule artefact, not a disagreement. The paper's barrier-based stopping rule avoids it.

**Not tested:** w = w_c exactly.

**Verdict: agrees.** The transition sits at 1/sinh^2 B for all four values of B.

## Test 3: the "less decided" sign rule at a two-atom tie (prop:twoatom (a), (b))

**Setup.** Atoms (+-1, 0) in d=2 (and d=1). Each field is described by its restricted log-odds B(p). 4096 sources per named recipe.

**Prediction.**
- A blend needs a subtracted field that lies strictly between the extremes in B and is subtracted.
- With three distinct values B1 > B2 > B3, no blend if c2 >= 0, c1 <= 0 or c3 <= 0.
- (These are necessary conditions, not sufficient ones.)

**Measured (named recipes; the d=1 and d=2 results agree):**

| recipe (B values; coefficients) | rule | sink profile | P(midpoint) d=1 / d=2 | paper |
|---|---|---|---|---|
| conjunction B=1, w=2w_c | allowed | yes | 0.394 / 0.418 (bisection: 0.4059) | 0.406 |
| unequal conjunction (1.2, 0.8, -1), B=+-2 | allowed | yes | 0.742 / 0.740 | 0.742 |
| pos a / neg b, unconditional base (3,-1,-1), B=+-2 | forbidden by (b) | no | 0 / 0 | 0 |
| pos a / neg b substituted, 3v_a - 2v_b | forbidden | no | 0 / 0 | 0 |
| pos B=2 (0.91), milder neg B=0.25 (-4), unconditional 4.09 | allowed | yes | 0.323 / 0.317 | 0.316 |
| neg prompt more decided: pos B=0.25 (4), neg B=2 (-1), unconditional (-2) | forbidden | no | 0 / 0 | - |
| neg more decided: 6 v_{B=1} - 5 v_{B=3} | forbidden | no | 0 / 0 | - |
| neutral negative B=0, grouped with the unconditional: 2v_{B=2} - v_0 | forbidden | no | 0 / 0 | - |
| subtract middle strongly (1.5, 1.5, -2), B=+-2, 0 | allowed | yes | 0.988 / 0.990 | - |
| subtract an extreme: (2, 1, -2) on B = 2, 0, -2 | forbidden | no | 0 / 0 | - |
| subtract both extremes: (-1, 3, -1) | forbidden | no | 0 / 0 | - |

**Random search.** 3000 combinations of 2 to 5 fields, with B uniform in [-4,4] and coefficients ~N(0,2) adjusted to sum to one.
- 1424 are forbidden by (a). Of these, 0 have a sink profile.
- 575 three-field combinations meet the hypotheses of (b). Of these, 0 have a sink profile.
- 209 combinations have a sink profile, and all of them subtract an inner field.

**Flow simulations on the random combinations** (256 sources each, d=1):

| group | combinations | combinations with P>0 | detail |
|---|---|---|---|
| forbidden | 120 | 0 | max P = 0 |
| allowed with a sink profile | 120 | 106 | mean P = 0.71; the other 14 have a basin below 1/256 |
| allowed without a sink | 60 | 0 | - |

**Verdict: agrees.**
- Subtracting a less-decided (middle) field can blend.
- Subtracting a more-decided field, or a negative prompt against one example, never did.
- The sufficiency gap is as the paper says.

## Test 4: thm:relerr (paper B)

**Setup.**
- d=2, five atoms with a positive label-noise prior.
- Gaussian sources: 200 for the first four rows, 60 for the rest, which were run in parallel to save time.
- Perturbed predictor x_hat1 = m* + rho_t (Z - m*), plus the variants listed in the table.
- Integrated in tau up to 40. n is measured to the final nearest atom.
- For radial errors, the prediction is n_40/n_2 = exp(-int_2^40 (1 - rho) dtau).
- In this construction e/n tends to rho_t as m* concentrates on a, and the radial ratio tends to rho_t as well. This makes part of the check close to tautological. The non-radial and gamma variants are the substantive ones.

**Measured** (median n at tau = 5 / 10 / 20 / 40; n40/n2 measured against predicted):

| variant | theorem says | n at tau 5 / 10 / 20 / 40 | n40/n2 meas / pred | verdict |
|---|---|---|---|---|
| rho=0.3 | lands (b) | 4.6e-2 / 1.4e-3 / 1.3e-6 / 1.1e-12 | 3.0e-12 / 2.8e-12 (rtol floor) | lands |
| rho=0.6 | lands | 0.17 / 2.3e-2 / 4.2e-4 / 1.4e-7 | 2.505e-7 / 2.505e-7 | lands, rate (1-t)^0.4 |
| rho=0.9 | lands | 0.62 / 0.38 / 0.14 / 1.9e-2 | 2.24e-2 / 2.24e-2 | lands at rate (1-t)^0.1 |
| rho=0.99 | lands | 0.92 / 0.87 / 0.79 / 0.65 | 0.684 / 0.684 | lands at rate (1-t)^0.01 (not visible at any cutoff) |
| rho=0.9, error rotated 90 degrees | lands | 1.4e-2 / 9.1e-5 / 4.1e-9 / 2.6e-13 | - | lands faster than radial |
| rho=0.9 plus constant gamma=0.05, outward | (b) needs gamma -> 0 | 0.83 / 0.70 / 0.57 / 0.51 | - | stalls near gamma/(1-rho)=0.5: misses |
| 1-rho = 0.6(1-t)^0.5 | misses (c) | 0.45 / 0.41 / 0.406 / 0.406 | 0.643 / 0.643 | positive limit |
| 1-rho = 0.6(1-t)^0.1 | misses (c) | 0.13 / 3.2e-2 / 7.9e-3 / 3.9e-3 | 8.2e-3 / 8.2e-3 (limit 7.4e-3 of n2) | positive limit, approached slowly |
| 1-rho = 0.6/(1+tau)^2 | misses (c) | 0.75 / 0.71 / 0.69 / 0.68 | 0.831 / 0.831 | positive limit |
| 1-rho = 0.6/(1+tau) (integral diverges) | neither (b) nor (c) applies | 0.45 / 0.31 / 0.21 / 0.14 | 0.208 / 0.208 | -> 0 like tau^-0.6 |
| 1-rho = 2/(1+tau) (integral diverges) | neither applies | 7.9e-2 / 2.3e-2 / 6.4e-3 / 1.7e-3 | 5.35e-3 / 5.35e-3 | -> 0 like tau^-2 |
| rho=1 exactly (d) | rho_bar=1 not enough | 0.999 at every tau | 1.000 | frozen, does not land |
| rho_t=1 but rotated 60 degrees (e=n) | the paper remarks this can land | still running at write-up | - | inconclusive (not finished) |
| rho=0.9 plus gamma=0.3(1-t)^0.3 | lands | still running at write-up | - | inconclusive (not finished) |

**Verdict: agrees** on every finished variant.
- Constant rho_bar < 1 lands, at exactly the rate (1-t)^{1-rho}.
- An integrable 1-rho_t gives a positive limit, which matches (c) and the paper's figure (c), where 1-rho = 0.6(1-t)^{1/2}.
- rho=1 freezes, which matches (d).
- With a non-integrable 1-rho ~ c/tau the trajectory still lands, but only logarithmically. The rate condition in (c) is therefore the right dividing line.

**Practical caveat.** At rho >= 0.9, no finite cutoff shows "landing" (at tau=40, n is still 0.02 for rho=0.9 and 0.65 for rho=0.99). A finite-time experiment cannot tell rho=0.99 from case (c). This is a measurement limitation, not a disagreement with the theorem. It matters for how paper B reads measured rho near 1 in EDM (rho of about 0.997 is cited).

**Not finished.** Two variants did not complete in time: the rotation with rho=1, and the vanishing gamma.

## Test 5: paper A Fig. unrolled(c) (triangle, B=2, 32768 sources, w=2w_c)

**Setup.**
- Equilateral triangle on the unit circle. Each condition's prior puts log-weight B on its own vertex.
- Coefficients (1+w)/3 on each conditional field and -w on the uniform unconditional field.
- w_c = (1-m^2)/m^2 = 1.1596 with m = (e^B - 1)/(e^B + 2). The edge threshold N/(2 tanh^2(B/2)) - 1 = 1.3678 w_c, which matches the paper's 1.368.
- Sources from seed 20261121, the paper's stated seed. My RNG stream use may differ from the paper's.

**Measured** (S_stop=1e3, no source unresolved):

| w/w_c | n | centre | edge midpoints | atoms | paper |
|---|---|---|---|---|---|
| 2 | 32768 | 0.1289 | 0.4102 | 0.4609 | 0.131 / 0.409 / 0.460 |
| 5 | 32768 | 0.6791 | 0.2966 | 0.0243 | 0.681 / 0.294 / 0.025 |
| 10 | 16384 | 0.9501 | 0.0497 | 0.0001 | 0.950 / 0.050 / 0.0001 |
| 1.1 | 16384 | 0.0009 | 0 | 0.9991 | centre 0.001, no edge |
| 1.3 (below edge threshold) | 16384 | 0.0128 | 0 | 0.987 | edge 0 predicted |
| 1.45 (above edge threshold) | 16384 | 0.0283 | 0.114 | 0.858 | edge > 0 predicted |

- The 13% and 41% in the caption are confirmed: 0.129 ± 0.002 and 0.410 ± 0.003.
- Paired check on the first 8192 sources: S_stop = 1e3 against 1e4 gives 0 class changes.
- The edge-midpoint threshold at 1.368 w_c is confirmed: no edge mass at 1.3, positive edge mass at 1.45.

**Verdict: agrees.**

## Plain-language summary (Vietnamese)

Mình viết lại "trường vận tốc chính xác" của flow matching (khi dữ liệu huấn luyện chỉ là vài điểm) và cho hàng chục nghìn điểm nhiễu chạy theo nó đến t gần 1, rồi xem chúng dừng ở đâu.
1. Trộn **hai** trường chính xác bất kỳ (guidance, negative prompt kiểu thay thế, hệ số âm hay rất lớn, kể cả lịch guidance thay đổi theo thời gian): 100% điểm đều rơi đúng vào một ảnh huấn luyện. Đúng như bài A nói.
2. Trộn **ba** trường kiểu "conjunction" (hai điều kiện cộng lại, trừ đi trường vô điều kiện): khi guidance w vượt 1/sinh^2 B thì một phần khối lượng rơi vào **trung điểm** giữa hai ảnh (một ảnh "pha trộn" không có trong tập huấn luyện); dưới ngưỡng thì không. Ngưỡng nằm đúng chỗ, và các con số trong bảng của bài A khớp đến 3 chữ số.
3. Quy tắc dấu: muốn ra ảnh pha trộn thì phải **trừ** đi một trường "lưỡng lự hơn" (ít nghiêng về ảnh nào hơn) so với các trường được cộng. Trừ một trường "quyết đoán hơn", hay negative prompt chống lại một ảnh, thì không bao giờ ra ảnh pha trộn (0/120 trường hợp ngẫu nhiên, 0/1424 kiểm tra đại số).
4. Bài B: nếu sai số của mạng luôn nhỏ hơn một tỉ lệ cố định (<1) của khoảng cách tới ảnh huấn luyện, quỹ đạo vẫn "chép" ảnh đó; nếu tỉ lệ này tiến về 1 đủ nhanh (tích phân hữu hạn), quỹ đạo dừng cách ảnh một khoảng dương, tức là sinh ảnh mới. Khớp hoàn toàn, nhưng khi tỉ lệ gần 1 (0.9-0.99) thì việc "chép" xảy ra cực chậm, thực nghiệm hữu hạn không phân biệt được.
5. Hình tam giác của bài A: 13% ở tâm, 41% ở trung điểm các cạnh: tái lập được (12.9% và 41.0%).

Không tìm thấy mâu thuẫn thật sự nào; những lệch nhỏ đều là do quy tắc dừng số học (đã giải thích và sửa).

## Things for a human (Khoi) to look at

1. **The stopping window near threshold** (test 2). A generic "stuck near the tie for sigma = 1e3 to 1e4" rule gives false blends just below w_c at large B, because the tie repels at rate sech^2 B (1 - w/w_c), about 1e-4. The paper uses barrier-based rules, which avoid this. Any other script in the repo that uses a fixed sigma window near threshold (for example the spectral table at 1.1 w_c, or the sigma-window classifier in `theory_basin_map.py`) should be checked for the same bias. The B=3, 1.1 w_c entries are the most exposed.
2. **rho close to 1 in paper B.** With rho = 0.99, n falls only to 0.65 of its value by 1-t = 4e-18. The paper's EDM evidence (rho of about 0.997 near sigma = 0.023) therefore cannot separate "lands slowly" from "stops short" at any practical cutoff. The wording should say measurements show the mechanism is consistent with the theorem, not that they test it.
3. **The figure's rho_t construction.** For x_hat1 = m* + rho(Z - m*), the radial ratio equals rho asymptotically, so the paper B figure illustrates the theorem almost by construction. A non-radial example, such as the 90-degree rotated error I used, makes a stronger illustration.
4. **The 0.406 conjunction number.** My 4096-source Monte Carlo runs gave 0.394 and 0.418. The bisection value (0.4059) is the reliable one and matches the paper. If the paper's figure value comes from Monte Carlo, its standard error is about 0.008.
5. **Not tested:** w = w_c exactly (non-hyperbolic), and two test 4 variants (rotation with rho=1, and vanishing gamma), which did not finish in time.
