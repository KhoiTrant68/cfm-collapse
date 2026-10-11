# -*- coding: utf-8 -*-
"""Supplementary paper-number audit: claims in paper/main.tex NOT covered by
scripts/verify_paper_numbers.py. Reads only saved outputs under results/.
Run from the repo root:
    uv run python docs/review/paper_verification_2026-10-10_checks.py
"""
import json, pathlib, re
import numpy as np
import pandas as pd

R = pathlib.Path("results")
TEX = pathlib.Path("paper/main.tex").read_text(encoding="utf-8")
rows = []


def rec(section, claim, paper, actual, ok=None, note=""):
    if ok is None:
        # tolerance: half a unit in the last printed digit of the paper value
        s = f"{paper}"
        dec = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-dec) + 1e-12
        ok = abs(float(paper) - float(actual)) <= tol
    rows.append((section, claim, paper, actual, "OK" if ok else "BAD", note))


def m(run, group="train"):
    df = pd.read_csv(R / run / "raw/metrics.csv")
    if "group" in df.columns:
        df = df[df["group"] == group]
    return df.set_index("iter")


def seeds(pattern, group="train"):
    return [m(p.relative_to(R).as_posix().rsplit("/raw", 1)[0], group)
            for p in sorted(R.glob(pattern + "/raw/metrics.csv"))]


def ms(vals):  # population std, as the paper states
    v = np.asarray(vals, float)
    return v.mean(), v.std()


# ---------------------------------------------------------------- EXP-1 Table 1
cond = seeds("exp1/exp1_cond_seed[0-4]")
unc = seeds("exp1/exp1_uncond_seed[0-4]", "uncond")
ext = seeds("exp1/exp1_ext_sched_seed[0-4]")
assert len(cond) == 5 and len(unc) == 5 and len(ext) == 5
tab1 = {  # paper Table tab:exp1
    "trace_cov_mean": {100: (1.08, .02), 10000: (1.03, .11), 100000: (0.58, .18), 200000: (0.396, .127), 1000000: (0.120, .054)},
    "vel_rel_err_mean_mean": {100: (.78, .03), 10000: (.75, .07), 100000: (.50, .04), 200000: (.40, .05), 1000000: (.168, .052)},
    "mean_err_train_point_mean": {100: (.90, .16), 10000: (.87, .20), 100000: (.58, .13), 200000: (.38, .10), 1000000: (.137, .065)},
    "mean_err_post_mean": {100: (.15, .06), 10000: (.25, .07), 100000: (.52, .10), 200000: (.66, .18), 1000000: (.816, .172)},
}
for col, cells in tab1.items():
    for it, (pm, ps) in cells.items():
        src = ext if it == 1000000 else cond
        mu, sd = ms([d.loc[it, col] for d in src])
        rec("Tab1", f"{col} @{it} mean", pm, mu)
        rec("Tab1", f"{col} @{it} std", ps, sd)
for it, (pm, ps) in {100: (1.85, .55), 10000: (1.93, .16), 100000: (1.91, .17), 200000: (1.926, .171)}.items():
    mu, sd = ms([d.loc[it, "trace_cov_mean"] for d in unc])
    rec("Tab1", f"uncond trace @{it} mean", pm, mu); rec("Tab1", f"uncond trace @{it} std", ps, sd)
tp, sp = ms([d["trace_post"].iloc[0] for d in cond])
rec("Tab1", "tr Sigma_post mean", 1.018, tp); rec("Tab1", "tr Sigma_post std", 0.016, sp)
td, sd_ = ms([d["trace_data"].iloc[0] for d in unc])
rec("Tab1", "tr Xhat mean", 1.931, td); rec("Tab1", "tr Xhat std", 0.162, sd_)

# ---------------------------------------------------------------- cosine schedule
fixed0 = m("exp1/exp1_cond_seed0_ext")
rec("Sched", "seed0 fixed-lr trace @7e5", 0.162, fixed0.loc[700000, "trace_cov_mean"])
rec("Sched", "seed0 sched trace @7e5", 0.128, ext[0].loc[700000, "trace_cov_mean"])
rec("Sched", "seed0 sched trace @1e6", 0.115, ext[0].loc[1000000, "trace_cov_mean"])
fin = [d.loc[1000000, "trace_cov_mean"] for d in ext]
rec("Sched", "min seed @1e6", 0.035, min(fin)); rec("Sched", "max seed @1e6", 0.186, max(fin))
imp = sum(d.loc[1000000, "trace_cov_mean"] < d.loc[700000, "trace_cov_mean"] for d in ext)
rec("Sched", "seeds improving 7e5->1e6", 4, imp, imp == 4)
rec("Sched", "memo ratio @1e6 mean", 0.955, np.mean([d.loc[1000000, "memorization_ratio_mean"] for d in ext]))

# ---------------------------------------------------------------- memorisation baseline
mr_c = seeds("exp1/exp1_cond_seed[0-4]_mr"); mr_u = seeds("exp1/exp1_uncond_seed[0-4]_mr", "uncond")
c0 = np.mean([d["memorization_ratio_mean"].iloc[0] for d in mr_c])
rec("Memo", "cond baseline ~0.11 (first ckpt)", 0.11, c0)
try:
    u0 = np.mean([d["memorization_ratio_mean"].iloc[0] for d in mr_u])
    rec("Memo", "uncond baseline ~0.11 (first ckpt)", 0.11, u0)
except KeyError as e:
    rec("Memo", "uncond baseline", 0.11, float("nan"), False, f"col missing {e}")

# ---------------------------------------------------------------- held-out table
ho = seeds("exp1/exp1_cond_seed[0-4]", "heldout")
want_tr = [0.407, 0.547, 0.450, 0.417, 0.162]
want_ho = [3.0e5, 0.212, 0.429, 0.364, 0.564]
for s in range(5):
    rec("Heldout", f"seed{s} train trace @2e5", want_tr[s], cond[s].loc[200000, "trace_cov_mean"])
    v = ho[s].loc[200000, "trace_cov_mean"]
    rec("Heldout", f"seed{s} heldout trace @2e5", want_ho[s], v, abs(v - want_ho[s]) / want_ho[s] < 0.02)
hv = [d.loc[200000, "trace_cov_mean"] for d in ho]
rec("Heldout", "heldout median @2e5", 0.43, np.median(hv))
rec("Heldout", "train median @2e5", 0.42, np.median(want_tr))
rec("Heldout", "heldout mean @1e5", 0.51, np.mean([d.loc[100000, "trace_cov_mean"] for d in ho]))
rec("Heldout", "train mean @1e5", 0.58, np.mean([d.loc[100000, "trace_cov_mean"] for d in cond]))
e0 = np.median([d["mean_err_post_mean"].iloc[0] for d in ho]); e1 = np.median([d.loc[200000, "mean_err_post_mean"] for d in ho])
rec("Heldout", "heldout |mean-mu_post| median first ckpt", 0.12, e0)
rec("Heldout", "heldout |mean-mu_post| median @2e5", 0.87, e1)
ratio_ho = [ho[s].loc[200000, "trace_cov_mean"] / cond[s].loc[200000, "trace_cov_mean"] for s in range(1, 5)]
rec("Heldout", "seeds 1-4 heldout/train within ~2x", "<=2", max(max(ratio_ho), 1 / min(ratio_ho)),
    max(max(ratio_ho), 1 / min(ratio_ho)) <= 2.2, "ratios " + ", ".join(f"{r:.2f}" for r in ratio_ho))

# ---------------------------------------------------------------- adversarial
adv = seeds("exp1/exp1_adv_shuffle_seed[0-4]")
mu, sd = ms([d["mean_err_post_mean"].iloc[0] for d in adv]); rec("Adv", "|mean-mu_post| start mean", 0.84, mu); rec("Adv", "start std", 0.13, sd)
mu, sd = ms([d["mean_err_train_point_mean"].iloc[0] for d in adv]); rec("Adv", "|mean-x^i| start mean", 1.35, mu); rec("Adv", "start std", 0.10, sd)
its = adv[0].index.values
mp = np.mean([d["mean_err_post_mean"].values for d in adv], 0); mx = np.mean([d["mean_err_train_point_mean"].values for d in adv], 0)
cross = [its[i] for i in range(1, len(its)) if (mp[i - 1] - mx[i - 1]) <= 0 < (mp[i] - mx[i])]
rec("Adv", "crossing iteration in (1e4, 3e4]", "1e4-3e4", cross, bool(cross) and 10000 <= cross[0] <= 30000, f"iters {list(its)}")

# ---------------------------------------------------------------- ablation table
ab = {"width32": (.657, .058), "width64": (.526, .058), "width256": (.403, .079),
      "depth2": (.860, .156), "depth6": (.407, .127), "sgd": (.711, .193)}
for k, (pm, ps) in ab.items():
    ds = seeds(f"exp1/ablation_{k}_seed[0-1]")
    mu, sd = ms([d.loc[200000, "trace_cov_mean"] for d in ds])
    rec("Ablation", f"{k} mean", pm, mu); rec("Ablation", f"{k} std", ps, sd)
w256 = np.mean([d.loc[200000, "train_loss"] for d in seeds("exp1/ablation_width256_seed[0-1]")])
base = np.mean([d.loc[200000, "train_loss"] for d in cond])
base2 = np.mean([d.loc[200000, "train_loss"] for d in cond[:2]])
rec("Ablation", "width256 train loss", 0.46, w256); rec("Ablation", "baseline train loss (5 seeds)", 0.59, base, note=f"2-seed baseline {base2:.3f}")

# ---------------------------------------------------------------- velocity-field table (dagger)
kv = pd.read_csv(R / "exp1/_theory/raw/kernel_verification.csv")
dag = {0.01: (.318, .030, .599, .104, .31, .18), 0.05: (.195, .019, .683, .103, .22, .02),
       0.1: (.162, .021, .703, .092, .16, .04), 0.5: (.164, .025, .791, .070, .16, .02)}
facs = []
for h, w in dag.items():
    g = kv[kv["h"] == h]
    for (col, pm, ps) in (("rel_err_vs_kernel", w[0], w[1]), ("rel_err_vs_star", w[2], w[3]), ("tv_mixture", w[4], w[5])):
        mu, sd = ms(g[col]); rec("Dagger", f"h={h} {col} mean", pm, mu); rec("Dagger", f"h={h} {col} std", ps, sd)
    facs.append(g["rel_err_vs_star"].mean() / g["rel_err_vs_kernel"].mean())
rec("Dagger", "'2-4x closer to kernel field'", "2-4", f"{min(facs):.2f}-{max(facs):.2f}", 1.95 <= min(facs) and max(facs) <= 4.5)

# ---------------------------------------------------------------- ||J||^2 claim in Table dagger caption
p7 = pd.read_csv(R / "exp1/_theory/raw/p7_kernel_summary.csv").set_index("h")
exp_h05 = p7.loc[0.5, "trace_expansion"]; meas = p7.loc[0.5, "trace_meas_mean"]
rec("Dagger", "Sigma_post + h^2*0.4031 at h=0.5 vs measured 1.29", 1.29, 1.0177 + 0.25 * 0.4031, False,
    f"5-seed expansion column = {exp_h05:.3f}; measured = {meas:.3f}")

# ---------------------------------------------------------------- gap diagnostic h=0.1
g01 = seeds("exp1/exp1_ext_sched_h01_seed[0-4]")
for it, (r_, me, tr) in {100: (1.649, .188, 1.091), 10000: (1.062, .151, 1.087), 100000: (1.002, .0534, 1.035),
                          400000: (.997, .0314, 1.018), 1000000: (1.004, .0220, 1.056)}.items():
    agg = np.median([d.loc[it, "trace_cov_mean"] / d.loc[it, "trace_cov_kernel_mean"] for d in g01])
    rec("Gap h01", f"@{it} [info] AGGREGATE ratio the audit box recommends", r_, agg, True,
        note="paper row is the mean of per-condition ratios; this is what the aggregate gives")
    rec("Gap h01", f"@{it} ratio_to_kernel_mean col median", r_, np.median([d.loc[it, "ratio_to_kernel_mean"] for d in g01]))
    rec("Gap h01", f"@{it} |mean - xbar_h| median", me, np.median([d.loc[it, "mean_err_kernel_mean"] for d in g01]))
    rec("Gap h01", f"@{it} tr Cov median", tr, np.median([d.loc[it, "trace_cov_mean"] for d in g01]))
rec("Gap h01", "tr Sigma_post (caption 1.004)", 1.004, np.median([d["trace_post"].iloc[0] for d in g01]))
ne = [d.loc[1000000, "n_eff_mean"] for d in g01]
rec("Gap h01", "n_eff median", 25.1, np.median(ne)); rec("Gap h01", "n_eff min", 13.7, min(ne)); rec("Gap h01", "n_eff max", 43.9, max(ne))
pr = sorted(d.loc[1000000, "ratio_to_kernel_mean"] for d in g01)
rec("Gap h01", "per-seed ratio @1e6 (0.99-1.03 x4, 2.85)", "0.99-1.03,2.85", [round(x, 3) for x in pr],
    abs(pr[-1] - 2.85) < 0.01 and pr[0] >= 0.985 and pr[3] <= 1.035)
pe = [d.loc[1000000, "mean_err_kernel_mean"] for d in g01]
rec("Gap h01", "per-seed mean err @1e6 range", "0.019-0.026", f"{min(pe):.4f}-{max(pe):.4f}", 0.0185 <= min(pe) and max(pe) <= 0.0265)
rec("Gap h01", "vel err h=0.1 first ckpt median", 0.78, np.median([d["vel_rel_err_mean_mean"].iloc[0] for d in g01]))
rec("Gap h01", "vel err h=0.1 @1e6 median", 0.65, np.median([d.loc[1000000, "vel_rel_err_mean_mean"] for d in g01]))
rec("Gap h01", "vel err h=0 @1e6 median", 0.15, np.median([d.loc[1000000, "vel_rel_err_mean_mean"] for d in ext]))
rec("Gap h01", "h=0 sched trCov first->1e6 (1.087->0.115) median start", 1.087, np.median([d["trace_cov_mean"].iloc[0] for d in ext]))
rec("Gap h01", "h=0 sched trCov @1e6 median", 0.115, np.median([d.loc[1000000, "trace_cov_mean"] for d in ext]))

# ---------------------------------------------------------------- optimality gap
og = pd.read_csv(R / "exp1/_theory/raw/optimality_gap.csv")
last = og.sort_values("iter").groupby("h").tail(1)
rec("Optgap", "last-ckpt gap range 0.09-0.44", "0.09-0.44", f"{last.gap.min():.3f}-{last.gap.max():.3f}",
    round(last.gap.min(), 2) == 0.09 and round(last.gap.max(), 2) == 0.44)
mono = all((np.diff(g.sort_values("iter").gap.values) <= 1e-9).all() for _, g in og.groupby("h"))
rec("Optgap", "gap decreases monotonically at every h", True, mono, mono)
rec("Optgap", "L* at h=0.5 (1.88)", 1.88, og[og.h == 0.5].L_star.mean())

# ---------------------------------------------------------------- P7 table / misc
rec("P7", "best-match h n_eff 26 (h=0.1)", 26, p7.loc[0.1, "n_eff"]); rec("P7", "n_eff h=0.5 (102)", 102, p7.loc[0.5, "n_eff"])
rec("P7", "ratio of mean traces 0.673/0.583", 1.15, p7.loc[0.01, "trace_meas_mean"] / p7.loc[0.01, "trace_kernel"])
rec("P7", "Covh|h=0.1 ~1.00", 1.00, p7.loc[0.1, "trace_kernel"])

# ---------------------------------------------------------------- endpoint smoothing per seed (Table tgt)
tg = {"rho00": [(0.2176, 0.2108), (0.4353, 0.4436)], "rho03": [(0.3959, 0.3908), (0.5870, 0.6236)]}
devs = []
for arm, vals in tg.items():
    for s, (tr, pred) in enumerate(vals):
        devs.append(abs(tr / pred - 1))
rec("Tgt", "'tracks tr Cov_h + d rho^2 to within 3% ... per seed'", "<=3%", f"max per-seed {max(devs)*100:.1f}%", max(devs) <= 0.03,
    "arm means: 0.2%, 3.1%")

# ---------------------------------------------------------------- sweeps
sw = json.loads((R / "exp1/_sweeps/summary.json").read_text())
P5 = sw["P5"]
rng = max(P5["ratio"]) - min(P5["ratio"])
rec("P5", "ratio range ~0.14", 0.14, rng)
ratio_sd = [s / t for s, t in zip(P5["trace_cov_std"], P5["trace_post"])]
rec("P5", "range < between-seed std at each point", True, f"range {rng:.3f}; trace std {np.round(P5['trace_cov_std'],3).tolist()}; ratio std {np.round(ratio_sd,3).tolist()}",
    all(rng < s for s in ratio_sd))

# ---------------------------------------------------------------- EXP-2 / EXP-3
e2 = json.loads((R / "exp2/_analysis/summary.json").read_text())
rec("EXP-2", "final mode coverage", 0.72, e2["final_mode_coverage"]["mean"])
rec("EXP-2", "final MMD ~0.25", 0.25, e2["final_mmd"]["mean"], abs(e2["final_mmd"]["mean"] - 0.25) < 0.006)
ns = json.loads((R / "exp3/_n_sweep/summary.json").read_text())
cb = ns["constant_budget"]; ce = ns["constant_exposure"]
lN = np.log([r["N"] for r in cb])
rec("N-sweep", "constant-budget slope", 0.90, np.polyfit(lN, np.log([r["pixel_var_inpaint_mean"] for r in cb]), 1)[0])
rec("N-sweep", "constant-exposure slope", -0.29, np.polyfit(lN, np.log([r["pixel_var_inpaint_mean"] for r in ce]), 1)[0])
rec("N-sweep", "constant-budget spread", 14.9, cb[2]["pixel_var_inpaint_mean"] / cb[0]["pixel_var_inpaint_mean"])
rec("N-sweep", "constant-exposure spread", 2.3, ce[0]["pixel_var_inpaint_mean"] / ce[2]["pixel_var_inpaint_mean"])
for r in ns["matched_loss"]:
    if r["train_loss"] in (0.02, 0.015, 0.01):
        want = {0.02: (1.09e-3, 2.77e-3, 3.13e-3), 0.015: (7.76e-4, 1.23e-3, 1.37e-3), 0.01: (3.15e-4, 6.16e-4, 5.80e-4)}[r["train_loss"]]
        for N, w in zip(("100", "500", "2000"), want):
            rec("N-sweep", f"matched loss {r['train_loss']} N={N}", w, r[N], abs(r[N] / w - 1) < 0.006)
rec("N-sweep", "EXP-1 P6 spread replicate quoted (14.9->2.34)", 2.34, ce[0]["pixel_var_inpaint_mean"] / ce[2]["pixel_var_inpaint_mean"])

# ---------------------------------------------------------------- collapse time
ct = json.loads((R / "collapse_time/collapse_time.json").read_text())
tc3072 = [ct["panel_b"][n]["t_c"][-1] for n in ("50", "500", "2000")]
rec("Collapse time", "t_c at d=3072 ('0.06')", 0.06, f"{min(tc3072):.3f}-{max(tc3072):.3f}", round(min(tc3072), 2) <= 0.06 <= round(max(tc3072), 2) + 0.005)
tc2 = [ct["panel_b"][n]["t_c"][0] for n in ("50", "500", "2000")]
rec("Collapse time", "t_c at d=2 0.86-0.97", "0.86-0.97", f"{min(tc2):.3f}-{max(tc2):.3f}", round(min(tc2), 2) == 0.86 and round(max(tc2), 2) == 0.97)

# ---------------------------------------------------------------- theory checks
t3 = json.loads((R / "theory/t3_coverage.json").read_text())
rec("T3", "large-N mean error <= 0.017", 0.017, max(r["mean_err"] for r in t3["t3a"]), max(r["mean_err"] for r in t3["t3a"]) <= 0.0175)
rec("T3", "large-N cov error <= 0.7%", 0.007, max(r["cov_rel_err"] for r in t3["t3a"]), max(r["cov_rel_err"] for r in t3["t3a"]) <= 0.0075)
rec("T3", "(d) E cov identity to 1e-3", 1e-3, abs(t3["t3c"]["E_cov_over_S"] - t3["t3c"]["pred_E_cov_over_S"]), abs(t3["t3c"]["E_cov_over_S"] - t3["t3c"]["pred_E_cov_over_S"]) <= 1e-3)
rec("T3", "(d) Var mean identity to 1e-3", 1e-3, abs(t3["t3c"]["Var_mean_over_S"] - t3["t3c"]["pred_Var_mean_over_S"]), abs(t3["t3c"]["Var_mean_over_S"] - t3["t3c"]["pred_Var_mean_over_S"]) <= 1e-3)
rec("T3", "coverage of N(mu_h,Sig_h) vs MC to 0.002", 0.002, max(abs(r["mc"] - r["formula"]) for r in t3["t3b"]), max(abs(r["mc"] - r["formula"]) for r in t3["t3b"]) <= 0.0025)
rows3 = pd.DataFrame(t3["t3d"]["rows"])
print("t3d columns:", list(rows3.columns))
tg_ = json.loads((R / "theory/t3_general.json").read_text())
ratios = [abs(r["clean"]["0.9"] - r["noisy"]["0.9"]) / r["tv_exact"] for r in tg_["rows"] if r["tv_exact"] > 0]
ratios5 = [abs(r["clean"]["0.5"] - r["noisy"]["0.5"]) / r["tv_exact"] for r in tg_["rows"] if r["tv_exact"] > 0]
rec("T3 general", "max |clean-noisy|/tau_h = 0.96", 0.96, max(ratios + ratios5))
t1 = json.loads((R / "theory/t1_check.json").read_text())
fd = max(max(r["rel_err_dT"], r["rel_err_dxbar"]) for r in t1["t1a_finite_difference"])
rec("T1", "finite-diff rel err < 1e-9", 1e-9, fd, fd < 1e-9, f"h range {t1['t1a_finite_difference'][0]['h']}-{t1['t1a_finite_difference'][-1]['h']}")
t2f = json.loads((R / "theory/t2_filtered.json").read_text())
print("t2_filtered flow rows:")
for r in t2f["flow"]:
    print("   ", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

# ---------------------------------------------------------------- CIFAR extras
st = json.loads((R / "exp3/_cifar_ddpm/stats.json").read_text())
reev = {f"{float(r['h']):.0f}": r for r in json.loads((R / "exp3/_cifar_ddpm/reeval.json").read_text())}
print("reeval keys:", sorted(reev["4"].keys()))
for h, run in (("4", "exp3_cifar_ddpm_h4_seed2"),):
    d = pd.read_csv(R / f"exp3/{run}/raw/metrics.csv").sort_values("iter").iloc[-1]
    rec("CIFAR", "h=4 seed2 n_eff 2.10", 2.10, d["n_eff_mean"])
for h, vals in (("5", (276.8, 321.2, 349.0)), ("6", (406.4, 347.1, 364.9))):
    for s, (suffix, v) in enumerate(zip(("", "_seed1", "_seed2"), vals)):
        d = pd.read_csv(R / f"exp3/exp3_cifar_ddpm_h{h}{suffix}/raw/metrics.csv").sort_values("iter").iloc[-1]
        rec("CIFAR", f"Tab seed3 h={h} seed{s} raw trace", v, d["trace_cov_mean"])
for h, (lo, hi) in (("5", (13.0, 17.2)), ("6", (50, 93))):
    ne_ = [pd.read_csv(R / f"exp3/exp3_cifar_ddpm_h{h}{s}/raw/metrics.csv").sort_values("iter").iloc[-1]["n_eff_mean"] for s in ("", "_seed1", "_seed2")]
    rec("CIFAR", f"Tab seed3 h={h} n_eff range", f"{lo}-{hi}", f"{min(ne_):.1f}-{max(ne_):.1f}",
        abs(min(ne_) - lo) < 0.6 and abs(max(ne_) - hi) < 0.6)
# same instance, two protocols: training log (8 cond, M=16) vs re-evaluation (48 cond, M=256)
for h, run in (("4", "exp3_cifar_ddpm_h4"), ("5", "exp3_cifar_ddpm_h5"), ("6", "exp3_cifar_ddpm_h6")):
    d = pd.read_csv(R / f"exp3/{run}/raw/metrics.csv").sort_values("iter").iloc[-1]
    a_log = d["trace_cov_mean"] / d["trace_cov_kernel_mean"]
    a_re = np.mean(reev[h]["trace_cov"]) / np.mean(reev[h]["trace_cov_kernel"])
    rec("CIFAR", f"h={h} seed0 aggregate: Tab seed3 (log) vs M=256 re-eval", f"{a_log:.3f}", f"{a_re:.3f}",
        abs(a_log / a_re - 1) < 0.05, f"protocol gap {100*abs(a_log/a_re-1):.1f}%")
h0 = [pd.read_csv(R / f"exp3/exp3_cifar_ddpm_h0{s}/raw/metrics.csv").sort_values("iter").iloc[-1]["trace_cov_mean"] for s in ("", "_seed1", "_seed2")]
rec("CIFAR", "h=0 final trace range 0.409-0.467", "0.409-0.467", f"{min(h0):.3f}-{max(h0):.3f}", round(min(h0), 3) == 0.409 and round(max(h0), 3) == 0.467)
h6 = pd.read_csv(R / "exp3/exp3_cifar_ddpm_h6/raw/metrics.csv").set_index("iter")
rec("CIFAR", "h=6 aggregate ratio @8000 (0.98) from training log", 0.98, h6.loc[8000, "trace_cov_mean"] / h6.loc[8000, "trace_cov_kernel_mean"],
    note="beta_trajectory.json (M=96) gives 0.984")
for k in ("ratio_mean", "mean_ratio", "ratio_to_kernel_mean"):
    if k in reev["4"]:
        rec("CIFAR", f"M=256 mean of per-condition ratios at h=4 ({k})", 20.4, reev["4"][k])
cfg = (pathlib.Path("configs/exp3_cifar_ddpm.yaml")).read_text()
rec("CIFAR", "training-log eval protocol used by Tab seed3 / 179.1->0.431", "48 cond, M=256 (Sec 4.2)",
    re.search(r"n_conditions:\s*(\d+)", cfg).group(1) + " cond, M=" + re.search(r"\bM:\s*(\d+)", cfg).group(1), False,
    "metrics.csv is the in-training evaluator")

# ---------------------------------------------------------------- class-conditional
for run, (sc, lo, hi) in (("exp3_cifar_class_h0", (717, 0.64, 0.83)), ("exp3_cifar_class_h0p4", (719, 0.62, 1.30))):
    d = pd.read_csv(R / f"exp3/{run}/raw/metrics.csv").sort_values("iter")
    ratio = d["trace_cov_mean"] / d["trace_cov_kernel_mean"]
    rec("Class", f"{run} within-class scatter", sc, d["trace_cov_kernel_mean"].iloc[-1], abs(d["trace_cov_kernel_mean"].iloc[-1] - sc) < 0.6)
    rec("Class", f"{run} ratio range", f"{lo}-{hi}", f"{ratio.min():.3f}-{ratio.max():.3f}", round(ratio.min(), 2) == lo and round(ratio.max(), 2) == hi)
    rec("Class", f"{run} final ratio 0.76", 0.76, ratio.iloc[-1])
    rec("Class", f"{run} loss start", 0.22, d["train_loss"].iloc[0], abs(d["train_loss"].iloc[0] - 0.22) < 0.006)
    rec("Class", f"{run} loss end", 0.06, d["train_loss"].iloc[-1], abs(d["train_loss"].iloc[-1] - 0.06) < 0.006)

# ---------------------------------------------------------------- output
w = max(len(r[1]) for r in rows)
bad = [r for r in rows if r[4] == "BAD"]
for sec in dict.fromkeys(r[0] for r in rows):
    print(f"\n[{sec}]")
    for r in rows:
        if r[0] == sec:
            a = r[3] if isinstance(r[3], (str, list, bool)) else f"{r[3]:.5g}"
            print(f"  {r[4]:3} {r[1]:{w}}  paper={r[2]!s:<14} file={a!s:<22} {r[5]}")
print(f"\n{len(rows) - len(bad)} OK, {len(bad)} BAD")
