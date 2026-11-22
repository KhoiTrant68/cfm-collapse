"""Independent verifier for the paper-B analysis "incremental" (numpy only; shares no code with
scripts/paperB_incremental.py, which was not read).

Question checked: does the field-error / late-contraction signal (predictive anchor keys rhoA, radA, C) add
information beyond the nearest-neighbour baseline log dD for predicting the off-atom label d1/d2 >= 1/3?

Recomputed from the saved per-sample data:
  * off-atom counts, sigma grid, window indices (nearest grid values to 5.3, 1.9, 0.585 and 0.06);
  * endpoint-information checks: the last Heun step of the 18-step EDM sampler is an Euler step to sigma = 0,
    so the endpoint equals D(x_17) and dD[:, 17] should equal the endpoint distance d1;
  * raw single-feature AUCs (fixed orientation: larger dD/rhoA/radA, smaller C = off-atom) and bootstrap CIs;
  * in-sample ML likelihood-ratio tests (1 df), Firth penalised LR where the MLE does not exist,
    Holm over the 69 field-error tests (rhoA 18, radA 18, C 24, truncated C 9);
  * 10-fold stratified CV x 20 repeats (own fold seeds), pooled out-of-fold AUC, Delta AUC with a paired
    class-stratified bootstrap of the stored out-of-fold predictions (B = 2000, repeats averaged per resample);
  * refit (out-of-bag) check for the headline rows, NN-distance history control, class-adjusted Firth check,
    class off-rate CV AUC, quadratic baseline for radA / rhoA;
and compares every number with results/paperB_20261121/incremental/incremental.json.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_incremental              # full run (~5 min)
    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_incremental --headline   # headline table only
"""
from __future__ import annotations

import json
import math
import pathlib
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = {"sub2000": ROOT / "results/n3_rho2_20261118/sub2000/q_per_sample.npz",
         "sub500s1": ROOT / "results/n3_rho2_20261118/sub500s1/q_per_sample.npz"}
REPORTED = ROOT / "results/paperB_20261121/incremental/incremental.json"
OUT = ROOT / "results/paperB_20261121/verify_incremental"
RATIO = 1.0 / 3.0
SEED = 9_731_552                     # deliberately different from the analysed run's seed
NREP, NFOLD, NBOOT, NREFIT = 20, 10, 2000, 500
RIDGE = 1e-4
WSTART = {"C5.3": 5.3, "C1.9": 1.9, "C0.585": 0.585}
TRUNC = 0.06


# ----------------------------------------------------------------------------------------------- basic tools
def expit(e):
    return 0.5 * (1.0 + np.tanh(0.5 * e))


def auc(s, y):
    """P(score_off > score_on) + ties/2 via average ranks; y boolean (True = off-atom)."""
    s = np.asarray(s, float); y = np.asarray(y, bool)
    o = np.argsort(s, kind="mergesort"); ss = s[o]
    brk = np.flatnonzero(np.diff(ss) != 0) + 1
    st = np.r_[0, brk]; en = np.r_[brk, len(ss)]
    r = np.empty(len(s)); r[o] = np.repeat((st + en + 1) / 2.0, en - st)
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def wauc(s, yf, W):
    """AUC under integer resampling weights W (B, n); ties count 1/2. yf: float 0/1 labels.
    W is float32: all partial sums are integers (or halves) below 2^24, hence exact."""
    o = np.argsort(s, kind="mergesort"); ss = s[o]
    st = np.r_[0, np.flatnonzero(np.diff(ss) != 0) + 1]
    Wo = W[:, o]; yo = yf[o].astype(W.dtype)
    if len(st) == len(ss):                       # no ties: positives see the negatives strictly below
        pos = yo > 0.5
        N = Wo * (1 - yo)
        cN = np.cumsum(N, axis=1)
        num = (Wo[:, pos] * cN[:, pos]).sum(1, dtype=np.float64)
        return num / (Wo[:, pos].sum(1, dtype=np.float64) * cN[:, -1].astype(np.float64))
    P = np.add.reduceat(Wo * yo, st, axis=1)
    N = np.add.reduceat(Wo * (1 - yo), st, axis=1)
    below = np.cumsum(N, axis=1) - N
    return ((P * (below + 0.5 * N)).sum(1, dtype=np.float64)
            / (P.sum(1, dtype=np.float64) * N.sum(1, dtype=np.float64)))


def strat_weights(y, B, rng):
    n = len(y); flat = np.zeros(B * n)
    for cls in (False, True):
        idx = np.flatnonzero(y == cls)
        draw = idx[rng.integers(0, len(idx), size=(B, len(idx)))]
        flat += np.bincount((np.arange(B)[:, None] * n + draw).ravel(), minlength=B * n)
    return flat.reshape(B, n).astype(np.float32)


def fit_ml(X, y, ridge=0.0, c=None, maxit=100):
    """Newton-Raphson logistic regression; ridge on slopes (not intercept); optional case weights c."""
    n, p = X.shape
    cw = np.ones(n) if c is None else c
    P = np.full(p, ridge); P[0] = 0.0
    b = np.zeros(p)

    def obj(bb):
        eta = X @ bb
        return float((cw * (y * eta - np.logaddexp(0.0, eta))).sum() - 0.5 * (P * bb * bb).sum())
    f = obj(b)
    for _ in range(maxit):
        mu = expit(X @ b); w = cw * mu * (1.0 - mu)
        g = X.T @ (cw * (y - mu)) - P * b
        H = (X.T * w) @ X + np.diag(P)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        t = 1.0
        while True:
            bn = b + t * step; fn = obj(bn)
            if fn >= f - 1e-10 or t < 1e-6:
                break
            t *= 0.5
        small = np.max(np.abs(bn - b)) < 1e-9 or abs(fn - f) < 1e-12 * max(1.0, abs(f))
        b, f = bn, fn
        if small:
            break
    return b, f


def fit_firth(X, y, free=None, maxit=300):
    """Firth-penalised logistic regression, l(b) + 0.5 log det I(b). 'free' marks estimated coefficients
    (the others stay 0) while the penalty always uses the full X (profile penalised likelihood)."""
    n, p = X.shape
    free = np.ones(p, bool) if free is None else free
    b = np.zeros(p)

    def pobj(bb):
        eta = X @ bb; mu = expit(eta); w = mu * (1.0 - mu)
        _, ld = np.linalg.slogdet((X.T * w) @ X)
        return float((y * eta - np.logaddexp(0.0, eta)).sum() + 0.5 * ld)
    f = pobj(b)
    for _ in range(maxit):
        eta = X @ b; mu = expit(eta); w = mu * (1.0 - mu)
        I = (X.T * w) @ X
        Iinv = np.linalg.inv(I)
        h = w * np.einsum("ij,jk,ik->i", X, Iinv, X)
        U = X.T @ (y - mu + h * (0.5 - mu))
        step = np.zeros(p)
        step[free] = np.linalg.solve(I[np.ix_(free, free)], U[free])
        t = 1.0
        while True:
            bn = b + t * step; fn = pobj(bn)
            if fn >= f - 1e-10 or t < 1e-6:
                break
            t *= 0.5
        small = np.max(np.abs(bn - b)) < 1e-10
        b, f = bn, fn
        if small:
            break
    return b, f


def design(F, mu=None, sd=None):
    F = np.atleast_2d(F.T).T if F.ndim == 1 else F
    mu = F.mean(0) if mu is None else mu
    sd = F.std(0) if sd is None else sd
    sd = np.where(sd > 0, sd, 1.0)
    return np.column_stack([np.ones(len(F)), (F - mu) / sd]), mu, sd


def chi2_sf1(x):
    return math.erfc(math.sqrt(max(x, 0.0) / 2.0))


def separated(X, y, b):
    eta = X @ b
    return bool(eta[y > 0.5].min() > eta[y < 0.5].max() or eta[y > 0.5].max() < eta[y < 0.5].min())


def lr_test(Fb, Ff, yf):
    """In-sample ML LR (1 df); Firth profile penalised LR when either MLE does not exist."""
    Xb, _, _ = design(Fb); Xf, _, _ = design(Ff)
    bb, lb = fit_ml(Xb, yf); bf, lf = fit_ml(Xf, yf)
    sep = separated(Xb, yf, bb) or separated(Xf, yf, bf) or max(lb, lf) > -1e-3
    out = {"ml_chi2": 2 * (lf - lb), "separation": sep}
    out["ml_p"] = chi2_sf1(out["ml_chi2"])
    _, pf = fit_firth(Xf, yf)
    free = np.ones(Xf.shape[1], bool); free[-1] = False
    _, pr = fit_firth(Xf, yf, free=free)
    _, pb = fit_firth(Xb, yf)
    out["firth_profile_chi2"] = 2 * (pf - pr)
    out["firth_separate_chi2"] = 2 * (pf - pb)
    out["p_primary"] = chi2_sf1(out["firth_profile_chi2"]) if sep else out["ml_p"]
    return out


def holm(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p, kind="mergesort")
    adj = np.maximum.accumulate(np.minimum(1.0, (m - np.arange(m)) * p[o]))
    out = np.empty(m); out[o] = adj
    return out


def make_folds(y, rep):
    rng = np.random.default_rng([SEED, rep])
    f = np.empty(len(y), int)
    for cls in (False, True):
        idx = rng.permutation(np.flatnonzero(y == cls))
        f[idx] = np.arange(len(idx)) % NFOLD
    return f


def cv_oof(F, yf, folds):
    """Out-of-fold linear predictors (NREP, n); standardisation from the training folds only."""
    F = F.reshape(len(yf), -1)
    out = np.empty((len(folds), len(yf)))
    for r, fo in enumerate(folds):
        for g in range(NFOLD):
            te = fo == g; tr = ~te
            Xtr, mu, sd = design(F[tr]); Xte, _, _ = design(F[te], mu, sd)
            b, _ = fit_ml(Xtr, yf[tr], ridge=RIDGE, maxit=60)
            out[r, te] = Xte @ b
    return out


def refit_oob(Fb, Ff, y, Wr):
    yf = y.astype(float); d = []
    Xb, _, _ = design(Fb.reshape(len(y), -1)); Xf, _, _ = design(Ff.reshape(len(y), -1))
    for c in Wr:
        oob = c == 0
        if y[oob].all() or not y[oob].any():
            continue
        a = []
        for X in (Xb, Xf):
            b, _ = fit_ml(X[~oob], yf[~oob], ridge=RIDGE, c=c[~oob], maxit=60)
            a.append(auc(X[oob] @ b, y[oob]))
        d.append(a[1] - a[0])
    d = np.asarray(d)
    return {"mean": float(d.mean()), "lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5)),
            "draws": int(len(d))}


# ----------------------------------------------------------------------------------------------- per model
def analyse(name, z, rep_model, do_hist=True, do_refit_rows=(), class_rows=()):
    t0 = time.time()
    sig = z["sigma"]; S = len(sig)
    d1, d2 = z["d1"], z["d2"]
    y = d1 / d2 >= RATIO; yf = y.astype(float)
    L = np.log(z["dD"]); rhoA = z["rhoA"]; radA = z["radA"]
    res = {"n": int(len(y)), "n_off": int(y.sum()), "n_off_key_label_nonzero": int((z["label"] != 0).sum()),
           "sigma": sig.tolist()}

    # windows: nearest grid value (log scale and linear scale give the same index here)
    j0 = {k: int(np.argmin(np.abs(np.log(sig) - np.log(v)))) for k, v in WSTART.items()}
    j0_lin = {k: int(np.argmin(np.abs(sig - v))) for k, v in WSTART.items()}
    jt = int(np.argmin(np.abs(np.log(sig) - np.log(TRUNC))))
    res["window_index"] = j0; res["window_index_linear"] = j0_lin; res["trunc_index"] = jt
    res["window_sigma"] = {k: float(sig[v]) for k, v in j0.items()}

    # ---- endpoint-information checks
    n1 = z["n1"]; nn1 = z["nn1"]; anc = z["anc"]; nA = z["nA"]; err = z["err"]
    leak = {"max_abs_dD17_minus_d1": float(np.abs(z["dD"][:, -1] - d1).max()),
            "max_rel_dD17_minus_d1": float((np.abs(z["dD"][:, -1] - d1) / d1).max()),
            "frac_anc17_eq_nn1": float((anc[:, -1].astype(int) == nn1).mean()),
            "max_abs_nA17_minus_n1_17": float(np.abs(nA[:, -1] - n1[:, -1]).max()),
            "max_abs_n1end_minus_d1": float(np.abs(z["n1_end"] - d1).max()),
            "max_abs_rhoA_minus_err_over_nA": float(np.nanmax(np.abs(rhoA - err / nA))),
            "frac_anc_eq_nn1_by_sigma": [float((anc[:, i].astype(int) == nn1).mean()) for i in range(S)],
            "auc_d1_alone": auc(d1, y), "auc_dD_by_sigma": [auc(z["dD"][:, i], y) for i in range(S)]}
    # how close is D(x_i) to the endpoint near the end: rank correlation of dD_i with d1
    def spearman(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return float(np.corrcoef(ra, rb)[0, 1])
    leak["spearman_dD_i_with_d1"] = {f"{sig[i]:.4g}": spearman(z["dD"][:, i], d1) for i in range(S - 6, S)}
    res["endpoint_checks"] = leak

    # ---- features
    dlog = np.log(sig[:-1] / sig[1:])
    incC = (1.0 - 0.5 * (rhoA[:, :-1] + rhoA[:, 1:])) * dlog
    incH = 0.5 * (L[:, :-1] + L[:, 1:]) * dlog
    rho_end = err / n1
    incC_end = (1.0 - 0.5 * (rho_end[:, :-1] + rho_end[:, 1:])) * dlog

    def C(w, i):
        return incC[:, j0[w]:i].sum(1)

    def H(w, i):
        return incH[:, j0[w]:i].sum(1)

    # reference: paper's late contraction (endpoint anchor) vs predictive-anchor C from 0.585 to 0.002
    Cp = incC_end[:, j0["C0.585"]:].sum(1); Cq = C("C0.585", S - 1)
    res["reference"] = {"auc_minus_C_paper": auc(-Cp, y), "auc_minus_C_pred": auc(-Cq, y),
                        "median_on_paper": float(np.median(Cp[~y])), "median_off_paper": float(np.median(Cp[y])),
                        "median_on_pred": float(np.median(Cq[~y])), "median_off_pred": float(np.median(Cq[y])),
                        "max_abs_Cpred_minus_Cpaper": float(np.abs(Cp - Cq).max()),
                        "n_samples_C_differs_gt_1e-9": int((np.abs(Cp - Cq) > 1e-9).sum()),
                        "auc_dD_end": auc(z["dD"][:, -1], y)}

    # ---- rows: (family, key, i, base features, full features)
    rows = []
    for i in range(S):
        rows.append(("rhoA", i, L[:, i], np.column_stack([L[:, i], rhoA[:, i]])))
        rows.append(("radA", i, L[:, i], np.column_stack([L[:, i], radA[:, i]])))
    for w in WSTART:
        for i in range(j0[w] + 1, S):
            rows.append((w, i, L[:, i], np.column_stack([L[:, i], C(w, i)])))
    for w in WSTART:
        for i in range(jt + 1, S):
            rows.append((w + "_trunc", i, L[:, i], np.column_stack([L[:, i], C(w, jt)])))
    holm_family = len(rows)
    for i in range(S):
        rows.append(("quad_radA", i, np.column_stack([L[:, i], L[:, i] ** 2]),
                     np.column_stack([L[:, i], L[:, i] ** 2, radA[:, i]])))
        rows.append(("quad_rhoA", i, np.column_stack([L[:, i], L[:, i] ** 2]),
                     np.column_stack([L[:, i], L[:, i] ** 2, rhoA[:, i]])))
        rows.append(("log_rhoA", i, L[:, i], np.column_stack([L[:, i], np.log(rhoA[:, i])])))
    if do_hist:
        for w in WSTART:
            hw = "Hist" + w[1:]
            for i in range(j0[w] + 1, S):
                rows.append((hw, i, L[:, i], np.column_stack([L[:, i], H(w, i)])))
                rows.append((w + "|hist", i, np.column_stack([L[:, i], H(w, i)]),
                             np.column_stack([L[:, i], H(w, i), C(w, i)])))

    # ---- in-sample LR tests
    for k, r in enumerate(rows):
        rows[k] = r + (lr_test(r[2].reshape(len(y), -1), r[3], yf),)
    p_family = np.array([r[4]["p_primary"] for r in rows[:holm_family]])
    p_holm = holm(p_family)
    res["holm_family_size"] = holm_family

    # ---- CV with own folds; cache OOF predictors by feature-set identity
    folds = [make_folds(y, r) for r in range(NREP)]
    rng = np.random.default_rng([SEED, 1])
    W = strat_weights(y, NBOOT, rng)
    cache = {}
    bcache = {}

    def oof(tag, F):
        if tag not in cache:
            cache[tag] = cv_oof(F, yf, folds)
        return cache[tag]

    def boot_auc(tag):
        """(NBOOT,) mean over repeats of the resampled AUC of the stored OOF predictor (cached per feature set)."""
        if tag not in bcache:
            o_ = cache[tag]
            bcache[tag] = np.mean([wauc(o_[r], yf, W) for r in range(NREP)], axis=0)
        return bcache[tag]

    out_rows = []
    for k, (fam, i, Fb, Ff, lr) in enumerate(rows):
        base_tag = ("base", fam.startswith("quad"), i) if not fam.endswith("|hist") else ("hist", fam, i)
        full_tag = (fam, i)
        if fam.endswith("|hist"):
            base_tag = ("Hist" + fam[1:].split("|")[0], i)    # the Hist row's full model is this base
        ob = oof(base_tag, Fb.reshape(len(y), -1)); of = oof(full_tag, Ff)
        ab = np.array([auc(ob[r], y) for r in range(NREP)]); af = np.array([auc(of[r], y) for r in range(NREP)])
        dd = boot_auc(full_tag) - boot_auc(base_tag)   # paired: same resamples, repeats averaged per resample
        row = {"family": fam, "i": int(i), "sigma": float(sig[i]),
               "cv_auc_base": float(ab.mean()), "cv_auc_base_sd": float(ab.std(ddof=1)),
               "cv_auc_full": float(af.mean()), "cv_auc_full_sd": float(af.std(ddof=1)),
               "dauc": float((af - ab).mean()), "dauc_sd_rep": float((af - ab).std(ddof=1)),
               "dauc_lo": float(np.percentile(dd, 2.5)), "dauc_hi": float(np.percentile(dd, 97.5)),
               "lr_chi2": float(lr["ml_chi2"]), "lr_p": float(lr["ml_p"]), "separation": lr["separation"],
               "firth_profile_chi2": float(lr["firth_profile_chi2"]),
               "firth_separate_chi2": float(lr["firth_separate_chi2"]), "p_primary": float(lr["p_primary"])}
        if k < holm_family:
            row["p_holm"] = float(p_holm[k])
        out_rows.append(row)
    res["rows"] = out_rows
    print(f"  [{name}] LR + CV + OOF bootstrap done ({time.time() - t0:.0f}s, {len(cache)} CV feature sets)",
          flush=True)

    # ---- single-feature AUCs with stratified bootstrap CIs (fixed orientation)
    sf = []
    for i in range(S):
        e = {"i": i, "sigma": float(sig[i])}
        feats = {"dD": z["dD"][:, i], "rhoA": rhoA[:, i], "radA": radA[:, i], "nA": nA[:, i]}
        boots = {}
        for kk, v in feats.items():
            boots[kk] = wauc(v, yf, W)
            e[kk] = [auc(v, y), float(np.percentile(boots[kk], 2.5)), float(np.percentile(boots[kk], 97.5))]
        for kk in ("rhoA", "radA"):
            dlt = boots[kk] - boots["dD"]
            e[kk + " - dD"] = [e[kk][0] - e["dD"][0], float(np.percentile(dlt, 2.5)),
                               float(np.percentile(dlt, 97.5))]
        if i > j0["C0.585"]:
            v = -C("C0.585", i); bC = wauc(v, yf, W)
            e["-C0.585"] = [auc(v, y), float(np.percentile(bC, 2.5)), float(np.percentile(bC, 97.5))]
            dlt = bC - boots["dD"]
            e["-C0.585 - dD"] = [e["-C0.585"][0] - e["dD"][0], float(np.percentile(dlt, 2.5)),
                                 float(np.percentile(dlt, 97.5))]
        sf.append(e)
    res["single_feature_auc"] = sf

    # ---- refit (out-of-bag) check on selected rows
    rng2 = np.random.default_rng([SEED, 2])
    Wr = strat_weights(y, NREFIT, rng2)
    ref = []
    for fam, i in do_refit_rows:
        r = next(rr for rr in rows if rr[0] == fam and rr[1] == i)
        o = refit_oob(r[2], r[3], y, Wr); o.update({"family": fam, "i": i, "sigma": float(sig[i])})
        ref.append(o)
    res["refit_oob"] = ref
    print(f"  [{name}] refit check done ({time.time() - t0:.0f}s)", flush=True)

    # ---- class-adjusted Firth check and class off-rate CV AUC
    cls = z["label"].astype(int); D = (cls[:, None] == np.unique(cls)[None, 1:]).astype(float)
    res["off_per_class"] = [int(y[cls == c].sum()) for c in np.unique(cls)]
    ca = []
    for fam, i in class_rows:
        cand = {"rhoA": rhoA[:, i], "radA": radA[:, i]}.get(fam)
        if cand is None:
            cand = C(fam, i)
        Xb, _, _ = design(np.column_stack([L[:, i], D]))
        Xf, _, _ = design(np.column_stack([L[:, i], D, cand]))
        _, pf = fit_firth(Xf, yf)
        free = np.ones(Xf.shape[1], bool); free[-1] = False
        _, pr = fit_firth(Xf, yf, free=free)
        _, pb = fit_firth(Xb, yf)
        ca.append({"family": fam, "i": i, "sigma": float(sig[i]), "firth_profile_chi2_class": 2 * (pf - pr),
                   "firth_separate_chi2_class": 2 * (pf - pb)})
    res["class_adjusted"] = ca
    rates = []
    for fo in folds:
        sc = np.empty(len(y))
        for g in range(NFOLD):
            te = fo == g; tr = ~te
            rate = {c: y[tr & (cls == c)].mean() for c in np.unique(cls)}
            sc[te] = [rate[c] for c in cls[te]]
        rates.append(auc(sc, y))
    res["cv_auc_class_rate"] = float(np.mean(rates))
    res["seconds"] = time.time() - t0
    return res


# ----------------------------------------------------------------------------------------------- comparison
def compare(name, mine, rep):
    """Pair my rows with the reported ones and list differences."""
    fam_map = {"quad_radA": ("radA", "quad"), "quad_rhoA": ("rhoA", "quad")}
    comp = []
    for r in mine["rows"]:
        fam = r["family"]
        if fam in fam_map:
            src, kind = fam_map[fam]
        else:
            src, kind = fam, "lin"
        lst = rep["incremental"].get(src)
        if lst is None:
            continue
        rr = next((x for x in lst if x["i"] == r["i"]), None)
        if rr is None:
            continue
        if kind == "quad":
            if "quad_dauc" not in rr:
                continue
            comp.append({"family": fam, "sigma": r["sigma"], "field": "quad_dauc", "reported": rr["quad_dauc"],
                         "mine": r["dauc"], "mc_sd_rep": r["dauc_sd_rep"]})
            continue
        for fld in ("cv_auc_base", "cv_auc_full", "dauc", "dauc_lo", "dauc_hi"):
            comp.append({"family": fam, "sigma": r["sigma"], "field": fld, "reported": rr.get(fld), "mine": r[fld],
                         "mc_sd_rep": r.get(fld + "_sd") or r["dauc_sd_rep"]})
        comp.append({"family": fam, "sigma": r["sigma"], "field": "lr_chi2", "reported": rr.get("lr_chi2"),
                     "mine": r["lr_chi2"]})
        comp.append({"family": fam, "sigma": r["sigma"], "field": "p_primary", "reported": rr.get("p_primary"),
                     "mine": r["p_primary"]})
        if "p_holm" in r:
            comp.append({"family": fam, "sigma": r["sigma"], "field": "p_holm", "reported": rr.get("p_holm"),
                         "mine": r["p_holm"]})
        comp.append({"family": fam, "sigma": r["sigma"], "field": "firth_chi2", "reported": rr.get("firth_chi2"),
                     "mine_profile": r["firth_profile_chi2"], "mine_separate": r["firth_separate_chi2"]})
    return comp


def summarise_comp(comp):
    s = {}
    det = ("lr_chi2", "p_primary", "p_holm")
    for fld in det:
        xs = [(c["mine"], c["reported"]) for c in comp if c["field"] == fld and c.get("reported") is not None]
        if not xs:
            continue
        a = np.array(xs, float)
        if fld == "lr_chi2":
            s[fld] = {"max_abs_diff": float(np.abs(a[:, 0] - a[:, 1]).max()), "n": len(a)}
        else:
            rel = np.abs(a[:, 0] - a[:, 1]) / np.maximum(a[:, 1], 1e-300)
            s[fld] = {"max_rel_diff": float(rel.max()), "n": len(a),
                      "n_rel_gt_1pct": int((rel > 0.01).sum())}
    xs = [(c["mine_profile"], c["mine_separate"], c["reported"]) for c in comp if c["field"] == "firth_chi2"
          and c.get("reported") is not None]
    if xs:
        a = np.array(xs, float)
        s["firth_chi2"] = {"max_abs_diff_profile": float(np.abs(a[:, 0] - a[:, 2]).max()),
                           "max_abs_diff_separate": float(np.abs(a[:, 1] - a[:, 2]).max()), "n": len(a)}
    for fld in ("cv_auc_base", "cv_auc_full", "dauc", "dauc_lo", "dauc_hi", "quad_dauc"):
        xs = [c for c in comp if c["field"] == fld and c.get("reported") is not None]
        if not xs:
            continue
        diff = np.array([c["mine"] - c["reported"] for c in xs])
        k = int(np.argmax(np.abs(diff)))
        s[fld] = {"n": len(xs), "max_abs_diff": float(np.abs(diff).max()), "median_abs_diff": float(np.median(np.abs(diff))),
                  "worst": {kk: xs[k][kk] for kk in ("family", "sigma", "reported", "mine")},
                  "n_abs_diff_gt_0.0015": int((np.abs(diff) > 0.0015).sum()),
                  "n_abs_diff_gt_0.005": int((np.abs(diff) > 0.005).sum())}
    return s


# (label, model, family, sigma index, decimals stated in the agent's headline findings)
HEADLINE_ROWS = [
    ("F1 radA sigma 19.4", "sub2000", "radA", 4, 3), ("F1 radA sigma 12.9", "sub2000", "radA", 5, 3),
    ("F1 radA sigma 8.4", "sub2000", "radA", 6, 3), ("F1 radA sigma 5.32", "sub2000", "radA", 7, 3),
    ("F1 radA sigma 3.26 (nothing)", "sub2000", "radA", 8, 3), ("F1 radA sigma 1.92", "sub2000", "radA", 9, 3),
    ("F1 radA sigma 1.09", "sub2000", "radA", 10, 4),
    ("F2 Hist5.3 sigma 3.26", "sub2000", "Hist5.3", 8, 3), ("F2 Hist1.9 sigma 0.14", "sub2000", "Hist1.9", 13, 3),
    ("F2 Hist0.585 sigma 0.14", "sub2000", "Hist0.585", 13, 3),
    ("F2 C5.3|hist sigma 1.92", "sub2000", "C5.3|hist", 9, 4), ("F2 C1.9|hist sigma 0.023", "sub2000", "C1.9|hist", 15, 4),
    ("F2 C0.585|hist sigma 0.002", "sub2000", "C0.585|hist", 17, 4),
    ("F3 rhoA sigma 80", "sub2000", "rhoA", 0, 3), ("F3 rhoA sigma 28.4", "sub2000", "rhoA", 3, 3),
    ("F3 rhoA sigma 3.26", "sub2000", "rhoA", 8, 3), ("F3 rhoA sigma 1.92", "sub2000", "rhoA", 9, 4),
    ("F3 rhoA sigma 1.09", "sub2000", "rhoA", 10, 4), ("F3 log_rhoA sigma 3.26", "sub2000", "log_rhoA", 8, 3),
    ("F4 C0.585 sigma 0.002", "sub2000", "C0.585", 17, 4),
    ("F5 C5.3 sigma 3.26", "sub2000", "C5.3", 8, 3), ("F5 C5.3 sigma 1.92", "sub2000", "C5.3", 9, 3),
    ("F5 C1.9 sigma 0.296", "sub2000", "C1.9", 12, 3), ("F5 C1.9 sigma 0.14", "sub2000", "C1.9", 13, 3),
    ("F5 C1.9 sigma 0.06", "sub2000", "C1.9", 14, 3), ("F5 C0.585 sigma 0.296", "sub2000", "C0.585", 12, 3),
    ("F5 C5.3 frozen@0.06 vs dD@0.002", "sub2000", "C5.3_trunc", 17, 4),
    ("F5 C1.9 frozen@0.06 vs dD@0.002", "sub2000", "C1.9_trunc", 17, 4),
    ("F5 C0.585 frozen@0.06 vs dD@0.002", "sub2000", "C0.585_trunc", 17, 4),
    ("F7 sub500s1 radA sigma 28.4", "sub500s1", "radA", 3, 3), ("F7 sub500s1 radA sigma 19.4", "sub500s1", "radA", 4, 3),
]


def headline(mine_all, rep_all):
    """Row-by-row comparison of the headline numbers: exact reported value, mine, agreement at the stated
    precision, and a Monte Carlo z-score (two independent 20-repeat means)."""
    out = []
    for lab, m, fam, i, dec in HEADLINE_ROWS:
        a = next(r for r in rep_all["models"][m]["incremental"][fam] if r["i"] == i)
        b = next(r for r in mine_all["models"][m]["rows"] if r["family"] == fam and r["i"] == i)
        ra = next((r for r in rep_all["models"][m]["refit_oob"] if r["cand"] == fam and r["i"] == i), None)
        rb = next((r for r in mine_all["models"][m]["refit_oob"] if r["family"] == fam and r["i"] == i), None)
        se = math.sqrt(2.0 / NREP) * max(b["dauc_sd_rep"], 1e-12)
        e = {"label": lab, "model": m, "family": fam, "sigma": a["sigma"], "decimals": dec,
             "z_dauc_mc": (b["dauc"] - a["dauc"]) / se,
             "p_holm_reported": a.get("p_holm"), "p_holm_mine": b.get("p_holm"),
             "lr_chi2_reported": a["lr_chi2"], "lr_chi2_mine": b["lr_chi2"]}
        for fld in ("cv_auc_base", "cv_auc_full", "dauc", "dauc_lo", "dauc_hi"):
            e[fld] = {"reported": a[fld], "mine": b[fld],
                      "same_at_stated_precision": round(a[fld], dec) == round(b[fld], dec)}
        if ra and rb:
            e["refit"] = {"reported": [ra["dauc_oob_mean"], ra["dauc_oob_lo"], ra["dauc_oob_hi"]],
                          "mine": [rb["mean"], rb["lo"], rb["hi"]],
                          "ci_excludes_0_reported": ra["dauc_oob_lo"] > 0, "ci_excludes_0_mine": rb["lo"] > 0}
        e["oof_ci_excludes_0"] = {"reported": a["dauc_lo"] > 0, "mine": b["dauc_lo"] > 0}
        out.append(e)
    return out


def seed_sensitivity():
    """Borderline significance labels: re-run folds + OOF bootstrap (and the refit check) with six seeds."""
    res = {}
    for m, fam, i, do_refit in (("sub500s1", "radA", 3, False), ("sub500s1", "radA", 4, False),
                                ("sub2000", "radA", 7, True), ("sub2000", "radA", 4, True)):
        z = dict(np.load(FILES[m])); y = z["d1"] / z["d2"] >= RATIO; yf = y.astype(float)
        L = np.log(z["dD"]); cand = z[fam][:, i]
        Fb = L[:, i]; Ff = np.column_stack([L[:, i], cand])
        rows = []
        for s in (11, 22, 33, 44, 55, 66):
            fo = []
            for r in range(NREP):
                rng = np.random.default_rng([s, r]); f = np.empty(len(y), int)
                for cls in (False, True):
                    idx = rng.permutation(np.flatnonzero(y == cls)); f[idx] = np.arange(len(idx)) % NFOLD
                fo.append(f)
            W = strat_weights(y, NBOOT, np.random.default_rng([s, 1]))
            ob = cv_oof(Fb, yf, fo); of = cv_oof(Ff, yf, fo)
            d = float(np.mean([auc(of[r], y) - auc(ob[r], y) for r in range(NREP)]))
            bb = np.mean([wauc(of[r], yf, W) - wauc(ob[r], yf, W) for r in range(NREP)], axis=0)
            row = {"seed": s, "dauc": d, "lo": float(np.percentile(bb, 2.5)), "hi": float(np.percentile(bb, 97.5))}
            if do_refit:
                rf = refit_oob(Fb, Ff, y, strat_weights(y, NREFIT, np.random.default_rng([s, 2])))
                row["refit"] = [rf["mean"], rf["lo"], rf["hi"]]
            rows.append(row)
        res[f"{m} {fam} sigma {z['sigma'][i]:.4g}"] = rows
    return res


def write_headline():
    mine_all = json.loads((OUT / "verify_incremental.json").read_text(encoding="utf-8"))
    rep_all = json.loads(REPORTED.read_text(encoding="utf-8"))
    h = {"headline_rows": headline(mine_all, rep_all), "seed_sensitivity": seed_sensitivity()}
    (OUT / "verify_incremental_headline.json").write_text(json.dumps(h, indent=1, default=float), encoding="utf-8")
    for e in h["headline_rows"]:
        print(f"{e['label']:36s} d rep {e['dauc']['reported']:+.5f} mine {e['dauc']['mine']:+.5f} "
              f"same@{e['decimals']}dp {e['dauc']['same_at_stated_precision']} z {e['z_dauc_mc']:+.2f} "
              f"CI rep [{e['dauc_lo']['reported']:+.4f},{e['dauc_hi']['reported']:+.4f}] "
              f"mine [{e['dauc_lo']['mine']:+.4f},{e['dauc_hi']['mine']:+.4f}]")
    print(json.dumps(h["seed_sensitivity"], indent=1, default=float))
    print("wrote", OUT / "verify_incremental_headline.json")


def main():
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    if "--headline" in sys.argv:
        write_headline()
        return
    reported = json.loads(REPORTED.read_text(encoding="utf-8"))
    refit_rows = {"sub2000": [("radA", i) for i in (4, 5, 6, 7, 8, 9, 10)] + [("rhoA", i) for i in (0, 8, 9, 10)]
                  + [("C5.3", 8), ("C5.3", 9), ("C1.9", 12), ("C1.9", 13), ("C1.9", 14), ("C0.585", 12),
                     ("C0.585", 17), ("C5.3_trunc", 17), ("C1.9_trunc", 17), ("C0.585_trunc", 17)],
                  "sub500s1": [("radA", 3), ("radA", 4)]}
    class_rows = {"sub2000": [("rhoA", 3), ("radA", 4), ("radA", 5), ("radA", 6), ("radA", 7), ("C5.3", 8)],
                  "sub500s1": [("radA", 3)]}
    allres = {"meta": {"script": "scripts/paperB_verify_incremental.py", "seed": SEED, "repeats": NREP,
                       "folds": NFOLD, "B": NBOOT, "B_refit": NREFIT, "ridge_cv": RIDGE, "ratio": RATIO,
                       "sources": {k: str(v.relative_to(ROOT)).replace("\\", "/") for k, v in FILES.items()},
                       "reported": str(REPORTED.relative_to(ROOT)).replace("\\", "/")}, "models": {}}
    for name, path in FILES.items():
        print(f"== {name}: {path}", flush=True)
        z = dict(np.load(path))
        mine = analyse(name, z, None, do_hist=(name == "sub2000"), do_refit_rows=refit_rows[name],
                       class_rows=class_rows[name])
        rep = reported["models"][name]
        comp = compare(name, mine, rep)
        mine["comparison_summary"] = summarise_comp(comp)
        mine["comparison"] = comp
        allres["models"][name] = mine
        print(json.dumps(mine["comparison_summary"], indent=1), flush=True)
    (OUT / "verify_incremental.json").write_text(json.dumps(allres, indent=1, default=float), encoding="utf-8")
    print("wrote", OUT / "verify_incremental.json")
    write_headline()


if __name__ == "__main__":
    main()
