"""Where does the ICLR main text end, on a machine that has Tectonic but no pdflatex?

Tectonic is XeTeX and cannot use psnfss ``times``; it silently falls back to Latin Modern,
which is wider than Times and reports a body that is a page too long. This builds a copy
of ``paper/main.tex`` with TeX Gyre Termes (metrically Times) as the text font, in a
scratch directory, and prints the page on which ``\\label{endmain}`` falls. Maths stays in
Computer Modern, so the result is a proxy, good for *comparing two versions* of the
source and not for certifying the limit: the real check is ``scripts/check_paper.py``
after ``latexmk -pdf``.

    python scripts/body_length_proxy.py                 # paper/main.tex
    python scripts/body_length_proxy.py --pad 100       # how far from page 10 are we?

``--pad K`` inserts K points of vertical space before the end of the body; the largest K
that still ends on page 9 is the slack, in points (about 13 per line of text).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1] / "paper"
FONTS = (r"\usepackage{fontspec}" "\n"
         r"\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,"
         r"ItalicFont=*-italic,BoldItalicFont=*-bolditalic]" "\n"
         r"\setsansfont{texgyreheros}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,"
         r"ItalicFont=*-italic,BoldItalicFont=*-bolditalic]" "\n"
         r"\setmonofont{texgyrecursor}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,"
         r"ItalicFont=*-italic,BoldItalicFont=*-bolditalic]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="?", type=Path, default=PAPER / "main.tex")
    ap.add_argument("--pad", type=float, default=0.0)
    args = ap.parse_args()

    tectonic = shutil.which("tectonic")
    if not tectonic:
        sys.exit("tectonic not found on PATH")
    src = args.tex.read_bytes().decode("utf-8").replace("\r\n", "\n")
    old = r"\usepackage{iclr2027_conference,times}"
    if old not in src:
        sys.exit("main.tex no longer loads the style as expected")
    src = src.replace(old, "\\usepackage{iclr2027_conference}\n" + FONTS)
    if args.pad:
        src = src.replace(r"\label{endmain}", r"\rule{0pt}{%gpt}\par\label{endmain}" % args.pad)

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for p in PAPER.iterdir():
            if p.is_file() and not p.name.startswith("main."):
                shutil.copy(p, d / p.name)
        if (PAPER / "figures").exists():
            shutil.copytree(PAPER / "figures", d / "figures")
        (d / "main.tex").write_text(src, encoding="utf-8")
        r = subprocess.run([tectonic, "-X", "compile", "main.tex", "--keep-intermediates"], cwd=d,
                           capture_output=True, text=True)
        errors = [l for l in r.stderr.splitlines() if l.startswith("error")]
        if errors:
            print("\n".join(errors[:5]))
            return 1
        aux = (d / "main.aux").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\\newlabel\{endmain\}\{\{[^}]*\}\{(\d+)\}", aux)
    print(f"main text ends on page {m.group(1) if m else '?'} (Times-metric proxy, pad={args.pad:g}pt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
