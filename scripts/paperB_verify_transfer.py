"""Independent verifier for the paper-B analysis "transfer" (app:measured-transfer of paper_mechanism/main.tex).

Written without reading scripts/paperB_transfer.py. Recomputes, from the saved per-sample arrays only,
the numbers that analysis reported, and records everything in
results/paperB_20261121/verify_transfer/verify_transfer.json.

Data (numpy only):
  results/s10_cifar_transfer_20261108/exp3_cifar_heff_h{0,4,6}_s{0,1,2}/per_sample_ckpt_60000.npz
      (written by scripts/exp_c_cifar_transfer.py): e_learned[n, g] = |m_hat - m*| along the learned
      RK4 path at grid tau_g (t = 1 - exp(-tau)); e_exact[n, g] = the same network error along the
      exact path from the same source; learned_ratio_k = d1/d2 of the learned state at cutoff
      eps_out[k] over the run's 2000 training images; learned_d1_k, learned_nn_k, exact_nn_k;
      rows = condition (training-row index), 48 conditions x 16 sources.
  results/s10_cifar_transfer_20261108/*/ckpt_60000.json and
  results/exp_c_cifar_transfer_20261022/*/ckpt_60000.json (run-level fractions).

Label: off-atom <=> learned_ratio_2 >= 1/3 (d1/d2 at 1-t = 1e-4), an endpoint quantity.
Score e(t): e_learned[:, g] uses the learned state at tau_g only (no endpoint information), but needs
the exact posterior mean m* over the training set. e_final (g = last) is ~ d1, an endpoint quantity.

Bootstrap (B replicates, 95% percentile intervals):
  cluster  conditions resampled (with replacement) within every run, networks fixed;
  iid      samples resampled within every run;
  hier     the 3 seeds resampled with replacement, then conditions within each drawn seed.
  For analyses that combine h=4 and h=6 runs, the "cluster" scheme is run twice: with independent
  draws per run, and with one draw per seed shared by h4_sK and h6_sK (they share training subset,
  conditions and sources: same config seed K, fixed SOURCE_SEED).

    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_transfer            (~10 min, B=4000)
    PYTHONPATH=. uv run --no-sync python -m scripts.paperB_verify_transfer --extra    (Monte Carlo spread
        of selected CI endpoints at B=2000 over 6 RNG seeds, min-over-t CI, dependence between runs)
"""
from __future__ import annotations

import json
import math
import pathlib
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
S10 = ROOT / "results" / "s10_cifar_transfer_20261108"
EXPC = ROOT / "results" / "exp_c_cifar_transfer_20261022"
OUT = ROOT / "results" / "paperB_20261121" / "verify_transfer"
RATIO = 1.0 / 3.0
B = int(__import__("os").environ.get("VERIFY_B", "4000"))
SEED = 20261121
T975_DF2 = 4.302652729911275          # Student t, 97.5% quantile, 2 degrees of freedom
SEEDS = (0, 1, 2)
THR_TIMES = {"t0.393": 1, "t0.528": 2, "t0.632": 3, "t0.865": 7, "final": 38}


# ----------------------------------------------------------------------------------------------
# data
def load_runs():
    runs = {}
    for h in (0, 4, 6):
        for s in SEEDS:
            f = S10 / f"exp3_cifar_heff_h{h}_s{s}" / "per_sample_ckpt_60000.npz"
            if not f.exists():
                continue
            z = np.load(f)
            ratio = z["learned_ratio_2"].astype(np.float64)
            d1 = z["learned_d1_2"].astype(np.float64)
            _, cond = np.unique(z["rows"], return_inverse=True)
            runs[(h, s)] = dict(
                eL=z["e_learned"].astype(np.float64), eX=z["e_exact"].astype(np.float64),
                rows=z["rows"], cond=cond, tau=z["grid_tau"].astype(np.float64),
                off=ratio >= RATIO, ratio=ratio, d1=d1, d2=d1 / ratio,
                lnn=z["learned_nn_2"], xnn=z["exact_nn_2"], xratio=z["exact_ratio_2"].astype(np.float64),
                off_k=[z[f"learned_ratio_{k}"].astype(np.float64) >= RATIO for k in range(3)])
    return runs


# ----------------------------------------------------------------------------------------------
# statistics
def auc_ranks(pos, neg):
    """Reference AUC (copied logic of scripts/summarize_s10_cifar.auc): P(pos>neg) + P(=)/2."""
    x = np.concatenate([pos, neg])
    r = np.empty(len(x))
    order = x.argsort(kind="mergesort")
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def wauc(s, y, W, chunk=1000):
    """Weighted Mann-Whitney AUC, P(s_pos > s_neg) + P(=)/2, for each row of W (B, n)."""
    W = np.atleast_2d(np.asarray(W, dtype=np.float64))
    order = np.argsort(s, kind="mergesort")
    ss, yy = s[order], y[order].astype(np.float64)
    starts = np.r_[0, np.flatnonzero(np.diff(ss) != 0) + 1]
    ties = len(starts) < len(ss)
    out = np.empty(len(W))
    for a in range(0, len(W), chunk):
        Wo = W[a:a + chunk][:, order]
        P, N = Wo * yy, Wo * (1.0 - yy)
        if ties:
            P, N = np.add.reduceat(P, starts, axis=1), np.add.reduceat(N, starts, axis=1)
        below = np.cumsum(N, axis=1) - N
        out[a:a + chunk] = (P * (below + 0.5 * N)).sum(1) / (P.sum(1) * N.sum(1))
    return out


def ci(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def spearman(a, b):
    ra = np.argsort(np.argsort(a, kind="mergesort"), kind="mergesort").astype(float)
    rb = np.argsort(np.argsort(b, kind="mergesort"), kind="mergesort").astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


# ----------------------------------------------------------------------------------------------
# bootstrap weights
def _counts(rng, k):
    d = rng.integers(0, k, size=(B, k))
    return np.bincount((d + k * np.arange(B)[:, None]).ravel(), minlength=B * k).reshape(B, k).astype(np.float64)


def weights_cluster(rng, runs, keys, shared=False):
    """Per-sample weights (B, sum n) for the listed runs; conditions resampled within each run
    (shared=True: one draw per seed, used by every run of that seed)."""
    cache, out = {}, []
    for key in keys:
        draw_key = key[1] if shared else key
        if draw_key not in cache:
            cache[draw_key] = _counts(rng, int(runs[key]["cond"].max()) + 1)
        out.append(cache[draw_key][:, runs[key]["cond"]])
    return np.concatenate(out, axis=1)


def weights_iid(rng, runs, keys):
    out = []
    for key in keys:
        n = len(runs[key]["off"])
        out.append(rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64))
    return np.concatenate(out, axis=1)


def weights_hier(rng, runs, keys):
    sizes = [len(runs[k]["off"]) for k in keys]
    offs = np.r_[0, np.cumsum(sizes)]
    W = np.zeros((B, offs[-1]))
    R = len(keys)
    pick = rng.integers(0, R, size=(B, R))
    for j in range(R):
        cnt = _counts(rng, int(runs[keys[0]]["cond"].max()) + 1)
        for r, key in enumerate(keys):
            m = pick[:, j] == r
            W[m, offs[r]:offs[r + 1]] += cnt[m][:, runs[key]["cond"]]
    return W


# ----------------------------------------------------------------------------------------------
# threshold rules  "flag if score > c"
def select_c(s, y, W, rule):
    """Threshold per bootstrap row of W (B, n), chosen on (s, y). Candidates c = observed scores
    (flag strictly above) plus -inf. Returns (c, c_mid) where c_mid is the midpoint to the next score."""
    W = np.atleast_2d(W)
    order = np.argsort(s, kind="mergesort")
    ss, yy = s[order], y[order].astype(np.float64)
    starts = np.r_[0, np.flatnonzero(np.diff(ss) != 0) + 1]
    vals = ss[starts]
    Wo = W[:, order]
    P = np.add.reduceat(Wo * yy, starts, axis=1)
    N = np.add.reduceat(Wo * (1.0 - yy), starts, axis=1)
    Pt, Nt = P.sum(1, keepdims=True), N.sum(1, keepdims=True)
    # column 0: c = -inf (flag everything); column g+1: c = vals[g]
    TPR = np.concatenate([np.ones((len(W), 1)), (Pt - np.cumsum(P, 1)) / Pt], 1)
    FPR = np.concatenate([np.ones((len(W), 1)), (Nt - np.cumsum(N, 1)) / Nt], 1)
    cand = np.r_[-np.inf, vals]
    nxt = np.r_[vals, np.inf]
    if rule == "youden":
        g = np.argmax(TPR - FPR, axis=1)                      # first (smallest c) maximiser
    elif rule == "tpr95":
        g = (TPR >= 0.95 - 1e-12).sum(1) - 1                  # largest c with TPR >= 0.95
    elif rule == "fpr10":
        g = (FPR > 0.10 + 1e-12).sum(1)                       # smallest c with FPR <= 0.10
    else:
        raise ValueError(rule)
    c = cand[g]
    c_mid = np.where(np.isfinite(c), 0.5 * (c + nxt[g]), -np.inf)
    return c, c_mid


def rates(s, y, W, c):
    """Weighted TP, P, FP, N of the rule s > c for each row (c per row)."""
    W = np.atleast_2d(W)
    flag = s[None, :] > np.asarray(c)[:, None]
    yy = y.astype(np.float64)
    return ((W * flag * yy).sum(1), (W * yy).sum(1), (W * flag * (1 - yy)).sum(1), (W * (1 - yy)).sum(1))


# ----------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    runs = load_runs()
    tau = runs[(4, 0)]["tau"]
    tgrid = 1 - np.exp(-tau)
    res = {"source": str(S10.relative_to(ROOT)), "B": B, "rng_seed": SEED,
           "label": "off-atom = learned_ratio_2 (d1/d2 at 1-t=1e-4) >= 1/3",
           "t_grid": [float(v) for v in tgrid]}

    # ---------------- inventory / sanity
    inv = {}
    rows0 = runs[(4, 0)]["rows"]
    for (h, s), R in runs.items():
        ef = R["eL"][:, -1]
        off = R["off"]
        inv[f"h{h}_s{s}"] = {
            "n": int(len(off)), "n_off": int(off.sum()), "off_frac": float(off.mean()),
            "rows_identical_to_h4_s0": bool((R["rows"] == rows0).all()),
            "max_rel_dev_efinal_d1": float(np.max(np.abs(ef / R["d1"] - 1))),
            "median_efinal_off": float(np.median(ef[off])) if off.any() else None,
            "median_efinal_on": float(np.median(ef[~off])),
            "median_e_t0.632_off": float(np.median(R["eL"][off, 3])) if off.any() else None,
            "median_e_t0.632_on": float(np.median(R["eL"][~off, 3])),
            "auc_final_run": auc_ranks(ef[off], ef[~off]) if off.any() else None,
            "exact_path_efinal_max": float(R["eX"][:, -1].max()),
            "exact_off_frac": float((R["xratio"] >= RATIO).mean()),
            "median_d2_off": float(np.median(R["d2"][off])) if off.any() else None,
            "median_d2_on": float(np.median(R["d2"][~off])),
            "median_d1_on": float(np.median(R["d1"][~off])),
            "median_d2over3_off": float(np.median(R["d2"][off] / 3)) if off.any() else None,
            "same_image_as_exact_on": float((R["lnn"][~off] == R["xnn"][~off]).mean()),
            "label_agree_1e-2_vs_1e-4": float((R["off_k"][0] == off).mean()),
            "label_agree_1e-3_vs_1e-4": float((R["off_k"][1] == off).mean()),
        }
    res["inventory"] = inv
    res["max_rel_dev_efinal_d1_all_runs"] = max(v["max_rel_dev_efinal_d1"] for v in inv.values())
    res["max_rel_dev_efinal_d1_h4h6"] = max(v["max_rel_dev_efinal_d1"] for k, v in inv.items() if not k.startswith("h0"))
    # pairing of labels
    pair = {}
    for s in SEEDS:
        a, b = runs[(4, s)]["off"].astype(float), runs[(6, s)]["off"].astype(float)
        pair[f"phi_h4s{s}_h6s{s}"] = float(np.corrcoef(a, b)[0, 1])
    for (h, s1, s2) in ((4, 0, 1), (4, 1, 2), (4, 0, 2), (6, 0, 1), (6, 1, 2), (6, 0, 2)):
        a, b = runs[(h, s1)]["off"].astype(float), runs[(h, s2)]["off"].astype(float)
        pair[f"phi_h{h}s{s1}_h{h}s{s2}"] = float(np.corrcoef(a, b)[0, 1])
    res["label_pairing"] = pair

    rng = np.random.default_rng(SEED)

    # ---------------- pooled AUC vs t, both paths, three bootstrap schemes
    auc_t, earliest, within, prior, spear = {}, {}, {}, {}, {}
    for h in (4, 6):
        keys = [(h, s) for s in SEEDS]
        y = np.concatenate([runs[k]["off"] for k in keys])
        EL = np.concatenate([runs[k]["eL"] for k in keys])
        EX = np.concatenate([runs[k]["eX"] for k in keys])
        Ws = {"cluster": weights_cluster(rng, runs, keys), "iid": weights_iid(rng, runs, keys),
              "hier": weights_hier(rng, runs, keys)}
        boot_L = {sch: np.empty((B, len(tau))) for sch in Ws}
        rowsL, rowsX = [], []
        for j in range(len(tau)):
            for path, E, rows_out in (("learned", EL, rowsL), ("exact_path", EX, rowsX)):
                pt = auc_ranks(E[y, j], E[~y, j])
                per_seed = [auc_ranks(runs[k][("eL" if path == "learned" else "eX")][runs[k]["off"], j],
                                      runs[k][("eL" if path == "learned" else "eX")][~runs[k]["off"], j]) for k in keys]
                rec = {"t": float(tgrid[j]), "tau": float(tau[j]), "auc": pt, "per_seed": per_seed,
                       "seed_mean": float(np.mean(per_seed)),
                       "seed_mean_t95": [float(np.mean(per_seed) - T975_DF2 * np.std(per_seed, ddof=1) / math.sqrt(3)),
                                         float(np.mean(per_seed) + T975_DF2 * np.std(per_seed, ddof=1) / math.sqrt(3))]}
                for sch, W in Ws.items():
                    bs = wauc(E[:, j], y, W)
                    rec[f"ci_{sch}"] = ci(bs)
                    if path == "learned":
                        boot_L[sch][:, j] = bs
                if path == "learned":
                    rec["spearman_vs_final"] = spearman(E[:, j], E[:, -1])
                rows_out.append(rec)
        # weighted AUC sanity: unit weights reproduce the rank AUC
        assert abs(wauc(EL[:, 2], y, np.ones((1, len(y))))[0] - rowsL[2]["auc"]) < 1e-12
        auc_t[f"h{h}"] = {"learned": rowsL, "exact_path": rowsX}

        # earliest t with AUC >= level (score at t only)
        ear = {}
        point = np.array([r["auc"] for r in rowsL])
        for L in (0.90, 0.95, 0.97):
            def first_cross(A):
                A = np.atleast_2d(A)
                hit = A >= L
                g = np.where(hit.any(1), hit.argmax(1), -1)
                t_grid_first = np.where(g >= 0, tgrid[np.clip(g, 0, None)], np.nan)
                tau_i = np.full(len(A), np.nan)
                for i in range(len(A)):
                    if g[i] > 0:
                        a0, a1 = A[i, g[i] - 1], A[i, g[i]]
                        tau_i[i] = tau[g[i] - 1] + (L - a0) / (a1 - a0) * (tau[g[i]] - tau[g[i] - 1])
                    elif g[i] == 0:
                        tau_i[i] = tau[0]
                return t_grid_first, 1 - np.exp(-tau_i)
            pf, pi = first_cross(point)
            rec = {"first_grid_t": float(pf[0]), "interp_t": float(pi[0])}
            for sch in Ws:
                bf, bi = first_cross(boot_L[sch])
                rec[f"interp_ci_{sch}"] = ci(bi)
                vals, cnts = np.unique(np.round(bf, 3), return_counts=True)
                rec[f"first_grid_dist_{sch}"] = {f"{v:.3f}": float(c / B) for v, c in zip(vals, cnts)}
            lo = np.array([r["ci_cluster"][0] for r in rowsL])
            k = np.flatnonzero(lo >= L)
            rec["first_grid_t_lower_cluster_bound"] = float(tgrid[k[0]]) if len(k) else None
            ear[f"level{L:.2f}"] = rec
        earliest[f"h{h}"] = ear

        # within-condition AUC (pairs from the same run and condition only)
        wc = {}
        for name, j in (("t0.528", 2), ("t0.632", 3), ("t0.713", 4), ("final", len(tau) - 1)):
            nums, dens = [], []
            for k in keys:
                R = runs[k]
                ncond = R["cond"].max() + 1
                num, den = np.zeros(ncond), np.zeros(ncond)
                for c in range(ncond):
                    m = R["cond"] == c
                    sc, yc = R["eL"][m, j], R["off"][m]
                    p, q = sc[yc], sc[~yc]
                    if len(p) and len(q):
                        d = p[:, None] - q[None, :]
                        num[c] = (d > 0).sum() + 0.5 * (d == 0).sum()
                        den[c] = len(p) * len(q)
                nums.append(num)
                dens.append(den)
            pt = float(sum(n.sum() for n in nums) / sum(d.sum() for d in dens))
            bn, bd = np.zeros(B), np.zeros(B)
            for num, den in zip(nums, dens):
                cnt = _counts(rng, len(num))
                bn += cnt @ num
                bd += cnt @ den
            # mean of per-condition AUCs (conditions with both groups), for reference
            per = np.concatenate([n[d > 0] / d[d > 0] for n, d in zip(nums, dens)])
            wc[name] = {"auc_pairs_pooled": pt, "ci_cluster": ci(bn / bd),
                        "mean_of_condition_aucs": float(per.mean()), "n_conditions_with_both": int(len(per))}
        within[f"h{h}"] = wc

        # condition-prior baseline: share of the other 15 sources of the same condition that end off-atom
        sc = []
        for k in keys:
            R = runs[k]
            tot = np.bincount(R["cond"], weights=R["off"].astype(float))
            n_c = np.bincount(R["cond"])
            sc.append((tot[R["cond"]] - R["off"]) / (n_c[R["cond"]] - 1))
        sc = np.concatenate(sc)
        prior[f"h{h}"] = {"auc": auc_ranks(sc[y], sc[~y]), "ci_cluster": ci(wauc(sc, y, Ws["cluster"]))}

        spear[f"h{h}"] = {f"{tgrid[j]:.3f}": spearman(EL[:, j], EL[:, -1]) for j in range(8)}
        # endpoint geometry
        d2 = np.concatenate([runs[k]["d2"] for k in keys])
        ratio_e = EL[:, -1] / d2
        res.setdefault("geometry", {})[f"h{h}"] = {
            "auc_d2": auc_ranks(d2[y], d2[~y]), "auc_efinal_over_d2": auc_ranks(ratio_e[y], ratio_e[~y]),
            "auc_d1": auc_ranks(np.concatenate([runs[k]["d1"] for k in keys])[y],
                                np.concatenate([runs[k]["d1"] for k in keys])[~y])}
        print(f"h{h}: AUC vs t done ({time.time()-t0:.0f}s)", flush=True)

    res["auc_vs_t"] = auc_t
    res["earliest_t"] = earliest
    res["within_condition"] = within
    res["condition_prior_baseline"] = prior
    res["spearman_e_t_vs_final"] = spear

    # ---------------- threshold rules
    keys_all = [(h, s) for h in (4, 6) for s in SEEDS]
    idx, off_ = {}, 0
    for k in keys_all:
        n = len(runs[k]["off"])
        idx[k] = slice(off_, off_ + n)
        off_ += n
    Wind = weights_cluster(rng, runs, keys_all, shared=False)
    Wsh = weights_cluster(rng, runs, keys_all, shared=True)
    ONE = np.ones((1, off_))

    def scheme_list():
        L = [("insample_h4", [[(4, s) for s in SEEDS]], [[(4, s) for s in SEEDS]], 4),
             ("insample_h6", [[(6, s) for s in SEEDS]], [[(6, s) for s in SEEDS]], 6),
             ("h4->h6", [[(4, s) for s in SEEDS]], [[(6, s) for s in SEEDS]], 6),
             ("h6->h4", [[(6, s) for s in SEEDS]], [[(4, s) for s in SEEDS]], 4)]
        for h in (4, 6):
            L.append((f"loso_within_h{h}", [[(h, s) for s in SEEDS if s != K] for K in SEEDS],
                      [[(h, K)] for K in SEEDS], h))
            L.append((f"loso_both_h{h}", [[(hh, s) for hh in (4, 6) for s in SEEDS if s != K] for K in SEEDS],
                      [[(h, K)] for K in SEEDS], h))
        return L

    thr = []
    for tname, j in THR_TIMES.items():
        S = np.concatenate([runs[k]["eL"][:, j] for k in keys_all])
        Y = np.concatenate([runs[k]["off"] for k in keys_all])
        for name, trains, tests, h_test in scheme_list():
            for rule in ("youden", "tpr95", "fpr10", "fixed4"):
                out = {"time": tname, "t": float(tgrid[j]), "scheme": name, "rule": rule}
                for wname, Wfull in (("point", ONE), ("cluster_indep", Wind), ("cluster_shared", Wsh)):
                    TP = Pn = FP = Nn = 0.0
                    cs, cmids = [], []
                    for tr, te in zip(trains, tests):
                        tr_i = np.concatenate([np.arange(off_)[idx[k]] for k in tr])
                        te_i = np.concatenate([np.arange(off_)[idx[k]] for k in te])
                        Wtr, Wte = Wfull[:, tr_i], Wfull[:, te_i]
                        if rule == "fixed4":
                            c = np.full(len(Wtr), 4.0)
                            cm = c
                        else:
                            c, cm = select_c(S[tr_i], Y[tr_i], Wtr, rule)
                        a, b, cc, d = rates(S[te_i], Y[te_i], Wte, c)
                        TP, Pn, FP, Nn = TP + a, Pn + b, FP + cc, Nn + d
                        cs.append(c)
                        cmids.append(cm)
                        if wname == "point" and rule != "fixed4":
                            # midpoint convention, for the reported c values
                            a2, b2, c2, d2_ = rates(S[te_i], Y[te_i], Wte, cm)
                            out.setdefault("tp_mid", 0.0)
                            out["tp_mid"] += float(a2[0]); out.setdefault("p_mid", 0.0); out["p_mid"] += float(b2[0])
                            out.setdefault("fp_mid", 0.0); out["fp_mid"] += float(c2[0])
                            out.setdefault("n_mid", 0.0); out["n_mid"] += float(d2_[0])
                    tpr, fpr = TP / Pn, FP / Nn
                    if wname == "point":
                        out["c"] = [float(c[0]) for c in cs]
                        out["c_mid"] = [float(c[0]) for c in cmids]
                        out["tpr"], out["fpr"] = float(tpr[0]), float(fpr[0])
                        out["n_pos"], out["n_neg"] = float(Pn[0]), float(Nn[0])
                        if rule != "fixed4":
                            out["tpr_mid"] = out.pop("tp_mid") / out.pop("p_mid")
                            out["fpr_mid"] = out.pop("fp_mid") / out.pop("n_mid")
                    else:
                        out[f"tpr_ci_{wname}"] = ci(tpr)
                        out[f"fpr_ci_{wname}"] = ci(fpr)
                        out[f"c_ci_{wname}"] = ci(np.concatenate(cs))
                thr.append(out)
        print(f"thresholds {tname} done ({time.time()-t0:.0f}s)", flush=True)
    res["threshold_rules"] = thr

    # ---------------- run-level fractions (S10 and EXP-C), sd conventions
    def msd(v):
        v = np.asarray(v, dtype=np.float64)
        return {"values": [float(x) for x in v], "mean": float(v.mean()), "sd_ddof0": float(v.std(ddof=0)),
                "sd_ddof1": float(v.std(ddof=1)),
                "t95": [float(v.mean() - T975_DF2 * v.std(ddof=1) / math.sqrt(len(v))),
                        float(v.mean() + T975_DF2 * v.std(ddof=1) / math.sqrt(len(v)))]}
    frac = {"s10_npz": {f"h{h}": msd([runs[(h, s)]["off"].mean() for s in SEEDS]) for h in (4, 6)}}
    frac["s10_json"] = {}
    for h in (4, 6):
        v = []
        for s in SEEDS:
            j = json.loads((S10 / f"exp3_cifar_heff_h{h}_s{s}" / "ckpt_60000.json").read_text())
            v.append(1 - j["cutoffs"][2]["learned"]["on_atom_run"])
        frac["s10_json"][f"h{h}"] = msd(v)
    frac["expc"] = {}
    for h in (4, 5, 6):
        eu, rk = [], []
        for s in SEEDS:
            j = json.loads((EXPC / f"exp3_cifar_heff_h{h}_s{s}" / "ckpt_60000.json").read_text())
            eu.append(1 - j["euler50_T1e-3"]["on_atom_run"])
            rk.append(1 - j["cutoffs"][2]["learned"]["on_atom_run"])
        frac["expc"][f"h{h}"] = {"euler50_1e-3": msd(eu), "rk4_1e-4": msd(rk)}
    res["run_level_fractions"] = frac

    # ---------------- same image as exact among on-atom, cluster CI per run
    same = {}
    for (h, s), R in runs.items():
        on = ~R["off"]
        m = (R["lnn"] == R["xnn"]) & on
        W = weights_cluster(rng, runs, [(h, s)])
        same[f"h{h}_s{s}"] = {"value": float(m.sum() / on.sum()), "ci_cluster": ci((W * m).sum(1) / (W * on).sum(1))}
    res["same_image_as_exact_on"] = same

    # ---------------- ICC(1) of the label within conditions (one-way ANOVA), per run
    icc = {}
    for (h, s), R in runs.items():
        if not R["off"].any():
            continue
        yv = R["off"].astype(float)
        k = 16
        g = R["cond"]
        means = np.bincount(g, weights=yv) / np.bincount(g)
        msb = k * ((means - yv.mean()) ** 2).sum() / (len(means) - 1)
        msw = ((yv - means[g]) ** 2).sum() / (len(yv) - len(means))
        icc[f"h{h}_s{s}"] = float((msb - msw) / (msb + (k - 1) * msw))
    res["label_icc_within_condition"] = icc

    (OUT / "verify_transfer.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    # compact csv of the AUC curves
    lines = ["h,path,t,tau,auc,ci_cluster_lo,ci_cluster_hi,ci_hier_lo,ci_hier_hi,ci_iid_lo,ci_iid_hi,seed0,seed1,seed2"]
    for h in ("h4", "h6"):
        for path in ("learned", "exact_path"):
            for r in auc_t[h][path]:
                lines.append(",".join([h, path, f"{r['t']:.6f}", f"{r['tau']:.6f}", f"{r['auc']:.6f}",
                                       *(f"{v:.6f}" for v in r["ci_cluster"] + r["ci_hier"] + r["ci_iid"]),
                                       *(f"{v:.6f}" for v in r["per_seed"])]))
    (OUT / "verify_auc_vs_t.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({time.time()-t0:.0f}s)")


def extra_checks(n_seeds=6, b=2000):
    """Monte Carlo spread (over RNG seeds, at the other agent's B=2000) of the bootstrap CI endpoints
    that differed from the reported ones; the CI of the per-replicate minimum of the exact-path AUC
    over t >= 0.71; score/label dependence between runs that share sources."""
    global B
    B = b
    runs = load_runs()
    tau = runs[(4, 0)]["tau"]
    res = {"B": b, "n_rng_seeds": n_seeds, "spread": {}}
    recs = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(1000 + seed)
        rec = {}
        for h in (4, 6):
            keys = [(h, s) for s in SEEDS]
            y = np.concatenate([runs[k]["off"] for k in keys])
            EL = np.concatenate([runs[k]["eL"] for k in keys])
            EX = np.concatenate([runs[k]["eX"] for k in keys])
            Wc = weights_cluster(rng, runs, keys)
            Wh = weights_hier(rng, runs, keys)
            rec[f"h{h}_final_learned_cluster"] = ci(wauc(EL[:, -1], y, Wc))
            rec[f"h{h}_exact_t0.713_cluster"] = ci(wauc(EX[:, 4], y, Wc))
            A = np.stack([wauc(EX[:, j], y, Wc) for j in range(4, len(tau))], 1)
            rec[f"h{h}_exact_final_cluster"] = ci(A[:, -1])
            rec[f"h{h}_exact_min_over_t>=0.71_cluster"] = ci(A.min(1))
            rec[f"h{h}_share_reps_min_over_late_t_le_0.5"] = [float((A.min(1) <= 0.5).mean())] * 2
            A = np.stack([wauc(EL[:, j], y, Wh) for j in range(4)], 1)
            g = (A >= 0.95).argmax(1)
            ti = np.array([tau[g[i] - 1] + (0.95 - A[i, g[i] - 1]) / (A[i, g[i]] - A[i, g[i] - 1]) * (tau[g[i]] - tau[g[i] - 1])
                           if g[i] > 0 else tau[0] for i in range(len(A))])
            rec[f"h{h}_earliest_t_auc0.95_hier"] = ci(1 - np.exp(-ti))
        for (h, s) in ((4, 0), (4, 1), (4, 2), (6, 0), (6, 1), (6, 2)):
            R = runs[(h, s)]
            on = ~R["off"]
            m = (R["lnn"] == R["xnn"]) & on
            W = weights_cluster(rng, runs, [(h, s)])
            rec[f"same_image_on_h{h}_s{s}"] = ci((W * m).sum(1) / (W * on).sum(1))
        keys_all = [(hh, s) for hh in (4, 6) for s in SEEDS]
        W = weights_cluster(rng, runs, keys_all)
        n3 = sum(len(runs[(4, s)]["off"]) for s in SEEDS)
        for name, j in (("t0.528", 2), ("final", len(tau) - 1)):
            S4 = np.concatenate([runs[(4, s)]["eL"][:, j] for s in SEEDS])
            Y4 = np.concatenate([runs[(4, s)]["off"] for s in SEEDS])
            S6 = np.concatenate([runs[(6, s)]["eL"][:, j] for s in SEEDS])
            Y6 = np.concatenate([runs[(6, s)]["off"] for s in SEEDS])
            c, _ = select_c(S6, Y6, W[:, n3:], "youden")
            tp, p, fp, nn = rates(S4, Y4, W[:, :n3], c)
            rec[f"h6->h4_{name}_youden_tpr"] = ci(tp / p)
        recs.append(rec)
    for k in recs[0]:
        lo = [r[k][0] for r in recs]
        hi = [r[k][1] for r in recs]
        res["spread"][k] = {"lo_min": min(lo), "lo_max": max(lo), "hi_min": min(hi), "hi_max": max(hi)}
    dep = {}
    for a, b2 in (((4, 0), (4, 1)), ((4, 1), (4, 2)), ((4, 0), (4, 2)), ((6, 0), (6, 1)), ((6, 1), (6, 2)),
                  ((4, 0), (6, 0)), ((4, 1), (6, 1)), ((4, 2), (6, 2))):
        dep[f"h{a[0]}s{a[1]}_vs_h{b2[0]}s{b2[1]}"] = {
            "spearman_e_t0.632": spearman(runs[a]["eL"][:, 3], runs[b2]["eL"][:, 3]),
            "spearman_e_final": spearman(runs[a]["eL"][:, -1], runs[b2]["eL"][:, -1]),
            "phi_label": float(np.corrcoef(runs[a]["off"].astype(float), runs[b2]["off"].astype(float))[0, 1])}
    res["dependence_between_runs_sharing_sources"] = dep
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "verify_transfer_extra.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, v in res["spread"].items():
        print(f"{k:42s} lo {v['lo_min']:.4f}..{v['lo_max']:.4f}  hi {v['hi_min']:.4f}..{v['hi_max']:.4f}")
    print("wrote", OUT / "verify_transfer_extra.json")


if __name__ == "__main__":
    if "--extra" in __import__("sys").argv:
        extra_checks()
    else:
        main()
