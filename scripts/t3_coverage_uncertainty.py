"""How sure is the R^2 = 0.90 of Theorem 1(d)'s coverage prediction?

The prediction has no parameter fitted to coverage (h_eff is read from the training
conditions), so there is nothing to cross-validate. What the 75 checkpoints do not give
is 75 independent units: they are nested in 15 runs. This script reports

  run_bootstrap   the R^2 (and MAE, Spearman) with a 95% interval from resampling runs
  noise_ceiling   the R^2 that a perfect prediction would reach given the binomial noise
                  of a coverage measured on n_test held-out pairs: 1 - E[p(1-p)/n] / Var(p)

for the local model and the exact finite reference law, at the 90% and 50% levels.

Reads:  results/theory/t3_coverage.json (written by scripts/theory_t3_coverage.py)
Writes: results/theory/t3_coverage_uncertainty.json
Usage:  uv run python scripts/t3_coverage_uncertainty.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

SRC = Path("results/theory/t3_coverage.json")
OUT = Path("results/theory/t3_coverage_uncertainty.json")
N_TEST = 100                                    # held-out pairs per checkpoint, as measured
N_BOOT = 10000


def scores(pred: np.ndarray, meas: np.ndarray) -> dict:
    rk = lambda v: np.argsort(np.argsort(v))
    return {"r2": float(1 - np.sum((meas - pred) ** 2) / np.sum((meas - meas.mean()) ** 2)),
            "mae": float(np.mean(np.abs(pred - meas))),
            "spearman": float(np.corrcoef(rk(pred), rk(meas))[0, 1])}


def main() -> None:
    rows = json.loads(SRC.read_text(encoding="utf-8"))["t3d"]["rows"]
    runs = sorted({r["run"] for r in rows})
    by_run = {u: [r for r in rows if r["run"] == u] for u in runs}
    rng = np.random.default_rng(0)
    out = {"n_checkpoints": len(rows), "n_runs": len(runs), "n_test": N_TEST}
    for a in (90, 50):
        meas = np.array([r[f"measured_cov_{a}"] for r in rows])
        noise = np.mean(meas * (1 - meas) / N_TEST)
        out[f"noise_ceiling_r2_{a}"] = float(1 - noise / np.var(meas))
        for model in ("local", "ref"):
            pred = np.array([r[f"{model}_cov_{a}"] for r in rows])
            boot = []
            for _ in range(N_BOOT):
                pick = [r for u in rng.choice(runs, len(runs)) for r in by_run[u]]
                p = np.array([r[f"{model}_cov_{a}"] for r in pick])
                m = np.array([r[f"measured_cov_{a}"] for r in pick])
                if np.var(m) > 0:
                    boot.append(scores(p, m))
            res = scores(pred, meas)
            for k in list(res):
                v = [b[k] for b in boot]
                res[f"{k}_ci95"] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
            out[f"{model}_{a}"] = res
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for a in (90, 50):
        print(f"{a}% level: noise ceiling R^2 {out[f'noise_ceiling_r2_{a}']:.3f}")
        for model in ("local", "ref"):
            r = out[f"{model}_{a}"]
            print(f"  {model:5s} R^2 {r['r2']:.3f} [{r['r2_ci95'][0]:.3f}, {r['r2_ci95'][1]:.3f}]  "
                  f"MAE {r['mae']:.3f}  Spearman {r['spearman']:.3f} "
                  f"[{r['spearman_ci95'][0]:.3f}, {r['spearman_ci95'][1]:.3f}]")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
