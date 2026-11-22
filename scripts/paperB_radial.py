"""Paper B, analysis "radial": relative error rho versus the radial ratio of Theorem relerr on EDM CIFAR-10 models.

Theorem relerr (paper/main.tex, label thm:relerr), in EDM coordinates (proof of Prop. trap): along the
probability-flow ODE dx/dsigma = (x - D(x, sigma))/sigma and for a training image a, n = |x - a| obeys exactly
    d log n / d log sigma = 1 - rad,          rad = <(x - a)/n, D - a> / n,                  (part (a))
and, by Cauchy-Schwarz and eq. offmass, rad <= rho + omega/n with rho = |D - m*|/n, omega = (1 - w_a) max_k |x^k - a|.
(b): lands if rho <= rho_bar < 1 (plus vanishing terms). (c): does not land if rad >= 1 - delta with
int delta^+ dlog(1/sigma) < inf. rho ~ 1 is therefore necessary (when omega/n ~ 0) but not sufficient for rad ~ 1.
This script measures both on the saved per-sample data of scripts/n3_directional_q.py (18-step EDM Heun sampler):
  rad1 (toward the endpoint's nearest training image y1) and radA (toward the nearest training image of
  D(x_k), the predictive anchor), next to rho = err/n1 and rhoA = err/nA. Off-atom: d1/d2 >= 1/3.

Quantities
  per sigma and group (on/off/all): median and IQR of rho, rad1 (radA, rhoA); fractions rad1 >= 0.9/0.95/0.99, rad1 > 1,
    rho >= 0.95, rho >= 1; joint fractions (rho > 0.95 and rad1 < 0.9), (rad1 > 0.95 and rho < 0.9) and their conditional
    versions; "stalled" = rad1 >= thr at every level from sigma_j down to 0.002; AUC = P(off score > on score).
  late window (sigma_j <= 0.585, intervals j -> j+1 with sigma_{j+1} >= 0.002):
    S        = sum_j (1 - rad1_j)^+ log(sigma_j / sigma_{j+1})       (the discrete proxy of int delta^+ of (c), left point)
    S_trap   = the same with the trapezoidal rule;  S_signed_trap = trapezoid of (1 - rad1) (no positive part)
    C        = trapezoid of (1 - rho)  (the paper's late contraction, Table tab:edm-models)
    actual   = log(n1(0.585) / n1(0.002)) along the Heun trajectory (the ODE identity gives actual = S_signed)
    S_A      = S with radA (predictive anchor; the anchor may change between levels)
    S_early, C_early, S_A_early, C_A_early = the same sums (left point) over sigma 0.585 -> 0.140 only, which use the
             field at sigma >= 0.296; with the predictive anchor they use no information after sigma = 0.296
  AUCs with 95% stratified bootstrap intervals (B = 2000, paired for differences), against C and against the
  nearest-neighbour baseline dD (distance from D to its nearest training image) at sigma = 0.002, and for the early sums
  at sigma = 0.296. Since actual = S_signed up to the Heun discretisation and n1 at sigma = 0.002 is the endpoint distance
  d1 that defines the off-atom label, the AUC of the full-window S is largely bookkeeping; the early sums are not.
  checks: rad1 = q1 + r1 (q1 is a 4-point midpoint quadrature, so this checks the quadrature), rad1 <= rho + omega/n1
  (pointwise, every file with omega), C_omega <= S_signed (integrated), and for the final Euler step x_K = D(x_{K-1}):
  rad1_{K-1} <= n1_end / n1_{K-1} <= rho_{K-1} + omega_{K-1}/n1_{K-1}.
  (b) on the finite window: fraction with max_j rho_j < rho_bar over [0.585, sigma_end]; step-count robustness of S
  with the 36- and 64-step runs.

Outputs in results/paperB_20261121/radial/: per_sigma_<model>.csv, late_<model>.npz (per-sample integrals),
radial_numbers.json (every number with its source file), radial_tables.md.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_radial
"""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np

R = pathlib.Path("results")
OUT = R / "paperB_20261121" / "radial"
RATIO = 1.0 / 3.0                  # off-atom: d1/d2 >= 1/3 (scripts/n3_edm_memorization.RATIO)
SIG_LATE = 0.5854                  # late window sigma <= 0.585 (the paper's C starts at sigma_11 = 0.5853)
B = 2000
SEED = 0
THR = (0.9, 0.95, 0.99)
RHO_HI, RAD_LO = 0.95, 0.9         # joint "rho ~ 1 but rad1 clearly < 1"
RAD_HI, RHO_LO = 0.95, 0.9         # joint "rad1 ~ 1 but rho clearly < 1"
SHOW = (9, 10, 11, 12, 13, 14, 15, 16, 17)   # 18-step indices shown in the markdown: sigma 1.92 ... 0.002
B_END = (13, 15, 17)               # (b) window ends: sigma 0.140, 0.023, 0.002
B_RHOBAR = (0.9, 0.95, 0.99, 1.0)

MODELS = [  # name, main file, aux file with the same latents (anchor and omega keys), description
    ("sub500", "n3_rho_20261117/sub500/q_per_sample.npz", "n3_anchor_20261117/sub500/q_per_sample.npz",
     "first 500-image model (subset/training seed 0), 1000 samples"),
    ("sub2000", "n3_rho2_20261118/sub2000/q_per_sample.npz", None, "2000-image model (seed 0), 1000 samples"),
    ("sub500s1", "n3_rho2_20261118/sub500s1/q_per_sample.npz", None, "second 500-image model (seed 1), 1000 samples"),
    ("public", "n3_rho_20261117/public/q_per_sample.npz", None, "public 50k model, 200 samples (all off-atom)"),
    ("public500", "n3_anchor_20261117/public/q_per_sample.npz", None,
     "public 50k model, 500 samples of the anchor run (all off-atom)"),
]
OMEGA_FILES = ["n3_anchor_20261117/sub500/q_per_sample.npz", "n3_rho2_20261118/sub2000/q_per_sample.npz",
               "n3_rho2_20261118/sub500s1/q_per_sample.npz", "n3_anchor_20261117/public/q_per_sample.npz"] + \
              [f"n3_steps_20261117/s{S}/{m}/q_per_sample.npz" for S in (18, 36, 64) for m in ("sub500", "public")]
IDENTITY_FILES = ["n3_rho_20261117/sub500/q_per_sample.npz", "n3_rho_20261117/public/q_per_sample.npz"]
STEP_FILES = [(S, f"n3_steps_20261117/s{S}/sub500/q_per_sample.npz") for S in (18, 36, 64)]


# --------------------------------------------------------------------------- helpers
def load(rel):
    z = np.load(R / rel)
    return {k: z[k] for k in z.files}


def finite(z, k):
    return k in z and np.isfinite(z[k]).any()


def auc(pos, neg):
    """P(pos > neg) + P(pos = neg)/2 (Mann-Whitney with average ranks), as scripts/n3_edm_memorization.auc."""
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    x = np.concatenate([pos, neg]); s = np.sort(x)
    r = 0.5 * (np.searchsorted(s, x, "left") + np.searchsorted(s, x, "right") + 1)
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot(scores, off, seed, pairs=()):
    """AUC point estimates and 95% stratified-bootstrap intervals; differences are paired (same resample)."""
    rng = np.random.default_rng(seed)
    io, ii = np.flatnonzero(off), np.flatnonzero(~off)
    est = {k: auc(v[off], v[~off]) for k, v in scores.items()}
    for a, b in pairs:
        est[f"{a}-{b}"] = est[a] - est[b]
    draws = {k: np.empty(B) for k in est}
    for t in range(B):
        so, si = rng.choice(io, len(io)), rng.choice(ii, len(ii))
        d = {k: auc(v[so], v[si]) for k, v in scores.items()}
        for a, b in pairs:
            d[f"{a}-{b}"] = d[a] - d[b]
        for k in est:
            draws[k][t] = d[k]
    return {k: [float(est[k]), *(float(v) for v in np.nanpercentile(draws[k], [2.5, 97.5]))] for k in est}


def q3(v):
    v = v[np.isfinite(v)]
    return [float(x) for x in np.percentile(v, [25, 50, 75])] if len(v) else [float("nan")] * 3


def mean(m):
    return float(np.mean(m)) if m.size else float("nan")


def f3(v, nd=3):
    return "-" if v is None or v != v else f"{v:.{nd}f}"


def pct(v, nd=1):
    return "-" if v is None or v != v else f"{100 * v:.{nd}f}%"


def med_iqr(q, nd=3):
    return "-" if q[1] != q[1] else f"{q[1]:.{nd}f} [{q[0]:.{nd}f}, {q[2]:.{nd}f}]"


def ci(e, nd=3):
    return f"{e[0]:.{nd}f} [{e[1]:.{nd}f}, {e[2]:.{nd}f}]"


def groups(z):
    off = z["d1"] / z["d2"] >= RATIO
    return {"on": ~off, "off": off, "all": np.ones_like(off)}, off


def stalled(rad, thr):
    """allok[:, j]: rad >= thr at every level j' >= j (down to the last level, sigma = 0.002)."""
    ok = rad >= thr
    allok = np.zeros_like(ok)
    allok[:, -1] = ok[:, -1]
    for j in range(ok.shape[1] - 2, -1, -1):
        allok[:, j] = ok[:, j] & allok[:, j + 1]
    return allok


def late_window(sig):
    """Intervals j -> j+1 inside sigma <= SIG_LATE (the last sampler level is sigma = 0.002; sigma_K = 0 is excluded)."""
    j = np.flatnonzero(sig[:-1] <= SIG_LATE)
    return j, np.log(sig[j] / sig[j + 1])


def integrals(z, rad, rho):
    """Per-sample late-window integrals (see module docstring)."""
    sig = z["sigma"]; j, dl = late_window(sig); j0, jl = j[0], j[-1] + 1
    dp = np.clip(1 - rad, 0, None); ds = 1 - rad; dr = 1 - rho
    trap = lambda v: (0.5 * (v[:, j] + v[:, j + 1]) * dl).sum(1)  # noqa: E731
    je = j[sig[j + 1] >= 0.1394]; dle = np.log(sig[je] / sig[je + 1])    # early part: sigma 0.585 -> 0.140, left point
    out = {"S_early": (dp[:, je] * dle).sum(1), "C_early": (dr[:, je] * dle).sum(1),
           "S": (dp[:, j] * dl).sum(1), "S_trap": trap(dp), "S_signed_left": (ds[:, j] * dl).sum(1),
           "S_signed_trap": trap(ds), "C": trap(dr), "C_left": (dr[:, j] * dl).sum(1),
           "actual": np.log(z["n1"][:, j0] / z["n1"][:, jl]), "actual_total": np.log(z["n1"][:, j0] / z["n1_end"]),
           "tail_frac": (dp[:, j] * dl)[:, sig[j] <= 0.0230].sum(1) / np.maximum((dp[:, j] * dl).sum(1), 1e-300)}
    return out, dict(j0=int(j0), j_last=int(jl), sigma_from=float(sig[j0]), sigma_to=float(sig[jl]),
                     n_intervals=int(len(j)), sum_dlog=float(dl.sum()))


# --------------------------------------------------------------------------- per-model analysis
def per_sigma(z, G, off):
    rho = z["err"] / z["n1"]; rad = z["rad1"]
    anc = finite(z, "radA")
    stall = {t: stalled(rad, t) for t in THR}
    rows = []
    for i, s in enumerate(z["sigma"]):
        r = {"i": i, "sigma": float(s), "n_on": int(G["on"].sum()), "n_off": int(G["off"].sum())}
        for g, sel in G.items():
            ro, ra = rho[sel, i], rad[sel, i]
            for name, v in (("rho", ro), ("rad1", ra)):
                r[f"{name}_{g}_q25"], r[f"{name}_{g}_med"], r[f"{name}_{g}_q75"] = q3(v)
            for t in THR:
                r[f"rad1_ge{t}_{g}"] = mean(ra >= t)
                r[f"stall{t}_{g}"] = mean(stall[t][sel, i])
            r[f"rad1_gt1_{g}"] = mean(ra > 1)
            r[f"rho_ge0.95_{g}"] = mean(ro >= 0.95)
            r[f"rho_ge1_{g}"] = mean(ro >= 1)
            hilo = (ro > RHO_HI) & (ra < RAD_LO); lohi = (ra > RAD_HI) & (ro < RHO_LO)
            r[f"n_rhohi_{g}"] = int((ro > RHO_HI).sum())
            r[f"rhohi_radlo_{g}"] = mean(hilo)
            r[f"radlo_given_rhohi_{g}"] = float(hilo.sum() / (ro > RHO_HI).sum()) if (ro > RHO_HI).any() else float("nan")
            r[f"radhi_rholo_{g}"] = mean(lohi)
            r[f"rholo_given_radhi_{g}"] = float(lohi.sum() / (ra > RAD_HI).sum()) if (ra > RAD_HI).any() else float("nan")
            r[f"ratio_{g}_med"] = q3(ra / ro)[1]                     # rad1/rho = cosine of (x - y1, D - y1) when omega ~ 0
            if anc:
                for name in ("radA", "rhoA"):
                    r[f"{name}_{g}_q25"], r[f"{name}_{g}_med"], r[f"{name}_{g}_q75"] = q3(z[name][sel, i])
                r[f"radA_ge0.95_{g}"] = mean(z["radA"][sel, i] >= 0.95)
                hA = (z["rhoA"][sel, i] > RHO_HI) & (z["radA"][sel, i] < RAD_LO)
                r[f"rhoAhi_radAlo_{g}"] = mean(hA)
                r[f"anchor_agree_{g}"] = mean(z["anc"][sel, i] == z["nn1"][sel])
            if finite(z, "omega"):
                r[f"omega_over_n1_{g}_max"] = float(np.max(z["omega_over_n1"][sel, i])) if sel.any() else float("nan")
        if G["on"].any() and G["off"].any():
            r["auc_rho"] = auc(rho[off, i], rho[~off, i]); r["auc_rad1"] = auc(rad[off, i], rad[~off, i])
            if anc:
                for k in ("radA", "rhoA", "dD"):
                    r[f"auc_{k}"] = auc(z[k][off, i], z[k][~off, i])
        rows.append(r)
    return rows


def b_hypothesis(z, G):
    """(b) on the finite window with gamma = 0: fraction with max_j rho_j < rho_bar for sigma_j in [sigma_end, 0.585]."""
    rho = z["err"] / z["n1"]; j0 = int(np.flatnonzero(z["sigma"] <= SIG_LATE)[0]); res = {}
    for je in B_END:
        if je >= len(z["sigma"]):
            continue
        mx = rho[:, j0:je + 1].max(1)
        for rb in B_RHOBAR:
            for g, sel in G.items():
                res[f"sigma{z['sigma'][je]:.3g}_rhobar{rb}_{g}"] = mean(mx[sel] < rb)
    return res


def stall_sigma(z, G):
    """Median over each group of the largest sigma from which rad1 >= thr holds at every later level."""
    sig = z["sigma"]; out = {}
    for t in THR:
        allok = stalled(z["rad1"], t)
        first = np.where(allok.any(1), allok.argmax(1), len(sig))          # len(sig): never within the schedule
        for g, sel in G.items():
            if not sel.any():
                continue
            m = int(np.quantile(first[sel], 0.5, method="inverted_cdf"))     # lower median of the level index
            out[f"thr{t}_{g}"] = {"median_sigma": float(sig[m]) if m < len(sig) else None,
                                  "frac_never": mean(first[sel] == len(sig)),
                                  "frac_by_sigma0.140": mean(first[sel] <= 13), "frac_by_sigma0.060": mean(first[sel] <= 14),
                                  "frac_by_sigma0.023": mean(first[sel] <= 15)}
    return out


def joint_totals(z, G):
    """Cells (sample x level) with rho > 0.95 and rad1 < 0.9, and with rad1 > 0.95 and rho < 0.9, summed over levels."""
    rho = z["err"] / z["n1"]; rad = z["rad1"]; out = {}
    for g, sel in G.items():
        if not sel.any():
            continue
        ro, ra = rho[sel], rad[sel]
        out[g] = {"cells": int(ro.size), "rho_gt0.95": int((ro > RHO_HI).sum()),
                  "rho_gt0.95_and_rad1_lt0.9": int(((ro > RHO_HI) & (ra < RAD_LO)).sum()),
                  "rad1_gt0.95": int((ra > RAD_HI).sum()),
                  "rad1_gt0.95_and_rho_lt0.9": int(((ra > RAD_HI) & (ro < RHO_LO)).sum()),
                  "min_rad1_given_rho_gt0.95": float(ra[ro > RHO_HI].min()) if (ro > RHO_HI).any() else None}
    return out


def context(z, G):
    """Endpoint distances and the trajectory distance to y1 at the window ends (medians by group)."""
    j, _ = late_window(z["sigma"]); j0, jl = j[0], j[-1] + 1; out = {}
    for g, sel in G.items():
        if not sel.any():
            continue
        out[g] = {"d1": q3(z["d1"][sel]), "d2": q3(z["d2"][sel]), "d1_over_d2": q3(z["d1"][sel] / z["d2"][sel]),
                  "n1_window_start": q3(z["n1"][sel, j0]), "n1_last_level": q3(z["n1"][sel, jl]),
                  "n1_end": q3(z["n1_end"][sel])}
        if finite(z, "omega"):
            late = z["sigma"] <= SIG_LATE; w = z["omega_over_n1"][sel][:, late]
            out[g].update({"omega_over_n1_late_p99": float(np.percentile(w, 99)), "omega_over_n1_late_max": float(w.max()),
                           "frac_late_cells_omega_over_n1_gt0.01": mean(w > 0.01)})
    return out


def per_interval(z, G):
    """Heun step versus the ODE identity per late interval: log(n_j/n_{j+1}) - trapezoid of (1 - rad1)."""
    j, dl = late_window(z["sigma"]); rad = z["rad1"]; rows = []
    for jj, d in zip(j, dl):
        act = np.log(z["n1"][:, jj] / z["n1"][:, jj + 1]); tr = 0.5 * ((1 - rad[:, jj]) + (1 - rad[:, jj + 1])) * d
        rows.append({"from": float(z["sigma"][jj]), "to": float(z["sigma"][jj + 1]), "dlog": float(d),
                     **{f"actual_{g}": q3(act[sel])[1] for g, sel in G.items() if sel.any()},
                     **{f"trap_{g}": q3(tr[sel])[1] for g, sel in G.items() if sel.any()},
                     **{f"diff_{g}": q3((act - tr)[sel])[1] for g, sel in G.items() if sel.any()}})
    return rows


def late_analysis(name, z, G, off, src):
    rho = z["err"] / z["n1"]
    I, win = integrals(z, z["rad1"], rho)
    if finite(z, "radA"):
        IA, _ = integrals(z, z["radA"], z["rhoA"]); I["S_A"] = IA["S"]
        I["S_A_early"] = IA["S_early"]; I["C_A_early"] = IA["C_early"]
    res = {"window": win, "source": src, "per_interval": per_interval(z, G)}
    for k, v in I.items():
        res[f"{k}_q"] = {g: q3(v[sel]) for g, sel in G.items() if sel.any()}
    # Heun trajectory versus the ODE identity, and the continuous bound actual <= S_trap
    d = I["actual"] - I["S_signed_trap"]
    res["actual_minus_Ssigned_q"] = {g: q3(d[sel]) for g, sel in G.items() if sel.any()}
    res["corr_actual_Ssigned"] = float(np.corrcoef(I["actual"], I["S_signed_trap"])[0, 1])
    res["frac_actual_gt_Strap"] = {g: mean(I["actual"][sel] > I["S_trap"][sel]) for g, sel in G.items() if sel.any()}
    if G["on"].any() and G["off"].any():
        sc = {"S": -I["S"], "S_trap": -I["S_trap"], "S_signed_trap": -I["S_signed_trap"], "C": -I["C"],
              "actual": -I["actual"]}
        pairs = [("S", "C")]
        sc["S_early"] = -I["S_early"]; sc["C_early"] = -I["C_early"]
        if "S_A" in I:
            sc["S_A"] = -I["S_A"]; sc["S_A_early"] = -I["S_A_early"]; sc["C_A_early"] = -I["C_A_early"]
        if finite(z, "dD"):
            je = int(np.flatnonzero(np.isclose(z["sigma"], 0.2964, rtol=1e-3))[0])   # last level used by the early sums
            sc["dD_end"] = z["dD"][:, -1]; sc["dD_0.296"] = z["dD"][:, je]; pairs += [("S", "dD_end")]
            if "S_A" in I:
                pairs += [("S_A", "dD_end"), ("S_A_early", "dD_0.296"), ("S_A_early", "C_A_early")]
        res["auc"] = boot(sc, off, SEED, pairs=pairs)
    np.savez_compressed(OUT / f"late_{name}.npz", off=off, sigma=z["sigma"], **I)
    return res


# --------------------------------------------------------------------------- checks
def inequality_check(rel):
    z = load(rel); G, off = groups(z)
    rho = z["err"] / z["n1"]; on1 = z["omega"] / z["n1"]; viol = z["rad1"] - (rho + on1)
    j, dl = late_window(z["sigma"])
    trap = lambda v: (0.5 * (v[:, j] + v[:, j + 1]) * dl).sum(1)  # noqa: E731
    Cw, Ss = trap(1 - rho - on1), trap(1 - z["rad1"])
    lo = z["rad1"][:, -1]; ratio = z["n1_end"] / z["n1"][:, -1]; hi = rho[:, -1] + on1[:, -1]
    late = z["sigma"] <= SIG_LATE
    return {"source": f"results/{rel}", "n_samples": int(len(off)), "n_off": int(off.sum()), "n_cells": int(viol.size),
            "n_viol_gt0": int((viol > 0).sum()), "n_viol_gt1e-9": int((viol > 1e-9).sum()), "max_viol": float(viol.max()),
            "max_omega_over_n1_late_on": float(on1[~off][:, late].max()) if (~off).any() else None,
            "max_omega_over_n1_late_off": float(on1[off][:, late].max()) if off.any() else None,
            "median_omega_over_n1_late": float(np.median(on1[:, late])),
            "max_omega_over_n1_all": float(on1.max()),
            "n_Comega_gt_Ssigned": int((Cw > Ss + 1e-9).sum()), "max_Comega_minus_Ssigned": float((Cw - Ss).max()),
            "last_step_lower_viol": int((lo > ratio * (1 + 1e-9) + 1e-12).sum()),
            "last_step_upper_viol": int((ratio > hi * (1 + 1e-9) + 1e-12).sum()),
            "last_step_max_lower_minus_ratio": float((lo - ratio).max()),
            "last_step_max_ratio_minus_upper": float((ratio - hi).max())}


def identity_check(rel):
    z = load(rel); G, off = groups(z)
    dev = z["rad1"] - z["q1"] - z["r1"]; a = np.abs(dev)
    per = [{"sigma": float(s), "max_abs": float(a[:, i].max()), "median_abs": float(np.median(a[:, i])),
            "p99_abs": float(np.percentile(a[:, i], 99)), "median_abs_on": float(np.median(a[~off, i])) if (~off).any() else None,
            "median_abs_off": float(np.median(a[off, i])) if off.any() else None,
            "median_rad1": float(np.median(z["rad1"][:, i])), "median_dev": float(np.median(dev[:, i])),
            "median_q1_plus_r1": float(np.median(z["q1"][:, i] + z["r1"][:, i])),
            "median_qx1": float(np.median(z["qx1"][:, i])),           # the integrand at the end point tau = 1 (x itself)
            "frac_abs_gt_0.05": mean(a[:, i] > 0.05)} for i, s in enumerate(z["sigma"])]
    return {"source": f"results/{rel}", "n_samples": int(len(off)), "max_abs_dev": float(a.max()),
            "sigma_at_max": float(z["sigma"][np.unravel_index(a.argmax(), a.shape)[1]]),
            "max_abs_dev_sigma_ge_1.9": float(a[:, z["sigma"] >= 1.9].max()),
            "max_abs_dev_sigma_le_0.0075": float(a[:, z["sigma"] <= 0.0076].max()),
            "frac_cells_abs_gt_0.05": mean(a > 0.05),
            "corr_absdev_n1_over_sigma_late": float(np.corrcoef(a[:, z["sigma"] <= SIG_LATE].ravel(),
                                                                (z["n1"] / z["sigma"])[:, z["sigma"] <= SIG_LATE].ravel())[0, 1]),
            "per_sigma": per}


def step_robustness():
    out = []
    for S, rel in STEP_FILES:
        z = load(rel); G, off = groups(z); rho = z["err"] / z["n1"]
        I, win = integrals(z, z["rad1"], rho)
        e = boot({"S": -I["S"], "S_trap": -I["S_trap"], "C": -I["C"]}, off, SEED, pairs=[("S", "C")])
        out.append({"steps": S, "source": f"results/{rel}", "window": win, "n_off": int(off.sum()),
                    "S_med_on": float(np.median(I["S"][~off])), "S_med_off": float(np.median(I["S"][off])),
                    "S_trap_med_on": float(np.median(I["S_trap"][~off])), "S_trap_med_off": float(np.median(I["S_trap"][off])),
                    "C_med_on": float(np.median(I["C"][~off])), "C_med_off": float(np.median(I["C"][off])),
                    "auc": e, "rad1_ge0.95_last_on": mean(z["rad1"][~off, -1] >= 0.95),
                    "rad1_ge0.95_last_off": mean(z["rad1"][off, -1] >= 0.95)})
    return out


# --------------------------------------------------------------------------- main
def load_model(name, main, aux):
    z = load(main); notes = {"main": f"results/{main}"}
    if aux:
        x = load(aux)
        same = (np.array_equal(z["label"], x["label"]) and
                np.max(np.abs(z["n1"][:, 0] - x["n1"][:, 0]) / z["n1"][:, 0]) < 1e-6 and
                np.array_equal(z["d1"] / z["d2"] >= RATIO, x["d1"] / x["d2"] >= RATIO))
        notes.update(aux=f"results/{aux}", aux_aligned=bool(same),
                     aux_max_abs_diff_rad1=float(np.max(np.abs(z["rad1"] - x["rad1"]))),
                     aux_max_abs_diff_rho=float(np.max(np.abs(z["err"] / z["n1"] - x["err"] / x["n1"]))),
                     aux_max_rel_diff_n1_sigma80=float(np.max(np.abs(z["n1"][:, 0] - x["n1"][:, 0]) / z["n1"][:, 0])))
        if not same:
            raise SystemExit(f"{aux} is not aligned with {main}")
        for k in ("omega", "anc", "nn1", "radA", "rhoA", "nA", "dD"):
            z[k] = x[k]
        z["omega_over_n1"] = x["omega"] / x["n1"]                       # omega and n1 from the same run
    elif finite(z, "omega"):
        z["omega_over_n1"] = z["omega"] / z["n1"]
    return z, notes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    numbers = {"definitions": {
        "off_atom": "d1/d2 >= 1/3", "rho": "err/n1", "rad1": "<(x-y1)/n1, D(x)-y1>/n1",
        "S": "sum_{j: sigma_j<=0.585, sigma_{j+1}>=0.002} (1-rad1_j)^+ log(sigma_j/sigma_{j+1}) (left point)",
        "C": "trapezoid of (1-rho) over the same intervals (paper's late contraction)",
        "actual": "log(n1(sigma=0.585)/n1(sigma=0.002)) along the Heun trajectory",
        "AUC": "P(off-atom score > on-atom score); contraction scores enter with a minus sign",
        "bootstrap": f"stratified, B={B}, seed {SEED}, percentile 95% interval, paired differences"}}
    md = ["# Paper B, radial analysis: relative error rho versus radial ratio rad1", "",
          "Generated by `scripts/paperB_radial.py`. Off-atom: d1/d2 >= 1/3. AUC = P(off-atom score > on-atom score). "
          "Medians with [25%, 75%] quantiles. rho = err/n1, rad1 = <(x-y1)/n1, D-y1>/n1 (y1 = endpoint's nearest "
          "training image of the class); radA, rhoA use the nearest training image of D(x_k) instead.", ""]
    for name, main_rel, aux_rel, desc in MODELS:
        z, notes = load_model(name, main_rel, aux_rel)
        G, off = groups(z)
        rows = per_sigma(z, G, off)
        with open(OUT / f"per_sigma_{name}.csv", "w", newline="", encoding="utf-8") as fh:
            keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("i", "sigma", "n_on", "n_off"), k))
            w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
        entry = {"description": desc, "sources": notes, "n": int(len(off)), "n_off": int(off.sum()),
                 "per_sigma": rows, "b_hypothesis": b_hypothesis(z, G), "stall": stall_sigma(z, G),
                 "joint_totals": joint_totals(z, G), "context": context(z, G)}
        entry["late"] = late_analysis(name, z, G, off, notes)
        numbers[name] = entry
        # ---- markdown
        has_on = G["on"].any()
        md += [f"## {name}: {desc}", "", f"Sources: {notes}", "",
               f"n = {len(off)}, off-atom {int(off.sum())} ({100 * off.mean():.1f}%).", "",
               "| sigma | rho on | rad1 on | rho off | rad1 off | AUC rho | AUC rad1 | median rad1/rho on | off |",
               "|---|---|---|---|---|---|---|---|---|"]
        for i in SHOW:
            r = rows[i]
            md.append(f"| {r['sigma']:.3g} | " + " | ".join([
                med_iqr([r["rho_on_q25"], r["rho_on_med"], r["rho_on_q75"]]),
                med_iqr([r["rad1_on_q25"], r["rad1_on_med"], r["rad1_on_q75"]]),
                med_iqr([r["rho_off_q25"], r["rho_off_med"], r["rho_off_q75"]]),
                med_iqr([r["rad1_off_q25"], r["rad1_off_med"], r["rad1_off_q75"]]),
                f3(r.get("auc_rho")), f3(r.get("auc_rad1")), f3(r["ratio_on_med"]), f3(r["ratio_off_med"])]) + " |")
        md += ["", "Fractions (on / off): rad1 >= 0.95; rho >= 0.95; rho > 0.95 and rad1 < 0.9 [conditional on rho > 0.95]; "
               "rad1 > 0.95 and rho < 0.9; stalled = rad1 >= 0.95 at every level from sigma down to 0.002.", "",
               "| sigma | rad1>=0.95 | rad1>1 | rho>=0.95 | rho>=1 | rho>.95 & rad1<.9 | P(rad1<.9 given rho>.95) | rad1>.95 & rho<.9 | stalled (0.95) |",
               "|---|---|---|---|---|---|---|---|---|"]
        for i in SHOW:
            r = rows[i]
            pair = lambda k: f"{pct(r[k + '_on'])} / {pct(r[k + '_off'])}"  # noqa: E731
            md.append(f"| {r['sigma']:.3g} | {pair('rad1_ge0.95')} | {pair('rad1_gt1')} | {pair('rho_ge0.95')} | "
                      f"{pair('rho_ge1')} | {pair('rhohi_radlo')} | {pair('radlo_given_rhohi')} "
                      f"(n={r['n_rhohi_on']}/{r['n_rhohi_off']}) | {pair('radhi_rholo')} | {pair('stall0.95')} |")
        if finite(z, "radA"):
            md += ["", "Predictive anchor (no endpoint information):", "",
                   "| sigma | radA on | radA off | rhoA on | rhoA off | radA>=0.95 on / off | rhoA>.95 & radA<.9 on / off | "
                   "AUC radA | AUC rhoA | AUC dD | anchor = y1 on / off |", "|---|---|---|---|---|---|---|---|---|---|---|"]
            for i in SHOW:
                r = rows[i]
                md.append(f"| {r['sigma']:.3g} | " + " | ".join([
                    med_iqr([r["radA_on_q25"], r["radA_on_med"], r["radA_on_q75"]]),
                    med_iqr([r["radA_off_q25"], r["radA_off_med"], r["radA_off_q75"]]),
                    med_iqr([r["rhoA_on_q25"], r["rhoA_on_med"], r["rhoA_on_q75"]]),
                    med_iqr([r["rhoA_off_q25"], r["rhoA_off_med"], r["rhoA_off_q75"]]),
                    f"{pct(r['radA_ge0.95_on'])} / {pct(r['radA_ge0.95_off'])}",
                    f"{pct(r['rhoAhi_radAlo_on'])} / {pct(r['rhoAhi_radAlo_off'])}",
                    f3(r.get("auc_radA")), f3(r.get("auc_rhoA")), f3(r.get("auc_dD")),
                    f"{pct(r['anchor_agree_on'])} / {pct(r['anchor_agree_off'])}"]) + " |")
        L = entry["late"]; w_ = L["window"]
        md += ["", f"Late window: sigma {w_['sigma_from']:.4g} -> {w_['sigma_to']:.4g}, {w_['n_intervals']} intervals, "
               f"sum of dlog sigma = {w_['sum_dlog']:.3f}.", "",
               "| quantity | on | off | all |", "|---|---|---|---|"]
        for k in ("S_early", "C_early", "S", "S_trap", "S_signed_left", "S_signed_trap", "C", "C_left", "actual",
                  "actual_total", "tail_frac") + (("S_A", "S_A_early", "C_A_early") if "S_A_q" in L else ()):
            qq = L[f"{k}_q"]
            md.append(f"| {k} | {med_iqr(qq['on']) if 'on' in qq else '-'} | {med_iqr(qq['off']) if 'off' in qq else '-'} | "
                      f"{med_iqr(qq['all'])} |")
        qd = L["actual_minus_Ssigned_q"]
        md.append(f"| actual - S_signed_trap | {med_iqr(qd['on']) if 'on' in qd else '-'} | "
                  f"{med_iqr(qd['off']) if 'off' in qd else '-'} | {med_iqr(qd['all'])} |")
        md += ["", f"corr(actual, S_signed_trap) = {L['corr_actual_Ssigned']:.3f}; fraction with actual > S_trap: "
               + ", ".join(f"{g} {pct(v)}" for g, v in L["frac_actual_gt_Strap"].items()), "",
               "Per interval (medians): actual Heun log-contraction log(n_j/n_{j+1}), trapezoid of (1 - rad1), difference:", "",
               "| interval | dlog | actual on / off | trap on / off | diff on / off |", "|---|---|---|---|---|"]
        for p in L["per_interval"]:
            two = lambda k: f"{f3(p.get(k + '_on'))} / {f3(p.get(k + '_off'))}"  # noqa: E731
            md.append(f"| {p['from']:.3g} -> {p['to']:.3g} | {p['dlog']:.3f} | {two('actual')} | {two('trap')} | {two('diff')} |")
        jt = entry["joint_totals"]
        md += ["", "Cells summed over all levels: " + "; ".join(
            f"{g}: rho>0.95 in {v['rho_gt0.95']} of {v['cells']}, of which rad1<0.9 in {v['rho_gt0.95_and_rad1_lt0.9']} "
            f"(min rad1 there {f3(v['min_rad1_given_rho_gt0.95'])}); rad1>0.95 and rho<0.9 in {v['rad1_gt0.95_and_rho_lt0.9']}"
            for g, v in jt.items()), ""]
        cx = entry["context"]
        md += ["Context (medians [IQR]): " + "; ".join(
            f"{g}: d1 {med_iqr(v['d1'], 2)}, d1/d2 {med_iqr(v['d1_over_d2'])}, n1 at {w_['sigma_from']:.3g} "
            f"{med_iqr(v['n1_window_start'], 2)}, n1 at {w_['sigma_to']:.3g} {med_iqr(v['n1_last_level'], 2)}, "
            f"n1_end {med_iqr(v['n1_end'], 2)}" + (f", late omega/n1 p99 {v['omega_over_n1_late_p99']:.2e}, max "
                                                   f"{v['omega_over_n1_late_max']:.2e}, cells > 0.01 "
                                                   f"{pct(v['frac_late_cells_omega_over_n1_gt0.01'], 2)}"
                                                   if "omega_over_n1_late_p99" in v else "")
            for g, v in cx.items()), ""]
        if "auc" in L:
            md += ["| AUC (95% CI) | value |", "|---|---|"] + [f"| {k} | {ci(v)} |" for k, v in L["auc"].items()]
        st = entry["stall"]
        md += ["", "Stall level (largest sigma from which rad1 >= thr at every later level): median sigma, never-stalled fraction:", ""]
        for t in THR:
            md.append("- thr " + str(t) + ": " + "; ".join(
                f"{g}: median sigma {f3(st[f'thr{t}_{g}']['median_sigma'], 4)}, never {pct(st[f'thr{t}_{g}']['frac_never'])}, "
                f"by 0.140 {pct(st[f'thr{t}_{g}']['frac_by_sigma0.140'])}, by 0.060 {pct(st[f'thr{t}_{g}']['frac_by_sigma0.060'])}"
                for g in ("on", "off", "all") if f"thr{t}_{g}" in st))
        bh = entry["b_hypothesis"]
        md += ["", "(b) on the finite window, gamma = 0: fraction with max rho over [sigma_end, 0.585] below rho_bar (on / off):", "",
               "| sigma_end | " + " | ".join(f"rho_bar {rb}" for rb in B_RHOBAR) + " |", "|---|" + "---|" * len(B_RHOBAR)]
        for je in B_END:
            s = z["sigma"][je]
            md.append(f"| {s:.3g} | " + " | ".join(
                f"{pct(bh[f'sigma{s:.3g}_rhobar{rb}_on']) if has_on else '-'} / {pct(bh[f'sigma{s:.3g}_rhobar{rb}_off'])}"
                for rb in B_RHOBAR) + " |")
        md.append("")

    numbers["inequality_rad_le_rho_plus_omega"] = [inequality_check(f) for f in OMEGA_FILES]
    md += ["## Inequality rad1 <= rho + omega/n1 (pointwise), C_omega <= S_signed (integrated), last Euler step", "",
           "| file | samples | cells | viol > 0 | viol > 1e-9 | max viol | max omega/n1 late on / off | C_omega > S_signed | "
           "last step: rad1 > ratio / ratio > rho+omega/n1 | max ratio-(rho+omega/n1) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in numbers["inequality_rad_le_rho_plus_omega"]:
        md.append(f"| {c['source']} | {c['n_samples']} | {c['n_cells']} | {c['n_viol_gt0']} | {c['n_viol_gt1e-9']} | "
                  f"{c['max_viol']:.3e} | "
                  f"{format(c['max_omega_over_n1_late_on'], '.1e') if c['max_omega_over_n1_late_on'] is not None else '-'}"
                  f" / {c['max_omega_over_n1_late_off']:.1e} | {c['n_Comega_gt_Ssigned']} | "
                  f"{c['last_step_lower_viol']} / {c['last_step_upper_viol']} | {c['last_step_max_ratio_minus_upper']:.3e} |")
    numbers["identity_rad_eq_q_plus_r"] = [identity_check(f) for f in IDENTITY_FILES]
    md += ["", "## Identity rad1 = q1 + r1 (q1: 4-point midpoint quadrature of the Jacobian Rayleigh quotient on [y1, x])", ""]
    for c in numbers["identity_rad_eq_q_plus_r"]:
        md += [f"{c['source']}: max |dev| = {c['max_abs_dev']:.3f} (at sigma {c['sigma_at_max']:.3g}); "
               f"max |dev| for sigma >= 1.9: {c['max_abs_dev_sigma_ge_1.9']:.4f}; for sigma <= 0.0075: "
               f"{c['max_abs_dev_sigma_le_0.0075']:.4f}; cells with |dev| > 0.05: {pct(c['frac_cells_abs_gt_0.05'])}; "
               f"corr(|dev|, n1/sigma) late = {c['corr_absdev_n1_over_sigma_late']:.3f}", "",
               "| sigma | max abs | median abs | p99 abs | median abs on | median abs off | median rad1 | median q1+r1 | "
               "median dev | median qx1 (at x) | frac abs > 0.05 |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for p in c["per_sigma"]:
            md.append(f"| {p['sigma']:.3g} | {p['max_abs']:.4f} | {p['median_abs']:.4f} | {p['p99_abs']:.4f} | "
                      f"{f3(p['median_abs_on'], 4) if p['median_abs_on'] is not None else '-'} | "
                      f"{f3(p['median_abs_off'], 4) if p['median_abs_off'] is not None else '-'} | {p['median_rad1']:.4f} | "
                      f"{p['median_q1_plus_r1']:.4f} | {p['median_dev']:.4f} | {p['median_qx1']:.4f} | {pct(p['frac_abs_gt_0.05'])} |")
        md.append("")
    numbers["step_robustness"] = step_robustness()
    md += ["## Step count (first 500-image model, same latents): late radial contraction S", "",
           "| steps | window | intervals | off | S on / off | S_trap on / off | C on / off | AUC -S | AUC -S_trap | AUC -C | "
           "rad1>=0.95 at 0.002 on / off |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in numbers["step_robustness"]:
        w_ = c["window"]
        md.append(f"| {c['steps']} | {w_['sigma_from']:.4g} -> {w_['sigma_to']:.4g} | {w_['n_intervals']} | {c['n_off']} | "
                  f"{c['S_med_on']:.2f} / {c['S_med_off']:.2f} | {c['S_trap_med_on']:.2f} / {c['S_trap_med_off']:.2f} | "
                  f"{c['C_med_on']:.2f} / {c['C_med_off']:.2f} | {ci(c['auc']['S'])} | {ci(c['auc']['S_trap'])} | "
                  f"{ci(c['auc']['C'])} | {pct(c['rad1_ge0.95_last_on'])} / {pct(c['rad1_ge0.95_last_off'])} |")
    (OUT / "radial_numbers.json").write_text(json.dumps(numbers, indent=1), encoding="utf-8")
    (OUT / "radial_tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
