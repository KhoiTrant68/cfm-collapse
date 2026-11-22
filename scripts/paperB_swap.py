"""Paper B, analysis "swap": the selection clock and the landing clock from the denoiser-swap runs.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_swap

Inputs, written by scripts/n3_swap.py (EDM's deterministic 18-step Heun sampler, 50 latents per class,
latent seed 0, 500 samples per model):
  results/n3_followup_20261111/swap_public/swap_per_sample.npz         public EDM model, 50k images
  results/n3_followup_20261111/swap_sub1000/swap_per_sample.npz        1000 images, 0.5 Mimg (under-trained)
  results/n3_followup_sub500_20261111/swap_sub500/swap_per_sample.npz  500 images, 10 Mimg (memorising)
Each holds, per sample, the endpoint's distances to the nearest and second-nearest training image of
its class (d1, d2) and the index of the nearest one (nn), for
  learned       the network at every sigma;
  exact         the exact class posterior mean m* at every sigma;
  net2exact@s   the network for sigma > s and m* for sigma <= s;
  exact2net@s   m* for sigma > s and the network for sigma <= s.
Off-atom means d1/d2 >= 1/3 (App. C.4 of paper/main.tex).

Definitions used here:
  =L   share of net->exact endpoints whose nearest image is that of the learned endpoint (selection);
  =E   share of exact->net endpoints whose nearest image is that of the all-exact endpoint;
  s_sel   largest s with =L >= 0.9, linear interpolation in log s between the two bracketing levels;
  s_land  s at which the exact->net off-atom share crosses 0.5, same interpolation;
  s_keepE s at which exact->net =E reaches 0.9 (the exact field's choice is kept by the network).
The hand-over happens on the sampler grid: the denoiser is switched for every evaluation at a grid level
sigma_k <= s, so the step from the last level above s to the first level at or below s is mixed (Euler
with the old field, corrector with the new one). Clocks are also reported on an "effective" axis, the
geometric mean of these two grid levels. Intervals: Wilson for shares, order statistics for medians,
paired bootstrap over samples (4000 resamples) for the clock levels.

Outputs in results/paperB_20261121/swap/:
  swap_clocks.json      every number with its interval and source, the figure curves, the checks;
  swap_levels.csv       one row per model and hand-over level;
  fig_swap_clocks.pdf   draft figure (fig_swap_clocks.png is a copy for inspection).
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.modules.setdefault("torch", None)  # figstyle imports torch optionally; this analysis must stay torch-free
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms  # noqa: E402,F401  (blended axes/data coordinates for in-place labels)
from matplotlib.lines import Line2D  # noqa: E402

from scripts.figstyle import OI, panel_tag, style, use_paper_style  # noqa: E402

R = Path("results")
OUT = R / "paperB_20261121" / "swap"
RATIO = 1.0 / 3.0
Z95 = 1.959963984540054
B_BOOT = 4000
SEED = 20261121

MODELS = [
    dict(key="public", path=R / "n3_followup_20261111/swap_public/swap_per_sample.npz",
         summary=R / "n3_followup_20261111/SWAP_SUMMARY.md", header="## swap_public",
         label="public, 50k images", short="public (50k)", color=OI["orange"]),
    dict(key="sub1000", path=R / "n3_followup_20261111/swap_sub1000/swap_per_sample.npz",
         summary=R / "n3_followup_20261111/SWAP_SUMMARY.md", header="## swap_sub1000",
         label="1k images, 0.5 Mimg", short="1000, under-trained", color=OI["purple"]),
    dict(key="sub500", path=R / "n3_followup_sub500_20261111/swap_sub500/swap_per_sample.npz",
         summary=R / "n3_followup_sub500_20261111/SWAP_SUMMARY.md", header="## swap_sub500",
         label="500 images, 10 Mimg", short="500, memorising", color=OI["green"]),
]


# --------------------------------------------------------------------------- statistics
def wilson(k: int, n: int, z: float = Z95) -> dict:
    """Wilson score interval for a binomial share k/n."""
    if n == 0:
        return {"k": 0, "n": 0, "p": float("nan"), "lo": float("nan"), "hi": float("nan")}
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {"k": int(k), "n": int(n), "p": p, "lo": max(0.0, c - h), "hi": min(1.0, c + h)}


def median_ci(x, conf: float = 0.95) -> dict:
    """Median with the distribution-free order-statistic interval [x_(j), x_(n-j+1)].

    j is the largest rank with P(Bin(n, 1/2) <= j-1) <= (1-conf)/2, so the coverage is at least conf.
    """
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    tot, cum, alpha = 2 ** n, 0, (1 - conf) / 2
    j = 0
    for k in range(n + 1):
        cum += math.comb(n, k)
        if cum / tot > alpha:
            j = k
            break
    below = (cum - math.comb(n, j)) / tot          # P(B <= j-1)
    lo, hi = (x[j - 1], x[n - j]) if j >= 1 else (-np.inf, np.inf)
    return {"median": float(np.median(x)), "lo": float(lo), "hi": float(hi),
            "ranks": [int(j), int(n - j + 1)], "coverage": float(1 - 2 * below)}


def crossing(s, f, thr: float, rising: bool = True):
    """First crossing of thr as s decreases from its largest value, linear in log s.

    rising=True looks for f >= thr (f grows as s shrinks); rising=False looks for f <= thr.
    Returns (value, status); status is "interp", "reached_at_max_s" (already past thr at the largest
    tested s, so the level is >= max s) or "not_reached" (never past thr, so the level is < min s).
    """
    s = np.asarray(s, dtype=float)
    f = np.asarray(f, dtype=float)
    hit = f >= thr if rising else f <= thr
    if not hit.any():
        return float("nan"), "not_reached"
    i = int(np.argmax(hit))
    if i == 0:
        return float("nan"), "reached_at_max_s"
    f0, f1 = f[i - 1], f[i]
    w = (thr - f0) / (f1 - f0)
    return float(math.exp(math.log(s[i - 1]) + w * (math.log(s[i]) - math.log(s[i - 1])))), "interp"


def boot_levels(rng, curves: dict, axes_s: dict, specs: list, n: int, B: int = B_BOOT) -> dict:
    """Paired bootstrap over samples of every clock level in specs.

    curves: name -> (n_levels, n) boolean per-sample indicators; axes_s: axis name -> s values;
    specs: (clock name, curve name, threshold, rising). Returns per clock and axis the percentile
    interval (censored replicates enter as +inf for "reached_at_max_s" and 0 for "not_reached") and
    the share of censored replicates, plus the per-replicate values for ratios.
    """
    idx = rng.integers(0, n, size=(B, n))
    means = {k: v[:, idx].mean(axis=2) for k, v in curves.items()}      # (n_levels, B)
    out, reps = {}, {}
    for name, curve, thr, rising in specs:
        out[name] = {}
        for ax_name, s in axes_s.items():
            vals = np.empty(B)
            st = {"interp": 0, "reached_at_max_s": 0, "not_reached": 0}
            for b in range(B):
                v, status = crossing(s, means[curve][:, b], thr, rising)
                st[status] += 1
                vals[b] = v if status == "interp" else (np.inf if status == "reached_at_max_s" else 0.0)
            q = np.quantile(vals, [0.025, 0.975], method="inverted_cdf")
            out[name][ax_name] = {"lo": float(q[0]), "hi": float(q[1]),
                                  "share_interp": st["interp"] / B,
                                  "share_reached_at_max_s": st["reached_at_max_s"] / B,
                                  "share_not_reached": st["not_reached"] / B}
            reps[(name, ax_name)] = vals
    return {"intervals": out, "replicates": reps}


# --------------------------------------------------------------------------- analysis
def effective_levels(sigma: np.ndarray, swaps: np.ndarray):
    """For each nominal s the grid bracket (last level > s, first level <= s) and its geometric mean."""
    br = []
    for s in swaps:
        k = int(np.nonzero(sigma > s)[0].max())
        hi, lo = float(sigma[k]), float(sigma[k + 1])
        br.append({"s": float(s), "last_old_level": hi, "first_new_level": lo, "step": k,
                   "s_eff": math.sqrt(hi * lo)})
    return br


def analyse(m: dict, rng) -> dict:
    z = np.load(m["path"])
    swaps = np.asarray(z["swap_sigmas"], dtype=float)
    sigma = np.asarray(z["sigma"], dtype=float)
    br = effective_levels(sigma, swaps)
    s_eff = np.array([b["s_eff"] for b in br])
    nnL, nnE = z["learned:nn"], z["exact:nn"]
    n = len(nnL)
    offL = z["learned:d1"] / z["learned:d2"] >= RATIO
    offE = z["exact:d1"] / z["exact:d2"] >= RATIO
    dis = nnL != nnE
    run = json.loads((m["path"].parent / "swap_run.json").read_text(encoding="utf-8"))
    res = {
        "source": str(m["path"]).replace("\\", "/"), "network": run["network"], "n_train": run["n_train"],
        "n": int(n), "steps": run["steps"], "swap_levels": swaps.tolist(), "sampler_sigma": sigma.tolist(),
        "handover_brackets": br,
        "learned_off": wilson(int(offL.sum()), n), "exact_off": wilson(int(offE.sum()), n),
        "learned_eq_exact_nn": wilson(int((~dis).sum()), n),
        "learned_d1": median_ci(z["learned:d1"]),
        "learned_d1_on_atom": median_ci(z["learned:d1"][~offL]) if (~offL).sum() > 0 else None,
        "learned_ratio_d1_d2": median_ci(z["learned:d1"] / z["learned:d2"]),
        "levels": [],
    }
    ind = {k: [] for k in ("n2e_eqL", "e2n_off", "e2n_on", "e2n_eqE")}
    for s in swaps:
        a, b = f"net2exact@{s:g}", f"exact2net@{s:g}"
        a_off = z[f"{a}:d1"] / z[f"{a}:d2"] >= RATIO
        b_off = z[f"{b}:d1"] / z[f"{b}:d2"] >= RATIO
        a_L, a_E = z[f"{a}:nn"] == nnL, z[f"{a}:nn"] == nnE
        b_L, b_E = z[f"{b}:nn"] == nnL, z[f"{b}:nn"] == nnE
        ind["n2e_eqL"].append(a_L); ind["e2n_off"].append(b_off)
        ind["e2n_on"].append(~b_off); ind["e2n_eqE"].append(b_E)
        lv = {"s": float(s), "t": 1 / (1 + float(s)),
              "net2exact": {"off": wilson(int(a_off.sum()), n), "eqL": wilson(int(a_L.sum()), n),
                            "eqE": wilson(int(a_E.sum()), n),
                            "d1_median": float(np.median(z[f"{a}:d1"])), "d1_max": float(z[f"{a}:d1"].max()),
                            "dist_to_learned_median": float(np.median(z[f"{a}:dist_to_learned"])),
                            "eqL_given_net_ne_exact": wilson(int((a_L & dis).sum()), int(dis.sum())),
                            "eqE_given_net_ne_exact": wilson(int((a_E & dis).sum()), int(dis.sum())),
                            "eqL_given_learned_off": wilson(int((a_L & offL).sum()), int(offL.sum())),
                            "eqL_given_learned_on": wilson(int((a_L & ~offL).sum()), int((~offL).sum()))},
              "exact2net": {"off": wilson(int(b_off.sum()), n), "on": wilson(int((~b_off).sum()), n),
                            "eqE": wilson(int(b_E.sum()), n), "eqL": wilson(int(b_L.sum()), n),
                            "d1": median_ci(z[f"{b}:d1"]),
                            "ratio_d1_d2": median_ci(z[f"{b}:d1"] / z[f"{b}:d2"]),
                            "dist_to_learned_median": float(np.median(z[f"{b}:dist_to_learned"])),
                            "eqE_given_net_ne_exact": wilson(int((b_E & dis).sum()), int(dis.sum())),
                            "eqL_given_net_ne_exact": wilson(int((b_L & dis).sum()), int(dis.sum())),
                            "off_given_net_ne_exact": wilson(int((b_off & dis).sum()), int(dis.sum())),
                            "off_given_learned_off": wilson(int((b_off & offL).sum()), int(offL.sum())),
                            "off_given_learned_on": wilson(int((b_off & ~offL).sum()), int((~offL).sum()))}}
        res["levels"].append(lv)
    curves = {k: np.stack(v) for k, v in ind.items()}

    # clock levels: point estimates on both axes, then a paired bootstrap
    specs = [("s_sel", "n2e_eqL", 0.9, True), ("s_sel50", "n2e_eqL", 0.5, True),
             ("s_sel95", "n2e_eqL", 0.95, True),
             ("s_land", "e2n_off", 0.5, False), ("s_land10", "e2n_on", 0.1, True),
             ("s_land90", "e2n_on", 0.9, True), ("s_keepE", "e2n_eqE", 0.9, True)]
    axes_s = {"nominal": swaps, "effective": s_eff}
    clocks = {}
    for name, curve, thr, rising in specs:
        clocks[name] = {"curve": curve, "threshold": thr}
        for ax_name, s_ax in axes_s.items():
            v, st = crossing(s_ax, curves[curve].mean(axis=1), thr, rising)
            clocks[name][ax_name] = {"value": v, "status": st}
    bt = boot_levels(rng, curves, axes_s, specs, n)
    for name in clocks:
        for ax_name in axes_s:
            clocks[name][ax_name]["boot95"] = bt["intervals"][name][ax_name]
    # paired ratios of clock levels (how many times larger in sigma), where both levels are interior
    for num, den in (("s_sel", "s_land"), ("s_sel50", "s_land"), ("s_keepE", "s_land")):
        ratio = {}
        for ax_name in axes_s:
            # censored replicates stay in: a level >= max s enters as +inf, a level < min s as 0, so a
            # censored numerator gives an open (+inf) end instead of a CI conditional on the uncensored ones
            a, b = bt["replicates"][(num, ax_name)], bt["replicates"][(den, ax_name)]
            with np.errstate(divide="ignore", invalid="ignore"):
                q = a / b
            defined = ~np.isnan(q)
            pa, pb = clocks[num][ax_name], clocks[den][ax_name]
            point = pa["value"] / pb["value"] if pa["status"] == pb["status"] == "interp" else float("nan")
            ratio[ax_name] = {"value": point, "share_defined_replicates": float(defined.mean()),
                              "share_finite_replicates": float(np.isfinite(q).mean()),
                              "boot95": ([float(v) for v in np.quantile(q[defined], [0.025, 0.975],
                                                                        method="inverted_cdf")]
                                         if defined.mean() >= 0.975 else None)}
        clocks[f"ratio_{num}_over_{den}"] = ratio
    res["clocks"] = clocks
    res["n_net_ne_exact"] = int(dis.sum())
    res["n_learned_off"] = int(offL.sum())

    # figure-ready curves
    def cur(key, sub):
        return {"p": [lv[key][sub]["p"] for lv in res["levels"]], "lo": [lv[key][sub]["lo"] for lv in res["levels"]],
                "hi": [lv[key][sub]["hi"] for lv in res["levels"]]}
    res["curves"] = {"s": swaps.tolist(), "s_eff": s_eff.tolist(),
                     "n2e_eqL": cur("net2exact", "eqL"), "n2e_off": cur("net2exact", "off"),
                     "e2n_on": cur("exact2net", "on"), "e2n_off": cur("exact2net", "off"),
                     "e2n_eqE": cur("exact2net", "eqE"),
                     "e2n_d1": {k: [lv["exact2net"]["d1"][k] for lv in res["levels"]] for k in ("median", "lo", "hi")}}
    return res


# --------------------------------------------------------------------------- checks against the quoted numbers
def parse_swap_summary(path: Path, header: str) -> dict:
    head, rows, on = None, {}, False
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.startswith(header):
            on = True
            head = [float(x) for x in re.findall(r"(\d+\.\d+)", ln)]
            continue
        if on and ln.startswith("| ") and ln[2].isdigit():
            c = [float(x.strip()) for x in ln.strip().strip("|").split("|")]
            rows[c[0]] = c
        elif on and rows and not ln.startswith("|"):
            break
    return {"head": head, "rows": rows}


def check_summary(m: dict, r: dict) -> dict:
    """Recompute every entry of SWAP_SUMMARY.md and return the largest absolute difference."""
    p = parse_swap_summary(m["summary"], m["header"])
    mine_head = [r["learned_off"]["p"], r["exact_off"]["p"], r["learned_eq_exact_nn"]["p"]]
    diffs = [abs(a - b) for a, b in zip(p["head"], mine_head)]
    bad = []
    for lv in r["levels"]:
        row = p["rows"][lv["s"]]
        A, Bx = lv["net2exact"], lv["exact2net"]
        mine = [lv["s"], lv["t"], A["off"]["p"], A["eqL"]["p"], A["eqE"]["p"], A["d1_median"],
                Bx["off"]["p"], Bx["eqL"]["p"], Bx["eqE"]["p"], Bx["d1"]["median"], Bx["dist_to_learned_median"]]
        for col, (q, v) in enumerate(zip(row, mine)):
            d = abs(q - v)
            diffs.append(d)
            if d > 5.01e-4:
                bad.append({"s": lv["s"], "column": col, "summary": q, "recomputed": v})
    return {"file": str(m["summary"]).replace("\\", "/"), "entries_checked": len(diffs),
            "max_abs_diff": max(diffs), "mismatches": bad}


def check_quotes(res: dict) -> list:
    """Numbers quoted in paper/main.tex (sec:edm, lines 1263-1269) and in the two NOTES_vi.md files."""
    def eqL(mk, s):
        return next(lv for lv in res[mk]["levels"] if lv["s"] == s)["net2exact"]["eqL"]["p"]

    def e2n(mk, s, q):
        return next(lv for lv in res[mk]["levels"] if lv["s"] == s)["exact2net"][q]

    out = []

    def add(src, claim, quoted, value, ok):
        out.append({"source": src, "claim": claim, "quoted": quoted, "recomputed": value, "agrees": bool(ok)})

    tex = "paper/main.tex sec:edm l.1263-1269"
    for s, q in ((5, 31), (2, 56), (1, 90), (0.2, 99), (0.02, 100)):
        v = 100 * eqL("public", s)
        add(tex, f"public net->exact =L at s={s:g} (%)", q, round(v, 1), round(v) == q)
    for s, q in ((5, 92.8), (2, 98.2), (1, 99.6)):
        v = 100 * eqL("sub500", s)
        add(tex, f"subset (sub500) net->exact =L at s={s:g} (%)", q, round(v, 1), abs(round(v, 1) - q) < 1e-9)
    v = [100 * eqL("sub500", s) for s in (0.2, 0.1, 0.05, 0.02)]
    add(tex, "subset (sub500) net->exact =L = 100% for every s <= 0.2", 100, v, all(x == 100 for x in v))
    for mk in ("public", "sub500"):
        v = [lv["net2exact"]["off"]["k"] for lv in res[mk]["levels"]]
        add(tex, f"{mk}: net->exact ends on a training image for every s in [0.02, 5] (off-atom counts)", 0, v,
            all(x == 0 for x in v))
    add(tex, "public: learned off-atom share (never memorises)", 1.0, res["public"]["learned_off"]["p"],
        res["public"]["learned_off"]["p"] == 1.0)
    notes = "results/n3_followup_20261111/NOTES_vi.md"
    for mk, qs in (("public", (31, 56, 90, 96, 99)), ("sub1000", (49, 63, 88, 95, 98))):
        for s, q in zip((5, 2, 1, 0.5, 0.2), qs):
            v = 100 * eqL(mk, s)
            add(notes, f"{mk} net->exact =L at s={s:g} (%)", q, round(v, 1), round(v) == q)
    for mk in ("public", "sub1000"):
        v = [round(100 * e2n(mk, s, "off")["p"], 1) for s in (5, 2, 1)]
        add(notes, f"{mk}: exact->net 'almost entirely off-atom for s >= 1' (% off at s=5,2,1)", ">~90", v,
            min(v) >= 90)
        v = [round(100 * e2n(mk, s, "off")["p"], 1) for s in (0.1, 0.05, 0.02)]
        add(notes, f"{mk}: exact->net on-atom for s <= 0.1 (% off at s=0.1,0.05,0.02)", "~0", v, max(v) <= 1)
    v = [round(e2n("public", s, "d1")["median"], 2) for s in (0.1, 0.05, 0.02)]
    add(notes, "public exact->net median d1 at s=0.1,0.05,0.02", [2.6, 1.4, 0.6], v,
        [round(x, 1) for x in v] == [2.6, 1.4, 0.6])
    notes5 = "results/n3_followup_sub500_20261111/NOTES_vi.md"
    v = [round(100 * eqL("sub500", s), 1) for s in (5, 2, 1, 0.2, 0.1, 0.05, 0.02)]
    add(notes5, "sub500 net->exact =L 92.8, 98.2, 99.6, then 100 from s <= 0.2", [92.8, 98.2, 99.6, 100, 100, 100, 100],
        v, v == [92.8, 98.2, 99.6, 100, 100, 100, 100])
    v = [lv["exact2net"]["off"]["k"] for lv in res["sub500"]["levels"]]
    add(notes5, "sub500 exact->net on-atom at every s (off-atom counts)", 0, v, all(x == 0 for x in v))
    v = min(lv["exact2net"]["eqE"]["p"] for lv in res["sub500"]["levels"])
    add(notes5, "sub500 exact->net =E >= 95.4%", 95.4, round(100 * v, 1), round(100 * v, 1) >= 95.4)
    v = [round(e2n("sub500", s, "d1")["median"], 2) for s in (5, 0.02)]
    add(notes5, "sub500 exact->net median d1 1.67 (s=5) -> 0.45 (s=0.02)", [1.67, 0.45], v, v == [1.67, 0.45])
    v = [round(lv["exact2net"]["dist_to_learned_median"], 1) for lv in res["sub500"]["levels"]]
    add(notes5, "sub500 exact->net endpoint ~27 from the network endpoint (medians over s)", "~27", v,
        all(26 <= x <= 28 for x in v))
    add(notes5, "sub500 swap run learned off-atom share", 0.038, res["sub500"]["learned_off"]["p"],
        abs(res["sub500"]["learned_off"]["p"] - 0.038) < 1e-9)
    return out


# --------------------------------------------------------------------------- output
def fmt_share(w: dict) -> str:
    return f"{100 * w['p']:.1f} [{100 * w['lo']:.1f}, {100 * w['hi']:.1f}]"


def fmt_clock(c: dict, ax: str = "nominal") -> str:
    v = c[ax]
    b = v["boot95"]
    if v["status"] == "interp":
        lo = "<min" if b["lo"] == 0 else ("inf" if not np.isfinite(b["lo"]) else f"{b['lo']:.3g}")
        hi = ">max" if not np.isfinite(b["hi"]) else ("<min" if b["hi"] == 0 else f"{b['hi']:.3g}")
        return f"{v['value']:.3g} [{lo}, {hi}]"
    return {"reached_at_max_s": ">= max s (already past the threshold at s=5)",
            "not_reached": "< min s (never past the threshold)"}[v["status"]]


def print_tables(res: dict) -> None:
    for m in MODELS:
        r = res[m["key"]]
        print(f"\n== {m['key']} ({r['source']}; n={r['n']}, n_train={r['n_train']})")
        print(f"   learned off-atom {fmt_share(r['learned_off'])}%, exact off-atom {fmt_share(r['exact_off'])}%, "
              f"learned and exact share the image {fmt_share(r['learned_eq_exact_nn'])}%")
        print(f"   learned median d1 {r['learned_d1']['median']:.3f}, median d1/d2 {r['learned_ratio_d1_d2']['median']:.3f}"
              + (f", on-atom median d1 {r['learned_d1_on_atom']['median']:.3f}" if r["learned_d1_on_atom"] else ""))
        print("   s     bracket          | n2e off | n2e =L               | e2n off              | e2n =E               "
              "| e2n median d1 [CI]")
        for lv, b in zip(r["levels"], r["handover_brackets"]):
            A, Bx = lv["net2exact"], lv["exact2net"]
            d = Bx["d1"]
            print(f"   {lv['s']:<5g} ({b['last_old_level']:.3g},{b['first_new_level']:.3g})".ljust(25)
                  + f"| {A['off']['k']:>3d}/{A['off']['n']} | {fmt_share(A['eqL']):<20} | {fmt_share(Bx['off']):<20} "
                  f"| {fmt_share(Bx['eqE']):<20} | {d['median']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]")
        c = r["clocks"]
        for k in ("s_sel", "s_sel50", "s_sel95", "s_keepE", "s_land10", "s_land", "s_land90"):
            print(f"   {k:<8} nominal {fmt_clock(c[k])}; effective {fmt_clock(c[k], 'effective')}")
        for k in ("ratio_s_sel_over_s_land", "ratio_s_sel50_over_s_land", "ratio_s_keepE_over_s_land"):
            for ax in ("nominal", "effective"):
                q = c[k][ax]
                b = "n/a" if q["boot95"] is None else f"[{q['boot95'][0]:.3g}, {q['boot95'][1]:.3g}]"
                print(f"   {k} ({ax}) {q['value']:.3g} boot95 {b} (finite in {q['share_finite_replicates']:.3f} "
                      f"of resamples)")
        print("   conditional: s | n2e =L given learned on / off | e2n =E, =L, off given net and exact choose differently")
        for lv in r["levels"]:
            A, Bx = lv["net2exact"], lv["exact2net"]
            print(f"   {lv['s']:<5g} | {fmt_share(A['eqL_given_learned_on'])} / {fmt_share(A['eqL_given_learned_off'])} "
                  f"| {fmt_share(Bx['eqE_given_net_ne_exact'])}, {fmt_share(Bx['eqL_given_net_ne_exact'])}, "
                  f"{fmt_share(Bx['off_given_net_ne_exact'])} (n={Bx['off_given_net_ne_exact']['n']})")


def write_csv(res: dict, path: Path) -> None:
    cols = ["model", "s", "t", "last_old_level", "first_new_level", "s_eff",
            "n2e_off_k", "n2e_off_lo", "n2e_off_hi", "n2e_eqL", "n2e_eqL_lo", "n2e_eqL_hi",
            "n2e_eqE", "n2e_d1_max",
            "e2n_off", "e2n_off_lo", "e2n_off_hi", "e2n_eqE", "e2n_eqE_lo", "e2n_eqE_hi",
            "e2n_eqL", "e2n_d1_median", "e2n_d1_lo", "e2n_d1_hi", "e2n_ratio_median", "e2n_dist_to_learned_median",
            "e2n_eqE_given_net_ne_exact", "n"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for m in MODELS:
            r = res[m["key"]]
            for lv, b in zip(r["levels"], r["handover_brackets"]):
                A, Bx = lv["net2exact"], lv["exact2net"]
                w.writerow([m["key"], lv["s"], f"{lv['t']:.4f}", b["last_old_level"], b["first_new_level"],
                            f"{b['s_eff']:.4f}",
                            A["off"]["k"], f"{A['off']['lo']:.4f}", f"{A['off']['hi']:.4f}",
                            f"{A['eqL']['p']:.4f}", f"{A['eqL']['lo']:.4f}", f"{A['eqL']['hi']:.4f}",
                            f"{A['eqE']['p']:.4f}", f"{A['d1_max']:.3g}",
                            f"{Bx['off']['p']:.4f}", f"{Bx['off']['lo']:.4f}", f"{Bx['off']['hi']:.4f}",
                            f"{Bx['eqE']['p']:.4f}", f"{Bx['eqE']['lo']:.4f}", f"{Bx['eqE']['hi']:.4f}",
                            f"{Bx['eqL']['p']:.4f}", f"{Bx['d1']['median']:.4f}", f"{Bx['d1']['lo']:.4f}",
                            f"{Bx['d1']['hi']:.4f}", f"{Bx['ratio_d1_d2']['median']:.4f}",
                            f"{Bx['dist_to_learned_median']:.3f}", f"{Bx['eqE_given_net_ne_exact']['p']:.4f}", r["n"]])


# --------------------------------------------------------------------------- figure
C_SEL, C_KEEP, C_LAND = OI["blue"], OI["sky"], OI["vermillion"]
XLIM = (7.0, 0.014)


def _xaxis(ax, label: bool = True) -> None:
    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.set_xticks([5, 1, 0.1, 0.02])
    ax.set_xticklabels(["5", "1", "0.1", "0.02"], fontsize=8)
    ax.set_xticks([2, 0.5, 0.2, 0.05], minor=True)
    ax.set_xticklabels([], minor=True)
    if label:
        ax.set_xlabel(r"hand-over level $s$", fontsize=9)


def _label(ax, tag: str, text: str, color: str = "black") -> None:
    """Panel letter (figstyle.panel_tag) with the panel's title anchored to its right edge (no overlap)."""
    panel_tag(ax, tag, dx=-0.02, dy=1.03)
    t = ax.texts[-1]
    ax.annotate(text, xy=(1, 0), xycoords=t, xytext=(3, 0), textcoords="offset points", ha="left", va="bottom",
                fontsize=8.2, color=color, fontweight="semibold" if color != "black" else "normal")


def _clock_text(c: dict) -> list:
    """Two short lines for the lower right corner of a panel: (text, colour)."""
    lines = []
    v = c["s_sel"]["nominal"]
    lines.append((rf"$s_{{\rm sel}}={v['value']:.2f}$" if v["status"] == "interp" else r"$s_{\rm sel}>5$", C_SEL))
    v = c["s_land"]["nominal"]
    if v["status"] == "interp":
        lines.append((rf"$s_{{\rm land}}={v['value']:.2f}$", C_LAND))
    else:
        lines.append(("lands at all $s$", C_LAND))
    return lines


def make_figure(res: dict, pdf: Path) -> None:
    use_paper_style()
    fig, axes = plt.subplots(1, 4, figsize=(7.6, 2.3), gridspec_kw={"width_ratios": [1, 1, 1, 1.12]})
    for ax, m, tag in zip(axes[:3], MODELS, "abc"):
        r = res[m["key"]]
        cv = r["curves"]
        s = np.array(cv["s"])
        for key, c, ls, mk in (("n2e_eqL", C_SEL, "-", "o"), ("e2n_eqE", C_KEEP, "--", None),
                               ("e2n_on", C_LAND, "-", "s")):
            p, lo, hi = (100 * np.array(cv[key][q]) for q in ("p", "lo", "hi"))
            if ls == "-":
                ax.fill_between(s, lo, hi, color=c, alpha=0.2, lw=0, zorder=1)
            ax.plot(s, p, color=c, ls=ls, lw=1.5 if ls == "-" else 1.2, marker=mk, ms=2.8, zorder=3)
        # each clock as a diamond where its curve crosses its threshold (both are linear in log s there)
        for key, c, y in (("s_sel", C_SEL, 90.0), ("s_land", C_LAND, 50.0)):
            v = r["clocks"][key]["nominal"]
            if v["status"] == "interp":
                ax.plot([v["value"]], [y], marker="D", ms=4.6, mfc="white", mec=c, mew=1.3, ls="none", zorder=5)
        for i, (txt, c) in enumerate(_clock_text(r["clocks"])):
            ax.text(0.96, 0.06 + 0.12 * (1 - i), txt, transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=7.6, color=c)
        _xaxis(ax)
        ax.set_ylim(-4, 106)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.tick_params(axis="y", labelsize=8)
        if tag == "a":
            ax.set_ylabel("share of samples (%)", fontsize=9)
        else:
            ax.set_yticklabels([])
        style(ax)
        _label(ax, tag, m["label"], color=m["color"])
    ax = axes[3]
    for m in MODELS:
        r = res[m["key"]]
        s = np.array(r["curves"]["s"])
        d = r["curves"]["e2n_d1"]
        # the network on its own (all-network trajectory from the same latents): a faint dashed level
        ax.axhline(r["learned_d1"]["median"], color=m["color"], ls="--", lw=0.9, alpha=0.7, zorder=1)
        ax.fill_between(s, d["lo"], d["hi"], color=m["color"], alpha=0.25, lw=0, zorder=2)
        ax.plot(s, d["median"], color=m["color"], marker="o", ms=2.8, lw=1.5, zorder=3, label=m["short"])
    _xaxis(ax)
    ax.set_yscale("log")
    ax.set_ylim(0.3, 40)
    ax.set_yticks([0.5, 1, 2, 5, 10, 20])
    ax.set_yticklabels(["0.5", "1", "2", "5", "10", "20"], fontsize=8)
    ax.set_yticks([], minor=True)
    ax.set_ylabel(r"median $d_1$", fontsize=9, labelpad=1)
    # model colours are those of the titles of (a)-(c); the dashed levels are labelled in place
    tr = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(0.97, 15.5, "network alone", transform=tr, ha="right", va="top", fontsize=6.6, color="#444444")
    ax.text(0.04, 1.95, "network alone", transform=tr, ha="left", va="bottom", fontsize=6.6, color="#444444")
    style(ax)
    _label(ax, "d", r"exact$\to$net: distance")
    fig.tight_layout(w_pad=0.5)
    # one legend for the three clock panels, above them
    entries = [(r"net$\to$exact: network's image ($=$L)", C_SEL, "-", "o"),
               (r"exact$\to$net: exact field's image ($=$E)", C_KEEP, "--", None),
               (r"exact$\to$net: on-atom (landed)", C_LAND, "-", "s")]
    hl = [Line2D([], [], color=c, ls=ls, lw=1.5, marker=mk, ms=2.8) for _, c, ls, mk in entries]
    x0 = axes[0].get_position().x0
    x1 = axes[2].get_position().x1
    fig.legend(hl, [e[0] for e in entries], loc="lower center", ncol=3, fontsize=7.2, frameon=False,
               bbox_to_anchor=((x0 + x1) / 2, 0.985), handlelength=2.0, columnspacing=1.2, handletextpad=0.5)
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(pdf.with_suffix(".png"), bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"  wrote {pdf} and {pdf.with_suffix('.png')}")


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return f if math.isfinite(f) else (None if math.isnan(f) else ("inf" if f > 0 else "-inf"))
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    res = {m["key"]: analyse(m, rng) for m in MODELS}
    print_tables(res)
    summ = {m["key"]: check_summary(m, res[m["key"]]) for m in MODELS}
    quotes = check_quotes(res)
    print("\n== SWAP_SUMMARY.md recomputation")
    for k, v in summ.items():
        print(f"   {k}: {v['entries_checked']} entries, max |diff| {v['max_abs_diff']:.2e}, mismatches {v['mismatches']}")
    print("\n== quoted numbers")
    for q in quotes:
        print(f"   [{'OK ' if q['agrees'] else 'NO '}] {q['source']}: {q['claim']}: quoted {q['quoted']}, "
              f"recomputed {q['recomputed']}")
    out = {"description": __doc__.split("\n\n")[0], "script": "scripts/paperB_swap.py",
           "off_atom_rule": "d1/d2 >= 1/3", "bootstrap": {"resamples": B_BOOT, "seed": SEED, "paired_over": "samples"},
           "interval_methods": {"shares": "Wilson 95%", "medians": "order-statistic 95% (distribution-free)",
                                "clock levels": "percentile 95% of a paired bootstrap; censored replicates as +inf "
                                                "(already past the threshold at s=5) or 0 (never past it)"},
           "models": res, "swap_summary_check": summ, "quoted_number_checks": quotes}
    (OUT / "swap_clocks.json").write_text(json.dumps(_jsonable(out), indent=1), encoding="utf-8")
    write_csv(res, OUT / "swap_levels.csv")
    print(f"  wrote {OUT / 'swap_clocks.json'} and {OUT / 'swap_levels.csv'}")
    make_figure(res, OUT / "fig_swap_clocks.pdf")


if __name__ == "__main__":
    main()
