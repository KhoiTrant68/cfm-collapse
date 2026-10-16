"""Reproduce the saved-statistics diagnostic; no training or model sampling.

Run from the repository root with its virtualenv. The 30-second ceiling is an
abort rule for this small audit, not an estimate for future model experiments.
"""
from pathlib import Path
import json
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.heff_family_test import reference_tables, loo_rmse


def main():
    started = time.monotonic()
    archive = np.load(ROOT / "results/exp1/_heff/family_stats.npz")
    saved = json.loads(Path(__file__).with_name("heldout_family.json").read_text())
    rows = []
    for name in archive["runs"]:
        name = str(name)
        seed, h, prior_std, _ = archive[f"{name}/meta"]
        if h > 0.1:
            continue
        args = [archive[f"{name}/{key}"] for key in ("X", "Y", "A")]
        args += [prior_std, archive[f"{name}/idx"]]
        refs = {
            family: np.log(np.maximum(reference_tables(family, *args)[1], 1e-300))
            for family in ("gauss", "laplace", "cauchy", "knn")
        }
        for iteration, trace in zip(archive[f"{name}/iters"], archive[f"{name}/trace"]):
            if iteration < 10000:
                continue
            row = dict(run=name, seed=int(seed), h=float(h), iter=int(iteration))
            row.update({family: loo_rmse((np.log(trace)[None, :] - table) ** 2)
                        for family, table in refs.items()})
            rows.append(row)
        if time.monotonic() - started > 30:
            raise TimeoutError("Saved-statistics audit exceeded its 30-second ceiling")
    expected = {(r["run"], r["iter"]): r for r in saved["rows"]}
    assert len(rows) == len(expected) == 48
    for row in rows:
        old = expected[row["run"], row["iter"]]
        for family in refs:
            np.testing.assert_allclose(row[family], old[family], rtol=1e-10, atol=1e-12)
    gaps = np.array([r["laplace"] - r["gauss"] for r in rows])
    print(json.dumps({"rows_checked": len(rows), "gaussian_wins": int((gaps > 0).sum()),
                      "median_paired_gap": float(np.median(gaps)),
                      "elapsed_seconds": time.monotonic() - started}))


if __name__ == "__main__":
    main()
