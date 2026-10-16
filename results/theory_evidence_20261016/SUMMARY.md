# Synthetic server pilot — 2026-10-16

Feasibility pilot on existing checkpoints; no training. Results are grouped by problem seed.

| training h | seed | fitted h_eff | mean energy | mean reference null | above diagnostic q95 | solver pass |
|---|---|---|---|---|---|---|
| 0 | 0 | 0.01873 | 0.29490 | 0.00330 | 8/8 | 8/8 |
| 0 | 1 | 0.01105 | 0.18828 | 0.00431 | 7/8 | 8/8 |
| 0 | 2 | 0.00361 | 0.09528 | 0.00366 | 8/8 | 8/8 |
| 0.1 | 0 | 0.10987 | 0.02648 | 0.00740 | 4/8 | 8/8 |
| 0.1 | 1 | 0.10325 | 0.01427 | 0.00616 | 3/8 | 8/8 |
| 0.1 | 2 | 0.09120 | 0.01478 | 0.01035 | 2/8 | 8/8 |

Independent NumPy checks: 192 energy distances and 192 same-moment control distances matched saved records; all 24 family scale fits reproduced.

Energy is normalized by the square root of analytic posterior trace. Reference mixtures use the same finite terminal time. Bandwidth fits use only 20 training queries; eight new queries evaluate the law. Gaussian moment matching is a descriptive fit, not a proof of distributional equality.

The q95 envelope uses only 16 independent reference pairs per condition and is diagnostic, not a calibrated multiple-testing decision. Eight conditions are nested within each of three reused problem seeds; checkpoints are not independent replicates. Two queries from seed 0 also appeared in the smoke, with no subsequent selection or tuning.

The solver screen compares paired displacement with a mean-based Monte Carlo proxy and one tenth of energy discrepancy. It is a practical screen, not a numerical-error certificate for every statistic.

## Terminal-time sensitivity

| run | paired displacement eps .001 to .0001 | nearest atom (.001) | nearest atom (.0001) | solver pass (.0001) |
|---|---|---|---|---|
| heff_p7y_h0_seed0 | 0.00140765 | 0.0636641 | 0.0633887 | 8/8 |
| heff_p7y_h0.1_seed0 | 0.00127501 | 0.0552048 | 0.0547428 | 8/8 |
| heff_p7y_h0_seed1 | 0.00142189 | 0.0350401 | 0.0348412 | 8/8 |
| heff_p7y_h0.1_seed1 | 0.00122973 | 0.0505829 | 0.0505448 | 8/8 |
| heff_p7y_h0_seed2 | 0.00136277 | 0.0480417 | 0.0473748 | 8/8 |
| heff_p7y_h0.1_seed2 | 0.00119244 | 0.0509053 | 0.0505764 | 8/8 |

## Teacher versus learned-path error

Hard-label diagnostics evaluate the exact field (a-x)/(1-t) at the same seven times, on teacher and learned paths, averaged over 20 training queries. They do not estimate uniform-time global training loss or establish a global density/risk-transfer bound.

| checkpoint | seed | teacher error t=.999 | learned-path error t=.999 | ratio |
|---|---|---|---|---|
| 10000 | 0 | 2.4538 | 2.6782e+06 | 1.0914e+06 |
| 10000 | 1 | 2.1493 | 2.2773e+06 | 1.0596e+06 |
| 10000 | 2 | 2.0797 | 2.0152e+06 | 9.69e+05 |
| 30000 | 0 | 2.2199 | 1.8837e+06 | 8.4855e+05 |
| 30000 | 1 | 2.1185 | 1.8204e+06 | 8.593e+05 |
| 30000 | 2 | 2.3334 | 1.9196e+06 | 8.2266e+05 |
| 200000 | 0 | 2.392 | 5.859e+05 | 2.4494e+05 |
| 200000 | 1 | 2.2607 | 1.1698e+06 | 5.1747e+05 |
| 200000 | 2 | 2.5949 | 1.1344e+06 | 4.3716e+05 |
