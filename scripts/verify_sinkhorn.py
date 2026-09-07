"""Pin the Sinkhorn implementation to three closed forms.

The paper reports Sinkhorn divergences to the true posterior, so the estimator has
to be right. The fallback implementation (the one that runs here, since geomloss
needs KeOps) was not: it mixed a raw-unit dual potential into a log-domain kernel,
which made the returned number unrelated to the transport cost. It scored two
independent draws from the same Gaussian at 3.34 and a point mass against a
standard Gaussian at exactly 0 -- both diagnostic of a broken dual, and neither
caught by any test, because nothing compared the output with a value known in
advance.

Three cases where W_2^2 is known exactly:

  identical laws        S(mu, mu) = 0. Two independent M-sample draws from the same
                        law give the finite-sample floor, not 0, so this checks the
                        floor is small rather than that the number vanishes.

  translation           N(0, I_d) against N(c, I_d) has W_2^2 = |c|^2 -- the optimal
                        map is the translation itself.

  point mass            delta_0 against N(0, Sigma) has W_2^2 = E|x|^2 = tr Sigma,
                        since all mass must travel to the single point.

The entropic divergence is biased low relative to W_2^2 by an O(eps) term, so the
tolerances are loose but the *scale* has to be right; a broken dual misses by
orders of magnitude or by sign, which is what happened.

    uv run python scripts/verify_sinkhorn.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics.distances import sinkhorn_distance  # noqa: E402

M = 1000
BLUR = 0.1


def report(name: str, got: float, expect: float, rtol: float, atol: float) -> bool:
    ok = abs(got - expect) <= atol + rtol * abs(expect)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name:<44} got {got:9.4f}   expected {expect:9.4f}")
    return ok


def main() -> None:
    g = torch.Generator().manual_seed(0)
    results = []
    print("Sinkhorn divergence against closed-form W_2^2 "
          f"(M={M}, blur={BLUR}, p=2):")

    # 1. identical laws -- the finite-sample floor, which must be small on the
    #    scale of the law's own spread (tr I_2 = 2).
    a = torch.randn(M, 2, generator=g)
    b = torch.randn(M, 2, generator=g)
    s_same = sinkhorn_distance(a, b, blur=BLUR)
    results.append(report("N(0,I_2) vs an independent draw of itself",
                          s_same, 0.0, 0.0, 0.10))

    # 2. translation: W_2^2 = |c|^2 exactly, for any c.
    for c in (1.0, 3.0):
        s = sinkhorn_distance(a, b + c, blur=BLUR)
        # the same finite-sample floor rides on top, so allow it as atol
        results.append(report(f"N(0,I_2) vs N({c:g}*1, I_2)   [W_2^2 = {2 * c * c:g}]",
                              s, 2 * c * c, 0.05, 0.15))

    # 3. point mass: W_2^2 = tr Sigma. Also the case the broken version returned 0
    #    for, which is the one that mattered -- a collapsed model is a point mass.
    for d, scale in ((2, 1.0), (2, 0.5), (4, 1.0)):
        gg = torch.Generator().manual_seed(1)
        s_ = scale * torch.randn(M, d, generator=gg)
        pt = torch.zeros(M, d)
        results.append(report(f"delta_0 vs N(0,{scale:g}^2 I_{d})  [tr Sigma = "
                              f"{d * scale * scale:g}]",
                              sinkhorn_distance(pt, s_, blur=BLUR),
                              d * scale * scale, 0.10, 0.15))

    # 4. symmetry. Exact for the true divergence; here the iteration updates f
    #    before g, so swapping the arguments leaves a residual at the level of
    #    what 200 annealed steps have not yet converged -- 4e-5 on a value of 1.9,
    #    which bounds that residual rather than merely asserting symmetry.
    s_ab = sinkhorn_distance(a, b + 1.0, blur=BLUR)
    s_ba = sinkhorn_distance(b + 1.0, a, blur=BLUR)
    results.append(report("symmetry S(x,y) = S(y,x)", s_ab - s_ba, 0.0, 0.0, 1e-3))

    n_ok = sum(results)
    print(f"\n{n_ok}/{len(results)} checks passed")
    if n_ok != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
