"""Unit + acceptance tests for src/metrics/kernel_theory.py (WORK_ORDER T1).

Runs without retraining. Checks:
  1. kernel_weights: h->0 one-hot at nearest label (Cor 11); h->inf uniform 1/N (Cor 12).
  2. kernel_field(sigma=0, h=0) matches closed_form_velocity to 1e-6.
  3. cov_expansion returns ||J||_F^2 = 0.4031 for default d=2,k=1,sigma_obs=0.1.
  4. Reproduces the WORK_ORDER section-0 table of tr Cov_h averaged over 20 conditions:
         h=0.01 -> 0.427,  h=0.05 -> 0.973,  h=0.1 -> 1.145,  h=0.5 -> 1.244   (<1% err).

    uv run python scripts/test_kernel_theory.py
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

from src.flows.interpolants import closed_form_velocity  # noqa: E402
from src.metrics.kernel_theory import (
    kernel_moments_trace,  # noqa: E402
    cov_expansion,
    kernel_field,
    kernel_trace_cov,
    kernel_weights,
)
from src.problems.linear_gaussian import LinearGaussianProblem  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
_ok = True


def check(name: str, cond: bool, detail: str = "") -> None:
    global _ok
    _ok = _ok and cond
    print(f"[{PASS if cond else FAIL}] {name}" + (f"  ({detail})" if detail else ""))


def main() -> None:
    torch.manual_seed(0)
    N, k = 200, 1
    Y = torch.randn(N, k, dtype=torch.float64)
    X = torch.randn(N, 2, dtype=torch.float64)
    y_q = Y[37].clone()

    # 1a. h -> 0 : one-hot at nearest label (here exactly y_q = Y[37])
    w0 = kernel_weights(y_q, Y, h=0.0)
    check("Cor 11: h=0 -> one-hot at nearest label",
          int(w0.argmax()) == 37 and abs(float(w0.max()) - 1.0) < 1e-9,
          f"argmax={int(w0.argmax())}, max={float(w0.max()):.6f}")

    # 1a. Duplicate labels: h=0 spreads uniformly over the tied set, which is the
    #     empirical conditional support of the duplicate-label case. With distinct
    #     labels this reduces to the one-hot above.
    lab = torch.tensor([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
    Yc = torch.zeros(12, 3, dtype=torch.float64)
    Yc[torch.arange(12), lab] = 1.0
    Xc = torch.randn(12, 5, dtype=torch.float64, generator=torch.Generator().manual_seed(0))
    wt = kernel_weights(Yc[5], Yc, h=0.0)
    check("duplicate labels: h=0 -> uniform on the tied class",
          bool(torch.allclose(wt[4:8], torch.full((4,), 0.25, dtype=torch.float64)))
          and float(wt.sum()) - float(wt[4:8].sum()) < 1e-12,
          f"class weights={[round(float(v), 4) for v in wt[4:8]]}")
    _, tr_tied, ne_tied = kernel_moments_trace(Yc[5], Xc, Yc, h=0.0)
    sub = Xc[4:8]
    want = float(((sub - sub.mean(0)) ** 2).sum(1).mean())
    check("duplicate labels: n_eff = class size, tr Cov_0 = within-class scatter",
          abs(ne_tied - 4.0) < 1e-9 and abs(tr_tied - want) < 1e-9,
          f"n_eff={ne_tied:.4f} (want 4), tr={tr_tied:.6f} (want {want:.6f})")

    # 1a'. small-but-positive h still concentrates on nearest label
    w_small = kernel_weights(y_q, Y, h=1e-3)
    check("h->0+ concentrates on nearest label",
          int(w_small.argmax()) == 37 and float(w_small.max()) > 0.99)

    # 1b. h -> inf : uniform 1/N
    w_big = kernel_weights(y_q, Y, h=1e6)
    check("Cor 12: h->inf -> uniform 1/N",
          float((w_big - 1.0 / N).abs().max()) < 1e-6,
          f"max|w-1/N|={float((w_big - 1.0 / N).abs().max()):.2e}")

    # 2. kernel_field(sigma=0, h=0) == closed_form_velocity (single-atom collapse)
    #    h=0 selects the nearest label; query y_q=Y[i] -> atom i, field = (x^i - x)/(1-t).
    i = 37
    P = 500
    g = torch.Generator().manual_seed(1)
    x = torch.randn(P, 2, generator=g, dtype=torch.float64)
    t = 0.9 * torch.rand(P, generator=g, dtype=torch.float64)
    v_kernel = kernel_field(x, t, Y[i], X, Y, h=0.0, source_std=1.0)
    v_star = closed_form_velocity(x, t, X[i].to(torch.float64)).to(torch.float64)
    max_abs = float((v_kernel - v_star).abs().max())
    check("Prop 8/4: kernel_field(h=0) == closed_form_velocity",
          max_abs < 1e-6, f"max|diff|={max_abs:.2e}")

    # 3. cov_expansion ||J||_F^2 for the default problem
    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0,
                                        prior_std=1.0, A_kind="random")
    _, j_fro_sq = cov_expansion(prob, h=0.1)
    check("Prop 15: ||J||_F^2 = 0.4031 (default d=2,k=1,sigma_obs=0.1)",
          abs(j_fro_sq - 0.4031) < 1e-3, f"||J||_F^2={j_fro_sq:.4f}")

    # 4. Reproduce the WORK_ORDER section-0 table on the real training set.
    #    p7y_h*_seed0 all share seed=0 -> identical (X, Y) = sample_dataset(N=200, seed=1).
    Xr, Yr = prob.sample_dataset(200, seed=1)
    Xr, Yr = Xr.to(torch.float64), Yr.to(torch.float64)
    idx = sorted(set(torch.linspace(0, 199, 20).round().long().tolist()))
    expected = {0.01: 0.427, 0.05: 0.973, 0.1: 1.145, 0.5: 1.244}
    print(f"\n  {'h':>6} | {'tr Cov_h (Thm 10)':>18} | {'expected':>9} | {'rel.err':>8}")
    print("  " + "-" * 50)
    for h, exp in expected.items():
        vals = [kernel_trace_cov(Yr[j], Xr, Yr, h) for j in idx]
        got = float(torch.tensor(vals).mean())
        rel = abs(got - exp) / exp
        print(f"  {h:>6.2f} | {got:>18.4f} | {exp:>9.3f} | {rel:>7.2%}")
        check(f"section-0 table h={h}", rel < 0.01, f"got={got:.4f} exp={exp}")

    print("\n" + ("ALL TESTS PASSED" if _ok else "SOME TESTS FAILED"))
    sys.exit(0 if _ok else 1)


if __name__ == "__main__":
    main()
