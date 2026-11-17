# Proposal 2: denoiser swap at sigma = s

off = fraction off-atom (d1/d2 >= 1/3); =L, =E = fraction whose nearest training image equals that of the learned / exact endpoint; d1 = median endpoint distance to the nearest image; abs-L = median distance of the exact->net endpoint to the learned endpoint.

## swap_sub500 (n=500; learned off-atom 0.038, exact off-atom 0.000, learned and exact share the nearest image 0.354)

| s | t | net->exact off | =L | =E | d1 | exact->net off | =L | =E | d1 | abs-L |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0.1667 | 0.000 | 0.928 | 0.374 | 0.000 | 0.000 | 0.374 | 0.954 | 1.670 | 26.951 |
| 2 | 0.3333 | 0.000 | 0.982 | 0.358 | 0.000 | 0.000 | 0.354 | 0.996 | 1.634 | 27.073 |
| 1 | 0.5000 | 0.000 | 0.996 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 1.492 | 27.053 |
| 0.5 | 0.6667 | 0.000 | 0.998 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 1.320 | 27.094 |
| 0.2 | 0.8333 | 0.000 | 1.000 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 1.126 | 27.006 |
| 0.1 | 0.9091 | 0.000 | 1.000 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 0.925 | 27.064 |
| 0.05 | 0.9524 | 0.000 | 1.000 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 0.692 | 27.017 |
| 0.02 | 0.9804 | 0.000 | 1.000 | 0.354 | 0.000 | 0.000 | 0.354 | 1.000 | 0.448 | 27.019 |
