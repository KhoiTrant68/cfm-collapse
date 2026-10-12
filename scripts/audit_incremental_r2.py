"""Does h_eff add predictive information beyond the free baselines? (synthetic, held out)

For the 75 synthetic checkpoints of the calibration audit (results/exp1/_heff/
audit_calibration_v2.json) this predicts three held-out quantities measured on fresh
pairs (x*, y*) never used to fit h_eff:

  test_coverage_90   coverage of the nominal 90% region
  test_pit_error     posterior-free PIT error
  test_w2_median     median W2 distance between generated and true posterior

from a baseline of quantities a practitioner has without the audit -- log iteration,
log training loss, log raw generated variance, the share of samples on a training atom,
and the training bandwidth h -- and from the same baseline plus log h_eff. Each
continuous feature enters with its square, so both models get the same flexibility.

R^2 is cross-validated leave-one-run-out (15 runs, all checkpoints of a run held out
together), so no run informs its own prediction. Delta R^2 = R^2(baseline + h_eff) -
R^2(baseline); its 95% interval resamples runs (the whole CV is redone per resample).

Reads:  results/exp1/_heff/audit_calibration_v2.json
Writes: results/exp1/_heff/audit_incremental_r2.json
Usage:  python scripts/audit_incremental_r2.py [--boot 1000]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

TARGETS = ("test_coverage_90", "test_pit_error", "test_w2_median")


def features(rows, with_heff: bool) -> np.ndarray:
    cols = [np.log([r["iter"] for r in rows]), np.log([r["train_loss"] for r in rows]),
            np.log([r["trace_raw"] for r in rows])]
    if with_heff:
        cols.append(np.log([r["h_eff"] for r in rows]))
    sq = [c ** 2 for c in cols]
    lin = [np.array([r["on_atom_train"] for r in rows]), np.array([r["h"] for r in rows])]
    return np.column_stack(cols + sq + lin)


def cv_r2(X: np.ndarray, y: np.ndarray, groups: np.ndarray, ridge: float = 1e-3) -> float:
    pred = np.empty_like(y)
    for g in np.unique(groups):
        tr, te = groups != g, groups == g
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12
        A = np.column_stack([np.ones(tr.sum()), (X[tr] - mu) / sd])
        B = np.column_stack([np.ones(te.sum()), (X[te] - mu) / sd])
        w = np.linalg.solve(A.T @ A + ridge * np.eye(A.shape[1]), A.T @ y[tr])
        pred[te] = B @ w
    return float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rows = json.loads(Path("results/exp1/_heff/audit_calibration_v2.json").read_text(encoding="utf-8"))
    runs = np.array([r["run"] for r in rows])
    uniq = np.unique(runs)
    X0, X1 = features(rows, False), features(rows, True)
    xh = np.column_stack([np.log([r["h_eff"] for r in rows]), np.log([r["h_eff"] for r in rows]) ** 2])
    rng = np.random.default_rng(args.seed)
    out = {"n": len(rows), "runs": len(uniq), "targets": {}}
    print(f"{len(rows)} checkpoints, {len(uniq)} runs; leave-one-run-out CV R^2")
    for t in TARGETS:
        y = np.array([r[t] for r in rows], float)
        r0, r1, rh = cv_r2(X0, y, runs), cv_r2(X1, y, runs), cv_r2(xh, y, runs)
        boots = []
        for _ in range(args.boot):
            pick = rng.choice(uniq, size=len(uniq), replace=True)
            idx = np.concatenate([np.flatnonzero(runs == g) for g in pick])
            # relabel resampled runs so a run drawn twice forms two groups
            grp = np.concatenate([np.full((runs == g).sum(), k) for k, g in enumerate(pick)])
            boots.append(cv_r2(X1[idx], y[idx], grp) - cv_r2(X0[idx], y[idx], grp))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        out["targets"][t] = {"r2_baseline": r0, "r2_baseline_plus_heff": r1, "r2_heff_alone": rh,
                             "delta_r2": r1 - r0, "delta_r2_ci95": [float(lo), float(hi)]}
        print(f"  {t:18s} baseline {r0:.3f}  +h_eff {r1:.3f}  dR2 {r1 - r0:+.3f} "
              f"[{lo:+.3f}, {hi:+.3f}]  (h_eff alone {rh:.3f})")
    p = Path("results/exp1/_heff/audit_incremental_r2.json")
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("Saved:", p)


if __name__ == "__main__":
    main()
