# mu = (1+sigma) lambda_max(sym dD/dx) along learned EDM trajectories

## mu_sub500 (n=200, off-atom 0.065)

| sigma | t | median mu off | median mu on | frac mu<1 off | frac mu<1 on | median mu* exact | AUC mu |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | 2.369 | 0.582 | 0.231 | 0.952 | 0.000 | 0.863 |
| 0.5853 | 0.6308 | 1.121 | 1.017 | 0.385 | 0.337 | 0.000 | 0.641 |
| 0.1395 | 0.8776 | 1.162 | 1.131 | 0.000 | 0.059 | 0.000 | 0.716 |
| 0.02293 | 0.9776 | 0.959 | 0.960 | 0.846 | 0.995 | 0.000 | 0.519 |
| 0.002 | 0.9980 | 0.960 | 0.962 | 1.000 | 1.000 | 0.000 | 0.466 |

precond: {'name': 'EDMPrecond', 'sigma_data': 0.5}; mu_min = (1+sigma) lambda_min(sym J_D); rho = 1 - lambda_max(sym J_D)/c_skip, the share of the exact field's contraction (exact: rho = 1) carried by the raw network

| sigma | t | median mu_min off | median mu_min on | median rho off | median rho on | median rho/sigma off | AUC rho |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | -0.346 | -0.163 | -11.801 | -2.145 | -6.136 | 0.137 |
| 0.5853 | 0.6308 | -0.001 | -0.014 | -0.676 | -0.521 | -1.155 | 0.359 |
| 0.1395 | 0.8776 | 0.066 | 0.004 | -0.099 | -0.070 | -0.708 | 0.284 |
| 0.02293 | 0.9776 | 0.261 | 0.089 | 0.061 | 0.060 | 2.640 | 0.481 |
| 0.002 | 0.9980 | 0.724 | 0.604 | 0.042 | 0.040 | 20.886 | 0.534 |
