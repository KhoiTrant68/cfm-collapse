"""Which law relates the effective bandwidth to the training bandwidth?

Candidate laws, each with one free parameter per training iteration t, shared by all
runs (all bandwidths h, all seeds) at that t:

    additive        h_eff^2 = h^2 + s(t)^2     the network resolves the label only to a
                                               scale s(t) of its own, which adds to the
                                               label noise in quadrature
    multiplicative  h_eff   = kappa(t) * h     (undefined at h = 0)
    maximum         h_eff   = max(h, s(t))

and the general family h_eff^p = h^p + s(t)^p with p fitted once for all t. Each law is
fitted in log space by least squares over the runs at each t, and scored by the RMSE of
log h_eff pooled over t (leave-one-seed-out as well, so a law is judged on runs it was
not fitted to).

The additive law is what one obtains if the trained field is the population optimum
for a label seen through Gaussian noise of total variance h^2 + s^2: training with
label noise h on a model that cannot resolve the label below scale s is training at
bandwidth sqrt(h^2 + s^2) (Gaussian noises add in variance).

Reads:  results/exp1/_heff/heff_synthetic.json, results/exp3/_heff/heff_exp3_cifar_heff_*.json
Writes: results/_heff_law.json

Usage:
    uv run python scripts/heff_law.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

OUT = Path("results/_heff_law.json")


def load_synthetic(min_iter=10000, max_h=0.1):
    rows = json.loads(Path("results/exp1/_heff/heff_synthetic.json").read_text(encoding="utf-8"))
    return [(r["iter"], r["h"], r.get("seed", 0), r["h_eff"]) for r in rows
            if r["iter"] >= min_iter and r["h"] <= max_h]


def load_cifar(min_iter=5000):
    out = []
    for p in sorted(Path("results/exp3/_heff").glob("heff_exp3_cifar_heff_h*_s*.json")):
        if "_from" in p.stem:
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        out += [(c["iter"], r["h"], r["seed"], c["h_eff"]) for c in r["checkpoints"]
                if c["iter"] >= min_iter]
    return out


def predict(law, h, s, p=2.0):
    if law == "additive":
        return np.sqrt(h ** 2 + s ** 2)
    if law == "multiplicative":
        return s * h
    if law == "maximum":
        return np.maximum(h, s)
    if law == "power":
        return (h ** p + s ** p) ** (1 / p)
    raise ValueError(law)


def fit_s(law, hs, he, p=2.0):
    lo, hi = (1e-4, 50.0) if law != "multiplicative" else (0.5, 5.0)
    f = lambda ls: np.sum((np.log(predict(law, hs, np.exp(ls), p)) - np.log(he)) ** 2)
    return float(np.exp(minimize_scalar(f, bounds=(np.log(lo), np.log(hi)),
                                        method="bounded").x))


def score(data, law, p=2.0, holdout_seed=None):
    """RMSE of log h_eff; if holdout_seed is set, fit on the other seeds, score on it."""
    errs, s_of_t = [], {}
    for t in sorted({d[0] for d in data}):
        at = [d for d in data if d[0] == t]
        if law == "multiplicative":
            at = [d for d in at if d[1] > 0]
        fit = [d for d in at if holdout_seed is None or d[2] != holdout_seed]
        test = [d for d in at if holdout_seed is None or d[2] == holdout_seed]
        if not fit or not test:
            continue
        s = fit_s(law, np.array([d[1] for d in fit]), np.array([d[3] for d in fit]), p)
        s_of_t[t] = s
        pred = predict(law, np.array([d[1] for d in test]), s, p)
        errs += list(np.log(pred) - np.log([d[3] for d in test]))
    return float(np.sqrt(np.mean(np.square(errs)))), s_of_t, len(errs)


def analyse(name, data):
    seeds = sorted({d[2] for d in data})
    res = {}
    for law in ("additive", "multiplicative", "maximum"):
        rmse, s_t, n = score(data, law)
        loo = [score(data, law, holdout_seed=sd)[0] for sd in seeds]
        res[law] = {"rmse_log": rmse, "rmse_log_leave_one_seed_out": float(np.mean(loo)),
                    "n": n, "s_of_t": s_t}
    ps = np.linspace(0.5, 8.0, 76)
    best = min(ps, key=lambda p: score(data, "power", p)[0])
    res["power"] = {"p": float(best), "rmse_log": score(data, "power", best)[0]}
    print(f"\n{name}: {len(data)} checkpoints, seeds {seeds}")
    for law in ("additive", "multiplicative", "maximum"):
        r = res[law]
        print(f"  {law:<15} RMSE(log) {r['rmse_log']:.3f}   leave-one-seed-out "
              f"{r['rmse_log_leave_one_seed_out']:.3f}   (n={r['n']})")
    print(f"  best power p = {res['power']['p']:.2f}  RMSE(log) {res['power']['rmse_log']:.3f}")
    print("  s(t) under the additive law: " +
          ", ".join(f"{t // 1000}k:{s:.3g}" for t, s in res["additive"]["s_of_t"].items()))
    return res


def main() -> None:
    out = {"synthetic_h_le_0.1": analyse("synthetic (h <= 0.1, >= 10k)", load_synthetic()),
           "synthetic_all_h": analyse("synthetic (all h, >= 10k)", load_synthetic(max_h=1.0)),
           "cifar": analyse("CIFAR-10 (h in {4,5}, >= 5k)", load_cifar())}
    OUT.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
