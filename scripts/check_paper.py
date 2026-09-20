#!/usr/bin/env python
"""Submission checks for paper/main.tex, run against the built PDF and .aux.

The main text must end on page 9 (ICLR's limit; references, the three ICLR
statements and the appendix do not count), every float must be cited from
running text, no reference may be undefined, and the manuscript must stay
anonymous. Run after `latexmk -pdf main.tex`:

    python scripts/check_paper.py            # exits non-zero on any failure
    python scripts/check_paper.py --baseline snapshot.tex

With --baseline, also checks that no reported number, citation key, label or
theorem environment present in the snapshot has disappeared -- the guard used
when compressing the body, where the failure mode is silently losing evidence
rather than breaking the build.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

PAGE_LIMIT = 9  # ICLR main-text limit, excluding references and appendices
PAPER = pathlib.Path(__file__).resolve().parents[1] / "paper"

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


def check_page_limit(aux: str, problems: list[str]) -> None:
    """`\\label{endmain}` sits immediately before the Reproducibility statement."""
    m = re.search(r"\\newlabel\{endmain\}\{\{[^}]*\}\{(\d+)\}", aux)
    if not m:
        fail("no \\label{endmain} in main.aux -- cannot check the page limit",
             problems)
        return
    page = int(m.group(1))
    if page > PAGE_LIMIT:
        fail(f"main text ends on page {page}, limit is {PAGE_LIMIT}", problems)
    else:
        ok(f"main text ends on page {page} (limit {PAGE_LIMIT})")


def check_log(log: str, problems: list[str]) -> None:
    undefined = log.count("undefined")
    if undefined:
        fail(f"{undefined} undefined reference/citation warnings in main.log",
             problems)
    else:
        ok("no undefined references or citations")

    overfull = log.count("Overfull \\hbox")
    if overfull:
        print(f"note  {overfull} overfull hbox(es)")
    else:
        ok("no overfull hboxes")


def check_tex(tex: str, problems: list[str]) -> None:
    labels = LABEL.findall(tex)
    dups = [k for k, v in collections.Counter(labels).items() if v > 1]
    if dups:
        fail(f"duplicate labels: {sorted(dups)}", problems)
    else:
        ok(f"{len(labels)} labels, all unique")

    refs = set(REF.findall(tex))
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
    if "\\iclrfinalcopy" in body:
        fail("\\iclrfinalcopy is uncommented -- would deanonymise the submission",
             problems)
    else:
        ok("anonymous (\\iclrfinalcopy not active)")


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
        names = ("equation", "align", "align*") if env == "equation" else (env,)
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
    args = ap.parse_args()

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    problems: list[str] = []

    for name, fn in (("main.aux", check_page_limit), ("main.log", check_log)):
        path = PAPER / name
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
