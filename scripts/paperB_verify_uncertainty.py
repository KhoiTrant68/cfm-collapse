"""Independent verifier for the paper-B analysis "uncertainty".

Recomputes from the saved files only (it does not import or read scripts/paperB_uncertainty.py,
scripts/kernel_tracking_uncertainty.py or scripts/uncertainty_common.py). Parts (1) tab:p7kernel and
(2) cover the label-noise numbers that now live in paper_theory; they are kept as a cross-check:

 (1) EXP-1 (sec:exp1, tab:exp1, tab:p7kernel): per-seed values, mean, population SD, sample SD,
     95% Student-t interval (n=5, df=4), exact seed bootstrap (all 5^5 resamples), seed-paired
     contrasts.
 (2) CIFAR kernel tracking (tab:cifarddpm, fig_kernel): OLS slope of log10 measured on log10
     reference, OLS / HC3 standard errors, R^2, decades, case bootstrap (percentile, BCa);
     the per-instance re-runs in results/exp3/_rerun: per-instance slopes, t over instances,
     pooled within-instance slope, exact cluster bootstrap, two-stage bootstrap.
 (3) EDM late contraction (sec:edm, tab:edm-models): C = sum_{k=11..16} (1-(rho_k+rho_{k+1})/2)
     log(sigma_k/sigma_{k+1}), rho = err/n1, off-atom = d1/d2 >= 1/3, AUC = P(-C_off > -C_on);
     stratified / DeLong / class-cluster / endpoint-image-cluster intervals, the nearest-image
     baseline dD at sigma=0.002 and the paired difference, and a distribution-free lower bound
     when the groups are completely separated.

numpy only:   PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_uncertainty
Writes:       results/paperB_20261121/verify_uncertainty/{verify.json, stdout.txt}
"""
from __future__ import annotations

import csv
import io
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

R = Path("results")
OUT = R / "paperB_20261121" / "verify_uncertainty"
LOG = io.StringIO()


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


# ----------------------------------------------------------------------------- distributions
def _betacf(a, b, x):
    fpmin, eps = 1e-300, 1e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > fpmin else fpmin)
    h = d
    for m in range(1, 2000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = d if abs(d) > fpmin else fpmin
        c = 1.0 + aa / c; c = c if abs(c) > fpmin else fpmin
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = d if abs(d) > fpmin else fpmin
        c = 1.0 + aa / c; c = c if abs(c) > fpmin else fpmin
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    p = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_ppf(q, df):
    lo, hi = -1e4, 1e4
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def Phi(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def Phi_inv(p):
    lo, hi = -40.0, 40.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if Phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


T4 = t_ppf(0.975, 4)
T2 = t_ppf(0.975, 2)
Z = Phi_inv(0.975)


# ----------------------------------------------------------------------------- helpers
def r3(x, k=3):
    return None if x is None else round(float(x), k)


def matches(value, printed, decimals):
    """True when value rounds to the printed number at its printed precision."""
    return abs(value - printed) <= 0.5 * 10 ** (-decimals) + 1e-12


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pick(rows, group, it, col):
    sel = [r for r in rows if r["group"] == group and int(float(r["iter"])) == it]
    assert len(sel) == 1, (group, it, col, len(sel))
    return float(sel[0][col])


def exact_boot(v):
    v = np.asarray(v, float)
    n = len(v)
    idx = np.array(list(itertools.product(range(n), repeat=n)))
    means = v[idx].mean(1)
    return [float(x) for x in np.percentile(means, [2.5, 97.5])], means


def summ(v):
    v = np.asarray(v, float)
    n = len(v)
    m, sd0, sd1 = float(v.mean()), float(v.std(ddof=0)), float(v.std(ddof=1))
    tq = t_ppf(0.975, n - 1)
    hw = tq * sd1 / math.sqrt(n)
    bci, _ = exact_boot(v)
    return {"per_seed": [float(x) for x in v], "mean": m, "sd_pop": sd0, "sd_sample": sd1,
            "t_ci": [m - hw, m + hw], "t_halfwidth": hw, "boot_ci": bci}


# ============================================================================= (1) EXP-1
def part1():
    say("=" * 100)
    say("(1) EXP-1: tab:exp1, sec:exp1, tab:p7kernel")
    say(f"t quantiles: t(0.975,4)={T4:.6f}  t(0.975,2)={T2:.6f}  t(0.975,46)={t_ppf(0.975, 46):.6f}  z={Z:.6f}")
    E = R / "exp1"
    S = range(5)
    cond = [read_rows(E / f"exp1_cond_seed{s}/raw/metrics.csv") for s in S]
    cos = [read_rows(E / f"exp1_ext_sched_seed{s}/raw/metrics.csv") for s in S]
    unc = [read_rows(E / f"exp1_uncond_seed{s}/raw/metrics.csv") for s in S]
    cmr = [read_rows(E / f"exp1_cond_seed{s}_mr/raw/metrics.csv") for s in S]
    umr = [read_rows(E / f"exp1_uncond_seed{s}_mr/raw/metrics.csv") for s in S]

    def col(runs, group, it, c):
        return np.array([pick(r, group, it, c) for r in runs])

    # instance identity: trace_post must be identical within a seed across the run families
    tp_c = np.array([pick(r, "train", 200000, "trace_post") for r in cond])
    tp_s = np.array([pick(r, "train", 1000000, "trace_post") for r in cos])
    tp_u = np.array([pick(r, "uncond", 200000, "trace_post") for r in unc])
    tp_cm = np.array([pick(r, "train", 200000, "trace_post") for r in cmr])
    tp_um = np.array([pick(r, "uncond", 200000, "trace_post") for r in umr])
    same_inst = bool(np.array_equal(tp_c, tp_s) and np.array_equal(tp_c, tp_u)
                     and np.array_equal(tp_c, tp_cm) and np.array_equal(tp_c, tp_um))
    say(f"trace_post identical per seed across cond / cosine / uncond / _mr runs: {same_inst}  {np.round(tp_c, 4)}")

    printed = {  # tab:exp1 as printed: (mean, sd, decimals)
        ("cond_trace", 100): (1.08, 0.02, 2), ("cond_trace", 10000): (1.03, 0.11, 2),
        ("cond_trace", 100000): (0.58, 0.18, 2), ("cond_trace", 200000): (0.396, 0.127, 3),
        ("cond_trace", 1000000): (0.120, 0.054, 3),
        ("vel_rel_err", 100): (0.78, 0.03, 2), ("vel_rel_err", 10000): (0.75, 0.07, 2),
        ("vel_rel_err", 100000): (0.50, 0.04, 2), ("vel_rel_err", 200000): (0.40, 0.05, 2),
        ("vel_rel_err", 1000000): (0.168, 0.052, 3),
        ("dist_atom", 100): (0.90, 0.16, 2), ("dist_atom", 10000): (0.87, 0.20, 2),
        ("dist_atom", 100000): (0.58, 0.13, 2), ("dist_atom", 200000): (0.38, 0.10, 2),
        ("dist_atom", 1000000): (0.137, 0.065, 3),
        ("dist_post", 100): (0.15, 0.06, 2), ("dist_post", 10000): (0.25, 0.07, 2),
        ("dist_post", 100000): (0.52, 0.10, 2), ("dist_post", 200000): (0.66, 0.18, 2),
        ("dist_post", 1000000): (0.816, 0.172, 3),
        ("uncond_trace", 100): (1.85, 0.55, 2), ("uncond_trace", 10000): (1.93, 0.16, 2),
        ("uncond_trace", 100000): (1.91, 0.17, 2), ("uncond_trace", 200000): (1.926, 0.171, 3),
        ("trace_post", 0): (1.018, 0.016, 3), ("trace_data", 0): (1.931, 0.162, 3),
        ("memratio_cond", 200000): (0.650, 0.033, 3), ("memratio_uncond", 200000): (0.389, 0.032, 3),
    }
    colname = {"cond_trace": "trace_cov_mean", "vel_rel_err": "vel_rel_err_mean_mean",
               "dist_atom": "mean_err_train_point_mean", "dist_post": "mean_err_post_mean"}
    cells = {}
    for (q, it), (pm, ps, dec) in printed.items():
        if q in colname:
            src = cos if it == 1000000 else cond
            v = col(src, "train", it, colname[q])
            srcname = "exp1_ext_sched_seed[0-4]" if it == 1000000 else "exp1_cond_seed[0-4]"
        elif q == "uncond_trace":
            v, srcname = col(unc, "uncond", it, "trace_cov_mean"), "exp1_uncond_seed[0-4]"
        elif q == "trace_post":
            v, srcname = tp_c, "exp1_cond_seed[0-4] (trace_post)"
        elif q == "trace_data":
            v, srcname = col(unc, "uncond", 200000, "trace_data"), "exp1_uncond_seed[0-4] (trace_data)"
        elif q == "memratio_cond":
            v, srcname = col(cmr, "train", it, "memorization_ratio_mean"), "exp1_cond_seed[0-4]_mr"
        else:
            v, srcname = col(umr, "uncond", it, "memorization_ratio_mean"), "exp1_uncond_seed[0-4]_mr"
        s = summ(v)
        s.update({"printed_mean": pm, "printed_sd": ps, "decimals": dec, "source": f"results/exp1/{srcname}/raw/metrics.csv",
                  "mean_ok": matches(s["mean"], pm, dec), "sd_pop_ok": matches(s["sd_pop"], ps, dec)})
        cells[f"{q}@{it}"] = s
    nbad = sum(not (c["mean_ok"] and c["sd_pop_ok"]) for c in cells.values())
    say(f"tab:exp1 + text: {len(cells)} cells; cells whose mean or population SD does NOT round to the printed value: {nbad}")
    say(f"{'cell':<26}{'printed':>16}{'mean':>9}{'sd_pop':>8}{'sd_samp':>8}  {'95% t-CI':>18}  {'exact boot CI':>18}")
    for k, c in cells.items():
        flag = "" if (c["mean_ok"] and c["sd_pop_ok"]) else "  <-- MISMATCH"
        say(f"{k:<26}{c['printed_mean']:>9}+-{c['printed_sd']:<5}{c['mean']:>9.4f}{c['sd_pop']:>8.4f}{c['sd_sample']:>8.4f}"
            f"  [{c['t_ci'][0]:.3f}, {c['t_ci'][1]:.3f}]  [{c['boot_ci'][0]:.3f}, {c['boot_ci'][1]:.3f}]{flag}")
    ratio_hw = [c["t_halfwidth"] / c["sd_pop"] for c in cells.values() if c["sd_pop"] > 0]
    say(f"t half-width / population SD: min {min(ratio_hw):.4f} max {max(ratio_hw):.4f} (theory t(0.975,4)/2 = {T4 / 2:.4f})")
    for k in ("cond_trace@200000", "cond_trace@1000000", "uncond_trace@200000"):
        c = cells[k]
        wt, wb = c["t_ci"][1] - c["t_ci"][0], c["boot_ci"][1] - c["boot_ci"][0]
        say(f"  {k}: bootstrap width / t width = {wb / wt:.3f} (narrower by {100 * (1 - wb / wt):.0f}%)")

    # ---- seed-paired contrasts
    tc2 = cells["cond_trace@200000"]["per_seed"]
    tc6 = cells["cond_trace@1000000"]["per_seed"]
    paired = {
        "trcov_over_trpost@2e5": np.array(tc2) / tp_c,
        "trcov_over_trpost@1e6cos": np.array(tc6) / tp_s,
        "cos1e6_minus_const2e5": np.array(tc6) - np.array(tc2),
        "uncond_trcov_over_trXhat@2e5": np.array(cells["uncond_trace@200000"]["per_seed"]) / np.array(cells["trace_data@0"]["per_seed"]),
        "memratio_cond_minus_uncond@2e5": np.array(cells["memratio_cond@200000"]["per_seed"]) - np.array(cells["memratio_uncond@200000"]["per_seed"]),
        "dist_atom_minus_post@1e5": col(cond, "train", 100000, colname["dist_atom"]) - col(cond, "train", 100000, colname["dist_post"]),
        "dist_atom_minus_post@2e5": col(cond, "train", 200000, colname["dist_atom"]) - col(cond, "train", 200000, colname["dist_post"]),
        "dist_atom_minus_post@1e6cos": col(cos, "train", 1000000, colname["dist_atom"]) - col(cos, "train", 1000000, colname["dist_post"]),
    }
    say("\nSeed-paired contrasts (mean, 95% t-CI df=4, exact bootstrap CI, per seed):")
    pc = {}
    for k, v in paired.items():
        s = summ(v)
        pc[k] = s
        say(f"  {k:<34} {s['mean']:+.4f}  t [{s['t_ci'][0]:+.3f}, {s['t_ci'][1]:+.3f}]  boot [{s['boot_ci'][0]:+.3f}, {s['boot_ci'][1]:+.3f}]"
            f"  seeds {np.round(v, 3).tolist()}")

    # ---- tab:p7kernel
    rows = read_rows(E / "_theory/raw/p7_kernel.csv")
    hs = sorted({float(r["h"]) for r in rows})
    p7_printed = {0.01: (0.583, 1.018, 0.673, 0.187, 1.308, 0.376, 0.66, 3.5),
                  0.05: (0.921, 1.018, 0.926, 0.169, 1.002, 0.050, 0.91, 13.6),
                  0.10: (1.004, 1.018, 1.001, 0.173, 0.994, 0.039, 0.98, 26.0),
                  0.50: (1.281, 1.018, 1.294, 0.166, 1.011, 0.022, 1.27, 101.5)}
    p7 = {}
    say("\ntab:p7kernel (results/exp1/_theory/raw/p7_kernel.csv):")
    nbad7 = 0
    for h in hs:
        rr = sorted([r for r in rows if float(r["h"]) == h], key=lambda r: int(r["seed"]))
        g = {c: np.array([float(r[c]) for r in rr]) for c in ("trace_meas", "trace_kernel", "trace_post", "ratio_to_kernel", "ratio_to_post", "n_eff")}
        pr = p7_printed[round(h, 2)]
        sr = summ(g["ratio_to_kernel"])
        sm = summ(g["trace_meas"])
        vals = [g["trace_kernel"].mean(), g["trace_post"].mean(), sm["mean"], sm["sd_pop"], sr["mean"], sr["sd_pop"],
                g["ratio_to_post"].mean(), g["n_eff"].mean()]
        decs = [3, 3, 3, 3, 3, 3, 2, 1]
        oks = [matches(v, p, d) for v, p, d in zip(vals, pr, decs)]
        nbad7 += sum(not o for o in oks)
        p7[str(h)] = {"seeds": [int(r["seed"]) for r in rr], "ratio_to_kernel": sr, "trace_meas": sm,
                      "trace_kernel_mean": float(g["trace_kernel"].mean()), "trace_post_mean": float(g["trace_post"].mean()),
                      "ratio_to_post_mean": float(g["ratio_to_post"].mean()),
                      "ratio_of_means_meas_over_post": float(g["trace_meas"].mean() / g["trace_post"].mean()),
                      "n_eff_mean": float(g["n_eff"].mean()), "printed": pr, "cells_ok": oks}
        say(f"  h={h:<5} ratio {sr['mean']:.4f} sd_pop {sr['sd_pop']:.4f} sd_samp {sr['sd_sample']:.4f}  t [{sr['t_ci'][0]:.3f}, {sr['t_ci'][1]:.3f}]"
            f"  boot [{sr['boot_ci'][0]:.3f}, {sr['boot_ci'][1]:.3f}]  per-seed {np.round(g['ratio_to_kernel'], 3).tolist()}  printed-cells ok {sum(oks)}/8")
    say(f"tab:p7kernel cells that do NOT round to the printed values: {nbad7} of {8 * len(hs)} checked (24 printed numeric cells + 8 SDs)")
    return {"same_instance_per_seed": same_inst, "cells": cells, "paired": pc, "p7kernel": p7,
            "n_mismatch_exp1": nbad, "n_mismatch_p7": nbad7, "t_quantile_df4": T4}


# ============================================================================= (2) CIFAR slopes
def ols(x, y):
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    s2 = float(e @ e) / (n - 2)
    se = math.sqrt(s2 * XtXi[1, 1])
    hdiag = np.einsum("ij,jk,ik->i", X, XtXi, X)
    meat = (X * (e ** 2 / (1 - hdiag) ** 2)[:, None]).T @ X
    se_hc3 = math.sqrt((XtXi @ meat @ XtXi)[1, 1])
    meat1 = (X * (e ** 2)[:, None]).T @ X
    se_hc1 = math.sqrt((XtXi @ meat1 @ XtXi)[1, 1] * n / (n - 2))
    r2 = 1 - float(e @ e) / float(((y - y.mean()) ** 2).sum())
    return {"slope": float(b[1]), "intercept": float(b[0]), "se": se, "se_hc3": se_hc3, "se_hc1": se_hc1, "r2": r2, "n": n}


def slope_only(x, y):
    xc = x - x.mean(axis=-1, keepdims=True)
    yc = y - y.mean(axis=-1, keepdims=True)
    return (xc * yc).sum(-1) / (xc * xc).sum(-1)


def case_boot(x, y, B, seed):
    rng = np.random.default_rng(seed)
    n = len(x)
    idx = rng.integers(0, n, size=(B, n))
    bs = slope_only(x[idx], y[idx])
    bs = bs[np.isfinite(bs)]
    th = slope_only(x, y)
    pct = np.percentile(bs, [2.5, 97.5])
    jk = np.array([slope_only(np.delete(x, i), np.delete(y, i)) for i in range(n)])
    d = jk.mean() - jk
    a = (d ** 3).sum() / (6 * ((d ** 2).sum()) ** 1.5)
    z0 = Phi_inv((bs < th).mean() + 0.5 * (bs == th).mean())
    lo = Phi(z0 + (z0 - Z) / (1 - a * (z0 - Z)))
    hi = Phi(z0 + (z0 + Z) / (1 - a * (z0 + Z)))
    bca = np.percentile(bs, [100 * lo, 100 * hi])
    return [float(v) for v in pct], [float(v) for v in bca], float(bs.std(ddof=1))


def load_reeval(path, h=None):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(rows, dict):
        rows = [rows]
    if h is not None:
        rows = [r for r in rows if float(r["h"]) == h]
    assert len(rows) == 1, (path, h, len(rows))
    r = rows[0]
    ref = np.asarray(r["trace_kernel_per_condition"], float)
    meas = np.asarray(r["ratio_per_condition"], float) * ref
    return r, ref, meas


def part2():
    say("\n" + "=" * 100)
    say("(2) CIFAR kernel tracking slopes")
    pub = R / "exp3/_cifar_ddpm/reeval.json"
    allrows = json.loads(pub.read_text(encoding="utf-8"))
    say(f"published file {pub}: runs = {[(r['run'], r['h'], r.get('n_conditions')) for r in allrows]}")
    t46 = t_ppf(0.975, 46)
    out = {"published": {}, "rerun": {}}
    printed = {4.0: (0.481, 0.037, 0.785, 4.57, 1.102), 5.0: (0.349, 0.049, 0.522, 2.16, 0.537), 6.0: (-0.156, 0.058, 0.135, 0.74, 0.208)}
    for h in (4.0, 5.0, 6.0):
        r, ref, meas = load_reeval(pub, h)
        ok = (ref > 0) & (meas > 0)
        x, y = np.log10(ref[ok]), np.log10(meas[ok])
        f = ols(x, y)
        tq = t_ppf(0.975, f["n"] - 2)
        f["ols_t_ci"] = [f["slope"] - tq * f["se"], f["slope"] + tq * f["se"]]
        f["hc3_t_ci"] = [f["slope"] - tq * f["se_hc3"], f["slope"] + tq * f["se_hc3"]]
        f["decades"] = float(np.ptp(x))
        f["ref_cv_ddof1"] = float(ref.std(ddof=1) / ref.mean())
        f["ref_cv_ddof0"] = float(ref.std(ddof=0) / ref.mean())
        f["n_used"] = int(ok.sum())
        f["run"] = r["run"]
        pct, bca, bsd = case_boot(x, y, 50000, 1234 + int(h))
        f["case_boot_pct"], f["case_boot_bca"], f["case_boot_sd"] = pct, bca, bsd
        # Monte Carlo spread of the endpoints at B=20000 (the other agent's B), 12 seeds
        mc = np.array([sum(case_boot(x, y, 20000, 9000 + s)[:2], []) for s in range(12)])
        f["case_boot_B20000_endpoint_range_over_12_seeds"] = {"pct_lo": [float(mc[:, 0].min()), float(mc[:, 0].max())],
                                                              "pct_hi": [float(mc[:, 1].min()), float(mc[:, 1].max())],
                                                              "bca_lo": [float(mc[:, 2].min()), float(mc[:, 2].max())],
                                                              "bca_hi": [float(mc[:, 3].min()), float(mc[:, 3].max())]}
        p = printed[h]
        f["printed"] = p
        f["printed_ok"] = [matches(f["slope"], p[0], 3), matches(f["se"], p[1], 3), matches(f["r2"], p[2], 3),
                           matches(f["decades"], p[3], 2), matches(f["ref_cv_ddof1"], p[4], 3)]
        out["published"][str(h)] = f
        say(f"  h={h:g} run={r['run']} n={f['n_used']}: slope {f['slope']:.4f} se {f['se']:.4f} HC3 {f['se_hc3']:.4f} R2 {f['r2']:.4f}"
            f" decades {f['decades']:.3f} CV {f['ref_cv_ddof1']:.3f}  OLS t-CI [{f['ols_t_ci'][0]:.3f}, {f['ols_t_ci'][1]:.3f}]"
            f"  HC3 t-CI [{f['hc3_t_ci'][0]:.3f}, {f['hc3_t_ci'][1]:.3f}]  case boot [{pct[0]:.3f}, {pct[1]:.3f}] BCa [{bca[0]:.3f}, {bca[1]:.3f}]"
            f"  printed-ok {f['printed_ok']}")
        mr = f["case_boot_B20000_endpoint_range_over_12_seeds"]
        say(f"      B=20000 endpoint ranges over 12 seeds: pct lo {np.round(mr['pct_lo'], 4).tolist()} hi {np.round(mr['pct_hi'], 4).tolist()}"
            f"  BCa lo {np.round(mr['bca_lo'], 4).tolist()} hi {np.round(mr['bca_hi'], 4).tolist()}")
    say(f"  t(0.975,46) = {t46:.6f}")

    # ---- re-runs: three instances per bandwidth
    rr = R / "exp3/_rerun"
    for h in (4, 5, 6):
        inst = []
        for s in (0, 1, 2):
            r, ref, meas = load_reeval(rr / f"reeval_exp3_cifar_heff_h{h}_s{s}/reeval.json")
            ok = (ref > 0) & (meas > 0)
            x, y = np.log10(ref[ok]), np.log10(meas[ok])
            f = ols(x, y)
            f["decades"] = float(np.ptp(x))
            f["run"] = r["run"]
            f["n_used"] = int(ok.sum())
            inst.append((x, y, f, ref))
        _, pref, pmeas = load_reeval(pub, float(h))
        same_ref_s0 = bool(np.allclose(inst[0][3], pref, rtol=1e-10, atol=0))
        same_ref_s1 = bool(len(inst[1][3]) == len(pref) and np.allclose(inst[1][3], pref, rtol=1e-6))
        slopes = np.array([f["slope"] for _, _, f, _ in inst])
        m, sd = slopes.mean(), slopes.std(ddof=1)
        tci = [m - T2 * sd / math.sqrt(3), m + T2 * sd / math.sqrt(3)]
        # pooled within-instance (fixed-effects) slope
        Sxy = np.array([((x - x.mean()) * (y - y.mean())).sum() for x, y, _, _ in inst])
        Sxx = np.array([((x - x.mean()) ** 2).sum() for x, y, _, _ in inst])
        bfe = Sxy.sum() / Sxx.sum()
        N = sum(len(x) for x, _, _, _ in inst)
        res = [(y - y.mean()) - bfe * (x - x.mean()) for x, y, _, _ in inst]
        s2 = sum((e ** 2).sum() for e in res) / (N - 3 - 1)
        se_fe = math.sqrt(s2 / Sxx.sum())
        G = 3
        scores = np.array([((x - x.mean()) * e).sum() for (x, _, _, _), e in zip(inst, res)])
        se_cr1 = math.sqrt(G / (G - 1) * (N - 1) / (N - 4) * (scores ** 2).sum() / Sxx.sum() ** 2)
        # exact cluster bootstrap over instances: 27 ordered resamples (FE estimator and pooled OLS)
        fe27, pool27 = [], []
        for trip in itertools.product(range(3), repeat=3):
            fe27.append(Sxy[list(trip)].sum() / Sxx[list(trip)].sum())
            xx = np.concatenate([inst[g][0] for g in trip]); yy = np.concatenate([inst[g][1] for g in trip])
            pool27.append(float(slope_only(xx, yy)))
        fe27, pool27 = np.array(fe27), np.array(pool27)
        # two-stage bootstrap: instances, then conditions within each drawn instance
        rng = np.random.default_rng(77 + h)
        B = 40000
        n_c = min(len(x) for x, _, _, _ in inst)
        assert all(len(x) == n_c for x, _, _, _ in inst)
        XS = np.stack([x for x, _, _, _ in inst]); YS = np.stack([y for _, y, _, _ in inst])
        gi = rng.integers(0, 3, size=(B, 3))
        ci = rng.integers(0, n_c, size=(B, 3, n_c))
        Xb, Yb = XS[gi[:, :, None], ci], YS[gi[:, :, None], ci]
        Xc, Yc = Xb - Xb.mean(-1, keepdims=True), Yb - Yb.mean(-1, keepdims=True)
        two = (Xc * Yc).sum((1, 2)) / (Xc * Xc).sum((1, 2))
        res_h = {"per_instance": [{"run": f["run"], "slope": f["slope"], "se": f["se"], "se_hc3": f["se_hc3"], "r2": f["r2"],
                                   "decades": f["decades"], "n": f["n_used"]} for _, _, f, _ in inst],
                 "s0_same_reference_as_published": same_ref_s0, "s1_same_reference_as_published": same_ref_s1,
                 "mean_slope": float(m), "sd_slope": float(sd), "t_ci_df2": tci,
                 "fe_slope": float(bfe), "fe_se_naive": se_fe, "fe_se_cr1": se_cr1,
                 "cluster_boot_exact_fe": [float(v) for v in np.percentile(fe27, [2.5, 97.5])],
                 "cluster_boot_exact_fe_distinct": int(len(np.unique(np.round(fe27, 12)))),
                 "cluster_boot_exact_pooled": [float(v) for v in np.percentile(pool27, [2.5, 97.5])],
                 "two_stage_boot": [float(v) for v in np.percentile(two, [2.5, 97.5])],
                 "published_minus_s0": float(out["published"][f"{float(h)}"]["slope"] - inst[0][2]["slope"])}
        res_h["published_minus_s0_in_ols_se"] = res_h["published_minus_s0"] / out["published"][f"{float(h)}"]["se"]
        se_pub = out["published"][f"{float(h)}"]["se"]
        res_h["published_minus_s0_in_se_of_difference"] = res_h["published_minus_s0"] / math.hypot(se_pub, inst[0][2]["se"])
        res_h["published_minus_s0_in_hc3_se_of_difference"] = res_h["published_minus_s0"] / math.hypot(
            out["published"][f"{float(h)}"]["se_hc3"], inst[0][2]["se_hc3"])
        out["rerun"][str(h)] = res_h
        say(f"  rerun h={h}: slopes {np.round(slopes, 4).tolist()} decades {[round(f['decades'], 2) for _, _, f, _ in inst]}"
            f"  s0 ref == published ref: {same_ref_s0}; s1 ref == published: {same_ref_s1}")
        say(f"     mean {m:.4f} t(df=2) [{tci[0]:.3f}, {tci[1]:.3f}]  FE slope {bfe:.4f} (naive se {se_fe:.4f}, CR1 se {se_cr1:.4f})"
            f"  exact cluster boot FE [{res_h['cluster_boot_exact_fe'][0]:.3f}, {res_h['cluster_boot_exact_fe'][1]:.3f}] ({res_h['cluster_boot_exact_fe_distinct']} distinct)"
            f"  pooled-OLS variant [{res_h['cluster_boot_exact_pooled'][0]:.3f}, {res_h['cluster_boot_exact_pooled'][1]:.3f}]"
            f"  two-stage [{res_h['two_stage_boot'][0]:.3f}, {res_h['two_stage_boot'][1]:.3f}]"
            f"  published - s0 = {res_h['published_minus_s0']:+.4f} ({res_h['published_minus_s0_in_ols_se']:.2f} OLS se;"
            f" {res_h['published_minus_s0_in_se_of_difference']:.2f} se of the difference; {res_h['published_minus_s0_in_hc3_se_of_difference']:.2f} HC3 se of diff)")
    # original-protocol seed1/seed2 runs: what do they contain?
    seedruns = {}
    for h in (4, 5, 6):
        for s in (1, 2):
            d = R / f"exp3/exp3_cifar_ddpm_h{h}_seed{s}"
            files = sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())
            seedruns[d.name] = files
    say(f"  original-protocol seed1/2 run contents (files): { {k: [f for f in v if not f.endswith('.png')] for k, v in seedruns.items()} }")
    out["seed_runs_files"] = seedruns
    return out


# ============================================================================= (3) EDM AUC
def psi_matrix(pos, neg):
    return (pos[:, None] > neg[None, :]).astype(float) + 0.5 * (pos[:, None] == neg[None, :])


def auc(pos, neg):
    return float(psi_matrix(pos, neg).mean())


def delong(pos_list, neg_list):
    """DeLong variances/covariances for one or more scores evaluated on the same samples."""
    V10, V01, A = [], [], []
    for p, n in zip(pos_list, neg_list):
        P = psi_matrix(p, n)
        V10.append(P.mean(1)); V01.append(P.mean(0)); A.append(P.mean())
    V10, V01 = np.array(V10), np.array(V01)
    S10 = np.atleast_2d(np.cov(V10)); S01 = np.atleast_2d(np.cov(V01))
    S = S10 / V10.shape[1] + S01 / V01.shape[1]
    return np.array(A), S


def weighted_auc_boot(P, Wpos, Wneg):
    """AUC for weight vectors (counts) over positives and negatives; P is the psi matrix."""
    num = ((Wpos @ P) * Wneg).sum(1)
    return num / (Wpos.sum(1) * Wneg.sum(1))


def late_C(z):
    rho = z["err"] / z["n1"]
    sg = z["sigma"]
    inc = (1 - 0.5 * (rho[:, :-1] + rho[:, 1:])) * np.log(sg[:-1] / sg[1:])
    return inc[:, 11:17].sum(1)


def late_C_direct(z):
    """Same integral written independently: trapezoid of (1 - rho) over u = log(1/sigma) on [sigma_17, sigma_11]."""
    rho = z["err"] / z["n1"]
    u = np.log(1 / z["sigma"])
    f = 1 - rho
    return np.trapezoid(f[:, 11:18], u[11:18], axis=1)


def sep_lcb(n_on, m_off, alpha=0.05):
    """Distribution-free one-sided lower confidence bound for theta=P(off>on) after complete separation.
    P(sep) <= w^n + (theta/w)^m for every w (continuous laws); bound = sup_w w * (alpha - w^n)^(1/m)."""
    w = np.linspace(1e-6, alpha ** (1 / n_on) - 1e-12, 2_000_001)
    th = w * (alpha - w ** n_on) ** (1 / m_off)
    return float(th.max()), float(alpha ** (1 / m_off))


def edm_model(name, path, base_path=None):
    z = np.load(path)
    zb = np.load(base_path) if base_path else z
    off = z["d1"] / z["d2"] >= 1 / 3
    on = ~off
    sg = z["sigma"]
    C = late_C(z)
    C2 = late_C_direct(z)
    assert np.allclose(C, C2, rtol=1e-10, atol=1e-12), np.abs(C - C2).max()
    res = {"file": str(path), "baseline_file": str(base_path or path), "n": int(len(off)), "n_off": int(off.sum()),
           "sigma_11": float(sg[11]), "sigma_17": float(sg[17]),
           "C_on_median": float(np.median(C[on])), "C_off_median": float(np.median(C[off]))}
    off_b = zb["d1"] / zb["d2"] >= 1 / 3
    res["baseline_off_flags_identical"] = bool(np.array_equal(off_b, off))
    if base_path:
        Cb = late_C(zb)
        res["C_maxabsdiff_vs_baseline_file"] = float(np.abs(Cb - C).max())
        res["d1_maxreldiff_vs_baseline_file"] = float(np.abs(zb["d1"] / z["d1"] - 1).max())
        res["labels_identical"] = bool(np.array_equal(zb["label"], z["label"]))
    sC = -C
    sB = zb["dD"][:, 17]
    a_C, a_B = auc(sC[off], sC[on]), auc(sB[off], sB[on])
    res["auc_C"], res["auc_baseline_dD_end"] = a_C, a_B
    res["auc_rho_end"] = auc((z["err"] / z["n1"])[off, 17], (z["err"] / z["n1"])[on, 17])
    res["auc_rho_0585"] = auc((z["err"] / z["n1"])[off, 11], (z["err"] / z["n1"])[on, 11])
    res["complete_separation"] = bool(C[off].max() < C[on].min())
    res["C_off_max"], res["C_on_min"] = float(C[off].max()), float(C[on].min())
    # DeLong
    A, S = delong([sC[off], sB[off]], [sC[on], sB[on]])
    se_C, se_B = math.sqrt(S[0, 0]), math.sqrt(S[1, 1])
    se_d = math.sqrt(max(S[0, 0] + S[1, 1] - 2 * S[0, 1], 0))
    res["delong_C"] = [a_C - Z * se_C, a_C + Z * se_C]
    res["delong_baseline"] = [a_B - Z * se_B, a_B + Z * se_B]
    res["delong_diff"] = [a_C - a_B - Z * se_d, a_C - a_B + Z * se_d]
    # stratified bootstrap (paired)
    P_C, P_B = psi_matrix(sC[off], sC[on]), psi_matrix(sB[off], sB[on])
    m, n = int(off.sum()), int(on.sum())
    rng = np.random.default_rng(2026)
    B = 20000
    Wp = rng.multinomial(m, np.full(m, 1 / m), size=B).astype(float)
    Wn = rng.multinomial(n, np.full(n, 1 / n), size=B).astype(float)
    bC, bB = weighted_auc_boot(P_C, Wp, Wn), weighted_auc_boot(P_B, Wp, Wn)
    res["strat_boot_C"] = [float(v) for v in np.percentile(bC, [2.5, 97.5])]
    res["strat_boot_baseline"] = [float(v) for v in np.percentile(bB, [2.5, 97.5])]
    res["strat_boot_diff"] = [float(v) for v in np.percentile(bC - bB, [2.5, 97.5])]
    res["diff_C_minus_baseline"] = a_C - a_B
    # class-cluster bootstrap (10 classes) and endpoint-image-cluster bootstrap
    lab = z["label"].astype(int)
    classes = np.unique(lab)
    rng = np.random.default_rng(7)
    Bc = 10000
    cnt = rng.multinomial(len(classes), np.full(len(classes), 1 / len(classes)), size=Bc).astype(float)
    w = cnt[:, np.searchsorted(classes, lab)]
    keep = (w[:, off].sum(1) > 0) & (w[:, on].sum(1) > 0)
    bcl = weighted_auc_boot(P_C, w[keep][:, off], w[keep][:, on])
    res["class_cluster_boot_C"] = [float(v) for v in np.percentile(bcl, [2.5, 97.5])]
    if "nn1" in zb.files:
        key = lab * 100000 + zb["nn1"].astype(int)
        uk, inv = np.unique(key, return_inverse=True)
        rng = np.random.default_rng(8)
        cnt = rng.multinomial(len(uk), np.full(len(uk), 1 / len(uk)), size=Bc).astype(float)
        w = cnt[:, inv]
        keep = (w[:, off].sum(1) > 0) & (w[:, on].sum(1) > 0)
        bim = weighted_auc_boot(P_C, w[keep][:, off], w[keep][:, on])
        res["image_cluster_boot_C"] = [float(v) for v in np.percentile(bim, [2.5, 97.5])]
        res["n_image_clusters"] = int(len(uk))
        res["nn1_source"] = str(base_path or path)
    if res["complete_separation"]:
        lcb, cap = sep_lcb(n, m)
        res["sep_lower_bound_95"], res["sep_lower_bound_cap_alpha_1_over_m"] = lcb, cap
    # late contraction with the PREDICTIVE anchor (rhoA = err / |x - nearest image of D(x_k)|): no endpoint anchor
    if "rhoA" in zb.files:
        rA = zb["rhoA"]
        incA = (1 - 0.5 * (rA[:, :-1] + rA[:, 1:])) * np.log(sg[:-1] / sg[1:])
        CA = incA[:, 11:17].sum(1)
        res["auc_C_predictive_anchor"] = auc(-CA[off], -CA[on])
        res["C_predictive_minus_endpoint_max_abs"] = float(np.abs(CA - (late_C(zb))).max())
        res["frac_anchor_eq_endpoint_nn_at_k11_to_17"] = (
            float((zb["anc"][:, 11:18] == zb["nn1"][:, None]).all(1).mean()) if "nn1" in zb.files else None)
        # remaining entries of late_contraction_bootstrap.json: radial ratio and baseline at sigma 19.4 and 12.9
        rng = np.random.default_rng(99)
        Wp = rng.multinomial(m, np.full(m, 1 / m), size=10000).astype(float)
        Wn = rng.multinomial(n, np.full(n, 1 / n), size=10000).astype(float)
        for tag, target in (("194", 19.4), ("129", 12.9)):
            i = int(np.argmin(np.abs(sg - target)))
            Pr, Pn = psi_matrix(zb["radA"][off, i], zb["radA"][on, i]), psi_matrix(zb["dD"][off, i], zb["dD"][on, i])
            br, bn = weighted_auc_boot(Pr, Wp, Wn), weighted_auc_boot(Pn, Wp, Wn)
            res[f"rad{tag}"] = [float(Pr.mean())] + [float(v) for v in np.percentile(br, [2.5, 97.5])]
            res[f"nn{tag}"] = [float(Pn.mean())] + [float(v) for v in np.percentile(bn, [2.5, 97.5])]
            res[f"rad{tag}-nn{tag}"] = [float(Pr.mean() - Pn.mean())] + [float(v) for v in np.percentile(br - bn, [2.5, 97.5])]
            res[f"sigma_index_{tag}"] = [i, float(sg[i])]
    return res


def part3():
    say("\n" + "=" * 100)
    say("(3) EDM late contraction AUC")
    models = {
        "sub2000": (R / "n3_rho2_20261118/sub2000/q_per_sample.npz", None),
        "sub500s1": (R / "n3_rho2_20261118/sub500s1/q_per_sample.npz", None),
        "sub500s0": (R / "n3_rho_20261117/sub500/q_per_sample.npz", R / "n3_anchor_20261117/sub500/q_per_sample.npz"),
        "sub500s0_anchorfile": (R / "n3_anchor_20261117/sub500/q_per_sample.npz", None),
    }
    out = {}
    for k, (p, b) in models.items():
        res = edm_model(k, p, b)
        out[k] = res
        say(f"  {k}: n_off={res['n_off']} sigma[11]={res['sigma_11']:.4f} sigma[17]={res['sigma_17']:.4f}"
            f"  C medians on {res['C_on_median']:.3f} / off {res['C_off_median']:.3f}")
        say(f"     AUC(C)={res['auc_C']:.5f}  strat boot [{res['strat_boot_C'][0]:.4f}, {res['strat_boot_C'][1]:.4f}]"
            f"  DeLong [{res['delong_C'][0]:.4f}, {res['delong_C'][1]:.4f}]  class-cluster [{res['class_cluster_boot_C'][0]:.4f}, {res['class_cluster_boot_C'][1]:.4f}]"
            + (f"  image-cluster [{res['image_cluster_boot_C'][0]:.4f}, {res['image_cluster_boot_C'][1]:.4f}] ({res['n_image_clusters']} clusters)" if "image_cluster_boot_C" in res else ""))
        say(f"     baseline dD(sigma=0.002) AUC={res['auc_baseline_dD_end']:.5f} boot [{res['strat_boot_baseline'][0]:.4f}, {res['strat_boot_baseline'][1]:.4f}]"
            f"  diff {res['diff_C_minus_baseline']:+.5f} boot [{res['strat_boot_diff'][0]:+.5f}, {res['strat_boot_diff'][1]:+.5f}]"
            f" DeLong [{res['delong_diff'][0]:+.5f}, {res['delong_diff'][1]:+.5f}]")
        say(f"     AUC rho(0.002)={res['auc_rho_end']:.4f}  AUC rho(0.585)={res['auc_rho_0585']:.4f}  complete separation: {res['complete_separation']}"
            f" (max C_off {res['C_off_max']:.4f}, min C_on {res['C_on_min']:.4f})"
            + (f"  95% distribution-free LCB {res['sep_lower_bound_95']:.4f} (cap alpha^(1/m) {res['sep_lower_bound_cap_alpha_1_over_m']:.4f})" if res['complete_separation'] else ""))
        if b:
            say(f"     baseline file {b}: off flags identical {res['baseline_off_flags_identical']}, labels identical {res.get('labels_identical')},"
                f" max |C diff| {res['C_maxabsdiff_vs_baseline_file']:.4f}, max rel d1 diff {res['d1_maxreldiff_vs_baseline_file']:.2e}")
        if "auc_C_predictive_anchor" in res:
            say(f"     predictive-anchor late contraction AUC {res['auc_C_predictive_anchor']:.5f} (max |C_A - C| {res['C_predictive_minus_endpoint_max_abs']:.4f};"
                f" share with anchor == endpoint image at all k>=11: {res['frac_anchor_eq_endpoint_nn_at_k11_to_17']})")
            say(f"     rad194 {np.round(res['rad194'], 3).tolist()} nn194 {np.round(res['nn194'], 3).tolist()} diff {np.round(res['rad194-nn194'], 3).tolist()}"
                f" | rad129 {np.round(res['rad129'], 3).tolist()} nn129 {np.round(res['nn129'], 3).tolist()} diff {np.round(res['rad129-nn129'], 3).tolist()}")
    js = json.loads((R / "n3_rho2_20261118/late_contraction_bootstrap.json").read_text(encoding="utf-8"))
    out["late_contraction_bootstrap_json"] = js
    for k in ("sub2000", "sub500s1", "sub500s0"):
        j = js[k]
        say(f"  JSON {k}: C {j['C']} nn_end {j['nn_end']} C-nn_end {j['C-nn_end']} rho_end {j['rho_end']} rho059 {j['rho059']}"
            f" medians {j['C_on_med']}/{j['C_off_med']} n_off {j['n_off']}")
    return out


def main():
    res = {"part1_exp1": part1(), "part2_cifar": part2(), "part3_edm": part3()}
    OUT.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return conv(o.tolist())
        return o
    (OUT / "verify.json").write_text(json.dumps(conv(res), indent=1), encoding="utf-8")
    (OUT / "stdout.txt").write_text(LOG.getvalue(), encoding="utf-8")
    say(f"\nwrote {OUT / 'verify.json'} and {OUT / 'stdout.txt'}")


if __name__ == "__main__":
    sys.exit(main())
