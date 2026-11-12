"""Summary of the label-bottleneck and tie-agnostic triangle runs (scripts/server_bottleneck_2d_cpu.sh).

Reads results/bottleneck_2d_20261107/<variant>_seed<k>/summary.json, the exact composite at the
bottleneck priors (exact_bottleneck/) and, for reference, the tie-centred runs and exact composite
of results/learned_composition_2d_20261021. Midpoint occupancy |x| < 0.05 at 1 - t = 1e-5; for
cfm_x_sq, w/w_c is in units of w_c(B_Q), the threshold of the bottleneck priors.

    python -m scripts.summarize_bottleneck_2d [results/bottleneck_2d_20261107]
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

from scripts.learned_composition import EPS_OUT
from scripts.learned_composition_2d import B_Q, R_CONTROLS, R_LIST, w_c

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results/bottleneck_2d_20261107")
REF = pathlib.Path("results/learned_composition_2d_20261021")
I_EPS = EPS_OUT.index(1e-5)


def occ(dirs, arm, r):
    vals = []
    for d in dirs:
        rows = json.loads((d / "summary.json").read_text())["arms"]
        vals.append(next(a for a in rows if a["arm"] == arm and a["r"] == r)["by_eps"][I_EPS]["occ_0.05"])
    return np.array(vals)


def fmt(v):
    return f"{v.mean():.3f} ± {v.std():.3f}" if len(v) > 1 else f"{v.mean():.3f}"


def main() -> int:
    runs = {v: sorted(d for d in ROOT.glob(f"{v}_seed[0-9]") if (d / "summary.json").exists())
            for v in ("cfm_x_sq", "cfm_x_o", "cfm_x_a")}
    runs["cfm_x_s (tie-centred, reference)"] = sorted(d for d in REF.glob("cfm_x_s_seed[0-9]"))
    runs = {v: d for v, d in runs.items() if d}
    ex = {r["r"]: r["midpoint_fraction"] for r in json.loads((REF / "exact" / "exact.json").read_text())["rows"]}
    exq_path = ROOT / "exact_bottleneck" / "exact.json"
    exq = ({r["r"]: r["midpoint_fraction"] for r in json.loads(exq_path.read_text())["rows"]}
           if exq_path.exists() else {})
    out = {"B_Q": B_Q, "w_c": w_c(), "w_c_Q": w_c(B_Q), "exact": ex, "exact_bottleneck": exq, "runs": {}}
    L = ["# Label bottleneck and tie-agnostic inputs on the triangle", "",
         f"w_c = {w_c():.4f}; bottleneck cell priors are vertex priors with B_Q = {B_Q:.6f}, "
         f"w_c(B_Q) = {w_c(B_Q):.4f}. Midpoint occupancy |x| < 0.05 at 1 - t = 1e-5, mean ± sd over seeds.", "",
         "## Composite L3", "", "| w/w_c | exact | exact (bottleneck priors) | " + " | ".join(runs) + " |",
         "|---|---|---|" + "---|" * len(runs)]
    for r in R_LIST:
        cells = []
        for v, dirs in runs.items():
            o = occ(dirs, "L3", r)
            out["runs"].setdefault(v, {}).setdefault("L3", {})[str(r)] = o.tolist()
            cells.append(fmt(o))
        L.append(f"| {r:g} | {ex.get(r, float('nan')):.3f} | {exq.get(r, float('nan')):.3f} | " + " | ".join(cells) + " |")
    L += ["", "## Single-query guidance L2 (exact: no midpoint mass at any w)", "",
          "| w/w_c | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    for r in R_CONTROLS:
        cells = []
        for v, dirs in runs.items():
            o = occ(dirs, "L2", r)
            out["runs"].setdefault(v, {}).setdefault("L2", {})[str(r)] = o.tolist()
            cells.append(fmt(o))
        L.append(f"| {r:g} | " + " | ".join(cells) + " |")
    (ROOT / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (ROOT / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
