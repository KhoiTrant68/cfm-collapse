# mu = (1+sigma) lambda_max(sym dD/dx) along learned EDM trajectories

## mu_public (n=200, off-atom 1.000)

| sigma | t | median mu off | median mu on | frac mu<1 off | frac mu<1 on | median mu* exact | AUC mu |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | 4.925 | - | 0.000 | - | 13.047 | - |
| 0.5853 | 0.6308 | 2.706 | - | 0.000 | - | 0.000 | - |
| 0.1395 | 0.8776 | 1.684 | - | 0.000 | - | 0.000 | - |
| 0.02293 | 0.9776 | 2.072 | - | 0.000 | - | 0.000 | - |
| 0.002 | 0.9980 | 1.001 | - | 0.415 | - | 0.000 | - |

precond: {'name': 'VPPrecond', 'sigma_data': 0.5, 'inferred': True}; mu_min = (1+sigma) lambda_min(sym J_D); rho = 1 - lambda_max(sym J_D)/c_skip, the share of the exact field's contraction (exact: rho = 1) carried by the raw network

| sigma | t | median mu_min off | median mu_min on | median rho off | median rho on | median rho/sigma off | AUC rho |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | - | - | -0.685 | - | -0.356 | - |
| 0.5853 | 0.6308 | - | - | -0.707 | - | -1.208 | - |
| 0.1395 | 0.8776 | - | - | -0.477 | - | -3.422 | - |
| 0.02293 | 0.9776 | - | - | -1.025 | - | -44.711 | - |
| 0.002 | 0.9980 | - | - | 0.001 | - | 0.449 | - |

## mu_sub1000 (n=100, off-atom 1.000)

| sigma | t | median mu off | median mu on | frac mu<1 off | frac mu<1 on | median mu* exact | AUC mu |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | 3.537 | - | 0.000 | - | 0.367 | - |
| 0.5853 | 0.6308 | 1.924 | - | 0.000 | - | 0.000 | - |
| 0.1395 | 0.8776 | 1.173 | - | 0.000 | - | 0.000 | - |
| 0.02293 | 0.9776 | 1.004 | - | 0.150 | - | 0.000 | - |
| 0.002 | 0.9980 | 0.988 | - | 1.000 | - | 0.000 | - |

precond: {'name': 'EDMPrecond', 'sigma_data': 0.5, 'inferred': True}; mu_min = (1+sigma) lambda_min(sym J_D); rho = 1 - lambda_max(sym J_D)/c_skip, the share of the exact field's contraction (exact: rho = 1) carried by the raw network

| sigma | t | median mu_min off | median mu_min on | median rho off | median rho on | median rho/sigma off | AUC rho |
|---|---|---|---|---|---|---|---|
| 1.923 | 0.3421 | - | - | -18.111 | - | -9.416 | - |
| 0.5853 | 0.6308 | - | - | -1.877 | - | -3.207 | - |
| 0.1395 | 0.8776 | - | - | -0.109 | - | -0.784 | - |
| 0.02293 | 0.9776 | - | - | 0.016 | - | 0.710 | - |
| 0.002 | 0.9980 | - | - | 0.014 | - | 6.804 | - |
