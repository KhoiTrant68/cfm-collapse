#!/usr/bin/env python
"""Submission checks for paper/main.tex, run against the built PDF and .aux.

Build provenance, citations, floats and anonymity are checked. TMLR has no
page cap here; --venue iclr explicitly checks the nine-page main-text limit.
Build and validate the current inputs with:

    python scripts/check_paper.py --build --build-dir tmp/paper-build
    python scripts/check_paper.py --build-dir tmp/paper-build
    python scripts/check_paper.py --baseline snapshot.tex

With --baseline, also checks that no reported number, citation key, label or
theorem environment present in the snapshot has disappeared -- the guard used
when compressing the body, where the failure mode is silently losing evidence
rather than breaking the build.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

PAPER = pathlib.Path(__file__).resolve().parents[1] / "paper"


def hashes(paths: list[pathlib.Path]) -> dict[str, str]:
    return {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def inputs() -> dict[str, str]:
    paths = [p for p in PAPER.iterdir() if p.suffix in {'.tex', '.bib', '.sty', '.bst'}]
    paths += [p for p in (PAPER / 'figures').rglob('*') if p.is_file()]
    return hashes(sorted(paths))


def build(directory: pathlib.Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    frozen = inputs()
    for name in frozen:
        source = pathlib.Path(name)
        if source.parent == PAPER and source.parent != directory:
            shutil.copy2(source, directory / source.name)
    env = os.environ.copy()
    # Local auxiliary files must precede the canonical directory's old cache.
    env['TEXINPUTS'] = '.;' + PAPER.as_posix() + '//;'
    if os.name != 'nt':
        env['TEXINPUTS'] = env['TEXINPUTS'].replace(';', ':')
    commands = [['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
                ['bibtex', 'main']]
    commands += [commands[0]] * 2
    for index, command in enumerate(commands):
        result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True, errors='replace')
        (directory / f'check-build-{index}.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f"{command[0]} failed; see {directory}/check-build-{index}.txt")
    if frozen != inputs():
        raise RuntimeError('paper inputs changed during compilation; rebuild')
    products = hashes([directory / f'main.{ext}' for ext in ('aux', 'log', 'pdf', 'bbl')])
    (directory / 'build-manifest.json').write_text(json.dumps(dict(inputs=frozen, products=products), indent=2), encoding='utf-8')


def check_provenance(directory: pathlib.Path, problems: list[str]) -> None:
    try:
        manifest = json.loads((directory / 'build-manifest.json').read_text(encoding='utf-8'))
        if manifest['inputs'] != inputs():
            raise ValueError('source, bibliography, style or figure changed since build')
        expected = {str((directory / f'main.{ext}').resolve()) for ext in ('aux', 'log', 'pdf', 'bbl')}
        if set(manifest['products']) != expected or hashes([pathlib.Path(p) for p in expected]) != manifest['products']:
            raise ValueError('build products changed or do not belong to this build directory')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        fail(f'build provenance unavailable or stale: {exc}; run with --build', problems)
    else:
        ok('source and build-product hashes match the recorded build')

NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
# Lengths and layout knobs: measurements of the typesetting, not of the model.
TYPESET_NUM = re.compile(
    r"\\includegraphics\[[^\]]*\]"
    r"|(?:width|height|scale|arraystretch|tabcolsep|hspace|vspace|linewidth)"
    r"\s*=?\s*\{?[-0-9.]+\}?")
LABEL = re.compile(r"\\label\{([^}]+)\}")
REF = re.compile(r"\\(?:ref|eqref)\{([^}]+)\}")
CITE = re.compile(r"\\cite[a-z]*\{([^}]+)\}")
ENVS = ("proposition", "theorem", "corollary", "lemma", "remark", "proof",
        "figure", "table", "equation")


def fail(msg: str, problems: list[str]) -> None:
    problems.append(msg)
    print("FAIL  " + msg)


def ok(msg: str) -> None:
    print("ok    " + msg)


def check_page_limit(aux: str, problems: list[str], page_limit: int | None = None) -> None:
    """`\\label{endmain}` sits immediately before the Reproducibility statement."""
    m = re.search(r"\\newlabel\{endmain\}\{\{[^}]*\}\{(\d+)\}", aux)
    if not m:
        fail("no \\label{endmain} in main.aux -- cannot check the page limit",
             problems)
        return
    page = int(m.group(1))
    if page_limit is not None and page > page_limit:
        fail(f"main text ends on page {page}, limit is {page_limit}", problems)
    else:
        ok(f"main text ends on page {page} (limit {page_limit if page_limit is not None else 'not imposed'})")


def check_log(log: str, problems: list[str]) -> None:
    if 'Float too large for page' in log:
        fail('a float is too large for the page', problems)
    undefined = log.count("undefined")
    if undefined:
        fail(f"{undefined} undefined reference/citation warnings in main.log",
             problems)
    else:
        ok("no undefined references or citations")

    overfull = log.count("Overfull \\hbox")
    if overfull:
        fail(f"{overfull} overfull hbox(es)", problems)
    else:
        ok("no overfull hboxes")


def check_tex(tex: str, problems: list[str]) -> None:
    labels = LABEL.findall(tex)
    dups = [k for k, v in collections.Counter(labels).items() if v > 1]
    if dups:
        fail(f"duplicate labels: {sorted(dups)}", problems)
    else:
        ok(f"{len(labels)} labels, all unique")

    refs = {r for r in REF.findall(tex) if not r.startswith("#")}  # `#1` is a macro argument
    dangling = sorted(refs - set(labels))
    if dangling:
        fail(f"references with no label: {dangling}", problems)
    else:
        ok("every \\ref/\\eqref resolves")

    for kind, name in (("fig", "figures"), ("tab", "tables")):
        floats = [l for l in labels if l.startswith(kind + ":")]
        uncited = [f for f in floats if f not in refs]
        if uncited:
            fail(f"uncited {name}: {uncited}", problems)
        else:
            ok(f"{len(floats)} {name}, all cited from running text")

    body = "\n".join(l for l in tex.split("\n") if not l.lstrip().startswith("%"))
    if "\\iclrfinalcopy" in body or re.search(r'\\usepackage\[(?:accepted|preprint)\]\{tmlr\}', body):
        fail("\\iclrfinalcopy is uncommented -- would deanonymise the submission",
             problems)
    else:
        ok("anonymous submission mode (author metadata still needs PDF inspection)")


def _reported_numbers(tex: str) -> collections.Counter:
    """Numbers a reader could quote, i.e. not typesetting measurements.

    A float's width is not a result: resizing a figure used to be reported as a
    lost number, which trains the reader of this check to ignore it.
    """
    tex = TYPESET_NUM.sub(" ", tex)
    return collections.Counter(NUM.findall(tex))


def check_baseline(tex: str, baseline: pathlib.Path, problems: list[str]) -> None:
    old = baseline.read_text(encoding="utf-8")

    before, now = _reported_numbers(old), _reported_numbers(tex)
    gone = sorted(k for k in before if now.get(k, 0) == 0)
    if gone:
        fail(f"numbers reported in the baseline and now absent: {gone}", problems)
    else:
        ok("no reported number lost against the baseline")

    keys_old = {k for g in CITE.findall(old) for k in g.split(",")}
    keys_new = {k for g in CITE.findall(tex) for k in g.split(",")}
    dropped = sorted(keys_old - keys_new)
    if dropped:
        fail(f"citation keys dropped: {dropped}", problems)
    else:
        ok("no citation key dropped")

    def count(t: str, env: str) -> int:
        # a displayed equation is an `equation` or an `align`: proofs written one line
        # per step use the latter, and that is not a lost equation
        names = ("equation", "equation*", "align", "align*") if env == "equation" else (env,)
        return sum(t.count("\\begin{%s}" % n) for n in names)

    for env in ENVS:
        a, b = count(old, env), count(tex, env)
        if b < a:
            fail(f"{env}: {a} in baseline, {b} now", problems)
    ok("no theorem environment, figure or table lost")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=pathlib.Path,
                    help="a main.tex snapshot to check for lost content")
    ap.add_argument('--build-dir', type=pathlib.Path, default=PAPER)
    ap.add_argument('--build', action='store_true', help='compile and record input/product hashes')
    ap.add_argument('--venue', choices=['tmlr', 'iclr'], default='tmlr')
    ap.add_argument('--page-limit', type=int, help='explicit main-text page cap')
    args = ap.parse_args()

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    problems: list[str] = []
    directory = args.build_dir.resolve()
    if args.build:
        try:
            build(directory)
        except (OSError, RuntimeError) as exc:
            fail(str(exc), problems)
            return 1
    check_provenance(directory, problems)
    if problems:
        return 1
    page_limit = args.page_limit if args.page_limit is not None else (9 if args.venue == 'iclr' else None)
    if args.venue == 'iclr' and '\\usepackage{tmlr}' in tex:
        fail('ICLR venue selected but canonical source uses TMLR style', problems)

    for name, fn in (("main.aux", lambda text, errors: check_page_limit(text, errors, page_limit)), ("main.log", check_log)):
        path = directory / name
        if not path.exists():
            fail(f"{name} not found -- build the paper first", problems)
        else:
            fn(path.read_text(encoding="utf-8", errors="replace"), problems)

    check_tex(tex, problems)
    if args.baseline:
        check_baseline(tex, args.baseline, problems)

    print()
    if problems:
        print(f"{len(problems)} problem(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
