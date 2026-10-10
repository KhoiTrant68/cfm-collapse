"""Rebuild the CIFAR-10 three-instance table at the protocol the paper states.

Table tab:seed3 was built from the in-training evaluator (8 conditions, M=16), while
Section 4.2 states 48 conditions at M=256. The re-runs (configs/exp3_cifar_ddpm_heff.yaml,
scripts/server_cifar_queue.sh) re-evaluate every 60k checkpoint at 48 conditions and
M=256. This joins those re-evaluations into the table, shows how far the training-log
estimate of the same run is from it, and summarises h_eff over training for every
bandwidth, including h=0 and h=6, which the published h_eff runs did not cover.

Reads:  results/exp3/_rerun/reeval_<run>/reeval.json, results/exp3/_rerun/heff_<run>.json,
        results/exp3/<run>/raw/metrics.csv
Writes: results/exp3/_rerun/seed_table.json (and prints the table)
Usage:  python scripts/analyze_cifar_reruns.py [--dir results/exp3/_rerun]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

HS = (0, 4, 5, 6)
SEEDS = (0, 1, 2)


def spread(v) -> float:
    v = np.asarray(v, float)
    return float((v.max() - v.min()) / v.mean() * 100) if len(v) > 1 else float("nan")


def overlap(a, b) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/exp3/_rerun")
    d = Path(ap.parse_args().dir)
    table, heff = {}, {}
    for h in HS:
        rows = []
        for s in SEEDS:
            run = f"exp3_cifar_heff_h{h}_s{s}"
            rf = d / f"reeval_{run}" / "reeval.json"
            if not rf.exists():
                continue
            r = json.loads(rf.read_text(encoding="utf-8"))[0]
            tc = np.asarray(r["trace_cov"] if isinstance(r["trace_cov"], list)
                            else [r["trace_cov"]], float)
            tk = np.asarray(r["trace_cov_kernel"] if isinstance(r["trace_cov_kernel"], list)
                            else [r["trace_cov_kernel"]], float)
            row = {"seed": s, "iter": r["iter"], "M": r["M"], "n_conditions": r["n_conditions"],
                   "trace": float(tc.mean()),
                   "aggregate": float(tc.mean() / tk.mean()) if h > 0 else None,
                   "mean_of_ratios": r.get("ratio_mean"), "median_ratio": r.get("ratio_median"),
                   "median_ci": [r.get("ratio_ci_lo"), r.get("ratio_ci_hi")],
                   "n_eff": r.get("n_eff"), "on_atom": r.get("memorization_ratio"),
                   "nn_correct": r.get("nn_correct_rate")}
            log = Path("results/exp3") / run / "raw" / "metrics.csv"
            if log.exists():
                last = pd.read_csv(log).sort_values("iter").iloc[-1]
                row["log_trace"] = float(last["trace_cov_mean"])
                if h > 0:
                    row["log_aggregate"] = float(last["trace_cov_mean"] / last["trace_cov_kernel_mean"])
                    row["log_vs_reeval_pct"] = 100 * (row["log_aggregate"] / row["aggregate"] - 1)
            rows.append(row)
        if rows:
            table[h] = {"rows": rows,
                        "spread_raw_pct": spread([x["trace"] for x in rows]),
                        "spread_aggregate_pct": spread([x["aggregate"] for x in rows]) if h > 0 else None,
                        "spread_mean_of_ratios_pct": spread([x["mean_of_ratios"] for x in rows])
                        if h > 0 and all(x["mean_of_ratios"] is not None for x in rows) else None}
        # h_eff over training
        traj = []
        for s in SEEDS:
            hf = d / f"heff_exp3_cifar_heff_h{h}_s{s}.json"
            if not hf.exists():
                continue
            c = json.loads(hf.read_text(encoding="utf-8"))
            ck = sorted(c["checkpoints"], key=lambda x: x["iter"])
            traj.append({"seed": s, "iters": [x["iter"] for x in ck],
                         "h_eff": [x["h_eff"] for x in ck],
                         "agree_from_5k": sum(overlap(x["h_eff_ci"], x["h_means_ci"])
                                              for x in ck if x["iter"] >= 5000),
                         "n_from_5k": sum(x["iter"] >= 5000 for x in ck),
                         "beta": [x.get("beta") for x in ck],
                         "monotone": bool(np.all(np.diff([x["h_eff"] for x in ck]) <= 0))})
        if traj:
            heff[h] = traj

    out = {"table": table, "heff": heff}
    (d / "seed_table.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    print("Three instances at 60k, re-evaluated at 48 conditions, M=256")
    print(f"{'h':>2} {'seed':>4} {'tr Cov':>8} {'aggregate':>9} {'mean/ratio':>10} "
          f"{'median [95% CI]':>22} {'n_eff':>6} {'on-atom':>7} | {'log agg':>7} {'log-reeval':>10}")
    for h, t in table.items():
        for x in t["rows"]:
            agg = f"{x['aggregate']:.3f}" if x["aggregate"] is not None else "--"
            mor = f"{x['mean_of_ratios']:.2f}" if x.get("mean_of_ratios") is not None else "--"
            med = (f"{x['median_ratio']:.2f} [{x['median_ci'][0]:.2f}, {x['median_ci'][1]:.2f}]"
                   if x.get("median_ratio") is not None else "--")
            la = f"{x['log_aggregate']:.3f}" if x.get("log_aggregate") is not None else "--"
            gap = f"{x['log_vs_reeval_pct']:+.1f}%" if x.get("log_vs_reeval_pct") is not None else "--"
            print(f"{h:>2} {x['seed']:>4} {x['trace']:>8.3f} {agg:>9} {mor:>10} {med:>22} "
                  f"{(x['n_eff'] or float('nan')):>6.1f} {(x['on_atom'] or float('nan')):>7.3f} | {la:>7} {gap:>10}")
        sa = t["spread_aggregate_pct"]
        print(f"   spread raw {t['spread_raw_pct']:.1f}%"
              + (f", aggregate {sa:.1f}%" if sa is not None else "")
              + (f", mean-of-ratios {t['spread_mean_of_ratios_pct']:.0f}%"
                 if t.get("spread_mean_of_ratios_pct") is not None else ""))
    print("\nh_eff over training (h_eff / h at the last checkpoint; agreement from 5k on)")
    for h, tr in heff.items():
        for x in tr:
            end = x["h_eff"][-1]
            rel = f"{end / h:.2f}h" if h > 0 else f"{end:.3f}"
            print(f"  h={h} seed {x['seed']}: h_eff {[round(v, 2) for v in x['h_eff']]} -> {rel}; "
                  f"agree {x['agree_from_5k']}/{x['n_from_5k']}; monotone {x['monotone']}")
    print(f"\nSaved: {d / 'seed_table.json'}")


if __name__ == "__main__":
    main()
