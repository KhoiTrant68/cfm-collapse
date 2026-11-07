"""Summarise the random-pair and large-w sensitivity runs of the exact CIFAR-10 composition.

Reads results/cifar_composition_random_20261108/{random,handoff1e-9_large,rtol1e-8_large}/ and the
main run results/cifar_composition_exact_20261105/main/, and writes SUMMARY.md and summary.json.
For the sensitivity runs it reports the midpoint fraction under each setting, the fraction of
sources with the same endpoint as the main run, and the fraction with the same coarse class
(midpoint / an atom of the pair / another atom).

    python -m scripts.summarize_cifar_random
"""
import json, pathlib

D = pathlib.Path("results/cifar_composition_random_20261108")
MAIN = pathlib.Path("results/cifar_composition_exact_20261105/main")


def load(d):
    return {tuple(j["pair"]): j for j in (json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("pair_*.json")))}


def coarse(c, i, j):
    return "mid" if c == "mid" else ("pair" if c in (f"atom:{i}", f"atom:{j}") else "other")


def main():
    pairs = json.loads((D / "pairs.json").read_text(encoding="utf-8"))
    rnd, main_ = load(D / "random"), load(MAIN)
    out = {"n_mutual_pairs": pairs["n_pairs"], "min_margin_sq_all": pairs["min_margin_sq"], "seed": pairs["seed"],
           "random": [], "sensitivity": {}}
    for (i, j), p in sorted(rnd.items(), key=lambda kv: -kv[1]["margin_sq"]):
        rows = {str(r["ratio"]): r for r in p["rows"]}
        out["random"].append({"pair": [i, j], "margin_sq": p["margin_sq"],
                              "mid": {k: r["midpoint"] for k, r in rows.items()},
                              "basin": {k: r["midpoint"] + r["pair_atoms"] for k, r in rows.items()},
                              "unresolved": max(r["unresolved"] for r in p["rows"])})
    for name in ("handoff1e-9_large", "rtol1e-8_large"):
        s = load(D / name)
        o = out["sensitivity"][name] = {}
        for (i, j), p in s.items():
            m = {r["ratio"]: r for r in main_[(i, j)]["rows"]}
            for r in p["rows"]:
                a, b = r["classes"], m[r["ratio"]]["classes"]
                o.setdefault(str(r["ratio"]), {})[f"{i}/{j}"] = {
                    "midpoint": r["midpoint"], "main_midpoint": m[r["ratio"]]["midpoint"],
                    "unresolved": r["unresolved"],
                    "agree": sum(x == y for x, y in zip(a, b)) / len(a),
                    "agree_coarse": sum(coarse(x, i, j) == coarse(y, i, j) for x, y in zip(a, b)) / len(a)}
    (D / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    R = ["0.9", "1.1", "2.0", "5.0"]
    L = [f"# Exact guided label averaging on {len(out['random'])} random CIFAR-10 pairs (B = 1, 512 sources)", "",
         f"{out['n_mutual_pairs']} mutual-nearest-neighbour pairs; smallest margin over all of them "
         f"{out['min_margin_sq_all']:.3f} (> 1 is what Theorem spectral(c) needs). Seed {out['seed']}.", "",
         "| pair | margin | " + " | ".join(R) + " |", "|---|---|" + "---|" * len(R)]
    for p in out["random"]:
        L.append(f"| {p['pair'][0]}/{p['pair'][1]} | {p['margin_sq']:.2f} | "
                 + " | ".join(f"{p['mid'][r]:.3f}" for r in R) + " |")
    L.append("| mean | | " + " | ".join(f"{sum(p['mid'][r] for p in out['random']) / len(out['random']):.3f}" for r in R) + " |")
    L += ["", f"Unresolved (max): {max(p['unresolved'] for p in out['random'])}", "",
          "## Sensitivity of the eight main pairs at w/w_c = 5 and 10", "",
          "| setting | w/w_c | pair | midpoint (main) | agree | agree coarse |", "|---|---|---|---|---|---|"]
    for name, o in out["sensitivity"].items():
        for k in sorted(o, key=float):
            for pr, v in sorted(o[k].items()):
                L.append(f"| {name} | {float(k):g} | {pr} | {v['midpoint']:.3f} ({v['main_midpoint']:.3f}) | "
                         f"{v['agree']:.3f} | {v['agree_coarse']:.3f} |")
    (D / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
