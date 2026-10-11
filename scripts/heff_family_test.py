"""Is the effective-bandwidth law specific to the Gaussian Nadaraya-Watson reference?

Section 4.3 fits one bandwidth h_eff to a trained model's per-condition variances and
recovers the same bandwidth from its per-condition means (48/48 synthetic checkpoints),
and reads this as evidence that the model "is a Nadaraya-Watson mixture at all". That
reading needs a control: a different reference family, also indexed by one scale and
also built from the training atoms, might fit the variances and the means just as well,
in which case the evidence is for *local averaging over training atoms at an effective
scale*, not for the Gaussian label kernel in particular.

This script refits the same samples under several families, each with one scale
parameter s, with the weights of training atom i at condition y

    gauss      exp(-|y - y_i|^2 / 2 s^2)           (the paper's reference)
    laplace    exp(-|y - y_i| / s)
    cauchy     1 / (1 + |y - y_i|^2 / s^2)
    knn        uniform over the K = s nearest labels (s an integer)
    posterior  NOT atomic: the linear-Gaussian posterior with observation noise s,
               N(mu_s(y), Sigma_s), whose covariance does not depend on y

and, for every (checkpoint, family), reports exactly what the paper reports for the
Gaussian family: the scale fitted to the log variances, the scale fitted to the means
(both with 95% bootstrap intervals over conditions), whether the intervals overlap, the
log-space R^2 of the variance fit, and how well the variance-fitted reference predicts
the means (mean error at s_var divided by the best achievable mean error).

The posterior family cannot fail informatively: its trace is the same at every
condition, so its log-space R^2 is at most 0 by construction. The non-atomic competitor
that can fail is the endpoint-smoothed mixture of Proposition `prop:tgtnoise`,

    gauss_rho  sum_i p_i^(s)(y) N(x_i, rho^2 I_d):  trace tr Cov_s(y) + d rho^2,
               mean x_bar_s(y)

which nests the Gaussian at rho = 0. It is fitted over (s, rho) to the log variances and
compared with the Gaussian by leave-one-condition-out error, so the extra parameter buys
nothing unless it predicts held-out conditions better. rho-hat at 0 means the variances
are explained by the atoms alone.

Two stages, so the fit can run anywhere numpy does:

    python -m scripts.heff_family_test --stage sample   # torch: draw samples, save stats
    python -m scripts.heff_family_test --stage fit      # numpy only

The sample stage draws exactly as scripts/test_heff_synthetic.py does (same runs,
conditions, M, solver and generator seed), so the gauss family reproduces
results/exp1/_heff/heff_synthetic.json; the fit stage checks that before reporting.

Reads:  results/exp1/heff_p7y_h*_seed*/{config.yaml,checkpoints/}
Writes: results/exp1/_heff/family_stats.npz, results/exp1/_heff/heff_families.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

STATS = Path("results/exp1/_heff/family_stats.npz")
OUT = Path("results/exp1/_heff/heff_families.json")
PUBLISHED = Path("results/exp1/_heff/heff_synthetic.json")
N_BOOT = 500
GRID = np.exp(np.linspace(np.log(3e-3), np.log(5.0), 240))     # as test_heff_synthetic
FAMILIES = ("gauss", "laplace", "cauchy", "knn", "posterior")
RHO_GRID = np.concatenate([[0.0], np.exp(np.linspace(np.log(1e-3), np.log(3.0), 48))])


# --------------------------------------------------------------------------- #
# stage 1: samples -> per-condition statistics (torch)
# --------------------------------------------------------------------------- #
def sample_stage() -> None:
    import torch

    from src.flows.ode_solver import generate_samples
    from src.models.mlp_velocity import build_model
    from src.problems.linear_gaussian import LinearGaussianProblem
    from src.utils import load_yaml

    torch.set_num_threads(16)
    runs = sorted(Path("results/exp1").glob("heff_p7y_h*_seed*"))
    store: dict[str, np.ndarray] = {}
    names = []
    for run in runs:
        cfg = load_yaml(run / "config.yaml")
        dc, ev = cfg["data"], cfg["eval"]
        ps = int(dc.get("problem_seed", cfg["seed"]))
        problem = LinearGaussianProblem.create(
            d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=ps,
            prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
        X, Y = problem.sample_dataset(dc["N"], seed=ps + 1)
        idx = sorted(set(torch.linspace(0, X.shape[0] - 1, ev["n_eval_train"])
                         .round().long().tolist()))
        model = build_model(cfg, data_dim=problem.d, cond_dim=problem.k)
        ckpts = sorted(run.glob("checkpoints/ckpt_*.pt"),
                       key=lambda p: int(p.stem.split("_")[1]))
        if not ckpts:
            print(f"[skip] {run.name}: no checkpoints")
            continue
        gen = torch.Generator().manual_seed(4242)                # as test_heff_synthetic
        its, trs, mus = [], [], []
        for ck in ckpts:
            it = int(ck.stem.split("_")[1])
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model.eval()
            tr_m, mu_m = [], []
            with torch.no_grad():
                for i in idx:
                    s = generate_samples(model, ev["M"], problem.d, Y[i],
                                         source_std=dc.get("source_std", 1.0),
                                         n_steps=ev["n_steps"],
                                         method=ev.get("ode_method", "rk4"),
                                         eps=ev.get("ode_eps", 1e-3), generator=gen,
                                         device="cpu").to(torch.float64)
                    tr_m.append(float(s.var(dim=0, unbiased=True).sum()))
                    mu_m.append(s.mean(0).numpy())
            its.append(it); trs.append(tr_m); mus.append(np.stack(mu_m))
            print(f"  {run.name} iter {it}: mean tr Cov {np.mean(tr_m):.4f}", flush=True)
        key = run.name
        names.append(key)
        store[f"{key}/X"] = X.numpy().astype(np.float64)
        store[f"{key}/Y"] = Y.numpy().astype(np.float64)
        store[f"{key}/A"] = problem.A.numpy().astype(np.float64)
        store[f"{key}/meta"] = np.array([float(cfg["seed"]),
                                         float(cfg["train"].get("y_noise_h", 0.0)),
                                         float(dc.get("prior_std", 1.0)),
                                         float(dc["sigma_obs"])])
        store[f"{key}/idx"] = np.array(idx)
        store[f"{key}/iters"] = np.array(its)
        store[f"{key}/trace"] = np.array(trs)                    # (n_ckpt, n_cond)
        store[f"{key}/mean"] = np.stack(mus)                     # (n_ckpt, n_cond, d)
    store["runs"] = np.array(names)
    STATS.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(STATS, **store)
    print(f"Saved: {STATS}")


# --------------------------------------------------------------------------- #
# stage 2: fit every family (numpy only)
# --------------------------------------------------------------------------- #
def weights(family: str, D: np.ndarray, s: float) -> np.ndarray:
    """Weights over atoms, (n_cond, N), from label distances D (n_cond, N)."""
    if family == "gauss":
        lw = -D ** 2 / (2 * s * s)
    elif family == "laplace":
        lw = -D / s
    elif family == "cauchy":
        lw = -np.log1p(D ** 2 / (s * s))
    else:
        raise ValueError(family)
    lw = lw - lw.max(axis=1, keepdims=True)
    w = np.exp(lw)
    return w / w.sum(axis=1, keepdims=True)


def knn_weights(D: np.ndarray, K: int) -> np.ndarray:
    order = np.argsort(D, axis=1, kind="stable")[:, :K]
    w = np.zeros_like(D)
    np.put_along_axis(w, order, 1.0 / K, axis=1)
    return w


def atomic_reference(W: np.ndarray, X: np.ndarray):
    mean = W @ X                                                  # (n_cond, d)
    sq = ((X[None, :, :] - mean[:, None, :]) ** 2).sum(-1)        # (n_cond, N)
    return (W * sq).sum(1), mean


def reference_tables(family: str, X, Y, A, prior_std, idx):
    """(scales, trace (n_s, n_cond), mean (n_s, n_cond, d))."""
    Yq = Y[idx]
    D = np.sqrt(((Yq[:, None, :] - Y[None, :, :]) ** 2).sum(-1))
    if family == "knn":
        scales = np.arange(1, X.shape[0] + 1, dtype=float)
        tabs = [atomic_reference(knn_weights(D, int(K)), X) for K in scales]
    elif family == "posterior":
        scales = GRID
        d = X.shape[1]
        tabs = []
        for s in scales:
            prec = np.eye(d) / prior_std ** 2 + A.T @ A / s ** 2
            Sig = np.linalg.inv(prec)
            mean = (Yq @ A) / s ** 2 @ Sig.T                     # prior mean 0
            tabs.append((np.full(len(idx), np.trace(Sig)), mean))
    else:
        scales = GRID
        tabs = [atomic_reference(weights(family, D, float(s)), X) for s in scales]
    tr = np.stack([t[0] for t in tabs])
    mu = np.stack([t[1] for t in tabs])
    return scales, tr, mu


def r2(y, yhat):
    ss = ((y - y.mean()) ** 2).sum()
    return float(1.0 - ((y - yhat) ** 2).sum() / ss) if ss > 0 else float("nan")


def fit_one(scales, tr_ref, mu_ref, tr_m, mu_m, rng):
    ly = np.log(tr_m)
    lref = np.log(np.maximum(tr_ref, 1e-300))
    se_c = (ly[None, :] - lref) ** 2                                # (n_s, n_cond)
    me_c = np.linalg.norm(mu_m[None] - mu_ref, axis=2)              # (n_s, n_cond)
    g = int(np.argmin(se_c.sum(1)))
    gm = int(np.argmin(me_c.mean(1)))
    bv, bm = [], []
    n = len(ly)
    for _ in range(N_BOOT):
        b = rng.integers(0, n, n)
        bv.append(scales[int(np.argmin(se_c[:, b].sum(1)))])
        bm.append(scales[int(np.argmin(me_c[:, b].mean(1)))])
    ci_v = [float(np.percentile(bv, 2.5)), float(np.percentile(bv, 97.5))]
    ci_m = [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))]
    return {"s_var": float(scales[g]), "s_var_ci": ci_v,
            "s_mean": float(scales[gm]), "s_mean_ci": ci_m,
            "overlap": not (ci_v[1] < ci_m[0] or ci_m[1] < ci_v[0]),
            "at_edge": g in (0, len(scales) - 1),
            "r2_var": r2(ly, lref[g]),
            "rmse_log": float(np.sqrt(se_c[g].mean())),
            "mean_err_at_svar": float(me_c[g].mean()),
            "mean_err_best": float(me_c[gm].mean()),
            "mean_err_ratio": float(me_c[g].mean() / max(me_c[gm].mean(), 1e-300)),
            "r2_var_at_smean": r2(ly, lref[gm])}


def loo_rmse(se: np.ndarray) -> float:
    """Leave-one-condition-out log-RMSE. se: (..., n_cond) squared log misfits over a
    parameter grid; each condition is predicted by the grid point that fits the others."""
    flat = se.reshape(-1, se.shape[-1])
    total = flat.sum(1)
    errs = [flat[int(np.argmin(total - flat[:, c])), c] for c in range(flat.shape[1])]
    return float(np.sqrt(np.mean(errs)))


def fit_rho(scales, tr_ref, tr_m, d: int, rng) -> dict:
    """The endpoint-smoothed family: trace tr_ref(s) + d rho^2, fitted over (s, rho)."""
    ly = np.log(tr_m)
    lref = np.log(np.maximum(tr_ref[:, None, :] + d * RHO_GRID[None, :, None] ** 2, 1e-300))
    se = (ly[None, None, :] - lref) ** 2                            # (n_s, n_rho, n_cond)
    flat = se.reshape(-1, len(ly))
    g = int(np.argmin(flat.sum(1)))
    gs, gr = np.unravel_index(g, se.shape[:2])
    counts = np.stack([np.bincount(rng.integers(0, len(ly), len(ly)), minlength=len(ly))
                       for _ in range(N_BOOT)], axis=1)            # (n_cond, N_BOOT)
    gb = np.argmin(flat @ counts, axis=0)
    rho_b = RHO_GRID[np.unravel_index(gb, se.shape[:2])[1]]
    se_gauss = se[:, 0, :]
    return {"s": float(scales[gs]), "rho": float(RHO_GRID[gr]),
            "rho_ci": [float(np.percentile(rho_b, 2.5)), float(np.percentile(rho_b, 97.5))],
            "rho_zero_share": float(np.mean(rho_b == 0.0)),
            "share_of_trace": float(d * RHO_GRID[gr] ** 2 / np.mean(tr_m)),
            "rmse_log": float(np.sqrt(flat[g].mean())),
            "r2_var": r2(ly, lref[gs, gr]),
            "loo_rmse": loo_rmse(se), "loo_rmse_gauss": loo_rmse(se_gauss)}


def fit_stage() -> None:
    z = np.load(STATS, allow_pickle=False)
    rows = []
    for run in z["runs"]:
        run = str(run)
        X, Y, A = z[f"{run}/X"], z[f"{run}/Y"], z[f"{run}/A"]
        seed, h, prior_std, _ = z[f"{run}/meta"]
        idx = z[f"{run}/idx"]
        tabs = {f: reference_tables(f, X, Y, A, prior_std, idx) for f in FAMILIES}
        for c, it in enumerate(z[f"{run}/iters"]):
            tr_m, mu_m = z[f"{run}/trace"][c], z[f"{run}/mean"][c]
            rng = np.random.default_rng(int(it) + 1000 * int(seed))
            row = {"run": run, "seed": int(seed), "h": float(h), "iter": int(it)}
            for f in FAMILIES:
                row[f] = fit_one(*tabs[f], tr_m, mu_m, np.random.default_rng(rng.integers(2**32)))
            row["gauss_rho"] = fit_rho(tabs["gauss"][0], tabs["gauss"][1], tr_m, X.shape[1],
                                       np.random.default_rng(rng.integers(2**32)))
            rows.append(row)

    # sanity: the gauss family must reproduce the published fit on the same samples
    pub = {(r["run"], r["iter"]): r for r in json.loads(PUBLISHED.read_text(encoding="utf-8"))}
    same = [abs(np.log(r["gauss"]["s_var"] / pub[(r["run"], r["iter"])]["h_eff"])) < 1e-9
            for r in rows if (r["run"], r["iter"]) in pub]
    print(f"gauss s_var equals published h_eff at {sum(same)}/{len(same)} checkpoints")

    def subset(name, keep):
        S = [r for r in rows if keep(r)]
        out = {"n": len(S)}
        for f in FAMILIES:
            v = [r[f] for r in S]
            out[f] = {
                "overlap": int(sum(x["overlap"] for x in v)),
                "median_r2_var": float(np.nanmedian([x["r2_var"] for x in v])),
                "median_rmse_log": float(np.median([x["rmse_log"] for x in v])),
                "median_mean_err_ratio": float(np.median([x["mean_err_ratio"] for x in v])),
                "median_mean_err_best": float(np.median([x["mean_err_best"] for x in v])),
                "median_abs_log_scale_gap": float(np.median(
                    [abs(np.log(x["s_var"] / x["s_mean"])) for x in v])),
                "log_corr_scales": float(np.corrcoef(np.log([x["s_var"] for x in v]),
                                                     np.log([x["s_mean"] for x in v]))[0, 1])
                if len(v) > 2 and np.std([x["s_var"] for x in v]) > 0 else float("nan"),
                "at_edge": int(sum(x["at_edge"] for x in v))}
        # head-to-head: which atomic family has the lower variance misfit per checkpoint
        atomic = ("gauss", "laplace", "cauchy", "knn")
        best = [min(atomic, key=lambda f: r[f]["rmse_log"]) for r in S]
        out["best_variance_fit_counts"] = {f: best.count(f) for f in atomic}
        bestm = [min(atomic, key=lambda f: r[f]["mean_err_at_svar"]) for r in S]
        out["best_cross_prediction_counts"] = {f: bestm.count(f) for f in atomic}
        g = [r["gauss_rho"] for r in S]
        loo_gap = np.array([x["loo_rmse_gauss"] - x["loo_rmse"] for x in g])  # >0: rho helps
        out["gauss_rho"] = {
            "rho_hat_zero": int(sum(x["rho"] == 0.0 for x in g)),
            "rho_ci_includes_zero": int(sum(x["rho_ci"][0] == 0.0 for x in g)),
            "median_rho": float(np.median([x["rho"] for x in g])),
            "median_share_of_trace": float(np.median([x["share_of_trace"] for x in g])),
            "max_share_of_trace": float(np.max([x["share_of_trace"] for x in g])),
            "loo_better_than_gauss": int((loo_gap > 1e-12).sum()),
            "loo_equal_to_gauss": int((np.abs(loo_gap) <= 1e-12).sum()),
            "median_loo_gain": float(np.median(loo_gap))}
        return name, out

    summary = dict([
        subset("h<=0.1, iter>=1e4 (the paper's 48)", lambda r: r["h"] <= 0.1 and r["iter"] >= 10000),
        subset("iter>=3000 (the paper's 75)", lambda r: r["iter"] >= 3000),
        subset("h=0.5, iter>=3000", lambda r: r["h"] == 0.5 and r["iter"] >= 3000),
    ] + [subset(f"h={hv:g}, iter>=1e4 (of the 48)",
                lambda r, hv=hv: r["h"] == hv and r["iter"] >= 10000)
         for hv in (0.0, 0.01, 0.05, 0.1)])

    # Paired, per checkpoint, on the 48: is the Gaussian misfit lower than each rival's?
    # Bootstrap over checkpoints for the median gap; runs count as the coarser unit.
    S48 = [r for r in rows if r["h"] <= 0.1 and r["iter"] >= 10000]
    runs48 = sorted({r["run"] for r in S48})
    brng = np.random.default_rng(0)
    paired = {}
    for f in ("laplace", "cauchy", "knn"):
        gap = np.array([r[f]["rmse_log"] - r["gauss"]["rmse_log"] for r in S48])  # >0: gauss better
        boot = [np.median(brng.choice(gap, len(gap))) for _ in range(5000)]
        per_run = [np.mean([r[f]["rmse_log"] - r["gauss"]["rmse_log"] for r in S48 if r["run"] == u])
                   for u in runs48]
        paired[f] = {"gauss_lower_checkpoints": int((gap > 0).sum()), "n": len(gap),
                     "median_gap": float(np.median(gap)),
                     "median_gap_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                     "gauss_lower_runs": int(sum(x > 0 for x in per_run)), "n_runs": len(per_run)}
    summary["paired_vs_gauss_48"] = paired
    OUT.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1), encoding="utf-8")
    for name, s in summary.items():
        if name == "paired_vs_gauss_48":
            print("\nPaired against the Gaussian reference, the 48 checkpoints:")
            for f, p in s.items():
                print(f"  {f:8s}: Gaussian misfit lower at {p['gauss_lower_checkpoints']}/{p['n']} "
                      f"checkpoints, {p['gauss_lower_runs']}/{p['n_runs']} runs; median log-RMSE gap "
                      f"{p['median_gap']:.3f} [{p['median_gap_ci95'][0]:.3f}, {p['median_gap_ci95'][1]:.3f}]")
            continue
        print(f"\n{name}: n={s['n']}")
        print(f"  {'family':10s} {'overlap':>8s} {'R2 var':>7s} {'rmse':>6s} "
              f"{'meanerr x':>9s} {'|log gap|':>9s} {'logcorr':>7s} {'edge':>4s}")
        for f in FAMILIES:
            v = s[f]
            print(f"  {f:10s} {v['overlap']:>4d}/{s['n']:<3d} {v['median_r2_var']:>7.3f} "
                  f"{v['median_rmse_log']:>6.3f} {v['median_mean_err_ratio']:>9.3f} "
                  f"{v['median_abs_log_scale_gap']:>9.3f} {v['log_corr_scales']:>7.3f} "
                  f"{v['at_edge']:>4d}")
        print(f"  lowest variance misfit: {s['best_variance_fit_counts']}")
        print(f"  best mean prediction from the variance fit: {s['best_cross_prediction_counts']}")
        gr = s["gauss_rho"]
        print(f"  endpoint-smoothed (gauss+rho): rho-hat = 0 at {gr['rho_hat_zero']}/{s['n']}, "
              f"CI includes 0 at {gr['rho_ci_includes_zero']}/{s['n']}, median d rho^2 / trace "
              f"{gr['median_share_of_trace']:.3f} (max {gr['max_share_of_trace']:.3f}); "
              f"held-out error lower than Gaussian at {gr['loo_better_than_gauss']}/{s['n']}, "
              f"equal at {gr['loo_equal_to_gauss']}")
    print(f"\nSaved: {OUT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("sample", "fit", "both"), default="both")
    a = ap.parse_args()
    if a.stage in ("sample", "both"):
        sample_stage()
    if a.stage in ("fit", "both"):
        fit_stage()


if __name__ == "__main__":
    main()
