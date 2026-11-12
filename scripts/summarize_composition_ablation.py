"""Midpoint occupancy of the composition ablation (cfm_v_s, cfm_x) next to cfm_v and cfm_x_s.

    python scripts/summarize_composition_ablation.py
Writes results/composition_ablation_20261105/SUMMARY.md and summary.json.
"""
import json
from pathlib import Path

import numpy as np

ABL = Path("results/composition_ablation_20261105")
OLD = Path("results/learned_composition_20261021")
EPS, DELTA = 1e-5, 0.05
ROWS = {"cfm_v": OLD, "cfm_v_s": ABL, "cfm_x": ABL, "cfm_x_s": OLD}


def occ(root, variant):
    per = {}
    for seed in range(5):
        s = json.loads((root / f"{variant}_seed{seed}" / "summary.json").read_text(encoding="utf-8"))
        for arm in s["arms"]:
            if arm["arm"] != "L3":
                continue
            row = next(e for e in arm["by_eps"] if abs(e["eps"] - EPS) < 1e-12)
            per.setdefault((arm["B"], arm["r"]), []).append(row[f"occ_{DELTA:g}"])
    assert all(len(v) == 5 for v in per.values()), variant
    return {k: (float(np.mean(v)), float(np.std(v))) for k, v in sorted(per.items())}


exact = {(r["B"], r["r"]): r["basin_probability"]
         for r in json.loads((OLD / "exact" / "summary.json").read_text(encoding="utf-8"))["rows"]
         if r["arm"] == "E4"}
res = {v: occ(root, v) for v, root in ROWS.items()}
keys = sorted(res["cfm_x"])
lines = ["# Composition ablation: L3 midpoint occupancy (eps=1e-5, delta=0.05, 5 seeds)", "",
         "| B | w/w_c | exact | " + " | ".join(ROWS) + " |", "|---|---|---|" + "---|" * len(ROWS)]
for B, r in keys:
    lines.append(f"| {B:g} | {r:g} | {exact.get((B, r), float('nan')):.3f} | "
                 + " | ".join(f"{res[v][(B, r)][0]:.3f} ± {res[v][(B, r)][1]:.3f}" if (B, r) in res[v] else "--"
                              for v in ROWS) + " |")
(ABL / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(ABL / "summary.json").write_text(json.dumps(
    {v: {f"{B:g}/{r:g}": m for (B, r), m in d.items()} for v, d in res.items()}, indent=1), encoding="utf-8")
print("\n".join(lines))
