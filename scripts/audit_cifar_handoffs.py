"""Audit reduced two-atom handoff states from CIFAR guided label averaging.

Run from the directory containing results/.
Optional arguments are directories of pair_*.json. Requires NumPy and SciPy.
Use --compare-replays results/cifar_composition_replay to compare signed
classes on all six archived sets. --sources-csv exports every source row.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import csv
import gzip
import json
import math

import numpy as np
from scipy.integrate import solve_ivp


def audit_row(data, row):
    """Evaluate labels holding first-stage output and single-atom decisions fixed."""
    ratio, r, B = row["ratio"], data["r"], data["B"]
    b2 = math.tanh(B) ** 2
    w = ratio / math.sinh(B) ** 2

    def field(s):
        # Equivalent to the signed sum of three tanh evaluations.
        y = np.tanh(s)
        return y * ((1 - b2) - w * b2 * (1 - y*y)) / (1 - b2 * y*y)

    def profile_rhs(tau, s):
        u = np.exp(-tau)
        t = -np.expm1(-tau)
        beta = t / u**2
        return r*r * beta * field(s) + s/t

    stored = row["classes"]
    assert len(stored) == len(row["handoff"]) == data["sources"]
    assert all(label == "unresolved" or label.startswith("atom:")
               for label, state in zip(stored, row["handoff"]) if state is None)
    labels = list(stored)
    counts = Counter(draws=len(stored), stored=stored.count("mid"),
                     unresolved=stored.count("unresolved"))
    ids = [i for i, state in enumerate(row["handoff"]) if state is not None]
    counts["handoffs"] = len(ids)
    states = [row["handoff"][i] for i in ids]
    q_signed = np.array([p["q"] for p in states])
    atom_labels = [f"atom:{data['pair'][0 if q > 0 else 1]}" for q in q_signed]
    if not ids or ratio <= 1:
        # The signed subcritical continuation escapes on its initial side,
        # except for q=0, the exact symmetric trajectory.
        for i, q, atom_label in zip(ids, q_signed, atom_labels):
            labels[i] = "mid" if q == 0 else atom_label
        counts["new"] = labels.count("mid")
        counts["lower"] = counts["new"]
        counts["upper"] = counts["new"] + counts["unresolved"]
        return counts, labels
    su = math.acosh(math.sqrt(ratio))
    tau = np.array([p["tau_handoff"] for p in states])
    q = np.abs(q_signed)
    beta = -np.expm1(-tau) * np.exp(2*tau)
    s = r * beta * q
    old = np.array([row["classes"][i] == "mid" for i in ids])

    # At s > 0 this strict condition means the interval [-s,s] is
    # inward pointing from now on: beta increases and 1/t decreases.
    direct_sink = (s < su) & ((s == 0) | (profile_rhs(tau, s) < 0))
    direct_atom = s >= su
    counts["direct_sink"] = direct_sink.sum()
    counts["direct_upper_pair_handoffs"] = (~direct_atom).sum()
    counts["stored_atom_direct_sink"] = (direct_sink & ~old).sum()
    counts["stored_mid_direct_atom"] = (direct_atom & old).sum()

    # At T, su/2 is in the basin by the same strict barrier; su escapes.
    # Backward trajectories from su/2 and su enclose the separatrix by
    # order preservation. Use both ends and two integration tolerances.
    # These are ordinary floating-point calculations, not interval arithmetic.
    T = 3.0
    assert max(tau) < T and profile_rhs(T, su/2) < 0
    lower, upper = [], []
    for rtol in [1e-9, 1e-11]:
        for start, dest in [(su/2, lower), (su, upper)]:
            sol = solve_ivp(profile_rhs, (T, min(tau)), [start], method="Radau",
                            rtol=rtol, atol=rtol*1e-3, dense_output=True)
            if not sol.success:
                raise RuntimeError(sol.message)
            dest.append(sol.sol(tau)[0])
    # Pad by more than the observed cross-tolerance discrepancy and numerical
    # crossing of the two theoretically ordered curves.
    all_limits = np.vstack(lower + upper)
    spread = all_limits.max(0) - all_limits.min(0)
    padding = 10*(1e-9 + spread)
    sink = s < all_limits.min(0) - padding
    atom = s > all_limits.max(0) + padding
    assert not np.any(sink & direct_atom) and not np.any(atom & direct_sink)
    counts["new"] = sink.sum()
    counts["inconclusive_bracket"] = (~(sink | atom)).sum()
    counts["stored_atom_new_mid"] = (sink & ~old).sum()
    counts["stored_mid_new_atom"] = (atom & old).sum()
    for k, i in enumerate(ids):
        if sink[k]:
            labels[i] = "mid"
        elif atom[k]:
            labels[i] = atom_labels[k]
        else:
            labels[i] = "inconclusive"
    counts["lower"] = direct_sink.sum()
    counts["upper"] = (~direct_atom).sum() + counts["unresolved"]
    assert counts["lower"] <= counts["new"] <= counts["upper"]
    return counts, labels


def compare_replays(directory, csv_file):
    root = Path("results")
    selected = root / "cifar_composition_exact_20261105"
    random = root / "cifar_composition_random_20261108"
    groups = {"selected": selected / "main", "random": random / "random",
              "handoff": selected / "handoff1e-9", "rtol": selected / "rtol1e-8",
              "handoff_large": random / "handoff1e-9_large", "rtol_large": random / "rtol1e-8_large"}
    writer = csv.writer(csv_file) if csv_file else None
    if writer:
        writer.writerow(["group", "pair", "ratio", "source_index", "stage", "archived",
                         "backward_bracket", "replay"])
    report = {}
    for name, original in groups.items():
        replay = json.loads((directory / f"{name}.json").read_text())
        totals, mismatches, seen = {}, [], set()
        for path in sorted(original.glob("pair_*.json")):
            data = json.loads(path.read_text())
            pair = "/".join(map(str, data["pair"]))
            assert pair not in seen
            seen.add(pair)
            assert set(replay[pair]) == {str(float(row["ratio"])) for row in data["rows"]}
            for row in data["rows"]:
                ratio = str(float(row["ratio"]))
                counts, expected = audit_row(data, row)
                corrected = replay[pair][ratio]
                actual = corrected["classes"]
                assert len(expected) == len(actual) == corrected["count"]
                assert actual.count("mid") == corrected["mid"]
                assert actual.count("unresolved") == corrected["unresolved"]
                for i, (old, independent, new) in enumerate(zip(row["classes"], expected, actual)):
                    counts["archive_label_changed"] += old != independent
                    if independent != new:
                        mismatches.append({"pair": pair, "ratio": ratio, "index": i,
                                           "archived": old, "independent": independent, "replay": new})
                    if writer:
                        stage = "pair" if row["handoff"][i] is not None else "first-stage"
                        writer.writerow([name, pair, ratio, i, stage, old, independent, new])
                totals.setdefault(ratio, Counter()).update(counts)
        assert seen and seen == set(replay)
        report[name] = {"by_ratio": {r: {k: int(v) for k,v in c.items()} for r,c in totals.items()},
                        "signed_mismatches": mismatches}
    return report


def check_fresh(directory):
    """Compare strict fresh runs with both labelers on their original handoffs."""
    with gzip.open(directory / "audit/cifar_signed_sources.csv.gz", "rt") as stream:
        original = {(r["pair"], r["ratio"], int(r["source_index"])): r
                    for r in csv.DictReader(stream) if r["group"] in ("selected", "random")}
    results = []
    for path in sorted(directory.glob("fresh*/*.json")):
        data = json.loads(path.read_text())
        pair = "/".join(map(str, data["pair"]))
        for row in data["rows"]:
            ratio = str(float(row["ratio"]))
            _, independent = audit_row(data, row)
            assert len(data["source_indices"]) == len(row["classes"]) == len(independent)
            for idx, observed, bracket in zip(data["source_indices"], row["classes"], independent):
                archived = original[pair, ratio, idx]
                assert observed == bracket == archived["backward_bracket"] == archived["replay"], (
                    str(path), pair, ratio, idx, observed, bracket, archived)
                results.append({"run": path.parent.name, "pair": pair, "ratio": float(ratio),
                                "source_index": idx, "tau0": data["tau0"], "class": observed})
    if not results:
        raise ValueError(f"No fresh runs in {directory}")
    return results


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="*", type=Path,
                        default=[Path("results/cifar_composition_exact_20261105/main"),
                                 Path("results/cifar_composition_random_20261108/random")])
    parser.add_argument("--compare-replays", type=Path)
    parser.add_argument("--check-fresh", type=Path,
                        help="check fresh CIFAR runs against the two archived-state classifications")
    parser.add_argument("--sources-csv", type=Path)
    args = parser.parse_args()
    if args.sources_csv and not args.compare_replays:
        parser.error("--sources-csv requires --compare-replays")
    if args.check_fresh:
        print(json.dumps(check_fresh(args.check_fresh), indent=2))
        return
    if args.compare_replays:
        if args.sources_csv:
            with args.sources_csv.open("w", newline="") as stream:
                report = compare_replays(args.compare_replays, stream)
        else:
            report = compare_replays(args.compare_replays, None)
        print(json.dumps(report, indent=2))
        if any(group["signed_mismatches"] for group in report.values()):
            raise SystemExit("Signed replay mismatch")
        return
    for directory in args.directories:
        totals = {}
        pair_files = sorted(directory.glob("pair_*.json"))
        if not pair_files:
            raise ValueError(f"No pair files in {directory}")
        for path in pair_files:
            data = json.loads(path.read_text())
            for row in data["rows"]:
                if row["ratio"] <= 1:
                    continue
                totals.setdefault(row["ratio"], Counter()).update(audit_row(data, row)[0])
        print(directory)
        for ratio, counts in sorted(totals.items()):
            print(f"{ratio:g} wc", json.dumps({k:int(v) for k,v in counts.items()}))


if __name__ == "__main__":
    main()
