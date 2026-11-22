"""Analysis of E1 (exact field on a window of noise levels) against its pre-registered predictions.

    uv run --no-sync python -m scripts.paperB_window_analysis results/paperB_20261121/window_swap_public

Reads window_per_sample.npz written by scripts/paperB_window_swap.py and writes WINDOW_ANALYSIS.md
and window_analysis.json next to it. Numpy only.

Conventions (as in the run script): the denoiser at an evaluation level s is the exact posterior
mean if lo < s <= hi and the network otherwise; window (lo, inf) is exact->net at lo, window (0, hi)
is net->exact at hi. Off-atom means d1/d2 >= 1/3. "=L" / "=E": the endpoint's nearest training
image (within the class) equals that of the learned / exact endpoint of the same latent.

Pre-registered predictions (docs/plan/paperB_gpu_experiments_2026-11-21.md, E1):
  P1.1  exact->net on the public model: median d1 proportional to lo, k = d1/lo about 27;
        falsified if k is outside [20, 35] or d1 is not monotone in lo.
  P1.2  middle windows (lo, hi] on the public model: the final deviation depends only on lo, not
        on hi, as long as hi >= 0.5; falsified if median d1 changes by more than 20% when hi goes
        from 0.5 to 2 at the same lo.
  P1.3  needs the 500-image model (not run here).

Intervals: Wilson 95% for shares; order-statistic 95% interval for medians; for ratios of medians a
class-stratified bootstrap (B = 4000, paired over latents, seed 20261121).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

RATIO = 1 / 3
Z = 1.959963984540054
OLD_SWAP_PUBLIC = {  # results/paperB_20261121/swap/swap_levels.csv, other latents (n = 500)
    "off": {5.0: 1.000, 2.0: 1.000, 1.0: 0.956, 0.5: 0.492, 0.2: 0.070, 0.1: 0.002, 0.05: 0.0, 0.02: 0.0},
    "d1_median": {5.0: 18.8506, 2.0: 16.1997, 1.0: 9.2075, 0.5: 6.4545, 0.2: 4.2188, 0.1: 2.5687,
                  0.05: 1.3737, 0.02: 0.6065},
    "eqL_n2e": {5.0: 0.306, 2.0: 0.560, 1.0: 0.896, 0.5: 0.956, 0.2: 0.986, 0.1: 0.996, 0.05: 0.998, 0.02: 1.000},
}


def wilson(k, n):
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def median_ci(x, level=0.95):
    """Distribution-free interval for the median from order statistics."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    logp = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2) for i in range(n + 1)]
    pmf = np.exp(logp)
    best = None
    for j in range(n // 2, -1, -1):          # symmetric ranks j and n-1-j (0-based)
        k = n - 1 - j
        cov = pmf[j + 1:k + 1].sum()          # P(j < B <= k) = P(x_(j) <= median < x_(k))
        if cov >= level:
            best = (j, k, float(cov))
            break
    if best is None:                          # n too small for the level: report (min, max) and its coverage
        return float(np.median(x)), float(x[0]), float(x[-1]), float(1 - 2 * 0.5 ** n)
    j, k, cov = best
    return float(np.median(x)), float(x[j]), float(x[k]), cov


def strat_boot(stat, labels, B=4000, seed=20261121):
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(labels == c) for c in np.unique(labels)]
    out = np.empty(B)
    for b in range(B):
        idx = np.concatenate([rng.choice(g, len(g), replace=True) for g in groups])
        out[b] = stat(idx)
    return np.quantile(out, [0.025, 0.975])


def main(d):
    D = Path(d)
    z = np.load(D / "window_per_sample.npz")
    meta = json.loads((D / "window_run.json").read_text(encoding="utf-8")) if (D / "window_run.json").exists() else {}
    lab = z["label"]
    n = len(lab)
    runs = sorted({k.split(":")[0] for k in z.files if ":" in k})
    get = lambda r, k: z[f"{r}:{k}"]
    nnL, nnE = get("learned", "nn"), get("exact", "nn")

    def parse(r):
        if not r.startswith("exact("):
            return None
        lo, hi = r[len("exact("):-1].split(",")
        return float(lo), (math.inf if hi == "inf" else float(hi))

    rows = []
    for r in runs:
        d1, d2 = get(r, "d1"), get(r, "d2")
        off = d1 / d2 >= RATIO
        p, lo_, hi_ = wilson(int(off.sum()), n)
        eqL = get(r, "nn") == nnL
        eqE = get(r, "nn") == nnE
        med, mlo, mhi, cov = median_ci(d1)
        w = parse(r)
        rows.append({"run": r, "lo": None if w is None else w[0], "hi": None if w is None else (None if math.isinf(w[1]) else w[1]),
                     "n": n, "off": p, "off_ci": [lo_, hi_],
                     "eqL": float(eqL.mean()), "eqL_ci": list(wilson(int(eqL.sum()), n)[1:]),
                     "eqE": float(eqE.mean()), "eqE_ci": list(wilson(int(eqE.sum()), n)[1:]),
                     "d1_median": med, "d1_median_ci": [mlo, mhi], "d1_median_ci_coverage": cov,
                     "dist_to_learned_median": float(np.median(get(r, "dist_to_learned")))})
    byname = {r["run"]: r for r in rows}

    # P1.1: exact->net windows (lo, inf)
    e2n = sorted([(parse(r)[0], r) for r in runs if parse(r) and math.isinf(parse(r)[1]) and parse(r)[0] > 0])
    p11 = []
    for lo, r in e2n:
        d1 = get(r, "d1")
        k = float(np.median(d1)) / lo
        ci = strat_boot(lambda idx, d1=d1, lo=lo: np.median(d1[idx]) / lo, lab)
        p11.append({"lo": lo, "run": r, "k": k, "k_ci": ci.tolist(), "in_20_35": bool(20 <= k <= 35),
                    "old_swap_d1_median": OLD_SWAP_PUBLIC["d1_median"].get(lo),
                    "old_swap_off": OLD_SWAP_PUBLIC["off"].get(lo)})
    meds = [byname[r]["d1_median"] for _, r in e2n]
    monotone = bool(all(a < b for a, b in zip(meds, meds[1:])))

    # P1.2: middle windows at fixed lo, compare hi
    p12 = []
    for lo in sorted({parse(r)[0] for r in runs if parse(r) and parse(r)[0] > 0}):
        his = sorted([(parse(r)[1], r) for r in runs if parse(r) and parse(r)[0] == lo])
        base = [r for h, r in his if h == 0.5]
        if not base:
            continue
        b = base[0]
        for h, r in his:
            if r == b:
                continue
            num, den = get(r, "d1"), get(b, "d1")
            ratio = float(np.median(num) / np.median(den))
            ci = strat_boot(lambda idx, num=num, den=den: np.median(num[idx]) / np.median(den[idx]), lab)
            p12.append({"lo": lo, "hi_ref": 0.5, "hi": None if math.isinf(h) else h, "run": r, "ref_run": b,
                        "median_ratio": ratio, "ratio_ci": ci.tolist(),
                        "change_gt_20pct": bool(abs(ratio - 1) > 0.2),
                        "ci_excludes_20pct_band": bool(ci[1] < 0.8 or ci[0] > 1.2)})

    res = {"dir": str(D), "meta": meta, "n": n, "rows": rows,
           "P1.1": {"per_lo": p11, "monotone_in_lo": monotone,
                    "verdict": ("holds for every lo" if all(x["in_20_35"] for x in p11) and monotone else
                                "fails for lo in " + ", ".join(f"{x['lo']:g} (k={x['k']:.1f})" for x in p11 if not x["in_20_35"])
                                + ("" if monotone else "; d1 not monotone in lo"))},
           "P1.2": {"comparisons": p12,
                    "verdict_hi_0.5_to_2": [
                        {"lo": x["lo"], "ratio": x["median_ratio"], "ci": x["ratio_ci"],
                         "falsified": x["change_gt_20pct"], "falsified_beyond_ci": x["ci_excludes_20pct_band"]}
                        for x in p12 if x["hi"] == 2.0]}}
    (D / "window_analysis.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    L = [f"# E1 window swap: analysis ({D.name}, n = {n})", "",
         "| run | off-atom [95%] | =L [95%] | =E [95%] | median d1 [95%] | median dist. to learned |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['run']} | {r['off']:.3f} [{r['off_ci'][0]:.3f}, {r['off_ci'][1]:.3f}] | {r['eqL']:.3f} "
                 f"[{r['eqL_ci'][0]:.3f}, {r['eqL_ci'][1]:.3f}] | {r['eqE']:.3f} [{r['eqE_ci'][0]:.3f}, {r['eqE_ci'][1]:.3f}] | "
                 f"{r['d1_median']:.3f} [{r['d1_median_ci'][0]:.3f}, {r['d1_median_ci'][1]:.3f}] | {r['dist_to_learned_median']:.2f} |")
    L += ["", "## P1.1 (exact->net: median d1 / lo, pre-registered k in [20, 35], monotone in lo)", "",
          "| lo | k = median d1 / lo [95% boot] | in [20,35] | old swap median d1 (other latents) | old swap off-atom |", "|---|---|---|---|---|"]
    for x in p11:
        L.append(f"| {x['lo']:g} | {x['k']:.1f} [{x['k_ci'][0]:.1f}, {x['k_ci'][1]:.1f}] | {x['in_20_35']} | "
                 f"{x['old_swap_d1_median']} | {x['old_swap_off']} |")
    L += ["", f"monotone in lo: {monotone}. Verdict: {res['P1.1']['verdict']}.", "",
          "## P1.2 (middle windows: median d1 relative to the window (lo, 0.5]; falsified if the change from hi = 0.5 to hi = 2 exceeds 20%)", "",
          "| lo | hi | ratio of median d1 to (lo, 0.5] [95% boot] | change > 20% | CI outside [0.8, 1.2] |", "|---|---|---|---|---|"]
    for x in p12:
        hs = "inf" if x["hi"] is None else format(x["hi"], "g")
        L.append(f"| {x['lo']:g} | {hs} | {x['median_ratio']:.3f} "
                 f"[{x['ratio_ci'][0]:.3f}, {x['ratio_ci'][1]:.3f}] | {x['change_gt_20pct']} | {x['ci_excludes_20pct_band']} |")
    (D / "WINDOW_ANALYSIS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/paperB_20261121/window_swap_public")
