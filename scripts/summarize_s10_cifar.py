"""S10: does the scaled field error separate the off-atom CIFAR-10 samples from the others?

Reads the per_sample_ckpt_<iter>.npz files written by scripts/exp_c_cifar_transfer.py, in which
e_learned[n, g] = (1-t)|Delta(Z_t)| = |m_hat - m*| along the learned path at grid point g, against
the exact field at the training bandwidth h. At the last cutoff a sample is off-atom when the ratio
d1/d2 of its nearest and second-nearest training image is at least 1/3 (as in App. C.4).

For every run it reports
  - the off-atom fraction;
  - the median final scaled error of off-atom and of on-atom samples, and the AUC with which the
    final scaled error separates them (0.5 = no separation);
  - the fraction of samples whose distance d1 to the nearest training image is at most the final
    scaled error (the form of Theorem thm:transfer; it is an identity in the limit, so this checks
    the bookkeeping, not the theory);
  - the median scaled error of each group along the path, so one sees when the groups separate;
  - among on-atom samples, the fraction that end on the same training image as the exact field
    integrated from the same source.
e_exact[n, g] is the same network error |m_hat - m*| evaluated along the exact path from the same
source, not an error of the exact field (which is zero against itself).

Pooled over the seeds of each bandwidth h > 0 (s10_pooled_ckpt_<iter>.json) it also reports the AUC
of the learned-path and of the exact-path error at every grid time, and the true/false positive
rates of the rule "final scaled error > c" for c = 3, 4, 5.

    python -m scripts.summarize_s10_cifar --dir results/s10_cifar_transfer_<date> [--checkpoint 60000]
"""
import argparse, json, pathlib, re
import numpy as np

RATIO = 1.0 / 3.0


def auc(pos, neg):
    """P(pos > neg) + P(pos = neg)/2, by ranks."""
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    x = np.concatenate([pos, neg]); r = np.empty(len(x)); order = x.argsort(kind="mergesort")
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):                       # average ranks of ties
        m = x == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--checkpoint", type=int, default=60000)
    a = ap.parse_args()
    D = pathlib.Path(a.dir)
    rows, L, pooled = [], [], {}
    for f in sorted(D.glob(f"*/per_sample_ckpt_{a.checkpoint}.npz")):
        z = np.load(f)
        k = len(z["eps_out"]) - 1
        off = z[f"learned_ratio_{k}"] >= RATIO
        e = z["e_learned"]; ef = e[:, -1]
        g = z["grid_tau"]
        prof = {}
        for tau in (1.0, 2.0, 3.0, 4.6, 6.9, 9.2):
            j = int(np.argmin(np.abs(g - tau)))
            prof[f"{1 - np.exp(-g[j]):.4f}"] = {"off": float(np.median(e[off, j])) if off.any() else None,
                                                "on": float(np.median(e[~off, j])) if (~off).any() else None,
                                                "exact": float(np.median(z["e_exact"][:, j]))}
        rec = {"run": f.parent.name, "n": int(len(off)), "off_frac": float(off.mean()),
               "e_final_off_median": float(np.median(ef[off])) if off.any() else None,
               "e_final_on_median": float(np.median(ef[~off])) if (~off).any() else None,
               "auc_final": auc(ef[off], ef[~off]),
               "d1_le_e_final": float((z[f"learned_d1_{k}"] <= ef * (1 + 1e-3) + 1e-3).mean()),
               "exact_e_final_max": float(z["e_exact"][:, -1].max()),
               "exact_off_frac": float((z[f"exact_ratio_{k}"] >= RATIO).mean()),
               "same_atom_on": float((z[f"learned_nn_{k}"][~off] == z[f"exact_nn_{k}"][~off]).mean())
               if (~off).any() else None,
               "profile_median": prof}
        rows.append(rec)
        P = pooled.setdefault(re.search(r"_h(\d+)_s\d+$", f.parent.name).group(1), {})
        for key, v in (("off", off), ("eL", e), ("eX", z["e_exact"])):
            P.setdefault(key, []).append(v)
        P["t"] = 1 - np.exp(-g)
    (D / f"s10_summary_ckpt_{a.checkpoint}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    pool = {}
    for h, P in sorted(pooled.items()):
        off = np.concatenate(P["off"]); eL = np.concatenate(P["eL"]); eX = np.concatenate(P["eX"])
        if not off.any():
            continue
        ef = eL[:, -1]
        pool[f"h{h}"] = {"n": int(len(off)), "off_frac": float(off.mean()), "t": [float(v) for v in P["t"]],
                         "auc_learned": [auc(eL[off, j], eL[~off, j]) for j in range(eL.shape[1])],
                         "auc_exact_path": [auc(eX[off, j], eX[~off, j]) for j in range(eX.shape[1])],
                         "threshold": {str(c): {"tpr": float((ef[off] > c).mean()), "fpr": float((ef[~off] > c).mean())}
                                       for c in (3, 4, 5)}}
    (D / f"s10_pooled_ckpt_{a.checkpoint}.json").write_text(json.dumps(pool, indent=1), encoding="utf-8")
    L = ["# S10: scaled field error of off-atom and on-atom CIFAR-10 samples", "",
         "| run | off-atom | median (1-t)|Δ| off | on | AUC | d1 ≤ e | exact e max | exact off |",
         "|---|---|---|---|---|---|---|---|"]
    fmt = lambda v: "–" if v is None else f"{v:.3f}"  # noqa: E731
    for r in rows:
        L.append(f"| {r['run']} | {r['off_frac']:.3f} | {fmt(r['e_final_off_median'])} | {fmt(r['e_final_on_median'])} | "
                 f"{fmt(r['auc_final'])} | {r['d1_le_e_final']:.3f} | {r['exact_e_final_max']:.3g} | {r['exact_off_frac']:.3f} |")
    L += ["", "Median scaled error along the path (off / on / exact) at t:", ""]
    for r in rows:
        L.append(f"- {r['run']}: " + "; ".join(f"t={t}: {fmt(v['off'])} / {fmt(v['on'])} / {fmt(v['exact'])}"
                                              for t, v in r["profile_median"].items()))
    L += ["", "Same training image as the exact field, among on-atom samples:", ""]
    L += [f"- {r['run']}: {fmt(r['same_atom_on'])}" for r in rows]
    for h, q in pool.items():
        L += ["", f"Pooled {h} (n={q['n']}, off-atom {q['off_frac']:.3f}): AUC learned path / exact path at t:", ""]
        L += ["- " + "; ".join(f"t={t:.3f}: {u:.3f} / {v:.3f}" for t, u, v in
                               zip(q["t"], q["auc_learned"], q["auc_exact_path"]))]
        L += ["- final error > c: " + "; ".join(f"c={c}: TPR {v['tpr']:.3f}, FPR {v['fpr']:.3f}" for c, v in q["threshold"].items())]
    (D / f"S10_SUMMARY_ckpt_{a.checkpoint}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
