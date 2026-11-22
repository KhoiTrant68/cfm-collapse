"""Independent verification of the "certificate" analysis (paper B), written without reading
scripts/paperB_certificate.py. numpy only.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_certificate

Theory checked (probability-flow ODE dx/dsigma = (x - D)/sigma, fixed image a, n = |x - a|):
    d log n / d log sigma = 1 - rad,   rad = <(x-a)/n, D - a>/n
    rad <= |D - a|/n <= rho + omega/n, rho = |D - m*|/n, omega = (1 - w_a) max_j |a - y_j|
so  log(n(s0)/n(s1)) = C_rad >= C_rho - Omega, every integral in d log(1/sigma), trapezoid on the grid.

Saved per-sample keys (scripts/n3_directional_q.py): index i is the state x_i at sigma_i; the last
grid point is sigma = 0.002 and the final output is x_K = D(x_{K-1}) (Euler step to sigma = 0).
Off-atom: d1/d2 >= 1/3.

Outputs: results/paperB_20261121/verify_certificate/{verify_certificate.json, VERIFY_CERTIFICATE.md}
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

OUT = pathlib.Path("results/paperB_20261121/verify_certificate")
R = pathlib.Path("results")
FILES = {
    "sub2000": R / "n3_rho2_20261118/sub2000/q_per_sample.npz",          # 2000-image model, omega + anchor keys
    "sub500s1": R / "n3_rho2_20261118/sub500s1/q_per_sample.npz",        # second 500-image model, omega + anchor
    "sub500_rho": R / "n3_rho_20261117/sub500/q_per_sample.npz",         # first 500-image model, no omega
    "public_rho": R / "n3_rho_20261117/public/q_per_sample.npz",         # public model, 200 samples, no omega
    "s18_sub500": R / "n3_steps_20261117/s18/sub500/q_per_sample.npz",   # first 500-image model, omega
    "s36_sub500": R / "n3_steps_20261117/s36/sub500/q_per_sample.npz",
    "s64_sub500": R / "n3_steps_20261117/s64/sub500/q_per_sample.npz",
    "s18_public": R / "n3_steps_20261117/s18/public/q_per_sample.npz",
    "s36_public": R / "n3_steps_20261117/s36/public/q_per_sample.npz",
    "s64_public": R / "n3_steps_20261117/s64/public/q_per_sample.npz",
    "anchor_sub500": R / "n3_anchor_20261117/sub500/q_per_sample.npz",   # first 500-image model WITH anchor keys
    "anchor_public": R / "n3_anchor_20261117/public/q_per_sample.npz",
}
MEMO = {  # n3_edm_memorization runs: nn_hat (= dD) and exact-field endpoints (gap of the image reached)
    "sub2000": R / "n3_edm_sub2000_20261117/sub2000_s0/per_sample.npz",
    "sub500s1": R / "n3_edm_sub500s1_20261117/sub500_s1/per_sample.npz",
    "sub500": R / "n3_edm_sub500_20261115/sub500_s0/per_sample.npz",
}
B_BOOT = 2000
RNG = np.random.default_rng(20261121)
Z95 = 1.959963984540054


# ----------------------------------------------------------------------------- helpers
def load(p):
    z = np.load(p)
    return {k: z[k] for k in z.files}


def i_near(sig, s0):
    return int(np.argmin(np.abs(np.log(sig) - np.log(s0))))


def dlog(sig):
    return np.log(sig[:-1]) - np.log(sig[1:])          # log(sigma_i / sigma_{i+1}) > 0


def inc(f, sig):
    """Per-interval trapezoid of f in d log(1/sigma): shape (n, K-1)."""
    return 0.5 * (f[:, :-1] + f[:, 1:]) * dlog(sig)[None]


def trap(f, sig, i0, i1):
    return inc(f, sig)[:, i0:i1].sum(1)


def auc(pos, neg):
    """P(pos > neg) + P(tie)/2 via average ranks."""
    x = np.concatenate([pos, neg])
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    avg = np.cumsum(cnt) - (cnt - 1) / 2.0
    r = avg[inv]
    n1, n0 = len(pos), len(neg)
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def boot_auc(scores, off, pairs=(), B=B_BOOT, rng=RNG):
    io, ii = np.where(off)[0], np.where(~off)[0]
    est = {k: auc(v[off], v[~off]) for k, v in scores.items()}
    for a, b in pairs:
        est[f"{a}-{b}"] = est[a] - est[b]
    dr = {k: [] for k in est}
    for _ in range(B):
        so, si = rng.choice(io, len(io)), rng.choice(ii, len(ii))
        d = {k: auc(v[so], v[si]) for k, v in scores.items()}
        for a, b in pairs:
            d[f"{a}-{b}"] = d[a] - d[b]
        for k in est:
            dr[k].append(d[k])
    return {k: [round(est[k], 4), *[round(float(q), 4) for q in np.percentile(dr[k], [2.5, 97.5])]] for k in est}


def r2(y, *xs):
    X = np.column_stack([np.ones(len(y))] + list(xs))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    return float(1 - (res @ res) / ((y - y.mean()) @ (y - y.mean()))), beta


def boot_r2_diff(y, xa, xb, strata, B=B_BOOT, rng=RNG):
    """Stratified bootstrap of R^2(xa) - R^2(xb) (paired) and each R^2."""
    groups = [np.where(strata == g)[0] for g in np.unique(strata)]
    da, db, dd = [], [], []
    for _ in range(B):
        idx = np.concatenate([rng.choice(g, len(g)) for g in groups])
        a = r2(y[idx], xa[idx])[0]; b = r2(y[idx], xb[idx])[0]
        da.append(a); db.append(b); dd.append(a - b)
    q = lambda v: [round(float(x), 4) for x in np.percentile(v, [2.5, 97.5])]  # noqa: E731
    return {"r2_a": round(r2(y, xa)[0], 4), "r2_a_ci": q(da), "r2_b": round(r2(y, xb)[0], 4), "r2_b_ci": q(db),
            "diff": round(r2(y, xa)[0] - r2(y, xb)[0], 4), "diff_ci": q(dd)}


def wilson(k, n, z=Z95):
    if n == 0:
        return [float("nan")] * 2
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(float(c - h), 4), round(float(c + h), 4)]


def med(v):
    return float(np.median(v)) if len(v) else float("nan")


def pct(v, q):
    return float(np.percentile(v, q)) if len(v) else float("nan")


def vmax(v):
    return float(np.max(v)) if np.size(v) else float("nan")


def fmean(v):
    return float(np.mean(v)) if np.size(v) else float("nan")


def rnd(x, k=4):
    return None if x is None else (round(float(x), k) if np.isfinite(x) else float("nan"))


# ----------------------------------------------------------------------------- data
Z = {k: load(p) for k, p in FILES.items() if p.exists()}
M = {k: load(p) for k, p in MEMO.items() if p.exists()}
res: dict = {"files": {k: str(p) for k, p in FILES.items()}, "memo_files": {k: str(p) for k, p in MEMO.items()}}
L: list[str] = ["# Independent verification of the certificate analysis", "",
                "Script: scripts/paperB_verify_certificate.py (numpy only). Off-atom = d1/d2 >= 1/3. "
                "Integrals are trapezoids in log sigma on the sampler grid; the late window runs from the grid "
                "point nearest sigma = 0.585 to sigma = 0.002.", ""]

# 0. labels and sanity
sanity = {}
for k, z in Z.items():
    off = z["d1"] / z["d2"] >= 1 / 3
    sanity[k] = {"n": int(len(off)), "off": int(off.sum()), "on": int((~off).sum()), "K": int(len(z["sigma"])),
                 "max|n1_end-d1|": float(np.max(np.abs(z["n1_end"] - z["d1"]))),
                 "has_omega": "omega" in z, "has_anchor": "anc" in z}
    if "dD" in z:
        sanity[k]["max|dD_last-d1|"] = float(np.max(np.abs(z["dD"][:, -1] - z["d1"])))
        sanity[k]["anc_last==nn1"] = float(np.mean(z["anc"][:, -1] == z["nn1"]))
    if "err" in z:
        # does err at sigma = 0.002 equal the endpoint distance d1? (x_K = D(x_{K-1}), m* ~ point mass)
        sanity[k]["median|err_last-d1|/d1"] = float(np.median(np.abs(z["err"][:, -1] - z["d1"]) / z["d1"]))
        sanity[k]["max|err_last-d1|/d1"] = float(np.max(np.abs(z["err"][:, -1] - z["d1"]) / z["d1"]))
res["sanity"] = sanity
L += ["## 0. Sanity", "", "| run | n | off | K | max abs(n1_end - d1) | max abs(dD_last - d1) | anc_last = nn1 | "
      "median abs(err_last - d1)/d1 |", "|---|---|---|---|---|---|---|---|"]
for k, s in sanity.items():
    L.append(f"| {k} | {s['n']} | {s['off']} | {s['K']} | {s['max|n1_end-d1|']:.1e} | "
             f"{s.get('max|dD_last-d1|', float('nan')):.1e} | {s.get('anc_last==nn1', float('nan'))} | "
             f"{s.get('median|err_last-d1|/d1', float('nan')):.2e} |")


# ----------------------------------------------------------------------------- 1. identity
def identity(z, s0=0.585):
    sig = z["sigma"]; K = len(sig); i0 = i_near(sig, s0); i1 = K - 1
    off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    ln = np.log(z["n1"])
    act_int = ln[:, :-1] - ln[:, 1:]                      # actual per-interval log contraction
    crad_int = inc(1 - z["rad1"], sig)
    gap_int = act_int - crad_int
    act = act_int[:, i0:i1].sum(1); gap = gap_int[:, i0:i1].sum(1)
    negrad = (z["rad1"][:, i0:i1 + 1] < 0).any(1)
    out = {"i0": i0, "sigma0": float(sig[i0]),
           "act_med_on": med(act[on]), "act_med_off": med(act[off]),
           "gap_med_on": med(gap[on]), "gap_med_off": med(gap[off]),
           "gap_p01_on": pct(gap[on], 1), "gap_p99_on": pct(gap[on], 99),
           "gap_p01_off": pct(gap[off], 1), "gap_p99_off": pct(gap[off], 99),
           "frac_gap_neg_on": fmean(gap[on] < 0), "frac_gap_neg_off": fmean(gap[off] < 0),
           "frac_gap_neg_all": fmean(gap < 0),
           "max_abs_gap_on": vmax(np.abs(gap[on])), "max_abs_gap_all": vmax(np.abs(gap)),
           "ratio_med_gap_over_act_on": med(gap[on] / act[on]), "ratio_of_medians_on": med(gap[on]) / med(act[on]),
           "max_abs_gap_interval_above_s0": float(np.max(np.abs(gap_int[:, :i0]))),
           "max_abs_gap_interval_late": float(np.max(np.abs(gap_int[:, i0:i1]))),
           "n_on_negrad_late": int(negrad[on].sum()), "n_on": int(on.sum()),
           "gap_med_on_negrad": med(gap[on & negrad]), "gap_med_on_posrad": med(gap[on & ~negrad])}
    # last Euler step x_K = D(x_{K-1}): -log(rho + omega/n) <= log(n_{K-1}/n_K) <= -log|rad|
    if "omega" in z:
        nl = z["n1"][:, -1]; lastact = np.log(nl / z["n1_end"])
        lo = -np.log(z["err"][:, -1] / nl + z["omega"][:, -1] / nl); hi = -np.log(np.abs(z["rad1"][:, -1]))
        out["last_step_lower_viol"] = int((lastact < lo - 1e-9).sum()); out["last_step_upper_viol"] = int((lastact > hi + 1e-9).sum())
    return out, gap, act


res["identity"] = {}
for k in ("sub2000", "sub500s1", "sub500_rho", "s18_sub500", "s36_sub500", "s64_sub500", "anchor_sub500",
          "public_rho", "s18_public", "s36_public", "s64_public"):
    if k in Z:
        res["identity"][k] = identity(Z[k])[0]
L += ["", "## 1. Identity log(n0/n1) = C_rad (gap = actual - trapezoid C_rad, late window)", "",
      "| run | sigma0 | actual on | gap on | gap off | p1..p99 on | frac gap<0 on / off | max abs gap on | "
      "max abs interval gap above s0 | on with rad<0 late | gap on (rad<0 / rest) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for k, o in res["identity"].items():
    L.append(f"| {k} | {o['sigma0']:.3f} | {o['act_med_on']:.3f} | {o['gap_med_on']:.4f} | {o['gap_med_off']:.4f} | "
             f"[{o['gap_p01_on']:.3f}, {o['gap_p99_on']:.3f}] | {o['frac_gap_neg_on']:.3f} / {o['frac_gap_neg_off']:.3f} | "
             f"{o['max_abs_gap_on']:.3f} | {o['max_abs_gap_interval_above_s0']:.4f} | {o['n_on_negrad_late']}/{o['n_on']} | "
             f"{o['gap_med_on_negrad']:.3f} / {o['gap_med_on_posrad']:.3f} |")


# ----------------------------------------------------------------------------- 2. certificate inequality
def certificate(z, s0=0.585, use_omega=True):
    sig = z["sigma"]; K = len(sig); i0 = i_near(sig, s0); i1 = K - 1
    off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    n = z["n1"]; rho = z["err"] / n
    om = z["omega"] / n if (use_omega and "omega" in z) else np.zeros_like(n)
    ln = np.log(n)
    act_int = ln[:, :-1] - ln[:, 1:]
    bnd_int = inc(1 - rho, sig) - inc(om, sig)
    ang_int = inc(rho + om - z["rad1"], sig)
    act = act_int[:, i0:i1].sum(1); bnd = bnd_int[:, i0:i1].sum(1); slack = act - bnd
    ang = ang_int[:, i0:i1].sum(1); gap = act - inc(1 - z["rad1"], sig)[:, i0:i1].sum(1)
    pw = rho + om - z["rad1"]
    viol_int = (act_int[:, i0:i1] < bnd_int[:, i0:i1])
    out = {"i0": i0, "with_omega": bool(use_omega and "omega" in z),
           "per_interval_viol_share_on": fmean(viol_int[on]),
           "n_viol": int((slack < 0).sum()), "n": int(len(slack)),
           "viol_on": int((slack[on] < 0).sum()), "viol_off": int((slack[off] < 0).sum()),
           "min_slack": float(slack.min()), "max_factor": float(np.exp(max(0.0, -slack.min()))),
           "slack_med_on": med(slack[on]), "slack_med_off": med(slack[off]),
           "angle_med_on": med(ang[on]), "gap_med_on": med(gap[on]),
           "max|slack-gap-angle|": float(np.max(np.abs(slack - gap - ang))),
           "pointwise_min_all": float(pw.min()), "pointwise_n_neg": int((pw < 0).sum()),
           "pointwise_min_late": float(pw[:, i0:].min()),
           "per_interval_viol_share": float(viol_int.mean()),
           "per_interval_viol_by_interval": [int(v) for v in viol_int.sum(0)],
           "per_interval_sigma_from": [float(s) for s in sig[i0:i1]],
           "per_interval_max_deficit": float(np.max(bnd_int[:, i0:i1] - act_int[:, i0:i1]))}
    if out["n_viol"]:
        j = np.where(slack < 0)[0]
        out["violators"] = [{"idx": int(t), "on_atom": bool(on[t]), "deficit": float(-slack[t]),
                             "d1/d2": float(z["d1"][t] / z["d2"][t])} for t in j]
    # start at sigma0 = 0.06
    i06 = i_near(sig, 0.06)
    s06 = act_int[:, i06:i1].sum(1) - bnd_int[:, i06:i1].sum(1)
    out["s0_0.06"] = {"sigma0": float(sig[i06]), "n_viol": int((s06 < 0).sum()),
                      "max_factor": float(np.exp(max(0.0, -s06.min())))}
    return out, slack


res["certificate"] = {}
for k in ("sub2000", "sub500s1", "s18_sub500", "s36_sub500", "s64_sub500", "s18_public", "s36_public", "s64_public",
          "anchor_sub500", "anchor_public"):
    if k in Z:
        res["certificate"][k] = certificate(Z[k])[0]
for k in ("sub500_rho", "public_rho"):   # no omega: the stronger inequality log(n0/n1) >= C_rho
    res["certificate"][k + "_noomega"] = certificate(Z[k], use_omega=False)[0]
L += ["", "## 2. Certificate log(n0/n1) >= C_rho - Omega over the late window", "",
      "| run | omega | violations (on/off) | min slack | slack on | angle on | gap on | pointwise min | "
      "per-interval share | per-interval by interval | max per-interval deficit | from 0.06: viol, factor |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for k, o in res["certificate"].items():
    L.append(f"| {k} | {o['with_omega']} | {o['n_viol']}/{o['n']} ({o['viol_on']}/{o['viol_off']}) | {o['min_slack']:.4f} | "
             f"{o['slack_med_on']:.3f} | {o['angle_med_on']:.3f} | {o['gap_med_on']:.3f} | {o['pointwise_min_all']:.2e} | "
             f"{o['per_interval_viol_share']:.3f} | {o['per_interval_viol_by_interval']} | {o['per_interval_max_deficit']:.4f} | "
             f"{o['s0_0.06']['n_viol']}, {o['s0_0.06']['max_factor']:.4f} |")


# ----------------------------------------------------------------------------- 3. landing certificate
def gap_map(m):
    """Training-set gap g of each image reached by the exact field: exact_d2 when exact_d1 ~ 0."""
    g = {}
    ok = m["exact_d1"] < 1e-4
    for c, i, d2 in zip(m["label"][ok], m["exact_nn"][ok], m["exact_d2"][ok]):
        g[(int(c), int(i))] = float(d2)
    return g


def landing(z, s0=0.585, anchor="predictive", gmap=None):
    sig = z["sigma"]; K = len(sig); i0 = i_near(sig, s0); last = K - 1; N = len(z["d1"])
    off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    if anchor == "predictive":
        n, rho, a = z["nA"], z["rhoA"], z["anc"]
    else:
        n, rho, a = z["n1"], z["err"] / z["n1"], np.repeat(z["nn1"][:, None], K, 1) if "nn1" in z else None
    om_abs = z["omega"] if "omega" in z else np.zeros_like(n)
    om = om_abs / n
    incC = inc(1 - rho, sig); incO = inc(om, sig)
    # S: literal formula with per-step anchors
    B17 = n[:, i0] * np.exp(-(incC[:, i0:last].sum(1) - incO[:, i0:last].sum(1)))
    BK = rho[:, last] * B17 + om_abs[:, last]
    out = {"i0": i0, "sigma0": float(sig[i0]), "anchor": anchor, "n_on": int(on.sum()), "n_off": int(off.sum())}
    const = np.ones(N, bool) if a is None else (a[:, i0:last + 1] == a[:, i0:i0 + 1]).all(1)
    out["const_anchor_on"] = int(const[on].sum()); out["const_anchor_off"] = int(const[off].sum())
    if a is not None and "nn1" in z:
        out["anchor_s0_eq_y1_on"] = float(np.mean(a[on, i0] == z["nn1"][on]))
        out["anchor_s0_eq_y1_off"] = float(np.mean(a[off, i0] == z["nn1"][off]))
    # R: restart at the last anchor switch
    if a is not None:
        sw = np.zeros(N, int) + i0
        for j in range(i0 + 1, last + 1):
            sw = np.where(a[:, j] != a[:, j - 1], j, sw)
        cumC = np.concatenate([np.cumsum(incC[:, ::-1], 1)[:, ::-1], np.zeros((N, 1))], 1)   # tail sums from index
        cumO = np.concatenate([np.cumsum(incO[:, ::-1], 1)[:, ::-1], np.zeros((N, 1))], 1)
        rr = np.arange(N)
        B17R = n[rr, sw] * np.exp(-(cumC[rr, sw] - cumO[rr, sw]))
        BKR = rho[:, last] * B17R + om_abs[:, last]
        out["restart_after_s0_on"] = int((sw[on] > i0).sum()); out["restart_after_s0_off"] = int((sw[off] > i0).sum())
    else:
        BKR = BK
    # D: |D - a| = dD in place of rho + omega/n (valid when a is the nearest image of D at that step)
    if "dD" in z and anchor == "predictive":
        incD = inc(1 - z["dD"] / n, sig)
        B17D = n[:, i0] * np.exp(-incD[:, i0:last].sum(1))
        BKD = (z["dD"][:, last] / n[:, last]) * B17D
    else:
        BKD = None
    thr = z["d2"] / 3
    for name, b in (("S", BK), ("R", BKR), ("D", BKD), ("S_B17_only", B17)):
        if b is None:
            continue
        cert = b < thr
        valid = const if name in ("S", "D", "S_B17_only") else np.ones(N, bool)
        o = {"cert_on": int(cert[on].sum()), "cert_off": int(cert[off].sum()),
             "cert_on_valid_const": int((cert & valid)[on].sum()),
             "frac_on": float(cert[on].mean()), "wilson_on": wilson(int(cert[on].sum()), int(on.sum())),
             "wilson_false_upper": wilson(int(cert[off].sum()), int(off.sum()))[1] if off.any() else None,
             "margin_med_on": med((b / thr)[on]), "margin_min_off": float((b / thr)[off].min()) if off.any() else None,
             "n_bound_below_d1": int((b < z["d1"] * (1 - 1e-12)).sum()),
             "max_d1_over_bound": float(np.max(z["d1"] / b))}
        for t in (0.2, 0.5):
            offt = z["d1"] / z["d2"] >= t
            ct = b < t * z["d2"]
            o[f"thr{t}"] = {"n_off": int(offt.sum()), "cert_on": int(ct[~offt].sum()), "false": int(ct[offt].sum())}
        out[name] = o
    out["sets_equal_S_R"] = bool(np.array_equal(BK < thr, BKR < thr))
    if BKD is not None:
        out["sets_equal_S_D"] = bool(np.array_equal(BK < thr, BKD < thr))
    # circularity: B_K = err_last * exp(slack) + omega_last when the anchor is fixed; err_last ~ d1
    ln_ = np.log(n)
    slack = (ln_[:, i0] - ln_[:, last]) - (incC[:, i0:last].sum(1) - incO[:, i0:last].sum(1))
    recon = z["err"][:, last] * np.exp(slack) + om_abs[:, last]
    out["circularity"] = {"max_rel|BK - err_last*e^slack - om|_const": float(np.max(np.abs(BK - recon)[const] / BK[const])),
                          "median|err_last/d1 - 1|": float(np.median(np.abs(z["err"][:, last] / z["d1"] - 1))),
                          "median_BK_over_d1_on": med((BK / z["d1"])[on]), "median_exp_slack_on": med(np.exp(slack[on])),
                          "rule_d1/d2<exp(-slack)/3_equals_cert": bool(np.array_equal(BK < thr,
                                                                       (z["d1"] * np.exp(slack) + om_abs[:, last]) < thr))}
    # T2: endpoint-free threshold g_a/4 with g from exact-field endpoints of the matching memorization run
    if gmap is not None:
        aa = z["anc"][:, i0] if anchor == "predictive" else z["nn1"]
        ga = np.array([gmap.get((int(c), int(i)), np.nan) for c, i in zip(z["label"], aa)])
        known = np.isfinite(ga)
        c2 = BKR < ga / 4
        out["T2"] = {"known_on": int((known & on).sum()), "known_off": int((known & off).sum()),
                     "cert_on": int((c2 & known & on).sum()), "cert_off": int((c2 & known & off).sum()),
                     "frac_on": float((c2 & known & on).sum() / max(1, (known & on).sum())),
                     "cert_on_S": int(((BK < ga / 4) & known & on).sum())}
    return out, BK, BKR


def heun_chain(z, s0=0.585, anchor="endpoint"):
    """Rigorous discrete chain of Prop. heun(b) (gamma = 0) from the grid point nearest s0, then the exact last step."""
    sig = z["sigma"]; K = len(sig); i0 = i_near(sig, s0); last = K - 1
    off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    n, nt = z["n1"], z["nt1"]
    r = sig[1:] / sig[:-1]; ka = np.abs((1 - r) * (2 * r - 1) / (2 * r)); th = (1 - r) / (2 * r)
    rk = np.maximum(z["err"][:, :-1] / n[:, :-1], z["errt"][:, :-1] / nt[:, :-1])
    ck = r + ka * rk + th * rk * (r + (1 - r) * rk)
    bk = (ka + th * rk * (1 - r)) * z["omega"][:, :-1] + th * z["omegat"][:, :-1]
    per_step_bound = ck + bk / n[:, :-1]
    act = n[:, 1:] / n[:, :-1]
    B = n[:, i0].copy(); viol = 0
    for k in range(i0, last):
        B = ck[:, k] * B + bk[:, k]
        viol += int((n[:, k + 1] > B * (1 + 1e-9)).sum())
    BK = (z["err"][:, last] / n[:, last]) * B + z["omega"][:, last]
    viol += int((z["n1_end"] > BK * (1 + 1e-9)).sum())
    cert = BK < z["d2"] / 3
    out = {"i0": i0, "sigma0": float(sig[i0]), "cert_on": int(cert[on].sum()), "n_on": int(on.sum()),
           "cert_off": int(cert[off].sum()), "n_off": int(off.sum()), "frac_on": float(cert[on].mean()),
           "wilson_on": wilson(int(cert[on].sum()), int(on.sum())), "violations": viol,
           "per_step_viol": int((act > per_step_bound * (1 + 1e-6) + 1e-9).sum()),
           "median_log_BK_over_nK_on": med(np.log(BK / z["n1_end"])[on]),
           "per_step_bound_med_on": {f"{sig[k]:.4g}": round(med(per_step_bound[on, k]), 3) for k in range(len(sig) - 1)},
           "per_step_factor_med_on": {f"{sig[k]:.4g}": round(med(act[on, k]), 3) for k in range(len(sig) - 1)}}
    return out, BK


res["landing"] = {}
gm = {k: gap_map(m) for k, m in M.items()}
for k, anc_mode, gkey in (("sub2000", "predictive", "sub2000"), ("sub500s1", "predictive", "sub500s1"),
                          ("anchor_sub500", "predictive", "sub500"),
                          ("sub2000", "endpoint", "sub2000"), ("sub500s1", "endpoint", "sub500s1"),
                          ("s18_sub500", "endpoint", "sub500"), ("anchor_sub500", "endpoint", "sub500"),
                          ("s36_sub500", "endpoint", None), ("s64_sub500", "endpoint", None),
                          ("s18_public", "endpoint", None), ("s36_public", "endpoint", None), ("s64_public", "endpoint", None),
                          ("anchor_public", "predictive", None)):
    if k in Z:
        res["landing"][f"{k}:{anc_mode}"] = landing(Z[k], anchor=anc_mode, gmap=gm.get(gkey) if gkey else None)[0]
res["heun_chain"] = {}
for k in ("sub2000", "sub500s1", "s18_sub500", "s36_sub500", "s64_sub500", "anchor_sub500", "s18_public", "s64_public"):
    if k in Z:
        res["heun_chain"][k] = heun_chain(Z[k])[0]
L += ["", "## 3. Landing certificate B_K = rho_last B(0.002) + omega_last, certified if B_K < d2/3", "",
      "| run:anchor | sigma0 | S cert on | S false | Wilson on | S margin on / min off | R cert on | R false | "
      "S = R | S = D | const anchor on/off | anchor(s0) = y1 on/off | B_K/d1 on | e^slack on | cert = rule d1 e^slack < d2/3 |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for k, o in res["landing"].items():
    S = o["S"]; Rr = o.get("R", S)
    L.append(f"| {k} | {o['sigma0']:.3f} | {S['cert_on']}/{o['n_on']} ({100 * S['frac_on']:.1f}%) | {S['cert_off']}/{o['n_off']} | "
             f"{S['wilson_on']} | {S['margin_med_on']:.2f} / {S['margin_min_off'] if S['margin_min_off'] is None else round(S['margin_min_off'], 2)} | "
             f"{Rr['cert_on']} | {Rr['cert_off']} | {o['sets_equal_S_R']} | {o.get('sets_equal_S_D', '-')} | "
             f"{o['const_anchor_on']}/{o['const_anchor_off']} | {o.get('anchor_s0_eq_y1_on', '-')}/{o.get('anchor_s0_eq_y1_off', '-')} | "
             f"{o['circularity']['median_BK_over_d1_on']:.3f} | {o['circularity']['median_exp_slack_on']:.3f} | "
             f"{o['circularity']['rule_d1/d2<exp(-slack)/3_equals_cert']} |")
L += ["", "T2 (B_K < g_a/4, g_a from exact-field endpoints of the n3_edm_memorization run with the same latents):", ""]
for k, o in res["landing"].items():
    if "T2" in o:
        t = o["T2"]
        L.append(f"- {k}: certified {t['cert_on']}/{t['known_on']} on-atom ({100 * t['frac_on']:.1f}%), false {t['cert_off']}/{t['known_off']}")
L += ["", "Heun chain (Prop. heun(b), gamma = 0, endpoint anchor y1):", "",
      "| run | sigma0 | cert on | false | Wilson | violations | median log(B_K/n_K) on |", "|---|---|---|---|---|---|---|"]
for k, o in res["heun_chain"].items():
    L.append(f"| {k} | {o['sigma0']:.3f} | {o['cert_on']}/{o['n_on']} ({100 * o['frac_on']:.1f}%) | {o['cert_off']}/{o['n_off']} | "
             f"{o['wilson_on']} | {o['violations']} | {o['median_log_BK_over_nK_on']:.3f} |")


# ----------------------------------------------------------------------------- 3b. certificate without the output
def no_output_variant(z, stop_sigma):
    """Predictive-anchor certificate using rho only down to the grid point nearest stop_sigma; rho := 1 (its a priori
    value for a non-expanding late flow) at later grid points and in the last Euler step. With stop at sigma = 0.0075
    nothing depends on D(x_{K-1}) = x_K; omega (a function of the states x_k only) is kept."""
    sig = z["sigma"]; K = len(sig); i0 = i_near(sig, 0.585); s = i_near(sig, stop_sigma); last = K - 1
    off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    rho = z["rhoA"].copy(); rho[:, s + 1:] = 1.0
    n = z["nA"]; om = z["omega"] / n
    B17 = n[:, i0] * np.exp(-(inc(1 - rho, sig)[:, i0:last].sum(1) - inc(om, sig)[:, i0:last].sum(1)))
    BK = rho[:, last] * B17 + z["omega"][:, last]
    cert = BK < z["d2"] / 3
    return {"stop_sigma": float(sig[s]), "cert_on": int(cert[on].sum()), "n_on": int(on.sum()),
            "false": int(cert[off].sum()), "n_off": int(off.sum()), "bound_below_d1": int((BK < z["d1"]).sum()),
            "share_rho_le_1_after_stop": fmean((z["rhoA"][:, s + 1:] <= 1).all(1)) if s + 1 < K else 1.0}


res["no_output_variant"] = {k: [no_output_variant(Z[k], s) for s in (0.002, 0.0075, 0.023, 0.06)]
                            for k in ("sub2000", "sub500s1", "anchor_sub500")}
L += ["", "### 3b. Same certificate without the output: rho := 1 below the stop level and in the last step", "",
      "| run | rho used down to sigma | cert on | false | B_K < d1 | share with rho <= 1 below stop |", "|---|---|---|---|---|---|"]
for k, rows in res["no_output_variant"].items():
    for o in rows:
        L.append(f"| {k} | {o['stop_sigma']:.4g} | {o['cert_on']}/{o['n_on']} | {o['false']}/{o['n_off']} | {o['bound_below_d1']} | "
                 f"{o['share_rho_le_1_after_stop']:.3f} |")


# 3c. the same information read directly: computing rhoA = err/nA needs nA(sigma_k) itself, so the distance to the
# anchor at the stop level is available; with rho <= 1 below it the flow does not expand and nA(sigma_s) bounds d1.
def direct_rule(z, s):
    sig = z["sigma"]; j = i_near(sig, s); off = z["d1"] / z["d2"] >= 1 / 3; on = ~off
    rule = z["nA"][:, j] < z["d2"] / 3
    return {"sigma": float(sig[j]), "cert_on": int(rule[on].sum()), "n_on": int(on.sum()), "false": int(rule[off].sum()),
            "n_off": int(off.sum()), "share_d1_le_nA": float(np.mean(z["d1"] <= z["nA"][:, j]))}


res["direct_distance_rule"] = {k: [direct_rule(Z[k], s) for s in (0.0075, 0.023, 0.06, 0.14)]
                               for k in ("sub2000", "sub500s1", "anchor_sub500")}
L += ["", "### 3c. Direct rule nA(sigma_s) < d2/3 with the same information (no relative error needed)", "",
      "| run | sigma_s | cert on | false | share d1 <= nA(sigma_s) |", "|---|---|---|---|---|"]
for k, rows in res["direct_distance_rule"].items():
    for o in rows:
        L.append(f"| {k} | {o['sigma']:.4g} | {o['cert_on']}/{o['n_on']} | {o['false']}/{o['n_off']} | {o['share_d1_le_nA']:.4f} |")


# ----------------------------------------------------------------------------- 4/5. detector and R^2
def late_C(z, i_from=None, i_to=None, s_from=0.585, s_to=0.002):
    sig = z["sigma"]; a = i_near(sig, s_from) if i_from is None else i_from; b = i_near(sig, s_to) if i_to is None else i_to
    return trap(1 - z["err"] / z["n1"], sig, a, b)


det = {}
for k in ("sub2000", "sub500s1", "anchor_sub500"):
    z = Z[k]; off = z["d1"] / z["d2"] >= 1 / 3; on = ~off; i0 = i_near(z["sigma"], 0.585)
    C = late_C(z)
    _, BK, BKR = landing(z, anchor="predictive")
    sc = {"dD059": z["dD"][:, i0], "negC": -C, "logBK": np.log(BK), "d1": z["d1"], "dD_end": z["dD"][:, -1]}
    d = boot_auc(sc, off, pairs=(("dD059", "negC"), ("dD059", "logBK"), ("negC", "dD_end")))
    thr0 = z["dD"][off, i0].min()
    d["C_med_on_off"] = [round(med(C[on]), 3), round(med(C[off]), 3)]
    d["oracle_dD059_recall_at_zeroFP"] = [int((z["dD"][on, i0] < thr0).sum()), int(on.sum()),
                                          float((z["dD"][on, i0] < thr0).mean())]
    naive = z["dD"][:, i0] < z["d2"] / 3
    d["naive_dD059<d2/3"] = {"on": int(naive[on].sum()), "off": int(naive[off].sum())}
    d["max|dD_end-d1|"] = float(np.max(np.abs(z["dD"][:, -1] - z["d1"])))
    det[k] = d
res["detector"] = det
L += ["", "## 4. Detector AUCs (P(off score > on score)), stratified bootstrap, 2000 resamples", ""]
for k, d in det.items():
    L.append(f"- {k}: " + "; ".join(f"{a} {v}" for a, v in d.items()))

r2res = {}
for k, dsrc in (("sub2000", "self"), ("sub500s1", "self"), ("anchor_sub500", "self"), ("sub500_rho", "memo:sub500"),
                ("s18_sub500", "memo:sub500")):
    z = Z[k]; off = z["d1"] / z["d2"] >= 1 / 3; on = ~off; sig = z["sigma"]; i0 = i_near(sig, 0.585)
    dD = z["dD"][:, i0] if dsrc == "self" else M["sub500"]["nn_hat"][:, i0]
    y = np.log(z["d1"]); C = late_C(z); C14 = trap(1 - z["err"] / z["n1"], sig, i0, i_near(sig, 0.14))
    lb = np.log(z["n1"][:, i0]) - C
    lbA = np.log(z["nA"][:, i0]) - trap(1 - z["rhoA"], sig, i0, len(sig) - 1) if "nA" in z else None
    out = {"dD_source": dsrc}
    strata = off.astype(int)
    for gname, sel in (("pooled", np.ones(len(y), bool)), ("on", on), ("off", off)):
        if sel.sum() < 10:
            continue
        g = {"R2_C": round(r2(y[sel], C[sel])[0], 4), "R2_logdD": round(r2(y[sel], np.log(dD[sel]))[0], 4),
             "R2_both": round(r2(y[sel], C[sel], np.log(dD[sel]))[0], 4),
             "R2_C_0.14": round(r2(y[sel], C14[sel])[0], 4),
             "R2_logn0-C": round(r2(y[sel], lb[sel])[0], 4), "slope_logn0-C": round(float(r2(y[sel], lb[sel])[1][1]), 3)}
        if lbA is not None:
            g["R2_lognA0-CA"] = round(r2(y[sel], lbA[sel])[0], 4)
        bb = boot_r2_diff(y[sel], C[sel], np.log(dD[sel]), strata[sel])
        g["boot_C_minus_dD"] = bb
        out[gname] = g
    r2res[k] = out
res["r2"] = r2res
L += ["", "## 5. R^2 of log d1 (simple OLS)", "",
      "| run | group | R2 C[0.002,0.585] | R2 log dD(0.585) | both | R2 C[0.14,0.585] | R2 log n0 - C (slope) | "
      "R2(C) - R2(dD) [95% CI] |", "|---|---|---|---|---|---|---|---|"]
for k, o in r2res.items():
    for gname in ("pooled", "on", "off"):
        if gname in o:
            g = o[gname]
            L.append(f"| {k} ({o['dD_source']}) | {gname} | {g['R2_C']:.3f} | {g['R2_logdD']:.3f} | {g['R2_both']:.3f} | "
                     f"{g['R2_C_0.14']:.3f} | {g['R2_logn0-C']:.3f} ({g['slope_logn0-C']}) | "
                     f"{g['boot_C_minus_dD']['diff']:.3f} {g['boot_C_minus_dD']['diff_ci']} |")

# ----------------------------------------------------------------------------- 6. rhoA vs dD/nA in the late window
rr = {}
for k in ("sub2000", "sub500s1", "anchor_sub500"):
    z = Z[k]; i0 = i_near(z["sigma"], 0.585)
    dif = np.abs(z["rhoA"][:, i0:] - z["dD"][:, i0:] / z["nA"][:, i0:])
    bad = (dif > 1e-6).any(1)
    om_pos = (z["omega"][:, i0:] > 0)
    rr[k] = {"median": float(np.median(dif)), "n_samples_gt_1e-6": int(bad.sum()),
             "bad_with_omega_pos_at_same_step": int(((dif > 1e-6) & om_pos).any(1).sum()),
             "bad_steps_without_omega_pos": int(((dif > 1e-6) & ~om_pos).sum())}
res["rhoA_vs_dD_over_nA"] = rr
L += ["", "## 6. abs(rhoA - dD/nA) for sigma <= 0.585", ""] + [f"- {k}: {v}" for k, v in rr.items()]

# ----------------------------------------------------------------------------- 7. claimed vs recomputed
I, C_, LA, HC, D_, R2_ = res["identity"], res["certificate"], res["landing"], res["heun_chain"], res["detector"], res["r2"]
f3 = lambda v: f"{v:.3f}"  # noqa: E731
rows = [
    ("gap median on-atom, 2000 / first 500 / second 500", "-0.031 / -0.043 / -0.039",
     " / ".join(f3(I[k]["gap_med_on"]) for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("actual late contraction median on-atom", "2.08 / 2.94 / 2.89",
     " / ".join(f"{I[k]['act_med_on']:.2f}" for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("gap as share of actual (median of per-sample ratio; ratio of medians)", "1.4-1.6%",
     " / ".join(f"{-100 * I[k]['ratio_med_gap_over_act_on']:.2f}%; {-100 * I[k]['ratio_of_medians_on']:.2f}%"
                for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("gap median off-atom", "-0.024 to -0.025", " / ".join(f3(I[k]["gap_med_off"]) for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("gap median on-atom 18/36/64 steps", "-0.043 / -0.010 / -0.003",
     " / ".join(f3(I[k]["gap_med_on"]) for k in ("s18_sub500", "s36_sub500", "s64_sub500"))),
    ("max abs gap on-atom 18/36/64", "0.722 / 0.134 / 0.026",
     " / ".join(f3(I[k]["max_abs_gap_on"]) for k in ("s18_sub500", "s36_sub500", "s64_sub500"))),
    ("p1-p99 gap on-atom, 2000 / first 500", "[-0.057, -0.023] / [-0.358, -0.019]",
     " / ".join(f"[{I[k]['gap_p01_on']:.3f}, {I[k]['gap_p99_on']:.3f}]" for k in ("sub2000", "s18_sub500"))),
    ("ratio of successive medians 18/36, 36/64", "4.4 / 3.3",
     f"{I['s18_sub500']['gap_med_on'] / I['s36_sub500']['gap_med_on']:.2f} / {I['s36_sub500']['gap_med_on'] / I['s64_sub500']['gap_med_on']:.2f}"),
    ("share of samples with gap < 0", ">= 99%", " / ".join(f"{I[k]['frac_gap_neg_all']:.3f}" for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("max per-interval abs gap above 0.585", "<= 0.016",
     " / ".join(f"{I[k]['max_abs_gap_interval_above_s0']:.4f}" for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("on-atom with rad < 0 in late window (first 500 / second 500 / 2000)", "308/959, 253/956, 3/499",
     ", ".join(f"{I[k]['n_on_negrad_late']}/{I[k]['n_on']}" for k in ("s18_sub500", "sub500s1", "sub2000"))),
    ("median gap, rad<0 vs rest (first 500)", "-0.089 vs -0.033",
     f"{I['s18_sub500']['gap_med_on_negrad']:.3f} vs {I['s18_sub500']['gap_med_on_posrad']:.3f}"),
    ("certificate violations, 18 steps (2000 + first + second 500)", "1/3000, deficit 0.0028 (on-atom, second 500)",
     f"{sum(C_[k]['n_viol'] for k in ('sub2000', 's18_sub500', 'sub500s1'))}/3000, min slack {C_['sub500s1']['min_slack']:.4f}"),
    ("violations 36 / 64 steps; public 200 (no omega) / 500", "0/1000, 0/1000; 0/200, 0/500",
     f"{C_['s36_sub500']['n_viol']}, {C_['s64_sub500']['n_viol']}; {C_['public_rho_noomega']['n_viol']}, {C_['s18_public']['n_viol']}"),
    ("median slack on-atom 2000 / first / second", "0.320 / 0.368 / 0.346",
     " / ".join(f3(C_[k]["slack_med_on"]) for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("median angle term on-atom", "0.351 / 0.411 / 0.388", " / ".join(f3(C_[k]["angle_med_on"]) for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("pointwise min of rho + omega/n - rad (18 steps)", "1.0e-6 to 1.4e-6",
     " / ".join(f"{C_[k]['pointwise_min_all']:.2e}" for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("per-interval violation share, first 500 / 2000 / 36 / 64 (all samples)", "17.3% / 25.3% / 3.2% / 0.1%",
     " / ".join(f"{100 * C_[k]['per_interval_viol_share']:.2f}%" for k in ("s18_sub500", "sub2000", "s36_sub500", "s64_sub500"))),
    ("same, on-atom samples only", "17.3% / 25.3% / 3.2% / 0.1%",
     " / ".join(f"{100 * C_[k]['per_interval_viol_share_on']:.2f}%" for k in ("s18_sub500", "sub2000", "s36_sub500", "s64_sub500"))),
    ("max per-interval deficit", "<= 0.015", " / ".join(f"{C_[k]['per_interval_max_deficit']:.4f}" for k in ("sub2000", "s18_sub500", "sub500s1"))),
    ("start at 0.06: violations 2000 / second 500 (first 500 not reported)", "5 / 7, factor up to 1.020",
     f"{C_['sub2000']['s0_0.06']['n_viol']} / {C_['sub500s1']['s0_0.06']['n_viol']} (first 500: {C_['s18_sub500']['s0_0.06']['n_viol']}), "
     f"factors {C_['sub2000']['s0_0.06']['max_factor']:.4f}, {C_['sub500s1']['s0_0.06']['max_factor']:.4f}, {C_['s18_sub500']['s0_0.06']['max_factor']:.4f}"),
    ("T1 certified on-atom 2000 / second / first (endpoint anchor)", "376/499, 952/956, 956/959",
     f"{LA['sub2000:predictive']['S']['cert_on']}/499, {LA['sub500s1:predictive']['S']['cert_on']}/956, {LA['s18_sub500:endpoint']['S']['cert_on']}/959"),
    ("T1 false certifications", "0/501, 0/44, 0/41; public 0/500 (18, 64)",
     f"{LA['sub2000:predictive']['S']['cert_off']}, {LA['sub500s1:predictive']['S']['cert_off']}, {LA['s18_sub500:endpoint']['S']['cert_off']}; "
     f"{LA['s18_public:endpoint']['S']['cert_off']}, {LA['s64_public:endpoint']['S']['cert_off']}"),
    ("Wilson 95% on-atom", "71.4-78.9, 98.9-99.8, 99.1-99.9",
     f"{LA['sub2000:predictive']['S']['wilson_on']}, {LA['sub500s1:predictive']['S']['wilson_on']}, {LA['s18_sub500:endpoint']['S']['wilson_on']}"),
    ("Wilson upper false-certification rate 2000", "0.76%", f"{100 * LA['sub2000:predictive']['S']['wilson_false_upper']:.2f}%"),
    ("margin B_K/(d2/3): on median 2000 / second; off min", "0.74 / 0.31; 1.28 / 2.08",
     f"{LA['sub2000:predictive']['S']['margin_med_on']:.2f} / {LA['sub500s1:predictive']['S']['margin_med_on']:.2f}; "
     f"{LA['sub2000:predictive']['S']['margin_min_off']:.2f} / {LA['sub500s1:predictive']['S']['margin_min_off']:.2f}"),
    ("T2 (g_a/4)", "134/284, 847/864; false 0/225, 0/38",
     f"{LA['sub2000:predictive']['T2']['cert_on']}/{LA['sub2000:predictive']['T2']['known_on']}, "
     f"{LA['sub500s1:predictive']['T2']['cert_on']}/{LA['sub500s1:predictive']['T2']['known_on']}; false "
     f"{LA['sub2000:predictive']['T2']['cert_off']}/{LA['sub2000:predictive']['T2']['known_off']} (endpoint-anchor lookup "
     f"{LA['sub2000:endpoint']['T2']['cert_off']}/{LA['sub2000:endpoint']['T2']['known_off']}), "
     f"{LA['sub500s1:predictive']['T2']['cert_off']}/{LA['sub500s1:predictive']['T2']['known_off']}"),
    ("S, R, D certify the same samples", "yes",
     f"{LA['sub2000:predictive']['sets_equal_S_R']} {LA['sub2000:predictive']['sets_equal_S_D']} "
     f"{LA['sub500s1:predictive']['sets_equal_S_R']} {LA['sub500s1:predictive']['sets_equal_S_D']}"),
    ("B_K equals err(0.002) e^slack + omega and err(0.002) equals d1", "(not stated)",
     f"max rel dev {LA['sub2000:predictive']['circularity']['max_rel|BK - err_last*e^slack - om|_const']:.1e}; "
     f"median abs(err_last/d1 - 1) {LA['sub2000:predictive']['circularity']['median|err_last/d1 - 1|']:.1e}"),
    ("Heun chain cert, 18 steps (2000 / second / first)", "0/499, 0/956, 2/959",
     f"{HC['sub2000']['cert_on']}/499, {HC['sub500s1']['cert_on']}/956, {HC['s18_sub500']['cert_on']}/959"),
    ("Heun chain cert, 36 / 64 steps; violations", "946/960, 952/961; 0",
     f"{HC['s36_sub500']['cert_on']}/{HC['s36_sub500']['n_on']}, {HC['s64_sub500']['cert_on']}/{HC['s64_sub500']['n_on']}; "
     f"{sum(h['violations'] for h in HC.values())}"),
    ("Heun chain Wilson 36 / 64", "97.6-99.1, 98.2-99.5", f"{HC['s36_sub500']['wilson_on']}, {HC['s64_sub500']['wilson_on']}"),
    ("median log(B_K/n_K) on-atom 2000: chain vs integral", "2.47 vs 0.32",
     f"{HC['sub2000']['median_log_BK_over_nK_on']:.2f} vs {np.log(LA['sub2000:predictive']['circularity']['median_BK_over_d1_on']):.2f}"),
    ("chain per-step bound medians at sigma 0.023, 0.0075", "1.575, 2.265",
     f"{HC['s18_sub500']['per_step_bound_med_on']['0.02293']}, {HC['s18_sub500']['per_step_bound_med_on']['0.007528']}"),
    ("AUC dD(0.585), -C, diff (2000)", "0.990 [0.986,0.994]; 0.983 [0.977,0.988]; 0.007 [0.004,0.010]",
     f"{D_['sub2000']['dD059']}; {D_['sub2000']['negC']}; {D_['sub2000']['dD059-negC']}"),
    ("AUC dD(0.585) - AUC log B_K", "0.006 [0.003, 0.008]", f"{D_['sub2000']['dD059-logBK']}"),
    ("max abs(dD(0.002) - d1); AUC d1", "0; 0.985", f"{D_['sub2000']['max|dD_end-d1|']}; {D_['sub2000']['d1'][0]}"),
    ("oracle dD(0.585) recall at zero FP; naive dD(0.585) < d2/3", "73.9%; 499/499 on, 26/501 off",
     f"{100 * D_['sub2000']['oracle_dD059_recall_at_zeroFP'][2]:.1f}%; {D_['sub2000']['naive_dD059<d2/3']}"),
    ("R2 log dD(0.585), 2000 pooled/on/off", "0.991 / 0.965 / 0.981",
     " / ".join(f3(R2_['sub2000'][g]['R2_logdD']) for g in ("pooled", "on", "off"))),
    ("R2 C, 2000 pooled/on/off", "0.976 / 0.883 / 0.956", " / ".join(f"{R2_['sub2000'][g]['R2_C']:.4f}" for g in ("pooled", "on", "off"))),
    ("R2 on-atom dD vs C: second / first 500", "0.809 vs 0.428; 0.778 vs 0.341",
     f"{R2_['sub500s1']['on']['R2_logdD']:.3f} vs {R2_['sub500s1']['on']['R2_C']:.3f}; "
     f"{R2_['sub500_rho']['on']['R2_logdD']:.3f} vs {R2_['sub500_rho']['on']['R2_C']:.3f}"),
    ("R2 both, 2000 pooled/on/off", "0.992 / 0.967 / 0.990", " / ".join(f3(R2_['sub2000'][g]['R2_both']) for g in ("pooled", "on", "off"))),
    ("boot R2(C)-R2(dD): 2000 pooled/on/off; second on; first on",
     "[-0.017,-0.012] [-0.097,-0.067] [-0.032,-0.019]; [-0.426,-0.338]; [-0.477,-0.395]",
     " ".join(str(R2_['sub2000'][g]['boot_C_minus_dD']['diff_ci']) for g in ("pooled", "on", "off"))
     + f"; {R2_['sub500s1']['on']['boot_C_minus_dD']['diff_ci']}; {R2_['sub500_rho']['on']['boot_C_minus_dD']['diff_ci']}"),
    ("R2 on-atom C over [0.14, 0.585]: 2000 / second / first", "0.949 / 0.784 / 0.713",
     " / ".join(f"{R2_[k]['on']['R2_C_0.14']:.4f}" for k in ("sub2000", "sub500s1", "sub500_rho", "s18_sub500"))),
    ("R2 log n0 - C: 2000 pooled, on (slope); 500 on", "0.990, 0.929 (0.95); 0.53, 0.44",
     f"{R2_['sub2000']['pooled']['R2_logn0-C']:.3f}, {R2_['sub2000']['on']['R2_logn0-C']:.3f} ({R2_['sub2000']['on']['slope_logn0-C']}); "
     f"{R2_['sub500s1']['on']['R2_logn0-C']:.2f}, {R2_['sub500_rho']['on']['R2_logn0-C']:.2f}"),
    ("median abs(rhoA - dD/nA), sigma <= 0.585; samples > 1e-6", "7.8e-16, 7.6e-15; 69, 6",
     f"{rr['sub2000']['median']:.1e}, {rr['sub500s1']['median']:.1e}; {rr['sub2000']['n_samples_gt_1e-6']}, {rr['sub500s1']['n_samples_gt_1e-6']}"),
]
res["claims_table"] = [{"claim": a, "claimed": b, "recomputed": c} for a, b, c in rows]
L += ["", "## 7. Claimed vs recomputed", "", "| claim | claimed | recomputed |", "|---|---|---|"]
L += [f"| {a} | {b} | {c} |" for a, b, c in rows]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "verify_certificate.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
(OUT / "VERIFY_CERTIFICATE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
