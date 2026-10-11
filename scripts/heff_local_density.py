"""E1 of docs/plan/main_track_plan_2026-10-11.md: is the effective bandwidth local?

T1(d) predicts that a kernel learner smooths sparse label regions more: its resolution
scale is b(y) proportional to p(y)^(-1/zeta), with p the label density. At h = 0 that
is h_eff(y) proportional to p(y)^(-1/zeta); at h > 0, h_eff(y)^2 - h^2 proportional
to p(y)^(-2/zeta) in the ridge form. The paper's h_eff is one number per checkpoint,
fitted across conditions; here it is fitted per condition.

Two stages, so the fit can run anywhere numpy does:

    python -m scripts.heff_local_density --stage sample   # torch: draw samples, save stats
    python -m scripts.heff_local_density --stage fit      # numpy only

sample  For each heff_p7y run, at every checkpoint >= 1e4, M = 1000 samples at 60
        training labels chosen at the 1%..99% quantiles of that run's label
        distribution (solver settings as test_heff_synthetic.py); saves the
        per-condition generated trace and mean.
fit     Per condition: h_mean(y_c) = argmin_h |m_c - x_bar_h(y_c)| and
        h_var(y_c) = argmin_h |log T_c - log tr Cov_h(y_c)| on the grid of eq. (heff);
        p_hat(y_c) is a Gaussian KDE of the training labels (Silverman's bandwidth).
        Regress log h_mean (h = 0) or log(h_mean^2 - h^2) (h > 0) on log p_hat: OLS per
        (run, checkpoint), with a bootstrap interval over conditions, and pooled per h
        over the seeds at checkpoints >= 1e5 with (run, checkpoint) fixed effects.
        Conditions whose bandwidth sits at an edge of the grid are excluded.

Reads:  results/exp1/heff_p7y_h*_seed*/{config.yaml,checkpoints/}
Writes: results/exp1/_heff/local_density_stats.npz, results/exp1/_heff/heff_local_density.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

STATS = Path("results/exp1/_heff/local_density_stats.npz")
OUT = Path("results/exp1/_heff/heff_local_density.json")
GRID = np.exp(np.linspace(np.log(3e-3), np.log(5.0), 240))     # as test_heff_synthetic
N_COND = 60
N_BOOT = 1000


def sample_stage(min_iter: int) -> None:
    import torch

    from src.flows.ode_solver import generate_samples
    from src.models.mlp_velocity import build_model
    from src.problems.linear_gaussian import LinearGaussianProblem
    from src.utils import get_device, load_yaml

    device = get_device("auto")
    torch.set_num_threads(8)
    store, names = {}, []
    for run in sorted(Path("results/exp1").glob("heff_p7y_h*_seed*")):
        cfg = load_yaml(run / "config.yaml")
        dc, ev = cfg["data"], cfg["eval"]
        ps = int(dc.get("problem_seed", cfg["seed"]))
        prob = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=ps,
                                            prior_std=dc.get("prior_std", 1.0),
                                            A_kind=dc.get("A_kind", "random"))
        X, Y = prob.sample_dataset(dc["N"], seed=ps + 1)
        order = torch.argsort(Y[:, 0])
        pos = np.unique(np.round(np.linspace(0.01, 0.99, N_COND) * (len(Y) - 1)).astype(int))
        idx = order[torch.as_tensor(pos)].tolist()
        model = build_model(cfg, data_dim=prob.d, cond_dim=prob.k).to(device)
        ckpts = sorted((p for p in run.glob("checkpoints/ckpt_*.pt")
                        if int(p.stem.split("_")[1]) >= min_iter),
                       key=lambda p: int(p.stem.split("_")[1]))
        if not ckpts:
            print(f"[skip] {run.name}: no checkpoints")
            continue
        gen = torch.Generator(device=device).manual_seed(4243)
        its, trs, mus = [], [], []
        for ck in ckpts:
            it = int(ck.stem.split("_")[1])
            model.load_state_dict(torch.load(ck, map_location=device)["model_state"])
            model.eval()
            tr_m, mu_m = [], []
            with torch.no_grad():
                for i in idx:
                    s = generate_samples(model, ev["M"], prob.d, Y[i].to(device),
                                         source_std=dc.get("source_std", 1.0), n_steps=ev["n_steps"],
                                         method=ev.get("ode_method", "rk4"), eps=ev.get("ode_eps", 1e-3),
                                         generator=gen, device=device).to(torch.float64).cpu()
                    tr_m.append(float(s.var(dim=0, unbiased=True).sum()))
                    mu_m.append(s.mean(0).numpy())
            its.append(it); trs.append(tr_m); mus.append(np.stack(mu_m))
            print(f"  {run.name} iter {it}: median tr Cov {np.median(tr_m):.4f}", flush=True)
        names.append(run.name)
        store[f"{run.name}/X"] = X.numpy().astype(np.float64)
        store[f"{run.name}/Y"] = Y.numpy().astype(np.float64)
        store[f"{run.name}/meta"] = np.array([float(cfg["seed"]), float(cfg["train"].get("y_noise_h", 0.0))])
        store[f"{run.name}/idx"] = np.array(idx)
        store[f"{run.name}/iters"] = np.array(its)
        store[f"{run.name}/trace"] = np.array(trs)
        store[f"{run.name}/mean"] = np.stack(mus)
    store["runs"] = np.array(names)
    STATS.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(STATS, **store)
    print(f"Saved: {STATS}")


def nw_tables(X, Y, Yq):
    """Reference mean (G, C, d) and trace (G, C) at every grid bandwidth, k = 1."""
    D2 = (Yq[:, None] - Y[None, :]) ** 2
    mus, trs = [], []
    for h in GRID:
        lw = -D2 / (2 * h * h)
        lw -= lw.max(1, keepdims=True)
        W = np.exp(lw)
        W /= W.sum(1, keepdims=True)
        m = W @ X
        mus.append(m)
        trs.append((W * ((X[None] - m[:, None]) ** 2).sum(-1)).sum(1))
    return np.stack(mus), np.stack(trs)


def ols_boot(x, y, rng):
    sl = float(np.polyfit(x, y, 1)[0])
    b = [np.polyfit(x[j], y[j], 1)[0] for j in (rng.integers(0, len(x), len(x)) for _ in range(N_BOOT))]
    return sl, [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def fit_stage() -> None:
    z = np.load(STATS)
    rng = np.random.default_rng(0)
    rows, pooled = [], {}
    for run in z["runs"]:
        run = str(run)
        X, Y = z[f"{run}/X"], z[f"{run}/Y"][:, 0]
        seed, h = z[f"{run}/meta"]
        idx = z[f"{run}/idx"]
        Yq = Y[idx]
        bw = 1.06 * Y.std() * len(Y) ** -0.2
        p_hat = np.exp(-(Yq[:, None] - Y[None, :]) ** 2 / (2 * bw * bw)).sum(1) / (len(Y) * bw * np.sqrt(2 * np.pi))
        ref_m, ref_t = nw_tables(X, Y, Yq)
        for c, it in enumerate(z[f"{run}/iters"]):
            tr, mu = z[f"{run}/trace"][c], z[f"{run}/mean"][c]
            hm = GRID[np.argmin(np.linalg.norm(ref_m - mu[None], axis=2), axis=0)]
            hv = GRID[np.argmin(np.abs(np.log(tr)[None] - np.log(np.maximum(ref_t, 1e-300))), axis=0)]
            row = {"run": run, "seed": int(seed), "h": float(h), "iter": int(it)}
            for name, hc in (("h_mean", hm), ("h_var", hv)):
                inner = (hc > GRID[1]) & (hc < GRID[-2])
                if h > 0:
                    inner &= hc > 1.05 * h
                    yv = np.log(hc ** 2 - h ** 2)
                else:
                    yv = np.log(hc)
                if inner.sum() >= 10:
                    sl, ci = ols_boot(np.log(p_hat[inner]), yv[inner], rng)
                    row[name] = {"slope": sl, "ci95": ci, "n": int(inner.sum())}
                    if it >= 100000:
                        key = f"h={h:g}/{name}"
                        xs, ys = np.log(p_hat[inner]), yv[inner]
                        pooled.setdefault(key, []).append((xs - xs.mean(), ys - ys.mean()))
                else:
                    row[name] = {"slope": float("nan"), "ci95": [float("nan")] * 2, "n": int(inner.sum())}
            rows.append(row)
    summary = {}
    for key, parts in sorted(pooled.items()):
        xs = np.concatenate([p[0] for p in parts]); ys = np.concatenate([p[1] for p in parts])
        sl, ci = ols_boot(xs, ys, rng)
        summary[key] = {"slope": sl, "ci95": ci, "n": int(len(xs)), "groups": len(parts)}
    OUT.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1), encoding="utf-8")
    for r in rows:
        print(f"  {r['run']:22s} it={r['iter']:>6d}  slope h_mean {r['h_mean']['slope']:+.2f} "
              f"[{r['h_mean']['ci95'][0]:+.2f},{r['h_mean']['ci95'][1]:+.2f}] (n={r['h_mean']['n']})  "
              f"h_var {r['h_var']['slope']:+.2f} (n={r['h_var']['n']})")
    print("\npooled, checkpoints >= 1e5, fixed effects per (run, checkpoint):")
    for k, v in summary.items():
        print(f"  {k:16s} slope {v['slope']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]  "
              f"n={v['n']} in {v['groups']} groups")
    print(f"Saved: {OUT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("sample", "fit", "both"), default="both")
    ap.add_argument("--min-iter", type=int, default=10000)
    a = ap.parse_args()
    if a.stage in ("sample", "both"):
        sample_stage(a.min_iter)
    if a.stage in ("fit", "both"):
        fit_stage()


if __name__ == "__main__":
    main()
