"""Build the anonymised code-and-results supplementary for the TMLR submission.

Collects the tracked files a reader needs to reproduce the paper's numbers -- the code,
the configs, the result files that scripts/verify_paper_numbers.py reads, and the
numerical proof checks (docs/audit/, shipped as proof_checks/ as the paper names it) --
writes a README for the archive, scrubs repository URLs, and refuses to write the zip if
any identifying string is left in any text file.

Left out: internal notes (docs/plan, docs/review), Kaggle notes, the LaTeX sources, git
history, and this script.

Writes: dist/supplementary.zip
Usage:  python scripts/make_supplementary.py
"""
from __future__ import annotations

import base64
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

INCLUDE = ("src/", "scripts/", "configs/", "results/", "docs/audit/",
           "pyproject.toml", "uv.lock", ".python-version", "LICENSE")
EXCLUDE = ("scripts/make_supplementary.py", "docs/audit/group4/refcheck.py")
RENAME = {"docs/audit/": "proof_checks/"}
# Identifying strings, stored encoded so that this file does not itself carry them.
_BANNED = [base64.b64decode(s).decode() for s in (
    "a2hvaQ==", "dHJhbnQ2OA==", "Z3Vlc3MwMw==", "c3NoIGd1ZXNz", "L21udC9ob21l",
    "YXdlc29tZWN2", "YzpcdXNlcnM=", "YzovdXNlcnM=")]
_URL = re.compile(r"https?://(?:raw\.)?github(?:usercontent)?\.com/[A-Za-z0-9_.-]+/cfm-collapse[^\s\"']*")
TEXT = {".py", ".sh", ".md", ".yaml", ".yml", ".toml", ".json", ".txt", ".csv", ".cfg", ""}

README = """# Supplementary material: code and results

Anonymised for review. Everything here is what the paper's numbers are computed from.

## Layout
- `src/` -- problems, models, training (`train.py` for the low-dimensional runs,
  `train_exp3.py` for the DDPM image runs), metrics (`metrics/kernel_theory.py`: the
  Nadaraya--Watson reference; `metrics/calibration.py`: rank-based calibration).
- `configs/` -- one YAML per experiment.
- `scripts/` -- training sweeps, analyses, and the checks named in the paper.
- `results/` -- the result files every reported number is read from (no network weights).
- `proof_checks/` -- numerical checks of the proofs (closed forms against simulation,
  symbolic expansions), grouped as in the appendix; `proof_audit.md` lists them.

## Environment
Python 3.12 with `uv`: `uv sync`, then prefix commands with `uv run`. Torch is pinned to
the CPU build in `pyproject.toml`; the image runs need a CUDA build.

## Checking the numbers
`uv run python scripts/verify_paper_numbers.py` checks the numbers in the paper against
the files in `results/` and exits non-zero if any differs.

## Reproducing
- Low-dimensional experiments: `scripts/run_exp1.sh`, `scripts/run_sweeps.py` (optional
  `--gpus N`), then the matching analysis script (e.g. `scripts/test_heff_synthetic.py`,
  `scripts/audit_calibration_v2.py`, `scripts/analyze_audit_v2.py`).
- Image experiments: `scripts/server_cifar_queue.sh <gpu> <h:seed> ...` trains a DDPM run
  and runs the h_eff fit, the held-out calibration and the re-evaluation;
  `scripts/calib_image_levels.py` adds the multi-level calibration;
  `scripts/analyze_cifar_reruns.py`, `scripts/summarize_calib_levels.py` and
  `scripts/joint_from_marginal.py` summarise them.
- Theory checks: `scripts/test_kernel_theory.py`, `scripts/verify_kernel_theory.py`,
  `scripts/verify_prop17.py`, `scripts/verify_target_noise.py`, `scripts/theory_t1_check.py`,
  `scripts/theory_b_check.py`, and `proof_checks/`.
"""


def main() -> None:
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                           check=True).stdout.split("\n")
    files = [f for f in files if f and f.startswith(INCLUDE) and f not in EXCLUDE]
    out = Path("dist/supplementary.zip")
    out.parent.mkdir(exist_ok=True)
    problems, n_url, size = [], 0, 0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            data = Path(f).read_bytes()
            arc = f
            for a, b in RENAME.items():
                if arc.startswith(a):
                    arc = b + arc[len(a):]
            if Path(f).suffix.lower() in TEXT:
                txt = data.decode("utf-8", errors="replace")
                txt, n = _URL.subn("<repository URL>", txt)
                n_url += n
                low = txt.lower()
                for s in _BANNED:
                    if s in low:
                        problems.append(f"{f}: contains an identifying string")
                data = txt.encode("utf-8")
            z.writestr("supplementary/" + arc, data)
            size += len(data)
        z.writestr("supplementary/README.md", README)
    if problems:
        print("NOT WRITTEN; identifying strings found:")
        print("\n".join(sorted(set(problems))))
        sys.exit(1)
    out.write_bytes(buf.getvalue())
    print(f"{len(files)} files ({size / 1e6:.1f} MB uncompressed), {n_url} repository URLs "
          f"scrubbed -> {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
