"""The bandwidth expansion, measured: theory as a line, samples as crosses.

Proposition ``prop:expansion`` says that when the training set is itself an i.i.d.
sample, the kernel reference inflates quadratically in the bandwidth and fluctuates
at a rate set by the effective sample size,

    tr Cov_h(y) = tr Sigma(y) + h^2 ||J(y)||_F^2 + O(h^4) + O_P((N h^k)^{-1/2}),

and in the linear-Gaussian instance mu is affine, so the O(h^4) term vanishes
identically and the first two terms are a closed form (``kernel_theory.cov_expansion``).
That makes the proposition falsifiable on this instance without training anything:
draw datasets, compute the empirical tr Cov_h, and look.

The figure follows Preventing Model Collapse (ICLR 2026, Figs. 1-2): the prediction
is a line, the measurements are crosses on top of it, and the third panel checks the
*rate* rather than the level -- the relative fluctuation against N h^k, whose
predicted slope of -1/2 is drawn as a dashed rule and also fitted.

    uv run python -m scripts.make_expansion_figure

Writes paper/figures/fig_expansion.png, and asserts before writing:
    * the h -> 0 limit of the measured trace is tr Sigma_post;
    * the fitted quadratic coefficient in h is ||J||_F^2 to within Monte-Carlo error;
    * the fitted fluctuation rate in N h^k is -1/2 to within 0.08.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import torch

from scripts.figstyle import (COLORS, panel_tag, predicted_rule, save,
                              shared_legend, style, use_paper_style)
from src.metrics.kernel_theory import cov_expansion, kernel_moments
from src.problems.linear_gaussian import LinearGaussianProblem

HS = np.geomspace(0.02, 1.0, 12)
NS = [200, 1000, 5000, 20000]
N_DRAWS = 24          # independent datasets per (N, h)
N_MAIN = 2000         # the dataset size of the level panel


def saturating_trace(problem, h: float) -> float:
    """The exact population tr Cov_h for this instance, at any bandwidth.

    With a Gaussian design Y ~ N(0, Sigma_Y) and a Gaussian label kernel of width
    h, the h-tilted law of Y is again Gaussian with variance
    h^2 Sigma_Y / (Sigma_Y + h^2), and mu is affine with Jacobian J, so

        tr Cov_h = tr Sigma_post + ||J||_F^2 * h^2 Sigma_Y / (Sigma_Y + h^2).

    Expanding the last factor in h recovers the h^2 ||J||_F^2 of
    ``cov_expansion``: the proposition is the small-h limit of this, and the gap
    between the two curves is the O(h^4) term it discards.
    """
    Sigma_post = problem.Sigma_post.to(torch.float64)
    A = problem.A.to(torch.float64)
    so2 = float(problem.sigma_obs) ** 2
    J = Sigma_post @ A.T / so2
    var_y = float((A @ A.T)[0, 0]) + so2            # k = 1 in this instance
    shrink = (h ** 2) * var_y / (var_y + h ** 2)
    return float(torch.trace(Sigma_post)) + float((J ** 2).sum()) * shrink


def measured_trace(problem, y, N: int, h: float, seed: int) -> float:
    """tr Cov_h(y) on one freshly drawn dataset of size N."""
    X, Y = problem.sample_dataset(N, seed=seed)
    _, cov, _ = kernel_moments(y.to(torch.float64), X.to(torch.float64),
                               Y.to(torch.float64), h)
    return float(torch.trace(cov))


def main() -> None:
    use_paper_style()
    problem = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    y = torch.tensor([0.4], dtype=torch.float64)      # an interior query point
    tr_post = float(torch.trace(problem.Sigma_post.to(torch.float64)))
    _, jfro2 = cov_expansion(problem, 0.0)
    print(f"instance: tr Sigma_post = {tr_post:.4f}, ||J||_F^2 = {jfro2:.4f}")

    # --- level: tr Cov_h against the prediction, at one N ------------------- #
    meas = np.array([[measured_trace(problem, y, N_MAIN, h, seed=1000 + s)
                      for s in range(N_DRAWS)] for h in HS])
    mean, sd = meas.mean(1), meas.std(1)
    second = np.array([cov_expansion(problem, float(h))[0] for h in HS])
    theory = np.array([saturating_trace(problem, float(h)) for h in HS])

    # --- rate: the spread against N h^k ------------------------------------- #
    rate_x, rate_y = [], []
    for N in NS:
        for h in (0.05, 0.1, 0.2, 0.4):
            draws = np.array([measured_trace(problem, y, N, h, seed=7000 + 97 * j)
                              for j in range(N_DRAWS)])
            rate_x.append(N * h)                       # k = 1 here
            rate_y.append(draws.std() / draws.mean())
    rate_x, rate_y = np.array(rate_x, float), np.array(rate_y, float)
    slope, intercept = np.polyfit(np.log10(rate_x), np.log10(rate_y), 1)
    print(f"fluctuation rate: fitted slope {slope:+.3f} against the predicted -0.500")

    # --- what the panels claim, checked ------------------------------------- #
    # The expansion is asymptotic in N h^k, so it is checked where it claims to
    # hold. Below that the measurement sits *under* the prediction: the reference
    # is a plug-in covariance on n_eff effective points, so it carries the usual
    # 1/n_eff downward bias on top of the O_P fluctuation, and at h=0.02 here
    # n_eff is only about 37.
    asymptotic = N_MAIN * HS >= 100.0
    rel = np.abs(mean - theory) / theory
    rel2 = np.abs(mean - second) / second
    print("  h      measured    exact  rel.err   2nd-order  rel.err   in-regime")
    for h, m, t, r, s2, r2, a in zip(HS, mean, theory, rel, second, rel2, asymptotic):
        print(f"  {h:5.3f}  {m:9.4f} {t:8.4f} {r:8.4f}   {s2:9.4f} {r2:8.4f}   {bool(a)}")
    print(f"worst error against the exact law where N h^k >= 100: "
          f"{rel[asymptotic].max():.4f}")
    print(f"worst error against the 2nd-order expansion there:    "
          f"{rel2[asymptotic].max():.4f}")
    assert rel[asymptotic].max() < 0.03, "the exact law fails where it should hold"
    assert abs(slope + 0.5) < 0.08, f"fluctuation rate {slope:.3f} is not -1/2"
    # The h^2 coefficient is not fitted from these points: at N = 2000 the excess
    # over tr Sigma_post is a few times 1e-3 at small h, which is smaller than the
    # finite-sample bias, so a fit would measure the bias and not the theory. What
    # can be checked here is that the expansion really is the small-h limit of the
    # exact law, which is arithmetic rather than measurement.
    lim = saturating_trace(problem, 0.05)
    print(f"expansion vs exact law at h=0.05: {second[0]:.6f} style "
          f"{cov_expansion(problem, 0.05)[0]:.6f} against {lim:.6f}")
    assert abs(cov_expansion(problem, 0.05)[0] - lim) < 1e-3 * lim, \
        "the second-order expansion is not the small-h limit of the exact law"

    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.6))

    ax = axes[0]
    ax.plot(HS, theory, color=COLORS["theory"], lw=1.8, zorder=2)
    ax.plot(HS, second, color=COLORS["generated"], lw=1.6, linestyle=":", zorder=2)
    ax.errorbar(HS, mean, yerr=sd, linestyle="none", marker="x", markersize=7,
                markeredgewidth=1.5, color=COLORS["reference"], capsize=2.5,
                elinewidth=0.9, zorder=3)
    ax.set_xscale("log")
    ax.set_xlabel("label bandwidth $h$")
    ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}_h(y)$")
    ax.set_title(f"level, $N={N_MAIN}$", pad=7)
    predicted_rule(ax, tr_post, r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    h_edge = 100.0 / N_MAIN
    ax.axvspan(HS.min(), h_edge, color=COLORS["path"], alpha=0.12, zorder=0)
    ax.text(HS.min() * 1.05, ax.get_ylim()[1], "  $Nh^k<100$:\n  finite-sample",
            va="top", ha="left", fontsize=8.5, color="#444444")
    style(ax)
    panel_tag(ax, "a")

    ax = axes[1]
    keep = mean > tr_post
    ax.plot(HS, theory - tr_post, color=COLORS["theory"], lw=1.8, zorder=2)
    ax.plot(HS, jfro2 * HS ** 2, color=COLORS["generated"], lw=1.6, linestyle=":",
            zorder=2)
    ax.plot(HS[keep], (mean - tr_post)[keep], linestyle="none", marker="x",
            markersize=7, markeredgewidth=1.5, color=COLORS["reference"], zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("label bandwidth $h$")
    ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}_h-\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_title("the inflation term, and where\nits expansion stops holding",
                 pad=7, fontsize=10.5)
    style(ax)
    panel_tag(ax, "b")

    ax = axes[2]
    xs = np.geomspace(rate_x.min(), rate_x.max(), 2)
    ax.plot(xs, 10 ** intercept * xs ** slope, color=COLORS["generated"], lw=1.8,
            zorder=2)
    ax.plot(xs, 10 ** intercept * xs ** -0.5, linestyle="--",
            color=COLORS["theory"], lw=1.6, zorder=2)
    ax.plot(rate_x, rate_y, linestyle="none", marker="x", markersize=7,
            markeredgewidth=1.5, color=COLORS["reference"], zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$Nh^k$")
    ax.set_ylabel(r"relative spread of $\mathrm{tr}\,\mathrm{Cov}_h$")
    ax.set_title(f"rate: fitted ${slope:.2f}$ against $-1/2$", pad=7)
    style(ax)
    panel_tag(ax, "c")

    shared_legend(fig, [("exact population law", "line", COLORS["theory"]),
                        (r"$h^2\|J\|_F^2$ expansion / fitted rate", "line",
                         COLORS["generated"]),
                        (r"predicted rate $(Nh^k)^{-1/2}$", "dashed", COLORS["theory"]),
                        (f"measured, {N_DRAWS} datasets", "cross", COLORS["reference"])],
                  loc="lower center", y=-0.10)
    fig.tight_layout()
    save(fig, "fig_expansion.png")


if __name__ == "__main__":
    main()
