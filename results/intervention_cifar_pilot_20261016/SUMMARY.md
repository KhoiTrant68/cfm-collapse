# Oracle interventions and CIFAR pilot

Existing checkpoints only; no retraining. Numerical illustrations and feasibility pilots do not establish novelty or venue readiness.

## Oracle interventions

Five new geometry seeds, five atoms in R^2, scalar labels, 128 shared Gaussian source samples per seed; paired log-time RK4 at 768/1536 steps.

| intervention | mean nearest-atom distance at eps=1e-6: range over seeds |
|---|---|
| hard_cfg_w0 | 1.65015e-06 – 3.62578e-06 |
| hard_cfg_w3 | 7.31583e-07 – 2.77049e-06 |
| hard_cfg_w12 | 1.7883e-06 – 4.59461e-06 |
| label_smoothed_cfg_w0 | 1.89735e-06 – 3.58385e-06 |
| label_smoothed_cfg_w3 | 1.51573e-06 – 2.85163e-06 |
| label_smoothed_cfg_w12 | 1.72042e-06 – 3.57853e-06 |
| average_three_label_fields | 1.96437e-06 – 3.66495e-06 |
| exact_target_noise_rho0.0 | 2.05341e-06 – 3.63124e-06 |
| exact_target_noise_rho0.15 | 0.178133 – 0.199065 |

The target-noise controls are exact finite-time law draws, not numerically integrated guided fields. Field averaging is the equal average of three fields, not averaging label priors. The symmetric source at the midpoint remains an exceptional non-atom trajectory; nearby sources move to atoms. Frequencies from 128 sources do not identify exact guided endpoint probabilities.

## Exact matched teacher loss

| delta | teacher loss / d (both fields) | counterexample endpoint variance / d | Lipschitz-attainer endpoint variance / d |
|---|---|---|---|
| 0.01 | 0.3264995 | 1 | 0.129843 |
| 0.003 | 0.1472526 | 1 | 0.02641069 |
| 0.001 | 0.06703156 | 1 | 0.005472834 |
| 0.0001 | 0.01137843 | 1 | 0.000157695 |

These are exact constructed fields with the same teacher loss. Their Lipschitz constants are not held equal. This is not evidence that the trained architectures realize the counterexample. Segmentwise quadrature was independently checked against its analytic loss.

## CIFAR solver/calibration pilot

Six exact DDPM checkpoints (35,750,915 parameters), h=0,4 × seeds 0,1,2 at 60k. Eight identical held-out test images and M=32 identical source draws across models/solvers. Four Euler resolutions, epsilon=.001, no clipping.

| h | seed | steps | pixel 90% coverage | joint8 coverage | joint32 coverage | hidden trace | hidden mean MSE | paired RMS to 400 |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 50 | 0.0635 | 0.000 | 0.000 | 0.46701 | 0.13359 | 0.0025339 |
| 0 | 0 | 100 | 0.0673 | 0.000 | 0.000 | 0.52403 | 0.13361 | 0.0014114 |
| 0 | 0 | 200 | 0.0706 | 0.000 | 0.000 | 0.56369 | 0.13362 | 0.00054276 |
| 0 | 0 | 400 | 0.0728 | 0.000 | 0.000 | 0.58847 | 0.13362 | 0 |
| 0 | 1 | 50 | 0.0695 | 0.000 | 0.000 | 0.53679 | 0.14339 | 0.0026 |
| 0 | 1 | 100 | 0.0750 | 0.000 | 0.000 | 0.60249 | 0.14341 | 0.0014193 |
| 0 | 1 | 200 | 0.0789 | 0.000 | 0.000 | 0.65065 | 0.14341 | 0.00054309 |
| 0 | 1 | 400 | 0.0815 | 0.000 | 0.000 | 0.67981 | 0.14341 | 0 |
| 0 | 2 | 50 | 0.0704 | 0.000 | 0.000 | 0.5905 | 0.15142 | 0.002527 |
| 0 | 2 | 100 | 0.0763 | 0.000 | 0.000 | 0.65112 | 0.15144 | 0.0013708 |
| 0 | 2 | 200 | 0.0802 | 0.000 | 0.000 | 0.6939 | 0.15146 | 0.0005231 |
| 0 | 2 | 400 | 0.0830 | 0.000 | 0.000 | 0.71974 | 0.15147 | 0 |
| 4 | 0 | 50 | 0.7598 | 0.625 | 1.000 | 212.44 | 0.20875 | 0.055806 |
| 4 | 0 | 100 | 0.7708 | 0.500 | 0.875 | 218.94 | 0.20867 | 0.028096 |
| 4 | 0 | 200 | 0.7769 | 0.500 | 0.875 | 221.89 | 0.20877 | 0.013859 |
| 4 | 0 | 400 | 0.7820 | 0.500 | 0.875 | 223.86 | 0.20951 | 0 |
| 4 | 1 | 50 | 0.7581 | 1.000 | 0.750 | 193.41 | 0.2029 | 0.069363 |
| 4 | 1 | 100 | 0.7677 | 1.000 | 0.625 | 199.28 | 0.202 | 0.042465 |
| 4 | 1 | 200 | 0.7716 | 1.000 | 0.500 | 202.29 | 0.2017 | 0.023301 |
| 4 | 1 | 400 | 0.7709 | 1.000 | 0.375 | 203.27 | 0.20155 | 0 |
| 4 | 2 | 50 | 0.7760 | 0.875 | 0.750 | 192.7 | 0.19893 | 0.061533 |
| 4 | 2 | 100 | 0.7868 | 0.875 | 0.875 | 197.68 | 0.1989 | 0.043645 |
| 4 | 2 | 200 | 0.7957 | 0.875 | 0.750 | 201.96 | 0.19789 | 0.015982 |
| 4 | 2 | 400 | 0.7983 | 0.875 | 0.875 | 203.51 | 0.19754 | 0 |

Finite-M reference coverage at nominal 90%: 0.8787878787878788 for central ranks and 0.9090909090909091 for upper ranks.

Eight images are the evaluation units; pixels and PCA coordinates are not independent replicates. The same images across seeds make this a paired pilot, not 48 independent test images. Joint coverage has resolution 1/8. There is no formal significance claim or full posterior-quality certificate. A 400-step output is a comparison reference, not a proven exact endpoint. Nearest-training-image MSE is not exact membership.

Independent raw checks: 135 oracle rows, four matched-loss constructions, 192 CIFAR image/solver rows.

CIFAR raw recomputation ran on the server. This local summary verifies result-file hashes and cross-h input-array hashes against that audit. Full raw samples remain on the server; local downloads may be incomplete.
