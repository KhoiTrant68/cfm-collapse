"""Tables for the triangle experiment of scripts/learned_composition_2d.py.

Reads results/learned_composition_2d_20261021/<variant>_seed<k>/ and exact/; writes SUMMARY.md
there. The learned composite's Jacobian at the tie is compared with the exact profile Jacobian
Gamma_w(0) = ((1-m^2) - w m^2)/2 I (Corollary cor:spectral-threshold): in s-units the learned
value is the composite's d m_hat/dx at x = 0 divided by beta.

    python -m scripts.summarize_learned_composition_2d
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from scripts.learned_composition import EPS_OUT, N_EVAL
from scripts.learned_composition_2d import N_EXACT, OUT, R_LIST, VARIANTS, m_of, w_c

ROOT = pathlib.Path(OUT)
CLS_DELTA = 0.1


def fmt(v):
    v = np.asarray(v, float)
    return f"{v.mean():.3f} ± {v.std():.3f}" if len(v) > 1 else f"{v.mean():.3f}"


def classify(x, delta, atoms):
    c = np.full(x.shape[0], 4)
    for k, a in enumerate(atoms):
        c[np.linalg.norm(x - a, axis=1) < delta] = k
    c[np.linalg.norm(x, axis=1) < delta] = 3
    return c


def main() -> int:
    runs = {v: sorted(d for d in ROOT.glob(f"{v}_seed[0-9]") if (d / "summary.json").exists()) for v in VARIANTS}
    runs = {v: d for v, d in runs.items() if d}
    exact = {r["r"]: r for r in json.loads((ROOT / "exact" / "exact.json").read_text())["rows"]}
    ex_cls = np.load(ROOT / "exact" / "exact_classes.npz")
    atoms = np.array(json.loads((next(iter(runs.values()))[0] / "summary.json").read_text())["atoms"])
    m2 = m_of(2.0) ** 2
    L = ["# Learned guided label averaging on the triangle — summary", "",
         "Runs: " + ", ".join(f"{v} ({len(d)} seeds)" for v, d in runs.items()) +
         f". w_c = {w_c():.4f}. Learned: the first {N_EVAL} of the shared sources; exact: the first {N_EXACT}.", "",
         "## Midpoint occupancy of the composite L3 (|x| < 0.05), mean ± sd over seeds", "",
         "| w/w_c | exact Pr(X1 = 0) | " + " | ".join(f"{v} ε=1e-3 | {v} ε=1e-5" for v in runs) + " |",
         "|---|---|" + "---|---|" * len(runs)]
    for r in R_LIST:
        cells = []
        for v, dirs in runs.items():
            rows = [next(a for a in json.loads((d / "summary.json").read_text())["arms"]
                         if a["arm"] == "L3" and a["r"] == r) for d in dirs]
            for i in (EPS_OUT.index(1e-3), EPS_OUT.index(1e-5)):
                cells.append(fmt([row["by_eps"][i]["occ_0.05"] for row in rows]))
        L.append(f"| {r:g} | {exact[r]['midpoint_fraction']:.3f} | " + " | ".join(cells) + " |")
    L += ["", f"## Paired classes at ε = 1e-5 (δ = {CLS_DELTA}): recall of the exact midpoint basin", "",
          "| variant | w/w_c | exact midpoint (paired) | learned at midpoint | recall | learned off all atoms |",
          "|---|---|---|---|---|---|"]
    for v, dirs in runs.items():
        finals = [np.load(d / "final_states.npz") for d in dirs]
        for r in R_LIST:
            lc = [classify(f[f"L3_r{r:g}"][-1][:N_EXACT].astype(float), CLS_DELTA, atoms) for f in finals]
            ec = ex_cls[f"classes_r{r:g}"][:len(lc[0])]                    # paired on the shared sources
            mid = ec == 3
            rec = [float((c[mid] == 3).mean()) if mid.any() else float("nan") for c in lc]
            L.append(f"| {v} | {r:g} | {mid.mean():.3f} | {fmt([(c == 3).mean() for c in lc])} | "
                     f"{fmt(rec) if mid.any() else '–'} | {fmt([(c == 4).mean() for c in lc])} |")
    L += ["", "## Composite Jacobian at the tie in s-units, w = 2 w_c (exact eigenvalue "
          f"{((1 - m2) - 2 * w_c() * m2) / 2:.3f}, twice); median over seeds of the larger eigenvalue", ""]
    for v, dirs in runs.items():
        dg = [np.load(d / "field_diagnostics.npz") for d in dirs]
        eps = dg[0]["eps_diag"]
        beta = (1 - eps) / eps ** 2
        if v == next(iter(runs)):
            L += ["| variant | quantity | " + " | ".join(f"1-t={e:g}" for e in eps) + " |",
                  "|---|---|" + "---|" * len(eps)]
        for name, r in (("λ_max Γ̂, w=2w_c", 2.0), ("λ_max Γ̂, w=0.5w_c", 0.5)):
            w = r * w_c()
            lam = []
            for g in dg:
                J = (1 + w) / 3 * g["jac0"][:, :3].sum(1) - w * g["jac0"][:, 4]     # (eps, 2, 2)
                sym = 0.5 * (J + np.swapaxes(J, 1, 2)) / beta[:, None, None]
                lam.append(np.linalg.eigvalsh(sym)[:, -1])
            L.append(f"| {v} | {name} | " + " | ".join(f"{x:.3g}" for x in np.median(lam, 0)) + " |")
        ebl = np.median([g["ebl"][:, :3].mean(1) for g in dg], 0)
        L.append(f"| {v} | E_BL conditional | " + " | ".join(f"{x:.3g}" for x in ebl) + " |")
    L += ["", f"Exact eigenvalue at w = 0.5 w_c: {((1 - m2) - 0.5 * w_c() * m2) / 2:.3f}. "
          "Negative means the tie attracts the profile (Theorem thm:spectral(a)).", ""]
    (ROOT / "SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote", ROOT / "SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
