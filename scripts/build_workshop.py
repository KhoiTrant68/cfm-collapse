"""Assemble paper/workshop.tex from paper/workshop_src.tex and paper/main.tex.

The workshop source holds the four-page main text and its workshop-only appendix by
hand. Every %%BLOCK:name%% line is filled with a block cut from the conference version
(paper/main.tex), so the proofs and the spectral-bias appendix that the two versions
share cannot drift apart. Run it after every change to either file.

Usage:  uv run python scripts/build_workshop.py
"""
from __future__ import annotations

from pathlib import Path

PAPER = Path("paper")


def cut(text: str, start: str, end: str, include_end: bool = True) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j + (len(end) if include_end else 0)]


def env_with_label(text: str, env: str, label: str) -> str:
    k = text.index(f"\\label{{{label}}}")
    i = text.rindex(f"\\begin{{{env}}}", 0, k)
    j = text.index(f"\\end{{{env}}}", k) + len(f"\\end{{{env}}}")
    return text[i:j]


def main() -> None:
    src = (PAPER / "workshop_src.tex").read_text(encoding="utf-8")
    m = (PAPER / "main.tex").read_text(encoding="utf-8")

    heffid = cut(m, r"\begin{proof}[Proof of Proposition~\ref{prop:heffid}]", r"\end{proof}")
    heffid = heffid.replace("\n" + r"\label{eq:pf:heffid:1}", "")
    calib = cut(m, r"\begin{proof}[Proof of Theorem~\ref{thm:calib}]", r"\end{proof}")
    calib = (r"In part (c) write $s_h^2=\sigma^2+h^2$, "
             r"$\Sigma_h=(\Sigma_x^{-1}+A^\top A/s_h^2)^{-1}$, $\Gamma_h=\Sigma_hA^\top/s_h^2$ and "
             r"$\mu_h(y)=\Sigma_h\Sigma_x^{-1}\mu_x+\Gamma_hy$ for the prior $\N(\mu_x,\Sigma_x)$ and "
             r"$g(x)=Ax$; then $\pi_h(\cdot\mid y)=\N(\mu_h(y),\Sigma_h)$, and the claim of (c) is "
             r"$X-\mu_h(Y)\sim\N(0,\Sigma_h-h^2\Gamma_h\Gamma_h^\top)$." + "\n\n" + calib)

    sb = cut(m, r"\subsection{A spectral-bias model of the effective bandwidth}",
             r"\subsection{An audit protocol for conditional flows}", include_end=False)
    sb = sb.split("\n", 2)[2]                      # drop the subsection line and its label
    stmt = env_with_label(m, "proposition", "prop:filtered").replace(
        r"\proofin{apx:pf-filtered}" + "\n", "")
    old = (r"Proposition~\ref{prop:filtered}" + "\n"
           r"(Section~\ref{sec:heff}) says that this keeps the atoms.")
    assert old in sb
    sb = sb.replace(old, r"Proposition~\ref{prop:filtered} says that this keeps the atoms."
                    + "\n\n" + stmt)
    sb = sb.replace(r"By Proposition~\ref{prop:kernel-field},",
                    r"By the proof of Theorem~\ref{thm:endpoint},")
    blocks = {"proof_heffid": heffid, "proof_calib": calib,
              "specbias": sb.rstrip() + "\n\n" + env_with_label(m, "figure", "fig:t2")}

    out = src.replace("This file is the source: scripts/build_workshop.py fills the %%BLOCK%% lines\n"
                      "% from main.tex and writes workshop.tex. Edit this file, not workshop.tex.",
                      "GENERATED from workshop_src.tex by scripts/build_workshop.py: do not edit.")
    for k, v in blocks.items():
        tag = f"%%BLOCK:{k}%%"
        assert tag in out, tag
        out = out.replace(tag, v)
    assert "%%BLOCK:" not in out
    (PAPER / "workshop.tex").write_text(out, encoding="utf-8", newline="")
    print("wrote paper/workshop.tex")


if __name__ == "__main__":
    main()
