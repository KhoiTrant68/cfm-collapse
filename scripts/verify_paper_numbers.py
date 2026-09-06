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
import json
import pathlib
import re

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

print("\nsanity: strings the new text depends on")
for s in (r"\label{sec:cifarddpm}", r"\label{tab:cifarddpm}",
          r"\label{fig:cifartrack}", r"\label{sec:p6exposure}",
          r"\label{sec:seedsplit}", r"fig_cifar_ddpm_tracking.png"):
    in_tex(s)

print(f"\n{ok} checks passed, {fail} failed")
raise SystemExit(1 if fail else 0)
