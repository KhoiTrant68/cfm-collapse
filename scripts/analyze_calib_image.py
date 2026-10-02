"""Join image-scale calibration (calib_<run>.json) with h_eff (heff_<run>.json).

For every checkpoint present in both files: h_eff, the posterior-free PIT error, the
90% pixel-interval coverage, the extraction rate and the per-pixel sd. Reports, pooled
over runs, the Spearman correlation of each predictor (h_eff, h_eff/h, pixel sd,
log iteration) with coverage and PIT error, and the correlation of h_eff with coverage
after partialling out log(iteration) -- the same tests as the synthetic audit
(audit_calibration_v2), now without a known posterior.

Reads:  <dir>/heff_<run>.json, <dir>/calib_<run>.json (from kaggle_heff.sh ANALYSIS=calib)
Writes: <dir>/calib_image_summary.json
Usage:  uv run --with scipy python scripts/analyze_calib_image.py --dir results/exp3/_heff
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr


def partial_spearman(a, b, c):
    ra, rb, rc = (rankdata(v) for v in (a, b, c))
    res = lambda r: r - np.polyval(np.polyfit(rc, r, 1), rc)
    return float(np.corrcoef(res(ra), res(rb))[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/exp3/_heff")
    args = ap.parse_args()
    d = Path(args.dir)
    rows = []
    for cf in sorted(d.glob("calib_*.json")):
        run = cf.stem[len("calib_"):]
        hf = d / f"heff_{run}.json"
        if not hf.exists():
            print(f"skip {run}: no {hf.name}")
            continue
        cal = json.loads(cf.read_text(encoding="utf-8"))
        he = {c["iter"]: c for c in json.loads(hf.read_text(encoding="utf-8"))["checkpoints"]}
        for c in cal["checkpoints"]:
            if c["iter"] in he and not he[c["iter"]].get("h_eff_at_edge"):
                rows.append({"run": run, "h": cal["h"], "iter": c["iter"],
                             "h_eff": he[c["iter"]]["h_eff"], **{k: c[k] for k in
                             ("pit_error", "coverage_90", "extraction", "pixel_sd")}})
    if len(rows) < 6:
        raise SystemExit(f"only {len(rows)} joined checkpoints; run ANALYSIS=calib first")
    col = lambda k: np.array([r[k] for r in rows], float)
    li = np.log(col("iter"))
    preds = {"h_eff": col("h_eff"), "h_eff_over_h": col("h_eff") / col("h"),
             "pixel_sd": col("pixel_sd"), "log_iter": li}
    out = {"n": len(rows), "rows": rows, "spearman": {}, "partial_given_log_iter": {}}
    for target in ("coverage_90", "pit_error", "extraction"):
        y = col(target)
        out["spearman"][target] = {k: float(spearmanr(v, y)[0]) for k, v in preds.items()}
        out["partial_given_log_iter"][target] = {
            k: partial_spearman(v, y, li) for k, v in preds.items() if k != "log_iter"}
    (d / "calib_image_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{len(rows)} checkpoints")
    for t in out["spearman"]:
        print(t, {k: round(v, 2) for k, v in out["spearman"][t].items()},
              "| given iter:", {k: round(v, 2) for k, v in out["partial_given_log_iter"][t].items()})


if __name__ == "__main__":
    main()
