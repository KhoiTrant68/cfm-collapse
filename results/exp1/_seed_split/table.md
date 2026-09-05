**Where the EXP-1 error bar comes from.** Collapse ratio tr(Cov)/tr(Sigma_post) at the final checkpoint; standard deviations use the sample convention (n-1).

| varying | held fixed | n | mean | std | range |
|---|---|---|---|---|---|
| training run | problem instance | 10 | 0.3363 | **0.0675** | [0.2477, 0.4500] |
| problem instance | training run | 10 | 0.3986 | **0.1261** | [0.1819, 0.5580] |

Added in quadrature: **0.1431**, against the published combined spread of 0.123 (population std over 5 seeds, 0.1375 on the sample convention). The two sources account for the observed spread, which is a check on the decomposition and not only a measurement.

**The problem instance carries 78% of the variance and the training run 22%.** Roughly 78% of every EXP-1 error bar is therefore which operator A happened to be drawn, not how the run went; genuine run-to-run variability is about 0.49 of what the published bars imply. Fixing the instance tightens every interval without adding a single run.
