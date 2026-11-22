"""Paper B: does the field-error / late-contraction signal add to the nearest-neighbour baseline?

EDM's 18-step Heun sampler on class-conditional CIFAR-10 subset models (per-sample arrays of
scripts/n3_directional_q.py). Target: the off-atom label, d1/d2 >= 1/3 at the endpoint. Predictors use
only information available at noise level sigma_i (predictive anchor A = nearest training image of the
class to D(x_i); no endpoint information):

  baseline     log dD_i     distance from D(x_i) to A (the nearest-neighbour detector)
  candidates   rhoA_i       relative field error |D - m*| / |x_i - A|
               radA_i       radial ratio <(x_i - A)/nA, D - A>/nA
               C_i^(s0)     causal late contraction
                              sum_{j=j0}^{i-1} (1 - (rhoA_j + rhoA_{j+1})/2) log(sigma_j / sigma_{j+1}),
                            window from sigma_{j0} (grid value nearest s0, s0 in {5.3, 1.9, 0.585}) to
                            sigma_i, defined for i > j0. The sum stops at interval [sigma_{i-1}, sigma_i],
                            so it uses rhoA only up to index i.
               C^(s0) truncated at sigma = 0.06 (grid 0.05995, index 14) and held fixed while the
                            baseline moves on to sigma_15..17 ("C restricted to sigma >= 0.06").
  diagnostics  log rhoA_i (functional form), log nA_i (rhoA ~ dD/nA once m* sits on A), and the placebo
               (log dD_i)^2 (a candidate that can only repair the baseline's functional form).
  history      H_i^(s0) = the same trapezoid integral of log dD over the same window as C_i^(s0). "Hist" tests H
               over log dD_i; "C|hist" tests C over (log dD_i, H_i): does the contraction add beyond the
               baseline's own trajectory history, or does its gain come only from using several noise levels?

For every sigma index with at least 10 samples in each class: label ~ baseline versus
label ~ baseline + candidate, logistic regression by Newton-Raphson in numpy, reporting
  (1) cross-validated AUC of both models: 10-fold stratified, repeated 20 times with fold seeds
      [seed, 0..19]; per repeat the AUC of the pooled out-of-fold linear predictor, then the mean;
  (2) Delta AUC (mean over repeats) with a 95% paired, class-stratified bootstrap interval that resamples
      SAMPLES and re-scores the stored OUT-OF-FOLD predictions (no refit; the 20 repeats are averaged
      inside every resample). A refit check (fit both models on a stratified resample, AUC on its
      out-of-bag samples) is run at selected noise levels;
  (3) the in-sample likelihood-ratio test (chi2, 1 df) of the maximum-likelihood fits; where the MLE does
      not exist (complete separation) the primary p-value is Firth's penalised LR test (Heinze & Schemper
      2002), which is also reported everywhere; Holm's adjustment over the family of field-error tests of
      each model (rhoA, radA, the three C windows and the truncated C rows; diagnostics are excluded);
plus Delta AUC against a quadratic baseline (log dD, (log dD)^2), the cross-validated log-likelihood gain
per sample, a class-adjusted check (Firth LR test with class dummies added to the baseline; off-atom rates
differ by class), and the AUC of every single feature with its bootstrap interval (orientation fixed in
advance: larger dD, rhoA, radA, nA and smaller C mean off-atom).

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_incremental

Outputs: results/paperB_20261121/incremental/{incremental.json, INCREMENTAL.md}
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import time

import numpy as np

R = pathlib.Path("results")
OUT = R / "paperB_20261121" / "incremental"
MODELS = (("sub2000", R / "n3_rho2_20261118" / "sub2000" / "q_per_sample.npz", "primary (balanced, 2000 images)"),
          ("sub500s1", R / "n3_rho2_20261118" / "sub500s1" / "q_per_sample.npz", "secondary (second 500-image model)"))
RATIO = 1.0 / 3.0                       # off-atom threshold, as scripts.n3_edm_memorization.RATIO
WINDOW_STARTS = (5.3, 1.9, 0.585)       # late-contraction windows start at the nearest grid value
SIGMA_STOP = 0.06                       # "C restricted to sigma >= 0.06": nearest grid value (0.05995)
MIN_CLASS = 10
RIDGE_CV = 1e-4                         # on standardised slopes; only keeps fits finite under separation
PRIMARY = ("rhoA", "radA", "C5.3", "C1.9", "C0.585")
DIAGNOSTIC = ("log_rhoA", "log_nA", "placebo_logdD2")
# history control: H^(s0) = the same trapezoid integral over the same window applied to log dD; "Hist" tests H
# over log dD_i, "C|hist" tests C over (log dD_i, H_i), i.e. whether C adds beyond the baseline's own history
HISTORY = tuple(f"Hist{s0:g}" for s0 in WINDOW_STARTS) + tuple(f"C{s0:g}|hist" for s0 in WINDOW_STARTS)


def is_diag(k):
    """Keys outside the Holm family of field-error tests."""
    return k in DIAGNOSTIC or k in HISTORY


# ----------------------------------------------------------------------------------------- statistics
def expit(eta):
    return 0.5 * (1.0 + np.tanh(0.5 * eta))


def loglik_terms(eta, y):
    """Per-sample Bernoulli log-likelihood y*eta - log(1 + e^eta)."""
    return y * eta - np.logaddexp(0.0, eta)


def fit_logistic(X, y, ridge=0.0, max_iter=100, tol=1e-9):
    """Newton-Raphson with step halving for l(b) - ridge/2 |b[1:]|^2 (column 0 = intercept).

    Returns (beta, unpenalised log-likelihood, converged). Converged means the last Newton step moved no
    coefficient by more than tol; under complete separation with ridge = 0 it never does."""
    p = X.shape[1]
    pen = np.full(p, float(ridge)); pen[0] = 0.0
    b = np.zeros(p)
    ybar = float(np.clip(y.mean(), 1e-6, 1 - 1e-6)); b[0] = math.log(ybar / (1 - ybar))

    def obj(bb):
        return float(loglik_terms(X @ bb, y).sum() - 0.5 * np.sum(pen * bb * bb))

    f = obj(b); conv = False
    for _ in range(max_iter):
        mu = expit(X @ b); w = mu * (1 - mu)
        g = X.T @ (y - mu) - pen * b
        H = (X.T * w) @ X + np.diag(pen)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        t = 1.0
        while True:
            nb = b + t * step; nf = obj(nb)
            if nf >= f - 1e-12 * (1 + abs(f)) or t < 1e-8:
                break
            t *= 0.5
        db = float(np.max(np.abs(nb - b)))
        b, f = nb, nf
        if db < tol:
            conv = True
            break
    return b, float(loglik_terms(X @ b, y).sum()), conv


def fit_firth(X, y, fixed=None, max_iter=200, tol=1e-9):
    """Firth logistic regression: maximise l(b) + 0.5 log det(X'WX). With fixed=k the coefficient k is
    held at 0 and the penalty still uses the full design (profile penalised likelihood). Returns
    (beta, penalised log-likelihood)."""
    p = X.shape[1]
    free = np.ones(p, bool)
    if fixed is not None:
        free[fixed] = False
    b = np.zeros(p)

    def pobj(bb):
        eta = X @ bb; mu = expit(eta); w = mu * (1 - mu)
        I = (X.T * w) @ X
        sign, logdet = np.linalg.slogdet(I)
        val = float(loglik_terms(eta, y).sum() + 0.5 * logdet) if sign > 0 else -np.inf
        return val, mu, w, I

    f, mu, w, I = pobj(b)
    for _ in range(max_iter):
        Iinv = np.linalg.inv(I)
        h = w * np.einsum("ij,jk,ik->i", X, Iinv, X)
        U = X.T @ (y - mu + h * (0.5 - mu))
        step = np.zeros(p)
        step[free] = np.linalg.solve(I[np.ix_(free, free)], U[free])
        t = 1.0
        while True:
            nb = b + t * step; nf, nmu, nw, nI = pobj(nb)
            if nf >= f - 1e-12 * (1 + abs(f)) or t < 1e-8:
                break
            t *= 0.5
        db = float(np.max(np.abs(nb - b)))
        b, f, mu, w, I = nb, nf, nmu, nw, nI
        if db < tol:
            break
    return b, f


def chi2_sf1(x):
    """P(chi2 with 1 df > x)."""
    if x is None or not np.isfinite(x):
        return float("nan")
    return math.erfc(math.sqrt(max(float(x), 0.0) / 2.0))


def holm(ps):
    ps = np.asarray(ps, float)
    ok = np.isfinite(ps); m = int(ok.sum())
    adj = np.full(len(ps), np.nan)
    order = np.argsort(np.where(ok, ps, np.inf))[:m]
    run = 0.0
    for k, idx in enumerate(order):
        run = max(run, min(1.0, (m - k) * ps[idx]))
        adj[idx] = run
    return adj


def wauc(score, pos, W=None):
    """AUC = P(score_pos > score_neg) + P(tie)/2, with sample weights W of shape (B, n) (bootstrap counts);
    W=None gives the plain AUC as a float. With integer counts every partial sum is an integer or half-integer
    below n_pos * n_neg < 2^24, so float32 counts are exact."""
    o = np.argsort(score, kind="mergesort")
    s, p = score[o], pos[o]
    ties = s[1:] == s[:-1]
    if ties.any():
        Wo = np.ones((1, len(s))) if W is None else W[:, o].astype(np.float64)
        wp = Wo * p
        wn = Wo - wp
        st = np.flatnonzero(np.r_[True, ~ties])
        wp, wn = np.add.reduceat(wp, st, axis=1), np.add.reduceat(wn, st, axis=1)
        num = (wp * (np.cumsum(wn, 1) - 0.5 * wn)).sum(1)
        a = num / (wp.sum(1) * wn.sum(1))
        return float(a[0]) if W is None else a
    ip, ineg = o[p], o[~p]                         # positives / negatives in increasing score order
    m = np.cumsum(~p)[p]                           # negatives below each positive (no ties)
    if W is None:
        return float(m.sum() / (len(ip) * len(ineg)))
    cn = np.zeros((W.shape[0], len(ineg) + 1), dtype=W.dtype)
    cn[:, 1:] = W[:, ineg]
    np.cumsum(cn, axis=1, out=cn)
    wp = W[:, ip]
    num = (wp * cn[:, m]).sum(1, dtype=np.float64)
    return num / (wp.sum(1, dtype=np.float64) * cn[:, -1].astype(np.float64))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float); rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def strat_folds(pos, k, seed):
    rng = np.random.default_rng(seed)
    f = np.empty(len(pos), int)
    for cls in (True, False):
        idx = rng.permutation(np.flatnonzero(pos == cls))
        f[idx] = np.arange(len(idx)) % k
    return f


def boot_weights(pos, B, rng):
    """Class-stratified bootstrap: row b holds how often each sample is drawn."""
    ip, ineg = np.flatnonzero(pos), np.flatnonzero(~pos)
    n = len(pos)
    W = np.empty((B, n), dtype=np.float32)          # integer counts, exact in float32
    for b in range(B):
        W[b] = np.bincount(rng.choice(ip, len(ip)), minlength=n) + np.bincount(rng.choice(ineg, len(ineg)), minlength=n)
    return W


def design(F, ref=None):
    """Intercept + columns standardised with the mean/sd of ref (default F)."""
    ref = F if ref is None else ref
    m, s = ref.mean(0), ref.std(0); s = np.where(s > 0, s, 1.0)
    return np.column_stack([np.ones(len(F)), (F - m) / s])


def cv_eta(F, y, folds):
    """Out-of-fold linear predictor of label ~ F, one row per repeat."""
    E = np.empty((len(folds), len(y)))
    for r, fo in enumerate(folds):
        for k in range(int(fo.max()) + 1):
            te = fo == k; tr = ~te
            b, _, _ = fit_logistic(design(F[tr]), y[tr], ridge=RIDGE_CV)
            E[r, te] = design(F[te], F[tr]) @ b
    return E


class CVBlock:
    """Out-of-fold predictions of one feature set and what is reused across comparisons."""

    def __init__(self, F, y, pos, folds, W):
        self.E = cv_eta(F, y, folds)
        self.auc = np.array([wauc(e, pos) for e in self.E])                  # (R,)
        self.boot = np.mean([wauc(e, pos, W) for e in self.E], axis=0)        # (B,), mean over repeats
        self.ll = loglik_terms(self.E, y[None, :]).mean(0)                    # (n,), mean over repeats


def compare(base: CVBlock, full: CVBlock, W):
    d = full.auc - base.auc
    db = full.boot - base.boot
    dll = full.ll - base.ll
    dllb = (W @ dll) / W.sum(1, dtype=np.float64)
    return {"cv_auc_base": float(base.auc.mean()), "cv_auc_base_sd": float(base.auc.std(ddof=1)),
            "cv_auc_full": float(full.auc.mean()), "cv_auc_full_sd": float(full.auc.std(ddof=1)),
            "dauc": float(d.mean()), "dauc_lo": float(np.percentile(db, 2.5)), "dauc_hi": float(np.percentile(db, 97.5)),
            "dauc_repeat_min": float(d.min()), "dauc_repeat_max": float(d.max()),
            "cv_dll": float(dll.mean()), "cv_dll_lo": float(np.percentile(dllb, 2.5)),
            "cv_dll_hi": float(np.percentile(dllb, 97.5))}


def insample_tests(Fb, x, y, pos):
    """ML likelihood-ratio test and Firth penalised LR test of the last column, in-sample."""
    F = np.column_stack([Fb, x])
    Xf = design(F); Xb = Xf[:, :-1]
    bb, llb, cb = fit_logistic(Xb, y); bf, llf, cf = fit_logistic(Xf, y)
    sep_b = (not cb) or wauc(Xb @ bb, pos) >= 1.0
    sep_f = (not cf) or wauc(Xf @ bf, pos) >= 1.0
    sep = bool(sep_b or sep_f)
    chi2 = float("nan") if sep else max(2.0 * (llf - llb), 0.0)
    bF, lF = fit_firth(Xf, y); _, l0 = fit_firth(Xf, y, fixed=Xf.shape[1] - 1)
    chi2F = max(2.0 * (lF - l0), 0.0)
    p_ml, p_f = chi2_sf1(chi2), chi2_sf1(chi2F)
    return {"lr_chi2": chi2, "lr_p": p_ml, "separation": sep, "separation_base": bool(sep_b),
            "firth_chi2": float(chi2F), "firth_p": p_f, "p_primary": p_f if sep else p_ml,
            "p_primary_test": "firth" if sep else "ml",
            "coef_per_sd": float("nan") if sep else float(bf[-1]), "coef_per_sd_firth": float(bF[-1])}


def refit_oob(Fb, x, y, pos, B, rng):
    """Fit both models on a stratified resample, AUC on its out-of-bag samples; returns Delta AUC draws."""
    F = np.column_stack([Fb, x]); n = len(y)
    ip, ineg = np.flatnonzero(pos), np.flatnonzero(~pos)
    out = []
    for _ in range(B):
        idx = np.r_[rng.choice(ip, len(ip)), rng.choice(ineg, len(ineg))]
        oob = np.ones(n, bool); oob[idx] = False
        if pos[oob].sum() < 2 or (~pos[oob]).sum() < 2:
            continue
        Xf_in = design(F[idx]); Xf_oob = design(F[oob], F[idx])
        bb, _, _ = fit_logistic(Xf_in[:, :-1], y[idx], ridge=RIDGE_CV)
        bf, _, _ = fit_logistic(Xf_in, y[idx], ridge=RIDGE_CV)
        out.append(wauc(Xf_oob @ bf, pos[oob]) - wauc(Xf_oob[:, :-1] @ bb, pos[oob]))
    return np.asarray(out)


# ----------------------------------------------------------------------------------------- features
def nearest(sig, s0):
    return int(np.argmin(np.abs(np.log(sig) - np.log(s0))))


def causal_int(v, sig, j0):
    """I[:, i] = sum_{j=j0}^{i-1} (v_j + v_{j+1})/2 log(sig_j/sig_{j+1}) for i > j0 (trapezoid rule in log sigma
    from sigma_{j0} down to sigma_i), NaN otherwise."""
    inc = 0.5 * (v[:, :-1] + v[:, 1:]) * np.log(sig[:-1] / sig[1:])   # interval [j, j+1]
    out = np.full(v.shape, np.nan)
    out[:, j0 + 1:] = np.cumsum(inc[:, j0:], axis=1)
    return out


def causal_C(rho, sig, j0):
    """C[:, i] = sum_{j=j0}^{i-1} (1 - (rho_j + rho_{j+1})/2) log(sig_j/sig_{j+1}) for i > j0, NaN otherwise."""
    return causal_int(1.0 - rho, sig, j0)


def ci(e):
    return float(e[0]), float(np.percentile(e[1], 2.5)), float(np.percentile(e[1], 97.5))


# ----------------------------------------------------------------------------------------- analysis
def analyse(name, path, role, a, mi):
    t0 = time.time()
    z = np.load(path)
    sig = z["sigma"]; S = len(sig)
    pos = (z["d1"] / z["d2"]) >= RATIO               # off-atom = positive class
    y = pos.astype(float); n = len(y)
    n_off, n_on = int(pos.sum()), int((~pos).sum())
    W = boot_weights(pos, a.B, np.random.default_rng([a.seed, 2, mi]))
    folds = [strat_folds(pos, a.folds, [a.seed, r]) for r in range(a.repeats)]

    dD, rhoA, radA, nA = z["dD"], z["rhoA"], z["radA"], z["nA"]
    logdD = np.log(dD)
    j0s = {f"C{s0:g}": nearest(sig, s0) for s0 in WINDOW_STARTS}
    Cs = {k: causal_C(rhoA, sig, j0) for k, j0 in j0s.items()}
    Hs = {k: causal_int(logdD, sig, j0) for k, j0 in j0s.items()}       # history control, same windows
    i_stop = nearest(sig, SIGMA_STOP)

    def cand(key, i):
        if key == "rhoA":
            return rhoA[:, i]
        if key == "radA":
            return radA[:, i]
        if key in Cs:
            return Cs[key][:, i]
        if key.endswith("_trunc"):
            return Cs[key[:-6]][:, i_stop] if i > i_stop else None
        if key == "log_rhoA":
            return np.log(rhoA[:, i])
        if key == "log_nA":
            return np.log(nA[:, i])
        if key == "placebo_logdD2":
            return logdD[:, i] ** 2
        if key.startswith("Hist"):
            return Hs["C" + key[4:]][:, i]
        if key.endswith("|hist"):
            return Cs[key[:-5]][:, i]
        raise KeyError(key)

    def spec(key, i):
        """(baseline key, baseline features, candidate) for a comparison at sigma_i."""
        if key.endswith("|hist"):
            h = Hs[key[:-5]][:, i]
            return f"dD+Hist{key[1:-5]}", np.column_stack([logdD[:, i], h]), cand(key, i)
        return "dD", logdD[:, i:i + 1], cand(key, i)

    # ---- single-feature AUCs (orientation fixed in advance), bootstrap CIs, paired differences vs dD
    single = {}
    sf = {"dD": dD, "rhoA": rhoA, "radA": radA, "nA": nA, **{f"-{k}": -v for k, v in Cs.items()}}
    for i in range(S):
        row = {"i": i, "sigma": float(sig[i])}
        bD = wauc(dD[:, i], pos, W)
        for k, v in sf.items():
            x = v[:, i]
            if not np.isfinite(x).all():
                continue
            e = (wauc(x, pos), wauc(x, pos, W))
            row[k] = ci(e)
            if k != "dD":
                row[f"{k} - dD"] = ci((e[0] - wauc(dD[:, i], pos), e[1] - bD))
        single[i] = row
    # reference (not causal): the paper's C with the endpoint anchor, rho = err/n1, from sigma 0.585 to 0.002
    rho_end = z["err"] / z["n1"]
    Cpaper = causal_C(rho_end, sig, j0s["C0.585"])[:, -1]
    ref = {"auc_minus_C_paper_endpoint_anchor": ci((wauc(-Cpaper, pos), wauc(-Cpaper, pos, W))),
           "auc_minus_C0.585_predictive_anchor_at_0.002": single[S - 1]["-C0.585"],
           "auc_dD_at_0.002": single[S - 1]["dD"],
           "C_paper_median_on": float(np.median(Cpaper[~pos])), "C_paper_median_off": float(np.median(Cpaper[pos])),
           "C0.585_predictive_median_on_at_0.002": float(np.median(Cs["C0.585"][~pos, -1])),
           "C0.585_predictive_median_off_at_0.002": float(np.median(Cs["C0.585"][pos, -1])),
           "anchor_equals_endpoint_nn_frac": [float(np.mean(z["anc"][:, i] == z["nn1"])) for i in range(S)]}

    # ---- incremental value over log dD
    keys = PRIMARY + tuple(f"{k}_trunc" for k in Cs) + DIAGNOSTIC + HISTORY
    inc = {k: [] for k in keys}
    for i in range(S):
        if n_off < MIN_CLASS or n_on < MIN_CLASS:
            continue
        cache = {}

        def block(key, F):
            if key not in cache:
                cache[key] = CVBlock(F, y, pos, folds, W)
            return cache[key]

        Fq = np.column_stack([logdD[:, i], logdD[:, i] ** 2])
        for k in keys:
            bkey, Fb, x = spec(k, i)
            if x is None or not np.isfinite(x).all() or not np.isfinite(Fb).all():
                continue
            base = block(bkey, Fb)
            full = block(f"{bkey}+{k.replace('|hist', '')}", np.column_stack([Fb, x]))
            orient = -1.0 if k.startswith("C") else 1.0                       # smaller C = off-atom
            row = {"i": i, "sigma": float(sig[i]), "baseline": bkey, "auc_dD_raw": wauc(dD[:, i], pos),
                   "auc_dD_raw_lo": single[i]["dD"][1], "auc_dD_raw_hi": single[i]["dD"][2],
                   "auc_cand_raw": None if k == "placebo_logdD2" else wauc(orient * x, pos),
                   **compare(base, full, W), **insample_tests(Fb, x, y, pos),
                   "spearman_with_logdD": spearman(x, logdD[:, i])}
            if not is_diag(k):
                cq = compare(block("quad", Fq), block(f"quad+{k}", np.column_stack([Fq, x])), W)
                row.update({"quad_cv_auc_base": cq["cv_auc_base"], "quad_cv_auc_full": cq["cv_auc_full"],
                            "quad_dauc": cq["dauc"], "quad_dauc_lo": cq["dauc_lo"], "quad_dauc_hi": cq["dauc_hi"]})
            inc[k].append(row)
        print(f"  [{name}] sigma {sig[i]:.4g} done ({time.time() - t0:.0f}s, {len(cache)} CV blocks)", flush=True)

    # Holm over the family of field-error tests (primary + truncated C), separately per model
    fam = [(k, r) for k in keys if not is_diag(k) for r in inc[k]]
    adj = holm([r["p_primary"] for _, r in fam])
    for (_, r), p in zip(fam, adj):
        r["p_holm"] = float(p)
    for k in keys:
        if is_diag(k):
            for r in inc[k]:
                r["p_holm"] = None

    # ---- class-adjusted check: the class is known at sampling time and off-atom rates differ by class.
    # Firth penalised LR test of the candidate given log dD + class dummies (Firth because classes with few
    # off-atom samples separate), and the CV AUC of the class off-rate alone (same folds).
    cl = z["label"].astype(int); nc = int(cl.max()) + 1; Dm = np.eye(nc)[cl][:, 1:]
    cls_auc = []
    for fo in folds:
        s_ = np.empty(n)
        for kf in range(int(fo.max()) + 1):
            te = fo == kf; tr = ~te
            rate = np.array([y[tr][cl[tr] == c].mean() if (cl[tr] == c).any() else y[tr].mean() for c in range(nc)])
            s_[te] = rate[cl[te]]
        cls_auc.append(wauc(s_, pos))
    class_adj = {"cv_auc_class_rate": float(np.mean(cls_auc)),
                 "off_per_class": [int(pos[cl == c].sum()) for c in range(nc)],
                 "n_per_class": [int((cl == c).sum()) for c in range(nc)], "rows": []}
    for i in range(S):
        for k in PRIMARY:
            x = cand(k, i)
            if x is None or not np.isfinite(x).all():
                continue
            Xf = design(np.column_stack([logdD[:, i], Dm, x]))
            _, lF = fit_firth(Xf, y); _, l0 = fit_firth(Xf, y, fixed=Xf.shape[1] - 1)
            c2 = max(2.0 * (lF - l0), 0.0)
            class_adj["rows"].append({"cand": k, "i": i, "sigma": float(sig[i]), "firth_chi2_class": c2,
                                      "firth_p_class": chi2_sf1(c2)})
    print(f"  [{name}] class-adjusted check done ({time.time() - t0:.0f}s)", flush=True)

    # ---- refit (out-of-bag) check for every field-error row
    refit = []
    rng = np.random.default_rng([a.seed, 3, mi])
    for k in keys:
        if is_diag(k):
            continue
        for i in range(S):
            x = cand(k, i)
            if x is None or not np.isfinite(x).all():
                continue
            d = refit_oob(logdD[:, i:i + 1], x, y, pos, a.b_refit, rng)
            refit.append({"cand": k, "i": i, "sigma": float(sig[i]), "B": int(len(d)), "dauc_oob_mean": float(d.mean()),
                          "dauc_oob_lo": float(np.percentile(d, 2.5)), "dauc_oob_hi": float(np.percentile(d, 97.5))})
    print(f"  [{name}] refit check done ({time.time() - t0:.0f}s)", flush=True)

    return {"source": str(path).replace("\\", "/"), "role": role, "n": n, "n_off": n_off, "n_on": n_on,
            "sigma": [float(s) for s in sig], "window_start_index": j0s,
            "window_start_sigma": {k: float(sig[j]) for k, j in j0s.items()},
            "trunc_index": i_stop, "trunc_sigma": float(sig[i_stop]),
            "single_feature_auc": [single[i] for i in range(S)], "incremental": inc, "refit_oob": refit,
            "class_adjusted": class_adj, "reference": ref, "seconds": time.time() - t0}


# ----------------------------------------------------------------------------------------- reporting
BEST_KEYS = ("i", "sigma", "auc_dD_raw", "auc_dD_raw_lo", "auc_cand_raw", "cv_auc_base", "cv_auc_full", "dauc",
             "dauc_lo", "dauc_hi", "p_primary", "p_holm", "lr_chi2", "firth_chi2", "separation", "quad_dauc",
             "quad_dauc_lo", "quad_dauc_hi", "cv_dll", "cv_dll_lo", "cv_dll_hi")


def headline(m):
    """Per candidate: where the CV Delta AUC interval excludes 0, where (Holm) p < 0.05, both, split by whether
    the baseline is informative there (raw AUC of dD with bootstrap interval above 0.5), and the largest gain
    with its refit (out-of-bag) check."""
    H = {}
    oob = {(r["cand"], r["i"]): r for r in m["refit_oob"]}

    def p_of(r, diag):
        p = r["p_primary"] if diag else r["p_holm"]
        return 1.0 if p is None or not np.isfinite(p) else p

    def best_of(k, rows):
        b = max(rows, key=lambda r: r["dauc"])
        out = {kk: b[kk] for kk in BEST_KEYS if kk in b}
        o = oob.get((k, b["i"]))
        if o:
            out.update({"dauc_oob_mean": o["dauc_oob_mean"], "dauc_oob_lo": o["dauc_oob_lo"], "dauc_oob_hi": o["dauc_oob_hi"]})
        gap = 1 - b["cv_auc_base"]
        out["gap_closed"] = b["dauc"] / gap if gap >= 0.005 else None
        return out

    for k, rows in m["incremental"].items():
        if not rows:
            continue
        diag = is_diag(k)
        both = [r for r in rows if r["dauc_lo"] > 0 and p_of(r, diag) < 0.05]
        H[k] = {"sigma_dauc_ci_above_0": [r["sigma"] for r in rows if r["dauc_lo"] > 0],
                "sigma_dauc_ci_below_0": [r["sigma"] for r in rows if r["dauc_hi"] < 0],
                "sigma_lr_significant": [r["sigma"] for r in rows if p_of(r, diag) < 0.05],
                "sigma_both": [r["sigma"] for r in both],
                "sigma_both_baseline_informative": [r["sigma"] for r in both if r["auc_dD_raw_lo"] > 0.5],
                "sigma_both_baseline_near_chance": [r["sigma"] for r in both if r["auc_dD_raw_lo"] <= 0.5],
                "sigma_both_and_refit_ci_above_0": [r["sigma"] for r in both
                                                    if (k, r["i"]) in oob and oob[(k, r["i"])]["dauc_oob_lo"] > 0],
                "best": best_of(k, rows)}
        inf = [r for r in rows if r["auc_dD_raw_lo"] > 0.5]
        if inf:
            H[k]["best_baseline_informative"] = best_of(k, inf)
        if k.startswith("C") and not k.endswith("_trunc"):
            rr = [r for r in rows if r["i"] <= m["trunc_index"]]
            if rr:
                H[k]["restricted_sigma_ge_0.06"] = {
                    "sigma_dauc_ci_above_0": [r["sigma"] for r in rr if r["dauc_lo"] > 0],
                    "sigma_both": [r["sigma"] for r in rr if r["dauc_lo"] > 0 and p_of(r, diag) < 0.05],
                    "best": best_of(k, rr)}
    return H


def f3(v):
    return "-" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.3f}"


def fci(v, lo, hi, d=3):
    return f"{v:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]"


def fp(p):
    if p is None or not np.isfinite(p):
        return "-"
    return "<1e-300" if p == 0 else (f"{p:.2g}" if p < 0.001 else f"{p:.3f}")


def fsig(v):
    return ", ".join(f"{s:.3g}" for s in v) if v else "none"


def write_md(res, path):
    L = ["# Paper B: incremental value of the field-error signal over the nearest-neighbour baseline", "",
         "Script: `scripts/paperB_incremental.py`. Target: off-atom label (endpoint d1/d2 >= 1/3; not the key "
         "`label`, which is the class). Every predictor at noise level sigma_i uses the predictive anchor (nearest "
         "training image of D(x_i)), so nothing uses the endpoint.", "",
         "* Baseline: log dD_i. Candidates: rhoA_i, radA_i, causal late contraction C_i^(s0) = sum_{j=j0}^{i-1} "
         "(1 - (rhoA_j + rhoA_{j+1})/2) log(sigma_j/sigma_{j+1}) from sigma_{j0} (grid 5.32, 1.92, 0.585) to sigma_i "
         "(the last interval ends at sigma_i, so only rhoA up to index i enters).",
         "* Logistic regression, Newton-Raphson; CV fits carry a ridge of 1e-4 on standardised slopes (inert unless the "
         "classes separate). CV = 10-fold stratified x 20 repeats (fold seeds [20261121, r], r = 0..19); CV AUC = AUC of "
         "the pooled out-of-fold linear predictor of a repeat, mean over repeats.",
         f"* Delta AUC interval: 95% paired class-stratified bootstrap over samples (B = {res['meta']['B']}) of the stored "
         "out-of-fold predictions, no refit, repeats averaged inside each resample. The refit check (fit on the "
         f"resample, AUC on out-of-bag samples, B = {res['meta']['b_refit']}) is in its own table.",
         "* LR test: in-sample ML fits, chi2 with 1 df; where the MLE does not exist (complete separation, marked F) the "
         "p-value is Firth's penalised LR test. Holm: over all field-error tests of a model (rhoA, radA, C windows, "
         "truncated C); diagnostics are not in the family and show raw p.",
         "* quad Delta AUC: the same comparison with a quadratic baseline (log dD, (log dD)^2).",
         "* CV dLL: out-of-fold log-likelihood gain per sample (nats), bootstrap interval as for Delta AUC.",
         "* 'C restricted to sigma >= 0.06': the C rows with sigma_i >= 0.05995 (grid value nearest 0.06, index 14), and "
         "the rows `C*_trunc`, where C is frozen at sigma 0.05995 and compared with log dD at sigma 0.0229, 0.00753, 0.002.",
         "* History control (diagnostic, not in the Holm family): `Hist*` = the same trapezoid integral over the same "
         "window applied to log dD, tested over log dD_i; `C*|hist` = C tested over (log dD_i, Hist_i). C aggregates "
         "several noise levels while the baseline uses one; this separates the field-error content of C from the "
         "benefit of using the trajectory's history.",
         "* Class-adjusted check: Firth LR test of the candidate given log dD + class dummies (the class is known at "
         "sampling time and off-atom rates differ by class).",
         "* Resolution: the OOF bootstrap resolves Delta AUC of order 1e-4 (the placebo (log dD)^2 has intervals "
         "slightly below 0), so an interval above 0 for a gain of 0.002 means a real but small gain; the refit "
         "interval is wider and is the more conservative one.", ""]
    for name, m in res["models"].items():
        H = m["headline"]
        L += [f"## {name}: {m['role']}", "",
              f"Source: `{m['source']}`; n = {m['n']}, off-atom {m['n_off']}, on-atom {m['n_on']}. Window starts: "
              + ", ".join(f"{k} -> sigma {v:.4g}" for k, v in m["window_start_sigma"].items())
              + f"; truncation for 'C restricted to sigma >= 0.06': sigma {m['trunc_sigma']:.4g} (index {m['trunc_index']}).", "",
              "### Headline: where a candidate adds to log dD", "",
              "'both' = CV Delta AUC interval above 0 and Holm p < 0.05 (diagnostics: raw p). 'Baseline informative' = "
              "raw AUC of dD with bootstrap interval above 0.5; where it is not, an uninformative baseline has a CV AUC "
              "below 0.5 and the gain is the candidate's own (weak) signal.", "",
              "| candidate | Delta AUC CI > 0 | Holm p < 0.05 | both, baseline informative | both, baseline near chance | both and refit CI > 0 | Delta AUC CI < 0 |",
              "|---|---|---|---|---|---|---|"]
        for k, h in H.items():
            L.append(f"| {k} | {fsig(h['sigma_dauc_ci_above_0'])} | {fsig(h['sigma_lr_significant'])}"
                     f"{' (raw p)' if is_diag(k) else ''} | {fsig(h['sigma_both_baseline_informative'])} | "
                     f"{fsig(h['sigma_both_baseline_near_chance'])} | {fsig(h['sigma_both_and_refit_ci_above_0'])} | "
                     f"{fsig(h['sigma_dauc_ci_below_0'])} |")
        L += ["", "### Headline: how large (largest CV Delta AUC over all sigma, and where the baseline is informative)", "",
              "| candidate | scope | sigma | raw AUC dD / candidate | CV AUC base -> full | Delta AUC [OOF bootstrap CI] | refit Delta AUC (OOB) [CI] | quad Delta AUC [CI] | p Holm | share of gap to 1 closed |",
              "|---|---|---|---|---|---|---|---|---|---|"]

        def best_line(k, scope, b):
            q = fci(b["quad_dauc"], b["quad_dauc_lo"], b["quad_dauc_hi"]) if "quad_dauc" in b else "-"
            o = fci(b["dauc_oob_mean"], b["dauc_oob_lo"], b["dauc_oob_hi"]) if "dauc_oob_mean" in b else "-"
            return (f"| {k} | {scope} | {b['sigma']:.3g} | {b['auc_dD_raw']:.3f} / {f3(b['auc_cand_raw'])} | "
                    f"{b['cv_auc_base']:.3f} -> {b['cv_auc_full']:.3f} | {fci(b['dauc'], b['dauc_lo'], b['dauc_hi'])} | {o} | "
                    f"{q} | {fp(b['p_holm']) if not is_diag(k) else fp(b['p_primary']) + ' (raw)'} | {f3(b['gap_closed'])} |")
        for k, h in H.items():
            L.append(best_line(k, "all sigma", h["best"]))
            if "best_baseline_informative" in h and h["best_baseline_informative"]["i"] != h["best"]["i"]:
                L.append(best_line(k, "baseline informative", h["best_baseline_informative"]))
        L += ["", "C restricted to sigma >= 0.06 (rows i <= truncation index; baseline at the same sigma):", "",
              "| window | Delta AUC CI > 0 | both | largest Delta AUC [CI] at sigma | refit Delta AUC (OOB) [CI] | Holm p there |",
              "|---|---|---|---|---|---|"]
        for k, h in H.items():
            if "restricted_sigma_ge_0.06" in h:
                rr = h["restricted_sigma_ge_0.06"]; b = rr["best"]
                o = fci(b["dauc_oob_mean"], b["dauc_oob_lo"], b["dauc_oob_hi"]) if "dauc_oob_mean" in b else "-"
                L.append(f"| {k} | {fsig(rr['sigma_dauc_ci_above_0'])} | {fsig(rr['sigma_both'])} | "
                         f"{fci(b['dauc'], b['dauc_lo'], b['dauc_hi'])} at {b['sigma']:.3g} | {o} | {fp(b['p_holm'])} |")
        rf = m["reference"]
        L += ["", "Reference checks (endpoint-anchored quantities are NOT causal; for comparison with the paper):", "",
              f"* AUC of -C, paper's definition (rho = err/n1, endpoint anchor, 0.585 -> 0.002): "
              f"{rf['auc_minus_C_paper_endpoint_anchor'][0]:.3f} [{rf['auc_minus_C_paper_endpoint_anchor'][1]:.3f}, "
              f"{rf['auc_minus_C_paper_endpoint_anchor'][2]:.3f}]; medians on/off {rf['C_paper_median_on']:.2f} / {rf['C_paper_median_off']:.2f}.",
              f"* AUC of -C0.585 with the predictive anchor at sigma 0.002: {rf['auc_minus_C0.585_predictive_anchor_at_0.002'][0]:.3f}; "
              f"medians on/off {rf['C0.585_predictive_median_on_at_0.002']:.2f} / {rf['C0.585_predictive_median_off_at_0.002']:.2f}.",
              f"* AUC of dD at sigma 0.002: {rf['auc_dD_at_0.002'][0]:.3f} [{rf['auc_dD_at_0.002'][1]:.3f}, {rf['auc_dD_at_0.002'][2]:.3f}].",
              "* Predictive anchor = endpoint's nearest image (all samples), by sigma: " + ", ".join(
                  f"{s:.3g}: {v:.3f}" for s, v in zip(m["sigma"], rf["anchor_equals_endpoint_nn_frac"])), ""]
        # single-feature table
        cols = ["dD", "rhoA", "radA", "nA", "-C5.3", "-C1.9", "-C0.585", "rhoA - dD", "radA - dD", "-C0.585 - dD"]
        L += ["### Single-feature AUC (off-atom vs on-atom), 95% stratified bootstrap interval", "",
              "| sigma | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        for row in m["single_feature_auc"]:
            cells = []
            for c in cols:
                if c in row:
                    v, lo, hi = row[c]
                    cells.append(f"{v:.3f} [{lo:.3f}, {hi:.3f}]" if " - " not in c else fci(v, lo, hi))
                else:
                    cells.append("-")
            L.append(f"| {row['sigma']:.4g} | " + " | ".join(cells) + " |")
        L.append("")
        # incremental tables
        for k, rows in m["incremental"].items():
            if not rows:
                continue
            diag = is_diag(k)
            title = {"rhoA": "rhoA (relative error, predictive anchor)", "radA": "radA (radial ratio, predictive anchor)",
                     "log_rhoA": "diagnostic: log rhoA", "log_nA": "diagnostic: log nA (distance of x to the anchor)",
                     "placebo_logdD2": "diagnostic placebo: (log dD)^2"}.get(k, None)
            if title is None:
                if k.endswith("_trunc"):
                    title = f"{k[:-6]} truncated at sigma {m['trunc_sigma']:.3g}, baseline at later sigma"
                elif k.startswith("Hist"):
                    title = (f"history control {k}: trapezoid integral of log dD from sigma "
                             f"{m['window_start_sigma']['C' + k[4:]]:.3g} to sigma_i (same window as C{k[4:]})")
                elif k.endswith("|hist"):
                    title = (f"Hist{k[1:-5]} + {k[:-5]}: does the late contraction add beyond the baseline's own history "
                             f"(baseline = log dD_i and Hist{k[1:-5]})")
                else:
                    title = f"{k}: causal late contraction from sigma {m['window_start_sigma'][k]:.3g}"
            L += [f"### log dD + {title}", "",
                  "| sigma | raw AUC dD / cand | CV AUC base | CV AUC full | Delta AUC [95% CI] | quad Delta AUC [CI] | CV dLL/sample [CI] | LR chi2 | p | "
                  + ("p (raw)" if diag else "p Holm") + " | Firth chi2 | coef/SD | Spearman with log dD |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for r in rows:
                q = fci(r["quad_dauc"], r["quad_dauc_lo"], r["quad_dauc_hi"]) if "quad_dauc" in r else "-"
                chi = "F" if r["separation"] else f"{r['lr_chi2']:.1f}"
                coef = r["coef_per_sd"] if np.isfinite(r["coef_per_sd"]) else r["coef_per_sd_firth"]
                L.append(f"| {r['sigma']:.4g} | {r['auc_dD_raw']:.3f} / {f3(r['auc_cand_raw'])} | {r['cv_auc_base']:.3f} | {r['cv_auc_full']:.3f} | "
                         f"{fci(r['dauc'], r['dauc_lo'], r['dauc_hi'])} | {q} | {fci(r['cv_dll'], r['cv_dll_lo'], r['cv_dll_hi'], 4)} | "
                         f"{chi} | {fp(r['p_primary'])}{'F' if r['separation'] else ''} | "
                         f"{fp(r['p_primary']) if diag else fp(r['p_holm'])} | {r['firth_chi2']:.1f} | "
                         f"{coef:+.2f}{'F' if r['separation'] else ''} | {r['spearman_with_logdD']:+.2f} |")
            L.append("")
        ca = m["class_adjusted"]
        firth0 = {(k, r["i"]): r["firth_chi2"] for k, rows in m["incremental"].items() for r in rows}
        crow = {(r["cand"], r["i"]): r for r in ca["rows"]}
        L += ["### Class-adjusted check (Firth penalised LR, 1 df): candidate given log dD vs given log dD + class dummies", "",
              f"CV AUC of the class off-rate alone (same folds): {ca['cv_auc_class_rate']:.3f}; off-atom per class: "
              + ", ".join(str(v) for v in ca["off_per_class"]) + f" (of {ca['n_per_class'][0]} each).", "",
              "| sigma | " + " | ".join(f"{k}: chi2 -> with class (p)" for k in PRIMARY) + " |",
              "|---|" + "---|" * len(PRIMARY)]
        for i, s in enumerate(m["sigma"]):
            cells = []
            for k in PRIMARY:
                r = crow.get((k, i))
                cells.append("-" if r is None else
                             f"{firth0[(k, i)]:.1f} -> {r['firth_chi2_class']:.1f} ({fp(r['firth_p_class'])})")
            L.append(f"| {s:.4g} | " + " | ".join(cells) + " |")
        L.append("")
        L += ["### Refit check: fit on a stratified resample, Delta AUC on its out-of-bag samples", "",
              "| candidate | sigma | draws | mean Delta AUC (OOB) | 95% interval |", "|---|---|---|---|---|"]
        for r in m["refit_oob"]:
            L.append(f"| {r['cand']} | {r['sigma']:.4g} | {r['B']} | {r['dauc_oob_mean']:+.4f} | "
                     f"[{r['dauc_oob_lo']:+.4f}, {r['dauc_oob_hi']:+.4f}] |")
        L.append("")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--B", type=int, default=2000, help="bootstrap resamples of the out-of-fold predictions")
    ap.add_argument("--repeats", type=int, default=20); ap.add_argument("--folds", type=int, default=10)
    ap.add_argument("--b-refit", type=int, default=500, help="resamples of the refit (out-of-bag) check")
    ap.add_argument("--seed", type=int, default=20261121)
    ap.add_argument("--models", default=",".join(m[0] for m in MODELS))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {"meta": {"script": "scripts/paperB_incremental.py", "B": a.B, "repeats": a.repeats, "folds": a.folds,
                    "b_refit": a.b_refit, "seed": a.seed, "ratio": RATIO, "window_starts_requested": WINDOW_STARTS,
                    "sigma_stop_requested": SIGMA_STOP, "ridge_cv": RIDGE_CV, "min_class": MIN_CLASS,
                    "auc_orientation": "larger dD, rhoA, radA, nA and smaller C = off-atom; AUC = P(off > on) + ties/2",
                    "dauc_ci": "paired class-stratified bootstrap over samples of the stored out-of-fold predictions "
                               "(no refit), repeats averaged inside each resample; refit_oob = refit on the resample, "
                               "AUC on out-of-bag samples",
                    "lr_test": "in-sample ML LR chi2 (1 df); Firth penalised LR where the MLE does not exist; "
                               "Holm over the field-error family of each model",
                    "c_window": "C_i = sum_{j=j0}^{i-1} (1 - (rhoA_j + rhoA_{j+1})/2) log(sigma_j/sigma_{j+1}); uses rhoA up "
                                "to index i only",
                    "history_control": "Hist_i = sum_{j=j0}^{i-1} (log dD_j + log dD_{j+1})/2 log(sigma_j/sigma_{j+1}); "
                                       "'C|hist' tests C over (log dD_i, Hist_i)",
                    "class_check": "Firth LR of the candidate given log dD + class dummies"},
           "models": {}}
    wanted = set(a.models.split(","))
    for mi, (name, path, role) in enumerate(MODELS):
        if name not in wanted:
            continue
        print(f"== {name}: {path}", flush=True)
        m = analyse(name, path, role, a, mi)
        m["headline"] = headline(m)
        res["models"][name] = m
    (out / "incremental.json").write_text(json.dumps(clean(res), indent=1), encoding="utf-8")
    write_md(res, out / "INCREMENTAL.md")
    print(f"wrote {out / 'incremental.json'} and {out / 'INCREMENTAL.md'}")


if __name__ == "__main__":
    main()
