**EXP-3 at realistic capacity** -- CIFAR-10 inpainting, DDPM U-Net (35.75M parameters), N=2000, 60000 iterations at batch 128 (3840 gradient samples per training image), seed 0.

| h | n_eff | tr Cov_h (target) | tr Cov measured | ratio | &#124;mean - x&#772;_h&#124; | pixel var | NN dist |
|---|---|---|---|---|---|---|---|
| 0 | 1.0 | 0 | 0.431 | -- | 0.8664 | 0.0002779 | 0.0002556 |
| 4 | 2.4 | 79.15 | 178.5 | 4.388 | 8.208 | 0.07936 | 0.02565 |
| 5 | 17.2 | 222.3 | 276.8 | 1.285 | 10.69 | 0.1096 | 0.02913 |
| 6 | 77.9 | 344.1 | 406.4 | 1.173 | 8.363 | 0.15 | 0.04095 |

At h=0 the kernel reference is a single atom, so tr Cov_h is exactly 0 and the ratio is undefined; |mean - x&#772;_h| is then the distance to the memorised training image.

**Trajectory of ratio_to_kernel** (target 1).

| iter | h=4 | h=5 | h=6 |
|---|---|---|---|
| 500 | 11.543 | 2.641 | 2.095 |
| 2000 | 10.923 | 2.439 | 1.774 |
| 8000 | 5.082 | 1.236 | 0.936 |
| 20000 | 6.151 | 1.324 | 0.773 |
| 40000 | 4.600 | 1.139 | 1.000 |
| 60000 | 4.388 | 1.285 | 1.173 |

**h=0 collapse trajectory** (Proposition 4 control).

| iter | tr Cov | &#124;mean - x^i&#124; | pixel var | NN dist |
|---|---|---|---|---|
| 500 | 179.1 | 14.47 | 0.1161 | 0.07014 |
| 2000 | 183.7 | 14.03 | 0.1195 | 0.06468 |
| 8000 | 2.958 | 1.937 | 0.001905 | 0.001278 |
| 20000 | 1.074 | 1.305 | 0.0006877 | 0.0005875 |
| 40000 | 0.5565 | 0.7966 | 0.0003583 | 0.0002163 |
| 60000 | 0.431 | 0.8664 | 0.0002779 | 0.0002556 |

Collapse factor in tr Cov over the run: **415x** (179.1 to 0.431).
