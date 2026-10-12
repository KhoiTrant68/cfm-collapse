"""Summarise the multi-level image-scale calibration of the twelve CIFAR-10 runs.

scripts/calib_image_levels.py writes, per run and archived checkpoint, rank-based
coverage of 64 held-out test images at ten levels: per hidden pixel, per principal
component of the hidden region (top 8 and 32), and for one joint region per image in
the span of the top k components (k = 8, 32). Each has an exact reference for a
calibrated sampler with the same M. This joins them with h_eff
(results/exp3/_rerun/heff_<run>.json) and asks two questions:

  1. How miscalibrated is the model, and is the joint region worse than the marginals?
  2. Which observable ranks the miscalibration: h_eff, the sample spread (per-pixel SD
     of the draws, which needs no training set), or the iteration?

Miscalibration is the mean absolute gap between measured and reference coverage over
the ten levels (central intervals for pixels and components, the one-sided region for
the joint statistic). Spearman correlations are over checkpoints with h > 0; the
partial correlation removes the rank of log(iteration) from both sides.

Reads:  results/exp3/_rerun/calib_levels_<run>.json, results/exp3/_rerun/heff_<run>.json
Writes: results/exp3/_rerun/calib_levels_summary.json
Usage:  python scripts/summarize_calib_levels.py
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path("results/exp3/_rerun")


def rankdata(v) -> np.ndarray:
    return pd.Series(np.asarray(v, float)).rank().to_numpy()


def spearmanr(x, y) -> tuple[float]:
    return (float(np.corrcoef(rankdata(x), rankdata(y))[0, 1]),)
STATS = ("pixel", "pc8", "pc32", "joint8", "joint32")


def gaps(c: dict, ref_c: np.ndarray, ref_u: np.ndarray) -> dict:
    cov = {"pixel": np.asarray(c["pixel"]["coverage"]),
           "pc8": np.asarray(c["pc_marginal"]["k8"]), "pc32": np.asarray(c["pc_marginal"]["k32"]),
           "joint8": np.asarray(c["joint"]["k8"]["coverage"]),
           "joint32": np.asarray(c["joint"]["k32"]["coverage"])}
    out = {}
    for k, v in cov.items():
        ref = ref_u if k.startswith("joint") else ref_c
        out[f"{k}_err"] = float(np.mean(np.abs(v - ref)))
        out[f"{k}_cov90"] = float(v[8])          # levels[8] = 0.9
    out["ref90_central"], out["ref90_upper"] = float(ref_c[8]), float(ref_u[8])
    return out


def partial_spearman(x, y, z) -> float:
    rx, ry, rz = (rankdata(v) for v in (x, y, z))
    res = [r - np.polyval(np.polyfit(rz, r, 1), rz) for r in (rx, ry)]
    return float(np.corrcoef(*res)[0, 1])


def main() -> None:
    rows = []
    for f in sorted(glob.glob(str(D / "calib_levels_exp3_cifar_heff_h*_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        ref_c, ref_u = np.asarray(d["reference"]["central"]), np.asarray(d["reference"]["upper"])
        hf = D / f"heff_{d['run']}.json"
        heff = ({c["iter"]: c["h_eff"] for c in json.loads(hf.read_text(encoding="utf-8"))["checkpoints"]}
                if hf.exists() else {})
        for c in d["checkpoints"]:
            r = {"run": d["run"], "h": float(d["h"]), "seed": d["seed"], "iter": c["iter"],
                 "h_eff": heff.get(c["iter"]), "pixel_sd": c["pixel_sd"]}
            r.update(gaps(c, ref_c, ref_u))
            rows.append(r)

    out = {"n": len(rows), "runs": len({r["run"] for r in rows}), "rows": rows}
    print(f"{len(rows)} checkpoints in {out['runs']} runs; reference 90%: "
          f"central {rows[0]['ref90_central']:.3f}, joint {rows[0]['ref90_upper']:.3f}")

    # 1. At 60k, by bandwidth
    by_h = {}
    print("\nat 60k, range over three instances (90% coverage; mean |gap| over ten levels)")
    for h in sorted({r["h"] for r in rows}):
        rs = [r for r in rows if r["h"] == h and r["iter"] == 60000]
        e = {}
        for k in STATS:
            cv = [r[f"{k}_cov90"] for r in rs]
            er = [r[f"{k}_err"] for r in rs]
            e[k] = {"cov90": [min(cv), max(cv)], "err": [min(er), max(er)]}
        by_h[str(h)] = e
        print(f"  h={h:g}: " + "  ".join(f"{k} {e[k]['cov90'][0]:.2f}-{e[k]['cov90'][1]:.2f} "
                                          f"({e[k]['err'][0]:.3f}-{e[k]['err'][1]:.3f})" for k in STATS))
    out["at_60k"] = by_h

    # joint worse than marginal: at how many checkpoints is the joint gap larger?
    for k in ("joint8", "joint32"):
        n = sum(r[f"{k}_err"] > r["pixel_err"] for r in rows)
        out[f"{k}_worse_than_pixel"] = n
        print(f"  {k} gap larger than the per-pixel gap at {n}/{len(rows)} checkpoints")

    # 2. which observable ranks miscalibration (h > 0)
    hr = [r for r in rows if r["h"] > 0 and r["h_eff"] is not None]
    li = np.log([r["iter"] for r in hr])
    sp = {}
    print(f"\nSpearman with the miscalibration, {len(hr)} checkpoints at h>0 "
          f"(partial given log iteration in brackets)")
    for k in STATS:
        y = [r[f"{k}_err"] for r in hr]
        s = {}
        for name, x in (("h_eff", [r["h_eff"] for r in hr]),
                        ("h_eff_over_h", [r["h_eff"] / r["h"] for r in hr]),
                        ("pixel_sd", [r["pixel_sd"] for r in hr]), ("log_iter", li)):
            rho = float(spearmanr(x, y)[0])
            pr = partial_spearman(x, y, li) if name != "log_iter" else None
            s[name] = {"spearman": rho, "partial_given_log_iter": pr}
        sp[k] = s
        print(f"  {k:8s} " + "  ".join(
            f"{n} {v['spearman']:+.2f}" + (f" [{v['partial_given_log_iter']:+.2f}]"
                                           if v["partial_given_log_iter"] is not None else "")
            for n, v in s.items()))
    out["spearman_h_pos"] = sp
    (D / "calib_levels_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nSaved: {D / 'calib_levels_summary.json'}")


if __name__ == "__main__":
    main()
