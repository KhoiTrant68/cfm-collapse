# -*- coding: utf-8 -*-
"""Check the numbers in the paper against the result files they came from.

main.tex opens with the claim "All numbers reproduced from the repo". This enforces
it for the realistic-capacity section and the two EXP-1 controls, which between them
are the parts written directly from JSON summaries rather than from a table the
analysis scripts emit. Each assertion names the file and field it reads, so a stale
number fails loudly instead of surviving a rewrite of the surrounding prose.

Exits non-zero if any check fails, so it can be run before a submission build.

    uv run python scripts/verify_paper_numbers.py
"""
import glob
import json
import pathlib
import re

import numpy as np
import pandas as pd

tex = pathlib.Path("paper/main.tex").read_text(encoding="utf-8")
reev = {f"{float(r['h']):.0f}": r
        for r in json.loads(pathlib.Path("results/exp3/_cifar_ddpm/reeval.json")
                            .read_text(encoding="utf-8"))}
stats = json.loads(pathlib.Path("results/exp3/_cifar_ddpm/stats.json")
                   .read_text(encoding="utf-8"))

ok = fail = 0


def check(label, claimed, actual, tol=5e-3):
    global ok, fail
    good = abs(claimed - actual) <= tol * max(1.0, abs(actual))
    print(f"  {'OK ' if good else 'BAD'} {label:44s} paper={claimed:<12g} file={actual:<12g}")
    ok, fail = ok + good, fail + (not good)


def in_tex(s):
    global ok, fail
    good = s in tex
    print(f"  {'OK ' if good else 'BAD'} present in main.tex: {s[:60]!r}")
    ok, fail = ok + good, fail + (not good)


print("CIFAR/DDPM, per bandwidth")
for h in ("4", "5", "6"):
    f = stats["per_h"][h]
    check(f"h={h} beta", {"4": 0.481, "5": 0.349, "6": -0.156}[h], f["slope"], 1e-3)
    check(f"h={h} R^2", {"4": 0.785, "5": 0.522, "6": 0.135}[h], f["r2"], 1e-3)
    check(f"h={h} decades", {"4": 4.57, "5": 2.16, "6": 0.74}[h], f["decades"], 5e-3)
    check(f"h={h} CV of reference", {"4": 1.102, "5": 0.537, "6": 0.208}[h],
          f["ref_cv"], 5e-3)
    check(f"h={h} median ratio", {"4": 5.30, "5": 1.38, "6": 1.15}[h],
          f["ratio_median"], 5e-3)

print("\nCIFAR/DDPM, other claims")
check("h=0 trace_cov at M=256", 0.458, reev["0"]["trace_cov"], 5e-3)
check("h=0 nn_correct_rate", 1.0, reev["0"]["nn_correct_rate"])
check("h=0 memorization_ratio", 1.0, reev["0"]["memorization_ratio"])
for h, v in (("0", 1.000), ("4", 0.829), ("5", 0.717), ("6", 0.620)):
    check(f"h={h} memorization_ratio", v, reev[h]["memorization_ratio"], 1e-3)
check("Spearman(n_eff, ratio)", -0.858, stats["pooled"]["spearman_neff_ratio"], 1e-3)
check("Spearman(h, ratio)", -0.554, stats["pooled"]["spearman_h_ratio"], 1e-3)
check("pooled n", 144, stats["pooled"]["n"])
check("n_eff h=4", 2.6, reev["4"]["n_eff"], 2e-2)
check("n_eff h=5", 16.4, reev["5"]["n_eff"], 2e-2)
check("n_eff h=6", 74.9, reev["6"]["n_eff"], 2e-2)

print("\nCIFAR/DDPM, training-time trajectory and seeds")
for name, it, col, want in (
        ("h0 iter500 trace_cov", 500, "trace_cov_mean", 179.1),
        ("h0 iter60000 trace_cov", 60000, "trace_cov_mean", 0.431),
        ("h0_seed1 iter60000 trace_cov", 60000, "trace_cov_mean", 0.409),
        ("h4 iter60000 trace_cov", 60000, "trace_cov_mean", 178.5),
        ("h4_seed1 iter60000 trace_cov", 60000, "trace_cov_mean", 240.7),
        ("h4 iter60000 ratio", 60000, "ratio_to_kernel_mean", 6.83),
        ("h4_seed1 iter60000 ratio", 60000, "ratio_to_kernel_mean", 7.07),
        ("h5 iter60000 ratio", 60000, "ratio_to_kernel_mean", 2.315),
        ("h5_seed1 iter60000 ratio", 60000, "ratio_to_kernel_mean", 1.356),
        ("h4 iter60000 n_eff", 60000, "n_eff_mean", 2.36),
        ("h4_seed1 iter60000 n_eff", 60000, "n_eff_mean", 2.77)):
    run = name.split()[0]
    df = pd.read_csv(f"results/exp3/exp3_cifar_ddpm_{run}/raw/metrics.csv")
    row = df[df["iter"] == it].iloc[0]
    check(name, want, float(row[col]), 2e-3)

print("\nSeed reproducibility: the AGGREGATE ratio is what the paper argues from")


def aggregate_ratio(run: str) -> float:
    df = pd.read_csv(f"results/exp3/exp3_cifar_ddpm_{run}/raw/metrics.csv")
    r = df.sort_values("iter").iloc[-1]
    return float(r["trace_cov_mean"]) / float(r["trace_cov_kernel_mean"])


for run, want in (("h4", 2.255), ("h4_seed1", 2.464),
                  ("h5", 1.2449), ("h5_seed1", 1.2482)):
    check(f"{run} aggregate ratio", want, aggregate_ratio(run), 1e-3)

for label, a, b, want in (("h=4 seed spread, aggregate", "h4", "h4_seed1", 9.3),
                          ("h=5 seed spread, aggregate", "h5", "h5_seed1", 0.27)):
    ra, rb = aggregate_ratio(a), aggregate_ratio(b)
    check(label + " (%)", want, abs(rb - ra) / ra * 100, 3e-2)

# The instability the paper now reports about the other estimator.
def mean_of_ratios(run: str) -> float:
    df = pd.read_csv(f"results/exp3/exp3_cifar_ddpm_{run}/raw/metrics.csv")
    return float(df.sort_values("iter").iloc[-1]["ratio_to_kernel_mean"])


check("h=5 mean-of-ratios instability (factor)", 1.7,
      mean_of_ratios("h5") / mean_of_ratios("h5_seed1"), 2e-2)

for run, want in (("h6", 1.181), ("h6_seed1", 0.924)):
    check(f"{run} aggregate ratio", want, aggregate_ratio(run), 1e-3)
check("h=6 seed spread, aggregate (%)", 21.7,
      abs(aggregate_ratio("h6_seed1") - aggregate_ratio("h6"))
      / aggregate_ratio("h6") * 100, 1e-2)

print("\nBeta trajectory (optimisation gap, not a fixed exponent)")
bt = json.loads(pathlib.Path("results/exp3/_cifar_ddpm/beta_trajectory.json")
                .read_text(encoding="utf-8"))
for h, it, want in ((4, 500, -0.031), (4, 8000, -0.045), (4, 20000, 0.119),
                    (4, 60000, 0.390), (5, 60000, 0.223), (6, 60000, -0.202)):
    row = next(r for r in bt if r["h"] == h and r["iter"] == it)
    check(f"beta h={h} at iter {it}", want, row["slope"], 5e-3)

collapse = 179.1 / 0.431
check("h=0 collapse factor 415x", 415, collapse, 3e-3)

print("\nEXP-1 controls (from the analysis summaries)")
p6 = json.loads(pathlib.Path("results/exp1/_p6_exposure/summary.json")
                .read_text(encoding="utf-8"))
check("P6 spread, fixed budget", 20.2, p6["spread_fixed_budget"], 5e-3)
check("P6 spread, fixed exposure", 2.28, p6["spread_fixed_exposure"], 5e-3)
for r in p6["rows"]:
    check(f"P6 N={r['N']} fixed-exposure mean",
          {50: 0.444, 200: 0.774, 1000: 0.928, 5000: 1.014}[r["N"]],
          r["ratio_mean"], 2e-3)

ss = json.loads(pathlib.Path("results/exp1/_seed_split/summary.json")
                .read_text(encoding="utf-8"))
check("seed split, std run", 0.0675, ss["std_run"], 2e-3)
check("seed split, std instance", 0.1261, ss["std_instance"], 2e-3)
check("seed split, quadrature", 0.1431, ss["quadrature"], 2e-3)
check("seed split, instance share", 0.78, ss["instance_share_of_variance"], 6e-3)

print("\nEntropic OT: the numbers, and whether the estimator can resolve them")
# Every OT value in the paper was, until this was caught, produced by a Sinkhorn
# whose log-domain dual mixed two unit conventions. Nothing here checked them,
# which is why it survived. These checks close that hole: the values, and -- for
# the differences the text reads -- whether they clear the estimator's own floor.
res = pd.read_csv("results/exp1/_theory/raw/ot_resolution.csv")
for d, N, want in ((2, 200, 0.0138), (2, 50, 0.0194), (2, 1000, 0.0198),
                   (5, 200, 0.6227), (10, 200, 4.2731)):
    row = res[(res["d"] == d) & (res["N"] == N)].iloc[0]
    check(f"OT sampling floor d={d} N={N}", want, row["ot_floor"], 2e-2)

pop = pd.read_csv("results/exp1/_theory/raw/target_noise_population.csv")


def cell(h, rho, col):
    r = pop[(pop["h"] == h) & (pop["rho"] == rho)]
    return float(r[col].iloc[0])


check("population best MMD (h=0.5, rho=0)", 0.0089, cell(0.5, 0.0, "mmd"), 2e-2)
check("smoothing at the best h hurts MMD", 0.0123, cell(0.5, 0.2, "mmd"), 2e-2)
check("population OT at h=0.5, rho=0", 0.106, cell(0.5, 0.0, "sinkhorn"), 3e-2)
check("smoothing at the best h hurts OT", 0.131, cell(0.5, 0.2, "sinkhorn"), 3e-2)
check("population OT at h=0.1, rho=0", 0.168, cell(0.1, 0.0, "sinkhorn"), 3e-2)
check("population OT at h=0.1, rho=0.1", 0.158, cell(0.1, 0.1, "sinkhorn"), 3e-2)
# The claim the paper actually makes about that pair: the improvement is smaller
# than the floor, so it is not a measurement. Checked as an inequality.
gain = cell(0.1, 0.0, "sinkhorn") - cell(0.1, 0.1, "sinkhorn")
flr = float(res[(res["d"] == 2) & (res["N"] == 200)]["ot_floor"].iloc[0])
print(f"  {'OK ' if gain < flr else 'BAD'} "
      f"{'h=0.1 OT gain is below the estimator floor':44s} "
      f"gain={gain:<12.4g} floor={flr:<12.4g}")
ok, fail = ok + (gain < flr), fail + (gain >= flr)

trn = pd.read_csv("results/exp1/_theory/raw/target_noise_trained.csv").set_index("arm")
b, sm = trn.loc["rho=0.0"], trn.loc["rho=0.3"]
check("trained-model MMD gain from rho", 1.49, b["mmd"] / sm["mmd"], 1e-2)
check("trained-model OT gain from rho", 1.29, b["sinkhorn"] / sm["sinkhorn"], 1e-2)
check("trained-model OT, rho=0", 0.692, b["sinkhorn"], 2e-2)
check("trained-model OT, rho=0.3", 0.537, sm["sinkhorn"], 2e-2)
# The ordering is the corrected claim: MMD gains MORE than OT, where the paper
# previously said the reverse.
mmd_wins = (b["mmd"] / sm["mmd"]) > (b["sinkhorn"] / sm["sinkhorn"])
print(f"  {'OK ' if mmd_wins else 'BAD'} "
      f"{'MMD gain exceeds OT gain (the reversal)':44s} "
      f"mmd={b['mmd'] / sm['mmd']:<12.3g} ot={b['sinkhorn'] / sm['sinkhorn']:<12.3g}")
ok, fail = ok + mmd_wins, fail + (not mmd_wins)

print("\nThe loss form against the measured collapse (Corollary cor:lossform)")
_m = pd.concat([pd.read_csv(f) for f in
                sorted(glob.glob("results/exp1/exp1_cond_seed[0-9]/raw/metrics.csv"))])
_m = _m[_m["group"] == "train"]
_g = _m.groupby("iter")[["train_loss", "trace_cov_mean"]].mean()
_it = _g.index.values
_k = _it >= 1000
_sl = np.polyfit(np.log(_g["train_loss"].values[_k]),
                 np.log(np.sqrt(_g["trace_cov_mean"].values[_k])), 1)[0]
_sl2 = np.polyfit(np.log(_g["train_loss"].values[_it >= 30000]),
                  np.log(np.sqrt(_g["trace_cov_mean"].values[_it >= 30000])), 1)[0]
check("sqrt-loss pacing, slope from iter 1000", 0.429, _sl, 5e-3)
check("sqrt-loss pacing, slope over last three", 0.485, _sl2, 5e-3)

print("\nsanity: strings the new text depends on")
for s in (r"\label{sec:cifarddpm}", r"\label{tab:cifarddpm}",
          r"\label{fig:cifartrack}", r"\label{sec:p6exposure}",
          r"\label{sec:seedsplit}", r"fig_cifar_ddpm_tracking.png"):
    in_tex(s)

print(f"\n{ok} checks passed, {fail} failed")
raise SystemExit(1 if fail else 0)
