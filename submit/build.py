#!/usr/bin/env python3
"""Build the submission packages from paper_theory/ and paper_mechanism/.

Targets (each written to submit/<name>/, PDF copied to submit/pdf/<name>.pdf):
  A_tmlr     paper A, anonymous, for TMLR (upload the PDF on OpenReview)
  A_arxiv    paper A, [preprint] with authors from authors_A_arxiv.tex (upload the zip)
  B_neurips  paper B, anonymous (still the TMLR style until neurips_2027.sty is out)
  supp_A, supp_B  anonymised code supplements (zip): the scripts each paper names, the
             results/ folders they read (no checkpoints or logs) and a README to run them

Every package gets: comments stripped (arXiv publishes the source), unused files pruned,
a clean latexmk build, and a leak scan of the sources and of the PDF text. The comments
that carried TODO/FLAG/decision notes are not lost: they go to submit/stripped_notes.txt.

Usage:  python submit/build.py            (all targets)
        python submit/build.py A_tmlr B_neurips
Exit code 0 only if every requested target built and passed its checks.
"""
import ast
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "submit"
PDF_DIR = OUT / "pdf"

PAPER_FILES = ["main.tex", "math_commands.tex", "refs.bib", "tmlr.sty", "tmlr.bst",
               "fancyhdr.sty", "natbib.sty"]

# Strings that must never reach a reviewer or the public source.
LEAK_ALWAYS = [r"/Users/", r"/mnt/", r"khoitm8", r"tmkhang", r"KhoiTrant",
               r"\bTODO\b", r"\bFLAG\b", r"DECISION", r"[Gg]roup decision",
               r"the assistant", r"PLACEHOLDER", r"forum\?id=XXXX"]
# Names, only for the anonymous builds. Word-bounded so "Transfer" etc. do not match.
LEAK_ANON = [r"gmail", r"\bKhang\b", r"\bKh[o\u00f4]i\b", r"\bTr[a\u1ea7]n\b", r"lab09"]
# Paper A must not point at paper B (TMLR forbids reuse with a parallel submission, and
# the A supplement must not carry B's files).
LEAK_A = [r"(?i)paper_?B", r"(?i)paper[ ~]B\b", r"(?i)paper[ ~]A\b", r"companion"]


class BuildError(Exception):
    pass


# --- comment stripping ----------------------------------------------------------------
def _comment_start(line):
    """Index of the first unescaped %, or -1."""
    i = 0
    while True:
        i = line.find("%", i)
        if i < 0:
            return -1
        bs = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            bs += 1
            j -= 1
        if bs % 2 == 0:
            return i
        i += 1


def strip_comments(text, label):
    """Drop full-line comments; cut trailing ones to a bare % so no space is added."""
    if re.search(r"\\begin\{(verbatim|lstlisting|comment)\}", text):
        raise BuildError(f"{label}: has a verbatim-like environment; strip it by hand")
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        k = _comment_start(line)
        if k < 0:
            out.append(line)
            continue
        head = line[:k]
        if head.strip() == "":
            continue
        out.append(head + "%")
    return "\n".join(out) + "\n"


# --- per-target source edits ----------------------------------------------------------
def replace_once(text, old, new, label):
    c = text.count(old)
    if c != 1:
        raise BuildError(f"{label}: expected exactly one {old!r}, found {c}")
    return text.replace(old, new)


def edit_A_arxiv(text):
    text = replace_once(text, "\\else\n  \\usepackage{tmlr}\n",
                        "\\else\n  \\usepackage[preprint]{tmlr}\n", "A_arxiv")
    authors = (OUT / "authors_A_arxiv.tex").read_text(encoding="utf-8")
    authors = "\n".join(l for l in authors.splitlines() if not l.lstrip().startswith("%"))
    text = replace_once(text, "\\author{Anonymous authors}", authors.strip(), "A_arxiv")
    text = replace_once(text, " (anonymised for review):", ":", "A_arxiv")
    return text


TARGETS = {
    "A_tmlr": {"src": "paper_theory", "edit": None, "anon": True, "zip": False},
    "A_arxiv": {"src": "paper_theory", "edit": edit_A_arxiv, "anon": False, "zip": True},
    "B_neurips": {"src": "paper_mechanism", "edit": None, "anon": True, "zip": False},
}


def run(cmd, cwd, log):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, errors="replace")
    log.write_text(p.stdout, encoding="utf-8")
    return p.returncode


def build_paper(name, notes):
    cfg = TARGETS[name]
    src = ROOT / cfg["src"]
    dst = OUT / name
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in PAPER_FILES:
        if not (src / f).exists():
            raise BuildError(f"{name}: missing {src / f}")
        shutil.copy2(src / f, dst / f)
    shutil.copytree(src / "figures", dst / "figures")

    main = (dst / "main.tex").read_text(encoding="utf-8")
    # tmlr.sty prints \openreview only with [accepted]; the placeholder id is dead weight.
    main = re.sub(r"\\newcommand\{\\openreview\}\{[^\n]*\}\n", "", main)
    if cfg["edit"]:
        main = cfg["edit"](main)
    (dst / "main.tex").write_text(main, encoding="utf-8")
    for tex in [dst / "main.tex", dst / "math_commands.tex"] + sorted(dst.glob("figures/**/*.tex")):
        rel = f"{name}/{tex.relative_to(dst).as_posix()}"
        tex.write_text(strip_comments(tex.read_text(encoding="utf-8"), rel),
                       encoding="utf-8")

    if shutil.which("latexmk") is None:
        raise BuildError("latexmk not found on PATH")
    rc = run(["latexmk", "-pdf", "-recorder", "-interaction=nonstopmode", "-halt-on-error",
              "main.tex"], dst, OUT / f"{name}.buildlog")
    log = (dst / "main.log").read_text(encoding="utf-8", errors="replace") \
        if (dst / "main.log").exists() else ""
    if rc != 0 or not (dst / "main.pdf").exists():
        raise BuildError(f"{name}: latexmk failed (rc={rc}), see submit/{name}.buildlog")
    bad = sorted(set(re.findall(r"(?:Citation|Reference) `[^']+' [^\n]*undefined", log)))
    bad += ["multiply defined labels"] if "multiply defined" in log else []
    bad += ["rerun needed"] if "Rerun to get" in log else []
    if bad:
        raise BuildError(f"{name}: " + "; ".join(bad[:10]))
    pages = re.search(r"Output written on main\.pdf \((\d+) pages", log)

    # Keep only what LaTeX actually read, plus the .bbl (arXiv does not need the .bib).
    used = set()
    for line in (dst / "main.fls").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("INPUT "):
            p = Path(line[6:].strip())
            p = p if p.is_absolute() else (dst / p)
            try:
                used.add(p.resolve().relative_to(dst.resolve()).as_posix())
            except ValueError:
                pass  # TeX distribution file
    PDF_DIR.mkdir(exist_ok=True)
    shutil.copy2(dst / "main.pdf", PDF_DIR / f"{name}.pdf")
    keep = {u for u in used if not u.endswith((".aux", ".out", ".toc"))} | {"main.tex", "main.bbl"}
    for f in sorted(dst.rglob("*"), reverse=True):
        rel = f.relative_to(dst).as_posix()
        if f.is_file() and rel not in keep:
            f.unlink()
        elif f.is_dir() and not any(f.iterdir()):
            f.rmdir()

    leaks = scan_dir(dst, cfg["anon"], name.startswith("A_"))
    leaks += scan_pdf(PDF_DIR / f"{name}.pdf", cfg["anon"], name.startswith("A_"))
    if not cfg["anon"]:
        leaks += [f"{name}: PDF has no author block"] if "Anonymous authors" in \
            pdf_text(PDF_DIR / f"{name}.pdf") else []
    if leaks:
        raise BuildError(f"{name}: leak scan failed:\n  " + "\n  ".join(leaks[:30]))

    if cfg["zip"]:
        make_zip(dst, OUT / f"{name}_source.zip")
    return f"{pages.group(1) if pages else '?'} pages, {len(keep)} files"


# --- leak scan ------------------------------------------------------------------------
def patterns(anon, is_A):
    return LEAK_ALWAYS + (LEAK_ANON if anon else []) + (LEAK_A if is_A else [])


def scan_text(text, where, anon, is_A):
    hits = []
    for pat in patterns(anon, is_A):
        for m in re.finditer(pat, text):
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{where}:{line}: {pat} -> {text[max(0, m.start()-30):m.end()+30]!r}")
    return hits


def scan_dir(d, anon, is_A):
    hits = []
    for f in sorted(d.rglob("*")):
        if f.is_file() and f.suffix in {".tex", ".bbl", ".py", ".sh", ".ps1", ".toml",
                                         ".md", ".yaml", ".yml", ".json", ".txt", ".cfg"}:
            hits += scan_text(f.read_text(encoding="utf-8", errors="replace"),
                              f.relative_to(OUT).as_posix(), anon, is_A)
    return hits


def pdf_text(pdf):
    if shutil.which("pdftotext") is None:
        raise BuildError("pdftotext not found on PATH (needed for the PDF leak scan)")
    p = subprocess.run(["pdftotext", str(pdf), "-"], stdout=subprocess.PIPE, text=True,
                       errors="replace")
    return p.stdout


def scan_pdf(pdf, anon, is_A):
    hits = scan_text(pdf_text(pdf), pdf.name, anon, is_A)
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(pdf)], stdout=subprocess.PIPE, text=True,
                              errors="replace").stdout
        hits += scan_text(info, pdf.name + " (metadata)", anon, is_A)
    return hits


def make_zip(d, zpath):
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(d.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(d).as_posix())


# --- code supplements -----------------------------------------------------------------
# Lab paths in the code are replaced by a neutral root; these files are lab tooling only.
SUPP_SKIP = {"build_papers.sh", "kaggle_session.sh", "kaggle_heff.sh", "kaggle_split.sh",
             "make_tt_fonts.py"}
SUPP_SUBST = [(r"/mnt/data/khoitm8", "/path/to/workdir"), (r"\bon lab09\b", "on the compute server")]
# verify_paper_numbers.py checks numbers of both papers (it reads A and B joined), so
# the folders only it reads are paper A's and stay out of B's supplement.
RES_REF_IGNORE = {"supp_B": {"verify_paper_numbers.py", "learned_composition.py"},
                  "supp_A": set()}
# Raw per-seed arrays left out to stay under TMLR's 100 MB cap. The summaries computed from
# them (summary.json, tables.json, SUMMARY.md) stay, so every printed number is still there;
# rerunning the generator rebuilds the arrays. (glob under results/, why, how to regenerate)
RES_OMIT = {
    "supp_A": [("learned_composition_20261021/*/final_states.npz",
                "endpoint arrays of the 1-D learned-composition runs",
                "scripts/learned_composition.py"),
               ("learned_composition_20261021/*/field_diagnostics.npz",
                "field diagnostics of the same runs",
                "scripts/learned_composition.py")],
    "supp_B": [],
}
# B-only files kept out of A's supplement.
SUPP_A_RENAME = {"paperB_verify_uncertainty.py": None}  # B-only checker; dropped from A


def named_scripts(tex):
    names = re.findall(r"\\texttt\{([A-Za-z0-9_\\]+\.(?:py|sh))\}", tex)
    return sorted({n.replace("\\_", "_") for n in names})


def local_imports(path, pool):
    """Names of local modules (in pool) that a script imports, transitively."""
    seen, todo = set(), [path]
    while todo:
        p = todo.pop()
        if p in seen or p.suffix != ".py":
            seen.add(p)
            continue
        seen.add(p)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            raise BuildError(f"cannot parse {p}: {e}")
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            for m in mods:
                parts = m.split(".")
                # "scripts.foo" / "src.a.b" resolve under ROOT; a bare "foo" is a sibling.
                cand = [ROOT.joinpath(*parts).with_suffix(".py"),
                        ROOT.joinpath(*parts) / "__init__.py"]
                if len(parts) == 1 and parts[0] in pool:
                    cand.insert(0, pool[parts[0]])
                hit = next((c for c in cand if c.exists()), None)
                if hit is not None:
                    todo.append(hit)
    return seen


def build_supp(name, notes):
    paper = "paper_theory" if name == "supp_A" else "paper_mechanism"
    tex = (ROOT / paper / "main.tex").read_text(encoding="utf-8")
    dst = OUT / name
    if dst.exists():
        shutil.rmtree(dst)
    pool = {p.stem: p for p in (ROOT / "scripts").glob("*.py")}
    pool.update({p.stem: p for p in (ROOT / "src").glob("*.py")})
    files = set()
    missing = []
    for s in named_scripts(tex):
        cand = [ROOT / "scripts" / s, ROOT / "src" / s]
        hit = next((c for c in cand if c.exists()), None)
        if hit is None:
            missing.append(s)
            continue
        files |= local_imports(hit, pool)
    for s in ["train_exp2", "train_exp3"] if name == "supp_B" else []:
        files |= local_imports(ROOT / "src" / f"{s}.py", pool)
    if missing:
        raise BuildError(f"{name}: scripts named in {paper}/main.tex not found: {missing}")
    # The whole src/ package: scripts import it as "src.<sub>.<mod>", so ship all of it.
    files |= {p for p in (ROOT / "src").rglob("*.py") if "__pycache__" not in p.parts}
    for extra in ["pyproject.toml", "uv.lock", "LICENSE"]:
        if (ROOT / extra).exists():
            files.add(ROOT / extra)
    if (ROOT / "configs").exists():
        files |= {p for p in (ROOT / "configs").rglob("*") if p.is_file()}
    for f in sorted(files):
        if f.name in SUPP_SKIP or (name == "supp_A" and f.name in SUPP_A_RENAME):
            continue
        rel = f.relative_to(ROOT)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat, rep in SUPP_SUBST:
            text = re.sub(pat, rep, text)
        out.write_text(text, encoding="utf-8")
    subst = SUPP_SUBST
    res_files = copy_results(name, dst, subst)
    write_supp_readme(name, dst, tex, res_files)
    leaks = scan_dir(dst, True, name == "supp_A")
    # Code may carry TODO/FLAG notes legitimately; only identity and cross-paper hits count.
    leaks = [h for h in leaks if not re.search(r"TODO|FLAG|DECISION", h.split("->")[0])]
    if leaks:
        raise BuildError(f"{name}: leak scan failed:\n  " + "\n  ".join(leaks[:30]))
    zpath = OUT / f"{name}.zip"
    make_zip(dst, zpath)
    mb = zpath.stat().st_size / 1e6
    if mb > SUPP_MAX_MB:
        raise BuildError(f"{name}: {zpath.name} is {mb:.0f} MB, over the {SUPP_MAX_MB} MB cap")
    n = sum(1 for p in dst.rglob("*") if p.is_file())
    return f"{n} files ({len(res_files)} from results/), zip {mb:.1f} MB"


# --- saved results ----------------------------------------------------------------------
# OpenReview caps supplementary material at about 100 MB; stay under it with margin.
SUPP_MAX_MB = 95
# Run logs carry host names and shell history and are not needed to rerun the analyses.
RES_SKIP_SUFFIX = {".log", ".pt", ".pth", ".ckpt"}
TEXT_SUFFIX = {".json", ".csv", ".yaml", ".yml", ".md", ".txt", ".sh", ".py", ".tex"}


def referenced_results(name, dst):
    """results/ entries named in the copied code, mapped back to their real names."""
    refs = set()
    for f in list(dst.rglob("*.py")) + list(dst.rglob("*.sh")):
        if f.name in RES_REF_IGNORE[name]:
            continue
        refs |= set(re.findall(r"results/([A-Za-z0-9_.-]+)", f.read_text(encoding="utf-8")))
    entries = {p.name for p in (ROOT / "results").iterdir()}
    out = set()
    for r in refs:
        r = r.rstrip(".")
        if r in entries:
            out.add(r)
        else:
            # f-string prefixes such as "s10_cifar_transfer_" match their dated folders
            out |= {e for e in entries if e.startswith(r) and r.endswith("_")}
    return sorted(out)


def copy_results(name, dst, subst):
    copied = []
    omit = {q.resolve() for pat, _, _ in RES_OMIT[name] for q in (ROOT / "results").glob(pat)}
    for r in referenced_results(name, dst):
        src = ROOT / "results" / r
        target = dst / "results" / r
        items = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
        for f in items:
            if f.suffix in RES_SKIP_SUFFIX or f.resolve() in omit:
                continue
            out = target if src.is_file() else target / f.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            if f.suffix in TEXT_SUFFIX:
                text = f.read_text(encoding="utf-8", errors="replace")
                for pat, rep in subst:
                    text = re.sub(pat, rep, text)
                out.write_text(text, encoding="utf-8")
            else:
                shutil.copy2(f, out)
            copied.append(out.relative_to(dst).as_posix())
    return copied


def first_doc_line(path):
    try:
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    except SyntaxError:
        doc = ""
    line = doc.strip().splitlines()[0] if doc.strip() else ""
    return line.replace("|", "/")


SUPP_README = """# Code for "{title}"

Anonymised supplementary material. It contains the code behind every number and figure of
the paper and the saved outputs those numbers are computed from.

## Setup

Python 3.10 to 3.12 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Without uv, `pip install torch numpy matplotlib pyyaml pandas torchvision` works too.
Run everything from this folder, so that `src` and `scripts` import as packages:

```bash
uv run python -m scripts.<name> --help
```

## What is where

- `src/`: models, flows, samplers and metrics shared by all scripts.
- `scripts/`: one script per experiment, analysis or figure (table below).
- `configs/`: training configurations.
- `results/`: the saved outputs the paper's numbers are read from. Model checkpoints and
  run logs are left out to keep the archive small.

The reproducibility statement at the end of the paper says which script produces which
figure, table or number. Analysis and figure scripts read `results/` and run on a CPU in
minutes. Training and sampling scripts rebuild those outputs from scratch; they write to a
new folder, so they never overwrite the saved results, and the image-scale ones need a GPU
and download CIFAR-10 or MNIST on first use. Paths shown as `/path/to/workdir` stand for a
local working directory; set them on the command line or edit the default.

## Scripts named in the paper

| Script | Purpose |
|---|---|
{rows}

## Saved results included

{results}
{omitted}"""


def write_supp_readme(name, dst, tex, res_files):
    m = re.search(r"\\title\{(.*?)\}\s*\n", tex, re.S)
    title = re.sub(r"\\\\\s*", " ", m.group(1)).strip() if m else "the paper"
    rows = []
    for s in named_scripts(tex):
        f = next((p for p in [dst / "scripts" / s, dst / "src" / s] if p.exists()), None)
        if f is None:
            continue
        rows.append(f"| `{f.relative_to(dst).as_posix()}` | {first_doc_line(f) if f.suffix == '.py' else 'shell driver'} |")
    tops = sorted({"/".join(r.split("/")[:2]) for r in res_files})
    results = "\n".join(f"- `{t}`" for t in tops) or "None."
    omitted = ""
    if RES_OMIT[name]:
        omitted = ("\nLeft out to keep the archive under 100 MB (the summaries computed from them "
                   "are included; rerun the script to rebuild them):\n\n" + "\n".join(
                       f"- `results/{pat}`: {why} (`{how}`)" for pat, why, how in RES_OMIT[name]) + "\n")
    (dst / "README.md").write_text(
        SUPP_README.format(title=title, rows="\n".join(rows), results=results, omitted=omitted),
        encoding="utf-8")


def open_notes():
    """Comments with open notes in the paper sources (line numbers of the originals)."""
    notes = []
    for paper in ["paper_theory", "paper_mechanism"]:
        d = ROOT / paper
        for tex in [d / "main.tex", d / "math_commands.tex"] + sorted(d.glob("figures/**/*.tex")):
            for n, line in enumerate(tex.read_text(encoding="utf-8").splitlines(), 1):
                k = _comment_start(line)
                if k >= 0 and re.search(r"TODO|FLAG|DECISION|[Gg]roup decision|Draft by|the assistant", line[k:]):
                    notes.append(f"{tex.relative_to(ROOT).as_posix()}:{n}: {line[k:].strip()}")
    return notes


def main(argv):
    names = argv or ["A_tmlr", "A_arxiv", "B_neurips", "supp_A", "supp_B"]
    notes, ok = open_notes(), True
    for name in names:
        # A failed target must not leave an older, unchecked upload file behind.
        for stale in [OUT / f"{name}.zip", OUT / f"{name}_source.zip", PDF_DIR / f"{name}.pdf"]:
            if stale.exists():
                stale.unlink()
        try:
            if name in TARGETS:
                msg = build_paper(name, notes)
            elif name in ("supp_A", "supp_B"):
                msg = build_supp(name, notes)
            else:
                raise BuildError(f"unknown target {name}")
            print(f"[ok]   {name}: {msg}")
        except BuildError as e:
            ok = False
            print(f"[FAIL] {e}")
    (OUT / "stripped_notes.txt").write_text(
        "Comments with open notes; build.py strips them from the packages, so resolve\n"
        "them in the paper sources listed here, not in submit/.\n\n" + "\n".join(notes) + "\n",
        encoding="utf-8")
    print(f"open notes stripped: {len(notes)} (submit/stripped_notes.txt)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
