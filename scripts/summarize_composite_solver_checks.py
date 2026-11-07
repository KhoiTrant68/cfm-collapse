"""Solver checks of the learned composite L3 in every learned-composition run.

For each results directory, variant and B this reports, over seeds and guidance strengths,
(a) the largest fraction of sources whose class (delta = 0.1) differs between the ROS2 tolerances
1e-5 and 1e-7 at the last gap, the largest change of the midpoint occupancy (delta = 0.05) between
those tolerances, and (b) the largest change of the midpoint occupancy (delta = 0.05)
between the gaps eps = 1e-3 and 1e-5.

    python -m scripts.summarize_composite_solver_checks --out results/composite_solver_checks_20261108.json
"""
import argparse, collections, json, pathlib

DIRS = ["results/learned_composition_20261021", "results/learned_composition_2d_20261021",
        "results/composition_ablation_20261105", "results/composition_ablation_2d_20261105",
        "results/bottleneck_2d_20261107"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    agg = collections.defaultdict(lambda: {"tol": [], "tol_occ": [], "eps": [], "seeds": set()})
    for d in DIRS:
        for f in sorted(pathlib.Path(d).glob("*_seed*/summary.json")):
            s = json.loads(f.read_text(encoding="utf-8"))
            for arm in s.get("arms", []):
                if arm.get("arm") != "L3":
                    continue
                B = float(arm.get("B", s.get("B", 0.0)))
                key = (d, s["variant"], B)
                by = {round(e["eps"], 12): e for e in arm["by_eps"]}
                last = arm["by_eps"][-1]
                if last.get("solver_class_disagree") is not None:
                    agg[key]["tol"].append(last["solver_class_disagree"])
                if "occ_0.05_tight" in last:
                    agg[key]["tol_occ"].append(abs(last["occ_0.05"] - last["occ_0.05_tight"]))
                if 1e-3 in by and 1e-5 in by:
                    agg[key]["eps"].append(abs(by[1e-3]["occ_0.05"] - by[1e-5]["occ_0.05"]))
                agg[key]["seeds"].add(s["seed"])
    rows = [{"dir": d, "variant": v, "B": B, "seeds": len(o["seeds"]),
             "tol_max": max(o["tol"]) if o["tol"] else None,
             "tol_occ_max": max(o["tol_occ"]) if o["tol_occ"] else None,
             "eps_max": max(o["eps"]) if o["eps"] else None}
            for (d, v, B), o in sorted(agg.items())]
    pathlib.Path(a.out).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['dir'].split('/')[-1]:38s} {r['variant']:10s} B={r['B']:<6g} seeds={r['seeds']} "
              f"tol={r['tol_max']} tol_occ={r['tol_occ_max']} eps={r['eps_max']}")


if __name__ == "__main__":
    main()
