"""Kernel tracking, uncertainty: intervals for the label-noise comparisons of the paper.

Every number below is recomputed from saved result files; the values the paper prints are typed
in only to be compared against.

1. Linear-Gaussian problem (Table tab:p7kernel; results/exp1/_theory/raw/p7_kernel.csv): for every
   reported mean over the five seeds, the sample SD (ddof=1), the 95% Student-t interval (df=4) and
   the exact seed bootstrap (all 5^5 = 3125 equally likely resamples of the five seeds).
2. CIFAR-10 kernel tracking (Table tab:cifar-kernel). The slope of the original run comes from
   results/exp3/_cifar_ddpm/reeval.json, whose 48 conditions all belong to ONE instance (run
   exp3_cifar_ddpm_h*, seed 0), so clustering cannot be assessed from that file: we give HC3 and
   case-bootstrap intervals. The re-trained runs in results/exp3/_rerun/ (three instances, 48
   conditions each; s0 is the original instance re-trained) do allow it: per-instance slopes, a
   t-interval over instances (df=2), a pooled within-instance slope with an instance (cluster)
   bootstrap and a two-stage bootstrap (instances, then conditions within instances).

    PYTHONPATH=. uv run --no-sync python -m scripts.kernel_tracking_uncertainty

numpy only (no scipy, no torch, no pandas). Writes results/kernel_tracking_20261121/uncertainty/.
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np

from scripts.uncertainty_common import (ALPHA, B_SLOPE, P7_CSV, SEED, Z975, _csv_rows, _entry,
                                        cell, check_t_quantiles, fnum, jsonable, matches,
                                        norm_cdf, norm_ppf, rel, seed_summary, tq)

OUT = Path("results/kernel_tracking_20261121/uncertainty")

# ============================================================================ 1. linear-Gaussian, tab:p7kernel
P7_PAPER = {
    0.01: {"trace_kernel": "0.583", "trace_post": "1.018", "trace_meas": "0.673+-0.187",
           "ratio_to_kernel": "1.308+-0.376", "ratio_to_post": "0.66", "n_eff": "3.5"},
    0.05: {"trace_kernel": "0.921", "trace_post": "1.018", "trace_meas": "0.926+-0.169",
           "ratio_to_kernel": "1.002+-0.050", "ratio_to_post": "0.91", "n_eff": "13.6"},
    0.1: {"trace_kernel": "1.004", "trace_post": "1.018", "trace_meas": "1.001+-0.173",
          "ratio_to_kernel": "0.994+-0.039", "ratio_to_post": "0.98", "n_eff": "26.0"},
    0.5: {"trace_kernel": "1.281", "trace_post": "1.018", "trace_meas": "1.294+-0.166",
          "ratio_to_kernel": "1.011+-0.022", "ratio_to_post": "1.27", "n_eff": "101.5"},
}


def part1_p7kernel() -> dict:
    res = {"p7kernel": []}
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
    return res


def p7_tables(r: dict) -> list[str]:
    L = ["% ---------------------------------------------------------------------------",
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


# ============================================================================ main
def main() -> None:
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    tchk = check_t_quantiles()

    e1 = part1_p7kernel()
    with open(OUT / "p7kernel_uncertainty.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "h", "column", "paper", "mean", "sd_pop", "sd_sample", "se", "t_lo", "t_hi",
                    "boot_lo", "boot_hi", "mean_matches_paper", "sd_pop_matches_paper", "values", "source"])
        for x in e1["p7kernel"]:
            w.writerow(["p7kernel", x["h"], x["column"], x["paper"], f"{x['mean']:.6g}", f"{x['sd_pop']:.6g}",
                        f"{x['sd_sample']:.6g}", f"{x['se']:.6g}", f"{x['t_lo']:.6g}", f"{x['t_hi']:.6g}",
                        f"{x['boot_lo']:.6g}", f"{x['boot_hi']:.6g}", x["mean_matches_paper"],
                        x["sd_pop_matches_paper"], ";".join(f"{v:.6g}" for v in x["values"]), x["source"]])
    c2 = part2_cifar()
    (OUT / "cifar_slopes.json").write_text(json.dumps(jsonable(c2), indent=1), encoding="utf-8")
    tex = p7_tables(e1) + cifar_tables(c2)
    (OUT / "tables.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(jsonable({"p7kernel": e1["p7kernel"], "cifar": c2,
                                                           "t_quantiles": tchk, "z975": Z975,
                                                           "seed": SEED}), indent=1), encoding="utf-8")

    print("\n--- Table tab:p7kernel ---")
    for x in e1["p7kernel"]:
        d = max(x["decimals"], 3)
        extra = f"  covers 1: {x['t_interval_covers_1']}" if "t_interval_covers_1" in x else ""
        print(f"h={x['h']:<5} {x['column']:16s} paper {x['paper']:>12s}  mean {x['mean']:.{d}f} popSD {x['sd_pop']:.{d}f} "
              f"[{'ok' if x['mean_matches_paper'] and x['sd_pop_matches_paper'] in (True, None) else 'MISMATCH'}]  "
              f"sSD {x['sd_sample']:.{d}f}  t [{x['t_lo']:.{d}f}, {x['t_hi']:.{d}f}]  "
              f"boot [{x['boot_lo']:.{d}f}, {x['boot_hi']:.{d}f}]{extra}")

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
    print(f"\nwrote {OUT}/p7kernel_uncertainty.csv, cifar_slopes.json, tables.tex, summary.json")


if __name__ == "__main__":
    main()
