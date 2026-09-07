"""Does the atomicity floor over *i.i.d.* training atoms really scale like N^(-2/d)?

The paper attributes the floor's scaling to Zador's theorem. Zador is about the
OPTIMAL N-point quantiser -- the infimum of E dist(X,S)^2 over all N-point sets S --
whereas the floor of \eqref{eq:w2floor} is

    F_N = E_{X ~ p} dist(X, {x^1..x^N})^2

over the atoms the training set happened to draw, which are i.i.d. from the data law
and not placed optimally. The two are different objects and only one of the two
directions is immediate: since the training atoms are one admissible N-point set,

    F_N  >=  (optimal N-point error)^2  ~  C N^(-2/d),

so Zador lower-bounds the floor, which is the direction the paper's argument needs.
Whether i.i.d. atoms also ACHIEVE that exponent, rather than doing worse, is a
separate question about nearest-neighbour distances under a random design.

This script measures it, so the paper can report the exponent instead of borrowing a
theorem about a different object. For a standard Gaussian target in d = 2, 3, 5, 8 it
sweeps N and fits log F_N on log N; the prediction is slope -2/d.

    uv run python scripts/verify_atom_floor_scaling.py

Writes: results/exp1/_theory/raw/atom_floor_scaling.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
import torch

OUT = Path("results/exp1/_theory/raw/atom_floor_scaling.csv")
DIMS = (2, 3, 5, 8)
NS = (50, 100, 200, 400, 800, 1600, 3200)
M_EVAL = 20000     # points at which dist(X, atoms) is averaged
N_REP = 12         # independent redraws of the atom set, to average F_N


@torch.no_grad()
def floor_iid(d: int, N: int, gen: torch.Generator) -> tuple[float, float]:
    """E dist(X, {X_1..X_N})^2 for i.i.d. standard-Gaussian atoms, and its s.d."""
    vals = []
    for _ in range(N_REP):
        atoms = torch.randn(N, d, generator=gen, dtype=torch.float64)
        x = torch.randn(M_EVAL, d, generator=gen, dtype=torch.float64)
        d2 = torch.cdist(x, atoms) ** 2
        vals.append(float(d2.min(dim=1).values.mean()))
    v = np.array(vals)
    return float(v.mean()), float(v.std(ddof=1))


def main() -> None:
    rows = []
    print(f"{'d':>3} {'N':>6} {'F_N':>12} {'s.d.':>10}")
    for d in DIMS:
        gen = torch.Generator().manual_seed(1000 + d)
        for N in NS:
            f, sd = floor_iid(d, N, gen)
            rows.append({"d": d, "N": N, "floor": f, "floor_sd": sd})
            print(f"{d:>3} {N:>6} {f:>12.6f} {sd:>10.6f}", flush=True)

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"\n{'d':>3} {'fitted slope':>13} {'predicted -2/d':>15} {'R^2':>8}  verdict")
    ok = True
    for d, g in df.groupby("d"):
        # Fit on the larger N only: the asymptotic rate is not the small-N regime,
        # where the atom set is too sparse for the nearest-neighbour picture.
        g = g[g["N"] >= 200]
        sl, _ = np.polyfit(np.log(g["N"]), np.log(g["floor"]), 1)
        r2 = np.corrcoef(np.log(g["N"]), np.log(g["floor"]))[0, 1] ** 2
        pred = -2.0 / d
        good = abs(sl - pred) < 0.15 * abs(pred)
        # d = 2 is expected to miss, and the reason is checked below rather than
        # waved at: i.i.d. atoms there carry a log N factor the optimal quantiser
        # does not, so the pure power law is the wrong model, not a failed fit.
        expect_power_law = d >= 3
        ok &= (good == expect_power_law)
        print(f"{d:>3} {sl:>13.4f} {pred:>15.4f} {r2:>8.4f}  "
              f"{'power law' if good else 'NOT a pure power law'}")

    print("\nd=2: is the deviation a log N correction? F_N * N / log N should then be "
          "constant.")
    g2 = df[(df["d"] == 2) & (df["N"] >= 200)]
    ratio_log = (g2["floor"] * g2["N"] / np.log(g2["N"])).values
    ratio_pow = (g2["floor"] * g2["N"]).values
    drift_log = ratio_log.max() / ratio_log.min()
    drift_pow = ratio_pow.max() / ratio_pow.min()
    print(f"  F*N/log N : {' '.join(f'{v:.3f}' for v in ratio_log)}"
          f"   (drift {drift_log:.2f}x)")
    print(f"  F*N       : {' '.join(f'{v:.3f}' for v in ratio_pow)}"
          f"   (drift {drift_pow:.2f}x)")
    log_wins = drift_log < drift_pow
    print(f"  the log model {'wins' if log_wins else 'DOES NOT win'}: "
          f"at d=2 the i.i.d. floor is c log(N)/N, not c/N.")
    ok &= log_wins

    print("\nSo the two objects genuinely differ. Zador bounds the floor from below "
          "for any\nN atoms, optimal or not, and that is the direction the paper's "
          "argument needs. In\ndimension 3 and above i.i.d. atoms attain the same "
          "exponent; at d=2 they are worse\nby a log N factor, so the paper should not "
          "cite Zador for its own floor's rate.")
    print(f"wrote {OUT}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
