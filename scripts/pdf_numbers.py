#!/usr/bin/env python3
"""Snapshot and compare the decimal numbers printed in a PDF (gate: no number changes silently).

  python scripts/pdf_numbers.py snapshot submit/pdf/A_tmlr.pdf docs/plan/baseline_numbers_A.txt
  python scripts/pdf_numbers.py compare  submit/pdf/A_tmlr.pdf docs/plan/baseline_numbers_A.txt

Only numbers with a decimal point or at least three digits are compared (page and section numbers
are noise). compare prints the multiset difference; exit 1 if it is nonempty.
"""
import re
import subprocess
import sys
from collections import Counter

NUM = re.compile(r"(?<![\w.])\d+\.\d+|(?<![\w.])\d{3,}(?![\w.])")


def numbers(pdf):
    text = subprocess.run(["pdftotext", "-q", "-enc", "UTF-8", pdf, "-"], capture_output=True,
                          check=True).stdout.decode("utf-8", errors="replace")
    return Counter(NUM.findall(text))


def main(argv):
    mode, pdf, snap = argv
    cur = numbers(pdf)
    if mode == "snapshot":
        with open(snap, "w", encoding="utf-8") as f:
            for k in sorted(cur):
                f.write(f"{k}\t{cur[k]}\n")
        print(f"{sum(cur.values())} numbers ({len(cur)} distinct) -> {snap}")
        return 0
    base = Counter()
    for line in open(snap, encoding="utf-8"):
        k, n = line.rstrip("\n").split("\t")
        base[k] = int(n)
    gone, new = base - cur, cur - base
    for k in sorted(gone):
        print(f"- {k} x{gone[k]}")
    for k in sorted(new):
        print(f"+ {k} x{new[k]}")
    print(f"removed {sum(gone.values())}, added {sum(new.values())}")
    return 1 if (gone or new) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
