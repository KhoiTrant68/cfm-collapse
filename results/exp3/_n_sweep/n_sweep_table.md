**Sweep A -- constant budget (30000 iters, mean +/- std over 3 seeds).**

| N | grad samples / image | inpaint pixel var | NN dist to train image |
|---|---|---|---|
| 100 | 19200 | 0.00012 +/- 2.1e-05 | 7.38e-05 +/- 2.9e-05 |
| 500 | 3840 | 0.000448 +/- 7.4e-05 | 0.000371 +/- 4.6e-06 |
| 2000 | 960 | 0.00179 +/- 0.00024 | 0.0013 +/- 0.00031 |

Power-law exponent in N: **+0.899** (spread 14.9x). Per-image exposure is proportional to 1/N here, so an exponent of ~+1 is equally consistent with a dependence on optimisation progress rather than on N itself. Sweep B is the control.

**Sweep B -- constant per-image exposure (3840 gradient samples, seed 0).**

| N | iters | inpaint pixel var | NN dist to train image | final train loss |
|---|---|---|---|---|
| 100 | 6000 | 0.000859 | 0.000383 | 0.0159 |
| 500 | 30000 | 0.000379 | 0.000376 | 0.0089 |
| 2000 | 120000 | 0.000368 | 0.000259 | 0.0080 |

Power-law exponent in N: **-0.289** (spread 2.34x). Holding the optimisation budget per image fixed removes most of the apparent N-dependence.

**Control C -- runs lined up by training loss** (pixel variance, interpolated over every checkpoint of every run at that N).

| train loss | N=100 | N=500 | N=2000 |
|---|---|---|---|
| 0.03 | 0.00309 | 0.00578 | 0.0103 |
| 0.02 | 0.00109 | 0.00277 | 0.00313 |
| 0.015 | 0.000776 | 0.00123 | 0.00137 |
| 0.01 | 0.000315 | 0.000616 | 0.00058 |
