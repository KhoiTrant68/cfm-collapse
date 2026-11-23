# -*- coding: utf-8 -*-
"""Paper B, uncertainty: confidence intervals instead of population SDs, clustered slopes, AUC intervals.

Reviewers objected that the paper reports mean +- population SD over five seeds (denominator n) instead of
confidence intervals, and OLS standard errors for a log-log slope that ignore clustering by instance. Every
number below is recomputed from saved result files. The values the paper prints are typed in only to be
compared against.

1. EXP-1 (Section sec:exp1, Tables tab:exp1 and tab:p7kernel). Sources as in scripts/make_results_figures.py
   (EXP1 = results/exp1, seed_mean), scripts/analyze_memorization_ratio.py and scripts/analyze_p7_kernel.py.
   For every reported mean: (a) the sample SD (ddof=1); (b) the 95% Student-t interval for the mean (n=5,
   df=4); (c) the seed-bootstrap percentile interval, computed exactly by enumerating all 5^5 = 3125
   equally likely resamples of the five seeds. Seed-paired contrasts are added for comparisons the text makes
   on the same five instances (the cond, uncond and cosine runs of one seed share the instance).
2. CIFAR-10 kernel tracking (Table tab:cifarddpm; fig_kernel in scripts/make_results_figures.py). The published
   slope comes from results/exp3/_cifar_ddpm/reeval.json, whose 48 conditions all belong to ONE instance
   (run exp3_cifar_ddpm_h*, seed 0), so clustering cannot be assessed from that file: we give HC3 and
   case-bootstrap intervals. The re-trained runs in results/exp3/_rerun/ (three instances, 48 conditions
   each; s0 is the published instance re-trained) do allow it: per-instance slopes, a t-interval over
   instances (df=2), a pooled within-instance slope with an instance (cluster) bootstrap and a two-stage
   bootstrap (instances, then conditions within instances).
3. EDM AUCs (Section sec:edm, Table tab:edm-models, Table tab:edm-rho). The late contraction
   C = sum_{k=11}^{16} (1 - (rho_k + rho_{k+1})/2) log(sigma_k/sigma_{k+1}), rho = err/n1, exactly as in
   fig_clocks of scripts/make_edm_figures.py, and the nearest-image baseline dD, recomputed from the per-sample
   files with stratified-bootstrap (B=10000) and DeLong intervals and a class-cluster bootstrap. Where the two
   groups are completely separated the percentile bootstrap returns the degenerate interval [1, 1]; there we
   give a distribution-free one-sided 95% lower confidence bound for the AUC.

    PYTHONPATH=. uv run --no-sync python -m scripts.kernel_tracking_uncertainty

numpy only (no scipy, no torch, no pandas). Writes results/paperB_20261121/uncertainty/.
"""
from __future__ import annotations

import csv
import glob
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np

OUT = Path("results/paperB_20261121/uncertainty")
SEED = 20261121
B_SLOPE = 20000
B_AUC = 10000
ALPHA = 0.05


# ============================================================================ distributions (numpy only)
def _t_cdf_pos(t: float, df: int) -> float:
    """P(T <= t) for t >= 0: Simpson integration of the Student-t density on [0, t]."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    xs = np.linspace(0.0, t, 40001)
    f = c * (1.0 + xs ** 2 / df) ** (-(df + 1) / 2)
    h = xs[1] - xs[0]
    return 0.5 + h / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())


def t_ppf(p: float, df: int) -> float:
    lo, hi = 0.0, 100.0
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if _t_cdf_pos(mid, df) < p else (lo, mid)
    return 0.5 * (lo + hi)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if norm_cdf(mid) < p else (lo, mid)
    return 0.5 * (lo + hi)


KNOWN_T975 = {1: 12.706204736174698, 2: 4.302652729749464, 4: 2.7764451051977987}
_TQ: dict[int, float] = {}


def tq(df: int) -> float:
    if df not in _TQ:
        _TQ[df] = t_ppf(0.975, df)
    return _TQ[df]


Z975 = norm_ppf(0.975)


# ============================================================================ small helpers
def rel(p) -> str:
    return Path(p).as_posix()


def fnum(x: float, d: int) -> str:
    s = f"{x:.{d}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def cell(m: float, lo: float, hi: float, d: int) -> str:
    """Paper style of tab:cifarddpm: $m$\\,[$lo$, $hi$]."""
    return f"${fnum(m, d)}$\\,[${fnum(lo, d)}$, ${fnum(hi, d)}$]"


def parse_pm(s: str):
    """'0.396±0.127' -> (0.396, 0.127, 3, 3); '0.583' -> (0.583, None, 3, None)."""
    if "±" in s:
        a, b = s.split("±")
        return float(a), float(b), len(a.split(".")[1]) if "." in a else 0, len(b.split(".")[1]) if "." in b else 0
    return float(s), None, len(s.split(".")[1]) if "." in s else 0, None


def matches(value: float, paper: float, d: int) -> bool:
    return abs(round(value, d) - paper) < 0.5 * 10 ** (-d) + 1e-12


def seed_summary(v) -> dict:
    """Mean, population SD (as printed), sample SD, t-interval (df=n-1), exact seed-bootstrap interval."""
    v = np.asarray(v, float)
    n = v.size
    m, sdp, sd = float(v.mean()), float(v.std(ddof=0)), float(v.std(ddof=1))
    se = sd / math.sqrt(n)
    tc = tq(n - 1)
    idx = np.array(list(itertools.product(range(n), repeat=n)))      # all n^n equally likely resamples
    bm = v[idx].mean(1)
    blo, bhi = (float(q) for q in np.percentile(bm, [2.5, 97.5]))
    return {"n": int(n), "values": [float(x) for x in v], "mean": m, "sd_pop": sdp, "sd_sample": sd,
            "se": se, "t_crit": tc, "t_lo": m - tc * se, "t_hi": m + tc * se, "boot_lo": blo,
            "boot_hi": bhi, "boot_resamples": int(len(bm))}


# ============================================================================ 1. EXP-1
EXP1 = Path("results/exp1")
PAT = {"cond": f"{EXP1.as_posix()}/exp1_cond_seed[0-4]/raw/metrics.csv",
       "cos": f"{EXP1.as_posix()}/exp1_ext_sched_seed[0-4]/raw/metrics.csv",
       "uncond": f"{EXP1.as_posix()}/exp1_uncond_seed[0-4]/raw/metrics.csv",
       "cond_mr": f"{EXP1.as_posix()}/exp1_cond_seed[0-4]_mr/raw/metrics.csv",
       "uncond_mr": f"{EXP1.as_posix()}/exp1_uncond_seed[0-4]_mr/raw/metrics.csv"}
P7_CSV = EXP1 / "_theory" / "raw" / "p7_kernel.csv"
ITERS = (100, 10000, 100000, 200000, 1000000)

# Table tab:exp1 as printed (mean ± population SD); the 10^6 column is the cosine-schedule run.
TAB_EXP1 = [
    ("cond_trcov", r"conditional $\tr\Cov$", "trace_cov_mean", "train",
     {100: "1.08±0.02", 10000: "1.03±0.11", 100000: "0.58±0.18", 200000: "0.396±0.127", 1000000: "0.120±0.054"}),
    ("vel_relerr", r"velocity rel.\ error vs.\ ($\star$)", "vel_rel_err_mean_mean", "train",
     {100: "0.78±0.03", 10000: "0.75±0.07", 100000: "0.50±0.04", 200000: "0.40±0.05", 1000000: "0.168±0.052"}),
    ("mean_to_atom", r"$\|\text{mean}-x^i\|$", "mean_err_train_point_mean", "train",
     {100: "0.90±0.16", 10000: "0.87±0.20", 100000: "0.58±0.13", 200000: "0.38±0.10", 1000000: "0.137±0.065"}),
    ("mean_to_post", r"$\|\text{mean}-\mu_{\mathrm{post}}\|$", "mean_err_post_mean", "train",
     {100: "0.15±0.06", 10000: "0.25±0.07", 100000: "0.52±0.10", 200000: "0.66±0.18", 1000000: "0.816±0.172"}),
    ("uncond_trcov", r"unconditional $\tr\Cov$", "trace_cov_mean", "uncond",
     {100: "1.85±0.55", 10000: "1.93±0.16", 100000: "1.91±0.17", 200000: "1.926±0.171"}),
]
# Reference values in the caption of tab:exp1 and the text of sec:exp1.
REFS = [
    ("trace_post", r"$\tr\Sigmapost$", "cond", "train", "trace_post", 200000, "1.018±0.016"),
    ("trace_data", r"$\tr\Xhat$", "uncond", "uncond", "trace_data", 200000, "1.931±0.162"),
    ("memratio_cond", "memorisation ratio, conditional", "cond_mr", "train", "memorization_ratio_mean", 200000,
     "0.650±0.033"),
    ("memratio_uncond", "memorisation ratio, unconditional", "uncond_mr", "uncond", "memorization_ratio_mean",
     200000, "0.389±0.032"),
]
P7_PAPER = {
    0.01: {"trace_kernel": "0.583", "trace_post": "1.018", "trace_meas": "0.673±0.187",
           "ratio_to_kernel": "1.308±0.376", "ratio_to_post": "0.66", "n_eff": "3.5"},
    0.05: {"trace_kernel": "0.921", "trace_post": "1.018", "trace_meas": "0.926±0.169",
           "ratio_to_kernel": "1.002±0.050", "ratio_to_post": "0.91", "n_eff": "13.6"},
    0.1: {"trace_kernel": "1.004", "trace_post": "1.018", "trace_meas": "1.001±0.173",
          "ratio_to_kernel": "0.994±0.039", "ratio_to_post": "0.98", "n_eff": "26.0"},
    0.5: {"trace_kernel": "1.281", "trace_post": "1.018", "trace_meas": "1.294±0.166",
          "ratio_to_kernel": "1.011±0.022", "ratio_to_post": "1.27", "n_eff": "101.5"},
}


def _csv_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def per_seed(key: str, group: str, col: str, it: int):
    files = sorted(glob.glob(PAT[key]))
    assert len(files) == 5, (PAT[key], files)
    vals, seeds = [], []
    for f in files:
        rows = [r for r in _csv_rows(f) if r["group"] == group and int(float(r["iter"])) == it]
        assert len(rows) == 1, (f, group, it, len(rows))
        vals.append(float(rows[0][col]))
        seeds.append(int(re.search(r"seed(\d)", f).group(1)))
    assert seeds == [0, 1, 2, 3, 4], seeds
    return np.array(vals)


def _entry(paper: str, s: dict, source: str) -> dict:
    pm, ppm, d, dpm = parse_pm(paper)
    e = dict(s)
    e.update({"source": source, "paper": paper, "paper_mean": pm, "paper_pm": ppm, "decimals": d,
              "mean_matches_paper": matches(s["mean"], pm, d),
              "sd_pop_matches_paper": None if ppm is None else matches(s["sd_pop"], ppm, dpm)})
    return e


def part1_exp1() -> dict:
    res = {"tab_exp1": [], "refs": [], "p7kernel": [], "contrasts": []}
    for key, label, col, group, cells in TAB_EXP1:
        for it, paper in cells.items():
            pk = "cos" if it == 1000000 else ("uncond" if group == "uncond" else "cond")
            v = per_seed(pk, group, col, it)
            src = f"{PAT[pk]} (group={group}, column={col}, iter={it})"
            e = _entry(paper, seed_summary(v), src)
            e.update({"row": key, "label": label, "iter": it})
            res["tab_exp1"].append(e)
    for key, label, pk, group, col, it, paper in REFS:
        v = per_seed(pk, group, col, it)
        e = _entry(paper, seed_summary(v), f"{PAT[pk]} (group={group}, column={col}, iter={it})")
        e.update({"row": key, "label": label, "iter": it})
        res["refs"].append(e)

    rows = _csv_rows(P7_CSV)
    for h, paper in P7_PAPER.items():
        rh = sorted((r for r in rows if abs(float(r["h"]) - h) < 1e-12), key=lambda r: int(r["seed"]))
        assert [int(r["seed"]) for r in rh] == [0, 1, 2, 3, 4], h
        for col, ps in paper.items():
            v = np.array([float(r[col]) for r in rh])
            e = _entry(ps, seed_summary(v), f"{rel(P7_CSV)} (h={h}, column={col}, seeds 0-4)")
            e.update({"h": h, "column": col})
            if col == "ratio_to_kernel":
                e["t_interval_covers_1"] = bool(e["t_lo"] <= 1.0 <= e["t_hi"])
            res["p7kernel"].append(e)

    # seed-paired contrasts on the same five instances (new; not in the paper)
    post = per_seed("cond", "train", "trace_post", 200000)
    data = per_seed("uncond", "uncond", "trace_data", 200000)
    con = {
        "cond tr Cov / tr Sigma_post at 2e5 (constant lr)":
            (per_seed("cond", "train", "trace_cov_mean", 200000) / post, "cond trace_cov_mean / trace_post"),
        "cond tr Cov / tr Sigma_post at 1e6 (cosine)":
            (per_seed("cos", "train", "trace_cov_mean", 1000000) / post, "cos trace_cov_mean / cond trace_post"),
        "uncond tr Cov / tr Xhat at 2e5":
            (per_seed("uncond", "uncond", "trace_cov_mean", 200000) / data, "uncond trace_cov_mean / trace_data"),
        "memorisation ratio, cond - uncond at 2e5":
            (per_seed("cond_mr", "train", "memorization_ratio_mean", 200000)
             - per_seed("uncond_mr", "uncond", "memorization_ratio_mean", 200000), "cond_mr - uncond_mr"),
        "|mean - x^i| - |mean - mu_post| at 1e5":
            (per_seed("cond", "train", "mean_err_train_point_mean", 100000)
             - per_seed("cond", "train", "mean_err_post_mean", 100000), "cond, both columns at iter 100000"),
        "|mean - x^i| - |mean - mu_post| at 2e5":
            (per_seed("cond", "train", "mean_err_train_point_mean", 200000)
             - per_seed("cond", "train", "mean_err_post_mean", 200000), "cond, both columns at iter 200000"),
        "|mean - x^i| - |mean - mu_post| at 1e6 (cosine)":
            (per_seed("cos", "train", "mean_err_train_point_mean", 1000000)
             - per_seed("cos", "train", "mean_err_post_mean", 1000000), "cos, both columns at iter 1000000"),
        "cond tr Cov at 1e6 (cosine) - at 2e5 (constant lr)":
            (per_seed("cos", "train", "trace_cov_mean", 1000000)
             - per_seed("cond", "train", "trace_cov_mean", 200000), "cos - cond trace_cov_mean"),
    }
    for name, (v, how) in con.items():
        s = seed_summary(v)
        s.update({"contrast": name, "how": how})
        res["contrasts"].append(s)
    return res


def exp1_tables(r: dict) -> list[str]:
    L = ["% ---------------------------------------------------------------------------",
         "% Revised Table tab:exp1: mean and 95% Student-t interval for the mean over the five seeds",
         "% (n=5, df=4, t=2.776). Generated by scripts/kernel_tracking_uncertainty.py; do not edit.",
         r"\begin{tabular}{lccccc}", r"\toprule", r"& \multicolumn{5}{c}{iteration}\\", r"\cmidrule(l){2-6}",
         r"quantity & $10^2$ & $10^4$ & $10^5$ & $2\times10^5$ & $1\times10^6$ \\", r"\midrule"]
    for key, label, *_ in TAB_EXP1:
        cells = []
        for it in ITERS:
            e = next((x for x in r["tab_exp1"] if x["row"] == key and x["iter"] == it), None)
            cells.append("---" if e is None else cell(e["mean"], e["t_lo"], e["t_hi"], e["decimals"]))
        L.append(f"{label} & " + " & ".join(cells) + r"\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    ref = {e["row"]: e for e in r["refs"]}
    L.append("% caption: EXP-1 at $h=0$, five seeds: mean and 95\\% Student-$t$ interval for the mean (4 degrees "
             "of freedom). Reference values: $\\tr\\Sigmapost=" + cell(ref["trace_post"]["mean"], ref["trace_post"]["t_lo"],
             ref["trace_post"]["t_hi"], 3).replace("$", "") + "$ and $\\tr\\Xhat=" + cell(ref["trace_data"]["mean"],
             ref["trace_data"]["t_lo"], ref["trace_data"]["t_hi"], 3).replace("$", "") + "$.")
    L += ["", "% ---------------------------------------------------------------------------",
          "% Revised Table tab:p7kernel: generated tr Cov and ratio to tr Cov_h as mean and 95% t-interval (df=4).",
          r"\begin{tabular}{lcccccc}", r"\toprule",
          r"$h$ & $\tr\Covh$ & $\tr\Sigmapost$ & generated $\tr\Cov$ & ratio to $\tr\Covh$ & ratio to $\tr\Sigmapost$ & $n_{\mathrm{eff}}$\\",
          r"\midrule"]
    for h in P7_PAPER:
        g = {e["column"]: e for e in r["p7kernel"] if e["h"] == h}
        L.append(f"{h:.2f} & {fnum(g['trace_kernel']['mean'], 3)} & {fnum(g['trace_post']['mean'], 3)} & "
                 f"{cell(g['trace_meas']['mean'], g['trace_meas']['t_lo'], g['trace_meas']['t_hi'], 3)} & "
                 f"{cell(g['ratio_to_kernel']['mean'], g['ratio_to_kernel']['t_lo'], g['ratio_to_kernel']['t_hi'], 3)} & "
                 f"{fnum(g['ratio_to_post']['mean'], 2)} & {fnum(g['n_eff']['mean'], 1)}\\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    return L


# ============================================================================ 2. CIFAR-10 slopes
EXP3 = Path("results/exp3")
REEVAL = EXP3 / "_cifar_ddpm" / "reeval.json"
RERUN = EXP3 / "_rerun"
PAPER_SLOPE = {4: ("0.481", "0.037", "0.785", "4.57"), 5: ("0.349", "0.049", "0.522", "2.16"),
               6: ("-0.156", "0.058", "0.135", "0.74")}


def ols(x, y) -> dict:
    n = x.size
    xm, ym = x.mean(), y.mean()
    xc, yc = x - xm, y - ym
    sxx = float((xc * xc).sum())
    b = float((xc * yc).sum() / sxx)
    a = float(ym - b * xm)
    e = y - a - b * x
    ssr, sst = float((e * e).sum()), float((yc * yc).sum())
    hii = 1.0 / n + xc * xc / sxx
    se_hc3 = math.sqrt(float((xc * xc * e * e / (1 - hii) ** 2).sum())) / sxx
    return {"slope": b, "intercept": a, "se_ols": math.sqrt(ssr / (n - 2) / sxx), "se_hc3": se_hc3,
            "r2": 1 - ssr / sst, "n": int(n), "decades": float(np.ptp(x))}


def boot_slopes(x, y, B, rng):
    idx = rng.integers(0, x.size, (B, x.size))
    X, Y = x[idx], y[idx]
    Xc, Yc = X - X.mean(1, keepdims=True), Y - Y.mean(1, keepdims=True)
    return (Xc * Yc).sum(1) / (Xc * Xc).sum(1)


def bca(est, boot, jack, alpha=ALPHA):
    z0 = norm_ppf(float(np.mean(boot < est)) + 0.5 * float(np.mean(boot == est)))
    d = jack.mean() - jack
    a = float((d ** 3).sum() / (6 * ((d ** 2).sum()) ** 1.5))
    qs = []
    for q in (alpha / 2, 1 - alpha / 2):
        z = norm_ppf(q)
        qs.append(100 * norm_cdf(z0 + (z0 + z) / (1 - a * (z0 + z))))
    return [float(v) for v in np.percentile(boot, qs)], {"z0": z0, "a": a}


def xy_from(r: dict):
    ref = np.asarray(r["trace_kernel_per_condition"], float)
    meas = np.asarray(r["ratio_per_condition"], float) * ref
    ok = (ref > 0) & (meas > 0)
    return np.log10(ref[ok]), np.log10(meas[ok]), ref


def config_seed(run: str):
    p = EXP3 / run / "config.yaml"
    if not p.exists():
        return None
    m = re.search(r"^seed:\s*(\d+)", p.read_text(encoding="utf-8"), flags=re.M)
    return int(m.group(1)) if m else None


def part2_cifar() -> dict:
    rng = np.random.default_rng(SEED + 2)
    pub = {int(float(r["h"])): r for r in json.loads(REEVAL.read_text(encoding="utf-8"))}
    out = {"source_published": rel(REEVAL), "per_h": {}}
    for h in (4, 5, 6):
        r = pub[h]
        x, y, ref_pub = xy_from(r)
        f = ols(x, y)
        bs = boot_slopes(x, y, B_SLOPE, rng)
        jack = np.array([ols(np.delete(x, i), np.delete(y, i))["slope"] for i in range(x.size)])
        bca_ci, bca_par = bca(f["slope"], bs, jack)
        tc = tq(f["n"] - 2)
        ps, pse, pr2, pdec = PAPER_SLOPE[h]
        published = dict(f)
        published.update({
            "run": r["run"], "config_seed": config_seed(r["run"]), "n_conditions_in_file": r["n_conditions"],
            "instances_in_file": 1, "t_crit_df": [tc, f["n"] - 2],
            "ci_ols_t": [f["slope"] - tc * f["se_ols"], f["slope"] + tc * f["se_ols"]],
            "ci_hc3_t": [f["slope"] - tc * f["se_hc3"], f["slope"] + tc * f["se_hc3"]],
            "ci_case_boot_percentile": [float(q) for q in np.percentile(bs, [2.5, 97.5])],
            "ci_case_boot_bca": bca_ci, "bca_params": bca_par, "case_boot_B": B_SLOPE,
            "case_boot_sd": float(bs.std(ddof=1)),
            "paper": {"slope": ps, "se": pse, "r2": pr2, "decades": pdec},
            "matches_paper": {"slope": matches(f["slope"], float(ps), 3), "se": matches(f["se_ols"], float(pse), 3),
                              "r2": matches(f["r2"], float(pr2), 3), "decades": matches(f["decades"], float(pdec), 2)}})

        inst = {}
        for s in (0, 1, 2):
            p = RERUN / f"reeval_exp3_cifar_heff_h{h}_s{s}" / "reeval.json"
            rr = json.loads(p.read_text(encoding="utf-8"))
            rr = rr[0] if isinstance(rr, list) else rr
            xs, ys, ref_s = xy_from(rr)
            fs = ols(xs, ys)
            fs.update({"source": rel(p), "run": rr["run"], "config_seed": config_seed(rr["run"]),
                       "same_reference_as_published": bool(ref_s.shape == ref_pub.shape
                                                           and np.allclose(ref_s, ref_pub, rtol=1e-9))})
            inst[s] = (xs, ys, fs)
        slopes = np.array([inst[s][2]["slope"] for s in inst])
        G = len(inst)
        parts = []
        for s in inst:
            xs, ys, _ = inst[s]
            xc, yc = xs - xs.mean(), ys - ys.mean()
            parts.append((float((xc * yc).sum()), float((xc * xc).sum()), xc, yc))
        b_fe = sum(p[0] for p in parts) / sum(p[1] for p in parts)
        N = sum(p[2].size for p in parts)
        res2 = [p[3] - b_fe * p[2] for p in parts]
        sxx = sum(p[1] for p in parts)
        se_fe_naive = math.sqrt(sum(float((e * e).sum()) for e in res2) / (N - G - 1) / sxx)
        se_fe_cr1 = math.sqrt(G / (G - 1) * sum(float((p[2] * e).sum()) ** 2 for p, e in zip(parts, res2))) / sxx
        clus = np.array([sum(parts[g][0] for g in tr) / sum(parts[g][1] for g in tr)
                         for tr in itertools.product(range(G), repeat=G)])
        two = np.empty(B_SLOPE)
        for b in range(B_SLOPE):
            sxy_b = sxx_b = 0.0
            for g in rng.integers(0, G, G):
                xs, ys, _ = inst[list(inst)[g]]
                i = rng.integers(0, xs.size, xs.size)
                xb, yb = xs[i], ys[i]
                xc = xb - xb.mean()
                sxy_b += float((xc * (yb - yb.mean())).sum())
                sxx_b += float((xc * xc).sum())
            two[b] = sxy_b / sxx_b
        pooled = ols(np.concatenate([inst[s][0] for s in inst]), np.concatenate([inst[s][1] for s in inst]))
        t2 = tq(G - 1)
        m_sl, sd_sl = float(slopes.mean()), float(slopes.std(ddof=1))
        out["per_h"][h] = {
            "published_single_instance": published,
            "rerun_instances": {f"s{s}": inst[s][2] for s in inst},
            "rerun_summary": {
                "slopes": [float(v) for v in slopes], "slope_min": float(slopes.min()),
                "slope_max": float(slopes.max()), "mean_of_instance_slopes": m_sl, "sd_of_instance_slopes": sd_sl,
                "t_crit_df2": t2, "ci_mean_t_df2": [m_sl - t2 * sd_sl / math.sqrt(G), m_sl + t2 * sd_sl / math.sqrt(G)],
                "fe_pooled_slope": b_fe, "fe_se_naive": se_fe_naive, "fe_se_cr1_G3": se_fe_cr1,
                "fe_ci_cr1_t_df2": [b_fe - t2 * se_fe_cr1, b_fe + t2 * se_fe_cr1],
                "cluster_boot_all_27_resamples": [float(q) for q in np.percentile(clus, [2.5, 97.5])],
                "cluster_boot_distinct_values": int(np.unique(np.round(clus, 12)).size),
                "two_stage_boot_ci": [float(q) for q in np.percentile(two, [2.5, 97.5])], "two_stage_B": B_SLOPE,
                "plain_pooled_ols": pooled,
                "published_minus_rerun_s0_same_instance": float(f["slope"] - inst[0][2]["slope"]),
            }}
    return out


def cifar_tables(c: dict) -> list[str]:
    L = ["", "% ---------------------------------------------------------------------------",
         "% Slope column for Table tab:cifarddpm. Published instance (48 conditions, one instance):",
         "% slope, 95% case-bootstrap interval (percentile, B=20000) and R^2; then the three re-trained",
         "% instances of results/exp3/_rerun: range of per-instance slopes and two-stage bootstrap interval.",
         r"$h$ & slope, one instance [case bootstrap] & $R^2$ & decades & slopes of 3 instances & pooled within-instance [two-stage bootstrap]\\"]
    for h, d in c["per_h"].items():
        p, s = d["published_single_instance"], d["rerun_summary"]
        L.append(f"${h}$ & {cell(p['slope'], *p['ci_case_boot_percentile'], 3)} & ${p['r2']:.3f}$ & "
                 f"${p['decades']:.2f}$ & " + ", ".join(f"${v:.3f}$" for v in s["slopes"]) + " & "
                 + cell(s["fe_pooled_slope"], *s["two_stage_boot_ci"], 3) + r"\\")
    return L


# ============================================================================ 3. EDM AUCs
R = Path("results")
EDM = {
    "sub500s0": {"q": R / "n3_rho_20261117/sub500/q_per_sample.npz",
                 "anchor": R / "n3_anchor_20261117/sub500/q_per_sample.npz"},
    "sub500s1": {"q": R / "n3_rho2_20261118/sub500s1/q_per_sample.npz"},
    "sub2000": {"q": R / "n3_rho2_20261118/sub2000/q_per_sample.npz"},
}
LC_JSON = R / "n3_rho2_20261118/late_contraction_bootstrap.json"
ROB_MD = R / "n3_robust_20261117/ROBUSTNESS.md"
N3_SUB500 = R / "n3_edm_sub500_20261115/sub500_s0/per_sample.npz"
RHO_COLS = {"1.92": 9, "0.585": 11, "0.140": 13, "0.023": 15, "0.002": 17}


def auc(pos, neg) -> float:
    """P(pos > neg) + P(pos = neg)/2 (as scripts.n3_edm_memorization.auc), via sorting."""
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    ns = np.sort(neg)
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    return float((lo.sum() + 0.5 * (hi - lo).sum()) / (pos.size * ns.size))


def auc_w(pos, wp, neg, wn) -> float:
    o = np.argsort(neg, kind="mergesort")
    ns, cw = neg[o], np.concatenate([[0.0], np.cumsum(wn[o])])
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    return float((wp * (cw[lo] + 0.5 * (cw[hi] - cw[lo]))).sum() / (wp.sum() * wn.sum()))


def strat_boot(scores: dict, off, B, rng, pairs=()):
    io, ii = np.where(off)[0], np.where(~off)[0]
    est = {k: auc(v[io], v[ii]) for k, v in scores.items()}
    for a, b in pairs:
        est[f"{a}-{b}"] = est[a] - est[b]
    draws = {k: np.empty(B) for k in est}
    for t in range(B):
        so, si = io[rng.integers(0, io.size, io.size)], ii[rng.integers(0, ii.size, ii.size)]
        d = {k: auc(v[so], v[si]) for k, v in scores.items()}
        for a, b in pairs:
            d[f"{a}-{b}"] = d[a] - d[b]
        for k in est:
            draws[k][t] = d[k]
    return {k: [est[k], *(float(q) for q in np.percentile(draws[k], [2.5, 97.5]))] for k in est}


def cluster_boot(scores: dict, off, cid, B, rng, pairs=()):
    """Resample whole clusters (multinomial cluster weights); off/on counts vary across resamples."""
    _, inv = np.unique(cid, return_inverse=True)
    G = int(inv.max()) + 1
    draws = {k: np.empty(B) for k in list(scores) + [f"{a}-{b}" for a, b in pairs]}
    for t in range(B):
        w = np.bincount(rng.integers(0, G, G), minlength=G)[inv].astype(float)
        wo, wi = w[off], w[~off]
        d = {k: auc_w(v[off], wo, v[~off], wi) if wo.sum() > 0 and wi.sum() > 0 else np.nan
             for k, v in scores.items()}
        for a, b in pairs:
            d[f"{a}-{b}"] = d[a] - d[b]
        for k in draws:
            draws[k][t] = d[k]
    return {k: [float(q) for q in np.nanpercentile(v, [2.5, 97.5])] for k, v in draws.items()}, G


def delong(scores: dict, off, pairs=()):
    """DeLong (1988) AUC standard errors, with covariances for paired differences."""
    io, ii = np.where(off)[0], np.where(~off)[0]
    m, n = io.size, ii.size
    V10, V01, est = {}, {}, {}
    for k, v in scores.items():
        p, q = v[io], v[ii]
        assert np.isfinite(p).all() and np.isfinite(q).all()
        qs, ps = np.sort(q), np.sort(p)
        V10[k] = (np.searchsorted(qs, p, "left") + 0.5 * (np.searchsorted(qs, p, "right")
                                                        - np.searchsorted(qs, p, "left"))) / n
        V01[k] = (m - np.searchsorted(ps, q, "right") + 0.5 * (np.searchsorted(ps, q, "right")
                                                              - np.searchsorted(ps, q, "left"))) / m
        est[k] = float(V10[k].mean())
    out = {}
    for k in scores:
        se = math.sqrt(V10[k].var(ddof=1) / m + V01[k].var(ddof=1) / n)
        out[k] = [est[k], est[k] - Z975 * se, est[k] + Z975 * se, se]
    for a, b in pairs:
        var = (V10[a].var(ddof=1) + V10[b].var(ddof=1) - 2 * np.cov(V10[a], V10[b])[0, 1]) / m \
            + (V01[a].var(ddof=1) + V01[b].var(ddof=1) - 2 * np.cov(V01[a], V01[b])[0, 1]) / n
        se = math.sqrt(max(var, 0.0))
        dlt = est[a] - est[b]
        out[f"{a}-{b}"] = [dlt, dlt - Z975 * se, dlt + Z975 * se, se]
    return out


def separation_bound(m: int, n: int, alpha: float = ALPHA):
    """One-sided (1-alpha) lower confidence bound for AUC = P(S_off > S_on) after complete separation.

    With W = G_on(S_off), E[W] = AUC = theta and P(separation) = E[(min_i W_i)^n] over the m off-atom samples.
    For any w0 in (theta, 1]: P(sep) <= w0^n + P(W >= w0)^m <= w0^n + (theta/w0)^m (Markov). Every theta with
    min_w0 [w0^n + (theta/w0)^m] < alpha is rejected, so theta_L below is a valid (conservative) bound. The
    two-point law W in {0, 1} attains P(sep) = theta^m, so no exact bound can exceed alpha^(1/m)."""
    def U(th):
        w0 = np.linspace(th, 1.0, 20001)[1:]
        return float(np.min(w0 ** n + (th / w0) ** m))
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if U(mid) < alpha else (lo, mid)
    return {"m_off": m, "n_on": n, "alpha_one_sided": alpha, "lower_bound_rigorous": lo,
            "two_point_ceiling": alpha ** (1.0 / m)}


def late_contraction(z):
    rho = z["err"] / z["n1"]
    sg = z["sigma"]
    inc = (1 - 0.5 * (rho[:, :-1] + rho[:, 1:])) * np.log(sg[:-1] / sg[1:])
    return inc[:, 11:].sum(1), rho, (float(sg[11]), float(sg[-1]))


def part3_edm() -> dict:
    rng = np.random.default_rng(SEED + 3)
    lc_json = json.loads(LC_JSON.read_text(encoding="utf-8"))
    out = {"late_contraction_json": rel(LC_JSON), "models": {}}
    for name, src in EDM.items():
        z = np.load(src["q"])
        off = z["d1"] / z["d2"] >= 1 / 3
        C, rho, (s_from, s_to) = late_contraction(z)
        za, anchor_src, rerun_check = z, rel(src["q"]), None
        if "dD" not in z.files:
            # n3_anchor_20261117/sub500 re-ran the same latents of the same model (GPU arithmetic differs slightly):
            # labels and off-atom flags must agree; the late contraction is also recomputed from that file.
            za, anchor_src = np.load(src["anchor"]), rel(src["anchor"])
            offa = za["d1"] / za["d2"] >= 1 / 3
            assert np.array_equal(z["label"], za["label"]) and np.array_equal(off, offa), "not the same samples"
            Ca = late_contraction(za)[0]
            rerun_check = {
                "same_labels_and_off_flags": True,
                "max_rel_diff_d1": float(np.max(np.abs(z["d1"] - za["d1"]) / z["d1"])),
                "max_abs_diff_C": float(np.max(np.abs(C - Ca))),
                "C_median_on_anchorfile": float(np.median(Ca[~off])), "C_median_off_anchorfile": float(np.median(Ca[off])),
                "AUC_C_anchorfile": auc(-Ca[off], -Ca[~off]),
            }
        sc = {"C": -C, "nn_end": za["dD"][:, 17], "rad194": za["radA"][:, 4], "nn194": za["dD"][:, 4],
              "rad129": za["radA"][:, 5], "nn129": za["dD"][:, 5]}
        sc.update({f"rho{k}": rho[:, i] for k, i in RHO_COLS.items()})
        pairs = (("C", "nn_end"), ("rad194", "nn194"), ("rad129", "nn129"))
        sb = strat_boot(sc, off, B_AUC, rng, pairs)
        dl = delong(sc, off, pairs)
        cb, G = cluster_boot(sc, off, z["label"], B_AUC, rng, pairs)
        nn1 = za["nn1"] if "nn1" in za.files else None
        if nn1 is not None:
            cid = z["label"].astype(np.int64) * 100000 + nn1.astype(np.int64)
            ib, Gi = cluster_boot({"C": sc["C"], "nn_end": sc["nn_end"]}, off, cid, B_AUC, rng, (("C", "nn_end"),))
        else:
            ib, Gi = None, None
        Coff, Con = C[off], C[~off]
        sep = {}
        for k in ("C", "nn_end", "rho0.585", "rho0.140", "rho0.023", "rho0.002"):
            v = sc[k]
            disc = int((v[off][:, None] < v[~off][None]).sum())
            ties = int((v[off][:, None] == v[~off][None]).sum())
            sep[k] = {"discordant_pairs": disc, "tied_pairs": ties, "pairs": int(off.sum() * (~off).sum()),
                      "complete_separation": disc == 0 and ties == 0}
            if disc == 0 and ties == 0:
                sep[k].update(separation_bound(int(off.sum()), int((~off).sum())))
                # scores are oriented so that off-atom is larger (C enters as -C)
                sep[k]["margin_min_off_score_minus_max_on_score"] = float(v[off].min() - v[~off].max())
        jl = lc_json.get(name, {})
        out["models"][name] = {
            "source": rel(src["q"]), "anchor_source": anchor_src, "anchor_rerun_check": rerun_check,
            "n": int(off.size), "n_off": int(off.sum()),
            "n_on": int((~off).sum()), "classes": int(np.unique(z["label"]).size),
            "sigma_from_to": [s_from, s_to],
            "C_median_on": float(np.median(Con)), "C_median_off": float(np.median(Coff)),
            "C_max_off": float(Coff.max()), "C_min_on": float(Con.min()),
            "stratified_bootstrap": sb, "stratified_B": B_AUC, "delong": dl,
            "class_cluster_bootstrap": cb, "class_clusters": G,
            "endpoint_image_cluster_bootstrap": ib, "endpoint_image_clusters": Gi,
            "separation": sep,
            "json_values": {k: jl.get(k) for k in ("C", "nn_end", "C-nn_end", "rad194", "nn194", "rad129", "nn129",
                                                   "rad194-nn194", "rad129-nn129", "rho_end", "rho059",
                                                   "C_on_med", "C_off_med", "n_off")},
        }
    # ROBUSTNESS.md values the paper quotes: e - nn at sigma 8.4 (first 500-image model), radA - dD at 19.4.
    rob = ROB_MD.read_text(encoding="utf-8")
    z = np.load(N3_SUB500)
    off = z["d1"] / z["d2"] >= 1 / 3
    e84 = strat_boot({"e": z["e_learned"][:, 6], "nn": z["nn_hat"][:, 6]}, off, B_AUC, rng, (("e", "nn"),))
    out["robustness_md"] = {
        "source_md": rel(ROB_MD), "source_npz": rel(N3_SUB500), "n_off": int(off.sum()),
        "e_minus_nn_sigma8.4": e84, "md_string_e_minus_nn": "e-nn -0.074 [-0.099, -0.049]",
        "md_string_present": "e-nn -0.074 [-0.099, -0.049]" in rob,
        "md_string_radA_minus_dD_19.4": "0.106 [0.056, 0.159]",
        "md_string_radA_present": "0.106 [0.056, 0.159]" in rob,
        "radA_minus_dD_sigma19.4_recomputed": out["models"]["sub500s0"]["stratified_bootstrap"]["rad194-nn194"],
        "method_md": "stratified bootstrap, B=1000 (header of ROBUSTNESS.md)",
    }
    return out


def edm_lines(e: dict) -> list[str]:
    L = ["", "% ---------------------------------------------------------------------------",
         "% EDM late contraction (sec:edm, tab:edm-models): AUC of -C, 95% stratified bootstrap (B=10000),",
         "% class-cluster bootstrap; for complete separation a one-sided 95% distribution-free lower bound."]
    for name, d in e["models"].items():
        sb, cb = d["stratified_bootstrap"]["C"], d["class_cluster_bootstrap"]["C"]
        s = d["separation"]["C"]
        if s["complete_separation"]:
            L.append(f"% {name}: AUC $1.000$ (complete separation of the ${d['n_off']}$ off-atom samples; one-sided "
                     f"$95\\%$ lower bound ${s['lower_bound_rigorous']:.2f}$); C medians "
                     f"${d['C_median_on']:.2f}$ / ${d['C_median_off']:.2f}$")
        else:
            L.append(f"% {name}: AUC ${sb[0]:.3f}$, $95\\%$ interval $[{sb[1]:.3f},{sb[2]:.3f}]$ (stratified bootstrap; "
                     f"class-cluster bootstrap $[{cb[0]:.3f},{cb[1]:.3f}]$); C medians ${d['C_median_on']:.2f}$ / "
                     f"${d['C_median_off']:.2f}$")
    return L


# ============================================================================ main
def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main() -> None:
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    tchk = {df: tq(df) for df in KNOWN_T975}
    for df, v in tchk.items():
        assert abs(v - KNOWN_T975[df]) < 1e-6, (df, v)
    print("t quantiles (0.975):", {df: round(v, 6) for df, v in tchk.items()}, " z:", round(Z975, 6))

    e1 = part1_exp1()
    with open(OUT / "exp1_uncertainty.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "row", "iter_or_h", "column_or_label", "paper", "mean", "sd_pop", "sd_sample", "se",
                    "t_lo", "t_hi", "boot_lo", "boot_hi", "mean_matches_paper", "sd_pop_matches_paper", "values",
                    "source"])
        for key in ("tab_exp1", "refs", "p7kernel"):
            for x in e1[key]:
                w.writerow([key, x.get("row", ""), x.get("iter", x.get("h", "")), x.get("column", x.get("label", "")),
                            x["paper"], f"{x['mean']:.6g}", f"{x['sd_pop']:.6g}", f"{x['sd_sample']:.6g}",
                            f"{x['se']:.6g}", f"{x['t_lo']:.6g}", f"{x['t_hi']:.6g}", f"{x['boot_lo']:.6g}",
                            f"{x['boot_hi']:.6g}", x["mean_matches_paper"], x["sd_pop_matches_paper"],
                            ";".join(f"{v:.6g}" for v in x["values"]), x["source"]])
        for x in e1["contrasts"]:
            w.writerow(["contrast", x["contrast"], "", x["how"], "", f"{x['mean']:.6g}", f"{x['sd_pop']:.6g}",
                        f"{x['sd_sample']:.6g}", f"{x['se']:.6g}", f"{x['t_lo']:.6g}", f"{x['t_hi']:.6g}",
                        f"{x['boot_lo']:.6g}", f"{x['boot_hi']:.6g}", "", "",
                        ";".join(f"{v:.6g}" for v in x["values"]), "paired by seed (same instance)"])

    c2 = part2_cifar()
    e3 = part3_edm()
    (OUT / "cifar_slopes.json").write_text(json.dumps(jsonable(c2), indent=1), encoding="utf-8")
    (OUT / "edm_auc.json").write_text(json.dumps(jsonable(e3), indent=1), encoding="utf-8")
    tex = exp1_tables(e1) + cifar_tables(c2) + edm_lines(e3)
    (OUT / "tables.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(jsonable({"exp1": e1, "cifar": c2, "edm": e3,
                                                           "t_quantiles": tchk, "z975": Z975,
                                                           "seed": SEED}), indent=1), encoding="utf-8")

    # ------------------------------------------------------------------ console summary
    print("\n=== 1. EXP-1: mean | pop SD (paper) | sample SD | 95% t-interval | exact seed bootstrap ===")
    for key in ("tab_exp1", "refs"):
        for x in e1[key]:
            d = x["decimals"]
            print(f"{x['row']:15s} {str(x['iter']):>8s}  paper {x['paper']:>12s}  mean {x['mean']:.{d}f} "
                  f"popSD {x['sd_pop']:.{d}f} [{'ok' if x['mean_matches_paper'] and x['sd_pop_matches_paper'] else 'MISMATCH'}]"
                  f"  sSD {x['sd_sample']:.{d}f}  t [{x['t_lo']:.{d}f}, {x['t_hi']:.{d}f}]"
                  f"  boot [{x['boot_lo']:.{d}f}, {x['boot_hi']:.{d}f}]")
    print("\n--- Table tab:p7kernel ---")
    for x in e1["p7kernel"]:
        d = max(x["decimals"], 3)
        extra = f"  covers 1: {x['t_interval_covers_1']}" if "t_interval_covers_1" in x else ""
        print(f"h={x['h']:<5} {x['column']:16s} paper {x['paper']:>12s}  mean {x['mean']:.{d}f} popSD {x['sd_pop']:.{d}f} "
              f"[{'ok' if x['mean_matches_paper'] and x['sd_pop_matches_paper'] in (True, None) else 'MISMATCH'}]  "
              f"sSD {x['sd_sample']:.{d}f}  t [{x['t_lo']:.{d}f}, {x['t_hi']:.{d}f}]  "
              f"boot [{x['boot_lo']:.{d}f}, {x['boot_hi']:.{d}f}]{extra}")
    print("\n--- seed-paired contrasts (new) ---")
    for x in e1["contrasts"]:
        print(f"{x['contrast']:52s} mean {x['mean']:.4f}  sSD {x['sd_sample']:.4f}  t [{x['t_lo']:.4f}, "
              f"{x['t_hi']:.4f}]  boot [{x['boot_lo']:.4f}, {x['boot_hi']:.4f}]  per seed "
              + " ".join(f"{v:.3f}" for v in x["values"]))

    print("\n=== 2. CIFAR-10 log-log slopes ===")
    for h, d in c2["per_h"].items():
        p, s = d["published_single_instance"], d["rerun_summary"]
        print(f"h={h} published ({p['run']}, config seed {p['config_seed']}, {p['n']} conditions, 1 instance): "
              f"slope {p['slope']:.3f} OLS se {p['se_ols']:.3f} HC3 se {p['se_hc3']:.3f} R2 {p['r2']:.3f} "
              f"decades {p['decades']:.2f}  matches paper {p['matches_paper']}")
        print(f"     OLS t-CI [{p['ci_ols_t'][0]:.3f}, {p['ci_ols_t'][1]:.3f}]  HC3 t-CI [{p['ci_hc3_t'][0]:.3f}, "
              f"{p['ci_hc3_t'][1]:.3f}]  case boot pct [{p['ci_case_boot_percentile'][0]:.3f}, "
              f"{p['ci_case_boot_percentile'][1]:.3f}]  BCa [{p['ci_case_boot_bca'][0]:.3f}, {p['ci_case_boot_bca'][1]:.3f}]")
        for k, fs in d["rerun_instances"].items():
            print(f"     rerun {k} ({fs['run']}, seed {fs['config_seed']}, same ref as published: "
                  f"{fs['same_reference_as_published']}): slope {fs['slope']:.3f} se {fs['se_ols']:.3f} "
                  f"R2 {fs['r2']:.3f} decades {fs['decades']:.2f}")
        print(f"     3 instances: mean slope {s['mean_of_instance_slopes']:.3f} sd {s['sd_of_instance_slopes']:.3f} "
              f"t(df=2) CI [{s['ci_mean_t_df2'][0]:.3f}, {s['ci_mean_t_df2'][1]:.3f}]  FE pooled {s['fe_pooled_slope']:.3f} "
              f"(naive se {s['fe_se_naive']:.3f}, CR1 se {s['fe_se_cr1_G3']:.3f})  cluster boot "
              f"[{s['cluster_boot_all_27_resamples'][0]:.3f}, {s['cluster_boot_all_27_resamples'][1]:.3f}] "
              f"two-stage boot [{s['two_stage_boot_ci'][0]:.3f}, {s['two_stage_boot_ci'][1]:.3f}]  plain pooled "
              f"{s['plain_pooled_ols']['slope']:.3f} (R2 {s['plain_pooled_ols']['r2']:.3f})  published - s0 "
              f"{s['published_minus_rerun_s0_same_instance']:+.3f}")

    print("\n=== 3. EDM AUCs ===")
    for name, d in e3["models"].items():
        sb, dl, cb = d["stratified_bootstrap"], d["delong"], d["class_cluster_bootstrap"]
        print(f"{name}: n_off {d['n_off']}/{d['n']}  C medians on {d['C_median_on']:.3f} off {d['C_median_off']:.3f}  "
              f"sigma {d['sigma_from_to'][0]:.4f}->{d['sigma_from_to'][1]:.4f}")
        if d["anchor_rerun_check"]:
            print(f"   anchor file re-run of the same latents: {d['anchor_rerun_check']}")
        jmap = {"rho0.002": "rho_end", "rho0.585": "rho059"}
        print(f"   json: C_on_med {d['json_values']['C_on_med']} C_off_med {d['json_values']['C_off_med']} "
              f"n_off {d['json_values']['n_off']}")
        for k in ("C", "nn_end", "C-nn_end", "rad194", "nn194", "rad194-nn194", "rad129", "nn129", "rad129-nn129",
                  "rho1.92", "rho0.585", "rho0.140", "rho0.023", "rho0.002"):
            j = d["json_values"].get(jmap.get(k, k))
            print(f"   {k:14s} AUC {sb[k][0]:.4f}  strat [{sb[k][1]:.3f}, {sb[k][2]:.3f}]  DeLong [{dl[k][1]:.3f}, "
                  f"{dl[k][2]:.3f}]  class-cluster [{cb[k][0]:.3f}, {cb[k][1]:.3f}]" + (f"  json {j}" if j else ""))
        if d["endpoint_image_cluster_bootstrap"]:
            ib = d["endpoint_image_cluster_bootstrap"]
            print(f"   endpoint-image clusters ({d['endpoint_image_clusters']}): C [{ib['C'][0]:.3f}, {ib['C'][1]:.3f}] "
                  f"C-nn_end [{ib['C-nn_end'][0]:.3f}, {ib['C-nn_end'][1]:.3f}]")
        for k, s in d["separation"].items():
            if s["complete_separation"]:
                print(f"   complete separation of {k}: margin {s['margin_min_off_score_minus_max_on_score']:.4g}; one-sided 95% "
                      f"lower bound {s['lower_bound_rigorous']:.4f} (two-point ceiling {s['two_point_ceiling']:.4f})")
            else:
                print(f"   {k}: {s['discordant_pairs']} discordant + {s['tied_pairs']} tied of {s['pairs']} pairs")
    rb = e3["robustness_md"]
    print(f"ROBUSTNESS.md e-nn at sigma 8.4 (B=1000 in md: present={rb['md_string_present']}): recomputed B={B_AUC} "
          f"{rb['e_minus_nn_sigma8.4']['e-nn']}")
    print(f"ROBUSTNESS.md radA-dD at 19.4 (present={rb['md_string_radA_present']}): recomputed "
          f"{rb['radA_minus_dD_sigma19.4_recomputed']}")
    print(f"\nwrote {OUT}/exp1_uncertainty.csv, cifar_slopes.json, edm_auc.json, tables.tex, summary.json")


if __name__ == "__main__":
    main()
