"""Summarise results/cifar_composition_exact_20261105 into SUMMARY.md and summary.json.

    python scripts/summarize_cifar_composition.py results/cifar_composition_exact_20261105
"""
import glob
import json
import os
import sys

root = sys.argv[1]
pairs = []
for f in sorted(glob.glob(os.path.join(root, "main", "*.json"))):
    d = json.load(open(f))
    rows = {r["ratio"]: r for r in d["rows"]}
    pairs.append({
        "pair": d["pair"], "r": d["r"], "margin_sq": d["margin_sq"], "w_c": d["w_c"],
        "unresolved": max(r["unresolved"] for r in d["rows"]),
        "mid": {str(k): v["midpoint"] for k, v in rows.items()},
        "basin": {str(k): v["midpoint"] + v["pair_atoms"] for k, v in rows.items()},
        "classes": {str(k): v["classes"] for k, v in rows.items()},
    })
ratios = sorted({float(k) for p in pairs for k in p["mid"]})
# Sensitivity: label agreement with the main run on the same pair.
sens_pairs = {}                  # setting -> "i/j" -> ratio -> comparison with the main run
for name in ("handoff1e-9", "rtol1e-8"):
    for f in glob.glob(os.path.join(root, name, "*.json")):
        d = json.load(open(f))
        ref = next(p for p in pairs if p["pair"] == d["pair"])
        out = {}
        for r in d["rows"]:
            a, b = r["classes"], ref["classes"][str(r["ratio"])]
            out[str(r["ratio"])] = {"midpoint": r["midpoint"], "main_midpoint": ref["mid"][str(r["ratio"])],
                                    "agree": sum(x == y for x, y in zip(a, b)) / len(a)}
        sens_pairs.setdefault(name, {})[f"{d['pair'][0]}/{d['pair'][1]}"] = out
sens = {name: o["292/1938"] for name, o in sens_pairs.items()}     # the first pair, as before

mean = lambda xs: sum(xs) / len(xs)
lines = ["# Exact guided label averaging on CIFAR-10 pairs (B = 1, 512 sources)", "",
         "Midpoint fraction by w/w_c; `margin` = min over other atoms of |x^k - z|^2 / r^2.", "",
         "| pair | margin | " + " | ".join(f"{r:g}" for r in ratios) + " |",
         "|---|---|" + "---|" * len(ratios)]
for p in pairs:
    lines.append(f"| {p['pair'][0]}/{p['pair'][1]} | {p['margin_sq']:.2f} | "
                 + " | ".join(f"{p['mid'][str(r)]:.3f}" for r in ratios) + " |")
lines.append("| mean | | " + " | ".join(f"{mean([p['mid'][str(r)] for p in pairs]):.3f}" for r in ratios) + " |")
lines += ["", "Fraction ending at the pair or its midpoint:", "",
          "| pair | " + " | ".join(f"{r:g}" for r in ratios) + " |", "|---|" + "---|" * len(ratios)]
for p in pairs:
    lines.append(f"| {p['pair'][0]}/{p['pair'][1]} | "
                 + " | ".join(f"{p['basin'][str(r)]:.3f}" for r in ratios) + " |")
lines += ["", f"Unresolved (max over all rows): {max(p['unresolved'] for p in pairs)}", "",
          "Sensitivity on pair 292/1938 (fraction of sources with the same endpoint as the main run):", ""]
for name, o in sens.items():
    for k, v in sorted(o.items(), key=lambda kv: float(kv[0])):
        lines.append(f"- {name}, w/w_c={float(k):g}: midpoint {v['midpoint']:.3f} (main {v['main_midpoint']:.3f}), agree {v['agree']:.3f}")
lines += ["", "Sensitivity on every pair: midpoint fraction under main / hand-off 1e-9 / rtol 1e-8:", "",
          "| pair | 0.9 | 1.1 | 2 |", "|---|---|---|---|"]
for p in pairs:
    key = f"{p['pair'][0]}/{p['pair'][1]}"
    cells = []
    for r in ("0.9", "1.1", "2.0"):
        vals = [p["mid"][r]] + [sens_pairs.get(n, {}).get(key, {}).get(r, {}).get("midpoint", float("nan"))
                                for n in ("handoff1e-9", "rtol1e-8")]
        cells.append(" / ".join(f"{v:.3f}" for v in vals))
    lines.append(f"| {key} | " + " | ".join(cells) + " |")
open(os.path.join(root, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
for p in pairs:
    del p["classes"]
json.dump({"pairs": pairs, "sensitivity": sens, "sensitivity_pairs": sens_pairs},open(os.path.join(root, "summary.json"), "w"), indent=1)
print("\n".join(lines))
