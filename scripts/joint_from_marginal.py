"""Does marginal under-dispersion explain the joint under-coverage at image scale?

At CIFAR-10 scale (scripts/summarize_calib_levels.py) per-component 90% coverage is
0.77-0.87 while the joint region in the top k principal components covers 0.47-0.78.
The simplest account: the sampler is under-dispersed by a common factor s in every
direction. Then a modest per-direction shortfall compounds in a k-dimensional region.

Model: the truth z ~ N(0, I_k) and the M = 64 draws ~ N(0, s^2 I_k), independent. For
each s on a grid this simulates exactly the rank statistics of src/metrics/calibration.py
(the marginal central-interval rank per coordinate, and the leave-one-out Mahalanobis
rank for the joint region) and tabulates their coverage at the ten levels. For every
checkpoint it then
  1. fits s to the measured marginal coverage of the top k components (pc_marginal, ten
     levels, least squares on the grid), separately for k = 8 and k = 32, and
  2. predicts the joint coverage curve at that s, with nothing else fitted,
and compares the prediction with the measured joint coverage.

Reads:  results/exp3/_rerun/calib_levels_exp3_cifar_heff_h*_s*.json
Writes: results/exp3/_rerun/joint_from_marginal.json
Usage:  python scripts/joint_from_marginal.py [--trials 1500]
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

from src.metrics.calibration import LEVELS, central_coverage, joint_pit, upper_coverage

M = 64
S_GRID = np.round(np.arange(0.30, 1.501, 0.025), 4)


def tables(k: int, trials: int, rng) -> tuple[np.ndarray, np.ndarray]:
    """Marginal (central) and joint (upper) coverage at LEVELS, for each s in S_GRID."""
    marg, joint = [], []
    for s in S_GRID:
        z = rng.standard_normal((trials, k))
        draws = s * rng.standard_normal((trials, M, k))
        below = (draws < z[:, None, :]).sum(1)                     # (trials, k)
        u_marg = (below + 0.5) / (M + 1)
        marg.append(central_coverage(u_marg.ravel(), LEVELS))
        u_joint = np.array([joint_pit(draws[t], z[t]) for t in range(trials)])
        joint.append(upper_coverage(u_joint, LEVELS))
    return np.array(marg), np.array(joint)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    tab = {k: tables(k, args.trials, rng) for k in (8, 32)}
    s1 = int(np.argmin(np.abs(S_GRID - 1.0)))
    for k in (8, 32):
        print(f"k={k}: at s=1 the model's 90% marginal {tab[k][0][s1][8]:.3f}, joint {tab[k][1][s1][8]:.3f}"
              f" (calibrated reference 0.908)")

    rows = []
    for f in sorted(glob.glob("results/exp3/_rerun/calib_levels_exp3_cifar_heff_h*_s*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if float(d["h"]) == 0:
            continue
        for c in d["checkpoints"]:
            r = {"run": d["run"], "h": float(d["h"]), "iter": c["iter"]}
            for k in (8, 32):
                mk = np.asarray(c["pc_marginal"][f"k{k}"])
                jm = np.asarray(c["joint"][f"k{k}"]["coverage"])
                marg_t, joint_t = tab[k]
                i = int(np.argmin(((marg_t - mk) ** 2).sum(1)))
                r[f"s{k}"] = float(S_GRID[i])
                r[f"s{k}_at_edge"] = i in (0, len(S_GRID) - 1)
                r[f"joint{k}_pred"] = joint_t[i].tolist()
                r[f"joint{k}_meas"] = jm.tolist()
                r[f"marg{k}_fit_rmse"] = float(np.sqrt(np.mean((marg_t[i] - mk) ** 2)))
            rows.append(r)

    out = {"M": M, "trials": args.trials, "s_grid": S_GRID.tolist(), "n": len(rows), "by_k": {}}
    for k in (8, 32):
        P = np.array([r[f"joint{k}_pred"] for r in rows])
        Y = np.array([r[f"joint{k}_meas"] for r in rows])
        p90, y90 = P[:, 8], Y[:, 8]
        r2_all = 1 - ((Y - P) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
        r2_90 = 1 - ((y90 - p90) ** 2).sum() / ((y90 - y90.mean()) ** 2).sum()
        corr90 = float(np.corrcoef(p90, y90)[0, 1])
        s = np.array([r[f"s{k}"] for r in rows])
        out["by_k"][str(k)] = {
            "r2_all_levels": float(r2_all), "r2_90": float(r2_90), "corr_90": corr90,
            "mae_90": float(np.abs(p90 - y90).mean()), "bias_90": float((p90 - y90).mean()),
            "s_range": [float(s.min()), float(s.max())], "s_median": float(np.median(s)),
            "marg_fit_rmse_median": float(np.median([r[f"marg{k}_fit_rmse"] for r in rows])),
            "pred90_range": [float(p90.min()), float(p90.max())],
            "meas90_range": [float(y90.min()), float(y90.max())],
            "at_edge": int(sum(r[f"s{k}_at_edge"] for r in rows))}
        b = out["by_k"][str(k)]
        print(f"k={k}: s in [{b['s_range'][0]:.3f}, {b['s_range'][1]:.3f}] (median {b['s_median']:.3f}), "
              f"marginal fit rmse {b['marg_fit_rmse_median']:.3f}; joint 90%: predicted "
              f"{b['pred90_range'][0]:.2f}-{b['pred90_range'][1]:.2f}, measured "
              f"{b['meas90_range'][0]:.2f}-{b['meas90_range'][1]:.2f}; R^2 {r2_90:.2f} at 90%, "
              f"{r2_all:.2f} over all levels; corr {corr90:.2f}; MAE {b['mae_90']:.3f}, "
              f"bias {b['bias_90']:+.3f}; s at grid edge {b['at_edge']}")
    # 60k only
    for k in (8, 32):
        r60 = [r for r in rows if r["iter"] == 60000]
        p = [r[f"joint{k}_pred"][8] for r in r60]
        y = [r[f"joint{k}_meas"][8] for r in r60]
        out["by_k"][str(k)]["at_60k"] = {"pred90": [min(p), max(p)], "meas90": [min(y), max(y)],
                                          "s": [min(r[f"s{k}"] for r in r60), max(r[f"s{k}"] for r in r60)]}
        print(f"  60k, k={k}: s {out['by_k'][str(k)]['at_60k']['s']}, predicted {min(p):.2f}-{max(p):.2f}, "
              f"measured {min(y):.2f}-{max(y):.2f}")
    # Per-component scales: s_j from component j's own 90% coverage, then the joint
    # coverage of N(0, diag(s_j^2)) draws against an N(0, I) truth.
    fine = np.round(np.arange(0.20, 1.801, 0.01), 4)
    big = rng.standard_normal((20000, 1))
    m90 = []
    for s in fine:
        draws = s * rng.standard_normal((20000, M))
        u = ((draws < big).sum(1) + 0.5) / (M + 1)
        m90.append(central_coverage(u, LEVELS)[8])
    m90 = np.array(m90)                                   # increasing in s

    def s_of_cov90(c):
        return float(np.interp(c, m90, fine))

    files = {json.loads(Path(f).read_text(encoding="utf-8"))["run"]: f
             for f in glob.glob("results/exp3/_rerun/calib_levels_exp3_cifar_heff_h*_s*.json")}
    for r in rows:
        d = json.loads(Path(files[r["run"]]).read_text(encoding="utf-8"))
        c = next(c for c in d["checkpoints"] if c["iter"] == r["iter"])
        sj = np.array([s_of_cov90(v) for v in c["pc_cov90_by_component"]])
        r["s_by_component"] = sj.tolist()
        for k in (8, 32):
            z = rng.standard_normal((args.trials, k))
            draws = rng.standard_normal((args.trials, M, k)) * sj[:k]
            u = np.array([joint_pit(draws[t], z[t]) for t in range(args.trials)])
            r[f"joint{k}_pred_percomp"] = upper_coverage(u, LEVELS).tolist()
    for k in (8, 32):
        P = np.array([r[f"joint{k}_pred_percomp"] for r in rows])
        Y = np.array([r[f"joint{k}_meas"] for r in rows])
        p90, y90 = P[:, 8], Y[:, 8]
        b = {"r2_all_levels": float(1 - ((Y - P) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()),
             "r2_90": float(1 - ((y90 - p90) ** 2).sum() / ((y90 - y90.mean()) ** 2).sum()),
             "corr_90": float(np.corrcoef(p90, y90)[0, 1]),
             "mae_90": float(np.abs(p90 - y90).mean()), "bias_90": float((p90 - y90).mean())}
        r60 = [r for r in rows if r["iter"] == 60000]
        b["at_60k_pred90"] = [min(r[f"joint{k}_pred_percomp"][8] for r in r60),
                              max(r[f"joint{k}_pred_percomp"][8] for r in r60)]
        out["by_k"][str(k)]["per_component"] = b
        print(f"per-component s_j, k={k}: R^2 {b['r2_90']:.2f} at 90%, {b['r2_all_levels']:.2f} over all "
              f"levels; corr {b['corr_90']:.2f}; MAE {b['mae_90']:.3f}, bias {b['bias_90']:+.3f}; "
              f"60k predicted {b['at_60k_pred90'][0]:.2f}-{b['at_60k_pred90'][1]:.2f}")
    sj_all = np.array([r["s_by_component"] for r in rows if r["iter"] == 60000])
    out["s_by_component_60k_median"] = np.median(sj_all, 0).tolist()
    print("median s_j at 60k, components 1-8:", np.round(np.median(sj_all, 0)[:8], 2),
          " 25-32:", np.round(np.median(sj_all, 0)[24:], 2))

    out["rows"] = rows
    path = Path("results/exp3/_rerun/joint_from_marginal.json")
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("Saved:", path)


if __name__ == "__main__":
    main()
