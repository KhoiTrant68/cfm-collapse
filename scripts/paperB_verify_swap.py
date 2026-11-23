"""Independent verifier for the paper-B "swap" analysis (two clocks from the denoiser-swap runs).

Written without reading scripts/paperB_swap.py. Recomputes, directly from the per-sample files that
scripts/n3_swap.py saved, every headline number of that analysis, and checks them (and the swap
numbers quoted in paper_mechanism/main.tex sec:edm, SWAP_SUMMARY.md and NOTES_vi.md) at the stated precision.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_swap

numpy only. Outputs: results/paperB_20261121/verify_swap/{verify_swap.json, verify_swap_report.txt}.

Definitions (as in scripts/n3_swap.py):
  learned      network at every sigma;            exact  exact class posterior mean at every sigma
  net2exact@s  network for sigma > s, exact field for sigma <= s
  exact2net@s  exact field for sigma > s, network for sigma <= s
  off-atom     d1/d2 >= 1/3 at the endpoint (d1, d2: distances to nearest / second nearest training
               image of the class);  ':nn' = index of the nearest training image of the class.
  =L / =E      endpoint's nearest image equals that of the learned / exact endpoint.
"""
from __future__ import annotations

import json
import math
import pathlib
import re

import numpy as np

ROOT = pathlib.Path(".")
OUT = ROOT / "results/paperB_20261121/verify_swap"
FILES = {
    "public": ROOT / "results/n3_followup_20261111/swap_public/swap_per_sample.npz",
    "sub1000": ROOT / "results/n3_followup_20261111/swap_sub1000/swap_per_sample.npz",
    "sub500": ROOT / "results/n3_followup_sub500_20261111/swap_sub500/swap_per_sample.npz",
}
SUMMARIES = {
    "public": (ROOT / "results/n3_followup_20261111/SWAP_SUMMARY.md", "## swap_public"),
    "sub1000": (ROOT / "results/n3_followup_20261111/SWAP_SUMMARY.md", "## swap_sub1000"),
    "sub500": (ROOT / "results/n3_followup_sub500_20261111/SWAP_SUMMARY.md", "## swap_sub500"),
}
RATIO = 1.0 / 3.0
Z = 1.959963984540054
LINES: list[str] = []


def say(*a):
    s = " ".join(str(x) for x in a)
    LINES.append(s)
    print(s.encode("ascii", "replace").decode())


# ----------------------------------------------------------------------------- statistics
def wilson(k, n, z=Z):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def binom_cdf(k, n, p=0.5):
    # P(B <= k), exact via log-gamma
    tot = 0.0
    for i in range(0, k + 1):
        tot += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                        + i * math.log(p) + (n - i) * math.log(1 - p))
    return tot


def median_ci(x, level=0.95):
    """Distribution-free CI for the median: [x_(j), x_(k)] (1-indexed order statistics), symmetric,
    the narrowest with coverage >= level."""
    x = np.sort(np.asarray(x, float)); n = len(x)
    best = None
    for j in range(n // 2, 0, -1):
        k = n + 1 - j
        cov = binom_cdf(k - 1, n) - binom_cdf(j - 1, n)   # P(j <= B <= k-1)
        if cov >= level:
            best = (j, k, cov)
            break
    j, k, cov = best
    return float(np.median(x)), float(x[j - 1]), float(x[k - 1]), (j, k, cov)


def cross_level(s, y, thr, direction):
    """Level in s (log-linear interpolation) where y crosses thr.
    s is decreasing (5 -> 0.02). direction='up': y rises with decreasing s and we want the LARGEST s
    with y >= thr; direction='down': y falls with decreasing s, we want where y first drops to <= thr
    ... returned as the interpolated crossing. Returns (value, flag) with flag in
    {'ok','above' (already passed at the largest s), 'below' (never passed)}."""
    s = np.asarray(s, float); y = np.asarray(y, float)
    ok = (y >= thr) if direction == "up" else (y <= thr)
    if ok[0]:
        return (float("inf"), "above")
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return (0.0, "below")
    i = idx[0]                      # first level (from the top) meeting the threshold
    s_hi, s_lo, y_hi, y_lo = s[i - 1], s[i], y[i - 1], y[i]
    f = (thr - y_hi) / (y_lo - y_hi)
    return (float(math.exp(math.log(s_hi) + f * (math.log(s_lo) - math.log(s_hi)))), "ok")


def edm_sigmas(steps=18, smin=0.002, smax=80.0, rho=7.0):
    i = np.arange(steps, dtype=np.float64)
    return (smax ** (1 / rho) + i / (steps - 1) * (smin ** (1 / rho) - smax ** (1 / rho))) ** rho


def heun(den, x0, sig):
    """Copy of the EDM deterministic Heun sampler of scripts/n3_edm_memorization.py (sig ends with 0)."""
    x = x0 * sig[0]
    n = len(sig) - 1
    for i in range(n):
        tc, tn = sig[i], sig[i + 1]
        D = den(x, tc)
        d = (x - D) / tc
        xn = x + (tn - tc) * d
        if i < n - 1:
            d2 = (xn - den(xn, tn)) / tn
            xn = x + (tn - tc) * (0.5 * d + 0.5 * d2)
        x = xn
    return x


# ----------------------------------------------------------------------------- per model
def analyse(name, z):
    S = [float(s) for s in z["swap_sigmas"]]
    n = len(z["label"])
    off = lambda r: z[f"{r}:d1"] / z[f"{r}:d2"] >= RATIO  # noqa: E731
    nnL, nnE = z["learned:nn"], z["exact:nn"]
    res = {"n": n, "S": S, "learned_off": int(off("learned").sum()), "exact_off": int(off("exact").sum()),
           "learned_eq_exact": int((nnL == nnE).sum()),
           "learned_median_d1": float(np.median(z["learned:d1"])),
           "learned_median_ratio": float(np.median(z["learned:d1"] / z["learned:d2"])),
           "exact_max_d1": float(z["exact:d1"].max()), "levels": []}
    for s in S:
        a, b = f"net2exact@{s:g}", f"exact2net@{s:g}"
        lv = {"s": s}
        for tag, r in (("n2e", a), ("e2n", b)):
            k_off = int(off(r).sum()); k_L = int((z[f"{r}:nn"] == nnL).sum()); k_E = int((z[f"{r}:nn"] == nnE).sum())
            med, lo, hi, ranks = median_ci(z[f"{r}:d1"])
            lv[tag] = {"off": k_off, "off_ci": wilson(k_off, n), "eqL": k_L, "eqL_ci": wilson(k_L, n),
                       "eqE": k_E, "eqE_ci": wilson(k_E, n), "med_d1": med, "med_d1_ci": (lo, hi),
                       "med_d1_ranks": ranks, "max_d1": float(z[f"{r}:d1"].max()),
                       "med_ratio": float(np.median(z[f"{r}:d1"] / z[f"{r}:d2"])),
                       "med_absL": float(np.median(z[f"{r}:dist_to_learned"]))}
        res["levels"].append(lv)
    return res


def clocks_from(z, S, idx=None, axis=None):
    """Clock levels for one (possibly resampled) set of samples."""
    if idx is None:
        idx = np.arange(len(z["label"]))
    ax = S if axis is None else axis
    nnL, nnE = z["learned:nn"][idx], z["exact:nn"][idx]
    eqL = [np.mean(z[f"net2exact@{s:g}:nn"][idx] == nnL) for s in S]
    offE = [np.mean(z[f"exact2net@{s:g}:d1"][idx] / z[f"exact2net@{s:g}:d2"][idx] >= RATIO) for s in S]
    eqE = [np.mean(z[f"exact2net@{s:g}:nn"][idx] == nnE) for s in S]
    return {"s_sel": cross_level(ax, eqL, 0.9, "up"), "s_sel50": cross_level(ax, eqL, 0.5, "up"),
            "s_sel95": cross_level(ax, eqL, 0.95, "up"),
            "s_land": cross_level(ax, offE, 0.5, "down"), "s_land10": cross_level(ax, offE, 0.9, "down"),
            "s_land90": cross_level(ax, offE, 0.1, "down"), "s_keepE": cross_level(ax, eqE, 0.9, "up"),
            "eqL5": eqL[0]}


def _q(v, q):
    # censored replicates are +inf (already past at s=5) or 0 (never past); linear quantile unless that
    # would interpolate across inf, then the order statistic
    with np.errstate(invalid="ignore"):
        x = float(np.quantile(v, q))
    return x if np.isfinite(x) or np.isinf(x) else float(np.quantile(v, q, method="inverted_cdf"))


def bootstrap(z, S, B=4000, seed=7, axis=None, rng=None):
    """Paired bootstrap over samples. Returns {'nom': ..., 'eff': ...} when axis is given (both axes on the same
    resamples), else the nominal result."""
    rng = np.random.default_rng(seed) if rng is None else rng
    n = len(z["label"])
    keys = ["s_sel", "s_sel50", "s_land", "s_land90", "s_keepE"]
    axes = {"nom": None} if axis is None else {"nom": None, "eff": axis}
    res = {}
    outs = {ak: {k: [] for k in keys} for ak in axes}
    eq5 = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        for ak, ax in axes.items():
            c = clocks_from(z, S, idx, ax)
            for k in keys:
                outs[ak][k].append(c[k][0])
        eq5.append(c["eqL5"] >= 0.9)
    for ak in axes:
        res[ak] = _summ(outs[ak], keys)
        res[ak]["frac_eqL5_ge_09"] = float(np.mean(eq5))
    return res if axis is not None else res["nom"]


def _summ(out, keys):
    pct = lambda v: (_q(v, 0.025), _q(v, 0.975))  # noqa: E731
    r = {k: pct(np.array(out[k])) for k in keys}
    a = {k: np.array(out[k]) for k in keys}
    with np.errstate(divide="ignore", invalid="ignore"):
        r["sel_over_land"] = pct(a["s_sel"] / a["s_land"])
        r["keepE_over_land"] = pct(a["s_keepE"] / a["s_land"])
        r["sel50_over_land"] = pct(a["s_sel50"] / a["s_land"])
        r["sel90_over_land90"] = pct(a["s_sel"] / a["s_land90"])
        r["P_sel50_gt_land50"] = float(np.mean(a["s_sel50"] > a["s_land"]))
        r["P_sel90_gt_land90"] = float(np.mean(a["s_sel"] > a["s_land90"]))
        r["P_sel90_gt_land50"] = float(np.mean(a["s_sel"] > a["s_land"]))
    return r


# ----------------------------------------------------------------------------- SWAP_SUMMARY.md
def parse_summary(path, header):
    head, rows, on = None, [], False
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if ln.startswith(header):
            on = True
            m = re.search(r"n=(\d+); learned off-atom ([\d.]+), exact off-atom ([\d.]+), learned and exact share the nearest image ([\d.]+)", ln)
            head = [float(m.group(i)) for i in range(1, 5)]
            continue
        if on and ln.startswith("| ") and ln[2].isdigit():
            rows.append([float(c.strip()) for c in ln.strip().strip("|").split("|")])
        elif on and rows and not ln.startswith("|"):
            break
    return head, rows


# ----------------------------------------------------------------------------- synthetic construction check
def construction_demo(seed=3, d=3072, K=50, n=200):
    """Is 'net->exact ends on a training image' informative? Use a denoiser that never lands (the
    Gaussian posterior mean of a Gaussian fitted to the atoms) as 'network', the exact posterior mean
    as 'exact field', and EDM's 18-step Heun sampler. Report off-atom shares."""
    rng = np.random.default_rng(seed)
    Y = 0.3 * rng.standard_normal((K, d))
    mu = Y.mean(0); C = float(Y.var())
    sq = (Y ** 2).sum(1)

    def exact(x, s):
        lg = -((x ** 2).sum(1, keepdims=True) - 2 * x @ Y.T + sq[None]) / (2 * s * s)
        lg -= lg.max(1, keepdims=True); w = np.exp(lg); w /= w.sum(1, keepdims=True)
        return w @ Y

    def gauss(x, s):
        return mu + (C / (C + s * s)) * (x - mu)

    def offatom(x):
        d2 = np.clip((x ** 2).sum(1, keepdims=True) - 2 * x @ Y.T + sq[None], 0, None)
        v = np.sqrt(np.sort(d2, 1)[:, :2])
        return float(np.mean(v[:, 0] / v[:, 1] >= RATIO)), float(np.max(v[:, 0]))

    sig = np.concatenate([edm_sigmas(), [0.0]])
    x0 = rng.standard_normal((n, d))
    out = {"learned(gauss)": offatom(heun(gauss, x0, sig)), "exact": offatom(heun(exact, x0, sig))}
    # note: sigma_17 evaluates to 0.002000000000000003 > 0.002, so s=0.002 itself would NOT switch any level
    for s in (5, 1, 0.1, 0.02, 0.003, 0.002):
        den = (lambda sw: (lambda x, t: gauss(x, t) if t > sw else exact(x, t)))(s)
        out[f"net2exact@{s:g}"] = offatom(heun(den, x0, sig))
    # replace ONLY the final denoiser evaluation (the Euler step sigma = 0.002 -> 0; call 35 of 35)
    calls = [0]

    def only_last(x, t):
        calls[0] += 1
        return exact(x, t) if calls[0] == 2 * (len(sig) - 1) - 1 else gauss(x, t)
    out["only_final_eval_exact"] = offatom(heun(only_last, x0, sig))
    out["only_final_eval_exact_ncalls"] = (float(calls[0]), float("nan"))
    return out


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    Zs = {k: np.load(v) for k, v in FILES.items()}
    grid = edm_sigmas()
    say("EDM 18-step grid:", " ".join(f"{g:.4g}" for g in grid))
    for k, z in Zs.items():
        assert np.allclose(z["sigma"], grid), k
    S = [float(s) for s in Zs["public"]["swap_sigmas"]]
    brackets = {}
    for s in S:
        hi = float(grid[grid > s].min()); lo = float(grid[grid <= s].max())
        brackets[s] = (hi, lo, math.sqrt(hi * lo))
    say("hand-over brackets (last level with the first denoiser, first level with the second, geo-mean):")
    for s in S:
        say(f"  s={s:g}: ({brackets[s][0]:.4g}, {brackets[s][1]:.4g}) eff={brackets[s][2]:.4g}")
    eff_axis = [brackets[s][2] for s in S]

    R, C, BS, BSE = {}, {}, {}, {}
    # seed 20261121 = the seed the analysis states. One numpy default_rng continued across the models in the order
    # public, sub1000, sub500, one integers(0, n, n) draw per resample, both axes on the same resamples: this
    # reproduces its stated intervals exactly. A second seed (7) shows the Monte Carlo error (<= ~0.03).
    g = np.random.default_rng(20261121)
    for name, z in Zs.items():
        R[name] = analyse(name, z)
        C[name] = clocks_from(z, S)
        C[name + "_eff"] = clocks_from(z, S, axis=eff_axis)
        both = bootstrap(z, S, axis=eff_axis, rng=g)
        BS[name], BSE[name] = both["nom"], both["eff"]
        BS[name + "_seed7"] = bootstrap(z, S, B=2000, seed=7)
    # ------------------------------------------------------------------ tables
    for name in Zs:
        r = R[name]; n = r["n"]
        say(f"\n=== {name}: n={n}; learned off-atom {r['learned_off']}/{n}; exact off-atom {r['exact_off']}/{n}; "
            f"learned==exact nn {r['learned_eq_exact']}/{n}; learned median d1 {r['learned_median_d1']:.3f}, median d1/d2 {r['learned_median_ratio']:.3f}")
        say("  s     | n2e off  n2e =L [Wilson]          max d1   | e2n off [Wilson]          e2n =E [Wilson]          e2n =L | e2n med d1 [CI]        med d1/d2")
        for lv in r["levels"]:
            a, b = lv["n2e"], lv["e2n"]
            say(f"  {lv['s']:<5g} | {a['off']:3d}  {100*a['eqL']/n:5.1f} [{100*a['eqL_ci'][0]:5.1f},{100*a['eqL_ci'][1]:5.1f}]  {a['max_d1']:.2e} | "
                f"{100*b['off']/n:5.1f} [{100*b['off_ci'][0]:5.1f},{100*b['off_ci'][1]:5.1f}]  {100*b['eqE']/n:5.1f} [{100*b['eqE_ci'][0]:5.1f},{100*b['eqE_ci'][1]:5.1f}]  "
                f"{100*b['eqL']/n:5.1f} | {b['med_d1']:.3f} [{b['med_d1_ci'][0]:.3f},{b['med_d1_ci'][1]:.3f}]  {b['med_ratio']:.3f}")
        for key in ("s_sel", "s_sel50", "s_sel95", "s_land", "s_land10", "s_land90", "s_keepE"):
            v, f = C[name][key]; ve, fe = C[name + "_eff"][key]
            say(f"  {key:8s} nominal {v:.4g} ({f})   effective {ve:.4g} ({fe})")
        b = BS[name]
        say(f"  bootstrap (nominal, 4000, seed 20261121): s_sel {b['s_sel']}, s_sel50 {b['s_sel50']}, s_land {b['s_land']}, "
            f"s_keepE {b['s_keepE']}, sel/land {b['sel_over_land']}, keepE/land {b['keepE_over_land']}, "
            f"sel50/land {b['sel50_over_land']}, P(=L(5)>=0.9) {b['frac_eqL5_ge_09']:.3f}")
        say(f"  matched thresholds: s_land90 boot {b['s_land90']}; sel90/land90 {b['sel90_over_land90']}; "
            f"P(s_sel50 > s_land50) {b['P_sel50_gt_land50']:.3f}; P(s_sel90 > s_land90) {b['P_sel90_gt_land90']:.3f}; "
            f"P(s_sel90 > s_land50) {b['P_sel90_gt_land50']:.3f}")
        be = BSE[name]
        say(f"  bootstrap (effective, 4000, seed 20261121): s_sel {be['s_sel']}, s_land {be['s_land']}")
        b7 = BS[name + "_seed7"]
        say(f"  bootstrap (nominal, 2000, seed 7, Monte Carlo check): s_sel {b7['s_sel']}, s_land {b7['s_land']}, "
            f"sel50/land {b7['sel50_over_land']}")

    # ------------------------------------------------------------------ conditional analyses (sub500)
    z = Zs["sub500"]; n = len(z["label"])
    dis = z["learned:nn"] != z["exact:nn"]
    k = int(dis.sum())
    e = z["exact2net@5:nn"][dis]
    kE = int((e == z["exact:nn"][dis]).sum()); kL = int((e == z["learned:nn"][dis]).sum())
    koff = int((z["exact2net@5:d1"][dis] / z["exact2net@5:d2"][dis] >= RATIO).sum())
    lo = z["learned:d1"] / z["learned:d2"] >= RATIO
    eqL5 = z["net2exact@5:nn"] == z["learned:nn"]
    cond = {"n_disagree": k, "e2n5_eqE": (kE, wilson(kE, k)), "e2n5_eqL": (kL, wilson(kL, k)), "e2n5_off": koff,
            "learned_off_n": int(lo.sum()),
            "e2n_off_among_learned_off_all_s": int(sum((z[f"exact2net@{s:g}:d1"][lo] / z[f"exact2net@{s:g}:d2"][lo] >= RATIO).sum() for s in S)),
            "n2e5_eqL_learned_off": (int(eqL5[lo].sum()), int(lo.sum()), wilson(int(eqL5[lo].sum()), int(lo.sum()))),
            "n2e5_eqL_learned_on": (int(eqL5[~lo].sum()), int((~lo).sum()), wilson(int(eqL5[~lo].sum()), int((~lo).sum())))}
    say("\n=== sub500 conditional")
    say(f"  network-alone and exact choose different images: {k}/{n}")
    say(f"  exact2net@5 on exact's image {kE}/{k} = {100*kE/k:.1f}% {tuple(round(100*x,1) for x in wilson(kE,k))}; "
        f"on network's own {kL}/{k} = {100*kL/k:.1f}% {tuple(round(100*x,1) for x in wilson(kL,k))}; off-atom {koff}/{k}")
    a, nn_, w = cond["n2e5_eqL_learned_off"]; say(f"  net2exact@5 =L among learned off-atom: {a}/{nn_} = {100*a/nn_:.1f}% {tuple(round(100*x,1) for x in w)}")
    a, nn_, w = cond["n2e5_eqL_learned_on"]; say(f"  net2exact@5 =L among learned on-atom:  {a}/{nn_} = {100*a/nn_:.1f}% {tuple(round(100*x,1) for x in w)}")
    say(f"  exact2net off-atom among the {int(lo.sum())} learned off-atom samples, summed over all 8 s: {cond['e2n_off_among_learned_off_all_s']}")

    # ------------------------------------------------------------------ public d1 scaling and model estimate
    rp = R["public"]
    md = {lv["s"]: lv["e2n"]["med_d1"] for lv in rp["levels"]}
    slope = math.log(md[0.1] / md[0.02]) / math.log(0.1 / 0.02)
    sqd = math.sqrt(3072)
    say("\n=== public exact->net median d1 scaling")
    say(f"  log-log slope s=0.1 -> 0.02: {slope:.3f}")
    for s in (0.1, 0.05, 0.02):
        say(f"  s={s:g}: median d1 {md[s]:.3f}; sqrt(d)*sigma_hi {sqd*brackets[s][0]:.3f}; sqrt(d)*sigma_lo {sqd*brackets[s][1]:.3f}; "
            f"d1/s {md[s]/s:.1f}")
    r1 = R["sub1000"]
    say(f"  sub1000 exact->net median d1 s=5: {r1['levels'][0]['e2n']['med_d1']:.3f}, s=0.02: {r1['levels'][-1]['e2n']['med_d1']:.3f}")
    slopes = {}
    for name in ("public", "sub1000", "sub500"):
        mdn = {lv["s"]: lv["e2n"]["med_d1"] for lv in R[name]["levels"]}
        for a_, b_ in ((5, 0.5), (1, 0.1), (0.5, 0.05), (0.2, 0.02), (0.1, 0.02)):
            slopes[f"{name}:{a_:g}->{b_:g}"] = math.log(mdn[a_] / mdn[b_]) / math.log(a_ / b_)
    say("  log-log slopes of exact->net median d1 vs s: " + ", ".join(f"{k} {v:.2f}" for k, v in slopes.items()))
    # No-contraction baseline that respects the mixed Heun step: exact field collapsed (D=y) at sigma_hi,
    # network = identity at sigma_lo -> x_{k+1}-y = (x_k-y)(1+r)/2, r = sigma_lo/sigma_hi; |x_k-y| ~ sqrt(d) sigma_hi.
    heun_base = {}
    for s in (0.2, 0.1, 0.05, 0.02):
        hi, lo_, _ = brackets[s]; rr = lo_ / hi
        base_hi = sqd * hi; base_heun = sqd * hi * (1 + rr) / 2
        heun_base[s] = {"sqrt_d_sigma_hi": base_hi, "heun_no_contraction": base_heun, "measured": md[s],
                        "factor_vs_sigma_hi": base_hi / md[s], "factor_vs_heun": base_heun / md[s]}
        say(f"  s={s:g}: no-contraction baseline sqrt(d)*sigma_hi {base_hi:.3f} (factor {base_hi/md[s]:.2f}); "
            f"Heun-aware {base_heun:.3f} (factor {base_heun/md[s]:.2f}); measured median d1 {md[s]:.3f}")

    # ------------------------------------------------------------------ matched-threshold clock ordering
    say("\n=== clock ordering at matched thresholds (nominal s; selection = net->exact =L, landing = exact->net on-atom)")
    for name in ("public", "sub1000"):
        c = C[name]
        say(f"  {name}: 50%: sel {c['s_sel50'][0]:.3g} vs land {c['s_land'][0]:.3g};  90%: sel {c['s_sel'][0]:.3g} vs land {c['s_land90'][0]:.3g};"
            f"  task thresholds (sel 90% vs land 50%): {c['s_sel'][0]:.3g} vs {c['s_land'][0]:.3g}")

    # ------------------------------------------------------------------ sub500 =L by learned group at every s
    say("\n=== sub500 net->exact =L by learned group")
    z5 = Zs["sub500"]; lo5 = z5["learned:d1"] / z5["learned:d2"] >= RATIO
    byg = {}
    for s in S:
        e_ = z5[f"net2exact@{s:g}:nn"] == z5["learned:nn"]
        byg[s] = (int(e_[lo5].sum()), int(lo5.sum()), int(e_[~lo5].sum()), int((~lo5).sum()))
        say(f"  s={s:g}: learned off-atom {byg[s][0]}/{byg[s][1]}; learned on-atom {byg[s][2]}/{byg[s][3]}")
    say(f"\n  last grid level sigma_17 = {grid[-1]!r} (> 0.002: {bool(grid[-1] > 0.002)})")

    # ------------------------------------------------------------------ SWAP_SUMMARY.md recomputation
    say("\n=== SWAP_SUMMARY.md entries")
    worst, count = 0.0, 0
    for name, (path, hdr) in SUMMARIES.items():
        head, rows = parse_summary(path, hdr)
        r = R[name]; n = r["n"]
        mine_head = [n, r["learned_off"] / n, r["exact_off"] / n, r["learned_eq_exact"] / n]
        for x, y in zip(head, mine_head):
            worst = max(worst, abs(x - y)); count += 1
        for row, lv in zip(rows, r["levels"]):
            a, b = lv["n2e"], lv["e2n"]
            mine = [lv["s"], 1 / (1 + lv["s"]), a["off"] / n, a["eqL"] / n, a["eqE"] / n, a["med_d1"],
                    b["off"] / n, b["eqL"] / n, b["eqE"] / n, b["med_d1"], b["med_absL"]]
            for x, y in zip(row, mine):
                worst = max(worst, abs(x - y)); count += 1
    say(f"  {count} entries (incl. header n/learned-off/exact-off/share and the s,t columns); max |diff| = {worst:.2e}")

    # ------------------------------------------------------------------ construction demo
    demo = construction_demo()
    say("\n=== construction check (synthetic: 50 Gaussian atoms in d=3072; 'network' = Gaussian denoiser that never lands)")
    for kk, (fo, mx) in demo.items():
        if kk.endswith("_ncalls"):
            say(f"  denoiser calls per trajectory: {fo:.0f} (only the last one used the exact field above)")
            continue
        say(f"  {kk:22s} off-atom {100*fo:5.1f}%   max d1 {mx:.2e}")

    # ------------------------------------------------------------------ claims at stated precision
    pct = lambda name, s, tag, key: 100 * R[name]["levels"][S.index(s)][tag][key] / R[name]["n"]  # noqa: E731
    wl = lambda name, s, tag, key: tuple(100 * x for x in R[name]["levels"][S.index(s)][tag][key + "_ci"])  # noqa: E731
    checks = []

    def chk(label, claimed, value, tol):
        ok = abs(claimed - value) <= tol + 1e-12
        checks.append({"claim": label, "claimed": claimed, "recomputed": value, "tol": tol, "agrees": bool(ok)})

    for s, v in zip(S, (30.6, 56.0, 89.6, 95.6, 98.6, 99.6, 99.8, 100.0)):
        chk(f"public n2e =L s={s:g} (%)", v, pct("public", s, "n2e", "eqL"), 0.05)
    for s, v in zip(S, (49.2, 63.2, 88.0, 94.8, 98.2, 100, 100, 100)):
        chk(f"sub1000 n2e =L s={s:g} (%)", v, pct("sub1000", s, "n2e", "eqL"), 0.05)
    for s, v in zip(S, (92.8, 98.2, 99.6, 99.8, 100, 100, 100, 100)):
        chk(f"sub500 n2e =L s={s:g} (%)", v, pct("sub500", s, "n2e", "eqL"), 0.05)
    for s, v in ((5, 31), (2, 56), (1, 90), (0.2, 99), (0.02, 100)):
        chk(f"PAPER public n2e =L s={s:g} (%, integer)", v, pct("public", s, "n2e", "eqL"), 0.5)
    for s, v in ((5, 92.8), (2, 98.2), (1, 99.6), (0.2, 100), (0.1, 100), (0.05, 100), (0.02, 100)):
        chk(f"PAPER sub500 n2e =L s={s:g} (%)", v, pct("sub500", s, "n2e", "eqL"), 0.05)
    for name in Zs:
        for s in S:
            chk(f"{name} n2e off-atom s={s:g} (count)", 0, R[name]["levels"][S.index(s)]["n2e"]["off"], 0)
    chk("public n2e max d1 over s (x1e-6)", 7.1, 1e6 * max(lv["n2e"]["max_d1"] for lv in R["public"]["levels"]), 0.05)
    chk("sub1000 n2e max d1 over s (x1e-6)", 1.5, 1e6 * max(lv["n2e"]["max_d1"] for lv in R["sub1000"]["levels"]), 0.05)
    chk("sub500 n2e max d1 over s (x1e-6)", 1.5, 1e6 * max(lv["n2e"]["max_d1"] for lv in R["sub500"]["levels"]), 0.05)
    chk("Wilson upper 0/500 (%)", 0.76, 100 * wilson(0, 500)[1], 0.005)
    chk("public Wilson =L s=1 lo", 86.6, wl("public", 1, "n2e", "eqL")[0], 0.05)
    chk("public Wilson =L s=1 hi", 92.0, wl("public", 1, "n2e", "eqL")[1], 0.05)
    chk("sub500 Wilson =L s=5 lo", 90.2, wl("sub500", 5, "n2e", "eqL")[0], 0.05)
    chk("sub500 Wilson =L s=5 hi", 94.8, wl("sub500", 5, "n2e", "eqL")[1], 0.05)
    chk("public s_sel", 0.95, C["public"]["s_sel"][0], 0.005)
    chk("sub1000 s_sel", 0.82, C["sub1000"]["s_sel"][0], 0.005)
    checks.append({"claim": "sub500 s_sel > 5 (censored above)", "claimed": "above", "recomputed": C["sub500"]["s_sel"][1],
                   "agrees": C["sub500"]["s_sel"][1] == "above"})
    chk("public s_sel50", 2.48, C["public"]["s_sel50"][0], 0.005)
    chk("sub1000 s_sel50", 4.74, C["sub1000"]["s_sel50"][0], 0.005)
    chk("public s_sel boot lo", 0.74, BS["public"]["s_sel"][0], 0.005)
    chk("public s_sel boot hi", 1.05, BS["public"]["s_sel"][1], 0.005)
    chk("sub1000 s_sel boot lo", 0.65, BS["sub1000"]["s_sel"][0], 0.005)
    chk("sub1000 s_sel boot hi", 1.02, BS["sub1000"]["s_sel"][1], 0.005)
    chk("sub500 P(=L(5)>=0.9) (%)", 99.3, 100 * BS["sub500"]["frac_eqL5_ge_09"], 0.5)
    chk("public s_sel effective", 0.76, C["public_eff"]["s_sel"][0], 0.005)
    chk("public s_sel effective boot lo", 0.60, BSE["public"]["s_sel"][0], 0.005)
    chk("public s_sel effective boot hi", 0.86, BSE["public"]["s_sel"][1], 0.005)
    for s, v in zip(S, (100, 100, 95.6, 49.2, 7.0, 0.2, 0, 0)):
        chk(f"public e2n off s={s:g} (%)", v, pct("public", s, "e2n", "off"), 0.05)
    for s, v in zip(S, (97.4, 88.2, 23.2, 7.4, 1.0, 0, 0, 0)):
        chk(f"sub1000 e2n off s={s:g} (%)", v, pct("sub1000", s, "e2n", "off"), 0.05)
    for s in S:
        chk(f"sub500 e2n off s={s:g} (%)", 0, pct("sub500", s, "e2n", "off"), 0.0)
    chk("public s_land", 0.51, C["public"]["s_land"][0], 0.005)
    chk("public s_land boot lo", 0.47, BS["public"]["s_land"][0], 0.005)
    chk("public s_land boot hi", 0.54, BS["public"]["s_land"][1], 0.005)
    chk("public s_land effective", 0.42, C["public_eff"]["s_land"][0], 0.005)
    chk("public s_land effective boot lo", 0.39, BSE["public"]["s_land"][0], 0.005)
    chk("public s_land effective boot hi", 0.45, BSE["public"]["s_land"][1], 0.005)
    chk("public e2n =E s=1 (count)", 500, R["public"]["levels"][S.index(1)]["e2n"]["eqE"], 0)
    chk("public e2n off s=1 Wilson lo", 93.4, wl("public", 1, "e2n", "off")[0], 0.05)
    chk("public e2n off s=1 Wilson hi", 97.1, wl("public", 1, "e2n", "off")[1], 0.05)
    chk("public s_sel/s_land", 1.89, C["public"]["s_sel"][0] / C["public"]["s_land"][0], 0.005)
    chk("public s_sel/s_land boot lo", 1.47, BS["public"]["sel_over_land"][0], 0.005)
    chk("public s_sel/s_land boot hi", 2.15, BS["public"]["sel_over_land"][1], 0.005)
    chk("public s_keepE", 1.51, C["public"]["s_keepE"][0], 0.005)
    chk("public s_keepE boot lo", 1.41, BS["public"]["s_keepE"][0], 0.005)
    chk("public s_keepE boot hi", 1.66, BS["public"]["s_keepE"][1], 0.005)
    chk("public s_keepE/s_land", 2.99, C["public"]["s_keepE"][0] / C["public"]["s_land"][0], 0.005)
    chk("public s_keepE/s_land boot lo", 2.78, BS["public"]["keepE_over_land"][0], 0.005)
    chk("public s_keepE/s_land boot hi", 3.29, BS["public"]["keepE_over_land"][1], 0.005)
    chk("public s_sel50/s_land", 4.91, C["public"]["s_sel50"][0] / C["public"]["s_land"][0], 0.005)
    chk("public s_sel50/s_land boot lo", 4.19, BS["public"]["sel50_over_land"][0], 0.005)
    chk("public s_sel50/s_land boot hi", 5.75, BS["public"]["sel50_over_land"][1], 0.005)
    chk("public landing 10% level", 0.92, C["public"]["s_land10"][0], 0.005)
    chk("public landing 90% level", 0.21, C["public"]["s_land90"][0], 0.005)
    chk("sub1000 s_land", 1.33, C["sub1000"]["s_land"][0], 0.005)
    chk("sub1000 s_land/s_sel ratio (s_sel/s_land)", 0.61, C["sub1000"]["s_sel"][0] / C["sub1000"]["s_land"][0], 0.005)
    chk("sub1000 e2n on-atom s=1 (%)", 76.8, 100 - pct("sub1000", 1, "e2n", "off"), 0.05)
    chk("public e2n on-atom s=1 (%)", 4.4, 100 - pct("public", 1, "e2n", "off"), 0.05)
    chk("sub1000 s_land boot lo", 1.29, BS["sub1000"]["s_land"][0], 0.005)
    chk("sub1000 s_land boot hi", 1.37, BS["sub1000"]["s_land"][1], 0.005)
    chk("sub1000 sel/land boot lo", 0.49, BS["sub1000"]["sel_over_land"][0], 0.005)
    chk("sub1000 sel/land boot hi", 0.77, BS["sub1000"]["sel_over_land"][1], 0.005)
    chk("sub1000 e2n off s=1 Wilson lo", 19.7, wl("sub1000", 1, "e2n", "off")[0], 0.05)
    chk("sub1000 e2n off s=1 Wilson hi", 27.1, wl("sub1000", 1, "e2n", "off")[1], 0.05)
    chk("sub1000 s_keepE", 2.87, C["sub1000"]["s_keepE"][0], 0.005)
    chk("sub1000 s_keepE boot lo", 2.65, BS["sub1000"]["s_keepE"][0], 0.005)
    chk("sub1000 s_keepE boot hi", 3.16, BS["sub1000"]["s_keepE"][1], 0.005)
    for name, vals in (("public", (42.2, 83.2, 100)), ("sub1000", (78.4, 97.6, 100)), ("sub500", (95.4, 99.6, 100))):
        for s, v in zip((5, 2, 1), vals):
            chk(f"{name} e2n =E s={s:g} (%)", v, pct(name, s, "e2n", "eqE"), 0.05)
        chk(f"{name} e2n =E 100% for all s<=1", 1, int(all(lv["e2n"]["eqE"] == R[name]["n"] for lv in R[name]["levels"] if lv["s"] <= 1)), 0)
    chk("sub500 disagreement samples", 323, cond["n_disagree"], 0)
    chk("sub500 e2n@5 =E among disagreement (%)", 92.9, 100 * cond["e2n5_eqE"][0] / cond["n_disagree"], 0.05)
    chk("sub500 e2n@5 =E among disagreement Wilson lo", 89.5, 100 * cond["e2n5_eqE"][1][0], 0.05)
    chk("sub500 e2n@5 =E among disagreement Wilson hi", 95.2, 100 * cond["e2n5_eqE"][1][1], 0.05)
    chk("sub500 e2n@5 =L among disagreement (%)", 3.1, 100 * cond["e2n5_eqL"][0] / cond["n_disagree"], 0.05)
    chk("sub500 e2n@5 =L among disagreement Wilson lo", 1.7, 100 * cond["e2n5_eqL"][1][0], 0.05)
    chk("sub500 e2n@5 =L among disagreement Wilson hi", 5.6, 100 * cond["e2n5_eqL"][1][1], 0.05)
    chk("sub500 e2n@5 off among disagreement", 0, cond["e2n5_off"], 0)
    chk("sub500 e2n median d1 s=5", 1.67, R["sub500"]["levels"][0]["e2n"]["med_d1"], 0.005)
    chk("sub500 learned median d1", 1.71, R["sub500"]["learned_median_d1"], 0.005)
    chk("sub500 e2n median d1 s=0.02", 0.45, R["sub500"]["levels"][-1]["e2n"]["med_d1"], 0.005)
    chk("sub500 e2n med d1 s=5 CI lo", 1.62, R["sub500"]["levels"][0]["e2n"]["med_d1_ci"][0], 0.005)
    chk("sub500 e2n med d1 s=5 CI hi", 1.71, R["sub500"]["levels"][0]["e2n"]["med_d1_ci"][1], 0.005)
    chk("sub500 e2n med d1 s=0.02 CI lo", 0.44, R["sub500"]["levels"][-1]["e2n"]["med_d1_ci"][0], 0.005)
    chk("sub500 e2n med d1 s=0.02 CI hi", 0.45, R["sub500"]["levels"][-1]["e2n"]["med_d1_ci"][1], 0.005)
    chk("sub500 learned off-atom count", 19, cond["learned_off_n"], 0)
    chk("sub500 e2n off among learned-off, all s", 0, cond["e2n_off_among_learned_off_all_s"], 0)
    a, nn_, w = cond["n2e5_eqL_learned_off"]
    chk("sub500 n2e@5 =L learned-off (%)", 52.6, 100 * a / nn_, 0.05)
    chk("sub500 n2e@5 =L learned-off Wilson lo", 31.7, 100 * w[0], 0.05)
    chk("sub500 n2e@5 =L learned-off Wilson hi", 72.7, 100 * w[1], 0.05)
    a, nn_, w = cond["n2e5_eqL_learned_on"]
    chk("sub500 n2e@5 =L learned-on (%)", 94.4, 100 * a / nn_, 0.05)
    chk("sub500 n2e@5 =L learned-on Wilson lo", 92.0, 100 * w[0], 0.05)
    chk("sub500 n2e@5 =L learned-on Wilson hi", 96.1, 100 * w[1], 0.05)
    for s, v in zip((5, 1, 0.5, 0.1, 0.05), (18.9, 9.2, 6.5, 2.6, 1.4)):
        chk(f"public e2n median d1 s={s:g}", v, md[s], 0.05)
    chk("public e2n median d1 s=0.02", 0.61, md[0.02], 0.005)
    chk("public learned median d1", 20.0, R["public"]["learned_median_d1"], 0.05)
    chk("public e2n median d1/d2 s=5", 0.963, R["public"]["levels"][0]["e2n"]["med_ratio"], 0.0005)
    chk("public learned median d1/d2", 0.977, R["public"]["learned_median_ratio"], 0.0005)
    chk("public e2n med d1 s=1 CI lo", 9.04, R["public"]["levels"][S.index(1)]["e2n"]["med_d1_ci"][0], 0.005)
    chk("public e2n med d1 s=1 CI hi", 9.36, R["public"]["levels"][S.index(1)]["e2n"]["med_d1_ci"][1], 0.005)
    chk("public e2n med d1 s=0.02 CI lo", 0.600, R["public"]["levels"][-1]["e2n"]["med_d1_ci"][0], 0.0005)
    chk("public e2n med d1 s=0.02 CI hi", 0.615, R["public"]["levels"][-1]["e2n"]["med_d1_ci"][1], 0.0005)
    chk("public e2n d1 log-log slope 0.1->0.02", 0.9, slope, 0.05)
    chk("sub1000 e2n median d1 s=5", 14.5, R["sub1000"]["levels"][0]["e2n"]["med_d1"], 0.05)
    chk("sub1000 e2n median d1 s=0.02", 0.68, R["sub1000"]["levels"][-1]["e2n"]["med_d1"], 0.005)
    for s, v in ((0.1, 7.7), (0.05, 3.3), (0.02, 1.27)):
        prec = 0.005 if s == 0.02 else 0.05
        chk(f"sqrt(d)*sigma_last_exact s={s:g}", v, sqd * brackets[s][0], prec)
    chk("order-stat ranks lo (n=500)", 228, R["public"]["levels"][0]["e2n"]["med_d1_ranks"][0], 0)
    chk("order-stat ranks hi (n=500)", 273, R["public"]["levels"][0]["e2n"]["med_d1_ranks"][1], 0)
    chk("order-stat coverage", 0.956, R["public"]["levels"][0]["e2n"]["med_d1_ranks"][2], 0.0005)
    # NOTES_vi (public folder): public / sub1000 =L table, integers
    for name, vals in (("public", (31, 56, 90, 96, 99)), ("sub1000", (49, 63, 88, 95, 98))):
        for s, v in zip((5, 2, 1, 0.5, 0.2), vals):
            chk(f"NOTES {name} n2e =L s={s:g} (%, integer)", v, pct(name, s, "n2e", "eqL"), 0.5)
    for s, v in ((0.1, 2.6), (0.05, 1.4), (0.02, 0.6)):
        chk(f"NOTES public e2n median d1 s={s:g}", v, md[s], 0.05)
    chk("NOTES 's>=1 almost entirely off-atom' public s=1 (%)", 95.6, pct("public", 1, "e2n", "off"), 0.05)
    chk("NOTES sub500 abs-L ~27 (min over s)", 27, min(lv["e2n"]["med_absL"] for lv in R["sub500"]["levels"]), 0.5)
    chk("NOTES sub500 abs-L ~27 (max over s)", 27, max(lv["e2n"]["med_absL"] for lv in R["sub500"]["levels"]), 0.5)
    chk("NOTES sub500 learned off-atom 3.8%", 3.8, 100 * R["sub500"]["learned_off"] / 500, 0.05)

    say("\n=== claims checked at the stated precision")
    nbad = 0
    for c in checks:
        if not c["agrees"]:
            nbad += 1
        rv = c["recomputed"]
        rvs = f"{rv:.4g}" if isinstance(rv, (int, float)) else str(rv)
        say(f"  [{'OK ' if c['agrees'] else 'BAD'}] {c['claim']}: claimed {c['claimed']}, recomputed {rvs}")
    say(f"  {len(checks) - nbad}/{len(checks)} agree")

    js = {"files": {k: str(v) for k, v in FILES.items()}, "grid": grid.tolist(),
          "brackets": {f"{s:g}": brackets[s] for s in S}, "per_model": R,
          "clocks": {k: {kk: list(vv) if isinstance(vv, tuple) else vv for kk, vv in v.items()} for k, v in C.items()},
          "bootstrap_nominal": BS, "bootstrap_effective": BSE, "sub500_conditional": cond,
          "public_d1_slope": slope, "e2n_d1_slopes": slopes, "heun_no_contraction_baseline": {f"{k:g}": v for k, v in heun_base.items()},
          "sub500_eqL_by_learned_group": {f"{k:g}": v for k, v in byg.items()}, "sigma_17": float(grid[-1]),
          "construction_demo": demo, "checks": checks}
    (OUT / "verify_swap.json").write_text(json.dumps(js, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                                          encoding="utf-8")
    (OUT / "verify_swap_report.txt").write_text("\n".join(LINES), encoding="utf-8")


if __name__ == "__main__":
    main()
