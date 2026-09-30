"""Does h_eff carry information about calibration beyond training progress?

Reads the per-checkpoint table written by audit_calibration_v2.py and answers the two
questions of the round-3 review.

1. Baselines and confounding. Spearman correlation of each audit statistic with the
   held-out calibration targets, pooled over (run, checkpoint); the same after partialling
   out log(iteration), log(iteration) and the training bandwidth h, and the training
   loss; and the average across-run correlation at a fixed iteration, where training
   time cannot be the explanation.

2. A stopping rule that needs no held-out pairs on the run it is applied to. For each
   run, the target h_eff* is the median h_eff of the best-validation checkpoints of the
   runs of the *other* seeds (leave-one-seed-out); the rule picks the checkpoint whose
   h_eff is closest to h_eff* in log. It is compared with the oracle (best test error),
   the last checkpoint, the same transfer rule on the training loss and on the
   iteration, and direct selection on 30 validation pairs of the run itself.

Usage:
    uv run python scripts/analyze_audit_v2.py --exp exp1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

PREDICTORS = ("h_eff", "h_mean", "trace_raw", "train_loss", "iter", "on_atom_train", "beta")
TARGETS = ("test_coverage_90", "test_calibration_error", "test_pit_error", "test_extraction")


def ranks(a):
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    r[order] = np.arange(len(a))
    for v in np.unique(a):
        m = a == v
        r[m] = r[m].mean()
    return r


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 4:
        return float("nan")
    return float(np.corrcoef(ranks(x[ok]), ranks(y[ok]))[0, 1])


def partial_spearman(x, y, controls):
    """Spearman partial correlation: correlate rank residuals after regressing on the
    ranks of the control variables."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    C = [np.asarray(c, float) for c in controls]
    ok = np.isfinite(x) & np.isfinite(y) & np.all([np.isfinite(c) for c in C], axis=0)
    rx, ry = ranks(x[ok]), ranks(y[ok])
    Z = np.column_stack([np.ones(ok.sum())] + [ranks(c[ok]) for c in C])
    res = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return float(np.corrcoef(res(rx), res(ry))[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=["exp1", "exp2"], required=True)
    ap.add_argument("--target", default="test_pit_error",
                    help="error the stopping rule minimises")
    args = ap.parse_args()
    rows = json.loads(Path(f"results/{args.exp}/_heff/audit_calibration_v2.json")
                      .read_text(encoding="utf-8"))
    col = lambda k: np.array([r.get(k, np.nan) for r in rows], float)
    it = col("iter")
    logit, hs = np.log(it), col("h")
    out = {"n": len(rows), "pooled": {}, "partial_iter": {}, "partial_iter_h": {},
           "partial_loss": {}, "fixed_iter": {}}

    print(f"{args.exp}: {len(rows)} (run, checkpoint) pairs\n")
    head = f"{'predictor':<15}" + "".join(f"{t:>26}" for t in TARGETS)
    for name, fn in (
        ("pooled", lambda p, t: spearman(col(p), col(t))),
        ("partial_iter", lambda p, t: partial_spearman(col(p), col(t), [logit])
         if p != "iter" else float("nan")),
        ("partial_iter_h", lambda p, t: partial_spearman(col(p), col(t), [logit, hs])
         if p != "iter" else float("nan")),
        ("partial_loss", lambda p, t: partial_spearman(col(p), col(t), [col("train_loss")])
         if p != "train_loss" else float("nan")),
    ):
        print(f"--- Spearman, {name} ---\n{head}")
        for p in PREDICTORS:
            vals = {t: fn(p, t) for t in TARGETS}
            out[name][p] = vals
            print(f"{p:<15}" + "".join(f"{vals[t]:>26.3f}" for t in TARGETS))
        print()

    iters = sorted(set(it.astype(int)))
    print(f"--- mean across-run Spearman at a fixed iteration ({len(iters)} iterations) ---\n{head}")
    for p in PREDICTORS:
        vals = {}
        for t in TARGETS:
            per = []
            for i in iters:
                m = it == i
                if m.sum() >= 5:
                    per.append(spearman(col(p)[m], col(t)[m]))
            vals[t] = float(np.nanmean(per)) if per else float("nan")
        out["fixed_iter"][p] = vals
        print(f"{p:<15}" + "".join(f"{vals[t]:>26.3f}" for t in TARGETS))

    # ---- stopping rules --------------------------------------------------- #
    tgt, val = args.target, args.target.replace("test_", "val_")
    runs = sorted({r["run"] for r in rows})
    by_run = {rn: sorted((r for r in rows if r["run"] == rn), key=lambda r: r["iter"])
              for rn in runs}
    seed_of = {rn: by_run[rn][0]["seed"] for rn in runs}

    def transfer(key, rn, log_space=True):
        others = [x for x in runs if seed_of[x] != seed_of[rn]]
        best = [min(by_run[x], key=lambda r: r[val])[key] for x in others]
        star = float(np.median(np.log(best) if log_space else best))
        f = (lambda v: abs(np.log(v) - star)) if log_space else (lambda v: abs(v - star))
        return min(by_run[rn], key=lambda r: f(r[key]))

    rules = {
        "oracle (best test)": lambda rn: min(by_run[rn], key=lambda r: r[tgt]),
        "last checkpoint": lambda rn: by_run[rn][-1],
        "validation on this run (30 pairs)": lambda rn: min(by_run[rn], key=lambda r: r[val]),
        "h_eff transferred from other seeds": lambda rn: transfer("h_eff", rn),
        "train loss transferred": lambda rn: transfer("train_loss", rn),
        "iteration transferred": lambda rn: transfer("iter", rn),
    }
    print(f"\n--- stopping rules, mean {tgt} of the selected checkpoint over {len(runs)} runs ---")
    out["stopping"] = {}
    for name, rule in rules.items():
        picks = [rule(rn) for rn in runs]
        err = float(np.mean([r[tgt] for r in picks]))
        cov = float(np.mean([r["test_coverage_90"] for r in picks]))
        out["stopping"][name] = {"error": err, "coverage_90": cov,
                                 "picked_iters": [int(r["iter"]) for r in picks]}
        print(f"  {name:<38} {tgt}={err:.4f}   90% coverage={cov:.3f}")
    path = Path(f"results/{args.exp}/_heff/audit_v2_analysis.json")
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
