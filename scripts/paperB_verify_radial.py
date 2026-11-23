"""Independent verifier for the paper-B "radial" analysis (Theorem relerr (b)/(c) on EDM CIFAR-10 runs).

numpy only; written without reading scripts/paperB_radial.py. Recomputes from the saved per-sample npz files
(18-step EDM Heun sampler, keys defined in scripts/n3_directional_q.py):
  * consistency of the two runs of the first 500-image model (n3_rho vs n3_anchor),
  * the deterministic checks rad1 <= rho + omega/n1, the last Euler step, n1_end = d1, dD(0.002) = d1,
    rad1 = q1 + r1 (only meaningful where q1 was computed),
  * joint behaviour of rho and rad1, the stall level (rad1 >= thr at every remaining level),
  * the discrete delta^+ sum S = sum_{j=11}^{16} (1 - rad1_j)^+ log(sigma_j/sigma_{j+1}) and its AUC,
    the paper's C (trapezoid of 1 - rho), the NN baseline dD, predictive-anchor early sums,
  * realized log-contraction vs the radial identity, finite-window version of (b).
Off-atom: d1/d2 >= 1/3. AUC = P(off > on) + P(tie)/2; contraction scores are negated.
Bootstrap: stratified (on / off resampled separately), percentile 95% interval, paired for differences.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_radial
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

R = pathlib.Path("results")
OUT = R / "paperB_20261121" / "verify_radial"
F = {
    "sub500": R / "n3_rho_20261117/sub500/q_per_sample.npz",
    "public200": R / "n3_rho_20261117/public/q_per_sample.npz",
    "sub2000": R / "n3_rho2_20261118/sub2000/q_per_sample.npz",
    "sub500s1": R / "n3_rho2_20261118/sub500s1/q_per_sample.npz",
    "anc_sub500": R / "n3_anchor_20261117/sub500/q_per_sample.npz",
    "anc_public500": R / "n3_anchor_20261117/public/q_per_sample.npz",
    "s18_sub500": R / "n3_steps_20261117/s18/sub500/q_per_sample.npz",
    "s36_sub500": R / "n3_steps_20261117/s36/sub500/q_per_sample.npz",
    "s64_sub500": R / "n3_steps_20261117/s64/sub500/q_per_sample.npz",
    "s18_public": R / "n3_steps_20261117/s18/public/q_per_sample.npz",
    "s36_public": R / "n3_steps_20261117/s36/public/q_per_sample.npz",
    "s64_public": R / "n3_steps_20261117/s64/public/q_per_sample.npz",
}
OMEGA_RUNS = ["sub2000", "sub500s1", "anc_sub500", "anc_public500", "s18_sub500", "s36_sub500", "s64_sub500",
              "s18_public", "s36_public", "s64_public"]
TRAINED = {"sub500": "sub500", "sub500s1": "sub500s1", "sub2000": "sub2000"}   # rad1/err/n1 source
ANCHOR_SRC = {"sub500": "anc_sub500", "sub500s1": "sub500s1", "sub2000": "sub2000"}  # radA/rhoA/dD source
_cache: dict = {}
res: dict = {}


def load(name):
    if name not in _cache:
        z = np.load(F[name])
        _cache[name] = {k: z[k] for k in z.files}
    return _cache[name]


def src(*names):
    return ", ".join(str(F[n]).replace("\\", "/") for n in names)


def off_atom(z, thr=1 / 3):
    return z["d1"] / z["d2"] >= thr


def late_start(sig, top=0.586):
    return int(np.argmax(sig <= top))          # first level with sigma <= 0.5853 (index 11 for 18 steps)


def rankavg(x):
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x)); r[o] = np.arange(1, len(x) + 1)
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    return (np.bincount(inv, weights=r) / cnt)[inv]


def auc(pos, neg):
    """P(pos > neg) + P(pos = neg)/2."""
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    rk = rankavg(np.concatenate([pos, neg]))
    return float((rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot(scores, off, B=2000, seed=0):
    """AUC (off > on) of each score with stratified bootstrap percentile intervals; paired differences vs the
    first score."""
    rng = np.random.default_rng(seed)
    io, inn = np.flatnonzero(off), np.flatnonzero(~off)
    point = [auc(s[off], s[~off]) for s in scores]
    bs = np.empty((B, len(scores)))
    for b in range(B):
        a = rng.choice(io, len(io)); c = rng.choice(inn, len(inn))
        bs[b] = [auc(s[a], s[c]) for s in scores]
    out = {"auc": point, "ci": [np.percentile(bs[:, k], [2.5, 97.5]).tolist() for k in range(len(scores))]}
    out["diff_vs_first"] = [[point[k] - point[0], *np.percentile(bs[:, k] - bs[:, 0], [2.5, 97.5]).tolist()]
                            for k in range(1, len(scores))]
    return out


def med_iqr(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.median(v)), float(np.percentile(v, 25)), float(np.percentile(v, 75))]


def trap(v, sig, j0, j1):
    """trapezoid of v over levels j0..j1 against d log(1/sigma) (per sample)."""
    dl = np.log(sig[j0:j1] / sig[j0 + 1:j1 + 1])
    return (0.5 * (v[:, j0:j1] + v[:, j0 + 1:j1 + 1]) * dl).sum(1)


def left(v, sig, j0, j1):
    """left-point sum of v_j log(sigma_j/sigma_{j+1}) for j = j0..j1-1."""
    dl = np.log(sig[j0:j1] / sig[j0 + 1:j1 + 1])
    return (v[:, j0:j1] * dl).sum(1)


def stall_index(rad, thr):
    """smallest j with rad[:, k] >= thr for every k >= j; K (len) if rad at the last level is < thr."""
    ok = rad >= thr
    K = rad.shape[1]; js = np.full(len(rad), K)
    for i in range(len(rad)):
        bad = np.flatnonzero(~ok[i])
        js[i] = 0 if len(bad) == 0 else bad[-1] + 1
    return js


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    z0 = load("sub500"); sig = z0["sigma"]
    J0 = late_start(sig); K = len(sig)
    assert J0 == 11 and K == 18
    res["sigma_18"] = sig.tolist()
    lvl = {s: int(np.argmin(np.abs(sig - s))) for s in (1.92, 1.09, 0.585, 0.296, 0.140, 0.060, 0.023, 0.0075, 0.002)}
    res["level_index"] = lvl

    # ---------------------------------------------------------------- A. two runs of the first 500-image model
    za, zb = load("sub500"), load("anc_sub500")
    res["A_same_latents"] = {
        "source": src("sub500", "anc_sub500"),
        "max_abs_dn1_sigma80": float(np.abs(za["n1"][:, 0] - zb["n1"][:, 0]).max()),
        "offatom_labels_identical": bool((off_atom(za) == off_atom(zb)).all()),
        "n_off": [int(off_atom(za).sum()), int(off_atom(zb).sum())],
        "max_abs_drad1": float(np.nanmax(np.abs(za["rad1"] - zb["rad1"]))),
        "max_abs_drho": float(np.nanmax(np.abs(za["err"] / za["n1"] - zb["err"] / zb["n1"]))),
    }

    # ---------------------------------------------------------------- B. rad1 <= rho + omega/n1, last step
    tot = viol = 0; worst = -np.inf; per = {}
    for n in OMEGA_RUNS:
        z = load(n); v = z["rad1"] - z["err"] / z["n1"] - z["omega"] / z["n1"]
        fin = np.isfinite(v); tot += int(fin.sum()); vv = int((v[fin] > 0).sum()); viol += vv
        worst = max(worst, float(np.nanmax(v)))
        per[n] = {"cells": int(fin.sum()), "viol": vv, "max_excess": float(np.nanmax(v))}
    late_on_omega = {}
    for m in ("anc_sub500", "sub500s1", "sub2000"):
        z = load(m); on = ~off_atom(z); om = z["omega"][:, J0:] / z["n1"][:, J0:]
        late_on_omega[m] = {"on_all_exact_zero": bool((om[on] == 0).all()), "on_max": float(om[on].max()),
                            "off_all_exact_zero": bool((om[~on] == 0).all()), "off_max": float(om[~on].max()),
                            "all_levels_on_max_by_sigma": [float(x) for x in (z["omega"] / z["n1"])[on].max(0)]}
    res["B_inequality"] = {"source": src(*OMEGA_RUNS), "cells": tot, "violations": viol, "max_excess": worst,
                           "per_run": per, "late_window_omega_over_n": late_on_omega}
    last = {}
    for n in list(F):
        z = load(n); nK = z["n1"][:, -1]; ratio = z["n1_end"] / nK
        d = {"n1_end_eq_d1_maxabs": float(np.abs(z["n1_end"] - z["d1"]).max()),
             "lower_viol(rad1>n_end/n)": int((z["rad1"][:, -1] > ratio + 1e-12).sum()),
             "lower_max_excess": float((z["rad1"][:, -1] - ratio).max())}
        if "omega" in z:
            ub = z["err"][:, -1] / nK + z["omega"][:, -1] / nK
            d["upper_viol(n_end/n>rho+om/n)"] = int((ratio > ub + 1e-12).sum())
            d["upper_max_excess"] = float((ratio - ub).max())
        if "dD" in z:
            d["dD_last_eq_d1_maxabs"] = float(np.abs(z["dD"][:, -1] - z["d1"]).max())
        last[n] = d
    res["B_last_step"] = last
    # C_omega <= S_signed under several quadrature conventions
    cw = {}
    for n in OMEGA_RUNS:
        z = load(n); sg = z["sigma"]; j0 = late_start(sg); jl = len(sg) - 1
        bnd = 1 - z["err"] / z["n1"] - z["omega"] / z["n1"]; s1 = 1 - z["rad1"]
        cw[n] = {"trap_vs_trap": int((trap(bnd, sg, j0, jl) > trap(s1, sg, j0, jl) + 1e-12).sum()),
                 "left_vs_left": int((left(bnd, sg, j0, jl) > left(s1, sg, j0, jl) + 1e-12).sum()),
                 "Ctrap_vs_Sleft": int((trap(bnd, sg, j0, jl) > left(s1, sg, j0, jl) + 1e-12).sum()),
                 "n": int(len(s1))}
    res["B_Comega_le_Ssigned_violations"] = cw

    # ---------------------------------------------------------------- C. joint behaviour of rho and rad1
    joint = {}; nb = nrhohi = 0; minrad = np.inf; rev = 0
    for m, n in TRAINED.items():
        z = load(n); rho = z["err"] / z["n1"]; rad = z["rad1"]
        hi = rho > 0.95; a = hi & (rad < 0.9); b = (rad > 0.95) & (rho < 0.9)
        joint[m] = {"rho>0.95": int(hi.sum()), "and_rad1<0.9": int(a.sum()),
                    "min_rad1_given_rho>0.95": float(rad[hi].min()), "rad1>0.95_and_rho<0.9": int(b.sum()),
                    "cells_rho>0.95_by_sigma": hi.sum(0).tolist()}
        nb += int(a.sum()); nrhohi += int(hi.sum()); minrad = min(minrad, float(rad[hi].min())); rev += int(b.sum())
    for n in ("public200", "anc_public500"):
        z = load(n); rho = z["err"] / z["n1"]; rad = z["rad1"]; hi = rho > 0.95
        joint[n] = {"rho>0.95": int(hi.sum()), "and_rad1<0.9": int((hi & (rad < 0.9)).sum()),
                    "rad1>0.95_and_rho<0.9": int(((rad > 0.95) & (rho < 0.9)).sum()),
                    "min_rad1_given_rho>0.95": float(rad[hi].min())}
    res["C_joint"] = {"source": src("sub500", "sub500s1", "sub2000", "public200", "anc_public500"),
                      "three_trained_total_rho>0.95": nrhohi, "three_trained_and_rad1<0.9": nb,
                      "three_trained_min_rad1": minrad, "three_trained_rad1>0.95_rho<0.9": rev, "per_model": joint}

    # ---------------------------------------------------------------- D. lag and stall levels
    z = load("sub500"); off = off_atom(z); i = lvl[0.140]; rho = z["err"] / z["n1"]
    res["D_lag_sub500_sigma0.140_off"] = {
        "source": src("sub500"), "n_off": int(off.sum()),
        "share_rho>=0.95": float((rho[off, i] >= 0.95).mean()), "share_rad1>=0.95": float((z["rad1"][off, i] >= 0.95).mean()),
        "rad1_med_iqr": med_iqr(z["rad1"][off, i]), "rho_med_iqr": med_iqr(rho[off, i])}
    stall = {}
    for m, n in TRAINED.items():
        z = load(n); off = off_atom(z); sg = z["sigma"]; d = {}
        for thr in (0.9, 0.95, 0.99):
            js = stall_index(z["rad1"], thr); ssig = np.where(js < K, sg[np.minimum(js, K - 1)], 0.0)
            d[str(thr)] = {
                "off_frac_from_0.060": float((js[off] <= lvl[0.060]).mean()), "off_count_from_0.060": int((js[off] <= lvl[0.060]).sum()),
                "off_frac_from_0.023": float((js[off] <= lvl[0.023]).mean()), "on_frac_from_0.060": float((js[~off] <= lvl[0.060]).mean()),
                "on_frac_from_0.023": float((js[~off] <= lvl[0.023]).mean()),
                "off_median_stall_sigma": float(np.median(ssig[off])), "on_median_stall_sigma": float(np.median(ssig[~off])),
                "on_never_stalled": int((js[~off] == K).sum()), "off_never_stalled": int((js[off] == K).sum())}
        rr = z["rad1"]
        d["on_share_rad1>=0.95_at_0.002"] = float((rr[~off, lvl[0.002]] >= 0.95).mean())
        d["on_share_rad1>=0.95_at_0.0075"] = float((rr[~off, lvl[0.0075]] >= 0.95).mean())
        d["on_median_rad1_at_0.002"] = float(np.median(rr[~off, lvl[0.002]]))
        d["on_median_1-rad1_at_0.023_0.0075_0.002"] = [float(np.median(1 - rr[~off, lvl[s]])) for s in (0.023, 0.0075, 0.002)]
        d["n_on_off"] = [int((~off).sum()), int(off.sum())]
        stall[m] = d
    res["D_stall"] = {"source": src(*TRAINED.values()), "per_model": stall}

    # ---------------------------------------------------------------- E. S, C, NN baseline, trapezoid, anchor
    Sres = {}
    for m, n in TRAINED.items():
        z = load(n); za_ = load(ANCHOR_SRC[m]); off = off_atom(z); sg = z["sigma"]
        rho = z["err"] / z["n1"]; rad = z["rad1"]
        S = left(np.clip(1 - rad, 0, None), sg, J0, K - 1)
        S_tr = trap(np.clip(1 - rad, 0, None), sg, J0, K - 1)
        S_sg = left(1 - rad, sg, J0, K - 1)
        C = trap(1 - rho, sg, J0, K - 1)
        terms = np.clip(1 - rad[:, J0:K - 1], 0, None) * np.log(sg[J0:K - 1] / sg[J0 + 1:K])
        late_part = terms[:, lvl[0.023] - J0:].sum(1)       # j = 15, 16 (sigma 0.023 and 0.0075)
        SA = left(np.clip(1 - za_["radA"], 0, None), sg, J0, K - 1)
        same_anchor = (za_["anc"][:, J0:K].astype(int) == za_["nn1"][:, None]).mean(0)
        sc = [-S, -C, za_["dD"][:, -1], -S_tr, -SA, -S_sg]
        bo = boot(sc, off)
        share = {"median_per_sample_on": float(np.median((late_part / S)[~off])),
                 "median_per_sample_off": float(np.median((late_part / S)[off & (S > 0)])) if (off & (S > 0)).any() else None,
                 "ratio_of_sums_on": float(late_part[~off].sum() / S[~off].sum()),
                 "ratio_of_sums_off": float(late_part[off].sum() / S[off].sum()),
                 "ratio_of_medians_on": float(np.median(late_part[~off]) / np.median(S[~off])),
                 "ratio_of_medians_off": float(np.median(late_part[off]) / np.median(S[off])),
                 "off_with_S_zero": int((off & (S == 0)).sum())}
        Sres[m] = {"source": src(n, ANCHOR_SRC[m]),
                   "S_median_on_off": [float(np.median(S[~off])), float(np.median(S[off]))],
                   "C_median_on_off": [float(np.median(C[~off])), float(np.median(C[off]))],
                   "AUC[S,C,NN(0.002),S_trap,S_A,S_signed]": bo["auc"], "CI": bo["ci"],
                   "diff_vs_S[C,NN,S_trap,S_A,S_signed](point,lo,hi)": bo["diff_vs_first"],
                   "share_of_S_from_sigma<=0.023": share,
                   "anchor_eq_y1_by_late_level": same_anchor.tolist(),
                   "max_abs_S_minus_SA": float(np.abs(S - SA).max()),
                   "frac_S_eq_SA": float(np.isclose(S, SA, rtol=0, atol=1e-12).mean())}
    res["E_S"] = Sres

    # ---------------------------------------------------------------- F. realized contraction vs the radial identity
    real = {}
    for m, n in TRAINED.items():
        z = load(n); off = off_atom(z); sg = z["sigma"]; rad = z["rad1"]
        act = np.log(z["n1"][:, J0] / z["n1"][:, K - 1])
        T = trap(1 - rad, sg, J0, K - 1); Tp = trap(np.clip(1 - rad, 0, None), sg, J0, K - 1)
        C = trap(1 - z["err"] / z["n1"], sg, J0, K - 1)
        per_int = np.log(z["n1"][:, J0:K - 1] / z["n1"][:, J0 + 1:K]) - \
            0.5 * ((1 - rad[:, J0:K - 1]) + (1 - rad[:, J0 + 1:K])) * np.log(sg[J0:K - 1] / sg[J0 + 1:K])
        real[m] = {"source": src(n), "pearson(actual,T)": float(np.corrcoef(act, T)[0, 1]),
                   "median(actual-T)_on_off": [float(np.median((act - T)[~off])), float(np.median((act - T)[off]))],
                   "actual>T_plus_count": int((act > Tp + 1e-12).sum()),
                   "actual_median_on_off": [float(np.median(act[~off])), float(np.median(act[off]))],
                   "C_median_on_off": [float(np.median(C[~off])), float(np.median(C[off]))],
                   "per_interval_median_on(actual-trap)": [float(np.median(per_int[~off, k])) for k in range(K - 1 - J0)],
                   "per_interval_median_off(actual-trap)": [float(np.median(per_int[off, k])) for k in range(K - 1 - J0)]}
    res["F_realized"] = real

    # ---------------------------------------------------------------- G. predictive anchor, early window 0.585 -> 0.140
    pred = {}
    j12 = lvl[0.296]; j13 = lvl[0.140]
    for m in TRAINED:
        z = load(ANCHOR_SRC[m]); zt = load(TRAINED[m]); off = off_atom(zt); sg = z["sigma"]
        assert (off == off_atom(z)).all()
        SAe = left(np.clip(1 - z["radA"], 0, None), sg, J0, j13)                 # uses radA at 0.585, 0.296
        CAe_trap = trap(1 - z["rhoA"], sg, J0, j13)                               # uses rhoA at 0.585, 0.296, 0.140
        CAe_left = left(1 - z["rhoA"], sg, J0, j13)                               # uses rhoA at 0.585, 0.296
        NN296 = z["dD"][:, j12]; NN140 = z["dD"][:, j13]
        bo = boot([-SAe, -CAe_trap, NN296, -CAe_left, NN140, z["rhoA"][:, j12]], off)
        pred[m] = {"source": src(ANCHOR_SRC[m]),
                   "AUC[S_A_early,C_A_early_trap,NN(0.296),C_A_early_left,NN(0.140),rhoA(0.296)]": bo["auc"],
                   "CI": bo["ci"], "diff_vs_S_A_early(point,lo,hi)": bo["diff_vs_first"]}
    res["G_predictive"] = pred

    # ---------------------------------------------------------------- H. finite-window (b)
    fb = {}
    for m, n in TRAINED.items():
        z = load(n); off = off_atom(z); rho = z["err"] / z["n1"]
        w1 = (rho[:, J0:lvl[0.023] + 1] < 0.9).all(1); w2 = (rho[:, J0:K] < 0.9).all(1); w3 = (rho[:, J0:K] < 1).all(1)
        fb[m] = {"source": src(n), "rho<0.9_all_in_[0.023,0.585]_on_off": [float(w1[~off].mean()), float(w1[off].mean())],
                 "rho<0.9_all_in_[0.002,0.585]_on_off": [float(w2[~off].mean()), float(w2[off].mean())],
                 "rho<1_all_late_on_off": [float(w3[~off].mean()), float(w3[off].mean())],
                 "on_median_rho_0.002": float(np.median(rho[~off, -1])), "n_on_off": [int((~off).sum()), int(off.sum())]}
    res["H_finite_b"] = fb

    # ---------------------------------------------------------------- I. identity rad1 = q1 + r1
    ident = {}
    for n in ("sub500", "public200", "sub2000", "sub500s1"):
        z = load(n)
        if not np.isfinite(z["q1"]).any():
            ident[n] = {"q1_all_nan": True}; continue
        dev = z["rad1"] - z["q1"] - z["r1"]; ad = np.abs(dev)
        k = np.unravel_index(np.nanargmax(ad), ad.shape)
        medl = np.nanmedian(ad, 0)
        ident[n] = {"source": src(n), "max_abs": float(ad[k]), "argmax_sigma": float(sig[k[1]]),
                    "median_abs_by_sigma": medl.tolist(),
                    "median_signed_by_sigma": np.nanmedian(dev, 0).tolist(),
                    "frac_abs>0.05_at_0.585_0.296_0.140": [float((ad[:, lvl[s]] > 0.05).mean()) for s in (0.585, 0.296, 0.140)],
                    "max_median_abs_sigma>=1.92": float(medl[:lvl[1.92] + 1].max()),
                    "max_median_abs_sigma<=0.023": float(medl[lvl[0.023]:].max()),
                    "max_median_abs_all": float(medl.max()),
                    "median_qx1_at_0.585_0.296_0.140": [float(np.nanmedian(z["qx1"][:, lvl[s]])) for s in (0.585, 0.296, 0.140)],
                    "median_rad1-r1_at_0.585_0.296_0.140": [float(np.nanmedian((z["rad1"] - z["r1"])[:, lvl[s]])) for s in (0.585, 0.296, 0.140)],
                    "median_q1_at_0.585_0.296_0.140": [float(np.nanmedian(z["q1"][:, lvl[s]])) for s in (0.585, 0.296, 0.140)]}
        if n == "sub500":
            off = off_atom(z)
            ident[n]["by_group_median_qx1_on_off"] = [[float(np.median(z["qx1"][~off, lvl[s]])), float(np.median(z["qx1"][off, lvl[s]]))]
                                                      for s in (0.585, 0.296, 0.140)]
            ident[n]["by_group_median_rad1-r1_on_off"] = [[float(np.median((z["rad1"] - z["r1"])[~off, lvl[s]])),
                                                           float(np.median((z["rad1"] - z["r1"])[off, lvl[s]]))] for s in (0.585, 0.296, 0.140)]
    res["I_identity"] = ident

    # ---------------------------------------------------------------- J. cosine rad1/rho and endpoint distances
    z = load("sub500"); off = off_atom(z); rho = z["err"] / z["n1"]; c = z["rad1"] / rho
    res["J_cosine_sub500"] = {"source": src("sub500"),
                              "median_rad1/rho_on_at_0.585_0.296_0.140_0.060": [float(np.median(c[~off, lvl[s]])) for s in (0.585, 0.296, 0.140, 0.060)],
                              "median_rad1/rho_off": [float(np.median(c[off, lvl[s]])) for s in (0.585, 0.296, 0.140, 0.060)],
                              "d1_on_med_iqr": med_iqr(z["d1"][~off]), "d1_off_med_iqr": med_iqr(z["d1"][off]),
                              "d1/d2_med_on_off": [float(np.median((z["d1"] / z["d2"])[~off])), float(np.median((z["d1"] / z["d2"])[off]))]}

    # ---------------------------------------------------------------- K. table tab:edm-rho and paper C AUC CI (data sanity)
    tab = {}
    for n in ("sub500", "sub2000", "public200"):
        z = load(n); off = off_atom(z); rho = z["err"] / z["n1"]
        tab[n] = {"on": [float(np.median(rho[~off, lvl[s]])) if (~off).any() else None for s in (1.92, 0.585, 0.140, 0.023, 0.002)],
                  "off": [float(np.median(rho[off, lvl[s]])) for s in (1.92, 0.585, 0.140, 0.023, 0.002)]}
        if (~off).any():
            tab[n]["auc"] = [auc(rho[off, lvl[s]], rho[~off, lvl[s]]) for s in (1.92, 0.585, 0.140, 0.023, 0.002)]
    res["K_table_edm_rho"] = tab

    # ---------------------------------------------------------------- L. robustness: steps and off-atom threshold
    rob = {}
    for n in ("s18_sub500", "s36_sub500", "s64_sub500"):
        z = load(n); sg = z["sigma"]; j0 = late_start(sg); off = off_atom(z)
        S = left(np.clip(1 - z["rad1"], 0, None), sg, j0, len(sg) - 1)
        C = trap(1 - z["err"] / z["n1"], sg, j0, len(sg) - 1)
        rob[n] = {"j0_sigma": float(sg[j0]), "n_off": int(off.sum()), "AUC_S": auc(-S[off], -S[~off]), "AUC_C": auc(-C[off], -C[~off]),
                  "S_med_on_off": [float(np.median(S[~off])), float(np.median(S[off]))]}
    for m, n in TRAINED.items():
        z = load(n); sg = z["sigma"]; S = left(np.clip(1 - z["rad1"], 0, None), sg, J0, K - 1)
        for thr in (0.2, 0.5):
            off = off_atom(z, thr); rob[f"{m}_thr{thr}"] = {"n_off": int(off.sum()), "AUC_S": auc(-S[off], -S[~off])}
    res["L_robustness"] = rob

    # bootstrap Monte Carlo spread of the sub2000 S interval (seed dependence)
    z = load("sub2000"); off = off_atom(z)
    S = left(np.clip(1 - z["rad1"], 0, None), z["sigma"], J0, K - 1)
    res["M_bootstrap_seed_spread_sub2000_S"] = [boot([-S], off, B=2000, seed=s)["ci"][0] for s in (1, 2, 3)]

    # ---------------------------------------------------------------- N. extra methodology probes
    ex = {}
    p2, p5 = load("public200"), load("anc_public500")
    ex["public_runs_shared_trajectories(n1 at sigma=80 equal)"] = int(len(np.intersect1d(np.round(p2["n1"][:, 0], 9),
                                                                                         np.round(p5["n1"][:, 0], 9))))
    ex["public_pooled_rho>0.95_cells"] = int(((p2["err"] / p2["n1"]) > 0.95).sum() + ((p5["err"] / p5["n1"]) > 0.95).sum())
    anc_detail, om_off, lag, s_book, c_real = {}, {}, {}, {}, {}
    for m in TRAINED:
        z = load(ANCHOR_SRC[m]); off = off_atom(z); eq = z["anc"].astype(int) == z["nn1"][:, None]
        anc_detail[m] = {"all_late": eq[:, J0:].mean(0).tolist(), "off_late": eq[off][:, J0:].mean(0).tolist(),
                         "joint_all_late_levels": float(eq[:, J0:].all(1).mean())}
        om = z["omega"] / z["n1"]
        om_off[m] = {"off_frac_samples_any_late_omega/n>1e-3": float((om[off][:, J0:] > 1e-3).any(1).mean()),
                     "off_frac_by_late_sigma": (om[off][:, J0:] > 1e-3).mean(0).tolist()}
        zt = load(TRAINED[m]); off = off_atom(zt); rho = zt["err"] / zt["n1"]; d = {}
        for key, v in (("rho", rho), ("rad1", zt["rad1"])):
            js = stall_index(v, 0.95); ss = np.where(js < K, sig[np.minimum(js, K - 1)], 0.0)
            d[key] = [float(np.median(ss[off])), float(np.median(ss[~off]))]
        lag[m] = d
        S = left(np.clip(1 - zt["rad1"], 0, None), sig, J0, K - 1)
        act = np.log(zt["n1"][:, J0] / zt["n1"][:, K - 1]); C = trap(1 - rho, sig, J0, K - 1)
        s_book[m] = {"corr(S,-log d1)": float(np.corrcoef(S, -np.log(zt["d1"]))[0, 1]),
                     "AUC_d1": auc(zt["d1"][off], zt["d1"][~off]), "AUC_S": auc(-S[off], -S[~off]),
                     "sd_log_n1(0.585)": float(np.log(zt["n1"][:, J0]).std()), "sd_log_d1": float(np.log(zt["d1"]).std())}
        c_real[m] = {"C>realized_count": int((C > act).sum()), "max(C-realized)": float((C - act).max())}
    ex["anchor_eq_y1"] = anc_detail; ex["offatom_late_omega"] = om_off
    ex["median_stall_sigma_thr0.95_[off,on]"] = lag; ex["S_vs_endpoint_distance"] = s_book; ex["C_vs_realized"] = c_real
    z = load("sub500"); off = off_atom(z); dev = z["rad1"] - z["q1"] - z["r1"]
    ex["identity_sign_sub500"] = {f"{sig[j]:.4g}": {"on_frac_dev<0": float((dev[~off, j] < 0).mean()),
                                                     "off_frac_dev<0": float((dev[off, j] < 0).mean()),
                                                     "on_median_q1": float(np.median(z["q1"][~off, j])),
                                                     "on_median_rad1-r1": float(np.median((z["rad1"] - z["r1"])[~off, j])),
                                                     "on_median_qx1": float(np.median(z["qx1"][~off, j]))} for j in range(9, K)}
    z = load("sub2000"); off = off_atom(z); win = {}
    for j0, j1 in ((11, 13), (10, 13), (11, 12), (9, 13)):
        SA = left(np.clip(1 - z["radA"], 0, None), sig, j0, j1); CA = left(1 - z["rhoA"], sig, j0, j1)
        bo = boot([-SA, -CA, z["dD"][:, j1 - 1]], off, B=2000)
        win[f"{sig[j0]:.3f}->{sig[j1]:.3f}"] = {"AUC[S_A,C_A,NN(last level used)]": bo["auc"], "CI": bo["ci"],
                                                 "diff_vs_S_A": bo["diff_vs_first"]}
    ex["predictive_windows_sub2000"] = win
    steps = {}
    for n in ("s18_sub500", "s36_sub500", "s64_sub500"):
        z = load(n); sg = z["sigma"]; j0 = late_start(sg); off = off_atom(z); u = np.clip(1 - z["rad1"], 0, None)
        steps[n] = {"S_left_med_on_off": [float(np.median(left(u, sg, j0, len(sg) - 1)[~off])), float(np.median(left(u, sg, j0, len(sg) - 1)[off]))],
                    "S_trap_med_on_off": [float(np.median(trap(u, sg, j0, len(sg) - 1)[~off])), float(np.median(trap(u, sg, j0, len(sg) - 1)[off]))]}
    ex["step_count_S_left_vs_trap"] = steps
    res["N_extra"] = ex

    (OUT / "verify_radial.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
