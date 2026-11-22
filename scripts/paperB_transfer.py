"""Paper B, analysis "transfer": out-of-sample statistics for App. app:measured-transfer
(scaled field error of the off-atom CIFAR-10 samples of the retrained DDPM U-Nets, h = 0, 4, 6).

Data (read only, nothing in the repository is modified):
  results/s10_cifar_transfer_20261108/exp3_cifar_heff_h{0,4,6}_s*/per_sample_ckpt_60000.npz
      written by scripts/exp_c_cifar_transfer.py, format documented in scripts/summarize_s10_cifar.py:
      e_learned[n, g] = (1-t)|Delta(Z_t)| = |m_hat - m*| along the learned RK4 path at grid point g
      (tau = -log(1-t) on a 0.25 grid plus the cutoffs 1-t = 1e-2, 1e-3, 1e-4); e_exact[n, g] = the
      same network error along the exact path from the same source; learned_ratio_k, learned_d1_k
      = d1/d2 and d1 of the learned state at cutoff eps_out[k]; rows = training index of the
      condition (48 conditions x 16 sources per run). h4_sK and h6_sK share seed K, hence the same
      2000-image training subset, the same 48 conditions and the same 768 Gaussian sources.
  results/s10_cifar_transfer_20261108/*/ckpt_60000.json and
  results/exp_c_cifar_transfer_20261022/*/ckpt_60000.json   (run-level fractions only; the original
      EXP-C runs kept no per-sample arrays, so no AUC can be recomputed for them).

Off-atom label (as in the paper): learned_ratio at the last cutoff (1-T = 1e-4) >= 1/3. The label is
an ENDPOINT quantity and every AUC/TPR/FPR below is computed against it.

  (1) Headline AUCs with bootstrap CIs: cluster bootstrap over the 48 conditions of each run with the
      trained networks fixed (primary), iid bootstrap over samples (sources) within each run, and a
      hierarchical bootstrap (seeds with replacement, then conditions); plus the mean of the
      per-seed AUCs with a t interval over the 3 seeds (df = 2).
  (2) The threshold rule "scaled error > c" with c chosen out of sample: on h=4, tested on h=6 and
      vice versa; leave one seed out within each h; leave one seed out at both h (the left-out seed
      is removed at both bandwidths, since h4_sK and h6_sK share conditions and sources). Selection
      rules fixed in advance: Youden J, training TPR >= 0.95, training FPR <= 0.10; the paper's c = 4
      for reference. CIs bootstrap the whole procedure (conditions resampled in training and test
      runs, threshold re-selected in every replicate).
  (3) AUC of e_learned(t) at every grid t (information available at t only: the state x_t, the
      network and m*(x_t)), pooled per h and per seed, the within-condition AUC (only pairs from the
      same condition), and the earliest t with AUC >= 0.90 / 0.95 / 0.97 on the grid and interpolated
      linearly in tau, with bootstrap CIs of the whole selection.
  (4) A table of which statistics use endpoint information.

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_transfer
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import re
import time

import numpy as np

S10 = pathlib.Path("results/s10_cifar_transfer_20261108")
EXPC = pathlib.Path("results/exp_c_cifar_transfer_20261022")
OUT = pathlib.Path("results/paperB_20261121/transfer")
CKPT = 60000
RATIO = 1.0 / 3.0
B = 2000                                   # bootstrap replicates
SEED = 20261121
LEVELS = (0.90, 0.95, 0.97)
RULE_TAUS = (0.5, 0.75, 1.0, 2.0, "final")  # times at which the threshold rule is evaluated
RULES = ("youden", "tpr95", "fpr10", "fixed4")
FIXED_C = (3.0, 4.0, 5.0)
CHUNK = 500                                 # replicates per chunk in threshold selection
T975 = {1: 12.706204736, 2: 4.302652730, 3: 3.182446305, 4: 2.776445105, 5: 2.570581836}


# ----------------------------------------------------------------------------------------------
# data
def load_s10():
    runs = []
    for f in sorted(S10.glob(f"*/per_sample_ckpt_{CKPT}.npz")):
        m = re.search(r"_h(\d+)_s(\d+)$", f.parent.name)
        z = np.load(f)
        k = len(z["eps_out"]) - 1
        ratio = z[f"learned_ratio_{k}"].astype(np.float64)
        d1 = z[f"learned_d1_{k}"].astype(np.float64)
        _, cond = np.unique(z["rows"], return_inverse=True)
        js = json.loads((f.parent / f"ckpt_{CKPT}.json").read_text(encoding="utf-8"))
        runs.append(dict(
            name=f.parent.name, file=f.as_posix(), json_file=(f.parent / f"ckpt_{CKPT}.json").as_posix(),
            h=int(m.group(1)), seed=int(m.group(2)), rows=z["rows"], cond=cond.astype(np.int64),
            tau=z["grid_tau"].astype(np.float64), eL=z["e_learned"].astype(np.float64),
            eX=z["e_exact"].astype(np.float64), ratio=ratio, d1=d1, d2=d1 / ratio, off=ratio >= RATIO,
            off_by_cutoff=[z[f"learned_ratio_{i}"] >= RATIO for i in range(k + 1)],
            eps_out=z["eps_out"].astype(np.float64), nnL=z[f"learned_nn_{k}"], nnX=z[f"exact_nn_{k}"],
            exact_off=z[f"exact_ratio_{k}"] >= RATIO,
            json_off=1.0 - js["cutoffs"][k]["learned"]["on_atom_run"]))
    return runs


def pooled(rs):
    return dict(eL=np.concatenate([r["eL"] for r in rs]), eX=np.concatenate([r["eX"] for r in rs]),
                off=np.concatenate([r["off"] for r in rs]), d1=np.concatenate([r["d1"] for r in rs]),
                d2=np.concatenate([r["d2"] for r in rs]))


# ----------------------------------------------------------------------------------------------
# statistics
def ref_auc(pos, neg):
    """Copied from scripts/summarize_s10_cifar.py (reference for the self-test)."""
    x = np.concatenate([pos, neg]); r = np.empty(len(x)); order = x.argsort(kind="mergesort")
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_w(score, pos, W=None):
    """Weighted Mann-Whitney AUC, P(s_pos > s_neg) + P(s_pos = s_neg)/2, for every row of the
    weight matrix W (B, n); W = None gives the unweighted AUC as a float."""
    s = np.asarray(score, dtype=np.float64); pos = np.asarray(pos, dtype=bool)
    single = W is None
    W = np.ones((1, len(s))) if single else np.asarray(W, dtype=np.float64)
    order = np.argsort(s, kind="mergesort")
    ss, ps = s[order], pos[order]
    Ws = W[:, order]
    wp = Ws * ps
    wn = Ws * ~ps
    first = np.r_[True, ss[1:] != ss[:-1]]
    gid = np.cumsum(first) - 1
    starts = np.flatnonzero(first); ends = np.r_[starts[1:], len(ss)]
    cum = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(wn, axis=1)], axis=1)
    below = cum[:, starts]; eq = cum[:, ends] - below
    num = (wp * (below[:, gid] + 0.5 * eq[:, gid])).sum(1)
    den = wp.sum(1) * wn.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        a = np.where(den > 0, num / den, np.nan)
    return float(a[0]) if single else a


def within_parts(score, pos, gid, C):
    """Per-condition Mann-Whitney numerator U_c and pair count P_c (pairs inside condition c)."""
    U = np.zeros(C); PN = np.zeros(C)
    for c in range(C):
        m = gid == c
        sp, sn = score[m & pos], score[m & ~pos]
        if len(sp) and len(sn):
            U[c] = (sp[:, None] > sn[None]).sum() + 0.5 * (sp[:, None] == sn[None]).sum()
            PN[c] = len(sp) * len(sn)
    return U, PN


def cond_counts(rs, nb, rng, kind):
    """(nb, C_total) multiplicities of the conditions of the pooled runs and the sample -> global
    condition map. kind 'cluster': conditions resampled within every run (networks fixed);
    'hier': runs (seeds) resampled with replacement, then conditions within every drawn run."""
    offs = np.cumsum([0] + [int(r["cond"].max()) + 1 for r in rs])
    gid = np.concatenate([r["cond"] + o for r, o in zip(rs, offs[:-1])])
    R = len(rs)
    if kind == "cluster":
        mult = np.ones((nb, R), dtype=np.int64)
    elif kind == "hier":
        draws = rng.integers(0, R, size=(nb, R))
        mult = np.stack([(draws == r).sum(1) for r in range(R)], 1)
    else:
        raise ValueError(kind)
    cnt = []
    for r, run in enumerate(rs):
        C = int(run["cond"].max()) + 1
        cnt.append(rng.multinomial(mult[:, r] * C, np.full(C, 1.0 / C)))
    return np.concatenate(cnt, 1).astype(np.float64), gid


def iid_weights(rs, nb, rng):
    """Samples (sources) resampled with replacement within every run, ignoring the conditions."""
    return np.concatenate([rng.multinomial(len(r["off"]), np.full(len(r["off"]), 1.0 / len(r["off"])), size=nb)
                           for r in rs], 1).astype(np.float64)


def pci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, dtype=np.float64); x = x[np.isfinite(x)]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))] if len(x) else [float("nan")] * 2


def t_interval(vals):
    v = np.asarray(vals, dtype=np.float64); n = len(v)
    m, s1 = float(v.mean()), float(v.std(ddof=1))
    half = T975[n - 1] * s1 / math.sqrt(n)
    return dict(values=[float(a) for a in v], mean=m, sd_ddof1=s1, sd_ddof0=float(v.std()),
                t95=[m - half, m + half], df=n - 1)


def wmean(y, W):
    return (W @ y.astype(np.float64)) / W.sum(1)


def wquantile(x, W, q):
    """Weighted quantile (lower) of x for every row of W."""
    o = np.argsort(x, kind="mergesort"); xs = x[o]; cw = np.cumsum(W[:, o], 1)
    k = np.argmax(cw >= q * cw[:, -1:], 1)
    return xs[k]


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(np.float64); rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def icc_binary(y, gid):
    """One-way ANOVA intra-class correlation of a 0/1 label within conditions (balanced groups)."""
    groups = [y[gid == c].astype(np.float64) for c in np.unique(gid)]
    k, m, g = len(groups), len(groups[0]), y.mean()
    msb = m * sum((x.mean() - g) ** 2 for x in groups) / (k - 1)
    msw = sum(((x - x.mean()) ** 2).sum() for x in groups) / (k * (m - 1))
    return float((msb - msw) / (msb + (m - 1) * msw)) if (msb + (m - 1) * msw) > 0 else float("nan")


def crossing(A, tau, level):
    """A (nb, T) AUC on the tau grid. Returns the first grid index with A >= level (-1: never), the
    crossing tau interpolated linearly between that grid point and the one before it (nan: never;
    tau[0] when already crossed at the first grid point), and the first index from which A stays
    >= level up to the end (T: never)."""
    A = np.atleast_2d(A); nb, T = A.shape
    ok = A >= level
    has = ok.any(1)
    j = np.where(has, np.argmax(ok, 1), -1)
    jj = np.clip(j, 0, None); jm = np.clip(j - 1, 0, None); ar = np.arange(nb)
    a0, a1 = A[ar, jm], A[ar, jj]
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(j > 0, (level - a0) / (a1 - a0), 0.0)
    ts = np.where(j > 0, tau[jm] + frac * (tau[jj] - tau[jm]), tau[0])
    ts = np.where(has, ts, np.nan)
    bad = ~ok
    last_bad = np.where(bad.any(1), T - 1 - np.argmax(bad[:, ::-1], 1), -1)
    return j, ts, last_bad + 1


def to_t(tau):
    return 1.0 - np.exp(-np.asarray(tau, dtype=np.float64))


# ----------------------------------------------------------------------------------------------
# threshold rules
def select_thresholds(s, y, W, rule):
    """Threshold c chosen on (s, y) with sample weights W (nb, n); positive means s > c.
    youden: argmax TPR - FPR; tpr95: the largest c with training TPR >= 0.95; fpr10: the smallest c
    with training FPR <= 0.10; fixed4: c = 4. Candidates are midpoints between sorted scores."""
    if rule == "fixed4":
        return np.full(W.shape[0], 4.0)
    order = np.argsort(s, kind="mergesort"); ss = s[order]; ys = y[order]
    cand = np.r_[ss[0] - 1e-9, 0.5 * (ss[1:] + ss[:-1]), ss[-1] + 1e-9]
    out = np.empty(W.shape[0])
    for a in range(0, W.shape[0], CHUNK):
        Ws = W[a:a + CHUNK][:, order]
        z = np.zeros((len(Ws), 1))
        TP = np.concatenate([np.cumsum((Ws * ys)[:, ::-1], 1)[:, ::-1], z], 1)
        FP = np.concatenate([np.cumsum((Ws * ~ys)[:, ::-1], 1)[:, ::-1], z], 1)
        tpr, fpr = TP / TP[:, :1], FP / FP[:, :1]
        if rule == "youden":
            k = np.argmax(tpr - fpr, 1)
        elif rule == "tpr95":
            k = (tpr >= 0.95 - 1e-12).sum(1) - 1
        elif rule == "fpr10":
            k = (fpr > 0.10 + 1e-12).sum(1)
        else:
            raise ValueError(rule)
        out[a:a + CHUNK] = cand[k]
    return out


def rate_counts(s, y, W, c):
    above = s[None, :] > np.asarray(c)[:, None]
    yf = y.astype(np.float64)
    return ((W * (above & y)).sum(1), W @ yf, (W * (above & ~y)).sum(1), W @ (1 - yf))


# ----------------------------------------------------------------------------------------------
def main():
    t_start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    runs = load_s10()
    H = {h: [r for r in runs if r["h"] == h] for h in sorted({r["h"] for r in runs})}
    tau = runs[0]["tau"]; tg = to_t(tau); T = len(tau)
    assert all(np.allclose(r["tau"], tau) for r in runs)
    J_FINAL = T - 1
    jt = lambda x: int(np.argmin(np.abs(tau - x)))  # noqa: E731
    J053, J063, J071 = jt(0.75), jt(1.0), jt(1.25)
    LATE = np.flatnonzero(tg >= 0.70)
    files = sorted(r["file"] for r in runs)
    res = {"meta": {
        "script": "scripts/paperB_transfer.py", "sources_per_sample": files,
        "sources_run_json": sorted(r["json_file"] for r in runs),
        "sources_expc_json": sorted(p.as_posix() for p in EXPC.glob(f"*/ckpt_{CKPT}.json")),
        "B": B, "rng_seed": SEED, "off_atom_label": "learned d1/d2 >= 1/3 at the last cutoff 1-T = 1e-4 (endpoint)",
        "score": "e_learned(t) = (1-t)|Delta(Z_t,t)| = |m_hat(Z_t) - m*(Z_t)| along the learned RK4 path",
        "grid_t": [float(v) for v in tg], "grid_tau": [float(v) for v in tau],
        "bootstrap": {"cluster": "48 conditions resampled with replacement within each run; trained networks fixed (primary)",
                      "iid": "samples (sources) resampled with replacement within each run, ignoring conditions",
                      "hier": "seeds resampled with replacement, then conditions within each drawn seed (3 seeds: crude)"},
        "ci": "percentile 95% intervals; seed t-intervals use t(0.975, df=2) = 4.303",
    }}

    # self-test of the weighted AUC against the reference implementation
    P4 = pooled(H[4])
    a_ref = ref_auc(P4["eL"][P4["off"], -1], P4["eL"][~P4["off"], -1])
    a_new = auc_w(P4["eL"][:, -1], P4["off"])
    rng0 = np.random.default_rng(0)
    xs = rng0.integers(0, 5, 300).astype(float); ys = rng0.random(300) < 0.3
    assert abs(a_ref - a_new) < 1e-12 and abs(ref_auc(xs[ys], xs[~ys]) - auc_w(xs, ys)) < 1e-12
    res["meta"]["auc_selftest"] = {"pooled_h4_final_ref": a_ref, "pooled_h4_final_new": a_new}

    # ------------------------------------------------------------------ inventory and bookkeeping
    rngI = np.random.default_rng([SEED, 1])
    inv = []
    for r in runs:
        cc, gid = cond_counts([r], B, rngI, "cluster"); W = cc[:, gid]
        on = ~r["off"]; ef = r["eL"][:, -1]
        same = r["nnL"] == r["nnX"]
        per_cond_off = np.bincount(r["cond"], weights=r["off"].astype(float)).astype(int)
        rec = {"run": r["name"], "file": r["file"], "h": r["h"], "seed": r["seed"], "n": int(len(on)),
               "n_conditions": int(r["cond"].max() + 1),
               "sources_per_condition": sorted(set(np.bincount(r["cond"]).tolist())),
               "n_off": int(r["off"].sum()), "off_frac": float(r["off"].mean()),
               "off_frac_ci_cluster": pci(wmean(r["off"], W)),
               "off_frac_from_run_json": float(r["json_off"]),
               "icc_off_within_condition": icc_binary(r["off"], r["cond"]),
               "conditions_without_off": int((per_cond_off == 0).sum()),
               "max_off_in_a_condition": int(per_cond_off.max()),
               "label_agreement_cutoff_1e-2_vs_1e-4": float((r["off_by_cutoff"][0] == r["off"]).mean()),
               "max_rel_diff_final_e_vs_d1": float(np.max(np.abs(r["d1"] - ef) / ef)),
               "exact_off_frac": float(r["exact_off"].mean()), "exact_path_final_e_max": float(r["eX"][:, -1].max()),
               "median_final_e_on": float(np.median(ef[on])) if on.any() else None,
               "median_final_e_off": float(np.median(ef[r["off"]])) if r["off"].any() else None,
               "median_final_e_on_ci": pci(wquantile_masked(ef, on, W)) if on.any() else None,
               "median_final_e_off_ci": pci(wquantile_masked(ef, r["off"], W)) if r["off"].any() else None,
               "median_e_t0632_on": float(np.median(r["eL"][on, J063])) if on.any() else None,
               "median_e_t0632_off": float(np.median(r["eL"][r["off"], J063])) if r["off"].any() else None,
               "median_d2_on": float(np.median(r["d2"][on])) if on.any() else None,
               "median_d2_off": float(np.median(r["d2"][r["off"]])) if r["off"].any() else None,
               "same_image_as_exact_on": float(same[on].mean()) if on.any() else None,
               "same_image_as_exact_on_ci": pci((W @ (same & on).astype(np.float64)) / (W @ on.astype(np.float64)))
               if on.any() else None,
               "rule_e_final_gt4_agrees_with_label": float(((ef > 4) == r["off"]).mean())}
        inv.append(rec)
    res["inventory"] = inv

    # pairing across bandwidths: h4_sK and h6_sK share the training subset, conditions and sources
    pairing = []
    for s in sorted({r["seed"] for r in H[4]}):
        a = next(r for r in H[4] if r["seed"] == s); b = next(r for r in H[6] if r["seed"] == s)
        assert np.array_equal(a["rows"], b["rows"])
        o4, o6 = a["off"], b["off"]
        phi = float(np.corrcoef(o4.astype(float), o6.astype(float))[0, 1])
        pairing.append({"seed": s, "same_rows": True, "p_off6_given_off4": float(o6[o4].mean()),
                        "p_off6_given_on4": float(o6[~o4].mean()), "phi": phi,
                        "spearman_final_e": spearman(a["eL"][:, -1], b["eL"][:, -1]),
                        "same_exact_endpoint_image": float((a["nnX"] == b["nnX"]).mean())})
    res["pairing_h4_h6_same_seed"] = pairing

    # ------------------------------------------------------------------ AUC curves (1) and (3)
    curves, perseed, within, cprior = {}, {}, {}, {}
    for h in (4, 6):
        rs = H[h]; P = pooled(rs)
        rng = np.random.default_rng([SEED, 10 + h])
        cc, gid = cond_counts(rs, B, rng, "cluster"); Wc = cc[:, gid]
        hc, _ = cond_counts(rs, B, rng, "hier"); Wh = hc[:, gid]
        Wi = iid_weights(rs, B, rng)
        C = int(gid.max()) + 1
        L = {"point": np.array([auc_w(P["eL"][:, j], P["off"]) for j in range(T)])}
        X = {"point": np.array([auc_w(P["eX"][:, j], P["off"]) for j in range(T)])}
        for kind, W in (("cluster", Wc), ("hier", Wh), ("iid", Wi)):
            L[kind] = np.stack([auc_w(P["eL"][:, j], P["off"], W) for j in range(T)], 1)
        for kind, W in (("cluster", Wc), ("hier", Wh)):
            X[kind] = np.stack([auc_w(P["eX"][:, j], P["off"], W) for j in range(T)], 1)
        # within-condition AUC: only (off, on) pairs from the same condition of the same run
        wpt, wcl = np.zeros(T), np.zeros((B, T))
        for j in range(T):
            U, PN = within_parts(P["eL"][:, j], P["off"], gid, C)
            wpt[j] = U.sum() / PN.sum(); wcl[:, j] = (cc @ U) / (cc @ PN)
        within[h] = {"point": wpt, "cluster": wcl,
                     "conditions_with_both_groups": int(sum(1 for c in range(C)
                                                            if P["off"][gid == c].any() and (~P["off"][gid == c]).any()))}
        # condition prior (reference only): share of the OTHER 15 sources of the same condition that end off-atom
        n_c = np.bincount(gid); k_c = np.bincount(gid, weights=P["off"].astype(float))
        q = (k_c[gid] - P["off"]) / (n_c[gid] - 1)
        cprior[h] = {"point": auc_w(q, P["off"]), "cluster_ci": pci(auc_w(q, P["off"], Wc))}
        curves[h] = {"L": L, "X": X, "n": int(len(P["off"])), "n_off": int(P["off"].sum()),
                     "spearman_e_t_vs_final": [spearman(P["eL"][:, j], P["eL"][:, -1]) for j in range(T)],
                     "auc_d1": auc_w(P["d1"], P["off"]), "auc_d2": auc_w(P["d2"], P["off"]),
                     "auc_final_e_over_d2": auc_w(P["eL"][:, -1] / P["d2"], P["off"]),
                     "icc_off": icc_binary(P["off"], gid)}
        for r in rs:
            rr = np.random.default_rng([SEED, 100 + 10 * h + r["seed"]])
            c1, g1 = cond_counts([r], B, rr, "cluster"); W1 = c1[:, g1]
            perseed[r["name"]] = {
                "point": np.array([auc_w(r["eL"][:, j], r["off"]) for j in range(T)]),
                "cluster": np.stack([auc_w(r["eL"][:, j], r["off"], W1) for j in range(T)], 1),
                "X_point": np.array([auc_w(r["eX"][:, j], r["off"]) for j in range(T)]),
                "X_cluster": np.stack([auc_w(r["eX"][:, j], r["off"], W1) for j in range(T)], 1)}
    print(f"AUC curves done {time.time() - t_start:.0f}s", flush=True)

    def item(h, A, j=None, fn=None):
        """point and CIs of an AUC functional (one grid index j, or fn over the curve)."""
        f = (lambda M: M[..., j]) if fn is None else fn
        d = {"point": float(f(A["point"]))}
        for kind in ("cluster", "iid", "hier"):
            if kind in A:
                d[f"ci_{kind}"] = pci(f(A[kind]))
        return d

    headline = {}
    for h in (4, 6):
        L, X = curves[h]["L"], curves[h]["X"]
        names = [r["name"] for r in H[h]]
        ps = lambda key, j: t_interval([perseed[n][key][j] for n in names])  # noqa: E731
        late_min = lambda M: np.min(M[..., LATE], axis=-1)  # noqa: E731
        late_max = lambda M: np.max(M[..., LATE], axis=-1)  # noqa: E731
        hl = {
            "final_learned": {**item(h, L, J_FINAL), "per_seed": {n: {"point": float(perseed[n]["point"][J_FINAL]),
                                                                     "ci_cluster": pci(perseed[n]["cluster"][:, J_FINAL])} for n in names},
                              "seed_mean_t": ps("point", J_FINAL)},
            "t0528_learned": {**item(h, L, J053), "per_seed": {n: {"point": float(perseed[n]["point"][J053]),
                                                                  "ci_cluster": pci(perseed[n]["cluster"][:, J053])} for n in names},
                              "seed_mean_t": ps("point", J053), "t": float(tg[J053])},
            "t0632_learned": {**item(h, L, J063), "per_seed": {n: {"point": float(perseed[n]["point"][J063]),
                                                                  "ci_cluster": pci(perseed[n]["cluster"][:, J063])} for n in names},
                              "seed_mean_t": ps("point", J063), "t": float(tg[J063])},
            "late_learned_min": item(h, L, fn=late_min), "late_learned_max": item(h, L, fn=late_max),
            "t0713_exact_path": {**item(h, X, J071), "t": float(tg[J071]),
                                 "per_seed": {n: float(perseed[n]["X_point"][J071]) for n in names}},
            "final_exact_path": {**item(h, X, J_FINAL),
                                 "per_seed": {n: float(perseed[n]["X_point"][J_FINAL]) for n in names}},
            "late_exact_path_min": item(h, X, fn=late_min), "late_exact_path_max": item(h, X, fn=late_max),
            "late_exact_path_ci_excludes_0.5_at_any_late_t": bool(np.any(
                np.percentile(X["cluster"][:, LATE], 2.5, axis=0) > 0.5)),
            "late_exact_path_ci_excludes_0.5_at_all_late_t": bool(np.all(
                np.percentile(X["cluster"][:, LATE], 2.5, axis=0) > 0.5)),
            "within_condition_final": {"point": float(within[h]["point"][J_FINAL]), "ci_cluster": pci(within[h]["cluster"][:, J_FINAL])},
            "within_condition_t0528": {"point": float(within[h]["point"][J053]), "ci_cluster": pci(within[h]["cluster"][:, J053])},
            "within_condition_t0632": {"point": float(within[h]["point"][J063]), "ci_cluster": pci(within[h]["cluster"][:, J063])},
            "condition_prior_baseline": cprior[h],
            "auc_d1_final": curves[h]["auc_d1"], "auc_d2_final": curves[h]["auc_d2"],
            "auc_final_e_over_d2": curves[h]["auc_final_e_over_d2"], "icc_off_pooled": curves[h]["icc_off"],
            "n": curves[h]["n"], "n_off": curves[h]["n_off"],
        }
        headline[f"h{h}"] = hl
    res["headline_auc"] = headline

    # AUC as a function of t
    avt = []
    for j in range(T):
        row = {"j": j, "tau": float(tau[j]), "t": float(tg[j])}
        for h in (4, 6):
            L, X = curves[h]["L"], curves[h]["X"]
            row[f"h{h}_auc"] = float(L["point"][j]); row[f"h{h}_ci_cluster"] = pci(L["cluster"][:, j])
            row[f"h{h}_ci_hier"] = pci(L["hier"][:, j]); row[f"h{h}_ci_iid"] = pci(L["iid"][:, j])
            row[f"h{h}_within_cond"] = float(within[h]["point"][j]); row[f"h{h}_within_cond_ci"] = pci(within[h]["cluster"][:, j])
            row[f"h{h}_exact_path_auc"] = float(X["point"][j]); row[f"h{h}_exact_path_ci_cluster"] = pci(X["cluster"][:, j])
            row[f"h{h}_spearman_e_t_vs_final"] = curves[h]["spearman_e_t_vs_final"][j]
            for r in H[h]:
                row[f"{r['name']}_auc"] = float(perseed[r["name"]]["point"][j])
                row[f"{r['name']}_ci_cluster"] = pci(perseed[r["name"]]["cluster"][:, j])
        avt.append(row)
    res["auc_vs_t"] = avt

    # earliest t with AUC >= level (score at t only)
    early = {}
    for level in LEVELS:
        for h in (4, 6):
            L = curves[h]["L"]
            jp, tsp, stp = crossing(L["point"], tau, level)
            d = {"grid_first_t": float(tg[jp[0]]) if jp[0] >= 0 else None,
                 "interp_t": float(to_t(tsp[0])) if np.isfinite(tsp[0]) else None,
                 "stays_from_t": float(tg[stp[0]]) if stp[0] < T else None}
            for kind in ("cluster", "hier"):
                jb, tsb, stb = crossing(L[kind], tau, level)
                tb = to_t(tsb)
                vals, cnts = np.unique(jb, return_counts=True)
                d[f"{kind}_interp_t_ci"] = pci(tb)
                d[f"{kind}_never_frac"] = float(np.mean(~np.isfinite(tsb)))
                d[f"{kind}_grid_first_t_dist"] = {("never" if v < 0 else f"{tg[v]:.3f}"): float(c / len(jb))
                                                  for v, c in zip(vals, cnts)}
                d[f"{kind}_grid_first_t_ci"] = pci(np.where(jb >= 0, tg[np.clip(jb, 0, None)], np.nan))
                d[f"{kind}_stays_from_t_ci"] = pci(np.where(stb < T, tg[np.clip(stb, 0, T - 1)], np.nan))
            lo = np.percentile(L["cluster"], 2.5, axis=0)
            jl = np.flatnonzero(lo >= level)
            d["first_t_with_lower_ci_cluster_ge_level"] = float(tg[jl[0]]) if len(jl) else None
            per = {}
            for r in H[h]:
                pp = perseed[r["name"]]
                j1, t1, _ = crossing(pp["point"], tau, level)
                jb, tsb, _ = crossing(pp["cluster"], tau, level)
                per[r["name"]] = {"grid_first_t": float(tg[j1[0]]) if j1[0] >= 0 else None,
                                  "interp_t": float(to_t(t1[0])) if np.isfinite(t1[0]) else None,
                                  "interp_t_ci_cluster": pci(to_t(tsb)), "never_frac": float(np.mean(~np.isfinite(tsb)))}
            d["per_seed"] = per
            early[f"h{h}_level{level:.2f}"] = d
    res["earliest_t"] = early
    print(f"earliest t done {time.time() - t_start:.0f}s", flush=True)

    # ------------------------------------------------------------------ threshold rules (2)
    R6 = H[4] + H[6]
    rngT = np.random.default_rng([SEED, 7])
    Wrun = {}
    for r in R6 + H.get(0, []):
        c1, g1 = cond_counts([r], B, rngT, "cluster"); Wrun[r["name"]] = c1[:, g1]
    seeds = sorted({r["seed"] for r in R6})
    schemes = {
        "in_sample_h4": [(H[4], H[4])], "in_sample_h6": [(H[6], H[6])],
        "h4_to_h6": [(H[4], H[6])], "h6_to_h4": [(H[6], H[4])],
        "loso_within_h4": [([x for x in H[4] if x is not r], [r]) for r in H[4]],
        "loso_within_h6": [([x for x in H[6] if x is not r], [r]) for r in H[6]],
        "loso_both_h_test_h4": [([x for x in R6 if x["seed"] != r["seed"]], [r]) for r in H[4]],
        "loso_both_h_test_h6": [([x for x in R6 if x["seed"] != r["seed"]], [r]) for r in H[6]],
    }
    cat = lambda rs, key, j: np.concatenate([r[key][:, j] for r in rs])  # noqa: E731
    catb = lambda rs, key: np.concatenate([r[key] for r in rs])  # noqa: E731
    catW = lambda rs: np.concatenate([Wrun[r["name"]] for r in rs], 1)  # noqa: E731
    thr = []
    for tk in RULE_TAUS:
        j = J_FINAL if tk == "final" else jt(tk)
        for sname, folds in schemes.items():
            for rule in RULES:
                acc_pt = np.zeros(4); acc_b = np.zeros((4, B)); fold_rows = []
                for tr, te in folds:
                    s_tr, y_tr = cat(tr, "eL", j), catb(tr, "off")
                    s_te, y_te = cat(te, "eL", j), catb(te, "off")
                    c_pt = select_thresholds(s_tr, y_tr, np.ones((1, len(s_tr))), rule)
                    c_b = select_thresholds(s_tr, y_tr, catW(tr), rule)
                    cp = np.array([v[0] for v in rate_counts(s_te, y_te, np.ones((1, len(s_te))), c_pt)])
                    cb = np.stack(rate_counts(s_te, y_te, catW(te), c_b))
                    acc_pt += cp; acc_b += cb
                    trp = np.array([v[0] for v in rate_counts(s_tr, y_tr, np.ones((1, len(s_tr))), c_pt)])
                    fold_rows.append({"train": [r["name"] for r in tr], "test": [r["name"] for r in te],
                                      "threshold": float(c_pt[0]), "threshold_ci": pci(c_b),
                                      "train_tpr": float(trp[0] / trp[1]), "train_fpr": float(trp[2] / trp[3]),
                                      "test_tpr": float(cp[0] / cp[1]), "test_fpr": float(cp[2] / cp[3])})
                thr.append({"time": "final" if tk == "final" else f"tau={tk}", "t": float(tg[j]), "scheme": sname,
                            "rule": rule, "tpr": float(acc_pt[0] / acc_pt[1]), "tpr_ci": pci(acc_b[0] / acc_b[1]),
                            "fpr": float(acc_pt[2] / acc_pt[3]), "fpr_ci": pci(acc_b[2] / acc_b[3]),
                            "n_test_off": int(acc_pt[1]), "n_test_on": int(acc_pt[3]), "folds": fold_rows,
                            "uses_test_labels_for_threshold": sname.startswith("in_sample") or rule == "fixed4"})
    res["threshold_rules"] = thr
    print(f"threshold rules done {time.time() - t_start:.0f}s", flush=True)

    # fixed thresholds c = 3, 4, 5 (in-sample; c = 4 is the paper's), per h and per seed, and h = 0
    fixed = []
    for tk in RULE_TAUS:
        j = J_FINAL if tk == "final" else jt(tk)
        for c in FIXED_C:
            for h in (4, 6):
                rs = H[h]; s, y = cat(rs, "eL", j), catb(rs, "off")
                rngF = np.random.default_rng([SEED, 20 + h])
                hc, gid = cond_counts(rs, B, rngF, "hier"); Wh = hc[:, gid]
                Wc = catW(rs)
                pt = [v[0] for v in rate_counts(s, y, np.ones((1, len(s))), [c])]
                cl, hi = rate_counts(s, y, Wc, np.full(B, c)), rate_counts(s, y, Wh, np.full(B, c))
                rec = {"time": "final" if tk == "final" else f"tau={tk}", "t": float(tg[j]), "c": c, "h": h,
                       "tpr": float(pt[0] / pt[1]), "fpr": float(pt[2] / pt[3]),
                       "tpr_ci_cluster": pci(cl[0] / cl[1]), "fpr_ci_cluster": pci(cl[2] / cl[3]),
                       "tpr_ci_hier": pci(hi[0] / hi[1]), "fpr_ci_hier": pci(hi[2] / hi[3]), "per_seed": {}}
                for r in rs:
                    s1, y1 = r["eL"][:, j], r["off"]
                    p1 = [v[0] for v in rate_counts(s1, y1, np.ones((1, len(s1))), [c])]
                    b1 = rate_counts(s1, y1, Wrun[r["name"]], np.full(B, c))
                    rec["per_seed"][r["name"]] = {"tpr": float(p1[0] / p1[1]), "fpr": float(p1[2] / p1[3]),
                                                  "tpr_ci": pci(b1[0] / b1[1]), "fpr_ci": pci(b1[2] / b1[3])}
                fixed.append(rec)
            for r in H.get(0, []):
                s0 = r["eL"][:, j]
                fixed.append({"time": "final" if tk == "final" else f"tau={tk}", "t": float(tg[j]), "c": c, "h": 0,
                              "run": r["name"], "flag_rate_all_on_atom": float((s0 > c).mean()),
                              "flag_rate_ci_cluster": pci(wmean(s0 > c, Wrun[r["name"]]))})
    res["fixed_thresholds"] = fixed

    # ------------------------------------------------------------------ EXP-C and S10 run-level fractions
    def fractions(root):
        out = {}
        for f in sorted(root.glob(f"*/ckpt_{CKPT}.json")):
            js = json.loads(f.read_text(encoding="utf-8"))
            h = int(js["h"]); d = out.setdefault(h, {"runs": [], "euler50_1e-3": [], "rk4_1e-3": [], "rk4_1e-4": [],
                                                       "rk4_1e-4_50k": [], "exact_1e-4": [], "same_atom_1e-3": []})
            d["runs"].append(f.parent.name)
            d["euler50_1e-3"].append(1 - js["euler50_T1e-3"]["on_atom_run"])
            d["rk4_1e-3"].append(1 - js["cutoffs"][1]["learned"]["on_atom_run"])
            d["rk4_1e-4"].append(1 - js["cutoffs"][2]["learned"]["on_atom_run"])
            d["rk4_1e-4_50k"].append(1 - js["cutoffs"][2]["learned"]["on_atom_50k"])
            d["exact_1e-4"].append(1 - js["cutoffs"][2]["exact"]["on_atom_run"])
            d["same_atom_1e-3"].append(js["cutoffs"][1]["same_atom_learned_exact"])
        summ = {}
        for h, d in sorted(out.items()):
            summ[f"h{h}"] = {"runs": d["runs"]}
            for k, v in d.items():
                if k != "runs":
                    summ[f"h{h}"][k] = t_interval(v) if len(v) > 1 else {"values": v}
        return summ
    res["run_level_fractions"] = {"exp_c_original_runs": {"source": (EXPC / "*" / f"ckpt_{CKPT}.json").as_posix(),
                                                          "by_h": fractions(EXPC)},
                                  "s10_retrained_runs": {"source": (S10 / "*" / f"ckpt_{CKPT}.json").as_posix(),
                                                         "by_h": fractions(S10)}}

    # ------------------------------------------------------------------ (4) endpoint information
    res["endpoint_information"] = [
        {"statistic": "off-atom label (learned d1/d2 >= 1/3 at 1-T = 1e-4)", "endpoint_info": "yes (it is the target)",
         "note": "every AUC, TPR and FPR is computed against it; unavoidable for evaluation"},
        {"statistic": "final scaled error e(t = 0.9999) and its AUC (0.985 / 0.977)", "endpoint_info": "yes",
         "note": "equals the endpoint's d1 within 0.2% for every sample; the label is d1/d2, so this AUC is the AUC of the label's numerator (bookkeeping, as the paper says)"},
        {"statistic": "rule 'final scaled error > 4' (94/95% TPR, 7/12% FPR)", "endpoint_info": "yes, and the threshold was chosen in sample",
         "note": "it is the rule 'd1 > 4' on the endpoint; it is not an early warning"},
        {"statistic": "e_learned(t) for grid t < 1 and its AUC", "endpoint_info": "no (score); label yes",
         "note": "the score uses only x_t, the network and m*(x_t) (training set and bandwidth); an online audit statistic, though it needs a sum over the training set at every step"},
        {"statistic": "e_exact(t) (network error on the exact path) and its AUC", "endpoint_info": "no (score); label yes",
         "note": "needs the exact trajectory from the same source, integrated separately; no learned-endpoint information"},
        {"statistic": "thresholds selected on other runs (h4->h6, h6->h4, leave-one-seed-out)", "endpoint_info": "labels of the training runs only",
         "note": "out of sample for the test runs; h4->h6 and h6->h4 share conditions and sources seed by seed, leave-one-seed-out at both h does not"},
        {"statistic": "earliest t with AUC >= 0.95", "endpoint_info": "score at t only; label yes; t selected post hoc",
         "note": "the selection over t is made on the evaluated data; the bootstrap CI repeats the selection in every replicate"},
        {"statistic": "within-condition AUC", "endpoint_info": "no (score); label yes", "note": "removes between-condition differences"},
        {"statistic": "condition-prior baseline (share of the other 15 sources of the condition that end off-atom)",
         "endpoint_info": "yes (endpoint labels of other samples)", "note": "reference for how much is predictable from the condition alone; not available for a new condition"},
        {"statistic": "final e / d2 of the endpoint", "endpoint_info": "yes", "note": "reproduces the label by construction"},
        {"statistic": "off-atom fractions; same training image as the exact field", "endpoint_info": "yes", "note": "endpoint descriptors"},
    ]

    # ------------------------------------------------------------------ claims check
    hl4, hl6 = headline["h4"], headline["h6"]
    f4 = next(x for x in fixed if x["time"] == "final" and x["c"] == 4.0 and x["h"] == 4)
    f6 = next(x for x in fixed if x["time"] == "final" and x["c"] == 4.0 and x["h"] == 6)
    e95_4, e95_6 = early["h4_level0.95"], early["h6_level0.95"]
    pos = [x for x in inv if x["h"] > 0]
    res["paper_claims_check"] = [
        {"claim": "final scaled error AUC 0.985 (h=4), 0.977 (h=6), pooled over seeds",
         "recomputed": [hl4["final_learned"]["point"], hl6["final_learned"]["point"]],
         "ci_cluster": [hl4["final_learned"]["ci_cluster"], hl6["final_learned"]["ci_cluster"]],
         "ci_hier": [hl4["final_learned"]["ci_hier"], hl6["final_learned"]["ci_hier"]],
         "verdict": "reproduced; endpoint statistic (bookkeeping)"},
        {"claim": "pooled AUC 0.97 (h=4) and 0.95 (h=6) by t~0.53; intro: 'AUC at least 0.95 by t~0.53'",
         "recomputed": [hl4["t0528_learned"]["point"], hl6["t0528_learned"]["point"]],
         "ci_cluster": [hl4["t0528_learned"]["ci_cluster"], hl6["t0528_learned"]["ci_cluster"]],
         "ci_hier": [hl4["t0528_learned"]["ci_hier"], hl6["t0528_learned"]["ci_hier"]],
         "per_seed_h6": hl6["t0528_learned"]["per_seed"],
         "verdict": "point estimates reproduced; see earliest_t for whether >= 0.95 at t~0.53 is supported at h=6"},
        {"claim": "AUC stays between 0.977 and 0.990 from t~0.71 on",
         "recomputed": [min(hl4["late_learned_min"]["point"], hl6["late_learned_min"]["point"]),
                        max(hl4["late_learned_max"]["point"], hl6["late_learned_max"]["point"])],
         "ci_cluster_min_h6": hl6["late_learned_min"]["ci_cluster"], "ci_cluster_max_h4": hl4["late_learned_max"]["ci_cluster"]},
        {"claim": "exact-path AUC 0.49-0.52 (h=4), 0.53-0.58 (h=6) from t~0.71: 'does not separate'",
         "recomputed_h4": [hl4["late_exact_path_min"]["point"], hl4["late_exact_path_max"]["point"]],
         "recomputed_h6": [hl6["late_exact_path_min"]["point"], hl6["late_exact_path_max"]["point"]],
         "h6_ci_excludes_0.5_at_any_late_t": hl6["late_exact_path_ci_excludes_0.5_at_any_late_t"],
         "h6_ci_excludes_0.5_at_all_late_t": hl6["late_exact_path_ci_excludes_0.5_at_all_late_t"],
         "h4_ci_excludes_0.5_at_any_late_t": hl4["late_exact_path_ci_excludes_0.5_at_any_late_t"]},
        {"claim": "final scaled error > 4 flags 94% / 95% of off-atom and 7% / 12% of on-atom (h=4 / h=6)",
         "recomputed": [[f4["tpr"], f4["fpr"]], [f6["tpr"], f6["fpr"]]],
         "ci_cluster": [[f4["tpr_ci_cluster"], f4["fpr_ci_cluster"]], [f6["tpr_ci_cluster"], f6["fpr_ci_cluster"]]],
         "verdict": "reproduced in sample; out-of-sample versions in threshold_rules"},
        {"claim": "earliest t with pooled AUC >= 0.95",
         "h4": {k: e95_4[k] for k in ("grid_first_t", "interp_t", "cluster_interp_t_ci", "hier_interp_t_ci",
                                        "cluster_grid_first_t_dist", "first_t_with_lower_ci_cluster_ge_level")},
         "h6": {k: e95_6[k] for k in ("grid_first_t", "interp_t", "cluster_interp_t_ci", "hier_interp_t_ci",
                                        "cluster_grid_first_t_dist", "first_t_with_lower_ci_cluster_ge_level")}},
        {"claim": "off-atom fraction 0.168 +- 0.012 (h=4), 0.276 +- 0.008 (h=6)",
         "recomputed": {f"h{h}": t_interval([x["off_frac"] for x in pos if x["h"] == h]) for h in (4, 6)},
         "note": "these +- are sd with ddof=1; the EXP-C fractions in the previous paragraph (0.173 +- 0.029 ...) are sd with ddof=0"},
        {"claim": "final medians 6.2-7.1 (off) vs 2.5-2.9 (on); h=0 median 1.08",
         "recomputed_off": [min(x["median_final_e_off"] for x in pos), max(x["median_final_e_off"] for x in pos)],
         "recomputed_on": [min(x["median_final_e_on"] for x in pos), max(x["median_final_e_on"] for x in pos)],
         "h0_on": [x["median_final_e_on"] for x in inv if x["h"] == 0]},
        {"claim": "at t~0.63 medians 7.2-8.0 (off) vs 2.2-3.0 (on)",
         "recomputed_off": [min(x["median_e_t0632_off"] for x in pos), max(x["median_e_t0632_off"] for x in pos)],
         "recomputed_on": [min(x["median_e_t0632_on"] for x in pos), max(x["median_e_t0632_on"] for x in pos)]},
        {"claim": "final scaled error equals d1 within 0.2% for every sample",
         "recomputed_max_rel_diff": max(x["max_rel_diff_final_e_vs_d1"] for x in inv)},
        {"claim": "same training image as the exact field among on-atom: 55-67% (h=4), 23-28% (h=6), all at h=0",
         "recomputed": {x["run"]: [x["same_image_as_exact_on"], x["same_image_as_exact_on_ci"]] for x in inv}},
    ]
    res["runtime_seconds"] = time.time() - t_start

    # ------------------------------------------------------------------ write
    (OUT / "transfer_summary.json").write_text(json.dumps(jsonable(res), indent=1), encoding="utf-8")
    write_csvs(res, H)
    write_markdown(res, H, tg)
    print(f"wrote {OUT} in {time.time() - t_start:.0f}s")


def wquantile_masked(x, mask, W, q=0.5):
    return wquantile(x[mask], W[:, mask], q)


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def write_csvs(res, H):
    with open(OUT / "auc_vs_t.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        hdr = ["t", "tau"]
        for h in (4, 6):
            hdr += [f"h{h}_auc", f"h{h}_lo_cluster", f"h{h}_hi_cluster", f"h{h}_lo_hier", f"h{h}_hi_hier",
                    f"h{h}_within_cond", f"h{h}_within_lo", f"h{h}_within_hi",
                    f"h{h}_exact_path_auc", f"h{h}_exact_lo", f"h{h}_exact_hi", f"h{h}_spearman_e_t_vs_final"]
            hdr += [f"{r['name']}_auc" for r in H[h]]
        w.writerow(hdr)
        for row in res["auc_vs_t"]:
            line = [f"{row['t']:.4f}", f"{row['tau']:.4f}"]
            for h in (4, 6):
                line += [f"{row[f'h{h}_auc']:.4f}", *(f"{v:.4f}" for v in row[f"h{h}_ci_cluster"]),
                         *(f"{v:.4f}" for v in row[f"h{h}_ci_hier"]), f"{row[f'h{h}_within_cond']:.4f}",
                         *(f"{v:.4f}" for v in row[f"h{h}_within_cond_ci"]), f"{row[f'h{h}_exact_path_auc']:.4f}",
                         *(f"{v:.4f}" for v in row[f"h{h}_exact_path_ci_cluster"]),
                         f"{row[f'h{h}_spearman_e_t_vs_final']:.4f}"]
                line += [f"{row[r['name'] + '_auc']:.4f}" for r in H[h]]
            w.writerow(line)
    with open(OUT / "threshold_rules.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time", "t", "scheme", "rule", "thresholds", "tpr", "tpr_lo", "tpr_hi", "fpr", "fpr_lo", "fpr_hi",
                    "n_test_off", "n_test_on", "uses_test_labels_for_threshold"])
        for r in res["threshold_rules"]:
            w.writerow([r["time"], f"{r['t']:.4f}", r["scheme"], r["rule"],
                        ";".join(f"{x['threshold']:.3f}" for x in r["folds"]), f"{r['tpr']:.4f}",
                        *(f"{v:.4f}" for v in r["tpr_ci"]), f"{r['fpr']:.4f}", *(f"{v:.4f}" for v in r["fpr_ci"]),
                        r["n_test_off"], r["n_test_on"], r["uses_test_labels_for_threshold"]])


def f3(v):
    return "–" if v is None else f"{v:.3f}"


def fci(c, nd=3):
    return "–" if c is None else f"[{c[0]:.{nd}f}, {c[1]:.{nd}f}]"


def write_markdown(res, H, tg):
    hl = res["headline_auc"]; L = []
    L += ["# Paper B / transfer: out-of-sample statistics for App. app:measured-transfer", "",
          "Script: `scripts/paperB_transfer.py`. Per-sample data: `results/s10_cifar_transfer_20261108/exp3_cifar_heff_h{0,4,6}_s*/per_sample_ckpt_60000.npz` "
          "(the only per-sample arrays; `results/exp_c_cifar_transfer_20261022/` holds run-level JSON only). "
          f"Label: off-atom = learned d1/d2 >= 1/3 at 1-T = 1e-4 (endpoint). Score: e(t) = (1-t)|Delta(Z_t)| = |m_hat - m*| on the learned path. "
          f"B = {B} bootstrap replicates; CIs are 95% percentile intervals. 'cluster' resamples the 48 conditions within every run "
          "(networks fixed, primary); 'iid' resamples samples (sources) within every run; 'hier' resamples the 3 seeds and then conditions "
          "(crude with 3 seeds). 'seed t' is the mean of the per-seed AUCs with a t interval, df = 2.", ""]
    L += ["## 1. Headline AUCs", "",
          "| statistic | h | AUC | cluster CI | iid CI | hier CI | per seed (cluster CI) | seed mean [t95] |", "|---|---|---|---|---|---|---|---|"]
    for key, lab in (("final_learned", "final e (t=0.9999), ENDPOINT"), ("t0528_learned", "e at t=0.528"),
                     ("t0632_learned", "e at t=0.632")):
        for h in (4, 6):
            d = hl[f"h{h}"][key]
            ps = "; ".join(f"{v['point']:.3f} {fci(v['ci_cluster'])}" for v in d["per_seed"].values())
            st = d["seed_mean_t"]
            L.append(f"| {lab} | {h} | {d['point']:.3f} | {fci(d['ci_cluster'])} | {fci(d.get('ci_iid'))} | {fci(d['ci_hier'])} | {ps} | "
                     f"{st['mean']:.3f} {fci(st['t95'])} |")
    for key, lab in (("late_learned_min", "min AUC over t>=0.71"), ("late_learned_max", "max AUC over t>=0.71"),
                     ("late_exact_path_min", "exact-path AUC, min over t>=0.71"), ("late_exact_path_max", "exact-path AUC, max over t>=0.71"),
                     ("t0713_exact_path", "exact-path AUC at t=0.713"), ("final_exact_path", "exact-path AUC at t=0.9999")):
        for h in (4, 6):
            d = hl[f"h{h}"][key]
            L.append(f"| {lab} | {h} | {d['point']:.3f} | {fci(d['ci_cluster'])} | {fci(d.get('ci_iid'))} | {fci(d['ci_hier'])} | | |")
    L += ["", "| check | h=4 | h=6 |", "|---|---|---|"]
    for key, lab in (("within_condition_t0528", "within-condition AUC at t=0.528"), ("within_condition_t0632", "within-condition AUC at t=0.632"),
                     ("within_condition_final", "within-condition AUC, final")):
        L.append(f"| {lab} | {hl['h4'][key]['point']:.3f} {fci(hl['h4'][key]['ci_cluster'])} | {hl['h6'][key]['point']:.3f} {fci(hl['h6'][key]['ci_cluster'])} |")
    L.append(f"| condition-prior baseline AUC (other sources' endpoint labels) | {hl['h4']['condition_prior_baseline']['point']:.3f} "
             f"{fci(hl['h4']['condition_prior_baseline']['cluster_ci'])} | {hl['h6']['condition_prior_baseline']['point']:.3f} "
             f"{fci(hl['h6']['condition_prior_baseline']['cluster_ci'])} |")
    for key, lab in (("auc_d1_final", "AUC of endpoint d1"), ("auc_d2_final", "AUC of endpoint d2"),
                     ("auc_final_e_over_d2", "AUC of final e / d2 (= label by construction)"), ("icc_off_pooled", "ICC of the label within conditions")):
        L.append(f"| {lab} | {hl['h4'][key]:.3f} | {hl['h6'][key]:.3f} |")
    L.append(f"| exact-path CI excludes 0.5 at some / all t>=0.71 | {hl['h4']['late_exact_path_ci_excludes_0.5_at_any_late_t']} / "
             f"{hl['h4']['late_exact_path_ci_excludes_0.5_at_all_late_t']} | {hl['h6']['late_exact_path_ci_excludes_0.5_at_any_late_t']} / "
             f"{hl['h6']['late_exact_path_ci_excludes_0.5_at_all_late_t']} |")

    L += ["", "## 2. AUC of e(t) against the endpoint label (score uses information at t only)", "",
          "| t | h=4 AUC [cluster] | h=4 within-cond | h=4 exact path | h=6 AUC [cluster] | h=6 within-cond | h=6 exact path | Spearman e(t) vs final e (h4 / h6) |",
          "|---|---|---|---|---|---|---|---|"]
    cut_taus = (math.log(1e2), math.log(1e3), math.log(1e4))
    for row in res["auc_vs_t"]:
        if row["tau"] > 3.0 + 1e-9 and min(abs(row["tau"] - c) for c in cut_taus) > 1e-6:
            continue
        L.append(f"| {row['t']:.3f} | {row['h4_auc']:.3f} {fci(row['h4_ci_cluster'])} | {row['h4_within_cond']:.3f} | "
                 f"{row['h4_exact_path_auc']:.3f} {fci(row['h4_exact_path_ci_cluster'])} | {row['h6_auc']:.3f} {fci(row['h6_ci_cluster'])} | "
                 f"{row['h6_within_cond']:.3f} | {row['h6_exact_path_auc']:.3f} {fci(row['h6_exact_path_ci_cluster'])} | "
                 f"{row['h4_spearman_e_t_vs_final']:.2f} / {row['h6_spearman_e_t_vs_final']:.2f} |")

    L += ["", "## 3. Earliest t with AUC >= level", "",
          "Grid: tau = -log(1-t) in steps of 0.25 (t = 0.221, 0.393, 0.528, 0.632, 0.713, ...). 'interp' interpolates the AUC linearly in tau between grid points.", "",
          "| h | level | first grid t | interp t | interp CI cluster | interp CI hier | P(first grid t) cluster | first t with lower CI >= level | per seed interp t [CI] |",
          "|---|---|---|---|---|---|---|---|---|"]
    for key, d in res["earliest_t"].items():
        h, lev = key.split("_level")
        dist = ", ".join(f"{k}: {v:.2f}" for k, v in d["cluster_grid_first_t_dist"].items())
        per = "; ".join(f"{f3(v['interp_t'])} {fci(v['interp_t_ci_cluster'])}" for v in d["per_seed"].values())
        L.append(f"| {h[1:]} | {lev} | {f3(d['grid_first_t'])} | {f3(d['interp_t'])} | {fci(d['cluster_interp_t_ci'])} | "
                 f"{fci(d['hier_interp_t_ci'])} | {dist} | {f3(d['first_t_with_lower_ci_cluster_ge_level'])} | {per} |")

    L += ["", "## 4. Threshold rule 'e(t) > c' chosen out of sample", "",
          "Rules fixed in advance: youden = argmax TPR-FPR on the training runs; tpr95 = largest c with training TPR >= 0.95; "
          "fpr10 = smallest c with training FPR <= 0.10; fixed4 = the paper's c = 4 (chosen in sample at the final time). "
          "LOSO results pool the test counts of the three folds. CIs bootstrap conditions in training and test runs and re-select c.", ""]
    for time_key in ("final", "tau=0.75", "tau=1.0"):
        rows = [r for r in res["threshold_rules"] if r["time"] == time_key]
        L += [f"### {time_key} (t = {rows[0]['t']:.4f})", "",
              "| scheme | rule | c (per fold) | TPR [CI] | FPR [CI] |", "|---|---|---|---|---|"]
        for r in rows:
            cs = ", ".join(f"{x['threshold']:.2f}" for x in r["folds"])
            L.append(f"| {r['scheme']} | {r['rule']} | {cs} | {r['tpr']:.3f} {fci(r['tpr_ci'])} | {r['fpr']:.3f} {fci(r['fpr_ci'])} |")
        L.append("")

    L += ["## 5. Fixed thresholds (in sample)", "",
          "| time | c | h | TPR [cluster] [hier] | FPR [cluster] [hier] | per seed TPR / FPR |", "|---|---|---|---|---|---|"]
    for r in res["fixed_thresholds"]:
        if r["h"] == 0:
            continue
        if r["time"] not in ("final", "tau=0.75", "tau=1.0"):
            continue
        per = "; ".join(f"{v['tpr']:.3f}/{v['fpr']:.3f}" for v in r["per_seed"].values())
        L.append(f"| {r['time']} | {r['c']:g} | {r['h']} | {r['tpr']:.3f} {fci(r['tpr_ci_cluster'])} {fci(r['tpr_ci_hier'])} | "
                 f"{r['fpr']:.3f} {fci(r['fpr_ci_cluster'])} {fci(r['fpr_ci_hier'])} | {per} |")
    h0 = [r for r in res["fixed_thresholds"] if r["h"] == 0 and r["c"] == 4.0]
    if h0:
        L += ["", "h = 0 (all samples on-atom), share flagged by e(t) > 4: " +
              "; ".join(f"{r['time']}: {r['flag_rate_all_on_atom']:.3f} {fci(r['flag_rate_ci_cluster'])}" for r in h0)]

    L += ["", "## 6. Inventory and bookkeeping", "",
          "| run | n off / n | off frac [cluster] | run JSON | ICC | conds w/o off | label 1e-2 = 1e-4 | max abs(e_final-d1)/e | median d2 on / off | same image (on) [cluster] | (e>4) = label |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in res["inventory"]:
        L.append(f"| {x['run']} | {x['n_off']}/{x['n']} | {x['off_frac']:.3f} {fci(x['off_frac_ci_cluster'])} | {x['off_frac_from_run_json']:.3f} | "
                 f"{x['icc_off_within_condition']:.3f} | {x['conditions_without_off']} | {x['label_agreement_cutoff_1e-2_vs_1e-4']:.3f} | "
                 f"{x['max_rel_diff_final_e_vs_d1']:.4f} | {f3(x['median_d2_on'])} / {f3(x['median_d2_off'])} | "
                 f"{f3(x['same_image_as_exact_on'])} {fci(x['same_image_as_exact_on_ci'])} | {x['rule_e_final_gt4_agrees_with_label']:.3f} |")
    L += ["", "Pairing of h4_sK with h6_sK (same training subset, conditions and sources):", ""]
    for p in res["pairing_h4_h6_same_seed"]:
        L.append(f"- seed {p['seed']}: P(off at h6 | off at h4) = {p['p_off6_given_off4']:.3f}, P(off at h6 | on at h4) = "
                 f"{p['p_off6_given_on4']:.3f}, phi = {p['phi']:.3f}, Spearman of final e = {p['spearman_final_e']:.3f}, "
                 f"same exact endpoint image = {p['same_exact_endpoint_image']:.3f}")
    L += ["", "Run-level off-atom fractions (mean, sd ddof=1, sd ddof=0, t95 over seeds):", ""]
    for src, blk in res["run_level_fractions"].items():
        for h, d in blk["by_h"].items():
            for k in ("euler50_1e-3", "rk4_1e-4"):
                v = d[k]
                if "mean" in v:
                    L.append(f"- {src} {h} {k}: {v['mean']:.3f}, sd1 {v['sd_ddof1']:.3f}, sd0 {v['sd_ddof0']:.3f}, t95 {fci(v['t95'])} "
                             f"(per seed {', '.join(f'{a:.3f}' for a in v['values'])})")
    L += ["", "## 7. Which statistics use endpoint information", "", "| statistic | endpoint information | note |", "|---|---|---|"]
    for e in res["endpoint_information"]:
        L.append(f"| {e['statistic']} | {e['endpoint_info']} | {e['note']} |")
    (OUT / "TRANSFER_SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
