"""Check the near-duplicate-label bounds numerically before they go in the paper.

Setting: the query label y sits within eps of a cluster C of training labels, and
at least Delta from every other label. With a Gaussian kernel of bandwidth h the
claim is

    (a)  sum_{j not in C} p_j  <=  eta := ((N-|C|)/|C|) exp(-(Delta^2 - eps^2)/(2h^2))
    (b)  p_i / p_i'            <=  kappa := exp(eps^2/(2h^2))        for i, i' in C
    (c)  n_eff                 >=  |C| / (kappa + |C| eta^2)

so that as eps/h -> 0 and Delta/h -> infinity the index posterior becomes uniform
on C, the endpoint law becomes the cluster average of the atoms, and n_eff -> |C|.

Each bound is checked against the exact weights over many random instances; the
script reports the worst violation, which should be none.

    uv run python scripts/verify_cluster_bounds.py
"""
from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(0)


def instance(N: int, k: int, csize: int, eps: float, delta: float):
    """Labels: `csize` of them within eps of the origin, the rest beyond delta."""
    y = np.zeros(k)
    inside = RNG.normal(size=(csize, k))
    inside *= (RNG.uniform(0, eps, size=(csize, 1))
               / np.linalg.norm(inside, axis=1, keepdims=True))
    outside = RNG.normal(size=(N - csize, k))
    outside *= ((delta + RNG.exponential(0.7, size=(N - csize, 1)))
                / np.linalg.norm(outside, axis=1, keepdims=True))
    return y, np.vstack([inside, outside])


def main() -> None:
    print(f"{'k':>2} {'N':>4} {'|C|':>4} {'eps':>6} {'Delta':>6} {'h':>5} "
          f"{'(a) slack':>11} {'(b) slack':>11} {'(c) slack':>11}")
    worst = {"a": np.inf, "b": np.inf, "c": np.inf}
    for k in (1, 3, 8):
        for csize in (2, 5, 17):
            for eps, delta, h in ((0.05, 2.0, 0.3), (0.2, 1.5, 0.4),
                                  (0.01, 3.0, 0.25), (0.4, 1.2, 0.5)):
                N = 60
                y, Y = instance(N, k, csize, eps, delta)
                d2 = ((y[None, :] - Y) ** 2).sum(1)
                logK = -0.5 * d2 / h ** 2
                logK -= logK.max()
                w = np.exp(logK)
                p = w / w.sum()

                eta = ((N - csize) / csize) * np.exp(-(delta ** 2 - eps ** 2)
                                                     / (2 * h ** 2))
                kappa = np.exp(eps ** 2 / (2 * h ** 2))
                out_mass = p[csize:].sum()
                ratio = p[:csize].max() / p[:csize].min()
                n_eff = 1.0 / (p ** 2).sum()
                n_eff_lb = csize / (kappa + csize * eta ** 2)

                sa, sb, sc = eta - out_mass, kappa - ratio, n_eff - n_eff_lb
                worst["a"] = min(worst["a"], sa)
                worst["b"] = min(worst["b"], sb)
                worst["c"] = min(worst["c"], sc)
                print(f"{k:>2} {N:>4} {csize:>4} {eps:>6.2f} {delta:>6.2f} {h:>5.2f} "
                      f"{sa:>11.3e} {sb:>11.3e} {sc:>11.3e}")
    print("\nworst slack (negative would be a violation):")
    for key, v in worst.items():
        print(f"  ({key})  {v:+.4e}   {'OK' if v >= 0 else 'VIOLATED'}")


if __name__ == "__main__":
    main()
