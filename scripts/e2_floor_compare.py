"""E2: does the h_eff floor move with weight decay, learning rate or a cosine schedule?

Reads the per-checkpoint h_eff fits of the E2 runs (heff_floor_*) and of the baseline
linear-Gaussian runs (heff_p7y_*), and compares the final-checkpoint h_eff and h_mean by
condition. Prediction (plan, E2): the floor rises with weight decay; a cosine schedule and
a smaller learning rate lower it.

Usage: python scripts/e2_floor_compare.py [--floor results/exp1/_heff/heff_floor.json]
"""
import argparse
import json
import re
from collections import defaultdict

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--floor", default="results/exp1/_heff/heff_floor.json")
ap.add_argument("--base", default="results/exp1/_heff/heff_synthetic.json")
ap.add_argument("--out", default="results/exp1/_heff/e2_floor_compare.json")
args = ap.parse_args()


def final_rows(rows):
    last = {}
    for r in rows:
        if r["run"] not in last or r["iter"] > last[r["run"]]["iter"]:
            last[r["run"]] = r
    return list(last.values())


def diverged(r):
    # a run whose generated samples blew up: non-finite or exploding trace, or no fit
    t, r2 = r.get("trace_measured_mean"), r.get("r2_heff")
    return not (np.isfinite(t) and t < 10 and r2 is not None and np.isfinite(r2))


def condition(run):
    if run.startswith("heff_p7y_"):
        return "base"
    m = re.match(r"heff_floor_(.+?)_h[0-9.]+_seed\d+$", run)
    return m.group(1)


groups, dropped = defaultdict(list), defaultdict(list)
for path in (args.base, args.floor):
    for r in final_rows(json.load(open(path))):
        if r["h"] not in (0.0, 0.05):
            continue
        (dropped if diverged(r) else groups)[(condition(r["run"]), r["h"])].append(r)

order = ["base", "wd0.0001", "wd0.001", "wd0.01", "lr0.0003", "lr0.003", "cos"]
summary = {}
print(f"{'condition':<10} {'h':>5} {'n':>2}  {'iter':>7}  {'h_eff (gm)':>10}  {'range':>17}  {'h_mean (gm)':>11}")
for h in (0.0, 0.05):
    base = None
    for c in order:
        rs = groups.get((c, h), [])
        nd = len(dropped.get((c, h), []))
        if not rs:
            if nd:
                print(f"{c:<10} {h:>5g}  all {nd} runs diverged")
                summary[f"{c}_h{h:g}"] = {"n": 0, "diverged": nd}
            continue
        he = np.array([r["h_eff"] for r in rs])
        hm = np.array([r["h_from_means"] for r in rs])
        gm, gmm = float(np.exp(np.log(he).mean())), float(np.exp(np.log(hm).mean()))
        if c == "base":
            base = np.log(he)
        # Welch-free summary: difference of mean log h_eff from base, with the seed spread
        dlog = None if base is None or c == "base" else float(np.log(he).mean() - base.mean())
        summary[f"{c}_h{h:g}"] = {
            "n": len(rs), "iter": int(max(r["iter"] for r in rs)),
            "h_eff": he.tolist(), "h_eff_gm": gm, "h_mean": hm.tolist(), "h_mean_gm": gmm,
            "dlog_heff_vs_base": dlog, "diverged": nd,
        }
        extra = ("" if dlog is None else f"  x{np.exp(dlog):.2f} vs base") + (f"  ({nd} diverged, dropped)" if nd else "")
        print(f"{c:<10} {h:>5g} {len(rs):>2}  {max(r['iter'] for r in rs):>7}  {gm:>10.4f}  "
              f"[{he.min():.4f},{he.max():.4f}]  {gmm:>11.4f}{extra}")
json.dump(summary, open(args.out, "w"), indent=1)
print("Saved:", args.out)
