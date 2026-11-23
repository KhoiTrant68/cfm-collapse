"""Off-atom thresholds for the comparison of Section sec:contraction ("Not a better detector").

Compares, on the trained EDM models, the baseline at sigma = 0.585 (distance dD from the denoiser
output to its nearest training image) with the late contraction C = int_{0.002}^{0.585} (1 - rho)
d log(1/sigma) (trapezoidal rule, endpoint anchor; Cpred: predictive anchor), at the off-atom
thresholds d1/d2 >= 1/3 (the paper's), 0.2 and 0.5:
  * AUC for telling off- from on-atom samples (dD at every sigma, -C, -Cpred, d1),
  * stratified bootstrap intervals (resampling off- and on-atom samples separately; the same
    resamples for every score, so differences are paired) and DeLong intervals for the differences,
  * R^2 of a linear fit of log d1 on log dD(sigma) and on C, pooled and within the on- and off-atom
    groups of each threshold.

This is the independent check of the memo verification (item 1.3) moved into the repository: the
computation, the bootstrap seeds and the resample counts are those of that check, so the AUC and
bootstrap entries reproduce it; the R^2 by threshold is added. numpy only.

    python scripts/threshold_auc_r2.py            # writes results/threshold_auc_r2_20261121/
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results")
OUT = os.path.join(R, "threshold_auc_r2_20261121")
FILES = {"sub2000": os.path.join(R, "n3_rho2_20261118", "sub2000", "q_per_sample.npz"),
         "sub500s1": os.path.join(R, "n3_rho2_20261118", "sub500s1", "q_per_sample.npz"),
         "sub500": os.path.join(R, "n3_anchor_20261117", "sub500", "q_per_sample.npz")}
THRESHOLDS = (1 / 3, 0.2, 0.5)


def auc(s, y):
    """Mann-Whitney AUC with mid-ranks: P(score of an off-atom sample > score of an on-atom one)."""
    s = np.asarray(s, float); y = np.asarray(y, bool)
    o = np.argsort(s, kind="mergesort"); ss = s[o]
    brk = np.flatnonzero(np.diff(ss) != 0) + 1
    st = np.r_[0, brk]; en = np.r_[brk, len(ss)]
    r = np.empty(len(s)); r[o] = np.repeat((st + en + 1) / 2.0, en - st)
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def boot_idx(y, B, seed):
    rng = np.random.default_rng(seed)
    ip, ineg = np.flatnonzero(y), np.flatnonzero(~y)
    for _ in range(B):
        yield np.r_[rng.choice(ip, len(ip)), rng.choice(ineg, len(ineg))]


def boot_aucs(scores, y, B, seed):
    """scores: dict name -> array; returns dict name -> (B,) bootstrap AUCs (same resamples for all)."""
    out = {k: np.empty(B) for k in scores}
    for b, idx in enumerate(boot_idx(y, B, seed)):
        yy = y[idx]
        for k, s in scores.items():
            out[k][b] = auc(s[idx], yy)
    return out


def delong(scores, y):
    """DeLong (1988) AUCs and covariance for a list of scores (positives = y True)."""
    pos, neg = np.flatnonzero(y), np.flatnonzero(~y)
    V10, V01, A = [], [], []
    for s in scores:
        sp, sn = s[pos][:, None], s[neg][None, :]
        psi = (sp > sn) + 0.5 * (sp == sn)
        V10.append(psi.mean(1)); V01.append(psi.mean(0)); A.append(psi.mean())
    V10, V01 = np.array(V10), np.array(V01)
    S = np.atleast_2d(np.cov(V10)) / len(pos) + np.atleast_2d(np.cov(V01)) / len(neg)
    return np.array(A), S


def pct(a):
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def r2(x, t):
    return float(np.corrcoef(x, t)[0, 1] ** 2)


def trapC(rho, sig, j0):
    inc = 0.5 * ((1 - rho[:, :-1]) + (1 - rho[:, 1:])) * np.log(sig[:-1] / sig[1:])
    return inc[:, j0:].sum(1)


def r2_block(L, dD, C, Cp, sig, m):
    return {**{f"logdD{sig[i]:.4g}": r2(np.log(dD[m, i]), L[m]) for i in range(len(sig))},
            "C": r2(C[m], L[m]), "Cpred": r2(Cp[m], L[m]),
            "logC": r2(np.log(np.clip(C[m], 1e-12, None)), L[m]) if (C[m] > 0).all() else None,
            "n": int(m.sum())}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for name, f in FILES.items():
        z = np.load(f)
        sig = z["sigma"]; d1, d2 = z["d1"], z["d2"]; dD = z["dD"]
        j0 = int(np.argmin(np.abs(np.log(sig) - np.log(0.585))))
        C = trapC(z["err"] / z["n1"], sig, j0)                    # endpoint anchor, 0.585 -> 0.002
        Cp = trapC(z["rhoA"], sig, j0)                            # predictive anchor
        r = {"source": os.path.relpath(f, ROOT).replace(os.sep, "/"), "j0": j0, "sigma_j0": float(sig[j0]),
             "n": int(len(d1)), "max_abs_dD_last_minus_d1": float(np.abs(dD[:, -1] - d1).max()),
             "n_exact_equal": int((dD[:, -1] == d1).sum()), "sigma": [float(s) for s in sig]}
        for thr in THRESHOLDS:
            y = (d1 / d2) >= thr
            key = f"thr{thr:.3g}"
            rr = {"n_off": int(y.sum())}
            rr["auc_dD"] = {f"{sig[i]:.4g}": auc(dD[:, i], y) for i in range(len(sig))}
            rr["auc_minus_C"] = auc(-C, y); rr["auc_minus_Cpred"] = auc(-Cp, y); rr["auc_d1"] = auc(d1, y)
            if 0 < y.sum() < len(y):
                idx = {s: int(np.argmin(np.abs(sig - s))) for s in (3.257, 1.923, 1.088, 0.5853, 0.2964, 0.002)}
                sc = {f"dD{s}": dD[:, i] for s, i in idx.items()}
                sc["-C"] = -C; sc["-Cpred"] = -Cp
                for B, seed in ((2000, 0), (2000, 1), (2000, 2), (10000, 3)):
                    bb = boot_aucs(sc, y, B, seed)
                    rr[f"boot_B{B}_seed{seed}"] = {
                        **{f"auc_{k}": pct(v) for k, v in bb.items()},
                        "diff_dD0.5853_minus_C": pct(bb["dD0.5853"] - bb["-C"]),
                        "diff_dD1.088_minus_C": pct(bb["dD1.088"] - bb["-C"]),
                        "diff_dD0.2964_minus_C": pct(bb["dD0.2964"] - bb["-C"]),
                        "diff_C_minus_dD0.002": pct(bb["-C"] - bb["dD0.002"]),
                        "diff_dD0.5853_minus_Cpred": pct(bb["dD0.5853"] - bb["-Cpred"])}
                A, S = delong([dD[:, idx[0.5853]], -C, dD[:, idx[0.002]]], y)
                se01 = float(np.sqrt(S[0, 0] + S[1, 1] - 2 * S[0, 1]))
                se21 = float(np.sqrt(S[1, 1] + S[2, 2] - 2 * S[1, 2]))
                rr["delong"] = {"auc_dD0.5853": float(A[0]), "auc_-C": float(A[1]), "auc_dD0.002": float(A[2]),
                                "diff_dD0.5853_minus_C": [float(A[0] - A[1]), float(A[0] - A[1] - 1.959964 * se01),
                                                          float(A[0] - A[1] + 1.959964 * se01)],
                                "diff_C_minus_dD0.002": [float(A[1] - A[2]), float(A[1] - A[2] - 1.959964 * se21),
                                                         float(A[1] - A[2] + 1.959964 * se21)]}
            r[key] = rr
        # R^2 of log d1 (endpoint distance) on single predictors: pooled, and within the on- and off-atom
        # groups of each threshold ("R2_logd1" keeps the groups of the paper's threshold 1/3).
        L = np.log(d1)
        R2 = {"all": r2_block(L, dD, C, Cp, sig, np.ones(len(d1), bool))}
        for thr in THRESHOLDS:
            y = (d1 / d2) >= thr
            for g, m in (("on", ~y), ("off", y)):
                if m.sum() >= 3:
                    R2[f"{g}_thr{thr:.3g}"] = r2_block(L, dD, C, Cp, sig, m)
        r["R2_logd1_by_threshold"] = R2
        y = (d1 / d2) >= 1 / 3
        r["R2_logd1"] = {"all": R2["all"], "on": R2["on_thr0.333"], **({"off": R2["off_thr0.333"]} if "off_thr0.333" in R2 else {})}
        r["C_median_on"] = float(np.median(C[~y])); r["C_median_off"] = float(np.median(C[y]))
        r["C_min"] = float(C.min())
        res[name] = r

    with open(os.path.join(OUT, "threshold_auc_r2.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for name, r in res.items():
        print("=====", name, "n", r["n"], "j0", r["j0"], "sigma_j0", r["sigma_j0"], "source", r["source"])
        print("  max|dD(0.002) - d1| =", r["max_abs_dD_last_minus_d1"], " exactly equal:", r["n_exact_equal"])
        print("  C medians on/off %.4f / %.4f   min C %.4f" % (r["C_median_on"], r["C_median_off"], r["C_min"]))
        for thr in THRESHOLDS:
            key = f"thr{thr:.3g}"
            rr = r[key]
            print("  --", key, "n_off", rr["n_off"])
            print("     AUC dD by sigma:", {k: round(v, 4) for k, v in rr["auc_dD"].items()})
            print("     AUC -C %.4f  -Cpred %.4f  d1 %.4f" % (rr["auc_minus_C"], rr["auc_minus_Cpred"], rr["auc_d1"]))
            for k, v in rr.items():
                if k.startswith("boot") or k == "delong":
                    print("    ", k, json.dumps({a: ([round(x, 4) for x in b] if isinstance(b, list) else round(b, 4))
                                                 for a, b in v.items()}))
        for g, d in r["R2_logd1_by_threshold"].items():
            print("  R2 log d1 [%s n=%d]: logdD0.5853 %.4f  logdD1.088 %.4f  C %.4f  Cpred %.4f"
                  % (g, d["n"], d["logdD0.5853"], d["logdD1.088"], d["C"], d["Cpred"]))


if __name__ == "__main__":
    main()
