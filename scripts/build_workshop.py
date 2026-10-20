"""Write paper/workshop.tex from paper/workshop_src.tex.

The workshop version used to fill %%BLOCK:name%% lines with blocks cut from the
conference version (paper/main.tex): the proofs of the bandwidth and calibration
results, the spectral-bias appendix and the reference-family control. The conference
version no longer contains that material, so the blocks are frozen in
workshop_src.tex (as of 19 October 2026) and this script only marks the output as
generated. Run it after every change to workshop_src.tex.

Usage:  uv run python scripts/build_workshop.py
"""
from __future__ import annotations

from pathlib import Path

PAPER = Path("paper")
SOURCE_NOTE = "% This file is the source; scripts/build_workshop.py copies it to workshop.tex.\n"
GENERATED_NOTE = "% GENERATED from workshop_src.tex by scripts/build_workshop.py: do not edit.\n"


def main() -> None:
    src = (PAPER / "workshop_src.tex").read_text(encoding="utf-8")
    assert "%%BLOCK:" not in src, "workshop_src.tex must be self-contained"
    assert src.count(SOURCE_NOTE) == 1
    (PAPER / "workshop.tex").write_text(src.replace(SOURCE_NOTE, GENERATED_NOTE),
                                        encoding="utf-8", newline="")
    print("wrote paper/workshop.tex")


if __name__ == "__main__":
    main()
