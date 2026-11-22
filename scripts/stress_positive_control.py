"""Positive control for the exact-field stress test (Section sec:intervention-tests).

    uv run --no-sync python -m scripts.stress_positive_control

The stress test of ``scripts/novelty_interventions.py`` integrates exact fields with a fixed-step
RK4 in the log time s = -log(1-t), 256 (coarse) and 512 (fine) steps per segment, segments ending at
the terminal gaps 1-T = 1e-2, 1e-4, 1e-6, and reports that no sample ends farther than 1% of the
minimum atom separation from an atom. None of its arms has an attracting non-atom candidate, so a
pipeline biased towards the atoms would pass it. This script feeds the same scheme a field that does
have one: guidance applied to the average of two conditional fields on the atoms (+-1, 0) in d=2
(Theorem thm:composition embedded in the plane; the second coordinate decays like e^{-s}), at
B = 1 and w/w_c in {0.9, 1.1, 2, 10}. The exact probabilities of the midpoint come from the stiff
integrator with proof-based stopping rules (results/theory_composition_20261019/summary.json).

The oracle and the RK4 below transcribe ``oracle`` and ``rk4`` of novelty_interventions.py into
NumPy (float64; that file needs torch, which does not load on this machine). Nothing here proves
anything: a fixed-step scheme that detects the blend is consistent with the theorem, and one that
misses it shows that the stress test cannot see attracting ties at that gap.

Per source, each row also compares the fixed-step class with the exact one. The second coordinate
decays like e^{-s} and the first follows the one-dimensional composite, so a source belongs to the
exact basin of the midpoint exactly when its first coordinate lies in the interval
(basin_low, basin_high) of the same summary file (empty when the threshold is not exceeded).
"disagree" counts the sources whose fixed-step endpoint lies within 0.05 of the midpoint but whose
first coordinate is outside the interval, or the converse; "flagged_vs_midpoint_disagree" counts
those flagged by the 1% criterion of the stress test that are not within 0.05 of the midpoint, or
the converse; max_abs_x1/x2_at_midpoint are the largest coordinates of the endpoints within 0.05 of
the midpoint.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

OUT = Path("results/stress_positive_control_20261121")
GAPS = (1e-2, 1e-4, 1e-6)
EXACT = Path("results/theory_composition_20261019/summary.json")


def softmax(z):
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


def oracle(x, s, atoms, lp, w):
    """(1+w) * mean_k posterior mean under prior lp[k]  -  w * uniform posterior mean  -  x."""
    eps = math.exp(-s); t = -math.expm1(-s)
    spatial = -0.5 * ((x[:, None, :] - t * atoms[None]) ** 2).sum(-1) / eps ** 2       # (M, N)
    cond = (softmax(spatial[:, None, :] + lp[None]) @ atoms).mean(1)                      # (M, d)
    unc = softmax(spatial) @ atoms
    return (1 + w) * cond - w * unc - x


def rk4(f, x, steps, ends):
    """Fixed-step RK4 recording at prescribed end times, as in novelty_interventions.rk4."""
    x = x.copy(); saved = []; start = 0.0
    for end in ends:
        ds = (end - start) / steps
        for i in range(steps):
            s = start + i * ds
            a = f(x, s); b = f(x + ds * a / 2, s + ds / 2)
            c = f(x + ds * b / 2, s + ds / 2); d = f(x + ds * c, s + ds)
            x = x + ds * (a + 2 * b + 2 * c + d) / 6
        saved.append(x.copy()); start = end
    return np.stack(saved)


def exact_row(B: float, ratio: float) -> dict:
    rows = json.loads(EXACT.read_text(encoding="utf-8"))["rows"]
    for r in rows:
        if r["name"] == f"symmetric_B{B:g}_w{ratio:g}wc":
            return r
    raise KeyError((B, ratio))


def exact_probability(B: float, ratio: float) -> float:
    return float(exact_row(B, ratio)["basin_probability"])


def exact_basin(B: float, ratio: float, x1: np.ndarray) -> np.ndarray:
    """Sources whose first coordinate lies in the exact basin interval of the midpoint."""
    r = exact_row(B, ratio)
    lo, hi = r.get("basin_low"), r.get("basin_high")
    if lo is None or hi is None:
        return np.zeros(len(x1), bool)
    return (x1 > lo) & (x1 < hi)


def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    atoms = np.array([[-1.0, 0.0], [1.0, 0.0]])
    sep = 2.0
    rng = np.random.default_rng(20261121)
    x0 = rng.normal(size=(4096, 2))
    ends = np.log(1 / np.array(GAPS))
    rows = []
    B = 1.0
    wc = 1 / math.sinh(B) ** 2
    lp = np.array([[-B, B], [B, -B]])        # log priors on (atom -1, atom +1): log-odds +-2B
    for ratio in (0.9, 1.1, 2.0, 10.0):
        w = ratio * wc
        f = lambda x, s: oracle(x, s, atoms, lp, w)   # noqa: E731
        basin = exact_basin(B, ratio, x0[:, 0])
        for steps in (256, 512):
            P = rk4(f, x0, steps, ends)
            for j, gap in enumerate(GAPS):
                end = P[j]
                finite = np.isfinite(end).all(1)
                near = np.linalg.norm(end[:, None, :] - atoms[None], axis=-1).min(1)
                mid = np.linalg.norm(end, axis=1) < 0.05
                flagged = near > 0.01 * sep
                rows.append({
                    "B": B, "w_over_wc": ratio, "steps_per_segment": steps, "gap": gap,
                    "dtau": float(ends[0] / steps),
                    "fraction_finite": float(finite.mean()),
                    "fraction_at_midpoint_0.05": float(mid[finite].mean()),
                    "fraction_outside_1pct_minseparation": float(flagged[finite].mean()),
                    "exact_midpoint_probability": exact_probability(B, ratio),
                    "midpoint_count": int(mid.sum()),
                    "exact_basin_count": int(basin.sum()),
                    "disagree": int((mid != basin).sum()),
                    "flagged_vs_midpoint_disagree": int((flagged != mid).sum()),
                    "max_abs_x1_at_midpoint": float(np.abs(end[mid, 0]).max()) if mid.any() else None,
                    "max_abs_x2_at_midpoint": float(np.abs(end[mid, 1]).max()) if mid.any() else None,
                })
                print(rows[-1], flush=True)
    res = {"script": "scripts/stress_positive_control.py", "M": len(x0), "gaps": GAPS,
           "seconds": time.time() - t0, "rows": rows,
           "note": "fixed-step log-time RK4 as in novelty_interventions.py; numerical check, not a proof"}
    (OUT / "summary.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"wrote {OUT / 'summary.json'}")


if __name__ == "__main__":
    main()
