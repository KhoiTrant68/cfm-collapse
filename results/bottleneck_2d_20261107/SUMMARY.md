# Label bottleneck and tie-agnostic inputs on the triangle

w_c = 1.1596; bottleneck cell priors are vertex priors with B_Q = 1.241279, w_c(B_Q) = 3.9262. Midpoint occupancy |x| < 0.05 at 1 - t = 1e-5, mean ± sd over seeds.

## Composite L3

| w/w_c | exact | exact (bottleneck priors) | cfm_x_sq | cfm_x_o | cfm_x_s (tie-centred, reference) |
|---|---|---|---|---|---|
| 0 | 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 0.5 | 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 0.9 | 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 1.1 | 0.002 | 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.001 ± 0.002 |
| 2 | 0.133 | 0.179 | 0.120 ± 0.093 | 0.000 ± 0.000 | 0.143 ± 0.004 |
| 5 | 0.673 | 0.757 | 0.760 ± 0.042 | 0.000 ± 0.000 | 0.692 ± 0.023 |
| 10 | 0.952 | 0.972 | 0.986 ± 0.002 | 0.000 ± 0.000 | 0.962 ± 0.005 |

## Single-query guidance L2 (exact: no midpoint mass at any w)

| w/w_c | cfm_x_sq | cfm_x_o | cfm_x_s (tie-centred, reference) |
|---|---|---|---|
| 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 2 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 10 | 0.309 ± 0.433 | 0.000 ± 0.000 | 0.000 ± 0.000 |
