"""Bound the midpoint count from the archived CIFAR two-atom handoff states.

Run with Python 3 from any directory. Optional positional argument: path to a
directory of pair_*.json files. This checks the scalar continuation actually
specified by the experiment. It assumes the stored handoffs and leaves direct
single-atom decisions untouched. It never integrates the 2,000-image field.
"""

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def count_pair(pair, counts):
    radius = pair["r"]
    bias = pair["B"]
    for row in pair["rows"]:
        w = row["w"]
        if row["ratio"] <= 1:
            continue
        outer = math.acosh(math.sqrt(w) * math.sinh(bias))
        tanh_bias_sq = math.tanh(bias)**2
        tally = counts[row["ratio"]]
        assert len(row["classes"]) == len(row["handoff"]) == pair["sources"]
        for label, handoff in zip(row["classes"], row["handoff"]):
            tally["n"] += 1
            tally["archived"] += label == "mid"
            if handoff is None:
                assert label.startswith("atom:") or label == "unresolved"
                tally["unresolved"] += label == "unresolved"
                continue
            u = math.expm1(handoff["tau_handoff"])
            s = abs(radius * u * (1 + u) * handoff["q"])
            # Evaluate F via tanh addition to avoid subtracting nearly equal
            # terms around zero. By oddness it suffices to check |s|.
            y = math.tanh(s)
            field = y * ((1 - tanh_bias_sq) - w * tanh_bias_sq * (1 - y*y))
            field /= 1 - tanh_bias_sq * y*y
            # ds/du = s/u + r^2 u F(s). At the current wall |s|, strict
            # inward velocity persists as u increases. Bounded s implies q -> 0.
            if s < outer and (s == 0 or radius**2 * u**2 * (-field) > s):
                tally["inside"] += 1
                tally["archived_atom_inside"] += label.startswith("atom:")
            elif s < outer:
                tally["undecided"] += 1
            # Outside the positive outer root F(s) >= 0, so |s| grows at
            # least proportionally to u and the trajectory escapes the tie.


def main():
    root = Path(__file__).resolve().parents[3]
    default_dir = root / "results/cifar_composition_exact_20261105/main"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=default_dir)
    args = parser.parse_args()
    files = sorted(args.directory.glob("pair_*.json"))
    if not files:
        parser.error(f"no pair_*.json in {args.directory}")
    counts = defaultdict(Counter)
    for path in files:
        count_pair(json.loads(path.read_text()), counts)
    print("w/wc    n  archived  lower  upper  archived_atom_inside  unresolved")
    for ratio, tally in sorted(counts.items()):
        lower = tally["inside"]
        upper = lower + tally["undecided"] + tally["unresolved"]
        print(f"{ratio:4g} {tally['n']:4d} {tally['archived']:9d} {lower:6d} "
              f"{upper:6d} {tally['archived_atom_inside']:21d} {tally['unresolved']:11d}")


if __name__ == "__main__":
    main()
