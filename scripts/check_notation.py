#!/usr/bin/env python3
"""Notation lint for paper_theory (A) and paper_mechanism (B).

Flags symbols and terms that docs/notation/shared_notation.md retires. Comments are ignored.
Usage:  python scripts/check_notation.py [A|B ...]     exit 1 if any retired form remains.
Counts of (1-t) are reported as a warning only (rule 5: write \\eps).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = {"A": ROOT / "paper_theory" / "main.tex", "B": ROOT / "paper_mechanism" / "main.tex"}

COMMON = [
    (r"[Ll]abel smoothing", "label smoothing -> label noise"),
    (r"w_\{?[ijk]\}?\^\{?\(h\)", "w_i^{(h)} -> q_i^{(h)} (posterior weight)"),
    (r"\\widetilde\{?w\}?_|\\tilde\{?w\}?_", "tilde w_i -> tilde q_i"),
]
RETIRED = {
    "A": COMMON + [
        (r"w_\{?c\}?\^\{?\\(?:rm|mathrm)\{?spec", "w_c^{spec} -> w_c"),
        (r"i\^\{?\\star", "i^\\star -> i_\\star"),
        (r"s\^\{?\\star", "s^\\star -> \\zeta_\\star"),
        (r"\\mu_\{?[cuw]\b", "\\mu_{c,u,w} -> m_{c,u,w}"),
        (r"\\omega\s*=\s*1\s*\+\s*w", "\\omega=1+w -> w_+"),
        (r"\\omega_\{?k", "\\omega_k -> \\bar q_k"),
        (r"\bhard labels?\b", "hard label -> hard conditioning"),
        (r"\bnon-atom\b", "non-atom -> blend / off-support"),
        (r"\bexact optimum\b", "exact optimum -> exact field"),
        (r"\bpopulation minimi", "population minimiser -> exact field"),
    ],
    "B": COMMON + [
        (r"\\omega_\{?t", "\\omega_t -> \\zeta_t"),
        (r"\\omega\(", "\\omega(y,\\sigma) -> \\zeta(y,\\sigma)"),
        (r"\\Omega(?![a-zA-Z])", "\\Omega -> \\bar\\zeta"),
        (r"\\delta_\{?t", "\\delta_t -> \\lambda_t"),
        (r"\\theta_\{?k", "Heun \\theta_k -> \\bar\\kappa_k"),
        (r"\\rho_\{?R", "\\rho_R -> c_R"),
        (r"(?<![a-zA-Z\\])w_\{?[ij]\}?(?![a-zA-Z^])", "w_j, w_i -> q_j, q_i"),
    ],
}
ONE_MINUS_T = re.compile(r"\(1\s*-\s*t\)")


def strip_comments(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def check(name):
    lines = strip_comments(FILES[name].read_text(encoding="utf-8")).splitlines()
    hits = 0
    for pat, msg in RETIRED[name]:
        rx = re.compile(pat)
        where = [i for i, l in enumerate(lines, 1) if rx.search(l)]
        if where:
            hits += len(where)
            shown = ", ".join(map(str, where[:8])) + (" ..." if len(where) > 8 else "")
            print(f"[{name}] {msg}: {len(where)} line(s): {shown}")
    n = sum(len(ONE_MINUS_T.findall(l)) for l in lines)
    if n:
        print(f"[{name}] warning: {n} occurrence(s) of (1-t); prefer \\eps")
    return hits


def main(argv):
    names = argv or ["A", "B"]
    total = sum(check(n) for n in names)
    print("notation lint:", "clean" if total == 0 else f"{total} line(s) with retired notation")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
