"""Symbolic and numerical checks behind the audit of Theorem thm:composition,
Proposition prop:composition-open, Theorem thm:spectral and Corollary cor:spectral-threshold.

Each check recomputes one step of the proofs in Appendix apx:pf-composition / apx:pf-spectral
from the definitions, independently of the paper's derivation. They locate algebra and sign
errors; they do not replace the arguments (the audit report says which step each one supports).

    python -I scripts/audit_composition_spectral.py      (run from the repository root)
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
import sympy as sp

OUT = pathlib.Path("results/learned_composition_20261021/audit_checks.json")
rng = np.random.default_rng(20261021)
checks: dict[str, dict] = {}


def record(name, ok, **info):
    checks[name] = {"ok": bool(ok), **info}
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {info}")


# --- Theorem thm:composition ------------------------------------------------------------
s, B, w, c, t = sp.symbols("s B w c t", real=True)
F = (1 + w) / 2 * (sp.tanh(s + B) + sp.tanh(s - B)) - w * sp.tanh(s)
closed = 2 * sp.tanh(s) * (sp.cosh(s) ** 2 - w * sp.sinh(B) ** 2) / (sp.cosh(2 * s) + sp.cosh(2 * B))
diff = sp.simplify(sp.expand_trig((F - closed).rewrite(sp.exp)))
pts = [(float(a), float(b), float(ww)) for a, b, ww in rng.uniform([-4, 0.1, 0], [4, 4, 20], (200, 3))]
num = max(abs(float((F - closed).subs({s: a, B: b, w: ww}))) for a, b, ww in pts)
record("A1 closed form of F_w", diff == 0 or num < 1e-12, symbolic_zero=bool(diff == 0), max_abs_numeric=num)

dF0 = sp.simplify(sp.diff(F, s).subs(s, 0))
alt = sp.sech(B) ** 2 - w * sp.tanh(B) ** 2
ok = sp.simplify((dF0 - ((1 + w) * sp.sech(B) ** 2 - w)).rewrite(sp.exp)) == 0 and \
    sp.simplify((dF0 - alt).rewrite(sp.exp)) == 0
root = sp.solve(sp.Eq(alt, 0), w)
record("A2 F_w'(0) and its zero", ok and len(root) == 1 and
       sp.simplify((root[0] - 1 / sp.sinh(B) ** 2).rewrite(sp.exp)) == 0, w_at_zero=str(root))

sign_factor = sp.simplify((closed * (sp.cosh(2 * s) + sp.cosh(2 * B)) / (2 * sp.tanh(s))
                           - (sp.cosh(s) ** 2 - w * sp.sinh(B) ** 2)))
record("A3 sign of F_w on s>0 is that of cosh^2 s - w sinh^2 B", sign_factor == 0)

# Barrier b(t) = c eps^2/t; v(b,t) - b'(t) for the field (F(s) - x)/eps, s = t x / eps^2.
Fc = sp.Function("F")(c)
eps = 1 - t
b = c * eps ** 2 / t
v_at_b = (Fc - b) / eps            # s = t b / eps^2 = c at x = b
lhs = sp.simplify(v_at_b - sp.diff(b, t))
rhs = (Fc + c * (eps ** 2 / t + eps ** 3 / t ** 2)) / eps
record("A4 moving-barrier derivative", sp.simplify(lhs - rhs) == 0)


import mpmath as mp  # noqa: E402  (float64 loses F_w ~ kappa s^3 to cancellation at w = w_c)

mp.mp.dps = 60
worst = mp.inf
for Bv in np.linspace(0.05, 6, 40):
    Bm = mp.mpf(Bv)
    kappa = 1 / (mp.cosh(2) + mp.cosh(2 * Bm))
    for wv in (0, 1 / (2 * mp.sinh(Bm) ** 2), 1 / mp.sinh(Bm) ** 2):  # F_w decreases in w on s>0
        for sv in np.concatenate([np.geomspace(1e-4, 1, 150), np.linspace(1, 60, 300)]):
            sm = mp.mpf(sv)
            Fv = (1 + wv) / 2 * (mp.tanh(sm + Bm) + mp.tanh(sm - Bm)) - wv * mp.tanh(sm)
            worst = min(worst, Fv / (kappa * min(sm ** 3, 1)))
record("A5 F_w >= kappa min(s^3,1) for w <= w_c (grid, 60 digits)", worst >= 1,
       min_ratio=float(worst))
record("A6 2 tanh(1) sinh(1)^2 > 1", 2 * math.tanh(1) * math.sinh(1) ** 2 > 1,
       value=2 * math.tanh(1) * math.sinh(1) ** 2)

# Total variance at the tie: Gamma_w(0) = C_u - (1+w) Var(component means), C_u = 1.
Gam = 1 - (1 + w) * sp.tanh(B) ** 2
record("A7 tie slope = C_u - (1+w) Var(means)", sp.simplify((Gam - alt).rewrite(sp.exp)) == 0)

u1, u2, v1, v2 = sp.symbols("u1 u2 v1 v2", real=True)
U, V = sp.Matrix([u1, u2]), sp.Matrix([v1, v2])
ident = ((1 + w) * U - w * V).dot((1 + w) * U - w * V) - \
    ((1 + w) * U.dot(U) - w * V.dot(V) + w * (1 + w) * (U - V).dot(U - V))
record("A8 |(1+w)u - wv|^2 identity (Thm schedule, Step 1)", sp.expand(ident) == 0)


# --- Theorem thm:spectral: blow-up coordinates on a random tied configuration ---------------
def config(d=4, m=2, n_off=3, K=3):
    """Atoms: |S| = m+1 points on a sphere around z inside z + L, plus off-S atoms farther out."""
    z = rng.normal(size=d)
    basis = np.linalg.qr(rng.normal(size=(d, m)))[0]          # orthonormal basis of L
    dirs = rng.normal(size=(m + 1, m))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    S = z + 1.3 * dirs @ basis.T
    off = z + rng.normal(size=(n_off, d)) * 3.0
    off = np.array([o if np.linalg.norm(o - z) > 2.0 else z + 2.5 * (o - z) / np.linalg.norm(o - z) for o in off])
    A = np.vstack([S, off])
    P = rng.dirichlet(np.ones(len(A)), size=K)
    coef = rng.normal(size=K); coef += (1 - coef.sum()) / K       # sum to one, signed
    return z, basis, A, len(S), P, coef


def posterior(p, A, x, tv):
    e = 1 - tv
    logit = np.log(p) - ((x - tv * A) ** 2).sum(1) / (2 * e ** 2)
    q = np.exp(logit - logit.max()); return q / q.sum()


z, Lb, A, nS, P, coef = config()
PL = Lb @ Lb.T; PN = np.eye(len(z)) - PL
SA = A[:nS]


def M_of(xi):
    out = np.zeros(len(z))
    for pk, ck in zip(P, coef):
        lw = np.log(pk[:nS]) + SA @ xi
        q = np.exp(lw - lw.max()); q /= q.sum()
        out += ck * q @ SA
    return out


worst_xi = worst_eta = worst_logit = worst_xz_ok = worst_xz_paper = 0.0
for _ in range(50):
    tv = rng.uniform(0.3, 0.97); e = 1 - tv; beta = tv / e ** 2
    x = z * tv + rng.normal(size=len(z)) * 0.3 * e
    mbar = sum(ck * posterior(pk, A, x, tv) @ A for pk, ck in zip(P, coef))
    xdot = mbar - x                                     # d x / d tau
    xi = beta * PL @ (x - tv * z); eta = PN @ (x - z)
    dbeta = beta * (1 + tv) / tv                        # d beta / d tau
    dxi = dbeta * PL @ (x - tv * z) + beta * PL @ (xdot - e * z)      # chain rule, dt/dtau = eps
    G = M_of(xi) - z
    R = e ** 2 / tv ** 2 * xi + PL @ (mbar - M_of(xi))
    worst_xi = max(worst_xi, np.abs(dxi / beta - (G + R)).max() / (1 + np.abs(dxi / beta).max()))
    E = PN @ (mbar - z)
    worst_eta = max(worst_eta, np.abs(PN @ xdot - (-eta + E)).max())
    # Lemma offtie: logit of an off-S atom j against i in S.
    p = P[0]; i, j = 0, nS
    lhs = (np.log(p[j]) - ((x - tv * A[j]) ** 2).sum() / (2 * e ** 2)) - \
          (np.log(p[i]) - ((x - tv * A[i]) ** 2).sum() / (2 * e ** 2))
    dj = ((A[j] - z) ** 2).sum() - ((A[i] - z) ** 2).sum()
    rhs = math.log(p[j] / p[i]) - beta * tv / 2 * dj + beta * (e * PN @ z + eta) @ (A[j] - A[i]) + xi @ (A[j] - A[i])
    worst_logit = max(worst_logit, abs(lhs - rhs) / (1 + abs(lhs)))
    # x - z in blow-up coordinates: corrected form and the form printed in the proof of (a),(b).
    worst_xz_ok = max(worst_xz_ok, np.abs((x - z) - (xi / beta - e * PL @ z + eta)).max())
    worst_xz_paper = max(worst_xz_paper, np.abs((x - z) - (xi / beta + e * PN @ z - e * PL @ z + eta)).max())
record("B1 d xi/d sigma = G(xi) + R (blow-up equation)", worst_xi < 1e-9, max_rel_err=worst_xi)
record("B2 d eta/d tau = -eta + E", worst_eta < 1e-10, max_abs_err=worst_eta)
record("B3 Lemma offtie logit identity", worst_logit < 1e-10, max_rel_err=worst_logit)
record("B4 x - z = xi/beta - eps P_L z + eta", worst_xz_ok < 1e-12, max_abs_err=worst_xz_ok)
record("B5 printed form x - z = xi/beta + eps P_Lperp z - eps P_L z + eta (typo check)",
       worst_xz_paper < 1e-12, max_abs_err=worst_xz_paper,
       note="expected FAIL: the printed form has an extra eps P_Lperp z; harmless, both tend to 0")

# Gamma = D_L M = sum_k c_k Cov_{pi_k}(P_L a), by finite differences in L.
xi0 = Lb @ rng.normal(size=Lb.shape[1])
Gam_fd = np.column_stack([(M_of(xi0 + 1e-6 * Lb[:, k]) - M_of(xi0 - 1e-6 * Lb[:, k])) / 2e-6
                          for k in range(Lb.shape[1])])
Gam_fd = Lb.T @ Gam_fd
Gam_cov = np.zeros((Lb.shape[1],) * 2)
for pk, ck in zip(P, coef):
    lw = np.log(pk[:nS]) + SA @ xi0
    q = np.exp(lw - lw.max()); q /= q.sum()
    Y = SA @ Lb; mu = q @ Y
    Gam_cov += ck * ((Y - mu).T * q) @ (Y - mu)
record("B6 Gamma = sum c_k Cov(P_L a) (symmetric)", np.abs(Gam_fd - Gam_cov).max() < 1e-7,
       max_abs_err=float(np.abs(Gam_fd - Gam_cov).max()))

# Potential: grad_L Psi = G.
def Psi(xi):
    return sum(ck * np.log(np.sum(pk[:nS] * np.exp(SA @ xi))) for pk, ck in zip(P, coef)) - xi @ z
g_fd = np.array([(Psi(xi0 + 1e-6 * Lb[:, k]) - Psi(xi0 - 1e-6 * Lb[:, k])) / 2e-6 for k in range(Lb.shape[1])])
record("B7 grad_L Psi = G", np.abs(g_fd - Lb.T @ (M_of(xi0) - z)).max() < 1e-7,
       max_abs_err=float(np.abs(g_fd - Lb.T @ (M_of(xi0) - z)).max()))

# --- Corollary cor:spectral-threshold ------------------------------------------------------
worst = 0.0
for N in range(2, 10):
    Vt = np.eye(N) - 1 / N                            # regular simplex in its (N-1)-dim span
    U_, S_, _ = np.linalg.svd(Vt)
    atoms = (U_[:, :N - 1] * S_[:N - 1])
    atoms /= np.linalg.norm(atoms, axis=1, keepdims=True)
    for Bv in (0.3, 1.0, 2.0, 4.0):
        covs, means = [], []
        for k in range(N):
            p = np.exp(Bv * (np.arange(N) == k)); p /= p.sum()
            mu = p @ atoms; means.append(mu)
            covs.append(((atoms - mu).T * p) @ (atoms - mu))
        Cav = np.mean(covs, 0)
        Cu = (atoms.T @ atoms) / N
        D = Cu - Cav
        ev, evec = np.linalg.eigh(D)
        Dm = evec @ np.diag(ev ** -0.5) @ evec.T
        wspec = np.linalg.eigvalsh(Dm @ Cav @ Dm).max()
        m = (math.exp(Bv) - 1) / (math.exp(Bv) + N - 1)
        worst = max(worst, abs(wspec - (1 - m ** 2) / m ** 2) / ((1 - m ** 2) / m ** 2),
                    np.abs(np.mean(means, 0)).max())
record("C1 simplex threshold (1-m^2)/m^2 and common equilibrium", worst < 1e-10, max_rel_err=worst)
two = max(abs((1 / math.cosh(Bv) ** 2) / (1 - 1 / math.cosh(Bv) ** 2) - 1 / math.sinh(Bv) ** 2)
          for Bv in np.linspace(0.1, 5, 50))
record("C2 two atoms: sech^2 B / tanh^2 B = 1/sinh^2 B", two < 1e-9, max_abs_err=two)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(checks, indent=1), encoding="utf-8")
print(f"wrote {OUT}")
