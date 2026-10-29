"""Tables and figure for the learned guided-label-averaging experiment.

Reads results/learned_composition_20261021/<variant>_seed<k>/ (scripts/learned_composition.py)
and exact/summary.json (scripts/learned_composition_exact.py); writes SUMMARY.md, tables.json
and fig_learned_composition.{pdf,png} next to them. Seeds are summarised by mean, population
standard deviation and a t-interval over seeds; sources are shared across arms, so learned and
exact arms are also compared source by source.

    python -m scripts.summarize_learned_composition
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib

import numpy as np
import torch

from scripts.figstyle import COLORS, OI, panel_tag, style, use_paper_style
from scripts.learned_composition import (B_LIST, DIAG_QUERIES, EPS_OUT, N_EVAL, N_SOURCES, R_LIST,
                                         SOURCE_SEED, VARIANTS, w_c)

import matplotlib.pyplot as plt  # noqa: E402  (after figstyle has set the backend)

LABEL = {"cfm_v": "CFM (main)", "cfm_v_tis": "CFM, late-t sampling", "cfm_v_sep": "CFM, separate unc.",
         "cfm_v_s": "CFM, velocity pred. + s input", "cfm_x": "CFM, data pred.",
         "cfm_x_s": "CFM, data pred. + s input", "distill_x_s": "distilled exact (positive control)"}
COLOR = {"cfm_v": COLORS["generated"], "cfm_v_tis": OI["orange"], "cfm_v_sep": OI["purple"],
         "cfm_v_s": OI["yellow"], "cfm_x": OI["green"],
         "cfm_x_s": OI["sky"], "distill_x_s": COLORS["accent"]}
EXACT_OF = {"L0": "E1", "L1": "E2", "L2": "E3", "L3": "E4", "L4": "E1"}
T95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}
UNC = len(DIAG_QUERIES)             # index of the unconditional branch in the diagnostics


def stats(values):
    v = np.asarray(values, float)
    n = len(v)
    sd = float(v.std()) if n > 1 else 0.0
    half = T95.get(n, 2.0) * float(v.std(ddof=1)) / math.sqrt(n) if n > 1 else float("nan")
    return {"mean": float(v.mean()), "sd": sd, "ci95": half, "n": n}


def fmt(s, digits=3):
    return f"{s['mean']:.{digits}f} ± {s['sd']:.{digits}f}" if s["n"] > 1 else f"{s['mean']:.{digits}f}"


def load(root):
    runs = {}
    for v in VARIANTS:
        for d in sorted(root.glob(f"{v}_seed[0-9]")):
            if (d / "summary.json").exists() and (d / "final_states.npz").exists():
                metadata = json.loads((d / "summary.json").read_text())
                if metadata.get("smoke", False) or metadata.get("n_sources") != N_EVAL:
                    print("skipping", d, "(smoke or incompatible source count)")
                    continue
                # An older fixed-step RK4 evaluation is not comparable; such runs are skipped.
                if "ROS2" not in json.loads((d / "summary.json").read_text()).get("solver", ""):
                    print("skipping", d, "(not evaluated with the ROS2 solver)")
                    continue
                runs.setdefault(v, []).append(d)
    exact = {}
    path = root / "exact" / "summary.json"
    if path.exists():
        for r in json.loads(path.read_text())["rows"]:
            exact[(r["arm"], r["B"], r["r"])] = r
    return runs, exact


def exact_row(exact, arm, B, r):
    e = EXACT_OF[arm]
    if e == "E1":
        return exact.get(("E1", 0.0, 0.0))
    if e == "E2":
        return exact.get(("E2", B, 0.0))
    return exact.get((e, B, r))


def exact_finite(row, eps, delta):
    return next(f for f in row["finite"] if f["eps"] == eps and f["delta"] == delta)


def exact_class(row, src):
    """Endpoint of each source under the exact field: -1, 0 (midpoint) or 1."""
    if row["basin"] is not None:
        lo, hi = row["basin"]
        return np.where(src < lo, -1, np.where(src > hi, 1, 0))
    return np.where(src > row["split"], 1, -1)


def classify(x, delta):
    c = np.full(x.shape, 2, int)
    for e in (-1, 0, 1):
        c[np.abs(x - e) < delta] = e
    return c


def occupancy_tables(runs, exact, src):
    out = []
    for v, dirs in runs.items():
        sums = [json.loads((d / "summary.json").read_text()) for d in dirs]
        keys = {(a["arm"], a["B"], a["r"]) for a in sums[0]["arms"]}
        for arm, B, r in sorted(keys):
            per = [next(a for a in s["arms"] if (a["arm"], a["B"], a["r"]) == (arm, B, r)) for s in sums]
            er = exact_row(exact, arm, B, r)
            for i, eps in enumerate(EPS_OUT):
                for delta in (0.02, 0.05, 0.1):
                    row = {"variant": v, "arm": arm, "B": B, "r": r, "eps": eps, "delta": delta,
                           "learned": stats([p["by_eps"][i][f"occ_{delta}"] for p in per]),
                           "ambiguous": stats([p["by_eps"][i][f"ambiguous_{delta}"] for p in per]),
                           "solver_disagree_max": max((p["by_eps"][i]["solver_class_disagree"] or 0.0)
                                                       for p in per)}
                    if er is not None:
                        f = exact_finite(er, eps, delta)
                        row["exact_endpoint_mass"] = er["basin_probability"]
                        row["exact_finite_prob"] = f["probability"]
                        lo, hi = f["interval"]
                        row["exact_finite_paired"] = float(((src > lo) & (src < hi)).mean())
                    out.append(row)
    return out


def agreement_tables(runs, exact, src):
    out = []
    for v, dirs in runs.items():
        finals = [np.load(d / "final_states.npz") for d in dirs]
        for B in B_LIST:
            for r in R_LIST:
                key = f"L3_B{B:g}_r{r:g}"
                er = exact.get(("E4", B, r))
                if er is None or key not in finals[0]:
                    continue
                ex = exact_class(er, src)
                for i, eps in enumerate(EPS_OUT):
                    if eps not in (1e-3, 1e-5):
                        continue
                    agree, prec, rec, amb = [], [], [], []
                    for f in finals:
                        lc = classify(f[key][i].astype(np.float64), 0.1)
                        agree.append(float((lc == ex).mean()))
                        amb.append(float((lc == 2).mean()))
                        ln, en = lc == 0, ex == 0
                        prec.append(float((ln & en).sum() / ln.sum()) if ln.any() else float("nan"))
                        rec.append(float((ln & en).sum() / en.sum()) if en.any() else float("nan"))
                    out.append({"variant": v, "B": B, "r": r, "eps": eps, "exact_mass": er["basin_probability"],
                                "exact_mass_paired": float((ex == 0).mean()),
                                "agreement": stats(agree), "ambiguous": stats(amb),
                                "precision_mid": stats([p for p in prec if p == p]) if any(p == p for p in prec) else None,
                                "recall_mid": stats([p for p in rec if p == p]) if any(p == p for p in rec) else None})
    return out


def field_tables(runs):
    """Boundary-layer error, tie slopes and the effective threshold, per variant and seed."""
    out = {}
    for v, dirs in runs.items():
        diags = [np.load(d / "field_diagnostics.npz") for d in dirs]
        s, eps = diags[0]["s_grid"], diags[0]["eps_diag"]
        i0 = int(np.argmin(np.abs(s)))
        t = 1 - eps
        beta = t / eps ** 2
        res = {"eps": eps.tolist(), "B": {}}
        for B in B_LIST:
            ip, im = DIAG_QUERIES.index(B), DIAG_QUERIES.index(-B)
            exact_p, exact_m, exact_u = np.tanh(s + B), np.tanh(s - B), np.tanh(s)
            per = {"ebl_cond": [], "ebl_unc": [], "kappa_c": [], "kappa_u": [], "offset": [],
                   "wc_eff": [], "ebl_comp": {r: [] for r in (1.0, 2.0, 10.0)},
                   "slope_s": {r: [] for r in (0.5, 1.0, 2.0, 10.0)}}
            for dg in diags:
                m, dx = dg["m_s"], dg["dmdx_s"]
                per["ebl_cond"].append(0.5 * (((m[:, ip] - exact_p) ** 2).mean(1) + ((m[:, im] - exact_m) ** 2).mean(1)))
                per["ebl_unc"].append(((m[:, UNC] - exact_u) ** 2).mean(1))
                kc = 0.5 * (dx[:, ip, i0] + dx[:, im, i0])
                ku = dx[:, UNC, i0]
                per["kappa_c"].append(kc); per["kappa_u"].append(ku)
                per["wc_eff"].append(np.where(ku > kc, (kc - 1) / np.where(ku > kc, ku - kc, 1), np.inf))
                per["offset"].append(0.5 * (m[:, ip, i0] + m[:, im, i0]) - m[:, UNC, i0])
                for r in per["ebl_comp"]:
                    w = r * w_c(B)
                    comp = (1 + w) / 2 * (m[:, ip] + m[:, im]) - w * m[:, UNC]
                    ex = (1 + w) / 2 * (exact_p + exact_m) - w * exact_u
                    per["ebl_comp"][r].append(((comp - ex) ** 2).mean(1))
                for r in per["slope_s"]:
                    w = r * w_c(B)
                    per["slope_s"][r].append(((1 + w) * kc - w * ku) / beta)
            res["B"][B] = {k: (np.array(val).tolist() if not isinstance(val, dict)
                              else {r: np.array(x).tolist() for r, x in val.items()})
                           for k, val in per.items()}
            res["B"][B]["exact_wc_eff"] = ((beta / np.cosh(B) ** 2 - 1) / (beta * np.tanh(B) ** 2)).tolist()
        out[v] = res
    return out


def validation_table(runs):
    out = {}
    for v, dirs in runs.items():
        vals = [json.loads((d / "summary.json").read_text())["validation"] for d in dirs]
        rows = []
        for j, r0 in enumerate(vals[0]):
            rows.append({"branch": r0["branch"], "t_lo": r0["t_lo"], "t_hi": r0["t_hi"],
                         "cfm_loss": stats([vv[j]["cfm_loss"] for vv in vals]),
                         "excess_m": stats([vv[j]["excess_m"] for vv in vals])})
        out[v] = rows
    return out


def figure(occ, agree, field, runs, exact, src, root):
    use_paper_style()
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.9))
    # (a) midpoint mass against w / w_c.
    ax = axes[0]
    rs = [r for r in R_LIST if r > 0]
    for B, ls in ((1.0, "-"), (2.0, "--")):
        em = [exact.get(("E4", B, r), {}).get("basin_probability", np.nan) for r in rs]
        ax.plot(rs, em, ls, color=COLORS["theory"], lw=1.6, label=f"exact endpoint, B={B:g}")
        for v in ("cfm_v", "distill_x_s"):
            pts = [next((o for o in occ if o["variant"] == v and o["arm"] == "L3" and o["B"] == B and o["r"] == r
                         and o["eps"] == 1e-5 and o["delta"] == 0.05), None) for r in rs]
            if all(p is None for p in pts):
                continue
            m = np.array([p["learned"]["mean"] if p else np.nan for p in pts])
            e = np.array([p["learned"]["ci95"] if p else np.nan for p in pts])
            ax.errorbar(rs, m, yerr=e, fmt="o" if v == "cfm_v" else "s", ls=ls, ms=4, lw=1.2, capsize=2,
                        color=COLOR[v], label=f"{LABEL[v]}, B={B:g}")
    ax.axvline(1, color="#888", lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xlabel(r"$w/w_c$"); ax.set_ylabel(r"$\Pr(|X_{1-\varepsilon}|<0.05)$")
    ax.set_title(r"midpoint mass, $\varepsilon=10^{-5}$")
    ax.legend(fontsize=6.5, loc="upper left")
    # (b) effective threshold w_c(t) / w_c from the tie slopes.
    ax = axes[1]
    for v, res in field.items():
        d = res["B"][1.0]
        epsg = np.array(res["eps"])
        wc = np.array(d["wc_eff"]) / w_c(1.0)
        med = np.nanmedian(np.where(np.isfinite(wc), wc, np.nan), 0)
        ax.plot(epsg, med, "o-", ms=3, lw=1.2, color=COLOR[v], label=LABEL[v])
    epsg = np.array(next(iter(field.values()))["eps"])
    ax.plot(epsg, np.array(next(iter(field.values()))["B"][1.0]["exact_wc_eff"]) / w_c(1.0), "-",
            color=COLORS["theory"], lw=1.6, label="exact field")
    ax.axhline(1, color="#888", lw=0.8, ls=":")
    ax.set_xscale("log"); ax.invert_xaxis(); ax.set_xlabel(r"$1-t$")
    ax.set_ylabel(r"$\hat w_c(t)/w_c$ (B=1)"); ax.set_title("threshold implied by tie slopes")
    ax.set_ylim(-1, 6); ax.legend(fontsize=6.5)
    # (c) paired sources, B = 1, w = 2 w_c.
    ax = axes[2]
    if "cfm_v" in runs and ("E4", 1.0, 2.0) in exact:
        f = np.load(runs["cfm_v"][0] / "final_states.npz")["L3_B1_r2"][-1].astype(np.float64)
        ex = exact_class(exact[("E4", 1.0, 2.0)], src)
        sel = np.random.default_rng(0).choice(len(src), 2000, replace=False)
        for c, col, lab in ((0, COLORS["generated"], "exact: midpoint"), (1, COLORS["source"], "exact: atom"),
                            (-1, COLORS["source"], None)):
            k = sel[ex[sel] == c]
            ax.scatter(src[k], f[k], s=4, color=col, alpha=0.6, label=lab, lw=0)
        lo, hi = exact[("E4", 1.0, 2.0)]["basin"]
        for b in (lo, hi):
            ax.axvline(b, color=COLORS["theory"], lw=0.8, ls="--")
        ax.set_xlabel(r"source $x_0$"); ax.set_ylabel(r"learned $X_{1-10^{-5}}$")
        ax.set_title(r"paired sources, $B=1$, $w=2w_c$ (seed 0)"); ax.legend(fontsize=7, markerscale=3)
    # (d) terminal-gap sensitivity.
    ax = axes[3]
    for r, mk in ((0.9, "v"), (1.1, "o"), (2.0, "s")):
        pts = [next((o for o in occ if o["variant"] == "cfm_v" and o["arm"] == "L3" and o["B"] == 1.0
                     and o["r"] == r and o["eps"] == e and o["delta"] == 0.05), None) for e in EPS_OUT]
        if all(p is None for p in pts):
            continue
        ax.errorbar(EPS_OUT, [p["learned"]["mean"] for p in pts], yerr=[p["learned"]["ci95"] for p in pts],
                    marker=mk, ms=4, lw=1.2, capsize=2, color=COLOR["cfm_v"], label=f"learned, $w={r:g}w_c$")
        ax.plot(EPS_OUT, [p.get("exact_finite_paired", np.nan) for p in pts], marker=mk, ms=4, lw=1.0,
                ls="--", color=COLORS["theory"], mfc="none", label=f"exact, $w={r:g}w_c$")
    ax.set_xscale("log"); ax.invert_xaxis(); ax.set_xlabel(r"terminal gap $\varepsilon$")
    ax.set_ylabel(r"$\Pr(|X_{1-\varepsilon}|<0.05)$"); ax.set_title(r"terminal-gap sensitivity, $B=1$")
    ax.legend(fontsize=6.5)
    for a, tag in zip(axes, "abcd"):
        style(a); panel_tag(a, tag)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(root / f"fig_learned_composition.{ext}", bbox_inches="tight")
    plt.close(fig)


def markdown(occ, agree, field, val, runs, exact, root):
    L = ["# Learned guided label averaging — summary", "",
         f"Runs: " + ", ".join(f"{v} ({len(d)} seeds)" for v, d in runs.items()) +
         f". Sources: the first {N_EVAL} of {N_SOURCES} shared Gaussian draws (seed {SOURCE_SEED}). "
         "Mean ± population sd over seeds.", ""]

    def occ_of(v, arm, B, r, eps, delta=0.05):
        return next((o for o in occ if o["variant"] == v and o["arm"] == arm and o["B"] == B and o["r"] == r
                     and o["eps"] == eps and o["delta"] == delta), None)
    for B in B_LIST:
        L += [f"## Midpoint occupancy of the composite L3, B = {B:g} (w_c = {w_c(B):.4f}), δ = 0.05", "",
              "| w/w_c | exact endpoint mass | exact ε=1e-5 (paired) | " +
              " | ".join(f"{v} ε=1e-3 | {v} ε=1e-5" for v in runs) + " |",
              "|---|---|---|" + "---|---|" * len(runs)]
        for r in R_LIST:
            o = occ_of("cfm_v", "L3", B, r, 1e-5) or next(iter(
                [occ_of(v, "L3", B, r, 1e-5) for v in runs if occ_of(v, "L3", B, r, 1e-5)]), None)
            if o is None:
                continue
            cells = []
            for v in runs:
                a, b = occ_of(v, "L3", B, r, 1e-3), occ_of(v, "L3", B, r, 1e-5)
                cells += [fmt(a["learned"]) if a else "–", fmt(b["learned"]) if b else "–"]
            L.append(f"| {r:g} | {o.get('exact_endpoint_mass', float('nan')):.3f} | "
                     f"{o.get('exact_finite_paired', float('nan')):.3f} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["## Controls (δ = 0.05, ε = 1e-5): learned occupancy; every exact counterpart has endpoint mass 0", "",
          "| variant | arm | B | w/w_c | learned | exact ε=1e-5 (paired) |", "|---|---|---|---|---|---|"]
    for v in runs:
        for o in occ:
            if (o["variant"] == v and o["arm"] in ("L0", "L1", "L2", "L4") and o["eps"] == 1e-5
                    and o["delta"] == 0.05 and o["r"] in (0.0, 1.0, 2.0, 10.0)):
                L.append(f"| {v} | {o['arm']} | {o['B']:g} | {o['r']:g} | {fmt(o['learned'])} | "
                         f"{o.get('exact_finite_paired', float('nan')):.3f} |")
    L += ["", "## Paired endpoint classes of L3 against the exact composite (δ_class = 0.1)", "",
          "| variant | B | w/w_c | ε | exact mass (paired) | agreement | precision (mid) | recall (mid) | ambiguous |",
          "|---|---|---|---|---|---|---|---|---|"]
    for a in agree:
        if a["r"] in (0.9, 1.1, 1.5, 2.0, 5.0, 10.0):
            p = fmt(a["precision_mid"]) if a["precision_mid"] else "–"
            rc = fmt(a["recall_mid"]) if a["recall_mid"] else "–"
            L.append(f"| {a['variant']} | {a['B']:g} | {a['r']:g} | {a['eps']:g} | {a['exact_mass_paired']:.3f} | "
                     f"{fmt(a['agreement'])} | {p} | {rc} | {fmt(a['ambiguous'])} |")
    L += ["", "## Boundary layer (B = 1): mean over s∈[-3,3] of (m̂ - m*)², median over seeds", "",
          "| variant | quantity | " + " | ".join(f"1-t={e:g}" for e in next(iter(field.values()))["eps"]) + " |",
          "|---|---|" + "---|" * len(next(iter(field.values()))["eps"])]
    for v, res in field.items():
        d = res["B"][1.0]
        for name, arr in (("E_BL cond ±B", d["ebl_cond"]), ("E_BL unc", d["ebl_unc"]),
                          ("E_BL composite w=2w_c", d["ebl_comp"][2.0]),
                          ("tie slope ∂sF̂ at w=2w_c (exact -0.420)", d["slope_s"][2.0]),
                          ("ŵ_c(t)/w_c", (np.array(d["wc_eff"]) / w_c(1.0)).tolist()),
                          ("guidance direction at tie, avg_c(0)-m_u(0)", d["offset"])):
            med = np.nanmedian(np.where(np.isfinite(np.array(arr, float)), np.array(arr, float), np.nan), 0)
            L.append(f"| {v} | {name} | " + " | ".join(f"{x:.3g}" for x in med) + " |")
        L.append(f"| exact | ŵ_c(t)/w_c | " + " | ".join(f"{x / w_c(1.0):.3g}" for x in d["exact_wc_eff"]) + " |")
    L += ["", "## Validation (held-out interpolant samples): excess risk E|m̂ - m*|², conditional branch", "",
          "| variant | " + " | ".join(f"t∈[{r['t_lo']:g},{r['t_hi']:g})" for r in next(iter(val.values())) if r["branch"] == "cond") + " |",
          "|---|" + "---|" * sum(1 for r in next(iter(val.values())) if r["branch"] == "cond")]
    for v, rows in val.items():
        L.append(f"| {v} | " + " | ".join(f"{r['excess_m']['mean']:.2e}" for r in rows if r["branch"] == "cond") + " |")
    dis = max((o["solver_disagree_max"] for o in occ), default=float("nan"))
    L += ["", f"Largest fraction of sources whose class (δ = 0.1) of the composite L3 differs between ROS2 tolerances 1e-5 and 1e-7: {dis:.4f}.", ""]
    (root / "SUMMARY.md").write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/learned_composition_20261021")
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    runs, exact = load(root)
    src = torch.randn(N_SOURCES, generator=torch.Generator().manual_seed(SOURCE_SEED)).double().numpy()[:N_EVAL]
    occ = occupancy_tables(runs, exact, src)
    agree = agreement_tables(runs, exact, src) if exact else []
    field = field_tables(runs)
    val = validation_table(runs)
    (root / "tables.json").write_text(json.dumps({"occupancy": occ, "agreement": agree, "field": field,
                                                  "validation": val}, indent=1), encoding="utf-8")
    markdown(occ, agree, field, val, runs, exact, root)
    figure(occ, agree, field, runs, exact, src, root)
    print(f"wrote {root/'SUMMARY.md'}, tables.json, fig_learned_composition.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
