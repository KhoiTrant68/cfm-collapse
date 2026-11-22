"""Paper B: the late-contraction certificate, tested on the saved EDM trajectories (numpy only).

Theory. For the probability-flow ODE dx/dsigma = (x - D(x, sigma))/sigma and a FIXED training image a, the distance
n = |x - a| obeys exactly
    d log n / d log sigma = 1 - rad,          rad = <(x - a)/n, D - a>/n          (radial ratio),
so over a window [sigma_1, sigma_0] (sigma_1 < sigma_0)
    log(n(sigma_0)/n(sigma_1)) = C_rad := int_{sigma_1}^{sigma_0} (1 - rad) dlog(1/sigma)              (IDENTITY)
and, by Cauchy-Schwarz and |m* - a| <= omega = (1 - w_a) max_k |x^k - a|,
    rad <= |D - a|/n <= rho + omega/n,       rho = |D - m*|/n,
    log(n(sigma_0)/n(sigma_1)) >= C_rho - Omega,   C_rho = int (1 - rho), Omega = int omega/n   (CERTIFICATE).
The saved per-sample arrays are values at the grid points of the Heun sampler, so all integrals are trapezoidal in
log sigma on the sampler's grid, exactly as the paper's late contraction (scripts/make_edm_figures.py, fig_clocks):
the IDENTITY then holds only up to the Heun discretisation gap, which is what section 1 measures.

Sections (all written to results/paperB_20261121/certificate/):
 1. identity: actual log contraction of n1 = |x - y1| vs trapezoidal C_rad (per grid interval, late window
    [0.002, 0.585], full window [0.002, 80]); the last Euler step (sigma 0.002 -> 0, x_K = D) is outside the ODE and
    is checked against its exact bounds -log(rho + omega/n) <= log(n_17/n_K) <= -log|rad|. 18/36/64-step runs show
    how the gap shrinks with the step count.
 2. certificate inequality: violations of log(n_0/n_1) >= C_rho - Omega (only through the discretisation gap,
    since rad <= rho + omega/n holds pointwise), per sample and per interval.
 3. predictive-anchor certificate (sub2000, sub500s1): anchor a = nearest training image of D(x_k) chosen at
    sigma_0 = 0.585 without endpoint information; certified bound on |x(0.002) - a| and, through the exact last-step
    bound n_K <= rho_K n + omega_K, on the output distance; certification of on-atom outputs (bound < d2/3, or
    < g_a/4 with g_a the training-set gap of a), false certifications, comparison with the baseline dD(sigma_0).
 4. R^2 of log d1 (final) on the late contraction vs on log dD(sigma_0) (simple regressions, bootstrap CIs).

Endpoint information. Keys anchored at y1 (the endpoint's nearest image) use the endpoint: n1, rho = err/n1, rad1,
omega (computed for y1), errt/nt1/omegat, d1, d2, n1_end. Keys anc, nA, rhoA, radA, dD at step k use only the
trajectory up to sigma_k. Two caveats are reported with the numbers: (i) a window that ends at sigma = 0.002 uses the
last denoiser output D(x_17), which IS the endpoint (x_K = D(x_17)); in particular dD at 0.002 equals d1 exactly;
(ii) omega is saved only for y1, so it is the anchor's omega only at steps where the anchor equals y1 (checked).

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_certificate
"""
from __future__ import annotations

import json
import math
import pathlib
import time

import numpy as np

OUT = pathlib.Path("results/paperB_20261121/certificate")
RATIO = 1.0 / 3.0           # off-atom: d1/d2 >= 1/3
SIG0 = 0.585                # start of the late window (grid point 11 of the 18-step schedule)
B_BOOT = 2000
SEED = 0

RUNS = {  # name -> (q_per_sample.npz, model key, description)
    "sub500_rho": ("results/n3_rho_20261117/sub500/q_per_sample.npz", "sub500",
                   "first 500-image model, 18 steps, run behind Table tab:edm-rho (no omega, no anchor keys)"),
    "public_rho": ("results/n3_rho_20261117/public/q_per_sample.npz", "public",
                   "public 50k model, 18 steps, 200 samples (no omega, no anchor keys)"),
    "sub2000": ("results/n3_rho2_20261118/sub2000/q_per_sample.npz", "sub2000",
                "2000-image model, 18 steps (omega and predictive-anchor keys)"),
    "sub500s1": ("results/n3_rho2_20261118/sub500s1/q_per_sample.npz", "sub500s1",
                 "second 500-image model, 18 steps (omega and predictive-anchor keys)"),
    "sub500_s18": ("results/n3_steps_20261117/s18/sub500/q_per_sample.npz", "sub500",
                   "first 500-image model, 18 steps, forward-only rerun with omega (same latents)"),
    "sub500_s36": ("results/n3_steps_20261117/s36/sub500/q_per_sample.npz", "sub500",
                   "first 500-image model, 36 steps, same latents"),
    "sub500_s64": ("results/n3_steps_20261117/s64/sub500/q_per_sample.npz", "sub500",
                   "first 500-image model, 64 steps, same latents"),
    "public_s18": ("results/n3_steps_20261117/s18/public/q_per_sample.npz", "public",
                   "public model, 18 steps, 500 samples, with omega"),
    "public_s36": ("results/n3_steps_20261117/s36/public/q_per_sample.npz", "public", "public model, 36 steps"),
    "public_s64": ("results/n3_steps_20261117/s64/public/q_per_sample.npz", "public", "public model, 64 steps"),
}
# n3_edm_memorization runs of the same models: exact-field endpoints from the same latents give the training-set gap
# g_i = min_{k != i} |x^i - x^k| of every image the exact field reached (exact_d1 ~ 1e-6, so g_i = exact_d2 +- exact_d1).
MEMO = {"sub500": "results/n3_edm_sub500_20261115/sub500_s0/per_sample.npz",
        "sub2000": "results/n3_edm_sub2000_20261117/sub2000_s0/per_sample.npz",
        "sub500s1": "results/n3_edm_sub500s1_20261117/sub500_s1/per_sample.npz"}
WINDOWS18 = ((0, 7), (7, 10), (10, 13), (13, 17), (11, 17), (0, 17))


# ----------------------------------------------------------------------------------------------------- helpers
def auc(pos, neg):
    """P(pos > neg) + P(pos = neg)/2; a copy of scripts.n3_edm_memorization.auc (that module imports torch)."""
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    x = np.concatenate([pos, neg]); r = np.empty(len(x)); o = x.argsort(kind="mergesort")
    r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_fast(pos, neg):
    """Same value as auc() (average ranks for ties), O(n log n); used inside the bootstrap."""
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    x = np.concatenate([pos, neg])
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    r = (np.cumsum(cnt) - (cnt - 1) / 2.0)[inv]
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot_auc_pair(sa, sb, off, rng, B=B_BOOT):
    """AUC(off > on) of two scores, their paired difference, stratified bootstrap 95% intervals."""
    io, ii = np.where(off)[0], np.where(~off)[0]
    est = (auc_fast(sa[off], sa[~off]), auc_fast(sb[off], sb[~off]))
    dr = []
    for _ in range(B):
        so, si = rng.choice(io, len(io)), rng.choice(ii, len(ii))
        a_, b_ = auc_fast(sa[so], sa[si]), auc_fast(sb[so], sb[si])
        dr.append((a_, b_, a_ - b_))
    dr = np.array(dr)
    return {"a": [est[0], *np.nanpercentile(dr[:, 0], [2.5, 97.5]).tolist()],
            "b": [est[1], *np.nanpercentile(dr[:, 1], [2.5, 97.5]).tolist()],
            "a_minus_b": [est[0] - est[1], *np.nanpercentile(dr[:, 2], [2.5, 97.5]).tolist()]}


def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return float("nan")
    return float(np.polyfit(x[m], y[m], 1)[0])


def incr(v, ls):
    """Trapezoidal increments of int v dlog(1/sigma) on each grid interval [sigma_{k+1}, sigma_k]: shape (n, K-1)."""
    return 0.5 * (v[:, :-1] + v[:, 1:]) * (ls[:-1] - ls[1:])[None, :]


def qs(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) == 0:
        return None
    p = np.percentile(v, [1, 5, 25, 50, 75, 95, 99])
    return {"n": int(len(v)), "min": float(v.min()), "p1": float(p[0]), "p5": float(p[1]), "p25": float(p[2]),
            "median": float(p[3]), "p75": float(p[4]), "p95": float(p[5]), "p99": float(p[6]), "max": float(v.max()),
            "mean": float(v.mean()), "median_abs": float(np.median(np.abs(v))), "max_abs": float(np.abs(v).max())}


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def r2(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3 or np.std(x[m]) == 0:
        return float("nan")
    c = np.corrcoef(x[m], y[m])[0, 1]
    return float(c * c)


def r2_multi(X, y):
    m = np.isfinite(y) & np.all(np.isfinite(X), 1)
    A = np.column_stack([np.ones(m.sum()), X[m]]); yy = y[m]
    coef, *_ = np.linalg.lstsq(A, yy, rcond=None)
    res = yy - A @ coef
    return float(1 - (res @ res) / ((yy - yy.mean()) @ (yy - yy.mean())))


def f3(v):
    return "-" if v is None or (isinstance(v, float) and v != v) else f"{v:.3f}"


def fe(v):
    return "-" if v is None or (isinstance(v, float) and v != v) else f"{v:.2e}"


def load(name):
    path, model, desc = RUNS[name]
    z = np.load(path); d = {k: z[k] for k in z.files}
    d.update(name=name, path=path, model=model, desc=desc)
    d["off"] = d["d1"] / d["d2"] >= RATIO
    d["on"] = ~d["off"]
    d["ls"] = np.log(d["sigma"])
    d["K"] = len(d["sigma"])
    d["i0"] = int(np.argmin(np.abs(d["sigma"] - SIG0)))
    d["has_omega"] = "omega" in d and bool(np.isfinite(d["omega"]).all())
    d["has_anchor"] = "anc" in d and bool(np.isfinite(d["anc"]).all())
    d["has_pred"] = "errt" in d and bool(np.isfinite(d["errt"][:, :-1]).all())
    return d


def gap_map(model):
    """(class, within-class image index) -> lower bound exact_d2 - exact_d1 on the training-set gap of that image."""
    if model not in MEMO:
        return {}
    m = np.load(MEMO[model]); g = {}
    for c, i, e1, e2 in zip(m["label"], m["exact_nn"], m["exact_d1"], m["exact_d2"]):
        if i >= 0 and np.isfinite(e2) and np.isfinite(e1):
            key = (int(c), int(i)); g[key] = min(g.get(key, np.inf), float(e2 - e1))
    return g


def groups(d):
    return {"on": d["on"], "off": d["off"], "all": np.ones_like(d["on"])}


# ------------------------------------------------------------------------------------- 1 + 2: identity, inequality
def identity_and_inequality(d):
    n1, rad, err, ls, K, i0 = d["n1"], d["rad1"], d["err"], d["ls"], d["K"], d["i0"]
    iL = K - 1
    act = np.log(n1[:, :-1]) - np.log(n1[:, 1:])                     # log(n_k / n_{k+1}) > 0 when contracting
    crad = incr(1 - rad, ls)
    gap = act - crad                                                  # Heun discretisation gap (+ quadrature)
    rho = err / n1
    om = d["omega"] / n1 if d["has_omega"] else np.zeros_like(n1)
    cert = incr(1 - rho, ls) - incr(om, ls)
    slack = act - cert                                                # >= 0 where the certificate holds
    tri = crad - cert                                                 # = incr(rho + om - rad) >= 0 exactly
    point = rho + om - rad                                            # pointwise rad <= rho + omega/n
    G = groups(d)
    res = {"run": d["name"], "source": d["path"], "desc": d["desc"], "n": int(len(n1)), "n_off": int(d["off"].sum()),
           "steps": int(K), "has_omega": d["has_omega"], "sigma0_used": float(d["sigma"][i0]), "i0": i0,
           "pointwise_min_slack": float(np.nanmin(point)), "pointwise_frac_negative": float((point < 0).mean()),
           "pointwise_min_slack_late": float(np.nanmin(point[:, i0:]))}
    wins = {"late": (i0, iL), "full": (0, iL)}
    if K == 18:
        for a, b in WINDOWS18:
            wins.setdefault(f"{d['sigma'][a]:.3g}->{d['sigma'][b]:.3g}", (a, b))
    res["windows"] = {}
    for wn, (a, b) in wins.items():
        A = act[:, a:b].sum(1); Cr = crad[:, a:b].sum(1); Gp = gap[:, a:b].sum(1)
        Ce = cert[:, a:b].sum(1); Sl = slack[:, a:b].sum(1); Tr = tri[:, a:b].sum(1)
        Crho = incr(1 - rho, ls)[:, a:b].sum(1); Om = incr(om, ls)[:, a:b].sum(1)
        w = {"sigma_from": float(d["sigma"][a]), "sigma_to": float(d["sigma"][b])}
        for g, sel in G.items():
            if not sel.any():
                continue
            viol = Sl[sel] < 0
            w[g] = {"actual": qs(A[sel]), "C_rad": qs(Cr[sel]), "gap": qs(Gp[sel]), "rel_gap": qs(Gp[sel] / A[sel]),
                    "C_rho": qs(Crho[sel]),
                    "Omega": qs(Om[sel]), "cert": qs(Ce[sel]), "slack": qs(Sl[sel]), "triangle_slack": qs(Tr[sel]),
                    "frac_violating": float(viol.mean()), "n_violating": int(viol.sum()),
                    "violation_depth": qs(-Sl[sel][viol]) if viol.any() else None,
                    "max_violation_factor": float(np.exp(max(0.0, -Sl[sel].min())))}
        res["windows"][wn] = w
    # per interval
    per = []
    for k in range(K - 1):
        row = {"k": k, "sigma_k": float(d["sigma"][k]), "sigma_k1": float(d["sigma"][k + 1])}
        for g, sel in G.items():
            if not sel.any():
                continue
            row[g] = {"gap_median": float(np.median(gap[sel, k])), "gap_max_abs": float(np.abs(gap[sel, k]).max()),
                      "gap_p1": float(np.percentile(gap[sel, k], 1)), "gap_p99": float(np.percentile(gap[sel, k], 99)),
                      "act_median": float(np.median(act[sel, k])), "crad_median": float(np.median(crad[sel, k])),
                      "frac_violating": float((slack[sel, k] < 0).mean()),
                      "min_slack": float(slack[sel, k].min())}
        per.append(row)
    res["per_interval"] = per
    res["frac_interval_violations_late"] = {g: float((slack[sel][:, i0:iL] < 0).mean()) for g, sel in G.items() if sel.any()}
    res["frac_interval_violations_all"] = {g: float((slack[sel] < 0).mean()) for g, sel in G.items() if sel.any()}
    # cumulative: certificate from sigma_0 down to every later grid point
    cum = np.cumsum(slack[:, i0:iL], 1)                               # windows [sigma_j, sigma_0], j = i0+1..iL
    res["frac_any_cumulative_violation_late"] = {g: float((cum[sel] < 0).any(1).mean()) for g, sel in G.items() if sel.any()}
    wl_slack = slack[:, i0:iL].sum(1)
    bad = np.where(wl_slack < 0)[0]
    res["late_window_violators"] = [{"index": int(s), "group": "off" if d["off"][s] else "on", "deficit": float(-wl_slack[s]),
                                     "factor": float(np.exp(-wl_slack[s]))} for s in bad]
    # overshoot: the denoiser output lies beyond y1 (rad < 0) somewhere in the late window; the big gaps come from here
    neg = (rad[:, i0:] < 0).any(1)
    wgap = gap[:, i0:iL].sum(1)
    res["overshoot_rad_negative_late"] = {g: {"n": int((neg & sel).sum()), "of": int(sel.sum()),
                                              "gap_median_overshoot": float(np.median(wgap[neg & sel])) if (neg & sel).any() else None,
                                              "gap_median_rest": float(np.median(wgap[~neg & sel])) if (~neg & sel).any() else None,
                                              "gap_min_rest": float(np.min(wgap[~neg & sel])) if (~neg & sel).any() else None}
                                          for g, sel in G.items() if sel.any()}
    # last Euler step sigma_{K-1} -> 0: x_K = D(x_{K-1}); exact bounds
    L = np.log(n1[:, -1] / d["n1_end"])
    hi = -np.log(np.abs(rad[:, -1])); lo = -np.log(rho[:, -1] + om[:, -1])
    to_end = np.log(n1[:, i0] / d["n1_end"])
    pred_end = crad[:, i0:iL].sum(1) + hi
    res["last_step"] = {g: {"log_n17_over_nK": qs(L[sel]), "upper_minus_actual": qs((hi - L)[sel]),
                            "actual_minus_lower": qs((L - lo)[sel]),
                            "frac_within_bounds": float(((L <= hi + 1e-9) & (L >= lo - 1e-9))[sel].mean()),
                            "to_end_actual": qs(to_end[sel]), "to_end_gap": qs((to_end - pred_end)[sel])}
                        for g, sel in G.items() if sel.any()}
    res["_arrays"] = {"act": act, "crad": crad, "gap": gap, "cert": cert, "slack": slack, "rho": rho, "om": om}
    return res


# --------------------------------------------------------------------------------- 3: predictive-anchor certificate
def heun_chain(d, j, B0):
    """Prop. heun(b), gamma = 0: n_{k+1} <= c_k n_k + b_k for k = j..K-2 (anchor = y1 on these steps)."""
    sg = d["sigma"]; r = sg[1:] / sg[:-1]
    kap = (1 - r) * (2 * r - 1) / (2 * r); th = (1 - r) / (2 * r)
    rk = np.maximum(d["err"][:, :-1] / d["n1"][:, :-1], d["errt"][:, :-1] / d["nt1"][:, :-1])
    ck = r + np.abs(kap) * rk + th * rk * (r + (1 - r) * rk)
    bk = (np.abs(kap) + th * rk * (1 - r)) * d["omega"][:, :-1] + th * d["omegat"][:, :-1]
    B = B0.astype(float).copy()
    for k in range(d["K"] - 1):
        B = np.where(k >= j, ck[:, k] * B + bk[:, k], B)
    return B


def certify(d, B17, gm, anchor_end):
    """Output bound B_K = rho_K B17 + omega_K (exact last Euler step), validity and certification counts."""
    on, off = d["on"], d["off"]
    rhoK = d["err"][:, -1] / d["n1"][:, -1]                          # anchor == y1 at the last step (checked)
    omK = d["omega"][:, -1] if d["has_omega"] else np.zeros(len(on))
    BK = rhoK * B17 + omK
    nK = d["n1_end"]
    v17 = d["n1"][:, -1] > B17 * (1 + 1e-9)
    vK = nK > BK * (1 + 1e-9)
    t1 = BK < d["d2"] / 3
    g = np.array([gm.get((int(c), int(a)), np.nan) for c, a in zip(d["label"], anchor_end)])
    known = np.isfinite(g)
    t2 = known & (BK < g / 4)
    margin = BK / (d["d2"] / 3)                                       # < 1: certified under T1
    out = {"viol_sigma_min": int(v17.sum()), "viol_output": int(vK.sum()),
           "viol_output_on": int(vK[on].sum()), "viol_output_off": int(vK[off].sum()),
           "violators": [{"index": int(s), "group": "off" if off[s] else "on", "factor": float(nK[s] / BK[s]),
                          "certified_T1": bool(t1[s])} for s in np.where(vK)[0]],
           "max_violation_factor_output": float(np.max(nK / BK)) if len(nK) else float("nan"),
           "T1_margin_BK_over_d2_3": {"on": qs(margin[on]), "off_min": float(margin[off].min()) if off.any() else None},
           "looseness_log_BK_over_nK": {"on": qs(np.log(BK / nK)[on]), "off": qs(np.log(BK / nK)[off])},
           "B17_over_n17": {"on": qs((B17 / d["n1"][:, -1])[on]), "off": qs((B17 / d["n1"][:, -1])[off])},
           "T1_d2_over_3": {"on_certified": int(t1[on].sum()), "n_on": int(on.sum()),
                            "frac_on": float(t1[on].mean()) if on.any() else float("nan"),
                            "frac_on_CI": wilson(int(t1[on].sum()), int(on.sum())),
                            "off_certified": int(t1[off].sum()), "n_off": int(off.sum()),
                            "false_rate_upper95": wilson(int(t1[off].sum()), int(off.sum()))[1]},
           "T1_literal_B17_below_d2_over_3": {"on_certified": int((B17 < d["d2"] / 3)[on].sum()),
                                              "off_certified": int((B17 < d["d2"] / 3)[off].sum()),
                                              "n_off_with_rhoK_above_1": int((rhoK > 1)[off].sum()),
                                              "n_on_with_rhoK_above_1": int((rhoK > 1)[on].sum())},
           "T2_gap_over_4": {"n_on_known": int((on & known).sum()), "n_off_known": int((off & known).sum()),
                             "on_certified": int(t2[on].sum()), "off_certified": int(t2[off].sum()),
                             "frac_on_known": float(t2[on & known].mean()) if (on & known).any() else float("nan"),
                             "frac_on_all": float(t2[on].mean()) if on.any() else float("nan")}}
    return out, BK, t1, t2, known


def anchor_certificate(d, gm, i_start, rng=None):
    """Certificates from the anchor chosen at sigma_{i_start} (nearest training image of D(x)), no endpoint info."""
    anc = d["anc"].astype(int); nn1 = d["nn1"]; K = d["K"]; ls = d["ls"]; N = len(nn1); on, off = d["on"], d["off"]
    sub = anc[:, i_start:]
    same = sub == sub[:, -1:]
    tail = np.flip(np.cumprod(np.flip(same, 1), 1), 1).astype(bool)
    j = i_start + tail.argmax(1)                                      # restart index: last anchor switch
    ok = np.array([np.all(anc[s, j[s]:] == nn1[s]) for s in range(N)])  # omega/err/n1 are the anchor's from j on
    cols = np.arange(K - 1)
    mR = cols[None, :] >= j[:, None]
    mS = np.broadcast_to(cols[None, :] >= i_start, mR.shape)
    nA, rhoA, dD, radA = d["nA"], d["rhoA"], d["dD"], d["radA"]
    omA = d["omega"] / nA                                             # omega is y1's; = anchor's where anc == y1
    I = lambda v, m: (incr(v, ls) * m).sum(1)  # noqa: E731
    nj = nA[np.arange(N), j]
    C = {"S": I(1 - rhoA, mS) - I(omA, mS), "R": I(1 - rhoA, mR) - I(omA, mR), "D": I(1 - dD / nA, mR),
         "rad": I(1 - radA, mR)}
    B17 = {"S": nA[:, i_start] * np.exp(-C["S"]), "R": nj * np.exp(-C["R"]), "D": nj * np.exp(-C["D"])}
    if d["has_pred"]:
        B17["H"] = heun_chain(d, j, nj)
    res = {"sigma_start": float(d["sigma"][i_start]), "i_start": int(i_start),
           "anchor_switch_in_window": {"on": int((j > i_start)[on].sum()), "off": int((j > i_start)[off].sum())},
           "anchor_start_is_y1": {"on": int((anc[:, i_start] == nn1)[on].sum()), "off": int((anc[:, i_start] == nn1)[off].sum()),
                                  "n_on": int(on.sum()), "n_off": int(off.sum())},
           "anchor_end_is_y1_all": bool(np.all(anc[:, -1] == nn1)), "omega_is_anchors_from_restart": bool(ok.all()),
           "C_R_median": {"on": float(np.median(C["R"][on])) if on.any() else float("nan"), "off": float(np.median(C["R"][off]))},
           "max_abs_C_R_minus_C_D": float(np.max(np.abs(C["R"] - C["D"]))),
           "n_C_R_ne_C_D_1e-6": int((np.abs(C["R"] - C["D"]) > 1e-6).sum()),
           "variants": {}}
    extra = {}
    for v, b in B17.items():
        out, BK, t1, t2, known = certify(d, b, gm, anc[:, -1])
        res["variants"][v] = out
        extra[v] = (BK, t1, t2, known)
    # comparison with the baseline dD(sigma_start)
    dd0 = dD[:, i_start]
    BKR = extra["R"][0]
    res["baseline"] = {"auc_dD_start": auc(dd0[off], dd0[on]), "auc_logBK_R": auc(np.log(BKR)[off], np.log(BKR)[on]),
                       "auc_minus_C_R": auc(-C["R"][off], -C["R"][on]),
                       "auc_minus_C_S": auc(-C["S"][off], -C["S"][on])}
    if off.any() and on.any():
        res["baseline"]["oracle_zeroFP_recall_dD_start"] = float((dd0[on] < dd0[off].min()).mean())
        res["baseline"]["oracle_zeroFP_recall_logBK_R"] = float((BKR[on] < BKR[off].min()).mean())
        res["baseline"]["oracle_zeroFP_recall_C_R"] = float((C["R"][on] > C["R"][off].max()).mean())
        naive = dd0 < d["d2"] / 3
        res["baseline"]["naive_dD_start_below_d2_over_3"] = {"on": int(naive[on].sum()), "off": int(naive[off].sum())}
        g = np.array([gm.get((int(c), int(a)), np.nan) for c, a in zip(d["label"], anc[:, i_start])])
        kn = np.isfinite(g); nv = kn & (dd0 < g / 4)
        res["baseline"]["naive_dD_start_below_g_over_4"] = {"on": int(nv[on].sum()), "off": int(nv[off].sum()),
                                                            "n_on_known": int((kn & on).sum()), "n_off_known": int((kn & off).sum())}
        # agreement of certificate and baseline
        t1 = extra["R"][1]
        res["baseline"]["certified_R_T1_and_dD_below_oracle"] = int((t1 & (dd0 < dd0[off].min()) & on).sum())
        if rng is not None:   # paired: AUC of dD(sigma_start) minus AUC of the late contraction (-C) / of log B_K
            res["baseline"]["boot_dD_vs_minusC_R"] = boot_auc_pair(dd0, -C["R"], off, rng)
            res["baseline"]["boot_dD_vs_logBK_R"] = boot_auc_pair(dd0, np.log(BKR), off, rng)
            res["baseline"]["auc_d1_itself"] = auc(d["d1"][off], d["d1"][on])   # = AUC of dD at sigma = 0.002
    # off-atom threshold sensitivity: certified at threshold tau when B_K < tau d2 (then d1/d2 <= B_K/d2 < tau)
    sens = {}
    for tau in (0.2, 1 / 3, 0.5):
        lab_off = d["d1"] / d["d2"] >= tau
        c_ = BKR < tau * d["d2"]
        sens[f"{tau:.3g}"] = {"n_off": int(lab_off.sum()), "on_certified": int((c_ & ~lab_off).sum()),
                              "n_on": int((~lab_off).sum()), "false": int((c_ & lab_off).sum())}
    res["threshold_sensitivity_R"] = sens
    return res, C, B17, extra


def endpoint_certificate(d, gm):
    """Certificate anchored at the endpoint's nearest image y1 (uses endpoint information for the anchor)."""
    i0, K, ls = d["i0"], d["K"], d["ls"]
    m = np.broadcast_to(np.arange(K - 1)[None, :] >= i0, (len(d["d1"]), K - 1))
    rho = d["err"] / d["n1"]
    om = d["omega"] / d["n1"] if d["has_omega"] else np.zeros_like(rho)
    C = (incr(1 - rho, ls) * m).sum(1) - (incr(om, ls) * m).sum(1)
    B17 = {"E": d["n1"][:, i0] * np.exp(-C)}
    if d["has_pred"] and d["has_omega"]:
        B17["H"] = heun_chain(d, np.full(len(d["d1"]), i0), d["n1"][:, i0])
    out = {}
    for v, b in B17.items():
        out[v] = certify(d, b, gm, d["nn1"] if "nn1" in d else np.full(len(b), -1))[0]
    return out


# ------------------------------------------------------------------------------------------------------- 4: R^2
def r2_analysis(d, dD, rng, logB=None, logB_D=None):
    """R^2 of log d1 on the late contraction vs log dD(sigma_0); dD is the NN distance of D along the same run.
    logB: log of the certified bound at sigma = 0.002 (log n(sigma_0) - C_rho + Omega); logB_D: the same with
    |D - a|/n in place of rho + omega/n (no Omega term)."""
    i0, K, ls, on, off = d["i0"], d["K"], d["ls"], d["on"], d["off"]
    y = np.log(d["d1"])
    rho = d["err"] / d["n1"]
    preds = {}
    inc_rho = incr(1 - rho, ls)
    for j in range(i0 + 1, K):
        preds[f"C_rho_endpoint[{d['sigma'][j]:.3g},{d['sigma'][i0]:.3g}]"] = inc_rho[:, i0:j].sum(1)
    if d["has_anchor"]:
        inc_A = incr(1 - d["rhoA"], ls)
        for j in range(i0 + 1, K):
            preds[f"C_rhoA_pred[{d['sigma'][j]:.3g},{d['sigma'][i0]:.3g}]"] = inc_A[:, i0:j].sum(1)
        preds[f"log_nA[{d['sigma'][i0]:.3g}]"] = np.log(d["nA"][:, i0])
    preds[f"log_n1_endpoint[{d['sigma'][i0]:.3g}]"] = np.log(d["n1"][:, i0])
    if logB is not None:
        preds["log_certified_bound_B(0.002)"] = logB
    if logB_D is not None:
        preds["log_certified_bound_B_D(0.002) (no Omega)"] = logB_D
    preds[f"log_n1[{d['sigma'][i0]:.3g}] - C_rho_endpoint(late) (no Omega)"] = np.log(d["n1"][:, i0]) - inc_rho[:, i0:].sum(1)
    if dD is not None:
        for j in range(max(0, i0 - 4), K):
            preds[f"log_dD[{d['sigma'][j]:.3g}]"] = np.log(dD[:, j])
    late = f"[{d['sigma'][K - 1]:.3g},{d['sigma'][i0]:.3g}]"
    out = {"y": "log d1", "groups": {}}
    G = groups(d)
    for g, sel in G.items():
        if sel.sum() < 5:
            continue
        out["groups"][g] = {"n": int(sel.sum()), "r2": {k: r2(v[sel], y[sel]) for k, v in preds.items()},
                            "slope": {k: slope(v[sel], y[sel]) for k, v in preds.items()}}
        if dD is not None:
            ck = f"C_rhoA_pred{late}" if d["has_anchor"] else f"C_rho_endpoint{late}"
            X = np.column_stack([preds[ck], np.log(dD[:, i0])])
            out["groups"][g]["r2_two_predictors_C_late_and_log_dD_sigma0"] = r2_multi(X[sel], y[sel])
    # bootstrap CIs (stratified by on/off for the pooled group) for the headline predictors
    if dD is not None:
        kc = f"C_rhoA_pred{late}" if d["has_anchor"] else f"C_rho_endpoint{late}"
        kd = f"log_dD[{d['sigma'][i0]:.3g}]"
        out["headline_keys"] = {"C_late": kc, "log_dD_sigma0": kd}
        io, ii = np.where(off)[0], np.where(on)[0]
        boots = {}
        for g in ("all", "on", "off"):
            if g == "all":
                draw = lambda: np.concatenate([rng.choice(io, len(io)), rng.choice(ii, len(ii))])  # noqa: E731
            else:
                base = ii if g == "on" else io
                if len(base) < 5:
                    continue
                draw = lambda base=base: rng.choice(base, len(base))  # noqa: E731
            vals = []
            for _ in range(B_BOOT):
                s = draw()
                a_, b_ = r2(preds[kc][s], y[s]), r2(preds[kd][s], y[s])
                vals.append((a_, b_, a_ - b_))
            vals = np.array(vals)
            boots[g] = {"C_late": np.nanpercentile(vals[:, 0], [2.5, 97.5]).tolist(),
                        "log_dD_sigma0": np.nanpercentile(vals[:, 1], [2.5, 97.5]).tolist(),
                        "difference": np.nanpercentile(vals[:, 2], [2.5, 97.5]).tolist()}
        out["bootstrap95"] = boots
    return out


# ------------------------------------------------------------------------------------------------------- figure
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "blue": "#0072B2",
      "vermillion": "#D55E00", "purple": "#CC79A7"}   # Okabe-Ito, as scripts/figstyle.py (not imported: it tries torch)


def make_figure(D, IDI, AC, stem):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"on": OI["blue"], "off": OI["vermillion"]}
    mk = {"sub2000": "o", "sub500s1": "^"}
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    ax = axes[0]                                   # (a) actual late contraction vs certified C_rho - Omega
    for n in ("sub2000", "sub500s1"):
        d, A = D[n], IDI[n]["_arrays"]; i0 = d["i0"]
        act = A["act"][:, i0:].sum(1); cert = A["cert"][:, i0:].sum(1)
        for g in ("on", "off"):
            s = d[g]
            ax.scatter(cert[s], act[s], s=5, marker=mk[n], color=col[g], alpha=0.45, lw=0,
                       label=f"{'2000' if n == 'sub2000' else '500 (seed 1)'}, {g}-atom")
    lim = [-0.5, 4.5]
    ax.plot(lim, lim, color="k", lw=0.9, ls="--")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel(r"certified $C_\varrho-\Omega$ on $[0.002,0.585]$"); ax.set_ylabel(r"actual $\log(n_0/n_{0.002})$")
    ax.legend(fontsize=6.5, loc="upper left", markerscale=2.5, handletextpad=0.2)
    ax.set_title("(a) certificate holds above the diagonal", fontsize=9, loc="left")
    ax = axes[1]                                   # (b) discretisation gap vs number of Heun steps
    steps = [18, 36, 64]
    for g in ("on", "off"):
        med = [abs(IDI[f"sub500_s{s}"]["windows"]["late"][g]["gap"]["median"]) for s in steps]
        mx = [IDI[f"sub500_s{s}"]["windows"]["late"][g]["gap"]["max_abs"] for s in steps]
        ax.loglog(steps, med, marker="o", color=col[g], lw=1.5, label=f"{g}-atom, |median|")
        ax.loglog(steps, mx, marker="s", color=col[g], lw=1.0, ls=":", label=f"{g}-atom, max")
    ref = np.array(steps, float)
    ax.loglog(ref, 0.043 * (ref / 18) ** -2, color="k", lw=0.8, ls="--", label=r"$\propto(\mathrm{steps})^{-2}$")
    ax.set_xticks(steps); ax.set_xticklabels([str(s) for s in steps]); ax.minorticks_off()
    ax.set_xlabel("Heun steps (first 500-image model)"); ax.set_ylabel(r"$|\log(n_0/n_1)-C_{\rm rad}|$, late window")
    ax.legend(fontsize=6.3, loc="lower left")
    ax.set_title("(b) identity gap is discretisation", fontsize=9, loc="left")
    ax = axes[2]                                   # (c) certified output bound vs label
    for n in ("sub2000", "sub500s1"):
        d = D[n]; BK = AC[n][3]["R"][0]
        x = BK / (d["d2"] / 3); y = d["d1"] / d["d2"]
        for g in ("on", "off"):
            s = d[g]
            ax.scatter(x[s], y[s], s=5, marker=mk[n], color=col[g], alpha=0.45, lw=0)
    xs = np.logspace(-1.2, 1.2, 50)
    ax.plot(xs, xs / 3, color="k", lw=0.9, ls="--", label=r"$d_1/d_2=x/3$ (valid bound: below)")
    ax.axvline(1, color=OI["green"], lw=1.0); ax.axhline(1 / 3, color="grey", lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xlim(10 ** -1.2, 10 ** 1.2); ax.set_ylim(0, 1.0)
    ax.text(0.08, 0.92, "certified\n(left of green)", fontsize=7, color=OI["green"], transform=ax.transAxes, va="top")
    ax.set_xlabel(r"$B_K/(d_2/3)$, predictive anchor at $\sigma_0=0.585$"); ax.set_ylabel(r"$d_1/d_2$ (off-atom $\geq1/3$)")
    ax.legend(fontsize=6.5, loc="upper right")
    ax.set_title("(c) one-sided landing certificate", fontsize=9, loc="left")
    for a in axes:
        a.tick_params(labelsize=7.5)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(f"{stem}.pdf", bbox_inches="tight"); fig.savefig(f"{stem}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------------- report
def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    D = {n: load(n) for n in RUNS}
    GM = {m: gap_map(m) for m in ("sub500", "sub2000", "sub500s1")}
    R = {"meta": {"script": "scripts/paperB_certificate.py", "sources": {n: RUNS[n][0] for n in RUNS},
                  "memo_sources": MEMO, "off_atom": "d1/d2 >= 1/3", "sigma0": SIG0,
                  "integral": "trapezoid in log sigma on the sampler grid (as scripts/make_edm_figures.py fig_clocks)",
                  "bootstrap": {"B": B_BOOT, "seed": SEED}}}
    # consistency of the two sub500 runs (same latents, batch 25 vs 50)
    a, b = D["sub500_rho"], D["sub500_s18"]
    R["meta"]["sub500_rho_vs_s18"] = {"same_off_label": float((a["off"] == b["off"]).mean()),
                                      "median_rel_d1_diff": float(np.median(np.abs(a["d1"] - b["d1"]) / b["d1"])),
                                      "max_rel_d1_diff": float(np.max(np.abs(a["d1"] - b["d1"]) / b["d1"]))}
    L = ["# Paper B: the late-contraction certificate on saved EDM trajectories", "",
         "Generated by `scripts/paperB_certificate.py`. Integrals are trapezoidal in log sigma on the sampler grid; "
         "late window = [0.002, sigma_0] with sigma_0 the grid point nearest 0.585. Off-atom: d1/d2 >= 1/3. "
         "All logs natural. 'actual' = log(n_0/n_1) of n1 = |x - y1| on the Heun trajectory.", ""]

    # ---- 1 + 2
    IDI = {}
    for n in RUNS:
        IDI[n] = identity_and_inequality(D[n])
    R["identity_inequality"] = {n: {k: v for k, v in r.items() if k != "_arrays"} for n, r in IDI.items()}
    L += ["## 1. Identity log(n_0/n_1) = C_rad: Heun discretisation gap (gap = actual - C_rad)", "",
          "| run | steps | sigma_0 | group | n | actual (med) | C_rad (med) | gap med | gap p1 | gap p99 | max abs gap | full-window gap med | full max abs |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in IDI.items():
        wl, wf = r["windows"]["late"], r["windows"]["full"]
        for g in ("on", "off"):
            if g not in wl:
                continue
            x, y = wl[g], wf[g]
            L.append(f"| {n} | {r['steps']} | {r['sigma0_used']:.3g} | {g} | {x['gap']['n']} | {f3(x['actual']['median'])} | "
                     f"{f3(x['C_rad']['median'])} | {f3(x['gap']['median'])} | {f3(x['gap']['p1'])} | {f3(x['gap']['p99'])} | "
                     f"{f3(x['gap']['max_abs'])} | {f3(y['gap']['median'])} | {f3(y['gap']['max_abs'])} |")
    for n in ("sub2000", "sub500s1", "sub500_rho"):
        r = IDI[n]
        L += ["", f"Per grid interval, {n} (gap = actual - trapezoidal C_rad on [sigma_k+1, sigma_k]; viol = share of "
              "samples with actual < C_rho - Omega on that interval):", "",
              "| k | sigma_k -> sigma_k+1 | gap med on | gap med off | max abs gap | gap p1 (all) | gap p99 (all) | viol on | viol off |",
              "|---|---|---|---|---|---|---|---|---|"]
        for row in r["per_interval"]:
            on_, off_, al = row.get("on", {}), row.get("off", {}), row["all"]
            L.append(f"| {row['k']} | {row['sigma_k']:.4g} -> {row['sigma_k1']:.4g} | {f3(on_.get('gap_median'))} | "
                     f"{f3(off_.get('gap_median'))} | {f3(al['gap_max_abs'])} | {f3(al['gap_p1'])} | {f3(al['gap_p99'])} | "
                     f"{f3(on_.get('frac_violating'))} | {f3(off_.get('frac_violating'))} |")
    L += ["", "Last Euler step (sigma 0.002 -> 0, x_K = D(x_17)): exact bounds -log(rho + omega/n) <= log(n_17/n_K) "
          "<= -log|rad| (omega = 0 where not saved). 'to-end gap' = log(n_0/n_K) - [C_rad(late) - log rad_17].", "",
          "| run | group | log(n17/nK) med | upper - actual med | actual - lower med | within bounds | to-end gap med | to-end gap max abs |",
          "|---|---|---|---|---|---|---|---|"]
    for n, r in IDI.items():
        for g in ("on", "off"):
            if g not in r["last_step"]:
                continue
            x = r["last_step"][g]
            L.append(f"| {n} | {g} | {f3(x['log_n17_over_nK']['median'])} | {fe(x['upper_minus_actual']['median'])} | "
                     f"{fe(x['actual_minus_lower']['median'])} | {f3(x['frac_within_bounds'])} | {f3(x['to_end_gap']['median'])} | "
                     f"{f3(x['to_end_gap']['max_abs'])} |")

    L += ["", "## 2. Certificate log(n_0/n_1) >= C_rho - Omega over the late window", "",
          "Pointwise rad <= rho + omega/n is exact (min slack below); violations of the integrated inequality can only "
          "come from the discretisation gap. slack = actual - (C_rho - Omega) = gap + triangle slack.", "",
          "| run | steps | omega | group | pointwise min slack | C_rho med | Omega med | slack med | gap med | triangle slack med | viol. samples | max deficit | factor | interval viol. | any cumul. viol. |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in IDI.items():
        wl = r["windows"]["late"]
        for g in ("on", "off"):
            if g not in wl:
                continue
            x = wl[g]
            dep = x["violation_depth"]
            L.append(f"| {n} | {r['steps']} | {'yes' if r['has_omega'] else 'no (0)'} | {g} | {fe(r['pointwise_min_slack'])} | "
                     f"{f3(x['C_rho']['median'])} | {fe(x['Omega']['median'])} | {f3(x['slack']['median'])} | {f3(x['gap']['median'])} | "
                     f"{f3(x['triangle_slack']['median'])} | {x['n_violating']}/{x['gap']['n']} ({100 * x['frac_violating']:.1f}%) | "
                     f"{f3(dep['max']) if dep else '0'} | {f3(x['max_violation_factor'])} | "
                     f"{100 * r['frac_interval_violations_late'][g]:.1f}% | {100 * r['frac_any_cumulative_violation_late'][g]:.1f}% |")

    L += ["", "Overshoot: samples with rad < 0 somewhere in the late window (the denoiser output lies beyond y1 along "
          "x - y1); they carry the large negative late-window gaps:", ""]
    for n in ("sub500_rho", "sub500s1", "sub2000", "sub500_s36", "sub500_s64"):
        o = IDI[n]["overshoot_rad_negative_late"]
        L.append(f"- {n}: " + "; ".join(
            f"{g} {v['n']}/{v['of']}, gap median {f3(v['gap_median_overshoot'])} vs {f3(v['gap_median_rest'])} for the rest "
            f"(rest min {f3(v['gap_min_rest'])})" for g, v in o.items() if g != "all"))
    for n in RUNS:
        v = IDI[n]["late_window_violators"]
        if v:
            L.append(f"- late-window certificate violators in {n}: {v}")

    # ---- 3
    R["anchor_certificate"] = {}; R["endpoint_certificate"] = {}
    L += ["", "## 3. One-sided certificate of landing from the predictive anchor", "",
          "Anchor a = nearest training image of D(x_k) at sigma_0 = 0.585 (no endpoint information). Variants: "
          "S = as specified (nA(sigma_0) exp(-(C_rhoA - Omega)) with the per-step saved anchors and the saved omega, "
          "which is computed for y1); R = restart the certificate at the last anchor switch (valid for one fixed image; "
          "on every step it uses, the anchor equals y1, so the saved omega is the anchor's); D = Cauchy-Schwarz with "
          "|D - a| = dD instead of rho + omega/n (no exact posterior needed); H = discrete Heun chain of Prop. heun(b) "
          "(rigorous for the sampler). Output bound B_K = rho_K B(0.002) + omega_K (exact last step). T1: B_K < d2/3 "
          "(d1 <= B_K < d2/3, uses the endpoint's d2 to read the label); T2: B_K < g_a/4 (training-set gap of a, "
          "endpoint-free; known only for images the exact field reached in the n3_edm_memorization run).", "",
          "| model | variant | output viol. | max n_K/B_K | median log(B_K/n_K) on | T1 on certified | T1 false (off) | T2 on certified (known) | T2 false | literal B(0.002) < d2/3: on / off |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    AC = {}
    for n in ("sub2000", "sub500s1"):
        d = D[n]; gm = GM[d["model"]]
        res, C, B17, extra = anchor_certificate(d, gm, d["i0"], rng)
        sweep = {}
        for i_s in range(9, 15):
            rs, *_ = anchor_certificate(d, gm, i_s)
            sweep[f"{d['sigma'][i_s]:.3g}"] = {"R_T1_on": rs["variants"]["R"]["T1_d2_over_3"],
                                               "D_T1_on": rs["variants"]["D"]["T1_d2_over_3"],
                                               "R_viol_output": rs["variants"]["R"]["viol_output"],
                                               "R_max_violation_factor": rs["variants"]["R"]["max_violation_factor_output"],
                                               "H_T1_on": rs["variants"].get("H", {}).get("T1_d2_over_3"),
                                               "auc_dD_start": rs["baseline"]["auc_dD_start"],
                                               "oracle_zeroFP_recall_dD_start": rs["baseline"].get("oracle_zeroFP_recall_dD_start")}
        res["start_sweep"] = sweep
        R["anchor_certificate"][n] = res
        AC[n] = (res, C, B17, extra)
        for v, o in res["variants"].items():
            t1, t2 = o["T1_d2_over_3"], o["T2_gap_over_4"]
            lit = o["T1_literal_B17_below_d2_over_3"]
            L.append(f"| {n} | {v} | {o['viol_output']}/{len(d['d1'])} | {f3(o['max_violation_factor_output'])} | "
                     f"{f3(o['looseness_log_BK_over_nK']['on']['median'])} | {t1['on_certified']}/{t1['n_on']} "
                     f"({100 * t1['frac_on']:.1f}%) | {t1['off_certified']}/{t1['n_off']} | "
                     f"{t2['on_certified']}/{t2['n_on_known']} | {t2['off_certified']}/{t2['n_off_known']} | "
                     f"{lit['on_certified']} / {lit['off_certified']} |")
    for n in ("sub500_s18", "sub500_s36", "sub500_s64", "sub500_rho", "sub2000", "sub500s1", "public_s18", "public_s64"):
        d = D[n]
        out = endpoint_certificate(d, GM.get(d["model"], {}))
        R["endpoint_certificate"][n] = out
    L += ["", "Endpoint-anchored (anchor y1, uses endpoint information; E = integral certificate, H = Heun chain):", "",
          "| run | variant | output viol. | max n_K/B_K | T1 on certified | T1 false (off) | T2 on certified (known) |",
          "|---|---|---|---|---|---|---|"]
    for n, out in R["endpoint_certificate"].items():
        for v, o in out.items():
            t1, t2 = o["T1_d2_over_3"], o["T2_gap_over_4"]
            fr = f"({100 * t1['frac_on']:.1f}%)" if t1["n_on"] else ""
            L.append(f"| {n} | {v} | {o['viol_output']}/{len(D[n]['d1'])} | {f3(o['max_violation_factor_output'])} | "
                     f"{t1['on_certified']}/{t1['n_on']} {fr} | {t1['off_certified']}/{t1['n_off']} | "
                     f"{t2['on_certified']}/{t2['n_on_known']} |")
    L += ["", "Anchor bookkeeping and baseline comparison (predictive anchor, sigma_0 = 0.585):", "",
          "| model | anchor = y1 at sigma_0 (on / off) | anchor switches in window (on / off) | max abs(C_R - C_D) | "
          "AUC dD(sigma_0) | AUC -C_R | AUC -C_S | AUC log B_K | zero-FP recall dD(sigma_0) (oracle) | zero-FP recall C_R (oracle) | "
          "naive dD(sigma_0) < d2/3 (on / off) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, (res, *_rest) in AC.items():
        a_, s_, b_ = res["anchor_start_is_y1"], res["anchor_switch_in_window"], res["baseline"]
        L.append(f"| {n} | {a_['on']}/{a_['n_on']} / {a_['off']}/{a_['n_off']} | {s_['on']} / {s_['off']} | "
                 f"{fe(res['max_abs_C_R_minus_C_D'])} | {f3(b_['auc_dD_start'])} | {f3(b_['auc_minus_C_R'])} | "
                 f"{f3(b_['auc_minus_C_S'])} | {f3(b_['auc_logBK_R'])} | {f3(b_['oracle_zeroFP_recall_dD_start'])} | "
                 f"{f3(b_['oracle_zeroFP_recall_C_R'])} | {b_['naive_dD_start_below_d2_over_3']['on']} / "
                 f"{b_['naive_dD_start_below_d2_over_3']['off']} |")
    L += ["", "Paired stratified bootstrap (95%) of the baseline dD(sigma_0) against the late contraction and against the "
          "certified bound, and the T1 margin B_K/(d2/3) (certified when < 1):", ""]
    for n, (res, *_rest) in AC.items():
        b_ = res["baseline"]
        x, y = b_["boot_dD_vs_minusC_R"], b_["boot_dD_vs_logBK_R"]
        mg = res["variants"]["R"]["T1_margin_BK_over_d2_3"]
        L.append(f"- {n}: AUC dD(0.585) {f3(x['a'][0])} [{f3(x['a'][1])}, {f3(x['a'][2])}], AUC -C {f3(x['b'][0])} "
                 f"[{f3(x['b'][1])}, {f3(x['b'][2])}], difference {f3(x['a_minus_b'][0])} [{f3(x['a_minus_b'][1])}, "
                 f"{f3(x['a_minus_b'][2])}]; AUC log B_K {f3(y['b'][0])}, dD - log B_K {f3(y['a_minus_b'][0])} "
                 f"[{f3(y['a_minus_b'][1])}, {f3(y['a_minus_b'][2])}]. Margin on-atom median {f3(mg['on']['median'])} "
                 f"(IQR {f3(mg['on']['p25'])}-{f3(mg['on']['p75'])}); smallest off-atom margin {f3(mg['off_min'])}. "
                 f"Output violators: {res['variants']['R']['violators']}")
    L += ["", "Start of the certificate (variant R and D, T1) against sigma_start:", "",
          "| model | sigma_start | R: on certified | R: false | R: output viol. | R: max n_K/B_K | D: on certified | H: on certified | AUC dD(sigma_start) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for n, (res, *_rest) in AC.items():
        for s, v in res["start_sweep"].items():
            h = v["H_T1_on"]
            L.append(f"| {n} | {s} | {v['R_T1_on']['on_certified']}/{v['R_T1_on']['n_on']} | {v['R_T1_on']['off_certified']} | "
                     f"{v['R_viol_output']} | {f3(v['R_max_violation_factor'])} | {v['D_T1_on']['on_certified']} | "
                     f"{h['on_certified'] if h else '-'} | {f3(v['auc_dD_start'])} |")
    L += ["", "Off-atom threshold sensitivity (variant R, sigma_0 = 0.585; certified when B_K < tau d2):", ""]
    for n, (res, *_rest) in AC.items():
        L.append(f"- {n}: " + "; ".join(f"tau {t}: {v['on_certified']}/{v['n_on']} on-atom certified, {v['false']} false "
                                       f"(of {v['n_off']} off-atom)" for t, v in res["threshold_sensitivity_R"].items())
                 + f"; AUC of d1 itself (= dD at 0.002) {f3(res['baseline'].get('auc_d1_itself'))}")

    # ---- 4
    R["r2"] = {}
    memo_dD = {}
    if "sub500" in MEMO:   # sub500_s18 reproduces the n3_edm_memorization trajectories exactly (d1 identical)
        m = np.load(MEMO["sub500"])
        if np.array_equal(m["d1"], D["sub500_s18"]["d1"]):
            memo_dD["sub500_s18"] = m["nn_hat"]
    for n in ("sub2000", "sub500s1", "sub500_s18", "sub500_rho", "public_rho"):
        d = D[n]
        dD = d["dD"] if d["has_anchor"] else memo_dD.get(n)
        logB_D = None
        if n in AC:
            logB = np.log(AC[n][2]["R"])                                 # predictive anchor, restart variant
            logB_D = np.log(AC[n][2]["D"])
        else:                                                            # endpoint anchor
            i0 = d["i0"]; om = d["omega"] / d["n1"] if d["has_omega"] else np.zeros_like(d["n1"])
            logB = np.log(d["n1"][:, i0]) - (incr(1 - d["err"] / d["n1"], d["ls"])[:, i0:].sum(1)
                                             - incr(om, d["ls"])[:, i0:].sum(1))
        R["r2"][n] = r2_analysis(d, dD, rng, logB, logB_D)
    L += ["", "## 4. Variance of log d1 explained (R^2 of simple linear regressions)", "",
          "C over [sigma_1, 0.585]; 'pred' uses the predictive anchor (rhoA), 'endpoint' the endpoint anchor (paper's C). "
          "dD at 0.002 equals d1 exactly (x_K = D(x_17)), so it is bookkeeping.", ""]
    for n, r in R["r2"].items():
        gs = r["groups"]
        keys = list(next(iter(gs.values()))["r2"].keys())
        L += [f"### {n}", "", "| predictor | " + " | ".join(f"R2 {g} (n={gs[g]['n']})" for g in gs) + " | " +
              " | ".join(f"slope {g}" for g in gs) + " |", "|---|" + "---|" * (2 * len(gs))]
        for k in keys:
            L.append(f"| {k} | " + " | ".join(f3(gs[g]["r2"][k]) for g in gs) + " | " +
                     " | ".join(f3(gs[g]["slope"][k]) for g in gs) + " |")
        if "r2_two_predictors_C_late_and_log_dD_sigma0" in next(iter(gs.values())):
            L.append("| C(late) + log dD(0.585), two predictors | " +
                     " | ".join(f3(gs[g]["r2_two_predictors_C_late_and_log_dD_sigma0"]) for g in gs) + " |")
        if "bootstrap95" in r:
            L += ["", f"bootstrap 95% ({B_BOOT} stratified resamples): " + "; ".join(
                f"{g}: C {f3(v['C_late'][0])}-{f3(v['C_late'][1])}, log dD {f3(v['log_dD_sigma0'][0])}-{f3(v['log_dD_sigma0'][1])}, "
                f"difference {f3(v['difference'][0])}-{f3(v['difference'][1])}" for g, v in r["bootstrap95"].items())]
        L.append("")

    # ---- reproduce the paper's late-contraction numbers (endpoint anchor, no Omega)
    rep = {}
    for n in ("sub500_rho", "sub500s1", "sub2000", "sub500_s18"):
        d = D[n]; i0 = d["i0"]
        C = incr(1 - d["err"] / d["n1"], d["ls"])[:, i0:].sum(1)
        rep[n] = {"C_on_median": float(np.median(C[d["on"]])), "C_off_median": float(np.median(C[d["off"]])),
                  "auc_minus_C": auc(-C[d["off"]], -C[d["on"]]), "n_off": int(d["off"].sum())}
        if d["has_anchor"]:
            CA = incr(1 - d["rhoA"], d["ls"])[:, i0:].sum(1)
            rep[n].update(CA_on_median=float(np.median(CA[d["on"]])), CA_off_median=float(np.median(CA[d["off"]])),
                          auc_minus_CA=auc(-CA[d["off"]], -CA[d["on"]]),
                          n_samples_CA_ne_C=int((np.abs(CA - C) > 1e-9).sum()))
    R["reproduced_paper_late_contraction"] = rep
    L += ["## Reproduced paper numbers (late contraction, endpoint anchor, trapezoid, no Omega)", "",
          "| run | C on (med) | C off (med) | AUC of -C | C with predictive anchor on / off | AUC | samples where they differ |",
          "|---|---|---|---|---|---|---|"]
    for n, v in rep.items():
        L.append(f"| {n} | {f3(v['C_on_median'])} | {f3(v['C_off_median'])} | {f3(v['auc_minus_C'])} | "
                 f"{f3(v.get('CA_on_median'))} / {f3(v.get('CA_off_median'))} | {f3(v.get('auc_minus_CA'))} | "
                 f"{v.get('n_samples_CA_ne_C', '-')} |")
    # rho_A versus dD/nA in the late window
    eqs = {}
    for n in ("sub2000", "sub500s1"):
        d = D[n]; i0 = d["i0"]
        diff = np.abs(d["rhoA"] - d["dD"] / d["nA"])[:, i0:]
        eqs[n] = {"median_abs_diff_late": float(np.median(diff)), "max_abs_diff_late": float(diff.max()),
                  "n_samples_diff_gt_1e-6": int((diff > 1e-6).any(1).sum()),
                  "dD_last_equals_d1_maxdiff": float(np.max(np.abs(d["dD"][:, -1] - d["d1"])))}
    R["rhoA_vs_dD_over_nA"] = eqs
    L += ["", "rho_A versus dD/n_A in the late window (|rho_A - dD/n_A| <= omega/n_A; the exact posterior is a point mass):", ""]
    for n, v in eqs.items():
        L.append(f"- {n}: median |diff| {fe(v['median_abs_diff_late'])}, max {fe(v['max_abs_diff_late'])}, samples with any "
                 f"|diff| > 1e-6: {v['n_samples_diff_gt_1e-6']}; max |dD(0.002) - d1| = {fe(v['dD_last_equals_d1_maxdiff'])}")
    try:
        make_figure(D, IDI, AC, OUT / "fig_certificate_diagnostics")
        R["meta"]["figure"] = str(OUT / "fig_certificate_diagnostics.pdf")
    except ImportError as e:  # matplotlib missing: the numbers do not depend on the figure
        R["meta"]["figure"] = f"skipped ({e})"
    R["meta"]["seconds"] = time.time() - t0

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    (OUT / "certificate.json").write_text(json.dumps(clean(R), indent=1), encoding="utf-8")
    (OUT / "CERTIFICATE_TABLES.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nwrote {OUT / 'certificate.json'} and {OUT / 'CERTIFICATE_TABLES.md'} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
