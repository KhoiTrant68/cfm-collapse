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

print("\nCIFAR/DDPM, training-time trajectory of the displayed instance")
for name, it, col, want in (
        ("h0 iter500 trace_cov", 500, "trace_cov_mean", 179.1),
        ("h0 iter60000 trace_cov", 60000, "trace_cov_mean", 0.431)):
    run = name.split()[0]
    df = pd.read_csv(f"results/exp3/exp3_cifar_ddpm_{run}/raw/metrics.csv")
    row = df[df["iter"] == it].iloc[0]
    check(name, want, float(row[col]), 2e-3)

# Table tab:seed3, rebuilt from the twelve re-trained runs re-measured at 48 conditions
# and M=256 (scripts/analyze_cifar_reruns.py -> results/exp3/_rerun/seed_table.json).
# The direction of the comparison (aggregate ratio against raw trace) is checked as well
# as the values, because that is the claim the table supports.
print("\nSeed reproducibility (Table tab:seed3, re-measured at 48 conditions, M=256)")
_st = json.loads(pathlib.Path("results/exp3/_rerun/seed_table.json").read_text(encoding="utf-8"))
_tab = {int(h): t for h, t in _st["table"].items()}
_rows = {h: sorted(t["rows"], key=lambda r: r["seed"]) for h, t in _tab.items()}
for h, traces, aggs in ((0, (0.411, 0.503, 0.444), None),
                        (4, (187.2, 207.1, 158.4), (2.261, 2.440, 2.490)),
                        (5, (297.6, 290.0, 288.1), (1.396, 1.260, 1.494)),
                        (6, (408.3, 315.9, 383.2), (1.177, 0.904, 1.127))):
    for s, want in enumerate(traces):
        check(f"h={h} seed {s} tr Cov", want, _rows[h][s]["trace"], 2e-3)
    for s, want in enumerate(aggs or ()):
        check(f"h={h} seed {s} aggregate ratio", want, _rows[h][s]["aggregate"], 1e-3)
for h, lo, hi in ((4, 1.8, 3.8), (5, 10.7, 24.0), (6, 58, 91)):
    ne = [r["n_eff"] for r in _rows[h]]
    check(f"h={h} n_eff min", lo, min(ne), 3e-2)
    check(f"h={h} n_eff max", hi, max(ne), 3e-2)
for s, want in enumerate((2.6, 3.8, 1.8)):
    check(f"h=4 seed {s} n_eff (text)", want, _rows[4][s]["n_eff"], 3e-2)
check("h=0 3-seed spread, raw (%)", 20.3, _tab[0]["spread_raw_pct"], 3e-3)
for h, want_raw, want_agg, want_mor in ((4, 26.5, 9.6, 274.0),
                                        (5, 3.3, 16.9, 48.0),
                                        (6, 25.0, 25.5, 27.0)):
    check(f"h={h} 3-seed spread, raw (%)", want_raw, _tab[h]["spread_raw_pct"], 2e-2)
    check(f"h={h} 3-seed spread, aggregate (%)", want_agg, _tab[h]["spread_aggregate_pct"], 2e-2)
    check(f"h={h} 3-seed spread, mean-of-ratios (%)", want_mor,
          _tab[h]["spread_mean_of_ratios_pct"], 2e-2)
want = {4: True, 5: False, 6: False}
for h in (4, 5, 6):
    got = _tab[h]["spread_aggregate_pct"] < _tab[h]["spread_raw_pct"]
    good = got == want[h]
    print(f"  {'OK ' if good else 'BAD'} "
          f"{f'h={h}: aggregate more stable than raw?':44s} "
          f"paper={str(want[h]):<12} file={str(got):<12}")
    ok, fail = ok + good, fail + (not good)
for h, vals in ((4, (40.7, 2364, 142.9)), (5, (2.86, 4.37, 4.78))):
    for s, want_v in enumerate(vals):
        check(f"h={h} seed {s} mean-of-ratios", want_v, _rows[h][s]["mean_of_ratios"], 2e-3)
_ref5 = [r["trace"] / r["aggregate"] for r in _rows[5]]
check("h=5 reference min (193)", 193, min(_ref5), 3e-3)
check("h=5 reference max (230)", 230, max(_ref5), 3e-3)
check("h=5 reference spread (18%)", 18, (max(_ref5) - min(_ref5)) / np.mean(_ref5) * 100, 3e-2)
check("h=5 raw traces min (288)", 288, min(r["trace"] for r in _rows[5]), 3e-3)
check("h=5 raw traces max (298)", 298, max(r["trace"] for r in _rows[5]), 3e-3)
_dev6 = sorted(abs(r["aggregate"] - 1) * 100 for r in _rows[6])
check("h=6 largest deviation from 1 (18%)", 18, _dev6[-1], 3e-2)
check("h=6 smallest deviation from 1 (10%)", 10, _dev6[0], 5e-2)
_gap = [r["log_vs_reeval_pct"] for h in (4, 5, 6) for r in _rows[h]]
check("training-time vs re-measured, min (%)", -15, min(_gap), 3e-2)
check("training-time vs re-measured, max (%)", 13, max(_gap), 3e-2)
check("training-time vs re-measured, median |.| (%)", 9.7, float(np.median(np.abs(_gap))), 1e-2)
_g0 = [100 * (r["log_trace"] / r["trace"] - 1) for r in _rows[0]]
check("h=0 training-time vs re-measured, max (%)", -5, max(_g0), 1e-1)
check("h=0 training-time vs re-measured, min (%)", -10, min(_g0), 3e-2)
for s in range(3):
    check(f"h=0 seed {s} correct image at 48/48", 1.0, _rows[0][s]["nn_correct"])

print("\nh_eff at the two ends, h=0 and h=6 (App. app:heffends)")
_he = {int(h): v for h, v in _st["heff"].items()}
check("h=0 agreement from 5k", 0, sum(x["agree_from_5k"] for x in _he[0]))
check("h=0 checkpoints from 5k", 18, sum(x["n_from_5k"] for x in _he[0]))
check("h=0 runs monotone", 3, sum(x["monotone"] for x in _he[0]))
check("h=0 final h_eff min", 3.44, min(x["h_eff"][-1] for x in _he[0]), 2e-3)
check("h=0 final h_eff max", 3.74, max(x["h_eff"][-1] for x in _he[0]), 2e-3)
check("h=6 agreement from 5k", 8, sum(x["agree_from_5k"] for x in _he[6]))
check("h=6 checkpoints from 5k", 18, sum(x["n_from_5k"] for x in _he[6]))
check("h=6 final h_eff/h min", 1.05, min(x["h_eff"][-1] for x in _he[6]) / 6, 5e-3)
check("h=6 final h_eff/h max", 1.14, max(x["h_eff"][-1] for x in _he[6]) / 6, 5e-3)
_hm0 = [c["h_means"] for f in sorted(glob.glob("results/exp3/_rerun/heff_exp3_cifar_heff_h0_s*.json"))
        for c in json.loads(pathlib.Path(f).read_text(encoding="utf-8"))["checkpoints"]
        if c["iter"] >= 5000]
check("h=0 h_mean max from 5k (at or below 2.8)", 2.8, max(_hm0), 2e-2)
in_tex(r"the two agree at 8/18;")
in_tex(r"$3.44$--$3.74$ at 60k")

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

print("\nThe atomicity floor over i.i.d. atoms (the paper no longer cites Zador for it)")
# Zador is about the optimal N-point quantiser; the floor is over the atoms the
# training set drew. The paper now reports measured exponents for the latter, so
# they belong here.
af = pd.read_csv("results/exp1/_theory/raw/atom_floor_scaling.csv")
for d, want in ((3, -0.612), (5, -0.379), (8, -0.249)):
    g = af[(af["d"] == d) & (af["N"] >= 200)]
    sl = np.polyfit(np.log(g["N"]), np.log(g["floor"]), 1)[0]
    check(f"i.i.d. floor slope, d={d}", want, sl, 5e-3)
g2 = af[(af["d"] == 2) & (af["N"] >= 200)]
r_log = (g2["floor"] * g2["N"] / np.log(g2["N"])).values
r_pow = (g2["floor"] * g2["N"]).values
check("d=2 log-model drift", 1.05, r_log.max() / r_log.min(), 1e-2)
check("d=2 power-model drift", 1.52, r_pow.max() / r_pow.min(), 1e-2)
_logwins = (r_log.max() / r_log.min()) < (r_pow.max() / r_pow.min())
print(f"  {'OK ' if _logwins else 'BAD'} "
      f"{'d=2 i.i.d. floor is log(N)/N, not 1/N':44s} "
      f"log drift={r_log.max() / r_log.min():<12.3g} "
      f"pow drift={r_pow.max() / r_pow.min():<12.3g}")
ok, fail = ok + _logwins, fail + (not _logwins)

print("\nProposition prop:survival(c): the bound is attained, so a>1 really diverges")
# The proposition used to infer divergence from a diverging upper bound. It now
# exhibits an error attaining the bound; that closed form is what makes the claim
# a claim, so it is checked here as well as in verify_error_survival.py.


def _e_closed(eps, a, c=1.0):
    if abs(a) < 1e-12:
        return -c * eps * np.log(eps)
    return c * (eps ** (1.0 - a) - eps) / a


check("a=1 retains exactly c at 1-t=1e-8", 1.0, _e_closed(1e-8, 1.0), 1e-6)
check("a=0.5 has vanished by 1-t=1e-8", 0.0002, _e_closed(1e-8, 0.5), 1e-3)
_div = _e_closed(1e-16, 1.3) > 1e4 and _e_closed(1e-8, 1.3) > 1e2
print(f"  {'OK ' if _div else 'BAD'} "
      f"{'a=1.3 diverges as the truncation tightens':44s} "
      f"1e-8={_e_closed(1e-8, 1.3):<12.4g} 1e-16={_e_closed(1e-16, 1.3):<12.4g}")
ok, fail = ok + _div, fail + (not _div)

print("\nProposition prop:survival(d): the fourth case of the converse is occupied")
# The converse claims four cases and calls them exhaustive. Exhaustiveness is free
# (e_t = (1-t)I(t) is an identity), but "bounded at the critical scale, yet with no
# limit" would be an empty case if nothing realised it. The rotating error
# Delta(t) = c (1-t)^{-1} exp(i log(1/(1-t))) does: e_t = c e^{i theta}/(1+i) + O(1-t).


def _e_rot(eps, c=1.0):
    th = np.log(1.0 / eps)
    return c * (np.exp(1j * th) - np.exp(-th)) / (1.0 + 1j)


check("rotating error holds |e_t| at c/sqrt2", 0.7071,
      abs(_e_rot(1e-5)), 1e-3)
_args = [np.angle(_e_rot(e)) for e in (1e-2, 1e-3, 1e-4, 1e-5)]
_mags = [abs(_e_rot(e)) for e in (1e-2, 1e-3, 1e-4, 1e-5)]
# bounded away from 0 and from a single value: magnitude flat, argument not settling
_nolimit = (max(_mags) - min(_mags) < 2e-3) and (max(_args) - min(_args) > 1.0)
print(f"  {'OK ' if _nolimit else 'BAD'} "
      f"{'critical magnitude, no endpoint (case 4)':44s} "
      f"|e| spread={max(_mags) - min(_mags):<10.3g} "
      f"arg spread={max(_args) - min(_args):<10.3g}")
ok, fail = ok + _nolimit, fail + (not _nolimit)

print("\nWhich reference family (Table tab:families, scripts/heff_family_test.py)")
# Interval agreement is what the paper used to call an out-of-sample check; it does
# not separate the families, so the table carries the fit-quality columns as well.
fam = json.loads(pathlib.Path("results/exp1/_heff/heff_families.json")
                 .read_text(encoding="utf-8"))
f48 = fam["summary"]["h<=0.1, iter>=1e4 (the paper's 48)"]
for f, agree, r2med in (("gauss", 48, 0.86), ("laplace", 45, 0.82), ("cauchy", 43, 0.65),
                        ("knn", 48, 0.36), ("posterior", 42, -0.12)):
    check(f"{f}: intervals agree (of 48)", agree, f48[f]["overlap"])
    check(f"{f}: median log-space R^2", r2med, f48[f]["median_r2_var"], 1e-2)
for f, best, bestm in (("gauss", 36, 41), ("laplace", 9, 5), ("cauchy", 3, 1),
                       ("knn", 0, 1)):
    check(f"{f}: best variance fit (of 48)", best, f48["best_variance_fit_counts"][f])
    check(f"{f}: best mean prediction (of 48)", bestm, f48["best_cross_prediction_counts"][f])
check("posterior optimum at grid edge (of 48)", 37, f48["posterior"]["at_edge"])
_rows = [r for r in fam["rows"] if r["h"] <= 0.1 and r["iter"] >= 10000]
_d = np.array([r["laplace"]["rmse_log"] - r["gauss"]["rmse_log"] for r in _rows])
check("gauss beats laplace (checkpoints of 48)", 36, int((_d > 0).sum()))
check("gauss vs laplace median log-RMSE gap", 0.020, float(np.median(_d)), 5e-2)
_runs = sorted({r["run"] for r in _rows})
_rd = [np.mean([r["laplace"]["rmse_log"] - r["gauss"]["rmse_log"]
                for r in _rows if r["run"] == u]) for u in _runs]
check("gauss beats laplace (runs of 12)", 9, sum(x > 0 for x in _rd))
_pl = fam["summary"]["paired_vs_gauss_48"]["laplace"]
check("gauss vs laplace gap, 95% CI low", 0.011, _pl["median_gap_ci95"][0], 5e-2)
check("gauss vs laplace gap, 95% CI high", 0.024, _pl["median_gap_ci95"][1], 5e-2)
for f, n in (("cauchy", 41), ("knn", 48)):
    check(f"gauss beats {f} (checkpoints of 48)", n,
          sum(r[f]["rmse_log"] > r["gauss"]["rmse_log"] for r in _rows))
_pub = {(r["run"], r["iter"]): r["h_eff"] for r in json.loads(
    pathlib.Path("results/exp1/_heff/heff_synthetic.json").read_text(encoding="utf-8"))}
check("gauss family reproduces published h_eff (of 120)", 120,
      sum(abs(np.log(r["gauss"]["s_var"] / _pub[(r["run"], r["iter"])])) < 1e-9
          for r in fam["rows"]))
f05 = fam["summary"]["h=0.5, iter>=3000"]
check("h=0.5: gauss best variance fit (of 15)", 14, f05["best_variance_fit_counts"]["gauss"])
check("h=0.5: gauss intervals agree (of 15)", 9, f05["gauss"]["overlap"])

print("\nNumbers introduced by the 2026-10-11 corrections (docs/review/paper_verification_2026-10-10.md)")
# (The seed-0 comparison of the training-time estimator with the M=256 re-evaluation that
# stood here is superseded by the twelve-run comparison in the seed-reproducibility block.)
check("beta h=6 at 60000, standard error", 0.06,
      next(r for r in bt if r["h"] == 6 and r["iter"] == 60000)["se"], 0.1)

# EXP-1 ablation, population SD over its two seeds.
for k, want in (("width32", 0.041), ("width64", 0.041), ("width256", 0.056),
                ("depth2", 0.110), ("depth6", 0.090), ("sgd", 0.136)):
    vals = [pd.read_csv(f).query("group == 'train'").set_index("iter").loc[200000, "trace_cov_mean"]
            for f in sorted(glob.glob(f"results/exp1/ablation_{k}_seed[01]/raw/metrics.csv"))]
    check(f"ablation {k} population SD", want, float(np.std(vals)), 1.5e-2)

# Table tab:gaph01, the aggregate row, and seed 4's aggregate at 1e6.
_g = [pd.read_csv(f).query("group == 'train'").set_index("iter")
      for f in sorted(glob.glob("results/exp1/exp1_ext_sched_h01_seed[0-4]/raw/metrics.csv"))]
for it, want in ((100, 1.045), (10000, 1.036), (100000, 0.991), (400000, 0.990), (1000000, 0.996)):
    check(f"h=0.1 aggregate ratio @{it} (median)", want,
          float(np.median([d.loc[it, "trace_cov_mean"] / d.loc[it, "trace_cov_kernel_mean"] for d in _g])), 1e-3)
check("h=0.1 seed 4 aggregate ratio @1e6", 0.987,
      float(_g[4].loc[1000000, "trace_cov_mean"] / _g[4].loc[1000000, "trace_cov_kernel_mean"]), 1e-3)
check("h=0.1 median tr Sigma_post", 1.015, float(np.median([d["trace_post"].iloc[0] for d in _g])), 1e-3)

# Table tab:p7kernel footnote, per-seed ratio at h=0.01.
_p7 = pd.read_csv("results/exp1/_theory/raw/p7_kernel.csv")
_r = _p7[_p7["h"] == 0.01].set_index("seed")["ratio_to_kernel"]
check("h=0.01 seed 0 ratio", 1.48, float(_r[0]), 5e-3)
check("h=0.01 seed 4 ratio", 1.96, float(_r[4]), 5e-3)
check("h=0.01 other seeds, low", 0.92, float(_r[[1, 2, 3]].min()), 5e-3)
check("h=0.01 other seeds, high", 1.10, float(_r[[1, 2, 3]].max()), 5e-3)
# Table tab:dagger caption: ||J||^2 across seeds, and seed 0's expansion vs measured.
_j = _p7[_p7["h"] == 0.5].set_index("seed")
check("||J||^2 smallest seed", 0.38, float(_j["j_fro_sq"].min()), 1e-2)
check("||J||^2 largest seed", 4.46, float(_j["j_fro_sq"].max()), 1e-2)
check("seed 0 expansion at h=0.5", 1.10, float(_j.loc[0, "trace_expansion"]), 1e-2)
check("seed 0 measured at h=0.5", 1.29, float(_j.loc[0, "trace_meas"]), 1e-2)
check("5-seed tr Cov_h at h=0.5", 1.28, float(_p7[_p7["h"] == 0.5]["trace_kernel"].mean()), 1e-2)
# Velocity-field factor, closer to the kernel field than to (star).
_kv = pd.read_csv("results/exp1/_theory/raw/kernel_verification.csv").groupby("h")
_fac = (_kv["rel_err_vs_star"].mean() / _kv["rel_err_vs_kernel"].mean())
check("velocity-field factor, smallest", 1.9, float(_fac.min()), 2e-2)
check("velocity-field factor, largest", 4.8, float(_fac.max()), 2e-2)
# Endpoint smoothing: per-arm and per-seed agreement with tr Cov_h + d rho^2.
_tn = pd.read_csv("results/exp1/_theory/raw/target_noise_trained.csv").set_index("arm")
check("rho arms, worst mean deviation (%)", 3.1,
      float((abs(_tn["trace_cov"] / _tn["predicted"] - 1)).max() * 100), 2e-2)
check("rho arms, worst per-seed deviation (%)", 6.0,
      max(abs(0.5870 / 0.6236 - 1), abs(0.2176 / 0.2108 - 1)) * 100, 3e-2)
# P5: between-seed SD of the collapse ratio.
_p5 = json.loads(pathlib.Path("results/exp1/_sweeps/summary.json").read_text(encoding="utf-8"))["P5"]
_rsd = [s / t for s, t in zip(_p5["trace_cov_std"], _p5["trace_post"])]
check("P5 ratio SD, smallest", 0.11, min(_rsd), 2e-2)
check("P5 ratio SD, largest", 0.15, max(_rsd), 2e-2)
# Held-out: largest train/held-out factor among seeds 1-4, and the two within 15%.
_tr = [0.547, 0.450, 0.417, 0.162]; _ho = [0.212, 0.429, 0.364, 0.564]
_fx = [max(a / b, b / a) for a, b in zip(_tr, _ho)]
check("held-out factor, largest (seeds 1-4)", 3.5, max(_fx), 1e-2)
check("held-out seeds within 15%", 2, sum(f <= 1.15 for f in _fx))
# Small corrections.
_a = json.loads(pathlib.Path("results/exp1/_heff/audit_v2_analysis.json").read_text(encoding="utf-8"))
check("Spearman of iteration with coverage", -0.41, _a["pooled"]["iter"]["test_coverage_90"], 1e-2)
check("EXP-2 final MMD", 0.24, json.loads(pathlib.Path("results/exp2/_analysis/summary.json")
      .read_text(encoding="utf-8"))["final_mmd"]["mean"], 3e-2)
_t3 = json.loads(pathlib.Path("results/theory/t3_coverage.json").read_text(encoding="utf-8"))
good = (max(r["mean_err"] for r in _t3["t3a"]) <= 0.018
        and max(r["cov_rel_err"] for r in _t3["t3a"]) <= 0.0075
        and abs(_t3["t3c"]["Var_mean_over_S"] - _t3["t3c"]["pred_Var_mean_over_S"]) <= 2e-3
        and abs(_t3["t3c"]["E_cov_over_S"] - _t3["t3c"]["pred_E_cov_over_S"]) <= 2e-3)
print(f"  {'OK ' if good else 'BAD'} {'T3 thresholds (0.018, 0.75%, 2e-3)':44s}")
ok, fail = ok + good, fail + (not good)
_t2f = json.loads(pathlib.Path("results/theory/t2_filtered.json").read_text(encoding="utf-8"))
check("filtered flow: worst endpoint distance to an atom", 0.0032,
      max(r["max_endpoint_dist_to_atom"] for r in _t2f["flow"]), 2e-2)
_ref = pd.read_csv("results/exp1/_theory/raw/posterior_reference_scales.csv").set_index("h")
check("atomic prediction over sampling floor, W2", 4.4,
      float(np.sqrt(_ref.loc[0.5, "sinkhorn_atomic"] / _ref.loc[0.5, "sinkhorn_floor"])), 1e-2)

print("\nNumbers introduced by the round-6 revision (docs/review/simulated_review_round6_2026-10-11.md)")
# The endpoint-smoothed family and the split by h (Table tab:families, bottom).
_er = f48["gauss_rho"]
check("endpoint-smoothed: 0 in rho interval (of 48)", 41, _er["rho_ci_includes_zero"])
check("endpoint-smoothed: max d rho^2 / trace", 0.08, _er["max_share_of_trace"], 5e-2)
check("endpoint-smoothed: held-out lower (of 48)", 10, _er["loo_better_than_gauss"])
check("endpoint-smoothed: held-out equal (of 48)", 21, _er["loo_equal_to_gauss"])
for hv, gb, lb, r2g, r2l, ci0, mx, lo, eq in (
        ("0", 7, 3, 0.82, 0.75, 9, 0.06, 6, 4), ("0.01", 8, 3, 0.82, 0.81, 10, 0.08, 1, 5),
        ("0.05", 11, 1, 0.94, 0.91, 12, 0.03, 1, 6), ("0.1", 10, 2, 0.95, 0.95, 10, 0.07, 2, 6)):
    s_ = fam["summary"][f"h={hv}, iter>=1e4 (of the 48)"]
    check(f"h={hv}: gauss / laplace best (of 12)", gb * 100 + lb,
          s_["best_variance_fit_counts"]["gauss"] * 100 + s_["best_variance_fit_counts"]["laplace"])
    check(f"h={hv}: median R^2 gauss", r2g, s_["gauss"]["median_r2_var"], 1e-2)
    check(f"h={hv}: median R^2 laplace", r2l, s_["laplace"]["median_r2_var"], 1e-2)
    check(f"h={hv}: 0 in rho interval (of 12)", ci0, s_["gauss_rho"]["rho_ci_includes_zero"])
    check(f"h={hv}: max d rho^2 / trace", mx, s_["gauss_rho"]["max_share_of_trace"], 0.1)
    check(f"h={hv}: held-out lower / equal", lo * 100 + eq,
          s_["gauss_rho"]["loo_better_than_gauss"] * 100 + s_["gauss_rho"]["loo_equal_to_gauss"])
check("h=0: median held-out gain", 0.0007,
      fam["summary"]["h=0, iter>=1e4 (of the 48)"]["gauss_rho"]["median_loo_gain"], 0.1)
# Run-level uncertainty of the coverage prediction.
_u = json.loads(pathlib.Path("results/theory/t3_coverage_uncertainty.json").read_text(encoding="utf-8"))
check("coverage R^2, run-resampled CI low", 0.85, _u["local_90"]["r2_ci95"][0], 1e-2)
check("coverage R^2, run-resampled CI high", 0.93, _u["local_90"]["r2_ci95"][1], 1e-2)
check("coverage R^2, binomial noise ceiling", 0.97, _u["noise_ceiling_r2_90"], 1e-2)
check("reference-law R^2, CI low", 0.89, _u["ref_90"]["r2_ci95"][0], 1e-2)
check("reference-law R^2, CI high", 0.96, _u["ref_90"]["r2_ci95"][1], 1e-2)
# Image-scale held-out calibration (second training of the six h_eff runs).
_ci = json.loads(pathlib.Path("results/exp3/_rerun/calib_image_summary.json").read_text(encoding="utf-8"))
_sp, _pa = _ci["spearman"], _ci["partial_given_log_iter"]
check("image: checkpoints", 42, _ci["n"])
check("image: Spearman h_eff with coverage", 0.63, _sp["coverage_90"]["h_eff"], 1e-2)
check("image: Spearman h_eff/h with coverage", 0.36, _sp["coverage_90"]["h_eff_over_h"], 2e-2)
check("image: Spearman pixel sd with coverage", 0.98, _sp["coverage_90"]["pixel_sd"], 1e-2)
check("image: partial h_eff | iteration", 0.59, _pa["coverage_90"]["h_eff"], 1e-2)
check("image: partial pixel sd | iteration", 0.97, _pa["coverage_90"]["pixel_sd"], 1e-2)
check("image: Spearman iteration with extraction", 0.98, _sp["extraction"]["log_iter"], 1e-2)
_by = {}
for r in _ci["rows"]:
    _by.setdefault(r["iter"], []).append(r)
for it, key, lo, hi in ((2000, "coverage_90", 0.91, 0.95), (20000, "coverage_90", 0.67, 0.78),
                        (60000, "coverage_90", 0.72, 0.81), (60000, "extraction", 0.67, 0.76)):
    v = [r[key] for r in _by[it]]
    check(f"image: {key} at {it // 1000}k, low", lo, min(v), 1e-2)
    check(f"image: {key} at {it // 1000}k, high", hi, max(v), 1e-2)
# A calibrated sampler's coverage by the 5-95% quantile interval of M=64 draws.
_g = np.random.default_rng(0).random((200000, 65))
_lo, _hi = np.quantile(_g[:, :64], 0.05, axis=1), np.quantile(_g[:, :64], 0.95, axis=1)
check("M=64 quantile interval, calibrated coverage", 0.873,
      float(((_g[:, 64] >= _lo) & (_g[:, 64] <= _hi)).mean()), 5e-3)
# The second rerun reproduces h_eff (the six runs at h in {4, 5}; h=0 and h=6 are
# checked separately above).
_he = {}
for f in sorted(glob.glob("results/exp3/_rerun/heff_exp3_cifar_heff_h[45]_s*.json")):
    d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    _he[(d["h"], d["seed"])] = d
check("rerun h_eff at 60k, h=4 seed 0", 4.93,
      [c["h_eff"] for c in _he[(4.0, 0)]["checkpoints"] if c["iter"] == 60000][0], 5e-3)
check("rerun h_eff at 60k, h=5 seed 0", 5.65,
      [c["h_eff"] for c in _he[(5.0, 0)]["checkpoints"] if c["iter"] == 60000][0], 5e-3)
_ag = [not (c["h_eff_ci"][1] < c["h_means_ci"][0] or c["h_means_ci"][1] < c["h_eff_ci"][0])
       for d in _he.values() for c in d["checkpoints"] if c["iter"] >= 5000]
check("rerun: h_eff and h_mean agree from 5k (of 36)", 31, sum(_ag))
_end = [c["h_eff"] / d["h"] for d in _he.values() for c in d["checkpoints"] if c["iter"] == 60000]
check("rerun: h_eff/h at 60k, low", 1.13, min(_end), 1e-2)
check("rerun: h_eff/h at 60k, high", 1.34, max(_end), 1e-2)
# Prop heffid: the bound against the bootstrap half-widths.
_t1 = json.loads(pathlib.Path("results/theory/t1_check.json").read_text(encoding="utf-8"))["width_vs_kappa"]
check("heffid bound holds (of 75)", 75, round(_t1["bound_holds_fraction"] * _t1["n"]))
check("heffid bound ranks widths, Spearman", 0.91, _t1["spearman_pred_vs_meas"], 1e-2)
# Audit box: trace error at M=128.
check("relative trace error at M=128 (%)", 12.5, 100 * np.sqrt(2 / 127), 5e-3)

print("\nImage-scale calibration at several levels (scripts/summarize_calib_levels.py)")
_cl = json.loads(pathlib.Path("results/exp3/_rerun/calib_levels_summary.json").read_text(encoding="utf-8"))
check("calib levels: checkpoints", 84, _cl["n"])
check("calib levels: runs", 12, _cl["runs"])
check("calib levels: 90% reference", 0.908, _cl["rows"][0]["ref90_central"], 2e-3)
_a = _cl["at_60k"]
_hp = [k for k in _a if float(k) > 0]
_marg = [x for k in _hp for st in ("pixel", "pc8", "pc32") for x in _a[k][st]["cov90"]]
check("60k marginal 90% coverage, h>0, min", 0.77, min(_marg), 1e-2)
check("60k marginal 90% coverage, h>0, max", 0.87, max(_marg), 1e-2)
_m0 = [x for st in ("pixel", "pc8", "pc32") for x in _a["0.0"][st]["cov90"]]
check("60k marginal 90% coverage, h=0, min", 0.06, min(_m0), 1e-1)
check("60k marginal 90% coverage, h=0, max", 0.08, max(_m0), 1e-1)
for st, lo, hi in (("joint8", 0.59, 0.78), ("joint32", 0.47, 0.77)):
    j = [x for k in _hp for x in _a[k][st]["cov90"]]
    check(f"60k {st} 90% coverage, h>0, min", lo, min(j), 1e-2)
    check(f"60k {st} 90% coverage, h>0, max", hi, max(j), 1e-2)
    check(f"60k {st} 90% coverage, h=0", 0.0, max(_a["0.0"][st]["cov90"]), 1e-9)
    check(f"{st} gap larger than per-pixel (of 84)", 84, _cl[f"{st}_worse_than_pixel"])
_sp = _cl["spearman_h_pos"]
_sd = [abs(_sp[st]["pixel_sd"]["spearman"]) for st in _sp]
_sdp = [abs(_sp[st]["pixel_sd"]["partial_given_log_iter"]) for st in _sp]
_he = [abs(_sp[st]["h_eff"]["spearman"]) for st in _sp]
check("spread |rho| min", 0.85, min(_sd), 1e-2)
check("spread |rho| max", 0.93, max(_sd), 1e-2)
check("spread partial |rho| min", 0.83, min(_sdp), 1e-2)
check("spread partial |rho| max", 0.92, max(_sdp), 1e-2)
check("h_eff |rho| min", 0.49, min(_he), 1e-2)
check("h_eff |rho| max", 0.65, max(_he), 1e-2)
check("spread has the smaller gap (negative rho), all", 5,
      sum(_sp[st]["pixel_sd"]["spearman"] < 0 for st in _sp))

print("\nIncremental value of h_eff over the free quantities (scripts/audit_incremental_r2.py)")
_ir = json.loads(pathlib.Path("results/exp1/_heff/audit_incremental_r2.json").read_text(encoding="utf-8"))["targets"]
_c = _ir["test_coverage_90"]
check("coverage: baseline CV R^2", 0.88, _c["r2_baseline"], 5e-3)
check("coverage: baseline + h_eff CV R^2", 0.92, _c["r2_baseline_plus_heff"], 5e-3)
check("coverage: delta R^2", 0.04, _c["delta_r2"], 5e-3)
check("coverage: delta R^2 CI low", -0.04, _c["delta_r2_ci95"][0], 5e-3)
check("coverage: delta R^2 CI high", 0.22, _c["delta_r2_ci95"][1], 5e-3)
check("PIT error: delta R^2", -0.13, _ir["test_pit_error"]["delta_r2"], 5e-3)
check("W2: delta R^2", -0.06, _ir["test_w2_median"]["delta_r2"], 5e-3)

print("\nTheorem thm:labelmix on the linear-Gaussian problem (scripts/theory_b_check.py)")
_tb = json.loads(pathlib.Path("results/theory/theorem_b_check.json").read_text(encoding="utf-8"))
check("Theorem B: violations (of 750)", 0, sum(v["violations"] for v in _tb["summary"].values()))
check("Theorem B: cases", 750, sum(v["cases"] for v in _tb["summary"].values()))
for n, mb, hb, he, eb in (("200", 2.34, 0.40, 0.225, 0.007), ("2000", 1.07, 0.17, 0.0949, 0.002),
                          ("10000", 0.62, 0.095, 0.0533, 0.004)):
    sm = _tb["summary"][n]
    check(f"N={n}: minimum bound", mb, sm["min_bound"], 5e-3)
    check(f"N={n}: minimiser of the bound", hb, sm["h_min_bound"], 1e-2)
    check(f"N={n}: best measured |C-0.9|", eb, sm["min_err90"], 1e-3)
    check(f"N={n}: minimiser ratio (1.8)", 1.8, sm["h_min_bound"] / sm["h_min_err90"], 2e-2)
    check(f"N={n}: bound / 2E[D] (about 5.6)", 5.6, sm["ratio_bound_to_2ED_median"], 3e-2)
_h3 = [r["err_0.9"] for r in _tb["rows"] if abs(r["h"] - 3.0) < 1e-9]
check("measured |C-0.9| at h=3 (0.03)", 0.03, float(np.mean(_h3)), 5e-3)

print("\nThree tests of the mechanism (App. app:specbias)")
_e3 = json.loads(pathlib.Path("results/theory/e3_ntk_label.json").read_text(encoding="utf-8"))
_last = lambda r: r["fits"][max(r["fits"], key=int)]
_dk = lambda r: r["change_from_first"][max(r["change_from_first"], key=int)]
_lo = [r for r in _e3["rows"] if r["h"] <= 0.1]
check("E3 kernel change h<=0.1, min", 0.68, min(_dk(r) for r in _lo), 1e-2)
check("E3 kernel change h<=0.1, max", 1.23, max(_dk(r) for r in _lo), 1e-2)
_hi = [r for r in _e3["rows"] if r["h"] == 0.5]
check("E3 kernel change h=0.5, min", 0.09, min(_dk(r) for r in _hi), 5e-2)
check("E3 kernel change h=0.5, max", 0.38, max(_dk(r) for r in _hi), 1e-2)
_z = [_last(r)["zeta_hat"] for r in _e3["rows"] if r["h"] <= 0.01]
check("E3 power-law exponent h<=0.01, min", 1.10, min(_z), 1e-2)
check("E3 power-law exponent h<=0.01, max", 1.29, max(_z), 1e-2)
check("E3 Laplace reference exponent", 2.09, _e3["reference"]["exponential_zeta2"]["zeta_hat"], 1e-2)
_e2 = json.loads(pathlib.Path("results/exp1/_heff/e2_floor_compare.json").read_text(encoding="utf-8"))
_arms = [k for k in _e2 if not k.startswith("base") and not k.startswith("lr0.003")]
_rat = [float(np.exp(_e2[k]["dlog_heff_vs_base"])) for k in _arms]
check("E2 h_eff / baseline, min", 0.86, min(_rat), 1e-2)
check("E2 h_eff / baseline, max", 1.22, max(_rat), 1e-2)
_r05 = [_e2[k]["h_eff_gm"] / 0.05 for k in _e2 if k.endswith("_h0.05") and not k.startswith("lr0.003")]
check("E2 h_eff/h at h=0.05, min", 1.01, min(_r05), 1e-2)
check("E2 h_eff/h at h=0.05, max", 1.18, max(_r05), 1e-2)
check("E2 lr 3e-3 diverged (of 6)", 4, _e2["lr0.003_h0"]["diverged"] + _e2["lr0.003_h0.05"]["diverged"])
_e1 = json.loads(pathlib.Path("results/exp1/_heff/heff_local_density.json").read_text(encoding="utf-8"))
_s0 = _e1["summary"]["h=0/h_mean"]
check("E1 pooled slope at h=0", -0.35, _s0["slope"], 1e-2)
check("E1 pooled CI low", -0.52, _s0["ci95"][0], 1e-2)
check("E1 pooled CI high", -0.16, _s0["ci95"][1], 1e-2)
_late = [r for r in _e1["rows"] if r["h"] == 0 and r["iter"] >= 100000]
check("E1 late checkpoints", 6, len(_late))
check("E1 per-run CI contains 0", 5, sum(r["h_mean"]["ci95"][0] <= 0 <= r["h_mean"]["ci95"][1] for r in _late))

print("\nJoint coverage from marginal under-dispersion (scripts/joint_from_marginal.py)")
_jm = json.loads(pathlib.Path("results/exp3/_rerun/joint_from_marginal.json").read_text(encoding="utf-8"))
_k8, _k32 = _jm["by_k"]["8"], _jm["by_k"]["32"]
check("joint model: checkpoints", 63, _jm["n"])
check("k=8: R^2 at 90%", 0.81, _k8["r2_90"], 5e-3)
check("k=8: R^2 over levels", 0.97, _k8["r2_all_levels"], 5e-3)
check("k=8: MAE at 90%", 0.05, _k8["mae_90"], 5e-3)
check("k=8: 60k predicted min", 0.51, _k8["at_60k"]["pred90"][0], 5e-3)
check("k=8: 60k predicted max", 0.78, _k8["at_60k"]["pred90"][1], 5e-3)
check("k=8: 60k measured min", 0.59, _k8["at_60k"]["meas90"][0], 5e-3)
check("k=8: 60k measured max", 0.78, _k8["at_60k"]["meas90"][1], 5e-3)
check("k=32: correlation", 0.92, _k32["corr_90"], 5e-3)
check("k=32: bias (overstated loss)", -0.19, _k32["bias_90"], 5e-3)
check("k=32 per component: bias", -0.16, _k32["per_component"]["bias_90"], 5e-3)
_s60 = [x for k in ("8", "32") for x in _jm["by_k"][k]["at_60k"]["s"]]
check("s at 60k, min (0.7)", 0.7, min(_s60), 1e-2)
check("s at 60k, max (0.9)", 0.9, max(_s60), 0.03)

print("\nRank-based per-pixel coverage in the main text (results/exp3/_rerun/calib_levels_summary.json)")
_clr = json.loads(pathlib.Path("results/exp3/_rerun/calib_levels_summary.json").read_text(encoding="utf-8"))["rows"]
for it, lo, hi in ((2000, 0.93, 0.96), (20000, 0.73, 0.82), (60000, 0.77, 0.86)):
    _v = [r["pixel_cov90"] for r in _clr if r["h"] > 0 and r["iter"] == it]
    check(f"per-pixel 90% coverage at {it}, min (2 d.p.)", lo, round(min(_v), 2), 1e-9)
    check(f"per-pixel 90% coverage at {it}, max (2 d.p.)", hi, round(max(_v), 2), 1e-9)
_spx = json.loads(pathlib.Path("results/exp3/_rerun/calib_levels_summary.json").read_text(encoding="utf-8"))["spearman_h_pos"]["pixel"]
check("per-pixel miscalibration vs spread |rho|", 0.90, round(abs(_spx["pixel_sd"]["spearman"]), 2), 1e-9)
check("per-pixel miscalibration vs h_eff |rho|", 0.52, round(abs(_spx["h_eff"]["spearman"]), 2), 1e-9)
in_tex(r"per-pixel coverage near nominal ($0.77$--$0.86$")

print("\nsanity: strings the new text depends on")
for s in (r"\label{sec:cifarddpm}", r"\label{tab:cifarddpm}",
          r"\label{fig:cifartrack}", r"\label{sec:p6exposure}",
          r"\label{sec:seedsplit}", r"fig_cifar_ddpm_tracking.png"):
    in_tex(s)

print(f"\n{ok} checks passed, {fail} failed")
raise SystemExit(1 if fail else 0)
