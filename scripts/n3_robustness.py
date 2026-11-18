"""Robustness of the N3 memorization AUCs: stratified bootstrap CIs and sensitivity to the off-atom threshold.

Scores, each at every noise level of the 18-step Heun sampler (AUC = P(off-atom score > on-atom score)):
  e_learned  |D - m*| along the learned trajectory           (per_sample.npz of scripts.n3_edm_memorization)
  nn_hat     distance from D to the nearest training image    (same file; the cheap baseline)
  rho        |D - m*| / |x - y1|, y1 = endpoint's nearest image (q_per_sample.npz of scripts.n3_directional_q)
  rhoA, radA the same with the anchor chosen at sigma_k as the nearest image of D(x_k), i.e. without endpoint
             information; dD is nn_hat on that run
The off-atom label is d1/d2 >= thr, thr in {0.2, 1/3, 0.5}. The CI for an AUC difference resamples on- and
off-atom samples jointly, so it is paired.

    python -m scripts.n3_robustness --n3 <per_sample.npz> --q <q_per_sample.npz> [--q <...>] --out <file.md>
"""
from __future__ import annotations

import argparse
import pathlib

import numpy as np

from scripts.n3_edm_memorization import auc

THRS = (0.2, 1 / 3, 0.5)


def boot(scores, off, B, rng, pairs=()):
    """AUC point estimates and 95% stratified-bootstrap intervals for each score and each paired difference."""
    io, ii = np.where(off)[0], np.where(~off)[0]
    est = {k: auc(v[off], v[~off]) for k, v in scores.items()}
    for a, b in pairs:
        est[f"{a}-{b}"] = est[a] - est[b]
    draws = {k: [] for k in est}
    for _ in range(B):
        so, si = rng.choice(io, len(io)), rng.choice(ii, len(ii))
        d = {k: auc(v[so], v[si]) for k, v in scores.items()}
        for a, b in pairs:
            d[f"{a}-{b}"] = d[a] - d[b]
        for k in est:
            draws[k].append(d[k])
    return {k: (est[k], *np.nanpercentile(draws[k], [2.5, 97.5])) for k in est}


def fmt(e):
    return f"{e[0]:.3f} [{e[1]:.3f}, {e[2]:.3f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n3", required=True); ap.add_argument("--q", action="append", default=[])
    ap.add_argument("--B", type=int, default=2000); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", default="4,5,6,7,8,9,10,13,15"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed); steps = [int(s) for s in a.steps.split(",")]
    L = ["# Robustness of the N3 AUCs (bootstrap 95% CIs, off-atom threshold)", "",
         f"Stratified bootstrap, B = {a.B}. AUC = P(off-atom score > on-atom score). "
         "Differences are paired (same resample).", ""]

    z = np.load(a.n3); r = z["d1"] / z["d2"]
    L += [f"## {a.n3}", "", "| thr | off-atom | " + " | ".join(f"sigma {z['sigma'][i]:.3g}" for i in steps) + " |",
          "|---|---|" + "---|" * len(steps)]
    for thr in THRS:
        off = r >= thr
        cells = []
        for i in steps:
            if off.sum() < 2 or (~off).sum() < 2:
                cells.append("-"); continue
            e = boot({"e": z["e_learned"][:, i], "nn": z["nn_hat"][:, i]}, off, a.B, rng, pairs=(("e", "nn"),))
            cells.append(f"e {fmt(e['e'])}<br>nn {fmt(e['nn'])}<br>e-nn {fmt(e['e-nn'])}")
        L.append(f"| {thr:.3g} | {int(off.sum())} | " + " | ".join(cells) + " |")

    for qf in a.q:
        z = np.load(qf); r = z["d1"] / z["d2"]
        has_anchor = "rhoA" in z.files and np.isfinite(z["rhoA"]).any()
        L += ["", f"## {qf}", ""]
        if has_anchor:
            L += ["Anchor agreement: fraction of on-atom samples whose sigma_k anchor (nearest image of D(x_k)) is "
                  "the endpoint's nearest image: " + ", ".join(
                      f"sigma {z['sigma'][i]:.3g}: {np.mean(z['anc'][r < 1/3, i] == z['nn1'][r < 1/3]):.3f}"
                      for i in steps), ""]
        L += ["| thr | off-atom | sigma | rho (endpoint anchor) | " +
              ("rhoA (sigma anchor) | radA | dD = nn_hat | rhoA - dD | radA - dD |" if has_anchor else ""),
              "|---|---|---|---|" + ("---|---|---|---|---|" if has_anchor else "")]
        for thr in THRS:
            off = r >= thr
            if off.sum() < 2 or (~off).sum() < 2:
                L.append(f"| {thr:.3g} | {int(off.sum())} | - | - |" + (" - | - | - | - | - |" if has_anchor else "")); continue
            for i in steps:
                sc = {"rho": z["err"][:, i] / z["n1"][:, i]}
                pairs = ()
                if has_anchor:
                    sc.update(rhoA=z["rhoA"][:, i], radA=z["radA"][:, i], dD=z["dD"][:, i]); pairs = (("rhoA", "dD"), ("radA", "dD"))
                e = boot(sc, off, a.B, rng, pairs=pairs)
                L.append(f"| {thr:.3g} | {int(off.sum())} | {z['sigma'][i]:.3g} | {fmt(e['rho'])} | " +
                         (" | ".join(fmt(e[k]) for k in ("rhoA", "radA", "dD", "rhoA-dD", "radA-dD")) + " |" if has_anchor else ""))
    pathlib.Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
