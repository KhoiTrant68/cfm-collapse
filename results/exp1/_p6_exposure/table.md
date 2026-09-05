**P6 at fixed budget versus at fixed exposure.** Collapse ratio tr(Cov)/tr(Sigma_post) at the final checkpoint, mean +/- std over seeds.

| N | iterations | grad. samples / point | fixed budget (2e5 iters) | fixed exposure |
|---|---|---|---|---|
| 50 | 10000 | 51200 | 0.049 +/- 0.038 | 0.444 +/- 0.196 (n=5) |
| 200 | 40000 | 51200 | 0.389 +/- 0.123 | 0.774 +/- 0.165 (n=5) |
| 1000 | 200000 | 51200 | 0.912 +/- 0.103 | 0.928 +/- 0.087 (n=5) |
| 5000 | 1000000 | 51200 | 0.990 +/- 0.031 | 1.014 +/- 0.065 (n=5) |

Spread across N: **20.2x** at fixed budget, **2.28x** at fixed exposure. In the published sweep each point of the N=50 run receives 1024000 gradient samples against 10240 for N=5000, a factor of 100; holding that fixed removes most of the apparent N-dependence, exactly as it did on EXP-3 (14.9x to 2.3x). What remains is a real but modest effect, and its smallness is what Proposition 4 predicts: the population minimiser is collapsed for every finite N, so a large intrinsic N-dependence would be the surprise.
