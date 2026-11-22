# Independent verification of the certificate analysis

Script: scripts/paperB_verify_certificate.py (numpy only). Off-atom = d1/d2 >= 1/3. Integrals are trapezoids in log sigma on the sampler grid; the late window runs from the grid point nearest sigma = 0.585 to sigma = 0.002.

## 0. Sanity

| run | n | off | K | max abs(n1_end - d1) | max abs(dD_last - d1) | anc_last = nn1 | median abs(err_last - d1)/d1 |
|---|---|---|---|---|---|---|---|
| sub2000 | 1000 | 501 | 18 | 1.9e-13 | 0.0e+00 | 1.0 | 1.23e-15 |
| sub500s1 | 1000 | 44 | 18 | 4.9e-13 | 0.0e+00 | 1.0 | 2.26e-14 |
| sub500_rho | 1000 | 41 | 18 | 5.0e-13 | nan | nan | 2.36e-14 |
| public_rho | 200 | 200 | 18 | 1.0e-13 | nan | nan | 3.74e-16 |
| s18_sub500 | 1000 | 41 | 18 | 6.5e-13 | nan | nan | 2.74e-14 |
| s36_sub500 | 1000 | 40 | 36 | 6.1e-13 | nan | nan | 2.80e-14 |
| s64_sub500 | 1000 | 39 | 64 | 4.4e-13 | nan | nan | 2.54e-14 |
| s18_public | 500 | 500 | 18 | 3.4e-13 | nan | nan | 9.15e-16 |
| s36_public | 500 | 500 | 36 | 3.1e-13 | nan | nan | 9.55e-16 |
| s64_public | 500 | 500 | 64 | 3.6e-13 | nan | nan | 9.16e-16 |
| anchor_sub500 | 1000 | 41 | 18 | 4.9e-13 | 0.0e+00 | 1.0 | 2.27e-14 |
| anchor_public | 500 | 500 | 18 | 8.5e-14 | 0.0e+00 | 1.0 | 3.41e-16 |

## 1. Identity log(n0/n1) = C_rad (gap = actual - trapezoid C_rad, late window)

| run | sigma0 | actual on | gap on | gap off | p1..p99 on | frac gap<0 on / off | max abs gap on | max abs interval gap above s0 | on with rad<0 late | gap on (rad<0 / rest) |
|---|---|---|---|---|---|---|---|---|---|---|
| sub2000 | 0.585 | 2.078 | -0.0307 | -0.0242 | [-0.057, -0.023] | 1.000 / 1.000 | 0.069 | 0.0082 | 3/499 | -0.058 / -0.031 |
| sub500s1 | 0.585 | 2.894 | -0.0395 | -0.0244 | [-0.250, -0.020] | 1.000 / 1.000 | 0.672 | 0.0087 | 253/956 | -0.084 / -0.034 |
| sub500_rho | 0.585 | 2.942 | -0.0427 | -0.0245 | [-0.358, -0.019] | 1.000 / 1.000 | 0.722 | 0.0161 | 308/959 | -0.089 / -0.033 |
| s18_sub500 | 0.585 | 2.942 | -0.0427 | -0.0245 | [-0.358, -0.019] | 1.000 / 1.000 | 0.722 | 0.0161 | 308/959 | -0.089 / -0.033 |
| s36_sub500 | 0.523 | 2.869 | -0.0096 | -0.0059 | [-0.053, -0.004] | 1.000 / 1.000 | 0.134 | 0.0043 | 295/960 | -0.018 / -0.008 |
| s64_sub500 | 0.562 | 2.946 | -0.0029 | -0.0018 | [-0.013, -0.001] | 1.000 / 1.000 | 0.026 | 0.0010 | 296/961 | -0.005 / -0.002 |
| anchor_sub500 | 0.585 | 2.942 | -0.0427 | -0.0245 | [-0.358, -0.019] | 1.000 / 1.000 | 0.722 | 0.0161 | 308/959 | -0.089 / -0.033 |
| public_rho | 0.585 | nan | nan | -0.0249 | [nan, nan] | nan / 1.000 | nan | 0.0079 | 0/0 | nan / nan |
| s18_public | 0.585 | nan | nan | -0.0248 | [nan, nan] | nan / 1.000 | nan | 0.0079 | 0/0 | nan / nan |
| s36_public | 0.523 | nan | nan | -0.0061 | [nan, nan] | nan / 1.000 | nan | 0.0011 | 0/0 | nan / nan |
| s64_public | 0.562 | nan | nan | -0.0018 | [nan, nan] | nan / 1.000 | nan | 0.0002 | 0/0 | nan / nan |

## 2. Certificate log(n0/n1) >= C_rho - Omega over the late window

| run | omega | violations (on/off) | min slack | slack on | angle on | gap on | pointwise min | per-interval share | per-interval by interval | max per-interval deficit | from 0.06: viol, factor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sub2000 | True | 0/1000 (0/0) | 0.1174 | 0.320 | 0.351 | -0.031 | 1.18e-06 | 0.253 | [0, 0, 0, 0, 522, 996] | 0.0078 | 5, 1.0031 |
| sub500s1 | True | 1/1000 (1/0) | -0.0028 | 0.346 | 0.388 | -0.039 | 1.41e-06 | 0.173 | [0, 0, 0, 1, 42, 993] | 0.0145 | 7, 1.0200 |
| s18_sub500 | True | 0/1000 (0/0) | 0.0188 | 0.368 | 0.411 | -0.043 | 1.00e-06 | 0.171 | [0, 0, 0, 3, 40, 985] | 0.0153 | 10, 1.0149 |
| s36_sub500 | True | 0/1000 (0/0) | 0.0275 | 0.399 | 0.409 | -0.010 | 2.21e-07 | 0.031 | [0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 15, 354] | 0.0009 | 0, 1.0000 |
| s64_sub500 | True | 0/1000 (0/0) | 0.0307 | 0.409 | 0.412 | -0.003 | 1.58e-07 | 0.001 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 16] | 0.0001 | 0, 1.0000 |
| s18_public | True | 0/500 (0/0) | 0.1228 | nan | nan | nan | 3.48e-07 | 0.231 | [0, 0, 0, 0, 197, 495] | 0.0007 | 2, 1.0006 |
| s36_public | True | 0/500 (0/0) | 0.1220 | nan | nan | nan | 3.72e-07 | 0.046 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 34, 241] | 0.0000 | 0, 1.0000 |
| s64_public | True | 0/500 (0/0) | 0.1384 | nan | nan | nan | 3.78e-07 | 0.003 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 6, 26] | 0.0000 | 0, 1.0000 |
| anchor_sub500 | True | 0/1000 (0/0) | 0.0187 | 0.368 | 0.411 | -0.043 | 1.00e-06 | 0.171 | [0, 0, 0, 3, 40, 985] | 0.0153 | 10, 1.0149 |
| anchor_public | True | 0/500 (0/0) | 0.1228 | nan | nan | nan | 3.48e-07 | 0.230 | [0, 0, 0, 0, 196, 495] | 0.0007 | 2, 1.0006 |
| sub500_rho_noomega | False | 0/1000 (0/0) | 0.0188 | 0.368 | 0.411 | -0.043 | 1.00e-06 | 0.171 | [0, 0, 0, 3, 40, 985] | 0.0153 | 10, 1.0149 |
| public_rho_noomega | False | 0/200 (0/0) | 0.1333 | nan | nan | nan | 4.28e-07 | 0.228 | [0, 0, 0, 0, 76, 198] | 0.0004 | 1, 1.0000 |

## 3. Landing certificate B_K = rho_last B(0.002) + omega_last, certified if B_K < d2/3

| run:anchor | sigma0 | S cert on | S false | Wilson on | S margin on / min off | R cert on | R false | S = R | S = D | const anchor on/off | anchor(s0) = y1 on/off | B_K/d1 on | e^slack on | cert = rule d1 e^slack < d2/3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sub2000:predictive | 0.585 | 376/499 (75.4%) | 0/501 | [0.7139, 0.7893] | 0.74 / 1.28 | 376 | 0 | True | True | 499/490 | 1.0/0.9800399201596807 | 1.377 | 1.377 | True |
| sub500s1:predictive | 0.585 | 952/956 (99.6%) | 0/44 | [0.9893, 0.9984] | 0.31 / 2.08 | 952 | 0 | True | True | 956/41 | 1.0/0.9318181818181818 | 1.413 | 1.413 | True |
| anchor_sub500:predictive | 0.585 | 956/959 (99.7%) | 0/41 | [0.9908, 0.9989] | 0.30 / 1.35 | 956 | 0 | True | True | 959/39 | 1.0/0.9512195121951219 | 1.445 | 1.445 | True |
| sub2000:endpoint | 0.585 | 376/499 (75.4%) | 0/501 | [0.7139, 0.7893] | 0.74 / 1.28 | 376 | 0 | True | - | 499/501 | 1.0/1.0 | 1.377 | 1.377 | True |
| sub500s1:endpoint | 0.585 | 952/956 (99.6%) | 0/44 | [0.9893, 0.9984] | 0.31 / 2.08 | 952 | 0 | True | - | 956/44 | 1.0/1.0 | 1.413 | 1.413 | True |
| s18_sub500:endpoint | 0.585 | 956/959 (99.7%) | 0/41 | [0.9908, 0.9989] | 0.30 / 1.33 | 956 | 0 | True | - | 959/41 | 1.0/1.0 | 1.445 | 1.445 | True |
| anchor_sub500:endpoint | 0.585 | 956/959 (99.7%) | 0/41 | [0.9908, 0.9989] | 0.30 / 1.35 | 956 | 0 | True | - | 959/41 | 1.0/1.0 | 1.445 | 1.445 | True |
| s36_sub500:endpoint | 0.523 | 957/960 (99.7%) | 0/40 | [0.9909, 0.9989] | 0.30 / 2.53 | 957 | 0 | True | - | 960/40 | 1.0/1.0 | 1.490 | 1.490 | True |
| s64_sub500:endpoint | 0.562 | 957/961 (99.6%) | 0/39 | [0.9893, 0.9984] | 0.30 / 2.57 | 957 | 0 | True | - | 961/39 | 1.0/1.0 | 1.505 | 1.505 | True |
| s18_public:endpoint | 0.585 | 0/0 (nan%) | 0/500 | [nan, nan] | nan / 2.57 | 0 | 0 | True | - | 0/500 | nan/1.0 | nan | nan | True |
| s36_public:endpoint | 0.523 | 0/0 (nan%) | 0/500 | [nan, nan] | nan / 2.56 | 0 | 0 | True | - | 0/500 | nan/1.0 | nan | nan | True |
| s64_public:endpoint | 0.562 | 0/0 (nan%) | 0/500 | [nan, nan] | nan / 2.61 | 0 | 0 | True | - | 0/500 | nan/1.0 | nan | nan | True |
| anchor_public:predictive | 0.585 | 0/0 (nan%) | 0/500 | [nan, nan] | nan / 2.57 | 0 | 0 | True | True | 0/471 | nan/0.95 | nan | nan | True |

T2 (B_K < g_a/4, g_a from exact-field endpoints of the n3_edm_memorization run with the same latents):

- sub2000:predictive: certified 134/284 on-atom (47.2%), false 0/226
- sub500s1:predictive: certified 847/864 on-atom (98.0%), false 0/38
- anchor_sub500:predictive: certified 874/890 on-atom (98.2%), false 0/38
- sub2000:endpoint: certified 134/284 on-atom (47.2%), false 0/225
- sub500s1:endpoint: certified 847/864 on-atom (98.0%), false 0/38
- s18_sub500:endpoint: certified 874/890 on-atom (98.2%), false 0/38
- anchor_sub500:endpoint: certified 874/890 on-atom (98.2%), false 0/38

Heun chain (Prop. heun(b), gamma = 0, endpoint anchor y1):

| run | sigma0 | cert on | false | Wilson | violations | median log(B_K/n_K) on |
|---|---|---|---|---|---|---|
| sub2000 | 0.585 | 0/499 (0.0%) | 0/501 | [0.0, 0.0076] | 0 | 2.470 |
| sub500s1 | 0.585 | 0/956 (0.0%) | 0/44 | [0.0, 0.004] | 0 | 2.461 |
| s18_sub500 | 0.585 | 2/959 (0.2%) | 0/41 | [0.0006, 0.0076] | 0 | 2.481 |
| s36_sub500 | 0.523 | 946/960 (98.5%) | 0/40 | [0.9757, 0.9913] | 0 | 0.582 |
| s64_sub500 | 0.562 | 952/961 (99.1%) | 0/39 | [0.9823, 0.9951] | 0 | 0.521 |
| anchor_sub500 | 0.585 | 2/959 (0.2%) | 0/41 | [0.0006, 0.0076] | 0 | 2.481 |
| s18_public | 0.585 | 0/0 (nan%) | 0/500 | [nan, nan] | 0 | nan |
| s64_public | 0.562 | 0/0 (nan%) | 0/500 | [nan, nan] | 0 | nan |

### 3b. Same certificate without the output: rho := 1 below the stop level and in the last step

| run | rho used down to sigma | cert on | false | B_K < d1 | share with rho <= 1 below stop |
|---|---|---|---|---|---|
| sub2000 | 0.002 | 376/499 | 0/501 | 0 | 1.000 |
| sub2000 | 0.007528 | 376/499 | 0/501 | 0 | 0.999 |
| sub2000 | 0.02293 | 370/499 | 0/501 | 0 | 0.999 |
| sub2000 | 0.05995 | 337/499 | 0/501 | 0 | 0.999 |
| sub500s1 | 0.002 | 952/956 | 0/44 | 1 | 1.000 |
| sub500s1 | 0.007528 | 952/956 | 0/44 | 0 | 0.999 |
| sub500s1 | 0.02293 | 951/956 | 0/44 | 0 | 0.999 |
| sub500s1 | 0.05995 | 948/956 | 0/44 | 0 | 0.999 |
| anchor_sub500 | 0.002 | 956/959 | 0/41 | 0 | 1.000 |
| anchor_sub500 | 0.007528 | 956/959 | 0/41 | 0 | 0.994 |
| anchor_sub500 | 0.02293 | 956/959 | 0/41 | 0 | 0.994 |
| anchor_sub500 | 0.05995 | 953/959 | 0/41 | 0 | 0.994 |

### 3c. Direct rule nA(sigma_s) < d2/3 with the same information (no relative error needed)

| run | sigma_s | cert on | false | share d1 <= nA(sigma_s) |
|---|---|---|---|---|
| sub2000 | 0.007528 | 498/499 | 0/501 | 0.9990 |
| sub2000 | 0.02293 | 487/499 | 0/501 | 1.0000 |
| sub2000 | 0.05995 | 425/499 | 0/501 | 1.0000 |
| sub2000 | 0.1395 | 84/499 | 0/501 | 1.0000 |
| sub500s1 | 0.007528 | 956/956 | 0/44 | 1.0000 |
| sub500s1 | 0.02293 | 956/956 | 0/44 | 1.0000 |
| sub500s1 | 0.05995 | 950/956 | 0/44 | 1.0000 |
| sub500s1 | 0.1395 | 492/956 | 0/44 | 1.0000 |
| anchor_sub500 | 0.007528 | 959/959 | 0/41 | 0.9970 |
| anchor_sub500 | 0.02293 | 959/959 | 0/41 | 0.9990 |
| anchor_sub500 | 0.05995 | 957/959 | 0/41 | 0.9990 |
| anchor_sub500 | 0.1395 | 548/959 | 0/41 | 1.0000 |

## 4. Detector AUCs (P(off score > on score)), stratified bootstrap, 2000 resamples

- sub2000: dD059 [0.9902, 0.9861, 0.9937]; negC [0.9831, 0.9771, 0.9882]; logBK [0.9846, 0.979, 0.9894]; d1 [0.9849, 0.9796, 0.9896]; dD_end [0.9849, 0.9796, 0.9896]; dD059-negC [0.0071, 0.0042, 0.0104]; dD059-logBK [0.0056, 0.0031, 0.0084]; negC-dD_end [-0.0018, -0.004, 0.0002]; C_med_on_off [1.752, 0.684]; oracle_dD059_recall_at_zeroFP [369, 499, 0.7394789579158316]; naive_dD059<d2/3 {'on': 499, 'off': 26}; max|dD_end-d1| 0.0
- sub500s1: dD059 [1.0, 1.0, 1.0]; negC [1.0, 1.0, 1.0]; logBK [1.0, 1.0, 1.0]; d1 [1.0, 1.0, 1.0]; dD_end [1.0, 1.0, 1.0]; dD059-negC [0.0, 0.0, 0.0]; dD059-logBK [0.0, 0.0, 0.0]; negC-dD_end [0.0, 0.0, 0.0]; C_med_on_off [2.528, 0.317]; oracle_dD059_recall_at_zeroFP [956, 956, 1.0]; naive_dD059<d2/3 {'on': 955, 'off': 0}; max|dD_end-d1| 0.0
- anchor_sub500: dD059 [0.9999, 0.9998, 1.0]; negC [1.0, 1.0, 1.0]; logBK [1.0, 1.0, 1.0]; d1 [1.0, 1.0, 1.0]; dD_end [1.0, 1.0, 1.0]; dD059-negC [-0.0001, -0.0002, 0.0]; dD059-logBK [-0.0001, -0.0002, 0.0]; negC-dD_end [0.0, 0.0, 0.0]; C_med_on_off [2.553, 0.29]; oracle_dD059_recall_at_zeroFP [957, 959, 0.9979144942648592]; naive_dD059<d2/3 {'on': 958, 'off': 0}; max|dD_end-d1| 0.0

## 5. R^2 of log d1 (simple OLS)

| run | group | R2 C[0.002,0.585] | R2 log dD(0.585) | both | R2 C[0.14,0.585] | R2 log n0 - C (slope) | R2(C) - R2(dD) [95% CI] |
|---|---|---|---|---|---|---|---|
| sub2000 (self) | pooled | 0.977 | 0.991 | 0.992 | 0.987 | 0.990 (1.048) | -0.014 [-0.0166, -0.012] |
| sub2000 (self) | on | 0.883 | 0.965 | 0.967 | 0.949 | 0.929 (0.951) | -0.082 [-0.0968, -0.0677] |
| sub2000 (self) | off | 0.956 | 0.981 | 0.990 | 0.979 | 0.988 (1.097) | -0.025 [-0.0319, -0.0188] |
| sub500s1 (self) | pooled | 0.870 | 0.966 | 0.966 | 0.930 | 0.906 (1.03) | -0.096 [-0.1078, -0.0855] |
| sub500s1 (self) | on | 0.428 | 0.809 | 0.809 | 0.784 | 0.530 (0.793) | -0.381 [-0.425, -0.337] |
| sub500s1 (self) | off | 0.897 | 0.996 | 0.996 | 0.933 | 0.991 (1.159) | -0.100 [-0.1812, -0.0532] |
| anchor_sub500 (self) | pooled | 0.830 | 0.960 | 0.960 | 0.923 | 0.877 (1.015) | -0.130 [-0.1428, -0.1166] |
| anchor_sub500 (self) | on | 0.341 | 0.778 | 0.781 | 0.714 | 0.438 (0.686) | -0.437 [-0.4791, -0.396] |
| anchor_sub500 (self) | off | 0.897 | 0.988 | 0.994 | 0.951 | 0.987 (1.079) | -0.091 [-0.1816, -0.0446] |
| sub500_rho (memo:sub500) | pooled | 0.830 | 0.960 | 0.960 | 0.923 | 0.877 (1.015) | -0.130 [-0.1435, -0.1163] |
| sub500_rho (memo:sub500) | on | 0.341 | 0.778 | 0.780 | 0.714 | 0.437 (0.686) | -0.437 [-0.4772, -0.3938] |
| sub500_rho (memo:sub500) | off | 0.898 | 0.987 | 0.993 | 0.951 | 0.988 (1.077) | -0.088 [-0.1776, -0.0441] |
| s18_sub500 (memo:sub500) | pooled | 0.830 | 0.960 | 0.960 | 0.923 | 0.877 (1.015) | -0.130 [-0.1434, -0.1169] |
| s18_sub500 (memo:sub500) | on | 0.341 | 0.778 | 0.780 | 0.713 | 0.437 (0.685) | -0.437 [-0.4779, -0.3939] |
| s18_sub500 (memo:sub500) | off | 0.899 | 0.988 | 0.994 | 0.951 | 0.988 (1.077) | -0.088 [-0.1735, -0.0426] |

## 6. abs(rhoA - dD/nA) for sigma <= 0.585

- sub2000: {'median': 7.771561172376096e-16, 'n_samples_gt_1e-6': 69, 'bad_with_omega_pos_at_same_step': 68, 'bad_steps_without_omega_pos': 2}
- sub500s1: {'median': 7.636252741249905e-15, 'n_samples_gt_1e-6': 6, 'bad_with_omega_pos_at_same_step': 5, 'bad_steps_without_omega_pos': 2}
- anchor_sub500: {'median': 7.827072323607354e-15, 'n_samples_gt_1e-6': 6, 'bad_with_omega_pos_at_same_step': 6, 'bad_steps_without_omega_pos': 1}

## 7. Claimed vs recomputed

| claim | claimed | recomputed |
|---|---|---|
| gap median on-atom, 2000 / first 500 / second 500 | -0.031 / -0.043 / -0.039 | -0.031 / -0.043 / -0.039 |
| actual late contraction median on-atom | 2.08 / 2.94 / 2.89 | 2.08 / 2.94 / 2.89 |
| gap as share of actual (median of per-sample ratio; ratio of medians) | 1.4-1.6% | 1.56%; 1.48% / 1.45%; 1.45% / 1.35%; 1.36% |
| gap median off-atom | -0.024 to -0.025 | -0.024 / -0.025 / -0.024 |
| gap median on-atom 18/36/64 steps | -0.043 / -0.010 / -0.003 | -0.043 / -0.010 / -0.003 |
| max abs gap on-atom 18/36/64 | 0.722 / 0.134 / 0.026 | 0.722 / 0.134 / 0.026 |
| p1-p99 gap on-atom, 2000 / first 500 | [-0.057, -0.023] / [-0.358, -0.019] | [-0.057, -0.023] / [-0.358, -0.019] |
| ratio of successive medians 18/36, 36/64 | 4.4 / 3.3 | 4.45 / 3.26 |
| share of samples with gap < 0 | >= 99% | 1.000 / 1.000 / 1.000 |
| max per-interval abs gap above 0.585 | <= 0.016 | 0.0082 / 0.0161 / 0.0087 |
| on-atom with rad < 0 in late window (first 500 / second 500 / 2000) | 308/959, 253/956, 3/499 | 308/959, 253/956, 3/499 |
| median gap, rad<0 vs rest (first 500) | -0.089 vs -0.033 | -0.089 vs -0.033 |
| certificate violations, 18 steps (2000 + first + second 500) | 1/3000, deficit 0.0028 (on-atom, second 500) | 1/3000, min slack -0.0028 |
| violations 36 / 64 steps; public 200 (no omega) / 500 | 0/1000, 0/1000; 0/200, 0/500 | 0, 0; 0, 0 |
| median slack on-atom 2000 / first / second | 0.320 / 0.368 / 0.346 | 0.320 / 0.368 / 0.346 |
| median angle term on-atom | 0.351 / 0.411 / 0.388 | 0.351 / 0.411 / 0.388 |
| pointwise min of rho + omega/n - rad (18 steps) | 1.0e-6 to 1.4e-6 | 1.18e-06 / 1.00e-06 / 1.41e-06 |
| per-interval violation share, first 500 / 2000 / 36 / 64 (all samples) | 17.3% / 25.3% / 3.2% / 0.1% | 17.13% / 25.30% / 3.12% / 0.10% |
| same, on-atom samples only | 17.3% / 25.3% / 3.2% / 0.1% | 17.26% / 25.28% / 3.17% / 0.09% |
| max per-interval deficit | <= 0.015 | 0.0078 / 0.0153 / 0.0145 |
| start at 0.06: violations 2000 / second 500 (first 500 not reported) | 5 / 7, factor up to 1.020 | 5 / 7 (first 500: 10), factors 1.0031, 1.0200, 1.0149 |
| T1 certified on-atom 2000 / second / first (endpoint anchor) | 376/499, 952/956, 956/959 | 376/499, 952/956, 956/959 |
| T1 false certifications | 0/501, 0/44, 0/41; public 0/500 (18, 64) | 0, 0, 0; 0, 0 |
| Wilson 95% on-atom | 71.4-78.9, 98.9-99.8, 99.1-99.9 | [0.7139, 0.7893], [0.9893, 0.9984], [0.9908, 0.9989] |
| Wilson upper false-certification rate 2000 | 0.76% | 0.76% |
| margin B_K/(d2/3): on median 2000 / second; off min | 0.74 / 0.31; 1.28 / 2.08 | 0.74 / 0.31; 1.28 / 2.08 |
| T2 (g_a/4) | 134/284, 847/864; false 0/225, 0/38 | 134/284, 847/864; false 0/226 (endpoint-anchor lookup 0/225), 0/38 |
| S, R, D certify the same samples | yes | True True True True |
| B_K equals err(0.002) e^slack + omega and err(0.002) equals d1 | (not stated) | max rel dev 7.0e-16; median abs(err_last/d1 - 1) 1.2e-15 |
| Heun chain cert, 18 steps (2000 / second / first) | 0/499, 0/956, 2/959 | 0/499, 0/956, 2/959 |
| Heun chain cert, 36 / 64 steps; violations | 946/960, 952/961; 0 | 946/960, 952/961; 0 |
| Heun chain Wilson 36 / 64 | 97.6-99.1, 98.2-99.5 | [0.9757, 0.9913], [0.9823, 0.9951] |
| median log(B_K/n_K) on-atom 2000: chain vs integral | 2.47 vs 0.32 | 2.47 vs 0.32 |
| chain per-step bound medians at sigma 0.023, 0.0075 | 1.575, 2.265 | 1.575, 2.265 |
| AUC dD(0.585), -C, diff (2000) | 0.990 [0.986,0.994]; 0.983 [0.977,0.988]; 0.007 [0.004,0.010] | [0.9902, 0.9861, 0.9937]; [0.9831, 0.9771, 0.9882]; [0.0071, 0.0042, 0.0104] |
| AUC dD(0.585) - AUC log B_K | 0.006 [0.003, 0.008] | [0.0056, 0.0031, 0.0084] |
| max abs(dD(0.002) - d1); AUC d1 | 0; 0.985 | 0.0; 0.9849 |
| oracle dD(0.585) recall at zero FP; naive dD(0.585) < d2/3 | 73.9%; 499/499 on, 26/501 off | 73.9%; {'on': 499, 'off': 26} |
| R2 log dD(0.585), 2000 pooled/on/off | 0.991 / 0.965 / 0.981 | 0.991 / 0.965 / 0.981 |
| R2 C, 2000 pooled/on/off | 0.976 / 0.883 / 0.956 | 0.9765 / 0.8835 / 0.9555 |
| R2 on-atom dD vs C: second / first 500 | 0.809 vs 0.428; 0.778 vs 0.341 | 0.809 vs 0.428; 0.778 vs 0.341 |
| R2 both, 2000 pooled/on/off | 0.992 / 0.967 / 0.990 | 0.992 / 0.967 / 0.990 |
| boot R2(C)-R2(dD): 2000 pooled/on/off; second on; first on | [-0.017,-0.012] [-0.097,-0.067] [-0.032,-0.019]; [-0.426,-0.338]; [-0.477,-0.395] | [-0.0166, -0.012] [-0.0968, -0.0677] [-0.0319, -0.0188]; [-0.425, -0.337]; [-0.4772, -0.3938] |
| R2 on-atom C over [0.14, 0.585]: 2000 / second / first | 0.949 / 0.784 / 0.713 | 0.9491 / 0.7841 / 0.7138 / 0.7134 |
| R2 log n0 - C: 2000 pooled, on (slope); 500 on | 0.990, 0.929 (0.95); 0.53, 0.44 | 0.990, 0.929 (0.951); 0.53, 0.44 |
| median abs(rhoA - dD/nA), sigma <= 0.585; samples > 1e-6 | 7.8e-16, 7.6e-15; 69, 6 | 7.8e-16, 7.6e-15; 69, 6 |
