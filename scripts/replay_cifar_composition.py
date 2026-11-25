"""Reclassify saved CIFAR pair handoffs. Run as python -m scripts.replay_cifar_composition."""
import json
from collections import Counter
from pathlib import Path

from scripts.cifar_pair_profile import classify_profile

SELECTED = Path("results/cifar_composition_exact_20261105")
RANDOM = Path("results/cifar_composition_random_20261108")
OUTPUT = Path("results/cifar_composition_replay")
GROUPS = {"selected": SELECTED / "main", "random": RANDOM / "random",
          "handoff": SELECTED / "handoff1e-9", "rtol": SELECTED / "rtol1e-8",
          "handoff_large": RANDOM / "handoff1e-9_large", "rtol_large": RANDOM / "rtol1e-8_large"}


def replay_group(directory):
    pairs = {}
    for file in sorted(directory.glob("pair_*.json")):
        raw = json.loads(file.read_text())
        first, second = raw["pair"]
        rows = {}
        for row in raw["rows"]:
            labels = list(row["classes"])
            reasons = Counter()
            assert len(labels) == len(row["handoff"]) == raw["sources"]
            for idx, state in enumerate(row["handoff"]):
                if state is None:
                    continue
                label, why = classify_profile(state["q"], state["tau_handoff"], raw["r"], row["w"], raw["B"])
                if label in ("+", "-"):
                    label = f"atom:{first if label == '+' else second}"
                labels[idx] = label
                reasons[why] += 1
            rows[str(float(row["ratio"]))] = {
                "classes": labels, "count": len(labels), "mid": labels.count("mid"),
                "unresolved": labels.count("unresolved"), "stops_after_handoff": dict(reasons)}
        pairs[f"{first}/{second}"] = rows
    if not pairs:
        raise ValueError(f"No archived pairs in {directory}")
    return pairs


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name, path in GROUPS.items():
        pairs = replay_group(path)
        (OUTPUT / f"{name}.json").write_text(json.dumps(pairs, separators=(",", ":")) + "\n")
        summary[name] = {pair: {ratio: row["mid"] / row["count"] for ratio, row in rows.items()}
                         for pair, rows in pairs.items()}
        print(name, len(pairs), flush=True)
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
